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

WAR-ROOM MODE (Pre-Deploy S12 part 2, the R6 driven proofs):

    .venv/Scripts/python.exe tools/uxr3_action_probe.py --war-room \
        --payload-dir <dir> --out-dir <dir> [--port 8006] [--only <road ids>]

It starts a backend on --port (8006 by default, the next free port above it if
taken, never 8005) with its own save directory (`<out>/saves`) and the mock
parser, then presses each road of ROADS inside the real main.tscn against it
(`tools/uxr3_action_probe.gd`'s war-room mode) and writes `<out>/war_room.json`:
per road, the control pressed and what the war room's LIVE frame showed within
500 ms and 30 frames. A road whose press quits the game is proven by the
engine exiting cleanly after its progress marker: the window closed.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPT = "../../tools/uxr3_action_probe.gd"
WINDOW = [1920, 1080]
SCALE = 1.0
HARNESS_PORT = "8999"
MAX_RELAUNCH = 40

sys.path.insert(0, str(REPO / "tools"))
import iq10_run_captures as R  # noqa: E402

# The R6 roads the war-room mode proves: (road id, IQ-10 shot whose payload and
# entry open the surface, the control's match). One control per road: every
# control a road's match names answers by the same handler, so the road's
# citation (`docs/audits/uxr3_s12b/live_citations.json`) names the match.
ROADS = [
    ("envoys", "war_room_boot", {"path_endswith": "MailboxButton"}),
    ("pause_save", "war_room_pause_settings", {"text": "Save Game"}),
    ("pause_load", "war_room_pause_settings", {"text": "Load Game"}),
    ("pause_new_campaign", "war_room_pause_settings", {"text": "New Campaign"}),
    ("pause_main_menu", "war_room_pause_settings", {"text": "Main Menu"}),
    ("pause_quit", "war_room_pause_settings", {"text": "Quit to Desktop"}),
    ("menu_quit", "main_menu", {"text": "Quit to Desktop"}),
    ("fall_main_menu", "campaign_end_fall_funeral", {"text": "Main Menu"}),
    ("generals_order", "generals_boot", {"kind": "link", "meta_startswith": "order:"}),
    ("generals_reward", "generals_np_field", {"kind": "link", "meta_startswith": "reward:"}),
    ("diplo_assess", "diplo_boot_talleyrand", {"kind": "link", "meta_startswith": "talleyrand_assess"}),
    ("diplo_vassal", "diplo_boot_vassals", {"kind": "link", "meta_startswith": "vassal:"}),
    ("diplo_congress_court", "diplo_boot_congress", {"kind": "link", "meta_startswith": "congress_court:"}),
    ("ledger_law", "ledger_boot_laws", {"kind": "link", "meta_startswith": "do:"}),
    ("ledger_admiralty", "ledger_boot_admiralty", {"kind": "link", "meta_startswith": "do:"}),
    ("ledger_cancel", "ledger_orders_display", {"kind": "link", "meta_startswith": "cancel:"}),
    ("region_order", "region_paris", {"kind": "link", "meta_startswith": "order:"}),
    ("region_do", "region_paris", {"kind": "link", "meta_startswith": "do:"}),
    ("region_negotiate", "region_amsterdam", {"kind": "link", "meta_startswith": "negotiate:"}),
    ("enemy_view_field", "enemy_phase_t20", {"kind": "link", "meta_startswith": "diorama:"}),
    ("rail_recall", "rail_mission_court", {"kind": "button", "text": "Recall"}),
    ("topbar_cabinet", "top_bar_mission_court", {"path_endswith": "TalleyrandLabel"}),
]
WAR_ROOM_PORT = 8006

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


def _free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def start_backend(work: pathlib.Path, port: int) -> tuple[subprocess.Popen, int]:
    """A sandboxed backend (the Mode B rule): an unused port, never 8005, its
    own save directory, the mock parser, the historical seed."""
    while port == 8005 or not _free(port):
        port += 1
    saves = work / "saves"
    saves.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_SMOKE_START"):
        env.pop(key, None)
    env.update({"SOVEREIGN_PORT": str(port), "INK_IRON_SAVE_DIR": str(saves), "LLM_MODE": "mock",
                "SOVEREIGN_SEED": "historical", "SOVEREIGN_MAP": "europe", "DEBUG_MODE": "false",
                "PYTHONHASHSEED": "0"})
    py = REPO / ".venv" / "Scripts" / "python.exe"
    log = (work / "backend.log").open("w", encoding="utf-8")
    proc = subprocess.Popen([str(py) if py.exists() else sys.executable, "-m", "backend.main"],
                            cwd=str(REPO), env=env, stdout=log, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL)
    for _ in range(240):
        if proc.poll() is not None:
            break
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/test", timeout=2) as r:
                if r.status == 200:
                    return proc, port
        except Exception:
            time.sleep(0.5)
    proc.terminate()
    raise SystemExit(f"the sandboxed backend did not answer /test on {port} (see {work / 'backend.log'})")


def stop_backend(proc: subprocess.Popen) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()


def war_room(args, work: pathlib.Path) -> int:
    wanted = [s.strip() for s in args.only.split(",") if s.strip()]
    roads = [r for r in ROADS if not wanted or r[0] in wanted]
    by_id = {s["id"]: s for s in R.SHOTS}
    rows = []
    for road_id, sid, match in roads:
        row = dict(by_id[sid])
        rows.append(row)
    spec = build(rows, pathlib.Path(args.payload_dir), work)
    entries = []
    built = {s["id"]: s for s in spec["shots"]}
    for road_id, sid, match in roads:
        if sid not in built:
            continue
        entry = dict(built[sid])
        entry["id"] = road_id
        entry["base_id"] = sid
        entry["road"] = match
        entries.append(entry)
    spec["war_room"] = True
    backend, port = start_backend(work, args.port)
    done: dict = {}
    script_errors: dict = {}
    try:
        remaining = entries
        for n in range(MAX_RELAUNCH):
            if not remaining:
                break
            spec["shots"] = remaining
            spec["resume"] = {}
            result_path = pathlib.Path(spec["result"])
            progress_path = pathlib.Path(str(result_path) + ".progress.json")
            for p in (result_path, progress_path):
                if p.exists():
                    p.unlink()
            t0 = time.time()
            code, log = run_engine(args.godot, spec, work, n, port=str(port))
            exited_s = time.time()
            errs = errors_by_press(log)
            for k, v in errs.items():
                script_errors.setdefault(k, []).extend(v)
            result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {}
            for rec in result.get("results", []):
                done[rec["id"]] = rec
            if result.get("done"):
                break
            progress = json.loads(progress_path.read_text(encoding="utf-8")) if progress_path.exists() else {}
            left = [e for e in remaining if e["id"] not in done]
            if not left:
                break
            road = progress.get("shot") if progress.get("shot") == left[0]["id"] else left[0]["id"]
            entry = next(e for e in left if e["id"] == road)
            pressed = progress.get("shot") == road and int(progress.get("control", -1)) >= 0
            clean = code == 0 and not errs.get(f"{road}#{progress.get('control')}")
            if pressed and progress.get("quit") and clean:
                done[road] = {"id": road, "base_id": entry["base_id"], "scene": entry["scene"],
                              "road": entry["road"], "reached": True, "backend": f"127.0.0.1:{port}",
                              "controls": [{"i": int(progress["control"]), "kind": "button",
                                            "text": entry["road"].get("text", ""), "result": "VISIBLE",
                                            "method": "click",
                                            "changes": ["the engine exited cleanly (code 0) after the press: "
                                                        "the window closed"],
                                            "engine_exit": code,
                                            "seconds_after_launch": round(exited_s - t0, 1)}],
                              "errors": []}
            else:
                done[road] = {"id": road, "base_id": entry["base_id"], "scene": entry["scene"],
                              "road": entry["road"], "reached": pressed, "controls": [],
                              "errors": [f"the engine stopped (exit {code}) "
                                         + ("during the press" if pressed else "opening the surface")]}
            remaining = [e for e in left if e["id"] != road]
    finally:
        stop_backend(backend)
    try:
        commit = subprocess.run(["git", "-C", str(PROJECT), "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = ""
    ordered = {e["id"]: done.get(e["id"], {"id": e["id"], "reached": False, "controls": [],
                                           "errors": ["never probed"]}) for e in entries}
    for rid, rec in ordered.items():
        for c in rec.get("controls", []):
            errs = script_errors.get(f"{rid}#{c.get('i')}")
            if errs:
                c["script_errors"] = errs
    out = {"tool": "tools/uxr3_action_probe.py --war-room", "client_commit": commit, "window": WINDOW,
           "scale": SCALE, "backend": "a sandboxed backend (mock parser, its own saves) on 127.0.0.1:%d" % port,
           "roads": ordered,
           "saves_written": sorted(f.name for f in (work / "saves").iterdir()) if (work / "saves").is_dir() else []}
    (work / "war_room.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    answered = [rid for rid, rec in ordered.items()
                if any(c.get("result") == "VISIBLE" and not c.get("script_errors") for c in rec.get("controls", []))]
    print(f"war room: {len(answered)} of {len(ordered)} roads answer in the live frame")
    for rid, rec in ordered.items():
        cs = rec.get("controls") or [{}]
        print(f"  {rid}: {cs[0].get('result', 'UNREACHED')} {cs[0].get('changes', [])[:3]} {rec.get('errors', [])[:1]}")
    print(f"WAR_ROOM_JSON={work / 'war_room.json'}")
    return 0


def run_engine(godot: str, spec: dict, work: pathlib.Path, n: int,
               port: str = "") -> tuple[int, pathlib.Path]:
    spec_path = work / f"probe_spec_{n}.json"
    spec_path.write_text(json.dumps(spec, indent=1), encoding="utf-8")
    log = work / f"probe_engine_{n}.log"
    env = dict(os.environ)
    env["UXR3_PROBE_SPEC"] = str(spec_path)
    env.pop("PYTHONIOENCODING", None)
    if port:
        env["SOVEREIGN_PORT"] = port      # the war room's sandboxed backend
    elif env.get("SOVEREIGN_PORT", "") in ("", "8005"):
        env["SOVEREIGN_PORT"] = HARNESS_PORT
    assert env["SOVEREIGN_PORT"] != "8005", "never the player's 8005"
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
    ap.add_argument("--war-room", action="store_true")
    ap.add_argument("--port", type=int, default=WAR_ROOM_PORT)
    args = ap.parse_args(argv)
    work = pathlib.Path(args.out_dir)
    work.mkdir(parents=True, exist_ok=True)
    if args.war_room:
        return war_room(args, work)
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
