"""Slice E settlement presentation tests.

Pins the Slice E presentation, ledger, and logs gate from
`docs/WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md`:

- Settlement event contract from spec §11.6 (event family, route ids,
  review targets, fog filter, one-liner shape).
- Top-four primary-beat cap + digest overflow per spec §11.6 line 1279.
- Warning cap per spec §16.3 (hard stops inline, top-2 warnings inline,
  rest behind "View all concerns").
- Sectioned settlement review per spec §16.2 (Terms / Allies / Warnings /
  Acceptance with compact / medium / verbose densities).
- Awe set-piece tagging per spec §20.8.
- Diplomatic ledger `recent_settlements` payload + war-status panel
  contribution-share rows.
- Notification rail spotlight metadata for major settlement outcomes.
"""

from __future__ import annotations

from typing import Any, Dict, List

from backend.campaign_log import filter_campaign_log
from backend.game_logic import settlement_presentation as sp
from backend.game_logic.dispatch import (
    _build_diplomatic_events_section,
    _enforce_settlement_primary_beat_cap,
    _is_dispatch_event_visible,
)
from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
from backend.game_logic.settlement_presentation import (
    SETTLEMENT_EVENT_FAMILY,
    SETTLEMENT_INLINE_WARNING_CAP,
    SETTLEMENT_LEDGER_DEFAULT_ROWS,
    SETTLEMENT_PRIMARY_BEAT_CAP,
    SETTLEMENT_REVIEW_TARGET_ACTIVE,
    SETTLEMENT_REVIEW_TARGET_ARCHIVED,
    SETTLEMENT_ROUTES,
    SETTLEMENT_STANDING_ROW_CAP,
    apply_warning_cap,
    build_contribution_share_rows,
    build_settlement_review,
    cap_settlement_dispatch_lines,
    compose_digest_oneliner,
    compose_summary_oneliner,
    detect_awe_set_pieces,
    is_settlement_event_type,
    is_settlement_event_visible,
    recent_settlement_summaries,
    settlement_notification_meta,
    settlement_priority,
    settlement_review_target,
    settlement_route,
)
from backend.game_logic.settlement_reactions import route_settlement_reactions
from backend.game_logic.war_status import build_active_wars
from backend.models.region import REGIONS_DATA
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _install_two_v_two_war(world: WorldState) -> Dict:
    war = make_synthetic_war_instance(
        "war_e",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_e"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_start_turns[pair] = world.current_turn
        world.war_scores[pair] = 0
        world.battle_records[pair] = []
    world.invalidate_war_instance_indexes()
    return war


def _make_settlement_event(
    *,
    war_id: str = "war_e",
    turn: int = 5,
    war_ended: bool = False,
    covered: List[str] | None = None,
    proposer_members: List[str] | None = None,
    accepting_members: List[str] | None = None,
    reactions: List[Dict[str, Any]] | None = None,
    awe_tags: List[str] | None = None,
    applied_clauses: List[Dict[str, Any]] | None = None,
    terms_summary: List[str] | None = None,
) -> Dict[str, Any]:
    review_target = (
        SETTLEMENT_REVIEW_TARGET_ARCHIVED
        if war_ended
        else SETTLEMENT_REVIEW_TARGET_ACTIVE
    )
    event: Dict[str, Any] = {
        "type": "settlement_summary",
        "turn": turn,
        "war_id": war_id,
        "covered_enemy_participants": list(covered or ["Austria"]),
        "proposer_side": "attackers",
        "accepting_side": "defenders",
        "proposer_members": list(proposer_members or ["France"]),
        "accepting_members": list(accepting_members or ["Austria"]),
        "terms_summary": list(terms_summary or ["territory_cede: Austria→France"]),
        "applied_clauses": list(applied_clauses or []),
        "participant_reactions": list(reactions or []),
        "war_ended": war_ended,
        "balance_projection": {},
        "route": {
            "event_family": SETTLEMENT_EVENT_FAMILY,
            "review_target": review_target,
            "route_id": f"settlement_summary:{war_id}:{turn}",
        },
    }
    if awe_tags:
        event["awe_tags"] = list(awe_tags)
    return event


# ===========================================================================
# Route metadata + priorities
# ===========================================================================


class TestSettlementRoutes:
    def test_summary_and_digest_have_routes(self):
        assert "settlement_summary" in SETTLEMENT_ROUTES
        assert "settlement_digest" in SETTLEMENT_ROUTES
        for route in SETTLEMENT_ROUTES.values():
            assert route["event_family"] == SETTLEMENT_EVENT_FAMILY

    def test_settlement_route_returns_copy(self):
        a = settlement_route("settlement_summary")
        a["mutated"] = True
        b = settlement_route("settlement_summary")
        assert "mutated" not in b

    def test_is_settlement_event_type(self):
        assert is_settlement_event_type("settlement_summary")
        assert is_settlement_event_type("settlement_digest")
        assert not is_settlement_event_type("bargain_fulfilled")
        assert not is_settlement_event_type("balance_of_europe_shifted")

    def test_summary_priority_defaults_to_high_without_awe(self):
        event = _make_settlement_event()
        assert settlement_priority("settlement_summary", event) == "HIGH"

    def test_summary_priority_upgrades_with_major_shut_out(self):
        event = _make_settlement_event(reactions=[
            {"kind": "ally_shut_out", "ally": "Prussia",
             "severity": "major_shut_out"},
        ])
        assert settlement_priority("settlement_summary", event) == "CRITICAL"

    def test_summary_priority_upgrades_with_bargain_breach(self):
        event = _make_settlement_event(reactions=[
            {"kind": "bargain_breach_at_settlement", "promiser": "France",
             "beneficiary": "Saxony"},
        ])
        assert settlement_priority("settlement_summary", event) == "CRITICAL"

    def test_summary_priority_upgrades_with_awe_tags(self):
        event = _make_settlement_event(awe_tags=["triple_forced_alignment"])
        assert settlement_priority("settlement_summary", event) == "CRITICAL"

    def test_digest_priority_stays_normal(self):
        digest = {"type": "settlement_digest", "war_id": "war_e",
                  "hidden_reaction_count": 4}
        assert settlement_priority("settlement_digest", digest) == "NORMAL"


# ===========================================================================
# Review-target routing
# ===========================================================================


class TestReviewTarget:
    def test_active_war_routes_to_settlement_review(self):
        event = _make_settlement_event(war_ended=False)
        assert (
            settlement_review_target(event)
            == SETTLEMENT_REVIEW_TARGET_ACTIVE
        )

    def test_archived_war_routes_to_diplomatic_ledger(self):
        event = _make_settlement_event(war_ended=True)
        assert (
            settlement_review_target(event)
            == SETTLEMENT_REVIEW_TARGET_ARCHIVED
        )

    def test_route_field_takes_precedence(self):
        event = _make_settlement_event(war_ended=False)
        event["route"]["review_target"] = "diplomatic_ledger"
        assert settlement_review_target(event) == "diplomatic_ledger"

    def test_missing_event_defaults_to_active(self):
        assert (
            settlement_review_target(None)
            == SETTLEMENT_REVIEW_TARGET_ACTIVE
        )


# ===========================================================================
# Fog filter (spec §11.6 line 1287)
# ===========================================================================


class TestFogFilter:
    def test_france_always_sees_its_own_settlement(self):
        world = WorldState()
        _install_two_v_two_war(world)
        event = _make_settlement_event(
            proposer_members=["France"], accepting_members=["Austria"],
        )
        assert is_settlement_event_visible(event, world, "France")

    def test_player_visible_through_covered_participant(self):
        world = WorldState()
        _install_two_v_two_war(world)
        # Player is France (not in this synthetic event's proposer or
        # accepting members) but Prussia is at PARTIAL visibility by
        # default through neighbouring French marshals, so participant
        # fog grants visibility.
        event = _make_settlement_event(
            war_id="war_other",
            proposer_members=["Saxony"], accepting_members=["Prussia"],
            covered=["Prussia"],
        )
        assert is_settlement_event_visible(event, world, "France")

    def test_invisible_when_no_overlap_and_player_not_involved(self):
        world = WorldState()
        # Wholly foreign settlement: Sweden vs Russia, no France
        # participation, no war pair touching France.
        event = _make_settlement_event(
            war_id="far_off",
            proposer_members=["Sweden"], accepting_members=["Russia"],
            covered=["Russia"],
        )
        # Player is Britain — Britain is not a participant, no covered
        # participant is visible (no marshals = UNKNOWN visibility), so
        # the event should be filtered out.
        assert not is_settlement_event_visible(event, world, "Britain")

    def test_non_settlement_event_never_visible_through_settlement_filter(self):
        event = {"type": "bargain_fulfilled", "war_id": "war_e"}
        world = WorldState()
        # The settlement filter rejects unrelated events entirely.
        assert not is_settlement_event_visible(event, world, "France")

    def test_digest_visible_when_summary_visible(self):
        world = WorldState()
        _install_two_v_two_war(world)
        digest = {
            "type": "settlement_digest", "war_id": "war_e",
            "covered_enemy_participants": ["Austria"],
            "proposer_members": ["France"],
            "accepting_members": ["Austria"],
            "hidden_reaction_count": 5,
            "route": {
                "event_family": SETTLEMENT_EVENT_FAMILY,
                "review_target": SETTLEMENT_REVIEW_TARGET_ARCHIVED,
                "route_id": "settlement_digest:war_e:5",
            },
        }
        assert is_settlement_event_visible(digest, world, "France")


# ===========================================================================
# One-liner formatting (spec §11.6 line 1287)
# ===========================================================================


class TestOneLiner:
    def test_summary_oneliner_caps_named_at_three_with_more(self):
        event = _make_settlement_event(reactions=[
            {"kind": "ally_rewarded", "ally": "Saxony"},
            {"kind": "enemy_sold_out", "burdened_participant": "Prussia"},
            {"kind": "ally_shut_out", "ally": "Bavaria"},
            {"kind": "ally_shut_out", "ally": "Russia"},
            {"kind": "ally_shut_out", "ally": "Sweden"},
        ])
        line = compose_summary_oneliner(event)
        assert "Saxony" in line and "Prussia" in line and "Bavaria" in line
        assert "+2 more" in line

    def test_summary_oneliner_no_more_when_under_cap(self):
        event = _make_settlement_event(reactions=[
            {"kind": "ally_rewarded", "ally": "Saxony"},
        ])
        line = compose_summary_oneliner(event)
        assert "Saxony" in line and "more" not in line

    def test_summary_oneliner_empty_reactions(self):
        event = _make_settlement_event(reactions=[])
        line = compose_summary_oneliner(event)
        assert "no participant reactions" in line

    def test_summary_oneliner_uses_war_label_when_world_provided(self):
        world = WorldState()
        _install_two_v_two_war(world)
        event = _make_settlement_event()
        line = compose_summary_oneliner(event, world=world)
        # War label should reflect the synthetic 2v2 war.
        assert "war" in line.lower() or "France" in line

    def test_digest_oneliner_includes_hidden_count(self):
        digest = {"type": "settlement_digest", "war_id": "war_42",
                  "hidden_reaction_count": 7}
        line = compose_digest_oneliner(digest)
        assert "7" in line
        assert "war_42" in line


# ===========================================================================
# Top-N cap + digest overflow (spec §11.6 line 1279)
# ===========================================================================


class TestTopFourCap:
    def test_cap_returns_unchanged_under_threshold(self):
        lines = [
            {"type": "settlement_summary", "text": "a"},
            {"type": "settlement_summary", "text": "b"},
        ]
        kept, hidden = cap_settlement_dispatch_lines(lines, cap=4)
        assert len(kept) == 2 and hidden == 0

    def test_cap_drops_overflow(self):
        lines = [
            {"type": "settlement_summary", "text": str(i)} for i in range(7)
        ]
        kept, hidden = cap_settlement_dispatch_lines(lines, cap=4)
        assert len(kept) == 4 and hidden == 3

    def test_cap_zero_drops_everything(self):
        lines = [{"type": "settlement_summary", "text": "x"}]
        kept, hidden = cap_settlement_dispatch_lines(lines, cap=0)
        assert kept == [] and hidden == 1

    def test_dispatch_enforces_cap_per_ratification(self):
        # Build 7 settlement summary entries from the same ratification;
        # only the first 4 should survive.
        rendered = [
            {"type": "settlement_summary", "text": f"line {i}",
             "war_id": "war_z", "route_id": "settlement_summary:war_z:5"}
            for i in range(7)
        ]
        capped = _enforce_settlement_primary_beat_cap(
            rendered, list(range(len(rendered))),
        )
        assert len(capped) == SETTLEMENT_PRIMARY_BEAT_CAP

    def test_dispatch_does_not_cap_across_ratifications(self):
        # Three different ratifications, each with two summaries.
        rendered: List[Dict[str, Any]] = []
        indexes: List[int] = []
        for war in ("war_a", "war_b", "war_c"):
            for _ in range(2):
                rendered.append({
                    "type": "settlement_summary",
                    "text": "x",
                    "war_id": war,
                    "route_id": f"settlement_summary:{war}:5",
                })
                indexes.append(len(rendered) - 1)
        capped = _enforce_settlement_primary_beat_cap(rendered, indexes)
        assert len(capped) == 6  # nothing dropped


# ===========================================================================
# Warning cap (spec §16.3)
# ===========================================================================


class TestWarningCap:
    def test_hard_stops_always_inline(self):
        warnings = [
            {"severity": "HARD_STOP", "code": "non_participant",
             "salience": 100, "message": "..."},
            {"severity": "HARD_STOP", "code": "self_target",
             "salience": 50, "message": "..."},
        ]
        result = apply_warning_cap(warnings)
        assert len(result["inline"]) == 2
        assert result["overflow"] == []

    def test_top_two_warnings_inline_rest_overflow(self):
        warnings = [
            {"severity": "WARNING", "code": "w1", "salience": 90},
            {"severity": "WARNING", "code": "w2", "salience": 80},
            {"severity": "WARNING", "code": "w3", "salience": 70},
            {"severity": "WARNING", "code": "w4", "salience": 60},
            {"severity": "INFO", "code": "i1", "salience": 50},
        ]
        result = apply_warning_cap(warnings)
        # Two top WARNINGs inline.
        assert len(result["inline"]) == SETTLEMENT_INLINE_WARNING_CAP
        codes_inline = {w["code"] for w in result["inline"]}
        assert codes_inline == {"w1", "w2"}
        codes_overflow = {w["code"] for w in result["overflow"]}
        assert codes_overflow == {"w3", "w4", "i1"}

    def test_hard_stop_does_not_consume_warning_slot(self):
        warnings = [
            {"severity": "HARD_STOP", "code": "blocker", "salience": 100},
            {"severity": "WARNING", "code": "w1", "salience": 90},
            {"severity": "WARNING", "code": "w2", "salience": 80},
            {"severity": "INFO", "code": "i1", "salience": 50},
        ]
        result = apply_warning_cap(warnings)
        # 1 hard stop + 2 warnings inline.
        assert len(result["inline"]) == 3
        assert {"i1"} == {w["code"] for w in result["overflow"]}


# ===========================================================================
# Sectioned settlement review (spec §16.2)
# ===========================================================================


class TestSettlementReview:
    def _ratification_payload(self, density: str = "compact") -> Dict[str, Any]:
        terms = [
            {"type": "territory_cede", "from": "Austria", "to": "France",
             "regions": ["Bohemia"], "marginal_cost": -5},
            {"type": "territory_cede", "from": "Austria", "to": "Saxony",
             "regions": ["Silesia"], "marginal_cost": -3},
            {"type": "forced_alliance", "from": "Austria", "to": "France"},
            {"type": "indemnity", "from": "Austria", "to": "France",
             "amount": 2000},
            {"type": "indemnity", "from": "Austria", "to": "Saxony",
             "amount": 500},
            {"type": "continental_system_join", "from": "Austria"},
            {"type": "war_objective_resolution", "objective": "defense"},
        ]
        allies = [
            {"nation": "France", "standing": "seat",
             "material_share": 0.55, "is_leader": True},
            {"nation": "Saxony", "standing": "seat",
             "material_share": 0.30, "is_beneficiary": True},
            {"nation": "Bavaria", "standing": "consult",
             "material_share": 0.10},
            {"nation": "Russia", "standing": "consult",
             "material_share": 0.08},
            {"nation": "Sweden", "standing": "consult",
             "material_share": 0.05},
            {"nation": "Denmark-Norway", "standing": "no_standing",
             "material_share": 0.02},
            {"nation": "Portugal", "standing": "no_standing",
             "material_share": 0.0},
        ]
        warnings = [
            {"severity": "HARD_STOP", "code": "blocker", "salience": 100},
            {"severity": "WARNING", "code": "ally_shut_out_risk",
             "salience": 90},
            {"severity": "WARNING", "code": "rival_strengthened",
             "salience": 70},
            {"severity": "WARNING", "code": "minor_concern", "salience": 30},
            {"severity": "INFO", "code": "context_note", "salience": 10},
        ]
        acceptance = {
            "total": 55, "band": "accept",
            "top_components": [
                {"name": "base_side_pressure", "value": 35},
                {"name": "settlement_tier_legitimacy", "value": 10},
                {"name": "war_objective_alignment", "value": 5},
            ],
            "debug_components": [
                {"name": "deal_balance", "value": 0},
                {"name": "abandoned_by_ally_acceptance_mod", "value": 0},
            ],
        }
        return build_settlement_review(
            war_id="war_e", war_label="War of the Third Coalition",
            proposer_side="attackers", accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            terms=terms, allies=allies, warnings=warnings,
            acceptance=acceptance, density=density,
            awe_tags=["tilsit_bargain_and_betrayal"],
        )

    def test_compact_density_caps_terms_at_three(self):
        review = self._ratification_payload("compact")
        terms = review["sections"]["terms"]
        assert len(terms["rows"]) == 3
        assert terms["overflow_count"] == 4

    def test_medium_density_caps_terms_at_five(self):
        review = self._ratification_payload("medium")
        terms = review["sections"]["terms"]
        assert len(terms["rows"]) == 5
        assert terms["overflow_count"] == 2

    def test_verbose_density_shows_all_rows(self):
        review = self._ratification_payload("verbose")
        terms = review["sections"]["terms"]
        assert terms["overflow_count"] == 0
        assert len(terms["rows"]) == 7

    def test_allies_section_caps_at_standing_row_cap(self):
        review = self._ratification_payload("medium")
        allies = review["sections"]["allies"]
        assert len(allies["rows"]) <= SETTLEMENT_STANDING_ROW_CAP
        assert allies["overflow_count"] >= 0

    def test_warnings_section_uses_warning_cap(self):
        review = self._ratification_payload("compact")
        warnings = review["sections"]["warnings"]
        # 1 hard stop + 2 warnings inline.
        assert len(warnings["inline"]) == 3
        assert len(warnings["overflow"]) >= 1

    def test_acceptance_top_components_capped_at_three(self):
        review = self._ratification_payload("compact")
        acceptance = review["sections"]["acceptance"]
        assert len(acceptance["top_components"]) == 3

    def test_verbose_includes_debug_components(self):
        review = self._ratification_payload("verbose")
        acceptance = review["sections"]["acceptance"]
        assert "debug_components" in acceptance

    def test_compact_strips_debug_components(self):
        review = self._ratification_payload("compact")
        acceptance = review["sections"]["acceptance"]
        assert "debug_components" not in acceptance

    def test_awe_tags_pass_through(self):
        review = self._ratification_payload("compact")
        assert "tilsit_bargain_and_betrayal" in review["awe_tags"]

    def test_unknown_density_falls_back_to_compact(self):
        review = build_settlement_review(
            war_id="w", war_label="W", proposer_side="attackers",
            accepting_side="defenders", covered_enemy_participants=[],
            terms=[], allies=[], warnings=[], acceptance=None,
            density="ridiculous",
        )
        assert review["density"] == "compact"


# ===========================================================================
# Awe set-piece tagging (spec §20.8)
# ===========================================================================


class TestAweSetPieces:
    def test_triple_forced_alignment_by_count(self):
        terms = [{"type": "forced_alliance", "from": n, "to": "France"}
                 for n in ("Austria", "Prussia", "Saxony")]
        tags = detect_awe_set_pieces(
            settlement_terms=terms, participant_reactions=[],
        )
        assert "triple_forced_alignment" in tags

    def test_triple_forced_alignment_by_threat_delta(self):
        # Two clauses each projecting +20 threat = +40 total triggers.
        terms = [
            {"type": "forced_alliance", "from": "Austria", "to": "France",
             "projected_threat_delta": 20},
            {"type": "forced_alliance", "from": "Prussia", "to": "France",
             "projected_threat_delta": 20},
        ]
        tags = detect_awe_set_pieces(
            settlement_terms=terms, participant_reactions=[],
        )
        assert "triple_forced_alignment" in tags

    def test_balance_crossing_only_with_forced_alignment(self):
        balance = {"crossed_thresholds": ["50"]}
        terms = [{"type": "forced_alliance", "from": "Austria",
                  "projected_threat_delta": 35}]
        tags = detect_awe_set_pieces(
            settlement_terms=terms, participant_reactions=[],
            balance_projection=balance,
        )
        assert "triple_forced_alignment" in tags
        assert "balance_of_europe_crossing" in tags

    def test_tilsit_bargain_and_betrayal_via_breach_and_shut_out(self):
        terms = []
        reactions = [
            {"kind": "bargain_breach_at_settlement"},
            {"kind": "ally_shut_out", "severity": "major_shut_out"},
        ]
        tags = detect_awe_set_pieces(
            settlement_terms=terms, participant_reactions=reactions,
        )
        assert "tilsit_bargain_and_betrayal" in tags

    def test_tilsit_bargain_and_betrayal_via_fulfillment_and_reward(self):
        terms = [{"type": "bargain_fulfilled"}]
        reactions = [{"kind": "ally_rewarded"}]
        tags = detect_awe_set_pieces(
            settlement_terms=terms, participant_reactions=reactions,
        )
        assert "tilsit_bargain_and_betrayal" in tags

    def test_defensive_coalition_preservation(self):
        terms = [{"type": "territory_return", "from": "France",
                  "to": "Austria"}]
        tags = detect_awe_set_pieces(
            settlement_terms=terms, participant_reactions=[],
            proposer_side="defenders",
        )
        assert "defensive_coalition_preservation" in tags

    def test_no_tags_when_nothing_extraordinary(self):
        terms = [{"type": "indemnity", "from": "Austria",
                  "to": "France", "amount": 500}]
        tags = detect_awe_set_pieces(
            settlement_terms=terms, participant_reactions=[],
        )
        assert tags == []


# ===========================================================================
# Notification rail spotlight metadata
# ===========================================================================


class TestNotificationMeta:
    def test_summary_meta_carries_route(self):
        event = _make_settlement_event()
        meta = settlement_notification_meta(event)
        assert meta["event_type"] == "settlement_summary"
        assert meta["event_family"] == SETTLEMENT_EVENT_FAMILY
        assert meta["review_target"] == SETTLEMENT_REVIEW_TARGET_ACTIVE
        assert meta["rail_spotlight"] == "yes"

    def test_digest_meta_marks_no_rail(self):
        digest = {
            "type": "settlement_digest", "war_id": "war_e", "turn": 5,
            "hidden_reaction_count": 3,
            "route": {
                "event_family": SETTLEMENT_EVENT_FAMILY,
                "review_target": SETTLEMENT_REVIEW_TARGET_ARCHIVED,
                "route_id": "settlement_digest:war_e:5",
            },
        }
        meta = settlement_notification_meta(digest)
        assert meta["rail_spotlight"] == "no"
        assert meta["review_target"] == SETTLEMENT_REVIEW_TARGET_ARCHIVED

    def test_meta_passes_through_awe_tags(self):
        event = _make_settlement_event(awe_tags=["triple_forced_alignment"])
        meta = settlement_notification_meta(event)
        assert "awe_tags" in meta
        assert "triple_forced_alignment" in meta["awe_tags"]


# ===========================================================================
# Recent settlements ledger view
# ===========================================================================


class TestRecentSettlements:
    def test_recent_settlements_picks_up_event_log(self):
        world = WorldState()
        _install_two_v_two_war(world)
        world.event_log.append(_make_settlement_event())
        rows = recent_settlement_summaries(world, "France")
        assert len(rows) == 1
        row = rows[0]
        assert row["war_id"] == "war_e"
        assert row["review_target"] == SETTLEMENT_REVIEW_TARGET_ACTIVE
        assert "headline" in row

    def test_recent_settlements_orders_newest_first(self):
        world = WorldState()
        _install_two_v_two_war(world)
        world.event_log.append(_make_settlement_event(
            war_id="war_e", turn=3,
        ))
        world.event_log.append(_make_settlement_event(
            war_id="war_e2", turn=7,
            proposer_members=["France"], accepting_members=["Prussia"],
            covered=["Prussia"],
        ))
        rows = recent_settlement_summaries(world, "France")
        assert rows[0]["war_id"] == "war_e2"

    def test_recent_settlements_respects_limit(self):
        world = WorldState()
        _install_two_v_two_war(world)
        for i in range(SETTLEMENT_LEDGER_DEFAULT_ROWS + 3):
            world.event_log.append(_make_settlement_event(
                war_id=f"war_{i}", turn=i,
            ))
        rows = recent_settlement_summaries(world, "France")
        assert len(rows) == SETTLEMENT_LEDGER_DEFAULT_ROWS

    def test_recent_settlements_filters_by_fog(self):
        world = WorldState()
        # Foreign settlement Britain has no visibility into.
        world.event_log.append(_make_settlement_event(
            war_id="far_off",
            proposer_members=["Sweden"], accepting_members=["Russia"],
            covered=["Russia"],
        ))
        rows = recent_settlement_summaries(world, "Britain")
        assert rows == []

    def test_diplomatic_ledger_includes_recent_settlements(self):
        world = WorldState()
        _install_two_v_two_war(world)
        world.event_log.append(_make_settlement_event())
        ledger = build_diplomatic_ledger(world)
        assert "recent_settlements" in ledger
        assert len(ledger["recent_settlements"]) == 1


# ===========================================================================
# Dispatch wiring (settlement events flow through pending_dispatch_events)
# ===========================================================================


class TestDispatchWiring:
    def test_dispatch_renders_settlement_summary_one_liner(self):
        world = WorldState()
        _install_two_v_two_war(world)
        # Drive the settlement reaction emission so the event lands in
        # `pending_dispatch_events`.
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        route_settlement_reactions(
            world,
            war_id="war_e",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria",
                "to": "France", "regions": [austria_region],
            }],
            resolved_pairs=[],
            applied_clauses=[{
                "type": "territory_cede", "from": "Austria",
                "to": "France", "regions": [austria_region],
            }],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        rendered = _build_diplomatic_events_section(world, "France")
        types = [r.get("type") for r in rendered]
        assert "settlement_summary" in types
        # Each settlement entry carries route_id for the §11.6 cap path.
        for entry in rendered:
            if entry.get("type") == "settlement_summary":
                assert entry.get("event_family") == "settlement"
                assert entry.get("route_id", "").startswith(
                    "settlement_summary:war_e:"
                )

    def test_dispatch_filters_out_invisible_settlement(self):
        world = WorldState()
        # Foreign settlement, player is France but has no visibility
        # into the participants.
        world.pending_dispatch_events.append(_make_settlement_event(
            war_id="far_off",
            proposer_members=["Sweden"], accepting_members=["Russia"],
            covered=["Russia"],
        ))
        rendered = _build_diplomatic_events_section(world, "Britain")
        types = [r.get("type") for r in rendered]
        assert "settlement_summary" not in types

    def test_dispatch_visible_when_proposer_is_player(self):
        world = WorldState()
        _install_two_v_two_war(world)
        world.pending_dispatch_events.append(_make_settlement_event())
        rendered = _build_diplomatic_events_section(world, "France")
        types = [r.get("type") for r in rendered]
        assert "settlement_summary" in types

    def test_dispatch_event_visible_uses_settlement_filter(self):
        world = WorldState()
        _install_two_v_two_war(world)
        event = _make_settlement_event()
        # The shared dispatch fog filter must dispatch settlement events
        # through the settlement-specific filter, not the legacy
        # `template_vars`/`fog_rule` path (which would default to
        # always-visible and leak fog).
        assert _is_dispatch_event_visible(event, world, "France")


# ===========================================================================
# Campaign log filter wiring
# ===========================================================================


class TestCampaignLogFilter:
    def test_settlement_summary_filtered_when_player_involved(self):
        world = WorldState()
        _install_two_v_two_war(world)
        events = [_make_settlement_event()]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 1

    def test_settlement_digest_filtered_when_visible(self):
        world = WorldState()
        _install_two_v_two_war(world)
        events = [{
            "type": "settlement_digest", "war_id": "war_e", "turn": 5,
            "covered_enemy_participants": ["Austria"],
            "proposer_members": ["France"],
            "accepting_members": ["Austria"],
            "hidden_reaction_count": 3,
            "route": {
                "event_family": SETTLEMENT_EVENT_FAMILY,
                "review_target": SETTLEMENT_REVIEW_TARGET_ARCHIVED,
                "route_id": "settlement_digest:war_e:5",
            },
        }]
        filtered = filter_campaign_log(events, world)
        assert len(filtered) == 1

    def test_settlement_dropped_when_player_not_involved(self):
        world = WorldState()
        events = [_make_settlement_event(
            war_id="far_off",
            proposer_members=["Sweden"], accepting_members=["Russia"],
            covered=["Russia"],
        )]
        filtered = filter_campaign_log(events, world)
        # World player_nation defaults to France; no fog visibility on
        # Sweden/Russia → drop.
        assert filtered == []


# ===========================================================================
# War status panel — contribution share rows
# ===========================================================================


class TestWarStatusContribution:
    def test_active_wars_include_contribution_share_block(self):
        world = WorldState()
        _install_two_v_two_war(world)
        result = build_active_wars(world)
        # France ↔ Austria pair: contribution rows live on the war
        # entry. Should be present (possibly empty if early-war
        # contribution data is missing) but not crash.
        for war in result["wars"]:
            assert "contribution_share" in war
            assert "contribution_overflow_count" in war
            assert isinstance(war["contribution_share"], list)

    def test_build_contribution_share_caps_top_n_with_overflow(self):
        world = WorldState()
        # 1v6 synthetic war so the overflow path engages.
        war = make_synthetic_war_instance(
            "war_big",
            attackers=["France"],
            defenders=["Austria", "Prussia", "Bavaria", "Saxony", "Russia",
                       "Sweden"],
            attacker_leader="France",
            defender_leader="Austria",
            created_turn=1, created_sequence=1,
        )
        world.war_instances["war_big"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
            world.war_start_turns[pair] = world.current_turn
            world.battle_records[pair] = []
        world.invalidate_war_instance_indexes()
        contribution = build_contribution_share_rows(world, "war_big", cap=5)
        assert len(contribution["rows"]) <= 5
        # 7 participants - 5 cap = 2 overflow.
        assert contribution["overflow_count"] >= 2

    def test_build_contribution_share_unknown_war_returns_empty(self):
        world = WorldState()
        contribution = build_contribution_share_rows(world, "no_such_war")
        assert contribution == {"rows": [], "overflow_count": 0}
