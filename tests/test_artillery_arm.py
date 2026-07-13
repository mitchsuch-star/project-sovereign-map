"""Artillery arm — filling the gap (docs/ARTILLERY_GAP_SPEC.md).

Before this pass the artillery arm was unreachable in the 1805 campaign: no
marshal carried it and the commission factory read only `cavalry`, so the
authored artillery manpower pools sat stranded. This slice makes the arm
reachable via the commission bench, drawn from the ARM-APPROPRIATE manpower
pool — which is also what makes artillery scarce (the pools are small) and
majors-favoured (France's pool is largest and her gunners are cheapest).

The artillery COMBAT mechanics (bombardment, +damage, fort degradation, the
tactical triangle) are pre-existing and covered by test_artillery.py /
test_bombardment.py in the legacy world; this file pins REACHABILITY +
the arm-aware manpower model + both-sides parity.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import recruitment as R
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)

MAJORS = ["France", "Austria", "Russia", "Prussia", "Britain"]


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


@pytest.fixture
def executor():
    return CommandExecutor()


def _commission(executor, world, name, nation=None):
    command = {"action": "recruit_marshal", "target": name, "type": "specific"}
    if nation:
        command["_acting_nation"] = nation
    return executor.execute({"command": command}, {"world": world})


def _artillery_candidates(world, nation):
    return [c for c in R.get_marshal_pool(world, nation) if c.get("artillery")]


# ═══════════════════════ REACHABILITY ══════════════════════════════════════


class TestReachability:
    def test_every_major_bench_has_a_gunner(self, world):
        for nation in MAJORS:
            arts = _artillery_candidates(world, nation)
            assert arts, f"{nation} has no artillery candidate"

    def test_no_active_marshal_starts_as_artillery(self, world):
        # Artillery enters via commission (a grand battery is raised), never
        # standing — the historically-clean choice (spec §3.2).
        assert not [m for m in world.marshals.values() if m.artillery]

    def test_france_is_favoured_two_cheaper_gunners(self, world):
        fr = _artillery_candidates(world, "France")
        assert {c["name"] for c in fr} == {"Marmont", "Senarmont"}
        cheapest_france = min(c["cost"] for c in fr)
        others = [c["cost"] for n in MAJORS if n != "France"
                  for c in _artillery_candidates(world, n)]
        # France's guns are the cheapest to raise + she has the most of them.
        assert cheapest_france <= min(others)
        assert len(fr) >= max(
            len(_artillery_candidates(world, n)) for n in MAJORS if n != "France")

    def test_france_has_the_largest_artillery_pool(self, world):
        fr = world.manpower_pools["France"]["artillery"]
        assert fr == 10000
        assert all(world.manpower_pools[n]["artillery"] < fr
                   for n in MAJORS if n != "France")


# ═══════════════════ ARM-AWARE MANPOWER (the fix) ══════════════════════════


class TestArmAwareManpower:
    def test_candidate_arm_classifies_all_three(self):
        assert R.candidate_arm({"artillery": True}) == "artillery"
        assert R.candidate_arm({"cavalry": True}) == "cavalry"
        assert R.candidate_arm({}) == "infantry"

    def test_corps_requirement_sizes(self):
        assert R.corps_requirement({"artillery": True}) == \
            ("artillery", R.RECRUIT_ARTILLERY_CORPS)
        assert R.corps_requirement({"cavalry": True}) == \
            ("cavalry", R.RECRUIT_CAVALRY_CORPS)
        assert R.corps_requirement({}) == ("infantry", R.RECRUIT_MARSHAL_CORPS)

    def test_artillery_commission_draws_from_artillery_pool(self, executor, world):
        world.nation_gold["France"] = 20000
        before = dict(world.manpower_pools["France"])
        result = _commission(executor, world, "Marmont")
        assert result["success"], result["message"]
        m = world.marshals["Marmont"]
        assert m.artillery is True
        assert m.strength == R.RECRUIT_ARTILLERY_CORPS
        # drew from ARTILLERY, left infantry + cavalry untouched
        assert world.manpower_pools["France"]["artillery"] == \
            before["artillery"] - R.RECRUIT_ARTILLERY_CORPS
        assert world.manpower_pools["France"]["infantry"] == before["infantry"]
        assert world.manpower_pools["France"]["cavalry"] == before["cavalry"]

    def test_cavalry_commission_draws_from_cavalry_pool(self, executor, world):
        world.nation_gold["Britain"] = 20000
        before = dict(world.manpower_pools["Britain"])
        result = _commission(executor, world, "Paget", nation="Britain")
        assert result["success"], result["message"]
        assert world.marshals["Paget"].cavalry is True
        assert world.manpower_pools["Britain"]["cavalry"] == \
            before["cavalry"] - R.RECRUIT_CAVALRY_CORPS
        assert world.manpower_pools["Britain"]["infantry"] == before["infantry"]

    def test_infantry_commission_unchanged(self, executor, world):
        world.nation_gold["France"] = 20000
        before = dict(world.manpower_pools["France"])
        result = _commission(executor, world, "Mortier")  # infantry
        assert result["success"], result["message"]
        assert world.manpower_pools["France"]["infantry"] == \
            before["infantry"] - R.RECRUIT_MARSHAL_CORPS
        assert world.manpower_pools["France"]["artillery"] == before["artillery"]


# ═══════════════════ SCARCITY (pool-gated) ═════════════════════════════════


class TestScarcity:
    def test_thin_artillery_pool_blocks_the_battery(self, world):
        """A small artillery pool (a minor's reality) cannot raise a battery,
        even with gold — the pool IS the scarcity gradient."""
        world.nation_gold["France"] = 20000
        world.manpower_pools["France"]["artillery"] = 2000  # < 3000 corps
        cand = R.find_candidate(world, "France", "Marmont")
        refusal = R.check_commission(world, "France", cand)
        assert refusal is not None
        assert "artillery" in refusal
        # ...while the full 10k pool clears it
        world.manpower_pools["France"]["artillery"] = 10000
        assert R.check_commission(world, "France", cand) is None


# ═══════════════════ BOTH-SIDES PARITY (GR5) ═══════════════════════════════


class TestParity:
    def test_ai_commissions_artillery_through_the_same_gate(self, executor, world):
        world.nation_gold["Austria"] = 20000
        result = _commission(executor, world, "Smola", nation="Austria")
        assert result["success"], result["message"]
        smola = world.marshals["Smola"]
        assert smola.nation == "Austria"
        assert smola.artillery is True
        assert smola.strength == R.RECRUIT_ARTILLERY_CORPS

    def test_ai_rung_can_reach_an_artillery_candidate(self, world):
        """find_ai_commission returns an artillery action when the gunner is
        the affordable pick (GR5 — the AI reads the same pool)."""
        world.marshal_pool["Austria"] = [
            R.find_candidate(world, "Austria", "Smola")]
        world.nation_gold["Austria"] = 20000
        world.marshals["ArchdukeJohn"].strength = 0  # under the standing cap
        action = R.find_ai_commission(
            world, "Austria", world.nation_gold["Austria"])
        assert action is not None
        assert action["action"] == "recruit_marshal"
        assert action["target"] == "Smola"


# ═══════════════════ GUARDS ════════════════════════════════════════════════


class TestGuards:
    def test_marshal_cannot_be_both_cavalry_and_artillery(self):
        with pytest.raises(ValueError):
            Marshal(name="X", location="Paris", personality="cautious",
                    strength=3000, cavalry=True, artillery=True)

    def test_commissioned_artillery_arm_reaches_the_object(self, executor, world):
        """The arm flag rides through create_marshal_from_data to the live
        Marshal — combat reads marshal.artillery, so the arm is live."""
        world.nation_gold["France"] = 20000
        _commission(executor, world, "Senarmont")
        assert world.marshals["Senarmont"].artillery is True
        assert world.marshals["Senarmont"].cavalry is False
