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
            assert "OPEN — owner S14h" in line, c["id"]
            assert f"tests/test_s14h_the_third_measure_rows.py::Test{c['id'].replace('-', '')}" in line, c["id"]
            if c.get("dr_id"):
                assert any(ln.startswith(f"| **{c['dr_id']}** |") for ln in design.splitlines()), c["dr_id"]
                assert c["dr_id"] in line, c["id"]
            for s in c["sightings"]:
                assert (REPO / s["frame"]).is_file(), s["frame"]
                assert s["frame"] in line, (c["id"], s["frame"])
        # the instrument row and the done-when's own question
        assert any(ln.startswith("| **S14G-I1** |") and "OPEN — owner S14h" in ln for ln in bugs.splitlines())
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
