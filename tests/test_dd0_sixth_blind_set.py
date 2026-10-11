"""DD-0 S4 part 4 "The Command Road" — THE SIXTH BLIND AUTHOR SET (October
11, 2026; PRE_DEPLOY_PLAN.md §3.0 "S4 landing record, part 4"; memo
docs/audits/UNREHEARSED_CENSUS_2026_10_11_SIXTH.md; rules
SYSTEMS_REFERENCE.md §104 part 4; rows BUG_FIXES.md DD0-19).

The first fresh set read on the RE-BASED instrument (read right by hand ≥
85 % keyless, 0 executed-other-than-meant). Written BLIND by a sixth author
(an agent with zero tool uses — the boot screen's facts and the judge's
family names), run on a fresh boot board through the real `POST /command`,
keyless and keyed, read by the ONE judge and by hand (the committed hand
file beside the records). At its first reading it read 249 of 300 by the
judge (83.0 %) and held THREE real executions (`Send the fleet to attack
Swabia.` fought with Soult's corps; `Davout: drill. The new conscripts are
green.` recruited; `Bernadotte leaves 3000 men to hold Franconia` held) —
NOT met; DD0-19 fixed them the same day, and the set, rehearsed by its own
fixes, re-reads at 290 of 300 by hand (96.7 %) with 0 executions. The
done-when was then read on a SEVENTH author's fresh set. The file stays
blind.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BLIND = REPO_ROOT / "tools" / "playtest_scripts" / "unrehearsed_2026_10_11_sixth.json"
RECORDS = REPO_ROOT / "docs" / "audits" / "unrehearsed"
KEYLESS = RECORDS / "2026_10_11_sixth_keyless.json"
KEYED = RECORDS / "2026_10_11_sixth_keyed.json"
BY_HAND = RECORDS / "by_hand" / "2026_10_11_sixth.json"

KEYLESS_DANGEROUS_CAP = {"misread": 0, "executed_when_refusal_meant": 2}
KEYED_DANGEROUS_CAP = {"misread": 0, "executed_when_refusal_meant": 4}   # the live model's own refusals, each read by hand
KEYLESS_READ_RIGHT_BY_HAND_AT_READING = 284     # 290 measured (96.7 %); the dice
KEYED_READ_RIGHT_BY_HAND_AT_READING = 288       # 294 measured (98.0 %)
KEYLESS_AS_MEANT_AT_READING = 152               # 158 measured; the objection dice ±4
EXECUTED_OTHER_THAN_MEANT_CAP = 0
# The three real executions the FIRST reading found (DD0-19), by line — each
# now refused or read as meant on the record.
THE_THREE = {
    "Send the fleet to attack Swabia.": ("fleet is not a corps", "relayed nothing"),
    "Davout: drill. The new conscripts are green.": ("cannot drill", "drill"),
    "Bernadotte leaves 3000 men to hold Franconia and moves on.": ("We do not control", "garrison"),
}


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _census():
    spec = importlib.util.spec_from_file_location(
        "unrehearsed_census_for_dd0_sixth", REPO_ROOT / "tools" / "unrehearsed_census.py")
    census = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(census)
    return census


class TestTheBlindFile:
    def test_shape(self):
        d = _load(BLIND)
        assert d["name"] == "unrehearsed-2026-10-11-sixth"
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
        d = _load(path)
        assert d["blind"] == "unrehearsed-2026-10-11-sixth"
        assert len(d["rows"]) == 300
        for r in d["rows"]:
            assert r["kind"] == "order"
            trace = r.get("parse_trace")
            assert trace, r["line"]
            assert trace[0]["stage"] == "typed" and trace[-1]["stage"] == "reply"

    def test_the_records_are_the_judges_own_reading(self):
        census = _census()
        for path in (KEYLESS, KEYED):
            d = _load(path)
            for r in d["rows"]:
                assert census.classify_order(r.get("intended") or {}, r) == r["class"], r["line"]

    @pytest.mark.parametrize("path,caps", [(KEYLESS, KEYLESS_DANGEROUS_CAP), (KEYED, KEYED_DANGEROUS_CAP)],
                             ids=["keyless", "keyed"])
    def test_the_dangerous_classes_only_fall(self, path, caps):
        d = _load(path)
        t = d["totals"]["order"]
        for cls, cap in caps.items():
            assert t.get(cls, 0) <= cap, (cls, t.get(cls))
        assert set(d["dangerous"]) == {r["line"] for r in d["rows"] if r["class"] in caps}

    def test_the_keyed_arm_consulted_the_model(self):
        d = _load(KEYED)
        assert d["llm"] == "anthropic" and d["live_parses"] > 0


class TestTheReBasedInstrument:
    def test_the_hand_file_reads_every_proxy_row_and_no_verdict_is_stale(self):
        census = _census()
        hand = census.load_by_hand(BY_HAND)
        assert hand["set"] == "unrehearsed-2026-10-11-sixth"
        for path in (KEYLESS, KEYED):
            d = census.apply_by_hand(_load(path), hand)
            assert d["by_hand_unread"] == [], (path.name, d["by_hand_unread"])
            assert set(d["dangerous"]) <= set(d["by_hand"]), path.name

    @pytest.mark.parametrize("path", [KEYLESS, KEYED], ids=["keyless", "keyed"])
    def test_the_record_carries_the_hand_reading_the_tool_computes(self, path):
        census = _census()
        d = _load(path)
        fresh = census.apply_by_hand(json.loads(json.dumps(d)), census.load_by_hand(BY_HAND))
        assert d["read_right"] == census.read_right_of(d) == fresh["read_right"]
        assert d["read_right_by_hand"] == fresh["read_right_by_hand"]
        assert d["by_hand"] == fresh["by_hand"]
        assert d["executed_other_than_meant"] == fresh["executed_other_than_meant"] == 0

    def test_the_figures_only_rise(self):
        kl, kd = _load(KEYLESS), _load(KEYED)
        assert kl["read_right_by_hand"] >= KEYLESS_READ_RIGHT_BY_HAND_AT_READING
        assert kd["read_right_by_hand"] >= KEYED_READ_RIGHT_BY_HAND_AT_READING
        assert kl["totals"]["order"].get("as_meant", 0) >= KEYLESS_AS_MEANT_AT_READING
        assert kl["executed_other_than_meant"] <= EXECUTED_OTHER_THAN_MEANT_CAP
        print(f"[dd0] sixth blind set keyless READ RIGHT BY HAND {kl['read_right_by_hand']} / 300 "
              f"({100.0 * kl['read_right_by_hand'] / 300:.1f} %); executed other than meant "
              f"{kl['executed_other_than_meant']}; as meant {kl['totals']['order'].get('as_meant')} / 300 beside")

    def test_the_three_real_executions_are_closed_by_line(self):
        d = _load(KEYLESS)
        rows = {r["line"]: r for r in d["rows"]}
        for line, (expect_a, expect_b) in THE_THREE.items():
            r = rows[line]
            msg = r["message"]
            assert expect_a in msg or expect_b in msg, (line, msg[:120])
            assert "MUSTER" not in msg and "recruits" not in msg and "will hold" not in msg, (line, msg[:120])
            assert r["class"] in ("as_meant", "asked", "board_refusal", "refused_as_meant", "honest_refusal")
