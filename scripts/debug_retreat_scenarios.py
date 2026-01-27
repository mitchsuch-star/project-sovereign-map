"""
Debug Script: Retreat System Testing

This script provides functions to set up and test Phase 2.9 retreat scenarios:
- Moving enemy units (Wellington, Blucher) to specific positions
- Testing ally cover system
- Testing smart retreat destinations
- Testing AI exposed target bonus

Run with: python scripts/debug_retreat_scenarios.py

Or import functions for interactive testing:
    from scripts.debug_retreat_scenarios import *
    world, executor = setup_game()
    move_enemy("Wellington", "Belgium")
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal, Stance
from backend.commands.executor import CommandExecutor
from backend.ai.enemy_ai import EnemyAI


def setup_game():
    """Initialize a fresh game state."""
    world = WorldState(player_nation="France")
    executor = CommandExecutor()
    return world, executor


def move_enemy(world: WorldState, marshal_name: str, region: str) -> str:
    """
    Move any marshal (including enemies) to a region.

    Args:
        world: WorldState instance
        marshal_name: "Wellington", "Blucher", "Ney", etc.
        region: Target region name

    Returns:
        Result message
    """
    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return f"Marshal '{marshal_name}' not found. Available: {list(world.marshals.keys())}"

    region_obj = world.get_region(region)
    if not region_obj:
        return f"Region '{region}' not found. Available: {list(world.regions.keys())}"

    old_loc = marshal.location
    marshal.location = region
    return f"Moved {marshal_name}: {old_loc} -> {region}"


def set_retreated(world: WorldState, marshal_name: str, value: bool = True) -> str:
    """Set retreated_this_turn flag on a marshal."""
    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return f"Marshal '{marshal_name}' not found"

    marshal.retreated_this_turn = value
    return f"{marshal_name}.retreated_this_turn = {value}"


def set_morale(world: WorldState, marshal_name: str, morale: int) -> str:
    """Set morale on a marshal (0-100)."""
    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return f"Marshal '{marshal_name}' not found"

    marshal.morale = max(0, min(100, morale))
    return f"{marshal_name}.morale = {marshal.morale}"


def set_strength(world: WorldState, marshal_name: str, strength: int) -> str:
    """Set troop strength on a marshal."""
    marshal = world.get_marshal(marshal_name)
    if not marshal:
        return f"Marshal '{marshal_name}' not found"

    marshal.strength = max(0, strength)
    return f"{marshal_name}.strength = {marshal.strength:,}"


def show_all_marshals(world: WorldState) -> None:
    """Print all marshals and their locations."""
    print("\n=== ALL MARSHALS ===")
    print(f"{'Name':<12} {'Nation':<10} {'Location':<15} {'Strength':>10} {'Morale':>7} {'Retreated':>10}")
    print("-" * 70)
    for name, m in sorted(world.marshals.items()):
        retreated = "YES" if getattr(m, 'retreated_this_turn', False) else "no"
        print(f"{name:<12} {m.nation:<10} {m.location:<15} {m.strength:>10,} {m.morale:>6}% {retreated:>10}")


def show_region_occupants(world: WorldState, region: str = None) -> None:
    """Show who is in a region (or all regions if not specified)."""
    if region:
        regions = [region]
    else:
        regions = list(world.regions.keys())

    print("\n=== REGION OCCUPANTS ===")
    for r in regions:
        occupants = world.get_marshals_in_region(r)
        region_obj = world.get_region(r)
        controller = region_obj.controller if region_obj else "Unknown"
        if occupants:
            names = [f"{m.name} ({m.nation})" for m in occupants]
            print(f"{r:<15} [{controller:>8}]: {', '.join(names)}")
        elif region:
            print(f"{r:<15} [{controller:>8}]: (empty)")


def test_retreat_destination(world: WorldState, marshal_name: str, attacker_location: str = None) -> str:
    """Test where a marshal would retreat to."""
    dest = world.get_safe_retreat_destination(marshal_name, attacker_location)
    if dest:
        if attacker_location:
            dist = world.get_distance(dest, attacker_location)
            return f"{marshal_name} would retreat to: {dest} (distance {dist} from attacker at {attacker_location})"
        return f"{marshal_name} would retreat to: {dest}"
    else:
        return f"{marshal_name} is ENCIRCLED - no safe retreat!"


def test_ally_cover(world: WorldState, target_name: str) -> str:
    """Test if a marshal has ally cover."""
    target = world.get_marshal(target_name)
    if not target:
        return f"Marshal '{target_name}' not found"

    if not getattr(target, 'retreated_this_turn', False):
        return f"{target_name} did NOT retreat this turn - no cover check needed"

    covering_candidates = [
        m for m in world.marshals.values()
        if m.location == target.location
        and m.nation == target.nation
        and m.name != target.name
        and m.strength > 0
        and not getattr(m, 'retreated_this_turn', False)
    ]

    if covering_candidates:
        cover = max(covering_candidates, key=lambda m: m.strength)
        return f"{target_name} is COVERED by {cover.name} ({cover.strength:,} troops)"
    else:
        return f"{target_name} is EXPOSED - no ally to cover!"


def test_ai_target_bonus(world: WorldState, target_name: str) -> dict:
    """Test AI targeting bonus for a marshal."""
    executor = CommandExecutor()
    ai = EnemyAI(executor)

    target = world.get_marshal(target_name)
    if not target:
        return {"error": f"Marshal '{target_name}' not found"}

    base_ratio = 1.0
    effective = ai._evaluate_target_ratio(base_ratio, target, world)

    return {
        "target": target_name,
        "base_ratio": base_ratio,
        "effective_ratio": effective,
        "bonus": f"+{(effective - base_ratio) * 100:.0f}%",
        "retreated": getattr(target, 'retreated_this_turn', False),
        "has_cover": test_ally_cover(world, target_name)
    }


# ════════════════════════════════════════════════════════════════════════════
# SCENARIO SETUPS - Pre-configured test scenarios
# ════════════════════════════════════════════════════════════════════════════

def scenario_ally_cover():
    """
    Scenario: Wellington retreated, Blucher covers.

    Setup: Both enemies in Netherlands, Wellington just retreated.
    Expected: Attacking Wellington should hit Blucher instead.
    """
    print("\n" + "=" * 60)
    print("SCENARIO: Ally Cover System")
    print("=" * 60)

    world, executor = setup_game()

    # Setup positions
    print(move_enemy(world, "Wellington", "Netherlands"))
    print(move_enemy(world, "Blucher", "Netherlands"))
    print(set_retreated(world, "Wellington", True))
    print(set_retreated(world, "Blucher", False))

    # Put attacker adjacent
    print(move_enemy(world, "Ney", "Belgium"))

    show_all_marshals(world)
    show_region_occupants(world, "Netherlands")

    print("\n--- COVER CHECK ---")
    print(test_ally_cover(world, "Wellington"))

    print("\n--- AI TARGET BONUS ---")
    bonus = test_ai_target_bonus(world, "Wellington")
    print(f"Target: {bonus['target']}")
    print(f"Retreated: {bonus['retreated']}")
    print(f"Cover: {bonus['has_cover']}")
    print(f"Effective ratio: {bonus['effective_ratio']} ({bonus['bonus']} from base)")

    return world, executor


def scenario_exposed_target():
    """
    Scenario: Wellington retreated and is ALONE (exposed).

    Setup: Wellington in Netherlands alone, just retreated.
    Expected: AI gets +30% targeting bonus.
    """
    print("\n" + "=" * 60)
    print("SCENARIO: Exposed Retreating Target (+30% AI bonus)")
    print("=" * 60)

    world, executor = setup_game()

    # Setup: Wellington alone and retreated
    print(move_enemy(world, "Wellington", "Netherlands"))
    print(move_enemy(world, "Blucher", "Waterloo"))  # Different region
    print(set_retreated(world, "Wellington", True))

    show_all_marshals(world)

    print("\n--- COVER CHECK ---")
    print(test_ally_cover(world, "Wellington"))

    print("\n--- AI TARGET BONUS ---")
    bonus = test_ai_target_bonus(world, "Wellington")
    print(f"Target: {bonus['target']}")
    print(f"Retreated: {bonus['retreated']}")
    print(f"Effective ratio: {bonus['effective_ratio']} ({bonus['bonus']} from base)")

    # Should be >= 1.30
    if bonus['effective_ratio'] >= 1.30:
        print("PASS: Exposed bonus applied correctly")
    else:
        print("FAIL: Expected at least +30% bonus")

    return world, executor


def scenario_smart_retreat_priority():
    """
    Scenario: Test retreat destination priority system.

    Tests: Friendly with ally > Friendly empty > Enemy unoccupied > Encircled
    """
    print("\n" + "=" * 60)
    print("SCENARIO: Smart Retreat Destination Priority")
    print("=" * 60)

    world, executor = setup_game()

    # Setup: Ney at Belgium, Davout at Paris (ally)
    print(move_enemy(world, "Ney", "Belgium"))
    print(move_enemy(world, "Davout", "Paris"))

    show_all_marshals(world)

    print("\n--- RETREAT DESTINATION ---")
    print(test_retreat_destination(world, "Ney"))

    # Now move Davout away - Ney should find different destination
    print("\n--- After moving Davout away ---")
    print(move_enemy(world, "Davout", "Lyon"))
    print(test_retreat_destination(world, "Ney"))

    return world, executor


def scenario_encirclement():
    """
    Scenario: Test encirclement detection.

    Setup: Ney surrounded by enemies in all adjacent regions.
    Expected: get_safe_retreat_destination returns None (army breaks).
    """
    print("\n" + "=" * 60)
    print("SCENARIO: Encirclement (No Safe Retreat)")
    print("=" * 60)

    world, executor = setup_game()

    # Put Ney somewhere
    print(move_enemy(world, "Ney", "Belgium"))

    # Get adjacent regions
    belgium = world.get_region("Belgium")
    print(f"\nBelgium adjacent to: {belgium.adjacent_regions}")

    # Put enemies in adjacent regions (we only have 2 enemies in the test map)
    adjacent = list(belgium.adjacent_regions)
    if len(adjacent) >= 1:
        print(move_enemy(world, "Wellington", adjacent[0]))
    if len(adjacent) >= 2:
        print(move_enemy(world, "Blucher", adjacent[1]))

    show_region_occupants(world)

    print("\n--- RETREAT DESTINATION ---")
    print(test_retreat_destination(world, "Ney"))

    return world, executor


def scenario_forced_retreat_combat():
    """
    Scenario: Test forced retreat triggered by low morale in combat.

    Setup: Wellington with 20% morale attacked by Ney.
    Expected: Combat triggers forced retreat, retreated_this_turn = True.
    """
    print("\n" + "=" * 60)
    print("SCENARIO: Forced Retreat from Combat (Morale <= 25%)")
    print("=" * 60)

    world, executor = setup_game()
    game_state = {"world": world}

    # Setup: Put them adjacent
    print(move_enemy(world, "Ney", "Belgium"))
    print(move_enemy(world, "Wellington", "Netherlands"))
    print(set_morale(world, "Wellington", 20))  # Below 25% threshold
    print(set_strength(world, "Wellington", 30000))

    show_all_marshals(world)

    print("\n--- BEFORE ATTACK ---")
    print(f"Wellington.morale = {world.marshals['Wellington'].morale}")
    print(f"Wellington.retreated_this_turn = {world.marshals['Wellington'].retreated_this_turn}")

    # Execute attack
    print("\n--- ATTACK ---")
    command = {"action": "attack", "marshal": "Ney", "target": "Wellington"}
    result = executor.execute(command, game_state)
    print(f"Result: {result.get('success')}")
    print(f"Message: {result.get('message', '')[:200]}...")

    print("\n--- AFTER ATTACK ---")
    print(f"Wellington.location = {world.marshals['Wellington'].location}")
    print(f"Wellington.retreated_this_turn = {world.marshals['Wellington'].retreated_this_turn}")
    print(f"Wellington.morale = {world.marshals['Wellington'].morale}")

    return world, executor


def run_all_scenarios():
    """Run all test scenarios."""
    print("\n" + "=" * 70)
    print("RUNNING ALL RETREAT SYSTEM SCENARIOS")
    print("=" * 70)

    scenario_ally_cover()
    scenario_exposed_target()
    scenario_smart_retreat_priority()
    scenario_encirclement()
    scenario_forced_retreat_combat()

    print("\n" + "=" * 70)
    print("ALL SCENARIOS COMPLETE")
    print("=" * 70)


# ════════════════════════════════════════════════════════════════════════════
# INTERACTIVE MODE
# ════════════════════════════════════════════════════════════════════════════

def interactive():
    """
    Start interactive debug session.

    Commands:
        move <marshal> <region>     - Move any marshal
        retreat <marshal>           - Set retreated_this_turn
        morale <marshal> <value>    - Set morale
        strength <marshal> <value>  - Set strength
        show                        - Show all marshals
        region [name]               - Show region occupants
        test_retreat <marshal>      - Test retreat destination
        test_cover <marshal>        - Test ally cover
        test_bonus <marshal>        - Test AI targeting bonus
        scenario <name>             - Run a scenario
        quit                        - Exit
    """
    print("\n" + "=" * 60)
    print("INTERACTIVE DEBUG MODE")
    print("=" * 60)
    print("Type 'help' for commands, 'quit' to exit")

    world, executor = setup_game()

    while True:
        try:
            cmd = input("\ndebug> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0].lower()

        if action == "quit" or action == "exit":
            break
        elif action == "help":
            print(interactive.__doc__)
        elif action == "move" and len(parts) >= 3:
            print(move_enemy(world, parts[1], parts[2]))
        elif action == "retreat" and len(parts) >= 2:
            print(set_retreated(world, parts[1]))
        elif action == "morale" and len(parts) >= 3:
            print(set_morale(world, parts[1], int(parts[2])))
        elif action == "strength" and len(parts) >= 3:
            print(set_strength(world, parts[1], int(parts[2])))
        elif action == "show":
            show_all_marshals(world)
        elif action == "region":
            show_region_occupants(world, parts[1] if len(parts) > 1 else None)
        elif action == "test_retreat" and len(parts) >= 2:
            print(test_retreat_destination(world, parts[1]))
        elif action == "test_cover" and len(parts) >= 2:
            print(test_ally_cover(world, parts[1]))
        elif action == "test_bonus" and len(parts) >= 2:
            bonus = test_ai_target_bonus(world, parts[1])
            for k, v in bonus.items():
                print(f"  {k}: {v}")
        elif action == "scenario":
            if len(parts) < 2:
                print("Available: ally_cover, exposed, priority, encircle, combat")
            else:
                name = parts[1].lower()
                if name == "ally_cover":
                    world, executor = scenario_ally_cover()
                elif name == "exposed":
                    world, executor = scenario_exposed_target()
                elif name == "priority":
                    world, executor = scenario_smart_retreat_priority()
                elif name == "encircle":
                    world, executor = scenario_encirclement()
                elif name == "combat":
                    world, executor = scenario_forced_retreat_combat()
                else:
                    print(f"Unknown scenario: {name}")
        elif action == "reset":
            world, executor = setup_game()
            print("Game state reset")
        else:
            print(f"Unknown command: {action}. Type 'help' for commands.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "interactive" or arg == "-i":
            interactive()
        elif arg == "all":
            run_all_scenarios()
        elif arg == "ally_cover":
            scenario_ally_cover()
        elif arg == "exposed":
            scenario_exposed_target()
        elif arg == "priority":
            scenario_smart_retreat_priority()
        elif arg == "encircle":
            scenario_encirclement()
        elif arg == "combat":
            scenario_forced_retreat_combat()
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python debug_retreat_scenarios.py [all|interactive|<scenario>]")
    else:
        # Default: run all scenarios
        run_all_scenarios()
