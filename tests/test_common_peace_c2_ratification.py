"""Slice C2 settlement_confirm.confirm ratification mutation tests.

The C2 foundation slice (commit ``cda009b``) staged Open Settlement /
preview / ``settlement_confirm`` dialogue handling without mutation; the
``confirm`` path returned ``ratification_deferred``. This slice closes
that path by wiring the live ratification through
``ratify_settlement_confirm`` per spec §10.5 / §11 / §11.1.

Coverage:

* Covered active hostile pairs resolve to ``PEACE`` and move from
  ``active_diplo_keys`` to ``resolved_diplo_keys`` (with
  ``pair_status="resolved"`` / ``resolved_turn`` stamped) through the
  same ``cleanup_war_end -> resolve_pair_to_resolved`` path bilateral
  peace uses.
* Forced-alliance pairs end in ``ALLIANCE`` with ``alliance_origins``
  stamped ``"forced"``, the covered enemy joining the Continental
  System, and France-imposed forced alliances generating ``+15``
  coalition threat.
* Territory cessions / gold lumps / liberation outcomes apply once at
  package level (territory transfers, gold transfers, vassal release +
  liberator alignment).
* Uncovered hostile / armistice pairs in the SAME war_instance stay
  active after a partial common peace; the war_instance only ends when
  no hostile pairs remain.
* Per-pair contribution episodes close via ``resolve_pair_to_resolved``
  and ``war_scores`` / ``war_start_turns`` clear for each resolved pair.
* Caches (``war_instances_by_*``, bloc, active-nation) invalidate
  before reaction routing in the next slice can read them.
* Failed live revalidation and unresolvable plans return
  ``mutated=False`` and pop the dialogue without touching state.
"""

from __future__ import annotations

import copy
from unittest.mock import patch

from backend.game_logic.settlement_preview import (
    ratify_settlement_confirm,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_helpers import _open_contribution_episode_for_participant
from backend.models.region import Region, REGIONS_DATA
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import make_synthetic_war_instance


def _acceptance_always_passes(*args, **kwargs):
    """Monkeypatch helper: acceptance always passes for mutation tests."""
    from backend.game_logic.settlement_scoring import calculate_common_peace_acceptance as real
    result = real(*args, **kwargs)
    result["score"] = 100
    result["verdict"] = "accept"
    result["hard_stops"] = []
    return result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _install_two_v_two_war(world: WorldState) -> dict:
    """Install a 2v2 (France+Saxony vs Austria+Prussia) common-peace war.

    Each cross-side pair starts at ``WAR``. War scores favor the proposer
    side (positive France / negative Austria-side from the alphabetical
    pair-key perspective) so direct-score gates pass for both covered
    enemies.
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
        nations = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_start_turns[pair] = world.current_turn
        # High war_score to ensure SC-3 acceptance gate passes for
        # ratification mutation tests.
        first = nations[0]
        score = 100 if first not in ("France", "Saxony") else -100
        world.war_scores[pair] = -score  # invert for proposer-winning intent
        world.battle_records[pair] = []
    # G2-Slice-1: boost war exhaustion + add a conquest objective so the
    # acceptance formula passes the SC-3 fresh rescore gate (threshold=50)
    # even with forced_alliance harshness + hegemony penalty.
    world.war_exhaustion["Austria"] = 500
    world.war_exhaustion["Prussia"] = 500
    world.war_objectives = getattr(world, "war_objectives", {})
    world.war_objectives["war_1"] = [{
        "type": "conquest",
        "declaring_nation": "France",
        "target_nation": "Austria",
        "side": "attackers",
    }]
    world.invalidate_war_instance_indexes()
    return war


def _stage_dialogue(
    world: WorldState,
    *,
    war_id: str = "war_1",
    settlement_terms=None,
    covered_enemy_participants=None,
) -> dict:
    # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 empty-Ratify gate:
    # editor-staged empty drafts (`caller_kind="player_editor"`,
    # `settlement_terms == []`, `white_peace=False`) cannot ratify. The
    # ratification mechanics tests below validate pair lifecycle and
    # mutation, not the editor gate — they author a minimum legitimate
    # `[{"type": "peace"}]` package when the caller does not supply
    # explicit material clauses, mirroring the spec's "peace-only is a
    # valid below-threshold draft" treatment.
    if not settlement_terms:
        settlement_terms = [{"type": "peace"}]
    result = stage_settlement_confirm(
        world,
        war_id=war_id,
        settlement_terms=settlement_terms,
        covered_enemy_participants=covered_enemy_participants,
    )
    assert result["success"] is True
    return world.pending_diplomatic_dialogue


# ---------------------------------------------------------------------------
# Pair lifecycle
# ---------------------------------------------------------------------------


def test_confirm_resolves_full_settlement_and_ends_war_instance():
    world = WorldState()
    _install_two_v_two_war(world)

    dialogue = _stage_dialogue(world, settlement_terms=[])
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    assert result["mutated"] is True
    assert result["war_ended"] is True
    war = world.war_instances["war_1"]
    assert war["active_diplo_keys"] == []
    # All four cross-side pairs resolved.
    assert sorted(war["resolved_diplo_keys"]) == sorted([
        "Austria|France", "Austria|Saxony",
        "France|Prussia", "Prussia|Saxony",
    ])
    for pair in war["resolved_diplo_keys"]:
        assert war["diplo_key_meta"][pair]["pair_status"] == "resolved"
        assert war["diplo_key_meta"][pair]["resolved_turn"] == world.current_turn
        assert world.diplomatic_states[pair] == "PEACE"
    assert war["ended_turn"] == world.current_turn
    assert war["end_reason"] == "all_pairs_resolved"


def test_confirm_partial_settlement_keeps_uncovered_pairs_active():
    world = WorldState()
    _install_two_v_two_war(world)

    # Cover only Austria; Prussia stays at war.
    dialogue = _stage_dialogue(
        world,
        settlement_terms=[],
        covered_enemy_participants=["Austria"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    war = world.war_instances["war_1"]
    # Pairs covering Austria resolved.
    for pair in ("Austria|France", "Austria|Saxony"):
        assert pair in war["resolved_diplo_keys"]
        assert pair not in war["active_diplo_keys"]
        assert world.diplomatic_states[pair] == "PEACE"
    # Pairs covering Prussia still active and at WAR.
    for pair in ("France|Prussia", "Prussia|Saxony"):
        assert pair in war["active_diplo_keys"]
        assert pair not in war["resolved_diplo_keys"]
        assert world.diplomatic_states[pair] == "WAR"
    assert war["ended_turn"] is None


def test_confirm_armistice_pair_resolves_to_peace_and_clears_armistice():
    world = WorldState()
    war = _install_two_v_two_war(world)
    armistice_pair = "Austria|France"
    world.diplomatic_states[armistice_pair] = "ARMISTICE"
    war["diplo_key_meta"][armistice_pair]["pair_status"] = "armistice"
    world.armistice_turns[armistice_pair] = world.current_turn
    world.armistice_cooldowns[armistice_pair] = 5

    dialogue = _stage_dialogue(world, covered_enemy_participants=["Austria"])
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    assert world.diplomatic_states[armistice_pair] == "PEACE"
    assert armistice_pair not in world.armistice_turns
    assert armistice_pair not in world.armistice_cooldowns
    assert armistice_pair in war["resolved_diplo_keys"]


# ---------------------------------------------------------------------------
# Term outcomes
# ---------------------------------------------------------------------------


def test_confirm_territory_cession_transfers_regions_and_invalidates_cache():
    world = WorldState()
    _install_two_v_two_war(world)
    target_region = next(
        name for name, _data in REGIONS_DATA.items()
        if world.regions[name].controller == "Austria"
    )

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[{
            "type": "territory_cede",
            "from": "Austria",
            "to": "France",
            "regions": [target_region],
        }],
        covered_enemy_participants=["Austria"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    assert world.regions[target_region].controller == "France"
    cession_clauses = [
        c for c in result["applied_clauses"] if c["type"] == "territory_cede"
    ]
    assert cession_clauses == [
        {"type": "territory_cede", "from": "Austria", "to": "France",
         "regions": [target_region]},
    ]


@patch("backend.game_logic.settlement_preview.calculate_common_peace_acceptance", _acceptance_always_passes)
def test_confirm_canonical_territory_cede_region_transfers_region():
    """The canonical SC-1 schema uses singular `region`; it must not
    validate/stage and then become a ratification no-op."""
    world = WorldState()
    _install_two_v_two_war(world)
    target_region = next(
        name for name, _data in REGIONS_DATA.items()
        if world.regions[name].controller == "Austria"
    )

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[{
            "type": "territory_cede",
            "from": "Austria",
            "to": "France",
            "region": target_region,
        }],
        covered_enemy_participants=["Austria"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    assert result["mutated"] is True
    assert world.regions[target_region].controller == "France"
    cession_clauses = [
        c for c in result["applied_clauses"] if c["type"] == "territory_cede"
    ]
    assert cession_clauses == [
        {"type": "territory_cede", "from": "Austria", "to": "France",
         "region": target_region},
    ]


def test_confirm_gold_lump_transfers_gold_clamped_to_payer_balance():
    world = WorldState()
    _install_two_v_two_war(world)
    world.nation_gold["Austria"] = 80
    world.nation_gold["France"] = 100

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[{
            "type": "gold_lump", "from": "Austria", "to": "France",
            "amount": 200,
        }],
        covered_enemy_participants=["Austria"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    assert world.nation_gold["Austria"] == 0
    assert world.nation_gold["France"] == 180  # clamped to available
    gold_clauses = [c for c in result["applied_clauses"] if c["type"] == "gold_lump"]
    assert gold_clauses[0]["amount"] == 80


@patch("backend.game_logic.settlement_preview.calculate_common_peace_acceptance", _acceptance_always_passes)
def test_confirm_forced_alliance_pair_ends_in_alliance_with_origin_and_threat():
    world = WorldState()
    _install_two_v_two_war(world)
    threat_before = int(world.threat_level)

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[{
            "type": "forced_alliance",
            "from": "Austria",
            "to": "France",
            "includes_continental_system": True,
        }],
        covered_enemy_participants=["Austria"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    fa_pair = "Austria|France"
    assert world.diplomatic_states[fa_pair] == "ALLIANCE"
    assert world.alliance_origins.get(fa_pair) == "forced"
    assert world.nation_relations.get(fa_pair, 0) == 0
    cs_members = world.continental_system_members
    if isinstance(cs_members, set):
        assert "Austria" in cs_members
    else:
        assert "Austria" in cs_members
    # G2-Slice-1b-Repair-1: forced_alliance with `includes_continental_system=True`
    # charges +15 base + +10 Continental System surcharge = +25.
    assert int(world.threat_level) == threat_before + 25
    # Pair still moved from active to resolved per spec §10.5 line 1040.
    war = world.war_instances["war_1"]
    assert fa_pair in war["resolved_diplo_keys"]
    assert fa_pair not in war["active_diplo_keys"]
    assert war["diplo_key_meta"][fa_pair]["pair_status"] == "resolved"
    # Other-side pair (Austria|Saxony) still goes to PEACE because the
    # forced alliance is per pair, not per covered enemy globally.
    assert world.diplomatic_states["Austria|Saxony"] == "PEACE"
    fa_event = next(
        e for e in world.event_log if e.get("type") == "forced_alliance_imposed"
    )
    assert fa_event["imposer"] == "France"
    assert fa_event["forced_nation"] == "Austria"


@patch("backend.game_logic.settlement_preview.calculate_common_peace_acceptance", _acceptance_always_passes)
def test_confirm_forced_alliance_with_territory_keeps_final_alliance_and_records_treaty():
    world = WorldState()
    _install_two_v_two_war(world)
    target_region = next(
        name for name, _data in REGIONS_DATA.items()
        if world.regions[name].controller == "Austria"
    )

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[
            {
                "type": "territory_cede",
                "from": "Austria",
                "to": "France",
                "regions": [target_region],
            },
            {
                "type": "forced_alliance",
                "from": "Austria",
                "to": "France",
            },
        ],
        covered_enemy_participants=["Austria"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    pair = "Austria|France"
    assert result["success"] is True
    assert world.regions[target_region].controller == "France"
    assert world.diplomatic_states[pair] == "ALLIANCE"
    assert world.war_instances["war_1"]["diplo_key_meta"][pair]["pair_status"] == "resolved"
    treaty = world.active_treaties[pair]
    assert treaty["type"] == "alliance"
    assert treaty["state_transition"] == "WAR_TO_ALLIANCE"
    assert [c["type"] for c in treaty["clauses"]] == ["territory_cede", "forced_alliance"]


def test_confirm_subjugation_creates_vassal_and_resolves_pair():
    world = WorldState()
    _install_two_v_two_war(world)
    threat_before = int(world.threat_level)

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[{
            "type": "subjugation",
            "from": "Prussia",
            "to": "France",
        }],
        covered_enemy_participants=["Prussia"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    pair = "France|Prussia"
    assert result["success"] is True
    assert world.diplomatic_states[pair] == "VASSAL"
    assert world.vassals["Prussia"]["lord"] == "France"
    assert world.vassals["Prussia"]["path"] == "conquest"
    assert pair in world.war_instances["war_1"]["resolved_diplo_keys"]
    assert int(world.threat_level) == threat_before + 25
    treaty = world.active_treaties[pair]
    assert treaty["type"] == "vassalage"
    assert treaty["clauses"][0]["type"] == "subjugation"


def test_confirm_subjugation_from_armistice_clears_tracking_and_ends_vassal():
    world = WorldState()
    war = _install_two_v_two_war(world)
    pair = "France|Prussia"
    world.diplomatic_states[pair] = "ARMISTICE"
    war["diplo_key_meta"][pair]["pair_status"] = "armistice"
    world.armistice_turns[pair] = world.current_turn
    world.armistice_cooldowns[pair] = 5

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[{
            "type": "subjugation",
            "from": "Prussia",
            "to": "France",
        }],
        covered_enemy_participants=["Prussia"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    assert world.diplomatic_states[pair] == "VASSAL"
    assert pair not in world.armistice_turns
    assert pair not in world.armistice_cooldowns
    assert pair in war["resolved_diplo_keys"]
    assert war["diplo_key_meta"][pair]["pair_status"] == "resolved"


def test_confirm_war_score_and_start_turn_clear_for_resolved_pairs():
    world = WorldState()
    war = _install_two_v_two_war(world)
    seed_pair = "Austria|France"
    assert seed_pair in world.war_scores
    assert seed_pair in world.war_start_turns

    dialogue = _stage_dialogue(world, covered_enemy_participants=["Austria"])
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    # Resolved pair scores cleared, uncovered Prussia pair preserved.
    assert seed_pair not in world.war_scores
    assert seed_pair not in world.war_start_turns
    assert "France|Prussia" in world.war_scores


def test_confirm_pre_cleanup_snapshots_capture_per_pair_data():
    world = WorldState()
    _install_two_v_two_war(world)
    world.battle_records["Austria|France"] = [{
        "attacker": "France", "defender": "Austria",
        "attacker_casualties": 1000, "defender_casualties": 2500,
    }]
    world.current_turn = 5
    world.war_start_turns["Austria|France"] = 1

    dialogue = _stage_dialogue(world, covered_enemy_participants=["Austria"])
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    snap = result["pre_cleanup_snapshots"]["Austria|France"]
    assert snap["war_duration"] == 4
    assert snap["french_casualties"] == 1000
    assert snap["enemy_casualties"] == 2500


def test_confirm_pre_cleanup_snapshots_use_non_france_proposer_pair_perspective():
    world = WorldState()
    _install_two_v_two_war(world)
    world.battle_records["Austria|Saxony"] = [{
        "attacker": "Saxony", "defender": "Austria",
        "attacker_casualties": 300, "defender_casualties": 900,
    }]
    world.current_turn = 6
    world.war_start_turns["Austria|Saxony"] = 2

    dialogue = _stage_dialogue(world, covered_enemy_participants=["Austria"])
    result = ratify_settlement_confirm(world, dialogue)

    snap = result["pre_cleanup_snapshots"]["Austria|Saxony"]
    assert snap["proposer_member"] == "Saxony"
    assert snap["covered_enemy"] == "Austria"
    assert snap["war_duration"] == 4
    assert snap["proposer_casualties"] == 300
    assert snap["covered_enemy_casualties"] == 900
    assert snap["french_casualties"] == 0


# ---------------------------------------------------------------------------
# Reaction prep + invalidation
# ---------------------------------------------------------------------------


def test_confirm_invalidates_war_instance_and_bloc_caches():
    world = WorldState()
    _install_two_v_two_war(world)
    # Prime the participant index so the post-ratification reader has to
    # rebuild rather than return a stale snapshot.
    primed_index = world.get_war_instances_by_participant()
    assert "war_1" in primed_index.get("Austria", set())

    dialogue = _stage_dialogue(world, covered_enemy_participants=["Austria"])
    ratify_settlement_confirm(world, dialogue)

    # After ratification the participant index must reflect the
    # post-ratification active set: Austria is no longer indexed against
    # ``war_1`` (its only active pair, Austria|Saxony, also resolved as
    # part of covering Austria). France remains indexed via the still-
    # active France|Prussia pair.
    fresh_index = world.get_war_instances_by_participant()
    assert "war_1" not in fresh_index.get("Austria", set())
    assert "war_1" in fresh_index.get("France", set())
    assert "war_1" in fresh_index.get("Prussia", set())


def test_confirm_pops_dialogue_on_success_and_clears_pending():
    world = WorldState()
    _install_two_v_two_war(world)

    dialogue = _stage_dialogue(world)
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    assert world.pending_diplomatic_dialogue is None


# ---------------------------------------------------------------------------
# Validation guards
# ---------------------------------------------------------------------------


def test_confirm_failed_revalidation_does_not_mutate():
    world = WorldState()
    war = _install_two_v_two_war(world)
    dialogue = _stage_dialogue(world)
    before_states = copy.deepcopy(world.diplomatic_states)
    before_war = copy.deepcopy(war)

    # Force the leader to change so revalidation rejects.
    war["attacker_leader"] = "Saxony"

    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is False
    assert result["error"] == "proposer_leader_changed"
    assert result["mutated"] is False
    assert result["must_reopen"] is True
    assert dict(world.diplomatic_states) == dict(before_states)
    # Active pairs untouched.
    assert war["active_diplo_keys"] == before_war["active_diplo_keys"]


def test_confirm_inactive_war_instance_blocks_without_mutation():
    world = WorldState()
    war = _install_two_v_two_war(world)
    dialogue = _stage_dialogue(world)
    before_states = copy.deepcopy(world.diplomatic_states)
    war["ended_turn"] = world.current_turn

    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is False
    assert result["error"] == "inactive_war_instance"
    assert result["mutated"] is False
    assert dict(world.diplomatic_states) == dict(before_states)


def test_confirm_pair_status_changed_blocks_without_mutation():
    world = WorldState()
    war = _install_two_v_two_war(world)
    dialogue = _stage_dialogue(world)
    before_states = copy.deepcopy(world.diplomatic_states)

    # Strip an active pair (separate-peace race) so the staged plan rejects.
    pair = war["active_diplo_keys"][0]
    war["active_diplo_keys"].remove(pair)
    war["resolved_diplo_keys"].append(pair)
    war["diplo_key_meta"][pair]["pair_status"] = "resolved"

    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is False
    assert result["error"] == "active_pair_changed"
    assert result["mutated"] is False
    assert dict(world.diplomatic_states) == dict(before_states)


# ---------------------------------------------------------------------------
# Liberation outcome
# ---------------------------------------------------------------------------


def test_confirm_liberation_releases_vassal_and_aligns_with_liberator():
    world = WorldState()
    _install_two_v_two_war(world)
    # Establish Bavaria as Austrian vassal so liberation has a target.
    if "Bavaria" not in world.regions:
        world.regions["Bavaria"] = Region(
            name="Bavaria", region_type="major", income_value=80,
        )
    world.regions["Bavaria"].controller = "Bavaria"
    world.vassals["Bavaria"] = {
        "lord": "Austria", "subject": "Bavaria", "loyalty": 50, "tribute_pct": 30,
    }

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[{
            "type": "liberation",
            "vassal_nation": "Bavaria",
            "lord_nation": "Austria",
            "liberator": "France",
        }],
        covered_enemy_participants=["Austria"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    assert "Bavaria" not in world.vassals
    fa_lib_pair = world._make_diplo_key("France", "Bavaria")
    assert world.diplomatic_states.get(fa_lib_pair) == "DEFENSIVE_ALLIANCE"
    lib_event = next(
        e for e in world.event_log if e.get("type") == "vassal_liberated"
    )
    assert lib_event["vassal_nation"] == "Bavaria"
    assert lib_event["liberator"] == "France"


def test_confirm_ally_region_restored_and_liberation_emit_occupation_contribution():
    world = WorldState()
    _install_two_v_two_war(world)
    _open_contribution_episode_for_participant(
        world, "war_1", "Saxony", joined_turn=world.current_turn,
    )
    _open_contribution_episode_for_participant(
        world, "war_1", "France", joined_turn=world.current_turn,
    )
    world.regions["Saxony"].controller = "Austria"
    if "Bavaria" not in world.regions:
        world.regions["Bavaria"] = Region(
            name="Bavaria", region_type="major", income_value=80,
        )
    world.regions["Bavaria"].controller = "Bavaria"
    world.vassals["Bavaria"] = {
        "lord": "Austria", "subject": "Bavaria", "loyalty": 50, "tribute_pct": 30,
    }

    dialogue = _stage_dialogue(
        world,
        settlement_terms=[
            {
                "type": "territory_cede",
                "from": "Austria",
                "to": "Saxony",
                "regions": ["Saxony"],
            },
            {
                "type": "liberation",
                "vassal_nation": "Bavaria",
                "lord_nation": "Austria",
                "liberator": "France",
            },
        ],
        covered_enemy_participants=["Austria"],
    )
    result = ratify_settlement_confirm(world, dialogue)

    assert result["success"] is True
    saxony_episode = next(iter(world.war_contribution_scores["war_1"]["Saxony"]["episodes"].values()))
    france_episode = next(iter(world.war_contribution_scores["war_1"]["France"]["episodes"].values()))
    assert saxony_episode["occupation"] > 0
    assert france_episode["occupation"] > 0
