"""DD-1 S6 "The Table and the Treaty" — instrument 3, THE ANSWER-BINDING
SHUFFLE (October 11, 2026; PRE_DEPLOY_PLAN.md §3.1; rules SYSTEMS_REFERENCE.md
§106; memo docs/audits/ANSWER_BINDING_2026_10_11.md; rows BUG_FIXES.md §DD-1 S6).

`tools/answer_binding_shuffle.py` delivers three letters (Prussia alliance,
Denmark non-aggression, Saxony open borders) through the real producer in
every order, then sends every typed answer and every button through the real
endpoints and reads each outcome against the shipped contract (IQ-7's closed
grammar, CA9's court guard, W6-0 / FA-N5's identity binding). 312 rows over
six orders; the committed record is `docs/audits/dd1/answer_binding.json`.

THE RATCHET. The first reading found ONE misbind class on four rows: `decline
<court>'s pact` is not read as an answer at all — `pact` is not among the
closed grammar's matter nouns, so the line falls to the order desk and is
shrugged at; nothing moved, but the court guard never spoke (DD1-9). The
class is the committed ledger `tests/data/answer_binding_known_misbinds.json`;
this file re-runs the whole shuffle live (seconds — the boot is cloned per
row) and pins that no misbind outside the ledger lands and that the ledger
only shrinks. The done-when of §3.1 (0 misbinds) is asserted NOT met so it is
re-seated on purpose.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
RECORD = REPO_ROOT / "docs" / "audits" / "dd1" / "answer_binding.json"
LEDGER = REPO_ROOT / "tests" / "data" / "answer_binding_known_misbinds.json"

MISBIND_CAP = 4          # October 11, 2026 — lower-only
LEDGER_CLASS_CAP = 2     # the one shape, two reply heads


@pytest.fixture(scope="module")
def ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def committed():
    return json.loads(RECORD.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def live():
    import answer_binding_shuffle as AB
    os.environ["INK_IRON_SAVE_DIR"] = str(REPO_ROOT / "tools" / "playtest_runs" / "_dd1_shuffle_pin")
    return AB.run(list_rows=False)


class TestTheCommittedRecord:
    def test_the_shape(self, committed):
        assert committed["orders"] == 6 and committed["count"] >= 300
        positions = {r["position"] for r in committed["rows"]}
        assert positions >= {"top", "activated", "button", "mailbox"}, positions

    def test_the_contract_holds_on_every_other_row(self, committed):
        """Every bare answer bound to the letter on top; every named answer
        for a QUEUED court was refused naming it; every stale button id was
        refused; every fail-closed line relayed nothing."""
        for row in committed["rows"]:
            if row["verdict"] == "misbind":
                continue
            assert row["verdict"] == "bound", row
            if row["expect"] == "nothing":
                assert not row["moved"]["gone"] and not row["moved"]["states_moved"], row
            if row["expect"] == "button_stale":
                assert not row["moved"]["gone"], row

    def test_the_misbinds_are_the_ledgers(self, committed, ledger):
        assert committed["misbinds"] <= MISBIND_CAP, committed["misbind_classes"]
        assert set(committed["misbind_classes"]) <= set(ledger), (
            set(committed["misbind_classes"]) - set(ledger))

    def test_the_done_when_is_read_and_not_met(self, committed):
        """§3.1: 'the answer-binding shuffle reads 0 misbinds'. NOT met on the
        first reading (4, one class). Re-seat when it is."""
        assert committed["misbinds"] > 0, "the done-when is met — re-seat this pin"


class TestTheLedgerIsARatchet:
    def test_the_ledger_only_shrinks(self, ledger):
        assert len(ledger) <= LEDGER_CLASS_CAP, sorted(ledger)
        for cls in ledger:
            assert "decline <court>'s pact" in cls, cls


class TestTheInstrumentLive:
    def test_the_live_shuffle_stays_within_the_ledger(self, live, ledger):
        assert live["count"] == 312, live["count"]
        assert live["misbinds"] <= MISBIND_CAP, live["misbind_classes"]
        assert set(live["misbind_classes"]) <= set(ledger), (
            set(live["misbind_classes"]) - set(ledger))

    def test_the_live_reading_matches_the_committed_one(self, live, committed):
        assert live["misbind_classes"] == committed["misbind_classes"]
        live_by = {(r["position"], tuple(r["order"]), r["form"]): r["verdict"] for r in live["rows"]}
        committed_by = {(r["position"], tuple(r["order"]), r["form"]): r["verdict"] for r in committed["rows"]}
        assert live_by == committed_by

    def test_a_bare_answer_never_leaves_the_letter_on_top(self, live):
        for row in live["rows"]:
            if row["expect"] in ("answer", "button_bare"):
                assert row["moved"]["courts_gone"] in ([], [row["current"]]), row

    def test_a_named_queued_court_is_refused_naming_it_and_nothing_moves(self, live, ledger):
        """Every named answer for a queued court: nothing moved, ever; and —
        outside the ledger's one form (`decline <court>'s pact`, which the
        grammar does not read as an answer at all, DD1-9) — refused NAMING
        the court."""
        for row in live["rows"]:
            if row["expect"] == "named" and row["named"] != row["current"] and row["position"] == "top":
                assert not row["moved"]["gone"] and not row["moved"]["states_moved"], row
                if row["verdict"] == "misbind":
                    assert "'s pact" in row["form"], row
                    continue
                assert row["verdict"] == "bound", row
                assert row["named"] in row["reply"], row

    def test_a_stale_button_id_is_refused(self, live):
        for row in live["rows"]:
            if row["expect"] == "button_stale":
                assert row["verdict"] == "bound" and not row["moved"]["gone"], row
