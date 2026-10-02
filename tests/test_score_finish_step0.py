"""Score Finish Step 0 — SF-0 "The ledger tells the truth" + SF-M "The instrument".

`docs/SCORE_FINISH_SPEC.md` §3 Step 0. The pins hold three things:

  * the CENSUS reads the ledgers by its stated vocabulary — the SF-0 marks
    (a struck id, an OPEN REMAINDER, a RE-HOMED row) and the SF tag every
    live row carries, so `--by-pillar` can hand the P1s to the rule;
  * the INSTRUMENT's frozen rule (§4.4) and its coverage reading, the
    checklist's shape (Appendix A: 14 pillars × 8 items, two floors and six
    ceilings each), and that every AUTO/PROBE item resolves to a reader;
  * the DRIVER fields SF-M added (the headline's class, the marshal's voice
    line, the ledger's bill notes) and the arm scripts the fixed benchmark
    names (the DL lines, the laws arm's SF-V3 fix, the blind HOLD shape).

Every pin is falsifiable: the sweep `tools/_sweep_score_finish_step0.json`
mutates each production line it binds to.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import defect_census as census  # noqa: E402
from tools import score_run as SR  # noqa: E402


def _load_driver():
    spec = importlib.util.spec_from_file_location("_sf_driver", ROOT / "tools" / "playtest_driver.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ═══════════════════════════ SF-0 — the census ═══════════════════════════
class TestTheCensusVocabulary:
    def test_a_struck_id_is_closed(self):
        assert census.classify(["~~**PC15-1**~~", "P1", "text", "owner"], False, False) == "closed"

    def test_an_open_remainder_is_partial_even_beside_a_fixed_word(self):
        cells = ["⚠ **NPC-12**", "P2", "FIXED at the acceptance lines", "OPEN REMAINDER (SF-0): the census"]
        assert census.classify(cells, False, False) == "partial"

    def test_a_re_homed_row_is_disposed(self):
        cells = ["**WO-D4**", "the question", "RE-HOMED → the Victory & Objectives gate (SF-0)"]
        assert census.classify(cells, False, False) == "disposed"

    def test_a_bare_row_stays_open(self):
        assert census.classify(["**RS-1**", "P1", "text", "owner"], False, False) == "OPEN"

    def test_the_tag_parses_step_slice_and_pillar(self):
        out = census._parse_tag("step=2 · SR-6a (with RS-19) · pillar=diplomacy")
        assert out == {"step": "2", "slice": "SR-6a (with RS-19)", "pillar": "diplomacy"}

    def test_by_pillar_lists_the_untagged_and_the_p1s(self):
        rows = [{"id": "A-1", "pillar": "ending", "severity": "P1"},
                {"id": "A-2", "pillar": "ending", "severity": "P2"},
                {"id": "A-3", "pillar": "", "severity": "P3"},
                {"id": "A-4", "pillar": "not-a-pillar", "severity": ""}]
        view = census.by_pillar(rows)
        assert view["pillars"]["ending"] == {"open": 2, "p1": ["A-1"], "p2": 1, "rows": ["A-1", "A-2"]}
        assert view["untagged"] == ["A-3", "A-4"]


class TestTheLedgersTellTheTruth:
    """SF-0's done-when, read off the committed ledgers."""

    @pytest.fixture(scope="class")
    def rows(self):
        return census.collect()

    def test_every_open_row_carries_an_sf_tag(self, rows):
        open_rows = [r for r in rows.values() if r["state"] in ("OPEN", "partial")]
        view = census.by_pillar(open_rows)
        assert view["untagged"] == [], view["untagged"]
        assert open_rows, "the census found no open rows at all — the ledgers moved"

    def test_the_stale_rows_are_struck(self, rows):
        for rid in ("PC15-1", "PC15-10", "GEV-5", "EAS-4", "S5-1", "XR-4", "CX5-L5-N1", "L2-3"):
            assert rows[rid]["state"] == "closed", rid

    def test_the_notes_are_disposed_not_open(self, rows):
        for rid in ("CA9-P2", "CA9-P3", "CX5-L5-N3"):
            assert rows[rid]["state"] == "disposed", rid

    def test_npc_12_keeps_its_open_remainder(self, rows):
        assert rows["NPC-12"]["state"] == "partial"
        assert rows["NPC-12"]["pillar"] == "combat_legibility"

    def test_the_design_rows_owned_elsewhere_are_re_homed(self, rows):
        for rid in ("WO-D4", "HC-D1", "EWC-D2", "S5-D3", "VP-D7", "VP-D3"):
            assert rows[rid]["state"] == "disposed", rid

    def test_the_six_twelve_dispositions(self, rows):
        assert rows["WO-D7"]["state"] == "disposed"
        assert rows["WO-D8"]["state"] == "closed"
        assert rows["WO-D13"]["state"] == "closed"
        assert rows["EWC-D3"]["state"] == "disposed"
        assert rows["VP-D8"]["state"] == "disposed"
        assert rows["IQ6-D2"]["state"] == "OPEN" and rows["IQ6-D2"]["step"] == "3"

    def test_the_heading_form_design_rows_are_counted(self, rows):
        # Step 0 read NPC-D1 / NPC-D4 OPEN; Step 2 BUILT both (Oct 2, 2026),
        # so the heading-form rows are now counted as CLOSED — the point of
        # the pin (the table form is read at all, with its pillar) stands.
        assert rows["NPC-D1"]["state"] == "closed" and rows["NPC-D1"]["pillar"] == "narration"
        assert rows["NPC-D4"]["state"] == "closed"
        assert rows["NPC-D2"]["state"] == "disposed" and rows["NPC-D3"]["state"] == "disposed"

    def test_the_two_p1s_are_where_the_rule_reads_them(self, rows):
        """Step 0 read the two P1s in their pillars' p1 lists (the rule's
        cap). Step 1 CLOSED them (Sept 29, 2026): the reader now shows them
        gone from the open view, and the rows carry their closing state — so
        the ending's and diplomacy's caps are lifted where the rule reads."""
        open_rows = [r for r in rows.values() if r["state"] in ("OPEN", "partial")]
        view = census.by_pillar(open_rows)
        assert "RS-1" not in (view["pillars"].get("diplomacy") or {}).get("p1", [])
        assert "RS-2" not in (view["pillars"].get("ending") or {}).get("p1", [])
        assert rows["RS-1"]["state"] not in ("OPEN", "partial")
        assert rows["RS-2"]["state"] not in ("OPEN", "partial")
        # the reader itself still hands a P1 to the rule when one is open
        staged = [dict(rows["RS-2"], state="OPEN", severity="P1", pillar="ending")]
        assert "RS-2" in census.by_pillar(staged)["pillars"]["ending"]["p1"]


# ═══════════════════════════ SF-M — the rule ═══════════════════════════
class TestTheFrozenRule:
    @pytest.mark.parametrize("ceilings,expected", [(0, 5.5), (1, 6.0), (2, 6.5), (3, 7.0), (4, 7.5), (5, 8.0), (6, 8.5)])
    def test_floors_green_no_p1(self, ceilings, expected):
        assert SR.score_from_items(True, True, ceilings) == expected

    @pytest.mark.parametrize("ceilings,expected", [(0, 5.0), (2, 5.5), (4, 6.0), (6, 6.0)])
    def test_otherwise_quarter_steps_capped_at_six(self, ceilings, expected):
        assert SR.score_from_items(False, True, ceilings) == expected
        assert SR.score_from_items(True, False, ceilings) == expected

    def _items(self, floors, ceilings, unmeasured=0):
        items = []
        for i, ok in enumerate(floors, 1):
            items.append({"id": f"F{i}", "kind": "AUTO", "measured": True, "pass": ok})
        for i, ok in enumerate(ceilings, 1):
            items.append({"id": f"C{i}", "kind": "AUTO", "measured": True, "pass": ok})
        for j in range(unmeasured):
            items.append({"id": f"C{len(ceilings) + j + 1}", "kind": "EYES", "measured": False, "pass": None})
        return items

    def test_eight_measured_reads_one_score(self):
        s = SR.pillar_score(self._items([True, True], [True, True, True, False, False, False]), [])
        assert s["exercised"] and s["score"] == 7.0 and s["reading"] == "7.00"

    def test_seven_measured_reads_a_range(self):
        s = SR.pillar_score(self._items([True, True], [True, True, True, False, False], unmeasured=1), [])
        assert s["exercised"] and s["score"] is None and (s["low"], s["high"]) == (7.0, 7.5)
        assert s["reading"] == "7.00–7.50"

    def test_five_measured_is_not_exercised(self):
        s = SR.pillar_score(self._items([True, True], [True, True, True], unmeasured=3), [])
        assert s["exercised"] is False and s["reading"] == "NOT EXERCISED"

    def test_a_verified_open_p1_caps_the_pillar(self):
        s = SR.pillar_score(self._items([True, True], [True] * 6), ["RS-2"])
        assert s["low"] == 6.0 and s["open_p1"] == ["RS-2"]

    def test_the_directional_averages_the_low_ends_of_exercised_pillars(self):
        scores = {"a": {"exercised": True, "low": 7.0}, "b": {"exercised": True, "low": 6.0},
                  "c": {"exercised": False, "low": 5.0}}      # a NOT EXERCISED pillar is never averaged
        d = SR.directional(scores)
        assert d["value"] == 6.5 and d["over"] == "2/3"


class TestTheChecklist:
    @pytest.fixture(scope="class")
    def checklist(self):
        return SR.load_checklist(SR.CHECKLIST_DEFAULT)

    def test_fourteen_pillars_of_eight_items(self, checklist):
        assert checklist["version"] == 1
        assert len(checklist["pillars"]) == 14
        for p in checklist["pillars"]:
            ids = [i["id"] for i in p["items"]]
            assert ids == ["F1", "F2", "C1", "C2", "C3", "C4", "C5", "C6"], p["key"]
            assert all(i["kind"] in ("AUTO", "PROBE", "EYES") for i in p["items"])
        assert sum(len(p["items"]) for p in checklist["pillars"]) == 112

    def test_every_pillar_at_target_is_the_directional_seven_and_a_half(self, checklist):
        assert sum(p["target_ceilings"] for p in checklist["pillars"]) == 56
        for p in checklist["pillars"]:
            assert SR.score_from_items(True, True, p["target_ceilings"]) >= 7.0

    def test_every_measurable_item_has_a_reader(self, checklist):
        missing = []
        for p in checklist["pillars"]:
            for i in p["items"]:
                if i["kind"] != "EYES" and SR.reader_for(p["key"], i["id"], i["kind"]) is None:
                    missing.append(f"{p['key']}.{i['id']}")
        assert missing == []

    def test_every_probe_name_exists(self):
        from tools import _score_probes as P
        missing = [k for k, name in SR.PROBES.items() if not callable(getattr(P, name, None))]
        assert missing == []

    def test_the_pillar_keys_are_the_census_vocabulary(self, checklist):
        assert {p["key"] for p in checklist["pillars"]} <= set(census.PILLARS)


class TestTheArmReader:
    def test_blocks_and_records(self, tmp_path):
        (tmp_path / "meta.json").write_text(json.dumps({"status": "completed", "unknown_blockers": []}), encoding="utf-8")
        (tmp_path / "digest.md").write_text("# d\n\n## Turn 1 — x\n- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (1) vs Mack (2) at Swabia — the balance of force looks favorable.\n"
                                            "  - ⚔ Ney (lost 100) vs Mack (lost 900) — x\n\n## Turn 2 — y\n- LEDGER treasury 1\n", encoding="utf-8")
        (tmp_path / "digest.jsonl").write_text('{"kind": "turn", "turn": 1}\n{"kind": "dispatch", "headline": "h", "headline_class": "own_broken"}\n'
                                               '{"kind": "turn", "turn": 2}\n', encoding="utf-8")
        arm = SR.Arm(tmp_path)
        assert [t for t, _ in arm.blocks()] == [1, 2]
        assert arm.status == "completed" and len(arm.by_turn()) == 2
        cmds = SR._cmd_blocks(arm)
        assert cmds[0]["ok"] and SR._band(cmds[0]) == "favorable" and any("⚔" in s for s in cmds[0]["sub"])

    def test_a_truncated_band_word_still_reads(self):
        assert SR._band({"head": "the balance of force looks unfavora…", "sub": []}) == "unfavorable"
        assert SR._band({"head": "the balance of force looks favora…", "sub": []}) == "favorable"


# ═══════════════════════════ SF-M — the driver fields ═══════════════════════════
class TestTheDriverFields:
    @pytest.fixture
    def digest(self, tmp_path):
        drv = _load_driver()
        meta = {"name": "t", "seed": "historical", "llm": "mock", "transport": "in-process", "policy": {}}
        return drv.Digest(tmp_path, meta), tmp_path

    def _records(self, path):
        return [json.loads(l) for l in (path / "digest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_the_dispatch_record_carries_the_headline_class(self, digest):
        d, path = digest
        d.dispatch("Sire — a headline", headline_class="own_broken")
        d.dispatch("Sire — another")
        recs = [r for r in self._records(path) if r["kind"] == "dispatch"]
        assert recs[0]["headline_class"] == "own_broken"
        assert "headline_class" not in recs[1]          # absent → the pre-SF-M record

    def test_the_battle_record_carries_the_marshals_voice(self, digest):
        d, path = digest
        report = {"casualty_summary": {"attacker_name": "Ney", "attacker_casualties": 100, "defender_name": "Mack", "defender_casualties": 900},
                  "marshal_voice": {"name": "Ney", "line": "They stood, Sire. Briefly."}}
        d.battle(report)
        d.battle({"casualty_summary": {"attacker_name": "Ney", "attacker_casualties": 1, "defender_name": "Mack", "defender_casualties": 2}})
        recs = [r for r in self._records(path) if r["kind"] == "battle"]
        assert recs[0]["voice"]["line"] == "They stood, Sire. Briefly."
        assert "voice" not in recs[1]

    def test_the_ledger_record_carries_the_bill_notes(self, digest):
        d, path = digest
        d.ledger_line(100, 10, 5, provinces=28, economy={"upkeep_note": "paid for the men", "state_charges_delta_note": "", "net": 10})
        d.ledger_line(100, 10, 5, provinces=28, economy={"net": 10})
        recs = [r for r in self._records(path) if r["kind"] == "ledger"]
        assert recs[0]["bill_notes"] == {"upkeep_note": "paid for the men"}
        assert "bill_notes" not in recs[1]


# ═══════════════════════════ SF-M — the arms ═══════════════════════════
class TestTheArmScripts:
    def test_the_laws_arm_types_the_staff_every_loop_from_three(self):
        d = json.loads((ROOT / "tools/playtest_scripts/sr_exit_chunk5_laws.json").read_text(encoding="utf-8"))
        for loop in range(3, 11):
            assert d["turns"][str(loop)].count("enact the Staff") == 1, loop
        for loop in ("1", "2"):
            assert "enact the Staff" not in d["turns"][loop]

    def test_every_docked_line_is_typed_on_the_dl_arm(self):
        d = json.loads((ROOT / "tools/playtest_scripts/score_docked_lines.json").read_text(encoding="utf-8"))
        typed = {l for lines in d["turns"].values() for l in lines}
        for row, lines in d["dl_lines"].items():
            for line in lines:
                assert line in typed, (row, line)

    def test_the_hold_arm_is_twenty_and_twenty(self):
        p = ROOT / "tools/playtest_scripts" / SR.HOLD_SCRIPT
        d = json.loads(p.read_text(encoding="utf-8"))
        q, o = d["hold"]["questions"], d["hold"]["orders"]
        assert len(q) == 20 and len(o) == 20
        assert d["turns"]["1"] == [x["line"] for x in q] and d["turns"]["2"] == [x["line"] for x in o]
        assert all(set(x["intended"]) >= {"action", "marshal"} for x in o)

    def test_the_congress_arm_replays_the_hand_campaigns_save(self):
        assert (ROOT / SR.T24_SAVE).exists()
        argv = SR.ARMS["CONG"]["argv"]
        assert "--from-save" in argv and SR.T24_SAVE in argv and "summon the congress" in json.loads(
            (ROOT / "tools/playtest_scripts/score_congress_sitting.json").read_text(encoding="utf-8"))["turns"]["1"]

    def test_the_benchmark_names_every_arm_the_checklist_reads(self):
        checklist = SR.load_checklist(SR.CHECKLIST_DEFAULT)
        named = {a for p in checklist["pillars"] for i in p["items"] for a in i["arms"]}
        known = set(SR.ARMS) | {"FLAG", "SUITE", "PEVAL", "AIV", "CLI", "AGD", "OP-LIVE", "*"}
        assert named <= known, named - known
