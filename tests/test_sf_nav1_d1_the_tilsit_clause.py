"""Score Finish Step 7 slice 4 (October 4, 2026) — the Tilsit clause.

§6 row 17 RULED (SCORE_FINISH_SPEC §6.6, FOR USER CONFIRMATION): a separate
peace may carry "joins the Continental System" — no forced alliance — on a
court the Emperor has beaten (Prussia and Russia at Tilsit, 1807; Austria at
Schönbrunn, 1809). ONE membership write (`diplomacy.join_continental_system`)
serves the clause on both roads and both forced-alliance arms; ONE predicate
(`diplomacy.continental_system_join_refusal`) says who may be asked; ONE exit
runs at `set_diplomatic_state`'s WAR transition.

Fixed in the same slice:
  SF7-X5 — the plain "Force X into alliance" link wrote no flag, which every
           ratification reader takes as the canonical True: the court joined
           the System and the alarm was charged for it while the staged line
           read "Forced alliance".
  SF7-X6 — the forced-alliance toggle row read "Adds France to the
           Continental System" for an alliance forced on Austria.

    diplomacy.A_MEMBER_AT_WAR_LEAVES_THE_SYSTEM
    settlement_actions.THE_PLAIN_ALLIANCE_KEEPS_NO_SYSTEM
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

import pytest

import backend.game_logic.diplomacy as D
import backend.game_logic.settlement_actions as SA
from backend.game_logic import naval
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")
CS = "continental_system_join"


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _war_with(world, court):
    for wid, inst in (world.war_instances or {}).items():
        if not isinstance(inst, dict):
            continue
        sides = (set(inst.get("attackers") or []), set(inst.get("defenders") or []))
        if (("France" in sides[0] and court in sides[1])
                or ("France" in sides[1] and court in sides[0])):
            return wid, inst
    raise AssertionError(f"no war between France and {court}")


def _cs_term(court="Austria", imposer="France"):
    return {"type": CS, "from": court, "to": imposer}


def _cs_demand():
    return {"type": CS, "value": 1}


def _events(world, etype):
    return [e for e in (world.event_log or []) if e.get("type") == etype]


# ═══════════════════════ THE BOOT ══════════════════════════════════════════

class TestTheBoot:
    def test_the_system_boots_empty_and_reads_ten_of_twenty_six(self, world):
        assert list(world.continental_system_members) == []
        assert naval.trade_dominance_nation(world) == "Britain"
        assert naval.closed_ports_against(world, "Britain") == 10
        assert naval.continental_ports_total(world) == 26

    def test_the_levers_default_on(self):
        assert D.A_MEMBER_AT_WAR_LEAVES_THE_SYSTEM is True
        assert SA.THE_PLAIN_ALLIANCE_KEEPS_NO_SYSTEM is True


# ═══════════════════════ THE PREDICATE ═════════════════════════════════════

class TestWhoMayBeAsked:
    def test_a_continental_court_at_war_may_be_asked(self, world):
        assert D.continental_system_join_refusal(world, "Austria", "France") is None
        assert D.continental_system_join_refusal(world, "Russia", "France") is None

    def test_an_island_or_portless_court_closes_nothing(self, world):
        assert D.continental_system_join_refusal(world, "Britain", "France") == "cs_no_ports"
        assert D.continental_system_join_refusal(world, "Saxony", "France") == "cs_no_ports"

    def test_the_trade_dominance_court_is_never_asked(self, world, monkeypatch):
        monkeypatch.setattr(naval, "trade_dominance_nation", lambda w: "Austria")
        assert (D.continental_system_join_refusal(world, "Austria", "France")
                == "cs_trade_dominance_court")

    def test_only_the_systems_lord_may_impose_it(self, world):
        # The System is France's own instrument (`apply_continental_system`
        # reads the player as its lord): no AI writes the clause (GR5 by scope).
        assert (D.continental_system_join_refusal(world, "Prussia", "Austria")
                == "cs_imposer_not_the_lord")

    def test_a_member_is_not_asked_twice(self, world):
        D.join_continental_system(world, "Austria", "France")
        assert (D.continental_system_join_refusal(world, "Austria", "France")
                == "cs_already_member")

    def test_our_own_satellites_join_on_their_own(self, world):
        assert (D.continental_system_join_refusal(world, "Holland", "France")
                == "cs_own_client")

    def test_a_court_cannot_impose_it_on_itself(self, world):
        assert (D.continental_system_join_refusal(world, "France", "France")
                == "dependency_direction_invalid")


# ═══════════════════════ THE MEMBERSHIP WRITE ══════════════════════════════

class TestTheOneMembershipWrite:
    def test_it_joins_once_announces_and_logs(self, world):
        assert D.join_continental_system(world, "Austria", "France",
                                         reason="by its peace with France")
        assert "Austria" in world.continental_system_members
        assert not D.join_continental_system(world, "Austria", "France")
        assert list(world.continental_system_members).count("Austria") == 1
        logged = _events(world, "continental_system_membership")
        assert len(logged) == 1, logged
        assert logged[0]["nation"] == "Austria"
        assert logged[0]["action"] == "joined"
        assert logged[0]["lord"] == "France"
        assert logged[0]["tail"] == " by its peace with France"

    def test_the_join_closes_a_port_against_britain(self, world):
        before = naval.closed_ports_against(world, "Britain")
        D.join_continental_system(world, "Austria", "France")
        assert naval.closed_ports_against(world, "Britain") == before + 1

    def test_the_terms_state_the_ports_and_the_alarm(self, world):
        terms = D.continental_system_join_terms(world, "Russia")
        assert terms == "closes 10 → 12 of 26 ports · +10 alarm", terms

    def test_a_set_shaped_store_stays_a_set(self, world):
        # (An EMPTY store reads as a list — `or []`, as the extracted arms
        # always read it.)
        world.continental_system_members = {"Naples"}
        D.join_continental_system(world, "Austria", "France")
        assert isinstance(world.continental_system_members, set)
        D.leave_continental_system(world, "Austria", reason="test")
        assert world.continental_system_members == {"Naples"}

    def test_the_joining_beat_rides_the_dispatch(self, world):
        D.join_continental_system(world, "Austria", "France", reason="by its peace with France")
        queued = [e for e in world.pending_dispatch_events
                  if e.get("type") == "diplomatic_continental_system"]
        assert len(queued) == 1, world.pending_dispatch_events
        assert queued[0]["template_vars"] == {
            "nation": "Austria", "action": "joined",
            "tail": " by its peace with France"}
        assert queued[0]["fog_rule"] == "always"
        from backend.game_logic.dispatch import _DIPLOMATIC_EVENT_TEMPLATES
        line = _DIPLOMATIC_EVENT_TEMPLATES["diplomatic_continental_system"]
        text = line if isinstance(line, str) else str(line)
        assert "{tail}" in text, text


    def test_the_beat_names_the_court_not_its_tag(self, world):
        """The PC-9 idiom: the raw tag had reached the dispatch for an
        auto-joined satellite ("KingdomOfItaly has joined …")."""
        from backend.game_logic.dispatch import _format_dispatch_event_text
        text = _format_dispatch_event_text(
            "diplomatic_continental_system",
            {"nation": "KingdomOfItaly", "action": "joined", "tail": ""})
        assert text == "The Kingdom of Italy has joined the Continental System."
        legacy = _format_dispatch_event_text(
            "diplomatic_continental_system", {"nation": "Austria", "action": "joined"})
        assert legacy == "Austria has joined the Continental System."
        left = _format_dispatch_event_text(
            "diplomatic_continental_system",
            {"nation": "Austria", "action": "left", "tail": " — now at war with France"})
        assert left == "Austria has left the Continental System — now at war with France."


# ═══════════════════════ THE EXIT ══════════════════════════════════════════

class TestTheExit:
    def _member_austria_at_peace(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "France", "Austria", "PEACE", "test_tilsit")
        D.join_continental_system(world, "Austria", "France")
        assert "Austria" in world.continental_system_members

    def test_a_member_at_war_with_the_lord_leaves(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        self._member_austria_at_peace(world)
        set_diplomatic_state(world, "France", "Austria", "WAR", "test_tilsit")
        assert "Austria" not in world.continental_system_members
        left = [e for e in _events(world, "continental_system_membership")
                if e.get("action") == "left"]
        assert len(left) == 1, left
        assert left[0]["tail"] == " — now at war with France"

    def test_lever_down_the_member_keeps_counting(self, world, monkeypatch):
        from backend.game_logic.diplomacy import set_diplomatic_state
        monkeypatch.setattr(D, "A_MEMBER_AT_WAR_LEAVES_THE_SYSTEM", False)
        self._member_austria_at_peace(world)
        set_diplomatic_state(world, "France", "Austria", "WAR", "test_tilsit")
        assert "Austria" in world.continental_system_members

    def test_a_war_with_another_court_is_not_the_exit(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        self._member_austria_at_peace(world)
        set_diplomatic_state(world, "Austria", "Prussia", "WAR", "test_tilsit")
        assert "Austria" in world.continental_system_members


# ═══════════════════════ THE JOINT ROAD ════════════════════════════════════

class TestTheJointRoad:
    def test_the_package_applies_the_clause_and_charges_the_alarm(self, world):
        from backend.game_logic.settlement_ratify import _apply_settlement_terms
        threat = int(world.threat_by_target.get("France", 0))
        applied = _apply_settlement_terms(world, settlement_terms=[_cs_term()])
        assert any(t.get("type") == CS for t in applied), applied
        assert "Austria" in world.continental_system_members
        assert int(world.threat_by_target.get("France", 0)) == min(100, threat + 10)
        assert any(r.get("source") == "continental_system"
                   for r in world.threat_sources_this_turn)

    def test_the_predicate_re_runs_at_ratification(self, world):
        """A court the predicate refuses (an island closes no continental
        port) is never enrolled — the case the join's own idempotency does
        not cover; and a member is not enrolled twice."""
        from backend.game_logic.settlement_ratify import _apply_settlement_terms
        threat = int(world.threat_by_target.get("France", 0))
        applied = _apply_settlement_terms(world, settlement_terms=[_cs_term(court="Britain")])
        assert not any(t.get("type") == CS for t in applied), applied
        assert "Britain" not in world.continental_system_members
        assert int(world.threat_by_target.get("France", 0)) == threat
        D.join_continental_system(world, "Austria", "France")
        applied = _apply_settlement_terms(world, settlement_terms=[_cs_term()])
        assert not any(t.get("type") == CS for t in applied), applied
        assert int(world.threat_by_target.get("France", 0)) == threat

    def test_no_alliance_is_formed(self, world):
        from backend.game_logic.settlement_ratify import _apply_settlement_terms
        _apply_settlement_terms(world, settlement_terms=[_cs_term()])
        assert world.get_diplomatic_state("France", "Austria") != "ALLIANCE"


# ═══════════════════════ THE SEPARATE PEACE ════════════════════════════════

class TestTheSeparatePeaceCarriesIt:
    def test_it_is_seeded_as_a_valued_demand(self):
        from backend.game_logic.settlement_actions import _pair_substitute_seed_terms
        seed = _pair_substitute_seed_terms(
            [_cs_term()], target="Austria", proposer_leader="France")
        assert {"type": CS, "value": 1} in seed["demands"], seed
        assert not any(s.get("type") == CS for s in seed["sweeteners"])

    def test_another_courts_or_an_allys_clause_does_not_travel(self):
        from backend.game_logic.settlement_actions import _pair_substitute_seed_terms
        for term in (_cs_term(court="Russia"), _cs_term(imposer="Spain")):
            seed = _pair_substitute_seed_terms(
                [term], target="Austria", proposer_leader="France")
            assert not any(d.get("type") == CS for d in seed["demands"]), (term, seed)

    def test_the_carried_set_and_the_dropped_labels_agree(self):
        from backend.game_logic.settlement_staging import (
            PAIR_SUBSTITUTE_CARRIED_TYPES, _PAIR_SUBSTITUTE_DROPPED_LABELS,
        )
        assert CS in PAIR_SUBSTITUTE_CARRIED_TYPES
        assert "continental_system" not in _PAIR_SUBSTITUTE_DROPPED_LABELS
        assert CS not in _PAIR_SUBSTITUTE_DROPPED_LABELS


class TestTheBilateralRatifies:
    def _ratify(self, world, court="Austria"):
        return world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": court,
            "sweeteners": [],
            "demands": [_cs_demand()],
        })

    def test_austria_signs_into_the_system_at_peace_not_allied(self, world):
        threat = int(world.threat_by_target.get("France", 0))
        self._ratify(world)
        assert "Austria" in world.continental_system_members
        assert world.get_diplomatic_state("France", "Austria") == "PEACE"
        assert int(world.threat_by_target.get("France", 0)) == min(100, threat + 10)

    def test_the_summary_names_it_and_it_is_not_a_white_peace(self, world):
        event = self._ratify(world)
        summary = event["peace_ratification_summary"]
        joined = " ".join(summary["terms_ratified"])
        assert "Continental System" in joined, summary["terms_ratified"]
        assert "continental_system_join" not in joined
        assert summary["war_outcome"] != "white_peace"

    def test_the_log_does_not_call_it_a_white_peace(self, world):
        self._ratify(world)
        ratified = [e for e in world.event_log if e.get("type") == "peace_ratified"]
        assert ratified, "no peace_ratified event"
        assert ratified[-1]["war_outcome"] != "white_peace", ratified[-1]

    def test_a_court_the_predicate_refuses_is_not_enrolled(self, world):
        """The bilateral road has no restage validator, so the predicate
        re-runs at ratification: an island court closes no continental port."""
        threat = int(world.threat_by_target.get("France", 0))
        self._ratify(world, court="Britain")
        assert "Britain" not in world.continental_system_members
        assert int(world.threat_by_target.get("France", 0)) == threat

    def test_a_court_that_can_no_longer_be_asked_is_not_enrolled(self, world):
        D.join_continental_system(world, "Austria", "France")
        before = list(world.event_log or [])
        threat = int(world.threat_by_target.get("France", 0))
        self._ratify(world)
        assert list(world.continental_system_members).count("Austria") == 1
        assert int(world.threat_by_target.get("France", 0)) == threat
        assert len(_events(world, "continental_system_membership")) == len(
            [e for e in before if e.get("type") == "continental_system_membership"])


# ═══════════════════════ THE PRICE ═════════════════════════════════════════

class TestThePrice:
    def _scored(self, world, court, france_points, age=10, demands=None):
        from backend.game_logic.diplomacy import calculate_acceptance
        pair = world._make_diplo_key("France", court)
        first = pair.split("|")[0]
        world.war_scores[pair] = france_points if first == "France" else -france_points
        world.war_start_turns[pair] = int(world.current_turn) - age
        world.invalidate_active_nations_cache()
        return calculate_acceptance({
            "type": "peace", "proposer_nation": "France", "target_nation": court,
            "sweeteners": [],
            "demands": [_cs_demand()] if demands is None else demands,
        }, world)

    def test_the_demand_value_and_both_harshness_dialects(self):
        from backend.game_logic.diplomatic_templates import calculate_raw_treaty_harshness
        assert D.DEMAND_VALUES[CS] == -10
        assert calculate_raw_treaty_harshness({"clauses": [_cs_term()]}) == pytest.approx(0.2)
        assert calculate_raw_treaty_harshness({"demands": [_cs_demand()]}) == pytest.approx(0.2)

    def test_the_clause_costs_ten_points_over_a_plain_peace(self, world):
        plain = self._scored(world, "Austria", 30, demands=[])["score"]
        cs = self._scored(world, "Austria", 30)["score"]
        assert plain - cs == 10, (plain, cs)

    def test_a_court_at_an_even_war_score_refuses_it(self, world):
        """Measured at the build (§6.6 item 4): at war age 10, France level
        with the court — Austria 24, Russia 28 against the bar of 50."""
        assert self._scored(world, "Austria", 0)["score"] < 50
        assert self._scored(world, "Russia", 0)["score"] < 50

    def test_a_beaten_court_signs_it(self, world):
        """Measured at the build: Austria signs at 60 points (52), Russia at
        45 (52). No sweetener."""
        assert self._scored(world, "Austria", 60)["score"] >= 50
        assert self._scored(world, "Russia", 45)["score"] >= 50

    def test_it_is_a_material_demand_the_war_age_prices(self, world):
        young = self._scored(world, "Austria", 60, age=0)
        assert young["components"]["war_age_penalty"] < 0
        assert young["score"] < 50


# ═══════════════════════ THE TABLE ═════════════════════════════════════════

def _rows(world, court):
    from backend.game_logic.settlement_staging import _court_demand_suggestions
    wid, inst = _war_with(world, court)
    rows = _court_demand_suggestions(
        world, court=court, direction="demand", war_id=wid, draft_key="d",
        war_instance=inst, proposer_side_participants=["France"],
        proposer_holdings=set(world.get_nation_regions("France")),
        proposer_leader="France", settlement_terms=[], promised_regions=set(),
        treasury_remaining=int(world.nation_gold.get("France", 0)),
        income_cache={})
    flat = rows[0] if isinstance(rows, tuple) else rows
    return flat


class TestTheGuidedRow:
    def test_austria_is_offered_the_clause_with_its_price(self, world):
        rows = [r for r in _rows(world, "Austria") if r.get("clause_type") == CS]
        assert len(rows) == 1, rows
        row = rows[0]
        assert row["label"] == "Austria joins the Continental System"
        assert row["available"] is True
        assert row["terms_display"] == "closes 10 → 11 of 26 ports · +10 alarm"
        assert row["reason_display"]
        assert row["action_params"] == {
            "nation": "Austria", "group": "demand", "clause_type": CS}

    def test_a_member_is_shown_the_row_greyed_with_its_reason(self, world):
        D.join_continental_system(world, "Austria", "France")
        rows = [r for r in _rows(world, "Austria") if r.get("clause_type") == CS]
        assert len(rows) == 1
        assert rows[0]["available"] is False
        assert rows[0]["disabled_reason_display"]

    def test_a_portless_court_is_offered_nothing(self, world, monkeypatch):
        monkeypatch.setattr(D, "continental_system_join_refusal",
                            lambda w, n, i: "cs_no_ports")
        rows = [r for r in _rows(world, "Austria") if r.get("clause_type") == CS]
        assert rows == []

    def test_the_client_states_the_price_on_a_clickable_row(self):
        src = (REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
               / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
        body = src[src.index("func _build_suggestion_lines"):]
        body = body[:body.index("\nfunc ")]
        available_arm = body[body.index('var bbcode = "          [url=sugg:'):]
        assert 'sugg.get("terms_display")' in available_arm


# ═══════════════════════ THE ADD VERB (SF7-X5) ═════════════════════════════

_SCORER_PATH = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"


def _scorer(world=None, *, accepting_leader=None, **kwargs):
    return {"score": 60, "verdict": "accept", "components": {}, "component_debug": {},
            "feedback": [], "hard_stops": [], "accept_threshold": 50,
            "near_acceptable_threshold": 35, "side_pressure_score": 30,
            "raw_total": 60, "raw_total_harshness": 0.0, "direct_scores": {},
            "direct_score_sources": {}}


def _staged(world, court):
    from backend.game_logic.settlement_preview import stage_settlement_confirm
    wid, _ = _war_with(world, court)
    with patch(_SCORER_PATH, side_effect=_scorer):
        staged = stage_settlement_confirm(
            world, war_id=wid, actor_nation="France",
            settlement_terms=[{"type": "peace"}],
            covered_enemy_participants=[court], selected_target_nation=court,
            caller_kind="player_editor", dialogue_mode="PROPOSE")
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


def _add(world, dialogue, params):
    from backend.game_logic.settlement_preview import handle_settlement_dialogue_action
    with patch(_SCORER_PATH, side_effect=_scorer):
        return handle_settlement_dialogue_action(
            world, action="settlement_demand_add", dialogue=dialogue,
            action_params={"action": "settlement_demand_add", **params})


def _clauses(result, ctype):
    terms = (result.get("diplomatic_dialogue") or {}).get("settlement_terms") or []
    return [dict(t) for t in terms if t.get("type") == ctype]


class TestTheAddVerb:
    def test_the_tilsit_clause_is_authored_court_to_emperor(self, world):
        result = _add(world, _staged(world, "Austria"),
                      {"nation": "Austria", "group": "demand", "clause_type": CS})
        assert result.get("success"), result
        added = _clauses(result, CS)
        assert len(added) == 1
        assert added[0]["from"] == "Austria" and added[0]["to"] == "France"

    def test_an_ineligible_court_is_refused_with_its_reason(self, world):
        D.join_continental_system(world, "Austria", "France")
        result = _add(world, _staged(world, "Austria"),
                      {"nation": "Austria", "group": "demand", "clause_type": CS})
        assert not result.get("success")
        assert _clauses(result, CS) == []

    def test_the_plain_alliance_writes_no_system(self, world):
        result = _add(world, _staged(world, "Austria"),
                      {"nation": "Austria", "group": "demand", "clause_type": "forced_alliance"})
        fa = _clauses(result, "forced_alliance")
        assert len(fa) == 1, result
        assert fa[0]["includes_continental_system"] is False

    def test_the_system_link_writes_it(self, world):
        result = _add(world, _staged(world, "Austria"),
                      {"nation": "Austria", "group": "demand", "clause_type": "forced_alliance",
                       "includes_continental_system": True})
        assert _clauses(result, "forced_alliance")[0]["includes_continental_system"] is True

    def test_lever_down_the_plain_link_writes_nothing(self, world, monkeypatch):
        monkeypatch.setattr(SA, "THE_PLAIN_ALLIANCE_KEEPS_NO_SYSTEM", False)
        result = _add(world, _staged(world, "Austria"),
                      {"nation": "Austria", "group": "demand", "clause_type": "forced_alliance"})
        assert "includes_continental_system" not in _clauses(result, "forced_alliance")[0]

    def test_the_plain_alliance_ratifies_without_the_system(self, world):
        """The defect's consequence, end to end on the joint arm: the plain
        alliance enrolled the court and charged the System's alarm."""
        from backend.game_logic.settlement_scoring import compute_forced_alliance_threat_preview
        plain = {"type": "forced_alliance", "from": "Austria", "to": "France",
                 "includes_continental_system": False}
        keyless = {"type": "forced_alliance", "from": "Austria", "to": "France"}
        assert compute_forced_alliance_threat_preview(
            world, settlement_terms=[plain])["projected_threat_delta"] == 15
        assert compute_forced_alliance_threat_preview(
            world, settlement_terms=[keyless])["projected_threat_delta"] == 25


class TestTheDisplaysReadTheCanonicalDefault:
    def test_a_keyless_forced_alliance_reads_as_with_the_system(self):
        from backend.game_logic.settlement_staging import _guided_line_display
        _, keyless = _guided_line_display(
            {"type": "forced_alliance", "from": "Austria", "to": "France"}, "Austria")
        _, plain = _guided_line_display(
            {"type": "forced_alliance", "from": "Austria", "to": "France",
             "includes_continental_system": False}, "Austria")
        assert keyless == "Forced alliance (Continental System)"
        assert plain == "Forced alliance"

    def test_the_tilsit_line_on_the_court_row(self):
        from backend.game_logic.settlement_staging import _guided_line_display
        tag, line = _guided_line_display(_cs_term(), "Austria")
        assert (tag, line) == ("Demanded", "Join the Continental System")

    def test_the_bilateral_label_honours_an_explicit_no(self):
        from backend.game_logic.diplomatic_templates import annotate_peace_terms
        rows = annotate_peace_terms({"demands": [
            {"type": "forced_alliance", "value": 1, "includes_continental_system": False},
            {"type": "forced_alliance", "value": 1},
            _cs_demand()]}, "France", "Austria")
        labels = [r["display_label"] for r in rows]
        assert labels[0] == "Austria enters ALLIANCE with France"
        assert labels[1].endswith("and joins the Continental System")
        assert labels[2] == ("Austria joins the Continental System and closes its "
                             "ports to British trade")


class TestTheToggleRowNamesTheJoiner:
    def test_the_row_names_the_court_forced_into_the_alliance(self, world):
        from backend.game_logic.settlement_scoring import (
            compute_forced_alliance_continental_toggle_differential,
        )
        rows = compute_forced_alliance_continental_toggle_differential(
            world, war_id=None, settlement_terms=[
                {"type": "forced_alliance", "from": "Austria", "to": "France",
                 "includes_continental_system": True}])
        assert rows[0]["display"] == (
            "Adds Austria to the Continental System; extra threat cost applies.")


# ═══════════════════════ THE PREVIEW, THE COUNTER, THE ADMIRALTY ════════════

class TestTheAppliedClausesPreview:
    def test_the_row_states_what_will_mutate(self, world):
        from backend.game_logic.settlement_presentation import build_applied_clauses_preview
        rows = build_applied_clauses_preview([_cs_term()], world=world)
        row = [r for r in rows if r["type"] == CS][0]
        assert row["from"] == "Austria" and row["to"] == "France"
        assert row["projected_threat_delta"] == 10
        assert row["terms_display"] == "closes 10 → 11 of 26 ports · +10 alarm"
        assert row["type_display"] == "Joins the Continental System"


class TestTheCounterOfferKeepsTheClause:
    """`generate_counter_offer` strikes whichever single element the court
    hates most — the IGR-D carve rule: the clause the peace was asked FOR
    is never re-drafted away; a court that will not keep the System refuses."""

    def _proposal(self, demands=None):
        return {"type": "peace", "proposer_nation": "France",
                "target_nation": "Austria", "sweeteners": [],
                "demands": demands if demands is not None
                else [_cs_demand(), {"type": "gold_lump", "value": 40}]}

    def test_a_counter_keeps_the_clause_and_strikes_the_gold(self, world):
        """Staged so the exemption decides it: striking the clause raises the
        score MORE than striking the gold (measured 42 -> 56 against 42 -> 48
        at war age 10, France 45 points ahead), so without the exemption the
        counter strikes the System and keeps the gold."""
        from backend.game_logic.ai_diplomacy import generate_counter_offer
        from backend.game_logic.diplomacy import calculate_acceptance
        pair = world._make_diplo_key("France", "Austria")
        first = pair.split("|")[0]
        world.war_scores[pair] = 45 if first == "France" else -45
        world.war_start_turns[pair] = int(world.current_turn) - 10
        world.nation_dp = {"Austria": 5}
        score = calculate_acceptance(self._proposal(), world)["score"]
        assert 30 <= score < 50, f"precondition: not in the counter band ({score})"
        cs_struck = calculate_acceptance(
            self._proposal([{"type": "gold_lump", "value": 40}]), world)["score"]
        gold_struck = calculate_acceptance(
            self._proposal([_cs_demand()]), world)["score"]
        assert cs_struck > gold_struck, (
            "precondition: the clause must be the element the court hates most")
        counter = generate_counter_offer(self._proposal(), world)
        assert counter is not None, "precondition: no counter was built"
        types = [d.get("type") for d in counter.get("demands", [])]
        assert CS in types, f"the counter re-drafted the System away: {types}"

    def test_the_exemption_sits_in_the_strike_loop(self):
        import inspect
        from backend.game_logic import ai_diplomacy
        body = inspect.getsource(ai_diplomacy.generate_counter_offer)
        loop = body[body.index("for i, d in enumerate("):]
        loop = loop[:loop.index("test_terms = copy.deepcopy(terms)")]
        assert 'd.get("type") == "continental_system_join"' in loop


class TestTheAdmiraltyNamesTheMembers:
    def test_the_members_line(self, world):
        D.join_continental_system(world, "Russia", "France")
        D.join_continental_system(world, "Austria", "France")
        report = naval.build_admiralty_report(world)
        assert report["continental_system"]["members_line"] == (
            "Members of the System: Austria (1 port) and Russia (2 ports)")

    def test_no_members_no_line(self, world):
        report = naval.build_admiralty_report(world)
        assert report["continental_system"]["members_line"] == ""

    def test_the_ledger_renders_it(self):
        src = (REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
               / "strategic_ledger.gd").read_text(encoding="utf-8")
        assert 'cs.get("members_line", "")' in src


# ═══════════════════════ THE LOG ═══════════════════════════════════════════

class TestTheCampaignLog:
    def test_the_type_is_registered_with_its_one_liner(self, world):
        from backend import campaign_log as CL
        assert "continental_system_membership" in CL.CAMPAIGN_LOG_TYPES
        line = CL.format_event_oneliner({
            "type": "continental_system_membership", "nation": "Austria",
            "action": "joined", "lord": "France",
            "tail": " by its peace with France", "turn": 9})
        assert re.search(r"Austria joins the Continental System by its peace with France", line), line


# ═══════════════════════ THE TILSIT ROAD (the benchmark arm) ════════════════

class TestTheTilsitRoadArm:
    """`tools/playtest_scripts/sf_nav1_tilsit_road.json`, benchmark
    NAV1T-H/A/M — the Step 6 arm with the clause on the separate peaces.
    The arm's played readings are the landing record's (per seed, never a
    pin); these pin what the arm IS."""

    def _script(self):
        import json
        path = REPO_ROOT / "tools" / "playtest_scripts" / "sf_nav1_tilsit_road.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def _lines(self):
        return [line for v in self._script()["turns"].values() for line in v]

    def test_the_arm_asks_through_the_tables_own_row(self):
        adds = [line for line in self._lines()
                if line.startswith("@settlement_demand_add") and CS in line]
        assert any('"Austria"' in line for line in adds)
        assert any('"Russia"' in line for line in adds)
        assert "@seek_bilateral_peace" in self._lines()

    def test_the_emperor_goes_home_on_turn_one(self):
        assert self._script()["turns"]["1"][0] == "Napoleon, march to Paris"

    def test_the_benchmark_declines_the_courts_own_truces(self):
        from tools import score_run as sr
        for name in ("NAV1T-H", "NAV1T-A", "NAV1T-M"):
            argv = sr.ARMS[name]["argv"]
            assert argv[argv.index("--decline-from") + 1] == (
                "Britain,Portugal,PapalStates,Naples,Austria,Russia")
            assert argv[argv.index("--script") + 1].endswith("sf_nav1_tilsit_road.json")
            assert "--save-at" in argv

