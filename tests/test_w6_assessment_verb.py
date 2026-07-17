"""W6-9 — "What does Europe intend?": the strategic assessment verb (EXP-D1).

Wave 6 slice 9 (docs/WAVE6_FUN_FACTOR_SPEC.md §11): "Talleyrand, assess our
situation" — the exact phrase that dead-ended in the live creative audit —
returns the war room: per-war trajectory in prose, the coalition's POSTURE
(computed for the AI six times over, shown to the player for the first time
here), the top-3 itemized threat sources, vassal loyalty trend + cause, and
ONE recommendation ending in an executable option (R117).

Composition only — no new formulas, no LLM (GR6); fog-safe via the same
builders the ledgers use; diplomacy itself has no fog (project rule).
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.commands.executor import CommandExecutor
from backend.game_logic.diplomatic_advisory import (
    _build_situation_recommendation,
    detect_advisory_type,
    generate_advisory,
)
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


# ════════════════════════════════════════════════════════════════════════
# Keyword routing
# ════════════════════════════════════════════════════════════════════════


class TestAdvisoryTypeDetection:
    @pytest.mark.parametrize("phrase", [
        "assess our situation",
        "Talleyrand, assess the situation",
        "what is the state of Europe?",
        "where do we stand",
        "how do we stand",
        "give me a situation report",
        "what does Europe intend?",
        "assess",
    ])
    def test_assessment_phrasings_route(self, phrase):
        assert detect_advisory_type(phrase) == "assess_situation"

    def test_what_about_still_wins_over_bare_assess(self):
        # Longest-first: the nation-question keyword keeps its arm.
        assert detect_advisory_type("what about Austria") == "assess_nation"

    def test_named_target_downgrades_to_nation_assessment(self, world):
        dialogue = generate_advisory("Austria", "assess_situation", world)
        # The nation arm, not the war room
        assert dialogue["target_nation"] == "Austria"
        assert dialogue["context"].get("advisory_type") != "assess_situation"


# ════════════════════════════════════════════════════════════════════════
# The war room payload
# ════════════════════════════════════════════════════════════════════════


class TestWarRoom:
    def test_payload_carries_posture_threats_and_recommendation(self, world):
        world.threat_sources_this_turn = [
            {"source": "battle_win", "amount": 8},
            {"source": "war_declaration", "amount": 15},
            {"source": "decay", "amount": -2},
            {"source": "region_capture", "amount": 5},
        ]
        dialogue = generate_advisory(None, "assess_situation", world)
        assert dialogue["type"] == "advisory"
        ctx = dialogue["context"]
        assert ctx["advisory_type"] == "assess_situation"
        assert ctx["posture"] in ("aggressive", "defensive", "cautious")
        # Top-3 by magnitude, humanized
        assert len(ctx["threat_sources"]) == 3
        assert ctx["threat_sources"][0]["label"] == "Declared war"
        # The 1805 boot has wars — trajectory rows present
        assert len(ctx["wars"]) >= 1
        for row in ctx["wars"]:
            # NA-1 (July 17, 2026): each war row now carries the
            # belligerents' agenda payloads for the design lines.
            assert set(row) == {"opponent", "war_score", "trend", "agendas"}
        # ONE recommendation, never a list, ending in an executable option
        assert ctx["recommendation"] is not None
        executable = dialogue["options"][0]
        assert executable["action"] in ("expand_options", "execute_suggestion")
        assert dialogue["options"][-1]["action"] == "dismiss"
        # The posture is IN the prose (surfaced, not just data)
        assert ctx["posture"].upper() in dialogue["talleyrand_text"] \
            or "No coalition" in dialogue["talleyrand_text"]

    def test_war_lines_present_in_prose(self, world):
        dialogue = generate_advisory(None, "assess_situation", world)
        text = dialogue["talleyrand_text"]
        assert "Against " in text  # at least one war line (1805 boot wars)
        assert "My counsel, Sire:" in text

    def test_fog_safety_no_exact_enemy_strength(self, world):
        """The war room composes from fog-safe builders and renders no army
        strengths at all — an unseen enemy's exact total must not leak."""
        enemy_total = sum(m.strength for m in world.marshals.values()
                          if m.nation == "Austria")
        dialogue = generate_advisory(None, "assess_situation", world)
        assert f"{enemy_total:,}" not in dialogue["talleyrand_text"]
        assert str(enemy_total) not in dialogue["talleyrand_text"]

    def test_vassal_block_with_trend_and_cause(self, world):
        world.vassals["Switzerland"] = {
            "lord": "France", "loyalty": 45, "autonomy": 1,
            "path": "conquest", "created_turn": 1, "tribute_rate": 0.5,
            "regions": [],
        }
        world.log_event({
            "type": "vassal_loyalty", "vassal": "Switzerland",
            "lord": "France", "nation": "France",
            "old_loyalty": 50, "new_loyalty": 45, "delta": -5,
            "reason": "puppet resentment, war weariness",
            "turn": world.current_turn,
        })
        dialogue = generate_advisory(None, "assess_situation", world)
        ctx = dialogue["context"]
        assert ctx["vassals"], "vassal block missing"
        entry = next(v for v in ctx["vassals"] if v["vassal"] == "Switzerland")
        assert entry["loyalty"] == 45
        assert entry["trend"] in ("rising", "falling", "steady")
        assert "puppet resentment" in entry["reason"]
        assert "Switzerland" in dialogue["talleyrand_text"]


# ════════════════════════════════════════════════════════════════════════
# The recommendation table (deterministic, priority order)
# ════════════════════════════════════════════════════════════════════════


class TestRecommendationTable:
    def test_losing_war_with_terms_available_recommends_seek_terms(self, world):
        rows = [{"opponent": "Austria", "war_score": -25, "trend": "falling",
                 "status": "war",
                 "request_terms_state": {"state": "available"},
                 "settlement_available": True}]
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec["kind"] == "request_terms"
        assert rec["target_nation"] == "Austria"

    def test_losing_war_without_terms_falls_to_open_talks(self, world):
        rows = [{"opponent": "Austria", "war_score": -25, "trend": "falling",
                 "status": "war",
                 "request_terms_state": {"state": "disabled"},
                 "settlement_available": True}]
        rec = _build_situation_recommendation(world, "France", rows, None,
                                              "defensive")
        assert rec["kind"] == "open_proposal"
        assert rec["target_nation"] == "Austria"

    def test_aggressive_coalition_recommends_shoring_weakest_ally(self, world):
        world.threat_level = 70
        key = world._make_diplo_key("France", "Bavaria")
        world.diplomatic_states[key] = "ALLIANCE"
        world.nation_relations[key] = 20
        rec = _build_situation_recommendation(
            world, "France", [], {"weak_link": "Prussia"}, "aggressive")
        assert rec["kind"] == "open_proposal"
        assert rec["target_nation"] == "Bavaria"

    def test_low_vassal_recommends_investment(self, world):
        world.vassals["Switzerland"] = {
            "lord": "France", "loyalty": 30, "autonomy": 1,
            "path": "conquest", "created_turn": 1, "tribute_rate": 0.5,
            "regions": [],
        }
        rec = _build_situation_recommendation(world, "France", [], None,
                                              "defensive")
        assert rec["kind"] == "invest_vassal"
        assert rec["target"] == "Switzerland"

    def test_default_picks_open_cooldown_nation_in_band(self, world):
        rec = _build_situation_recommendation(world, "France", [], None,
                                              "defensive")
        # 1805 boot: neutral courts exist in the -10..40 band
        assert rec is not None
        assert rec["kind"] == "open_proposal"
        target = rec["target_nation"]
        assert not world.is_at_war("France", target)
        rel = world.nation_relations.get(
            world._make_diplo_key("France", target), 0)
        assert -10 <= rel <= 40


# ════════════════════════════════════════════════════════════════════════
# The executable option (R117) — execute_suggestion
# ════════════════════════════════════════════════════════════════════════


class TestExecutableOption:
    def test_invest_suggestion_executes_through_the_real_executor(self, world):
        world.vassals["Switzerland"] = {
            "lord": "France", "loyalty": 30, "autonomy": 1,
            "path": "conquest", "created_turn": 1, "tribute_rate": 0.5,
            "regions": [],
        }
        world.diplomatic_points = 3
        world.nation_gold["France"] = 1000
        # Quiet the higher-priority rules: the 1805 boot legitimately runs
        # threat > 60 with an aggressive posture (rule 2 would win), and
        # NA-1's rung 1.5 legitimately counsels satisfying Austria's
        # design at the boot coalition war (strip the decks so the
        # invest rung is reachable).
        world.threat_level = 0
        world.agendas = {}
        world._agenda_cache = None
        dialogue = generate_advisory(None, "assess_situation", world)
        assert dialogue["options"][0]["action"] == "execute_suggestion"
        world.dialogue_manager.replace(dialogue)
        executor = CommandExecutor()
        result = executor.handle_diplomatic_dialogue_response(
            1, {"world": world})
        assert result["success"] is True, result.get("message")
        assert world.vassals["Switzerland"]["loyalty"] == 40
        assert "new_state" not in result

    def test_lapsed_suggestion_refuses_gracefully(self, world):
        dialogue = {
            "type": "advisory", "target_nation": "",
            "talleyrand_text": "x",
            "options": [
                {"label": "Do it", "description": "",
                 "action": "execute_suggestion",
                 "terms": {"suggestion": {"kind": "unknown_kind"}}},
                {"label": "Thank you", "description": "",
                 "action": "dismiss"},
            ],
            "context": {}, "turn_created": 1, "blocking": False,
        }
        world.dialogue_manager.replace(dialogue)
        executor = CommandExecutor()
        result = executor.handle_diplomatic_dialogue_response(
            1, {"world": world})
        assert result["success"] is False
        assert "lapsed" in result["message"]


# ════════════════════════════════════════════════════════════════════════
# Typed surface — the audit's dead end, reversed
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def endpoint():
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP

    original_parser = main_module.parser
    original_world = main_module.world
    original_game_state = main_module.game_state
    main_module.parser = _CP(use_real_llm=False)
    main_module.world = WorldState.from_scenario(str(SCENARIO_PATH))
    main_module.game_state = {"world": main_module.world}
    try:
        yield TestClient(main_module.app), main_module
    finally:
        main_module.parser = original_parser
        main_module.world = original_world
        main_module.game_state = original_game_state


class TestTypedSurface:
    def test_assess_our_situation_reaches_the_war_room(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={
            "command": "Talleyrand, assess our situation"}).json()
        assert data["success"] is True
        # NOT the swallowing nation-picker (the audit's dead end)
        assert "which nation shall I approach" not in data["message"]
        assert "state of Europe" in data["message"]
        dialogue = m.world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue["type"] == "advisory"
        assert dialogue["context"]["advisory_type"] == "assess_situation"

    def test_question_form_reaches_the_war_room(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={
            "command": "Talleyrand, what is the state of Europe?"}).json()
        assert data["success"] is True
        dialogue = m.world.pending_diplomatic_dialogue
        assert dialogue["context"]["advisory_type"] == "assess_situation"

    def test_assess_nation_still_gets_nation_assessment(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={
            "command": "Talleyrand, what about Austria?"}).json()
        assert data["success"] is True
        dialogue = m.world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue["target_nation"] == "Austria"
        assert dialogue["context"].get("advisory_type") != "assess_situation"

    def test_advisory_costs_nothing(self, endpoint):
        client, m = endpoint
        ap_before = int(m.world.actions_remaining)
        dp_before = int(m.world.diplomatic_points)
        client.post("/command", json={
            "command": "Talleyrand, assess our situation"})
        assert int(m.world.actions_remaining) == ap_before
        assert int(m.world.diplomatic_points) == dp_before
