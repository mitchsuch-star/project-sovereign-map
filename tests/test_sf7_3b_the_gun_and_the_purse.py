"""Score Finish Step 7 slice 3b (October 4, 2026) — the two rows slice 3's own
measurement found.

SF7-X2: the muster's expected figure priced an arriving gun corps at nothing
while the battle counts him whole (the resolver's Gate-4 block appends every
gun that answered to the participants, and the committed term sums him at
full weight). He rolls the same die as any reinforcer, and is priced at it.

SF7-X3: the counsel's build line looked only at a province with a corps on it
— AAR-18's counsel half, missed — so with the whole army abroad "what can I
do" named nothing to buy against any chest. Ground is broken without a corps.

    combat_executor.AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL
    counsel.THE_BUILD_LINE_NEEDS_NO_CORPS
"""

from __future__ import annotations

import random
import re

import pytest
from fastapi.testclient import TestClient

import backend.ai.counsel as CO
import backend.commands.combat_executor as CE
import backend.main as M
from backend.commands.parser import CommandParser


@pytest.fixture
def board(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


class TestTheGunIsWeighedByHisRoll:
    def test_the_levers_default_on(self):
        assert CE.AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL is True
        assert CO.THE_BUILD_LINE_NEEDS_NO_CORPS is True

    def test_his_weight_is_his_arrival_roll(self, board, monkeypatch):
        _, world = board
        combat = M.executor._combat
        ney, mack, lannes = (world.marshals[n] for n in ("Ney", "Mack", "Lannes"))
        assert lannes.location != mack.location
        lannes.artillery = True
        weight = combat._expected_arrival_weight(ney, lannes, world, mack.location)
        roll = combat._arrival_probability(
            combat._arrival_deterministic(lannes, ney, world),
            combat._arrival_threshold(lannes, ney, mack.location, world))
        assert weight == roll and weight > 0.0
        monkeypatch.setattr(CE, "AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL", False)
        assert combat._expected_arrival_weight(ney, lannes, world, mack.location) == 0.0

    def test_the_muster_prices_and_names_the_gun(self, board, monkeypatch):
        _, world = board
        combat = M.executor._combat
        ney, mack, lannes = (world.marshals[n] for n in ("Ney", "Mack", "Lannes"))
        lannes.artillery = True
        up = combat._build_muster_preview(ney, mack, world, {"world": world})
        row = next(r for r in up["rows"] if r["marshal"] == "Lannes")
        assert row["will_join"] and "arrival_odds" in row
        monkeypatch.setattr(CE, "AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL", False)
        down = combat._build_muster_preview(ney, mack, world, {"world": world})
        row_down = next(r for r in down["rows"] if r["marshal"] == "Lannes")
        assert "arrival_odds" not in row_down
        assert up["attacker"]["committed_strength"] > down["attacker"]["committed_strength"]
        # the ceiling never read the weight: unchanged either way
        assert up["attacker"]["ceiling_strength"] == down["attacker"]["ceiling_strength"]

    def test_the_census_rule_holds_with_a_gun(self, board, monkeypatch):
        """Every promised corps arriving, the ceiling is the battle's massed
        strength and the expectation sits beneath it — no longer a gun short."""
        client, _ = board
        found = None
        for seed in range(1, 60):
            M._reset_world_state()
            monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
            world = M.world
            world.marshals["Lannes"].artillery = True
            world.marshals["Murat"].location = "Paris"
            world.invalidate_bloc_members_cache()
            random.seed(seed)
            reply = client.post("/command", json={"command": "Ney, attack Mack"}).json()
            pv, ms = reply["muster_preview"], reply["massed_strength"]
            promised = {r["marshal"] for r in pv["rows"] if r["will_join"]}
            fought = set(ms["arrived"]) | set(ms["contributors"])
            if promised and promised <= fought:
                found = (pv["attacker"]["committed_strength"],
                         pv["attacker"]["ceiling_strength"], ms["total"])
                break
        assert found is not None
        expected, ceiling, massed = found
        assert ceiling == massed
        assert 0.85 * massed <= expected <= massed, found


class TestTheAISeesTheGunToo:
    """GR5: the enemy AI prices the same weight in its defender muster
    (`EnemyAI._muster_price` -> `_committed_reinforcement_strength(
    expected_at=...)`). Found by the hook on the FA slice-4 counter-punch
    board: Wellington (cautious, 20,000) beside a 5,000-man Ney at Paris,
    Drouot's 25,000 guns at Bordeaux next door. The gun answers at ~98%
    and the battle would sum him whole, so the free blow is declined; with
    the lever down he is priced at nothing and the blow is thrown into
    him."""

    @staticmethod
    def _board():
        import contextlib
        import io

        from backend.models.marshal import Stance
        from backend.models.world_state import WorldState

        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldState(player_nation="France")
        # the FA slice-2 `_war` idiom: the state alone, no cascade
        world.diplomatic_states["Britain|France"] = "WAR"
        world.war_start_turns["Britain|France"] = world.current_turn
        for m in world.marshals.values():
            if m.nation == "France":
                m.location = "Marseille"
        world.marshals["Ney"].location = "Paris"
        world.marshals["Ney"].strength = 5000
        world.marshals["Drouot"].location = "Bordeaux"
        wel = world.marshals["Wellington"]
        wel.location, wel.strength = "Belgium", 20000
        wel.stance = Stance.DEFENSIVE
        wel.fortified = False
        wel.counter_punch_available = True
        world.invalidate_active_nations_cache()
        world._build_marshal_index()
        world.calculate_visibility()
        assert wel.has_counter_punch()
        return world, wel

    @staticmethod
    def _blow(world, wel):
        import contextlib
        import io

        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor

        with contextlib.redirect_stdout(io.StringIO()):
            return EnemyAI(CommandExecutor())._get_counter_punch_action(
                wel, "Britain", world)

    def test_the_counter_punch_prices_the_gun_next_door(self, monkeypatch):
        world, wel = self._board()
        assert self._blow(world, wel) is None
        monkeypatch.setattr(CE, "AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL", False)
        world, wel = self._board()
        assert self._blow(world, wel) == {
            "marshal": "Wellington", "action": "attack", "target": "Ney"}


def _everyone_abroad(world):
    """Stage the commanded campaign's turn-20 shape: every French corps on
    soil France does not hold."""
    abroad = [name for name, region in world.regions.items()
              if getattr(region, "controller", None) not in (world.player_nation, None)]
    for i, marshal in enumerate(world.get_player_marshals()):
        marshal.location = abroad[i % len(abroad)]
    world.invalidate_bloc_members_cache()


class TestTheBuildLineNeedsNoCorps:
    def test_a_build_is_named_with_the_army_abroad(self, board, monkeypatch):
        _, world = board
        _everyone_abroad(world)
        assert CO._first_own_region_with_a_corps(world, "France") is None
        lines = CO.economy_counsel(world, "France", limit=2)
        assert any(line.startswith("build ") for line in lines), lines
        monkeypatch.setattr(CO, "THE_BUILD_LINE_NEEDS_NO_CORPS", False)
        assert not any(line.startswith("build ")
                       for line in CO.economy_counsel(world, "France", limit=2))

    def test_the_finder_is_the_desks_and_the_capital_comes_first(self, board):
        from backend.ai.question_desk import _first_own_region_that_can_build
        _, world = board
        _everyone_abroad(world)
        where = _first_own_region_that_can_build(world, "France")
        assert where == world.get_nation_capital("France")
        lines = CO._build_terms(world, "France", limit=2)
        assert lines and all(f" in {where} — " in line for line in lines), lines

    def test_what_can_i_do_names_it_on_the_wire(self, board):
        client, world = board
        _everyone_abroad(world)
        message = client.post("/command", json={"command": "what can I do"}).json()["message"]
        assert re.search(r"build [a-z ]+ in \w+ — [\d,]+g", message), message

    def test_a_corps_at_home_keeps_its_province(self, board):
        """With a corps on our own soil the line is byte-identical: his
        province, as before."""
        _, world = board
        home = CO._first_own_region_with_a_corps(world, "France")
        assert home is not None
        lines = CO._build_terms(world, "France", limit=2)
        assert lines and all(f" in {home} — " in line for line in lines), lines
