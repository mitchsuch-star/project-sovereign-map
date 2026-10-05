"""SR-5a "The chest" — Score Mandate Chunk 5 (`docs/SCORE_MANDATE_PLAN.md` §2),
RULED by the user September 28, 2026. Rules `docs/SYSTEMS_REFERENCE.md` §76.

  * AAR-6 — an ADMINISTRATIVE order asks only the administrative pool: a
    marshal-addressed levy walked into the objection branch, whose own AP
    pre-check read the MILITARY pool (lever
    `executor.AN_ADMIN_ORDER_ASKS_ONLY_THE_ADMIN_POOL`).
  * Found reproducing AAR-6 — `buy substitutes in <province>` means the
    infantry marshal of ours standing there, and a refusal is a sentence,
    never the fuzzy matcher's error dict stuffed into `message` (lever
    `economy_executor.THE_NAMED_GROUND_RECEIVES_THE_SUBSTITUTES`).
  * THE RULED BALANCE — "Britain up, France trimmed": every French homeland
    province at three-quarters of its registry yield; London 500, East
    Anglia 300, Midlands 300, Northumbria and Scotland 150; Britain's trade
    dominance 450 and overseas pool 1,000. Scenario-scoped
    (`europe_1805.json` region_overrides + navies).
  * Question (c), RULED "keep the rules, make it legible" — the ledger says
    why each bill moved since the last charged turn (lever
    `ledger.THE_BILLS_SAY_WHY_THEY_MOVED`; the ratchet's own pins live in
    `tests/test_iq1_iq1_5_the_exit.py`).
  * PTJ-D1 ([P3-5]) REFUTED at HEAD — a coordinated battle's pool is the
    lead's own nation by construction; the precondition is pinned here.
  * ES-4 and ES-7b STRUCK by the user's ruling; IGR-X9 re-verified closed.
"""
import contextlib
import io
import json
import random
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands import economy_executor as EE
from backend.commands import executor as EX
from backend.commands.executor import CommandExecutor
from backend.game_logic import ledger as LG
from backend.game_logic.ledger import _build_economy, why_the_bills_moved
from backend.models.region import create_europe_regions
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario
from tests import _chip_census as C

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
SCENARIO = MAPS / "europe_1805.json"
TUTORIAL = MAPS / "tutorial_1805.json"
DOCS = ROOT / "docs"

BRITAIN_INCOME = {"London": 500, "East Anglia": 300, "Midlands": 300,
                  "Northumbria": 150, "Scotland": 150}


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot():
    with _quiet():
        return WorldState.from_scenario(str(SCENARIO))


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
    M.world.nation_gold["France"] = 20_000
    return M.world


@pytest.fixture
def client(world):
    return TestClient(M.app)


def _post(client, command):
    with _quiet():
        return client.post("/command", json={"command": command}).json()


# ═══════════════════════════════════════════════════════════════════════
# AAR-6 — an administrative order asks only the administrative pool
# ═══════════════════════════════════════════════════════════════════════

class TestAAR6TheAdminPool:
    @pytest.mark.parametrize("order", ["recruit 10000 infantry with Soult",
                                       "Soult, recruit infantry"])
    def test_a_levy_is_raised_with_the_military_pool_spent(self, world, client, order):
        world.actions_remaining, world.admin_actions_remaining = 0, 2
        r = _post(client, order)
        assert r.get("success") is True, r.get("message")
        assert "recruits" in str(r.get("message")), r.get("message")
        assert world.admin_actions_remaining == 1
        assert world.actions_remaining == 0

    def test_the_admin_pool_still_gates_it(self, world, client):
        world.actions_remaining, world.admin_actions_remaining = 4, 0
        r = _post(client, "Soult, recruit infantry")
        assert r.get("success") is False
        assert "No administrative actions remaining" in str(r.get("message"))
        assert world.actions_remaining == 4

    def test_the_objection_gate_still_prices_a_field_order(self, world, client):
        """The exemption is for ADMIN verbs only. What this pre-check alone
        guards (the head-of-execute gate prices a stance change at its flat
        1) is the VARIABLE cost: defensive -> aggressive is 2 actions.
        Found by the sweep — a pin on "a field order at zero actions" was
        INERT, because the head gate refuses that before this one runs."""
        from backend.models.marshal import Stance
        world.marshals["Ney"].stance = Stance.DEFENSIVE
        world.actions_remaining, world.admin_actions_remaining = 1, 2
        r = _post(client, "Ney, go aggressive")
        assert r.get("success") is False
        assert "(2 actions)" in str(r.get("message")), r.get("message")
        assert world.marshals["Ney"].stance == Stance.DEFENSIVE
        assert world.actions_remaining == 1

    def test_lever_down_is_the_reported_refusal(self, world, client, monkeypatch):
        monkeypatch.setattr(EX, "AN_ADMIN_ORDER_ASKS_ONLY_THE_ADMIN_POOL", False)
        world.actions_remaining, world.admin_actions_remaining = 0, 2
        r = _post(client, "Soult, recruit infantry")
        assert r.get("success") is False
        assert "Not enough actions remaining" in str(r.get("message"))
        assert world.admin_actions_remaining == 2


# ═══════════════════════════════════════════════════════════════════════
# The substitutes' named ground (found reproducing AAR-6)
# ═══════════════════════════════════════════════════════════════════════

class TestTheNamedGroundReceivesTheSubstitutes:
    def test_the_marshal_standing_there_receives_them(self, world, client):
        assert world.marshals["Lannes"].location == "Franche-Comte"
        r = _post(client, "buy substitutes in Franche-Comte")
        assert r.get("success") is True, r.get("message")
        assert "Lannes takes" in str(r.get("message"))

    def test_empty_ground_is_refused_in_a_sentence_that_keeps_the_name(self, world, client):
        assert not any(m.location == "Paris" and m.nation == "France"
                       for m in world.marshals.values())
        r = _post(client, "buy substitutes in Paris")
        assert r.get("success") is False
        message = r.get("message")
        assert isinstance(message, str) and "Paris" in message, message
        assert not message.lstrip().startswith("{"), message

    def test_an_unknown_name_is_answered_in_a_sentence(self, world):
        ex = CommandExecutor()
        with _quiet():
            r = ex._economy._execute_purchase_levy(
                {"action": "purchase_levy", "target": "Zorglub"},
                {"world": world})
        assert r.get("success") is False
        assert isinstance(r.get("message"), str), r.get("message")

    def test_lever_down_is_the_dict_in_the_message(self, world, monkeypatch):
        monkeypatch.setattr(EE, "THE_NAMED_GROUND_RECEIVES_THE_SUBSTITUTES", False)
        ex = CommandExecutor()
        with _quiet():
            r = ex._economy._execute_purchase_levy(
                {"action": "purchase_levy", "target": "Paris"},
                {"world": world})
        assert isinstance(r.get("message"), dict), r.get("message")


# ═══════════════════════════════════════════════════════════════════════
# The ruled balance — Britain up, France trimmed
# ═══════════════════════════════════════════════════════════════════════

class TestTheRuledBalance:
    def test_britain_nets_more_than_twice_what_france_nets_at_boot(self):
        w = _boot()
        with _quiet():
            britain = _build_economy(w, "Britain")
            france = _build_economy(w, "France")
        assert britain["net"] == 2851, britain["net"]
        # RE-SEATED consciously by the economy gate (October 5, 2026; EAD-1,
        # SYSTEMS_REFERENCE §98.1): France's boot Net 1,032 → 828. Campaign
        # pay bills Bernadotte's 17,000 at Franconia — an ally's soil, outside
        # the 1805 homeland — at 12 gold per 1,000 men: 204. The lever-down
        # arm below keeps SR-5a's own measurement.
        assert france["net"] == 828, france["net"]
        assert britain["net"] > 2 * france["net"]

    def test_the_ruled_balance_without_campaign_pay(self, monkeypatch):
        from backend.models import world_state as WS
        monkeypatch.setattr(WS, "CAMPAIGN_PAY_ON_FOREIGN_SOIL", False)
        w = _boot()
        with _quiet():
            britain = _build_economy(w, "Britain")
            france = _build_economy(w, "France")
        assert britain["net"] == 2851, britain["net"]
        assert france["net"] == 1032, france["net"]

    def test_every_french_homeland_province_yields_three_quarters(self):
        """Read against the REGISTRY, not restated: each French province's
        authored income is the registry's times 0.75, rounded to ten."""
        w = _boot()
        registry = create_europe_regions()
        homeland = w.nation_starting_regions["France"]
        assert len(homeland) == 28
        for name in homeland:
            base = int(registry[name].income_value)
            expected = int(round(base * 0.75 / 10.0)) * 10
            assert w.regions[name].income_value == expected, name
        assert sum(w.regions[n].income_value for n in homeland) == 2590

    def test_englands_industrial_and_commercial_provinces_rise(self):
        w = _boot()
        for name, value in BRITAIN_INCOME.items():
            assert w.regions[name].income_value == value, name
        britain = [r for r in w.regions.values() if r.controller == "Britain"]
        assert sum(r.income_value for r in britain) == 2050

    def test_the_city_carries_the_trade_and_the_colonies(self):
        navies = json.loads(SCENARIO.read_text(encoding="utf-8"))["navies"]
        assert navies["Britain"]["trade_dominance"] == 450
        assert navies["Britain"]["overseas_income"] == 1000
        w = _boot()
        income = w.calculate_turn_income("Britain")
        assert income["overseas"] == 615
        assert income["breakdown"]["naval_income"] == 276

    def test_it_is_scenario_scoped(self):
        """The registry, the tutorial and the legacy world keep their
        figures — only the 1805 campaign carries the ruling."""
        registry = create_europe_regions()
        assert registry["Paris"].income_value == 300
        assert registry["London"].income_value == 300
        tutorial = json.loads(TUTORIAL.read_text(encoding="utf-8"))
        overrides = tutorial.get("region_overrides") or {}
        assert not any("income_value" in (row or {}) for row in overrides.values())

    def test_the_scenario_validates(self):
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        assert "_economy_balance_comment" in data
        from backend.models.world_state import WorldState as _W  # noqa: F401
        result = validate_scenario(data, check_adjacency=False)
        assert result.is_valid, [f"{e.path}: {e.message}" for e in result.errors[:3]]


# ═══════════════════════════════════════════════════════════════════════
# Question (c) — the ledger says why each bill moved
# ═══════════════════════════════════════════════════════════════════════

class _FakeWorld:
    def __init__(self, last, gold=0):
        self._income_phase_results = {"France": last}
        self.nation_gold = {"France": gold}


CROWN = {"key": "crown", "label": "the household and the pensions", "amount": 30}
WAR = {"key": "war_establishment", "label": "the war establishment", "amount": 50}
WE8 = {"key": "war_exhaustion", "label": "the long war wears on", "amount": 8}
WE16 = {"key": "war_exhaustion", "label": "the long war wears on", "amount": 16}


def _charge(gold, terms):
    rate = sum(t["amount"] for t in terms)
    return max(0, gold - 2000) * rate // 2500


class TestWhyTheBillsMoved:
    def test_a_smaller_army_names_the_fallen(self):
        last = {"upkeep_data": {"total": 2000, "total_strength": 150_000}}
        out = why_the_bills_moved(_FakeWorld(last), "France",
                                  {"total": 1500, "total_strength": 110_000}, 0)
        assert out["upkeep_note"] == (
            "paid for the 110,000 men under arms — the fallen draw no pay; "
            "500g less than last turn's bill, the army 40,000 men smaller")

    def test_a_larger_army_names_the_new_men(self):
        last = {"upkeep_data": {"total": 1500, "total_strength": 110_000}}
        out = why_the_bills_moved(_FakeWorld(last), "France",
                                  {"total": 1600, "total_strength": 120_000}, 0)
        assert out["upkeep_note"].endswith(
            "100g more than last turn's bill, the army 10,000 men larger")

    def test_a_fuller_chest_is_named_when_the_rate_holds(self):
        terms = [CROWN, WAR]
        last = {"state_charges": _charge(6_000, terms),
                "breakdown": {"state_charges_terms": terms}}
        now = _charge(8_000, terms)
        out = why_the_bills_moved(_FakeWorld(last, 8_000), "France", {}, now, terms)
        # EA-13 (the economy audit, October 5, 2026) — conscious flip: the
        # note names its line ("charge", not "draw"), so it says which bill
        # it explains wherever it is quoted out of its line.
        assert out["charges_note"] == (
            f"{now - last['state_charges']}g more than last turn's charge — "
            f"the chest is fuller")

    def test_a_raised_rate_is_named_by_its_term_not_the_chest(self):
        last = {"state_charges": _charge(10_000, [CROWN]),
                "breakdown": {"state_charges_terms": [CROWN]}}
        now = _charge(10_000, [CROWN, WAR])
        out = why_the_bills_moved(_FakeWorld(last, 10_000), "France", {}, now,
                                  [CROWN, WAR])
        assert out["charges_note"].endswith("— the war establishment (+50)"), out
        assert "chest" not in out["charges_note"]

    def test_both_causes_are_named_when_both_moved(self):
        """The war rolls on AND the chest filled: the tick's +8 and the new
        gold are both reasons, and the note says both."""
        was = [CROWN, WAR, WE8]
        now_terms = [CROWN, WAR, WE16]
        last = {"state_charges": _charge(6_000, was),
                "breakdown": {"state_charges_terms": was}}
        now = _charge(9_000, now_terms)
        out = why_the_bills_moved(_FakeWorld(last, 9_000), "France", {}, now,
                                  now_terms)
        assert out["charges_note"].endswith(
            "— the chest is fuller and the long war wears on (+8)"), out

    def test_a_calmer_realm_and_a_leaner_chest(self):
        was = [CROWN, WAR]
        last = {"state_charges": _charge(10_000, was),
                "breakdown": {"state_charges_terms": was}}
        calmer = why_the_bills_moved(_FakeWorld(last, 10_000), "France", {},
                                     _charge(10_000, [CROWN]), [CROWN])
        assert calmer["charges_note"].endswith("— the realm is calmer"), calmer
        leaner = why_the_bills_moved(_FakeWorld(last, 7_000), "France", {},
                                     _charge(7_000, was), was)
        assert leaner["charges_note"].endswith("— the chest is leaner"), leaner

    def test_after_a_load_only_the_standing_rule_is_said(self):
        class _Loaded:
            pass
        out = why_the_bills_moved(_Loaded(), "France",
                                  {"total": 900, "total_strength": 60_000}, 50)
        assert out == {"upkeep_note": "paid for the 60,000 men under arms — the "
                                      "fallen draw no pay", "charges_note": ""}

    def test_the_ledger_carries_both_keys_and_the_rate_note_says_it(self):
        w = _boot()
        with _quiet():
            econ = _build_economy(w, "France")
        assert "the fallen draw no pay" in econ["upkeep_note"]
        assert "state_charges_delta_note" in econ
        assert econ["state_charges_rate_note"].endswith("so a fuller chest pays more")

    def test_the_client_renders_both_notes(self):
        gd = (ROOT / "godot-client" / "project-sovereign" / "scripts"
              / "strategic_ledger.gd").read_text(encoding="utf-8")
        assert 'econ.get("upkeep_note", "")' in gd
        assert 'econ.get("state_charges_delta_note", "")' in gd

    def test_lever_down_is_silent(self, monkeypatch):
        monkeypatch.setattr(LG, "THE_BILLS_SAY_WHY_THEY_MOVED", False)
        out = why_the_bills_moved(_FakeWorld({}), "France",
                                  {"total": 900, "total_strength": 60_000}, 50)
        assert out == {"upkeep_note": "", "charges_note": ""}


# ═══════════════════════════════════════════════════════════════════════
# IQ1-5-1 (owned by SR-5a, PB-7) — the forecast reads the tick
# ═══════════════════════════════════════════════════════════════════════

class TestTheForecastAndTheTick:
    """`coalition.next_war_exhaustion` is the tick's single source: the
    advance writes it, and every forecast of the Charges of Empire reads it
    (the quote-is-the-levy pins live in `test_iq1_iq1_5_the_exit.py`)."""

    def test_at_war_it_climbs_eight_and_caps(self):
        from backend.game_logic.coalition import WAR_EXHAUSTION_MAX, next_war_exhaustion
        w = _boot()
        assert w.get_nations_at_war_with("France")
        w.war_exhaustion["France"] = 10
        assert next_war_exhaustion(w, "France") == 18
        w.war_exhaustion["France"] = WAR_EXHAUSTION_MAX - 3
        assert next_war_exhaustion(w, "France") == WAR_EXHAUSTION_MAX

    def test_at_peace_it_decays_five(self):
        from backend.game_logic.coalition import next_war_exhaustion
        from backend.game_logic.diplomacy import set_diplomatic_state
        w = _boot()
        with _quiet():
            for other in list(w.get_nations_at_war_with("France")):
                set_diplomatic_state(w, "France", other, "PEACE")
        assert not w.get_nations_at_war_with("France")
        w.war_exhaustion["France"] = 20
        assert next_war_exhaustion(w, "France") == 15
        w.war_exhaustion["France"] = 3
        assert next_war_exhaustion(w, "France") == 0

    def test_the_advance_writes_what_the_forecast_said(self):
        from backend.game_logic.coalition import next_war_exhaustion
        w = _boot()
        w.war_exhaustion["France"] = 40
        predicted = next_war_exhaustion(w, "France")
        with _quiet():
            w.advance_turn()
        assert int(w.war_exhaustion["France"]) == predicted == 48

    def test_the_legacy_player_row_never_ticks(self):
        from backend.game_logic.coalition import next_war_exhaustion
        with _quiet():
            legacy = WorldState()
        assert legacy.sovereign_map != "europe"
        legacy.war_exhaustion[legacy.player_nation] = 30
        assert next_war_exhaustion(legacy, legacy.player_nation) == 30

    def test_the_projected_rate_carries_tomorrows_term(self):
        w = _boot()
        w.war_exhaustion["France"] = 40
        today = w.get_state_charges_rate("France")
        tomorrow = w.get_state_charges_rate("France", projected=True)
        assert tomorrow["rate"] - today["rate"] == 8


# ═══════════════════════════════════════════════════════════════════════
# PTJ-D1 ([P3-5]) — REFUTED: the pool is the lead's own nation
# ═══════════════════════════════════════════════════════════════════════

def _stage(w, placements):
    for m in w.marshals.values():
        if m.name not in placements:
            m.location = "Moscow" if m.nation != "France" else "Gascony"
    for name, (region, strength) in placements.items():
        m = w.marshals[name]
        m.location, m.strength, m.morale = region, strength, 75
        m.retreat_recovery = 0
        for attr in ("broken", "retreated_this_turn", "moved_this_turn",
                     "reinforced_this_turn", "drilling", "holding_position",
                     "fortified"):
            setattr(m, attr, False)
        m.strategic_order = None
    with _quiet():
        w.calculate_visibility()
    return w


class TestPTJD1IsRefuted:
    """The row's premise: a coordinated battle bills France's pensions for
    a Bavarian reinforcer's dead. It cannot happen:
    `_get_casualty_participants` admits only the lead's own nation, so an
    allied corps on the field neither bleeds nor enters the pool. Measured on
    three seeds: Deroy 0 lost, Kutuzov 0 lost, the ledger's France figure
    exactly Ney's plus Davout's. Killed by: participants that admit another
    court — which is the day PTJ-D1's own fix (per-nation attribution
    through `casualty_distribution`) becomes necessary."""

    @pytest.mark.parametrize("seed", [1, 2, 3])
    def test_an_allied_corps_on_the_field_is_not_in_the_pool(self, seed):
        placements = {"Ney": ("Swabia", 30000), "Davout": ("Swabia", 20000),
                      "Deroy": ("Swabia", 20000), "Mack": ("Swabia", 40000)}
        w = _stage(_boot(), placements)
        before = {n: int(w.marshals[n].strength) for n in placements}
        random.seed(seed)
        ex = CommandExecutor()
        with _quiet():
            r = ex.execute({"command": {"type": "specific", "marshal": "Ney",
                                        "action": "attack", "target": "Mack",
                                        "_autonomous_execution": True}},
                           {"world": w, "debug_mode": True, "executor": ex})
        assert r.get("success"), r.get("message")
        after = {n: int(getattr(w.marshals.get(n), "strength", 0)) for n in placements}
        assert after["Deroy"] == before["Deroy"]
        french_dead = sum(before[n] - after[n] for n in ("Ney", "Davout"))
        ledger = w.campaign_ledgers[w._make_diplo_key("France", "Austria")]
        assert ledger["casualties"]["France"] == french_dead
        assert "Bavaria" not in ledger["casualties"]

    def test_participants_are_the_lead_nation_by_construction(self):
        w = _stage(_boot(), {"Ney": ("Swabia", 30000), "Deroy": ("Swabia", 20000)})
        ex = CommandExecutor()
        parts = ex._combat._get_casualty_participants(
            w.marshals["Ney"], "Swabia", "France", w)
        assert {p.nation for p in parts} == {"France"}


# ═══════════════════════════════════════════════════════════════════════
# The records — ES-4 and ES-7b struck, IGR-X9 re-verified, AIDR-D1 decided
# ═══════════════════════════════════════════════════════════════════════

class TestTheRecords:
    def test_es4_and_es7b_are_struck_with_their_reopen_conditions(self):
        spec = (DOCS / "ECONOMY_REVISIT_SPEC.md").read_text(encoding="utf-8")
        assert "ES-4 STRUCK" in spec and "ES-7b STRUCK" in spec
        assert "Re-open condition" in spec

    def test_igr_x9_is_closed_at_head(self):
        """A ruin bills nothing (the Aug 7 EB-3.2 decision), re-verified."""
        w = _boot()
        region = w.regions["Paris"]
        before = w.calculate_turn_income("France")["infrastructure"]
        # EA-9 (the economy audit, October 5, 2026) — re-seated: a market now
        # keeps itself (it bills nothing standing or ruined), so the ruin rule
        # is pinned on a work that still bills its keep — a supply depot.
        region.buildings = list(getattr(region, "buildings", []) or []) + [
            {"type": "supply_depot", "damaged": True}]
        assert w.calculate_turn_income("France")["infrastructure"] == before
        region.buildings[-1]["damaged"] = False
        assert w.calculate_turn_income("France")["infrastructure"] > before

    def test_the_plan_records_the_slice(self):
        plan = (DOCS / "SCORE_MANDATE_PLAN.md").read_text(encoding="utf-8")
        assert "SR-5a The chest" in plan and "LANDED September 28, 2026" in plan
