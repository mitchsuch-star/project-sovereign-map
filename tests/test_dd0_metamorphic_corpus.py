"""DD-0 S3 "The Command Road" — instrument 2, THE METAMORPHIC CORPUS
(October 10, 2026; PRE_DEPLOY_PLAN.md §3.0; rules SYSTEMS_REFERENCE.md §101).

From the golden corpus's order rows, `backend/ai/parser_metamorphic.py`
generates variants whose reading is known by construction — a `same`
relation (please, an honorific, a reason tail, a dash aside, a
contraction, a leading-verb typo, the address moved to the tail, the
second name as a role, lowercase) and a flip (a negation must be REFUSED;
a modal question or a hedge must not execute the order). Each variant is
parsed beside its original on the same board and judged on the harness's
own keys; a failure carries the variant's parse trace (§100).

THE RATCHET. The first reading of the instrument fails in places — that is
what it is for. The failing variant ids are the committed ledger
`tests/data/metamorphic_known_failures.json` (S4's worklist, attributed by
stage); this file pins that NO failure outside the ledger lands (a new
regression is red the day it is written) and that the ledger's count only
FALLS (`tools/metamorphic_census.py --write-ledger` after a fix). A ledger
row that now passes is reported, not failed — prune it with the tool.

Also pinned: the generator's shape (every family fires; the applicability
rules keep the unfair cases out — a negation only on a single-clause order
led by a verb; the flip families never on a question or a diplomatic row),
the judge on hand-built results, and that the corpus itself is untouched
(the harness's own count).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.ai import parser_eval
from backend.ai import parser_metamorphic as pm

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "tests" / "data" / "metamorphic_known_failures.json"

# The ledger's count at the landing (October 10, 2026) — lower-only.
LEDGER_CAP = 161


@pytest.fixture(scope="module")
def rows():
    return parser_eval.load_corpus()["entries"]


@pytest.fixture(scope="module")
def outcomes(rows):
    return pm.run(rows)


@pytest.fixture(scope="module")
def ledger():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


class TestTheGenerator:
    def test_every_family_fires(self, rows):
        variants = pm.generate(rows)
        fired = {v.family for v in variants}
        assert fired == {f.name for f in pm.FAMILIES}, fired
        assert len(variants) > 1500
        assert len({v.id for v in variants}) == len(variants), "ids unique"

    def test_only_order_rows(self, rows):
        by_id = {r["id"]: r for r in rows}
        for v in pm.generate(rows):
            row = by_id[v.row_id]
            exp = row["expected"]
            assert exp.get("action") in pm.ORDER_ACTIONS
            assert not exp.get("diplo") and exp.get("success") is not False
            assert "?" not in row["utterance"]

    def test_negation_needs_a_verb_and_one_clause(self):
        row = {"id": "x", "utterance": "Ney, attack Mack", "world": "1805",
               "expected": {"action": "attack", "marshal": "Ney"}}
        v = [x for x in pm.generate([row], ["negation"])]
        assert [x.utterance for x in v][:2] == ["Ney, do not attack Mack", "Ney, never attack Mack"]
        for bad in ("hold on, Ney, retreat", "Ney, I want you to move to Lorraine",
                    "Gen. Ney, hold on, move"):
            row["utterance"] = bad
            assert not pm.generate([row], ["negation"]), bad

    def test_the_honorific_is_read_through(self):
        row = {"id": "x", "utterance": "Marshal Ney, hold", "world": "1805",
               "expected": {"action": "hold", "marshal": "Ney"}}
        v = pm.generate([row], ["honorific", "modal_question", "word_order"])
        assert {x.utterance for x in v} == {"Ney, hold", "should Ney hold?"}

    def test_the_verb_typo_uses_the_repair_passs_vocabulary(self):
        row = {"id": "x", "utterance": "Ney, attack Mack", "world": "1805",
               "expected": {"action": "attack", "marshal": "Ney"}}
        assert pm.generate([row], ["verb_typo"])[0].utterance == "Ney, attcak Mack"
        row["utterance"] = "Ney, storm Swabia"   # not the pass's verb
        assert not pm.generate([row], ["verb_typo"])


class TestTheJudge:
    def _ok(self, **cmd):
        return {"success": True, "command": {"marshal": "Ney", "action": "attack",
                                             "target": "Mack", "type": "specific", **cmd}}

    def test_same_holds_and_breaks(self):
        v = pm.Variant("i", "please", "same", "please, Ney, attack Mack", "r", "1805", "Ney, attack Mack")
        assert pm.judge(v, self._ok(), self._ok()) is None
        assert "target" in pm.judge(v, self._ok(), self._ok(target="Swabia"))

    def test_refusal_wants_parse_negs_kind(self):
        v = pm.Variant("i", "negation", "refusal", "Ney, do not attack Mack", "r", "1805", "Ney, attack Mack")
        assert pm.judge(v, self._ok(), {"success": False, "refusal": "negation"}) is None
        assert "shrug" in pm.judge(v, self._ok(), {"success": False})
        assert "EXECUTED" in pm.judge(v, self._ok(), self._ok())

    def test_question_accepts_a_question_a_refusal_or_the_desk(self):
        v = pm.Variant("i", "hedge", "question", "maybe Ney, attack Mack", "r", "1805", "Ney, attack Mack")
        assert pm.judge(v, self._ok(), {"success": True, "command": {"action": "status", "question": {"kind": "what_if"}}}) is None
        assert pm.judge(v, self._ok(), {"success": True, "command": {"action": "help"}}) is None
        assert pm.judge(v, self._ok(), {"success": False}) is None
        assert "EXECUTED" in pm.judge(v, self._ok(), self._ok())


class TestTheRatchet:
    def test_no_failure_outside_the_ledger(self, outcomes, ledger):
        known = {f["id"] for f in ledger["failures"]}
        new = [o for o in outcomes if o.verdict and o.variant.id not in known]
        assert not new, "NEW metamorphic failures (not in the ledger):\n" + "\n".join(
            f"  {o.variant.id}  {o.variant.utterance!r}\n     {o.verdict}\n     last stage {o.last_stage}"
            for o in new[:25])

    def test_the_ledger_only_falls(self, ledger):
        assert ledger["count"] == len(ledger["failures"]) <= LEDGER_CAP

    def test_the_ledger_rows_are_attributed(self, ledger):
        for f in ledger["failures"]:
            assert f["id"] and f["family"] and f["why"] and f["last_stage"], f

    def test_a_fixed_row_is_reported_for_pruning(self, outcomes, ledger, capsys):
        still = {o.variant.id for o in outcomes if o.verdict}
        stale = [f["id"] for f in ledger["failures"] if f["id"] not in still]
        if stale:
            print(f"[metamorphic] {len(stale)} ledger rows now PASS — prune with "
                  f"tools/metamorphic_census.py --write-ledger: " + ", ".join(stale[:10]))
        # a measurement, not a pin

    def test_the_flip_families_never_execute(self, outcomes, ledger):
        """The dangerous class on the instrument: a negated order that RAN,
        a question that ordered. Every such case is in the ledger by name;
        the count is the landing record's and may only fall."""
        executed = [o for o in outcomes if o.verdict and "EXECUTED" in o.verdict]
        known = {f["id"] for f in ledger["failures"]}
        assert all(o.variant.id in known for o in executed)
        assert len(executed) <= sum(1 for f in ledger["failures"] if "EXECUTED" in f["why"])


class TestTheCorpusIsUntouched:
    def test_the_harness_count(self, rows):
        assert len(rows) == 614
