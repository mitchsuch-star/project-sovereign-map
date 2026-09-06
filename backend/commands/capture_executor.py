"""
Capture Executor — Region capture choice handling (R13A)

Extracted from executor.py: handle_capture_choice (plunder/secure).

W6-8 (The Spoils of War): when the captured province funds an ENEMY
marshal's estate, a SECOND choice follows plunder/secure on the same
capture_choice pipeline — confiscate the estate (windfall + grudge) or
respect the title (goodwill). The second stage rides the same
world.pending_capture_choice field with stage="estate" and carries a
dialogue_id minted from the W6-0 counter, so a stale popup answer can
never resolve the wrong question.
"""
from typing import Dict, Optional

from backend.display_names import humanize_entity_name
from backend.game_logic.formations import formed_display_name


def _estate_holder_display(pending) -> str:
    """FA-69: the holder's NAME as a reader should see it.

    The stored `estate_holder` is the machine key and must stay one — the
    answer handler looks the marshal up by it, and a humanised value fails
    that lookup and returns "The estate question has lapsed." So the display
    form rides beside it, and every sentence reads the display key with the
    raw one as a fallback, which is also what makes a PRE-FIX save render:
    a save taken before this slice carries no `_display` key and falls
    through to the humaniser here rather than to the raw string.
    """
    if not isinstance(pending, dict):
        return "?"
    shown = pending.get("estate_holder_display")
    if shown:
        return str(shown)
    raw = pending.get("estate_holder")
    return humanize_entity_name(str(raw)) if raw else "?"


class CaptureExecutor:
    """Handles post-capture plunder/secure choice."""

    def __init__(self, parent_executor):
        self._executor = parent_executor

    def handle_capture_choice(self, choice: str, game_state: Dict,
                              dialogue_id: Optional[int] = None,
                              region: Optional[str] = None) -> Dict:
        """Handle player's capture choices: plunder/secure, then (when the
        province sustains an enemy marshal's estate) confiscate/respect.

        Args:
            choice: 'plunder' or 'secure' (stage 1);
                    'confiscate' or 'respect' (stage 2, estate)
            game_state: Current game state dict with 'world' key
            dialogue_id: optional W6-0 identity check — if provided and it
                    does not match the pending question's id, the choice is
                    refused and the current question re-attached.
            region: WO-29 — the province the player NAMED with a typed
                    answer ("plunder Swabia"). The typed route carries no
                    dialogue_id (there is none to carry: `/command` has no
                    such field, and the client's only capture id is written
                    when the modal renders, which disables the command
                    line), so identity on that path is bound by CONTENT,
                    exactly as the typed diplomatic route already binds by
                    the court's name. A named province that is not the one
                    standing is refused and the real question restated —
                    never applied to a different province.

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

        # W6-0 discipline: an answer aimed at a superseded question is
        # refused; the CURRENT question is re-attached for the player.
        if (dialogue_id is not None
                and pending.get("dialogue_id") is not None
                and int(dialogue_id) != int(pending["dialogue_id"])):
            return {
                "success": False,
                "stale_dialogue": True,
                "message": ("Sire, another matter has arisen since — "
                            + self._pending_prompt(pending)),
                "pending_capture_choice": True,
                "capture_data": pending,
            }

        # WO-29: the same rule, bound by content for the typed path.
        if region is not None and str(region) != str(pending.get("region", "")):
            return {
                "success": False,
                "stale_dialogue": True,
                "message": (f"Sire, {region} is not the matter before us — "
                            + self._pending_prompt(pending)),
                "pending_capture_choice": True,
                "capture_data": pending,
            }

        if pending.get("stage") == "estate":
            return self._handle_estate_choice(choice, pending, world)

        region_name = pending["region"]
        capturer_name = pending["capturer"]
        region = world.get_region(region_name)

        if not region:
            world.pending_capture_choice = None
            return {"success": False, "message": f"Region {region_name} not found."}

        # IGR-X8: re-validate the holder at ANSWER time. A full turn can pass
        # between capture and answer (a jealousy autonomous attack's
        # _strategic_execution bypasses the pending-choice block), so the
        # province may have been retaken — answering "plunder" would sack an
        # enemy-held province and credit the player the gold.
        if region.controller != world.player_nation:
            world.pending_capture_choice = None
            return {
                "success": False,
                "message": (f"Sire, the question has lapsed — {region_name} "
                            f"is no longer in our hands."),
            }

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
            response = {
                "success": True,
                "message": (f"{capturer_name}'s troops plunder {region_name}! "
                            f"Gained {result['gold_gained']:,} gold. "
                            f"Buildings destroyed. Stability set to 10."),
                "events": [{
                    "type": "plunder",
                    "region": region_name,
                    "capturer": capturer_name,
                    "gold_gained": result["gold_gained"],
                }],
                "capture_choice": "plunder",
            }
            self._maybe_mount_estate_choice(world, region, capturer_name,
                                            pending, response)
            return response
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
            response = {
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
            self._maybe_mount_estate_choice(world, region, capturer_name,
                                            pending, response)
            return response
        else:
            # IGR-E: restate through the shared prompt (so the price
            # survives a wrong token) and RE-ATTACH the pending question,
            # as the estate stage's wrong-token branch already did — this
            # branch used to drop capture_data from the response, leaving
            # the client with a question still pending in world state but
            # nothing to render it from.
            return {
                "success": False,
                "message": (f"Invalid choice: '{choice}'. Sire, "
                            + self._pending_prompt(pending)),
                "pending_capture_choice": True,
                "capture_data": pending,
            }

    # ── W6-8: the estate stage ────────────────────────────────────────

    @staticmethod
    def _pending_prompt(pending: Dict) -> str:
        """The current question, restated (BUG-CA-10 discipline: always
        enumerate the answers the game will accept)."""
        if pending.get("stage") == "estate":
            return (f"the fate of Marshal "
                    f"{_estate_holder_display(pending)}'s "
                    f"estate at {pending.get('region', '?')} awaits your word: "
                    f"'confiscate' or 'respect'.")
        # IGR-E: the restatement quotes the price too — a player who typed a
        # stale or wrong token must not lose the figure the prompt carried.
        # Post-landing review #4: a payload predating the priced keys omits
        # the figure rather than quoting "0 gold" for a real payout.
        gold = pending.get("plunder_gold")
        if gold is None:
            return (f"{pending.get('region', 'the captured region')} awaits "
                    f"your word: 'plunder' or 'secure'.")
        return (f"{pending.get('region', 'the captured region')} awaits your "
                f"word: 'plunder' (for {int(gold):,} gold) or 'secure'.")

    def _maybe_mount_estate_choice(self, world, region, capturer_name: str,
                                   pending: Dict, response: Dict) -> None:
        """After plunder/secure resolves: if the province sustains an enemy
        marshal's estate, mount the second question on the same pipeline.

        The windfall is computed NOW — after plunder/secure applied — so a
        plundered estate is worth confiscating less than one kept whole
        (deterministic and order-honest: plunder's +0.35 war damage is
        already on the region when confiscation_windfall reads it).
        IGR-X4: priced by the single source in dotation.py — the old
        effective-income read here was structurally 0 on every province."""
        from backend.game_logic.dotation import (
            confiscation_windfall, derive_estate_noun, derive_title,
            find_enemy_estate_holder,
        )
        holder = find_enemy_estate_holder(world, region.name,
                                          world.player_nation)
        if holder is None:
            return
        title = derive_title(region.name)
        estate_pending = {
            "stage": "estate",
            "region": region.name,
            "capturer": capturer_name,
            "previous_controller": pending.get("previous_controller", ""),
            # FA-69: `estate_holder` STAYS the machine key — the answer
            # handler re-reads it (`world.marshals.get(...)`) and a
            # humanised value fails that lookup and returns "The estate
            # question has lapsed." The display forms ride BESIDE it.
            # Measured before this: "Sire — Bohemia sustains Marshal
            # ArchdukeCharles's household", and the raw key survived the
            # ANSWER as well as the question, on both outcome sentences.
            "estate_holder": holder.name,
            "estate_holder_display": humanize_entity_name(holder.name),
            "estate_holder_nation": holder.nation,
            "estate_holder_nation_display": formed_display_name(
                world, holder.nation),
            "windfall": confiscation_windfall(region),
            "title": title,
            "options": ["confiscate", "respect"],
            "dialogue_id": world.dialogue_manager.mint_dialogue_id(),
        }
        world.pending_capture_choice = estate_pending
        response["pending_capture_choice"] = True
        response["capture_data"] = estate_pending
        response["message"] += (
            f"\n\nSire — {region.name} sustains Marshal "
            f"{humanize_entity_name(holder.name)}'s "
            f"household ({derive_estate_noun(region.name)}). "
            f"Confiscate the estate (+{estate_pending['windfall']:,} gold; "
            # Aug 30, 2026 review: the confiscate branch below was routed
            # through `formed_display_name` (NA-6 §11.8-3 — a formed nation
            # must not be named by its dead tag, and the camelCase split
            # mangles "KingdomOfItaly" into "Kingdom Of Italy"); its three
            # siblings, including this prompt, kept interpolating the raw key.
            f"{formed_display_name(world, holder.nation)} will not forgive "
            f"it) or respect the title "
            f"({formed_display_name(world, holder.nation)} will remember "
            f"the courtesy)?")

    def _handle_estate_choice(self, choice: str, pending: Dict, world) -> Dict:
        """Resolve the confiscate/respect question (stage 2)."""
        from backend.game_logic.dotation import (
            apply_estate_confiscation, apply_estate_respect,
            derive_estate_noun,
        )
        region = world.get_region(pending.get("region", ""))
        holder = world.marshals.get(pending.get("estate_holder", ""))
        if region is None or holder is None:
            world.pending_capture_choice = None
            return {"success": False,
                    "message": "The estate question has lapsed."}
        # IGR-X8: same holder re-validation as stage 1 — confiscating an
        # estate on a province we no longer hold is not a choice we have.
        if region.controller != world.player_nation:
            world.pending_capture_choice = None
            return {"success": False,
                    "message": (f"Sire, the question has lapsed — "
                                f"{region.name} is no longer in our hands.")}

        if choice == "confiscate":
            outcome = apply_estate_confiscation(
                world, region, holder, world.player_nation,
                windfall=pending.get("windfall"))
            world.pending_capture_choice = None
            message = (f"The estate at {region.name} is confiscated! "
                       f"{outcome['windfall']:,} gold seized for the treasury. "
                       f"Marshal {humanize_entity_name(holder.name)}'s "
                       f"title is extinguished — "
                       f"{formed_display_name(world, holder.nation)} "
                       f"will not forgive it.")
            if outcome["disapproving"]:
                names = ", ".join(outcome["disapproving"])
                message += (f" Your cautious marshals disapprove — property "
                            f"is sacred ({names}: -1 trust).")
            return {
                "success": True,
                "message": message,
                "events": [{
                    "type": "estate_confiscated",
                    "region": region.name,
                    "marshal": holder.name,
                    "windfall": int(outcome["windfall"]),
                }],
                "capture_choice": "confiscate",
            }
        elif choice == "respect":
            outcome = apply_estate_respect(world, region, holder,
                                           world.player_nation)
            world.pending_capture_choice = None
            return {
                "success": True,
                "message": (f"Marshal {humanize_entity_name(holder.name)}'s "
                            f"title stands — "
                            f"{derive_estate_noun(region.name)} "
                            f"keeps its revenues under our occupation. "
                            f"{formed_display_name(world, holder.nation)} "
                            f"will remember the courtesy."),
                "events": [{
                    "type": "estate_respected",
                    "region": region.name,
                    "marshal": holder.name,
                }],
                "capture_choice": "respect",
            }
        else:
            # Wrong token (incl. a late 'plunder'/'secure') — refuse without
            # clearing, and restate the question with its answers.
            return {
                "success": False,
                "message": ("Sire, " + self._pending_prompt(pending)),
                "pending_capture_choice": True,
                "capture_data": pending,
            }
