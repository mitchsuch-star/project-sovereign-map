"""
Session 8A Tests — Diplomatic Ledger, Debug Arsenal, Pass-throughs, Top Bar

Tests cover:
  - Diplomatic Ledger builder (4 tabs × ~5 tests)
  - Fog design for army_strength
  - Cheat commands (11 × 2 tests)
  - Debug endpoints (8 tests)
  - Pass-through wiring (3 tests)
  - Top-bar /test fields (1 test)
"""

import os
import pytest

# Ensure mock mode for tests
os.environ["LLM_MODE"] = "mock"

from backend.models.world_state import WorldState
from backend.game_logic.diplomatic_ledger import (
    build_diplomatic_ledger,
    _get_nation_visibility,
    _format_army_strength,
)
from backend.models.intel import FULL, PARTIAL, STALE, UNKNOWN
from backend.commands.executor import CommandExecutor


# ════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with sensible defaults for testing."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _set_relation(world, nation_a, nation_b, value):
    key = "|".join(sorted([nation_a, nation_b]))
    world.nation_relations[key] = value


def _set_diplo_state(world, nation_a, nation_b, state):
    key = "|".join(sorted([nation_a, nation_b]))
    world.diplomatic_states[key] = state


def _make_game_state(world):
    """Create game_state dict as used by executor."""
    return {"world": world, "debug_mode": True}


# ════════════════════════════════════════════════════════════════
# TAB 1: NATIONS
# ════════════════════════════════════════════════════════════════

class TestDiplomaticLedgerNations:
    """Tests for nations tab of diplomatic ledger."""

    def test_nations_returns_all_enemy_nations(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        nations = ledger["nations"]
        nation_names = [n["name"] for n in nations]
        assert "Britain" in nation_names
        assert "Prussia" in nation_names
        assert "Austria" in nation_names
        assert "Saxony" in nation_names
        # Player (France) should NOT be in the list
        assert "France" not in nation_names

    def test_nations_correct_keys(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        nation = ledger["nations"][0]
        required_keys = {
            "name", "diplomatic_state", "relation", "diplomat",
            "army_strength", "regions_controlled", "active_treaties",
            "vassal_eligible", "bloc_stamp",
        }
        assert required_keys.issubset(set(nation.keys()))

    def test_nations_relation_is_int(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        for nation in ledger["nations"]:
            assert isinstance(nation["relation"], int)

    def test_nations_regions_controlled_is_int(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        for nation in ledger["nations"]:
            assert isinstance(nation["regions_controlled"], int)

    def test_nations_diplomat_info(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        # Find Britain
        britain = next(n for n in ledger["nations"] if n["name"] == "Britain")
        assert britain["diplomat"] is not None
        assert britain["diplomat"]["name"] == "Castlereagh"
        assert britain["diplomat"]["personality"] == "hawk"
        assert isinstance(britain["diplomat"]["skill"], int)

    def test_nations_diplomatic_state(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        britain = next(n for n in ledger["nations"] if n["name"] == "Britain")
        assert britain["diplomatic_state"] == "WAR"

    def test_nations_major_power_not_vassal_eligible_at_war(self):
        """Major powers at war should not show the vassalizable ledger stamp."""
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        britain = next(n for n in ledger["nations"] if n["name"] == "Britain")
        assert britain["power_tier"] == "major"
        assert britain["vassal_eligible"] is False
        assert britain["vassal_block_reason"] == "major_power"

    def test_nations_minor_power_vassal_eligible_at_war(self):
        """Minor powers can still show the vassalizable ledger stamp."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "WAR")
        _set_relation(world, "France", "Saxony", -20)
        ledger = build_diplomatic_ledger(world)
        saxony = next(n for n in ledger["nations"] if n["name"] == "Saxony")
        assert saxony["power_tier"] == "minor"
        assert saxony["vassal_eligible"] is True
        assert saxony["vassal_block_reason"] is None

    def test_nations_minor_power_vassal_eligible_from_open_borders(self):
        """Saxony's starting Open Borders treaty path is vassal-eligible."""
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        saxony = next(n for n in ledger["nations"] if n["name"] == "Saxony")
        assert saxony["diplomatic_state"] == "OPEN_BORDERS"
        assert saxony["power_tier"] == "minor"
        assert saxony["vassal_eligible"] is True
        assert saxony["vassal_block_reason"] is None

    def test_nations_vassal_not_eligible_when_vassal(self):
        world = _make_world()
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1}
        ledger = build_diplomatic_ledger(world)
        saxony = next(n for n in ledger["nations"] if n["name"] == "Saxony")
        assert saxony["vassal_eligible"] is False


# ════════════════════════════════════════════════════════════════
# FOG DESIGN: ARMY STRENGTH VISIBILITY
# ════════════════════════════════════════════════════════════════

    def test_nations_bloc_stamp_uses_proper_bloc_name_at_fifty_percent(self):
        """Opening Balance geometry stamps Prussia's bloc with its proper name."""
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        prussia = next(n for n in ledger["nations"] if n["name"] == "Prussia")
        austria = next(n for n in ledger["nations"] if n["name"] == "Austria")
        saxony = next(n for n in ledger["nations"] if n["name"] == "Saxony")

        assert prussia["bloc_stamp"] == {
            "label": "Berlin Alignment",
            "kind": "proper_bloc",
            "priority": 80,
        }
        assert austria["bloc_stamp"]["label"] == "Berlin Alignment"
        assert saxony["bloc_stamp"] == {
            "label": "Neutral",
            "kind": "neutral",
            "priority": 10,
        }

    def test_nations_bloc_stamp_uses_descriptive_label_at_noticed_band(self):
        """33-49% bands use the helper's descriptive label, not a proper noun."""
        world = _make_world()
        world.diplomatic_states = {}
        world.vassals = {}
        _set_diplo_state(world, "France", "Saxony", "ALLIANCE")
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()

        ledger = build_diplomatic_ledger(world)
        saxony = next(n for n in ledger["nations"] if n["name"] == "Saxony")
        assert saxony["bloc_stamp"] == {
            "label": "French-led alignment",
            "kind": "descriptive_bloc",
            "priority": 70,
        }

    def test_nations_coalition_member_stamp_dominates_bloc_label(self):
        """Formal coalition membership wins over hegemon-bloc labels."""
        world = _make_world()
        world.active_coalition = {
            "name": "First Coalition",
            "leader": "Prussia",
            "members": ["Prussia", "Saxony"],
        }
        ledger = build_diplomatic_ledger(world)
        prussia = next(n for n in ledger["nations"] if n["name"] == "Prussia")
        saxony = next(n for n in ledger["nations"] if n["name"] == "Saxony")

        assert prussia["bloc_stamp"] == {
            "label": "Coalition Member",
            "kind": "coalition",
            "priority": 100,
        }
        assert saxony["bloc_stamp"]["label"] == "Coalition Member"

    def test_nations_vassal_stamp_for_non_bloc_vassal(self):
        """Vassal tags appear when Balance naming is active and no higher stamp wins."""
        world = _make_world()
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1}
        ledger = build_diplomatic_ledger(world)
        saxony = next(n for n in ledger["nations"] if n["name"] == "Saxony")

        assert saxony["bloc_stamp"] == {
            "label": "Vassal of France",
            "kind": "vassal",
            "priority": 40,
        }


class TestArmyStrengthFog:
    """Tests for fog-filtered army strength display."""

    def test_unknown_visibility_shows_unknown(self):
        assert _format_army_strength(50000, UNKNOWN) == "Unknown"

    def test_stale_bands_negligible(self):
        assert _format_army_strength(5000, STALE) == "Negligible"

    def test_stale_bands_minor(self):
        assert _format_army_strength(15000, STALE) == "Minor Force"

    def test_stale_bands_considerable(self):
        assert _format_army_strength(45000, STALE) == "Considerable"

    def test_stale_bands_powerful(self):
        assert _format_army_strength(75000, STALE) == "Powerful"

    def test_stale_bands_dominant(self):
        assert _format_army_strength(120000, STALE) == "Dominant"

    def test_partial_rounded_to_5k(self):
        result = _format_army_strength(47000, PARTIAL)
        assert result == "~45,000 men"

    def test_partial_rounded_up(self):
        result = _format_army_strength(48000, PARTIAL)
        assert result == "~50,000 men"

    def test_full_exact_number(self):
        result = _format_army_strength(47123, FULL)
        assert result == "47,123 men"

    def test_nation_visibility_unknown_for_unseen(self):
        """Nation with no visible marshals should return UNKNOWN."""
        world = _make_world()
        # Set all region intel to UNKNOWN for Austria
        for region_name in world.regions:
            intel = world.get_region_intel(region_name)
            intel.visibility = UNKNOWN
        result = _get_nation_visibility("Austria", world)
        assert result == UNKNOWN

    def test_nation_visibility_full_when_present(self):
        """Nation with a marshal in a FULL visibility region should return FULL."""
        world = _make_world()
        # Find an Austrian marshal and set their region to FULL
        for m in world.marshals.values():
            if m.nation == "Austria" and m.strength > 0:
                intel = world.get_region_intel(m.location)
                intel.visibility = FULL
                break
        result = _get_nation_visibility("Austria", world)
        assert result == FULL

    def test_nation_visibility_stale_when_stale(self):
        """Nation with a marshal in a STALE visibility region should return STALE."""
        world = _make_world()
        # Set all Austrian marshal regions to STALE
        for region_name in world.regions:
            intel = world.get_region_intel(region_name)
            intel.visibility = UNKNOWN
        for m in world.marshals.values():
            if m.nation == "Austria" and m.strength > 0:
                intel = world.get_region_intel(m.location)
                intel.visibility = STALE
                break
        result = _get_nation_visibility("Austria", world)
        assert result == STALE

    def test_ledger_army_strength_fog_applied(self):
        """Verify ledger applies fog to army strength in nations tab."""
        world = _make_world()
        # Set all regions to UNKNOWN
        for region_name in world.regions:
            intel = world.get_region_intel(region_name)
            intel.visibility = UNKNOWN
        ledger = build_diplomatic_ledger(world)
        # Nations with all-UNKNOWN marshals should show "Unknown"
        for nation in ledger["nations"]:
            if nation["name"] in ("Austria", "Saxony"):
                # These nations likely have no visible marshals now
                assert nation["army_strength"] == "Unknown"


# ════════════════════════════════════════════════════════════════
# TAB 2: TREATIES
# ════════════════════════════════════════════════════════════════

class TestDiplomaticLedgerTreaties:
    """Tests for treaties tab."""

    def test_treaties_empty_by_default(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        assert isinstance(ledger["treaties"], list)
        # Default game has no active treaties
        assert len(ledger["treaties"]) == 0

    def test_treaties_with_active_treaty(self):
        world = _make_world()
        world.active_treaties = {
            "Austria|France": {
                "nations": ["Austria", "France"],
                "type": "non_aggression",
                "clauses": ["mutual_defense"],
                "duration": 10,
            }
        }
        ledger = build_diplomatic_ledger(world)
        assert len(ledger["treaties"]) == 1
        treaty = ledger["treaties"][0]
        assert treaty["nation_a"] == "Austria"
        assert treaty["nation_b"] == "France"
        assert treaty["treaty_type"] == "non_aggression"
        assert treaty["cancel_cost"] == 1

    def test_treaties_correct_keys(self):
        world = _make_world()
        world.active_treaties = {
            "Austria|France": {
                "nations": ["Austria", "France"],
                "type": "peace",
                "clauses": [],
                "duration": "permanent",
            }
        }
        ledger = build_diplomatic_ledger(world)
        treaty = ledger["treaties"][0]
        required_keys = {"nation_a", "nation_b", "treaty_type", "clauses", "duration", "cancel_cost"}
        assert required_keys.issubset(set(treaty.keys()))


# ════════════════════════════════════════════════════════════════
# TAB 3: THREAT & COALITION
# ════════════════════════════════════════════════════════════════

class TestDiplomaticLedgerThreatCoalition:
    """Tests for threat & coalition tab."""

    def test_threat_default_zero(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        boe = ledger["balance_of_europe"]
        assert boe["threat_level"] == 0
        assert boe["threat_tier"] == "LOW"

    def test_threat_tier_moderate(self):
        world = _make_world(threat_level=35)
        ledger = build_diplomatic_ledger(world)
        assert ledger["balance_of_europe"]["threat_tier"] == "MODERATE"

    def test_threat_tier_high(self):
        world = _make_world(threat_level=65)
        ledger = build_diplomatic_ledger(world)
        assert ledger["balance_of_europe"]["threat_tier"] == "HIGH"

    def test_threat_tier_critical(self):
        world = _make_world(threat_level=85)
        ledger = build_diplomatic_ledger(world)
        assert ledger["balance_of_europe"]["threat_tier"] == "CRITICAL"

    def test_no_active_coalition_default(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        assert ledger["balance_of_europe"]["active_coalition"] is None

    def test_active_coalition_present(self):
        world = _make_world()
        world.active_coalition = {
            "name": "The Austrian Coalition",
            "leader": "Austria",
            "members": ["Austria", "Britain"],
            "strategic_posture": "defensive",
        }
        ledger = build_diplomatic_ledger(world)
        ac = ledger["balance_of_europe"]["active_coalition"]
        assert ac is not None
        assert ac["name"] == "The Austrian Coalition"
        assert ac["leader"] == "Austria"
        assert len(ac["members"]) == 2

    def test_qualifying_nations_list(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        boe = ledger["balance_of_europe"]
        assert isinstance(boe["qualifying_nations"], list)

    def test_coalition_brewing_fields(self):
        world = _make_world()
        world.coalition_brewing = {"turns_remaining": 2, "qualifying_nations": ["Austria"]}
        ledger = build_diplomatic_ledger(world)
        boe = ledger["balance_of_europe"]
        assert boe["coalition_state"] == "BREWING"
        assert boe["brewing_turns_remaining"] == 2

    def test_correct_keys(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        assert "balance_of_europe" in ledger
        assert "threat_coalition" not in ledger
        boe = ledger["balance_of_europe"]
        required_keys = {
            "headline_case", "hegemon", "hegemon_share",
            "coalition_state", "threat_level", "threat_tier",
            "threat_sources_this_turn", "qualifying_nations",
            "brewing_turns_remaining", "active_coalition",
        }
        assert required_keys.issubset(set(boe.keys()))

    def test_merged_numeric_fields_are_int_wrapped(self):
        world = _make_world(threat_level=47)
        world.coalition_cooldown = 4
        ledger = build_diplomatic_ledger(world)
        boe = ledger["balance_of_europe"]

        assert isinstance(boe["coalition_cooldown"], int)
        assert isinstance(boe["cooldown_turns_remaining"], int)
        assert isinstance(boe["dissolution_threat_threshold"], int)
        assert isinstance(boe["dissolution_war_exhaustion_limit"], int)

        projection = boe["threat_projection"]
        for key in (
            "current",
            "after_next_war",
            "brewing_threshold",
            "instant_threshold",
            "wars_until_brewing",
            "wars_until_instant",
        ):
            assert isinstance(projection[key], int)

        coalition_world = _make_world()
        coalition_world.active_coalition = {
            "name": "The Austrian Coalition",
            "leader": "Austria",
            "members": ["Austria", "Britain"],
            "strategic_posture": "defensive",
        }
        coalition_boe = build_diplomatic_ledger(coalition_world)["balance_of_europe"]
        for member in coalition_boe["active_coalition"]["members"]:
            assert isinstance(member["war_exhaustion"], int)


# ════════════════════════════════════════════════════════════════
# TAB 4: TALLEYRAND
# ════════════════════════════════════════════════════════════════

class TestDiplomaticLedgerTalleyrand:
    """Tests for Talleyrand status tab."""

    def test_talleyrand_default_values(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        t = ledger["talleyrand"]
        assert isinstance(t["authority"], int)
        assert t["skill"] == 10
        assert isinstance(t["dp_remaining"], int)
        assert isinstance(t["dp_max"], int)

    def test_talleyrand_authority_label_default(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        assert isinstance(ledger["talleyrand"]["authority_label"], str)

    def test_talleyrand_no_active_mission(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        assert ledger["talleyrand"]["active_mission"] is None

    def test_talleyrand_with_active_mission(self):
        world = _make_world()
        world.active_diplomatic_mission = {
            "type": "IMPROVE_RELATIONS",
            "target": "Austria",
            "turns_active": 2,
            "paused": False,
        }
        ledger = build_diplomatic_ledger(world)
        mission = ledger["talleyrand"]["active_mission"]
        assert mission is not None
        assert mission["type"] == "IMPROVE_RELATIONS"
        assert mission["target"] == "Austria"

    def test_talleyrand_pending_envoy_count(self):
        world = _make_world()
        # Push mailbox-type proposals via dialogue_manager
        world.dialogue_manager.push({
            "type": "incoming_proposal", "turn_created": 1,
            "target_nation": "Prussia", "blocking": True,
        })
        world.dialogue_manager.push({
            "type": "incoming_proposal", "turn_created": 1,
            "target_nation": "Austria", "blocking": True,
        })
        ledger = build_diplomatic_ledger(world)
        assert ledger["talleyrand"]["pending_envoy_count"] == 2

    def test_talleyrand_correct_keys(self):
        world = _make_world()
        ledger = build_diplomatic_ledger(world)
        t = ledger["talleyrand"]
        required_keys = {
            "authority", "authority_label", "skill", "dp_remaining", "dp_max",
            "active_mission", "proposal_in_transit",
            "pending_envoy_count", "sabotage_warnings",
        }
        assert required_keys.issubset(set(t.keys()))


# ════════════════════════════════════════════════════════════════
# CHEAT COMMANDS
# ════════════════════════════════════════════════════════════════

class TestCheatCommands:
    """Tests for 11 cheat commands in executor."""

    def _run_cheat(self, world, cheat_type, cheat_args=None):
        executor = CommandExecutor()
        gs = _make_game_state(world)
        command = {
            "action": "cheat",
            "cheat_type": cheat_type,
            "cheat_args": cheat_args or [],
        }
        return executor._execute_cheat(command, gs)

    def test_set_threat(self):
        world = _make_world()
        result = self._run_cheat(world, "set_threat", ["75"])
        assert result["success"] is True
        assert world.threat_level == 75

    def test_set_threat_clamps(self):
        world = _make_world()
        self._run_cheat(world, "set_threat", ["150"])
        assert world.threat_level == 100

    def test_set_relation(self):
        world = _make_world()
        result = self._run_cheat(world, "set_relation", ["Austria", "50"])
        assert result["success"] is True
        key = world._make_diplo_key("France", "Austria")
        assert world.nation_relations[key] == 50

    def test_set_relation_clamps(self):
        world = _make_world()
        self._run_cheat(world, "set_relation", ["Austria", "-200"])
        key = world._make_diplo_key("France", "Austria")
        assert world.nation_relations[key] == -100

    def test_give_dp(self):
        world = _make_world()
        old_dp = world.diplomatic_points
        result = self._run_cheat(world, "give_dp", ["2"])
        assert result["success"] is True
        assert world.diplomatic_points == old_dp + 2

    def test_give_dp_bypasses_cap(self):
        """Cheat give_dp bypasses max_dp cap for testing convenience."""
        world = _make_world()
        self._run_cheat(world, "give_dp", ["100"])
        assert world.diplomatic_points > world.max_diplomatic_points

    def test_give_region_assigns_controller_for_smoke_testing(self):
        world = _make_world()
        world.threat_level = 10
        world.get_active_nations()  # populate cache so invalidation is observable

        result = self._run_cheat(world, "give_region", ["berlin", "france"])

        assert result["success"] is True
        assert world.regions["Berlin"].controller == "France"
        assert world.threat_level == 10
        assert world._active_nations_cache is None

    def test_give_region_rejects_unknown_region(self):
        world = _make_world()
        result = self._run_cheat(world, "give_region", ["Atlantis", "France"])
        assert result["success"] is False
        assert "Unknown region" in result["message"]

    def test_trigger_coalition(self):
        world = _make_world()
        # Ensure qualifying nations exist: need relation < -10 and not at war
        _set_relation(world, "France", "Austria", -20)
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Saxony", -20)
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        result = self._run_cheat(world, "trigger_coalition")
        assert result.get("success") is True or "Insufficient" in result.get("message", "")

    def test_trigger_commitment_paradox(self):
        world = _make_world()

        result = self._run_cheat(
            world,
            "trigger_commitment_paradox",
            ["Prussia", "Austria"],
        )

        assert result["success"] is True
        assert world.commitment_paradox_popup is not None
        assert world.commitment_paradox_popup["attacker"] == "Prussia"
        assert world.commitment_paradox_popup["defender"] == "Austria"
        assert world.pending_diplomatic_dialogue["type"] == "commitment_paradox"
        assert world.get_diplomatic_state("France", "Prussia") == "ALLIANCE"
        assert world.get_diplomatic_state("France", "Austria") == "ALLIANCE"
        assert world.get_diplomatic_state("Prussia", "Austria") == "WAR"

    def test_set_war_exhaustion(self):
        world = _make_world()
        result = self._run_cheat(world, "set_war_exhaustion", ["Britain", "50"])
        assert result["success"] is True
        assert world.war_exhaustion["Britain"] == 50

    def test_set_diplo_state(self):
        world = _make_world()
        result = self._run_cheat(world, "set_diplo_state", ["Austria", "alliance"])
        assert result["success"] is True
        key = world._make_diplo_key("France", "Austria")
        assert world.diplomatic_states[key] == "ALLIANCE"

    def test_create_vassal(self):
        world = _make_world()
        # Need OPEN_BORDERS+ for treaty vassal
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        result = self._run_cheat(world, "create_vassal", ["Saxony"])
        assert result["success"] is True
        assert "Saxony" in world.vassals

    def test_set_vassal_loyalty(self):
        world = _make_world()
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60, "autonomy": 1}
        result = self._run_cheat(world, "set_vassal_loyalty", ["Saxony", "25"])
        assert result["success"] is True
        assert world.vassals["Saxony"]["loyalty"] == 25

    def test_set_vassal_loyalty_nonexistent(self):
        world = _make_world()
        result = self._run_cheat(world, "set_vassal_loyalty", ["Saxony", "25"])
        assert result["success"] is False

    def test_queue_ai_proposal(self):
        world = _make_world()
        result = self._run_cheat(world, "queue_ai_proposal", ["Austria", "peace"])
        assert result["success"] is True
        # Proposal delivered via deliver_ai_proposal → dialogue_manager.push()
        assert world.dialogue_manager.get_mailbox_count() >= 1
        # Active dialogue should be the delivered proposal
        active = world.pending_diplomatic_dialogue
        assert active is not None
        assert active["type"] == "incoming_proposal"
        assert active["target_nation"] == "Austria"

    def test_seed_hard_reject_sets_warning_ready_history(self):
        from backend.game_logic.diplomacy import has_hard_reject_posture
        from backend.game_logic.diplomatic_dialogue import generate_dialogue

        world = _make_world()
        result = self._run_cheat(world, "seed_hard_reject", ["Austria"])

        assert result["success"] is True
        assert has_hard_reject_posture(world, "France", "Austria") is True
        record = world.betrayal_history["France|Austria"]
        assert len(record["strikes"]) == 3

        dialogue = generate_dialogue("proposal_confirm", {
            "target_nation": "Austria",
            "proposal_type": "alliance",
            "raw_text": "propose alliance with Austria",
            "has_diplomatic_keywords": True,
        }, world)
        warnings = dialogue.get("warnings") or []
        assert warnings
        assert warnings[0]["category"] == "hard_reject"

    def test_seed_hard_reject_accepts_custom_count(self):
        from backend.game_logic.diplomacy import has_hard_reject_posture

        world = _make_world()
        result = self._run_cheat(world, "seed_hard_reject", ["Austria", "2"])

        assert result["success"] is True
        assert has_hard_reject_posture(world, "France", "Austria") is False
        assert len(world.betrayal_history["France|Austria"]["strikes"]) == 2

    def test_cheat_guard_rejects_non_mock(self):
        """Cheat should be rejected when not in mock/debug mode."""
        world = _make_world()
        executor = CommandExecutor()
        gs = {"world": world, "debug_mode": False}
        # Temporarily set LLM_MODE to non-mock
        old_mode = os.environ.get("LLM_MODE")
        os.environ["LLM_MODE"] = "anthropic"
        try:
            command = {"action": "cheat", "cheat_type": "set_threat", "cheat_args": ["50"]}
            result = executor._execute_cheat(command, gs)
            assert result["success"] is False
            assert "mock/debug" in result["message"]
        finally:
            if old_mode:
                os.environ["LLM_MODE"] = old_mode
            else:
                os.environ["LLM_MODE"] = "mock"

    def test_unknown_cheat_type(self):
        world = _make_world()
        result = self._run_cheat(world, "nonexistent_cheat")
        assert result["success"] is False


# ════════════════════════════════════════════════════════════════
# DEBUG ENDPOINTS (using TestClient)
# ════════════════════════════════════════════════════════════════

class TestDebugEndpoints:
    """Tests for 8 debug endpoints."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        from fastapi.testclient import TestClient
        import backend.main as main_module
        main_module.DEBUG_MODE = True  # R134: Enable debug for tests
        main_module.game_state["debug_mode"] = True
        self.client = TestClient(main_module.app)

    def test_diplomatic_status(self):
        response = self.client.get("/debug/diplomatic_status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "diplomatic_states" in data
        assert "nation_relations" in data
        assert "diplomatic_points" in data

    def test_war_scores(self):
        response = self.client.get("/debug/war_scores")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "war_scores" in data

    def test_acceptance_preview(self):
        proposal = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Britain",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        response = self.client.post("/debug/acceptance_preview", json={"proposal": proposal})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "acceptance" in data
        assert "score" in data["acceptance"]
        assert "outcome" in data["acceptance"]

    def test_coalition_status(self):
        response = self.client.get("/debug/coalition_status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "threat_level" in data
        assert "threat_tier" in data
        assert "qualifying_nations" in data

    def test_threat_sources(self):
        response = self.client.get("/debug/threat_sources")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "threat_sources_this_turn" in data

    def test_proposal_cooldowns(self):
        response = self.client.get("/debug/proposal_cooldowns")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ai_proposal_cooldowns" in data
        assert "player_proposal_cooldowns" in data

    def test_vassal_loyalty_not_found(self):
        response = self.client.get("/debug/vassal_loyalty/Nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_proposal_queue(self):
        response = self.client.get("/debug/proposal_queue")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "mailbox_items" in data
        assert "mailbox_count" in data


# ════════════════════════════════════════════════════════════════
# PASS-THROUGH WIRING
# ════════════════════════════════════════════════════════════════

class TestPassThroughs:
    """Tests for pass-through popup fields in /command response."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        from fastapi.testclient import TestClient
        from backend.main import app, world
        self.client = TestClient(app)
        self.world = world

    def test_coalition_popup_key_present(self):
        """coalition_popup key must be present in /command response."""
        response = self.client.post("/command", json={"command": "help"})
        assert response.status_code == 200
        data = response.json()
        assert "coalition_popup" in data

    def test_diplomatic_sabotage_key_present(self):
        """diplomatic_sabotage key must be present in /command response."""
        response = self.client.post("/command", json={"command": "help"})
        data = response.json()
        assert "diplomatic_sabotage" in data

    def test_vassal_rebellion_imminent_key_present(self):
        """vassal_rebellion_imminent key must be present in /command response."""
        response = self.client.post("/command", json={"command": "help"})
        data = response.json()
        assert "vassal_rebellion_imminent" in data

    def test_coalition_popup_cleared_after_read(self):
        """Popup field should be cleared after being read (Golden Rule 4)."""
        self.world.coalition_popup = {"title": "TEST COALITION"}
        response = self.client.post("/command", json={"command": "help"})
        data = response.json()
        assert data["coalition_popup"] == {"title": "TEST COALITION"}
        # Field should be cleared now
        assert self.world.coalition_popup is None

    def test_diplomatic_sabotage_cleared_after_read(self):
        self.world.diplomatic_sabotage_popup = {"target": "Austria"}
        response = self.client.post("/command", json={"command": "help"})
        data = response.json()
        assert data["diplomatic_sabotage"] == {"target": "Austria"}
        assert self.world.diplomatic_sabotage_popup is None

    def test_vassal_rebellion_imminent_cleared_after_read(self):
        self.world.vassal_rebellion_imminent_popup = {"vassal": "Saxony"}
        response = self.client.post("/command", json={"command": "help"})
        data = response.json()
        assert data["vassal_rebellion_imminent"] == {"vassal": "Saxony"}
        assert self.world.vassal_rebellion_imminent_popup is None


# ════════════════════════════════════════════════════════════════
# TOP-BAR /test FIELDS
# ════════════════════════════════════════════════════════════════

class TestTopBarFields:
    """Tests for diplomatic top-bar fields in /test response."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        self.client = TestClient(app)

    def test_all_diplomatic_fields_present(self):
        response = self.client.get("/test")
        assert response.status_code == 200
        data = response.json()
        assert "diplomatic_points" in data
        assert "max_diplomatic_points" in data
        assert "talleyrand_state" in data
        assert "talleyrand_mission_summary" in data
        assert "threat_level" in data
        assert "coalition_brewing" in data
        assert "coalition_brewing_turns" in data
        assert "pending_envoy_count" in data

    def test_diplomatic_points_is_int(self):
        response = self.client.get("/test")
        data = response.json()
        assert isinstance(data["diplomatic_points"], int)
        assert isinstance(data["max_diplomatic_points"], int)
        assert isinstance(data["threat_level"], int)
        assert isinstance(data["pending_envoy_count"], int)

    def test_talleyrand_state_is_string(self):
        response = self.client.get("/test")
        data = response.json()
        assert isinstance(data["talleyrand_state"], str)
        assert data["talleyrand_state"] in ("Divine Right", "Commanding", "Respected", "Questionable", "Emperor in Name Only", "UNKNOWN")

    def test_talleyrand_mission_none_by_default(self):
        response = self.client.get("/test")
        data = response.json()
        assert data["talleyrand_mission_summary"] == "None"


# ════════════════════════════════════════════════════════════════
# DIPLOMATIC LEDGER ENDPOINT
# ════════════════════════════════════════════════════════════════

class TestDiplomaticLedgerEndpoint:
    """Tests for GET /diplomatic_ledger endpoint."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        self.client = TestClient(app)

    def test_endpoint_returns_success(self):
        response = self.client.get("/diplomatic_ledger")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_endpoint_has_all_4_tabs(self):
        response = self.client.get("/diplomatic_ledger")
        data = response.json()
        ledger = data["ledger"]
        assert "nations" in ledger
        assert "treaties" in ledger
        assert "balance_of_europe" in ledger
        assert "talleyrand" in ledger

    def test_endpoint_nations_is_list(self):
        response = self.client.get("/diplomatic_ledger")
        data = response.json()
        assert isinstance(data["ledger"]["nations"], list)
        assert len(data["ledger"]["nations"]) > 0


# ════════════════════════════════════════════════════════════════
# WAR SCORE COMPONENTS
# ════════════════════════════════════════════════════════════════

class TestWarScoreComponents:
    """Tests for calculate_war_score return_components extension."""

    def test_default_returns_int(self):
        from backend.game_logic.diplomacy import calculate_war_score
        world = _make_world()
        result = calculate_war_score("France", "Britain", world)
        assert isinstance(result, int)

    def test_return_components_returns_dict(self):
        from backend.game_logic.diplomacy import calculate_war_score
        world = _make_world()
        result = calculate_war_score("France", "Britain", world, return_components=True)
        assert isinstance(result, dict)
        assert "total" in result
        assert "territory" in result
        assert "battles" in result
        assert "decisive" in result
        assert "capital" in result

    def test_components_total_matches_default(self):
        from backend.game_logic.diplomacy import calculate_war_score
        world = _make_world()
        int_result = calculate_war_score("France", "Britain", world)
        dict_result = calculate_war_score("France", "Britain", world, return_components=True)
        assert int_result == dict_result["total"]
