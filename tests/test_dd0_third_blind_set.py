"""DD-0 S3 "The Command Road" — instrument 3, THE THIRD BLIND AUTHOR SET
(October 10, 2026; PRE_DEPLOY_PLAN.md §3.0; memo
docs/audits/UNREHEARSED_CENSUS_2026_10_10.md; rules SYSTEMS_REFERENCE.md §102).

300 orders written BLIND by a third author who never saw the corpus, the
tests, the docs or the two earlier blind files — only what a player sees on
the 1805 boot screen and the judge's family names — each line run on a
FRESH boot board through the real `POST /command`, keyless and keyed, read
by the ONE judge (`tools/_score_probes.py`) and carrying its parse trace
(§100). The records are committed under `docs/audits/unrehearsed/` and are
re-read by the shipping judge here, so a judge that changes re-reads the
evidence.

Pinned: the blind file's shape and pledge; every row of the records carries
a trace that ends on the reply; the DANGEROUS classes on the committed
records at their measured count as a lower-only ratchet (the memo splits
them by hand into the parser's and the judge's — both are S4's); the
`as_meant` reading recorded as S4's baseline (a measurement line, not a
pin — DD-0's done-when is ≥ 85 %, read on a FRESH set, never this one).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BLIND = REPO_ROOT / "tools" / "playtest_scripts" / "unrehearsed_2026_10_10_third.json"
RECORDS = REPO_ROOT / "docs" / "audits" / "unrehearsed"
KEYLESS = RECORDS / "2026_10_10_third_keyless.json"
KEYED = RECORDS / "2026_10_10_third_keyed.json"

# The landing's readings (October 10, 2026). The dangerous classes are a
# lower-only ratchet; `as_meant` is the baseline S4 is measured against.
KEYLESS_DANGEROUS_CAP = {"misread": 8, "executed_when_refusal_meant": 11}
KEYED_DANGEROUS_CAP = {"misread": 10, "executed_when_refusal_meant": 10}
KEYLESS_AS_MEANT_AT_LANDING = 137
KEYED_AS_MEANT_AT_LANDING = 152


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


class TestTheBlindFile:
    def test_shape(self):
        d = _load(BLIND)
        assert len(d["orders"]) == 300
        lines = [o["line"] for o in d["orders"]]
        assert len(set(lines)) == 300, "every line unique"
        for o in d["orders"]:
            assert o["intended"]["action"] and o["intended"].get("note")
            assert "marshal" in o["intended"] and "target" in o["intended"]
        assert "blind" in d["_note"].lower() and "never edited" in d["_note"].lower()
        assert "questions" not in d  # orders only — the spec's third set

    def test_the_traps_and_the_registers(self):
        d = _load(BLIND)
        assert sum(1 for o in d["orders"] if o["intended"]["action"] == "refuse") >= 30
        families = {o["intended"]["action"] for o in d["orders"]}
        assert len(families) >= 30
        lines = " || ".join(o["line"] for o in d["orders"])
        # a few of the registers the brief asked for
        assert any(c.islower() and " " in c and c == c.lower() for c in
                   (o["line"] for o in d["orders"])), "a lowercase line"
        assert "please" in lines.lower() and " — " in lines and " if " in lines.lower()


class TestTheRecords:
    @pytest.mark.parametrize("path", [KEYLESS, KEYED], ids=["keyless", "keyed"])
    def test_every_row_carries_a_trace_that_ends_on_the_reply(self, path):
        if not path.exists():
            pytest.skip(f"{path.name} not recorded")
        d = _load(path)
        assert d["blind"] == "unrehearsed-2026-10-10-third"
        assert len(d["rows"]) == 300
        for r in d["rows"]:
            assert r["kind"] == "order"
            trace = r.get("parse_trace")
            assert trace, r["line"]
            assert trace[0]["stage"] == "typed" and trace[-1]["stage"] == "reply"

    def test_the_records_are_the_judges_own_reading(self):
        """The committed classes are what the shipping judge reads today —
        a judge that changes must re-read the evidence (the Oct 3 rule)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "unrehearsed_census_for_dd0", REPO_ROOT / "tools" / "unrehearsed_census.py")
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
        d = _load(path)
        t = d["totals"]["order"]
        for cls, cap in caps.items():
            assert t.get(cls, 0) <= cap, (cls, t.get(cls))
        assert set(d["dangerous"]) == {r["line"] for r in d["rows"] if r["class"] in caps}

    def test_the_three_real_executions_are_named(self):
        """The memo's by-hand split: of the judge's dangerous rows, these
        three RAN something the player did not mean (the rest are honest
        replies the judge's shape list does not know — DD0-8). Pinned by
        line so S4's fix is read on the same evidence."""
        d = _load(KEYLESS)
        by_line = {r["line"]: r for r in d["rows"]}
        for line in ("Ney, attack Davout", "Ney, Davout, Soult, everyone — attack everything",
                     "Ney, attack Mack and also do not attack Mack"):
            assert by_line[line]["class"] == "executed_when_refusal_meant", line
            assert by_line[line]["success"] is True

    def test_the_baseline_is_recorded(self):
        """A measurement, not a pin: S4 is read against it on a FRESH set."""
        for path, at in ((KEYLESS, KEYLESS_AS_MEANT_AT_LANDING), (KEYED, KEYED_AS_MEANT_AT_LANDING)):
            d = _load(path)
            print(f"[dd0] third blind set {d['llm']} as_meant {d['totals']['order'].get('as_meant')} / 300 "
                  f"(at landing {at})")

    def test_the_keyed_arm_consulted_the_model(self):
        if not KEYED.exists():
            pytest.skip("keyed record not recorded")
        d = _load(KEYED)
        assert d["llm"] == "anthropic" and d["live_parses"] > 0
