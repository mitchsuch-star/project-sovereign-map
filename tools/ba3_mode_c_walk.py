"""Row BA, BA-3 — the day's points pressed in the real client: the runner
(`docs/BATTLE_DIORAMA_SPEC.md` §15.14; November 15, 2026) — modeled on
tools/ba2_mode_c_walk.py.

STATUS: WRITTEN, NOT RUN in a window. Its seed hunt (`--hunt-only`) is pure
Python and runs anywhere; the windowed engine (`tools/ba3_mode_c_walk.gd`)
needs a real Godot window, so the lead session runs it once on the final tree.

    .venv/Scripts/python.exe tools/ba3_mode_c_walk.py --hunt-only [--board ulm|massena|defence|all]
    .venv/Scripts/python.exe tools/ba3_mode_c_walk.py --out <run> [--port 8006] [--godot PATH]
                                                      [--board ulm|massena|defence|all (both = all)]
                                                      [--seed ba3-walk-07] [--export <audit dir>]

Three boards, three walks: `ulm` (the real opening: the panel at rest, the Guard),
`massena` (an attack day: the province panel's chip, the lead's press, "Leave it
to ..."), `defence` (the enemy opens a great battle in his phase: End Turn, the
enemy phase's dialog, the rail's notice "Take the field", "digs in", "Fall back").

The campaign is the 1805 scenario with two corps moved to a great-battle board
(`write_scenario`, `SOVEREIGN_SCENARIO`); see the board's note in the source.

A day exists only in a campaign the game server holds, and a served campaign
on a ROLLED seed fights its battles with the campaign's own dice (WS-11), so a
seed names the battle. The hunt plays the walk's three server calls in-process
(a fresh world on the seed, `Massena, attack ArchdukeCharles`, the lead's press, then
`POST /battle_day/word leave_it`) through the real FastAPI app until one seed
leaves a day hanging that stays open through the press, takes it with no
marshal's question and no action spent, and then lets the lead be left to it.
The sandboxed backend is then started on that seed (the port asked for or the
next free one, never 8005; `<run>/saves` as its save directory; the mock
parser) and the engine walks the same road through the REAL client: the attack
card's Send, the day's panel at rest, the "Massena presses" chip, the "Leave it to
Massena" chip. After the engine ends the runner asks the live backend what it
holds (`GET /battle_day`) and writes `<run>/run.json`.

Rails: never two engines (refused while any Godot runs); the player's 8005 is
never touched. Exit 0 only when the engine ended cleanly, no script error was
logged and every step of the walk held. `--export` copies the frames,
`walk.json` and `run.json` to the named audit folder (none by default).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
PROJECT = REPO / "godot-client" / "project-sovereign"
WALK = REPO / "tools" / "ba3_mode_c_walk.gd"
GODOT_DEFAULT = (r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
                 r"\Godot_v4.4.1-stable_win64.exe")
SCRIPT_ERROR_RX = re.compile(r"SCRIPT ERROR|Parse Error|Invalid call|Invalid access|Invalid get|"
                             r"Invalid set|Attempt to call|Nonexistent function", re.I)
ENGINE_ERROR_RX = re.compile(r"^\s*ERROR:", re.M)
# The board. Round 2 (the server's "a road is a road to the rear"): on the REAL
# 1805 opening Mack, surrounded at Ulm, no longer slips away into France — he
# digs in or stands and the day opens and stays open (measured: 18 of 40 seeds,
# thirteen chips, his_road false). But the lead's press then DECIDES the day
# (`ended: decided`, measured on every hanging seed of 8) because Mack is dug in
# and surrounded: the walk's second step ("Leave it to ...") would have no day.
# So the live walk keeps the two-corps board (a scenario copy: Masséna in the
# Tyrol, the Archduke Charles in Carniola; five chips; the press leaves the day
# open). `--board ulm` runs the opening board for the day's panel and the press
# only (its hunt asks for the whole road and so finds no seed: use `--seed`).
#
# The `defence` board (a great battle the ENEMY opens in his phase, walked at
# dawn): the same two corps, but the lead is ALONE in the Tyrol and the Archduke
# Charles, in Carniola beside him, is the one who attacks when the player presses
# End Turn. What the AI needs to attack (`EnemyAI.the_days_word`'s sibling, P4 in
# enemy_ai.py: ratio = his combined strength / the defenders' strength against his
# temper's bar, `ATTACK_THRESHOLDS` x its mood `MOOD_VARIANCE`): cautious 1.3 (1.17
# - 1.43), literal 1.0, aggressive 0.7. Charles is CAUTIOUS (54,000 against
# Masséna's 42,000 = 1.29: the edge of his bar), so the board's first tuning raises
# his corps to 64,000 (ratio 1.52, over the top of his bar) and a second falls back
# to an aggressive Charles at his own 54,000 (bar 0.595 - 0.805). The hunt tries
# the tunings in order and keeps the first (tuning, seed) whose phase leaves the day
# the brief describes; the tuning is written into run.json.
BOARDS = {"ulm": ("Ney", "Mack", "Swabia"),
          "massena": ("Massena", "ArchdukeCharles", "Carniola"),
          "defence": ("Massena", "ArchdukeCharles", "Tyrol"),
          # the Masséna board again, the day's third road: a word TYPED with the table closed
          "typed": ("Massena", "ArchdukeCharles", "Carniola"),
          # the review's R15: the defence board's dawn, a word given from the table raised over the list
          "review": ("Massena", "ArchdukeCharles", "Tyrol"),
          # the review's R12: the typed board's first half, then End Turn with the day open
          "r12": ("Massena", "ArchdukeCharles", "Carniola")}
PLANS = {"ulm": "guard", "massena": "leave", "defence": "dawn", "typed": "typed", "review": "r15", "r12": "r12"}
BOARD = "massena"
LEAD, FOE, FIELD = BOARDS["massena"]
# the corps' starting ground on the two-corps boards (the lead's, the foe's)
GROUND = ("Tyrol", "Carniola")
DEFENCE_TUNINGS = ({"foe_strength": 64000}, {"foe_personality": "aggressive"})
SCENARIO = (REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json")
HUNT_TRIES = 60


def _quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def _day(body: dict) -> dict:
    day = (body or {}).get("battle_day")
    return day if isinstance(day, dict) else {}


def write_scenario(path: pathlib.Path, tuning: dict | None = None) -> pathlib.Path:
    """The 1805 campaign with the board the day needs: Masséna in the Tyrol and the
    Archduke Charles in Carniola, no other corps near (the stage tool's
    `_stage_massena`) — 96,000 men engaged, a great battle, two corps, and a
    day whose chips fit the panel. The opening board has Mack drawing off from
    every clash he loses, which leaves no day to press."""
    data = json.loads(SCENARIO.read_text(encoding="utf-8"))
    for name, marshal in data["marshals"].items():
        if name in (LEAD, FOE):
            continue
        marshal["location"] = {"France": "Paris", "Austria": "Vienna", "Russia": "Hungary"}.get(
            marshal.get("nation"), marshal["location"])
    data["marshals"][LEAD]["location"], data["marshals"][FOE]["location"] = GROUND
    for key, value in (tuning or {}).items():          # the defence board's tuning
        if key == "foe_strength":
            data["marshals"][FOE]["strength"] = int(value)
        elif key == "foe_personality":
            data["marshals"][FOE]["personality"] = str(value)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def _muster_question(M):
    """The muster's own question on the lead (`pending_interrupt`), or None."""
    ney = M.world.marshals.get(LEAD)
    asking = getattr(ney, "pending_interrupt", None)
    return asking if asking and asking.get("interrupt_type") == "muster_confirm" else None


def _go(client, M, command: str) -> dict:
    """An order through the ordinary road, and the muster's "Commit the Attack"
    answered if the order raised it (the interrupt popup's button, whose choice
    is `attack_anyway` on `/strategic_response`)."""
    body = _quiet(client.post, "/command", json={"command": command}).json()
    asking = _muster_question(M)
    if asking:
        body = _quiet(client.post, "/strategic_response", json={
            "marshal_name": asking["marshal"], "response_type": asking["interrupt_type"],
            "choice": "attack_anyway"}).json()
    if getattr(M.world, "pending_objection", None):
        # a marshal's objection ("I would rather attack than sit idle"): the modal's
        # Insist button, `POST /respond_to_objection`
        body = _quiet(client.post, "/respond_to_objection", json={"choice": "insist"}).json()
    return body


def _has_day_awaiting_us(obj) -> bool:
    """A tableau with a `day` that awaits us, anywhere in an end-turn response (the
    enemy phase's battle row: the dialog says 'the day awaits your word')."""
    if isinstance(obj, dict):
        day = obj.get("day")
        if isinstance(day, dict) and day.get("open") and day.get("awaits") == "ours":
            return True
        return any(_has_day_awaiting_us(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_has_day_awaiting_us(v) for v in obj)
    return False


def _hunt_defence(limit: int, tempdir: pathlib.Path) -> dict | None:
    """The defended day: End Turn through `/command`, then `GET /battle_day` as
    the notice's button reads it. The day must be the enemy's (side `defence`),
    open, awaiting us, banner "The day hangs", with "<Lead> strikes back" and
    "Fall back" both lit — and the enemy phase's own response must carry the
    battle row whose day awaits us."""
    from fastapi.testclient import TestClient
    import backend.main as M
    before = M.world
    try:
        with TestClient(M.app) as client:
            for index, tuning in enumerate(DEFENCE_TUNINGS):
                scenario = write_scenario(tempdir / f"ba3_defence_{index}.json", tuning)
                for n in range(limit):
                    seed = f"ba3-walk-{n:02d}"
                    _quiet(M._reset_world_state, player_nation="France",
                           scenario_override=str(scenario), seed=seed)
                    phase = _go(client, M, "end turn")
                    days = _quiet(client.get, "/battle_day").json().get("days") or []
                    day = next((d for d in days if d.get("side") == "defence" and d.get("open")
                                and d.get("awaits") == "ours"), None)
                    if day is None or day.get("banner") != "The day hangs":
                        continue
                    chips = day.get("chips") or []
                    strike = [c for c in chips if c.get("kind") == "press" and c.get("ok")
                              and str(c.get("label", "")).endswith("strikes back")]
                    fall = [c for c in chips if c.get("kind") == "break_off" and c.get("ok")
                            and c.get("label") == "Fall back"]
                    dig = [c for c in chips if c.get("kind") == "dig_in" and c.get("ok")]
                    if not (strike and fall and dig) or not _has_day_awaiting_us(phase.get("enemy_phase")):
                        continue
                    # the rest of the walk's road, played in-process: "<Lead> digs in" (a typed
                    # order that the lead may object to: Insist), then "Fall back"
                    left = int(M.world.actions_remaining)
                    dug = _go(client, M, dig[0]["command"])
                    mid = _day(dug)
                    if not dug.get("success") or int((dug.get("action_info") or {}).get("cost", -1)) != 0                             or int(M.world.actions_remaining) != left                             or int(mid.get("ours", 0)) != int(day.get("ours", 0)) - 1:
                        continue
                    reply = mid.get("reply") or {}
                    fell = None
                    if mid.get("open") and mid.get("awaits") == "ours":
                        fb2 = [c for c in mid.get("chips") or [] if c.get("label") == "Fall back" and c.get("ok")]
                        if not fb2:
                            continue
                        ground = M.world.marshals[LEAD].location
                        back = _go(client, M, fb2[0]["command"])
                        fell = _day(back)
                        if not back.get("success") or fell.get("ended") != "fell_back"                                 or fell.get("banner") != f"{LEAD} falls back"                                 or int((back.get("action_info") or {}).get("cost", -1)) != 0                                 or M.world.marshals[LEAD].location == ground:
                            continue
                    return {"seed": seed, "plan": "dawn", "tuning": tuning, "tuning_index": index,
                            "dig_in": {"ours": mid.get("ours"), "theirs": mid.get("theirs"), "open": mid.get("open"),
                                       "awaits": mid.get("awaits"), "his_reply": reply.get("kind"),
                                       "his_line": reply.get("line"), "his_tableau": bool(reply.get("diorama")),
                                       "chips": [c.get("label") for c in mid.get("chips") or []],
                                       "ended": mid.get("ended")},
                            "fall_back": None if fell is None else {"ended": fell.get("ended"), "banner": fell.get("banner")},
                            "day": {k: day.get(k) for k in ("ours", "theirs", "ours_of", "awaits", "side",
                                                            "banner", "his_temper", "field")},
                            "chips": [c.get("label") for c in chips]}
    finally:
        M._set_active_world(before)
    return None


def hunt(limit: int = HUNT_TRIES) -> dict | None:
    """The first seed of `ba3-walk-NN` whose campaign plays the board's road.
    The Masséna board: the opening's day hangs, the lead digs in (1 point, as the
    province panel's chip will), his answer leaves the day ours, the lead's press
    leaves it open, and the lead may then be left to it. The real Ulm opening:
    the day opens with the Guard lit as the second chip of row C, and the Guard
    goes in for two points and no action (whatever the day then does is
    recorded: Mack is dug in and surrounded, so the clash usually DECIDES it).
    The defence board: see `_hunt_defence`. Returns what the server answered, or
    None."""
    import tempfile
    # the hunt plays a real app in this process: its autosaves must never reach
    # the player's save folder
    os.environ["INK_IRON_SAVE_DIR"] = tempfile.mkdtemp(prefix="ba3_hunt_saves_")
    os.environ.setdefault("LLM_MODE", "mock")
    tempdir = pathlib.Path(tempfile.mkdtemp(prefix="ba3_hunt_"))
    if BOARD in ("defence", "review"):
        return _hunt_defence(limit, tempdir)
    scenario = write_scenario(tempdir / "ba3_scenario.json") if LEAD == "Massena" else None
    from fastapi.testclient import TestClient
    import backend.main as M
    before = M.world
    try:
        with TestClient(M.app) as client:
            for n in range(limit):
                seed = f"ba3-walk-{n:02d}"
                _quiet(M._reset_world_state, player_nation="France",
                       scenario_override=str(scenario) if scenario else "", seed=seed)
                opening = _go(client, M, f"{LEAD}, attack {FOE}")
                day = _day(opening)
                chips = day.get("chips") or []
                lit = [c for c in chips if c.get("ok") and c.get("kind") == "press"]
                words = {c.get("word") for c in chips if c.get("word")}
                if not (day.get("open") and day.get("awaits") == "ours" and lit and "leave_it" in words
                        and day.get("banner") == "The day hangs"):
                    continue
                left = int(M.world.actions_remaining)
                if LEAD == "Ney":
                    guard = [i for i, c in enumerate(chips) if c.get("kind") == "guard" and c.get("ok")]
                    if guard != [1]:
                        continue                    # the Guard is chip 1, lit, beside the press
                    press = _go(client, M, chips[1]["command"])
                    if not press.get("success") or int((press.get("action_info") or {}).get("cost", -1)) != 0 \
                            or int(M.world.actions_remaining) != left:
                        continue
                    after = _day(press)
                    return {"seed": seed, "plan": "guard",
                            "day": {k: day.get(k) for k in ("ours", "theirs", "ours_of", "awaits", "side", "banner")},
                            "guard": {"ended": after.get("ended"), "banner": after.get("banner"),
                                      "ours": after.get("ours"), "open": after.get("open")}}
                # the province panel's press: "<lead> digs in", one point, no action
                dig = [c for c in chips if c.get("kind") == "dig_in" and c.get("ok")]
                if not dig:
                    continue
                dug = _go(client, M, dig[0]["command"])
                mid = _day(dug)
                if not dug.get("success") or int((dug.get("action_info") or {}).get("cost", -1)) != 0 \
                        or int(M.world.actions_remaining) != left or not mid.get("open") \
                        or mid.get("awaits") != "ours" or int(mid.get("ours", 0)) != int(day.get("ours", 0)) - 1:
                    continue
                lit = [c for c in mid.get("chips") or [] if c.get("ok") and c.get("kind") == "press"]
                if not lit:
                    continue
                press = _go(client, M, lit[0]["command"])
                after = _day(press)
                if not press.get("success") or not after.get("open") \
                        or after.get("awaits") != "ours" \
                        or int((press.get("action_info") or {}).get("cost", -1)) != 0 \
                        or int(M.world.actions_remaining) != left \
                        or "leave_it" not in {c.get("word") for c in after.get("chips") or []}:
                    continue
                word = _quiet(client.post, "/battle_day/word",
                              json={"enemy": after.get("enemy"), "word": "leave_it"}).json()
                if not word.get("success"):
                    continue
                return {"seed": seed, "plan": "leave",
                        "day": {k: day.get(k) for k in ("ours", "theirs", "awaits", "side", "banner")},
                        "dig_in": {k: mid.get(k) for k in ("ours", "theirs", "awaits")},
                        "press": {k: after.get(k) for k in ("ours", "theirs", "awaits")},
                        "word": {"ended": _day(word).get("ended"), "message": word.get("message")}}
    finally:
        M._set_active_world(before)
    return None


def _godot_running() -> int:
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=30,
                             stdin=subprocess.DEVNULL).stdout
    except Exception:
        return 0
    return sum(1 for line in out.splitlines() if "godot" in line.lower())


def _free(port: int) -> bool:
    import socket
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def start_backend(work: pathlib.Path, port: int, seed: str, scenario):
    """`uxr3_action_probe.start_backend` on a ROLLED seed (that one pins
    `historical`, whose battle dice are the module's and name no battle)."""
    while port == 8005 or not _free(port):
        port += 1
    saves = work / "saves"
    saves.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.pop("SOVEREIGN_SMOKE_START", None)
    env.pop("SOVEREIGN_SCENARIO", None)
    if scenario:
        env["SOVEREIGN_SCENARIO"] = str(scenario)
    env.update({"SOVEREIGN_PORT": str(port), "INK_IRON_SAVE_DIR": str(saves), "LLM_MODE": "mock",
                "SOVEREIGN_SEED": seed, "DEBUG_MODE": "false",
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


def _lead_location(port: int) -> str:
    """Where the server says the lead stands (`GET /marshal_overview`: the first
    card named for him that carries a location), or "" when it cannot say."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/marshal_overview", timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return ""

    def find(obj):
        if isinstance(obj, dict):
            if obj.get("name") == LEAD and isinstance(obj.get("location"), str):
                return obj["location"]
            for v in obj.values():
                got = find(v)
                if got:
                    return got
        elif isinstance(obj, list):
            for v in obj:
                got = find(v)
                if got:
                    return got
        return ""
    return find(data)


def run_board(board: str, args, root: pathlib.Path) -> int:
    """One walk on one board: hunt (or take `--seed`), the sandboxed backend, the
    engine, the run record. Returns 0 only when the walk passed."""
    global LEAD, FOE, FIELD, BOARD
    BOARD = board
    LEAD, FOE, FIELD = BOARDS[board]
    print(f"== board {board}: {LEAD} against {FOE} at {FIELD}, plan {PLANS[board]}")
    if args.seed:
        found = {"seed": args.seed}
        if board in ("defence", "review"):
            found["tuning"] = DEFENCE_TUNINGS[args.tuning]
    else:
        found = hunt()
        if found is None:
            print(f"no campaign seed of ba3-walk-00..{HUNT_TRIES - 1} plays the {board} road")
            return 1
    print("seed:", json.dumps(found, ensure_ascii=False))
    if args.hunt_only:
        return 0
    run = (root / board).resolve()
    frames = run / "frames"
    if frames.is_dir():
        shutil.rmtree(frames)
    frames.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    scenario = (write_scenario(run / "ba3_scenario.json", found.get("tuning"))
                if board in ("massena", "defence", "typed", "review", "r12") else None)
    backend, port = start_backend(run, args.port, found["seed"], scenario)
    result = {"board": board, "port": port, "seed": found, "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "lead_before": _lead_location(port)}
    try:
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.update({"SOVEREIGN_PORT": str(port), "BA3_WALK_OUT": str(frames), "BA3_PLAN": PLANS[board],
                    "BA3_LEAD": LEAD, "BA3_FOE": FOE, "BA3_FIELD": FIELD})
        argv = [args.godot, "--audio-driver", "Dummy", "--windowed", "--resolution", "1920x1080",
                "--log-file", str(run / "engine.log"),
                "--path", str(PROJECT), "--script", str(WALK)]
        t1 = time.time()
        with (run / "godot.log").open("w", encoding="utf-8") as log:
            proc = subprocess.run(argv, cwd=str(PROJECT), env=env, stdout=log, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, timeout=args.timeout)
        result["engine_exit"] = proc.returncode
        result["engine_s"] = round(time.time() - t1, 1)
        result["lead_after"] = _lead_location(port)
        try:    # what the server holds after the walk
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/battle_day", timeout=20) as r:
                result["server_days"] = json.loads(r.read().decode("utf-8"))
        except Exception as exc:
            result["server_days"] = {"error": repr(exc)}
    finally:
        backend.terminate()
        try:
            backend.wait(timeout=20)
        except Exception as exc:
            print(f"the backend did not stop ({exc!r}); killed")
            backend.kill()
    engine_log = run / "engine.log"
    log_text = engine_log.read_text(encoding="utf-8", errors="replace") if engine_log.is_file() else ""
    result["engine_log_bytes"] = len(log_text)
    result["script_errors"] = [ln.strip() for ln in log_text.splitlines() if SCRIPT_ERROR_RX.search(ln)]
    result["engine_errors"] = len(ENGINE_ERROR_RX.findall(log_text))
    walk_path = frames / "walk.json"
    result["walk"] = json.loads(walk_path.read_text(encoding="utf-8")) if walk_path.is_file() else None
    result["total_s"] = round(time.time() - t0, 1)
    (run / "run.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    walk = result["walk"] or {}
    print(f"engine exit {result.get('engine_exit')} in {result.get('engine_s')} s; "
          f"results {len(walk.get('results', []))}; frames {len(walk.get('steps', []))}; "
          f"errors {len(walk.get('errors', []))}; script errors {len(result['script_errors'])}")
    for row in walk.get("results", []):
        print(f"  {'ok ' if row.get('ok') else 'BAD'} {row.get('step'):22s} {row.get('did')}\n"
              f"        -> {row.get('saw')}")
    for err in walk.get("errors", []):
        print("  ERROR", err)
    for line in result["script_errors"][:12]:
        print("  SCRIPT", line)
    passed = bool(result.get("engine_exit") == 0 and not result["script_errors"]
                  and result["engine_log_bytes"] > 0 and walk.get("results")
                  and not walk.get("errors"))
    if board == "defence" and any(r.get("step") == "fall_back" and r.get("ok") for r in walk.get("results", [])) \
            and result.get("lead_before") and result.get("lead_after") == result.get("lead_before") \
            and not any(r.get("step") == "fall_back" and "no longer awaits" in str(r.get("did", "")) for r in walk.get("results", [])):
        print(f"  BAD the corps has NOT moved: {result.get('lead_before')} -> {result.get('lead_after')}")
        passed = False
    if board == "defence":
        print(f"  the lead's ground: {result.get('lead_before')!r} -> {result.get('lead_after')!r}")
    if args.export and not passed:
        print("NOT exported — the run did not pass. Run folder:", run)
    elif args.export:
        dest = pathlib.Path(args.export)
        dest = (dest if dest.is_absolute() else REPO / dest) / board
        if (dest / "frames").is_dir():
            shutil.rmtree(dest / "frames")
        (dest / "frames").mkdir(parents=True, exist_ok=True)
        for f in sorted(frames.glob("*.jpg")):
            shutil.copyfile(f, dest / "frames" / f.name)
        if walk_path.is_file():
            shutil.copyfile(walk_path, dest / "walk.json")
        shutil.copyfile(run / "run.json", dest / "run.json")
        print("exported ->", dest)
    return 0 if passed else 1


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    ap.add_argument("--port", type=int, default=8006)
    ap.add_argument("--godot", default=os.environ.get("GODOT_BIN") or GODOT_DEFAULT)
    ap.add_argument("--export", default="")
    ap.add_argument("--seed", default="", help="skip the hunt: a seed already known to play the road")
    ap.add_argument("--tuning", type=int, default=0, help="with --seed on the defence board: which of "
                    "DEFENCE_TUNINGS the seed was found with (the hunt prints it)")
    ap.add_argument("--hunt-only", action="store_true")
    ap.add_argument("--board", choices=sorted(BOARDS) + ["all", "both"], default="all",
                    help="`both` is an alias of `all` (the three boards)")
    ap.add_argument("--timeout", type=int, default=1200)
    args = ap.parse_args()
    boards = sorted(BOARDS) if args.board in ("all", "both") else [args.board]
    if not args.hunt_only:
        if not args.out:
            raise SystemExit("--out <run folder> is required for the walk")
        if not pathlib.Path(args.godot).is_file():
            raise SystemExit(f"no Godot at {args.godot}")
        n = _godot_running()
        if n:
            raise SystemExit(f"refused: {n} Godot process(es) already running - never two engines at once")
    root = pathlib.Path(args.out) if args.out else pathlib.Path(".")
    codes = [run_board(board, args, root) for board in boards]
    return 0 if not any(codes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
