"""T0-D "small fixes and the books" — Tier 0 of the November 6, 2026 whole-game
review, the fourth slice (`PRE_DEPLOY_PLAN.md` §2 row S15-R; the rules
`SYSTEMS_REFERENCE.md` §181; `BUG_FIXES.md` §GR the twenty-three T0-D rows).

The books (Golden Rule 8) — GR-33 / GR-59 the purse read without the tab's
rows, GR-60 the edicts read the store first, GR-62 the summary's bucket and the
index that is rebuilt only when a corps moved, GR-61 the capped offer history.
The quotes — GR-20 the applied loyalty, GR-40 the short chest named, GR-42 the
neutrality floor, GR-13 the white peace's words, GR-19 the plural possessive.
The courts — GR-5 a sleeping design wakes silently, GR-34 the regen never
deletes men, GR-38 the player in hand, GR-45 every trait names its code path,
GR-7 the player's lead keeps the player's rule, GR-12 the purses name the
bankrupt. The narration — GR-63 the garrison counter said once. The docs and
the dead code — GR-16 / GR-48, GR-43, GR-49, GR-50.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


@pytest.fixture
def world(monkeypatch, tmp_path):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setenv("INK_IRON_SAVE_DIR", str(tmp_path / "saves"))
    from backend.models.world_state import WorldState
    return WorldState.from_scenario(str(SCENARIO))


# ═══════════════════════════════ 1. THE BOOKS ═══════════════════════════════

class TestThePurseReadWithoutTheRows:
    """GR-33 / GR-59: `rows=False` is every figure of the full build with the
    display rows empty; the forecast and the courts' purse reads take it."""

    FIGURES = ("treasury", "income", "trade_income", "admin_bonus", "treaty_gold",
               "vassal_tribute", "settlement_gold", "subsidies", "continental_system",
               "blockade", "admiralty", "occupation", "contributions", "requisitions",
               "overseas", "state_charges", "dotation_skim", "rente_cost", "laws",
               "infrastructure", "upkeep", "upkeep_base", "upkeep_surcharge",
               "grande_armee", "campaign_pay", "garrison_pay", "garrison_men",
               "force_limit", "army_strength_total", "net", "bankruptcy_turns",
               "ceiling", "ceiling_state", "spent", "materiel")

    def test_every_figure_equals_the_full_build_for_every_court(self, world):
        from backend.game_logic.ledger import _build_economy
        for nation in world.get_active_nations():
            full = _build_economy(world, nation)
            lean = _build_economy(world, nation, rows=False)
            for key in self.FIGURES:
                assert lean[key] == full[key], (nation, key)

    def test_the_rows_are_empty_and_the_levy_is_never_read(self, world, monkeypatch):
        from backend.game_logic import ledger
        monkeypatch.setattr(ledger, "_levy_block", lambda *a, **k: 1 / 0)
        monkeypatch.setattr(ledger, "why_the_bills_moved", lambda *a, **k: 1 / 0)
        lean = ledger._build_economy(world, "Austria", rows=False)
        assert lean["levy"] == {} and lean["construction_queue"] == []
        assert lean["income_breakdown"] == [] and lean["campaign_ground"] == []
        assert lean["upkeep_note"] == "" and lean["state_charges_delta_note"] == ""
        assert lean["net_moves_note"] == "" and lean["blockade_note"] == ""

    def test_the_forecast_takes_the_purse_read(self, world, monkeypatch):
        from backend.game_logic import ledger
        full_net = ledger._build_economy(world, "Austria")["net"]
        monkeypatch.setattr(ledger, "_levy_block", lambda *a, **k: 1 / 0)
        fc = ledger.chest_forecast(world, "Austria")
        assert fc["net"] == full_net
        assert fc["projected"] == fc["chest"] + fc["net"]

    def test_the_rows_read_the_nations_provinces_in_one_pass(self, world, monkeypatch):
        from backend.game_logic.ledger import _build_economy
        player = world.player_nation
        expected = [r.name for r in world.regions.values() if r.controller == player]
        econ = _build_economy(world, player)
        assert [row["region"] for row in econ["income_breakdown"]] == expected
        queue = [r.name for r in world.regions.values() if r.controller == player
                 and r.building_under_construction is not None]
        assert [row["region"] for row in econ["construction_queue"]] == queue

    def test_the_two_full_map_scans_are_gone(self):
        body = _src("backend/game_logic/ledger.py").split("def _build_economy(")[1].split("\ndef ")[0]
        assert "for region in world.regions.values()" not in body
        assert "world.get_nation_regions(player)" in body


class TestTheEdictsReadTheStoreFirst:
    """GR-60: a court with no decree running past the turn has none in force,
    and the deck is never walked; with one running, the walk's answer."""

    def _edict(self, world):
        from backend.game_logic import affairs
        return next(e for e in affairs.deck(world) if affairs.edict_block(e))

    def test_no_decree_never_walks_the_deck(self, world, monkeypatch):
        from backend.game_logic import affairs
        if not affairs.armed(world):
            pytest.skip("the affairs deck is not armed on this board")
        e = self._edict(world)
        turn = int(world.current_turn)
        store = affairs.runtime(world).setdefault(affairs.EDICTS_KEY, {})
        store[affairs.edict_key("Russia", e["id"])] = turn + 5      # another court
        store[affairs.edict_key("Austria", e["id"])] = turn          # expired
        monkeypatch.setattr(affairs, "deck", lambda w: 1 / 0)
        assert affairs.edicts_in_force(world, "Austria") == []
        assert affairs.edicts_in_force(world, "Prussia") == []

    def test_a_running_decree_is_the_walks_answer(self, world):
        from backend.game_logic import affairs
        if not affairs.armed(world):
            pytest.skip("the affairs deck is not armed on this board")
        e = self._edict(world)
        turn = int(world.current_turn)
        affairs.runtime(world).setdefault(affairs.EDICTS_KEY, {})[
            affairs.edict_key("Austria", e["id"])] = turn + 4
        got = affairs.edicts_in_force(world, "Austria")
        assert [(x["id"], until) for x, until in got] == [(e["id"], turn + 4)]


class TestTheSummaryAndTheIndex:
    """GR-62: the API summary buckets the roster in one pass; the index is
    rebuilt only when a corps moved, joined, left or was swapped."""

    def test_the_summary_lists_the_linear_scans_marshals(self, world):
        summary = world.get_game_state_summary()
        for name, region in world.regions.items():
            want = [m.name for m in world.get_marshals_in_region(name) if m.strength > 0]
            got = [m["name"] for m in (summary["map_data"].get(name) or {}).get("marshals", [])]
            assert got == want, name

    def test_an_unchanged_board_keeps_the_same_lists(self, world):
        world.refresh_marshal_indexes()
        index = world._marshals_by_region
        world._live_visible_regions_cache = {"France": {"Paris"}}
        world.refresh_marshal_indexes()
        assert world._marshals_by_region is index
        assert world._live_visible_regions_cache == {}, "the sight cache is cleared every refresh"

    def test_a_march_rebuilds(self, world):
        world.refresh_marshal_indexes()
        index = world._marshals_by_region
        ney = world.marshals["Ney"]
        dest = next(r for r in world.regions if r != ney.location)
        ney.location = dest
        world.refresh_marshal_indexes()
        assert world._marshals_by_region is not index
        assert ney in world._get_marshals_in_region_indexed(dest)

    def test_a_replaced_index_or_a_swapped_marshal_rebuilds(self, world):
        from backend.models.marshal import Marshal
        world.refresh_marshal_indexes()
        world._marshals_by_region = {}
        world.refresh_marshal_indexes()
        assert world._marshals_by_region, "a cleared index is rebuilt"
        old = world.marshals["Ney"]
        new = Marshal.from_dict(old.to_dict())
        world.marshals["Ney"] = new
        world.refresh_marshal_indexes()
        here = world._get_marshals_in_region_indexed(new.location)
        assert new in here and all(m is not old for m in here)


class TestTheOfferHistoryIsCapped:
    """GR-61: the per-war history keeps the last OFFER_HISTORY_CAP letters and
    every older one the ratchet, the standing refusal and the refusal note read."""

    @staticmethod
    def _e(turn, outcome="sent", proposer="Britain", recipient="France",
           channel="bilateral", answered=None):
        e = {"turn": turn, "proposer": proposer, "recipient": recipient,
             "channel": channel, "tier": 0, "label": "", "summary": "", "ask_gold": 0,
             "outcome": outcome}
        if answered is not None:
            e["answered_turn"] = answered
        return e

    def test_a_long_run_is_capped(self):
        from backend.game_logic.ai_diplomacy import OFFER_HISTORY_CAP, trim_offer_history
        history = [self._e(t) for t in range(1, 90)]
        trimmed = trim_offer_history(history)
        assert len(trimmed) == OFFER_HISTORY_CAP
        assert trimmed == history[-OFFER_HISTORY_CAP:]

    def test_old_refusals_and_the_last_unanswered_letter_survive(self):
        from backend.game_logic.ai_diplomacy import (
            DICTATED_RATCHET_CAP, OFFER_HISTORY_CAP, trim_offer_history)
        history = ([self._e(1, "refused", answered=1), self._e(2, "lapsed", answered=9),
                    self._e(3, "refused", answered=3), self._e(4, channel="settlement")]
                   + [self._e(t, channel="bilateral") for t in range(5, 60)])
        trimmed = trim_offer_history(history)
        refused = [e for e in trimmed if e["outcome"] in ("refused", "lapsed")]
        assert min(DICTATED_RATCHET_CAP, len(refused)) == DICTATED_RATCHET_CAP
        assert max(e["answered_turn"] for e in refused) == 9, "the latest answer by turn"
        assert any(e["channel"] == "settlement" and e["outcome"] == "sent" for e in trimmed)
        assert len(trimmed) <= OFFER_HISTORY_CAP + 4
        assert [history.index(e) for e in trimmed] == sorted(history.index(e) for e in trimmed)

    def test_the_writer_caps_a_live_war(self, world):
        from backend.game_logic import ai_diplomacy as AD
        inst = AD._find_war_instance_for_pair(world, "Britain", world.player_nation)
        if inst is None:
            pytest.skip("no Britain–France war instance on this board")
        for t in range(3):
            world.current_turn = t + 1
            AD.record_dictated_offer(world, "Britain", world.player_nation, channel="bilateral",
                                     tier=0, summary="", ask_gold=0)
            AD.note_dictated_refusal(world, "Britain", world.player_nation, channel="bilateral")
        for t in range(4, 130):
            world.current_turn = t
            AD.record_dictated_offer(world, "Britain", world.player_nation, channel="bilateral",
                                     tier=0, summary="", ask_gold=0)
        assert len(inst["offer_history"]) <= AD.OFFER_HISTORY_CAP + 3
        assert AD.dictated_ratchet(world, "Britain", world.player_nation) == AD.DICTATED_RATCHET_CAP


# ═══════════════════════════════ 2. THE QUOTES ══════════════════════════════

class TestTheAutonomyReplyIsTheAppliedChange:
    """GR-20 (ACH-1's class) and its siblings, the invest quote and reply."""

    def _ready(self, world, loyalty, autonomy=1):
        state = world.vassals["Holland"]
        state["loyalty"] = loyalty
        state["autonomy"] = autonomy
        world.diplomatic_points = 9
        return state

    def test_at_full_loyalty_the_grant_buys_none_and_says_so(self, world):
        from backend.game_logic.vassal import change_vassal_autonomy
        self._ready(world, 100)
        r = change_vassal_autonomy(world, "Holland", 2, actor=world.player_nation)
        assert r["success"]
        assert "Loyalty stays 100 (already full - the grant buys no loyalty" in r["message"]
        assert "+10 loyalty" not in r["message"]
        assert "a permanent income cut" in r["message"]

    def test_near_the_cap_the_reply_prints_what_lands(self, world):
        from backend.game_logic.vassal import change_vassal_autonomy
        self._ready(world, 95)
        r = change_vassal_autonomy(world, "Holland", 2, actor=world.player_nation)
        assert "+5 loyalty (95 → 100, increased autonomy)" in r["message"]

    def test_a_downgrade_prints_what_lands(self, world):
        from backend.game_logic.vassal import change_vassal_autonomy
        self._ready(world, 10)
        r = change_vassal_autonomy(world, "Holland", 0, actor=world.player_nation)
        assert "-10 loyalty (10 → 0, decreased autonomy)" in r["message"]
        self._ready(world, 0)
        r = change_vassal_autonomy(world, "Holland", 0, actor=world.player_nation)
        assert "Loyalty stays 0 (already at the floor)" in r["message"]

    def test_the_invest_quote_and_reply_print_what_lands(self, world):
        from backend.game_logic.vassal import invest_in_vassal, invest_quote_words
        self._ready(world, 95)
        world.gold = 5000
        q = invest_in_vassal(world, "Holland", actor=world.player_nation, quote_only=True)
        assert "rises +5 (95 → 100)" in invest_quote_words(world, q["quote"])
        r = invest_in_vassal(world, "Holland", actor=world.player_nation)
        assert r["message"].startswith("Invested in")
        assert "+5 loyalty (95 → 100)" in r["message"]


class TestTheShortChestIsNamed:
    """GR-40: the war's price stands (PC-R3); the letter says what the chest pays."""

    def test_the_note(self):
        from backend.game_logic.settlement_offers import indemnity_chest_note
        w = SimpleNamespace(nation_gold={"Austria": 50, "Britain": 9000, "Russia": -200})
        note = indemnity_chest_note(w, {"from": "Austria", "to": "France", "amount": 4200})
        assert note == (" — Austria's chest holds 50: the lump is paid from the chest at "
                        "signing, and what it lacks is never paid")
        assert "holds 0" in indemnity_chest_note(w, {"from": "Russia", "amount": 100})
        assert indemnity_chest_note(w, {"from": "Britain", "amount": 4200}) == ""
        assert indemnity_chest_note(w, {"from": "Spain", "amount": 4200}) == ""

    def test_the_popup_carries_it(self, world):
        from backend.game_logic.settlement_offers import build_incoming_settlement_offer_popup
        world.nation_gold["Austria"] = 50
        payload = build_incoming_settlement_offer_popup(world, {
            "war_id": "", "offer_id": "x", "proposer_nation": "Austria",
            "settlement_terms": [{"type": "peace"},
                                 {"type": "gold_indemnity", "from": "Austria",
                                  "to": world.player_nation, "amount": 4200}]})
        text = json.dumps(payload, ensure_ascii=False)
        assert "Austria's chest holds 50" in text

    def test_the_stale_comment_is_gone(self):
        src = _src("backend/game_logic/ai_diplomacy.py")
        assert "a bankrupt payer → white peace" not in src
        assert "cannot be squeezed, so the\n    # INDEMNITY is dropped" not in src


class TestTheNeutralityFloor:
    """GR-42: a chest under the floor sells nothing; the arm sends no letter."""

    def test_a_token_lump_is_never_offered(self, world):
        from backend.game_logic import ai_diplomacy as AD
        world.nation_gold["Prussia"] = 7
        terms = AD._build_proposal_terms("Prussia", "sell_neutrality", 0, world)
        assert not terms.get("sweeteners")

    def test_a_real_offer_stands(self, world):
        from backend.game_logic import ai_diplomacy as AD
        world.nation_gold["Prussia"] = 5000
        terms = AD._build_proposal_terms("Prussia", "sell_neutrality", 0, world)
        lumps = [s["value"] for s in terms.get("sweeteners") or [] if s.get("type") == "gold_lump"]
        assert lumps and lumps[0] >= AD.SELL_NEUTRALITY_BASE


class TestTheWhitePeaceWords:
    """GR-13: no "takes nothing" above the provinces the status quo concedes."""

    def test_the_line(self):
        from backend.game_logic.diplomatic_templates import resolve_settlement_voice_line
        line = resolve_settlement_voice_line(
            "settlement_advisory_white_peace_talleyrand", war_label="the War for Berry",
            price_line="No ally is left out by it.")
        assert "takes nothing" not in line
        assert "writes no clause: each side keeps what it holds" in line


class TestThePluralPossessive:
    """GR-19 and its siblings: SRX-22's one rule wherever a label takes a possessive."""

    def test_the_rule(self):
        from backend.display_names import possessive
        assert possessive("the 1792 frontiers") == "the 1792 frontiers'"
        assert possessive("Châtillon") == "Châtillon's"

    def test_no_label_takes_a_bare_apostrophe_s(self):
        for rel in ("backend/game_logic/ai_diplomacy.py", "backend/game_logic/dispatch.py"):
            src = _src(rel)
            assert not re.search(r"(LABELS\[[^]]*\]|label'\]|\blabel)\}'s ", src), rel


# ═══════════════════════════════ 3. THE COURTS ══════════════════════════════

class TestASleepingDesignWakesSilently:
    """GR-5 (AMB-5): Sweden's lone design, announced at T22 and again at T28."""

    def _view(self, design_id):
        return SimpleNamespace(id=design_id, title="Scourge of the Usurper", survival=False,
                               type="humble", regions=[], params={})

    def _run(self, world, monkeypatch, views):
        from backend.game_logic import agendas
        real = agendas.get_active_agenda
        monkeypatch.setattr(agendas, "get_active_agenda",
                            lambda n, w: views[n] if n in views else real(n, w))
        return [e for e in agendas.process_agenda_shifts(world) if e["nation"] == "Sweden"]

    def test_sleep_then_wake_the_same_design(self, world, monkeypatch):
        from backend.game_logic.agendas import DORMANT_DESIGN_MARK
        world.nation_agenda_seen["Sweden"] = ""
        assert len(self._run(world, monkeypatch, {"Sweden": self._view("scourge")})) == 1
        assert self._run(world, monkeypatch, {"Sweden": None}) == []
        assert world.nation_agenda_seen["Sweden"] == DORMANT_DESIGN_MARK + "scourge"
        assert self._run(world, monkeypatch, {"Sweden": None}) == []
        assert self._run(world, monkeypatch, {"Sweden": self._view("scourge")}) == []
        assert world.nation_agenda_seen["Sweden"] == "scourge"

    def test_waking_a_different_design_is_news(self, world, monkeypatch):
        world.nation_agenda_seen["Sweden"] = "~scourge"
        assert len(self._run(world, monkeypatch, {"Sweden": self._view("other")})) == 1

    def test_the_first_observation_is_still_silent(self, world, monkeypatch):
        world.nation_agenda_seen.pop("Sweden", None)
        assert self._run(world, monkeypatch, {"Sweden": self._view("scourge")}) == []
        world.nation_agenda_seen.pop("Sweden", None)
        assert self._run(world, monkeypatch, {"Sweden": None}) == []
        assert world.nation_agenda_seen["Sweden"] == ""


class TestTheRegenNeverDeletesMen:
    """GR-34: the regen fills toward the cap and keeps a pool already over it;
    men leave only for a pool that receives them."""

    def test_the_rule(self):
        from backend.models.world_state import regen_toward_cap
        assert regen_toward_cap(140000, 5000, 100000) == 140000
        assert regen_toward_cap(98000, 5000, 100000) == 100000
        assert regen_toward_cap(50000, 5000, 100000) == 55000

    def test_an_over_cap_pool_survives_the_regen(self, world):
        from backend.models.world_state import MAX_INFANTRY_POOL
        world.manpower_pools["France"]["infantry"] = MAX_INFANTRY_POOL + 40000
        world._process_manpower_regen()
        assert world.manpower_pools["France"]["infantry"] == MAX_INFANTRY_POOL + 40000

    def test_a_treaty_stream_to_a_court_without_a_pool_debits_nothing(self, world):
        before = int(world.manpower_pools["Austria"]["infantry"])
        world.manpower_pools.pop("Nowhere", None)
        world.active_treaties["Austria|Nowhere"] = {"clauses": [
            {"type": "manpower_per_turn", "from": "Austria", "to": "Nowhere", "amount": 5000}]}
        world._process_treaty_clauses()
        assert int(world.manpower_pools["Austria"]["infantry"]) == before

    def test_an_ultimatum_to_a_court_without_a_pool_takes_nothing(self, world):
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        before = int(world.manpower_pools["Austria"]["infantry"])
        world.manpower_pools.pop(world.player_nation)
        DiplomaticExecutor.__new__(DiplomaticExecutor)._apply_ultimatum_demands(
            [{"type": "manpower", "value": 5000}], "Austria", world)
        assert int(world.manpower_pools["Austria"]["infantry"]) == before


class TestThePlayerInHand:
    """GR-38: the counter-offer's relation check never falls back to a literal."""

    def test_no_literal(self):
        src = _src("backend/game_logic/ai_diplomacy.py")
        assert 'or "France", _counter_target' not in src
        assert 'or player_nation, _counter_target' in src


class TestEveryTraitNamesItsCodePath:
    """GR-45: the statecraft table's claims each name a code path that exists."""

    def test_the_named_paths_exist(self):
        from backend.game_logic import instruments, statecraft
        src = _src("backend/game_logic/statecraft.py")
        for name in ("create_compensation_bargain", "_renege", "has_renege_grievance"):
            assert name in src and hasattr(instruments, name), name
        assert "coercion_acceptance_delta" in src and hasattr(statecraft, "coercion_acceptance_delta")
        assert "sponsorship" in src and "guarantee" in src

    def test_the_table_points_there(self):
        cfg = _src("backend/nation_config.py")
        assert "code paths in statecraft.py" in cfg
        assert "the sponsorship + guarantee branches, statecraft.py" in cfg


class TestThePlayersLeadKeepsThePlayersRule:
    """GR-7: the courts' tree driving France no longer scores a field its
    executor refuses; every court keeps PT-F1."""

    def _stage(self, world):
        """A Russian corps on Prussian soil (France at peace with Prussia)
        beside a French corps."""
        if world.is_at_war(world.player_nation, "Prussia"):
            pytest.skip("France is at war with Prussia on this board")
        prussian = [r for r in world.regions.values() if r.controller == "Prussia"]
        for region in prussian:
            for adj in region.adjacent_regions:
                if adj not in world.regions or world.regions[adj].controller == "Prussia":
                    continue
                return region.name, adj
        pytest.skip("no Prussian province borders another court's")

    def test_the_predicate(self, world):
        from backend.ai.enemy_ai import EnemyAI
        field, beside = self._stage(world)
        ney, kutuzov, mack = world.marshals["Ney"], world.marshals["Kutuzov"], world.marshals["Mack"]
        ney.location, kutuzov.location = beside, field
        ai = EnemyAI(None)
        assert ai._lead_barred_from_field(ney, kutuzov, world) is True
        mack.location = beside
        ney.location = field
        assert ai._lead_barred_from_field(mack, ney, world) is False, "a court keeps PT-F1"

    def test_p4_never_picks_it(self, world, monkeypatch):
        from backend.ai.enemy_ai import EnemyAI
        field, beside = self._stage(world)
        ney, kutuzov = world.marshals["Ney"], world.marshals["Kutuzov"]
        ney.location, kutuzov.location = beside, field
        ney.strength, kutuzov.strength = 40000, 2000
        world.refresh_marshal_indexes()
        world.calculate_visibility()
        assert EnemyAI(None)._find_attack_opportunity(ney, world.player_nation, world) is None
        # the control: the same board with the rule held down engages him
        monkeypatch.setattr(EnemyAI, "_lead_barred_from_field", lambda *a, **k: False)
        assert EnemyAI(None)._find_attack_opportunity(ney, world.player_nation, world) is not None

    def test_the_four_rungs_read_it(self):
        src = _src("backend/ai/enemy_ai.py")
        assert src.count("self._lead_barred_from_field(") == 4


class TestThePursesNameTheBankrupt:
    """GR-12 (ECON-2): the overdraft is the Butcher's Bill and the mercy rule
    counts it; the driver's purse record names the courts whose count stands."""

    def _driver(self):
        spec = importlib.util.spec_from_file_location("t0d_drv", REPO / "tools" / "playtest_driver.py")
        drv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(drv)
        return drv

    def test_the_reader(self, world):
        drv = self._driver()
        world.nation_bankruptcy_turns = {"Austria": 1, "Prussia": 0}
        t = SimpleNamespace(backend_main=SimpleNamespace(world=world))
        assert drv._all_bankruptcies(t) == {"Austria": 1}
        assert drv._all_bankruptcies(SimpleNamespace()) is None

    def test_the_record(self, tmp_path):
        drv = self._driver()
        d = drv.Digest(tmp_path, {"name": "x", "seed": "s", "llm": "mock", "transport": "t", "policy": {}})
        d.ledger_line(100, 5, 50, purses={"Austria": -317}, bankrupt={"Austria": 1})
        d.ledger_line(100, 5, 50, purses={"Austria": 12}, bankrupt={})
        recs = [json.loads(x) for x in (tmp_path / "digest.jsonl").read_text(encoding="utf-8").splitlines()]
        purses = [r for r in recs if r["kind"] == "purses"]
        assert purses[0]["bankrupt"] == {"Austria": 1}
        assert "bankrupt" not in purses[1]

    def test_a_battles_bill_below_zero_is_counted(self, world):
        world.nation_gold["Austria"] = -300
        world._update_bankruptcy("Austria")
        assert world.nation_bankruptcy_turns["Austria"] == 1


# ═══════════════════════════════ 4. THE NARRATION ═══════════════════════════

class TestTheGarrisonCounterIsSaidOnce:
    """GR-63: the counter once a campaign, the fact of who stands there every time."""

    def test_said_then_latched(self, world):
        from backend.game_logic import dispatch as DS
        world.headline_lead_memory = {}
        lever = DS._home_captured_lever(world, "Provence", world.player_nation, {})
        assert DS.GARRISON_COUNTER_HEAD in lever
        DS._note_garrison_counter_said(world, {"text": "Sire — Provence has fallen." + lever}, [])
        assert world.headline_lead_memory["garrison_counter_said"] == int(world.current_turn)
        # the same morning, re-built or re-read, says it again
        assert DS.GARRISON_COUNTER_HEAD in DS._home_captured_lever(
            world, "Provence", world.player_nation, {})
        world.current_turn += 1
        later = DS._home_captured_lever(world, "Provence", world.player_nation, {})
        assert DS.GARRISON_COUNTER_HEAD not in later

    def test_an_unread_counter_is_not_latched(self, world):
        from backend.game_logic import dispatch as DS
        world.headline_lead_memory = {}
        DS._note_garrison_counter_said(world, {"text": "Sire — the courts stir."}, ["nothing"])
        assert "garrison_counter_said" not in world.headline_lead_memory

    def test_the_latch_rides_the_memory(self, world):
        from backend.game_logic import dispatch as DS
        world.headline_lead_memory = {}
        lever = DS._home_captured_lever(world, "Provence", world.player_nation, {})
        cand = {"class": "home_captured", "weight": 99, "identity": "home_captured:Provence",
                "text": "Sire — Provence has fallen." + lever, "fields": {}}
        DS._select_headline(world, [dict(cand)], record=True)
        assert "garrison_counter_said" in world.headline_lead_memory
        quiet = {"class": "home_captured", "weight": 99, "identity": "home_captured:Berry",
                 "text": "Sire — Berry has fallen.", "fields": {}}
        world.current_turn += 1
        DS._select_headline(world, [quiet], record=True)
        assert "garrison_counter_said" in world.headline_lead_memory


# ═══════════════════════════ 5. THE DOCS AND THE DEAD CODE ═══════════════════

class TestTheDocsSayTheAIRepeals:
    """GR-16 / GR-48: SFR-B14's repeal rung, named where "never repeals" stood."""

    @pytest.mark.parametrize("rel", ["docs/REFORMS_SPEC.md", "docs/ENEMY_AI_REFERENCE.md",
                                     "docs/SYSTEMS_REFERENCE.md"])
    def test_the_reference(self, rel):
        text = _src(rel)
        assert "ai_repeal_before_lapse" in text and "ai_holds_the_purse" in text, rel
        assert "**The AI never repeals.**" not in text
        assert "it never repeals." not in text

    def test_the_comment(self):
        assert "The AI never repeals" not in _src("backend/ai/enemy_ai.py")


class TestOneTruthForThePostBreakStates:
    """GR-43: the comment and DIPLOMACY_SPEC §7d state the map as written."""

    def _map(self):
        src = _src("backend/game_logic/diplomacy.py")
        block = src.split("post_break_map = {")[1].split("}")[0]
        return dict(re.findall(r'"([A-Z_]+)":\s*"([A-Z_]+)"', block))

    def test_the_spec_states_the_map(self):
        line = next(x for x in _src("docs/DIPLOMACY_SPEC.md").splitlines()
                    if "**Post-break state (E11):**" in x)
        stated = dict(re.findall(r"Breaking (?:a )?([A-Z_]+)(?: bond)? → ([A-Z_]+)", line))
        the_map = self._map()
        assert stated, line
        for broken, after in stated.items():
            assert the_map[broken] == after, (broken, after)
        for broken in ("ALLIANCE", "DEFENSIVE_ALLIANCE", "NON_AGGRESSION", "OPEN_BORDERS",
                       "PEACE", "VASSAL", "ARMISTICE"):
            assert broken in stated, broken

    def test_the_comment_says_two_rungs(self):
        src = _src("backend/game_logic/diplomacy.py")
        assert "one level below broken treaty" not in src
        assert "TWO rungs down `_DOWNGRADE_ORDER`" in src


class TestTheDeadWrapperAndTheSecondCopy:
    """GR-49: one reader per seam. GR-50: one source for the blockade's cut."""

    def test_the_wrapper_is_gone(self):
        from backend.game_logic import reforms
        assert not hasattr(reforms, "recruit_morale_bonus")

    def test_the_cut_has_one_source(self):
        src = _src("backend/game_logic/naval.py")
        assert src.count("(1.0 - BLOCKADE_TRADE_FACTOR)") == 1
        assert "blockade_cut_percent(_f)" in src
