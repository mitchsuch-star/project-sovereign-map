"""
Test Disobedience System (Phase 2)

Tests the complete disobedience system including:
- Trust system and obedience curve
- Authority tracker (anti-sycophancy)
- Severity calculation
- Objection handling
- Vindication tracking
"""

import pytest
from backend.models.trust import Trust, calculate_obedience_chance
from backend.models.authority import AuthorityTracker
from backend.models.personality import (
    Personality, get_personality, get_base_severity, PERSONALITY_TRIGGERS
)
from backend.commands.severity import (
    calculate_objection_severity, get_severity_breakdown,
    get_trust_modifier, get_vindication_modifier
)
from backend.commands.disobedience import DisobedienceSystem, MAX_MAJOR_OBJECTIONS_PER_TURN
from backend.commands.vindication import VindicationTracker
from backend.models.marshal import Marshal, create_starting_marshals
from backend.models.world_state import WorldState


class TestTrustSystem:
    """Test Trust class and obedience curve."""

    def test_trust_initialization(self):
        """Trust initializes with correct value."""
        trust = Trust(70)
        assert trust.value == 70

    def test_trust_clamping(self):
        """Trust clamps to 0-100 range."""
        trust_high = Trust(150)
        trust_low = Trust(-50)
        assert trust_high.value == 100
        assert trust_low.value == 0

    def test_trust_modify(self):
        """Trust modification works correctly."""
        trust = Trust(70)
        change = trust.modify(-15)
        assert trust.value == 55
        assert change == -15

    def test_trust_modify_clamping(self):
        """Trust modification respects bounds."""
        trust = Trust(95)
        change = trust.modify(20)
        assert trust.value == 100
        assert change == 5  # Only gained 5, not 20

    def test_trust_labels(self):
        """Trust labels match expected thresholds."""
        assert Trust(90).get_label() == "Loyal"
        assert Trust(70).get_label() == "Reliable"
        assert Trust(50).get_label() == "Questioning"
        assert Trust(30).get_label() == "Strained"
        assert Trust(10).get_label() == "Broken"


class TestObedienceCurve:
    """Test non-linear obedience probability curve."""

    def test_high_trust_guaranteed_obedience(self):
        """Trust 80+ = 100% obedience."""
        assert calculate_obedience_chance(80) == 1.0
        assert calculate_obedience_chance(90) == 1.0
        assert calculate_obedience_chance(100) == 1.0

    def test_reliable_range_obedience(self):
        """Trust 60-79 = 90-99% obedience."""
        assert 0.90 <= calculate_obedience_chance(60) <= 0.91
        assert 0.93 <= calculate_obedience_chance(70) <= 0.97
        assert 0.98 <= calculate_obedience_chance(79) <= 1.0

    def test_questioning_range_obedience(self):
        """Trust 40-59 = 70-89% obedience."""
        assert 0.70 <= calculate_obedience_chance(40) <= 0.71
        assert 0.78 <= calculate_obedience_chance(50) <= 0.82
        assert 0.88 <= calculate_obedience_chance(59) <= 0.90

    def test_strained_range_obedience(self):
        """Trust 20-39 = 40-69% obedience."""
        assert 0.40 <= calculate_obedience_chance(20) <= 0.41
        assert 0.50 <= calculate_obedience_chance(30) <= 0.60

    def test_broken_range_obedience(self):
        """Trust <20 = 20-39% obedience."""
        assert calculate_obedience_chance(0) == 0.20
        assert 0.25 <= calculate_obedience_chance(10) <= 0.35


class TestAuthorityTracker:
    """Test authority tracking and anti-sycophancy."""

    def test_authority_starts_at_100(self):
        """Authority starts at maximum."""
        tracker = AuthorityTracker()
        assert tracker.authority == 100

    def test_always_trust_reduces_authority(self):
        """Always trusting marshals reduces authority."""
        tracker = AuthorityTracker()
        for _ in range(8):
            tracker.record_response('trust')
        assert tracker.authority < 100

    def test_trust_gain_modifier_for_sycophant(self):
        """Always trusting reduces trust gain modifier."""
        tracker = AuthorityTracker()
        for _ in range(8):
            tracker.record_response('trust')
        modifier = tracker.get_trust_gain_modifier()
        assert modifier < 1.0

    def test_balanced_responses_maintain_authority(self):
        """Balanced responses maintain or increase authority."""
        tracker = AuthorityTracker()
        responses = ['trust', 'insist', 'compromise', 'trust', 'insist',
                    'compromise', 'trust', 'compromise']
        for r in responses:
            tracker.record_response(r)
        assert tracker.authority >= 100

    def test_obedience_modifier_high_authority(self):
        """High authority gives obedience bonus."""
        tracker = AuthorityTracker()
        assert tracker.get_obedience_modifier() == 1.1

    def test_authority_threshold_events(self):
        """Authority crossing thresholds triggers events."""
        tracker = AuthorityTracker()
        # Drop authority by always trusting
        for _ in range(15):
            event = tracker.record_response('trust')
            if event and event['threshold'] == 70:
                assert event['name'] == 'Whispers of Weakness'
                break


class TestPersonalityTriggers:
    """Test personality-based objection triggers."""

    def test_aggressive_defend_trigger(self):
        """Aggressive personality triggers on defend orders."""
        severity = PERSONALITY_TRIGGERS[Personality.AGGRESSIVE].get('defend')
        assert severity is not None
        assert severity >= 0.50  # Major objection

    def test_cautious_outnumbered_trigger(self):
        """Cautious personality triggers on outnumbered attacks."""
        severity = PERSONALITY_TRIGGERS[Personality.CAUTIOUS].get('attack_outnumbered_2to1')
        assert severity is not None
        assert severity >= 0.50

    def test_literal_ambiguous_trigger(self):
        """Literal personality triggers on ambiguous orders."""
        severity = PERSONALITY_TRIGGERS[Personality.LITERAL].get('ambiguous_order')
        assert severity is not None

    def test_loyal_minimal_triggers(self):
        """Loyal personality has few triggers."""
        loyal_triggers = PERSONALITY_TRIGGERS[Personality.LOYAL]
        # Loyal marshals only object to extreme situations
        assert 'defend' not in loyal_triggers
        assert 'attack' not in loyal_triggers

    def test_get_personality_conversion(self):
        """String personality converts to enum correctly."""
        assert get_personality('aggressive') == Personality.AGGRESSIVE
        assert get_personality('Cautious') == Personality.CAUTIOUS
        assert get_personality('unknown') == Personality.BALANCED


class TestSeverityCalculation:
    """Test objection severity calculation."""

    def test_ney_defend_severity(self):
        """Ney objects to defensive orders with high severity."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]
        order = {'action': 'defend', 'target': 'Belgium'}

        severity = calculate_objection_severity(ney, order, None, include_variance=False)

        # Base 0.60 * trust modifier (0.9 for trust 75) = ~0.54
        assert 0.45 <= severity <= 0.70

    def test_ney_attack_no_severity(self):
        """Ney doesn't object to attack orders."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]
        order = {'action': 'attack', 'target': 'Wellington'}

        severity = calculate_objection_severity(ney, order, None, include_variance=False)
        assert severity == 0.0

    def test_davout_no_objection_normal_attack(self):
        """Davout doesn't object to normal attacks."""
        marshals = create_starting_marshals()
        davout = marshals["Davout"]
        order = {'action': 'attack', 'target': 'Wellington'}

        # Without game state showing outnumbered situation
        severity = calculate_objection_severity(davout, order, None, include_variance=False)
        assert severity == 0.0

    def test_trust_modifier_effect(self):
        """Low trust increases severity."""
        low_trust_marshal = Marshal("Test", "Paris", 50000, "aggressive")
        low_trust_marshal.trust.set(30)

        high_trust_marshal = Marshal("Test2", "Paris", 50000, "aggressive")
        high_trust_marshal.trust.set(90)

        assert get_trust_modifier(low_trust_marshal) > get_trust_modifier(high_trust_marshal)

    def test_vindication_modifier_effect(self):
        """Positive vindication increases severity (marshal bolder)."""
        vindicated_marshal = Marshal("Test", "Paris", 50000, "aggressive")
        vindicated_marshal.vindication_score = 4

        normal_marshal = Marshal("Test2", "Paris", 50000, "aggressive")
        normal_marshal.vindication_score = 0

        assert get_vindication_modifier(vindicated_marshal) > get_vindication_modifier(normal_marshal)

    def test_severity_capped_at_95(self):
        """Severity never exceeds 0.95."""
        marshal = Marshal("Test", "Paris", 50000, "aggressive")
        marshal.trust.set(10)  # Very low trust
        marshal.vindication_score = 5  # Max vindication
        marshal.recent_overrides = [True, True, True, True, True]  # Frequently overridden

        order = {'action': 'defend'}
        severity = calculate_objection_severity(marshal, order, None, include_variance=False)

        assert severity <= 0.95


class TestDisobedienceSystem:
    """Test main disobedience system."""

    def test_no_objection_below_threshold(self):
        """No objection for severity < 0.20."""
        system = DisobedienceSystem()
        marshal = Marshal("Test", "Paris", 50000, "balanced")
        order = {'action': 'move', 'target': 'Lyon'}

        objection = system.evaluate_order(marshal, order, None)
        assert objection is None

    def test_mild_objection_threshold(self):
        """Mild objection for 0.20 <= severity < 0.50."""
        system = DisobedienceSystem()
        marshals = create_starting_marshals()
        ney = marshals["Ney"]
        ney.trust.set(90)  # High trust reduces severity

        order = {'action': 'hold', 'target': 'Belgium'}
        objection = system.evaluate_order(ney, order, None)

        if objection:
            # Could be mild or no objection depending on variance
            assert objection['type'] in ('mild_objection', 'major_objection')

    def test_major_objection_creates_options(self):
        """Major objection provides player options."""
        system = DisobedienceSystem()
        marshals = create_starting_marshals()
        ney = marshals["Ney"]
        ney.trust.set(50)  # Lower trust

        order = {'action': 'defend', 'target': 'Belgium'}
        objection = system.evaluate_order(ney, order, None)

        if objection and objection['type'] == 'major_objection':
            assert 'options' in objection
            option_ids = [o['id'] for o in objection['options']]
            assert 'trust' in option_ids
            assert 'insist' in option_ids

    def test_objection_cap_per_turn(self):
        """Maximum 2 major objections per turn."""
        system = DisobedienceSystem()
        ney = Marshal("Ney", "Belgium", 72000, "aggressive")
        ney.trust.set(40)  # Lower trust for more objections

        defend_order = {'action': 'defend', 'target': 'Belgium'}
        major_count = 0

        for i in range(5):
            objection = system.evaluate_order(ney, defend_order, None)
            if objection and objection['type'] == 'major_objection':
                major_count += 1

        assert major_count <= MAX_MAJOR_OBJECTIONS_PER_TURN

    def test_turn_reset_clears_objection_count(self):
        """Turn reset clears major objection count."""
        system = DisobedienceSystem()
        system.major_objections_this_turn = 2

        system.reset_turn()

        assert system.major_objections_this_turn == 0


class TestVindicationTracker:
    """Test vindication tracking system."""

    def test_record_choice(self):
        """Choices are recorded for vindication."""
        tracker = VindicationTracker()
        tracker.record_choice('Ney', 'trust', {'action': 'attack'})

        assert tracker.has_pending('Ney')
        pending = tracker.get_pending('Ney')
        assert pending['choice'] == 'trust'

    def test_trust_victory_vindicates_marshal(self):
        """Trusting marshal + victory = marshal vindicated."""
        tracker = VindicationTracker()

        # Create mock game state
        class MockMarshal:
            def __init__(self):
                self.name = 'Ney'
                self.trust = Trust(70)
                self.vindication_score = 0
                self.recent_battles = []
                self.recent_overrides = []
                self.redemption_pending = False

            def modify_trust(self, delta):
                """Mock modify_trust that wraps trust.modify and clears redemption_pending."""
                actual = self.trust.modify(delta)
                if self.redemption_pending and self.trust.value > 20:
                    self.redemption_pending = False
                return actual

        class MockWorld:
            def __init__(self):
                self.marshal = MockMarshal()
            def get_marshal(self, name):
                return self.marshal

        class MockGameState:
            def __init__(self):
                self.world = MockWorld()

        game_state = MockGameState()
        tracker.record_choice('Ney', 'trust', {'action': 'attack'})

        result = tracker.resolve_battle('Ney', 'victory', game_state)

        assert result['vindication_change'] == 1
        assert result['trust_change'] > 0
        assert game_state.world.marshal.vindication_score == 1

    def test_insist_defeat_vindicates_marshal(self):
        """Insisting + defeat = marshal was right."""
        tracker = VindicationTracker()

        class MockMarshal:
            def __init__(self):
                self.name = 'Ney'
                self.trust = Trust(70)
                self.vindication_score = 0
                self.recent_battles = []
                self.recent_overrides = []
                self.redemption_pending = False

            def modify_trust(self, delta):
                """Mock modify_trust that wraps trust.modify and clears redemption_pending."""
                actual = self.trust.modify(delta)
                if self.redemption_pending and self.trust.value > 20:
                    self.redemption_pending = False
                return actual

        class MockAuthority:
            def __init__(self):
                self.authority = 100
            def get_trust_gain_modifier(self):
                return 1.0

        class MockWorld:
            def __init__(self):
                self.marshal = MockMarshal()
            def get_marshal(self, name):
                return self.marshal

        class MockGameState:
            def __init__(self):
                self.world = MockWorld()
                self.authority_tracker = MockAuthority()

        game_state = MockGameState()
        tracker.record_choice('Ney', 'insist', {'action': 'attack'})

        result = tracker.resolve_battle('Ney', 'defeat', game_state)

        assert result['vindication_change'] == 1  # Marshal vindicated
        assert result['trust_change'] < 0  # Trust penalty
        assert result['authority_change'] < 0  # Authority penalty


class TestWorldStateIntegration:
    """Test disobedience integration with WorldState."""

    def test_world_state_has_trackers(self):
        """WorldState initializes with disobedience trackers."""
        world = WorldState()

        assert hasattr(world, 'authority_tracker')
        assert hasattr(world, 'vindication_tracker')
        assert hasattr(world, 'disobedience_system')
        assert isinstance(world.authority_tracker, AuthorityTracker)
        assert isinstance(world.vindication_tracker, VindicationTracker)
        assert isinstance(world.disobedience_system, DisobedienceSystem)

    def test_marshals_have_trust(self):
        """Marshals initialized with Trust objects."""
        world = WorldState()

        for marshal in world.marshals.values():
            assert hasattr(marshal, 'trust')
            assert isinstance(marshal.trust, Trust)
            assert hasattr(marshal, 'vindication_score')

    def test_turn_advance_resets_disobedience(self):
        """Turn advance resets disobedience counters."""
        world = WorldState()
        world.disobedience_system.major_objections_this_turn = 2

        world.force_end_turn()

        assert world.disobedience_system.major_objections_this_turn == 0

    def test_marshal_starting_trust_values(self):
        """Marshals have appropriate starting trust."""
        world = WorldState()

        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        grouchy = world.get_marshal("Grouchy")

        assert ney.trust.value == 75
        assert davout.trust.value == 85  # Most trusted
        assert grouchy.trust.value == 65  # Newly promoted


class TestSeverityBreakdown:
    """Test detailed severity breakdown for debugging/UI."""

    def test_breakdown_includes_all_modifiers(self):
        """Breakdown shows all modifier components."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]
        order = {'action': 'defend', 'target': 'Belgium'}

        breakdown = get_severity_breakdown(ney, order, None)

        assert 'personality' in breakdown
        assert 'situation' in breakdown
        assert 'base_severity' in breakdown
        assert 'modifiers' in breakdown
        assert 'final_severity' in breakdown
        assert 'trust' in breakdown['modifiers']
        assert 'vindication' in breakdown['modifiers']

    def test_breakdown_identifies_will_object(self):
        """Breakdown indicates if objection will occur."""
        marshals = create_starting_marshals()
        ney = marshals["Ney"]

        defend_breakdown = get_severity_breakdown(ney, {'action': 'defend'}, None)
        attack_breakdown = get_severity_breakdown(ney, {'action': 'attack'}, None)

        assert defend_breakdown['will_object'] == True
        assert attack_breakdown['will_object'] == False


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_marshal_without_trust_attribute(self):
        """Handles marshals without trust gracefully."""
        marshal = Marshal("Old", "Paris", 50000, "balanced")
        # Manually remove trust for testing backward compat
        if hasattr(marshal, 'trust'):
            delattr(marshal, 'trust')

        modifier = get_trust_modifier(marshal)
        # Default trust 70 = Reliable range = 0.9 modifier
        assert modifier == 0.9

    def test_vindication_no_pending(self):
        """Resolving battle with no pending vindication."""
        tracker = VindicationTracker()
        result = tracker.resolve_battle('Unknown', 'victory', None)
        assert result is None

    def test_empty_order(self):
        """Empty order causes no objection."""
        system = DisobedienceSystem()
        marshal = Marshal("Test", "Paris", 50000, "aggressive")

        objection = system.evaluate_order(marshal, {}, None)
        assert objection is None

    def test_unknown_action(self):
        """Unknown action causes no objection."""
        system = DisobedienceSystem()
        marshal = Marshal("Test", "Paris", 50000, "aggressive")
        order = {'action': 'unknown_action', 'target': 'Paris'}

        objection = system.evaluate_order(marshal, order, None)
        assert objection is None


class TestExecutorIntegration:
    """Test executor integration with disobedience system."""

    def test_pending_objection_blocks_commands(self):
        """Pending objection blocks new commands."""
        from backend.commands.executor import CommandExecutor

        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        # Manually set a pending objection (matching disobedience.py keys)
        world.pending_objection = {
            "type": "major_objection",
            "marshal": "Ney",
            "message": "Test objection",
            "original_order": {"action": "attack"},
            "suggested_alternative": None,
            "compromise": None
        }

        # Try to execute a command
        result = executor.execute(
            {"command": {"action": "attack", "marshal": "Davout", "target": "Waterloo"}},
            game_state
        )

        assert result["success"] == False
        assert "awaiting your response" in result["message"]

    def test_handle_objection_response_clears_pending(self):
        """Handle objection response clears pending objection."""
        from backend.commands.executor import CommandExecutor

        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        # Manually set a pending objection (matching disobedience.py keys)
        world.pending_objection = {
            "type": "major_objection",
            "marshal": "Ney",
            "message": "Test objection",
            "original_order": {"action": "defend", "marshal": "Ney"},
            "suggested_alternative": None,
            "compromise": None,
            "severity": 0.6
        }

        # Respond with 'insist'
        result = executor.handle_objection_response("insist", game_state)

        # Pending objection should be cleared
        assert world.pending_objection is None
        assert result["objection_resolved"] == True

    def test_no_pending_objection_returns_error(self):
        """Handle response with no pending returns error."""
        from backend.commands.executor import CommandExecutor

        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        result = executor.handle_objection_response("trust", game_state)

        assert result["success"] == False
        assert "No objection pending" in result["message"]

    def test_invalid_choice_returns_error(self):
        """Invalid choice returns error."""
        from backend.commands.executor import CommandExecutor

        world = WorldState()
        game_state = {"world": world}
        executor = CommandExecutor()

        world.pending_objection = {
            "type": "major_objection",
            "marshal": "Ney",
            "message": "Test",
            "original_order": {"action": "attack"},
            "suggested_alternative": None,
            "compromise": None
        }

        result = executor.handle_objection_response("invalid_choice", game_state)

        assert result["success"] == False
        assert "Invalid choice" in result["message"]

    def test_world_state_has_pending_objection_field(self):
        """WorldState has pending_objection initialized to None."""
        world = WorldState()
        assert hasattr(world, 'pending_objection')
        assert world.pending_objection is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
