"""The economy audit's exit attribution arms (October 5, 2026).

The audit's reading (`docs/audits/score_runs/2026_10_05_econ_audit/`) was
compared with the final reading of the Score Finish
(`2026_10_05_sfr`). This tool re-runs each flipped item's arms on this tree
with one group of the audit's levers DOWN and reads them with the
instrument's own readers, so every flip is attributed by experiment.

    .venv/Scripts/python.exe tools/_econ_audit_exit_attribution.py [--out DIR] [--jobs N]

The arms take the reading's own command lines (its `run.json`). The record
is `docs/audits/score_runs/2026_10_05_econ_audit/attribution.md`.
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
PY = str(ROOT / ".venv" / "Scripts" / "python.exe") if os.name == "nt" else sys.executable
READING = ROOT / "docs" / "audits" / "score_runs" / "2026_10_05_econ_audit"

ARMS_UP = "backend.ai.enemy_ai:THE_COURT_ARMS_WITH_ITS_PURSE=0"
TOWERS = "backend.ai.enemy_ai:THE_AI_BUILDS_NO_WATCHTOWERS=0"
LEAGUE = ["backend.game_logic.coalition:THE_LEAGUE_DECLARES_IN_ITS_OWN_RIGHT=0",
          "backend.game_logic.coalition:A_FAILED_DECLARATION_IS_NOT_A_MEMBER=0"]
NOTE = "backend.game_logic.ledger:THE_NET_SAYS_WHY_IT_MOVED=0"
ALL = [
    ARMS_UP, TOWERS, NOTE, *LEAGUE,
    "backend.game_logic.coalition:A_SUBSIDY_PAYS_A_COURT_THAT_FIGHTS=0",
    "backend.game_logic.instruments:THE_SUBSIDIES_ARE_ON_THE_BOOKS=0",
    "backend.game_logic.diplomacy:A_PEACE_EARNS_NO_TRADE=0",
    "backend.game_logic.diplomacy:THE_DEAD_DO_NOT_TRADE=0",
    "backend.game_logic.diplomacy:THE_SYSTEM_CHARGES_ONLY_THE_TRADE_EARNED=0",
    "backend.game_logic.ledger:THE_VASSAL_PAYS_ON_ITS_OWN_BOOKS=0",
    "backend.game_logic.contingent:THE_SATELLITE_PAYS_ON_ITS_OWN_BILL=0",
    "backend.game_logic.war_council:THE_BEAT_READS_THE_MORNINGS_CHEST=0",
    "backend.models.world_state:ARREARS_ARE_REMEMBERED=0",
    "backend.models.world_state:A_MARKET_PAYS_ITS_OWN_KEEP=0",
    "backend.ai.counsel:THE_COUNSEL_NAMES_THE_LAW=0",
    "backend.game_logic.jealousy:THE_TOP_RUNG_PROMISES_NOTHING_HIGHER=0",
]

JOBS = [
    ("CMD-H", "all_down", ALL), ("CMD-H", "arms_down", [ARMS_UP]),
    ("CMD-H", "league_down", LEAGUE), ("CMD-H", "note_down", [NOTE]),
    ("CMD-H", "towers_down", [TOWERS]),
    ("CMD-A", "all_down", ALL), ("CMD-A", "arms_down", [ARMS_UP]),
    ("CMD-A", "league_down", LEAGUE),
    ("CMD-M", "all_down", ALL), ("CMD-M", "arms_down", [ARMS_UP]),
    ("CMD-M", "league_down", LEAGUE),
    ("FLAG", "all_down", ALL), ("FLAG", "arms_down", [ARMS_UP]),
    ("NAV1T-H", "all_down", ALL), ("NAV1T-H", "arms_down", [ARMS_UP]),
]


def _arm_args(run: dict, arm: str) -> list:
    cmd = list(run["arms"][arm]["cmd"])
    if arm == "FLAG":
        cmd = cmd[cmd.index("--") + 1:]
    out, skip = [], 0
    for tok in cmd:
        if skip:
            skip -= 1
            continue
        if tok in ("--name", "--out"):
            skip = 1
            continue
        if tok == "--fresh":
            continue
        out.append(tok)
    return out


def _run(out: pathlib.Path, run: dict, arm: str, tag: str, levers: list):
    name = f"{arm}-{tag}"
    cmd = [PY, "tools/playtest_driver.py", "--name", name, "--fresh", "--out", str(out)]
    if arm != "FLAG" and "--llm" not in _arm_args(run, arm):
        cmd += ["--llm", "mock"]
    cmd += _arm_args(run, arm)
    for lever in levers:
        cmd += ["--lever", lever]
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env["PYTHONUTF8"] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["LLM_MODE"] = "mock"
    env["INK_IRON_SAVE_DIR"] = str(out / "_saves")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED"):
        env.pop(key, None)
    with open(out / f"{name}.log", "w", encoding="utf-8") as fh:
        return name, subprocess.call(cmd, cwd=str(ROOT), stdout=fh,
                                     stderr=subprocess.STDOUT, env=env)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "tools" / "playtest_runs" / "econ_audit_attribution"))
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    run = json.loads((READING / "run.json").read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for name, rc in ex.map(lambda j: _run(out, run, *j), JOBS):
            print(name, rc, flush=True)

    sys.path.insert(0, str(ROOT / "tools"))
    import score_run as SR

    def arm(name):
        return SR.Arm(out / name)

    lines = ["# The economy audit's exit attribution (October 5, 2026)", "",
             "Each flipped item, read on this tree with one group of the audit's levers DOWN "
             "(`tools/_econ_audit_exit_attribution.py`; the reading's own command lines).", ""]

    def say(text):
        print(text, flush=True)
        lines.append(f"- {text}")

    for tag in ("all_down", "arms_down", "league_down"):
        cmd = {n: arm(f"{n}-{tag}") for n in ("CMD-H", "CMD-A", "CMD-M")}
        say(f"living balance C4 [{tag}]: " + SR.r_living_balance_C4(cmd, {})["evidence"][:220])
        fn = SR.reader_for("living_balance", "C5", "PROBE")
        say(f"living balance C5 [{tag}]: " + fn(cmd, {"run_dir": out})["evidence"][:220])
        fn = SR.reader_for("ai_aliveness", "C6", "AUTO")
        say(f"AI aliveness C6 [{tag}]: " + fn(cmd, {})["evidence"][:160])
        fn = SR.reader_for("ai_aliveness", "C1", "AUTO")
        say(f"AI aliveness C1 [{tag}]: " + fn(cmd, {})["evidence"][:160])
        fn = SR.reader_for("ai_aliveness", "C5", "PROBE")
        say(f"AI aliveness C5 [{tag}]: " + fn(cmd, {})["evidence"][:160])
        say(f"living balance F1 [{tag}]: " + SR.r_living_balance_F1(cmd, {})["evidence"][:160])
    for tag in ("note_down", "towers_down"):
        cmdh = {"CMD-H": arm(f"CMD-H-{tag}")}
        fn = SR.reader_for("economy", "C2", "PROBE")
        say(f"economy C2 [{tag}]: " + fn(cmdh, {})["evidence"][:200])
    cmdh = {"CMD-H": arm("CMD-H-towers_down")}
    fn = SR.reader_for("ai_aliveness", "C1", "AUTO")
    say("AI aliveness C1 [towers_down, CMD-H]: " + fn(cmdh, {})["evidence"][:160])
    for tag in ("all_down", "arms_down"):
        a = arm(f"FLAG-{tag}")
        modals = sum(1 for r in a.kind("popup") if r.get("key") == "marshal_petition")
        say(f"marshal drama F1 [{tag}]: FLAG petition modals {modals}")
        n = arm(f"NAV1T-H-{tag}")
        say(f"NAV1T-H [{tag}]: status {n.status}")
    (out / "attribution.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
