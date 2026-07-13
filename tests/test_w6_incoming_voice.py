"""W6-10 — Incoming diplomacy: voice, variety, and honest terms (E-CA-6 + E-CA-5).

Wave 6 slice 10 (docs/WAVE6_FUN_FACTOR_SPEC.md §12):
  1. The diplomat SPEAKS: `incoming_proposal` carries `diplomat_line` — a
     deterministic per-register bank (hawk/schemer/dove/chancery per the
     Voice Bible; every name resolves through resolve_named_diplomat) that
     voices the proposal AND its motive (decision_reason in-character,
     never as a tag).
  2. Anti-monotony: after a proposal of type T from nation N lapses or is
     rejected, N may not re-propose T for 6 turns; the hegemony-pressure
     (P3) trigger picks its ask by relation band instead of always
     open_borders.
  3. E-CA-5 territorial honesty: a settlement offer's terms_summary says
     who keeps what ("Status quo: Britain retains Flanders, Amsterdam").

No LLM anywhere (GR6); diplomacy has no fog (project rule).
"""

from pathlib import Path

import pytest

from backend.game_logic.ai_diplomacy import (
    TYPE_LAPSE_COOLDOWN,
    TYPE_REJECTION_COOLDOWN,
    _build_proposal_terms,
    _hegemony_ask_candidates,
    apply_lapse_type_cooldown,
    apply_rejection_cooldowns,
    build_ai_proposal_dialogue,
    process_diplomatic_phase,
)
from backend.game_logic.diplomatic_templates import (
    compose_incoming_diplomat_line,
)
from backend.game_logic.mailbox_payloads import (
    build_pending_envoy_popup_from_terms,
)
from backend.game_logic.settlement_offers import _derive_status_quo_lines
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _terms(nation, ptype="open_borders"):
    return {"type": ptype, "proposer_nation": nation,
            "target_nation": "France", "sweeteners": [], "demands": [],
            "clauses": []}


# ════════════════════════════════════════════════════════════════════════
# 1. The diplomat speaks
# ════════════════════════════════════════════════════════════════════════


class TestDiplomatLine:
    def test_line_present_and_motive_voiced_not_tagged(self, world):
        payload = build_pending_envoy_popup_from_terms(
            world, nation="Prussia", terms=_terms("Prussia"),
            decision_reason="hegemony_pressure")
        line = payload["diplomat_line"]
        assert line, "diplomat_line missing"
        assert "Hardenberg" in line          # named-cast attribution
        assert "hegemony_pressure" not in line  # raw enum absent — voiced
        assert "Open the borders." in line   # the ask, in-register

    def test_register_matches_the_diplomat(self, world):
        # Metternich (Austria, schemer) — cold politeness, never loud
        line = compose_incoming_diplomat_line(
            world, nation="Austria", proposal_type="non_aggression",
            decision_reason="hegemony_pressure")
        assert "Metternich" in line
        # Einsiedel (Saxony, the dove) — anxious formality
        line = compose_incoming_diplomat_line(
            world, nation="Saxony", proposal_type="non_aggression",
            decision_reason="war_overload")
        assert "Einsiedel" in line
        # Castlereagh (Britain, institutional hawk) — third-person register
        line = compose_incoming_diplomat_line(
            world, nation="Britain", proposal_type="peace",
            decision_reason="war_overload")
        assert "Castlereagh" in line

    def test_loyalist_courts_use_loyalist_register(self, world):
        """DEF-1: the loyalist courts (Spain et al.) now speak in the
        dutiful crown-servant register, not the bare chancery fallback."""
        line = compose_incoming_diplomat_line(
            world, nation="Spain", proposal_type="non_aggression",
            decision_reason="hegemony_pressure")
        assert line
        assert "Cevallos" in line          # the named loyalist minister
        assert "conveys:" not in line      # no longer the chancery register

    def test_loyalist_register_bank_defined(self):
        """DEF-1: the loyalist register class is authored for all four
        decision reasons with two deterministic variants and a {nation}
        slot (the Voice Bible-owned register class)."""
        from backend.game_logic.diplomatic_templates import (
            _INCOMING_MOTIVE_LINES,
        )
        for reason in ("war_overload", "shared_enemy_survival",
                       "hegemony_pressure", "unknown_baseline"):
            variants = _INCOMING_MOTIVE_LINES[("loyalist", reason)]
            assert len(variants) == 2
            for line in variants:
                assert "{nation}" in line

    def test_all_europe_courts_have_bespoke_voices(self, world):
        """DEF-1 Roster Voices: every one of the 15 Europe courts resolves
        to its own named voice (never the bare chancery fallback) across
        all four decision reasons — the token is a fragment of that court's
        authored attribution."""
        courts = {
            "Russia": "Czartoryski", "Bavaria": "Montgelas",
            "Ottoman": "Reis Efendi", "Naples": "Medici",
            "Portugal": "Araujo", "PapalStates": "Consalvi",
            "Hanover": "Hanover", "Hesse": "Hesse",
            "Switzerland": "Helvetic", "Spain": "Cevallos",
            "Sweden": "Ehrenheim", "Denmark": "Bernstorff",
            "Sardinia": "Sardinian", "Holland": "Schimmelpenninck",
            "KingdomOfItaly": "Marescalchi",
        }
        for nation, token in courts.items():
            for reason in ("war_overload", "shared_enemy_survival",
                           "hegemony_pressure", "unknown_baseline"):
                line = compose_incoming_diplomat_line(
                    world, nation=nation, proposal_type="peace",
                    decision_reason=reason)
                assert token in line, (nation, reason, line)
                assert "conveys:" not in line, (nation, reason, line)

    def test_unknown_court_gets_chancery_line(self):
        legacy = WorldState(player_nation="France")
        line = compose_incoming_diplomat_line(
            legacy, nation="Prussia", proposal_type="open_borders",
            decision_reason="unknown_baseline")
        assert line  # STARTING_DIPLOMATS or chancery — never empty

    def test_deterministic_and_varied(self, world):
        a = compose_incoming_diplomat_line(
            world, nation="Prussia", proposal_type="open_borders",
            decision_reason="hegemony_pressure")
        b = compose_incoming_diplomat_line(
            world, nation="Prussia", proposal_type="open_borders",
            decision_reason="hegemony_pressure")
        assert a == b  # same inputs, same line (GR6, no RNG)
        world.current_turn += 1
        c = compose_incoming_diplomat_line(
            world, nation="Prussia", proposal_type="open_borders",
            decision_reason="hegemony_pressure")
        assert c != a  # the 2-variant rotation actually rotates

    def test_typed_surface_carries_the_line(self, world):
        proposal = {
            "source": "Prussia", "proposal_type": "open_borders",
            "priority": 3, "terms": _terms("Prussia"),
            "talleyrand_assessment": "An assessment.",
            "decision_reason": "hegemony_pressure",
            "turn_generated": int(world.current_turn),
        }
        dialogue = build_ai_proposal_dialogue(proposal, world)
        assert dialogue["popup_payload"]["diplomat_line"] in \
            dialogue["talleyrand_text"]


# ════════════════════════════════════════════════════════════════════════
# 2. Anti-monotony
# ════════════════════════════════════════════════════════════════════════


class TestAntiMonotony:
    def test_blessed_cooldowns(self):
        assert TYPE_REJECTION_COOLDOWN == 6  # blessed (band 4-10)
        assert TYPE_LAPSE_COOLDOWN == 6

    def test_rejection_blocks_type_for_six_turns(self, world):
        apply_rejection_cooldowns("Prussia", "open_borders", world)
        assert world.ai_proposal_cooldowns["Prussia|open_borders"] == 6

    def test_lapse_blocks_type_for_six_turns(self, world):
        apply_lapse_type_cooldown("Prussia", "open_borders", world)
        assert world.ai_proposal_cooldowns["Prussia|open_borders"] == 6
        # unknown/absent types never write a key
        apply_lapse_type_cooldown("Prussia", "unknown", world)
        apply_lapse_type_cooldown("Prussia", "", world)
        assert "Prussia|unknown" not in world.ai_proposal_cooldowns
        assert "Prussia|" not in world.ai_proposal_cooldowns

    def test_lapse_info_prefers_stable_label(self):
        """The documented cooldown trap: terms['type'] is rewritten
        (harsh_peace -> 'peace'); the lapse info must carry the stable
        P-rule label from the dialogue context."""
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        info = dm._extract_lapse_info({
            "type": "incoming_proposal", "target_nation": "Austria",
            "context": {"proposal": {"type": "peace"},
                        "proposal_type": "harsh_peace"},
        })
        assert info["proposal_type"] == "harsh_peace"

    def test_lapsed_offer_blocks_retype_end_to_end(self, world):
        """An unanswered offer of type T blocks T for 6 turns at the
        turn_manager lapse seam."""
        from backend.game_logic.turn_manager import TurnManager
        dialogue = {
            "type": "incoming_proposal", "target_nation": "Prussia",
            "talleyrand_text": "x",
            "options": [{"label": "Accept", "description": "",
                         "action": "accept_ai_proposal"}],
            "context": {"proposal": _terms("Prussia"),
                        "source_nation": "Prussia",
                        "proposal_type": "open_borders"},
            "turn_created": int(world.current_turn), "blocking": False,
        }
        world.dialogue_manager.push(dialogue)
        tm = TurnManager(world)
        tm.end_turn()
        assert world.ai_proposal_cooldowns.get(
            "Prussia|open_borders", 0) >= TYPE_LAPSE_COOLDOWN - 1

    def test_hegemony_ask_varies_by_relation_band(self, world):
        # Warm court: the ladder upgrade leads
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = 40
        assert _hegemony_ask_candidates("Prussia", "PEACE", 40, world)[0] \
            == "open_borders"  # PEACE ladder rung
        # Neutral court: non-aggression leads (relation 10 meets req 0)
        candidates = _hegemony_ask_candidates("Prussia", "PEACE", 10, world)
        assert candidates[0] == "non_aggression"
        assert "friendly_gift" in candidates
        # Cool court: the gift leads; non_aggression (req 0) is illegal
        candidates = _hegemony_ask_candidates("Prussia", "PEACE", -10, world)
        assert candidates[0] == "friendly_gift"
        assert "non_aggression" not in candidates

    def test_friendly_gift_terms_shape(self, world):
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = -10
        world.nation_gold["Prussia"] = 1000
        terms = _build_proposal_terms("Prussia", "friendly_gift", 0, world)
        assert terms["type"] == "open_borders"  # legal at relation -10
        assert any(s["type"] == "gold_lump" for s in terms["sweeteners"])
        world.nation_relations[key] = 10
        terms = _build_proposal_terms("Prussia", "friendly_gift", 0, world)
        assert terms["type"] == "non_aggression"

    def test_trigger_diversifies_after_block(self, world):
        """The audit's five-identical-proposals loop: once the first ask is
        blocked (rejected/lapsed), the next P3 approach differs."""
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.nation_relations[key] = 10
        world.threat_level = 70
        world.nation_gold["Prussia"] = 1000
        first = process_diplomatic_phase("Prussia", world)
        assert first is not None
        first_type = first["proposal_type"]
        apply_lapse_type_cooldown("Prussia", first_type, world)
        second = process_diplomatic_phase("Prussia", world)
        assert second is not None
        assert second["proposal_type"] != first_type


class TestCounterOfferCarriesStableLabel:
    def test_counter_dialogue_context_keeps_proposal_type(self, world,
                                                          monkeypatch):
        """Review fix: the successful-counter dialogue must carry the
        STABLE P-rule label so a rejected/lapsed counter keys the type
        cooldown on the label the P-rule checks read (harsh_peace), never
        the rewritten terms type (peace) — the documented trap."""
        import backend.game_logic.ai_diplomacy as aidip
        from backend.commands.executor import CommandExecutor

        harsh_terms = {"type": "peace", "proposer_nation": "Austria",
                       "target_nation": "France", "sweeteners": [],
                       "demands": [{"type": "gold_lump", "value": 500}],
                       "clauses": []}
        monkeypatch.setattr(aidip, "generate_counter_offer",
                            lambda terms, w: dict(terms))
        dialogue = {
            "type": "incoming_proposal", "target_nation": "Austria",
            "talleyrand_text": "x",
            "options": [],
            "context": {"proposal": harsh_terms,
                        "source_nation": "Austria",
                        "proposal_type": "harsh_peace",
                        "decision_reason": "war_overload"},
            "turn_created": int(world.current_turn), "blocking": False,
        }
        world.diplomatic_points = 3
        executor = CommandExecutor()
        result = executor._diplomatic._handle_counter_ai_proposal(
            dialogue, world)
        assert result["success"] is True, result.get("message")
        counter = world.pending_diplomatic_dialogue
        assert counter["type"] == "counter_offer"
        assert counter["context"]["proposal_type"] == "harsh_peace"
        # And the lapse extractor reads the stable label from it
        info = world.dialogue_manager._extract_lapse_info(counter)
        assert info["proposal_type"] == "harsh_peace"


# ════════════════════════════════════════════════════════════════════════
# 3. E-CA-5 — territorial honesty
# ════════════════════════════════════════════════════════════════════════


class TestTerritorialHonesty:
    def _war(self, **side_by_nation):
        return {"side_by_nation": side_by_nation}

    def test_lists_exactly_the_occupied_home_regions(self, world):
        britain_home = list(world.nation_starting_regions.get("Britain", []))
        france_home = list(world.nation_starting_regions.get("France", []))
        assert britain_home and france_home
        # Britain occupies two French homeland provinces
        occupied = france_home[:2]
        for r in occupied:
            world.regions[r].controller = "Britain"
        world.invalidate_active_nations_cache()
        lines = _derive_status_quo_lines(
            world, self._war(Britain="attackers", France="defenders"))
        assert len(lines) == 1
        assert lines[0] == f"Britain retains {', '.join(sorted(occupied))}"

    def test_no_line_without_occupation(self, world):
        lines = _derive_status_quo_lines(
            world, self._war(Britain="attackers", France="defenders"))
        assert lines == []

    def test_same_side_holdings_never_listed(self, world):
        france_home = list(world.nation_starting_regions.get("France", []))
        world.regions[france_home[0]].controller = "Spain"
        world.invalidate_active_nations_cache()
        # Spain fights BESIDE France — its holding is not "retained soil"
        lines = _derive_status_quo_lines(
            world, self._war(Britain="attackers", France="defenders",
                             Spain="defenders"))
        assert lines == []

    def test_third_party_occupation_listed_without_fog(self, world):
        """Diplomacy has no fog (project rule): an occupation the player
        has never scouted still appears in the status-quo line."""
        russia_home = list(world.nation_starting_regions.get("Russia", []))
        assert russia_home
        target = russia_home[0]
        world.regions[target].controller = "Austria"
        world.invalidate_active_nations_cache()
        lines = _derive_status_quo_lines(
            world, self._war(Austria="attackers", Russia="defenders",
                             France="defenders"))
        assert any(line.startswith("Austria retains") and target in line
                   for line in lines)

    def test_offer_popup_appends_status_quo(self, world):
        france_home = list(world.nation_starting_regions.get("France", []))
        occupied = france_home[0]
        world.regions[occupied].controller = "Britain"
        world.invalidate_active_nations_cache()
        world.war_instances["war_9"] = {
            "war_id": "war_9",
            "side_by_nation": {"Britain": "attackers", "France": "defenders"},
            "attacker_leader": "Britain", "defender_leader": "France",
            "participants": ["Britain", "France"],
        }
        from backend.game_logic.settlement_offers import (
            build_incoming_settlement_offer_popup,
        )
        payload = build_incoming_settlement_offer_popup(world, {
            "offer_id": "settlement_offer:war_9:1:1",
            "war_id": "war_9",
            "proposer_nation": "Britain",
            "proposer_side": "attackers",
            "accepting_side": "defenders",
            "accepting_leader": "France",
            "covered_enemy_participants": [],
            "settlement_terms": [{"type": "peace"}],
            "turn_created": 1,
        })
        status_lines = [s for s in payload["terms_summary"]
                        if s.startswith("Status quo:")]
        assert len(status_lines) == 1
        assert "Britain retains" in status_lines[0]
        assert occupied in status_lines[0]
