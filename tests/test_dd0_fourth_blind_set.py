"""DD-0 S4 "The Command Road" — THE FOURTH BLIND AUTHOR SET, the done-when's
reading (October 10, 2026; PRE_DEPLOY_PLAN.md §3.0 "S4 landing record, part
2 — the measurement"; memo docs/audits/UNREHEARSED_CENSUS_2026_10_10_FOURTH.md;
rules SYSTEMS_REFERENCE.md §104).

300 orders written BLIND by a fourth author (an agent that used no tool —
never the repository, the corpus, the tests, the docs or the three earlier
blind files; only the boot screen's facts and the judge's family names),
each line run on a FRESH boot board through the real `POST /command`,
keyless and keyed, read by the ONE judge and carrying its parse trace.

Pinned: the blind file's shape and pledge; every row carries a trace that
ends on the reply; the committed classes are the shipping judge's own
reading; the DANGEROUS classes at their measured count, lower-only (the memo
splits them by hand: two real executions, one wrong order on the desk, two
dropped halves, one disclosed substitution, five honest refusals the judge
does not know); the two real executions named by line; the `as_meant`
reading printed as the measurement — 119 of 300 keyless against the ≥ 85 %
done-when, which is NOT met and is recorded as such.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BLIND = REPO_ROOT / "tools" / "playtest_scripts" / "unrehearsed_2026_10_10_fourth.json"
RECORDS = REPO_ROOT / "docs" / "audits" / "unrehearsed"
KEYLESS = RECORDS / "2026_10_10_fourth_keyless.json"
KEYED = RECORDS / "2026_10_10_fourth_keyed.json"

KEYLESS_DANGEROUS_CAP = {"misread": 5, "executed_when_refusal_meant": 6}
KEYED_DANGEROUS_CAP = {"misread": 4, "executed_when_refusal_meant": 7}
KEYLESS_AS_MEANT_AT_READING = 119
KEYED_AS_MEANT_AT_READING = 134
DONE_WHEN = 0.85


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


class TestTheBlindFile:
    def test_shape(self):
        d = _load(BLIND)
        assert d["name"] == "unrehearsed-2026-10-10-fourth"
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
        assert d["blind"] == "unrehearsed-2026-10-10-fourth"
        assert len(d["rows"]) == 300
        for r in d["rows"]:
            assert r["kind"] == "order"
            trace = r.get("parse_trace")
            assert trace, r["line"]
            assert trace[0]["stage"] == "typed" and trace[-1]["stage"] == "reply"

    def test_the_records_are_the_judges_own_reading(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "unrehearsed_census_for_dd0_fourth", REPO_ROOT / "tools" / "unrehearsed_census.py")
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

    def test_the_two_real_executions_are_named(self):
        """The memo's by-hand split: of the judge's eleven dangerous rows,
        these two RAN something the player did not mean — a line that
        forbade the fight fought (DD0-11), and a declaration became a charm
        mission (DD0-12). Pinned by line so the fix is read on the same
        evidence; a fix that lands rewrites the record and lowers the caps."""
        d = _load(KEYLESS)
        by_line = {r["line"]: r for r in d["rows"]}
        murat = by_line["Murat, your light horse to the Tyrol — eyes only, no fighting."]
        assert murat["class"] == "misread" and "MUSTER" in murat["message"]
        sweden = by_line["Berthier, inform the courts: France declares war on Sweden."]
        assert sweden["class"] == "misread" and "court and charm" in sweden["message"]

    def test_the_measurement_is_recorded_and_the_done_when_is_not_met(self):
        """The ≥ 85 % is read here, honestly: 119 of 300 keyless at the first
        fresh reading. Printed and asserted as NOT met, so the day it is met
        this pin is re-seated on purpose, never by drift."""
        d = _load(KEYLESS)
        as_meant = d["totals"]["order"].get("as_meant", 0)
        print(f"[dd0] fourth blind set keyless as_meant {as_meant} / 300 "
              f"(done-when {DONE_WHEN:.0%}; at the reading {KEYLESS_AS_MEANT_AT_READING})")
        assert as_meant >= KEYLESS_AS_MEANT_AT_READING, "the fresh reading only rises"
        assert as_meant < DONE_WHEN * 300, "re-seat this pin when the done-when is met"

    def test_the_keyed_arm_consulted_the_model(self):
        if not KEYED.exists():
            pytest.skip("keyed record not recorded")
        d = _load(KEYED)
        assert d["llm"] == "anthropic" and d["live_parses"] > 0
        print(f"[dd0] fourth blind set keyed as_meant {d['totals']['order'].get('as_meant')} / 300 "
              f"(at the reading {KEYED_AS_MEANT_AT_READING})")
