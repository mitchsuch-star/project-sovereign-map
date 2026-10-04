"""SR-8b + SF-AGD-1 "The agendas arm" — Score Finish Step 5 (October 3, 2026).

A PLAYED road that carves a client through the settlement path and fires
the Proclamation, with the formables gate flipping in play; SF-M's TILSIT
probe is its instrument (the same board, the same carve, the same answer:
the bare carve COUNTERs at 30 and the carve with 6,000 gold is ACCEPTed at
90). Done when agendas C5 reads ✓ on the new arm.

Pinned here:
* the AGD fixture's shape (`tools/gen_agd_fixture.py`): the TILSIT board with
  POSEN STILL PRUSSIAN, Davout beside it, Britain's war running (Tilsit's own
  shape) and every other war ended with the engine's own pair resolution;
* the driver's script grammar for the settlement table's own clicks — a line
  beginning with "@" answers the held dialogue with that action and its JSON
  action_params, exactly as the client posts it, and the dialogue a line
  opened is HELD (never policy-answered) while the next line is a click;
* the played road end to end (the arm run in a subprocess, the committed
  script and fixture): Posen taken on turn 1, the carve's terms stated on
  the table, the separate peace, Prussia's acceptance, the Proclamation;
* agendas C5's reader on that arm, and the instrument correction both C5's
  gate-flip evidence and C3 carry (a province-held term drops its
  "(currently X-held)" tail when met, so the raw text could never flip).
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "playtest_saves" / "fixture_agd_tilsit.json"
SCRIPT = REPO / "tools" / "playtest_scripts" / "sf_agd1_tilsit_road.json"
DRIVER = REPO / "tools" / "playtest_driver.py"


def _load(path):
    from backend import save_manager as SM
    with contextlib.redirect_stdout(io.StringIO()):
        res = SM.load_game(Path(path))
    assert res.get("success"), res.get("message")
    return res["world"]


def _duchy_terms(world):
    from backend.game_logic import formations as F
    payload = F.build_formables_payload(world)
    row = next(r for r in payload["formables"] if r.get("tag") == "DuchyOfWarsaw")
    return row


# ═══════════════════════════════════════════════════════════════════════════
# The fixture — the TILSIT board with Posen still Prussian
# ═══════════════════════════════════════════════════════════════════════════

class TestTheFixture:
    @pytest.fixture(scope="class")
    def world(self):
        return _load(FIXTURE)

    def test_posen_is_still_prussian_and_davout_stands_beside_it(self, world):
        assert world.regions["Posen"].controller == "Prussia"
        assert world.regions["Berlin"].controller == "France"
        assert world.regions["Silesia"].controller == "France"
        assert world.marshals["Davout"].location == "Silesia"
        assert "Posen" in world.regions["Silesia"].adjacent_regions

    def test_prussias_field_army_is_gone(self, world):
        assert not [m for m in world.marshals.values() if m.nation == "Prussia"]
        assert {"Brunswick", "Hohenlohe"} <= set(world.fallen_marshals)

    def test_it_is_tilsits_shape(self, world):
        """France at war with Prussia and Britain only — the Duchy of
        Warsaw was carved while Britain's war ran (IGR-D's gate Q2(a))."""
        assert sorted(world.get_nations_at_war_with("France")) == ["Britain", "Prussia"]

    def test_the_duchys_gate_is_shut_on_posen(self, world):
        row = _duchy_terms(world)
        assert row["available"] is False
        terms = {t["text"]: t["met"] for t in row["gate_terms"]}
        assert terms["at war with Prussia"] is True
        assert terms["Posen held at the settlement table (currently Prussia-held)"] is False


# ═══════════════════════════════════════════════════════════════════════════
# The driver's click grammar
# ═══════════════════════════════════════════════════════════════════════════

class _Transport:
    def __init__(self):
        self.posts = []

    def post(self, path, body):
        self.posts.append((path, body))
        return {"success": True, "message": "ok"}

    def get(self, path):
        return {}


class _Digest:
    def __init__(self):
        self.popups = []
        self.terms = []
        self.recent = []

    def popup(self, key, summary, answer):
        self.popups.append((key, summary, answer))

    def settlement_terms(self, dialogue):
        self.terms.append(dialogue)

    def note(self, *_a, **_k):
        pass

    def __getattr__(self, name):          # every other digest call is a no-op
        return lambda *a, **k: None


class TestTheClickGrammar:
    def _answerer(self):
        sys.path.insert(0, str(REPO))
        from tools import playtest_driver as PD
        transport, digest = _Transport(), _Digest()
        policy = dict(PD.POLICY_DEFAULTS)
        policy["diplomacy"] = "accept"
        return PD.Answerer(transport, digest, policy, strict=False), transport, digest

    def test_a_held_dialogue_is_never_answered_and_is_said(self):
        answerer, transport, digest = self._answerer()
        answerer.hold_dialogue = True
        dialogue = {"type": "settlement_confirm", "dialogue_id": 7,
                    "dialogue_mode": "PROPOSE", "options": [{"action": "submit_settlement_for_review"}]}
        followups = answerer.scan({"diplomatic_dialogue": dialogue})
        assert followups == [] and transport.posts == []
        assert answerer.held_dialogue is dialogue
        assert digest.popups[-1][2] == "(held for the script's own clicks)"

    def test_a_click_posts_the_action_and_its_params_on_the_held_dialogue(self):
        answerer, transport, _ = self._answerer()
        answerer.held_dialogue = {"type": "settlement_confirm", "dialogue_id": 9}
        answerer.script_click('@settlement_demand_add {"nation": "Prussia", "group": "demand", '
                              '"clause_type": "create_client", "tag": "DuchyOfWarsaw"}')
        path, body = transport.posts[-1]
        assert path == "/respond_to_diplomatic_dialogue"
        assert body["choice"] == "settlement_demand_add" and body["dialogue_id"] == 9
        assert body["action_params"] == {
            "action": "settlement_demand_add", "nation": "Prussia", "group": "demand",
            "clause_type": "create_client", "tag": "DuchyOfWarsaw"}
        assert answerer.held_dialogue is None

    def test_a_bare_click_carries_no_params(self):
        answerer, transport, _ = self._answerer()
        answerer.held_dialogue = {"type": "settlement_confirm", "dialogue_id": 3}
        answerer.script_click("@submit_settlement_for_review")
        _, body = transport.posts[-1]
        assert body == {"choice": "submit_settlement_for_review", "dialogue_id": 3}

    def test_unheld_the_policy_answers_as_before(self):
        answerer, transport, _ = self._answerer()
        dialogue = {"type": "incoming_proposal", "dialogue_id": 4,
                    "options": [{"action": "accept", "label": "Accept"},
                                {"action": "reject", "label": "Reject"}]}
        answerer.scan({"diplomatic_dialogue": dialogue})
        assert transport.posts and transport.posts[-1][1]["dialogue_id"] == 4


# ═══════════════════════════════════════════════════════════════════════════
# The played road — end to end
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def played(tmp_path_factory):
    out = tmp_path_factory.mktemp("agd_arm")
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0", PYTHONPATH=str(REPO), LLM_MODE="mock")
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "PYTHONIOENCODING", "SOVEREIGN_SEED"):
        env.pop(key, None)
    proc = subprocess.run(
        [sys.executable, str(DRIVER), "--script", str(SCRIPT), "--from-save", str(FIXTURE),
         "--turns", "3", "--diplomacy", "accept", "--save-at", "1,2,3",
         "--name", "AGD", "--out", str(out), "--fresh"],
        cwd=str(REPO), env=env, capture_output=True, text=True, timeout=1200)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    arm = out / "AGD"
    records = [json.loads(line) for line in
               (arm / "digest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return arm, records


class TestThePlayedRoad:
    def test_it_completes(self, played):
        arm, _ = played
        assert json.loads((arm / "meta.json").read_text(encoding="utf-8"))["status"] == "completed"

    def test_posen_is_taken_in_play_and_the_gate_flips(self, played):
        arm, _ = played
        before = {t["text"]: t["met"] for t in _duchy_terms(_load(FIXTURE))["gate_terms"]}
        after_row = _duchy_terms(_load(arm / "saves" / "AGD_t1.json"))
        after = {t["text"]: t["met"] for t in after_row["gate_terms"]}
        assert before["Posen held at the settlement table (currently Prussia-held)"] is False
        assert after["Posen held at the settlement table"] is True
        assert after_row["available"] is True

    def test_the_carve_states_its_terms_on_the_table(self, played):
        _, records = played
        stated = [c for r in records if r.get("kind") == "settlement_terms"
                  for c in (r.get("carves") or [])]
        assert stated, "no table stated the carve"
        assert stated[0]["client_display_name"] == "Duchy of Warsaw"
        assert stated[0]["from"] == "Prussia" and stated[0]["provinces"] == ["Posen"]
        modes = {r.get("dialogue_mode") for r in records if r.get("kind") == "settlement_terms"
                 and r.get("carves")}
        assert {"PROPOSE", "REVIEW"} <= modes

    def test_the_clicks_are_the_clients(self, played):
        _, records = played
        clicks = [r.get("text") for r in records if r.get("kind") == "command"
                  and str(r.get("text", "")).startswith("@")]
        assert [c.split()[0] for c in clicks] == [
            "@settlement_demand_add", "@settlement_demand_add",
            "@submit_settlement_for_review", "@seek_bilateral_peace"]

    def test_prussia_signs_and_the_proclamation_fires(self, played):
        _, records = played
        cards = [r for r in records if r.get("kind") == "popup"
                 and r.get("key") == "nation_proclamation"]
        assert cards and "DuchyOfWarsaw" in str(cards[0].get("summary"))
        ratified = [r for r in records if r.get("kind") == "ratified"]
        assert ratified
        summary = ratified[0]["summary"]
        assert summary.get("target_nation") == "Prussia" and summary.get("new_state") == "PEACE"

    def test_the_duchy_stands_on_the_last_save(self, played):
        arm, _ = played
        world = _load(arm / "saves" / "AGD_t3.json")
        assert world.regions["Posen"].controller == "DuchyOfWarsaw"
        assert "DuchyOfWarsaw" in world.get_active_nations()

    def test_agendas_c5_reads_true_on_the_arm(self, played, tmp_path):
        sys.path.insert(0, str(REPO))
        from tools import score_run as SR
        arm, _ = played
        verdict = SR.r_agendas_C5({"AGD": SR.Arm(arm)}, {"run_dir": str(tmp_path)})
        assert verdict["measured"] is True and verdict["pass"] is True, verdict
        assert "gate flipped to met in play" in verdict["evidence"]

    def test_c5_without_the_arm_is_unmeasured(self, tmp_path):
        sys.path.insert(0, str(REPO))
        from tools import score_run as SR
        verdict = SR.r_agendas_C5({}, {"run_dir": str(tmp_path)})
        assert verdict["measured"] is False


# ═══════════════════════════════════════════════════════════════════════════
# The instrument correction — the gate-term key
# ═══════════════════════════════════════════════════════════════════════════

class TestTheGateTermKey:
    def test_the_holder_tail_is_not_part_of_the_term(self):
        sys.path.insert(0, str(REPO))
        from tools import _score_probes as P
        assert P._gate_term_key("Posen held at the settlement table (currently Prussia-held)") \
            == "Posen held at the settlement table"
        assert P._gate_term_key("at war with Prussia") == "at war with Prussia"

    def test_c3_keys_on_the_corrected_term(self):
        src = (REPO / "tools" / "_score_probes.py").read_text(encoding="utf-8")
        start = src.index("def agendas_c3_gate_flips")
        body = src[start:src.index("\ndef ", start + 10)]
        assert "_gate_term_key(term.get(\"text\"))" in body
