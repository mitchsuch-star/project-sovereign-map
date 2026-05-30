"""Settlement Conversational Re-front — Slice 3 behavior tests.

`docs/SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md` v0.6 §14 Slice 3 (Tier 3
valid-by-construction editor):

- `Adjust terms` from PROPOSE opens the Tier-3 editor, optionally focused on a
  court (§14 `test_adjust_terms_from_propose_opens_edit_optionally_focused`).
- Multi-party cross-court validity V1-V3 in `validate_settlement_terms` (§12):
  V1 `region_double_promised`, V2 `clause_target_uncovered`,
  V3 `clause_side_mismatch`. (V4 self-reference + V5 coverage floor already
  land in Slice 0 / Slice 2 and are exercised there.)
- P2/P3 picker filtering: the nation pickers offer only proposer-side + covered
  courts, and a coverage drop re-filters every picker (§13).
- REFRONT-8: the Godot Tier-3 editor consumes `clause_control_schema[type]
  .enabled` / `disabled_reason_display` instead of opening an empty picker.
- DWL-SET-SC5R-3: inline merge-conflict `Discard new clause` /
  `Replace active clause` controls (cleanup spec line 589).

Backend validity is tested against the live validator. The Godot editor /
main.gd surfaces are pinned at source level (the project has no scene-graph
harness; the headless parse harness is `tools/godot_parse_report.json`).
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.settlement_preview import (
    _build_clause_control_schema_for_review,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)

_SCORER_PATH = "backend.game_logic.settlement_preview.calculate_common_peace_acceptance"

GODOT_ROOT = Path(__file__).resolve().parent.parent / "godot-client" / "project-sovereign"
EDITOR_SCRIPT = GODOT_ROOT / "scripts" / "settlement_editor_popup.gd"
MAIN_SCRIPT = GODOT_ROOT / "scripts" / "main.gd"


# ===========================================================================
# Helpers
# ===========================================================================


def _read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _function_body(path: Path, function_name: str) -> str:
    source = _read_source(path)
    marker = f"func {function_name}"
    start = source.find(marker)
    assert start != -1, f"{path} missing {marker}"
    next_func = re.search(r"\nfunc\s+\w+", source[start + 1:])
    end = len(source) if next_func is None else start + 1 + next_func.start()
    return source[start:end]


def _set_war_score(world: WorldState, frm: str, to: str, score: int) -> None:
    key = world._make_diplo_key(frm, to)
    world.diplomatic_states[key] = "WAR"
    if sorted([frm, to])[0] == frm:
        world.war_scores[key] = int(score)
    else:
        world.war_scores[key] = -int(score)


def _three_court_world():
    """France (attacker) vs Britain + Prussia + Austria (defenders)."""
    world = WorldState()
    inst = make_synthetic_war_instance(
        "war_rf",
        attackers=["France"],
        defenders=["Britain", "Prussia", "Austria"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances["war_rf"] = inst
    _set_war_score(world, "France", "Prussia", 70)
    _set_war_score(world, "France", "Britain", -70)
    _set_war_score(world, "France", "Austria", 0)
    world.invalidate_war_instance_indexes()
    return world, inst


def _accept_scorer(world=None, *, accepting_leader=None, **kwargs):
    return {
        "score": 60,
        "verdict": "accept",
        "components": {},
        "component_debug": {},
        "feedback": [],
        "hard_stops": [],
        "accept_threshold": 50,
        "near_acceptable_threshold": 35,
        "side_pressure_score": 30,
        "raw_total": 60,
        "raw_total_harshness": 0.0,
        "direct_scores": {},
        "direct_score_sources": {},
    }


def _stage_propose(world, *, terms=None, covered=None):
    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        staged = stage_settlement_confirm(
            world,
            war_id="war_rf",
            actor_nation="France",
            settlement_terms=terms or [{"type": "peace"}],
            covered_enemy_participants=covered or ["Britain", "Prussia", "Austria"],
            selected_target_nation="Austria",
            caller_kind="player_editor",
            dialogue_mode="PROPOSE",
        )
    assert staged.get("success"), staged
    return staged["diplomatic_dialogue"]


# ===========================================================================
# 1. Adjust terms from PROPOSE opens the Tier-3 editor (optionally focused)
# ===========================================================================


def test_adjust_terms_from_propose_opens_edit_optionally_focused():
    world, _ = _three_court_world()
    dialogue = _stage_propose(world)
    # The PROPOSE dialogue carries the full editor contract so `Adjust terms`
    # can mount the Tier-3 editor locally (no backend round-trip).
    assert dialogue.get("can_edit_terms") is True
    assert isinstance(dialogue.get("editor_route"), dict) and dialogue["editor_route"]
    assert dialogue.get("dialogue_mode") == "PROPOSE"
    assert dialogue.get("focused_court") in (None, "")

    # Focusing a court (presentation-only) carries `focused_court` onto the
    # dialogue while preserving the editor contract — so `Adjust terms` opens
    # EDIT focused on that court.
    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        focused = handle_settlement_dialogue_action(
            world,
            action="settlement_focus_court",
            dialogue=dialogue,
            action_params={"nation": "Prussia"},
        )
    assert focused.get("success"), focused
    fdlg = focused["diplomatic_dialogue"]
    assert fdlg.get("focused_court") == "Prussia"
    assert fdlg.get("can_edit_terms") is True
    assert isinstance(fdlg.get("editor_route"), dict) and fdlg["editor_route"]

    # Godot side: main.gd routes `adjust_terms` to the local editor mount and
    # the editor surfaces the focused court.
    main_body = _function_body(MAIN_SCRIPT, "_on_proposal_confirm_choice")
    assert 'if action == "adjust_terms":' in main_body
    assert "settlement_editor_popup.show_editor(data)" in main_body
    show_body = _function_body(EDITOR_SCRIPT, "show_editor")
    assert 'focused_court = str(data.get("focused_court", ""))' in show_body
    header_body = _function_body(EDITOR_SCRIPT, "_render_header")
    assert "focused_court" in header_body


# ===========================================================================
# 2-4. Multi-party cross-court validity rules (§12 V1-V3)
# ===========================================================================


def test_no_region_promised_to_two_courts():
    """V1 — a region may appear in at most one territory_cede clause."""
    _, inst = _three_court_world()
    result = validate_settlement_terms(
        [
            {"type": "territory_cede", "from": "Britain", "to": "France", "region": "Hanover"},
            {"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Hanover"},
        ],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert result["valid"] is False
    assert result["error"] == "region_double_promised"
    # Both offending clause indices are named so the editor can resolve.
    assert result["error_index"] == 1
    assert result["conflicting_index"] == 0
    assert result.get("disabled_reason_display")

    # A single promise of the same region is valid.
    ok = validate_settlement_terms(
        [{"type": "territory_cede", "from": "Britain", "to": "France", "region": "Hanover"}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert ok["valid"] is True


def test_clause_cannot_bind_uncovered_court():
    """V2 — a clause may not bind an enemy court outside the covered set."""
    _, inst = _three_court_world()
    # Prussia is NOT covered; a clause naming it must reject.
    result = validate_settlement_terms(
        [{"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Hanover"}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain"],
    )
    assert result["valid"] is False
    assert result["error"] == "clause_target_uncovered"
    assert result.get("uncovered_nation") == "Prussia"

    # Covering Prussia makes the same clause bindable (V3 still applies to
    # from/to sides, which here are correct: Prussia=defender, France=attacker).
    ok = validate_settlement_terms(
        [{"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Hanover"}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia"],
    )
    assert ok["valid"] is True


def test_clause_from_to_must_match_war_sides():
    """V3 — a value-transfer clause must straddle opposite war sides."""
    _, inst = _three_court_world()
    # Britain and Prussia are both defenders — a transfer between them is a
    # same-side clause and must reject even though both are covered.
    result = validate_settlement_terms(
        [{"type": "territory_cede", "from": "Britain", "to": "Prussia", "region": "Hanover"}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert result["valid"] is False
    assert result["error"] == "clause_side_mismatch"

    # A self-referential transfer (from == to) is the degenerate same-side
    # case V3 also catches (kills "France pays France").
    self_ref = validate_settlement_terms(
        [{"type": "gold_indemnity", "from": "France", "to": "France", "amount": 100}],
        war_instance=inst,
        proposer_side="attackers",
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
    )
    assert self_ref["valid"] is False
    assert self_ref["error"] == "clause_side_mismatch"


def test_submit_revalidation_enforces_uncovered_court_defense_in_depth():
    """§12 defense-in-depth: the EDIT Submit revalidation re-runs V2 with the
    covered set, so a tampered package binding an uncovered court is rejected
    at Submit (not only at POST preview)."""
    world, _ = _three_court_world()
    executor = DiplomaticExecutor(None)
    cmd = {
        "action": "propose_common_peace",
        "target_nation": "Britain",
        "war_id": "war_rf",
        "selected_target_nation": "Britain",
        "covered_enemy_participants": ["Britain"],
        "settlement_terms": [
            {"type": "territory_cede", "from": "Prussia", "to": "France", "region": "Hanover"},
        ],
        "caller_kind": "player_editor",
    }
    with patch(_SCORER_PATH, side_effect=_accept_scorer):
        result = executor._execute_propose_common_peace(cmd, {"world": world})
    assert result.get("success") is False
    assert result.get("error") == "submitted_terms_failed_revalidation"
    assert result.get("validation_error") == "clause_target_uncovered"


# ===========================================================================
# 7-8. Picker valid-by-construction (§13 P3 + OQ#7)
# ===========================================================================


def _nation_option_ids(schema, ctype="gold_indemnity", field="from"):
    return [o["id"] for o in schema[ctype]["fields"][field]["options"]]


def test_tier3_picker_refilters_on_coverage_change():
    """P3 — dropping a court from coverage removes it from every picker."""
    world, inst = _three_court_world()
    full = _build_clause_control_schema_for_review(
        world,
        war_instance=inst,
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
        proposer_side="attackers",
    )
    assert "Prussia" in _nation_option_ids(full)

    dropped = _build_clause_control_schema_for_review(
        world,
        war_instance=inst,
        covered_enemy_participants=["Britain"],
        proposer_side="attackers",
    )
    ids = _nation_option_ids(dropped)
    assert "Prussia" not in ids
    assert "Austria" not in ids
    # Proposer-side France and the still-covered Britain remain pickable.
    assert "France" in ids
    assert "Britain" in ids


def test_tier1_default_identity_remains_replaceable_in_tier3():
    """OQ#7 — a Tier-1 pre-filled region/payer default is not locked: the
    editor pickers always offer the full filtered option set, so the player can
    change the requested region or payer identity in Tier 3."""
    world, inst = _three_court_world()
    schema = _build_clause_control_schema_for_review(
        world,
        war_instance=inst,
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
        proposer_side="attackers",
    )
    # The payer/payee identity can be swapped — more than one nation is offered.
    from_ids = _nation_option_ids(schema, "gold_indemnity", "from")
    to_ids = _nation_option_ids(schema, "gold_indemnity", "to")
    assert len(from_ids) >= 2
    assert len(to_ids) >= 2
    # The requested region can be replaced — the territory picker is a real list
    # of alternatives, not a single locked default.
    region_opts = schema["territory_cede"]["fields"]["region"]["options"]
    assert len(region_opts) >= 2


# ===========================================================================
# 5-6 + 9. Godot Tier-3 editor surfaces (REFRONT-8 + DWL-SET-SC5R-3)
# ===========================================================================


def test_godot_editor_disables_add_clause_for_disabled_type_and_surfaces_reason():
    """REFRONT-8 — the editor consumes clause_control_schema[type].enabled /
    disabled_reason_display: it greys disabled types in the dropdown and
    surfaces the reason instead of opening an empty picker."""
    # Backend half: with no vassals in the world, liberation has an empty vassal
    # picker, so its schema row is disabled with a humanized reason while the
    # type stays a schema key (available_clause_types unchanged).
    world, inst = _three_court_world()
    schema = _build_clause_control_schema_for_review(
        world,
        war_instance=inst,
        covered_enemy_participants=["Britain", "Prussia", "Austria"],
        proposer_side="attackers",
    )
    assert "liberation" in schema
    assert schema["liberation"]["enabled"] is False
    assert schema["liberation"]["disabled_reason_display"]

    # Godot half: the dropdown population reads `enabled` + greys the item, and
    # the Add Clause handler surfaces `disabled_reason_display` rather than
    # opening an empty picker.
    populate_body = _function_body(EDITOR_SCRIPT, "_populate_add_clause_selector")
    assert "clause_control_schema.get(str(ttype), {})" in populate_body
    assert 'schema_entry.get("enabled", true)' in populate_body
    assert "set_item_disabled(idx, not type_enabled)" in populate_body

    add_body = _function_body(EDITOR_SCRIPT, "_on_add_clause_pressed")
    assert 'schema_entry.get("enabled", true)' in add_body
    assert 'disabled_reason_display' in add_body
    # The disabled branch returns BEFORE opening the editor panel.
    assert "return" in add_body
    assert add_body.index('disabled_reason_display') < add_body.index("clause_editor_panel.visible = true")


def test_merge_conflict_discard_new_clause_control():
    """DWL-SET-SC5R-3 — a newly authored clause that conflicts with an active
    clause is held (not appended); `Discard new clause` drops the new clause and
    keeps the active one."""
    confirm_body = _function_body(EDITOR_SCRIPT, "_on_confirm_clause_pressed")
    # The conflict is detected before append, and on conflict the new clause is
    # stashed + the resolution controls shown, with an early return (no append).
    assert "_find_conflict_for_new_clause(clause)" in confirm_body
    assert "pending_conflict_clause = clause.duplicate(true)" in confirm_body
    assert "_render_merge_conflict_controls()" in confirm_body
    assert confirm_body.index("_find_conflict_for_new_clause(clause)") < confirm_body.index(
        "settlement_terms.append(clause)"
    )

    discard_body = _function_body(EDITOR_SCRIPT, "_on_discard_new_clause_pressed")
    # Discard clears the pending new clause and does NOT append it.
    assert "pending_conflict_clause = {}" in discard_body
    assert "pending_conflict_index = -1" in discard_body
    assert "settlement_terms.append" not in discard_body
    assert "remove_at" not in discard_body

    # The control exists and is wired.
    source = _read_source(EDITOR_SCRIPT)
    assert 'discard_new_clause_button.text = "Discard new clause"' in source
    assert "discard_new_clause_button.pressed.connect(_on_discard_new_clause_pressed)" in source


def test_merge_conflict_replace_active_clause_control():
    """DWL-SET-SC5R-3 — `Replace active clause` removes the conflicting active
    clause and commits the new clause in its place."""
    replace_body = _function_body(EDITOR_SCRIPT, "_on_replace_active_clause_pressed")
    assert "settlement_terms.remove_at(pending_conflict_index)" in replace_body
    assert "settlement_terms.append(pending_conflict_clause)" in replace_body
    # Removal of the active clause happens before appending the new one.
    assert replace_body.index("remove_at(pending_conflict_index)") < replace_body.index(
        "append(pending_conflict_clause)"
    )
    assert "pending_conflict_clause = {}" in replace_body

    source = _read_source(EDITOR_SCRIPT)
    assert 'replace_active_clause_button.text = "Replace active clause"' in source
    assert "replace_active_clause_button.pressed.connect(_on_replace_active_clause_pressed)" in source


def test_merge_conflict_detection_mirrors_backend_authority():
    """The client-side conflict helper mirrors the backend conflict authority
    (CLAUSE_CONFLICT_MATRIX + V1 region rule) so inline resolution matches what
    Submit would reject."""
    helper_body = _function_body(EDITOR_SCRIPT, "_find_conflict_for_new_clause")
    # V1 region-double-promise mirror.
    assert 'ntype == "territory_cede" and etype == "territory_cede"' in helper_body
    assert 'new_clause.get("region"' in helper_body
    pair_body = _function_body(EDITOR_SCRIPT, "_is_conflicting_type_pair")
    for ctype in ("vassalage", "forced_alliance", "subjugation"):
        assert ctype in pair_body
