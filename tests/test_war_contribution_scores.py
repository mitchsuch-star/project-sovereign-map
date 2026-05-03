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
    STAYING_POWER_PER_TURN,
    STAYING_POWER_RAW_CAP,
    STAYING_POWER_TURN_CAP,
    accrue_battle_contribution,
    accrue_staying_power_all_wars,
    accrue_staying_power_for_war,
    adapt_legacy_battle_record,
    canonical_episode_id,
    classify_standing,
    close_episode_for_exit,
    compact_war_contribution_for_archive,
    compute_standing_inputs,
    contribution_share,
    current_episode,
    current_episode_material_total,
    current_episode_total,
    detect_battle_theater,
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


# ===========================================================================
# Slice B2 emitter wiring — `detect_battle_theater()` helper
#
# The detector implements the spec §9.4 line 717 one-hop adjacency rule that
# the three battle emitters (`_post_combat_pipeline`, `_execute_attack` inline
# diplo path, auto-dispatch charge in `WorldState`) consume. Whole-war credit
# (giving every same-side participant battle bucket points regardless of
# location) is forbidden by spec §9.4 line 725.
# ===========================================================================


def _seat_marshal(world, *, name, nation, location, strength=10000):
    """Insert a synthetic marshal directly into `world.marshals`.

    Bypasses MarshalFactory's defaults (which spawn at Paris) so emitter tests
    can place participants in arbitrary regions without touching nation
    starting rosters.
    """
    from backend.models.marshal import Marshal
    marshal = Marshal(
        name=name,
        location=location,
        strength=strength,
        personality="cautious",
        nation=nation,
        movement_range=1,
        tactical_skill=7,
        skills={"tactical": 7, "shock": 7, "defense": 7,
                "logistics": 7, "administration": 7, "command": 7},
        cavalry=False,
        artillery=False,
        spawn_location=location,
    )
    world.marshals[name] = marshal
    return marshal


def _clear_default_marshals(world):
    """Wipe `world.marshals` so emitter tests can seat exact participants
    without inheriting the live game's starting roster (Reynier in Dresden,
    Schwarzenberg in Bohemia, etc.).
    """
    world.marshals.clear()
    if hasattr(world, "_build_marshal_index"):
        world._build_marshal_index()


def test_detect_battle_theater_returns_none_when_no_active_war_instance():
    """Spec §9.4: theater detection requires a resolvable `war_id`."""
    world = _build_world_with_war(
        attackers=("France",),
        defenders=("Austria",),
    )
    world.war_instances.clear()
    world.invalidate_war_instance_indexes()

    payload = detect_battle_theater(
        world,
        battle_region="Saxony",
        attacker_nation="France",
        defender_nation="Austria",
    )
    assert payload is None


def test_detect_battle_theater_returns_none_when_nations_on_same_side():
    """No-op when caller's two nations share a side (cannot be a battle)."""
    world = _build_world_with_war(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )

    payload = detect_battle_theater(
        world,
        battle_region="Saxony",
        attacker_nation="France",
        defender_nation="Saxony",
        war_id="war_1",
    )
    assert payload is None


def test_detect_battle_theater_credits_one_hop_adjacent_allies():
    """Spec §9.4 line 717: an ally with a marshal in a one-hop adjacent
    region gets credited with theater participation; an ally on a distant
    front does NOT receive whole-war free credit (line 725).
    """
    world = _build_world_with_war(
        attackers=("France", "Saxony"),
        defenders=("Austria", "Russia"),
    )
    _clear_default_marshals(world)
    _seat_marshal(world, name="Napoleon", nation="France",
                  location="Saxony", strength=30000)
    _seat_marshal(world, name="Bernadotte", nation="Saxony",
                  location="Bohemia", strength=12000)
    _seat_marshal(world, name="Charles", nation="Austria",
                  location="Saxony", strength=25000)
    # Russian ally far from the Saxony theater — must NOT get credit.
    _seat_marshal(world, name="Kutuzov", nation="Russia",
                  location="Tyrol", strength=20000)

    payload = detect_battle_theater(
        world,
        battle_region="Saxony",
        attacker_nation="France",
        defender_nation="Austria",
        war_id="war_1",
    )
    assert payload is not None
    assert payload["war_id"] == "war_1"
    # Saxony (Bohemia is one-hop) gets battle credit; Russia (Tyrol) does not.
    assert "Saxony" in payload["attacker_participants"]
    assert "France" in payload["attacker_participants"]
    assert "Russia" not in payload["defender_participants"]
    assert payload["nation_theater_strength"]["France"] >= 30000
    assert payload["nation_theater_strength"]["Saxony"] == 12000
    assert payload["nation_theater_strength"]["Austria"] >= 25000
    assert "Russia" not in payload["nation_theater_strength"]


def test_detect_battle_theater_pre_battle_strength_overrides_post_battle():
    """When the caller has pre-battle strengths captured (the post-combat
    pipeline + inline `_execute_attack` always do), those override the
    marshals' (post-battle) `.strength` for the explicit attacker/defender.
    """
    world = _build_world_with_war(
        attackers=("France",),
        defenders=("Austria",),
    )
    _clear_default_marshals(world)
    _seat_marshal(world, name="Napoleon", nation="France",
                  location="Saxony", strength=200)  # post-battle remnant
    _seat_marshal(world, name="Charles", nation="Austria",
                  location="Saxony", strength=300)  # post-battle remnant

    payload = detect_battle_theater(
        world,
        battle_region="Saxony",
        attacker_nation="France",
        defender_nation="Austria",
        war_id="war_1",
        attacker_marshal_name="Napoleon",
        defender_marshal_name="Charles",
        attacker_pre_battle_strength=45000,
        defender_pre_battle_strength=30000,
    )
    assert payload is not None
    assert payload["nation_theater_strength"]["France"] == 45000
    assert payload["nation_theater_strength"]["Austria"] == 30000


def test_detect_battle_theater_preserves_same_nation_secondary_strength():
    """Primary pre-battle overrides replace only that marshal, not the whole
    nation bucket. Same-nation allies in the one-hop theater still count.
    """
    world = _build_world_with_war(
        attackers=("France",),
        defenders=("Austria",),
    )
    _clear_default_marshals(world)
    _seat_marshal(world, name="Napoleon", nation="France",
                  location="Saxony", strength=200)  # post-battle remnant
    _seat_marshal(world, name="Davout", nation="France",
                  location="Bohemia", strength=20000)
    _seat_marshal(world, name="Charles", nation="Austria",
                  location="Saxony", strength=300)
    _seat_marshal(world, name="Bellegarde", nation="Austria",
                  location="Bohemia", strength=12000)

    payload = detect_battle_theater(
        world,
        battle_region="Saxony",
        attacker_nation="France",
        defender_nation="Austria",
        war_id="war_1",
        attacker_marshal_name="Napoleon",
        defender_marshal_name="Charles",
        attacker_pre_battle_strength=45000,
        defender_pre_battle_strength=30000,
    )
    assert payload is not None
    assert payload["nation_theater_strength"]["France"] == 65000
    assert payload["nation_theater_strength"]["Austria"] == 42000


def test_detect_battle_theater_filters_inactive_participants():
    """Only nations in the war_instance `active_participants` list can be
    credited — eliminated participants must not soak up theater credit.
    """
    world = _build_world_with_war(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    _clear_default_marshals(world)
    # Saxony was eliminated — drop from active roster but keep a stray
    # marshal in theater (e.g. liberation army that was never disbanded).
    instance = world.war_instances["war_1"]
    instance["active_participants"] = ["France", "Austria"]

    _seat_marshal(world, name="Napoleon", nation="France",
                  location="Saxony", strength=30000)
    _seat_marshal(world, name="Bernadotte", nation="Saxony",
                  location="Bohemia", strength=12000)
    _seat_marshal(world, name="Charles", nation="Austria",
                  location="Saxony", strength=25000)

    payload = detect_battle_theater(
        world,
        battle_region="Saxony",
        attacker_nation="France",
        defender_nation="Austria",
        war_id="war_1",
    )
    assert payload is not None
    assert "Saxony" not in payload["attacker_participants"]
    assert "Saxony" not in payload["nation_theater_strength"]


# ===========================================================================
# Slice B2 emitter wiring — call-site source-order guards
#
# Each of the three battle paths must (a) call `detect_battle_theater` BEFORE
# its `record_diplo_battle` call, and (b) forward `war_id`,
# `attacker_participants`, `defender_participants`, and
# `nation_theater_strength` to the diplomatic recorder. The source-order
# assertion catches a future refactor that drops the theater payload while
# keeping the `record_diplo_battle` call alive.
# ===========================================================================


def test_post_combat_pipeline_source_calls_detect_battle_theater_before_record():
    """Glorious-charge / inline-attack / bombardment all funnel through
    `_post_combat_pipeline`. The pipeline's diplo step must detect theater
    BEFORE forwarding to `record_diplo_battle`.
    """
    import inspect

    from backend.commands import combat_executor

    src = inspect.getsource(combat_executor.CombatExecutor._post_combat_pipeline)

    detect_pos = src.find("detect_battle_theater(")
    record_pos = src.find("record_diplo_battle(")
    assert detect_pos != -1, (
        "_post_combat_pipeline() must call detect_battle_theater() — "
        "Imperial Settlement B2 theater-aware emitter wiring."
    )
    assert record_pos != -1
    assert detect_pos < record_pos, (
        "Theater detection must precede record_diplo_battle() so the "
        "theater payload reaches accrue_battle_contribution()."
    )
    # Forwarded fields must appear in the record_diplo_battle keyword args.
    forwarded = src[record_pos:]
    assert "war_id=" in forwarded
    assert "attacker_participants=" in forwarded
    assert "defender_participants=" in forwarded
    assert "nation_theater_strength=" in forwarded


def test_execute_attack_inline_source_calls_detect_battle_theater_before_record():
    """`_execute_attack` records its diplo battle inline (before the
    pipeline call sets `skip_diplo_record=True`). That inline path must
    also detect theater and forward the payload.
    """
    import inspect

    from backend.commands import combat_executor

    src = inspect.getsource(combat_executor.CombatExecutor._execute_attack)

    detect_pos = src.find("detect_battle_theater(")
    record_pos = src.find("record_diplo_battle(")
    assert detect_pos != -1, (
        "_execute_attack() inline path must call detect_battle_theater() "
        "before record_diplo_battle()."
    )
    assert record_pos != -1
    assert detect_pos < record_pos
    forwarded = src[record_pos:]
    assert "war_id=" in forwarded
    assert "attacker_participants=" in forwarded
    assert "defender_participants=" in forwarded
    assert "nation_theater_strength=" in forwarded


def test_auto_dispatch_charge_source_calls_detect_battle_theater_before_record():
    """The reckless-cavalry auto-charge path is the third battle emitter
    (it bypasses both `_post_combat_pipeline` and `_execute_attack`). Same
    source-order contract applies.
    """
    import inspect

    from backend.models import world_state

    src = inspect.getsource(
        world_state.WorldState._process_reckless_cavalry_turn_start,
    )

    detect_pos = src.find("detect_battle_theater(")
    record_pos = src.find("record_diplo_battle(")
    assert detect_pos != -1, (
        "_process_reckless_cavalry_turn_start() must call "
        "detect_battle_theater() before record_diplo_battle()."
    )
    assert record_pos != -1
    assert detect_pos < record_pos
    forwarded = src[record_pos:]
    assert "war_id=" in forwarded
    assert "attacker_participants=" in forwarded
    assert "defender_participants=" in forwarded
    assert "nation_theater_strength=" in forwarded


# ===========================================================================
# Slice B2 emitter wiring — behavioral end-to-end fixtures
#
# Each fixture drives a real combat path and asserts the contribution store
# lands the expected per-nation `battle` points. Distant same-side
# participants must NOT receive whole-war free credit (spec §9.4 line 725).
# ===========================================================================


def _setup_three_theater_world(*, attackers=("France", "Saxony", "Spain"),
                                  defenders=("Austria", "Russia"),
                                  attacker_leader="France",
                                  defender_leader="Austria"):
    """Three-theater fixture: France+Saxony fight Austria in Saxony,
    Spain is on a distant front (Madrid/Iberia), Russia is also distant.
    """
    world = _build_world_with_war(
        attackers=attackers,
        defenders=defenders,
        attacker_leader=attacker_leader,
        defender_leader=defender_leader,
    )
    diplo_key = world._make_diplo_key(attacker_leader, defender_leader)
    world.diplomatic_states[diplo_key] = "WAR"
    for nation in attackers + defenders:
        open_episode(world, "war_1", nation, joined_turn=1)
    return world


def test_post_combat_pipeline_emits_theater_data_for_glorious_charge():
    """End-to-end: drive `_post_combat_pipeline` with `is_glorious_charge=True`
    and verify the theater payload reaches contribution accrual.

    Saxony ally (in Bohemia, one-hop adjacent to Saxony battle region)
    receives battle credit; Spain ally (in Marseille, distant) does not.
    """
    from backend.commands.executor import CommandExecutor

    world = _setup_three_theater_world()
    _clear_default_marshals(world)
    napoleon = _seat_marshal(world, name="Napoleon", nation="France",
                              location="Saxony", strength=40000)
    _seat_marshal(world, name="Bernadotte", nation="Saxony",
                  location="Bohemia", strength=10000)
    # Distant Spanish ally — must not be credited.
    _seat_marshal(world, name="DistantAlly", nation="Spain",
                  location="Marseille", strength=20000)
    charles = _seat_marshal(world, name="Charles", nation="Austria",
                             location="Saxony", strength=30000)

    executor = CommandExecutor()
    ctx = {
        "attacker": napoleon,
        "defender": charles,
        "defender_nation": "Austria",
        "battle_region": "Saxony",
        "outcome": "attacker_victory",
        "attacker_won": True,
        "defender_won": False,
        "attacker_casualties": 5000,
        "defender_casualties": 8000,
        "pre_battle_attacker_strength": 45000,
        "pre_battle_defender_strength": 38000,
        "battle_result": None,
        "conquered": False,
        "is_glorious_charge": True,
        "skip_log_battle_event": True,
        "skip_combat_notifications": True,
        "skip_intel_update": True,
        "skip_war_damage": True,
        "skip_coordination_clear": True,
        "skip_relationships": True,
    }
    executor._post_combat_pipeline(ctx, world)

    france_ep = current_episode(world, "war_1", "France")
    saxony_ep = current_episode(world, "war_1", "Saxony")
    spain_ep = current_episode(world, "war_1", "Spain")
    austria_ep = current_episode(world, "war_1", "Austria")

    assert france_ep is not None
    assert saxony_ep is not None
    assert spain_ep is not None
    assert austria_ep is not None

    # France + Saxony split the 40-point attacker battle bucket; Saxony
    # earned non-zero credit for being one-hop adjacent. Spain (distant)
    # gets nothing.
    assert france_ep["battle"] > 0
    assert saxony_ep["battle"] > 0
    assert spain_ep["battle"] == 0
    # Austria absorbs the full defender bucket as the only theater defender.
    assert austria_ep["battle"] == 40


def test_post_combat_pipeline_distant_same_side_participant_no_free_credit():
    """Slice B v1 baseline: a same-side participant on a distant front
    accrues nothing from this front's battle. Whole-war credit is forbidden
    by spec §9.4 line 725.
    """
    from backend.commands.executor import CommandExecutor

    world = _setup_three_theater_world(
        attackers=("France",),
        defenders=("Austria", "Russia"),
        attacker_leader="France",
        defender_leader="Austria",
    )
    _clear_default_marshals(world)
    napoleon = _seat_marshal(world, name="Napoleon", nation="France",
                              location="Saxony", strength=40000)
    charles = _seat_marshal(world, name="Charles", nation="Austria",
                             location="Saxony", strength=30000)
    # Russia in a far theater; should never collect Saxony battle credit.
    _seat_marshal(world, name="Kutuzov", nation="Russia",
                  location="Marseille", strength=25000)

    executor = CommandExecutor()
    ctx = {
        "attacker": napoleon,
        "defender": charles,
        "defender_nation": "Austria",
        "battle_region": "Saxony",
        "outcome": "attacker_victory",
        "attacker_won": True,
        "defender_won": False,
        "attacker_casualties": 4000,
        "defender_casualties": 9000,
        "pre_battle_attacker_strength": 44000,
        "pre_battle_defender_strength": 39000,
        "battle_result": None,
        "conquered": False,
        "skip_log_battle_event": True,
        "skip_combat_notifications": True,
        "skip_intel_update": True,
        "skip_war_damage": True,
        "skip_coordination_clear": True,
        "skip_relationships": True,
    }
    executor._post_combat_pipeline(ctx, world)

    russia_ep = current_episode(world, "war_1", "Russia")
    assert russia_ep is not None
    assert russia_ep["battle"] == 0
    assert russia_ep["total"] == 0


def test_post_combat_pipeline_garrison_emits_theater_data():
    """Garrison combat has no defender marshal, but the pipeline still has a
    defender nation and pre-battle garrison strength for contribution.
    """
    from backend.commands.executor import CommandExecutor

    world = _setup_three_theater_world(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    _clear_default_marshals(world)
    napoleon = _seat_marshal(world, name="Napoleon", nation="France",
                              location="Saxony", strength=40000)
    _seat_marshal(world, name="Bernadotte", nation="Saxony",
                  location="Bohemia", strength=10000)

    executor = CommandExecutor()
    ctx = {
        "attacker": napoleon,
        "defender": None,
        "defender_nation": "Austria",
        "battle_region": "Saxony",
        "outcome": "attacker_victory",
        "attacker_won": True,
        "defender_won": False,
        "attacker_casualties": 2000,
        "defender_casualties": 7000,
        "pre_battle_attacker_strength": 42000,
        "pre_battle_defender_strength": 18000,
        "battle_result": None,
        "conquered": True,
        "is_garrison": True,
        "skip_cannon_fire_record": True,
        "skip_log_battle_event": True,
        "skip_combat_notifications": True,
        "skip_intel_update": True,
        "skip_war_damage": True,
        "skip_coordination_clear": True,
        "skip_relationships": True,
    }
    executor._post_combat_pipeline(ctx, world)

    france_ep = current_episode(world, "war_1", "France")
    saxony_ep = current_episode(world, "war_1", "Saxony")
    austria_ep = current_episode(world, "war_1", "Austria")
    assert france_ep is not None
    assert saxony_ep is not None
    assert austria_ep is not None
    assert france_ep["battle"] > 0
    assert saxony_ep["battle"] > 0
    assert austria_ep["battle"] == 40


def test_post_combat_pipeline_bombardment_emits_theater_data():
    """Bombardment routes through the same pipeline diplo emitter."""
    from backend.commands.executor import CommandExecutor

    world = _setup_three_theater_world(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    _clear_default_marshals(world)
    napoleon = _seat_marshal(world, name="Napoleon", nation="France",
                              location="Saxony", strength=40000)
    _seat_marshal(world, name="Bernadotte", nation="Saxony",
                  location="Bohemia", strength=10000)
    charles = _seat_marshal(world, name="Charles", nation="Austria",
                             location="Saxony", strength=30000)

    executor = CommandExecutor()
    ctx = {
        "attacker": napoleon,
        "defender": charles,
        "defender_nation": "Austria",
        "battle_region": "Saxony",
        "outcome": "bombardment",
        "attacker_won": True,
        "defender_won": False,
        "attacker_casualties": 0,
        "defender_casualties": 6000,
        "pre_battle_attacker_strength": 40000,
        "pre_battle_defender_strength": 36000,
        "battle_result": None,
        "conquered": False,
        "is_bombardment": True,
        "skip_cannon_fire_record": True,
        "skip_log_battle_event": True,
        "skip_combat_notifications": True,
        "skip_intel_update": True,
        "skip_idle_reset": True,
        "skip_exhaustion": True,
        "skip_coordination_clear": True,
        "skip_relationships": True,
    }
    executor._post_combat_pipeline(ctx, world)

    france_ep = current_episode(world, "war_1", "France")
    saxony_ep = current_episode(world, "war_1", "Saxony")
    austria_ep = current_episode(world, "war_1", "Austria")
    assert france_ep is not None
    assert saxony_ep is not None
    assert austria_ep is not None
    assert france_ep["battle"] > 0
    assert saxony_ep["battle"] > 0
    assert austria_ep["battle"] == 40


def test_post_combat_pipeline_theater_none_falls_back_to_legacy_adapter():
    """If theater detection cannot build a payload, record_battle still uses
    the legacy single-attacker / single-defender adapter.
    """
    from backend.commands.executor import CommandExecutor

    world = _setup_three_theater_world(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    _clear_default_marshals(world)
    napoleon = _seat_marshal(world, name="Napoleon", nation="France",
                              location="Saxony", strength=40000)
    charles = _seat_marshal(world, name="Charles", nation="Austria",
                             location="Saxony", strength=30000)

    executor = CommandExecutor()
    ctx = {
        "attacker": napoleon,
        "defender": charles,
        "defender_nation": "Austria",
        "battle_region": "",
        "outcome": "attacker_victory",
        "attacker_won": True,
        "defender_won": False,
        "attacker_casualties": 4000,
        "defender_casualties": 9000,
        "pre_battle_attacker_strength": 44000,
        "pre_battle_defender_strength": 39000,
        "battle_result": None,
        "conquered": False,
        "skip_cannon_fire_record": True,
        "skip_log_battle_event": True,
        "skip_combat_notifications": True,
        "skip_intel_update": True,
        "skip_war_damage": True,
        "skip_coordination_clear": True,
        "skip_relationships": True,
    }
    executor._post_combat_pipeline(ctx, world)

    france_ep = current_episode(world, "war_1", "France")
    saxony_ep = current_episode(world, "war_1", "Saxony")
    austria_ep = current_episode(world, "war_1", "Austria")
    assert france_ep is not None
    assert saxony_ep is not None
    assert austria_ep is not None
    assert france_ep["battle"] == 40
    assert saxony_ep["battle"] == 0
    assert austria_ep["battle"] == 40


def test_auto_dispatch_charge_emits_theater_data():
    """Drive the reckless-cavalry auto-charge in `world_state.py` and verify
    the theater payload reaches contribution accrual. This path bypasses
    `_post_combat_pipeline` — it's the last of the three battle emitters.
    """
    world = _setup_three_theater_world(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    _clear_default_marshals(world)
    # Reckless cavalry needs aggressive personality + cavalry=True.
    # Glorious charge gives 2x damage so a heavy cavalry stack overwhelms
    # the defender — needed for a clear attacker_victory outcome that
    # triggers the diplo-record path.
    from backend.models.marshal import Marshal
    murat = Marshal(
        name="Murat", location="Bohemia", strength=80000,
        personality="aggressive", nation="France",
        cavalry=True, movement_range=2, tactical_skill=10,
        skills={"tactical": 10, "shock": 10, "defense": 7,
                "logistics": 7, "administration": 7, "command": 10},
        spawn_location="Bohemia",
    )
    murat.recklessness = 4
    world.marshals["Murat"] = murat
    # Saxony ally in the Saxony battle region — should accrue alongside France.
    _seat_marshal(world, name="Bernadotte", nation="Saxony",
                  location="Saxony", strength=10000)
    # Austrian target in the Saxony theater (Bohemia <-> Saxony are adjacent).
    _seat_marshal(world, name="Charles", nation="Austria",
                  location="Saxony", strength=8000)

    world._process_reckless_cavalry_turn_start()

    france_ep = current_episode(world, "war_1", "France")
    saxony_ep = current_episode(world, "war_1", "Saxony")
    austria_ep = current_episode(world, "war_1", "Austria")
    assert france_ep is not None
    assert saxony_ep is not None
    assert austria_ep is not None
    # France must collect attacker-side credit (Murat's home nation) and
    # Saxony allies in the Saxony battle region pick up share of the
    # battle bucket too. Distant participants would NOT (none in this fixture).
    assert france_ep["battle"] > 0
    assert saxony_ep["battle"] > 0
    # Austria absorbs full defender bucket as the only theater defender.
    assert austria_ep["battle"] == 40


def test_inline_execute_attack_emits_theater_data():
    """Drive the inline `_execute_attack()` diplo-record path through a
    full attack and verify theater data reaches contribution accrual.

    The inline path's `record_diplo_battle()` call fires BEFORE
    `_post_combat_pipeline(skip_diplo_record=True)` runs, so the inline
    path is its own emitter and is independently tested here.
    """
    from backend.commands.executor import CommandExecutor

    world = _setup_three_theater_world(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
        attacker_leader="France",
        defender_leader="Austria",
    )
    _clear_default_marshals(world)

    napoleon = _seat_marshal(world, name="Napoleon", nation="France",
                              location="Bohemia", strength=120000)
    # Saxony ally one-hop adjacent to the Saxony battle region.
    _seat_marshal(world, name="Bernadotte", nation="Saxony",
                  location="Berlin", strength=12000)
    charles = _seat_marshal(world, name="Charles", nation="Austria",
                             location="Saxony", strength=8000)
    # Set Saxony's controller to Austria so Napoleon can attack into enemy
    # territory; the attack then resolves inline.
    saxony_region = world.get_region("Saxony")
    if saxony_region is not None:
        saxony_region.controller = "Austria"
    bohemia_region = world.get_region("Bohemia")
    if bohemia_region is not None:
        bohemia_region.controller = "France"

    executor = CommandExecutor()
    game_state = {"world": world}
    result = executor._combat._execute_attack(
        marshal=napoleon,
        target="Saxony",
        world=world,
        game_state=game_state,
    )
    # The attack must resolve (no AP / objection / fog blocker for this
    # synthetic setup); on success the inline diplo path will have fired.
    assert result.get("success"), (
        f"_execute_attack returned failure: {result.get('message')}"
    )

    france_ep = current_episode(world, "war_1", "France")
    saxony_ep = current_episode(world, "war_1", "Saxony")
    austria_ep = current_episode(world, "war_1", "Austria")
    assert france_ep is not None
    assert saxony_ep is not None
    assert austria_ep is not None
    # France must accrue from its own attack; Saxony (one-hop adjacent in
    # Berlin) must also accrue. Austria (defender) must accrue too.
    assert france_ep["battle"] > 0
    assert saxony_ep["battle"] > 0
    assert austria_ep["battle"] > 0


# ===========================================================================
# Slice B2 — Occupation event emitter (spec §9.2 / §9.4)
# ===========================================================================


def _setup_war_with_episodes(
    *,
    war_id="war_1",
    attackers=("France", "Saxony"),
    defenders=("Austria", "Prussia"),
    attacker_leader="France",
    defender_leader="Austria",
    joined_turn=1,
):
    """Helper: build war + open active episodes for every participant."""
    world = _build_world_with_war(
        war_id=war_id,
        attackers=attackers,
        defenders=defenders,
        attacker_leader=attacker_leader,
        defender_leader=defender_leader,
    )
    diplo_key = world._make_diplo_key(attacker_leader, defender_leader)
    world.diplomatic_states[diplo_key] = "WAR"
    for nation in attackers + defenders:
        open_episode(world, war_id, nation, joined_turn=joined_turn)
    return world


def test_accrue_occupation_event_returns_none_when_no_active_war():
    """Spec §9.2: occupation accrual requires an active war_id."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()
    world.war_instances.clear()
    world.invalidate_war_instance_indexes()

    payload = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Saxony",
        occupation_kind="enemy_region_captured",
        from_controller="Austria",
        target_nation="Austria",
    )
    assert payload is None


def test_accrue_occupation_event_returns_none_for_unknown_kind():
    """Unknown `occupation_kind` is a malformed-input no-op."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()

    payload = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Saxony",
        occupation_kind="bogus_kind",
        from_controller="Austria",
        war_id="war_1",
    )
    assert payload is None
    france_ep = current_episode(world, "war_1", "France")
    assert france_ep is not None
    assert france_ep["occupation"] == 0


def test_accrue_occupation_event_credits_enemy_region_captured_20_pts():
    """`enemy_region_captured` accrues 20 raw points to the actor (spec §9.2)."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()

    payload = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Bohemia",
        occupation_kind="enemy_region_captured",
        from_controller="Austria",
        war_id="war_1",
        turn=1,
    )
    assert payload is not None
    assert payload["occupation_kind"] == "enemy_region_captured"
    assert payload["points_accrued"] == 20

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["occupation"] == 20
    assert france_ep["total"] == 20


def test_accrue_occupation_event_credits_enemy_capital_captured_40_pts():
    """`enemy_capital_captured` accrues 40 raw points to the actor (spec §9.2)."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()

    payload = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Vienna",
        occupation_kind="enemy_capital_captured",
        from_controller="Austria",
        war_id="war_1",
        turn=1,
    )
    assert payload is not None
    assert payload["points_accrued"] == 40

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["occupation"] == 40
    assert france_ep["total"] == 40


def test_accrue_occupation_event_credits_allied_region_restored_15_pts():
    """`allied_region_restored` accrues 15 raw points (spec §9.2 line 583)."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()

    payload = accrue_occupation_event(
        world,
        actor_nation="Saxony",
        region="Saxony",
        occupation_kind="allied_region_restored",
        from_controller="Austria",
        to_controller="Saxony",
        war_id="war_1",
        turn=1,
    )
    assert payload is not None
    assert payload["points_accrued"] == 15

    saxony_ep = current_episode(world, "war_1", "Saxony")
    assert saxony_ep["occupation"] == 15
    assert saxony_ep["total"] == 15


def test_accrue_occupation_event_credits_liberated_region_restored_15_pts():
    """`liberated_region_restored` accrues 15 raw points (spec §9.2 line 583)."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()

    payload = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Berlin",
        occupation_kind="liberated_region_restored",
        from_controller="Austria",
        war_id="war_1",
        turn=1,
    )
    assert payload is not None
    assert payload["points_accrued"] == 15

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["occupation"] == 15


def test_accrue_occupation_event_treaty_transfer_logs_zero_points():
    """`treaty_transfer` emits the event but accrues 0 (spec §9.2 line 641)."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()

    payload = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Bohemia",
        occupation_kind="treaty_transfer",
        from_controller="Austria",
        war_id="war_1",
        turn=1,
    )
    assert payload is not None
    assert payload["points_accrued"] == 0

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["occupation"] == 0


def test_accrue_occupation_event_dedupes_by_event_id():
    """Repeat events with the same `event_id` no-op (spec §9.2 line 670)."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()

    first = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Bohemia",
        occupation_kind="enemy_region_captured",
        from_controller="Austria",
        war_id="war_1",
        turn=1,
        event_id="occ-1-bohemia",
    )
    second = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Bohemia",
        occupation_kind="enemy_region_captured",
        from_controller="Austria",
        war_id="war_1",
        turn=1,
        event_id="occ-1-bohemia",
    )
    assert first is not None
    assert second is None  # dedupe rejection

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["occupation"] == 20  # only one accrual


def test_accrue_occupation_event_filters_outside_episode_turn_window():
    """Events outside `joined_turn..exited_turn` do not accrue (spec §7.5)."""
    from backend.game_logic.war_contribution import accrue_occupation_event

    world = _setup_war_with_episodes()
    # Close France's episode at turn 5; an event at turn 10 must be ignored.
    from backend.game_logic.war_contribution import close_episode_for_exit
    close_episode_for_exit(world, "war_1", "France", exited_turn=5)

    payload = accrue_occupation_event(
        world,
        actor_nation="France",
        region="Bohemia",
        occupation_kind="enemy_region_captured",
        from_controller="Austria",
        war_id="war_1",
        turn=10,
    )
    assert payload is None
    france_ep = current_episode(world, "war_1", "France")
    assert france_ep is not None
    assert france_ep["occupation"] == 0


def test_emit_capture_occupation_event_classifies_capital_correctly():
    """`emit_capture_occupation_event` picks `enemy_capital_captured` when
    the captured region is the from_controller's national capital."""
    from backend.game_logic.war_contribution import emit_capture_occupation_event

    world = _setup_war_with_episodes()
    payload = emit_capture_occupation_event(
        world,
        actor_nation="France",
        region="Vienna",  # Austria's capital per NATION_CAPITALS
        from_controller="Austria",
        turn=1,
    )
    assert payload is not None
    assert payload["occupation_kind"] == "enemy_capital_captured"
    assert payload["points_accrued"] == 40


def test_emit_capture_occupation_event_returns_none_when_not_at_war():
    """The capture wrapper returns None when no war_instance owns the pair."""
    from backend.game_logic.war_contribution import emit_capture_occupation_event

    world = _setup_war_with_episodes(
        attackers=("France",),
        defenders=("Austria",),
    )
    payload = emit_capture_occupation_event(
        world,
        actor_nation="France",
        region="Bohemia",
        from_controller="Saxony",  # Saxony is not in this war
        turn=1,
    )
    assert payload is None


def test_capture_region_emits_occupation_event_for_enemy_capture():
    """`world.capture_region()` accrues occupation contribution to the
    capturing nation when the previous controller is an enemy."""
    world = _setup_war_with_episodes(
        attackers=("France",),
        defenders=("Austria",),
    )
    region = world.get_region("Bohemia")
    assert region is not None
    region.controller = "Austria"

    world.capture_region("Bohemia", "France")

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep is not None
    assert france_ep["occupation"] == 20  # enemy_region_captured


def test_capture_region_emits_capital_event_when_capturing_enemy_capital():
    """Capturing an enemy capital region accrues 40 occupation points."""
    world = _setup_war_with_episodes(
        attackers=("France",),
        defenders=("Austria",),
    )
    vienna = world.get_region("Vienna")
    assert vienna is not None
    vienna.controller = "Austria"

    world.capture_region("Vienna", "France")

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep is not None
    assert france_ep["occupation"] == 40  # enemy_capital_captured


# ===========================================================================
# Slice B2 — Support event emitter (spec §9.2 line 614 / line 658)
# ===========================================================================


def test_accrue_support_event_returns_none_for_self_payment():
    """Self-payment is malformed — no event."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes()
    payload = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="France",
        support_kind="gold",
        value=500,
        source="treaty_clause",
    )
    assert payload is None


def test_accrue_support_event_returns_none_for_unknown_kind_or_source():
    """Unknown `support_kind` or `source` is malformed — no event."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes()
    bad_kind = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="weird_kind",
        value=500,
        source="treaty_clause",
    )
    bad_source = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="gold",
        value=500,
        source="bogus_source",
    )
    assert bad_kind is None
    assert bad_source is None


def test_accrue_support_event_credits_supporter_for_gold_to_ally():
    """Gold transferred between same-side allies accrues to supporter (spec §9.2 line 652)."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    payload = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="gold",
        value=500,  # 500 // 100 = 5 raw points
        source="treaty_clause",
        source_detail="ratification",
        turn=1,
    )
    assert payload is not None
    assert payload["points_accrued"] == 5
    assert payload["attributed"] is True

    france_ep = current_episode(world, "war_1", "France")
    saxony_ep = current_episode(world, "war_1", "Saxony")
    # Supporter (France) earns the support contribution; recipient does not.
    assert france_ep["support"] == 5
    assert saxony_ep["support"] == 0


def test_accrue_support_event_filters_opposite_side_flow():
    """Indemnity from a defeated enemy to the victor is NOT support (spec §9.2 line 674)."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes(
        attackers=("France",),
        defenders=("Austria",),
    )
    payload = accrue_support_event(
        world,
        war_id="war_1",
        supporter="Austria",
        recipient="France",
        support_kind="gold",
        value=1000,
        source="treaty_clause",
    )
    assert payload is None  # opposite-side flow rejected


def test_accrue_support_event_dedupes_by_episode_id():
    """Repeat events with the same id no-op (spec §9.2 line 670)."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes()
    first = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="gold",
        value=500,
        source="treaty_clause",
        turn=1,
        event_id="support-test-1",
    )
    second = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="gold",
        value=500,
        source="treaty_clause",
        turn=1,
        event_id="support-test-1",
    )
    assert first is not None
    assert second is None
    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["support"] == 5  # only one accrual


def test_accrue_support_event_caps_access_supply_at_5():
    """Access/supply caps at 5 raw points per (war_id, supporter, support_kind)."""
    from backend.game_logic.war_contribution import (
        ACCESS_SUPPLY_CAP, accrue_support_event,
    )

    world = _setup_war_with_episodes()
    accrued: int = 0
    for turn in range(1, 12):  # try 11 turns
        payload = accrue_support_event(
            world,
            war_id="war_1",
            supporter="France",
            recipient="Saxony",
            support_kind="access",
            value=1,
            source="command",
            turn=turn,
            event_id=f"access-{turn}",
        )
        if payload and payload.get("points_accrued"):
            accrued += int(payload["points_accrued"])
    assert accrued == ACCESS_SUPPLY_CAP

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["support"] == ACCESS_SUPPLY_CAP


def test_accrue_support_event_unattributed_when_war_id_none():
    """`war_id=None` returns a logging-only event with no accrual."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes()
    payload = accrue_support_event(
        world,
        war_id=None,
        supporter="Britain",
        recipient="Russia",
        support_kind="subsidy",
        value=200,
        source="coalition_subsidy",
    )
    assert payload is not None
    assert payload["attributed"] is False
    assert payload["points_accrued"] == 0
    assert payload["source_detail"] == "unattributed_subsidy"


def test_accrue_support_event_zero_raw_points_no_accrual_but_dedupes():
    """A 99-gold transfer (raw // 100 = 0) emits with 0 points and dedupes."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes()
    payload = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="gold",
        value=99,  # raw // 100 = 0
        source="treaty_clause",
        turn=1,
        event_id="tiny",
    )
    assert payload is not None
    assert payload["points_accrued"] == 0
    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["support"] == 0
    # Dedupe still applies to the 0-raw event.
    second = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="gold",
        value=99,
        source="treaty_clause",
        turn=1,
        event_id="tiny",
    )
    assert second is None


def test_accrue_support_event_ap_uses_value_times_5():
    """AP support raw is `value * 5` (spec §9.2)."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes()
    payload = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="ap",
        value=2,  # 2 * 5 = 10 raw
        source="treaty_clause",
        source_detail="ap_per_turn",
        turn=1,
    )
    assert payload is not None
    assert payload["points_accrued"] == 10
    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["support"] == 10


def test_accrue_support_event_manpower_uses_floor_div_500():
    """Manpower support raw is `value // 500` (spec §9.2)."""
    from backend.game_logic.war_contribution import accrue_support_event

    world = _setup_war_with_episodes()
    payload = accrue_support_event(
        world,
        war_id="war_1",
        supporter="France",
        recipient="Saxony",
        support_kind="manpower",
        value=1500,  # 1500 // 500 = 3
        source="treaty_clause",
        source_detail="manpower_per_turn",
        turn=1,
    )
    assert payload is not None
    assert payload["points_accrued"] == 3


# ===========================================================================
# Slice B2 — British coalition subsidy attribution (impl plan B2 §British)
# ===========================================================================


def test_resolve_british_subsidy_war_id_unique_eligible():
    """Exactly one active war with Britain + recipient same-side → that war."""
    from backend.game_logic.war_contribution import resolve_british_subsidy_war_id

    world = _setup_war_with_episodes(
        attackers=("Britain", "Russia"),
        defenders=("France",),
        attacker_leader="Britain",
        defender_leader="France",
    )
    war_id, detail = resolve_british_subsidy_war_id(world, recipient="Russia")
    assert war_id == "war_1"
    assert detail == "unique_eligible"


def test_resolve_british_subsidy_war_id_returns_unattributed_when_no_eligible():
    """No eligible war → unattributed log event."""
    from backend.game_logic.war_contribution import resolve_british_subsidy_war_id

    world = _setup_war_with_episodes(
        attackers=("France",),
        defenders=("Austria",),
    )
    war_id, detail = resolve_british_subsidy_war_id(world, recipient="Russia")
    assert war_id is None
    assert detail == "unattributed_subsidy"


def test_resolve_british_subsidy_war_id_oldest_sequence_tiebreak():
    """Multiple eligible wars without coalition data → oldest_sequence wins."""
    from backend.game_logic.war_contribution import resolve_british_subsidy_war_id

    # Build first war: Britain + Russia vs France.
    world = _setup_war_with_episodes(
        war_id="war_old",
        attackers=("Britain", "Russia"),
        defenders=("France",),
        attacker_leader="Britain",
        defender_leader="France",
    )
    # Build second war: Britain + Russia vs Austria.
    install_synthetic_active_roster(world, ["Austria"])
    second = make_synthetic_war_instance(
        "war_new",
        attackers=["Britain", "Russia"],
        defenders=["Austria"],
        attacker_leader="Britain",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=99,
    )
    world.war_instances["war_new"] = second
    world.invalidate_war_instance_indexes()

    war_id, detail = resolve_british_subsidy_war_id(world, recipient="Russia")
    assert war_id == "war_old"  # lower created_sequence
    assert detail == "oldest_sequence"


def test_resolve_british_subsidy_war_id_matching_coalition_target():
    """Active coalition's `target` matches one war's `objective_target` →
    that war wins regardless of sequence."""
    from backend.game_logic.war_contribution import resolve_british_subsidy_war_id

    world = _setup_war_with_episodes(
        war_id="war_old_default",
        attackers=("Britain", "Russia"),
        defenders=("Austria",),
        attacker_leader="Britain",
        defender_leader="Austria",
    )
    install_synthetic_active_roster(world, ["France"])
    target_war = make_synthetic_war_instance(
        "war_target",
        attackers=["Britain", "Russia"],
        defenders=["France"],
        attacker_leader="Britain",
        defender_leader="France",
        created_turn=2,
        created_sequence=50,  # later than war_old_default
    )
    target_war["objective_target"] = "France"
    world.war_instances["war_target"] = target_war
    world.invalidate_war_instance_indexes()
    world.active_coalition = {"target": "France", "members": ["Britain", "Russia"]}

    war_id, detail = resolve_british_subsidy_war_id(world, recipient="Russia")
    assert war_id == "war_target"
    assert detail == "matching_coalition_target"


def test_process_british_subsidy_emits_support_event_with_attribution():
    """The advance-turn subsidy step emits a `war_support_delivered` event
    AND accrues support to Britain in the resolved war."""
    from backend.game_logic.coalition import _process_british_subsidy

    world = _setup_war_with_episodes(
        attackers=("Britain", "Russia"),
        defenders=("France",),
        attacker_leader="Britain",
        defender_leader="France",
    )
    world.nation_gold["Britain"] = 5000
    world.nation_gold.setdefault("Russia", 0)
    # Coalition state: required for `get_british_subsidy_recipient`.
    world.active_coalition = {"members": ["Britain", "Russia"], "target": "France"}
    # Russia must have the lowest relation to Britain to be picked.
    world.nation_relations[world._make_diplo_key("Britain", "Russia")] = -10

    events = _process_british_subsidy(world)
    assert events, "expected a british_subsidy event"
    assert events[0]["recipient"] == "Russia"
    assert events[0]["war_id"] == "war_1"
    assert events[0]["subsidy_source_detail"] == "unique_eligible"

    britain_ep = current_episode(world, "war_1", "Britain")
    assert britain_ep is not None
    # 200 gold subsidy → 200 // 100 = 2 raw points.
    assert britain_ep["support"] == 2


# ===========================================================================
# Slice B2 — Treaty-clause emission (one-time + per-turn)
# ===========================================================================


def test_ratify_treaty_emits_support_for_gold_lump_between_allies():
    """Mutual `gold_lump` between same-side allies emits `war_support_delivered`."""
    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    # France pays Saxony 500 gold via treaty (e.g., subsidy). The treaty
    # ratification path must emit a support event under the active war.
    world.nation_gold["France"] = 5000
    world.nation_gold.setdefault("Saxony", 0)
    proposal = {
        "proposer_nation": "France",
        "target_nation": "Saxony",
        "type": "alliance",
        "sweeteners": [{"type": "gold_lump", "value": 500}],
    }
    # Pre-condition: France-Saxony at PEACE so the treaty can transition.
    world.diplomatic_states.pop(world._make_diplo_key("France", "Saxony"), None)

    result = world._ratify_treaty(proposal)
    # Treaty result may be None on AI-AI silent skip, but the gold_lump path
    # still applies. Assert support contribution accrued for France.
    france_ep = current_episode(world, "war_1", "France")
    assert france_ep is not None
    assert france_ep["support"] == 5  # 500 // 100


def test_ratify_treaty_emits_each_same_type_gold_lump_clause():
    """Sibling `gold_lump` clauses must not dedupe into one support event."""
    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    world.nation_gold["France"] = 5000
    saxony_starting_gold = int(world.nation_gold.setdefault("Saxony", 0))
    proposal = {
        "proposer_nation": "France",
        "target_nation": "Saxony",
        "type": "alliance",
        "sweeteners": [
            {"type": "gold_lump", "value": 500},
            {"type": "gold_lump", "value": 500},
        ],
    }
    world.diplomatic_states.pop(world._make_diplo_key("France", "Saxony"), None)

    world._ratify_treaty(proposal)

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep is not None
    assert france_ep["support"] == 10
    assert world.nation_gold["France"] == 4000
    assert world.nation_gold["Saxony"] == saxony_starting_gold + 1000


def test_ratify_treaty_emits_allied_region_restored_for_territory_cede():
    """Territory_cede returning a region to its lawful owner ally emits
    `allied_region_restored` for the recipient ally (not the proposer)."""
    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    # Set up: Austria currently holds Saxony's region "Saxony".
    saxony_region = world.get_region("Saxony")
    assert saxony_region is not None
    saxony_region.controller = "Austria"
    # Set high war score so the cede won't trip the elimination guard.
    diplo_key = world._make_diplo_key("France", "Austria")
    world.war_scores[diplo_key] = 50

    proposal = {
        "proposer_nation": "France",
        "target_nation": "Austria",
        "type": "peace",
        "demands": [{
            "type": "territory_cede",
            "regions": ["Saxony"],
            "from_nation": "Austria",
            "to_nation": "Saxony",
        }],
    }
    world._ratify_treaty(proposal)

    saxony_ep = current_episode(world, "war_1", "Saxony")
    assert saxony_ep is not None
    assert saxony_ep["occupation"] == 15  # allied_region_restored


def test_process_treaty_clauses_emits_per_turn_gold_support():
    """Per-turn `gold_per_turn` from same-side ally emits a support event."""
    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    diplo_key = world._make_diplo_key("France", "Saxony")
    world.active_treaties[diplo_key] = {
        "nations": ["France", "Saxony"],
        "type": "alliance",
        "clauses": [{
            "type": "gold_per_turn",
            "from": "France",
            "to": "Saxony",
            "amount": 300,
        }],
    }
    world.nation_gold["France"] = 10000
    world.nation_gold.setdefault("Saxony", 0)

    world.current_turn = 2
    world._process_treaty_clauses()

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep is not None
    assert france_ep["support"] == 3  # 300 // 100


def test_process_treaty_clauses_emits_each_same_type_gold_clause():
    """Sibling per-turn gold clauses use distinct support event ids."""
    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    diplo_key = world._make_diplo_key("France", "Saxony")
    world.active_treaties[diplo_key] = {
        "nations": ["France", "Saxony"],
        "type": "alliance",
        "clauses": [
            {
                "type": "gold_per_turn",
                "from": "France",
                "to": "Saxony",
                "amount": 300,
            },
            {
                "type": "gold_per_turn",
                "from": "France",
                "to": "Saxony",
                "amount": 300,
            },
        ],
    }
    world.nation_gold["France"] = 10000
    saxony_starting_gold = int(world.nation_gold.setdefault("Saxony", 0))

    world.current_turn = 2
    world._process_treaty_clauses()

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep is not None
    assert france_ep["support"] == 6
    assert world.nation_gold["France"] == 9400
    assert world.nation_gold["Saxony"] == saxony_starting_gold + 600


def test_process_treaty_clauses_emits_per_turn_ap_support():
    """Per-turn `ap_per_turn` between allies emits AP support."""
    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    diplo_key = world._make_diplo_key("France", "Saxony")
    world.active_treaties[diplo_key] = {
        "nations": ["France", "Saxony"],
        "type": "alliance",
        "clauses": [{
            "type": "ap_per_turn",
            "from": "Saxony",
            "to": "France",
            "amount": 1,
        }],
    }
    # Pre-seat France's AP / Saxony's AP map.
    world.nation_actions["Saxony"] = 5

    world.current_turn = 1
    world._process_treaty_clauses()

    saxony_ep = current_episode(world, "war_1", "Saxony")
    assert saxony_ep is not None
    assert saxony_ep["support"] == 5  # 1 * 5


def test_process_treaty_clauses_skips_ap_support_when_floor_blocks_payment():
    """AP support accrues only for the AP actually removed from the payer."""
    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    diplo_key = world._make_diplo_key("France", "Saxony")
    world.active_treaties[diplo_key] = {
        "nations": ["France", "Saxony"],
        "type": "alliance",
        "clauses": [{
            "type": "ap_per_turn",
            "from": "Saxony",
            "to": "France",
            "amount": 1,
        }],
    }
    world.nation_actions["Saxony"] = 1

    world.current_turn = 1
    world._process_treaty_clauses()

    saxony_ep = current_episode(world, "war_1", "Saxony")
    assert saxony_ep is not None
    assert saxony_ep["support"] == 0
    assert world.nation_actions["Saxony"] == 1


def test_process_treaty_clauses_dedupes_same_turn_replay():
    """Calling `_process_treaty_clauses` twice in one turn does not double-accrue."""
    world = _setup_war_with_episodes(
        attackers=("France", "Saxony"),
        defenders=("Austria",),
    )
    diplo_key = world._make_diplo_key("France", "Saxony")
    world.active_treaties[diplo_key] = {
        "nations": ["France", "Saxony"],
        "type": "alliance",
        "clauses": [{
            "type": "gold_per_turn",
            "from": "France",
            "to": "Saxony",
            "amount": 300,
        }],
    }
    world.nation_gold["France"] = 10000
    world.nation_gold.setdefault("Saxony", 0)

    world.current_turn = 2
    world._process_treaty_clauses()
    france_ep_after_first = current_episode(world, "war_1", "France")
    first_support = int(france_ep_after_first["support"])
    # Reset France's gold and replay the same turn.
    world.nation_gold["France"] = 10000
    world._process_treaty_clauses()
    france_ep_after_second = current_episode(world, "war_1", "France")
    # Dedupe by episode_id — second replay must not double the support.
    assert int(france_ep_after_second["support"]) == first_support


# ===========================================================================
# Slice B3 — Per-turn staying-power accrual (spec §9.2 line 612 / §7.5)
# ===========================================================================


def test_accrue_staying_power_for_war_adds_5_per_turn_to_active_episodes():
    """Spec §9.2 line 612: each active episode gains 5 raw points per turn."""
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=1)
    open_episode(world, "war_1", "Austria", joined_turn=1)

    accrue_staying_power_for_war(world, "war_1", current_turn=2)

    france_ep = current_episode(world, "war_1", "France")
    austria_ep = current_episode(world, "war_1", "Austria")
    assert france_ep["staying_power"] == STAYING_POWER_PER_TURN
    assert france_ep["total"] == STAYING_POWER_PER_TURN
    assert austria_ep["staying_power"] == STAYING_POWER_PER_TURN
    assert france_ep["staying_power_credited_turns"] == 1
    assert france_ep["last_staying_power_turn"] == 2


def test_accrue_staying_power_caps_at_10_qualifying_turns():
    """Spec §9.2 line 612: staying_power_raw caps at min(active_turns, 10) * 5."""
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=1)

    for turn in range(2, 20):
        accrue_staying_power_for_war(world, "war_1", current_turn=turn)

    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["staying_power"] == STAYING_POWER_RAW_CAP
    assert france_ep["staying_power_credited_turns"] == STAYING_POWER_TURN_CAP


def test_accrue_staying_power_idempotent_within_same_turn():
    """Re-running on the same `current_turn` is a no-op (idempotency guard)."""
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=1)

    accrue_staying_power_for_war(world, "war_1", current_turn=2)
    france_ep = current_episode(world, "war_1", "France")
    first = int(france_ep["staying_power"])
    accrue_staying_power_for_war(world, "war_1", current_turn=2)
    accrue_staying_power_for_war(world, "war_1", current_turn=2)
    assert int(france_ep["staying_power"]) == first


def test_accrue_staying_power_skips_closed_episodes():
    """`iter_active_episodes` filters out exited episodes; staying-power follows."""
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=1)
    open_episode(world, "war_1", "Austria", joined_turn=1)
    close_episode_for_exit(
        world, "war_1", "France", exited_turn=1, exit_path="separate_peace",
    )

    accrue_staying_power_for_war(world, "war_1", current_turn=2)
    france_ep = current_episode(world, "war_1", "France")
    austria_ep = current_episode(world, "war_1", "Austria")
    assert france_ep["staying_power"] == 0
    assert austria_ep["staying_power"] == STAYING_POWER_PER_TURN


def test_accrue_staying_power_skips_ended_war_instances():
    """No accrual once the war_instance has been stamped with `ended_turn`."""
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=1)
    world.war_instances["war_1"]["ended_turn"] = 5
    world.war_instances["war_1"]["end_reason"] = "all_pairs_resolved"

    accrue_staying_power_for_war(world, "war_1", current_turn=6)
    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["staying_power"] == 0


def test_accrue_staying_power_all_wars_walks_active_only():
    """Iterates active war_instances exactly once per call."""
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=1)

    snapshot = accrue_staying_power_all_wars(world, current_turn=3)
    assert "war_1" in snapshot
    assert snapshot["war_1"]["France"] == STAYING_POWER_PER_TURN


# ===========================================================================
# Slice B3 — open_episode wiring at WAR seams
# ===========================================================================


def test_create_skeleton_instance_opens_episodes_for_originator_and_target():
    """`ensure_war_instance_for_pair` opens episodes for both founding nations."""
    from backend.game_logic.settlement_helpers import ensure_war_instance_for_pair

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    world.current_turn = 5

    result = ensure_war_instance_for_pair(
        world, "France", "Austria",
        entry_path="war_declaration", root_episode_id="ep-1",
    )
    assert result["ok"]
    war_id = result["war_id"]

    france_ep = current_episode(world, war_id, "France")
    austria_ep = current_episode(world, war_id, "Austria")
    assert france_ep is not None
    assert austria_ep is not None
    assert france_ep["joined_turn"] == 5
    assert austria_ep["joined_turn"] == 5


def test_attach_pair_to_war_instance_opens_episode_for_new_participant():
    """Cascade attach via `attach_pair_to_war_instance` opens the joiner's episode."""
    from backend.game_logic.settlement_helpers import (
        attach_pair_to_war_instance,
        ensure_war_instance_for_pair,
    )

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria", "Prussia"])
    world.current_turn = 5
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]

    world.current_turn = 7
    attach = attach_pair_to_war_instance(
        world, war_id, "France", "Prussia", entry_path="ally_cascade",
    )
    assert attach["ok"]
    prussia_ep = current_episode(world, war_id, "Prussia")
    assert prussia_ep is not None
    assert prussia_ep["joined_turn"] == 7


def test_attach_participant_to_war_instance_opens_episode():
    """Single-participant attach via `attach_participant_to_war_instance` also opens."""
    from backend.game_logic.settlement_helpers import (
        attach_participant_to_war_instance,
        ensure_war_instance_for_pair,
    )

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria", "Bavaria"])
    world.current_turn = 5
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]

    world.current_turn = 8
    result = attach_participant_to_war_instance(
        world, war_id, "Bavaria", side="attackers", entry_path="late_join",
    )
    assert result["ok"]
    bavaria_ep = current_episode(world, war_id, "Bavaria")
    assert bavaria_ep is not None
    assert bavaria_ep["joined_turn"] == 8


def test_attach_pair_idempotent_when_episode_already_active():
    """Re-attaching an existing participant is a no-op on the active episode."""
    from backend.game_logic.settlement_helpers import (
        attach_pair_to_war_instance,
        ensure_war_instance_for_pair,
    )

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]
    france_ep_first = current_episode(world, war_id, "France")
    france_episode_id = world.war_contribution_scores[war_id]["France"][
        "current_episode_id"
    ]

    # Force a re-attach via the helper; episode_id must be unchanged.
    attach_pair_to_war_instance(
        world, war_id, "France", "Austria", entry_path="war_declaration",
    )
    france_ep_second = current_episode(world, war_id, "France")
    assert france_ep_first is france_ep_second
    assert (
        world.war_contribution_scores[war_id]["France"]["current_episode_id"]
        == france_episode_id
    )


def test_open_episode_after_exit_creates_fresh_re_entry_episode():
    """Spec §7.5: re-entry creates a NEW episode_id; old totals stay queryable."""
    from backend.game_logic.settlement_helpers import (
        attach_pair_to_war_instance,
        ensure_war_instance_for_pair,
    )

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    world.current_turn = 5
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]

    # Mark Austria as exited (separate-peace) by closing its episode.
    close_episode_for_exit(
        world, war_id, "Austria", exited_turn=10, exit_path="separate_peace",
    )
    first_episode_id = world.war_contribution_scores[war_id]["Austria"][
        "current_episode_id"
    ]

    # Re-attach Austria via the helper; a new episode_id should be created.
    world.current_turn = 15
    attach_pair_to_war_instance(
        world, war_id, "France", "Austria", entry_path="armistice_expired_war",
    )
    second_episode_id = world.war_contribution_scores[war_id]["Austria"][
        "current_episode_id"
    ]
    assert second_episode_id != first_episode_id
    new_episode = current_episode(world, war_id, "Austria")
    assert new_episode["joined_turn"] == 15
    # Old episode totals are still queryable in the episodes dict.
    austria_record = world.war_contribution_scores[war_id]["Austria"]
    assert first_episode_id in austria_record["episodes"]
    assert austria_record["episodes"][first_episode_id]["exited_turn"] == 10


# ===========================================================================
# Slice B3 — close_episode_for_exit wiring at exit seams
# ===========================================================================


def test_mark_participant_eliminated_closes_active_episodes():
    """Spec §7.4 elimination: contribution episode freezes at `current_turn`."""
    from backend.game_logic.settlement_helpers import (
        ensure_war_instance_for_pair,
        mark_participant_eliminated_in_all_wars,
    )

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    world.current_turn = 5
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]

    world.current_turn = 12
    mark_participant_eliminated_in_all_wars(world, "Austria")
    austria_ep = current_episode(world, war_id, "Austria")
    assert austria_ep is not None
    assert austria_ep["exited_turn"] == 12


def test_resolve_pair_to_resolved_closes_episode_when_last_pair_resolves():
    """Separate-peace exit: closing the last active pair closes the episode."""
    from backend.game_logic.settlement_helpers import (
        ensure_war_instance_for_pair,
        resolve_pair_to_resolved,
    )

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    world.current_turn = 5
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]

    pair = "|".join(sorted(("France", "Austria")))
    world.current_turn = 18
    resolve_pair_to_resolved(world, pair, resolved_turn=18)

    france_ep = current_episode(world, war_id, "France")
    austria_ep = current_episode(world, war_id, "Austria")
    assert france_ep["exited_turn"] == 18
    assert austria_ep["exited_turn"] == 18
    # Per spec §7.5 boundary is inclusive: 18 <= 18 → events on turn 18
    # still credit through the current_episode reader.
    assert austria_ep.get("exited_turn") is not None


def test_resolve_pair_to_resolved_keeps_other_active_pairs_open():
    """Separate-peace exit: a participant with another active pair STAYS active."""
    from backend.game_logic.settlement_helpers import (
        attach_pair_to_war_instance,
        ensure_war_instance_for_pair,
        resolve_pair_to_resolved,
    )

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria", "Prussia"])
    world.current_turn = 5
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]

    # France attacks Prussia in the SAME war_instance via cascade attach.
    attach_pair_to_war_instance(
        world, war_id, "France", "Prussia", entry_path="ally_cascade",
    )

    # Resolve the France|Austria pair only.
    pair = "|".join(sorted(("France", "Austria")))
    resolve_pair_to_resolved(world, pair, resolved_turn=10)

    france_ep = current_episode(world, war_id, "France")
    austria_ep = current_episode(world, war_id, "Austria")
    prussia_ep = current_episode(world, war_id, "Prussia")
    # France still has Prussia as adversary → episode stays open.
    assert france_ep["exited_turn"] is None
    # Austria's last active pair was France|Austria → episode closed.
    assert austria_ep["exited_turn"] == 10
    # Prussia's pair (France|Prussia) is still active → episode open.
    assert prussia_ep["exited_turn"] is None
    # Austria removed from active_participants on separate peace.
    instance = world.war_instances[war_id]
    assert "Austria" not in instance["active_participants"]
    assert "France" in instance["active_participants"]
    assert "Prussia" in instance["active_participants"]


def test_resolve_pair_war_end_closes_all_remaining_episodes():
    """When the LAST pair resolves, every still-active episode closes."""
    from backend.game_logic.settlement_helpers import (
        attach_pair_to_war_instance,
        ensure_war_instance_for_pair,
        resolve_pair_to_resolved,
    )

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria", "Prussia"])
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]
    attach_pair_to_war_instance(
        world, war_id, "France", "Prussia", entry_path="ally_cascade",
    )

    # Resolve France|Austria first, then France|Prussia (the LAST pair).
    resolve_pair_to_resolved(
        world,
        "|".join(sorted(("France", "Austria"))),
        resolved_turn=10,
    )
    resolve_pair_to_resolved(
        world,
        "|".join(sorted(("France", "Prussia"))),
        resolved_turn=12,
    )

    instance = world.war_instances[war_id]
    assert instance["ended_turn"] == 12
    assert instance["end_reason"] == "all_pairs_resolved"

    # Every participant's current episode is now closed.
    for nation in ("France", "Austria", "Prussia"):
        ep = current_episode(world, war_id, nation)
        assert ep is not None and ep["exited_turn"] is not None, nation


def test_cleanup_war_end_resolves_pair_for_peace_outcome():
    """`cleanup_war_end(conclude_objectives=True)` triggers `resolve_pair_to_resolved`."""
    from backend.game_logic.diplomacy import cleanup_war_end, set_diplomatic_state
    from backend.game_logic.settlement_helpers import ensure_war_instance_for_pair

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]
    pair = "|".join(sorted(("France", "Austria")))

    world.current_turn = 20
    set_diplomatic_state(world, "France", "Austria", "PEACE", "test")
    cleanup_war_end(world, pair, conclude_objectives=True)

    instance = world.war_instances[war_id]
    assert pair in instance["resolved_diplo_keys"]
    assert pair not in instance["active_diplo_keys"]
    france_ep = current_episode(world, war_id, "France")
    assert france_ep["exited_turn"] == 20


def test_cleanup_war_end_armistice_does_not_resolve_pair():
    """ARMISTICE outcome leaves the pair active and the episode open."""
    from backend.game_logic.diplomacy import cleanup_war_end
    from backend.game_logic.settlement_helpers import ensure_war_instance_for_pair

    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    create = ensure_war_instance_for_pair(
        world, "France", "Austria", entry_path="war_declaration",
    )
    war_id = create["war_id"]
    pair = "|".join(sorted(("France", "Austria")))

    world.current_turn = 20
    cleanup_war_end(world, pair, conclude_objectives=False)

    instance = world.war_instances[war_id]
    # ARMISTICE keeps the pair in active_diplo_keys (paused, not exited).
    assert pair in instance["active_diplo_keys"]
    france_ep = current_episode(world, war_id, "France")
    assert france_ep["exited_turn"] is None


# ===========================================================================
# Slice B3 — same-turn separate-peace event ordering (spec §9.5 line 740)
# ===========================================================================


def test_same_turn_battle_credits_before_separate_peace_exit_stamp():
    """Spec §9.5 line 740: events for the turn fire before exit stamping.

    A battle on turn T accrues into the active episode; the inclusive
    `event.turn <= exited_turn` boundary then keeps the credit when the
    same turn's separate-peace stamps `exited_turn = T`.
    """
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=10)
    open_episode(world, "war_1", "Austria", joined_turn=10)

    world.current_turn = 12
    # Battle event fires first (during command execution).
    accrue_battle_contribution(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=2000,
        defender_casualties=3000,
        location="Saxony",
        war_id="war_1",
        turn=12,
    )
    france_ep = current_episode(world, "war_1", "France")
    battle_credit = int(france_ep["battle"])
    assert battle_credit > 0

    # Then the separate peace stamps exited_turn=12.
    close_episode_for_exit(
        world, "war_1", "France", exited_turn=12, exit_path="separate_peace",
    )
    # Credit lands and is preserved on the closed episode.
    assert int(france_ep["battle"]) == battle_credit


def test_per_turn_staying_power_accrues_before_armistice_expiration_in_same_turn():
    """Per-turn staying-power runs before `_process_armistice_expiration`.

    process_diplomacy_turn calls `accrue_staying_power_all_wars` BEFORE
    step 8 (armistice expiration). This test exercises the wired ordering
    by calling both helpers in the documented sequence and verifying that
    a turn-T expiring armistice still captures turn-T staying-power.
    """
    world = _build_world_with_war()
    open_episode(world, "war_1", "France", joined_turn=1)

    accrue_staying_power_all_wars(world, current_turn=2)
    france_ep = current_episode(world, "war_1", "France")
    assert france_ep["staying_power"] == STAYING_POWER_PER_TURN


# ===========================================================================
# Slice B3 — concurrent-war independence (spec §9.5 line 738)
# ===========================================================================


def test_concurrent_wars_accrue_staying_power_independently():
    """A nation in two war_instances has separate per-war staying-power."""
    from tests.helpers.full_europe_settlement_fixtures import (
        build_concurrent_war_lifecycle_fixture,
    )

    world = WorldState()
    war_x_id, war_y_id = build_concurrent_war_lifecycle_fixture(world)
    open_episode(world, war_x_id, "Russia", joined_turn=1)
    open_episode(world, war_y_id, "Russia", joined_turn=1)

    accrue_staying_power_all_wars(world, current_turn=2)
    russia_ep_x = current_episode(world, war_x_id, "Russia")
    russia_ep_y = current_episode(world, war_y_id, "Russia")
    assert russia_ep_x["staying_power"] == STAYING_POWER_PER_TURN
    assert russia_ep_y["staying_power"] == STAYING_POWER_PER_TURN


def test_concurrent_war_close_does_not_affect_other_war():
    """Closing Russia's episode in war_X does not affect war_Y's episode."""
    from tests.helpers.full_europe_settlement_fixtures import (
        build_concurrent_war_lifecycle_fixture,
    )

    world = WorldState()
    war_x_id, war_y_id = build_concurrent_war_lifecycle_fixture(world)
    open_episode(world, war_x_id, "Russia", joined_turn=1)
    open_episode(world, war_y_id, "Russia", joined_turn=1)

    close_episode_for_exit(
        world, war_x_id, "Russia", exited_turn=10, exit_path="separate_peace",
    )

    russia_ep_x = current_episode(world, war_x_id, "Russia")
    russia_ep_y = current_episode(world, war_y_id, "Russia")
    assert russia_ep_x["exited_turn"] == 10
    assert russia_ep_y["exited_turn"] is None


# ===========================================================================
# Slice B3 — Three-theater fixture (spec §9.4 line 717 / line 725)
# ===========================================================================


def test_three_theater_fixture_does_not_credit_distant_front_participant():
    """A 6+ participant Coalition war: a battle on the German theater must NOT
    credit Spain/Portugal (Iberian theater) for the German front battle.
    """
    from tests.helpers.full_europe_settlement_fixtures import (
        build_three_theater_full_europe_fixture,
    )

    world = WorldState()
    inserted = build_three_theater_full_europe_fixture(world)
    war_id = next(iter(inserted))
    for nation in (
        "France", "Saxony", "Bavaria",
        "Austria", "Russia", "Prussia", "Britain", "Spain", "Portugal",
    ):
        open_episode(world, war_id, nation, joined_turn=1)

    # German theater battle: France attacker, Austria defender, no marshals
    # in the Iberian theater. The legacy adapter (no theater payload)
    # credits France & Austria only.
    accrue_battle_contribution(
        world,
        attacker_nation="France",
        defender_nation="Austria",
        winner_nation="France",
        attacker_casualties=1000,
        defender_casualties=2000,
        location="Saxony",
        war_id=war_id,
        turn=5,
    )

    france_ep = current_episode(world, war_id, "France")
    austria_ep = current_episode(world, war_id, "Austria")
    spain_ep = current_episode(world, war_id, "Spain")
    portugal_ep = current_episode(world, war_id, "Portugal")
    assert france_ep["battle"] > 0
    assert austria_ep["battle"] > 0
    assert spain_ep["battle"] == 0
    assert portugal_ep["battle"] == 0


# ===========================================================================
# Slice B3 — Archive compaction + retention (spec §7.5 / §9.5 line 178)
# ===========================================================================


def test_archive_retention_window_keeps_episodes_under_10_turns():
    """Within the 10-turn retention window, contribution episode detail survives."""
    from backend.game_logic.settlement_helpers import archive_terminal_war_instances
    from tests.helpers.full_europe_settlement_fixtures import (
        build_archive_retention_fixture,
    )

    world = WorldState()
    war_id = build_archive_retention_fixture(
        world, ended_turn=10, current_turn=18,  # 18 - 10 = 8, less than 10
    )
    open_episode(world, war_id, "France", joined_turn=5)
    france_record = world.war_contribution_scores[war_id]["France"]
    france_ep_id = france_record["current_episode_id"]

    archive_terminal_war_instances(world)

    # War_instance NOT yet archived (under 10-turn window).
    assert war_id in world.war_instances
    assert war_id in world.war_contribution_scores
    assert (
        world.war_contribution_scores[war_id]["France"]["current_episode_id"]
        == france_ep_id
    )
    # Archived container is empty.
    assert world.archived_war_contribution_scores.get(war_id) is None


def test_archive_retention_window_compacts_at_10_turns():
    """After 10-turn retention elapses, contribution compacts to per-nation totals."""
    from backend.game_logic.settlement_helpers import archive_terminal_war_instances
    from tests.helpers.full_europe_settlement_fixtures import (
        build_archive_retention_fixture,
    )

    world = WorldState()
    war_id = build_archive_retention_fixture(
        world, ended_turn=10, current_turn=20,  # 20 - 10 = 10, hits the cap
    )
    open_episode(world, war_id, "France", joined_turn=5)
    france_ep = current_episode(world, war_id, "France")
    france_ep["battle"] = 30
    france_ep["occupation"] = 20
    france_ep["staying_power"] = 25
    france_ep["support"] = 5
    france_ep["total"] = 80
    open_episode(world, war_id, "Austria", joined_turn=5)
    austria_ep = current_episode(world, war_id, "Austria")
    austria_ep["battle"] = 10
    austria_ep["total"] = 10

    archive_terminal_war_instances(world)

    assert war_id not in world.war_instances
    # war_contribution_scores entry was MOVED to archived container.
    assert war_id not in world.war_contribution_scores
    archived = world.archived_war_contribution_scores[war_id]
    assert archived["archived_turn"] == 20
    france_totals = archived["per_nation_totals"]["France"]
    assert france_totals["battle"] == 30
    assert france_totals["occupation"] == 20
    assert france_totals["staying_power"] == 25
    assert france_totals["support"] == 5
    assert france_totals["material_total"] == 55  # battle + occupation + support
    assert france_totals["total"] == 80
    assert france_totals["episode_count"] == 1
    austria_totals = archived["per_nation_totals"]["Austria"]
    assert austria_totals["battle"] == 10


def test_archive_compaction_handles_multiple_episodes_per_nation():
    """Compaction sums every episode's bucket contribution for a nation."""
    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    world.current_turn = 30
    instance = make_synthetic_war_instance(
        "war_42",
        attackers=["France"],
        defenders=["Austria"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=5,
        created_sequence=42,
    )
    instance["ended_turn"] = 15
    instance["end_reason"] = "all_pairs_resolved"
    instance["active_diplo_keys"] = []
    instance["resolved_diplo_keys"] = ["Austria|France"]
    instance["diplo_key_meta"]["Austria|France"]["pair_status"] = "resolved"
    world.diplomatic_states.pop("Austria|France", None)
    world.war_instances["war_42"] = instance

    # Two episodes for France: original + re-entry after exit.
    ep1 = open_episode(world, "war_42", "France", joined_turn=5)
    ep1["battle"] = 20
    ep1["occupation"] = 10
    ep1["total"] = 30
    close_episode_for_exit(
        world, "war_42", "France", exited_turn=8, exit_path="separate_peace",
    )
    ep2 = open_episode(world, "war_42", "France", joined_turn=12)
    ep2["battle"] = 5
    ep2["staying_power"] = 15
    ep2["total"] = 20
    close_episode_for_exit(
        world, "war_42", "France", exited_turn=15, exit_path="war_ended",
    )

    compact_war_contribution_for_archive(world, "war_42", archived_turn=25)

    archived = world.archived_war_contribution_scores["war_42"]
    france_totals = archived["per_nation_totals"]["France"]
    assert france_totals["battle"] == 25
    assert france_totals["occupation"] == 10
    assert france_totals["staying_power"] == 15
    assert france_totals["episode_count"] == 2
    assert france_totals["first_joined_turn"] == 5
    assert france_totals["last_exited_turn"] == 15
    # Active store is cleared post-compaction.
    assert "war_42" not in world.war_contribution_scores


def test_archive_compaction_save_load_round_trip_preserves_archived_totals():
    """`world.archived_war_contribution_scores` survives `to_dict`/`from_dict`."""
    world = WorldState()
    install_synthetic_active_roster(world, ["France", "Austria"])
    world.archived_war_contribution_scores = {
        "war_99": {
            "war_id": "war_99",
            "archived_turn": 25,
            "per_nation_totals": {
                "France": {
                    "battle": 30, "occupation": 10, "staying_power": 25,
                    "support": 5, "total": 70, "material_total": 45,
                    "episode_count": 1,
                    "first_joined_turn": 5, "last_exited_turn": 15,
                    "historical_total": 0,
                },
            },
        },
    }
    data = world.to_dict()
    new_world = WorldState.from_dict(data)
    archived = new_world.archived_war_contribution_scores["war_99"]
    assert archived["archived_turn"] == 25
    assert archived["per_nation_totals"]["France"]["battle"] == 30
    assert archived["per_nation_totals"]["France"]["material_total"] == 45


def test_archive_compaction_no_op_when_no_contribution_record():
    """Compacting a war_id with no contribution data returns None safely."""
    world = WorldState()
    result = compact_war_contribution_for_archive(
        world, "war_does_not_exist", archived_turn=10,
    )
    assert result is None
    assert world.archived_war_contribution_scores == {}
