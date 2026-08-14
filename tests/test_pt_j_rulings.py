"""Row PT, slices J1–J4 — the four §4 rulings, built.

Gate record: `docs/PLAYTEST_FIXES_SPEC.md` §4 (RULED August 12, 2026);
build contracts §4.1. Four slices:

* **PT-J1 "The Truce Holds"** — coalition ejection (+ the −15 betrayal)
  moved to the set_diplomatic_state chokepoint, firing on formal PEACE
  (or VASSAL subjugation) from WAR **or ARMISTICE** — never on a truce.
  The truce keeps membership, the collapse resumes the coalition war,
  and the previously-masked ARMISTICE→PEACE road now ejects.
* **PT-J2 "The Campaign Ledger"** — the war gains MEMORY: a serialized
  per-pair record of unique captures + casualties per side, feeding two
  bounded score components (campaign, blood) while the raw battle caps
  come DOWN (CA9 row 1's farm guard).
* **PT-J3 "The Pensions of the Fallen"** — the EB-1 rate prices the
  campaign's own dead from the same ledger.
* **PT-J4 "The Bench Speaks"** — three advisory surfaces for marshal
  commissioning, every one reading the executor's OWN gate.

§3 acceptance rule 2 governs: a pin that can pass while the delivered
value is wrong is not a pin — assertions here read delivered state
(members lists, relation deltas, rate terms, rendered notes), not
producer internals.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic.coalition import check_dissolution
from backend.game_logic.diplomacy import (
    BATTLE_SCORE_CAP,
    BLOOD_DIFF_CAP,
    BLOOD_DIFF_DIVISOR,
    CAMPAIGN_CAPTURE_CAP,
    CAMPAIGN_CAPTURE_SCORE,
    DECISIVE_SCORE_CAP,
    calculate_side_war_score,
    calculate_war_score,
    record_battle,
    set_diplomatic_state,
)
from backend.game_logic.diplomatic_advisory import generate_advisory
from backend.game_logic.dispatch import _pick_berthier_note
from backend.game_logic.recruitment import (
    commission_counsel_need,
    first_affordable_commission,
)
from backend.models.world_state import (
    CHARGES_PENSIONS_CAP,
    CHARGES_PENSIONS_DIVISOR,
    WorldState,
)
from backend.notifications import COMMISSION_AVAILABLE

from tests.conftest import WorldFactory

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def europe():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _coalition_world():
    """Legacy world with a three-member anti-France coalition at war."""
    world = WorldFactory.basic()
    for member in ("Austria", "Prussia", "Russia"):
        key = world._make_diplo_key("France", member)
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = 1
    world.active_coalition = {
        "id": "coalition_test", "name": "Third Coalition",
        "target_nation": "France", "leader": "Austria",
        "members": ["Austria", "Prussia", "Russia"],
        "formed_turn": 1, "strategic_posture": "defensive",
        "posture_last_updated": 1,
    }
    world.threat_by_target["France"] = 60  # above dissolution threshold
    return world


def _relation(world, a, b):
    return int(world.nation_relations.get(world._make_diplo_key(a, b), 0))


# ═══════════════════════════════════════════════════════════════════════
# PT-J1 — The Truce Holds
# ═══════════════════════════════════════════════════════════════════════


class TestTruceKeepsMembership:
    def test_armistice_does_not_eject_and_brands_no_traitor(self):
        world = _coalition_world()
        before = _relation(world, "Austria", "Prussia")
        set_diplomatic_state(world, "France", "Austria", "ARMISTICE")
        assert "Austria" in world.active_coalition["members"]
        assert _relation(world, "Austria", "Prussia") == before

    def test_collapse_resumes_the_coalition_war_intact(self):
        world = _coalition_world()
        set_diplomatic_state(world, "France", "Austria", "ARMISTICE")
        set_diplomatic_state(world, "France", "Austria", "WAR")
        assert world.active_coalition is not None
        assert set(world.active_coalition["members"]) == {
            "Austria", "Prussia", "Russia"}

    def test_truce_does_not_dissolve_via_insufficient_members(self):
        """The seam the naive fix would have missed: check_dissolution
        counted only WAR pairs, so membership surviving the truce would
        have been erased by insufficient_members anyway. An ARMISTICE
        pair is a STANDING member (Pläswitz: the whole war truced, the
        coalition held)."""
        world = _coalition_world()
        world.active_coalition["members"] = ["Austria", "Prussia"]
        set_diplomatic_state(world, "France", "Austria", "ARMISTICE")
        set_diplomatic_state(world, "France", "Prussia", "ARMISTICE")
        assert check_dissolution(world) is None

    def test_formal_peace_ejects_with_betrayal(self):
        world = _coalition_world()
        before_pr = _relation(world, "Austria", "Prussia")
        before_ru = _relation(world, "Austria", "Russia")
        set_diplomatic_state(world, "France", "Austria", "PEACE")
        assert "Austria" not in world.active_coalition["members"]
        assert _relation(world, "Austria", "Prussia") == before_pr - 15
        assert _relation(world, "Austria", "Russia") == before_ru - 15

    def test_armistice_then_peace_ejects_exactly_once(self):
        """The masked hole: ARMISTICE→PEACE never ejected (the old seam
        required current_state == "WAR"), invisible only because the
        truce itself used to eject. Now the truce keeps membership and
        the thaw's formal peace does the ejecting — once."""
        world = _coalition_world()
        before = _relation(world, "Austria", "Prussia")
        set_diplomatic_state(world, "France", "Austria", "ARMISTICE")
        assert "Austria" in world.active_coalition["members"]
        set_diplomatic_state(world, "France", "Austria", "PEACE")
        coalition = world.active_coalition
        if coalition is not None:  # dissolution may fire on 2 remaining
            assert "Austria" not in coalition["members"]
        assert _relation(world, "Austria", "Prussia") == before - 15

    def test_vassal_subjugation_still_ejects(self):
        world = _coalition_world()
        set_diplomatic_state(world, "France", "Austria", "VASSAL")
        coalition = world.active_coalition
        if coalition is not None:
            assert "Austria" not in coalition["members"]

    def test_member_to_member_peace_never_ejects(self):
        """A pair not containing the coalition's target is none of the
        chokepoint's business."""
        world = _coalition_world()
        key = world._make_diplo_key("Prussia", "Russia")
        world.diplomatic_states[key] = "WAR"
        set_diplomatic_state(world, "Prussia", "Russia", "PEACE")
        assert set(world.active_coalition["members"]) == {
            "Austria", "Prussia", "Russia"}

    def test_no_coalition_no_crash(self):
        world = WorldFactory.with_war("France", "Prussia")
        assert world.active_coalition is None
        set_diplomatic_state(world, "France", "Prussia", "PEACE")
        assert world.active_coalition is None

    def test_elimination_teardown_still_removes(self):
        """The other caller (world_state.py elimination path) is
        untouched — a dead nation leaves the coalition regardless of
        diplomatic state."""
        world = _coalition_world()
        world._eliminate_nation("Austria")
        coalition = world.active_coalition
        if coalition is not None:
            assert "Austria" not in coalition["members"]


# ═══════════════════════════════════════════════════════════════════════
# PT-J2 — The Campaign Ledger
# ═══════════════════════════════════════════════════════════════════════


def _prussian_region(world):
    return next(r for r in world.regions.values()
                if r.controller == "Prussia")


class TestCampaignCaptures:
    def test_wartime_capture_is_remembered(self):
        world = WorldFactory.with_war("France", "Prussia")
        region = _prussian_region(world)
        world.capture_region(region.name, "France")
        key = world._make_diplo_key("France", "Prussia")
        assert world.campaign_ledgers[key]["captures"]["France"] == [
            region.name]

    def test_capture_is_unique_per_province_per_war(self):
        world = WorldFactory.with_war("France", "Prussia")
        region = _prussian_region(world)
        world.record_campaign_capture("Prussia", "France", region.name)
        world.record_campaign_capture("Prussia", "France", region.name)
        key = world._make_diplo_key("France", "Prussia")
        assert world.campaign_ledgers[key]["captures"]["France"] == [
            region.name]

    def test_retaking_credits_each_side_once_and_washes(self):
        """The playtest shape: lose provinces, retake them. Each side is
        credited once; the CAPTURE component nets zero — the
        differentiating memory is blood, by design."""
        world = WorldFactory.with_war("France", "Prussia")
        region = _prussian_region(world)
        world.capture_region(region.name, "France")
        world.capture_region(region.name, "Prussia")
        components = calculate_war_score(
            "France", "Prussia", world, return_components=True)
        assert components["campaign"] == 0
        key = world._make_diplo_key("France", "Prussia")
        assert world.campaign_ledgers[key]["captures"]["France"] == [
            region.name]
        assert world.campaign_ledgers[key]["captures"]["Prussia"] == [
            region.name]

    def test_peacetime_capture_records_nothing(self):
        world = WorldFactory.basic()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"  # legacy boot is at war
        region = _prussian_region(world)
        world.capture_region(region.name, "France")
        assert world.campaign_ledgers == {}

    def test_campaign_component_scores_and_caps(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {"France": [f"R{i}" for i in range(9)]},
            "casualties": {},
        }
        components = calculate_war_score(
            "France", "Prussia", world, return_components=True)
        assert components["campaign"] == min(
            CAMPAIGN_CAPTURE_CAP, 9 * CAMPAIGN_CAPTURE_SCORE)


class TestCampaignBlood:
    def test_record_battle_accrues_both_sides_below_the_1000_floor(self):
        """The ledger remembers every skirmish's dead even though only
        real battles earn a battle_records row."""
        world = WorldFactory.with_war("France", "Prussia")
        record_battle(world, "France", "Prussia", "France", 400, 500)
        key = world._make_diplo_key("France", "Prussia")
        assert world.campaign_ledgers[key]["casualties"] == {
            "France": 400, "Prussia": 500}
        assert world.battle_records.get(key, []) == []

    def test_blood_differential_scores_scales_and_caps(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {},
            "casualties": {"France": 10000, "Prussia": 30000},
        }
        components = calculate_war_score(
            "France", "Prussia", world, return_components=True)
        assert components["blood"] == min(
            BLOOD_DIFF_CAP, 20000 // BLOOD_DIFF_DIVISOR)
        # And the mirror read is symmetric.
        mirror = calculate_war_score(
            "Prussia", "France", world, return_components=True)
        assert mirror["blood"] == -components["blood"]

    def test_blood_truncates_toward_zero(self):
        """Floor division would score −1 for a single man's deficit."""
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {},
            "casualties": {"France": 1, "Prussia": 0},
        }
        components = calculate_war_score(
            "France", "Prussia", world, return_components=True)
        assert components["blood"] == 0


class TestDrawnBattleAccrues:
    def test_a_drawn_battle_still_bleeds_into_the_ledger(self):
        """Review round [P2-3]: every battle-record producer gated the
        record_battle call on a WINNER, so mutual destruction and
        stalemate — the bloodiest outcomes, and the blood component's
        own founding case (the DR-1 out-bled stalemate) — accrued
        nothing. The draw arms feed the ledger directly while
        battle_records stays winner-only."""
        from tests.conftest import MarshalFactory
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000, nation="France")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=30000,
                                    personality="cautious")
        world = WorldFactory.with_marshals([ney, mack])
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        result = CommandExecutor().execute(
            {"success": True,
             "command": {"marshal": "Ney", "action": "attack",
                         "target": "Mack"}},
            {"world": world})
        assert result.get("success"), result.get("message")
        event = next(e for e in world.event_log
                     if e.get("type") == "battle")
        # The general contract: the ledger holds each side's dead from
        # the battle regardless of outcome…
        cas = world.campaign_ledgers[key]["casualties"]
        assert cas.get("France", 0) == int(event["attacker_casualties"])
        assert cas.get("Austria", 0) == int(event["defender_casualties"])
        assert cas.get("France", 0) > 0 and cas.get("Austria", 0) > 0
        # …and when the field produced no victor, the winner-only
        # battle_records row correctly does not exist while the ledger
        # does (the pre-fix code dropped BOTH).
        if "victory" not in str(event.get("outcome", "")):
            assert world.battle_records.get(key, []) == []


class TestBattleReweight:
    def test_battle_component_caps_at_the_new_cap(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.battle_records[key] = [
            {"turn": int(world.current_turn), "winner": "France",
             "attacker": "France", "defender": "Prussia",
             "attacker_casualties": 1000, "defender_casualties": 1000,
             "location": "X", "battle_name": ""}
            for _ in range(8)
        ]
        components = calculate_war_score(
            "France", "Prussia", world, return_components=True)
        assert components["battles"] == BATTLE_SCORE_CAP
        assert BATTLE_SCORE_CAP == 15  # the blessed re-weight

    def test_decisive_component_caps_at_the_new_cap(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.decisive_battles[key] = [
            {"turn": 1, "winner": "France", "total_casualties": 20000,
             "ratio": 3.0},
            {"turn": 2, "winner": "France", "total_casualties": 20000,
             "ratio": 3.0},
        ]
        components = calculate_war_score(
            "France", "Prussia", world, return_components=True)
        assert components["decisive"] == DECISIVE_SCORE_CAP
        assert DECISIVE_SCORE_CAP == 15  # the blessed re-weight

    def test_side_score_aggregates_the_memory_components(self):
        world = WorldFactory.with_war("France", "Prussia")
        key_p = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[
            world._make_diplo_key("France", "Austria")] = "WAR"
        key_a = world._make_diplo_key("France", "Austria")
        world.campaign_ledgers[key_p] = {
            "captures": {"France": ["R1"]},
            "casualties": {"France": 0, "Prussia": 5000},
        }
        world.campaign_ledgers[key_a] = {
            "captures": {"France": ["R2"]},
            "casualties": {"France": 0, "Austria": 5000},
        }
        side = calculate_side_war_score(
            "France", ["Prussia", "Austria"], world,
            return_components=True)
        assert side["campaign"] == 2 * CAMPAIGN_CAPTURE_SCORE
        assert side["blood"] == 2 * (5000 // BLOOD_DIFF_DIVISOR)


class TestTheWhitePeaceFix:
    def test_a_fought_war_at_status_quo_scores_above_zero(self):
        """The measured defect: 18 turns of war, four provinces lost and
        retaken, every settlement sample "White Peace". With the ledger,
        the same status-quo board carries the war's memory: captures
        wash, blood and battles do not."""
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            # Four provinces taken by Prussia, all four retaken by France:
            # the capture memory washes.
            "captures": {"France": ["A", "B", "C", "D"],
                         "Prussia": ["A", "B", "C", "D"]},
            # France out-bled the invader expelling him.
            "casualties": {"France": 15000, "Prussia": 40000},
        }
        world.battle_records[key] = [
            {"turn": int(world.current_turn), "winner": "France",
             "attacker": "Prussia", "defender": "France",
             "attacker_casualties": 5000, "defender_casualties": 2000,
             "location": "X", "battle_name": ""}
            for _ in range(4)
        ]
        components = calculate_war_score(
            "France", "Prussia", world, return_components=True)
        assert components["campaign"] == 0        # the board nets zero…
        assert components["total"] > 0            # …the war does not.


class TestLedgerLifecycle:
    """The ledger's ONE demobilize seam is the set_diplomatic_state
    chokepoint (review round [P1-2/P3-4]: two formal-end roads never
    reach cleanup_war_end, so the rule cannot live there) — every test
    here drives the delivered transition, not a helper."""

    def test_formal_peace_clears_the_pair_ledger(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {"France": 5000}}
        set_diplomatic_state(world, "France", "Prussia", "PEACE")
        assert key not in world.campaign_ledgers

    def test_armistice_keeps_the_ledger_and_collapse_keeps_it_too(self):
        """A truce pauses the war (same war_id on collapse) — it must not
        amnesty four provinces of blood. Deliberate divergence from
        battle_records, which armistice wipes (pre-existing)."""
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {"France": 5000}}
        set_diplomatic_state(world, "France", "Prussia", "ARMISTICE")
        assert key in world.campaign_ledgers
        set_diplomatic_state(world, "France", "Prussia", "WAR")
        assert key in world.campaign_ledgers

    def test_typed_conquest_vassalization_demobilizes(self):
        """[P1-2] the typed `make X a vassal` conquest road never runs
        cleanup_war_end — the settlement road does — so before the
        chokepoint arm the ledger survived vassalization forever: both
        sides paid pensions for a concluded war, and a later REBELLION
        war opened preloaded with the dead war's captures and blood."""
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {"France": ["R1"]},
            "casualties": {"France": 5000, "Prussia": 9000}}
        set_diplomatic_state(
            world, "France", "Prussia", "VASSAL", "conquest_vassalization")
        assert key not in world.campaign_ledgers

    def test_ledger_round_trips_through_serialization(self):
        world = WorldFactory.with_war("France", "Prussia")
        key = world._make_diplo_key("France", "Prussia")
        world.campaign_ledgers[key] = {
            "captures": {"France": ["R1", "R2"]},
            "casualties": {"France": 400, "Prussia": 500},
        }
        restored = WorldState.from_dict(world.to_dict())
        assert restored.campaign_ledgers == world.campaign_ledgers

    def test_pre_ledger_save_defaults_empty(self):
        world = WorldFactory.basic()
        data = world.to_dict()
        data.pop("campaign_ledgers", None)
        restored = WorldState.from_dict(data)
        assert restored.campaign_ledgers == {}


class TestShownEqualsApplied:
    def test_war_status_breakdown_carries_the_memory_components(self, europe):
        from backend.game_logic.war_status import build_active_wars
        key = world_key = None
        for k, state in europe.diplomatic_states.items():
            if state == "WAR" and "France" in k.split("|"):
                world_key = k
                break
        assert world_key is not None
        europe.campaign_ledgers[world_key] = {
            "captures": {"France": ["Swabia"]},
            "casualties": {"France": 1000,
                           [n for n in world_key.split("|")
                            if n != "France"][0]: 6000},
        }
        del key
        wars = build_active_wars(europe)["wars"]
        row = next(w for w in wars
                   if w.get("breakdown") and w.get("status") == "war"
                   and (w.get("breakdown") or {}).get("campaign"))
        assert "blood" in row["breakdown"]


# ═══════════════════════════════════════════════════════════════════════
# PT-J3 — The Pensions of the Fallen
# ═══════════════════════════════════════════════════════════════════════


class TestPensionsOfTheFallen:
    def test_boot_is_pension_free(self, europe):
        keys = {t["key"] for t in
                europe.get_state_charges_rate("France")["terms"]}
        assert "pensions_of_the_fallen" not in keys

    def test_the_dead_price_the_rate(self, europe):
        europe.campaign_ledgers["Austria|France"] = {
            "captures": {}, "casualties": {"France": 76500}}
        terms = europe.get_state_charges_rate("France")["terms"]
        pension = next(t for t in terms
                       if t["key"] == "pensions_of_the_fallen")
        assert pension["amount"] == 76500 // CHARGES_PENSIONS_DIVISOR
        assert pension["label"] == "the pensions of the fallen"

    def test_scale_distinguishes_bloodlettings(self, europe):
        """The reason the flat-term retune was rejected: 10k and 76k dead
        must price DIFFERENTLY."""
        europe.campaign_ledgers["Austria|France"] = {
            "captures": {}, "casualties": {"France": 10000}}
        small = europe.get_state_charges_rate("France")["rate"]
        europe.campaign_ledgers["Austria|France"]["casualties"][
            "France"] = 76500
        large = europe.get_state_charges_rate("France")["rate"]
        assert large > small

    def test_cap(self, europe):
        europe.campaign_ledgers["Austria|France"] = {
            "captures": {}, "casualties": {"France": 500000}}
        pension = next(
            t for t in europe.get_state_charges_rate("France")["terms"]
            if t["key"] == "pensions_of_the_fallen")
        assert pension["amount"] == CHARGES_PENSIONS_CAP

    def test_below_the_divisor_no_term(self, europe):
        europe.campaign_ledgers["Austria|France"] = {
            "captures": {},
            "casualties": {"France": CHARGES_PENSIONS_DIVISOR - 1}}
        keys = {t["key"] for t in
                europe.get_state_charges_rate("France")["terms"]}
        assert "pensions_of_the_fallen" not in keys

    def test_gr5_every_nation_pays_its_own_dead(self, europe):
        europe.campaign_ledgers["Austria|France"] = {
            "captures": {},
            "casualties": {"France": 76500, "Austria": 40000}}
        austria = next(
            t for t in europe.get_state_charges_rate("Austria")["terms"]
            if t["key"] == "pensions_of_the_fallen")
        assert austria["amount"] == 40000 // CHARGES_PENSIONS_DIVISOR

    def test_dead_sum_across_live_wars(self, europe):
        europe.campaign_ledgers["Austria|France"] = {
            "captures": {}, "casualties": {"France": 3000}}
        europe.campaign_ledgers["Britain|France"] = {
            "captures": {}, "casualties": {"France": 4500}}
        assert europe.get_campaign_dead("France") == 7500

    def test_elimination_demobilizes_the_pair_ledger(self):
        """Elimination ends wars WITHOUT cleanup_war_end (the EC-W2
        mirror), so the teardown clears the dead nation's pair ledgers
        itself — a leaked ledger would bill pensions forever for a war
        that no longer exists."""
        world = _coalition_world()
        key = world._make_diplo_key("France", "Austria")
        world.campaign_ledgers[key] = {
            "captures": {}, "casualties": {"France": 9000}}
        world._eliminate_nation("Austria")
        assert key not in world.campaign_ledgers
        assert world.get_campaign_dead("France") == 0


# ═══════════════════════════════════════════════════════════════════════
# PT-J4 — The Bench Speaks
# ═══════════════════════════════════════════════════════════════════════


class TestAvailabilityPredicate:
    def test_poor_chest_means_no_candidate(self, europe):
        europe.nation_gold["France"] = 0
        assert first_affordable_commission(europe, "France") is None

    def test_rich_chest_returns_the_cheapest_gate_clear_candidate(
            self, europe):
        europe.nation_gold["France"] = 50000
        bench = first_affordable_commission(europe, "France")
        assert bench is not None
        costs = [int(c.get("cost", 0))
                 for c in europe.marshal_pool.get("France", [])]
        assert int(bench["cost"]) == min(costs)

    def test_need_is_thin_roster_or_understrength(self, europe):
        # Boot France: 7 standing marshals at 189k over a 130k limit —
        # neither arm fires.
        assert commission_counsel_need(europe, "France") is False
        # Thin the roster below 3 standing.
        french = [m for m in europe.marshals.values()
                  if m.nation == "France"]
        for m in french[2:]:
            m.strength = 0
        assert commission_counsel_need(europe, "France") is True


class TestCounselRung:
    def _quiet_crises(self, europe):
        """Strip the higher rungs so 3.5 is reachable (the W6-9 idiom)."""
        for key, state in list(europe.diplomatic_states.items()):
            if state == "WAR":
                europe.diplomatic_states[key] = "PEACE"
        europe.war_exhaustion.clear()
        europe.threat_level = 0
        europe.agendas = {}
        europe._agenda_cache = None

    def test_the_bench_rung_fires_when_needed_and_affordable(self, europe):
        self._quiet_crises(europe)
        europe.nation_gold["France"] = 50000
        french = [m for m in europe.marshals.values()
                  if m.nation == "France"]
        for m in french[2:]:
            m.strength = 0
        dialogue = generate_advisory(None, "assess_situation", europe)
        rec = dialogue["context"]["recommendation"]
        assert rec is not None and rec["kind"] == "commission_marshal"
        assert rec["target"]
        assert f"{int(first_affordable_commission(europe, 'France')['cost']):,}g" \
            in rec["text"]

    def test_the_rung_stays_silent_without_need(self, europe):
        self._quiet_crises(europe)
        europe.nation_gold["France"] = 50000
        dialogue = generate_advisory(None, "assess_situation", europe)
        rec = dialogue["context"]["recommendation"]
        assert rec is None or rec["kind"] != "commission_marshal"

    def test_a_revolting_vassal_outranks_the_bench(self, europe):
        self._quiet_crises(europe)
        europe.nation_gold["France"] = 50000
        europe.diplomatic_points = 3
        french = [m for m in europe.marshals.values()
                  if m.nation == "France"]
        for m in french[2:]:
            m.strength = 0
        europe.vassals["Switzerland"] = {
            "lord": "France", "loyalty": 30, "autonomy": 1,
            "path": "conquest", "created_turn": 1, "tribute_rate": 0.5,
            "regions": [],
        }
        dialogue = generate_advisory(None, "assess_situation", europe)
        rec = dialogue["context"]["recommendation"]
        assert rec["kind"] == "invest_vassal"


class TestExecutableArm:
    def _bench_dialogue(self, europe):
        self_quiet = TestCounselRung()
        self_quiet._quiet_crises(europe)
        europe.nation_gold["France"] = 50000
        french = [m for m in europe.marshals.values()
                  if m.nation == "France"]
        for m in french[2:]:
            m.strength = 0
        return generate_advisory(None, "assess_situation", europe)

    def test_commission_executes_through_the_real_executor(self, europe):
        dialogue = self._bench_dialogue(europe)
        assert dialogue["options"][0]["action"] == "execute_suggestion"
        target = dialogue["context"]["recommendation"]["target"]
        europe.dialogue_manager.replace(dialogue)
        ap_before = int(europe.admin_actions_remaining)
        assert ap_before >= 1
        result = CommandExecutor().handle_diplomatic_dialogue_response(
            1, {"world": europe})
        assert result["success"] is True, result.get("message")
        assert target in europe.marshals
        assert "new_state" not in result

    def test_the_arm_charges_the_admin_ap_the_typed_route_charges(
            self, europe):
        """Found in passing: the W6-9 arm called the sub-executors
        directly and skipped the 1 admin AP the typed route charges at
        executor pre-flight — the war room's button rode CHEAPER than
        the same order typed. Both admin kinds now mirror the
        pre-flight."""
        dialogue = self._bench_dialogue(europe)
        europe.dialogue_manager.replace(dialogue)
        ap_before = int(europe.admin_actions_remaining)
        result = CommandExecutor().handle_diplomatic_dialogue_response(
            1, {"world": europe})
        assert result["success"] is True
        assert int(europe.admin_actions_remaining) == ap_before - 1

    def test_the_arm_refuses_honestly_at_zero_admin_ap(self, europe):
        dialogue = self._bench_dialogue(europe)
        europe.dialogue_manager.replace(dialogue)
        europe.admin_actions_remaining = 0
        result = CommandExecutor().handle_diplomatic_dialogue_response(
            1, {"world": europe})
        assert result["success"] is False
        assert "administrative" in result["message"].lower()

    def test_invest_arm_stays_free_like_the_typed_route(self, europe):
        """Review-round correction [P2-1]: `invest_vassal` is NOT an
        ADMIN_ACTION — it sits in `free_actions` (R72: vassal commands
        cost DP/gold, never AP), so the typed route charges NO admin AP
        and the war-room button must not either. The first cut of this
        test pinned the opposite without ever comparing to the typed
        route — the exact inert-pin shape §3 rule 2 forbids. Parity is
        the pin now: the button's price equals the typed price."""
        self_quiet = TestCounselRung()
        self_quiet._quiet_crises(europe)
        europe.diplomatic_points = 3
        europe.nation_gold["France"] = 1000
        europe.vassals["Switzerland"] = {
            "lord": "France", "loyalty": 30, "autonomy": 1,
            "path": "conquest", "created_turn": 1, "tribute_rate": 0.5,
            "regions": [],
        }
        dialogue = generate_advisory(None, "assess_situation", europe)
        assert dialogue["context"]["recommendation"]["kind"] == \
            "invest_vassal"
        europe.dialogue_manager.replace(dialogue)
        ap_before = int(europe.admin_actions_remaining)
        dp_before = int(europe.diplomatic_points)
        result = CommandExecutor().handle_diplomatic_dialogue_response(
            1, {"world": europe})
        assert result["success"] is True, result.get("message")
        assert int(europe.admin_actions_remaining) == ap_before  # free (R72)
        assert int(europe.diplomatic_points) == dp_before - 1  # DP-priced

    def test_invest_arm_works_at_zero_admin_ap(self, europe):
        """The inverted mirror's failure scenario, pinned in the
        direction the review proved: with the chancellery's day spent,
        the war-room invest button must still work exactly as the typed
        free-action order would."""
        self_quiet = TestCounselRung()
        self_quiet._quiet_crises(europe)
        europe.diplomatic_points = 3
        europe.nation_gold["France"] = 1000
        europe.vassals["Switzerland"] = {
            "lord": "France", "loyalty": 30, "autonomy": 1,
            "path": "conquest", "created_turn": 1, "tribute_rate": 0.5,
            "regions": [],
        }
        dialogue = generate_advisory(None, "assess_situation", europe)
        europe.dialogue_manager.replace(dialogue)
        europe.admin_actions_remaining = 0
        result = CommandExecutor().handle_diplomatic_dialogue_response(
            1, {"world": europe})
        assert result["success"] is True, result.get("message")

    def test_commission_arm_mirrors_should_end_turn(self, europe):
        """[P3-1] executor.py's admin deduct auto-ends the turn when
        BOTH pools exhaust; the button mirrors the whole shape, not just
        the price."""
        dialogue = self._bench_dialogue(europe)
        europe.dialogue_manager.replace(dialogue)
        europe.actions_remaining = 0
        europe.admin_actions_remaining = 1
        result = CommandExecutor().handle_diplomatic_dialogue_response(
            1, {"world": europe})
        assert result["success"] is True, result.get("message")
        assert result.get("should_end_turn") is True


class TestCaptureBeatNote:
    def test_the_note_names_the_bench_when_the_gate_clears(self, europe):
        europe.nation_gold["France"] = 50000
        bench = first_affordable_commission(europe, "France")
        note = _pick_berthier_note(
            europe, "France", [], {}, headline_class="marshal_captured")
        assert bench["name"] in note
        assert f"{int(bench['cost']):,}g" in note
        assert "ransom" in note  # the base note survives in front

    def test_the_note_stays_honest_when_the_gate_refuses(self, europe):
        europe.nation_gold["France"] = 0
        note = _pick_berthier_note(
            europe, "France", [], {}, headline_class="marshal_captured")
        assert "Marshalate" not in note
        assert "ransom" in note


class TestFirstAffordableNotification:
    def _advance(self, europe):
        europe._last_advanced_turn = -1
        europe.advance_turn()

    def _bench_notes(self, europe):
        return [n for n in europe.notifications.get_pending()
                if n.get("type") == COMMISSION_AVAILABLE]

    def test_fires_once_when_first_affordable_then_latches(self, europe):
        europe.nation_gold["France"] = 50000
        self._advance(europe)
        notes = self._bench_notes(europe)
        assert len(notes) == 1
        assert europe.commission_hint_shown is True
        # A second turn adds nothing.
        europe.nation_gold["France"] = 50000
        self._advance(europe)
        assert len(self._bench_notes(europe)) == 1

    def test_does_not_fire_while_unaffordable(self, europe):
        europe.nation_gold["France"] = 0
        self._advance(europe)
        assert self._bench_notes(europe) == []
        assert europe.commission_hint_shown is False

    def test_latch_serializes(self, europe):
        europe.commission_hint_shown = True
        restored = WorldState.from_dict(europe.to_dict())
        assert restored.commission_hint_shown is True
