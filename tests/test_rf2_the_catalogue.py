"""SR-5r RF-2 — "The catalogue" (`docs/REFORMS_SPEC.md` §4, §6, §11 T1/T2/T8;
gate record §0 RULED September 27, 2026).

RF-2 wires the other eight effect types, each on ONE existing source that both
applies it and is quoted by every surface (shown = applied), each naming its
law where it applies (T8), each the same rule for the player and every AI court
(GR5), and authors the catalogue: 25 laws, five decks (the Train des Équipages
joins France's at Chunk 7 as a doctrine cure).

  * manpower_regen    → `WorldState.get_manpower_regen_rates` (last, after the
                        war exhaustion); the treasury report and the ledger's
                        manpower rows read and name it;
  * recruit_price     → `EconomyExecutor._recruit_cost_terms` on the DRAFT only
                        (the RV-17 rule: never the substitute market), named on
                        the terms list, before the Intendance;
  * recruit_morale    → on the draft's green-conscript base, before the
                        training ground's rung and Moore's floor (void there);
  * drill_morale      → `WorldState.drill_morale_gain` (the drill, the
                        dispatch's remedy line and the build chip);
  * supply_capacity   → the FED multiplier in `_supply_multiplier` only;
  * satellite_loyalty → ONE reader for the loyalty tick AND its forecast;
  * cs_closure        → `naval.closure_against`'s client arm (the Berlin
                        Decree counts every client, whatever its autonomy);
  * blockade_denial   → inside `naval.blockade_trade_loss`, the BLOCKADER's
                        law; the five "halved" copies read one phrase.
Lever `reforms.THE_STATE_HAS_LAWS` — down, no law is in force anywhere.
"""
import contextlib
import copy
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend import campaign_log as CL
from backend.commands.economy_executor import (
    EconomyExecutor, INFANTRY_RECRUIT_GOLD_COST_BASE, ARTILLERY_RECRUIT_GOLD_COST_BASE,
    substitute_arrival_morale)
from backend.game_logic import naval as N
from backend.game_logic import reforms as R
from backend.game_logic.ledger import _build_economy, _build_manpower
from backend.game_logic.vassal import (
    AUTONOMY_AUTONOMOUS, forecast_vassal_loyalty, process_vassal_loyalty)
from backend.modding.validator import validate_scenario
from tests import _chip_census as C

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


@pytest.fixture
def client(world):
    return TestClient(M.app)


def post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


def law(world, nation, law_id):
    return R.find_law(world, nation, law_id)


def enact(world, nation, law_id):
    """Put a law in force the way the verb does (charges its price)."""
    world.nation_gold[nation] = int(world.nation_gold.get(nation, 0)) + 20000
    row = law(world, nation, law_id)
    assert row is not None, (nation, law_id)
    R.enact_law(world, nation, row)
    return row


def add_law(world, nation, law_id, effects, upkeep=100):
    row = {"id": law_id, "name": f"The {law_id.replace('_', ' ').title()}",
           "date": "1806", "currency": "gold", "price": 1000, "upkeep": upkeep,
           "effects": effects, "says": "test law"}
    world.reforms[nation].append(row)
    world.nation_gold[nation] = int(world.nation_gold.get(nation, 0)) + 5000
    R.enact_law(world, nation, row)
    return row


def ex():
    return EconomyExecutor(None)


# ═══════════════════════════════ THE CATALOGUE ════════════════════════════════

class TestTheCatalogue:

    @pytest.fixture(scope="class")
    def scenario(self):
        return json.loads(SCENARIO.read_text(encoding="utf-8"))

    def test_twenty_six_laws_five_decks(self, scenario):
        # SR-7d "The Doctrines" (October 3, 2026): the Train des Équipages joined France's
        # deck at DC-2 (D-R3) — 25 laws became 26.
        decks = {c: rows for c, rows in scenario["reforms"].items() if not c.startswith("_")}
        assert set(decks) == set(R.GREAT_POWERS)
        assert {c: len(rows) for c, rows in decks.items()} == {
            "France": 6, "Austria": 5, "Prussia": 5, "Russia": 5, "Britain": 5}

    def test_the_train_arrived_with_the_doctrines(self, scenario):
        """RE-SEATED by SR-7d "The Doctrines" (October 3, 2026): the pin that held the Train
        back until Chunk 7 now holds that it arrived — a cure only (D-R3), with
        `cures` wired to the doctrine's seam (DC-2)."""
        train = next(r for r in scenario["reforms"]["France"] if r["id"] == "train_des_equipages")
        assert train["effects"] == [{"type": "cures", "flaw": "Living off the land"}]
        assert "cures" in R.WIRED_EFFECT_TYPES

    def test_every_type_the_catalogue_uses_is_wired(self, scenario):
        used = {c["type"] for rows in scenario["reforms"].values() if isinstance(rows, list)
                for r in rows for c in r["effects"]}
        assert used == set(R.WIRED_EFFECT_TYPES)

    def test_the_three_pricing_rules(self, scenario):
        for court, rows in scenario["reforms"].items():
            if court.startswith("_"):
                continue
            for r in rows:
                if R.is_staff(r):
                    assert (r["price"], r["upkeep"]) == (9000, 300)
                elif r["currency"] == "authority":
                    assert r["price"] == 15, (court, r["id"])
                assert 100 <= r["upkeep"] <= 300, (court, r["id"])

    def test_the_scenario_validates_clean(self, scenario):
        assert validate_scenario(scenario).is_valid

    @pytest.mark.parametrize("court,expected", [
        # SR-7d "The Doctrines" (October 3, 2026): the Train second, beside the Staff it needs.
        ("France", ["grand_quartier_general", "train_des_equipages", "artillery_reserve",
                    "anticipated_class", "berlin_decree", "code_abroad"]),
        ("Britain", ["horse_guards_reforms", "orders_in_council", "militia_transfer",
                     "commissariat", "congreve_rockets"]),
    ])
    def test_deck_order_is_authored(self, scenario, court, expected):
        assert [r["id"] for r in scenario["reforms"][court]] == expected


class TestTheClauseShapes:

    @pytest.fixture
    def scenario(self):
        return json.loads(SCENARIO.read_text(encoding="utf-8"))

    def _set(self, scenario, clause):
        # SR-7d "The Doctrines" (October 3, 2026): France's second law is the Train (a cure
        # the doctrine cross-check guards); the shape probe writes the third.
        scenario["reforms"]["France"][2]["effects"] = [clause]
        return validate_scenario(scenario)

    @pytest.mark.parametrize("clause", [
        {"type": "manpower_regen", "pool": "cavalry", "value": 25},
        {"type": "manpower_regen", "pool": "infantry", "value": 0},
        {"type": "recruit_price", "arm": "navy", "value": 0.9},
        {"type": "recruit_price", "arm": "all", "value": 1.0},
        {"type": "recruit_morale", "arm": "infantry", "value": 40},
        {"type": "drill_morale", "value": 5.5},
        {"type": "supply_capacity", "value": 0.8},
        {"type": "satellite_loyalty", "value": 9},
        {"type": "cs_closure", "rule": "every_port"},
        {"type": "blockade_denial", "value": 3.0},
        {"type": "drill_morale", "value": 5, "arm": "infantry"},
        {"type": "recruit_price", "value": 0.9},
    ])
    def test_a_bad_clause_is_refused(self, scenario, clause):
        assert not self._set(scenario, clause).is_valid

    def test_a_good_clause_passes(self, scenario):
        assert self._set(scenario, {"type": "recruit_price", "arm": "all", "value": 0.9}).is_valid


# ═══════════════════════════════ 1. MANPOWER ══════════════════════════════════

class TestManpowerRegen:

    def test_the_rate_the_tick_applies(self, world):
        before = world.get_manpower_regen_rates("France")
        enact(world, "France", "anticipated_class")
        after = world.get_manpower_regen_rates("France")
        assert after["infantry"] == before["infantry"] * 125 // 100
        assert after["cavalry"] == before["cavalry"]
        world.manpower_pools["France"]["infantry"] = 0
        with _quiet():
            world._process_manpower_regen()
        assert world.manpower_pools["France"]["infantry"] == after["infantry"]

    def test_it_applies_after_the_war_exhaustion(self, world):
        world.war_exhaustion["France"] = 100
        halved = world.get_manpower_regen_rates("France")["infantry"]
        enact(world, "France", "anticipated_class")
        assert world.get_manpower_regen_rates("France")["infantry"] == halved * 125 // 100

    def test_gr5_an_ai_court_the_same(self, world):
        before = world.get_manpower_regen_rates("Austria")["infantry"]
        enact(world, "Austria", "landwehr")
        assert world.get_manpower_regen_rates("Austria")["infantry"] == before * 125 // 100

    def test_the_treasury_report_names_it_and_quotes_the_applied_rate(self, world, client):
        world.war_exhaustion["France"] = 100
        enact(world, "France", "anticipated_class")
        rate = world.get_manpower_regen_rates("France")["infantry"]
        r = post(client, "show me the treasury")
        assert f"(+{rate:,}/turn — +25% by the Anticipated Class)" in r["message"], r["message"]

    def test_the_ledger_row_names_it(self, world):
        enact(world, "France", "anticipated_class")
        rows = _build_manpower(world, "France")
        assert rows["infantry"]["regen_terms"] == [["the Anticipated Class", 25]]
        assert rows["cavalry"]["regen_terms"] == []


# ═══════════════════════════════ 2. RECRUIT PRICE ═════════════════════════════

class TestRecruitPrice:

    def _price(self, world, nation, arm, base, draft=True, marshal=None):
        region = world.get_region(world.get_nation_capital(nation))
        return ex()._recruit_cost_terms(region, world, base_cost=base, nation=nation,
                                        marshal=marshal, arm=arm, draft=draft)

    def test_the_law_prices_its_arm_and_names_itself(self, world):
        before, _t = self._price(world, "France", "artillery", ARTILLERY_RECRUIT_GOLD_COST_BASE)
        inf_before, _ = self._price(world, "France", "infantry", INFANTRY_RECRUIT_GOLD_COST_BASE)
        enact(world, "France", "artillery_reserve")
        after, terms = self._price(world, "France", "artillery", ARTILLERY_RECRUIT_GOLD_COST_BASE)
        assert after == int(round(before * 0.85))
        assert "×0.85 by the Artillery Reserve" in terms
        inf_after, _ = self._price(world, "France", "infantry", INFANTRY_RECRUIT_GOLD_COST_BASE)
        assert inf_after == inf_before

    @pytest.mark.parametrize("arm,base", [
        ("infantry", INFANTRY_RECRUIT_GOLD_COST_BASE),
        ("artillery", ARTILLERY_RECRUIT_GOLD_COST_BASE),
    ])
    def test_the_arm_is_read_from_the_base_when_not_given(self, world, arm, base):
        """A caller that names no arm and no marshal (the ledger at the
        capital, the levy status) is priced by the arm of the base it asks
        at — a law on that arm applies."""
        add_law(world, "France", f"{arm}_act", [{"type": "recruit_price", "arm": arm, "value": 0.8}])
        region = world.get_region("Paris")
        explicit = ex()._calculate_recruit_cost(region, world, base_cost=base,
                                                nation="France", arm=arm)
        inferred = ex()._calculate_recruit_cost(region, world, base_cost=base,
                                                nation="France")
        R.repeal_law(world, "France", law(world, "France", f"{arm}_act"))
        bare = ex()._calculate_recruit_cost(region, world, base_cost=base, nation="France")
        assert explicit == inferred < bare

    def test_the_substitute_market_is_never_priced_by_a_law(self, world):
        from backend.commands.economy_executor import levy_substitute_price
        base = levy_substitute_price(world, "France")
        before, _ = self._price(world, "France", None, base, draft=False)
        add_law(world, "France", "all_arms_act", [{"type": "recruit_price", "arm": "all", "value": 0.9}])
        after, terms = self._price(world, "France", None, base, draft=False)
        assert after == before and not any("by the" in t for t in terms)

    def _room(self, world):
        """The substitute market buys back only what we have lost: open it."""
        davout = world.marshals["Davout"]
        davout.strength = max(1000, int(davout.strength) - 15000)
        world.nation_gold["France"] = 50000

    def test_the_substitute_chip_is_never_priced_by_a_law(self, world):
        from backend.commands.economy_executor import substitute_quote
        self._room(world)
        before = substitute_quote(world, "Rhineland")
        assert before.get("price"), before
        add_law(world, "France", "all_arms_act", [{"type": "recruit_price", "arm": "all", "value": 0.8}])
        world.nation_gold["France"] = 50000
        assert substitute_quote(world, "Rhineland")["price"] == before["price"]

    def test_the_substitute_purchase_is_never_priced_by_a_law(self, world, client):
        from backend.commands.economy_executor import substitute_quote
        self._room(world)
        quote = substitute_quote(world, "Rhineland")
        quoted, recipient = quote["price"], quote["recipient"]
        add_law(world, "France", "all_arms_act", [{"type": "recruit_price", "arm": "all", "value": 0.8}])
        world.nation_gold["France"] = 50000
        r = post(client, f"buy substitutes for {recipient}")
        assert r["success"] is True, r.get("message")
        assert 50000 - world.nation_gold["France"] == quoted

    def test_the_executor_charges_the_quoted_price_and_names_the_law(self, world, client):
        add_law(world, "France", "all_arms_act", [{"type": "recruit_price", "arm": "all", "value": 0.9}])
        world.nation_gold["France"] = 50000
        from backend.commands.economy_executor import recruit_quote
        quote = recruit_quote(world, "Rhineland", arm="infantry")
        assert quote.get("ok"), quote
        assert "×0.9 by the All Arms Act" in quote["price_terms"]
        gold = world.nation_gold["France"]
        r = post(client, "recruit infantry in Rhineland")
        assert r["success"] is True, r.get("message")
        assert gold - world.nation_gold["France"] == quote["price"]
        assert "(×0.9 by the All Arms Act)" in r["message"]

    def test_gr5_the_ai_prices_through_the_same_seam(self, world):
        enact(world, "Austria", "generalissimus")
        mack = world.marshals["Mack"]
        region = world.get_region(mack.location) or world.get_region("Vienna")
        base = INFANTRY_RECRUIT_GOLD_COST_BASE
        with_law = ex()._calculate_recruit_cost(region, world, base_cost=base, nation="Austria", marshal=mack)
        R.repeal_law(world, "Austria", law(world, "Austria", "generalissimus"))
        without = ex()._calculate_recruit_cost(region, world, base_cost=base, nation="Austria", marshal=mack)
        assert with_law < without

    def test_an_authority_law_moves_the_remedy_cache(self, world):
        """A law bought with authority moves every draft price without
        moving the chest — the remedy's memo must not serve the old one."""
        from backend.commands.economy_executor import recruit_remedy
        row = {"id": "authority_act", "name": "The Authority Act", "date": "1806",
               "currency": "authority", "price": 15, "upkeep": 100,
               "effects": [{"type": "recruit_price", "arm": "all", "value": 0.8}],
               "says": "test law"}
        world.reforms["France"].append(row)
        world.nation_gold["France"] = 50000
        with _quiet():
            before = copy.deepcopy(recruit_remedy(world, "France"))
        key_before = world._recruit_remedy_cache[0]
        row["enacted_turn"] = world.current_turn   # in force; the chest untouched
        assert world.nation_gold["France"] == 50000
        with _quiet():
            after = recruit_remedy(world, "France")
        assert world._recruit_remedy_cache[0] != key_before
        assert after != before, "the memo served the price the law had moved"


# ═══════════════════════════════ 3. RECRUIT MORALE ════════════════════════════

class TestRecruitMorale:

    def _recruit(self, client, world):
        world.nation_gold["France"] = 50000
        return post(client, "recruit infantry in Rhineland")

    def test_the_law_raises_the_draft_and_names_itself(self, world, client):
        add_law(world, "France", "jager_act", [{"type": "recruit_morale", "arm": "infantry", "value": 10}])
        r = self._recruit(client, world)
        assert r["success"] is True, r.get("message")
        assert "The Jager Act: infantry recruits muster at 50, not 40." in r["message"]

    def test_a_training_ground_voids_it(self, world, client):
        add_law(world, "France", "jager_act", [{"type": "recruit_morale", "arm": "infantry", "value": 10}])
        world.get_region("Rhineland").buildings.append(
            {"type": "training_ground", "damaged": False})
        assert world.get_region("Rhineland").has_building("training_ground")
        r = self._recruit(client, world)
        assert r["success"] is True, r.get("message")
        assert "muster at" not in r["message"]

    def test_a_negative_law_lowers_it(self, world, client):
        add_law(world, "France", "levy_act", [{"type": "recruit_morale", "arm": "infantry", "value": -10}])
        r = self._recruit(client, world)
        assert "infantry recruits muster at 30, not 40." in r["message"]

    def test_the_substitute_market_mirrors_the_unreformed_rung(self, world):
        region = world.get_region("Swabia")
        before = substitute_arrival_morale(ex(), region, None)
        add_law(world, "France", "jager_act", [{"type": "recruit_morale", "arm": "infantry", "value": 10}])
        assert substitute_arrival_morale(ex(), region, None) == before

    def test_the_bonus_reader_by_arm(self, world):
        enact(world, "Russia", "extraordinary_levy")
        assert R.recruit_morale_bonus(world, "Russia", "infantry") == -10
        assert R.recruit_morale_bonus(world, "Russia", "cavalry") == 0


# ═══════════════════════════════ 4. DRILL MORALE ══════════════════════════════

class TestDrillMorale:

    def test_the_gain_the_drill_applies(self, world):
        assert world.drill_morale_gain("Austria", False) == 10
        enact(world, "Austria", "infantry_regulations")
        assert world.drill_morale_gain("Austria", False) == 15
        assert world.drill_morale_gain("Austria", True) == 20
        assert world.drill_morale_gain("France", False) == 10
        mack = world.marshals["Mack"]
        mack.morale = 50
        assert world._apply_drill_morale(mack) == 15

    def test_the_note_names_the_applied_share(self, world):
        enact(world, "Austria", "infantry_regulations")
        mack = world.marshals["Mack"]
        assert world._drill_law_note(mack, 15) == " (+5 from the New Infantry Regulations)"
        assert world._drill_law_note(mack, 12) == " (+2 from the New Infantry Regulations)"
        assert world._drill_law_note(mack, 8) == ""

    def test_the_dispatch_remedy_quotes_the_applied_gain(self, world):
        add_law(world, "France", "drill_act", [{"type": "drill_morale", "value": 5}])
        from backend.game_logic import dispatch as D
        ney = world.marshals["Ney"]
        ney.morale = 20
        line = D._derive_danger(ney, world, "France", {})
        assert "+15 morale; +20 with a training ground" in line, line

    def test_the_build_chip_quotes_it(self, world):
        add_law(world, "France", "drill_act", [{"type": "drill_morale", "value": 5}])
        terms = world._region_build_terms(world.get_region("Paris"), 0)
        assert terms["training_ground"]["drill_gain_base"] == 15
        assert terms["training_ground"]["drill_gain"] == 20


# ═══════════════════════════════ 5. SUPPLY ════════════════════════════════════

class TestSupplyCapacity:

    def test_the_fed_multiplier_only(self, world):
        london = world.get_region("London")
        assert world.get_effective_supply_cap("Britain", london) == int(london.supply_capacity * 1.5)
        enact(world, "Britain", "commissariat")
        assert world.get_effective_supply_cap("Britain", london) == int(london.supply_capacity * 1.875)
        swabia = world.get_region("Swabia")
        assert world._supply_multiplier("Britain", swabia) in (1.0, 1.875)
        if swabia.controller != "Britain" and world.get_diplomatic_state(
                "Britain", swabia.controller) not in world.ALLY_SUPPLY_STATES:
            assert world._supply_multiplier("Britain", swabia) == 1.0

    def test_another_court_unchanged(self, world):
        paris = world.get_region("Paris")
        enact(world, "Britain", "commissariat")
        assert world.get_effective_supply_cap("France", paris) == int(paris.supply_capacity * 1.5)

    def test_the_reader(self, world):
        enact(world, "Britain", "commissariat")
        assert R.supply_capacity_terms(world, "Britain") == [("the Commissariat", 1.25)]


# ═══════════════════════════════ 6. SATELLITE LOYALTY ═════════════════════════

class TestSatelliteLoyalty:

    def test_the_forecast_names_it(self, world):
        world.vassals["Holland"]["loyalty"] = 50
        before = forecast_vassal_loyalty(world, "France", "Holland")
        enact(world, "France", "code_abroad")
        after = forecast_vassal_loyalty(world, "France", "Holland")
        assert after["law_bonus"] == 1
        assert after["law_terms"] == [["the Code Abroad", 1]]
        assert after["forecast"] == before["forecast"] + 1

    def test_the_tick_applies_the_same_term_and_names_it(self, world):
        for name in world.vassals:
            world.vassals[name]["loyalty"] = 50
        enact(world, "France", "code_abroad")
        expected = forecast_vassal_loyalty(world, "France", "Holland")["forecast"]
        with _quiet():
            process_vassal_loyalty(world)
        assert world.vassals["Holland"]["loyalty"] == 50 + expected

    def test_the_tick_names_the_law_as_a_cause(self, world):
        """The event's `reason` names its dominant causes; a law strong enough
        to lead is named by the law (T8)."""
        for name in world.vassals:
            world.vassals[name]["loyalty"] = 50
        add_law(world, "France", "strong_code", [{"type": "satellite_loyalty", "value": 5}])
        with _quiet():
            events = process_vassal_loyalty(world)
        ev = [e for e in events if e.get("type") == "vassal_loyalty"
              and "Holland" in (str(e.get("vassal")), str(e.get("nation")))]
        assert ev, events
        assert "the Strong Code" in ev[0]["reason"], ev[0]

    def test_every_client_whatever_its_autonomy(self, world):
        world.vassals["Holland"]["loyalty"] = 50
        world.vassals["Holland"]["autonomy"] = AUTONOMY_AUTONOMOUS
        enact(world, "France", "code_abroad")
        assert forecast_vassal_loyalty(world, "France", "Holland")["law_bonus"] == 1

    def test_without_the_law_the_forecast_is_unchanged(self, world):
        f = forecast_vassal_loyalty(world, "France", "Holland")
        assert f["law_bonus"] == 0 and f["law_terms"] == []


# ═══════════════════════════════ 7. THE BERLIN DECREE ═════════════════════════

class TestTheBerlinDecree:

    def test_an_autonomous_client_counts_under_the_decree(self, world):
        base = N.closure_against(world, "Britain")
        world.vassals["KingdomOfItaly"]["autonomy"] = AUTONOMY_AUTONOMOUS
        dropped = N.closure_against(world, "Britain")
        assert dropped < base
        assert N.decree_clients(world, "Britain") == []
        enact(world, "France", "berlin_decree")
        assert N.closure_against(world, "Britain") == base
        assert N.decree_clients(world, "Britain") == ["KingdomOfItaly"]

    def test_the_decree_needs_the_lord_at_war_with_the_target(self, world):
        world.vassals["KingdomOfItaly"]["autonomy"] = AUTONOMY_AUTONOMOUS
        enact(world, "France", "berlin_decree")
        assert "KingdomOfItaly" not in N.decree_clients(world, "Prussia")


# ═══════════════════════════════ 8. THE ORDERS IN COUNCIL ═════════════════════

class TestTheOrdersInCouncil:

    def test_the_blockaders_law_deepens_the_loss_everywhere(self, world):
        assert N.blockade_trade_loss(world)["France"] == 175
        assert N.blockade_trade_words(world, "France") == "halved"
        enact(world, "Britain", "orders_in_council")
        assert N.blockade_trade_loss(world)["France"] == 219
        assert N.blockade_trade_words(world, "France") == "cut by 62% (the Orders in Council)"

    def test_the_ledger_reads_the_same_loss_and_words(self, world):
        enact(world, "Britain", "orders_in_council")
        econ = _build_economy(world, "France")
        assert econ["blockade"] == 219
        assert econ["blockade_note"] == "trade cut by 62% (the Orders in Council) under enemy sail"

    def test_the_board_says_it(self, world):
        enact(world, "Britain", "orders_in_council")
        board = N.build_admiralty_report(world)["blockade_board"]
        row = next(b for b in board if b["nation"] == "France")
        assert "trade cut by 62% (the Orders in Council) (−219/turn)" in row["effects"]

    def test_the_blockaded_courts_own_law_does_nothing(self, world):
        add_law(world, "France", "own_orders", [{"type": "blockade_denial", "value": 1.25}])
        assert N.blockade_trade_loss(world)["France"] == 175

    def test_the_beat_and_the_log_carry_the_words(self, world):
        event = {"type": "blockade_begins", "nation": "France", "blockader": "Britain",
                 "trade_words": "cut by 62% (the Orders in Council)"}
        assert "trade cut by 62% (the Orders in Council)" in CL.format_event_oneliner(event, "France")
        old = {"type": "blockade_begins", "nation": "France", "blockader": "Britain"}
        assert "trade halved" in CL.format_event_oneliner(old, "France")


# ═══════════════════════════════ THE LEVER ════════════════════════════════════

class TestTheLever:

    def test_lever_down_no_law_is_in_force_anywhere(self, world, monkeypatch):
        enact(world, "Britain", "orders_in_council")
        enact(world, "France", "anticipated_class")
        monkeypatch.setattr(R, "THE_STATE_HAS_LAWS", False)
        assert N.blockade_trade_loss(world)["France"] == 175
        assert world.get_manpower_regen_rates("France")["infantry"] == 2500


# ═══════════════════════════════ T2 / T1 MEASURED ═════════════════════════════

class TestTheSinkAndTheReach:
    """§11 T2 read on RF-2's five-law slate against the IQ-1 control arm's own
    archived Net (the committed `iq13-control-cmd-historical` digest)."""

    DIGEST = ROOT / "docs" / "audits" / "playtest_digests" / "iq13-control-cmd-historical" / "digest.jsonl"

    def test_the_slate_and_the_share(self):
        rows = [json.loads(line) for line in self.DIGEST.read_text(encoding="utf-8").splitlines() if line.strip()]
        nets = [r["net"] for r in rows if r.get("kind") == "ledger"]
        surplus = sum(nets) / len(nets)
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
        slate = sum(r["upkeep"] for r in scenario["reforms"]["France"])
        # SR-7d "The Doctrines" (October 3, 2026): REFORMS_SPEC §11 T2 re-run with the Train in
        # France's slate (DC-2) — 850 → 1,050 a turn, the share RF-2 forecast
        # at 45.3% measured on this archive; the band's top admits it.
        assert slate == 1050
        share = slate / surplus
        assert 0.30 < share < 0.50, share
