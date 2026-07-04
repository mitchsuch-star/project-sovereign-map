"""CR-4 behavior tests (COMMAND_ROBUSTNESS_SPEC.md §2 CR-4).

Context carryover on the existing ``world.command_history`` substrate:
- Semantic reference resolution ("again", "same target", "him"/"there",
  "not you, Davout") — deterministic pre-parse rewrites (Golden Rule 6).
- Persistent Command Focus — a bare specific order defaults to the marshal
  the player is already commanding instead of re-asking.
- The CR-4 recording decisions: history records in BOTH mock and live modes,
  and each entry now carries the parsed ``target``.

The reference resolver and focus fallback live in main.py's player-command
path (never for AI commands, which share the executor but not the endpoint),
so the wiring is pinned end-to-end through the /command endpoint alongside
the unit coverage of the pure resolver.
"""

import pytest
from fastapi.testclient import TestClient

from backend.ai.parser_eval import build_world, build_llm_game_state
from backend.commands.context_carryover import (
    get_focus_marshal,
    resolve_context_references,
    _reconstruct_order,
)


# ════════════════════════════════════════════════════════════════════════
# Fixtures / helpers
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def world():
    w = build_world("legacy")
    w.command_history = []
    return w


def _order(raw_input, marshal, action, target, turn=1):
    return {"raw_input": raw_input, "marshal": marshal,
            "action": action, "target": target, "turn": turn}


def seed(w, *entries):
    w.command_history = list(entries)


# ════════════════════════════════════════════════════════════════════════
# "again" — repeat the last order verbatim
# ════════════════════════════════════════════════════════════════════════

class TestAgain:
    @pytest.mark.parametrize("phrase", [
        "again", "Again", "do it again", "do that again", "once more",
        "repeat that", "same order", "as before", "the same again.",
    ])
    def test_again_repeats_last_order(self, world, phrase):
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        out = resolve_context_references(phrase, world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Ney, attack Wellington"

    def test_again_skips_non_order_entries(self, world):
        seed(world,
             _order("Ney, attack Wellington", "Ney", "attack", "Wellington", 1),
             _order("status", None, "status", None, 1))
        out = resolve_context_references("again", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Ney, attack Wellington"

    def test_again_with_empty_history_errors(self, world):
        out = resolve_context_references("again", world)
        assert out["kind"] == "error"
        assert "repeat" in out["message"].lower()

    def test_again_reconstructs_when_raw_input_missing(self, world):
        seed(world, {"marshal": "Davout", "action": "move",
                     "target": "Belgium", "turn": 1})
        out = resolve_context_references("again", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Davout, move to Belgium"


# ════════════════════════════════════════════════════════════════════════
# "not you, X" — re-address the last order to another marshal
# ════════════════════════════════════════════════════════════════════════

class TestReaddress:
    def test_not_you_reissues_to_named_marshal(self, world):
        seed(world, _order("attack Wellington", None, "attack", "Wellington"))
        out = resolve_context_references("not you, Davout", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Davout, attack Wellington"

    def test_no_comma_name_reissues(self, world):
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        out = resolve_context_references("no, Grouchy", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Grouchy, attack Wellington"

    def test_readdress_tolerates_typo(self, world):
        seed(world, _order("attack Wellington", None, "attack", "Wellington"))
        out = resolve_context_references("not you, Davut", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Davout, attack Wellington"

    def test_readdress_with_filler_phrase(self, world):
        seed(world, _order("attack Wellington", None, "attack", "Wellington"))
        out = resolve_context_references("not you — I meant Davout", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Davout, attack Wellington"

    def test_readdress_reconstructs_move_verb(self, world):
        seed(world, _order("Ney, move to Belgium", "Ney", "move", "Belgium"))
        out = resolve_context_references("not you, Grouchy", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Grouchy, move to Belgium"

    def test_readdress_unknown_name_passes(self, world):
        # A cue with a name that resolves to no marshal is not treated as a
        # re-address — it falls through to the normal pipeline.
        seed(world, _order("attack Wellington", None, "attack", "Wellington"))
        out = resolve_context_references("no worries about that", world)
        assert out["kind"] == "pass"

    def test_bare_not_you_passes_through(self, world):
        # Bare "not you" (no resolvable name) is a dialogue decline / stray
        # correction — it must pass, never hijack (so it reaches the dialogue
        # routing or Berthier).
        seed(world, _order("attack Wellington", None, "attack", "Wellington"))
        assert resolve_context_references("not you", world)["kind"] == "pass"
        assert resolve_context_references("no", world)["kind"] == "pass"

    def test_bare_not_you_without_history_passes(self, world):
        out = resolve_context_references("not you", world)
        assert out["kind"] == "pass"

    def test_readdress_reissues_underscore_action_from_raw(self, world):
        # "not you, X" after a form_square order re-issues the player's OWN
        # phrasing, dodging the unparseable "form_square" key (finding-7).
        seed(world, _order("Ney, form square", "Ney", "form_square", None))
        out = resolve_context_references("not you, Davout", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Davout, form square"

    def test_cue_with_reference_resolves_reference(self, world):
        # "no, attack him" — the cue is not a re-address, so it falls through
        # and the pronoun still resolves (finding-9).
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        out = resolve_context_references("no, attack him", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "attack Wellington"


# ════════════════════════════════════════════════════════════════════════
# "same target" — reuse the last objective
# ════════════════════════════════════════════════════════════════════════

class TestSameTarget:
    def test_same_target_substitutes_last_target(self, world):
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        out = resolve_context_references("Grouchy, scout the same target", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Grouchy, scout Wellington"

    def test_same_place_substitutes_region(self, world):
        seed(world, _order("Ney, move to Belgium", "Ney", "move", "Belgium"))
        out = resolve_context_references("Davout, march to the same place", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Davout, march to Belgium"

    def test_same_target_no_history_errors(self, world):
        out = resolve_context_references("attack the same target", world)
        assert out["kind"] == "error"
        assert "objective" in out["message"].lower()

    def test_same_enemy_prefers_enemy_over_recent_region(self, world):
        # "same enemy" must reach the last ENEMY, not the most-recent target
        # of any kind (finding-4).
        seed(world,
             _order("Ney, attack Wellington", "Ney", "attack", "Wellington", 1),
             _order("Davout, move to Belgium", "Davout", "move", "Belgium", 2))
        out = resolve_context_references("Soult, attack the same enemy", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Soult, attack Wellington"

    def test_same_place_prefers_region_over_recent_enemy(self, world):
        seed(world,
             _order("Davout, move to Belgium", "Davout", "move", "Belgium", 1),
             _order("Ney, attack Wellington", "Ney", "attack", "Wellington", 2))
        out = resolve_context_references("Grouchy, march to the same place", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Grouchy, march to Belgium"


# ════════════════════════════════════════════════════════════════════════
# Pronouns / deixis — "him"/"her"/"them" and "there"
# ════════════════════════════════════════════════════════════════════════

class TestPronouns:
    def test_him_resolves_to_last_enemy(self, world):
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        out = resolve_context_references("Davout, attack him", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Davout, attack Wellington"

    def test_them_resolves_to_last_enemy(self, world):
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        out = resolve_context_references("charge them", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "charge Wellington"

    def test_person_pronoun_prefers_enemy_over_recent_region(self, world):
        # Most recent target is a region, but a person pronoun should reach
        # back to the last ENEMY named.
        seed(world,
             _order("Ney, attack Wellington", "Ney", "attack", "Wellington", 1),
             _order("Davout, move to Belgium", "Davout", "move", "Belgium", 2))
        out = resolve_context_references("Grouchy, attack him", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Grouchy, attack Wellington"

    def test_there_resolves_to_last_region(self, world):
        seed(world, _order("Ney, move to Belgium", "Ney", "move", "Belgium"))
        out = resolve_context_references("Davout, hold there", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == "Davout, hold Belgium"

    def test_there_falls_back_to_enemy_location(self, world):
        # No region has been targeted, but the last-named enemy stands
        # somewhere — "there" resolves to that province.
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        enemy_loc = world.get_marshal("Wellington").location
        out = resolve_context_references("Davout, march there", world)
        assert out["kind"] == "rewrite"
        assert out["command"] == f"Davout, march {enemy_loc}"

    def test_incidental_pronoun_without_referent_passes(self, world):
        # No history at all — an incidental pronoun is not hijacked into an
        # error; it passes to the parser (which handles it).
        out = resolve_context_references("Davout, attack him", world)
        assert out["kind"] == "pass"

    def test_person_pronoun_never_falls_back_to_region(self, world):
        # Only a region was ever targeted — "him" must NOT become that
        # province (finding-5); it passes to the parser instead.
        seed(world, _order("Ney, move to Belgium", "Ney", "move", "Belgium"))
        out = resolve_context_references("Davout, attack him", world)
        assert out["kind"] == "pass"


# ════════════════════════════════════════════════════════════════════════
# Pass-through — plain commands are untouched
# ════════════════════════════════════════════════════════════════════════

class TestPassThrough:
    @pytest.mark.parametrize("cmd", [
        "Ney, attack Wellington",
        "move to Belgium",
        "status",
        "end turn",
        "Grouchy, scout Paris",
    ])
    def test_plain_command_passes(self, world, cmd):
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        assert resolve_context_references(cmd, world)["kind"] == "pass"

    def test_empty_and_none_pass(self, world):
        assert resolve_context_references("", world)["kind"] == "pass"
        assert resolve_context_references("attack", None)["kind"] == "pass"


# ════════════════════════════════════════════════════════════════════════
# Persistent Command Focus — get_focus_marshal
# ════════════════════════════════════════════════════════════════════════

class TestFocusMarshal:
    def test_focus_is_last_addressed_marshal(self, world):
        seed(world,
             _order("Ney, attack Wellington", "Ney", "attack", "Wellington", 1),
             _order("Davout, scout Belgium", "Davout", "scout", "Belgium", 2))
        focus = get_focus_marshal(world)
        assert focus is not None and focus.name == "Davout"

    def test_focus_skips_marshalless_entries(self, world):
        seed(world,
             _order("Ney, attack Wellington", "Ney", "attack", "Wellington", 1),
             _order("attack Wellington", None, "attack", "Wellington", 2))
        focus = get_focus_marshal(world)
        assert focus is not None and focus.name == "Ney"

    def test_focus_none_on_empty_history(self, world):
        assert get_focus_marshal(world) is None

    def test_focus_skips_dead_marshal(self, world):
        seed(world, _order("Ney, attack Wellington", "Ney", "attack", "Wellington"))
        world.get_marshal("Ney").strength = 0
        assert get_focus_marshal(world) is None


class TestReconstruct:
    def test_verb_map(self):
        assert _reconstruct_order("Ney", _order("", None, "move", "Vienna")) == \
            "Ney, move to Vienna"
        assert _reconstruct_order("Ney", _order("", None, "attack", "Mack")) == \
            "Ney, attack Mack"
        assert _reconstruct_order("Ney", _order("", None, "fortify", None)) == \
            "Ney, fortify"


# ════════════════════════════════════════════════════════════════════════
# Endpoint wiring (main.py /command) — full round trips
# ════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def endpoint():
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP
    from backend.models.world_state import WorldState

    original_parser = main_module.parser
    original_world = main_module.world
    original_game_state = main_module.game_state
    main_module.parser = _CP(use_real_llm=False)
    main_module.world = WorldState()
    main_module.world.actions_remaining = 30
    main_module.game_state = {"world": main_module.world}
    try:
        yield TestClient(main_module.app), main_module
    finally:
        main_module.parser = original_parser
        main_module.world = original_world
        main_module.game_state = original_game_state


class TestRecordingDecisions:
    def test_mock_mode_records_history(self, endpoint):
        # CR-4 decision: mock mode records too (was live-only).
        client, m = endpoint
        client.post("/command", json={"command": "Ney, scout Belgium"})
        assert len(m.world.command_history) >= 1
        entry = m.world.command_history[-1]
        assert entry["marshal"] == "Ney"
        assert entry["action"] == "scout"

    def test_target_is_recorded(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "Ney, scout Belgium"})
        assert m.world.command_history[-1]["target"] == "Belgium"


class TestAgainEndpoint:
    def test_again_repeats_resolved_command(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "Ney, scout Belgium"})
        data = client.post("/command", json={"command": "again"}).json()
        assert data["success"] is True
        # The resolved command was recorded, not the literal "again"
        assert m.world.command_history[-1]["raw_input"] == "Ney, scout Belgium"

    def test_again_empty_history_errors(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={"command": "again"}).json()
        assert data["success"] is False
        assert "repeat" in data["message"].lower()


class TestReferenceEndpoint:
    def test_him_end_to_end(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "Ney, attack Wellington"})
        client.post("/command", json={"command": "Davout, scout him"})
        # "him" resolved to Wellington and was recorded as the objective
        assert m.world.command_history[-1]["target"] == "Wellington"
        assert m.world.command_history[-1]["marshal"] == "Davout"

    def test_same_target_end_to_end(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "Ney, attack Wellington"})
        client.post("/command", json={"command": "Grouchy, scout the same target"})
        assert m.world.command_history[-1]["target"] == "Wellington"
        assert m.world.command_history[-1]["marshal"] == "Grouchy"

    def test_not_you_end_to_end(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "attack Wellington"})
        client.post("/command", json={"command": "not you, Davout"})
        last = m.world.command_history[-1]
        assert last["marshal"] == "Davout"
        assert last["target"] == "Wellington"


class TestFocusEndpoint:
    def test_bare_order_defaults_to_focus_marshal(self, endpoint):
        # Grouchy (disciplined) fortifies without objecting. The reissue is
        # recorded against Grouchy and the executor message names him — no
        # separate "Continuing with" note (the message is already explicit).
        client, m = endpoint
        client.post("/command", json={"command": "Grouchy, scout Belgium"})
        data = client.post("/command", json={"command": "fortify"}).json()
        assert data["success"] is True
        assert data.get("state") != "awaiting_clarification"
        assert "Grouchy" in data["message"]
        assert m.world.command_history[-1]["raw_input"] == "Grouchy, fortify"
        assert m.world.command_history[-1]["marshal"] == "Grouchy"

    def test_focus_reissues_even_when_marshal_objects(self, endpoint):
        # Ney (aggressive) may object to a bare "fortify" (mild or hard,
        # nondeterministic), but focus still reissued to him — it never
        # silently drops to a "which marshal?" question. Deterministic
        # regardless of the objection roll.
        client, m = endpoint
        client.post("/command", json={"command": "Ney, scout Belgium"})
        data = client.post("/command", json={"command": "fortify"}).json()
        assert data.get("state") != "awaiting_clarification"
        assert m.world.command_history[-1]["raw_input"] == "Ney, fortify"

    def test_no_focus_falls_through_to_clarification(self, endpoint):
        client, m = endpoint
        data = client.post("/command", json={"command": "fortify"}).json()
        # No prior addressed marshal → CR-2 clarification still fires
        assert data.get("state") == "awaiting_clarification"
        assert data.get("clarification_kind") == "marshal_choice"

    def test_focus_not_used_for_explicitly_addressed_order(self, endpoint):
        client, m = endpoint
        client.post("/command", json={"command": "Ney, scout Belgium"})
        data = client.post("/command", json={"command": "Grouchy, fortify"}).json()
        assert data["success"] is True
        assert m.world.command_history[-1]["marshal"] == "Grouchy"

    def test_collective_order_not_hijacked_by_focus(self, endpoint):
        # "all marshals fortify" is a multi-marshal intent — focus must NOT
        # collapse it to the single focus marshal (finding-3); it falls
        # through to the CR-2 clarification instead.
        client, m = endpoint
        client.post("/command", json={"command": "Ney, scout Belgium"})
        data = client.post("/command", json={"command": "all marshals fortify"}).json()
        assert data.get("state") == "awaiting_clarification"
        assert m.world.command_history[-1]["raw_input"] != "Ney, all marshals fortify"
