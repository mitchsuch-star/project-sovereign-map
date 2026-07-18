"""Settlement Guided Terms — GT-Slice-3 behavior tests (Godot per-court UI).

`docs/SETTLEMENT_GUIDED_TERMS_SPEC.md` v0.2 §9 GT-Slice-3: the Godot
per-court demand UI (inline `Add demand` expansion, treasury line, per-row
Remove + magnitude controls, routed through
`send_dialogue_response_with_params`), the re-homed **REFRONT-9** focused
component breakdown (re-front spec §14 / OQ-5 / GT-A4 — a PROPOSE row
click focuses the court via the presentation-only `settlement_focus_court`
and the expanded row renders the FULL 10-component table incl.
`concession_credit`), **UX-2** (REVIEW is a frozen staged-decision
surface: server rows carry no dial/holdout affordances outside PROPOSE;
the popup renders a distinct REVIEW branch), **UX-5** (a ScrollContainer
wraps the per-court table), and the D4-lesson **HTTP-boundary test**
posting the exact Godot `action_params` shape for `settlement_demand_add`
through `/respond_to_diplomatic_dialogue` (executor-direct shapes do not
count).

Fixture idioms mirror `tests/test_settlement_guided_terms_slice1.py`; the
REFRONT-9 and HTTP tests run the REAL scorer (the breakdown is the
scorer's own component table).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from backend.game_logic.settlement_preview import (
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

_SCORER_PATH = "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance"

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_SCRIPTS = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
GODOT_SCENES = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes"

# The ten acceptance components of the live scorer (settlement_scoring.py
# step 13) — REFRONT-9's completion names the full table incl.
# concession_credit.
_TEN_COMPONENTS = {
    "base_side_pressure",
    "settlement_tier_legitimacy",
    "term_harshness_penalty",
    "leader_own_losses",
    "burdened_participant_penalty",
    "projected_hegemony_mod",
    "war_objective_alignment",
    "concession_credit",
    "war_exhaustion",
    "abandoned_by_ally_acceptance_mod",
    # NA-3 §7 rider (a) — July 17, 2026: the per-court agenda term joined
    # the scorer (0 on agenda-less fixtures; the name is now historical).
    "agenda_settlement_mod",
}


# ===========================================================================
# Helpers (slice-1 idioms)
# ===========================================================================


def _set_war_score(world: WorldState, frm: str, to: str, score: int) -> None:
    key = world._make_diplo_key(frm, to)
    world.diplomatic_states[key] = "WAR"
    if sorted([frm, to])[0] == frm:
        world.war_scores[key] = int(score)
    else:
        world.war_scores[key] = -int(score)


def _three_court_world(*, prussia: int = 70, britain: int = -70, austria: int = 0):
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_gt",
        attackers=["France"],
        defenders=["Britain", "Prussia", "Austria"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances["war_gt"] = inst
    _set_war_score(world, "France", "Prussia", prussia)
    _set_war_score(world, "France", "Britain", britain)
    _set_war_score(world, "France", "Austria", austria)
    world.invalidate_war_instance_indexes()
    return world, inst


def _make_scorer(score_by_leader: dict, default: int = 60):
    def _side_effect(world=None, *, accepting_leader=None, **kwargs):
        score = score_by_leader.get(accepting_leader, default)
        verdict = "accept" if (score or 0) >= 50 else (
            "near_acceptable" if (score or 0) >= 35 else "reject"
        )
        return {
            "score": score,
            "verdict": verdict,
            "components": {},
            "component_debug": {},
            "feedback": [],
            "hard_stops": [],
            "accept_threshold": 50,
            "near_acceptable_threshold": 35,
            "side_pressure_score": 30,
            "raw_total": score if score is not None else 0,
            "raw_total_harshness": 0.0,
            "direct_scores": {},
            "direct_score_sources": {},
        }

    return _side_effect


def _stage_propose_real_scorer(world, *, terms=None, covered=None):
    """Stage a PROPOSE settlement_confirm with the REAL scorer — the
    component breakdown under test is the scorer's own component table."""
    covered = covered or ["Britain", "Prussia", "Austria"]
    staged = stage_settlement_confirm(
        world,
        war_id="war_gt",
        actor_nation="France",
        settlement_terms=terms,
        covered_enemy_participants=covered,
        selected_target_nation=covered[-1],
        caller_kind="player_editor",
        dialogue_mode="PROPOSE",
    )
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


# ===========================================================================
# REFRONT-9 — the focused-court full component breakdown (re-homed test)
# ===========================================================================


def test_tier3_focused_court_expands_full_component_breakdown():
    """REFRONT-9 (re-front spec §14, re-owned by Guided Terms GT-A4 /
    OQ-5): every scoreable PROPOSE row carries the FULL 10-component
    breakdown (incl. `concession_credit`) ready for the expanded-row
    render, a row click focuses the court through the presentation-only
    `settlement_focus_court` round trip, and the Godot popup renders the
    breakdown for the focused row."""
    world, _ = _three_court_world()
    dialogue = _stage_propose_real_scorer(world, terms=[{"type": "peace"}])
    rows = {r["nation"]: r for r in dialogue["per_court_acceptance"]}
    for nation in ("Britain", "Prussia", "Austria"):
        breakdown = rows[nation]["component_breakdown"]
        assert {entry["component"] for entry in breakdown} == _TEN_COMPONENTS
        for entry in breakdown:
            assert isinstance(entry["value"], int)  # Golden Rule #2
            assert entry["component_display"]
            assert entry["value_display"] in (f"{entry['value']:+d}",)
        # Ordered by absolute magnitude descending, name tie-break
        # (deterministic — Golden Rule #6).
        magnitudes = [
            (-abs(e["value"]), e["component"]) for e in breakdown
        ]
        assert magnitudes == sorted(magnitudes)

    # The focus trigger: presentation-only round trip sets `focused_court`
    # on the re-mounted dialogue; terms and scores are untouched.
    result = handle_settlement_dialogue_action(
        world,
        action="settlement_focus_court",
        dialogue=dialogue,
        action_params={"nation": "Prussia"},
    )
    assert result.get("success"), result
    assert result.get("focused_court") == "Prussia"
    focused_dialogue = result["diplomatic_dialogue"]
    assert focused_dialogue.get("focused_court") == "Prussia"
    assert focused_dialogue["settlement_terms"] == dialogue["settlement_terms"]
    focused_rows = {
        r["nation"]: r for r in focused_dialogue["per_court_acceptance"]
    }
    assert {
        entry["component"]
        for entry in focused_rows["Prussia"]["component_breakdown"]
    } == _TEN_COMPONENTS

    # The Godot popup renders the breakdown on the focused row: the court
    # name is the focus url and the expanded state reads
    # `component_breakdown` (source-level pin; the parse harness covers
    # syntax).
    popup = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
    assert "_build_focused_component_breakdown" in popup
    assert "component_breakdown" in popup
    assert "[url=focus:" in popup
    assert '"settlement_focus_court"' in popup
    assert "focused_court" in popup


def test_hard_stop_row_carries_empty_component_breakdown():
    """A hard-stopped court has no score pass — its row exposes an empty
    breakdown (nothing to expand; the row's authoring is already disabled
    per §3.3)."""
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_gt",
        attackers=["France"],
        defenders=["Britain", "Prussia", "Austria", "Russia"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances["war_gt"] = inst
    _set_war_score(world, "France", "Prussia", 70)
    _set_war_score(world, "France", "Britain", -70)
    _set_war_score(world, "France", "Austria", 0)
    world.invalidate_war_instance_indexes()
    dialogue = _stage_propose_real_scorer(
        world, terms=[{"type": "peace"}],
        covered=["Britain", "Prussia", "Austria", "Russia"],
    )
    rows = {r["nation"]: r for r in dialogue["per_court_acceptance"]}
    assert rows["Russia"]["total"] is None
    assert rows["Russia"]["component_breakdown"] == []
    # Live rows still carry the full table alongside the hard stop.
    assert rows["Prussia"]["component_breakdown"]


# ===========================================================================
# UX-2 — REVIEW is a frozen staged-decision surface
# ===========================================================================


def test_review_mode_rows_expose_no_dial_or_holdout_affordances():
    """UX-2 server half: outside PROPOSE the per-court rows carry NO
    dial/holdout affordances — REVIEW freezes the terms; the route back to
    shaping is the blocked rail's `Return to terms`.

    G4F-19 note: the package carries a material clause — a bare [peace]
    package is now a WHITE PEACE, which ratifies past the per-court gate
    by design and would not stage the blocked rail this test pins."""
    world, _ = _three_court_world()
    scorer = _make_scorer({"Austria": 60, "Britain": 60, "Prussia": 20})
    with patch(_SCORER_PATH, side_effect=scorer):
        staged = stage_settlement_confirm(
            world,
            war_id="war_gt",
            actor_nation="France",
            settlement_terms=[
                {"type": "peace"},
                {"type": "gold_indemnity", "from": "Prussia", "to": "France",
                 "amount": 100},
            ],
            covered_enemy_participants=["Britain", "Prussia", "Austria"],
            selected_target_nation="Austria",
            caller_kind="player_editor",
            dialogue_mode="REVIEW",
        )
    assert staged.get("success"), staged
    dialogue = staged["diplomatic_dialogue"]
    assert dialogue["dialogue_mode"] == "REVIEW"
    for row in dialogue["per_court_acceptance"]:
        assert row["dial_actions"] == [], row["nation"]
        assert row["holdout_actions"] == [], row["nation"]
    # The holdout is still flagged (the REVIEW banner promotes it), and the
    # blocked rail offers the route back to the authoring surface.
    assert "Prussia" in dialogue["overall_acceptance"]["holdout_courts"]
    assert "return_to_settlement_terms" in dialogue["available_action_ids"]


def test_godot_popup_has_review_staged_decision_render_branch():
    """UX-2 client half (source pins): the popup branches on
    `dialogue_mode` — REVIEW renders the staged-decision banner with
    promoted blockers, and the tier-2 affordance buttons are gated to
    PROPOSE at the render layer too."""
    popup = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
    assert "dialogue_mode" in popup
    assert "STAGED FOR REVIEW" in popup
    assert "Holding out:" in popup
    # Authoring affordances render only on the PROPOSE authoring surface.
    assert 'authoring_surface = (dialogue_mode == "PROPOSE")' in popup
    # The tier-2 button rail is gated the same way.
    gate = 'if str(data.get("dialogue_mode", "REVIEW")) != "PROPOSE":'
    add_buttons_body = popup.split("func _add_settlement_tier2_buttons(")[1]
    add_buttons_body = add_buttons_body.split("\nfunc ")[0]
    assert gate in add_buttons_body


# ===========================================================================
# UX-5 — scroll container around the per-court table
# ===========================================================================


def test_godot_scene_wraps_per_court_table_in_scroll_container():
    """UX-5 (source pins): the per-court table renders in its own
    RichTextLabel inside a ScrollContainer, so the inline expansion scrolls
    instead of growing the popup unbounded (the full-1805 horizon)."""
    scene = (GODOT_SCENES / "proposal_confirm_popup.tscn").read_text(encoding="utf-8")
    assert '[node name="PerCourtScroll" type="ScrollContainer"' in scene
    assert (
        '[node name="PerCourtTable" type="RichTextLabel" '
        'parent="PanelContainer/VBoxContainer/PerCourtScroll"]'
    ) in scene
    assert '[node name="FooterLabel" type="RichTextLabel"' in scene
    popup = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
    assert "PerCourtScroll/PerCourtTable" in popup
    assert "_render_per_court_table" in popup
    # The settlement layout splits header / scrollable table / footer.
    assert "_build_settlement_footer" in popup


# ===========================================================================
# The guided authoring controls (source pins)
# ===========================================================================


def test_godot_popup_renders_guided_authoring_controls():
    """GT-Slice-3 source pins: the popup consumes the GT-Slice-2 payload —
    treasury line, current demand lines with Remove + magnitude controls,
    the `Add demand` expansion with both §3.3 groups and reason lines, the
    GT-Slice-V voice beats — and routes every mutation through the
    structured `action_params` path (main.gd `send_dialogue_response_with_
    params`, already pinned by the slice-2 source test)."""
    popup = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(encoding="utf-8")
    # GT-Slice-2 payload consumption.
    for field in (
        "treasury_line",
        "current_demands",
        "demand_suggestions",
        "remove_action",
        "set_magnitude_action",
        "reason_display",
        "lead_group",
        "can_author",
        "authoring_disabled_reason_display",
        "region_options",
        "vassal_options",
        "authoring_voice_beats",
    ):
        assert field in popup, field
    # The inline affordances are url metas dispatched by the meta handler.
    assert "meta_clicked.connect(_on_per_court_meta_clicked)" in popup
    for op in ("[url=addmenu:", "[url=sugg:", "[url=rm:", "[url=mag:", "[url=focus:"):
        assert op in popup, op
    # Suggestion clicks fire the GT-Slice-1 add verb with the suggestion's
    # exact action_params (valid-by-construction at the suggestion source).
    assert '"settlement_demand_add"' in popup
    assert "_fire_suggestion" in popup
    assert "_emit_settlement_action" in popup
    # The popup never builds identities — payloads come from the backend's
    # ready-made action dicts (no from/to construction anywhere).
    assert '"from"' not in popup
    assert '"to":' not in popup


# ===========================================================================
# HTTP boundary (the D4 lesson — executor-direct shapes do not count)
# ===========================================================================


def test_http_boundary_settlement_demand_add_exact_godot_action_params_shape():
    """Post the EXACT payload shape the Godot popup emits for a suggestion
    click — the suggestion's `action_params` plus the `war_id` /
    `draft_key` transport keys — through `/respond_to_diplomatic_dialogue`
    (`{"choice": <action>, "action_params": <payload>}`, the
    `send_dialogue_response_with_params` wire shape) and watch the clause
    land in the restaged dialogue with live per-court re-scoring."""
    from fastapi.testclient import TestClient

    import backend.main as main_module

    client = TestClient(main_module.app)
    saved_world = main_module.world
    saved_state = main_module.game_state
    try:
        world, _ = _three_court_world()
        main_module.world = world
        main_module.game_state = {"world": world}
        dialogue = _stage_propose_real_scorer(world, terms=[{"type": "peace"}])
        prussia = next(
            r for r in dialogue["per_court_acceptance"]
            if r["nation"] == "Prussia"
        )
        suggestion = next(
            s for s in prussia["demand_suggestions"]
            if s["clause_type"] == "territory_cede" and s["group"] == "demand"
        )
        # _fire_suggestion in proposal_confirm_popup.gd: the payload IS the
        # suggestion's action_params plus war_id / draft_key.
        payload = dict(suggestion["action_params"])
        payload["war_id"] = suggestion["war_id"]
        payload["draft_key"] = suggestion["draft_key"]
        response = client.post(
            "/respond_to_diplomatic_dialogue",
            json={"choice": suggestion["action"], "action_params": payload},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True, data
        new_dialogue = data.get("diplomatic_dialogue")
        assert new_dialogue, data
        added = [
            t for t in new_dialogue["settlement_terms"]
            if t.get("type") == "territory_cede"
        ]
        assert len(added) == 1
        assert added[0]["from"] == "Prussia"
        assert added[0]["to"] == "France"
        assert added[0]["region"] == suggestion["action_params"]["region"]
        assert added[0]["authored_by"] == "player"
        # Live per-court re-score rode back with the restaged dialogue.
        assert new_dialogue.get("per_court_acceptance")
        assert new_dialogue.get("dialogue_mode") == "PROPOSE"
        # The GT-Slice-V reaction beat crossed the HTTP boundary too.
        kinds = {
            b.get("kind")
            for b in (new_dialogue.get("authoring_voice_beats") or [])
        }
        assert "court_reaction" in kinds
    finally:
        main_module.world = saved_world
        main_module.game_state = saved_state
