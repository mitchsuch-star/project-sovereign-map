"""S14c — the moments' pacing, measured (`docs/EVENTS_SPEC.md` §7). Part 2's
first landing (S14C-X3): the instruments see a moment letter. Part 4: the
moments' production-time trace (`tools/_moments_trace.py`) judges the
ceilings, the floors and shown = applied — its teeth on synthetic rows, the
S14C-X24 board read through it, and part 4's measurement
(`tools/_s14c_sweep_final.json`: the 10-seed sweep, the archived commanded
arms, the accept arms, the VP-1 road arms) pinned against the shipped deck.

The sweep (`tools/ai_v_sweep.py`) counts the letters by object identity and
their rows per producing turn, never as a court's courting; the driver
(`tools/playtest_driver.py`) prints the rows and answers a letter from its
own `--moment` dial, by the option's action — a closed Accept left standing
with its reason, where it used to fall to the Decline in silence.
"""
import argparse
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import moments as MO
from tests import _chip_census as C
from tests.test_moments_engine import _at, _block, _tick

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
RECORD = REPO / "tools" / "_s14c_sweep_final.json"
FAMILIES = ("sweep", "commanded", "accept", "road", "road_accept")
CRISIS = {"Prussia": {"coveter": "Prussia", "target": "Hanover", "opened_turn": 7,
                      "foregrounded": True, "foregrounded_turn": 7}}


def _sweep():
    spec = importlib.util.spec_from_file_location("_ai_v_sweep", REPO / "tools" / "ai_v_sweep.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def _digest(rows, final=None):
    base = {"turn": 0, "threat": 0, "mirror": [0, 0, ""], "intents": {}, "wars_opened": [],
            "wars_ended": [], "events": [], "dispatch_queue": [], "incoming_proposals": [],
            "exhaustion": {}, "gold": {}, "strength": {}}
    return {"meta": {"player": "France", "france_needles": ["france", "french"]},
            "turns": [dict(base, **r) for r in rows],
            "final": final or {}}


class TestTheSweepCountsTheLetters:
    def test_a_moment_letter_is_no_court_s_courting(self, world):
        sweep = _sweep()
        world.moments = MO.from_block(_block())
        capture = sweep.RunCapture(world)
        _at(world, 8)
        _tick(world)
        assert not [r for r in capture._incoming_proposals() if r["ptype"] == "moment_letter"]
        letters = capture._moment_letters()
        assert [r["moment"] for r in letters] == ["bavarian_match"]
        assert capture._moment_letters() == []          # by identity: seen once
        assert capture._moments_open() == 1

    def test_the_metrics_read_the_rows(self):
        sweep = _sweep()
        rows = [
            {"turn": 8, "events": [{"type": "moment", "phase": "arrived", "moment": "a"},
                                   {"type": "moment", "phase": "arrived", "moment": "b"}],
             "moments_open": 2, "foreground_in_tenure": True},
            {"turn": 10, "events": [{"type": "moment", "phase": "passed", "reason": "crowded",
                                     "moment": "c"},
                                    {"type": "offer_lapsed", "proposal_type": "moment_letter"}],
             "dispatch_queue": [{"type": "moment_receipt", "vars": {"line": "c passed"},
                                 "queued_turn": 10}]},
        ]
        final = {"moments": {"state": {"a": {"status": "lapsed"}, "c": {"status": "passed", "reason": "crowded"},
                                       "d": {"status": "passed", "reason": "premise"}}}}
        derived = sweep.derive_metrics(_digest(rows, final))
        assert derived["moments_arrived"] == 2
        assert derived["moments_max_per_producing_turn"] == 2   # two in one turn — the R3 break, seen
        assert derived["letters_during_foreground"] == 2
        assert derived["open_letters_max"] == 2
        assert derived["moments_passed"] == {"crowded": 1, "premise": 1}
        assert derived["moments_lapsed"] == 1
        assert derived["fire_turns"] == {"a": [8], "b": [8]}
        assert derived["soap_opera_lines"] == [0, 0]            # a receipt is France's own

    def test_an_archived_digest_still_derives(self):
        derived = _sweep().derive_metrics(_digest([{"turn": 1}]))
        assert derived["moments_arrived"] == 0 and derived["moments_passed"] == {}


class TestTheDriverAnswersByIntent:
    def _answerer(self, policy):
        from tools import playtest_driver as D
        return D.Answerer(None, None, dict(D.POLICY_DEFAULTS) | policy, False), D

    def _letter(self, accept_enabled=True, reason=""):
        return {"is_moment": True, "proposal_type": "moment_letter", "from_nation": "",
                "options": [{"label": "Seal the match", "action": "accept_ai_proposal",
                             "enabled": accept_enabled, "reason": reason},
                            {"label": "Let Baden keep her", "action": "reject_ai_proposal",
                             "enabled": True, "reason": ""}]}

    def test_the_dial_is_absent_by_default_so_every_arm_is_unchanged(self):
        from tools import playtest_driver as D
        assert "moment" in D.POLICY_FLAG_KEYS and "moment" not in D.POLICY_DEFAULTS
        assert json.dumps(D.resolve_policy(argparse.Namespace(), {})) == json.dumps(dict(D.POLICY_DEFAULTS))
        assert D.moment_mode({}) == "decline"
        assert D.moment_mode({"diplomacy": "accept"}) == "decline"   # never the diplomacy dial

    def test_the_letter_is_answered_by_its_action(self):
        answerer, _ = self._answerer({"moment": "accept"})
        assert answerer._pick_dialogue_choice(self._letter()) == "accept_ai_proposal"
        answerer, _ = self._answerer({})
        assert answerer._pick_dialogue_choice(self._letter()) == "reject_ai_proposal"

    def test_a_closed_accept_leaves_the_letter_standing_with_its_reason(self):
        answerer, _ = self._answerer({"moment": "accept", "diplomacy": "accept"})
        reason = "1,000 gold is asked; the treasury holds 800."
        assert answerer._pick_dialogue_choice(self._letter(False, reason)) is None
        assert answerer.last_standing_reason == reason

    def test_the_log_prints_a_moment_s_rows(self):
        from tools import playtest_driver as D
        lines = []

        class _Rec:
            def _md(self, text):
                lines.append(text)

            def record(self, *a, **k):
                pass

        rec = _Rec()
        D.Digest.campaign_log(rec, [
            {"type": "moment", "display": "The Bavarian Match — a letter of the record is laid before the Emperor"},
            {"type": "offer_lapsed", "proposal_type": "moment_letter",
             "display": "The Bavarian Match was left unanswered — Let Baden keep her: Bavaria's goodwill 60 → 55."},
            {"type": "offer_lapsed", "proposal_type": "open_borders", "display": "Sweden's offer lapsed"},
        ], turn=8)
        assert any("LOG moment:" in ln for ln in lines)
        assert any("left unanswered" in ln for ln in lines)
        assert not any("Sweden" in ln for ln in lines)          # every other lapse stays unprinted


# ═══════════════════════════════════════════════════════════════════════════
# Part 4 — the trace, its teeth, the X24 board, the measured arms
# ═══════════════════════════════════════════════════════════════════════════

def _m(turn, **fields):
    row = {"turn": turn, "open": 0, "crisis": None, "true": [], "false": [], "delivered": [], "passed": {}}
    row.update(fields)
    return row


class TestTheTraceHasTeeth:
    """The judge sees each rule broken — an instrument that cannot fail measures nothing."""

    def _judge(self, mornings, applications=(), state=None):
        from tools._moments_trace import judge
        return judge(list(mornings), list(applications), state or {}, {"max_open": 1, "min_gap": 3})

    def test_each_ceiling_is_seen_broken(self):
        judged = self._judge([
            _m(8, true=["a", "b"], delivered=["a", "b"]),       # two in one morning, two open
            _m(12, open=1, true=["c"], delivered=["c"]),        # a second letter open
            _m(16, crisis=True, true=["d"], delivered=["d"]),   # under a foregrounded crisis
            _m(20, false=["e"], delivered=["e"])])              # its premise false
        assert [(b["turn"], b["rule"]) for b in judged["ceiling_breaches"]] == [
            (8, "R3"), (8, "max_open"), (12, "max_open"), (16, "R1"), (20, "premise")]

    def test_a_due_moment_passed_in_silence_breaks_the_floor(self):
        due = [_m(8, crisis=True, true=["a"])]
        assert self._judge(due, state={"a": {"status": "passed", "reason": "premise"}})["floor_breaches"] == ["a"]
        crowded = self._judge(due, state={"a": {"status": "passed", "reason": "crowded"}})
        assert crowded["floor_breaches"] == [] and crowded["floors"]["a"]["verdict"] == "ok"
        assert self._judge(due)["floors"]["a"]["verdict"] == "pending"   # the run stopped inside its window
        never_due = self._judge([_m(8, false=["a"])], state={"a": {"status": "passed", "reason": "premise"}})
        assert never_due["floors"] == {} and never_due["floor_breaches"] == []

    def test_a_figure_off_its_quote_is_seen(self):
        app = {"turn": 8, "moment": "a", "kind": "answer", "answer": "accept",
               "shown": "Yes: 100 gold.", "applied": "Yes: 90 gold.",
               "rows": [{"op": "gold", "figure": "treasury", "quoted": 900, "delivered": 910}]}
        judged = self._judge([], [app])
        assert judged["shown_equals_applied"] is False
        assert [m["figure"] for m in judged["mismatches"]] == ["quote", "treasury"]


class TestTheTraceOnTheX24Board:
    """S14C-X24 read through the trace: the Match due under a crisis on T8 and
    T9, Bavaria cooled that evening. The part-3 tick (the due mark held down)
    passes it in silence and the floor names it; the fix ends it on screen —
    the instrument and the fix, each the other's control."""

    def _walk(self, world, monkeypatch, *, marked=True, traced=True):
        from tools._moments_trace import MomentsTrace
        if not marked:
            monkeypatch.setattr(MO, "_mark_due", lambda *_a, **_k: None)
        world.moments = MO.from_block(_block())
        world.war_intents = copy.deepcopy(CRISIS)
        trace = MomentsTrace(lambda: world).install() if traced else None
        try:
            for turn in (8, 9):
                _at(world, turn)
                _tick(world)
            key = world._make_diplo_key("France", "Bavaria")
            world.diplomatic_states[key] = "PEACE"
            world.nation_relations[key] = 10
            for turn in (10, 11):
                _at(world, turn)
                _tick(world)
            return trace.summary()["judged"] if trace else None
        finally:
            if trace:
                trace.uninstall()

    def test_the_part_3_tick_is_read_silent(self, world, monkeypatch):
        judged = self._walk(world, monkeypatch, marked=False)
        assert judged["floor_breaches"] == ["bavarian_match"]
        assert judged["floors"]["bavarian_match"] == {
            "first_due": 8, "status": "passed", "reason": "premise", "verdict": "silent"}

    def test_the_fix_ends_it_on_screen(self, world, monkeypatch):
        judged = self._walk(world, monkeypatch)
        assert judged["floor_breaches"] == [] and judged["ceiling_breaches"] == []
        assert judged["passed"] == {"bavarian_match": "crowded"}
        assert [(a["kind"], a["figures"]) for a in judged["answers"]] == [("crowded", 1)]
        assert judged["shown_equals_applied"]

    def test_the_trace_calls_through(self, world, monkeypatch):
        self._walk(world, monkeypatch, traced=False)
        plain = (copy.deepcopy(world.moments), [dict(e) for e in world.event_log if e.get("type") == "moment"],
                 int(world.nation_relations[world._make_diplo_key("France", "Bavaria")]))
        C.boot()
        world = M.world
        self._walk(world, monkeypatch)
        traced = (copy.deepcopy(world.moments), [dict(e) for e in world.event_log if e.get("type") == "moment"],
                  int(world.nation_relations[world._make_diplo_key("France", "Bavaria")]))
        assert traced == plain
        assert MO._tick.__qualname__ == "_tick" and MO.premise.__qualname__ == "premise"   # uninstalled


class TestTheMeasuredArms:
    """`tools/_s14c_sweep_final.json` (`tools/_s14c_sweep_record.py`): the
    10-seed sweep with its control, variance and scripted-France arms, the
    nine archived commanded arms, the three accept arms, the VP-1 road arms
    and Road I answered — every run carrying the trace. Seeded paths, not
    laws: each moment's reach is reported per arm."""

    @pytest.fixture(scope="class")
    def record(self):
        return json.loads(RECORD.read_text(encoding="utf-8"))

    def _rows(self, record, families=FAMILIES):
        for family in families:
            for name, row in record[family].items():
                yield family, name, row

    def test_the_measured_identity_is_mechanical(self, record):
        """S14D-X42 (October 24, 2026): a corrected voice or record line must not
        demand a re-measure of arrivals and answers; an edited window or op must."""
        import copy
        from tools._s14c_sweep_record import deck_sha
        block = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
        reworded = copy.deepcopy(block)
        reworded["deck"][1]["voice"] = {"speaker": "cabinet"}
        reworded["deck"][1]["record"] = "another sentence"
        reworded["deck"][0]["title"] = "Another title"
        reworded["deck"][0]["accept"]["caption"] = "Another caption"
        assert deck_sha(reworded) == deck_sha(block)
        moved = copy.deepcopy(block)
        moved["deck"][1]["turn"] = {"value": 19, "band": [18, 20]}
        assert deck_sha(moved) != deck_sha(block)
        assert record["deck_sha"] == deck_sha(block)
        assert "mechanical" in str(record.get("deck_sha_note", ""))

    def test_it_measured_the_shipped_deck(self, record):
        from tools._s14c_sweep_record import deck_sha
        block = json.loads(SCENARIO.read_text(encoding="utf-8"))["moments"]
        assert record["deck_sha"] == deck_sha(block), "the deck changed: re-measure (tools/_s14c_sweep_record.py)"
        assert record["pacing"] == block["pacing"] and record["deck"] == [e["id"] for e in block["deck"]]

    def test_every_family_was_measured_with_the_trace(self, record):
        arm_c = {row["seed"] for name, row in record["sweep"].items() if name.startswith("armC_")}
        assert arm_c == set(_sweep().SWEEP_SEEDS)
        assert set(record["commanded"]) == {"CMD-A", "CMD-H", "CMD-M", "DL", "FC", "FLD", "LAW", "OP", "VOLTE"}
        assert set(record["accept"]) == {"CMD-A-ACCEPT", "CMD-H-ACCEPT", "CMD-M-ACCEPT"}
        assert {n.rsplit("-", 1)[0] for n in record["road"]} == {"VP1-RH", "VP1-CS", "VP1-TH"}
        assert set(record["road_accept"]) == {"VP1-RH-historical", "VP1-RH-austerlitz", "VP1-RH-marengo"}
        for family, name, row in self._rows(record):
            assert row["measured"] and row["mornings"] > 0 and row["errors"] == [], (family, name)

    def test_the_ceilings_hold_on_every_arm(self, record):
        max_open = int(record["pacing"]["max_open"])
        for family, name, row in self._rows(record):
            assert row["ceiling_breaches"] == [], (family, name)
        for name, row in record["sweep"].items():
            metrics = row["metrics"]
            assert metrics["max_per_turn"] <= 1 and metrics["open_max"] <= max_open, name
            assert metrics["during_foreground"] == 0, name

    def test_the_floors_hold_where_moments_can_fire(self, record):
        for family, name, row in self._rows(record):
            assert row["floor_breaches"] == [], (family, name)
        fired = {mid for _f, _n, row in self._rows(record, ("commanded", "accept", "road", "road_accept"))
                 for mid, floor in row["floors"].items() if floor["verdict"] == "ok"}
        assert {"bavarian_match", "throne_of_holland", "crown_of_the_reich"} <= fired

    def test_each_moment_s_reach_is_reported_per_arm(self, record):
        for family, name, row in self._rows(record):
            assert list(row["reach"]) == record["deck"], (family, name)

    def test_every_delivered_figure_equals_its_quote(self, record):
        for family, name, row in self._rows(record):
            assert row["shown_equals_applied"] and row["mismatches"] == [], (family, name)
        accepted = {a["moment"] for _f, _n, row in self._rows(record, ("accept", "road_accept"))
                    for a in row["answers"] if a["kind"] == "answer" and a["answer"] == "accept" and a["figures"]}
        assert accepted == {"bavarian_match", "throne_of_holland", "crown_of_the_reich"}
