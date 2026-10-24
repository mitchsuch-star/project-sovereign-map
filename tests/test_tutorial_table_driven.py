"""The Table lesson, driven (S14d part 2 — `docs/TABLE_LESSON_SPEC.md` §4.2,
§6; October 24, 2026).

The School of War's second lesson — the Peace of Pressburg: a mission, a
separate peace, a vassal, seven cards over three turns — pinned the way the
Danube is (`tests/test_tutorial_unbreakable_2026_09_23.py`): the backend half
runs in-process on the real `tutorial_table_1805.json` through
`/new_game {"scenario": "tutorial_table"}` and the SAME answer endpoints the
client uses (the chip's structured params, the chooser's Proceed, the terms
page's Send — never a typed diplomatic verb), and the recorded responses are
fed to the real `tutorial_overlay.tscn` through
`tools/tutorial_overlay_harness.gd`. The driven classes SKIP without a Godot
engine — and a skip is not a pass.

Pins (§6 part 2): the committed script `tools/playtest_scripts/
tutorial_table_lesson.json` sees all seven cards in order through the real
overlay and reaches the hand-off with zero skips; the refused door releases
its step with the Table's own note; the skip chip releases; the backend
mirror is never ahead of the turn; a Table armed after the Danube in the same
scene inherits no latch (S14D-X20); the three `alt` arms render on the
responses that select them.
"""

import importlib.util
import json
import pathlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

REPO = pathlib.Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
OVERLAY = SCRIPTS / "tutorial_overlay.gd"
TABLE_STEPS_GD = SCRIPTS / "tutorial_table_steps.gd"
MAIN_GD = SCRIPTS / "main.gd"
MENU_GD = SCRIPTS / "main_menu.gd"
HARNESS = REPO / "tools" / "tutorial_overlay_harness.gd"
SCRIPT = REPO / "tools" / "playtest_scripts" / "tutorial_table_lesson.json"

# The Danube's driven kit, reused by path (tests are not a package).
_spec = importlib.util.spec_from_file_location(
    "_unbreakable", REPO / "tests" / "test_tutorial_unbreakable_2026_09_23.py")
U = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(U)

TABLE_IDS = ["austerlitz", "table", "austria_alone", "pressburg", "bavaria", "first_stone", "handoff"]
TABLE_GATES = {"austerlitz": 1, "table": 1, "austria_alone": 1, "pressburg": 2, "bavaria": 2,
               "first_stone": 3, "handoff": 3}
TABLE_TITLE = "THE SCHOOL OF WAR — THE TABLE"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _script() -> dict:
    return json.loads(_read(SCRIPT))


@pytest.fixture
def table_lesson(monkeypatch, tmp_path):
    """A TestClient on the REAL Table scenario, booted through the same
    /new_game handshake the main menu's second School row uses, on the
    lesson's own RNG sequence (SRX-8)."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    with U._lesson_draws():
        with patch("backend.save_manager.SAVE_DIR", save_dir):
            import backend.main as M
            from backend.commands.parser import CommandParser

            M._reset_world_state()
            monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
            with TestClient(M.app) as client:
                boot = client.post("/new_game", json={"scenario": "tutorial_table"}).json()
                assert boot.get("success") is True, boot
                assert boot["game_state"]["scenario_name"] == "tutorial_table"
                yield client, M, boot
            M._reset_world_state()


class TableRecorder(U.Recorder):
    """The Danube's recorder plus the two answers the Table's screens take:
    a per-court chip (structured `action_params`, as main.gd sends a row
    affordance) and an option picked by its action or label (the 1-based
    index path)."""

    def __init__(self, client, module, boot):
        super().__init__(client, module, boot)
        self.clicks = {}

    def click(self, meta: str):
        """A card chip pressed before the NEXT response (the harness's clicks)."""
        self.clicks.setdefault(str(len(self.responses)), []).append(meta)

    def answer_chip(self, dialogue: dict, action: str, nation: str):
        chip = None
        for row in dialogue.get("per_court_acceptance") or []:
            if isinstance(row, dict) and row.get("nation") == nation:
                for a in row.get("dial_actions") or []:
                    if isinstance(a, dict) and a.get("action") == action:
                        chip = a
        assert chip is not None, (action, nation, [r.get("nation") for r in dialogue.get("per_court_acceptance") or []])
        body = {"choice": action, "action_params": dict(chip)}
        if dialogue.get("dialogue_id") is not None:
            body["dialogue_id"] = dialogue["dialogue_id"]
        reply = self.client.post("/respond_to_diplomatic_dialogue", json=body).json()
        self.responses.append(reply)
        return reply

    def answer_option(self, dialogue: dict, option: str):
        options = [o for o in (dialogue.get("options") or []) if isinstance(o, dict)]
        for i, o in enumerate(options, start=1):
            if o.get("action") == option or str(o.get("label") or "") == option:
                return self.answer_dialogue(i, dialogue)
        raise AssertionError(f"no option {option!r} on {dialogue.get('type')!r}: "
                             f"{[o.get('label') for o in options]}")

    LETTERS = ("incoming_proposal", "incoming_settlement_offer", "incoming_ultimatum",
               "counter_offer_response")

    def settle(self, reply=None):
        """The Danube's answers, then a standing letter DECLINED (the Table's
        board writes none on the lesson's road; the idle run meets Austria's
        own peace letter, which a hard stop would hold `end turn` on)."""
        reply = super().settle(reply)
        for _ in range(3):
            dialogue = self.world.pending_diplomatic_dialogue or {}
            if dialogue.get("type") not in self.LETTERS:
                return reply
            options = [o for o in (dialogue.get("options") or []) if isinstance(o, dict)]
            pick = next((i for i, o in enumerate(options, start=1)
                         if "reject" in str(o.get("action") or "").lower()
                         or "decline" in str(o.get("action") or "").lower()
                         or str(o.get("label") or "").lower().startswith(("reject", "decline", "refuse"))),
                        len(options))
            reply = self.answer_dialogue(pick, dialogue)
        return reply

    def spec(self, clicks=None):
        merged = {k: list(v) for k, v in self.clicks.items()}
        for k, v in (clicks or {}).items():
            merged.setdefault(k, []).extend(v)
        return super().spec(merged)


def _play(rec: TableRecorder, script: dict, *, through_turn: int = 3, doors: bool = True):
    """The committed script, played by hand through the client's endpoints:
    each line stands for a card's door (pressed on the card first), the
    `clicks` follow the dialogue chain the line opens, and every turn is
    ended until the next loop's gate."""
    plan = script.get("clicks", {})
    door_of = script.get("doors", {})
    for loop in range(1, through_turn + 1):
        pending = list(plan.get(str(loop), []))
        for line in script["turns"].get(str(loop), []):
            if doors and door_of.get(line):
                rec.click(door_of[line])
            reply = rec.settle(rec.say(line))
            dialogue = (reply or {}).get("diplomatic_dialogue") or {}
            while pending and dialogue.get("type") == pending[0]["on"]:
                step = pending.pop(0)
                if step.get("chip"):
                    reply = rec.answer_chip(dialogue, step["chip"], step["nation"])
                else:
                    reply = rec.answer_option(dialogue, step["option"])
                dialogue = (reply or {}).get("diplomatic_dialogue") or {}
        assert not pending, f"loop {loop}: the dialogue chain never reached {pending[0]['on']!r}"
        rec.end_turn_until(loop + 1)


def _ids(result):
    return [row["id"] for row in result["steps"]]


def _seen_order(ids):
    seen = []
    for sid in ids:
        if not seen or seen[-1] != sid:
            seen.append(sid)
    return seen


# ═══════════════════════════════════════════════════════════════════════
# 1. The happy lesson — the committed script, every card in order
# ═══════════════════════════════════════════════════════════════════════

class TestTheHappyTable:

    def test_the_script_sees_all_seven_cards_in_order_with_zero_skips(self, table_lesson, tmp_path):
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        _play(rec, _script())
        # the board's own verdicts, on the real road (TABLE_LESSON_SPEC §4.1)
        assert M.world.diplomatic_states.get("Austria|France") == "PEACE"
        assert M.world.diplomatic_states.get("Bavaria|France") == "VASSAL"
        assert M.world.diplomatic_states.get("France|Russia") == "WAR"
        result = U._drive_overlay(rec.spec(), tmp_path)
        rows = result["steps"]
        assert rows[0]["active"] is True and rows[0]["lesson"] == "tutorial_table"
        assert rows[0]["id"] == "austerlitz" and rows[0]["title"] == TABLE_TITLE
        seen = _seen_order(_ids(result))
        trace = [(r["i"], r["id"], r["turn"], r["table_state"]) for r in rows]
        print("TRACE", json.dumps(trace), "SENT", json.dumps(rec.sent))
        assert seen == TABLE_IDS, (seen, trace)
        assert rows[-1]["id"] == "handoff" and rows[-1]["badge"] == "7 of 7"
        assert rows[-1]["done"] is False          # the hand-off waits for Conclude
        for row in rows:
            assert row["turn"] <= TABLE_GATES[row["id"]] + 2, row
        bodies = "\n".join(row["body"] for row in rows)
        assert "You skipped" not in bodies
        assert "refused that act" not in bodies
        # the doors the cards offer asked main.gd for the real screens
        assert result["cabinet_opened"] == ["Bavaria", "Bavaria"], result["cabinet_opened"]
        assert result["settlement_opened"] == [["war_1", "Austria"]], result["settlement_opened"]
        # the hand-off carries the Conclude chip and no skip chip
        assert "skipdone:" in rows[-1]["body"] and "skipstep:" not in rows[-1]["body"]
        for row in rows[:-1]:
            if row["id"] != "handoff":
                assert "skipstep:" in row["body"], row["id"]

    def test_the_table_the_door_opens_carries_austrias_chip(self, table_lesson):
        """Card III names the row's chip — the engine's own rule puts it there
        (the row at or above the threshold); the lesson pre-sets nothing."""
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        rec.settle(rec.say("reassure Bavaria"))
        reply = rec.say("propose common peace with Austria")
        dialogue = reply.get("diplomatic_dialogue") or {}
        assert dialogue.get("type") == "settlement_confirm", reply.get("message")
        rows = {r.get("nation"): r for r in dialogue.get("per_court_acceptance") or [] if isinstance(r, dict)}
        assert int(rows["Austria"]["total"]) >= int(rows["Austria"]["threshold"])
        assert int(rows["Russia"]["total"]) < int(rows["Russia"]["threshold"])
        chips = [a for a in rows["Austria"].get("dial_actions") or []
                 if isinstance(a, dict) and a.get("action") == "seek_bilateral_peace"]
        assert chips and chips[0]["label"].startswith("Separate peace with Austria"), chips
        assert chips[0]["bilateral_estimate"]["outcome"] == "ACCEPT", chips[0]["bilateral_estimate"]


# ═══════════════════════════════════════════════════════════════════════
# 2. Unbreakable — the refused door, the skip, the catch-up floor
# ═══════════════════════════════════════════════════════════════════════

class TestTheRefusedDoor:

    def test_the_table_refused_releases_card_two_with_the_tables_own_note(self, table_lesson, tmp_path):
        """Card II's door sends `propose common peace with Austria`; if the
        board refuses it, the card moves on and says why in the Table's own
        voice (S14D-X19) — never the Danube's "The war refused that order"."""
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        rec.settle(rec.say("reassure Bavaria"))         # card I fires
        # the board turns: Austria is no longer at war with France
        M.world.diplomatic_states["Austria|France"] = "PEACE"
        reply = rec.say("propose common peace with Austria")
        assert reply.get("success") is False, reply.get("message")
        assert "Austria" in str(reply.get("message"))
        result = U._drive_overlay(rec.spec(), tmp_path)
        ids = _ids(result)
        # the mission confirm, Begin mission (card I fires), the refused door
        assert ids == ["austerlitz", "austerlitz", "table", "austria_alone"], ids
        last = result["steps"][-1]
        assert "The table refused that act" in last["body"], last["body"]
        assert "The school moves on" in last["body"]
        assert "The war refused that order" not in last["body"]

    def test_the_door_card_names_the_line_its_door_sends(self):
        src = _read(TABLE_STEPS_GD)
        assert '"refusal_of": "propose common peace with Austria"' in src
        overlay = _read(OVERLAY)
        assert 'step.get("refusal_of", step.get("suggest", ""))' in overlay
        # the Danube's own route text, byte for byte (its pin reads it)
        assert '_norm_line(str(step["suggest"])) != _last_sent' in overlay


class TestTheSkipAndTheFloor:

    def test_skip_releases_the_step_with_a_word(self, table_lesson, tmp_path):
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        rec.settle(rec.say("economy"))
        result = U._drive_overlay(rec.spec(clicks={"1": ["skipstep:"]}), tmp_path)
        ids = _ids(result)
        assert ids == ["austerlitz", "table"], ids
        assert "You skipped the last page" in result["steps"][1]["body"]

    def test_the_idle_emperor_still_reaches_the_hand_off(self, table_lesson, tmp_path):
        """Four `end turn`s and nothing else: the gate+2 floor walks every
        card and the hand-off is reached (the catch-up may walk two cards in
        one observe, so the pin is the end, not every page)."""
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        rec.end_turn_until(5, limit=12)       # the floor reaches VII at turn 5 (gate 3 + 2)
        assert M.world.current_turn >= 5
        result = U._drive_overlay(rec.spec(), tmp_path)
        assert result["steps"][-1]["id"] == "handoff", _ids(result)
        for row in result["steps"]:
            assert row["turn"] <= TABLE_GATES[row["id"]] + 2, row


# ═══════════════════════════════════════════════════════════════════════
# 3. The mirror, the re-arm, the alt arms
# ═══════════════════════════════════════════════════════════════════════

class TestTheMirrorAndTheRearm:

    def test_the_backend_mirror_never_names_a_gate_the_turn_has_not_reached(self, table_lesson, tmp_path):
        from backend.game_logic import tutorial_state as T
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        _play(rec, _script(), doors=False)
        result = U._drive_overlay(rec.spec(), tmp_path)

        class W:
            scenario_name = "tutorial_table"
            current_turn = 1
        for row in result["steps"]:
            W.current_turn = row["turn"]
            mirror = T.tutorial_step_for(W())
            assert mirror["approximate"] is True
            assert mirror["turn_gate"] <= row["turn"], (mirror, row)
        W.current_turn = 40
        assert T.tutorial_step_for(W())["id"] == "handoff" == result["steps"][-1]["id"]

    def test_a_table_armed_after_the_danube_inherits_no_latch(self, table_lesson, tmp_path):
        """S14D-X20: the Danube sets a latch (an objection), then the Table
        boots in the same scene — the card re-arms on the Table with every
        latch clear, its own title, its own seven pages."""
        client, M, boot = table_lesson
        danube = client.post("/new_game", json={"scenario": "tutorial"}).json()
        assert danube["game_state"]["scenario_name"] == "tutorial"
        rec = TableRecorder(client, M, danube)
        objection = rec.say("Ney, defend")          # the Danube's objection latch
        assert objection.get("pending_objection") or objection.get("state") == "awaiting_player_choice", objection.get("message")
        rec.answer_objection("trust")
        table = client.post("/new_game", json={"scenario": "tutorial_table"}).json()
        assert table["game_state"]["scenario_name"] == "tutorial_table"
        rec.responses.append(table)
        swap_index = str(len(rec.responses) - 1)
        spec = rec.spec()
        spec["swaps"] = {swap_index: True}
        result = U._drive_overlay(spec, tmp_path)
        rows = result["steps"]
        assert rows[0]["lesson"] == "tutorial" and rows[0]["title"] == "THE SCHOOL OF WAR"
        assert any(row["saw_objection"] for row in rows[1:-1]), "the Danube never latched"
        armed = rows[-1]
        assert armed["lesson"] == "tutorial_table" and armed["title"] == TABLE_TITLE
        assert armed["id"] == "austerlitz" and armed["badge"] == "1 of 7"
        assert armed["saw_objection"] is False
        assert armed["kienmayer_state"] == "" and armed["table_state"] == ""


class TestTheAltArms:
    """The three branch arms (`_note_table`), selected by the response fields
    the client renders — fed as synthetic responses after the real road."""

    @staticmethod
    def _synthetic(turn: int, **fields):
        body = {"success": True, "game_state": {"turn": turn, "scenario_name": "tutorial_table"}}
        body.update(fields)
        return body

    def test_austrias_refusal_turns_card_four(self, table_lesson, tmp_path):
        """No peace sent: the floor carries the card to IV on turn 3 with the
        war unsettled; Austria's refusal then turns the page."""
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        rec.settle(rec.say("reassure Bavaria"))
        rec.end_turn_until(3, limit=6)
        rec.responses.append(self._synthetic(
            3, proposal_result={"target_nation": "Austria", "proposal_type": "Peace Treaty", "outcome": "REJECT"},
            events=[{"type": "diplomatic_proposal_returned", "target": "Austria", "outcome": "REJECT",
                     "message": "Talleyrand returns from Austria with grim news: they have rejected our proposal."}]))
        result = U._drive_overlay(rec.spec(), tmp_path)
        last = result["steps"][-1]
        assert last["id"] == "pressburg" and last["table_state"] == "austria_refused", last
        assert "Austria has NOT signed" in last["body"], last["body"]

    def test_a_standing_letter_turns_card_five(self, table_lesson, tmp_path):
        """The peace signed on the real morning puts card V up; a letter on
        the rail then turns it — on THAT response, not the next turn."""
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        _play(rec, _script(), through_turn=1, doors=False)     # cards I–IV done, turn 2
        rec.responses.append(self._synthetic(
            2, diplomatic_dialogue={"type": "incoming_proposal", "target_nation": "Prussia"}))
        result = U._drive_overlay(rec.spec(), tmp_path)
        last = result["steps"][-1]
        assert last["id"] == "bavaria" and last["table_state"] == "letter_waiting", last
        assert "answer the envoy first" in last["body"], last["body"]

    def test_bavarias_counter_turns_card_six(self, table_lesson, tmp_path):
        """No vassalage sent: the floor carries the card to VI on turn 4 with
        Bavaria still an ally; her counter then turns the page."""
        client, M, boot = table_lesson
        rec = TableRecorder(client, M, boot)
        _play(rec, _script(), through_turn=1, doors=False)     # the peace, turn 2
        rec.end_turn_until(4, limit=6)
        rec.responses.append(self._synthetic(
            4, diplomatic_dialogue={"type": "counter_offer_response", "target_nation": "Bavaria"}))
        result = U._drive_overlay(rec.spec(), tmp_path)
        last = result["steps"][-1]
        assert last["id"] == "first_stone" and last["table_state"] == "bavaria_countered", last
        assert "Bavaria has COUNTERED" in last["body"], last["body"]


# ═══════════════════════════════════════════════════════════════════════
# 4. The wiring (source — runs everywhere)
# ═══════════════════════════════════════════════════════════════════════

class TestTheWiring:

    def test_the_overlay_routes_the_settlement_door_to_main_gd(self):
        overlay = _read(OVERLAY)
        assert "signal open_settlement(war_id: String, nation: String)" in overlay
        meta = U._overlay_steps  # the Danube module's census is importable (smoke)
        assert callable(meta)
        assert 'meta_str.begins_with("open:settlement:")' in overlay
        assert "open_settlement.emit(str(parts[0]), str(parts[1]))" in overlay
        main = _read(MAIN_GD)
        assert "tutorial_overlay.open_settlement.connect(_on_tutorial_open_settlement)" in main
        body = main[main.index("func _on_tutorial_open_settlement("):]
        body = body[:body.index("\nfunc ", 10)]
        assert "_on_war_settlement_clicked(war_id, nation)" in body
        assert 'tutorial_overlay.note_sent("propose common peace with " + nation)' in body
        assert "_is_modal_dialog_open()" in body
        assert '"tutorial_table":\n\t\t\t_on_tutorial_boot_requested("tutorial_table")' in main

    def test_the_menu_offers_the_second_lesson_on_the_same_road(self):
        menu = _read(MENU_GD)
        assert '_add_menu_button("tutorial_table", "The School of War — The Table (a guided peace)", _on_tutorial_table_pressed, false)' in menu
        assert '"begin", "return", "tutorial", "tutorial_table":' in menu
        pressed = menu[menu.index("func _on_tutorial_table_pressed("):]
        pressed = pressed[:pressed.index("\nfunc ", 10)]
        assert '_confirm_action = "tutorial_table"' in pressed and '_launch("tutorial_table")' in pressed

    def test_the_registry_binds_the_table_to_its_own_steps_and_notes(self):
        overlay = _read(OVERLAY)
        assert 'const TableLesson := preload("res://scripts/tutorial_table_steps.gd")' in overlay
        entry = overlay[overlay.index('\t"tutorial_table": {'):]
        entry = entry[:entry.index("\n\t},")]
        assert '"steps": TableLesson.STEPS,' in entry
        assert f'"title": "{TABLE_TITLE}",' in entry
        assert '"done": "tutorial_table",' in entry
        assert '"refused": "The table refused that act — %s The school moves on."' in entry
        steps = _read(TABLE_STEPS_GD)
        assert steps.count('"id": "') == 7
        for sid in TABLE_IDS:
            assert f'"id": "{sid}"' in steps, sid
        # every step a door or a button — no typed suggestion anywhere
        assert '"suggest": ""' in steps and steps.count('"suggest": "') == steps.count('"suggest": ""')

    def test_the_harness_records_the_new_signal_and_the_swap(self):
        harness = _read(HARNESS)
        assert '"settlement_opened"' in harness
        assert "_overlay.open_settlement.connect(" in harness
        assert 'var swaps: Dictionary = _spec.get("swaps", {})' in harness
        assert "if i == 0 or swaps.has(key):" in harness
        for key in ('"lesson"', '"table_state"', '"kienmayer_state"', '"saw_objection"'):
            assert key in harness, key
