"""
VS-3 — Land Grants to Vassals (docs/VASSAL_DEEPENING_SPEC.md §1),
landed July 16, 2026.

"Reward Bavaria for its service — cede it the province it bled for."
grant_region_to_vassal: controller flips (NO stability reset), worth-scaled
loyalty (never spiral-blunted), the lord forfeits the income and the vassal
tributes it, granted_regions provenance reclaims on a WAR-path rebellion,
1 DP / 3-turn per-vassal cooldown, GR5 lord-neutral.

Legacy-fixture geography used throughout: the vassal Saxony holds Dresden
(capital) + the Saxony region; Bohemia (Austrian, income 150) adjoins both.
"""

import pytest

from backend.models.world_state import WorldState
from backend.game_logic.vassal import (
    AUTONOMY_SATELLITE,
    GRANT_COOLDOWN,
    GRANT_DP_COST,
    GRANT_LOYALTY_BASE,
    GRANT_LOYALTY_CAP,
    TRIBUTE_RATES,
    check_vassal_rebellion,
    decrement_vassal_cooldowns,
    grant_loyalty_bonus,
    grant_region_to_vassal,
    list_grantable_regions,
    process_vassal_tribute,
    recovery_hint_for_grip,
)


def make_world():
    return WorldState()


def add_vassal(world, vassal="Saxony", lord="France", loyalty=60,
               autonomy=AUTONOMY_SATELLITE):
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": int(autonomy),
        "path": "treaty",
        "created_turn": 1,
        "tribute_rate": TRIBUTE_RATES[autonomy],
        "carved_from": None,
        "regions": None,
    }
    key = world._make_diplo_key(lord, vassal)
    world.diplomatic_states[key] = "VASSAL"
    world.nation_relations[key] = 0
    world.invalidate_active_nations_cache()
    return world.vassals[vassal]


def conquer(world, region_name, by="France"):
    world.regions[region_name].controller = by
    world.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════
# 1. The worth-scaled bonus formula
# ═══════════════════════════════════════════════════════

class TestGrantBonusFormula:
    def test_base_for_poor_province(self):
        assert grant_loyalty_bonus(0) == GRANT_LOYALTY_BASE
        assert grant_loyalty_bonus(199) == GRANT_LOYALTY_BASE

    def test_worth_scaling(self):
        assert grant_loyalty_bonus(400) == GRANT_LOYALTY_BASE + 2

    def test_cap(self):
        assert grant_loyalty_bonus(100000) == GRANT_LOYALTY_CAP


# ═══════════════════════════════════════════════════════
# 2. Eligibility gates
# ═══════════════════════════════════════════════════════

class TestEligibility:
    def test_not_a_vassal(self):
        world = make_world()
        result = grant_region_to_vassal(world, "Prussia", "Bohemia")
        assert not result["success"]
        assert "not a vassal" in result["message"]

    def test_not_your_vassal(self):
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Prussia")
        conquer(world, "Bohemia", by="France")
        result = grant_region_to_vassal(world, "Saxony", "Bohemia")  # player actor
        assert not result["success"]
        assert "not your vassal" in result["message"]

    def test_region_not_controlled(self):
        world = make_world()
        add_vassal(world)
        # Bohemia stays Austrian
        result = grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert not result["success"]
        assert "do not control" in result["message"]

    def test_homeland_excluded(self):
        """Only conquered land may be ceded — never the lord's homeland."""
        world = make_world()
        add_vassal(world)
        # Paris is France's homeland (and also a capital — homeland fires first)
        assert "Belgium" in world.nation_starting_regions.get("France", [])
        result = grant_region_to_vassal(world, "Saxony", "Belgium")
        assert not result["success"]
        assert "homeland" in result["message"]

    def test_capital_excluded(self):
        world = make_world()
        add_vassal(world)
        conquer(world, "Vienna", by="France")
        result = grant_region_to_vassal(world, "Saxony", "Vienna")
        assert not result["success"]
        assert "capital" in result["message"].lower()

    def test_estate_excluded(self):
        """A marshal's LIVE estate cannot be given away (ES-7 interlock)."""
        world = make_world()
        add_vassal(world)
        conquer(world, "Bohemia", by="France")
        marshal = next(m for m in world.marshals.values() if m.nation == "France")
        marshal.dotation_regions = ["Bohemia"]
        result = grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert not result["success"]
        assert "estate" in result["message"]

    def test_contiguity_required(self):
        """A province that does not adjoin the vassal's territory is refused."""
        world = make_world()
        add_vassal(world)
        saxon_holdings = set(world.get_nation_regions("Saxony"))
        # Find a conquerable region NOT adjoining Saxony, not homeland, not capital
        pick = None
        for name, region in world.regions.items():
            if name in world.nation_starting_regions.get("France", []):
                continue
            if getattr(region, 'is_capital', False) or region.region_type == "capital":
                continue
            if set(getattr(region, 'adjacent_regions', [])) & saxon_holdings:
                continue
            from backend.models.region import get_starting_controllers
            if get_starting_controllers().get(name) == "Saxony":
                continue
            pick = name
            break
        assert pick, "fixture should contain a non-adjacent grantable region"
        conquer(world, pick, by="France")
        result = grant_region_to_vassal(world, "Saxony", pick)
        assert not result["success"]
        assert "adjoin" in result["message"]

    def test_contiguity_waived_for_landless_vassal(self):
        """A carved/landless vassal must not be permanently ineligible."""
        world = make_world()
        add_vassal(world)
        # France takes everything Saxony held
        for name in list(world.get_nation_regions("Saxony")):
            conquer(world, name, by="France")
        # A far-away conquered province is now grantable (contiguity waived);
        # note Dresden itself is a capital, so use a plain region.
        conquer(world, "Bavaria", by="France")
        result = grant_region_to_vassal(world, "Saxony", "Bavaria")
        assert result["success"], result["message"]

    def test_cooldown_blocks(self):
        world = make_world()
        add_vassal(world)
        world.diplomatic_points = 5
        conquer(world, "Bohemia", by="France")
        conquer(world, "Bavaria", by="France")
        r1 = grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert r1["success"], r1["message"]
        r2 = grant_region_to_vassal(world, "Saxony", "Bavaria")
        assert not r2["success"]
        assert "settled" in r2["message"]

    def test_insufficient_dp(self):
        world = make_world()
        add_vassal(world)
        world.diplomatic_points = 0
        conquer(world, "Bohemia", by="France")
        result = grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert not result["success"]
        assert "diplomatic points" in result["message"].lower()


# ═══════════════════════════════════════════════════════
# 3. The grant itself
# ═══════════════════════════════════════════════════════

class TestGrantEffects:
    def _granted_world(self, loyalty=60):
        world = make_world()
        add_vassal(world, loyalty=loyalty)
        world.diplomatic_points = 3
        conquer(world, "Bohemia", by="France")
        return world

    def test_controller_flips_no_stability_reset(self):
        world = self._granted_world()
        region = world.regions["Bohemia"]
        region.stability = 80
        result = grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert result["success"], result["message"]
        assert region.controller == "Saxony"
        # A gift of a functioning province, NOT the settlement sacking idiom
        assert region.stability == 80

    def test_worth_scaled_loyalty_applied(self):
        world = self._granted_world(loyalty=60)
        income = world.regions["Bohemia"].income_value  # 150 → bonus 10
        expected = grant_loyalty_bonus(income)
        result = grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert result["success"]
        assert world.vassals["Saxony"]["loyalty"] == 60 + expected
        assert result["loyalty_gain"] == expected

    def test_dp_charged_and_cooldown_armed(self):
        world = self._granted_world()
        world.diplomatic_points = 2
        grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert world.diplomatic_points == 2 - GRANT_DP_COST
        assert world.vassals["Saxony"]["grant_cooldown"] == GRANT_COOLDOWN

    def test_cooldown_decrements_and_expires(self):
        world = self._granted_world()
        grant_region_to_vassal(world, "Saxony", "Bohemia")
        for _ in range(GRANT_COOLDOWN):
            decrement_vassal_cooldowns(world)
        assert "grant_cooldown" not in world.vassals["Saxony"]

    def test_provenance_recorded(self):
        world = self._granted_world()
        grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert world.vassals["Saxony"]["granted_regions"] == ["Bohemia"]

    def test_tribute_handoff_zero_new_wiring(self):
        """After the grant the vassal's tribute INCLUDES the ceded province —
        pure consequence of the controller flip (assert-only, no new code)."""
        world = self._granted_world()
        world.nation_gold["Saxony"] = 10000
        before = process_vassal_tribute(world).get("Saxony", {}).get("amount", 0)
        world.nation_gold["Saxony"] = 10000
        grant_region_to_vassal(world, "Saxony", "Bohemia")
        after = process_vassal_tribute(world).get("Saxony", {}).get("amount", 0)
        rate = world.vassals["Saxony"]["tribute_rate"]
        gained = int(world.regions["Bohemia"].get_effective_income() * rate)
        assert after >= before + gained - 1  # int truncation slack

    def test_unblunted_in_spiral_band(self):
        """Spec §2.4-Q3: the land grant is NEVER softened by the VS-R
        lever multiplier — full worth-scaled bonus even in a grip spiral."""
        world = self._granted_world(loyalty=40)
        world.authority_tracker.authority = 20
        paris = world.regions.get("Paris")
        if paris is not None:
            paris.controller = "Austria"
        from backend.models.authority import get_imperial_grip
        assert get_imperial_grip(world, "France") < 30  # in the spiral
        income = world.regions["Bohemia"].income_value
        result = grant_region_to_vassal(world, "Saxony", "Bohemia")
        assert result["success"]
        assert result["loyalty_gain"] == grant_loyalty_bonus(income)

    def test_gr5_enemy_lord_grants_via_same_function(self):
        """An AI lord grants through the SAME function, spending nation_dp.
        Austria conquers the Saxony region and hands it back to its new
        vassal — a homeland return (conquered land for Austria, waived
        contiguity for the vassal)."""
        world = make_world()
        add_vassal(world, vassal="Saxony", lord="Austria", loyalty=40)
        world.nation_dp = {"Austria": 2}
        for name in list(world.get_nation_regions("Saxony")):
            conquer(world, name, by="Austria")
        result = grant_region_to_vassal(world, "Saxony", "Saxony",
                                        actor="Austria")
        assert result["success"], result["message"]
        assert world.nation_dp["Austria"] == 1
        assert world.regions["Saxony"].controller == "Saxony"


# ═══════════════════════════════════════════════════════
# 4. Reclaim-on-rebellion
# ═══════════════════════════════════════════════════════

class TestReclaimOnRebellion:
    def _world_after_grant(self):
        world = make_world()
        add_vassal(world, loyalty=60)
        world.diplomatic_points = 3
        conquer(world, "Bohemia", by="France")
        grant_region_to_vassal(world, "Saxony", "Bohemia")
        return world

    def test_war_rebellion_reclaims_granted_province(self):
        world = self._world_after_grant()
        world.vassals["Saxony"]["loyalty"] = 0
        events = check_vassal_rebellion(world)
        types = [e["type"] for e in events]
        assert "vassal_rebellion" in types
        assert "vassal_grant_reclaimed" in types
        assert world.regions["Bohemia"].controller == "France"

    def test_armistice_break_keeps_the_land(self):
        """An armistice-respected break KEEPS the gift — flipping provinces
        back during a respected armistice would itself be a violation."""
        world = self._world_after_grant()
        world.vassals["Saxony"]["loyalty"] = 0
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "ARMISTICE"
        events = check_vassal_rebellion(world)
        types = [e["type"] for e in events]
        assert "vassal_rebellion_armistice" in types
        assert "vassal_grant_reclaimed" not in types
        assert world.regions["Bohemia"].controller == "Saxony"

    def test_reclaim_skips_regions_the_vassal_lost(self):
        """Only provinces STILL held by the rebel flip back."""
        world = self._world_after_grant()
        world.regions["Bohemia"].controller = "Austria"  # lost meanwhile
        world.vassals["Saxony"]["loyalty"] = 0
        events = check_vassal_rebellion(world)
        types = [e["type"] for e in events]
        assert "vassal_grant_reclaimed" not in types
        assert world.regions["Bohemia"].controller == "Austria"


# ═══════════════════════════════════════════════════════
# 5. Serialization (nested vassal-row keys ride the wholesale copy)
# ═══════════════════════════════════════════════════════

class TestSerialization:
    def test_round_trip_preserves_grant_state(self):
        world = make_world()
        add_vassal(world)
        world.diplomatic_points = 3
        conquer(world, "Bohemia", by="France")
        grant_region_to_vassal(world, "Saxony", "Bohemia")

        data = world.to_dict()
        restored = WorldState.from_dict(data)

        row = restored.vassals["Saxony"]
        assert row["granted_regions"] == ["Bohemia"]
        assert row["grant_cooldown"] == GRANT_COOLDOWN


# ═══════════════════════════════════════════════════════
# 6. Surfaces — executor, wizard option, eligible list, hint copy
# ═══════════════════════════════════════════════════════

class TestSurfaces:
    def _executor(self, world):
        from backend.commands.executor import CommandExecutor
        return CommandExecutor(), {"world": world, "debug_mode": True}

    def test_executor_structured_region_field(self):
        world = make_world()
        add_vassal(world)
        world.diplomatic_points = 3
        conquer(world, "Bohemia", by="France")
        executor, game_state = self._executor(world)
        result = executor._vassal._execute_grant_region_to_vassal(
            {"action": "grant_region_to_vassal", "target": "Saxony",
             "region": "Bohemia"},
            game_state,
        )
        assert result["success"], result["message"]
        assert world.regions["Bohemia"].controller == "Saxony"

    def test_executor_extracts_region_from_raw_text(self):
        world = make_world()
        add_vassal(world)
        world.diplomatic_points = 3
        conquer(world, "Bohemia", by="France")
        executor, game_state = self._executor(world)
        result = executor._vassal._execute_grant_region_to_vassal(
            {"action": "grant_region_to_vassal", "target": "Saxony",
             "raw_command": "cede bohemia to saxony"},
            game_state,
        )
        assert result["success"], result["message"]

    def test_executor_lists_eligibles_when_no_region(self):
        world = make_world()
        add_vassal(world)
        world.diplomatic_points = 3
        conquer(world, "Bohemia", by="France")
        executor, game_state = self._executor(world)
        result = executor._vassal._execute_grant_region_to_vassal(
            {"action": "grant_region_to_vassal", "target": "Saxony"},
            game_state,
        )
        assert not result["success"]
        assert "Bohemia" in result["message"]
        assert "loyalty +" in result["message"]

    def test_wizard_option_carries_eligible_regions(self):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        world = make_world()
        add_vassal(world)
        world.diplomatic_points = 3
        conquer(world, "Bohemia", by="France")
        actions = get_available_diplomatic_actions(world, "Saxony")
        grant = next(a for a in actions if a["action"] == "grant_region_to_vassal")
        assert grant["available"]
        regions = [e["region"] for e in grant["eligible_regions"]]
        assert "Bohemia" in regions
        entry = next(e for e in grant["eligible_regions"] if e["region"] == "Bohemia")
        assert entry["loyalty_gain"] == grant_loyalty_bonus(
            world.regions["Bohemia"].income_value)
        assert entry["tribute_pct"] == 75

    def test_wizard_option_disabled_without_eligible_province(self):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        world = make_world()
        add_vassal(world)
        world.diplomatic_points = 3
        actions = get_available_diplomatic_actions(world, "Saxony")
        grant = next(a for a in actions if a["action"] == "grant_region_to_vassal")
        assert not grant["available"]
        assert "No eligible province" in grant["disabled_reason"]

    def test_list_grantable_sorted_richest_first(self):
        world = make_world()
        add_vassal(world)
        conquer(world, "Bohemia", by="France")
        # Make a second eligible region adjacent to Saxon holdings
        saxon = set(world.get_nation_regions("Saxony"))
        second = None
        for name, region in world.regions.items():
            if name == "Bohemia" or region.controller == "France":
                continue
            if name in world.nation_starting_regions.get("France", []):
                continue
            if getattr(region, 'is_capital', False) or region.region_type == "capital":
                continue
            if set(getattr(region, 'adjacent_regions', [])) & saxon:
                second = name
                break
        if second:
            conquer(world, second, by="France")
            world.regions[second].income_value = 5000
            out = list_grantable_regions(world, "Saxony")
            assert out[0]["region"] == second  # richest first

    def test_recovery_hints_name_the_grant(self):
        assert "cede" in recovery_hint_for_grip(80).lower()
        assert "province" in recovery_hint_for_grip(10).lower()
