"""W6-6 — Enemy marshals speak (EXP-M2).

After a battle the enemy commander gets one line in his register, in the
battle report (`battle_report.enemy_voice`) and as a campaign-log suffix.
Deterministic bank (personality × situation), rotated by the region's
battle count; named rows (Mack, Kutuzov, Archduke Charles, Wellington,
Blücher) override the personality default. Display-only, no serialization.
"""

from backend.campaign_log import format_event_oneliner
from backend.commands.executor import CommandExecutor
from backend.game_logic.enemy_voice import (
    VOICE_SITUATIONS,
    _NAMED_LINES,
    _PERSONALITY_LINES,
    derive_enemy_situation,
    pick_enemy_voice,
)

from tests.conftest import MarshalFactory, WorldFactory


class TestSituationDerivation:
    def test_defender_enemy_repels_your_attack(self):
        assert derive_enemy_situation("defender_victory", False, False) \
            == "repelled_you"

    def test_attacker_enemy_beats_you(self):
        assert derive_enemy_situation("attacker_tactical_victory", True,
                                      False) == "beat_you_attacking"

    def test_enemy_loses_ground_either_side(self):
        assert derive_enemy_situation("attacker_victory", False, False) \
            == "lost_ground"
        assert derive_enemy_situation("defender_tactical_victory", True,
                                      False) == "lost_ground"

    def test_forced_retreat_wins_over_outcome(self):
        assert derive_enemy_situation("attacker_victory", False, True) \
            == "forced_retreat"

    def test_stalemate(self):
        assert derive_enemy_situation("stalemate", True, False) == "stalemate"

    def test_mutual_destruction_silences(self):
        assert derive_enemy_situation("mutual_destruction", False, False) is None


class TestVoicePicking:
    def test_personality_matches_situation(self):
        line = pick_enemy_voice("Schwarzenberg", "cautious", "repelled_you", 0)
        assert "Schwarzenberg" in line
        assert line.split(": ", 1)[1].strip('"') in [
            v for v in _PERSONALITY_LINES["cautious"]["repelled_you"]]

    def test_named_override_wins(self):
        line = pick_enemy_voice("Mack", "cautious", "repelled_you", 0)
        assert "Mack does not leave his ground" in line

    def test_named_falls_back_to_personality_for_missing_situation(self):
        # Mack has no beat_you_attacking row — his cautious register speaks.
        line = pick_enemy_voice("Mack", "cautious", "beat_you_attacking", 0)
        assert line != ""
        assert "Mack" in line

    def test_deterministic_across_identical_inputs(self):
        a = pick_enemy_voice("Kutuzov", "cautious", "lost_ground", 3)
        b = pick_enemy_voice("Kutuzov", "cautious", "lost_ground", 3)
        assert a == b

    def test_rotation_by_battle_count(self):
        lines = {pick_enemy_voice("Schwarzenberg", "aggressive",
                                  "stalemate", k) for k in range(3)}
        assert len(lines) >= 2

    def test_camel_case_names_humanized(self):
        line = pick_enemy_voice("ArchdukeCharles", "cautious",
                                "repelled_you", 0)
        assert line.startswith("Archduke Charles:")

    def test_every_personality_covers_every_situation(self):
        for personality, bank in _PERSONALITY_LINES.items():
            for situation in VOICE_SITUATIONS:
                assert bank.get(situation), (personality, situation)
                assert len(bank[situation]) >= 2

    def test_named_rows_are_marquee_only(self):
        assert set(_NAMED_LINES) == {"Mack", "Kutuzov", "ArchdukeCharles",
                                     "Wellington", "Blucher"}


class TestEnemyVoiceEndToEnd:
    def _fight(self, attacker_strength=60000, defender_strength=8000):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=attacker_strength,
                                      personality="aggressive")
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

    def test_report_carries_the_voice(self):
        world, result = self._fight(attacker_strength=40000,
                                    defender_strength=35000)
        report = result.get("battle_report") or {}
        voice = report.get("enemy_voice", "")
        if world.get_marshal("Mack") and world.get_marshal("Mack").strength > 0:
            assert voice.startswith("Mack:")

    def test_campaign_log_suffix(self):
        world, result = self._fight(attacker_strength=40000,
                                    defender_strength=35000)
        battle_events = [e for e in world.event_log
                         if e.get("type") == "battle"]
        assert battle_events
        event = battle_events[-1]
        if event.get("enemy_voice"):
            line = format_event_oneliner(event)
            assert "Mack:" in line

    def test_garrison_assault_has_no_voice(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=60000,
                                      personality="aggressive")
        world = WorldFactory.with_marshals([ney])
        key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Ney", "action": "attack",
                         "target": "Rhineland",
                         "_muster_confirmed": True}},
            {"world": world})
        report = result.get("battle_report") or {}
        assert "enemy_voice" not in report

    def test_no_serialization(self):
        """Display-only: the voice never enters the save format."""
        world, _ = self._fight()
        data = world.to_dict()
        import json
        assert "enemy_voice" not in json.dumps(data.get("marshals", {}))
