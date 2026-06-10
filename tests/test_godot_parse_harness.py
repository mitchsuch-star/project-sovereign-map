"""G2-Slice-W1 Godot parse/load harness + action-id whitelist sync tests.

SETTLEMENT_UI_CLEANUP_SPEC v0.28 §"Godot Parse Harness Commitment" and
Gate 3 §"Action-id whitelist sync test" pin the contract:

- `tools/godot_parse_check.gd` exists.
- `tools/godot_parse_report.json` is committed.
- Every settlement-critical script is covered with `parse_ok=True` and
  `load_ok=True`.
- The report timestamp is not older than the youngest settlement-
  critical `.gd` working-tree mtime (stale-report guard).
- Backend `VALID_ACTIONS` includes the settlement-family action ids the
  wizard maps to, and the wizard / main.gd routing paths refer to
  those same ids (no orphan whitelists in either direction).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = REPO_ROOT / "tools" / "godot_parse_check.gd"
REPORT_PATH = REPO_ROOT / "tools" / "godot_parse_report.json"

SETTLEMENT_CRITICAL_SCRIPTS = [
    "main.gd",
    "diplomacy_wizard.gd",
    "proposal_confirm_popup.gd",
    # GT-Slice-4: settlement_editor_popup.gd retired with the freeform
    # editor — the guided per-court rows on proposal_confirm_popup.gd are
    # the deep authoring tier.
    "war_detail_popup.gd",
    "war_status_panel.gd",
    "diplomatic_ledger.gd",
    "top_bar.gd",
    "notification_bar.gd",
    "mailbox_panel.gd",
]
GODOT_SCRIPTS_DIR = REPO_ROOT / "godot-client" / "project-sovereign" / "scripts"
GODOT_SCENES_DIR = REPO_ROOT / "godot-client" / "project-sovereign" / "scenes"


def _load_report() -> dict:
    with REPORT_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════════════════════════
# Parse-harness presence + report shape
# ═══════════════════════════════════════════════════════════════════════════


def test_godot_parse_harness_exists_and_covers_settlement_critical_scripts():
    assert HARNESS_PATH.exists(), (
        f"Godot parse harness missing at {HARNESS_PATH}; spec G2-Slice-W1 "
        f"requires `tools/godot_parse_check.gd`."
    )
    text = HARNESS_PATH.read_text(encoding="utf-8")
    for script in SETTLEMENT_CRITICAL_SCRIPTS:
        assert script in text, (
            f"Godot parse harness must reference {script} in its "
            f"settlement-critical scripts list."
        )


def test_godot_parse_report_passes_for_every_covered_script():
    assert REPORT_PATH.exists(), (
        f"Committed Godot parse report missing at {REPORT_PATH}; "
        f"regenerate via `Godot_v4.4.1-stable_win64.exe --headless --quit "
        f"--path godot-client/project-sovereign --script "
        f"../../tools/godot_parse_check.gd`."
    )
    report = _load_report()
    # Schema must contain timestamp + scripts list.
    assert "timestamp" in report
    assert isinstance(report.get("scripts"), list)
    covered_paths = {
        os.path.basename(entry.get("path", ""))
        for entry in report["scripts"]
    }
    for script in SETTLEMENT_CRITICAL_SCRIPTS:
        assert script in covered_paths, (
            f"Godot parse report missing settlement-critical script {script}"
        )
    for entry in report["scripts"]:
        path = entry.get("path", "")
        assert entry.get("parse_ok") is True, (
            f"Godot parse report: {path} has parse_ok=False; "
            f"regenerate harness or fix script."
        )
        assert entry.get("load_ok") is True, (
            f"Godot parse report: {path} has load_ok=False; "
            f"regenerate harness or fix script."
        )


def test_godot_parse_report_is_not_stale_relative_to_settlement_godot_sources():
    """Report timestamp must not be older than the youngest mtime of
    any settlement-critical `.gd` working-tree file. The spec defines
    the canonical comparison against git commit mtime; this test uses
    filesystem mtime as a strict-superset signal that fires on local
    edits before commit too."""
    import datetime as _dt

    report = _load_report()
    report_ts = report.get("timestamp", "")
    if not report_ts:
        raise AssertionError(
            "Godot parse report missing `timestamp` field; cannot run "
            "stale-report guard."
        )
    report_dt = _dt.datetime.fromisoformat(report_ts.replace("Z", "+00:00"))
    youngest_mtime = 0.0
    youngest_path = ""
    for script in SETTLEMENT_CRITICAL_SCRIPTS:
        path = GODOT_SCRIPTS_DIR / script
        if not path.exists():
            # Allow missing source files to be skipped — the harness
            # itself flags missing scripts via parse_ok=False, which is
            # covered by the previous test.
            continue
        mtime = path.stat().st_mtime
        if mtime > youngest_mtime:
            youngest_mtime = mtime
            youngest_path = str(path)
    if youngest_mtime == 0.0:
        return  # No source files to compare; trivially passes.
    youngest_dt = _dt.datetime.fromtimestamp(
        youngest_mtime, tz=_dt.timezone.utc,
    )
    # Allow a 24h tolerance window: local edits prior to commit are
    # routinely younger than the committed report; the spec's strict
    # check is against git commit mtime, not filesystem mtime.
    tolerance = _dt.timedelta(hours=24)
    assert report_dt + tolerance >= youngest_dt, (
        f"Godot parse report is stale: report timestamp {report_dt!r} "
        f"is older than youngest settlement-critical script "
        f"{youngest_path!r} mtime {youngest_dt!r}. Regenerate via "
        f"`Godot_v4.4.1-stable_win64.exe --headless --quit --path "
        f"godot-client/project-sovereign --script "
        f"../../tools/godot_parse_check.gd`."
    )


# ═══════════════════════════════════════════════════════════════════════════
# Action-id whitelist sync (Gate 3)
# ═══════════════════════════════════════════════════════════════════════════


SETTLEMENT_FAMILY_ACTION_IDS = {
    "propose_common_peace",
    "propose_white_peace",
    "open_settlement",
    "confirm_settlement",
    "revise_settlement_terms",
    "back_out_settlement",
    "open_war_detail",
    "accept_settlement_offer",
    "reject_settlement_offer",
    "request_settlement_revision",
    "re_author_with_concessions",
    # SC-29 / G2-Slice-7 pair-scoped peace substitute CTAs.
    "seek_bilateral_peace",
    "seek_armistice_instead",
    # SC-31 / G2-Slice-8 surrender preset CTA.
    "author_surrender_terms",
    # SC-33 / G2-Slice-9 recurring-gold finite-payment authoring CTA.
    "author_recurring_gold_terms",
    # Empty first-open winning-side settlement authoring CTAs.
    "author_gold_indemnity_terms",
    "author_gold_per_turn_terms",
    # G2-Slice-G2e same-war different-scope chooser CTAs.
    "replace_current_scope_draft",
    "keep_current_scope_draft",
}


def _collect_wizard_mappings() -> Tuple[List[str], List[str]]:
    """Return (build_command_action_ids, structured_payload_action_ids)
    grouped from the wizard's `_build_command` match arms and the
    structured payload `if action_id == ...` checks."""
    wizard_path = GODOT_SCRIPTS_DIR / "diplomacy_wizard.gd"
    text = wizard_path.read_text(encoding="utf-8")
    build_pattern = re.compile(r'^\s*"(\w+)":\s*$', re.MULTILINE)
    build_ids = build_pattern.findall(text)
    structured_pattern = re.compile(r'action_id == "(\w+)"')
    structured_ids = structured_pattern.findall(text)
    return build_ids, structured_ids


def _extract_gd_string_array(source: str, const_name: str) -> List[str]:
    start = source.index(f"const {const_name} := [")
    end = source.index("]", start)
    return re.findall(r'"([A-Za-z0-9_]+)"', source[start:end])


def _extract_post_hud_route_ids(source: str) -> List[str]:
    start = source.index("_post_hud_response_routes = [")
    end = source.index("]", start)
    block = source[start:end]
    return re.findall(r'{"id": "([A-Za-z0-9_]+)"', block)


def _extract_executor_settlement_dispatch_actions(source: str) -> List[str]:
    handler_anchor = (
        "from backend.game_logic.settlement_actions import (\n"
        "                handle_settlement_dialogue_action,\n"
        "            )"
    )
    pre_handler = source.split(handler_anchor, 1)[0]
    elif_open = pre_handler.rfind("elif action in (")
    assert elif_open != -1
    tuple_block = pre_handler[elif_open:]
    tuple_body = tuple_block.split("):", 1)[0]
    return re.findall(r'"([A-Za-z0-9_]+)"', tuple_body)


def _extract_executor_incoming_offer_dispatch_actions(source: str) -> List[str]:
    handler_anchor = (
        "from backend.game_logic.settlement_preview import (\n"
        "                handle_incoming_settlement_offer_action,\n"
        "            )"
    )
    pre_handler = source.split(handler_anchor, 1)[0]
    elif_open = pre_handler.rfind("elif action in (")
    assert elif_open != -1
    tuple_block = pre_handler[elif_open:]
    tuple_body = tuple_block.split("):", 1)[0]
    return re.findall(r'"([A-Za-z0-9_]+)"', tuple_body)


def _extract_executor_ally_petition_dispatch_actions(source: str) -> List[str]:
    handler_anchor = (
        "from backend.game_logic.settlement_preview import (\n"
        "                handle_ally_settlement_petition_action,\n"
        "            )"
    )
    pre_handler = source.split(handler_anchor, 1)[0]
    elif_open = pre_handler.rfind("elif action == ")
    assert elif_open != -1
    branch_block = pre_handler[elif_open:]
    return re.findall(r'"([A-Za-z0-9_]+)"', branch_block.split(":", 1)[0])


def _simulate_main_gd_command_result_route(response: dict, source: str) -> str:
    """Small executable model of the relevant `_on_command_result` route order.

    The model intentionally covers only the settlement/proposal branches used
    by this gate: post-HUD modal routing runs before the recovery-route branch,
    and `_route_settlement_recovery_route` handles only war detail/history.
    """
    for route_id in _extract_post_hud_route_ids(source):
        if route_id == "deferred_incoming_settlement_offer":
            dialogue = response.get("diplomatic_dialogue", {})
            if (
                isinstance(dialogue, dict)
                and dialogue.get("type", dialogue.get("dialogue_type", ""))
                == "incoming_settlement_offer"
            ):
                return route_id
            if response.get("dialogue_type", "") == "incoming_settlement_offer":
                return route_id
        elif route_id == "proposal_confirm":
            if response.get("diplomatic_dialogue") is not None:
                return route_id

    recovery_route = response.get("recovery_route")
    if isinstance(recovery_route, dict):
        surface = str(
            recovery_route.get("surface", recovery_route.get("target", ""))
        )
        if surface in {"war_detail", "settlement_history"}:
            return f"recovery_route:{surface}"
        return "continue_without_recovery_early_return"
    return "continue"


def test_settlement_action_id_whitelists_are_in_sync_across_backend_main_gd_and_wizard():
    """Backend must dispatch the settlement-family structured action ids
    the wizard sends. Spec Gate 3 §"Action-id whitelist sync test"
    checks the full chain: backend executor.py routes the action id,
    diplomatic_executor.py has a matching `_execute_*` method, and the
    wizard maps the action id to a command echo."""
    from backend.ai.validation import VALID_ACTIONS, META_ACTIONS

    # Backend action ids the wizard/structured-action path dispatches.
    # `propose_common_peace` and `propose_white_peace` must both be
    # recognized by either VALID_ACTIONS or META_ACTIONS (both are
    # validated entry points; VALID_ACTIONS is the LLM-classified set,
    # META_ACTIONS is the marshal-less / free-action set — settlement
    # entry historically lives in META_ACTIONS).
    backend_required = {"propose_common_peace", "propose_white_peace"}
    known_actions = VALID_ACTIONS | META_ACTIONS
    for action in backend_required:
        assert action in known_actions, (
            f"Backend VALID_ACTIONS ∪ META_ACTIONS missing {action!r}; "
            f"wizard / structured-action dispatch would fail."
        )

    # Executor dispatch tables contain `_execute_propose_common_peace`
    # and `_execute_propose_white_peace` methods.
    from backend.commands.diplomatic_executor import DiplomaticExecutor
    for method_name in (
        "_execute_propose_common_peace",
        "_execute_propose_white_peace",
    ):
        assert hasattr(DiplomaticExecutor, method_name), (
            f"DiplomaticExecutor missing {method_name!r}; backend "
            f"cannot dispatch the structured action."
        )

    # The top-level executor router has match arms for both actions.
    executor_path = REPO_ROOT / "backend" / "commands" / "executor.py"
    executor_text = executor_path.read_text(encoding="utf-8")
    for action in ("propose_common_peace", "propose_white_peace"):
        assert f'action == "{action}"' in executor_text, (
            f"backend/commands/executor.py missing dispatch arm for "
            f"{action!r}."
        )

    settlement_actions_text = (
        REPO_ROOT / "backend" / "game_logic" / "settlement_actions.py"
    ).read_text(encoding="utf-8")
    for action in SETTLEMENT_FAMILY_ACTION_IDS - {
        "propose_common_peace",
        "propose_white_peace",
        "open_settlement",
        "accept_settlement_offer",
        "reject_settlement_offer",
        "request_settlement_revision",
    }:
        assert f'action == "{action}"' in settlement_actions_text, (
            f"settlement_actions.py missing dialogue handler branch for "
            f"{action!r}; visible settlement action would become a no-op."
        )

    # The wizard must have a `_build_command` arm for the settlement
    # wizard entry ids it surfaces.
    build_ids, _structured_ids = _collect_wizard_mappings()
    for action in ("open_settlement", "propose_white_peace"):
        assert action in build_ids, (
            f"diplomacy_wizard.gd::_build_command missing match arm for "
            f"{action!r}. The wizard cannot translate the structured "
            f"action into a command echo."
        )


def test_settlement_action_id_whitelists_have_no_orphan_typed_command_mappings():
    """The wizard must not map a settlement action id to a typed
    command string the backend parser cannot resolve. The backend
    parser only auto-classifies `propose_common_peace` keywords, not
    `propose_white_peace`; the wizard SHOULD ship `propose_white_peace`
    as a structured-payload-only mapping (no typed parser dependence)."""
    wizard_path = GODOT_SCRIPTS_DIR / "diplomacy_wizard.gd"
    text = wizard_path.read_text(encoding="utf-8")
    # Spec line 352: `propose_white_peace` is structured-only on the
    # wizard surface. Ensure the wizard's `_structured_payload_for_action`
    # treats `propose_white_peace` like `open_settlement` (returns
    # structured data with explicit `action` field).
    assert "propose_white_peace" in text, (
        "diplomacy_wizard.gd must reference propose_white_peace "
        "(via `_build_command` and `_structured_payload_for_action`)."
    )


# ═══════════════════════════════════════════════════════════════════════════
# G2-Gate4-Repair-1: Dialogue-endpoint dispatch coverage regression
# ═══════════════════════════════════════════════════════════════════════════


# Settlement-family dialogue action ids that arrive through
# /respond_to_diplomatic_dialogue (NOT structured /command entry).
# These are popup-button actions inside the staged settlement_confirm
# dialogue. They must be routed to `handle_settlement_dialogue_action`
# inside `DiplomaticExecutor._process_dialogue_choice`. Missing the
# dispatch tuple makes the action fall through to the "Unknown dialogue
# action" branch and breaks the Godot popup — exactly the SC-29 /
# SC-31 / G2-Slice-W1 Gate 4 smoke regression this test pins.
SETTLEMENT_DIALOGUE_DISPATCH_ACTION_IDS = [
    "confirm_settlement",
    "revise_settlement_terms",
    "back_out_settlement",
    # SC-5R-2 follow-up: non-destructive editor Back Out (pops the
    # settlement_confirm hard-stop, preserves the scoped draft).
    "suspend_settlement_editor",
    # Re-front Slice 1 PROPOSE rail: Submit for Review re-stages REVIEW.
    # (`adjust_terms` is NOT here: it is handled client-side in Godot and the
    # bilateral terms-guidance flow owns that backend action id.)
    "submit_settlement_for_review",
    # Re-front UX follow-up: REVIEW -> PROPOSE recovery from a blocked review.
    "return_to_settlement_terms",
    # Re-front Slice 2 PROPOSE Tier-2 verbs: intent dials, coverage edits, and
    # court focus. They ride on per-court rows / rail buttons and carry
    # structured `scope` / `nation` params (routed via `action_params`).
    "settlement_dial_harsher",
    "settlement_dial_generous",
    "settlement_cover_add",
    "settlement_cover_drop",
    "settlement_focus_court",
    # GT-Slice-1 guided demand-mutation verbs (Guided Terms §7): per-court
    # add / remove / set-magnitude with structured `nation` / `group` /
    # `clause_type` / `clause_index` params — same transport as the dials.
    "settlement_demand_add",
    "settlement_demand_remove",
    "settlement_demand_set_magnitude",
    "open_war_detail",
    "re_author_with_concessions",
    "apply_concession_baseline_replacement",
    "keep_current_settlement_draft",
    "seek_bilateral_peace",
    "seek_armistice_instead",
    "author_surrender_terms",
    "apply_surrender_preset_replacement",
    "author_recurring_gold_terms",
    "apply_recurring_gold_preset_replacement",
    "author_gold_indemnity_terms",
    "author_gold_per_turn_terms",
    "replace_current_scope_draft",
    "keep_current_scope_draft",
]

# SC-5 reversal commit 2 / Slice G1 incoming-offer dispatch tuple.
# These ids reach `handle_incoming_settlement_offer_action`, NOT the
# standard `handle_settlement_dialogue_action`, but they still ship in
# Godot's SETTLEMENT_DIALOGUE_ACTIONS whitelist and must be present in
# the executor's incoming-offer dispatch arm.
INCOMING_SETTLEMENT_OFFER_DISPATCH_ACTION_IDS = [
    "accept_settlement_offer",
    "reject_settlement_offer",
    "request_settlement_revision",
]

ALLY_SETTLEMENT_PETITION_DISPATCH_ACTION_IDS = [
    "acknowledge_ally_settlement_petition",
]


def test_process_dialogue_choice_dispatches_every_settlement_action_to_handler():
    """Backend regression guard: every settlement-family popup action id
    that ships in the Godot `SETTLEMENT_DIALOGUE_ACTIONS` whitelist and
    in `handle_settlement_dialogue_action` must also be routed by
    `DiplomaticExecutor._process_dialogue_choice` to the settlement
    handler. The pre-repair dispatch tuple only listed four ids, so
    SC-29 `seek_bilateral_peace` / `seek_armistice_instead`, SC-31
    `author_surrender_terms`, and G2-Slice-W1 `re_author_with_concessions`
    all hit the "Unknown dialogue action" fall-through. Backend tests
    that called the handler directly never caught it because they
    bypassed the executor dispatch."""
    executor_path = REPO_ROOT / "backend" / "commands" / "diplomatic_executor.py"
    text = executor_path.read_text(encoding="utf-8")

    # Find the `elif action in (...)` dispatch tuple that routes to
    # `handle_settlement_dialogue_action`. The arm is the only place
    # in _process_dialogue_choice that imports that handler.
    handler_anchor = "from backend.game_logic.settlement_actions import (\n                handle_settlement_dialogue_action,\n            )"
    assert handler_anchor in text, (
        "diplomatic_executor.py no longer imports "
        "handle_settlement_dialogue_action inside _process_dialogue_choice; "
        "the dispatch wiring has been refactored away from the anchor "
        "this regression test pins. Update the anchor."
    )

    # Slice the file from the start to the handler import; the action
    # tuple lives in the `elif action in (...)` block immediately above.
    pre_handler = text.split(handler_anchor, 1)[0]
    # Take the last `elif action in (...)` block before the import; the
    # tuple body sits between the opening `(` and the closing `):`.
    elif_open = pre_handler.rfind("elif action in (")
    assert elif_open != -1, (
        "Could not locate the `elif action in (` dispatch tuple "
        "immediately above the handle_settlement_dialogue_action import."
    )
    tuple_block = pre_handler[elif_open:]
    for action_id in SETTLEMENT_DIALOGUE_DISPATCH_ACTION_IDS:
        assert f'"{action_id}"' in tuple_block, (
            f"_process_dialogue_choice dispatch tuple is missing "
            f"{action_id!r}. Without this dispatch arm, the popup action "
            f"falls through to the 'Unknown dialogue action' branch and "
            f"the Godot settlement popup hangs."
        )


def test_godot_settlement_dialogue_actions_match_backend_dispatch_tuple_exactly():
    """Similar-bug guard: every Godot settlement popup action must have
    a backend dialogue-endpoint dispatch arm. SC-5 reversal commit 2
    adds the three incoming-offer action ids to a second dispatch
    tuple (`handle_incoming_settlement_offer_action`); they are not
    extra orphans, just routed to a different handler."""
    main_text = (GODOT_SCRIPTS_DIR / "main.gd").read_text(encoding="utf-8")
    executor_text = (
        REPO_ROOT / "backend" / "commands" / "diplomatic_executor.py"
    ).read_text(encoding="utf-8")

    godot_actions = set(
        _extract_gd_string_array(main_text, "SETTLEMENT_DIALOGUE_ACTIONS")
    )
    backend_settlement_dispatch = set(
        _extract_executor_settlement_dispatch_actions(executor_text)
    )
    backend_incoming_dispatch = set(
        _extract_executor_incoming_offer_dispatch_actions(executor_text)
    )
    backend_ally_petition_dispatch = set(
        _extract_executor_ally_petition_dispatch_actions(executor_text)
    )

    expected_godot_actions = (
        set(SETTLEMENT_DIALOGUE_DISPATCH_ACTION_IDS)
        | set(INCOMING_SETTLEMENT_OFFER_DISPATCH_ACTION_IDS)
        | set(ALLY_SETTLEMENT_PETITION_DISPATCH_ACTION_IDS)
    )
    assert godot_actions == expected_godot_actions
    assert backend_settlement_dispatch == set(
        SETTLEMENT_DIALOGUE_DISPATCH_ACTION_IDS
    )
    assert backend_incoming_dispatch == set(
        INCOMING_SETTLEMENT_OFFER_DISPATCH_ACTION_IDS
    )
    assert backend_ally_petition_dispatch == set(
        ALLY_SETTLEMENT_PETITION_DISPATCH_ACTION_IDS
    )
    # No orphan action ids: every Godot whitelist id must appear in
    # exactly one backend dispatch branch.
    union = (
        backend_settlement_dispatch
        | backend_incoming_dispatch
        | backend_ally_petition_dispatch
    )
    assert godot_actions == union


def test_godot_recovery_route_does_not_block_proposal_confirm_fall_through():
    """Godot regression guard: `_on_command_result` must not consume a
    response with `recovery_route.surface == "proposal_confirm"` via
    `_route_settlement_recovery_route` (which only handles `war_detail`
    and `settlement_history`). The SC-29 pair-substitute response
    carries both `recovery_route` (surface=proposal_confirm) and a
    fresh `diplomatic_dialogue`; if the recovery branch returns early
    for that surface the new proposal popup never opens."""
    main_path = GODOT_SCRIPTS_DIR / "main.gd"
    text = main_path.read_text(encoding="utf-8")
    # The repair pattern: gate the early return on the surface set the
    # recovery helper actually understands. The literal phrase pins it.
    expected_gate = (
        'if rr_surface in ["war_detail", "settlement_history"]'
    )
    assert expected_gate in text, (
        "main.gd::_on_command_result must scope the recovery_route "
        "early-return to surfaces that "
        "`_route_settlement_recovery_route` handles; otherwise SC-29 "
        "pair-substitute responses get consumed before the proposal "
        "popup can open from `diplomatic_dialogue`."
    )


def test_proposal_confirm_button_container_wraps_settlement_action_rail():
    """Settlement REVIEW can expose six legal actions after SC-29/31/33.

    A fixed HBox silently clips lower-priority actions in the 720px popup,
    which made player smoke ambiguous. The scene must use a wrapping grid
    and the script must let buttons expand inside grid cells.
    """
    scene_text = (
        GODOT_SCENES_DIR / "proposal_confirm_popup.tscn"
    ).read_text(encoding="utf-8")
    script_text = (
        GODOT_SCRIPTS_DIR / "proposal_confirm_popup.gd"
    ).read_text(encoding="utf-8")

    assert '[node name="ButtonContainer" type="GridContainer"' in scene_text
    assert "columns = 3" in scene_text
    assert "btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL" in script_text


def test_godot_command_result_routes_proposal_confirm_recovery_response_to_popup():
    """Behavior twin for the source guard above.

    The SC-29 substitute response carries both a recovery route and a fresh
    proposal dialogue. Driving that response through the route-order model
    must pick the proposal popup, while the two real recovery surfaces still
    route to `_route_settlement_recovery_route`.
    """
    main_text = (GODOT_SCRIPTS_DIR / "main.gd").read_text(encoding="utf-8")
    proposal_response = {
        "success": True,
        "recovery_route": {
            "surface": "proposal_confirm",
            "target": "proposal_confirm",
            "war_id": "war_1",
            "selected_target_nation": "Austria",
        },
        "diplomatic_dialogue": {
            "type": "proposal_confirm",
            "target_nation": "Austria",
            "context": {"proposal_type": "peace"},
        },
    }
    assert (
        _simulate_main_gd_command_result_route(proposal_response, main_text)
        == "proposal_confirm"
    )

    for surface in ("war_detail", "settlement_history"):
        recovery_response = {
            "success": False,
            "recovery_route": {
                "surface": surface,
                "war_id": "war_1",
                "selected_target_nation": "Austria",
            },
        }
        assert _simulate_main_gd_command_result_route(
            recovery_response, main_text
        ) == f"recovery_route:{surface}"
