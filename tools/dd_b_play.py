"""DD-B "The fresh-eyes campaign" — the player's hands (Pre-Deploy S13,
Slice 1, October 14, 2026).

A player of DD-B sees exactly what a player sees and acts only as a player
can: one action at a time on the REAL client (`tools/dd_b_client.gd`) at
5120x1440, against a sandboxed backend.

    .venv/Scripts/python.exe tools/dd_b_play.py start --road conquest --out <run>
        Starts a sandboxed backend (`uxr3_action_probe.start_backend`: an
        unused port from 8006, never 8005, `<run>/saves`, the mock parser, the
        historical seed), then the ONE engine. Prints the title screen, then
        SUPERVISES: it stays up until the engine exits (run it in the
        background), then stops the backend and writes `<run>/run.json`.
    .venv/Scripts/python.exe tools/dd_b_play.py act --out <run> [--meant "<what you meant>"] "<action>"
        Writes `<run>/inbox/NNNN.json` and waits for the engine's state
        (120 s). Prints the view JPEG's path and a compact summary: the open
        surfaces and their lines, any popup's title and buttons, the command
        window's new lines, the turn. A typed line needs `--meant`: the
        family of order you meant (attack, move, hold, …, question, or
        "other: <your words>") and the marshal, if one ("attack Ney").
        Actions: type <text> | click <words> | click#N <words> |
        click_at <x> <y> | key <K> | scroll <x> <y> up|down <n> | look
    .venv/Scripts/python.exe tools/dd_b_play.py crop --out <run> --n N --rect X Y W H
        A JPEG crop of frame N's full PNG (logical px), for reading small text.
    .venv/Scripts/python.exe tools/dd_b_play.py row --out <run> --n N --severity P1|P2|P3 \
        --did "..." --expected "..." --saw "..."
        Files a confusion in `<run>/rows.json` against action N (its turn and
        frame are read off the state).
    .venv/Scripts/python.exe tools/dd_b_play.py stop --out <run>
        Quits the engine (the supervisor then stops the backend and writes
        `<run>/run.json`: the turn reached, the actions, the durations, the
        engine's SCRIPT ERROR lines).
    .venv/Scripts/python.exe tools/dd_b_play.py judge --out <run>
        Every typed line and its reply, classified by the ONE judge
        (`tools/_score_probes.py`'s regexes, read through
        `unrehearsed_census.classify_order`): `<run>/judge.json`. A `misread`
        or an `executed_when_refusal_meant` is a P1 row by itself.

Rails: never two engines (start refuses while any Godot runs); never the
player's 8005; the engine's UiSettings are in memory only.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
CLIENT = REPO / "tools" / "dd_b_client.gd"
GODOT_DEFAULT = (r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
                 r"\Godot_v4.4.1-stable_win64.exe")
WINDOW = "5120x1440"
PARKED = "5200,20"
ROADS = {
    "conquest": "win the war in the field; take Vienna",
    "diplomacy": "end the war at the table before fighting it out; make the peace or the alliances you need",
    "sea": "make the navy count: break the blockade, raise Ireland, or carry the war across the Channel",
}
ACT_TIMEOUT_S = 120
BOOT_TIMEOUT_S = 240
# The families a typed line may be MEANT as (the judge's ACTION_WORDS keys,
# plus a question and the free "other: …").
GENERIC_FAMILIES = ("attack", "move", "hold", "scout", "fortify", "drill", "retreat", "recruit",
                    "build", "repair", "garrison", "support", "pursue", "diplomacy", "declare_war",
                    "naval_build", "naval_posture", "naval_land", "end_turn", "question")
SCRIPT_ERROR_RX = re.compile(r"SCRIPT ERROR|Parse Error|Invalid call|Invalid access|Invalid get|"
                             r"Invalid set|Attempt to call|Nonexistent function", re.I)

sys.path.insert(0, str(REPO / "tools"))


# ── plumbing ────────────────────────────────────────────────────────────────

def _read(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: pathlib.Path, value) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def _godot_running() -> int:
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=30,
                             stdin=subprocess.DEVNULL).stdout
    except Exception:
        return 0
    return sum(1 for line in out.splitlines() if "godot" in line.lower())


def _engine_path(arg: str | None) -> str:
    for cand in (arg, os.environ.get("GODOT_BIN"), GODOT_DEFAULT):
        if cand and pathlib.Path(cand).is_file():
            return cand
    raise SystemExit("no Godot engine found (pass --godot)")


def _families() -> set:
    import _score_probes as judge
    return set(judge.ACTION_WORDS) | {"question"}


def _parse_meant(meant: str) -> dict:
    """'attack Ney' -> {action: attack, marshal: Ney}; 'question';
    'other: my words' -> {action: other, words: …}."""
    m = (meant or "").strip()
    if m.lower().startswith("other"):
        return {"action": "other", "marshal": "", "words": m.split(":", 1)[-1].strip()}
    parts = m.split(None, 1)
    fam = parts[0].lower().replace("-", "_") if parts else ""
    fam = {"declare": "declare_war", "endturn": "end_turn", "end": "end_turn"}.get(fam, fam)
    who = parts[1].strip() if len(parts) > 1 else ""
    if fam == "end_turn" and who.lower() in ("turn",):
        who = ""
    return {"action": fam, "marshal": who}


# ── start / supervise ───────────────────────────────────────────────────────

def cmd_start(args) -> int:
    import uxr3_action_probe as AP
    run = pathlib.Path(args.out).resolve()
    if (run / "state").is_dir() and any((run / "state").glob("*.json")):
        raise SystemExit(f"{run} already holds a run — choose a fresh --out")
    n = _godot_running()
    if n:
        raise SystemExit(f"refused: {n} Godot process(es) already running — never two engines at once")
    run.mkdir(parents=True, exist_ok=True)
    for sub in ("inbox", "frames", "state"):
        (run / sub).mkdir(exist_ok=True)
    godot = _engine_path(args.godot)
    backend, port = AP.start_backend(run, args.port)
    if port == 8005:
        AP.stop_backend(backend)
        raise SystemExit("refused: never the player's 8005")
    env = dict(os.environ, SOVEREIGN_PORT=str(port), DD_B_RUN=str(run))
    env.pop("PYTHONIOENCODING", None)
    log = (run / "engine.log").open("w", encoding="utf-8")
    t0 = time.time()
    engine = subprocess.Popen(
        [godot, "--audio-driver", "Dummy", "--windowed", "--resolution", WINDOW,
         "--position", PARKED, "--path", str(PROJECT), "--script", str(CLIENT)],
        cwd=str(PROJECT), env=env, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    meta = {"road": args.road, "brief": ROADS.get(args.road, ""), "port": port,
            "backend_pid": backend.pid, "engine_pid": engine.pid, "godot": godot,
            "started": _dt.datetime.now().isoformat(timespec="seconds"), "window": WINDOW}
    _write(run / "meta.json", meta)
    try:
        boot = run / "state" / "0000.json"
        while time.time() - t0 < BOOT_TIMEOUT_S and not boot.is_file() and engine.poll() is None:
            time.sleep(0.5)
        if boot.is_file():
            print(f"started: backend on {port} (pid {backend.pid}), engine pid {engine.pid}")
            print(summary(run, 0))
        else:
            print(f"the engine wrote no boot state (exit {engine.poll()}); see {run / 'engine.log'}")
        sys.stdout.flush()
        if args.no_supervise:
            return 0
        engine.wait()
    finally:
        if not args.no_supervise:
            _close(run, backend, engine, t0)
    return 0


def _close(run: pathlib.Path, backend, engine, t0: float) -> None:
    import uxr3_action_probe as AP
    if engine.poll() is None:
        engine.terminate()
        try:
            engine.wait(timeout=20)
        except subprocess.TimeoutExpired:
            engine.kill()
    AP.stop_backend(backend)
    _write(run / "run.json", run_record(run, time.time() - t0, engine.returncode))
    print(f"closed: {run / 'run.json'}")


def run_record(run: pathlib.Path, wall_s: float | None = None, exit_code=None) -> dict:
    states = sorted((run / "state").glob("[0-9][0-9][0-9][0-9].json"))
    actions = []
    turn = ""
    for p in states:
        s = _read(p)
        req = {}
        inbox = run / "inbox" / p.name
        if inbox.is_file():
            req = _read(inbox)
        if s.get("turn"):
            turn = s["turn"]
        actions.append({"n": s.get("n"), "action": s.get("action"), "meant": req.get("meant", ""),
                        "ok": s.get("ok"), "error": s.get("error", ""), "turn": s.get("turn", ""),
                        "durations_ms": s.get("durations_ms", {})})
    errors = []
    log = run / "engine.log"
    if log.is_file():
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if SCRIPT_ERROR_RX.search(line):
                errors.append(line.strip()[:400])
    meta = _read(run / "meta.json") if (run / "meta.json").is_file() else {}
    return {"road": meta.get("road"), "port": meta.get("port"), "turn_reached": turn,
            "turn_number": _turn_number(turn), "actions": actions, "n_actions": len(actions),
            "wall_s": round(wall_s, 1) if wall_s else None, "engine_exit": exit_code,
            "script_errors": errors, "n_script_errors": len(errors)}


def _turn_number(turn: str) -> int | None:
    m = re.search(r"Turn\s+(\d+)", turn or "", re.I)
    return int(m.group(1)) if m else None


# ── act ─────────────────────────────────────────────────────────────────────

def _next_n(run: pathlib.Path) -> int:
    nums = [int(p.stem) for p in (run / "inbox").glob("[0-9][0-9][0-9][0-9].json")]
    return (max(nums) + 1) if nums else 1


def _engine_alive(run: pathlib.Path) -> bool:
    if (run / "run.json").is_file():
        return False
    meta = run / "meta.json"
    if not meta.is_file():
        return False
    pid = int(_read(meta).get("engine_pid", 0))
    if pid <= 0:
        return False
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True,
                             timeout=30, stdin=subprocess.DEVNULL).stdout
    except Exception:
        return True
    return str(pid) in out


def cmd_act(args) -> int:
    run = pathlib.Path(args.out).resolve()
    if not (run / "meta.json").is_file():
        raise SystemExit(f"no run at {run} (start it first)")
    action = " ".join(args.action).strip()
    if not action:
        raise SystemExit("act wants an action")
    verb = action.split()[0].lower()
    meant = (args.meant or "").strip()
    if verb == "type":
        if not meant:
            raise SystemExit("a typed line needs --meant: what you meant, as one of "
                             + ", ".join(GENERIC_FAMILIES)
                             + ", or \"other: <your words>\" — with the marshal if one "
                             "(e.g. --meant \"attack Ney\")")
        fam = _parse_meant(meant)["action"]
        if fam not in _families() and fam != "other":
            raise SystemExit(f"--meant: unknown family {fam!r}; use one of "
                             + ", ".join(GENERIC_FAMILIES) + ", or \"other: <your words>\"")
    n = _next_n(run)
    prev = run / "state" / f"{n - 1:04d}.json"
    t0 = time.time()
    while n > 1 and not prev.is_file() and time.time() - t0 < ACT_TIMEOUT_S:
        if not _engine_alive(run):
            break
        time.sleep(0.25)
    _write(run / "inbox" / f"{n:04d}.json",
           {"n": n, "action": action, "meant": meant,
            "written": _dt.datetime.now().isoformat(timespec="seconds")})
    state = run / "state" / f"{n:04d}.json"
    t0 = time.time()
    while not state.is_file():
        if time.time() - t0 > ACT_TIMEOUT_S:
            print(f"#{n:04d} {action}: no state after {ACT_TIMEOUT_S} s — the game is still working. "
                  f"Run `act --out {args.out} look` to wait for it and see the screen.")
            return 1
        if not _engine_alive(run) and not state.is_file():
            time.sleep(1.0)
            if not state.is_file():
                print(f"#{n:04d} {action}: THE GAME IS GONE (the engine exited). "
                      f"Last lines of the engine log:\n" + _log_tail(run, 25))
                return 2
        time.sleep(0.2)
    s = _read(state)
    with (run / "actions.log").open("a", encoding="utf-8", newline="\n") as f:
        f.write("\t".join([f"{n:04d}", _dt.datetime.now().isoformat(timespec="seconds"),
                           f"{time.time() - t0:.1f}s", action, meant,
                           "ok" if s.get("ok") else "ERROR: " + str(s.get("error", ""))]) + "\n")
    print(summary(run, n))
    return 0


def _log_tail(run: pathlib.Path, k: int) -> str:
    log = run / "engine.log"
    if not log.is_file():
        return "(no engine log)"
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-k:])


def _new_script_errors(run: pathlib.Path) -> list:
    log = run / "engine.log"
    mark = run / "engine_log_offset.txt"
    if not log.is_file():
        return []
    start = int(mark.read_text()) if mark.is_file() else 0
    data = log.read_bytes()
    mark.write_text(str(len(data)))
    fresh = data[start:].decode("utf-8", errors="replace").splitlines()
    return [ln.strip()[:300] for ln in fresh if SCRIPT_ERROR_RX.search(ln)]


# ── the summary ─────────────────────────────────────────────────────────────

def _sig(sf: dict) -> str:
    return json.dumps([sf.get("lines", []), [(b.get("text"), b.get("disabled")) for b in sf.get("buttons", [])]],
                      ensure_ascii=False)


def _centre(rect) -> str:
    return f"({int(rect[0] + rect[2] / 2)},{int(rect[1] + rect[3] / 2)})"


def _button_label(b: dict) -> str:
    text = (b.get("text") or "").replace("\n", " ").strip()
    kind = b.get("kind")
    if kind == "slider":
        r = b["rect"]
        return (f"[slider {b.get('value')} of {b.get('range')}, track x {int(r[0])}..{int(r[0] + r[2])}"
                f" at y {int(r[1] + r[3] / 2)}]")
    if not text:
        text = "icon" + (f": {b['tooltip'][:60]}" if b.get("tooltip") else "") + f" @{_centre(b['rect'])}"
    if kind == "link":
        out = f"<{text}>"
    elif kind == "chip":
        out = "{" + text + "}"
    else:
        out = f"[{text}]"
    if b.get("disabled"):
        out += "(disabled" + (f": {b['tooltip'][:90]}" if b.get("tooltip") else "") + ")"
    if b.get("toggled") is True:
        out += "(on)"
    return out


def summary(run: pathlib.Path, n: int, width: int = 9000) -> str:
    s = _read(run / "state" / f"{n:04d}.json")
    prev = None
    if n > 0 and (run / "state" / f"{n - 1:04d}.json").is_file():
        prev = _read(run / "state" / f"{n - 1:04d}.json")
    prev_sigs = {}
    if prev:
        for sf in prev.get("surfaces", []):
            prev_sigs[(sf["name"], sf["layer"])] = _sig(sf)
    out = []
    head = f"#{n:04d}  {s.get('action', '')}  ->  " + ("ok" if s.get("ok") else "ERROR: " + str(s.get("error", "")))
    out.append(head)
    if s.get("note"):
        out.append(f"  ({s['note']})")
    if s.get("candidates"):
        out.append("  candidates: " + " | ".join(
            f"#{i + 1} {_button_label(c)} on {c.get('surface')} @{_centre(c['rect'])}"
            for i, c in enumerate(s["candidates"][:20])))
    f = s.get("factor", {})
    out.append(f"view: {run / s.get('view', '')}   (a view-JPEG pixel x {f.get('logical_per_view_px', '?')} "
               f"= logical px; screen {f.get('logical_size')} logical)")
    cl = s.get("command_line") or {}
    line = f"turn: {s.get('turn', '-')}"
    if cl:
        line += f"   command line: {cl.get('text', '')!r}" + (" (focused)" if cl.get("focused") else "") + \
                ("" if cl.get("editable", True) else " (disabled)")
    out.append(line)
    o = s.get("open", {})
    out.append("open: " + ", ".join(
        [f"screens={o.get('screens', [])}", f"pinned={o.get('pinned') or '-'}",
         f"popups={o.get('popups', [])}", f"region_panel={'yes' if o.get('region_panel') else 'no'}"]
        + ([f"other={o.get('other')}"] if o.get("other") else [])))
    reply = s.get("reply")
    if reply:
        out.append("reply: " + ("ok " if reply.get("success") else "") + str(reply.get("message", ""))[:1500])
    for sf in s.get("surfaces", []):
        key = (sf["name"], sf["layer"])
        tag = f"── {sf['name']} (layer {sf['layer']})" + ("" if sf.get("above_floor", True) else " [under a modal]")
        if prev is not None and prev_sigs.get(key) == _sig(sf):
            out.append(tag + ": unchanged")
            continue
        out.append(tag + " ──")
        budget = 2600
        for ln in sf.get("lines", []):
            ln = ln.replace("\n", " / ")
            if len(ln) > 400:
                ln = ln[:400] + " …"
            if budget - len(ln) < 0:
                out.append("   … (more in the state file)")
                break
            budget -= len(ln)
            out.append("   " + ln)
        if sf.get("buttons"):
            labels = [_button_label(b) for b in sf["buttons"]]
            text = "  ".join(labels)
            if len(text) > 1800:
                text = text[:1800] + " …"
            out.append("   controls: " + text)
    new = s.get("terminal_new") or []
    if new:
        out.append("── command window, new lines ──")
        for ln in new[-40:]:
            out.append("   " + ln[:600])
    elif s.get("terminal_tail"):
        out.append("── command window, last lines ──")
        for ln in s["terminal_tail"][-4:]:
            out.append("   " + ln[:300])
    m = s.get("map") or []
    pm = (prev or {}).get("map") or []
    if m:
        if prev is not None and [r["text"] for r in m] == [r["text"] for r in pm]:
            out.append(f"map: unchanged ({len(m)} labels)")
        else:
            places = [r for r in m if str(r.get("kind", "")).startswith("place")]
            pieces = [r for r in m if not str(r.get("kind", "")).startswith("place")]
            if places:
                out.append("map names: " + "  ".join(f"{r['text']}{_centre(r['rect'])}" for r in places[:90]))
            if pieces:
                out.append("map pieces: " + "  ".join(f"{r['text']}{_centre(r['rect'])}" for r in pieces[:60]))
    errs = _new_script_errors(run)
    if errs:
        out.append(f"engine: {len(errs)} new SCRIPT ERROR line(s): " + " || ".join(errs[:3]))
    text = "\n".join(out)
    if len(text) > width:
        text = text[:width] + "\n… (the rest is in " + str(run / "state" / f"{n:04d}.json") + ")"
    return text


# ── crop / row ──────────────────────────────────────────────────────────────

def cmd_crop(args) -> int:
    from PIL import Image
    run = pathlib.Path(args.out).resolve()
    s = _read(run / "state" / f"{args.n:04d}.json")
    k = float(s.get("factor", {}).get("physical_per_logical", 1.0))
    x, y, w, h = args.rect
    img = Image.open(run / "frames" / f"{args.n:04d}.png").convert("RGB")
    box = (int(x * k), int(y * k), int((x + w) * k), int((y + h) * k))
    crops = run / "crops"
    crops.mkdir(exist_ok=True)
    path = crops / f"{args.n:04d}_{int(x)}_{int(y)}_{int(w)}x{int(h)}.jpg"
    img.crop(box).save(path, quality=90)
    print(path)
    return 0


def cmd_row(args) -> int:
    run = pathlib.Path(args.out).resolve()
    st = run / "state" / f"{args.n:04d}.json"
    if not st.is_file():
        raise SystemExit(f"no action {args.n} in {run}")
    s = _read(st)
    rows_path = run / "rows.json"
    rows = _read(rows_path) if rows_path.is_file() else []
    row = {"id": len(rows) + 1, "source": "player", "turn": s.get("turn", ""),
           "turn_number": _turn_number(s.get("turn", "")), "action": args.n,
           "action_text": s.get("action", ""), "frame": s.get("view", ""),
           "did": args.did, "expected": args.expected, "saw": args.saw, "severity": args.severity}
    rows.append(row)
    _write(rows_path, rows)
    print(f"row {row['id']} filed ({args.severity}) against #{args.n:04d}")
    return 0


# ── stop ────────────────────────────────────────────────────────────────────

def cmd_stop(args) -> int:
    run = pathlib.Path(args.out).resolve()
    if (run / "run.json").is_file():
        print(f"already closed: {run / 'run.json'}")
        return 0
    if _engine_alive(run):
        n = _next_n(run)
        _write(run / "inbox" / f"{n:04d}.json", {"n": n, "action": "quit", "meant": ""})
    t0 = time.time()
    while not (run / "run.json").is_file() and time.time() - t0 < 120:
        time.sleep(0.5)
    if not (run / "run.json").is_file():
        # No supervisor (a --no-supervise start): close by hand.
        import uxr3_action_probe as AP  # noqa: F401
        meta = _read(run / "meta.json")
        for pid in (meta.get("engine_pid"), meta.get("backend_pid")):
            if pid:
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True,
                               stdin=subprocess.DEVNULL)
        _write(run / "run.json", run_record(run))
    print(json.dumps({k: v for k, v in _read(run / "run.json").items() if k != "actions"}, indent=1))
    return 0


# ── the judge ───────────────────────────────────────────────────────────────

def judge_run(run: pathlib.Path) -> dict:
    import unrehearsed_census as C
    rows = []
    for st in sorted((run / "state").glob("[0-9][0-9][0-9][0-9].json")):
        s = _read(st)
        action = str(s.get("action", ""))
        if not action.lower().startswith("type "):
            continue
        inbox = run / "inbox" / st.name
        req = _read(inbox) if inbox.is_file() else {}
        meant = _parse_meant(req.get("meant", ""))
        reply = s.get("reply")
        if not reply:
            reply = {"message": "\n".join(s.get("terminal_new") or []), "success": None}
        if meant["action"] == "question":
            cls = C.classify_question(reply)
        elif meant["action"] == "other":
            cls = "unjudged_other"
        else:
            cls = C.classify_order({"action": meant["action"], "marshal": meant["marshal"]}, reply)
        rows.append({"n": s.get("n"), "turn": s.get("turn", ""), "line": action[5:],
                     "meant": req.get("meant", ""), "class": cls,
                     "success": reply.get("success"), "reply": str(reply.get("message", ""))[:600]})
    counts: dict = {}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    p1 = [r for r in rows if r["class"] in C.PROXY_CLASSES]
    return {"lines": len(rows), "classes": counts, "p1": p1, "rows": rows}


def cmd_judge(args) -> int:
    run = pathlib.Path(args.out).resolve()
    record = judge_run(run)
    _write(run / "judge.json", record)
    print(json.dumps({"lines": record["lines"], "classes": record["classes"],
                      "p1": [(r["n"], r["line"], r["class"]) for r in record["p1"]]}, indent=1,
                     ensure_ascii=False))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start")
    p.add_argument("--road", required=True, choices=sorted(ROADS))
    p.add_argument("--out", required=True)
    p.add_argument("--port", type=int, default=8006)
    p.add_argument("--godot")
    p.add_argument("--no-supervise", action="store_true", help="return after the boot (tests)")
    p.set_defaults(fn=cmd_start)
    p = sub.add_parser("act")
    p.add_argument("--out", required=True)
    p.add_argument("--meant", default="")
    p.add_argument("action", nargs=argparse.REMAINDER)
    p.set_defaults(fn=cmd_act)
    p = sub.add_parser("crop")
    p.add_argument("--out", required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--rect", type=float, nargs=4, required=True, metavar=("X", "Y", "W", "H"))
    p.set_defaults(fn=cmd_crop)
    p = sub.add_parser("row")
    p.add_argument("--out", required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--severity", required=True, choices=["P1", "P2", "P3"])
    p.add_argument("--did", required=True)
    p.add_argument("--expected", required=True)
    p.add_argument("--saw", required=True)
    p.set_defaults(fn=cmd_row)
    p = sub.add_parser("stop")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_stop)
    p = sub.add_parser("judge")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_judge)
    p = sub.add_parser("summary")
    p.add_argument("--out", required=True)
    p.add_argument("--n", type=int, required=True)
    p.set_defaults(fn=lambda a: print(summary(pathlib.Path(a.out).resolve(), a.n)) or 0)
    args = ap.parse_args(argv)
    return int(args.fn(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
