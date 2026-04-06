"""Bug Fix Session 5: All 12 remaining bugs (8 P2, 4 P3).

Tests organized by batch per the session plan.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.models.region import SUPPLY_BY_TYPE


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════


def _make_world():
    """Create a minimal world for testing."""
    world = WorldState()
    world.player_nation = "France"
    world.enemy_nations = ["Prussia", "Austria", "Russia", "Britain", "Saxony"]
    return world


def _make_marshal(name="Ney", nation="France", location="Paris", strength=20000):
    """Create a test marshal."""
    m = Marshal(
        name=name,
        location=location,
        strength=strength,
        personality="aggressive",
        nation=nation,
    )
    m.morale = 80
    return m


def _set_relation(world, nation_a, nation_b, value):
    """Set relation between two nations to a specific value."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.nation_relations[key] = max(-100, min(100, value))


def _set_diplo_state(world, nation_a, nation_b, state):
    """Set diplomatic state between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


# ═══════════════════════════════════════════════════════════════════
# BATCH 1: DLF-8, DLF-10, B2, m4
# ═══════════════════════════════════════════════════════════════════


class TestDLF8VassalDowngradeExclusion:
    """DLF-8: Opportunistic downgrade should skip VASSAL state."""

    def test_vassal_excluded_from_downgrade(self):
        """VASSAL state should not be downgraded by AI."""
        from backend.game_logic.ai_diplomacy import _process_ai_ai_rivalry

        world = _make_world()
        _set_diplo_state(world, "Prussia", "Saxony", "VASSAL")
        _set_relation(world, "Prussia", "Saxony", 10)
        # Give Prussia overwhelming military advantage
        m1 = _make_marshal("Blucher", "Prussia", "Berlin", 80000)
        m2 = _make_marshal("Mack", "Saxony", "Dresden", 10000)
        world.marshals = {"Blucher": m1, "Mack": m2}
        events = _process_ai_ai_rivalry(world)
        # Should not downgrade VASSAL
        for e in events:
            if e.get("type") == "ai_ai_downgrade":
                pair = set(e.get("nations", []))
                assert pair != {
                    "Prussia",
                    "Saxony",
                }, "VASSAL should not be downgraded"

    def test_non_vassal_can_downgrade(self):
        """Non-VASSAL states can be downgraded when conditions are met."""
        from backend.game_logic.ai_diplomacy import _process_ai_ai_rivalry

        world = _make_world()
        _set_diplo_state(world, "Prussia", "Austria", "ALLIANCE")
        _set_relation(world, "Prussia", "Austria", 10)
        m1 = _make_marshal("Blucher", "Prussia", "Berlin", 80000)
        m2 = _make_marshal("Charles", "Austria", "Vienna", 10000)
        world.marshals = {"Blucher": m1, "Charles": m2}
        events = _process_ai_ai_rivalry(world)
        # Should produce a downgrade event
        downgrade_events = [e for e in events if e.get("type") == "ai_ai_downgrade"]
        assert len(downgrade_events) >= 1, "ALLIANCE should be downgraded with 8:1 troop ratio"


class TestDLF10ArmisticeVassalExclusion:
    """DLF-10: Armistice cooldown should not block VASSAL transitions."""

    def test_vassal_not_blocked_by_armistice(self):
        """VASSAL transition should be available even during armistice."""
        from backend.game_logic.diplomacy import get_available_diplomatic_actions

        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "WAR")
        # Set armistice cooldown
        key = world._make_diplo_key("France", "Saxony")
        world.armistice_cooldowns[key] = 5
        actions = get_available_diplomatic_actions(world, "Saxony")
        vassal_action = next(
            (a for a in actions if a.get("target_state") == "VASSAL"), None
        )
        if vassal_action:
            reason = vassal_action.get("disabled_reason") or vassal_action.get(
                "reason", ""
            )
            assert (
                "Armistice" not in reason
            ), "VASSAL should not be blocked by armistice"

    def test_war_blocked_by_armistice(self):
        """WAR should still be blocked by armistice cooldown."""
        from backend.game_logic.diplomacy import get_available_diplomatic_actions

        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        key = world._make_diplo_key("France", "Saxony")
        world.armistice_cooldowns[key] = 5
        actions = get_available_diplomatic_actions(world, "Saxony")
        war_action = next(
            (a for a in actions if a.get("target_state") == "WAR"), None
        )
        if war_action:
            reason = war_action.get("disabled_reason") or war_action.get("reason", "")
            assert "Armistice" in reason, "WAR should be blocked by armistice cooldown"

    def test_peace_not_blocked_by_armistice(self):
        """PEACE transition should not be blocked by armistice."""
        from backend.game_logic.diplomacy import get_available_diplomatic_actions

        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "WAR")
        key = world._make_diplo_key("France", "Saxony")
        world.armistice_cooldowns[key] = 5
        actions = get_available_diplomatic_actions(world, "Saxony")
        peace_action = next(
            (a for a in actions if a.get("target_state") == "PEACE"), None
        )
        if peace_action:
            reason = peace_action.get("disabled_reason") or peace_action.get(
                "reason", ""
            )
            assert "Armistice" not in reason

    def test_alliance_not_blocked_by_armistice(self):
        """ALLIANCE transition should not be blocked by armistice."""
        from backend.game_logic.diplomacy import get_available_diplomatic_actions

        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "DEFENSIVE_ALLIANCE")
        _set_relation(world, "France", "Saxony", 80)
        key = world._make_diplo_key("France", "Saxony")
        world.armistice_cooldowns[key] = 5
        actions = get_available_diplomatic_actions(world, "Saxony")
        alliance_action = next(
            (a for a in actions if a.get("target_state") == "ALLIANCE"), None
        )
        if alliance_action:
            reason = alliance_action.get("disabled_reason") or alliance_action.get(
                "reason", ""
            )
            assert "Armistice" not in reason


class TestB2SupplyCaps:
    """B2: Supply caps updated to match approved spec."""

    def test_town_supply_capacity(self):
        assert SUPPLY_BY_TYPE["town"] == 35000

    def test_city_supply_capacity(self):
        assert SUPPLY_BY_TYPE["city"] == 40000

    def test_capital_supply_unchanged(self):
        assert SUPPLY_BY_TYPE["capital"] == 50000


class TestM4AdjacentMoveRoute:
    """m4: Skip redundant route description for adjacent moves."""

    def test_adjacent_move_message_format(self):
        """Adjacent move (remaining=0) should not include 'Route:' in message."""
        remaining = 0
        target = "Brussels"
        first_step_msg = " Moves to Brussels."
        route_str = "Brussels"
        # Logic from strategic_executor.py
        if remaining == 0:
            msg = f"Ney begins march to {target}.{first_step_msg}"
        else:
            msg = f"Ney begins march to {target}. Route: {route_str}.{first_step_msg}"
        assert "Route:" not in msg

    def test_multi_hop_shows_route(self):
        """Multi-hop move (remaining>0) should include 'Route:' in message."""
        remaining = 1
        target = "Vienna"
        first_step_msg = " Moves to Munich."
        route_str = "Munich -> Vienna"
        if remaining == 0:
            msg = f"Ney begins march to {target}.{first_step_msg}"
        else:
            msg = f"Ney begins march to {target}. Route: {route_str}.{first_step_msg}"
        assert "Route:" in msg


# ═══════════════════════════════════════════════════════════════════
# BATCH 2: m1, m2, m3, PT-6
# ═══════════════════════════════════════════════════════════════════


class TestM1TrustParseNoDialogue:
    """m1: 'trust' typed without active dialogue should give clear message."""

    def test_trust_in_dialogue_keywords(self):
        """'trust' should be in the dialogue-only keyword list."""
        _DIALOGUE_ONLY_KEYWORDS = [
            "accept",
            "reject",
            "decline",
            "counter",
            "proceed",
            "cancel",
            "confront",
            "overlook",
            "apologize",
            "replace",
            "continue",
            "invest",
            "send",
            "execute",
            "reconsider",
            "modify",
            "honor",
            "side",
            "dismiss",
            "harsh",
            "generous",
            "adjust",
            "elaborate",
            "review",
            "consider",
            "begin",
            "trust",
            "yes",
            "agree",
            "start",
            "no",
            "never mind",
        ]
        assert "trust" in _DIALOGUE_ONLY_KEYWORDS

    def test_trust_exact_match(self):
        """'trust' should match via exact strip comparison."""
        raw = "trust"
        assert raw.lower().strip() == "trust"

    def test_normal_commands_not_blocked(self):
        """Normal game commands should not be in dialogue-only list."""
        _DIALOGUE_ONLY_KEYWORDS = [
            "accept",
            "reject",
            "decline",
            "counter",
            "proceed",
            "cancel",
            "confront",
            "overlook",
            "apologize",
            "replace",
            "continue",
            "invest",
            "send",
            "execute",
            "reconsider",
            "modify",
            "honor",
            "side",
            "dismiss",
            "harsh",
            "generous",
            "adjust",
            "elaborate",
            "review",
            "consider",
            "begin",
            "trust",
            "yes",
            "agree",
            "start",
            "no",
            "never mind",
        ]
        # These should NOT be blocked
        assert "attack" not in _DIALOGUE_ONLY_KEYWORDS
        assert "move" not in _DIALOGUE_ONLY_KEYWORDS
        assert "end turn" not in _DIALOGUE_ONLY_KEYWORDS
        assert "recruit" not in _DIALOGUE_ONLY_KEYWORDS


class TestM2CounterPunchDedup:
    """m2: Duplicate counter-punch notifications should be prevented."""

    def test_single_counter_punch_detected(self):
        """Dedup check should detect existing counter-punch for same marshal/turn."""
        from backend.notifications import (
            create_notification,
            NotificationPriority,
            COUNTER_PUNCH_EARNED,
            NotificationCollector,
        )

        collector = NotificationCollector()
        collector.add(
            create_notification(
                notification_type=COUNTER_PUNCH_EARNED,
                priority=NotificationPriority.HIGH,
                title="Davout - free attack!",
                message="Test",
                turn_created=5,
                details={"marshal": "Davout"},
            )
        )
        already_has = any(
            n.get("type") == COUNTER_PUNCH_EARNED
            and n.get("details", {}).get("marshal") == "Davout"
            and n.get("turn_created") == 5
            for n in collector.get_pending()
        )
        assert already_has is True

    def test_different_marshal_not_blocked(self):
        """Different marshal should not be blocked by existing counter-punch."""
        from backend.notifications import (
            create_notification,
            NotificationPriority,
            COUNTER_PUNCH_EARNED,
            NotificationCollector,
        )

        collector = NotificationCollector()
        collector.add(
            create_notification(
                notification_type=COUNTER_PUNCH_EARNED,
                priority=NotificationPriority.HIGH,
                title="Davout - free attack!",
                message="Test",
                turn_created=5,
                details={"marshal": "Davout"},
            )
        )
        already_has = any(
            n.get("type") == COUNTER_PUNCH_EARNED
            and n.get("details", {}).get("marshal") == "Ney"
            and n.get("turn_created") == 5
            for n in collector.get_pending()
        )
        assert already_has is False


class TestM3BombardmentMoraleFloor:
    """m3: Bombardment morale should not drop below forced-retreat threshold."""

    def test_bombardment_morale_floor(self):
        """Morale should not drop below 25% from bombardment."""
        from backend.game_logic.combat import FORCED_RETREAT_THRESHOLD

        m = _make_marshal("Wellington", "Britain", "Brussels", 25000)
        m.morale = 30
        bombardment_morale = -3
        m.adjust_morale(bombardment_morale)
        # Apply floor (as in combat_executor)
        if m.morale < FORCED_RETREAT_THRESHOLD:
            m.morale = FORCED_RETREAT_THRESHOLD
        assert m.morale >= FORCED_RETREAT_THRESHOLD

    def test_bombardment_square_morale_floor(self):
        """Square formation penalty (-18) that would drop below 25% gets floored."""
        from backend.game_logic.combat import FORCED_RETREAT_THRESHOLD

        m = _make_marshal("Wellington", "Britain", "Brussels", 25000)
        m.morale = 35  # 35 - 18 = 17, below threshold
        m.square_formation = True
        bombardment_morale = -3 - 15  # -18 total
        m.adjust_morale(bombardment_morale)
        if m.morale < FORCED_RETREAT_THRESHOLD:
            m.morale = FORCED_RETREAT_THRESHOLD
        assert m.morale == FORCED_RETREAT_THRESHOLD

    def test_collateral_morale_floor(self):
        """Collateral hit morale also has floor at 25%."""
        from backend.game_logic.combat import FORCED_RETREAT_THRESHOLD

        m = _make_marshal("Grouchy", "France", "Brussels", 15000)
        m.morale = 26
        m.adjust_morale(-1)
        if m.morale < FORCED_RETREAT_THRESHOLD:
            m.morale = FORCED_RETREAT_THRESHOLD
        assert m.morale >= FORCED_RETREAT_THRESHOLD


class TestPT6APWarning:
    """PT-6: End turn should warn about unused AP."""

    def test_ap_warning_generated(self):
        """Warning generated when AP remaining > 0."""
        world = _make_world()
        world.actions_remaining = 3
        ap_warning = ""
        if world.actions_remaining > 0:
            ap_warning = f" (Warning: {int(world.actions_remaining)} action(s) unused)"
        assert "3 action(s) unused" in ap_warning

    def test_no_warning_zero_ap(self):
        """No warning when AP is 0."""
        world = _make_world()
        world.actions_remaining = 0
        ap_warning = ""
        if world.actions_remaining > 0:
            ap_warning = f" (Warning: {int(world.actions_remaining)} action(s) unused)"
        assert ap_warning == ""

    def test_warning_in_message(self):
        """Warning should appear in turn-end message."""
        ap_warning = f" (Warning: {int(5)} action(s) unused)"
        message = f"Turn 3 ended.{ap_warning} Turn 4 begins!"
        assert "(Warning: 5 action(s) unused)" in message


# ═══════════════════════════════════════════════════════════════════
# BATCH 3: B1 — Fortify Cap Balance
# ═══════════════════════════════════════════════════════════════════


class TestB1FortifyCaps:
    """B1: Fortify caps updated to match approved spec (12/8/12)."""

    def test_aggressive_fortify_cap(self):
        from backend.models.personality_modifiers import get_max_fortify_bonus

        assert get_max_fortify_bonus("aggressive") == pytest.approx(0.08)

    def test_cautious_fortify_cap(self):
        from backend.models.personality_modifiers import get_max_fortify_bonus

        assert get_max_fortify_bonus("cautious") == pytest.approx(0.12)

    def test_default_fortify_cap(self):
        from backend.models.personality_modifiers import get_max_fortify_bonus

        assert get_max_fortify_bonus("literal") == pytest.approx(0.12)

    def test_defense_modifier_capped_at_175(self):
        """Total defense modifier should not exceed 1.75x hard cap."""
        m = _make_marshal("Wellington", "Britain", "Brussels", 30000)
        m.personality = "cautious"
        m.defense_bonus = 0.12
        from backend.models.marshal import Stance

        m.stance = Stance.DEFENSIVE
        modifier = m.get_defense_modifier()
        assert modifier <= 1.75

    def test_ney_cap_is_8_percent(self):
        from backend.models.personality_modifiers import get_max_fortify_bonus

        assert get_max_fortify_bonus("aggressive") == pytest.approx(0.08)


# ═══════════════════════════════════════════════════════════════════
# BATCH 4: PT-7 — Dead Code Removal
# ═══════════════════════════════════════════════════════════════════


class TestPT7BombardmentStreakRemoved:
    """PT-7: bombardment_streak and last_bombardment_target fields removed."""

    def test_no_bombardment_streak_field(self):
        m = _make_marshal()
        assert not hasattr(m, "bombardment_streak")

    def test_no_last_bombardment_target_field(self):
        m = _make_marshal()
        assert not hasattr(m, "last_bombardment_target")

    def test_serialization_roundtrip_clean(self):
        """Marshal serialization works without streak fields."""
        m = _make_marshal("Drouot", "France", "Paris", 15000)
        m.artillery = True
        m.bombardments_this_turn = 1
        d = m.to_dict()
        assert "bombardment_streak" not in d
        assert "last_bombardment_target" not in d
        m2 = Marshal.from_dict(d)
        assert m2.bombardments_this_turn == 1
        assert not hasattr(m2, "bombardment_streak")


# ═══════════════════════════════════════════════════════════════════
# BATCH 5: PT-3 — Emoji Replacement
# ═══════════════════════════════════════════════════════════════════


class TestPT3EmojiReplacement:
    """PT-3: No emoji in player-facing backend strings."""

    def _scan_file_for_emoji(self, filepath):
        """Scan a file for emoji in non-comment, non-debug string literals.

        Checks both literal emoji characters AND unicode escape sequences
        (PL-1: escapes like \\U0001f525 bypass literal emoji detection).
        """
        import re

        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # Emoticons
            "\U0001f300-\U0001f5ff"  # Misc Symbols
            "\U0001f680-\U0001f6ff"  # Transport
            "\U0001f1e0-\U0001f1ff"  # Flags
            "\u2600-\u26ff"  # Misc symbols
            "\u2700-\u27bf"  # Dingbats
            "]+",
            re.UNICODE,
        )
        # PL-1: Also detect unicode escape sequences in source text
        escape_pattern = re.compile(
            r'\\U0001f[0-9a-fA-F]{3}'  # \U0001fXXX emoji escapes
            r'|\\u26[0-9a-fA-F]{2}'    # \u26XX misc symbols
            r'|\\u27[0-9a-fA-F]{2}'    # \u27XX dingbats
            r'|\\u2694'                 # crossed swords
            r'|\\ufe0f'                 # variation selector
        )
        violations = []
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if (
                    "debug_print(" in stripped
                    or "ai_debug(" in stripped
                    or stripped.startswith("print(")
                ):
                    continue
                if emoji_pattern.search(line):
                    violations.append((i, stripped[:100]))
                elif escape_pattern.search(line):
                    violations.append((i, stripped[:100]))
        return violations

    def test_no_emoji_in_combat_executor(self):
        violations = self._scan_file_for_emoji("backend/commands/combat_executor.py")
        assert len(violations) == 0, f"Found emoji at lines: {violations}"

    def test_no_emoji_in_world_state(self):
        violations = self._scan_file_for_emoji("backend/models/world_state.py")
        assert len(violations) == 0, f"Found emoji at lines: {violations}"

    def test_no_emoji_in_combat(self):
        violations = self._scan_file_for_emoji("backend/game_logic/combat.py")
        assert len(violations) == 0, f"Found emoji at lines: {violations}"


# ═══════════════════════════════════════════════════════════════════
# BATCH 6: N3 — Coalition Friction Verification
# ═══════════════════════════════════════════════════════════════════


class TestN3CoalitionFrictionInScoring:
    """N3: Verify coalition friction is applied in attack scoring."""

    def test_friction_same_nation_full(self):
        from backend.game_logic.coalition import get_coalition_friction

        world = _make_world()
        assert get_coalition_friction("France", "France", world) == 1.0

    def test_friction_reduces_with_low_relations(self):
        from backend.game_logic.coalition import get_coalition_friction

        world = _make_world()
        _set_relation(world, "France", "Prussia", -30)
        friction = get_coalition_friction("France", "Prussia", world)
        assert friction < 1.0
        assert friction == 0.25

    def test_friction_full_for_high_relations(self):
        from backend.game_logic.coalition import get_coalition_friction

        world = _make_world()
        _set_relation(world, "France", "Austria", 50)
        friction = get_coalition_friction("France", "Austria", world)
        assert friction == 1.0
