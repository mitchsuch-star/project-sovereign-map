"""SF-MD-1 "Every man his own voice" (Score Finish Step 2, October 2, 2026).

RS-24: the voice banks rotate on the SPEAKER's own battles, every French
marshal of 1805, both Archdukes and Kutuzov have a row in every situation,
the personality bank follows a named row, and no man says a line twice in
five battles.
"""
import contextlib
import io
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import combat_executor as CE
from backend.commands.parser import CommandParser
from backend.game_logic import enemy_voice as EV
from backend.game_logic import marshal_voice as MV
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCEN = str(REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
           / "europe_1805.json")


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture
def world():
    with _quiet():
        return WorldState.from_scenario(SCEN)


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def _world_with(log):
    return SimpleNamespace(event_log=list(log), battle_counts={"Swabia": 3})


def _man(name, won, lost):
    return SimpleNamespace(name=name, battles_won=won, battles_lost=lost)


# ═══════════════════════════════════════════════════════════════════════════
# The key is his own
# ═══════════════════════════════════════════════════════════════════════════

class TestTheKeyIsHisOwn:

    def test_a_decided_battle_subtracts_itself_back_out(self):
        # resolve_combat has already counted today's battle (won 2 -> 3).
        assert CE._voice_rotation_key_for(_world_with([]), _man("Ney", 3, 1), "Swabia",
                                          "carried_the_field") == 3
        assert CE._voice_rotation_key_for(_world_with([]), _man("Ney", 1, 0), "Swabia",
                                          "lost_ground") == 0

    def test_a_draw_counts_on_neither_record_and_is_read_from_the_log(self):
        key_first_draw = CE._voice_rotation_key_for(_world_with([]), _man("Ney", 2, 1),
                                                    "Swabia", "stalemate")
        assert key_first_draw == 3
        log = [{"type": "battle", "outcome": "stalemate", "attacker": "Ney", "defender": "Mack"},
               {"type": "battle", "outcome": "stalemate", "attacker": {"name": "Mack"},
                "defender": {"name": "Ney"}},
               {"type": "battle", "outcome": "attacker_victory", "attacker": "Ney", "defender": "Mack"},
               {"type": "battle", "outcome": "stalemate", "attacker": "Davout", "defender": "Mack"}]
        assert CE._voice_rotation_key_for(_world_with(log), _man("Ney", 2, 1), "Swabia",
                                          "stalemate") == 5
        assert CE._voice_rotation_key_for(_world_with(log), _man("Ney", 3, 1), "Swabia",
                                          "carried_the_field") == 5
        # Mack: three logged draws + one loss counted today -> 0 + 1 - 1 + 3.
        assert CE._voice_rotation_key_for(_world_with(log), _man("Mack", 0, 1), "Swabia",
                                          "lost_ground") == 3

    def test_every_battle_advances_the_key_by_one(self):
        """Five battles of mixed outcomes, in order: the keys read 0..4."""
        log, won, lost, keys = [], 0, 0, []
        for outcome in ("attacker_victory", "stalemate", "defender_victory",
                        "stalemate", "attacker_victory"):
            if outcome == "stalemate":
                keys.append(CE._voice_rotation_key_for(_world_with(log), _man("Ney", won, lost),
                                                       "Swabia", "stalemate"))
            else:
                won += 1 if outcome == "attacker_victory" else 0
                lost += 1 if outcome == "defender_victory" else 0
                keys.append(CE._voice_rotation_key_for(_world_with(log), _man("Ney", won, lost),
                                                       "Swabia", "carried_the_field"))
            log.append({"type": "battle", "outcome": outcome, "attacker": "Ney", "defender": "Mack"})
        assert keys == [0, 1, 2, 3, 4]

    def test_lever_down_reads_the_province(self, monkeypatch):
        monkeypatch.setattr(CE, "THE_VOICE_ROTATES_ON_HIS_OWN_RECORD", False)
        assert CE._voice_rotation_key_for(_world_with([]), _man("Ney", 3, 1), "Swabia",
                                          "carried_the_field") == 2


# ═══════════════════════════════════════════════════════════════════════════
# The bank falls through
# ═══════════════════════════════════════════════════════════════════════════

class TestTheBankFallsThrough:

    def test_index_zero_is_the_authored_opening_line(self):
        assert MV.pick_marshal_voice("Ney", "aggressive", "carried_the_field", 0) == \
            'Ney: "They stood, Sire. Briefly."'
        assert EV.pick_enemy_voice("Mack", "cautious", "repelled_you", 0) == \
            'Mack: "Mack does not leave his ground. He sees no reason to start today."'

    def test_the_personality_lines_follow_the_named_row(self):
        own = [MV.pick_marshal_voice("Ney", "aggressive", "carried_the_field", k) for k in range(7)]
        assert len(set(own)) == 7
        assert own[2].split(": ", 1)[1].strip('"') == \
            MV._OWN_PERSONALITY_LINES["aggressive"]["carried_the_field"][0]
        enemy = [EV.pick_enemy_voice("Mack", "cautious", "repelled_you", k) for k in range(8)]
        assert len(set(enemy)) == 8
        assert enemy[3].split(": ", 1)[1].strip('"') == \
            EV._PERSONALITY_LINES["cautious"]["repelled_you"][0]

    def test_lever_down_is_the_named_row_alone(self, monkeypatch):
        monkeypatch.setattr(MV, "THE_NAMED_BANK_FALLS_THROUGH", False)
        monkeypatch.setattr(EV, "THE_NAMED_BANK_FALLS_THROUGH", False)
        assert MV.pick_marshal_voice("Ney", "aggressive", "carried_the_field", 2) == \
            MV.pick_marshal_voice("Ney", "aggressive", "carried_the_field", 0)
        assert EV.pick_enemy_voice("Mack", "cautious", "repelled_you", 3) == \
            EV.pick_enemy_voice("Mack", "cautious", "repelled_you", 0)

    def test_the_sovereign_still_never_speaks(self):
        assert MV.pick_marshal_voice("Napoleon", "sovereign", "carried_the_field", 0) == ""
        assert EV.pick_enemy_voice("Alexander", "sovereign", "repelled_you", 0) == ""


# ═══════════════════════════════════════════════════════════════════════════
# The census: no line twice in five battles, for every man on the board
# ═══════════════════════════════════════════════════════════════════════════

class TestNoManRepeatsHimselfInFiveBattles:

    def test_every_marshal_on_the_1805_board(self, world):
        failures = []
        for name, marshal in sorted(world.marshals.items()):
            personality = str(getattr(marshal, "personality", "") or "")
            if personality == "sovereign":
                continue
            own = marshal.nation == world.player_nation
            situations = MV.OWN_VOICE_SITUATIONS if own else EV.VOICE_SITUATIONS
            picker = MV.pick_marshal_voice if own else EV.pick_enemy_voice
            for situation in situations:
                for start in range(0, 8):
                    lines = [picker(name, personality, situation, k)
                             for k in range(start, start + 5)]
                    if "" in lines or len(set(lines)) != 5:
                        failures.append((name, situation, start, lines))
        assert not failures, failures[:3]

    def test_every_row_covers_every_situation(self):
        for name in ("Ney", "Davout", "Murat", "Lannes", "Soult", "Bernadotte", "Massena"):
            assert set(MV._OWN_NAMED_LINES[name]) == set(MV.OWN_VOICE_SITUATIONS), name
        for name in ("ArchdukeCharles", "ArchdukeJohn", "Kutuzov", "Mack"):
            assert set(EV._NAMED_LINES[name]) == set(EV.VOICE_SITUATIONS), name

    def test_no_bank_carries_a_line_twice(self):
        for name, rows in MV._OWN_NAMED_LINES.items():
            for situation in MV.OWN_VOICE_SITUATIONS:
                for personality in ("aggressive", "cautious", "literal"):
                    bank = MV.voice_bank(name, personality, situation)
                    assert len(bank) == len(set(bank)) >= 5, (name, situation)
        for name, rows in EV._NAMED_LINES.items():
            for situation in EV.VOICE_SITUATIONS:
                for personality in ("aggressive", "cautious", "literal"):
                    bank = EV.voice_bank(name, personality, situation)
                    assert len(bank) == len(set(bank)) >= 5, (name, situation)


# ═══════════════════════════════════════════════════════════════════════════
# Driven: the line the report carries is the one his own record selects
# ═══════════════════════════════════════════════════════════════════════════

class TestTheReportReadsHisRecord:

    def test_both_mouths_rotate_on_their_own_battles(self, shipped):
        client, world = shipped
        ney = world.marshals["Ney"]
        charles = world.marshals["ArchdukeCharles"]
        charles.location = ney.location
        world._build_marshal_index()
        world.calculate_visibility()
        ney.battles_won, ney.battles_lost = 2, 1          # three battles behind him
        charles.battles_won, charles.battles_lost = 0, 0  # his first
        world.battle_counts = {ney.location: 6}           # the province has seen many
        r = post(client, "Ney, attack Archduke Charles")
        if r.get("muster_confirm"):
            r = post(client, "attack anyway")
        elif r.get("pending_objection"):
            r = post(client, "trust")
        report = r.get("battle_report") or {}
        assert report, r.get("message")
        outcome = str(report.get("outcome") or r.get("outcome") or "")
        own_forced = bool((report.get("attacker") or {}).get("forced_retreat"))
        enemy_forced = bool((report.get("defender") or {}).get("forced_retreat"))
        own_situation = MV.derive_own_situation(outcome, True, own_forced)
        enemy_situation = EV.derive_enemy_situation(outcome, False, enemy_forced)
        if own_situation and ney.strength > 0:
            assert report.get("marshal_voice") == MV.pick_marshal_voice(
                "Ney", ney.personality, own_situation, 3), report.get("marshal_voice")
        if enemy_situation and charles.strength > 0:
            assert report.get("enemy_voice") == EV.pick_enemy_voice(
                "ArchdukeCharles", charles.personality, enemy_situation, 0), report.get("enemy_voice")
