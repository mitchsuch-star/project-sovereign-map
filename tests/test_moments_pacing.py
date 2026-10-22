"""S14c — the moments' pacing, measured (`docs/EVENTS_SPEC.md` §7). Part 2's
first landing (S14C-X3): the instruments see a moment letter. Part 4 adds the
10-seed sweep's ceilings and the arms' floors here.

The sweep (`tools/ai_v_sweep.py`) counts the letters by object identity and
their rows per producing turn, never as a court's courting; the driver
(`tools/playtest_driver.py`) prints the rows and answers a letter from its
own `--moment` dial, by the option's action — a closed Accept left standing
with its reason, where it used to fall to the Decline in silence.
"""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic import moments as MO
from tests import _chip_census as C
from tests.test_moments_engine import _at, _block, _tick

REPO = Path(__file__).resolve().parents[1]


def _sweep():
    spec = importlib.util.spec_from_file_location("_ai_v_sweep", REPO / "tools" / "ai_v_sweep.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def _restore_active_world():
    prior = (M.world, M.game_state.get("world"), M.parser)
    yield
    M.world = prior[0]
    M.game_state["world"] = prior[1]
    M.parser = prior[2]


@pytest.fixture
def world(monkeypatch):
    C.board_env(monkeypatch)
    return M.world


def _digest(rows, final=None):
    base = {"turn": 0, "threat": 0, "mirror": [0, 0, ""], "intents": {}, "wars_opened": [],
            "wars_ended": [], "events": [], "dispatch_queue": [], "incoming_proposals": [],
            "exhaustion": {}, "gold": {}, "strength": {}}
    return {"meta": {"player": "France", "france_needles": ["france", "french"]},
            "turns": [dict(base, **r) for r in rows],
            "final": final or {}}


class TestTheSweepCountsTheLetters:
    def test_a_moment_letter_is_no_court_s_courting(self, world):
        sweep = _sweep()
        world.moments = MO.from_block(_block())
        capture = sweep.RunCapture(world)
        _at(world, 8)
        _tick(world)
        assert not [r for r in capture._incoming_proposals() if r["ptype"] == "moment_letter"]
        letters = capture._moment_letters()
        assert [r["moment"] for r in letters] == ["bavarian_match"]
        assert capture._moment_letters() == []          # by identity: seen once
        assert capture._moments_open() == 1

    def test_the_metrics_read_the_rows(self):
        sweep = _sweep()
        rows = [
            {"turn": 8, "events": [{"type": "moment", "phase": "arrived", "moment": "a"},
                                   {"type": "moment", "phase": "arrived", "moment": "b"}],
             "moments_open": 2, "foreground_in_tenure": True},
            {"turn": 10, "events": [{"type": "moment", "phase": "passed", "reason": "crowded",
                                     "moment": "c"},
                                    {"type": "offer_lapsed", "proposal_type": "moment_letter"}],
             "dispatch_queue": [{"type": "moment_receipt", "vars": {"line": "c passed"},
                                 "queued_turn": 10}]},
        ]
        final = {"moments": {"state": {"a": {"status": "lapsed"}, "c": {"status": "passed", "reason": "crowded"},
                                       "d": {"status": "passed", "reason": "premise"}}}}
        derived = sweep.derive_metrics(_digest(rows, final))
        assert derived["moments_arrived"] == 2
        assert derived["moments_max_per_producing_turn"] == 2   # two in one turn — the R3 break, seen
        assert derived["letters_during_foreground"] == 2
        assert derived["open_letters_max"] == 2
        assert derived["moments_passed"] == {"crowded": 1, "premise": 1}
        assert derived["moments_lapsed"] == 1
        assert derived["fire_turns"] == {"a": [8], "b": [8]}
        assert derived["soap_opera_lines"] == [0, 0]            # a receipt is France's own

    def test_an_archived_digest_still_derives(self):
        derived = _sweep().derive_metrics(_digest([{"turn": 1}]))
        assert derived["moments_arrived"] == 0 and derived["moments_passed"] == {}


class TestTheDriverAnswersByIntent:
    def _answerer(self, policy):
        from tools import playtest_driver as D
        return D.Answerer(None, None, dict(D.POLICY_DEFAULTS) | policy, False), D

    def _letter(self, accept_enabled=True, reason=""):
        return {"is_moment": True, "proposal_type": "moment_letter", "from_nation": "",
                "options": [{"label": "Seal the match", "action": "accept_ai_proposal",
                             "enabled": accept_enabled, "reason": reason},
                            {"label": "Let Baden keep her", "action": "reject_ai_proposal",
                             "enabled": True, "reason": ""}]}

    def test_the_dial_is_absent_by_default_so_every_arm_is_unchanged(self):
        from tools import playtest_driver as D
        assert "moment" in D.POLICY_FLAG_KEYS and "moment" not in D.POLICY_DEFAULTS
        assert json.dumps(D.resolve_policy(argparse.Namespace(), {})) == json.dumps(dict(D.POLICY_DEFAULTS))
        assert D.moment_mode({}) == "decline"
        assert D.moment_mode({"diplomacy": "accept"}) == "decline"   # never the diplomacy dial

    def test_the_letter_is_answered_by_its_action(self):
        answerer, _ = self._answerer({"moment": "accept"})
        assert answerer._pick_dialogue_choice(self._letter()) == "accept_ai_proposal"
        answerer, _ = self._answerer({})
        assert answerer._pick_dialogue_choice(self._letter()) == "reject_ai_proposal"

    def test_a_closed_accept_leaves_the_letter_standing_with_its_reason(self):
        answerer, _ = self._answerer({"moment": "accept", "diplomacy": "accept"})
        reason = "1,000 gold is asked; the treasury holds 800."
        assert answerer._pick_dialogue_choice(self._letter(False, reason)) is None
        assert answerer.last_standing_reason == reason

    def test_the_log_prints_a_moment_s_rows(self):
        from tools import playtest_driver as D
        lines = []

        class _Rec:
            def _md(self, text):
                lines.append(text)

            def record(self, *a, **k):
                pass

        rec = _Rec()
        D.Digest.campaign_log(rec, [
            {"type": "moment", "display": "The Bavarian Match — a letter of the record is laid before the Emperor"},
            {"type": "offer_lapsed", "proposal_type": "moment_letter",
             "display": "The Bavarian Match was left unanswered — Let Baden keep her: Bavaria's goodwill 60 → 55."},
            {"type": "offer_lapsed", "proposal_type": "open_borders", "display": "Sweden's offer lapsed"},
        ], turn=8)
        assert any("LOG moment:" in ln for ln in lines)
        assert any("left unanswered" in ln for ln in lines)
        assert not any("Sweden" in ln for ln in lines)          # every other lapse stays unprinted
