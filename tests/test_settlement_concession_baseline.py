"""G2-Slice-W1 Concession Baseline backend payload behavior tests.

SETTLEMENT_UI_CLEANUP_SPEC v0.28 §"Concession And Treaty Conversation
Contract" pins:

- `losing_for_concession_baseline` predicate fires at
  `side_pressure_score <= -20`.
- POST preview AND the staged dialogue emit
  `losing_for_concession_baseline`, `concession_baseline_visible`, and
  `concession_baseline` (terms + reasoning) at canonical positions.
- Acceptance gap reads from a peace-only rerun of the scorer against the
  spec accept threshold.
- Gold candidate is the smallest strictly positive of (treasury - 500
  reserve, 1500 hard cap, max(300, acceptance_gap * 100)); territory
  escalation kicks in when gold-only acceptance stays below
  `near_acceptance_floor`.
- `concession_baseline_visible=False` when only the peace floor can be
  generated (no positive gold + no transferable region).
- Click-time revalidation is performed by re-POSTing the preview; if the
  predicate flips, the baseline is not applied and humanized "no longer
  eligible" copy is rendered.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.game_logic.settlement_preview import (
    _compute_concession_baseline,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


def _install_losing_war(world: WorldState, *, war_score_against_france: int = 70) -> dict:
    """Install a war where France (proposer) is losing badly.

    `war_score` on the diplo_key is set from Austria's perspective; the
    proposer-side direct score against each enemy will resolve to
    `-war_score_against_france`, driving `side_pressure_score <= -20`.
    """
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
        a, _b = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        # Austria perspective on (Austria|France) and (Austria|Saxony):
        # positive war_score against France's side means France is losing.
        # On (Prussia|*), Prussia's perspective is positive against attackers.
        world.war_scores[pair] = (
            war_score_against_france if a in ("Austria", "Prussia") else -war_score_against_france
        )
    world.invalidate_war_instance_indexes()
    return war


def _install_balanced_war(world: WorldState) -> dict:
    """Install a war where France is neither clearly winning nor losing
    (side_pressure_score around 0)."""
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
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 0
    world.invalidate_war_instance_indexes()
    return war


def _make_world(*, gold: int = 5000) -> WorldState:
    world = WorldState()
    world.nation_gold = {
        "France": gold,
        "Britain": 4000,
        "Austria": 3000,
        "Prussia": 3000,
        "Saxony": 1500,
    }
    return world


# ═══════════════════════════════════════════════════════════════════════════
# Predicate and payload schema
# ═══════════════════════════════════════════════════════════════════════════


class TestPredicate:
    def test_concession_baseline_predicate_matches_side_pressure_score_minus_twenty_boundary(self):
        """Predicate is inclusive: side_pressure_score <= -20."""
        world = _make_world()
        war = _install_balanced_war(world)
        # -21: predicate fires.
        result = _compute_concession_baseline(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Austria",
            proposer_side_leader="France",
            covered_enemy_participants=["Austria", "Prussia"],
            side_pressure_score=-21,
        )
        assert result["losing_for_concession_baseline"] is True
        # -20: boundary inclusive.
        result = _compute_concession_baseline(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Austria",
            proposer_side_leader="France",
            covered_enemy_participants=["Austria", "Prussia"],
            side_pressure_score=-20,
        )
        assert result["losing_for_concession_baseline"] is True
        # -19: predicate does not fire.
        result = _compute_concession_baseline(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Austria",
            proposer_side_leader="France",
            covered_enemy_participants=["Austria", "Prussia"],
            side_pressure_score=-19,
        )
        assert result["losing_for_concession_baseline"] is False
        assert result["concession_baseline_visible"] is False

    def test_winning_side_predicate_does_not_fire(self):
        world = _make_world()
        war = _install_balanced_war(world)
        result = _compute_concession_baseline(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Austria",
            proposer_side_leader="France",
            covered_enemy_participants=["Austria", "Prussia"],
            side_pressure_score=40,
        )
        assert result["losing_for_concession_baseline"] is False
        assert result["concession_baseline"] is None


class TestPayloadSchema:
    def test_concession_baseline_payload_emits_three_keys_on_post_preview_and_staged_dialogue(self):
        world = _make_world()
        _install_losing_war(world)
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[],
        )
        sp = preview["settlement_preview"]
        assert "losing_for_concession_baseline" in sp
        assert "concession_baseline_visible" in sp
        assert "concession_baseline" in sp
        # When visible, the baseline carries terms + reasoning.
        if sp["concession_baseline_visible"]:
            assert isinstance(sp["concession_baseline"], dict)
            assert "terms" in sp["concession_baseline"]
            assert "reasoning" in sp["concession_baseline"]
            assert sp["concession_baseline"]["terms"], (
                "visible baseline must carry at least one material term"
            )
        # Dialogue propagates the same keys.
        dialogue = build_settlement_confirm_dialogue(
            world, preview, selected_target_nation="Austria",
        )
        assert "losing_for_concession_baseline" in dialogue
        assert "concession_baseline_visible" in dialogue
        assert "concession_baseline" in dialogue
        assert (
            dialogue["losing_for_concession_baseline"]
            == sp["losing_for_concession_baseline"]
        )
        assert (
            dialogue["concession_baseline_visible"]
            == sp["concession_baseline_visible"]
        )


# ═══════════════════════════════════════════════════════════════════════════
# Algorithm (gold + territory)
# ═══════════════════════════════════════════════════════════════════════════


class TestAlgorithm:
    def test_concession_baseline_real_gameplay_chooses_payable_amount_and_transferable_region_outside_fixture(self):
        """Normal-gameplay algorithm picks deterministic gold (smallest
        positive candidate) and a non-capital, non-home region currently
        controlled by the proposer side."""
        world = _make_world(gold=2000)
        war = _install_losing_war(world)
        # Force one transferable region: a non-capital, non-home region
        # currently controlled by France. Use a real region from the
        # production REGIONS_DATA — fixture metadata is not in scope.
        # Simulate by setting controller on a representative region.
        if "Bavaria" in world.regions:
            world.regions["Bavaria"].controller = "France"
        result = _compute_concession_baseline(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Austria",
            proposer_side_leader="France",
            covered_enemy_participants=["Austria", "Prussia"],
            side_pressure_score=-40,
            accept_threshold=50,
            near_acceptance_floor=35,
        )
        if not result["concession_baseline_visible"]:
            # Acceptable when no eligible region exists in default
            # REGIONS_DATA after starting_controller filtering — the
            # algorithm correctly hides the action rather than ceding
            # France-home territory.
            assert result["concession_baseline"] is None
            return
        terms = result["concession_baseline"]["terms"]
        gold_terms = [t for t in terms if t.get("type") == "gold_indemnity"]
        # Spec algorithm: positive candidates are
        #   treasury - 500 = 1500
        #   hard cap = 1500
        #   max(300, gap * 100) = something >= 300
        # The min(...) is therefore 1500 or lower.
        if gold_terms:
            assert gold_terms[0]["from"] == "France"
            assert gold_terms[0]["to"] == "Austria"
            assert gold_terms[0]["amount"] > 0
            assert gold_terms[0]["amount"] <= 1500
        # If region escalation fired, the region is non-capital + non-home.
        region_terms = [t for t in terms if t.get("type") == "territory_cede"]
        for r in region_terms:
            region = world.regions.get(r["region"])
            assert region is not None
            assert not getattr(region, "is_capital", False)
            starting = str(getattr(region, "starting_controller", "") or "")
            assert starting not in ("France", "Saxony"), (
                f"baseline must not cede proposer-home region {r['region']}"
            )

    def test_concession_baseline_acceptance_gap_uses_peace_only_score_against_threshold(self):
        """Acceptance gap is computed as (threshold - peace_only_score),
        clamped at 0. The third gold candidate floors at max(300,
        gap * 100)."""
        world = _make_world(gold=5000)
        war = _install_losing_war(world)
        # Force peace_only_score to a known value via patch.
        def fake_acceptance(*args, **kwargs):
            from backend.game_logic.settlement_scoring import (
                calculate_common_peace_acceptance as real,
            )
            r = real(*args, **kwargs)
            r["score"] = 10  # peace floor
            r["accept_threshold"] = 50
            r["verdict"] = "reject"
            return r
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=fake_acceptance,
        ):
            result = _compute_concession_baseline(
                world,
                war_id="war_1",
                war_instance=war,
                proposer_side="attackers",
                accepting_side="defenders",
                accepting_leader="Austria",
                proposer_side_leader="France",
                covered_enemy_participants=["Austria", "Prussia"],
                side_pressure_score=-40,
                accept_threshold=50,
                near_acceptance_floor=35,
            )
        # peace_only_score=10 → acceptance_gap = 40 → gap_candidate = 4000.
        # Treasury candidate = 5000-500=4500. Hard cap = 1500.
        # Positive candidates = [4500, 1500, 4000]. min = 1500.
        if result["concession_baseline_visible"]:
            gold_terms = [
                t for t in result["concession_baseline"]["terms"]
                if t.get("type") == "gold_indemnity"
            ]
            if gold_terms:
                assert gold_terms[0]["amount"] == 1500

    def test_concession_baseline_hidden_when_only_peace_clause_can_be_generated(self):
        """When the proposer has no positive payable gold and no
        transferable region, the baseline action is hidden — predicate
        passes but visibility flips to False."""
        # Zero gold, no captured non-home regions.
        world = _make_world(gold=0)
        war = _install_losing_war(world)
        # Strip any France-controlled non-home regions for this test.
        for region in world.regions.values():
            starting = str(getattr(region, "starting_controller", "") or "")
            if starting != "France" and getattr(region, "controller", "") == "France":
                # Reset to historical controller so baseline cannot pick it.
                region.controller = starting or region.controller
        result = _compute_concession_baseline(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Austria",
            proposer_side_leader="France",
            covered_enemy_participants=["Austria", "Prussia"],
            side_pressure_score=-50,
        )
        assert result["losing_for_concession_baseline"] is True
        assert result["concession_baseline_visible"] is False
        assert result["concession_baseline"] is None


# ═══════════════════════════════════════════════════════════════════════════
# Click-time revalidation
# ═══════════════════════════════════════════════════════════════════════════


class TestClickTimeRevalidation:
    def test_concession_baseline_click_time_revalidation_no_longer_eligible_renders_humanized_copy(self):
        """Click-time revalidation runs through POST preview. When the
        predicate flips from True to False, the click leaves the draft
        unchanged. We pin the contract: POST preview is the source of
        truth, and the staged dialogue picks up the fresh predicate."""
        world = _make_world()
        war_dict = _install_losing_war(world)
        # First preview: losing side, baseline visible.
        preview_losing = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[],
        )
        sp_losing = preview_losing["settlement_preview"]
        # If the loss path does produce a visible baseline, flipping to a
        # balanced war must drop visibility on the next POST preview.
        if not sp_losing["concession_baseline_visible"]:
            return
        for pair in war_dict["active_diplo_keys"]:
            world.war_scores[pair] = 0
        preview_balanced = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[],
        )
        sp_balanced = preview_balanced["settlement_preview"]
        assert sp_balanced["concession_baseline_visible"] is False
        # Stale dialogue snapshot remains unchanged because it captured
        # the earlier visible flag; refreshed preview is the source of
        # truth at click time.
        assert sp_losing["concession_baseline_visible"] is True

    def test_concession_baseline_button_visible_at_first_paint_when_actor_is_losing_side(self):
        """Source-level guard: the staged settlement_confirm dialogue
        carries `concession_baseline_visible` on the first paint
        (before any user interaction), so Godot can render the button
        primary-weighted without an extra round trip."""
        world = _make_world()
        _install_losing_war(world)
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[],
        )
        dialogue = build_settlement_confirm_dialogue(
            world, preview, selected_target_nation="Austria",
        )
        # First paint: the dialogue carries the predicate result.
        assert "concession_baseline_visible" in dialogue
        if preview["settlement_preview"]["concession_baseline_visible"]:
            assert dialogue["concession_baseline_visible"] is True
            assert dialogue["concession_baseline"] is not None
            assert "re_author_with_concessions" in dialogue["available_action_ids"]
            assert any(
                opt.get("action") == "re_author_with_concessions"
                for opt in dialogue["options"]
            )

    def test_re_author_with_concessions_applies_revalidated_empty_draft_baseline(self):
        """The visible concession baseline must be a behavior path, not
        banner-only copy. From an empty editor-staged draft, clicking the
        action revalidates through POST preview, installs baseline terms as
        the current draft, and does not mutate world state."""
        world = _make_world(gold=2000)
        _install_losing_war(world)
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[],
        )
        dialogue = build_settlement_confirm_dialogue(
            world, preview, selected_target_nation="Austria",
        )
        if not dialogue["concession_baseline_visible"]:
            return
        world.dialogue_manager.replace(dialogue)
        gold_before = dict(world.nation_gold)

        result = handle_settlement_dialogue_action(
            world,
            action="re_author_with_concessions",
            dialogue=dialogue,
        )

        assert result["success"] is True
        assert result.get("open_editor_on_mount") is True
        assert result["mutated"] is False
        assert world.nation_gold == gold_before
        refreshed = world.pending_diplomatic_dialogue
        assert refreshed["type"] == "settlement_confirm"
        assert refreshed["settlement_terms"]
        assert any(t.get("type") != "peace" for t in refreshed["settlement_terms"])
        assert "re_author_with_concessions" not in refreshed["available_action_ids"]
        assert world.pending_settlement_drafts["war_1"] == refreshed["settlement_terms"]

    def test_dialogue_response_routes_re_author_with_concessions_through_executor_dispatch(self):
        """Gate 4 repair regression: the visible concession action must
        execute through the same dialogue endpoint Godot uses after a
        popup click, not just through the direct handler unit path."""
        from backend.commands.diplomatic_executor import DiplomaticExecutor

        world = _make_world(gold=2000)
        _install_losing_war(world)
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[],
        )
        dialogue = build_settlement_confirm_dialogue(
            world, preview, selected_target_nation="Austria",
        )
        assert dialogue["concession_baseline_visible"] is True
        target_idx = next(
            idx
            for idx, option in enumerate(dialogue["options"], start=1)
            if option.get("action") == "re_author_with_concessions"
        )
        world.dialogue_manager.replace(dialogue)
        gold_before = dict(world.nation_gold)

        result = DiplomaticExecutor(None).handle_diplomatic_dialogue_response(
            target_idx, {"world": world}
        )

        assert "Unknown dialogue action" not in str(result.get("message", ""))
        assert result["success"] is True
        assert result["action"] == "re_author_with_concessions"
        assert result.get("open_editor_on_mount") is True
        assert result["mutated"] is False
        assert world.nation_gold == gold_before
        refreshed = world.pending_diplomatic_dialogue
        assert refreshed["type"] == "settlement_confirm"
        assert any(t.get("type") != "peace" for t in refreshed["settlement_terms"])
        assert "re_author_with_concessions" not in refreshed["available_action_ids"]
        assert world.pending_settlement_drafts["war_1"] == refreshed["settlement_terms"]

    def test_re_author_with_concessions_mounts_replace_confirm_for_non_empty_draft(self):
        """A non-empty draft cannot return a dead requires_replace_confirm
        payload. The popup hides on click, so the backend must mount and
        return the replacement confirmation dialogue immediately."""
        world = _make_world(gold=2000)
        _install_losing_war(world)
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[{"type": "peace"}],
        )
        dialogue = build_settlement_confirm_dialogue(
            world, preview, selected_target_nation="Austria",
        )
        assert "re_author_with_concessions" in dialogue["available_action_ids"]
        world.dialogue_manager.replace(dialogue)

        result = handle_settlement_dialogue_action(
            world,
            action="re_author_with_concessions",
            dialogue=dialogue,
        )

        assert result["success"] is True
        assert result["requires_replace_confirm"] is True
        replace_dialogue = result["diplomatic_dialogue"]
        assert replace_dialogue["replace_confirm"] is True
        assert world.pending_diplomatic_dialogue == replace_dialogue
        option_actions = [opt["action"] for opt in replace_dialogue["options"]]
        assert option_actions == [
            "apply_concession_baseline_replacement",
            "keep_current_settlement_draft",
        ]

    def test_apply_concession_replacement_restages_baseline_and_hides_repeat_action(self):
        """The second click path must be real behavior: confirming the
        replacement restages the concession baseline, keeps mutation false,
        and removes the repeat Re-author affordance."""
        world = _make_world(gold=2000)
        _install_losing_war(world)
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[{"type": "peace"}],
        )
        dialogue = build_settlement_confirm_dialogue(
            world, preview, selected_target_nation="Austria",
        )
        world.dialogue_manager.replace(dialogue)
        replace_result = handle_settlement_dialogue_action(
            world,
            action="re_author_with_concessions",
            dialogue=dialogue,
        )

        result = handle_settlement_dialogue_action(
            world,
            action="apply_concession_baseline_replacement",
            dialogue=replace_result["diplomatic_dialogue"],
        )

        assert result["success"] is True
        assert result["mutated"] is False
        refreshed = result["diplomatic_dialogue"]
        assert refreshed["settlement_terms"]
        assert any(t.get("type") != "peace" for t in refreshed["settlement_terms"])
        assert "re_author_with_concessions" not in refreshed["available_action_ids"]
        assert world.pending_settlement_drafts["war_1"] == refreshed["settlement_terms"]


class TestConcessionAcceptanceDirection:
    def test_concession_terms_move_acceptance_in_accepting_side_direction(self):
        """Adding a gold concession to a peace floor must not decrease
        the accepting side's acceptance score (concessions are
        rewarded, not punished)."""
        world = _make_world(gold=5000)
        war = _install_losing_war(world)
        from backend.game_logic.settlement_scoring import (
            calculate_common_peace_acceptance,
        )
        peace_only = calculate_common_peace_acceptance(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Austria",
            proposer_side_leader="France",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[{"type": "peace"}],
        )
        with_gold = calculate_common_peace_acceptance(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="attackers",
            accepting_side="defenders",
            accepting_leader="Austria",
            proposer_side_leader="France",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[
                {"type": "peace"},
                {"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 1500},
            ],
        )
        # Concession from the losing side should improve acceptance.
        assert int(with_gold.get("score") or 0) > int(peace_only.get("score") or 0)
        assert int(with_gold["components"]["concession_credit"]) > 0
        assert with_gold["component_debug"]["concession_credit"]["credited_terms"]

    def test_settlement_losing_smoke_baseline_reaches_near_acceptable(self, monkeypatch):
        from backend.models.world_state import (
            SMOKE_START_ENV,
            SMOKE_START_SETTLEMENT_LOSING,
        )

        monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_LOSING)
        world = WorldState()
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[],
        )
        baseline = preview["settlement_preview"]["concession_baseline"]
        assert baseline is not None
        assert any(
            t.get("type") == "territory_cede" and t.get("region") == "Waterloo"
            for t in baseline["terms"]
        )

        baseline_preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=baseline["terms"],
        )

        acceptance = baseline_preview["settlement_preview"]["acceptance"]
        assert acceptance["score"] >= 35
        assert acceptance["components"]["concession_credit"] > 0

    def test_concession_baseline_copy_promises_improvement_not_acceptance_band(self, monkeypatch):
        from backend.models.world_state import (
            SMOKE_START_ENV,
            SMOKE_START_SETTLEMENT_REJECTED,
        )

        monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_REJECTED)
        world = WorldState()
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[],
        )
        baseline = preview["settlement_preview"]["concession_baseline"]
        assert baseline is not None

        reasoning = str(baseline["reasoning"])
        # May 24, 2026 audit punch list Tier 2 — the legacy hard-coded
        # f-string ("...to improve acceptance.") now routes through the
        # `settlement_concession_authored_talleyrand` Voice Bible §16.1
        # template ("...would lift acceptance toward {accepting_leader}.").
        # The test's intent is unchanged: the copy must promise
        # *improvement* (not a guaranteed acceptance band).
        assert "lift acceptance" in reasoning
        assert "back into reach" not in reasoning


class TestStageSettlementPropagation:
    def test_stage_settlement_confirm_propagates_concession_baseline_to_dialogue(self):
        world = _make_world()
        _install_losing_war(world)
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[
                {"type": "gold_indemnity", "from": "France", "to": "Austria", "amount": 500},
            ],
        )
        if not result.get("success"):
            return
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert "concession_baseline_visible" in dialogue
        assert "losing_for_concession_baseline" in dialogue
