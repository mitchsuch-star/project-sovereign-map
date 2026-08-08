"""Marshal Voice Tier 1 + XR-5 (ROADMAP position 9, Aug 8 2026).

Tier 1 completes marshal_voice.py's trio on the proven enemy_voice.py
pattern: aggressive + cautious acknowledgment/completion banks at the two
seams the literal has owned since W6-5, and post-battle lines for the
player's own commander in all three registers
(`battle_report.marshal_voice`, the enemy_voice mirror — named marquee
rows Ney/Davout/Murat). Deterministic, GR6 display-only, zero LLM cost.

XR-5 (BUG_FIXES): enemy battle-quip variety — Mack's one-line stalemate
bank repeated verbatim 3× across the seven-battle Ulm grind. Bank growth
is APPEND-ONLY (index 0 pinned by the W6-6 tests + serialized
battle_counts rotation): every named bank >= 2 lines (Mack's four >= 3),
every personality bank >= 3.
"""

import json

from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.game_logic import enemy_voice as EV
from backend.game_logic import marshal_voice as MV
from backend.models.marshal import Marshal, StrategicOrder

from tests.conftest import MarshalFactory, WorldFactory


# ═══════════════════ POST-BATTLE MIRROR (module level) ═════════════════════


class TestOwnSituationDerivation:
    def test_attacker_carries_the_field(self):
        assert MV.derive_own_situation("attacker_victory", True, False) \
            == "carried_the_field"

    def test_defender_holds_the_line(self):
        assert MV.derive_own_situation("defender_victory", False, False) \
            == "held_the_line"

    def test_lost_ground_either_side(self):
        assert MV.derive_own_situation("defender_victory", True, False) \
            == "lost_ground"
        assert MV.derive_own_situation("attacker_tactical_victory", False,
                                       False) == "lost_ground"

    def test_forced_retreat_wins_over_outcome(self):
        assert MV.derive_own_situation("attacker_victory", True, True) \
            == "driven_back"

    def test_stalemate(self):
        assert MV.derive_own_situation("stalemate", True, False) \
            == "stalemate"

    def test_mutual_destruction_silences(self):
        assert MV.derive_own_situation("mutual_destruction", True, False) \
            is None


class TestOwnVoicePicking:
    def test_personality_matches_situation(self):
        line = MV.pick_marshal_voice("Bernadotte", "cautious",
                                     "held_the_line", 0)
        assert line.startswith("Bernadotte:")
        assert line.split(": ", 1)[1].strip('"') in \
            MV._OWN_PERSONALITY_LINES["cautious"]["held_the_line"]

    def test_named_override_wins(self):
        line = MV.pick_marshal_voice("Davout", "cautious",
                                     "carried_the_field", 0)
        assert "The Third Corps does not require luck" in line

    def test_named_falls_back_for_missing_situation(self):
        # Murat has no stalemate row — his aggressive register speaks.
        line = MV.pick_marshal_voice("Murat", "aggressive", "stalemate", 0)
        assert line != ""
        assert line.split(": ", 1)[1].strip('"') in \
            MV._OWN_PERSONALITY_LINES["aggressive"]["stalemate"]

    def test_deterministic_across_identical_inputs(self):
        a = MV.pick_marshal_voice("Ney", "aggressive", "driven_back", 4)
        b = MV.pick_marshal_voice("Ney", "aggressive", "driven_back", 4)
        assert a == b

    def test_rotation_by_battle_count(self):
        lines = {MV.pick_marshal_voice("Lannes", "aggressive",
                                       "stalemate", k) for k in range(3)}
        assert len(lines) >= 2

    def test_every_personality_covers_every_situation(self):
        for personality, bank in MV._OWN_PERSONALITY_LINES.items():
            for situation in MV.OWN_VOICE_SITUATIONS:
                assert bank.get(situation), (personality, situation)
                assert len(bank[situation]) >= 3, (personality, situation)

    def test_named_rows_are_marquee_only(self):
        assert set(MV._OWN_NAMED_LINES) == {"Ney", "Davout", "Murat"}

    def test_unknown_situation_is_silent(self):
        assert MV.pick_marshal_voice("Ney", "aggressive", "repelled_you",
                                     0) == ""


# ═══════════════════ ACK + COMPLETION (module level) ═══════════════════════


class TestPersonalityAck:
    def test_aggressive_and_cautious_cover_all_order_types(self):
        for personality in ("aggressive", "cautious"):
            for order_type in ("MOVE_TO", "PURSUE", "HOLD", "SUPPORT"):
                line = MV.personality_ack(personality, order_type, 1)
                assert line, (personality, order_type)
                assert line in MV._ACK_LINES[personality][order_type]

    def test_literal_returns_empty(self):
        """The literal's verbatim-quote ack is the W6-5 doctrine — these
        banks must never speak for him."""
        assert MV.personality_ack("literal", "MOVE_TO", 1) == ""

    def test_unknown_personality_and_order_type_silent(self):
        assert MV.personality_ack("balanced", "MOVE_TO", 1) == ""
        assert MV.personality_ack("aggressive", "CANCEL", 1) == ""

    def test_deterministic_and_rotating(self):
        a = MV.personality_ack("aggressive", "HOLD", 3)
        b = MV.personality_ack("aggressive", "HOLD", 3)
        assert a == b
        lines = {MV.personality_ack("cautious", "PURSUE", t)
                 for t in range(3)}
        assert len(lines) >= 2


class TestPersonalityCompletion:
    def test_wraps_reason_with_register_line(self):
        out = MV.personality_completion("aggressive", "Arrived at Vienna.",
                                        "Ney", 2)
        assert out.startswith("Arrived at Vienna.")
        assert "Ney:" in out
        assert any(v in out for v in MV._COMPLETION_LINES["aggressive"])

    def test_literal_passes_through_unchanged(self):
        assert MV.personality_completion(
            "literal", "Arrived.", "Soult", 2) == "Arrived."

    def test_unknown_personality_passes_through(self):
        assert MV.personality_completion(
            "balanced", "Arrived.", "X", 2) == "Arrived."


# ═══════════════════════ SEAM WIRING (end to end) ══════════════════════════


class TestBattleReportCarriesOwnVoice:
    def _fight(self, personality="aggressive", attacker_strength=40000,
               defender_strength=35000):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=attacker_strength,
                                      personality=personality)
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria",
                                    strength=defender_strength,
                                    personality="cautious")
        world = WorldFactory.with_marshals([ney, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Ney", "action": "attack",
                         "target": "Mack", "_muster_confirmed": True}},
            {"world": world})
        return world, result

    def test_report_carries_the_players_commander(self):
        world, result = self._fight()
        report = result.get("battle_report") or {}
        ney = world.get_marshal("Ney")
        if ney and ney.strength > 0:
            voice = report.get("marshal_voice", "")
            assert voice.startswith("Ney:")

    def test_own_voice_beside_enemy_voice_not_instead(self):
        world, result = self._fight()
        report = result.get("battle_report") or {}
        mack = world.get_marshal("Mack")
        if mack and mack.strength > 0 and report.get("enemy_voice"):
            assert report.get("marshal_voice", "").startswith("Ney:")
            assert report["enemy_voice"].startswith("Mack:")

    def test_no_serialization(self):
        world, _ = self._fight()
        data = world.to_dict()
        assert "marshal_voice" not in json.dumps(data.get("marshals", {}))


class TestAckSeam:
    def _order(self, personality, strategic_type, action, target=None):
        marshal = MarshalFactory.infantry(name="Ney", location="Belgium",
                                          strength=30000,
                                          personality=personality)
        marshal.trust.set(90)
        world = WorldFactory.with_marshals([marshal])
        if target is None:
            region = world.get_region("Belgium")
            target = next(
                adj for adj in region.adjacent_regions
                if not world.get_enemies_in_region(adj, "France"))
        executor = CommandExecutor()
        # is_strategic/strategic_type live at the PARSE-RESULT top level
        # (executor.py:627 copies them down), not inside command.
        result = executor.execute(
            {"success": True,
             "is_strategic": True,
             "strategic_type": strategic_type,
             "command": {"marshal": "Ney", "action": action,
                         "target": target}},
            {"world": world})
        return result

    def test_aggressive_ack_line_rides_the_message(self):
        # MOVE_TO — aggressive marshals object to sitting idle (a HOLD
        # order can legitimately raise the strategic objection), never to
        # marching.
        result = self._order("aggressive", "MOVE_TO", "move")
        assert result.get("success"), result.get("message")
        assert any(v in result.get("message", "")
                   for v in MV._ACK_LINES["aggressive"]["MOVE_TO"]), \
            result.get("message")
        assert "Ney:" in result.get("message", "")

    def test_cautious_ack_line_rides_the_message(self):
        # HOLD — the cautious marshal's favorite instruction.
        result = self._order("cautious", "HOLD", "hold", target="Belgium")
        assert result.get("success"), result.get("message")
        assert any(v in result.get("message", "")
                   for v in MV._ACK_LINES["cautious"]["HOLD"]), \
            result.get("message")

    def test_literal_keeps_the_quote_doctrine(self):
        result = self._order("literal", "MOVE_TO", "move")
        assert result.get("success"), result.get("message")
        message = result.get("message", "")
        for bank in MV._ACK_LINES.values():
            for lines in bank.values():
                for line in lines:
                    assert line not in message


class TestCompletionSeam:
    def _complete(self, personality, name="Ney"):
        marshal = MarshalFactory.infantry(name=name, location="Belgium",
                                          strength=30000,
                                          personality=personality)
        world = WorldFactory.with_marshals([marshal])
        marshal.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Belgium", target_type="region",
            started_turn=1, original_command="march to Belgium")
        return StrategicOrderProcessor(CommandExecutor())._complete_order(
            marshal, world, "Arrived at Belgium.")

    def test_aggressive_completion_speaks(self):
        out = self._complete("aggressive")
        assert out["message"].startswith("Arrived at Belgium.")
        assert any(v in out["message"]
                   for v in MV._COMPLETION_LINES["aggressive"])

    def test_cautious_completion_speaks(self):
        out = self._complete("cautious")
        assert any(v in out["message"]
                   for v in MV._COMPLETION_LINES["cautious"])

    def test_literal_completion_still_quotes_the_order(self):
        out = self._complete("literal", name="Soult")
        assert "march to Belgium" in out["message"]
        for bank in MV._COMPLETION_LINES.values():
            for line in bank:
                assert line not in out["message"]

    def test_enemy_marshal_completion_stays_plain(self):
        marshal = MarshalFactory.enemy(name="Mack", location="Belgium",
                                       nation="Austria", strength=20000,
                                       personality="cautious")
        world = WorldFactory.with_marshals([marshal])
        marshal.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Belgium", target_type="region",
            started_turn=1, original_command="advance")
        out = StrategicOrderProcessor(CommandExecutor())._complete_order(
            marshal, world, "Arrived.")
        assert out["message"] == "Arrived."


class TestClientRenders:
    """The two .gd surfaces consume the new field (the CA8-7 lesson: a
    voice generated and never rendered is mute in its own scene)."""

    def test_berthier_report_renders_marshal_voice(self):
        from pathlib import Path
        repo = Path(__file__).resolve().parents[1]
        main_gd = (repo / "godot-client" / "project-sovereign" / "scripts"
                   / "main.gd").read_text(encoding="utf-8")
        assert 'report.get("marshal_voice"' in main_gd

    def test_enemy_phase_dialog_renders_marshal_voice(self):
        from pathlib import Path
        repo = Path(__file__).resolve().parents[1]
        dlg = (repo / "godot-client" / "project-sovereign" / "scripts"
               / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
        assert 'report.get("marshal_voice"' in dlg

    def test_report_propagation_site_carries_both_voices(self):
        from pathlib import Path
        repo = Path(__file__).resolve().parents[1]
        src = (repo / "backend" / "commands"
               / "combat_executor.py").read_text(encoding="utf-8")
        assert 'result["battle_report"]["marshal_voice"]' in src


# ═══════════════════════════ XR-5 VARIETY ══════════════════════════════════


class TestXr5QuipVariety:
    def test_every_named_bank_has_at_least_two_lines(self):
        for name, banks in EV._NAMED_LINES.items():
            for situation, lines in banks.items():
                assert len(lines) >= 2, (name, situation)

    def test_mack_banks_reach_three(self):
        """The measured offender: the seven-battle Ulm grind repeated his
        one stalemate line verbatim 3×."""
        for situation, lines in EV._NAMED_LINES["Mack"].items():
            assert len(lines) >= 3, situation

    def test_personality_banks_reach_three(self):
        for personality, banks in EV._PERSONALITY_LINES.items():
            for situation in EV.VOICE_SITUATIONS:
                assert len(banks[situation]) >= 3, (personality, situation)

    def test_grind_of_three_gives_three_distinct_mack_lines(self):
        lines = {EV.pick_enemy_voice("Mack", "cautious", "stalemate", k)
                 for k in (1, 2, 3)}
        assert len(lines) == 3

    def test_append_only_growth_keeps_index_zero(self):
        """The rotation key is serialized state (battle_counts) and the
        W6-6 pins anchor index 0 — growth must never reorder."""
        assert EV._NAMED_LINES["Mack"]["stalemate"][0] \
            == "You see? The position was sound. It is always sound."
        assert EV._PERSONALITY_LINES["cautious"]["forced_retreat"][0] \
            == "An army preserved is a battle not yet lost."


class TestVoiceOwnershipUndisturbed:
    def test_own_named_rows_never_collide_with_enemy_named_rows(self):
        """Voice ownership (WAVE6 §14): player marquee rows vs enemy
        marquee rows are disjoint casts."""
        assert not set(MV._OWN_NAMED_LINES) & set(EV._NAMED_LINES)

    def test_no_verbatim_line_shared_between_modules(self):
        own = {line for banks in MV._OWN_PERSONALITY_LINES.values()
               for lines in banks.values() for line in lines}
        enemy = {line for banks in EV._PERSONALITY_LINES.values()
                 for lines in banks.values() for line in lines}
        assert not own & enemy
