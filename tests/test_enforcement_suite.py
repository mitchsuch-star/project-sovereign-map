"""
R18 — Test Enforcement Suite (Architecture Refactoring Session 9)

Cross-cutting enforcement tests that catch the recurring bug pattern where a new
action/event/proposal type is added to one registry but not another.

Complements existing enforcement tests:
- test_campaign_log_enforcement.py (R8) — event types ↔ CAMPAIGN_LOG_TYPES
- test_serialization_enforcement.py — round-trip serialization
"""

import os
import re

import pytest

from backend.ai.validation import VALID_ACTIONS, META_ACTIONS
from backend.display_names import (
    ACTION_DISPLAY,
    OBJECTION_DISPLAY,
    DEFIANCE_DISPLAY,
    PROPOSAL_TYPE_DISPLAY,
    STATE_DISPLAY,
    STATE_NARRATIVE_DISPLAY,
    FEEDBACK_STRINGS,
)
from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP


# ============================================================================
# Helpers
# ============================================================================

def _get_parser_valid_actions():
    """Get the parser's valid_actions list without constructing a full parser."""
    from backend.commands.parser import CommandParser
    parser = CommandParser(use_real_llm=False)
    return set(parser.valid_actions)


def _get_action_costs():
    """Get the _action_costs dict from a fresh WorldState."""
    from backend.models.world_state import WorldState
    ws = WorldState()
    return dict(ws._action_costs)


def _get_free_actions():
    """Get the free_actions list from executor source (avoids executing code)."""
    # These are actions in the executor's free_actions list that bypass AP costs.
    # Maintained here as a mirror — if executor changes, this test catches drift.
    return {
        "status", "help", "end_turn", "unknown", "retreat", "wait", "debug",
        "economy", "treasury", "finances", "break_square",
        "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility",
        "diplomatic_advisory", "diplomatic_error",
        "diplomatic_break", "diplomatic_downgrade",
        "diplomatic_declare_war", "diplomatic_ultimatum",
        "invest_vassal", "change_autonomy", "make_vassal", "release_vassal",
        # VS-3: land grant — paid in DP (the land IS the cost), no AP
        "grant_region_to_vassal",
        # B-B7: Make Amends — paid in DP/gold, no AP cost (spec §8.6.1)
        "make_amends",
        # Imperial Settlement — opens settlement_confirm dialogue, free.
        "propose_common_peace",
        # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 — labeled white
        # peace shares settlement_confirm dialogue, free action.
        "propose_white_peace",
    }


def _get_executor_method_names():
    """Extract all _execute_* method names from all executor source files."""
    pattern = re.compile(r'def (_execute_\w+)\(')
    methods = set()
    executor_files = (
        'executor.py', 'combat_executor.py', 'strategic_executor.py',
        'diplomatic_executor.py', 'economy_executor.py', 'tactical_executor.py',
        'vassal_executor.py', 'capture_executor.py',
        'movement_executor.py', 'meta_executor.py',
    )
    for filename in executor_files:
        path = os.path.join(
            os.path.dirname(__file__), '..', 'backend', 'commands', filename
        )
        path = os.path.normpath(path)
        with open(path, 'r', encoding='utf-8') as f:
            methods.update(pattern.findall(f.read()))
    return methods


def _get_executor_dispatch_actions():
    """Extract actions dispatched in _execute_specific from executor source.

    Parses the if/elif chain in _execute_specific to find which action strings
    are handled.
    """
    executor_path = os.path.join(
        os.path.dirname(__file__), '..', 'backend', 'commands', 'executor.py'
    )
    executor_path = os.path.normpath(executor_path)
    with open(executor_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the _execute_specific method body (R13B: may be last method in class)
    pattern = re.compile(
        r'def _execute_specific\(.*?\n(.*?)(?=\n    def |\nclass |\Z)',
        re.DOTALL
    )
    match = pattern.search(content)
    if not match:
        return set()

    body = match.group(1)
    # Extract action == "xxx" patterns
    action_pattern = re.compile(r'action\s*==\s*["\'](\w+)["\']')
    return set(action_pattern.findall(body))


def _find_proposal_types_in_source():
    """Scan backend source for proposal type strings used in diplomacy code."""
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
    backend_dir = os.path.normpath(backend_dir)

    # Files that define/use proposal types
    target_files = [
        os.path.join(backend_dir, 'game_logic', 'diplomatic_dialogue.py'),
        os.path.join(backend_dir, 'game_logic', 'ai_diplomacy.py'),
        os.path.join(backend_dir, 'game_logic', 'diplomacy.py'),
    ]

    # Known non-proposal "type" values to exclude
    non_proposal_types = {
        "territory", "gold_lump", "gold_per_turn", "open_borders",
        "protection", "ap_reduction", "continental_system",
        "protection_promised", "territory_saxony",
    }

    found_types = set()
    for filepath in target_files:
        if not os.path.exists(filepath):
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract proposal_type = "xxx" and proposal_type == "xxx" patterns
        pt_assign = re.compile(r'proposal_type\s*(?:=|==|in\s*\()\s*["\'](\w+)["\']')
        for match in pt_assign.finditer(content):
            val = match.group(1)
            if val not in non_proposal_types:
                found_types.add(val)

    return found_types


# ============================================================================
# Test 1: All valid actions have explicit AP costs or are free
# ============================================================================

class TestAllActionsHaveAPCosts:
    """Every action should have an explicit AP cost or be in free_actions.

    Actions that fall through to the default cost of 1 in get_action_cost()
    are a latent bug risk — the cost is implicit rather than intentional.
    """

    # Actions that handle cost via variable_action_cost in their handler
    # (these bypass _action_costs entirely)
    VARIABLE_COST_ACTIONS = {
        "wait",            # returns variable_action_cost: 0
        "defend",          # returns variable_action_cost based on stance transition
        "hold",            # routes to defend
        "stance_change",   # returns variable_action_cost based on stance transition
    }

    def test_non_free_actions_have_explicit_costs(self):
        """Actions that cost AP should be in _action_costs or use variable_action_cost."""
        action_costs = _get_action_costs()
        free_actions = _get_free_actions()

        missing = []
        for action in VALID_ACTIONS:
            if action in free_actions:
                continue
            if action in self.VARIABLE_COST_ACTIONS:
                continue
            # Strategic actions (pursue/support/reinforce/march) are handled
            # via strategic cost path (2 AP / 1 for literal), not _action_costs
            if action in ("pursue", "support", "reinforce", "march"):
                continue
            if action not in action_costs:
                missing.append(action)

        assert not missing, (
            f"Actions in VALID_ACTIONS with no explicit AP cost "
            f"(defaulting to 1 via get_action_cost): {sorted(missing)}. "
            f"Add them to WorldState._action_costs or free_actions."
        )

    def test_free_actions_not_in_action_costs_with_nonzero(self):
        """Free actions should not also appear in _action_costs with cost > 0."""
        action_costs = _get_action_costs()
        free_actions = _get_free_actions()

        conflicts = []
        for action in free_actions:
            if action in action_costs and action_costs[action] > 0:
                conflicts.append((action, action_costs[action]))

        assert not conflicts, (
            f"Actions are in free_actions AND _action_costs with cost>0 "
            f"(ambiguous AP handling): {conflicts}"
        )

    def test_action_costs_are_integers(self):
        """All AP costs must be integers (Godot crashes on floats)."""
        action_costs = _get_action_costs()
        non_int = {k: v for k, v in action_costs.items() if not isinstance(v, int)}
        assert not non_int, f"Non-integer AP costs: {non_int}"


# ============================================================================
# Test 2: All valid actions have display names
# ============================================================================

class TestAllActionsHaveDisplayNames:
    """Player-facing actions should have display names to avoid leaking raw
    internal action strings to the UI."""

    # Actions that never appear in player-facing UI text
    # (meta commands, diplomatic routing, etc.)
    DISPLAY_EXEMPT = {
        "help", "end_turn", "debug", "status", "unknown",
        # Strategic aliases — displayed as their strategic type (PURSUE, SUPPORT, etc.)
        "pursue", "support", "reinforce", "march",
        # Diplomatic meta-actions — displayed via proposal type, not action name
        "diplomatic_proposal", "diplomatic_mission", "diplomatic_feasibility",
        "diplomatic_advisory", "diplomatic_error",
        "diplomatic_break", "diplomatic_downgrade",
        "diplomatic_declare_war", "diplomatic_ultimatum",
        # Vassal actions — displayed via custom messages
        "invest_vassal", "change_autonomy", "make_vassal", "release_vassal",
        # SETTLEMENT_UI_CLEANUP_SPEC v0.28 G2-Slice-W1 — labeled CTAs
        # displayed by the wizard ("Propose White Peace"), not via
        # ACTION_DISPLAY's tactical-action humanizer.
        "propose_white_peace",
        # Aliases
        "hold",  # Maps to defend
    }

    def test_tactical_actions_have_display_names(self):
        """All non-exempt VALID_ACTIONS should have an entry in ACTION_DISPLAY."""
        missing = []
        for action in VALID_ACTIONS:
            if action in self.DISPLAY_EXEMPT:
                continue
            if action not in ACTION_DISPLAY:
                missing.append(action)

        assert not missing, (
            f"Actions missing from ACTION_DISPLAY (raw names would leak to UI): "
            f"{sorted(missing)}"
        )

    def test_action_display_has_objection_form(self):
        """Every action in ACTION_DISPLAY should also have an objection form
        (gerund) for objection/campaign log context."""
        missing = []
        for action in ACTION_DISPLAY:
            if action not in OBJECTION_DISPLAY:
                missing.append(action)

        assert not missing, (
            f"Actions in ACTION_DISPLAY but missing from OBJECTION_DISPLAY "
            f"(objection log would show raw name): {sorted(missing)}"
        )

    def test_action_display_has_defiance_form(self):
        """Every action in ACTION_DISPLAY should also have a defiance form
        (past tense) for defiance context."""
        missing = []
        for action in ACTION_DISPLAY:
            if action not in DEFIANCE_DISPLAY:
                missing.append(action)

        assert not missing, (
            f"Actions in ACTION_DISPLAY but missing from DEFIANCE_DISPLAY "
            f"(defiance log would show raw name): {sorted(missing)}"
        )


# ============================================================================
# Test 3: All logged event types are whitelisted
# (Complementary to test_campaign_log_enforcement.py — tests the reverse direction)
# ============================================================================

class TestCampaignLogCompleteness:
    """Complementary checks beyond what R8 enforcement already covers."""

    def test_every_whitelisted_type_has_category(self):
        """Every type in CAMPAIGN_LOG_TYPES must have a CATEGORY_MAP entry."""
        missing = CAMPAIGN_LOG_TYPES - set(CATEGORY_MAP.keys())
        assert not missing, (
            f"Types in CAMPAIGN_LOG_TYPES with no CATEGORY_MAP entry: {sorted(missing)}"
        )

    def test_category_map_subset_of_whitelist(self):
        """CATEGORY_MAP should not contain types not in CAMPAIGN_LOG_TYPES."""
        extra = set(CATEGORY_MAP.keys()) - CAMPAIGN_LOG_TYPES
        assert not extra, (
            f"Types in CATEGORY_MAP but not in CAMPAIGN_LOG_TYPES: {sorted(extra)}"
        )

    def test_categories_are_known(self):
        """All category values should be from a known set."""
        known_categories = {"combat", "territory", "economy", "command", "diplomacy"}
        unknown = set()
        for event_type, category in CATEGORY_MAP.items():
            if category not in known_categories:
                unknown.add((event_type, category))
        assert not unknown, f"Unknown categories in CATEGORY_MAP: {unknown}"


# ============================================================================
# Test 4: All proposal types have display strings
# ============================================================================

class TestProposalTypesHaveDisplay:
    """Every proposal type used in the diplomacy system must have a display name."""

    # Known proposal types from the codebase
    KNOWN_PROPOSAL_TYPES = {
        "peace",
        "alliance",
        "non_aggression",
        "open_borders",
        "defensive_alliance",
        "armistice",
        "armistice_losing",
        "armistice_stalemate",
        "armistice_winning",
        "vassalage",
        "opportunistic",
    }

    def test_all_known_types_have_display(self):
        """All known proposal types must have a PROPOSAL_TYPE_DISPLAY entry."""
        missing = self.KNOWN_PROPOSAL_TYPES - set(PROPOSAL_TYPE_DISPLAY.keys())
        assert not missing, (
            f"Proposal types missing from PROPOSAL_TYPE_DISPLAY "
            f"(raw names would appear in popup): {sorted(missing)}"
        )

    def test_source_proposal_types_have_display(self):
        """Proposal types found in source code should have display names."""
        found = _find_proposal_types_in_source()
        if not found:
            pytest.skip("No proposal types found in source (regex may be broken)")

        missing = found - set(PROPOSAL_TYPE_DISPLAY.keys())
        # Filter out values that are clearly not proposal types
        false_positives = {"peace_terms", "type", "counter", "modify", "start"}
        missing -= false_positives

        assert not missing, (
            f"Proposal types found in source but missing from PROPOSAL_TYPE_DISPLAY: "
            f"{sorted(missing)}"
        )

    def test_feedback_strings_cover_known_factors(self):
        """All acceptance formula factors should have feedback strings."""
        # Known factors from the acceptance formula in diplomacy.py
        known_factors = {
            "relation_modifier", "war_score_modifier",
            "deal_balance", "personality_modifier", "diplomat_skill_bonus",
            "base_disposition", "special_desire_bonus",
            "hegemony_target_mod", "bilateral_betrayal_mod",
            "harshness_penalty", "harshness_bonus", "reliability_modifier",
            "war_weariness", "stalemate_duration", "military_supremacy",
            "battlefield_diplomacy", "military_pressure", "ultimatum_bonus",
        }

        missing = known_factors - set(FEEDBACK_STRINGS.keys())
        assert not missing, (
            f"Acceptance formula factors missing from FEEDBACK_STRINGS: "
            f"{sorted(missing)}"
        )

    def test_feedback_strings_have_both_polarities(self):
        """Each feedback string must have both negative and positive forms."""
        for factor, polarities in FEEDBACK_STRINGS.items():
            assert "negative" in polarities, (
                f"FEEDBACK_STRINGS['{factor}'] missing 'negative' polarity"
            )
            assert "positive" in polarities, (
                f"FEEDBACK_STRINGS['{factor}'] missing 'positive' polarity"
            )


# ============================================================================
# Test 5: VALID_ACTIONS consistent across modules
# ============================================================================

class TestValidActionsConsistency:
    """VALID_ACTIONS (validation.py) must be consistent with parser + executor."""

    # Actions in parser but not in validation (meta/legacy — known gaps)
    PARSER_ONLY_KNOWN = {
        "help", "end_turn", "debug", "status",
    }

    # Actions in validation but not in parser (these go through LLM, not parser list)
    VALIDATION_ONLY_KNOWN = {
        # These are in VALID_ACTIONS for LLM validation but the parser doesn't
        # list them because they're handled by strategic_parser or diplomatic routing
    }

    def test_parser_covers_valid_actions(self):
        """Every VALID_ACTIONS entry should be in the parser's valid_actions."""
        parser_actions = _get_parser_valid_actions()

        # Actions that validation.py has but parser doesn't need
        # (parser handles them through other paths)
        parser_exempt = set()

        missing = VALID_ACTIONS - parser_actions - parser_exempt
        assert not missing, (
            f"Actions in VALID_ACTIONS but not in parser.valid_actions: "
            f"{sorted(missing)}. The parser won't recognize these actions."
        )

    def test_parser_subset_of_valid_actions(self):
        """Parser's valid_actions should be a subset of VALID_ACTIONS + META_ACTIONS."""
        parser_actions = _get_parser_valid_actions()
        all_known = VALID_ACTIONS | META_ACTIONS | {"cheat"}

        extra = parser_actions - all_known
        assert not extra, (
            f"Actions in parser.valid_actions but not in VALID_ACTIONS or META_ACTIONS: "
            f"{sorted(extra)}. These may bypass LLM validation."
        )

    def test_executor_handles_dispatched_actions(self):
        """Every action dispatched in _execute_specific should have a handler."""
        dispatch_actions = _get_executor_dispatch_actions()
        method_names = _get_executor_method_names()

        # Map action names to expected method names
        # Some actions have non-standard method names
        METHOD_NAME_MAP = {
            "retreat": "_execute_retreat_action",  # historical naming
        }
        expected_methods = set()
        for action in dispatch_actions:
            if action in ("hold",):
                continue  # hold routes to defend, no _execute_hold
            expected_methods.add(METHOD_NAME_MAP.get(action, f"_execute_{action}"))

        missing = expected_methods - method_names
        assert not missing, (
            f"Actions dispatched in _execute_specific but no matching _execute_* method: "
            f"{sorted(missing)}"
        )

    def test_execute_specific_covers_tactical_actions(self):
        """Tactical (non-meta, non-diplomatic, non-strategic) actions should
        be dispatched in _execute_specific."""
        dispatch_actions = _get_executor_dispatch_actions()

        # Tactical actions that should be in the dispatch chain
        tactical_actions = {
            "attack", "defend", "hold", "wait", "move", "scout", "retreat",
            "drill", "fortify", "unfortify", "form_square", "break_square",
            "stance_change",
        }

        missing = tactical_actions - dispatch_actions
        assert not missing, (
            f"Tactical actions not dispatched in _execute_specific: "
            f"{sorted(missing)}. These would hit the 'Unknown action' fallback."
        )


# ============================================================================
# Test 6: Diplomatic state display completeness
# ============================================================================

class TestDiplomaticStateDisplayCompleteness:
    """All diplomatic states should have display names."""

    def test_state_display_covers_all_states(self):
        """Every diplomatic state used in diplomacy.py should have a display name."""
        from backend.game_logic.diplomacy import DIPLOMATIC_STATES
        missing = set()
        for state in DIPLOMATIC_STATES:
            if state not in STATE_DISPLAY:
                missing.add(state)
        assert not missing, (
            f"Diplomatic states missing from STATE_DISPLAY: {sorted(missing)}"
        )

    def test_state_narrative_covers_all_states(self):
        """STATE_NARRATIVE_DISPLAY should cover the same states as STATE_DISPLAY."""
        missing = set(STATE_DISPLAY.keys()) - set(STATE_NARRATIVE_DISPLAY.keys())
        assert not missing, (
            f"States in STATE_DISPLAY but missing from STATE_NARRATIVE_DISPLAY: "
            f"{sorted(missing)}"
        )

    def test_state_display_values_not_empty(self):
        """Display values should be non-empty strings."""
        for state, display in STATE_DISPLAY.items():
            assert display and isinstance(display, str), (
                f"STATE_DISPLAY['{state}'] has empty or non-string value: {display!r}"
            )
        for state, display in STATE_NARRATIVE_DISPLAY.items():
            assert display and isinstance(display, str), (
                f"STATE_NARRATIVE_DISPLAY['{state}'] has empty or non-string value: "
                f"{display!r}"
            )


# ============================================================================
# Test 7: Free actions list consistency
# ============================================================================

class TestFreeActionsConsistency:
    """The free_actions lists in executor must be consistent."""

    def test_executor_free_actions_lists_match(self):
        """The free_actions lists in executor.py (execute) and meta_executor.py
        (_execute_post_objection) must contain the same entries."""
        # Scan both executor.py and meta_executor.py (R13B split)
        commands_dir = os.path.join(
            os.path.dirname(__file__), '..', 'backend', 'commands'
        )
        action_lists = []
        pattern = re.compile(
            r'free_actions\s*=\s*\[(.*?)\]',
            re.DOTALL,
        )
        for filename in ('executor.py', 'meta_executor.py'):
            path = os.path.normpath(os.path.join(commands_dir, filename))
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            matches = pattern.findall(content)
            for match_content in matches:
                # Skip defiance_free_actions (small 2-item lists)
                if match_content.count('"') <= 6:
                    continue
                actions = set(re.findall(r'"(\w+)"', match_content))
                action_lists.append(actions)

        assert len(action_lists) >= 2, (
            f"Expected at least 2 free_actions lists across executor+meta_executor, found {len(action_lists)}"
        )

        # All free_actions lists should be identical
        for i in range(1, len(action_lists)):
            diff_a = action_lists[0] - action_lists[i]
            diff_b = action_lists[i] - action_lists[0]
            assert not diff_a and not diff_b, (
                f"free_actions list mismatch: "
                f"list[0] has extra {sorted(diff_a)}, "
                f"list[{i}] has extra {sorted(diff_b)}. "
                f"Both lists must stay in sync."
            )
