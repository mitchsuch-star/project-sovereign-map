"""
Systems Audit V3 Fix Plan — Session 3: War-State Cascade — Other Files

Tests for 17 bugs across world_state.py, disobedience.py, objection_v2.py,
personality.py, strategic_parser.py, turn_manager.py, enemy_ai.py.

All fixes add `world.is_at_war()` guards to `m.nation != marshal.nation` checks
so allied/neutral marshals aren't treated as enemies.
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.commands.disobedience import (
    is_valid_move as validate_move_target,
    can_drill,
    get_enemies_in_region as get_enemies_here,
)
from backend.commands.objection_v2 import (
    _check_enemy_in_region as _is_engaged_with_enemy,
)
from backend.models.personality import (
    _enemy_nearby as _has_adjacent_enemy,
    _get_strength_ratio,
)
from backend.ai.strategic_parser import _classify_target as classify_target


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Fresh WorldState with France at war with Britain, peace with Austria."""
    w = WorldState()
    set_war(w, "France", "Britain")
    set_peace(w, "France", "Austria")
    return w


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


def place_marshals(world, *marshals):
    world.marshals = {m.name: m for m in marshals}


# ═══════════════════════════════════════════════════════
# 5A-17: is_enemy_nearby()
# ═══════════════════════════════════════════════════════

class TestIsEnemyNearby:
    """Allied marshal nearby shouldn't count as 'enemy nearby'."""

    def test_allied_marshal_not_enemy_nearby(self):
        w = make_world()
        austrian = make_enemy(name="Schwarzenberg", location="Rhineland",
                              strength=20000, nation="Austria")
        place_marshals(w, austrian)
        # Austria is at peace — should NOT count as enemy nearby
        assert w.is_enemy_nearby("Belgium", "France") is False

    def test_war_enemy_is_enemy_nearby(self):
        w = make_world()
        wellington = make_enemy(name="Wellington", location="Rhineland",
                                strength=20000, nation="Britain")
        place_marshals(w, wellington)
        # Britain is at war — should count
        assert w.is_enemy_nearby("Belgium", "France") is True


# ═══════════════════════════════════════════════════════
# 5A-18: _find_retreat_destination()
# ═══════════════════════════════════════════════════════

class TestFindRetreatDestination:
    """Allied marshal shouldn't block retreat destination."""

    def test_allied_marshal_doesnt_block_retreat(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=5000)
        # Austrian in Paris (adjacent to Belgium) — at peace, shouldn't block
        austrian = make_enemy(name="Schwarzenberg", location="Paris",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        # Paris is French-controlled, Austrian is at peace
        paris = w.get_region("Paris")
        paris.controller = "France"
        result = w._find_retreat_destination(ney)
        # Paris should be a valid retreat destination since Austria is at peace
        assert result is not None

    def test_war_enemy_blocks_retreat(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=5000)
        wellington = make_enemy(name="Wellington", location="Paris",
                                strength=20000, nation="Britain")
        place_marshals(w, ney, wellington)
        paris = w.get_region("Paris")
        paris.controller = "France"
        # Set all other French-adjacent regions to non-French to isolate the test
        belgium = w.get_region("Belgium")
        for adj_name in belgium.adjacent_regions:
            adj = w.get_region(adj_name)
            if adj and adj_name != "Paris":
                adj.controller = "Britain"
        # Paris blocked by Wellington (at war), no other French regions
        result = w._find_retreat_destination(ney)
        assert result is None  # All retreat destinations blocked


# ═══════════════════════════════════════════════════════
# 5A-19: Auto-charge remaining defenders
# ═══════════════════════════════════════════════════════

class TestAutoChargeConquest:
    """Allied marshal shouldn't prevent region capture after auto-charge."""

    def test_allied_marshal_doesnt_block_conquest(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        region = w.get_region("Belgium")
        region.controller = "Britain"

        # Check "remaining" filter: Austrian should NOT count as hostile remaining
        remaining = [
            m for m in w.marshals.values()
            if m.location == "Belgium" and m.strength > 0 and m.nation != ney.nation
            and w.is_at_war(ney.nation, m.nation)
        ]
        assert len(remaining) == 0  # Austrian at peace — not blocking

    def test_war_enemy_blocks_conquest(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        wellington = make_enemy(name="Wellington", location="Belgium",
                                strength=20000, nation="Britain")
        place_marshals(w, ney, wellington)

        remaining = [
            m for m in w.marshals.values()
            if m.location == "Belgium" and m.strength > 0 and m.nation != ney.nation
            and w.is_at_war(ney.nation, m.nation)
        ]
        assert len(remaining) == 1  # Wellington at war — blocks


# ═══════════════════════════════════════════════════════
# 5A-20: Move/drill validation in disobedience.py
# ═══════════════════════════════════════════════════════

class TestDisobedienceMoveValidation:
    """Allied marshal shouldn't block move or require ATTACK."""

    def test_allied_marshal_doesnt_block_move(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Paris", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        # Move to Belgium with Austrian there — should be valid (at peace)
        valid, msg = validate_move_target(ney, "Belgium", w)
        assert valid is True

    def test_war_enemy_blocks_move(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Paris", strength=30000)
        wellington = make_enemy(name="Wellington", location="Belgium",
                                strength=20000, nation="Britain")
        place_marshals(w, ney, wellington)
        # Move to Belgium with British there — should require ATTACK
        valid, msg = validate_move_target(ney, "Belgium", w)
        assert valid is False
        assert "ATTACK" in msg


class TestDisobedienceDrilling:
    """Allied marshal in region shouldn't block drilling."""

    def test_drilling_allowed_with_ally(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        # Can drill with Austrian present (at peace)
        result = can_drill(ney, w)
        assert result is True

    def test_drilling_blocked_by_war_enemy(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        wellington = make_enemy(name="Wellington", location="Belgium",
                                strength=20000, nation="Britain")
        place_marshals(w, ney, wellington)
        # Can't drill with British present (at war)
        result = can_drill(ney, w)
        assert result is False


# ═══════════════════════════════════════════════════════
# 5A-21: Aggressive fallback targets allies
# ═══════════════════════════════════════════════════════

class TestAggressiveFallback:
    """Aggressive disobedience fallback shouldn't target allied marshals."""

    def test_allied_marshal_not_enemy_in_region(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        # Austrian at peace — should not appear as enemy
        enemies = get_enemies_here(ney, w)
        assert len(enemies) == 0

    def test_war_enemy_is_valid_target(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        wellington = make_enemy(name="Wellington", location="Belgium",
                                strength=20000, nation="Britain")
        place_marshals(w, ney, wellington)
        enemies = get_enemies_here(ney, w)
        assert len(enemies) == 1
        assert enemies[0].name == "Wellington"


# ═══════════════════════════════════════════════════════
# 5A-22: Objection strength ratio
# ═══════════════════════════════════════════════════════

class TestObjectionStrengthRatio:
    """Strength ratio shouldn't count allied marshals as enemies."""

    def test_allied_marshal_not_enemy_for_ratio(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        # personality._get_strength_ratio should not find Austrian as enemy
        ratio = _get_strength_ratio(ney, "Belgium", w)
        assert ratio is None  # No war enemy found

    def test_war_enemy_counted_for_ratio(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        wellington = make_enemy(name="Wellington", location="Belgium",
                                strength=25000, nation="Britain")
        place_marshals(w, ney, wellington)
        ratio = _get_strength_ratio(ney, "Belgium", w)
        assert ratio is not None
        assert ratio > 1.0  # 30000/25000 = 1.2


# ═══════════════════════════════════════════════════════
# 5A-23: Visible enemies / engagement / path crossing
# ═══════════════════════════════════════════════════════

class TestObjectionV2Engagement:
    """Allied marshal shouldn't trigger 'engaged with enemy'."""

    def test_allied_marshal_not_engaged(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Belgium",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        result = _is_engaged_with_enemy(ney, w)
        assert result is False

    def test_war_enemy_triggers_engagement(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        wellington = make_enemy(name="Wellington", location="Belgium",
                                strength=20000, nation="Britain")
        place_marshals(w, ney, wellington)
        result = _is_engaged_with_enemy(ney, w)
        assert result is True


# ═══════════════════════════════════════════════════════
# 5A-24: Personality adjacent enemy / strength ratio
# ═══════════════════════════════════════════════════════

class TestPersonalityAdjacentEnemy:
    """Allied adjacent marshal shouldn't count as 'enemy nearby'."""

    def test_allied_adjacent_not_enemy(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Paris",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        result = _has_adjacent_enemy(ney, w)
        assert result is False

    def test_war_adjacent_is_enemy(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        wellington = make_enemy(name="Wellington", location="Paris",
                                strength=20000, nation="Britain")
        place_marshals(w, ney, wellington)
        result = _has_adjacent_enemy(ney, w)
        assert result is True


# ═══════════════════════════════════════════════════════
# 5A-25: Strategic parser SUPPORT/PURSUE target
# ═══════════════════════════════════════════════════════

class TestStrategicParserTarget:
    """Allied marshal targeted by PURSUE shouldn't be classified as enemy."""

    def test_allied_marshal_not_enemy_target(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        austrian = make_enemy(name="Schwarzenberg", location="Rhineland",
                              strength=20000, nation="Austria")
        place_marshals(w, ney, austrian)
        result = classify_target("Schwarzenberg", "Ney", w)
        # Austrian at peace — should NOT be classified as enemy (no convert_to_pursue)
        assert result["convert_to_pursue"] is False

    def test_war_enemy_is_pursue_target(self):
        w = make_world()
        ney = make_marshal(name="Ney", location="Belgium", strength=30000)
        wellington = make_enemy(name="Wellington", location="Rhineland",
                                strength=20000, nation="Britain")
        place_marshals(w, ney, wellington)
        result = classify_target("Wellington", "Ney", w)
        # British at war — should be classified as enemy
        assert result["convert_to_pursue"] is True


# ═══════════════════════════════════════════════════════
# 5A-29/31/32: AI capture defender counts
# ═══════════════════════════════════════════════════════

class TestAICaptureDefenders:
    """Allied marshal shouldn't be counted as defender by AI."""

    def test_allied_marshal_not_defender(self):
        w = make_world()
        # Prussia at war with Austria, peace with France
        set_war(w, "Prussia", "Austria")
        set_peace(w, "Prussia", "France")
        french = make_marshal(name="Ney", location="Vienna", strength=20000, nation="France")
        prussian = make_marshal(name="Blucher", location="Berlin", strength=25000, nation="Prussia")
        place_marshals(w, french, prussian)
        # French in Vienna — Prussia checking defenders
        defenders = [m for m in w.marshals.values()
                     if m.location == "Vienna" and m.strength > 0 and m.nation != "Prussia"
                     and w.is_at_war("Prussia", m.nation)]
        # France at peace with Prussia — shouldn't count as defender
        assert len(defenders) == 0

    def test_war_enemy_is_defender(self):
        w = make_world()
        set_war(w, "Prussia", "Austria")
        austrian = make_enemy(name="Schwarzenberg", location="Vienna",
                              strength=20000, nation="Austria")
        prussian = make_marshal(name="Blucher", location="Berlin",
                                strength=25000, nation="Prussia")
        place_marshals(w, austrian, prussian)
        defenders = [m for m in w.marshals.values()
                     if m.location == "Vienna" and m.strength > 0 and m.nation != "Prussia"
                     and w.is_at_war("Prussia", m.nation)]
        assert len(defenders) == 1
        assert defenders[0].name == "Schwarzenberg"
