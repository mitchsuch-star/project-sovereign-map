"""SR-5b (Score Mandate Chunk 5, September 28, 2026) — the shut-out probe.

Reads the saves a driver run wrote (`--save-at 2,4,...`) and prints one JSON
row per save: the Continental System's closure against Britain, the Congress's
SHUT OUT reading (`congress._shut_out_reading`: the closure term AND no
British corps on the Continent), Britain's war exhaustion, the France–Britain
state, who holds Lisbon and Rome, and France's province count. The evidence
memo `docs/audits/SR5B_SHUT_OUT_ARM_2026_09_28.md` is this probe run over the
six arms of `tools/playtest_scripts/sr5b_shut_out.json`.

    .venv/Scripts/python.exe tools/playtest_driver.py \
        --script tools/playtest_scripts/sr5b_shut_out.json --turns 40 \
        --seed historical --declare-war proceed --diplomacy accept \
        --name sr5b-accept-historical --save-at 2,4,...,40
    PYTHONPATH=. .venv/Scripts/python.exe tools/sr5b_shut_out_probe.py \
        tools/playtest_runs/sr5b-accept-historical

Read-only: the saves are loaded into fresh worlds; nothing is written.
"""
import contextlib
import glob
import io
import json
import os
import re
import sys

from backend.game_logic import naval
from backend.game_logic.congress import _shut_out_reading
from backend.models.world_state import WorldState


def probe(run_dir: str):
    rows = []
    paths = glob.glob(os.path.join(run_dir, "saves", "*_t*.json"))
    paths.sort(key=lambda p: int(re.search(r"_t(\d+)\.json$", p).group(1)))
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        state = data.get("world_state") or data.get("world") or data
        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldState.from_dict(state)
        reading = _shut_out_reading(world, "Britain")
        rows.append({
            "turn": int(world.current_turn),
            "closure": round(naval.closure_against(world, "Britain"), 3),
            "closed": reading.get("closed"),
            "needed": reading.get("needed"),
            "shut_out_holds": reading.get("holds"),
            "corps_abroad": reading.get("corps_abroad"),
            "britain_we": int(world.war_exhaustion.get("Britain", 0)),
            "fr_gb": world.get_diplomatic_state("France", "Britain"),
            "lisbon": world.regions["Lisbon"].controller,
            "rome": world.regions["Rome"].controller,
            "gb_gold": int(world.nation_gold.get("Britain", 0)),
            "fr_provinces": len(world.get_nation_regions("France")),
        })
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    for row in probe(sys.argv[1]):
        print(json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
