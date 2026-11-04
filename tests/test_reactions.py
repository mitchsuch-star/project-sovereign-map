"""RE-R — "Affairs of State": the reactions (`docs/RECURRING_EVENTS_SPEC.md`
§12c, §16b "RE-R"; the landing record §24). The world answers a letter back
within the budget — one line per surface per letter, three per letter over
three turns, one COURTS line, no new rail notice, the only sound the seal:

the echo on the answer's own response (a second green line under the quote)
and the marshal's remark on the Host's "Live off the land" (the largest corps
on the host's soil, by name, by personality, else the default; frozen as
`remark_by`); the morning-after SITUATION receipt (`situation["affair_receipt"]`,
both views, plain; none for a lapse — LAPSED ENVOYS already says it); THE
COURTS' per-row transform (an affair's `answered` and `outcome` rows print
their authored `press`, nothing else prints); the `remember` board line on
the next letter of the same template and subject; `moment_answered` forwarded
at the response edge (the seal's trigger — RER-1); the noise census.

Every pin arms the real booted world with the staged fixture
`tests/fixtures/affairs_block.json`, as `tests/test_affairs_engine.py` does.
"""
import io
import json
import re
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import gazette as GZ
from backend.game_logic import moments as MO
from backend.game_logic import naval
from backend.game_logic.dispatch import build_morning_dispatch
from tests.test_affairs_engine import (  # noqa: F401 — the fixtures ride the import
    FIXTURE, SCENARIO, T1, _at, _letter, _make_current, _moment_rows, _no_moments, _quarter, _quiet,
    _restore_active_world, _run, _tick, armed, client, world,
)
from tests.test_affairs_haiti import _haiti_board
from tests.test_first_open import _func, _gd

H1 = "santo_domingo"
T2, T3 = "the_host", "berthiers_memorial"
REPO = Path(__file__).resolve().parents[1]
CHOICE = {"accept": "accept_ai_proposal", "decline": "reject_ai_proposal"}


def _answer(armed, client, mid, answer):
    letter = _letter(armed, mid)
    assert letter is not None, mid
    _make_current(armed, letter)
    with _quiet():
        result = client.post("/respond_to_diplomatic_dialogue",
                             json={"choice": CHOICE[answer], "dialogue_id": letter["dialogue_id"]}).json()
    assert result["success"] is True, result
    return result


def _host_board(armed, names=("Ney", "Davout", "Lannes"), gold=5_000):
    _no_moments(armed)
    _quarter(armed, names)
    armed.nation_gold["France"] = int(gold)
    armed.__dict__.pop("_affairs_memo", None)


def _morning(armed, turn):
    _at(armed, turn)
    armed.__dict__.pop("_affairs_memo", None)
    with _quiet():
        return build_morning_dispatch(armed)


def _courts(armed, since=1):
    return GZ.compose_issue(armed, since)["courts"]


def _answered_log(armed, mid):
    rows = [e for e in armed.event_log if e.get("type") == "moment" and e.get("phase") == "answered"
            and e.get("moment") == mid]
    assert rows, mid
    return rows[-1]


# ═══════════════════════════════════════════════════════════════════════════
# The echo and the remark on the response
# ═══════════════════════════════════════════════════════════════════════════

class TestTheEcho:
    def test_the_minister_s_echo_is_the_response_s_second_line(self, armed, client):
        """The Haiti letter's squadron form (the boot's blockade): the response
        prices the answer on its first line and carries Decrès's echo on the
        second — the one surface the player is already reading."""
        _haiti_board(armed)
        assert _run(armed, range(1, 8)) == {7: [f"{H1}#1"]}
        result = _answer(armed, client, f"{H1}#1", "accept")
        lines = result["message"].split("\n")
        assert lines[0].startswith("The Squadron for Santo Domingo — Send five of the line:")
        assert lines[1] == "Decrès: the squadron slips out of Brest on the night tide."
        assert len(lines) == 2
        assert result["moment_answered"] == {"id": f"{H1}#1", "answer": "accept"}
        row = MO.status_row(armed, f"{H1}#1")
        assert row["echo"] == lines[1] and "remark_by" not in row

    def test_the_bill_s_decline_echoes_decres_filing_the_letter(self, armed, client):
        _haiti_board(armed)
        _run(armed, range(1, 6))
        armed.diplomatic_states[armed._make_diplo_key("France", "Britain")] = "PEACE"
        armed.invalidate_active_nations_cache()
        armed.__dict__.pop("_affairs_memo", None)
        assert _run(armed, [6, 7]) == {7: [f"{H1}#1"]}
        result = _answer(armed, client, f"{H1}#1", "decline")
        assert result["message"].split("\n")[1] == "Decrès files Ferrand's letter; the garrison of Santo Domingo holds alone."

    def test_a_refusal_carries_no_key_and_no_echo(self, armed, client):
        """A closed Accept (no administrative action left) refuses: the letter
        stands, `moment_answered` is absent, the message is the refusal."""
        _haiti_board(armed)
        _run(armed, range(1, 8))
        letter = _letter(armed, f"{H1}#1")
        _make_current(armed, letter)
        armed.admin_actions_remaining = 0
        with _quiet():
            result = client.post("/respond_to_diplomatic_dialogue",
                                 json={"choice": CHOICE["accept"], "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is False and "moment_answered" not in result
        assert "\n" not in result["message"]
        assert MO.status(armed, f"{H1}#1") == "fired"


class TestTheMarshalsRemark:
    def test_the_largest_corps_on_the_host_s_soil_speaks_by_name(self, armed, client):
        """Ney 24,000, Davout 26,000 and Lannes 18,000 on Swabia (Bavaria's):
        Davout's hen line, frozen as `remark_by`; the response's second line."""
        _host_board(armed)
        assert _run(armed, range(1, 8)) == {7: [f"{T2}#1"]}
        assert AF.largest_corps_on_host(armed, "France", "Bavaria") == "Davout"
        result = _answer(armed, client, f"{T2}#1", "decline")
        lines = result["message"].split("\n")
        # AU-2a (AUTHORITY_CURRENCY_SPEC.md §5.4): the Host's Complaint priced first
        assert lines[0] == ("The Host's Claims — Live off the land: Authority 100 → 97 — the marshals' "
                            "calm holds above 70; Bavaria's goodwill 60 → 56.")
        assert lines[1] == ("Davout: I will hang the first man who takes a hen unpaid, Sire — "
                            "but discipline does not feed a corps.")
        row = MO.status_row(armed, f"{T2}#1")
        assert row["echo"] == lines[1] and row["remark_by"] == "Davout"

    def test_the_slots_and_the_personality_fallbacks(self, armed):
        """Masséna's line carries the host; a marshal outside the seven speaks
        by personality; a retired type takes the default."""
        _host_board(armed, names=("Massena",))
        armed.marshals["Massena"].location = "Swabia"
        row = {"id": f"{T2}#1", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1, "turn": 7}
        e = MO.entry(armed, T2)
        line, who = AF.host_remark(armed, e, row)
        assert who == "Massena" and line == "Massena: Bavaria is a fat country, Sire. My men will not go hungry, nor will I."
        armed.marshals["Massena"].location = "Lorraine"
        armed.marshals["Soult"].location = "Swabia"
        line, who = AF.host_remark(armed, e, row)
        assert who == "Soult" and line.startswith("Soult: The quartermasters have their lists, Sire; Munich shall have its receipts")
        for name, personality, expected in (
                ("Ney", "cautious", AF.HOST_REMARKS["Ney"]),          # a named marshal keeps his own line
                ("Murat", "aggressive", AF.HOST_REMARKS["Murat"])):
            assert AF.HOST_REMARKS[name] == expected
        armed.marshals["Soult"].location = "Lorraine"
        # a marshal outside the seven: by personality, else the default
        stranger = armed.marshals["Ney"]
        original_name = stranger.name
        try:
            armed.marshals["Oudinot"] = stranger            # the key is what the filter reads
            stranger.name = "Oudinot"
            stranger.location = "Swabia"
            for personality, expected in (("aggressive", AF.HOST_REMARKS_BY_PERSONALITY["aggressive"]),
                                          ("literal", AF.HOST_REMARKS_BY_PERSONALITY["literal"]),
                                          ("balanced", AF.HOST_REMARK_DEFAULT)):
                stranger.personality = personality
                line, who = AF.host_remark(armed, e, row)
                assert (who, line) == ("Oudinot", f"Oudinot: {expected}"), personality
        finally:
            armed.marshals.pop("Oudinot", None)
            stranger.name = original_name
            stranger.personality = "aggressive"
            stranger.location = "Rhineland"

    def test_no_corps_left_on_the_soil_means_no_remark(self, armed, client):
        """The corps marched on between delivery and answer: the response keeps
        its one line and the row carries no `remark_by`."""
        _host_board(armed)
        _run(armed, range(1, 8))
        for name in ("Ney", "Davout", "Lannes", "Bernadotte"):
            armed.marshals[name].location = "Rhineland"
        result = _answer(armed, client, f"{T2}#1", "decline")
        assert "\n" not in result["message"]
        row = MO.status_row(armed, f"{T2}#1")
        assert row.get("echo", "") == "" and "remark_by" not in row

    def test_the_remark_table_is_within_the_echo_cap_and_names_no_nation(self):
        for line in list(AF.HOST_REMARKS.values()) + list(AF.HOST_REMARKS_BY_PERSONALITY.values()) + [AF.HOST_REMARK_DEFAULT]:
            assert len(line) <= AF.TEXT_MAX["echo"] - 12, line
            assert "Sire" in line and "?" not in line and "_" not in line
        assert set(AF.HOST_REMARKS) == {"Davout", "Massena", "Ney", "Lannes", "Murat", "Soult", "Bernadotte"}
        assert set(AF.HOST_REMARKS_BY_PERSONALITY) == {"aggressive", "cautious", "literal"}
        from backend.nation_config import EUROPE_ROSTER
        src = (REPO / "backend" / "game_logic" / "affairs.py").read_text(encoding="utf-8")
        table = src[src.index("HOST_REMARKS: Dict"):src.index("def largest_corps_on_host")]
        assert not [n for n in EUROPE_ROSTER if re.search(rf'["\']{n}["\']', table)]


# ═══════════════════════════════════════════════════════════════════════════
# The morning's receipt — both views, the next morning only
# ═══════════════════════════════════════════════════════════════════════════

class TestTheReceipt:
    def test_the_receipt_lands_the_morning_after_and_never_twice(self, armed, client):
        _host_board(armed)
        _run(armed, range(1, 8))
        _answer(armed, client, f"{T2}#1", "decline")
        assert "affair_receipt" not in _morning(armed, 7)["situation"]
        morning = _morning(armed, 8)
        assert morning["situation"]["affair_receipt"] == [
            "The army lives on the country of Bavaria; Munich keeps the account."]
        assert "affair_fate" not in morning["situation"]
        assert "affair_receipt" not in _morning(armed, 9)["situation"]

    def test_the_squadron_s_receipt_carries_its_date_and_berthier_s_accept_has_none(self, armed, client):
        _haiti_board(armed)
        _run(armed, range(1, 8))
        _answer(armed, client, f"{H1}#1", "accept")
        assert _morning(armed, 8)["situation"]["affair_receipt"] == [
            f"Five of the line are at sea for Santo Domingo; Decrès expects them home by {MO._dateline(armed, 11)}."]
        # Berthier's Accept authors no `situation` — the Staff's own line covers it
        e = MO.entry(armed, T3)
        assert "situation" not in e["accept"]
        row = {"id": f"{T3}#1", "lord": "France", "bind": {"law": "grand_quartier_general"}, "tier": 1,
               "turn": 9, "status": "answered", "answer": "accept", "answered_turn": 9}
        armed.moments["state"][f"{T3}#1"] = row
        _at(armed, 10)
        assert AF.receipt_lines(armed) == []

    def test_a_lapse_prints_no_receipt_the_lapsed_envoys_line_is_its_record(self, armed):
        _host_board(armed)
        _run(armed, range(1, 8))
        letter = _letter(armed, f"{T2}#1")
        _at(armed, 8)
        key = MO.lapse_default(armed, letter)
        assert key["moment"]["line"].startswith("The Host's Claims was left unanswered — Live off the land")
        row = MO.status_row(armed, f"{T2}#1")
        assert row["status"] == "lapsed" and row["answer"] == "decline"
        _at(armed, 9)
        armed.__dict__.pop("_affairs_memo", None)
        assert AF.receipt_lines(armed) == []

    def test_both_views_print_the_key_plain_before_the_fate(self):
        """The two-view pin (the laws' idiom): the terminal's morning dispatch
        and the Dispatch screen read `affair_receipt` in `COLOR_INFO`, after
        the Staff's line and before the amber fate."""
        for name, fn in (("main.gd", "_display_morning_dispatch"), ("dispatch_view.gd", "_on_dispatch_received")):
            body = _func(_gd(name), fn)
            assert 'situation.get("affair_receipt", null)' in body, name
            assert body.index('situation.get("staff_arrived", null)') < body.index('situation.get("affair_receipt", null)') \
                < body.index('situation.get("affair_fate", null)'), name
            arm = body[body.index('situation.get("affair_receipt", null)'):body.index('situation.get("affair_fate", null)')]
            assert "Utils.COLOR_INFO" in arm and "COLOR_WARNING" not in arm, name
            assert "THE SQUADRON" not in arm and ']  " + str(receipt_line)' in arm, name

    def test_the_build_is_a_pure_read(self, armed, client):
        _host_board(armed)
        _run(armed, range(1, 8))
        _answer(armed, client, f"{T2}#1", "decline")
        _at(armed, 8)
        armed.__dict__.pop("_affairs_memo", None)
        before = json.dumps(armed.to_dict(), sort_keys=True)
        lines = AF.receipt_lines(armed)
        assert lines and json.dumps(armed.to_dict(), sort_keys=True) == before


# ═══════════════════════════════════════════════════════════════════════════
# THE COURTS — the Moniteur's line, once, and never for an arrival
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCourts:
    def test_the_answered_press_prints_once_and_the_arrival_never(self, armed, client):
        _host_board(armed)
        _run(armed, range(1, 8))
        before = _courts(armed)
        assert not any("Host's Claims" in ln or "MUNICH" in ln for ln in before), before
        _answer(armed, client, f"{T2}#1", "decline")
        after = _courts(armed)
        assert after.count("MUNICH — The Grand Army is quartered upon the country of Bavaria.") == 1
        assert not any("laid before the Emperor" in ln or "the Emperor answers" in ln for ln in after), after
        assert _answered_log(armed, f"{T2}#1")["press"] == "MUNICH — The Grand Army is quartered upon the country of Bavaria."

    def test_not_now_prints_nothing_and_the_squadron_waits_for_its_fate(self, armed, client):
        # Berthier's door: at war four turns with the chest above the Staff's bar
        _no_moments(armed)
        armed.nation_gold["France"] = 20_000
        armed.__dict__.pop("_affairs_memo", None)
        delivered = _run(armed, range(1, 12))
        assert any(f"{T3}#1" in ids for ids in delivered.values()), delivered
        _answer(armed, client, f"{T3}#1", "decline")
        assert "press" not in _answered_log(armed, f"{T3}#1")
        assert not any("Berthier" in ln or "HEADQUARTERS" in ln for ln in _courts(armed))

    def test_the_squadron_s_outcome_prints_the_paper_s_line_home_or_the_moniteur_s_lie(self, armed, client):
        _haiti_board(armed)
        _run(armed, range(1, 8))
        _answer(armed, client, f"{H1}#1", "accept")
        assert "press" not in _answered_log(armed, f"{H1}#1")
        assert not any("SANTO DOMINGO" in ln or "SAN DOMINGO" in ln for ln in _courts(armed))
        for turn in range(8, 12):
            _at(armed, turn)
            naval._squadron_tick(armed)
        AF.settle_squadrons(armed)
        row = MO.status_row(armed, f"{H1}#1")
        courts = _courts(armed, since=8)
        expected = ("SANTO DOMINGO — The Emperor's squadron is home; the garrison is relieved."
                    if row["outcome"] == "home"
                    else "SAN DOMINGO — Our squadron sustained the honour of the flag against a superior enemy.")
        assert courts.count(expected) == 1, courts
        assert not any(ln.startswith("The Squadron for Santo Domingo") for ln in courts), courts

    def test_a_moment_s_rows_and_the_one_liner_are_as_before(self, armed):
        from backend import campaign_log as CL
        base = {"type": "moment", "nation": "France", "title": "The Host's Claims", "register": "affair"}
        assert GZ._affair_courts_line({**base, "phase": "arrived"}) == ""
        assert GZ._affair_courts_line({**base, "phase": "withdrawn", "line": "set aside"}) == ""
        assert GZ._affair_courts_line({**base, "phase": "answered", "press": "MUNICH — the line"}) == "MUNICH — the line"
        assert GZ._affair_courts_line({**base, "phase": "answered"}) == ""
        assert GZ._affair_courts_line({**base, "phase": "outcome", "press": "SAN DOMINGO — the lie"}) == "SAN DOMINGO — the lie"
        moment = {"type": "moment", "phase": "answered", "nation": "France", "title": "The Bavarian Match",
                  "caption": "Seal the match"}
        assert GZ._affair_courts_line(moment) is None
        assert CL.format_event_oneliner(moment) == "The Bavarian Match — the Emperor answers: Seal the match"
        assert GZ._affair_courts_line({"type": "battle"}) is None


# ═══════════════════════════════════════════════════════════════════════════
# The remember line — the next letter of the same template and subject
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRememberLine:
    def test_the_second_letter_from_the_same_host_remembers_the_first(self, armed, client):
        _host_board(armed)
        _run(armed, range(1, 8))
        _answer(armed, client, f"{T2}#1", "decline")
        e = MO.entry(armed, T2)
        first = MO.status_row(armed, f"{T2}#1")
        assert AF.remember_line(armed, e, dict(first, id=f"{T2}#1")) == ""        # a first letter remembers nothing
        second = {"id": f"{T2}#2", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1, "turn": 17, "status": "fired"}
        armed.moments["state"][f"{T2}#2"] = second
        month = MO._dateline(armed, 7)
        assert AF.remember_line(armed, e, second) == f"In {month} the army lived on the country of Bavaria; its court writes again."
        assert AF.board_lines(armed, e, second)[-1] == f"In {month} the army lived on the country of Bavaria; its court writes again."
        # another host's letter remembers nothing of Bavaria's
        other = {"id": f"{T2}#3", "lord": "France", "bind": {"host": "KingdomOfItaly"}, "tier": 1, "turn": 18, "status": "fired"}
        armed.moments["state"][f"{T2}#3"] = other
        assert AF.remember_line(armed, e, other) == ""

    def test_the_arch_chancellor_remembers_an_answer_and_a_lapse(self, armed):
        e = MO.entry(armed, T1)
        state = armed.moments["state"]
        state[f"{T1}#1"] = {"id": f"{T1}#1", "lord": "France", "bind": {"region": "Swabia"}, "tier": 1, "turn": 7,
                            "status": "lapsed", "answer": "decline", "lapsed_turn": 8}
        second = {"id": f"{T1}#2", "lord": "France", "bind": {"region": "Swabia"}, "tier": 1, "turn": 17, "status": "fired"}
        state[f"{T1}#2"] = second
        assert AF.remember_line(armed, e, second) == f"In {MO._dateline(armed, 8)} you let the Council act; Cambacérès writes again."
        state[f"{T1}#2"].update({"status": "answered", "answer": "accept", "answered_turn": 17})
        third = {"id": f"{T1}#3", "lord": "France", "bind": {"region": "Swabia"}, "tier": 1, "turn": 27, "status": "fired"}
        state[f"{T1}#3"] = third
        assert AF.remember_line(armed, e, third) == f"In {MO._dateline(armed, 17)} you dictated from the field; Cambacérès writes again."

    def test_the_remember_line_is_the_board_s_last_line_in_the_letter_payload(self, armed, client):
        _host_board(armed)
        _run(armed, range(1, 8))
        _answer(armed, client, f"{T2}#1", "decline")
        # the second Host's letter from Bavaria, after the cooldown of ten — the
        # row crafted as `_deliver` freezes it (the engine's own second arrival
        # would wait on the pulse behind the Haiti letter on this board)
        second = {"id": f"{T2}#2", "lord": "France", "bind": {"host": "Bavaria"}, "tier": 1, "turn": 17,
                  "status": "fired"}
        armed.moments["state"][f"{T2}#2"] = second
        _at(armed, 17)
        armed.__dict__.pop("_affairs_memo", None)
        payload = MO.letter_payload(armed, MO.entry(armed, T2), 17, 18, second)
        assert payload["board"][-1] == f"In {MO._dateline(armed, 7)} the army lived on the country of Bavaria; its court writes again."
        assert len(payload["board"][-1]) <= AF.TEXT_MAX["remember"]


# ═══════════════════════════════════════════════════════════════════════════
# The budget — the noise census, the alarm, the copy
# ═══════════════════════════════════════════════════════════════════════════

class TestTheBudget:
    def test_two_lines_in_the_response_one_receipt_one_courts_line_nothing_else(self, armed, client):
        _host_board(armed)
        _run(armed, range(1, 8))
        alarm_before = dict(getattr(armed, "threat_by_target", {}) or {})
        result = _answer(armed, client, f"{T2}#1", "decline")
        assert len(result["message"].split("\n")) == 2
        assert dict(getattr(armed, "threat_by_target", {}) or {}) == alarm_before
        receipts = _morning(armed, 8)["situation"].get("affair_receipt", [])
        assert len(receipts) == 1
        assert _morning(armed, 9)["situation"].get("affair_receipt") is None
        assert sum(1 for ln in _courts(armed) if "Bavaria" in ln) == 1

    def test_the_answer_road_adds_no_popup_sound_or_notice(self):
        src = (REPO / "backend" / "game_logic" / "moments.py").read_text(encoding="utf-8")
        body = _func_py(src, "answer")
        for forbidden in ("queue_dispatch_event", "add_notification", "incoming_proposal_popup", "play("):
            assert forbidden not in body, forbidden
        aff = (REPO / "backend" / "game_logic" / "affairs.py").read_text(encoding="utf-8")
        tail = aff[aff.index("RE-R — the reactions"):]
        for forbidden in ("queue_dispatch_event", "add_notification", "log_event", "world.notifications"):
            assert forbidden not in tail, forbidden

    def test_every_reaction_line_fills_on_every_host(self, armed):
        """The copy with its slots over each court the Host's Claims can bind:
        no brace, no question mark, within the caps."""
        e = MO.entry(armed, T2)
        for host in ("Bavaria", "KingdomOfItaly", "Prussia", "Saxony"):
            row = {"id": f"{T2}#1", "lord": "France", "bind": {"host": host}, "tier": 1, "turn": 7,
                   "answer": "decline", "status": "answered", "answered_turn": 7}
            for text in (AF.press_of(armed, e, row, "decline"), AF.press_of(armed, e, row, "accept"),
                         AF.fill_slots(armed, e["decline"]["situation"], row, e),
                         AF.fill_slots(armed, e["accept"]["remember"], row, e)):
                assert text and "{" not in text and "}" not in text and "?" not in text, (host, text)
                assert len(text) <= 160, (host, text)
            for line in AF.HOST_REMARKS.values():
                filled = AF.fill_slots(armed, line, row, e)
                assert "{" not in filled and "?" not in filled, (host, filled)

    def test_the_fixture_and_the_scenario_stay_in_lockstep(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["affairs"]
        shipped = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]["affairs"]
        assert fixture == shipped


def _func_py(src: str, name: str) -> str:
    start = src.index(f"\ndef {name}(")
    nxt = src.find("\ndef ", start + 1)
    return src[start:nxt if nxt > 0 else len(src)]


# ═══════════════════════════════════════════════════════════════════════════
# The frame (IQ-10) and the readability record
# ═══════════════════════════════════════════════════════════════════════════

FRAME_DATE = "2026_11_02"
AUDITS = REPO / "docs" / "audits"


class TestTheFrame:
    def test_the_receipt_shot_is_registered_and_captured(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("iq10_run_captures", REPO / "tools" / "iq10_run_captures.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        row = {s["id"]: s for s in mod.SHOTS}["dispatch_affair_receipt"]
        assert row["scene"] == "res://scenes/dispatch_view.tscn" and row["api_method"] == "get_dispatch"
        assert row["steps"][0]["scroll_to"] == {"text": "SITUATION"}
        for needle in ("The army lives on the country of Bavaria; Munich keeps the account.", "no prefix", "no amber"):
            assert needle in row["must_show"], needle
        cap = (REPO / "tools" / "iq10_capture_payloads.py").read_text(encoding="utf-8")
        assert 'record("dispatch_affair_receipt"' in cap

    def test_the_frames_are_committed_at_both_scales_and_named_in_the_plan(self):
        for tail in ("", "_X2"):
            png = AUDITS / f"IQ10_DISPATCH_AFFAIR_RECEIPT{tail}_{FRAME_DATE}.png"
            assert png.exists() and png.stat().st_size > 8000, png
        plan = (REPO / "docs" / "UX_UI_REVIEW_PLAN.md").read_text(encoding="utf-8")
        assert "IQ10_DISPATCH_AFFAIR_RECEIPT" in plan

    def test_the_record_covers_the_receipt_at_every_resolution_with_no_red(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        from uxr0_readability_report import PHYSICAL_RESOLUTIONS, totals
        record = json.loads((AUDITS / "uxr0" / f"readability_reactions_{FRAME_DATE}.json").read_text(encoding="utf-8"))
        surf = record["surfaces"]["dispatch_affair_receipt"]
        keys = set(surf["readings"])
        for (w, h) in PHYSICAL_RESOLUTIONS:
            assert any(k.startswith(f"{w}x{h}@") for k in keys), (w, h, keys)
        for key, r in surf["readings"].items():
            assert r["ok"] and r["counts"]["rows"] > 0 and r["counts"]["red"] == 0 and r["counts"]["p1"] == 0, (key, r)
        t = totals(record)
        assert t["red"] == 0 and t["p1"] == 0, t
