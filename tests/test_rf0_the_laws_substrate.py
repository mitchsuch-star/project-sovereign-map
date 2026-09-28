"""SR-5r RF-0 — the laws' substrate (`docs/REFORMS_SPEC.md` §1, §2, §4, §5,
§10, §12; gate record §0 RULED, readings §0.1 CONFIRMED September 27, 2026).

RF-0 lands the store and the rules, and changes no behaviour:
  * `backend/game_logic/reforms.py` — the closed effect-type set (§4), the
    deck/in-force readers, `law_upkeep_bill`, `staff_actions`,
    `law_refusal` (the ONE predicate for the verb, its chip, the AI rung and
    the preview — §2) and `restoration_price` (R8 "The Arrears", the ONE
    price every surface quotes);
  * the scenario key `reforms` — each great power's Staff (§5: one
    `actions` law, one price for every court), nothing in force (§1);
  * the validator block (§1/§4: closed set, wired types only, ≤2 clauses,
    one Staff per court at one price, no in-force state in a scenario);
  * ONE serialized world field `reforms` (§10), backfilled at load for a
    pre-reform 1805 save only (the doctrines review, `DOCTRINES_SPEC.md` §9).
No verb exists yet (RF-1), so no law can be enacted: `BASELINE_SERIES` and
M1–M7 cannot move.
"""

import copy
import json
from pathlib import Path

import pytest

from backend import save_manager
from backend.game_logic import reforms as R
from backend.modding.validator import validate_scenario
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@pytest.fixture(scope="module")
def scenario():
    with open(SCENARIO, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO))


def _staff(world, nation):
    return next(r for r in R.deck(world, nation)
                if any(c.get("type") == "actions" for c in r["effects"]))


# ═══════════════════════ the authored catalogue ═════════════════════════════

class TestTheAuthoredCatalogue:

    def test_five_decks_the_great_powers_only(self, scenario):
        block = scenario["reforms"]
        assert set(block) == set(R.GREAT_POWERS)

    def test_one_staff_per_court_one_price_for_all(self, scenario):
        terms = set()
        for court, rows in scenario["reforms"].items():
            staffs = [r for r in rows
                      if any(c.get("type") == "actions" for c in r["effects"])]
            assert len(staffs) == 1, court
            s = staffs[0]
            terms.add((s["currency"], s["price"], s["upkeep"]))
            assert s["effects"] == [{"type": "actions", "value": 1}]
        assert terms == {("gold", 9000, 300)}, "§5: one price for every court"

    def test_nothing_is_in_force_at_boot(self, scenario, world):
        for rows in scenario["reforms"].values():
            for row in rows:
                assert "enacted_turn" not in row and "lapsed_turn" not in row
        for nation in R.GREAT_POWERS:
            assert R.laws_in_force(world, nation) == []
            assert R.law_upkeep_bill(world, nation) == 0
            assert R.staff_actions(world, nation) == 0

    def test_the_staff_counts_once_in_force(self, world):
        """In force, the Staff mints its one action and bills its upkeep —
        derived from the row, never written anywhere else (§2)."""
        _staff(world, "Austria")["enacted_turn"] = 5
        assert R.staff_actions(world, "Austria") == 1
        assert R.law_upkeep_bill(world, "Austria") == 300
        assert R.staff_actions(world, "France") == 0, "one court's law is its own"
        assert [r["id"] for r in R.laws_in_force(world, "Austria")] == ["corps_d_armee"]

    def test_the_rivals_name_what_they_copy(self, scenario):
        """Q7: the rivals' descriptions name what they copy from France."""
        for court in ("Austria", "Prussia", "Russia", "Britain"):
            says = scenario["reforms"][court][0]["says"]
            assert "French" in says or "France" in says, court

    def test_the_scenario_validates_clean(self, scenario):
        result = validate_scenario(copy.deepcopy(scenario))
        errs = [str(e) for e in result.errors if "reforms" in str(e)]
        assert not errs, errs


# ═══════════════════════ the validator ══════════════════════════════════════

def _with(scenario, mutate):
    data = copy.deepcopy(scenario)
    mutate(data["reforms"])
    return [str(e) for e in validate_scenario(data).errors if "reforms" in str(e)]


class TestTheValidator:

    def test_in_force_state_is_refused_in_a_scenario(self, scenario):
        errs = _with(scenario, lambda b: b["France"][0].__setitem__("enacted_turn", 1))
        assert errs and any("in force" in e for e in errs)
        errs = _with(scenario, lambda b: b["France"][0].__setitem__("lapsed_turn", 1))
        assert errs

    def test_an_unwired_effect_type_is_refused(self, scenario):
        unwired = next(t for t in R.EFFECT_TYPES if t not in R.WIRED_EFFECT_TYPES)
        errs = _with(scenario, lambda b: b["France"].append({
            "id": "x", "name": "X", "date": "1806", "currency": "gold",
            "price": 100, "upkeep": 10, "says": "x",
            "effects": [{"type": unwired}]}))
        assert errs and any("not wired" in e for e in errs)

    def test_an_unknown_effect_type_is_refused(self, scenario):
        errs = _with(scenario, lambda b: b["France"][0]["effects"].append(
            {"type": "research"}))
        assert errs

    def test_three_clauses_are_refused(self, scenario):
        errs = _with(scenario, lambda b: b["France"][0].__setitem__(
            "effects", [{"type": "actions", "value": 1}] * 3))
        assert errs

    def test_two_staffs_are_refused(self, scenario):
        def two(b):
            extra = copy.deepcopy(b["France"][0])
            extra["id"] = "second_staff"
            b["France"].append(extra)
        assert _with(scenario, two)

    def test_an_unequal_staff_price_is_refused(self, scenario):
        assert _with(scenario, lambda b: b["Austria"][0].__setitem__("price", 8000))

    def test_an_unknown_currency_is_refused(self, scenario):
        assert _with(scenario, lambda b: b["France"][0].__setitem__("currency", "credit"))

    def test_a_missing_field_is_refused(self, scenario):
        assert _with(scenario, lambda b: b["France"][0].pop("says"))


# ═══════════════════════ law_refusal — ONE predicate ════════════════════════

class TestTheOnePredicate:

    def test_a_law_the_court_can_afford_passes(self, world):
        world.nation_gold["France"] = 9000
        world.admin_actions_remaining = 1
        assert R.law_refusal(world, "France", "grand_quartier_general") == ""

    def test_not_this_courts_law(self, world):
        assert "not one of France's laws" in R.law_refusal(
            world, "France", "corps_d_armee")

    def test_already_in_force(self, world):
        _staff(world, "France")["enacted_turn"] = 3
        assert "already in force (since turn 3)" in R.law_refusal(
            world, "France", "grand_quartier_general")

    def test_the_price(self, world):
        world.nation_gold["France"] = 8999
        world.admin_actions_remaining = 2
        msg = R.law_refusal(world, "France", "grand_quartier_general")
        assert "costs 9,000 gold; the treasury holds 8,999" in msg

    def test_no_admin_action_left(self, world):
        world.nation_gold["France"] = 20000
        world.admin_actions_remaining = 0
        assert "admin action" in R.law_refusal(world, "France", "grand_quartier_general")

    def test_the_ai_passes_its_own_admin_budget(self, world):
        world.nation_gold["Austria"] = 20000
        assert R.law_refusal(world, "Austria", "corps_d_armee", admin_actions=1) == ""
        assert "admin action" in R.law_refusal(
            world, "Austria", "corps_d_armee", admin_actions=0)

    def test_lever_down_the_state_has_no_laws(self, world, monkeypatch):
        monkeypatch.setattr(R, "THE_STATE_HAS_LAWS", False)
        _staff(world, "France")["enacted_turn"] = 1
        assert R.laws_in_force(world, "France") == []
        assert R.staff_actions(world, "France") == 0
        assert R.law_refusal(world, "France", "grand_quartier_general") != ""


# ═══════════════════════ R8 "The Arrears" ═══════════════════════════════════

class TestTheArrears:

    @pytest.mark.parametrize("dead,price,arrears", [
        (1, 4500, 300), (5, 4500, 1500), (10, 4500, 3000)])
    def test_the_worked_example(self, world, dead, price, arrears):
        staff = _staff(world, "France")
        world.current_turn = 20
        staff["lapsed_turn"] = 20 - dead + 1
        q = R.restoration_price(world, "France", staff)
        assert q["kind"] == "restore"
        assert (q["price"], q["arrears"]) == (price, arrears)
        assert q["price"] + q["arrears"] == {1: 4800, 5: 6000, 10: 7500}[dead]

    def test_on_the_eleventh_turn_it_has_dispersed(self, world):
        staff = _staff(world, "France")
        world.current_turn = 20
        staff["lapsed_turn"] = 10          # 11 dead turns
        q = R.restoration_price(world, "France", staff)
        assert q["kind"] == "enact" and q["price"] == 9000 and q["arrears"] == 0

    def test_a_repealed_law_costs_its_full_price(self, world):
        q = R.restoration_price(world, "France", _staff(world, "France"))
        assert (q["kind"], q["price"], q["arrears"]) == ("enact", 9000, 0)

    def test_the_refusal_reads_the_arrears_price(self, world):
        staff = _staff(world, "France")
        world.current_turn = 20
        staff["lapsed_turn"] = 20
        world.admin_actions_remaining = 1
        world.nation_gold["France"] = 4799
        assert "costs 4,800 gold" in R.law_refusal(world, "France", staff["id"])
        world.nation_gold["France"] = 4800
        assert R.law_refusal(world, "France", staff["id"]) == ""

    def test_an_authority_law_restores_for_half_its_authority(self, world):
        row = {"id": "t", "name": "T", "currency": "authority", "price": 15,
               "upkeep": 150, "effects": [], "lapsed_turn": 5}
        world.current_turn = 7                # 3 dead turns
        q = R.restoration_price(world, "France", row)
        assert (q["currency"], q["price"], q["arrears"]) == ("authority", 8, 450)


# ═══════════════════════ the store: save, legacy, backfill ══════════════════

class TestTheStore:

    def test_the_round_trip_keeps_in_force_state(self, world):
        staff = _staff(world, "France")
        staff["enacted_turn"] = 4
        _staff(world, "Austria")["lapsed_turn"] = 6
        loaded = WorldState.from_dict(world.to_dict())
        assert _staff(loaded, "France")["enacted_turn"] == 4
        assert _staff(loaded, "Austria")["lapsed_turn"] == 6
        assert _staff(loaded, "France") is not staff, "deep-copied (no aliasing)"

    def test_the_legacy_world_has_no_laws(self):
        legacy = WorldState(player_nation="France")
        assert legacy.reforms == {}
        assert "reforms" in legacy.to_dict()

    def test_a_pre_reform_1805_save_is_backfilled(self, world):
        world.reforms = {}
        save_manager._backfill_reforms(world)
        assert set(world.reforms) == set(R.GREAT_POWERS)
        assert R.laws_in_force(world, "France") == []

    def test_an_armed_save_is_never_overwritten(self, world):
        _staff(world, "France")["enacted_turn"] = 9
        save_manager._backfill_reforms(world)
        assert _staff(world, "France")["enacted_turn"] == 9

    def test_a_tutorial_save_receives_no_deck(self, world):
        world.reforms = {}
        world.scenario_name = "tutorial"
        save_manager._backfill_reforms(world)
        assert world.reforms == {}

    def test_a_legacy_save_receives_no_deck(self):
        legacy = WorldState(player_nation="France")
        save_manager._backfill_reforms(legacy)
        assert legacy.reforms == {}

    def test_the_committed_fixture_loads_armed(self):
        """The committed t20 fixture is a genuine pre-reform 1805 save."""
        fixture = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_t20_ambient.json"
        with open(fixture, encoding="utf-8") as fh:
            assert "reforms" not in json.load(fh)["world_state"]
        loaded = save_manager.load_game(fixture)
        assert loaded["success"], loaded["message"]
        world = loaded["world"]
        assert set(world.reforms) == set(R.GREAT_POWERS)
        assert all(R.laws_in_force(world, n) == [] for n in R.GREAT_POWERS)
