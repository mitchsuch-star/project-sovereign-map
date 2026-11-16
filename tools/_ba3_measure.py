"""Row BA, BA-3 — the France band on the COMMANDED arms with the day's points
(BATTLE_DIORAMA_SPEC.md §15; November 15, 2026). In the manner of
`tools/_ba1_band_measure.py`, extended to an N-seed sweep of deltas.

The reading is `tools/_g5_measure.py::_band`'s own: `score_run.ARMS` CMD-H /
CMD-A / CMD-M (commanded_full40.json, forty turns, the mock parser), France's
provinces on the last `ledger` row, plus the run's day counters off meta.json
(`rounds`: days opened, words given by kind, days ended by kind — written by
`tools/playtest_driver.py`'s `RoundsPlayer`). `--seeds jena,wagram,...` adds
extra named campaign seeds (run `SEED-<name>`: the same commanded script and
flags, `--seed <name>`) beside the three commanded seeds.

Arms (seams held DOWN / set through the driver's own `--seam`; `--rounds` is
the driver's dial):

    0    every new seam down: the_day_has_points, the_temper_is_seeded,
         the_narration_varies — MUST reproduce the recorded 26 / 27 / 28
         (CMD-H 26, CMD-A 27, CMD-M 28) on the three commanded seeds
    T    the_day_has_points down only (the seeded temper + varied telling)
    S    all seams up, `--rounds none` (the points up, France silent)
    P G D B L   `--rounds press | guard | dig_in | break_off | leave`
    ALL  the shipped tree, `--rounds sense`
    E0   sense + the_enemy_spends_his=False
    N2   sense + points_high=2          N3  sense + points_low=3
    K50  sense + key_bar=50000
    NG   guard + the_guards_numbers_bite=False

    .venv/Scripts/python.exe tools/_ba3_measure.py [--arms 0,T,ALL]
        [--seeds jena,wagram] [--stamp 2026_11_15] [--jobs 3] [--out PATH]

Output: the absolute table, then two DELTA tables (provinces_X - provinces_T,
and - provinces_0) with mean / min / max / n per arm. A failed run (exit != 0,
status not completed, no ledger row) is shown FAIL and excluded from deltas,
never counted as 0. Exit code 2 if arm 0 ran and the three commanded seeds do
not reproduce 26 / 27 / 28. Default record: tools/_ba3_band_<stamp>.json; with
--seeds: tools/_ba3_sweep_<stamp>.json. Run ALONE — no backend, test or deck
edit lands while it runs. THIS PARENT RUNS PLAIN (never `-X utf8`): the
children print cp1252.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
BD = "backend.game_logic.battle_day"
CV = "backend.game_logic.campaign_variance"
DAY_DOWN = f"{BD}:the_day_has_points=False"
TEMPER_DOWN = f"{CV}:the_temper_is_seeded=False"
NARR_DOWN = f"{CV}:the_narration_varies=False"

# arm -> (the seams set/held, the --rounds value or "" for none passed)
ARMS = {
    "0": ([DAY_DOWN, TEMPER_DOWN, NARR_DOWN], ""),
    "T": ([DAY_DOWN], ""),
    "S": ([], "none"),
    "P": ([], "press"),
    "G": ([], "guard"),
    "D": ([], "dig_in"),
    "B": ([], "break_off"),
    "L": ([], "leave"),
    "ALL": ([], "sense"),
    "E0": ([f"{BD}:the_enemy_spends_his=False"], "sense"),
    "N2": ([f"{BD}:points_high=2"], "sense"),
    "N3": ([f"{BD}:points_low=3"], "sense"),
    "K50": ([f"{BD}:key_bar=50000"], "sense"),
    "NG": ([f"{BD}:the_guards_numbers_bite=False"], "guard"),
}
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
ARM0_EXPECTED = {"CMD-H": 26, "CMD-A": 27, "CMD-M": 28}
MAX_JOBS = 4


def _read(arms_dir: pathlib.Path, name: str, result: dict) -> dict:
    """One run's reading; a failed run / missing ledger row is a failure, never 0."""
    reading = {"provinces": None, "turn": None, "status": result.get("status") or "no-meta",
               "exit": result.get("exit"), "ok": False, "days_opened": 0, "words_given": 0,
               "words_by_kind": {}, "days_ended": {}}
    try:
        rows = [json.loads(line) for line in (arms_dir / name / "digest.jsonl")
                .read_text(encoding="utf-8").splitlines() if line.strip()]
        ledgers = [r for r in rows if r.get("kind") == "ledger"]
        turns = [r for r in rows if r.get("kind") == "turn"]
        meta = json.loads((arms_dir / name / "meta.json").read_text(encoding="utf-8"))
        days = meta.get("rounds") or {}
        reading.update(turn=int(turns[-1]["turn"]) if turns else None,
                       days_opened=int(days.get("days_opened", 0)),
                       words_given=int(days.get("words_given", 0)),
                       words_by_kind=days.get("words_by_kind", {}),
                       days_ended=days.get("days_ended", {}))
        if ledgers:
            reading["provinces"] = int(ledgers[-1]["provinces"])
    except Exception as exc:  # an instrument reports its own failure
        reading["error"] = repr(exc)[:200]
    reading["ok"] = (result.get("exit") == 0 and reading["status"] == "completed"
                     and reading["provinces"] is not None)
    return reading


def _seed_runs(SR, seeds):
    """[(label, argv-without-seams)]: the three commanded arms, then SEED-<name>."""
    runs = [(n, list(SR.ARMS[n]["argv"])) for n in BAND_ARMS]
    runs += [(f"SEED-{s}", list(SR._cmd(s, []))) for s in seeds]
    return runs


def measure(arms, jobs: int, seeds=()) -> dict:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools import score_run as SR

    run_dir = ROOT / "tools" / "playtest_runs" / "ba3_band"
    labels = [n for n, _ in _seed_runs(SR, seeds)]
    record = {"_note": ("Row BA, BA-3 (the day's points) - the France band on the commanded arms "
                        "(DYNAMISM_SPEC.md 2: the deploy gate's difficulty guard, 23-28) with the "
                        "day's points: score_run's CMD-H / CMD-A / CMD-M (commanded_full40.json, "
                        "forty turns, the mock parser) per arm plus any extra --seeds (SEED-<name>, "
                        "the same script and flags) - France's provinces on the last ledger row, "
                        "plus the run's day counters (meta.json `rounds`). Arm 0 holds every new "
                        "seam down and is the recorded 26 / 27 / 28 on the commanded three; ALL is "
                        "the shipped tree with `--rounds sense`. `deltas_vs_T` / `deltas_vs_0` are "
                        "per-seed differences (a failed run is excluded, never 0). "
                        "Written by tools/_ba3_measure.py (run ALONE)."),
              "band": list(BAND), "seeds": labels, "arms": {}}
    tasks = []
    for arm in arms:
        arms_dir = run_dir / arm
        arms_dir.mkdir(parents=True, exist_ok=True)
        seams, rounds = ARMS[arm]
        extra = [f for spec in seams for f in ("--seam", spec)]
        if rounds:
            extra += ["--rounds", rounds]
        record["arms"][arm] = {"seams": list(seams), "rounds": rounds or "(absent)"}
        for name, argv in _seed_runs(SR, seeds):
            tasks.append((arm, name, arms_dir, argv + extra))

    def _one(task):
        arm, name, arms_dir, argv = task
        print(f"[ba3] band {arm} {name} ...", flush=True)
        try:
            result = SR._run_driver(ROOT, arms_dir, name, argv)
        except Exception as exc:
            result = {"exit": -1, "status": f"driver-error {exc!r}"[:120]}
        reading = _read(arms_dir, name, result)
        if not reading["ok"]:
            print(f"[ba3] band {arm} {name} FAILED: exit {result.get('exit')} "
                  f"status {reading['status']!r}", flush=True)
        return arm, name, reading

    with ThreadPoolExecutor(max_workers=max(1, min(jobs, MAX_JOBS))) as pool:
        for arm, name, reading in pool.map(_one, tasks):
            record["arms"][arm][name] = reading
    record["deltas_vs_T"] = _deltas(record, "T")
    record["deltas_vs_0"] = _deltas(record, "0")
    return record


def _prov(record, arm, name):
    r = record["arms"].get(arm, {}).get(name)
    return r["provinces"] if r and r.get("ok") else None


def _deltas(record: dict, base: str) -> dict:
    out = {}
    for arm in record["arms"]:
        per = {}
        for name in record["seeds"]:
            x, b = _prov(record, arm, name), _prov(record, base, name)
            per[name] = None if x is None or b is None else x - b
        vals = [v for v in per.values() if v is not None]
        out[arm] = {"per_seed": per, "n": len(vals),
                    "mean": round(sum(vals) / len(vals), 2) if vals else None,
                    "min": min(vals) if vals else None, "max": max(vals) if vals else None}
    return out


def _cell(v, w=5):
    return f"{'.' if v is None else v:>{w}}"


def _short(label):
    return label.replace("SEED-", "")[:7]


def _table(record: dict) -> str:
    seeds = record["seeds"]
    lines = [f"{'arm':<4} {'rounds':<9}" + "".join(f"{_short(s):>8}" for s in seeds)
             + "  days  words  ended"]
    for arm, r in record["arms"].items():
        cells, days, words, ended = [], 0, 0, {}
        for n in seeds:
            x = r[n]
            cells.append(f"{x['provinces']:>8}" if x["ok"] else f"{'FAIL':>8}")
            days += x["days_opened"]
            words += x["words_given"]
            for k, v in x["days_ended"].items():
                ended[k] = ended.get(k, 0) + v
        lines.append(f"{arm:<4} {r['rounds']:<9}" + "".join(cells)
                     + f"  {days:>4}  {words:>5}  {ended}")
    fails = [f"{a}/{n}: {r[n]['status']}" for a, r in record["arms"].items()
             for n in seeds if not r[n]["ok"]]
    if fails:
        lines.append(f"FAILED runs (excluded from deltas): {fails}")
    return "\n".join(lines)


def _delta_table(record: dict, key: str, base: str) -> str:
    seeds = record["seeds"]
    lines = [f"deltas vs arm {base} (provinces_X - provinces_{base}; '.' = not measured)",
             f"{'arm':<4}" + "".join(f"{_short(s):>8}" for s in seeds) + "    mean   min   max   n"]
    for arm, d in record[key].items():
        lines.append(f"{arm:<4}" + "".join(_cell(d["per_seed"][s], 8) for s in seeds)
                     + f"  {_cell(d['mean'], 6)} {_cell(d['min'], 5)} {_cell(d['max'], 5)} {d['n']:>3}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--seeds", default="", help="extra named campaign seeds, e.g. jena,wagram")
    ap.add_argument("--stamp", default="2026_11_15")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", default="", help="the record's path (default tools/_ba3_band_<stamp>.json; "
                    "with --seeds tools/_ba3_sweep_<stamp>.json)")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    seeds = [s for s in args.seeds.split(",") if s]
    unknown = [a for a in arms if a not in ARMS]
    if unknown:
        raise SystemExit(f"[ba3] unknown arm(s) {unknown}; known: {list(ARMS)}")
    record = measure(arms, args.jobs, seeds)
    default = f"_ba3_sweep_{args.stamp}.json" if seeds else f"_ba3_band_{args.stamp}.json"
    out = pathlib.Path(args.out) if args.out else ROOT / "tools" / default
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(_table(record), flush=True)
    print(_delta_table(record, "deltas_vs_T", "T"), flush=True)
    print(_delta_table(record, "deltas_vs_0", "0"), flush=True)
    print(f"[ba3] record written {out}", flush=True)
    if "0" in record["arms"]:
        got = {n: record["arms"]["0"][n]["provinces"] for n in BAND_ARMS}
        if got != ARM0_EXPECTED:
            print(f"[ba3] STOP: arm 0 does not reproduce the recorded band {ARM0_EXPECTED}: got {got}. "
                  f"A seam is not fully down or the tree moved; do not read the other arms.",
                  flush=True)
            raise SystemExit(2)


if __name__ == "__main__":
    main()
