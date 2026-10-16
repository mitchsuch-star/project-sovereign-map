"""DD-1 S8 Step 3 — THE VERBS: the three the depth campaign reached for and
could not touch (Pre-Deploy S8, October 12, 2026; `docs/PRE_DEPLOY_PLAN.md`
§3.1 "The verbs"; rules `SYSTEMS_REFERENCE.md` §109).

  the ask-back   `ask <ally> to return <province>` (SFR-D42): a liberated
                 home province an ally holds, asked back — ONE verdict
                 (`treaty.can_ask_return`, the clause in words) and ONE
                 answer (`treaty.ask_return_score`, the acceptance formula)
                 read by the chip under the ally's card, the typed road and
                 the AI's own ask-back tick (GR5); the grant moves the
                 province as a cession does; 1 DP when the ask is delivered.
  the bid        `bid for <court>` (SFR-D40): on an OPEN allegiance auction,
                 gold laid before the court — recorded on the auction,
                 weighed at the resolution beside relations and standing
                 patronage; the refusal when no auction is open names the
                 court and the ones in play; the chip on the auction's
                 notice and on the court's card; the bids round-trip a save.
  the followers  the truce's (SFR-D28's announce half): the armistice's
                 confirm and the incoming letter carry the ally whose war
                 the truce LEAVES RUNNING with our corps on her soil, and
                 the clients it BINDS; the dispatch's truce line says both.
  the words      no verb's refusal names a raw code.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy, treaty
from backend.game_logic import diplomacy as D
from backend.game_logic import game_end as GE
from backend.game_logic.intent import IntentView
from backend.game_logic.treaty import names_a_raw_code
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def boot() -> WorldState:
    with contextlib.redirect_stdout(io.StringIO()):
        return WorldState.from_scenario(str(SCENARIO))


@pytest.fixture
def w(boot) -> WorldState:
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


@pytest.fixture
def client(monkeypatch):
    """The typed road: `POST /command` on the shipped 1805 boot, the mock parser."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with contextlib.redirect_stdout(io.StringIO()):
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _post(client, command: str) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post("/command", json={"command": command}).json()


def _liberated(world, region: str, holder: str, taken_from: str = "Austria") -> None:
    """`holder` walked into `region` as a liberator: the capture road's title."""
    world.regions[region].controller = holder
    GE.record_province_title(world, region, GE.TITLE_CONQUEST, taken_from, holder)
    world.invalidate_active_nations_cache()


def _dispatched(world, event_type: str) -> list:
    return [e for e in getattr(world, "pending_dispatch_events", []) or []
            if e.get("type") == event_type]


def _logged(world, event_type: str) -> list:
    return [e for e in getattr(world, "event_log", []) or [] if e.get("type") == event_type]


# ═══════════════════════════════════════════════════════════════════════════
# the ask-back (SFR-D42)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheAskBack:

    def test_sfr_d42_the_ally_hands_the_liberated_soil_back(self, w):
        """Spain, an ally fighting beside us against Britain, holds Provence
        (taken from Austria): asked, she hands it back — the province moves
        as a cession does, the title is popped (home soil is title by
        construction), 1 DP is spent, the log and the dispatch say so."""
        _liberated(w, "Provence", "Spain")
        dp = w.diplomatic_points
        verdict = treaty.can_ask_return(w, "France", "Spain", "Provence")
        assert verdict.ok and verdict.target == "Spain"
        answer = treaty.ask_return_score(w, "France", "Spain", "Provence")
        assert answer["accepts"] and answer["components"]["common_enemy"] == "Britain"
        assert answer["components"]["road_name"] == "liberated"
        result = D.ask_return_province(w, "France", "Spain", "Provence")
        assert result["asked"] and result["accepted"]
        assert w.regions["Provence"].controller == "France"
        assert w.regions["Provence"].stability == 50
        assert "Provence" not in (getattr(w, "province_title", {}) or {})
        assert w.diplomatic_points == dp - treaty.ASK_RETURN_DP_COST
        assert "Spain" in result["message"] and "Provence" in result["message"]
        (event,) = _logged(w, "province_returned")
        assert (event["outcome"], event["nation"], event["target_nation"]) == ("returned", "France", "Spain")
        assert _dispatched(w, "province_returned")

    def test_the_court_declines_in_words_naming_the_shortfall(self, w):
        _liberated(w, "Provence", "Spain")
        w.nation_relations[w._make_diplo_key("France", "Spain")] = -20
        dp = w.diplomatic_points
        answer = treaty.ask_return_score(w, "France", "Spain", "Provence")
        assert not answer["accepts"] and answer["shortfall"] > 0
        result = D.ask_return_province(w, "France", "Spain", "Provence")
        assert result["asked"] and not result["accepted"]
        assert w.regions["Provence"].controller == "Spain"
        assert w.diplomatic_points == dp - 1, "a delivered ask is paid for whatever the answer"
        assert f"{answer['shortfall']} more" in result["message"]
        assert "Spain" in result["message"] and not names_a_raw_code(result["message"])
        (event,) = _logged(w, "province_returned")
        assert event["outcome"] == "refused" and event["shortfall"] == answer["shortfall"]
        assert not _dispatched(w, "province_returned"), "a refusal is the reply's, not the dispatch's"

    @pytest.mark.parametrize("stage, holder, region, clause", [
        ("ours", "Spain", "Provence", "already_ours"),
        ("not_our_soil", "Spain", "Aragon", "not_our_soil"),
        ("not_held", "Spain", "Provence", "not_held"),
        ("not_an_ally", "Prussia", "Rhineland", "not_an_ally"),
        ("war_purpose", "Spain", "Provence", "war_purpose"),
        ("no_dp", "Spain", "Provence", "no_dp"),
        ("unknown", "Spain", "Atlantis", "unknown_province"),
        ("no_region", "Spain", "", "no_province"),
    ])
    def test_the_clauses_in_words(self, w, stage, holder, region, clause):
        if stage == "not_held":
            _liberated(w, "Provence", "Austria")
        elif stage == "not_an_ally":
            _liberated(w, "Rhineland", "Prussia")
        elif stage == "war_purpose":
            _liberated(w, "Provence", "Spain")
            key = w._make_diplo_key("Spain", "Austria")
            w.war_objectives.setdefault(key, {})["Spain"] = D.create_war_objective(
                "conquest", "Spain", "Austria", ["Provence"], w.current_turn)
        elif stage == "no_dp":
            _liberated(w, "Provence", "Spain")
            w.diplomatic_points = 0
        dp = w.diplomatic_points
        verdict = treaty.can_ask_return(w, "France", holder, region)
        assert not verdict.ok and verdict.clause == clause
        assert verdict.message and not names_a_raw_code(verdict.message), verdict.message
        result = D.ask_return_province(w, "France", holder, region)
        assert not result["asked"] and result["message"] == verdict.message
        assert w.diplomatic_points == dp, "an ask that cannot be made costs nothing"
        assert not _logged(w, "province_returned")

    def test_the_chip_under_the_allys_card_reads_the_one_verdict(self, w):
        assert not [a for a in D.get_available_diplomatic_actions(w, "Spain")
                    if a["action"] == "ask_return_province"], "no chip without a held province"
        _liberated(w, "Provence", "Spain")
        (row,) = [a for a in D.get_available_diplomatic_actions(w, "Spain")
                  if a["action"] == "ask_return_province"]
        assert row["region"] == "Provence" and row["available"] is True
        assert row["likelihood"] == "Favorable" and row["dp_cost"] == treaty.ASK_RETURN_DP_COST
        w.diplomatic_points = 0
        (row,) = [a for a in D.get_available_diplomatic_actions(w, "Spain")
                  if a["action"] == "ask_return_province"]
        verdict = treaty.can_ask_return(w, "France", "Spain", "Provence")
        assert row["available"] is False and row["closed_clause"] == "no_dp"
        assert row["disabled_reason_display"] == verdict.message

    def test_the_typed_road_delivers_the_ask(self, client):
        tc, world = client
        _liberated(world, "Provence", "Spain")
        dp = world.diplomatic_points
        r = _post(tc, "Talleyrand, ask Spain to give back Provence")
        assert r.get("success") is True, r.get("message")
        assert "Spain" in r["message"] and "Provence" in r["message"]
        assert world.regions["Provence"].controller == "France"
        assert world.diplomatic_points == dp - 1

    @pytest.mark.parametrize("line", [
        "ask Spain to return Provence",
        "demand Provence back from Spain",
        "request the return of Provence from Spain",
    ])
    def test_the_phrasings_reach_the_desk(self, client, line):
        tc, world = client
        _liberated(world, "Provence", "Spain")
        r = _post(tc, line)
        assert r.get("success") is True, r.get("message")
        assert world.regions["Provence"].controller == "France"

    def test_a_bare_ask_names_what_the_ally_holds(self, client):
        tc, world = client
        _liberated(world, "Provence", "Spain")
        r = _post(tc, "ask Spain to return ")
        assert r.get("success") is False
        assert "Provence" in r["message"] and "Spain" in r["message"]
        assert not names_a_raw_code(r["message"])

    def test_the_ai_asks_back_through_the_same_road(self, w):
        """GR5: Saxony, Prussia's ally, holds Silesia (taken from Austria);
        the tick asks for it back through `ask_return_province` — and only
        when the formula says the ally would grant it."""
        D.set_diplomatic_state(w, "Prussia", "Saxony", "ALLIANCE", "test")
        w.nation_relations[w._make_diplo_key("Prussia", "Saxony")] = 60
        _liberated(w, "Silesia", "Saxony")
        events = ai_diplomacy.process_province_returns(w)
        assert [e["outcome"] for e in events] == ["returned"]
        assert events[0]["nation"] == "Prussia" and events[0]["target_nation"] == "Saxony"
        assert w.regions["Silesia"].controller == "Prussia"

    def test_the_ai_does_not_spend_an_ask_the_formula_refuses(self, w):
        D.set_diplomatic_state(w, "Prussia", "Saxony", "ALLIANCE", "test")
        w.nation_relations[w._make_diplo_key("Prussia", "Saxony")] = -30
        _liberated(w, "Silesia", "Saxony")
        assert ai_diplomacy.process_province_returns(w) == []
        assert w.regions["Silesia"].controller == "Saxony"
        assert not _logged(w, "province_returned")

    def test_the_boot_is_dormant(self, w):
        assert ai_diplomacy.process_province_returns(w) == []


# ═══════════════════════════════════════════════════════════════════════════
# the bid (SFR-D40)
# ═══════════════════════════════════════════════════════════════════════════

def _crest(monkeypatch, nations):
    """The auction tests' own chokepoint: the named minors crest at bandwagon."""
    def fake(nation, world):
        if nation in nations:
            return IntentView(nation=nation, want_id="test_design", want_title="Test",
                              want_type="acquire_regions", against="Austria", weight=66,
                              price="bandwagon")
        return IntentView(nation=nation, want_id=None, want_title=None, want_type=None,
                          against=None, weight=0, price="indifferent")
    monkeypatch.setattr("backend.game_logic.intent.get_nation_intent", fake)


def _open(world, nation="Denmark", turns=3):
    world.allegiance_auctions[nation] = {"opened_turn": int(world.current_turn),
                                         "resolves_turn": int(world.current_turn) + turns}


class TestTheBid:

    def test_sfr_d40_no_auction_names_the_court_and_the_ones_in_play(self, w):
        why = ai_diplomacy.allegiance_bid_refusal(w, "France", "Sardinia", 100)
        assert "Sardinia" in why and "No court" in why and not names_a_raw_code(why)
        _open(w, "Denmark")
        why = ai_diplomacy.allegiance_bid_refusal(w, "France", "Sardinia", 100)
        assert "Sardinia" in why and "Denmark" in why
        assert ai_diplomacy.allegiance_bid_refusal(w, "France", "Denmark", 100) == ""

    def test_the_bid_moves_the_gold_and_is_recorded(self, client):
        tc, world = client
        _open(world, "Denmark")
        gold, dp = world.nation_gold["France"], world.diplomatic_points
        danish = int(world.nation_gold.get("Denmark", 0) or 0)
        r = _post(tc, "Talleyrand, bid for Denmark, 200 gold")
        assert r.get("success") is True, r.get("message")
        assert world.nation_gold["France"] == gold - 200
        assert world.nation_gold["Denmark"] == danish + 200
        assert world.allegiance_auctions["Denmark"]["bids"] == {"France": 200}
        assert world.diplomatic_points == dp - 1
        assert "200" in r["message"] and "Denmark" in r["message"]
        r = _post(tc, "bid for Denmark")
        assert r.get("success") is True
        assert world.allegiance_auctions["Denmark"]["bids"] == {"France": 200 + ai_diplomacy.DEFAULT_ALLEGIANCE_BID}
        (first, second) = _logged(world, "allegiance_bid")
        assert (first["gold"], second["total"]) == (200, 300)

    def test_the_refusals_cost_nothing_and_name_no_code(self, client):
        tc, world = client
        gold, dp = world.nation_gold["France"], world.diplomatic_points
        r = _post(tc, "bid for Sardinia")
        assert r.get("success") is False and "Sardinia" in r["message"]
        assert not names_a_raw_code(r["message"])
        assert (world.nation_gold["France"], world.diplomatic_points) == (gold, dp)
        _open(world, "Denmark")
        world.nation_gold["France"] = 50
        r = _post(tc, "bid for Denmark, 100 gold")
        assert r.get("success") is False and "50" in r["message"]
        assert world.allegiance_auctions["Denmark"].get("bids") is None

    def test_the_bid_decides_the_flip(self, w, monkeypatch):
        """Britain leans ahead on relations; France's gold outweighs it
        through the SAME divisor standing patronage uses, and France wins
        the auction — the pact arriving as an offer (SF-V1's net)."""
        _crest(monkeypatch, {"Denmark"})
        monkeypatch.setattr("backend.game_logic.coalition.identify_ranked_bloc_shares",
                            lambda world: [("Britain", 0.3), ("Austria", 0.2)])
        _open(w, "Denmark", turns=0)
        w.nation_relations[w._make_diplo_key("Denmark", "Britain")] = 30
        w.nation_relations[w._make_diplo_key("Denmark", "France")] = 20
        w.nation_gold["France"] = 5000
        lose = WorldState.from_dict(w.to_dict())
        (event,) = [e for e in ai_diplomacy.process_allegiance_auctions(lose)
                    if e["type"] == "allegiance_auction_resolved"]
        assert event["winner"] == "Britain", "without the bid Britain's lean wins"
        bid = ai_diplomacy.place_allegiance_bid(w, "France", "Denmark", 300)
        assert bid["success"], bid["message"]
        (event,) = [e for e in ai_diplomacy.process_allegiance_auctions(w)
                    if e["type"] == "allegiance_auction_resolved"]
        assert event["winner"] == "France" and event["outcome"] in ("player_offer", "player_won_no_pact")

    def test_the_chip_and_the_notice_carry_the_verb(self, w, monkeypatch):
        assert not [a for a in D.get_available_diplomatic_actions(w, "Denmark")
                    if a["action"] == "bid_for_allegiance"]
        _crest(monkeypatch, {"Denmark"})
        ai_diplomacy.process_allegiance_auctions(w)
        notice = [n for n in w.notifications.to_list() if "Denmark" in str(n.get("title", ""))]
        assert notice, "the flip is announced"
        details = notice[-1].get("details") or {}
        assert details.get("action_command") == f"bid for Denmark, {ai_diplomacy.DEFAULT_ALLEGIANCE_BID} gold"
        (row,) = [a for a in D.get_available_diplomatic_actions(w, "Denmark")
                  if a["action"] == "bid_for_allegiance"]
        assert row["available"] is True and row["gold_cost"] == ai_diplomacy.DEFAULT_ALLEGIANCE_BID
        w.diplomatic_points = 0
        (row,) = [a for a in D.get_available_diplomatic_actions(w, "Denmark")
                  if a["action"] == "bid_for_allegiance"]
        assert row["available"] is False
        assert row["disabled_reason_display"] == ai_diplomacy.allegiance_bid_refusal(
            w, "France", "Denmark", ai_diplomacy.DEFAULT_ALLEGIANCE_BID)

    def test_the_bids_round_trip_the_save(self, w):
        _open(w, "Denmark")
        w.nation_gold["France"] = 1000
        ai_diplomacy.place_allegiance_bid(w, "France", "Denmark", 150)
        again = WorldState.from_dict(json.loads(json.dumps(w.to_dict(), default=str)))
        assert again.allegiance_auctions["Denmark"]["bids"] == {"France": 150}

    def test_a_bidder_is_a_suitor_by_that_act(self, w, monkeypatch):
        """A court outside the ranked suitors who laid gold is weighed."""
        _crest(monkeypatch, {"Denmark"})
        monkeypatch.setattr("backend.game_logic.coalition.identify_ranked_bloc_shares",
                            lambda world: [("Britain", 0.3)])
        monkeypatch.setattr("backend.game_logic.agendas._hegemon", lambda world: ("Britain", 0.3))
        _open(w, "Denmark", turns=0)
        w.nation_relations[w._make_diplo_key("Denmark", "Britain")] = 5
        w.nation_relations[w._make_diplo_key("Denmark", "France")] = 0
        w.nation_relations[w._make_diplo_key("Denmark", "Sweden")] = 40
        w.nation_gold["Sweden"] = 1000
        bid = ai_diplomacy.place_allegiance_bid(w, "Sweden", "Denmark", 100)
        assert bid["success"], bid["message"]
        (event,) = [e for e in ai_diplomacy.process_allegiance_auctions(w)
                    if e["type"] == "allegiance_auction_resolved"]
        assert event["winner"] == "Sweden"


# ═══════════════════════════════════════════════════════════════════════════
# the truce's followers (SFR-D28's announce half)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheTrucesFollowers:

    def _stand_in_bavaria(self, world):
        """Ney and Lannes march onto Bavarian soil; whoever of ours already
        stands there (the boot's own dispositions) is counted with them."""
        bavarian = list(world.get_nation_regions("Bavaria"))
        world.marshals["Ney"].location = bavarian[0]
        world.marshals["Lannes"].location = bavarian[0]
        return len([m for m in world.marshals.values()
                    if m.nation == "France" and m.location in bavarian])

    def _clear_bavaria(self, world):
        bavarian = set(world.get_nation_regions("Bavaria"))
        for m in world.marshals.values():
            if m.nation == "France" and m.location in bavarian:
                m.location = "Paris"

    def test_sfr_d28_the_confirm_names_the_ally_whose_war_runs_on(self, w):
        """Bavaria, an ally (not a client) at war with Austria, is named on
        the armistice's confirm with the French corps standing on her soil."""
        n = self._stand_in_bavaria(w)
        snap = D.build_war_context_snapshot(w, "France", "Austria", "armistice_winning")
        (row,) = [c for c in snap["commitment_conflicts"] if c["conflict_type"] == "war_runs_on"]
        assert row["severity"] == "WARNING" and row["affected_entity"] == "Bavaria"
        assert "Bavaria stays at war with Austria" in row["display"]
        assert f"{n} French corps stand on Bavarian soil under the truce" in row["display"]
        assert {"Lannes", "Ney"} <= set(row["detail"]["corps"]) and len(row["detail"]["corps"]) == n
        assert not any(c["severity"] == "HARD_STOP" for c in snap["commitment_conflicts"])

    def test_the_incoming_letter_says_it_too(self, w):
        self._stand_in_bavaria(w)
        snap = D.build_war_context_snapshot(w, "France", "Austria", "armistice_winning",
                                            incoming=True)
        assert any(c["conflict_type"] == "war_runs_on" for c in snap["commitment_conflicts"])

    def test_a_peace_carries_the_ally_a_truce_leaves_running(self, w):
        # PC-R1 (S13e part 1): the peace's conflicts name Bavaria CARRIED IN
        # (never a HARD_STOP); only the truce names her war running on.
        conflicts = D.get_peace_commitment_conflicts(w, "France", "Austria", [])
        assert any(c["severity"] == "INFO" and c["conflict_type"] == "carried_in"
                   for c in conflicts)
        assert not any(c["severity"] == "HARD_STOP" for c in conflicts)
        assert not any(c["conflict_type"] == "war_runs_on" for c in conflicts)

    def test_the_client_is_bound_and_the_ally_runs_on(self, w):
        n = self._stand_in_bavaria(w)
        line = D.truce_followers_line(w, "France", "Austria")
        assert "Kingdom of Italy" in line, line        # the client follows the lord
        assert "Bavaria stays at war with Austria" in line
        assert f"{n} French corps stand on Bavarian soil" in line
        assert not names_a_raw_code(line)

    def test_no_corps_on_her_soil_is_said_too(self, w):
        self._clear_bavaria(w)
        line = D.truce_followers_line(w, "France", "Austria")
        assert "no corps of ours stands on Bavarian soil" in line, line

    def test_the_dispatch_names_them_on_the_truce(self, w):
        n = self._stand_in_bavaria(w)
        from backend.game_logic.dispatch import _format_dispatch_event_text
        variant = D.armistice_variant_for(w, "France", "Austria")
        with contextlib.redirect_stdout(io.StringIO()):
            event = w._ratify_treaty({"type": variant, "proposer_nation": "France",
                                      "target_nation": "Austria", "sweeteners": [],
                                      "demands": [], "clauses": []})
        assert event and event.get("type") != "diplomatic_treaty_failed", event
        assert w.get_diplomatic_state("France", "Austria") == "ARMISTICE"
        (queued,) = _dispatched(w, "armistice_ratified")
        text = _format_dispatch_event_text("armistice_ratified", queued["template_vars"])
        assert "A truce with Austria" in text
        assert "Bavaria stays at war with Austria" in text
        assert f"{n} French corps stand on Bavarian soil under the truce" in text
        assert "{followers}" not in text

    def test_a_truce_with_nobody_following_says_nothing_extra(self, w):
        """Spain at peace with everyone we truce with: the line is empty and
        the dispatch template renders clean."""
        from backend.game_logic.dispatch import _format_dispatch_event_text
        assert D.truce_followers_line(w, "France", "Prussia") == ""
        # PC-R2 / PC-F44: the line carries what the truce keeps and where it
        # heads (`{keeps}` / `{heading}` from `truce_words`)
        text = _format_dispatch_event_text("armistice_ratified", {
            "proposer_nation": "France", "target_nation": "Prussia", "other": "Prussia",
            "turns": 10, "thaw": 20, "keeps": " The ledger stands.",
            "heading": " At expiry: the war resumes where it stood.", "followers": ""})
        assert text.endswith("At expiry: the war resumes where it stood.")


# ═══════════════════════════════════════════════════════════════════════════
# the recipe
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRecipe:

    def test_the_actions_are_registered_everywhere(self):
        from backend.ai.validation import DIPLOMATIC_ACTION_ALLOWLIST, VALID_ACTIONS
        from backend.display_names import ACTION_DISPLAY, DEFIANCE_DISPLAY, OBJECTION_DISPLAY
        for action in ("diplomatic_ask_return", "diplomatic_bid"):
            assert action in VALID_ACTIONS and action in DIPLOMATIC_ACTION_ALLOWLIST
            assert action in ACTION_DISPLAY and action in OBJECTION_DISPLAY
            assert action in DEFIANCE_DISPLAY

    def test_the_log_knows_both_events(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP, format_event_oneliner
        for etype in ("allegiance_bid", "province_returned"):
            assert etype in CAMPAIGN_LOG_TYPES and CATEGORY_MAP[etype] == "diplomacy"
        line = format_event_oneliner({"type": "province_returned", "nation": "France",
                                      "target_nation": "Spain", "region": "Provence",
                                      "outcome": "returned"})
        assert "Spain" in line and "Provence" in line
        line = format_event_oneliner({"type": "allegiance_bid", "nation": "France",
                                      "target_nation": "Denmark", "gold": 100, "total": 100,
                                      "resolves_turn": 4})
        assert "Denmark" in line and "100" in line

    def test_the_wizard_echoes_both_verbs(self):
        src = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
               / "scripts" / "diplomacy_wizard.gd").read_text(encoding="utf-8")
        assert '"ask_return_province":' in src and '"bid_for_allegiance":' in src
        assert '"ask " + nation + " to return " + ask_region' in src

    def test_the_routed_words_are_regenerated(self):
        from backend.ai.routed_order_words import ROUTED_ORDER_WORDS
        assert {"bid", "bids", "outbid", "asks", "requests"} <= set(ROUTED_ORDER_WORDS)
