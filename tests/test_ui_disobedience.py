"""
UI Test Scenarios for Hold/Wait/Disobedience System

This file provides test scenarios for manually testing the disobedience system
through the UI. Run these tests by starting the game and issuing the commands.

Run with: python tests/test_ui_disobedience.py

This will print test scenarios and expected outcomes for manual verification.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.commands.parser import CommandParser


def create_test_world():
    """Create a fresh world state for testing."""
    world = WorldState(player_nation="France")
    return world


def test_hold_action():
    """Test that 'hold' works as an alias for defend."""
    print("\n" + "=" * 70)
    print("TEST: HOLD ACTION (Alias for Defend)")
    print("=" * 70)

    world = create_test_world()
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)

    # Get initial state
    ney = world.marshals.get("Ney")
    initial_stance = getattr(ney, 'stance', None)
    initial_actions = world.actions_remaining

    print(f"\nInitial State:")
    print(f"  - Ney's stance: {initial_stance.value if initial_stance else 'None'}")
    print(f"  - Actions remaining: {initial_actions}")

    # Parse and execute hold command
    parsed = parser.parse("Ney, hold")
    print(f"\nParsed command: {parsed}")

    if parsed.get("success"):
        result = executor.execute(parsed, {"world": world})
        print(f"\nExecution result:")
        print(f"  - Success: {result.get('success')}")
        print(f"  - Message: {result.get('message')}")

        # Check final state
        final_stance = getattr(ney, 'stance', None)
        final_actions = world.actions_remaining

        print(f"\nFinal State:")
        print(f"  - Ney's stance: {final_stance.value if final_stance else 'None'}")
        print(f"  - Actions remaining: {final_actions}")

        # Verify
        if final_stance and final_stance.value == 'defensive':
            print("\n[PASS] PASS: Hold correctly changed Ney to defensive stance")
        else:
            print("\n[FAIL] FAIL: Hold did not change stance to defensive")

        if initial_actions - final_actions >= 1:
            print("[PASS] PASS: Hold consumed an action")
        else:
            print("[FAIL] FAIL: Hold should consume an action")
    else:
        print(f"\n[FAIL] FAIL: Command parsing failed - {parsed.get('error')}")


def test_wait_action():
    """Test that 'wait' is a free action with no state change."""
    print("\n" + "=" * 70)
    print("TEST: WAIT ACTION (Free Action)")
    print("=" * 70)

    world = create_test_world()
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)

    # Get initial state
    ney = world.marshals.get("Ney")
    initial_stance = getattr(ney, 'stance', None)
    initial_actions = world.actions_remaining
    initial_location = ney.location

    print(f"\nInitial State:")
    print(f"  - Ney's stance: {initial_stance.value if initial_stance else 'None'}")
    print(f"  - Ney's location: {initial_location}")
    print(f"  - Actions remaining: {initial_actions}")

    # Parse and execute wait command
    parsed = parser.parse("Ney, wait")
    print(f"\nParsed command: {parsed}")

    if parsed.get("success"):
        result = executor.execute(parsed, {"world": world})
        print(f"\nExecution result:")
        print(f"  - Success: {result.get('success')}")
        print(f"  - Message: {result.get('message')}")
        print(f"  - Action cost: {result.get('variable_action_cost', 'not specified')}")

        # Check final state
        final_stance = getattr(ney, 'stance', None)
        final_actions = world.actions_remaining
        final_location = ney.location

        print(f"\nFinal State:")
        print(f"  - Ney's stance: {final_stance.value if final_stance else 'None'}")
        print(f"  - Ney's location: {final_location}")
        print(f"  - Actions remaining: {final_actions}")

        # Verify - stance unchanged
        if initial_stance == final_stance:
            print("\n[PASS] PASS: Wait did not change stance")
        else:
            print(f"\n[FAIL] FAIL: Wait changed stance from {initial_stance} to {final_stance}")

        # Verify - location unchanged
        if initial_location == final_location:
            print("[PASS] PASS: Wait did not change location")
        else:
            print(f"[FAIL] FAIL: Wait changed location from {initial_location} to {final_location}")

        # Verify - actions unchanged (free action)
        if initial_actions == final_actions:
            print("[PASS] PASS: Wait is FREE (no action cost)")
        else:
            print(f"[FAIL] FAIL: Wait consumed actions ({initial_actions} -> {final_actions})")
    else:
        print(f"\n[FAIL] FAIL: Command parsing failed - {parsed.get('error')}")


def test_ney_defend_objection():
    """Test that Ney objects to defend orders (aggressive personality)."""
    print("\n" + "=" * 70)
    print("TEST: NEY DEFEND OBJECTION (Aggressive Personality)")
    print("=" * 70)

    world = create_test_world()
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)

    ney = world.marshals.get("Ney")
    print(f"\nMarshal: Ney (Aggressive)")
    print(f"Trust: {getattr(ney, 'trust', 75)}")
    print(f"Expected: Major objection (severity 0.60)")

    # Parse defend command
    parsed = parser.parse("Ney, defend")

    if parsed.get("success"):
        result = executor.execute(parsed, {"world": world})

        if result.get('objection'):
            objection = result['objection']
            print(f"\n[PASS] OBJECTION TRIGGERED")
            print(f"  - Type: {objection.get('type')}")
            print(f"  - Severity: {objection.get('severity')}")
            print(f"  - Message: {objection.get('message')}")
            print(f"  - Options: {objection.get('options', [])}")

            if objection.get('type') == 'major_objection':
                print("\n[PASS] PASS: Major objection as expected")
            else:
                print(f"\n[INFO] INFO: Got {objection.get('type')} instead of major_objection")
        else:
            print(f"\n[INFO] No objection triggered")
            print(f"  - This can happen if severity + variance < 0.50")
            print(f"  - Result: {result.get('message')}")
    else:
        print(f"\n[FAIL] FAIL: Command parsing failed - {parsed.get('error')}")


def test_ney_hold_objection():
    """Test that Ney has MILD objection to hold (less than defend)."""
    print("\n" + "=" * 70)
    print("TEST: NEY HOLD OBJECTION (Milder than Defend)")
    print("=" * 70)

    world = create_test_world()
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)

    ney = world.marshals.get("Ney")
    print(f"\nMarshal: Ney (Aggressive)")
    print(f"Trust: {getattr(ney, 'trust', 75)}")
    print(f"Expected: Mild objection (severity 0.45)")

    # Parse hold command
    parsed = parser.parse("Ney, hold")

    if parsed.get("success"):
        result = executor.execute(parsed, {"world": world})

        if result.get('objection'):
            objection = result['objection']
            print(f"\n[PASS] OBJECTION TRIGGERED")
            print(f"  - Type: {objection.get('type')}")
            print(f"  - Severity: {objection.get('severity')}")
            print(f"  - Message: {objection.get('message')}")

            if objection.get('type') == 'mild_objection':
                print("\n[PASS] PASS: Mild objection as expected (less severe than defend)")
            elif objection.get('type') == 'major_objection':
                print("\n[INFO] INFO: Got major objection - variance may have pushed it over 0.50")
            else:
                print(f"\n[INFO] INFO: Got {objection.get('type')}")
        else:
            print(f"\n[INFO] No objection triggered")
            print(f"  - Base severity 0.45 may have been reduced by high trust")
            print(f"  - Result: {result.get('message')}")
    else:
        print(f"\n[FAIL] FAIL: Command parsing failed - {parsed.get('error')}")


def test_ney_wait_objection():
    """Test that Ney objects to wait orders."""
    print("\n" + "=" * 70)
    print("TEST: NEY WAIT OBJECTION")
    print("=" * 70)

    world = create_test_world()
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)

    ney = world.marshals.get("Ney")
    print(f"\nMarshal: Ney (Aggressive)")
    print(f"Trust: {getattr(ney, 'trust', 75)}")
    print(f"Expected: Major objection (severity 0.50)")

    # Parse wait command
    parsed = parser.parse("Ney, wait")

    if parsed.get("success"):
        result = executor.execute(parsed, {"world": world})

        if result.get('objection'):
            objection = result['objection']
            print(f"\n[PASS] OBJECTION TRIGGERED")
            print(f"  - Type: {objection.get('type')}")
            print(f"  - Severity: {objection.get('severity')}")
            print(f"  - Message: {objection.get('message')}")
        else:
            print(f"\n[INFO] No objection triggered")
            print(f"  - This can happen with high trust reducing severity")
            print(f"  - Result: {result.get('message')}")
    else:
        print(f"\n[FAIL] FAIL: Command parsing failed - {parsed.get('error')}")


def test_davout_no_defend_objection():
    """Test that Davout (cautious) does NOT object to defend."""
    print("\n" + "=" * 70)
    print("TEST: DAVOUT DEFEND - NO OBJECTION (Cautious Personality)")
    print("=" * 70)

    world = create_test_world()
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)

    davout = world.marshals.get("Davout")
    print(f"\nMarshal: Davout (Cautious)")
    print(f"Trust: {getattr(davout, 'trust', 85)}")
    print(f"Expected: No objection (cautious marshals like defense)")

    # Parse defend command
    parsed = parser.parse("Davout, defend")

    if parsed.get("success"):
        result = executor.execute(parsed, {"world": world})

        if result.get('objection'):
            objection = result['objection']
            print(f"\n[FAIL] UNEXPECTED OBJECTION")
            print(f"  - Type: {objection.get('type')}")
            print(f"  - Davout should NOT object to defend")
        else:
            print(f"\n[PASS] PASS: No objection - Davout is happy to defend")
            print(f"  - Result: {result.get('message')}")
    else:
        print(f"\n[FAIL] FAIL: Command parsing failed - {parsed.get('error')}")


def test_grouchy_always_obeys():
    """Test that Grouchy (literal) follows orders without objection."""
    print("\n" + "=" * 70)
    print("TEST: GROUCHY OBEDIENCE (Literal Personality)")
    print("=" * 70)

    world = create_test_world()
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)

    grouchy = world.marshals.get("Grouchy")
    print(f"\nMarshal: Grouchy (Literal)")
    print(f"Trust: {getattr(grouchy, 'trust', 65)}")
    print(f"Expected: No objection to any standard order")

    # Test multiple commands
    test_commands = [
        "Grouchy, defend",
        "Grouchy, wait",
        "Grouchy, move to Belgium",
    ]

    for cmd in test_commands:
        parsed = parser.parse(cmd)
        if parsed.get("success"):
            result = executor.execute(parsed, {"world": world})
            objection = result.get('objection')

            if objection:
                print(f"\n[FAIL] '{cmd}' -> Unexpected objection: {objection.get('type')}")
            else:
                print(f"\n[PASS] '{cmd}' -> Grouchy obeys")
        else:
            print(f"\n[INFO] '{cmd}' -> Parse failed: {parsed.get('error')}")


def test_objection_response_flow():
    """Test the full objection response flow (trust/insist/compromise)."""
    print("\n" + "=" * 70)
    print("TEST: OBJECTION RESPONSE FLOW")
    print("=" * 70)

    world = create_test_world()
    executor = CommandExecutor()
    parser = CommandParser(use_real_llm=False)

    ney = world.marshals.get("Ney")

    # Lower Ney's trust to make objection more likely
    if hasattr(ney.trust, 'set'):
        ney.trust.set(40)
    else:
        ney.trust._value = 40  # Direct attribute access for Trust class
    print(f"\nSetup: Lowered Ney's trust to 40 to ensure objection")

    # Issue defend command to trigger objection
    parsed = parser.parse("Ney, defend")

    if parsed.get("success"):
        result = executor.execute(parsed, {"world": world})

        if result.get('objection'):
            objection = result['objection']
            print(f"\nObjection triggered: {objection.get('type')}")
            print(f"Severity: {objection.get('severity')}")

            if objection.get('type') == 'major_objection':
                print(f"\nAvailable choices:")
                options = objection.get('options', [])
                for opt in options:
                    print(f"  - {opt}")

                # Test handling a response
                print(f"\nTo test responses in UI, issue commands like:")
                print(f"  - 'trust' to accept marshal's alternative")
                print(f"  - 'insist' to force original order")
                print(f"  - 'compromise' for middle ground")
            else:
                print(f"\nMild objection - auto-resolved")
        else:
            print(f"\n[INFO] No objection triggered even with low trust")
    else:
        print(f"\n[FAIL] Parse failed: {parsed.get('error')}")


def print_manual_test_scenarios():
    """Print scenarios for manual UI testing."""
    print("\n" + "=" * 70)
    print("MANUAL UI TEST SCENARIOS")
    print("=" * 70)

    scenarios = """
+----------------------------------------------------------------------+
|  SCENARIO 1: Hold vs Defend vs Wait                                  |
+----------------------------------------------------------------------+
|  Commands to try:                                                    |
|    > "Ney, hold"       (Should cost 1 action, change to defensive)   |
|    > "Ney, hold the line" (Same effect)                              |
|    > "Davout, defend"  (Should cost 1 action, change to defensive)   |
|    > "Grouchy, wait"   (Should be FREE, no state change)             |
|                                                                      |
|  Expected: Hold and defend cost actions, wait is free                |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
|  SCENARIO 2: Aggressive Marshal Objections                           |
+----------------------------------------------------------------------+
|  Commands to try:                                                    |
|    > "Ney, defend"     (Major objection ~0.60)                       |
|    > "Ney, hold"       (Mild objection ~0.45)                        |
|    > "Ney, wait"       (Major objection ~0.50)                       |
|    > "Ney, fortify"    (Major objection ~0.55)                       |
|    > "Ney, retreat"    (Strong objection ~0.70)                      |
|                                                                      |
|  Expected: Ney should object to defensive orders                     |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
|  SCENARIO 3: Cautious Marshal Objections                             |
+----------------------------------------------------------------------+
|  Setup: Move Davout next to a larger enemy force                     |
|                                                                      |
|  Commands to try:                                                    |
|    > "Davout, attack Wellington"  (Should object if outnumbered)     |
|    > "Davout, defend"            (Should NOT object)                 |
|    > "Davout, adopt aggressive stance" (Should object)               |
|                                                                      |
|  Expected: Davout objects to risky attacks, not defense              |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
|  SCENARIO 4: Literal Marshal (No Objections)                         |
+----------------------------------------------------------------------+
|  Commands to try:                                                    |
|    > "Grouchy, defend"           (Should NOT object)                 |
|    > "Grouchy, wait"             (Should NOT object)                 |
|    > "Grouchy, attack Wellington" (Should NOT object)                |
|    > "Grouchy, retreat"          (Should NOT object)                 |
|                                                                      |
|  Expected: Grouchy follows orders literally, rarely objects          |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
|  SCENARIO 5: Objection Response Choices                              |
+----------------------------------------------------------------------+
|  Setup: Issue an order that triggers a major objection               |
|    > "Ney, defend"                                                   |
|                                                                      |
|  When objection appears, test each response:                         |
|    > 'trust'      (Accept marshal's alternative, +12 trust)          |
|    > 'insist'     (Force order, -10 trust if obey, -15 if disobey)   |
|    > 'compromise' (Middle ground action, +3 trust)                   |
|                                                                      |
|  Expected: Trust affects future objection severity                   |
+----------------------------------------------------------------------+

+----------------------------------------------------------------------+
|  SCENARIO 6: Action Economy with Wait                                |
+----------------------------------------------------------------------+
|  Start of turn: Should have 4 actions                                |
|                                                                      |
|  Commands:                                                           |
|    > "Ney, attack Wellington"    (1 action)                          |
|    > "Davout, move to Belgium"   (1 action)                          |
|    > "Grouchy, wait"             (FREE - still 2 actions left!)      |
|    > "Ney, wait"                 (FREE - still 2 actions left!)      |
|    > "Davout, attack"            (1 action - now 1 left)             |
|                                                                      |
|  Expected: Wait never consumes actions, use it to skip marshals      |
+----------------------------------------------------------------------+
"""
    print(scenarios)


if __name__ == "__main__":
    print("=" * 70)
    print("DISOBEDIENCE SYSTEM UI TEST SUITE")
    print("=" * 70)
    print("\nThis test file provides both automated checks and manual test scenarios.")
    print("Run these tests to verify hold/wait/disobedience functionality.\n")

    # Run automated tests
    test_hold_action()
    test_wait_action()
    test_ney_defend_objection()
    test_ney_hold_objection()
    test_ney_wait_objection()
    test_davout_no_defend_objection()
    test_grouchy_always_obeys()
    test_objection_response_flow()

    # Print manual test scenarios
    print_manual_test_scenarios()

    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\nFor full UI testing, start the game server with:")
    print("  python backend/main.py")
    print("\nThen try the manual test scenarios above in the game UI.")
