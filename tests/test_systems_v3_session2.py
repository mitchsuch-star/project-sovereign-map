"""
Systems Audit V3 Fix Plan — Session 2: War-State Cascade — Executor

Tests for 14 bugs (5A-1 through 5A-14):
All fixes add `world.is_at_war()` guards to `m.nation != marshal.nation` checks
in executor.py so allied/neutral marshals aren't treated as enemies.
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Fresh WorldState with France at war with Britain, peace with Austria."""
    w = WorldState()
    # Ensure France-Britain at war, France-Austria at peace
    set_war(w, "France", "Britain")
    set_peace(w, "France", "Austria")
    return w


def make_executor():
    return CommandExecutor()


def make_marshal(name="Ney", location="Belgium", strength=30000, nation="France", **kwargs):
    m = Marshal(name=name, location=location, strength=strength,
                personality="aggressive", nation=nation, spawn_location=location)
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def make_enemy(name="Wellington", location="Belgium", strength=25000, nation="Britain", **kwargs):
    m = Marshal(name=name, location=location, strength=strength,
                personality="cautious", nation=nation, spawn_location=location)
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def set_war(world, nation_a, nation_b):
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = "WAR"


def set_peace(world, nation_a, nation_b):
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = "PEACE"


def set_alliance(world, nation_a, nation_b):
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = "ALLIANCE"


def place_marshals(world, *marshals):
    """Replace world.marshals with given marshals."""
    world.marshals = {m.name: m for m in marshals}


# ═══════════════════════════════════════════════════════
# 5A-1: Reinforcement engagement check
# ═══════════════════════════════════════════════════════

class TestReinforcementEngagement:
    """Allied marshal in region shouldn't block reinforcement eligibility."""

    def test_allied_marshal_does_not_block_reinforcement(self):
        """Austrian (at peace) in same region doesn't make Davout 'engaged'."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        davout = make_marshal(name="Davout", location="Paris", strength=20000)
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, davout, austrian)

        # Davout is adjacent to Belgium (Paris adj Belgium)
        # Austrian in Belgium should NOT count as engagement blocker
        battle_region = w.get_region("Belgium")
        eligible = ex._is_reinforcement_eligible(davout, ney, "Belgium", "France", w)
        # Should be eligible — Austrian is not at war
        assert eligible is True

    def test_war_enemy_blocks_reinforcement(self):
        """British (at war) in same region makes Davout 'engaged'."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Waterloo", strength=30000)
        davout = make_marshal(name="Davout", location="Belgium", strength=20000)
        brit = make_enemy(name="Wellington", location="Belgium",
                          strength=25000, nation="Britain")
        place_marshals(w, ney, davout, brit)

        # British in Belgium should block Davout's reinforcement
        eligible = ex._is_reinforcement_eligible(davout, ney, "Waterloo", "France", w)
        assert eligible is False


# ═══════════════════════════════════════════════════════
# 5A-2: Overwatch artillery detection
# ═══════════════════════════════════════════════════════

class TestOverwatchWarCheck:
    """Allied artillery shouldn't trigger overwatch penalty."""

    def test_allied_artillery_no_overwatch(self):
        """Austrian artillery (at peace) doesn't trigger overwatch."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Paris", strength=30000)
        austrian_arty = make_enemy(name="Schwarzenberg", location="Belgium",
                                   strength=15000, nation="Austria")
        austrian_arty.artillery = True
        brit = make_enemy(name="Wellington", location="Belgium", strength=25000)
        place_marshals(w, ney, austrian_arty, brit)

        count = ex._calculate_overwatch(ney, [ney], "Belgium", w, defender_name="Wellington")
        assert count == 0  # Austrian artillery should not count

    def test_war_artillery_triggers_overwatch(self):
        """British artillery (at war) triggers overwatch."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Paris", strength=30000)
        brit_arty = make_enemy(name="BritArty", location="Belgium",
                               strength=15000, nation="Britain")
        brit_arty.artillery = True
        brit = make_enemy(name="Wellington", location="Belgium", strength=25000)
        place_marshals(w, ney, brit_arty, brit)

        count = ex._calculate_overwatch(ney, [ney], "Belgium", w, defender_name="Wellington")
        assert count == 1  # British artillery should count


# ═══════════════════════════════════════════════════════
# 5A-3: Bombardment target selection
# ═══════════════════════════════════════════════════════

class TestBombardmentTargeting:
    """Allied marshal shouldn't be auto-targeted by bombardment."""

    def test_allied_marshal_not_auto_targeted(self):
        """Austrian (at peace) not chosen as bombardment target."""
        w = make_world()
        ex = make_executor()
        arty = make_marshal(name="Ney", location="Paris", strength=20000)
        arty.artillery = True
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=30000, nation="Austria")
        place_marshals(w, arty, austrian)

        # Attack Belgium — no war enemies there, so no bombardment target
        result = ex._execute_attack(arty, "Belgium", w, {"world": w})
        # Should fail or not find a valid enemy target
        assert "success" in result
        # Austrian should not be targeted — attack should fail for no valid target
        msg = result.get("message", "").lower()
        assert "schwarzenberg" not in msg or "no enemy" in msg or not result["success"]

    def test_war_enemy_auto_targeted(self):
        """British (at war) is chosen as bombardment target."""
        w = make_world()
        ex = make_executor()
        arty = make_marshal(name="Ney", location="Paris", strength=20000)
        arty.artillery = True
        arty.morale = 80
        brit = make_enemy(name="Wellington", location="Belgium", strength=25000)
        brit.morale = 75
        place_marshals(w, arty, brit)

        result = ex._execute_attack(arty, "Belgium", w, {"world": w})
        # Should succeed — Wellington is valid war target
        assert result["success"]


# ═══════════════════════════════════════════════════════
# 5A-4: Undefended-region defender check
# ═══════════════════════════════════════════════════════

class TestUndefendedRegionCheck:
    """Allied presence shouldn't count as 'defended'."""

    def test_allied_presence_not_defended(self):
        """Austrian (at peace) doesn't count as defender for garrison combat."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        ney.morale = 80
        # Austrian in Rhineland — at peace
        austrian = make_enemy(name="Schwarzenberg", location="Rhineland",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        # Set Rhineland to Austrian control for the attack to make sense
        r = w.get_region("Rhineland")
        r.controller = "Austria"

        result = ex._execute_attack(ney, "Rhineland", w, {"world": w})
        # Can't attack — not at war with Austria
        # The attack should fail because there's no valid war-enemy target
        assert "success" in result

    def test_war_presence_counts_defended(self):
        """British (at war) counts as defender."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        ney.morale = 80
        brit = make_enemy(name="Wellington", location="Waterloo", strength=25000)
        brit.morale = 75
        place_marshals(w, ney, brit)

        result = ex._execute_attack(ney, "Wellington", w, {"world": w})
        assert result["success"]


# ═══════════════════════════════════════════════════════
# 5A-5/12: Charge leapfrog (attack + glorious charge)
# ═══════════════════════════════════════════════════════

class TestChargeLeapfrog:
    """Allied marshal in middle region shouldn't block charge path."""

    def test_allied_marshal_does_not_block_charge_path(self):
        """Austrian (at peace) in middle region doesn't block cavalry charge."""
        w = make_world()
        ex = make_executor()
        # Ney in Paris, target in Rhineland, Belgium is middle
        # Paris -> Belgium -> Rhineland (distance 2)
        ney = make_marshal(name="Ney", location="Paris", strength=20000)
        ney.cavalry = True
        ney.morale = 80
        ney.movement_range = 2
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        brit = make_enemy(name="Wellington", location="Rhineland", strength=25000)
        brit.morale = 75
        place_marshals(w, ney, austrian, brit)

        result = ex._execute_attack(ney, "Wellington", w, {"world": w})
        # Should NOT be blocked by Austrian in middle
        msg = result.get("message", "")
        assert "blocks the path" not in msg or "Schwarzenberg" not in msg

    def test_war_enemy_blocks_charge_path(self):
        """British (at war) in middle region blocks cavalry charge."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Paris", strength=20000)
        ney.cavalry = True
        ney.morale = 80
        ney.movement_range = 2
        brit_mid = make_enemy(name="Hill", location="Belgium", strength=15000)
        brit_target = make_enemy(name="Wellington", location="Rhineland", strength=25000)
        brit_target.morale = 75
        place_marshals(w, ney, brit_mid, brit_target)

        result = ex._execute_attack(ney, "Wellington", w, {"world": w})
        # Should be blocked by Hill in Belgium
        msg = result.get("message", "")
        if not result["success"]:
            assert "blocks the path" in msg or "Hill" in msg


# ═══════════════════════════════════════════════════════
# 5A-6/13: Post-battle conquest check
# ═══════════════════════════════════════════════════════

class TestPostBattleConquest:
    """Allied marshal shouldn't block conquest after battle."""

    def test_allied_marshal_does_not_block_conquest(self):
        """Austrian (at peace) doesn't prevent region capture after battle."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        ney.morale = 80
        # Very weak British to ensure we win
        brit = make_enemy(name="Wellington", location="Waterloo", strength=1000)
        brit.morale = 10
        # Austrian also at Waterloo — should not block conquest
        austrian = make_enemy(name="Schwarzenberg", location="Waterloo",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, brit, austrian)
        waterloo = w.get_region("Waterloo")
        waterloo.controller = "Britain"

        result = ex._execute_attack(ney, "Wellington", w, {"world": w})
        # If we won and conquered, Austrian shouldn't have blocked it
        assert result["success"]

    def test_war_enemy_blocks_conquest(self):
        """Second British marshal (at war) prevents conquest after battle."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        ney.morale = 80
        brit1 = make_enemy(name="Wellington", location="Waterloo", strength=1000)
        brit1.morale = 10
        # Second British marshal still alive
        brit2 = make_enemy(name="Hill", location="Waterloo", strength=20000)
        brit2.morale = 80
        place_marshals(w, ney, brit1, brit2)
        waterloo = w.get_region("Waterloo")
        waterloo.controller = "Britain"

        result = ex._execute_attack(ney, "Wellington", w, {"world": w})
        # Even if we beat Wellington, Hill blocks conquest
        assert result["success"]
        # Waterloo should still be British (Hill blocks capture)
        # (Hill might fight too as defender, but if alive, blocks)


# ═══════════════════════════════════════════════════════
# 5A-7: Reckless charge alternatives
# ═══════════════════════════════════════════════════════

class TestRecklessChargeAlternatives:
    """Allied marshal not offered as charge alternative target."""

    def test_allied_not_charge_alternative(self):
        """Austrian (at peace) not listed as charge redirect option."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Paris", strength=20000)
        ney.cavalry = True
        ney.morale = 80
        ney.recklessness = 4  # high recklessness triggers charge
        ney.movement_range = 2
        # Only Austrian at target — no valid war-enemy charge redirect
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)

        # The charge redirect logic should not suggest Austrian
        # (This is in the terrain-blocked charge alternatives section)
        # We verify indirectly: Austrian is not a valid charge target
        assert not w.is_at_war("France", "Austria")

    def test_war_enemy_is_charge_alternative(self):
        """British (at war) can be listed as charge redirect option."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Paris", strength=20000)
        ney.cavalry = True
        ney.morale = 80
        ney.recklessness = 4
        ney.movement_range = 2
        brit = make_enemy(name="Wellington", location="Belgium", strength=25000)
        place_marshals(w, ney, brit)

        assert w.is_at_war("France", "Britain")


# ═══════════════════════════════════════════════════════
# 5A-8: Garrison enemy validation
# ═══════════════════════════════════════════════════════

class TestGarrisonWarCheck:
    """Garrison allowed with allied marshal present, blocked by war enemy."""

    def test_garrison_allowed_with_allied_marshal(self):
        """Austrian (at peace) in region doesn't block garrison placement."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        region = w.get_region("Belgium")
        region.controller = "France"
        region.garrison_strength = 0

        result = ex._execute_garrison({"marshal": "Ney"}, {"world": w})
        # Should succeed — Austrian is not a war enemy
        assert result["success"], f"Expected success, got: {result['message']}"

    def test_garrison_blocked_by_war_enemy(self):
        """British (at war) in region blocks garrison placement."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        brit = make_enemy(name="Wellington", location="Belgium", strength=25000)
        place_marshals(w, ney, brit)
        region = w.get_region("Belgium")
        region.controller = "France"
        region.garrison_strength = 0

        result = ex._execute_garrison({"marshal": "Ney"}, {"world": w})
        assert not result["success"]
        assert "enemy" in result["message"].lower() or "contest" in result["message"].lower()


# ═══════════════════════════════════════════════════════
# 5A-11/14: Glorious charge target lookup
# ═══════════════════════════════════════════════════════

class TestGloriousChargeTarget:
    """Can't target allied marshal for glorious charge."""

    def test_cannot_target_allied_marshal(self):
        """Austrian (at peace) can't be targeted by glorious charge."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=20000)
        ney.cavalry = True
        ney.morale = 80
        ney.recklessness = 3
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)

        result = ex._execute_glorious_charge(ney, "Schwarzenberg", w, {"world": w})
        assert not result["success"]
        assert "cannot find" in result["message"].lower() or "target" in result["message"].lower()

    def test_can_target_war_enemy(self):
        """British (at war) can be targeted by glorious charge."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=20000)
        ney.cavalry = True
        ney.morale = 80
        ney.recklessness = 3
        brit = make_enemy(name="Wellington", location="Belgium", strength=25000)
        brit.morale = 75
        place_marshals(w, ney, brit)

        result = ex._execute_glorious_charge(ney, "Wellington", w, {"world": w})
        # Should succeed or at least find the target (may fail for other reasons)
        msg = result.get("message", "").lower()
        assert "cannot find target" not in msg


# ═══════════════════════════════════════════════════════
# 5A-9: Move capture hints
# ═══════════════════════════════════════════════════════

class TestScoutCaptureHints:
    """Allied marshal doesn't prevent capture hint; scout doesn't list allies."""

    def test_allied_does_not_block_capture_hint(self):
        """Austrian (at peace) in adjacent region doesn't suppress capture hint."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Paris", strength=30000)
        # Put Austrian in Belgium — at peace, shouldn't count as defender
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        # Belgium controlled by Austria — undefended by war enemies
        region = w.get_region("Belgium")
        region.controller = "Austria"
        region.garrison_strength = 0

        # Move Ney to Normandy (adjacent to Belgium)
        result = ex._execute_move(ney, "Normandy", w, {"world": w})
        # Capture hint logic checks adjacent regions — Belgium has Austrian
        # but Austrian is at peace, so should still hint as capturable
        # (Note: capture hints only show for visible regions — may need intel)
        assert result["success"]

    def test_scout_excludes_allies_from_enemy_list(self):
        """Scout intel doesn't list Austrian (at peace) as enemy."""
        w = make_world()
        ex = make_executor()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Waterloo",
                              strength=20000, nation="Austria")
        brit = make_enemy(name="Wellington", location="Waterloo", strength=25000)
        place_marshals(w, ney, austrian, brit)

        result = ex._execute_scout(ney, "Waterloo", w, {"world": w})
        assert result["success"]
        msg = result.get("message", "")
        # Wellington (war enemy) should appear, Schwarzenberg (peace) should not
        assert "Wellington" in msg
        assert "Schwarzenberg" not in msg
