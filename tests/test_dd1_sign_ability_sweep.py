"""DD-1 S6 "The Table and the Treaty" — instrument 1, THE SIGN-ABILITY SWEEP
(October 11, 2026; PRE_DEPLOY_PLAN.md §3.1; rules SYSTEMS_REFERENCE.md §106;
memo docs/audits/SIGN_ABILITY_SWEEP_2026_10_11.md; rows BUG_FIXES.md §DD-1 S6).

`tools/sign_ability_sweep.py` runs the driver's own diplomacy arms (and three
fresh seeds) with spies on the six surfaces and dry-runs every promise through
the REAL ratifier on a clone of the world at the moment it is shown. Two
counts: A "shown as signable, refused when signed" and B "refused without
naming the clause". The committed records are `docs/audits/dd1/sign_ability_
<ARM>.json`.

THE RATCHET. The first reading (S6) found eleven A rows — every one a LETTER
— and two B rows (the raw code on the editor an ally petition's grant
opens). DD-1 S7 Slice B (the same day) landed `treaty.can_sign`, the ONE
verdict read by every surface AND the ratifier, and the sweep re-read 0 / 0
on every arm and the three seeds — the done-when of §3.1 MET. This file pins
that the committed counts stay at 0 (per arm), that the record carries the
shape the memo cites, and that the four clauses of the first reading no
longer appear as A rows. A short live arm (the FC arm and a four-turn seed,
the quick set) re-runs the instrument in a subprocess and must read 0.

MEASURED (October 11, 2026, S7 Slice B): A = 0 and B = 0 over ten arms
(2,822 promises); the S6 reading was A = 11 / B = 2.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
RECORDS = REPO_ROOT / "docs" / "audits" / "dd1"
TOOL = REPO_ROOT / "tools" / "sign_ability_sweep.py"

ARMS = ("FC", "OP", "VOLTE", "CONG", "PRESS", "REACH-AAR",
        "SEED-dd1-one", "SEED-dd1-two", "SEED-dd1-three", "SEED-quick")
# The committed reading (October 11, 2026, S7 Slice B) — A and B per arm, 0.
A_CAP = {arm: 0 for arm in ARMS}
B_CAP = {arm: 0 for arm in ARMS}
SURFACES = {"letter", "chip", "counsel", "congress", "settlement", "real"}
# The four clauses of the S6 reading (DD1-1 … DD1-4, SFR-B1) — none may
# appear as a refused LETTER row again.
S6_CLAUSES = {"leader_only", "one_to_one_war", "petition_table_closed", "already_given"}


def _record(arm: str) -> dict:
    path = RECORDS / f"sign_ability_{arm}.json"
    assert path.exists(), f"missing committed record {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def records():
    return {arm: _record(arm) for arm in A_CAP}


class TestTheCommittedRecords:
    def test_every_arm_has_a_record_with_the_shape(self, records):
        for arm, rec in records.items():
            assert rec["arm"] == arm
            assert rec["counts"]["shown"] > 0, arm
            assert rec["errors"] == [], (arm, rec["errors"][:3])
            for row in rec["rows"]:
                assert row["surface"] in SURFACES, (arm, row)
                assert "verdict" in row and "turn" in row, (arm, row)

    def test_the_counts_are_the_tools_own_reading(self, records):
        from sign_ability_sweep import summarize
        for arm, rec in records.items():
            fresh = summarize(rec["rows"])
            assert fresh["A_shown_signable_refused"] == rec["counts"]["A_shown_signable_refused"], arm
            assert fresh["B_refused_unnamed"] == rec["counts"]["B_refused_unnamed"], arm

    @pytest.mark.parametrize("arm", sorted(A_CAP))
    def test_a_and_b_only_fall(self, records, arm):
        counts = records[arm]["counts"]
        assert counts["A_shown_signable_refused"] <= A_CAP[arm], (arm, counts)
        assert counts["B_refused_unnamed"] <= B_CAP[arm], (arm, counts["B_messages"])

    def test_no_shown_promise_was_refused(self, records):
        """Every promise a surface made, the ratifier kept — on every arm; a
        refusal reached only through a letter the surface itself had
        closed (`enabled: False`) is not a promise."""
        for arm, rec in records.items():
            for row in rec["rows"]:
                if row["surface"] == "real" or not row.get("shown_signable"):
                    continue
                assert row.get("verdict") != "refused", (arm, row["surface"], row.get("message"))
                after = row.get("after_ask") or {}
                assert after.get("verdict") != "refused", (arm, row["surface"], after.get("message"))

    def test_the_s6_rows_are_gone(self, records):
        """SFR-B1 (the leader-only letter), the one-on-one settlement letter,
        the ally petition that could not be granted from the letter and the
        client petition for a province already given (DD1-1 … DD1-4): each
        was an A row of the first reading; none is a refused letter now."""
        clauses = set()
        for rec in records.values():
            for row in rec["rows"]:
                if (row["surface"] == "letter" and row.get("shown_signable")
                        and row.get("verdict") == "refused"):
                    clauses.add(row.get("clause"))
        assert not (S6_CLAUSES & clauses), clauses

    def test_every_refusal_names_its_clause(self, records):
        for arm, rec in records.items():
            for row in rec["rows"]:
                if row.get("verdict") == "refused":
                    assert row.get("clause") not in ("", "unnamed"), (arm, row.get("message"))
                after = row.get("after_ask") or {}
                if after.get("verdict") == "refused":
                    from sign_ability_sweep import clause_of
                    assert clause_of(after.get("message", "")) != "unnamed", (arm, after)

    def test_no_real_sign_by_the_player_was_refused(self, records):
        """The driver's own accepts: the letters, the chips and the levers are
        stamped from the one verdict, so the real ratifier never refused a
        click on an arm."""
        for arm, rec in records.items():
            assert rec["counts"]["real_refused_player"] == 0, arm

    def test_the_done_when_is_read_and_met(self, records):
        """§3.1: 'the sign-ability sweep reads 0 on every committed arm and
        three fresh seeds'. NOT met on the first reading (S6: 11 / 2); MET
        since DD-1 S7 Slice B (October 11, 2026 — `treaty.can_sign`,
        `SYSTEMS_REFERENCE.md` §108). Held at 0 / 0 from here."""
        total_a = sum(rec["counts"]["A_shown_signable_refused"] for rec in records.values())
        total_b = sum(rec["counts"]["B_refused_unnamed"] for rec in records.values())
        assert (total_a, total_b) == (0, 0), (total_a, total_b)


class TestTheInstrumentLive:
    @pytest.fixture(scope="class")
    def live(self):
        out = Path(tempfile.mkdtemp(prefix="dd1_sweep_pin_"))
        env = dict(os.environ)
        for key in ("PYTHONIOENCODING",):
            env.pop(key, None)
        proc = subprocess.run(
            [sys.executable, str(TOOL), "--quick", "--out", str(out / "records"),
             "--work", str(out / "work"), "--jobs", "2"],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=900,
        )
        assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
        return {p.stem.replace("sign_ability_", ""): json.loads(p.read_text(encoding="utf-8"))
                for p in (out / "records").glob("sign_ability_*.json")}

    def test_the_quick_arms_run_and_read_zero(self, live, records):
        assert set(live) == {"FC", "SEED-quick"}, sorted(live)
        for arm, rec in live.items():
            assert rec["errors"] == [], (arm, rec["errors"][:3])
            assert rec["counts"]["shown"] >= 30, (arm, rec["counts"])
            assert rec["counts"]["A_shown_signable_refused"] == 0, (arm, rec["counts"])
            assert rec["counts"]["B_refused_unnamed"] == 0, (arm, rec["counts"]["B_messages"])

    def test_the_live_reading_matches_the_committed_one(self, live, records):
        """The same arms on the same tree read the same promises (the dice
        are pinned; the dry run never touches the live world)."""
        for arm in ("FC", "SEED-quick"):
            assert live[arm]["counts"]["verdicts"] == records[arm]["counts"]["verdicts"], arm


class TestTheClauseVocabulary:
    def test_the_ratifiers_shapes_are_named(self):
        from sign_ability_sweep import clause_of
        assert clause_of("We already have Peace with Austria. An Armistice treaty would be a downgrade.") == "no_downgrade"
        assert clause_of("Relations with Prussia stand at 12; an Alliance needs 60.") == "relation_floor"
        assert clause_of("Only the war leader can settle this side.") == "leader_only"
        assert clause_of("Use bilateral peace or armistice for a one-on-one war.") == "one_to_one_war"
        assert clause_of("Cannot vassalize Prussia: too powerful to subjugate (80%).") == "vassal_cap"

    def test_a_raw_code_is_unnamed(self):
        from sign_ability_sweep import clause_of
        assert clause_of("Cannot declare war: war_instance_side_conflict (both nations live in war_1)") == "unnamed"
        assert clause_of("Please choose an option (1-4), Sire.") == "unnamed"
        assert clause_of("") == "unnamed"
