"""SF-NAV-1-D1's research (Score Finish Step 7, October 4, 2026) — the
conquest road the Step 6 arm never tried, and the two driver dials it needed.

`docs/SCORE_FINISH_SPEC.md` §6.6 is the gate record (the Tilsit clause; the
build is Step 7's row-17 slice); `docs/audits/SF_NAV1_D1_THE_A2_ANCHOR_2026_10_04.md`
is the research. These pins hold:

1. SF7-X1 — the decline list reads the STORED dialogue shape a stale
   answer's refusal re-carries (its court in `context.source_nation`, an
   incoming proposal's in `target_nation`), and never the player's own
   confirms; the lever down reproduces the defect.
2. `policy_at` — the script's own dials change from a given loop on.
3. The research arms are committed in the shape the memo cites, and the
   archived records read what the memo says.
"""

from __future__ import annotations

import argparse
import importlib
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIGESTS = ROOT / "docs" / "audits" / "playtest_digests"
SCRIPTS = ROOT / "tools" / "playtest_scripts"


@pytest.fixture(scope="module")
def D():
    return importlib.import_module("tools.playtest_driver")


def _answerer(D, **policy):
    return D.Answerer(None, None, dict(D.POLICY_DEFAULTS) | policy, False)


# The STORED incoming proposal — the shape `ai_diplomacy` builds and
# `diplomatic_executor`'s W6-0 binding returns on a stale answer.
STORED_ARMISTICE = {
    "type": "incoming_proposal",
    "target_nation": "Hanover",
    "options": [
        {"label": "Accept", "action": "accept_ai_proposal"},
        {"label": "Reject", "action": "reject_ai_proposal"},
    ],
    "context": {"source_nation": "Hanover", "proposal_type": "armistice"},
    "dialogue_id": 21,
}


class TestTheDeclineListReadsTheStoredShape:
    """SF7-X1: Step 6's NAV1-H arm signed Portugal's armistice on turn 20 under
    `--decline-from Portugal`; the conquest drafts signed Hanover's, Portugal's
    and Naples's on 8 of 12 runs."""

    def test_the_stored_shape_names_its_court(self, D):
        assert D._court_of(dict(STORED_ARMISTICE)) == "Hanover"

    def test_the_context_alone_names_the_court(self, D):
        # A counter-offer's stored shape carries only the context.
        assert D._court_of({"type": "counter_offer",
                            "context": {"source_nation": "Portugal"}}) == "Portugal"

    def test_a_declined_court_is_refused_on_the_stored_shape(self, D):
        a = _answerer(D, diplomacy="accept", decline_from="Hanover")
        assert a._pick_dialogue_choice(dict(STORED_ARMISTICE)) == "reject_ai_proposal"

    def test_an_undeclined_court_is_still_accepted(self, D):
        a = _answerer(D, diplomacy="accept", decline_from="Britain")
        assert a._pick_dialogue_choice(dict(STORED_ARMISTICE)) == "accept_ai_proposal"

    def test_the_players_own_confirm_is_never_read_as_an_envoy(self, D):
        # target_nation on the player's confirm is the court France writes TO.
        assert D._court_of({"type": "proposal_confirm", "target_nation": "Austria"}) == ""

    def test_the_lever_down_reproduces_the_defect(self, D, monkeypatch):
        monkeypatch.setattr(D, "THE_DECLINE_LIST_READS_THE_STORED_SHAPE", False)
        assert D._court_of(dict(STORED_ARMISTICE)) == ""
        a = _answerer(D, diplomacy="accept", decline_from="Hanover")
        assert a._pick_dialogue_choice(dict(STORED_ARMISTICE)) == "accept_ai_proposal"


class _StubTransport:
    label = "stub"

    def __init__(self, gets):
        self.posts = []
        self.gets = gets

    def post(self, path, payload=None):
        self.posts.append((path, payload))
        return {"success": True, "message": "ok"}

    def get(self, path):
        return dict(self.gets.get(path, {}))


def _args(tmp_path, script_path, turns):
    return argparse.Namespace(
        script=str(script_path), name="policy_at", seed="historical", llm="mock",
        scenario="", out=str(tmp_path), fresh=False, objection="", diplomacy="",
        redemption="", petition="", paradox="", rebellion="", sabotage="", reward="",
        last_stand="", contact="", http=False, strict=False, turns=turns, save_at="",
        from_save="", cheats=False, reload_every=0, verbose=False, archive=False)


class TestPolicyAt:
    def _run(self, D, monkeypatch, tmp_path, script):
        script_path = tmp_path / "script.json"
        script_path.write_text(json.dumps(script), encoding="utf-8")
        transport = _StubTransport(gets={"/status": {"turn": 1}})
        monkeypatch.setattr(D, "make_inprocess_transport", lambda args, out_dir: transport)
        seen = {}
        real = D.Answerer

        class Spy(real):
            def __init__(self, transport, digest, policy, strict):
                super().__init__(transport, digest, policy, strict)
                seen["policy"] = policy

        monkeypatch.setattr(D, "Answerer", Spy)
        D.run(_args(tmp_path, script_path, 2))
        md = (tmp_path / "policy_at" / "digest.md").read_text(encoding="utf-8")
        return seen["policy"], md

    def test_the_dial_changes_from_its_loop(self, D, monkeypatch, tmp_path):
        policy, md = self._run(D, monkeypatch, tmp_path, {
            "turns": {},
            "policy": {"diplomacy": "accept"},
            "policy_at": {"2": {"decline_from": "Hanover,Austria"}},
        })
        # The answerer holds the run's own dict: the change reached it.
        assert policy["decline_from"] == "Hanover,Austria"
        assert "POLICY decline_from -> Hanover,Austria" in md
        # ... from loop 2, not before: the note sits under the second header
        # and not under the first.
        sections = md.split("## Turn")
        assert len(sections) >= 3, md
        assert "POLICY decline_from" not in sections[1]
        assert "POLICY decline_from" in sections[2]

    def test_a_script_without_the_key_notes_nothing(self, D, monkeypatch, tmp_path):
        policy, md = self._run(D, monkeypatch, tmp_path, {"turns": {}})
        assert "POLICY " not in md
        assert not policy.get("decline_from")


class TestTheResearchArms:
    """The memo cites two committed drafts and their archived records."""

    @pytest.mark.parametrize("name", ["sf_nav1_conquest_road.json",
                                      "sf_nav1_conquest_danube.json"])
    def test_the_drafts_are_committed(self, name):
        script = json.loads((SCRIPTS / name).read_text(encoding="utf-8"))
        lines = [line for loop in script["turns"].values() for line in loop]
        assert any("Hanover" in line for line in lines), name
        assert any("Lisbon" in line for line in lines), name

    def test_the_danube_draft_refuses_austria_until_loop_nine(self):
        script = json.loads((SCRIPTS / "sf_nav1_conquest_danube.json").read_text(encoding="utf-8"))
        assert "Austria" not in script["policy_at"]["9"]["decline_from"].split(",")
        assert any("take Vienna" in line for loop in script["turns"].values() for line in loop)

    @pytest.mark.parametrize("seed", ["historical", "austerlitz", "marengo"])
    @pytest.mark.parametrize("road", ["danube", "road"])
    def test_the_archived_records_never_hold_past_spains_exit(self, road, seed):
        probe = json.loads((DIGESTS / f"sfnav1d1-{road}-{seed}" / "probe.json")
                           .read_text(encoding="utf-8"))
        summary = probe["summary"]
        exit_turn = summary["spain_exit_turn"]
        assert exit_turn is not None
        held_after = [t for t in summary["holds_turns"] if t > exit_turn]
        assert held_after == [], (road, seed, held_after)
        # The memo's peaks: 10–13 of 26, tier 2 (16) never reached.
        assert 10 <= summary["peak_closed"] <= 13, (road, seed, summary["peak_closed"])
        assert summary["peak_tier"] <= 1

    def test_no_archived_draft_signed_a_declined_court(self):
        for path in DIGESTS.glob("sfnav1d1-*/digest.md"):
            text = path.read_text(encoding="utf-8")
            for court in ("Hanover", "Portugal", "Naples", "Britain"):
                assert f"You have accepted {court}'s proposal" not in text, (path, court)
