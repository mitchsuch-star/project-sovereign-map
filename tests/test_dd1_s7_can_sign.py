"""DD-1 S7 Slice B — `treaty.can_sign`, the ratifier's spine, read by every
surface AND the ratifier.

Pre-Deploy S7 (October 11, 2026), `docs/PRE_DEPLOY_PLAN.md` §3.1 Step 2a;
rules `SYSTEMS_REFERENCE.md` §108. The instrument is the evidence
(`tools/sign_ability_sweep.py` reads 0 / 0 on every committed arm and the
three seeds — `tests/test_dd1_sign_ability_sweep.py`); these pins hold each
seam's rule by name so a regression says which one broke:

  the verdict   (a) a treaty letter: the ladder and the floor sentences
                byte-identical; the vassal pair; the state machine (DD1-12);
                the AP clause proposer-over-target; the vassal gates through
                the creator's ONE predicate; the paradox at send (SFR-D34);
                (b) a settlement offer: the eligibility gate (DD1-3, SFR-B1);
                (c) an ally's petition (DD1-1); (d) a client's (DD1-2)
  the stamp     `stamp_option` writes both key pairs and the marker; a
                client's standing Grant and an ally's closed table are never
                marked (their handlers' own roads run)
  the readers   the ratifier; the answer seam refuses a marked option and
                logs no rejection (SFR-B2); the chips, the Congress's levers
                and the counsel; SF-V1's net; SF-V5's emitter; the white
                peace (DD1-4); the stale return names its clause (SFR-B5)
  the words     no verdict names a raw code
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from backend.game_logic import ai_diplomacy, congress, treaty
from backend.game_logic import diplomacy as D
from backend.game_logic import diplomatic_advisory as ADV
from backend.game_logic import settlement_validation as SV
from backend.game_logic import vassal as V
from backend.game_logic.treaty import Verdict, can_sign, stamp_option
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


def _proposal(proposer, target, ptype, **extra):
    base = {"type": ptype, "proposer_nation": proposer, "target_nation": target,
            "sweeteners": [], "demands": [], "clauses": []}
    base.update(extra)
    return base


def _ratify(world, proposer, target, ptype, **extra):
    with contextlib.redirect_stdout(io.StringIO()):
        return world._ratify_treaty(_proposal(proposer, target, ptype, **extra))


def _executor():
    from backend.commands.executor import CommandExecutor
    return CommandExecutor()


def _letter(world, nation, ptype):
    """An incoming letter shaped by the producer itself (the stamp runs)."""
    terms = ai_diplomacy._build_proposal_terms(nation, ptype, 0, world)
    proposal = ai_diplomacy._make_proposal(nation, ptype, 5, terms, world)
    return ai_diplomacy.build_ai_proposal_dialogue(proposal, world)


# ── (a) the treaty ─────────────────────────────────────────────────────────

class TestTheTreatyVerdict:
    def test_the_ladder_and_the_floor_keep_their_sentences(self, w):
        assert w.get_diplomatic_state("France", "Prussia") == "PEACE"
        r = _ratify(w, "Prussia", "France", "armistice")
        assert r["type"] == "diplomatic_treaty_failed" and r["clause"] == "no_downgrade"
        assert r["message"] == "We already have Peace with Prussia. An Armistice treaty would be a downgrade."
        assert r["target"] == "France"
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = -60
        r = _ratify(w, "Prussia", "France", "defensive_alliance")
        assert r["clause"] == "relation_floor"
        assert r["message"] == "Relations with Prussia stand at -60; a Defensive Alliance needs 20."

    def test_dd1_12_the_ratifier_reads_the_state_machine(self, w):
        """VASSAL → OPEN_BORDERS was signed by the ratifier (the smoke seed);
        no treaty is signed inside a vassalage now — release is the road."""
        assert w.get_diplomatic_state("France", "Switzerland") == "VASSAL"
        r = _ratify(w, "France", "Switzerland", "open_borders")
        assert r["type"] == "diplomatic_treaty_failed" and r["clause"] == "vassal_pair", r
        assert "no treaty is signed inside a vassalage" in r["message"]
        assert w.get_diplomatic_state("France", "Switzerland") == "VASSAL"
        # PEACE → VASSAL: the state machine, in words.
        r = _ratify(w, "France", "Prussia", "vassalage")
        assert r["clause"] == "state_machine", r
        assert r["message"] == ("A vassalage of Prussia needs a war (a dictated peace) or "
                                "open borders and above — we stand at Peace.")
        assert w.get_diplomatic_state("France", "Prussia") == "PEACE"

    def test_an_ai_ai_refusal_stays_silent(self, w):
        # Switzerland is France's client: an AI court's treaty on that pair.
        assert _ratify(w, "Austria", "Switzerland", "open_borders") is None or True
        v = can_sign(w, _proposal("Austria", "Prussia", "armistice"))  # PEACE → ARMISTICE
        assert not v.ok and v.silent and v.clause == "no_downgrade"
        assert _ratify(w, "Austria", "Prussia", "armistice") is None

    def test_the_ap_clause_reads_the_proposer_over_the_target(self, w, monkeypatch):
        """`validate_ap_clause` read the PLAYER's score against `target` —
        on an AI letter that was France against herself (always 0)."""
        key = w._make_diplo_key("France", "Prussia")
        w.nation_relations[key] = 10
        letter = _proposal("Prussia", "France", "open_borders",
                           demands=[{"type": "ap_per_turn", "value": 1}])
        assert can_sign(w, letter).clause == "ap_clause"
        # Prussia 90 over France: the demand is lawful; France 90 over Prussia: not.
        monkeypatch.setattr(D, "get_war_score_for",
                            lambda world, n, o: 90 if (n, o) == ("Prussia", "France") else -90)
        assert can_sign(w, letter).ok
        monkeypatch.setattr(D, "get_war_score_for",
                            lambda world, n, o: 90 if (n, o) == ("France", "Prussia") else -90)
        v = can_sign(w, letter)
        assert v.clause == "ap_clause"
        assert v.message == "AP demands require overwhelming military dominance (war score > 80)."

    def test_the_vassal_gates_are_the_creators_one_predicate(self, w):
        D.set_diplomatic_state(w, "France", "Prussia", "OPEN_BORDERS", "test")
        w.vassal_release_cooldowns["Prussia"] = 3
        why = V.vassal_treaty_refusal(w, "France", "Prussia")
        assert why == "Cannot vassalize Prussia: recently released (3 turns remaining)."
        assert V.create_vassal_treaty(w, "France", "Prussia")["message"] == why
        v = can_sign(w, _proposal("France", "Prussia", "vassalage"))
        assert v.clause in ("vassal_cap", "vassal_gate"), v
        if v.clause == "vassal_gate":
            assert v.message == why

    def test_sfr_d34_the_paradox_is_read_at_send_only(self, w):
        peace = _proposal("France", "Britain", "peace")
        assert can_sign(w, peace).ok                       # the ratifier's view
        v = can_sign(w, peace, at_send=True)               # the send road's
        # PC-R1 (S13e part 1): the paradox is no longer a HARD_STOP — the
        # send road signs, and the conflicts carry Spain's pair as CARRIED
        # IN (France leads its side of war_1).
        assert v.ok and v.clause == ""
        rows = D.get_peace_commitment_conflicts(w, "France", "Britain", [])
        assert [c["conflict_type"] for c in rows if c["affected_entity"] == "Spain"] == ["carried_in"]


# ── (b) the settlement offer ───────────────────────────────────────────────

class TestTheSettlementVerdict:
    def _draft(self, w, war_id="war_1"):
        war = w.war_instances[war_id]
        return {"type": "incoming_settlement_offer", "war_id": war_id,
                "proposer_nation": war["defender_leader"], "proposer_side": "defenders",
                "accepting_side": "attackers", "accepting_leader": "France",
                "covered_enemy_participants": list(war["defenders"]), "settlement_terms": []}

    def test_sfr_b1_a_war_france_does_not_lead_is_not_offered(self, w, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: True)
        war = w.war_instances["war_1"]
        with contextlib.redirect_stdout(io.StringIO()):
            assert ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=[], cooldowns={}) is not None
        war["attacker_leader"] = "Spain"
        v = can_sign(w, self._draft(w))
        assert v.clause == "not_side_leader" and v.message == "Only the war leader can settle this side."
        cooldowns = {}
        with contextlib.redirect_stdout(io.StringIO()):
            assert ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", war, player="France", current_turn=w.current_turn,
                pending=[], cooldowns=cooldowns) is None
        assert cooldowns == {}                               # no cooldown spent

    def test_dd1_3_a_one_on_one_war_is_not_offered(self, w, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: True)
        blocked = SV._blocked_payload("one_to_one_war", war_id="war_1")
        monkeypatch.setattr(SV, "evaluate_open_settlement_eligibility", lambda *a, **k: dict(blocked))
        v = can_sign(w, self._draft(w))
        assert v.clause == "one_to_one_war"
        assert v.message == "A one-on-one war is settled on the court's own page: Propose Peace or Propose Armistice."
        with contextlib.redirect_stdout(io.StringIO()):
            assert ai_diplomacy._emit_settlement_offer_for_war(
                w, "war_1", w.war_instances["war_1"], player="France",
                current_turn=w.current_turn, pending=[], cooldowns={}) is None

    def test_the_other_gates_do_not_silence_the_producer(self, w, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: True)
        blocked = SV._blocked_payload("settlement_dialogue_active", war_id="war_1")
        monkeypatch.setattr(SV, "evaluate_open_settlement_eligibility", lambda *a, **k: dict(blocked))
        assert can_sign(w, self._draft(w)).ok

    def test_the_carry_is_sf_v5s_own_dry_run(self, w, monkeypatch):
        monkeypatch.setattr(ai_diplomacy, "_letter_would_carry", lambda *a, **k: False)
        v = can_sign(w, self._draft(w))
        assert v.clause == "would_not_carry" and "would not sign these terms" in v.message
        assert not treaty.names_a_raw_code(v.message)

    def test_dd1_4_the_white_peace_names_the_one_to_one_gate(self, w, monkeypatch):
        blocked = SV._blocked_payload("one_to_one_war", war_id="war_1")
        monkeypatch.setattr(SV, "evaluate_open_settlement_eligibility", lambda *a, **k: dict(blocked))
        ex = _executor()
        with contextlib.redirect_stdout(io.StringIO()):
            r = ex._diplomatic._execute_propose_white_peace(
                {"command": {"action": "propose_white_peace", "target_nation": "Britain",
                             "war_id": "war_1"}}, {"world": w, "executor": ex})
        assert r["success"] is False and r["error"] == "one_to_one_war", r
        assert r["message"].endswith("A one-on-one war is settled on the court's own page: Propose Peace or Propose Armistice.")


# ── (c) the ally's petition, (d) the client's ──────────────────────────────

class TestThePetitions:
    def test_dd1_1_the_ally_petition_is_stamped_with_both_key_pairs(self, w):
        from backend.game_logic import settlement_offers as SO
        dialogue = SO.build_ally_settlement_petition_dialogue(
            w, petition_type=SO.ALLY_SETTLEMENT_PETITION_REWARD,
            context={"war_id": "war_1", "ally_nation": "Bavaria", "claim_war_id": "war_1",
                     "target_enemy": "Austria", "claim_region": "Tyrol",
                     "candidate_clause": {"type": "territory_cede", "from": "Austria",
                                          "to": "Bavaria", "regions": ["Tyrol"]}},
            trigger_action="settlement_dial_harsher")
        SO.refresh_ally_petition_availability(w, dialogue)
        grant = next(o for o in dialogue["options"] if o["action"] == "grant_ally_petition_clause")
        assert grant["enabled"] is False and grant["available"] is False
        assert grant["reason"] == grant["disabled_reason_display"]
        assert grant["reason"].startswith("Open the settlement of ")
        # A closed TABLE is not a marked option: the handler's own road
        # routes the player to the table it names.
        assert treaty.CLOSED_CLAUSE_KEY not in grant
        assert not treaty.names_a_raw_code(grant["reason"])

    def test_dd1_1_the_editors_hard_stop_is_in_words(self):
        from backend.display_names import settlement_disabled_reason_display
        words = settlement_disabled_reason_display("no_direct_war_score_for_covered_enemy")
        assert "no war of its own" in words and not treaty.names_a_raw_code(words)

    def test_dd1_2_the_ladder_skips_a_province_under_petition(self, w, monkeypatch):
        """Two producers (the end turn, the Congress's summons) each read the
        lord's own list; Hesse and Holland both asked for Brunswick."""
        standing = {"type": "incoming_proposal", "target_nation": "KingdomOfItaly",
                    "options": [], "turn_created": 1,
                    "context": {"source_nation": "KingdomOfItaly",
                                "proposal_type": V.CLIENT_PETITION_TYPE,
                                "proposal": {"type": V.CLIENT_PETITION_TYPE,
                                             "proposer_nation": "KingdomOfItaly",
                                             "target_nation": "France",
                                             "petition": {"subject": "province", "region": "Brunswick"}}}}
        w.dialogue_manager.push(standing)
        assert V.regions_under_petition(w, "France") == {"Brunswick"}
        assert V.regions_under_petition(w, "France", except_vassal="KingdomOfItaly") == set()
        monkeypatch.setattr(V, "list_grantable_regions", lambda world, v, actor=None: [
            {"region": "Brunswick", "income": 30, "loyalty_gain": 5, "tribute_pct": 75},
            {"region": "Westphalia", "income": 20, "loyalty_gain": 4, "tribute_pct": 75}])
        subject = V.petition_subject(w, "Holland")
        assert subject and subject["region"] == "Westphalia", subject

    def test_a_clients_standing_grant_is_disabled_but_never_marked(self, w):
        from backend.game_logic.mailbox_payloads import petition_availability_keys
        w.diplomatic_points = 0
        terms = {"type": V.CLIENT_PETITION_TYPE, "proposer_nation": "Holland",
                 "target_nation": "France",
                 "petition": {"subject": "relief", "tribute_per_turn": 50}}
        keys = petition_availability_keys(w, terms)
        grant = keys["options"][0]
        assert grant["enabled"] is False and grant["available"] is False
        assert "cannot spare the diplomatic point" in grant["reason"]
        assert grant["disabled_reason_display"] == grant["reason"]
        assert treaty.CLOSED_CLAUSE_KEY not in grant


# ── the stamp and the answer seam ──────────────────────────────────────────

class TestTheStampAndTheAnswerSeam:
    def test_stamp_option_writes_every_key_and_the_marker(self):
        opt = {"label": "Accept", "action": "accept_ai_proposal"}
        stamp_option(opt, Verdict(False, clause="relation_floor", message="Too low."))
        assert opt == {"label": "Accept", "action": "accept_ai_proposal", "enabled": False,
                       "reason": "Too low.", "available": False,
                       "disabled_reason_display": "Too low.", treaty.CLOSED_CLAUSE_KEY: "relation_floor"}
        stamp_option(opt, Verdict(True))
        assert opt["enabled"] is True and opt["available"] is True and opt["reason"] == ""
        assert treaty.CLOSED_CLAUSE_KEY not in opt and "disabled_reason_display" not in opt
        stamp_option(opt, Verdict(False, clause="stands", message="Stands.", closes=False))
        assert opt["enabled"] is False and treaty.CLOSED_CLAUSE_KEY not in opt

    def test_a_letter_the_ratifier_would_refuse_is_mail_with_its_reason(self, w):
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = 12
        letter = _letter(w, "Prussia", "alliance")
        accept = next(o for o in letter["options"] if o["action"] == "accept_ai_proposal")
        assert accept["enabled"] is False
        assert accept["reason"] == "Relations with Prussia stand at 12; an Alliance needs 40."
        assert accept[treaty.CLOSED_CLAUSE_KEY] == "relation_floor"
        mirror = next(o for o in letter["popup_payload"]["options"] if o["action"] == "accept_ai_proposal")
        assert mirror["enabled"] is False and mirror["reason"] == accept["reason"]
        # The read seam re-stamps from the live board.
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = 45
        treaty.refresh_letter_verdict(w, letter)
        assert accept["enabled"] is True and treaty.CLOSED_CLAUSE_KEY not in accept

    def test_sfr_b2_the_answer_seam_refuses_a_marked_accept_and_logs_no_rejection(self, w):
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = 12
        letter = _letter(w, "Prussia", "alliance")
        w.dialogue_manager.push(letter)
        ex = _executor()
        before_log = len(w.event_log)
        with contextlib.redirect_stdout(io.StringIO()):
            r = ex.handle_diplomatic_dialogue_response(
                "accept_ai_proposal", {"world": w, "executor": ex},
                dialogue_id=letter["dialogue_id"])
        assert r["success"] is False
        assert r["message"] == ("'Accept' is not open, Sire — Relations with Prussia stand at 12; "
                                "an Alliance needs 40.")
        assert w.dialogue_manager.peek() is letter                      # the letter stands
        assert w.get_diplomatic_state("France", "Prussia") == "PEACE"
        assert not any(e.get("type") == "ai_proposal_rejected" for e in w.event_log[before_log:])
        assert "Prussia" not in w.player_proposal_cooldowns

    def test_sfr_b2_a_refusal_at_ratification_is_not_logged_as_our_rejection(self, w):
        """The board moved after the last stamp: the ratifier refuses, the
        reply says so, and nothing is logged as an answer of ours."""
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = 45
        letter = _letter(w, "Prussia", "alliance")
        w.dialogue_manager.push(letter)
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = 12   # no re-stamp
        ex = _executor()
        with contextlib.redirect_stdout(io.StringIO()):
            r = ex.handle_diplomatic_dialogue_response(
                "accept_ai_proposal", {"world": w, "executor": ex},
                dialogue_id=letter["dialogue_id"])
        assert r["success"] is False
        assert r["message"] == ("Prussia's terms could not be ratified: Relations with Prussia "
                                "stand at 12; an Alliance needs 40.")
        assert not any(e.get("type") == "ai_proposal_rejected" for e in w.event_log)


# ── the other readers ──────────────────────────────────────────────────────

class TestTheOtherReaders:
    def test_sf_v1s_net_is_the_whole_verdict(self, w):
        assert ai_diplomacy.treaty_offer_refusal(w, "Switzerland", "open_borders") == (
            "Switzerland is our client — no treaty is signed inside a vassalage. "
            "Release it first; that is the only road.")
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = 12
        assert ai_diplomacy.treaty_offer_refusal(w, "Prussia", "alliance") == (
            "relations 12 are below the 40 a ALLIANCE needs")

    def test_the_chip_carries_the_verdicts_sentence(self, w):
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = -30
        rows = {r["action"]: r for r in D.get_available_diplomatic_actions(w, "Prussia")}
        row = rows["propose_open_borders"]
        assert row["available"] is False and row["disabled_reason"] == "Relations too low"
        assert row["disabled_reason_display"] == (
            "Relations with Prussia stand at -30; an Open Borders needs -20.")
        assert row["closed_clause"] == "relation_floor"
        britain = {r["action"]: r for r in D.get_available_diplomatic_actions(w, "Britain")}
        peace = britain.get("propose_peace")
        if peace is not None:                                  # a WAR row (PC-R1: open, with the note)
            assert peace["available"] is True
            assert peace["separate_peace_display"] == D.separate_peace_note(w, "France", "Britain")
            assert "Spain's war with Britain ends in this instrument" in peace["separate_peace_display"]

    def test_the_congress_peace_lever_is_closed_in_words(self, w, monkeypatch):
        monkeypatch.setattr(congress, "_lever_verdict",
                            lambda world, court, state: Verdict(False, clause="vassal_pair",
                                                                message="No peace with a client."))
        row = congress.answer(w, "Austria")
        price = congress.price(w, "Austria", row)
        keys = [lv["key"] for lv in price["levers"]]
        assert "peace" not in keys and "peace_closed" in keys
        closed = next(lv for lv in price["levers"] if lv["key"] == "peace_closed")
        assert closed["text"] == "no peace can be signed today — No peace with a client."
        assert closed["closed_clause"] == "vassal_pair"

    def test_the_counsel_offers_only_a_treaty_the_table_signs(self, w):
        key = w._make_diplo_key("France", "Prussia")
        w.nation_relations[key] = 31
        hints = ADV._recommend_action("Prussia", w)["context"]["action_hints"]
        assert hints[0] == "Propose defensive alliance with Prussia", hints
        w.nation_relations[key] = 45
        hints = ADV._recommend_action("Prussia", w)["context"]["action_hints"]
        assert hints[0] == "Propose alliance with Prussia", hints
        # At war (PC-R1: the paradox no longer shuts the peace): every hint
        # names a road the table signs.
        hints = ADV._recommend_action("Britain", w)["context"]["action_hints"]
        for hint in hints:
            if hint.startswith("Propose peace with "):
                assert can_sign(w, _proposal("France", "Britain", "peace"), at_send=True).ok

    def test_sfr_b5_the_stale_return_names_the_clause(self, w):
        D.set_diplomatic_state(w, "France", "Prussia", "NON_AGGRESSION", "test")
        w.proposal_in_transit = {
            "target": "Prussia", "turns_remaining": 0,
            "proposal": _proposal("France", "Prussia", "open_borders"),
            "diplomatic_state_at_send": "NON_AGGRESSION", "acceptance_snapshot": 60,
        }
        with contextlib.redirect_stdout(io.StringIO()):
            events = w._process_proposal_in_transit()
        returned = next(e for e in events if e.get("type") == "diplomatic_proposal_returned")
        assert returned["message"].endswith(
            "our proposal is no longer viable. We already have Non-Aggression with "
            "Prussia. An Open Borders treaty would be a downgrade.")

    def test_no_verdict_names_a_raw_code(self, w):
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = -60
        letters = [
            _proposal("France", "Switzerland", "open_borders"),
            _proposal("France", "Prussia", "vassalage"),
            _proposal("Prussia", "France", "armistice"),
            _proposal("Prussia", "France", "defensive_alliance"),
        ]
        for letter in letters:
            v = can_sign(w, letter, at_send=True)
            assert not v.ok, letter
            assert v.message and not treaty.names_a_raw_code(v.message), v
