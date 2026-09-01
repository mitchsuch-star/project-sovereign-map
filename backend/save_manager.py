"""Save/Load manager for game state persistence.

Handles all file I/O for save games: manual save, manual load, autosave,
listing saves, and deleting saves.

Save format:
{
    "metadata": {
        "format_version": 3,
        "save_name": "...",
        "saved_at": "ISO-8601",
        "turn": int,
        "player_nation": "..."
    },
    "world_state": { ... }  # Output of world.to_dict()
}

The hard part (serialization) is already done — WorldState.to_dict()/from_dict()
handle all nested objects (marshals, regions, trust, strategic orders, etc.)
with .get(key, default) for backward compatibility.
"""

import json
import os  # noqa: E402 - used in atomic save write
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict

from backend.models.world_state import WorldState


def _resolve_save_dir() -> Path:
    """Resolve where saves live (Aug 2026 shippable-build P0).

    A bare ``Path("saves")`` is CWD-relative — fine for the dev repo, but a
    frozen (PyInstaller) build writes saves wherever the exe happened to be
    launched from: Desktop, a zip-extract temp dir, Program Files (where the
    write may silently fail). Precedence:

    1. ``INK_IRON_SAVE_DIR`` env — explicit override, wins everywhere.
    2. Frozen build (``sys.frozen``) — ``%APPDATA%/InkAndIron/saves`` on
       Windows, ``~/.ink_iron/saves`` where APPDATA is absent.
    3. Dev default — repo-relative ``saves/`` (unchanged; the whole test
       suite patches ``backend.save_manager.SAVE_DIR`` and keeps working).
    """
    env_dir = os.getenv("INK_IRON_SAVE_DIR")
    if env_dir:
        return Path(env_dir)
    if getattr(sys, "frozen", False):
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "InkAndIron" / "saves"
        return Path.home() / ".ink_iron" / "saves"
    return Path("saves")


SAVE_DIR = _resolve_save_dir()
AUTOSAVE_FILENAME = "autosave.json"
# Format history (DEF-2 — every bump invalidates older saves with a clear
# message rather than a silent crash):
#   1 — 13-region map
#   2 — 19-region map (pre-Europe-cutover)
#   3 — 126-province Europe map cutover (Map Slice 5); region keys changed
FORMAT_VERSION = 3
# (Aug 2026 health-check audit: the dead `MAX_MANUAL_SAVES = 10` constant was
# removed — no code ever enforced a manual-save cap; if a cap is wanted it
# belongs in save_game with an oldest-non-autosave prune, as its own slice.)


def ensure_save_dir():
    """Create saves directory if it doesn't exist.

    parents=True: the frozen-build location (%APPDATA%/InkAndIron/saves)
    is two levels deep on first run.
    """
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def save_game(world: WorldState, save_name: str = "Quicksave", filepath: Optional[Path] = None) -> Dict:
    """
    Save game state to JSON file.

    Args:
        world: Current WorldState
        save_name: Display name for the save
        filepath: Optional explicit path. If None, auto-generates in SAVE_DIR.

    Returns:
        {"success": True/False, "message": str, "filepath": str}
    """
    ensure_save_dir()

    try:
        save_data = {
            "metadata": {
                "format_version": FORMAT_VERSION,
                "save_name": save_name,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "turn": int(world.current_turn),
                # HC-0: dated save-slot label ("" without an anchor —
                # the menu renders it only when non-empty).
                "calendar_label": world.get_calendar_label(),
                "player_nation": world.player_nation,
                # AI-0b display affordance: the campaign's seed on the save
                # slot (the authoritative copy rides world_state.campaign_seed).
                "campaign_seed": str(
                    getattr(world, "campaign_seed", "historical")),
            },
            "world_state": world.to_dict()
        }

        if filepath is None:
            # Auto-generate filename from save name
            safe_name = "".join(c if c.isalnum() or c in "- _" else "_" for c in save_name)
            filepath = SAVE_DIR / f"{safe_name}.json"

        # Atomic write: write to temp file, then rename
        tmp_path = filepath.with_suffix('.tmp')
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
            os.replace(str(tmp_path), str(filepath))
        except Exception:
            # Clean up temp file on failure
            if tmp_path.exists():
                tmp_path.unlink()
            raise

        return {"success": True, "message": f"Game saved: {save_name}", "filepath": str(filepath)}

    except Exception as e:
        return {"success": False, "message": f"Save failed: {str(e)}", "filepath": ""}


def load_game(filepath: Path) -> Dict:
    """
    Load game state from JSON file.

    Returns:
        {"success": True/False, "message": str, "world": WorldState or None, "metadata": dict}
    """
    try:
        if not filepath.exists():
            return {"success": False, "message": f"Save file not found: {filepath}", "world": None, "metadata": {}}

        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        metadata = save_data.get("metadata", {})
        world_data = save_data.get("world_state")

        # Hard break: reject saves that predate the current map (DEF-2).
        # v1 = 13-region map, v2 = 19-region map; the 126-province Europe
        # cutover (format v3) changed every region key, so older saves
        # cannot load — fail with a clear versioned message, never crash.
        # Aug 2026 health-check audit: coerce defensively (a null/string
        # format_version used to raise TypeError into the generic "Load
        # failed: '<' not supported…" handler) and reject NEWER saves too —
        # feeding a future-format save to from_dict mis-loads silently.
        try:
            save_version = int(metadata.get("format_version") or 1)
        except (TypeError, ValueError):
            save_version = 0
        if save_version < FORMAT_VERSION:
            return {"success": False,
                    "message": (
                        f"This save (format v{save_version}) predates the "
                        f"126-province Europe map (format v{FORMAT_VERSION}) "
                        "and is incompatible with the current version."
                    ),
                    "world": None, "metadata": metadata}
        if save_version > FORMAT_VERSION:
            return {"success": False,
                    "message": (
                        f"This save (format v{save_version}) was written by a "
                        f"NEWER version of the game (this build reads "
                        f"v{FORMAT_VERSION}). Update the game to load it."
                    ),
                    "world": None, "metadata": metadata}

        if world_data is None:
            return {"success": False, "message": "Invalid save file: no world_state", "world": None, "metadata": metadata}

        world = WorldState.from_dict(world_data)

        # Clear transient per-turn data that shouldn't persist across save/load
        #
        # REV-F1 (Aug 31, 2026) — a FIFTH deliberate non-clear, and the reason
        # the fourth is documented two lines down. `battles_this_turn` was
        # wiped here, and the glorious charge's V2-2 engagement gate
        # (`combat_executor._execute_glorious_charge`) reads exactly that list
        # to refuse a second engagement of the same pair in one turn. MEASURED
        # through the typed command path on five seeds: Ney (recklessness
        # carried from an earlier turn) attacks Wellington to a stalemate,
        # then `charge` — refused, "has already engaged". Save mid-turn,
        # reload, charge again — the full 2x-damage GLORIOUS CHARGE lands.
        # Every other gate on that path (cavalry, aggressive, recklessness,
        # AP, range, terrain, the naval crossing) survives the round trip, so
        # nothing masked it. The list is serialized under `to_dict`'s
        # mid-turn-save contract, restored by `from_dict`, and cleared at the
        # real turn boundary by `clear_turn_battles` — the same contract the
        # other four non-clears cite. It also feeds cannon-fire detection,
        # vassal loyalty and the war-score reader, all of which were reading
        # an empty list after a mid-turn load.
        #
        # Aug 30, 2026 review — a FOURTH deliberate non-clear, for the reason
        # the first three were added. `in_combat_this_turn` was wiped here,
        # and the turn-end idle pass reads it as one of its only two
        # exemptions, so a mid-turn save/load marked every marshal who had
        # fought that turn as IDLE. `idle_turns` drives real mechanics: the
        # jealousy grievance threshold drops to hair-trigger at >= 3, the
        # hostile-pair triggers REQUIRE >= 2, and vindication decays on it.
        # The flag is serialized, restored by `from_dict`, and cleared at the
        # real turn boundary by `clear_turn_battles` — which is precisely the
        # contract the other three non-clears cite.
        world.mild_concerns_this_turn = []
        world.gold_spent_this_turn = {}
        # Aug 2026 health-check audit — deliberate NON-clears:
        # `diplomatic_trust_applied` is the ±5/turn diplomatic trust cap
        # ("survives save/load" is its in-code contract; wiping it here let
        # a mid-turn save/load refresh every marshal's budget), and
        # `attacks_this_turn` is serialized under an explicit "for mid-turn
        # saves" contract (wiping it cost the player the flanking bonus).
        #
        # WO-23 (Aug 21, 2026) adds a THIRD, for the identical reason the
        # first was added: `objection_popups_this_turn` is the ONLY live
        # limiter on the objection trust channel — max one MODERATE+
        # objection popup per marshal per turn (`world_state`, read by
        # `executor` and `strategic_executor`) — and wiping it here let a
        # mid-turn save/load refresh every marshal's budget. The trigger is
        # trust-INDEPENDENT (`objection_v2._evaluate_relationship_support`
        # reads personality and relationship only), so nothing self-limits
        # the loop as trust climbs: it runs to the 100 clamp. Three of the
        # four non-literal French marshals sit on authored -2 pairs at the
        # 1805 boot, so the vehicle ships with the game.
        #
        # All three are restored by from_dict and cleared at the real turn
        # boundary by _advance_turn_internal / reset_attack_tracking.
        world.threat_sources_this_turn = []

        # Fog of War: recalculate visibility after load (Phase 6 Session 33)
        # Handles backward compat for old saves that have no intel data —
        # calculate_visibility() populates from current game state.
        world.calculate_visibility()

        return {"success": True, "message": f"Loaded: {metadata.get('save_name', 'Unknown')}", "world": world, "metadata": metadata}

    except json.JSONDecodeError as e:
        return {"success": False, "message": f"Corrupt save file: {str(e)}", "world": None, "metadata": {}}
    except Exception as e:
        return {"success": False, "message": f"Load failed: {str(e)}", "world": None, "metadata": {}}


def autosave(world: WorldState) -> Dict:
    """Save to autosave slot. Called at start of each new turn.

    The tutorial ("The Danube Lesson") NEVER touches the slot: autosave.json
    belongs to the player's campaign, and the menu's Continue reads the newest
    save — a lesson that wrote here would both destroy the campaign autosave
    (at /new_game AND every tutorial end-turn) and hijack Continue into
    resuming the school instead of the war. Manual, player-named saves of the
    tutorial stay allowed (scenario_name rides the save, so the overlay
    re-arms on load). Position-8 session fix, Aug 8 2026.
    """
    if str(getattr(world, "scenario_name", "")) == "tutorial":
        return {
            "success": True,
            "skipped": "tutorial",
            "message": "Tutorial — campaign autosave untouched",
            "filepath": "",
        }
    return save_game(
        world,
        save_name=f"Autosave - Turn {world.current_turn}",
        filepath=SAVE_DIR / AUTOSAVE_FILENAME
    )


def list_saves() -> List[Dict]:
    """
    List all save files with metadata.

    Returns:
        List of {"filename": str, "filepath": str, "metadata": dict}
        Sorted by saved_at descending (newest first).
    """
    ensure_save_dir()
    saves = []

    for f in SAVE_DIR.glob("*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            metadata = data.get("metadata", {})
            saves.append({
                "filename": f.name,
                "filepath": str(f),
                "metadata": metadata
            })
        except (json.JSONDecodeError, Exception):
            # Skip corrupt files
            continue

    # Sort: newest first
    saves.sort(key=lambda s: s["metadata"].get("saved_at", ""), reverse=True)
    return saves


def delete_save(filepath: Path) -> Dict:
    """Delete a save file. Cannot delete autosave."""
    if filepath.name == AUTOSAVE_FILENAME:
        return {"success": False, "message": "Cannot delete autosave"}
    try:
        if filepath.exists():
            filepath.unlink()
            return {"success": True, "message": f"Deleted: {filepath.name}"}
        return {"success": False, "message": "File not found"}
    except Exception as e:
        return {"success": False, "message": f"Delete failed: {str(e)}"}
