"""G2-Slice-G2c/G2f settlement-agency cut-evidence tests."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping
from unittest.mock import patch

from backend.game_logic.ai_diplomacy import process_settlement_offer_phase
from backend.game_logic.diplomatic_templates import resolve_settlement_voice_line
from backend.game_logic.settlement_preview import (
    handle_incoming_settlement_offer_action,
    handle_settlement_dialogue_action,
    stage_settlement_confirm,
    validate_settlement_terms,
)
from backend.game_logic.settlement_scoring import (
    CANONICAL_CLAUSE_TYPES,
    CLAUSE_CONTROL_SCHEMA,
    SETTLEMENT_DEPENDENCY_CLAUSE_TYPES,
    SETTLEMENT_LIVE_CLAUSE_TYPES,
    SETTLEMENT_MVP_CLAUSE_TYPES,
    SETTLEMENT_RECURRING_GOLD_CLAUSE_TYPES,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# CH-1 stable-seam note: the scorer is patched at
# backend.game_logic.settlement_scoring.calculate_common_peace_acceptance,
# so wrap-the-real side effects must capture the real function at import
# time (a lazy import inside the side effect would fetch the mock).
from backend.game_logic.settlement_scoring import (
    calculate_common_peace_acceptance as _REAL_COMMON_PEACE_ACCEPTANCE,
)


def _install_multi_party_war(world: WorldState) -> Mapping[str, object]:
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
        world.war_scores[pair] = 70
    world.invalidate_war_instance_indexes()
    return war


def _settlement_terms() -> list[dict[str, object]]:
    return [
        {"type": "peace"},
        {"type": "gold_indemnity", "from": "Austria", "to": "France", "amount": 50},
    ]


def _acceptance_accepts(*args, **kwargs):
    real = _REAL_COMMON_PEACE_ACCEPTANCE
    result = real(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    result["side_pressure_score"] = 70
    return result


def _acceptance_rejects(*args, **kwargs):
    real = _REAL_COMMON_PEACE_ACCEPTANCE
    result = real(*args, **kwargs)
    result["score"] = 10
    result["verdict"] = "reject"
    result["hard_stops"] = []
    result["accept_threshold"] = 50
    result["side_pressure_score"] = -20
    return result


def _all_dialogues(world: WorldState) -> list[Mapping[str, object]]:
    dm = world.dialogue_manager
    items = []
    current = dm.peek()
    if isinstance(current, Mapping):
        items.append(current)
    items.extend(d for d in dm.iter_queue() if isinstance(d, Mapping))
    return items


def _code_text() -> str:
    chunks: list[str] = []
    for root in (REPO_ROOT / "backend", REPO_ROOT / "godot-client"):
        for path in root.rglob("*"):
            if path.suffix not in {".py", ".gd", ".tscn"}:
                continue
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def test_settlement_rejection_does_not_produce_ai_counterproposal():
    world = WorldState()
    world.current_turn = 5
    _install_multi_party_war(world)

    with patch(
        "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
        side_effect=_acceptance_accepts,
    ):
        staged = stage_settlement_confirm(
            world,
            war_id="war_1",
            actor_nation="France",
            selected_target_nation="Austria",
            settlement_terms=_settlement_terms(),
        )
    dialogue = staged["diplomatic_dialogue"]

    with patch(
        "backend.game_logic.settlement_scoring.calculate_common_peace_acceptance",
        side_effect=_acceptance_rejects,
    ):
        result = handle_settlement_dialogue_action(
            world,
            action="confirm_settlement",
            dialogue=dialogue,
        )

    assert result["success"] is False
    assert result["error"] == "acceptance_rejected"
    assert result["mutated"] is False
    assert "counterproposal_origin_offer_id" not in result
    assert "incoming_settlement_offer" not in {
        str(item.get("type") or "") for item in _all_dialogues(world)
    }
    assert world.pending_settlement_dialogues == []


def test_request_revision_remains_only_counter_flow_for_incoming_offers():
    world = WorldState()
    world.current_turn = 5
    _install_multi_party_war(world)
    [offer] = process_settlement_offer_phase(world)

    result = handle_incoming_settlement_offer_action(
        world,
        action="request_settlement_revision",
        dialogue=offer,
    )

    assert result["success"] is True
    assert result["action"] == "request_settlement_revision"
    assert result["dialogue_type"] == "settlement_confirm"
    assert result["counter_to_offer_id"] == offer["offer_id"]
    assert result["counter_seed_terms"] == offer["settlement_terms"]
    assert result["counter_seed_covered_participants"] == offer[
        "covered_enemy_participants"
    ]
    assert "counterproposal_origin_offer_id" not in result
    assert world.pending_settlement_dialogues == []


def test_no_counterproposal_constants_or_voice_families_in_code():
    text = _code_text()
    forbidden = [
        "counterproposal_",
        "settlement_counterproposal",
        "counterproposal_origin_offer_id",
    ]
    for token in forbidden:
        assert token not in text
    assert (
        resolve_settlement_voice_line(
            "settlement_counterproposal_arrival_talleyrand",
            war_label="France vs Austria",
        )
        == ""
    )


def test_voluntary_alliance_clause_type_absent_from_schema():
    clause_type = "voluntary_alliance"
    assert clause_type not in CANONICAL_CLAUSE_TYPES
    assert clause_type not in SETTLEMENT_MVP_CLAUSE_TYPES
    assert clause_type not in SETTLEMENT_DEPENDENCY_CLAUSE_TYPES
    assert clause_type not in SETTLEMENT_RECURRING_GOLD_CLAUSE_TYPES
    assert clause_type not in SETTLEMENT_LIVE_CLAUSE_TYPES
    assert clause_type not in CLAUSE_CONTROL_SCHEMA


def test_settlement_editor_remains_forced_alliance_only_for_alliance_authoring():
    assert "forced_alliance" in SETTLEMENT_MVP_CLAUSE_TYPES
    assert "forced_alliance" in SETTLEMENT_LIVE_CLAUSE_TYPES
    assert CLAUSE_CONTROL_SCHEMA["forced_alliance"]["visibility"] == "live"

    valid_forced = validate_settlement_terms([
        {"type": "forced_alliance", "from": "Austria", "to": "France"}
    ])
    assert valid_forced["valid"] is True

    invalid_voluntary = validate_settlement_terms([
        {"type": "voluntary_alliance", "from": "Austria", "to": "France"}
    ])
    assert invalid_voluntary["valid"] is False
    assert invalid_voluntary["error"] == "invalid_clause_type"


def test_voluntary_alliance_no_validator_or_voice_path():
    text = _code_text()
    assert "voluntary_alliance" not in text
    assert "settlement_voluntary_alliance" not in text
    assert (
        resolve_settlement_voice_line(
            "settlement_voluntary_alliance_authored_talleyrand",
            war_label="France vs Austria",
        )
        == ""
    )

