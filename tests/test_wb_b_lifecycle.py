"""WB-B: War bargain lifecycle — fulfillment, breach, void, zombie clock."""

import pytest
from backend.game_logic.diplomacy import (
    _get_live_bargains,
    _is_bargain_live,
    _source_treaty_valid,
    _claim_basis_valid,
    _are_cobelligerents,
    _check_bargain_fulfillment,
    _fulfill_bargain,
    _void_bargain,
    _detect_void,
    _process_zombie_clock,
    breach_bargain,
    process_bargain_lifecycle,
    detect_bargain_breach_on_treaty_change,
    detect_bargain_breach_on_peace,
    create_war_bargain_commitment,
    set_diplomatic_state,
    execute_downgrade,
    break_treaty,
    get_peace_commitment_conflicts,
    _archive_concluded_bargains,
    _get_live_bargains_by_promiser,
    BARGAIN_ARCHIVE_GRACE_TURNS,
    BARGAIN_BREACH_COOLDOWN_TURNS,
    BARGAIN_VOID_COOLDOWN_TURNS,
    BARGAIN_ZOMBIE_VOID_THRESHOLD,
    BARGAIN_FULFILLMENT_RELIABILITY_DELTA,
    BARGAIN_FULFILLMENT_RELATION_DELTA,
    BARGAIN_BREACH_RELIABILITY_DELTA,
    BARGAIN_BREACH_RELATION_DELTA,
)
from backend.models.world_state import WorldState


def _wb_world() -> WorldState:
    world = WorldState()
    world.enemy_nations = ["Austria", "Prussia", "Britain", "Russia", "Saxony"]
    world.diplomatic_states = {}
    world.active_treaties = {}
    world.vassals = {}
    world.pending_dispatch_events = []
    world.event_log = []
    world.diplomatic_commitments = {}
    world.next_commitment_id = 1
    world.diplomatic_reliability = {"France": 50, "Prussia": 50, "Britain": 50}
    world.betrayal_history = {}
    world.current_turn = 5
    return world


def _create_live_bargain(world, status="active", **overrides):
    """Helper: set up alliance + war + create bargain."""
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "setup")
    set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
    rec = create_war_bargain_commitment(
        world, "France", "Prussia", "Britain", "Hanover",
        "treaty_clause", "France|Prussia",
    )
    if status == "triggered":
        rec["status"] = "triggered"
        rec["triggered_turn"] = int(world.current_turn)
        set_diplomatic_state(world, "Prussia", "Britain", "WAR", "setup")
    for k, v in overrides.items():
        rec[k] = v
    return rec


def _add_active_treaty(world, nation_a="France", nation_b="Prussia", treaty_type="alliance"):
    pair_key = world._make_diplo_key(nation_a, nation_b)
    world.active_treaties[pair_key] = {
        "nations": [nation_a, nation_b],
        "type": treaty_type,
        "clauses": [],
        "turn_signed": max(0, int(world.current_turn) - 2),
    }
    return pair_key


# ═══════════════════════════════════════════════════════
# STATUS TRANSITIONS (6 tests)
# ═══════════════════════════════════════════════════════

class TestStatusTransitions:
    def test_active_to_triggered_on_cobelligerence(self):
        world = _wb_world()
        _create_live_bargain(world)
        set_diplomatic_state(world, "Prussia", "Britain", "WAR", "setup")
        events = process_bargain_lifecycle(world)
        bargain = list(world.diplomatic_commitments.values())[0]
        assert bargain["status"] == "triggered"
        assert bargain["triggered_turn"] == world.current_turn
        assert any(e["type"] == "bargain_triggered" for e in events)

    def test_stays_active_without_cobelligerence(self):
        world = _wb_world()
        _create_live_bargain(world)
        events = process_bargain_lifecycle(world)
        bargain = list(world.diplomatic_commitments.values())[0]
        assert bargain["status"] == "active"
        assert not any(e["type"] == "bargain_triggered" for e in events)

    def test_triggered_to_active_on_inconclusive_war(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        # End the war between Prussia and Britain — no longer co-belligerents
        set_diplomatic_state(world, "Prussia", "Britain", "PEACE", "peace")
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "active"
        assert rec["dormant_notice_fired"] is False

    def test_triggered_does_not_reactivate_when_treaty_lost(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        # Break the source treaty
        set_diplomatic_state(world, "France", "Prussia", "PEACE", "break")
        set_diplomatic_state(world, "Prussia", "Britain", "PEACE", "peace")
        events = process_bargain_lifecycle(world)
        # Should void instead of reactivating
        assert rec["status"] == "void"

    def test_fulfilled_is_terminal(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        # France controls Hanover
        world.regions["Hanover"].controller = "France"
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "fulfilled"
        assert rec["ended_turn"] == world.current_turn
        # Further processing doesn't change it
        events2 = process_bargain_lifecycle(world)
        assert rec["status"] == "fulfilled"

    def test_breached_is_terminal(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        breach_bargain(world, rec, "source_treaty_downgrade")
        assert rec["status"] == "breached"
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "breached"


# ═══════════════════════════════════════════════════════
# FULFILLMENT (7 tests)
# ═══════════════════════════════════════════════════════

class TestFulfillment:
    def test_fulfillment_all_conditions_met(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        world.regions["Hanover"].controller = "France"
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "fulfilled"
        assert rec["fulfillment_snapshot"] is not None
        assert rec["fulfillment_snapshot"]["claim_region"] == "Hanover"
        assert rec["fulfillment_snapshot"]["reliability_delta"] == BARGAIN_FULFILLMENT_RELIABILITY_DELTA
        assert rec["fulfillment_snapshot"]["relation_delta"] == BARGAIN_FULFILLMENT_RELATION_DELTA

    def test_fulfillment_reliability_increase(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        world.regions["Hanover"].controller = "France"
        old_rel = world.diplomatic_reliability["France"]
        process_bargain_lifecycle(world)
        assert world.diplomatic_reliability["France"] == old_rel + BARGAIN_FULFILLMENT_RELIABILITY_DELTA

    def test_fulfillment_relation_increase(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        world.regions["Hanover"].controller = "France"
        diplo_key = world._make_diplo_key("France", "Prussia")
        old_rel = world.nation_relations.get(diplo_key, 0)
        process_bargain_lifecycle(world)
        assert world.nation_relations[diplo_key] == old_rel + BARGAIN_FULFILLMENT_RELATION_DELTA

    def test_fulfillment_fails_without_region_control(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        # Hanover still controlled by Britain
        events = process_bargain_lifecycle(world)
        assert rec["status"] != "fulfilled"

    def test_fulfillment_fails_without_source_treaty(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        world.regions["Hanover"].controller = "France"
        set_diplomatic_state(world, "France", "Prussia", "NON_AGGRESSION", "break")
        events = process_bargain_lifecycle(world)
        # Should void (source treaty lost) rather than fulfill
        assert rec["status"] != "fulfilled"

    def test_fulfillment_10_turn_cap(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        world.regions["Hanover"].controller = "France"
        # Simulate prior fulfillment 3 turns ago
        if not hasattr(world, "_bargain_fulfillment_log"):
            world._bargain_fulfillment_log = {}
        world._bargain_fulfillment_log["France|Prussia"] = int(world.current_turn) - 3
        process_bargain_lifecycle(world)
        assert rec["fulfillment_snapshot"]["reward_reduced"] == "full"
        assert rec["fulfillment_snapshot"]["reliability_delta"] == 0

    def test_fulfillment_outside_cap_window(self):
        world = _wb_world()
        world.current_turn = 20
        rec = _create_live_bargain(world, status="triggered")
        world.regions["Hanover"].controller = "France"
        if not hasattr(world, "_bargain_fulfillment_log"):
            world._bargain_fulfillment_log = {}
        world._bargain_fulfillment_log["France|Prussia"] = 5  # 15 turns ago
        process_bargain_lifecycle(world)
        assert rec["fulfillment_snapshot"]["reward_reduced"] == "none"
        assert rec["fulfillment_snapshot"]["reliability_delta"] == BARGAIN_FULFILLMENT_RELIABILITY_DELTA


# ═══════════════════════════════════════════════════════
# BREACH (7 tests)
# ═══════════════════════════════════════════════════════

class TestBreach:
    def test_breach_sets_terminal_fields(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        breach_bargain(world, rec, "source_treaty_downgrade")
        assert rec["status"] == "breached"
        assert rec["end_reason"] == "source_treaty_downgrade"
        assert rec["end_reason_family"] == "french_breach"
        assert rec["fault_nation"] == "France"
        assert rec["ended_turn"] == world.current_turn

    def test_breach_cooldown_set(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        breach_bargain(world, rec, "test_reason")
        assert rec["cooldown_until_turn"] == world.current_turn + BARGAIN_BREACH_COOLDOWN_TURNS

    def test_breach_reliability_loss(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        old_rel = world.diplomatic_reliability["France"]
        breach_bargain(world, rec, "test_reason")
        assert world.diplomatic_reliability["France"] == old_rel + BARGAIN_BREACH_RELIABILITY_DELTA

    def test_breach_relation_penalty(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        diplo_key = world._make_diplo_key("France", "Prussia")
        old_rel = world.nation_relations.get(diplo_key, 0)
        breach_bargain(world, rec, "test_reason")
        assert world.nation_relations[diplo_key] == old_rel + BARGAIN_BREACH_RELATION_DELTA

    def test_breach_records_strike(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        breach_bargain(world, rec, "test_reason")
        diplo_key = world._make_diplo_key("France", "Prussia")
        record = world.betrayal_history.get(diplo_key)
        assert record is not None
        assert len(record["strikes"]) == 1
        assert record["strikes"][0]["source"] == "bargain_breach"

    def test_breach_respects_2_strike_cap(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        ep_id = "ep_test"
        # Pre-add 2 strikes with same episode
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.betrayal_history[diplo_key] = {
            "strikes": [
                {"severity": "high", "turn": 1, "source": "treaty_breach", "episode_id": ep_id, "decays_on_turn": 21},
                {"severity": "high", "turn": 1, "source": "treaty_breach", "episode_id": ep_id, "decays_on_turn": 21},
            ],
            "categories": {"treaty_breach"},
            "grievance_flags": [],
        }
        breach_bargain(world, rec, "test_reason", episode_id=ep_id)
        assert len(world.betrayal_history[diplo_key]["strikes"]) == 2  # No new strike

    def test_breach_cap_counts_only_active_same_episode_strikes(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        ep_id = "ep_old"
        diplo_key = "France|Prussia"
        world.betrayal_history[diplo_key] = {
            "strikes": [
                {"severity": "medium", "turn": 1, "source": "treaty_breach", "episode_id": ep_id, "decays_on_turn": 2},
                {"severity": "medium", "turn": 1, "source": "treaty_breach", "episode_id": ep_id, "decays_on_turn": 2},
            ],
            "categories": ["treaty_breach"],
            "grievance_flags": [],
            "last_turn": 1,
        }
        breach_bargain(world, rec, "test_reason", episode_id=ep_id)
        assert len(world.betrayal_history[diplo_key]["strikes"]) == 3

    def test_breach_records_actor_victim_key_and_list_categories(self):
        world = _wb_world()
        set_diplomatic_state(world, "France", "Austria", "ALLIANCE", "setup")
        set_diplomatic_state(world, "France", "Britain", "WAR", "setup")
        rec = create_war_bargain_commitment(
            world, "France", "Austria", "Britain", "Hanover",
            "treaty_clause", "Austria|France",
            validate=False,
        )
        world.betrayal_history["France|Austria"] = {
            "strikes": [],
            "categories": ["treaty_breach"],
            "grievance_flags": [],
            "last_turn": 1,
        }
        breach_bargain(world, rec, "test_reason", episode_id="ep_key")
        assert "France|Austria" in world.betrayal_history
        assert "Austria|France" not in world.betrayal_history
        assert isinstance(world.betrayal_history["France|Austria"]["categories"], list)
        assert "bargain_breach" in world.betrayal_history["France|Austria"]["categories"]

    def test_breach_on_already_terminal_noop(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        rec["status"] = "fulfilled"
        result = breach_bargain(world, rec, "test_reason")
        assert result == {}
        assert rec["status"] == "fulfilled"


# ═══════════════════════════════════════════════════════
# VOID (7 tests)
# ═══════════════════════════════════════════════════════

class TestVoid:
    def test_void_counterparty_treaty_break(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        # Beneficiary breaks source treaty
        set_diplomatic_state(world, "France", "Prussia", "NON_AGGRESSION", "break")
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "void"
        assert rec["end_reason_family"] == "counterparty_reversal"
        assert rec["fault_nation"] == "Prussia"

    def test_void_beneficiary_aligns_with_enemy(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        set_diplomatic_state(world, "Prussia", "Britain", "NON_AGGRESSION", "setup")
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "void"
        assert rec["end_reason"] == "beneficiary_aligned_with_enemy"
        assert rec["end_reason_family"] == "counterparty_reversal"

    def test_void_beneficiary_joins_anti_promiser_coalition(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        world.active_coalition = {"target_nation": "France", "members": ["Prussia", "Austria"]}
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "void"
        assert rec["end_reason"] == "beneficiary_joined_anti_promiser_coalition"

    def test_void_claim_basis_lost(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        # Third party takes Hanover
        world.regions["Hanover"].controller = "Russia"
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "void"
        assert rec["end_reason"] == "claim_basis_lost"
        assert rec["end_reason_family"] == "obsolescence_or_external"

    def test_void_parties_at_war(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        # Setting to WAR destroys the source treaty first, so source_treaty_lost fires
        set_diplomatic_state(world, "France", "Prussia", "WAR", "war")
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "void"
        assert rec["end_reason"] == "source_treaty_lost"
        assert rec["end_reason_family"] == "counterparty_reversal"

    def test_void_cooldown_set(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        world.regions["Hanover"].controller = "Russia"
        process_bargain_lifecycle(world)
        assert rec["cooldown_until_turn"] == world.current_turn + BARGAIN_VOID_COOLDOWN_TURNS

    def test_void_no_reliability_loss(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        old_rel = world.diplomatic_reliability["France"]
        world.regions["Hanover"].controller = "Russia"
        process_bargain_lifecycle(world)
        assert world.diplomatic_reliability["France"] == old_rel


# ═══════════════════════════════════════════════════════
# ZOMBIE CLOCK (5 tests)
# ═══════════════════════════════════════════════════════

class TestZombieClock:
    def test_zombie_increments_when_both_armistice(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        set_diplomatic_state(world, "France", "Britain", "ARMISTICE", "arm")
        set_diplomatic_state(world, "Prussia", "Britain", "ARMISTICE", "arm")
        _process_zombie_clock(world, rec)
        assert rec["zombie_clock_turns_elapsed"] == 1

    def test_zombie_resets_on_war(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        rec["zombie_clock_turns_elapsed"] = 3
        # France still at WAR with Britain (set by _create_live_bargain)
        _process_zombie_clock(world, rec)
        assert rec["zombie_clock_turns_elapsed"] == 0

    def test_zombie_voids_at_threshold(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        rec["zombie_clock_turns_elapsed"] = BARGAIN_ZOMBIE_VOID_THRESHOLD - 1
        set_diplomatic_state(world, "France", "Britain", "ARMISTICE", "arm")
        set_diplomatic_state(world, "Prussia", "Britain", "ARMISTICE", "arm")
        _process_zombie_clock(world, rec)
        assert rec["status"] == "void"
        assert rec["end_reason"] == "zombie_lapse"

    def test_zombie_does_not_increment_if_one_at_war(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        # France at WAR, Prussia at ARMISTICE
        set_diplomatic_state(world, "Prussia", "Britain", "ARMISTICE", "arm")
        _process_zombie_clock(world, rec)
        assert rec["zombie_clock_turns_elapsed"] == 0

    def test_zombie_increments_at_peace_too(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        set_diplomatic_state(world, "France", "Britain", "PEACE", "peace")
        set_diplomatic_state(world, "Prussia", "Britain", "PEACE", "peace")
        _process_zombie_clock(world, rec)
        assert rec["zombie_clock_turns_elapsed"] == 1


# ═══════════════════════════════════════════════════════
# BREACH DETECTION ON STATE CHANGES (5 tests)
# ═══════════════════════════════════════════════════════

class TestBargainScaleIndexes:
    def test_live_bargains_by_promiser_filters_relevant_bargains(self):
        world = _wb_world()
        france_bargain = _create_live_bargain(world)
        world.diplomatic_commitments["99"] = {
            "id": 99,
            "type": "war_bargain",
            "status": "active",
            "promiser": "Austria",
            "beneficiary": "Saxony",
            "target_enemy": "Russia",
            "claim_term": {"claim_region": "Bohemia"},
        }
        world._live_bargain_indexes_dirty = True

        assert _get_live_bargains_by_promiser(world, "France") == [france_bargain]

    def test_old_terminal_bargains_archive_out_of_hot_store(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        rec["status"] = "fulfilled"
        rec["ended_turn"] = int(world.current_turn) - BARGAIN_ARCHIVE_GRACE_TURNS
        world._live_bargain_indexes_dirty = True

        archived = _archive_concluded_bargains(world)

        assert archived == 1
        assert world.diplomatic_commitments == {}
        assert len(world.archived_diplomatic_commitments) == 1
        assert world.archived_diplomatic_commitments[0]["archived_commitment_id"] == "1"

    def test_recent_terminal_bargain_stays_in_hot_store_until_grace_expires(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        rec["status"] = "void"
        rec["ended_turn"] = int(world.current_turn) - BARGAIN_ARCHIVE_GRACE_TURNS + 1
        world._live_bargain_indexes_dirty = True

        archived = _archive_concluded_bargains(world)

        assert archived == 0
        assert "1" in world.diplomatic_commitments
        assert world.archived_diplomatic_commitments == []


class TestBreachDetection:
    def test_breach_on_source_treaty_downgrade(self):
        world = _wb_world()
        _create_live_bargain(world)
        events = detect_bargain_breach_on_treaty_change(
            world, "France", "Prussia", "NON_AGGRESSION",
        )
        assert len(events) == 1
        bargain = list(world.diplomatic_commitments.values())[0]
        assert bargain["status"] == "breached"
        assert bargain["end_reason"] == "source_treaty_downgrade"

    def test_breach_on_normalization_with_enemy(self):
        world = _wb_world()
        _create_live_bargain(world)
        events = detect_bargain_breach_on_treaty_change(
            world, "France", "Britain", "NON_AGGRESSION",
        )
        assert len(events) == 1
        bargain = list(world.diplomatic_commitments.values())[0]
        assert bargain["end_reason"] == "normalization_with_enemy"

    def test_no_breach_on_unrelated_state_change(self):
        world = _wb_world()
        _create_live_bargain(world)
        events = detect_bargain_breach_on_treaty_change(
            world, "France", "Russia", "NON_AGGRESSION",
        )
        assert len(events) == 0
        bargain = list(world.diplomatic_commitments.values())[0]
        assert bargain["status"] == "active"

    def test_breach_on_peace_with_named_enemy(self):
        world = _wb_world()
        _create_live_bargain(world)
        events = detect_bargain_breach_on_peace(world, "France", "Britain")
        assert len(events) == 1
        bargain = list(world.diplomatic_commitments.values())[0]
        assert bargain["end_reason"] == "peace_with_named_enemy"

    def test_no_breach_on_peace_with_unrelated_nation(self):
        world = _wb_world()
        _create_live_bargain(world)
        events = detect_bargain_breach_on_peace(world, "France", "Russia")
        assert len(events) == 0

    def test_break_treaty_wires_source_bargain_breach(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        pair_key = _add_active_treaty(world)
        result = break_treaty(pair_key, "France", world)
        assert result["success"] is True
        assert rec["status"] == "breached"
        assert rec["end_reason"] == "source_treaty_downgrade"
        assert result["bargain_breach_events"][0]["type"] == "bargain_breached"

    def test_execute_downgrade_wires_source_bargain_breach(self):
        world = _wb_world()
        rec = _create_live_bargain(world)
        first = execute_downgrade(world, "France", "Prussia")
        assert first["success"] is True
        result = execute_downgrade(world, "France", "Prussia")
        assert result["success"] is True
        assert rec["status"] == "breached"
        assert rec["end_reason"] == "source_treaty_downgrade"
        assert result["bargain_breach_events"][0]["type"] == "bargain_breached"

    def test_peace_ratification_wires_named_enemy_breach(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        world.nation_relations[world._make_diplo_key("France", "Britain")] = 0
        result = world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Britain",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        })
        assert result["type"] == "diplomatic_treaty_signed"
        assert rec["status"] == "breached"
        assert rec["end_reason"] == "peace_with_named_enemy"
        assert result["bargain_breach_events"][0]["type"] == "bargain_breached"

    def test_peace_ratification_can_fulfill_after_claim_transfer(self):
        world = _wb_world()
        rec = _create_live_bargain(world, status="triggered")
        world.nation_relations[world._make_diplo_key("France", "Britain")] = 0
        result = world._ratify_treaty({
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Britain",
            "sweeteners": [],
            "demands": [
                {"type": "territory_cede", "regions": ["Hanover"], "value": 0},
            ],
            "clauses": [],
        })
        assert result["type"] == "diplomatic_treaty_signed"
        assert rec["status"] == "triggered"
        events = process_bargain_lifecycle(world)
        assert rec["status"] == "fulfilled"
        assert any(e["type"] == "bargain_fulfilled" for e in events)

    def test_peace_conflicts_include_unresolved_bargain_breach_warning(self):
        world = _wb_world()
        _create_live_bargain(world)
        conflicts = get_peace_commitment_conflicts(world, "France", "Britain", [])
        bargain_conflicts = [
            c for c in conflicts if c["conflict_type"] == "bargain_breach"
        ]
        assert len(bargain_conflicts) == 1
        assert bargain_conflicts[0]["severity"] == "WARNING"
        assert bargain_conflicts[0]["affected_entity"] == "Prussia"

    def test_peace_conflict_suppressed_when_terms_transfer_claim(self):
        world = _wb_world()
        _create_live_bargain(world)
        conflicts = get_peace_commitment_conflicts(
            world,
            "France",
            "Britain",
            [
                {
                    "type": "territory_cede",
                    "regions": ["Hanover"],
                    "from": "Britain",
                    "to": "France",
                },
            ],
        )
        assert not any(c["conflict_type"] == "bargain_breach" for c in conflicts)


# ═══════════════════════════════════════════════════════
# CAMPAIGN LOG + DISPATCH (3 tests)
# ═══════════════════════════════════════════════════════

class TestEventEmission:
    def test_bargain_triggered_emits_event(self):
        world = _wb_world()
        _create_live_bargain(world)
        set_diplomatic_state(world, "Prussia", "Britain", "WAR", "setup")
        events = process_bargain_lifecycle(world)
        assert any(e["type"] == "bargain_triggered" for e in events)
        assert any(e.get("type") == "bargain_triggered" for e in world.event_log)

    def test_bargain_fulfilled_emits_event(self):
        world = _wb_world()
        _create_live_bargain(world, status="triggered")
        world.regions["Hanover"].controller = "France"
        events = process_bargain_lifecycle(world)
        assert any(e["type"] == "bargain_fulfilled" for e in events)

    def test_bargain_voided_emits_event(self):
        world = _wb_world()
        _create_live_bargain(world)
        world.regions["Hanover"].controller = "Russia"
        events = process_bargain_lifecycle(world)
        assert any(e["type"] == "bargain_voided" for e in events)
        dispatched = [e for e in world.pending_dispatch_events if e.get("type") == "bargain_voided"]
        assert len(dispatched) >= 1


# ═══════════════════════════════════════════════════════
# DORMANT NOTICE (2 tests)
# ═══════════════════════════════════════════════════════

class TestDormantNotice:
    def test_dormant_fires_after_8_turns(self):
        world = _wb_world()
        world.current_turn = 15
        rec = _create_live_bargain(world)
        rec["created_turn"] = 5
        process_bargain_lifecycle(world)
        assert rec["dormant_notice_fired"] is True
        assert any(
            e.get("type") == "bargain_dormant_notice"
            for e in world.pending_dispatch_events
        )

    def test_dormant_resets_on_reactivation(self):
        world = _wb_world()
        world.current_turn = 15
        rec = _create_live_bargain(world, status="triggered")
        rec["created_turn"] = 5
        rec["dormant_notice_fired"] = True
        # End the war → reactivation
        set_diplomatic_state(world, "Prussia", "Britain", "PEACE", "peace")
        process_bargain_lifecycle(world)
        assert rec["dormant_notice_fired"] is False
