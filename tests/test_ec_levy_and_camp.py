"""EC-L — "The Levy Is Open" + the Camp of Boulogne (ROADMAP position 3.5).

The econ spec review (`docs/audits/ECON_SPEC_REVIEW_2026_08_04.md`) accepted
half the August-3 memo and replaced the other half:

  (a)  The Levy is Open — the establishment as a first-class number, on the
       ledger, in the dispatch and on the region panel. The measured defect:
       France boots +59,000 OVER its own force limit, so ten turns teach that
       recruitment is forbidden; by turn 12 it stood under the limit with a
       full pool, and NOTHING said so. The ledger even rendered the force
       limit only inside `if over_limit_surcharge > 0` — visible exactly while
       the gate was shut.
  (a2) The strength-share threat term — every passive threat contributor read
       TERRITORY, so a power that grew stronger without growing bigger was
       invisible to Europe. That made "stop conquering, re-arm, strike a
       Europe that stopped watching" dominant, and (a) makes it reachable.
  (b') Drill restores morale — REPLACING the memo's proposed
       `Marshal.readiness`. Morale is already a 0-100 condition stat feeding
       combat at 0.90x-1.50x; green conscripts already arrive at 40 and
       dilute the corps; `training_ground` already lifts that to 70. What was
       missing is that morale NEVER moves in peacetime, so the axis was
       one-way: a corps could be debased by rebuilding and never trained
       back. Zero new serialized fields.
  (c)  The supply-strain headline — `supply_attrition` was not in
       HEADLINE_WEIGHTS at all, so the drain that took the played campaign
       from 189,000 men to 60,183 could never lead a dispatch. Inherits the
       intent of the CUT EC-7 / ES-6.
"""

import pathlib

import backend.game_logic.dispatch as dispatch_mod
import backend.game_logic.coalition as coalition_mod
from backend.commands.economy_executor import get_levy_status
from backend.game_logic.dispatch import _build_headline
from backend.game_logic.ledger import build_strategic_ledger
from backend.models.region import BUILDING_TYPES
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory

EUROPE_SCENARIO = (
    pathlib.Path(__file__).resolve().parents[1] / "godot-client"
    / "project-sovereign" / "assets" / "maps" / "europe_1805.json")


def _europe():
    return WorldState.from_scenario(str(EUROPE_SCENARIO))


def _french(world):
    return [m for m in world.marshals.values()
            if m.nation == "France" and m.strength > 0]


def _maul(world, factor=0.38):
    """Take France down to roughly the turn-12 state of the played campaign."""
    for m in _french(world):
        m.strength = int(m.strength * factor)


# ════════════════════════════════════════════════════════════════════════
# (a) The Levy is Open
# ════════════════════════════════════════════════════════════════════════

class TestLevyStatus:
    def test_boot_france_is_over_its_own_force_limit(self):
        """The measured defect, pinned: the first ten turns teach that
        recruiting is forbidden, and they are telling the truth."""
        levy = get_levy_status(_europe())
        assert levy["force_limit"] == 130_000
        assert levy["army_strength"] == 189_000
        assert levy["over_by"] == 59_000
        assert levy["headroom"] == 0
        assert levy["open"] is False

    def test_the_gate_opens_when_the_army_falls(self):
        world = _europe()
        _maul(world)
        levy = get_levy_status(world)
        assert levy["over_by"] == 0
        assert levy["headroom"] > 10_000
        assert levy["open"] is True

    def test_the_open_price_is_the_memos_measured_450(self):
        """⊕ 450g per 10,000 foot at Paris — the purchase that would have
        saved the campaign, quoted from the single source that charges it."""
        world = _europe()
        _maul(world)
        levy = get_levy_status(world)
        assert levy["infantry_amount"] == 10_000
        assert levy["infantry_price"] == 450

    def test_being_over_the_limit_prices_the_levy_higher(self):
        """Shown = applied: the boot price carries W6-11's overage multiplier,
        so the number the player reads is the number he would pay."""
        assert (get_levy_status(_europe())["infantry_price"]
                > 450)

    def test_an_empty_pool_keeps_the_gate_shut(self):
        """Headroom alone is not an offer — the depots must be able to fill
        it. Both halves were true from turn 12 and neither was reported."""
        world = _europe()
        _maul(world)
        world.manpower_pools["France"]["infantry"] = 0
        assert get_levy_status(world)["open"] is False

    def test_the_legacy_world_has_no_establishment(self):
        """force_limit 0 is the existing 'do not render' sentinel (GR2)."""
        levy = get_levy_status(WorldFactory.basic())
        assert levy["force_limit"] == 0
        assert levy["open"] is False

    def test_the_ledger_carries_it(self):
        world = _europe()
        _maul(world)
        econ = build_strategic_ledger(world)["economy"]
        assert econ["levy"]["open"] is True
        assert econ["levy"]["headroom"] == get_levy_status(world)["headroom"]

    def test_the_map_summary_carries_it(self):
        """The region panel's source — nation-level, computed once, never a
        per-province scan (GR8)."""
        world = _europe()
        summary = world.get_game_state_summary()
        assert "levy" in summary
        assert summary["levy"]["force_limit"] == 130_000


class TestLevyHeadline:
    def test_silent_while_the_gate_is_shut(self):
        world = _europe()
        head = _build_headline(world, "France") or {}
        assert head.get("class") != "levy_open"

    def test_it_speaks_the_moment_the_gate_opens(self):
        world = _europe()
        _maul(world)
        head = _build_headline(world, "France") or {}
        assert head.get("class") == "levy_open"
        assert "450 gold" in head["text"]
        assert "Paris" in head["text"]

    def test_it_is_a_standing_class_so_it_cannot_become_a_stuck_record(self):
        """PC-7's lesson applies to it exactly: it is a STATE predicate that
        re-manufactures its candidate every turn the offer stands. Riding the
        existing cooldown is also why this needs no serialized memory of the
        over->under flip."""
        assert "levy_open" in dispatch_mod.STANDING_HEADLINE_CLASSES
        assert "levy_open" in dispatch_mod._STANDING_ESCALATION

    def test_it_escalates_rather_than_repeating(self):
        world = _europe()
        _maul(world)
        seen = []
        for _ in range(5):
            seen.append((_build_headline(world, "France") or {}).get("text"))
        assert all(t for t in seen)
        # Two at the base wording, then the ladder must say something new.
        assert len(set(seen)) >= 3, seen
        assert any("nobody has asked for them" in t for t in seen), seen

    def test_it_never_outranks_a_wound(self):
        """An opportunity sits below every crisis — pin 13's discipline."""
        w = dispatch_mod.HEADLINE_WEIGHTS
        assert w["levy_open"] < w["estate_eroding"]
        assert w["levy_open"] < w["region_lost"]
        assert w["levy_open"] < w["home_captured"]


# ════════════════════════════════════════════════════════════════════════
# (a2) The strength-share threat term
# ════════════════════════════════════════════════════════════════════════

class TestEstablishmentThreat:
    def test_nobody_accrues_at_boot(self):
        """⊕ France is 31.5% of Europe's 600,000 standing men, so the 0.40
        gate is boot-zero for every court — the pin that keeps this from
        being a hidden opening-turn balance change."""
        world = _europe()
        totals = coalition_mod._standing_strength_by_nation(world)
        europe = sum(totals.values())
        assert europe == 600_000
        assert max(totals.values()) / europe < coalition_mod.ESTABLISHMENT_THREAT_SHARE

    def test_a_re_arming_hegemon_becomes_visible(self):
        world = _europe()
        for m in world.marshals.values():
            if m.nation != "France":
                m.strength = int(m.strength * 0.25)
        before = int(world.threat_level)
        coalition_mod._establishment_threat(world, "France")
        assert int(world.threat_level) > before

    def test_it_is_actually_WIRED_into_the_turn(self):
        """FALSIFIABLE WIRING PIN. The test above drives the function
        directly, so it passes just as happily when the call site is gone —
        the mutation sweep caught exactly that, and a production-dead
        contributor is this project's most-repeated defect shape (NA-3's
        grudge shipped dead for the same reason). This one goes through
        `process_coalition_turn`, which is what actually runs each turn.
        """
        world = _europe()
        for m in world.marshals.values():
            if m.nation != "France":
                m.strength = int(m.strength * 0.25)
        world.threat_sources_this_turn = []
        coalition_mod.process_coalition_turn(world)
        sources = {s.get("source") for s in world.threat_sources_this_turn}
        assert "military_establishment" in sources, sorted(sources)

    def test_it_is_symmetric(self):
        """GR5: a re-arming Austria is seen too, in its own slot."""
        world = _europe()
        for m in world.marshals.values():
            if m.nation not in ("Austria",):
                m.strength = int(m.strength * 0.05)
        coalition_mod._establishment_threat(world, "France")
        assert int(world.threat_by_target.get("Austria", 0)) > 0

    def test_the_legacy_world_is_untouched(self):
        """N1 + the measured reason: the 19-region fixture is four French
        corps against seven enemy ones, so a SHARE gate trips there at once
        and perturbs pins that have nothing to do with this mechanic."""
        world = WorldFactory.basic()
        before = int(world.threat_level)
        coalition_mod._establishment_threat(world, "France")
        assert int(world.threat_level) == before

    def test_the_panel_names_it(self):
        from backend.game_logic.diplomatic_ledger import _threat_source_label
        label = _threat_source_label(_europe(), "military_establishment")
        assert label and label != "military_establishment"


# ════════════════════════════════════════════════════════════════════════
# (b') Drill restores morale — the Camp of Boulogne
# ════════════════════════════════════════════════════════════════════════

class TestDrillRestoresMorale:
    def _drilled(self, location="Paris", morale=60, building=None):
        marshal = MarshalFactory.infantry(name="Ney", location=location,
                                          strength=30000)
        marshal.morale = morale
        world = WorldFactory.with_marshals([marshal])
        if building:
            world.get_region(location).buildings.append(
                {"type": building, "damaged": False})
        return world, marshal

    def test_a_completed_drill_lifts_a_debased_corps(self):
        world, marshal = self._drilled()
        gain = world._apply_drill_morale(marshal)
        assert gain == world.DRILL_MORALE_GAIN
        assert marshal.morale == 60 + world.DRILL_MORALE_GAIN

    def test_a_training_ground_makes_the_drill_worth_more(self):
        """The building the memo called 'no measurable peacetime effect'
        earns its second reason to exist."""
        world, marshal = self._drilled(building="training_ground")
        assert world._apply_drill_morale(marshal) == world.DRILL_MORALE_GAIN_TRAINED

    def test_it_never_exceeds_the_existing_cap(self):
        world, marshal = self._drilled(morale=100)
        assert world._apply_drill_morale(marshal) == 0
        assert marshal.morale == 100

    def test_the_gain_is_reported_where_it_is_applied(self):
        """Shown = applied — and silent when there was nothing to restore."""
        from backend.models.world_state import _drill_morale_note
        world, marshal = self._drilled()
        assert "morale +10" in _drill_morale_note(marshal, 10)
        assert _drill_morale_note(marshal, 0) == ""

    def test_it_reaches_combat_through_the_existing_chokepoint(self):
        """No new modifier: morale feeds `get_combat_effectiveness`, which is
        why this needed no new serialized field and no new bar on the card."""
        world, marshal = self._drilled(morale=60)
        before = marshal.get_combat_effectiveness()
        world._apply_drill_morale(marshal)
        assert marshal.get_combat_effectiveness() > before

    def test_the_one_way_axis_is_closed(self):
        """The whole point. A levy debases a corps (shipped); before this
        there was no way back, measured — nothing moved morale in peacetime."""
        world, marshal = self._drilled(morale=100)
        # The shipped half: five levies at RECRUIT_MORALE 40 dilute him.
        marshal.morale = int((25000 * 100 + 50000 * 40) / 75000)
        assert marshal.morale == 60
        debased = marshal.get_combat_effectiveness()
        for _ in range(4):
            world._apply_drill_morale(marshal)
        assert marshal.morale == 100
        assert marshal.get_combat_effectiveness() > debased

    def test_both_drill_completion_arms_pay_the_same(self):
        """Single source: the payoff must not depend on whether Soult's
        one-turn Drillmaster arm or the standard two-turn arm produced it."""
        import inspect
        src = inspect.getsource(WorldState._process_tactical_states)
        assert src.count("_apply_drill_morale") == 2


# ════════════════════════════════════════════════════════════════════════
# (c) The supply-strain headline
# ════════════════════════════════════════════════════════════════════════

class TestSupplyStrainHeadline:
    def _starving(self, region_type=None, turns=(9, 10)):
        world = _europe()
        corps = _french(world)[:3]
        loc = corps[0].location
        for m in corps:
            m.location = loc
        if region_type:
            world.get_region(loc).region_type = region_type
        for t in turns:
            world.current_turn = t
            for m in corps:
                world.log_event({"type": "supply_attrition", "marshal": m.name,
                                 "nation": "France", "region": loc,
                                 "losses": 1400})
        world.current_turn = max(turns)
        return world, loc

    def test_a_starving_stack_can_finally_lead_the_dispatch(self):
        world, loc = self._starving()
        head = _build_headline(world, "France") or {}
        assert head.get("class") == "supply_strain"
        assert loc in head["text"]
        assert "8,400 men" in head["text"]

    def test_one_bad_turn_is_not_a_crisis(self):
        world, _loc = self._starving(turns=(10,))
        head = _build_headline(world, "France") or {}
        assert head.get("class") != "supply_strain"

    def test_it_never_advises_a_depot_where_one_is_illegal(self):
        """⊕ `supply_depot` is illegal in 16 of France's 28 provinces, so the
        obvious advice is often the advice the executor would refuse."""
        assert "town" not in BUILDING_TYPES["supply_depot"]["allowed_in"]
        world, loc = self._starving(region_type="town")
        text = (_build_headline(world, "France") or {})["text"]
        # CA9 review round: the remedy no longer WRAPS a refusal that
        # already names the region — that produced "No depot may be laid
        # at Tyrol — cannot build in Tyrol — not controlled by France."
        # For the region-TYPE arm the executor's sentence does not name
        # the province, so the prefix (and the word "depot") still rides.
        assert "depot" in text.lower()
        assert "No depot may be laid" in text
        # CA9-F10: the reason is no longer this surface's own paraphrase —
        # it is the string `_execute_build` would have answered with, so
        # the briefing and the order cannot say different things.
        from backend.models.region import can_build
        _ok, _refusal, _remedy = can_build(
            world, world.get_region(loc), "supply_depot", "France")
        assert _ok is False
        # CA9 review round: the headline strips the executor's own
        # redundant "Cannot build in <region> — " lead-in (it was
        # stuttering against the prefix) and quotes the REASON verbatim.
        _reason = _refusal.rstrip(".")
        _lead = f"Cannot build in {loc} — "
        if _reason.startswith(_lead):
            _reason = _reason[len(_lead):]
        assert _reason in text, (
            f"the headline paraphrased the gate instead of quoting it: "
            f"{text!r} vs {_reason!r}")
        assert "Move a corps" in text

    def test_it_names_the_depot_where_one_is_legal(self):
        world, loc = self._starving(region_type="city")
        text = (_build_headline(world, "France") or {})["text"]
        assert f"A supply depot at {loc}" in text

    def test_it_outranks_the_household_nag_that_used_to_bury_it(self):
        """Between a lost province and a war declaration: slower than the
        first, faster than the second — and far above the 180g nag that led
        half the played campaign's dispatches while this killed the army."""
        w = dispatch_mod.HEADLINE_WEIGHTS
        assert w["supply_strain"] > w["estate_eroding"]
        assert w["supply_strain"] > w["war_touches_us"]
        assert w["supply_strain"] < w["region_lost"]

    def test_it_is_standing_so_it_cannot_become_the_next_stuck_record(self):
        """PC-7 again: a stack over capacity re-manufactures its candidate
        every turn, so without the cooldown the famine merely replaces the
        household nag as the sentence that repeats."""
        assert "supply_strain" in dispatch_mod.STANDING_HEADLINE_CLASSES
        assert "supply_strain" in dispatch_mod._STANDING_ESCALATION

    def test_an_enemy_stack_starving_is_not_our_headline(self):
        world, loc = self._starving()
        for e in world.event_log:
            if e.get("type") == "supply_attrition":
                e["nation"] = "Austria"
        head = _build_headline(world, "France") or {}
        assert head.get("class") != "supply_strain"
