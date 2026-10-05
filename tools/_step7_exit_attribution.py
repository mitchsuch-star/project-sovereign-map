"""The Score Finish Step 7 exit's attribution arms (October 5, 2026).

The exit read the final tree (`e83be52a` + the exit's instrument fixes)
against the start reading on `bc93ffaf`. Seven items flipped. This tool
re-runs each flipped item's arms on this tree with one slice's levers DOWN
and reads them with the instrument's own readers, so every flip is
attributed by experiment rather than by argument.

    .venv/Scripts/python.exe tools/_step7_exit_attribution.py [--out DIR]

The arms take the final reading's own command lines (its `run.json`), so
the comparison is the arm with and without the lever. Measured on the exit
(the record `docs/audits/score_runs/2026_10_05_step7/attribution.md`):

  the field read (Step 7 slice 3, §6 row 16 — the user's ruling) down:
      combat C2, ui C4, AI C5, economy C1 and marshal drama F1 each read as
      they did on `bc93ffaf`;
  slice 10's levers down: nothing moves;
  §6 row 20 (slice 6) down: the volte arm's beat does not fire (diplomacy C3);
  first contact C4 needs BOTH slice 3b's build line and the field read down
      to read as on `bc93ffaf` — either alone names the purchase.
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
FINAL = ROOT / "tools" / "playtest_runs" / "score_2026_10_05_step7_final"
ARCHIVE = ROOT / "docs" / "audits" / "score_runs" / "2026_10_05_step7"

FIELD = ["backend.commands.combat_executor:THE_COORDINATION_IS_READ_ON_THE_FIELD=0",
         "backend.commands.combat_executor:THE_GATE_READS_THE_PREVIEWS_CONTEXT=0",
         "backend.commands.combat_executor:AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL=0"]
S10 = ["backend.ai.enemy_ai:THE_STAGNATION_COUNTS_A_CAPTURE=0",
       "backend.game_logic.diplomacy:A_NEW_WAR_HAS_A_PURPOSE=0"]
BUILD_LINE = ["backend.ai.counsel:THE_BUILD_LINE_NEEDS_NO_CORPS=0"]
ALLYS_WAR = ["backend.game_logic.emergent_designs:AN_ALLYS_WAR_IS_ITS_OWN=0"]
OVERFLOW = ["backend.models.dialogue_manager:THE_QUEUE_OVERFLOWS_INTO_THE_MAILBOX=0"]

JOBS = [
    ("LAW", "field_down", FIELD), ("LAW", "s10_down", S10),
    ("CMD-H", "field_down", FIELD), ("CMD-H", "s10_down", S10),
    ("FLAG", "field_down", FIELD), ("FLAG", "s10_down", S10),
    ("OP", "field_down", FIELD), ("OP", "overflow_down", OVERFLOW),
    ("FLD", "field_down", FIELD), ("CMD-A", "field_down", FIELD),
    ("CMD-M", "field_down", FIELD),
    ("DL", "buildline_down", BUILD_LINE), ("DL", "field_down", FIELD),
    ("DL", "both_down", BUILD_LINE + FIELD),
    ("VOLTE", "allyswar_down", ALLYS_WAR),
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
    cmd += _arm_args(run, arm)
    for lever in levers:
        cmd += ["--lever", lever]
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env["PYTHONUTF8"] = "1"
    with open(out / f"{name}.log", "w", encoding="utf-8") as fh:
        return name, subprocess.call(cmd, cwd=str(ROOT), stdout=fh,
                                     stderr=subprocess.STDOUT, env=env)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "tools" / "playtest_runs" / "step7_exit_attribution"))
    ap.add_argument("--jobs", type=int, default=3)
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    run_json = FINAL / "run.json" if (FINAL / "run.json").exists() else ARCHIVE / "run.json"
    run = json.loads(run_json.read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for name, rc in ex.map(lambda j: _run(out, run, *j), JOBS):
            print(name, rc, flush=True)

    sys.path.insert(0, str(ROOT / "tools"))
    import score_run as SR

    def arm(name):
        return SR.Arm(out / name)

    def petition_modals(a):
        return sum(1 for r in a.kind("popup") if r.get("key") == "marshal_petition")

    print("FLAG petition modals:", {t: petition_modals(arm(f"FLAG-{t}"))
                                    for t in ("field_down", "s10_down")})
    for t in ("field_down", "s10_down"):
        print(f"LAW {t}:", SR.reader_for("economy", "C1", "AUTO")(
            {"LAW": arm(f"LAW-{t}")}, {})["evidence"][:60])
        print(f"CMD-H {t}:", SR.reader_for("ai_aliveness", "C5", "AUTO")(
            {"CMD-H": arm(f"CMD-H-{t}")}, {})["evidence"][:120])
    c2 = {n: arm(f"{n}-field_down") for n in ("OP", "FLD", "CMD-H", "CMD-A", "CMD-M")}
    print("combat C2 field_down:", SR.r_combat_legibility_C2(c2, {})["evidence"])
    for t in ("field_down", "overflow_down"):
        print(f"ui C4 {t}:", SR.reader_for("ui_ux", "C4", "AUTO")(
            {"OP": arm(f"OP-{t}")}, {})["evidence"][:100])
    for t in ("buildline_down", "field_down", "both_down"):
        print(f"first contact C4 {t}:", SR.r_first_contact_C4(
            {"DL": arm(f"DL-{t}")}, {})["evidence"][:140])
    fn = SR.reader_for("diplomacy", "C3", "AUTO") or SR.reader_for("diplomacy", "C3", "PROBE")
    print("diplomacy C3 allyswar_down:", fn({"VOLTE": arm("VOLTE-allyswar_down")},
                                             {"run_dir": out})["evidence"][:100])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
