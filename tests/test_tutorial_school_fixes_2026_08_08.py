"""Aug 8, 2026 tutorial live report, second wave (TUT-F4/F5 + the Acknowledge
legibility fix) — the user drove The School of War and filed three reports:

1. Step IX (Conquest) would not clear. Reproduced: the Austrian reserve's only
   westward road runs THROUGH Bohemia (it adjoins both Vienna and Hungary), so
   a lesson run a turn or two slow meets 20k+ Austrians parked on the step's
   target — and the card's own recovery ("attack that name") was then EATEN by
   a stale cannon_fire interrupt: the refused move cancelled Davout's standing
   order but left the order's interrupt on him, and main.py's interrupt route
   consumed the next command as its answer ("Davout has no active strategic
   order"). TUT-F4a: an order-bound interrupt dies WITH its order at the
   executor's override-cancel; standalone decisions survive.
   TUT-F4c (client): the card re-renders on turn change and an overdue event
   step SAYS the school will move on (the catch-up already guaranteed it).
2. "A general is in the way" on the Ney→Swabia beat — working as designed
   (armies bar moves; attack clears them), now stated on the VII card.
3. Grievance popups "happen a lot" and Acknowledge is opaque. Measured: five
   Soult confrontations in three lesson turns. TUT-F5: the lesson world is
   jealousy-dormant (no fires, no petitions of any kind — glory still
   accrues); and the Acknowledge arm now states its terms (free, no effect,
   the grievance's remaining turns and its standing cost) in the main game.
"""

from pathlib import Path
from unittest.mock import patch

from backend.commands.executor import CommandExecutor
from backend.commands.movement_executor import MovementExecutor
from backend.commands.objection_v2 import ConcernLevel
from backend.commands.strategic import ORDER_BOUND_INTERRUPT_TYPES
from backend.game_logic import jealousy
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState
from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
TUTORIAL_JSON = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "tutorial_1805.json")
OVERLAY = (REPO / "godot-client" / "project-sovereign" / "scripts"
           / "tutorial_overlay.gd")


def _order(target: str = "Belgium") -> StrategicOrder:
    return StrategicOrder(
        command_type="MOVE_TO", target=target, target_type="region",
        started_turn=1, original_command="march to " + target,
        path=[target], issued_turn=0,
    )


def _french_pair():
    ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                  personality="aggressive", nation="France")
    davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                     personality="cautious", nation="France")
    world = WorldFactory.with_marshals([ney, davout])
    world.actions_remaining = 4
    return world, ney, davout


# ═══════════════════════════════════════════════════════════════════════════
# TUT-F4a — the stale order-bound interrupt
# ═══════════════════════════════════════════════════════════════════════════


class TestOrderBoundInterruptClearedOnOverride:
    def test_constant_contents(self):
        """The split is the fix: order-raised questions die with the order;
        standalone decisions (a cornered last stand, an unconfirmed muster)
        are never silently dropped — main.py's addressed-other guard says
        dropping those strands the marshal."""
        assert ORDER_BOUND_INTERRUPT_TYPES == {
            "contact", "contact_bad_odds", "cannon_fire",
            "destination_blocked", "combat_stalemate",
        }
        assert "last_stand" not in ORDER_BOUND_INTERRUPT_TYPES
        assert "muster_confirm" not in ORDER_BOUND_INTERRUPT_TYPES

    def test_override_cancel_clears_order_bound_interrupt(self):
        """The live shape: a player move to the interrupted marshal cancels
        his standing order — the order's cannon_fire question must go WITH
        it, or the next command naming him is consumed as its answer."""
        world, ney, _ = _french_pair()
        ney.strategic_order = _order()
        ney.pending_interrupt = {
            "interrupt_type": "cannon_fire", "marshal": "Ney",
            "options": ["investigate", "continue"],
        }
        CommandExecutor().execute(
            {"command": {"marshal": "Ney", "action": "move",
                         "target": "Belgium"}},
            {"world": world})
        assert ney.strategic_order is None
        assert ney.pending_interrupt is None, (
            "the stale order-bound interrupt survived the override-cancel — "
            "it will eat the player's next command for this marshal")

    def test_override_cancel_preserves_last_stand_decision(self):
        """A cornered marshal's last-stand question is NOT order-bound: it
        must survive the override (dropping it strands him).

        Flipped consciously by FA slice 2 (Sept 4, 2026 — FA-16). This pin
        used to assert that the override EXECUTED and cancelled the standing
        order while the question survived. Measured, "executed" meant the
        cornered marshal was marched away with his question still parked —
        and a fresh strategic order's own contact question could OVERWRITE
        it. The rule now is that no order reaches a cornered marshal until
        his question is answered: the move is REFUSED at zero cost, the
        refusal names the two answers, and both the decision and the
        standing order (which cannot progress while the ask stands) are left
        exactly as they were."""
        world, ney, _ = _french_pair()
        ney.strategic_order = _order()
        pending = {
            "interrupt_type": "last_stand", "marshal": "Ney",
            "options": ["fight", "surrender"],
        }
        ney.pending_interrupt = pending
        result = CommandExecutor().execute(
            {"command": {"marshal": "Ney", "action": "move",
                         "target": "Belgium"}},
            {"world": world})
        assert result.get("success") is False
        assert result.get("last_stand_pending") is True
        assert "fight to the last" in result.get("message", "")
        assert "attempt a breakout" in result.get("message", "")
        assert ney.strategic_order is not None, "the order is untouched"
        assert ney.pending_interrupt == pending, "the decision survives"
        assert ney.location == "Paris", "he did not march"

    def test_refused_move_still_clears_the_interrupt(self):
        """The probe's exact shape: the move is REFUSED (enemy in the target)
        yet the order is cancelled — the interrupt must not outlive it."""
        world, ney, _ = _french_pair()
        enemy = MarshalFactory.infantry(name="Blocker", location="Normandy",
                                        personality="cautious",
                                        nation="Britain")
        world.marshals["Blocker"] = enemy
        ney.strategic_order = _order("Normandy")
        ney.pending_interrupt = {
            "interrupt_type": "destination_blocked", "marshal": "Ney",
            "options": ["attack", "wait"],
        }
        result = CommandExecutor().execute(
            {"command": {"marshal": "Ney", "action": "move",
                         "target": "Normandy"}},
            {"world": world})
        assert result.get("success") is False
        assert ney.strategic_order is None
        assert ney.pending_interrupt is None


# ═══════════════════════════════════════════════════════════════════════════
# TUT-F5 — the lesson world is jealousy-dormant
# ═══════════════════════════════════════════════════════════════════════════


class TestTutorialJealousyDormant:
    def test_predicate_is_the_tut_f2_discriminator(self):
        tutorial = WorldState.from_scenario(str(TUTORIAL_JSON))
        campaign = WorldState(player_nation="France")
        assert jealousy.jealousy_dormant(tutorial) is True
        assert jealousy.jealousy_dormant(campaign) is False

    def test_apply_jealousy_never_fires_on_the_lesson_world(self):
        world = WorldState.from_scenario(str(TUTORIAL_JSON))
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        events = []
        jealousy.apply_jealousy(world, ney, davout, delta=10, threshold=5,
                                events=events)
        assert not ney.jealous_of
        assert events == []
        assert world.pending_marshal_petition is None
        assert not getattr(world, "jealousy_confrontations_seen", [])

    def test_push_petition_dropped_for_every_kind_on_the_lesson_world(self):
        world = WorldState.from_scenario(str(TUTORIAL_JSON))
        for kind in ("jealousy_confrontation", "rivalry_confrontation",
                     "fontainebleau", "war_weary"):
            jealousy._push_petition(world, {"kind": kind, "options": []})
            assert world.pending_marshal_petition is None, kind

    def test_campaign_world_still_fires_and_petitions(self):
        """The control arm: outside the schoolroom nothing changed — the
        grievance sets, the dispatch line lands, the confrontation queues."""
        world, ney, davout = _french_pair()
        events = []
        jealousy.apply_jealousy(world, ney, davout, delta=10, threshold=5,
                                events=events)
        assert ney.jealous_of == "Davout"
        assert any(e.get("type") == "jealousy_fired" for e in events)
        petition = world.pending_marshal_petition
        assert petition is not None
        assert petition["kind"] == "jealousy_confrontation"


# ═══════════════════════════════════════════════════════════════════════════
# Acknowledge states its terms (main game)
# ═══════════════════════════════════════════════════════════════════════════


class TestAcknowledgeDetailStatesTerms:
    def _petition_with_remaining(self, turns: int):
        world, ney, davout = _french_pair()
        ney.jealousy_turns_remaining = turns
        jealousy.queue_confrontation_petition(world, ney, davout, 0)
        petition = world.pending_marshal_petition
        assert petition is not None
        by_id = {o["id"]: o for o in petition["options"]}
        return by_id

    def test_acknowledge_names_cost_effect_duration_and_stakes(self):
        """CONSCIOUS PIN FLIP (CA9 row 3 §3, Aug 9 2026).

        This asserted the word "coordination", and that abstraction was the
        problem: the audit's finding was that "souring his ties and
        coordination" is not a decision, while "he brings NONE of his 30,000
        men to any battle Davout leads" is. The arm is also renamed to
        "Let it stand" — `Acknowledge` is the DISMISS verb everywhere else in
        the client, which framed the whole card as an inbox receipt. The
        option ID is unchanged because it is the POST value.

        The contract asserted is now stronger, not weaker: the cost must be
        stated in MEN, and the number must be the marshal's real strength.
        """
        world, ney, davout = _french_pair()
        ney.jealousy_turns_remaining = 3
        jealousy.queue_confrontation_petition(world, ney, davout, 0)
        by_id = {o["id"]: o for o in world.pending_marshal_petition["options"]}
        arm = by_id["acknowledge"]
        assert arm["label"] == "Let it stand"
        detail = arm["detail"]
        assert "Free, and it fixes nothing" in detail
        assert "3 more turns" in detail
        assert "Davout" in detail
        assert f"{int(ney.strength):,}" in detail, (
            "the cost must be stated in men, not in adjectives")
        assert "harden" in detail

    def test_singular_turn_reads_singular(self):
        detail = self._petition_with_remaining(1)["acknowledge"]["detail"]
        assert "1 more turn " in detail
        assert "1 more turns" not in detail

    def test_priced_arms_still_state_their_terms(self):
        by_id = self._petition_with_remaining(3)
        assert str(jealousy.CONFRONT_PROMISE_DURATION_CUT) \
            in by_id["promise"]["detail"]
        assert str(jealousy.CONFRONT_REBUKE_TRUST) in by_id["rebuke"]["detail"]


# ═══════════════════════════════════════════════════════════════════════════
# TUT-F4c + copy — client structural pins (the .gd asserted as text, the
# test_tutorial_position7 idiom)
# ═══════════════════════════════════════════════════════════════════════════


class TestOverlayLivenessPins:
    def _overlay(self) -> str:
        return OVERLAY.read_text(encoding="utf-8")

    def test_rerender_on_turn_change(self):
        overlay = self._overlay()
        assert overlay.count("_last_rendered_turn") >= 3, (
            "declaration + observe comparison + render stamp")
        assert "_turn != _last_rendered_turn" in overlay
        # The stamp lives in _render so every render path resets it.
        render_body = overlay.split("func _render(")[1].split("\nfunc ")[0]
        assert "_last_rendered_turn = _turn" in render_body

    def test_overdue_line_exists_and_skips_self_releasing_steps(self):
        overlay = self._overlay()
        assert "The war has outrun this page" in overlay
        render_body = overlay.split("func _render(")[1].split("\nfunc ")[0]
        assert 'begins_with("_pred_turn_gte")' in render_body
        assert '"_pred_never"' in render_body

    def test_step_vii_teaches_strike_again(self):
        assert "strike again before you walk in" in self._overlay()

    def test_step_ix_offers_the_alternate_and_drops_the_position_claim(self):
        overlay = self._overlay()
        assert "the battered Tyrol will do" in overlay
        assert "and Davout stands at its border" not in overlay, (
            "the card asserted a position the standing order cannot promise "
            "(an enemy-held Franconia re-routes him through Munich, which "
            "does not border Bohemia)")

    def test_suggest_chips_unchanged(self):
        """The T-B1 mock-parse harness re-checks every pair; here just pin
        that the two touched steps kept their chips verbatim."""
        overlay = self._overlay()
        assert '"suggest": "Davout, move to Bohemia"' in overlay
        assert '"suggest": "Ney, attack Kienmayer"' in overlay


# ═══════════════════════════════════════════════════════════════════════════
# TUT-F6 — a marshal never objects to a command that is about to be refused
# ("sometimes the general objects even if the command cant be executed").
# The forced-MODERATE patch makes each arm falsifiable: without the
# suppression, evaluate_situation runs and raises the popup; with it, the
# probe short-circuits and the canonical refusal surfaces immediately.
# ═══════════════════════════════════════════════════════════════════════════


class TestObjectionNeverPrecedesRefusal:
    def _forced_moderate(self):
        return patch("backend.commands.executor.evaluate_situation",
                     return_value=ConcernLevel.MODERATE)

    def test_engaged_distant_march_refuses_without_objection(self):
        """The tutorial's live shape: engaged Davout ordered on a distant
        march — pre-fix, the objection modal fired and INSIST then hit
        'cannot begin a strategic march'."""
        world, ney, _ = _french_pair()
        enemy = MarshalFactory.infantry(name="Wellington", location="Paris",
                                        personality="cautious",
                                        nation="Britain")
        world.marshals["Wellington"] = enemy
        # Friendly distant target: with a non-friendly one the earlier
        # "cannot advance while engaged" arm answers instead — also a
        # refusal-without-objection, but this test pins the R5 arm the
        # tutorial hit.
        world.get_region("Netherlands").controller = "France"
        with self._forced_moderate() as evaluate:
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "move",
                             "target": "Netherlands"}},
                {"world": world})
        evaluate.assert_not_called()
        assert result["success"] is False
        assert "strategic march" in result["message"]
        assert world.pending_objection is None

    def test_no_ap_distant_march_refuses_without_objection(self):
        world, ney, _ = _french_pair()
        world.actions_remaining = 1
        with self._forced_moderate() as evaluate:
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "move",
                             "target": "Netherlands"}},
                {"world": world})
        evaluate.assert_not_called()
        assert result["success"] is False
        assert "Not enough actions for a strategic march" in result["message"]
        assert world.pending_objection is None

    def test_move_into_visible_enemy_refuses_without_objection(self):
        world, ney, _ = _french_pair()
        enemy = MarshalFactory.infantry(name="Wellington",
                                        location="Normandy",
                                        personality="cautious",
                                        nation="Britain")
        world.marshals["Wellington"] = enemy
        with self._forced_moderate() as evaluate:
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "move",
                             "target": "Normandy"}},
                {"world": world})
        evaluate.assert_not_called()
        assert result["success"] is False
        assert "enemy forces present" in result["message"]
        assert world.pending_objection is None

    def test_executable_move_still_reaches_objection_evaluation(self):
        """Control: the suppression must never over-fire — a clean move
        still consults the objection system."""
        world, ney, _ = _french_pair()
        with patch("backend.commands.executor.evaluate_situation",
                   return_value=ConcernLevel.NONE) as evaluate:
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "move",
                             "target": "Normandy"}},
                {"world": world})
        evaluate.assert_called_once()
        assert result["success"] is True

    def test_probe_is_a_pure_read(self):
        world, ney, _ = _french_pair()
        enemy = MarshalFactory.infantry(name="Wellington",
                                        location="Normandy",
                                        personality="cautious",
                                        nation="Britain")
        world.marshals["Wellington"] = enemy
        ap_before = world.actions_remaining
        refusal = MovementExecutor.move_refusal_probe(
            world, ney, world.get_region("Normandy"), "Normandy")
        assert refusal is not None
        assert ney.location == "Paris"
        assert world.actions_remaining == ap_before

    def test_covered_water_attack_refuses_without_objection(self):
        """TUT-F6b: an in-range attack across a SHUT crossing — the naval
        refusal comes from the combat seam; no bad-odds objection first."""
        world, ney, _ = _french_pair()
        enemy = MarshalFactory.infantry(name="Wellington",
                                        location="Normandy", strength=90000,
                                        personality="cautious",
                                        nation="Britain")
        world.marshals["Wellington"] = enemy
        world.fleets = {"__naval__": {}}
        shut = {"allowed": False, "coverer": "Britain", "ratio": 0.5,
                "message": "The Royal Navy commands that water."}
        with self._forced_moderate() as evaluate, \
                patch("backend.game_logic.naval.crossing_check_reach",
                      return_value=shut):
            result = CommandExecutor().execute(
                {"command": {"marshal": "Ney", "action": "attack",
                             "target": "Wellington"}},
                {"world": world})
        evaluate.assert_not_called()
        assert result["success"] is False
        assert world.pending_objection is None
