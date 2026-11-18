"""Row BA, session BA-6 (November 17, 2026): the weak-spot review's two
battle-pipeline rows, taken into the battle's finishing pass under the user's
"dont leave any open items" (`docs/BUG_FIXES.md` §WS).

WS-13  "outnumbered" and "outnumbering" — the +5 / −5 of authority, the glory
       point won against the odds, the aggressive marshal's no-stomp win — read
       the men each side put on the field (the lead and every corps that fought
       beside him, at the muster), the very figures the verdict's "numbers
       told" reads. Seam `combat_executor.outnumbered_is_read_on_the_field`.

WS-15  an attack that certainly struck no blow — refused for free, a war still
       to declare, the muster's confirm — puts back what the attack road's
       first stage spent: a first-turn drill, the counter-punch, a square (and
       what breaking it cleared), on every road. A march into an undefended
       province is a move and keeps them spent. Seam
       `combat_executor.a_refused_attack_spends_nothing`.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from backend.commands import combat_executor as ce
from backend.commands.combat_executor import CombatExecutor
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture(scope="module")
def opening():
    return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def world(opening):
    return WorldState.from_dict(opening.to_dict())


# ═══════════════════════════════ WS-13 ════════════════════════════════════

class TestTheOddsOfTheField:

    def test_the_field_men_decide_the_odds(self):
        assert ce._the_odds_of_the_field(
            {"field_attacker_strength": 64000, "field_defender_strength": 20000}, 4000, 20000) == (64000, 20000)

    def test_a_road_with_no_field_figures_keeps_the_leads(self):
        assert ce._the_odds_of_the_field({}, 4000, 20000) == (4000, 20000)

    def test_seam_down_the_leads_alone(self, monkeypatch):
        monkeypatch.setattr(ce, "outnumbered_is_read_on_the_field", lambda: False)
        assert ce._the_odds_of_the_field(
            {"field_attacker_strength": 64000, "field_defender_strength": 20000}, 4000, 20000) == (4000, 20000)

    def test_every_odds_read_of_the_pipeline_is_the_fields(self):
        src = inspect.getsource(CombatExecutor._post_combat_pipeline)
        assert "outnumbered = pre_atk < pre_def" not in src and "outnumbering = pre_atk > pre_def" not in src
        assert "outnumbered = odds_atk < odds_def" in src and "outnumbering = odds_atk > odds_def" in src
        assert "pre_attacker_strength=int(odds_atk)" in src, "the glory point reads the field"
        glory = src.split("check_battle_resolution(", 1)[1].split("attacker_participants", 1)[0]
        assert "int(odds_atk), int(odds_def)" in glory, "the aggressive marshal's no-stomp win reads the field"

    def test_the_field_battle_gives_its_committed_men(self):
        src = inspect.getsource(CombatExecutor._attack_advance_and_capture)
        assert "_the_committed_men(ctx)" in src

    def _won(self, world, monkeypatch, field):
        """France's small lead on a large stack beats a larger lead: does the
        throne take +5 for a field won against the odds?"""
        ex = CommandExecutor()
        lead, foe = world.marshals["Davout"], world.marshals["Mack"]
        lead.strength, foe.strength = 4000, 20000
        world.authority_tracker.authority = 50
        ctx = {
            "attacker": lead, "defender": foe, "defender_nation": foe.nation,
            "battle_region": lead.location, "outcome": "attacker_victory",
            "attacker_won": True, "defender_won": False,
            "attacker_casualties": 1500, "defender_casualties": 6000,
            "pre_battle_attacker_strength": 4000, "pre_battle_defender_strength": 20000,
            "battle_result": {"outcome": "attacker_victory"}, "conquered": False,
            "skip_log_battle_event": True, "skip_idle_reset": True, "skip_exhaustion": True,
            "skip_cannon_fire_record": True, "skip_war_damage": True, "skip_intel_update": True,
            "skip_coordination_clear": True, "skip_jealousy": True, "skip_combat_notifications": True,
        }
        if field:
            ctx.update(field_attacker_strength=64000, field_defender_strength=20000)
        ex._combat._post_combat_pipeline(ctx, world)
        return " | ".join(str(m.get("cause") or "") for m in (getattr(world.authority_tracker, "moves", None) or []))

    def test_a_small_lead_on_a_large_stack_wins_no_field_against_the_odds(self, world, monkeypatch):
        said = self._won(world, monkeypatch, field=True)
        assert "won against the odds" not in said and "Bulletin" in said, said

    def test_seam_down_he_did(self, world, monkeypatch):
        monkeypatch.setattr(ce, "outnumbered_is_read_on_the_field", lambda: False)
        assert "won against the odds" in self._won(world, monkeypatch, field=True)

    def test_without_the_field_figures_the_leads_still_read(self, world, monkeypatch):
        assert "won against the odds" in self._won(world, monkeypatch, field=False)


# ═══════════════════════════════ WS-15 ════════════════════════════════════

def _drilling(m, world):
    m.drilling = True
    m.drilling_locked = False
    m.drill_complete_turn = int(world.current_turn) + 2


class TestARefusedAttackSpendsNothing:

    def _refused(self, world):
        """An attack on a name nobody bears: refused before any blow, free."""
        ex = CommandExecutor()
        davout = world.marshals["Davout"]
        res = ex._combat._execute_attack(davout, "Nobody Of That Name", world, {"world": world})
        assert not res.get("success", False), res.get("message")
        return davout, res, ex

    def test_the_drill_stands(self, world):
        _drilling(world.marshals["Davout"], world)
        turn = world.marshals["Davout"].drill_complete_turn
        davout, _res, _ex = self._refused(world)
        assert davout.drilling is True and davout.drill_complete_turn == turn

    def test_the_counter_punch_stands(self, world):
        davout = world.marshals["Davout"]
        davout.counter_punch_available, davout.counter_punch_turns = True, 1
        self._refused(world)
        assert davout.counter_punch_available is True and davout.counter_punch_turns == 1

    def test_the_square_stands_and_says_nothing(self, world):
        davout = world.marshals["Davout"]
        davout.square_formation, davout.ai_square_cooldown = True, 0
        _d, res, ex = self._refused(world)
        assert davout.square_formation is True and davout.ai_square_cooldown == 0
        assert getattr(ex, "_pending_square_break", None) is None, "no notice of a square that was never broken"
        assert "Square broken" not in str(res.get("message") or "")

    def test_seam_down_the_old_road_spends_them(self, world, monkeypatch):
        monkeypatch.setattr(ce, "a_refused_attack_spends_nothing", lambda: False)
        davout = world.marshals["Davout"]
        _drilling(davout, world)
        davout.square_formation = True
        self._refused(world)
        assert davout.drilling is False and davout.square_formation is False

    def test_a_blow_struck_spends_them(self, world):
        """A real battle: the drill is dispersed and the square broken."""
        ex = CommandExecutor()
        davout, mack = world.marshals["Davout"], world.marshals["Mack"]
        for m in world.marshals.values():
            if m.name not in ("Davout", "Mack") and m.location == mack.location:
                m.location = "London" if m.nation != "Britain" else "Paris"
        davout.location = mack.location
        _drilling(davout, world)
        davout.square_formation = True
        res = ex._combat._execute_attack(davout, "Mack", world, {"world": world})
        if ce.attack_struck_no_blow(res):
            pytest.skip("the board staged a question first: " + str(res.get("message"))[:120])
        assert davout.drilling is False and davout.square_formation is False

    def test_the_typed_belt_reads_the_one_list(self):
        src = inspect.getsource(CommandExecutor)
        assert "attack_struck_no_blow(_res)" in src

    def test_the_no_blow_list(self):
        assert ce.attack_struck_no_blow({"success": False})
        assert ce.attack_struck_no_blow({"success": True, "war_purpose_popup": {"court": "Prussia"}})
        assert ce.attack_struck_no_blow({"success": True, "requires_input": True})
        assert ce.attack_struck_no_blow({"success": True, "occupation_started": True})
        assert not ce.attack_struck_no_blow({"success": True, "outcome": "attacker_victory"})
