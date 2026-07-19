"""
CR-3 behavior tests — LLM modernization (COMMAND_ROBUSTNESS_SPEC.md).

Contract under test:
  1. Model pin refreshed: claude-haiku-4-5 (the deprecated 2024 Haiku pin
     retires Apr 19, 2026).
  2. Forced tool-use structured output: the parse request carries
     PARSE_TOOL + tool_choice, and the parse is read from the tool_use
     block's input — brace-extraction survives only as a text fallback.
  3. Audit item (a): LLM strategic verbs (pursue/march/support/reinforce)
     remap to executor-dispatchable base actions at the provider seam.
  4. Audit item (b): the dead "dialogue" field is cut from the prompt
     surface and the tool schema (Flavor Echoing stays parked at the
     CR-5 gate).
  5. Audit item (c): an API-layer parse failure sets llm_error, which
     suppresses every SECOND blocking LLM call in the same request
     (Berthier recovery + the CR-2 forced retry).
  6. Audit item (d): diplomatic_data["action"] is validated against an
     allowlist at the anti-hallucination seam, and the cheat gate keys
     off the parse result's key_source instead of the LLM_MODE env var.
  7. Prompt modernization: dynamic per-marshal geography from live grid
     positions, live-roster few-shots, live_phrasing_backlog verb
     coverage, no retired-world geographic block.
  8. build_clarification_prompt is REMOVED (CR-2 disposition executed:
     the shipped clarification dialogue is deterministic).
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.ai.llm_client import LLMClient
from backend.ai.prompt_builder import (
    OUTPUT_SCHEMA,
    _compass_label,
    _format_examples,
    _format_geography,
    build_parse_prompt,
)
from backend.ai.providers import (
    LLM_STRATEGIC_ACTION_REMAP,
    PARSE_TOOL,
    PARSE_TOOL_NAME,
    AnthropicProvider,
    json_to_parse_result,
)
from backend.ai.schemas import ParseResult
from backend.ai.validation import (
    DIPLOMATIC_ACTION_ALLOWLIST,
    validate_parse_result,
)
from backend.commands.parser import CommandParser
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def world1805():
    """Read-only module world — the shipped 126-province 1805 campaign."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _llm_game_state(world):
    """get_llm_game_state()-shaped payload INCLUDING the world reference
    (main.py:148 ships it for command history + CR-3 geography)."""
    from backend.models.intel import FULL, PARTIAL, VISIBILITY_PRIORITY
    marshals = {
        m.name: {"location": m.location, "strength": int(m.strength),
                 "morale": int(m.morale)}
        for m in world.get_player_marshals() if m.strength > 0
    }
    enemies = {}
    for m in world.get_enemy_marshals():
        if m.strength > 0:
            vis = world.get_region_intel(m.location).visibility
            if VISIBILITY_PRIORITY.get(vis, 0) >= VISIBILITY_PRIORITY[PARTIAL]:
                enemies[m.name] = {
                    "location": m.location,
                    "strength": int(m.strength) if vis == FULL else "unknown",
                    "nation": m.nation,
                }
    map_data = {
        name: {"controller": r.controller or "Neutral", "marshals": []}
        for name, r in world.regions.items()
    }
    return {"turn": int(world.current_turn), "gold": int(world.gold),
            "marshals": marshals, "enemies": enemies, "map_data": map_data,
            "world": world}


@pytest.fixture(scope="module")
def gs1805(world1805):
    return _llm_game_state(world1805)


COLD_STATE = {
    "marshals": {"Ney": {"location": "Paris", "strength": 50000}},
    "enemies": {"Wellington": {"location": "Waterloo", "strength": 60000,
                               "nation": "Britain"}},
    "map_data": {"Paris": {}, "Waterloo": {}},
}


def _armed_provider():
    """AnthropicProvider with a fake key so validate_config passes."""
    provider = AnthropicProvider()
    provider._api_key = "sk-test-key"
    return provider


def _tool_response(input_dict):
    """Canned Messages API response carrying the forced tool call."""
    return {
        "content": [
            {"type": "tool_use", "id": "toolu_test", "name": PARSE_TOOL_NAME,
             "input": input_dict},
        ],
        "usage": {"input_tokens": 2500, "output_tokens": 120},
    }


# ═══════════════════════════════════════════════════════════════════
# 1. Model pin
# ═══════════════════════════════════════════════════════════════════

class TestModelPin:
    def test_pin_is_haiku_4_5(self):
        provider = AnthropicProvider()
        assert provider.config.model == "claude-haiku-4-5"

    def test_deprecated_2024_pin_is_gone(self):
        provider = AnthropicProvider()
        assert "20240307" not in provider.config.model


# ═══════════════════════════════════════════════════════════════════
# 2. Forced tool-use structured output
# ═══════════════════════════════════════════════════════════════════

class TestForcedToolUse:
    def test_tool_schema_shape(self):
        assert PARSE_TOOL["name"] == PARSE_TOOL_NAME
        props = PARSE_TOOL["input_schema"]["properties"]
        for field in ("matched", "marshals", "action", "target",
                      "is_strategic", "strategic_type", "ambiguity",
                      "strategic_score", "interpretation", "diplomatic_data"):
            assert field in props, f"tool schema missing {field}"
        required = PARSE_TOOL["input_schema"]["required"]
        assert "action" in required and "marshals" in required

    def test_tool_schema_has_no_dialogue_field(self):
        # Audit item (b): dead field cut; Flavor Echoing parked at CR-5 gate
        assert "dialogue" not in PARSE_TOOL["input_schema"]["properties"]

    def test_parse_request_forces_tool_choice(self, gs1805):
        provider = _armed_provider()
        captured = {}

        def fake_post(body):
            captured.update(body)
            return _tool_response({"matched": True, "marshals": [],
                                   "action": "attack", "target": None,
                                   "ambiguity": 40, "strategic_score": 30,
                                   "interpretation": "x"}), None

        with patch.object(provider, "_post_messages", side_effect=fake_post):
            result = provider.parse("hunt down the enemy", gs1805)

        assert captured["tools"] == [PARSE_TOOL]
        assert captured["tool_choice"] == {"type": "tool",
                                           "name": PARSE_TOOL_NAME}
        assert captured["model"] == "claude-haiku-4-5"
        assert result.matched is True
        assert result.action == "attack"
        assert result.mode == "anthropic"

    def test_tool_input_is_read_without_json_extraction(self, gs1805):
        provider = _armed_provider()
        canned = _tool_response({"matched": True, "marshals": ["Ney"],
                                 "action": "move", "target": "Swabia",
                                 "ambiguity": 10, "strategic_score": 55,
                                 "interpretation": "march"})
        with patch.object(provider, "_post_messages",
                          return_value=(canned, None)):
            result = provider.parse("anything", gs1805)
        assert result.marshals == ["Ney"]
        assert result.target == "Swabia"

    def test_text_block_json_fallback_still_works(self, gs1805):
        # Defensive path: forced tool_choice should make this impossible,
        # but a text response with JSON must not crash the pipeline.
        provider = _armed_provider()
        canned = {
            "content": [{"type": "text", "text":
                         'Here: {"matched": true, "marshals": [], '
                         '"action": "scout", "ambiguity": 20, '
                         '"strategic_score": 10, "interpretation": "s"}'}],
        }
        with patch.object(provider, "_post_messages",
                          return_value=(canned, None)):
            result = provider.parse("anything", gs1805)
        assert result.matched is True
        assert result.action == "scout"

    def test_no_usable_parse_is_not_an_api_error(self, gs1805):
        provider = _armed_provider()
        canned = {"content": [{"type": "text", "text": "I cannot comply."}]}
        with patch.object(provider, "_post_messages",
                          return_value=(canned, None)):
            result = provider.parse("anything", gs1805)
        assert result.matched is False
        assert result.llm_error is False

    def test_api_error_sets_llm_error(self, gs1805):
        provider = _armed_provider()
        with patch.object(provider, "_post_messages",
                          return_value=(None, "Request timed out after 5.0s")):
            result = provider.parse("anything", gs1805)
        assert result.matched is False
        assert result.llm_error is True

    def test_berthier_text_contract_preserved(self):
        # llm_client.generate_berthier_recovery calls _make_api_request
        # directly and expects (text, error) — the CR-3 refactor must not
        # change that contract.
        provider = _armed_provider()
        canned = {"content": [{"type": "text",
                               "text": "Sire, I could not parse that."}]}
        with patch.object(provider, "_post_messages",
                          return_value=(canned, None)):
            text, error = provider._make_api_request("sys", "user")
        assert error is None
        assert text.startswith("Sire")


# ═══════════════════════════════════════════════════════════════════
# 3. Audit item (a): strategic action remap at the provider seam
# ═══════════════════════════════════════════════════════════════════

class TestStrategicActionRemap:
    @pytest.mark.parametrize("verb,expected", [
        ("pursue", "attack"),
        ("march", "move"),
        ("support", "move"),
        ("reinforce", "move"),
    ])
    def test_llm_strategic_verbs_remap(self, verb, expected):
        result = json_to_parse_result(
            {"matched": True, "marshals": [], "action": verb}, "x", "anthropic")
        assert result.action == expected

    def test_normal_actions_pass_through(self):
        result = json_to_parse_result(
            {"matched": True, "marshals": [], "action": "fortify"},
            "x", "anthropic")
        assert result.action == "fortify"

    def test_null_action_stays_null_for_validation(self):
        # July 2026 audit: action=null must reach validate_parse_result's
        # not-result.action guard, not crash the remap.
        result = json_to_parse_result(
            {"matched": True, "marshals": [], "action": None}, "x", "anthropic")
        assert result.action is None

    def test_remap_map_covers_exactly_the_dead_end_verbs(self):
        assert set(LLM_STRATEGIC_ACTION_REMAP) == {
            "pursue", "march", "support", "reinforce"}


# ═══════════════════════════════════════════════════════════════════
# 4. Audit item (b): dialogue field cut from the prompt surface
# ═══════════════════════════════════════════════════════════════════

class TestDialogueFieldCut:
    def test_output_schema_has_no_dialogue(self):
        assert '"dialogue"' not in OUTPUT_SCHEMA

    def test_prompt_never_mentions_dialogue_field(self, gs1805):
        prompt = build_parse_prompt("Ney, attack", gs1805)
        assert '"dialogue"' not in prompt


# ═══════════════════════════════════════════════════════════════════
# 5. Audit item (c): llm_error suppresses second blocking LLM calls
# ═══════════════════════════════════════════════════════════════════

class TestLLMErrorSignal:
    def _live_client(self):
        client = LLMClient(provider="anthropic", api_key="sk-test-key")
        return client

    def test_provider_error_marks_fallback_result(self):
        client = self._live_client()
        error_result = ParseResult(matched=False, action="unknown",
                                   mode="anthropic", llm_error=True)
        with patch.object(client.provider, "parse",
                          return_value=error_result):
            result = client.parse_command_structured(
                "flurble the wibble", COLD_STATE)
        assert result.mode == "mock"          # fast-parser fallback
        assert result.llm_error is True       # signal survives the fallback

    def test_provider_exception_marks_fallback_result(self):
        client = self._live_client()
        with patch.object(client.provider, "parse",
                          side_effect=RuntimeError("boom")):
            result = client.parse_command_structured(
                "flurble the wibble", COLD_STATE)
        assert result.llm_error is True

    def test_reparse_skipped_after_llm_error(self):
        client = self._live_client()
        with patch.object(client.provider, "parse",
                          side_effect=AssertionError("second LLM call fired")):
            retried, retry_llm_error = client.reparse_with_llm(
                "Murat, charge", COLD_STATE,
                {"action": "charge", "mode": "mock", "llm_error": True})
        assert retried is None
        # The pre-existing llm_error short-circuits BEFORE any call, so this
        # retry made none of its own — the flag reports THIS call, not history.
        assert retry_llm_error is False

    def test_berthier_skip_llm_uses_template_without_api_call(self):
        client = self._live_client()
        with patch.object(client.provider, "_make_api_request",
                          side_effect=AssertionError("second LLM call fired")):
            msg = client.generate_berthier_recovery(
                "gibberish order", COLD_STATE, {}, skip_llm=True)
        assert isinstance(msg, str) and len(msg) > 0
        assert "Sire" in msg

    def test_llm_error_reaches_parser_top_level_on_failure(self):
        parser = CommandParser(use_real_llm=False)
        with patch.object(parser.llm, "parse_command",
                          return_value={"marshal": None, "action": "unknown",
                                        "target": None, "confidence": 0.5,
                                        "mode": "mock", "llm_error": True,
                                        "raw_command": "x"}):
            parsed = parser.parse("x", COLD_STATE)
        assert parsed["success"] is False
        assert parsed.get("llm_error") is True

    def test_llm_error_reaches_parser_top_level_on_success(self):
        parser = CommandParser(use_real_llm=False)
        with patch.object(parser.llm, "parse_command",
                          return_value={"marshal": "Ney", "action": "defend",
                                        "target": None, "confidence": 0.9,
                                        "mode": "mock", "llm_error": True,
                                        "raw_command": "Ney, defend"}):
            parsed = parser.parse("Ney, defend", COLD_STATE)
        assert parsed["success"] is True
        assert parsed.get("llm_error") is True

    def test_no_llm_error_key_when_clean(self):
        parser = CommandParser(use_real_llm=False)
        parsed = parser.parse("Ney, defend", COLD_STATE)
        assert parsed["success"] is True
        assert "llm_error" not in parsed

    def test_llm_error_round_trips_serialization(self):
        result = ParseResult(matched=False, llm_error=True)
        data = result.to_dict()
        assert data["llm_error"] is True
        assert ParseResult.from_dict(data).llm_error is True

    def test_llm_error_omitted_from_dict_when_false(self):
        assert "llm_error" not in ParseResult(matched=True).to_dict()


# ═══════════════════════════════════════════════════════════════════
# 6. Audit item (d): diplomatic allowlist + key_source cheat gate
# ═══════════════════════════════════════════════════════════════════

class TestDiplomaticActionAllowlist:
    def _validate(self, result):
        return validate_parse_result(result, ["Ney"], ["Paris"], ["Paris"])

    def test_unknown_diplomatic_action_rejected(self):
        result = ParseResult(
            matched=True, action="diplomatic_proposal",
            diplomatic_data={"action": "seize_the_treasury",
                             "target_nation": "Austria"})
        validated = self._validate(result)
        assert validated.matched is False
        assert validated.diplomatic_data is None
        assert "seize_the_treasury" in (validated.suggestion or "")

    def test_missing_diplomatic_action_rejected(self):
        result = ParseResult(matched=True, action="diplomatic_proposal",
                             diplomatic_data={"target_nation": "Austria"})
        assert self._validate(result).matched is False

    def test_non_dict_diplomatic_data_rejected(self):
        result = ParseResult(matched=True, action="diplomatic_proposal",
                             diplomatic_data="propose peace")
        assert self._validate(result).matched is False

    @pytest.mark.parametrize("action", sorted(DIPLOMATIC_ACTION_ALLOWLIST))
    def test_every_mock_emittable_action_passes(self, action):
        result = ParseResult(
            matched=True, action=action,
            diplomatic_data={"action": action, "target_nation": "Austria"})
        validated = self._validate(result)
        assert validated.matched is True
        assert validated.diplomatic_data is not None

    def test_military_results_without_diplomatic_data_unaffected(self):
        result = ParseResult(matched=True, action="attack", marshals=["Ney"],
                             target="Paris")
        assert self._validate(result).matched is True


class TestCheatGateKeySource:
    def _executor_and_state(self, debug=False):
        from backend.commands.executor import CommandExecutor
        world = WorldState(player_nation="France")
        executor = CommandExecutor()
        gs = {"world": world}
        if debug:
            gs["debug_mode"] = True
        return executor, gs

    def _cheat(self, key_source=None):
        command = {"action": "cheat", "cheat_type": "set_threat",
                   "cheat_args": ["50"]}
        if key_source is not None:
            command["key_source"] = key_source
        return command

    def test_key_source_none_allows_even_under_live_env(self):
        executor, gs = self._executor_and_state()
        with patch.dict(os.environ, {"LLM_MODE": "anthropic"}):
            result = executor._execute_cheat(self._cheat("none"), gs)
        assert result["success"] is True

    def test_key_source_byok_denies_even_under_mock_env(self):
        # The latent BYOK hole: env says mock, but the player armed a key.
        executor, gs = self._executor_and_state()
        with patch.dict(os.environ, {"LLM_MODE": "mock"}):
            result = executor._execute_cheat(self._cheat("byok"), gs)
        assert result["success"] is False
        assert "mock/debug" in result["message"]

    def test_key_source_inhouse_denied_without_debug(self):
        executor, gs = self._executor_and_state()
        result = executor._execute_cheat(self._cheat("inhouse"), gs)
        assert result["success"] is False

    def test_key_source_inhouse_allowed_with_debug(self):
        executor, gs = self._executor_and_state(debug=True)
        result = executor._execute_cheat(self._cheat("inhouse"), gs)
        assert result["success"] is True

    def test_legacy_command_without_key_source_uses_env(self):
        executor, gs = self._executor_and_state()
        with patch.dict(os.environ, {"LLM_MODE": "mock"}):
            allowed = executor._execute_cheat(self._cheat(), gs)
        with patch.dict(os.environ, {"LLM_MODE": "anthropic"}):
            denied = executor._execute_cheat(self._cheat(), gs)
        assert allowed["success"] is True
        assert denied["success"] is False

    def test_parser_threads_key_source_into_cheat_command(self):
        parser = CommandParser(use_real_llm=False)
        parsed = parser.parse("cheat set_threat 50", COLD_STATE)
        assert parsed["success"] is True
        assert parsed["command"]["key_source"] == "none"


# ═══════════════════════════════════════════════════════════════════
# 7. Prompt modernization
# ═══════════════════════════════════════════════════════════════════

class TestPromptModernization:
    def test_legacy_geographic_block_is_gone(self, gs1805):
        prompt = build_parse_prompt("march north", gs1805)
        assert "Central-West: Normandy" not in prompt
        assert "South-East: Bavaria, Vienna" not in prompt

    def test_live_geography_lines_per_marshal(self, gs1805):
        geo = _format_geography(gs1805)
        assert geo is not None
        # One line per positioned player marshal, carrying compass labels
        for name in gs1805["marshals"]:
            assert name in geo
        assert any(label in geo for label in ("N:", "S:", "E:", "W:"))

    def test_geography_absent_without_world(self):
        assert _format_geography(COLD_STATE) is None
        # ...and the prompt still builds with the explicit fallback note
        prompt = build_parse_prompt("march north", COLD_STATE)
        assert "no map orientation data" in prompt

    def test_compass_labels(self):
        assert _compass_label(-1, 0) == "N"
        assert _compass_label(1, 0) == "S"
        assert _compass_label(0, 1) == "E"
        assert _compass_label(0, -1) == "W"
        assert _compass_label(1, 1) == "SE"
        assert _compass_label(-1, -1) == "NW"

    def test_few_shots_use_live_roster_names(self, gs1805):
        examples = _format_examples(gs1805)
        live_enemies = list(gs1805["enemies"])
        assert any(enemy in examples for enemy in live_enemies)
        # The retired-world-only names must not leak into live examples
        for retired in ("Wellington", "Grouchy", "Drouot", "Rhineland"):
            if retired not in gs1805["marshals"] and \
               retired not in gs1805["enemies"] and \
               retired not in gs1805["map_data"]:
                assert retired not in examples

    def test_few_shots_fall_back_to_legacy_names_cold(self):
        examples = _format_examples({})
        assert "Ney" in examples

    def test_few_shot_coverage_of_previously_uncovered_verbs(self, gs1805):
        examples = _format_examples(gs1805)
        for action in ("recruit", "garrison", "form_square", "invest_vassal",
                       "diplomatic_declare_war", "request_terms"):
            assert f'"{action}"' in examples, f"no few-shot for {action}"

    def test_backlog_phrasings_documented(self, gs1805):
        # live_phrasing_backlog (corpus) → CR-3 verb-coverage broadening
        prompt = build_parse_prompt("x", gs1805)
        for phrase in ("hunt down", "run down", "track down", "press on to",
                       "stand fast", "hold your ground", "rally to",
                       "shore up", "combine with"):
            assert phrase in prompt, f"backlog phrasing missing: {phrase}"

    def test_strategic_examples_teach_base_actions(self):
        # Few-shots must teach executor-dispatchable actions, not the
        # dead-end verbs (which are remapped anyway).
        examples = _format_examples({})
        assert '"pursue"' not in examples
        assert '"reinforce"' not in examples

    def test_diplomatic_data_guidance_present(self, gs1805):
        prompt = build_parse_prompt("declare war on Austria", gs1805)
        assert "diplomatic_data" in prompt
        # Pre-CR-3 assertions preserved (test_phase4_batch1_parser.py)
        assert "Diplomatic Commands" in prompt
        assert "MILITARY" in prompt and "NOT diplomatic" in prompt

    def test_prompt_instructs_tool_call(self, gs1805):
        prompt = build_parse_prompt("x", gs1805)
        assert "submit_parsed_command" in prompt


# ═══════════════════════════════════════════════════════════════════
# 8. build_clarification_prompt removed (CR-2 disposition: CUT)
# ═══════════════════════════════════════════════════════════════════

class TestClarificationPromptCut:
    def test_function_is_gone(self):
        import backend.ai.prompt_builder as pb
        assert not hasattr(pb, "build_clarification_prompt")


# ═══════════════════════════════════════════════════════════════════
# 9. Adversarial-review fixes (July 4, 2026 pre-commit pass)
# ═══════════════════════════════════════════════════════════════════

class TestReviewFixes:
    def test_live_results_carry_true_key_source(self):
        # Review fix: providers built ParseResults with key_source="none" —
        # wrong provenance on exactly the path the cheat gate reads.
        client = LLMClient(provider="anthropic", api_key="sk-test-key")
        live = ParseResult(matched=True, action="defend", marshals=["Ney"],
                           mode="anthropic")
        with patch.object(client.provider, "parse", return_value=live):
            result = client.parse_command_structured(
                "flurble the wibble", COLD_STATE)
        assert result.mode == "anthropic"
        assert result.key_source == client.key_source
        assert result.key_source != "none"

    def test_empty_diplomatic_data_normalized_not_killed(self):
        # Review fix: {} is falsy at the dispatch seam — normalize, don't
        # reject an otherwise-valid military parse over it.
        result = ParseResult(matched=True, action="attack", marshals=["Ney"],
                             target="Paris", diplomatic_data={})
        validated = validate_parse_result(result, ["Ney"], ["Paris"], ["Paris"])
        assert validated.matched is True
        assert validated.diplomatic_data is None

    def test_diplomatic_data_field_smuggling_stripped(self):
        # Review fix: confirmation-gate flags are minted by dialogue
        # responses, never by a parse — strip them at the seam.
        result = ParseResult(
            matched=True, action="diplomatic_declare_war",
            diplomatic_data={
                "action": "diplomatic_declare_war",
                "target_nation": "Austria",
                "_treaty_warning_resolved": True,
                "_ally_entry_resolved": True,
                "confirmed_objection": True,
                "war_objective": "conquest",
            })
        validated = validate_parse_result(result, ["Ney"], ["Paris"], ["Paris"])
        assert validated.matched is True
        data = validated.diplomatic_data
        assert data["action"] == "diplomatic_declare_war"
        assert data["target_nation"] == "Austria"
        for smuggled in ("_treaty_warning_resolved", "_ally_entry_resolved",
                         "confirmed_objection", "war_objective"):
            assert smuggled not in data

    def test_max_tokens_headroom_for_tool_call(self):
        # Review fix: measured tool outputs already hit ~300 tokens; 500
        # risked truncating the forced tool call mid-input.
        assert AnthropicProvider().config.max_tokens >= 1000

    def test_single_marshal_world_does_not_graft_retired_names(self):
        from backend.ai.prompt_builder import _example_names
        gs = {"marshals": {"Soult": {"location": "Ulm", "strength": 40000}},
              "enemies": {"Mack": {"location": "Vienna", "strength": 30000,
                                   "nation": "Austria"}},
              "map_data": {"Ulm": {}, "Vienna": {}}}
        names = _example_names(gs)
        assert names["m1"] == "Soult"
        assert names["m2"] == "Soult"          # not "Davout"
        examples = _format_examples(gs)
        assert "Davout" not in examples
        # ...and the self-support pair example is skipped, not rendered
        assert "link up with" not in examples

    def test_fogged_live_world_teaches_generic_not_wellington(self):
        gs = {"marshals": {"Soult": {"location": "Ulm", "strength": 40000}},
              "enemies": {},
              "map_data": {"Ulm": {}, "Vienna": {}}}
        examples = _format_examples(gs)
        assert "Wellington" not in examples
        assert '"generic"' in examples

    def test_cold_state_still_uses_legacy_names(self):
        examples = _format_examples({})
        assert "Ney" in examples and "Wellington" in examples
