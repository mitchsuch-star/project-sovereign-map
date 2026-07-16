"""SC-31 / G2-Slice-8 - Dependency And Surrender Terms Restoration.

Behavior tests for the cleanup slice that unhides `vassalage`,
`subjugation`, and `liberation` clause types in the settlement editor,
ships the `Author surrender terms (Talleyrand)` EDIT-rail preset, and
propagates the `surrender_preset` flag through staging / ratification /
reactions / `settlement_summary`.

Spec gates covered:

- SC-31 dependency clause types are live in
  `CLAUSE_CONTROL_SCHEMA` / `available_clause_types[]`.
- POST preview validator rejects illegal-by-state dependency clauses:
  reversed direction, target not in war, target already a vassal,
  power-cap blocked, liberation against non-vassal, liberation lord
  mismatch, liberation with invalid liberator.
- Surrender preset is deterministic `[peace, harshest-legal dependency]`
  in the order `subjugation -> vassalage`.
- Preset visibility reuses the losing-side concession baseline predicate
  (`side_pressure_score <= -20`) AND requires a legal dependency
  clause; otherwise the affordance is hidden (not disabled).
- `author_surrender_terms` dialogue action: replace-confirm on a
  non-empty draft, click-time revalidation refuses to mutate on stale
  state, and on positive re-check restages a fresh `settlement_confirm`
  with `surrender_preset=True`.
- Ratified surrender preset propagates `surrender_preset=True` through
  the emitted `settlement_summary` event.
- `applied_clauses_preview` rows for vassalage / subjugation include
  `pair_state_transition`, `autonomy_after`, `loyalty_after`,
  `tribute_rate_after`, `vassal_path`, `marshal_assimilation_count`,
  and `threat_delta_for_lord`. Liberation rows include
  `pair_state_transition`, `defensive_alliance_with_liberator`,
  `relation_deltas`, and `threat_reduction`.

Power-cap behavior: the default 1805 map gives France ~275% of any
single hostile lord's national power, so settlement_losing cannot prove
the positive surrender path. These tests construct fixtures where the
accepting leader satisfies WPS-B `target_power <= lord_power // 2` and
verify the surrender preset both authors AND ratifies through real
mutation.
"""

from __future__ import annotations

import copy
import os
from unittest.mock import patch

from backend.game_logic.settlement_preview import (
    LOSING_SIDE_PRESSURE_THRESHOLD,
    build_settlement_confirm_dialogue,
    build_settlement_preview,
    evaluate_liberation_eligibility,
    evaluate_subjugation_eligibility,
    evaluate_vassalage_eligibility,
    handle_settlement_dialogue_action,
    ratify_settlement_confirm,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.game_logic.settlement_baseline import (
    _compute_surrender_preset,
)
from backend.game_logic.settlement_scoring import (
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONTROL_SCHEMA,
    SETTLEMENT_DEPENDENCY_CLAUSE_TYPES,
    SETTLEMENT_LIVE_CLAUSE_TYPES,
    SETTLEMENT_MVP_CLAUSE_TYPES,
)
from backend.models.world_state import (
    WorldState,
    SMOKE_START_SETTLEMENT_SURRENDER,
    SMOKE_START_ENV,
)
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


# ═══════════════════════════════════════════════════════════════════════════
# Fixture: power-cap-legal war where the accepting leader can vassalize France
# ═══════════════════════════════════════════════════════════════════════════


def _install_power_legal_surrender_war(world: WorldState) -> dict:
    """Install a France vs Britain + Prussia war where Britain can
    legally vassalize France under WPS-B `target_power <= lord_power // 2`.

    Strips France's high-income regions to Britain so France keeps
    ~350 power vs Britain's ~1300, well below the 1:2 cap. Mirrors the
    `SOVEREIGN_SMOKE_START=settlement_surrender` fixture so behavior
    tests stay parallel to the manual smoke path.
    """
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["Britain", "Prussia"],
        defenders=["France"],
        attacker_leader="Britain",
        defender_leader="France",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_start_turns[pair] = world.current_turn
        first = pair.split("|")[0]
        world.war_scores[pair] = -100 if first == "France" else 100
        world.battle_records[pair] = []
    # Reassign French regions so Britain has roughly 3x France's power.
    for region_name in ("Belgium", "Lyon", "Marseille", "Milan", "Normandy", "Bordeaux"):
        region = world.regions.get(region_name)
        if region is not None:
            region.controller = "Britain"
    world._national_power_cache = {}
    world.invalidate_active_nations_cache()
    world.invalidate_war_instance_indexes()
    return war


def _stage_player_editor_dialogue(
    world: WorldState,
    *,
    settlement_terms=None,
    covered_enemy_participants=None,
    selected_target_nation="Britain",
    caller_kind="player_editor",
    white_peace=False,
    surrender_preset=False,
):
    if not settlement_terms:
        settlement_terms = [{"type": "peace"}]
    result = stage_settlement_confirm(
        world,
        war_id="war_1",
        settlement_terms=settlement_terms,
        covered_enemy_participants=covered_enemy_participants or ["Britain"],
        selected_target_nation=selected_target_nation,
        actor_nation="France",
        caller_kind=caller_kind,
        white_peace=white_peace,
        surrender_preset=surrender_preset,
    )
    assert result.get("success"), result
    return world.pending_diplomatic_dialogue


# ═══════════════════════════════════════════════════════════════════════════
# Clause-control schema: dependency clauses are now live (DWL inversion)
# ═══════════════════════════════════════════════════════════════════════════


class TestClauseControlSchema:
    def test_dependency_clause_types_are_live_in_clause_control_schema(self):
        for ctype in ("vassalage", "subjugation", "liberation"):
            row = CLAUSE_CONTROL_SCHEMA[ctype]
            assert row["enabled"] is True, ctype
            assert row["visibility"] == "live", ctype

    def test_settlement_live_clause_types_is_mvp_plus_dependency_plus_recurring(self):
        # SC-33 / G2-Slice-9 - `gold_per_turn` joins the live set; the
        # pre-G2-Slice-9 invariant
        # `SETTLEMENT_LIVE_CLAUSE_TYPES == MVP | DEPENDENCY`
        # is inverted to also include the recurring-gold set.
        from backend.game_logic.settlement_scoring import (
            SETTLEMENT_RECURRING_GOLD_CLAUSE_TYPES,
        )
        assert SETTLEMENT_LIVE_CLAUSE_TYPES == (
            SETTLEMENT_MVP_CLAUSE_TYPES
            | SETTLEMENT_DEPENDENCY_CLAUSE_TYPES
            | SETTLEMENT_RECURRING_GOLD_CLAUSE_TYPES
        )

    def test_gold_per_turn_is_live_after_sc33(self):
        # SC-33 / G2-Slice-9 - DWL-SET-SC33 inversion: `gold_per_turn`
        # is now editor-live with the canonical
        # `{type, from, to, amount, turns}` schema; the prior hidden
        # assertion is inverted in the same slice that lands the clause.
        row = CLAUSE_CONTROL_SCHEMA["gold_per_turn"]
        assert row["enabled"] is True
        assert row["visibility"] == "live"

    def test_dependency_clause_required_keys_match_canonical(self):
        for ctype in ("vassalage", "subjugation"):
            row = CLAUSE_CONTROL_SCHEMA[ctype]
            assert row["required_keys"] == sorted(
                CANONICAL_CLAUSE_TYPES[ctype]["required"]
            )
        liberation_row = CLAUSE_CONTROL_SCHEMA["liberation"]
        assert "vassal_nation" in liberation_row["required_keys"]
        assert "lord_nation" in liberation_row["required_keys"]
        assert "liberator" in liberation_row["required_keys"]


# ═══════════════════════════════════════════════════════════════════════════
# POST preview validator: closed taxonomy for dependency rejection
# ═══════════════════════════════════════════════════════════════════════════


class TestValidatorDependencyRejection:
    def test_subjugation_with_same_from_and_to_rejected_as_invalid_direction(self):
        # `from == to` is unambiguous: it can never be legal regardless of
        # war state or power. The validator surfaces the explicit
        # `dependency_direction_invalid` code rather than collapsing onto
        # one of the later refusal codes.
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        result = validate_settlement_terms(
            [{"type": "subjugation", "from": "Britain", "to": "Britain"}],
            world=world,
            war_instance=war,
        )
        assert result["valid"] is False
        assert result["error"] == "dependency_direction_invalid"

    def test_dependency_canonical_direction_is_vassal_to_lord(self):
        """Lock the canonical projection direction: `from = vassal`,
        `to = lord`. A reversed payload (lord as `from`) must be
        rejected by either the direction guard OR the power-cap, but
        never silently treated as the canonical direction."""
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        # Canonical direction: France (vassal) -> Britain (lord) is legal.
        canonical = validate_settlement_terms(
            [{"type": "subjugation", "from": "France", "to": "Britain"}],
            world=world,
            war_instance=war,
        )
        assert canonical["valid"] is True, canonical
        # Reversed direction (Britain -> France): the validator must
        # reject because Britain cannot be subjugated by France under the
        # power cap (Britain's accumulated regions give it ~1300 power,
        # France's reduced share gives it ~350). The fail is not silent.
        reversed_ = validate_settlement_terms(
            [{"type": "subjugation", "from": "Britain", "to": "France"}],
            world=world,
            war_instance=war,
        )
        assert reversed_["valid"] is False
        assert reversed_["error"] in {
            "dependency_direction_invalid",
            "dependency_target_not_in_war",
            "dependency_power_cap_blocked",
        }

    def test_subjugation_with_target_not_in_war_rejected(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        # Austria is not a participant of war_1.
        result = validate_settlement_terms(
            [{"type": "subjugation", "from": "Austria", "to": "Britain"}],
            world=world,
            war_instance=war,
        )
        assert result["valid"] is False
        assert result["error"] == "dependency_target_not_in_war"

    def test_subjugation_against_already_vassal_rejected(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        world.vassals["France"] = {
            "lord": "Britain",
            "loyalty": 50,
            "autonomy": 1,
            "path": "treaty",
            "tribute_rate": 0.75,
        }
        result = validate_settlement_terms(
            [{"type": "subjugation", "from": "France", "to": "Britain"}],
            world=world,
            war_instance=war,
        )
        assert result["valid"] is False
        assert result["error"] == "dependency_target_already_vassal"

    def test_subjugation_against_power_cap_hidden(self):
        """Default map: France 1100 power vs Britain 400. The validator
        must refuse a subjugation clause that violates the WPS-B cap."""
        world = WorldState()
        war = make_synthetic_war_instance(
            "war_1",
            attackers=["Britain"],
            defenders=["France"],
            attacker_leader="Britain",
            defender_leader="France",
            created_turn=1,
            created_sequence=1,
        )
        world.war_instances["war_1"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
        world._national_power_cache = {}
        result = validate_settlement_terms(
            [{"type": "subjugation", "from": "France", "to": "Britain"}],
            world=world,
            war_instance=war,
        )
        assert result["valid"] is False
        assert result["error"] == "dependency_power_cap_blocked"

    def test_vassalage_uses_same_pre_checks_as_subjugation(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        ok = validate_settlement_terms(
            [{"type": "vassalage", "from": "France", "to": "Britain"}],
            world=world,
            war_instance=war,
        )
        assert ok["valid"] is True

    def test_liberation_target_not_vassal_rejected(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        result = validate_settlement_terms(
            [{
                "type": "liberation",
                "vassal_nation": "Saxony",
                "lord_nation": "Britain",
                "liberator": "France",
            }],
            world=world,
            war_instance=war,
        )
        assert result["valid"] is False
        assert result["error"] == "liberation_target_not_vassal"

    def test_liberation_lord_mismatch_rejected(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        world.vassals["Saxony"] = {
            "lord": "Britain",
            "loyalty": 50,
            "autonomy": 1,
            "path": "treaty",
            "tribute_rate": 0.75,
        }
        # Spec contract: declared lord_nation must match the current lord.
        result = validate_settlement_terms(
            [{
                "type": "liberation",
                "vassal_nation": "Saxony",
                "lord_nation": "Prussia",
                "liberator": "France",
            }],
            world=world,
            war_instance=war,
        )
        assert result["valid"] is False
        assert result["error"] == "liberation_lord_mismatch"

    def test_liberation_with_lord_as_liberator_rejected(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        world.vassals["Saxony"] = {
            "lord": "Britain",
            "loyalty": 50,
            "autonomy": 1,
            "path": "treaty",
            "tribute_rate": 0.75,
        }
        result = validate_settlement_terms(
            [{
                "type": "liberation",
                "vassal_nation": "Saxony",
                "lord_nation": "Britain",
                "liberator": "Britain",
            }],
            world=world,
            war_instance=war,
        )
        assert result["valid"] is False
        assert result["error"] == "liberation_invalid_liberator"

    def test_legal_liberation_passes(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        world.vassals["Saxony"] = {
            "lord": "Britain",
            "loyalty": 50,
            "autonomy": 1,
            "path": "treaty",
            "tribute_rate": 0.75,
        }
        ok = validate_settlement_terms(
            [{
                "type": "liberation",
                "vassal_nation": "Saxony",
                "lord_nation": "Britain",
                "liberator": "France",
            }],
            world=world,
            war_instance=war,
        )
        assert ok["valid"] is True

    def test_validator_skips_dependency_checks_without_world(self):
        # Without world+war_instance the validator returns schema-only OK
        # so legacy callers (and pure SC-1 conflict-matrix tests) still
        # accept dependency clauses by shape alone.
        ok = validate_settlement_terms(
            [{"type": "subjugation", "from": "Foo", "to": "Bar"}],
        )
        assert ok["valid"] is True


# ═══════════════════════════════════════════════════════════════════════════
# Eligibility helpers: closed taxonomy with explicit refusal codes
# ═══════════════════════════════════════════════════════════════════════════


class TestEligibilityHelpers:
    def test_subjugation_eligibility_positive(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        result = evaluate_subjugation_eligibility(
            world,
            war_instance=war,
            lord_nation="Britain",
            target_nation="France",
        )
        assert result["eligible"] is True
        assert result["refusal_code"] is None

    def test_subjugation_eligibility_self_target(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        result = evaluate_subjugation_eligibility(
            world,
            war_instance=war,
            lord_nation="Britain",
            target_nation="Britain",
        )
        assert result["eligible"] is False
        assert result["refusal_code"] == "dependency_direction_invalid"

    def test_vassalage_eligibility_shares_subjugation_pre_checks(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        subj = evaluate_subjugation_eligibility(
            world,
            war_instance=war,
            lord_nation="Britain",
            target_nation="France",
        )
        vass = evaluate_vassalage_eligibility(
            world,
            war_instance=war,
            lord_nation="Britain",
            target_nation="France",
        )
        assert subj["eligible"] == vass["eligible"]

    def test_liberation_eligibility_positive(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        world.vassals["Saxony"] = {
            "lord": "Britain",
            "loyalty": 50,
            "autonomy": 1,
            "path": "treaty",
            "tribute_rate": 0.75,
        }
        result = evaluate_liberation_eligibility(
            world,
            war_instance=war,
            vassal_nation="Saxony",
            lord_nation="Britain",
            liberator="France",
        )
        assert result["eligible"] is True
        assert result["current_lord"] == "Britain"


# ═══════════════════════════════════════════════════════════════════════════
# Surrender preset algorithm: deterministic [peace, harshest-legal]
# ═══════════════════════════════════════════════════════════════════════════


class TestSurrenderPresetAlgorithm:
    def test_compute_surrender_preset_returns_peace_plus_subjugation(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        result = _compute_surrender_preset(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="defenders",
            accepting_side="attackers",
            accepting_leader="Britain",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain"],
            side_pressure_score=-90,
        )
        assert result["losing_for_surrender_preset"] is True
        assert result["surrender_preset_visible"] is True
        preset = result["surrender_preset"]
        assert preset is not None
        types = [t["type"] for t in preset["terms"]]
        assert types == ["peace", "subjugation"]
        # Canonical direction: from = vassal/subjugated (France),
        # to = lord (Britain). The projection helper / power cap reads
        # `from` as the prospective vassal.
        sub_clause = preset["terms"][1]
        assert sub_clause["from"] == "France"
        assert sub_clause["to"] == "Britain"
        assert preset["dependency_kind"] == "subjugation"

    def test_compute_surrender_preset_falls_back_to_vassalage_when_subjugation_blocked(
        self,
    ):
        # Subjugation and vassalage share pre-checks in the current
        # implementation. To exercise the fallback path the test patches
        # only the subjugation helper so vassalage stays eligible. Spec
        # contract: when subjugation is blocked but vassalage is legal,
        # the preset picks vassalage.
        world = WorldState()
        war = _install_power_legal_surrender_war(world)

        def _subj_refusal(*args, **kwargs):
            return {
                "eligible": False,
                "refusal_code": "dependency_power_cap_blocked",
                "disabled_reason_display": "",
            }

        with patch.object(
            __import__(
                "backend.game_logic.settlement_baseline",
                fromlist=["evaluate_subjugation_eligibility"],
            ),
            "evaluate_subjugation_eligibility",
            side_effect=_subj_refusal,
        ):
            # Vassalage eligibility must NOT be patched; we want to see
            # the preset reach the vassalage branch. Because vassalage
            # delegates to subjugation, we also patch the vassalage
            # helper to a hardcoded eligible payload so the test pins the
            # fallback path explicitly.
            with patch(
                "backend.game_logic.settlement_baseline."
                "evaluate_vassalage_eligibility",
                return_value={
                    "eligible": True,
                    "refusal_code": None,
                    "disabled_reason_display": None,
                },
            ):
                result = _compute_surrender_preset(
                    world,
                    war_id="war_1",
                    war_instance=war,
                    proposer_side="defenders",
                    accepting_side="attackers",
                    accepting_leader="Britain",
                    proposer_side_leader="France",
                    covered_enemy_participants=["Britain"],
                    side_pressure_score=-90,
                )
        assert result["surrender_preset_visible"] is True
        preset = result["surrender_preset"]
        types = [t["type"] for t in preset["terms"]]
        assert types == ["peace", "vassalage"]
        assert preset["dependency_kind"] == "vassalage"

    def test_compute_surrender_preset_hidden_when_not_losing(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        result = _compute_surrender_preset(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="defenders",
            accepting_side="attackers",
            accepting_leader="Britain",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain"],
            side_pressure_score=10,
        )
        assert result["losing_for_surrender_preset"] is False
        assert result["surrender_preset_visible"] is False
        assert result["surrender_preset"] is None

    def test_compute_surrender_preset_hidden_when_no_legal_dependency(self):
        """Power-cap blocks both subjugation AND vassalage."""
        world = WorldState()
        war = make_synthetic_war_instance(
            "war_1",
            attackers=["Britain"],
            defenders=["France"],
            attacker_leader="Britain",
            defender_leader="France",
            created_turn=1,
            created_sequence=1,
        )
        world.war_instances["war_1"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
        world._national_power_cache = {}
        result = _compute_surrender_preset(
            world,
            war_id="war_1",
            war_instance=war,
            proposer_side="defenders",
            accepting_side="attackers",
            accepting_leader="Britain",
            proposer_side_leader="France",
            covered_enemy_participants=["Britain"],
            side_pressure_score=-90,
        )
        assert result["losing_for_surrender_preset"] is True
        assert result["surrender_preset_visible"] is False
        assert result["surrender_preset_reason"] == "no_legal_dependency_clause"


# ═══════════════════════════════════════════════════════════════════════════
# build_settlement_preview / build_settlement_confirm_dialogue: payload
# ═══════════════════════════════════════════════════════════════════════════


class TestSurrenderPresetPayloadShape:
    def test_post_preview_emits_surrender_preset_keys(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            settlement_terms=[],
            covered_enemy_participants=["France"],
            actor_nation="Britain",
            proposer_side="attackers",
        )
        assert preview["success"] is True
        body = preview["settlement_preview"]
        # Britain authoring is the winning side; surrender preset should
        # be False for it.
        assert body["losing_for_surrender_preset"] is False
        assert body["surrender_preset_visible"] is False

    def test_staged_dialogue_carries_surrender_preset_keys_for_losing_player(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        # Boost war pressure so the losing-side predicate fires for
        # France (the player). Authoring an empty draft makes the
        # editor empty-Ratify gate fire; the dialogue still carries the
        # surrender preset payload regardless.
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            settlement_terms=[{"type": "peace"}],
            covered_enemy_participants=["Britain"],
            actor_nation="France",
            selected_target_nation="Britain",
            caller_kind="player_editor",
            proposer_side="defenders",
        )
        assert result.get("success") is True, result
        dialogue = world.pending_diplomatic_dialogue
        # Behavior contract: the staged dialogue exposes the same three
        # keys POST preview does, regardless of can_ratify.
        assert "losing_for_surrender_preset" in dialogue
        assert "surrender_preset_visible" in dialogue
        assert "surrender_preset_payload" in dialogue


# ═══════════════════════════════════════════════════════════════════════════
# Blocked settlement_confirm: author_surrender_terms option visibility
# ═══════════════════════════════════════════════════════════════════════════


class TestBlockedPopupAuthorSurrenderOption:
    def test_blocked_review_renders_author_surrender_terms_when_visible(self):
        world = WorldState()
        war = _install_power_legal_surrender_war(world)
        # Force the dialogue into blocked state by patching the
        # acceptance scorer to return a rejecting verdict; the surrender
        # preset payload must still appear because the predicate fires.
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance"
        ) as mock_accept:
            mock_accept.return_value = {
                "score": 10,
                "verdict": "reject",
                "hard_stops": [],
                "feedback": [],
                "top_components": [],
                "components": {},
                "side_pressure_score": -90,
                "accept_threshold": 50,
                "near_acceptable_threshold": 35,
            }
            result = stage_settlement_confirm(
                world,
                war_id="war_1",
                settlement_terms=[{"type": "peace"}],
                covered_enemy_participants=["Britain"],
                actor_nation="France",
                selected_target_nation="Britain",
                proposer_side="defenders",
                caller_kind="player_editor",
            )
        assert result["success"] is True
        dialogue = world.pending_diplomatic_dialogue
        action_ids = list(dialogue.get("available_action_ids") or [])
        assert "author_surrender_terms" in action_ids

    def test_blocked_review_hides_author_surrender_terms_when_no_legal_dependency(self):
        """Power-cap blocks both dependency types → action hidden.

        Default 1805 map: France has 1100 power vs Britain's 400, so
        the WPS-B power cap (target <= lord/2) fails for both
        subjugation and vassalage. The blocked-popup must not surface
        `author_surrender_terms` because the surrender preset cannot
        author a legal harsh dependency.
        """
        world = WorldState()
        # Multilateral default-map war so settlement eligibility passes
        # but the power cap fails for France-as-target.
        war = make_synthetic_war_instance(
            "war_1",
            attackers=["Britain", "Prussia"],
            defenders=["France"],
            attacker_leader="Britain",
            defender_leader="France",
            created_turn=1,
            created_sequence=1,
        )
        world.war_instances["war_1"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
        world._national_power_cache = {}
        world.invalidate_active_nations_cache()
        world.invalidate_war_instance_indexes()
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance"
        ) as mock_accept:
            mock_accept.return_value = {
                "score": 10,
                "verdict": "reject",
                "hard_stops": [],
                "feedback": [],
                "top_components": [],
                "components": {},
                "side_pressure_score": -90,
                "accept_threshold": 50,
                "near_acceptable_threshold": 35,
            }
            result = stage_settlement_confirm(
                world,
                war_id="war_1",
                settlement_terms=[{"type": "peace"}],
                covered_enemy_participants=["Britain", "Prussia"],
                actor_nation="France",
                selected_target_nation="Britain",
                proposer_side="defenders",
                caller_kind="player_editor",
            )
        assert result["success"] is True
        dialogue = world.pending_diplomatic_dialogue
        action_ids = list(dialogue.get("available_action_ids") or [])
        assert "author_surrender_terms" not in action_ids


# ═══════════════════════════════════════════════════════════════════════════
# author_surrender_terms dialogue handler
# ═══════════════════════════════════════════════════════════════════════════


def _stage_blocked_surrender_dialogue(world: WorldState, *, with_draft=None):
    """Force a blocked settlement_confirm dialogue with the surrender
    preset visible, optionally carrying a non-empty draft."""
    terms = with_draft or [{"type": "peace"}]
    with patch(
        "backend.game_logic.settlement_scoring."
        "calculate_common_peace_acceptance"
    ) as mock_accept:
        mock_accept.return_value = {
            "score": 10,
            "verdict": "reject",
            "hard_stops": [],
            "feedback": [],
            "top_components": [],
            "components": {},
            "side_pressure_score": -90,
            "accept_threshold": 50,
            "near_acceptable_threshold": 35,
        }
        result = stage_settlement_confirm(
            world,
            war_id="war_1",
            settlement_terms=terms,
            covered_enemy_participants=["Britain"],
            actor_nation="France",
            selected_target_nation="Britain",
            proposer_side="defenders",
            caller_kind="player_editor",
        )
    assert result["success"] is True
    return world.pending_diplomatic_dialogue


class TestAuthorSurrenderTermsHandler:
    def test_handler_applies_preset_and_restages_with_flag_when_draft_empty(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        dialogue = _stage_blocked_surrender_dialogue(world)
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance"
        ) as mock_accept:
            mock_accept.return_value = {
                "score": 10,
                "verdict": "reject",
                "hard_stops": [],
                "feedback": [],
                "top_components": [],
                "components": {},
                "side_pressure_score": -90,
                "accept_threshold": 50,
                "near_acceptable_threshold": 35,
            }
            # Drop the existing draft so the no-replace-confirm path fires.
            dialogue = dict(dialogue)
            dialogue["settlement_terms"] = []
            result = handle_settlement_dialogue_action(
                world, action="author_surrender_terms", dialogue=dialogue,
            )
        assert result["success"] is True
        assert result["action"] == "author_surrender_terms"
        new_dialogue = result["diplomatic_dialogue"]
        # Newly staged dialogue carries surrender_preset=True so
        # downstream ratification tags the settlement_summary event.
        assert new_dialogue["surrender_preset"] is True
        assert new_dialogue["concession_baseline_visible"] is False
        assert new_dialogue["concession_baseline"] is None
        assert "re_author_with_concessions" not in new_dialogue["available_action_ids"]
        # Pre-applied terms are [peace, subjugation].
        types = [t["type"] for t in new_dialogue["settlement_terms"]]
        assert types == ["peace", "subjugation"]

    def test_handler_returns_replace_confirm_when_draft_non_empty(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        dialogue = _stage_blocked_surrender_dialogue(
            world,
            with_draft=[{
                "type": "gold_indemnity",
                "from": "France",
                "to": "Britain",
                "amount": 500,
            }],
        )
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance"
        ) as mock_accept:
            mock_accept.return_value = {
                "score": 10,
                "verdict": "reject",
                "hard_stops": [],
                "feedback": [],
                "top_components": [],
                "components": {},
                "side_pressure_score": -90,
                "accept_threshold": 50,
                "near_acceptable_threshold": 35,
            }
            result = handle_settlement_dialogue_action(
                world, action="author_surrender_terms", dialogue=dialogue,
            )
        assert result["success"] is True
        assert result["requires_replace_confirm"] is True
        replace_dialogue = result["diplomatic_dialogue"]
        assert replace_dialogue["replace_confirm"] is True
        assert world.pending_diplomatic_dialogue == replace_dialogue
        assert [opt["action"] for opt in replace_dialogue["options"]] == [
            "apply_surrender_preset_replacement",
            "keep_current_settlement_draft",
        ]
        # Replacement terms come from the surrender preset, not the
        # concession baseline. Replacement must not run until the player
        # confirms discard of the active draft.
        types = [t["type"] for t in result["replacement_terms"]]
        assert "subjugation" in types or "vassalage" in types

    def test_apply_surrender_replacement_restages_preset_after_confirm(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        dialogue = _stage_blocked_surrender_dialogue(
            world,
            with_draft=[{
                "type": "gold_indemnity",
                "from": "France",
                "to": "Britain",
                "amount": 500,
            }],
        )
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance"
        ) as mock_accept:
            mock_accept.return_value = {
                "score": 10,
                "verdict": "reject",
                "hard_stops": [],
                "feedback": [],
                "top_components": [],
                "components": {},
                "side_pressure_score": -90,
                "accept_threshold": 50,
                "near_acceptable_threshold": 35,
            }
            replace_result = handle_settlement_dialogue_action(
                world, action="author_surrender_terms", dialogue=dialogue,
            )
            result = handle_settlement_dialogue_action(
                world,
                action="apply_surrender_preset_replacement",
                dialogue=replace_result["diplomatic_dialogue"],
            )

        assert result["success"] is True
        assert result["mutated"] is False
        refreshed = result["diplomatic_dialogue"]
        assert refreshed["surrender_preset"] is True
        assert refreshed["concession_baseline_visible"] is False
        assert refreshed["concession_baseline"] is None
        assert "re_author_with_concessions" not in refreshed["available_action_ids"]
        types = [t["type"] for t in refreshed["settlement_terms"]]
        assert "subjugation" in types or "vassalage" in types
        assert "author_surrender_terms" not in refreshed["available_action_ids"]

    def test_handler_refuses_mutation_on_stale_failure(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        dialogue = _stage_blocked_surrender_dialogue(world)
        # Flip the state: drop France's vassalage eligibility by giving
        # France a fictitious vassal record. The handler revalidates at
        # click time and must refuse without consuming the draft.
        original_draft = list(dialogue.get("settlement_terms") or [])
        with patch(
            "backend.game_logic.settlement_staging._compute_surrender_preset"
        ) as mock_preset:
            mock_preset.return_value = {
                "losing_for_surrender_preset": True,
                "surrender_preset_visible": False,
                "surrender_preset": None,
                "surrender_preset_reason": "no_legal_dependency_clause",
            }
            result = handle_settlement_dialogue_action(
                world, action="author_surrender_terms", dialogue=dialogue,
            )
        assert result["success"] is False
        assert result["error"] == "surrender_preset_unavailable"
        # No-overwrite contract: preserved_terms echo the player's draft.
        assert result["preserved_terms"] == original_draft

    def test_dialogue_response_routes_author_surrender_terms_through_executor_dispatch(self):
        """Gate 4 repair regression: the player clicks a popup option,
        so the action must travel through `/respond_to_diplomatic_dialogue`
        and `DiplomaticExecutor._process_dialogue_choice`, not only the
        direct settlement handler unit path."""
        from backend.commands.diplomatic_executor import DiplomaticExecutor

        world = WorldState()
        _install_power_legal_surrender_war(world)
        dialogue = _stage_blocked_surrender_dialogue(world)
        target_idx = next(
            idx
            for idx, option in enumerate(dialogue["options"], start=1)
            if option.get("action") == "author_surrender_terms"
        )

        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance"
        ) as mock_accept:
            mock_accept.return_value = {
                "score": 10,
                "verdict": "reject",
                "hard_stops": [],
                "feedback": [],
                "top_components": [],
                "components": {},
                "side_pressure_score": -90,
                "accept_threshold": 50,
                "near_acceptable_threshold": 35,
            }
            result = DiplomaticExecutor(None).handle_diplomatic_dialogue_response(
                target_idx, {"world": world}
            )

        assert "Unknown dialogue action" not in str(result.get("message", ""))
        assert result["success"] is True
        assert result["action"] == "author_surrender_terms"
        assert result["requires_replace_confirm"] is True
        assert result["diplomatic_dialogue"]["replace_confirm"] is True
        assert result["mutated"] is False


# ═══════════════════════════════════════════════════════════════════════════
# Ratification: settlement_summary.surrender_preset propagation
# ═══════════════════════════════════════════════════════════════════════════


def _force_acceptance(score=100, verdict="accept"):
    return {
        "score": score,
        "verdict": verdict,
        "hard_stops": [],
        "feedback": [],
        "top_components": [],
        "components": {},
        "side_pressure_score": score,
        "accept_threshold": 50,
        "near_acceptable_threshold": 35,
    }


class TestSettlementSummarySurrenderPresetFlag:
    def test_losing_side_surrender_ratification_vassalizes_player_nation(self):
        """Player-side surrender must apply the dependency consequence.

        Regression for codex-2026-05-14-settlement-G2-Slice-8: the
        surrender preset authors `from=France, to=Britain` while France
        is the proposer-side member and Britain is the covered enemy. The
        ratification plan must still treat Britain as lord and France as
        vassal instead of resolving the pair as plain peace.
        """
        world = WorldState()
        _install_power_legal_surrender_war(world)
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance",
            return_value=_force_acceptance(),
        ):
            stage_result = stage_settlement_confirm(
                world,
                war_id="war_1",
                settlement_terms=[
                    {"type": "peace"},
                    {"type": "subjugation", "from": "France", "to": "Britain"},
                ],
                covered_enemy_participants=["Britain"],
                actor_nation="France",
                selected_target_nation="Britain",
                proposer_side="defenders",
                caller_kind="player_editor",
                surrender_preset=True,
            )
            assert stage_result["success"] is True, stage_result
            dialogue = world.pending_diplomatic_dialogue
            result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        assert result["mutated"] is True
        assert world.get_diplomatic_state("France", "Britain") == "VASSAL"
        assert world.vassals["France"]["lord"] == "Britain"
        sub_clauses = [
            c for c in result["applied_clauses"] if c.get("type") == "subjugation"
        ]
        assert len(sub_clauses) == 1
        assert sub_clauses[0]["from"] == "France"
        assert sub_clauses[0]["to"] == "Britain"
        assert result["settlement_reactions"]["summary_event"]["surrender_preset"] is True

    def test_summary_event_tags_surrender_preset_true_after_preset_ratification(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance",
            return_value=_force_acceptance(),
        ):
            stage_result = stage_settlement_confirm(
                world,
                war_id="war_1",
                settlement_terms=[
                    {"type": "peace"},
                    {"type": "subjugation", "from": "France", "to": "Britain"},
                ],
                covered_enemy_participants=["France"],
                actor_nation="Britain",
                selected_target_nation="France",
                proposer_side="attackers",
                caller_kind="player_editor",
                surrender_preset=True,
            )
            assert stage_result["success"] is True, stage_result
            dialogue = world.pending_diplomatic_dialogue
            result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        assert result["mutated"] is True
        reactions = result["settlement_reactions"]
        summary = reactions["summary_event"]
        assert summary is not None
        # SC-31 contract: emitted event surfaces the surrender_preset flag.
        assert summary["surrender_preset"] is True

    def test_summary_event_surrender_preset_defaults_false(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance",
            return_value=_force_acceptance(),
        ):
            stage_result = stage_settlement_confirm(
                world,
                war_id="war_1",
                settlement_terms=[
                    {"type": "peace"},
                    {
                        "type": "gold_indemnity",
                        "from": "France",
                        "to": "Britain",
                        "amount": 200,
                    },
                ],
                covered_enemy_participants=["France"],
                actor_nation="Britain",
                selected_target_nation="France",
                proposer_side="attackers",
                caller_kind="player_editor",
                surrender_preset=False,
            )
            assert stage_result["success"] is True, stage_result
            dialogue = world.pending_diplomatic_dialogue
            result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        summary = result["settlement_reactions"]["summary_event"]
        assert summary is not None
        assert summary["surrender_preset"] is False


# ═══════════════════════════════════════════════════════════════════════════
# applied_clauses preview fields for ratified dependency clauses
# ═══════════════════════════════════════════════════════════════════════════


class TestAppliedClausesPreviewFields:
    def test_subjugation_applied_clause_has_pair_state_and_post_state_fields(self):
        world = WorldState()
        _install_power_legal_surrender_war(world)
        with patch(
            "backend.game_logic.settlement_scoring."
            "calculate_common_peace_acceptance",
            return_value=_force_acceptance(),
        ):
            stage_settlement_confirm(
                world,
                war_id="war_1",
                settlement_terms=[
                    {"type": "peace"},
                    {"type": "subjugation", "from": "France", "to": "Britain"},
                ],
                covered_enemy_participants=["France"],
                actor_nation="Britain",
                selected_target_nation="France",
                proposer_side="attackers",
                caller_kind="player_editor",
                surrender_preset=True,
            )
            dialogue = world.pending_diplomatic_dialogue
            result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        sub_clauses = [c for c in result["applied_clauses"] if c.get("type") == "subjugation"]
        assert len(sub_clauses) == 1
        clause = sub_clauses[0]
        # Required preview fields per spec §"Concession And Treaty
        # Conversation Contract" amendment for dependency clauses.
        assert clause["pair_state_transition"] == "WAR -> VASSALAGE"
        assert clause["autonomy_after"] in {"Puppet", "Satellite", "Autonomous"}
        assert isinstance(clause["loyalty_after"], int)
        assert isinstance(clause["tribute_rate_after"], float)
        assert clause["vassal_path"] == "conquest"
        # Vassal Depth Slice 0 (July 16, 2026) made coalition threat
        # player-scoped: Britain (an AI lord) pays NO threat for subjugating
        # France, and the preview must not claim otherwise — pin flipped
        # consciously (post-build review C9). A PLAYER-lord subjugation
        # still previews 25/5.
        assert clause["threat_delta_for_lord"] == 0
        assert "marshal_assimilation_count" in clause


# ═══════════════════════════════════════════════════════════════════════════
# Smoke fixture preset: settlement_surrender
# ═══════════════════════════════════════════════════════════════════════════


class TestSettlementSurrenderSmokeFixture:
    def test_settlement_surrender_smoke_start_seeds_legal_surrender_war(self, monkeypatch):
        monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_SURRENDER)
        world = WorldState()
        # Power cap must now allow Britain to vassalize France.
        from backend.game_logic.diplomacy import check_vassalage_power_cap
        cap = check_vassalage_power_cap(world, "Britain", "France")
        assert cap["allowed"] is True, cap
        # Fixture metadata names the lord candidate explicitly.
        meta = getattr(world, "settlement_smoke_fixture", {})
        assert meta.get("name") == SMOKE_START_SETTLEMENT_SURRENDER
        assert meta.get("surrender_lord_candidate") == "Britain"
        assert meta.get("expected_surrender_dependency") == "subjugation"

    def test_settlement_surrender_smoke_preset_is_ratifiable_without_acceptance_patch(self, monkeypatch):
        monkeypatch.setenv(SMOKE_START_ENV, SMOKE_START_SETTLEMENT_SURRENDER)
        world = WorldState()
        preview = build_settlement_preview(
            world,
            war_id="war_1",
            actor_nation="France",
            settlement_terms=[
                {"type": "peace"},
                {"type": "subjugation", "from": "France", "to": "Britain"},
            ],
            ignore_active_dialogue=True,
        )
        assert preview["success"] is True, preview
        acceptance = preview["settlement_preview"]["acceptance"]
        assert acceptance["verdict"] == "accept"
        assert acceptance["score"] >= acceptance["accept_threshold"]
        assert acceptance["components"]["concession_credit"] >= 100

        dialogue = build_settlement_confirm_dialogue(
            world,
            preview,
            selected_target_nation="Britain",
            caller_kind="player_editor",
            surrender_preset=True,
        )
        assert dialogue["can_ratify"] is True
        assert "confirm_settlement" in dialogue["available_action_ids"]
        assert "re_author_with_concessions" not in dialogue["available_action_ids"]


# ═══════════════════════════════════════════════════════════════════════════
# Voice Bible §16.1 surrender / dependency families
# ═══════════════════════════════════════════════════════════════════════════


class TestVoiceBibleSurrenderDependencyFamilies:
    def test_settlement_voice_templates_register_dependency_families(self):
        from backend.game_logic.diplomatic_templates import (
            SETTLEMENT_VOICE_TEMPLATES,
            resolve_settlement_voice_line,
        )
        required = [
            "settlement_surrender_preset_authored_talleyrand",
            "settlement_surrender_preset_blocked_talleyrand",
            "settlement_dependency_ratified_talleyrand",
            "settlement_dependency_acceptance_castlereagh",
            "settlement_dependency_acceptance_hardenberg",
            "settlement_dependency_acceptance_metternich",
            "settlement_dependency_acceptance_einsiedel",
            "settlement_dependency_rejection_castlereagh",
            "settlement_dependency_rejection_hardenberg",
            "settlement_dependency_rejection_metternich",
            "settlement_dependency_rejection_einsiedel",
            "settlement_liberation_ratified_talleyrand",
        ]
        for key in required:
            assert key in SETTLEMENT_VOICE_TEMPLATES, key
            line = resolve_settlement_voice_line(
                key,
                war_label="France vs Britain",
                vassal_nation="France",
                lord_nation="Britain",
                vassal_kind="conquest vassal",
                proposer_leader="France",
                accepting_leader="Britain",
                former_lord="Britain",
                liberator="France",
                top_blocker="war exhaustion",
            )
            # No TODO/fallback prose per the spec gate.
            assert "TODO" not in line
            assert "fallback" not in line.lower()
            assert line.strip() != ""
