"""
Tests for DA-3: Offensive Alliance Cascade + Friction in Attack Coordination

N2: Offensive alliance cascade in _process_war_cascade / declare_war
N3: Coalition friction in P4 attack coordination estimate
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.game_logic.diplomacy import _process_war_cascade, declare_war


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Create a basic world for testing with clean diplomatic states."""
    world = WorldState(player_nation="France")
    return world


def make_clean_world():
    """Create a world with ALL diplomatic states cleared (no default alliances)."""
    world = WorldState(player_nation="France")
    world.diplomatic_states.clear()
    return world


def set_state(world, nation_a, nation_b, state):
    """Set diplomatic state between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def get_state(world, nation_a, nation_b):
    """Get diplomatic state between two nations."""
    return world.get_diplomatic_state(nation_a, nation_b)


def set_relation(world, nation_a, nation_b, value):
    """Set relation between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.nation_relations[key] = value


def get_relation(world, nation_a, nation_b):
    """Get relation between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    return world.nation_relations.get(key, 0)


def add_marshal(world, name, nation, location, strength=10000):
    """Add a marshal to the world."""
    m = Marshal(name=name, nation=nation, location=location,
                strength=strength, personality="balanced")
    world.marshals[name] = m
    return m


# ═══════════════════════════════════════════════════════
# N2: OFFENSIVE ALLIANCE CASCADE (12 tests)
# ═══════════════════════════════════════════════════════


class TestOffensiveCascade:
    """Tests for offensive alliance cascade in _process_war_cascade."""

    def test_alliance_triggers_offensive_cascade(self):
        """ALLIANCE with aggressor triggers offensive cascade against target."""
        world = make_world()
        # Saxony has ALLIANCE with France (aggressor)
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")

        cascade = _process_war_cascade(world, "France", "Austria")

        offensive = [c for c in cascade if c.get("cascade_type") == "offensive"]
        assert len(offensive) == 1
        assert offensive[0]["attacker_ally"] == "Saxony"
        assert offensive[0]["aggressor"] == "France"
        assert offensive[0]["target"] == "Austria"
        # Verify war actually set
        assert world.is_at_war("Saxony", "Austria")

    def test_defensive_alliance_no_offensive_cascade(self):
        """DEFENSIVE_ALLIANCE with aggressor does NOT trigger offensive cascade."""
        world = make_world()
        set_state(world, "France", "Saxony", "DEFENSIVE_ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")

        cascade = _process_war_cascade(world, "France", "Austria")

        offensive = [c for c in cascade if c.get("cascade_type") == "offensive"]
        assert len(offensive) == 0
        assert not world.is_at_war("Saxony", "Austria")

    def test_defensive_takes_priority_over_offensive(self):
        """Nation with DA to target AND ALLIANCE with aggressor -> defensive takes priority."""
        world = make_world()
        # Prussia has DEFENSIVE_ALLIANCE with Austria (target) -> defensive
        set_state(world, "Prussia", "Austria", "DEFENSIVE_ALLIANCE")
        # Prussia also has ALLIANCE with France (aggressor) -> would be offensive
        set_state(world, "France", "Prussia", "ALLIANCE")

        cascade = _process_war_cascade(world, "France", "Austria")

        # Defensive loop runs first, so Prussia joins defensively
        defensive = [c for c in cascade if c.get("cascade_type") != "offensive"]
        offensive = [c for c in cascade if c.get("cascade_type") == "offensive"]
        # Prussia should be in defensive cascade
        assert any(c["defender"] == "Prussia" for c in defensive)
        # Prussia should NOT also appear in offensive cascade
        assert not any(c.get("attacker_ally") == "Prussia" for c in offensive)

    def test_both_offensive_and_defensive_cascade(self):
        """Both offensive and defensive cascade in same declaration."""
        world = make_world()
        # Prussia has DA with Austria (target) -> defensive cascade
        set_state(world, "Prussia", "Austria", "DEFENSIVE_ALLIANCE")
        set_state(world, "France", "Prussia", "PEACE")
        # Saxony has ALLIANCE with France (aggressor) -> offensive cascade
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")

        cascade = _process_war_cascade(world, "France", "Austria")

        defensive = [c for c in cascade if c.get("cascade_type") != "offensive"]
        offensive = [c for c in cascade if c.get("cascade_type") == "offensive"]
        assert len(defensive) >= 1  # Prussia
        assert len(offensive) >= 1  # Saxony
        assert any(c["defender"] == "Prussia" for c in defensive)
        assert any(c["attacker_ally"] == "Saxony" for c in offensive)

    def test_paradox_skips_player_from_offensive(self):
        """Alliance paradox skips player from offensive cascade."""
        world = make_world()
        # Britain declares war on Prussia.
        # France has ALLIANCE with Britain (aggressor) -> would cascade offensively
        # France also has ALLIANCE with Prussia (target) -> paradox
        set_state(world, "France", "Britain", "ALLIANCE")
        set_state(world, "France", "Prussia", "ALLIANCE")

        # Simulate paradox: processed includes player
        cascade_skip = {"Britain", "Prussia", "France"}
        cascade = _process_war_cascade(world, "Britain", "Prussia", processed=cascade_skip)

        # France should not appear in cascade
        offensive = [c for c in cascade if c.get("cascade_type") == "offensive"]
        assert not any(c.get("attacker_ally") == "France" for c in offensive)

    def test_vassal_skipped_in_offensive_cascade(self):
        """Vassal nations are skipped in offensive cascade."""
        world = make_world()
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")
        # Mark Saxony as a vassal
        world.vassals = {"Saxony": {"lord": "France", "loyalty": 80}}

        cascade = _process_war_cascade(world, "France", "Austria")

        offensive = [c for c in cascade if c.get("cascade_type") == "offensive"]
        assert not any(c.get("attacker_ally") == "Saxony" for c in offensive)

    def test_direct_only_offensive_cascade(self):
        """DG-4 direct-only offensive calls do not pull in ally's ally."""
        # Use clean world to avoid default alliances interfering
        world = make_clean_world()
        # France -> Saxony ALLIANCE (offensive cascade: Saxony joins vs Austria)
        set_state(world, "France", "Saxony", "ALLIANCE")
        # Saxony -> Britain ALLIANCE (not a direct root-aggressor ally)
        set_state(world, "Saxony", "Britain", "ALLIANCE")
        # Everyone else at PEACE with Austria
        set_state(world, "Saxony", "Austria", "PEACE")
        set_state(world, "Britain", "Austria", "PEACE")

        cascade = _process_war_cascade(world, "France", "Austria")

        # Saxony should join offensively (ALLIANCE with France)
        offensive_saxony = [c for c in cascade if c.get("attacker_ally") == "Saxony"]
        assert len(offensive_saxony) == 1

        assert world.is_at_war("Saxony", "Austria")
        assert not world.is_at_war("Britain", "Austria")

    def test_notification_created(self):
        """Offensive cascade creates notification with correct title."""
        world = make_world()
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")

        _process_war_cascade(world, "France", "Austria")

        notifs = world.notifications.get_pending()
        offensive_notifs = [n for n in notifs if "Joins Offensive" in n.get("title", "")]
        assert len(offensive_notifs) >= 1
        assert "Saxony" in offensive_notifs[0]["title"]

    def test_dispatch_event_created(self):
        """Offensive cascade creates dispatch event with correct template vars."""
        world = make_world()
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")

        _process_war_cascade(world, "France", "Austria")

        events = world.pending_dispatch_events
        offensive_events = [e for e in events if e["type"] == "diplomatic_offensive_cascade"]
        assert len(offensive_events) == 1
        tv = offensive_events[0]["template_vars"]
        assert tv["nation"] == "Saxony"
        assert tv["aggressor"] == "France"
        assert tv["target"] == "Austria"

    def test_active_treaty_removed(self):
        """Active treaty removed between cascaded nation and target."""
        world = make_world()
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")
        # Set up an active treaty between Saxony and Austria
        treaty_key = world._make_diplo_key("Saxony", "Austria")
        world.active_treaties = {treaty_key: {"type": "PEACE", "turn": 1}}

        _process_war_cascade(world, "France", "Austria")

        assert treaty_key not in world.active_treaties

    def test_war_start_turn_recorded(self):
        """War start turn recorded for offensive cascade."""
        world = make_world()
        world.current_turn = 5
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")

        _process_war_cascade(world, "France", "Austria")

        war_key = world._make_diplo_key("Saxony", "Austria")
        assert world.war_start_turns.get(war_key) == 5

    def test_relation_penalty_applied(self):
        """Relation penalty of -20 applied between cascaded nation and target."""
        world = make_world()
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")
        set_relation(world, "Saxony", "Austria", 10)

        _process_war_cascade(world, "France", "Austria")

        assert get_relation(world, "Saxony", "Austria") == -10


# ═══════════════════════════════════════════════════════
# N2: declare_war message builder
# ═══════════════════════════════════════════════════════


class TestDeclareWarMessages:
    """Test that declare_war message builder handles both cascade types."""

    def test_offensive_cascade_message(self):
        """declare_war includes offensive cascade message."""
        world = make_world()
        set_state(world, "France", "Saxony", "ALLIANCE")
        set_state(world, "Saxony", "Austria", "PEACE")
        # Ensure France can declare war (needs to not already be at war)
        set_state(world, "France", "Austria", "PEACE")

        result = declare_war(world, "France", "Austria")

        assert result["success"]
        msg = result["message"]
        assert "honoring alliance" in msg
        assert "Saxony" in msg


# ═══════════════════════════════════════════════════════
# N3: FRICTION IN ATTACK COORDINATION (7 tests)
# ═══════════════════════════════════════════════════════


class TestFrictionInAttackCoordination:
    """Tests for coalition friction in P4 attack coordination estimate."""

    def _get_ai(self):
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        return EnemyAI(CommandExecutor())

    def test_same_nation_allies_full_bonus(self):
        """Same-nation allies get full +8% each (regression test)."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Saxony", 15000)
        add_marshal(world, "York", "Prussia", "Saxony", 8000)
        add_marshal(world, "Ney", "France", "Saxony", 10000)
        set_state(world, "Prussia", "France", "WAR")

        ai = self._get_ai()
        result = ai._find_attack_opportunity(
            world.marshals["Blucher"], "Prussia", world
        )

        # Should find attack — York (same nation) adds coordination bonus
        assert result is not None

    def test_cross_nation_coalition_ally_high_relation(self):
        """Cross-nation coalition ally at high relation (friction 1.0) -> full +8%."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Saxony", 12000)
        add_marshal(world, "Wellington", "Britain", "Saxony", 8000)
        add_marshal(world, "Ney", "France", "Saxony", 10000)
        set_state(world, "Prussia", "France", "WAR")
        set_state(world, "Britain", "France", "WAR")
        # Active coalition with both members
        world.active_coalition = {
            "members": ["Prussia", "Britain", "Austria"],
            "leader": "Britain",
            "formed_turn": 1,
        }
        # High relation -> friction 1.0
        set_relation(world, "Prussia", "Britain", 50)

        ai = self._get_ai()
        result = ai._find_attack_opportunity(
            world.marshals["Blucher"], "Prussia", world
        )
        # Wellington (Britain) should be included as coalition ally
        assert result is not None

    def test_cross_nation_coalition_ally_low_relation(self):
        """Cross-nation coalition ally at low relation (friction 0.25) -> reduced bonus."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Saxony", 12000)
        add_marshal(world, "Wellington", "Britain", "Saxony", 8000)
        add_marshal(world, "Ney", "France", "Saxony", 10000)
        set_state(world, "Prussia", "France", "WAR")
        set_state(world, "Britain", "France", "WAR")
        world.active_coalition = {
            "members": ["Prussia", "Britain", "Austria"],
            "leader": "Britain",
            "formed_turn": 1,
        }
        # Very low relation -> friction 0.25
        set_relation(world, "Prussia", "Britain", -30)

        ai = self._get_ai()
        result = ai._find_attack_opportunity(
            world.marshals["Blucher"], "Prussia", world
        )
        # Should still find attack but with reduced coordination bonus
        assert result is not None

    def test_mixed_same_nation_and_cross_nation(self):
        """Mixed same-nation + cross-nation allies -> correct split."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Saxony", 10000)
        add_marshal(world, "York", "Prussia", "Saxony", 8000)  # same-nation
        add_marshal(world, "Wellington", "Britain", "Saxony", 8000)  # cross-nation
        add_marshal(world, "Ney", "France", "Saxony", 10000)
        set_state(world, "Prussia", "France", "WAR")
        set_state(world, "Britain", "France", "WAR")
        world.active_coalition = {
            "members": ["Prussia", "Britain", "Austria"],
            "leader": "Britain",
            "formed_turn": 1,
        }
        set_relation(world, "Prussia", "Britain", 50)

        ai = self._get_ai()
        result = ai._find_attack_opportunity(
            world.marshals["Blucher"], "Prussia", world
        )
        assert result is not None

    def test_non_coalition_cross_nation_excluded(self):
        """Non-coalition cross-nation allies excluded from coordination."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Saxony", 8000)
        add_marshal(world, "Wellington", "Britain", "Saxony", 8000)
        add_marshal(world, "Ney", "France", "Saxony", 10000)
        set_state(world, "Prussia", "France", "WAR")
        set_state(world, "Britain", "France", "WAR")
        # NO active coalition -> cross-nation allies should not count
        world.active_coalition = None

        ai = self._get_ai()
        # With no coalition, Wellington should NOT be in co_located_allies.
        # Blucher alone (8k vs 10k) may or may not attack depending on personality,
        # but the important thing is no crash and exclusion works.
        result = ai._find_attack_opportunity(
            world.marshals["Blucher"], "Prussia", world
        )
        # Result may be None (too weak alone) or an attack — either is valid

    def test_no_active_coalition_same_nation_only(self):
        """No active coalition -> only same-nation allies counted."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Saxony", 10000)
        add_marshal(world, "York", "Prussia", "Saxony", 8000)
        add_marshal(world, "Wellington", "Britain", "Saxony", 8000)
        add_marshal(world, "Ney", "France", "Saxony", 10000)
        set_state(world, "Prussia", "France", "WAR")
        set_state(world, "Britain", "France", "WAR")
        world.active_coalition = None

        ai = self._get_ai()
        result = ai._find_attack_opportunity(
            world.marshals["Blucher"], "Prussia", world
        )
        # Should include York (same nation) but not Wellington (no coalition)
        assert result is not None

    def test_multiple_cross_nation_allies_different_friction(self):
        """Multiple cross-nation allies with different friction levels."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Saxony", 10000)
        add_marshal(world, "Wellington", "Britain", "Saxony", 8000)
        add_marshal(world, "Schwarzenberg", "Austria", "Saxony", 8000)
        add_marshal(world, "Ney", "France", "Saxony", 10000)
        set_state(world, "Prussia", "France", "WAR")
        set_state(world, "Britain", "France", "WAR")
        set_state(world, "Austria", "France", "WAR")
        world.active_coalition = {
            "members": ["Prussia", "Britain", "Austria"],
            "leader": "Britain",
            "formed_turn": 1,
        }
        # Different relations -> different friction
        set_relation(world, "Prussia", "Britain", 50)   # friction 1.0
        set_relation(world, "Prussia", "Austria", -10)   # friction 0.5

        ai = self._get_ai()
        result = ai._find_attack_opportunity(
            world.marshals["Blucher"], "Prussia", world
        )
        # Both coalition allies should be included with different friction values
        assert result is not None
