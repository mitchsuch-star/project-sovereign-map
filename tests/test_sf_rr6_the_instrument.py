"""Score Finish Step 9, SF-RR6 "the instrument reads what the player sees"
(October 21, 2026; rules SYSTEMS_REFERENCE.md §141; the re-reads and their
deltas `docs/audits/score_runs/2026_10_21_rr6/README.md`).

Every reader misread reproduced on the archived digest that carries it before
a line was written:

    combat C5: 46 raw keys on the final reading, 124 on the baseline, every
      one in the enemy-phase `message` the dialog never renders; the ⚔ and
      MUSTER lines carry none                                  (SFR-I7, SFR-I2)
    drama C5: "Lannes's claim is 21 turns in arrears" unread — the reader
      keyed on "Marshal X's claim" — and the notice in the Unmet Marshals
      block never recorded                                             (SFR-I4)
    AI C6: "Prussia has declared war on Hanover", the turn of France's
      peace, counted 22 peace turns as France at war (CMD-M)           (SFR-I5)
    DL: `Davout, fortify` refused for actions, so the what-if asked about an
      unfortified man; Ney's muster carried Davout off French ground before
      the levy                                                        (SFR-I6)
    economy F1: net_residual zero by construction — the sponsorship arm's
      200 a turn off the books read 0 on 12 of 12 records               (EA-2)
    narration C4: the gate's CMD-M turn 20 — Kutuzov "at Vienna" on the
      row, "Bohemia" in the store; the STORE was stale: a scout's FULL view
      never expired beside a French corps                              (EG-X4)
    AI C1: 19–20 laws with 0 lapses read ✗ against "13–18"     (EG-D1, ruled)

and the siblings the sweep found: RR6-X1 (first contact C4's RS-15 board,
SFR-I6's class) and RR6-X2 (vassals C5 read a capital's fall off the
unrendered prose, SFR-I2's class). Each pin holds its lever down to show
the misread, and up to show the fix.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
import backend.models.world_state as WSM
from backend.commands.parser import CommandParser
from backend.game_logic import instruments as IN
from backend.models.intel import FULL, PARTIAL, scouted_view_expired
from tests._ledgers import doc_text
from tools import _score_probes as P
from tools import playtest_driver as PD
from tools import score_reread as RR
from tools import score_run as SR

REPO = Path(__file__).resolve().parents[1]
ARCHIVES = REPO / "docs" / "audits" / "score_runs"
RR6 = ARCHIVES / "2026_10_21_rr6"
V1_1 = json.loads((REPO / "docs" / "SCORE_CHECKLIST_V1_1.json").read_text(encoding="utf-8"))
V1_2 = json.loads((REPO / "docs" / "SCORE_CHECKLIST_V1_2.json").read_text(encoding="utf-8"))
DIALOG = (REPO / "godot-client" / "project-sovereign" / "scripts"
          / "enemy_phase_dialog.gd").read_text(encoding="utf-8")
DISPATCH_VIEW = (REPO / "godot-client" / "project-sovereign" / "scripts"
                 / "dispatch_view.gd").read_text(encoding="utf-8")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@pytest.fixture
def shipped(monkeypatch):
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    with _quiet():
        M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


class _Recorder:
    """Borrows the real Digest's methods (the stub-Digest idiom)."""

    def __init__(self):
        self.lines, self.records, self.notes = [], [], []
        self.counters = {"commands": 0, "popups": 0, "battles": 0, "turns": 0}
        self.meta = {}

    def _md(self, line):
        self.lines.append(line)

    def record(self, kind, **fields):
        self.records.append({"kind": kind} | fields)

    def note(self, text):
        self.notes.append(text)

    def battle(self, report):
        self.counters["battles"] += 1

    enemy_phase = PD.Digest.enemy_phase
    dispatch = PD.Digest.dispatch
    chest_window = PD.Digest.chest_window
    wars = PD.Digest.wars
    precondition = PD.Digest.precondition


def _arm(root: Path, name: str, md: str = "", records=(), meta=None) -> Path:
    """An arm on disk the readers load like any archive's."""
    d = root / "arms" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.json").write_text(json.dumps(meta or {"status": "completed"}), encoding="utf-8")
    (d / "digest.md").write_text(f"# Playtest digest — {name}\n\n" + md, encoding="utf-8")
    (d / "digest.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records),
                                    encoding="utf-8")
    return d


def _ctx(run: Path) -> dict:
    arms = SR.load_arms(run)
    ctx = {"run_dir": run, "arms": arms,
           "dl_script": json.loads((REPO / SR.SCRIPTS / "score_docked_lines.json")
                                   .read_text(encoding="utf-8"))}
    return arms, ctx


# The archived enemy-phase line the depth campaign and the panel read as the
# game (the final reading's FLD turn 2) — and the action behind it, as the
# client receives it.
ARCHIVED_CAPTURE = {
    "nation": "Austria",
    "ai_action": {"marshal": "ArchdukeCharles", "action": "attack", "target": "Franconia"},
    "events": [{"type": "conquest", "marshal": "ArchdukeCharles", "region": "Franconia",
                "unopposed": True, "captured_by": "Austria", "captured_from": "Bavaria",
                "capture_choice": "secure", "captured_from_alignment": "foe"}],
    "message": "ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria",
}


# ═════════════════════════ SFR-I2 the digest prints what the dialog shows ═════════════════════════
class TestSFRI2TheDigestPrintsWhatTheDialogShows:
    def test_the_archived_line_was_the_unrendered_message(self, monkeypatch):
        """Lever down: the digest quotes the `message` — the raw key the
        depth campaign filed as SFR-D12, which no client screen draws."""
        monkeypatch.setattr(PD, "THE_DIGEST_PRINTS_WHAT_THE_DIALOG_SHOWS", False)
        d = _Recorder()
        d.enemy_phase([ARCHIVED_CAPTURE], {"fog_hidden_nations": "Britain stirred"})
        assert any("ArchdukeCharles takes Franconia" in ln for ln in d.lines), d.lines

    def test_the_digest_quotes_the_dialogs_lines(self):
        d = _Recorder()
        d.enemy_phase([ARCHIVED_CAPTURE], {"fog_hidden_nations": "Britain stirred"})
        text = "\n".join(d.lines)
        assert "Archduke Charles attacks Franconia" in text
        assert "🏴 Austria: Archduke Charles attacks Franconia — Region captured: Franconia (was Bavaria) (secured)" in text
        assert not SR.RAW_KEY_RX.findall(text), text

    def test_the_jsonl_keeps_the_message_marked_unrendered(self):
        d = _Recorder()
        d.enemy_phase([ARCHIVED_CAPTURE], {})
        rec = [r for r in d.records if r["kind"] == "enemy_phase"][0]
        assert rec["unrendered"] == ["message"]
        assert rec["actions"][0]["message"] == ARCHIVED_CAPTURE["message"]
        assert rec["actions"][0]["shown"] == "Archduke Charles attacks Franconia"
        assert rec["captures"] == 1

    @pytest.mark.parametrize("action, line, captures", [
        ({"nation": "Austria", "ai_action": {"marshal": "ArchdukeCharles", "action": "attack",
                                             "target": "Massena"}},
         "Archduke Charles attacks Massena", []),
        ({"nation": "Austria", "ai_action": {"marshal": "Mack", "action": "attack", "target": "Munich"},
          "events": [{"type": "garrison_destroyed", "region": "Munich"},
                     {"type": "conquest", "region": "Munich", "captured_from": "Bavaria",
                      "capture_choice": "secure"}]},
         "Mack attacks Munich",
         ["The garrison of Munich is destroyed.", "Region captured: Munich (was Bavaria) (secured)"]),
        ({"nation": "Austria", "ai_action": {"marshal": "ArchdukeJohn", "action": "move", "target": "Provence"},
          "events": [{"type": "move", "from": "Piedmont", "to": "Provence", "captured_from": "France",
                      "capture_choice": "plunder"}]},
         "Archduke John moves to Provence — Provence falls (was France) and is sacked",
         ["Archduke John moves to Provence — Provence falls (was France) and is sacked"]),
        ({"nation": "Austria",
          "events": [{"type": "battle", "attacker": {"name": "Mack"}, "defender": {"name": "Ney"},
                      "region_conquered": True, "region_name": "Swabia", "captured_from": "France"}]},
         "Mack attacks Ney", ["Swabia CAPTURED! (was France)"]),
        ({"nation": "Britain", "ai_action": {"marshal": "Paget", "action": "naval_expedition"}},
         "Paget embarks an expedition", []),
        ({"nation": "KingdomOfItaly", "ai_action": {"action": "recruit"}},
         "Kingdom of Italy recruits troops", []),
        ({"nation": "Austria", "ai_action": {"marshal": "Mack", "action": "grant_dotation",
                                             "target": "Bohemia"}},
         "Mack is endowed with Bohemia", []),
    ])
    def test_the_mirror_draws_each_line(self, action, line, captures):
        assert PD.rendered_enemy_line(action) == line
        assert PD.rendered_capture_lines(action) == captures

    def test_the_mirror_holds_the_dialogs_verbs(self):
        """Drift pin: `_format_action`'s `match action_type` arms, verb for
        verb, and each fixed phrase in the dialog's own source."""
        block = DIALOG[DIALOG.index("\tmatch action_type:"):DIALOG.index('result += "[color=#" + line_color')]
        arms = set(re.findall(r'^\t\t"([a-z_]+)":', block, re.M))
        assert arms == set(PD.ENEMY_VERB_PHRASES) | {"forced_march", "build", "acts"}, arms
        for phrase, bare in PD.ENEMY_VERB_PHRASES.values():
            assert phrase.split("{t}")[0].strip() in DIALOG, phrase
            if bare:
                assert bare in DIALOG, bare

    def test_meta_says_the_lines_are_rendered(self, tmp_path, monkeypatch):
        meta = {"name": "x", "seed": "historical", "llm": "mock", "transport": "in-process",
                "policy": {}}
        PD.Digest(tmp_path, dict(meta))
        assert json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))["enemy_phase_text"] == "rendered"
        monkeypatch.setattr(PD, "THE_DIGEST_PRINTS_WHAT_THE_DIALOG_SHOWS", False)
        (tmp_path / "b").mkdir()
        PD.Digest(tmp_path / "b", dict(meta))
        assert "enemy_phase_text" not in json.loads((tmp_path / "b" / "meta.json").read_text(encoding="utf-8"))

    def test_a_real_enemy_phase_carries_raw_keys_only_in_the_message(self, shipped):
        """The boot board's own enemy phases: the `message` still carries the
        roster keys (the reproduction), the dialog's lines never do."""
        client, _world = shipped
        raw_in_message, raw_in_shown = 0, 0
        for _ in range(3):
            with _quiet():
                r = client.post("/command", json={"command": "end turn"}).json()
            for a in PD._flatten_enemy_phase(r.get("enemy_phase")):
                raw_in_message += bool(re.search(r"\b(ArchdukeCharles|ArchdukeJohn)\b",
                                                 str(a.get("message") or "")))
                raw_in_shown += bool(re.search(r"\b(ArchdukeCharles|ArchdukeJohn)\b",
                                               PD.rendered_enemy_line(a)
                                               + " ".join(PD.rendered_capture_lines(a))))
        assert raw_in_message > 0, "the reproduction: the message no longer carries a key"
        assert raw_in_shown == 0


# ═════════════════════════ SFR-I7 combat C5 reads rendered text ═════════════════════════
class TestSFRI7CombatC5ReadsWhatThePlayerSees:
    MD = ("## Turn 2 — x\n"
          "- enemy phase: 2 actions, 1 attacks — Britain stirred. — ArchdukeJohn assaults the Milan garrison!\n"
          "  - 🏴 Austria: ArchdukeJohn marches into Milan! Captured: KingdomOfItaly → Austria\n"
          "  - ⚔ Archduke John (lost 100) vs Massena (lost 200)\n")

    def test_an_older_digests_enemy_phase_is_not_read(self, tmp_path):
        _arm(tmp_path, "OP", self.MD)
        arms, ctx = _ctx(tmp_path)
        assert SR.r_combat_legibility_C5(arms, ctx)["pass"] is False      # the misread
        res = SR.r_combat_legibility_C5_v12(arms, ctx)
        assert res["pass"] is True and "not read" in res["evidence"], res

    def test_a_rendered_digests_enemy_phase_is_read(self, tmp_path):
        _arm(tmp_path, "OP", self.MD, meta={"status": "completed", "enemy_phase_text": "rendered"})
        arms, ctx = _ctx(tmp_path)
        assert SR.r_combat_legibility_C5_v12(arms, ctx)["pass"] is False

    def test_a_battle_line_is_always_read(self, tmp_path):
        _arm(tmp_path, "OP", "## Turn 1 — x\n  - ⚔ ArchdukeJohn (lost 1) vs Ney (lost 2)\n")
        arms, ctx = _ctx(tmp_path)
        assert SR.r_combat_legibility_C5_v12(arms, ctx)["pass"] is False

    def test_the_final_reading_reads_clean_on_rendered_text(self):
        arms, ctx = _ctx(ARCHIVES / "2026_10_05_sfr")
        assert SR.r_combat_legibility_C5(arms, ctx)["pass"] is False
        assert SR.r_combat_legibility_C5_v12(arms, ctx)["pass"] is True


# ═════════════════════════ SFR-I4 drama C5 reads every copy ═════════════════════════
SITUATION = {
    "expectation_rises": [{"marshal": "Lannes", "expectation": 40, "previous": 0, "satisfaction": 0}],
    "unmet_marshals": [{"marshal": "Lannes", "expectation": 40, "satisfaction": 0, "eroding": False,
                        "grace_turns_left": 2, "pension": 0},
                       {"marshal": "Soult", "expectation": 160, "satisfaction": 80, "eroding": True,
                        "grace_turns_left": 0, "pension": 50}],
}


def _turns(*blocks):
    """jsonl records: a `turn` record and its records, per (turn, [records])."""
    out = []
    for t, recs in blocks:
        out.append({"kind": "turn", "turn": t})
        out.extend(recs)
    return out


class TestSFRI4DramaC5ReadsEveryCopy:
    def test_the_driver_records_the_block_as_the_screen_draws_it(self):
        rows = PD.unmet_marshal_rows(SITUATION)
        assert [r["line"] for r in rows["expectation_rises"]] == [
            "Lannes's victories raise his expectation — he now looks for 40g/turn (holds 0g)."]
        assert [r["line"] for r in rows["unmet_marshals"]] == [
            "Lannes expects 40g/turn, holds 0g — patience holds 2 more turns",
            "Soult expects 160g/turn, holds 80g (incl. 50g rente) — loyalty eroding"]
        for fixed in ("'s victories raise his expectation — he now looks for ",
                      "g/turn, holds ", " — patience holds ", " — loyalty eroding", "g rente)"):
            assert fixed in DISPATCH_VIEW, fixed

    def test_lever_down_no_block(self, monkeypatch):
        monkeypatch.setattr(PD, "THE_DIGEST_RECORDS_THE_UNMET_BLOCK", False)
        assert PD.unmet_marshal_rows(SITUATION) == {}

    def test_a_headless_morning_still_records_the_block(self):
        seen = {}

        class _D:
            def dispatch(self, text, events=None, turn_events=None, headline_class="", page=None):
                seen["page"] = page

        PD._record_morning_headline(_D(), {"situation": SITUATION})
        assert [r["marshal"] for r in seen["page"]["unmet_marshals"]] == ["Lannes", "Soult"]

    def _drama(self, tmp_path, blocks, recorded=True, md=""):
        meta = {"status": "completed"} | ({"unmet_block": "recorded"} if recorded else {})
        _arm(tmp_path, "CMD-H", md, _turns(*blocks), meta=meta)
        arms, ctx = _ctx(tmp_path)
        return P.drama_c5_expectation_before_erosion_v12(arms, ctx)

    def test_a_notice_before_the_erosion_passes(self, tmp_path):
        res = self._drama(tmp_path, [
            (6, [{"kind": "dispatch", "headline": "x", "expectation_rises": SITUATION["expectation_rises"]}]),
            (10, [{"kind": "dispatch", "headline": "x", "unmet_marshals": [
                {"marshal": "Lannes", "eroding": True}]}]),
        ])
        assert res["measured"] and res["pass"], res

    def test_an_erosion_unannounced_fails(self, tmp_path):
        res = self._drama(tmp_path, [
            (10, [{"kind": "dispatch", "headline": "x",
                   "sub_beats": ["Sire — Lannes's claim is 8 turns in arrears and has stopped being "
                                 "a household matter. It is now a question of the army."]}]),
        ])
        assert res["measured"] and res["pass"] is False, res

    def test_before_is_strict(self, tmp_path):
        res = self._drama(tmp_path, [
            (10, [{"kind": "dispatch", "headline": "Sire — Marshal Lannes's household goes unpaid.",
                   "expectation_rises": SITUATION["expectation_rises"]}]),
        ])
        assert res["pass"] is False, res

    def test_the_v1_reader_never_sees_the_copy_without_marshal(self, tmp_path):
        """The reproduction: the page dropped "Marshal" (SF5-X3) and v1 keyed on it."""
        md = ("## Turn 14 — x\n- DISPATCH: Sire — Lannes's claim is 8 turns in arrears and has "
              "stopped being a household matter. It is now a question of the army.\n")
        _arm(tmp_path, "CMD-H", md)
        arms, ctx = _ctx(tmp_path)
        assert P.drama_c5_expectation_before_erosion(arms, ctx)["measured"] is False
        assert "Lannes t14" in P.drama_c5_expectation_before_erosion_v12(arms, ctx)["evidence"]

    def test_an_archive_without_the_block_is_unmeasured(self, tmp_path):
        res = self._drama(tmp_path, [
            (10, [{"kind": "dispatch", "headline": "Sire — Marshal Lannes's household goes unpaid."}]),
        ], recorded=False)
        assert res["measured"] is False and "predates the Unmet Marshals block" in res["evidence"]

    def test_the_slice_reads_every_claim_announced(self):
        arms, ctx = _ctx(RR6 / "slice")
        res = P.drama_c5_expectation_before_erosion_v12(arms, ctx)
        assert res["measured"] and res["pass"], res
        arms, ctx = _ctx(RR6 / "entry")
        assert P.drama_c5_expectation_before_erosion_v12(arms, ctx)["measured"] is False


# ═════════════════════════ SFR-I5 AI C6 counts France's wars ═════════════════════════
def _row(dtype, text):
    return {"kind": "rail", "dtype": dtype, "text": text, "priority": "HIGH"}


class TestSFRI5AiC6CountsFrancesWars:
    BLOCKS = [
        (1, [{"kind": "enemy_phase", "attacks": 2}]),
        (2, [{"kind": "enemy_phase", "attacks": 1}]),
        (3, [_row("settlement_summary", "Settlement of France vs Austria + Britain + Russia: settlement ratified."),
             _row("diplomatic_war_declared", "Prussia has declared war on Hanover.")]),
        (4, []),
        (5, [_row("diplomatic_alliance_cascade",
                  "France enters the war against Austria via its alliance with Bavaria.")]),
        (6, [{"kind": "enemy_phase", "attacks": 1}]),
    ]

    def test_another_courts_declaration_is_not_frances_war(self, tmp_path):
        _arm(tmp_path, "CMD-M", "", _turns(*self.BLOCKS))
        arm = SR.load_arms(tmp_path)["CMD-M"]
        assert SR._turns_at_war(arm) == [1, 2, 3, 4, 5, 6]           # the misread
        turns, source = SR._france_turns_at_war(arm)
        assert turns == [1, 2, 5, 6] and source == "France's war and peace rows"

    def test_the_drivers_war_record_decides_where_it_exists(self, tmp_path):
        blocks = [(t, recs + [{"kind": "wars", "turn": t, "enemies": (["Austria"] if t != 4 else [])}])
                  for t, recs in self.BLOCKS]
        _arm(tmp_path, "CMD-M", "", _turns(*blocks))
        turns, source = SR._france_turns_at_war(SR.load_arms(tmp_path)["CMD-M"])
        assert turns == [1, 2, 3, 5, 6] and source == "the driver's war record"

    def test_the_driver_records_frances_wars(self, shipped, monkeypatch):
        _client, world = shipped

        class _T:
            backend_main = M

        wars = PD.player_wars(_T())
        assert {"Austria", "Britain", "Russia"} <= set(wars)
        d = _Recorder()
        d.wars(1, wars)
        assert d.records == [{"kind": "wars", "turn": 1, "enemies": wars}]
        monkeypatch.setattr(PD, "THE_DIGEST_RECORDS_FRANCES_WARS", False)
        d.wars(2, wars)
        assert len(d.records) == 1

    def test_the_final_reading_reads_frances_wars(self):
        arms, ctx = _ctx(ARCHIVES / "2026_10_05_sfr")
        assert "11/39" in SR.r_ai_aliveness_C6(arms, ctx)["evidence"]
        assert "'CMD-M': '11/17'" in SR.r_ai_aliveness_C6_v12(arms, ctx)["evidence"]


# ═════════════════════════ SFR-I6 the DL arm stages its preconditions ═════════════════════════
DL_SCRIPT = json.loads((REPO / SR.SCRIPTS / "score_docked_lines.json").read_text(encoding="utf-8"))
#: The entry tree's staging (the drift SFR-I6 measured), for the lever-down arm.
DRIFTED_TURNS = {
    "1": ["Ney, march on Swabia and destroy Mack", "Bernadotte, take Bohemia",
          "Marshal Soult, bring your corps up in support of Ney.", "Davout, fortify",
          "what if Davout attacks Mack?", "where are the Russians?", "why is Europe alarmed?"],
    "2": DL_SCRIPT["turns"]["2"][1:],
    "3": ["request terms from Austria", "Ney, attack Zorglub", "attack Alsace",
          "Bernadotte, scout Bohemia", "Murat, scout Swabia", "Lannes, scout Swabia",
          "what can I do", "recruit 10000 infantry with Davout"],
}


def _run_dl(tmp_path: Path, script: dict) -> dict:
    path = tmp_path / "dl.json"
    path.write_text(json.dumps(script), encoding="utf-8")
    env = dict(os.environ)
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START", "SOVEREIGN_SEED",
                "PYTHONIOENCODING"):
        env.pop(key, None)
    env.update(PYTHONHASHSEED="0", LLM_MODE="mock", INK_IRON_SAVE_DIR=str(tmp_path / "saves"))
    out = tmp_path / "run"
    proc = subprocess.run([sys.executable, "tools/playtest_driver.py", "--name", "DL", "--fresh",
                           "--out", str(out / "arms"), "--llm", "mock", "--script", str(path),
                           "--turns", "3"], cwd=REPO, env=env, capture_output=True, timeout=900)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")[-2000:]
    arms = SR.load_arms(out)
    return arms, {"run_dir": out, "arms": arms, "dl_script": script}


class TestSFRI6TheDlArmStagesItsPreconditions:
    def test_the_script_names_the_boards_it_needs(self):
        pre = DL_SCRIPT["preconditions"]
        assert pre["what if Davout attacks Mack?"]["require"] == [
            {"fortified": "Davout"}, {"within_reach": ["Davout", "Mack"]}]
        assert {"military_actions": 0} in pre["recruit 10000 infantry with Davout"]["require"]
        assert {"on_own_ground": "Davout"} in pre["recruit 10000 infantry with Davout"]["require"]
        assert DL_SCRIPT["turns"]["1"][0] == "Davout, fortify"
        typed = {line for lines in DL_SCRIPT["turns"].values() for line in lines}
        for row, lines in DL_SCRIPT["dl_lines"].items():
            assert set(lines) <= typed, row       # the arm never drops a docked line

    def test_the_driver_reads_each_precondition(self, shipped):
        _client, world = shipped

        class _T:
            backend_main = M

        what_if = DL_SCRIPT["preconditions"]["what if Davout attacks Mack?"]
        assert PD.precondition_failures(_T(), what_if) == ["Davout is not fortified"]
        world.marshals["Davout"].fortified = True
        assert PD.precondition_failures(_T(), what_if) == []
        levy = DL_SCRIPT["preconditions"]["recruit 10000 infantry with Davout"]
        world.actions_remaining = 0
        assert PD.precondition_failures(_T(), levy) == []
        world.marshals["Davout"].location = "Swabia"
        assert PD.precondition_failures(_T(), levy) == [
            "Davout stands at Swabia, not on France's ground"]

    def test_a_failed_precondition_is_written_into_the_digest(self):
        d = _Recorder()
        d.precondition("what if Davout attacks Mack?", {"row": "RS-12"}, ["Davout is not fortified"])
        assert d.notes and d.notes[0].startswith("⚠ SCRIPT PRECONDITION — `what if Davout attacks Mack?` (RS-12)")
        assert d.meta["script_preconditions_failed"] == ["RS-12"]
        assert d.records[-1]["held"] is False

    def test_the_restaged_arm_reads_its_rows(self, tmp_path):
        arms, ctx = _run_dl(tmp_path, DL_SCRIPT)
        assert "SCRIPT PRECONDITION" not in arms["DL"].md
        for reader in (SR.r_combat_legibility_C4_v12, SR.r_economy_C5_v12, SR.r_first_contact_C4_v12):
            res = reader(arms, ctx)
            assert res["measured"] and res["pass"], (reader.__name__, res)

    def test_the_drifted_arm_reads_unmeasured(self, tmp_path):
        """Lever down: the entry tree's staging — the misread returns as ✗ on
        the v1 readers, and the corrected readers refuse to read it."""
        drifted = copy.deepcopy(DL_SCRIPT)
        drifted["turns"] = DRIFTED_TURNS
        arms, ctx = _run_dl(tmp_path, drifted)
        assert "SCRIPT PRECONDITION — `what if Davout attacks Mack?` (RS-12)" in arms["DL"].md
        assert SR.r_combat_legibility_C4(arms, ctx)["pass"] is False
        assert SR.r_combat_legibility_C4_v12(arms, ctx)["measured"] is False
        assert SR.r_economy_C5_v12(arms, ctx)["measured"] is False

    def test_an_older_archive_is_read_off_its_staging_lines(self):
        arms, ctx = _ctx(ARCHIVES / "2026_10_05_sfr")
        assert SR.r_combat_legibility_C4(arms, ctx)["pass"] is False
        assert "SCRIPT PRECONDITION (RS-12" in SR.r_combat_legibility_C4_v12(arms, ctx)["evidence"]
        assert "SCRIPT PRECONDITION (AAR-6" in SR.r_economy_C5_v12(arms, ctx)["evidence"]


# ═════════════════════════ EA-2 economy F1 sees an off-books flow ═════════════════════════
class TestEA2EconomyF1SeesAnOffBooksFlow:
    def _f1(self, tmp_path, windows):
        recs = [{"kind": "economy", "net_residual": 0}] + windows
        _arm(tmp_path, "CMD-H", "", recs)
        arms, ctx = _ctx(tmp_path)
        return SR.r_economy_F1(arms, ctx), SR.r_economy_F1_v12(arms, ctx)

    def test_an_off_books_flow_is_seen(self, tmp_path):
        v1, v12 = self._f1(tmp_path, [{"kind": "chest_window", "turn": 3, "off_books": -200}])
        assert v1["pass"] is True                       # the misread: blind
        assert v12["pass"] is False and "-200" in v12["evidence"]

    def test_books_that_balance_pass(self, tmp_path):
        assert self._f1(tmp_path, [{"kind": "chest_window", "turn": 3, "off_books": 0}])[1]["pass"] is True

    def test_an_archive_without_the_measure_is_unmeasured(self, tmp_path):
        assert self._f1(tmp_path, [])[1]["measured"] is False

    def test_the_window_prices_a_purchase_made_with_the_last_action(self):
        """An auto-advance: the command bought 200 before the engine opened
        its window (`treasury - net`) — the window's one-shot."""
        d = _Recorder()
        d.chest_window({"events": [{"type": "turn_end", "old_turn": 4, "treasury": 1100, "net": 300,
                                    "materiel": 0}],
                        "morning_dispatch": {"situation": {"treasury_delta": 300}}}, 1000, 1100)
        rec = d.records[-1]
        assert (rec["one_shots"], rec["off_books"]) == (-200, 0)

    @pytest.mark.parametrize("on_the_books, off", [(True, 0), (False, -200)])
    def test_a_sponsorship_off_the_books_is_measured(self, shipped, monkeypatch, on_the_books, off):
        """The economy audit's case, rebuilt: France pays Prussia 200 a turn.
        EA-1's lever down takes the payment off the books (the shipped tree
        before the audit) — the chest still pays it."""
        client, world = shipped
        res = IN.grant_directed_sponsorship(world, payer="France", recipient="Prussia",
                                            aim="Hanover", amount_per_turn=200)
        assert res["success"], res
        monkeypatch.setattr(IN, "THE_SUBSIDIES_ARE_ON_THE_BOOKS", on_the_books)
        before = M.world.nation_gold["France"]
        with _quiet():
            r = client.post("/command", json={"command": "end turn"}).json()
        d = _Recorder()
        d.chest_window(r, before, M.world.nation_gold["France"])
        assert d.records[-1]["off_books"] == off, d.records[-1]

    def test_lever_down_no_measure(self, monkeypatch):
        monkeypatch.setattr(PD, "THE_DIGEST_MEASURES_THE_CHEST", False)
        d = _Recorder()
        d.chest_window({"events": [{"type": "turn_end", "treasury": 1, "net": 1}]}, 0, 1)
        assert d.records == []

    def test_the_slice_measures_every_end_turn(self):
        arms, ctx = _ctx(RR6 / "slice")
        windows = [r for a in arms.values() for r in a.kind("chest_window")]
        assert len(windows) >= 200 and all(r["off_books"] == 0 for r in windows)


# ═════════════════════════ EG-X4 the scouted view expires ═════════════════════════
class TestEGX4TheScoutedViewExpires:
    def _board(self, world):
        """Swabia scouted with Mack in it, a French corps next door, Mack gone
        — then three turns pass with the corps still beside it."""
        swabia = world.regions["Swabia"]
        beside = next(r for r in swabia.adjacent_regions
                      if not any(m.location == r for m in world.marshals.values()
                                 if m.nation != world.player_nation))
        for m in world.marshals.values():
            if m.nation == world.player_nation and m.location == "Swabia":
                m.location = "Paris"
        world.marshals["Davout"].location = beside
        turn = int(world.current_turn)
        world.update_intel_from_scout("Swabia", turn)
        assert any(k.get("name") == "Mack" for k in world.intel["Swabia"].known_marshals)
        # Mack goes where no French eye reaches: off French soil, beside no
        # French corps (else this turn's read sees him there, rightly).
        seen = set()
        for m in world.marshals.values():
            if m.nation == world.player_nation and m.strength > 0:
                seen |= {m.location, *world.regions[m.location].adjacent_regions}
        far = next(r for r, reg in world.regions.items()
                   if reg.controller == "Austria" and r not in seen
                   and r not in swabia.adjacent_regions and r != "Swabia")
        world.marshals["Mack"].location = far
        world.current_turn = turn + 3
        world.calculate_visibility()
        world.decay_intel()
        return world.intel["Swabia"]

    def test_the_stale_view_is_replaced_by_this_turns_read(self, shipped):
        _client, world = shipped
        intel = self._board(world)
        assert intel.visibility == PARTIAL
        assert not any(k.get("name") == "Mack" for k in intel.known_marshals)
        last = world.get_last_known_location("Mack")
        assert last is None or last[0] != "Swabia"

    def test_seam_down_the_phantom_stands(self, shipped, monkeypatch):
        """The gate's CMD-M turn 20, in miniature: FULL, three turns old, the
        man long gone — the store's last sighting stale."""
        _client, world = shipped
        monkeypatch.setattr(WSM, "scouted_view_expired", lambda *a, **k: False)
        intel = self._board(world)
        assert intel.visibility == FULL
        assert any(k.get("name") == "Mack" for k in intel.known_marshals)
        assert world.get_last_known_location("Mack")[0] == "Swabia"

    def test_a_live_grant_keeps_the_view(self, shipped):
        _client, world = shipped
        world.intel_grants["Swabia"] = int(world.current_turn) + 5
        assert self._board(world).visibility == FULL

    def test_the_rule(self):
        class _I:
            visibility, intel_source, last_updated_turn = FULL, "scout", 10

        assert scouted_view_expired(_I(), 13) and not scouted_view_expired(_I(), 12)
        assert not scouted_view_expired(_I(), 13, granted=True)
        _I.intel_source = "own_territory"
        assert not scouted_view_expired(_I(), 13)


# ═════════════════════════ EG-D1 the re-band, checklist v1.2 ═════════════════════════
class TestEGD1TheRebandInChecklistV12:
    def _c1(self, tmp_path, counts):
        for n, (enacted, lapsed) in counts.items():
            rows = ([{"kind": "dispatch_row", "dtype": "law_enacted_abroad"}] * enacted
                    + [{"kind": "dispatch_row", "dtype": "law_lapsed_abroad"}] * lapsed)
            _arm(tmp_path, n, "", rows)
        arms, ctx = _ctx(tmp_path)
        return SR.r_ai_aliveness_C1(arms, ctx), SR.r_ai_aliveness_C1_v12(arms, ctx)

    def test_a_fully_competent_ai_passes(self, tmp_path):
        v1, v12 = self._c1(tmp_path, {"CMD-H": (20, 0), "CMD-A": (19, 0), "CMD-M": (19, 0)})
        assert v1["pass"] is False and v12["pass"] is True        # the misread, then the band

    @pytest.mark.parametrize("counts", [{"CMD-H": (12, 0)}, {"CMD-H": (20, 1)}])
    def test_the_floor_and_the_lapse_still_bind(self, tmp_path, counts):
        assert self._c1(tmp_path, counts)[1]["pass"] is False

    def test_the_checklist_carries_the_band(self):
        item = next(i for p in V1_2["pillars"] if p["key"] == "ai_aliveness"
                    for i in p["items"] if i["id"] == "C1")
        assert item["text"] == "The rival courts enact at least 13 of their decks' 20 laws, with 0 lapses"
        assert item["reader"] == "r_ai_aliveness_C1_v12" and "EG-D1" in item["amended"]
        assert SR.AI_C1_LAW_FLOOR == 13

    def test_v1_2_is_v1_1_but_for_its_amendments(self):
        assert V1_2["version"] == "1.2"
        assert (V1_2["rule"], V1_2["done_when"]) == (V1_1["rule"], V1_1["done_when"])
        old = {(p["key"], i["id"]): i for p in V1_1["pillars"] for i in p["items"]}
        amended = 0
        for p in V1_2["pillars"]:
            for i in p["items"]:
                if i.get("amended") and i.get("amended") != old[(p["key"], i["id"])].get("amended"):
                    amended += 1
                    assert i.get("reader") and SR._named_reader(i["reader"]) is not None, i["id"]
                else:
                    assert i == old[(p["key"], i["id"])], (p["key"], i["id"])
        assert amended == 10

    def test_both_archives_read_the_band(self):
        """The baseline and the final reading, re-read under v1.2 beside
        their records — the same reader on both."""
        for run, mark in (("2026_09_29_c20d5bba", True), ("2026_10_05_sfr", False),
                          ("2026_10_05_econ_gate", True)):
            rer = json.loads((ARCHIVES / run / "checklist_v1_2.json").read_text(encoding="utf-8"))
            assert rer["checklist_version"] == "1.2"
            item = next(i for i in rer["pillars"]["ai_aliveness"]["items"] if i["id"] == "C1")
            assert item["pass"] is mark and "at least 13" in item["evidence"], (run, item)
            frozen = json.loads((ARCHIVES / run / "checklist.json").read_text(encoding="utf-8"))
            assert frozen.get("checklist_version") != "1.2"     # the record kept


# ═════════════════════════ the re-read ═════════════════════════
class TestTheReRead:
    def test_a_probe_without_saves_keeps_its_mark(self, tmp_path):
        _arm(tmp_path, "CMD-H", "## Turn 1 — x\n")
        base = {"pillars": {p["key"]: {"items": [{"id": i["id"], "kind": i["kind"], "measured": True,
                                                  "pass": True, "evidence": "as read"}
                                                 for i in p["items"]]}
                            for p in V1_2["pillars"]}}
        (tmp_path / "checklist.json").write_text(json.dumps(base), encoding="utf-8")
        checklist = copy.deepcopy(V1_2)
        for p in checklist["pillars"]:
            p["items"] = [i for i in p["items"] if p["key"] == "narration" or not i.get("amended")]
        with _quiet():
            out = RR.reread(tmp_path, checklist, {}, "t")
        item = next(i for i in out["pillars"]["narration"]["items"] if i["id"] == "C4")
        assert item["pass"] is True and item["reread"].startswith("kept")

    def test_the_rereads_sit_beside_their_records(self):
        for run in ("2026_09_29_c20d5bba", "2026_10_05_sfr", "2026_10_05_econ_gate",
                    "2026_10_21_rr6/entry"):
            assert (ARCHIVES / run / "checklist_v1_2.json").exists(), run
            assert (ARCHIVES / run / "checklist.json").exists(), run

    def test_the_corrected_auto_readers_reproduce_the_published_marks(self):
        readers = {("combat_legibility", "C5"): SR.r_combat_legibility_C5_v12,
                   ("ai_aliveness", "C1"): SR.r_ai_aliveness_C1_v12,
                   ("ai_aliveness", "C6"): SR.r_ai_aliveness_C6_v12,
                   ("economy", "F1"): SR.r_economy_F1_v12}
        for run in ("2026_09_29_c20d5bba", "2026_10_05_sfr", "2026_10_05_econ_gate"):
            arms, ctx = _ctx(ARCHIVES / run)
            rer = json.loads((ARCHIVES / run / "checklist_v1_2.json").read_text(encoding="utf-8"))
            for (pillar, iid), fn in readers.items():
                item = next(i for i in rer["pillars"][pillar]["items"] if i["id"] == iid)
                res = fn(arms, ctx)
                assert (res["measured"], res["pass"]) == (item["measured"], item["pass"]), (run, pillar, iid)


# ═════════════════════════ the siblings ═════════════════════════
class TestRR6X1FirstContactC4ReadsItsBoard:
    def test_an_answer_with_actions_in_hand_is_unmeasured(self, tmp_path):
        md = ("## Turn 3 — x\n- CMD `what can I do` → ✓ These orders would be carried out today, Sire:\n"
              "  - ↳ Davout, attack Archduke Charles / Ney, march to Munich\n")
        _arm(tmp_path, "DL", md, [{"kind": "command", "text": "what can I do", "success": True}])
        arms, ctx = _ctx(tmp_path)
        assert SR.r_first_contact_C4(arms, ctx)["pass"] is False          # the misread
        res = SR.r_first_contact_C4_v12(arms, ctx)
        assert res["measured"] is False and "SCRIPT PRECONDITION (RS-15" in res["evidence"]


class TestRR6X2VassalsC5ReadsTheDialogsLines:
    def test_a_fall_the_dialog_drew_is_read(self, tmp_path):
        md = ("## Turn 5 — x\n- enemy phase: 5 actions, 4 attacks — Archduke John attacks Milan\n"
              "  - 🏴 Austria: Archduke John attacks Milan — The garrison of Milan is destroyed. · "
              "Region captured: Milan (was Kingdom of Italy) (secured)\n"
              "## Turn 6 — x\n- LEDGER x\n## Turn 7 — x\n- LEDGER x\n")
        _arm(tmp_path, "CMD-A", md)
        arms, ctx = _ctx(tmp_path)
        assert P.vassals_c5_client_capital_contested(arms, ctx)["measured"] is False   # blind
        res = P.vassals_c5_client_capital_contested_v12(arms, ctx)
        assert res["measured"] and res["pass"] is False and "CMD-A t5 Milan" in res["evidence"]

    def test_an_older_digests_prose_still_names_the_event(self, tmp_path):
        md = ("## Turn 5 — x\n  - 🏴 Austria: ArchdukeJohn marches into Milan! Milan has been captured by Austria!\n"
              "## Turn 6 — x\n- CMD `Massena, attack Milan` → ✓ x\n")
        _arm(tmp_path, "CMD-A", md)
        arms, ctx = _ctx(tmp_path)
        res = P.vassals_c5_client_capital_contested_v12(arms, ctx)
        assert res["measured"] and res["pass"], res


class TestTheLedgers:
    def test_every_row_is_closed_with_its_slice(self):
        text = doc_text("BUG_FIXES.md")
        for row in ("SFR-I2", "SFR-I4", "SFR-I5", "SFR-I6", "SFR-I7", "EA-2", "EG-X4"):
            line = next(ln for ln in text.splitlines() if f"| **{row}** |" in ln)
            assert "FIXED — SF-RR6" in line, row
        for row in ("RR6-X1", "RR6-X2"):
            line = next(ln for ln in text.splitlines() if f"| **{row}** |" in ln)
            assert "✅ FIXED October 21, 2026" in line, row

    def test_the_sibling_routed_carries_its_owner(self):
        line = next(ln for ln in doc_text("BUG_FIXES.md").splitlines() if "| **RR6-X3** |" in ln)
        assert "OPEN — owner: Pre-Deploy S14b" in line and "test_rr6_x3_one_sighting_rule.py" in line
