"""Save/Load manager for game state persistence.

Handles all file I/O for save games: manual save, manual load, autosave,
listing saves, and deleting saves.

Save format:
{
    "metadata": {
        "format_version": 1,
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict

from backend.models.world_state import WorldState

SAVE_DIR = Path("saves")
AUTOSAVE_FILENAME = "autosave.json"
FORMAT_VERSION = 2
MAX_MANUAL_SAVES = 10


def ensure_save_dir():
    """Create saves directory if it doesn't exist."""
    SAVE_DIR.mkdir(exist_ok=True)


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
                "player_nation": world.player_nation,
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

        # Hard break: reject saves from 13-region map (format version 1)
        save_version = metadata.get("format_version", 1)
        if save_version < FORMAT_VERSION:
            return {"success": False,
                    "message": "This save is from a 13-region map and is incompatible with the current version.",
                    "world": None, "metadata": metadata}

        if world_data is None:
            return {"success": False, "message": "Invalid save file: no world_state", "world": None, "metadata": metadata}

        world = WorldState.from_dict(world_data)

        # Clear transient per-turn data that shouldn't persist across save/load
        world.battles_this_turn = []
        for marshal in world.marshals.values():
            marshal.in_combat_this_turn = False

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
    """Save to autosave slot. Called at start of each new turn."""
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
