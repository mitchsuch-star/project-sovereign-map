"""FA slice 11 — the three-lens review round (September 5, 2026).

Three lenses at `63924903`. **Seventeen of the twenty-three agents died on a
session usage limit mid-run**, so the refuter verdicts are missing for most
rows and every finding below was verified by hand instead. That is worth
saying plainly: the workflow's own `survives: false` on those rows is an
artefact of the failure, not a judgement, and treating it as one would have
buried a P2.

**Two lenses independently found the same P2, and it is a fix I shipped
production-dead.** FA-N33's client arm read `action.get("captured_from")`.
The backend stamps the capture on `events[0]`, and the action dict IS the
executor result — measured, its top-level keys are exactly
`[action_info, action_summary, drill_cancelled, events, message, new_state,
success]`. So the enemy-phase dialog still said "Mack moves to Rhineland" and
nothing else. Worse, the pin meant to prove the fix was a source-text census
for the wrong expression, which is precisely the trap the slice-10 round had
just taught — and I walked into it one slice later.

**Three lenses independently found the second one.** FA-2 gave the armistice
exit an early `continue` so it would stop falling through to the war tail's
"War declared." copy — and took FOUR MECHANICAL effects with it, which the
comment did not name and the record did not disclose. Measured, armistice
exit, before and after:

    the freed nation's corps come home      False  ->  True
    a sibling satellite notices (loyalty)   100    ->  90
    relation with the freed court           0      ->  -50
    the lord's coalition threat             70     ->  60

The GRACEFUL-INDEPENDENCE exit had the same gap since long before the slice —
its own `continue` predates it and the lever does not reach that branch —
which matters because that is the exit BOTH big satellites take on the 1805
board. All three exits share one helper now.

The rest: the CRITICAL rebellion banner was the one surface in the family
left lord-blind, and once its siblings became lord-aware it contradicted them
(measured: an Austria-lorded Bavaria rebelling raised *"Bavaria has rebelled
against Austria! War declared."* on FRANCE's rail, ungated); the new
campaign-log fog arm read one court where every sibling reads two; and
`coalition_member_rows` carried whole 32-key rows where the card reads six,
measured at 3,578 -> 13,630 bytes of `active_wars` on every HTTP response.
"""

import contextlib
import io
import json
from pathlib import Path

import pytest

import backend.campaign_log as CL
import backend.game_logic.vassal as VASSAL
import backend.game_logic.war_status as WS
from backend.campaign_log import filter_campaign_log
from backend.commands.executor import CommandExecutor
from backend.game_logic.vassal import check_vassal_rebellion
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
DIALOG = (ROOT / "godot-client" / "project-sovereign" / "scripts"
          / "enemy_phase_dialog.gd")

LEVERS = [
    (VASSAL, "THE_BREAK_IS_BRIEFED_TRUTHFULLY"),
    (VASSAL, "EVERY_BREAK_COMPLETES_ITSELF"),
    (WS, "COALITION_CARD_KEEPS_ITS_MEMBERS"),
]


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = [(mod, name, getattr(mod, name)) for mod, name in LEVERS]
    yield
    for mod, name, value in saved:
        setattr(mod, name, value)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


def _relation(w, a, b):
    return w.nation_relations.get(w._make_diplo_key(a, b), 0)


def _assimilate(w, vassal):
    """Give the satellite a corps serving under its lord's flag."""
    corps = next(m for m in w.marshals.values() if m.nation == "France")
    corps.original_nation = vassal
    return corps


def _sibling(w, vassal):
    return next(n for n, s in w.vassals.items()
                if s["lord"] == "France" and n != vassal)


def _move_arm() -> str:
    """The body of enemy_phase_dialog's `match action_type` "move" arm.

    Anchored on the INDENTED arm label, not on the bare string. The arm's
    own body contains `!= "move":`, so slicing on that naively cuts the
    extract off three lines ABOVE the code under test — which is how the
    first cut of this pin passed while reading the wrong region. A source
    pin that reads the wrong region is the same class of defect this round
    was called to find.
    """
    src = DIALOG.read_text(encoding="utf-8").replace("\r\n", "\n")
    start = src.index('\n\t\t"move":\n')
    end = src.index('\n\t\t"forced_march":', start)
    return src[start:end]


# ═══════════════════════════════════════════════════════════════════════
# The break completes itself, whichever exit it took
# ═══════════════════════════════════════════════════════════════════════


class TestEveryBreakCompletesItself:

    def _break(self, world, vassal, *, armistice=False):
        world.vassals[vassal]["loyalty"] = 0
        if armistice:
            key = world._make_diplo_key("France", vassal)
            world.diplomatic_states[key] = "ARMISTICE"
        corps = _assimilate(world, vassal)
        sibling = _sibling(world, vassal)
        before = {
            "sibling": world.vassals[sibling]["loyalty"],
            "relation": _relation(world, "France", vassal),
            "threat": int(getattr(world, "threat_level", 0)),
        }
        with _quiet():
            events = check_vassal_rebellion(world)
        return corps, sibling, before, events

    def test_the_armistice_exit_sends_the_corps_home(self, world):
        """The measured regression. The `continue` FA-2 added to stop the
        false "War declared." copy took the marshal transfer-back with it, so
        the freed nation's own corps stayed under its ex-lord's flag."""
        corps, _sib, _before, events = self._break(
            world, "Switzerland", armistice=True)
        assert [e.get("type") for e in events] == [
            "vassal_rebellion_armistice"]
        assert corps.nation == "Switzerland"
        assert getattr(corps, "original_nation", None) is None

    def test_the_armistice_exit_still_moves_the_world(self, world):
        _corps, sibling, before, _events = self._break(
            world, "Switzerland", armistice=True)
        assert world.vassals[sibling]["loyalty"] == before["sibling"] - 10
        assert _relation(world, "France", "Switzerland") == (
            before["relation"] - 50)
        assert int(world.threat_level) == before["threat"] - 10

    def test_the_armistice_exit_raises_no_war_alarm(self, world):
        """What the `continue` was FOR: the shared tail's CRITICAL banner and
        `vassal_rebellion` event both say "War declared." of a break in which
        none was."""
        world.vassals["Switzerland"]["loyalty"] = 0
        key = world._make_diplo_key("France", "Switzerland")
        world.diplomatic_states[key] = "ARMISTICE"
        before = len(world.notifications.to_list())
        with _quiet():
            check_vassal_rebellion(world)
        fresh = world.notifications.to_list()[before:]
        assert not any("War declared" in str(n.get("message") or "")
                       for n in fresh), fresh
        assert world.get_diplomatic_state("France", "Switzerland") == "ARMISTICE"

    def test_the_graceful_exit_completes_too(self, world):
        """PRE-EXISTING: this exit's own `continue` predates slice 11 and the
        FA-2 lever does not reach it — and it is the exit BOTH big satellites
        take on the shipped board, so its corps were stranded forever."""
        corps, sibling, before, events = self._break(world, "Holland")
        assert [e.get("type") for e in events] == [
            "vassal_rebellion_independent"]
        assert corps.nation == "Holland"
        assert world.vassals[sibling]["loyalty"] == before["sibling"] - 10
        assert _relation(world, "France", "Holland") == before["relation"] - 50

    def test_the_war_exit_is_unchanged(self, world):
        """The tail was EXTRACTED, not altered: the exit that always ran it
        must still see exactly the same four effects, once each."""
        corps, sibling, before, _events = self._break(world, "Switzerland")
        assert corps.nation == "Switzerland"
        assert world.vassals[sibling]["loyalty"] == before["sibling"] - 10
        assert _relation(world, "France", "Switzerland") == (
            before["relation"] - 50)

    def test_the_lever_down_reproduces_the_gap(self, world):
        VASSAL.EVERY_BREAK_COMPLETES_ITSELF = False
        corps, sibling, before, _events = self._break(
            world, "Switzerland", armistice=True)
        assert corps.nation == "France"
        assert world.vassals[sibling]["loyalty"] == before["sibling"]
        assert _relation(world, "France", "Switzerland") == before["relation"]

    def test_no_exit_applies_the_tail_twice(self, world):
        """Found by the lever arm itself: the helper call has to sit INSIDE
        the same gate as the `continue`, or with the briefing lever down the
        armistice arm falls through to the war tail and both apply it
        (measured: sibling -20, relation -100)."""
        VASSAL.THE_BREAK_IS_BRIEFED_TRUTHFULLY = False
        _corps, sibling, before, _events = self._break(
            world, "Switzerland", armistice=True)
        assert world.vassals[sibling]["loyalty"] == before["sibling"] - 10
        assert _relation(world, "France", "Switzerland") == (
            before["relation"] - 50)

    def test_the_war_only_reclaim_is_not_shared(self):
        """The helper deliberately excludes the VS-3 granted-province
        reclaim: flipping provinces back during a respected armistice would
        itself be a treaty violation, and the WAR branch documents that."""
        import inspect
        body = inspect.getsource(VASSAL.complete_vassal_break)
        assert "granted_regions" not in body
        assert "controller" not in body


# ═══════════════════════════════════════════════════════════════════════
# The rail banner knows whose satellite it was
# ═══════════════════════════════════════════════════════════════════════


class TestTheRailBannerKnowsTheLord:

    def _foreign_break(self, world):
        world.vassals["Bavaria"] = {
            "lord": "Austria", "loyalty": 0, "autonomy": 50,
            "tribute_rate": 0.1, "created_turn": 0}
        before = len(world.notifications.to_list())
        with _quiet():
            check_vassal_rebellion(world)
        return world.notifications.to_list()[before:]

    def test_a_foreign_lords_rebellion_raises_no_crisis_banner(self, world):
        """Measured before: France's own rail carried a CRITICAL
        "Bavaria has rebelled against Austria! War declared." — a crisis
        banner about somebody else's satellite, ungated by fog. It was the
        one surface in the family left lord-blind, and once the dispatch line
        and the log row became lord-aware it contradicted both."""
        fresh = self._foreign_break(world)
        assert not any("rebelled against" in str(n.get("message") or "")
                       for n in fresh), fresh

    def test_the_break_still_happened(self, world):
        """The banner is silenced, not the event — otherwise the pin above
        would pass on a rebellion that never fired."""
        self._foreign_break(world)
        assert "Bavaria" not in world.vassals
        rows = [e for e in world.event_log
                if e.get("type") == "vassal_broke_free"]
        assert rows and rows[-1]["lord"] == "Austria"

    def test_our_own_satellite_still_raises_it(self, world):
        world.vassals["Switzerland"]["loyalty"] = 0
        before = len(world.notifications.to_list())
        with _quiet():
            check_vassal_rebellion(world)
        fresh = world.notifications.to_list()[before:]
        assert any("Switzerland has rebelled against France" in
                   str(n.get("message") or "") for n in fresh), fresh

    def test_the_lever_down_restores_the_lord_blind_banner(self, world):
        VASSAL.THE_BREAK_IS_BRIEFED_TRUTHFULLY = False
        fresh = self._foreign_break(world)
        assert any("rebelled against Austria" in str(n.get("message") or "")
                   for n in fresh), fresh


# ═══════════════════════════════════════════════════════════════════════
# The fog arm reads both courts
# ═══════════════════════════════════════════════════════════════════════


class TestTheFogArmReadsBothCourts:

    def _log_foreign_break(self, world):
        VASSAL.record_vassal_break(
            world, vassal="Bavaria", lord="Austria",
            exit_path="vassal_rebellion")

    def _visible(self, world):
        with _quiet():
            rows = filter_campaign_log(world.event_log, world)
        return [e for e in rows if e.get("type") == "vassal_broke_free"]

    def test_a_break_from_a_lord_we_watch_is_news(self, world):
        """Every sibling vassal arm in `filter_campaign_log` reads BOTH
        courts (`for nation in (vassal, overlord)`); this one read the vassal
        alone, so a satellite breaking from a lord we watch closely was
        hidden when the satellite itself was dark."""
        from backend.models.intel import UNKNOWN
        for region in world.regions.values():
            if region.controller == "Bavaria":
                world.get_region_intel(region.name).visibility = UNKNOWN
        self._log_foreign_break(world)
        assert self._visible(world)

    def test_a_break_between_two_courts_we_cannot_see_is_hidden(self, world):
        """The gate is still a gate."""
        from backend.models.intel import UNKNOWN
        for region in world.regions.values():
            if region.controller in ("Bavaria", "Austria"):
                world.get_region_intel(region.name).visibility = UNKNOWN
        self._log_foreign_break(world)
        assert not self._visible(world)

    def test_our_own_satellite_is_always_shown(self, world):
        VASSAL.record_vassal_break(
            world, vassal="Holland", lord="France",
            exit_path="vassal_rebellion_independent")
        assert self._visible(world)


# ═══════════════════════════════════════════════════════════════════════
# The coalition rows carry what the card reads
# ═══════════════════════════════════════════════════════════════════════


class TestTheCoalitionRowsAreNotWholeRows:

    def _card(self, world):
        world.war_exhaustion = {"Britain": 20, "Austria": 55, "Russia": 31}
        with _quiet():
            return WS.build_active_wars(world)

    def test_a_member_row_carries_only_what_the_card_reads(self, world):
        """Measured: whole rows are 32 keys each and took `active_wars` from
        3,578 to 13,630 bytes on EVERY response."""
        data = self._card(world)
        folded = next(r["coalition_member_rows"] for r in data["wars"]
                      if r.get("coalition_member_rows"))
        assert set(folded[0]) == set(WS.COALITION_MEMBER_ROW_KEYS)
        assert len(folded[0]) == 7

    def test_the_payload_cost_is_small(self, world):
        with _quiet():
            WS.COALITION_CARD_KEEPS_ITS_MEMBERS = False
            base = len(json.dumps(WS.build_active_wars(world), default=str))
            WS.COALITION_CARD_KEEPS_ITS_MEMBERS = True
            full = len(json.dumps(WS.build_active_wars(world), default=str))
        assert full - base < 2000, (base, full)

    def test_each_member_keeps_its_own_fogging(self, world):
        """The point of carrying them at all: the collapsed row's
        `war_exhaustion` is the LEADER's."""
        data = self._card(world)
        folded = next(r["coalition_member_rows"] for r in data["wars"]
                      if r.get("coalition_member_rows"))
        by_nation = {r["opponent"]: r for r in folded}
        assert by_nation["Austria"]["war_exhaustion"] == 55
        assert by_nation["Britain"]["war_exhaustion"] is None

    def test_the_card_still_gets_its_members(self, world):
        data = self._card(world)
        rows = WS._coalition_rows(data["wars"])
        assert [r["opponent"] for r in rows if r["in_coalition"]] == [
            "Britain", "Austria", "Russia"]
        assert data["coalition"]["weak_link"] == "Austria"


# ═══════════════════════════════════════════════════════════════════════
# The client reads what the backend writes
# ═══════════════════════════════════════════════════════════════════════


class TestTheClientReadsWhatTheBackendWrites:

    def _ai_capture(self, world):
        for m in list(world.marshals.values()):
            if m.location == "Rhineland" and m.nation == "France":
                m.location = "Paris"
        world.regions["Rhineland"].garrison = 0
        executor = CommandExecutor()
        with _quiet():
            return executor.execute(
                {"command": {"action": "move", "marshal": "Mack",
                             "target": "Rhineland",
                             "_acting_nation": "Austria"}},
                {"world": world, "executor": executor})

    def test_the_capture_is_not_at_the_top_level_of_the_action(self, world):
        """The measurement that killed the first cut. The enemy-phase action
        dict IS the executor result (`enemy_ai` stamps `ai_action` onto it),
        and the capture lives on `events[0]` — so an arm reading
        `action.get("captured_from")` can never fire."""
        result = self._ai_capture(world)
        assert result.get("success") is True, result.get("message")
        assert "captured_from" not in result
        assert "capture_choice" not in result
        move = next(e for e in result["events"] if e.get("type") == "move")
        assert move["captured_from"] == "France"
        assert move["capture_choice"] in ("secure", "plunder")

    def test_the_client_arm_reads_the_event_and_not_the_action(self):
        """A source pin, but a REAL one: it asserts the arm reads the place
        the pin above proves the data is in, and that it does NOT read the
        place the pin above proves is empty. The first cut's pin asserted
        only that a literal existed, which a wrong expression satisfies."""
        arm = _move_arm()
        assert 'action.get("events"' in arm
        assert 'mv.get("captured_from"' in arm
        assert 'mv.get("capture_choice"' in arm
        assert 'action.get("captured_from"' not in arm
        assert 'action.get("capture_choice"' not in arm

    def test_it_only_reads_a_move_event(self, world):
        """A conquest event carries `captured_from` too and has its own arm
        below; the move arm must not double-report it."""
        assert 'str(mv.get("type", "")) != "move"' in _move_arm()

    def test_a_plain_march_says_nothing_extra(self, world):
        """The arm is silent when nothing changed hands. Mack marches onto
        Austria's OWN soil (Franconia, adjacent to his boot province at
        Swabia), so no capture can occur."""
        world.regions["Franconia"].controller = "Austria"
        for m in list(world.marshals.values()):
            if m.location == "Franconia":
                m.location = "Paris"
        executor = CommandExecutor()
        with _quiet():
            result = executor.execute(
                {"command": {"action": "move", "marshal": "Mack",
                             "target": "Franconia",
                             "_acting_nation": "Austria"}},
                {"world": world, "executor": executor})
        assert result.get("success") is True, result.get("message")
        moves = [e for e in result.get("events", [])
                 if e.get("type") == "move"]
        assert moves, result.get("events")
        assert "captured_from" not in moves[0]
        assert "capture_choice" not in moves[0]
