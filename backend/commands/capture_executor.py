"""
Capture Executor — Region capture choice handling (R13A)

Extracted from executor.py: handle_capture_choice (plunder/secure).
"""
from typing import Dict


class CaptureExecutor:
    """Handles post-capture plunder/secure choice."""

    def __init__(self, parent_executor):
        self._executor = parent_executor

    def handle_capture_choice(self, choice: str, game_state: Dict) -> Dict:
        """Handle player's plunder/secure choice after capturing a region.

        Args:
            choice: 'plunder' or 'secure'
            game_state: Current game state dict with 'world' key

        Returns:
            Result dict with effects applied
        """
        from backend.models.world_state import WorldState
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No world state available"}

        pending = world.pending_capture_choice
        if not pending:
            return {"success": False, "message": "No pending capture choice."}

        region_name = pending["region"]
        capturer_name = pending["capturer"]
        region = world.get_region(region_name)

        if not region:
            world.pending_capture_choice = None
            return {"success": False, "message": f"Region {region_name} not found."}

        if choice == "plunder":
            result = self._executor._combat._apply_plunder(region, world)
            world.pending_capture_choice = None
            # Log region_captured event
            world.log_event({
                "type": "region_captured",
                "region": region_name,
                "captured_by": world.player_nation,
                "captured_from": pending.get("previous_controller", ""),
                "method": "plunder",
            })
            return {
                "success": True,
                "message": (f"{capturer_name}'s troops plunder {region_name}! "
                            f"Gained {result['gold_gained']} gold. "
                            f"Buildings destroyed. Stability set to 10."),
                "events": [{
                    "type": "plunder",
                    "region": region_name,
                    "capturer": capturer_name,
                    "gold_gained": result["gold_gained"],
                }],
                "capture_choice": "plunder",
            }
        elif choice == "secure":
            self._executor._combat._apply_secure(region)
            world.pending_capture_choice = None
            damaged_count = len([b for b in region.buildings if b.get("damaged")])
            # Log region_captured event
            world.log_event({
                "type": "region_captured",
                "region": region_name,
                "captured_by": world.player_nation,
                "captured_from": pending.get("previous_controller", ""),
                "method": "secure",
            })
            return {
                "success": True,
                "message": (f"{capturer_name} secures {region_name}. "
                            f"Stability set to 25. Order is maintained."
                            + (f" {damaged_count} building(s) damaged." if damaged_count else "")),
                "events": [{
                    "type": "secure",
                    "region": region_name,
                    "capturer": capturer_name,
                }],
                "capture_choice": "secure",
            }
        else:
            return {
                "success": False,
                "message": f"Invalid choice: '{choice}'. Choose 'plunder' or 'secure'."
            }
