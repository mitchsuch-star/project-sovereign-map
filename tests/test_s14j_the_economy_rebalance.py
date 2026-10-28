"""S14j — the economy rebalance (October 27, 2026).

The user: "i mean a revalnce of amounts would fix it … lets actually fix this
economy before build too it shouldnt run away like this. in reall ife you need
to maintain conquests etc etc look into why its a runaway". Record:
`docs/audits/ECONOMY_REBALANCE_2026_10_27.md`; rules `SYSTEMS_REFERENCE.md`
§159; seams `tests/_oct27_seams.py::S14J_SEAMS_BY_ROW`; series
`tools/_s14j_series_arms_final.json`.

Three amounts, the same functions for every court (GR5):
  J1 a detached garrison keeps its pay — the field rate, in the base;
  J2 conquered soil costs 0.15 more of its base in every stability tier
     (pinned in `test_economy_es2_occupation.py`; IGR-E's judge unchanged);
  J3 the state's running cost — the Charges' crown term 30 → 250, and the
     AI's purse reads the Net before the Charges.
The opening is untouched: France's turn-1 bill stays 2,834 and every court
still charges 0 at boot.
"""
from pathlib import Path

import pytest

import backend.models.world_state as ws
from backend.game_logic import reforms
from backend.game_logic.ledger import _build_economy, why_the_bills_moved
from backend.models.marshal import Marshal
from backend.models.world_state import (
    CHARGES_CROWN_BASE, CHARGES_HOARD_FLOOR, EUROPE_UPKEEP_RATE,
    WAR_EFFORT_DIVISOR, WorldState,
)

SCENARIO_PATH = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def europe():
    """Bare Europe flag world with one 30,000-man French corps."""
    w = WorldState(player_nation="France", sovereign_map="europe")
    for name in [n for n, m in w.marshals.items() if m.nation == "France"]:
        del w.marshals[name]
    w.marshals["TestCorps"] = Marshal(
        name="TestCorps", location=w.get_nation_regions("France")[0],
        strength=30000, personality="cautious", nation="France")
    return w


def _detach(world, region_name, men):
    region = world.regions[region_name]
    region.garrison_strength = men
    region.garrison_detachment = True
    return region


class TestTheOpeningIsUntouched:
    def test_frances_turn_one_bill_is_the_shipped_one(self, world):
        upkeep = world.calculate_turn_upkeep("France")
        assert upkeep["total"] == 2834
        assert upkeep["garrison_pay"] == 0
        assert upkeep["garrison_men"] == 0

    def test_no_court_charges_at_boot(self, world):
        for nation in world.get_active_nations():
            assert world.calculate_state_charges(nation) == 0, nation

    def test_no_standing_garrison_is_billed(self, world):
        """The courts' capital garrisons (Paris 25,000, Vienna 25,000 …) stay
        unbilled: paying them drained ~2,200 a turn from the courts and the
        coalition stopped breaking the conquering France (measured)."""
        for nation in world.get_active_nations():
            assert world.calculate_turn_upkeep(nation)["garrison_pay"] == 0, nation


class TestJ1ADetachedGarrisonKeepsItsPay:
    def test_a_detached_garrison_draws_the_field_rate(self, europe):
        before = europe.calculate_turn_upkeep("France")
        region = _detach(europe, europe.get_nation_regions("France")[1], 3000)
        after = europe.calculate_turn_upkeep("France")
        assert after["garrison_pay"] == 3 * EUROPE_UPKEEP_RATE == 24
        assert after["garrison_men"] == 3000
        assert after["base"] - before["base"] == 24
        assert after["total"] == after["base"] + after["surcharge"]
        # outside the fielded strength: the force limit and the premium read
        # the field army only
        assert after["total_strength"] == before["total_strength"] == 30000
        region.garrison_detachment = False
        assert europe.calculate_turn_upkeep("France")["garrison_pay"] == 0

    def test_the_garrison_verb_moves_the_men_and_not_the_bill(self, europe):
        """A corps that detaches 3,000 men pays the same a turn: 27,000 in the
        field and 3,000 in garrison (before S14j the bill fell by 24)."""
        from backend.commands.executor import CommandExecutor
        before = europe.calculate_turn_upkeep("France")["total"]
        marshal = europe.marshals["TestCorps"]
        result = CommandExecutor()._economy._execute_garrison(
            {"action": "garrison", "marshal": "TestCorps", "target": marshal.location},
            {"world": europe})
        assert result.get("success"), result
        after = europe.calculate_turn_upkeep("France")
        assert after["total_strength"] == 27000
        assert after["garrison_men"] == 3000
        assert after["total"] == before

    def test_the_seam_holds_it_down(self, europe, monkeypatch):
        _detach(europe, europe.get_nation_regions("France")[1], 3000)
        monkeypatch.setattr(ws, "garrisons_draw_pay", lambda *a, **k: False)
        upkeep = europe.calculate_turn_upkeep("France")
        assert upkeep["garrison_pay"] == 0
        assert upkeep["base"] == 30 * EUROPE_UPKEEP_RATE

    def test_the_ledger_note_names_the_garrison(self, world):
        name = world.get_nation_regions("France")[3]
        _detach(world, name, 6000)
        upkeep = world.calculate_turn_upkeep("France")
        note = why_the_bills_moved(world, "France", upkeep, 0)["upkeep_note"]
        assert "and 6,000 in garrison" in note, note

    def test_a_granted_province_relieves_its_garrisons_pay(self, world):
        from backend.game_logic.vassal import province_grant_price, province_price_line
        name = world.get_nation_regions("France")[0]
        region = _detach(world, name, 6000)
        parts = province_grant_price(world, "France", "Holland", name)
        assert parts["garrison_relieved"] == 6 * EUROPE_UPKEEP_RATE
        assert "48g of its garrison's pay relieved" in province_price_line(parts)
        region.garrison_detachment = False
        assert province_grant_price(world, "France", "Holland", name)["garrison_relieved"] == 0


class TestJ3TheStatesRunningCost:
    def test_the_crown_is_250(self):
        assert CHARGES_CROWN_BASE == 250
        assert ws.charges_crown_rate() == 250

    def test_a_peaceful_chest_levels_off_near_ten_turns_of_its_surplus(self):
        """The plateau the ledger names: FLOOR + surplus × DIVISOR / rate. At
        the crown alone (a golden peace) that is 2,000 + 10 × the surplus — a
        France banking 3,800 a turn levels near 40,000 (was 318,666 at 30)."""
        from backend.game_logic.ledger import state_charges_ceiling
        assert state_charges_ceiling(3800, CHARGES_CROWN_BASE) == 40_000
        assert state_charges_ceiling(3800, 30) == 318_666
        assert CHARGES_HOARD_FLOOR + 3800 * WAR_EFFORT_DIVISOR // CHARGES_CROWN_BASE == 40_000

    def test_a_rich_court_still_arms_at_war(self, world):
        """The AI's purse reads the Net before the Charges: Britain at war on
        60,000 arms past its establishment. With the plain read its forecast
        Net is negative (the Charges draw on the hoard) and it refused."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        world.nation_gold["Britain"] = 60_000
        assert _build_economy(world, "Britain")["net"] < 0
        ai = EnemyAI(CommandExecutor())
        order = ai._court_arms_with_its_purse("Britain", world)
        assert order is not None and order["action"] == "recruit"

    def test_the_plain_read_refuses_the_rich_court(self, world, monkeypatch):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        monkeypatch.setattr(reforms, "ai_reads_net_before_charges", lambda *a, **k: False)
        world.nation_gold["Britain"] = 60_000
        ai = EnemyAI(CommandExecutor())
        assert ai._court_arms_with_its_purse("Britain", world) is None

    def test_the_laws_rung_reads_before_the_charges(self, world, monkeypatch):
        """`find_ai_enactment` passes the read to the purse test, so a rich
        court is not refused a law for being rich."""
        seen = []
        real = reforms.ai_purse_refusal

        def spy(*args, **kwargs):
            seen.append(kwargs.get("net_before_charges"))
            return real(*args, **kwargs)

        monkeypatch.setattr(reforms, "ai_purse_refusal", spy)
        world.nation_gold["Austria"] = 40_000
        reforms.find_ai_enactment(world, "Austria", 40_000, 2)
        assert seen and all(flag is True for flag in seen), seen
