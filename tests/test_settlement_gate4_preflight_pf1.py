"""PF-1 — Gate-4 pre-flight audit §4: losing-baseline validity + failure-path
visibility (`docs/SETTLEMENT_GATE4_PREFLIGHT_AUDIT.md`).

Pins the seven named PF-1 tests:

- D1: the real `settlement_losing` fixture opens to a validator-clean
  baseline (no region double-promise, no treasury double-spend) with honest
  per-court bands instead of a false "carries".
- D1: concede-court gold draws split the ONE treasury.
- D1/D2: generated baselines are validated before staging (PROPOSE mount and
  the `submit_settlement_for_review` arm).
- D2: a blocked ratify re-attaches the staged dialogue with a rendered
  `error_display` (never a popped dialogue with no surface and no reason).
- D2: `/respond_to_diplomatic_dialogue` passes the handler's text through
  instead of defaulting to "Response processed".
- D3: Godot renders the failure on the re-mounted popup (source pins).
- D6: the targeted-posture advisory never recommends "press" on a
  concede-direction court.

Plus the DC-2 binding-constraint guidance (budget-bound hint variant +
Talleyrand voice line) that lands with PF-1.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.game_logic.diplomatic_templates import resolve_settlement_voice_line
from backend.game_logic.settlement_preview import (
    CONCESSION_BASELINE_TREASURY_RESERVE,
    _settlement_budget_bound_constraint,
    _settlement_propose_carry_hint,
    _settlement_targeted_posture_advisory,
    build_settlement_preview,
    compute_settlement_baseline,
    handle_settlement_dialogue_action,
    ratify_settlement_confirm,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.models.world_state import (
    SMOKE_START_ENV,
    SMOKE_START_SETTLEMENT_LOSING,
    WorldState,
)

GODOT_SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "godot-client"
    / "project-sovereign"
    / "scripts"
)


@pytest.fixture
def losing_world(monkeypatch):
    """The REAL `settlement_losing` smoke fixture (the D1/D2 repro world)."""
    monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_LOSING)
    return WorldState()


def _losing_baseline(world: WorldState) -> dict:
    war_instance = world.war_instances["war_1"]
    return compute_settlement_baseline(
        world,
        war_id="war_1",
        war_instance=war_instance,
        proposer_side="attackers",
        accepting_side="defenders",
        proposer_side_leader="France",
        covered_enemy_participants=["Britain", "Prussia"],
    )


def _stage_losing_propose(world: WorldState) -> dict:
    return stage_settlement_confirm(
        world,
        war_id="war_1",
        actor_nation="France",
        selected_target_nation="Britain",
        covered_enemy_participants=["Britain", "Prussia"],
        caller_kind="player_editor",
        dialogue_mode="PROPOSE",
    )


class TestLosingBaselineValidity:
    def test_losing_multicourt_baseline_validates_clean(self, losing_world):
        """D1: the exact pre-fix failure — `settlement_losing` generated
        `[peace, 1000g→Britain, cede Waterloo→Britain, 1000g→Prussia,
        cede Waterloo→Prussia]` (region double-promised + 2000g from a
        1500g treasury) and showed "This peace carries". The generated
        baseline must now validate clean with honest holdout bands."""
        preview = build_settlement_preview(
            losing_world,
            war_id="war_1",
            actor_nation="France",
            generate_baseline_when_empty=True,
        )
        assert preview.get("success"), preview
        sp = preview["settlement_preview"]
        terms = sp["settlement_terms"]
        validation = validate_settlement_terms(
            terms,
            proposer_side=sp["proposer_side"],
            covered_enemy_participants=sp["covered_enemy_participants"],
            world=losing_world,
            war_instance=losing_world.war_instances["war_1"],
        )
        assert validation.get("valid"), (validation, terms)
        # No region is promised twice (the V1 class).
        regions = [
            t.get("region") for t in terms if t.get("type") == "territory_cede"
        ]
        assert len(regions) == len(set(regions)), regions
        # No treasury double-spend (the budget class).
        committed = sum(
            int(t.get("amount", 0) or 0)
            for t in terms
            if t.get("type") in ("gold_indemnity", "gold_lump")
            and t.get("from") == "France"
        )
        assert committed <= int(losing_world.nation_gold.get("France", 0))
        # Honest bands: a losing table the treasury cannot fully satisfy is
        # holdouts with guidance, NOT a false carry.
        assert sp["overall_acceptance"]["carries"] is False

    def test_losing_baseline_splits_treasury_across_concede_courts(
        self, losing_world
    ):
        """D1: each concede court draws an even share of the ONE affordable
        treasury (`payer_balance - reserve`), never the full treasury each."""
        baseline = _losing_baseline(losing_world)
        balance = int(losing_world.nation_gold.get("France", 0))
        affordable = balance - CONCESSION_BASELINE_TREASURY_RESERVE
        per_court = baseline["per_court_baseline"]
        concede_courts = [
            court
            for court, entry in per_court.items()
            if entry.get("direction") == "concede"
        ]
        assert len(concede_courts) == 2, per_court
        share = affordable // len(concede_courts)
        gold_amounts = [
            int(t.get("amount", 0) or 0)
            for t in baseline["settlement_terms"]
            if t.get("type") == "gold_indemnity" and t.get("from") == "France"
        ]
        assert gold_amounts, baseline["settlement_terms"]
        assert all(amount <= share for amount in gold_amounts), gold_amounts
        assert sum(gold_amounts) <= affordable

    def test_generated_baseline_is_validated_before_staging_propose_and_submit(
        self, losing_world
    ):
        """D1/D2: both staging points hold the validity bar. The PROPOSE
        mount stages a validator-clean generated draft; the submit arm
        validates the draft BEFORE popping PROPOSE and re-attaches the
        still-mounted dialogue on failure instead of staging a poisoned
        REVIEW."""
        staged = _stage_losing_propose(losing_world)
        assert staged.get("success"), staged
        dialogue = staged["diplomatic_dialogue"]
        assert dialogue["dialogue_mode"] == "PROPOSE"
        validation = validate_settlement_terms(
            list(dialogue["settlement_terms"]),
            proposer_side=dialogue["proposer_side"],
            covered_enemy_participants=list(
                dialogue["covered_enemy_participants"]
            ),
            world=losing_world,
            war_instance=losing_world.war_instances["war_1"],
        )
        assert validation.get("valid"), validation

        # Submit arm: a tampered (D1-shaped) double-promise package must be
        # blocked at submit, with the mounted PROPOSE re-attached.
        tampered = dict(dialogue)
        tampered["settlement_terms"] = [
            {"type": "peace"},
            {"type": "territory_cede", "from": "France", "to": "Britain",
             "region": "Waterloo"},
            {"type": "territory_cede", "from": "France", "to": "Prussia",
             "region": "Waterloo"},
        ]
        result = handle_settlement_dialogue_action(
            losing_world,
            action="submit_settlement_for_review",
            dialogue=tampered,
            action_params={},
        )
        assert result["success"] is False
        assert result["error"] == "submitted_terms_failed_revalidation"
        assert result["validation_error"] == "region_double_promised"
        assert result.get("error_display")
        assert result.get("message")
        # Re-attach contract: the PROPOSE surface is still mounted and rides
        # back on the response; no REVIEW was staged.
        assert result.get("diplomatic_dialogue")
        mounted = losing_world.dialogue_manager.peek()
        assert mounted is not None
        assert str(mounted.get("dialogue_mode")) == "PROPOSE"


class TestBlockedRatifyVisibility:
    def test_blocked_ratify_reattaches_dialogue_with_error_display(
        self, losing_world
    ):
        """D2: the Submit→Ratify dead-end. A staged REVIEW whose terms fail
        the V1–V5 gate must keep the dialogue mounted and return it with a
        rendered reason — never pop into a no-popup "Response processed"
        loop."""
        staged = _stage_losing_propose(losing_world)
        dialogue = dict(staged["diplomatic_dialogue"])
        # Tamper the staged terms into the D1 double-promise shape so the
        # ratify-time V1–V5 defense-in-depth gate blocks.
        dialogue["settlement_terms"] = [
            {"type": "peace"},
            {"type": "territory_cede", "from": "France", "to": "Britain",
             "region": "Waterloo"},
            {"type": "territory_cede", "from": "France", "to": "Prussia",
             "region": "Waterloo"},
        ]
        losing_world.dialogue_manager.replace(dialogue)
        result = ratify_settlement_confirm(losing_world, dialogue)
        assert result["success"] is False
        assert result["error"] == "submitted_terms_failed_revalidation"
        assert result["mutated"] is False
        assert result.get("error_display")
        assert result.get("message")
        assert result["message"] != "Response processed"
        # The staged REVIEW stays mounted AND rides back on the response so
        # the popup re-mounts with the failure rendered.
        assert result.get("diplomatic_dialogue")
        assert losing_world.dialogue_manager.peek() is not None

    def test_dialogue_response_passes_handler_message_not_default(
        self, losing_world
    ):
        """D2: the HTTP boundary. A failing settlement action whose handler
        returns `error_display` but no `message` must NOT collapse to the
        literal "Response processed" — the player reads the real reason."""
        import backend.main as main_module

        main_module._set_active_world(losing_world)
        staged = _stage_losing_propose(losing_world)
        assert staged.get("success"), staged
        client = TestClient(main_module.app)
        response = client.post(
            "/respond_to_diplomatic_dialogue",
            json={
                "choice": "settlement_focus_court",
                "action_params": {
                    "action": "settlement_focus_court",
                    "nation": "Spain",
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert data.get("message"), data
        assert data["message"] != "Response processed"
        assert "Spain" in data["message"]
        # PF-1/D3: the failure fields ride the response for the client render.
        assert data.get("error_display")

    def test_failed_dial_renders_error_display_not_silent_noop(self):
        """D3 (Godot source pin): the proposal-confirm route attaches the
        failure to the re-mounted dialogue, and the settlement content
        renders it — a blocked dial is never a silent blink."""
        main_gd = (GODOT_SCRIPTS / "main.gd").read_text(encoding="utf-8")
        route_match = re.search(
            r"func _route_proposal_confirm_response\(response: Dictionary\):"
            r"(.*?)(?=\nfunc )",
            main_gd,
            re.DOTALL,
        )
        assert route_match, "missing _route_proposal_confirm_response"
        route_body = route_match.group(1)
        assert "transient_error_display" in route_body
        assert "error_display" in route_body
        # The injection only happens on failure responses.
        assert re.search(
            r"if not bool\(response\.get\(\"success\", true\)\)",
            route_body,
        )
        popup_gd = (GODOT_SCRIPTS / "proposal_confirm_popup.gd").read_text(
            encoding="utf-8"
        )
        content_match = re.search(
            r"func _build_settlement_content\(data: Dictionary\) -> String:"
            r"(.*?)(?=\nfunc )",
            popup_gd,
            re.DOTALL,
        )
        assert content_match, "missing _build_settlement_content"
        assert "transient_error_display" in content_match.group(1)


class TestAdvisoryAndConstraintGuidance:
    def test_advisory_never_presses_concede_direction_court(self):
        """D6: 'I'd press Britain, Prussia, Sire' on a war France is losing
        −85/−85. An accept-band court whose direction is `concede` is never
        a press candidate; demand-direction courts still are."""
        concede_rows = [
            {"nation": "Britain", "band": "accept", "total": 62,
             "direction": "concede"},
            {"nation": "Prussia", "band": "accept", "total": 62,
             "direction": "concede"},
        ]
        advisory = _settlement_targeted_posture_advisory(concede_rows, [])
        assert "press" not in advisory
        demand_rows = [
            {"nation": "Austria", "band": "accept", "total": 70,
             "direction": "demand"},
        ]
        advisory_demand = _settlement_targeted_posture_advisory(demand_rows, [])
        assert "press Austria" in advisory_demand

    def test_losing_fixture_advisory_does_not_press_the_winners(
        self, losing_world
    ):
        """D6 integration: on the real losing fixture the PROPOSE advisory
        never counsels pressing the courts that are beating France."""
        staged = _stage_losing_propose(losing_world)
        advisory = str(
            staged["diplomatic_dialogue"].get("targeted_posture_advisory") or ""
        )
        assert "press Britain" not in advisory
        assert "press Prussia" not in advisory

    def test_budget_bound_hint_pivots_to_binding_constraint(self):
        """D5/DC-2: when the next 'More generous' step would breach the
        treasury, the carry hint stops promising "ease until each accepts"
        (D3's silent wall) and names the real choice: drop a court or pay
        in land."""
        stub_world = SimpleNamespace(
            nation_gold={"France": 600},
            recurring_settlement_payments=[],
            regions={},
        )
        terms = [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 300},
            {"type": "gold_indemnity", "from": "France", "to": "Prussia",
             "amount": 300},
        ]
        rows = [
            {"nation": "Britain", "band": "near_acceptable", "total": 36,
             "direction": "concede"},
            {"nation": "Prussia", "band": "near_acceptable", "total": 36,
             "direction": "concede"},
        ]
        holdouts = ["Britain", "Prussia"]
        constraint = _settlement_budget_bound_constraint(
            stub_world,
            proposer_leader="France",
            per_court_acceptance=rows,
            holdout_courts=holdouts,
            settlement_terms=terms,
        )
        assert constraint.get("budget_bound") is True
        assert constraint.get("concede_holdouts") == ["Britain", "Prussia"]
        hint = _settlement_propose_carry_hint(
            holdouts, rows, budget_bound_constraint=constraint,
        )
        assert "More generous" not in hint
        assert "pay in land" in hint
        assert "Drop a court" in hint

    def test_budget_bound_constraint_silent_when_treasury_has_headroom(self):
        """The constraint binds exactly when the validator's budget rule
        would start failing dials — with headroom it stays out of the way."""
        stub_world = SimpleNamespace(
            nation_gold={"France": 5000},
            recurring_settlement_payments=[],
            regions={},
        )
        terms = [
            {"type": "peace"},
            {"type": "gold_indemnity", "from": "France", "to": "Britain",
             "amount": 300},
        ]
        rows = [
            {"nation": "Britain", "band": "near_acceptable", "total": 36,
             "direction": "concede"},
        ]
        constraint = _settlement_budget_bound_constraint(
            stub_world,
            proposer_leader="France",
            per_court_acceptance=rows,
            holdout_courts=["Britain"],
            settlement_terms=terms,
        )
        assert constraint == {}
        hint = _settlement_propose_carry_hint(
            ["Britain"], rows, budget_bound_constraint=constraint,
        )
        assert "More generous" in hint

    def test_budget_bound_voice_line_is_registered_committed_copy(self):
        """DC-2: the binding-constraint line is Voice Bible committed copy
        (resolved by template key), in Talleyrand's register."""
        line = resolve_settlement_voice_line(
            "settlement_budget_bound_constraint_talleyrand",
            holdout_names="Britain and Prussia",
        )
        assert line.startswith("Sire,")
        assert "Britain and Prussia" in line
        assert "pay" in line and "land" in line

    def test_submit_failure_voice_line_is_registered_committed_copy(self):
        """UX-6: error paths stay in character — the submit-failure line is
        committed copy, not a player-blaming default."""
        line = resolve_settlement_voice_line(
            "settlement_submit_failed_validation_talleyrand",
            war_label="the war with Britain",
            blocker="The same region cannot be promised to two different courts.",
        )
        assert line.startswith("Sire,")
        assert "promised to two different courts" in line
