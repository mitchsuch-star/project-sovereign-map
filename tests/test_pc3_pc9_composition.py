"""The composition slice — ROADMAP position 3 (August 3-4, 2026).

Position 1's 42-turn played campaign re-scored the enemy phase as theater at
6.0 against a 6.5 target, so the plan's own dissent clause moved this slice
ahead of the shippable build. PC-2/PC-3(display)/PC-7 landed in that session;
this file covers the rows that stayed OPEN:

  PC-3 (balance half) — the AI burns 2 of 4 AP fortifying and immediately
      unfortifying. Fixed at the PRODUCER, but on the fortify side: the P3
      threat rung was the one fortify site in `enemy_ai.py` missing the
      engaged guard its three siblings carry, and P0 unfortifies an engaged
      fortified marshal unconditionally — so the pair was self-cancelling by
      construction. NOT the reverted latch, which blocked the unfortify and
      collapsed the AI-V §4.7 variance signature.
  PC-4 — battle names collided and the ordinal sequence had holes.
      (Pins live in `test_w6_battle_naming.py`, beside the W6-2 contract.)
  PC-5 — "held the field alone" fired over a tableau of three engaged corps.
  PC-6 — the flanking tracker was side-blind: two armies contesting one
      province pooled their approaches, so each was credited with the other's
      march as a friendly pincer, and the message named the enemy's start
      line as a friendly one.
  PC-8 — the bad-odds interrupt priced solo strength and said "in greater
      strength", while `press on` committed two more corps. The GATE stays
      solo (re-pricing it breaks a CR-5 pin); the COPY gains the muster.
  PC-9 — player tutorial copy inside the enemy's report; "The Switzerland";
      `en_route` to where the marshal stands; and the notification tray.
"""

import backend.game_logic.battle_report as battle_report
from backend.ai.enemy_ai import EnemyAI
from backend.commands.delegation import describe_inferred_bad_odds
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.display_names import with_definite_article, takes_definite_article
from backend.game_logic.battle_report import _pick_observation
from backend.game_logic.dispatch import (
    _derive_marshal_status, _format_dispatch_event_text,
)
from backend.models.marshal import StrategicOrder, Stance
from backend.notifications import (
    NotificationCollector, NotificationPriority, create_notification,
)

from tests.conftest import MarshalFactory, WorldFactory


# ════════════════════════════════════════════════════════════════════════
# PC-3 — the AI stops paying for a round trip P0 always undid
# ════════════════════════════════════════════════════════════════════════

def _threat_world(enemy_location):
    """A cautious defender with a STRONGER enemy either on him or next door."""
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=20000, personality="cautious")
    ney.stance = Stance.DEFENSIVE
    mack = MarshalFactory.enemy(name="Mack", location=enemy_location,
                                nation="Austria", strength=40000)
    world = WorldFactory.with_marshals([ney, mack])
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    return world, ney


class TestPC3FortifyThrash:
    def test_p3_does_not_fortify_with_an_enemy_in_the_same_region(self):
        """The thrash: fortify here, and P0 unfortifies unconditionally next
        selection — 2 AP for no state change."""
        world, ney = _threat_world("Belgium")
        action = EnemyAI(CommandExecutor())._check_threats(ney, "France", world)
        assert action is None or action.get("action") != "fortify", action

    def test_p3_still_fortifies_against_an_ADJACENT_stronger_enemy(self):
        """FALSIFIABLE NEGATIVE: the capability is not removed. A stronger
        enemy next door is exactly what this rung exists for, and nothing
        unfortifies him for it."""
        world, ney = _threat_world("Rhineland")
        region = world.get_region("Belgium")
        assert "Rhineland" in region.adjacent_regions, "fixture assumption"
        action = EnemyAI(CommandExecutor())._check_threats(ney, "France", world)
        assert action is not None
        assert action.get("action") == "fortify", action

    def test_the_reverted_latch_is_not_what_landed(self):
        """The unfortify escape stays open — that is the difference between
        this fix and the one the previous session measured and reverted."""
        world, ney = _threat_world("Belgium")
        ney.fortified = True
        ai = EnemyAI(CommandExecutor())
        # P0's engaged-while-fortified arm still frees him to fight.
        action, _priority = ai._evaluate_marshal(ney, "France", world)
        assert action.get("action") in ("unfortify", "attack"), action


# ════════════════════════════════════════════════════════════════════════
# PC-5 — solitude is verified, never assumed
# ════════════════════════════════════════════════════════════════════════

def _battle_result(participants, failed_ally="Murat"):
    """A stalemate in which every called-for reinforcement failed to arrive —
    the branch that owns the 'held the field alone' bank."""
    return {
        "outcome": "stalemate",
        "attacker_nation": "France",
        "defender_nation": "Austria",
        "attacker_original_strength": 30000,
        "defender_original_strength": 30000,
        "attacker": {"name": "Lannes", "casualties": 4000, "remaining": 26000},
        "defender": {"name": "Mack", "casualties": 4000, "remaining": 26000},
        "modifier_snapshot": {"attacker": [], "defender": []},
        "coordination_context": {"attacker_participants": participants},
        "reinforcement_results_for_report": {
            "attacker": [{"marshal": failed_ally, "arrived": False}]},
    }


class TestPC5HeldTheFieldAlone:
    def test_alone_line_is_unreachable_when_others_fought(self):
        """The live case: three engaged corps, 64,943 committed, and Berthier
        reporting that the lead 'held the field alone'."""
        result = _battle_result(["Lannes", "Davout", "Ney"])
        for _ in range(40):
            line = _pick_observation(result, "France")
            assert "alone" not in line.lower(), line
            assert "single-handed" not in line.lower(), line

    def test_alone_line_IS_reachable_when_he_really_was_alone(self):
        """FALSIFIABLE POSITIVE: the bank is gated, not deleted."""
        result = _battle_result(["Lannes"])
        lines = {_pick_observation(result, "France") for _ in range(60)}
        assert any("alone" in ln.lower() or "single-handed" in ln.lower()
                   for ln in lines), lines

    def test_a_missing_participants_list_does_not_claim_solitude(self):
        """When we cannot check, we do not claim it — the first-pass call
        from inside resolve_battle has no coordination context."""
        result = _battle_result(["Lannes"])
        result["coordination_context"] = {}
        for _ in range(40):
            line = _pick_observation(result, "France")
            assert "alone" not in line.lower(), line

    def test_the_defender_side_reads_its_own_participants(self):
        """Perspective correctness: as the DEFENDER we must read the
        defender's participants, not the attacker's."""
        result = _battle_result(["Lannes"])
        result["attacker_nation"] = "Austria"
        result["defender_nation"] = "France"
        result["coordination_context"] = {
            "attacker_participants": ["Mack"],
            "defender_participants": ["Lannes", "Davout"]}
        result["reinforcement_results_for_report"] = {
            "defender": [{"marshal": "Murat", "arrived": False}]}
        for _ in range(40):
            line = _pick_observation(result, "France")
            assert "alone" not in line.lower(), line

    def test_both_banks_are_populated(self):
        """A split bank with an empty half would make random.choice raise."""
        assert battle_report._OBSERVATIONS["coordination_reinforcement_failure"]
        assert battle_report._OBSERVATIONS[
            "coordination_reinforcement_failure_alone"]


# ════════════════════════════════════════════════════════════════════════
# PC-6 — the pincer is counted among your OWN columns
# ════════════════════════════════════════════════════════════════════════

class TestPC6FlankingIsSideAware:
    def test_an_enemy_attack_on_the_same_region_is_not_our_pincer(self):
        """Live: `Mack flanks from Swabia while allies attack from
        Rhineland!` — Rhineland was French."""
        world = WorldFactory.basic()
        world.record_attack("Ney", "Rhineland", "Swabia", "France")
        world.record_attack("Mack", "Swabia", "Swabia", "Austria")
        austrian = world.calculate_flanking_bonus("Swabia", "Austria")
        assert austrian["bonus"] == 0, austrian
        assert world.get_flanking_message(
            "Mack", "Swabia", "Swabia", "Austria") is None

    def test_our_own_two_columns_still_flank(self):
        """FALSIFIABLE NEGATIVE: the mechanic survives the filter."""
        world = WorldFactory.basic()
        world.record_attack("Ney", "Rhineland", "Swabia", "France")
        world.record_attack("Davout", "Alsace", "Swabia", "France")
        french = world.calculate_flanking_bonus("Swabia", "France")
        assert french["bonus"] == 1, french
        msg = world.get_flanking_message("Davout", "Alsace", "Swabia", "France")
        assert msg and "Rhineland" in msg

    def test_the_nation_blind_call_is_unchanged(self):
        """Legacy callers (and 40+ pre-existing tests) keep the old pooling."""
        world = WorldFactory.basic()
        world.record_attack("Ney", "Rhineland", "Swabia")
        world.record_attack("Davout", "Alsace", "Swabia")
        assert world.calculate_flanking_bonus("Swabia")["bonus"] == 1

    def test_a_marshal_in_the_contested_province_does_not_flank_from_it(self):
        """Live: `ArchdukeCharles flanks from Swabia…` while attacking into
        Swabia. He is the anvil, not the hammer."""
        world = WorldFactory.basic()
        world.record_attack("ArchdukeCharles", "Swabia", "Swabia", "Austria")
        world.record_attack("Mack", "Tyrol", "Swabia", "Austria")
        msg = world.get_flanking_message(
            "ArchdukeCharles", "Swabia", "Swabia", "Austria")
        assert msg is not None
        assert "flanks from Swabia" not in msg, msg
        assert "holds them at Swabia" in msg, msg

    def test_the_attack_record_carries_the_nation(self):
        world = WorldFactory.basic()
        record = world.record_attack("Ney", "Rhineland", "Swabia", "France")
        assert record["nation"] == "France"
        restored = type(world).from_dict(world.to_dict())
        assert restored.attacks_this_turn["Swabia"][0]["nation"] == "France"


# ════════════════════════════════════════════════════════════════════════
# PC-8 — the marshal's read stays solo; Berthier names the muster
# ════════════════════════════════════════════════════════════════════════

class TestPC8BadOddsNamesTheMuster:
    def _world(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=24000, personality="aggressive")
        davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                         strength=30000, personality="cautious")
        mack = MarshalFactory.enemy(name="Mack", location="Rhineland",
                                    nation="Austria", strength=52000)
        world = WorldFactory.with_marshals([ney, davout, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        return world, ney, davout, mack

    def test_the_note_names_who_marches_and_the_joint_figure(self):
        world, ney, davout, mack = self._world()
        note = CommandExecutor()._combat._bad_odds_muster_note(ney, mack, world)
        assert "Davout" in note, note
        assert "24,000" in note, note          # his own
        assert "Berthier" in note, note

    def test_the_note_is_empty_when_nobody_would_answer(self):
        world, ney, davout, mack = self._world()
        del world.marshals["Davout"]
        assert CommandExecutor()._combat._bad_odds_muster_note(
            ney, mack, world) == ""

    def test_the_note_carries_the_player_nation_guard(self):
        """Same guard the muster preview's own call site uses."""
        world, ney, davout, mack = self._world()
        ney.nation = "Austria"
        davout.nation = "Austria"
        assert CommandExecutor()._combat._bad_odds_muster_note(
            ney, mack, world) == ""

    def test_the_modal_reads_as_one_sentence_run(self):
        msg = describe_inferred_bad_odds("Ney", "Mack", " Berthier adds: X.")
        assert "charge on your word. Berthier adds: X. Confirm" in msg

    def test_the_modal_is_unchanged_without_a_note(self):
        """FALSIFIABLE NEGATIVE: the no-muster case is byte-stable."""
        msg = describe_inferred_bad_odds("Ney", "Mack")
        assert msg == (
            "Ney reads this as a call to give battle, Sire — but Mack stands "
            "dug in and in greater strength. He will charge on your word. "
            "Confirm the assault, or hold him back?")


# ════════════════════════════════════════════════════════════════════════
# PC-9 — the copy and tray family
# ════════════════════════════════════════════════════════════════════════

class TestPC9SquareTutorialCopy:
    def _form_square(self, nation):
        marshal = MarshalFactory.infantry(name="Ney", location="Belgium",
                                          strength=20000, nation=nation)
        world = WorldFactory.with_marshals([marshal])
        return CommandExecutor().execute(
            {"success": True,
             "command": {"marshal": "Ney", "action": "form_square"}},
            {"world": world})

    def test_the_players_own_square_keeps_the_rule(self):
        result = self._form_square("France")
        assert "break the discipline" in result["message"]

    def test_an_enemy_square_does_not_lecture_the_player(self):
        """Live: the sentence appeared under [Austria], telling the player
        about the discipline of an Austrian square."""
        result = self._form_square("Austria")
        assert "forms square" in result["message"]
        assert "break the discipline" not in result["message"]


class TestPC9DefiniteArticle:
    def test_a_bare_state_takes_no_article(self):
        assert with_definite_article("Switzerland") == "Switzerland"
        assert not takes_definite_article("Switzerland")

    def test_an_institution_takes_one(self):
        assert (with_definite_article("Duchy of Warsaw", capitalize=True)
                == "The Duchy of Warsaw")
        assert with_definite_article("Roman Republic") == "the Roman Republic"

    def test_the_dissolution_line_reads_both_ways(self):
        """Live: `The Switzerland has ceased to exist.`"""
        assert _format_dispatch_event_text(
            "diplomatic_carved_vassal_dissolved",
            {"carved_name": "Switzerland"}
        ) == "Switzerland has ceased to exist."
        assert _format_dispatch_event_text(
            "diplomatic_carved_vassal_dissolved",
            {"carved_name": "DuchyOfWarsaw"}
        ) == "The Duchy of Warsaw has ceased to exist."

    def test_the_creation_line_uses_the_same_rule(self):
        line = _format_dispatch_event_text(
            "diplomatic_carved_vassal_created",
            {"carved_name": "DuchyOfWarsaw", "protector": "France"})
        assert line.startswith("The Duchy of Warsaw has been established")

    def test_a_name_that_already_carries_its_article_is_not_doubled(self):
        assert with_definite_article("the Papal States") == "the Papal States"


class TestPC9EnRoute:
    def _marshal_under_orders(self, destination):
        marshal = MarshalFactory.infantry(name="Ney", location="Swabia")
        world = WorldFactory.with_marshals([marshal])
        # `in_strategic_mode` is derived from the order — no setter.
        marshal.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target=destination,
            target_type="region", started_turn=world.current_turn,
            original_command=f"Ney, move to {destination}")
        return marshal, world

    def test_a_march_to_where_he_stands_is_not_a_march(self):
        """Live: `en_route` — 'Moving to Swabia' for a man in Swabia."""
        marshal, world = self._marshal_under_orders("Swabia")
        status, note = _derive_marshal_status(marshal, world)
        assert status != "en_route"
        assert "Moving to" not in note
        assert "Swabia" in note

    def test_a_real_march_still_reports_as_one(self):
        marshal, world = self._marshal_under_orders("Bavaria")
        status, note = _derive_marshal_status(marshal, world)
        assert status == "en_route"
        assert note.startswith("Moving to Bavaria")


class TestPC9NotificationTray:
    def _cornered(self, marshal="Ney", turn=3):
        return create_notification(
            "marshal_last_stand", NotificationPriority.CRITICAL,
            f"{marshal} is cornered", f"{marshal} is surrounded.", turn,
            details={"marshal": marshal})

    def test_seven_identical_alerts_collapse_to_one(self):
        """Live: the tray hit its 50-row cap with 7x 'Ney is cornered'."""
        tray = NotificationCollector()
        for turn in range(3, 10):
            tray.add(self._cornered(turn=turn))
        pending = tray.get_pending()
        assert len(pending) == 1
        assert pending[0]["repeat_count"] == 7
        assert pending[0]["title"] == "Ney is cornered (x7)"
        assert pending[0]["turn_created"] == 9      # refreshed, not stale

    def test_a_different_subject_is_a_different_alert(self):
        tray = NotificationCollector()
        tray.add(self._cornered("Ney"))
        tray.add(self._cornered("Davout"))
        assert len(tray.get_pending()) == 2

    def test_a_shared_headline_with_different_subjects_survives(self):
        """FALSIFIABLE NEGATIVE — this is PF-5's own pin in miniature: two
        proposal results share a title and must NOT collapse."""
        tray = NotificationCollector()
        for target in ("Prussia", "Austria"):
            tray.add(create_notification(
                "diplomatic_proposal_result", NotificationPriority.NORMAL,
                "alliance Accepted", f"{target} has responded.", 1,
                details={"target_nation": target}))
        assert len(tray.get_pending()) == 2

    def test_a_pre_pc9_saved_notification_still_collapses(self):
        """from_list restores dicts with no base_title / repeat_count."""
        legacy = self._cornered()
        legacy.pop("base_title")
        legacy.pop("repeat_count")
        tray = NotificationCollector.from_list([legacy])
        tray.add(self._cornered(turn=8))
        assert len(tray.get_pending()) == 1

    def test_a_repeat_takes_the_higher_priority(self):
        tray = NotificationCollector()
        low = create_notification("x", NotificationPriority.NORMAL, "t", "m", 1)
        high = create_notification("x", NotificationPriority.CRITICAL, "t", "m", 2)
        tray.add(low)
        tray.add(high)
        assert tray.get_pending()[0]["priority"] == int(
            NotificationPriority.CRITICAL)

    def _cornered_world(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=3000, personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=40000)
        world = WorldFactory.with_marshals([ney, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        world.notifications.add(self._cornered())
        ney.pending_interrupt = {
            "marshal": "Ney", "interrupt_type": "last_stand",
            "enemy": "Mack", "enemy_nation": "Austria",
            "options": ["fight_to_the_last", "attempt_breakout"],
        }
        return world, ney

    def _live_last_stand_notices(self, world):
        return [n for n in world.notifications.get_pending()
                if n.get("type") == "marshal_last_stand"]

    def test_a_successful_breakout_retires_the_notice(self):
        """Live: a turn-3 alert still sitting in the tray at turn 42, for a
        marshal whose fate had been decided 39 turns earlier.

        This is the ANSWER seam specifically: the marshal escapes, so he is
        never captured and `_capture_marshal`'s own sweep cannot be what
        cleans up. Mutation-checked — disabling the dismissal in
        `strategic.py` must fail this test and no other.
        """
        import random as _random
        world, ney = self._cornered_world()
        original = _random.random
        _random.random = lambda: 0.0          # the escape roll succeeds
        try:
            StrategicOrderProcessor(CommandExecutor()).handle_response(
                "Ney", "last_stand", "attempt_breakout", world,
                {"world": world})
        finally:
            _random.random = original
        assert not getattr(ney, "captured_by", ""), "fixture: he must escape"
        assert not self._live_last_stand_notices(world)

    def test_being_taken_retires_the_notice(self):
        """The other seam: he is captured by some path the player never
        answered, and the ask is moot."""
        world, ney = self._cornered_world()
        CommandExecutor()._combat._capture_marshal(ney, "Austria", world)
        assert not self._live_last_stand_notices(world)
