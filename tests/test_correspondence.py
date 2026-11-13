"""RE-C — "Affairs of State": the Correspondence, the home of the letters
(`docs/RECURRING_EVENTS_SPEC.md` §12b.1, §16b, §22.3; the landing record §23).

The builder `moments.correspondence(world)` on crafted rows and on letters the
production engine delivered: ON THE DESK (every `fired` row — Not Now is the
client's), ANSWERED newest first (the caption derived from the authored side,
the receipt, the echo dated the next morning, a squadron at sea and then its
fate, the chips from the consequence to its remedy), IN THE OFFING (the Watch
read pure), LEFT UNANSWERED / SET ASIDE (lapsed with its price, withdrawn,
crowded out — the silent passes never show), the closing record the morning
after the file closes; the page rides `GET /dispatch` with its first-open
line and is absent on an unarmed world; a read writes nothing; every figure
an int. Then the client's page by source: the slips' ink, the ceiling
cleared on close, the roads main connects, the first-open draw site.

Every pin arms the real booted world with the staged fixture
`tests/fixtures/affairs_block.json`, as `tests/test_affairs_engine.py` does.
"""
import json
import re
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import first_open as FO
from backend.game_logic import moments as MO
from backend.game_logic import naval
from tests.test_affairs_engine import (  # noqa: F401 — the fixtures ride the import
    FIXTURE, _at, _letter, _make_current, _no_moments, _quiet, _restore_active_world, _run,
    _tick, armed, client, world,
)
from tests.test_affairs_haiti import _haiti_board
from tests.test_first_open import _TYPED, _func, _gd

H1 = "santo_domingo"
T1, T2, T3 = "chancellors_letters", "the_host", "berthiers_memorial"
REPO = Path(__file__).resolve().parents[1]
SCENES = REPO / "godot-client" / "project-sovereign" / "scenes"
TEXT_KEYS = ("title", "writer", "office", "dateline", "answer_by_label", "answered_label", "echo_label",
             "receipt", "echo", "caption", "line", "label", "button", "words", "expected_label")


def _page(w):
    w.__dict__.pop("_affairs_memo", None)
    return MO.correspondence(w)


def _sail(armed, client):
    """The Haiti letter at T7 in its squadron form (the boot's blockade), the
    Accept through the endpoint — five of the line at sea until T11."""
    _haiti_board(armed)
    assert _run(armed, range(1, 8)) == {7: [f"{H1}#1"]}
    letter = _letter(armed, f"{H1}#1")
    _make_current(armed, letter)
    with _quiet():
        result = client.post("/respond_to_diplomatic_dialogue",
                             json={"choice": "accept_ai_proposal", "dialogue_id": letter["dialogue_id"]}).json()
    assert result["success"] is True, result
    return MO.status_row(armed, f"{H1}#1")


def _settle(armed, turn=11):
    for t in range(8, turn + 1):
        _at(armed, t)
        naval._squadron_tick(armed)
    AF.settle_squadrons(armed)


def _walk(value, path=""):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk(v, f"{path}[{i}]")
    else:
        yield path, value


def _ids(page):
    out = []
    for key in ("standing", "answered", "set_aside"):
        out += [r["id"] for r in page[key]]
    return out


# ═══════════════════════════════════════════════════════════════════════════
# ON THE DESK
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDesk:
    def test_a_standing_letter_is_on_the_desk_with_its_road(self, armed, client):
        """The Haiti letter standing at T7 in its squadron form: the rubric's
        answer-by date, the writer and the office, the monogram, both answers
        as the buttons say them, and the mailbox id the rail card's road
        takes ("Read the letter ▸")."""
        _haiti_board(armed)
        assert _run(armed, range(1, 8)) == {7: [f"{H1}#1"]}
        page = _page(armed)
        assert page["counts"] == {"standing": 1, "answered": 0, "set_aside": 0}
        assert page["button"] == "The Correspondence (1 standing)" and page["at_sea"] is False
        [slip] = page["standing"]
        assert slip["id"] == f"{H1}#1" and slip["register"] == "affair"
        assert slip["title"] == "The Squadron for Santo Domingo"
        assert (slip["writer"], slip["office"]) == ("Decrès", "Minister of Marine and the Colonies")
        assert slip["device"] == {"kind": "monogram", "nation": "", "letter": "D"}
        assert slip["turn"] == 7 and slip["dateline"] == MO._dateline(armed, 7)
        assert slip["answer_by"] == 8 and slip["answer_by_label"] == MO._dateline(armed, 8)
        assert slip["answers"] == [
            {"caption": "Send five of the line", "receipt": "−500 gold · 1 action · 36 in 100 home"},
            {"caption": "Ferrand must hold alone", "receipt": "authority 100 → 97"}]
        letter = _letter(armed, f"{H1}#1")
        assert slip["mailbox_id"] == int(letter["mailbox_id"]) > 0
        assert MO.mailbox_id_of(armed, f"{H1}#1") == slip["mailbox_id"]
        assert MO.mailbox_id_of(armed, "nobody#9") == 0

    def test_the_mailbox_row_names_the_form(self, armed, client):
        """REC-1 (REH-2's sibling, found by RE-C's sweep): the letter-book's
        row read the entry's title ("The Relief of Santo Domingo") under a
        letter that read "The Squadron for Santo Domingo" — `build_letter`'s
        `proposal_terms_summary` is now the frozen form's title."""
        _haiti_board(armed)
        _run(armed, range(1, 8))
        letter = _letter(armed, f"{H1}#1")
        assert letter["proposal_terms_summary"] == "The Squadron for Santo Domingo"
        _make_current(armed, letter)
        rows = client.get("/mailbox").json()["items"]
        [row] = [r for r in rows if r.get("proposal_type") == "moment_letter"]
        assert row["summary_text"] == "An Affair of State: The Squadron for Santo Domingo"
        assert row["mailbox_id"] == MO.mailbox_id_of(armed, f"{H1}#1")

    def test_not_now_is_the_client_s_and_the_letter_still_stands(self, armed):
        """Reading 1: a set-aside letter writes nothing on the server — the
        row stays `fired`, its dialogue stays in the manager, the desk keeps it."""
        _haiti_board(armed)
        _run(armed, range(1, 8))
        assert MO.status(armed, f"{H1}#1") == "fired"
        assert [r["id"] for r in _page(armed)["standing"]] == [f"{H1}#1"]
        assert _page(armed)["answered"] == [] and _page(armed)["set_aside"] == []


# ═══════════════════════════════════════════════════════════════════════════
# ANSWERED — the caption, the receipt, the echo, the sea and the fate
# ═══════════════════════════════════════════════════════════════════════════

class TestAnswered:
    def test_an_accepted_squadron_shows_at_sea_then_its_fate(self, armed, client):
        row = _sail(armed, client)
        page = _page(armed)
        assert page["counts"]["standing"] == 0 and page["at_sea"] is True
        assert page["button"] == "The Correspondence (a squadron at sea)"
        [slip] = page["answered"]
        assert slip["id"] == f"{H1}#1" and slip["title"] == "The Squadron for Santo Domingo"
        assert slip["answer"] == "accept" and slip["caption"] == "Send five of the line"
        assert slip["answered_turn"] == 7 and slip["answered_label"] == MO._dateline(armed, 7)
        assert slip["receipt"] == "−500 gold · 1 action · 36 in 100 home"
        assert slip["echo"] == row["echo"] == "Decrès: the squadron slips out of Brest on the night tide."
        assert slip["echo_label"] == MO._dateline(armed, 8)
        assert slip["at_sea"] == {"words": "five of the line", "expected": 11,
                                  "expected_label": MO._dateline(armed, 11),
                                  "line": f"At sea — five of the line; word expected about {MO._dateline(armed, 11)}."}
        assert slip["fate"] == {} and slip["chips"] == [{"kind": "admiralty", "nation": ""}]
        _settle(armed)
        row = MO.status_row(armed, f"{H1}#1")
        assert row["outcome"] in AF.OUTCOMES and row["outcome_turn"] == 11
        page = _page(armed)
        [slip] = page["answered"]
        assert page["at_sea"] is False and page["button"] == "The Correspondence"
        assert slip["at_sea"] == {}
        assert slip["fate"] == {"outcome": row["outcome"], "turn": 11, "label": MO._dateline(armed, 11),
                                "line": row["outcome_line"]}
        assert slip["fate"]["line"]

    def test_an_answered_moment_shows_its_caption_only(self, armed):
        """A dated moment's row carries no receipt or echo (a pre-RE save's
        rows the same): the apostille's caption is derived from the authored
        side; the court chip comes from the moment's own court."""
        armed.moments["state"]["bavarian_match"] = {"status": "answered", "turn": 8, "answer": "accept",
                                                    "answered_turn": 8}
        page = _page(armed)
        [slip] = page["answered"]
        assert slip["id"] == "bavarian_match" and slip["register"] == "moment"
        assert slip["title"] == "The Bavarian Match" and slip["caption"] == "Seal the match"
        assert slip["receipt"] == "" and slip["echo"] == "" and slip["echo_label"] == ""
        assert slip["at_sea"] == {} and slip["fate"] == {}
        assert slip["chips"] == [{"kind": "court", "nation": "Bavaria"}]
        assert slip["device"]["kind"] == "sheet" and slip["device"]["nation"] == "France"

    def test_newest_first_and_the_host_s_slip(self, armed):
        armed.moments["state"]["bavarian_match"] = {"status": "answered", "turn": 8, "answer": "accept",
                                                    "answered_turn": 8}
        armed.moments["state"][f"{T2}#1"] = {
            "id": f"{T2}#1", "status": "answered", "turn": 12, "answer": "accept", "answered_turn": 12,
            "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1, "receipt": "−300 gold",
            "echo": "Montgelas: the account between Bavaria and Paris is square for the season."}
        page = _page(armed)
        assert [r["id"] for r in page["answered"]] == [f"{T2}#1", "bavarian_match"]
        host = page["answered"][0]
        assert host["title"] == "The Host's Claims" and host["caption"] == "Pay the host's claims"
        assert host["device"] == {"kind": "arms", "nation": "Bavaria", "letter": ""}
        assert host["chips"] == [{"kind": "court", "nation": "Bavaria"}]
        assert host["receipt"] == "−300 gold" and host["echo_label"] == MO._dateline(armed, 13)
        assert host["office"].startswith("for the court of") or host["office"] == ""

    def test_the_law_s_door_is_the_laws_chip(self, armed):
        armed.moments["state"][f"{T3}#1"] = {
            "id": f"{T3}#1", "status": "answered", "turn": 9, "answer": "decline", "answered_turn": 9,
            "lord": "France", "bind": {"law": "grand_quartier_general"}, "tier": 1, "receipt": "no change",
            "echo": ""}
        [slip] = _page(armed)["answered"]
        # Session UI-5: the memorial's refusal is "Let the tent serve" (its "Not now"
        # doubled the letter's own Not Now button — tests/test_affairs_engine.py).
        assert slip["caption"] == "Let the tent serve" and slip["chips"] == [{"kind": "laws", "nation": ""}]
        assert slip["device"] == {"kind": "monogram", "nation": "", "letter": "B"}


# ═══════════════════════════════════════════════════════════════════════════
# LEFT UNANSWERED / SET ASIDE — and the silent passes that never show
# ═══════════════════════════════════════════════════════════════════════════

class TestSetAside:
    def _craft(self, armed):
        state = armed.moments["state"]
        state[f"{T1}#1"] = {"id": f"{T1}#1", "status": "lapsed", "turn": 7, "answer": "decline", "lapsed_turn": 8,
                            "lord": "France", "bind": {"region": "Swabia"}, "tier": 1,
                            "receipt": "authority 100 → 95", "echo": "Cambacérès: the Council has acted."}
        state[f"{T2}#2"] = {"id": f"{T2}#2", "status": "withdrawn", "turn": 13, "withdrawn_turn": 13,
                            "set_aside_for": "bavarian_match", "lord": "France", "bind": {"host": "Bavaria"},
                            "tier": 1, "receipt": "The Host's Claims was set aside for The Bavarian Match"}
        state[f"{T3}#1"] = {"id": f"{T3}#1", "status": "passed", "reason": "crowded", "turn": 15,
                            "lord": "France", "bind": {"law": "grand_quartier_general"}, "tier": 1}
        state["throne_of_holland"] = {"status": "passed", "turn": 20, "reason": "premise"}
        state["crown_of_the_reich"] = {"status": "passed", "turn": 21, "reason": "forsworn"}
        state["decree_of_berlin"] = {"status": "passed", "turn": 22, "reason": "verdict"}
        state["bavarian_match"] = {"status": "passed", "turn": 5, "reason": "before_save"}

    def test_three_kinds_newest_first_and_the_silent_passes_hidden(self, armed):
        self._craft(armed)
        page = _page(armed)
        assert page["counts"] == {"standing": 0, "answered": 0, "set_aside": 3}
        rows = page["set_aside"]
        assert [(r["id"], r["kind"], r["when"]) for r in rows] == [
            (f"{T3}#1", "crowded", 15), (f"{T2}#2", "withdrawn", 13), (f"{T1}#1", "lapsed", 8)]
        assert rows[0]["line"] == "Set aside on a busy desk — its second answer taken"
        assert rows[1]["line"] == "Set aside for The Bavarian Match — nothing was spent"
        assert rows[2]["line"] == "Filed unanswered — Let the Council act · authority 100 → 95"
        assert [r["label"] for r in rows] == [MO._dateline(armed, t) for t in (15, 13, 8)]
        assert rows[2]["title"] == "The Arch-Chancellor's Letters"
        shown = _ids(page)
        for silent in ("throne_of_holland", "crown_of_the_reich", "decree_of_berlin", "bavarian_match"):
            assert silent not in shown


# ═══════════════════════════════════════════════════════════════════════════
# IN THE OFFING — the Watch read pure; THE FILE CLOSED
# ═══════════════════════════════════════════════════════════════════════════

class TestTheOffingAndTheClosing:
    def test_the_offing_is_the_watch_and_the_read_writes_nothing(self, armed):
        _haiti_board(armed)
        _run(armed, range(1, 4))                   # three blockaded mornings: the Watch counts them
        armed.__dict__.pop("_affairs_memo", None)
        lines = AF.watch(armed, record=False)
        assert lines and all("Decrès may write" in line or "may" in line for line in lines)
        watched_before = dict(AF.runtime(armed).get("watched") or {})
        before = json.dumps(armed.to_dict(), sort_keys=True)
        page = _page(armed)
        assert page["offing"] == lines
        assert json.dumps(armed.to_dict(), sort_keys=True) == before
        assert dict(AF.runtime(armed).get("watched") or {}) == watched_before
        # the morning builder's Watch (record=True) remembers what it showed
        armed.__dict__.pop("_affairs_memo", None)
        AF.watch(armed)
        assert AF.runtime(armed)["watched"].get(H1) == MO._turn(armed)

    def test_the_closing_record_appears_the_morning_after_the_file_closes(self, armed):
        e = MO.entry(armed, H1)
        assert e["ends"]["turn"] == 76 and len(e["closing"]) == 2
        _at(armed, 76)
        assert _page(armed)["closing"] == []
        _at(armed, 77)
        assert _page(armed)["closing"] == [{"id": H1, "title": "The Relief of Santo Domingo", "turn": 76,
                                            "label": MO._dateline(armed, 76), "lines": list(e["closing"])}]

    def test_the_empty_states_are_the_ruled_lines(self, armed):
        page = _page(armed)
        assert page["empty"] == {"desk": "No letter of state lies on the desk, Sire.",
                                 "answered": "Nothing has yet been answered.",
                                 "offing": "Nothing is gathering, Sire."}
        assert page["title"] == "The Correspondence" and page["turn"] == MO._turn(armed)


# ═══════════════════════════════════════════════════════════════════════════
# The GET, the first-open line, the figures
# ═══════════════════════════════════════════════════════════════════════════

class TestTheEndpoint:
    def test_get_dispatch_carries_the_page_with_its_first_open_line(self, armed, client):
        _sail(armed, client)
        response = client.get("/dispatch").json()
        assert response["success"] is True and "dispatch" in response
        page = response["correspondence"]
        assert page["button"] == "The Correspondence (a squadron at sea)"
        fo = page["first_open"]
        assert fo["screen"] == "correspondence" and len(fo["line"]) <= FO.LINE_CAP
        assert "Sire" in fo["line"] and not _TYPED.search(fo["line"]) and "_" not in fo["line"]
        assert fo["line"] == FO.line_for(armed, "correspondence")
        assert "correspondence" in FO.SCREENS
        for path, value in _walk(page):
            assert not isinstance(value, float), (path, value)
            if any(path.endswith("." + key) for key in TEXT_KEYS) and isinstance(value, str):
                assert "_" not in value, (path, value)

    def test_an_unarmed_world_carries_no_page(self, world, client):
        world.moments = {}
        assert MO.correspondence(world) == {}
        response = client.get("/dispatch").json()
        assert response["success"] is True and "correspondence" not in response

    def test_the_page_survives_a_save_round_trip_unchanged(self, armed, client):
        _sail(armed, client)
        before = _page(armed)
        from backend.models.world_state import WorldState
        with _quiet():
            twin = WorldState.from_dict(json.loads(json.dumps(armed.to_dict())))
        twin.__dict__.pop("_affairs_memo", None)
        after = MO.correspondence(twin)
        # the mailbox id lives in the dialogue manager; the rest is the state rows' and the deck's
        for key in ("answered", "set_aside", "closing", "offing", "button", "counts", "at_sea", "empty"):
            assert after[key] == before[key], key


# ═══════════════════════════════════════════════════════════════════════════
# The client's page — by source (the frames are the IQ-10 pipeline's)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheClient:
    def test_the_slips_write_ink_and_the_chips_are_the_theme_s_plaques(self):
        src = _gd("dispatch_view.gd")
        body = _func(src, "_corr_body_bbcode")
        colours = re.findall(r'\[color=#" \+ Utils\.(\w+)', body)
        assert colours and all(name.startswith("INK_") for name in colours), colours
        chips = re.findall(r"Utils\.bb_button_chip\(([^\n]*)\)", body)
        assert chips and all("Utils.COLOR_GOLD, CORR_CHIP_BG" in chip for chip in chips), chips
        assert '"corr:read:" + str(mailbox_id)' in body and '"corr:court:" + nation' in body
        assert '"ledger:6"' in body and '"ledger:7"' in body
        assert "[font_size" not in src.split("RE-C — the Correspondence page", 1)[1]

    def test_the_ceiling_is_the_letter_s_and_clears_on_close(self):
        src = _gd("dispatch_view.gd")
        assert 'set_meta("clamp_ceiling_override"' in _func(src, "_raise_page_ceiling")
        reset = _func(src, "_reset_correspondence_page")
        assert 'remove_meta("clamp_ceiling_override")' in reset and "title_label.text = DISPATCH_TITLE" in reset
        assert "_reset_correspondence_page()" in _func(src, "close_view")
        assert "func refit() -> void:" in src
        for const in ("CORR_HEIGHT_FRACTION := 0.8", "CORR_WIDTH_FRACTION := 0.45", "CORR_MIN_WIDTH := 680.0",
                      "CORR_MIN_HEIGHT := 440.0", "CORR_MAX_WIDTH := 860.0"):
            assert const in src, const

    def test_the_page_respects_the_pinned_refresh_and_the_first_open_road(self):
        src = _gd("dispatch_view.gd")
        pinned = _func(src, "_on_pinned_dispatch")
        assert "Utils.restore_scroll(scroll_container, held_scroll)" in pinned
        assert "Utils.restore_scroll(corr_scroll, _corr_scroll_hold)" in pinned
        assert "_take_correspondence(response)" in _func(src, "_on_dispatch_received")
        render = _func(src, "_render_correspondence")
        assert 'data.get("first_open")' in render and "note_first_open(CORR_SCREEN)" in render
        assert render.index('data.get("first_open")') < render.index('"ON THE DESK (%d)"')

    def test_the_roads_main_connects_and_the_pointers_in(self):
        main = _gd("main.gd")
        assert "dispatch_view.read_letter_requested.connect(_on_correspondence_read_letter)" in main
        assert "dispatch_view.open_diplomacy_for.connect(_on_ledger_open_diplomacy_for)" in main
        assert "mailbox_panel.correspondence_requested.connect(_on_mailbox_correspondence_requested)" in main
        assert main.count("_no_envoys_line()") >= 2
        line = _func(main, "_no_envoys_line")
        assert "and the Correspondence (the Dispatch) keeps every letter answered." in line
        assert "dispatch_view.has_correspondence()" in line
        reader = _func(main, "_on_correspondence_read_letter")
        assert "api_client.activate_mailbox_item(mailbox_id, _on_mailbox_activate_result)" in reader
        mailbox = _gd("mailbox_panel.gd")
        assert "signal correspondence_requested" in mailbox and '"The Correspondence ▸"' in mailbox
        view = _gd("dispatch_view.gd")
        meta = _func(view, "_on_corr_meta")
        assert meta.index("close_view()") < meta.index("read_letter_requested.emit(mailbox_id)")
        assert "open_diplomacy_for.emit(nation)" in meta

    def test_the_scene_authors_the_page_s_nodes(self):
        scene = (SCENES / "dispatch_view.tscn").read_text(encoding="utf-8")
        assert '[node name="CorrespondenceScroll" type="ScrollContainer"' in scene
        assert scene.index("CorrespondenceScroll") < scene.index("custom_minimum_size = Vector2(0, 160)")
        assert '[node name="CorrespondenceBox" type="VBoxContainer" parent="PanelContainer/VBoxContainer/CorrespondenceScroll"]' in scene
        assert 'text = "The Correspondence"' in scene and 'text = "◂ The Dispatch"' in scene


# ═══════════════════════════════════════════════════════════════════════════
# The frames (IQ-10) and the readability record
# ═══════════════════════════════════════════════════════════════════════════

FRAME_DATE = "2026_11_01"
STEMS = ("DESK", "ANSWERED", "FATE")
SURFACES = ("correspondence_desk", "correspondence_answered", "correspondence_fate")
AUDITS = REPO / "docs" / "audits"


class TestTheFrames:
    def _runner(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("iq10_run_captures", REPO / "tools" / "iq10_run_captures.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_the_three_shots_turn_the_page_by_its_method(self):
        shots = {s["id"]: s for s in self._runner().SHOTS}
        for sid, needles in (("correspondence_desk", ("SEALED · ANSWER BY", "Read the letter ▸", "IN THE OFFING",
                                                      "◂ The Dispatch")),
                             ("correspondence_answered", ("Send five of the line. — N.", "wax seal",
                                                          "At sea — five of the line", "Admiralty ▸", "Bavaria ▸")),
                             ("correspondence_fate", ("fate in rubric", "LEFT UNANSWERED / SET ASIDE",
                                                      "Filed unanswered"))):
            row = shots[sid]
            assert row["scene"] == "res://scenes/dispatch_view.tscn" and row["method"] == "open"
            assert row["api_method"] == "get_dispatch" and row["payload"] == sid
            assert row["steps"][0]["call"] == "open_correspondence"
            for needle in needles:
                assert needle in row["must_show"], (sid, needle)
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        for sid in SURFACES:
            assert f'record("{sid}"' in cap, sid

    @pytest.mark.parametrize("stem", STEMS)
    def test_the_frames_are_committed_at_both_scales(self, stem):
        for tail in ("", "_X2"):
            png = AUDITS / f"IQ10_CORRESPONDENCE_{stem}{tail}_{FRAME_DATE}.png"
            assert png.exists(), png
            assert png.stat().st_size > 8000, png

    def test_the_review_plan_names_the_stems(self):
        plan = (REPO / "docs" / "UX_UI_REVIEW_PLAN.md").read_text(encoding="utf-8")
        for stem in STEMS:
            assert f"IQ10_CORRESPONDENCE_{stem}" in plan, stem

    def test_the_record_covers_the_page_at_every_resolution_with_no_red(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        from uxr0_readability_report import PHYSICAL_RESOLUTIONS, totals
        record = json.loads((AUDITS / "uxr0" / f"readability_correspondence_{FRAME_DATE}.json").read_text(encoding="utf-8"))
        for sid in SURFACES:
            surf = record["surfaces"].get(sid)
            assert surf is not None, sid
            keys = set(surf["readings"])
            for (w, h) in PHYSICAL_RESOLUTIONS:
                assert any(k.startswith(f"{w}x{h}@") for k in keys), (sid, w, h, keys)
            for key, r in surf["readings"].items():
                assert r["ok"] and r["counts"]["rows"] > 0, (sid, key)
                assert r["counts"]["red"] == 0 and r["counts"]["p1"] == 0, (sid, key, r["flagged"][:3])
        t = totals(record)
        assert t["red"] == 0 and t["p1"] == 0, t
