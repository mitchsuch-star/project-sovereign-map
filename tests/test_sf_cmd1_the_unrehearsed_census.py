"""SF-CMD-1 "The unrehearsed line" — part (i), THE CENSUS (SCORE_FINISH_SPEC.md
§3 Step 4, October 3, 2026; rules SYSTEMS_REFERENCE.md §87).

The held-out census: 150 orders + 150 questions written BLIND (an author
that never saw the corpus, the tests or the docs — only the roster, the map
and the verb families), each line run on a FRESH 1805 boot board through
the real `POST /command`, keyless and keyed, and every reply read by the ONE
judge the HOLD arm uses. The measured records are committed
(`docs/audits/unrehearsed/2026_10_03_{keyless,keyed}.json`); the fixes the
census sizes are part (ii) and Chunk 3b.

Pinned here: the blind file's shape; the one judge (its constants are the
HOLD reader's — no inline copy survives); the judge's classes on the reply
shapes that fooled its first draft; and the two committed records' DANGEROUS
classes at zero (nothing the player did not mean was executed, on either
arm) — the worklist counts are measurements, not pins.
"""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BLIND = REPO_ROOT / "tools" / "playtest_scripts" / "unrehearsed_2026_10_03.json"
RECORDS = REPO_ROOT / "docs" / "audits" / "unrehearsed"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


census = _load("unrehearsed_census_for_cmd1", "tools/unrehearsed_census.py")
probes = _load("score_probes_for_cmd1", "tools/_score_probes.py")


class TestTheBlindFile:
    def test_shape(self):
        d = json.loads(BLIND.read_text(encoding="utf-8"))
        assert len(d["orders"]) == 150 and len(d["questions"]) == 150
        lines = [o["line"] for o in d["orders"]] + [q["line"] for q in d["questions"]]
        assert len(set(lines)) == 300, "every line unique"
        for o in d["orders"]:
            assert o["intended"]["action"] and o["intended"].get("note")
        assert "blind" in d["_note"].lower() and "never edited" in d["_note"].lower()

    def test_the_deliberate_traps_are_present(self):
        d = json.loads(BLIND.read_text(encoding="utf-8"))
        lines = " || ".join(o["line"] for o in d["orders"]).lower()
        for trap in ("zorglub", "atlantis", "hunt mack down", "bernadote", "we're", "nobody", "if ", "then "):
            assert trap in lines, trap
        assert sum(1 for o in d["orders"] if o["intended"]["action"] == "refuse") >= 10


class TestTheOneJudge:
    def test_the_hold_reader_uses_the_module_constants(self):
        src = (REPO_ROOT / "tools" / "_score_probes.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == "command_c3_hold_orders")
        names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
        assert {"ACTION_WORDS", "BOARD_GATE_RX", "REFUSED_RX"} <= names
        # no inline regex literal of the old shape survives in the reader
        literals = [n.value for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        assert not any("No administrative actions" in s for s in literals)
        assert probes.MISREAD_RX is probes.REFUSED_RX and probes._ACTION_WORDS is probes.ACTION_WORDS

    @pytest.mark.parametrize("intended,reply,expected", [
        ({"action": "move", "marshal": "Soult"}, {"success": True, "message": "Soult moves from Lorraine to Rhineland"}, "as_meant"),
        ({"action": "diplomacy", "marshal": "state"}, {"success": True, "message": "Sire — the state of Europe, plainly told."}, "as_meant"),
        ({"action": "fortify", "marshal": "Ney"}, {"success": True, "message": "Which marshal shall carry out this order, Sire?"}, "asked"),
        ({"action": "move", "marshal": "Davout"}, {"success": True, "message": "Davout respectfully raises concerns: 'That road to Swabia runs through enemy country, Sire.'"}, "asked"),
        ({"action": "recruit", "marshal": "Murat"}, {"success": False, "message": "Murat's levy: Berthier shakes his head. 'The treasury cannot support this, Sire. Need 1504 gold, have 800.'"}, "board_refusal"),
        # the HOLD rule: a board refusal that names NEITHER the man nor the
        # order is read as the parser's, not the board's (the treasury refusal
        # names no marshal today — SF-CMD-1-W10's note)
        ({"action": "recruit", "marshal": "Murat"}, {"success": False, "message": "Berthier shakes his head. 'The treasury cannot support this, Sire. Need 1504 gold, have 800.'"}, "honest_refusal"),
        ({"action": "enact", "marshal": "state"}, {"success": False, "message": "The Grand Quartier Général costs 9,000 gold; the treasury holds 800."}, "board_refusal"),
        ({"action": "attack", "marshal": "Ney"}, {"success": False, "message": "Berthier sets down his pen. \"Sire, that is a contingency, not an order\""}, "honest_refusal"),
        ({"action": "pursue", "marshal": "Murat"}, {"success": True, "message": "Cannot find 'Mack Down' to pursue."}, "honest_refusal"),
        ({"action": "fortify", "marshal": "Ney"}, {"success": True, "message": "Berthier sets down his pen. \"I cannot answer that from the dispatches, Sire.\""}, "shrug"),
        ({"action": "refuse", "marshal": "Zorglub"}, {"success": True, "message": "There is no Marshal 'Zorglub' in the order of battle, Sire. Whom did you intend?"}, "refused_as_meant"),
        ({"action": "refuse", "marshal": "state"}, {"success": True, "message": "Sire, I am a diplomat, not a general. Perhaps you meant to address one of your marshals?"}, "refused_as_meant"),
        ({"action": "refuse", "marshal": "state"}, {"success": True, "message": "Cannot build in Swabia — not controlled by France"}, "refused_as_meant"),
        ({"action": "refuse", "marshal": "Ney"}, {"success": True, "message": "Ney moves from Rhineland to Swabia"}, "executed_when_refusal_meant"),
        ({"action": "hold", "marshal": "Ney"}, {"success": True, "message": "Ney moves from Rhineland to Swabia"}, "misread"),
    ])
    def test_the_classes(self, intended, reply, expected):
        assert census.classify_order(intended, reply) == expected

    def test_a_question_is_answered_or_shrugged(self):
        assert census.classify_question({"message": "Mack of Austria was reported at Swabia — large force."}) == "answered"
        assert census.classify_question({"message": "Berthier sets down his pen. \"I cannot answer that from the dispatches, Sire.\""}) == "shrug"
        assert census.classify_question({"message": ""}) == "shrug"


class TestTheCommittedRecords:
    @pytest.mark.parametrize("name", ["2026_10_03_keyless.json", "2026_10_03_keyed.json"])
    def test_nothing_the_player_did_not_mean_was_executed(self, name):
        rec = json.loads((RECORDS / name).read_text(encoding="utf-8"))
        assert len(rec["rows"]) == 300
        # the record is read by the judge that ships, not the one it was written with
        rec = census.reclassify(rec)
        assert rec["dangerous"] == [], rec["dangerous"]
        assert rec["totals"]["order"].get("misread", 0) == 0
        assert rec["totals"]["order"].get("executed_when_refusal_meant", 0) == 0
        assert rec["totals"]["order"].get("as_meant", 0) >= 50

    def test_the_keyed_arm_consulted_the_model(self):
        keyed = json.loads((RECORDS / "2026_10_03_keyed.json").read_text(encoding="utf-8"))
        keyless = json.loads((RECORDS / "2026_10_03_keyless.json").read_text(encoding="utf-8"))
        assert keyed["llm"] == "anthropic" and keyed["live_parses"] > 0
        assert keyless["llm"] == "mock" and keyless["live_parses"] == 0
