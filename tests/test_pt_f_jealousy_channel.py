"""Row PT, slice F — the jealousy channel finishes.

Build spec: `docs/PLAYTEST_FIXES_SPEC.md` §2 PT-F.

* **F1** the autonomous attack is a rumour — the marquee payoff of the
  whole system lands as one sentence and no battle.
* **F2** an unopposed capture never clears `idle_turns`.
* **F3** the rivalry arms are priced like their siblings.
* **F5** "any command would restrain him" — three arms that do not.
* **F6** the trust warning advises an unreachable lever.
* **F7** a ladder shift is narrated twice.
* **F8** "he has not seen laurels" is asserted without reading his glory.
* **F9** the jealousy attack silently deletes the standing order.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from backend.game_logic import jealousy as J

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"
MAIN_GD = (SCRIPTS / "main.gd").read_text(encoding="utf-8")


@pytest.fixture()
def board():
    # Rhineland, NOT Belgium: Belgium adjoins Paris, so an enemy standing
    # there makes `is_capital_threatened` true and
    # `process_autonomous_attacks` returns [] before it does anything —
    # the fixture would have pinned nothing.
    ney = MarshalFactory.infantry(name="Ney", location="Rhineland",
                                  strength=25000, personality="aggressive")
    murat = MarshalFactory.infantry(name="Murat", location="Lyon",
                                    strength=21000, personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Rhineland",
                                nation="Austria", strength=12000,
                                personality="cautious")
    world = WorldFactory.with_marshals([ney, murat, mack])
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    world.calculate_visibility()
    world.actions_remaining = 4
    return world


# ═══════════════════════════════════════════════════════════════════════
# F1 — the attack reaches the player as a battle
# ═══════════════════════════════════════════════════════════════════════

class TestTheAutonomousAttackIsShown:
    def test_the_results_are_carried_not_dropped(self):
        """`jealousy_attack_results` was a dead local — grep-verified, no
        reader anywhere in the backend or the client."""
        src = (REPO / "backend" / "game_logic"
               / "turn_manager.py").read_text(encoding="utf-8")
        assert 'result["jealousy_attacks"] = _autonomous' in src

    def test_new_state_is_stripped(self):
        """The standing serialization rule — the executor result carries a
        WorldState with circular refs."""
        src = (REPO / "backend" / "game_logic"
               / "turn_manager.py").read_text(encoding="utf-8")
        block = src.split("if jealousy_attack_results:")[1].split(
            "if all_events:")[0]
        assert 'key != "new_state"' in block

    def test_the_endpoint_passes_it_through(self):
        src = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert 'response["jealousy_attacks"] = result["jealousy_attacks"]' in src

    def test_the_client_renders_it_through_the_battle_chokepoint(self):
        """`_display_battle_result` is where the "⚔ View the field" link
        and the diorama stash live, structurally inseparable since BD
        §14.1 — so routing through it is what gives the beat a picture."""
        assert "func _display_jealousy_attacks" in MAIN_GD
        body = MAIN_GD.split("func _display_jealousy_attacks")[1].split(
            "\nfunc ")[0]
        assert "_display_battle_result(" in body
        assert "_display_berthier_report(" in body

    def test_it_is_called_before_the_enemy_phase(self):
        """The order they were fought in: the marshal goes, then the enemy
        answers."""
        head = MAIN_GD.split("_display_jealousy_attacks(response)")[1]
        assert head.lstrip().startswith("\n\t\tif response.has(\"enemy_phase\")") \
            or 'if response.has("enemy_phase")' in head[:200]


# ═══════════════════════════════════════════════════════════════════════
# F9 — and it says what it voided
# ═══════════════════════════════════════════════════════════════════════

class TestTheVoidedOrderIsAnnounced:
    def test_the_order_clear_is_reported(self, board):
        """CA9-F13's own comment states the rule — "a standing order died
        here SILENTLY… Say what was voided, and by what" — and applied it
        to the reinforcement seam only, while the row it was filed against
        names the jealousy autonomous attack in its one-liner."""
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import StrategicOrder

        ney = board.marshals["Ney"]
        ney.jealous_of = "Murat"
        ney.jealousy_autonomous_warned = True
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Rhineland",
            target_type="region", started_turn=board.current_turn,
            original_command="Ney, move to Rhineland")
        executor = CommandExecutor()
        random.seed(5)
        J.process_autonomous_attacks(
            board, executor, {"world": board, "executor": executor})
        voided = [e for e in J._pending_events(board)
                  if e.get("type") == "order_voided_by_battle"]
        assert voided, "the player's plan must not vanish in silence"
        assert "Rhineland" in voided[0]["message"]
        assert voided[0]["marshal"] == "Ney"

    def test_no_event_when_there_was_no_order(self, board):
        from backend.commands.executor import CommandExecutor

        ney = board.marshals["Ney"]
        ney.jealous_of = "Murat"
        ney.jealousy_autonomous_warned = True
        ney.strategic_order = None
        executor = CommandExecutor()
        random.seed(5)
        J.process_autonomous_attacks(
            board, executor, {"world": board, "executor": executor})
        assert not [e for e in J._pending_events(board)
                    if e.get("type") == "order_voided_by_battle"]


# ═══════════════════════════════════════════════════════════════════════
# F2 — taking a province is not idling
# ═══════════════════════════════════════════════════════════════════════

class TestAnUnopposedCaptureIsNotIdling:
    def test_the_capture_arm_clears_the_counter(self):
        src = (REPO / "backend" / "commands"
               / "combat_executor.py").read_text(encoding="utf-8")
        block = src.split("# Move attacker to captured region")[1].split(
            "# Attempt capture")[0]
        assert "marshal.idle_turns = 0" in block
        assert "marshal.acted_this_turn = True" in block

    def test_the_inert_pin_was_replaced_not_extended(self):
        """⚠ The spec names this one: `test_idle_turns_reset_on_attack`
        hand-assigned `idle_turns = 0` under a comment reading "# Simulate
        what executor does after attack" and never called the executor.
        It could not fail unless Python's assignment broke."""
        src = (REPO / "tests" / "test_objection_v2.py").read_text(
            encoding="utf-8")
        assert "# Simulate what executor does after attack" not in src


# ═══════════════════════════════════════════════════════════════════════
# F3 — the rivalry arms state their terms
# ═══════════════════════════════════════════════════════════════════════

def _rivalry(world, new_value, authority=None, personality="aggressive"):
    world.marshals["Ney"].personality = personality
    if authority is not None:
        world.authority_tracker.authority = authority
    J.queue_rivalry_petition(world, world.marshals["Ney"],
                             world.marshals["Murat"], new_value)
    petition = world.pending_marshal_petition
    return {o["id"]: o for o in petition["options"]}


class TestTheRivalryArmsArePriced:
    def test_let_be_states_the_personality_band(self, board):
        aggressive = _rivalry(board, -1, personality="aggressive")
        assert "40%" in aggressive["let_be"]["detail"]
        board.pending_marshal_petition = None
        cautious = _rivalry(board, -1, personality="cautious")
        assert "80%" in cautious["let_be"]["detail"]

    def test_mediate_states_the_authority_band_and_the_failure_cost(self,
                                                                    board):
        low = _rivalry(board, -1, authority=20)
        assert "20%" in low["mediate"]["detail"]
        assert "authority" in low["mediate"]["detail"]

    def test_reprimand_discloses_the_extra_five(self, board):
        arms = _rivalry(board, -1)
        assert "-5 trust" in arms["reprimand"]["detail"]

    def test_accept_breach_says_it_unlocks_defiance(self, board):
        arms = _rivalry(board, -2)
        assert "20%" in arms["accept_breach"]["detail"]
        assert "defiance" in arms["accept_breach"]["detail"]

    def test_force_reconciliation_states_the_band_and_the_partial_thaw(
            self, board):
        arms = _rivalry(board, -2, authority=85)
        assert "50%" in arms["force_reconciliation"]["detail"]
        assert "rivalry" in arms["force_reconciliation"]["detail"], (
            "success is `_restore(-1)` — a thaw to rivalry, never to "
            "friendly, and the copy never said so")

    def test_separate_is_untouched(self, board):
        """The one arm whose copy already matched its effect exactly."""
        arms = _rivalry(board, -2)
        assert "Not a fix" in arms["separate"]["detail"]


# ═══════════════════════════════════════════════════════════════════════
# F5 / F6 / F7 / F8 — the honesty rows
# ═══════════════════════════════════════════════════════════════════════

class TestTheStandDownReachesHim:
    def test_an_objected_order_still_stands_him_down(self):
        """The `pending_objection` exclusion meant the marshal most likely
        to be warned — aggressive, jealous, and so the likeliest to object
        — was the one the stand-down could not reach."""
        src = (REPO / "backend" / "commands" / "executor.py").read_text(
            encoding="utf-8")
        block = src.split("PT-F5")[1].split("_warned_marshal = ")[0]
        assert 'result.get("pending_objection")' in block
        assert 'not result.get("pending_objection")' not in block

    def test_answering_the_objection_stands_him_down(self):
        """`_execute_post_objection` calls the sub-executors directly and
        never re-enters `execute()`, where the hook lives.

        Bounded to the block that follows that call — the first draft
        grepped the whole module and the sweep walked through it, because
        replacing the call's RESULT with None leaves the import behind.
        """
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        block = src.split(
            "execution_result = self._execute_post_objection("
            "parsed_command, game_state, marshal_name)")[-1].split(
                "if execution_result.get(\"success\"):")[0]
        assert "cancel_autonomous_warning_on_order(world, _warned)" in block

    def test_the_promise_no_longer_says_any_command(self):
        """A REFUSED order never reached him, so it still does not count —
        and the warning stops claiming otherwise."""
        src = (REPO / "backend" / "game_logic" / "jealousy.py").read_text(
            encoding="utf-8")
        assert "any command would restrain him" not in src


class TestTheTrustWarningNamesARealLever:
    def test_it_no_longer_advises_independence(self):
        """`grant_autonomy` is reachable only from the redemption event at
        trust <= 20, and `change_autonomy` is the VASSAL verb. Between 39
        and 21 the advice named an action the player could not take."""
        src = (REPO / "backend" / "models" / "world_state.py").read_text(
            encoding="utf-8")
        block = src.split("trust is faltering")[1].split("})")[0]
        assert "more independence" not in block

    def test_the_warning_still_fires(self):
        world = WorldFactory.basic()
        marshal = next(m for m in world.marshals.values()
                       if m.nation == world.player_nation)
        marshal.trust.set(35)
        marshal.trust_warning_shown = False
        warnings = world._check_trust_warnings()
        mine = [w for w in warnings if w["marshal"] == marshal.name]
        assert mine and "faltering" in mine[0]["message"]
        assert "20" in mine[0]["message"], (
            "and it names the threshold where a real lever appears")


class TestTheLadderShiftIsNarratedOnce:
    def test_the_duplicate_type_is_retired(self):
        from backend.game_logic.dispatch import _DISPATCH_EVENT_TYPES

        assert "jealousy_ladder_shift" not in _DISPATCH_EVENT_TYPES

    def test_the_surviving_beat_carries_the_cause(self, board):
        ney = board.marshals["Ney"]
        ney.jealous_of = "Murat"
        ney.jealousy_turns_remaining = 3
        J._append_glory(ney, board.current_turn, 5)
        board._jealousy_processed_turn = None
        events = J.process_turn(board)
        resolved = [e for e in events if e.get("type") == "jealousy_resolved"]
        assert len(resolved) == 1
        assert "surpassed Murat" in resolved[0]["message"]
        assert not [e for e in events
                    if e.get("type") == "jealousy_ladder_shift"]


class TestTheRestlessnessClauseReadsHisOwnGlory:
    def test_a_marshal_with_laurels_is_not_told_he_has_none(self):
        """The subject's glory entered the beat ONLY as a subtrahend. A
        marshal with points in the window and a target above him satisfies
        the gate exactly, and Berthier said "he has not seen laurels" of a
        man who had."""
        src = (REPO / "backend" / "game_logic" / "jealousy.py").read_text(
            encoding="utf-8")
        block = src.split("PT-F8")[1].split("warned += 1")[0]
        assert "_own_glory" in block
        assert "has not seen laurels" in block
        assert "counted smaller" in block

    def test_the_refuted_half_was_not_built(self):
        """⚠ The audit's first wording — "names a comparator who is not
        winning" — is REFUTED: `find_jealousy_target` draws only from
        peers strictly above on the ladder."""
        src = (REPO / "backend" / "game_logic" / "jealousy.py").read_text(
            encoding="utf-8")
        block = src.split("PT-F8")[1].split("warned += 1")[0]
        assert "{target.name} wins them" in block


# ═══════════════════════════════════════════════════════════════════════
# THE REVIEW-FLEET ROUND: the seams the first cut's pins did not bind
# ═══════════════════════════════════════════════════════════════════════

class TestF1ActuallyReachesTheClient:
    """PT-F1 shipped PRODUCTION-DEAD and five green pins did not notice.

    The producer, the forwarder and the renderer were each asserted as
    SOURCE TEXT, in three separate files, and nothing exercised the joint
    — `_execute_end_turn` builds a FRESH result dict and hand-copies a
    fixed key set, of which `jealousy_attacks` was not one. This drives a
    real end turn instead.
    """

    def test_the_payload_survives_the_executor_seam(self, board, monkeypatch):
        from backend.commands.executor import CommandExecutor

        executor = CommandExecutor()
        sentinel = [{"jealousy_autonomous": "Ney",
                     "message": "Ney went in without orders.",
                     "battle_report": {"observation": "SENTINEL"},
                     "events": [{"type": "battle"}],
                     "new_state": object()}]
        monkeypatch.setattr(
            "backend.game_logic.jealousy.process_autonomous_attacks",
            lambda *_a, **_k: [dict(s) for s in sentinel])
        result = executor._meta._execute_end_turn(
            {"action": "end_turn"}, {"world": board, "executor": executor})
        assert "jealousy_attacks" in result, (
            "the end-turn executor must forward it — it builds a fresh "
            "dict and copies a fixed key set")
        assert result["jealousy_attacks"][0]["battle_report"][
            "observation"] == "SENTINEL"
        assert "new_state" not in result["jealousy_attacks"][0]

    def test_the_auto_advance_mirror_forwards_it_too(self):
        """A player whose last AP ends the turn takes the other path."""
        src = (REPO / "backend" / "commands" / "executor.py").read_text(
            encoding="utf-8")
        assert 'result["jealousy_attacks"] = turn_result["jealousy_attacks"]' in src


class TestTheVoidedOrderLineIsHumanized:
    def test_it_does_not_emit_raw_keys(self, board):
        from backend.commands.executor import CommandExecutor
        from backend.models.marshal import StrategicOrder

        ney = board.marshals["Ney"]
        ney.jealous_of = "Murat"
        ney.jealousy_autonomous_warned = True
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="ArchdukeCharles",
            target_type="marshal", started_turn=board.current_turn,
            original_command="x")
        executor = CommandExecutor()
        random.seed(5)
        J.process_autonomous_attacks(
            board, executor, {"world": board, "executor": executor})
        voided = [e for e in J._pending_events(board)
                  if e.get("type") == "order_voided_by_battle"]
        assert voided
        message = voided[0]["message"]
        assert "move_to" not in message
        assert "ArchdukeCharles" not in message
        assert "Archduke Charles" in message
