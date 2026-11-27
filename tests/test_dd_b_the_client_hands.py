"""DD-B "The fresh-eyes campaign" — the instrument: a player's hands on the
real client (Pre-Deploy S13, Slice 1, October 14, 2026).

`docs/PRE_DEPLOY_PLAN.md` row S13 / §3 DD-B: three campaigns played IN THE
CLIENT at 5120x1440 by players who have not read the ledgers. The players see
exactly what a player sees and act only as a player can:

* `tools/dd_b_client.gd` boots the game as it launches (the title screen,
  `main_menu.tscn`, whose real client talks to a sandboxed backend) in a
  5120x1440 window parked past the desktop, at the Interface Scale the menu
  derives for that screen (1.6 since Session UI-2; 1.4 before), from a FIRST launch (an empty in-memory
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

import collections
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

import pytest

from tests._ledgers import doc_text  # CODE-4: the ledger plus its archives

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
    def test_the_screenshot_scene_refuses_the_players_backend_too(self):
        """S14D-X18 (October 24, 2026): `tools/tutorial_screenshot.gd` said
        "Requires the LIVE backend on 8005" and would `/new_game` over the
        player's world; it now holds the same port rail as the client."""
        src = (CLIENT.parent / "tutorial_screenshot.gd").read_text(encoding="utf-8")
        assert 'Utils.backend_url().ends_with(":8005")' in src
        assert "quit(2)" in src
        assert "Requires the LIVE backend on 8005" not in src

    def test_the_client_refuses_the_players_backend_and_writes_nothing_to_disk(self):
        src = CLIENT.read_text(encoding="utf-8")
        assert 'Utils.backend_url().ends_with(":8005")' in src
        assert "UiSettings._cfg = ConfigFile.new()" in src
        assert 'settings_class.set("_persist", false)' in src
        # A FIRST launch: no latch is pre-set (the scale card, the parser
        # hint and the tutor are as a new player has them).
        # Row PW (November 18, 2026): `DD_B_UI_SCALE=<scale>` stands the run at
        # a RETURNING player's stored scale (the player who found the oversized
        # war window plays at 1.8) — inside that arm, and nowhere else, the
        # scale card is acknowledged as his settings file has it. With the
        # variable unset the launch is a first launch, as before.
        arm_at = src.index("if own_scale.is_valid_float():")
        arm = src[arm_at:src.index("_run.call_deferred()", arm_at)]
        first_launch = src.replace(arm, "")
        assert 'var own_scale := OS.get_environment("DD_B_UI_SCALE")' in src
        assert '"scale_acknowledged", true' in arm
        for latch in ("scale_acknowledged", "hint_seen", '"tutorial", "done"'):
            assert latch not in first_launch, latch
        for latch in ("hint_seen", '"tutorial", "done"'):
            assert latch not in arm, latch

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


class TestTheAnswerChain:
    """FUN-2b (the commit hook's engine lane): a walk is not one road, and on
    one of them a cornered general's choice stands — the chain answers it,
    and never passes over a plain answer for it."""

    @staticmethod
    def _state(*faces: str, floor: int = 100) -> dict:
        return {"modal_floor": floor,
                "buttons": [{"text": f, "layer": 110, "rect": [0, 0, 10, 10]} for f in faces]}

    def test_a_cornered_generals_choice_is_answered_with_the_first(self):
        pick, _ = _pick_answer(self._state("Fight to the Last", "Attempt a Breakout"))
        assert pick is not None and pick["text"] == "Fight to the Last"

    def test_a_plain_answer_still_comes_first(self):
        pick, _ = _pick_answer(self._state("Fight to the Last", "Continue"))
        assert pick["text"] == "Continue"

    def test_a_name_heading_a_stack_is_found_on_the_map(self):
        state = {"map": [{"text": "Napoleon · 2 more"}, {"text": "Mack · 1 more", "rect": [1, 2, 3, 4]},
                         {"text": "Mackenzie"}]}
        assert _map_label(state, "Mack")["text"] == "Mack · 1 more"
        assert _map_label({"map": [{"text": "Mack"}]}, "Mack")["text"] == "Mack"
        assert _map_label({"map": [{"text": "Mackenzie"}]}, "Mack") is None

    def test_no_answer_below_the_floor(self):
        pick, live = _pick_answer({"modal_floor": 120, "buttons": [
            {"text": "Continue", "layer": 110, "rect": [0, 0, 10, 10]}]})
        assert pick is None and live == []


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

    def test_the_musters_standing_line_is_not_a_board_refusal(self, tmp_path):
        """S14e (October 24, 2026): "Standing modifiers, already in the band:"
        rides every executed attack's muster; `already in` read nine fought
        battles of the conquest road as board refusals. A true "already in"
        refusal still reads as one."""
        run = self._run(tmp_path, [
            ("Ney, attack Mack", "attack Ney",
             {"success": True, "message": "MUSTER — Ney (21,725) vs Mack at Munich — the balance of force "
                                          "looks favorable.\n  WILL NOT — Davout: has already marched this turn\n"
                                          "  Standing modifiers, already in the band: the ground favors the "
                                          "defender (+25%, mountains).\nNey engages in solid combat. Ney gains "
                                          "the advantage over Mack. ⚔"}),
            ("Ney, form square", "other: form square",
             {"success": False, "message": "Ney is already in square formation."}),
            ("Ney, fortify", "fortify Ney",
             {"success": False, "message": "Ney is already in square formation."}),
        ])
        classes = [r["class"] for r in P.judge_run(run)["rows"]]
        assert classes == ["as_meant", "unjudged_other", "board_refusal"]

    def test_a_line_the_engine_never_sent_is_not_judged(self, tmp_path):
        """S14e (October 24, 2026): a line typed under a modal never reaches
        the game (`_act_type` refuses: "the command line is not taking orders
        now"); twelve such lines of the conquest road read as shrugs and
        honest refusals. They are listed apart, never classified."""
        run = self._run(tmp_path, [
            ("what if Massena attacks Kutuzov", "question", {"success": True, "message": "Were you to…"}),
            ("Davout, move to Vienna", "move Davout", None),
        ])
        st = run / "state" / "0002.json"
        rec = json.loads(st.read_text(encoding="utf-8"))
        rec.update({"ok": False, "error": "the command line is not taking orders now (it is disabled)",
                    "open": {"popups": ["incoming_proposal", "war_status_panel (not modal)"]}})
        rec.pop("reply", None)
        st.write_text(json.dumps(rec), encoding="utf-8")
        out = P.judge_run(run)
        assert out["lines"] == 1 and [r["class"] for r in out["rows"]] == ["answered"]
        assert out["n_unsent"] == 1
        assert out["unsent"][0]["n"] == 2 and out["unsent"][0]["popups"] == ["incoming_proposal"]
        assert out["p1"] == []

    def test_a_halt_meant_as_a_hold_is_the_march_cancelled(self, tmp_path):
        """S14e (October 24, 2026): the sea road's one judged P1 — "Murat,
        halt" (meant hold, the nearest family) answered "halts his march and
        awaits new orders": the march cancelled, as the player wanted."""
        run = self._run(tmp_path, [
            ("Murat, halt", "hold Murat",
             {"success": True, "message": "Murat halts his march and awaits new orders."}),
        ])
        assert [r["class"] for r in P.judge_run(run)["rows"]] == ["as_meant"]

    def test_a_support_halted_at_the_approach_is_the_support_meant(self, tmp_path):
        """The diplomacy road's one false misread (S13)."""
        run = self._run(tmp_path, [
            ("Soult, support Ney", "support Soult",
             {"success": True, "message": "Soult reaches the approach to Swabia, but Mack's forces hold it."}),
        ])
        assert [r["class"] for r in P.judge_run(run)["rows"]] == ["as_meant"]


# ── the driven test: a player's hands on the real client ───────────────────

def _act(run: pathlib.Path, action: str, meant: str = "") -> dict:
    argv = ["act", "--out", str(run)] + (["--meant", meant] if meant else []) + [action]
    code = P.main(argv)
    assert code == 0, f"{action}: act returned {code}"
    n = P._next_n(run) - 1
    return json.loads((run / "state" / f"{n:04d}.json").read_text(encoding="utf-8"))


def _modal(state: dict) -> list:
    return [p for p in state.get("open", {}).get("popups", []) if "(not modal)" not in p]


# (FUN-2b, the commit hook's engine lane, November 27, 2026: a walk on the
# historical seed is not one road — the same code took Archduke Charles to
# Milan on turn 2 in one run and to Franconia in the next — and on the Milan
# road the Italian contingent's Teulie is cornered: "Fight to the Last /
# Attempt a Breakout". The chain answers it as the playtest driver's default
# policy does (`last_stand: first`), the first choice; a choice is the LAST
# word tried, so no plain answer is ever passed over for it.)
_ANSWERS = ("continue", "close", "dismiss", "acknowledge", "ok", "later", "proceed", "insist",
            "fight to the last")


def _pick_answer(state: dict) -> tuple:
    """(the button, the live buttons): the first answering button above the
    modal floor, by the words of `_ANSWERS` in their order — the one pick of
    `_answer_chain` and `_answer_chain_step`."""
    floor = int(state.get("modal_floor", -10**6))
    live = [b for b in state.get("buttons", [])
            if int(b["layer"]) >= floor and not b.get("disabled") and b.get("kind") != "slider"]
    for word in _ANSWERS:
        pick = next((b for b in live if b["text"].strip().lower().startswith(word)), None)
        if pick:
            return pick, live
    return None, live


def _answer_chain(run: pathlib.Path, state: dict, answered: list, limit: int = 14) -> dict:
    """Answer the modals until none stands, as a player would: the first
    answering button above the modal floor, pressed by a real click."""
    for _ in range(limit):
        modal = _modal(state)
        if not modal and state.get("scene") == "main":
            return state
        pick, live = _pick_answer(state)
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


def _a_window_stays() -> bool:
    """OC-X5 (row OC, November 18, 2026 — OC-X3's sibling in the pins' own
    gate): an engine starting or exiting in a sibling lane reads as a window
    for an instant, and the driven pins skipped on it (nine skips in a loaded
    hook run; a skip is not a pass). A window counts only if it is still
    there after three re-reads, two seconds apart."""
    for _ in range(3):
        time.sleep(2)
        if not P._godot_running(True):
            return False
    return True


@pytest.fixture(scope="module")
def played(tmp_path_factory) -> dict:
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, and a skip is not a pass")
    # A headless engine in another lane is no second window (conftest,
    # ENGINE_LANES): only a WINDOW skips the pins, and a skip is not a pass.
    if P._godot_running(windowed_only=True) and _a_window_stays():
        pytest.skip("another Godot window is open — never two at once")
    run = tmp_path_factory.mktemp("dd_b_hands") / "run"
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    log = (run.parent / "start.log").open("w", encoding="utf-8")
    sup = subprocess.Popen([sys.executable, "-X", "utf8", str(PLAY), "start", "--road", "conquest",
                            "--out", str(run), "--godot", engine, "--beside-headless"],
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
        # A stray letter on the line, selected with Ctrl+A: the typed order
        # replaces it, as a player's first key replaces a selection (road 2's
        # tool note: the harness once pressed End first and appended).
        line = states["pin"]["command_line"]["rect"]
        _act(run, f"click_at {int(line[0] + line[2] - 8)} {int(line[1] + line[3] / 2)}")
        states["stray"] = _act(run, "key Q")
        _act(run, "key Ctrl+A")
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


# ── S14G-I1: the settlement table's gold [-][+], on the real client ────────
# (Pre-Deploy S14h part 2, October 26, 2026.) The sea player of DD-B's third
# measure saw the gold line's `[-][+]` in the screen text, could not press it
# by words (the instrument stripped a bracketed link's text to the empty
# string and skipped the control) and clicked a guessed point that missed.
# `fixture table` plays the road to that line from turn 1 — the typed
# "propose common peace with Britain" mounts the whole table (Austria, Britain,
# Russia; the dialogue arrives `propose_on_mount`), each court's "+ Add demand"
# opens its suggestions, "Demand 300 gold from Britain" stages the line —
# and presses the line's `[-]` by words and its `[+]` by a real click at the
# centre the listing gave.

def _start_engine_run(tmp_path_factory, name: str):
    """The instrument started as the `played` fixture starts it -> (run,
    supervisor); the driven pins skip without the engine (a skip is not a pass)."""
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, and a skip is not a pass")
    # A headless engine in another lane is no second window (conftest,
    # ENGINE_LANES): only a WINDOW skips the pins, and a skip is not a pass.
    if P._godot_running(windowed_only=True) and _a_window_stays():
        pytest.skip("another Godot window is open — never two at once")
    run = tmp_path_factory.mktemp(name) / "run"
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    log = (run.parent / "start.log").open("w", encoding="utf-8")
    sup = subprocess.Popen([sys.executable, "-X", "utf8", str(PLAY), "start", "--road", "diplomacy",
                            "--out", str(run), "--godot", engine, "--beside-headless"],
                           cwd=str(REPO), env=env, stdout=log, stderr=subprocess.STDOUT,
                           stdin=subprocess.DEVNULL)
    t0 = time.time()
    while not (run / "state" / "0000.json").is_file():
        assert sup.poll() is None, (run.parent / "start.log").read_text(encoding="utf-8")
        assert time.time() - t0 < 300, "the engine never booted"
        time.sleep(0.5)
    return run, sup


def _stop_engine_run(run: pathlib.Path, sup) -> None:
    """Quit the engine and wait for the supervisor; whatever is still alive is killed."""
    try:
        if sup.poll() is None:
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


def _icons(state: dict, glyph: str = "") -> list:
    return [b for b in state.get("buttons", [])
            if b.get("kind") == "icon" and (not glyph or b.get("glyph") == glyph)]


def _gold_demand(state: dict) -> int:
    """The Britain gold line's figure as the table reads it: "Demanded · 300 gold (yours)"."""
    text = "\n".join(t["text"] for t in state.get("texts", []))
    m = re.search(r"Demanded\s*·\s*(\d[\d,]*)\s*gold", text)
    assert m, "no 'Demanded · N gold' line on the table:\n" + text[:1500]
    return int(m.group(1).replace(",", ""))


def _centre_of(rect) -> tuple:
    return int(rect[0] + rect[2] / 2), int(rect[1] + rect[3] / 2)


@pytest.fixture(scope="module")
def table(tmp_path_factory) -> dict:
    run, sup = _start_engine_run(tmp_path_factory, "dd_b_table")
    states: dict = {}
    try:
        states["looks_right"] = _act(run, "click Looks right")
        states["begin"] = _act(run, "click Begin")
        # The player's road to the table: diplomacy is never typed (the line
        # answers a typed proposal with Berthier's "Matters of state are
        # conducted at the table" and sends nothing) — F1 opens the Cabinet,
        # the court's button its page, "Open Settlement — the whole table" the
        # guided table with its gold line ("Propose Peace" is the bilateral
        # preview, which has no demand lines).
        states["cabinet"] = _act(run, "key F1")
        states["court"] = _act(run, "click Britain")
        # row PW (November 18, 2026): the Cabinet's row says what it does — "Make peace —
        # choose the terms — with Britain, Austria and Russia" (it read "Open Settlement")
        states["opened"] = _act(run, "click Make peace — choose the terms")
        st = states["opened"]
        # Session UI-4 (November 12, 2026), re-ruled consciously: EVERY court is one
        # uniform status row and its words (the demand lines, "+ Add demand") stand
        # behind its name — only the court in focus opens by itself. The player's
        # road opens the courts by name ("Austria ▸", "Britain ▸") before it can
        # add a demand.
        def _open_court(st, court_name):
            # (only a CLOSED court: an open one carries its row's "▾" — its card's
            # own head also reads "<court> ▸", and clicking that folded the
            # demand list the walk had just opened)
            if [b for b in st["buttons"] if b["text"].strip() == court_name + " ▾"]:
                return st
            if [b for b in st["buttons"] if b["text"].strip() == court_name + " ▸"]:
                st = _act(run, f"click {court_name} ▸")
                states[court_name.lower() + "_opened"] = st
            return st

        prev = None
        for court_name in ("Austria", "Britain"):
            # Session UI-4: at the shipped 115 % an open court's words fill the
            # scroll and push the next court's row out of view — the player closes
            # the court they worked on (its row's own "▾"), as the accordion asks
            if prev is not None and [b for b in st["buttons"] if b["text"].strip() == prev + " ▾"]:
                st = _act(run, f"click {prev} ▾")
                states[prev.lower() + "_closed"] = st
            st = _open_court(st, court_name)
            for _ in range(3):
                if not [b for b in st["buttons"] if b.get("kind") == "link" and b["text"] == "+ Add demand"]:
                    break
                st = _act(run, "click#1 + Add demand")
            prev = court_name
        # a re-mount closes every court but the one in focus: Britain's words
        # must stand again for its folded options to be clicked
        st = _open_court(st, "Britain")
        # Session UI-4: on the user's panel (800 logical px tall at the derived
        # 1.80) the open court's words run below the body's fold — the player
        # scrolls the table down to its "Demands of Britain" (at one point inside
        # the body, found once on Britain's row)
        anchor = [b for b in st["buttons"] if b["text"].strip().startswith("Britain ")]
        scroll_at = _centre_of(anchor[0]["rect"]) if anchor else None
        if scroll_at is not None:
            for _ in range(8):
                if [b for b in st["buttons"] if "Demands of Britain" in b["text"]]:
                    break
                st = _act(run, f"scroll {scroll_at[0]} {scroll_at[1]} down 3")
        states["expanded"] = st
        # the expansion folds each court's options under "▸ Demands of <court> (N)"
        st = _act(run, "click Demands of Britain")

        def _gold_rows(state: dict) -> list:
            return [b["text"].strip() for b in state["buttons"] if b.get("kind") == "link"
                    and re.fullmatch(r"Demand \d[\d,]* gold from Britain", b["text"].strip())]

        # row PW (November 18, 2026): the table's head and its lead stand two
        # lines taller (the change line's row, the caption on the number), so
        # the opened options may stand under the body's fold — the player
        # scrolls to them
        if scroll_at is not None:
            for _ in range(6):
                if _gold_rows(st):
                    break
                st = _act(run, f"scroll {scroll_at[0]} {scroll_at[1]} down 3")
        states["demands"] = st
        gold = _gold_rows(st)
        assert gold, [b["text"] for b in st["buttons"] if b.get("kind") == "link"]
        states["staged"] = _act(run, f"click {gold[0]}")
        # Session UI-4: the staged gold line stands under Britain's open card,
        # below the body's fold on the user's panel — the player scrolls to it
        if scroll_at is not None:
            st = states["staged"]
            for _ in range(6):
                if [i for i in _icons(st, "-") if "gold" in str(i.get("on_line", "")).lower()]:
                    break
                st = _act(run, f"scroll {scroll_at[0]} {scroll_at[1]} down 3")
            states["staged"] = st
        states["minus"] = _act(run, "click - on the Britain gold line")
        plus = (_icons(states["minus"], "+") or [None])[0]
        if plus is not None:
            x, y = _centre_of(plus["rect"])
            states["plus_at"] = [x, y]
            states["plus"] = _act(run, f"click_at {x} {y}")
        _stop_engine_run(run, sup)
    finally:
        _stop_engine_run(run, sup)
    states["dir"] = run
    return states


class TestThePlayersHands:
    def test_a_first_launch_at_5120x1440_and_the_derived_scale(self, played):
        boot = played["boot"]
        assert boot["ok"], boot["error"]
        assert boot["scene"] == "main_menu"
        assert boot["factor"]["physical_size"] == [5120, 1440]
        # Session UI-2 (November 12, 2026): the 32:9 term 0.25 -> 0.45 (the
        # user's approved plan) — 5120x1440 derived 1.60 (logical 3200x900).
        # Session UI-4 (November 12, 2026): 0.45 -> 0.65 after the interim readers
        # found the edge-anchored HUD "tiny and stranded" — 1.80 (logical 2844x800).
        assert boot["ui_scale"]["derived_for_5120x1440"] == 1.8
        assert boot["ui_scale"]["window"] == 1.8
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
        assert played["stray"]["command_line"]["text"] == "q"
        s = played["end_turn"]
        assert s["ok"], s["error"]
        assert "own road" not in s["note"], s["note"]
        assert s["typed"] == "end turn", "the selection is replaced, not appended to"
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
        assert rec["n_actions"] >= 12
        assert rec["n_script_errors"] == 0, rec["script_errors"]
        assert rec["port"] != 8005

    # ── S14G-I1: a bracketed glyph link is a control the player can name ──
    # (Pre-Deploy S14h part 2, October 26, 2026.)

    def test_s14g_i1_the_listing_has_an_icon_arm_for_a_bracketed_glyph_link(self):
        """Non-engine. The sea player of DD-B's third measure could not press
        the settlement table's gold `[-][+]` by words: `dd_b_client.gd` stripped
        a link's bracketed text to the empty string and the control listing
        skipped it. The strip is UNCHANGED (every other link lists as before; an
        image-only link is still skipped) and the empty-label arm now lists a
        bracketed GLYPH link as an icon before it skips."""
        src = CLIENT.read_text(encoding="utf-8")
        strip = ('var label := _tag_re.sub(_img_re.sub(m.get_string(2), "", true), "", true)'
                 '.replace("\\u00A0", " ").strip_edges()')
        assert strip in src, "the link-label strip must stay byte-identical"
        arm = src.split(strip, 1)[1].split("var link := base.duplicate()", 1)[0]
        assert 'if label == "":' in arm
        assert "_glyph_of(m.get_string(2))" in arm and "_icon_link(rtl, base, vis, m, glyph)" in arm
        assert arm.rstrip().endswith("continue"), "an image-only or empty link is still skipped"
        # the icon: kind, no text, the glyph, the line, a measured rect
        for needle in ('icon["kind"] = "icon"', 'icon["text"] = ""', 'icon["glyph"] = glyph',
                       'icon["on_line"] = str(where.get("on_line", ""))',
                       'icon["rect"] = _r(where["rect"])',
                       'icon["meta_value"] = meta if meta != "" else m.get_string(2)'):
            assert needle in src, needle
        # a link is measured the way the label lays it out (no rect API exists)
        for needle in ('rtl.call("get_character_line", idx)', "font.get_string_size(",
                       "rtl.get_line_offset(line)", "rtl.get_v_scroll_bar().value if rtl.scroll_active",
                       'scratch.get_parsed_text().replace("\\u00A0", " ").length()'):
            assert needle in src, needle

    def test_s14g_i1_click_names_the_icon_before_a_text_that_merely_holds_a_plus(self):
        """Non-engine. `click +` must reach the `[+]` icon even where "+ Add
        demand" is on screen (its text HOLDS a plus): the icons are their own
        tier between the exact text and the contained one, and the click of an
        icon is the link's own meta_clicked road."""
        src = CLIENT.read_text(encoding="utf-8")
        assert "var tiers := [[], [], [], []]" in src
        exact = src.index("tiers[0].append(c)")
        icon = src.index("_icon_matches(c, want)")
        held = src.index("t.find(want) >= 0")
        tooltip = src.index("tiers[3].append(c)")
        assert exact < icon < held < tooltip
        assert 'str(c["kind"]) == "link" or str(c["kind"]) == "icon"' in src
        assert "rtl.meta_clicked.emit" in src.split('str(c["kind"]) == "link" or str(c["kind"]) == "icon"', 1)[1][:200]

    def test_s14g_i1_the_glyph_patterns_take_a_symbol_and_never_a_tag(self):
        """Non-engine. The instrument's own patterns, read from the source and
        compiled here: a glyph is one to three symbols in brackets (no letter,
        no digit); a named tag is never one."""
        src = CLIENT.read_text(encoding="utf-8")

        def pattern(name: str):
            m = re.search(r'var %s := RegEx\.create_from_string\("((?:[^"\\]|\\.)*)"\)' % name, src)
            assert m, name
            return re.compile(m.group(1).replace("\\\\", "\\"))

        glyph = pattern("_glyph_re")
        for text, want in (("[+]", "+"), ("[-]", "-"), ("[−]", "−"), ("[×]", "×"),
                           ("[▲]", "▲")):
            m = glyph.search(text)
            assert m and m.group(1) == want, text
        for text in ("[b]", "[Esc]", "[color=#fff]", "[1]", "[/url]", "[]", "[++++]", "+", "Britain [+]"):
            assert glyph.search(text) is None, text
        # a glyph wrapped in styling tags still reads as the glyph
        tag = pattern("_bbtag_re")
        assert glyph.search(tag.sub("", "[color=#e0a040][+][/color]")).group(1) == "+"
        assert tag.sub("", "[b]x[/b]") == "x"
        # a line's own words lose their glyphs; its heading loses its bullet
        every = pattern("_glyph_any_re")
        assert re.sub(r"\s+", " ", every.sub("", "Demanded · 300 gold (yours)  [-][+]  Remove")).strip() \
            == "Demanded · 300 gold (yours) Remove"
        lead = pattern("_lead_sym_re")
        assert lead.sub("", "  * Britain ▸ - Holding out").lstrip() == "Britain ▸ - Holding out"

    def test_s14g_i1_the_player_side_reads_an_icon_as_its_glyph_its_line_and_its_place(self, tmp_path):
        """Non-engine. The summary prints an icon as `[icon: + <line> @(x,y)]`
        — the glyph, the line it stands on and its centre — beside the
        controls it printed before."""
        icon = {"kind": "icon", "text": "", "glyph": "+", "tooltip": "", "disabled": False,
                "on_line": "Britain · Demanded · 300 gold (yours)",
                "rect": [1580, 366, 22, 18], "layer": 110, "surface": "ProposalConfirmPopup"}
        assert P._button_label(icon) == "[icon: + Britain · Demanded · 300 gold (yours) @(1591,375)]"
        bare = dict(icon, on_line="")
        assert P._button_label(bare) == "[icon: + @(1591,375)]"
        # the other kinds print as they did
        assert P._button_label({"kind": "link", "text": "Remove", "rect": [0, 0, 4, 4]}) == "<Remove>"
        assert P._button_label({"kind": "button", "text": "Back Out", "rect": [0, 0, 4, 4]}) == "[Back Out]"
        assert P._button_label({"kind": "button", "text": "", "tooltip": "Menu", "rect": [0, 0, 4, 4]}) \
            == "[icon: Menu @(2,2)]"
        run = tmp_path / "run"
        (run / "state").mkdir(parents=True)
        (run / "state" / "0001.json").write_text(json.dumps({
            "n": 1, "action": "look", "ok": True, "turn": "Turn 1", "factor": {}, "open": {},
            "surfaces": [{"name": "ProposalConfirmPopup", "layer": 110, "lines": ["The table"],
                          "buttons": [icon, dict(icon, glyph="-", rect=[1558, 366, 22, 18]),
                                      {"kind": "link", "text": "Remove", "rect": [1620, 366, 40, 18],
                                       "disabled": False}]}]}), encoding="utf-8")
        text = P.summary(run, 1, live=False)
        assert "[icon: + Britain · Demanded · 300 gold (yours) @(1591,375)]  " \
               "[icon: - Britain · Demanded · 300 gold (yours) @(1569,375)]  <Remove>" in text

    def test_s14g_i1_the_gold_line_lists_its_two_glyphs_as_icons_with_a_place(self, table):
        """Engine. The Britain gold line on the real client: `[-]` and `[+]`
        are listed (they were not), each with its glyph, the line it stands on
        (the court's name, the line's words) and a rect that lies on the
        table's text — the `[+]` to the right of the `[-]` on the same line —
        and the controls the table listed before are still listed."""
        opened = table["opened"]
        assert opened["ok"], opened["error"]
        assert "proposal_confirm" in _modal(opened), (opened["open"], opened.get("reply"))
        staged = table["staged"]
        assert staged["ok"], staged["error"]
        icons = _icons(staged)
        assert sorted(b["glyph"] for b in icons) == ["+", "-"], [b["text"] for b in staged["buttons"]]
        minus, plus = _icons(staged, "-")[0], _icons(staged, "+")[0]
        for b in (minus, plus):
            assert b["text"] == "" and b["placed"] is True, b
            line = b["on_line"].lower()
            assert "britain" in line and "gold" in line, b["on_line"]
            assert b["rect"][2] >= 8 and b["rect"][3] >= 8, b
        assert plus["rect"][0] > minus["rect"][0], "the [+] stands right of the [-]"
        assert abs(plus["rect"][1] - minus["rect"][1]) <= 2, "both stand on the one line"
        rows = [t for t in staged["texts"] if "Demanded" in t["text"] and "gold" in t["text"]]
        assert rows, [t["text"][:80] for t in staged["texts"]]
        for b in (minus, plus):
            cx, cy = _centre_of(b["rect"])
            assert any(r["rect"][0] <= cx <= r["rect"][0] + r["rect"][2]
                       and r["rect"][1] <= cy <= r["rect"][1] + r["rect"][3] for r in rows),                 (b["rect"], [r["rect"] for r in rows])
        links = [b["text"] for b in staged["buttons"] if b.get("kind") == "link"]
        assert "Remove" in links and any(t.endswith("Add demand") for t in links), links

    def test_s14g_i1_click_by_words_and_click_at_its_centre_both_reach_the_glyph(self, table):
        """Engine. `click - on the Britain gold line` names the `[-]` by the
        glyph and the line's words and presses it by the link's own road: the
        figure falls by the step (100). The `[+]`'s centre, as the listing gave
        it, then takes a REAL click and the figure rises back — the sea
        player's guessed (1758, 530) missed; the listed centre does not."""
        staged, minus, plus = table["staged"], table["minus"], table.get("plus")
        before = _gold_demand(staged)
        assert before == 300, before
        assert minus["ok"], minus["error"]
        assert "meta_clicked" in minus["note"], minus["note"]
        assert minus["pressed"]["kind"] == "icon" and minus["pressed"]["glyph"] == "-"
        after_minus = _gold_demand(minus)
        assert after_minus == before - 100, (before, after_minus)
        assert plus is not None, "no [+] icon was listed after the [-] was pressed"
        assert plus["ok"], plus["error"]
        assert plus["note"].startswith("clicked at "), plus["note"]
        assert _gold_demand(plus) == after_minus + 100, (after_minus, _gold_demand(plus), table["plus_at"])


# ── the close: the records hold (S13, October 14, 2026) ───────────────────

AUD = REPO / "docs" / "audits" / "dd_b"
ROADS = ("conquest", "diplomacy", "sea")


class TestTheMetricTool:
    """S14e (October 24, 2026): the metric is read off the records by ONE
    tool, `tools/dd_b_metric.py`, which reproduces the first measure's
    committed `metric.json` byte for byte from its `causes.json` and the
    three roads' `rows.json` — so the re-measure's figures come from a
    checked instrument, not a hand."""

    def test_the_first_measure_is_reproduced(self):
        import dd_b_metric as M
        causes = json.loads((AUD / "causes.json").read_text(encoding="utf-8"))
        roads = {road: AUD / road for road in ROADS}
        assert M.check(causes, roads) == []
        got = M.metric(causes, roads)
        want = json.loads((AUD / "metric.json").read_text(encoding="utf-8"))
        assert got == want

    def test_the_check_names_an_orphan_row_and_a_missing_frame(self, tmp_path):
        import dd_b_metric as M
        run = tmp_path / "conquest"
        run.mkdir()
        (run / "rows.json").write_text(json.dumps([{"id": 1}, {"id": 2}]), encoding="utf-8")
        (run / "run.json").write_text(json.dumps({"turn_number": 21}), encoding="utf-8")
        causes = {"causes": [{"id": "X-1", "sightings": [
            {"road": "conquest", "row": 1, "severity": "P2", "frame": "no/such/frame.jpg"}]}],
            "struck": []}
        problems = M.check(causes, {"conquest": run})
        assert any("row 2 is neither" in p for p in problems)
        assert any("not in the repository" in p for p in problems)
        m = M.metric(causes, {"conquest": run})
        assert m["per_road"]["conquest"] == {"turns": 20, "rows": 1, "by_severity": {"P1": 0, "P2": 1, "P3": 0},
                                             "per_10_turns": 0.5, "player_rows_filed": 2,
                                             "player_rows_struck": 0}
        assert m["across"]["done_when"] == {"under_5_per_10": True, "zero_p1": True}
        assert m["done_when_met"] is True


class TestTheReMeasureRecords:
    """S14e (October 24, 2026) — DD-B's re-measure on the DD-B instrument:
    three fresh players, the same brief and roads, 20 turns each in the
    client. Its records agree with each other as the first measure's do:
    every player row a sighting of a filed cause (or struck with its reason),
    the metric read off the records by the ONE tool, every cause a tagged
    ledger row whose cited frames are in the repository; and the done-when
    is read as the tool reads it."""

    DATE = "2026_10_24"

    def _causes(self):
        return json.loads((AUD / f"causes_{self.DATE}.json").read_text(encoding="utf-8"))

    def _roads(self):
        return {road: AUD / f"{road}_{self.DATE}" for road in ROADS}

    def test_three_roads_of_twenty_turns_in_the_client(self):
        for road, d in self._roads().items():
            run = json.loads((d / "run.json").read_text(encoding="utf-8"))
            assert run["road"] == road and run["turn_number"] == 21, road
            assert run["n_script_errors"] == 0, road
            assert run["port"] != 8005
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            assert meta["window"] == "5120x1440" and "godot" not in meta
            for name in ("rows.json", "judge.json", "actions.log", "summaries.md", "player_notes.md"):
                assert (d / name).is_file(), (road, name)

    def test_every_player_row_is_a_sighting_or_struck(self):
        import dd_b_metric as M
        assert M.check(self._causes(), self._roads()) == []

    def test_the_metric_is_the_tools_reading_of_the_records(self):
        import dd_b_metric as M
        rec = self._causes()
        metric = json.loads((AUD / f"metric_{self.DATE}.json").read_text(encoding="utf-8"))
        assert metric == M.metric(rec, self._roads())
        across = metric["across"]
        assert across["turns"] == 60
        assert across["rows"] == len(rec["causes"])
        assert across["per_10_turns"] == round(len(rec["causes"]) / 6, 1)
        assert metric["done_when_met"] == (across["per_10_turns"] < 5 and across["by_severity"]["P1"] == 0)

    def test_the_judge_read_every_sent_line_and_found_no_p1(self):
        for road, d in self._roads().items():
            judge = json.loads((d / "judge.json").read_text(encoding="utf-8"))
            assert judge["p1"] == [], road
            assert judge["lines"] == len(judge["rows"])
            assert all(r["class"] != "" for r in judge["rows"])
            for u in judge.get("unsent", []):
                assert "not taking orders" in u["error"], (road, u)

    def test_every_cause_is_a_tagged_ledger_row_with_its_frames(self):
        rec = self._causes()
        bugs = doc_text("BUG_FIXES.md")
        design = doc_text("DESIGN_REFINEMENT.md")
        for c in rec["causes"]:
            line = next(ln for ln in bugs.splitlines() if ln.startswith(f"| **{c['id']}** |"))
            assert "⟨SF step=pre-deploy S14e · DD-B re-measure · pillar=" in line, c["id"]
            assert f"pillar={c['pillar']}⟩" in line, c["id"]
            if c.get("dr_id"):
                assert any(ln.startswith(f"| **{c['dr_id']}** |") for ln in design.splitlines()), c["dr_id"]
            for s in c["sightings"]:
                assert (REPO / s["frame"]).is_file(), s["frame"]
                assert s["frame"] in line, (c["id"], s["frame"])


class TestTheThirdMeasureRecords:
    """S14g (October 25–26, 2026) — DD-B's third measure on the DD-B instrument:
    three fresh players, the same brief and roads, 20 turns each in the client,
    on the build the testers will get (master a47bc116). Its records agree with
    each other as the second measure's do: every player row a sighting of a filed
    cause (or struck with its reason), the metric read off the records by the ONE
    tool, every cause a tagged ledger row whose cited frames are in the
    repository, every design half a ruled-for row; and the done-when is read as
    the tool reads it: 33 causes in 60 turns = 5.5 per 10 turns, no P1 — met on
    the P1 bar, NOT met on the rate."""

    DATE = "2026_10_25"
    TAG = "⟨SF step=pre-deploy S14g · DD-B third measure · pillar="

    def _causes(self):
        return json.loads((AUD / f"causes_{self.DATE}.json").read_text(encoding="utf-8"))

    def _roads(self):
        return {road: AUD / f"{road}_{self.DATE}" for road in ROADS}

    def test_three_roads_of_twenty_turns_in_the_client(self):
        for road, d in self._roads().items():
            run = json.loads((d / "run.json").read_text(encoding="utf-8"))
            assert run["road"] == road and run["turn_number"] == 21, road
            assert run["n_script_errors"] == 0, road
            assert run["port"] != 8005
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            assert meta["window"] == "5120x1440" and "godot" not in meta
            for name in ("rows.json", "judge.json", "actions.log", "summaries.md", "player_notes.md"):
                assert (d / name).is_file(), (road, name)

    def test_every_player_row_is_a_sighting_or_struck(self):
        import dd_b_metric as M
        assert M.check(self._causes(), self._roads()) == []

    def test_the_metric_is_the_tools_reading_of_the_records(self):
        import dd_b_metric as M
        rec = self._causes()
        metric = json.loads((AUD / f"metric_{self.DATE}.json").read_text(encoding="utf-8"))
        assert metric == M.metric(rec, self._roads())
        across = metric["across"]
        assert across["turns"] == 60
        assert across["rows"] == len(rec["causes"]) == 33
        assert across["by_severity"] == {"P1": 0, "P2": 12, "P3": 21}
        assert across["per_10_turns"] == round(33 / 6, 1) == 5.5
        assert across["done_when"] == {"under_5_per_10": False, "zero_p1": True}
        assert metric["done_when_met"] is False
        assert {r: metric["per_road"][r]["rows"] for r in ROADS} == {"conquest": 12, "diplomacy": 15, "sea": 9}
        assert {r: metric["per_road"][r]["player_rows_filed"] for r in ROADS} == {"conquest": 12, "diplomacy": 16, "sea": 9}

    def test_the_causes_classes_are_counted(self):
        rec = self._causes()["causes"]
        fam = collections.Counter(c["family"] for c in rec)
        kinds = collections.Counter(c["prior_kind"] for c in rec)
        assert (fam[1], fam[2], fam[3]) == (13, 11, 9)
        assert (kinds["partial_return"], kinds["sibling"], kinds["new"]) == (9, 18, 6)
        # none of the second measure's 35 rows returned as filed; five came back in part
        back = {pid for c in rec if c["prior_kind"] == "partial_return" for pid in c["prior_ids"]
                if re.fullmatch(r"S14E-\d+", pid)}
        assert back >= {"S14E-11", "S14E-13", "S14E-15", "S14E-17", "S14E-18"}

    def test_the_judge_read_every_sent_line_and_found_no_p1(self):
        for road, d in self._roads().items():
            judge = json.loads((d / "judge.json").read_text(encoding="utf-8"))
            assert judge["p1"] == [], road
            assert judge["lines"] == len(judge["rows"])
            assert all(r["class"] != "" for r in judge["rows"])
            for u in judge.get("unsent", []):
                assert "not taking orders" in u["error"], (road, u)

    def test_a_repeat_of_a_standing_order_is_the_board_declining_not_a_misread(self):
        """The sea road's one P1 proxy (action 187): "Davout, march to Lorraine" typed a
        second time answers "Davout is already carrying out that order. No change." —
        free, `strategic_executor.py:1040`. A SEPARATE shape, read after the action
        words fail, so the second measure's multi-line group order that carries the
        phrase beside "begins march" keeps reading `as_meant`."""
        import unrehearsed_census as U
        said = "Davout is already carrying out that order. No change."
        assert U.classify_order({"action": "move", "marshal": "Davout"}, {"message": said, "success": True}) == "board_refusal"
        group = ("The Grand Quartier Général carries the Emperor's order — 2 actions, the whole column: 6 corps "
                 "within 2 provinces of the Emperor, 'march to Frankfurt'.\nNey: Ney begins march to Frankfurt.\n"
                 "Davout: Davout is already carrying out that order.\nLannes: Lannes begins march to Frankfurt.")
        assert U.classify_order({"action": "move", "marshal": ""}, {"message": group, "success": True}) == "as_meant"

    def test_every_cause_is_a_tagged_ledger_row_with_its_frames(self):
        rec = self._causes()
        bugs = doc_text("BUG_FIXES.md")
        design = doc_text("DESIGN_REFINEMENT.md")
        for c in rec["causes"]:
            line = next(ln for ln in bugs.splitlines() if ln.startswith(f"| **{c['id']}** |"))
            assert self.TAG in line, c["id"]
            assert f"pillar={c['pillar']}⟩" in line, c["id"]
            # S14h part 1 (October 26, 2026): the twelve P2s read FIXED by the part;
            # the P3s stay OPEN until part 2 closes them.
            assert ("OPEN — owner S14h" in line
                    or "✅ FIXED October 26, 2026 — S14h part 1" in line
                    or "✅ FIXED October 26, 2026 — S14h part 2" in line), c["id"]
            assert f"tests/test_s14h_the_third_measure_rows.py::Test{c['id'].replace('-', '')}" in line, c["id"]
            if c.get("dr_id"):
                assert any(ln.startswith(f"| **{c['dr_id']}** |") for ln in design.splitlines()), c["dr_id"]
                assert c["dr_id"] in line, c["id"]
            for s in c["sightings"]:
                assert (REPO / s["frame"]).is_file(), s["frame"]
                assert s["frame"] in line, (c["id"], s["frame"])
        # the instrument row and the done-when's own question
        # S14h part 2 (October 26, 2026): the instrument row reads FIXED by the part.
        assert any(ln.startswith("| **S14G-I1** |")
                   and ("OPEN — owner S14h" in ln
                        or "✅ FIXED October 26, 2026 — S14h part 2" in ln)
                   for ln in bugs.splitlines())
        assert any(ln.startswith("| **S14G-D7** |") for ln in design.splitlines())

    def test_the_six_design_halves_and_the_done_whens_question_are_filed(self):
        rec = self._causes()["causes"]
        ids = sorted(c["dr_id"] for c in rec if c.get("dr_id"))
        assert ids == ["S14G-D1", "S14G-D2", "S14G-D3", "S14G-D4", "S14G-D5", "S14G-D6"]
        design = doc_text("DESIGN_REFINEMENT.md")
        for d in ids + ["S14G-D7"]:
            row = next(ln for ln in design.splitlines() if ln.startswith(f"| **{d}** |"))
            assert "**Recommendation:**" in row, d
            assert "S14h" in row, d

    def test_the_rulings_are_recorded_as_recommended(self):
        """October 26, 2026, the user under the standing delegation: "Take S14G-D1 … D7 as
        recommended"; S14h builds D1, D2, D3, D6 in part 1 and D4, D5 in part 2; D7 is closed."""
        design = doc_text("DESIGN_REFINEMENT.md")
        rows = {ln.split("**")[1]: ln for ln in design.splitlines() if ln.startswith("| **S14G-D")}
        part = {"D1": 1, "D2": 1, "D3": 1, "D6": 1, "D4": 2, "D5": 2}
        for k, n in part.items():
            row = rows[f"S14G-{k}"]
            if n == 1:
                # S14h part 1 (October 26, 2026) built D1, D2, D3 and D6 as recommended.
                assert "**BUILT October 26, 2026 — S14h part 1, as recommended" in row, k
            else:
                # S14h part 2 (October 26, 2026) built D4 and D5 as recommended.
                assert "**BUILT October 26, 2026 — S14h part 2, as recommended" in row, k
            assert f"TestS14G{k}" in row, k
        assert "✅ RULED as recommended on October 26, 2026" in rows["S14G-D7"]
        assert "no fourth measure runs before the deploy" in rows["S14G-D7"]

    def test_the_plan_homes_the_rows_and_the_write_up_states_the_verdict(self):
        plan = doc_text("PRE_DEPLOY_PLAN.md")
        for row in ("| S14g ", "| S14h "):
            assert row in plan, row
        text = (REPO / "docs" / "audits" / f"DD_B_THIRD_MEASURE_{self.DATE}.md").read_text(encoding="utf-8")
        assert "33 causes" in text and "5.5 rows per 10 turns" in text
        assert "NOT met on the rate" in text and "met on the P1 bar" in text
        assert "S14h" in text


class TestTheRecords:
    """DD-B's committed records agree with each other: every player row is a
    sighting of a filed cause (or struck with its reason), the metric is the
    count of the causes, and every cause is a tagged ledger row whose cited
    frames are in the repository."""

    def _causes(self):
        return json.loads((AUD / "causes.json").read_text(encoding="utf-8"))

    def test_every_player_row_is_a_sighting_or_struck(self):
        rec = self._causes()
        sighted = {(s["road"], s["row"]) for c in rec["causes"] for s in c["sightings"]}
        struck = {(s["road"], s["row"]) for s in rec["struck"]}
        for road in ROADS:
            rows = json.loads((AUD / road / "rows.json").read_text(encoding="utf-8"))
            for r in rows:
                assert (road, r["id"]) in sighted | struck, (road, r["id"])
        assert struck == {("conquest", 2)}, "the one instrument artifact, struck with its reason"

    def test_the_metric_is_the_count_of_the_causes(self):
        rec = self._causes()
        metric = json.loads((AUD / "metric.json").read_text(encoding="utf-8"))
        across = metric["across"]
        assert across["rows"] == len(rec["causes"]) == 69
        assert across["by_severity"] == {"P1": 3, "P2": 21, "P3": 45}
        assert across["per_10_turns"] == 11.5
        assert metric["done_when_met"] is False
        for road in ROADS:
            n = sum(1 for c in rec["causes"] if any(s["road"] == road for s in c["sightings"]))
            assert metric["per_road"][road]["rows"] == n

    def test_every_cause_is_a_tagged_ledger_row_with_its_frames(self):
        rec = self._causes()
        bugs = doc_text("BUG_FIXES.md")
        design = doc_text("DESIGN_REFINEMENT.md")
        for c in rec["causes"]:
            text = design if c["id"].startswith("DDB-D") else bugs
            line = next(ln for ln in text.splitlines() if ln.startswith(f"| **{c['id']}** |"))
            assert "⟨SF step=pre-deploy S13 · DD-B · pillar=" in line, c["id"]
            if c.get("dr_id"):
                assert any(ln.startswith(f"| **{c['dr_id']}** |") for ln in design.splitlines()), c["dr_id"]
            for s in c["sightings"]:
                assert (REPO / s["frame"]).is_file(), s["frame"]


# ═══════════════════════════════════════════════════════════════════════════
# Row PW "Plain Words" (November 18, 2026 — the first playtest): the windows
# FIT the first player's own screen and STAND STILL, on the real client
# ═══════════════════════════════════════════════════════════════════════════
# "clicking war detail makes a popup buigger than screen … some screens bobble
# up and down". He plays at Interface Scale 1.8 on a maximised 5120-wide
# window (a logical view of 2844 x 765) — a size no measure had stood at. The
# instrument stands the run there (`DD_B_UI_SCALE`, `DD_B_WINDOW`), and every
# action's record now carries what reaches PAST THE SCREEN (`off_screen`) and
# which window MOVED after it had opened (`settle_moves`). The walk: the war
# card's Make peace, a press on the peace table (the table stays), the war's
# own window, the turn's end and its report.

def _pw_said(state: dict) -> str:
    return " | ".join(str(t.get("text") or "") for t in state.get("texts") or [])


def _pw_buttons(state: dict) -> list:
    return [str(b.get("text") or "") for b in state.get("buttons") or []]


def _pw_panel_moves(state: dict) -> list:
    """A WINDOW that moved after it had opened (a list inside it coming to
    rest on a whole line — `Utils.keep_whole_lines`, UXR3-F3 — is not one)."""
    return [m for m in state.get("settle_moves") or [] if str(m.get("what", "")).startswith("panel ")]


@pytest.fixture(scope="module")
def pw_walk(tmp_path_factory) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        run, sup = _start_engine_run(tmp_path_factory, "pw_fit")
    states: dict = {}
    try:
        states["boot"] = json.loads((run / "state" / "0000.json").read_text(encoding="utf-8"))
        states["begin"] = _act(run, "click Begin")
        states["table"] = _act(run, "click Make peace")
        states["offer"] = _act(run, "click Offer them more")
        states["offer_again"] = _act(run, "click Offer them more")
        states["ask"] = _act(run, "click Ask for more")
        states["cancel"] = _act(run, "click Cancel")
        states["war_window"] = _act(run, "click War with the Third Coalition")
        states["esc"] = _act(run, "key Escape")
        states["end_turn"] = _act(run, "click End Turn", meant="end_turn")
        states["continue"] = _act(run, "click Continue") if "enemy_phase" in " ".join(_modal(states["end_turn"])) \
            else states["end_turn"]
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    states["run_dir"] = str(run)
    return states


class TestRowPWTheWindowsFitAndStandStill:

    def test_the_run_stands_at_the_first_players_own_setup(self, pw_walk):
        boot = pw_walk["boot"]
        assert float(boot["ui_scale"]["at_boot"]) == 1.8
        assert boot["factor"]["physical_size"] == [5120, 1377]
        logical = boot["factor"]["logical_size"]
        assert [round(float(logical[0])), round(float(logical[1]))] == [2844, 765], logical
        assert pw_walk["run"]["n_script_errors"] == 0, pw_walk["run"]["script_errors"]

    def test_nothing_reaches_past_the_screen(self, pw_walk):
        past = {name: state.get("off_screen") for name, state in pw_walk.items()
                if isinstance(state, dict) and state.get("off_screen")}
        assert past == {}, past

    def test_no_window_moves_once_it_has_opened(self, pw_walk):
        moved = {name: _pw_panel_moves(state) for name, state in pw_walk.items()
                 if isinstance(state, dict) and _pw_panel_moves(state)}
        assert moved == {}, moved

    def test_the_war_card_ends_the_war_in_one_press(self, pw_walk):
        assert "Make peace" in _pw_buttons(pw_walk["begin"])
        table = pw_walk["table"]
        assert any("proposal_confirm" in p for p in _modal(table))
        said = _pw_said(table)
        assert "THIS DEAL" in said and "You get:" in said and "You give:" in said
        assert "They will not sign yet" in said or "They will sign" in said
        for face in ("Ask for more", "Offer them more", "Review and sign", "Cancel"):
            assert any(b.split("\n", 1)[0] == face for b in _pw_buttons(table)), face

    def test_a_dial_wears_what_its_next_press_does(self, pw_walk):
        """PW-X13 (the blind reading): the face's second line, before any press."""
        faces = {b.split("\n", 1)[0]: b for b in _pw_buttons(pw_walk["table"])}
        for name in ("Ask for more", "Offer them more"):
            lines = faces[name].split("\n")
            assert len(lines) == 2 and "gold" in lines[1], faces[name]
        assert faces["Offer them more"].split("\n")[1] == "you pay each court 100 more gold"
        # row PW part 2: and the review wears what it will find
        assert faces["Review and sign"].split("\n")[1] in ("they will not sign it yet", "they would all sign")

    def test_the_peace_table_stands_still_under_a_dial(self, pw_walk):
        """PW-X12: measured frame by frame, the rail stood in two rows for two
        frames under every press and the list's height swung 78 px and back.
        Nothing of the table moves now — not as it opens, not under a press."""
        for name in ("table", "offer", "offer_again", "ask"):
            moved = [m for m in pw_walk[name].get("settle_moves") or []
                     if "ProposalConfirmPopup" in str(m.get("what", ""))]
            assert moved == [], (name, moved)

    def test_the_table_stays_through_a_press_and_says_what_changed(self, pw_walk):
        offer = pw_walk["offer"]
        assert any("proposal_confirm" in p for p in _modal(offer)), "the table left the screen on a press"
        said = _pw_said(offer)
        assert "Changed: " in said or "Nothing changed — " in said, said[:600]
        assert not any("proposal_confirm" in p for p in _modal(pw_walk["cancel"]))

    def test_the_wars_window_leads_with_make_peace(self, pw_walk):
        war = pw_walk["war_window"]
        assert any("war_detail" in p for p in war["open"]["popups"])
        buttons = _pw_buttons(war)
        assert any(b.startswith("Make peace") for b in buttons), buttons
        assert "Open Settlement" not in buttons and "Negotiate Peace" not in buttons

    def test_the_turns_report_opens_on_what_changed_for_the_player(self, pw_walk):
        end = pw_walk["end_turn"]
        assert end["ok"], end.get("error")
        if any("enemy_phase" in p for p in _modal(end)):
            said = _pw_said(end)
            assert "THE ENEMY'S MOVES" in said, said[:400]
            assert "Continue" in _pw_buttons(end)


# ═══════════════════════════════════════════════════════════════════════════
# Row PW part 2 (November 18, 2026): THE ENEMY'S MOVES ARE PLAYED ON THE MAP
# ═══════════════════════════════════════════════════════════════════════════
# The user, of the report after End Turn: "can we show the pieces moving or
# something better?" At his own setup the instrument plays as his game does
# (`play_enemy_moves` on): the map tells the turn — the pieces and the fog's
# markers march, the provinces that changed hands take their colour and wear a
# plaque — and THEN the report opens. The settle waits the telling out and
# keeps a frame of each beat (`replay`, `replay_frames`); `endturn_skip`
# presses a key while it runs, as a player who will not wait does.

@pytest.fixture(scope="module")
def pw_skip(tmp_path_factory) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        run, sup = _start_engine_run(tmp_path_factory, "pw_skip")
    states: dict = {}
    try:
        states["begin"] = _act(run, "click Begin")
        # (the part's review) Shift alone must not end the telling; then a real click on the map — on
        # France, clear of every panel — ends it and must pick nothing under the cursor
        states["skip"] = _act(run, "endturn_skip shift click 1330 400", meant="end_turn")
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


class TestRowPWTheEnemysMovesArePlayedOnTheMap:

    def test_the_map_tells_the_turn_and_then_the_report_opens(self, pw_walk):
        end = pw_walk["end_turn"]
        if not any("enemy_phase" in p for p in _modal(end)):
            pytest.skip("a turn of fog alone: one line in the log, nothing to play")
        replay = end.get("replay") or {}
        assert replay.get("ended") is True and replay.get("skipped") is False, replay
        shown = int(replay.get("moved", 0)) + len(replay.get("changed") or []) + len(replay.get("plaques") or [])
        assert shown >= 1, replay
        assert "THE ENEMY'S MOVES" in _pw_said(end), "the report stands once the telling has ended"

    def test_its_plaques_are_the_reports_own_words(self, pw_walk):
        end = pw_walk["end_turn"]
        replay = end.get("replay") or {}
        if not replay.get("plaques"):
            pytest.skip("nothing of the player's changed this turn: no plaque to wear")
        said = _pw_said(end)
        for text in replay["plaques"]:
            place = text.split(" — ", 1)[0]
            assert place in said, (text, said[:500])

    def test_a_frame_of_each_beat_is_kept(self, pw_walk):
        end = pw_walk["end_turn"]
        if not end.get("replay"):
            pytest.skip("no telling this turn")
        frames = end.get("replay_frames") or []
        assert len(frames) == 2, frames
        for rel in frames:
            assert (pathlib.Path(pw_walk["run_dir"]) / rel).is_file(), rel

    def test_nothing_of_the_telling_reaches_past_the_screen_or_is_left_behind(self, pw_walk):
        end = pw_walk["end_turn"]
        assert not end.get("off_screen"), end.get("off_screen")
        left = [s for s in (end.get("surfaces") or []) if "EnemyMoves" in str(s.get("name", ""))]
        assert left == [], "the banner and the plaques are cleared when the report opens"

    def test_a_press_skips_it_and_the_report_opens_at_once(self, pw_skip):
        skip = pw_skip["skip"]
        if "told nothing" in str(skip.get("note", "")):
            pytest.skip("a turn of fog alone: nothing to skip")
        replay = skip.get("replay") or {}
        assert replay.get("skipped") is True and replay.get("ended") is True, (replay, skip.get("note"))
        assert any("enemy_phase" in p for p in _modal(skip)), "the report opened on the press"
        assert pw_skip["run"]["n_script_errors"] == 0, pw_skip["run"]["script_errors"]

    def test_a_modifier_alone_is_no_answer(self, pw_skip):
        """The review (PW2-R11): Shift — or Alt on its way to Alt+Tab, the screenshot key — ended it."""
        skip = pw_skip["skip"]
        if "told nothing" in str(skip.get("note", "")):
            pytest.skip("a turn of fog alone: nothing to skip")
        assert skip.get("shift_left_it_running") is True, skip.get("note")

    def test_the_press_that_skips_it_picks_nothing_on_the_map(self, pw_skip):
        """The review (PW2-R10): the map reads a press before `main._input` ends the telling — the click
        that skipped it also opened the province under the cursor, beneath the report."""
        skip = pw_skip["skip"]
        if "told nothing" in str(skip.get("note", "")):
            pytest.skip("a turn of fog alone: nothing to skip")
        assert skip.get("click_found_it_running") is True, "the click came while the map was telling"
        assert skip["open"]["region_panel"] is False, "the click reached the map: a province panel opened"
        assert (skip.get("replay") or {}).get("skipped") is True



# ═════════════════════════════════════════════════════════════════════════════
# Row PW "Plain Words", part 3 (November 19, 2026) — the finishing pass, pressed
# in the real client at the first player's own setup: a general sent by a click
# and his order TAKEN BACK from the map's controls; the map's key; the price in
# words on the general's card; the empty command line's ideas. (The rule and the
# sources: `tests/test_pw3_the_finishing_pass.py`.)
# ═════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def pw3_walk(tmp_path_factory) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        run, sup = _start_engine_run(tmp_path_factory, "pw3")
    states: dict = {}
    try:
        states["begin"] = _act(run, "click Begin")
        states["select"] = _act(run, "click Soult")
        # a province of France two marches west of Lorraine: a plain order, nothing fought or shown
        states["send"] = _act(run, "clickshots 1436 375 4 220")
        states["take_back"] = _act(run, "click Take back")
        states["key"] = _act(run, "click Key")
        states["key_esc"] = _act(run, "key Escape")
        # the line where the client draws it (row FR, Session FR-1 — IC2-N1 moved it up a
        # row: the Cabinet and End Turn stand on their own row under it now)
        line = states["key_esc"]["command_line"]["rect"]
        states["line"] = _act(run, f"click_at {int(line[0]) + 100} {int(line[1] + line[3] / 2)}")
        states["tab"] = _act(run, "key Tab")
        # Row IC (the desk) rides the same engine — one boot fewer in the window
        # lane. Its own steps, guarded: a fault in them is row IC's to report
        # (`TestRowICTheDesk`), never a PW3 pin's.
        try:
            _ic_steps(run, states)
        except Exception as exc:      # noqa: BLE001 - re-raised by row IC's own class
            states["ic_error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    states["run_dir"] = str(run)
    return states


def _ic_on(state: dict, surface: str) -> list:
    """The controls of one surface, in the listing's order."""
    return [b for b in state.get("buttons") or [] if str(b.get("surface") or "") == surface]


def _ic_press(run: pathlib.Path, button: dict) -> dict:
    r = button["rect"]
    return _act(run, f"click_at {int(r[0] + r[2] / 2)} {int(r[1] + r[3] / 2)}")


def _ic_steps(run: pathlib.Path, states: dict) -> None:
    """Row IC's walk at the first player's own setup: a row of the desk's card is a door;
    the card folds; two corps marched off their province leave it in danger — on the card,
    on the map and at End Turn; the list's row opens the province."""
    states["ic_boot"] = json.loads((run / "state" / "0000.json").read_text(encoding="utf-8"))
    _act(run, "key Ctrl+A")
    states["ic_clear"] = _act(run, "key Delete")              # PW3's last step left an idea on the line
    card = _ic_on(states["ic_clear"], "DeskCard")
    first = next(b for b in card if str(b["text"]).startswith("1. "))
    states["ic_row"] = _ic_press(run, first)
    states["ic_let_go"] = _act(run, "key Escape")
    fold = next(b for b in _ic_on(states["ic_let_go"], "DeskCard") if str(b["text"]) == "–")
    states["ic_folded"] = _ic_press(run, fold)
    unfold = next(b for b in _ic_on(states["ic_folded"], "DeskCard") if str(b["text"]) == "+")
    states["ic_unfolded"] = _ic_press(run, unfold)
    answered: list = []
    for line, meant in (("Davout, march to Lorraine", "move Davout"), ("Ney, march to Lorraine", "move Ney")):
        state = _act(run, f"type {line}", meant=meant)
        state = _answer_chain(run, state, answered)
    states["ic_answered"] = answered
    states["ic_danger"] = _act(run, "look")
    states["ic_end_turn"] = _act(run, "click End Turn (E)")
    rows = _ic_on(states["ic_end_turn"], "TurnEndList")
    danger = next(b for b in rows if "Nothing holds Rhineland" in str(b["text"]))
    states["ic_door"] = _ic_press(run, danger)
    states["ic_key"] = _act(run, "click Key")
    states["ic_key_esc"] = _act(run, "key Escape")
    # the card's row set aside from the keyboard: Tab to the card's first row, Delete
    card = _ic_on(states["ic_key_esc"], "DeskCard")
    first = next(b for b in card if str(b["text"]).startswith("1. "))
    states["ic_aside_before"] = states["ic_key_esc"]
    states["ic_aside"] = _ic_press(run, next(b for b in card if str(b["text"]) == "×"
                                             and abs(b["rect"][1] - first["rect"][1]) < first["rect"][3]))


def _pw3_button(state: dict, text: str) -> dict:
    found = [b for b in state.get("buttons") or [] if str(b.get("text") or "") == text]
    assert found, f"no button reads {text!r}"
    return found[0]


class TestRowPW3TheFinishingPass:

    def test_the_cards_orders_say_their_price_in_words(self, pw3_walk):
        faces = _pw_buttons(pw3_walk["select"])
        # row IC, Session 2 (IC-7): the slot says WHICH hold — the standing one —
        # now that "Stand here" (the one-turn stand) is a button beside it
        assert "1 Hold the ground · 1 action" in faces and "5 Fall back · free" in faces, faces
        assert not any(re.search(r"(?<![A-Za-z])AP(?![A-Za-z])", face) for face in faces), faces

    def test_the_counters_wear_their_words(self, pw3_walk):
        said = _pw_said(pw3_walk["begin"])
        for word in ("Actions", "Admin", "Recruits", "Gold", "Diplomacy", "Authority", "Threat"):
            assert word in said, word

    def test_a_sent_general_can_be_taken_back_from_the_maps_controls(self, pw3_walk):
        assert _pw3_button(pw3_walk["begin"], "Take back")["disabled"] is True, "nothing to take back at the open"
        sent = pw3_walk["send"]
        shots = sent.get("shots") or []
        assert len(shots) == 4 and all((pathlib.Path(pw3_walk["run_dir"]) / s["file"]).is_file() for s in shots)
        chip = _pw3_button(sent, "Take back")
        assert chip["disabled"] is False and "Soult" in chip["tooltip"], chip
        assert "until it shows you something new" in chip["tooltip"]
        back = pw3_walk["take_back"]
        assert "Order taken back" in _pw_said(back)
        assert _pw3_button(back, "Take back")["disabled"] is True
        assert "4/4" in _pw_said(back), "the action is the player's again"

    def test_the_maps_key_opens_over_the_controls_and_esc_puts_it_away(self, pw3_walk):
        opened = pw3_walk["key"]
        key = [s for s in opened.get("surfaces") or [] if str(s.get("name", "")) == "MapKeyLayer"]
        assert key and "MAP KEY" in key[0]["lines"], [s.get("name") for s in opened.get("surfaces") or []]
        assert not opened.get("off_screen"), opened.get("off_screen")
        closed = pw3_walk["key_esc"]
        assert not [s for s in closed.get("surfaces") or [] if str(s.get("name", "")) == "MapKeyLayer"]
        assert not _modal(closed), "Esc put the key away and opened nothing"

    def test_a_click_on_the_empty_line_offers_what_can_be_asked(self, pw3_walk):
        said = _pw_said(pw3_walk["line"])
        assert "what can " in said and "what now?" in said, said[-600:]
        line = pw3_walk["tab"].get("command_line") or {}
        assert str(line.get("text", "")).startswith("what can "), ("Tab takes the first idea", line)

    def test_the_run_met_no_script_error(self, pw3_walk):
        assert pw3_walk["run"]["n_script_errors"] == 0, pw3_walk["run"]["script_errors"]


# ═════════════════════════════════════════════════════════════════════════════
# Row IC "Independent Command", the desk (November 19, 2026) — pressed in the real
# client at the first player's own setup (Interface Scale 1.8 on 5120 x 1377):
# THE PEACE, THE WAR and TO DECIDE on a card at the map's corner; a row is a door
# that sends nothing; a province left open beside an enemy in sight is said on
# the card, marked on the map and listed at End Turn. (The rule and the sources:
# `tests/test_ic1_the_desk.py`, `tests/test_ic2_the_turns_end.py`,
# `tests/test_ic3_what_was_hidden.py`.) The walk rides PW3's engine (`_ic_steps`).
# ═════════════════════════════════════════════════════════════════════════════

def _ic_rect_of(buttons: list) -> list:
    """The box around a surface's controls: [x, y, right, bottom]."""
    return [min(b["rect"][0] for b in buttons), min(b["rect"][1] for b in buttons),
            max(b["rect"][0] + b["rect"][2] for b in buttons),
            max(b["rect"][1] + b["rect"][3] for b in buttons)]


def _ic_sent_an_order(state: dict) -> bool:
    """A `/command` reply carries the board (`game_state`); a reading does not."""
    return any("game_state" in (r.get("keys") or []) for r in state.get("responses") or [])


class TestRowICTheDesk:

    @pytest.fixture(scope="class")
    def walk(self, pw3_walk):
        assert "ic_error" not in pw3_walk, pw3_walk.get("ic_error")
        return pw3_walk

    def test_a_first_time_menu_lights_the_school_and_keeps_its_title(self, walk):
        boot = walk["ic_boot"]
        said = _pw_said(boot)
        assert "INK & IRON" in said                         # the line beside the row costs the title nothing
        line = [t for t in boot["texts"] if str(t["text"]).startswith("New here? Start with the School of War")]
        assert line, said
        width, height = boot["factor"]["logical_size"]
        assert line[0]["rect"][0] + line[0]["rect"][2] <= width and line[0]["rect"][1] + line[0]["rect"][3] <= height
        school = _pw3_button(boot, "The School of War — a guided campaign")
        assert line[0]["rect"][0] >= school["rect"][0] + school["rect"][2]     # beside the row, not under it
        assert abs((line[0]["rect"][1] + line[0]["rect"][3] / 2)
                   - (school["rect"][1] + school["rect"][3] / 2)) < school["rect"][3]
        assert "(Button)" in str(boot.get("focus") or "")                       # the keyboard is on a row
        assert "Begin the 1805 Campaign" in _pw_buttons(boot)                   # one press away, as ever
        # the review: no count of turns is promised (the lesson is longer than "twelve")
        assert str(line[0]["text"]) == ("New here? Start with the School of War — a short guided campaign you "
                                        "can leave at any time.")
        # lever L1 (all three readers: "two lit rows"): ONE row is lit — the School's row stands
        # taller in its prominent face, "Begin" in the plain face every other row wears
        begin = _pw3_button(boot, "Begin the 1805 Campaign")
        other = _pw3_button(boot, "Settings")
        assert begin["disabled"] is False
        assert school["rect"][3] > begin["rect"][3], (school["rect"], begin["rect"])
        assert abs(begin["rect"][3] - other["rect"][3]) < 0.5, (begin["rect"], other["rect"])

    def test_the_card_says_the_peace_the_war_and_what_to_decide(self, walk):
        begin = walk["begin"]
        faces = [str(b["text"]) for b in _ic_on(begin, "DeskCard")]
        assert any(f.startswith("THE PEACE — Win the peace: hold 45 titled provinces — your homeland, lands a "
                                "treaty gave you, and conquests kept ") for f in faces), faces
        assert any(f.startswith("THE WAR — ") and "to hold the homeland" in f for f in faces), faces
        assert any(f.startswith("TO DECIDE — ") for f in faces), faces
        rows = [f for f in faces if re.match(r"\d+\. ", f)]
        # ours first, then the enemy (the review): "7 corps of yours have no orders and Mack (…) is within one march…"
        assert 1 <= len(rows) <= 3 and " no orders and Mack (" in rows[0], rows
        log = " ".join(begin.get("terminal_new") or [])
        assert log.count("Three things stay in view, Sire:") == 1, log[:400]   # said once, in the log

    def test_the_card_stands_on_the_map_s_corner_and_moves_nothing(self, walk):
        begin = walk["begin"]
        width, height = begin["factor"]["logical_size"]
        card = _ic_rect_of(_ic_on(begin, "DeskCard"))
        window = _ic_rect_of(_ic_on(begin, "BottomLeftUI"))
        assert card[0] >= window[2], (card, window)             # beside the command window, never on it
        assert 30 <= card[1] and card[2] <= width and card[3] <= height * 0.6, card
        head = [t for t in begin["texts"] if str(t["text"]) == "IMPERIAL COMMAND"]
        assert head and head[0]["rect"][1] >= 36, head          # the window's header stands under the top bar
        for key in ("begin", "ic_row", "ic_folded", "ic_unfolded", "ic_danger", "ic_end_turn", "ic_door"):
            assert not walk[key].get("off_screen"), (key, walk[key].get("off_screen"))
        for key in ("ic_folded", "ic_unfolded", "ic_end_turn"):
            assert not _pw_panel_moves(walk[key]), (key, _pw_panel_moves(walk[key]))

    def test_a_row_is_a_door_that_sends_nothing(self, walk):
        pressed = walk["ic_row"]
        assert not _ic_sent_an_order(pressed), pressed.get("responses")
        assert any(str(s.get("name", "")) == "SelectionCard" for s in pressed.get("surfaces") or [])
        line = pressed.get("command_line") or {}
        assert line.get("focused") and str(line.get("text", "")) == "", line     # the keyboard is the line's again
        assert not _modal(pressed)
        assert "4/4" in _pw_said(pressed), "nothing was spent"

    def test_the_card_folds_to_one_line_and_opens_again(self, walk):
        folded = [str(b["text"]) for b in _ic_on(walk["ic_folded"], "DeskCard")]
        assert len(folded) == 2 and folded[0].startswith("TO DECIDE (") and folded[1] == "+", folded
        opened = [str(b["text"]) for b in _ic_on(walk["ic_unfolded"], "DeskCard")]
        assert any(f.startswith("THE PEACE — ") for f in opened) and "–" in opened, opened
        before = _ic_rect_of(_ic_on(walk["ic_let_go"], "DeskCard"))
        after = _ic_rect_of(_ic_on(walk["ic_folded"], "DeskCard"))
        assert after[3] - after[1] < (before[3] - before[1]) / 2          # put away: it gives the map back

    def test_a_province_left_open_is_said_marked_and_listed(self, walk):
        danger = walk["ic_danger"]
        assert danger.get("map_dangers") == ["Rhineland"], (danger.get("map_dangers"), walk.get("ic_answered"))
        # lever L3 (reader 2: "the red triangle on the map has no name"): the mark wears it
        assert danger.get("map_danger_names") == ["Rhineland"], danger.get("map_danger_names")
        # lever L2 (all three readers: "the ! is not explained"): said under the card's rows …
        assert "! can cost you when the turn ends" in _pw_said(danger)
        faces = [str(b["text"]) for b in _ic_on(danger, "DeskCard")]
        assert any(re.match(r"\d+\. ! Nothing holds Rhineland — Mack \(", f) and f.endswith("one march away.")
                   for f in faces), faces
        stop = walk["ic_end_turn"]
        assert not _ic_sent_an_order(stop) and not _modal(stop)            # the turn did not end
        assert "EndTurnButton" in str(stop.get("focus") or "")
        listed = [str(b["text"]) for b in _ic_on(stop, "TurnEndList")]
        assert any(f.startswith("! Nothing holds Rhineland") for f in listed), listed
        said = _pw_said(stop)
        assert "Still to decide before the turn ends — " in said
        # no action is left (two marches spent four): the one remedy in hand is said
        assert "No actions are left — Take back (Ctrl+Z) undoes your last order." in said
        assert "(! can cost you when the turn ends)" in said                # … and in the list's head
        assert "Press End Turn again, or Enter, to end the turn anyway." in said
        # lever L6 (both readings: the log's last reply showed above the list, cut off): the
        # list's panel covers the log's whole room — from under the marshals to the line
        where = stop.get("turn_end") or {}
        listing, log, line = where.get("list"), where.get("log"), (stop.get("command_line") or {}).get("rect")
        assert listing and log and line, where
        assert listing[1] <= log[1] + 1.0, ("the panel's head stands at the log's head", listing, log)
        assert listing[1] + listing[3] <= line[1] + 1.0, ("its foot stands above the line", listing, line)
        assert "Nothing holds Rhineland" in " ".join(stop.get("terminal_new") or [])    # the log's warning says it too

    def test_the_list_s_row_opens_the_province_and_the_wait_stands(self, walk):
        """RE-SEATED by the review: a door does not end End Turn's wait. The list stays up — a
        second matter is one press away, and "End Turn again, or Enter" still means what it says."""
        door = walk["ic_door"]
        assert door["open"]["region_panel"] is True
        assert "RHINELAND" in _pw_said(door).upper()
        assert _ic_on(door, "TurnEndList"), "the list stands while the wait stands"
        assert "Press End Turn again, or Enter, to end the turn anyway." in _pw_said(door)
        assert not _ic_sent_an_order(door)
        line = door.get("command_line") or {}
        assert line.get("focused") and line.get("editing"), line          # the keyboard is the line's, live

    def test_a_row_set_aside_leaves_the_card_for_the_turn(self, walk):
        before = [str(b["text"]) for b in _ic_on(walk["ic_aside_before"], "DeskCard") if re.match(r"\d+\. ", str(b["text"]))]
        after = [str(b["text"]) for b in _ic_on(walk["ic_aside"], "DeskCard") if re.match(r"\d+\. ", str(b["text"]))]
        gone = before[0].split(". ", 1)[1]
        assert all(gone not in face for face in after), (before, after)
        assert not _ic_sent_an_order(walk["ic_aside"])

    def test_the_map_s_key_names_the_mark(self, walk):
        key = [s for s in walk["ic_key"].get("surfaces") or [] if str(s.get("name", "")) == "MapKeyLayer"]
        assert key, [s.get("name") for s in walk["ic_key"].get("surfaces") or []]
        assert any("A province of yours with nothing strong enough to hold it" in line
                   for line in key[0]["lines"]), key[0]["lines"]
        assert not walk["ic_key"].get("off_screen")


# ═════════════════════════════════════════════════════════════════════════════
# Row IC, the second commit — DIRECTIVES (November 19, 2026) — pressed in the real
# client at the first player's own setup (Interface Scale 1.8 on 5120 x 1377): an
# order to several corps is ONE list before anything is spent (typed, or a group
# Ctrl-clicked and sent by a click on a province), given as ONE request and taken
# back as one; a named army's chip selects its corps and its card's Hold lists them
# by the army's name; a war goal is named on the desk, ringed on the map, and its
# row opens the march as one list that fits the screen. (The rule and the sources:
# `tests/test_ic4_the_directive.py`, `tests/test_ic5_named_armies.py`,
# `tests/test_ic6_the_war_goal.py`; the blind readings: `docs/audits/ic_client/directives/`.)
# The two Ctrl-clicks fall on Ney's and Davout's pieces at Rhineland and the click on
# Lorraine, at this setup's boot camera; a moved map fails the group's own pin first.
# ═════════════════════════════════════════════════════════════════════════════

_IC_LINE = "Ney, Davout, Soult and Lannes, march to Lorraine"


@pytest.fixture(scope="module")
def ic_dir_walk(tmp_path_factory) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        run, sup = _start_engine_run(tmp_path_factory, "ic_dir")
    states: dict = {}
    try:
        states["begin"] = _act(run, "click Begin")
        states["typed"] = _act(run, f"type {_IC_LINE}", meant="move Ney")
        states["down"] = _act(run, "key Down")
        states["untick"] = _act(run, "key Space")
        states["retick"] = _act(run, "key Space")
        states["esc"] = _act(run, "key Escape")
        states["again"] = _act(run, "key Enter")              # the line Esc put back: the list again
        states["give"] = _act(run, "key Enter")
        states["take_back"] = _act(run, "click Take back")
        states["ctrl_ney"] = _act(run, "ctrlclick_at 1642 248")
        states["group"] = _act(run, "ctrlclick_at 1684 246")
        states["sent_to"] = _act(run, "click_at 1544 342")
        states["group_give"] = _act(run, "key Enter")
        states["group_back"] = _act(run, "click Take back")
        states["army"] = _act(run, "type form the Army of Italy with Lannes and Murat", meant="other: name an army")
        _act(run, "key Escape")
        states["chip"] = _act(run, "click Army of Italy · 2 corps")
        states["hold"] = _act(run, "click Hold…")
        states["hold_esc"] = _act(run, "key Escape")
        _act(run, "key Escape")                                # the group let go
        states["goal"] = _act(run, "type the war goal is Vienna", meant="other: set the war goal")
        row = next(b for b in _ic_on(states["goal"], "DeskCard")
                   if str(b["text"]).startswith("1. Your corps with no orders can march on Vienna"))
        states["goal_row"] = _ic_press(run, row)
        states["goal_esc"] = _act(run, "key Escape")
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    states["run_dir"] = str(run)
    return states


def _ic_log(state: dict) -> str:
    return " ".join(state.get("terminal_new") or [])


def _ic_card(state: dict) -> dict:
    return state.get("directive_card") or {}


def _ic_replies_with(state: dict, key: str) -> list:
    return [r for r in state.get("responses") or [] if key in (r.get("keys") or [])]


def _ic_actions(state: dict) -> str:
    """The desk's actions counter as it reads ("4/4")."""
    texts = [str(t.get("text") or "") for t in state.get("texts") or []]
    for i, text in enumerate(texts):
        if text == "Actions" and i + 1 < len(texts):
            return texts[i + 1]
    return ""


def _ic_still_and_on_screen(state: dict) -> None:
    card = _ic_card(state)
    width, height = state["factor"]["logical_size"]
    x, y, w, h = card["rect"]
    assert x >= 0 and y >= 0 and x + w <= width and y + h <= height, (card["rect"], width, height)
    assert not _pw_panel_moves(state), _pw_panel_moves(state)
    assert not state.get("off_screen"), state.get("off_screen")


class TestRowICDirectives:

    @pytest.fixture(scope="class")
    def walk(self, ic_dir_walk):
        assert "error" not in ic_dir_walk, ic_dir_walk.get("error")
        return ic_dir_walk

    def test_a_line_to_several_shows_one_list_first_and_spends_nothing(self, walk):
        typed = walk["typed"]
        card = _ic_card(typed)
        assert card["visible"] is True and card["mode"] == "directive"
        assert card["title"] == "ORDERS FOR 2 OF 4 CORPS"
        assert card["who"] == "Ney, Davout, Soult and Lannes: march to Lorraine"
        assert [r["marshal"] for r in card["rows"]] == ["Ney", "Davout", "Soult", "Lannes"]
        assert card["members"] == ["Ney", "Davout"] and card["total"] == 4 and card["have"] == 4
        assert card["line"] == _IC_LINE and card["give_disabled"] is False
        soult = next(r for r in card["rows"] if r["marshal"] == "Soult")
        assert soult["ok"] is False and soult["text"] == "already stands at Lorraine"
        said = card["total_text"]
        # (row IC, Session 2b's words census: "on his own" is kept for a man set
        # on his own - the list says each goes BY his own order)
        assert "Cost: 4 actions (2 + 2) of the 4 in hand — 2 corps go, each by his own order." in said
        assert "Lannes is not ticked: he needs 2 actions, and the ticked corps leave none." in said
        assert "undoes them all and gives their actions back" in _pw_said(typed)
        assert _ic_actions(typed) == "4/4"                                # nothing spent
        assert _ic_replies_with(typed, "directive") and not _ic_replies_with(typed, "group")

    def test_the_list_fits_and_stands_still(self, walk):
        for key in ("typed", "sent_to", "hold", "goal_row"):
            _ic_still_and_on_screen(walk[key])

    def test_its_keys_move_tick_and_untick(self, walk):
        assert _ic_card(walk["down"])["cursor"] == "Davout"
        untick = _ic_card(walk["untick"])
        assert untick["members"] == ["Ney"] and untick["total"] == 2
        assert untick["title"] == "ORDERS FOR 1 OF 4 CORPS"
        assert "Cost: 2 actions of the 4 in hand — 1 corps goes, by his own order." in untick["total_text"]
        assert _ic_card(walk["retick"])["members"] == ["Ney", "Davout"]

    def test_esc_spends_nothing_says_so_and_puts_the_line_back(self, walk):
        esc = walk["esc"]
        assert _ic_card(esc) == {}
        assert (esc.get("command_line") or {}).get("text") == _IC_LINE
        assert ("Not given: Ney, Davout, Soult and Lannes: march to Lorraine — nothing was spent. Your line "
                "is back below: change it, or press Enter to see the list again.") in _ic_log(esc)
        assert not _ic_replies_with(esc, "group") and _ic_actions(esc) == "4/4"

    def test_give_is_one_request_and_take_back_undoes_it_whole(self, walk):
        assert _ic_card(walk["again"])["members"] == ["Ney", "Davout"]       # Enter: the list again
        give = walk["give"]
        assert len(_ic_replies_with(give, "group")) == 1                     # ONE request
        log = _ic_log(give)
        assert ("The order goes to Ney and Davout, corps by corps — 2 corps, 4 actions for the 4 in hand: "
                "'march to Lorraine'.") in log
        assert "Ney begins march to Lorraine." in log and "Davout begins march to Lorraine." in log
        assert _ic_actions(give) == "0/4"
        back = walk["take_back"]
        assert "Taken back: “Ney, Davout, Soult and Lannes, march to Lorraine”." in _ic_log(back)
        assert _ic_actions(back) == "4/4"

    def test_a_ctrl_click_group_sent_by_a_click_lists_each_mans_move(self, walk):
        group = walk["group"]
        said = _pw_said(group)
        assert "Ney, Davout" in said, "the two Ctrl-clicks did not gather Ney and Davout (has the map moved?)"
        assert "sending them costs up to 4 actions · you have 4" in said
        assert {"Hold…", "Fortify…", "Drill…", "Name this army…"} <= set(_pw_buttons(group))
        card = _ic_card(walk["sent_to"])
        assert card["who"] == "Ney and Davout: go to Lorraine" and card["total"] == 2
        assert all("move to Lorraine — arrives now · 1 action" in r["text"] for r in card["rows"])
        give = walk["group_give"]
        assert len(_ic_replies_with(give, "group")) == 1
        assert "► Ney and Davout: go to Lorraine — 2 corps" in _ic_log(give)
        assert "'go to Lorraine'." in _ic_log(give)
        assert _ic_actions(walk["group_back"]) == "4/4"

    def test_an_armys_chip_selects_its_corps_and_its_hold_lists_them_by_name(self, walk):
        assert walk["army"]["army_chips"] == ["Army of Italy"]
        assert "The Army of Italy is formed: Lannes and Murat." in _ic_log(walk["army"])
        chip = walk["chip"]
        assert "The Army of Italy — Lannes, Murat" in _pw_said(chip)
        assert "Disband the Army of Italy" in _pw_buttons(chip)
        assert "Each button first shows each corps' order and price" in _pw_said(chip)
        card = _ic_card(walk["hold"])
        assert card["who"] == "The Army of Italy: hold" and card["members"] == ["Lannes", "Murat"]
        assert not _ic_replies_with(walk["hold"], "group")                   # a list is no order
        assert "Not given: The Army of Italy: hold — nothing was spent." in _ic_log(walk["hold_esc"])

    def test_the_war_goal_is_named_ringed_and_its_row_opens_a_list_that_fits(self, walk):
        goal = walk["goal"]
        assert "The goal of the war with the Third Coalition is now Vienna." in _ic_log(goal)
        war = next(str(b["text"]) for b in _ic_on(goal, "DeskCard") if str(b["text"]).startswith("THE WAR — "))
        assert war.endswith("— your war goal: Vienna."), war
        assert goal["map_goals"] == ["Vienna"] and goal["map_goal_names"] == ["War goal: Vienna"]
        assert any(str(m.get("text")) == "Austria" for m in goal.get("map") or []), "the plate hid AUSTRIA"
        card = _ic_card(walk["goal_row"])
        assert card["title"] == "ORDERS FOR 3 OF 8 CORPS"
        assert card["who"].startswith("Go to Vienna — Ney, Davout"), card["who"]   # the order leads a long line
        assert _ic_card(walk["goal_esc"]) == {}

    def test_the_run_met_no_script_error(self, walk):
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


# ═════════════════════════════════════════════════════════════════════════════
# Row IC, Session 2 — BUTTONS FOR ORDERS, THE LINE FOR TASKS, EXACT ORDERS
# (November 20, 2026; `docs/SYSTEMS_REFERENCE.md` §231; IC-V4's driven class,
# and the review's row IC2-R19: the client's half was pinned only by reading
# its source). The real client at the first player's own setup — Interface
# Scale 1.8 on 5120 x 1377 — with the reading under the command line shown as
# his game shows it (`DD_B_READBACK=1`; a harness's default is off). Every
# place is read off the state (the map moves when a card opens); nothing is
# pressed at a remembered pixel.
# ═════════════════════════════════════════════════════════════════════════════

_IC2_EXACT = "Soult, hold Lorraine. If attacked, dig in. If outnumbered, fall back to Champagne."


def _ic2_btn(state: dict, surface: str, starts: str) -> dict:
    found = [b for b in _ic_on(state, surface) if str(b["text"]).startswith(starts)]
    assert found, f"no control of {surface} starts {starts!r}: {[b['text'] for b in _ic_on(state, surface)]}"
    return found[0]


def _ic2_faces(state: dict) -> dict:
    """The general's card: face -> rect."""
    return {str(b["text"]): b["rect"] for b in _ic_on(state, "SelectionCard")}


def _ic2_piece(state: dict, name: str) -> tuple:
    row = next(m for m in state["map"] if str(m["text"]) == name)
    return _centre_of(row["rect"])


def _ic2_readback(state: dict) -> str:
    """The reading under the command line, as drawn ("" for none)."""
    for t in state.get("texts") or []:
        text = str(t.get("text") or "")
        if "Not taken:" in text or "Taken:" in text or "Enter sends:" in text:
            return text
    return ""


def _ic2_card_lines(state: dict) -> str:
    for s in state.get("surfaces") or []:
        if isinstance(s, dict) and s.get("name") == "OrderConfirmCard":
            return "\n".join(str(line) for line in s.get("lines") or [])
    return ""


def _ic2_order_card(state: dict) -> dict:
    """The order card on any of its faces, read off the screen: its title, its
    headline and everything it says ({} while it is shut). (`_ic_card` is the
    list's own report — it is empty on the other faces.)"""
    said = _ic2_card_lines(state)
    if not said or "order_card" not in " ".join((state.get("open") or {}).get("popups") or []):
        return {}
    lines = said.split("\n")
    return {"title": lines[0], "who": lines[1] if len(lines) > 1 else "", "said": said}


@pytest.fixture(scope="module")
def ic2_walk(tmp_path_factory) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        mp.setenv("DD_B_READBACK", "1")
        run, sup = _start_engine_run(tmp_path_factory, "ic2")
    states: dict = {}
    answered: list = []
    try:
        states["begin"] = _act(run, "click Begin")
        # ── the general's card: the second row, the posture menu, the ready tasks
        states["select"] = _act(run, "click Murat")
        states["posture"] = _ic_press(run, _ic2_btn(states["select"], "SelectionCard", "Posture"))
        states["posture_shut"] = _ic_press(run, _ic2_btn(states["posture"], "SelectionCard", "Posture"))
        states["tasks"] = _ic_press(run, _ic2_btn(states["posture_shut"], "SelectionCard", "Give him a task"))
        states["tasks_shut"] = _ic_press(run, _ic2_btn(states["tasks"], "SelectionCard", "Give him a task"))
        # ── the card that opens on an enemy: "Chase him" beside the attack (F1)
        x, y = _ic2_piece(states["tasks_shut"], "Mack")
        states["enemy"] = _act(run, f"click_at {x} {y}")
        _act(run, "key Escape")                                   # the card
        states["let_go"] = _act(run, "key Escape")                # the selection
        # ── the typed line: what it took, what it did not, what Enter sends (F2)
        states["draft"] = _act(run, "draft Ney, retreat if outnumbered")
        _act(run, "key Ctrl+A")
        _act(run, "key Delete")
        # a typed line sent before its reading is back: held, and filled as understood
        states["gate"] = _act(run, "type Murat, scout Swabia boldly", meant="scout Murat")
        states["gate_enter"] = _answer_chain(run, _act(run, "key Enter"), answered)
        # ... and with the reading on show, Enter sends the line as understood
        states["draft2"] = _act(run, "draft Bernadotte, defend carefully")
        states["understood"] = _answer_chain(run, _act(run, "key Enter"), answered)
        # ── an exact order: typed, given, and read off its mark on the map (F4)
        states["exact"] = _answer_chain(run, _act(run, f"type {_IC2_EXACT}", meant="hold Soult"), answered)
        assert [m["marshal"] for m in states["exact"]["order_marks"]] == ["Soult"]
        states["standing"] = _act(run, "click_mark Soult")
        states["standing_esc"] = _act(run, "key Escape")
        # ── "Stand here": one press
        select = _act(run, "click Davout")
        states["stand_pressed"] = _ic_press(run, _ic2_btn(select, "SelectionCard", "Stand here"))
        states["stand"] = _answer_chain(run, states["stand_pressed"], answered)
        _act(run, "key Escape")
        # ── the group face: Attack…, Support…, Fall back…, Garrison…
        _act(run, "type form the Army of Italy with Lannes and Murat", meant="other: name an army")
        _act(run, "key Escape")
        states["army"] = _act(run, "click Army of Italy · 2 corps")
        states["fall_back"] = _ic_press(run, _ic2_btn(states["army"], "SelectionCard", "Fall back"))
        states["fall_back_esc"] = _act(run, "key Escape")
        states["attack_pick"] = _ic_press(run, _ic2_btn(states["fall_back_esc"], "SelectionCard", "Attack"))
        # a wrong click - one of ours - leaves the pick waiting, as its toast says (IC2-R21)
        x, y = _ic2_piece(states["attack_pick"], "Bernadotte")
        states["attack_wrong"] = _act(run, f"click_at {x} {y}")
        x, y = _ic2_piece(states["attack_wrong"], "Mack")
        states["attack_card"] = _act(run, f"click_at {x} {y}")
        states["attack_esc"] = _act(run, "key Escape")
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["answered"] = answered
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    states["run_dir"] = str(run)
    return states


class TestRowIC7TheButtons:

    @pytest.fixture(scope="class")
    def walk(self, ic2_walk):
        assert "error" not in ic2_walk, ic2_walk.get("error")
        return ic2_walk

    def test_the_run_stands_at_the_first_players_own_setup(self, walk):
        state = walk["select"]
        assert state["ui_scale"]["window"] == pytest.approx(1.8)
        assert state["factor"]["logical_size"] == [2844.0, 765.0]

    def test_the_card_wears_the_simple_orders_under_its_seven(self, walk):
        faces = list(_ic2_faces(walk["select"]))
        assert faces[1:8] == [
            "1 Hold the ground · 2 actions", "2 Fortify · 2 actions", "3 Drill · 1 action",
            "4 Scout · 1 action", "5 Fall back · free", "6 Garrison · 2 actions", "7 Cancel order"]
        # (row IC, Session 4b: a man who may be set on his own wears its button last —
        # no task, he makes war as he sees fit)
        assert faces[8:] == ["Stand here · 1 action", "Stay put · free", "Posture: steady ▾",
                             "Give him a task…", "Set him on his own · 2 actions"]
        assert not walk["select"].get("off_screen")

    def test_the_posture_menu_opens_where_the_hint_stood_and_moves_nothing(self, walk):
        """Pressed at his setup: with the menu added at the card's foot,
        "Posture" itself moved 84 px up as it was pressed."""
        before, opened = _ic2_faces(walk["select"]), _ic2_faces(walk["posture"])
        opened["Posture: steady ▾"] = opened.pop("Posture: steady ▴")
        for face, rect in before.items():
            assert opened[face] == rect, face
        menu = {str(b["text"]): bool(b.get("disabled")) for b in _ic_on(walk["posture"], "SelectionCard")
                if str(b["text"]) not in before and not str(b["text"]).startswith("Posture")}
        assert menu == {"Attacking · 1 action": False, "Steady · free": True,
                        "Defending · 1 action": False, "Form square · 1 action": True}
        steady = _ic2_btn(walk["posture"], "SelectionCard", "Steady")
        assert "already in that posture" in str(steady.get("tooltip"))
        assert _ic2_faces(walk["posture_shut"]) == before
        assert not walk["posture"].get("off_screen")

    def test_the_ready_tasks_stand_above_his_orders_and_write_nothing_unasked(self, walk):
        before, opened = _ic2_faces(walk["select"]), _ic2_faces(walk["tasks"])
        for face, rect in before.items():
            if face != "×":                      # only his name's row is lifted
                assert opened[face] == rect, face
        tasks = [face for face in opened if face not in before]
        # (row IC, Session 3: a man who may be set on his own is offered HIS
        # OWN proposal first — §233.5; the ready tasks follow it)
        assert tasks[0].startswith("On his own: ") and "his idea" in tasks[0], tasks
        assert "Chase Mack · 2 actions" in tasks and 2 <= len(tasks) <= 4, tasks
        top = min(opened[face][1] for face in tasks)
        assert top + 37 * len(tasks) <= before["1 Hold the ground · 2 actions"][1], "above his orders"
        assert "a press writes the sentence on the command line" in _pw_said(walk["tasks"])
        assert (walk["tasks"].get("command_line") or {}).get("text") == "", "nothing written unasked"
        assert "A task is typed, Sire" in _ic_log(walk["tasks"]), "the first-open line, once"
        assert _ic2_faces(walk["tasks_shut"]) == before, "a second press puts them away"
        assert not walk["tasks"].get("off_screen")

    def test_the_enemy_card_offers_the_chase_beside_the_attack(self, walk):
        card = _ic2_order_card(walk["enemy"])
        assert card["title"] == "ORDERS FOR MURAT" and card["who"] == "Murat, attack Mack"
        assert "Or another order — a chip sends it now, and this card closes:" in card["said"]
        chips = [str(b["text"]) for b in _ic_on(walk["enemy"], "OrderConfirmCard")]
        assert "Chase him · 2 actions" in chips, chips
        assert not walk["enemy"].get("off_screen") and not _pw_panel_moves(walk["enemy"])

    def test_the_reading_says_what_was_not_taken_and_what_enter_sends(self, walk):
        reading = _ic2_readback(walk["draft"])
        assert "Ney · fall back · free" in reading
        assert "Not taken: ‘if outnumbered’ — this order takes no condition; it would go out now" in reading
        assert "Enter sends: Ney, retreat" in reading
        assert "Or press to write: [Ney, hold. If he is outnumbered, fall back to Lorraine.]" in reading
        assert (walk["draft"].get("command_line") or {}).get("text") == "Ney, retreat if outnumbered"
        assert _ic_actions(walk["draft"]) == "4/4", "typed, not sent: nothing spent"

    def test_a_typed_line_sent_with_a_part_not_taken_is_held_and_filled(self, walk):
        gate = walk["gate"]
        assert "Not sent, Sire" in _ic_log(gate) and "'boldly'" in _ic_log(gate)
        assert (gate.get("command_line") or {}).get("text") == "Murat, scout Swabia"
        assert _ic_actions(gate) == "4/4"
        assert _ic_actions(walk["gate_enter"]) == "3/4", "the next Enter sends what was shown"

    def test_enter_sends_the_line_as_understood_and_says_so(self, walk):
        assert "Enter sends: Bernadotte, defend" in _ic2_readback(walk["draft2"])
        log = _ic_log(walk["understood"])
        assert "You typed: Bernadotte, defend carefully" in log and "Sent as understood:" in log
        assert "► Bernadotte, defend " in log + " "
        assert "defend carefully" not in log.split("Sent as understood:")[1], "what was shown is what was sent"
        assert _ic_actions(walk["understood"]) == "2/4"

    def test_an_exact_order_is_given_and_its_mark_opens_what_it_says(self, walk):
        log = _ic_log(walk["exact"])
        assert ("Soult's exact orders — (1) if he is attacked, dig in; (2) if he is outnumbered, "
                "fall back to Champagne.") in log
        card = _ic2_order_card(walk["standing"])
        assert card["title"] == "STANDING ORDER — SOULT" and card["who"] == "Soult holds Lorraine"
        assert "His exact orders — 2 of 2 left:" in card["said"]
        assert "1.  if he is attacked, dig in" in card["said"]
        assert "2.  if he is outnumbered, fall back to Champagne" in card["said"]
        # the blind reading: all three readers asked which line wins when two are true
        assert "he carries out the first of them that is true" in card["said"]
        assert not walk["standing"].get("off_screen") and not _pw_panel_moves(walk["standing"])
        assert _ic2_order_card(walk["standing_esc"]) == {}

    def test_stand_here_is_one_press(self, walk):
        assert "► Davout, defend" in _ic_log(walk["stand_pressed"])
        assert _ic_actions(walk["stand"]) == "0/4"

    def test_the_group_face_offers_attack_support_fall_back_and_garrison(self, walk):
        faces = [str(b["text"]) for b in _ic_on(walk["army"], "SelectionCard")]
        for face in ("Attack…", "Support…", "Fall back…", "Garrison…"):
            assert face in faces, faces
        listed = _ic_card(walk["fall_back"])
        assert listed["visible"] is True and listed["mode"] == "directive"
        assert [row["marshal"] for row in listed["rows"]] == ["Lannes", "Murat"]
        _ic_still_and_on_screen(walk["fall_back"])
        # "Attack…" waits for the enemy: a click on one of ours opens nothing and
        # asks again (the second look: the pick used to be let go by it, and the
        # next click opened the group's march list) ...
        assert _ic2_order_card(walk["attack_wrong"]) == {} and _ic_card(walk["attack_wrong"]) == {}
        assert "Click an enemy corps in sight to attack." in _pw_said(walk["attack_wrong"])
        # ... and the click on the enemy opens the LEAD's attack card
        lead = _ic2_order_card(walk["attack_card"])
        assert lead["title"] == "ORDERS FOR LANNES" and lead["who"] == "Lannes, attack Mack"
        assert _ic2_order_card(walk["attack_esc"]) == {}

    def test_the_command_line_shows_the_task_being_typed(self, walk):
        """The blind reading's three readers, each unasked: the box read "retreat
        if outnumbered" — "Ney," had scrolled out. Forty characters is a short
        task ("Soult, hold Lorraine. If attacked, dig in."). IC2-N1 — FIXED in
        row FR's Session FR-1 (November 23, 2026): on the desk and in the column
        the Cabinet, End Turn and Open Envoys stand on a row of their own under
        the line (`main._fr1_seat_turn_buttons`); 171 px became 391."""
        box = (walk["draft"].get("command_line") or {})["rect"]
        assert box[2] >= 360, f"the command line is {box[2]} px wide at his setup"

    def test_the_run_met_no_script_error(self, walk):
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


# ════════════════════════════════════════════════════════════════════════════
# Row IC, Session 2b (November 20, 2026) — the task to prove himself, pressed
# in the real client at the first player's own setup. The audience is reached
# through the staging switch (`DD_B_STAGE=1`: the sandbox's own debug road —
# `debug audience <marshal>` sets his trust to 15 and raises the game's own
# question through its one seam); everything after it is a player's press.
# ════════════════════════════════════════════════════════════════════════════

def _ic2b_window(state: dict) -> dict:
    """The audience's window as drawn: its lines and its answers ({} when shut)."""
    for s in state.get("surfaces") or []:
        if isinstance(s, dict) and s.get("name") == "RedemptionDialog":
            return {"lines": [str(line) for line in s.get("lines") or []],
                    "answers": _ic_on(state, "RedemptionDialog")}
    return {}


def _ic2b_card(state: dict) -> dict:
    for s in state.get("surfaces") or []:
        if isinstance(s, dict) and s.get("name") == "SelectionCard":
            return {"lines": [str(line) for line in s.get("lines") or []],
                    "buttons": [str(b["text"]) for b in _ic_on(state, "SelectionCard")]}
    return {}


def _ic2b_text(state: dict, starts: str) -> dict:
    """The audience window's text that starts `starts` — or whose words start
    it on the line under his own quoted line (row IC, Session 4 — IC-13: his
    proposal is headed by "Ney: “…”", the line he asks with)."""
    for t in state.get("texts") or []:
        if str(t.get("surface") or "") != "RedemptionDialog":
            continue
        text = str(t.get("text") or "")
        head, _, rest = text.partition("\n")
        if text.startswith(starts) or (head.endswith("”") and rest.startswith(starts)):
            return t
    raise AssertionError(f"no text of the audience's window starts {starts!r}")


def _ic2b_rect(state: dict, starts: str) -> list:
    """The rect of the audience window's text that starts `starts`."""
    return _ic2b_text(state, starts)["rect"]


@pytest.fixture(scope="module")
def ic2b_walk(tmp_path_factory) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        mp.setenv("DD_B_STAGE", "1")
        run, sup = _start_engine_run(tmp_path_factory, "ic2b")
    states: dict = {}
    try:
        states["begin"] = _act(run, "click Begin")
        _act(run, "type debug set_location Ney Franconia", meant="other: staging")
        _act(run, "type debug set_location Davout Franconia", meant="other: staging")
        states["ney"] = _act(run, "type debug audience Ney", meant="other: staging")
        states["given"] = _act(run, "click Give Ney a task to prove himself")
        states["card"] = _act(run, "click Ney")
        states["let_go"] = _act(run, "key Escape")
        # the Generals page: his row, then his detail (the review - his card's
        # sibling: no order button there either)
        states["generals"] = _act(run, "click Generals (G)")
        row = next(b for b in _ic_on(states["generals"], "MarshalManagement")
                   if "On a task to prove himself" in str(b.get("tooltip") or ""))
        states["generals_ney"] = _ic_press(run, row)
        states["generals_shut"] = _act(run, "key Escape")
        states["davout"] = _act(run, "type debug audience Davout", meant="other: staging")
        states["davout_given"] = _act(run, "click Give Davout a task to prove himself")
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


class TestRowIC9bTheTaskToProveHimself:

    @pytest.fixture(scope="class")
    def walk(self, ic2b_walk):
        assert "error" not in ic2b_walk, ic2b_walk.get("error")
        return ic2b_walk

    def test_the_run_stands_at_the_first_players_own_setup(self, walk):
        state = walk["ney"]
        assert state["ui_scale"]["window"] == pytest.approx(1.8)
        assert state["factor"]["logical_size"] == [2844.0, 765.0]

    def test_the_audience_offers_the_task_and_says_it_in_full(self, walk):
        window = _ic2b_window(walk["ney"])
        assert window["lines"][0] == "NEY REQUESTS AUDIENCE"
        assert [str(b["text"]) for b in window["answers"]] == [
            "Give Ney a task to prove himself", "Dismiss Ney", "Transfer Ney to Staff"]
        said = "\n".join(window["lines"])
        assert ("Ney is a bold man, so he asks to march from Franconia and take Bohemia, where France "
                "sees no defenders — and then to hold it, striking any enemy next to him that he "
                "outnumbers.") in said
        for needed in ("for 3 turns — this one and the next two — then he is under your orders again",
                       "Until then he takes no orders, and you cannot call him back.",
                       "up to 6 turns in all, the first 3 included",
                       "40 (and your authority by 10) if he won two battles or took a defended place;",
                       "5 if he lost more than he won."):
            assert needed in said, needed
        assert "Trust: 15 of 100 — critical" in said
        assert "autonom" not in said.lower() and "independent" not in said.lower()

    def test_every_answers_words_stand_under_its_own_button(self, walk):
        """The first blind reading: "Dismiss Ney" and "Transfer Ney to Staff"
        stood with no words. Each answer's words are between its own button
        and the next one."""
        state = walk["ney"]
        buttons = {str(b["text"]): b["rect"] for b in _ic2b_window(state)["answers"]}
        task = _ic2b_rect(state, "Ney is a bold man")
        dismiss = _ic2b_rect(state, "Ney is dismissed for good; his men join the nearest marshal within three")
        staff = _ic2b_rect(state, "Ney leaves the field for a post on your staff; his corps waits in depot.")
        give, out, transfer = (buttons["Give Ney a task to prove himself"], buttons["Dismiss Ney"],
                               buttons["Transfer Ney to Staff"])
        assert give[1] < task[1] < out[1] < dismiss[1] < transfer[1] < staff[1]
        # ... each nearer its own button than the next answer's
        assert task[1] - (give[1] + give[3]) < out[1] - (task[1] + task[3])
        assert dismiss[1] - (out[1] + out[3]) < transfer[1] - (dismiss[1] + dismiss[3])
        assert all(str(b.get("tooltip") or "") == "" for b in _ic2b_window(state)["answers"]), \
            "the words stand on the window: no hover repeats them"

    def test_the_window_stands_whole_below_the_top_bar_and_does_not_move(self, walk):
        """Pressed at his setup: with every answer's words it first stood 720 px
        in a 765 px view, over the top bar."""
        for key in ("ney", "davout"):
            state = walk[key]
            assert not state.get("off_screen"), (key, state.get("off_screen"))
            assert not _pw_panel_moves(state), (key, _pw_panel_moves(state))
            rects = [t["rect"] for t in state["texts"] if str(t.get("surface") or "") == "RedemptionDialog"]
            rects += [b["rect"] for b in _ic2b_window(state)["answers"]]
            assert min(r[1] for r in rects) >= 44.0, (key, "below the top bar")
            assert max(r[1] + r[3] for r in rects) <= 765.0 - 8.0, key

    def test_giving_it_is_free_and_says_what_he_will_do(self, walk):
        log = _ic_log(walk["given"])
        assert ('Ney has his task to prove himself: "Ney, take Bohemia and hold it." He marches on '
                "Bohemia as this turn ends. He takes no orders until it ends — 3 turns, or up to 6 "
                "while he keeps winning.") in log
        assert _ic_actions(walk["given"]) == "4/4", "giving it costs no action"
        assert _ic2b_window(walk["given"]) == {}, "the window is shut"
        assert [m["marshal"] for m in walk["given"]["order_marks"]] == ["Ney"], "his order is on the map"

    def test_the_desk_lists_no_matter_for_a_man_who_takes_no_orders(self, walk):
        """Pressed at his setup: TO DECIDE said "Ney will leave his post to
        join a battle near him — Mack is close."."""
        desk = [str(b["text"]) for b in _ic_on(walk["given"], "DeskCard")]
        assert desk and not [row for row in desk if "Ney" in row], desk

    def test_his_card_carries_no_order_and_says_why(self, walk):
        """The first blind reading: eleven greyed order buttons under "he takes
        no orders" — every reader doubted them."""
        card = _ic2b_card(walk["card"])
        assert card["buttons"] == ["×"], card["buttons"]
        said = "\n".join(card["lines"])
        assert "On a task to prove himself — 3 turns left: marches on Bohemia as this turn ends." in said
        assert 'His task: "Ney, take Bohemia and hold it."' in said
        assert "He takes no orders until it ends, and you cannot call him back." in said
        assert card["lines"][-1] == "Esc closes this card"
        assert "actions left" not in said and "lets him go" not in said
        assert "Click a province to send him" not in said
        assert not walk["card"].get("off_screen")
        assert _ic2b_card(walk["let_go"]) == {}, "Esc closes it"

    def test_the_generals_page_shows_his_task_and_no_order_button(self, walk):
        """The review (rule 10, his card's sibling): his Generals page still
        wore seven greyed order buttons - "Cancel order" among them - under a
        man who takes no orders: the thing every reader of the first blind
        reading doubted on his card."""
        roster = walk["generals"]
        assert roster["open"]["screens"] == ["generals"]
        state = walk["generals_ney"]
        page = next(s for s in state["surfaces"] if s.get("name") == "MarshalManagement")
        said = "\n".join(str(line) for line in page["lines"])
        assert "On a task to prove himself — 3 turns left: marches on Bohemia as this turn ends" in said
        assert "His task: Ney, take Bohemia and hold it." in said
        assert "He takes no orders until his task ends, and you cannot call him back." in said
        faces = [str(b["text"]) for b in _ic_on(state, "MarshalManagement")]
        assert "On the map" in faces
        orders = ("Hold", "Fortify", "Unfortify", "Drill", "Scout", "Fall back", "Garrison", "Cancel order")
        assert not [face for face in faces if face.startswith(orders)], faces
        assert not state.get("off_screen")
        assert walk["generals_shut"]["open"]["screens"] == [], "Esc closes the page"

    def test_davout_proposes_by_his_own_nature_on_the_same_ground(self, walk):
        """The blind reading's question: two men on one ground, two tasks."""
        said = "\n".join(_ic2b_window(walk["davout"])["lines"])
        assert "Davout is a careful man, so he asks to hold Franconia, where he stands, and to dig in." in said
        log = _ic_log(walk["davout_given"])
        assert 'Davout has his task to prove himself: "Davout, hold Franconia."' in log
        assert "marches on" not in log.split("Davout has his task")[1]

    def test_the_run_met_no_script_error(self, walk):
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


@pytest.fixture(scope="module")
def ic2b_compact(tmp_path_factory) -> dict:
    """The audience at the smallest view the client supports: Interface Scale
    2.0 on a 1600 x 900 window - a logical 800 x 450."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "2.0")
        mp.setenv("DD_B_WINDOW", "1600x900")
        mp.setenv("DD_B_STAGE", "1")
        run, sup = _start_engine_run(tmp_path_factory, "ic2b_compact")
    states: dict = {}
    try:
        _act(run, "click Begin")
        _act(run, "type debug set_location Ney Franconia", meant="other: staging")
        states["ney"] = _act(run, "type debug audience Ney", meant="other: staging")
        states["given"] = _act(run, "click Give Ney a task to prove himself")
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


class TestRowIC9bTheAudienceAtTheCompactView:
    """The review (the client's lane), pressed: at Interface Scale 2.0 on
    1600 x 900 the window ran 77 px past the screen - its header under the top
    bar, "Transfer to Staff" off the bottom. Where the window cannot hold his
    proposal whole, his quoted line steps aside and the proposal SCROLLS: every
    answer stays on the screen."""

    @pytest.fixture(scope="class")
    def walk(self, ic2b_compact):
        assert "error" not in ic2b_compact, ic2b_compact.get("error")
        return ic2b_compact

    def test_the_view_is_the_compact_one(self, walk):
        state = walk["ney"]
        assert state["ui_scale"]["window"] == pytest.approx(2.0)
        assert state["factor"]["logical_size"] == [800.0, 450.0]

    def test_every_answer_stands_on_the_screen(self, walk):
        state = walk["ney"]
        assert not state.get("off_screen"), state.get("off_screen")
        answers = {str(b["text"]): b["rect"] for b in _ic2b_window(state)["answers"]}
        assert list(answers) == ["Give Ney a task to prove himself", "Dismiss Ney", "Transfer Ney to Staff"]
        for face, rect in answers.items():
            assert rect[1] >= 44.0, (face, "below the top bar")
            assert rect[1] + rect[3] <= 450.0, (face, "above the screen's bottom edge")
        title = _ic2b_rect(state, "NEY REQUESTS AUDIENCE")
        assert title[1] >= 44.0, "the header is not under the top bar"

    def test_his_proposal_scrolls_and_the_other_answers_keep_their_words_in_hovers(self, walk):
        state = walk["ney"]
        proposal = _ic2b_text(state, "Ney is a bold man")
        assert proposal.get("clipped"), "the proposal stands in a scroll: it is longer than its room"
        assert "you cannot call him back" in str(proposal["text"]), "nothing of it is cut from the text"
        hovers = {str(b["text"]): str(b.get("tooltip") or "") for b in _ic2b_window(state)["answers"]}
        assert hovers["Dismiss Ney"].startswith("Ney is dismissed for good")
        assert hovers["Transfer Ney to Staff"].startswith("Ney leaves the field for a post on your staff")

    def test_the_task_is_given_from_there_too(self, walk):
        assert 'Ney has his task to prove himself: "Ney, take Bohemia and hold it."' in _ic_log(walk["given"])
        assert _ic2b_window(walk["given"]) == {}

    def test_the_run_met_no_script_error(self, walk):
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


# ═══════════════════════════ row IC, Session 3 — on his own ═════════════════
# (`SYSTEMS_REFERENCE.md` §233; `docs/audits/ic_client/session3/README.md` —
# the frames the blind reading read, taken by this same walk at the first
# player's own setup)

@pytest.fixture(scope="module")
def ic3_walk(tmp_path_factory) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        mp.setenv("DD_B_READBACK", "1")
        mp.setenv("DD_B_STAGE", "1")
        run, sup = _start_engine_run(tmp_path_factory, "ic3")
    states: dict = {}
    try:
        states["begin"] = _act(run, "click Begin")
        states["draft"] = _act(run, "draft Davout, hold Rhineland on your own", meant="hold Davout")
        _act(run, "key ctrl+a")
        _act(run, "key BackSpace")
        states["given"] = _act(run, "type Masséna, hold Milan and Piedmont on your own", meant="hold Massena")
        states["card"] = _act(run, "click Massena")
        states["desk"] = _act(run, "key Escape")
        states["asked"] = _act(run, "type Masséna, what will you do?", meant="other: a question")
        states["stood_down"] = _act(run, "type Masséna, stand down", meant="other: stand down")
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


class TestRowIC10OnHisOwn:

    @pytest.fixture(scope="class")
    def walk(self, ic3_walk):
        assert "error" not in ic3_walk, ic3_walk.get("error")
        return ic3_walk

    def test_the_run_stands_at_the_first_players_own_setup(self, walk):
        state = walk["draft"]
        assert state["ui_scale"]["window"] == pytest.approx(1.8)
        assert state["factor"]["logical_size"] == [2844.0, 765.0]

    def test_typing_a_task_is_answered_before_enter_and_spends_nothing(self, walk):
        reading = _ic2_readback(walk["draft"])
        assert "on his own: hold Rhineland" in reading, reading
        assert "once given, 1 of the 1 you may have (laws raise it)" in reading
        assert "he attacks only when the odds are our" in reading
        assert "At the start of next turn he means to — if nothing changes first:" in reading  # (Session 4b)
        assert (walk["draft"].get("command_line") or {}).get("text") == "Davout, hold Rhineland on your own", \
            "typed, not sent"
        assert "is on his own" not in _ic_log(walk["draft"]), "nothing given by typing"

    def test_giving_it_says_when_he_starts_and_charges_two_actions(self, walk):
        log = _ic_log(walk["given"])
        assert ("on his own: hold Milan and Piedmont. He makes his first move at the start of next turn."
                in log), log
        assert "On their own: 1 of the 1 you may have." in log
        before, after = (int(_ic_actions(walk["begin"]).split("/")[0]),
                         int(_ic_actions(walk["given"]).split("/")[0]))
        assert before - after == 2

    def test_his_card_says_when_he_moves_and_offers_his_own_buttons(self, walk):
        faces = list(_ic2_faces(walk["card"]))
        said = _pw_said(walk["card"])
        # (Session 4b — "He moves at turn start": no preview, the card says when he moves)
        assert "On his own" in said and "He makes his first move at the start of next turn." in said
        assert "Tonight" not in said
        assert "Ask him" in faces and "Change his task…" in faces
        assert any(f.startswith("Stand him down · free") for f in faces), faces
        assert "Give him a task…" not in faces, "a man on his own changes his task instead"
        assert not walk["card"].get("off_screen")

    def test_the_desk_says_the_count_and_his_night(self, walk):
        desk = [str(b.get("text") or "") for b in _ic_on(walk["desk"], "DeskCard")]
        line = next((t for t in desk if t.startswith("ON THEIR OWN")), "")
        assert "1 of the 1 you may have" in line and "they move as each turn opens" in line, desk

    def test_asking_him_is_free_and_answered_in_his_voice(self, walk):
        assert _ic_actions(walk["asked"]) == _ic_actions(walk["given"]), "a question spends nothing"
        assert "Massena" in _ic_log(walk["asked"]) or "Masséna" in _ic_log(walk["asked"])

    def test_standing_him_down_the_same_turn_gives_the_actions_back(self, walk):
        assert "stands down and awaits your orders" in _ic_log(walk["stood_down"])
        assert _ic_actions(walk["stood_down"]) == _ic_actions(walk["begin"])

    def test_the_run_met_no_script_error(self, walk):
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


# ═══════════════════════════ row IC, Session 3b — an army's task ═════════════
# (`SYSTEMS_REFERENCE.md` §234; `docs/audits/ic_client/session3b/README.md` —
# the frames the blind reading read were taken by these same steps at the first
# player's own setup)

@pytest.fixture(scope="module")
def ic3b_walk(tmp_path_factory) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        mp.setenv("DD_B_READBACK", "1")
        mp.setenv("DD_B_STAGE", "1")
        run, sup = _start_engine_run(tmp_path_factory, "ic3b")
    states: dict = {}
    try:
        states["begin"] = _act(run, "click Begin")
        states["formed"] = _act(run, "type form the Army of Italy with Ney, Davout and Soult",
                                meant="other: name an army")
        states["draft"] = _act(run, "draft Army of Italy, take Swabia", meant="other: an army's task")
        states["list"] = _act(run, "key Enter")
        states["untick"] = _act(run, "key Space")          # the commander unticked: nobody follows him
        _act(run, "key Down")
        states["retick"] = _act(run, "key Space")          # a follower ticked: his commander with him
        _act(run, "key Down")
        states["all"] = _act(run, "key Space")
        states["given"] = _act(run, "key Enter")
        states["commander"] = _act(run, "click Ney")
        _act(run, "key Escape")
        states["follower"] = _act(run, "click Davout")
        _act(run, "key Escape")
        states["taken_back"] = _act(run, "click Take back")
        states["goal"] = _act(run, "type the war goal is Bohemia", meant="other: name the war goal")
        states["goal_task"] = _act(run, "type Ney, take the war goal", meant="other: the war goal's task")
        states["goal_list"] = _act(run, "type the war goal is Tyrol", meant="other: change the war goal")
        states["goal_given"] = _act(run, "key Enter")
        # Ney fills the one place: the army's task says so and offers his stand-down
        states["full"] = _act(run, "type Army of Italy under Davout, take Swabia",
                              meant="other: an army's task")
        states["offer"] = _act(run, "click Stand down Ney")
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


def _ic3b_card_fits(state: dict) -> None:
    """The general's card stands whole on the screen: no button cut at its foot."""
    _width, height = state["factor"]["logical_size"]
    rows = _ic_on(state, "SelectionCard")
    assert rows, "the card is open"
    assert max(b["rect"][1] + b["rect"][3] for b in rows) <= height
    assert min(b["rect"][3] for b in rows) >= 30, sorted((b["rect"][3], b["text"]) for b in rows)[:3]


class TestRowIC12AnArmysTask:

    @pytest.fixture(scope="class")
    def walk(self, ic3b_walk):
        assert "error" not in ic3b_walk, ic3b_walk.get("error")
        return ic3b_walk

    def test_the_run_stands_at_the_first_players_own_setup(self, walk):
        state = walk["draft"]
        assert state["ui_scale"]["window"] == pytest.approx(1.8)
        assert state["factor"]["logical_size"] == [2844.0, 765.0]

    def test_typing_the_task_says_who_commands_and_who_follows_before_enter(self, walk):
        said = _pw_said(walk["draft"])
        assert "The Army of Italy · on its own: take Swabia" in said, said[-1500:]
        assert "Ney commands — the highest-ranked of its men who can be set on his own" in said
        assert "Davout and Soult follow him" in said
        assert (walk["draft"].get("command_line") or {}).get("text") == "Army of Italy, take Swabia", \
            "typed, not sent"
        assert "is given its task" not in _ic_log(walk["draft"]), "nothing given by typing"

    def test_enter_shows_one_list_its_commander_and_his_followers_on_one_screen(self, walk):
        card = _ic_card(walk["list"])
        assert card["visible"] is True and card["mode"] == "directive"
        assert card["title"] == "A TASK FOR THE ARMY OF ITALY"
        assert card["who"] == "The Army of Italy: take Swabia, on its own"
        assert [r["marshal"] for r in card["rows"]] == ["Ney", "Davout", "Soult"]
        assert card["members"] == ["Ney", "Davout", "Soult"] and card["total"] == 4
        assert ("Cost: 4 actions (2 + 1 + 1) of the 4 in hand — Ney on his own, 2 men following him."
                in card["total_text"])
        assert card["rows"][0]["text"].startswith("[b]Ney[/b] · on his own: take Swabia · 2 actions")
        assert card["rows"][1]["text"].startswith("[b]Davout[/b] · follow Ney · 1 action")
        _ic_still_and_on_screen(walk["list"])
        # every row stands on the screen at once (pressed: the commander's read-back, whole,
        # pushed the men who follow him below the fold)
        ticks = [b for b in _ic_on(walk["list"], "OrderConfirmCard")
                 if str(b.get("tooltip") or "").startswith("Click to tick or untick")]
        _width, height = walk["list"]["factor"]["logical_size"]
        # a row is a chip with its tick box on it: three of each, all on the screen
        assert sorted(b["kind"] for b in ticks) == ["button"] * 3 + ["chip"] * 3, ticks
        assert all(b["rect"][1] + b["rect"][3] <= height for b in ticks), ticks
        assert not _ic_replies_with(walk["list"], "group"), "the list spends nothing"

    def test_nobody_is_ticked_to_follow_a_commander_who_is_left_out(self, walk):
        untick = _ic_card(walk["untick"])
        assert untick["members"] == [] and untick["give_disabled"] is True
        assert untick["total_text"].startswith("Nobody is ticked — tick Ney to give the army its task")
        assert _ic_card(walk["retick"])["members"] == ["Ney", "Davout"], "a follower ticks his commander"
        assert _ic_card(walk["all"])["members"] == ["Ney", "Davout", "Soult"]

    def test_give_is_one_request_and_the_board_says_the_army_is_on_its_own(self, walk):
        give = walk["given"]
        assert len(_ic_replies_with(give, "group")) == 1                     # ONE request
        log = _ic_log(give)
        assert ("The Army of Italy is given its task — Ney commands, on his own; Davout and Soult follow "
                "him — 4 actions for the 4 in hand.") in log, log
        assert "Army of Italy · 3 corps · on its own" in _pw_buttons(give)
        desk = [str(b.get("text") or "") for b in _ic_on(give, "DeskCard")]
        line = next((t for t in desk if t.startswith("ON THEIR OWN")), "")
        assert ("1 of the 1 you may have · the Army of Italy, 2 men following · they move as each turn "
                "opens") in line, desk

    def test_the_commanders_card_names_his_army_and_stands_whole(self, walk):
        said = _pw_said(walk["commander"])
        assert "Commands the Army of Italy — 2 men follow him." in said, said[-1200:]
        assert "He makes his first move at the start of next turn." in said and "Tonight" not in said
        _ic3b_card_fits(walk["commander"])          # (pressed: his last button ran past the screen's foot)

    def test_a_followers_card_says_whom_he_follows_and_his_night(self, walk):
        said = _pw_said(walk["follower"])
        assert "Follows Ney — the Army of Italy is on its own: take Swabia." in said, said[-1200:]
        assert "He moves with Ney from the start of next turn." in said
        assert "He takes none of your places for men on their own." in said
        _ic3b_card_fits(walk["follower"])

    def test_take_back_undoes_the_whole_task(self, walk):
        assert "Taken back: “Army of Italy, take Swabia”." in _ic_log(walk["taken_back"])
        assert _ic_actions(walk["taken_back"]) == "4/4"
        assert "Army of Italy · 3 corps" in _pw_buttons(walk["taken_back"])

    def test_take_the_war_goal_sets_him_on_his_own_toward_it(self, walk):
        assert "Ney is on his own: take Bohemia." in _ic_log(walk["goal_task"]), _ic_log(walk["goal_task"])

    def test_a_changed_war_goal_is_a_list_that_turns_him(self, walk):
        card = _ic_card(walk["goal_list"])
        assert card["title"] == "A NEW WAR GOAL" and [r["marshal"] for r in card["rows"]] == ["Ney"]
        assert card["total"] == 1 and card["members"] == ["Ney"]
        assert card["note_text"].startswith("The war goal becomes Tyrol (it was Bohemia) when you Give")
        assert card["rows"][0]["text"].startswith("[b]Ney[/b] · on his own: take Tyrol · 1 action")
        assert "Untick him and he keeps to his task (take Bohemia)" in card["rows"][0]["text"]
        _ic_still_and_on_screen(walk["goal_list"])
        log = _ic_log(walk["goal_given"])
        assert "The goal of the war with the Third Coalition is now Tyrol." in log, log
        assert "Ney changes his task: take Tyrol." in log

    def test_the_count_full_offers_the_stand_down_and_the_list_stands_still(self, walk):
        full = _ic_card(walk["full"])
        assert full["offer_text"] == "Stand down Ney (free) and list again", full
        assert full["give_disabled"] is True
        assert full["note_text"].startswith("You already have as many on their own as you may")
        again = walk["offer"]
        assert "Ney stands down and awaits your orders." in _ic_log(again), _ic_log(again)
        card = _ic_card(again)
        assert card["visible"] is True and card["give_disabled"] is False and card["offer_text"] == ""
        assert "Davout" in card["members"]
        # the list drawn again stands where the first stood (the first play's "bobbing"):
        # the same x, and the same top — or, where the new list is the taller (three men
        # may now go), raised only as far as keeps its foot on the screen
        assert card["rect"][0] == pytest.approx(full["rect"][0], abs=1.0)
        _width, height = again["factor"]["logical_size"]
        foot = card["rect"][1] + card["rect"][3]
        if card["rect"][1] != pytest.approx(full["rect"][1], abs=1.0):
            assert card["rect"][3] > full["rect"][3] and card["rect"][1] < full["rect"][1]
            assert foot == pytest.approx(height - 12.0, abs=1.5), (card["rect"], full["rect"])
        assert card["rect"][1] >= 0 and foot <= height and not again.get("off_screen")
        # the one move there is: the held "reading" face becoming the list — never sideways
        moves = _pw_panel_moves(again)
        assert all(m["what"] == "panel OrderConfirmCard/PanelContainer" and m["from"][0] == m["to"][0]
                   and m["from"][2] == m["to"][2] for m in moves), moves

    def test_the_run_met_no_script_error(self, walk):
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


# ═══════════════════════════ row IC, Session 4 — the voice (IC-13) ═══════════
# (`SYSTEMS_REFERENCE.md` §235; `docs/MARSHAL_VOICE_BIBLE.md`.) A marshal's own
# line stands beside his NAME and his small PORTRAIT wherever the text surfaces
# quote him: under the command line as you type, and in the reply when the
# order is given. Pressed first at the first player's setup (Interface Scale
# 1.8 on 5120 x 1377) and at the compact view (2.0 on 1600 x 900) — where it
# showed his line TWICE (once folded into the staff's sentence): fixed, pinned.

def _ic4_steps(run: pathlib.Path, states: dict) -> None:
    states["begin"] = _act(run, "click Begin")
    _act(run, "draft Ney, take Swabia on your own", meant="other: a task on his own")
    # (the reading is fetched after the keystroke: a second look — the caret
    # sent to the line's end, nothing changed — reads it once it has landed)
    states["draft"] = _act(run, "key End")
    states["given"] = _act(run, "key Enter")
    _act(run, "draft Soult, hold Lorraine. If attacked, dig in.", meant="other: exact orders")
    states["exact"] = _act(run, "key End")
    states["exact_given"] = _act(run, "key Enter")
    states["refused"] = _act(run, "type Soult, hold Lorraine on your own",
                             meant="other: asked to act on his own")


def _ic4_walk(tmp_path_factory, name: str, scale: str, window: str) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", scale)
        mp.setenv("DD_B_WINDOW", window)
        mp.setenv("DD_B_READBACK", "1")
        mp.setenv("DD_B_STAGE", "1")
        run, sup = _start_engine_run(tmp_path_factory, name)
    states: dict = {}
    try:
        _ic4_steps(run, states)
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


@pytest.fixture(scope="module")
def ic4_walk(tmp_path_factory) -> dict:
    return _ic4_walk(tmp_path_factory, "ic4", "1.8", "5120x1377")


@pytest.fixture(scope="module")
def ic4_compact(tmp_path_factory) -> dict:
    return _ic4_walk(tmp_path_factory, "ic4_compact", "2.0", "1600x900")


def _ic4_voice_pins(walk: dict) -> None:
    from backend.game_logic import own_voice
    ney = own_voice.pool("Ney", "bold", "ack")
    # as you type: his line under the command line, by NAME — never "He says"
    reading = _ic2_readback(walk["draft"])
    assert "He says:" not in reading, reading
    said = [line for line in ney if f"Ney: “{line}”" in reading]
    assert len(said) == 1, reading
    assert "is on his own" not in _ic_log(walk["draft"]), "nothing given by typing"
    # given: the SAME line, once, with his name — not folded into the staff's sentence too
    log = _ic_log(walk["given"])
    assert "Ney is on his own: take Swabia." in log, log
    assert log.count(said[0]) == 1, log
    assert f"Ney: “{said[0]}”" in log
    # the senior man passed over says so himself
    assert any(f"Murat: “{line}”" in log for line in own_voice.pool("Murat", "bold", "passed_over")), log
    # the letter-following man: his own line as you type; refused in his own words
    exact = _ic2_readback(walk["exact"])
    # (a new campaign draws its own seed, and a seed starts each set at its own
    # place: the line is one of the lines HE can say — his own or his nature's)
    assert any(f"Soult: “{line}”" in exact
               for line in own_voice.pool("Soult", "literal", "exact")), exact
    refused = _ic_log(walk["refused"])
    assert "cannot be set on his own" in refused, refused
    assert any(f"Soult: “{line}”" in refused
               for line in own_voice.pool("Soult", "literal", "refusal")), refused
    assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


class TestRowIC13TheVoice:

    @pytest.fixture(scope="class")
    def walk(self, ic4_walk):
        assert "error" not in ic4_walk, ic4_walk.get("error")
        return ic4_walk

    def test_the_run_stands_at_the_first_players_own_setup(self, walk):
        assert walk["draft"]["ui_scale"]["window"] == pytest.approx(1.8)
        assert walk["draft"]["factor"]["logical_size"] == [2844.0, 765.0]

    def test_his_line_stands_by_his_name_as_typed_and_once_when_given(self, walk):
        _ic4_voice_pins(walk)

    def test_nothing_runs_off_the_screen(self, walk):
        for key in ("draft", "given", "exact", "refused"):
            assert not walk[key].get("off_screen"), (key, walk[key].get("off_screen"))


class TestRowIC13TheVoiceAtTheCompactView:

    @pytest.fixture(scope="class")
    def walk(self, ic4_compact):
        assert "error" not in ic4_compact, ic4_compact.get("error")
        return ic4_compact

    def test_the_run_stands_at_the_compact_view(self, walk):
        assert walk["draft"]["factor"]["logical_size"] == [800.0, 450.0]

    def test_his_line_stands_by_his_name_as_typed_and_once_when_given(self, walk):
        _ic4_voice_pins(walk)


# The census's roads, pressed (row IC, Session 4 — IC-13): the audience window
# heads his proposal with his own line and, given, he says that line once; an
# army's task, given, carries its men's lines into the reply.

@pytest.fixture(scope="module")
def ic4_audience(tmp_path_factory) -> dict:
    """The audience at the compact view: Interface Scale 2.0 on 1600 x 900."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "2.0")
        mp.setenv("DD_B_WINDOW", "1600x900")
        mp.setenv("DD_B_STAGE", "1")
        run, sup = _start_engine_run(tmp_path_factory, "ic4_audience")
    states: dict = {}
    try:
        _act(run, "click Begin")
        _act(run, "type debug set_location Ney Franconia", meant="other: staging")
        states["ney"] = _act(run, "type debug audience Ney", meant="other: staging")
        states["given"] = _act(run, "click Give Ney a task to prove himself")
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


@pytest.fixture(scope="module")
def ic4_army(tmp_path_factory) -> dict:
    """An army's task at the first player's setup (1.8 on 5120 x 1377)."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        mp.setenv("DD_B_READBACK", "1")
        mp.setenv("DD_B_STAGE", "1")
        run, sup = _start_engine_run(tmp_path_factory, "ic4_army")
    states: dict = {}
    try:
        _act(run, "click Begin")
        _act(run, "type form the Army of the Rhine with Davout, Soult and Bernadotte",
             meant="other: name an army")
        _act(run, "draft Army of the Rhine, take Swabia", meant="other: an army's task")
        states["list"] = _act(run, "key Enter")
        states["given"] = _act(run, "key Enter")
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


class TestRowIC13TheAudienceSpeaksAtTheCompactView:

    @pytest.fixture(scope="class")
    def walk(self, ic4_audience):
        assert "error" not in ic4_audience, ic4_audience.get("error")
        return ic4_audience

    def test_his_line_heads_his_proposal_and_he_says_it_once_when_given(self, walk):
        from backend.game_logic import own_voice
        assert walk["ney"]["factor"]["logical_size"] == [800.0, 450.0]
        asks = own_voice.pool("Ney", "bold", "trial_ask")
        window = [str(t.get("text") or "") for t in walk["ney"].get("texts") or []]
        heads = [line for line in asks if any(text.startswith(f"Ney: “{line}”") for text in window)]
        assert len(heads) == 1, window[:6]
        log = _ic_log(walk["given"])
        assert "A TASK TO PROVE HIMSELF" in log
        assert log.count(f"Ney: “{heads[0]}”") == 1, log[-600:]
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


class TestRowIC13AnArmysTaskSpeaks:

    @pytest.fixture(scope="class")
    def walk(self, ic4_army):
        assert "error" not in ic4_army, ic4_army.get("error")
        return ic4_army

    def test_the_given_army_reply_carries_its_mens_lines(self, walk):
        import re
        from backend.game_logic import own_voice
        log = _ic_log(walk["given"])
        found = re.search(r"(\w+) commands, on his own", log)
        assert found, log[-800:]
        lead = found.group(1)
        nature = {"Davout": "careful", "Bernadotte": "careful"}.get(lead, "bold")
        kinds = ("ack", "object", "bolder", "careful", "remembers")
        his = [line for kind in kinds for line in own_voice.pool(lead, nature, kind)]
        said = [line for line in his if f"{lead}: “{line}”" in log]
        assert len(said) == 1, log[-800:]
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


# ═══════════════════════ row IC, Session 4b — his own judgement ═════════════
# (`SYSTEMS_REFERENCE.md` §236; the user's "He moves at turn start" and his
# correction: an autonomous army whose orders are goals that weigh in its
# decision tree.) Pressed at the first player's own setup and at the small
# window: a man set on his own with NO task ("act on your own"), the turn
# ended, the morning's report of what he did as the turn opened, his card's
# "This turn", and his nature on the Generals page.

def _ic4b_steps(run: pathlib.Path, by_button: bool) -> dict:
    states: dict = {}
    answered: list = []
    states["begin"] = _act(run, "click Begin")
    if by_button:
        # the card's own button (the server's `buttons.offered.own_free`)
        states["card_before"] = _act(run, "click Ney")
        face = next((b for b in _ic_on(states["card_before"], "SelectionCard")
                     if str(b.get("text") or "").startswith("Set him on his own")), None)
        assert face is not None, sorted(_ic2_faces(states["card_before"]))
        states["given"] = _ic_press(run, face)
        _act(run, "key Escape")
    else:
        states["draft"] = _act(run, "draft Ney, act on your own", meant="other: on his own, no task")
        states["given"] = _act(run, "key Enter")
    # the morning's lines arrive with the End Turn press and the answers after
    # it: gathered across every state of the chain, not read off its last one
    log: list = []
    state = _act(run, "click End Turn (E)")
    log += list(state.get("terminal_new") or [])
    if _ic_on(state, "TurnEndList"):
        state = _act(run, "click End Turn (E)")          # the list stops once; the button stays one press away
        log += list(state.get("terminal_new") or [])
    for _ in range(14):
        if not _modal(state) and state.get("scene") == "main":
            break
        state = _answer_chain_step(run, state, answered)
        log += list(state.get("terminal_new") or [])
    states["ended"] = state
    states["morning"] = " ".join(log)
    states["answered"] = answered
    states["card"] = _act(run, "click Ney")          # (his piece may stand off the small window's map)
    _act(run, "key Escape")
    states["generals"] = _act(run, "key alt+g")        # (the small window's top bar is icons)
    two = next((b for b in _ic_on(states["generals"], "MarshalManagement")
                if str(b.get("text") or "") == "2"), None)
    # Ney, the second on the roll (the small window draws the roll as portraits:
    # its number key selects him there)
    states["generals_ney"] = _ic_press(run, two) if two else _act(run, "key 2")
    return states


def _answer_chain_step(run: pathlib.Path, state: dict, answered: list) -> dict:
    """One answer of `_answer_chain` (the same pick), returning the next state."""
    modal = _modal(state)
    pick, live = _pick_answer(state)
    if pick is None and "battle_diorama" in " ".join(modal):
        w, h = state["factor"]["logical_size"]
        answered.append("battle_diorama: skip")
        return _act(run, f"click_at {int(w / 2)} {int(h / 2)}")
    assert pick is not None, f"no answer on {modal}: {[b['text'] for b in live]}"
    r = pick["rect"]
    answered.append(f"{modal}: {pick['text']}")
    return _act(run, f"click_at {int(r[0] + r[2] / 2)} {int(r[1] + r[3] / 2)}")


def _ic4b_walk_at(tmp_path_factory, name: str, scale: str, window: str, by_button: bool) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", scale)
        mp.setenv("DD_B_WINDOW", window)
        mp.setenv("DD_B_READBACK", "1")
        mp.setenv("DD_B_STAGE", "1")
        run, sup = _start_engine_run(tmp_path_factory, name)
    states: dict = {}
    try:
        states.update(_ic4b_steps(run, by_button))
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


@pytest.fixture(scope="module")
def ic4b_walk(tmp_path_factory) -> dict:
    """The first player's own setup: Interface Scale 1.8 on 5120 x 1377."""
    return _ic4b_walk_at(tmp_path_factory, "ic4b", "1.8", "5120x1377", by_button=True)


@pytest.fixture(scope="module")
def ic4b_compact(tmp_path_factory) -> dict:
    """The small window: Interface Scale 2.0 on 1600 x 900."""
    return _ic4b_walk_at(tmp_path_factory, "ic4b_compact", "2.0", "1600x900", by_button=False)


def _ic4b_pins(walk: dict) -> None:
    if "draft" in walk:                               # the typed road: answered before Enter
        reading = _ic2_readback(walk["draft"])
        assert "on his own: make war as he sees fit" in reading, reading
        assert "At the start of next turn he means to" in reading, reading
    log = _ic_log(walk["given"])
    assert "Ney is on his own: make war as he sees fit. He makes his first move at the start of next turn." \
        in log, log[-600:]
    begin, given = _ic_actions(walk["begin"]), _ic_actions(walk["given"])
    if begin and given:                               # (the counter as the wide desk draws it)
        assert int(begin.split("/")[0]) - int(given.split("/")[0]) == 2, "on his own costs two actions"
    # the morning report says what he did as the turn opened: the dispatch's
    # own line for him (the probe keeps a step's last 80 terminal lines, and
    # the dispatch fills them; the "as this turn opened" block printed just
    # above it is pinned at the server's road, `strategic_reports`)
    morning = walk["morning"]
    assert "On his own: make war as he sees fit. This turn: Ney " in morning, morning[-1500:]
    assert "Tonight" not in morning
    generals = _pw_said(walk["generals_ney"]) + " " + " ".join(_pw_buttons(walk["generals_ney"]))
    assert "Bold" in generals, "his nature stands on his Generals card"
    assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


class TestRowIC4bHisOwnJudgement:

    @pytest.fixture(scope="class")
    def walk(self, ic4b_walk):
        assert "error" not in ic4b_walk, ic4b_walk.get("error")
        return ic4b_walk

    def test_the_run_stands_at_the_first_players_own_setup(self, walk):
        assert walk["given"]["ui_scale"]["window"] == pytest.approx(1.8)
        assert walk["given"]["factor"]["logical_size"] == [2844.0, 765.0]

    def test_on_his_own_with_no_task_moves_at_turn_start_and_says_what_he_did(self, walk):
        _ic4b_pins(walk)

    def test_the_button_says_its_price_before_the_press(self, walk):
        face = next(str(b.get("text") or "") for b in _ic_on(walk["card_before"], "SelectionCard")
                    if str(b.get("text") or "").startswith("Set him on his own"))
        assert "2 actions" in face, face

    def test_the_price_reads_on_the_desk(self, walk):
        assert _ic_actions(walk["begin"]) and _ic_actions(walk["given"]), "the wide desk shows the counter"

    def test_his_card_says_what_he_did_this_turn_and_nothing_ahead(self, walk):
        said = _pw_said(walk["card"])
        assert "This turn: Ney " in said, said[-800:]
        assert "Tonight" not in said and "tonight" not in said

    def test_his_card_says_each_thing_once_and_no_task_reads_as_none(self, walk):
        # pressed in the real client (the screens' reading, Session 4b): the
        # state's own words "(makes his first move at the start of next turn)"
        # stood right above the same sentence, and a man with NO task read
        # "Your task guides him"
        card = " | ".join(str(t.get("text") or "") for t in walk["given"].get("texts") or []
                          if t.get("surface") == "SelectionCard")
        assert card.count("first move at the start of next turn") == 1, card[-900:]
        assert "No task: each turn he weighs the chances around him" in card, card[-900:]
        assert "Your task guides him" not in card

    def test_nothing_runs_off_the_screen(self, walk):
        for key in ("card_before", "given", "card"):
            assert not walk[key].get("off_screen"), (key, walk[key].get("off_screen"))


class TestRowIC4bHisOwnJudgementAtTheCompactView:

    @pytest.fixture(scope="class")
    def walk(self, ic4b_compact):
        assert "error" not in ic4b_compact, ic4b_compact.get("error")
        return ic4b_compact

    def test_the_run_stands_at_the_small_window(self, walk):
        assert walk["draft"]["ui_scale"]["window"] == pytest.approx(2.0)

    def test_on_his_own_with_no_task_moves_at_turn_start_and_says_what_he_did(self, walk):
        _ic4b_pins(walk)


# ═══════════════ row IC, Session 4b, continued — what we know of their plans ═══════════════
# (`SYSTEMS_REFERENCE.md` §236.8; the user's "fix warplans", then "Switch them on".) Pressed at
# the first player's own setup: agents sent to Austria from the Cabinet, three turns ended, then
# the war's page and the province window under Mack. Pressing found both rows pinned here: the
# Folded war page never listed what the spy brought back (IC4b-32), and the command window told
# an enemy's written orders as the player's — "Mack holds at Swabia, per your orders" (IC4b-31).
# A new campaign draws its own seed, so the plan Austria draws varies; the pins read the words
# every plan shares.

def _map_label(state: dict, name: str):
    """A name on the map as the map draws it: alone ("Mack"), or heading the
    corps that share his province ("Mack · 1 more"). FUN2B-24 (the hook's
    second run): on the Milan road a second Austrian corps joined Mack in
    Swabia by turn 4, his label read "Mack · 1 more", and the walk, which
    looked for "Mack" alone, found no one."""
    for lab in state.get("map") or []:
        text = str(lab.get("text") or "")
        if text == name or text.startswith(name + " · "):
            return lab
    return None


def _ic4b_plans_steps(run: pathlib.Path) -> dict:
    states: dict = {}
    log: list = []
    states["begin"] = _act(run, "click Begin")
    _act(run, "click ⚖ Cabinet")
    states["austria"] = _act(run, "click Austria")
    w, h = states["austria"]["factor"]["logical_size"]
    state = _act(run, f"scroll {int(w * 0.63)} {int(h * 0.61)} down 8")   # the wizard's action list
    gather = next((b for b in state.get("buttons", []) if str(b.get("text")) == "Gather Intel"), None)
    assert gather is not None, [b.get("text") for b in state.get("buttons", [])][:40]
    state = _ic_press(run, gather)
    begin = next((b for b in state.get("buttons", []) if str(b.get("text")) == "Begin mission"), None)
    assert begin is not None, [b.get("text") for b in state.get("buttons", [])][:20]
    state = _ic_press(run, begin)
    log += list(state.get("terminal_new") or [])
    answered: list = []
    for _ in range(3):                                # the mission's three turns
        state = _act(run, "click End Turn (E)")
        log += list(state.get("terminal_new") or [])
        if _ic_on(state, "TurnEndList"):
            state = _act(run, "click End Turn (E)")
            log += list(state.get("terminal_new") or [])
        for _ in range(16):
            if not _modal(state) and state.get("scene") == "main":
                break
            state = _answer_chain_step(run, state, answered)
            log += list(state.get("terminal_new") or [])
    states["log"] = log
    states["answered"] = answered
    war = next((b for b in state.get("buttons", []) if b.get("surface") == "WarStatusPanel"
                and str(b.get("text") or "").startswith("War ")), None)
    assert war is not None, [b.get("text") for b in _ic_on(state, "WarStatusPanel")]
    states["war_page"] = _ic_press(run, war)
    state = _act(run, "key Escape")
    mack = _map_label(state, "Mack")
    assert mack is not None, [lab.get("text") for lab in state.get("map") or []]
    r = mack["rect"]
    states["province"] = _act(run, f"click_at {int(r[0] + r[2] / 2)} {int(r[1] + r[3] / 2 + 5)}")
    return states


@pytest.fixture(scope="module")
def ic4b_plans_walk(tmp_path_factory) -> dict:
    """The first player's own setup: Interface Scale 1.8 on 5120 x 1377."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", "1.8")
        mp.setenv("DD_B_WINDOW", "5120x1377")
        mp.setenv("DD_B_READBACK", "1")
        run, sup = _start_engine_run(tmp_path_factory, "ic4b_plans")
    states: dict = {}
    try:
        states.update(_ic4b_plans_steps(run))
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


class TestRowIC4bWhatWeKnowOfTheirPlans:

    @pytest.fixture(scope="class")
    def walk(self, ic4b_plans_walk):
        assert "error" not in ic4b_plans_walk, ic4b_plans_walk.get("error")
        return ic4b_plans_walk

    def test_the_spys_report_names_their_written_orders(self, walk):
        said = " ".join(walk["log"])
        assert "His report on their written orders: Mack " in said, said[-1200:]

    def test_the_war_page_lists_what_we_know_of_their_plans(self, walk):
        page = " || ".join(str(t.get("text") or "") for t in walk["war_page"].get("texts") or []
                           if t.get("surface") == "WarDetailPopup")
        assert "What we know of their plans" in page, page[-900:]
        known = page[page.index("What we know of their plans"):]
        assert "Mack " in known                              # his orders, whichever plan was drawn
        assert "(learned this turn, from your spy's report)" in known
        assert "Austria's corps " in known                   # "favour no province" / "lean toward X"
        assert known.index("What we know of their plans") < known.index("Recent Battles")

    def test_the_province_window_gives_mack_his_known_orders(self, walk):
        panel = " || ".join(str(t.get("text") or "") for t in walk["province"].get("texts") or []
                            if t.get("surface") == "RegionPanel")
        assert "Nature: To the letter" in panel, panel[-800:]
        assert "Known orders (learned this turn, from your spy's report): Mack " in panel

    def test_no_line_tells_an_enemys_orders_as_yours(self, walk):
        said = " ".join(walk["log"])
        assert "Mack holds at" not in said and "per your orders" not in said, said[-1200:]

    def test_nothing_runs_off_the_screen_and_no_script_errs(self, walk):
        for key in ("war_page", "province"):
            assert not walk[key].get("off_screen"), (key, walk[key].get("off_screen"))
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


# ════════════════════════════════════════════════════════════════════════════
# Row FR, Session FR-1 (November 23, 2026) — the four rows on the player's
# screen, pressed in the real client at the first player's own setup
# (Interface Scale 1.8 on 5120 x 1377) and at the small window (2.0 on
# 1600 x 900):
#   WS-10   a pinned ledger leaves the bare digits to the war room (the
#           selected marshal's card) and turns its books on Alt+digit;
#   FR1-1   the pinned flag is read where it is set — the pinned Generals
#           screen stands aside (UI-6's rule, dead until this session) and a
#           ledger let go takes its bare digits back;
#   PW3-D1  five courts stand on the Cabinet's first page;
#   IC3-N1  the Congress page says what a titled province is before it uses
#           the word; a dashed (locked) order button is said on the card;
#   IC2-N1  the line on a row of its own (its width is pinned by
#           TestRowIC7TheButtons::test_the_command_line_shows_the_task_being_typed).
# The probe before the build: `docs/audits/fr1_client/before/README.md`.
# ════════════════════════════════════════════════════════════════════════════

_FR1_BOOKS = ("FORCES", "TERRITORIES", "ECONOMY", "INTELLIGENCE", "MANPOWER", "ORDERS", "ADMIRALTY", "LAWS")
_FR1_COURTS = ("Britain", "Russia", "Austria", "Spain", "Bavaria", "Kingdom of Italy", "Prussia", "Ottoman Empire",
               "Portugal", "Hanover", "Naples", "Sardinia", "Hesse", "Holland", "Switzerland", "Saxony",
               "Papal States", "Denmark", "Sweden", "Württemberg", "Baden")


def _fr1_text(state: dict, surface: str) -> str:
    return " || ".join(str(t.get("text") or "") for t in state.get("texts") or [] if t.get("surface") == surface)


def _fr1_book(state: dict) -> str:
    """The Strategic Ledger's open book, by the heading its page opens with."""
    for t in state.get("texts") or []:
        if t.get("surface") != "StrategicLedger":
            continue
        head = str(t.get("text") or "").lstrip()
        for book in _FR1_BOOKS:
            if head == book or head.startswith(book + " ") or head.startswith(book + "\n"):
                return book
    return ""


def _fr1_generals_detail(state: dict) -> str:
    """The Generals screen's detail: the marshal it shows (its first line)."""
    for t in state.get("texts") or []:
        if t.get("surface") == "MarshalManagement":
            return str(t.get("text") or "").strip()
    return ""


def _fr1_courts_in_view(state: dict) -> list:
    """The Cabinet's court rows standing WHOLE in view — the court's button at
    its full height (36 folded, 44 on the page), not cut by the list's scroll."""
    out = []
    for b in _ic_on(state, "DiplomacyWizard"):
        name = str(b.get("text") or "")
        r = b.get("rect") or [0, 0, 0, 0]
        if name in _FR1_COURTS and float(r[3]) >= 35.0:
            out.append(name)
    return out


def _fr1_reopen_cabinet(run: pathlib.Path) -> dict:
    """The Cabinet opened again in the same turn, read on a fresh frame once the
    new request's answer has drawn. (Its first-open line still stands: S14d keeps
    a line on every payload of the turn it was first shown —
    `first_open.line_for`, "the line must not vanish mid-read" — and drops it
    the next turn.)"""
    _act(run, "key F1")
    return _act(run, "look")


def _fr1_steps(run: pathlib.Path, states: dict) -> None:
    states["begin"] = _act(run, "click Begin")
    # IC2-N1: a task typed on the line; Cabinet and End Turn stand on the row under it
    states["draft"] = _act(run, "draft Ney, retreat if outnumbered")
    _act(run, "key Ctrl+A")
    _act(run, "key Delete")
    # FR1-2: the longest reading there is — a task on his own — keeps the window's head in view
    states["long_reading"] = _act(run, "draft Davout, hold Rhineland on your own")
    _act(run, "key Ctrl+A")
    _act(run, "key Delete")
    # WS-10: the Strategic Ledger pinned at its third book, a corps selected, the caret off the line
    _act(run, "key Alt+t")
    _act(run, "key Alt+3")
    states["ledger_pinned"] = _act(run, "click Pin")
    states["murat"] = _act(run, "click Murat")
    states["off_line"] = _act(run, "click ECONOMY")
    states["ledger_digit"] = _act(run, "key 4")       # the card's Scout — never the ledger's fourth book
    states["ledger_alt"] = _act(run, "key Alt+1")     # the book turns on Alt
    # let go, the ledger is a book again and its bare digits are its own (FR1-1: the flag removed)
    _act(run, "click Unpin")
    _act(run, "key Alt+t")
    states["book_tab"] = _act(run, "click TERRITORIES")
    states["book_digit"] = _act(run, "key 3")
    _act(run, "key Escape")
    # FR1-1: the Generals screen pinned stands aside for the selected marshal's card
    _act(run, "key Alt+g")
    states["generals_pinned"] = _act(run, "click Pin")
    _act(run, "click Davout")
    _act(run, "key Escape")                                    # let him go (the line keeps the caret)
    x, y = _ic2_piece(states["begin"], "Britain")
    _act(run, f"click_at {int(x)} {int(y) + 30}")              # a province: the map takes the caret
    states["davout"] = _act(run, "click Davout")
    states["generals_digit"] = _act(run, "key 4")
    _act(run, "click Unpin")
    # PW3-D1: the Cabinet's first page — its first opening (the first-open line at its head) and a second
    states["cabinet"] = _act(run, "key F1")
    _act(run, "key Escape")
    states["cabinet_again"] = _fr1_reopen_cabinet(run)
    _act(run, "key Escape")
    # IC3-N1: the Congress page names what a titled province is before it uses the word
    _act(run, "key Alt+d")
    states["congress"] = _act(run, "key Alt+7")


def _fr1_walk(tmp_path_factory, name: str, scale: str, window: str, steps) -> dict:
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DD_B_UI_SCALE", scale)
        mp.setenv("DD_B_WINDOW", window)
        mp.setenv("DD_B_READBACK", "1")
        run, sup = _start_engine_run(tmp_path_factory, name)
    states: dict = {}
    try:
        steps(run, states)
    except Exception as exc:      # noqa: BLE001 - re-raised by the class's own fixture
        states["error"] = repr(exc)
    finally:
        _stop_engine_run(run, sup)
    states["run"] = json.loads((run / "run.json").read_text(encoding="utf-8"))
    return states


@pytest.fixture(scope="module")
def fr1_walk(tmp_path_factory) -> dict:
    return _fr1_walk(tmp_path_factory, "fr1", "1.8", "5120x1377", _fr1_steps)


class TestRowFR1TheFourRows:

    @pytest.fixture(scope="class")
    def walk(self, fr1_walk):
        assert "error" not in fr1_walk, fr1_walk.get("error")
        return fr1_walk

    def test_the_run_stands_at_the_first_players_own_setup(self, walk):
        assert walk["begin"]["ui_scale"]["window"] == pytest.approx(1.8)
        assert walk["begin"]["factor"]["logical_size"] == [2844.0, 765.0]

    # ── WS-10 ────────────────────────────────────────────────────────────────
    def test_a_pinned_ledger_leaves_the_bare_digit_to_the_card(self, walk):
        assert walk["off_line"]["open"]["pinned"] == "ledger"
        assert not walk["off_line"]["command_line"]["focused"], "the caret is off the line"
        assert _fr1_book(walk["off_line"]) == "ECONOMY"
        after = walk["ledger_digit"]
        assert "► Murat, scout" in _ic_log(after), _ic_log(after)
        assert _fr1_book(after) == "ECONOMY", "the ledger kept its book"

    def test_the_pinned_ledger_turns_on_alt(self, walk):
        assert walk["ledger_alt"]["open"]["pinned"] == "ledger"
        assert _fr1_book(walk["ledger_alt"]) == "FORCES"

    def test_let_go_the_book_takes_its_bare_digits_again(self, walk):
        assert walk["book_tab"]["open"]["pinned"] == ""
        assert _fr1_book(walk["book_tab"]) == "TERRITORIES"
        assert _fr1_book(walk["book_digit"]) == "ECONOMY"

    # ── FR1-1 ────────────────────────────────────────────────────────────────
    def test_the_pinned_generals_screen_stands_aside(self, walk):
        before = walk["davout"]
        assert before["open"]["pinned"] == "generals"
        assert not before["command_line"]["focused"], "the caret is off the line"
        shown = _fr1_generals_detail(before)
        after = walk["generals_digit"]
        assert "► Davout, scout" in _ic_log(after), _ic_log(after)
        assert _fr1_generals_detail(after) == shown, "the Generals screen kept its marshal"

    # ── PW3-D1 ───────────────────────────────────────────────────────────────
    def test_five_courts_stand_on_the_cabinets_first_page(self, walk):
        for key in ("cabinet", "cabinet_again"):
            courts = _fr1_courts_in_view(walk[key])
            assert len(courts) >= 5, (key, courts)
        # the first opening carries the first-open line at its head, and still five
        assert "Any court may be treated with here, Sire" in _fr1_text(walk["cabinet"], "DiplomacyWizard")

    def test_the_designs_status_rides_its_door(self, walk):
        faces = [str(b["text"]) for b in _ic_on(walk["cabinet"], "DiplomacyWizard")]
        assert any(f.startswith("The Emperor's Designs — ") for f in faces), faces
        assert "Formable Nations" in faces

    # ── IC3-N1 ───────────────────────────────────────────────────────────────
    def test_the_congress_page_says_what_a_titled_province_is_first(self, walk):
        page = _fr1_text(walk["congress"], "DiplomaticLedger")
        assert "A titled province is one held for good" in page, page[:600]
        assert page.index("A titled province is") < page.index(" titled"), page[:600]

    def test_the_card_says_what_a_dashed_button_is(self, walk):
        assert "A dashed button is an order not open to him now" in _fr1_text(walk["murat"], "SelectionCard")

    # ── IC2-N1 ───────────────────────────────────────────────────────────────
    def test_cabinet_and_end_turn_stand_under_the_line(self, walk):
        state = walk["draft"]
        line = state["command_line"]["rect"]
        assert line[2] >= 360, f"the command line is {line[2]} px wide"
        for face in ("⚖ Cabinet", "End Turn (E)"):
            b = _ic2_btn(state, "BottomLeftUI", face)
            assert b["rect"][1] >= line[1] + line[3], (face, b["rect"], line)
        top = min(float(t["rect"][1]) for t in state["texts"] if t.get("surface") == "BottomLeftUI")
        assert top >= 34.0, f"the command window's head stands at {top}, under the top bar"

    # ── FR1-2 ────────────────────────────────────────────────────────────────
    def test_a_long_reading_keeps_the_windows_head_in_view(self, walk):
        state = walk["long_reading"]
        reading = next(t for t in state["texts"] if t.get("surface") == "BottomLeftUI"
                       and "on his own: hold Rhineland" in str(t.get("text") or ""))
        width, height = state["factor"]["logical_size"]
        assert reading["rect"][3] <= height * 0.4 + 1, reading["rect"]       # it scrolls past its share
        top = min(float(t["rect"][1]) for t in state["texts"] if t.get("surface") == "BottomLeftUI")
        assert top >= 34.0, f"the command window's head stands at {top}, under the top bar"
        assert "2 actions of the 4 in hand" in str(reading.get("text")), "IC3-N1: the price against the pool"

    def test_the_run_met_no_script_error(self, walk):
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]


def _fr1_compact_steps(run: pathlib.Path, states: dict) -> None:
    states["begin"] = _act(run, "click Begin")
    states["draft"] = _act(run, "draft Ney, retreat if outnumbered")
    _act(run, "key Ctrl+A")
    _act(run, "key Delete")
    states["cabinet"] = _act(run, "key F1")
    _act(run, "key Escape")
    states["cabinet_again"] = _fr1_reopen_cabinet(run)


@pytest.fixture(scope="module")
def fr1_compact(tmp_path_factory) -> dict:
    return _fr1_walk(tmp_path_factory, "fr1_compact", "2.0", "1600x900", _fr1_compact_steps)


class TestRowFR1AtTheSmallWindow:
    """The slim bar keeps End Turn on the line's row (Session UI-6's form — its
    height is the scarce thing there); the Cabinet's taller list still fits."""

    @pytest.fixture(scope="class")
    def walk(self, fr1_compact):
        assert "error" not in fr1_compact, fr1_compact.get("error")
        return fr1_compact

    def test_the_bar_keeps_end_turn_on_the_lines_row(self, walk):
        state = walk["draft"]
        assert state["factor"]["logical_size"] == [800.0, 450.0]
        line = state["command_line"]["rect"]
        end = _ic2_btn(state, "BottomLeftUI", "End Turn")
        assert abs(float(end["rect"][1]) - float(line[1])) < float(line[3]), (end["rect"], line)

    def test_the_cabinet_stands_whole_on_the_small_window(self, walk):
        """At 800 x 450 the turn's openings are the head and the first-open line
        (it stands all that turn), the courts a scroll below — as before this
        session, with less room then (the list's share and the Designs fold give
        it 62 px more); the page stands whole, its doors and its foot in view."""
        for key in ("cabinet", "cabinet_again"):
            state = walk[key]
            assert not state.get("off_screen"), (key, state.get("off_screen"))
            faces = [str(b["text"]) for b in _ic_on(state, "DiplomacyWizard")]
            assert "Cancel" in faces and "Formable Nations" in faces, (key, faces)
            assert "▼ more below" in _fr1_text(state, "DiplomacyWizard"), key

    def test_the_run_met_no_script_error(self, walk):
        assert walk["run"]["n_script_errors"] == 0, walk["run"]["script_errors"]
