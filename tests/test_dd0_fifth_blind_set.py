"""DD-0 S4 "The Command Road" — THE FIFTH BLIND AUTHOR SET, the done-when's
second fresh reading (October 10, 2026; PRE_DEPLOY_PLAN.md §3.0 "S4 landing
record, part 3"; memo docs/audits/UNREHEARSED_CENSUS_2026_10_10_FIFTH.md;
rules SYSTEMS_REFERENCE.md §104).

The fourth set became rehearsed by its own fixes (DD0-11 … DD0-17), so the
≥ 85 % done-when is read again on a FRESH set: 300 orders written BLIND by a
fifth author (an agent that used no tool — only the boot screen's facts and
the judge's family names), run on a fresh boot board through the real
`POST /command`, keyless and keyed, read by the ONE judge, each row carrying
its trace. The file stays blind: nothing in it is fixed by this slice; its
shrug register is the next worklist (DD0-18).

Pinned: the blind file's shape; the committed classes are the judge's own
reading; the dangerous classes lower-only; the `as_meant` reading printed as
the measurement — 125 of 300 keyless against the ≥ 85 % done-when, NOT met
and recorded as such.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BLIND = REPO_ROOT / "tools" / "playtest_scripts" / "unrehearsed_2026_10_10_fifth.json"
RECORDS = REPO_ROOT / "docs" / "audits" / "unrehearsed"
KEYLESS = RECORDS / "2026_10_10_fifth_keyless.json"
KEYED = RECORDS / "2026_10_10_fifth_keyed.json"

KEYLESS_DANGEROUS_CAP = {"misread": 2, "executed_when_refusal_meant": 6}
KEYED_DANGEROUS_CAP = {"misread": 3, "executed_when_refusal_meant": 7}
KEYLESS_AS_MEANT_AT_READING = 121      # 125 measured; the objection dice move it ±4 (asked)
DONE_WHEN = 0.85


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


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
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "unrehearsed_census_for_dd0_fifth", REPO_ROOT / "tools" / "unrehearsed_census.py")
        census = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(census)
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

    def test_the_measurement_is_recorded_and_the_done_when_is_not_met(self):
        """The ≥ 85 % read on the SECOND fresh set: 125 of 300 keyless.
        Printed and asserted as NOT met, so the day it is met this pin is
        re-seated on purpose, never by drift."""
        d = _load(KEYLESS)
        as_meant = d["totals"]["order"].get("as_meant", 0)
        print(f"[dd0] fifth blind set keyless as_meant {as_meant} / 300 "
              f"(done-when {DONE_WHEN:.0%}; at the reading {KEYLESS_AS_MEANT_AT_READING})")
        assert as_meant >= KEYLESS_AS_MEANT_AT_READING, "the fresh reading only rises"
        assert as_meant < DONE_WHEN * 300, "re-seat this pin when the done-when is met"

    def test_read_right_by_hand_is_the_wider_figure(self):
        """The done-when counts `as_meant` alone; on a boot board where the
        neighbouring provinces are a neutral's and the marshals object, the
        board's own refusals and the objections are the game reading RIGHT.
        Recorded beside the done-when, never in its place."""
        d = _load(KEYLESS)
        t = d["totals"]["order"]
        read_right = sum(t.get(k, 0) for k in ("as_meant", "asked", "board_refusal", "refused_as_meant"))
        print(f"[dd0] fifth blind set keyless read right by hand {read_right} / 300")
        assert read_right >= 235

    def test_the_keyed_arm_consulted_the_model(self):
        if not KEYED.exists():
            pytest.skip("keyed record not recorded")
        d = _load(KEYED)
        assert d["llm"] == "anthropic" and d["live_parses"] > 0
        print(f"[dd0] fifth blind set keyed as_meant {d['totals']['order'].get('as_meant')} / 300")
