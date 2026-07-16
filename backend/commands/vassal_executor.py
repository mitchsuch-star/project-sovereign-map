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

        # Slice 0 (GR5): AI lords invest through this same executor, marked
        # with _acting_nation; the domain function validates lordship + pays
        # from the actor's own DP/gold pools.
        actor = command.get("_acting_nation") or getattr(world, 'player_nation', 'France')

        from backend.game_logic.vassal import invest_in_vassal
        result = invest_in_vassal(world, target, actor=actor)
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
        # Slice 0 (GR5): AI callers and structured (wizard) payloads pass the
        # level as a FIELD — honored before any raw-text parse so an AI order
        # never depends on synthesizing English.
        actor = command.get("_acting_nation") or getattr(world, 'player_nation', 'France')
        structured_level = command.get("new_level")
        if structured_level is None:
            structured_level = command.get("autonomy_level")
        if isinstance(structured_level, int) and structured_level in (
                AUTONOMY_PUPPET, AUTONOMY_SATELLITE, AUTONOMY_AUTONOMOUS):
            result = change_vassal_autonomy(world, target, structured_level, actor=actor)
            if result.get("success"):
                result["new_state"] = game_state
            return result
        # F6 (playtest): the parser populates `raw_command`; the old chain read
        # only `raw_input`/`original_command` (never set), so the level phrase
        # was always empty and every order dead-ended on "Specify autonomy
        # level" — the exact verb VS-1's recovery hint teaches. Read raw_command.
        raw_text = (
            command.get("raw_input")
            or command.get("original_command")
            or command.get("raw_command")
            or ""
        ).lower()
        if "puppet" in raw_text:
            new_level = AUTONOMY_PUPPET
        elif "satellite" in raw_text:
            new_level = AUTONOMY_SATELLITE
        elif "autonomous" in raw_text:
            new_level = AUTONOMY_AUTONOMOUS
        elif any(w in raw_text for w in ("increase", "more autonomy", "loosen", "grant")):
            # Direction-based: one level MORE autonomy (VS-1 hint: "grant autonomy")
            vassals = getattr(world, 'vassals', {})
            v = vassals.get(target, {})
            current = v.get("autonomy", AUTONOMY_SATELLITE)
            if current >= AUTONOMY_AUTONOMOUS:
                return {"success": False, "message": f"{target} is already at maximum autonomy."}
            new_level = current + 1
        elif any(w in raw_text for w in ("decrease", "less autonomy", "tighten", "reduce")):
            # Direction-based: one level LESS autonomy
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

        result = change_vassal_autonomy(world, target, new_level, actor=actor)
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

        # Slice 0 (GR5): the lord is the acting nation, not hardcoded-player.
        player = command.get("_acting_nation") or getattr(world, 'player_nation', 'France')

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

            # R23: Marshal trust reactions for vassal creation — the player's
            # marshals react to the PLAYER's deed only (Slice 0 guard).
            if player == getattr(world, 'player_nation', 'France'):
                self._executor._diplomatic._apply_diplomatic_trust_reactions(world, "vassal_created", target)

        return result

    def _execute_grant_region_to_vassal(self, command: Dict, game_state: Dict) -> Dict:
        """VS-3: cede a controlled province to a vassal (1 DP, no AP).

        Region resolution order: structured `region` field (the wizard's
        sub-picker / AI rung) → a known-region name in the raw text (typed
        path, longest match wins) → no region = answer with the eligible
        list so the typed path is discoverable.
        """
        from backend.models.world_state import WorldState
        world: WorldState = game_state.get("world")
        if not world:
            return {"success": False, "message": "No active game."}

        target = (command.get("target") or command.get("target_nation") or "").strip()
        if not target:
            return {"success": False, "message": "Specify which vassal receives the province."}

        actor = command.get("_acting_nation") or getattr(world, 'player_nation', 'France')

        region = (command.get("region") or "").strip()
        if not region:
            raw_text = (
                command.get("raw_input")
                or command.get("original_command")
                or command.get("raw_command")
                or ""
            ).lower()
            # Post-build review C6: the RECIPIENT's name must never be
            # scanned as the province ("cede tyrol to hanover" — Hanover is
            # both a nation and a region; the wizard's no-pick echo "cede
            # territory to naples" likewise). Cut the trailing "to <target>"
            # clause, then take the longest word-boundary region match
            # ("United Provinces" must beat a hypothetical "Provinces").
            import re as _re
            scan_text = _re.sub(
                rf'\bto\s+{_re.escape(target.lower())}\b.*$', ' ', raw_text)
            scan_text = scan_text.replace(target.lower(), ' ')
            best = ""
            for region_name in world.regions:
                pattern = rf'(?<![a-z]){_re.escape(region_name.lower())}(?![a-z])'
                if _re.search(pattern, scan_text) and len(region_name) > len(best):
                    best = region_name
            region = best

        from backend.game_logic.vassal import (
            GRANT_DP_COST,
            grant_region_to_vassal,
            list_grantable_regions,
        )
        if not region:
            eligible = list_grantable_regions(world, target, actor=actor)
            if not eligible:
                return {
                    "success": False,
                    "message": (
                        f"No province is eligible to cede to {target} — it must "
                        f"be conquered land (not your homeland, not a capital, "
                        f"not a marshal's estate) adjoining their territory."
                    ),
                }
            options = "; ".join(
                f"{e['region']} (income {e['income']}g, loyalty +{e['loyalty_gain']})"
                for e in eligible[:6]
            )
            return {
                "success": False,
                "message": (
                    f"Specify which province to cede to {target} "
                    f"(costs {GRANT_DP_COST} DP). Eligible: {options}."
                ),
            }

        result = grant_region_to_vassal(world, target, region, actor=actor)
        if result.get("success"):
            result["new_state"] = game_state
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
