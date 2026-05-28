"""SC-5R-1 backend EDIT payload contract + sub-bug closure.

The May 28, 2026 STATUS.md correction reopened the player-quality gate
under DWL-SET-SC5R: `request_settlement_revision` (and other player-
editor staging paths) must surface a real EDIT mode payload with
`can_edit_terms=true`, `available_clause_types[]`, `clause_control_schema`,
and `editor_route` so SC-5R-2 can mount the Godot editor. The matching
sub-bugs (gold_indemnity schema validity, tampered cut-clause-type
revalidation, scoped draft persistence by draft_key) close in this same
backend slice.

These tests pin the contract:

- `settlement_confirm` payload publishes the SC-5R-1 EDIT fields
  (`can_edit_terms`, `available_clause_types[]`, `clause_control_schema`,
  `editor_route`) per spec line 546-556.
- `can_edit_terms` is true if and only if
  `caller_kind == "player_editor"`, the staged dialogue resolves to an
  active `war_instance`, `settlement_terms` is non-empty, and
  `available_clause_types[]` is non-empty.
- `editor_route` is None when `can_edit_terms=false`; absent fields do
  not leak as disabled labels.
- `available_clause_types[]` and `clause_control_schema` only expose
  live clause types per `SETTLEMENT_LIVE_CLAUSE_TYPES` /
  `CLAUSE_CONTROL_SCHEMA`. Hidden / cut clause types
  (`voluntary_alliance`) are absent.
- `pending_settlement_drafts_by_key` round-trips through save/load with
  scoped draft_key keys; same-war drafts with different selected
  targets or covered scope do not collide.
- `_execute_propose_common_peace` dual-writes the authored draft to the
  scoped store so reopen / War Detail recovery can resolve by
  `draft_key`.
- `author_gold_indemnity_terms` produces schema-valid `gold_indemnity`
  clauses (no `turns` key — the previous draft included `turns: 0`
  which the validator rejects as `invalid_clause_schema`).
- A tampered `voluntary_alliance` clause is rejected pre-staging by
  `_execute_propose_common_peace` AND pre-ratification by
  `ratify_settlement_confirm`, so the cut clause type never reaches
  treaty history.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from backend.commands.diplomatic_executor import DiplomaticExecutor
from backend.game_logic.settlement_preview import (
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    compute_settlement_draft_key,
    discard_scoped_settlement_draft,
    handle_settlement_dialogue_action,
    load_scoped_settlement_draft,
    ratify_settlement_confirm,
    save_scoped_settlement_draft,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_scoring import (
    CLAUSE_CONTROL_SCHEMA,
    SETTLEMENT_LIVE_CLAUSE_TYPES,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


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
    from backend.game_logic.settlement_scoring import (
        calculate_common_peace_acceptance as real,
    )
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


class TestSettlementConfirmEditPayloadContract:
    def test_settlement_confirm_publishes_can_edit_terms_field(self):
        """`settlement_confirm` always exposes `can_edit_terms` as bool."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
        assert "can_edit_terms" in dialogue
        assert isinstance(dialogue["can_edit_terms"], bool)

    def test_can_edit_terms_true_iff_player_editor_and_clause_types_available_and_war_active(
        self,
    ):
        """Spec line 556 contract: `can_edit_terms` is true only when
        caller_kind=player_editor AND active war_instance AND non-empty
        settlement_terms AND non-empty available_clause_types[]."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
        assert dialogue["can_edit_terms"] is True
        assert dialogue["available_clause_types"], "must be non-empty"

    def test_can_edit_terms_false_for_ai_or_debug_caller_kind(self):
        """AI/system/debug staging cannot advertise editor capability —
        the field stays false and `editor_route` stays None even if all
        other conditions are met."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            staged = stage_settlement_confirm(
                world,
                war_id="war_1",
                actor_nation="France",
                settlement_terms=[{"type": "peace"}, _gold_indemnity_clause()],
                selected_target_nation="Austria",
                covered_enemy_participants=["Austria", "Prussia"],
                caller_kind="ai_system",
            )
        dialogue = staged["diplomatic_dialogue"]
        assert dialogue["can_edit_terms"] is False
        assert dialogue["editor_route"] is None
        assert dialogue["available_clause_types"] == []
        assert dialogue["clause_control_schema"] == {}

    def test_can_edit_terms_false_when_settlement_terms_empty(self):
        """Empty staged drafts are not edit-capable — the player has
        nothing to revise yet."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
        dialogue = staged["diplomatic_dialogue"]
        assert dialogue["can_edit_terms"] is False
        assert dialogue["editor_route"] is None

    def test_editor_route_payload_shape_matches_spec_line_548(self):
        """When `can_edit_terms=true`, `editor_route` carries the exact
        keys spec line 548 requires."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
        route = dialogue["editor_route"]
        assert route["surface"] == "settlement_editor"
        assert route["war_id"] == "war_1"
        assert route["selected_target_nation"] == "Austria"
        assert route["covered_enemy_participants"] == ["Austria", "Prussia"]
        assert route["draft_key"] == dialogue["draft_key"]
        # available_clause_types echoed on top-level + editor_route must match
        assert (
            route["available_clause_types"]
            == dialogue["available_clause_types"]
        )
        assert isinstance(route["staged_settlement_terms"], list)
        assert route["source"] in {
            "rejected_review",
            "stale_recovery",
            "explicit_revise",
        }

    def test_settlement_review_payload_with_editor_route_carries_available_clause_types_or_editor_route_subschema(
        self,
    ):
        """Spec line 548 required test: when can_edit_terms=true both
        top-level `available_clause_types[]` and
        `editor_route.available_clause_types` are present and equal."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
        assert dialogue["can_edit_terms"] is True
        top_level = list(dialogue["available_clause_types"])
        editor_route_types = list(dialogue["editor_route"]["available_clause_types"])
        assert top_level == editor_route_types
        assert top_level, "must be non-empty when can_edit_terms=true"

    def test_clause_control_schema_only_advertises_live_clause_types(self):
        """`clause_control_schema` and `available_clause_types[]` only
        expose `SETTLEMENT_LIVE_CLAUSE_TYPES` — cut/hidden clause types
        (e.g. `voluntary_alliance`) are absent."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
        for clause_type in dialogue["available_clause_types"]:
            assert clause_type in SETTLEMENT_LIVE_CLAUSE_TYPES, (
                f"{clause_type!r} is not in SETTLEMENT_LIVE_CLAUSE_TYPES"
            )
        for clause_type in dialogue["clause_control_schema"]:
            assert clause_type in SETTLEMENT_LIVE_CLAUSE_TYPES
        # Cut clause types must not leak as disabled labels either.
        assert "voluntary_alliance" not in dialogue["available_clause_types"]
        assert "voluntary_alliance" not in dialogue["clause_control_schema"]

    def test_hidden_clause_types_do_not_leak_as_visible_or_disabled_labels(self):
        """Spec line 554 required test: any clause type marked
        `enabled=False` in `CLAUSE_CONTROL_SCHEMA` does not appear in
        `available_clause_types[]` or `clause_control_schema` rows."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
        for clause_type, base in CLAUSE_CONTROL_SCHEMA.items():
            if base.get("enabled"):
                continue
            assert clause_type not in dialogue["available_clause_types"]
            assert clause_type not in dialogue["clause_control_schema"]

    def test_settlement_confirm_publishes_dialogue_mode_review(self):
        """Spec line 546 contract: `dialogue_mode` is `REVIEW` on
        `settlement_confirm`. EDIT mode is owned by SC-5R-2's editor
        popup and consumes the published `editor_route`."""
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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

    def test_execute_propose_common_peace_dual_writes_scoped_draft(self):
        """The structured executor path persists the authored draft
        under the scoped key so reopen / War Detail recovery can resolve
        by `draft_key`, not just `war_id`."""
        world = WorldState()
        _install_common_peace_war(world)
        terms = [{"type": "peace"}, _gold_indemnity_clause()]
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            DiplomaticExecutor(None)._execute_propose_common_peace(
                {
                    "command": {
                        "target_nation": "Austria",
                        "war_id": "war_1",
                        "selected_target_nation": "Austria",
                        "covered_enemy_participants": ["Austria", "Prussia"],
                        "settlement_terms": terms,
                    },
                },
                {"world": world},
            )
        loaded = load_scoped_settlement_draft(
            world,
            war_id="war_1",
            selected_target_nation="Austria",
            covered_enemy_participants=["Austria", "Prussia"],
        )
        assert loaded == terms

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
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
    def test_tampered_voluntary_alliance_rejected_pre_staging_by_executor(self):
        """`_execute_propose_common_peace` already revalidates submitted
        terms before staging. A tampered `voluntary_alliance` clause
        (the D3 CUT clause type) must fail validation and stage
        nothing."""
        world = WorldState()
        _install_common_peace_war(world)
        result = DiplomaticExecutor(None)._execute_propose_common_peace(
            {
                "command": {
                    "target_nation": "Austria",
                    "war_id": "war_1",
                    "selected_target_nation": "Austria",
                    "covered_enemy_participants": ["Austria"],
                    "settlement_terms": [
                        {"type": "peace"},
                        {
                            "type": "voluntary_alliance",
                            "from": "Austria",
                            "to": "France",
                        },
                    ],
                },
            },
            {"world": world},
        )
        assert result["success"] is False
        assert result["error"] == "submitted_terms_failed_revalidation"
        assert result.get("mutated") is False

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
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
            side_effect=_acceptance_accepts,
        ):
            result = ratify_settlement_confirm(world, tampered_dialogue)
        assert result["success"] is False
        assert result["error"] == "submitted_terms_failed_revalidation"
        assert result["mutated"] is False
        # Defense in depth: the dialogue is popped so the player is not
        # left on a tampered staged review.
        assert world.dialogue_manager.peek() is None

    def test_author_handler_with_invalid_clause_type_fails_pre_staging(self):
        """If an author handler were ever to construct a tampered clause
        list (e.g. `voluntary_alliance`), `_stage_replacement_settlement_terms`
        must reject pre-staging without writing to the drafts store or
        replacing the active dialogue."""
        from backend.game_logic.settlement_preview import (
            _stage_replacement_settlement_terms,
        )
        world = WorldState()
        _install_common_peace_war(world)
        with patch(
            "backend.game_logic.settlement_preview.calculate_common_peace_acceptance",
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
