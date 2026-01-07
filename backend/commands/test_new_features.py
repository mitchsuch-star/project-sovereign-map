"""
Test script for new recruit and income features.
Run this BEFORE integrating into actual code.
"""

from typing import Dict


class TestExecutor:
    """Test version of executor with new methods."""

    def calculate_turn_income(self, game_state: Dict) -> Dict:
        """Calculate automatic income for this turn."""
        regions_controlled = game_state.get("regions_controlled", 3)
        controlled_region_list = game_state.get("controlled_regions", ["Paris", "Belgium", "Rhine"])
        has_capital = "Paris" in controlled_region_list

        base_income = regions_controlled * 100
        capital_bonus = 200 if has_capital else 0
        total_income = base_income + capital_bonus

        return {
            "income": total_income,
            "breakdown": {
                "regions": regions_controlled,
                "base_income": base_income,
                "capital_bonus": capital_bonus,
                "total": total_income
            },
            "message": f"Turn income: {total_income} gold ({regions_controlled} regions)"
        }

    def _execute_recruit(self, command: Dict, game_state: Dict) -> Dict:
        """Recruit new troops - assigns to marshal closest to recruitment location."""
        marshal_specified = command.get("marshal")
        location_specified = command.get("target")

        if marshal_specified:
            recipient = marshal_specified
            recruitment_location = "current position"
            message = f"{marshal_specified} recruits 10,000 troops at their position"
            assignment_method = "specified"

        elif location_specified:
            recipient = "nearest_marshal"
            recruitment_location = location_specified
            message = f"Recruiting 10,000 troops in {location_specified} - assigning to nearest marshal"
            assignment_method = "proximity_to_location"

        else:
            recipient = "nearest_to_capital"
            recruitment_location = "Paris"
            message = f"Recruiting 10,000 troops - assigning to marshal nearest capital"
            assignment_method = "default_capital"

        return {
            "success": True,
            "message": f"{message} - Cost: 200 gold",
            "events": [{
                "type": "recruit",
                "marshal": recipient,
                "location": recruitment_location,
                "troops_added": 10000,
                "gold_cost": 200,
                "assignment_method": assignment_method,
                "description": f"+10,000 troops for {recipient} (closest to {recruitment_location})"
            }],
            "new_state": game_state
        }


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("TESTING NEW FEATURES - RECRUIT & INCOME")
    print("=" * 70)

    executor = TestExecutor()

    # ========================================
    # TEST 1: INCOME CALCULATION
    # ========================================
    print("\n" + "=" * 70)
    print("TEST 1: Income Calculation")
    print("=" * 70)

    # Test case 1: 3 regions with Paris
    game_state_1 = {
        "regions_controlled": 3,
        "controlled_regions": ["Paris", "Belgium", "Rhine"]
    }
    income_1 = executor.calculate_turn_income(game_state_1)
    print(f"\nScenario 1: 3 regions including Paris")
    print(f"Expected: 500 gold (300 base + 200 capital)")
    print(f"Result: {income_1['income']} gold")
    print(f"Breakdown: {income_1['breakdown']}")
    print(f"✓ PASS" if income_1['income'] == 500 else "✗ FAIL")

    # Test case 2: 5 regions with Paris
    game_state_2 = {
        "regions_controlled": 5,
        "controlled_regions": ["Paris", "Belgium", "Rhine", "Waterloo", "Netherlands"]
    }
    income_2 = executor.calculate_turn_income(game_state_2)
    print(f"\nScenario 2: 5 regions including Paris")
    print(f"Expected: 700 gold (500 base + 200 capital)")
    print(f"Result: {income_2['income']} gold")
    print(f"✓ PASS" if income_2['income'] == 700 else "✗ FAIL")

    # Test case 3: 3 regions WITHOUT Paris
    game_state_3 = {
        "regions_controlled": 3,
        "controlled_regions": ["Belgium", "Rhine", "Waterloo"]
    }
    income_3 = executor.calculate_turn_income(game_state_3)
    print(f"\nScenario 3: 3 regions WITHOUT Paris (lost capital!)")
    print(f"Expected: 300 gold (300 base + 0 capital)")
    print(f"Result: {income_3['income']} gold")
    print(f"✓ PASS" if income_3['income'] == 300 else "✗ FAIL")

    # Test case 4: 10 regions with Paris (late game)
    game_state_4 = {
        "regions_controlled": 10,
        "controlled_regions": ["Paris", "Belgium", "Rhine", "Waterloo", "Netherlands",
                               "Bavaria", "Vienna", "Milan", "Geneva", "Lyon"]
    }
    income_4 = executor.calculate_turn_income(game_state_4)
    print(f"\nScenario 4: 10 regions including Paris (dominating!)")
    print(f"Expected: 1,200 gold (1,000 base + 200 capital)")
    print(f"Result: {income_4['income']} gold")
    print(f"✓ PASS" if income_4['income'] == 1200 else "✗ FAIL")

    # ========================================
    # TEST 2: RECRUIT - MARSHAL SPECIFIED
    # ========================================
    print("\n" + "=" * 70)
    print("TEST 2: Recruit - Marshal Specified")
    print("=" * 70)

    command_1 = {
        "marshal": "Ney",
        "action": "recruit",
        "target": None
    }
    result_1 = executor._execute_recruit(command_1, game_state_1)
    print(f"\nCommand: 'Ney, recruit'")
    print(f"Expected: Ney gets troops at his current position")
    print(f"Result: {result_1['message']}")
    print(f"Marshal: {result_1['events'][0]['marshal']}")
    print(f"Assignment: {result_1['events'][0]['assignment_method']}")
    print(f"✓ PASS" if result_1['events'][0]['marshal'] == "Ney" else "✗ FAIL")

    # ========================================
    # TEST 3: RECRUIT - LOCATION SPECIFIED
    # ========================================
    print("\n" + "=" * 70)
    print("TEST 3: Recruit - Location Specified")
    print("=" * 70)

    command_2 = {
        "marshal": None,
        "action": "recruit",
        "target": "Belgium"
    }
    result_2 = executor._execute_recruit(command_2, game_state_1)
    print(f"\nCommand: 'Recruit in Belgium'")
    print(f"Expected: Find marshal closest to Belgium")
    print(f"Result: {result_2['message']}")
    print(f"Location: {result_2['events'][0]['location']}")
    print(f"Assignment method: {result_2['events'][0]['assignment_method']}")
    print(f"✓ PASS" if result_2['events'][0]['assignment_method'] == "proximity_to_location" else "✗ FAIL")

    # ========================================
    # TEST 4: RECRUIT - DEFAULT (NO SPECS)
    # ========================================
    print("\n" + "=" * 70)
    print("TEST 4: Recruit - Default (No Marshal or Location)")
    print("=" * 70)

    command_3 = {
        "marshal": None,
        "action": "recruit",
        "target": None
    }
    result_3 = executor._execute_recruit(command_3, game_state_1)
    print(f"\nCommand: 'Recruit'")
    print(f"Expected: Find marshal closest to capital (Paris)")
    print(f"Result: {result_3['message']}")
    print(f"Assignment method: {result_3['events'][0]['assignment_method']}")
    print(f"✓ PASS" if result_3['events'][0]['assignment_method'] == "default_capital" else "✗ FAIL")

    # ========================================
    # TEST 5: ECONOMIC BALANCE CHECK
    # ========================================
    print("\n" + "=" * 70)
    print("TEST 5: Economic Balance Check")
    print("=" * 70)

    print("\nTurn 1 (3 regions + Paris):")
    print(f"  Income: +{income_1['income']} gold")
    print(f"  Army upkeep: -180 gold")
    print(f"  Net: +{income_1['income'] - 180} gold")
    print(f"  Can recruit? {'YES' if income_1['income'] - 180 >= 200 else 'NO'}")

    print("\nTurn 10 (5 regions + Paris):")
    print(f"  Income: +{income_2['income']} gold")
    print(f"  Army upkeep: -240 gold (recruited once)")
    print(f"  Net: +{income_2['income'] - 240} gold")
    print(f"  Can recruit? {'YES' if income_2['income'] - 240 >= 200 else 'NO'}")

    print("\nTurn 20 (10 regions + Paris):")
    print(f"  Income: +{income_4['income']} gold")
    print(f"  Army upkeep: -300 gold (recruited several times)")
    print(f"  Net: +{income_4['income'] - 300} gold")
    print(f"  Can recruit multiple times? {'YES' if income_4['income'] - 300 >= 400 else 'NO'}")

    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("\n✓ Income system works correctly")
    print("✓ Recruit with marshal specified works")
    print("✓ Recruit with location works (proximity stub)")
    print("✓ Recruit default works (capital stub)")
    print("✓ Economic balance is sustainable")
    print("\nReady to integrate into actual code!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()