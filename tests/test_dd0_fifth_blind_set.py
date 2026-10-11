"""DD-0 S4 "The Command Road" — THE FIFTH BLIND AUTHOR SET, the done-when's
second fresh reading (October 10, 2026; PRE_DEPLOY_PLAN.md §3.0 "S4 landing
record, part 3"; memo docs/audits/UNREHEARSED_CENSUS_2026_10_10_FIFTH.md;
rules SYSTEMS_REFERENCE.md §104).

The fourth set became rehearsed by its own fixes (DD0-11 … DD0-17), so the
done-when is read again on a FRESH set: 300 orders written BLIND by a
fifth author (an agent that used no tool — only the boot screen's facts and
the judge's family names), run on a fresh boot board through the real
`POST /command`, keyless and keyed, read by the ONE judge, each row carrying
its trace. The file stays blind: nothing in it is fixed by this slice; its
shrug register is the next worklist (DD0-18).

S4 PART 4 (October 11, 2026) — THE RE-BASED INSTRUMENT, the user's ruling
(PRE_DEPLOY_PLAN.md §3.0): the done-when reads READ RIGHT BY HAND (as meant
+ asked + the board's own refusal + refused as meant) ≥ 85 % keyless with 0
EXECUTED-OTHER-THAN-MEANT by hand; `as_meant` is printed beside it, never in
its place. The judge's two dangerous classes are PROXIES, each read against
its trace in the committed hand file beside the records
(`by_hand/2026_10_10_fifth.json`, applied by `unrehearsed_census.py
--by-hand`). At this reading the fifth set stands at 241 of 300 (80.3 %)
with ONE real execution (`Ney, strike camp, abandon the works.` fought) —
NOT met; the fix (DD0-18) is read on this set's re-read and the done-when on
a SIXTH author's fresh set.

Pinned: the blind file's shape; the committed classes are the judge's own
reading; the dangerous classes lower-only; every proxy row read by hand
against the reply it was read against (no row unread, no verdict stale);
the two figures printed and the done-when's standing asserted on purpose.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BLIND = REPO_ROOT / "tools" / "playtest_scripts" / "unrehearsed_2026_10_10_fifth.json"
RECORDS = REPO_ROOT / "docs" / "audits" / "unrehearsed"
KEYLESS = RECORDS / "2026_10_10_fifth_keyless.json"
KEYED = RECORDS / "2026_10_10_fifth_keyed.json"
BY_HAND = RECORDS / "by_hand" / "2026_10_10_fifth.json"

KEYLESS_DANGEROUS_CAP = {"misread": 2, "executed_when_refusal_meant": 6}
KEYED_DANGEROUS_CAP = {"misread": 3, "executed_when_refusal_meant": 7}
KEYLESS_AS_MEANT_AT_READING = 121      # 125 measured; the objection dice move it ±4 (asked)
# S4 part 4 — the re-based instrument's figures at this reading (lower-only
# for the floor, lower-only for the cap).
KEYLESS_READ_RIGHT_AT_READING = 235    # 241 measured (80.3 %); the dice move it too
KEYED_READ_RIGHT_AT_READING = 259      # 265 measured (88.3 %)
EXECUTED_OTHER_THAN_MEANT_CAP = 1      # the one real execution — 0 once DD0-18 (a) lands
DONE_WHEN = 0.85
# The re-based done-when's standing on THIS set, asserted on purpose so it
# is re-seated by a hand and never by drift. The done-when itself is read on
# a FRESH set (the sixth author's); this set is read for its fixes.
DONE_WHEN_MET_ON_THIS_SET = False


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _census():
    spec = importlib.util.spec_from_file_location(
        "unrehearsed_census_for_dd0_fifth", REPO_ROOT / "tools" / "unrehearsed_census.py")
    census = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(census)
    return census


class TestTheBlindFile:
    def test_shape(self):
        d = _load(BLIND)
        assert d["name"] == "unrehearsed-2026-10-10-fifth"
        assert "never edited after the run" in d["_note"]
        assert len(d["orders"]) == 300
        lines = [o["line"] for o in d["orders"]]
        assert len(set(lines)) == 300, "every line unique"
        assert sum(1 for o in d["orders"] if o["intended"]["action"] == "refuse") == 30
        for o in d["orders"]:
            assert set(o["intended"]) >= {"action", "marshal", "target", "note"}


class TestTheRecords:
    @pytest.mark.parametrize("path", [KEYLESS, KEYED], ids=["keyless", "keyed"])
    def test_every_row_carries_a_trace_that_ends_on_the_reply(self, path):
        if not path.exists():
            pytest.skip(f"{path.name} not recorded")
        d = _load(path)
        assert d["blind"] == "unrehearsed-2026-10-10-fifth"
        assert len(d["rows"]) == 300
        for r in d["rows"]:
            assert r["kind"] == "order"
            trace = r.get("parse_trace")
            assert trace, r["line"]
            assert trace[0]["stage"] == "typed" and trace[-1]["stage"] == "reply"

    def test_the_records_are_the_judges_own_reading(self):
        census = _census()
        for path in (KEYLESS, KEYED):
            if not path.exists():
                continue
            d = _load(path)
            for r in d["rows"]:
                assert census.classify_order(r.get("intended") or {}, r) == r["class"], r["line"]

    @pytest.mark.parametrize("path,caps", [(KEYLESS, KEYLESS_DANGEROUS_CAP), (KEYED, KEYED_DANGEROUS_CAP)],
                             ids=["keyless", "keyed"])
    def test_the_dangerous_classes_only_fall(self, path, caps):
        if not path.exists():
            pytest.skip(f"{path.name} not recorded")
        d = _load(path)
        t = d["totals"]["order"]
        for cls, cap in caps.items():
            assert t.get(cls, 0) <= cap, (cls, t.get(cls))
        assert set(d["dangerous"]) == {r["line"] for r in d["rows"] if r["class"] in caps}

    def test_the_keyed_arm_consulted_the_model(self):
        if not KEYED.exists():
            pytest.skip("keyed record not recorded")
        d = _load(KEYED)
        assert d["llm"] == "anthropic" and d["live_parses"] > 0
        print(f"[dd0] fifth blind set keyed as_meant {d['totals']['order'].get('as_meant')} / 300")


class TestTheReBasedInstrument:
    """S4 part 4 — read right by hand and executed-other-than-meant, the
    judge's proxies read against their traces in the committed hand file."""

    def test_the_hand_file_reads_every_proxy_row_and_no_verdict_is_stale(self):
        census = _census()
        hand = census.load_by_hand(BY_HAND)
        assert hand["set"] == "unrehearsed-2026-10-10-fifth"
        for path in (KEYLESS, KEYED):
            if not path.exists():
                continue
            d = census.apply_by_hand(_load(path), hand)
            assert d["by_hand_unread"] == [], (path.name, d["by_hand_unread"])
            assert set(d["by_hand"]) == set(d["dangerous"]), path.name
            assert d["executed_other_than_meant"] is not None

    @pytest.mark.parametrize("path", [KEYLESS, KEYED], ids=["keyless", "keyed"])
    def test_the_record_carries_the_hand_reading_the_tool_computes(self, path):
        if not path.exists():
            pytest.skip(f"{path.name} not recorded")
        census = _census()
        d = _load(path)
        fresh = census.apply_by_hand(json.loads(json.dumps(d)), census.load_by_hand(BY_HAND))
        assert d["read_right"] == census.read_right_of(d) == fresh["read_right"]
        assert d["by_hand"] == fresh["by_hand"]
        assert d["executed_other_than_meant"] == fresh["executed_other_than_meant"]

    def test_executed_other_than_meant_only_falls(self):
        for path in (KEYLESS, KEYED):
            if not path.exists():
                continue
            d = _load(path)
            assert d["executed_other_than_meant"] <= EXECUTED_OTHER_THAN_MEANT_CAP, path.name

    def test_read_right_only_rises(self):
        d = _load(KEYLESS)
        assert d["read_right"] >= KEYLESS_READ_RIGHT_AT_READING
        if KEYED.exists():
            assert _load(KEYED)["read_right"] >= KEYED_READ_RIGHT_AT_READING

    def test_the_two_figures_are_printed_and_the_done_when_is_read_on_purpose(self):
        """The re-based done-when (the user's ruling, October 11, 2026):
        read right by hand ≥ 85 % keyless AND 0 executed-other-than-meant.
        `as_meant` printed beside, never in its place. Asserted at its
        standing so the day it flips this pin is re-seated by a hand."""
        d = _load(KEYLESS)
        t = d["totals"]["order"]
        as_meant = int(t.get("as_meant", 0))
        read_right, eotm = d["read_right"], d["executed_other_than_meant"]
        print(f"[dd0] fifth blind set keyless READ RIGHT BY HAND {read_right} / 300 "
              f"({100.0 * read_right / 300:.1f} %; done-when >= {DONE_WHEN:.0%}); "
              f"executed other than meant {eotm} (done-when 0); as meant {as_meant} / 300 beside")
        assert as_meant >= KEYLESS_AS_MEANT_AT_READING, "the fresh reading only rises"
        met = read_right >= DONE_WHEN * 300 and eotm == 0
        assert met is DONE_WHEN_MET_ON_THIS_SET, (
            "re-seat DONE_WHEN_MET_ON_THIS_SET by hand — and remember the done-when is read on a FRESH set")
