"""Row BA, BA-4 — "the roads and the fog", pressed in the real client: the
runner (`docs/BATTLE_DIORAMA_SPEC.md` §15.20; November 16, 2026) — after
tools/ba3_mode_c_walk.py, whose board, backend sandbox and helpers it uses.

    .venv/Scripts/python.exe tools/ba4_mode_c_walk.py --hunt-only
    .venv/Scripts/python.exe tools/ba4_mode_c_walk.py --out <run> [--board day|roads|oldsave|all]
                                                      [--port 8006] [--seed ba4-walk-NN] [--export <audit dir>]

Three boards, three walks through the REAL main.tscn against a sandboxed backend
(never 8005; `<run>/<board>/saves` as its save folder; the mock parser):

`day` — Masséna in the Tyrol against the Archduke Charles in Carniola (BA-3's
two-corps board): the attack card BEFORE a day (an ordinary order, 1 action);
the day opens and its FIRST-OPEN LINE stands on a row of its own and is
acknowledged; the chips carry their DIGITS; `2` (no Guard on this field) is
denied and sends nothing — neither a word nor a slot of the selection card
under the table; `1` presses (one word, a point, no action); with the day open
the same attack's card reads "A word of the day — 1 point" and the province's
panel lists it once (the day's chips, no second ATTACK row); the panel's
"Break off" closes the day and its CLOSE is told with its tally; a digit on
the closed day's table does nothing.

`roads` — the real 1805 opening: Murat's support card for Ney, whose road runs
through Mack's Swabia, reads "halts at the approach" and its Send raises no
question; a march whose first step costs men names the figure on its card;
Help's Terms page carries the session's three terms.

`oldsave` — a save BA-3 wrote: `tests/fixtures/playtest_saves/
fixture_ba3_open_day_aeae6967.json` (HEAD `aeae6967` through its own `/save`,
the `day` board's campaign with the day OPEN after two clashes and awaiting our
word). The client loads it by its own Load; the day is offered on its
province's panel with its chips; the press from the panel brings the table,
the next clash under its own name (a day that kept no name names no "further
clash") and the first day's line; the digit `8` breaks off, and the close
tells how it ended and NO tally (a day that kept no count from its opening
starts none mid-day).

The `day` board's campaign seed is HUNTED in-process (a served campaign on a
rolled seed fights its battles with the campaign's own dice, so a seed names
the battle): the opening day must hang and await us with the press lit and the
first-open line on its block; the press must leave it open and ours; "Break
off" must then close it with its close line. Rails as BA-3's: never two
engines; exit 0 only when the engine ended cleanly, no script error was logged
and every step held.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import ba3_mode_c_walk as B3  # noqa: E402

PROJECT = B3.PROJECT
WALK = REPO / "tools" / "ba4_mode_c_walk.gd"
BOARDS = {"day": ("Massena", "ArchdukeCharles", "Carniola"), "roads": ("Ney", "Mack", "Swabia"),
          "oldsave": ("Massena", "ArchdukeCharles", "Carniola")}
OLD_SAVE = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_ba3_open_day_aeae6967.json"
HUNT_TRIES = 80


def hunt(limit: int = HUNT_TRIES) -> dict | None:
    """The first seed of `ba4-walk-NN` whose campaign plays the `day` board's
    road (see the module's word)."""
    os.environ["INK_IRON_SAVE_DIR"] = tempfile.mkdtemp(prefix="ba4_hunt_saves_")
    os.environ.setdefault("LLM_MODE", "mock")
    tempdir = pathlib.Path(tempfile.mkdtemp(prefix="ba4_hunt_"))
    B3.BOARD = "massena"
    B3.LEAD, B3.FOE, B3.FIELD = B3.BOARDS["massena"]
    scenario = B3.write_scenario(tempdir / "ba4_scenario.json")
    from fastapi.testclient import TestClient
    import backend.main as M
    before = M.world
    try:
        with TestClient(M.app) as client:
            for n in range(limit):
                seed = f"ba4-walk-{n:02d}"
                B3._quiet(M._reset_world_state, player_nation="France",
                          scenario_override=str(scenario), seed=seed)
                opening = B3._go(client, M, f"{B3.LEAD}, attack {B3.FOE}")
                day = B3._day(opening)
                chips = day.get("chips") or []
                press = [c for c in chips if c.get("ok") and c.get("kind") == "press"]
                words = {c.get("word") for c in chips if c.get("word")}
                if not (day.get("open") and day.get("awaits") == "ours" and press
                        and "break_off" in words and day.get("first_open")
                        and not any(c.get("kind") == "guard" for c in chips)):
                    continue
                left = int(M.world.actions_remaining)
                pressed = B3._go(client, M, press[0]["command"])
                after = B3._day(pressed)
                if not pressed.get("success") or not after.get("open") or after.get("awaits") != "ours" \
                        or int(M.world.actions_remaining) != left \
                        or int(after.get("ours", -1)) != int(day.get("ours", 0)) - 1 \
                        or "break_off" not in {c.get("word") for c in after.get("chips") or []}:
                    continue
                broke = B3._quiet(client.post, "/battle_day/word",
                                  json={"enemy": after.get("enemy"), "word": "break_off"}).json()
                closing = B3._day(broke)
                if not broke.get("success") or closing.get("ended") != "broke_off" or not closing.get("close"):
                    continue
                return {"seed": seed,
                        "day": {k: day.get(k) for k in ("ours", "theirs", "awaits", "side", "banner")},
                        "press": {k: after.get(k) for k in ("ours", "theirs", "awaits")},
                        "close": closing.get("close")}
    finally:
        M._set_active_world(before)
    return None


def a_march_with_a_cost() -> dict:
    """On the real opening: Ney's ground (the friend Murat is ordered to
    support) and a march whose quote names the men its first step costs."""
    from backend.commands import order_quotes
    from tools import ba1_stage_battles as stage
    world, _executor = stage._board()
    out = {"friend_at": world.marshals["Ney"].location, **a_pitched_battle()}
    for name in ("Davout", "Soult", "Lannes", "Ney"):
        marshal = world.marshals[name]
        for dest in world.get_region(marshal.location).adjacent_regions:
            quote = order_quotes.march_quote(world, marshal, dest)
            if quote.get("ok") and quote.get("march_cost"):
                out.update(who=name, to=dest, cost=str(quote["march_cost"]))
                return out
    return out


def a_pitched_battle() -> dict:
    """On the real opening: an attack of ours on a corps in sight whose card
    forecasts a key battle SHORT of a great one (50,000 men or more engaged,
    under 80,000) — and the sentence its card must then carry, worked here
    from the server's own quote. On a board of its own, marked SERVED as the
    sandboxed server's campaign is: a day is forecast only where a campaign
    is served."""
    from backend.commands import order_quotes
    from backend.game_logic import campaign_variance
    from tools import ba1_stage_battles as stage
    world, _executor = stage._board()
    campaign_variance.serve_campaign(world)
    player = world.player_nation
    for name in sorted(world.marshals):
        marshal = world.marshals[name]
        if marshal.nation != player or int(getattr(marshal, "strength", 0) or 0) <= 0:
            continue
        for foe_name in sorted(world.marshals):
            foe = world.marshals[foe_name]
            if foe.nation == player or int(getattr(foe, "strength", 0) or 0) <= 0 \
                    or not world.is_at_war(player, foe.nation):
                continue
            seen = any((row.get("name") if isinstance(row, dict) else getattr(row, "name", "")) == foe.name
                       for row in world.get_visible_enemies_in_region(foe.location, player))
            if not seen:
                continue
            quote = order_quotes.attack_quote(world, marshal, foe)
            day = quote.get("day") or {}
            if quote.get("ok") and day.get("pitched") and int(quote.get("ap") or 0) == 1:
                points = int(day.get("points") or 0)
                return {"pitched_who": name, "pitched_foe": foe.name, "pitched_at": foe.location,
                        "pitched_said": "A pitched battle — %s commands the day: %d point%s." % (
                            quote.get("shown") or name, points, "" if points == 1 else "s")}
    return {}


def run_board(board: str, args, root: pathlib.Path) -> int:
    lead, foe, field = BOARDS[board]
    print(f"== board {board}: {lead} against {foe} at {field}")
    extra_env = {}
    if board == "day":
        found = {"seed": args.seed} if args.seed else hunt()
        if found is None:
            print(f"no campaign seed of ba4-walk-00..{HUNT_TRIES - 1} plays the day's road")
            return 1
    elif board == "oldsave":
        saved = json.loads(OLD_SAVE.read_text(encoding="utf-8"))
        old_day = next(iter(saved["world_state"]["battle_days"]["days"].values()))
        found = {"seed": args.seed or "ba4-walk-oldsave", "save": OLD_SAVE.name,
                 "saved_seed": saved["metadata"].get("campaign_seed"), "field": old_day.get("field"),
                 "day_keys": sorted(old_day)}
        extra_env = {"BA4_OLD_SAVE": OLD_SAVE.name, "BA4_OLD_FIELD": str(old_day.get("field") or "")}
    else:
        found = {"seed": args.seed or "ba4-walk-roads", **a_march_with_a_cost()}
        extra_env = {"BA4_FRIEND_AT": found.get("friend_at", ""), "BA4_MARCH_WHO": found.get("who", ""),
                     "BA4_MARCH_TO": found.get("to", ""), "BA4_MARCH_COST": found.get("cost", ""),
                     "BA4_PITCHED_WHO": found.get("pitched_who", ""), "BA4_PITCHED_FOE": found.get("pitched_foe", ""),
                     "BA4_PITCHED_AT": found.get("pitched_at", ""), "BA4_PITCHED_SAID": found.get("pitched_said", "")}
    print("seed:", json.dumps(found, ensure_ascii=False))
    if args.hunt_only:
        return 0
    run = (root / board).resolve()
    frames = run / "frames"
    if frames.is_dir():
        shutil.rmtree(frames)
    frames.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    scenario = None
    if board == "oldsave":
        # the sandbox's save folder holds the old save before the server starts
        (run / "saves").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(OLD_SAVE, run / "saves" / OLD_SAVE.name)
    if board in ("day", "oldsave"):
        B3.BOARD = "massena"
        B3.LEAD, B3.FOE, B3.FIELD = B3.BOARDS["massena"]
        scenario = B3.write_scenario(run / "ba4_scenario.json")
    backend, port = B3.start_backend(run, args.port, found["seed"], scenario)
    result = {"board": board, "port": port, "seed": found, "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    try:
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.update({"SOVEREIGN_PORT": str(port), "BA4_WALK_OUT": str(frames),
                    "BA4_PLAN": board,
                    "BA4_LEAD": lead, "BA4_FOE": foe, "BA4_FIELD": field, **extra_env})
        argv = [args.godot, "--audio-driver", "Dummy", "--windowed", "--resolution", "1920x1080",
                "--log-file", str(run / "engine.log"), "--path", str(PROJECT), "--script", str(WALK)]
        t1 = time.time()
        with (run / "godot.log").open("w", encoding="utf-8") as log:
            proc = subprocess.run(argv, cwd=str(PROJECT), env=env, stdout=log, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, timeout=args.timeout)
        result["engine_exit"] = proc.returncode
        result["engine_s"] = round(time.time() - t1, 1)
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
    result["script_errors"] = [ln.strip() for ln in log_text.splitlines() if B3.SCRIPT_ERROR_RX.search(ln)]
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
                  and result["engine_log_bytes"] > 0 and walk.get("results") and not walk.get("errors"))
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
    ap.add_argument("--godot", default=os.environ.get("GODOT_BIN") or B3.GODOT_DEFAULT)
    ap.add_argument("--export", default="")
    ap.add_argument("--seed", default="", help="skip the hunt: a seed already known to play the day's road")
    ap.add_argument("--hunt-only", action="store_true")
    ap.add_argument("--board", choices=sorted(BOARDS) + ["all"], default="all")
    ap.add_argument("--timeout", type=int, default=1200)
    args = ap.parse_args()
    boards = sorted(BOARDS) if args.board == "all" else [args.board]
    if not args.hunt_only:
        if not args.out:
            raise SystemExit("--out <run folder> is required for the walk")
        if not pathlib.Path(args.godot).is_file():
            raise SystemExit(f"no Godot at {args.godot}")
        n = B3._godot_running()
        if n:
            raise SystemExit(f"refused: {n} Godot process(es) already running - never two engines at once")
    root = pathlib.Path(args.out) if args.out else pathlib.Path(".")
    codes = [run_board(board, args, root) for board in boards]
    return 0 if not any(codes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
