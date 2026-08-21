"""WO slice 1b — re-run the ten weird arms on the fixed instrument.

Protocol (WEIRD_OUTCOMES_SPEC §3 slice 1b, verbatim): each committed
`weird_*.json` arm runs 3 seeds (`historical` + 2 banded variance seeds) ×
3 repeats on the fixed driver. Report per-arm median final provinces +
min–max. The funnel claim STANDS only if the worst fighting-arm median
exceeds the best non-military-arm median AND the min–max bands do not
overlap. A script arm that wedges on a variance seed reports as `blocked`,
never silently dropped.

Usage:
    .venv/Scripts/python.exe tools/wo_1b_sweep.py            # full sweep
    .venv/Scripts/python.exe tools/wo_1b_sweep.py --mock-only

Output: tools/playtest_runs/wo_1b_results.json + a markdown table on
stdout. Run dirs land under tools/playtest_runs/1b-<arm>-<seed>-r<k>/.

The two live-parser arms (weird_live_voice, weird_live_voice2) spend real
API tokens and are NONDETERMINISTIC by nature — their repeats measure parse
variance, not engine variance, and they are excluded from the funnel bands
(both are fighting-shaped torture arms; the funnel question is decided by
the mock arms).
"""

import argparse
import concurrent.futures
import json
import statistics
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
DRIVER = REPO_ROOT / "tools" / "playtest_driver.py"
RUNS = REPO_ROOT / "tools" / "playtest_runs"

# arm -> (script, turns, live?)  — turns match the original Aug-16 runs.
ARMS = {
    "absurdist": ("weird_absurdist.json", 30, False),
    "eagle": ("weird_eagle_in_chains.json", 30, False),
    "tyrant": ("weird_tyrant.json", 30, False),
    "merchant": ("weird_merchant.json", 30, False),
    "admiral": ("weird_admiral.json", 30, False),
    "kingmaker": ("weird_kingmaker.json", 30, False),
    "pacifist": ("weird_pacifist.json", 30, False),
    "worldburns": ("weird_world_burns.json", 30, False),
    "livevoice": ("weird_live_voice.json", 10, True),
    "livevoice2": ("weird_live_voice2.json", 10, True),
}

# The §1 funnel classification (the memo's own grouping): arms whose premise
# fights vs arms whose premise is anything else. The Pacifist's premise is
# zero attacks — non-military BY PREMISE even though jealousy fought for it.
FIGHTING_ARMS = ["absurdist", "eagle", "tyrant", "worldburns"]
NON_MILITARY_ARMS = ["merchant", "admiral", "kingmaker", "pacifist"]

SEEDS = ["historical", "ulm", "austerlitz"]
REPEATS = 3


def run_one(arm, seed, repeat):
    script, turns, _live = ARMS[arm]
    name = f"1b-{arm}-{seed}-r{repeat}"
    cmd = [str(PYTHON), str(DRIVER),
           "--script", str(REPO_ROOT / "tools" / "playtest_scripts" / script),
           "--seed", seed, "--turns", str(turns),
           "--name", name, "--fresh"]
    env = {"PYTHONHASHSEED": "0"}
    import os
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              env=os.environ | env, timeout=3600)
        returncode = proc.returncode
    except subprocess.TimeoutExpired:
        # A frozen child (e.g. the Windows asyncio socketpair race under
        # heavy process concurrency, seen Aug 21) must become a ROW, not
        # a crashed sweep — blocked is reported, never silently dropped.
        returncode = "timeout"
    out_dir = RUNS / name
    row = {"arm": arm, "seed": seed, "repeat": repeat, "name": name,
           "exit": returncode}
    try:
        meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
        row["status"] = meta.get("status")
        row["counters"] = meta.get("counters")
        row["unknown_blockers"] = len(meta.get("unknown_blockers") or [])
    except Exception as exc:  # noqa: BLE001 — a sweep row must never vanish
        row["status"] = f"meta-unreadable ({exc})"
    provinces = treasury = None
    estate_seen = False
    try:
        for line in (out_dir / "digest.jsonl").open(encoding="utf-8"):
            rec = json.loads(line)
            if rec.get("kind") == "ledger":
                provinces = rec.get("provinces", provinces)
                treasury = rec.get("treasury", treasury)
            if (rec.get("kind") == "popup"
                    and str(rec.get("key", "")).startswith(
                        "capture_choice[estate]")):
                estate_seen = True
    except Exception:
        pass
    row["final_provinces"] = provinces
    row["final_treasury"] = treasury
    row["estate_stage_answered"] = estate_seen
    print(f"[1b] {name}: {row['status']} provinces={provinces} "
          f"treasury={treasury}", flush=True)
    return row


def collect_one(arm, seed, repeat):
    """Row from an EXISTING run dir — the --reassemble path (used after
    the Aug-21 sweep, when five pacifist children froze in asyncio's
    Windows socketpair fallback under ~25 concurrent python processes and
    were killed + re-run; not a game or driver defect — determinism was
    verified by byte-prefix diff against the completed sibling repeat)."""
    name = f"1b-{arm}-{seed}-r{repeat}"
    out_dir = RUNS / name
    row = {"arm": arm, "seed": seed, "repeat": repeat, "name": name,
           "exit": None}
    try:
        meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
        row["status"] = meta.get("status")
        row["counters"] = meta.get("counters")
        row["unknown_blockers"] = len(meta.get("unknown_blockers") or [])
    except Exception as exc:  # noqa: BLE001
        row["status"] = f"meta-unreadable ({exc})"
    provinces = treasury = None
    estate_seen = False
    try:
        for line in (out_dir / "digest.jsonl").open(encoding="utf-8"):
            rec = json.loads(line)
            if rec.get("kind") == "ledger":
                provinces = rec.get("provinces", provinces)
                treasury = rec.get("treasury", treasury)
            if (rec.get("kind") == "popup"
                    and str(rec.get("key", "")).startswith(
                        "capture_choice[estate]")):
                estate_seen = True
    except Exception:
        pass
    row["final_provinces"] = provinces
    row["final_treasury"] = treasury
    row["estate_stage_answered"] = estate_seen
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock-only", action="store_true")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--only", default="",
                    help="comma-separated arm names to (re)run")
    ap.add_argument("--reassemble", action="store_true",
                    help="rebuild the table/results from EXISTING run dirs "
                         "without running anything")
    args = ap.parse_args()

    jobs = []
    only = {a for a in args.only.split(",") if a.strip()}
    for arm, (_s, _t, live) in ARMS.items():
        if live and args.mock_only:
            continue
        if only and arm not in only:
            continue
        for seed in SEEDS:
            for repeat in range(1, REPEATS + 1):
                jobs.append((arm, seed, repeat))

    rows = []
    if args.reassemble:
        for arm in ARMS:
            for seed in SEEDS:
                for repeat in range(1, REPEATS + 1):
                    rows.append(collect_one(arm, seed, repeat))
    else:
        # Live-parser jobs are throttled implicitly by their own API
        # latency; the pool size bounds total concurrency either way.
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=args.jobs) as pool:
            futures = [pool.submit(run_one, *job) for job in jobs]
            for future in concurrent.futures.as_completed(futures):
                rows.append(future.result())

    results_path = RUNS / "wo_1b_results.json"
    results_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    # ── The addendum table ────────────────────────────────────────────
    print("\n| arm | class | median | min–max | statuses | repeats identical |")
    print("|---|---|---|---|---|---|")
    verdict_inputs = {}
    for arm in ARMS:
        arm_rows = [r for r in rows if r["arm"] == arm]
        if not arm_rows:
            continue
        vals = [r["final_provinces"] for r in arm_rows
                if r["final_provinces"] is not None]
        statuses = sorted({str(r["status"]) for r in arm_rows})
        # Determinism check: per (seed) the three repeats must agree (mock).
        identical = True
        for seed in SEEDS:
            per_seed = [r["final_provinces"] for r in arm_rows
                        if r["seed"] == seed]
            if len(set(map(str, per_seed))) > 1:
                identical = False
        med = statistics.median(vals) if vals else None
        lo, hi = (min(vals), max(vals)) if vals else (None, None)
        klass = ("fighting" if arm in FIGHTING_ARMS
                 else "non-military" if arm in NON_MILITARY_ARMS
                 else "live (excluded)")
        if arm in FIGHTING_ARMS or arm in NON_MILITARY_ARMS:
            verdict_inputs[arm] = (med, lo, hi)
        print(f"| {arm} | {klass} | {med} | {lo}–{hi} | "
              f"{'/'.join(statuses)} | {identical} |")

    fighting = {a: v for a, v in verdict_inputs.items() if a in FIGHTING_ARMS}
    nonmil = {a: v for a, v in verdict_inputs.items()
              if a in NON_MILITARY_ARMS}
    if fighting and nonmil:
        worst_f = min(fighting.items(), key=lambda kv: kv[1][0])
        best_n = max(nonmil.items(), key=lambda kv: kv[1][0])
        medians_separate = worst_f[1][0] > best_n[1][0]
        # Band overlap: worst fighting arm's min vs best non-military's max.
        bands_disjoint = worst_f[1][1] > best_n[1][2]
        print(f"\nworst fighting arm: {worst_f[0]} median {worst_f[1][0]} "
              f"(min {worst_f[1][1]})")
        print(f"best non-military arm: {best_n[0]} median {best_n[1][0]} "
              f"(max {best_n[1][2]})")
        print(f"medians separate: {medians_separate} · bands disjoint: "
              f"{bands_disjoint}")
        print("FUNNEL VERDICT: " + ("STANDS" if medians_separate
                                    and bands_disjoint else "WITHDRAWN"))
    estate_runs = [r["name"] for r in rows if r["estate_stage_answered"]]
    print(f"\nestate stage answered in {len(estate_runs)} run(s): "
          f"{estate_runs[:6]}")
    print(f"results: {results_path}")


if __name__ == "__main__":
    main()
