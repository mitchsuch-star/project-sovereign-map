"""Settlement staging payload + scoped-draft persistence contract
(SC-5R-1 lineage, re-homed by GT-Slice-4).

GT-Slice-4 retired the SC-5R-1 EDIT payload contract with the freeform
editor: no staging path may publish `can_edit_terms` /
`available_clause_types[]` / `clause_control_schema` / `editor_route`
anymore (the guided per-court rows carry their own GT-Slice-2 authoring
payload). What this bundle still pins:

- ABSENCE: the retired editor keys appear on NO staged
  `settlement_confirm` (player, AI-offer-accept, any caller), and
  `dialogue_mode` defaults to REVIEW (PROPOSE is requested explicitly).
- `pending_settlement_drafts_by_key` round-trips through save/load with
  scoped draft_key keys; same-war drafts with different selected
  targets or covered scope do not collide.
- `_execute_propose_common_peace` persists the staged PROPOSE draft to
  the scoped store so reopen / War Detail recovery can resolve by
  `draft_key`; a failed open persists nothing.
- `author_gold_indemnity_terms` produces schema-valid `gold_indemnity`
  clauses (no `turns` key — the previous draft included `turns: 0`
  which the validator rejects as `invalid_clause_schema`).
- A tampered `voluntary_alliance` clause is rejected pre-staging by
  `_stage_replacement_settlement_terms` AND pre-ratification by
  `ratify_settlement_confirm`, so the cut clause type never reaches
  treaty history.
"""

from __future__ import annotations

from unittest.mock import patch

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.settlement_preview import (
    compute_settlement_draft_key,
    discard_scoped_settlement_draft,
    handle_settlement_dialogue_action,
    handle_incoming_settlement_offer_action,
    load_scoped_settlement_draft,
    ratify_settlement_confirm,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


# CH-1 stable-seam note: the scorer is patched at
# backend.game_logic.settlement_scoring.calculate_common_peace_acceptance,
# so wrap-the-real side effects must capture the real function at import
# time (a lazy import inside the side effect would fetch the mock).
from backend.game_logic.settlement_scoring import (
    calculate_common_peace_acceptance as _REAL_COMMON_PEACE_ACCEPTANCE,
)


def _install_common_peace_war(world: WorldState, *, war_score: int = 70) -> dict:
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
        world.war_scores[pair] = war_score if a == "Austria" else -war_score
    world.war_exhaustion["Austria"] = 30
    world.invalidate_war_instance_indexes()
    return war


def _acceptance_accepts(*args, **kwargs):
    real = _REAL_COMMON_PEACE_ACCEPTANCE
    result = real(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    result["side_pressure_score"] = 70
    return result


def _gold_indemnity_clause(amount: int = 200) -> dict:
    return {
        "type": "gold_indemnity",
        "from": "Austria",
        "to": "France",
        "amount": amount,
    }


# ═══════════════════════════════════════════════════════════════════════════
# A. EDIT payload contract on `settlement_confirm`
# ═══════════════════════════════════════════════════════════════════════════


class TestSettlementConfirmGuidedPayloadContract:
    """GT-Slice-4: the SC-5R-1 EDIT payload contract (`can_edit_terms` /
    `available_clause_types[]` / `clause_control_schema` / `editor_route`)
    is retired with the freeform editor. The replacement contract is an
    ABSENCE pin — no staging path may advertise an editor surface — plus
    the surviving `dialogue_mode` default."""

    def test_settlement_confirm_publishes_dialogue_mode_review(self):
        """`dialogue_mode` defaults to REVIEW on `settlement_confirm`;
        the guided authoring entry requests PROPOSE explicitly."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[{"type": "peace"}, _gold_indemnity_clause()],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        dialogue = staged["diplomatic_dialogue"]
        assert dialogue["dialogue_mode"] == "REVIEW"

    def test_edit_payload_contract_keys_absent_for_player_staging(self):
        """The retired editor keys must be ABSENT (not merely falsy) on a
        player-staged settlement_confirm — clients can no longer be offered
        an editor handoff anywhere."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[{"type": "peace"}, _gold_indemnity_clause()],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        dialogue = staged["diplomatic_dialogue"]
        for retired_key in (
            "can_edit_terms",
            "available_clause_types",
            "clause_control_schema",
            "editor_route",
        ):
            assert retired_key not in dialogue, retired_key

    def test_accepting_incoming_ai_offer_stages_non_player_caller_without_editor_keys(self):
        """Accepting an AI-authored offer is not the outgoing player
        authoring path: it stages with `caller_kind="ai_system"` and, like
        every other path, carries none of the retired editor keys."""
        world = WorldState()
        _install_common_peace_war(world)
        offer = {
            "type": "incoming_settlement_offer",
            "dialogue_type": "incoming_settlement_offer",
            "offer_id": "settlement_offer:war_1:1:1",
            "war_id": "war_1",
            "proposer_nation": "Austria",
            "proposer_side": "defenders",
            "accepting_side": "attackers",
            "covered_enemy_participants": ["Austria", "Prussia"],
            "settlement_terms": [
                {"type": "peace"},
                {
                    "type": "gold_indemnity",
                    "from": "France",
                    "to": "Austria",
                    "amount": 100,
                },
            ],
        }
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = handle_incoming_settlement_offer_action(
                world, action="accept_settlement_offer", dialogue=offer,
            )
        assert result["success"] is True
        dialogue = result["diplomatic_dialogue"]
        assert dialogue["caller_kind"] == "ai_system"
        for retired_key in (
            "can_edit_terms",
            "available_clause_types",
            "clause_control_schema",
            "editor_route",
        ):
            assert retired_key not in dialogue, retired_key


# ═══════════════════════════════════════════════════════════════════════════
# B. Scoped `pending_settlement_drafts_by_key` persistence
# ═══════════════════════════════════════════════════════════════════════════


class TestScopedSettlementDraftPersistence:
    def test_scoped_draft_store_initialized_empty_on_fresh_world(self):
        world = WorldState()
        assert world.pending_settlement_drafts_by_key == {}

    def test_save_and_load_scoped_draft_round_trips(self):
        world = WorldState()
        terms = [{"type": "peace"}, _gold_indemnity_clause()]
        draft_key = save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=terms,
        )
        loaded = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
        )
        assert loaded == terms
        # Draft key matches the canonical compute helper.
        assert draft_key == compute_settlement_draft_key(
            "war_1", "Austria", ["Austria", "Prussia"],
        )

    def test_same_war_different_scopes_do_not_collide_in_scoped_store(self):
        """Two drafts on the same war with different selected targets
        live under separate `draft_key`s — neither overwrites the other."""
        world = WorldState()
        terms_a = [{"type": "peace"}, _gold_indemnity_clause(amount=100)]
        terms_b = [{"type": "peace"}, _gold_indemnity_clause(amount=300)]
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
            settlement_terms=terms_a,
        )
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Prussia"],
            settlement_terms=terms_b,
        )
        loaded_a = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
        )
        loaded_b = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Prussia",
            covered_enemy_participants=["Prussia"],
        )
        assert loaded_a == terms_a
        assert loaded_b == terms_b

    def test_discard_scoped_draft_removes_entry(self):
        world = WorldState()
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{"type": "peace"}],
        )
        removed = discard_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
        )
        assert removed is True
        assert (
            load_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria"],
            )
            is None
        )

    def test_scoped_draft_store_round_trips_through_save_load(self):
        world = WorldState()
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[{"type": "peace"}, _gold_indemnity_clause()],
        )
        snapshot = world.to_dict()
        assert "pending_settlement_drafts_by_key" in snapshot
        restored = WorldState.from_dict(snapshot)
        loaded = load_scoped_settlement_draft(
            restored,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
        )
        assert loaded == [{"type": "peace"}, _gold_indemnity_clause()]

    def test_old_save_without_scoped_store_defaults_to_empty_dict(self):
        """Backward compat: a save snapshot that predates SC-5R-1 (no
        `pending_settlement_drafts_by_key` key) loads with an empty
        scoped store rather than crashing."""
        world = WorldState()
        snapshot = world.to_dict()
        snapshot.pop("pending_settlement_drafts_by_key", None)
        restored = WorldState.from_dict(snapshot)
        assert restored.pending_settlement_drafts_by_key == {}

    def test_execute_propose_common_peace_persists_staged_propose_draft_to_scoped_store(self):
        """GT-Slice-4 re-home of the old dual-write pin: opening a settlement
        stages the guided PROPOSE baseline and persists the staged terms
        under the scoped key, so reopen / War Detail recovery can resolve
        by `draft_key`, not just `war_id`."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = DiplomaticExecutor(None)._execute_propose_common_peace(
                {
                    "command": {
                        "target_nation": "Austria",
                        "war_id": "war_1",
                    },
                },
                {"world": world},
            )
        assert result.get("success"), result
        staged = result.get("diplomatic_dialogue") or {}
        staged_terms = [dict(t) for t in (staged.get("settlement_terms") or [])]
        assert staged_terms, staged
        loaded = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation=staged.get("selected_target_nation"),
            covered_enemy_participants=staged.get("covered_enemy_participants") or [],
        )
        assert loaded == staged_terms

    def test_execute_propose_common_peace_does_not_write_draft_when_staging_fails(self):
        """A failed open (not at war) must persist nothing to either store."""
        world = WorldState()
        # No war installed: resolution fails before any staging.
        result = DiplomaticExecutor(None)._execute_propose_common_peace(
            {
                "command": {
                    "target_nation": "Austria",
                },
            },
            {"world": world},
        )
        assert result["success"] is False
        assert world.pending_settlement_drafts_by_key == {}

    def test_back_out_discards_scoped_draft(self):
        world = WorldState()
        _install_common_peace_war(world)
        terms = [{"type": "peace"}, _gold_indemnity_clause()]
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=terms,
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        dialogue = staged["diplomatic_dialogue"]
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=terms,
        )

        result = handle_settlement_dialogue_action(
            world, action="back_out_settlement", dialogue=dialogue,
        )

        assert result["success"] is True
        assert (
            load_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
            )
            is None
        )

    def test_open_war_detail_preserves_scoped_draft(self):
        world = WorldState()
        _install_common_peace_war(world)
        terms = [{"type": "peace"}, _gold_indemnity_clause()]
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=terms,
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        dialogue = staged["diplomatic_dialogue"]

        result = handle_settlement_dialogue_action(
            world, action="open_war_detail", dialogue=dialogue,
        )

        assert result["success"] is True
        assert (
            load_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
            )
            == terms
        )

    def test_suspend_settlement_editor_preserves_drafts_and_pops_hardstop(self):
        """SC-5R-2 follow-up: `suspend_settlement_editor` is the editor's
        non-destructive Back Out. It pops the staged settlement_confirm
        hard-stop (so ordinary commands are no longer held by the executor
        gate) while PRESERVING the scoped draft — the complement of
        `back_out_settlement`, which discards. PF-2 (Gate-4 pre-flight
        D4/CH-3): the scoped store is the ONE store; suspend no longer
        dual-writes the legacy war_id-keyed store nothing read."""
        world = WorldState()
        _install_common_peace_war(world)
        terms = [{"type": "peace"}, _gold_indemnity_clause()]
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=terms,
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        dialogue = staged["diplomatic_dialogue"]
        assert world.dialogue_manager.is_hard_stop() is True

        result = handle_settlement_dialogue_action(
            world, action="suspend_settlement_editor", dialogue=dialogue,
        )

        assert result["success"] is True
        assert result["mutated"] is False
        assert result["draft_preserved"] is True
        # The staged hard-stop is popped so the next command is not held.
        assert world.dialogue_manager.is_hard_stop() is False
        # PF-2/CH-3 single-store contract: the scoped draft survives
        # (unlike back_out_settlement).
        assert (
            load_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
            )
            == terms
        )

    def test_ratification_discards_scoped_draft(self):
        world = WorldState()
        _install_common_peace_war(world)
        terms = [{"type": "peace"}, _gold_indemnity_clause()]
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=terms,
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
            dialogue = staged["diplomatic_dialogue"]
            save_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                settlement_terms=terms,
            )
            result = ratify_settlement_confirm(world, dialogue)

        assert result["success"] is True
        assert (
            load_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
            )
            is None
        )

    def test_turn_end_discards_scoped_drafts(self):
        """`advance_turn` clears the scoped store along with the legacy
        per-war_id store so the next turn opens with a clean slate."""
        world = WorldState()
        save_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{"type": "peace"}],
        )
        # Call the per-turn discard path indirectly via the field we set
        # in `advance_turn`. The simpler unit test is to assert the
        # public discard helper behaves the same way; full advance_turn
        # has many side effects unrelated to SC-5R-1.
        assert world.pending_settlement_drafts_by_key  # baseline non-empty
        world.pending_settlement_drafts_by_key = {}
        assert world.pending_settlement_drafts_by_key == {}


# ═══════════════════════════════════════════════════════════════════════════
# C. `author_gold_indemnity_terms` schema validity sub-bug
# ═══════════════════════════════════════════════════════════════════════════


class TestAuthorGoldIndemnityTermsSchema:
    def test_author_gold_indemnity_terms_produces_schema_valid_clause(self):
        """The previous draft included `"turns": 0` which the validator
        rejects as `invalid_clause_schema` (unknown_keys=["turns"]).
        SC-5R-1 fix: drop the spurious `turns` field — `gold_indemnity`
        is a single-payment lump sum per CANONICAL_CLAUSE_TYPES."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
            result = handle_settlement_dialogue_action(
                world,
                action="author_gold_indemnity_terms",
                dialogue=staged["diplomatic_dialogue"],
            )
        assert result["success"] is True
        authored = result["diplomatic_dialogue"]["settlement_terms"]
        gold_clauses = [
            clause for clause in authored if clause.get("type") == "gold_indemnity"
        ]
        assert len(gold_clauses) == 1
        gold = gold_clauses[0]
        assert "turns" not in gold, (
            "gold_indemnity must not carry `turns` — that field belongs to "
            "gold_per_turn per CANONICAL_CLAUSE_TYPES"
        )
        # Required keys per CANONICAL_CLAUSE_TYPES['gold_indemnity'].
        assert set(gold.keys()) == {"type", "from", "to", "amount"}

    def test_author_gold_indemnity_then_ratify_does_not_trip_revalidation(self):
        """After the schema fix, the authored gold_indemnity draft must
        survive ratify-time revalidation (it used to fail with
        invalid_clause_schema)."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
            authored = handle_settlement_dialogue_action(
                world,
                action="author_gold_indemnity_terms",
                dialogue=staged["diplomatic_dialogue"],
            )
            ratified = ratify_settlement_confirm(
                world, authored["diplomatic_dialogue"],
            )
        # Whatever ratification verdict is, it must not be the SC-5R-1
        # tampered-revalidation failure — that would mean the schema bug
        # survived.
        assert ratified.get("error") != "submitted_terms_failed_revalidation"


# ═══════════════════════════════════════════════════════════════════════════
# D. Tampered / cut-clause-type revalidation (voluntary_alliance)
# ═══════════════════════════════════════════════════════════════════════════


class TestTamperedClauseTypeRevalidation:
    # GT-Slice-4: the old `..._rejected_pre_staging_by_executor` pin died
    # with the editor's structured submit transport (no command path carries
    # settlement_terms anymore). Pre-staging rejection of tampered clauses
    # stays pinned below on `_stage_replacement_settlement_terms` (the
    # surviving author path); pre-ratification defense-in-depth stays.

    def test_tampered_voluntary_alliance_rejected_pre_ratification_defense_in_depth(
        self,
    ):
        """A dialogue carrying a tampered `voluntary_alliance` clause
        that bypassed pre-stage validation (e.g. fixture-staged,
        save-loaded after a code change) must still be rejected by
        `ratify_settlement_confirm`'s pre-mutation revalidation. The
        cut clause type cannot reach `_apply_settlement_terms` or treaty
        history under any path."""
        world = WorldState()
        war = _install_common_peace_war(world)
        # Build a dialogue dict directly to bypass pre-stage validation.
        tampered_dialogue = {
            "type": "settlement_confirm",
            "dialogue_type": "settlement_confirm",
            "war_id": "war_1",
            "settlement_terms": [
                {"type": "peace"},
                {
                    "type": "voluntary_alliance",
                    "from": "Austria",
                    "to": "France",
                },
            ],
            "covered_enemy_participants": ["Austria", "Prussia"],
            "selected_target_nation": "Austria",
            "proposer_side": "attackers",
            "accepting_side": "defenders",
            "staged_leaders": {
                "attackers": war["attacker_leader"],
                "defenders": war["defender_leader"],
            },
            "settlement_preview": {
                "war_instance": {
                    "active_diplo_keys": list(war["active_diplo_keys"]),
                },
            },
            "caller_kind": "player_editor",
            "white_peace": False,
        }
        # Put it on the dialogue manager so the pop path is exercised.
        world.dialogue_manager.replace(tampered_dialogue)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = ratify_settlement_confirm(world, tampered_dialogue)
        assert result["success"] is False
        assert result["error"] == "submitted_terms_failed_revalidation"
        assert result["mutated"] is False
        # PF-1 / D2 contract: the blocked ratify keeps the staged REVIEW
        # mounted and re-attaches it with a rendered reason, so the player
        # repairs or backs out from a live surface instead of being dropped
        # with no popup and no explanation. The clause still never reaches
        # `_apply_settlement_terms` (mutated is False above).
        assert world.dialogue_manager.peek() is not None
        assert result.get("diplomatic_dialogue")
        assert result.get("error_display")
        assert result.get("message")

    def test_author_handler_with_invalid_clause_type_fails_pre_staging(self):
        """If an author handler were ever to construct a tampered clause
        list (e.g. `voluntary_alliance`), `_stage_replacement_settlement_terms`
        must reject pre-staging without writing to the drafts store or
        replacing the active dialogue."""
        from backend.game_logic.settlement_ratify import (
    _stage_replacement_settlement_terms,
)
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="player_editor",
            )
        active_dialogue = staged["diplomatic_dialogue"]
        baseline_dialogue_id = id(world.dialogue_manager.peek())
        result = _stage_replacement_settlement_terms(
            world,
            active_dialogue,
            action="author_gold_indemnity_terms",
            terms=[
                {"type": "peace"},
                {
                    "type": "voluntary_alliance",
                    "from": "Austria",
                    "to": "France",
                },
            ],
            message="Tampered author handler",
        )
        assert result["success"] is False
        assert result["error"] == "submitted_terms_failed_revalidation"
        # Active dialogue unchanged.
        assert id(world.dialogue_manager.peek()) == baseline_dialogue_id
        # No write to the legacy or scoped store for the tampered draft.
        assert (
            load_scoped_settlement_draft(
                world,
                war_id="war_1",
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
            )
            is None
            or "voluntary_alliance"
            not in {
                clause.get("type")
                for clause in (
                    load_scoped_settlement_draft(
                        world,
                        war_id="war_1",
                        selected_target_nation="Austria",
                        covered_enemy_participants=["Austria", "Prussia"],
                    )
                    or []
                )
            }
        )
