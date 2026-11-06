"""RE-2 — "Affairs of State": the client and the dress (`docs/RECURRING_EVENTS_SPEC.md`
§12 the client, §12b.2 the letter's dress, §0b P9/P11/P12/P14, §16 "RE-2";
row RE built before S15 by the user's ruling of October 31, 2026 — §0c).

PART 1 — THE BACKEND HALF (commit A): the quiet arrival (no popup slot for an
affair, the campaign's first one excepted; a NORMAL card that survives a full
tray and retires with the letter; the safety valve exempt; a court's letter
takes the head from a standing affair; the mailbox rank below the courts'
mail); the register on every backend reader (the payload's dress keys, the
mailbox row, the notice, the lapse row, the envoy list, the first-open
screen); the Watch on the situation only when armed; the derived button
lines; the driver's own dial; the first-open line.

PART 2 — THE CLIENT HALF (commit B): the `INK_*` census, the letterhead, the
two-line buttons, the counsel, the answer beat, the frames, the harness, the
readability record.

The shipped 1805 boot authors no `moments.affairs` key (RE-3 arms it), so
every pin here arms the real booted world with the staged fixture
`tests/fixtures/affairs_block.json`, as `tests/test_affairs_engine.py` does.
"""
import argparse
import contextlib
import io
import json
import re
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import ai_diplomacy as AI
from backend.game_logic import dispatch as DP
from backend.game_logic import envoy_digest as ED
from backend.game_logic import first_open as FO
from backend.game_logic import moments as MO
from backend.notifications import (
    DIPLOMATIC_PROPOSAL, NOTIFICATION_CAP, NotificationPriority, create_notification,
)
from tests import _chip_census as C
from tests.test_first_open import _TYPED

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "backend"
FIXTURE = REPO / "tests" / "fixtures" / "affairs_block.json"
T1, T2, T3 = "chancellors_letters", "the_host", "berthiers_memorial"
MATCH = "bavarian_match"


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _block():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


@pytest.fixture
def armed(world):
    world.moments = MO.from_block(_block())
    # RE-3: the shipped boot is ARMED and read its first morning's premises
    # before the test re-arms the board, so the memo of that morning is the
    # boot's (the Emperor at home, no corps quartered); a board built at
    # turn 1 must read its own morning.
    world.__dict__.pop("_affairs_memo", None)
    return world


def _at(world, turn):
    world.current_turn = int(turn)
    world.invalidate_active_nations_cache()


def _tick(world):
    with _quiet():
        return MO.tick(world)


def _run(world, turns):
    out = {}
    for turn in turns:
        _at(world, turn)
        delivered = _tick(world)
        if delivered:
            out[int(turn)] = delivered
    return out


def _letter(world, moment_id):
    dm = world.dialogue_manager
    for d in [dm.peek()] + list(dm.iter_queue()):
        if MO.is_moment_letter(d) and MO.moment_id_of(d) == moment_id:
            return d
    return None


def _notice(world, moment_id):
    rows = [n for n in world.notifications.get_pending()
            if (n.get("details") or {}).get("moment_id") == moment_id]
    assert len(rows) <= 1, rows
    return rows[0] if rows else None


def _no_moments(world):
    for e in MO.deck(world):
        world.moments["state"][str(e["id"])] = {"status": "passed", "turn": 1, "reason": "premise"}


def _quarter(world, names, region="Swabia"):
    for name in names:
        world.marshals[name].location = region


def _rel(world, court):
    return int(world.nation_relations.get(world._make_diplo_key("France", court), 0))


def _deliver_affair(world, template, mid, turn, bind=None, tier=1):
    """Seam 1 directly: the occurrence row as the engine freezes it."""
    _at(world, turn)
    row = {"id": mid, "lord": "France", "bind": dict(bind or {}), "tier": int(tier)}
    with _quiet():
        return MO.deliver_letter(world, MO.entry(world, template), int(turn), mid=mid, row=row)


def _deliver_moment(world, mid, turn):
    _at(world, turn)
    with _quiet():
        return MO.deliver_letter(world, MO.entry(world, mid), int(turn))


def _court_letter(world, court="Sweden"):
    terms = {"type": "open_borders", "proposer_nation": court, "target_nation": "France",
             "demands": [], "sweeteners": []}
    with _quiet():
        return AI.build_ai_proposal_dialogue(
            AI._make_proposal(court, "open_borders", 3, terms, world), world)


def _floats(value, path=""):
    if isinstance(value, bool):
        return []
    if isinstance(value, float):
        return [path]
    if isinstance(value, dict):
        return [p for k, v in value.items() for p in _floats(v, f"{path}.{k}")]
    if isinstance(value, list):
        return [p for i, v in enumerate(value) for p in _floats(v, f"{path}[{i}]")]
    return []


# ═══════════════════════════════════════════════════════════════════════════
# The quiet arrival (§12, Q8)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheQuietArrival:
    def test_the_campaign_s_first_affair_opens_itself_once(self, armed):
        _no_moments(armed)
        _quarter(armed, ("Ney", "Davout"))
        armed.incoming_proposal_popup = None
        assert _run(armed, range(1, 8)) == {7: ["the_host#1"]}
        popup = armed.incoming_proposal_popup
        assert popup and popup["moment_id"] == "the_host#1" and popup["register"] == "affair"
        letter = _letter(armed, "the_host#1")
        assert letter["mailbox_priority"] == MO.AFFAIR_MAILBOX_PRIORITY == 5
        notice = _notice(armed, "the_host#1")
        assert int(notice["priority"]) == int(NotificationPriority.NORMAL)
        assert notice["title"] == "An Affair of State: The Host's Claims"
        assert notice["details"]["standing_letter"] is True
        assert notice["details"]["review_target"] == "moment_letter"
        assert notice["details"]["route_id"] == str(letter["mailbox_id"])
        assert notice["expires_after_turn"] == letter["popup_payload"]["answer_by_turn"]

    def test_a_later_affair_arrives_quietly_even_at_the_head_of_the_queue(self, armed):
        _no_moments(armed)
        _deliver_affair(armed, T2, "the_host#1", 7, {"host": "Bavaria"})
        first = _letter(armed, "the_host#1")
        with _quiet():
            assert MO.answer(armed, first, MO.ANSWER_DECLINE)["success"] is True
        armed.incoming_proposal_popup = None
        _deliver_affair(armed, T2, "the_host#2", 12, {"host": "Bavaria"})
        second = _letter(armed, "the_host#2")
        assert armed.dialogue_manager.peek() is second
        assert armed.incoming_proposal_popup is None          # its card and its row open it
        notice = _notice(armed, "the_host#2")
        assert notice["details"]["route_id"] == str(second["mailbox_id"])
        rows = armed.dialogue_manager.get_mailbox_items()
        assert [r["mailbox_id"] for r in rows] == [second["mailbox_id"]]

    def test_a_moment_letter_still_opens_itself_and_rings_high(self, armed):
        armed.incoming_proposal_popup = None
        _deliver_moment(armed, MATCH, 8)
        letter = _letter(armed, MATCH)
        assert armed.incoming_proposal_popup["moment_id"] == MATCH
        assert letter["mailbox_priority"] == MO.MAILBOX_PRIORITY == 2
        notice = _notice(armed, MATCH)
        assert int(notice["priority"]) == int(NotificationPriority.HIGH)
        assert notice["title"] == "A Moment of History: The Bavarian Match"
        assert "standing_letter" not in notice["details"]
        assert "expires_after_turn" not in notice

    def test_the_card_survives_a_full_tray_and_retires_with_the_letter(self, armed):
        _no_moments(armed)
        _deliver_affair(armed, T2, "the_host#1", 7, {"host": "Bavaria"})
        for i in range(NOTIFICATION_CAP + 5):
            armed.notifications.add(create_notification(
                DIPLOMATIC_PROPOSAL, NotificationPriority.NORMAL, f"Envoy {i}", "x", 9))
        assert len(armed.notifications._pending) == NOTIFICATION_CAP
        assert _notice(armed, "the_host#1") is not None       # newer NORMAL rows went first
        with _quiet():
            MO.answer(armed, _letter(armed, "the_host#1"), MO.ANSWER_ACCEPT)
        assert _notice(armed, "the_host#1") is None

    def test_the_card_retires_at_the_lapse_too(self, armed):
        _no_moments(armed)
        _deliver_affair(armed, T2, "the_host#1", 7, {"host": "Bavaria"})
        letter = _letter(armed, "the_host#1")
        with _quiet():
            lapsed = MO.lapse_default(armed, letter)
        assert lapsed["moment"]["id"] == "the_host#1"
        assert _notice(armed, "the_host#1") is None
        assert MO.status(armed, "the_host#1") == "lapsed"

    def test_the_safety_valve_never_re_sends_an_affair(self, armed):
        _no_moments(armed)
        _deliver_affair(armed, T2, "the_host#1", 7, {"host": "Bavaria"})
        affair = _letter(armed, "the_host#1")
        assert armed.dialogue_manager.peek() is affair
        armed.incoming_proposal_popup = None
        with _quiet():
            response = M.build_base_response(armed)
        assert response["incoming_proposal"] is None
        # a moment at the head is re-derived as before — and it takes the head
        _deliver_moment(armed, MATCH, 8)
        armed.incoming_proposal_popup = None
        assert armed.dialogue_manager.peek() is _letter(armed, MATCH)
        with _quiet():
            response = M.build_base_response(armed)
        assert (response["incoming_proposal"] or {}).get("moment_id") == MATCH

    def test_the_valve_s_tuple_is_unchanged(self):
        assert M.SAFETY_VALVE_DIALOGUE_TYPES == (
            "incoming_proposal", "incoming_ultimatum", "counter_offer", "counter_offer_response")
        assert MO.is_quiet_letter({"context": {"proposal_type": "moment_letter", "moment_id": "the_host#1"}})
        assert not MO.is_quiet_letter({"context": {"proposal_type": "moment_letter", "moment_id": MATCH}})
        assert not MO.is_quiet_letter({"type": "incoming_proposal", "context": {}})
        assert MO.register_of({"context": {"proposal_type": "moment_letter", "moment_id": MATCH}}) == "moment"

    def test_a_court_s_letter_takes_the_head_from_a_standing_affair(self, armed):
        _no_moments(armed)
        _deliver_affair(armed, T2, "the_host#1", 7, {"host": "Bavaria"})
        affair = _letter(armed, "the_host#1")
        dm = armed.dialogue_manager
        court = _court_letter(armed)
        dm.push(court)
        assert dm.peek() is court and affair in list(dm.iter_queue())
        # a second quiet letter behind a quiet head stays queued
        dm.remove_matching(lambda d: d is court)
        dm.promote_if_empty()
        assert dm.peek() is affair
        _deliver_affair(armed, T1, "chancellors_letters#1", 9, {"region": "Swabia"})
        assert dm.peek() is affair and _letter(armed, "chancellors_letters#1") in list(dm.iter_queue())

    def test_a_moment_at_the_head_is_not_displaced(self, armed):
        _deliver_moment(armed, MATCH, 8)
        moment = _letter(armed, MATCH)
        dm = armed.dialogue_manager
        court = _court_letter(armed)
        dm.push(court)
        assert dm.peek() is moment and court in list(dm.iter_queue())

    def test_the_mailbox_ranks_an_affair_below_the_courts_mail(self, armed):
        _no_moments(armed)
        _deliver_affair(armed, T2, "the_host#1", 7, {"host": "Bavaria"})
        dm = armed.dialogue_manager
        court = _court_letter(armed)
        dm.push(court)                                          # the head
        _deliver_moment(armed, MATCH, 8)                        # queued behind the court
        rows = dm.get_mailbox_items()
        ids = [r["mailbox_id"] for r in rows]
        assert ids == [court["mailbox_id"], _letter(armed, MATCH)["mailbox_id"],
                       _letter(armed, "the_host#1")["mailbox_id"]]
        assert [r.get("register") for r in rows] == [None, None, "affair"]


# ═══════════════════════════════════════════════════════════════════════════
# The register on every backend reader (§12, §12b.2)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRegister:
    def test_the_affair_s_payload_carries_the_dress(self, armed):
        _no_moments(armed)
        rel = _rel(armed, "Bavaria")
        _deliver_affair(armed, T2, "the_host#1", 7, {"host": "Bavaria"})
        p = _letter(armed, "the_host#1")["popup_payload"]
        assert p["register"] == "affair" and p["proposal_type_display"] == "An Affair of State"
        assert p["header"] == f"AN AFFAIR OF STATE — {p['dateline'].upper()}"
        assert p["device"] == {"kind": "arms", "nation": "Bavaria", "letter": ""}
        assert (p["arms"], p["monogram"]) == ("Bavaria", "")
        assert (p["writer"], p["office"]) == ("Montgelas", "for the court of Munich")
        assert p["diplomat_name"] == "Montgelas"
        assert p["ground"].startswith("Historically the Emperor's rule was that war must feed war")
        assert p["chapter"] == "" and p["exhibit"] == "" and p["odds"] == 0
        assert p["counsel"].startswith("Talleyrand — An ally presents his bill once as an account")
        assert p["talleyrand_assessment"] == p["counsel"]
        assert p["button_accept"] == "−300 gold"
        assert p["button_decline"] == f"auth 100 → 98 · Bavaria {rel} → {rel - 2}"   # AU-2a: the Host's Complaint priced first
        assert p["occurrence"] == "the_host#1"
        assert _floats(p) == []                                 # GR2: every figure an int

    def test_the_moment_s_payload_carries_the_same_dress_in_its_own_register(self, armed):
        rel = _rel(armed, "Bavaria")
        _deliver_moment(armed, MATCH, 8)
        m = _letter(armed, MATCH)["popup_payload"]
        assert m["register"] == "moment" and m["proposal_type_display"] == "A Moment of History"
        # BUG_FIXES RE2-1: RE-1 dressed every delivered moment as an affair
        # (its status row read as an occurrence) and emptied its board — the
        # moments' own board lines, as S14c wrote them.
        assert m["board"] == MO.board_lines(armed, MO.entry(armed, MATCH)) != []
        assert m["header"] == f"A MOMENT OF HISTORY — {m['dateline'].upper()}"
        assert m["device"] == {"kind": "sheet", "nation": "France", "letter": ""}
        assert (m["arms"], m["monogram"]) == ("", "")
        assert (m["writer"], m["office"]) == ("The Secretariat", "")
        assert m["line"] == "" and m["chapter"] == "" and m["exhibit"] == ""
        assert m["ground"] == m["record"]
        # RE-3 (P12) authored the four moments' counsel lines — under the buttons
        assert m["counsel"].startswith("Talleyrand — A match binds Munich to the family")
        assert m["talleyrand_assessment"] == m["counsel"]
        assert m["button_accept"] == f"−2 DP · −1,000 gold · Bavaria {rel} → {min(100, rel + 20)}"
        assert len(m["button_accept"]) <= MO.BUTTON_LINE_MAX
        assert m["button_decline"] == f"Bavaria {rel} → {rel - 5}"
        assert "occurrence" not in m
        assert _floats(m) == []

    def test_the_device_by_speaker(self, armed):
        occ = {"id": "chancellors_letters#1", "lord": "France", "bind": {"region": "Swabia"}, "tier": 1}
        assert MO.device_of(armed, MO.entry(armed, T1), occ, "Cambacérès") == \
            {"kind": "monogram", "nation": "", "letter": "C"}
        assert MO.device_of(armed, MO.entry(armed, T3), {"id": "berthiers_memorial#1"}, "Berthier") == \
            {"kind": "monogram", "nation": "", "letter": "B"}
        # a court's deputation (Ver Huell for the States General) under the court's arms
        assert MO.device_of(armed, MO.entry(armed, "throne_of_holland"), {}, "Admiral Ver Huell") == \
            {"kind": "arms", "nation": "Holland", "letter": ""}
        assert MO.device_of(armed, MO.entry(armed, "decree_of_berlin"), {}, "Talleyrand") == \
            {"kind": "monogram", "nation": "", "letter": "T"}
        assert MO.device_of(armed, {"voice": {"speaker": "envoy", "nation": "Austria"}}, {}, "Metternich") == \
            {"kind": "arms", "nation": "Austria", "letter": ""}
        assert MO.device_of(armed, {"voice": {"speaker": "cabinet"}}, {}, "The Secretariat") == \
            {"kind": "sheet", "nation": "France", "letter": ""}

    def test_the_writer_and_the_office_and_the_holders_by_the_turn(self, armed):
        occ = {"id": "chancellors_letters#1", "lord": "France", "bind": {}, "tier": 1}
        assert MO._writer_and_office(armed, MO.entry(armed, T1), occ,
                                     "Cambacérès, Arch-Chancellor of the Empire") == \
            ("Cambacérès", "Arch-Chancellor of the Empire")
        assert MO._writer_and_office(armed, {"voice": {"speaker": "named"}}, {}, "Berthier") == ("Berthier", "")
        host = {"id": "the_host#1", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1}
        assert MO._writer_and_office(armed, MO.entry(armed, T2), host, "Montgelas") == \
            ("Montgelas", "for the court of Munich")
        assert MO._writer_and_office(armed, MO.entry(armed, T2), host, "The Chancery of Bavaria") == \
            ("The Chancery of Bavaria", "")
        voice = {"speaker": "office", "name": "Daru",
                 "holders": [{"name": "Dejean", "date": "1806-01-01", "turn": 10}]}
        assert MO.voice_of(armed, {"voice": voice}, None, 5) == "Dejean"
        assert MO.voice_of(armed, {"voice": voice}, None, 10) == "Daru"
        assert MO.voice_of(armed, {"voice": voice}) == "Daru"

    def test_every_backend_reader_names_the_register(self, armed):
        _no_moments(armed)
        _deliver_affair(armed, T2, "the_host#1", 7, {"host": "Bavaria"})
        dm = armed.dialogue_manager
        affair = _letter(armed, "the_host#1")
        row = next(r for r in dm.get_mailbox_items(armed) if r["mailbox_id"] == affair["mailbox_id"])
        assert row["register"] == "affair"
        assert row["summary"] == "The Secretariat — An Affair of State"
        assert row["summary_text"] == "An Affair of State: The Host's Claims"
        assert row["reason"] == ED.ROW_REASON_AFFAIR
        # the dispatch's envoy list
        with _quiet():
            dispatch = DP.build_morning_dispatch(armed)
        envoy = next(e for e in dispatch["pending_envoys"] if e.get("register") == "affair")
        assert envoy["proposal_type_display"] == "An Affair of State"
        assert envoy["nation"] == "The Secretariat"
        # the lapse row
        lapsed = DP._lapsed_offer_row({
            "nation": "The Secretariat", "proposal_type": "moment_letter",
            "moment": {"id": "the_host#1", "title": "The Host's Claims", "line": "x"}})
        assert lapsed["register"] == "affair" and lapsed["is_moment"] is True
        assert lapsed["proposal_type_display"] == "An Affair of State"
        plain = DP._lapsed_offer_row({
            "nation": "The Secretariat", "proposal_type": "moment_letter",
            "moment": {"id": MATCH, "title": "The Bavarian Match", "line": "x"}})
        assert "register" not in plain and plain["is_moment"] is True
        # the first-open screen
        assert FO.dialogue_screen(affair) == ("affair_letter", {})
        wired = FO.with_line(armed, affair)
        assert wired["first_open"]["screen"] == "affair_letter"
        assert "Sire" in wired["first_open"]["line"]
        assert "first_open" not in affair
        # a moment's row: no register key, the moment's reason, the moment's screen
        _deliver_moment(armed, MATCH, 8)
        moment = _letter(armed, MATCH)
        mrow = next(r for r in dm.get_mailbox_items(armed) if r["mailbox_id"] == moment["mailbox_id"])
        assert "register" not in mrow and mrow["reason"] == ED.ROW_REASON_MOMENT
        assert FO.dialogue_screen(moment) == ("moment_letter", {})

    def test_the_affair_s_reason_names_the_lapse(self):
        assert ED.ROW_REASON_AFFAIR.startswith("An affair of state is answered in full")
        assert "second answer" in ED.ROW_REASON_AFFAIR


# ═══════════════════════════════════════════════════════════════════════════
# The Watch on the situation (§12)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheWatch:
    def test_the_watch_rides_the_situation_only_when_armed(self, world):
        world.moments["block"].pop("affairs", None)              # an unarmed world, explicitly (RE-3)
        world.moments.pop("affairs", None)
        with _quiet():
            unarmed = DP._build_situation(world, "France")
        assert "affairs_watch" not in unarmed
        world.moments = MO.from_block(_block())
        world.__dict__.pop("_affairs_memo", None)               # the boot's morning, not this board's
        _quarter(world, ("Ney", "Davout"))
        world.nation_gold["France"] = 20_000
        # RE-6: the corps on Bavaria draw campaign pay (the Magazines' clause)
        # and the pool sits at 50 % (the Remounts') — the offers stood aside
        from tests._affairs_boards import rest_the_offers, without_the_proclamation
        rest_the_offers(world)
        without_the_proclamation(world)                       # AU-3b armed: the Host and the door alone
        _run(world, [1, 2])
        with _quiet():
            situation = DP._build_situation(world, "France")
        assert situation["affairs_watch"] == [
            "3 corps on Bavaria's soil: 2 of 3 mornings — its court may present its claims.",
            "At war 2 of 4 turns, and the chest could found the headquarters — Berthier may write."]
        assert all(isinstance(x, str) for x in situation["affairs_watch"])

    def test_the_watch_is_empty_not_absent_while_a_letter_stands(self, armed):
        from tests._affairs_boards import without_the_proclamation
        _no_moments(armed)
        without_the_proclamation(armed)                       # AU-3b armed: the Host's letter alone
        _quarter(armed, ("Ney", "Davout"))
        _run(armed, range(1, 8))
        assert MO.status(armed, "the_host#1") == "fired"
        with _quiet():
            situation = DP._build_situation(armed, "France")
        assert situation["affairs_watch"] == []


# ═══════════════════════════════════════════════════════════════════════════
# The derived button lines (P11)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDerivedButtonLines:
    def test_the_figures_as_tokens_cut_at_a_token_boundary(self, armed):
        rows = [{"op": "gold", "amount": 1000}, {"op": "dp", "amount": 2},
                {"op": "relation", "court": "Bavaria", "before": 46, "after": 66},
                {"op": "alarm", "before": 0, "after": 3}]
        line = MO._derived_button_line(armed, "France", rows)
        assert line == "−1,000 gold · −2 DP · Bavaria 46 → 66"
        assert len(line) <= MO.BUTTON_LINE_MAX == 40
        assert MO._derived_button_line(armed, "France", []) == "no change"
        assert MO._derived_button_line(armed, "France", [
            {"op": "relation", "skip": True}, {"op": "authority", "skip": True}]) == "no change"
        assert MO._derived_button_line(armed, "France", [
            {"op": "authority", "before": 85, "after": 80}]) == "authority 85 → 80"
        assert MO._derived_button_line(armed, "France", [{"op": "admin", "amount": 1}]) == "1 action"
        assert MO._derived_button_line(armed, "France", [
            {"op": "loyalty", "courts": [{"court": "Bavaria", "before": 60, "after": 75}]}]) == \
            "Bavaria loyalty 60 → 75"
        assert MO._derived_button_line(armed, "France", [
            {"op": "enact_law", "law": "grand_quartier_general", "refusal": ""}]) == \
            "−9,000 gold · 300 a turn · 1 action"
        assert MO._derived_button_line(armed, "France", [
            {"op": "enact_law", "law": "grand_quartier_general", "refusal": "closed"}]) == "no change"
        # a decree priced in authority says so in the button's own word — and
        # the full line (41) is cut at the token boundary: the action drops
        standing = int(armed.authority_tracker.authority)
        decree = MO._derived_button_line(armed, "France", [
            {"op": "enact_law", "law": "berlin_decree", "refusal": ""}])
        assert decree == f"authority {standing} → {standing - 15} · 150 a turn"
        assert len(decree) <= MO.BUTTON_LINE_MAX
        long = MO._derived_button_line(armed, "France", [
            {"op": "relation", "court": "A" * 60, "before": 1, "after": 2}])
        assert len(long) == MO.BUTTON_LINE_MAX and long.endswith("…")

    def test_an_authored_button_line_wins_and_every_plan_carries_a_receipt(self, armed):
        rel = _rel(armed, "Bavaria")
        p = MO.plan(armed, MO.entry(armed, MATCH), MO.ANSWER_ACCEPT)
        assert p["receipt"] == f"−2 DP · −1,000 gold · Bavaria {rel} → {min(100, rel + 20)}"
        occ = {"id": "the_host#1", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1}
        assert MO.plan(armed, MO.entry(armed, T2), MO.ANSWER_ACCEPT, occ)["receipt"] == "−300 gold"
        occ = {"id": "berthiers_memorial#1", "lord": "France", "bind": {"law": "grand_quartier_general"}, "tier": 1}
        assert MO.plan(armed, MO.entry(armed, T3), MO.ANSWER_DECLINE, occ)["receipt"] == "no change"


# ═══════════════════════════════════════════════════════════════════════════
# The driver's own dial
# ═══════════════════════════════════════════════════════════════════════════

class TestTheDriverDial:
    def _options(self, accept_enabled=True, reason=""):
        return [{"label": "Pay the host's claims", "action": "accept_ai_proposal",
                 "enabled": accept_enabled, "reason": reason},
                {"label": "Live off the land", "action": "reject_ai_proposal",
                 "enabled": True, "reason": ""}]

    def test_the_dial_is_absent_by_default_so_every_arm_is_unchanged(self):
        from tools import playtest_driver as D
        assert "affair" in D.POLICY_FLAG_KEYS and "affair" not in D.POLICY_DEFAULTS
        assert json.dumps(D.resolve_policy(argparse.Namespace(), {})) == json.dumps(dict(D.POLICY_DEFAULTS))
        assert D.affair_mode({}) == "decline"
        assert D.affair_mode({"moment": "accept", "diplomacy": "accept"}) == "decline"
        assert D.affair_mode({"affair": "accept"}) == "accept"
        assert D.resolve_policy(argparse.Namespace(affair="accept"), {})["affair"] == "accept"
        src = (REPO / "tools" / "playtest_driver.py").read_text(encoding="utf-8")
        assert '"--affair"' in src

    def test_an_affair_answers_from_its_own_dial_never_the_moment_s(self):
        from tools import playtest_driver as D
        affair = {"is_moment": True, "proposal_type": "moment_letter", "register": "affair",
                  "moment_id": "the_host#1", "from_nation": "", "options": self._options()}
        moment = {"is_moment": True, "proposal_type": "moment_letter", "register": "moment",
                  "moment_id": MATCH, "from_nation": "", "options": self._options()}
        by_moment = D.Answerer(None, None, dict(D.POLICY_DEFAULTS) | {"moment": "accept"}, False)
        assert by_moment._pick_dialogue_choice(affair) == "reject_ai_proposal"
        assert by_moment._pick_dialogue_choice(moment) == "accept_ai_proposal"
        by_affair = D.Answerer(None, None, dict(D.POLICY_DEFAULTS) | {"affair": "accept"}, False)
        assert by_affair._pick_dialogue_choice(affair) == "accept_ai_proposal"
        assert by_affair._pick_dialogue_choice(moment) == "reject_ai_proposal"
        closed = dict(affair, options=self._options(False, "the day's administration is spoken for."))
        assert by_affair._pick_dialogue_choice(closed) is None
        assert by_affair.last_standing_reason == "the day's administration is spoken for."
        assert D._is_affair_surface({"moment_id": "the_host#1"})
        assert not D._is_affair_surface({"moment_id": MATCH})
        assert D._is_affair_surface({"context": {"proposal_type": "moment_letter", "moment_id": "the_host#1"}})

    def test_the_lapse_dial_leaves_the_quiet_letter_in_the_mailbox_unopened(self):
        """RE-3 (§16 "RE-3", the lapse default): under `--affair lapse` the
        mailbox pass never activates an affair's row — a player who lets a
        letter lapse never opens it, and the engine lapses it in the queue
        on its answer-by turn (`lapse_gate_rows` reads the queue). Opening it
        every turn put it in the active slot and displaced the dialogue
        standing there (a client's petition, which lapsed unanswered): the
        Rhine road moved on two seeds for that, not for the letter — the
        attribution ran the same arm with the Host's decline billing nothing
        and moved the same way. Under `decline` and `accept` the row is
        activated and answered on arrival, as before."""
        from tests.test_fa_slice17_f_the_instrument_answers_2026_09_11 import make_answerer
        mailbox = {"items": [
            {"mailbox_id": 15, "source_nation": "The Secretariat", "item_type": "incoming_proposal",
             "summary": "The Secretariat — An Affair of State", "register": "affair"},
            {"mailbox_id": 16, "source_nation": "Bavaria", "item_type": "incoming_proposal",
             "summary": "Bavaria — Client's Petition"},
        ]}
        for mode in ("decline", "accept"):
            a, t, d = make_answerer(gets={"/mailbox": mailbox}, policy_overrides={"affair": mode})
            a.answer_mailbox_items(mailbox)
            assert [p[1]["mailbox_id"] for p in t.posts if p[0] == "/mailbox/activate"] == [15, 16], mode
        a, t, d = make_answerer(gets={"/mailbox": mailbox}, policy_overrides={"affair": "lapse"})
        a.answer_mailbox_items(mailbox)
        a.answer_mailbox_items(mailbox)                     # the next turn lists it again
        assert [p[1]["mailbox_id"] for p in t.posts if p[0] == "/mailbox/activate"] == [16, 16]
        left = [n for n in d.notes if "left in the mailbox" in str(n)]
        assert len(left) == 1 and "#15" in str(left[0]) and "--affair lapse" in str(left[0]), d.notes


# ═══════════════════════════════════════════════════════════════════════════
# The first-open line (§12b.1) and the copy census
# ═══════════════════════════════════════════════════════════════════════════

class TestTheFirstOpenLine:
    def test_the_line_under_the_cap_opens_to_the_sovereign_and_teaches_no_typed_order(self, armed):
        assert "affair_letter" in FO.SCREENS and "affair_letter" in FO.LINES
        line = FO.line_for(armed, "affair_letter")
        assert line and len(line) <= FO.LINE_CAP and "Sire" in line and "_" not in line
        assert not _TYPED.search(line)
        assert "priced on its button" in line and "second answer" in line
        assert FO.mark_seen(armed, "affair_letter") is True
        assert "affair_letter" in FO.seen(armed)

    def test_the_fixture_s_copy_teaches_no_typed_order(self):
        texts = []
        for e in _block()["affairs"]["deck"]:
            for key in ("title", "record", "line", "counsel", "watch", "exhibit"):
                if e.get(key):
                    texts.append((e["id"], key, str(e[key])))
            for side in ("accept", "decline"):
                for key in ("caption", "button_line", "echo"):
                    if (e.get(side) or {}).get(key):
                        texts.append((e["id"], f"{side}.{key}", str(e[side][key])))
        assert len(texts) >= 20
        for template, key, text in texts:
            assert not _TYPED.search(text), (template, key, text)
            plain = re.sub(r"\{[a-z_]+\}", "", text)            # the slots are the author's
            assert "_" not in plain, (template, key, text)      # no internal key leaks


# ═══════════════════════════════════════════════════════════════════════════
# PART 2 — THE CLIENT HALF (commit B): the dress (§12b.2), the beat, the readers
# ═══════════════════════════════════════════════════════════════════════════

GODOT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = GODOT / "scripts"
AUDITS = REPO / "docs" / "audits"
INK = {"INK_BODY": "2B1D12", "INK_RUBRIC": "6A1410", "INK_SEPIA": "4E3820",
       "INK_RULE": "8A7A5A", "INK_SHEET_HC": "EFE3C6"}
FRAME_DATE = "2026_10_31"
AFFAIR_STEMS = ("THE_HOST", "BERTHIERS_MEMORIAL", "CLOSED_ACCEPT")
# RE-H (November 1, 2026): the Haiti letter's two forms, shot under their own date
FRAME_DATE_H = "2026_11_01"
AFFAIR_STEMS_H = ("SANTO_DOMINGO_BILL", "SANTO_DOMINGO_SQUADRON")


def _gd(name):
    return (SCRIPTS / name).read_text(encoding="utf-8")


def _func(src, name):
    start = src.index(f"func {name}(")
    nxt = src.find("\nfunc ", start + 5)
    return src[start:nxt if nxt > 0 else len(src)]


def _code(src):
    """The source without comments and docstrings (a census reads code)."""
    src = re.sub(r'"""(.*?)"""', '""', src, flags=re.S)
    return "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))


class TestTheInk:
    def test_the_five_inks_are_hex_tokens_in_utils(self):
        src = _gd("utils.gd")
        for name, hexval in INK.items():
            assert f'const {name} := "{hexval}"' in src, name

    def test_every_inline_colour_the_register_emits_is_an_ink(self):
        """§12b.2 — no gold on paper: the dress's own code paths name only
        `Utils.INK_*` tokens, and the remap covers every token the S14c
        register wrote (the grey first-open line, the closed-Accept red, the
        gold header and lapse lines, the grey assessment slot)."""
        src = _gd("incoming_proposal_popup.gd")
        for name in ("_build_moment_body", "_dress_letter", "_ensure_letter_dress",
                     "play_answer_beat", "_set_letter_device"):
            body = _code(_func(src, name))
            for tok in re.findall(r'\[color=#" \+ Utils\.([A-Z_]+)', body):
                assert tok.startswith("INK_"), (name, tok)
            assert not re.search(r'\[color=#[0-9a-fA-F]{6}\]', body), name
            for m in re.finditer(r'Color\.html\(Utils\.([A-Z_]+)\)', body):
                assert m.group(1).startswith("INK_"), (name, m.group(1))
        # the remap: every S14c token the register still writes lands on an ink
        ink = _code(_func(src, "_ink"))
        remaps = re.findall(r'\.replace\((.+?), "\[color=#" \+ Utils\.([A-Z_]+) \+ "\]"\)', ink)
        assert remaps, "the remap is gone"
        for _source, target in remaps:
            assert target.startswith("INK_"), (_source, target)
        for source in ('Utils.COLOR_INFO', 'Utils.COLOR_ERROR', '"[color=#e0c060]"',
                       'Utils.COLOR_WARNING', 'Utils.COLOR_GOLD', '"[color=gray]"'):
            assert source in ink, source
        # the body is inked whole, under the one wrapper
        assert '"[color=#" + Utils.INK_BODY + "]" + _ink(body) + "[/color]"' in _func(src, "_dress_letter")

    def test_the_type_stays_on_the_ladder(self):
        src = _code(_gd("incoming_proposal_popup.gd"))
        assert "add_theme_font_size_override(" not in src
        assert "[font_size=" not in src
        assert "CanvasLayer.new()" not in src                  # the beat rides an existing layer
        assert "_set_aside_line = Label.new()" in _func(_gd("incoming_proposal_popup.gd"), "_ready")


class TestTheDress:
    def test_the_sheet_the_letterhead_and_the_device(self):
        src = _gd("incoming_proposal_popup.gd")
        build = _func(src, "_ensure_letter_dress")
        assert 'const LETTER_SHEET := "res://assets/textures/old-parchment_alpha.png"' in src
        assert "StyleBoxTexture.new()" in build and "load(LETTER_SHEET)" in build
        assert "vbox.move_child(_letterhead, 0)" in build         # the VBox's head, no new sibling
        assert "Color.html(Utils.INK_SHEET_HC)" in build           # High contrast: the cream sheet
        dress = _func(src, "_dress_letter")
        assert "UiSettings.get_high_contrast()" in dress
        assert 'add_theme_stylebox_override("panel", panel_style)' in dress   # restored otherwise
        device = _func(src, "_set_letter_device")
        assert "PortraitLocket.new()" in device and "Utils.nation_flag_path(" in device
        assert "Napoleon" not in device                            # never his portrait
        for name in ("_sheet", "_sheet_hc", "_closed_plaque", "_fell_italic", "_cinzel"):
            assert re.search(rf"(?m)^var {name}\b", src), name
            assert not re.search(rf"(?m)^static var {name}\b", src), name   # S14E-X207

    def test_the_two_line_buttons_and_the_opaque_plaque(self):
        src = _gd("incoming_proposal_popup.gd")
        dress = _func(src, "_dress_letter")
        assert "const LETTER_BUTTON_MIN_HEIGHT := 56.0" in src
        assert "const LETTER_BUTTON_LINE_MAX := 40" in src
        assert 'const NOT_NOW_DESK_LINE := "waits on the desk"' in src
        assert 'accept_btn.text = accept_btn.text + "\\n" + accept_line' in dress
        assert '_button_second_line(data, "button_decline"' in dress
        assert 'dismiss_btn.text = dismiss_btn.text + "\\n" + NOT_NOW_DESK_LINE' in dress
        assert 'accept_btn.add_theme_stylebox_override("disabled", _closed_plaque)' in dress
        assert 'accept_btn.remove_theme_stylebox_override("disabled")' in dress
        assert "Vector2(140, 45)" in dress                        # the scene's size, restored

    def test_the_counsel_rides_under_the_buttons_and_the_grey_slot_is_skipped(self):
        src = _gd("incoming_proposal_popup.gd")
        dress = _func(src, "_dress_letter")
        assert '_moment_text(data.get("counsel", ""))' in dress
        assert '_set_aside_line.add_theme_font_override("font", _fell_italic)' in dress
        assert 'Color.html(Utils.INK_SEPIA)' in dress
        show = _func(src, "show_proposal")
        assert "if is_moment:\n\t\tassessment = \"\"" in show
        # the dress is applied after the body and the captions, before show()
        assert show.index("_dress_letter(data, is_moment, grant_enabled, grant_reason)") < show.index("\tshow()")
        # the pinned S14c strings are where they were
        assert "A MOMENT OF HISTORY — " in show and 'data.get("unanswered_line", "")' in show

    def test_the_body_writes_history_in_fell_italic_and_the_board_with_fleurons(self):
        body = _func(_gd("incoming_proposal_popup.gd"), "_build_moment_body")
        assert '"[font=" + LETTER_FELL_ITALIC + "]"' in body
        src = _gd("incoming_proposal_popup.gd")
        assert 'const LETTER_FLEURON := "❧"' in src                # EB Garamond's hedera, a glyph
        assert '"]" + LETTER_FLEURON + "[/color] "' in body and "[img" not in body
        assert '"What each answer does".to_upper()' in body     # the S14c literal, in the rubric
        assert 'data.get("line", "")' in body and 'data.get("exhibit", "")' in body
        assert body.index('data.get("first_open")') < body.index('data.get("line", "")') < body.index('data.get("record", "")')


class TestTheBeat:
    def test_the_beat_plays_on_the_backends_own_word(self):
        popup = _gd("incoming_proposal_popup.gd")
        beat = _func(popup, "play_answer_beat")
        assert 'AudioManager.play("wax_seal", 1.4)' in beat
        assert "const LETTER_BEAT_SECONDS := 0.8" in popup
        assert "tw.tween_callback(slip.queue_free)" in beat
        assert "parent.add_child(slip)" in beat                   # under the given layer
        assert "rotation_degrees" in beat and '"N"' in beat        # the settle and the cipher
        for handler in ("_on_accept", "_on_reject"):
            assert "_pressed_rect = " in _func(popup, handler), handler
        assert "_pressed_rect" not in _func(popup, "_on_dismiss")  # Not Now: no slip
        main = _func(_gd("main.gd"), "_on_command_result")
        assert 'response.get("moment_answered", null)' in main
        assert "incoming_proposal_popup.play_answer_beat(" in main and "_beat_parent)" in main
        # RE5-3 (RE-5): the slip rides the scale card's existing layer 125, above
        # every dialog (the top bar's 75 sat beneath a promoted envoy); the top bar
        # stays the fallback
        assert "var _beat_parent = _scale_card_layer" in main and "_beat_parent = top_bar" in main

    def test_the_seal_is_imported_with_mipmaps(self):
        imp = (GODOT / "assets" / "ui" / "ornaments" / "wax_seal.png.import").read_text(encoding="utf-8")
        assert "mipmaps/generate=true" in imp


class TestTheReaders:
    def test_the_mailbox_tags_an_affair_and_keeps_the_moment_tag(self):
        src = _gd("mailbox_panel.gd")
        assert '"moment_letter": "Moment"' in src
        row = _func(src, "_build_item_row")
        assert 'str(item.get("proposal_type", "")) == "moment_letter"' in row
        assert 'str(item.get("register", "")) == "affair"' in row and '"Affair"' in row

    def test_the_dispatch_view_renders_the_watch(self):
        src = _gd("dispatch_view.gd")
        assert 'situation.get("affairs_watch", null)' in src
        assert "IN THE OFFING: " in src


class TestTheFrames:
    def _runner(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("_iq10_runner_re2", REPO / "tools" / "iq10_run_captures.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_the_affair_shots_are_registered_beside_the_moments(self):
        shots = {s["id"]: s for s in self._runner().SHOTS}
        for aid, needles in (("the_host", ("Pay the host's claims", "Live off the land", "parchment", "counsel")),
                             ("berthiers_memorial", ("Found the headquarters", "monogram", "counsel")),
                             ("closed_accept", ("OPAQUE", "spoken for", "authority 80 → 75")),
                             # RE-H: the Haiti letter's two forms
                             ("santo_domingo_bill", ("Send flour and muskets", "Ferrand must hold alone",
                                                     "FROM HAITI", "monogram 'D'", "IM Fell roman")),
                             ("santo_domingo_squadron", ("Send five of the line", "36 in 100 home",
                                                         "The passage: 36 in 100", "Boulogne counts them too"))):
            row = shots[f"affair_letter_{aid}"]
            assert row["scene"] == "res://scenes/incoming_proposal_popup.tscn"
            assert row["method"] == "show_proposal"
            for needle in needles:
                assert needle in row["must_show"], (aid, needle)
        for mid in ("bavarian_match", "decree_of_berlin"):
            assert "two-line" in shots[f"moment_letter_{mid}"]["must_show"]
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        for name in ("affair_letter_the_host", "affair_letter_berthiers_memorial", "affair_letter_closed_accept",
                     "affair_letter_santo_domingo_bill", "affair_letter_santo_domingo_squadron"):
            assert f'record("{name}"' in cap, name

    @pytest.mark.parametrize("stem, date", [(f"AFFAIR_LETTER_{s}", FRAME_DATE) for s in AFFAIR_STEMS]
                             + [("MOMENT_LETTER_BAVARIAN_MATCH", FRAME_DATE), ("MOMENT_LETTER_DECREE_OF_BERLIN", FRAME_DATE)]
                             + [(f"AFFAIR_LETTER_{s}", FRAME_DATE_H) for s in AFFAIR_STEMS_H])
    def test_the_frames_are_committed_at_both_scales(self, stem, date):
        for tail in ("", "_X2"):
            png = AUDITS / f"IQ10_{stem}{tail}_{date}.png"
            assert png.exists(), png
            assert png.stat().st_size > 8000, png

    def test_the_review_plan_names_the_new_stems(self):
        plan = (REPO / "docs" / "UX_UI_REVIEW_PLAN.md").read_text(encoding="utf-8")
        for stem in AFFAIR_STEMS + AFFAIR_STEMS_H:
            assert f"IQ10_AFFAIR_LETTER_{stem}" in plan, stem


class TestTheReadabilityRecord:
    RECORD = REPO / "docs" / "audits" / "uxr0" / f"readability_affairs_{FRAME_DATE}.json"
    RECORD_H = REPO / "docs" / "audits" / "uxr0" / f"readability_affairs_{FRAME_DATE_H}.json"

    @pytest.mark.parametrize("record_path, surface_ids", [
        (RECORD, ("moment_letter_bavarian_match", "affair_letter_the_host",
                  "affair_letter_berthiers_memorial", "affair_letter_closed_accept")),
        # RE-H: the Haiti letter's two forms, shot into their own record
        (RECORD_H, ("affair_letter_santo_domingo_bill", "affair_letter_santo_domingo_squadron")),
    ], ids=["re2", "re_h"])
    def test_the_record_covers_the_letters_at_every_resolution_with_no_red(self, record_path, surface_ids):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        from uxr0_readability_report import PHYSICAL_RESOLUTIONS, totals
        record = json.loads(record_path.read_text(encoding="utf-8"))
        surfaces = record["surfaces"]
        for sid in surface_ids:
            surf = surfaces.get(sid)
            assert surf is not None, sid
            keys = set(surf["readings"])
            for (w, h) in PHYSICAL_RESOLUTIONS:
                assert any(k.startswith(f"{w}x{h}@") for k in keys), (sid, w, h, keys)
            for key, r in surf["readings"].items():
                assert r["ok"], (sid, key)
                assert r["counts"]["rows"] > 0, (sid, key)
                assert r["counts"]["red"] == 0 and r["counts"]["p1"] == 0, (sid, key, r["flagged"][:3])
        t = totals(record)
        assert t["red"] == 0 and t["p1"] == 0, t
