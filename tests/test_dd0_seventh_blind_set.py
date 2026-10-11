"""DD-0 S4 part 4 "The Command Road" — THE SEVENTH BLIND AUTHOR SET, the
re-based done-when READ AND MET (October 11, 2026; PRE_DEPLOY_PLAN.md §3.0
"S4 landing record, part 4"; memo docs/audits/UNREHEARSED_CENSUS_2026_10_11_
SEVENTH.md; rules SYSTEMS_REFERENCE.md §104 part 4; the register's remainder
BUG_FIXES.md DD0-20).

The sixth set became rehearsed by its own fixes (DD0-19), so the re-based
done-when — *a FRESH blind set reads ≥ 85 % READ RIGHT BY HAND keyless (as
meant + asked + the board's own refusal + refused as meant) with 0
executed-other-than-meant* — was read on a SEVENTH author's set: 300 orders
written BLIND (an agent with zero tool uses), run on a fresh boot board
through the real `POST /command`, keyless and keyed, read by the ONE judge
and by hand (the committed hand file beside the records: six proxy rows —
two wrong desks, one staged proposal, three board refusals of lines meant to
be refused — and eight honest refusals that are the border law's and the
levy's reach rule).

MEASURED: keyless 255 of 300 read right by hand (85.0 %) — the done-when's
floor exactly, no margin — with 0 executed-other-than-meant; keyed 280
(93.3 %), 0. `as_meant` 153 / 300 beside. MET. The 27 shrugs and the
parser's share of the honest refusals are DD0-20's worklist. Nothing in the
file was fixed before this reading; the file stays blind.

DD0-20 (Pre-Deploy S5, October 11, 2026): the register read and the set
RE-READ as fresh runs — keyless 294 of 300 by hand (98.0 %), 0; keyed 296
(98.7 %), 0 (SYSTEMS_REFERENCE.md §105; tests/test_dd0_s5_the_register.py).
The one shrug left is the bare `probe <place>` (CX-R1's hand list); the
three honest refusals left are the design's own contingencies.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BLIND = REPO_ROOT / "tools" / "playtest_scripts" / "unrehearsed_2026_10_11_seventh.json"
RECORDS = REPO_ROOT / "docs" / "audits" / "unrehearsed"
KEYLESS = RECORDS / "2026_10_11_seventh_keyless.json"
KEYED = RECORDS / "2026_10_11_seventh_keyed.json"
BY_HAND = RECORDS / "by_hand" / "2026_10_11_seventh.json"

DONE_WHEN = 0.85
# DD0-20 (Pre-Deploy S5, October 11, 2026): the register's remainder read on
# the set's RE-READ — the records rewritten as fresh runs, the file still
# blind. Keyless: as meant 152 → 174 / 173 (two runs), shrugs 26 → 1 / 2
# (the bare `probe`, CX-R1's own; one line with the dice), the judge's four
# 244 → 277, READ RIGHT BY HAND 255 → 294 of 300 (98.0 %) on both runs, 0
# executed-other-than-meant; keyed: 281 → 296 (98.7 %), 0,
# the model consulted on 7 lines where it had been on 37. The dangerous caps
# lowered to the reading; the floors raised to it (the dice ±4 on as meant,
# a margin of 2 on the keyed arm).
KEYLESS_DANGEROUS_CAP = {"misread": 0, "executed_when_refusal_meant": 4}
KEYED_DANGEROUS_CAP = {"misread": 0, "executed_when_refusal_meant": 4}
KEYLESS_READ_RIGHT_BY_HAND_AT_READING = 294
KEYED_READ_RIGHT_BY_HAND_AT_READING = 294       # 296 measured
KEYLESS_AS_MEANT_AT_READING = 170               # 174 measured; the objection dice ±4
EXECUTED_OTHER_THAN_MEANT_CAP = 0
DONE_WHEN_MET_ON_THIS_SET = True


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _census():
    spec = importlib.util.spec_from_file_location(
        "unrehearsed_census_for_dd0_seventh", REPO_ROOT / "tools" / "unrehearsed_census.py")
    census = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(census)
    return census


class TestTheBlindFile:
    def test_shape(self):
        d = _load(BLIND)
        assert d["name"] == "unrehearsed-2026-10-11-seventh"
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
        assert d["blind"] == "unrehearsed-2026-10-11-seventh"
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


class TestTheReBasedDoneWhen:
    def test_the_hand_file_reads_every_proxy_row_and_no_verdict_is_stale(self):
        census = _census()
        hand = census.load_by_hand(BY_HAND)
        assert hand["set"] == "unrehearsed-2026-10-11-seventh"
        for path in (KEYLESS, KEYED):
            d = census.apply_by_hand(_load(path), hand)
            assert d["by_hand_unread"] == [], (path.name, d["by_hand_unread"])
            assert set(d["dangerous"]) <= set(d["by_hand"]), path.name
            assert d["executed_other_than_meant"] is not None

    @pytest.mark.parametrize("path", [KEYLESS, KEYED], ids=["keyless", "keyed"])
    def test_the_record_carries_the_hand_reading_the_tool_computes(self, path):
        census = _census()
        d = _load(path)
        fresh = census.apply_by_hand(json.loads(json.dumps(d)), census.load_by_hand(BY_HAND))
        assert d["read_right"] == census.read_right_of(d) == fresh["read_right"]
        assert d["read_right_by_hand"] == fresh["read_right_by_hand"]
        assert d["by_hand"] == fresh["by_hand"]
        assert d["executed_other_than_meant"] == fresh["executed_other_than_meant"]

    def test_no_proxy_row_executed_anything_by_hand(self):
        """The proxy rows read against their traces: one staged proposal
        (nothing sent) and three board refusals of lines meant to be
        refused. The two wrong desks of the first reading (`Soult: assault
        Mack's position, Ney in support.`, `Send 50 gold to the Kingdom of
        Italy's treasury.`) execute AS MEANT on the DD0-20 re-read (S5,
        October 11, 2026) and are proxy rows no longer; their hand rows
        were withdrawn with the traces they were read against."""
        d = _load(KEYLESS)
        assert d["executed_other_than_meant"] == 0
        verdicts = d["by_hand"]
        assert verdicts["Berthier, propose peace to Austria."] == "staged"
        assert "executed" not in verdicts.values()
        classes = {r["line"]: r["class"] for r in d["rows"] if r["kind"] == "order"}
        assert classes["Soult: assault Mack's position, Ney in support."] == "as_meant"
        # the investment reaches its desk; on the boot board the Kingdom of
        # Italy's loyalty is already full, so the board refuses it in words
        assert classes["Send 50 gold to the Kingdom of Italy's treasury."] in ("as_meant", "board_refusal")

    def test_the_done_when_is_read_and_met(self):
        """The ruling's instrument, on the FRESH seventh set: read right by
        hand >= 85 % keyless AND 0 executed-other-than-meant. Met at the
        floor — 255 of 300 — and asserted at its standing so a re-read that
        falls under it fails here, by name."""
        kl, kd = _load(KEYLESS), _load(KEYED)
        rr, eotm = kl["read_right_by_hand"], kl["executed_other_than_meant"]
        as_meant = int(kl["totals"]["order"].get("as_meant", 0))
        print(f"[dd0] SEVENTH blind set keyless READ RIGHT BY HAND {rr} / 300 ({100.0 * rr / 300:.1f} %; "
              f"done-when >= {DONE_WHEN:.0%}); executed other than meant {eotm} (done-when 0); "
              f"as meant {as_meant} / 300 beside; keyed {kd['read_right_by_hand']} / 300")
        assert rr >= KEYLESS_READ_RIGHT_BY_HAND_AT_READING
        assert kd["read_right_by_hand"] >= KEYED_READ_RIGHT_BY_HAND_AT_READING
        assert as_meant >= KEYLESS_AS_MEANT_AT_READING
        assert eotm <= EXECUTED_OTHER_THAN_MEANT_CAP
        met = rr >= DONE_WHEN * 300 and eotm == 0
        assert met is DONE_WHEN_MET_ON_THIS_SET
