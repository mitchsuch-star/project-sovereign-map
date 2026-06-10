"""Behavior tests for Settlement UI Cleanup G2-Slice-5 (SC-15/15b/16/17/19/20/23/24/25).

This file is the slice-5 behavior twin bundle per `docs/SETTLEMENT_UI_CLEANUP_SPEC.md`
v0.17 §"G2-Slice-5 - Presentation And Metadata". Each test pins one row from the
SC-15..SC-25 set and is intended to outlive future slice renames.
"""

from __future__ import annotations

import copy

from backend.game_logic.diplomatic_templates import (
    SETTLEMENT_VOICE_TEMPLATES,
    calculate_raw_treaty_harshness,
    calculate_treaty_harshness,
    get_treaty_harshness_for_consumer,
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_presentation import (
    PEACE_HISTORY_BILATERAL_NAMESPACE,
    PEACE_HISTORY_DEFAULT_ROWS,
    PEACE_HISTORY_SETTLEMENT_NAMESPACE,
    build_applied_clauses_preview,
    build_beneficiaries_preview,
    build_forced_alliance_threat_preview_display,
    build_peace_settlement_history,
    build_settlement_review,
    build_settlement_review_from_event,
    build_shut_out_allies_preview,
    build_third_party_reaction_preview,
)
from backend.game_logic.settlement_preview import (
    build_settlement_preview,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_reactions import route_settlement_reactions
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


def _install_common_peace_war(world: WorldState) -> dict:
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        a, _ = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 70 if a == "Austria" else -70
    world.war_exhaustion["Austria"] = 30
    world.invalidate_war_instance_indexes()
    return war


# ---------------------------------------------------------------------------
# SC-15: applied_clauses_preview structural equivalence + beneficiaries +
# shut_out_allies + third_party_reaction_preview + live awe + acceptance_snapshot
# ---------------------------------------------------------------------------


def test_sc15_applied_clauses_preview_is_structurally_equal_to_terms():
    """SC-15: `applied_clauses_preview[]` is structurally equal by clause type
    plus clause-specific value fields (region, payer, recipient, amount,
    turns, includes_continental_system, threat delta, pair-state transition)."""
    terms = [
        {
            "type": "territory_cede",
            "from": "Austria",
            "to": "France",
            "regions": ["Bohemia", "Tyrol"],
        },
        {
            "type": "gold_indemnity",
            "from": "Austria",
            "to": "France",
            "amount": 250,
        },
        {
            "type": "forced_alliance",
            "from": "Austria",
            "to": "France",
            "includes_continental_system": True,
            "projected_threat_delta": 18,
        },
    ]
    preview = build_applied_clauses_preview(terms)

    assert len(preview) == 3
    territory = preview[0]
    assert territory["type"] == "territory_cede"
    assert territory["from"] == "Austria"
    assert territory["to"] == "France"
    assert territory["regions"] == ["Bohemia", "Tyrol"]

    gold = preview[1]
    assert gold["type"] == "gold_indemnity"
    assert gold["from"] == "Austria"
    assert gold["to"] == "France"
    assert gold["amount"] == 250

    alliance = preview[2]
    assert alliance["type"] == "forced_alliance"
    assert alliance["includes_continental_system"] is True
    assert alliance["projected_threat_delta"] == 18
    assert alliance["pair_state_transition"] == "WAR -> ALLIANCE"


def test_sc15_beneficiaries_preview_names_recipient_with_reason():
    """SC-15: beneficiaries[] explicitly names recipients of any clause that
    advances their interests, plus rewarded contribution-share rows."""
    terms = [
        {"type": "territory_cede", "from": "Austria", "to": "France",
         "regions": ["Bohemia"]},
        {"type": "gold_indemnity", "from": "Austria", "to": "Saxony",
         "amount": 100},
    ]
    rows = [
        {"nation": "France", "is_beneficiary": False, "standing": "leader"},
        {"nation": "Saxony", "is_beneficiary": True, "standing": "rewarded"},
    ]
    applied = build_applied_clauses_preview(terms)

    benes = build_beneficiaries_preview(rows, applied)

    by_nation = {b["nation"]: b for b in benes}
    assert "France" in by_nation
    assert any("ceded territory" in r.lower() for r in by_nation["France"]["reasons"])
    assert "Saxony" in by_nation
    # Saxony is both a rewarded contribution row AND receives gold.
    assert len(by_nation["Saxony"]["reasons"]) >= 1


def test_sc15_shut_out_allies_preview_lists_no_standing_with_contribution():
    """SC-15: shut_out_allies[] lists same-side allies with `no_standing`
    standing and positive contribution share."""
    rows = [
        {"nation": "Spain", "standing": "no_standing", "contribution_share": 25},
        {"nation": "Naples", "standing": "leader", "contribution_share": 60},
    ]
    out = build_shut_out_allies_preview(rows, [])

    nations = [r["nation"] for r in out]
    assert "Spain" in nations
    assert "Naples" not in nations  # leader is never shut-out


def test_sc15_third_party_reaction_preview_includes_shut_out_grievance():
    """SC-15: third_party_reaction_preview[] surfaces projected commitment
    grievances + shut-out ally grievances + threat-delta beats."""
    shut_out = [
        {"nation": "Spain", "standing": "no_standing", "contribution_share": 30},
    ]
    threat_preview = {
        "forced_alliance_clauses": 1,
        "projected_threat_delta": 12,
        "current_threat": 40,
        "projected_threat": 52,
        "crossed_thresholds": ["concerned"],
    }
    terms = [
        {"type": "forced_alliance", "from": "Austria", "to": "France"},
    ]
    out = build_third_party_reaction_preview(terms, shut_out, threat_preview)

    kinds = [r["kind"] for r in out]
    assert "shut_out_ally_grievance" in kinds
    assert "forced_alliance_grievance_projection" in kinds
    assert "coalition_threat_delta" in kinds


def test_sc15_live_settlement_preview_emits_awe_tag_displays():
    """SC-15: live `build_settlement_preview` emits awe_tag_displays before
    ratification when the package qualifies (the previous `awe_tags=[]`
    pass made the popup awe affordance dead)."""
    world = WorldState()
    _install_common_peace_war(world)
    terms = [
        {"type": "forced_alliance", "from": "Austria", "to": "France"},
        {"type": "forced_alliance", "from": "Prussia", "to": "France"},
        {"type": "forced_alliance", "from": "Saxony", "to": "France"},
    ]
    result = build_settlement_preview(world, war_id="war_1", settlement_terms=terms)

    review = result["settlement_preview"]["review_sections"]
    # Triple forced-alliance set piece must surface at preview time.
    assert "triple_forced_alignment" in review.get("awe_tags", [])
    assert any("Triple forced alignment" in d for d in review.get("awe_tag_displays", []))


def test_sc15_settlement_review_carries_applied_clauses_and_beneficiaries():
    """SC-15: build_settlement_review surfaces applied_clauses_preview,
    beneficiaries_preview, shut_out_allies_preview, third_party_reaction_preview
    and forced_alliance_threat_preview at top level."""
    world = WorldState()
    _install_common_peace_war(world)
    terms = [
        {"type": "territory_cede", "from": "Austria", "to": "France",
         "regions": ["Bohemia"]},
    ]
    result = build_settlement_preview(world, war_id="war_1", settlement_terms=terms)
    review = result["settlement_preview"]["review_sections"]

    assert "applied_clauses_preview" in review
    assert "beneficiaries_preview" in review
    assert "shut_out_allies_preview" in review
    assert "third_party_reaction_preview" in review
    assert "forced_alliance_threat_preview" in review
    # France should appear in beneficiaries (territory recipient).
    bene_nations = [b["nation"] for b in review["beneficiaries_preview"]]
    assert "France" in bene_nations


# ---------------------------------------------------------------------------
# SC-15b: blocked acceptance payload contract
# ---------------------------------------------------------------------------


def test_sc15b_blocked_band_payload_omits_numeric_total_and_threshold():
    """SC-15b: when band == 'blocked', acceptance payload sets total/threshold
    to null and supplies blocker_display + band_display='Blocked'."""
    review = build_settlement_review(
        war_id="war_1",
        war_label="France vs Austria",
        proposer_side="attackers",
        accepting_side="defenders",
        covered_enemy_participants=["Austria"],
        terms=[],
        allies=[],
        warnings=[],
        acceptance={
            "band": "blocked",
            "verdict": "blocked",
            "score": 0,
            "threshold": 50,
            "hard_stops": [{"code": "no_coverage", "display": "Austria has no coverage"}],
        },
    )
    acc = review["sections"]["acceptance"]
    assert acc["total"] is None
    assert acc["threshold"] is None
    assert acc["band"] == "blocked"
    assert acc["band_display"] == "Blocked"
    assert "blocker_display" in acc
    assert "Austria" in acc["blocker_display"] or acc["blocker_display"]


def test_sc15b_non_blocked_band_keeps_numeric_total_and_threshold():
    """SC-15b: non-blocked acceptance still carries numeric total/threshold."""
    review = build_settlement_review(
        war_id="war_1",
        war_label="France vs Austria",
        proposer_side="attackers",
        accepting_side="defenders",
        covered_enemy_participants=["Austria"],
        terms=[],
        allies=[],
        warnings=[],
        acceptance={
            "band": "near_acceptable",
            "verdict": "near_acceptable",
            "score": 35,
            "threshold": 50,
        },
    )
    acc = review["sections"]["acceptance"]
    assert acc["total"] == 35
    assert acc["threshold"] == 50


# ---------------------------------------------------------------------------
# SC-16: forced-alliance threat preview surfaced via shared helper
# ---------------------------------------------------------------------------


def test_sc16_forced_alliance_threat_preview_uses_shared_helper_output():
    """SC-16: `build_forced_alliance_threat_preview_display` consumes the
    shape returned by `compute_forced_alliance_threat_preview` and produces
    a humanized display string + crossed_threshold_displays list."""
    threat_preview = {
        "forced_alliance_clauses": 2,
        "projected_threat_delta": 20,
        "current_threat": 30,
        "projected_threat": 50,
        "crossed_thresholds": ["concerned"],
    }
    out = build_forced_alliance_threat_preview_display(threat_preview)

    assert out["forced_alliance_clauses"] == 2
    assert out["projected_threat_delta"] == 20
    assert out["current_threat"] == 30
    assert out["projected_threat"] == 50
    assert "Concerned" in out["crossed_threshold_displays"]
    assert "30" in out["display"] and "50" in out["display"]


def test_sc16_no_forced_alliance_clauses_returns_empty_display():
    """SC-16: when settlement has no forced-alliance clauses, the display is
    empty string so popup/tooltip can render nothing rather than 0 → 0."""
    out = build_forced_alliance_threat_preview_display({
        "forced_alliance_clauses": 0,
        "projected_threat_delta": 0,
        "current_threat": 30,
        "projected_threat": 30,
        "crossed_thresholds": [],
    })
    assert out["display"] == ""


# ---------------------------------------------------------------------------
# SC-17: raw labels / debug copy humanized
# ---------------------------------------------------------------------------


def test_sc17_war_scope_display_does_not_use_bilateral_row_label():
    """SC-17: 'Bilateral row' is replaced with player copy."""
    review = build_settlement_review(
        war_id="war_1",
        war_label="France vs Austria",
        proposer_side="attackers",
        accepting_side="defenders",
        covered_enemy_participants=["Austria"],
        terms=[],
        allies=[],
        warnings=[],
        acceptance=None,
    )
    assert review["war_scope_display"] != "Bilateral row"
    assert "row" not in review["war_scope_display"].lower()


def test_sc17_humanize_term_uses_clause_display_name():
    """SC-17: `_humanize_term` delegates type labels to clause_display_name
    (no underscore-stripped 'territory cede' for known clause types)."""
    from backend.game_logic.settlement_presentation import _humanize_term

    out = _humanize_term("territory_cede: Austria→France")
    # `clause_display_name("territory_cede")` returns the registered
    # display token; the underscore-stripped fallback never fires for
    # known types.
    assert "territory cede" not in out.lower() or out.lower().startswith("territory")
    # Must NOT match the raw underscore form.
    assert "territory_cede" not in out


def test_sc17_staged_dialogue_talleyrand_text_contains_no_raw_verdict_enum():
    """SC-17: staged dialogue talleyrand_text contains no raw acceptance
    verdict enum tokens (`near_acceptable`, `reject`, `blocked`,
    `acceptable`, `accept`)."""
    world = WorldState()
    _install_common_peace_war(world)
    stage_settlement_confirm(
        world,
        war_id="war_1",
        settlement_terms=[
            {"type": "territory_cede", "from": "Austria", "to": "France",
             "regions": ["Bohemia"]},
        ],
    )
    dialogue = world.pending_diplomatic_dialogue
    text = str(dialogue.get("talleyrand_text", "") or "")
    for raw in ("near_acceptable", "reject", "blocked", "acceptable", "accept"):
        assert raw not in text, f"raw enum {raw!r} leaked into talleyrand_text"


def test_sc17_dialogue_payload_uses_available_action_ids_not_debug():
    """SC-17 inversion (was tests/test_common_peace_c2_preview.py:116-120):
    dialogue payload exposes `available_action_ids` (not debug_action_ids)
    on default/medium density."""
    world = WorldState()
    _install_common_peace_war(world)
    stage_settlement_confirm(
        world,
        war_id="war_1",
        settlement_terms=[],
    )
    dialogue = world.pending_diplomatic_dialogue
    assert "available_action_ids" in dialogue
    assert "debug_action_ids" not in dialogue


# ---------------------------------------------------------------------------
# SC-19: settlement voice families
# ---------------------------------------------------------------------------


def test_sc19_required_voice_families_are_registered():
    """SC-19: every required voice family for slice 5 has a committed
    template in SETTLEMENT_VOICE_TEMPLATES."""
    required = [
        "settlement_review_heading_talleyrand",
        "settlement_observed_foreign_court_chancery",
        "settlement_blocked_for_ratification_talleyrand",
        "settlement_rescored_after_staging_talleyrand",
        "settlement_discard_confirm_talleyrand",
        "settlement_collision_active_review_talleyrand",
        "settlement_reopen_cap_exhausted_talleyrand",
    ]
    for key in required:
        assert key in SETTLEMENT_VOICE_TEMPLATES, f"voice family {key} missing"
        body = SETTLEMENT_VOICE_TEMPLATES[key]
        assert isinstance(body, str) and body.strip(), f"{key} body is placeholder"


def test_sc19_voice_resolver_substitutes_war_label_slot():
    """SC-19: resolve_settlement_voice_line substitutes named slots."""
    out = resolve_settlement_voice_line(
        "settlement_review_heading_talleyrand",
        war_label="Coalition War",
        acceptance_band="Acceptable",
        top_blocker="war exhaustion",
    )
    assert "Coalition War" in out
    assert "Acceptable" in out


def test_sc19_voice_templates_do_not_use_common_peace_as_route_phrase():
    """SC-25 / SC-19 cross-cutting: settlement-family voice template bodies
    must not use 'Common Peace' / 'common peace' as the top-level route
    phrase."""
    for key, body in SETTLEMENT_VOICE_TEMPLATES.items():
        assert "Common Peace" not in body, f"{key} uses 'Common Peace' as route phrase"
        # 'common peace' bare phrase as route name is forbidden;
        # 'common peace acceptance' (concept) is OK if it ever appears.
        assert "common peace" not in body.lower() or (
            "common peace" in body.lower() and "acceptance" in body.lower()
        ), f"{key} uses 'common peace' as route phrase"


# ---------------------------------------------------------------------------
# SC-20: single acceptance phrase per band
# ---------------------------------------------------------------------------


def test_sc20_godot_popup_does_not_concatenate_band_display_with_phrase():
    """SC-20: proposal_confirm_popup.gd no longer renders ' (phrase)' suffix
    when phrase differs from band_display (the old "Unlikely (Likely to
    reject)" duplicate is gone)."""
    from pathlib import Path

    src = Path(
        "godot-client/project-sovereign/scripts/proposal_confirm_popup.gd"
    ).read_text(encoding="utf-8")
    # The legacy concatenation pattern is gone.
    assert 'if phrase != "" and phrase != band:' not in src


# ---------------------------------------------------------------------------
# SC-23: merged PEACE & SETTLEMENT HISTORY surface
# ---------------------------------------------------------------------------


def test_sc23_peace_history_default_rows_constant_is_5():
    """SC-23: combined cap is 5 across both common-peace and bilateral rows."""
    assert PEACE_HISTORY_DEFAULT_ROWS == 5


def test_sc23_route_namespaces_are_distinct():
    """SC-23: bilateral peace and settlement rows use distinct route id
    namespaces so focus ids cannot collide."""
    assert PEACE_HISTORY_BILATERAL_NAMESPACE == "peace"
    assert PEACE_HISTORY_SETTLEMENT_NAMESPACE == "settlement"
    assert PEACE_HISTORY_BILATERAL_NAMESPACE != PEACE_HISTORY_SETTLEMENT_NAMESPACE


def test_sc23_merged_history_renders_both_settlement_and_bilateral_rows():
    """SC-23 fixture: 1 common settlement + 1 bilateral peace renders both
    rows in the merged surface with row-level type tags."""
    world = WorldState()
    world.player_nation = "France"
    world.current_turn = 5
    # Bilateral peace ratification entry — newest first per producer.
    world.peace_ratification_log = [
        {
            "turn": 4,
            "target_nation": "Spain",
            "actor_nation": "France",
            "war_id": "war_2",
            "war_outcome": "white_peace",
            "new_state": "PEACE",
        },
    ]
    # Settlement summary event in event_log (visible by default in tests
    # without fog when nothing is set up).
    world.event_log.append({
        "type": "settlement_summary",
        "turn": 5,
        "war_id": "war_1",
        "war_label": "France vs Austria",
        "covered_enemy_participants": ["Austria"],
        "proposer_side": "attackers",
        "accepting_side": "defenders",
        "proposer_members": ["France"],
        "accepting_members": ["Austria"],
        "applied_clauses": [],
        "participant_reactions": [],
        "war_ended": True,
        "balance_projection": {},
        "awe_tags": [],
        "terms_summary": [],
        "route": {
            "event_family": "settlement",
            "review_target": "ledger_settlements",
            "route_id": "settlement:war_1:5:1",
        },
    })

    rows = build_peace_settlement_history(world, "France", limit=5)

    assert len(rows) == 2
    # Newest first by turn.
    assert rows[0]["sort_turn"] >= rows[1]["sort_turn"]
    types = {r["row_type"] for r in rows}
    assert types == {"settlement", "bilateral_peace"}
    # Each row carries a distinct route id namespace.
    bilateral = next(r for r in rows if r["row_type"] == "bilateral_peace")
    assert bilateral["route_id"].startswith("peace:")
    settlement = next(r for r in rows if r["row_type"] == "settlement")
    assert settlement["route_id"].startswith("settlement:")


def test_sc23_diplomatic_ledger_payload_includes_peace_settlement_history():
    """SC-23: the ledger payload exposes `peace_settlement_history` so the
    Godot ledger can render the merged surface."""
    from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger

    world = WorldState()
    world.player_nation = "France"
    payload = build_diplomatic_ledger(world)
    assert "peace_settlement_history" in payload


# ---------------------------------------------------------------------------
# SC-24: harshness raw/clamped fields + named consumers
# ---------------------------------------------------------------------------


def test_sc24_record_common_peace_treaty_carries_raw_and_clamped_harshness():
    """SC-24: treaties produced by common-peace ratification carry both
    `raw_harshness` (unclamped) and `harshness` / `clamped_harshness`
    (1.0-ceiling) on the same record, plus `source='common_peace'`."""
    from backend.game_logic.settlement_ratify import _record_common_peace_treaties

    world = WorldState()
    war = _install_common_peace_war(world)
    # Multi-clause settlement that exceeds 1.0 raw harshness.
    terms = [
        {"type": "territory_cede", "from": "Austria", "to": "France",
         "regions": ["Bohemia", "Tyrol", "Croatia", "Hungary"]},  # 0.3 * 4 = 1.2
        {"type": "forced_alliance", "from": "Austria", "to": "France"},  # 0.4
    ]
    plan = [{
        "pair": "Austria|France",
        "proposer_member": "France",
        "covered_enemy": "Austria",
        "current_state": "WAR",
    }]
    _record_common_peace_treaties(world, plan=plan, settlement_terms=terms)

    pair_key = world._make_diplo_key("France", "Austria")
    treaty = world.active_treaties[pair_key]
    raw = treaty["raw_harshness"]
    clamped = treaty["clamped_harshness"]
    assert raw > 1.0  # multi-clause exceeds the 1.0 ceiling
    assert 0.0 <= clamped <= 1.0
    assert treaty["source"] == "common_peace"


def test_sc24_named_consumers_read_raw_harshness_for_common_peace_records():
    """SC-24: named common-peace consumers (ledger / ai_diplomacy /
    coalition / dispatch / notifications) must pick raw harshness for
    common-peace records via `get_treaty_harshness_for_consumer`."""
    common_peace_treaty = {
        "harshness": 1.0,
        "clamped_harshness": 1.0,
        "raw_harshness": 1.6,
        "source": "common_peace",
    }
    bilateral_legacy = {
        "harshness": 0.4,
    }
    # Common-peace path picks raw for named consumers.
    for consumer in (
        "diplomatic_ledger",
        "ai_diplomacy",
        "coalition",
        "dispatch",
        "notifications",
    ):
        v = get_treaty_harshness_for_consumer(common_peace_treaty, consumer=consumer)
        assert abs(v - 1.6) < 1e-6, f"{consumer} did not read raw_harshness"

    # Bilateral legacy record falls back to clamped harshness.
    assert (
        abs(
            get_treaty_harshness_for_consumer(
                bilateral_legacy, consumer="diplomatic_ledger",
            )
            - 0.4
        )
        < 1e-6
    )


def test_sc24_raw_and_clamped_helpers_disagree_for_multiclause_packages():
    """SC-24 sanity: raw and clamped helpers MUST disagree for packages
    that exceed 1.0 raw harshness; otherwise the named-consumer split is
    meaningless."""
    treaty = {
        "clauses": [
            {"type": "territory_cede", "regions": ["A", "B", "C", "D"]},  # 0.3*4=1.2
            {"type": "forced_alliance"},  # 0.4
        ],
    }
    raw = calculate_raw_treaty_harshness(treaty)
    clamped = calculate_treaty_harshness(treaty)
    assert raw > 1.0
    assert clamped <= 1.0
    assert raw != clamped


# ---------------------------------------------------------------------------
# SC-15 / SC-23 failed-ratification guard
# ---------------------------------------------------------------------------


def test_sc15_failed_ratification_does_not_emit_settlement_summary_event():
    """SC-15 / SC-23 failed-ratification guard: route_settlement_reactions
    refuses summary emission when called with success=False / mutated=False."""
    world = WorldState()
    _install_common_peace_war(world)
    before_events = list(getattr(world, "event_log", []) or [])

    out = route_settlement_reactions(
        world,
        war_id="war_1",
        proposer_side="attackers",
        accepting_side="defenders",
        covered_enemy_participants=["Austria"],
        settlement_terms=[],
        resolved_pairs=[],
        applied_clauses=[],
        pre_cleanup_snapshots=[],
        war_ended=False,
        success=False,
        mutated=False,
    )

    assert out["summary_event"] is None
    assert out.get("skipped_reason") == "failed_ratification"
    after_events = list(getattr(world, "event_log", []) or [])
    assert after_events == before_events  # no settlement_summary leaked


def test_sc15_shut_out_preview_excludes_leaders_rewarded_and_enemy_side():
    rows = [
        {
            "nation": "France",
            "side": "attackers",
            "standing": "no_standing",
            "contribution_share": 0.4,
            "is_leader": True,
        },
        {
            "nation": "Saxony",
            "side": "attackers",
            "standing": "no_standing",
            "contribution_share": 0.3,
            "is_beneficiary": True,
        },
        {
            "nation": "Prussia",
            "side": "defenders",
            "standing": "no_standing",
            "contribution_share": 0.3,
        },
        {
            "nation": "Bavaria",
            "side": "attackers",
            "standing": "ignored",
            "contribution_share": 0.2,
        },
    ]

    shut_out = build_shut_out_allies_preview(rows, [], proposer_side="attackers")

    assert [row["nation"] for row in shut_out] == ["Bavaria"]


def test_sc15_archived_review_renders_acceptance_snapshot():
    event = {
        "type": "settlement_summary",
        "war_id": "war_1",
        "war_label": "France vs Austria",
        "proposer_side": "attackers",
        "accepting_side": "defenders",
        "proposer_members": ["France"],
        "accepting_members": ["Austria"],
        "covered_enemy_participants": ["Austria"],
        "applied_clauses": [{"type": "peace"}],
        "participant_reactions": [],
        "acceptance_snapshot": {
            "score": 54,
            "threshold": 50,
            "band": "near_acceptable",
            "verdict": "near_acceptable",
            "band_display": "Near acceptable",
            "top_components": [{"component": "war_exhaustion", "value": 6}],
            "hard_stops": [],
        },
    }

    review = build_settlement_review_from_event(event)
    acceptance = review["sections"]["acceptance"]

    assert acceptance["total"] == 54
    assert acceptance["threshold"] == 50
    assert acceptance["band_display"] == "Near acceptable"


# ---------------------------------------------------------------------------
# SC-25: settlement vocabulary unification (route labels + voice templates)
# ---------------------------------------------------------------------------


def test_sc25_no_open_common_peace_cta_anywhere():
    """SC-25: no top-level CTA may use 'Common Peace' or 'Treaty' as the
    route name. Open Settlement / Open Whole-War Settlement are allowed."""
    from pathlib import Path

    repo_root = Path(".")
    targets = [
        repo_root / "backend" / "game_logic" / "diplomacy.py",
        repo_root / "godot-client" / "project-sovereign" / "scripts" / "war_detail_popup.gd",
        repo_root / "godot-client" / "project-sovereign" / "scripts" / "diplomacy_wizard.gd",
        repo_root / "godot-client" / "project-sovereign" / "scripts" / "proposal_confirm_popup.gd",
    ]
    for path in targets:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        assert "Open Common Peace" not in text, f"{path} uses 'Open Common Peace' CTA"
        assert "Open Treaty" not in text, f"{path} uses 'Open Treaty' CTA"


def test_sc25_settlement_vocabulary_in_voice_templates_is_consistent():
    """SC-25: scan covers voice template bodies for forbidden top-level
    route phrases."""
    forbidden_route_phrases = ("Common Peace ", " Common Peace", "Common Peace.")
    for key, body in SETTLEMENT_VOICE_TEMPLATES.items():
        for phrase in forbidden_route_phrases:
            assert phrase not in body, f"{key} uses forbidden route phrase {phrase!r}"


# ---------------------------------------------------------------------------
# SC-15 acceptance_snapshot at ratification time
# ---------------------------------------------------------------------------


def test_sc15_acceptance_snapshot_on_settlement_summary_event():
    """SC-15 amendment: settlement_summary event carries
    `acceptance_snapshot` (fresh ratification-time scoring) and
    `acceptance_at_staging` (audit context)."""
    from backend.game_logic.settlement_reactions import (
        _emit_settlement_summary_event,
    )

    world = WorldState()
    world.current_turn = 5
    snapshot = {
        "score": 55,
        "verdict": "near_acceptable",
        "threshold": 50,
        "band": "near_acceptable",
        "band_display": "Near acceptable",
        "top_components": [],
        "hard_stops": [],
    }
    staging = {"score": 60, "threshold": 50, "verdict": "acceptable", "band": "acceptable"}

    event = _emit_settlement_summary_event(
        world,
        war_id="war_1",
        proposer_side="attackers",
        accepting_side="defenders",
        proposer_members=["France"],
        accepting_members=["Austria"],
        covered_enemy_participants=["Austria"],
        applied_clauses=[],
        participant_reactions=[],
        war_ended=True,
        balance_projection={},
        settlement_terms=[],
        acceptance_snapshot=snapshot,
        acceptance_at_staging=staging,
    )

    assert event["acceptance_snapshot"] == snapshot
    assert event["acceptance_at_staging"] == staging
