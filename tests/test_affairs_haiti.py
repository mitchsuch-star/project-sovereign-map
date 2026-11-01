"""RE-H — "Affairs of State": the Haiti letter (`docs/RECURRING_EVENTS_SPEC.md`
§6.5, §16 "RE-H", §16b; the user's word of November 1, 2026 — "conditions
that make them appear"; the landing record §22).

H0 — the bill alone (the first landing, tier 1 "the letter" closes with it):
the premise `colony_cut_off` clause by clause on crafted boots (the latch of
four blockaded mornings in twelve, the Emperor at home, 25 sail in port, the
purse above the Marine's bar); `bites: "floor"` — the floor half alone, so the
letter arrives at full standing and the Decline is a dent there, a wound
across the aura's line (§0b P16 amended); the arrival on the pulse's first
morning; the frozen row; the Decline grip-floored and never a rise; the lapse
as the Decline; both answers through the endpoint; the dress keys (the
monogram "D", the writer and the office, the exhibit under its own run-in, the
chapter by arrival and by the last squadron's fate, the slot by the issued
turn); the closing lines authored for the Correspondence (RE-C); the alarm
untouched; the validator's refusals; and RE3-8 — the driver answers the
objection it can afford.

Every pin arms the real booted world with the staged fixture
`tests/fixtures/affairs_block.json`, as `tests/test_affairs_engine.py` does.
"""
import json
import re

import pytest

import backend.main as M
from backend.game_logic import affairs as AF
from backend.game_logic import moments as MO
from backend.game_logic import naval
from backend.models.authority import AURA_GRIP_FULL, get_imperial_grip
from tests.test_affairs_engine import (  # noqa: F401 — the fixtures ride the import
    FIXTURE, SCENARIO, T1, _aff, _at, _bad, _block, _letter, _make_current, _moment_rows,
    _no_moments, _quiet, _restore_active_world, _run, _tick, armed, client, world,
)
from tests.test_first_open import _TYPED

H1 = "santo_domingo"
HOME = "Lorraine"             # Napoleon's seat at the 1805 boot (the sovereign holds court here)


def _haiti_board(w, gold=5_000, authority=100):
    """The board §6.5 writes for: the Emperor at home (the boot), France
    blockaded by Britain from the opening (the boot), 45 sail in port, the
    chest above the Marine's bar but under the Staff's (so Berthier's door
    stays out of the morning), the standing as given."""
    _no_moments(w)
    w.nation_gold["France"] = int(gold)
    w.authority_tracker.authority = int(authority)
    w.__dict__.pop("_affairs_memo", None)


def _read(w):
    w.__dict__.pop("_affairs_memo", None)
    return AF.premise_holds(w, MO.entry(w, H1), "France")


def _occ(n=1, turn=7, **extra):
    row = {"id": f"{H1}#{n}", "lord": "France", "bind": {"region": HOME, "sovereign": "Napoleon"},
           "tier": 1, "turn": int(turn)}
    row.update(extra)
    return row


# ═══════════════════════════════════════════════════════════════════════════
# RE3-8 — the driver answers the objection it can afford
# ═══════════════════════════════════════════════════════════════════════════

class _Transport:
    def __init__(self):
        self.posts = []

    def post(self, path, body):
        self.posts.append((path, dict(body)))
        return {"success": True}

    def get(self, path):
        return {}


class _Digest:
    def __init__(self):
        self.notes, self.popups, self.recent = [], [], []

    def popup(self, key, summary, choice):
        self.popups.append((key, choice))

    def note(self, text):
        self.notes.append(text)

    def __getattr__(self, name):
        return lambda *a, **k: None


class TestRE3_8TheDriverAnswersWhatItCanAfford:
    def _answerer(self, policy):
        from tools import playtest_driver as D
        t, d = _Transport(), _Digest()
        return D.Answerer(t, d, dict(D.POLICY_DEFAULTS) | policy, False), t, d

    def _objection(self, **extra):
        response = {"success": False, "pending_objection": {"marshal": "Lannes", "message": "Lannes objects",
                                                            "choices": ["trust", "insist"]}}
        response.update(extra)
        return response

    def test_a_plain_objection_takes_the_policy_s_answer(self):
        answerer, t, d = self._answerer({"objection": "insist"})
        answerer.begin_post()
        answerer.scan(self._objection())
        assert t.posts == [("/respond_to_objection", {"choice": "insist"})]
        assert d.notes == []

    def test_an_unpayable_insist_falls_back_to_the_first_open_road(self):
        """VP1-CS austerlitz stopped at T4: Lannes's fortify from NEUTRAL costs
        two actions with one left; the backend refused the insist with the
        objection kept and the roads still open (`objection_kept`,
        `choices`), and the driver re-posted `insist` into the cycle guard.
        It now answers the first open road — trust — and says so."""
        answerer, t, d = self._answerer({"objection": "insist"})
        answerer.begin_post()
        answerer.scan(self._objection(objection_kept=True, choices=["trust", "cancel"]))
        assert t.posts == [("/respond_to_objection", {"choice": "trust"})]
        assert d.popups == [("objection", "trust")]
        assert len(d.notes) == 1 and "RE3-8" in d.notes[0] and "'insist' cannot be paid" in d.notes[0]

    def test_the_fallback_prefers_trust_then_compromise_then_cancel(self):
        answerer, t, _d = self._answerer({"objection": "insist"})
        answerer.begin_post()
        answerer.scan(self._objection(objection_kept=True, choices=["compromise", "cancel"]))
        answerer.scan(self._objection(objection_kept=True, choices=["cancel"]))
        assert [b["choice"] for _p, b in t.posts] == ["compromise", "cancel"]

    def test_the_refusal_s_reply_is_answered_without_a_pending_objection_key(self):
        """The reply to `/respond_to_objection` carries the refusal's own keys
        and NO `pending_objection` (that key rides the /command road alone) —
        the shape that stopped VP1-CS austerlitz at T4 on both the armed arm
        and the control even after the first fix."""
        answerer, t, d = self._answerer({"objection": "insist"})
        answerer.begin_post()
        answerer.scan({"success": False, "objection_kept": True, "choices": ["trust", "cancel"],
                       "message": "Not enough actions! Need 2, have 1 — Lannes's objection stands — reply 'trust' or 'cancel'."})
        assert t.posts == [("/respond_to_objection", {"choice": "trust"})]
        assert len(d.notes) == 1 and "RE3-8" in d.notes[0]

    def test_an_affordable_answer_is_never_overridden(self):
        """The refusal names the roads still open; a policy whose answer is
        among them (a refused `trust` with `trust` open cannot happen, but a
        `compromise` policy with compromise open) keeps its own word."""
        answerer, t, _d = self._answerer({"objection": "compromise"})
        answerer.begin_post()
        answerer.scan(self._objection(objection_kept=True, choices=["trust", "compromise", "cancel"]))
        assert t.posts == [("/respond_to_objection", {"choice": "compromise"})]

    def test_the_reply_carries_the_refusal_s_own_keys(self):
        """`_respond_to_objection_sync` copies `objection_kept` and `choices`
        from the executor's refusal onto the reply (shown = offered)."""
        src = (M.__file__ and open(M.__file__, encoding="utf-8").read())
        assert '_copy_truthy_result_fields(response, result, ("objection_kept", "choices"))' in src


# ═══════════════════════════════════════════════════════════════════════════
# The premise — clause by clause (§6.5; Rule 8)
# ═══════════════════════════════════════════════════════════════════════════

class TestThePremise:
    def test_the_shipped_deck_carries_the_letter_as_authored(self, armed):
        e = MO.entry(armed, H1)
        assert e["shape"] == "bill" and e["title"] == "The Relief of Santo Domingo"
        assert e["when"] == {"predicate": "colony_cut_off", "min_ships": 25, "min_purse": 500}
        assert e["latch"] == {"of": 12, "at_least": 4} and e["streak"] == 1
        assert e["bites"] == AF.BITES_FLOOR and e["cooldown"] == 12 and e["cap"] == 2
        assert e["ends"] == {"date": "1808-11-07", "turn": 76}
        assert e["voice"] == {"speaker": "named", "name": "Decrès, Minister of Marine and the Colonies"}
        assert "forms" not in e                      # H0: the bill alone (the squadron is the second landing)

    def test_the_boot_reads_the_latch_but_not_the_purse(self, armed):
        """The 1805 boot: Britain blockades France from the opening, the Emperor
        holds court at Lorraine, 45 sail in port — and the chest holds 800,
        under the Marine's bar (500 + the AI's reserve of 1,000)."""
        _no_moments(armed)
        read = _read(armed)
        assert read["latch"] is True and read["holds"] is False
        assert naval.is_blockaded(armed, "France") and naval.trade_dominance_nation(armed) == "Britain"

    def test_the_purse_bar_is_five_hundred_plus_the_reserve(self, armed):
        _haiti_board(armed, gold=1_499)
        assert _read(armed)["holds"] is False
        _haiti_board(armed, gold=1_500)
        read = _read(armed)
        assert read["holds"] is True and read["bind"] == {"region": HOME, "sovereign": "Napoleon"}
        assert read["measure"] is None and read["latch"] is True

    def test_the_emperor_afield_or_captive_silences_the_marine(self, armed):
        """Afield the Arch-Chancellor writes instead — T1 and H1 never compete."""
        _haiti_board(armed)
        armed.marshals["Napoleon"].location = "Swabia"
        assert _read(armed)["holds"] is False and _read(armed)["latch"] is True
        armed.marshals["Napoleon"].location = HOME
        armed.marshals["Napoleon"].captured_by = "Austria"
        assert _read(armed)["holds"] is False
        armed.marshals["Napoleon"].captured_by = ""
        assert _read(armed)["holds"] is True

    def test_twenty_four_sail_are_not_enough(self, armed):
        _haiti_board(armed)
        naval.get_fleet(armed, "France")["ships"] = 24
        assert _read(armed)["holds"] is False
        naval.get_fleet(armed, "France")["ships"] = 25
        assert _read(armed)["holds"] is True

    def test_peace_with_the_hunter_drops_the_latch_bit_not_the_rest(self, armed):
        _haiti_board(armed)
        armed.diplomatic_states[armed._make_diplo_key("France", "Britain")] = "PEACE"
        armed.invalidate_active_nations_cache()
        read = _read(armed)
        assert read["latch"] is False and read["holds"] is True

    def test_no_region_scan_and_no_nation_literal_in_the_predicate(self):
        src = open(AF.__file__, encoding="utf-8").read()
        start = src.index("def _colony_cut_off(")
        body = src[start:src.index("\nPREDICATES", start)]
        assert ".regions.values()" not in body and ".regions.items()" not in body
        for literal in ("Britain", "France", "Haiti", "Santo Domingo"):
            assert f'"{literal}"' not in body


# ═══════════════════════════════════════════════════════════════════════════
# The latch, the pulse and the arrival (§7, P7)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheLatchAndTheArrival:
    def test_the_mask_shifts_every_morning_and_the_watch_counts_it(self, armed):
        _haiti_board(armed)
        e = MO.entry(armed, H1)
        for turn in range(1, 7):
            _at(armed, turn)
            _tick(armed)
            assert AF.latch_count(armed, e) == turn
            assert AF.latch_ok(armed, e) is (turn >= 4)
            assert AF.watch(armed) == [f"Blockaded {turn} of the last 12 mornings, the Emperor at home — "
                                       f"Decrès may write of Santo Domingo."]
        assert AF.runtime(armed)["masks"][H1] == 0b111111

    def test_the_letter_arrives_on_the_pulse_s_first_morning_at_full_standing(self, armed):
        """The user's word: the letter APPEARS. At standing 100 (every scripted
        board) `bites: "floor"` lets it through — the pulse's first morning,
        T7, with the latch full since T4; the row frozen with the Emperor's
        seat; no `form` (H0 authors none)."""
        _haiti_board(armed, authority=100)
        delivered = _run(armed, range(1, 8))
        assert delivered == {7: [f"{H1}#1"]}
        row = MO.status_row(armed, f"{H1}#1")
        assert row == {"status": "fired", "turn": 7, "id": f"{H1}#1", "lord": "France",
                       "bind": {"region": HOME, "sovereign": "Napoleon"}, "tier": 1}
        assert AF.watch(armed) == []                       # silent while the letter stands
        letter = _letter(armed, f"{H1}#1")
        assert letter is not None and MO.is_quiet_letter(letter)

    def test_the_latch_needs_four_of_twelve_so_a_short_blockade_never_writes(self, armed):
        _haiti_board(armed)
        armed.diplomatic_states[armed._make_diplo_key("France", "Britain")] = "PEACE"
        armed.invalidate_active_nations_cache()
        assert _run(armed, range(1, 12)) == {}
        e = MO.entry(armed, H1)
        assert AF.latch_count(armed, e) == 0 and AF.candidates(armed, 11) == []

    def test_the_file_closes_at_ferrand_s_death(self, armed):
        """`ends` T76 (7 November 1808): no candidate and no Watch line after it."""
        _haiti_board(armed)
        _run(armed, range(1, 6))
        e = MO.entry(armed, H1)
        _at(armed, 76)
        AF.update_morning(armed)
        assert [c["e"]["id"] for c in AF.candidates(armed, 76)] == [H1]
        _at(armed, 77)
        AF.update_morning(armed)
        assert AF.candidates(armed, 77) == [] and AF.watch(armed) == []

    def test_the_cooldown_and_the_cap_space_the_letters(self, armed):
        """Twice an act, twelve turns apart: against repetition (the user's word)."""
        _haiti_board(armed)
        e = MO.entry(armed, H1)
        delivered = _run(armed, range(1, 8))
        assert delivered == {7: [f"{H1}#1"]}
        _at(armed, 8)
        MO.lapse_default(armed, _letter(armed, f"{H1}#1"))
        armed.dialogue_manager.remove_matching(MO.is_moment_letter)
        armed.__dict__.pop("_affairs_memo", None)
        assert AF.on_cooldown(armed, e, "", 18) and not AF.on_cooldown(armed, e, "", 19)
        assert AF.under_cap(armed, e, "", 19)


# ═══════════════════════════════════════════════════════════════════════════
# `bites: "floor"` — the user's amendment to P16 (November 1, 2026)
# ═══════════════════════════════════════════════════════════════════════════

class TestBitesOnTheFloorHalf:
    @pytest.mark.parametrize("authority", [100, 95, 88, 85, 80, 74])
    def test_the_letter_bites_wherever_the_three_can_be_paid_whole(self, armed, authority):
        _haiti_board(armed, authority=authority)
        assert AF.bites(armed, "France", MO.entry(armed, H1), 1) is True

    @pytest.mark.parametrize("authority", [73, 72, 71, 60])
    def test_the_floor_half_still_silences_it(self, armed, authority):
        _haiti_board(armed, authority=authority)
        assert get_imperial_grip(armed, "France") - 3 < MO.AUTHORITY_GRIP_FLOOR
        assert AF.bites(armed, "France", MO.entry(armed, H1), 1) is False

    def test_the_arch_chancellor_s_both_halves_are_untouched(self, armed):
        _no_moments(armed)
        armed.marshals["Napoleon"].location = "Swabia"
        e = MO.entry(armed, T1)
        assert e["bites"] is True
        for authority, expected in ((100, False), (85, True), (72, False)):
            armed.authority_tracker.authority = authority
            armed.__dict__.pop("_affairs_memo", None)
            assert AF.bites(armed, "France", e, 1) is expected, authority
        assert AF.BITES_MODES == (True, "floor") and AURA_GRIP_FULL == 85


# ═══════════════════════════════════════════════════════════════════════════
# The answers — shown = applied, the lapse, the alarm
# ═══════════════════════════════════════════════════════════════════════════

class TestTheAnswers:
    def _arrive(self, armed, authority=100, gold=5_000):
        _haiti_board(armed, gold=gold, authority=authority)
        assert _run(armed, range(1, 8)) == {7: [f"{H1}#1"]}
        letter = _letter(armed, f"{H1}#1")
        _make_current(armed, letter)
        return letter

    def test_the_accept_applies_its_quote_through_the_endpoint(self, armed, client):
        letter = self._arrive(armed)
        armed.admin_actions_remaining = 2
        payload = MO.refresh_letter(armed, letter)
        assert payload["button_accept"] == "−600 gold · 1 action"
        with _quiet():
            result = client.post("/respond_to_diplomatic_dialogue",
                                 json={"choice": "accept_ai_proposal", "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is True, result
        assert armed.nation_gold["France"] == 5_000 - 600 and armed.admin_actions_remaining == 1
        assert armed.authority_tracker.authority == 100
        row = MO.status_row(armed, f"{H1}#1")
        assert row["status"] == "answered" and row["answer"] == "accept"
        assert row["receipt"] == "−600 gold · 1 action"
        assert row["echo"] == "Decrès: two frigates clear Brest with flour and muskets for Santo Domingo."
        assert _letter(armed, f"{H1}#1") is None
        assert [e["phase"] for e in _moment_rows(armed)] == ["arrived", "answered"]
        assert _moment_rows(armed)[-1]["register"] == "affair"

    def test_the_decline_costs_three_of_standing_and_no_purse(self, armed, client):
        letter = self._arrive(armed, authority=100)
        gold, admin = armed.nation_gold["France"], armed.admin_actions_remaining
        payload = MO.refresh_letter(armed, letter)
        assert payload["button_decline"] == "standing 100 → 97"
        with _quiet():
            result = client.post("/respond_to_diplomatic_dialogue",
                                 json={"choice": "reject_ai_proposal", "dialogue_id": letter["dialogue_id"]}).json()
        assert result["success"] is True, result
        assert armed.authority_tracker.authority == 97
        assert armed.nation_gold["France"] == gold and armed.admin_actions_remaining == admin
        row = MO.status_row(armed, f"{H1}#1")
        assert row["answer"] == "decline" and row["receipt"] == "standing 100 → 97"
        assert row["echo"] == "Decrès files Ferrand's letter; the garrison of Santo Domingo holds alone."

    def test_the_decline_is_grip_floored_and_never_a_rise(self, armed):
        letter = self._arrive(armed, authority=74)
        p = MO.plan(armed, MO.entry(armed, H1), MO.ANSWER_DECLINE, MO.status_row(armed, f"{H1}#1"))
        row = next(r for r in p["rows"] if r["op"] == "authority")
        assert row["loss"] == 3 and row["after"] == 71
        with _quiet():
            MO._apply(armed, p)
        assert armed.authority_tracker.authority == 71
        assert letter is not None

    def test_the_lapse_is_the_decline(self, armed):
        letter = self._arrive(armed, authority=100)
        _at(armed, 8)
        out = MO.lapse_default(armed, letter)
        assert out["moment"]["id"] == f"{H1}#1"
        assert "Ferrand must hold alone" in out["moment"]["line"]
        assert armed.authority_tracker.authority == 97
        row = MO.status_row(armed, f"{H1}#1")
        assert row["status"] == "lapsed" and row["receipt"] == "standing 100 → 97"

    def test_the_accept_closes_with_no_action_left_and_the_letter_stands(self, armed):
        letter = self._arrive(armed)
        armed.admin_actions_remaining = 0
        payload = MO.refresh_letter(armed, letter)
        accept = next(o for o in payload["options"] if o["action"] == "accept_ai_proposal")
        assert accept.get("enabled") is False and "administration is spoken for" in str(accept.get("reason") or "")
        with _quiet():
            result = MO.answer(armed, letter, MO.ANSWER_ACCEPT)
        assert result["success"] is False and result.get("moment_stands") is True
        assert MO.status(armed, f"{H1}#1") == "fired"

    def test_no_answer_touches_the_alarm(self, armed):
        self._arrive(armed)
        e, row = MO.entry(armed, H1), MO.status_row(armed, f"{H1}#1")
        before = (dict(getattr(armed, "threat_by_target", {}) or {}),
                  dict(getattr(armed, "threat_sources_this_turn", {}) or {}))
        for answer in (MO.ANSWER_ACCEPT, MO.ANSWER_DECLINE):
            p = MO.plan(armed, e, answer, row)
            assert "alarm" not in {r.get("op") for r in p["rows"]}
            with _quiet():
                MO._apply(armed, p)
        after = (dict(getattr(armed, "threat_by_target", {}) or {}),
                 dict(getattr(armed, "threat_sources_this_turn", {}) or {}))
        assert after == before


# ═══════════════════════════════════════════════════════════════════════════
# The copy and the dress (§6.5, §12b.2, P1, P18)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCopyAndTheDress:
    def test_every_line_is_inside_its_cap_and_teaches_no_typed_order(self, armed):
        e = MO.entry(armed, H1)
        texts = [("record", e["record"]), ("line", e["line"]), ("watch", e["watch"]),
                 ("counsel", e["counsel"]), ("exhibit_from", e["exhibit_from"])]
        texts += [("variant", v["text"]) for v in e["variants"]]
        texts += [("exhibit", x) for x in e["exhibit"]]
        texts += [("closing", x) for x in e["closing"]]
        for side in ("accept", "decline"):
            for key in ("caption", "echo", "press", "remember", "situation"):
                texts.append((key, e[side][key]))
            texts.append(("button_line", re.sub(r"\{[a-z_]+\}", "####", e[side]["button_line"])))
        for key, text in texts:
            assert text and len(text) <= AF.TEXT_MAX[key], (key, len(text), text)
            assert not _TYPED.search(text), (key, text)
        assert len(e["variants"]) == 4 == AF.VARIANTS_MAX and len(e["exhibit"]) == 2 and len(e["closing"]) == 2
        assert e["watch"].count("may") == 1 and "will" not in e["watch"]

    def test_the_chapter_by_arrival_and_by_the_last_squadron_s_fate(self, armed):
        e = MO.entry(armed, H1)
        assert AF.chapter_of(e, _occ(1)).startswith("Historically Haiti killed the French who stayed in 1804")
        assert AF.chapter_of(e, _occ(2, turn=19)).startswith("Historically Ferrand could buy twenty days' bread")
        assert AF.chapter_of(e, _occ(2, turn=19, last_fate="home")).startswith("Historically Missiessy's squadron")
        assert AF.chapter_of(e, _occ(3, turn=31, last_fate="caught")).startswith("Historically Leissègues landed")
        assert [(v["key"], v["value"]) for v in e["variants"]] == [
            ("last_fate", "home"), ("last_fate", "caught"), ("arrival", "first"), ("arrival", "later")]

    def test_the_exhibits_alternate_by_arrival_under_their_own_run_in(self, armed):
        e = MO.entry(armed, H1)
        first, second = e["exhibit"]
        assert AF.exhibit_of(e, _occ(1)) == first and AF.exhibit_of(e, _occ(2)) == second
        assert AF.exhibit_of(e, _occ(3)) == first
        assert first.startswith("‘Slavery is forever abolished.’") and "Boisrond-Tonnerre" in second
        assert second.startswith("‘Nous avons osé être libres") and second.endswith("draft.")
        assert e["exhibit_from"] == "FROM HAITI —"
        # the engine holds no literal for the run-in — the deck's word alone
        src = open(AF.__file__, encoding="utf-8").read()
        assert "FROM HAITI" not in src

    def test_the_slot_says_last_february_until_the_autumn_of_1806(self, armed):
        e = MO.entry(armed, H1)
        assert AF.authored_slots(e, 7) == {"wrote": "last February"}
        assert AF.authored_slots(e, 26) == {"wrote": "last February"}
        assert AF.authored_slots(e, 27) == {"wrote": "two years ago"}
        assert AF.fill_slots(armed, e["line"], _occ(1, turn=7), e).startswith("Sire, Ferrand wrote last February")
        assert AF.fill_slots(armed, e["line"], _occ(2, turn=30), e).startswith("Sire, Ferrand wrote two years ago")
        assert "{" not in AF.fill_slots(armed, e["line"], _occ(1, turn=7), e)

    def test_the_payload_wears_the_dress_in_the_affairs_register(self, armed):
        _haiti_board(armed)
        assert _run(armed, range(1, 8)) == {7: [f"{H1}#1"]}
        letter = _letter(armed, f"{H1}#1")
        payload = MO.refresh_letter(armed, letter)
        assert payload["register"] == "affair" and payload["header"] == "AN AFFAIR OF STATE — LATE DECEMBER 1805"
        assert payload["title"] == "The Relief of Santo Domingo"
        assert (payload["writer"], payload["office"]) == ("Decrès", "Minister of Marine and the Colonies")
        assert payload["device"] == {"kind": "monogram", "nation": "", "letter": "D"}
        assert payload["line"].startswith("Sire, Ferrand wrote last February")
        assert payload["ground"] == MO.entry(armed, H1)["record"]
        assert payload["chapter"].startswith("Historically Haiti killed the French")
        assert payload["exhibit"].startswith("‘Slavery is forever abolished.’")
        assert payload["exhibit_from"] == "FROM HAITI —"
        assert payload["record"] == f"{payload['ground']} {payload['chapter']}"
        assert payload["board"] == [
            "France blockaded 7 of the last 12 mornings; the Emperor holds court at Lorraine.",
            "Britain's squadrons hold the coast: 100 sail effective against our 31."]
        assert payload["counsel"].startswith("Berthier — Two frigates and flour")
        assert payload["counsel"] == payload["talleyrand_assessment"]
        assert payload["odds"] == 0                          # H0: no squadron
        for key in ("board", "exhibit", "chapter", "exhibit_from"):
            assert "_" not in re.sub(r"\{[a-z_]+\}", "", str(payload[key]))

    def test_the_board_names_an_open_sea_when_no_hunter_holds_the_coast(self, armed):
        _haiti_board(armed)
        assert _run(armed, range(1, 8)) == {7: [f"{H1}#1"]}
        armed.diplomatic_states[armed._make_diplo_key("France", "Britain")] = "PEACE"
        armed.invalidate_active_nations_cache()
        armed.__dict__.pop("_affairs_memo", None)
        board = AF.board_lines(armed, MO.entry(armed, H1), MO.status_row(armed, f"{H1}#1"))
        assert board[1] == "No enemy squadron holds the coast this morning; 31 sail effective in port."

    def test_a_moment_s_payload_carries_no_exhibit_keys(self, armed):
        """RE2-1's lesson: the dress keys are the occurrence's; a moment reads
        no exhibit, no run-in."""
        e = MO.entry(armed, "bavarian_match")
        payload = MO.letter_payload(armed, e, 8, 9, {})
        assert payload["exhibit"] == "" and "exhibit_from" not in payload

    def test_the_closing_record_is_authored_for_the_correspondence(self, armed):
        """§6.5: when the file closes the Correspondence (RE-C, §12b.1) prints the
        closing record and the 1825 line — authored here, rendered there; a
        display key struck from the measured identity."""
        e = MO.entry(armed, H1)
        assert e["closing"][0].startswith("Historically the Spanish colonists rose in 1808")
        assert "Palo Hincado" in e["closing"][0] and "July 1809" in e["closing"][0]
        assert "1825" in e["closing"][1] and "150 million francs" in e["closing"][1] and "Boyer" in e["closing"][1]
        assert "closing" in AF.DISPLAY_KEYS and "exhibit_from" in AF.DISPLAY_KEYS and "slots" in AF.DISPLAY_KEYS

    def test_the_lockstep_and_the_measured_identity(self):
        from tools._s14c_sweep_record import deck_sha
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
        assert scenario["affairs"] == _block()["affairs"]
        assert [e["id"] for e in scenario["affairs"]["deck"]][-1] == H1
        import copy
        reworded = copy.deepcopy(scenario)
        haiti = reworded["affairs"]["deck"][-1]
        haiti["exhibit"] = ["another exhibit"]
        haiti["exhibit_from"] = "FROM ELSEWHERE —"
        haiti["closing"] = ["another closing"]
        haiti["slots"] = {"wrote": [{"text": "once"}]}
        haiti["variants"][0]["text"] = "another chapter"
        assert deck_sha(reworded) == deck_sha(scenario)
        moved = copy.deepcopy(scenario)
        moved["affairs"]["deck"][-1]["latch"]["at_least"] = 5
        assert deck_sha(moved) != deck_sha(scenario)


# ═══════════════════════════════════════════════════════════════════════════
# The validator (RE-H's rules)
# ═══════════════════════════════════════════════════════════════════════════

def _h(b):
    return _aff(b, 3)


REH_BAD = [
    ("a fifth chapter", lambda b: _h(b)["variants"].append({"key": "arrival", "value": "later", "text": "x"}),
     "moments.affairs.deck[3].variants"),
    ("a fate the record does not name", lambda b: _h(b)["variants"][0].update(value="scattered"),
     "moments.affairs.deck[3].variants[0].value"),
    ("an exhibit without its run-in", lambda b: _h(b).pop("exhibit_from"), "moments.affairs.deck[3].exhibit_from"),
    ("a run-in without an exhibit", lambda b: _aff(b, 0).update(exhibit_from="FROM PARIS —"),
     "moments.affairs.deck[0].exhibit_from"),
    ("three exhibits", lambda b: _h(b)["exhibit"].append("a third"), "moments.affairs.deck[3].exhibit"),
    ("an exhibit past 160", lambda b: _h(b)["exhibit"].__setitem__(0, "x" * 161), "moments.affairs.deck[3].exhibit[0]"),
    ("a run-in past 40", lambda b: _h(b).update(exhibit_from="F" * 41), "moments.affairs.deck[3].exhibit_from"),
    ("a slot date off its turn", lambda b: _h(b)["slots"]["wrote"][0]["until"].update(turn=20),
     "moments.affairs.deck[3].slots.wrote[0].until.date"),
    ("a slot whose last entry is dated", lambda b: _h(b)["slots"]["wrote"][1].update(
        until={"date": "1807-01-01", "turn": 32}), "moments.affairs.deck[3].slots.wrote[1].until"),
    ("a slot phrase past 60", lambda b: _h(b)["slots"]["wrote"][1].update(text="x" * 61),
     "moments.affairs.deck[3].slots.wrote[1].text"),
    ("a closing past 240", lambda b: _h(b)["closing"].__setitem__(0, "x" * 241), "moments.affairs.deck[3].closing[0]"),
    ("three closing lines", lambda b: _h(b)["closing"].append("a third"), "moments.affairs.deck[3].closing"),
    ("a fleet of none", lambda b: _h(b)["when"].update(min_ships=0), "moments.affairs.deck[3].when.min_ships"),
    ("a purse bar past 5,000", lambda b: _h(b)["when"].update(min_purse=5001), "moments.affairs.deck[3].when.min_purse"),
    ("a bites word the engine lacks", lambda b: _h(b).update(bites="aura"), "moments.affairs.deck[3].bites"),
    ("an ends before the anchor", lambda b: _h(b).update(ends={"date": "1805-01-01", "turn": 1}),
     "moments.affairs.deck[3].ends.date"),
]


class TestTheValidatorREH:
    @pytest.mark.parametrize("label, mutate, path", REH_BAD, ids=[row[0] for row in REH_BAD])
    def test_each_bad_block_is_refused(self, label, mutate, path):
        assert path in _bad(mutate), label

    def test_the_marine_s_letter_needs_the_owner_s_navy(self):
        from backend.modding.validator import validate_scenario
        data = json.loads(SCENARIO.read_text(encoding="utf-8"))
        data["moments"] = _block()
        data["navies"]["France"]["ships"] = 0
        paths = {e.path for e in validate_scenario(data).errors}
        assert "moments.affairs.deck[3].when.predicate" in paths

    def test_the_fixture_still_validates(self):
        from tests.test_affairs_engine import _errors
        assert _errors(_block()) == []


# ═══════════════════════════════════════════════════════════════════════════
# The nondominance of the fourth letter (§16 "RE-3"'s pin, extended)
# ═══════════════════════════════════════════════════════════════════════════

class TestEachAnswerIsTheBetterOneSomewhere:
    @pytest.mark.parametrize("authority", [100, 85])
    def test_on_the_boards_where_the_letter_arrives(self, armed, authority):
        """At full standing the Decline is a dent (100 → 97) and the Accept
        buys honour for 600 gold and an action; across the aura's line the
        Decline costs the aura. Each answer is strictly better than the other
        on at least one delivered axis on both boards."""
        _haiti_board(armed, gold=40_000, authority=authority)
        e = MO.entry(armed, H1)
        accept = MO.plan(armed, e, MO.ANSWER_ACCEPT, _occ(1))
        decline = MO.plan(armed, e, MO.ANSWER_DECLINE, _occ(1))
        assert accept["ok"] and decline["ok"]
        gold = next(r for r in accept["rows"] if r["op"] == "gold")
        admin = next(r for r in accept["rows"] if r["op"] == "admin")
        standing = next(r for r in decline["rows"] if r["op"] == "authority")
        assert (gold["amount"], admin["amount"], standing["loss"]) == (600, 1, 3)
        assert not [r for r in decline["rows"] if r["op"] in ("gold", "dp", "admin")]
