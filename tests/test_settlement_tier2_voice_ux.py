"""May 24, 2026 audit punch list Tier 2 - voice/UX wiring behavior tests.

Behavior coverage for the 5 backend wiring changes and the 2 Godot
render changes landed in the May 24, 2026 audit punch list Tier 2:

Backend (Python):

- (A) 4 missing Voice Bible §16.1 templates are registered:
  `settlement_white_peace_heading_talleyrand`,
  `settlement_white_peace_blocked_talleyrand`,
  `settlement_concession_authored_talleyrand`,
  `settlement_losing_side_pressure_explained_talleyrand`.
- (B) 2 existing templates now route through `resolve_settlement_voice_line`
  at their preset helpers instead of hard-coded f-strings:
  `settlement_surrender_preset_authored_talleyrand` at
  `_compute_surrender_preset` and
  `settlement_recurring_gold_authored_talleyrand` at
  `_compute_recurring_gold_preset`. We assert the Voice Bible signature
  text reaches the `reasoning` field rather than the legacy
  ``"Talleyrand's draft: ..."`` opening.
- The concession-baseline reasoning at `_format_concession_reasoning`
  routes through `settlement_concession_authored_talleyrand`.
- The settlement-confirm dialogue surfaces a new
  `losing_side_pressure_voice` field resolved through
  `settlement_losing_side_pressure_explained_talleyrand` when the
  player is on the losing concession-baseline side, and an empty
  string otherwise.

Godot (source-level scan):

- (C) `proposal_confirm_popup.gd::_build_settlement_content` reads
  `terminal_recovery_copy` from the staged-dialogue payload and renders
  it directly after the `ratify_blocked_reason` block.
- (D) `diplomacy_wizard.gd::_add_action_button` renders an in-wizard
  per-war picker when an action carries
  `error == "multi_war_ambiguity"` and a non-empty `available_wars`
  list; each picker button forwards `_on_action_selected` with the
  original `action_id` and a payload clone carrying the chosen
  `war_id`, which `_structured_payload_for_action` then routes back to
  the backend.

These tests are deliberately co-located in one bundle because they
share the same Tier-2 landing story; they should remain a single
audit-traceable focus suite rather than scattered across the broader
settlement test files.
"""

from __future__ import annotations

import pathlib
from typing import Any, Mapping
from unittest.mock import patch

import pytest

from backend.game_logic.diplomatic_templates import (
    SETTLEMENT_VOICE_TEMPLATES,
    resolve_settlement_voice_line,
)
from backend.game_logic.settlement_preview import (
    _compute_recurring_gold_preset,
    _compute_surrender_preset,
    _format_concession_reasoning,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


# ─────────────────────────────────────────────────────────────────────────────
# (A) Template registration
# ─────────────────────────────────────────────────────────────────────────────


class TestTier2TemplatesRegistered:
    """The 4 missing Voice Bible §16.1 settlement templates must exist."""

    def test_settlement_white_peace_heading_talleyrand_template_registered(self):
        assert "settlement_white_peace_heading_talleyrand" in SETTLEMENT_VOICE_TEMPLATES
        line = resolve_settlement_voice_line(
            "settlement_white_peace_heading_talleyrand",
            war_label="France vs Britain",
        )
        assert line, "template must resolve to non-empty copy"
        assert "France vs Britain" in line
        # Sire-form Talleyrand voice register per Voice Bible §16.1.
        assert "Sire" in line

    def test_settlement_white_peace_blocked_talleyrand_template_registered(self):
        assert "settlement_white_peace_blocked_talleyrand" in SETTLEMENT_VOICE_TEMPLATES
        line = resolve_settlement_voice_line(
            "settlement_white_peace_blocked_talleyrand",
            war_label="France vs Britain",
            top_blocker="no settlement terms authored",
        )
        assert line
        assert "France vs Britain" in line
        assert "no settlement terms authored" in line
        assert "Sire" in line

    def test_settlement_concession_authored_talleyrand_template_registered(self):
        assert "settlement_concession_authored_talleyrand" in SETTLEMENT_VOICE_TEMPLATES
        line = resolve_settlement_voice_line(
            "settlement_concession_authored_talleyrand",
            summary="France would pay Britain 500 gold",
            accepting_leader="Britain",
        )
        assert line
        assert "France would pay Britain 500 gold" in line
        assert "Britain" in line
        assert "Sire" in line

    def test_settlement_losing_side_pressure_explained_talleyrand_template_registered(self):
        assert (
            "settlement_losing_side_pressure_explained_talleyrand"
            in SETTLEMENT_VOICE_TEMPLATES
        )
        line = resolve_settlement_voice_line(
            "settlement_losing_side_pressure_explained_talleyrand",
            war_label="France vs Britain",
            top_pressure_label="war exhaustion",
            accepting_leader="Britain",
        )
        assert line
        assert "France vs Britain" in line
        assert "war exhaustion" in line
        assert "Britain" in line
        assert "Sire" in line


# ─────────────────────────────────────────────────────────────────────────────
# (B) Preset helper reasoning routes through the template resolver
# ─────────────────────────────────────────────────────────────────────────────


def _install_basic_war(
    world: WorldState,
    *,
    accepting_leader: str = "Britain",
    proposer_leader: str = "France",
    accepting_side: str = "defenders",
    proposer_side: str = "attackers",
) -> Mapping[str, Any]:
    war = make_synthetic_war_instance(
        "war_1",
        attackers=[proposer_leader],
        defenders=[accepting_leader],
        attacker_leader=proposer_leader,
        defender_leader=accepting_leader,
        created_turn=2,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 0
        world.battle_records[pair] = []
    world.current_turn = 5
    world.invalidate_war_instance_indexes()
    return war


class TestTier2PresetReasoningRoutesThroughResolver:
    """Surrender + recurring-gold preset reasoning must hit the templates."""

    def test_surrender_preset_reasoning_routes_through_template_not_fstring(self):
        # Stub eligibility so `_compute_surrender_preset` reaches the
        # reasoning branch deterministically without standing up the
        # full dependency-eligibility chain.
        def _stub_eligible(*_args, **_kwargs):
            return {"eligible": True}

        world = WorldState()
        war = _install_basic_war(world)

        with patch(
            "backend.game_logic.settlement_baseline.evaluate_subjugation_eligibility",
            _stub_eligible,
        ):
            result = _compute_surrender_preset(
                world,
                war_id="war_1",
                war_instance=war,
                proposer_side="attackers",
                accepting_side="defenders",
                accepting_leader="Britain",
                proposer_side_leader="France",
                covered_enemy_participants=["Britain"],
                side_pressure_score=-50,
            )

        assert result["surrender_preset_visible"] is True
        reasoning = str(result["surrender_preset"]["reasoning"])
        expected_voice = resolve_settlement_voice_line(
            "settlement_surrender_preset_authored_talleyrand",
            war_label="war_1",
            vassal_kind="conquest vassal",
            proposer_leader="France",
            accepting_leader="Britain",
        )
        assert reasoning == expected_voice
        # Voice Bible signature: surrender_preset_authored opens with
        # "Sire, the surrender draft for ...". The pre-Tier-2 f-string
        # opened with "Talleyrand's draft: ..." — that legacy opening
        # must not appear.
        assert reasoning.startswith("Sire, the surrender draft for war_1")
        assert "conquest vassal" in reasoning
        assert "Talleyrand's draft:" not in reasoning

    def test_recurring_gold_preset_reasoning_routes_through_template_not_fstring(self):
        world = WorldState()
        war = _install_basic_war(world)
        world.nation_gold["France"] = 5000
        # Smoke fixture metadata feeds the preset's amount + turns.
        world.settlement_smoke_fixture = {
            "expected_recurring_amount_min": 50,
            "expected_recurring_turns_min": 3,
        }
        result = _compute_recurring_gold_preset(
            world,
            war_instance=war,
            proposer_side_leader="France",
            accepting_leader="Britain",
            covered_enemy_participants=["Britain"],
            side_pressure_score=-50,
        )

        assert result["recurring_gold_preset_visible"] is True
        reasoning = str(result["recurring_gold_preset"]["reasoning"])
        amount = int(result["recurring_gold_preset"]["amount"])
        turns = int(result["recurring_gold_preset"]["turns"])
        projected_total = amount * turns
        expected_voice = resolve_settlement_voice_line(
            "settlement_recurring_gold_authored_talleyrand",
            payer="France",
            amount_per_turn=str(amount),
            recipient="Britain",
            turns=str(turns),
            projected_total=str(projected_total),
        )
        assert reasoning == expected_voice
        assert reasoning.startswith("Sire, the draft commits France")
        # Projected-total framing the Voice Bible template added must
        # reach the player; the pre-Tier-2 f-string omitted the
        # "({projected_total} gold in total)" phrase entirely.
        assert str(projected_total) in reasoning
        assert "Talleyrand's draft:" not in reasoning

    def test_concession_baseline_reasoning_routes_through_template_not_fstring(self):
        # Direct unit test of the helper — keeps the assertion focused
        # on the template wiring rather than the full settlement
        # preview pipeline.
        reasoning = _format_concession_reasoning(
            proposer_leader="France",
            accepting_leader="Britain",
            gold_amount=500,
            region=None,
        )
        expected = resolve_settlement_voice_line(
            "settlement_concession_authored_talleyrand",
            summary="France would pay Britain 500 gold",
            accepting_leader="Britain",
        )
        assert reasoning == expected
        assert reasoning.startswith("Sire, the concession draft")
        assert "France would pay Britain 500 gold" in reasoning
        assert "Talleyrand's draft:" not in reasoning


# ─────────────────────────────────────────────────────────────────────────────
# `losing_side_pressure_voice` field on the staged dialogue
# ─────────────────────────────────────────────────────────────────────────────


class TestTier2LosingSidePressureVoiceField:
    """Settlement-confirm dialogue must expose the new field correctly."""

    def _losing_preview_response(self) -> dict:
        """Build a minimal `preview_response` dict shape sufficient for
        `build_settlement_confirm_dialogue` to reach the
        `losing_side_pressure_voice` branch deterministically without
        standing up the full POST preview pipeline."""
        return {
            "war_id": "war_1",
            "settlement_preview": {
                "war_id": "war_1",
                "war_label": "France vs Britain",
                "proposer_side": "attackers",
                "accepting_side": "defenders",
                "war_instance": {
                    "war_id": "war_1",
                    "attacker_leader": "France",
                    "defender_leader": "Britain",
                    "attackers": ["France"],
                    "defenders": ["Britain"],
                    "active_diplo_keys": ["Britain|France"],
                },
                # Non-empty term avoids the editor empty-Ratify gate that
                # would otherwise overwrite `top_blocker_display` with the
                # "no settlement terms authored" sentinel and obscure the
                # losing-side pressure component the test is pinning.
                "settlement_terms": [{"type": "peace"}],
                "covered_enemy_participants": ["Britain"],
                "selected_target_nation": "Britain",
                "acceptance": {
                    "score": 20,
                    "verdict": "near_acceptable",
                    "band": "near_acceptable",
                    "threshold": 50,
                    "top_components": [
                        {
                            "component": "war_exhaustion",
                            "component_display": "war exhaustion",
                            "value": -25,
                        },
                    ],
                },
                "acceptance_components": {},
                "warnings": [],
                "hard_stops": [],
                "review_sections": {
                    "sections": {"acceptance": {}},
                    "coverage_scope_display": "",
                    "war_scope_display": "",
                    "covered_enemy_display_chips": [],
                    "uncovered_enemy_display_chips": [],
                },
                "losing_for_concession_baseline": True,
                "concession_baseline_visible": False,
                "concession_baseline": None,
                "losing_for_surrender_preset": False,
                "surrender_preset_visible": False,
                "surrender_preset": None,
                "surrender_preset_reason": "",
                "losing_for_recurring_gold_preset": False,
                "recurring_gold_preset_visible": False,
                "recurring_gold_preset": None,
                "recurring_gold_preset_reason": "",
                "forced_alliance_continental_toggle_differential": {},
            },
        }

    def test_losing_side_pressure_voice_emitted_on_dialogue_when_losing(self):
        world = WorldState()
        _install_basic_war(world)
        preview_response = self._losing_preview_response()
        dialogue = build_settlement_confirm_dialogue(
            world,
            preview_response,
            caller_kind="player_editor",
            white_peace=False,
        )
        voice = str(dialogue.get("losing_side_pressure_voice", ""))
        assert voice, "losing_side_pressure_voice must be populated when losing"
        # Voice Bible §16.1 signature for losing-side-pressure family.
        assert "war exhaustion" in voice
        assert "Britain" in voice
        assert "Sire" in voice

    def test_losing_side_pressure_voice_empty_when_not_losing(self):
        world = WorldState()
        _install_basic_war(world)
        preview_response = self._losing_preview_response()
        # Flip the predicate to false — Talleyrand should not narrate
        # losing-side pressure when the player is not losing.
        preview_response["settlement_preview"]["losing_for_concession_baseline"] = False
        dialogue = build_settlement_confirm_dialogue(
            world,
            preview_response,
            caller_kind="player_editor",
            white_peace=False,
        )
        assert dialogue.get("losing_side_pressure_voice", "") == ""


# ─────────────────────────────────────────────────────────────────────────────
# (C) + (D) Godot source-level guards
# ─────────────────────────────────────────────────────────────────────────────


GODOT_ROOT = pathlib.Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign" / "scripts"


class TestTier2GodotRenderWiring:
    """Source-level scans pinning the Godot changes to the contract."""

    def test_godot_proposal_confirm_popup_renders_terminal_recovery_copy_after_ratify_blocked_reason(self):
        path = GODOT_ROOT / "proposal_confirm_popup.gd"
        text = path.read_text(encoding="utf-8")
        idx_blocked = text.find("ratify_blocked_reason + \"[/color]\\n\"")
        idx_terminal = text.find(
            "var terminal_recovery_copy = str(data.get(\"terminal_recovery_copy\", \"\"))"
        )
        assert idx_blocked >= 0, "ratify_blocked_reason render must still exist"
        assert idx_terminal >= 0, "terminal_recovery_copy must be read from data"
        assert (
            idx_blocked < idx_terminal
        ), "terminal_recovery_copy must render AFTER ratify_blocked_reason"
        # The render itself must be a bbcode-formatted line so the
        # popup actually shows the chancery recovery copy when the
        # backend emits a non-empty string.
        assert "[i]\" + terminal_recovery_copy + \"[/i]" in text

    def test_godot_diplomacy_wizard_renders_multi_war_ambiguity_picker(self):
        path = GODOT_ROOT / "diplomacy_wizard.gd"
        text = path.read_text(encoding="utf-8")
        # The picker detection branch must guard on the literal backend
        # error code so a future renaming on either side is caught.
        assert (
            'error_code == "multi_war_ambiguity"' in text
        ), "wizard must detect the multi_war_ambiguity error code literally"
        # The picker must read `available_wars` from the action payload.
        assert (
            'action.get("available_wars", [])' in text
        ), "wizard must read available_wars from the action"
        # Each picker button must forward `_on_action_selected` so the
        # standard wizard dispatch (with `_structured_payload_for_action`
        # forwarding the chosen `war_id` to the backend) is reused
        # rather than a bespoke handler.
        assert (
            "war_btn.pressed.connect(_on_action_selected.bind(action_id, picker_payload))"
            in text
        ), "picker buttons must reuse _on_action_selected"
        # Picker payload must inject the chosen war_id so the
        # structured-payload forwarder routes it back to the backend.
        assert (
            'picker_payload["war_id"] = war_str' in text
        ), "picker payload must carry the chosen war_id"
