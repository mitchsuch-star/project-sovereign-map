"""SF-RR6 (Score Finish residue 5, October 21, 2026): did the slice move the
GAME on the instrument's arms, or only what the driver records?

    python tools/_sf_rr6_arm_attribution.py ENTRY_RUN SEAM_DOWN_RUN SHIPPED_RUN

Three runs of the same arms: the entry tree (the old driver, the old intel
store), the slice with EG-X4's seam held DOWN (the new driver's records, the
old store — `--seam backend.models.world_state:scouted_view_expired=False`)
and the slice as shipped. Two streams per arm, compared pairwise:

  GAME — the chest, the Net, the provinces and the army off every LEDGER
         record, and every command's text and outcome: the campaign itself;
  VIEW — every enemy phase's visible counts and every battle record: what
         the player is SHOWN, which the player's fog decides (the enemy
         phase reaches the client fog-filtered, so an intel change moves
         this stream without touching the game).

  entry → seam down   isolates the driver (its records and the DL arm's
                      re-staged script, which moves the DL board by design);
  seam down → shipped isolates EG-X4's store (the only backend change).

The first turn each stream parts names the movement; equal streams mean the
change did not reach that arm's game.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import score_run as SR  # noqa: E402


def stream(arm: SR.Arm, which: str) -> list:
    out, turn = [], 0
    for r in arm.records:
        kind = r.get("kind")
        if kind == "turn":
            turn = int(r.get("turn") or turn)
        elif which == "game" and kind == "ledger":
            out.append((turn, "ledger", r.get("treasury"), r.get("net"),
                        r.get("provinces"), r.get("army")))
        elif which == "game" and kind == "command":
            out.append((turn, "command", r.get("text"), r.get("success")))
        elif which == "view" and kind == "battle":
            out.append((turn, "battle", json.dumps({k: r.get(k) for k in sorted(r)
                                                    if k not in ("kind",)},
                                                   sort_keys=True, default=str)[:400]))
        elif which == "view" and kind == "enemy_phase":
            # `captures` is the driver's own count — read off the prose by the
            # old driver, off the events by the new (SFR-I2) — so it is not
            # compared across the two drivers.
            out.append((turn, "enemy_phase", r.get("count"), r.get("attacks")))
    return out


def first_parting(a: list, b: list):
    for x, y in zip(a, b):
        if x != y:
            return x[0], x, y
    if len(a) != len(b):
        return "length", len(a), len(b)
    return None


def main() -> int:
    entry, down, shipped = (SR.load_arms(pathlib.Path(p)) for p in sys.argv[1:4])
    result = {}
    for name in sorted(set(entry) & set(down) & set(shipped)):
        result[name] = {}
        for which in ("game", "view"):
            s_entry, s_down, s_ship = (stream(entry[name], which), stream(down[name], which),
                                       stream(shipped[name], which))
            result[name][f"{which}: driver (entry -> seam down)"] = first_parting(s_entry, s_down)
            result[name][f"{which}: EG-X4 (seam down -> shipped)"] = first_parting(s_down, s_ship)
        for k, v in result[name].items():
            shown = "equal" if v is None else f"parts at turn {v[0]}: {str(v[1])[:150]} | {str(v[2])[:150]}"
            print(f"{name:7s} {k:38s} {shown}")
    if len(sys.argv) > 4:
        pathlib.Path(sys.argv[4]).write_text(json.dumps(result, indent=1, default=str) + "\n",
                                             encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
