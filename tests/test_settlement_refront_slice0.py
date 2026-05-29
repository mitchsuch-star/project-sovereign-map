"""Slice 0 — interim picker valid-by-construction band-aid.

Settlement Conversational Re-front spec §13 (P1) + §16: the cleanup spec
(`SETTLEMENT_UI_CLEANUP_SPEC.md` line 601) promised that a clause type whose
picker has zero valid options has its Add Clause control disabled, and line
618 named a test for it — neither the implementation nor the test ever
landed. Slice 0 lands that contract:

- `_build_clause_control_schema_for_review` computes ``enabled`` per clause
  type from picker emptiness (it previously hardcoded ``enabled=True``), and
  carries a humanized ``disabled_reason_display`` when disabled.
- liberation's ``vassal_nation`` picker offers only real vassals — the
  ``vassal_options or nation_options`` fallback that let non-vassals
  (including France) appear is removed — so the France-liberates-France
  nonsense found during Gate 4 smoke is not constructible.

This is the symptom patch; the full conversational re-front (Slices 1–3)
builds the cure on top.
"""

from __future__ import annotations

from backend.game_logic.settlement_preview import (
    _build_clause_control_schema_for_review,
    validate_settlement_terms,
)
from backend.game_logic.settlement_scoring import SETTLEMENT_LIVE_CLAUSE_TYPES
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


def _install_war(world: WorldState) -> dict:
    """France + Saxony vs Austria + Prussia, no vassals by default."""
    war = make_synthetic_war_instance(
        "war_1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
    )
    world.war_instances["war_1"] = war
    for pair in war["active_diplo_keys"]:
        world.diplomatic_states[pair] = "WAR"
    world.invalidate_war_instance_indexes()
    return war


def test_clause_add_disabled_when_picker_filter_empty_for_each_live_clause():
    """Cleanup-spec line-601 contract / line-618 test (never landed before).

    With no world context every picker filter is empty, so every live clause
    type that exposes a picker is disabled; ``peace`` (no fields) stays
    enabled. Disabled rows remain schema keys so the client greys them out
    rather than the type silently vanishing.
    """
    schema = _build_clause_control_schema_for_review()

    # Disabled rows are still keys — the schema covers the whole live set.
    assert set(schema) == set(SETTLEMENT_LIVE_CLAUSE_TYPES)

    for clause_type, row in schema.items():
        has_picker = any(
            field.get("control") == "picker"
            for field in row["fields"].values()
        )
        if has_picker:
            assert row["enabled"] is False, clause_type
            assert row["disabled_reason_display"], clause_type
        else:
            assert row["enabled"] is True, clause_type
            assert row["disabled_reason_display"] is None, clause_type


def test_liberation_vassal_picker_excludes_non_vassals():
    """liberation's ``vassal_nation`` picker offers only current vassals;
    non-vassals (France, war participants) can never appear."""
    world = WorldState()
    war = _install_war(world)
    world.vassals["Bavaria"] = {"lord": "France", "lord_nation": "France"}

    schema = _build_clause_control_schema_for_review(
        world,
        war_instance=war,
        covered_enemy_participants=["Austria", "Prussia"],
    )
    vassal_field = schema["liberation"]["fields"]["vassal_nation"]
    option_ids = {opt["id"] for opt in vassal_field["options"]}

    assert option_ids == {"Bavaria"}
    assert "France" not in option_ids
    assert "Austria" not in option_ids
    assert "Prussia" not in option_ids
    # A real vassal exists, so the liberation row is live.
    assert schema["liberation"]["enabled"] is True


def test_clause_control_schema_enabled_false_carries_disabled_reason():
    """A disabled clause-type row carries a non-empty humanized reason; an
    enabled row carries ``None``. With no vassals, liberation is the disabled
    row and its reason names the empty vassal picker."""
    world = WorldState()
    war = _install_war(world)  # no vassals → liberation picker empty

    schema = _build_clause_control_schema_for_review(
        world,
        war_instance=war,
        covered_enemy_participants=["Austria", "Prussia"],
    )

    liberation = schema["liberation"]
    assert liberation["enabled"] is False
    assert isinstance(liberation["disabled_reason_display"], str)
    assert liberation["disabled_reason_display"]
    assert "Vassal to liberate" in liberation["disabled_reason_display"]

    # Invariant across the whole schema: enabled ⇒ no reason; disabled ⇒ reason.
    for clause_type, row in schema.items():
        if row["enabled"]:
            assert row["disabled_reason_display"] is None, clause_type
        else:
            assert row["disabled_reason_display"], clause_type


def test_settlement_no_self_referential_clause():
    """France-liberates-France is killed two ways: it is not constructible
    (France is never a vassal-picker option) and a tampered self-referential
    liberation clause is rejected pre-stage by the validator (V4)."""
    world = WorldState()
    war = _install_war(world)
    world.vassals["Bavaria"] = {"lord": "France", "lord_nation": "France"}

    # (a) Not constructible — France can never be picked as the vassal.
    schema = _build_clause_control_schema_for_review(
        world,
        war_instance=war,
        covered_enemy_participants=["Austria", "Prussia"],
    )
    vassal_options = {
        opt["id"]
        for opt in schema["liberation"]["fields"]["vassal_nation"]["options"]
    }
    assert "France" not in vassal_options

    # (b) Rejected pre-stage — a tampered self-referential clause fails
    # validation (France is not a vassal of anyone).
    terms = [
        {
            "type": "liberation",
            "vassal_nation": "France",
            "lord_nation": "France",
            "liberator": "France",
        }
    ]
    result = validate_settlement_terms(terms, world=world, war_instance=war)
    assert result["valid"] is False
    assert result["error"] == "liberation_target_not_vassal"
