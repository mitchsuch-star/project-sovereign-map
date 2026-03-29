"""
Vassal Executor — Vassal management commands (R13A)

Extracted from executor.py: invest_vassal, change_autonomy, make_vassal, release_vassal.
"""
from typing import Dict


class VassalExecutor:
    """Handles vassal management commands."""

    def __init__(self, parent_executor):
        self._executor = parent_executor

    def _execute_invest_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Invest in a vassal: 1 DP + 200g → +10 loyalty."""
        from backend.models.world_state import WorldState
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal to invest in."}

        from backend.game_logic.vassal import invest_in_vassal
        result = invest_in_vassal(world, target)
        if result.get("success"):
            result["new_state"] = game_state
        return result

    def _execute_change_autonomy(self, command: Dict, game_state: Dict) -> Dict:
        """Change vassal autonomy level."""
        from backend.models.world_state import WorldState
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal."}

        # Parse autonomy level from command
        from backend.game_logic.vassal import (
            AUTONOMY_PUPPET, AUTONOMY_SATELLITE, AUTONOMY_AUTONOMOUS,
            change_vassal_autonomy
        )
        raw_text = (command.get("raw_input") or command.get("original_command") or "").lower()
        if "puppet" in raw_text:
            new_level = AUTONOMY_PUPPET
        elif "satellite" in raw_text:
            new_level = AUTONOMY_SATELLITE
        elif "autonomous" in raw_text:
            new_level = AUTONOMY_AUTONOMOUS
        elif "increase" in raw_text:
            # Direction-based: increase by one level
            vassals = getattr(world, 'vassals', {})
            v = vassals.get(target, {})
            current = v.get("autonomy", AUTONOMY_SATELLITE)
            if current >= AUTONOMY_AUTONOMOUS:
                return {"success": False, "message": f"{target} is already at maximum autonomy."}
            new_level = current + 1
        elif "decrease" in raw_text:
            # Direction-based: decrease by one level
            vassals = getattr(world, 'vassals', {})
            v = vassals.get(target, {})
            current = v.get("autonomy", AUTONOMY_SATELLITE)
            if current <= AUTONOMY_PUPPET:
                return {"success": False, "message": f"{target} is already at minimum autonomy."}
            new_level = current - 1
        else:
            return {
                "success": False,
                "message": "Specify autonomy level: puppet, satellite, or autonomous."
            }

        result = change_vassal_autonomy(world, target, new_level)
        if result.get("success"):
            result["new_state"] = game_state
        return result

    def _execute_make_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Create a vassal from treaty or conquest path."""
        from backend.models.world_state import WorldState
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which nation to vassalize."}

        player = getattr(world, 'player_nation', 'France')

        from backend.game_logic.vassal import (
            create_vassal_treaty, create_vassal_conquest,
            assimilate_vassal_marshals, AUTONOMY_PUPPET, AUTONOMY_SATELLITE
        )

        # Determine path: if at WAR → conquest, if OPEN_BORDERS+ → treaty
        current_state = world.get_diplomatic_state(player, target)
        if current_state == "WAR":
            result = create_vassal_conquest(world, player, target)
        else:
            result = create_vassal_treaty(world, player, target)

        if result.get("success"):
            # Assimilate marshals for PUPPET/SATELLITE
            vassal_state = world.vassals.get(target, {})
            autonomy = vassal_state.get("autonomy", AUTONOMY_SATELLITE)
            if autonomy in (AUTONOMY_PUPPET, AUTONOMY_SATELLITE):
                assimilated = assimilate_vassal_marshals(world, target)
                if assimilated:
                    result["message"] += (
                        f" Marshals assimilated: {', '.join(assimilated)}."
                    )
            result["new_state"] = game_state

            # R23: Marshal trust reactions for vassal creation
            self._executor._diplomatic._apply_diplomatic_trust_reactions(world, "vassal_created", target)

        return result

    def _execute_release_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """Release a vassal nation. Costs 1 DP."""
        from backend.models.world_state import WorldState
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal to release."}

        vassals = getattr(world, 'vassals', {})
        if target not in vassals:
            return {"success": False, "message": f"{target} is not a vassal."}

        if world.diplomatic_points < 1:
            return {"success": False, "message": "Insufficient Diplomatic Points. Releasing a vassal costs 1 DP."}

        from backend.game_logic.vassal import release_vassal
        result = release_vassal(world, target)
        if result.get("success"):
            world.diplomatic_points -= 1
            result["new_state"] = game_state
        return result
