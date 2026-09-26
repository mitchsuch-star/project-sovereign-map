"""SR-2a — "One verdict per screen" (Score Mandate Chunk 2 DIPLOMACY,
September 26, 2026; `docs/SCORE_MANDATE_PLAN.md` §2 Chunk 2; rows
`BUG_FIXES.md` AAR-2, AAR-3, AAR-7, AAR-26, AAR-27).

AAR-2  — the settlement table seats the senior COVERED court, and the
         per-court table the player reads IS the ratify gate: never "Term
         harshness" under a "Will carry" table.
AAR-3  — "Request Revision" carries the offering courts' consent for the
         unchanged package (its root: an offer laid back verbatim carries at
         its own threshold) and keeps the letter answerable until the draft
         changes or the consented draft ratifies.
AAR-7  — ONE harsh transform; identical eased packages collapse to one
         honest option; an eased package is never labelled "Harsh demands".
AAR-26 — an ally settlement petition's Grant/Honor arm is derived from the
         live table at every read, its refusal routes to the settlement,
         and the petition expires with the table it was filed against.
AAR-27 — the settlement request's war label names the courts still AT WAR.
"""
from __future__ import annotations

import contextlib
import copy
import io
from pathlib import Path
from typing import Dict

import pytest

import backend.commands.diplomatic_executor as DE
import backend.game_logic.ai_diplomacy as AD
import backend.game_logic.diplomatic_dialogue as DD
import backend.game_logic.diplomatic_templates as DT
import backend.game_logic.settlement_offers as SO
import backend.game_logic.settlement_scoring as SC
import backend.game_logic.settlement_staging as SS
import backend.game_logic.settlement_validation as SV
from backend.game_logic.diplomacy import set_diplomatic_state
from backend.game_logic.settlement_actions import handle_settlement_dialogue_action
from backend.game_logic.settlement_preview import (
    handle_incoming_settlement_offer_action,
)
from backend.game_logic.settlement_ratify import ratify_settlement_confirm
from backend.game_logic.settlement_staging import stage_settlement_confirm
from backend.game_logic.settlement_validation import (
    get_coverable_enemy_participants,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _boot(turn: int = 3) -> WorldState:
    with _quiet():
        w = WorldState.from_scenario(str(SCENARIO_PATH))
    w.current_turn = turn
    return w


def _legacy(turn: int = 5) -> WorldState:
    w = WorldState()
    w.current_turn = turn
    return w


def _stamp_player_war_score(world, player, opponent, player_score):
    key = world._make_diplo_key(player, opponent)
    parts = key.split("|")
    world.war_scores[key] = player_score if parts[0] == player else -player_score


def _install_war(world, *, attackers, defenders, created_turn=None,
                 player_war_score=-30):
    war = make_synthetic_war_instance(
        "war_1",
        attackers=list(attackers), defenders=list(defenders),
        attacker_leader=attackers[0], defender_leader=defenders[0],
        created_turn=int(created_turn if created_turn is not None
                         else world.current_turn),
    )
    world.war_instances["war_1"] = war
    for atk in attackers:
        for dfd in defenders:
            world.diplomatic_states["|".join(sorted([atk, dfd]))] = "WAR"
    _stamp_player_war_score(world, attackers[0], defenders[0], player_war_score)
    world.invalidate_war_instance_indexes()
    return war


def _reset_table(world):
    """Clear the mounted settlement surface and the scoped draft store so
    the next staging is a fresh table (a same-war restage with a DIFFERENT
    scope mounts the SC-14b scope-replace chooser instead)."""
    dm = world.dialogue_manager
    while isinstance(dm.peek(), dict) and str(dm.peek().get("type") or "").startswith("settlement_"):
        dm.pop()
    world.pending_settlement_drafts_by_key = {}


def _stage(world, covered, mode="PROPOSE", terms=None):
    kwargs = dict(
        war_id="war_1", actor_nation="France", caller_kind="player_editor",
        dialogue_mode=mode, covered_enemy_participants=list(covered),
        selected_target_nation=covered[0],
    )
    if terms is not None:
        kwargs["settlement_terms"] = terms
    with _quiet():
        r = stage_settlement_confirm(world, **kwargs)
    assert r.get("success"), r
    return world.dialogue_manager.peek()


# ═══════════════════════════════════════════════════════════════════════
# AAR-2 — the table seats the covered leader; the table IS the gate
# ═══════════════════════════════════════════════════════════════════════

SCORES = {"Britain": 32, "Austria": 51, "Russia": 60}


@pytest.fixture
def scored(monkeypatch):
    """The stable scorer seam, overridden BY COURT: Britain 32 (the leader,
    below the line), Austria 51, Russia 60 — the AAR's own numbers."""
    real = SC.calculate_common_peace_acceptance

    def fake(world, **kw):
        r = dict(real(world, **kw))
        court = str(kw.get("accepting_leader") or "")
        score = SCORES.get(court, r.get("score"))
        r["score"] = score
        r["verdict"] = "accept" if score is not None and score >= 50 else "near_acceptable"
        r["hard_stops"] = []
        r["feedback"] = ([] if (score or 0) >= 50
                         else [{"component": "term_harshness", "value": -33}])
        return r

    monkeypatch.setattr(SC, "calculate_common_peace_acceptance", fake)
    return SCORES


def _coalition_world():
    w = _legacy(5)
    _install_war(w, attackers=("France", "Saxony"),
                 defenders=("Britain", "Austria", "Russia"),
                 player_war_score=40)
    return w


def _material(payer: str):
    """A package with a material clause — a white peace (bare `peace`) is
    exempt from the per-court gate by design (G4F-19), so the AAR's case is
    a table with terms on it."""
    return [{"type": "peace"},
            {"type": "gold_indemnity", "from": payer, "to": "France", "amount": 100}]


def _submit(world, dialogue):
    with _quiet():
        r = handle_settlement_dialogue_action(
            world, action="submit_settlement_for_review", dialogue=dialogue)
    assert r.get("success"), r
    review = world.dialogue_manager.peek()
    assert review["dialogue_mode"] == "REVIEW"
    return review


class TestAcceptingLeaderForCoverage:

    def test_the_side_leader_while_it_is_covered(self):
        war = {"defender_leader": "Britain", "defenders": ["Britain", "Austria"]}
        assert SV.accepting_leader_for_coverage(war, "defenders", ["Austria", "Britain"]) == "Britain"

    def test_the_senior_covered_court_when_the_leader_is_dropped(self):
        war = {"defender_leader": "Britain",
               "defenders": ["Britain", "Austria", "Russia"]}
        assert SV.accepting_leader_for_coverage(war, "defenders", ["Russia", "Austria"]) == "Austria"

    def test_empty_coverage_keeps_the_leader(self):
        war = {"defender_leader": "Britain", "defenders": ["Britain"]}
        assert SV.accepting_leader_for_coverage(war, "defenders", []) == "Britain"

    def test_the_lever_down_is_the_side_leader_always(self, monkeypatch):
        monkeypatch.setattr(SV, "THE_TABLE_SEATS_THE_COVERED_LEADER", False)
        war = {"defender_leader": "Britain", "defenders": ["Britain", "Austria"]}
        assert SV.accepting_leader_for_coverage(war, "defenders", ["Austria"]) == "Britain"


class TestTheCoverageDropRoute:

    def test_austria_alone_ratifies_when_austria_carries(self, scored):
        w = _coalition_world()
        d = _stage(w, ["Austria"], terms=_material("Austria"))
        assert d["white_peace"] is False
        assert d["staged_leaders"]["defenders"] == "Austria"
        assert d["overall_acceptance"]["carries"] is True
        assert d["can_ratify"] is True
        assert d["ratify_blocked_reason"] == ""
        # the review's summary score is the covered leader's
        assert int(d["acceptance_display"]["total"]) == 51

    def test_the_blocker_is_the_tables_own_verdict(self, scored):
        w = _coalition_world()
        d = _stage(w, ["Austria", "Britain"], terms=_material("Austria"))
        assert d["white_peace"] is False
        assert d["overall_acceptance"]["carries"] is False
        assert d["can_ratify"] is False
        verdict = d["overall_acceptance"]["carry_verdict_display"]
        assert d["ratify_blocked_reason"] == verdict
        assert "Britain 32/50" in verdict
        assert "harshness" not in d["ratify_blocked_reason"].lower()

    def test_the_lever_down_reproduces_the_aar(self, scored, monkeypatch):
        """The measured contradiction: "Will carry" beside "cannot be
        ratified now … Term harshness"."""
        monkeypatch.setattr(SS, "THE_TABLE_TELLS_ONE_TRUTH", False)
        monkeypatch.setattr(SV, "THE_TABLE_SEATS_THE_COVERED_LEADER", False)
        w = _coalition_world()
        d = _stage(w, ["Austria"], terms=_material("Austria"))
        assert d["overall_acceptance"]["carries"] is True
        assert d["can_ratify"] is False
        assert "harshness" in d["ratify_blocked_reason"].lower()

    def test_ratification_seats_the_same_covered_leader(self, scored):
        w = _coalition_world()
        d = _submit(w, _stage(w, ["Austria"], terms=_material("Austria")))
        assert d["can_ratify"] is True
        assert d["staged_leaders"]["defenders"] == "Austria"
        with _quiet():
            r = ratify_settlement_confirm(w, d)
        assert r.get("success") is True, r
        assert any(p.get("pair") == "Austria|France" for p in r["resolved_pairs"])
        assert all(p.get("covered_enemy") == "Austria" for p in r["resolved_pairs"])

    def test_ratification_lever_down_refuses_the_same_table(self, scored, monkeypatch):
        monkeypatch.setattr(SV, "THE_TABLE_SEATS_THE_COVERED_LEADER", False)
        w = _coalition_world()
        d = _submit(w, _stage(w, ["Austria"], terms=_material("Austria")))
        with _quiet():
            r = ratify_settlement_confirm(w, d)
        assert r.get("success") is False
        assert r.get("error") == "acceptance_rejected"

    def test_the_table_outranks_the_summary_when_they_disagree(self, monkeypatch):
        """The residual the lever exists for: the leader-level SUMMARY scorer
        (no precomputed side pressure) and the per-court TABLE scorer (the
        aggregator's shared pass) can disagree on the same court. The table
        the player reads is the gate; the summary cannot veto it."""
        real = SC.calculate_common_peace_acceptance

        def split(world, **kw):
            r = dict(real(world, **kw))
            in_table = kw.get("direct_scores") is not None
            score = 51 if in_table else 32
            r["score"] = score
            r["verdict"] = "accept" if score >= 50 else "near_acceptable"
            r["hard_stops"] = []
            r["feedback"] = ([] if score >= 50
                             else [{"component": "term_harshness", "value": -33}])
            return r

        monkeypatch.setattr(SC, "calculate_common_peace_acceptance", split)
        w = _coalition_world()
        d = _stage(w, ["Austria"], terms=_material("Austria"))
        assert d["overall_acceptance"]["carries"] is True
        assert int(d["acceptance_display"]["total"]) == 32     # the summary
        assert d["can_ratify"] is True                         # the table
        assert d["ratify_blocked_reason"] == ""

    def test_white_peace_keeps_the_leader_gate(self, scored):
        """A white peace ratifies an EMPTY package by design (G4F-19) and is
        exempt from the per-court gate; the leader-level gate still binds
        it — on the covered leader."""
        w = _coalition_world()
        d = _stage(w, ["Austria", "Britain"], terms=[{"type": "peace"}])
        assert d["white_peace"] is True
        assert d["staged_leaders"]["defenders"] == "Britain"
        assert d["can_ratify"] is False
        _reset_table(w)
        d2 = _stage(w, ["Austria"], terms=[{"type": "peace"}])
        assert d2["white_peace"] is True
        assert d2["can_ratify"] is True


class TestNeverTermHarshnessUnderAWillCarryTable:

    def test_every_coverage_subset_of_the_boot_war(self):
        """Drift pin over the shipped board: on every non-empty subset of the
        boot war's coverable courts, Ratify is live exactly when the table
        carries with no hard stop, and the blocker is the table's own
        verdict otherwise."""
        w = _boot()
        war = w.war_instances["war_1"]
        coverable = list(get_coverable_enemy_participants(war, "attackers"))
        assert len(coverable) >= 2
        subsets = []
        for mask in range(1, 1 << len(coverable)):
            subsets.append([c for i, c in enumerate(coverable) if mask & (1 << i)])
        material_tables = 0
        for covered in subsets:
            # the baseline (usually a white peace on the boot board, which
            # keeps the leader gate by G4F-19's design) and a material table
            for terms in (None, _material(covered[0])):
                _reset_table(w)
                d = _stage(w, covered, terms=terms)
                assert d["staged_leaders"]["defenders"] in covered, covered
                if d["white_peace"]:
                    continue
                material_tables += 1
                carries = bool(d["overall_acceptance"]["carries"])
                hard_stops = list(d["acceptance_display"].get("hard_stops") or [])
                expected = carries and not hard_stops
                assert bool(d["can_ratify"]) is expected, (covered, d["ratify_blocked_reason"])
                if expected:
                    assert d["ratify_blocked_reason"] == ""
                elif not hard_stops:
                    assert d["ratify_blocked_reason"] == d["overall_acceptance"]["carry_verdict_display"]
                    assert "harshness" not in d["ratify_blocked_reason"].lower()
        assert material_tables == len(subsets)


# ═══════════════════════════════════════════════════════════════════════
# AAR-3 — the revision route carries consent; the letter stands
# ═══════════════════════════════════════════════════════════════════════

def _offer_world():
    """The real road: the producer emits the offer, the mailbox PROMOTES it
    (the pending-envoy poll's own step), and the player answers the letter
    the manager holds."""
    w = _legacy(5)
    _install_war(w, attackers=("France", "Saxony"),
                 defenders=("Austria", "Britain"), created_turn=1)
    with _quiet():
        [entry] = AD.process_settlement_offer_phase(w)
        SO.promote_pending_settlement_offers(w)
    offer = w.dialogue_manager.peek()
    assert offer["type"] == "incoming_settlement_offer"
    assert offer["offer_id"] == entry["offer_id"]
    return w, offer


def _promoted(world, war_id="war_1"):
    return AD._settlement_offer_already_promoted(world, war_id=war_id)


class TestTheRevisionCarriesConsent:

    def test_laid_back_verbatim_the_offer_carries_at_its_own_threshold(self):
        w, offer = _offer_world()
        with _quiet():
            r = handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
        assert r["success"] is True
        d = w.dialogue_manager.peek()
        assert d["type"] == "settlement_confirm" and d["dialogue_mode"] == "PROPOSE"
        assert sorted(d["consenting_courts"]) == sorted(offer["covered_enemy_participants"])
        assert d["consent_terms"] == offer["settlement_terms"]
        assert d["consent_offer_id"] == offer["offer_id"]
        assert d["overall_acceptance"]["carries"] is True
        assert d["overall_acceptance"]["carry_verdict_display"].startswith(
            "Will carry — these are the terms they offered")
        for row in d["per_court_acceptance"]:
            assert row.get("consents") is True, row
        assert d["can_ratify"] is True

    def test_the_letter_stands_behind_the_draft(self):
        w, offer = _offer_world()
        with _quiet():
            r = handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
        assert r.get("letter_stands") is True
        # promotion moved the entry from the pending store into the mailbox;
        # the letter now waits in the manager's queue behind the draft
        assert _promoted(w)
        assert w.dialogue_manager.peek()["type"] == "settlement_confirm"
        assert any(q.get("offer_id") == offer["offer_id"]
                   for q in w.dialogue_manager.iter_queue())

    def test_back_out_promotes_the_letter_and_it_is_answerable(self):
        w, offer = _offer_world()
        with _quiet():
            handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
            d = w.dialogue_manager.peek()
            r = handle_settlement_dialogue_action(
                w, action="suspend_settlement_editor", dialogue=d)
        assert r["success"] is True
        letter = w.dialogue_manager.peek()
        assert letter["type"] == "incoming_settlement_offer"
        assert letter["offer_id"] == offer["offer_id"]
        with _quiet():
            a = handle_incoming_settlement_offer_action(
                w, action="accept_settlement_offer", dialogue=letter)
        assert a["success"] is True
        assert w.dialogue_manager.peek()["type"] == "settlement_confirm"

    def test_a_changed_draft_lapses_consent_and_consumes_the_letter(self):
        w, offer = _offer_world()
        with _quiet():
            handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
            d = w.dialogue_manager.peek()
            r = handle_settlement_dialogue_action(
                w, action="settlement_cover_drop", dialogue=d,
                action_params={"nation": "Britain"})
        assert r["success"] is True, r
        nd = w.dialogue_manager.peek()
        assert nd["type"] == "settlement_confirm"
        assert not nd.get("consenting_courts")
        assert not nd.get("consent_offer_id")
        assert not _promoted(w)

    def test_submitted_unchanged_the_review_carries_and_ratifies(self):
        w, offer = _offer_world()
        with _quiet():
            handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
            d = w.dialogue_manager.peek()
            r = handle_settlement_dialogue_action(
                w, action="submit_settlement_for_review", dialogue=d)
        assert r["success"] is True, r
        review = w.dialogue_manager.peek()
        assert review["dialogue_mode"] == "REVIEW"
        assert sorted(review["consenting_courts"]) == sorted(offer["covered_enemy_participants"])
        assert review["can_ratify"] is True
        with _quiet():
            done = ratify_settlement_confirm(w, review)
        assert done["success"] is True, done
        assert not _promoted(w)

    def test_the_lever_down_is_the_old_consume_at_staging(self, monkeypatch):
        monkeypatch.setattr(SO, "THE_LETTER_STANDS_UNTIL_THE_DRAFT_CHANGES", False)
        w, offer = _offer_world()
        with _quiet():
            r = handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
        assert r["success"] is True
        d = w.dialogue_manager.peek()
        assert not d.get("consenting_courts")
        assert not _promoted(w)

    def test_an_unchanged_restage_keeps_consent_and_the_letter(self):
        """A focus change redraws nothing: the package is still the one the
        courts offered, so consent rides the restage and the letter stands."""
        w, offer = _offer_world()
        with _quiet():
            handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
            d = w.dialogue_manager.peek()
            other = [c for c in d["covered_enemy_participants"]
                     if c != d.get("selected_target_nation")][0]
            r = handle_settlement_dialogue_action(
                w, action="settlement_focus_court", dialogue=d,
                action_params={"nation": other})
        assert r["success"] is True, r
        nd = w.dialogue_manager.peek()
        assert nd["type"] == "settlement_confirm"
        assert nd["settlement_terms"] == offer["settlement_terms"]
        assert sorted(nd["consenting_courts"]) == sorted(offer["covered_enemy_participants"])
        assert nd["consent_offer_id"] == offer["offer_id"]
        assert nd["overall_acceptance"]["carries"] is True
        assert _promoted(w)

    def test_a_same_magnitude_redial_keeps_consent_and_the_letter(self):
        """The redraw seam itself (`_restage_settlement_after_redraw`): a
        magnitude re-set to the SAME figure restages the same package, so
        consent rides it and the letter still stands."""
        w, offer = _offer_world()
        with _quiet():
            handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
        d = w.dialogue_manager.peek()
        gold = [(i, t) for i, t in enumerate(d["settlement_terms"])
                if t.get("type") in ("gold_indemnity", "gold_per_turn")]
        assert gold, d["settlement_terms"]
        idx, clause = gold[0]
        with _quiet():
            r = handle_settlement_dialogue_action(
                w, action="settlement_demand_set_magnitude", dialogue=d,
                action_params={"clause_index": idx, "amount": int(clause["amount"]),
                               "expected_type": clause["type"]})
        assert r["success"] is True, r
        nd = w.dialogue_manager.peek()
        assert nd is not d
        # the dial stamps provenance (`authored_by`) on the clause it touched;
        # consent is to the package's SUBSTANCE, which is unchanged
        assert nd["settlement_terms"] != d["settlement_terms"]
        assert SV.consent_terms_equal(nd["settlement_terms"], d["settlement_terms"])
        assert sorted(nd["consenting_courts"]) == sorted(offer["covered_enemy_participants"])
        assert nd["consent_offer_id"] == offer["offer_id"]
        assert nd["consent_terms"] == offer["settlement_terms"]
        assert _promoted(w)

    def test_consent_kwargs_lapse_on_any_changed_term(self):
        d = {"consenting_courts": ["Austria"],
             "consent_terms": [{"type": "peace"}, {"type": "gold_indemnity", "amount": 100}],
             "consent_offer_id": "offer_9"}
        same = SS.consent_kwargs_for_restage(d, [{"type": "peace"}, {"type": "gold_indemnity", "amount": 100}])
        assert same["consenting_courts"] == ["Austria"] and same["consent_offer_id"] == "offer_9"
        assert SS.consent_kwargs_for_restage(d, [{"type": "peace"}, {"type": "gold_indemnity", "amount": 150}]) == {}
        assert SS.consent_kwargs_for_restage({}, [{"type": "peace"}]) == {}

    def test_consume_offer_by_id_reaches_the_queue_and_the_store(self):
        w, offer = _offer_world()
        with _quiet():
            handle_incoming_settlement_offer_action(
                w, action="request_settlement_revision", dialogue=offer)
        assert SO.consume_offer_by_id(w, offer_id=offer["offer_id"], war_id="war_1") is True
        assert not _promoted(w)
        assert SO.consume_offer_by_id(w, offer_id=offer["offer_id"], war_id="war_1") is False


# ═══════════════════════════════════════════════════════════════════════
# AAR-7 — one harsh transform; the menu collapses identical packages
# ═══════════════════════════════════════════════════════════════════════

class TestHardenProposalTerms:

    def test_the_executors_arithmetic_verbatim(self):
        terms = {"demands": [{"type": "gold_per_turn", "value": 100},
                             {"type": "territory_cede", "value": 1, "regions": ["Tyrol"]}],
                 "sweeteners": [{"type": "gold_lump", "value": 500}]}
        out = DT.harden_proposal_terms(copy.deepcopy(terms), proposal_type="peace",
                                       round_num=1, target_nation="Austria")
        assert out["demands"][0] == {"type": "gold_per_turn", "value": 150}
        assert out["demands"][1] == {"type": "territory_cede", "value": 1, "regions": ["Tyrol"]}
        assert out["sweeteners"] == []
        assert out["talleyrand_commentary"] == DT._get_smart_commentary("Austria", "modified_harsh")

    def test_a_gold_demand_when_there_is_none_and_the_round_two_cession(self):
        out = DT.harden_proposal_terms({"demands": [], "sweeteners": []},
                                       proposal_type="peace", round_num=1,
                                       target_nation="Austria")
        assert out["demands"] == [{"type": "gold_per_turn", "value": 300}]
        out2 = DT.harden_proposal_terms({"demands": [{"type": "gold_per_turn", "value": 100}],
                                         "sweeteners": []},
                                        proposal_type="peace", round_num=2,
                                        target_nation="Austria")
        assert {"type": "territory_cede", "value": 2} in out2["demands"]

    def test_friendship_types_strip_territory_and_ask_less_gold(self):
        out = DT.harden_proposal_terms(
            {"demands": [{"type": "territory_cede", "value": 1, "regions": ["Tyrol"]}],
             "sweeteners": []},
            proposal_type="alliance", round_num=2, target_nation="Prussia")
        assert all(d.get("type") not in ("territory_cede", "territory") for d in out["demands"])
        out2 = DT.harden_proposal_terms({"demands": [], "sweeteners": []},
                                        proposal_type="non_aggression", round_num=1,
                                        target_nation="Prussia")
        assert out2["demands"] == [{"type": "gold_per_turn", "value": 100}]

    def test_the_executor_calls_the_single_source(self):
        src = (REPO / "backend" / "commands" / "diplomatic_executor.py").read_text(encoding="utf-8")
        start = src.index('elif action == "modify_harsh":')
        body = src[start:start + 3000]
        assert "harden_proposal_terms(" in body
        assert "Escalate existing demands by 1.5x" not in body


class TestTheMenuCollapses:

    def _opt(self, label, terms, variant=None):
        o = {"label": label, "description": "", "action": "execute_proposal",
             "terms": dict(terms, proposal_type="peace")}
        if variant:
            o["variant"] = variant
        return o

    def test_identical_packages_collapse_and_say_so(self):
        generous = self._opt("Generous peace", {"demands": [], "sweeteners": []})
        harsh = self._opt("Harsh demands", {"demands": [], "sweeteners": [],
                                            "suggestion_eased_to_estimate": True}, "harsh")
        keep = {"label": "Continue fighting", "description": "", "action": "dismiss"}
        options, text = DT.collapse_identical_packages([generous, harsh, keep], "Sire.", "Austria")
        assert [o["label"] for o in options] == ["Generous peace", "Continue fighting"]
        assert text.endswith("Austria will sign nothing harsher today.")

    def test_an_eased_distinct_harsh_package_is_relabelled(self):
        generous = self._opt("Generous peace", {"demands": [], "sweeteners": []})
        harsh = self._opt("Harsh demands", {"demands": [{"type": "gold_per_turn", "value": 50}],
                                            "sweeteners": [],
                                            "suggestion_eased_to_estimate": True}, "harsh")
        options, text = DT.collapse_identical_packages([generous, harsh], "Sire.", "Austria")
        assert [o["label"] for o in options] == ["Generous peace", DT.HARSH_EASED_LABEL]
        assert text == "Sire."

    def test_a_distinct_uneased_harsh_package_keeps_its_label(self):
        generous = self._opt("Generous peace", {"demands": [], "sweeteners": []})
        harsh = self._opt("Harsh demands", {"demands": [{"type": "gold_per_turn", "value": 300}],
                                            "sweeteners": []}, "harsh")
        options, _ = DT.collapse_identical_packages([generous, harsh], "Sire.", "Austria")
        assert [o["label"] for o in options] == ["Generous peace", "Harsh demands"]

    def test_the_t1_template_marks_its_harsh_option(self):
        t = DT.get_template("proposal_options", "WAR", "winning_comfortably")
        harsh = [o for o in t["options"] if o["label"] == "Harsh demands"]
        assert harsh and harsh[0]["variant"] == "harsh"

    def test_the_menu_never_sends_the_generous_package_under_a_harsh_label(self):
        """The AAR's turn-5 menu on the shipped board: France winning
        comfortably against Austria."""
        w = _boot(5)
        _stamp_player_war_score(w, "France", "Austria", 60)
        parsed = {"action": "diplomatic_proposal", "diplomat": "Talleyrand",
                  "target_nation": "Austria", "proposal_type": None,
                  "clauses": [], "is_question": False,
                  "has_diplomatic_keywords": True, "tone": "propose",
                  "raw_text": "propose to Austria"}
        with _quiet():
            d = DD.generate_dialogue("proposal_options", parsed, w)
        execs = [o for o in d["options"] if o.get("action") == "execute_proposal"]
        assert execs, d["options"]
        labels = [o["label"] for o in execs]
        harsh = [o for o in execs if o.get("variant") == "harsh"]
        generous = [o for o in execs if not o.get("variant")]
        if harsh:
            assert generous
            assert not DT.same_package(harsh[0]["terms"], generous[0]["terms"])
            if harsh[0]["terms"].get("suggestion_eased_to_estimate"):
                assert harsh[0]["label"] == DT.HARSH_EASED_LABEL
            else:
                assert harsh[0]["label"] == "Harsh demands"
        else:
            assert "Harsh demands" not in labels
            assert d["talleyrand_text"].endswith("will sign nothing harsher today.")

    def test_the_easing_family_matches_the_stage_3_5_tuple(self):
        src = (REPO / "backend" / "game_logic" / "diplomatic_templates.py").read_text(encoding="utf-8")
        assert '"peace", "armistice", "armistice_winning", "armistice_losing",' in src
        assert set(DT.PEACE_FAMILY_FOR_EASING) == {
            "peace", "armistice", "armistice_winning", "armistice_losing"}


# ═══════════════════════════════════════════════════════════════════════
# AAR-26 — the petition's arm is honest, routed, and expires with its table
# ═══════════════════════════════════════════════════════════════════════

def _restoration_world():
    """Slice H's fixture: France + Prussia vs Austria; Austria holds Berlin."""
    w = _legacy(5)
    _install_war(w, attackers=("France", "Prussia"), defenders=("Austria",),
                 player_war_score=70)
    for pair in w.war_instances["war_1"]["active_diplo_keys"]:
        w.war_scores[pair] = 70
    set_diplomatic_state(w, "France", "Prussia", "ALLIANCE", "test")
    w.regions["Berlin"].controller = "Austria"
    return w


def _queue_petition(world):
    with _quiet():
        queued = SO.queue_ally_settlement_petitions_for_player_action(
            world, trigger_action="stage_settlement", war_id="war_1",
            covered_enemy_participants=["Austria"], settlement_terms=[])
    assert len(queued) == 1, queued
    return queued[0]


def _petitions(world):
    dm = world.dialogue_manager
    return [d for d in ([dm.peek()] + list(dm.iter_queue()))
            if isinstance(d, dict) and d.get("type") == "ally_settlement_petition"]


def _grant_option(dialogue):
    return next(o for o in dialogue["options"]
                if o["action"] == SO.ALLY_SETTLEMENT_PETITION_GRANT_ACTION)


class TestThePetitionsArmIsHonest:

    def test_no_table_no_grant_with_the_door_named(self):
        w = _restoration_world()
        p = _queue_petition(w)
        popup = SO.refresh_ally_petition_availability(w, p)
        opt = _grant_option(p)
        assert opt["available"] is False
        assert "Open the settlement" in opt["disabled_reason_display"]
        popup_opt = next(o for o in popup["options"]
                         if o["action"] == SO.ALLY_SETTLEMENT_PETITION_GRANT_ACTION)
        assert popup_opt["available"] is False

    def test_the_built_petition_is_never_baked_available(self):
        w = _restoration_world()
        p = _queue_petition(w)
        assert _grant_option(p)["available"] is False
        assert _grant_option(p["popup_payload"])["available"] is False

    def test_an_open_table_flips_the_arm(self):
        w = _restoration_world()
        p = _queue_petition(w)
        _stage(w, ["Austria"])
        SO.refresh_ally_petition_availability(w, p)
        assert _grant_option(p)["available"] is True
        assert "disabled_reason_display" not in _grant_option(p)

    def test_the_refusal_routes_to_the_settlement(self):
        w = _restoration_world()
        p = _queue_petition(w)
        with _quiet():
            r = SO.handle_ally_settlement_petition_action(
                w, action=SO.ALLY_SETTLEMENT_PETITION_GRANT_ACTION, dialogue=p)
        assert r["success"] is False
        assert r["error"] == "petition_table_not_mounted"
        assert r["petition_retained"] is True
        assert r["must_reopen"] is True
        assert r["reopen_target"]["war_id"] == "war_1"
        assert r["reopen_target"]["target_nation"] == "Austria"
        assert len(_petitions(w)) == 1

    def test_a_dead_war_is_said_plainly(self):
        w = _restoration_world()
        p = _queue_petition(w)
        w.war_instances["war_1"]["ended_turn"] = 5
        SO.refresh_ally_petition_availability(w, p)
        assert _grant_option(p)["available"] is False
        assert "has ended" in _grant_option(p)["disabled_reason_display"]


class TestThePetitionExpiresWithItsTable:

    def test_unmounted_it_lapses_at_turns_end_with_a_notice(self):
        w = _restoration_world()
        _queue_petition(w)
        assert len(_petitions(w)) == 1
        with _quiet():
            w.advance_turn()
        assert _petitions(w) == []
        notices = [n for n in w.pending_settlement_draft_notices
                   if n.get("petition_lapsed")]
        assert len(notices) == 1
        assert "Prussia" in notices[0]["message_display"]
        assert "set aside at turn's end" in notices[0]["message_display"]

    def test_a_mounted_table_keeps_it(self):
        w = _restoration_world()
        _queue_petition(w)
        _stage(w, ["Austria"])
        assert w.dialogue_manager.peek()["type"] == "settlement_confirm"
        with _quiet():
            w.advance_turn()
        assert len(_petitions(w)) == 1

    def test_a_war_that_ended_takes_its_petition_with_it(self):
        w = _restoration_world()
        _queue_petition(w)
        _stage(w, ["Austria"])
        w.war_instances["war_1"]["ended_turn"] = 5
        with _quiet():
            w.advance_turn()
        assert _petitions(w) == []
        notices = [n for n in w.pending_settlement_draft_notices if n.get("petition_lapsed")]
        assert notices and "the war it was filed against" in notices[0]["message_display"]

    def test_the_lever_down_keeps_the_old_persistence(self, monkeypatch):
        monkeypatch.setattr(SO, "A_PETITION_LAPSES_WITH_ITS_TABLE", False)
        w = _restoration_world()
        _queue_petition(w)
        with _quiet():
            w.advance_turn()
        assert len(_petitions(w)) == 1

    def test_the_rail_row_goes_with_the_petition(self):
        w = _restoration_world()
        p = _queue_petition(w)
        from backend.notifications import ALLY_SETTLEMENT_PETITION
        rows = [n for n in w.notifications.get_pending()
                if n.get("type") == ALLY_SETTLEMENT_PETITION]
        assert rows
        with _quiet():
            w.advance_turn()
        rows_after = [n for n in w.notifications.get_pending()
                      if n.get("type") == ALLY_SETTLEMENT_PETITION
                      and (n.get("details") or {}).get("petition_id") == p["petition_id"]]
        assert rows_after == []


class TestTheWireServesTheDerivedArm:

    def test_pending_envoy_re_derives_the_grant_arm(self, monkeypatch):
        """The seam the AAR measured: the payload the client renders. The
        poll serves the arm derived NOW — dimmed with the door named while no
        table is open; live once a suspended draft exists."""
        import backend.main as M
        from fastapi.testclient import TestClient
        w = _restoration_world()
        _queue_petition(w)
        monkeypatch.setattr(M, "world", w)
        monkeypatch.setitem(M.game_state, "world", w)
        client = TestClient(M.app)
        with _quiet():
            r = client.get("/pending_envoy").json()
        assert r["has_pending"] is True
        assert r["dialogue_type"] == "ally_settlement_petition"
        grant = next(o for o in r["diplomatic_dialogue"]["options"]
                     if o["action"] == SO.ALLY_SETTLEMENT_PETITION_GRANT_ACTION)
        assert grant["available"] is False
        assert "Open the settlement" in grant["disabled_reason_display"]
        # open a table on the war, then back out — a suspended draft is a
        # table the handler will use, so the arm is live on the next poll
        d = _stage(w, ["Austria"])
        with _quiet():
            s = handle_settlement_dialogue_action(
                w, action="suspend_settlement_editor", dialogue=d)
            assert s["success"] is True
            r2 = client.get("/pending_envoy").json()
        assert r2["dialogue_type"] == "ally_settlement_petition"
        grant2 = next(o for o in r2["diplomatic_dialogue"]["options"]
                      if o["action"] == SO.ALLY_SETTLEMENT_PETITION_GRANT_ACTION)
        assert grant2["available"] is True


# ═══════════════════════════════════════════════════════════════════════
# AAR-27 — the label names the courts still at war
# ═══════════════════════════════════════════════════════════════════════

class TestTheWarLabelReadsActivePairs:

    def _war(self):
        war = make_synthetic_war_instance(
            "war_1", attackers=["France", "Saxony"],
            defenders=["Britain", "Austria", "Russia"],
            attacker_leader="France", defender_leader="Britain", created_turn=1)
        meta = war["diplo_key_meta"]
        meta["Austria|France"]["pair_status"] = "resolved"
        meta["France|Russia"]["pair_status"] = "armistice"
        meta["Austria|Saxony"]["pair_status"] = "resolved"
        meta["Russia|Saxony"]["pair_status"] = "resolved"
        return war

    def test_courts_at_peace_or_in_truce_have_left_the_label(self):
        label = AD._settlement_request_war_label(self._war(), "war_1", player="France")
        assert label == "France + Saxony vs Britain"

    def test_an_ally_with_no_live_pair_against_the_enemies_named_is_not_listed(self):
        war = self._war()
        war["diplo_key_meta"]["Britain|Saxony"]["pair_status"] = "resolved"
        label = AD._settlement_request_war_label(war, "war_1", player="France")
        assert label == "France vs Britain"

    def test_a_bare_roster_dict_keeps_the_full_join(self):
        label = AD._settlement_request_war_label(
            {"attackers": ["France", "KingdomOfItaly"],
             "defenders": ["Britain", "PapalStates"]}, "war_1")
        assert label == "France + Kingdom of Italy vs Britain + Papal States"

    def test_both_producers_pass_the_player(self):
        for path, needle in (
            ("backend/game_logic/ai_diplomacy.py",
             "_settlement_request_war_label(war, war_id, player=player)"),
            ("backend/commands/diplomatic_executor.py",
             "war, requested_war_id, player=player)"),
        ):
            assert needle in (REPO / path).read_text(encoding="utf-8"), path
