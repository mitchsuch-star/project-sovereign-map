"""CX3-R9 (Score Finish Step 7 slice 8, October 4, 2026): the completer's
screenshot board, taken from the REAL 1805 boot.

`tools/cx3_completer_screenshot.gd` used to stub five provinces and two
enemies, so the widest row the shipped game can draw (126 provinces, every
foe in sight) was never on screen. This writes the fog-filtered summary the
client reads at boot (`WorldState.get_filtered_game_state_summary`, the same
builder `/test` and `/command` serve) to `tools/cx3_completer_board.json`.

    .venv/Scripts/python.exe tools/gen_cx3_completer_board.py

Regenerate after a map, roster or payload-shape change; the committed file
is what the capture tool reads.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["LLM_MODE"] = "mock"
for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
    os.environ.pop(key, None)

from backend.models.world_state import WorldState  # noqa: E402

SCENARIO = ROOT / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
OUT = ROOT / "tools" / "cx3_completer_board.json"


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO))
        summary = world.get_filtered_game_state_summary()
    OUT.write_text(json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n",
                   encoding="utf-8")
    regions = len(summary.get("map_data", {}) or {})
    enemies = len(summary.get("enemies", {}) or {})
    print(f"wrote {OUT.relative_to(ROOT)}: {regions} provinces, {enemies} foes in sight, "
          f"{OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
