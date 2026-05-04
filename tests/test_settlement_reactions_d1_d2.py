"""Slice D1/D2 settlement / cross-war reaction routing tests.

The C2 ratification slice (commit ``f9af6f2`` + follow-ups) closed the
``settlement_confirm.confirm`` mutation but deliberately left the
post-ratification reactions for the next slice. This module pins:

* ``settlement_memories`` storage lifecycle (add / refresh / prune /
  save round-trip).
* ``settlement_gratitude_mod`` acceptance hook fires only for the
  spec-named proposal families and only when an active gratitude
  memory exists (spec §14.3).
* Proposer-side ally reactions: rewarded ally gets ``they_chose_us`` +
  ``settlement_gratitude``; shut-out ally with seat or
  ``material_share >= 0.20`` gets the ``settlement_shut_out`` grievance
  flag through the existing ``_add_grievance_flag`` machinery; zero-
  material major reduces relation hit and skips the grievance flag
  per spec §14.2 line 1469.
* Enemy-side sold-out reactions: only burdened non-leader participants
  get ``sold_out_by_war_leader`` memories, with relation deltas vs.
  France and the leader gradient by severity.
* WB-B integration: a French claim-region awarded to a different
  ally at settlement breaches the bargain through ``breach_bargain``.
* Cross-war reaction scan is bounded by ``war_instances_by_participant``
  (per spec §11.5 line 1241), and writes ``rival_strengthened``
  grievance flags into the affected war's pair record.
* ``settlement_summary`` / ``settlement_digest`` events emit through
  ``log_event`` + ``pending_dispatch_events`` with the spec §11.6 route
  metadata, and ``settlement_digest`` only fires once the primary-beat
  cap of 4 reactions is exceeded.
* The ratification entry point now returns ``settlement_reactions``
  in its summary and runs reactions AFTER cache invalidation but
  BEFORE ``dialogue_manager.pop()`` per spec line 1239.
"""

from __future__ import annotations

import copy

from backend.campaign_log import (
    CAMPAIGN_LOG_TYPES,
    CATEGORY_MAP,
    format_event_oneliner,
)
from backend.game_logic.diplomacy import (
    _add_grievance_flag,
    _get_grievance_flags,
    grievance_modifier,
)
from backend.game_logic.settlement_preview import (
    ratify_settlement_confirm,
    stage_settlement_confirm,
)
from backend.game_logic.settlement_reactions import (
    SETTLEMENT_DISPATCH_PRIMARY_CAP,
    SETTLEMENT_GRATITUDE_MOD,
    SETTLEMENT_GRATITUDE_TURNS,
    SOLD_OUT_BY_LEADER_TURNS,
    _add_settlement_memory,
    _compute_affected_nations,
    _evaluate_proposer_side_reactions,
    _gradient_relation,
    _scan_cross_war_reactions,
    get_settlement_memories,
    prune_expired_settlement_memories,
    route_settlement_reactions,
    settlement_gratitude_mod,
)
from backend.models.region import REGIONS_DATA
from backend.models.world_state import WorldState
from tests.helpers.full_europe_settlement_fixtures import (
    make_synthetic_war_instance,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _install_two_v_two_war(world: WorldState) -> dict:
    war = make_synthetic_war_instance(
        "war_d1",
        attackers=["France", "Saxony"],
        defenders=["Austria", "Prussia"],
        attacker_leader="France",
        defender_leader="Austria",
        created_turn=1,
        created_sequence=1,
    )
    world.war_instances["war_d1"] = war
    for pair in war["active_diplo_keys"]:
        nations = pair.split("|")
        world.diplomatic_states[pair] = "WAR"
        world.war_start_turns[pair] = world.current_turn
        first = nations[0]
        score = 60 if first not in ("France", "Saxony") else -60
        world.war_scores[pair] = -score
        world.battle_records[pair] = []
    world.invalidate_war_instance_indexes()
    return war


def _stage(world, *, war_id="war_d1", terms=None, covered=None):
    result = stage_settlement_confirm(
        world,
        war_id=war_id,
        settlement_terms=terms or [],
        covered_enemy_participants=covered,
    )
    assert result["success"] is True
    return world.pending_diplomatic_dialogue


# ===========================================================================
# Memory storage lifecycle
# ===========================================================================


class TestSettlementMemoryStorage:
    def test_add_memory_creates_record_with_expiry(self):
        world = WorldState()
        world.current_turn = 12
        record = _add_settlement_memory(
            world,
            actor="France",
            subject="Prussia",
            memory_type="settlement_gratitude",
            episode_id="ep_1",
            payload={"war_id": "war_42", "standing_level": "seat"},
            expires_in=10,
        )
        assert record["actor"] == "France"
        assert record["subject"] == "Prussia"
        assert record["memory_type"] == "settlement_gratitude"
        assert record["expires_on_turn"] == 22
        assert record["payload"]["standing_level"] == "seat"
        assert "France|Prussia" in world.settlement_memories

    def test_durable_memory_has_no_expiry(self):
        world = WorldState()
        world.current_turn = 5
        record = _add_settlement_memory(
            world,
            actor="France",
            subject="Saxony",
            memory_type="they_chose_us",
            episode_id="ep_2",
            payload={},
            expires_in=None,
        )
        assert record["expires_on_turn"] is None

    def test_refresh_replaces_same_type_memory_in_place(self):
        world = WorldState()
        world.current_turn = 1
        first = _add_settlement_memory(
            world,
            actor="France",
            subject="Prussia",
            memory_type="settlement_gratitude",
            episode_id="ep_a",
            payload={"first": True},
            expires_in=10,
        )
        assert first["expires_on_turn"] == 11
        world.current_turn = 7
        second = _add_settlement_memory(
            world,
            actor="France",
            subject="Prussia",
            memory_type="settlement_gratitude",
            episode_id="ep_b",
            payload={"second": True},
            expires_in=10,
        )
        # Same record reused, expires_on_turn refreshed to current+10.
        assert second["expires_on_turn"] == 17
        assert second["episode_id"] == "ep_b"
        records = world.settlement_memories["France|Prussia"]
        assert len(records) == 1

    def test_prune_drops_only_expired_transients(self):
        world = WorldState()
        world.current_turn = 1
        _add_settlement_memory(
            world, actor="France", subject="Prussia",
            memory_type="settlement_gratitude",
            episode_id="ep_g", payload={}, expires_in=5,
        )
        _add_settlement_memory(
            world, actor="France", subject="Prussia",
            memory_type="they_chose_us",
            episode_id="ep_t", payload={}, expires_in=None,
        )
        world.current_turn = 6
        pruned = prune_expired_settlement_memories(world)
        assert pruned == 1
        kinds = {
            r["memory_type"] for r in world.settlement_memories.get("France|Prussia", [])
        }
        assert kinds == {"they_chose_us"}

    def test_prune_removes_empty_pair_keys(self):
        world = WorldState()
        world.current_turn = 1
        _add_settlement_memory(
            world, actor="France", subject="Bavaria",
            memory_type="sold_out_by_war_leader",
            episode_id="ep_s", payload={}, expires_in=2,
        )
        world.current_turn = 4
        prune_expired_settlement_memories(world)
        assert "France|Bavaria" not in world.settlement_memories

    def test_save_round_trip_preserves_settlement_memories(self):
        world = WorldState()
        world.current_turn = 3
        _add_settlement_memory(
            world, actor="France", subject="Prussia",
            memory_type="settlement_context",
            episode_id="ep_x",
            payload={"war_id": "war_42", "standing_level": "consult"},
            expires_in=None,
        )
        data = world.to_dict()
        restored = WorldState.from_dict(data)
        assert "France|Prussia" in restored.settlement_memories
        record = restored.settlement_memories["France|Prussia"][0]
        assert record["memory_type"] == "settlement_context"
        assert record["payload"]["standing_level"] == "consult"
        assert record["expires_on_turn"] is None


# ===========================================================================
# settlement_gratitude_mod acceptance hook (spec §14.3 line 1482)
# ===========================================================================


class TestSettlementGratitudeMod:
    def test_returns_zero_when_no_memory(self):
        world = WorldState()
        assert (
            settlement_gratitude_mod(world, "France", "Prussia", "ALLIANCE") == 0
        )

    def test_fires_for_deep_treaty_when_memory_active(self):
        world = WorldState()
        world.current_turn = 1
        _add_settlement_memory(
            world, actor="France", subject="Prussia",
            memory_type="settlement_gratitude",
            episode_id="ep", payload={}, expires_in=10,
        )
        for proposal_type in ("ALLIANCE", "DEFENSIVE_ALLIANCE", "war_entry",
                              "war_bargain", "ally_entry"):
            assert (
                settlement_gratitude_mod(
                    world, "France", "Prussia", proposal_type
                )
                == SETTLEMENT_GRATITUDE_MOD
            )

    def test_skipped_for_non_treaty_proposals(self):
        world = WorldState()
        world.current_turn = 1
        _add_settlement_memory(
            world, actor="France", subject="Prussia",
            memory_type="settlement_gratitude",
            episode_id="ep", payload={}, expires_in=10,
        )
        for proposal_type in ("PEACE", "NON_AGGRESSION", "OPEN_BORDERS",
                              "TRADE", "WAR"):
            assert (
                settlement_gratitude_mod(
                    world, "France", "Prussia", proposal_type
                )
                == 0
            )

    def test_other_actor_does_not_steal_gratitude(self):
        world = WorldState()
        world.current_turn = 1
        _add_settlement_memory(
            world, actor="France", subject="Prussia",
            memory_type="settlement_gratitude",
            episode_id="ep", payload={}, expires_in=10,
        )
        # Austria asking Prussia must not benefit from France's reward.
        assert (
            settlement_gratitude_mod(world, "Austria", "Prussia", "ALLIANCE")
            == 0
        )


# ===========================================================================
# Proposer-side reactions (spec §14.1 / §14.3)
# ===========================================================================


class TestProposerSideReactions:
    def test_rewarded_seat_ally_gets_they_chose_us_and_relation_bonus(self):
        world = WorldState()
        war = _install_two_v_two_war(world)
        # Saxony is `secondary` by default tier; force `seat` standing
        # via a direct material-share contribution event.
        world.current_turn = 5
        # Award a region to Saxony as beneficiary.
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        starting_relation = world.nation_relations.get(
            world._make_diplo_key("France", "Saxony"), 0,
        )
        # Use the orchestrator entry point so the tested code mirrors
        # the post-ratification call shape from C2.
        summary = route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "Saxony",
                "beneficiary": "Saxony", "regions": [austria_region],
            }],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        ally_rewarded = [
            r for r in summary["proposer_side_reactions"]
            if r["kind"] == "ally_rewarded"
        ]
        assert ally_rewarded, "Saxony beneficiary should produce ally_rewarded"
        ally = ally_rewarded[0]
        assert ally["ally"] == "Saxony"
        assert ally["awarded_regions"] == [austria_region]
        # Relation bumped per the standing tier.
        new_relation = world.nation_relations.get(
            world._make_diplo_key("France", "Saxony"), 0,
        )
        assert new_relation > starting_relation
        # `they_chose_us` durable record exists.
        durable = get_settlement_memories(
            world, actor="France", subject="Saxony",
            memory_type="they_chose_us",
        )
        assert durable, "they_chose_us memory must be written"
        assert durable[0]["expires_on_turn"] is None

    def test_settlement_gratitude_only_when_material_points_positive(self):
        world = WorldState()
        _install_two_v_two_war(world)
        # No contribution events emitted → material_contribution_points == 0.
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "Saxony",
                "beneficiary": "Saxony", "regions": [austria_region],
            }],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        # Spec §14.3 line 1478: zero-material rewarded ally gets the
        # immediate relation bonus + they_chose_us, but NO transient
        # `settlement_gratitude` (which would farm the +5 hook).
        gratitude = get_settlement_memories(
            world, actor="France", subject="Saxony",
            memory_type="settlement_gratitude",
        )
        assert gratitude == [], (
            "Zero-material beneficiary must not get gratitude memory"
        )

    def test_shut_out_seat_ally_gets_grievance_flag_and_relation_hit(self):
        world = WorldState()
        _install_two_v_two_war(world)
        # Promote Saxony to `seat` standing via direct contribution.
        # Open episodes for both same-side participants then bump
        # Saxony's `battle` bucket so material_share >= 0.20.
        from backend.game_logic.war_contribution import open_episode
        sax_ep = open_episode(
            world, "war_d1", "Saxony", joined_turn=0, war_sequence=1,
        )
        sax_ep["battle"] = 200
        sax_ep["total"] = 200
        fra_ep = open_episode(
            world, "war_d1", "France", joined_turn=0, war_sequence=1,
        )
        fra_ep["battle"] = 50
        fra_ep["total"] = 50
        starting_relation = world.nation_relations.get(
            world._make_diplo_key("France", "Saxony"), 0,
        )
        # Settlement awards Austria's region to FRANCE, not Saxony.
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        summary = route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "France",
                "beneficiary": "France", "regions": [austria_region],
            }],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        shut_out = [
            r for r in summary["proposer_side_reactions"]
            if r["kind"] == "ally_shut_out" and r["ally"] == "Saxony"
        ]
        assert shut_out, "Saxony with seat must register a shut-out"
        # `settlement_shut_out` grievance flag is on France->Saxony pair.
        flags = _get_grievance_flags(world, "France", "Saxony")
        assert any(
            f.get("grievance_type") == "settlement_shut_out" for f in flags
        ), "Major shut-out must add a grievance flag"
        # Relation hit logged.
        new_relation = world.nation_relations.get(
            world._make_diplo_key("France", "Saxony"), 0,
        )
        assert new_relation < starting_relation

    def test_zero_material_major_seat_skips_grievance(self):
        """Spec §14.2 line 1469 — zero-material `major` reduces severity."""
        world = WorldState()
        war = _install_two_v_two_war(world)
        # Promote Saxony's tier to `major` for the test (spec call:
        # zero-material major with seat reduced reaction).
        if not hasattr(world, "_test_power_tiers"):
            world._test_power_tiers = {}
        world._test_power_tiers["Saxony"] = "major"
        original_tier_getter = getattr(world, "get_power_tier", None)
        world.get_power_tier = lambda nation: world._test_power_tiers.get(
            nation, original_tier_getter(nation) if callable(original_tier_getter) else "secondary"
        )
        # Saxony has no contribution events → material_points == 0.
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "France",
                "beneficiary": "France", "regions": [austria_region],
            }],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        # No grievance flag — reduced reaction band.
        flags = _get_grievance_flags(world, "France", "Saxony")
        assert not any(
            f.get("grievance_type") == "settlement_shut_out" for f in flags
        ), "Zero-material major-seat must NOT receive grievance flag"


# ===========================================================================
# Enemy-side reactions (spec §14.6 — sold_out_by_war_leader)
# ===========================================================================


class TestEnemySideSoldOut:
    def test_burdened_non_leader_gets_sold_out_memory(self):
        world = WorldState()
        _install_two_v_two_war(world)
        # Cede Prussia's region to France while Austria is the enemy
        # leader. Prussia is the burdened non-leader participant.
        prussia_region = next(
            (name for name in REGIONS_DATA
             if world.regions[name].controller == "Prussia"),
            None,
        )
        if prussia_region is None:
            prussia_region = next(
                name for name in REGIONS_DATA
                if world.regions[name].controller == "Austria"
            )
            world.regions[prussia_region].controller = "Prussia"
        starting_vs_france = world.nation_relations.get(
            world._make_diplo_key("France", "Prussia"), 0,
        )
        starting_vs_austria = world.nation_relations.get(
            world._make_diplo_key("Austria", "Prussia"), 0,
        )
        summary = route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Prussia", "to": "France",
                "regions": [prussia_region],
            }],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        sold_out = [
            r for r in summary["enemy_side_reactions"]
            if r["kind"] == "enemy_sold_out"
        ]
        assert sold_out, "Prussia burdened by territory loss must register"
        record = sold_out[0]
        assert record["burdened_participant"] == "Prussia"
        assert record["leader"] == "Austria"
        assert "territory_loss" in record["burdens"]
        # Relation hits applied — both vs proposer and vs leader.
        assert (
            world.nation_relations.get(
                world._make_diplo_key("France", "Prussia"), 0,
            )
            < starting_vs_france
        )
        assert (
            world.nation_relations.get(
                world._make_diplo_key("Austria", "Prussia"), 0,
            )
            < starting_vs_austria
        )
        # Sold-out memory written under leader->subject.
        memories = get_settlement_memories(
            world, actor="Austria", subject="Prussia",
            memory_type="sold_out_by_war_leader",
        )
        assert memories, "sold_out_by_war_leader memory must be written"
        assert memories[0]["expires_on_turn"] is not None

    def test_minor_terms_do_not_trigger_sold_out(self):
        """Spec §14.6 line 1518 — gold/AP/access alone does NOT fire."""
        world = WorldState()
        _install_two_v_two_war(world)
        world.nation_gold["Prussia"] = 200
        summary = route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria", "Prussia"],
            settlement_terms=[{
                "type": "gold_lump", "from": "Prussia", "to": "France",
                "amount": 50,
            }],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        sold_out = [
            r for r in summary["enemy_side_reactions"]
            if r["kind"] == "enemy_sold_out"
        ]
        assert sold_out == [], "Minor gold burden must not trigger sold-out"

    def test_severity_gradient_clamps_relation_deltas(self):
        # Light burden (1 territory loss) → milder hit.
        light = _gradient_relation(-25, -10, 1)
        # Heavy burden (vassalage = 3) → harsher.
        heavy = _gradient_relation(-25, -10, 4)
        assert -10 == light
        assert -25 == heavy
        assert _gradient_relation(-25, -10, 0) == 0


# ===========================================================================
# Bargain breach at settlement (spec §15)
# ===========================================================================


class TestBargainBreachAtSettlement:
    def _install_active_bargain(self, world, claim_region):
        from backend.game_logic.diplomacy import (
            _ensure_live_bargain_indexes,
        )
        commitments = getattr(world, "diplomatic_commitments", None)
        if commitments is None:
            commitments = {}
            world.diplomatic_commitments = commitments
        bargain = {
            "id": "wb_test_1",
            "type": "war_bargain",
            "war_id": "war_d1",
            "promiser": "France",
            "beneficiary": "Saxony",
            "target_enemy": "Austria",
            "claim_term": {"claim_region": claim_region},
            "status": "active",
            "created_turn": 1,
            "ended_turn": None,
            "cooldown_until_turn": 0,
            "zombie_clock_turns_elapsed": 0,
            "side_at_creation": "attackers",
        }
        commitments[bargain["id"]] = bargain
        # Mark the bargain index dirty so live-getter rebuilds.
        if hasattr(world, "_mark_live_bargain_indexes_dirty"):
            world._mark_live_bargain_indexes_dirty()
        _ensure_live_bargain_indexes(world)
        return bargain

    def test_claim_region_awarded_to_other_breaches_bargain(self):
        world = WorldState()
        _install_two_v_two_war(world)
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        bargain = self._install_active_bargain(world, austria_region)
        summary = route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "Bavaria",
                "beneficiary": "Bavaria", "regions": [austria_region],
            }],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        breaches = [
            r for r in summary["bargain_reactions"]
            if r["kind"] == "bargain_breach_at_settlement"
        ]
        assert breaches, "Awarding bargain region to other ally must breach"
        # Underlying bargain mutated.
        assert bargain["status"] == "breached"
        assert bargain["fault_nation"] == "France"

    def test_award_to_promiser_does_not_breach(self):
        world = WorldState()
        _install_two_v_two_war(world)
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        bargain = self._install_active_bargain(world, austria_region)
        summary = route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "France",
                "beneficiary": "France", "regions": [austria_region],
            }],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        assert summary["bargain_reactions"] == []
        # Bargain still live for lifecycle pass to fulfill next turn.
        assert bargain["status"] == "active"


# ===========================================================================
# Cross-war scan (spec §11.5 line 1241/1243)
# ===========================================================================


class TestCrossWarScan:
    def test_affected_nations_includes_term_payers_and_beneficiaries(self):
        affected = _compute_affected_nations(
            settlement_terms=[
                {"type": "territory_cede", "from": "Austria", "to": "France",
                 "regions": ["Bohemia"]},
                {"type": "liberation", "vassal_nation": "Saxony",
                 "lord_nation": "France", "liberator": "Prussia"},
            ],
            applied_clauses=[],
            resolved_pairs=[
                {"proposer_member": "France", "covered_enemy": "Austria"},
            ],
            covered_enemy_participants=["Austria"],
            proposer_side_members=["France", "Saxony"],
        )
        assert {"Austria", "France", "Saxony", "Prussia"} <= affected

    def test_cross_war_scan_uses_bounded_index(self):
        """Per spec §11.5 line 1241: scan only via war_instances_by_participant."""
        world = WorldState()
        _install_two_v_two_war(world)
        # Install a SEPARATE active war where Russia is at war with
        # France. The war_d1 settlement awarding Austria's territory
        # to France strengthens France — Russia (France's enemy in
        # war_other) should record a `rival_strengthened` grievance
        # against France.
        other = make_synthetic_war_instance(
            "war_other",
            attackers=["Russia"],
            defenders=["France"],
            attacker_leader="Russia",
            defender_leader="France",
            created_turn=1,
            created_sequence=2,
        )
        world.war_instances["war_other"] = other
        for pair in other["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
            world.war_start_turns[pair] = world.current_turn
            world.war_scores[pair] = 0
            world.battle_records[pair] = []
        world.invalidate_war_instance_indexes()
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        results = _scan_cross_war_reactions(
            world,
            own_war_id="war_d1",
            affected_nations={"Austria", "France", "Russia"},
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "France",
                "regions": [austria_region],
            }],
            episode_id="ep_cross",
            proposer_leader="France",
        )
        flags = _get_grievance_flags(world, "France", "Russia")
        kinds = {f.get("grievance_type") for f in flags}
        assert "rival_strengthened" in kinds
        assert any(
            r["kind"] == "cross_war_rival_strengthened"
            and r["victim"] == "Russia"
            for r in results
        )

    def test_cross_war_scan_skips_own_war(self):
        world = WorldState()
        _install_two_v_two_war(world)
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        results = _scan_cross_war_reactions(
            world,
            own_war_id="war_d1",
            affected_nations={"Austria", "France", "Saxony", "Prussia"},
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "France",
                "regions": [austria_region],
            }],
            episode_id="ep_cross",
            proposer_leader="France",
        )
        for r in results:
            assert r["cross_war_id"] != "war_d1"


# ===========================================================================
# Dispatch event emission (spec §11.6)
# ===========================================================================


class TestSettlementDispatchEvents:
    def test_settlement_summary_event_emitted(self):
        world = WorldState()
        _install_two_v_two_war(world)
        austria_region = next(
            name for name in REGIONS_DATA
            if world.regions[name].controller == "Austria"
        )
        summary = route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            settlement_terms=[{
                "type": "territory_cede", "from": "Austria", "to": "France",
                "regions": [austria_region],
            }],
            resolved_pairs=[],
            applied_clauses=[{
                "type": "territory_cede", "from": "Austria", "to": "France",
                "regions": [austria_region],
            }],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        event = summary["summary_event"]
        assert event["type"] == "settlement_summary"
        assert event["route"]["event_family"] == "settlement"
        assert event["route"]["review_target"] == "settlement_review"
        assert event["route"]["route_id"].startswith("settlement_summary:war_d1:")
        assert "settlement_summary" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP["settlement_summary"] == "diplomacy"
        # event_log + dispatch both received the event.
        types_in_log = {e.get("type") for e in world.event_log}
        types_in_dispatch = {
            e.get("type") for e in (world.pending_dispatch_events or [])
        }
        assert "settlement_summary" in types_in_log
        assert "settlement_summary" in types_in_dispatch

    def test_settlement_review_target_flips_to_ledger_when_war_ends(self):
        world = WorldState()
        _install_two_v_two_war(world)
        summary = route_settlement_reactions(
            world,
            war_id="war_d1",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            settlement_terms=[],
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=True,
        )
        assert (
            summary["summary_event"]["route"]["review_target"]
            == "diplomatic_ledger"
        )

    def test_digest_only_fires_when_reactions_exceed_primary_cap(self):
        world = WorldState()
        # Build a 1 vs many war so we get more than 4 reactions.
        war = make_synthetic_war_instance(
            "war_big",
            attackers=["France"],
            defenders=["Austria", "Prussia", "Bavaria", "Saxony", "Russia"],
            attacker_leader="France",
            defender_leader="Austria",
            created_turn=1,
            created_sequence=1,
        )
        world.war_instances["war_big"] = war
        for pair in war["active_diplo_keys"]:
            world.diplomatic_states[pair] = "WAR"
            world.war_start_turns[pair] = world.current_turn
            world.war_scores[pair] = 0
            world.battle_records[pair] = []
        world.invalidate_war_instance_indexes()
        # 4 enemy non-leader participants get burdened by territory loss.
        burden_terms = []
        for nation in ("Prussia", "Bavaria", "Saxony", "Russia"):
            region = next(
                (name for name in REGIONS_DATA
                 if world.regions[name].controller == nation),
                None,
            )
            if region is None:
                # Synthesize: borrow a region from Austria and stamp it.
                region = next(
                    name for name in REGIONS_DATA
                    if world.regions[name].controller == "Austria"
                )
                world.regions[region].controller = nation
            burden_terms.append({
                "type": "territory_cede", "from": nation, "to": "France",
                "regions": [region],
            })
        summary = route_settlement_reactions(
            world,
            war_id="war_big",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=[
                "Austria", "Prussia", "Bavaria", "Saxony", "Russia",
            ],
            settlement_terms=burden_terms,
            resolved_pairs=[],
            applied_clauses=[],
            pre_cleanup_snapshots=[],
            war_ended=False,
        )
        all_reactions = (
            summary["proposer_side_reactions"]
            + summary["enemy_side_reactions"]
            + summary["bargain_reactions"]
            + summary["cross_war_reactions"]
        )
        if len(all_reactions) > SETTLEMENT_DISPATCH_PRIMARY_CAP:
            assert summary["digest_event"] is not None
            assert summary["digest_event"]["type"] == "settlement_digest"
            assert (
                summary["digest_event"]["hidden_reaction_count"]
                == len(all_reactions) - SETTLEMENT_DISPATCH_PRIMARY_CAP
            )
            assert summary["digest_event"]["route"]["review_target"] == (
                "diplomatic_ledger"
            )
        else:
            assert summary["digest_event"] is None

    def test_format_event_oneliner_handles_summary_and_digest(self):
        event = {
            "type": "settlement_summary",
            "war_id": "war_42",
            "terms_summary": ["territory_cede: Austria→France"],
            "participant_reactions": [
                {"kind": "ally_rewarded", "ally": "Saxony"},
                {"kind": "enemy_sold_out", "burdened_participant": "Prussia"},
                {"kind": "ally_shut_out", "ally": "Bavaria"},
                {"kind": "ally_shut_out", "ally": "Russia"},
                {"kind": "ally_shut_out", "ally": "Sweden"},
            ],
        }
        line = format_event_oneliner(event)
        assert "war_42" in line
        # First three named, plus +N more.
        assert "Saxony" in line and "Prussia" in line and "Bavaria" in line
        assert "+2 more" in line

        digest = {
            "type": "settlement_digest",
            "war_id": "war_42",
            "hidden_reaction_count": 7,
        }
        digest_line = format_event_oneliner(digest)
        assert "7" in digest_line
        assert "war_42" in digest_line


# ===========================================================================
# Ratification wiring + ordering
# ===========================================================================


class TestRatificationWiring:
    def test_confirm_returns_settlement_reactions_in_summary(self):
        world = WorldState()
        _install_two_v_two_war(world)
        dialogue = _stage(world)
        result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        assert "settlement_reactions" in result
        assert isinstance(result["settlement_reactions"], dict)
        # All required reaction buckets present.
        for key in (
            "proposer_side_reactions",
            "enemy_side_reactions",
            "bargain_reactions",
            "cross_war_reactions",
            "affected_nations",
            "summary_event",
        ):
            assert key in result["settlement_reactions"]

    def test_settlement_summary_event_logged_after_confirm(self):
        world = WorldState()
        _install_two_v_two_war(world)
        dialogue = _stage(world, covered=["Austria"])
        result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        types_logged = [e.get("type") for e in world.event_log]
        assert "settlement_summary" in types_logged

    def test_invalidate_runs_before_reactions(self):
        """Spec §11 line 1239 — caches must invalidate before reactions read."""
        world = WorldState()
        _install_two_v_two_war(world)
        # Sentinel: prime the by-participant index then ratify; the
        # reactions module reads via `get_war_instances_by_participant`,
        # which only returns fresh data if invalidation ran first.
        prior = world.get_war_instances_by_participant("Austria")
        assert "war_d1" in prior
        dialogue = _stage(world)  # full settlement
        result = ratify_settlement_confirm(world, dialogue)
        assert result["success"] is True
        # After full settlement the war_instance ends; participant index
        # for Austria must reflect that (no longer including war_d1).
        post = world.get_war_instances_by_participant("Austria")
        assert "war_d1" not in post

    def test_dialogue_popped_after_reactions(self):
        world = WorldState()
        _install_two_v_two_war(world)
        dialogue = _stage(world)
        ratify_settlement_confirm(world, dialogue)
        assert world.pending_diplomatic_dialogue is None


# ===========================================================================
# Per-turn pruning is wired into advance_turn
# ===========================================================================


class TestAdvanceTurnPruning:
    def test_advance_turn_prunes_expired_memories(self):
        world = WorldState()
        world.current_turn = 1
        _add_settlement_memory(
            world, actor="France", subject="Prussia",
            memory_type="settlement_gratitude",
            episode_id="ep", payload={}, expires_in=1,
        )
        # Sanity check.
        assert get_settlement_memories(
            world, actor="France", subject="Prussia",
            memory_type="settlement_gratitude",
        )
        world.advance_turn()
        # current_turn becomes 2; the memory expires_on_turn == 2 → pruned.
        assert get_settlement_memories(
            world, actor="France", subject="Prussia",
            memory_type="settlement_gratitude",
        ) == []
