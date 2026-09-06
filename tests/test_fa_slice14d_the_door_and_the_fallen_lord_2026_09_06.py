"""FA slice 14 part 2d — "THE DOOR AND THE FALLEN LORD".

The two rulings slice 12 filed against itself:

* **FA-S12-1** — a peace that stranded nobody left no corridor at all, so a
  corps stranded DURING that peace was silently abandoned while the identical
  stranding under a peace that DID strand somebody was handed a road.
* **FA-S12-2** — elimination is a FOURTH way to stop being a satellite and
  applied none of the break effects; and a FIFTH, worse, when the LORD dies.

Landing record: the boxed SLICE 14 (part 2d) block in `docs/BUG_FIXES.md`
§Final Whole-Game Audit. Rules: `SYSTEMS_REFERENCE.md` §39.
"""

import contextlib
import io

import pytest

from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
from backend.game_logic import withdrawal as W
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.game_logic.diplomatic_ledger import _THREAT_SOURCE_LABELS
from backend.models.world_state import WorldState

EUROPE = "godot-client/project-sovereign/assets/maps/europe_1805.json"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(EUROPE)


def _everyone_home(world, nation="France"):
    for marshal in world.marshals.values():
        if marshal.nation == nation:
            marshal.location = "Paris"


def _quiet_peace(world, a="France", b="Russia", state="PEACE"):
    with contextlib.redirect_stdout(io.StringIO()):
        set_diplomatic_state(world, a, b, state, "test")


def _tick(world, turns=1):
    events = []
    for _ in range(turns):
        with contextlib.redirect_stdout(io.StringIO()):
            events.extend(W.process_evacuation_grants(world))
    return events


# ═══════════════════════════════════════════════════════════════════════════
# FA-S12-1 — the peace that stranded nobody still leaves a door
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDoorIsLeftOpen:

    def test_a_stranding_free_peace_writes_a_window(self):
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        key = world._make_diplo_key("France", "Russia")
        assert world.corridor_windows == {
            key: world.current_turn + W.CORRIDOR_MINIMUM_WINDOW}
        assert world.evacuation_grants == {}, (
            "the rollback still stands — a window is not a grant")

    def test_the_control_arm_abandons_him(self, monkeypatch):
        """Without the lever the tick returns at `if not grants:` forever."""
        monkeypatch.setattr(W, "CORRIDOR_MINIMUM_WINDOW_ACTIVE", False)
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        assert world.corridor_windows == {}
        world.marshals["Davout"].location = "Volhynia"
        events = _tick(world, 5)
        assert world.evacuation_grants == {}
        assert events == []
        assert world.marshals["Davout"].strategic_order is None

    def test_a_corps_stranded_inside_the_window_is_handed_a_road(self):
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        world.marshals["Davout"].location = "Volhynia"
        events = _tick(world)
        key = world._make_diplo_key("France", "Russia")
        assert key in world.evacuation_grants
        assert key not in world.corridor_windows, "the window is spent"
        assert any(e.get("type") == "evacuation_granted" for e in events)
        assert world.marshals["Davout"].strategic_order is not None


class TestAWindowIsNotARightOfTransit:
    """The whole Trojan-corridor question, closed by construction: a window is
    invisible to `has_evacuation_grant`, so nobody can walk on one."""

    def test_a_standing_window_grants_nothing(self):
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        assert world.corridor_windows, "fixture: a window must be standing"
        assert W.has_evacuation_grant(
            world, "France", "Russia", "Volhynia") is False

    def test_once_promoted_only_the_stranded_corps_may_walk(self):
        """WO-17's direction term still owns the answer."""
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        world.marshals["Davout"].location = "Volhynia"
        _tick(world)
        assert W.has_evacuation_grant(
            world, "France", "Russia", "Volhynia") is True
        assert W.has_evacuation_grant(
            world, "France", "Russia", "Paris") is False


class TestTheCorridorIsSizedAtDiscovery:
    """⚠ The difference between a fix and a corps-killer. Sizing from the
    treaty turn hands a corps a clock that has already been running."""

    def test_the_clock_starts_when_he_is_found(self):
        """The surplus a corps is handed must not depend on how long ago the
        peace was — that is the whole content of "sized at discovery".

        ⚠ Asserting only `expiry > current` (or a loose floor) is too weak:
        a treaty-sized corridor still leaves several turns on the clock, and
        the mutation sweep found exactly that pin INERT. Two arms, same
        surplus.
        """
        surpluses = []
        for delay in (0, W.CORRIDOR_MINIMUM_WINDOW):
            world = _boot()
            _everyone_home(world)
            _quiet_peace(world)
            world.current_turn += delay
            world.marshals["Davout"].location = "Volhynia"
            _tick(world)
            key = world._make_diplo_key("France", "Russia")
            expiry = world.evacuation_grants[key]
            assert expiry > world.current_turn, delay
            surpluses.append(expiry - world.current_turn)
        assert surpluses[0] == surpluses[1], (
            f"a corps discovered {W.CORRIDOR_MINIMUM_WINDOW} turns after the "
            f"peace was handed a shorter clock: {surpluses}")

    def test_he_is_not_interned_on_the_turn_he_is_discovered(self):
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        world.current_turn += W.CORRIDOR_MINIMUM_WINDOW
        world.marshals["Davout"].location = "Volhynia"
        events = _tick(world)
        assert not any(e.get("type") == "marshal_interned" for e in events)
        assert "Davout" in world.marshals

    def test_the_promotion_writes_a_provisional_grant_first(self):
        """⚠ Without it the promotion NEVER FIRES — measured, and it is how
        this shipped broken the first time.

        `distance_home` routes WITH the corridor (it must — the corridor IS
        the road), so asking "how far is he from home" before writing the
        grant asks him to walk a road that does not exist and he answers
        "no road". `open_evacuation_corridor` solves it the same way.
        """
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        davout = world.marshals["Davout"]
        davout.location = "Volhynia"
        home = W.get_home_zone(world, "France")
        # The pre-condition that makes the trap real: with no grant standing
        # he has no measurable road at all.
        assert W.distance_home(world, davout, home) is None
        _tick(world)
        assert world.evacuation_grants, (
            "the promotion measured the road before opening it")


class TestTheDoorHasAHorizon:
    """The honest limit of the fix, and the only place the constant is
    falsifiable: a corps stranded more than CORRIDOR_MINIMUM_WINDOW turns
    after the peace is not helped at all."""

    def test_past_the_window_he_is_on_his_own(self):
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        world.current_turn += W.CORRIDOR_MINIMUM_WINDOW + 1
        world.marshals["Davout"].location = "Volhynia"
        _tick(world)
        assert world.evacuation_grants == {}
        assert world.corridor_windows == {}, "the lapsed window is retired"

    def test_the_horizon_is_the_constant(self):
        for delay, expected in ((0, True), (W.CORRIDOR_MINIMUM_WINDOW, True),
                                (W.CORRIDOR_MINIMUM_WINDOW + 1, False)):
            world = _boot()
            _everyone_home(world)
            _quiet_peace(world)
            world.current_turn += delay
            world.marshals["Davout"].location = "Volhynia"
            _tick(world)
            assert bool(world.evacuation_grants) is expected, delay


class TestTheWindowKnowsWhenNotToOpen:

    def test_a_state_that_already_opens_the_border_writes_nothing(self):
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world, state="VASSAL")
        assert world.corridor_windows == {}

    def test_the_all_cut_off_branch_gets_one_too(self):
        """Symmetry is the argument: withholding it would mean a peace that
        stranded people we could not help affords LESS than a peace that
        stranded nobody."""
        world = _boot()
        _everyone_home(world)
        davout = world.marshals["Davout"]
        davout.location = "Ionian Islands"
        _quiet_peace(world, "France", "Austria")
        home = W.get_home_zone(world, "France")
        if W.distance_home(world, davout, home) is not None:
            pytest.skip("fixture drift: this province is reachable by land")
        assert world._make_diplo_key("France", "Austria") in world.corridor_windows

    def test_a_resumed_war_purges_the_window(self):
        """§3.4: a peace instrument cannot outlive the peace — and a window
        that survived would promote into a real corridor the moment somebody
        was found stranded."""
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        assert world.corridor_windows
        _quiet_peace(world, state="WAR")
        assert world.corridor_windows == {}

    def test_the_boot_board_writes_none(self):
        assert _boot().corridor_windows == {}


class TestTheWindowSurvivesTheSave:

    def test_it_round_trips(self):
        world = _boot()
        _everyone_home(world)
        _quiet_peace(world)
        assert world.corridor_windows
        with contextlib.redirect_stdout(io.StringIO()):
            restored = WorldState.from_dict(world.to_dict())
        assert restored.corridor_windows == world.corridor_windows

    def test_a_legacy_save_with_no_key_loads_empty(self):
        world = _boot()
        data = world.to_dict()
        data.pop("corridor_windows", None)
        with contextlib.redirect_stdout(io.StringIO()):
            restored = WorldState.from_dict(data)
        assert restored.corridor_windows == {}


# ═══════════════════════════════════════════════════════════════════════════
# FA-S12-2 — the fourth exit, and the fifth
# ═══════════════════════════════════════════════════════════════════════════

def _eliminate_satellite(world, satellite="KingdomOfItaly"):
    for region in world.regions.values():
        if region.controller == satellite:
            region.controller = "Austria"
    with contextlib.redirect_stdout(io.StringIO()):
        world._eliminate_nation(satellite)


class TestTheFourthExitRelievesTheLord:

    def test_the_empire_is_one_satellite_smaller(self):
        world = _boot()
        assert world.vassals.get("KingdomOfItaly", {}).get("lord") == "France"
        before = int(world.threat_by_target.get("France", world.threat_level))
        _eliminate_satellite(world)
        after = int(world.threat_by_target.get("France", world.threat_level))
        assert after == before - 10

    def test_the_control_arm_relieves_nothing(self, monkeypatch):
        import backend.models.world_state as WSM
        monkeypatch.setattr(WSM, "ELIMINATION_RELIEVES_THE_LORD", False)
        world = _boot()
        before = int(world.threat_by_target.get("France", world.threat_level))
        _eliminate_satellite(world)
        assert int(world.threat_by_target.get(
            "France", world.threat_level)) == before

    def test_the_empire_does_not_dock_itself(self):
        """The ordering trap: sited BEFORE the pop, the departing row still
        satisfies `other_state["lord"] == lord`."""
        world = _boot()
        sources = []
        _eliminate_satellite(world)
        sources = [s for s in getattr(world, "threat_sources_this_turn", [])
                   if s.get("source") == "vassal_lost_to_conquest"]
        assert len(sources) == 1, sources
        assert sources[0].get("target") == "France"

    def test_the_relief_is_labelled_on_the_ledger(self):
        assert (_THREAT_SOURCE_LABELS["vassal_lost_to_conquest"]
                == "Lost a satellite to conquest")


class TestTheThreeDeclines:
    """Each decline is a ruling, so each is pinned. A decline nobody can see
    is indistinguishable from an omission."""

    def test_the_siblings_do_not_notice(self):
        """`check_vassal_rebellion`'s -10 is a defiance-is-contagious signal,
        and a satellite EATEN by a rival demonstrates the opposite. It is also
        the only arm that costs France a province against the FA-D27 gate."""
        world = _boot()
        before = int(world.vassals["Holland"]["loyalty"])
        _eliminate_satellite(world)
        assert int(world.vassals["Holland"]["loyalty"]) == before

    def test_no_relation_moves(self):
        """There is no court left to be angry with."""
        world = _boot()
        key = world._make_diplo_key("France", "KingdomOfItaly")
        before = world.nation_relations.get(key)
        _eliminate_satellite(world)
        assert world.nation_relations.get(key) == before

    def test_no_corps_is_handed_back_on_the_satellite_path(self):
        """An assimilated contingent flies the LORD's flag and has no
        homeland to return to. Neither siting is right: before the sweep it
        acquires the dead satellite's name and dies; after, it is an orphan of
        a nation with no territory."""
        world = _boot()
        soult = world.marshals["Soult"]
        soult.original_nation = "KingdomOfItaly"
        _eliminate_satellite(world)
        assert soult.nation == "France"
        assert soult.original_nation == "KingdomOfItaly"


class TestTheFifthExitIsWorseThanTheFourth:
    """When a LORD is eliminated the same handler frees its satellites in
    total silence — and the satellite's own corps is DESTROYED and tombstoned
    under the lord's flag, because the marshal sweep keys on `m.nation`."""

    @staticmethod
    def _kill_the_lord(world):
        world.vassals["Bavaria"] = {"lord": "Austria", "loyalty": 80,
                                    "autonomy": 50}
        corps = world.marshals["Mack"]
        corps.original_nation = "Bavaria"
        corps.nation = "Austria"
        for region in world.regions.values():
            if region.controller == "Austria":
                region.controller = "France"
        with contextlib.redirect_stdout(io.StringIO()):
            world._eliminate_nation("Austria")
        return corps

    def test_the_freed_satellite_keeps_its_army(self):
        world = _boot()
        self._kill_the_lord(world)
        assert "Mack" in world.marshals
        assert world.marshals["Mack"].nation == "Bavaria"
        assert world.marshals["Mack"].original_nation is None
        assert "Mack" not in world.fallen_marshals

    def test_the_control_arm_annihilates_it_under_the_lords_flag(
            self, monkeypatch):
        import backend.models.world_state as WSM
        monkeypatch.setattr(WSM, "FREED_SATELLITE_KEEPS_ITS_ARMY", False)
        world = _boot()
        self._kill_the_lord(world)
        assert "Mack" not in world.marshals
        assert world.fallen_marshals.get("Mack", {}).get("nation") == "Austria"

    def test_the_freeing_is_no_longer_silent(self):
        world = _boot()
        self._kill_the_lord(world)
        rows = [e for e in world.event_log
                if e.get("type") == "vassal_broke_free"
                and e.get("vassal") == "Bavaria"]
        assert len(rows) == 1, rows
        assert rows[0]["exit"] == "lord_eliminated"
        assert rows[0]["lord"] == "Austria"

    def test_the_one_liner_does_not_declare_a_war_nobody_fought(self):
        """⚠ Reuse is not free. Without its own arm the `lord_eliminated`
        exit falls through to "…has broken free of {lord}. War." — wrong in
        every clause: nobody broke anything and there is no war."""
        line = format_event_oneliner({
            "type": "vassal_broke_free", "vassal": "Bavaria",
            "lord": "Austria", "exit": "lord_eliminated", "turn": 5})
        assert "War" not in line
        assert "rebellion" not in line.lower()
        assert "Austria has fallen" in line and "Bavaria" in line

    def test_no_new_campaign_log_type_was_minted(self):
        """Minting one costs twelve pins across twelve files and forfeits the
        fog arm, the one-liner switch and the dispatch consumer that the reuse
        inherits for free."""
        assert len(CAMPAIGN_LOG_TYPES) == 161
        assert "vassal_freed_by_conquest" not in CAMPAIGN_LOG_TYPES
