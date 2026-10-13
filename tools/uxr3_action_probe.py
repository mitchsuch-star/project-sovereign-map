"""UXR-3 "The action probe" — the runner (Pre-Deploy S11, October 13, 2026).

    .venv/Scripts/python.exe tools/uxr3_action_probe.py --payload-dir <dir> --out-dir <dir> \
        [--only <substr>[,<substr>...]] [--godot <path>]

The driven record behind R5 (Affordance) and R6 (Feedback) of
`docs/UX_CHECKLIST_V1.json`. It builds the probe's spec from the IQ-10
manifest through `iq10_run_captures.build_spec` (the same payloads, scenes,
entry methods and steps the frames were shot from), runs
`tools/uxr3_action_probe.gd` in ONE windowed engine parked past the desktop at
1920x1080 and Interface Scale 1.0, and writes `<out>/probe.json`: per surface,
every control of its live frame with its answer (VISIBLE / HANDOFF / SILENT /
NOT PRESSED / DISABLED), what changed, the API calls and the script signals.

The engine writes its result after every surface and a progress marker before
every press. If the engine dies mid-run (a crash, a quit no word warned of),
the runner records the control it was pressing as CRASHED, with the SCRIPT
ERROR lines of the log, and resumes after it. Every SCRIPT ERROR between two
`[UXR3] PRESS` markers is attributed to that press.

Rails: SOVEREIGN_PORT is pointed at an unused port (never the player's 8005);
the engine is the only one running (the caller's job: never beside a shoot).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPT = "../../tools/uxr3_action_probe.gd"
WINDOW = [1920, 1080]
SCALE = 1.0
HARNESS_PORT = "8999"
MAX_RELAUNCH = 40

sys.path.insert(0, str(REPO / "tools"))
import iq10_run_captures as R  # noqa: E402

_PRESS = re.compile(r"\[UXR3\] PRESS (\S+) (\d+)")
_BEGIN = re.compile(r"\[UXR3\] BEGIN (\S+)")


def build(shots: list[dict], payload_dir: pathlib.Path, work: pathlib.Path) -> dict:
    captures = R.load_manifest(payload_dir)
    spec_path, result_path = work / "probe_spec.json", work / "probe_result.json"
    spec, _index = R.build_spec(shots, captures, [SCALE], "probe", spec_path, result_path,
                                png_dir=work / "unused_png")
    spec["window"] = WINDOW
    spec["scale"] = SCALE
    spec["result"] = str(result_path)
    return spec


def run_engine(godot: str, spec: dict, work: pathlib.Path, n: int) -> tuple[int, pathlib.Path]:
    spec_path = work / f"probe_spec_{n}.json"
    spec_path.write_text(json.dumps(spec, indent=1), encoding="utf-8")
    log = work / f"probe_engine_{n}.log"
    env = dict(os.environ)
    env["UXR3_PROBE_SPEC"] = str(spec_path)
    env.pop("PYTHONIOENCODING", None)
    if env.get("SOVEREIGN_PORT", "") in ("", "8005"):
        env["SOVEREIGN_PORT"] = HARNESS_PORT
    args = [godot, "--audio-driver", "Dummy", "--windowed", "--resolution", f"{WINDOW[0]}x{WINDOW[1]}",
            "--position", "5200,20", "--log-file", str(log), "--path", str(PROJECT), "--script", SCRIPT]
    proc = subprocess.run(args, env=env, cwd=str(REPO), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=6 * 3600)
    return proc.returncode, log


def errors_by_press(log: pathlib.Path) -> dict:
    """{"shot#i": [SCRIPT ERROR lines]} and {"shot": [...]} for errors outside a press."""
    out: dict = {}
    if not log.exists():
        return out
    key = ""
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, ln in enumerate(lines):
        m = _PRESS.search(ln)
        if m:
            key = f"{m.group(1)}#{m.group(2)}"
            continue
        m = _BEGIN.search(ln)
        if m:
            key = m.group(1)
            continue
        if "SCRIPT ERROR" in ln:
            detail = ln.strip()
            if i + 1 < len(lines) and "at:" in lines[i + 1]:
                detail += " " + lines[i + 1].strip()
            out.setdefault(key or "(boot)", []).append(detail[:400])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--godot", default=os.environ.get("IQ10_GODOT", R.GODOT_DEFAULT))
    args = ap.parse_args(argv)
    work = pathlib.Path(args.out_dir)
    work.mkdir(parents=True, exist_ok=True)
    wanted = [s.strip().lower() for s in args.only.split(",") if s.strip()]
    shots = [s for s in R.SHOTS if not wanted or any(w in s["id"].lower() for w in wanted)]
    spec = build(shots, pathlib.Path(args.payload_dir), work)
    all_shots = list(spec["shots"])
    done: dict = {}
    script_errors: dict = {}
    crashes: list = []
    remaining = all_shots
    resume: dict = {}
    for n in range(MAX_RELAUNCH):
        spec["shots"] = remaining
        spec["resume"] = resume
        result_path = pathlib.Path(spec["result"])
        for p in (result_path, pathlib.Path(str(result_path) + ".progress.json")):
            if p.exists():
                p.unlink()
        code, log = run_engine(args.godot, spec, work, n)
        for k, v in errors_by_press(log).items():
            script_errors.setdefault(k, []).extend(v)
        result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {}
        for rec in result.get("results", []):
            done[rec["id"]] = rec
        if result.get("done"):
            break
        # the engine died: name the control it was pressing, resume after it
        progress_path = pathlib.Path(str(result_path) + ".progress.json")
        progress = json.loads(progress_path.read_text(encoding="utf-8")) if progress_path.exists() else {}
        left = [s for s in all_shots if s["id"] not in done]
        if not left:
            break
        crashed_shot = progress.get("shot") if progress.get("shot") == left[0]["id"] else left[0]["id"]
        crashed_control = int(progress.get("control", -1)) if progress.get("shot") == crashed_shot else -1
        crashes.append({"shot": crashed_shot, "control": crashed_control, "exit_code": code,
                        "log": str(log)})
        print(f"engine stopped (exit {code}) at {crashed_shot} control {crashed_control}; resuming")
        if crashed_control < 0:
            # it died opening the surface itself: record it unreached and move on
            done[crashed_shot] = {"id": crashed_shot, "reached": False, "controls": [],
                                  "errors": [f"the engine stopped opening this surface (exit {code})"]}
            left = left[1:]
            resume = {}
        else:
            resume = {"shot": crashed_shot, "skip_through": crashed_control}
        remaining = left
        if not remaining:
            break
    try:
        commit = subprocess.run(["git", "-C", str(PROJECT), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = ""
    ordered = {s["id"]: done.get(s["id"], {"id": s["id"], "reached": False, "controls": [],
                                           "errors": ["never probed"]}) for s in all_shots}
    for sid, rec in ordered.items():
        for c in rec.get("controls", []):
            errs = script_errors.get(f"{sid}#{c.get('i')}")
            if errs:
                c["script_errors"] = errs
        if script_errors.get(sid):
            rec["script_errors_open"] = script_errors[sid]
    out = {"tool": "tools/uxr3_action_probe.py", "client_commit": commit, "window": WINDOW,
           "scale": SCALE, "crashes": crashes, "shots": ordered}
    (work / "probe.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    counts: dict = {}
    for rec in ordered.values():
        for c in rec.get("controls", []):
            counts[c.get("result", "?")] = counts.get(c.get("result", "?"), 0) + 1
    print(f"probe: {len(ordered)} surfaces, {sum(1 for r in ordered.values() if r.get('reached'))} reached; "
          f"controls {counts}; crashes {len(crashes)}; script-error keys {len(script_errors)}")
    print(f"PROBE_JSON={work / 'probe.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
