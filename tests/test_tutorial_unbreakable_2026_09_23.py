"""The School of War cannot be broken by the war (September 23, 2026).

The user's report: *"I had issues of not being able to finish tasks because
conditions in game grabbed it"* — a card demanded an order the board no
longer allowed, and the only way out was the whole-tutorial Skip. The rebuilt
card (tutorial_overlay.gd) answers with three mechanisms, each pinned here
by DRIVING the real overlay over real backend responses:

* a refusal of the card's OWN suggested order releases the step at once,
  with the reason on the next card (main.gd notes what was sent;
  `_refused_our_order` reads the refusal);
* every card but the last carries a `Skip this lesson` chip;
* the turn-gate catch-up stays as the floor under both.

And the three new lessons: **VII. The Cabinet** (diplomacy — the chip opens
the REAL wizard on Austria, the step completes when the mission the wizard
confirms is live), **IX. The Marshalate** (trust, glory, relationships,
envy — a self-releasing card), **XVI. The Wooden Wall** (the naval rule the
lesson cannot stage — self-releasing). The pushback/trust/defiance
explanation rides cards IV/V.

The backend half of every path below runs in-process on the real tutorial
scenario through `/new_game {"scenario": "tutorial"}` and the same answer
endpoints the client uses; the recorded responses are then fed to the real
`tutorial_overlay.tscn` through `tools/tutorial_overlay_harness.gd`. The
driven classes SKIP without a Godot engine — and a skip is not a pass.
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
OVERLAY = PROJECT / "scripts" / "tutorial_overlay.gd"
MAIN_GD = PROJECT / "scripts" / "main.gd"
HARNESS = REPO / "tools" / "tutorial_overlay_harness.gd"
LESSON = REPO / "tools" / "playtest_scripts" / "tutorial_lesson.json"
LESSON_TRUST = REPO / "tools" / "playtest_scripts" / "tutorial_lesson_trust.json"

_CANDIDATES = [
    os.environ.get("GODOT_BIN", ""),
    r"C:\Users\User\Downloads\Godot_v4.4.1-stable_win64.exe"
    r"\Godot_v4.4.1-stable_win64.exe",
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
        elif shutil.which(candidate):
            return shutil.which(candidate)
    return None


def _drive_overlay(spec: dict, work: pathlib.Path, timeout: int = 300) -> dict:
    engine = _engine()
    if engine is None:
        pytest.skip("Godot engine not on this machine — the driven pins skip, "
                    "and a skip is not a pass")
    out = work / "result.json"
    log = work / "godot.log"
    spec = dict(spec, out=str(out))
    spec_path = work / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    env = dict(os.environ, TUT_SPEC=str(spec_path), TUT_OUT=str(out))
    proc = subprocess.run(
        [engine, "--headless", "--path", str(PROJECT), "--log-file", str(log),
         "--script", str(HARNESS)],
        capture_output=True, text=True, timeout=timeout, env=env, cwd=str(PROJECT))
    if not out.is_file():
        pytest.fail("the harness wrote no result\n"
                    f"exit={proc.returncode}\nstderr tail:\n{proc.stderr[-2000:]}")
    result = json.loads(out.read_text(encoding="utf-8"))
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    result["_script_errors"] = log_text.count("SCRIPT ERROR")
    assert "error" not in result, result.get("error")
    assert result["_script_errors"] == 0, log_text[-3000:]
    return result


# ═══════════════════════════════════════════════════════════════════════
# The lesson, driven at the real endpoints
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def lesson(monkeypatch, tmp_path):
    """A TestClient on the REAL tutorial scenario, booted through the same
    /new_game handshake the main menu uses (test_tutorial_position7's
    idiom: /new_game rebinds both module globals — read `M.world`)."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    with patch("backend.save_manager.SAVE_DIR", save_dir):
        import backend.main as M
        from backend.commands.parser import CommandParser

        M._reset_world_state()
        monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
        with TestClient(M.app) as client:
            boot = client.post("/new_game", json={"scenario": "tutorial"}).json()
            assert boot.get("success") is True, boot
            assert boot["game_state"]["scenario_name"] == "tutorial"
            yield client, M, boot
        M._reset_world_state()


class Recorder:
    """Every response the client would have handed to `observe()`, in order,
    with what main.gd would have `note_sent` before it."""

    def __init__(self, client, module, boot):
        self.client = client
        self.M = module
        self.responses = [boot]
        self.sent = {}

    @property
    def world(self):
        return self.M.world

    def say(self, line):
        reply = self.client.post("/command", json={"command": line}).json()
        self.sent[str(len(self.responses))] = line
        self.responses.append(reply)
        return reply

    def answer_objection(self, choice="insist"):
        reply = self.client.post("/respond_to_objection", json={"choice": choice}).json()
        self.responses.append(reply)
        return reply

    def answer_capture(self, choice="secure"):
        pending = self.world.pending_capture_choice or {}
        body = {"choice": choice}
        if isinstance(pending, dict) and pending.get("dialogue_id") is not None:
            body["dialogue_id"] = pending.get("dialogue_id")
        reply = self.client.post("/capture_choice", json=body).json()
        self.responses.append(reply)
        return reply

    def answer_dialogue(self, choice, reply_with_dialogue=None):
        dialogue = reply_with_dialogue or (self.world.pending_diplomatic_dialogue or {})
        body = {"choice": choice}
        if isinstance(dialogue, dict) and dialogue.get("dialogue_id") is not None:
            body["dialogue_id"] = dialogue.get("dialogue_id")
        reply = self.client.post("/respond_to_diplomatic_dialogue", json=body).json()
        self.responses.append(reply)
        return reply

    def end_turn(self):
        return self.say("end turn")

    def settle(self, reply=None):
        """Answer whatever the board put up — the client's own answers, in
        the lesson's own counsel: an objection is INSISTED on, a capture is
        SECURED, a mission confirm is BEGUN. The engine's unseeded defiance
        and combat rolls make every path RNG-shaped, so a driven test never
        assumes which popup comes; it answers what came."""
        for _ in range(4):
            world = self.world
            reply = reply or {}
            if world.pending_objection or reply.get("pending_objection")                     or reply.get("state") == "awaiting_player_choice":
                reply = self.answer_objection("insist")
                continue
            if world.pending_capture_choice:
                reply = self.answer_capture("secure")
                continue
            dialogue = world.pending_diplomatic_dialogue or {}
            if dialogue.get("type") == "mission":
                reply = self.answer_dialogue("start_mission", dialogue)
                continue
            return reply
        return reply

    def end_turn_until(self, turn, limit=4):
        """End turns (answering popups between) until the world reaches
        `turn`; a HARD-STOP question can refuse one `end turn`."""
        for _ in range(limit):
            if self.world.current_turn >= turn:
                return
            self.settle(self.end_turn())
        assert self.world.current_turn >= turn, (self.world.current_turn, turn)

    def spec(self, clicks=None):
        return {"responses": self.responses, "sent": self.sent,
                "clicks": clicks or {}}


def _ids(result):
    return [row["id"] for row in result["steps"]]


# ═══════════════════════════════════════════════════════════════════════
# 1. The idle Emperor — thirteen `end turn`s and nothing else
# ═══════════════════════════════════════════════════════════════════════

class TestTheIdleEmperorStillReachesTheEnd:

    def test_the_backend_plays_thirteen_empty_turns(self, lesson):
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        for _ in range(13):
            reply = rec.end_turn()
            assert reply.get("success") is True, reply.get("message")
            # a popup may be pending (an objection cannot — nothing was
            # ordered); a capture choice cannot either.
            assert not M.world.pending_capture_choice
        assert M.world.current_turn >= 13
        return rec

    def test_the_card_reaches_the_handoff_by_the_gate_of_the_last_page(self, lesson, tmp_path):
        """No step may hold the idle player past its gate + 2: the catch-up
        walks every unfired card, and the handoff is reached by turn 12."""
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        for _ in range(13):
            rec.end_turn()
        result = _drive_overlay(rec.spec(), tmp_path)
        rows = result["steps"]
        assert rows[0]["active"] is True and rows[0]["id"] == "survey"
        # the FLOOR: on every recorded response the card is never more than
        # two turns behind its current step's gate
        gates = {sid: gate for sid, gate, _title in _overlay_steps()}
        for row in rows:
            assert row["turn"] <= gates[row["id"]] + 2, row
        assert rows[-1]["id"] == "handoff", _ids(result)
        assert rows[-1]["done"] is False  # the handoff waits for the player's Conclude
        # every card BEFORE the handoff offered the skip chip; the handoff offers Conclude
        for row in rows[:-1]:
            if row["id"] != "handoff":
                assert "skipstep:" in row["body"], row["id"]
        assert "skipdone:" in rows[-1]["body"]
        assert "skipstep:" not in rows[-1]["body"]

    def test_the_backend_mirror_never_names_a_gate_the_turn_has_not_reached(self, lesson, tmp_path):
        """The mirror (`tutorial_state`) is approximate BY CONSTRUCTION — it
        reports the latest gate the turn has reached, which can run ahead of
        the card inside a turn (turn 1: the card is on I while the mirror
        already says III) and behind it when the card waits on a later gate.
        What holds on every response: the mirror's gate is one the turn has
        reached, and at the end both name the handoff."""
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        for _ in range(13):
            rec.end_turn()
        result = _drive_overlay(rec.spec(), tmp_path)
        for i, row in enumerate(result["steps"]):
            mirror = rec.responses[i].get("tutorial_step")
            if not mirror:
                continue
            assert mirror["approximate"] is True
            assert mirror["turn_gate"] <= row["turn"], (mirror, row)
        last = rec.responses[-1]["tutorial_step"]
        assert last["id"] == "handoff" == result["steps"][-1]["id"]


# ═══════════════════════════════════════════════════════════════════════
# 2. The refused order releases its step at once
# ═══════════════════════════════════════════════════════════════════════

class TestTheRefusedOrderReleasesItsStep:

    def _block_munich(self, world):
        """Austria's Jellacic stands in Munich: the card's own first march
        (`Senarmont, move to Munich`) is refused — enemy forces present."""
        jellacic = world.get_marshal("Jellacic")
        assert jellacic is not None
        jellacic.location = "Munich"
        world.invalidate_active_nations_cache()

    def test_the_backend_refuses_the_cards_own_order(self, lesson):
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        rec.say("economy")
        self._block_munich(M.world)
        reply = rec.say("Senarmont, move to Munich")
        assert reply.get("success") is False, reply.get("message")
        assert "Munich" in reply["message"]
        assert M.world.get_marshal("Senarmont").location == "Franche-Comte"

    def test_the_card_moves_on_and_says_why(self, lesson, tmp_path):
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        rec.say("economy")                       # I → II
        self._block_munich(M.world)
        rec.say("Senarmont, move to Munich")     # refused → III at once
        result = _drive_overlay(rec.spec(), tmp_path)
        ids = _ids(result)
        assert ids == ["survey", "first_move", "first_end_turn"], ids
        last = result["steps"][-1]
        assert "The war refused that order" in last["body"], last["body"]
        assert "The school moves on" in last["body"]

    def test_a_refusal_of_some_other_order_does_not_release(self, lesson, tmp_path):
        """Only the card's OWN suggestion counts — a refused order of the
        player's own devising leaves the lesson where it stands."""
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        rec.say("economy")                       # I → II
        reply = rec.say("Ney, move to Rhineland")   # refused: he is already there
        assert reply.get("success") is False, reply.get("message")
        assert "already" in reply["message"].lower(), reply["message"]
        result = _drive_overlay(rec.spec(), tmp_path)
        assert _ids(result) == ["survey", "first_move", "first_move"], _ids(result)

    def test_the_route_reads_what_main_gd_noted_never_the_payload(self):
        src = OVERLAY.read_text(encoding="utf-8")
        assert "func note_sent(cmd: String)" in src
        assert "_norm_line(str(step[\"suggest\"])) != _last_sent" in src
        assert 'response.get("command"' not in src, "the endpoint ships no command echo"


# ═══════════════════════════════════════════════════════════════════════
# 3. The Skip chip and the Cabinet chip
# ═══════════════════════════════════════════════════════════════════════

class TestTheChips:

    def test_skip_releases_the_step_with_a_word(self, lesson, tmp_path):
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        rec.say("economy")   # index 1 → the card is on II when this is observed
        rec.say("status")    # index 2: the skip is pressed before it
        result = _drive_overlay(rec.spec(clicks={"2": ["skipstep:"]}), tmp_path)
        ids = _ids(result)
        assert ids[1] == "first_move"
        assert ids[2] == "first_end_turn", ids
        assert "You skipped the last page" in result["steps"][2]["body"]

    def test_the_cabinet_chip_asks_main_gd_for_the_wizard_on_austria(self, lesson, tmp_path):
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        rec.say("status")
        result = _drive_overlay(rec.spec(clicks={"1": ["open:cabinet:Austria"]}), tmp_path)
        assert result["cabinet_opened"] == ["Austria"], result["cabinet_opened"]

    def test_the_handoff_carries_no_skip_chip(self):
        src = OVERLAY.read_text(encoding="utf-8")
        i = src.index('if str(step["id"]) == "handoff":')
        block = src[i:i + 600]
        assert '"skipdone:"' in block and 'else:' in block and '"skipstep:"' in block


# ═══════════════════════════════════════════════════════════════════════
# 4. The Cabinet lesson completes on the mission the wizard confirms
# ═══════════════════════════════════════════════════════════════════════

class TestTheCabinetLesson:

    def _to_turn_three(self, rec):
        rec.settle(rec.say("economy"))
        rec.settle(rec.say("Senarmont, move to Munich"))
        rec.end_turn_until(2)
        rec.settle(rec.say("Ney, defend"))
        rec.settle(rec.say("Senarmont, bombard Jellacic"))
        rec.end_turn_until(3)
        assert rec.world.current_turn == 3

    def test_the_wizards_own_sentence_stages_the_confirm_and_the_confirm_goes_live(self, lesson):
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        self._to_turn_three(rec)
        staged = rec.say("gather intel on Austria")     # the wizard's _build_command line
        dialogue = staged.get("diplomatic_dialogue") or {}
        assert dialogue.get("type") == "mission", staged.get("message")
        assert str(staged.get("talleyrand_mission_summary")) == "None"
        live = rec.answer_dialogue("start_mission", dialogue)
        assert live.get("success") is True, live.get("message")
        assert M.world.active_diplomatic_mission is not None
        assert live.get("talleyrand_mission_summary") not in (None, "", "None"), live
        assert "Austria" in str(live.get("talleyrand_mission_summary"))

    def test_the_card_advances_on_the_confirm_response(self, lesson, tmp_path):
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        self._to_turn_three(rec)
        staged = rec.say("gather intel on Austria")
        rec.answer_dialogue("start_mission", staged.get("diplomatic_dialogue"))
        result = _drive_overlay(rec.spec(), tmp_path)
        ids = _ids(result)
        assert "cabinet" in ids, ids
        # the staging response (a question, not a refusal) leaves the card
        # on VII; the confirm completes it → VIII (waiting for turn 4)
        assert ids[-2] == "cabinet" and ids[-1] == "first_battle", ids
        # the door chip renders once the card's own gate (turn 3) is reached
        # — on turn 2 the card WAITS ("Berthier resumes with the morning
        # dispatch") and offers no chip, by the waiting rule
        on_gate = [row for row in result["steps"]
                   if row["id"] == "cabinet" and row["turn"] >= 3]
        assert on_gate, [(row["id"], row["turn"]) for row in result["steps"]]
        assert "open:cabinet:Austria" in on_gate[-1]["body"], on_gate[-1]["body"]
        assert "The war refused" not in result["steps"][-1]["body"]

    def test_the_mission_predicate_reads_the_backends_own_sentinel(self):
        src = OVERLAY.read_text(encoding="utf-8")
        assert 'text != "None"' in src
        body = src[src.index("func _pred_mission_started"):]
        body = body[:body.index("\n\n\n")]
        assert 'talleyrand_mission_summary' in body


# ═══════════════════════════════════════════════════════════════════════
# 5. The happy lesson, end to end — the driver's script is the card's own
# ═══════════════════════════════════════════════════════════════════════

def _overlay_steps():
    src = OVERLAY.read_text(encoding="utf-8")
    i = src.index("const STEPS")
    j = src.index("\n]", i)
    rows = []
    for block in src[i:j].split("\n\t{")[1:]:
        sid = re.search(r'"id":\s*"([a-z_]+)"', block).group(1)
        gate = int(re.search(r'"turn_gate":\s*(\d+)', block).group(1))
        title = re.search(r'"title":\s*"([^"]+)"', block).group(1)
        rows.append((sid, gate, title))
    return rows


class TestTheHappyLesson:

    def test_the_lesson_script_reaches_the_handoff_without_a_skip(self, lesson, tmp_path):
        """The committed driver script, played by hand through the same
        endpoints: every card either fires or is released by the floor, and
        the handoff is reached without a single skip."""
        client, M, boot = lesson
        rec = Recorder(client, M, boot)
        script = json.loads(LESSON.read_text(encoding="utf-8"))
        for loop in range(1, 13):
            for line in script["turns"].get(str(loop), []):
                rec.settle(rec.say(line))
            rec.end_turn_until(loop + 1)
        result = _drive_overlay(rec.spec(), tmp_path)
        ids = _ids(result)
        assert ids[-1] == "handoff", ids
        seen = []
        for sid in ids:
            if not seen or seen[-1] != sid:
                seen.append(sid)
        expected = [sid for sid, _g, _t in _overlay_steps()]
        # the catch-up floor may walk two cards inside ONE observe (only the
        # last is recorded), so the pin is ORDER, not one-to-one presence
        assert [sid for sid in expected if sid in seen] == seen, (seen, expected)
        for sid in ("cabinet", "marshalate", "naval", "first_battle", "handoff"):
            assert sid in seen, (sid, seen)
        bodies = "\n".join(row["body"] for row in result["steps"])
        assert "You skipped" not in bodies


# ═══════════════════════════════════════════════════════════════════════
# 6. The table, the mirror, the scripts and the client wiring
# ═══════════════════════════════════════════════════════════════════════

class TestTheTableAndItsMirrors:

    def test_eighteen_cards_in_gate_order_with_the_three_new_lessons(self):
        rows = _overlay_steps()
        ids = [r[0] for r in rows]
        assert len(rows) == 18
        assert ids.index("cabinet") == ids.index("bombardment") + 1
        assert ids.index("marshalate") == ids.index("first_battle") + 1
        assert ids.index("naval") == ids.index("free_stand") + 1
        gates = [r[1] for r in rows]
        assert gates == sorted(gates), gates
        assert dict((r[0], r[1]) for r in rows)["cabinet"] == 3
        assert dict((r[0], r[1]) for r in rows)["naval"] == 10

    def test_the_backend_mirror_matches(self):
        from backend.game_logic import tutorial_state as T
        assert T.STEPS == _overlay_steps()

    def test_the_new_cards_teach_what_the_user_asked_for(self):
        src = OVERLAY.read_text(encoding="utf-8")
        # diplomacy
        assert "GATHER INTELLIGENCE" in src and "diplomatic point" in src
        # pushback
        assert "PUSH BACK" in src and "DEFY" in src and "TRUST is the currency" in src
        # relationships / envy / reward
        assert "Ney and Soult are at odds" in src and "half their weight" in src
        assert "ENVIOUS" in src and "envy sleeps in this lesson" in src
        assert "EXPECTATION of reward" in src
        # naval — honest about the lesson having no fleet
        assert "There is no fleet in this lesson" in src
        assert "Royal Navy" in src and "THE ADMIRALTY" in src and "BLOCKADE" in src
        # first contact
        assert "what can I do" in src and "Tab" in src and "Esc" in src

    def test_the_overlay_keeps_its_hygiene(self):
        src = OVERLAY.read_text(encoding="utf-8")
        assert "get_tree().create_timer" not in src
        assert "send_command" not in src
        assert "signal open_cabinet(nation: String)" in src

    def test_main_gd_wires_the_door_and_notes_every_send(self):
        src = MAIN_GD.read_text(encoding="utf-8")
        assert "tutorial_overlay.open_cabinet.connect(_on_tutorial_open_cabinet)" in src
        handler = src[src.index("func _on_tutorial_open_cabinet"):]
        handler = handler[:handler.index("\nfunc ")]
        assert "diplomacy_wizard.open_for_nation(nation)" in handler
        assert "_is_modal_dialog_open()" in handler
        assert src.count("tutorial_overlay.note_sent(command)") == 3

    def test_the_driver_scripts_open_the_cabinet_on_turn_three_and_begin_the_mission(self):
        for path in (LESSON, LESSON_TRUST):
            script = json.loads(path.read_text(encoding="utf-8"))
            assert "gather intel on Austria" in script["turns"]["3"], path.name
            assert script["policy"]["missions"] == "begin", path.name

    def test_the_driver_knows_the_begin_dial(self):
        from tools import playtest_driver as driver
        assert "begin" in driver.MISSIONS_MODES and "decline" in driver.MISSIONS_MODES
        assert driver.missions_mode({"missions": "begin"}) == "begin"
        assert driver.missions_mode({}) == "off"

    def test_the_parse_harness_lists_the_driven_tool(self):
        src = (REPO / "tools" / "godot_parse_check.gd").read_text(encoding="utf-8")
        assert "tools/tutorial_overlay_harness.gd" in src
        assert HARNESS.is_file()
