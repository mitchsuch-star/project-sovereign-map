"""Row OC — "the rulings built" (November 18, 2026): the session's ONE measure,
with arms, after `tools/_ba6_measure.py` (its idiom, read on this session's
ladder).

THE ARMS — cumulative, each bringing its seams UP over the arm before it
(`tests/_oc_seams.py`, read in its order, never a copy kept here):

    HEAD      no seam passed on an untouched copy of the commit before
              (`git archive 9c5228a5`) — the probe's base rows only
    0         every OC seam DOWN — must reproduce the commit before on every
              surface (OC-4, golden rule 1, carries no seam and stands IN arm 0)
    LETTER    OC-3 BRIT-1: a strangled Britain writes without contact
    ARREARS   OC-2 GRD-20: the mercy's turn pays no arrears down
    RESTLESS  OC-2 GRD-19: the restless interior priced by the province
    CURE      OC-1 GRD-29: a cure is never stranded by an edict
    STAFF     OC-1 GRD-37: the at-war Staff without five turns of upkeep
    SAVE      OC-1 the save's reach: a saving court holds its discretionary gold
    USED      OC-1 GRD-15: a law buys what is used
    ALL       no seam passed: the tree as shipped (the last row, CHEAP, up)

THE SURFACES, each a chain run ALONE (no backend, test or deck edit lands while
it runs — run this tool from a FROZEN COPY of the tree and copy its records
back): probe, band (with the S14j chest re-read), sweep, ambient, d, purse, t8,
sea, promotions (clause 2's twenty further seeds), gate. Arm 0 is compared with BA-6's records of the commit before:
`tools/_ba6_sweep_all_2026_11_17.json`, `tools/_dy_signature_ba6_all_2026_11_17.json`,
`tools/_ba6_all_census_2026_11_17.json`, `tools/_ba6_chain_d_2026_11_17.json` (arm ALL),
and the band reading 28 / 27 / 28.

THE GUARD, written before the data (the plan): every arm's band inside 23–28;
a breach stops the chain at that arm. Fallbacks fixed in advance — RESTLESS:
the cap falls to 150; CHEAP: the urgent recruit of a court at war is exempt
from the keep. A row with no written fallback that breaks the band is reported
with its attribution and put to the user.

    .venv/Scripts/python.exe tools/_oc_measure.py --surfaces probe --probe-base DIR [--arms ...]
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _ladder():
    from tests._oc_seams import OC_SEAMS_BY_ROW
    return {row: [spec.rsplit("=", 1)[0] for spec in specs]
            for row, specs in OC_SEAMS_BY_ROW.items()}


LADDER = _ladder()
ROWS = list(LADDER)
ORDER = ["0"] + ROWS[:-1]          # the last row's arm IS the tree as shipped: ALL
STAMP = "2026_11_18"
BAND = (23, 28)
BAND_ARMS = ("CMD-H", "CMD-A", "CMD-M")
ARM0_BAND = {"CMD-H": 28, "CMD-A": 27, "CMD-M": 28}       # BA-6's final reading (§15.25)
BA6_SWEEP = TOOLS / "_ba6_sweep_all_2026_11_17.json"
BA6_SIGNATURE = TOOLS / "_dy_signature_ba6_all_2026_11_17.json"
BA6_CENSUS = TOOLS / "_ba6_all_census_2026_11_17.json"
BA6_CHAIN_D = TOOLS / "_ba6_chain_d_2026_11_17.json"
SWEEP_SEEDS8 = ("jena", "wagram", "lodi", "eylau", "friedland")
PROBE_SEEDS = ("jena", "marengo")
PROBE_TURNS = 40
SEA_ARMS = ("SHUT-H", "SHUT-A", "SHUT-M", "NAV1-H", "NAV1-A", "NAV1-M")


def held(arm: str) -> list:
    """The seams an arm holds DOWN: every seam of a later row."""
    if arm in ("HEAD", "ALL"):
        return []
    later = ROWS[ROWS.index(arm) + 1:] if arm != "0" else ROWS
    return [f"{spec}=False" for name in later for spec in LADDER[name]]


def _known(arm: str) -> bool:
    """The ladder's arms and ALL. (No HEAD arm: the commit before is the probe's
    `--probe-base` rows, never an arm run on this tree.)"""
    return arm in ORDER or arm == "ALL"


def _label(arm: str) -> str:
    return "oc_" + arm.lower()


def _write(path: pathlib.Path, record: dict) -> None:
    from tools import _ba4_measure as B4
    B4._write(path, record)


# ── the keyed world probe ────────────────────────────────────────────────────

def _all_differences(a_rows: list, b_rows: list) -> dict:
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
    record = {"_note": ("Row OC — the keyed world probe per arm (jena and marengo, "
                        f"{PROBE_TURNS} ambient turns, one hash per top-level key of to_dict a "
                        "turn) against the commit before's own rows (`git archive 9c5228a5`): "
                        "`vs_head` says identical or the first turn that differs, `keys` every key "
                        "that differs on any turn with [first turn, turns]. Written by "
                        "tools/_oc_measure.py."),
              "turns": PROBE_TURNS, "arms": {}}
    for arm in arms:
        record["arms"][arm] = {"seams_held": held(arm)}
        for seed in PROBE_SEEDS:
            out = run_dir / f"probe_{arm}_{seed}.json"
            rc = B4._run([TOOLS / "keyed_world_probe.py", "run", ROOT, seed, PROBE_TURNS, out],
                         seams=";".join(held(arm)), env_extra={"PYTHONHASHSEED": "0"})
            if rc != 0:
                raise SystemExit(f"[oc] probe {arm} {seed} failed (rc {rc})")
            got = json.loads(out.read_text(encoding="utf-8"))
            cell = {"crashes": int(got.get("crashes", 0)), "keys_a_turn": int(got.get("keys", 0))}
            head_file = base_dir / f"probe_head_{seed}.json"
            if head_file.exists():
                head = json.loads(head_file.read_text(encoding="utf-8"))
                found = _all_differences(head["rows"], got["rows"])
                cell["head_crashes"] = int(head.get("crashes", 0))
                cell["vs_head"] = ({"identical": True} if not found else
                                   {"identical": False, "first_turn": min(v[0] for v in found.values())})
                cell["keys"] = found
            record["arms"][arm][seed] = cell
            print(f"[oc] probe {arm} {seed}: {cell.get('vs_head')} keys that differ: "
                  f"{sorted(cell.get('keys') or {})}", flush=True)
            if arm == "0" and cell.get("vs_head", {}).get("identical") is False:
                _write(TOOLS / f"_oc_probe_{stamp}.json", record)
                raise SystemExit(f"[oc] STOP: arm 0 does not reproduce the commit before on {seed}")
    _write(TOOLS / f"_oc_probe_{stamp}.json", record)
    return record


# ── the commanded band, with the S14j chest re-read ──────────────────────────

def _chests(run: pathlib.Path, name: str) -> dict:
    """France's and the courts' chests at the run's last save (S14j's bands)."""
    saves = sorted(run.glob(f"saves/{name}_t*.json"),
                   key=lambda p: int(p.stem.rsplit("_t", 1)[1]))
    if not saves:
        return {}
    data = json.loads(saves[-1].read_text(encoding="utf-8"))
    world = data.get("world_state") or {}
    gold = dict(world.get("nation_gold") or {})
    player = world.get("player_nation") or "France"
    france = int(world.get("gold", gold.get(player, 0)) or 0)
    courts = {n: int(v) for n, v in gold.items() if n != player}
    return {"turn": int(saves[-1].stem.rsplit("_t", 1)[1]), "france": france,
            "courts_total": sum(courts.values()), "court_max": max(courts.values()) if courts else 0,
            "court_max_name": max(courts, key=courts.get) if courts else ""}


def band(arms, stamp: str, jobs: int) -> dict:
    from tools import _ba4_measure as B4
    from tools import score_run as SR

    run_dir = TOOLS / "playtest_runs" / "oc_band"
    record = {"_note": ("Row OC — the France band on the commanded arms (DYNAMISM_SPEC.md §2: the "
                        "deploy gate's difficulty guard, 23–28): score_run's CMD-H / CMD-A / CMD-M "
                        "per arm of the OC ladder, France's provinces on the last ledger row, and "
                        "S14j's chests re-read at the last save (France; the courts' total and the "
                        "largest court). Arm 0 must read 28 / 27 / 28, BA-6's final reading. "
                        "Written by tools/_oc_measure.py --surfaces band (a chain run ALONE)."),
              "band": list(BAND), "s14j_bands": {"france": [16000, 40000], "court_max": 35000,
                                                 "courts_total": 200000}, "arms": {}}
    tasks = []
    for arm in arms:
        where = run_dir / arm
        where.mkdir(parents=True, exist_ok=True)
        record["arms"][arm] = {"seams_held": held(arm)}
        for name in BAND_ARMS:
            tasks.append((arm, name, where, list(SR.ARMS[name]["argv"]) + B4._flags(held(arm))))
    for arm, name, reading in B4._driven(tasks, jobs, "band"):
        reading["chests"] = _chests(run_dir / arm / name, name)
        record["arms"][arm][name] = reading
    _write(TOOLS / f"_oc_band_{stamp}.json", record)
    breach = []
    for arm in arms:
        cells = {n: record["arms"][arm][n]["provinces"] for n in BAND_ARMS}
        chests = {n: record["arms"][arm][n].get("chests", {}).get("france") for n in BAND_ARMS}
        print(f"[oc] band {arm:<9} {cells}  France's chest {chests}", flush=True)
        if any(v is None or not (BAND[0] <= v <= BAND[1]) for v in cells.values()):
            breach.append(arm)
    if "0" in record["arms"]:
        got = {n: record["arms"]["0"][n]["provinces"] for n in BAND_ARMS}
        if got != ARM0_BAND:
            print(f"[oc] STOP: arm 0 does not reproduce the band {ARM0_BAND}: got {got}.", flush=True)
            raise SystemExit(2)
    if breach:
        print(f"[oc] GUARD: the band leaves 23–28 on arm(s) {breach} — bisect, fallback, report.", flush=True)
    return record


# ── the day's sweep ──────────────────────────────────────────────────────────

def sweep(arm: str, stamp: str, jobs: int, day_arms) -> dict:
    from tools import _ba3_measure as B3
    from tools import _ba4_measure as B4
    from tools import score_run as SR

    seams_held = held(arm)
    run_dir = TOOLS / "playtest_runs" / f"oc_sweep_{arm.lower()}"
    seeds = [n for n, _ in B3._seed_runs(SR, SWEEP_SEEDS8)]
    record = {"_note": ("Row OC — BA-3's eight-seed sweep of the day (its arms, its seeds, its "
                        f"reading) at arm {arm} of the OC ladder ({len(seams_held)} seam(s) held), the "
                        "game's own key bar. Arm 0 must equal the day's sweep on the commit before "
                        "(tools/_ba6_sweep_all_2026_11_17.json) cell for cell. Written by "
                        "tools/_oc_measure.py --surfaces sweep (a chain run ALONE)."),
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
    for day_arm, name, reading in B4._driven(tasks, jobs, f"sweep[{arm}]"):
        record["arms"][day_arm][name] = reading
    if "T" in record["arms"]:
        record["deltas_vs_T"] = B3._deltas(record, "T")
    prior = json.loads(BA6_SWEEP.read_text(encoding="utf-8"))
    moved = [(a, n, prior["arms"][a][n]["provinces"], record["arms"][a][n]["provinces"])
             for a in record["arms"] if a in prior["arms"] for n in seeds
             if n in prior["arms"][a] and n in record["arms"][a]
             and (prior["arms"][a][n]["provinces"], prior["arms"][a][n]["status"])
             != (record["arms"][a][n]["provinces"], record["arms"][a][n]["status"])]
    record["cells_moved_vs_commit_before"] = moved
    _write(TOOLS / f"_oc_sweep_{arm.lower()}_{stamp}.json", record)
    print(B3._table(record), flush=True)
    print(f"[oc] sweep arm {arm}: {len(moved)} cell(s) differ from the commit before {moved[:16]}", flush=True)
    if arm == "0" and moved:
        raise SystemExit(2)
    return record


# ── the ambient ten and the AI-France harness ────────────────────────────────

def _strip(d: dict) -> dict:
    return {k: v for k, v in d.items() if not k.startswith("_")}


def ambient(arms, stamp: str, turns: int) -> None:
    from tools import _ba4_measure as B4

    for arm in arms:
        label = _label(arm)
        sig = TOOLS / f"_dy_signature_{label}_{stamp}.json"
        cen = TOOLS / f"_{label}_census_{stamp}.json"
        rc = B4._run([TOOLS / "_t3_4_measure.py", "--turns", turns, "--label", label.replace("_", "-"),
                      "--out", sig, "--census", cen], seams=";".join(held(arm)))
        if rc != 0:
            raise SystemExit(f"[oc] ambient {arm} failed (rc {rc})")
        if arm == "0":
            a_sig = _strip(json.loads(BA6_SIGNATURE.read_text(encoding="utf-8")))
            b_sig = _strip(json.loads(sig.read_text(encoding="utf-8")))
            a_cen = _strip(json.loads(BA6_CENSUS.read_text(encoding="utf-8")))
            b_cen = _strip(json.loads(cen.read_text(encoding="utf-8")))
            same = (a_sig == b_sig, a_cen == b_cen)
            print(f"[oc] ambient arm 0 against BA-6's ALL: signature {'EQUAL' if same[0] else 'DIFFERENT'}, "
                  f"census {'EQUAL' if same[1] else 'DIFFERENT'}", flush=True)
            if not all(same):
                raise SystemExit("[oc] STOP: ambient arm 0 does not reproduce the commit before")


def chain_d(arms, stamp: str, turns: int) -> None:
    from tools import _ba4_measure as B4

    out = TOOLS / f"_oc_chain_d_{stamp}.json"
    cmd = [TOOLS / "_t3_5_chain_d.py", "--turns", turns, "--arms", ",".join(arms),
           "--out", out, "--run-dir", TOOLS / "playtest_runs" / "oc_chain_d"]
    for arm in arms:
        if held(arm):
            cmd += ["--arm-seams", f"{arm}={';'.join(held(arm))}"]
    rc = B4._run(cmd)
    if rc != 0:
        raise SystemExit(f"[oc] chain d failed (rc {rc})")
    if "0" in arms:
        prior = json.loads(BA6_CHAIN_D.read_text(encoding="utf-8"))
        got = json.loads(out.read_text(encoding="utf-8"))
        same = (prior["arms"]["ALL"] == got["arms"]["0"]
                and prior["totals"]["ALL"] == got["totals"]["0"])
        print(f"[oc] chain d arm 0 against BA-6's ALL: {'EQUAL' if same else 'DIFFERENT'}", flush=True)
        if not same:
            raise SystemExit("[oc] STOP: the harness's arm 0 does not reproduce the commit before")


# ── OC-1's purse probe, the T8 re-read, OC-3's sea arms ─────────────────────

def purse(arms, stamp: str, jobs: int) -> None:
    from tools import _ba4_measure as B4

    for arm in arms:
        rc = B4._run([TOOLS / "_oc_purse_probe.py", "--out",
                      TOOLS / f"_oc_purse_{arm.lower()}_{stamp}.json", "--jobs", jobs],
                     seams=";".join(held(arm)))
        if rc != 0:
            raise SystemExit(f"[oc] purse {arm} failed (rc {rc})")


def t8(arms, stamp: str) -> None:
    from tools import _ba4_measure as B4

    for arm in arms:
        rc = B4._run([TOOLS / "_sr7d_t8_probe.py", "--out",
                      TOOLS / f"_oc_t8_{arm.lower()}_{stamp}.json"], seams=";".join(held(arm)))
        if rc != 0:
            raise SystemExit(f"[oc] t8 {arm} failed (rc {rc})")


def _sea_read(run: pathlib.Path, name: str) -> dict:
    """Per turn: the closure against the trade power, her exhaustion, contact
    with France, the stalemate count; and her letters off the digest."""
    import contextlib
    import io
    from backend.game_logic import diplomacy, naval
    from backend.game_logic.ai_diplomacy import break_ranks_lines, stalemate_counter_key
    from tools.sf_nav1_strangulation_probe import _envoys, _load

    rows = []
    for path in sorted(run.glob(f"saves/{name}_t*.json"), key=lambda p: int(p.stem.rsplit("_t", 1)[1])):
        turn = int(path.stem.rsplit("_t", 1)[1])
        with contextlib.redirect_stdout(io.StringIO()):
            world = _load(str(path))
        target = naval.trade_dominance_nation(world)
        if not target:
            continue
        key = world._make_diplo_key(world.player_nation, target)
        at_war = world.get_diplomatic_state(world.player_nation, target) == "WAR"
        rows.append({"turn": turn, "at_war": at_war,
                     "closure": round(float(naval.closure_against(world, target)), 3),
                     "exhaustion": int(world.war_exhaustion.get(target, 0) or 0),
                     "line": int(break_ranks_lines(world, target)["exhaustion"]),
                     "fought": bool(diplomacy.pair_has_fought(world, key)),
                     "stalemate": int((world.ai_stalemate_counters or {}).get(
                         stalemate_counter_key(target, world.player_nation, world), 0))})
    letters = [{"turn": t, "kind": k} for t, k in _envoys(str(run))]
    first_armistice = next((l["turn"] for l in letters if l["kind"] == "armistice"), None)
    contact_by_then = None
    if first_armistice is not None:
        # the digest's "## Turn N" and the save `_tN` both stand at turn N's
        # close; a turn with no trade power to read leaves the answer open
        before = [r for r in rows if r["turn"] <= first_armistice]
        contact_by_then = any(r["fought"] for r in before) if before else None
    strangled = [r["turn"] for r in rows if r["at_war"] and r["closure"] >= 0.40
                 and r["exhaustion"] > r["line"] and not r["fought"]]
    return {"turns": rows, "letters": letters, "first_armistice": first_armistice,
            "contact_by_the_first_armistice": contact_by_then,
            "strangled_without_contact_turns": strangled}


def sea(arms, stamp: str, jobs: int) -> dict:
    from concurrent.futures import ThreadPoolExecutor
    from tools import _ba4_measure as B4
    from tools import score_run as SR

    run_dir = TOOLS / "playtest_runs" / "oc_sea"
    record = {"_note": ("Row OC, OC-3 (BRIT-1) — the benchmark's shut-out arm (SHUT-H/A/M, "
                        "sr5b_shut_out.json, naval C4) and the strangulation arm (NAV1-H/A/M, "
                        "reported) per arm, a save every turn: per turn the closure against the "
                        "trade power, her exhaustion and break-ranks line, contact with France and "
                        "the stalemate count; her letters off the digest; the first armistice and "
                        "whether contact had come by then. Written by tools/_oc_measure.py --surfaces sea."),
              "arms": {}}
    tasks = []
    for arm in arms:
        where = run_dir / arm
        where.mkdir(parents=True, exist_ok=True)
        record["arms"][arm] = {"seams_held": held(arm)}
        for name in SEA_ARMS:
            argv = list(SR.ARMS[name]["argv"])
            turns = int(argv[argv.index("--turns") + 1])
            if "--save-at" not in argv:
                argv += ["--save-at", ",".join(str(t) for t in range(1, turns + 1))]
            tasks.append((arm, name, where, argv + B4._flags(held(arm))))

    def _one(task):
        arm, name, where, argv = task
        result = SR._run_driver(ROOT, where, name, argv)
        return arm, name, result

    with ThreadPoolExecutor(max_workers=max(1, min(jobs, 4))) as pool:
        for arm, name, result in pool.map(_one, tasks):
            cell = _sea_read(run_dir / arm / name, name)
            cell["exit"], cell["status"] = result.get("exit"), result.get("status")
            record["arms"][arm][name] = cell
            print(f"[oc] sea {arm:<7} {name}: first armistice {cell['first_armistice']} "
                  f"(contact by then {cell['contact_by_the_first_armistice']}); strangled w/o "
                  f"contact on {cell['strangled_without_contact_turns'][:6]}", flush=True)
    _write(TOOLS / f"_oc_sea_{stamp}.json", record)
    return record


# Clause 2 of the deploy gate (a minor raised to secondary rank by promotion on
# at least one seed) is read on THIRTY ambient seeds from row OC on — the ten
# the ambient surface plays and these twenty — by the user's ruling of November
# 18, 2026 ("make best decision for gameplay … do research"): on the ten it had
# rested on ONE seed since BA-6 (marengo, Hesse at turn 34), and row OC's
# rulings, as they were meant to, re-time that one story (Britain's cure and
# Staff arrive early and she holds Hanover's Westphalia) while the twenty more
# promote at the same rate with the rules up as down. The other clauses read
# the ten as before.
WIDE_SEEDS = ("aspern", "borodino", "leipzig", "waterloo", "talavera", "salamanca", "vitoria",
              "dresden", "bautzen", "lutzen", "hohenlinden", "trafalgar", "abukir", "arcole",
              "castiglione", "zurich", "valmy", "jemappes", "smolensk", "wavre")


def _wide_promotions(seed: str, seams: str) -> list:
    import subprocess
    from tools import ai_v_sweep as V

    env = V.child_env(seed)
    env.pop("INK_IRON_SEAMS", None)
    if seams:
        env["INK_IRON_SEAMS"] = seams
    env["PYTHONHASHSEED"] = "0"
    proc = subprocess.run([sys.executable, str(TOOLS / "ai_v_sweep.py"), "--run", "--seed", seed,
                           "--ambient-base", "10000", "--turns", "40", "--emit"],
                          env=env, cwd=str(ROOT), capture_output=True, text=True, timeout=1800)
    return list(V.derive_metrics(V.payload_from(proc, seed)).get("rank_promotions") or [])


def promotions(arms, stamp: str, jobs: int) -> dict:
    """Clause 2's twenty further ambient seeds per arm (the ambient surface's own
    runner and reading: `ai_v_sweep --run`, `derive_metrics`'s rank promotions)."""
    from concurrent.futures import ThreadPoolExecutor

    record = {"_note": ("Row OC — the deploy gate's clause 2 on twenty ambient seeds beyond the "
                        "ten (forty turns, the ambient runner, per arm): each seed's rank "
                        "promotions [turn, court]. Read with the ten's record by the gate "
                        "surface. Written by tools/_oc_measure.py --surfaces promotions."),
              "seeds": list(WIDE_SEEDS), "arms": {}}
    for arm in arms:
        seams = ";".join(held(arm))
        with ThreadPoolExecutor(max_workers=max(1, min(jobs, 4))) as pool:
            got = dict(zip(WIDE_SEEDS, pool.map(lambda sd: _wide_promotions(sd, seams), WIDE_SEEDS)))
        record["arms"][arm] = {"seams_held": held(arm), "seeds": got,
                               "seeds_promoting": sorted(sd for sd, v in got.items() if v)}
        print(f"[oc] promotions {arm}: {record['arms'][arm]['seeds_promoting']}", flush=True)
    _write(TOOLS / f"_oc_promotions_wide_{stamp}.json", record)
    return record


def gate(arms, stamp: str) -> dict:
    """The deploy gate per arm (`_ba4_measure.gate`'s reading of the ten), with
    clause 2 read on the thirty seeds (the ten and `WIDE_SEEDS`)."""
    from tools import _ba4_measure as B4

    original = B4._label
    B4._label = _label
    try:
        out = B4.gate(arms, stamp)
    finally:
        B4._label = original
    wide_file = TOOLS / f"_oc_promotions_wide_{stamp}.json"
    wide = json.loads(wide_file.read_text(encoding="utf-8")) if wide_file.exists() else {"arms": {}}
    for arm, cell in out.items():
        extra = wide["arms"].get(arm, {}).get("seeds_promoting")
        cell["promotions_on_the_twenty"] = extra
        ten = bool(cell["promotions"])
        cell["clause_2_on_thirty"] = ten or bool(extra)
        cell["met_on_thirty"] = (cell["story_classes"] >= 6 and cell["clause_2_on_thirty"]
                                 and cell["roster_readings"] >= 2
                                 and cell["annexations_outside_aim"] == 0)
        print(f"[oc] gate {arm}: clause 2 on the ten {ten}, on the twenty {extra} -> "
              f"{'MET' if cell['met_on_thirty'] else 'NOT MET'} on thirty", flush=True)
    _write(TOOLS / f"_oc_gate_{stamp}.json",
           {"_note": ("Row OC — the deploy gate per arm: story classes >= 6, the roster in >= 2 "
                      "readings and no annexation outside aim on the ten ambient seeds; clause 2 "
                      "(a minor promoted on >= 1 seed) on thirty — the ten and the twenty of "
                      "_oc_promotions_wide (the user's ruling of November 18, 2026). `met` is "
                      "the reading on the ten alone, `met_on_thirty` the gate's. Written by "
                      "tools/_oc_measure.py --surfaces gate."),
            "arms": out})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ORDER + ["ALL"]))
    ap.add_argument("--surfaces", default="probe")
    ap.add_argument("--stamp", default=STAMP)
    ap.add_argument("--turns", type=int, default=40)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--probe-base", default="", help="the folder holding probe_head_<seed>.json")
    ap.add_argument("--probe-runs", default=str(TOOLS / "playtest_runs" / "oc_probe"))
    ap.add_argument("--sweep-arm", default="ALL")
    ap.add_argument("--day-arms", default="0,T,S,L,P,D,B,G,ALL")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    unknown = [a for a in arms + [args.sweep_arm] if not _known(a)]
    if unknown:
        raise SystemExit(f"[oc] unknown arm(s) {unknown}; known: {ORDER}, ALL")
    surfaces = set(args.surfaces.split(","))
    if "probe" in surfaces:
        probe(arms, args.stamp, pathlib.Path(args.probe_base or "."), pathlib.Path(args.probe_runs))
    if "band" in surfaces:
        band(arms, args.stamp, args.jobs)
    if "sweep" in surfaces:
        sweep(args.sweep_arm, args.stamp, args.jobs, [a for a in args.day_arms.split(",") if a])
    if "ambient" in surfaces:
        ambient(arms, args.stamp, args.turns)
    if "d" in surfaces:
        chain_d(arms, args.stamp, args.turns)
    if "purse" in surfaces:
        purse(arms, args.stamp, args.jobs)
    if "t8" in surfaces:
        t8(arms, args.stamp)
    if "sea" in surfaces:
        sea(arms, args.stamp, args.jobs)
    if "promotions" in surfaces:
        promotions(arms, args.stamp, args.jobs)
    if "gate" in surfaces:
        gate(arms, args.stamp)
    print("[oc] done", flush=True)


if __name__ == "__main__":
    main()
