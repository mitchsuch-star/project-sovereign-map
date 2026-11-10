"""T0-I (November 7, 2026) — the benchmark's own arms (`PRE_DEPLOY_PLAN.md`
§2 row S15-R; the November 6 review's harness rows; the rules
`SYSTEMS_REFERENCE.md` §184).

What this file pins:

  * THE RECORD (`tools/_t0i_benchmark_arms.json`, written by
    `tools/_t0i_benchmark_arms.py` from the slice's Mode-A runs):
      - GR-66 — the re-staged shut-out arm: Britain sues at T8 on
        austerlitz AND marengo (naval C4's ≤ T10), ZERO attack_target
        rewrites on all three seeds (the staging defect — a blind
        attack-by-name rewriting Soult's Lisbon march to a pursuit of the
        nearest visible foe — is gone), and on historical the suit is
        structurally absent: Spain destroys Paget outright at T7, Britain
        lands no second corps inside the twelve turns, and a court that
        has never fought France cannot sue her (the GR-18 ruling,
        §181.3 — exhaustion alone cannot sue; §7c standing).
      - SEA — the SF6-X2 re-stage to the post-S14j chest curve: the yard
        at loop 4, the commission at loop 8, the landing quoted with its
        levers at 10 and RESOLVED at sea at 11 (an interception is an
        outcome, not a refusal), no SCRIPT PRECONDITION (naval F2), and
        both diversion quotes at odds = readiness − 25 (naval C1).
      - GR-2 / GR-3 — the DRAMA arm: objections pressed in the dozens
        where the control provoked ONE in forty turns, V2b defiance on
        the fixed line, the chest spent five figures, the refusal rate a
        fraction of the control's 29–40%, and the trust cost written on
        the MARSHALS row.
  * THE STAGING (the scripts' own shapes), so a drive-by edit cannot
    quietly restore the defects the records measure the absence of.
  * THE DIGEST ROWS (DIP-3 / ECON-1) and the sweep's seams (AIF-9 /
    AIF-10) as units, against stub worlds and crafted responses.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

RECORD = REPO / "tools" / "_t0i_benchmark_arms.json"
SCRIPTS = REPO / "tools" / "playtest_scripts"
PY = str(REPO / ".venv" / "Scripts" / "python.exe")
if not Path(PY).exists():  # non-Windows checkout
    PY = sys.executable


@pytest.fixture(scope="module")
def record():
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _loops(name: str) -> dict:
    d = json.loads((SCRIPTS / name).read_text(encoding="utf-8"))
    return {int(k): v for k, v in d["turns"].items()}


# ═══════════════════════════════════════════════════════════════════════
# The record — GR-66, the shut-out arm re-staged
# ═══════════════════════════════════════════════════════════════════════
class TestTheShutOutRecord:
    def test_britain_sues_at_eight_on_austerlitz_and_marengo(self, record):
        shut = record["shut"]
        assert shut["austerlitz"]["britain_sues_turn"] == 8
        assert shut["marengo"]["britain_sues_turn"] == 8

    def test_the_suit_is_inside_naval_c4s_bar(self, record):
        for seed in ("austerlitz", "marengo"):
            assert record["shut"][seed]["britain_sues_turn"] <= 10

    def test_no_clarification_rewrote_an_order_on_any_seed(self, record):
        """The staging defect itself: 'Soult, attack Paget' with the man
        out of sight fell to an attack_target clarification whose first
        answer re-targeted Soult and SET ASIDE the Lisbon march."""
        for seed in ("historical", "austerlitz", "marengo"):
            arm = record["shut"][seed]
            assert arm["attack_target_rewrites"] == 0, (seed, arm)
            assert arm["completed"], seed

    def test_historical_cannot_sue_and_the_record_says_so(self, record):
        """On historical Spain destroys Paget outright at T7 (the T6-T7
        saves: 2,117 men at Lisbon, then gone from the roster), Britain
        lands no second corps inside the arm, and the GR-18 ruling stands:
        a court that has never fought France cannot sue her. The absence
        is the seeded truth, not a staging failure — the march completes
        and the storm lands at T8 regardless."""
        arm = record["shut"]["historical"]
        assert arm["britain_sues_turn"] is None
        assert arm["storm_turn"] == 8

    def test_the_script_stages_no_blind_attack_by_name(self):
        loops = _loops("sr5b_shut_out.json")
        for n in range(1, 13):
            for line in loops.get(n, []):
                assert not any(
                    line.startswith(f"Soult, attack {man}")
                    for man in ("Paget", "Wellesley", "Moore")), (n, line)
        assert "Soult, march to Lisbon" in loops[1]
        assert "Soult, attack Lisbon" in loops[8]


# ═══════════════════════════════════════════════════════════════════════
# The record — SEA re-staged to the chest's curve
# ═══════════════════════════════════════════════════════════════════════
class TestTheSeaRecord:
    def test_every_staged_purchase_lands(self, record):
        sea = record["sea"]
        assert sea["yard_turn"] == 4
        assert sea["commission_turn"] == 8
        assert sea["landing_quoted_turn"] == 10
        assert sea["landing_resolved"] is True
        assert sea["completed"] is True

    def test_no_script_precondition_failed(self, record):
        """Naval F2's own criterion — the October run read SCRIPT
        PRECONDITION because both expedition lines were refused after the
        3,500g commission met an 1,377g chest."""
        assert record["sea"]["precondition_failed"] is False

    def test_the_two_diversion_quotes_price_at_readiness_minus_25(self, record):
        sea = record["sea"]
        assert len(sea["diversion_quotes"]) >= 2
        assert sea["odds_are_readiness_minus_25"] is True
        assert sea["resolved_throws"] >= 2

    def test_the_script_spends_on_the_chests_own_curve(self):
        loops = _loops("sr_exit_chunk5_sea.json")
        assert "build a naval yard in Artois" in loops[4]
        assert "commission Oudinot" in loops[8]
        assert "Oudinot, march to Normandy" in loops[9]
        assert any(line.startswith("land Oudinot") for line in loops[10])
        assert any("confirmed" in line for line in loops[11])


# ═══════════════════════════════════════════════════════════════════════
# The record — GR-2 / GR-3, the drama arm
# ═══════════════════════════════════════════════════════════════════════
class TestTheDramaRecord:
    def test_the_arm_provokes_in_the_dozens(self, record):
        drama = record["drama"]
        assert drama["objection_popups"] >= 10, drama
        assert drama["insists"] >= 10, drama

    def test_the_defiance_road_is_priced_shut_at_full_authority(self, record):
        """The slice's own measured finding (GRD-38, the user's to rule):
        on the committed line every one of the 13 pressed objections rolled
        and OBEYED, because `defiance.py`'s authority tier (−0.10 at ≥ 80)
        prices a MODERATE concern at literally zero (0.05 − 0.10 +
        U(−0.08, 0.08), clamped — a 0.0 roll still obeys) and caps STRONG
        near 0.13; the one real window all slice was Bernadotte's STRONG
        bad-odds ask (+0.10 ability) at 0.12–0.22, and no reachable roll
        fell under it. The pricing table is the record's own evidence —
        chance and the peeked roll per insist, none consumed. A GRD-38
        ruling that reprices defiance re-records this arm; until then the
        zero IS the design's reading, pinned."""
        drama = record["drama"]
        assert drama["defiances"] == 0, drama
        pricing = drama["defiance_pricing"]
        assert len(pricing) == drama["insists"] == 13
        for row in pricing:
            assert row["defies"] is False
            assert row["chance"] <= 0.25, row
            assert row["authority"] >= 80, row
            if row["concern"] == "MODERATE" and row["trust"] > 20:
                assert row["chance"] <= 0.02, row

    def test_the_redemption_arc_is_reached_and_refused(self, record):
        """The pressure's visible V2b consequence on this line: two
        pressed marshals fall to rock-bottom trust and ask for redemption;
        under `--redemption dismiss` the Emperor refuses both and they
        stay in the line."""
        assert record["drama"]["redemptions"] >= 2, record["drama"]

    def test_the_chest_is_spent(self, record):
        assert record["drama"]["gold_spent"] >= 10_000, record["drama"]

    def test_mostly_valid_against_the_open_loop_control(self, record):
        """GR-2's evidence on commanded_full40: 29-40% refused. The drama
        arm stays under half the control's floor."""
        assert record["drama"]["refusal_rate_pct"] <= 15, record["drama"]

    def test_the_trust_cost_is_written_on_the_marshals_row(self, record):
        drama = record["drama"]
        first, last = drama["trust_first_turn"], drama["trust_last_turn"]
        pressed = [w for w in ("Ney", "Murat", "Lannes")
                   if first.get(w) is not None and last.get(w) is not None]
        assert pressed, (first, last)
        assert any(first[w] - last[w] >= 15 for w in pressed), (first, last)

    def test_the_script_is_the_benchmarks_own_arm(self):
        import tools.score_run as score_run
        arm = score_run.ARMS["DRAMA"]
        argv = arm["argv"]
        assert f"{score_run.SCRIPTS}/commanded_provoke40.json" in argv
        assert "insist" in argv and "accept" in argv and "pay" in argv
        assert arm.get("long") is True
        assert "marshal_drama" in arm["feeds"]

    def test_the_script_shape_holds(self):
        loops = _loops("commanded_provoke40.json")
        assert sorted(loops) == list(range(1, 41))
        # The hot window presses the aggressive marshals while the enemy
        # stands at hand; Bernadotte (capture risk) appears only there.
        waits = sum(1 for n in loops for line in loops[n]
                    if line.endswith(", wait"))
        assert waits >= 15
        for n, lines in loops.items():
            for line in lines:
                if line.startswith("Bernadotte"):
                    assert n <= 10, (n, line)
        spends = sum(1 for n in loops for line in loops[n]
                     if line.startswith(("recruit ", "buy ", "grant ")))
        assert spends >= 15


# ═══════════════════════════════════════════════════════════════════════
# VOLTE — read, not re-staged: the beat fires on the live benchmark arm
# ═══════════════════════════════════════════════════════════════════════
class TestTheVolteFiresOnTheLiveArm:
    def test_the_committed_benchmark_arm_carries_the_beat(self):
        """The review's VOLTE row said the commanded script could no longer
        beat Austria so the volte-face could not fire; T0-H's benchmark
        (077efb37) shows it FIRING on the arm's own live line — Austria
        beaten, then courted into alliance at T27, her court turning to
        The Eastern Question. The brief's rule: READ the arm first, then
        re-stage only if still needed. It is not. (The rs27 firing arm is
        a different record — it holds the desperation seam down by design;
        this is the live one.)"""
        md = (REPO / "docs" / "audits" / "score_runs"
              / "2026_11_07_077efb37" / "arms" / "VOLTE"
              / "digest.md").read_text(encoding="utf-8")
        assert ("THE VOLTE-FACE: Austria, beaten and then courted, "
                "takes France's hand") in md


# ═══════════════════════════════════════════════════════════════════════
# LAW-5 — rf3_commanded_enacts asks for the Staff all forty loops
# ═══════════════════════════════════════════════════════════════════════
class TestTheStaffIsAskedAllForty:
    def test_every_loop_asks(self):
        loops = _loops("rf3_commanded_enacts.json")
        for n in range(1, 41):
            assert "enact the Staff" in loops[n], n


# ═══════════════════════════════════════════════════════════════════════
# DIP-3 / ECON-1 — the driver's digest rows, as units
# ═══════════════════════════════════════════════════════════════════════
def _digest(tmp_path):
    import tools.playtest_driver as drv
    return drv.Digest(tmp_path, {"name": "t0i-unit", "seed": "historical",
                                 "llm": "mock", "transport": "in-process",
                                 "policy": {}})


class TestTheTermsRow:
    def test_an_incoming_proposal_states_its_terms(self, tmp_path):
        d = _digest(tmp_path)
        d.proposal_terms({
            "from_nation": "Prussia", "proposal_type": "open_borders",
            "clauses": ["Proposal: Open Borders Agreement",
                        "Clause: free military passage"]})
        md = (tmp_path / "digest.md").read_text(encoding="utf-8")
        assert "TERMS (incoming open_borders from Prussia)" in md
        rows = [json.loads(line) for line in
                io.open(tmp_path / "digest.jsonl", encoding="utf-8")]
        terms = [r for r in rows if r.get("kind") == "proposal_terms"]
        assert terms and terms[0]["clauses"][0].startswith("Proposal:")

    def test_a_dialogue_without_the_envoy_shape_prints_nothing(self, tmp_path):
        d = _digest(tmp_path)
        d.proposal_terms({"type": "settlement_confirm",
                          "clauses": ["peace"]})
        d.proposal_terms({"from_nation": "Prussia",
                          "proposal_type": "open_borders"})
        assert "TERMS (incoming" not in (
            (tmp_path / "digest.md").read_text(encoding="utf-8"))

    def test_the_letter_books_answer_carries_the_clauses(self, tmp_path):
        d = _digest(tmp_path)
        d.envoy_answer({"mailbox_id": 3, "from_nation": "Saxony",
                        "proposal_type": "open_borders",
                        "clauses": ["Clause: open borders"]},
                       "decline", "")
        rows = [json.loads(line) for line in
                io.open(tmp_path / "digest.jsonl", encoding="utf-8")]
        answer = [r for r in rows if r.get("kind") == "envoy_digest_answer"]
        assert answer and answer[0]["clauses"] == ["Clause: open borders"]


class TestTheTreatyLumpIsOnTheBooks:
    RESPONSE = {
        "events": [{"type": "turn_end", "old_turn": 18,
                    "treasury": 5_000, "net": 100, "materiel": 0}],
        "morning_dispatch": {"situation": {"treasury_delta": 100}},
    }

    def test_a_named_lump_is_explained(self, tmp_path):
        """ECON-1's own case (the NAV1T-H T18 OFF THE BOOKS −1,000g):
        France's offered indemnity leaves the chest when the court accepts
        at the rollover — the ratification summary the popups carry names
        it, so it is on the books now."""
        d = _digest(tmp_path)
        response = dict(self.RESPONSE)
        response["proposal_result"] = {"peace_ratification_summary": {
            "gold_received": 0, "gold_paid": 1_000}}
        # before 4900, after 4000: the chest moved −900 = −1,000 lump
        # + net 100; the window opened at treasury − net = 4,900.
        d.chest_window(response, 4_900, 4_000)
        rows = [json.loads(line) for line in
                io.open(tmp_path / "digest.jsonl", encoding="utf-8")]
        window = [r for r in rows if r.get("kind") == "chest_window"][0]
        assert window["treaty_lump"] == -1_000
        assert window["off_books"] == 0
        assert "OFF THE BOOKS" not in (
            (tmp_path / "digest.md").read_text(encoding="utf-8"))

    def test_an_unnamed_lump_still_reads_off_the_books(self, tmp_path):
        d = _digest(tmp_path)
        d.chest_window(dict(self.RESPONSE), 4_900, 4_000)
        rows = [json.loads(line) for line in
                io.open(tmp_path / "digest.jsonl", encoding="utf-8")]
        window = [r for r in rows if r.get("kind") == "chest_window"][0]
        assert window["treaty_lump"] == 0
        assert window["off_books"] == -1_000
        assert "OFF THE BOOKS" in (
            (tmp_path / "digest.md").read_text(encoding="utf-8"))

    # ── GR-11's own evidence (closed November 9, 2026): T0-I's arm read a
    # PEACE's summary; the row's digests showed a VASSALAGE ("Austria has
    # accepted our Vassalage! You paid Austria 750 gold from the treasury.")
    # — no peace, no summary — still reading OFF THE BOOKS −150 / −124 / −750
    # on the review's own repro at HEAD. The treaty event carries the figure
    # now (`receipt_gold`), and the window reads every treaty the rollover
    # signed.
    def _window(self, tmp_path, response):
        d = _digest(tmp_path)
        d.chest_window(response, 4_900, 4_000)
        rows = [json.loads(line) for line in
                io.open(tmp_path / "digest.jsonl", encoding="utf-8")]
        md = (tmp_path / "digest.md").read_text(encoding="utf-8")
        return [r for r in rows if r.get("kind") == "chest_window"][0], md

    def test_a_treaty_that_is_no_peace_is_explained(self, tmp_path):
        response = dict(self.RESPONSE)
        response["events"] = list(response["events"]) + [{
            "type": "diplomatic_treaty_signed", "target": "Austria",
            "treaty_type": "vassalage", "receipt_gold": -1_000,
            "receipt_lines": ["You paid Austria 1,000 gold from the treasury."]}]
        response["proposal_result"] = {
            "outcome": "ACCEPT",
            "message": "Austria has accepted our Vassalage! "
                       "You paid Austria 1,000 gold from the treasury."}
        window, md = self._window(tmp_path, response)
        assert window["treaty_lump"] == -1_000
        assert window["off_books"] == 0
        assert "OFF THE BOOKS" not in md

    def test_every_treaty_of_the_rollover_is_summed(self, tmp_path):
        """The popup slot holds ONE treaty; the events hold them all — and a
        lump paid IN (an AI court's sweetener) offsets one paid out."""
        response = dict(self.RESPONSE)
        response["events"] = list(response["events"]) + [
            {"type": "diplomatic_treaty_signed", "target": "Bavaria",
             "treaty_type": "vassalage", "receipt_gold": -1_150},
            {"type": "diplomatic_treaty_signed", "target": "Saxony",
             "treaty_type": "open_borders", "receipt_gold": 150},
            {"type": "diplomatic_treaty_signed", "target": "Baden",
             "treaty_type": "open_borders"}]
        window, md = self._window(tmp_path, response)
        assert window["treaty_lump"] == -1_000
        assert window["off_books"] == 0

    def test_one_peace_is_counted_once(self, tmp_path):
        """A peace accepted in transit rides BOTH the treaty event and the
        popup (`world_state` copies the summary onto the popup) — the
        window reads the event and leaves the copy alone."""
        summary = {"gold_received": 0, "gold_paid": 1_000}
        response = dict(self.RESPONSE)
        response["events"] = list(response["events"]) + [{
            "type": "diplomatic_treaty_signed", "target": "Russia",
            "treaty_type": "peace", "peace_ratification_summary": summary,
            "receipt_gold": -1_000}]
        response["proposal_result"] = {"peace_ratification_summary": summary}
        window, md = self._window(tmp_path, response)
        assert window["treaty_lump"] == -1_000
        assert window["off_books"] == 0

    def test_the_lump_reader_survives_any_shape(self):
        import tools.playtest_driver as drv
        assert drv.rollover_treaty_lump(None) == 0
        assert drv.rollover_treaty_lump({}) == 0
        assert drv.rollover_treaty_lump({"events": [None, "x", {"type": "battle"}]}) == 0
        assert drv.rollover_treaty_lump(
            {"events": [{"type": "diplomatic_treaty_signed",
                         "receipt_gold": None}]}) == 0


# ═══════════════════════════════════════════════════════════════════════
# AIF-9 / AIF-10 — the sweep's seams
# ═══════════════════════════════════════════════════════════════════════
class TestTheSweepsSeams:
    def test_the_documented_command_line_imports_without_pythonpath(self):
        """AIF-9: `python tools/ai_v_sweep.py --run` boots with
        sys.path[0] = tools/, and the --run branch's first statement
        imports tools._seams_env — it died on ModuleNotFoundError before
        reaching its own PYTHONHASHSEED guard. The guard speaking IS the
        import having worked."""
        env = {k: v for k, v in os.environ.items()
               if k not in ("PYTHONPATH", "PYTHONHASHSEED")}
        proc = subprocess.run(
            [PY, "tools/ai_v_sweep.py", "--run", "--turns", "1"],
            cwd=str(REPO), env=env, capture_output=True, text=True,
            timeout=120)
        assert proc.returncode == 2, (proc.returncode, proc.stderr[-400:])
        assert "PYTHONHASHSEED" in proc.stderr
        assert "ModuleNotFoundError" not in proc.stderr

    def test_the_capture_reads_frances_own_fate(self):
        """AIF-10: provinces, laws, satellites per turn (men already ride
        `strength`, gold `gold`) — read off the test-fixture world."""
        from backend.models.world_state import WorldState
        from tools.ai_v_sweep import RunCapture
        world = WorldState()
        fate = RunCapture(world)._france_fate()
        assert fate["provinces"] == len(world.get_nation_regions("France"))
        assert isinstance(fate["laws"], list)
        assert isinstance(fate["satellites"], dict)
        for vassal, loyalty in fate["satellites"].items():
            assert world.vassals[vassal].get("lord") == "France"
            assert isinstance(loyalty, int)

    def test_the_per_turn_row_carries_the_fate_block(self):
        import inspect

        from tools.ai_v_sweep import RunCapture
        src = inspect.getsource(RunCapture.capture_turn)
        assert '"france": self._france_fate()' in src
