"""Phase 3 (Combat Overhaul, spec §3.2) — DR-1 glory-from-attrition and
DR-2 slow glory decay.

The triple lock that kept Marshal Drama starved had three parts; this file
pins the first two:

  DR-1  a hard-fought INCONCLUSIVE battle feeds the ladder — the commander who
        out-bleeds the other >=2:1 (or takes a province) earns partial glory,
        so the "ground them down over six assaults" campaign accretes laurels
        before a clean rout. Symmetric player/enemy (GR5).
  DR-2  the glory window lengthened 5 -> 8 so occasional deeds survive long
        enough to open a ladder gap instead of evaporating.

DR-3 (authority-dampening rework) is pinned in test_drama_ladder_liveness.py.
Companion metric: M7 in tests/test_combat_sweep_metrics.py.
"""

from pathlib import Path

import pytest

from backend.game_logic import jealousy as J
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
    w = WorldState.from_dict(world1805.to_dict())
    w.authority_tracker.authority = 50
    w.current_turn = 5
    return w


# ═══════════════════════ DR-1: the out-bled predicate ══════════════════════


class TestOutBled:
    def test_two_to_one_qualifies(self):
        assert J._out_bled(1000, 2000) is True

    def test_more_than_two_to_one_qualifies(self):
        assert J._out_bled(1000, 5000) is True

    def test_under_two_to_one_does_not(self):
        assert J._out_bled(1000, 1999) is False

    def test_even_exchange_does_not(self):
        assert J._out_bled(1000, 1000) is False

    def test_flawless_qualifies(self):
        # took nothing, dealt something — a clean domination
        assert J._out_bled(0, 300) is True

    def test_flawless_stalemate_zero_zero_does_not(self):
        assert J._out_bled(0, 0) is False


# ═══════════════════ DR-1: stalemate & occupation glory ════════════════════


class TestStalemateGlory:
    def test_attacker_out_bleeds_scores(self, world):
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        # inconclusive result, attacker inflicts 3000 for 1000 lost (>=2:1)
        J.record_battle_glory(
            world, ney, mack, attacker_won=False, defender_won=False,
            attacker_casualties=1000, defender_casualties=3000,
            conquered=False,
            pre_attacker_strength=40000, pre_defender_strength=40000)
        assert J.get_glory_score(ney, world.current_turn) == J.STALEMATE_GLORY
        # the out-bled defender earns nothing from this exchange
        assert J.get_glory_score(mack, world.current_turn) == 0

    def test_defender_out_bleeds_scores_symmetrically(self, world):
        # GR5: whichever side dominates the exchange is rewarded — here the
        # defender out-bleeds the attacker >=2:1 in an inconclusive battle.
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        J.record_battle_glory(
            world, ney, mack, attacker_won=False, defender_won=False,
            attacker_casualties=4000, defender_casualties=1500,
            conquered=False,
            pre_attacker_strength=40000, pre_defender_strength=40000)
        assert J.get_glory_score(mack, world.current_turn) == J.STALEMATE_GLORY
        assert J.get_glory_score(ney, world.current_turn) == 0

    def test_even_stalemate_scores_nobody(self, world):
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        J.record_battle_glory(
            world, ney, mack, attacker_won=False, defender_won=False,
            attacker_casualties=2000, defender_casualties=2200,
            conquered=False,
            pre_attacker_strength=40000, pre_defender_strength=40000)
        assert J.get_glory_score(ney, world.current_turn) == 0
        assert J.get_glory_score(mack, world.current_turn) == 0

    def test_occupation_scores_without_clean_victory(self, world):
        # taking a province off an uncontested/inconclusive field result still
        # earns the attacker partial glory (spec DR-1 "and for taking a
        # province").
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        J.record_battle_glory(
            world, ney, mack, attacker_won=False, defender_won=False,
            attacker_casualties=0, defender_casualties=0,
            conquered=True,
            pre_attacker_strength=40000, pre_defender_strength=40000)
        assert J.get_glory_score(ney, world.current_turn) == J.STALEMATE_GLORY

    def test_decisive_win_still_uses_victory_points(self, world):
        # regression: a clean win is unchanged by DR-1 — full victory formula.
        ney, mack = world.marshals["Ney"], world.marshals["Mack"]
        J.record_battle_glory(
            world, ney, mack, attacker_won=True, defender_won=False,
            attacker_casualties=1000, defender_casualties=3000,
            conquered=True,
            pre_attacker_strength=40000, pre_defender_strength=40000)
        # 1 base + 1 decisive + 1 territory = 3 (not the DR-1 flat +1)
        assert J.get_glory_score(ney, world.current_turn) == 3

    def test_enemy_side_scores_through_same_seam(self, world):
        # GR5: enemy marshals accrue stalemate glory through the identical seam.
        # Mack (Austria) out-bleeds a France defender in an inconclusive clash.
        mack, ney = world.marshals["Mack"], world.marshals["Ney"]
        J.record_battle_glory(
            world, mack, ney, attacker_won=False, defender_won=False,
            attacker_casualties=800, defender_casualties=2000,
            conquered=False,
            pre_attacker_strength=30000, pre_defender_strength=30000)
        assert J.get_glory_score(mack, world.current_turn) == J.STALEMATE_GLORY
        assert J.get_glory_score(ney, world.current_turn) == 0


# ═══════════════════════════ DR-2: slow decay ══════════════════════════════


class TestGloryWindow:
    def test_window_is_eight(self):
        assert J.GLORY_WINDOW == 8

    def test_deed_survives_to_the_edge_of_the_window(self, world):
        ney = world.marshals["Ney"]
        J._append_glory(ney, 1, 2)          # a deed on turn 1
        # turn 8: age 7 < 8 — still counted (the old 5-turn window dropped it
        # at turn 6, so no gap could ever form).
        assert J.get_glory_score(ney, 8) == 2
        # turn 9: age 8 — falls out of the window.
        assert J.get_glory_score(ney, 9) == 0

    def test_deeds_accrete_across_the_longer_window(self, world):
        ney = world.marshals["Ney"]
        J._append_glory(ney, 2, 1)
        J._append_glory(ney, 4, 1)
        J._append_glory(ney, 6, 1)
        # all three within an 8-turn window at turn 7 -> a real ladder gap;
        # under the old 5-turn window the turn-2 deed would already be gone.
        assert J.get_glory_score(ney, 7) == 3
