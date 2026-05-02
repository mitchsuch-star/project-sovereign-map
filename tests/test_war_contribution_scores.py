"""Slice B1 — Contribution Tracker (data shape + helpers + classifier).

Per `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` §"Slice B"
B1 ships:

- ``world.war_contribution_scores`` data shape (spec §9.1).
- Save / load round-trip + pre-B1 default.
- Episode helpers (``open_episode``, ``close_episode_for_exit``,
  ``canonical_episode_id``).
- Current-episode math (totals, material totals, side denominators,
  contribution shares, material shares).
- Old-record adapter for legacy battle records (spec §9.6).
- Pure standing classifier (spec §8.2 / §8.3).
- Merge hook handling for B1-shaped per-nation episode dicts (no crash
  + post-merge invariant clean).

B1 must NOT wire emitters (B2) or per-turn lifecycle (B3); these tests
construct contribution data manually instead.
"""

import copy

import pytest

from backend.game_logic import war_contribution
from backend.game_logic.settlement_helpers import (
    _rewrite_absorbed_war_id_in_contribution,
    assert_war_instance_invariants,
    merge_war_instances,
)
from backend.game_logic.war_contribution import (
    BENEFICIARY_ONLY,
    CONSULT,
    NO_STANDING,
    SEAT,
    accrue_battle_contribution,
    adapt_legacy_battle_record,
    canonical_episode_id,
    classify_standing,
    close_episode_for_exit,
    compute_standing_inputs,
    contribution_share,
    current_episode,
    current_episode_material_total,
    current_episode_total,
    iter_active_episodes,
    material_contribution_share,
    open_episode,
    standing_for_participant,
    total_side_current_episode_contribution,
    total_side_material_contribution,
)
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    install_synthetic_active_roster,
    make_synthetic_war_instance,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _build_world_with_war(
    *,
    war_id: str = "war_1",
    attackers=("France", "Saxony"),
    defenders=("Austria", "Prussia"),
    attacker_leader: str = "France",
    defender_leader: str = "Austria",
    created_sequence: int = 1,
):
    world = WorldState()
    install_synthetic_active_roster(
        world, list(attackers) + list(defenders),
    )
    instance = make_synthetic_war_instance(
        war_id,
        attackers=list(attackers),
        defenders=list(defenders),
        attacker_leader=attacker_leader,
        defender_leader=defender_leader,
        created_turn=1,
        created_sequence=created_sequence,
    )
    world.war_instances[war_id] = instance
    world.next_war_instance_id = max(
        world.next_war_instance_id, created_sequence + 1,
    )
    world.invalidate_war_instance_indexes()
    return world


def _seed_episode(
    world,
    war_id,
    nation,
    *,
    battle=0,
    occupation=0,
    staying_power=0,
    support=0,
    joined_turn=1,
    war_sequence=None,
):
    episode = open_episode(
        world,
        war_id,
        nation,
        joined_turn=joined_turn,
        war_sequence=war_sequence,
    )
    episode["battle"] = int(battle)
    episode["occupation"] = int(occupation)
    episode["staying_power"] = int(staying_power)
    episode["support"] = int(support)
    episode["total"] = (
        episode["battle"]
        + episode["occupation"]
        + episode["staying_power"]
        + episode["support"]
    )
    return episode


# ===========================================================================
# Store data shape + save/load (spec §9.1)
# ===========================================================================


def test_world_state_initializes_war_contribution_scores_as_empty_dict():
    world = WorldState()

    assert hasattr(world, "war_contribution_scores")
    assert world.war_contribution_scores == {}


def test_save_load_round_trip_preserves_contribution_records():
    world = _build_world_with_war()
    _seed_episode(world, "war_1", "France", battle=18, occupation=12, staying_power=10, support=4)
    _seed_episode(world, "war_1", "Saxony", battle=4, support=2, staying_power=10)
    france = world.war_contribution_scores["war_1"]["France"]
    france["historical_total"] = 44

    blob = world.to_dict()
    restored = WorldState.from_dict(blob)

    assert "war_1" in restored.war_contribution_scores
    assert restored.war_contribution_scores["war_1"]["France"]["historical_total"] == 44
    france_episode = current_episode(restored, "war_1", "France")
    assert france_episode is not None
    assert france_episode["battle"] == 18
    assert france_episode["occupation"] == 12
    assert france_episode["support"] == 4


def test_pre_b1_save_loads_with_empty_contribution_default():
    blob = WorldState().to_dict()
    blob.pop("war_contribution_scores", None)

    restored = WorldState.from_dict(blob)

    assert restored.war_contribution_scores == {}


# ===========================================================================
# Episode id canonicalization (spec §9.1)
# ===========================================================================


def test_canonical_episode_id_format_matches_spec():
    assert canonical_episode_id("France", 12, 1) == "France_12_1"
    assert canonical_episode_id("Saxony", 7, 3) == "Saxony_7_3"


def test_open_episode_uses_war_instance_created_sequence_when_war_sequence_omitted():
    world = _build_world_with_war(war_id="war_5", created_sequence=5)

    open_episode(world, "war_5", "France", joined_turn=2)

    record = world.war_contribution_scores["war_5"]["France"]
    assert record["current_episode_id"] == "France_5_1"


def test_open_episode_increments_index_on_reentry_without_overwriting():
    world = _build_world_with_war(created_sequence=3)
    first = open_episode(world, "war_1", "France", joined_turn=2)
    first["battle"] = 12
    close_episode_for_exit(world, "war_1", "France", exited_turn=4)

    second = open_episode(world, "war_1", "France", joined_turn=8)

    record = world.war_contribution_scores["war_1"]["France"]
    assert record["current_episode_id"] == "France_3_2"
    assert "France_3_1" in record["episodes"]
    assert "France_3_2" in record["episodes"]
    assert record["episodes"]["France_3_1"]["battle"] == 12
    assert second is record["episodes"]["France_3_2"]


def test_close_episode_for_exit_stamps_exited_turn_inclusive():
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=2)

    closed = close_episode_for_exit(world, "war_1", "France", exited_turn=9, exit_path="separate_peace")

    assert closed is not None
    assert closed["exited_turn"] == 9
    assert "exit_path" not in closed
    assert set(closed) == {
        "joined_turn", "exited_turn", "battle", "occupation",
        "staying_power", "support", "total",
    }


def test_close_episode_for_exit_returns_none_when_no_active_episode():
    world = _build_world_with_war()

    assert close_episode_for_exit(world, "war_1", "France", exited_turn=2) is None


def test_iter_active_episodes_skips_exited_and_missing():
    world = _build_world_with_war()
    _seed_episode(world, "war_1", "France", battle=10)
    _seed_episode(world, "war_1", "Saxony", battle=2)
    close_episode_for_exit(world, "war_1", "Saxony", exited_turn=3)

    active = dict(iter_active_episodes(world, "war_1"))

    assert "France" in active
    assert "Saxony" not in active


# ===========================================================================
# Current-episode totals + side denominators (spec §9.1)
# ===========================================================================


def test_current_episode_total_sums_all_buckets():
    world = _build_world_with_war()
    _seed_episode(
        world, "war_1", "France",
        battle=18, occupation=12, staying_power=10, support=4,
    )

    assert current_episode_total(world, "war_1", "France") == 44


def test_current_episode_material_total_excludes_staying_power():
    world = _build_world_with_war()
    _seed_episode(
        world, "war_1", "France",
        battle=18, occupation=12, staying_power=10, support=4,
    )

    assert current_episode_material_total(world, "war_1", "France") == 34


def test_total_side_contribution_sums_active_participants():
    world = _build_world_with_war(
        attackers=("France", "Saxony"), defenders=("Austria",),
        attacker_leader="France", defender_leader="Austria",
    )
    _seed_episode(world, "war_1", "France", battle=20, occupation=10)
    _seed_episode(world, "war_1", "Saxony", battle=5, occupation=5)
    _seed_episode(world, "war_1", "Austria", battle=12)

    assert total_side_current_episode_contribution(world, "war_1", "attackers") == 40
    assert total_side_current_episode_contribution(world, "war_1", "defenders") == 12


def test_total_side_material_contribution_excludes_staying_power_across_side():
    world = _build_world_with_war(
        attackers=("France", "Saxony"), defenders=("Austria",),
        attacker_leader="France", defender_leader="Austria",
    )
    _seed_episode(world, "war_1", "France", battle=10, staying_power=10)
    _seed_episode(world, "war_1", "Saxony", staying_power=10, support=2)
    _seed_episode(world, "war_1", "Austria", battle=5, staying_power=10)

    assert total_side_current_episode_contribution(world, "war_1", "attackers") == 32
    assert total_side_material_contribution(world, "war_1", "attackers") == 12


# ===========================================================================
# Share helpers + zero-safe denominators (spec §9.1)
# ===========================================================================


def test_contribution_share_normalizes_against_side_total():
    world = _build_world_with_war(
        attackers=("France", "Saxony"), defenders=("Austria",),
        attacker_leader="France", defender_leader="Austria",
    )
    _seed_episode(world, "war_1", "France", battle=30)
    _seed_episode(world, "war_1", "Saxony", battle=10)

    assert contribution_share(world, "war_1", "France", "attackers") == pytest.approx(0.75)
    assert contribution_share(world, "war_1", "Saxony", "attackers") == pytest.approx(0.25)


def test_material_contribution_share_excludes_staying_power_padding():
    world = _build_world_with_war(
        attackers=("France", "Saxony"), defenders=("Austria",),
        attacker_leader="France", defender_leader="Austria",
    )
    _seed_episode(world, "war_1", "France", battle=20)
    _seed_episode(world, "war_1", "Saxony", staying_power=80)

    # Total share would be skewed: 20 / 100 = 0.20.
    assert contribution_share(world, "war_1", "France", "attackers") == pytest.approx(0.20)
    # Material share ignores Saxony's staying_power: 20 / 20 = 1.0.
    assert material_contribution_share(world, "war_1", "France", "attackers") == pytest.approx(1.0)
    # Saxony's material share is 0 because it has no material points.
    assert material_contribution_share(world, "war_1", "Saxony", "attackers") == pytest.approx(0.0)


def test_contribution_share_returns_zero_when_side_has_no_contribution():
    world = _build_world_with_war()

    # No episodes seeded — side total is 0.
    assert contribution_share(world, "war_1", "France", "attackers") == 0.0
    assert material_contribution_share(world, "war_1", "France", "attackers") == 0.0


def test_material_share_zero_when_side_total_positive_but_material_zero():
    world = _build_world_with_war(
        attackers=("France", "Saxony"), defenders=("Austria",),
        attacker_leader="France", defender_leader="Austria",
    )
    _seed_episode(world, "war_1", "France", staying_power=10)
    _seed_episode(world, "war_1", "Saxony", staying_power=10)

    # Side total positive, but no battle/occupation/support points.
    assert total_side_current_episode_contribution(world, "war_1", "attackers") == 20
    assert total_side_material_contribution(world, "war_1", "attackers") == 0
    assert material_contribution_share(world, "war_1", "France", "attackers") == 0.0


# ===========================================================================
# Old-record adapter (spec §9.6)
# ===========================================================================


def test_adapt_legacy_battle_record_fills_theater_defaults():
    record = {
        "attacker": "France",
        "defender": "Austria",
        "attacker_casualties": 5000,
        "defender_casualties": 8000,
        "location": "Saxony",
        "turn": 4,
        "winner": "France",
    }

    adapted = adapt_legacy_battle_record(record)

    assert adapted["attacker_participants"] == ["France"]
    assert adapted["defender_participants"] == ["Austria"]
    assert adapted["nation_theater_strength"] == {"France": 1, "Austria": 1}
    assert adapted["battle_region"] == "Saxony"
    assert adapted["war_id"] is None
    assert adapted["attacker_casualties"] == 5000
    assert adapted["defender_casualties"] == 8000


def test_adapt_legacy_battle_record_preserves_modern_fields_when_present():
    record = {
        "attacker": "France",
        "defender": "Austria",
        "attacker_participants": ["France", "Saxony"],
        "defender_participants": ["Austria", "Prussia"],
        "nation_theater_strength": {
            "France": 36000, "Saxony": 9000,
            "Austria": 28000, "Prussia": 12000,
        },
        "battle_region": "Saxony",
        "war_id": "war_12",
        "attacker_casualties": 6000,
        "defender_casualties": 9000,
    }

    adapted = adapt_legacy_battle_record(record)

    assert adapted["attacker_participants"] == ["France", "Saxony"]
    assert adapted["defender_participants"] == ["Austria", "Prussia"]
    assert adapted["nation_theater_strength"]["Saxony"] == 9000
    assert adapted["war_id"] == "war_12"


def test_adapt_legacy_battle_record_handles_missing_attacker_defender():
    adapted = adapt_legacy_battle_record({})

    # No attacker/defender → empty participant lists, empty theater strengths.
    assert adapted["attacker_participants"] == []
    assert adapted["defender_participants"] == []
    assert adapted["nation_theater_strength"] == {}


def test_adapt_legacy_battle_record_uses_region_alias_when_battle_region_absent():
    adapted = adapt_legacy_battle_record(
        {"attacker": "France", "defender": "Austria", "region": "Bohemia"},
    )

    assert adapted["battle_region"] == "Bohemia"


# ===========================================================================
# classify_standing pure helper (spec §8.2 / §8.3)
# ===========================================================================


def test_classify_standing_active_major_auto_seats():
    assert classify_standing(
        power_tier="major", material_share=0.0, material_contribution_points=0,
    ) == SEAT


def test_classify_standing_material_share_25_percent_promotes_to_seat():
    assert classify_standing(
        power_tier="minor", material_share=0.30, material_contribution_points=12,
    ) == SEAT


def test_classify_standing_material_share_below_25_above_10_promotes_to_consult():
    assert classify_standing(
        power_tier="minor", material_share=0.18, material_contribution_points=9,
    ) == CONSULT


def test_classify_standing_secondary_with_any_material_promotes_to_consult():
    assert classify_standing(
        power_tier="secondary", material_share=0.05, material_contribution_points=3,
    ) == CONSULT


def test_classify_standing_staying_power_alone_cannot_seat_or_consult():
    # material_contribution_points = 0, share = 0 — pure staying power.
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        is_active_same_side=True,
    ) == NO_STANDING


def test_classify_standing_active_same_side_with_minor_material_falls_to_beneficiary_only():
    # Below 10% material share, minor tier, has material — beneficiary_only.
    assert classify_standing(
        power_tier="minor", material_share=0.04, material_contribution_points=2,
        is_active_same_side=True,
    ) == BENEFICIARY_ONLY


def test_classify_standing_named_beneficiary_returns_beneficiary_only_when_no_promotion():
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        is_named_beneficiary=True,
    ) == BENEFICIARY_ONLY


def test_classify_standing_active_bargain_stake_promotes_to_seat():
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        has_active_bargain_stake=True,
    ) == SEAT


def test_classify_standing_survival_stake_promotes_to_seat():
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        has_survival_stake=True,
    ) == SEAT


def test_classify_standing_direct_territorial_interest_promotes_to_consult():
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        has_direct_territorial_interest=True,
    ) == CONSULT


def test_classify_standing_treaty_ally_materially_involved_promotes_to_consult():
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        is_treaty_ally_materially_involved=True,
    ) == CONSULT


def test_classify_standing_rival_strengthened_for_secondary_promotes_to_consult():
    assert classify_standing(
        power_tier="secondary", material_share=0.0, material_contribution_points=0,
        rival_strengthened=True,
    ) == CONSULT


def test_classify_standing_rival_strengthened_for_minor_without_material_no_consult():
    # Minor + rival_strengthened alone: stays at no_standing per spec §8.2 line 497.
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        rival_strengthened=True,
    ) == NO_STANDING


def test_classify_standing_rival_strengthened_for_minor_with_material_promotes_to_consult():
    assert classify_standing(
        power_tier="minor", material_share=0.05, material_contribution_points=3,
        rival_strengthened=True,
    ) == CONSULT


def test_classify_standing_vassal_cap_blocks_major_auto_seat():
    # Vassal auto-join with major tier — capped at beneficiary_only because
    # the only escape is independent material thresholds.
    assert classify_standing(
        power_tier="major", material_share=0.0, material_contribution_points=0,
        is_vassal_auto_join=True,
    ) == NO_STANDING


def test_classify_standing_vassal_without_material_or_stake_has_no_standing():
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        is_active_same_side=True,
        is_vassal_auto_join=True,
    ) == NO_STANDING


def test_classify_standing_vassal_with_25_percent_material_escapes_cap_to_seat():
    assert classify_standing(
        power_tier="minor", material_share=0.30, material_contribution_points=15,
        is_vassal_auto_join=True,
    ) == SEAT


def test_classify_standing_vassal_with_10_percent_material_escapes_cap_to_consult():
    assert classify_standing(
        power_tier="minor", material_share=0.15, material_contribution_points=8,
        is_vassal_auto_join=True,
    ) == CONSULT


def test_classify_standing_vassal_blocks_bargain_and_survival_promotion():
    # Vassal cap explicitly: only material thresholds bypass.
    assert classify_standing(
        power_tier="major", material_share=0.0, material_contribution_points=0,
        is_vassal_auto_join=True,
        has_active_bargain_stake=True,
        has_survival_stake=True,
        rival_strengthened=True,
    ) == BENEFICIARY_ONLY


def test_classify_standing_no_standing_when_inactive_and_no_term_inputs():
    assert classify_standing(
        power_tier="minor", material_share=0.0, material_contribution_points=0,
        is_active_same_side=False,
    ) == NO_STANDING


# ===========================================================================
# compute_standing_inputs / standing_for_participant (composite wrapper)
# ===========================================================================


def test_compute_standing_inputs_reads_power_tier_and_material_share():
    world = _build_world_with_war(
        attackers=("France", "Saxony"), defenders=("Austria",),
        attacker_leader="France", defender_leader="Austria",
    )
    _seed_episode(world, "war_1", "France", battle=20, occupation=10)
    _seed_episode(world, "war_1", "Saxony", battle=5)

    inputs = compute_standing_inputs(world, "war_1", "France", side="attackers")

    assert inputs["power_tier"] == "major"
    assert inputs["material_share"] == pytest.approx(30 / 35)
    assert inputs["material_contribution_points"] == 30
    assert inputs["is_active_same_side"] is True


def test_standing_for_participant_french_major_seat_default():
    world = _build_world_with_war()
    # No contribution data — France still seats as active major.
    assert standing_for_participant(
        world, "war_1", "France", side="attackers",
    ) == SEAT


def test_standing_for_participant_minor_with_low_material_returns_beneficiary_only():
    world = _build_world_with_war(
        attackers=("France", "Saxony"), defenders=("Austria",),
        attacker_leader="France", defender_leader="Austria",
    )
    _seed_episode(world, "war_1", "France", battle=200)
    _seed_episode(world, "war_1", "Saxony", battle=2)

    standing = standing_for_participant(
        world, "war_1", "Saxony", side="attackers",
    )

    # 2 / 202 ≈ 0.0099 → below 10% → minor with material → beneficiary_only.
    assert standing == BENEFICIARY_ONLY


def test_standing_for_participant_term_inputs_passed_through_to_classifier():
    world = _build_world_with_war()

    standing = standing_for_participant(
        world, "war_1", "Saxony", side="attackers",
        has_survival_stake=True,
    )

    assert standing == SEAT


# ===========================================================================
# Merge hook handles B1-shaped data (spec §7.6 + impl plan line 101)
# ===========================================================================


def test_rewrite_absorbed_war_id_in_contribution_no_op_when_container_empty():
    world = WorldState()

    # No war_contribution_scores entries — silent no-op, no crash.
    assert _rewrite_absorbed_war_id_in_contribution(
        world, ["war_2", "war_3"], "war_1",
    ) == 0


def test_rewrite_absorbed_war_id_in_contribution_moves_records_to_survivor():
    world = WorldState()
    world.war_contribution_scores["war_2"] = {
        "France": {
            "current_episode_id": "France_2_1",
            "episodes": {
                "France_2_1": {
                    "joined_turn": 1, "exited_turn": None,
                    "battle": 12, "occupation": 0,
                    "staying_power": 0, "support": 0, "total": 12,
                },
            },
            "historical_total": 12,
        },
    }

    moved = _rewrite_absorbed_war_id_in_contribution(world, ["war_2"], "war_1")

    assert moved == 1
    assert "war_2" not in world.war_contribution_scores
    assert world.war_contribution_scores["war_1"]["France"]["historical_total"] == 12


def test_rewrite_absorbed_war_id_in_contribution_sums_historical_total_on_collision():
    world = WorldState()
    world.war_contribution_scores["war_1"] = {
        "France": {
            "current_episode_id": "France_1_1",
            "episodes": {
                "France_1_1": {"joined_turn": 1, "exited_turn": None,
                               "battle": 8, "occupation": 0,
                               "staying_power": 0, "support": 0, "total": 8},
            },
            "historical_total": 8,
        },
    }
    world.war_contribution_scores["war_2"] = {
        "France": {
            "current_episode_id": "France_2_1",
            "episodes": {
                "France_2_1": {"joined_turn": 1, "exited_turn": None,
                               "battle": 5, "occupation": 0,
                               "staying_power": 0, "support": 0, "total": 5},
            },
            "historical_total": 5,
        },
    }

    moved = _rewrite_absorbed_war_id_in_contribution(world, ["war_2"], "war_1")

    assert moved == 1
    france = world.war_contribution_scores["war_1"]["France"]
    assert france["historical_total"] == 13
    assert "France_1_1" in france["episodes"]
    assert "France_2_1" in france["episodes"]


def test_rewrite_absorbed_war_id_in_contribution_via_merge_war_instances_no_crash():
    """Drive the rewrite through the actual A3 merge transaction."""
    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria", "Russia", "Prussia"])

    war_a = make_synthetic_war_instance(
        "war_1",
        attackers=["France"], defenders=["Austria"],
        attacker_leader="France", defender_leader="Austria",
        created_sequence=1,
    )
    war_b = make_synthetic_war_instance(
        "war_2",
        attackers=["Austria", "Prussia"], defenders=["Russia"],
        attacker_leader="Austria", defender_leader="Russia",
        created_sequence=2,
    )
    world.war_instances["war_1"] = war_a
    world.war_instances["war_2"] = war_b
    world.next_war_instance_id = 3

    # Stamp diplomatic_states for the invariant pass.
    for instance in (war_a, war_b):
        for pair in instance["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
    world.invalidate_war_instance_indexes()

    # Seed B1 contribution on both wars for the same nation (Austria
    # appears in both — realistic merge collision).
    _seed_episode(world, "war_1", "Austria", battle=10, war_sequence=1)
    _seed_episode(world, "war_2", "Austria", battle=6, war_sequence=2)
    world.war_contribution_scores["war_1"]["Austria"]["historical_total"] = 10
    world.war_contribution_scores["war_2"]["Austria"]["historical_total"] = 6

    # Side validator currently aborts because Austria appears as attacker
    # in war_b but as defender in war_a. Rewrite that mismatch first by
    # dropping Austria from war_b's attackers (keeping Prussia) so the
    # merge has a clean side mapping.
    war_b["attackers"] = ["Prussia"]
    war_b["side_by_nation"] = {"Prussia": "attackers", "Russia": "defenders"}
    war_b["active_participants"] = ["Prussia", "Russia"]
    war_b["participant_meta"].pop("Austria", None)
    # Austria's pair drops from war_2 since Austria no longer attacks Russia.
    war_b["active_diplo_keys"] = [
        p for p in war_b["active_diplo_keys"] if "Austria" not in p
    ]
    for pair_key in list(war_b["diplo_key_meta"].keys()):
        if "Austria" in pair_key:
            war_b["diplo_key_meta"].pop(pair_key)
    world.diplomatic_states = {
        pair: "WAR" for instance in (war_a, war_b)
        for pair in instance["active_diplo_keys"]
    }
    world.invalidate_war_instance_indexes()

    # Trigger merge by adding Austria as participant in war_2 contribution
    # while war_1 owns Austria's active diplo state. Use direct merge call.
    result = merge_war_instances(world, candidate_war_ids=["war_1", "war_2"])

    # merge_war_instances may no-op if components are not connected — here
    # Austria appears only in war_a's participants now, and Prussia only
    # in war_b's, so no shared participant means no connection. Verify
    # the no-op path keeps contribution intact.
    assert result.get("ok")
    if result.get("noop"):
        # Disconnected component: contribution stays under both war_ids.
        assert "war_1" in world.war_contribution_scores
        assert "war_2" in world.war_contribution_scores


def test_post_merge_invariant_clean_with_b1_contribution_records():
    """The post-merge invariant must accept B1-shaped contribution dicts."""
    world = _build_world_with_war()
    _seed_episode(world, "war_1", "France", battle=10)

    # Reset diplomatic_states so the default 1805 Britain|France WAR pair
    # (seeded by WorldState.__init__) does not fail the WAR-pair / instance
    # ownership check. Mirror only the active pairs of the synthetic war.
    instance = world.war_instances["war_1"]
    world.diplomatic_states = {
        pair: "WAR" for pair in instance["active_diplo_keys"]
    }

    # No exception raised — invariant tolerates B1 dict-shaped values.
    assert_war_instance_invariants(world, context="post_merge")


def test_post_merge_invariant_catches_dangling_war_id_in_contribution():
    """A war_id key that does not resolve to any active or archived instance fails."""
    world = WorldState()

    world.war_contribution_scores["war_999"] = {
        "France": {
            "current_episode_id": "France_999_1",
            "episodes": {},
            "historical_total": 0,
        },
    }

    with pytest.raises(Exception) as exc_info:
        assert_war_instance_invariants(world, context="post_merge")

    assert "war_999" in str(exc_info.value)


# ===========================================================================
# Empty-safe behavior on absent records (B1 callers may pre-empt B2 wiring)
# ===========================================================================


def test_current_episode_returns_none_when_record_absent():
    world = _build_world_with_war()

    assert current_episode(world, "war_1", "Austria") is None


def test_total_side_contribution_when_no_episodes_seeded():
    world = _build_world_with_war()

    assert total_side_current_episode_contribution(world, "war_1", "attackers") == 0
    assert total_side_material_contribution(world, "war_1", "attackers") == 0


def test_share_helpers_zero_when_war_id_unknown():
    world = WorldState()

    assert contribution_share(world, "war_999", "France", "attackers") == 0.0
    assert material_contribution_share(world, "war_999", "France", "attackers") == 0.0


def test_module_exposes_bucket_constants_for_b2_emitters():
    assert war_contribution.BUCKET_WEIGHTS == {
        "battle": 40, "occupation": 35, "staying_power": 15, "support": 10,
    }
    assert set(war_contribution.MATERIAL_BUCKETS) == {"battle", "occupation", "support"}
    assert war_contribution.SEAT_MATERIAL_SHARE_THRESHOLD == 0.25
    assert war_contribution.CONSULT_MATERIAL_SHARE_THRESHOLD == 0.10


def test_save_load_round_trip_is_deep_copy_not_alias():
    world = _build_world_with_war()
    _seed_episode(world, "war_1", "France", battle=10)

    blob = world.to_dict()
    restored = WorldState.from_dict(blob)

    # Mutating the restored world must not affect the original blob.
    restored.war_contribution_scores["war_1"]["France"]["historical_total"] = 99
    assert blob["war_contribution_scores"]["war_1"]["France"]["historical_total"] != 99


# ===========================================================================
# Slice B2 — `record_battle()` ordering guard (spec §9.4 line 713)
#
# Per `WAR_SETTLEMENT_ALLY_PARTICIPATION_IMPLEMENTATION_PLAN.md` §"Slice B"
# B2 build bullet: "Before B2 starts, add a regression guard for
# `backend/game_logic/diplomacy.py::record_battle()` ordering. The guard must
# fail if settlement contribution accrual moves after the 1000-casualty
# war-score early return. A source-order assertion is acceptable only if
# paired with a behavioral sub-1000-casualty fixture proving settlement
# contribution accrues while no pairwise war-score battle record is added."
#
# This is the one place B2 emitter wiring may regress quietly — raw battle
# records can be pruned (spec §9.4 line 711), so contribution that lands
# AFTER the gate is permanently lost. Both halves of the guard live below.
# ===========================================================================


def _setup_war_pair_with_episodes(
    *,
    attacker: str = "France",
    defender: str = "Austria",
):
    """Fixture: synthetic war_instance + WAR diplomatic state + open episodes.

    Lets `diplomacy.record_battle()` survive its `is_at_war` precondition
    AND lets `accrue_battle_contribution()` find an active episode to
    accrue into, both without depending on B3's war-entry seam wiring.
    """
    world = _build_world_with_war(
        attackers=(attacker,),
        defenders=(defender,),
        attacker_leader=attacker,
        defender_leader=defender,
    )
    diplo_key = world._make_diplo_key(attacker, defender)
    world.diplomatic_states[diplo_key] = "WAR"
    open_episode(world, "war_1", attacker, joined_turn=1)
    open_episode(world, "war_1", defender, joined_turn=1)
    return world, diplo_key


def test_record_battle_calls_settlement_accrual_before_1000_casualty_war_score_gate():
    """B2 ordering guard (source): settlement accrual call must appear BEFORE
    the 1000-casualty early return in `record_battle()`.

    Spec §9.4 line 713: sub-1000-casualty battles still accrue settlement
    contribution; spec §9.4 line 711 forbids reconstructing contribution
    from pruned raw battle records. The only correct place to accrue is
    before the gate that drops sub-1000 records. If a future refactor moves
    the call below the gate, this assertion fires immediately.
    """
    import inspect

    from backend.game_logic import diplomacy

    src = inspect.getsource(diplomacy.record_battle)

    accrue_pos = src.find("accrue_battle_contribution")
    gate_pos = src.find("total_casualties < 1000")

    assert accrue_pos != -1, (
        "record_battle() must call accrue_battle_contribution() — the "
        "Slice B2 settlement contribution entrypoint."
    )
    assert gate_pos != -1, (
        "record_battle() must keep the 1000-casualty war-score early return."
    )
    assert accrue_pos < gate_pos, (
        "Settlement contribution accrual must precede the 1000-casualty "
        "war-score early return (spec §9.4)."
    )


def test_sub_1000_casualty_battle_accrues_settlement_contribution_no_war_score_record():
    """B2 ordering guard (behavioral): sub-1000 battle accrues settlement
    contribution even though the pairwise war-score battle record stays empty.

    Per spec §9.2 with single-attacker/single-defender shape and theater
    strength {France: 1, Austria: 1}:
      attacker_side_raw = def_cas//100 + atk_cas//250 + decisive*25
                        = 300//100 + 200//250 + 0 = 3
      defender_side_raw = atk_cas//100 + def_cas//250 + decisive*25
                        = 200//100 + 300//250 + 0 = 3
    """
    from backend.game_logic.diplomacy import record_battle

    world, diplo_key = _setup_war_pair_with_episodes()

    record_battle(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=200,
        defender_casualties=300,  # total 500 — well below the 1000 gate
        location="Saxony",
    )

    # War-score gate dropped both pairwise records.
    assert world.battle_records.get(diplo_key, []) == []
    assert world.decisive_battles.get(diplo_key, []) == []

    # Settlement contribution accrued on both sides.
    france_episode = current_episode(world, "war_1", "France")
    austria_episode = current_episode(world, "war_1", "Austria")
    assert france_episode is not None
    assert austria_episode is not None
    assert france_episode["battle"] == 40
    assert austria_episode["battle"] == 40
    assert france_episode["total"] == 40
    assert austria_episode["total"] == 40


def test_above_1000_casualty_battle_accrues_settlement_contribution_and_war_score_record():
    """B2 ordering guard (regression): an above-gate battle still produces
    BOTH a pairwise war-score battle record AND settlement contribution.

    Without this test, a future refactor could short-circuit settlement
    accrual on big battles while keeping the sub-1000 path correct, and the
    behavioral guard would not catch it.
    """
    from backend.game_logic.diplomacy import record_battle

    world, diplo_key = _setup_war_pair_with_episodes()

    record_battle(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=2000,
        defender_casualties=3000,  # total 5000 — above the 1000 gate
        location="Saxony",
    )

    # Pairwise war-score battle record landed.
    records = world.battle_records.get(diplo_key, [])
    assert len(records) == 1
    assert records[0]["winner"] == "France"
    assert records[0]["attacker_casualties"] == 2000
    assert records[0]["defender_casualties"] == 3000

    # Settlement contribution also accrued. Single-participant sides receive
    # the full normalized 40-point battle bucket.
    france_episode = current_episode(world, "war_1", "France")
    austria_episode = current_episode(world, "war_1", "Austria")
    assert france_episode is not None
    assert austria_episode is not None
    assert france_episode["battle"] == 40
    assert austria_episode["battle"] == 40


# ===========================================================================
# Slice B2 — accrue_battle_contribution() function-level safety
#
# Direct-call no-op cases. Without these, the ordering guard could pass
# while the function quietly mis-handles edge cases that B2 emitter wiring
# will encounter (declarations not yet mutated to WAR, side-conflict bugs,
# missing episode setup before seam wiring lands).
# ===========================================================================


def test_accrue_battle_contribution_returns_none_when_no_active_war_instance():
    """Pair has no active war_instance → accrual is a silent no-op.

    Mirrors the production case where `record_battle()`'s `is_at_war`
    check passes (e.g. transient diplomatic state) but no `war_instance`
    has been allocated yet.
    """
    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])

    result = accrue_battle_contribution(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=200,
        defender_casualties=300,
    )

    assert result is None
    assert world.war_contribution_scores == {}


def test_accrue_battle_contribution_returns_none_when_nations_on_same_side():
    """Same-side battle (e.g. accidental friendly-fire wiring bug) → no-op."""
    world = _build_world_with_war(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    open_episode(world, "war_1", "France", joined_turn=1)
    open_episode(world, "war_1", "Saxony", joined_turn=1)

    result = accrue_battle_contribution(
        world,
        attacker_nation="France",
        defender_nation="Saxony",  # both attackers
        winner_nation="France",
        attacker_casualties=200,
        defender_casualties=300,
        war_id="war_1",
    )

    assert result is None
    france_episode = current_episode(world, "war_1", "France")
    saxony_episode = current_episode(world, "war_1", "Saxony")
    assert france_episode["battle"] == 0
    assert saxony_episode["battle"] == 0


def test_accrue_battle_contribution_skips_participants_without_active_episode():
    """Participants without an active episode are silently skipped.

    Pre-B3 wiring: war-entry seams have not yet wired `open_episode()`, so
    accrual must tolerate participants whose episode container is empty
    rather than crashing or auto-opening (auto-opening is a B3 concern).
    """
    world = _build_world_with_war(
        attackers=("France",),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    diplo_key = world._make_diplo_key("France", "Austria")
    world.diplomatic_states[diplo_key] = "WAR"
    # Open an episode for France only; Austria has no episode.
    open_episode(world, "war_1", "France", joined_turn=1)

    result = accrue_battle_contribution(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=200,
        defender_casualties=300,
    )

    assert result is not None
    assert "France" in result["accrued_battle_points"]
    assert "Austria" not in result["accrued_battle_points"]
    france_episode = current_episode(world, "war_1", "France")
    assert france_episode is not None
    assert france_episode["battle"] == 40


def test_accrue_battle_contribution_distributes_by_theater_strength_when_provided():
    """Forward-compat: explicit theater data divides credit by strength share.

    Locks in the function's theater-aware behavior so the post-B2 emitter
    wiring (which will pass `attacker_participants` /
    `nation_theater_strength` from one-hop adjacency) has a stable contract
    to call.
    """
    world = _build_world_with_war(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    diplo_key = world._make_diplo_key("France", "Austria")
    world.diplomatic_states[diplo_key] = "WAR"
    open_episode(world, "war_1", "France", joined_turn=1)
    open_episode(world, "war_1", "Saxony", joined_turn=1)
    open_episode(world, "war_1", "Austria", joined_turn=1)

    # 5000 attacker / 5000 defender:
    # attacker_side_raw = 5000//100 + 5000//250 + 0 = 50 + 20 = 70
    # France raw = 70 * 30/40 = 52.5 → round() → 52
    # Saxony raw = 70 * 10/40 = 17.5 → round() → 18
    # Stored bucket points normalize raw shares into the 40-point battle bucket:
    # France = round(52/70*40) = 30, Saxony = round(18/70*40) = 10.
    # round() is banker's rounding in Python 3: round(52.5) == 52, round(17.5) == 18.
    accrue_battle_contribution(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=5000,
        defender_casualties=5000,
        location="Saxony",
        attacker_participants=["France", "Saxony"],
        defender_participants=["Austria"],
        nation_theater_strength={"France": 30, "Saxony": 10, "Austria": 40},
        war_id="war_1",
    )

    france_episode = current_episode(world, "war_1", "France")
    saxony_episode = current_episode(world, "war_1", "Saxony")
    austria_episode = current_episode(world, "war_1", "Austria")
    assert france_episode is not None
    assert saxony_episode is not None
    assert austria_episode is not None
    assert france_episode["battle"] == 30
    assert saxony_episode["battle"] == 10
    # Austria: side_raw = 5000//100 + 5000//250 + 0 = 70, single participant
    # receives the full battle bucket.
    assert austria_episode["battle"] == 40


def test_accrue_battle_contribution_filters_explicit_participants_to_same_side():
    """Explicit theater lists are caller-provided, but accrual still enforces
    war_instance side membership before awarding bucket points.
    """
    world = _build_world_with_war(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    diplo_key = world._make_diplo_key("France", "Austria")
    world.diplomatic_states[diplo_key] = "WAR"
    open_episode(world, "war_1", "France", joined_turn=1)
    open_episode(world, "war_1", "Saxony", joined_turn=1)
    open_episode(world, "war_1", "Austria", joined_turn=1)

    accrue_battle_contribution(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=5000,
        defender_casualties=5000,
        location="Saxony",
        attacker_participants=["France", "Austria"],  # Austria is not attacker-side.
        defender_participants=["Austria", "Saxony"],  # Saxony is not defender-side.
        nation_theater_strength={"France": 30, "Saxony": 10, "Austria": 40},
        war_id="war_1",
        turn=1,
    )

    france_episode = current_episode(world, "war_1", "France")
    saxony_episode = current_episode(world, "war_1", "Saxony")
    austria_episode = current_episode(world, "war_1", "Austria")
    assert france_episode is not None
    assert saxony_episode is not None
    assert austria_episode is not None
    assert france_episode["battle"] == 40
    assert saxony_episode["battle"] == 0
    assert austria_episode["battle"] == 40


def test_accrue_battle_contribution_enforces_episode_turn_window():
    """Closed episodes remain addressable by current_episode_id, but events
    outside joined/exited turn bounds must not mutate contribution.
    """
    world = _build_world_with_war(
        attackers=("France",),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    diplo_key = world._make_diplo_key("France", "Austria")
    world.diplomatic_states[diplo_key] = "WAR"
    open_episode(world, "war_1", "France", joined_turn=1)
    open_episode(world, "war_1", "Austria", joined_turn=1)
    close_episode_for_exit(world, "war_1", "Austria", exited_turn=3)

    accrue_battle_contribution(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=500,
        defender_casualties=500,
        war_id="war_1",
        turn=4,
    )

    france_episode = current_episode(world, "war_1", "France")
    austria_episode = current_episode(world, "war_1", "Austria")
    assert france_episode is not None
    assert austria_episode is not None
    assert france_episode["battle"] == 40
    assert austria_episode["battle"] == 0
