"""RE-5 — the dial's instrument (`docs/RECURRING_EVENTS_SPEC.md` §17, Q13;
written at RE-5, November 2, 2026): the share of affairs LAPSING, read from
the testers' saves.

The dial ("Affairs: Off / Standard") was struck from v1 and re-opens only on
Round 1 evidence — more than 60 % of affairs lapsing. The evidence is in the
saves: every occurrence row of the moments' state (`world_state.moments.state`,
the ids `template#n`) carries its status — `answered`, `lapsed`, `withdrawn`
(set aside for a moment of history, free), `passed` (never delivered —
crowded or its premise fell) or `fired` (standing). The share is

    lapsed / (lapsed + answered)

— the letters the player let fall against the letters the player answered.
A withdrawal and a pass are counted apart: neither is the player's silence.

    .venv/Scripts/python.exe tools/_affairs_lapse_share.py [--saves DIR ...] [--glob "*.json"]
                                                           [--out share.json] [--check [PCT]]

With no `--saves` the game's own save directory is read (`INK_IRON_SAVE_DIR`,
else `backend.save_manager.SAVE_DIR`). `--check` (60 when bare) exits 2 when
the overall share is over the threshold — the dial's re-open evidence. A raw
JSON reader: no world is booted, so a save from any build reads.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
SEP = "#"
STATUSES = ("lapsed", "answered", "withdrawn", "passed", "fired")
DIAL_THRESHOLD_PCT = 60.0


def default_save_dir() -> Path:
    env = os.getenv("INK_IRON_SAVE_DIR")
    if env:
        return Path(env)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from backend.save_manager import SAVE_DIR
    return Path(SAVE_DIR)


def occurrence_rows(save: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """The occurrence rows of one save's world (either wrapper, or a bare world)."""
    world = save.get("world_state") if isinstance(save.get("world_state"), dict) else save.get("world")
    if not isinstance(world, dict):
        world = save
    state = ((world.get("moments") or {}).get("state") or {}) if isinstance(world.get("moments"), dict) else {}
    return {str(k): v for k, v in state.items() if isinstance(v, dict) and SEP in str(k)}


def read_save(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    world = data.get("world_state") if isinstance(data.get("world_state"), dict) else data.get("world")
    if not isinstance(world, dict):
        world = data
    return {"save": path.name, "turn": world.get("current_turn"), "rows": occurrence_rows(data)}


def _template(occurrence_id: str) -> str:
    return occurrence_id.split(SEP, 1)[0]


def share_of(counts: Dict[str, int]) -> Optional[float]:
    """lapsed / (lapsed + answered), as a percentage; None with nothing to read."""
    lapsed, answered = int(counts.get("lapsed", 0)), int(counts.get("answered", 0))
    if lapsed + answered == 0:
        return None
    return round(100.0 * lapsed / (lapsed + answered), 1)


def tally(rows: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    counts = {s: 0 for s in STATUSES}
    counts["other"] = 0
    per_template: Dict[str, Dict[str, int]] = {}
    for mid, row in sorted(rows.items()):
        status = str(row.get("status") or "")
        key = status if status in STATUSES else "other"
        counts[key] += 1
        t = per_template.setdefault(_template(mid), {s: 0 for s in STATUSES})
        if key in t:
            t[key] += 1
    return {"counts": counts, "share": share_of(counts),
            "templates": {t: {"counts": c, "share": share_of(c)} for t, c in sorted(per_template.items())}}


def _merge(into: Dict[str, Any], one: Dict[str, Any]) -> None:
    for s, n in one["counts"].items():
        into["counts"][s] = into["counts"].get(s, 0) + int(n)
    for t, row in one["templates"].items():
        acc = into["templates"].setdefault(t, {s: 0 for s in STATUSES})
        for s, n in row["counts"].items():
            acc[s] = acc.get(s, 0) + int(n)


def measure(paths: Iterable[Path]) -> Dict[str, Any]:
    saves: List[Dict[str, Any]] = []
    overall = {"counts": {s: 0 for s in STATUSES}, "templates": {}}
    overall["counts"]["other"] = 0
    unread: List[str] = []
    for path in paths:
        rec = read_save(path)
        if rec is None:
            unread.append(path.name)
            continue
        t = tally(rec["rows"])
        saves.append({"save": rec["save"], "turn": rec["turn"], "rows": len(rec["rows"]), **t})
        _merge(overall, t)
    overall_share = share_of(overall["counts"])
    return {
        "saves": saves, "unread": unread,
        "overall": {"counts": overall["counts"], "share": overall_share,
                    "templates": {t: {"counts": c, "share": share_of(c)} for t, c in sorted(overall["templates"].items())}},
        "affairs_seen": sum(s["rows"] for s in saves),
    }


def verdict(record: Dict[str, Any], threshold_pct: float) -> str:
    share = record["overall"]["share"]
    if share is None:
        return "no affairs answered or lapsed yet"
    return "over" if share > threshold_pct else "under"


def _fmt(share: Optional[float]) -> str:
    return "—" if share is None else f"{share:.1f} %"


def print_table(record: Dict[str, Any], threshold_pct: Optional[float]) -> None:
    print(f"{'save':40s} {'turn':>4s} {'rows':>4s} {'lapsed':>6s} {'answ.':>5s} {'withdr.':>7s} {'passed':>6s} {'stand.':>6s}  share")
    for s in record["saves"]:
        c = s["counts"]
        print(f"{s['save'][:40]:40s} {str(s['turn'] or ''):>4s} {s['rows']:4d} {c['lapsed']:6d} {c['answered']:5d} "
              f"{c['withdrawn']:7d} {c['passed']:6d} {c['fired']:6d}  {_fmt(s['share'])}")
    o = record["overall"]
    c = o["counts"]
    print(f"{'ALL':40s} {'':>4s} {record['affairs_seen']:4d} {c['lapsed']:6d} {c['answered']:5d} "
          f"{c['withdrawn']:7d} {c['passed']:6d} {c['fired']:6d}  {_fmt(o['share'])}")
    for t, row in o["templates"].items():
        tc = row["counts"]
        print(f"  {t:38s} {'':>4s} {'':>4s} {tc['lapsed']:6d} {tc['answered']:5d} {tc['withdrawn']:7d} {tc['passed']:6d} {tc['fired']:6d}  {_fmt(row['share'])}")
    if record["unread"]:
        print("unread (not a save):", ", ".join(record["unread"]))
    if threshold_pct is not None:
        print(f"the dial's evidence (over {threshold_pct:g} % lapsing): {verdict(record, threshold_pct)}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--saves", nargs="*", default=None, help="save directories (default: the game's)")
    ap.add_argument("--glob", default="*.json")
    ap.add_argument("--out", default="", help="write the record as JSON")
    ap.add_argument("--check", nargs="?", const=DIAL_THRESHOLD_PCT, type=float, default=None,
                    help="exit 2 when the overall share is over PCT (60 when bare)")
    args = ap.parse_args(argv)
    dirs = [Path(d) for d in (args.saves or [])] or [default_save_dir()]
    paths: List[Path] = []
    for d in dirs:
        if d.is_file():
            paths.append(d)
        elif d.is_dir():
            paths.extend(sorted(p for p in d.glob(args.glob) if p.is_file()))
    record = measure(paths)
    record["dirs"] = [str(d) for d in dirs]
    record["threshold_pct"] = args.check
    if args.check is not None:
        record["verdict"] = verdict(record, float(args.check))
    print_table(record, args.check)
    if args.out:
        Path(args.out).write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", args.out)
    if args.check is not None and record.get("verdict") == "over":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
