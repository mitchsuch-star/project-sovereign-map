"""SR-1e — the board probe: the Congress's titled count off a run's save.

The driver's digest prints the Congress clock only once the count reaches
the summons, so a road's count is read the way VP-R1 read it — off the
run's own autosave (or a `--save-at` snapshot), through the game's own
`congress.titled` — and written beside the digest as `titled.json`
(`turn`, `titled`, `held`, `hold_titled`, `roads`, `status`), the shape the
standing xfail `test_a_played_arm_reaches_forty_five_by_turn_forty` reads.

    .venv/Scripts/python.exe tools/sr1e_titled_probe.py <run-name> [<save.json> ...]

With no save given, the run's `saves/autosave.json` under `tools/playtest_runs/`
is read; the result is written to `docs/audits/playtest_digests/<run>/titled.json`
when that archive exists (and printed either way).
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
    os.environ.pop(key, None)
os.environ.setdefault("LLM_MODE", "mock")


def probe(save_path: Path) -> dict:
    from backend.game_logic import congress, game_end
    from backend.save_manager import load_game
    with contextlib.redirect_stdout(io.StringIO()):
        loaded = load_game(save_path)
    if not loaded.get("success") or loaded.get("world") is None:
        raise SystemExit(f"could not load {save_path}: {loaded.get('message')}")
    world = loaded["world"]
    view = congress.titled(world)
    roads = game_end.title_roads(world, world.player_nation)
    ended = game_end.terminal_ending(world)
    return {
        "turn": int(world.current_turn),
        "titled": int(view["count"]),
        "held": list(view["held"]),
        "hold_titled": int(view["needed"]),
        "provinces": len(world.get_nation_regions(world.player_nation) or []),
        "status": ("game-over" if ended is not None else "completed"),
        "roads": [{"region": r["region"], "kind": r["kind"], "short": r["short"]} for r in roads],
        "save": str(save_path),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    run = sys.argv[1]
    saves = [Path(p) for p in sys.argv[2:]] or [ROOT / "tools" / "playtest_runs" / run / "saves" / "autosave.json"]
    results = [probe(p) for p in saves]
    for r in results:
        print(json.dumps({k: v for k, v in r.items() if k != "roads"}, ensure_ascii=False))
        for road in r["roads"][:12]:
            print("   ", road["short"])
    archive = ROOT / "docs" / "audits" / "playtest_digests" / run
    if archive.exists():
        final = results[-1]
        out = {k: final[k] for k in ("turn", "titled", "hold_titled", "status")}
        out["held"] = final["held"]
        out["provinces"] = final["provinces"]
        out["note"] = ("SR-1e re-measure (September 26, 2026): read off the run's own save by "
                       "tools/sr1e_titled_probe.py through congress.titled — the same count "
                       "the summons reads.")
        if len(results) > 1:
            out["series"] = [{"turn": r["turn"], "titled": r["titled"]} for r in results]
        (archive / "titled.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                             encoding="utf-8")
        print("wrote", archive / "titled.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
