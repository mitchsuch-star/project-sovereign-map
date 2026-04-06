"""
Tests for Bombardment Part 4: Strategic HOLD + Objections (Session 51)

Covers BOMBARDMENT_SPEC.md:
  §9 — Strategic HOLD Artillery Override
  §7.1 — Artillery Objection Triggers (5 new triggers)
  §9.6 — bombardment_target serialization
"""

from backend.models.marshal import (
    Marshal, StrategicOrder, StrategicCondition,
)
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.commands.objection_v2 import (
    evaluate_cautious, evaluate_aggressive, ConcernLevel,
)


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _make_world(**overrides):
    """Create a WorldState with default game setup."""
    world = WorldState()
    for k, v in overrides.items():
        setattr(world, k, v)
    return world


def _make_artillery(name="Drouot", location="Paris", strength=25000, nation="France", **kw):
    """Create an artillery marshal."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "cautious"),
        nation=nation, movement_range=1, tactical_skill=7,
        skills=kw.pop("skills", {"tactical": 8, "shock": 7, "defense": 6,
                                  "logistics": 7, "administration": 6, "command": 7}),
        artillery=True, spawn_location=location, **kw
    )


def _make_infantry(name="TestInf", location="Paris", strength=40000, nation="France", **kw):
    """Create an infantry marshal."""
    return Marshal(
        name=name, location=location, strength=strength,
        personality=kw.pop("personality", "cautious"),
        nation=nation, movement_range=1, tactical_skill=6,
        skills=kw.pop("skills", {"tactical": 6, "shock": 5, "defense": 6,
                                  "logistics": 5, "administration": 5, "command": 5}),
        spawn_location=location, **kw
    )


def _setup_hold_scenario(artillery_loc="Belgium", enemy_loc="Waterloo",
                         enemy_strength=40000, enemy_defense=0.15,
                         enemy_name="Wellington", enemy_nation="Britain"):
    """Set up a standard HOLD bombardment test scenario."""
    world = _make_world()
    # Clear default marshals for isolated testing
    world.marshals.clear()
    art = _make_artillery(location=artillery_loc)
    enemy = _make_infantry(
        name=enemy_name, location=enemy_loc,
        strength=enemy_strength, nation=enemy_nation,
    )
    enemy.defense_bonus = enemy_defense

    world.marshals["Drouot"] = art
    world.marshals[enemy_name] = enemy

    # Set up strategic HOLD order
    art.strategic_order = StrategicOrder(
        command_type="HOLD",
        target=artillery_loc,
        target_type="region",
        started_turn=1,
        original_command=f"Drouot, hold {artillery_loc}",
        issued_turn=1,
    )


    executor = CommandExecutor()
    strategic = StrategicOrderProcessor(executor)
    game_state = {"world": world}

    return world, art, enemy, strategic, game_state


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS: Strategic HOLD Auto-Bombardment
# ════════════════════════════════════════════════════════════════════════════════

class TestHoldBombardment:
    """Tests for _execute_hold_bombardment (BOMBARDMENT_SPEC §9)."""

    def test_artillery_hold_auto_bombards_adjacent_enemy(self):
        """Artillery on HOLD at position auto-bombards adjacent enemy."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2  # Not the issued turn

        result = strategic._execute_hold(art, world, game_state)

        assert result["action"] == "hold_bombardment"
        assert result["target"] == "Wellington"
        assert result["order_status"] == "continues"
        assert "bombard" in result["message"].lower() or "guns" in result["message"].lower()

    def test_hold_bombardment_increments_counter(self):
        """HOLD bombardment increments bombardments_this_turn."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2

        assert art.bombardments_this_turn == 0
        strategic._execute_hold(art, world, game_state)
        assert art.bombardments_this_turn >= 1

    def test_hold_bombardment_spent_when_at_limit(self):
        """HOLD returns 'spent' when artillery already at bombardment limit."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2
        art.bombardments_this_turn = 2  # Already at limit

        result = strategic._execute_hold(art, world, game_state)

        assert result["action"] == "hold_artillery_spent"
        assert result["order_status"] == "continues"
        assert "already fired" in result["message"].lower()

    def test_hold_bombardment_no_targets(self):
        """HOLD returns 'no targets' when no adjacent enemies exist."""
        world = _make_world()
        world.marshals.clear()
        art = _make_artillery(location="Paris")
        world.marshals["Drouot"] = art

        art.strategic_order = StrategicOrder(
            command_type="HOLD", target="Paris", target_type="region",
            started_turn=1, original_command="Drouot, hold Paris", issued_turn=1,
        )
    
        world.current_turn = 2

        executor = CommandExecutor()
        strategic = StrategicOrderProcessor(executor)
        game_state = {"world": world}

        result = strategic._execute_hold(art, world, game_state)

        assert result["action"] == "hold_artillery_ready"
        assert "no targets" in result["message"].lower()
        assert result["order_status"] == "continues"

    def test_hold_bombardment_breaks_on_enemy_contact(self):
        """HOLD breaks when enemy enters artillery's region."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2
        # Move enemy INTO artillery's region
        enemy.location = "Belgium"

        result = strategic._execute_hold(art, world, game_state)

        assert result["action"] == "hold_broken_contact"
        assert result["order_status"] == "cancelled"
        assert art.strategic_order is None  # Order cleared
        assert "enemy forces" in result["message"].lower()

    def test_hold_bombardment_skips_broken_targets(self):
        """HOLD skips broken/retreating targets in target selection."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2
        enemy.broken = True  # Target is broken

        result = strategic._execute_hold(art, world, game_state)

        # Should return no targets since the only adjacent enemy is broken
        assert result["action"] == "hold_artillery_ready"
        assert "no targets" in result["message"].lower()

    def test_hold_bombardment_skips_retreating_targets(self):
        """HOLD skips retreating targets."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2
        enemy.retreating = True

        result = strategic._execute_hold(art, world, game_state)

        assert result["action"] == "hold_artillery_ready"

    def test_hold_bombardment_cautious_prefers_fortified(self):
        """Cautious artillery on HOLD prefers most-fortified target."""
        world, art, _, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2

        # Add a second enemy with higher defense
        enemy2 = _make_infantry(
            name="Blucher", location="Waterloo",
            strength=30000, nation="Prussia",
        )
        enemy2.defense_bonus = 0.30  # More fortified than Wellington (0.15)
        world.marshals["Blucher"] = enemy2

        result = strategic._execute_hold(art, world, game_state)

        assert result["action"] == "hold_bombardment"
        assert result["target"] == "Blucher"  # Higher defense_bonus

    def test_hold_bombardment_stores_target_lock(self):
        """HOLD bombardment stores bombardment_target on the order."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2

        strategic._execute_hold(art, world, game_state)

        assert art.strategic_order.bombardment_target == "Wellington"

    def test_hold_bombardment_literal_uses_locked_target(self):
        """Literal artillery on HOLD fires at locked target if still available."""
        world = _make_world()
        world.marshals.clear()
        art = _make_artillery(location="Belgium", personality="literal")
        enemy1 = _make_infantry(name="Wellington", location="Waterloo", strength=40000, nation="Britain")
        enemy1.defense_bonus = 0.10
        enemy2 = _make_infantry(name="Blucher", location="Waterloo", strength=60000, nation="Prussia")
        enemy2.defense_bonus = 0.20  # Stronger and more fortified

        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy1
        world.marshals["Blucher"] = enemy2

        art.strategic_order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="Drouot, hold Belgium", issued_turn=1,
            bombardment_target="Wellington",  # Locked target from previous turn
        )
    
        world.current_turn = 2

        executor = CommandExecutor()
        strategic = StrategicOrderProcessor(executor)
        game_state = {"world": world}

        result = strategic._execute_hold(art, world, game_state)

        assert result["target"] == "Wellington"  # Keeps locked target

    def test_hold_bombardment_literal_fallback_when_target_gone(self):
        """Literal artillery falls back to default selection when locked target moves away."""
        world = _make_world()
        world.marshals.clear()
        art = _make_artillery(location="Belgium", personality="literal")
        # Only one enemy, and it's NOT the locked target
        enemy = _make_infantry(name="Blucher", location="Waterloo", strength=40000, nation="Prussia")
        world.marshals["Drouot"] = art
        world.marshals["Blucher"] = enemy

        art.strategic_order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="Drouot, hold Belgium", issued_turn=1,
            bombardment_target="Wellington",  # Wellington left the area
        )
    
        world.current_turn = 2

        executor = CommandExecutor()
        strategic = StrategicOrderProcessor(executor)
        game_state = {"world": world}

        result = strategic._execute_hold(art, world, game_state)

        # Falls through to Blucher since Wellington isn't adjacent
        assert result["target"] == "Blucher"

    def test_hold_manual_then_strategic_respects_limit(self):
        """Manual bombardment before strategic HOLD respects shared limit."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2
        art.bombardments_this_turn = 1  # One manual bombardment already

        result = strategic._execute_hold(art, world, game_state)

        # Should still fire (limit is 2, we've done 1)
        assert result["action"] == "hold_bombardment"

        # Now at 2
        art.bombardments_this_turn = 2
        result2 = strategic._execute_hold(art, world, game_state)
        assert result2["action"] == "hold_artillery_spent"

    def test_hold_bombardment_passes_through_results(self):
        """HOLD bombardment passes through bombardment_result and advisory."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2

        result = strategic._execute_hold(art, world, game_state)

        # The battle_details should contain bombardment info
        assert "battle_details" in result
        details = result["battle_details"]
        assert details.get("success") is True

    def test_non_artillery_hold_still_uses_personality(self):
        """Infantry on HOLD still uses personality behavior (not bombardment)."""
        world = _make_world()
        world.marshals.clear()
        inf = _make_infantry(name="Ney", location="Paris", personality="aggressive", nation="France")
        world.marshals["Ney"] = inf

        inf.strategic_order = StrategicOrder(
            command_type="HOLD", target="Paris", target_type="region",
            started_turn=1, original_command="Ney, hold Paris", issued_turn=1,
        )
    
        world.current_turn = 2

        executor = CommandExecutor()
        strategic = StrategicOrderProcessor(executor)
        game_state = {"world": world}

        result = strategic._execute_hold(inf, world, game_state)

        # Should NOT be bombardment action
        assert result["action"] != "hold_bombardment"
        assert result["action"] != "hold_artillery_ready"


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS: bombardment_target Serialization
# ════════════════════════════════════════════════════════════════════════════════

class TestBombardmentTargetSerialization:
    """Tests for bombardment_target field on StrategicOrder (§9.6)."""

    def test_bombardment_target_in_to_dict(self):
        """bombardment_target is included in to_dict output."""
        order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="hold Belgium",
            bombardment_target="Wellington",
        )
        d = order.to_dict()
        assert d["bombardment_target"] == "Wellington"

    def test_bombardment_target_from_dict(self):
        """bombardment_target is restored from from_dict."""
        data = {
            "command_type": "HOLD", "target": "Belgium", "target_type": "region",
            "started_turn": 1, "original_command": "hold Belgium",
            "bombardment_target": "Blucher",
        }
        order = StrategicOrder.from_dict(data)
        assert order.bombardment_target == "Blucher"

    def test_bombardment_target_defaults_none(self):
        """bombardment_target defaults to None for old saves."""
        data = {
            "command_type": "HOLD", "target": "Belgium", "target_type": "region",
            "started_turn": 1, "original_command": "hold Belgium",
        }
        order = StrategicOrder.from_dict(data)
        assert order.bombardment_target is None

    def test_bombardment_target_roundtrip(self):
        """bombardment_target survives to_dict -> from_dict roundtrip."""
        order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="hold Belgium",
            bombardment_target="Wellington",
        )
        d = order.to_dict()
        restored = StrategicOrder.from_dict(d)
        assert restored.bombardment_target == "Wellington"


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS: Artillery Objection Triggers (§7.1)
# ════════════════════════════════════════════════════════════════════════════════

class TestArtilleryObjectionTriggers:
    """Tests for the 5 new artillery objection triggers (§7.1)."""

    # --- Ordered into melee (STRONG) ---

    def test_cautious_artillery_strong_objection_on_melee(self):
        """Cautious artillery objects STRONG when ordered to attack in same region."""
        art = _make_artillery(location="Waterloo")
        enemy = _make_infantry(name="Wellington", location="Waterloo", nation="Britain")

        world = _make_world()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy

        game_state = {"world": world}
        order = {"action": "attack", "target": "Wellington"}

        concern = evaluate_cautious(art, "attack", order, game_state)
        assert concern == ConcernLevel.STRONG

    def test_cautious_artillery_no_melee_objection_when_ranged(self):
        """Cautious artillery does NOT object to bombardment (different region)."""
        art = _make_artillery(location="Belgium")
        enemy = _make_infantry(name="Wellington", location="Waterloo", nation="Britain")

        world = _make_world()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy

        game_state = {"world": world}
        order = {"action": "attack", "target": "Wellington"}

        concern = evaluate_cautious(art, "attack", order, game_state)
        assert concern == ConcernLevel.NONE  # Bombardment is what artillery wants

    # --- Reckless repositioning (MODERATE) ---

    # test_cautious_artillery_moderate_reckless_repositioning removed — bombardment_streak objection logic removed in PT-7
    # test_cautious_artillery_no_reckless_at_low_streak removed — same
    # test_cautious_artillery_no_reckless_when_target_cracked removed — same
    # test_cautious_artillery_moderate_cease_fire removed — same
    # test_cautious_artillery_no_cease_fire_when_no_streak removed — same

    def test_cautious_artillery_no_cease_fire_when_fort_nearly_gone(self):
        """No cease fire trigger when enemy defense_bonus <= 0.05."""
        art = _make_artillery(location="Belgium")

        enemy = _make_infantry(name="Wellington", location="Waterloo", nation="Britain")
        enemy.defense_bonus = 0.04  # Below threshold

        world = _make_world()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy

        game_state = {"world": world}
        order = {"action": "defend"}

        concern = evaluate_cautious(art, "defend", order, game_state)
        assert concern == ConcernLevel.NONE

    # --- Wasted fire (MILD) — Cautious ---

    def test_cautious_artillery_mild_wasted_fire(self):
        """Cautious artillery MILD when bombarding target with no forts and < 8k strength."""
        art = _make_artillery(location="Belgium")
        enemy = _make_infantry(name="Wellington", location="Waterloo", nation="Britain", strength=5000)
        enemy.defense_bonus = 0.0

        world = _make_world()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy

        game_state = {"world": world}
        order = {"action": "attack", "target": "Wellington"}

        concern = evaluate_cautious(art, "attack", order, game_state)
        assert concern == ConcernLevel.MILD

    def test_cautious_artillery_no_wasted_fire_when_strong(self):
        """No wasted fire when target still has significant strength."""
        art = _make_artillery(location="Belgium")
        enemy = _make_infantry(name="Wellington", location="Waterloo", nation="Britain", strength=20000)
        enemy.defense_bonus = 0.0

        world = _make_world()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy

        game_state = {"world": world}
        order = {"action": "attack", "target": "Wellington"}

        concern = evaluate_cautious(art, "attack", order, game_state)
        assert concern == ConcernLevel.NONE  # Target strong enough to warrant bombardment

    # --- Wasted fire (MILD) — Aggressive ---

    def test_aggressive_artillery_mild_wasted_fire(self):
        """Aggressive artillery MILD when bombarding broken weak target."""
        art = _make_artillery(name="AggrArt", personality="aggressive")
        enemy = _make_infantry(name="WeakTarget", location="Waterloo", nation="Britain", strength=5000)
        enemy.defense_bonus = 0.0

        world = _make_world()
        world.marshals["AggrArt"] = art
        world.marshals["WeakTarget"] = enemy

        game_state = {"world": world}
        order = {"action": "attack", "target": "WeakTarget"}

        concern = evaluate_aggressive(art, "attack", order, game_state)
        assert concern == ConcernLevel.MILD

    def test_aggressive_artillery_no_wasted_fire_when_fortified(self):
        """Aggressive artillery no wasted fire when target still has defenses."""
        art = _make_artillery(name="AggrArt", personality="aggressive")
        enemy = _make_infantry(name="FortTarget", location="Waterloo", nation="Britain", strength=5000)
        enemy.defense_bonus = 0.10  # Still fortified

        world = _make_world()
        world.marshals["AggrArt"] = art
        world.marshals["FortTarget"] = enemy

        game_state = {"world": world}
        order = {"action": "attack", "target": "FortTarget"}

        concern = evaluate_aggressive(art, "attack", order, game_state)
        assert concern == ConcernLevel.NONE

    # --- Last-shot advisory (MILD) ---

    def test_cautious_artillery_mild_last_shot(self):
        """Cautious artillery MILD on last bombardment when multiple targets exist."""
        art = _make_artillery(location="Belgium")
        art.bombardments_this_turn = 1  # Last shot

        enemy1 = _make_infantry(name="Wellington", location="Waterloo", nation="Britain", strength=40000)
        enemy2 = _make_infantry(name="Blucher", location="Waterloo", nation="Prussia", strength=30000)

        world = _make_world()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy1
        world.marshals["Blucher"] = enemy2

        game_state = {"world": world}
        order = {"action": "attack", "target": "Wellington"}

        concern = evaluate_cautious(art, "attack", order, game_state)
        assert concern == ConcernLevel.MILD

    def test_cautious_artillery_no_last_shot_when_fresh(self):
        """No last-shot advisory when no bombardments fired yet."""
        art = _make_artillery(location="Belgium")
        art.bombardments_this_turn = 0  # Fresh

        enemy1 = _make_infantry(name="Wellington", location="Waterloo", nation="Britain", strength=40000)
        enemy2 = _make_infantry(name="Blucher", location="Waterloo", nation="Prussia", strength=30000)

        world = _make_world()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy1
        world.marshals["Blucher"] = enemy2

        game_state = {"world": world}
        order = {"action": "attack", "target": "Wellington"}

        concern = evaluate_cautious(art, "attack", order, game_state)
        assert concern == ConcernLevel.NONE

    def test_cautious_artillery_no_last_shot_single_target(self):
        """No last-shot advisory when only one adjacent target."""
        art = _make_artillery(location="Belgium")
        art.bombardments_this_turn = 1  # Last shot

        enemy = _make_infantry(name="Wellington", location="Waterloo", nation="Britain", strength=40000)

        world = _make_world()
        world.marshals.clear()
        world.marshals["Drouot"] = art
        world.marshals["Wellington"] = enemy

        game_state = {"world": world}
        order = {"action": "attack", "target": "Wellington"}

        concern = evaluate_cautious(art, "attack", order, game_state)
        assert concern == ConcernLevel.NONE  # Only one target, no advisory needed

    # --- Non-artillery marshals unaffected ---

    def test_non_artillery_no_melee_objection(self):
        """Non-artillery cautious marshal uses standard attack objection, not melee trigger."""
        inf = _make_infantry(name="Davout", location="Waterloo", nation="France")
        enemy = _make_infantry(name="Wellington", location="Waterloo", nation="Britain", strength=40000)

        world = _make_world()
        world.marshals["Davout"] = inf
        world.marshals["Wellington"] = enemy

        game_state = {"world": world}
        order = {"action": "attack", "target": "Wellington"}

        concern = evaluate_cautious(inf, "attack", order, game_state)
        # Standard cautious attack evaluation based on odds ratio, NOT STRONG melee
        assert concern != ConcernLevel.STRONG  # Only artillery gets STRONG for melee


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS: Artillery Flavor Text
# ════════════════════════════════════════════════════════════════════════════════

class TestArtilleryFlavorText:
    """Tests for artillery flavor text in disobedience.py (§7.5)."""

    def test_cautious_artillery_flavor_keys_exist(self):
        """All 5 artillery flavor keys exist in the cautious personality dict."""
        from backend.commands.disobedience import OBJECTION_TEMPLATES

        cautious = OBJECTION_TEMPLATES.get('cautious', {})
        expected_keys = [
            'reckless_repositioning',
            'ordered_into_melee',
            'ordered_to_cease_fire',
            'wasted_fire',
            'last_shot_advisory',
        ]
        for key in expected_keys:
            assert key in cautious, f"Missing flavor text key: {key}"
            assert len(cautious[key]) >= 2, f"Need at least 2 variants for {key}"

    def test_flavor_text_has_name_placeholder(self):
        """All flavor text templates contain {name} placeholder."""
        from backend.commands.disobedience import OBJECTION_TEMPLATES

        cautious = OBJECTION_TEMPLATES.get('cautious', {})
        artillery_keys = [
            'reckless_repositioning', 'ordered_into_melee',
            'ordered_to_cease_fire', 'wasted_fire', 'last_shot_advisory',
        ]
        for key in artillery_keys:
            for template in cautious[key]:
                assert "{name}" in template, f"Missing {{name}} in {key}: {template[:50]}"


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS: Integration — Strategic HOLD bombardment streak
# ════════════════════════════════════════════════════════════════════════════════

class TestHoldBombardmentStreak:
    """Tests for bombardment streak accumulation during HOLD."""

    # test_hold_bombardment_increments_streak removed — bombardment_streak field removed in PT-7

    def test_hold_bombardment_damage_applied(self):
        """HOLD bombardment actually damages the target."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario(
            enemy_strength=40000
        )
        world.current_turn = 2
        initial_strength = enemy.strength

        strategic._execute_hold(art, world, game_state)

        assert enemy.strength < initial_strength

    def test_hold_bombardment_fort_degradation(self):
        """HOLD bombardment degrades target's defense_bonus."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario(
            enemy_defense=0.20
        )
        world.current_turn = 2

        strategic._execute_hold(art, world, game_state)

        assert enemy.defense_bonus < 0.20


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS: Edge Cases
# ════════════════════════════════════════════════════════════════════════════════

class TestHoldBombardmentEdgeCases:
    """Edge cases for HOLD bombardment."""

    def test_hold_still_moves_to_position_if_not_there(self):
        """Artillery HOLD that hasn't reached position yet still moves."""
        world = _make_world()
        world.marshals.clear()
        art = _make_artillery(location="Paris")
        world.marshals["Drouot"] = art

        art.strategic_order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="Drouot, hold Belgium", issued_turn=1,
        )
    
        world.current_turn = 2

        executor = CommandExecutor()
        strategic = StrategicOrderProcessor(executor)
        game_state = {"world": world}

        result = strategic._execute_hold(art, world, game_state)

        # Should be moving toward Belgium, not bombarding
        assert result["action"] in ("moving_to_position", "arriving")

    def test_hold_timed_expiry_for_artillery(self):
        """Artillery HOLD with max_turns condition still expires."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        art.strategic_order.condition = StrategicCondition(max_turns=2)
        art.strategic_order.issued_turn = 1
        world.current_turn = 3  # 2 turns elapsed

        result = strategic._execute_hold(art, world, game_state)

        assert result["order_status"] == "expired"
        assert art.strategic_order is None

    def test_hold_bombardment_zero_strength_target_excluded(self):
        """Target with 0 strength is not selected for bombardment."""
        world, art, enemy, strategic, game_state = _setup_hold_scenario()
        world.current_turn = 2
        enemy.strength = 0  # Dead

        result = strategic._execute_hold(art, world, game_state)

        assert result["action"] == "hold_artillery_ready"
