"""DD-B "The fresh-eyes campaign" — the instrument: a player's hands on the
real client (Pre-Deploy S13, Slice 1, October 14, 2026).

`docs/PRE_DEPLOY_PLAN.md` row S13 / §3 DD-B: three campaigns played IN THE
CLIENT at 5120x1440 by players who have not read the ledgers. The players see
exactly what a player sees and act only as a player can:

* `tools/dd_b_client.gd` boots the game as it launches (the title screen,
  `main_menu.tscn`, whose real client talks to a sandboxed backend) in a
  5120x1440 window parked past the desktop, at the Interface Scale the menu
  derives for that screen (1.4), from a FIRST launch (an empty in-memory
  `UiSettings`, `_persist` false). It polls `<run>/inbox/NNNN.json` for one
  action at a time, acts through real input events, settles, and writes the
  full frame, a 2560-wide view JPEG and the state record;
* `tools/dd_b_play.py` starts the sandboxed backend (`uxr3_action_probe.
  start_backend`: never 8005) and the ONE engine, writes each action and
  prints a compact summary, stops the run (`run.json`), and judges every
  typed line with the ONE judge (`tools/_score_probes.py`'s regexes, through
  `unrehearsed_census.classify_order`).

The driven test plays the short script the S13 prompt names — title → Begin →
the war room → T → Pin → `type end turn` → the enemy phase → Continue → Esc —
and asserts each state record shows what its action changed. It SKIPS without
the engine (a skip is not a pass). The judge and the rails are pinned on the
source and on a synthetic run, engine or not.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
CLIENT = REPO / "tools" / "dd_b_client.gd"
PLAY = REPO / "tools" / "dd_b_play.py"
sys.path.insert(0, str(REPO / "tools"))

import dd_b_play as P  # noqa: E402

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    P.GODOT_DEFAULT,
    "godot",
    "godot4",
]


def _engine():
    for candidate in _CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate or "/" in candidate:
            if pathlib.Path(candidate).is_file():
                return candidate
            continue
        found = shutil.which(candidate)
        if found:
            return found
    return None


# ── the rails and the judge, on the source and a synthetic run ─────────────

class TestTheRails:
    def test_the_client_refuses_the_players_backend_and_writes_nothing_to_disk(self):
        src = CLIENT.read_text(encoding="utf-8")
        assert 'Utils.backend_url().ends_with(":8005")' in src
        assert "UiSettings._cfg = ConfigFile.new()" in src
        assert 'settings_class.set("_persist", false)' in src
        # A FIRST launch: no latch is pre-set (the scale card, the parser
        # hint and the tutor are as a new player has them).
        for latch in ("scale_acknowledged", "hint_seen", '"tutorial", "done"'):
            assert latch not in src, latch

    def test_the_window_is_the_users_screen_parked_past_the_desktop(self):
        assert P.WINDOW == "5120x1440"
        assert P.PARKED.startswith("5200,")
        src = CLIENT.read_text(encoding="utf-8")
        assert "Vector2i(5120, 1440)" in src and "Vector2i(5200, 20)" in src
        # The parked window never takes the OS focus: the player's own keys
        # never reach it.
        assert 'root.unfocusable = OS.get_environment("DD_B_FOCUSABLE") != "1"' in src

    def test_start_refuses_a_second_engine_and_the_players_port(self):
        src = PLAY.read_text(encoding="utf-8")
        assert "never two engines at once" in src
        assert "refused: never the player's 8005" in src
        assert "AP.start_backend(run, args.port)" in src

    def test_a_typed_line_states_what_it_meant(self):
        with pytest.raises(SystemExit) as e:
            P.main(["act", "--out", str(REPO / "no_such_run"), "type Ney, attack Mack"])
        assert "no run" in str(e.value)
        assert P._parse_meant("attack Ney") == {"action": "attack", "marshal": "Ney"}
        assert P._parse_meant("question")["action"] == "question"
        assert P._parse_meant("other: enact a law") == {"action": "other", "marshal": "",
                                                         "words": "enact a law"}
        assert set(P.GENERIC_FAMILIES) <= P._families()


class TestTheJudge:
    """Every typed line is classified by the ONE judge; a misread is P1."""

    def _run(self, tmp_path, lines):
        run = tmp_path / "run"
        (run / "state").mkdir(parents=True)
        (run / "inbox").mkdir()
        for i, (line, meant, reply) in enumerate(lines, start=1):
            (run / "inbox" / f"{i:04d}.json").write_text(
                json.dumps({"n": i, "action": "type " + line, "meant": meant}), encoding="utf-8")
            (run / "state" / f"{i:04d}.json").write_text(
                json.dumps({"n": i, "action": "type " + line, "turn": "Turn 3 — x", "reply": reply}),
                encoding="utf-8")
        return run

    def test_the_classes_and_the_p1(self, tmp_path):
        run = self._run(tmp_path, [
            ("Ney, attack Mack", "attack Ney",
             {"success": True, "message": "Ney attacks Mack at Swabia! ⚔"}),
            ("Davout, go to Lorraine", "move Davout",
             {"success": True, "message": "Davout fortifies his position."}),
            ("who am I fighting", "question",
             {"success": True, "message": "We are at war with Britain, Austria and Russia."}),
            ("Soult, fortify", "fortify Soult",
             {"success": False, "message": "Not enough actions remaining, Sire — Soult waits."}),
            ("enact the conscription law", "other: enact a law",
             {"success": True, "message": "Enacted."}),
        ])
        rec = P.judge_run(run)
        classes = [r["class"] for r in rec["rows"]]
        assert classes == ["as_meant", "misread", "answered", "board_refusal", "unjudged_other"]
        assert [r["n"] for r in rec["p1"]] == [2]

    def test_an_assault_on_the_works_is_the_attack_meant(self, tmp_path):
        """The conquest road's twelve false misreads (S13): a typed attack on a
        province's works answers in the assault's own words."""
        run = self._run(tmp_path, [
            ("Ney, attack Vienna", "attack Ney",
             {"success": True, "message": "ASSAULT — Ney storms the works at Vienna alone: 16,494 men."}),
            ("Soult, attack Silesia", "attack Soult",
             {"success": True, "message": "Soult assaults the Silesia garrison! Garrison holds."}),
            ("Lannes, take Posen", "attack Lannes",
             {"success": True, "message": "The detachment of 375 at Posen lays down its arms."}),
            ("Massena, retake Vienna", "attack Massena",
             {"success": True, "message": "Massena marches from Dresden into Vienna unopposed!"}),
        ])
        rec = P.judge_run(run)
        assert [r["class"] for r in rec["rows"]] == ["as_meant"] * 4
        assert rec["p1"] == []


# ── the driven test: a player's hands on the real client ───────────────────

def _act(run: pathlib.Path, action: str, meant: str = "") -> dict:
    argv = ["act", "--out", str(run)] + (["--meant", meant] if meant else []) + [action]
    code = P.main(argv)
    assert code == 0, f"{action}: act returned {code}"
    n = P._next_n(run) - 1
    return json.loads((run / "state" / f"{n:04d}.json").read_text(encoding="utf-8"))


def _modal(state: dict) -> list:
    return [p for p in state.get("open", {}).get("popups", []) if "(not modal)" not in p]


_ANSWERS = ("continue", "close", "dismiss", "acknowledge", "ok", "later", "proceed", "insist")


def _answer_chain(run: pathlib.Path, state: dict, answered: list, limit: int = 14) -> dict:
    """Answer the modals until none stands, as a player would: the first
    answering button above the modal floor, pressed by a real click."""
    for _ in range(limit):
        modal = _modal(state)
        if not modal and state.get("scene") == "main":
            return state
        floor = int(state.get("modal_floor", -10**6))
        live = [b for b in state.get("buttons", [])
                if int(b["layer"]) >= floor and not b.get("disabled") and b.get("kind") != "slider"]
        pick = None
        for word in _ANSWERS:
            pick = next((b for b in live if b["text"].strip().lower().startswith(word)), None)
            if pick:
                break
        if pick is None and "battle_diorama" in " ".join(modal):
            w, h = state["factor"]["logical_size"]
            state = _act(run, f"click_at {int(w / 2)} {int(h / 2)}")
            answered.append("battle_diorama: skip")
            continue
        assert pick is not None, f"no answer on {modal}: {[b['text'] for b in live]}"
        r = pick["rect"]
        state = _act(run, f"click_at {int(r[0] + r[2] / 2)} {int(r[1] + r[3] / 2)}")
        answered.append(f"{modal}: {pick['text']}")
    raise AssertionError(f"the chain never ended: {answered}")


@pytest.fixture(scope="module")
def played(tmp_path_factory) -> dict:
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, and a skip is not a pass")
    if P._godot_running():
        pytest.skip("another Godot engine is running — never two at once")
    run = tmp_path_factory.mktemp("dd_b_hands") / "run"
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    log = (run.parent / "start.log").open("w", encoding="utf-8")
    sup = subprocess.Popen([sys.executable, "-X", "utf8", str(PLAY), "start", "--road", "conquest",
                            "--out", str(run), "--godot", engine],
                           cwd=str(REPO), env=env, stdout=log, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL)
    states: dict = {"answered": []}
    try:
        t0 = time.time()
        while not (run / "state" / "0000.json").is_file():
            assert sup.poll() is None, (run.parent / "start.log").read_text(encoding="utf-8")
            assert time.time() - t0 < 300, "the engine never booted"
            time.sleep(0.5)
        states["boot"] = json.loads((run / "state" / "0000.json").read_text(encoding="utf-8"))
        states["looks_right"] = _act(run, "click Looks right")
        states["begin"] = _act(run, "click Begin")
        # The war room hands the command line the focus: a bare T would type
        # a "t" there. Esc gives the focus back to the map, as a player finds.
        states["esc_line"] = _act(run, "key Escape")
        states["t"] = _act(run, "key T")
        states["pin"] = _act(run, "click Pin")
        states["end_turn"] = _act(run, "type end turn", meant="end_turn")
        states["continue"] = _act(run, "click Continue") if "enemy_phase" in _modal(states["end_turn"]) \
            else states["end_turn"]
        states["settled"] = _answer_chain(run, states["continue"], states["answered"])
        esc = states["settled"]
        for _ in range(3):
            esc = _act(run, "key Escape")
            if not esc["open"]["pinned"]:
                break
        states["esc"] = esc
        P.main(["stop", "--out", str(run)])
        sup.wait(timeout=180)
    finally:
        if sup.poll() is None:
            sup.terminate()
            meta = run / "meta.json"
            if meta.is_file():
                for pid in (json.loads(meta.read_text(encoding="utf-8")).get(k)
                            for k in ("engine_pid", "backend_pid")):
                    if pid:
                        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True,
                                       stdin=subprocess.DEVNULL)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    states["dir"] = run
    return states


class TestThePlayersHands:
    def test_a_first_launch_at_5120x1440_and_the_derived_scale(self, played):
        boot = played["boot"]
        assert boot["ok"], boot["error"]
        assert boot["scene"] == "main_menu"
        assert boot["factor"]["physical_size"] == [5120, 1440]
        assert boot["ui_scale"]["derived_for_5120x1440"] == 1.4
        assert boot["ui_scale"]["window"] == 1.4
        assert "scale_card" in boot["open"]["popups"], "a first launch shows the sizing card"
        assert any("Begin the 1805 Campaign" == b["text"] for b in boot["buttons"])

    def test_the_frames_and_the_record(self, played):
        run = played["dir"]
        from PIL import Image
        with Image.open(run / "frames" / "0000_view.jpg") as im:
            assert im.size[0] == 2560
        with Image.open(run / "frames" / "0000.png") as im:
            assert im.size == (5120, 1440)
        s = played["begin"]
        assert s["texts"] and all({"text", "rect", "layer", "surface"} <= set(t) for t in s["texts"])
        assert s["buttons"] and all({"text", "rect", "disabled", "layer"} <= set(b) for b in s["buttons"])
        assert s["map"], "the map's names and pieces, with their screen rects"
        assert len(s["terminal_tail"]) <= 12 and s["terminal_tail"]

    def test_the_card_answered_and_the_campaign_begun(self, played):
        assert "scale_card" not in played["looks_right"]["open"]["popups"]
        begin = played["begin"]
        assert begin["scene"] == "main"
        assert begin["turn"].startswith("Turn 1")
        assert begin["command_line"]["focused"] is True

    def test_t_opens_the_ledger_and_the_chip_pins_it(self, played):
        assert played["esc_line"]["command_line"]["focused"] is False
        assert played["t"]["open"]["screens"] == ["ledger"]
        assert played["pin"]["open"]["pinned"] == "ledger"

    def test_a_typed_line_goes_by_its_keys_and_the_turn_ends(self, played):
        s = played["end_turn"]
        assert s["ok"], s["error"]
        assert "own road" not in s["note"], s["note"]
        assert s["reply"] and s["reply"]["success"] is True
        assert "Turn 2" in s["turn"]
        assert s["open"]["pinned"] == "ledger", "the pinned ledger survives the end turn"

    def test_the_chain_is_answered_and_esc_closes_the_desk(self, played):
        assert not _modal(played["settled"])
        esc = played["esc"]
        assert esc["open"]["pinned"] == "" and esc["open"]["screens"] == []

    def test_the_run_record(self, played):
        rec = played["run"]
        assert rec["turn_number"] == 2
        assert rec["n_actions"] >= 9
        assert rec["n_script_errors"] == 0, rec["script_errors"]
        assert rec["port"] != 8005
