"""Row BA, BA-5 — "the finish" (BATTLE_DIORAMA_SPEC.md §15.22–§15.23; November
17, 2026): the session's ONE measure, with arms, after `tools/_ba4_measure.py`
(whose helpers it uses) and `tools/_ba3_measure.py` (the day's sweep).

THE ARMS — cumulative, each bringing its seams UP over the arm before it:

    HEAD      no seam passed: an untouched copy of the commit before
              (`git archive 1b5bc533`) — the probe's base rows only
    0         every BA-5 seam DOWN — must reproduce the commit before on every
              surface (the probe key for key, the band, the day's sweep cell
              for cell against tools/_ba4_sweep_x14_2026_11_16_k50.json)
    TELL      the rows that move no number of the game, together: D1 (our
              table reads the day as our clash left it), the telling's five
              seams, the truce's named ground, the news' commanders, a
              marshal's days, the ground on the table, the first day's line
              on its first table, and (the session's review) a rout told only
              where the battle made it
    ONEDAY    BA5-X1: "one day a lead" is read as the lead stood when the
              battle began
    OWNWAY    the session's review: a word's battle is its own clash (an
              objection answered "his own way" against another corps is no
              clash of the day) — the one rung after ONEDAY that can move a
              number, on that one road
    RESERVE   the reserve's seam as the tree has it (alias ALL: no seam
              passed). Since the rule's reading the reserve is PARKED — down
              in the game — so this arm IS every rung before it up and the
              reserve down: the tree as shipped. Every record of the final
              chain was read on that tree.
    R2000 R3000 R5000
              the reserve ARMED (`battle_day:the_reserve_pursues=True`) with
              its number held at a ladder value (`battle_day:reserve_pursuit=<n>`
              — a number, not a switch); both are passed

THE SURFACES (`--surfaces`, each a chain run ALONE — no backend, test or deck
edit lands while it runs; THIS PARENT RUNS PLAIN, never `-X utf8`):

    probe    the keyed world probe (jena and marengo, 40 ambient turns) under
             `INK_IRON_SEAMS`: each arm against the HEAD copy's rows
             (`--probe-base DIR` holding probe_head_<seed>.json) — and, where
             an arm differs, EVERY key that differs on any turn (the telling
             moves words, never a number: the keys say which)
    ambient  the ten SWEEP_SEEDS x 40 turns (`tools/_t3_4_measure.py`): a DY
             signature record and a census per arm
    d        the AI-France harness (`tools/_t3_5_chain_d.py`), ONE record
    band     the commanded arms CMD-H / CMD-A / CMD-M at the game's own key bar
    sweep    BA-3's eight-seed sweep of the day (its nine arms) at one ladder
             arm (`--sweep-arm`), each run's reserve tally kept
    rule     no run: the reserve's rule, written in the plan BEFORE the data,
             read off the sweep and band records of R2000 / R3000 / R5000, with
             the reserve-down baseline read off the sweep at ALL
    gate     no run: the deploy gate's clauses off the ambient records

THE RESERVE'S RULE (pre-registered, plan of November 16–17, 2026). The number
becomes the LOWEST of 2,000 / 3,000 / 5,000 men a point at which, over BA-3's
eight seeds and its ways of playing a day:
  (i)   the reserve pursues on at least eight days (it is felt);
  (ii)  no way of playing is best on more than five seeds, and neither pressing
        nor the Guard stops being best anywhere (neither is made pointless);
  (iii) of the men it takes, neither side takes more than three quarters;
  (iv)  the band stays inside 23–28 on the commanded seeds;
  (v)   the hand stays healthy (§15.16: no arm's mean delta against `T` reaches
        +3 or -3; no arm best on six seeds or more).
If none passes the rule is NOT built. The table is reported per seed either
way, with the largest single pursuit seen.

    .venv/Scripts/python.exe tools/_ba5_measure.py --surfaces probe --arms 0,TELL,ALL
        --probe-base <dir>
    .venv/Scripts/python.exe tools/_ba5_measure.py --surfaces band --arms 0,ONEDAY,R2000,R3000,R5000
    .venv/Scripts/python.exe tools/_ba5_measure.py --surfaces sweep --sweep-arm R3000
    .venv/Scripts/python.exe tools/_ba5_measure.py --surfaces rule
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BD = "backend.game_logic.battle_day"
BT = "backend.game_logic.battle_telling"
LADDER = {
    "TELL": [f"{BD}:our_table_reads_the_day_as_our_clash_left_it",
             f"{BT}:the_day_tells_its_clashes", f"{BT}:a_word_says_what_it_does",
             f"{BT}:the_table_reads_him", f"{BT}:the_close_names_what_told",
             f"{BT}:a_verdict_names_what_told",
             "backend.game_logic.battle_report:a_rout_won_on_points_has_left_the_field",
             "backend.game_logic.diplomacy:a_truce_names_the_ground_it_would_title",
             "backend.game_logic.battle_news:a_great_battle_names_its_commanders",
             f"{BD}:a_marshal_keeps_his_days",
             f"{BD}:the_first_days_line_stands_on_its_first_table",
             "backend.game_logic.battle_diorama:the_table_shows_its_ground",
             "backend.game_logic.battle_script:a_rout_is_one_this_battle_made"],
    "ONEDAY": [f"{BD}:a_lead_holds_his_day_as_the_battle_began"],
    # the session's review: a word's battle is its own clash (one rare road can move a number)
    "OWNWAY": [f"{BD}:a_words_battle_is_its_own_clash"],
    "RESERVE": [f"{BD}:the_reserve_pursues"],
}
ORDER = ["0"] + list(LADDER)
RESERVE_LADDER = (2000, 3000, 5000)
STAMP = "2026_11_17"
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
ARM0_BAND = {"CMD-H": 28, "CMD-A": 28, "CMD-M": 27}      # BA-4's shipped reading (§15.20)
BA4_SWEEP = TOOLS / "_ba4_sweep_x14_2026_11_16_k50.json"   # the day's sweep on the commit before
SWEEP_SEEDS8 = ("jena", "wagram", "lodi", "eylau", "friedland")
PROBE_SEEDS = ("jena", "marengo")
PROBE_TURNS = 40
PLAYED = ("S", "L", "P", "D", "B", "G", "ALL")           # the ways of playing a day (§15.16)
RESERVE_FREE = ("0", "T")                                 # the day's seam down: no reserve can act


def held(arm: str) -> list:
    """The seams an arm holds: every seam of a later arm DOWN; for a ladder
    value, the reserve's number."""
    if arm in ("HEAD", "ALL"):
        return []
    if arm.startswith("R") and arm[1:].isdigit():
        return [f"{BD}:the_reserve_pursues=True", f"{BD}:reserve_pursuit={int(arm[1:])}"]
    later = ORDER[ORDER.index(arm) + 1:]
    return [f"{spec}=False" for name in later for spec in LADDER[name]]


def _known(arm: str) -> bool:
    return arm in ORDER or arm in ("HEAD", "ALL") or (arm.startswith("R") and arm[1:].isdigit())


def _label(arm: str) -> str:
    return "ba5_" + arm.lower()


# ── the keyed world probe ────────────────────────────────────────────────────

def _all_differences(a_rows: list, b_rows: list) -> dict:
    """{key: [first turn, turns on which it differs]} over the whole campaign."""
    out = {}
    for index, (a, b) in enumerate(zip(a_rows, b_rows), start=1):
        for key in sorted(set(a) | set(b)):
            if a.get(key) != b.get(key):
                cell = out.setdefault(key, [index, 0])
                cell[1] += 1
    return out


def probe(arms, stamp: str, base_dir: pathlib.Path, run_dir: pathlib.Path) -> dict:
    from tools import _ba4_measure as B4

    run_dir.mkdir(parents=True, exist_ok=True)
    record = {"_note": ("Row BA, BA-5 — the keyed world probe per arm (jena and marengo, "
                        f"{PROBE_TURNS} ambient turns, one hash per top-level key of to_dict a "
                        "turn) against the commit before's own rows (`git archive 1b5bc533`): "
                        "`vs_head` says identical or the first turn that differs, and `keys` "
                        "every key that differs on any turn with [first turn, turns]. The probe "
                        "serves no campaign: no day of battle is fought in it. Written by "
                        "tools/_ba5_measure.py."),
              "turns": PROBE_TURNS, "arms": {}}
    for arm in arms:
        record["arms"][arm] = {"seams_held": held(arm)}
        for seed in PROBE_SEEDS:
            out = run_dir / f"probe_{arm}_{seed}.json"
            rc = B4._run([TOOLS / "keyed_world_probe.py", "run", ROOT, seed, PROBE_TURNS, out],
                         seams=";".join(held(arm)), env_extra={"PYTHONHASHSEED": "0"})
            if rc != 0:
                raise SystemExit(f"[ba5] probe {arm} {seed} failed (rc {rc})")
            got = json.loads(out.read_text(encoding="utf-8"))
            cell = {"crashes": int(got.get("crashes", 0)), "keys_a_turn": int(got.get("keys", 0))}
            head_file = base_dir / f"probe_head_{seed}.json"
            if head_file.exists():
                head = json.loads(head_file.read_text(encoding="utf-8"))
                found = _all_differences(head["rows"], got["rows"])
                cell["head_crashes"] = int(head.get("crashes", 0))
                cell["vs_head"] = ({"identical": True} if not found else
                                   {"identical": False,
                                    "first_turn": min(v[0] for v in found.values())})
                cell["keys"] = found
            record["arms"][arm][seed] = cell
            print(f"[ba5] probe {arm} {seed}: {cell.get('vs_head')} keys that differ: "
                  f"{sorted(cell.get('keys') or {})}", flush=True)
    B4._write(TOOLS / f"_ba5_probe_{stamp}.json", record)
    return record


# ── the ambient sweep and the AI-France harness ──────────────────────────────

def ambient(arms, stamp: str, turns: int) -> None:
    from tools import _ba4_measure as B4

    for arm in arms:
        label = _label(arm)
        rc = B4._run([TOOLS / "_t3_4_measure.py", "--turns", turns, "--label", label.replace("_", "-"),
                      "--out", TOOLS / f"_dy_signature_{label}_{stamp}.json",
                      "--census", TOOLS / f"_{label}_census_{stamp}.json"],
                     seams=";".join(held(arm)))
        if rc != 0:
            raise SystemExit(f"[ba5] ambient {arm} failed (rc {rc})")


def chain_d(arms, stamp: str, turns: int) -> None:
    from tools import _ba4_measure as B4

    cmd = [TOOLS / "_t3_5_chain_d.py", "--turns", turns, "--arms", ",".join(arms),
           "--out", TOOLS / f"_ba5_chain_d_{stamp}.json",
           "--run-dir", TOOLS / "playtest_runs" / "ba5_chain_d"]
    for arm in arms:
        if held(arm):
            cmd += ["--arm-seams", f"{arm}={';'.join(held(arm))}"]
    rc = B4._run(cmd)
    if rc != 0:
        raise SystemExit(f"[ba5] chain d failed (rc {rc})")


# ── the commanded band and the day's sweep ───────────────────────────────────

def _reserve_of(run: pathlib.Path) -> dict:
    """The run's reserve tally, as the driver kept it (meta.json `rounds`)."""
    try:
        meta = json.loads((run / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict((meta.get("rounds") or {}).get("reserve") or {})


def _driven(tasks, jobs: int, tag: str):
    from tools import _ba4_measure as B4

    out = []
    for group, name, reading in B4._driven(tasks, jobs, tag):
        where = next(t[2] for t in tasks if t[0] == group and t[1] == name)
        reading["reserve"] = _reserve_of(where / name)
        out.append((group, name, reading))
    return out


def band(arms, stamp: str, jobs: int) -> dict:
    from tools import _ba4_measure as B4
    from tools import score_run as SR

    run_dir = TOOLS / "playtest_runs" / "ba5_band"
    record = {"_note": ("Row BA, BA-5 — the France band on the commanded arms (DYNAMISM_SPEC.md §2: "
                        "the deploy gate's difficulty guard, 23–28): score_run's CMD-H / CMD-A / "
                        "CMD-M (forty turns, the mock parser, silent on a day) per arm of the BA-5 "
                        "ladder at the game's own key bar — France's provinces on the last ledger "
                        "row, and each run's reserve tally. Arm 0 (every BA-5 seam down) must read "
                        "28 / 28 / 27, BA-4's shipped reading. Written by tools/_ba5_measure.py "
                        "--surfaces band (a chain run ALONE)."),
              "band": list(BAND), "arms": {}}
    tasks = []
    for arm in arms:
        where = run_dir / arm
        where.mkdir(parents=True, exist_ok=True)
        record["arms"][arm] = {"seams_held": held(arm)}
        for name in BAND_ARMS:
            tasks.append((arm, name, where, list(SR.ARMS[name]["argv"]) + B4._flags(held(arm))))
    for arm, name, reading in _driven(tasks, jobs, "band"):
        record["arms"][arm][name] = reading
    B4._write(TOOLS / f"_ba5_band_{stamp}.json", record)
    for arm in arms:
        print(f"[ba5] band {arm:<8}" + "  ".join(
            f"{n} {record['arms'][arm][n]['provinces']}" for n in BAND_ARMS)
            + "   reserve " + json.dumps({n: record["arms"][arm][n].get("reserve") or {}
                                           for n in BAND_ARMS}), flush=True)
    if "0" in record["arms"]:
        got = {n: record["arms"]["0"][n]["provinces"] for n in BAND_ARMS}
        if got != ARM0_BAND:
            print(f"[ba5] STOP: arm 0 does not reproduce the band {ARM0_BAND}: got {got}.", flush=True)
            raise SystemExit(2)
    return record


def sweep(arm: str, stamp: str, jobs: int, day_arms) -> dict:
    """BA-3's own sweep (its arms, its seeds) with `arm`'s seams held too, at
    the game's own key bar."""
    from tools import _ba3_measure as B3
    from tools import _ba4_measure as B4
    from tools import score_run as SR

    seams_held = held(arm)
    run_dir = TOOLS / "playtest_runs" / f"ba5_sweep_{arm.lower()}"
    seeds = [n for n, _ in B3._seed_runs(SR, SWEEP_SEEDS8)]
    record = {"_note": ("Row BA, BA-5 — BA-3's eight-seed sweep of the day (its arms, its seeds, its "
                        f"reading) at arm {arm} of the BA-5 ladder ({len(seams_held)} seam(s) held), "
                        "the game's own key bar; each run keeps its reserve tally (`reserve`: days "
                        "on which the reserve pursued, the men it took from him and from us, the "
                        "largest single pursuit). Arm 0 must equal the day's sweep on the commit "
                        "before (tools/_ba4_sweep_x14_2026_11_16_k50.json) cell for cell. Written "
                        "by tools/_ba5_measure.py --surfaces sweep (a chain run ALONE)."),
              "band": list(BAND), "seeds": seeds, "ladder_arm": arm, "held": seams_held, "arms": {}}
    tasks = []
    for day_arm in day_arms:
        day_seams, rounds = B3.ARMS[day_arm]
        where = run_dir / day_arm
        where.mkdir(parents=True, exist_ok=True)
        extra = B4._flags(list(day_seams) + seams_held) + (["--rounds", rounds] if rounds else [])
        record["arms"][day_arm] = {"seams": list(day_seams), "rounds": rounds or "(absent)"}
        for name, argv in B3._seed_runs(SR, SWEEP_SEEDS8):
            tasks.append((day_arm, name, where, argv + extra))
    for day_arm, name, reading in _driven(tasks, jobs, f"sweep[{arm}]"):
        record["arms"][day_arm][name] = reading
    if "T" in record["arms"]:
        record["deltas_vs_T"] = B3._deltas(record, "T")
    B4._write(TOOLS / f"_ba5_sweep_{arm.lower()}_{stamp}.json", record)
    print(B3._table(record), flush=True)
    if BA4_SWEEP.exists():
        prior = json.loads(BA4_SWEEP.read_text(encoding="utf-8"))
        moved = [(a, n, prior["arms"][a][n]["provinces"], record["arms"][a][n]["provinces"])
                 for a in record["arms"] if a in prior["arms"] for n in seeds
                 if (prior["arms"][a][n]["provinces"], prior["arms"][a][n]["status"])
                 != (record["arms"][a][n]["provinces"], record["arms"][a][n]["status"])]
        print(f"[ba5] sweep arm {arm} against the day's sweep on the commit before: "
              f"{len(moved)} cell(s) differ {moved[:16]}", flush=True)
        record["cells_moved_vs_commit_before"] = moved
        B4._write(TOOLS / f"_ba5_sweep_{arm.lower()}_{stamp}.json", record)
        if arm == "0" and moved:
            raise SystemExit(2)
    return record


# ── the reserve's rule, read off the records ─────────────────────────────────

def _cells(record: dict, arm: str, seeds) -> dict:
    return {n: record["arms"][arm][n] for n in seeds if n in record["arms"].get(arm, {})}


def _best_counts(record: dict, seeds) -> dict:
    """arm -> [seeds on which it is best or level-best, seeds on which it is
    best alone], over the ways of playing a day."""
    out = {arm: [0, 0] for arm in PLAYED if arm in record["arms"]}
    for seed in seeds:
        got = {arm: record["arms"][arm][seed]["provinces"] for arm in out
               if record["arms"][arm].get(seed, {}).get("ok")}
        if not got:
            continue
        top = max(got.values())
        leaders = [arm for arm, v in got.items() if v == top]
        for arm in leaders:
            out[arm][0] += 1
            if len(leaders) == 1:
                out[arm][1] += 1
    return out


def rule(stamp: str) -> dict:
    """The reserve's rule on each ladder value's sweep and band (the plan's
    words, in the module's docstring). The pick is the lowest that passes."""
    from tools import _ba3_measure as B3

    out = {"_note": ("Row BA, BA-5 — the reserve's rule, written in the plan before the data, read "
                     "off tools/_ba5_sweep_r<n>_<stamp>.json and tools/_ba5_band_<stamp>.json. "
                     "`pick` is the lowest ladder value that passes every clause, or null (the "
                     "rule is then NOT built). Written by tools/_ba5_measure.py --surfaces rule."),
           "ladder": list(RESERVE_LADDER), "values": {}, "pick": None}
    band_file = TOOLS / f"_ba5_band_{stamp}.json"
    bands = json.loads(band_file.read_text(encoding="utf-8")) if band_file.exists() else {"arms": {}}
    # the reserve down, every other rung up — the tree as shipped (arm ALL; the session's review
    # put OWNWAY after ONEDAY, so ONEDAY's sweep no longer is that tree): `0`, `T` and the baseline
    base_file = TOOLS / f"_ba5_sweep_all_{stamp}.json"
    base = json.loads(base_file.read_text(encoding="utf-8")) if base_file.exists() else None
    for value in RESERVE_LADDER:
        arm = f"R{value}"
        file = TOOLS / f"_ba5_sweep_{arm.lower()}_{stamp}.json"
        if not file.exists():
            continue
        record = json.loads(file.read_text(encoding="utf-8"))
        seeds = record["seeds"]
        if base is not None:                 # the day's seam down sees no reserve: read once
            for free in RESERVE_FREE:
                if free not in record["arms"] and free in base["arms"]:
                    record["arms"][free] = base["arms"][free]
        tallies = [(a, n, (record["arms"][a][n].get("reserve") or {}))
                   for a in PLAYED if a in record["arms"] for n in seeds if n in record["arms"][a]]
        days = sum(int(t.get("days", 0)) for _, _, t in tallies)
        from_him = sum(int(t.get("men_from_him", 0)) for _, _, t in tallies)
        from_us = sum(int(t.get("men_from_us", 0)) for _, _, t in tallies)
        largest = max([int(t.get("largest", 0)) for _, _, t in tallies] or [0])
        taken = from_him + from_us
        best = _best_counts(record, seeds)
        deltas = B3._deltas(record, "T") if "T" in record["arms"] else {}
        means = {a: deltas[a]["mean"] for a in PLAYED if a in deltas and deltas[a].get("n")}
        band_cell = bands["arms"].get(arm, {})
        band_read = {n: (band_cell.get(n) or {}).get("provinces") for n in BAND_ARMS}
        base_best = _best_counts(base, seeds) if base is not None else {}
        clauses = {
            "i_felt": days >= 8,
            "ii_no_dominant_way": bool(best) and max(v[0] for v in best.values()) <= 5,
            "ii_press_still_best_somewhere": best.get("P", [0, 0])[0] >= 1
                or (base is not None and base_best.get("P", [0, 0])[0] == 0),
            "ii_guard_still_best_somewhere": best.get("G", [0, 0])[0] >= 1
                or (base is not None and base_best.get("G", [0, 0])[0] == 0),
            "iii_neither_side_takes_three_quarters": taken > 0 and max(from_him, from_us) <= 0.75 * taken,
            "iv_band_in": all(v is not None and BAND[0] <= v <= BAND[1] for v in band_read.values()),
            "v_hand_healthy": bool(means) and all(-3 < m < 3 for m in means.values())
                and max(v[0] for v in best.values()) < 6,
        }
        out["values"][str(value)] = {
            "days_the_reserve_pursued": days, "men_from_him": from_him, "men_from_us": from_us,
            "largest_single_pursuit": largest,
            "share_of_the_larger_side": round(max(from_him, from_us) / taken, 3) if taken else None,
            "best_or_level_best_then_alone": best,
            "best_with_the_reserve_down": base_best,
            "mean_delta_vs_T": means, "band": band_read,
            "per_run": {f"{a}/{n}": t for a, n, t in tallies if t},
            "clauses": clauses, "passes": all(clauses.values()),
        }
        print(f"[ba5] rule {value}: {json.dumps(out['values'][str(value)]['clauses'])} "
              f"days {days} him {from_him} us {from_us} largest {largest} band {band_read}", flush=True)
        if out["pick"] is None and all(clauses.values()):
            out["pick"] = value
    (TOOLS / f"_ba5_reserve_rule_{stamp}.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[ba5] the rule's pick: {out['pick']}", flush=True)
    return out


def gate(arms, stamp: str) -> dict:
    from tools import _ba4_measure as B4

    original = B4._label
    B4._label = _label                      # the same reading, on this session's records
    try:
        return B4.gate(arms, stamp)
    finally:
        B4._label = original


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="0,TELL,ONEDAY,ALL")
    ap.add_argument("--surfaces", default="probe")
    ap.add_argument("--stamp", default=STAMP)
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--probe-base", default="", help="the folder holding probe_head_<seed>.json")
    ap.add_argument("--probe-runs", default=str(TOOLS / "playtest_runs" / "ba5_probe"))
    ap.add_argument("--sweep-arm", default="ALL", help="the ladder arm the day's sweep is taken at")
    ap.add_argument("--day-arms", default="0,T,S,L,P,D,B,G,ALL")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    unknown = [a for a in arms + [args.sweep_arm] if not _known(a)]
    if unknown:
        raise SystemExit(f"[ba5] unknown arm(s) {unknown}; known: HEAD, {ORDER}, ALL, R<n>")
    surfaces = set(args.surfaces.split(","))
    if "probe" in surfaces:
        probe(arms, args.stamp, pathlib.Path(args.probe_base or "."), pathlib.Path(args.probe_runs))
    if "ambient" in surfaces:
        ambient(arms, args.stamp, args.turns)
    if "d" in surfaces:
        chain_d(arms, args.stamp, args.turns)
    if "band" in surfaces:
        band(arms, args.stamp, args.jobs)
    if "sweep" in surfaces:
        sweep(args.sweep_arm, args.stamp, args.jobs, [a for a in args.day_arms.split(",") if a])
    if "rule" in surfaces:
        rule(args.stamp)
    if "gate" in surfaces:
        gate(arms, args.stamp)
    print("[ba5] done", flush=True)


if __name__ == "__main__":
    main()
