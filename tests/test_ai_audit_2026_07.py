"""
July 2026 AI-layer audit — regression pins for the fixed defects.

A 4-lens audit (enemy AI decision tree, AI diplomacy, LLM plumbing, turn
machinery) of the shipped 1805 campaign found 26 defects; the fixes landed
here are pinned below. Routed (NOT fixed) items live in ROADMAP.md §8.EVAL
(diplomacy balance triage) and COMMAND_ROBUSTNESS_SPEC.md CR-3 (LLM
modernization).
"""

from pathlib import Path

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)


def _fresh_1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _game_state(world):
    return {"world": world}


# ═══════════════════════════════════════════════════════════════════
# 1. AI-execution context: AI admin actions never touch player pools
# ═══════════════════════════════════════════════════════════════════

class TestAIAdminPoolIsolation:

    def test_ai_admin_phase_ignores_exhausted_player_pool(self):
        """AI builds were gated on AND consumed the PLAYER's admin AP —
        with the player's pool at 0, all 19 AI nations were locked out of
        build/repair every turn."""
        world = _fresh_1805()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        world.admin_actions_remaining = 0
        world.actions_remaining = 0
        world.nation_gold["Austria"] = 5000
        turn_before = world.current_turn

        results = ai.execute_admin_phase("Austria", world, _game_state(world))

        # The phase must not be blocked by the player's empty pools...
        for r in results:
            msg = (r.get("result") or {}).get("message", "")
            assert "No administrative actions remaining" not in msg, (
                f"AI admin action gated on the PLAYER's admin pool: {msg}")
        # ...must not consume them...
        assert world.admin_actions_remaining == 0
        assert world.actions_remaining == 0
        # ...and must NEVER auto-end the turn mid-enemy-phase (the
        # recursive end_turn double-advance)
        assert world.current_turn == turn_before

    def test_ai_admin_success_leaves_player_pool_untouched(self):
        world = _fresh_1805()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        world.admin_actions_remaining = 2
        world.nation_gold["Austria"] = 5000

        ai.execute_admin_phase("Austria", world, _game_state(world))

        assert world.admin_actions_remaining == 2, (
            "AI admin actions drained the player's admin AP pool")


# ═══════════════════════════════════════════════════════════════════
# 2. Autonomous marshals actually act
# ═══════════════════════════════════════════════════════════════════

class TestAutonomousExecution:

    def test_autonomous_marshal_executes_real_action(self):
        """The executor's 'cannot command autonomous marshal' gate bounced
        every AI-decided autonomous action — autonomy was a no-op."""
        world = _fresh_1805()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        ney = world.get_marshal("Ney")
        ney.autonomous = True
        ney.autonomy_turns = 3
        ap_before = (world.actions_remaining, world.admin_actions_remaining)

        outcome = ai.decide_single_action(ney, "France", world, _game_state(world))

        result = outcome.get("result") or {}
        assert "acting independently" not in result.get("message", ""), (
            "Autonomous action bounced off the autonomy gate")
        assert result.get("success") is True, result.get("message")
        # The marshal acts on his own initiative — never on the player's AP
        assert (world.actions_remaining, world.admin_actions_remaining) == ap_before


# ═══════════════════════════════════════════════════════════════════
# 3. C3 auto-advance guard absorbs, never soft-locks
# ═══════════════════════════════════════════════════════════════════

class TestC3GuardAbsorbs:

    def test_second_end_turn_after_auto_advance_advances(self):
        """The guard swallowed EVERY end-turn after an auto-advance until
        some other command cleared the flag — End Turn read as dead."""
        from backend.game_logic.turn_manager import TurnManager
        world = _fresh_1805()
        executor = CommandExecutor()
        tm = TurnManager(world, executor=executor)
        world._auto_advanced_to_turn = world.current_turn
        turn_now = world.current_turn

        first = tm.end_turn(_game_state(world))
        assert world.current_turn == turn_now, "first press should be absorbed"
        assert "already advanced" in first.get("message", "")

        tm.end_turn(_game_state(world))
        assert world.current_turn == turn_now + 1, (
            "second deliberate end-turn must advance the new turn")


# ═══════════════════════════════════════════════════════════════════
# 4. Hard-stop dialogues do not block the enemy phase
# ═══════════════════════════════════════════════════════════════════

class TestDialogueGateScopedToPlayer:

    def test_enemy_command_passes_hard_stop_gate(self):
        world = _fresh_1805()
        executor = CommandExecutor()
        world.dialogue_manager.push({
            "type": "commitment_paradox",
            "target_nation": "Austria",
            "options": [{"label": "Honor", "action": "honor"}],
        })
        assert world.dialogue_manager.is_hard_stop()

        result = executor.execute({
            "command": {"type": "specific", "marshal": "Mack",
                        "action": "wait", "target": None}
        }, _game_state(world))

        assert not result.get("awaiting_diplomatic_response"), (
            "AI command blocked by the player's hard-stop dialogue")


# ═══════════════════════════════════════════════════════════════════
# 5. P3.5 fortification opportunity respects war state + garrisons
# ═══════════════════════════════════════════════════════════════════

class TestFortificationOpportunityFilters:

    def test_no_unfortify_capture_against_peaceful_neighbor(self):
        """Bavaria's Deroy (fortified at Franconia) chased Hesse-held
        Frankfurt despite Bavaria being at peace with Hesse — permanent
        fortify/unfortify oscillation on peace-heavy 1805 fronts."""
        world = _fresh_1805()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        deroy = world.get_marshal("Deroy")
        deroy.fortified = True
        assert not world.is_at_war("Bavaria", "Hesse")

        action = ai._check_fortification_opportunity(deroy, "Bavaria", world)

        if action is not None:
            assert ai._pending_intents.get("Deroy", {}).get("target") != "Frankfurt"
        assert not (action and action.get("action") == "unfortify"
                    and ai._pending_intents.get("Deroy", {}).get("intent") == "capture"
                    and not world.is_at_war(
                        "Bavaria",
                        world.get_region(ai._pending_intents["Deroy"]["target"]).controller))


# ═══════════════════════════════════════════════════════════════════
# 6. Pending capture intent: fortified marshal unfortifies first
# ═══════════════════════════════════════════════════════════════════

class TestIntentFortifiedGuard:

    def test_fortified_marshal_unfortifies_before_intent_attack(self):
        """The intent path emitted attack-while-fortified, which the
        executor rejected — then _record_failed_action banned the marshal
        from attacking for 2 turns."""
        world = _fresh_1805()
        executor = CommandExecutor()
        ai = EnemyAI(executor)
        mack = world.get_marshal("Mack")
        mack.fortified = True
        # Bavaria-controlled, Austria at war with Bavaria, undefended
        target = "Munich"
        region = world.get_region(target)
        region.controller = "Bavaria"
        region.garrison_strength = 0
        assert world.is_at_war("Austria", "Bavaria")
        ai._pending_intents["Mack"] = {"intent": "capture", "target": target}

        ai._enter_indexed_evaluation_scope(world)
        try:
            action, priority = ai._evaluate_marshal(mack, "Austria", world)
        finally:
            ai._exit_indexed_evaluation_scope()

        assert action is not None
        assert action.get("action") == "unfortify", (
            f"fortified marshal must unfortify before the capture, got {action}")
        # Intent survives for the follow-through
        assert ai._pending_intents.get("Mack", {}).get("target") == target


# ═══════════════════════════════════════════════════════════════════
# 7. Attribute fixes: personality threshold + income_value
# ═══════════════════════════════════════════════════════════════════

class TestAttributeFixes:

    def test_no_personality_type_reads_remain(self):
        source = Path("backend/ai/enemy_ai.py").read_text(encoding="utf-8")
        assert "'personality_type'" not in source.replace('"personality_type"', "'personality_type'"), (
            "marshal.personality_type does not exist — use marshal.personality")

    def test_no_bare_region_income_reads_remain(self):
        source = Path("backend/ai/enemy_ai.py").read_text(encoding="utf-8")
        assert "adj_region.income if" not in source, (
            "Region has income_value, not income (CLAUDE.md attribute trap)")


# ═══════════════════════════════════════════════════════════════════
# 8. AI-AI diplomacy acceptance evaluates the real pair
# ═══════════════════════════════════════════════════════════════════

class TestAIAIAcceptancePair:

    def test_initiator_side_never_self_pairs(self, monkeypatch):
        """The initiator-side check evaluated (initiator vs itself) — the
        whole AI-AI treaty phase was dead (nothing ever scored >= 50)."""
        import backend.game_logic.ai_diplomacy as ai_diplomacy
        world = _fresh_1805()
        captured = {}

        def fake_calculate_acceptance(proposal, w):
            captured.update(proposal)
            return {"score": 0}

        monkeypatch.setattr(ai_diplomacy, "calculate_acceptance",
                            fake_calculate_acceptance)
        proposal = {"type": "non_aggression", "proposer": "Prussia",
                    "target": "Saxony"}
        ai_diplomacy._ai_ai_acceptance(proposal, "Prussia", "Saxony", world)

        assert captured["target_nation"] == "Prussia"
        assert captured["proposer_nation"] == "Saxony", (
            "initiator-side acceptance must evaluate the COUNTERPARTY as "
            "proposer, never a self-pair")


# ═══════════════════════════════════════════════════════════════════
# 9. LLM plumbing: validation + target sets + repetition history
# ═══════════════════════════════════════════════════════════════════

class TestLLMPlumbing:

    def test_null_action_rejected_by_validation(self):
        from backend.ai.schemas import ParseResult
        from backend.ai.validation import validate_parse_result
        result = ParseResult(matched=True, action=None)
        validated = validate_parse_result(result, ["Ney"], ["Paris"], ["Paris"])
        assert validated.matched is False, (
            "a live-LLM 'action': null must not pass the anti-hallucination layer")

    def test_valid_targets_include_friendly_marshals_and_generic(self):
        from backend.ai.llm_client import LLMClient
        client = LLMClient(use_real_api=False)
        gs = {"marshals": {"Ney": {}, "Soult": {}},
              "enemies": {"Mack": {}},
              "map_data": {"Paris": {}}}
        targets = client._extract_valid_targets(gs)
        assert "Ney" in targets and "Soult" in targets, (
            "the prompt mandates friendly-marshal SUPPORT targets — "
            "validation must not clear them")
        assert "generic" in targets

    def test_llm_game_state_carries_world_for_repetition_history(self):
        """Providers read game_state['world'] for the command-history
        repetition guardrail — it was silently absent, so the designed
        anti-spam on strategic-score bonuses never engaged in live mode."""
        from backend.ai.parser_eval import build_llm_game_state
        world = _fresh_1805()
        gs = build_llm_game_state(world)
        assert gs.get("world") is world


# ═══════════════════════════════════════════════════════════════════
# 10. M3 counter-offers never promise inert territory
# ═══════════════════════════════════════════════════════════════════

class TestNoPhantomTerritorySweetener:

    def test_territory_not_in_offerable_sweetener_branch(self):
        """Source pin: the M3 sweetener branch must not offer 'territory'
        until region selection + ratification wiring exists (8.EVAL row)."""
        source = Path("backend/game_logic/ai_diplomacy.py").read_text(encoding="utf-8")
        assert 'if dtype in ("gold_lump", "gold_per_turn", "territory")' not in source
