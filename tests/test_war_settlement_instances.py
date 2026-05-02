"""Slice A2 tests — war-entry threading across every WAR seam.

Slice A2 of `WAR_SETTLEMENT_ALLY_PARTICIPATION_SPEC.md` v1.24 §7.2 wires
`ensure_war_instance_for_pair(...)` and `attach_pair_to_war_instance(...)`
into every WAR-entry seam. This file exercises each inventoried seam and
verifies the spec invariant holds afterwards.

`WAR_ENTRY_SEAMS_UNDER_TEST` is the durable checklist required by the
implementation plan §"Slice A - War Identity And Grouping". Adding a new
WAR seam to the codebase MUST also add an entry here AND a focused test.
The list is asserted in a structural test below so future contributors
cannot quietly drop coverage.
"""

from __future__ import annotations

from typing import Dict

import pytest

from backend.game_logic.diplomacy import (
    _process_armistice_expiration,
    _process_war_cascade,
    accept_counter_bargain,
    declare_war,
    resolve_join_opportunity,
    set_diplomatic_state,
)
from backend.game_logic.settlement_helpers import (
    CascadeContext,
    WAR_INSTANCE_MERGE_REQUIRED,
    WAR_INSTANCE_SIDE_CONFLICT,
    assert_war_instance_invariants,
    attach_pair_to_war_instance,
    attach_participant_to_war_instance,
    ensure_war_instance_for_pair,
    mark_pair_armistice,
    resolve_pair_to_resolved,
    validate_war_declaration,
)
from backend.game_logic.vassal import (
    AUTONOMY_SATELLITE,
    LOYALTY_MAX,
    TRIBUTE_RATES,
    check_vassal_rebellion,
    release_vassal,
)
from backend.models.world_state import WorldState


def _install_vassal(world: WorldState, lord: str, vassal: str, *, loyalty: int = 60) -> None:
    """Install a vassal directly without going through the treaty validation.

    Bypasses `create_vassal_treaty` so test setup can pin vassal state
    onto a `_clean_world()` without first negotiating up to OPEN_BORDERS.
    Mirrors the runtime shape for `world.vassals[name]`.
    """
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": AUTONOMY_SATELLITE,
        "path": "treaty",
        "created_turn": int(world.current_turn),
        "tribute_rate": TRIBUTE_RATES[AUTONOMY_SATELLITE],
        "carved_from": None,
        "regions": None,
    }
    world.diplomatic_states[world._make_diplo_key(lord, vassal)] = "VASSAL"
    world.invalidate_active_nations_cache()


# ---------------------------------------------------------------------------
# WAR-entry seam inventory (mandatory checklist per plan §"Slice A - War
# Identity And Grouping" — A2 must fail if a listed seam loses coverage).
# ---------------------------------------------------------------------------

WAR_ENTRY_SEAMS_UNDER_TEST = (
    "player_declaration",
    "ai_declaration",
    "coalition_declaration",
    "vassal_rebellion",
    "vassal_release_rebellion",
    "commitment_paradox_outcome",
    "scripted_or_debug_war_entry",
    "join_opportunity_acceptance",
    "counter_bargain_acceptance",
    "armistice_collapse",
    "combat_triggered_auto_war_fallback",
    "defensive_cascade_attach",
    "offensive_cascade_attach",
    "vassal_defensive_auto_join",
    "vassal_offensive_auto_join",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clean_world(player_nation: str = "France") -> WorldState:
    """A WorldState with diplomacy cleared so the invariant only sees test data."""
    world = WorldState(player_nation=player_nation)
    world.diplomatic_states.clear()
    world.invalidate_war_instance_indexes()
    return world


def _set_state(world: WorldState, a: str, b: str, state: str) -> None:
    world.diplomatic_states[world._make_diplo_key(a, b)] = state


def _pair(a: str, b: str) -> str:
    return "|".join(sorted((a, b)))


def _active_instances(world: WorldState) -> Dict[str, Dict]:
    return {
        wid: inst
        for wid, inst in world.war_instances.items()
        if inst.get("ended_turn") is None
    }


# ---------------------------------------------------------------------------
# Seam inventory structural guard
# ---------------------------------------------------------------------------


def test_war_entry_seam_inventory_is_durable():
    """The inventory must cover every live WAR seam A2 wires.

    If a future PR adds a new WAR-entry seam (new executor path, new
    cheat, new spec mechanic), the contributor MUST add it here AND
    cover it with a focused test below. This guard fails fast if the
    list is empty or accidentally renamed.
    """
    required = {
        "player_declaration",
        "ai_declaration",
        "coalition_declaration",
        "vassal_rebellion",
        "vassal_release_rebellion",
        "commitment_paradox_outcome",
        "scripted_or_debug_war_entry",
        "join_opportunity_acceptance",
        "counter_bargain_acceptance",
        "armistice_collapse",
        "combat_triggered_auto_war_fallback",
        "defensive_cascade_attach",
        "offensive_cascade_attach",
        "vassal_defensive_auto_join",
        "vassal_offensive_auto_join",
    }
    assert required.issubset(set(WAR_ENTRY_SEAMS_UNDER_TEST))
    # Inventory must be unique.
    assert len(WAR_ENTRY_SEAMS_UNDER_TEST) == len(set(WAR_ENTRY_SEAMS_UNDER_TEST))


# ---------------------------------------------------------------------------
# Direct helper contract
# ---------------------------------------------------------------------------


def test_validate_war_declaration_rejects_self_war():
    world = _clean_world()
    result = validate_war_declaration(
        world, "France", "France", entry_path="war_declaration"
    )
    assert result["ok"] is False
    assert result["error"] == WAR_INSTANCE_SIDE_CONFLICT


def test_ensure_war_instance_creates_skeleton_with_originator_and_target():
    world = _clean_world()
    result = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    assert result["ok"] is True
    assert result["created_new"] is True
    war_id = result["war_id"]
    instance = world.war_instances[war_id]
    assert instance["originator"] == "France"
    assert instance["origin_target"] == "Austria"
    assert instance["origin_diplo_key"] == _pair("France", "Austria")
    assert instance["attackers"] == ["France"]
    assert instance["defenders"] == ["Austria"]
    assert instance["attacker_leader"] == "France"
    assert instance["defender_leader"] == "Austria"
    assert instance["active_diplo_keys"] == [_pair("France", "Austria")]
    pair_meta = instance["diplo_key_meta"][_pair("France", "Austria")]
    assert pair_meta["pair_status"] == "war"
    assert pair_meta["attacker"] == "France"
    assert pair_meta["defender"] == "Austria"


def test_ensure_war_instance_reuses_existing_pair_owner():
    world = _clean_world()
    first = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    second = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    assert second["created_new"] is False
    assert second["reused"] is True
    assert second["war_id"] == first["war_id"]


def test_ensure_war_instance_attaches_new_pair_to_existing_attacker_war():
    """If France is already attacker of war_1 (vs Austria) and now declares
    war on Russia, the new pair joins war_1 as another front (concurrent
    cobelligerent rule)."""
    world = _clean_world()
    first = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    war_id = first["war_id"]
    second = ensure_war_instance_for_pair(
        world, "France", "Russia", entry_path="war_declaration"
    )
    assert second["war_id"] == war_id
    assert second["created_new"] is False
    instance = world.war_instances[war_id]
    assert "Russia" in instance["defenders"]
    assert _pair("France", "Russia") in instance["active_diplo_keys"]
    assert instance["side_by_nation"]["Russia"] == "defenders"


def test_ensure_war_instance_returns_side_conflict_for_same_side_pair():
    """If France and Saxony are already on the same side of war_1 (against
    Austria), trying to declare a NEW war between them must hard-stop:
    they cannot fight each other while co-belligerents."""
    world = _clean_world()
    first = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    war_id = first["war_id"]
    # Saxony joins France's attacker side as a co-belligerent vs Austria.
    attach_pair_to_war_instance(
        world, war_id, "Saxony", "Austria", entry_path="ally_entry"
    )
    # Now France tries to declare war on Saxony — both are on the
    # attackers side of war_id, so a new pair would put one of them on
    # both sides of the same conflict.
    result = ensure_war_instance_for_pair(
        world, "France", "Saxony", entry_path="war_declaration"
    )
    assert result["ok"] is False
    assert result["error"] == WAR_INSTANCE_SIDE_CONFLICT
    assert result["details"]["war_id"] == war_id


def test_ensure_war_instance_runs_merge_then_reveals_side_conflict():
    """A3: when both nations live in distinct active war_instances, the
    transitive merge runs first; the post-merge re-validation hard-stops
    only if the new pair is intrinsically incompatible (both nations on
    the same side of the merged war)."""
    world = _clean_world()
    war_a = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    war_b = ensure_war_instance_for_pair(
        world, "Russia", "Prussia", entry_path="war_declaration"
    )
    assert war_a["war_id"] != war_b["war_id"]
    # Austria (defender of war_a) declares on Prussia (defender of war_b).
    # Merge runs and consolidates; both Austria and Prussia land on the
    # `defenders` side of the survivor, so the new pair would put one of
    # them on both sides -- side_conflict is the correct hard stop.
    result = ensure_war_instance_for_pair(
        world, "Austria", "Prussia", entry_path="war_declaration"
    )
    assert result["ok"] is False
    assert result["error"] == WAR_INSTANCE_SIDE_CONFLICT
    # Merge consolidated war_a/war_b into a single survivor.
    active = _active_instances(world)
    assert len(active) == 1
    surviving_id = next(iter(active))
    assert surviving_id in (war_a["war_id"], war_b["war_id"])
    assert {"France", "Austria", "Russia", "Prussia"}.issubset(
        set(active[surviving_id]["active_participants"])
    )


def test_attach_pair_to_war_instance_is_idempotent():
    world = _clean_world()
    result = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    war_id = result["war_id"]
    # Re-attach the existing pair — should be a no-op aside from refresh.
    attach_result = attach_pair_to_war_instance(
        world, war_id, "France", "Austria", entry_path="war_declaration"
    )
    assert attach_result["ok"] is True
    instance = world.war_instances[war_id]
    assert instance["attackers"].count("France") == 1
    assert instance["defenders"].count("Austria") == 1
    assert instance["active_diplo_keys"].count(_pair("France", "Austria")) == 1


def test_attach_participant_rejects_side_conflict():
    world = _clean_world()
    result = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    war_id = result["war_id"]
    bad = attach_participant_to_war_instance(
        world, war_id, "Austria", side="attackers", entry_path="bad"
    )
    assert bad["ok"] is False
    assert bad["error"] == WAR_INSTANCE_SIDE_CONFLICT


# ---------------------------------------------------------------------------
# declare_war + cascade integration
# ---------------------------------------------------------------------------


def test_player_declaration_creates_war_instance_and_ledger_uses_war_id():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")

    result = declare_war(world, "France", "Austria")

    assert result["success"] is True
    war_id = result["war_id"]
    assert war_id in world.war_instances
    assert world.war_instances[war_id]["originator"] == "France"
    assert world.war_instances[war_id]["origin_target"] == "Austria"
    # War-entry ledger event must use the allocated war_id (not war_{episode}).
    ledger_events = [
        e for e in world.event_log if e.get("type") == "war_entry_ledger"
    ]
    assert ledger_events, "expected a war_entry_ledger event"
    assert ledger_events[-1]["war_id"] == war_id
    assert ledger_events[-1]["war_id"].startswith("war_")
    assert "episode" not in ledger_events[-1]["war_id"]
    assert_war_instance_invariants(world, context="post_player_declaration")


def test_ai_declaration_creates_war_instance():
    world = _clean_world()
    _set_state(world, "Russia", "Austria", "PEACE")

    result = declare_war(world, "Russia", "Austria")

    assert result["success"] is True
    war_id = result["war_id"]
    instance = world.war_instances[war_id]
    assert instance["originator"] == "Russia"
    assert instance["origin_target"] == "Austria"
    assert_war_instance_invariants(world, context="post_ai_declaration")


def test_defensive_cascade_attaches_to_root_war_id():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "Austria", "Prussia", "DEFENSIVE_ALLIANCE")

    result = declare_war(world, "France", "Austria")

    war_id = result["war_id"]
    instance = world.war_instances[war_id]
    # Prussia was pulled in defensively — must attach to same war_id.
    assert "Prussia" in instance["defenders"]
    assert _pair("France", "Prussia") in instance["active_diplo_keys"]
    assert instance["diplo_key_meta"][_pair("France", "Prussia")]["pair_status"] == "war"
    # Only ONE active war_instance — cascade did not split a parallel war.
    assert len(_active_instances(world)) == 1
    assert_war_instance_invariants(world, context="post_defensive_cascade")


def test_offensive_cascade_attaches_to_root_war_id():
    world = _clean_world()
    _set_state(world, "France", "Saxony", "ALLIANCE")  # Saxony cascades offensively
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "Saxony", "Austria", "PEACE")

    result = declare_war(world, "France", "Austria")

    war_id = result["war_id"]
    instance = world.war_instances[war_id]
    assert "Saxony" in instance["attackers"]
    assert _pair("Austria", "Saxony") in instance["active_diplo_keys"]
    assert len(_active_instances(world)) == 1
    assert_war_instance_invariants(world, context="post_offensive_cascade")


def test_vassal_defensive_auto_join_attaches_to_root_war_id():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _install_vassal(world, "Austria", "Saxony")
    _set_state(world, "France", "Saxony", "PEACE")

    result = declare_war(world, "France", "Austria")

    war_id = result["war_id"]
    instance = world.war_instances[war_id]
    assert "Saxony" in instance["defenders"]
    assert _pair("France", "Saxony") in instance["active_diplo_keys"]
    assert_war_instance_invariants(world, context="post_vassal_defensive_join")


def test_vassal_offensive_auto_join_attaches_to_root_war_id():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _install_vassal(world, "France", "Saxony")
    _set_state(world, "Saxony", "Austria", "PEACE")

    result = declare_war(world, "France", "Austria")

    war_id = result["war_id"]
    instance = world.war_instances[war_id]
    assert "Saxony" in instance["attackers"]
    assert _pair("Austria", "Saxony") in instance["active_diplo_keys"]
    assert_war_instance_invariants(world, context="post_vassal_offensive_join")


def test_recursive_cascade_uses_same_war_id_for_all_entries():
    """Honored, vassal-cascading, and offensive-cascading allies all attach
    to the SAME war_id — never the legacy episode-derived id."""
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "Austria", "Prussia", "DEFENSIVE_ALLIANCE")
    _set_state(world, "France", "Saxony", "ALLIANCE")
    _set_state(world, "Saxony", "Austria", "PEACE")
    _install_vassal(world, "Austria", "Bavaria")

    result = declare_war(world, "France", "Austria")
    war_id = result["war_id"]
    instance = world.war_instances[war_id]
    # All non-principals attached to one instance.
    assert "Prussia" in instance["defenders"]
    assert "Saxony" in instance["attackers"]
    assert "Bavaria" in instance["defenders"]
    # Exactly one active war_instance — no sibling instance was created.
    assert len(_active_instances(world)) == 1
    assert_war_instance_invariants(world, context="recursive_cascade")


# ---------------------------------------------------------------------------
# Vassal rebellion + vassal-release rebellion seams
# ---------------------------------------------------------------------------


def test_vassal_rebellion_creates_war_instance_before_cascade():
    world = _clean_world()
    _install_vassal(world, "France", "Saxony")
    _set_state(world, "France", "Saxony", "VASSAL")
    # Force loyalty to zero so rebellion fires.
    world.vassals["Saxony"]["loyalty"] = 0

    events = check_vassal_rebellion(world)

    rebellion_events = [e for e in events if e.get("type") == "vassal_rebellion"]
    assert rebellion_events, "expected vassal_rebellion event"
    # War instance owns the Saxony↔France pair with Saxony as originator.
    war_pairs = [
        wid
        for wid, inst in _active_instances(world).items()
        if _pair("France", "Saxony") in inst["active_diplo_keys"]
    ]
    assert len(war_pairs) == 1
    war_id = war_pairs[0]
    instance = world.war_instances[war_id]
    assert instance["originator"] == "Saxony"
    assert instance["origin_target"] == "France"
    assert_war_instance_invariants(world, context="post_vassal_rebellion")


def test_vassal_release_rebellion_creates_war_instance():
    world = _clean_world()
    _install_vassal(world, "France", "Saxony")
    _set_state(world, "France", "Saxony", "VASSAL")

    result = release_vassal(world, "Saxony", rebellion=True)

    assert result["success"] is True
    war_pairs = [
        wid
        for wid, inst in _active_instances(world).items()
        if _pair("France", "Saxony") in inst["active_diplo_keys"]
    ]
    assert len(war_pairs) == 1
    instance = world.war_instances[war_pairs[0]]
    assert instance["originator"] == "France"
    assert instance["origin_target"] == "Saxony"
    assert_war_instance_invariants(world, context="post_vassal_release_rebellion")


# ---------------------------------------------------------------------------
# Direct ally-entry seams
# ---------------------------------------------------------------------------


def test_resolve_join_opportunity_attaches_to_promiser_war():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "France", "Saxony", "ALLIANCE")
    _set_state(world, "Saxony", "Austria", "PEACE")

    # France declares war on Austria first — Saxony has ALLIANCE so cascade
    # would normally pull it in. We test the DIRECT-entry seam where Saxony
    # is asked again later via resolve_join_opportunity.
    declare_war(world, "France", "Austria", suppress_unresolved_offensive_cascade=True)

    # Saxony should NOT yet be at war with Austria.
    assert not world.is_at_war("Saxony", "Austria")

    opportunity = {
        "id": 1,
        "beneficiary": "Saxony",
        "named_enemy": "Austria",
        "request_type": "offensive_ally_request",
        "promiser": "France",
        "hard_blocks": [],
        "origin_episode_id": "ep_1",
    }
    result = resolve_join_opportunity(world, opportunity, "accept")
    assert result["success"] is True
    assert result["joined"] is True

    # Should attach to the existing war (one active instance), Saxony joins attackers.
    active = _active_instances(world)
    assert len(active) == 1
    war_id, instance = next(iter(active.items()))
    assert "Saxony" in instance["attackers"]
    assert _pair("Austria", "Saxony") in instance["active_diplo_keys"]
    assert result.get("war_id") == war_id
    assert_war_instance_invariants(world, context="post_resolve_join_opportunity")


def test_accept_counter_bargain_attaches_to_war():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "France", "Saxony", "ALLIANCE")
    _set_state(world, "Saxony", "Austria", "PEACE")

    declare_war(world, "France", "Austria", suppress_unresolved_offensive_cascade=True)

    counter = {
        "type": "war_entry_counter_bargain",
        "promiser": "France",
        "beneficiary": "Saxony",
        "named_enemy": "Austria",
        "demanded_region": "Bohemia",
        "war_entry_score": {"score": 35},
        "reroll_key": "",
    }
    result = accept_counter_bargain(world, counter)
    assert result["success"] is True
    assert result["joined"] is True

    active = _active_instances(world)
    assert len(active) == 1
    war_id = result["war_id"]
    instance = world.war_instances[war_id]
    assert "Saxony" in instance["attackers"]
    assert _pair("Austria", "Saxony") in instance["active_diplo_keys"]
    assert_war_instance_invariants(world, context="post_counter_bargain_accept")


# ---------------------------------------------------------------------------
# Armistice collapse / resolution
# ---------------------------------------------------------------------------


def test_armistice_collapse_reuses_same_war_id():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")

    declare_war(world, "France", "Austria")
    active_before = list(_active_instances(world).keys())
    assert len(active_before) == 1
    original_war_id = active_before[0]

    # Move the pair to ARMISTICE manually, then mark pair_meta accordingly.
    _set_state(world, "France", "Austria", "ARMISTICE")
    mark_pair_armistice(world, _pair("France", "Austria"))

    # Hostile relations + 5 turns -> collapse to WAR.
    world.nation_relations[world._make_diplo_key("France", "Austria")] = -90
    world.armistice_turns = {world._make_diplo_key("France", "Austria"): 5}
    _process_armistice_expiration(world)

    # War resumed: only ONE active war instance, same war_id.
    active_after = list(_active_instances(world).keys())
    assert active_after == [original_war_id]
    instance = world.war_instances[original_war_id]
    pair_meta = instance["diplo_key_meta"][_pair("France", "Austria")]
    assert pair_meta["pair_status"] == "war"
    assert_war_instance_invariants(world, context="post_armistice_collapse")


def test_armistice_to_peace_moves_pair_to_resolved_diplo_keys():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")

    declare_war(world, "France", "Austria")
    war_id = list(_active_instances(world).keys())[0]

    _set_state(world, "France", "Austria", "ARMISTICE")
    mark_pair_armistice(world, _pair("France", "Austria"))

    # Friendly relations + 5 turns -> ARMISTICE expires to PEACE.
    world.nation_relations[world._make_diplo_key("France", "Austria")] = 0
    world.armistice_turns = {world._make_diplo_key("France", "Austria"): 5}
    _process_armistice_expiration(world)

    instance = world.war_instances[war_id]
    pair_key = _pair("France", "Austria")
    assert pair_key not in instance["active_diplo_keys"]
    assert pair_key in instance["resolved_diplo_keys"]
    assert instance["diplo_key_meta"][pair_key]["pair_status"] == "resolved"


# ---------------------------------------------------------------------------
# Index invalidation + concurrent wars + invariant integration
# ---------------------------------------------------------------------------


def test_war_instance_index_rebuilds_after_declaration():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    declare_war(world, "France", "Austria")

    leader_index = world.get_war_instances_by_leader()
    participant_index = world.get_war_instances_by_participant()

    assert "France" in leader_index
    assert "Austria" in leader_index
    assert leader_index["France"][0].startswith("war_")
    assert "France" in participant_index
    assert "Austria" in participant_index


def test_concurrent_wars_create_independent_instances_when_sides_clash():
    """If France is attacker in war_1 (vs Austria) and Russia attacks France,
    Russia cannot put France on attackers of a new pair (France is already
    attacker; defender role conflicts) so a NEW war_2 is allocated."""
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "France", "Russia", "PEACE")

    first = declare_war(world, "France", "Austria")
    second = declare_war(world, "Russia", "France")

    assert first["success"] and second["success"]
    war_a = first["war_id"]
    war_b = second["war_id"]
    # Spec §9.2 explicitly supports concurrent wars per nation.
    assert war_a != war_b
    inst_a = world.war_instances[war_a]
    inst_b = world.war_instances[war_b]
    assert inst_a["side_by_nation"]["France"] == "attackers"
    assert inst_b["side_by_nation"]["France"] == "defenders"
    assert_war_instance_invariants(world, context="concurrent_wars")


def test_invariant_holds_for_full_combined_cascade_and_vassal_fixture():
    """End-to-end: declare a war that triggers offensive cascade + vassal
    auto-join + defensive cascade, then assert invariants hold."""
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "Austria", "Prussia", "DEFENSIVE_ALLIANCE")
    _set_state(world, "France", "Saxony", "ALLIANCE")
    _set_state(world, "Saxony", "Austria", "PEACE")
    _install_vassal(world, "Austria", "Bavaria")
    _install_vassal(world, "France", "Naples")

    declare_war(world, "France", "Austria")
    assert_war_instance_invariants(world, context="full_combined_fixture")
    active = _active_instances(world)
    assert len(active) == 1
    war_id, instance = next(iter(active.items()))
    assert {"France", "Saxony", "Naples"}.issubset(set(instance["attackers"]))
    assert {"Austria", "Prussia", "Bavaria"}.issubset(set(instance["defenders"]))


def test_resolve_pair_to_resolved_handles_unknown_pair_safely():
    world = _clean_world()
    result = resolve_pair_to_resolved(world, _pair("France", "Austria"))
    assert result["ok"] is False
    assert result["war_id"] is None


def test_mark_pair_armistice_handles_unknown_pair_safely():
    world = _clean_world()
    result = mark_pair_armistice(world, _pair("France", "Austria"))
    assert result["ok"] is False
    assert result["war_id"] is None


def test_cascade_context_propagates_through_legacy_kwargs():
    """Callers that haven't migrated to ctx still get a synthesized
    CascadeContext so behavior is preserved during the transition."""
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "Austria", "Prussia", "DEFENSIVE_ALLIANCE")

    # Manually allocate the war_instance so we control the war_id.
    seed = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="test_seed"
    )
    war_id = seed["war_id"]
    set_diplomatic_state(world, "France", "Austria", "WAR", "test_seed")

    ctx = CascadeContext(war_id=war_id, root_aggressor="France")
    cascade = _process_war_cascade(
        world, "France", "Austria", processed={"France", "Austria"}, ctx=ctx
    )
    assert cascade  # at least the defensive cascade fired
    instance = world.war_instances[war_id]
    assert "Prussia" in instance["defenders"]
    assert _pair("France", "Prussia") in instance["active_diplo_keys"]
    assert_war_instance_invariants(world, context="legacy_cascade_kwargs")


def test_validate_war_declaration_attach_when_only_one_nation_in_existing_war():
    """If France is attacker of war_1 and now declares war on Russia (not
    yet in any war), attaching the new pair to war_1 keeps France on the
    attacker side and adds Russia as a new defender on the same front."""
    world = _clean_world()
    seed = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    war_id = seed["war_id"]
    second = ensure_war_instance_for_pair(
        world, "France", "Russia", entry_path="war_declaration"
    )
    assert second["war_id"] == war_id
    instance = world.war_instances[war_id]
    assert "Russia" in instance["defenders"]


def test_declare_war_blocks_when_post_merge_revalidation_finds_side_conflict():
    """A3: declare_war must NOT mutate the (Austria, Prussia) state to WAR
    when the post-merge re-validation reveals a side conflict, even though
    the merge transaction itself succeeded."""
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    _set_state(world, "Russia", "Prussia", "PEACE")
    declare_war(world, "France", "Austria")
    declare_war(world, "Russia", "Prussia")

    # Austria (defender of war_1) tries to declare on Prussia (defender of
    # war_2). A3 merges war_1 + war_2 into a single survivor; on the
    # survivor both Austria and Prussia are defenders -- the new pair is a
    # genuine side conflict.
    result = declare_war(world, "Austria", "Prussia")

    assert result["success"] is False
    assert result.get("error") == WAR_INSTANCE_SIDE_CONFLICT
    # The (Austria, Prussia) pair must not have advanced to WAR.
    assert (
        world.get_diplomatic_state("Austria", "Prussia") != "WAR"
    ), "side-conflict hard-stop must precede the new pair's WAR mutation"


def test_cascade_attach_failure_does_not_mutate_war_state():
    """Cascade attach failures must stop before the WAR edge is visible."""
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    declare_war(world, "France", "Austria", suppress_unresolved_offensive_cascade=True)
    war_id = list(_active_instances(world).keys())[0]
    attach_pair_to_war_instance(
        world, war_id, "Prussia", "Austria", entry_path="ally_entry"
    )
    _set_state(world, "Prussia", "Austria", "WAR")
    _set_state(world, "France", "Prussia", "PEACE")
    _set_state(world, "France", "Britain", "PEACE")
    _set_state(world, "Britain", "Prussia", "DEFENSIVE_ALLIANCE")

    result = declare_war(world, "France", "Britain", suppress_unresolved_offensive_cascade=True)

    assert result["success"] is True
    assert world.get_diplomatic_state("France", "Prussia") != "WAR"
    assert _pair("France", "Prussia") not in world.war_instances[war_id]["active_diplo_keys"]
    assert any(e.get("type") == "war_cascade_blocked" for e in world.event_log)
    assert_war_instance_invariants(world, context="blocked_cascade")


def test_attach_pair_triggers_merge_when_pair_owned_by_other_active_instance():
    """A3: attaching a pair that already lives in a different active
    war_instance triggers `merge_war_instances(...)`, retargets `war_id` to
    the survivor, and completes the attachment idempotently."""
    world = _clean_world()
    first = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration"
    )
    second = ensure_war_instance_for_pair(
        world, "Russia", "Prussia", entry_path="war_declaration"
    )
    result = attach_pair_to_war_instance(
        world,
        second["war_id"],
        "France",
        "Austria",
        entry_path="cross_war_attach",
    )

    assert result["ok"] is True
    # The merge folded `second` into `first` (oldest survives).
    surviving = result["war_id"]
    assert surviving == first["war_id"]
    active = _active_instances(world)
    assert len(active) == 1
    assert surviving in active
    instance = active[surviving]
    # France/Austria pair is still present (idempotent re-attach), and
    # Russia/Prussia pair was carried in by the merge.
    assert _pair("France", "Austria") in instance["active_diplo_keys"]
    assert _pair("Russia", "Prussia") in instance["active_diplo_keys"]


def test_armistice_collapse_blocks_on_merge_required_without_war_mutation():
    world = _clean_world()
    declare_war(world, "France", "Austria")
    declare_war(world, "Russia", "Prussia")
    armistice_pair = _pair("Austria", "Prussia")
    _set_state(world, "Austria", "Prussia", "ARMISTICE")
    world.nation_relations[armistice_pair] = -90
    world.armistice_turns = {armistice_pair: 5}

    events = _process_armistice_expiration(world)

    assert world.get_diplomatic_state("Austria", "Prussia") == "ARMISTICE"
    assert any(e.get("type") == "armistice_expired_war_blocked" for e in events)
    assert_war_instance_invariants(world, context="blocked_armistice_collapse")


def test_counter_bargain_hard_stop_when_post_merge_finds_side_conflict():
    """A3: accept_counter_bargain hard-stops without mutating bargains or
    diplomatic_states when the post-merge re-validation reveals a side
    conflict on the bargain's would-be war pair."""
    world = _clean_world()
    declare_war(world, "France", "Austria")
    declare_war(world, "Russia", "Prussia")
    before = dict(world.diplomatic_commitments)
    counter = {
        "type": "war_entry_counter_bargain",
        "promiser": "France",
        "beneficiary": "Austria",
        "named_enemy": "Prussia",
        "demanded_region": "Bohemia",
    }

    result = accept_counter_bargain(world, counter)

    assert result["success"] is False
    assert result["error"] == WAR_INSTANCE_SIDE_CONFLICT
    assert world.diplomatic_commitments == before
    assert world.get_diplomatic_state("Austria", "Prussia") != "WAR"


def test_scripted_debug_war_entry_allocates_war_instance():
    from backend.commands.executor import CommandExecutor

    world = _clean_world()
    result = CommandExecutor()._execute_cheat(
        {
            "action": "cheat",
            "cheat_type": "set_diplo_state",
            "cheat_args": ["Prussia", "WAR"],
        },
        {"world": world, "debug_mode": True},
    )

    assert result["success"] is True
    assert world.is_at_war("France", "Prussia")
    assert len(_active_instances(world)) == 1
    assert_war_instance_invariants(world, context="debug_war_entry")


def test_coalition_declaration_threads_war_instance():
    from backend.game_logic.coalition import form_coalition

    world = _clean_world()
    _set_state(world, "France", "Prussia", "PEACE")
    _set_state(world, "France", "Austria", "PEACE")

    result = form_coalition(["Prussia", "Austria"], world)

    assert result["success"] is True
    active = _active_instances(world)
    assert len(active) == 1
    instance = next(iter(active.values()))
    assert _pair("France", "Prussia") in instance["active_diplo_keys"]
    assert _pair("Austria", "France") in instance["active_diplo_keys"]
    assert_war_instance_invariants(world, context="coalition_declaration")


def test_commitment_paradox_outcome_threads_war_instance():
    from backend.commands.executor import CommandExecutor

    world = _clean_world()
    player = world.player_nation
    _set_state(world, player, "Prussia", "ALLIANCE")
    _set_state(world, player, "Austria", "ALLIANCE")
    _set_state(world, "Austria", "Prussia", "PEACE")
    declare_war(world, "Prussia", "Austria")
    if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
        world.dialogue_manager.promote_if_empty()

    result = CommandExecutor().handle_diplomatic_dialogue_response(
        "1", {"world": world, "debug_mode": True}
    )

    assert result["success"] is True
    assert world.is_at_war(player, "Prussia")
    assert any(
        _pair(player, "Prussia") in inst["active_diplo_keys"]
        for inst in _active_instances(world).values()
    )
    assert_war_instance_invariants(world, context="commitment_paradox_outcome")


def test_combat_triggered_auto_war_fallback_threads_war_instance():
    from backend.commands.executor import CommandExecutor

    world = WorldState(player_nation="France")
    world.diplomatic_states.clear()
    world.invalidate_war_instance_indexes()
    _set_state(world, "France", "Prussia", "PEACE")
    ney = world.get_marshal("Ney")
    blucher = world.get_marshal("Blucher")
    assert ney is not None and blucher is not None
    ney.location = "Belgium"
    blucher.location = "Belgium"
    blucher.strength = 30000

    CommandExecutor()._execute_attack(blucher, "Ney", world, {"world": world})

    assert world.is_at_war("Prussia", "France")
    assert any(
        _pair("France", "Prussia") in inst["active_diplo_keys"]
        for inst in _active_instances(world).values()
    )
    assert_war_instance_invariants(world, context="combat_auto_war")


def test_reused_pair_keeps_original_joined_turn_under_armistice_resumption():
    world = _clean_world()
    _set_state(world, "France", "Austria", "PEACE")
    declare_war(world, "France", "Austria")
    war_id = list(_active_instances(world).keys())[0]
    pair_key = _pair("France", "Austria")
    original_joined_turn = world.war_instances[war_id]["diplo_key_meta"][pair_key][
        "joined_turn"
    ]

    # Suspend to armistice, advance a few turns, then resume.
    _set_state(world, "France", "Austria", "ARMISTICE")
    mark_pair_armistice(world, pair_key)
    world.current_turn = int(world.current_turn) + 4

    result = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="armistice_expired_war"
    )
    assert result["reused"] is True
    assert result["armistice_resumed"] is True
    pair_meta = world.war_instances[war_id]["diplo_key_meta"][pair_key]
    assert pair_meta["pair_status"] == "war"
    # joined_turn is preserved across resumption — the participant episode
    # continues; A3 will model true exit/re-entry episode boundaries.
    assert pair_meta["joined_turn"] == original_joined_turn
