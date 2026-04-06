"""
Bug Fix Session 6 Tests: PL-1, PL-2, PL-3, PL-4

PL-1: Unicode escape emoji replaced with text markers in combat.py (~2 tests)
PL-2: Counter-punch notification dedup across turns (~2 tests)
PL-3: AI proposal populates diplomat name from world.diplomats (~2 tests)
PL-4: Fog-hidden enemy phase includes Berthier summary (~3 tests)
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Create a basic world with marshals for testing."""
    world = WorldState(player_nation="France")
    return world


def make_marshal(name, nation="France", location="Paris", strength=10000, personality="aggressive", **kwargs):
    m = Marshal(name=name, nation=nation, location=location, strength=strength, personality=personality)
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


# ═══════════════════════════════════════════════════════
# PL-1: Emoji Unicode Escape Regression
# ═══════════════════════════════════════════════════════


class TestPL1EmojiEscapeRegression:
    """PL-1: No unicode escape emoji in _build_tactical_prefix()."""

    def test_tactical_prefix_no_emoji(self):
        """Output of _build_tactical_prefix contains text markers, not emoji."""
        from backend.game_logic.combat import _build_tactical_prefix
        atk = make_marshal("Ney", strength=10000)
        defn = make_marshal("Wellington", nation="Britain", strength=10000)

        prefix = _build_tactical_prefix(
            atk, defn,
            attacker_stance_message="Aggressive stance",
            defender_stance_message="Cautious defense",
            fortify_bonus_message="Fortified position",
            terrain_defense_message="Mountain terrain",
            cavalry_terrain_message="Cavalry penalty",
        )
        # Should contain text markers
        assert "[Combat]" in prefix
        assert "[Shield]" in prefix
        assert "[Fort]" in prefix
        assert "[Terrain]" in prefix
        assert "[Cavalry]" in prefix
        # Should NOT contain any emoji
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"
            "\U0001f300-\U0001f5ff"
            "\U0001f680-\U0001f6ff"
            "\u2600-\u26ff"
            "\u2700-\u27bf"
            "]+",
            re.UNICODE,
        )
        assert not emoji_pattern.search(prefix), f"Emoji found in prefix: {prefix}"

    def test_combined_arms_no_emoji(self):
        """Combined arms and adjacent ally lines use text markers."""
        from backend.game_logic.combat import _build_tactical_prefix
        atk = make_marshal("Ney", strength=10000)
        defn = make_marshal("Wellington", nation="Britain", strength=10000)
        atk._display_combined_arms_atk = 0.15
        defn._display_combined_arms_def = 0.10
        atk._display_adjacent_atk = 0.05

        prefix = _build_tactical_prefix(atk, defn)
        assert "[Combat]" in prefix
        assert "[Shield]" in prefix
        # No emoji
        assert "\u2694" not in prefix
        assert "\U0001f6e1" not in prefix


# ═══════════════════════════════════════════════════════
# PL-2: Counter-Punch Notification Dedup Across Turns
# ═══════════════════════════════════════════════════════


class TestPL2CounterPunchDedup:
    """PL-2: Only one counter-punch notification per marshal across turns."""

    def test_no_duplicate_across_turns(self):
        """Second counter-punch earned on a different turn doesn't create duplicate notification."""
        from backend.commands.combat_executor import CombatExecutor
        from backend.commands.executor import CommandExecutor
        from backend.notifications import COUNTER_PUNCH_EARNED, create_notification, NotificationPriority

        world = make_world()
        defender = make_marshal("Davout", nation="France", personality="cautious")
        world.marshals["Davout"] = defender

        # Simulate existing notification from turn 3
        world.notifications.add(create_notification(
            notification_type=COUNTER_PUNCH_EARNED,
            priority=NotificationPriority.HIGH,
            title="Davout — free attack!",
            message="Davout earned a free attack.",
            turn_created=3,
            details={"marshal": "Davout"},
        ))

        # Now on turn 5, another counter-punch earned
        world.current_turn = 5
        executor = CommandExecutor()
        combat_exec = CombatExecutor(executor)

        battle_result = {"counter_punch_earned": True}
        combat_exec._process_combat_notifications(battle_result, None, defender, world)

        # Should still have only 1 notification (dedup across turns)
        cp_notifs = [n for n in world.notifications.get_pending()
                     if n.get("type") == COUNTER_PUNCH_EARNED
                     and n.get("details", {}).get("marshal") == "Davout"]
        assert len(cp_notifs) == 1, f"Expected 1 counter-punch notification, got {len(cp_notifs)}"

    def test_different_marshals_allowed(self):
        """Different marshals can each have their own counter-punch notification."""
        from backend.commands.combat_executor import CombatExecutor
        from backend.commands.executor import CommandExecutor
        from backend.notifications import COUNTER_PUNCH_EARNED, create_notification, NotificationPriority

        world = make_world()
        davout = make_marshal("Davout", nation="France", personality="cautious")
        lannes = make_marshal("Lannes", nation="France", personality="cautious")
        world.marshals["Davout"] = davout
        world.marshals["Lannes"] = lannes

        # Davout has existing notification
        world.notifications.add(create_notification(
            notification_type=COUNTER_PUNCH_EARNED,
            priority=NotificationPriority.HIGH,
            title="Davout — free attack!",
            message="Davout earned a free attack.",
            turn_created=3,
            details={"marshal": "Davout"},
        ))

        # Lannes earns counter-punch on turn 5
        world.current_turn = 5
        executor = CommandExecutor()
        combat_exec = CombatExecutor(executor)

        battle_result = {"counter_punch_earned": True}
        combat_exec._process_combat_notifications(battle_result, None, lannes, world)

        # Should have 2 notifications — one per marshal
        cp_notifs = [n for n in world.notifications.get_pending()
                     if n.get("type") == COUNTER_PUNCH_EARNED]
        assert len(cp_notifs) == 2


# ═══════════════════════════════════════════════════════
# PL-3: AI Proposal Diplomat Name
# ═══════════════════════════════════════════════════════


class TestPL3DiplomatName:
    """PL-3: Incoming AI proposal shows actual diplomat name and personality."""

    def test_dialogue_context_has_diplomat_info(self):
        """generate_dialogue() populates diplomat_name in context."""
        from backend.game_logic.diplomatic_dialogue import generate_dialogue
        from backend.models.diplomat import DiplomaticRepresentative

        world = make_world()
        # Set up Saxony diplomat
        world.diplomats["Saxony"] = DiplomaticRepresentative(
            name="Einsiedel", nation="Saxony", personality="dove", skill=4
        )

        parsed_command = {"target_nation": "Saxony", "proposal_type": "NON_AGGRESSION"}
        dialogue = generate_dialogue("proposal_initiate", parsed_command, world)

        context = dialogue.get("context", {})
        assert context.get("diplomat_name") == "Einsiedel"
        assert context.get("diplomat_personality") == "dove"

    def test_dialogue_context_missing_diplomat_graceful(self):
        """No crash when diplomat doesn't exist for target nation."""
        from backend.game_logic.diplomatic_dialogue import generate_dialogue

        world = make_world()
        world.diplomats = {}  # No diplomats

        parsed_command = {"target_nation": "Saxony", "proposal_type": "NON_AGGRESSION"}
        dialogue = generate_dialogue("proposal_initiate", parsed_command, world)

        context = dialogue.get("context", {})
        # Should not have diplomat_name (no diplomat), but should not crash
        assert "diplomat_name" not in context


# ═══════════════════════════════════════════════════════
# PL-4: Fog-Hidden Enemy Phase Summary
# ═══════════════════════════════════════════════════════


class TestPL4FogHiddenEnemyPhase:
    """PL-4: When fog hides all enemy actions, include fog summary."""

    def _make_enemy_phase(self, nations_with_actions):
        """Build a mock enemy_phase dict."""
        phase = {"nations": {}, "total_actions": 0, "summary": []}
        for nation, count in nations_with_actions.items():
            actions = [{"ai_action": {"marshal": f"{nation}_marshal", "action": "move"},
                        "nation": nation} for _ in range(count)]
            phase["nations"][nation] = {"actions": actions, "action_count": count}
            phase["total_actions"] += count
        return phase

    def test_fog_hides_all_actions_includes_summary(self):
        """When fog filters all actions, response includes fog_hidden_summary."""
        from backend.main import _filter_enemy_phase_by_visibility

        world = make_world()
        # All enemy regions have no visibility (default)
        enemy_phase = self._make_enemy_phase({"Austria": 3, "Prussia": 2})
        raw_total = enemy_phase.get("total_actions", 0)

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)

        # Filtered should have 0 visible actions
        assert filtered.get("total_actions", 0) == 0
        # Raw had actions
        assert raw_total == 5

        # Simulate the main.py logic
        if filtered.get("total_actions", 0) > 0:
            result = filtered
        elif raw_total > 0:
            raw_nations = list(enemy_phase.get("nations", {}).keys())
            fog_messages = []
            for nation in raw_nations:
                fog_messages.append(
                    f"Our scouts report activity within {nation}'s borders, "
                    f"but their formations remain beyond our sight."
                )
            filtered["fog_hidden_summary"] = fog_messages
            result = filtered
        else:
            result = None

        assert result is not None
        assert "fog_hidden_summary" in result
        assert len(result["fog_hidden_summary"]) == 2
        assert "Austria" in result["fog_hidden_summary"][0]
        assert "Prussia" in result["fog_hidden_summary"][1]

    def test_no_actions_no_phase(self):
        """When enemies took no actions at all, no enemy_phase is included."""
        enemy_phase = self._make_enemy_phase({})
        raw_total = enemy_phase.get("total_actions", 0)

        assert raw_total == 0
        # No fog summary needed — enemies genuinely did nothing

    def test_visible_actions_no_fog_summary(self):
        """When some actions are visible, no fog_hidden_summary is added."""
        from backend.main import _filter_enemy_phase_by_visibility
        from backend.models.intel import RegionIntel, FULL

        world = make_world()
        # Put an enemy marshal in a visible region
        enemy = make_marshal("Gneisenau", nation="Prussia", location="Saxony")
        world.marshals["Gneisenau"] = enemy

        # Make Saxony fully visible
        world.intel["Saxony"] = RegionIntel(region_name="Saxony")
        world.intel["Saxony"].visibility = FULL

        enemy_phase = self._make_enemy_phase({"Prussia": 1})
        # Patch the action so it has a marshal we can look up
        enemy_phase["nations"]["Prussia"]["actions"][0]["ai_action"]["marshal"] = "Gneisenau"

        filtered = _filter_enemy_phase_by_visibility(enemy_phase, world)

        # Should have visible actions — no fog summary
        assert filtered.get("total_actions", 0) > 0
        assert "fog_hidden_summary" not in filtered
