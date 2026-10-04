#!/usr/bin/env python
"""THE INSTRUMENT — the Score Finish's fixed benchmark, read twice.

`docs/SCORE_FINISH_SPEC.md` §4 (the method) and §3 Step 0 (SF-M). A pillar
score is no longer one reviewer's impression of one campaign: it is read off a
FIXED set of arms (§4.2), through a checklist of binary items (Appendix A =
`docs/SCORE_CHECKLIST_V1.json`), by a FROZEN rule (§4.4), and adjusted within
±0.25 by a blind panel that never sees the previous number (§4.5).

    .venv/Scripts/python.exe tools/score_run.py run     --out RUN_DIR [--tree PATH] [--jobs 3] [--only ARM ...] [--skip ARM ...]
    .venv/Scripts/python.exe tools/score_run.py check   --run RUN_DIR [--checklist docs/SCORE_CHECKLIST_V1.json] [--eyes EYES.json]
    .venv/Scripts/python.exe tools/score_run.py packet  --run RUN_DIR
    .venv/Scripts/python.exe tools/score_run.py compare --base RUN_A --run RUN_B

`run` drives every arm through `tools/playtest_driver.py` (Mode A, the mock
parser, `PYTHONHASHSEED=0`) on the tree named by `--tree` (default: this
checkout) — a baseline runs on a detached worktree of the pinned commit — and
writes `RUN_DIR/arms/<ARM>/` (the driver's digest.md / digest.jsonl / meta.json
/ saves) plus `RUN_DIR/run.json`. The AI-V sweep, the suite floors and the
parser eval are arms too. The client arm (IQ-10 frames) needs the Godot
binary: without `--godot` it is recorded SKIPPED and UI/UX reads NOT EXERCISED.

`check` reads the arms: every AUTO item off the digests, every PROBE item
through `tools/_score_probes.py` (read-only, in-process against this tree's
backend, on the run's own saves), every EYES item from `--eyes` (the user's
marks; the panel's marks otherwise; absent = unmeasured). It writes
`checklist.json`, `scores.json`, `census_by_pillar.json`, `findings_rate.json`.

The rule (§4.4, frozen): both floors green and no verified open P1 in the
pillar -> 5.5 + 0.5 per ceiling passed; otherwise 5.0 + 0.25 per ceiling, at
most 6.0. A pillar is EXERCISED at >= 6 of 8 items measured; with 6–7 measured
its score is a RANGE (unmeasured read as failed, then as passed) and the
directional takes the low end; under 6 it is NOT EXERCISED and never averaged.
The directional is reported "x.xx over n/14".

Honesty rules this file keeps:
  * nothing here changes a game state — the arms are the driver's, the probes
    load saves read-only, the rule is arithmetic over the items;
  * an item that could not be measured says WHY (`measured: false, reason`),
    and is never counted as a pass or a fail;
  * every item carries its evidence line, so a reader can check the mark
    against the digest without trusting the reader function.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as _dt
import json
import os
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CHECKLIST_DEFAULT = ROOT / "docs" / "SCORE_CHECKLIST_V1.json"
SCRIPTS = "tools/playtest_scripts"
T24_SAVE = "docs/audits/playtest_digests/rs0928-hand-played/retest_t24_summonable.json"
# SF-AGD-1 (Step 5, October 3, 2026): the TILSIT board with Posen still
# Prussian — `tools/gen_agd_fixture.py` regenerates it.
AGD_FIXTURE = "tests/fixtures/playtest_saves/fixture_agd_tilsit.json"
GE3_FIXTURE = "tests/fixtures/playtest_saves/fixture_ge3_pressburg.json"
HOLD_SCRIPT = "score_hold_2026_09_29.json"  # re-written fresh each run (§4.2)


# ── §4.2 the fixed benchmark ────────────────────────────────────────────────
# One row per arm: the driver's argv (the driver adds --name/--fresh/--out).
# `feeds` names the pillars the arm is read for (documentation; the checklist
# items name their own arms).
def _cmd(seed, extra):
    return [
        "--script",
        f"{SCRIPTS}/commanded_full40.json",
        "--turns",
        "40",
        "--diplomacy",
        "accept",
        "--save-at",
        "10,20,30,40",
        "--seed",
        seed,
    ] + extra


ARMS: dict[str, dict] = {
    "FC": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr_exit_first_contact.json",
            "--turns",
            "2",
            "--diplomacy",
            "decline",
        ],
        "feeds": ["first_contact"],
    },
    "OP": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr_exit_aar_typed.json",
            "--turns",
            "18",
            "--objection",
            "insist",
            "--diplomacy",
            "accept",
        ],
        "feeds": ["command", "first_contact", "marshal_drama", "ui_ux"],
    },
    "DL": {
        "argv": ["--script", f"{SCRIPTS}/score_docked_lines.json", "--turns", "3"],
        "feeds": [
            "command",
            "first_contact",
            "diplomacy",
            "economy",
            "combat_legibility",
        ],
    },
    "HOLD": {
        "argv": ["--script", f"{SCRIPTS}/{HOLD_SCRIPT}", "--turns", "2"],
        "feeds": ["command", "first_contact"],
        "optional": True,
    },
    "CMD-H": {
        "argv": _cmd("historical", []),
        "feeds": [
            "ending",
            "living_balance",
            "vassals",
            "economy",
            "agendas",
            "narration",
            "ai_aliveness",
        ],
        "long": True,
    },
    "CMD-A": {
        "argv": _cmd("austerlitz", []),
        "feeds": ["ending", "living_balance", "vassals"],
        "long": True,
    },
    "CMD-M": {
        "argv": _cmd("marengo", []),
        "feeds": ["ending", "living_balance", "vassals"],
        "long": True,
    },
    "CMD-ULM": {"argv": _cmd("ulm", []), "feeds": ["agendas"], "long": True},
    "CMDR-H": {
        "argv": [
            "--script",
            f"{SCRIPTS}/commanded_full40.json",
            "--turns",
            "30",
            "--diplomacy",
            "accept",
            "--client-petition",
            "refuse",
            "--seed",
            "historical",
        ],
        "feeds": ["vassals"],
        "long": True,
    },
    "FLD": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr_exit_chunk4_field.json",
            "--turns",
            "10",
            "--objection",
            "insist",
            "--diplomacy",
            "decline",
        ],
        "feeds": ["combat_legibility", "marshal_drama"],
    },
    "LAW": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr_exit_chunk5_laws.json",
            "--turns",
            "10",
            "--diplomacy",
            "accept",
        ],
        "feeds": ["economy"],
    },
    "SEA": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr_exit_chunk5_sea.json",
            "--turns",
            "12",
            "--diplomacy",
            "decline",
        ],
        "feeds": ["naval"],
    },
    "SHUT-H": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr5b_shut_out.json",
            "--turns",
            "12",
            "--diplomacy",
            "accept",
            "--seed",
            "historical",
        ],
        "feeds": ["naval"],
    },
    "SHUT-A": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr5b_shut_out.json",
            "--turns",
            "12",
            "--diplomacy",
            "accept",
            "--seed",
            "austerlitz",
        ],
        "feeds": ["naval"],
    },
    "SHUT-M": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr5b_shut_out.json",
            "--turns",
            "12",
            "--diplomacy",
            "accept",
            "--seed",
            "marengo",
        ],
        "feeds": ["naval"],
    },
    "DESC": {
        "argv": ["--script", f"{SCRIPTS}/naval_descent.json", "--turns", "14"],
        "feeds": ["naval"],
    },
    "PROP-H": {
        "argv": ["--turns", "20", "--diplomacy", "propose", "--seed", "historical"],
        "feeds": ["diplomacy"],
    },
    "PROP-A": {
        "argv": ["--turns", "20", "--diplomacy", "propose", "--seed", "austerlitz"],
        "feeds": ["diplomacy"],
    },
    "PROP-M": {
        "argv": ["--turns", "20", "--diplomacy", "propose", "--seed", "marengo"],
        "feeds": ["diplomacy"],
    },
    "ADV": {
        "argv": ["--missions", "advisor", "--diplomacy", "accept", "--turns", "20"],
        "feeds": ["diplomacy"],
    },
    "VOLTE": {
        "argv": [
            "--script",
            f"{SCRIPTS}/volte_court_austria.json",
            "--turns",
            "40",
            "--diplomacy",
            "accept",
        ],
        "feeds": ["diplomacy", "living_balance"],
        "long": True,
    },
    "PRESS": {
        "argv": [
            "--script",
            f"{SCRIPTS}/ge3_pressburg.json",
            "--from-save",
            GE3_FIXTURE,
            "--diplomacy",
            "accept",
            "--stop-on-ending",
            "--turns",
            "12",
        ],
        "feeds": ["ending"],
    },
    "VERDICT": {
        "argv": ["--seed", "austerlitz", "--turns", "46", "--stop-on-ending"],
        "feeds": ["ending"],
        "long": True,
    },
    "CONG": {
        "argv": [
            "--script",
            f"{SCRIPTS}/score_congress_sitting.json",
            "--from-save",
            T24_SAVE,
            "--diplomacy",
            "accept",
            "--turns",
            "9",
        ],
        "feeds": ["ending"],
    },
    "REACH-AAR": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr1e_aar_road.json",
            "--turns",
            "40",
            "--objection",
            "insist",
            "--diplomacy",
            "accept",
            "--client-petition",
            "grant",
        ],
        "feeds": ["ending"],
        "long": True,
    },
    "REACH-GEVB": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sr1e_gev_b.json",
            "--turns",
            "40",
            "--objection",
            "insist",
            "--diplomacy",
            "accept",
            "--declare-war",
            "proceed",
            "--client-petition",
            "grant",
        ],
        "feeds": ["ending"],
        "long": True,
    },
    "SCH": {
        "argv": [
            "--script",
            f"{SCRIPTS}/tutorial_lesson.json",
            "--turns",
            "12",
            "--scenario",
            "tutorial",
            "--objection",
            "insist",
            "--diplomacy",
            "decline",
        ],
        "feeds": ["first_contact"],
    },
    "TYPED": {
        "argv": ["--script", f"{SCRIPTS}/typed_road.json", "--turns", "12"],
        "feeds": ["command"],
    },
    # SF-AGD-1 "The agendas arm" (Step 5 SR-8b): a PLAYED road from the TILSIT
    # board — Posen taken in play (the Duchy's gate flips), the Duchy carved
    # through the settlement table's own clicks and the separate peace, the
    # Proclamation on ratification. SF-M's TILSIT probe is its instrument.
    "AGD": {
        "argv": [
            "--script",
            f"{SCRIPTS}/sf_agd1_tilsit_road.json",
            "--from-save",
            AGD_FIXTURE,
            "--turns",
            "3",
            "--diplomacy",
            "accept",
            "--save-at",
            "1,2,3",
        ],
        "feeds": ["agendas"],
    },
}
# The petition acceptance probe (drama F1) wraps the flagship arm in-process.
FLAG_ARGV = [
    "--name",
    "FLAG",
    "--seed",
    "historical",
    "--llm",
    "mock",
    "--script",
    f"{SCRIPTS}/flagship_1805.json",
    "--turns",
    "24",
    "--objection",
    "insist",
    "--diplomacy",
    "decline",
    "--redemption",
    "dismiss",
    "--petition",
    "first_enabled",
    "--audience",
    "open",
    "--declare-war",
    "proceed",
    "--fresh",
]
# The suite floors (living balance F2, AI aliveness F1, naval F1, agendas F1).
SUITE_FILES = [
    "tests/test_combat_sweep_metrics.py",
    "tests/test_ai_intent_threat_migration.py",
    "tests/test_ai_intent_assurance.py",
    "tests/test_naval_channel_gate.py",
    "tests/test_naval_substrate.py",
    "tests/test_nation_agendas.py",
    "tests/test_nation_agendas_formables.py",
]
CMD_ARMS = ("CMD-H", "CMD-A", "CMD-M")
SAVE_ARMS = (
    "CMD-H",
    "CMD-A",
    "CMD-M",
    "CMD-ULM",
    "REACH-AAR",
    "REACH-GEVB",
    "CMDR-H",
    "VOLTE",
)


def _python() -> str:
    for rel in (("Scripts", "python.exe"), ("bin", "python")):
        cand = ROOT.joinpath(".venv", *rel)
        if cand.exists():
            return str(cand)
    return sys.executable


def _tree_sha(tree: pathlib.Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(tree),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return ""


def _env(run_dir: pathlib.Path) -> dict:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["LLM_MODE"] = "mock"
    env["INK_IRON_SAVE_DIR"] = str(run_dir / "_saves")
    for key in (
        "SOVEREIGN_SCENARIO",
        "SOVEREIGN_MAP",
        "SOVEREIGN_SMOKE_START",
        "SOVEREIGN_SEED",
    ):
        env.pop(key, None)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _run_driver(
    tree: pathlib.Path, arms_dir: pathlib.Path, name: str, argv: list[str]
) -> dict:
    py = _python()
    log = arms_dir / f"{name}.log"
    cmd = [
        py,
        str(tree / "tools" / "playtest_driver.py"),
        "--name",
        name,
        "--fresh",
        "--out",
        str(arms_dir),
        "--llm",
        "mock",
    ] + argv
    t0 = time.time()
    with log.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(
            cmd,
            cwd=str(tree),
            env=_env(arms_dir),
            stdout=fh,
            stderr=subprocess.STDOUT,
            text=True,
        )
    meta = arms_dir / name / "meta.json"
    status = ""
    if meta.exists():
        try:
            status = json.loads(meta.read_text(encoding="utf-8")).get("status", "")
        except Exception:
            status = "unreadable-meta"
    return {
        "arm": name,
        "exit": proc.returncode,
        "status": status,
        "seconds": round(time.time() - t0, 1),
        "cmd": cmd[2:],
    }


def _run_flag(tree: pathlib.Path, arms_dir: pathlib.Path) -> dict:
    py = _python()
    t0 = time.time()
    out = arms_dir / "FLAG_probe.json"
    cmd = (
        [py, str(tree / "tools" / "_pc15_10_acceptance_probe.py"), str(out), "--"]
        + FLAG_ARGV
        + ["--out", str(arms_dir)]
    )
    with (arms_dir / "FLAG.log").open("w", encoding="utf-8") as fh:
        proc = subprocess.run(
            cmd,
            cwd=str(tree),
            env=_env(arms_dir),
            stdout=fh,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return {
        "arm": "FLAG",
        "exit": proc.returncode,
        "status": "completed" if out.exists() else "no-output",
        "seconds": round(time.time() - t0, 1),
        "cmd": cmd[2:],
    }


def _run_titled(tree: pathlib.Path, arms_dir: pathlib.Path, name: str) -> dict:
    """The titled count off every save the arm left (SR-1e's probe, in-process
    on the TREE's backend so a baseline reads its own code)."""
    py = _python()
    saves = (
        sorted((arms_dir / name / "saves").glob("*.json"))
        if (arms_dir / name / "saves").exists()
        else []
    )
    if not saves:
        return {"arm": name, "titled": "no saves"}
    code = (
        "import json,sys,os,io,contextlib,pathlib\n"
        "sys.path.insert(0, os.getcwd())\n"
        "for k in ('SOVEREIGN_SCENARIO','SOVEREIGN_MAP','SOVEREIGN_SMOKE_START'): os.environ.pop(k, None)\n"
        "os.environ.setdefault('LLM_MODE','mock')\n"
        "out=[]\n"
        "with contextlib.redirect_stdout(io.StringIO()):\n"
        "    from backend.game_logic import congress\n"
        "    from backend.save_manager import load_game\n"
        "    for p in sys.argv[1:]:\n"
        "        r = load_game(pathlib.Path(p))\n"
        "        w = r.get('world')\n"
        "        if w is None: out.append({'save': p, 'error': r.get('message')}); continue\n"
        "        v = congress.titled(w)\n"
        "        out.append({'save': os.path.basename(p), 'turn': int(w.current_turn), 'titled': int(v['count']),\n"
        "                    'hold_titled': int(v['needed']), 'provinces': len(w.get_nation_regions(w.player_nation))})\n"
        "print(json.dumps(out))\n"
    )
    proc = subprocess.run(
        [py, "-c", code] + [str(s) for s in saves],
        cwd=str(tree),
        env=_env(arms_dir),
        capture_output=True,
        text=True,
    )
    try:
        rows = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        rows = [{"error": proc.stdout[-500:] + proc.stderr[-500:]}]
    (arms_dir / name / "titled.json").write_text(
        json.dumps({"rows": rows}, indent=1), encoding="utf-8"
    )
    return {"arm": name, "titled": rows}


def _run_suite(tree: pathlib.Path, arms_dir: pathlib.Path) -> dict:
    py = _python()
    t0 = time.time()
    out_dir = arms_dir / "SUITE"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for f in SUITE_FILES:
        if not (tree / f).exists():
            results[f] = {"missing": True}
            continue
        proc = subprocess.run(
            [py, "-m", "pytest", f, "-q", "-p", "no:cacheprovider", "--tb=line"],
            cwd=str(tree),
            env=_env(arms_dir),
            capture_output=True,
            text=True,
        )
        tail = (
            proc.stdout.strip().splitlines()[-1]
            if proc.stdout.strip()
            else proc.stderr[-300:]
        )
        results[f] = {"exit": proc.returncode, "summary": tail}
        (out_dir / (pathlib.Path(f).stem + ".log")).write_text(
            proc.stdout + proc.stderr, encoding="utf-8"
        )
    (out_dir / "result.json").write_text(
        json.dumps(results, indent=1), encoding="utf-8"
    )
    return {
        "arm": "SUITE",
        "exit": max(r.get("exit", 0) for r in results.values()),
        "status": "completed",
        "seconds": round(time.time() - t0, 1),
    }


def _run_parser_eval(tree: pathlib.Path, arms_dir: pathlib.Path) -> dict:
    py = _python()
    t0 = time.time()
    out_dir = arms_dir / "PEVAL"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for label, extra in (("corpus", []), ("replay", ["--replay"])):
        proc = subprocess.run(
            [py, "-m", "backend.ai.parser_eval"] + extra,
            cwd=str(tree),
            env=_env(arms_dir),
            capture_output=True,
            text=True,
        )
        text = proc.stdout + proc.stderr
        (out_dir / f"{label}.log").write_text(text, encoding="utf-8")
        m = None
        for line in reversed(text.strip().splitlines()):
            m = re.search(
                r"(\d+)\s*/\s*(\d+)\s*(?:passed|entries|correct|ok)|(\d+) passed[, ]+(\d+) failed|passed[: ]+(\d+)\s*/\s*(\d+)",
                line,
                re.I,
            )
            if m:
                break
        passed = total = None
        if m:
            nums = [int(x) for x in m.groups() if x is not None]
            if "failed" in m.group(0).lower() and len(nums) == 2:
                passed, total = nums[0], nums[0] + nums[1]
            elif len(nums) >= 2:
                passed, total = nums[0], nums[1]
        results[label] = {
            "exit": proc.returncode,
            "tail": (
                m.group(0)
                if m
                else (text.strip().splitlines()[-1][:300] if text.strip() else "")
            ),
            "passed": passed,
            "total": total,
        }
    (out_dir / "result.json").write_text(
        json.dumps(results, indent=1), encoding="utf-8"
    )
    return {
        "arm": "PEVAL",
        "exit": max(r["exit"] for r in results.values()),
        "status": "completed",
        "seconds": round(time.time() - t0, 1),
    }


def cmd_run(args) -> int:
    tree = pathlib.Path(args.tree).resolve() if args.tree else ROOT
    run_dir = pathlib.Path(args.out).resolve()
    arms_dir = run_dir / "arms"
    arms_dir.mkdir(parents=True, exist_ok=True)
    only = set(args.only or [])
    skip = set(args.skip or [])
    selected = [a for a in ARMS if (not only or a in only) and a not in skip]
    if "HOLD" in selected and not (tree / SCRIPTS / HOLD_SCRIPT).exists():
        print(
            f"HOLD: {SCRIPTS}/{HOLD_SCRIPT} is not on the tree — skipped (write it blind first, §4.2)"
        )
        selected.remove("HOLD")
    # the long arms first, so the pool's tail is short
    selected.sort(key=lambda a: (not ARMS[a].get("long"), a))
    record = {
        "tree": str(tree),
        "sha": _tree_sha(tree),
        "started": _dt.datetime.now().isoformat(timespec="minutes"),
        "jobs": args.jobs,
        "arms": {},
        "skipped": {},
    }
    if not only or "FLAG" in only:
        if "FLAG" not in skip:
            selected.append("FLAG")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {}
        for name in selected:
            if name == "FLAG":
                futures[pool.submit(_run_flag, tree, arms_dir)] = name
            else:
                futures[
                    pool.submit(_run_driver, tree, arms_dir, name, ARMS[name]["argv"])
                ] = name
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            record["arms"][res["arm"]] = res
            print(
                f"  {res['arm']:<10} exit {res['exit']} status {res.get('status', '')!s:<16} {res['seconds']}s"
            )
            (run_dir / "run.json").write_text(
                json.dumps(record, indent=1), encoding="utf-8"
            )
    for name in SAVE_ARMS:
        if name in record["arms"]:
            record["arms"][name]["titled"] = _run_titled(tree, arms_dir, name).get(
                "titled"
            )
    if (not only or "SUITE" in only) and "SUITE" not in skip:
        record["arms"]["SUITE"] = _run_suite(tree, arms_dir)
        print("  SUITE done")
    if (not only or "PEVAL" in only) and "PEVAL" not in skip:
        record["arms"]["PEVAL"] = _run_parser_eval(tree, arms_dir)
        print("  PEVAL done")
    if args.aiv_dir:
        record["arms"]["AIV"] = {
            "arm": "AIV",
            "dir": str(pathlib.Path(args.aiv_dir).resolve()),
            "status": "linked",
        }
    elif (not only or "AIV" in only) and "AIV" not in skip:
        py = _python()
        t0 = time.time()
        out = arms_dir / "AIV"
        out.mkdir(exist_ok=True)
        with (arms_dir / "AIV.log").open("w", encoding="utf-8") as fh:
            proc = subprocess.run(
                [
                    py,
                    str(tree / "tools" / "ai_v_sweep.py"),
                    "--all",
                    "--out",
                    str(out),
                    "--turns",
                    "40",
                    "--acceptance-n",
                    str(args.acceptance_n),
                ],
                cwd=str(tree),
                env=_env(arms_dir),
                stdout=fh,
                stderr=subprocess.STDOUT,
                text=True,
            )
        record["arms"]["AIV"] = {
            "arm": "AIV",
            "exit": proc.returncode,
            "dir": str(out),
            "status": "completed" if proc.returncode == 0 else "failed",
            "seconds": round(time.time() - t0, 1),
        }
    if args.godot:
        record["skipped"]["CLI"] = (
            "the client arm is run by tools/iq10_run_captures.py with --godot; not wired here yet"
        )
    else:
        record["skipped"]["CLI"] = (
            "no Godot binary given (--godot): UI/UX reads NOT EXERCISED (§4.6)"
        )
    record["finished"] = _dt.datetime.now().isoformat(timespec="minutes")
    (run_dir / "run.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(f"run recorded at {run_dir / 'run.json'}")
    return 0


# ── the arm reader ──────────────────────────────────────────────────────────
class Arm:
    """One arm's archive: meta.json, digest.jsonl (records), digest.md (turn blocks)."""

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.ok = (path / "meta.json").exists()
        self.meta = (
            json.loads((path / "meta.json").read_text(encoding="utf-8"))
            if self.ok
            else {}
        )
        self.records: list[dict] = []
        if (path / "digest.jsonl").exists():
            for line in (
                (path / "digest.jsonl").read_text(encoding="utf-8").splitlines()
            ):
                if line.strip():
                    try:
                        self.records.append(json.loads(line))
                    except Exception:
                        pass
        self.md = (
            (path / "digest.md").read_text(encoding="utf-8")
            if (path / "digest.md").exists()
            else ""
        )
        self.titled = (
            json.loads((path / "titled.json").read_text(encoding="utf-8"))
            if (path / "titled.json").exists()
            else {}
        )

    def kind(self, k: str) -> list[dict]:
        return [r for r in self.records if r.get("kind") == k]

    def blocks(self) -> list[tuple[int, str]]:
        """[(turn, text)] — the digest's turn blocks."""
        out = []
        for m in re.finditer(
            r"\n## Turn (\d+)[^\n]*\n(.*?)(?=\n## Turn \d+|\Z)", self.md, re.S
        ):
            out.append((int(m.group(1)), m.group(2)))
        return out

    def by_turn(self) -> list[list[dict]]:
        """The jsonl records grouped by the `turn` record that opens each block."""
        groups: list[list[dict]] = []
        for r in self.records:
            if r.get("kind") == "turn":
                groups.append([r])
            elif groups:
                groups[-1].append(r)
        return groups

    @property
    def status(self) -> str:
        return str(self.meta.get("status", ""))

    @property
    def blockers(self) -> list:
        return list(self.meta.get("unknown_blockers") or [])


def load_arms(run_dir: pathlib.Path) -> dict[str, Arm]:
    arms = {}
    arms_dir = run_dir / "arms"
    if arms_dir.exists():
        for p in sorted(arms_dir.iterdir()):
            if p.is_dir() and (p / "meta.json").exists():
                arms[p.name] = Arm(p)
    return arms


# ── the rule (§4.4, frozen) ────────────────────────────────────────────────
def score_from_items(
    floors_pass: bool, no_open_p1: bool, ceilings_passed: int
) -> float:
    if floors_pass and no_open_p1:
        return round(5.5 + 0.5 * ceilings_passed, 2)
    return round(min(6.0, 5.0 + 0.25 * ceilings_passed), 2)


def pillar_score(items: list[dict], open_p1: list[str]) -> dict:
    """items: the pillar's eight, each {id, kind, measured, pass}. Returns the
    reading: score / range / NOT EXERCISED, with the counts."""
    measured = [i for i in items if i.get("measured")]
    floors = [i for i in items if i["id"].startswith("F")]
    ceils = [i for i in items if i["id"].startswith("C")]
    n_meas = len(measured)
    out = {
        "measured": n_meas,
        "of": len(items),
        "open_p1": open_p1,
        "ceilings_passed": sum(1 for c in ceils if c.get("measured") and c.get("pass")),
        "ceilings_failed": sum(
            1 for c in ceils if c.get("measured") and not c.get("pass")
        ),
        "floors_passed": sum(1 for f in floors if f.get("measured") and f.get("pass")),
        "floors_failed": sum(
            1 for f in floors if f.get("measured") and not f.get("pass")
        ),
    }
    if n_meas < 6:
        out.update(
            {
                "exercised": False,
                "score": None,
                "low": None,
                "high": None,
                "reading": "NOT EXERCISED",
            }
        )
        return out

    # low: unmeasured read as failed; high: unmeasured read as passed
    def _score(assume_pass: bool) -> float:
        fl = all((f.get("pass") if f.get("measured") else assume_pass) for f in floors)
        ce = sum(
            1 for c in ceils if (c.get("pass") if c.get("measured") else assume_pass)
        )
        return score_from_items(fl, not open_p1, ce)

    low, high = _score(False), _score(True)
    out.update(
        {
            "exercised": True,
            "low": low,
            "high": high,
            "score": low if low == high else None,
            "reading": f"{low:.2f}" if low == high else f"{low:.2f}–{high:.2f}",
        }
    )
    return out


def directional(scores: dict) -> dict:
    lows = [v["low"] for v in scores.values() if v.get("exercised")]
    return {
        "value": round(sum(lows) / len(lows), 2) if lows else None,
        "over": f"{len(lows)}/{len(scores)}",
        "note": "the mean of each exercised pillar's LOW end (§4.4); NOT EXERCISED pillars are never averaged",
    }


# ── the readers: one per AUTO item, keyed "pillar.ID" ──────────────────────
# Each returns {"measured": bool, "pass": bool|None, "evidence": str} and
# never raises: an exception is a measurement failure with the traceback's
# last line as the reason, so one bad digest cannot hide the other items.
SHRUG_RX = re.compile(
    r"cannot answer that from the dispatches|cannot determine the order|"
    r"instruction is unclear|cannot parse this order|order eludes me|"
    r"cannot make sense of this|I did not understand|Unclear instruction",
    re.I,
)
READING_REFUSAL_RX = re.compile(
    r"Cannot find marshal '|Cannot find '[^']+' to \w+|"
    r"Region '[^']+' not found\. Did you mean",
    re.I,
)
RAW_KEY_RX = re.compile(
    r"\b(ArchdukeCharles|ArchdukeJohn|PapalStates|KingdomOfItaly|"
    r"[A-Z][a-z]+(?:[A-Z][a-z]+)+)\b"
)
RAW_KEY_ALLOW = {
    "McDonald",
    "MacDonald",
    "LeMarois",
    "DeRoy",
    "DuPont",
    "LaSalle",
    "McMahon",
}
BLOCKING_POPUPS = {
    "diplomatic_dialogue",
    "marshal_petition",
    "objection",
    "strategic_interrupt",
    "capture_choice[capture]",
    "settlement_confirm",
    "settlement_review",
    "last_stand",
    "clarification",
    "ultimatum",
    "war_purpose",
    "glorious_charge",
    "vassal_rebellion",
    "envoy_digest",
    "incoming_settlement_offer",
    "sabotage",
    "redemption",
    "paradox",
}
NON_BLOCKING_POPUPS = {"battle_diorama", "proposal_result", "marshal_audience"}
COURTS_TYPES = {"intent_hardens", "intent_eases"}
GREAT_CAPITALS = {
    "Vienna",
    "Berlin",
    "London",
    "St Petersburg",
    "Moscow",
    "Madrid",
    "Paris",
    "Constantinople",
    "Stockholm",
    "Copenhagen",
    "Lisbon",
    "Naples",
    "Rome",
    "Munich",
    "Dresden",
    "Amsterdam",
    "Milan",
    "Bern",
    "Kassel",
    "Hanover",
}


def _res(measured, ok=None, evidence=""):
    return {
        "measured": bool(measured),
        "pass": (bool(ok) if measured else None),
        "evidence": str(evidence)[:600],
    }


def _unmeasured(reason):
    return _res(False, None, reason)


def _need(arms: dict, *names) -> list:
    missing = [n for n in names if n not in arms]
    return missing


def _cmd_records(arm: Arm) -> list[dict]:
    return arm.kind("command")


def _find_cmd(arm: Arm, text: str) -> dict | None:
    for r in _cmd_records(arm):
        if str(r.get("text", "")).strip().lower() == text.strip().lower():
            return r
    return None


def _last_ledger(arm: Arm) -> dict:
    led = arm.kind("ledger")
    return led[-1] if led else {}


def _titled_rows(arm: Arm) -> list[dict]:
    return [
        r
        for r in (arm.titled.get("rows") or [])
        if isinstance(r, dict) and "titled" in r
    ]


def _titled_at(arm: Arm, turn_max: int = 41) -> int | None:
    rows = [r for r in _titled_rows(arm) if int(r.get("turn", 0)) <= turn_max]
    if not rows:
        return None
    return int(max(rows, key=lambda r: int(r.get("turn", 0)))["titled"])


def _dispatch_rows(arm: Arm) -> list[dict]:
    return arm.kind("dispatch_row")


def _count_dtype(arm: Arm, dtype: str) -> int:
    n = sum(1 for r in _dispatch_rows(arm) if str(r.get("dtype")) == dtype)
    n += sum(1 for r in arm.kind("rail") if str(r.get("dtype")) == dtype)
    # the DIPLO tally lines carry the MEDIUM/LOW rows the rail did not print
    for m in re.finditer(r"- DIPLO \+\d+ medium/low \((.*?)\)\n", arm.md):
        for part in m.group(1).split(", "):
            mm = re.match(r"(\S+)(?: ×(\d+))?$", part.strip())
            if mm and mm.group(1) == dtype:
                pass  # already counted through dispatch_row (every row is recorded)
    return n


def _blocks_with(arm: Arm, needle: str) -> list[tuple[int, str]]:
    out = []
    for turn, text in arm.blocks():
        for line in text.split("\n"):
            if needle.lower() in line.lower():
                out.append((turn, line.strip()))
    return out


def _aiv(run_dir: pathlib.Path) -> tuple[dict, dict]:
    """(summary.json, {seed_key: per-run json}) from the AIV arm, or ({}, {})."""
    cands = [run_dir / "arms" / "AIV", run_dir / "AIV"]
    rec = {}
    if (run_dir / "run.json").exists():
        rec = (
            json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            .get("arms", {})
            .get("AIV", {})
        )
        if rec.get("dir"):
            cands.insert(0, pathlib.Path(rec["dir"]))
    for c in cands:
        if (c / "summary.json").exists():
            summary = json.loads((c / "summary.json").read_text(encoding="utf-8"))
            runs = {}
            for p in sorted(c.glob("arm*_*.json")):
                try:
                    runs[p.stem] = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    pass
            return summary, runs
    return {}, {}


def _suite(run_dir: pathlib.Path) -> dict:
    p = run_dir / "arms" / "SUITE" / "result.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _peval(run_dir: pathlib.Path) -> dict:
    p = run_dir / "arms" / "PEVAL" / "result.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _suite_green(run_dir, files, label):
    res = _suite(run_dir)
    if not res:
        return _unmeasured("the SUITE arm did not run")
    rows = {f: res.get(f) for f in files}
    missing = [f for f, r in rows.items() if r is None]
    if missing:
        return _unmeasured(f"SUITE has no result for {missing}")
    ok = all(int(r.get("exit", 1)) == 0 for r in rows.values())
    return _res(
        True,
        ok,
        f"{label}: "
        + "; ".join(
            f"{pathlib.Path(f).name} → {r.get('summary', '')[:80]}"
            for f, r in rows.items()
        ),
    )


def _cmd_blocks(arm: Arm) -> list[dict]:
    """The digest's CMD lines with the sub-lines that follow each, per turn."""
    out = []
    for turn, text in arm.blocks():
        cur = None
        for line in text.split("\n"):
            m = re.match(r"^- CMD `(.*)` → ([✓✗])(.*)$", line)
            if m:
                cur = {
                    "turn": turn,
                    "text": m.group(1),
                    "ok": m.group(2) == "✓",
                    "head": m.group(3).strip(),
                    "sub": [],
                }
                out.append(cur)
            elif cur is not None and line.startswith("  "):
                cur["sub"].append(line.strip())
            elif cur is not None and line.startswith("- "):
                cur = None
    return out


def _battles_after(cmd: dict) -> list[str]:
    return [
        s
        for s in cmd["sub"]
        if s.startswith("⚔") or s.startswith("- ⚔") or "⚔ " in s[:4]
    ]


def _band(cmd: dict) -> str:
    text = cmd["head"] + " " + " ".join(cmd["sub"])
    m = re.search(r"balance of force looks (\w+)", text)
    if not m:
        return ""
    word = m.group(1)
    for band in ("unfavorable", "favorable", "even"):
        if band.startswith(word) or word.startswith(band):
            return band
    return ""


BATTLE_RX = re.compile(
    r"⚔ (?P<a>[^()]+?) \(lost (?P<al>[\d,]+)[^)]*\) vs (?P<d>[^()]+?) \(lost (?P<dl>[\d,]+)[^)]*\)"
)


def _int(s):
    try:
        return int(str(s).replace(",", ""))
    except Exception:
        return None


# ═════════════════════════ THE ENDING ═════════════════════════
def r_ending_F1(arms, ctx):
    if _need(arms, "PRESS"):
        return _unmeasured("PRESS did not run")
    a = arms["PRESS"]
    hits = _blocks_with(a, "ENDING — THE IMPERIAL PEACE")
    if not hits:
        return _res(
            True, False, f"PRESS status {a.status}; no IMPERIAL PEACE ending line"
        )
    turn = hits[0][0]
    return _res(
        True, turn <= 36, f"THE IMPERIAL PEACE at turn {turn} (status {a.status})"
    )


def r_ending_F2(arms, ctx):
    if _need(arms, "VERDICT"):
        return _unmeasured("VERDICT did not run")
    a = arms["VERDICT"]
    hits = _blocks_with(a, "THE VERDICT")
    if not hits:
        return _res(True, False, f"VERDICT status {a.status}; no Verdict block")
    turn = hits[0][0]
    return _res(True, 44 <= turn <= 46, f"Verdict at turn {turn}: {hits[0][1][:140]}")


def r_ending_C1(arms, ctx):
    if _need(arms, "CONG"):
        return _unmeasured("CONG did not run")
    a = arms["CONG"]
    # Step 1 (Sept 29, 2026): the CONGRESS's own dissolution — the CONGRESS
    # line ("dissolved on turn N — <cause>") or the dispatch beat — never a
    # league's ("Coalition against France has dissolved — the league is
    # spent"), which the first reader took as the named cause.
    diss = [(t, l) for t, l in _blocks_with(a, "dissolv") if "congress" in l.lower()]
    if not diss:
        peace = _blocks_with(a, "IMPERIAL PEACE")
        return _res(
            True,
            True,
            "the Congress was not dissolved in the sitting"
            + (f"; {peace[0][1][:100]}" if peace else ""),
        )
    bad = [
        (t, l)
        for t, l in diss
        if re.search(r"unsign|reopen|cede|cession|retained", l, re.I)
    ]
    if bad:
        return _res(
            True,
            False,
            f"dissolved by a reopened cession at turn {bad[0][0]}: {bad[0][1][:200]}",
        )
    return _res(
        True,
        True,
        f"dissolved for a named cause at turn {diss[0][0]}: {diss[0][1][:200]}",
    )


def r_ending_C2(arms, ctx):
    if _need(arms, "CONG"):
        return _unmeasured("CONG did not run")
    r = _find_cmd(arms["CONG"], "summon the congress")
    if not r:
        return _unmeasured("CONG has no summons command")
    msg = str(r.get("message", ""))
    ok = bool(
        re.search(r"\b40\b", msg) and re.search(r"league|coalition|gate", msg, re.I)
    )
    return _res(True, ok, "summons: " + msg[:220])


def r_ending_C4(arms, ctx):
    vals = {n: _titled_at(arms[n]) for n in CMD_ARMS if n in arms}
    if len(vals) < 3 or any(v is None for v in vals.values()):
        return _unmeasured(f"titled counts missing: {vals}")
    ok = sum(1 for v in vals.values() if v >= 40) >= 2
    return _res(True, ok, f"titled at turn 40: {vals}")


def r_ending_C5(arms, ctx):
    vals = {
        n: _titled_at(arms[n])
        for n in ("CMD-H", "CMD-A", "CMD-M", "CMD-ULM", "REACH-AAR", "REACH-GEVB")
        if n in arms
    }
    vals = {k: v for k, v in vals.items() if v is not None}
    if not vals:
        return _unmeasured("no titled counts")
    return _res(
        True,
        max(vals.values()) >= 45,
        f"best road {max(vals, key=vals.get)} = {max(vals.values())}; all {vals}",
    )


# ═════════════════════════ DIPLOMACY ═════════════════════════
PEACE_RX = re.compile(
    r"Treaty signed: [^.]*→ (Peace|Armistice)|peace[^.]{0,40}ratif|Settlement Ratif|ratif[^.]{0,60}peace",
    re.I,
)


def r_diplomacy_F1(arms, ctx):
    need = [n for n in ("PROP-H", "PROP-A", "PROP-M") if n in arms]
    if len(need) < 3:
        return _unmeasured(f"propose arms present: {need}")
    ev = {}
    for n in need:
        hits = [
            l
            for t, l in arms[n].blocks()
            for l in [l]
            for l in l.split("\n")
            if PEACE_RX.search(l)
        ]
        ev[n] = hits[0][:120] if hits else "no peace"
    return _res(
        True,
        all(v != "no peace" for v in ev.values()),
        json.dumps(ev, ensure_ascii=False)[:500],
    )


def r_diplomacy_F2(arms, ctx):
    if _need(arms, "ADV"):
        return _unmeasured("ADV did not run")
    types = set(re.findall(r"^- MISSION (.+?) — ", arms["ADV"].md, re.M))
    return _res(True, len(types) >= 2, f"mission types ticked: {sorted(types)}")


def r_diplomacy_C3(arms, ctx):
    if _need(arms, "VOLTE"):
        return _unmeasured("VOLTE did not run")
    hits = _blocks_with(arms["VOLTE"], "volte_face")
    return _res(
        True, bool(hits), hits[0][1][:160] if hits else "no volte_face on the volte arm"
    )


def _dl_lines(ctx, key):
    script = ctx.get("dl_script") or {}
    return (script.get("dl_lines") or {}).get(key, [])


def r_diplomacy_C4(arms, ctx):
    if _need(arms, "DL"):
        return _unmeasured("DL did not run")
    a = arms["DL"]
    fails = []
    seen = 0
    for line in _dl_lines(ctx, "RS-7"):
        r = _find_cmd(a, line)
        if not r:
            continue
        seen += 1
        msg = str(r.get("message", ""))
        if (
            re.search(r"await your instructions", msg, re.I)
            or SHRUG_RX.search(msg)
            or r.get("success") is None
        ):
            fails.append(f"{line!r} → {msg[:80]}")
    if seen == 0:
        return _unmeasured("none of the RS-7 lines is on the DL digest")
    return _res(
        True,
        not fails,
        f"{seen} Cabinet phrasings; dead ends: {fails[:3]}"
        if fails
        else f"{seen} phrasings all start a mission or refuse with a price",
    )


def r_diplomacy_C5(arms, ctx):
    if _need(arms, "DL"):
        return _unmeasured("DL did not run")
    r = _find_cmd(arms["DL"], "request terms from Austria")
    if not r:
        return _unmeasured("the request-terms line is not on the DL digest")
    msg = str(r.get("message", ""))
    # honest: Austria answers, or the league's LEADER is named as the court that answers for the war ("leads a league … names no terms")
    honest = bool(
        re.search(
            r"answers? for (the war|its war|the coalition|the league)|answer for|leads (a|the) (league|coalition)|speaks for",
            msg,
            re.I,
        )
    ) or ("Austria" in msg and "Britain's chancery" not in msg)
    return _res(True, honest, msg[:220])


def r_diplomacy_C6(arms, ctx):
    hits = []
    for n, a in arms.items():
        for m in re.finditer(
            r"Relations with [A-Za-z ]+ are insufficient for ([A-Z_]+)", a.md
        ):
            hits.append(f"{n}: {m.group(0)}")
    if not arms:
        return _unmeasured("no arms")
    return _res(
        True,
        not hits,
        f"{len(hits)} treaty-refused-after-accept lines"
        + (": " + "; ".join(hits[:3]) if hits else ""),
    )


# ═════════════════════════ FIRST CONTACT ═════════════════════════
def r_first_contact_F1(arms, ctx):
    if _need(arms, "FC"):
        return _unmeasured("FC did not run")
    cmds = _cmd_records(arms["FC"])
    shrugs = [c["text"] for c in cmds if SHRUG_RX.search(str(c.get("message", "")))]
    refusals = [
        c["text"]
        for c in cmds
        if c.get("success") is False
        and not re.search(r"attack|undo", str(c.get("text")), re.I)
    ]
    return _res(
        True,
        not shrugs and not refusals,
        f"{len(cmds)} lines; shrugs {shrugs[:3]}; refusals {refusals[:3]}",
    )


def r_first_contact_F2(arms, ctx):
    if _need(arms, "SCH"):
        return _unmeasured("SCH did not run")
    steps = [int(x) for x in re.findall(r"^- SCHOOL step (\d+)", arms["SCH"].md, re.M)]
    return _res(
        True,
        bool(steps) and max(steps) >= 19,
        f"School steps reached: {sorted(set(steps))[-4:] if steps else 'none'}",
    )


def r_first_contact_C3(arms, ctx):
    if _need(arms, "DL"):
        return _unmeasured("DL did not run")
    out = []
    ok = True
    for line in _dl_lines(ctx, "RS-14"):
        r = _find_cmd(arms["DL"], line)
        if not r:
            continue
        msg = str(r.get("message", ""))
        good = r.get("success") is not False and not SHRUG_RX.search(msg)
        ok = ok and good
        out.append(f"{line!r} → {'answered' if good else 'shrug'}: {msg[:70]}")
    if not out:
        return _unmeasured("RS-14 lines not on the DL digest")
    return _res(True, ok, " | ".join(out))


def r_first_contact_C4(arms, ctx):
    if _need(arms, "DL"):
        return _unmeasured("DL did not run")
    cmds = [
        c
        for c in _cmd_blocks(arms["DL"])
        if c["text"].strip().lower() == "what can i do"
    ]
    if not cmds:
        return _unmeasured("'what can I do' not on the DL digest")
    msg = cmds[-1]["head"] + " / " + " / ".join(cmds[-1]["sub"])
    ok = bool(
        re.search(
            r"recruit|build|enact|invest|Talleyrand|grant|commission|lay down",
            msg,
            re.I,
        )
    )
    return _res(True, ok, msg[:260])


def r_first_contact_C6(arms, ctx):
    if _need(arms, "OP"):
        return _unmeasured("OP did not run")
    first = (
        [c for c in _cmd_blocks(arms["OP"]) if c["turn"] == arms["OP"].blocks()[0][0]]
        if arms["OP"].blocks()
        else []
    )
    bad = [c["text"][:50] for c in first if READING_REFUSAL_RX.search(c["head"])]
    return _res(True, not bad, f"loop 1: {len(first)} lines, reading refusals {bad}")


# ═════════════════════════ ECONOMY ═════════════════════════
def r_economy_F1(arms, ctx):
    recs = [(n, r) for n, a in arms.items() for r in a.kind("economy")]
    if not recs:
        return _unmeasured("no economy records")
    bad = [
        (n, r.get("net_residual"))
        for n, r in recs
        if int(r.get("net_residual") or 0) != 0
    ]
    return _res(True, not bad, f"{len(recs)} records; nonzero residuals {bad[:5]}")


def r_economy_C1(arms, ctx):
    if _need(arms, "LAW"):
        return _unmeasured("LAW did not run")
    for c in _cmd_blocks(arms["LAW"]):
        if (
            c["text"].strip().lower() == "enact the staff"
            and c["ok"]
            and not re.search(r"costs 9,000|treasury holds", c["head"])
        ):
            return _res(
                True,
                c["turn"] <= 9,
                f"the Staff enacted at loop {c['turn']}: {c['head'][:120]}",
            )
    return _res(True, False, "the Staff was never enacted on the LAW arm")


def r_economy_C5(arms, ctx):
    if _need(arms, "DL"):
        return _unmeasured("DL did not run")
    lines = _dl_lines(ctx, "AAR-6") or ["recruit 10000 infantry with Davout"]
    r = next(
        (_find_cmd(arms["DL"], line) for line in lines if _find_cmd(arms["DL"], line)),
        None,
    )
    if not r:
        return _unmeasured("the levy line is not on the DL digest")
    return _res(True, r.get("success") is True, str(r.get("message", ""))[:200])


# ═════════════════════════ NAVAL ═════════════════════════
def r_naval_F1(arms, ctx):
    return _suite_green(
        ctx["run_dir"],
        ["tests/test_naval_channel_gate.py", "tests/test_naval_substrate.py"],
        "naval gate",
    )


def r_naval_F2(arms, ctx):
    if _need(arms, "SEA"):
        return _unmeasured("SEA did not run")
    a = arms["SEA"]
    ok = (
        a.status in ("completed", "ending-reached")
        and not a.blockers
        and "SCRIPT PRECONDITION" not in a.md
    )
    return _res(
        True,
        ok,
        f"status {a.status}; blockers {a.blockers}; preconditions {'present' if 'SCRIPT PRECONDITION' in a.md else 'none'}",
    )


def r_naval_C1(arms, ctx):
    if _need(arms, "SEA"):
        return _unmeasured("SEA did not run")
    a = arms["SEA"]
    quotes = [
        (c["turn"], c["head"])
        for c in _cmd_blocks(a)
        if c["text"].strip().lower() == "order the diversion" and c["ok"]
    ]
    pairs = [
        (int(m.group(1)), int(m.group(2)))
        for _, h in quotes
        for m in [re.search(r"(\d+) times in 100 at her readiness \((\d+)\)", h)]
        if m
    ]
    # a throw resolves as open water (strait_open) or as the fleet caught coming home
    resolved = (
        len(_blocks_with(a, "diversion draws"))
        + len(_blocks_with(a, "shattered in action"))
        + len(_blocks_with(a, "caught coming home"))
    )
    if len(quotes) < 2:
        return _res(
            True,
            False,
            f"only {len(quotes)} diversion quotes (the second throw never came); resolved {resolved}",
        )
    priced = (
        all(odds == readiness - 25 for odds, readiness in pairs) if pairs else False
    )
    ok = priced and resolved >= 2
    return _res(
        True,
        ok,
        f"quotes (odds, readiness) {pairs} — odds = readiness − 25: {priced}; throws resolved {resolved}",
    )


def r_naval_C2(arms, ctx):
    ev = []
    for n in ("SEA", "DESC", "SHUT-H", "SHUT-A", "SHUT-M"):
        if n not in arms:
            continue
        groups = arms[n].by_turn()
        for i, g in enumerate(groups):
            fought = any(
                re.search(
                    r"fleet_action|TRAFALGAR|fleet action|loses \d+ sail|shattered in action|sail lost",
                    json.dumps(r),
                    re.I,
                )
                for r in g
                if r.get("kind")
                in ("rail", "dispatch_row", "campaign_log", "battle", "dispatch")
            )
            if fought:
                heads = [
                    str(r.get("headline", "")) for r in g if r.get("kind") == "dispatch"
                ]
                if i + 1 < len(groups):
                    heads += [
                        str(r.get("headline", ""))
                        for r in groups[i + 1]
                        if r.get("kind") == "dispatch"
                    ]
                ev.append((n, g[0].get("turn"), (heads[0] if heads else "")[:100]))
    if not ev:
        return _unmeasured("no fleet action on the naval arms")
    ok = any(
        re.search(r"fleet|sail|squadron|Admiralty|Trafalgar", h, re.I) for _, _, h in ev
    )
    return _res(True, ok, f"the dispatch on/after a fleet action: {ev[:3]}")


def r_naval_C3(arms, ctx):
    if _need(arms, "DESC"):
        return _unmeasured("DESC did not run")
    a = arms["DESC"]
    quotes = [
        c
        for c in _cmd_blocks(a)
        if re.search(r"\bland\b|expedition", c["text"], re.I) and c["ok"]
    ]
    q = " ".join(c["head"] + " " + " ".join(c["sub"]) for c in quotes)
    odds = bool(re.search(r"\d+ times in 100|\d+%|odds", q, re.I))
    lever = bool(re.search(r"readiness|sail|diversion|corps|squadron|ally", q, re.I))
    fell = bool(
        re.search(
            r"Munster.*(captured|falls|taken)|captured Munster|landing at Munster",
            a.md,
            re.I,
        )
    )
    return _res(
        True,
        odds and lever and fell,
        f"quotes {len(quotes)}; odds named {odds}; lever named {lever}; Munster falls {fell}",
    )


def r_naval_C4(arms, ctx):
    need = [n for n in ("SHUT-H", "SHUT-A", "SHUT-M") if n in arms]
    if len(need) < 3:
        return _unmeasured(f"shut-out arms present: {need}")
    ev = {}
    for n in need:
        t = None
        for turn, line in _blocks_with(arms[n], "Britain"):
            if re.search(
                r"sues|armistice|proposes peace|offers peace|peace proposal|settlement offer",
                line,
                re.I,
            ):
                t = turn
                break
        ev[n] = t
    return _res(
        True,
        all(t is not None and t <= 10 for t in ev.values()),
        f"Britain sues at turn {ev}",
    )


# ═════════════════════════ LIVING BALANCE ═════════════════════════
def r_living_balance_F1(arms, ctx):
    vals = {n: _last_ledger(arms[n]).get("provinces") for n in CMD_ARMS if n in arms}
    if len(vals) < 3 or any(v is None for v in vals.values()):
        return _unmeasured(f"CMD ledgers missing: {vals}")
    return _res(
        True, all(int(v) >= 20 for v in vals.values()), f"France at turn 40: {vals}"
    )


def r_living_balance_F2(arms, ctx):
    return _suite_green(
        ctx["run_dir"],
        [
            "tests/test_combat_sweep_metrics.py",
            "tests/test_ai_intent_threat_migration.py",
        ],
        "M1–M7 + BASELINE_SERIES",
    )


def r_living_balance_C1(arms, ctx):
    s, runs = _aiv(ctx["run_dir"])
    if not s:
        return _unmeasured("no AIV summary")
    wars = {k: v.get("ai_wars", 0) for k, v in (s.get("arm_c") or {}).items()}
    return _res(
        True, any(int(v) > 0 for v in wars.values()), f"AI-vs-AI wars per seed: {wars}"
    )


def r_living_balance_C2(arms, ctx):
    s, runs = _aiv(ctx["run_dir"])
    if not s:
        return _unmeasured("no AIV summary")
    tps = {
        k: v.get("third_party_settlements", 0)
        for k, v in (s.get("arm_c") or {}).items()
    }
    return _res(
        True,
        any(int(v) > 0 for v in tps.values()),
        f"standalone third-party settlements per seed: {tps}",
    )


def r_living_balance_C3(arms, ctx):
    s, runs = _aiv(ctx["run_dir"])
    if not s:
        return _unmeasured("no AIV summary")
    pp = {
        k: (v.get("beats") or {}).get("third_party_peace", 0)
        for k, v in (s.get("arm_c") or {}).items()
    }
    return _res(
        True,
        bool(pp) and all(int(v) > 0 for v in pp.values()),
        f"exhaustion pair peaces (third_party_peace beats) per seed: {pp}",
    )


def r_living_balance_C6(arms, ctx):
    s, runs = _aiv(ctx["run_dir"])
    if not runs:
        return _unmeasured("no AIV per-run records")
    elim = {
        k: (v.get("derived") or {}).get("eliminations")
        for k, v in runs.items()
        if k.startswith("armC")
    }
    if not elim:
        return _unmeasured("no arm C runs")
    return _res(
        True,
        all(bool(v) for v in elim.values()),
        "an AI court takes another's last province (eliminations, the proxy the run records) per seed: "
        + json.dumps({k: [e[1] for e in (v or [])] for k, v in elim.items()})[:400],
    )


WAR_DECL_RX = re.compile(
    r"^(?P<court>[A-Z][A-Za-z ]+?) (?:declares|has declared) war on (France|us)\b"
)


def r_living_balance_C4(arms, ctx):
    need = [n for n in CMD_ARMS if n in arms]
    if not need:
        return _unmeasured("no CMD arms")
    ev = []
    found = False
    for n in need:
        a = arms[n]
        peace_turn = {}
        for turn, line in _blocks_with(a, "Treaty signed:"):
            m = re.search(
                r"Treaty signed: [^.]*→ (Peace|Armistice) with ([A-Z][A-Za-z ]+)", line
            )
            if m:
                peace_turn.setdefault(m.group(2).strip(), turn)
        for turn, text in a.blocks():
            for line in text.split("\n"):
                mm = re.search(
                    r"([A-Z][A-Za-z ]+?) (?:declares|declared) war on (?:France|us)",
                    line,
                )
                if mm and not re.search(
                    r"enters the war|joins|cascade|calls? .* to arms", line, re.I
                ):
                    # "Britain has declared war on France" — the court is the
                    # word before the auxiliary, never the auxiliary (Step 3
                    # found the reader reading "has" as the court, so every
                    # league declaration was invisible to it).
                    words = [w for w in mm.group(1).strip().split()
                             if w.lower() not in ("has", "have", "had")]
                    court = words[-1] if words else mm.group(1).strip()
                    pt = peace_turn.get(court)
                    if pt is not None and turn - pt > 5:
                        found = True
                        ev.append((n, court, pt, turn))
        if not ev:
            ev.append((n, "peaces", dict(list(peace_turn.items())[:4])))
    return _res(True, found, f"declarations beyond the fresh-peace floor: {ev[:4]}")


# ═════════════════════════ COMBAT LEGIBILITY ═════════════════════════
def r_combat_legibility_F1(arms, ctx):
    lines = [
        (n, l)
        for n in ("OP", "FLD", "CMD-H")
        if n in arms
        for _, l in _blocks_with(arms[n], "⚔")
    ]
    if not lines:
        return _unmeasured("no battle lines")
    bad = [(n, l[:90]) for n, l in lines if len(re.findall(r"\(lost [\d,]+", l)) < 2]
    return _res(
        True, not bad, f"{len(lines)} battle lines; missing a side's losses: {bad[:3]}"
    )


_BOARD_REFUSAL = re.compile(
    r"recovering from retreat|cannot scout|is broken|is captured|is a prisoner|"
    r"out of range|not in range|no longer stands",
    re.I,
)


def r_combat_legibility_F2(arms, ctx):
    """The scout of a hostile capital names its garrison. §4.2: a BOARD
    refusal (the scout refused because the man is recovering, captured or
    out of range) is counted separately from a reading refusal — it does
    not test the item. The reader looks across the arms for a scout of a
    capital the board let through; when every one was board-refused the
    item is unmeasured with the refusals counted."""
    board = []
    for n in ("OP", "FLD", "CMD-H"):
        if n not in arms:
            continue
        for c in _cmd_blocks(arms[n]):
            if not re.search(r"scout (Vienna|Berlin|London|Madrid|Munich|Dresden)", c["text"], re.I):
                continue
            if not c["ok"] and _BOARD_REFUSAL.search(c["head"]):
                board.append(f"{n} t{c['turn']}: {c['head'][:80]}")
                continue
            return _res(
                True,
                "Garrison" in c["head"] or any("Garrison" in s for s in c["sub"]),
                f"{n} turn {c['turn']}: {c['head'][:200]}"
                + (f"; board refusals counted separately: {board}" if board else ""),
            )
    if board:
        return _unmeasured(f"every capital scout was a board refusal: {board}")
    return _unmeasured("no arm scouted a capital")


def r_combat_legibility_C1(arms, ctx):
    fails = []
    n_att = 0
    for n in ("OP", "FLD", "CMD-H"):
        if n not in arms:
            continue
        for c in _cmd_blocks(arms[n]):
            if not re.search(
                r"\battack\b|fall upon|assault|storm\b|charge\b", c["text"], re.I
            ):
                continue
            fought = any("⚔" in s for s in c["sub"])
            if not fought:
                continue
            n_att += 1
            if "MUSTER" not in c["head"] and not any("MUSTER" in s for s in c["sub"]):
                fails.append(f"{n} t{c['turn']}: {c['text'][:40]}")
    if n_att == 0:
        return _unmeasured("no attack that fought")
    return _res(
        True, not fails, f"{n_att} attacks fought; without a muster first: {fails[:4]}"
    )


def r_combat_legibility_C2(arms, ctx):
    rows = {"favorable": [], "even": [], "unfavorable": []}
    for n in ("OP", "FLD", "CMD-H", "CMD-A", "CMD-M"):
        if n not in arms:
            continue
        for c in _cmd_blocks(arms[n]):
            band = _band(c)
            if not band:
                continue
            for s in c["sub"]:
                m = BATTLE_RX.search(s)
                if m:
                    al, dl = _int(m.group("al")), _int(m.group("dl"))
                    if al is not None and dl is not None:
                        rows[band].append(al < dl)
                    break
    fav, even = rows["favorable"], rows["even"]
    if len(fav) < 5:
        return _unmeasured(f"only {len(fav)} favorable battles read (need 5)")
    fav_rate = sum(fav) / len(fav)
    even_rate = (sum(even) / len(even)) if even else 0.0
    ok = fav_rate >= 0.70 and (not even or fav_rate > even_rate)
    return _res(
        True,
        ok,
        f"favorable out-bleeds {sum(fav)}/{len(fav)} = {fav_rate:.2f}; even {sum(even)}/{len(even)}; unfavorable {sum(rows['unfavorable'])}/{len(rows['unfavorable'])}",
    )


def r_combat_legibility_C4(arms, ctx):
    if _need(arms, "DL"):
        return _unmeasured("DL did not run")
    blocks = [
        c
        for c in _cmd_blocks(arms["DL"])
        if c["text"].strip().lower() == "what if davout attacks mack?"
    ]
    if not blocks:
        return _unmeasured("the what-if line is not on the DL digest")
    c = blocks[-1]
    text = c["head"] + " / " + " / ".join(c["sub"])
    mustered = "MUSTER" in text
    refuses = bool(
        re.search(
            r"would be refused|Nothing spent|is fortified|unfortify first",
            c["head"],
            re.I,
        )
    )
    return _res(
        True,
        refuses and not mustered,
        ("weighs a muster for a fortified man: " if mustered else "") + text[:220],
    )


def r_combat_legibility_C5(arms, ctx):
    hits = {}
    for n in ("OP", "FLD", "CMD-H", "CMD-A", "CMD-M"):
        if n not in arms:
            continue
        for turn, text in arms[n].blocks():
            for line in text.split("\n"):
                if "⚔" in line or "MUSTER" in line or line.startswith("- enemy phase:"):
                    for tok in RAW_KEY_RX.findall(line):
                        if tok not in RAW_KEY_ALLOW:
                            hits.setdefault(tok, []).append(f"{n} t{turn}")
    if not any(n in arms for n in ("OP", "FLD", "CMD-H")):
        return _unmeasured("no combat arms")
    total = sum(len(v) for v in hits.values())
    return _res(
        True,
        total == 0,
        f"raw keys in combat/muster/enemy-phase lines: {total} "
        + json.dumps({k: len(v) for k, v in hits.items()})[:300],
    )


# ═════════════════════════ MARSHAL DRAMA ═════════════════════════
def r_marshal_drama_F2(arms, ctx):
    if _need(arms, "OP"):
        return _unmeasured("OP did not run")
    a = arms["OP"]
    fired = (
        _blocks_with(a, "jealousy_confrontation")
        + _blocks_with(a, "seeks an audience")
        + _blocks_with(a, "demands to be heard")
    )
    resolved = (
        _blocks_with(a, "runs its course")
        + _blocks_with(a, "jealousy_resolved")
        + _blocks_with(a, "Settled")
    )
    return _res(
        True,
        bool(fired) and bool(resolved),
        f"grievances fired {len(fired)}, heard/resolved lines {len(resolved)}"
        + (f"; e.g. {resolved[0][1][:100]}" if resolved else ""),
    )


def r_marshal_drama_C1(arms, ctx):
    if _need(arms, "OP"):
        return _unmeasured("OP did not run")
    pops = arms["OP"].kind("popup")
    modals = sum(1 for p in pops if p.get("key") == "marshal_petition")
    aud = sum(1 for p in pops if p.get("key") == "marshal_audience")
    return _res(
        True, modals <= 3 and aud >= 3, f"petition modals {modals}, audiences {aud}"
    )


def r_marshal_drama_C4(arms, ctx):
    lines = [
        (n, t, l)
        for n in ("OP", "CMD-H", "CMD-A", "CMD-M", "FLD")
        if n in arms
        for t, l in _blocks_with(arms[n], "crown")
    ]
    moves = [
        (n, t, l)
        for n, t, l in lines
        if re.search(
            r"crown (passes|moves|goes|lost|falls|is lost|now)|loses the crown|takes the crown|wears the crown",
            l,
            re.I,
        )
    ]
    if not moves:
        return _unmeasured("no crown moved on the arms")
    bad = [
        l[:100]
        for _, _, l in moves
        if re.search(r"lost|loses|falls", l, re.I)
        and not re.search(r"to [A-Z][a-z]+|passes to|now [A-Z][a-z]+", l)
    ]
    return _res(
        True,
        not bad,
        f"{len(moves)} crown moves; loss lines without a destination: {bad[:2]}; e.g. {moves[0][2][:120]}",
    )


# ═════════════════════════ VASSALS ═════════════════════════
def r_vassals_F1(arms, ctx):
    vals = {
        n: len(_last_ledger(arms[n]).get("vassals") or {})
        for n in CMD_ARMS
        if n in arms
    }
    if len(vals) < 3:
        return _unmeasured(f"CMD arms present: {list(vals)}")
    return _res(
        True, all(v >= 2 for v in vals.values()), f"satellites at turn 40: {vals}"
    )


def r_vassals_F2(arms, ctx):
    if _need(arms, "CMDR-H"):
        return _unmeasured("CMDR-H did not run")
    a = arms["CMDR-H"]
    leds = a.kind("ledger")
    if not leds:
        return _unmeasured("CMDR-H has no ledger records")
    start = len(leds[0].get("vassals") or {})
    lost_turn = None
    for i, l in enumerate(leds):
        if len(l.get("vassals") or {}) < start:
            lost_turn = i + 1
            break
    rebel = _blocks_with(a, "rebell") + _blocks_with(a, "independen")
    return _res(
        True,
        (lost_turn is not None and lost_turn <= 30) or any(t <= 30 for t, _ in rebel),
        f"satellites {start} → first loss at turn {lost_turn}; rebellion lines {[(t, l[:60]) for t, l in rebel[:2]]}",
    )


def r_vassals_C1(arms, ctx):
    vals = {
        n: sum(
            1
            for p in arms[n].kind("popup")
            if "client_petition" in str(p.get("summary", ""))
        )
        for n in CMD_ARMS
        if n in arms
    }
    if len(vals) < 3:
        return _unmeasured(f"CMD arms present: {list(vals)}")
    return _res(
        True, all(v >= 4 for v in vals.values()), f"priced petitions per seed: {vals}"
    )


def r_vassals_C4(arms, ctx):
    ev = []
    ok = True
    seen = False
    for n in ("CMDR-H", "CMD-H", "CMD-A", "CMD-M"):
        if n not in arms:
            continue
        groups = arms[n].by_turn()
        blocks = dict(arms[n].blocks())
        crossed = set()
        for i, g in enumerate(groups):
            led = next((r for r in g if r.get("kind") == "ledger"), None)
            if not led:
                continue
            for sat, loy in (led.get("vassals") or {}).items():
                if int(loy) < 40 and sat not in crossed:
                    crossed.add(sat)
                    seen = True
                    t = g[0].get("turn")
                    window = (
                        blocks.get(t, "")
                        + blocks.get(t - 1, "")
                        + blocks.get(t + 1, "")
                    )
                    named = bool(
                        re.search(
                            rf"{re.escape(sat.split()[-1])}[^\n]*(invest|autonomy|garrison|cede|grant|relief|subsid)|(invest|autonomy|garrison|cede|grant|relief|subsid)[^\n]*{re.escape(sat.split()[-1])}",
                            window,
                            re.I,
                        )
                    )
                    ok = ok and named
                    ev.append(
                        f"{n} t{t}: {sat} at {loy} → remedy {'named' if named else 'MISSING'}"
                    )
    if not seen:
        return _unmeasured("no satellite fell under 40 on the arms")
    return _res(True, ok, " | ".join(ev[:4]))


# ═════════════════════════ UI/UX ═════════════════════════
def r_ui_ux_C4(arms, ctx):
    if _need(arms, "OP"):
        return _unmeasured("OP did not run")
    worst = (0, None, [])
    blocking = {k.split("[")[0] for k in BLOCKING_POPUPS}
    for g in arms["OP"].by_turn():
        ends = [
            i
            for i, r in enumerate(g)
            if r.get("kind") == "command"
            and str(r.get("text", "")).strip().lower() == "end turn"
        ]
        if not ends:
            continue
        raised = [
            r
            for r in g[ends[-1] :]
            if r.get("kind") == "popup" and str(r.get("key")).split("[")[0] in blocking
        ]
        if len(raised) > worst[0]:
            worst = (
                len(raised),
                g[0].get("turn"),
                [
                    str(r.get("key")) + ":" + str(r.get("summary", ""))[:30]
                    for r in raised
                ],
            )
    return _res(
        True,
        worst[0] <= 3,
        f"most blocking popups one end turn raised: {worst[0]} (turn {worst[1]}) {worst[2][:5]}",
    )


def _cli_unmeasured(arms, ctx):
    return _unmeasured("the client arm (IQ-10 frames) needs the Godot binary; not run")


r_ui_ux_F1 = r_ui_ux_F2 = r_ui_ux_C1 = r_ui_ux_C2 = r_ui_ux_C3 = _cli_unmeasured


# ═════════════════════════ COMMAND & PARSING ═════════════════════════
def r_command_F1(arms, ctx):
    pe = _peval(ctx["run_dir"]).get("corpus")
    if not pe:
        return _unmeasured("PEVAL did not run")
    return _res(
        True,
        pe.get("exit") == 0 and (pe.get("passed") == pe.get("total")),
        pe.get("tail", "")[:200],
    )


def r_command_F2(arms, ctx):
    pe = _peval(ctx["run_dir"]).get("replay")
    if not pe:
        return _unmeasured("PEVAL did not run")
    return _res(
        True,
        pe.get("exit") == 0 and (pe.get("passed") == pe.get("total")),
        pe.get("tail", "")[:200],
    )


def r_command_C1(arms, ctx):
    if _need(arms, "OP"):
        return _unmeasured("OP did not run")
    cmds = _cmd_records(arms["OP"])
    shrugs = [
        c["text"][:50] for c in cmds if SHRUG_RX.search(str(c.get("message", "")))
    ]
    return _res(
        True, len(shrugs) <= 1, f"{len(cmds)} lines, shrugs {len(shrugs)}: {shrugs[:3]}"
    )


def r_command_C2(arms, ctx):
    if _need(arms, "OP"):
        return _unmeasured("OP did not run")
    bad = [
        c["text"][:50]
        for c in _cmd_blocks(arms["OP"])
        if READING_REFUSAL_RX.search(c["head"])
    ]
    return _res(True, not bad, f"reading refusals {len(bad)}: {bad[:3]}")


def r_command_C4(arms, ctx):
    if _need(arms, "DL"):
        return _unmeasured("DL did not run")
    a = arms["DL"]
    blocks = {c["text"].strip().lower(): c for c in _cmd_blocks(a)}
    fails = []
    for line in _dl_lines(ctx, "RS-6"):
        c = blocks.get(line.strip().lower())
        if c and (
            not c["ok"]
            or re.search(r"Cannot find|In Support Of|Aid Of|Of Ney", c["head"])
        ):
            fails.append(f"RS-6 {line!r} → {c['head'][:60]}")
    for line in _dl_lines(ctx, "RS-8"):
        c = blocks.get(line.strip().lower())
        if c and (not c["ok"] or "Mack" not in c["head"] + " ".join(c["sub"])):
            fails.append(f"RS-8 → {c['head'][:60] if c else 'missing'}")
    for line in _dl_lines(ctx, "RS-11"):
        c = blocks.get(line.strip().lower())
        if c and (not c["ok"] or SHRUG_RX.search(c["head"])):
            fails.append(f"RS-11 → {c['head'][:60]}")
    for line in _dl_lines(ctx, "SF-V4"):
        c = blocks.get(line.strip().lower())
        if c:
            # Chunk 3b (Oct 3, 2026): a battle AFTER the player's answer to
            # the question is the order he gave, not a substitution — the
            # driver answers the clarification by its dial ("first": yes), so
            # only a fight BEFORE that answer fails the ruling (§6.3).
            subs = c["sub"]
            answered_at = next(
                (i for i, s in enumerate(subs)
                 if s.lstrip("- ").startswith("POPUP clarification")),
                len(subs),
            )
            fought = any("⚔" in s for s in subs[:answered_at]) or re.search(
                r"marches on|MUSTER", c["head"]
            )
            asked = (
                bool(
                    re.search(
                        r"\?|did you mean|which|no foe our maps know", c["head"], re.I
                    )
                )
                and not fought
            )
            if not asked:
                fails.append(f"SF-V4 {line!r} → {c['head'][:70]}")
    if not blocks:
        return _unmeasured("DL has no commands")
    return _res(
        True,
        not fails,
        "all docked command lines execute or ask"
        if not fails
        else " | ".join(fails[:4]),
    )


def r_command_C5(arms, ctx):
    if _need(arms, "TYPED"):
        return _unmeasured("TYPED did not run")
    script = ctx.get("typed_script") or {}
    ORDER_RX = re.compile(
        r"\b(attack|march|move|hold|retreat|scout|fortify|drill|recruit|build|halt)\b",
        re.I,
    )
    QUESTION_LEAD = re.compile(
        r"^(what|why|can|is|who|where|am|how|should|shall|would|could|does|do|did|will|are|has|have|when|which)\b",
        re.I,
    )
    MARSHALS = (
        "Ney",
        "Davout",
        "Soult",
        "Lannes",
        "Murat",
        "Bernadotte",
        "Massena",
        "Napoleon",
    )
    blocks = _cmd_blocks(arms["TYPED"])
    ev = []
    ok = True
    for c in blocks:
        if c["text"].strip().lower() != "end turn":
            continue
        m = re.search(r"Warning: (\d+) actions? unused", c["head"])
        unused = int(m.group(1)) if m else 0
        lines = script.get("turns", {}).get(str(c["turn"]), [])

        def _is_order(l):
            # the game's own rule (clause_guards): an ADDRESSED line keeps its order even with a "?";
            # an unaddressed "?" or an interrogative lead is a question; a prohibition or a contingency is no order
            addressed = any(l.strip().lower().startswith(mn.lower()) for mn in MARSHALS)
            if re.search(r"\bnever\b|\bif\b", l, re.I):
                return False
            if QUESTION_LEAD.match(l.strip()):
                return False
            if l.rstrip().endswith("?") and not addressed:
                return False
            return bool(ORDER_RX.search(l))

        order_lines = [
            l for l in lines if _is_order(l) and l.strip().lower() != "end turn"
        ]
        # an order turn EXPECTS a spend only if one of its orders was carried out (a board refusal spends nothing)
        carried = [
            b
            for b in blocks
            if b["turn"] == c["turn"] and b["ok"] and b["text"] in order_lines
        ]
        spent = unused < 4 if m else True
        if order_lines and carried and not spent:
            ok = False
            ev.append(f"t{c['turn']}: {len(carried)} orders carried out, nothing spent")
        if not order_lines and spent:
            ok = False
            ev.append(f"t{c['turn']}: a question turn spent actions ({unused} unused)")
    if not ev:
        ev.append(
            "question turns spent 0; order turns spent when an order was carried out"
        )
    return _res(True, ok, " | ".join(ev[:4]))


def r_command_C6(arms, ctx):
    return _unmeasured("the live-parser arm needs an ANTHROPIC_API_KEY; not run")


# ═════════════════════════ NARRATION ═════════════════════════
def r_narration_F1(arms, ctx):
    need = [n for n in CMD_ARMS if n in arms]
    if not need:
        return _unmeasured("no CMD arms")
    ev = {}
    ok = True
    for n in need:
        groups = arms[n].by_turn()
        no_head = 0
        raw = 0
        for g in groups:
            d = [r for r in g if r.get("kind") == "dispatch"]
            if not d:
                no_head += 1
            elif any(
                tok not in RAW_KEY_ALLOW
                for tok in RAW_KEY_RX.findall(str(d[0].get("headline", "")))
            ):
                raw += 1
        ev[n] = f"{no_head}/{len(groups)} turns without a headline, {raw} raw"
        ok = ok and no_head == 0 and raw == 0
    return _res(True, ok, json.dumps(ev))


def r_narration_F2(arms, ctx):
    need = [n for n in CMD_ARMS if n in arms]
    if not need:
        return _unmeasured("no CMD arms")
    worst = 0
    for n in need:
        for g in arms[n].by_turn():
            worst = max(
                worst,
                sum(
                    1
                    for r in g
                    if r.get("kind") == "dispatch_row"
                    and str(r.get("dtype")) in COURTS_TYPES
                ),
            )
    return _res(
        True,
        worst <= 3,
        f"most routine intent lines in one dispatch: {worst} (cap 2 + one tail)",
    )


def r_narration_C1(arms, ctx):
    need = [n for n in CMD_ARMS if n in arms]
    if not need:
        return _unmeasured("no CMD arms")
    ev = {}
    ok = True
    any_class = False
    for n in need:
        classes = []
        for g in arms[n].by_turn():
            d = [r for r in g if r.get("kind") == "dispatch"]
            classes.append(str(d[0].get("headline_class", "")) if d else "")
        if any(classes):
            any_class = True
        worst = ("", 0)
        for i in range(0, max(1, len(classes) - 9)):
            window = [c for c in classes[i : i + 10] if c]
            # a tie is broken by name, so two runs of the reader print the same class
            for c in sorted(set(window)):
                if window.count(c) > worst[1]:
                    worst = (c, window.count(c))
        ev[n] = worst
        ok = ok and worst[1] <= 4
    if not any_class:
        return _unmeasured(
            "the dispatch records carry no headline_class (a pre-SF-M archive)"
        )
    return _res(True, ok, f"worst class in any 10-turn window: {ev}")


def r_narration_C2(arms, ctx):
    need = [n for n in ("CMD-H", "CMD-A", "CMD-M", "OP") if n in arms]
    if not need:
        return _unmeasured("no arms")
    rep = []
    nameless = []
    for n in need:
        for g in arms[n].by_turn():
            rails = [r for r in g if r.get("kind") in ("rail", "dispatch_row")]
            counts = {}
            for r in rails:
                k = (str(r.get("dtype")), str(r.get("text", ""))[:80])
                counts[k] = counts.get(k, 0) + 1
            rep += [
                f"{n} t{g[0].get('turn')} {k[0]}×{v}"
                for k, v in counts.items()
                if v > 3
            ]
            nameless += [
                f"{n} t{g[0].get('turn')}: {str(r.get('text', ''))[:60]}"
                for r in rails
                if re.search(
                    r"enters the war\.?$|joins the war\.?$",
                    str(r.get("text", "")).strip(),
                )
            ]
    return _res(
        True,
        not rep and not nameless,
        f"rail rows repeated >3×: {rep[:3]}; war entries naming no enemy: {nameless[:3]}",
    )


# ═════════════════════════ AI ALIVENESS ═════════════════════════
def r_ai_aliveness_F1(arms, ctx):
    return _suite_green(
        ctx["run_dir"], ["tests/test_ai_intent_assurance.py"], "AI-intent assurance"
    )


def r_ai_aliveness_F2(arms, ctx):
    if not arms:
        return _unmeasured("no arms")
    bad = []
    for n, a in arms.items():
        if a.status not in ("completed", "ending-reached", "game-over") or a.blockers:
            bad.append(f"{n}: {a.status} {a.blockers[:1]}")
        log = a.path.parent / f"{n}.log"
        if log.exists() and "Traceback" in log.read_text(
            encoding="utf-8", errors="replace"
        ):
            bad.append(f"{n}: traceback in log")
    return _res(
        True,
        not bad,
        f"{len(arms)} arms; "
        + (
            "all completed, no blockers, no tracebacks"
            if not bad
            else "; ".join(bad[:4])
        ),
    )


def r_ai_aliveness_C1(arms, ctx):
    need = [n for n in CMD_ARMS if n in arms]
    if not need:
        return _unmeasured("no CMD arms")
    ev = {
        n: (
            _count_dtype(arms[n], "law_enacted_abroad"),
            sum(
                1
                for r in _dispatch_rows(arms[n])
                if "law" in str(r.get("dtype")) and "laps" in str(r.get("dtype"))
            ),
        )
        for n in need
    }
    return _res(
        True,
        all(13 <= e <= 18 and l == 0 for e, l in ev.values()),
        f"laws enacted abroad (enacted, lapsed) per seed: {ev}",
    )


def r_ai_aliveness_C2(arms, ctx):
    need = [
        n
        for n in (
            "CMD-H",
            "CMD-A",
            "CMD-M",
            "CMD-ULM",
            "VOLTE",
            "REACH-AAR",
            "REACH-GEVB",
        )
        if n in arms
    ]
    if not need:
        return _unmeasured("no 40-turn arms")
    ev = {n: len(_blocks_with(arms[n], "design_promoted")) for n in need}
    return _res(
        True,
        all(v >= 1 for v in ev.values()),
        f"design promotions per 40-turn arm: {ev}",
    )


def r_ai_aliveness_C3(arms, ctx):
    need = [n for n in CMD_ARMS if n in arms]
    if not need:
        return _unmeasured("no CMD arms")
    ev = {}
    for n in need:
        hit = [
            l
            for _, l in _blocks_with(arms[n], "Britain")
            if re.search(
                r"captured by Britain|lands? at|landing|ashore|expedition", l, re.I
            )
        ]
        hit += [
            l
            for _, l in _blocks_with(arms[n], "Moore")
            + _blocks_with(arms[n], "Wellesley")
            + _blocks_with(arms[n], "Paget")
            if re.search(r"lands|landing|ashore|captured", l, re.I)
        ]
        ev[n] = hit[0][:90] if hit else "no landing"
    return _res(
        True,
        all(v != "no landing" for v in ev.values()),
        json.dumps(ev, ensure_ascii=False)[:500],
    )


def r_ai_aliveness_C6(arms, ctx):
    need = [n for n in CMD_ARMS if n in arms]
    if not need:
        return _unmeasured("no CMD arms")
    ev = {}
    ok = True
    for n in need:
        war_turns = _turns_at_war(arms[n])
        attacks = _attacks_by_turn(arms[n])
        visible = sum(1 for t in war_turns if attacks.get(t, 0) > 0)
        ratio = visible / len(war_turns) if war_turns else 0.0
        ev[n] = f"{visible}/{len(war_turns)}"
        ok = ok and ratio >= 0.5
    return _res(True, ok, f"turns with a visible AI attack over the turns at war: {ev}")


def _attacks_by_turn(arm: Arm) -> dict[int, int]:
    """Enemy-phase attack counts keyed by the turn whose end they close."""
    out = {}
    turn = 0
    for r in arm.records:
        if r.get("kind") == "turn":
            turn = int(r.get("turn") or turn)
        elif r.get("kind") == "enemy_phase":
            out[turn] = out.get(turn, 0) + int(r.get("attacks", 0) or 0)
    return out


def _turns_at_war(arm: Arm) -> list[int]:
    """The turns on which France stood in a war, read off the digest's own
    war and peace rows: the boot wars until a whole-war settlement or the
    league's dissolution ends them; a declaration or a formed league opens
    them again. (Step 3: the Armed Peace puts twenty quiet turns between
    two wars — reading "every turn up to the last attack" as war had
    counted the peace against the AI.)"""
    at_war = True
    out = []
    turn = 0
    seen = None
    for r in arm.records:
        if r.get("kind") == "turn":
            if seen is not None and at_war:
                out.append(seen)
            turn = int(r.get("turn") or turn)
            seen = turn
            continue
        if r.get("kind") not in ("rail", "dispatch_row", "campaign_log"):
            continue
        d = r.get("dtype") or ""
        if d in ("diplomatic_war_declared", "diplomatic_coalition_formed", "coalition_declared"):
            at_war = True
        elif d in ("settlement_summary", "diplomatic_coalition_dissolved", "coalition_dissolved"):
            at_war = False
    if seen is not None and at_war and seen not in out:
        out.append(seen)
    return out


# ═════════════════════════ AGENDAS ═════════════════════════
def r_agendas_F1(arms, ctx):
    return _suite_green(
        ctx["run_dir"],
        ["tests/test_nation_agendas.py", "tests/test_nation_agendas_formables.py"],
        "agenda + formables tests",
    )


def r_agendas_C1(arms, ctx):
    need = [
        n
        for n in (
            "CMD-H",
            "CMD-A",
            "CMD-M",
            "CMD-ULM",
            "VOLTE",
            "REACH-AAR",
            "REACH-GEVB",
        )
        if n in arms
    ]
    if not need:
        return _unmeasured("no 40-turn arms")
    ev = {n: _count_dtype(arms[n], "agenda_shift") for n in need}
    return _res(
        True, all(v >= 2 for v in ev.values()), f"agenda_shift rows per arm: {ev}"
    )


def r_agendas_C2(arms, ctx):
    s, runs = _aiv(ctx["run_dir"])
    if not runs:
        return _unmeasured("no AIV per-run records")
    opening = {}
    for k, v in runs.items():
        decks = (v.get("boot") or {}).get("decks") or {}
        if "Austria" in decks and decks["Austria"]:
            opening[k] = decks["Austria"][0]
    hist = [v for k, v in opening.items() if "historical" in k]
    ok = bool(hist) and any(v != hist[0] for k, v in opening.items())
    return _res(True, ok, f"Austria's opening design per seed: {opening}")


def r_agendas_C5(arms, ctx):
    """SF-AGD-1: on the AGD arm, a carve STATES its terms (a settlement table
    the player read carries a create_client clause naming its client and the
    provinces it takes) and the Proclamation card FIRES. The formables gate
    flipping in play (the fixture before Posen, the arm's first save after)
    is read off the saves as evidence."""
    if _need(arms, "AGD"):
        return _unmeasured("AGD did not run")
    arm = arms["AGD"]
    stated = [c for r in arm.kind("settlement_terms") for c in (r.get("carves") or [])
              if (c.get("client_display_name") or c.get("tag")) and c.get("provinces")]
    cards = [p for p in arm.kind("popup") if str(p.get("key")) == "nation_proclamation"]
    flip = ""
    try:
        from tools import _score_probes as P
        flip = P.agd_gate_flip(arm, ctx)
    except Exception as exc:  # pragma: no cover - evidence only
        flip = f"gate flip unread ({type(exc).__name__})"
    first = stated[0] if stated else {}
    return _res(
        True,
        bool(stated) and bool(cards),
        f"carve terms stated {len(stated)}x"
        + (f" ({first.get('client_display_name') or first.get('tag')} from "
           f"{first.get('from')}: {'/'.join(first.get('provinces') or [])})" if first else "")
        + f"; Proclamation cards {len(cards)}"
        + (f" ({cards[0].get('summary')})" if cards else "")
        + (f"; {flip}" if flip else ""),
    )


# ── probe dispatch ─────────────────────────────────────────────────────────
def _probe(name):
    def _reader(arms, ctx):
        try:
            from tools import _score_probes as P
        except Exception as exc:  # pragma: no cover
            return _unmeasured(f"tools/_score_probes.py could not be imported: {exc}")
        fn = getattr(P, name, None)
        if fn is None:
            return _unmeasured(f"probe {name} is not built")
        import contextlib
        import io

        try:
            with contextlib.redirect_stdout(io.StringIO()):
                out = fn(arms, ctx)
        except Exception as exc:
            return _unmeasured(
                f"probe {name} raised: {type(exc).__name__}: {str(exc)[:160]}"
            )
        return out

    return _reader


PROBES = {
    "ending.C3": "ending_c3_alarm_forecast",
    "ending.C6": "ending_c6_refuser_prices",
    "diplomacy.C1": "diplomacy_c1_fresh_peace_holds",
    "diplomacy.C2": "diplomacy_c2_ratification_label",
    "first_contact.C1": "first_contact_c1_hold_shrugs",
    "first_contact.C5": "first_contact_c5_today_orders",
    "economy.F2": "economy_f2_britain_net",
    "economy.C2": "economy_c2_bills_named",
    "economy.C3": "economy_c3_quote_equals_applied",
    "economy.C4": "economy_c4_priced_orders",
    "economy.C6": "economy_c6_affordable_purchase",
    "naval.C5": "naval_c5_ports_now_zero",
    "living_balance.C5": "living_balance_c5_front_page",
    "combat_legibility.C3": "combat_c3_capital_garrison",
    "marshal_drama.F1": "drama_f1_flagship_probe",
    "marshal_drama.C2": "drama_c2_trust_names_visible",
    "marshal_drama.C3": "drama_c3_no_repeated_line",
    "marshal_drama.C5": "drama_c5_expectation_before_erosion",
    "vassals.C2": "vassals_c2_petition_quote",
    "vassals.C3": "vassals_c3_client_not_left_at_war",
    "vassals.C5": "vassals_c5_client_capital_contested",
    "command.C3": "command_c3_hold_orders",
    "narration.C3": "narration_c3_near_miss_headline",
    "narration.C4": "narration_c4_intel_row",
    "narration.C5": "narration_c5_moniteur",
    "ai_aliveness.C4": "ai_c4_garrison_grind",
    "ai_aliveness.C5": "ai_c5_fortify_dither",
    "agendas.F2": "agendas_f2_formables_on_saves",
    "agendas.C3": "agendas_c3_gate_flips",
    "agendas.C4": "agendas_c4_tilsit",
}


def reader_for(pillar: str, item_id: str, kind: str):
    key = f"{pillar}.{item_id}"
    if kind == "EYES":
        return None
    if key in PROBES:
        return _probe(PROBES[key])
    fn = globals().get(f"r_{pillar}_{item_id}")
    return fn


# ── check ──────────────────────────────────────────────────────────────────
def load_checklist(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def census_by_pillar() -> dict:
    try:
        from tools import defect_census as C

        rows = C.collect()
        open_rows = [r for r in rows.values() if r["state"] in ("OPEN", "partial")]
        view = C.by_pillar(open_rows)
        view["counted_at"] = _dt.datetime.now().isoformat(timespec="minutes")
        view["open_total"] = len(open_rows)
        return view
    except Exception as exc:
        return {"error": f"census unavailable: {exc}", "pillars": {}, "untagged": []}


def cmd_check(args) -> int:
    run_dir = pathlib.Path(args.run).resolve()
    checklist = load_checklist(pathlib.Path(args.checklist))
    arms = load_arms(run_dir)
    eyes = (
        json.loads(pathlib.Path(args.eyes).read_text(encoding="utf-8"))
        if args.eyes
        else {}
    )
    ctx = {"run_dir": run_dir, "arms": arms}
    for key, script in (
        ("dl_script", "score_docked_lines.json"),
        ("typed_script", "typed_road.json"),
        ("hold_script", HOLD_SCRIPT),
    ):
        p = ROOT / SCRIPTS / script
        ctx[key] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    census = census_by_pillar()
    results = {
        "run": str(run_dir),
        "checklist_version": checklist.get("version"),
        "checked": _dt.datetime.now().isoformat(timespec="minutes"),
        "pillars": {},
    }
    scores = {}
    for pillar in checklist["pillars"]:
        key = pillar["key"]
        items_out = []
        for item in pillar["items"]:
            iid = item["id"]
            kind = item["kind"]
            if kind == "EYES":
                mark = eyes.get(f"{key}.{iid}")
                if mark is None:
                    out = _unmeasured("EYES: no mark given (--eyes)")
                else:
                    out = _res(
                        True,
                        bool(mark.get("pass"))
                        if isinstance(mark, dict)
                        else bool(mark),
                        (
                            mark.get("evidence", "")
                            if isinstance(mark, dict)
                            else "marked"
                        )
                        + " (EYES)",
                    )
            else:
                fn = reader_for(key, iid, kind)
                if fn is None:
                    out = _unmeasured(f"no reader for {key}.{iid}")
                else:
                    import contextlib
                    import io

                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            out = fn(arms, ctx)
                    except Exception as exc:
                        out = _unmeasured(
                            f"reader raised {type(exc).__name__}: {str(exc)[:160]}"
                        )
            items_out.append({"id": iid, "kind": kind, "text": item["text"], **out})
        open_p1 = (census.get("pillars", {}).get(key) or {}).get("p1", [])
        sc = pillar_score(items_out, open_p1)
        sc["open_p2"] = (census.get("pillars", {}).get(key) or {}).get("p2", 0)
        sc["target_ceilings"] = pillar["target_ceilings"]
        results["pillars"][key] = {
            "name": pillar["name"],
            "items": items_out,
            "score": sc,
        }
        scores[key] = sc
    results["directional"] = directional(scores)
    (run_dir / "checklist.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (run_dir / "scores.json").write_text(
        json.dumps(
            {
                "directional": results["directional"],
                "pillars": {
                    k: {"name": results["pillars"][k]["name"], **v}
                    for k, v in scores.items()
                },
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    (run_dir / "census_by_pillar.json").write_text(
        json.dumps(census, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    findings = pathlib.Path(args.findings) if args.findings else None
    fr = (
        json.loads(findings.read_text(encoding="utf-8"))
        if findings and findings.exists()
        else {
            "note": "no findings file given; a hand-played campaign supplies rows filed per 10 turns played (§4.4)",
            "hand": None,
            "driver": {"rows_filed": 0},
        }
    )
    (run_dir / "findings_rate.json").write_text(
        json.dumps(fr, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print_scores(results)
    return 0


def print_scores(results: dict) -> None:
    print(
        f"{'pillar':20} {'reading':11} {'meas':>4} {'ceil✓':>5} {'ceil✗':>5} {'floors':>7}  P1"
    )
    for key, p in results["pillars"].items():
        s = p["score"]
        print(
            f"{p['name']:20} {s['reading']:11} {s['measured']:>4} {s['ceilings_passed']:>5} {s['ceilings_failed']:>5} "
            f"{str(s['floors_passed']) + '/' + str(s['floors_passed'] + s['floors_failed']):>7}  {','.join(s['open_p1']) or '-'}"
        )
    d = results["directional"]
    print(f"\ndirectional {d['value']} over {d['over']}")
    for key, p in results["pillars"].items():
        for it in p["items"]:
            mark = "✓" if it["pass"] else ("✗" if it["measured"] else "·")
            print(f"  {key:18} {it['id']} {mark} {it['evidence'][:110]}")


# ── packet ─────────────────────────────────────────────────────────────────
PACKET_README = """# THE PANEL PACKET — read only what is in this folder

You are one of three blind scorers (SCORE_FINISH_SPEC.md §4.5). You have NOT
seen any previous score, and you must not look for one: do not open STATUS.md,
CLAUDE.md, SCORE_MANDATE_PLAN.md, the audit memos, prior runs or the git log.

In this folder:
- checklist.json — every item, its kind, whether it was measured, its mark and its evidence line;
- scores.json — the anchor score per pillar from the frozen rule (§4.4), and the directional;
- census_by_pillar.json — the open defect rows per pillar, with the P1s;
- findings_rate.json — rows filed per 10 turns played, beside the score (never subtracted);
- digests/ — the arms' digest.md files (one block per turn: the orders, the replies, the battles, the popups, the ledger, the dispatch);
- frames/ — the client frames and their index, when the client arm ran.

Your job, per pillar:
1. Mark each EYES item you can judge from the digests (pass / fail / cannot judge), citing a digest line.
2. Take the anchor score as given. Adjust it by −0.25, 0 or +0.25 for FEEL only, citing ONE digest line or frame.
3. Return JSON: {"pillar_key": {"anchor": x, "adjust": -0.25|0|0.25, "eyes": {"C2": {"pass": true, "cite": "..."}}, "cite": "one line", "flag": "optional: something a human should check"}}.
A flag never moves a score. The median and the spread of the three panels are what gets published.
"""


def cmd_packet(args) -> int:
    run_dir = pathlib.Path(args.run).resolve()
    pk = run_dir / "panel_packet"
    if pk.exists():
        shutil.rmtree(pk)
    (pk / "digests").mkdir(parents=True)
    for name in (
        "checklist.json",
        "scores.json",
        "census_by_pillar.json",
        "findings_rate.json",
    ):
        if (run_dir / name).exists():
            shutil.copy(run_dir / name, pk / name)
    for arm_dir in (
        sorted((run_dir / "arms").iterdir()) if (run_dir / "arms").exists() else []
    ):
        if (arm_dir / "digest.md").exists():
            shutil.copy(arm_dir / "digest.md", pk / "digests" / f"{arm_dir.name}.md")
    frames = run_dir / "frames"
    if frames.exists():
        shutil.copytree(frames, pk / "frames")
    (pk / "README.md").write_text(PACKET_README, encoding="utf-8")
    print(f"packet at {pk} ({len(list((pk / 'digests').iterdir()))} digests)")
    return 0


# ── compare ────────────────────────────────────────────────────────────────
def _items(results: dict) -> dict:
    out = {}
    for key, p in results["pillars"].items():
        for it in p["items"]:
            out[f"{key}.{it['id']}"] = it
    return out


def cmd_compare(args) -> int:
    base = pathlib.Path(args.base).resolve()
    run = pathlib.Path(args.run).resolve()
    a = json.loads((base / "checklist.json").read_text(encoding="utf-8"))
    b = json.loads((run / "checklist.json").read_text(encoding="utf-8"))
    pa = (
        json.loads((base / "panel.json").read_text(encoding="utf-8"))
        if (base / "panel.json").exists()
        else {}
    )
    pb = (
        json.loads((run / "panel.json").read_text(encoding="utf-8"))
        if (run / "panel.json").exists()
        else {}
    )
    ia, ib = _items(a), _items(b)
    lines = [f"# compare — {base.name} → {run.name}", "", "## Item flips", ""]
    flips = 0
    for k in sorted(set(ia) | set(ib)):
        x, y = ia.get(k, {}), ib.get(k, {})

        def st(i):
            return "·" if not i.get("measured") else ("✓" if i.get("pass") else "✗")

        if st(x) != st(y):
            flips += 1
            lines.append(f"- `{k}` {st(x)} → {st(y)} — {y.get('evidence', '')[:140]}")
    if flips == 0:
        lines.append("- no item flipped")
    lines += [
        "",
        "## Pillars",
        "",
        "| pillar | base | run | base median (spread) | run median (spread) | claim |",
        "|---|---|---|---|---|---|",
    ]
    for key in a["pillars"]:
        sa, sb = a["pillars"][key]["score"], b["pillars"].get(key, {}).get("score", {})
        ma, sp_a = _panel_median(pa, key)
        mb, sp_b = _panel_median(pb, key)
        moved = (
            ma is not None
            and mb is not None
            and abs(mb - ma) > max(sp_a or 0, sp_b or 0)
        )
        flipped_here = any(
            k.startswith(key + ".")
            and ia.get(k, {}).get("pass") != ib.get(k, {}).get("pass")
            for k in ib
        )
        claim = "MOVED" if (moved and flipped_here) else "held"
        lines.append(
            f"| {a['pillars'][key]['name']} | {sa.get('reading')} | {sb.get('reading')} | {ma} ({sp_a}) | {mb} ({sp_b}) | {claim} |"
        )
    lines += [
        "",
        f"directional: {a['directional']} → {b['directional']}",
        "",
        "A move is claimed only when an item flipped AND the median moved by more than the larger spread (§4.5).",
    ]
    (run / "compare.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


def _panel_median(panel: dict, key: str):
    vals = [
        p.get(key, {}).get("score")
        for p in (panel.get("panels") or [])
        if isinstance(p, dict)
        and isinstance(p.get(key), dict)
        and p[key].get("score") is not None
    ]
    if not vals:
        return None, None
    return round(statistics.median(vals), 2), round(max(vals) - min(vals), 2)


# ── main ───────────────────────────────────────────────────────────────────
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--tree", default="")
    r.add_argument("--jobs", type=int, default=3)
    r.add_argument("--only", action="append")
    r.add_argument("--skip", action="append")
    r.add_argument("--aiv-dir", default="")
    r.add_argument("--acceptance-n", type=int, default=10)
    r.add_argument("--godot", default="")
    c = sub.add_parser("check")
    c.add_argument("--run", required=True)
    c.add_argument("--checklist", default=str(CHECKLIST_DEFAULT))
    c.add_argument("--eyes", default="")
    c.add_argument("--findings", default="")
    p = sub.add_parser("packet")
    p.add_argument("--run", required=True)
    m = sub.add_parser("compare")
    m.add_argument("--base", required=True)
    m.add_argument("--run", required=True)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    return {
        "run": cmd_run,
        "check": cmd_check,
        "packet": cmd_packet,
        "compare": cmd_compare,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
