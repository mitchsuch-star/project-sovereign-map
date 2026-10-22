"""VP-1 "The Emperor's Designs", S14b part 1 — the substrate, UNARMED
(`docs/VP1_DESIGNS_SPEC.md` §9 Part 1; the siblings `docs/BUG_FIXES.md` §VP1).

The store `world.imperial_designs`, the six predicates, the holds and latches,
the terms latch (a fact recorded before any proclamation), the reward seams and
THE DECISIVE PEACE's rule — armed here on a STAGED 1805 scenario carrying the
authored block part 2 ships (`tests/fixtures/vp1_imperial_designs_block.json`).
The shipped boot is unarmed: no row, no payload, no road a player could reach
before the Cabinet's road page exists (diplomacy is never typed).
"""
import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import imperial_designs as ID
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SHIPPED = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
BLOCK = REPO / "tests" / "fixtures" / "vp1_imperial_designs_block.json"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _block():
    return json.loads(BLOCK.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def staged_path(tmp_path_factory):
    scen = json.loads(SHIPPED.read_text(encoding="utf-8"))
    scen["imperial_designs"] = _block()
    path = tmp_path_factory.mktemp("vp1") / "staged_1805.json"
    path.write_text(json.dumps(scen), encoding="utf-8")
    return path


@pytest.fixture
def w(staged_path):
    with _quiet():
        return WorldState.from_scenario(str(staged_path))


def _vassalize(world, court, loyalty=60, lord="France"):
    world.vassals[court] = {"lord": lord, "loyalty": int(loyalty), "autonomy": 1,
                            "path": "treaty", "tribute_rate": 0.5}
    world.diplomatic_states[world._make_diplo_key(lord, court)] = "VASSAL"
    world.invalidate_active_nations_cache()


def _tick(world, n=1):
    for _ in range(n):
        world.current_turn += 1
        ID.tick(world, world.current_turn)


def _peace(world, court, demands, proposer="France"):
    """A real bilateral war-ending peace through `WorldState._ratify_treaty`."""
    world.diplomatic_states[world._make_diplo_key(proposer, court)] = "WAR"
    with _quiet():
        return world._ratify_treaty({"proposer": proposer, "target": court,
                                     "proposal_type": "peace", "type": "peace",
                                     "demands": demands, "offers": []})


# ═══════════════════════════════════════════════════════════════════════════
# The store: armed only where authored
# ═══════════════════════════════════════════════════════════════════════════

class TestTheStore:
    def test_the_shipped_boot_is_unarmed(self):
        with _quiet():
            shipped = WorldState.from_scenario(str(SHIPPED))
        assert shipped.imperial_designs == {}
        assert ID.build_designs_payload(shipped) is None
        assert ID.proclaim_refusal(shipped, ID.ROAD_RHINE) == "The Empire has no road to proclaim."
        assert ID.drift_suspended(shipped, "Holland") is False
        assert ID.order_decay(shipped, "France") == 0

    def test_the_boot_readings(self, w):
        payload = ID.build_designs_payload(w)
        by_id = {d["id"]: d for r in payload["roads"] for d in r["designs"]}
        assert (by_id["rhine.confederation"]["held"], by_id["rhine.confederation"]["required"]) == (0, 3)
        assert (by_id["crowns.iron_crown"]["held"], by_id["crowns.iron_crown"]["required"]) == (2, 3)
        assert (by_id["system.blockade"]["held"], by_id["system.blockade"]["required"]) == (10, 13)
        assert by_id["system.blockade"]["progress"] == "10 of 26 ports shut to Britain — 13 needed"
        assert all(r["gate_met"] and not r["refusal"] for r in payload["roads"])
        assert payload["road"] == ""

    def test_the_store_survives_a_save_and_load(self, w):
        ID.proclaim(w, ID.ROAD_SYSTEM)
        again = WorldState.from_dict(w.to_dict())
        assert ID.proclaimed_road(again) == ID.ROAD_SYSTEM
        assert ID.owner(again) == "France"

    def test_a_pre_vp1_save_is_armed_by_its_scenario_and_never_overwritten(
            self, w, staged_path, monkeypatch):
        from backend import save_manager as SM
        name = str(w.scenario_name)
        w.imperial_designs = {}
        SM._backfill_imperial_designs(w)                 # the shipped file authors no block
        assert w.imperial_designs == {}
        monkeypatch.setattr(SM, "_BACKFILL_SCENARIOS", {name: (str(staged_path),)})
        SM._backfill_imperial_designs(w)
        assert ID.armed(w) and ID.owner(w) == "France"
        ID.proclaim(w, ID.ROAD_CROWNS)
        SM._backfill_imperial_designs(w)
        assert ID.proclaimed_road(w) == ID.ROAD_CROWNS   # a carried store is kept

    def test_the_block_validates(self, staged_path):
        from backend.modding.validator import validate_scenario
        data = json.loads(staged_path.read_text(encoding="utf-8"))
        errors = [e for e in validate_scenario(data).errors if e.path.startswith("imperial_designs")]
        assert errors == []
        bad = json.loads(staged_path.read_text(encoding="utf-8"))
        bad["imperial_designs"]["roads"][0]["designs"].pop()
        bad["imperial_designs"]["roads"][1]["id"] = "naples"
        paths = {e.path for e in validate_scenario(bad).errors}
        assert "imperial_designs.roads[0].designs" in paths
        assert "imperial_designs.roads[1].id" in paths


# ═══════════════════════════════════════════════════════════════════════════
# The branch: one proclamation, irreversible
# ═══════════════════════════════════════════════════════════════════════════

class TestTheBranch:
    def test_a_second_proclamation_is_refused_with_its_reason(self, w):
        assert ID.proclaim(w, ID.ROAD_RHINE)["success"] is True
        refusal = ID.proclaim_refusal(w, ID.ROAD_SYSTEM)
        assert "The Act of Confederation" in refusal and "cannot be undone" in refusal
        assert ID.proclaim(w, ID.ROAD_SYSTEM)["success"] is False

    def test_the_proclamation_bites(self, w):
        rel = lambda a, b: w.nation_relations.get(w._make_diplo_key(a, b), 0)  # noqa: E731
        before = (rel("France", "Austria"), rel("France", "Prussia"))
        alarm = int(w.threat_level)
        ID.proclaim(w, ID.ROAD_RHINE)
        assert rel("France", "Austria") == max(-100, before[0] - 10)
        assert rel("France", "Prussia") == max(-100, before[1] - 10)
        assert int(w.threat_level) > alarm

    def test_a_forsworn_design_never_fulfils(self, w):
        ID.proclaim(w, ID.ROAD_RHINE)
        w.continental_system_members = ["Denmark", "Ottoman"]   # 15 of 26 shut
        _tick(w, 8)
        assert not ID.is_fulfilled(w, "system.blockade")

    def test_no_hold_runs_before_the_proclamation(self, w):
        w.continental_system_members = ["Denmark", "Ottoman"]
        _tick(w, 8)
        assert ID.design_reading(w, ID.design(w, "system.blockade"))["met"] is True
        assert not ID.is_fulfilled(w, "system.blockade")


# ═══════════════════════════════════════════════════════════════════════════
# The six predicates: latch on their boards, lapse when broken
# ═══════════════════════════════════════════════════════════════════════════

class TestThePredicates:
    def test_the_confederation_latches_on_its_fourth_end_turn_and_shields(self, w):
        ID.proclaim(w, ID.ROAD_RHINE)
        for court in ("Bavaria", "Hesse", "Saxony"):
            _vassalize(w, court)
        from backend.game_logic.vassal import autonomy_drift
        assert autonomy_drift(w, "Hesse", 1) == -2       # the shield waits for the latch
        _tick(w, 3)
        assert not ID.is_fulfilled(w, "rhine.confederation")
        _tick(w, 1)
        assert ID.is_fulfilled(w, "rhine.confederation")
        assert autonomy_drift(w, "Hesse", 1) == 0        # the Protector's shield
        assert autonomy_drift(w, "Holland", 1) == -2     # not a member
        w.vassals["Saxony"]["loyalty"] = 30              # one falls below the line
        assert ID.holds(w, "rhine.confederation") is False
        assert autonomy_drift(w, "Hesse", 1) == -2       # lapsed: the shield is off
        payload = ID.build_designs_payload(w)
        row = next(d for r in payload["roads"] for d in r["designs"] if d["id"] == "rhine.confederation")
        assert row["lapsed"] is True

    def test_the_throne_of_naples_pays_its_authority_once(self, w):
        ID.proclaim(w, ID.ROAD_CROWNS)
        _vassalize(w, "Naples")
        before = int(w.authority_tracker.authority)
        _tick(w, 1)
        assert ID.is_fulfilled(w, "crowns.naples")
        assert int(w.authority_tracker.authority) == min(100, before + 15)
        again = WorldState.from_dict(w.to_dict())
        paid = int(again.authority_tracker.authority)
        _tick(again, 3)
        assert int(again.authority_tracker.authority) == paid

    def test_the_blockade_latches_on_its_sixth_end_turn_and_orders_the_continent(self, w):
        from backend.game_logic.coalition import _calculate_threat_decay
        ID.proclaim(w, ID.ROAD_SYSTEM)
        w.continental_system_members = ["Denmark", "Ottoman"]
        _tick(w, 5)
        assert not ID.is_fulfilled(w, "system.blockade")
        base = _calculate_threat_decay(w, "France")
        _tick(w, 1)
        assert ID.is_fulfilled(w, "system.blockade")
        assert ID.order_decay(w, "France") == 2
        assert _calculate_threat_decay(w, "France") == base + 2
        again = WorldState.from_dict(w.to_dict())
        assert ID.order_decay(again, "France") == 2      # the live reward survives a load
        w.continental_system_members = []                # below 13: lapsed
        assert ID.order_decay(w, "France") == 0

    def test_a_partition_before_the_proclamation_seals_after_it(self, w):
        # a Pressburg on turn 7 (two homeland provinces ceded) — recorded as a fact
        w.current_turn = 7
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Tyrol", "Carniola"],
                               "to_nation": "France"}])
        assert (w.imperial_designs["state"]["terms"].get("Austria") or {}).get("manner") == ID.MANNER_PARTITION
        w.current_turn = 8
        ID.proclaim(w, ID.ROAD_RHINE)
        _tick(w, 1)
        assert ID.is_fulfilled(w, "rhine.german_crown")

    def test_a_new_war_breaks_the_terms(self, w):
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Tyrol", "Carniola"],
                               "to_nation": "France"}])
        from backend.game_logic.diplomacy import set_diplomatic_state
        with _quiet():
            set_diplomatic_state(w, "France", "Austria", "WAR", "declaration")
        assert ID.terms_met(w, "France", "Austria") == (False, "")

    def test_the_moderate_peace_needs_her_alliance_inside_the_window(self, w):
        terms = [{"type": "territory_cede", "from": "Austria", "to": "France", "regions": ["Tyrol"]},
                 {"type": "territory_compensate", "from": "Bavaria", "to": "Austria", "region": "Franconia"}]
        assert ID.manner_for_terms(w, "France", "Austria", terms) == ID.MANNER_MODERATE
        ID.note_ratification(w, terms=terms, counterparts=["Austria"], war_ending=True)
        assert ID.terms_met(w, "France", "Austria") == (False, ID.MANNER_MODERATE)
        w.diplomatic_states[w._make_diplo_key("France", "Austria")] = "ALLIANCE"
        _tick(w, 1)
        assert ID.terms_met(w, "France", "Austria") == (True, ID.MANNER_MODERATE)

    def test_the_manner_reads_the_compensation_netting_ruling_j_kept(self, w):
        three = [{"type": "territory_cede", "from": "Austria", "to": "France",
                  "regions": ["Tyrol", "Carniola", "Croatia"]},
                 {"type": "territory_compensate", "from": "Bavaria", "to": "Austria", "region": "Franconia"}]
        # three ceded, one compensated: net two — still the punitive record
        assert ID.manner_for_terms(w, "France", "Austria", three) == ID.MANNER_PARTITION
        capital = [{"type": "territory_cede", "from": "Austria", "to": "France", "regions": ["Vienna"]},
                   {"type": "territory_compensate", "from": "Bavaria", "to": "Austria", "region": "Franconia"}]
        assert ID.manner_for_terms(w, "France", "Austria", capital) == ID.MANNER_PARTITION
        assert ID.manner_for_terms(w, "France", "Austria", [
            {"type": "gold_lump", "from": "Austria", "to": "France", "amount": 500}]) == ""

    def test_subjugation_is_a_manner(self, w):
        _vassalize(w, "Austria")
        assert ID.manner_for_terms(w, "France", "Austria", []) == ID.MANNER_SUBJUGATION

    def test_the_iron_crown_needs_carniola_titled_and_austria_brought_to_terms(self, w):
        ID.proclaim(w, ID.ROAD_CROWNS)
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Carniola", "Tyrol"],
                               "to_nation": "KingdomOfItaly"}])
        reading = ID.design_reading(w, ID.design(w, "crowns.iron_crown"))
        assert reading["held"] == 3 and reading["met"] is True
        _tick(w, 1)
        assert ID.is_fulfilled(w, "crowns.iron_crown")

    def test_britain_signs_after_the_blockade_with_a_great_power_enrolled(self, w):
        ID.proclaim(w, ID.ROAD_SYSTEM)
        w.continental_system_members = ["Denmark", "Ottoman", "Russia"]
        _tick(w, 6)
        assert ID.is_fulfilled(w, "system.blockade")
        ID.note_ratification(w, terms=[], counterparts=["Britain"], war_ending=True)
        signed = w.imperial_designs["state"]["britain_signed"]
        assert signed["qualified"] is True and signed["members"] == ["Russia"]
        _tick(w, 1)
        assert ID.is_fulfilled(w, "system.continent_peace")

    def test_a_lift_clause_spoils_the_signature(self, w):
        ID.proclaim(w, ID.ROAD_SYSTEM)
        w.continental_system_members = ["Denmark", "Ottoman", "Russia"]
        _tick(w, 6)
        ID.note_ratification(w, terms=[{"type": "continental_system_lifted"}],
                             counterparts=["Britain"], war_ending=True)
        assert w.imperial_designs["state"]["britain_signed"]["qualified"] is False

    def test_the_proclaimed_system_stops_drafting_its_own_lifting(self, w):
        from backend.game_logic.diplomatic_templates import continental_system_lift_offered
        w.continental_system_members = ["Russia"]
        before = continental_system_lift_offered(w, "France", "Britain")
        ID.proclaim(w, ID.ROAD_SYSTEM)
        assert before is True
        assert continental_system_lift_offered(w, "France", "Britain") is False


# ═══════════════════════════════════════════════════════════════════════════
# THE DECISIVE PEACE — the rule computed, nothing stamped (part 3 stamps)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDecisivePeaceRule:
    def _both_latched(self, w):
        ID.proclaim(w, ID.ROAD_RHINE)
        for court in ("Bavaria", "Hesse", "Saxony"):
            _vassalize(w, court)
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Tyrol", "Carniola"],
                               "to_nation": "France"}])
        _tick(w, 4)

    def test_ready_when_both_designs_hold_and_the_court_is_at_peace(self, w):
        self._both_latched(w)
        reading = ID.decisive_peace_reading(w)
        assert reading["ready"] is True, reading["conditions"]
        assert (reading["court"], reading["manner"]) == ("Austria", ID.MANNER_PARTITION)
        assert ID.decisive_peace_released() is False
        assert not any(e.get("cause") == "decisive_peace" for e in (w.endings or []))

    def test_not_while_the_sealing_court_holds_french_soil(self, w):
        self._both_latched(w)
        w.regions["Provence"].controller = "Austria"
        assert ID.decisive_peace_reading(w)["conditions"]["homeland_whole"] is False

    def test_not_while_the_construction_lapses(self, w):
        self._both_latched(w)
        w.vassals["Saxony"]["loyalty"] = 30
        assert ID.decisive_peace_reading(w)["ready"] is False


# ═══════════════════════════════════════════════════════════════════════════
# The siblings (BUG_FIXES §VP1): X1, X2, X3 (+ X11), X9 — each with its seam
# ═══════════════════════════════════════════════════════════════════════════

def _punitive(world, victim):
    from backend.game_logic.emergent_designs import PUNITIVE_MEMORY_TYPE
    from backend.game_logic.settlement_reactions import get_settlement_memories
    return get_settlement_memories(world, subject=victim, memory_type=PUNITIVE_MEMORY_TYPE)


class TestVP1X1AHeldCessionIsPunitive:
    def test_a_partition_signed_over_occupied_ground_is_recorded(self, w):
        w.regions["Tyrol"].controller = "France"
        w.regions["Carniola"].controller = "France"
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Tyrol", "Carniola"],
                               "to_nation": "France"}])
        assert _punitive(w, "Austria"), "the punitive record missed the cession"

    def test_seam_down_the_record_was_empty(self, w, monkeypatch):
        from backend.game_logic import emergent_designs as ED
        monkeypatch.setattr(ED, "held_cessions_are_punitive", lambda: False)
        w.regions["Tyrol"].controller = "France"
        w.regions["Carniola"].controller = "France"
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Tyrol", "Carniola"],
                               "to_nation": "France"}])
        assert not _punitive(w, "Austria")


class TestVP1X3TheBeatenLatchReadsTheBloc:
    def test_carniola_to_the_kingdom_of_italy_latches_austria_beaten(self, w):
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Carniola"],
                               "to_nation": "KingdomOfItaly"}])
        signed = (w.congress or {}).get("signed") or {}
        assert (signed.get("Austria") or {}).get("kind") == "beaten", signed
        from backend.game_logic.game_end import totals
        assert totals(w)["provinces_gained_by_treaty"] >= 1      # X11, the twin

    def test_seam_down_the_latch_was_literal(self, w, monkeypatch):
        from backend.game_logic import game_end as GE
        monkeypatch.setattr(GE, "receiver_in_bloc", lambda world, receiver, player: receiver == player)
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Carniola"],
                               "to_nation": "KingdomOfItaly"}])
        assert "Austria" not in ((w.congress or {}).get("signed") or {})

    def test_an_ally_is_not_the_bloc(self, w):
        _peace(w, "Austria", [{"type": "territory_cede", "regions": ["Carniola"],
                               "to_nation": "Bavaria"}])
        assert "Austria" not in ((w.congress or {}).get("signed") or {})


class TestVP1X2TheSignedArmisticeExitIsARatification:
    def test_the_exit_runs_the_ratifiers_note(self, w, monkeypatch):
        from backend.game_logic import game_end as GE
        calls = []
        real = GE.note_ratification
        monkeypatch.setattr(GE, "note_ratification", lambda world, **k: calls.append(k) or real(world, **k))
        GE.note_armistice_exit(w, "France", "Austria", clauses=[
            {"type": "territory_cede", "from": "Austria", "to": "France", "regions": ["Vienna"],
             "held_line": True}], source="armistice_dictated", was_vassal=False)
        assert calls and calls[0]["counterparts"] == ["Austria"] and calls[0]["war_ending"] is True

    def test_an_ai_pair_keeps_count_peace_exactly(self, w, monkeypatch):
        from backend.game_logic import game_end as GE
        before = dict(GE.totals(w))
        called = []
        monkeypatch.setattr(GE, "note_ratification", lambda world, **k: called.append(k))
        GE.note_armistice_exit(w, "Austria", "Bavaria", clauses=[], source="armistice_dictated",
                               was_vassal=False)
        assert called == [] and GE.totals(w) == before

    def test_the_held_line_keeps_its_retained_title(self, w):
        from backend.game_logic import game_end as GE
        w.province_title = {"Vienna": {"kind": "treaty", "since": 1, "from": "Austria",
                                       "holder": "France", "house": "France", "retained": True}}
        w.regions["Vienna"].controller = "France"
        GE.title_signed_cessions(w, [{"type": "territory_cede", "from": "Austria", "to": "France",
                                      "regions": ["Vienna"], "held_line": True}])
        assert w.province_title["Vienna"].get("retained") is True


class TestVP1X9TheIntentNeverReadsThePlayersPlans:
    def test_a_player_deck_reads_indifferent_and_survival_stays(self, w):
        from backend.game_logic import intent as I
        from backend.game_logic import agendas as AG
        w.agendas["France"] = [{"id": "natural_frontiers", "type": "acquire_regions",
                                "title": "Natural Frontiers", "regions": ["Vienna"]}]
        w._agenda_cache = None
        assert AG.get_active_agenda("France", w) is not None
        assert I._derive_intent("France", w).price == "indifferent"


class TestVP1X2OnThePcR2Board:
    """The dictated exit end to end (the PC-R2 board `turn6_vienna_held`):
    the Congress latches Austria as it does for the bilateral peace, the
    peace is counted once, and the held line keeps its retained title."""

    def _dictated(self):
        import copy
        from backend.game_logic import diplomacy as D
        from tests.test_pc_rulings import _board, _kill_hope, _truce
        w = _board("turn6_vienna_held.json")
        k = "Austria|France"
        _truce(w, proposer="Austria", target="France",
               sweeteners=[{"type": "gold_per_turn", "value": 80}])
        w.nation_relations[k] = -80
        w.armistice_turns[k] = D.ARMISTICE_DURATION - 1
        _kill_hope(w)
        assert D.armistice_expiry_exit(w, "France", "Austria")["exit"] == "dictated"
        return w, copy.deepcopy(w)

    def test_the_dictated_peace_latches_the_congress_and_counts_once(self):
        from backend.game_logic import diplomacy as D
        from backend.game_logic.game_end import totals
        w, _ = self._dictated()
        before = int(totals(w)["peaces_signed"])
        with _quiet():
            D._process_armistice_expiration(w)
        signed = (w.congress or {}).get("signed") or {}
        assert (signed.get("Austria") or {}).get("kind") in ("beaten", "capital"), signed
        assert int(totals(w)["peaces_signed"]) == before + 1
        assert (w.province_title.get("Vienna") or {}).get("retained") is True

    def test_seam_down_the_exit_counted_the_peace_alone(self, monkeypatch):
        from backend.game_logic import diplomacy as D
        from backend.game_logic import game_end as GE
        monkeypatch.setattr(GE, "note_armistice_exit",
                            lambda world, a, b, **k: GE.count_peace(world, a, b))
        w, _ = self._dictated()
        with _quiet():
            D._process_armistice_expiration(w)
        assert "Austria" not in ((w.congress or {}).get("signed") or {})


def _shipped():
    with _quiet():
        return WorldState.from_scenario(str(SHIPPED))


def _vassal_draft(world, court):
    from backend.game_logic.diplomatic_templates import generate_suggested_terms
    draft = generate_suggested_terms(court, "vassalage", world, deterministic=True)
    return {"type": "vassalage", "proposer_nation": world.player_nation, "target_nation": court,
            "sweeteners": list(draft.get("sweeteners") or []),
            "demands": list(draft.get("demands") or []),
            "clauses": list(draft.get("clauses") or [])}


class TestVP1X12TheTurnOneCounterReadsTheComingPurse:
    """VP1-X12 (found by part 1's boot reproduction): before the first advance
    no court's purse is written, so the counter's dry run read every court as
    penniless and turn 1's Cabinet withheld "a counter is likely" from five
    rows (Bavaria's vassalage; Denmark's, the Papal States', Portugal's and
    Saxony's open borders) that the advance — regen first, then the
    resolution — answers with a counter. The dry run projects the purse the
    regen writes; a written purse is read as written."""

    def test_bavaria_turn_one_band_promises_the_counter_the_advance_makes(self):
        from backend.game_logic.ai_diplomacy import generate_counter_offer
        from backend.game_logic.diplomacy import (
            calculate_acceptance, counter_aware_likelihood, process_diplomacy_turn,
        )
        world = _shipped()
        proposal = _vassal_draft(world, "Bavaria")
        score = int(calculate_acceptance(proposal, world)["score"])
        assert 30 <= score < 50
        assert "counter is likely" in counter_aware_likelihood(world, proposal, score)
        # the projection branch: a purse not yet written (a world built outside
        # `from_scenario`, which seeds every purse since VP1-X13)
        world.nation_dp = {}
        assert "counter is likely" in counter_aware_likelihood(world, proposal, score)
        assert world.nation_dp == {}  # the dry run writes no purse
        assert generate_counter_offer(dict(proposal), world, dry_run=True) is not None
        world.proposal_in_transit = {"target": "Bavaria", "proposal": proposal,
                                     "turn_sent": world.current_turn, "dp_cost": 1,
                                     "acceptance_snapshot": score,
                                     "diplomatic_state_at_send": ""}
        with _quiet():
            process_diplomacy_turn(world)
            world.current_turn += 1
            events = world._process_proposal_in_transit()
        assert "COUNTER_OFFER" in [e.get("outcome") for e in events]

    def test_a_written_empty_purse_still_refuses_the_counter(self):
        from backend.game_logic.ai_diplomacy import generate_counter_offer
        world = _shipped()
        world.nation_dp = {"Bavaria": 0}
        assert generate_counter_offer(_vassal_draft(world, "Bavaria"), world, dry_run=True) is None

    def test_the_projection_is_the_regen_and_the_seat(self):
        from backend.game_logic.diplomacy import (
            _process_dp_regen, regen_dp_for, sovereign_seat_bonus,
        )
        world = _shipped()
        world.nation_dp = {}
        projected = {n: int(regen_dp_for(world, n)) + int(sovereign_seat_bonus(world, n))
                     for n in world.enemy_nations}
        _process_dp_regen(world)
        assert {n: world.nation_dp.get(n) for n in projected} == projected


class TestVP1X13TheCourtsOpenWithTheirPurses:
    """VP1-X13 (X12's sweep, part 2's head): France opened at her regen (5)
    while every AI court opened with an empty purse until the first advance —
    on turn 1 no court could court a sagging satellite, counter, renege or pay
    a bond's point. `diplomacy.seed_boot_purses` writes each court's regen at
    the scenario boot; a save, or a scenario naming `nation_dp`, keeps its own."""

    def test_every_court_opens_with_its_regen_as_the_emperor_does(self):
        from backend.game_logic.diplomacy import regen_dp_for, sovereign_seat_bonus
        world = _shipped()
        expected = {n: int(regen_dp_for(world, n)) + int(sovereign_seat_bonus(world, n))
                    for n in world.enemy_nations}
        assert world.nation_dp == expected
        assert all(type(v) is int and v >= 1 for v in world.nation_dp.values())
        assert int(world.diplomatic_points) == int(regen_dp_for(world, world.player_nation)) +             int(sovereign_seat_bonus(world, world.player_nation))

    def test_a_save_keeps_its_purses_and_never_reseeds(self):
        world = _shipped()
        world.nation_dp["Austria"] = 1
        again = WorldState.from_dict(world.to_dict())
        assert again.nation_dp["Austria"] == 1
        data = world.to_dict()
        data.pop("nation_dp")
        assert WorldState.from_dict(data).nation_dp == {}

    def test_a_scenario_naming_its_purses_keeps_them(self, tmp_path):
        scen = json.loads(SHIPPED.read_text(encoding="utf-8"))
        scen["nation_dp"] = {"Austria": 1}
        path = tmp_path / "purses.json"
        path.write_text(json.dumps(scen), encoding="utf-8")
        with _quiet():
            world = WorldState.from_scenario(str(path))
        assert world.nation_dp == {"Austria": 1}

    def test_a_turn_one_courtier_can_pay_and_seam_down_could_not(self, monkeypatch):
        from backend.game_logic import diplomacy as D
        from backend.game_logic.vassal import attempt_vassal_courting

        def _board():
            world = _shipped()
            world.vassals["Holland"]["loyalty"] = 30           # a sagging satellite
            world.nation_relations[world._make_diplo_key("Britain", "Holland")] = 20
            return world

        world = _board()
        events = attempt_vassal_courting(world, "Britain")
        assert events and world.vassals["Holland"]["loyalty"] < 30
        monkeypatch.setattr(D, "seed_boot_purses", lambda w: 0)
        down = _board()
        assert down.nation_dp == {}
        assert attempt_vassal_courting(down, "Britain") == []
        assert down.vassals["Holland"]["loyalty"] == 30


# ═══════════════════════════════════════════════════════════════════════════
# S14b part 2's siblings (BUG_FIXES §VP1): X4, X5, X6, X8, X10, X15, X16
# ═══════════════════════════════════════════════════════════════════════════

GODOT = REPO / "godot-client" / "project-sovereign"


def _dominance_to(world, court):
    """Stage the trade-dominance court elsewhere (GR5: the System's target is
    derived, never the literal)."""
    from backend.game_logic import naval
    fleets = naval.get_fleets(world)
    dom = int(fleets["Britain"].get("trade_dominance") or 0)
    fleets["Britain"]["trade_dominance"] = 0
    fleets[court]["trade_dominance"] = dom or 450
    assert naval.trade_dominance_nation(world) == court


class TestVP1X4TheDeskStatesTheSystemInPorts:
    def test_the_boot_answer_counts_ports_and_states_the_rule(self):
        from backend.ai.state_desk import _answer_closure
        from backend.game_logic import naval
        world = _shipped()
        answer = _answer_closure(world)
        assert answer.startswith("10 of 26 of the Continent's ports are shut to Britain")
        assert naval.PORT_CLOSURE_RULE.format(target="Britain") in answer
        assert "The next tier is at 40% — 1 more port." in answer
        assert "of Britain's trade" not in answer and "her own blockade" not in answer

    def test_it_reads_the_derived_court(self):
        from backend.ai.state_desk import _answer_closure
        world = _shipped()
        _dominance_to(world, "Spain")
        assert "shut to Spain" in _answer_closure(world)

    def test_a_world_with_no_mistress_of_the_seas_says_so(self):
        from backend.ai.state_desk import _answer_closure
        assert "no one to shut out" in _answer_closure(WorldState())


class TestVP1X5TheClosureInPortsOfTheContinent:
    def test_the_admiralty_prints_n_of_26(self):
        gd = (GODOT / "scripts" / "strategic_ledger.gd").read_text(encoding="utf-8")
        line = next(ln for ln in gd.splitlines() if "var cs_line =" in ln)
        assert 'cs.get("ports_closed"' in line and 'cs.get("ports_total"' in line

    def test_the_tier_shift_names_the_ports_and_an_old_event_its_percentage(self):
        from backend.campaign_log import format_event_oneliner
        from backend.game_logic.dispatch import _format_dispatch_event_text as _format_diplomatic_event
        new = {"type": "cs_tier_shift", "turn": 9, "target": "Britain", "closure_pct": 42,
               "ports_closed": 11, "ports_total": 26, "tier": 1, "previous_tier": 0}
        assert "11 of 26 of the Continent's ports closed (42%)" in format_event_oneliner(new)
        old = {k: v for k, v in new.items() if k not in ("ports_closed", "ports_total")}
        assert "42% of the Continent's ports closed" in format_event_oneliner(old)
        vars_new = {"target": "Britain", "closure_pct": 42, "ports_closed": 11,
                    "ports_total": 26, "tier": 1, "direction": "tightens"}
        assert "11 of 26 (42%) of the Continent's ports are closed to Britain" in \
            _format_diplomatic_event("cs_tier_shift", vars_new)
        vars_old = {k: v for k, v in vars_new.items() if k not in ("ports_closed", "ports_total")}
        assert "42% of the Continent's ports are closed" in _format_diplomatic_event("cs_tier_shift", vars_old)


class TestVP1X6OneTitleForTheBalanceOfEurope:
    def test_the_tab_the_tooltip_and_the_pointer_agree(self):
        import re
        from backend.ai.counsel import _SURFACE_FOR_KIND
        tscn = (GODOT / "scenes" / "diplomatic_ledger.tscn").read_text(encoding="utf-8")
        block = tscn[tscn.index('[node name="ThreatTab"'):]
        title = re.search(r'text = "([^"]*)"', block).group(1)
        assert title == "BALANCE OF EUROPE"
        assert "Balance of Europe" in _SURFACE_FOR_KIND["balance"][0]
        top_bar = (GODOT / "scripts" / "top_bar.gd").read_text(encoding="utf-8")
        assert "Balance of Europe tab" in top_bar
        for path in (GODOT / "scripts").glob("*.gd"):
            assert "threat & coalition" not in path.read_text(encoding="utf-8").lower(), path.name
        assert "THREAT & COALITION" not in tscn


class TestVP1X8TheCongressIsSummonedFromTheCabinet:
    def test_first_contact_names_the_row_never_the_typed_summons(self, monkeypatch):
        from backend.ai import first_contact as FC
        from backend.game_logic import congress
        world = _shipped()
        clause, _signed = FC._congress_goal_clause(world)
        assert congress.SUMMON_CONTROL in clause
        none_answer = FC._congress_answer("how is the reign won", None)
        assert congress.SUMMON_CONTROL in none_answer
        monkeypatch.setattr(congress, "summon_refusal", lambda w, skip_admin=False: None)
        verdict = FC._congress_answer("can we summon the congress", world)
        assert "It can be summoned this morning, Sire, from the Cabinet" in verdict
        for text in (clause, none_answer, verdict):
            assert f"'{congress.SUMMON_COMMAND}'" not in text
            assert "gold for recognition'" not in text

    def test_the_counsel_and_the_parse_failure_name_the_cabinet(self, monkeypatch):
        from backend.ai import counsel
        from backend.ai.validation import validate_parse_result  # noqa: F401  (the module loads)
        from backend.game_logic import congress
        world = _shipped()
        monkeypatch.setattr(congress, "summon_refusal", lambda w, skip_admin=False: None)
        lines = counsel.congress_counsel(world, world.player_nation)
        assert lines and lines[0].startswith(congress.SUMMON_CONTROL)
        assert congress.SUMMON_COMMAND not in lines[0]
        src = (REPO / "backend" / "ai" / "validation.py").read_text(encoding="utf-8")
        assert "Try: propose peace with" not in src

    def test_an_unbound_name_on_a_cabinet_act_hands_back_the_door(self):
        from backend.commands import executor as E
        src = (REPO / "backend" / "commands" / "executor.py").read_text(encoding="utf-8")
        at = src.index("if command.get(\"action\") in CABINET_ACTIONS:")
        assert "Matters of state are conducted at the Cabinet (F1)." in src[at:at + 400]
        assert E.CommandExecutor.THE_UNBOUND_NAME_SPENDS_NOTHING


class TestVP1X10TheSystemIsAimedAtTheDerivedCourt:
    def test_the_target_is_derived_with_the_legacy_fallback(self):
        from backend.game_logic.diplomacy import SPECIAL_BONUSES, system_target
        assert system_target(_shipped()) == "Britain"
        assert system_target(WorldState()) == "Britain"      # no naval layer
        assert "Britain" not in SPECIAL_BONUSES

    def test_the_lift_desire_follows_the_dominance(self):
        from backend.game_logic.diplomacy import special_bonuses_for, system_target
        from backend.game_logic.diplomatic_templates import continental_system_lift_offered
        world = _shipped()
        assert special_bonuses_for(world, "Britain") == {"continental_system_lifted": 15}
        _dominance_to(world, "Spain")
        assert system_target(world) == "Spain"
        assert special_bonuses_for(world, "Spain") == {"continental_system_lifted": 15}
        assert "continental_system_lifted" not in special_bonuses_for(world, "Britain")
        world.continental_system_members = ["Denmark"]
        assert continental_system_lift_offered(world, "France", "Spain") is True
        assert continental_system_lift_offered(world, "France", "Britain") is False


class TestVP1X15TheReReadPrintsTheDoctrine:
    def test_both_renderers_print_today_doctrine(self):
        for name in ("main.gd", "dispatch_view.gd"):
            gd = (GODOT / "scripts" / name).read_text(encoding="utf-8")
            assert 'today.get("doctrine"' in gd, name


class TestVP1X16TheGoalFallbackReadsTheBar:
    def test_no_literal_45(self, monkeypatch):
        from backend.ai import first_contact as FC
        from backend.ai.state_desk import _answer_goal
        from backend.game_logic import congress
        world = _shipped()
        monkeypatch.setattr(FC, "answer_first_contact", lambda kind, asked, w: "")
        monkeypatch.setattr(congress, "hold_titled", lambda w: 50)
        assert "summoned at 50 titled provinces" in _answer_goal(world, "what is the goal")
