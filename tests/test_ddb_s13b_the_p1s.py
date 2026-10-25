"""Pre-Deploy S13b part 1, slice S13b-1 — DD-B's three P1s (October 14, 2026;
`docs/BUG_FIXES.md` §DD-B; the rulings `docs/audits/DD_B_RULINGS_2026_10_14.md`
§2 D8 / D9; rules `SYSTEMS_REFERENCE.md` §116).

  DDB-1  the objection arrives WITH the proposal, bound to its dialogue, before
         anything is sent; "Use Talleyrand's suggestion" APPLIES a draft he will
         carry (the tribute stepped down the generous rung until his objection
         no longer raises) and sends nothing; Proceed sends as drafted, Modify
         returns to the draft (nothing sent, no DP, nothing in transit), Cancel
         drops it free; "Not Now" never raises it; Harsher / More generous /
         Adjust survive the rebuild; the Cabinet's band word is the draft's own.
  DDB-2  France is ASKED (DDB-D8): an ally's offensive war posts a call to arms
         — Join attaches France to the ally's war instance, Refuse is the
         offensive-refusal episode, two turns unanswered is a refusal at the
         same price; a court France joined at a call may be offered a priced
         separate peace; the full alliance states the binding and the ally's
         design; an AI-AI cascade is unchanged.
  DDB-3  a truce pauses the shared war (DDB-D9): a serving contingent holds its
         post through its lord's truce (no march home, no Road Home order, no
         judging); the peace walks it home under its own colours, and the peace
         names the contingent it releases; an AI lord's contingent alike.

Drives the real endpoints (the in-process TestClient on the shipped 1805 boot)
where the player acts, and the world's own turn seams where the engine does.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.commands.diplomatic_defiance import (
    draft_terms_talleyrand_supports,
    objection_fires,
)
from backend.game_logic import call_to_arms as CTA
from backend.game_logic import contingent as CG
from backend.game_logic import diplomacy as D
from backend.game_logic import withdrawal as WD
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
    """The player's roads: the endpoints on the shipped 1805 boot, the mock parser."""
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


def _post(client, path: str, body: dict) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return client.post(path, json=body).json()


def _actions(dialogue: dict) -> list:
    return [o.get("action") for o in (dialogue or {}).get("options", [])]


def _option(dialogue: dict, action: str) -> dict:
    return next(o for o in dialogue.get("options", []) if o.get("action") == action)


# ═══════════════════════════════════════════════════════════════════════════
# DDB-1 — the objection arrives with the proposal
# ═══════════════════════════════════════════════════════════════════════════

class TestDDB1:
    """The diplomacy-first player's Spain vassalage (#23/#24/#31/#32): a rich
    Spain makes the drafted tribute objectionable (vassalage +0.3, 600 gold a
    turn ±20% → harshness > 0.7 at every jitter)."""

    @pytest.fixture
    def spain(self, client):
        c, w = client
        w.nation_gold["Spain"] = 4000
        w.diplomatic_points = 8
        r = _post(c, "/command", {"command": "Talleyrand, propose vassalage to Spain"})
        return c, w, r

    def test_the_objection_rides_the_first_response_with_the_dialogues_id(self, spain):
        _c, w, r = spain
        dialogue = r["diplomatic_dialogue"]
        objection = r.get("diplomatic_objection")
        assert objection, "the objection stands WITH the proposal, before anything is sent"
        assert objection["dialogue_id"] == dialogue["dialogue_id"]
        assert w.diplomatic_points == 8, "nothing is charged before Send"
        assert w.proposal_in_transit is None and w.talleyrand_state != "IN_TRANSIT"
        assert w.diplomatic_objection_popup is None, "delivered, not left to drain later"
        assert objection["talleyrand_draft"].startswith("the tribute stepped down to")

    def test_the_draft_keeps_its_controls_under_the_objection(self, spain):
        _c, _w, r = spain
        actions = _actions(r["diplomatic_dialogue"])
        for kept in ("modify_harsh", "modify_generous", "adjust_terms", "reconsider"):
            assert kept in actions, f"{kept} survives the objection's rebuild"
        assert "send_override" in actions and "apply_suggestion" in actions
        assert "execute_proposal" not in actions and "send_suggested" not in actions
        send = _option(r["diplomatic_dialogue"], "send_override")
        assert "my terms" not in send["label"].lower(), "the player wrote no terms (#23)"

    def test_modify_returns_to_the_draft_with_nothing_sent(self, spain):
        c, w, r = spain
        did = r["diplomatic_dialogue"]["dialogue_id"]
        out = _post(c, "/respond_to_diplomatic_objection", {"choice": "modify", "dialogue_id": did})
        assert out["success"] and out["diplomatic_dialogue"]["dialogue_id"] == did
        assert "apply_suggestion" in _actions(out["diplomatic_dialogue"])
        assert w.diplomatic_points == 8
        assert w.proposal_in_transit is None and w.talleyrand_state != "IN_TRANSIT"

    def test_the_suggestion_applies_terms_that_pass_and_sends_nothing(self, spain):
        c, w, r = spain
        did = r["diplomatic_dialogue"]["dialogue_id"]
        drafted = _option(r["diplomatic_dialogue"], "send_override")["terms"]
        out = _post(c, "/respond_to_diplomatic_dialogue",
                    {"choice": "apply_suggestion", "dialogue_id": did})
        assert out["success"]
        redraft = out["diplomatic_dialogue"]
        assert redraft["dialogue_id"] == did, "the same matter keeps its identity"
        terms = _option(redraft, "execute_proposal")["terms"]
        assert not objection_fires({"type": "vassalage", "target_nation": "Spain",
                                    "demands": terms["demands"],
                                    "sweeteners": terms["sweeteners"]}, w)
        assert terms["demands"][0]["value"] < drafted["demands"][0]["value"]
        for kept in ("modify_harsh", "modify_generous", "adjust_terms", "reconsider"):
            assert kept in _actions(redraft)
        assert w.diplomatic_points == 8 and w.proposal_in_transit is None
        assert "Nothing has been sent" in redraft["talleyrand_text"]
        sent = _post(c, "/respond_to_diplomatic_dialogue",
                     {"choice": "execute_proposal", "dialogue_id": did})
        assert sent["success"] and w.proposal_in_transit is not None
        assert w.diplomatic_points == 5, "Send is the player's own click, priced then"
        assert w.proposal_in_transit["proposal"]["demands"] == terms["demands"]

    def test_proceed_sends_as_drafted(self, spain):
        c, w, r = spain
        did = r["diplomatic_dialogue"]["dialogue_id"]
        drafted = _option(r["diplomatic_dialogue"], "send_override")["terms"]
        out = _post(c, "/respond_to_diplomatic_objection", {"choice": "proceed", "dialogue_id": did})
        assert out["success"] and "despite his objections" in out["message"]
        assert w.proposal_in_transit["proposal"]["demands"] == drafted["demands"]

    def test_cancel_drops_it_at_no_cost(self, spain):
        c, w, r = spain
        did = r["diplomatic_dialogue"]["dialogue_id"]
        out = _post(c, "/respond_to_diplomatic_objection", {"choice": "cancel", "dialogue_id": did})
        assert out["success"] and w.pending_diplomatic_dialogue is None
        assert w.diplomatic_points == 8 and w.proposal_in_transit is None

    def test_not_now_closes_without_raising_the_objection(self, spain):
        c, w, r = spain
        did = r["diplomatic_dialogue"]["dialogue_id"]
        _post(c, "/respond_to_diplomatic_objection", {"choice": "modify", "dialogue_id": did})
        out = _post(c, "/respond_to_diplomatic_dialogue", {"choice": "reconsider", "dialogue_id": did})
        assert out["success"] and not out.get("diplomatic_objection")
        nxt = _post(c, "/command", {"command": "Ney, status"})
        assert not nxt.get("diplomatic_objection"), "never raised on a dropped proposal (#32)"
        assert w.diplomatic_points == 8 and w.proposal_in_transit is None

    def test_a_stale_answer_changes_nothing(self, spain):
        c, w, r = spain
        out = _post(c, "/respond_to_diplomatic_objection",
                    {"choice": "proceed", "dialogue_id": int(r["diplomatic_dialogue"]["dialogue_id"]) + 99})
        assert not out["success"] and w.proposal_in_transit is None
        assert w.diplomatic_points == 8

    def test_the_cabinets_band_word_is_the_drafts_own(self, w):
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        w.nation_gold["Spain"] = 4000
        row = next(a for a in D.get_available_diplomatic_actions(w, "Spain")
                   if a["action"] == "propose_vassal")
        draft = generate_suggested_terms("Spain", "vassalage", w, deterministic=True)
        score = D.calculate_acceptance({
            "type": "vassalage", "proposer_nation": "France", "target_nation": "Spain",
            "sweeteners": draft["sweeteners"], "demands": draft["demands"],
            "clauses": draft["clauses"]}, w)["score"]
        assert draft["demands"], "the click opens a draft with a tribute"
        assert row["likelihood_score"] == int(score)
        bare = D.calculate_acceptance({
            "type": "vassalage", "proposer_nation": "France", "target_nation": "Spain",
            "sweeteners": [], "demands": [], "clauses": []}, w)["score"]
        assert row["likelihood_score"] < int(bare), "no longer scored on a package with no terms"

    def test_no_round_passing_is_the_vassalage_with_no_tribute(self, w):
        terms = {"demands": [{"type": "territory_cede", "regions": ["Aragon", "Navarre", "Andalusia"]},
                             {"type": "gold_per_turn", "value": 900}], "sweeteners": []}
        draft = draft_terms_talleyrand_supports(
            terms, proposal_type="vassalage", target_nation="Spain", world=w)
        assert draft["talleyrand_draft"] == "no_tribute" and draft["demands"] == []
        from backend.commands.diplomatic_defiance import talleyrand_draft_line
        assert "no tribute" in talleyrand_draft_line(
            draft, proposal_type="vassalage", target_nation="Spain")
        assert terms["demands"][1]["value"] == 900, "the input is never mutated"


# ═══════════════════════════════════════════════════════════════════════════
# DDB-2 — France is asked (DDB-D8)
# ═══════════════════════════════════════════════════════════════════════════

def _ally_prussia(w) -> None:
    D.set_diplomatic_state(w, "France", "Prussia", "ALLIANCE", "test_fixture")
    w.nation_relations[w._make_diplo_key("France", "Prussia")] = 60
    w.invalidate_active_nations_cache()


def _prussia_declares(w) -> dict:
    with contextlib.redirect_stdout(io.StringIO()):
        return D.declare_war(w, "Prussia", "Hanover")


def _call_letter(w):
    dm = w.dialogue_manager
    return next((d for d in [dm.peek()] + list(dm.iter_queue())
                 if d and CTA.is_call_to_arms(d)), None)


class TestDDB2:
    """The diplomacy #29 shape: Prussia's design war on Hanover ("The
    Hanoverian Prize") while France holds a full alliance with her."""

    @pytest.fixture
    def called(self, client):
        c, w = client
        _ally_prussia(w)
        result = _prussia_declares(w)
        return c, w, result

    def test_the_letter_is_posted_and_france_is_not_at_war(self, called):
        _c, w, result = called
        assert w.get_diplomatic_state("France", "Hanover") == "PEACE"
        assert w.is_at_war("Prussia", "Hanover")
        assert [e["path"] for e in result["war_entry_ledger"] if e["nation"] == "France"] == ["call_posted"]
        letter = _call_letter(w)
        assert letter is not None and letter["type"] == "incoming_proposal"
        assert _actions(letter) == ["accept_ai_proposal", "reject_ai_proposal"], "Join / Refuse, no Counter"
        head = letter["popup_payload"]["clauses"][0]
        assert head.startswith("Prussia calls on her ally to join her war on Hanover — join, or refuse at a price:")
        assert "unanswered in two turns, it is refused" in head
        terms = CTA.call_terms_of(letter)
        price = CTA.refusal_price(w, "France", "Prussia", "Hanover")
        assert f"reliability {price['reliability_delta']:+d}" in head
        assert terms["war_id"] and terms["answer_by_turn"] == terms["issued_turn"] + 2
        assert letter["popup_payload"]["is_call_to_arms"] is True

    def test_join_attaches_france_to_prussias_war(self, called):
        c, w, _result = called
        letter = _call_letter(w)
        war_id = CTA.call_terms_of(letter)["war_id"]
        relation = w.nation_relations.get(w._make_diplo_key("France", "Hanover"), 0)
        out = _post(c, "/respond_to_diplomatic_dialogue",
                    {"choice": "accept", "dialogue_id": letter["dialogue_id"]})
        assert out["success"] and w.get_diplomatic_state("France", "Hanover") == "WAR"
        instance = w.war_instances[war_id]
        assert "France" in instance["attackers"]
        meta = instance["diplo_key_meta"][w._make_diplo_key("France", "Hanover")]
        assert meta["entry_path"] == CTA.CALL_ACCEPTED_PATH
        assert CTA.entered_by_call(w, "France", "Hanover")
        assert w.nation_relations[w._make_diplo_key("France", "Hanover")] <= relation - 20
        ledger = [e for e in w.event_log if e.get("type") == "war_entry_ledger"]
        assert ledger[-1]["entries"][0]["path"] == "call_accepted"
        from backend.game_logic.game_end import player_drew_the_sword
        assert player_drew_the_sword(w, "France", "Hanover", CTA.CALL_ACCEPTED_REASON)

    def test_refuse_is_the_offensive_refusal_episode(self, called):
        c, w, _result = called
        letter = _call_letter(w)
        price = CTA.refusal_price(w, "France", "Prussia", "Hanover")
        out = _post(c, "/respond_to_diplomatic_dialogue",
                    {"choice": "reject", "dialogue_id": letter["dialogue_id"]})
        assert out["success"] and w.get_diplomatic_state("France", "Hanover") == "PEACE"
        (episode,) = [e for e in w.event_log if e.get("type") == D.DG4_EVENT_REFUSED_OFFENSIVE]
        assert (episode["breaker"], episode["victim"]) == ("France", "Prussia")
        assert episode["resolved_reliability_delta"] == price["reliability_delta"]
        assert episode["witness_relation_delta"] == price["witness_relation_delta"]
        assert episode["victim_strikes"] >= 1 and episode["witness_count"] >= 1
        assert _call_letter(w) is None

    def test_two_turns_unanswered_is_refused_at_the_same_price(self, called):
        """The letter says "answer by the end of turn N" (its issue turn + 2,
        `GUARANTEE_GRACE_TURNS`): a call that arrives in the AI's phase of
        turn T is read on T+1 and T+2. This fixture declares inside turn T,
        so the call stands through the ends of T and T+1 and lapses at the
        end of T+2 — never earlier than the turn it names."""
        c, w, _result = called
        price = CTA.refusal_price(w, "France", "Prussia", "Hanover")
        answer_by = CTA.call_terms_of(_call_letter(w))["answer_by_turn"]
        while int(w.current_turn) < answer_by:
            _post(c, "/command", {"command": "end turn"})
            assert _call_letter(w) is not None, f"the call stands until the end of turn {answer_by}"
            assert not [e for e in w.event_log if e.get("type") == D.DG4_EVENT_REFUSED_OFFENSIVE]
        _post(c, "/command", {"command": "end turn"})
        assert _call_letter(w) is None
        (episode,) = [e for e in w.event_log if e.get("type") == D.DG4_EVENT_REFUSED_OFFENSIVE]
        assert episode["resolved_reliability_delta"] == price["reliability_delta"]
        assert episode["call_context"]["how"] == "unanswered"
        (row,) = [e for e in w.event_log if e.get("type") == "offer_lapsed"
                  and e.get("proposal_type") == "call_to_arms"]
        assert row["call_to_arms"]["penalty"] is True
        assert w.get_diplomatic_state("France", "Hanover") == "PEACE"

    def test_after_join_a_separate_peace_is_offered_and_priced(self, called):
        c, w, _result = called
        letter = _call_letter(w)
        _post(c, "/respond_to_diplomatic_dialogue",
              {"choice": "accept", "dialogue_id": letter["dialogue_id"]})
        rows = {a["action"]: a for a in D.get_available_diplomatic_actions(w, "Hanover")}
        assert rows["open_settlement"]["available"] is False
        assert rows["propose_peace"]["available"] is True, "past not_side_leader"
        conflicts = D.get_peace_commitment_conflicts(w, "France", "Hanover", [])
        assert not [x for x in conflicts if x["severity"] == "HARD_STOP"]
        assert any(x["affected_entity"] == "Prussia" and x["severity"] == "WARNING" for x in conflicts)
        snapshot = D.build_war_context_snapshot(w, "France", "Hanover", "peace")
        # S14E-X204 (flipped): the price is on the paradox row now - one ally,
        # one sentence; the fallout row that priced her in other words is folded in.
        assert not [f for f in snapshot["fallout_warnings"]
                    if f.get("warning_type") == "separate_peace_ally"]
        (priced,) = [c for c in snapshot["commitment_conflicts"]
                     if c.get("affected_entity") == "Prussia"]
        assert priced["conflict_type"] == "paradox" and priced["detail"]["relation_change"] < 0
        assert "joined at an ally's call" in priced["display"]
        assert f"({priced['detail']['relation_change']} relation)" in priced["display"]
        from backend.game_logic.treaty import can_sign
        assert can_sign(w, {"type": "peace", "proposer_nation": "France", "target_nation": "Hanover",
                            "sweeteners": [], "demands": [], "clauses": []}, at_send=True).ok

    def test_a_war_france_did_not_join_keeps_the_paradox(self, w):
        _ally_prussia(w)
        D.set_diplomatic_state(w, "France", "Hanover", "WAR", "war_declaration")
        _prussia_declares(w)
        assert not CTA.entered_by_call(w, "France", "Hanover")
        conflicts = D.get_peace_commitment_conflicts(w, "France", "Hanover", [])
        # PC-R1 (S13e part 1, §46 B): never a stop — Prussia's pair is either
        # carried in by France's peace (France leads the instance) or left
        # fighting at a named price; DDB-2's own "joined at a call" words do
        # not apply to a war France declared herself.
        prussia = [x for x in conflicts if x["affected_entity"] == "Prussia"]
        assert prussia and prussia[0]["severity"] in ("WARNING", "INFO")
        assert not any(x["severity"] == "HARD_STOP" for x in conflicts)
        assert "joined at an ally's call" not in prussia[0]["display"]

    def test_the_counter_is_refused(self, called):
        c, w, _result = called
        letter = _call_letter(w)
        out = _post(c, "/respond_to_diplomatic_dialogue",
                    {"choice": "counter_ai_proposal", "dialogue_id": letter["dialogue_id"]})
        assert not out["success"] and _call_letter(w) is not None

    def test_the_full_alliance_states_the_binding_and_the_design(self, client):
        c, w = client
        D.set_diplomatic_state(w, "France", "Prussia", "DEFENSIVE_ALLIANCE", "test_fixture")
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = 80
        w.diplomatic_points = 10
        r = _post(c, "/command", {"command": "Talleyrand, propose alliance to Prussia"})
        summary = r["diplomatic_dialogue"]["proposal_terms_summary"]
        assert "Binds France to Prussia's wars, offensive and defensive" in summary
        assert "Prussia's design: The Hanoverian Prize on Hanover" in summary

    def test_an_ai_ai_cascade_is_unchanged(self, w):
        D.set_diplomatic_state(w, "Russia", "Prussia", "ALLIANCE", "test_fixture")
        w.nation_relations[w._make_diplo_key("Russia", "Prussia")] = 60
        w.invalidate_active_nations_cache()
        result = _prussia_declares(w)
        assert w.get_diplomatic_state("Russia", "Hanover") == "WAR"
        assert any(e["nation"] == "Russia" and e["path"] == "honored" for e in result["war_entry_ledger"])
        assert _call_letter(w) is None


# ═══════════════════════════════════════════════════════════════════════════
# DDB-3 — a truce pauses the shared war (DDB-D9)
# ═══════════════════════════════════════════════════════════════════════════

def _post_contingent(w, vassal: str, post: str, lord: str) -> object:
    with contextlib.redirect_stdout(io.StringIO()):
        CG.raise_contingent(w, vassal)
    record = CG.contingent_record(w, vassal)
    assert record and record["lord"] == lord
    marshal = w.marshals[record["marshal"]]
    w.regions[post].controller = lord
    w.invalidate_active_nations_cache()
    marshal.location = post
    marshal.strategic_order = None
    return marshal


def _truce(w, lord: str, vassal: str, court: str) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        D.set_diplomatic_state(w, lord, court, "ARMISTICE", "armistice_ratified")
        D.set_diplomatic_state(w, vassal, court, "ARMISTICE", "armistice_ratified")


def _peace(w, lord: str, vassal: str, court: str) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        D.set_diplomatic_state(w, lord, court, "PEACE", "peace_ratified")
        D.set_diplomatic_state(w, vassal, court, "PEACE", "peace_ratified")


class TestDDB3:
    """The sea #19 / #21 shape: Holland's contingent (Dumonceau) posted in
    Ulster, a conquest from Britain."""

    @pytest.fixture
    def posted(self, w):
        marshal = _post_contingent(w, "Holland", "Ulster", "France")
        return w, marshal

    def test_a_truce_keeps_the_contingent_at_its_post(self, posted):
        w, marshal = posted
        _truce(w, "France", "Holland", "Britain")
        assert CG.truce_courts(w, "France", "Holland") == ["Britain"]
        with contextlib.redirect_stdout(io.StringIO()):
            beats = CG.process_vassal_contingents(w)
        assert CG.contingent_record(w, "Holland")["state"] == "serving"
        assert "marching_home" not in [b.get("beat") for b in beats]
        assert marshal.location == "Ulster" and marshal.strategic_order is None, \
            "no home order and no Road Home order"
        assert CG.holds_its_post(w, marshal)

    def test_the_road_home_neither_issues_nor_judges_it(self, posted):
        w, marshal = posted
        _truce(w, "France", "Holland", "Britain")
        home = WD.get_home_zone(w, "France")
        assert WD.is_stranded(w, marshal, home), "it stands where a truce strands a corps"
        assert marshal not in WD._evacuating_marshals(w, "France", home)
        with contextlib.redirect_stdout(io.StringIO()):
            ticks = WD.process_evacuation_grants(w)
        assert not [t for t in ticks or [] if t.get("marshal") == marshal.name]
        assert marshal.strategic_order is None

    def test_the_peace_walks_it_home_with_the_right_line(self, posted):
        w, marshal = posted
        _truce(w, "France", "Holland", "Britain")
        snapshot = D.build_war_context_snapshot(w, "France", "Britain", "peace")
        released = [f["display"] for f in snapshot["fallout_warnings"]
                    if f.get("warning_type") == "contingent_released"]
        assert released == ["Dumonceau's Holland contingent is released — it leaves "
                            "its post at Ulster and marches home"]
        _peace(w, "France", "Holland", "Britain")
        assert CG.contingent_record(w, "Holland")["state"] == "homeward"
        assert CG.is_contingent_home_order(marshal.strategic_order)
        messages = [e["message"] for e in w.event_log if e.get("type") == "evacuation_granted"]
        assert messages and "marching home under Holland's colours" in messages[-1]
        assert "not moved" not in messages[-1]
        assert "Normandy" not in messages[-1], "the treaty's road is not the contingent's"

    def test_the_raise_stays_war_only(self, w):
        _truce(w, "France", "Holland", "Britain")
        with contextlib.redirect_stdout(io.StringIO()):
            CG.process_vassal_contingents(w)
        assert CG.contingent_record(w, "Holland") is None

    def test_an_ai_lords_contingent_behaves_alike(self, w):
        w.vassals["Switzerland"]["lord"] = "Austria"
        w.vassals["Switzerland"]["loyalty"] = 100
        with contextlib.redirect_stdout(io.StringIO()):
            D.set_diplomatic_state(w, "Switzerland", "Bavaria", "WAR", "test_fixture")
        w.manpower_pools.setdefault("Switzerland", {})["infantry"] = 20000
        for name in w.get_nation_regions("Switzerland"):
            w.regions[name].income_value = max(int(w.regions[name].income_value or 0), 300)
        assert CG.shared_enemies(w, "Austria", "Switzerland") == ["Bavaria"]
        marshal = _post_contingent(w, "Switzerland", "Munich", "Austria")
        _truce(w, "Austria", "Switzerland", "Bavaria")
        with contextlib.redirect_stdout(io.StringIO()):
            CG.process_vassal_contingents(w)
        assert CG.contingent_record(w, "Switzerland")["state"] == "serving"
        assert CG.holds_its_post(w, marshal) and marshal.strategic_order is None
        _peace(w, "Austria", "Switzerland", "Bavaria")
        with contextlib.redirect_stdout(io.StringIO()):
            CG.process_vassal_contingents(w)
        assert CG.contingent_record(w, "Switzerland")["state"] == "homeward"
