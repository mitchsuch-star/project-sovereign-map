"""DD-1 S6 "The Table and the Treaty" — instrument 2, THE TREATY STATE-MACHINE
FUZZER (October 11, 2026; PRE_DEPLOY_PLAN.md §3.1; rules SYSTEMS_REFERENCE.md
§106; memo docs/audits/TREATY_FUZZER_2026_10_11.md; rows BUG_FIXES.md §DD-1 S6).

`tools/treaty_fuzzer.py` drives random lawful sequences of the table's verbs
through the REAL executor (structured commands, no parser) and reads the
§70 / §81 invariants after every step. The committed records are
`docs/audits/dd1/treaty_fuzzer_<seed>.json` (10 seeds x 1,000 steps).

THE RATCHET. The first reading found violations in a handful of CLASSES —
each class one defect that persists over many steps (the record counts
DISTINCT (class, detail) pairs). The classes are the committed ledger
`tests/data/treaty_fuzzer_known_violations.json`; this file pins that NO
class outside the ledger lands (a new regression is red the day it is
written) and that the ledger only SHRINKS (`tools/treaty_fuzzer.py
--write-ledger` after a fix, with the count falling). A live run of two
seeds x 150 steps (seconds) must stay within the ledger's classes; the
done-when of §3.1 (10 seeds x 1,000 steps, 0 violations) is read on the
committed records and asserted NOT met so it is re-seated on purpose.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
RECORDS = REPO_ROOT / "docs" / "audits" / "dd1"
LEDGER = REPO_ROOT / "tests" / "data" / "treaty_fuzzer_known_violations.json"
SEEDS = [f"dd1-fuzz-{i}" for i in range(1, 11)]

# The invariant classes the instrument can name (the memo's vocabulary).
CLASSES = {
    "I1_instance_ownership", "I1_war_without_purpose", "I1_checker_raised",
    "I2_client_at_war_lord_is_not",
    "I3_write_outside_setter", "I3_states_reassigned",
    "I4_negative",
    "I5_side_without_meta", "I5_meta_without_side_not_exited", "I5_active_not_on_a_side",
    "I5_active_but_exited", "I5_pair_meta_sides", "I5_pair_both_active_and_resolved",
    "I5_resolved_pair_not_stamped",
    "I6_round_trip", "verb_raised",
}


@pytest.fixture(scope="module")
def ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def records():
    out = {}
    for seed in SEEDS:
        path = RECORDS / f"treaty_fuzzer_{seed}.json"
        assert path.exists(), path
        out[seed] = json.loads(path.read_text(encoding="utf-8"))
    return out


class TestTheCommittedRecords:
    def test_ten_seeds_a_thousand_steps(self, records):
        for seed, rec in records.items():
            assert rec["seed"] == seed and rec["steps"] == 1000, seed
            assert rec["final_turn"] >= 20, (seed, rec["final_turn"])
            assert len(rec["sequence"]) == 1000, seed

    def test_every_verb_was_drawn_and_some_succeeded(self, records):
        """The sequences are lawful often: every verb drawn on every seed,
        and the table's verbs each succeeded at least once over the run."""
        succeeded: set = set()
        for seed, rec in records.items():
            assert set(rec["verbs"]) >= {"end_turn", "answer", "propose", "declare_war", "break",
                                         "make_vassal", "release_vassal", "white_peace",
                                         "common_peace", "summon"}, (seed, rec["verbs"])
            for row in rec["sequence"]:
                if row.get("ok"):
                    succeeded.add(row["verb"])
        assert {"end_turn", "answer", "propose", "declare_war", "break", "make_vassal",
                "release_vassal", "white_peace"} <= succeeded, succeeded

    def test_every_violation_is_a_known_class(self, records):
        for seed, rec in records.items():
            for v in rec["violations"]:
                assert v["cls"] in CLASSES, (seed, v["cls"])

    def test_the_states_dict_was_only_written_through_the_setter(self, records):
        """I3 — no write to `diplomatic_states` outside `set_diplomatic_state`
        on any seed (§70.2's known direct writers never fired on these roads)."""
        for seed, rec in records.items():
            assert rec["writers_outside_setter"] == {}, (seed, rec["writers_outside_setter"])
            assert not [v for v in rec["violations"] if v["cls"].startswith("I3_")], seed

    def test_nothing_below_zero(self, records):
        for seed, rec in records.items():
            assert not [v for v in rec["violations"] if v["cls"] == "I4_negative"], seed

    def test_no_verb_raised(self, records):
        for seed, rec in records.items():
            assert not [v for v in rec["violations"] if v["cls"] == "verb_raised"], (
                seed, [v["detail"] for v in rec["violations"] if v["cls"] == "verb_raised"][:2])

    def test_the_ledger_holds_every_committed_class(self, records, ledger):
        found = {v["cls"] for rec in records.values() for v in rec["violations"]}
        assert found <= set(ledger), found - set(ledger)

    def test_the_done_when_is_read_and_not_met(self, records):
        """§3.1: 'the fuzzer holds its invariants for 10 seeds x 1,000 steps'.
        Read here; NOT met on the first reading. Re-seat when Step 2 lands."""
        total = sum(len(rec["violations"]) for rec in records.values())
        assert total > 0, "the done-when is met — re-seat this pin"


class TestTheLedgerIsARatchet:
    def test_the_ledger_only_shrinks(self, ledger):
        # The count of classes at the landing (October 11, 2026) — lower-only.
        assert len(ledger) <= 9, sorted(ledger)
        for cls, row in ledger.items():
            assert cls in CLASSES, cls
            assert row["count"] >= 1 and row["examples"], cls


class TestTheInstrumentLive:
    @pytest.fixture(scope="class")
    def live(self):
        import treaty_fuzzer as TF
        os.environ["INK_IRON_SAVE_DIR"] = str(REPO_ROOT / "tools" / "playtest_runs" / "_dd1_fuzz_pin")
        TF._env()
        return {seed: TF.run_seed(seed, 150, 10, False) for seed in ("dd1-pin-a", "dd1-pin-b")}

    def test_two_seeds_run_and_stay_within_the_ledger(self, live, ledger):
        for seed, rec in live.items():
            assert rec["steps"] == 150 and rec["final_turn"] >= 5, (seed, rec["final_turn"])
            assert rec["writers_outside_setter"] == {}, (seed, rec["writers_outside_setter"])
            for v in rec["violations"]:
                assert v["cls"] in ledger, (seed, v["cls"], v["detail"][:200], v["sequence"][-3:])

    def test_the_recorder_sees_the_setter(self, live):
        """The recording dict attributed every transition to the setter
        (the instrument's own sanity: a transition tally that is not empty)."""
        for seed, rec in live.items():
            assert rec["transitions"], seed


class TestTheRecorder:
    def test_a_write_outside_the_setter_is_attributed(self):
        from treaty_fuzzer import RecordingStates
        states = RecordingStates({"A|B": "PEACE"})
        states["A|B"] = "WAR"
        assert states.log and states.log[0]["through_setter"] is False
        assert states.log[0]["old"] == "PEACE" and states.log[0]["new"] == "WAR"

    def test_a_write_through_the_setter_is_attributed(self):
        from backend.game_logic.diplomacy import set_diplomatic_state
        from backend.models.world_state import WorldState
        from treaty_fuzzer import RecordingStates
        world = WorldState()
        world.diplomatic_states = RecordingStates(world.diplomatic_states)
        a, b = sorted(world.get_active_nations())[:2]
        set_diplomatic_state(world, a, b, "WAR", reason="pin")
        writes = [w for w in world.diplomatic_states.log if w["new"] == "WAR"]
        assert writes and writes[-1]["through_setter"] is True
        assert writes[-1]["reason"] == "pin"

    def test_the_round_trip_reads_a_difference(self):
        from treaty_fuzzer import _first_diff
        assert _first_diff({"a": {"b": 1}}, {"a": {"b": 2}}, "") == "/a/b: '1' vs '2'"
        assert _first_diff({"a": [1, 2]}, {"a": [1, 2]}, "") == ""
