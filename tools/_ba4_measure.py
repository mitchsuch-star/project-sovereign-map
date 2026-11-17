"""Row BA, BA-4 — the roads and the fog (BATTLE_DIORAMA_SPEC.md §15.19;
November 16, 2026): the session's ONE measure, with arms, on every surface a
rule of the session can move. After `tools/_g5_measure.py` (the three gate
surfaces) and `tools/_ba3_measure.py` (the commanded band and the day's sweep).

BA-3 moved nothing outside a campaign the server holds; BA-4's rules move
world-lines nobody serves (the AI's fairness tally, the battery's own roll,
the roads, the pursuit, the last hour), so the deploy gate is read again whole.

THE ARMS — cumulative, each bringing ONE seam up over the arm before it:

    HEAD      no seam passed at all: the untouched tree (M0, the control —
              the seams do not exist there)
    0         every BA-4 seam DOWN — must reproduce HEAD on every surface
    X2        a corps raised mid-phase takes its turn         (BA2-X2)
    X12       a battery is spared its own shells              (BA2-X12)
    X10       a road round keeps to open frontiers            (BA2-X10)
    APPROACH  a support order halts before the friend's foe   (ruled IN)
    X20       a battle lights its field for those who fought  (BA2-X20)
    PURSUIT   a pursuit is any corps that fought              (§15.5.7)
    QUARTERS  the last hour brings three quarters             (§15.5.7)
    TELL      the rows that move no number, together — must read as QUARTERS
    OFFER     the day takes only the order its table offers   (BA4-X1) — must
              read as TELL (no arm of the measure sends another)
    X13       a dead day bars nothing                         (BA3-X13)
    X16       an order draws its own temper                   (BA3-X16)
    X15       a lead holds one day                            (BA3-X15)
    X14       his word is scored from the day — the shipped tree (alias ALL)

THE SURFACES (`--surfaces`, each a chain run ALONE — no backend, test or deck
edit lands while it runs; THIS PARENT RUNS PLAIN, never `-X utf8`):

    probe    the keyed world probe (jena and marengo, 40 ambient turns) under
             `INK_IRON_SEAMS`, each arm compared with the HEAD copy's rows
             (`--probe-base DIR` holding probe_head_<seed>.json) and with the
             arm before it
    ambient  the ten SWEEP_SEEDS x 40 turns (`tools/_t3_4_measure.py`): a DY
             signature record and a census per arm
    d        the AI-France harness (`tools/_t3_5_chain_d.py`), ONE record
    band     the commanded arms CMD-H / CMD-A / CMD-M through the driver's own
             `--seam` — France's provinces on the last ledger row
    sweep    BA-3's eight-seed sweep of the day (its nine arms) with this
             run's `--sweep-arm` seams held as well: `0` must equal
             tools/_ba3_sweep_2026_11_15.json cell for cell; `X14` is the
             shipped tree
    kbar     the key-bar ladder (M6): `--bars` x {S, L} x eight seeds with the
             day's own rows (how rich, how varied, how rested)
    gate     no run: the deploy gate's clauses read off the records written

THE KEY BAR (`--key-bar`, the two SERVED surfaces — band and sweep). The bar a
battle must reach to be fought on as a day is no switch but a number, and M6
picked 50,000 men where the game had the great battle's 80,000
(`battle_day.key_bar`). The ladder was read while the game's bar was still
80,000 — so the records of November 16 name no bar among an arm's seams —
and then X14 once more with the picked bar in the game (`--stamp
2026_11_16_k50`). From the final tree the first reading is `--key-bar 80000`
(the default: every arm holds the bar where the ladder was read, and arm 0 is
the commit before again) and the second `--key-bar shipped`. The probe, the
ambient sweep and the harness serve no campaign and see no bar.

    .venv/Scripts/python.exe tools/_ba4_measure.py --arms 0,X2,...,X14
        --surfaces probe,ambient,d,band [--stamp 2026_11_16] [--jobs 3]
    .venv/Scripts/python.exe tools/_ba4_measure.py --arms X14 --surfaces band,sweep
        --key-bar shipped --stamp 2026_11_16_k50
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

BD = "backend.game_logic.battle_day"
CE = "backend.commands.combat_executor"
ST = "backend.commands.strategic"
# arm -> the seams it brings UP (the ladder's order is the dict's order)
LADDER = {
    "X2": ["backend.ai.enemy_ai:a_corps_raised_mid_phase_takes_its_turn"],
    "X12": [f"{CE}:a_battery_is_spared_its_own_shells"],
    "X10": [f"{ST}:a_road_round_keeps_to_open_frontiers"],
    "APPROACH": [f"{ST}:a_support_order_halts_before_the_friends_foe"],
    "X20": ["backend.game_logic.intel_surfaces:a_battle_lights_its_field_only_for_those_who_fought"],
    "PURSUIT": [f"{CE}:a_pursuit_is_any_corps_that_fought"],
    "QUARTERS": [f"{CE}:the_last_hour_brings_three_quarters"],
    "TELL": [f"{CE}:the_muster_names_only_an_order_that_brings",
             f"{BD}:a_day_is_one_battle", f"{BD}:a_days_close_is_told",
             f"{BD}:a_word_is_quoted_in_points"],
    "OFFER": [f"{BD}:a_brought_up_corps_is_one_the_table_offers"],
    "X13": [f"{BD}:a_dead_day_bars_nothing"],
    "X16": ["backend.game_logic.campaign_variance:an_order_draws_its_own_temper"],
    "X15": [f"{BD}:a_lead_holds_one_day"],
    "X14": [f"{BD}:his_word_is_scored_from_the_day"],
}
ORDER = ["0"] + list(LADDER)
ALIASES = {"ALL": "X14"}
# The key bar: a number, not a switch (the module's word). The served surfaces
# hold it at the bar the ladder was read at unless `--key-bar shipped`.
KEY_BAR_SEAM = f"{BD}:key_bar"
LADDER_BAR = 80000
UNSERVED = ["0", "X2", "X12", "X10", "APPROACH", "X20", "PURSUIT", "QUARTERS", "TELL", "X14"]
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
ARM0_BAND = {"CMD-H": 28, "CMD-A": 27, "CMD-M": 27}
SWEEP_SEEDS8 = ("jena", "wagram", "lodi", "eylau", "friedland")
BA3_SWEEP = TOOLS / "_ba3_sweep_2026_11_15.json"
PROBE_SEEDS = ("jena", "marengo")
PROBE_TURNS = 40
MAX_JOBS = 4


def canon(arm: str) -> str:
    return ALIASES.get(arm, arm)


def down(arm: str) -> list:
    """The seams an arm holds DOWN: every seam of a later arm. `HEAD` passes
    none (the seams do not exist on the untouched tree)."""
    arm = canon(arm)
    if arm == "HEAD":
        return []
    later = ORDER[ORDER.index(arm) + 1:]
    return [f"{spec}=False" for name in later for spec in LADDER[name]]


def bar_held(key_bar) -> list:
    """The seam that holds the key bar for a served surface: none for
    `shipped` (the game's own bar), else the bar itself."""
    if str(key_bar).strip().lower() in ("", "shipped"):
        return []
    return [f"{KEY_BAR_SEAM}={int(key_bar)}"]


def _run(cmd, seams: str = "", env_extra=None) -> int:
    env = dict(os.environ)
    env.pop("INK_IRON_SEAMS", None)
    env.pop("PYTHONHASHSEED", None)
    if seams:
        env["INK_IRON_SEAMS"] = seams
    env.update(env_extra or {})
    print("[ba4]", " ".join(str(c) for c in cmd), f"(seams down: {seams.count('=')})", flush=True)
    return subprocess.run([sys.executable, *map(str, cmd)], cwd=str(ROOT), env=env).returncode


def _write(path: pathlib.Path, record: dict) -> None:
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[ba4] written {path}", flush=True)


def _label(arm: str) -> str:
    return "ba4_" + canon(arm).lower()


# ── the keyed world probe ────────────────────────────────────────────────────

def probe(arms, stamp: str, base_dir: pathlib.Path, run_dir: pathlib.Path) -> dict:
    sys.path.insert(0, str(ROOT))
    from tools.keyed_world_probe import first_difference

    run_dir.mkdir(parents=True, exist_ok=True)
    record = {"_note": ("Row BA, BA-4 — the keyed world probe per arm (jena and marengo, "
                        f"{PROBE_TURNS} ambient turns, one hash per top-level key of to_dict a "
                        "turn): `vs_head` compares the arm with a `git archive HEAD` copy's rows, "
                        "`vs_before` with the arm before it in this run. `crashes` counts a "
                        "court's lost turn (BA2-X2). Written by tools/_ba4_measure.py."),
              "turns": PROBE_TURNS, "arms": {}}
    rows, before = {}, None
    for arm in arms:
        record["arms"][arm] = {"seams_down": down(arm)}
        rows[arm] = {}
        for seed in PROBE_SEEDS:
            out = run_dir / f"probe_{canon(arm)}_{seed}.json"
            rc = _run([TOOLS / "keyed_world_probe.py", "run", ROOT, seed, PROBE_TURNS, out],
                      seams=";".join(down(arm)), env_extra={"PYTHONHASHSEED": "0"})
            if rc != 0:
                raise SystemExit(f"[ba4] probe {arm} {seed} failed (rc {rc})")
            got = json.loads(out.read_text(encoding="utf-8"))
            rows[arm][seed] = got["rows"]
            cell = {"crashes": int(got.get("crashes", 0)), "keys": int(got.get("keys", 0))}
            head_file = base_dir / f"probe_head_{seed}.json"
            if head_file.exists():
                head = json.loads(head_file.read_text(encoding="utf-8"))
                cell["head_crashes"] = int(head.get("crashes", 0))
                cell["vs_head"] = _difference(first_difference(head["rows"], got["rows"]))
            if before is not None:
                cell["vs_before"] = _difference(first_difference(rows[before][seed], got["rows"]))
                cell["before"] = before
            record["arms"][arm][seed] = cell
            print(f"[ba4] probe {arm} {seed}: {cell}", flush=True)
        before = arm
    _write(TOOLS / f"_ba4_probe_{stamp}.json", record)
    return record


def _difference(found) -> dict:
    if found is None:
        return {"identical": True}
    turn, keys = found
    return {"identical": False, "first_turn": int(turn), "keys": list(keys)}


# ── the ambient sweep and the AI-France harness ──────────────────────────────

def ambient(arms, stamp: str, turns: int) -> None:
    for arm in arms:
        label = _label(arm)
        rc = _run([TOOLS / "_t3_4_measure.py", "--turns", turns, "--label", label.replace("_", "-"),
                   "--out", TOOLS / f"_dy_signature_{label}_{stamp}.json",
                   "--census", TOOLS / f"_{label}_census_{stamp}.json"],
                  seams=";".join(down(arm)))
        if rc != 0:
            raise SystemExit(f"[ba4] ambient {arm} failed (rc {rc})")


def chain_d(arms, stamp: str, turns: int, tag: str = "") -> None:
    cmd = [TOOLS / "_t3_5_chain_d.py", "--turns", turns, "--arms", ",".join(canon(a) for a in arms),
           "--out", TOOLS / f"_ba4_chain_d{tag}_{stamp}.json",
           "--run-dir", TOOLS / "playtest_runs" / f"ba4_chain_d{tag}"]
    for arm in arms:
        if down(arm):
            cmd += ["--arm-seams", f"{canon(arm)}={';'.join(down(arm))}"]
    rc = _run(cmd)
    if rc != 0:
        raise SystemExit(f"[ba4] chain d failed (rc {rc})")


# ── the commanded band, the day's sweep, the key bar ─────────────────────────

def _driven(tasks, jobs: int, tag: str):
    """[(group, name, dir, argv)] -> [(group, name, reading)] through the
    driver, `_ba3_measure`'s own reading (a failed run is a failure, never 0)."""
    sys.path.insert(0, str(ROOT))
    from tools import _ba3_measure as B3
    from tools import score_run as SR

    def _one(task):
        group, name, where, argv = task
        print(f"[ba4] {tag} {group} {name} ...", flush=True)
        try:
            result = SR._run_driver(ROOT, where, name, argv)
        except Exception as exc:
            result = {"exit": -1, "status": f"driver-error {exc!r}"[:120]}
        reading = B3._read(where, name, result)
        reading["days"] = _day_rows(where / name)
        if not reading["ok"]:
            print(f"[ba4] {tag} {group} {name} FAILED: {reading['status']!r}", flush=True)
        return group, name, reading

    with ThreadPoolExecutor(max_workers=max(1, min(jobs, MAX_JOBS))) as pool:
        return list(pool.map(_one, tasks))


def _day_rows(run: pathlib.Path) -> list:
    """The driver's `day` rows (one a day of battle met, with its lit words)."""
    try:
        rows = [json.loads(line) for line in (run / "digest.jsonl")
                .read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        return []
    keep = ("turn", "field", "enemy", "lead", "side", "ours", "theirs", "chips", "priced", "men")
    return [{k: r.get(k) for k in keep} for r in rows if r.get("kind") == "day"]


def _flags(seams) -> list:
    return [flag for spec in seams for flag in ("--seam", spec)]


def band(arms, stamp: str, jobs: int, tag: str = "", key_bar=LADDER_BAR) -> dict:
    sys.path.insert(0, str(ROOT))
    from tools import score_run as SR

    held_bar = bar_held(key_bar)
    run_dir = TOOLS / "playtest_runs" / f"ba4_band{tag}"
    record = {"_note": ("Row BA, BA-4 — the France band on the commanded arms (DYNAMISM_SPEC.md "
                        "§2: the deploy gate's difficulty guard, 23–28): score_run's CMD-H / CMD-A "
                        "/ CMD-M (commanded_full40.json, forty turns, the mock parser, silent on a "
                        "day) per arm of the BA-4 ladder — France's provinces on the last ledger "
                        "row. Arm 0 (every BA-4 seam down) and arm HEAD (the untouched tree) must "
                        "read 28 / 27 / 27, BA-3's shipped reading. Written by "
                        "tools/_ba4_measure.py --surfaces band (a chain run ALONE)."),
              "band": list(BAND), "key_bar": str(key_bar), "arms": {}}
    tasks = []
    for arm in arms:
        where = run_dir / canon(arm)
        where.mkdir(parents=True, exist_ok=True)
        record["arms"][arm] = {"seams_down": down(arm) + held_bar}
        for name in BAND_ARMS:
            tasks.append((arm, name, where,
                          list(SR.ARMS[name]["argv"]) + _flags(down(arm) + held_bar)))
    for arm, name, reading in _driven(tasks, jobs, "band"):
        record["arms"][arm][name] = reading
    _write(TOOLS / f"_ba4_band{tag}_{stamp}.json", record)
    for arm in arms:
        print(f"[ba4] band {arm:<9}" + "  ".join(
            f"{n} {record['arms'][arm][n]['provinces']}" for n in BAND_ARMS), flush=True)
    for arm in ("HEAD", "0"):
        if arm in record["arms"]:
            got = {n: record["arms"][arm][n]["provinces"] for n in BAND_ARMS}
            if got != ARM0_BAND:
                print(f"[ba4] STOP: arm {arm} does not reproduce the band {ARM0_BAND}: got {got}.",
                      flush=True)
                raise SystemExit(2)
    return record


def sweep(arm: str, stamp: str, jobs: int, day_arms, key_bar=LADDER_BAR) -> dict:
    """BA-3's own sweep (its arms, its seeds) with `arm`'s seams held too —
    and the key bar where `--key-bar` puts it."""
    sys.path.insert(0, str(ROOT))
    from tools import _ba3_measure as B3
    from tools import score_run as SR

    held = down(arm) + bar_held(key_bar)
    run_dir = TOOLS / "playtest_runs" / f"ba4_sweep_{canon(arm).lower()}"
    seeds = [n for n, _ in B3._seed_runs(SR, SWEEP_SEEDS8)]
    record = {"_note": ("Row BA, BA-4 — BA-3's eight-seed sweep of the day (its arms, its seeds, "
                        f"its reading) taken again with the BA-4 ladder at arm {canon(arm)} "
                        f"({len(held)} BA-4 seams held down). Arm 0 of the ladder must equal "
                        "tools/_ba3_sweep_2026_11_15.json cell for cell; arm X14 is the shipped "
                        "tree, on which §15.16's rule is checked again. Written by "
                        "tools/_ba4_measure.py --surfaces sweep (a chain run ALONE)."),
              "band": list(BAND), "seeds": seeds, "ladder_arm": canon(arm), "held_down": held,
              "arms": {}}
    tasks = []
    for day_arm in day_arms:
        seams, rounds = B3.ARMS[day_arm]
        where = run_dir / day_arm
        where.mkdir(parents=True, exist_ok=True)
        extra = _flags(list(seams) + held) + (["--rounds", rounds] if rounds else [])
        record["arms"][day_arm] = {"seams": list(seams), "rounds": rounds or "(absent)"}
        for name, argv in B3._seed_runs(SR, SWEEP_SEEDS8):
            tasks.append((day_arm, name, where, argv + extra))
    for day_arm, name, reading in _driven(tasks, jobs, f"sweep[{canon(arm)}]"):
        record["arms"][day_arm][name] = reading
    record["deltas_vs_T"] = B3._deltas(record, "T")
    record["deltas_vs_0"] = B3._deltas(record, "0")
    _write(TOOLS / f"_ba4_sweep_{canon(arm).lower()}_{stamp}.json", record)
    print(B3._table(record), flush=True)
    print(B3._delta_table(record, "deltas_vs_T", "T"), flush=True)
    if canon(arm) == "0" and BA3_SWEEP.exists():
        prior = json.loads(BA3_SWEEP.read_text(encoding="utf-8"))
        moved = [(a, n, prior["arms"][a][n]["provinces"], record["arms"][a][n]["provinces"])
                 for a in record["arms"] if a in prior["arms"] for n in seeds
                 if (prior["arms"][a][n]["provinces"], prior["arms"][a][n]["status"])
                 != (record["arms"][a][n]["provinces"], record["arms"][a][n]["status"])]
        print(f"[ba4] sweep arm 0 against the sweep of record: {len(moved)} cell(s) differ "
              f"{moved[:12]}", flush=True)
        if moved:
            raise SystemExit(2)
    return record


def kbar(bars, stamp: str, jobs: int) -> dict:
    """M6 — the key-bar ladder on the shipped tree: the silent arm and "left
    to the marshal", eight seeds a bar, each day's own row kept."""
    sys.path.insert(0, str(ROOT))
    from tools import _ba3_measure as B3
    from tools import score_run as SR

    run_dir = TOOLS / "playtest_runs" / "ba4_kbar"
    seeds = [n for n, _ in B3._seed_runs(SR, SWEEP_SEEDS8)]
    record = {"_note": ("Row BA, BA-4 — the key-bar ladder (M6, BATTLE_DIORAMA_SPEC.md §15.19): "
                        "the bar a battle must reach to be fought with the day's points, read on "
                        "the shipped tree — `--rounds none` (S) and `leave` (L), the three "
                        "commanded seeds and five more, forty turns. Each run keeps the driver's "
                        "`day` rows. The rule was written before this record. Written by "
                        "tools/_ba4_measure.py --surfaces kbar (a chain run ALONE)."),
              "band": list(BAND), "seeds": seeds, "bars": {}}
    tasks = []
    for bar in bars:
        record["bars"][str(bar)] = {"S": {}, "L": {}}
        for mode, rounds in (("S", "none"), ("L", "leave")):
            where = run_dir / f"K{bar}" / mode
            where.mkdir(parents=True, exist_ok=True)
            extra = ["--seam", f"{BD}:key_bar={int(bar)}", "--rounds", rounds]
            for name, argv in B3._seed_runs(SR, SWEEP_SEEDS8):
                tasks.append(((str(bar), mode), name, where, argv + extra))
    for (bar, mode), name, reading in _driven(tasks, jobs, "kbar"):
        record["bars"][bar][mode][name] = reading
    for bar in record["bars"]:
        record["bars"][bar]["rule"] = fun_rule(record["bars"][bar], seeds)
        print(f"[ba4] kbar {bar}: {json.dumps(record['bars'][bar]['rule'])}", flush=True)
    _write(TOOLS / f"_ba4_kbar_{stamp}.json", record)
    return record


def fun_rule(cell: dict, seeds) -> dict:
    """The rule written in the plan BEFORE the data: rich, varied, rested,
    balanced. Returns each clause's figure and whether it passes."""
    runs = [(mode, name, cell[mode][name]) for mode in ("S", "L") for name in seeds
            if cell[mode].get(name, {}).get("ok")]
    days = [(mode, name, d) for mode, name, r in runs for d in r.get("days") or []]
    rich = sum(1 for _, _, d in days if int(d.get("priced") or 0) >= 4)
    repeats = 0
    for mode, name, r in runs:
        seen = []
        for d in sorted(r.get("days") or [], key=lambda d: int(d.get("turn") or 0)):
            pair, turn = (d.get("lead"), d.get("enemy")), int(d.get("turn") or 0)
            if any(p == pair and 0 <= turn - t <= 2 for p, t in seen):
                repeats += 1
            seen.append((pair, turn))
    per_run = [len(r.get("days") or []) for _, _, r in runs]
    four_running = 0
    for _, _, r in runs:
        turns = sorted({int(d.get("turn") or 0) for d in r.get("days") or []})
        if any(all(t + k in turns for k in range(4)) for t in turns):
            four_running += 1
    band_s = {n: cell["S"].get(n, {}).get("provinces") for n in BAND_ARMS}
    n_days = len(days)
    out = {
        "runs": len(runs), "days": n_days,
        "rich_share": round(rich / n_days, 3) if n_days else None,
        "repeat_share": round(repeats / n_days, 3) if n_days else None,
        "days_per_campaign": round(sum(per_run) / len(per_run), 2) if per_run else None,
        "campaigns_with_four_turns_running": four_running,
        "band_silent": band_s,
    }
    out["rich"] = bool(n_days) and rich * 3 >= n_days * 2
    out["varied"] = bool(n_days) and repeats * 5 <= n_days
    out["rested"] = bool(per_run) and sum(per_run) <= 8 * len(per_run) and four_running <= 1
    out["band_in"] = all(v is not None and BAND[0] <= v <= BAND[1] for v in band_s.values())
    return out


# ── the gate, read off the records ───────────────────────────────────────────

def gate(arms, stamp: str) -> dict:
    out = {}
    for arm in arms:
        label = _label(arm)
        sig_file = TOOLS / f"_dy_signature_{label}_{stamp}.json"
        cen_file = TOOLS / f"_{label}_census_{stamp}.json"
        if not (sig_file.exists() and cen_file.exists()):
            continue
        sig = json.loads(sig_file.read_text(encoding="utf-8"))
        cen = json.loads(cen_file.read_text(encoding="utf-8"))
        promoted = {s: v["signature"]["rank_promotions"] for s, v in sig["seeds"].items()
                    if v["signature"]["rank_promotions"]}
        rosters = {s: tuple(n for _, n in v["signature"]["eliminations"])
                   for s, v in sig["seeds"].items()}
        out[arm] = {
            "story_classes": int(sig["story_class_count"]),
            "promotions": promoted,
            "roster_readings": len(set(rosters.values())),
            "rosters": {s: list(r) for s, r in rosters.items()},
            "annexations_outside_aim": int(cen["totals"]["annexations_outside_aim"]),
            "captures_outside_aim": int(cen["totals"]["captures_outside_aim"]),
        }
        out[arm]["met"] = (out[arm]["story_classes"] >= 6 and bool(promoted)
                           and out[arm]["roster_readings"] >= 2
                           and out[arm]["annexations_outside_aim"] == 0)
        print(f"[ba4] gate {arm}: classes {out[arm]['story_classes']}, promotions "
              f"{promoted}, roster readings {out[arm]['roster_readings']}, annexations "
              f"{out[arm]['annexations_outside_aim']} -> {'MET' if out[arm]['met'] else 'NOT MET'}",
              flush=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ORDER))
    ap.add_argument("--surfaces", default="probe,ambient,d,band")
    ap.add_argument("--stamp", default="2026_11_16")
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--tag", default="", help="a suffix for the band / chain-d records (e.g. _control)")
    ap.add_argument("--probe-base", default="", help="the folder holding probe_head_<seed>.json")
    ap.add_argument("--probe-runs", default=str(TOOLS / "playtest_runs" / "ba4_probe"))
    ap.add_argument("--sweep-arm", default="X14", help="the ladder arm the day's sweep is taken at")
    ap.add_argument("--day-arms", default="0,T,S,L,P,D,B,G,ALL")
    ap.add_argument("--bars", default="50000,60000,70000,80000")
    ap.add_argument("--key-bar", default=str(LADDER_BAR),
                    help="band and sweep: the bar a battle must reach to be fought on as a day — "
                         "80000 (the default: the bar the ladder was read at) or `shipped` (the "
                         "game's own, M6's pick)")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    unknown = [a for a in arms if canon(a) not in ORDER + ["HEAD"]]
    if unknown:
        raise SystemExit(f"[ba4] unknown arm(s) {unknown}; known: HEAD, {ORDER}, ALL")
    surfaces = set(args.surfaces.split(","))
    if "probe" in surfaces:
        probe(arms, args.stamp, pathlib.Path(args.probe_base or "."), pathlib.Path(args.probe_runs))
    if "ambient" in surfaces:
        ambient(arms, args.stamp, args.turns)
    if "d" in surfaces:
        chain_d(arms, args.stamp, args.turns, args.tag)
    if "band" in surfaces:
        band(arms, args.stamp, args.jobs, args.tag, args.key_bar)
    if "sweep" in surfaces:
        sweep(args.sweep_arm, args.stamp, args.jobs, [a for a in args.day_arms.split(",") if a],
              args.key_bar)
    if "kbar" in surfaces:
        kbar([int(b) for b in args.bars.split(",") if b], args.stamp, args.jobs)
    if "gate" in surfaces:
        gate(arms, args.stamp)
    print("[ba4] done", flush=True)


if __name__ == "__main__":
    main()
