"""IQ-4 S4 — the playtest driver's `--missions` dial and the Cabinet advisor.

Before IQ-4 nothing in the harness ever chose a Talleyrand mission (0
launches in 360 driven turns), so "not one mission type" measured the
harness, not the game. These pins hold the instrument that asks:

* the policy key `missions` rides `resolve_policy` (flag over script over
  default) and is ABSENT unless set, so every pre-IQ-4 digest header — which
  prints the policy verbatim — is unchanged;
* with the dial off, a mission confirm is answered exactly as it was before
  it had a row in the answer table (the diplomacy mirror);
* the advisor chooses ONLY among Cabinet rows the preview marks available,
  types the wizard's own command text, sends a prepared treaty at ACCEPT and
  recalls only once Talleyrand is home, and never ends a mission it did not
  send;
* the digest prints one MISSION line per live turn and nothing when idle.
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "tools" / "playtest_driver.py"
WIZARD = (ROOT / "godot-client" / "project-sovereign" / "scripts"
          / "diplomacy_wizard.gd")


def _driver():
    spec = importlib.util.spec_from_file_location("playtest_driver", DRIVER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("playtest_driver", mod)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def drv():
    return _driver()


def _answerer(drv, **policy):
    return drv.Answerer(None, None, dict(drv.POLICY_DEFAULTS, **policy), False)


def _mission_dialogue():
    return {
        "type": "mission", "target_nation": "Prussia",
        "options": [
            {"label": "Begin mission", "action": "start_mission",
             "terms": {"mission_type": "COURT_NATION", "target_nation": "Prussia"}},
            {"label": "Not now", "action": "dismiss"},
        ],
    }


def _cancel_dialogue():
    return {
        "type": "mission", "target_nation": "Prussia",
        "options": [
            {"label": "Confirm cancel", "action": "cancel_mission"},
            {"label": "Continue mission", "action": "dismiss"},
        ],
    }


def _undermine_dialogue():
    return {
        "type": "mission", "target_nation": "Austria",
        "options": [
            {"label": "Bavaria", "action": "start_mission",
             "terms": {"mission_type": "UNDERMINE_ALLIANCE",
                       "target_nation": "Austria", "target_ally": "Bavaria"}},
            {"label": "Russia", "action": "start_mission",
             "terms": {"mission_type": "UNDERMINE_ALLIANCE",
                       "target_nation": "Austria", "target_ally": "Russia"}},
            {"label": "Not now", "action": "dismiss"},
        ],
    }


def _dismiss_only():
    return {"type": "mission", "target_nation": "Austria",
            "options": [{"label": "Dismiss", "action": "dismiss"}]}


# ════════════════════════════════════════════════════════════════════
# 1. The dial reaches the policy — and is absent unless set
# ════════════════════════════════════════════════════════════════════

class TestResolvePolicyCarriesMissions:

    def test_the_flag_reaches_the_policy(self, drv):
        policy = drv.resolve_policy(argparse.Namespace(missions="advisor"), {})
        assert policy["missions"] == "advisor"
        assert drv.missions_mode(policy) == "advisor"

    def test_script_key_and_flag_precedence(self, drv):
        script = {"policy": {"missions": "advisor"}}
        assert drv.resolve_policy(argparse.Namespace(), script)["missions"] == "advisor"
        assert drv.resolve_policy(
            argparse.Namespace(missions="off"), script)["missions"] == "off"

    def test_absent_by_default_so_the_header_is_unchanged(self, drv):
        """The digest header prints `json.dumps(policy)`; a default run must
        print exactly what it printed before IQ-4."""
        policy = drv.resolve_policy(argparse.Namespace(), {})
        assert "missions" not in policy
        assert "missions" not in drv.POLICY_DEFAULTS
        assert json.dumps(policy) == json.dumps(dict(drv.POLICY_DEFAULTS))
        assert drv.missions_mode(policy) == "off"

    def test_an_unknown_value_reads_as_off(self, drv):
        assert drv.missions_mode({"missions": "sometimes"}) == "off"
        assert drv.missions_mode(None) == "off"

    def test_the_confirm_rides_its_own_row(self, drv):
        assert drv.DIALOGUE_TYPE_ANSWERS["mission"] == "missions"
        assert "missions" in drv.POLICY_FLAG_KEYS

    def test_the_cli_parses_the_dial(self):
        env = dict(os.environ, PYTHONHASHSEED="0")
        out = subprocess.run([sys.executable, str(DRIVER), "--help"],
                             capture_output=True, env=env, cwd=str(ROOT),
                             encoding="utf-8", errors="replace", timeout=120)
        assert out.returncode == 0, out.stderr
        assert "--missions" in out.stdout
        # argparse spells the choices with the "" (unset) arm first, as it
        # does for every dial here: `{,off,advisor}`.
        assert "{,off,advisor}" in out.stdout


# ════════════════════════════════════════════════════════════════════
# 2. The default mirrors --diplomacy
# ════════════════════════════════════════════════════════════════════

class TestTheDefaultMirrorsDiplomacy:

    @pytest.mark.parametrize("mode", ["decline", "accept", "first", "propose"])
    @pytest.mark.parametrize("shape", [_mission_dialogue, _cancel_dialogue,
                                       _undermine_dialogue, _dismiss_only])
    def test_the_answer_it_got_before_the_row(self, drv, monkeypatch, mode, shape):
        with_row = _answerer(drv, diplomacy=mode)._dialogue_choice(shape())
        monkeypatch.delitem(drv.DIALOGUE_TYPE_ANSWERS, "mission")
        before = _answerer(drv, diplomacy=mode)._dialogue_choice(shape())
        assert with_row == before

    def test_no_options_list_is_still_left_standing(self, drv, monkeypatch):
        """The keyword-less fallback ("decline" / "1") must not newly reach
        a mission confirm just because it now has a table row."""
        bare = {"type": "mission", "target_nation": "Prussia"}
        for mode in ("decline", "accept"):
            assert _answerer(drv, diplomacy=mode)._dialogue_choice(dict(bare)) is None

    def test_the_mirror_values(self, drv):
        assert _answerer(drv, diplomacy="decline")._dialogue_choice(
            _mission_dialogue()) == "dismiss"
        assert _answerer(drv, diplomacy="accept")._dialogue_choice(
            _mission_dialogue()) == "start_mission"


# ════════════════════════════════════════════════════════════════════
# 3. The advisor answers its own intent
# ════════════════════════════════════════════════════════════════════

class TestTheAdvisorAnswers:

    def test_it_begins_even_under_decline(self, drv):
        answerer = _answerer(drv, diplomacy="decline", missions="advisor")
        assert answerer._dialogue_choice(_mission_dialogue()) == "start_mission"

    def test_a_recall_confirms_the_cancel(self, drv):
        answerer = _answerer(drv, diplomacy="accept", missions="advisor")
        answerer.mission_intent = {"kind": "recall"}
        assert answerer._dialogue_choice(_cancel_dialogue()) == "cancel_mission"

    def test_undermine_answers_the_ally_by_index(self, drv):
        answerer = _answerer(drv, diplomacy="decline", missions="advisor")
        answerer.mission_intent = {"kind": "begin", "ally": "Russia"}
        assert answerer._dialogue_choice(_undermine_dialogue()) == "2"
        answerer.mission_intent = {"kind": "begin", "ally": "Bavaria"}
        assert answerer._dialogue_choice(_undermine_dialogue()) == "1"

    def test_a_dismiss_only_refusal_falls_back_to_the_diplomacy_read(self, drv):
        answerer = _answerer(drv, diplomacy="decline", missions="advisor")
        assert answerer._dialogue_choice(_dismiss_only()) == "dismiss"


# ════════════════════════════════════════════════════════════════════
# 4. The advisor chooses only among available rows
# ════════════════════════════════════════════════════════════════════

def _row(action, available=True, score=None):
    row = {"action": action, "available": available}
    if score is not None:
        row["likelihood_score"] = score
    return row


def _previews(table):
    def preview_of(name):
        return table.get(name, {})
    return preview_of


class TestTheAdvisorPicksOnlyAvailableRows:

    def test_counsel_picks_the_court_whose_row_is_open(self, drv):
        categories = {"neutral": [{"name": "Prussia", "state": "PEACE", "relation": 60},
                                  {"name": "Saxony", "state": "PEACE", "relation": 20}]}
        previews = _previews({
            "Prussia": {"recommended_mission": "COURT_NATION",
                        "actions": [_row("mission_court", available=False),
                                    _row("propose_alliance", score=48)]},
            "Saxony": {"recommended_mission": "IMPROVE_RELATIONS",
                       "actions": [_row("mission_improve_relations"),
                                   _row("propose_alliance", score=20)]},
        })
        choice = drv.MissionAdvisor().pick(categories, previews, [], 1)
        assert choice["nation"] == "Saxony"
        assert choice["action"] == "mission_improve_relations"
        assert choice["prepared"] == "propose_alliance"

    def test_nothing_available_means_nothing_sent(self, drv):
        categories = {
            "at_war": [{"name": "Austria", "state": "WAR", "relation": -80}],
            "treaties": [{"name": "Bavaria", "state": "ALLIANCE", "relation": 10}],
            "neutral": [{"name": "Prussia", "state": "PEACE", "relation": 60}],
        }
        closed = [_row(a, available=False) for a in (
            "mission_reassure", "mission_court", "mission_improve_relations",
            "mission_gather_intel", "mission_undermine")]
        previews = _previews({n: {"recommended_mission": "COURT_NATION",
                                  "actions": closed}
                              for n in ("Austria", "Bavaria", "Prussia")})
        rows = [{"name": "Austria", "regions_controlled": 9,
                 "ai_relations": [{"nation": "Russia", "state": "ALLIANCE"}]}]
        assert drv.MissionAdvisor().pick(categories, previews, rows, 1) is None

    def test_reassure_comes_first_and_needs_its_row(self, drv):
        categories = {"treaties": [{"name": "Bavaria", "state": "ALLIANCE", "relation": 30}],
                      "neutral": [{"name": "Saxony", "state": "PEACE", "relation": 20}]}
        table = {"Bavaria": {"actions": [_row("mission_reassure")]},
                 "Saxony": {"recommended_mission": "IMPROVE_RELATIONS",
                            "actions": [_row("mission_improve_relations")]}}
        choice = drv.MissionAdvisor().pick(categories, _previews(table), [], 1)
        assert (choice["branch"], choice["nation"]) == (1, "Bavaria")
        table["Bavaria"] = {"actions": [_row("mission_reassure", available=False)]}
        choice = drv.MissionAdvisor().pick(categories, _previews(table), [], 1)
        assert (choice["branch"], choice["nation"]) == (2, "Saxony")

    def test_a_healthy_ally_is_not_reassured(self, drv):
        categories = {"treaties": [{"name": "Bavaria", "state": "ALLIANCE", "relation": 50}]}
        table = {"Bavaria": {"actions": [_row("mission_reassure")]}}
        assert drv.MissionAdvisor().pick(categories, _previews(table), [], 1) is None

    def test_the_smallest_accept_gap_goes_first(self, drv):
        categories = {"neutral": [{"name": "Denmark", "state": "PEACE", "relation": 10},
                                  {"name": "Prussia", "state": "PEACE", "relation": 60}]}
        table = {
            "Denmark": {"recommended_mission": "IMPROVE_RELATIONS",
                        "actions": [_row("mission_improve_relations"),
                                    _row("propose_non_aggression", score=30)]},
            "Prussia": {"recommended_mission": "COURT_NATION",
                        "actions": [_row("mission_court"),
                                    _row("propose_alliance", score=48)]},
        }
        choice = drv.MissionAdvisor().pick(categories, _previews(table), [], 1)
        assert (choice["nation"], choice["action"]) == ("Prussia", "mission_court")

    def test_gather_takes_the_largest_enemy_whose_row_is_open(self, drv):
        categories = {"at_war": [{"name": "Austria", "state": "WAR"},
                                 {"name": "Russia", "state": "WAR"},
                                 {"name": "Britain", "state": "WAR"}]}
        rows = [{"name": "Austria", "regions_controlled": 9},
                {"name": "Russia", "regions_controlled": 14},
                {"name": "Britain", "regions_controlled": 5}]
        table = {"Russia": {"actions": [_row("mission_gather_intel", available=False)]},
                 "Austria": {"actions": [_row("mission_gather_intel")]},
                 "Britain": {"actions": [_row("mission_gather_intel")]}}
        advisor = drv.MissionAdvisor()
        choice = advisor.pick(categories, _previews(table), rows, 10)
        assert (choice["branch"], choice["nation"]) == (3, "Austria")
        advisor.last_intel_turn = 5
        assert advisor.pick(categories, _previews(table), rows, 10) is None
        assert advisor.pick(categories, _previews(table), rows, 13)["nation"] == "Austria"

    def test_undermine_needs_an_ally_at_war_with_france_too(self, drv):
        categories = {"at_war": [{"name": "Austria", "state": "WAR"},
                                 {"name": "Russia", "state": "WAR"}]}
        rows = [{"name": "Austria", "regions_controlled": 9, "ai_relations": [
                    {"nation": "Bavaria", "state": "ALLIANCE"},
                    {"nation": "Russia", "state": "ALLIANCE"}]},
                {"name": "Russia", "regions_controlled": 14, "ai_relations": [
                    {"nation": "Austria", "state": "WAR"}]}]
        table = {"Austria": {"actions": [_row("mission_undermine"),
                                         _row("mission_gather_intel", available=False)]},
                 "Russia": {"actions": [_row("mission_undermine"),
                                        _row("mission_gather_intel", available=False)]}}
        choice = drv.MissionAdvisor().pick(categories, _previews(table), rows, 1)
        assert (choice["branch"], choice["nation"], choice["ally"]) == (4, "Austria", "Russia")

    def test_a_benched_branch_sits_out_one_pick(self, drv):
        categories = {"neutral": [{"name": "Saxony", "state": "PEACE", "relation": 20}]}
        table = {"Saxony": {"recommended_mission": "IMPROVE_RELATIONS",
                            "actions": [_row("mission_improve_relations")]}}
        advisor = drv.MissionAdvisor()
        advisor.benched = 2
        assert advisor.pick(categories, _previews(table), [], 1) is None
        assert advisor.pick(categories, _previews(table), [], 2)["nation"] == "Saxony"


# ════════════════════════════════════════════════════════════════════
# 5. The advisor's turn, over a fake transport
# ════════════════════════════════════════════════════════════════════

class _FakeTransport:
    label = "fake"

    def __init__(self, cabinet, categories=None, previews=None, nations=None):
        self.cabinet = cabinet
        self.categories = categories or {}
        self.previews = previews or {}
        self.nations = nations or []
        self.posts = []
        self.answerer = None
        self.on_post = None

    def get(self, path):
        if path == "/ledger":
            body = {} if self.cabinet is None else {"cabinet": self.cabinet}
            return {"success": True, "ledger": body}
        if path == "/diplomatic_preview":
            return {"success": True, "mode": "nations", "categories": self.categories}
        if path.startswith("/diplomatic_preview?nation="):
            name = path.split("=", 1)[1]
            return self.previews.get(name, {"success": False})
        if path == "/diplomatic_ledger":
            return {"success": True, "ledger": {"nations": self.nations}}
        return {}

    def post(self, path, payload=None):
        intent = dict(self.answerer.mission_intent or {}) if self.answerer else {}
        self.posts.append((path, (payload or {}).get("command"), intent))
        if self.on_post:
            self.on_post(self, payload or {})
        return {"success": True, "message": "ok"}


def _harness(drv, tmp_path, transport, **policy):
    digest = drv.Digest(tmp_path, {"name": "iq4", "seed": "historical",
                                   "llm": "mock", "transport": "fake",
                                   "policy": {}})
    answerer = drv.Answerer(transport, digest,
                            dict(drv.POLICY_DEFAULTS, missions="advisor", **policy),
                            False)
    transport.answerer = answerer
    return digest, answerer


def _live(target="Prussia", mtype="COURT_NATION", started=1, pause_reason=""):
    return {"live": True, "type": mtype, "target": target, "started_turn": started,
            "paused": bool(pause_reason), "pause_reason": pause_reason,
            "recall_command": f"Talleyrand, cancel mission with {target}"}


class TestTheAdvisorTurn:

    def _court_world(self):
        transport = _FakeTransport(
            {"live": False},
            categories={"neutral": [{"name": "Prussia", "state": "PEACE", "relation": 60}]},
            previews={"Prussia": {"success": True, "recommended_mission": "COURT_NATION",
                                  "actions": [_row("mission_court"),
                                              _row("propose_alliance", score=48)]}})

        def launch(t, payload):
            if payload.get("command") == "court Prussia":
                t.cabinet = _live()
        transport.on_post = launch
        return transport

    def test_launch_types_the_wizard_command_under_its_intent(self, drv, tmp_path):
        transport = self._court_world()
        digest, answerer = _harness(drv, tmp_path, transport)
        advisor = drv.MissionAdvisor()
        advisor.turn(transport, digest, answerer, 1, False)
        assert [p[1] for p in transport.posts] == ["court Prussia"]
        assert transport.posts[0][2] == {"kind": "begin", "ally": None}
        assert answerer.mission_intent is None
        assert advisor.desk["prepared"] == "propose_alliance"
        assert "MISSION ADVISOR branch 2" in digest.md_path.read_text(encoding="utf-8")

    def test_the_prepared_treaty_goes_at_accept_and_the_recall_waits(self, drv, tmp_path):
        transport = self._court_world()
        digest, answerer = _harness(drv, tmp_path, transport)
        advisor = drv.MissionAdvisor()
        advisor.turn(transport, digest, answerer, 1, False)
        # Still a counter-offer: nothing sent.
        advisor.turn(transport, digest, answerer, 2, False)
        assert len(transport.posts) == 1
        # The favour carried it to ACCEPT.
        transport.previews["Prussia"]["actions"][1]["likelihood_score"] = 58

        def carry(t, payload):
            if payload.get("command") == "propose alliance with Prussia":
                t.cabinet = _live(pause_reason="transit")
        transport.on_post = carry
        advisor.turn(transport, digest, answerer, 3, False)
        assert transport.posts[-1][1] == "propose alliance with Prussia"
        assert advisor.desk["sent"] is True
        # In transit: never recalled (the favour is priced on the send).
        advisor.turn(transport, digest, answerer, 4, False)
        assert transport.posts[-1][1] == "propose alliance with Prussia"
        # Home: recalled, under the recall intent.
        transport.cabinet = _live()
        advisor.turn(transport, digest, answerer, 5, False)
        assert transport.posts[-1][1] == "Talleyrand, cancel mission with Prussia"
        assert transport.posts[-1][2] == {"kind": "recall"}
        assert advisor.desk is None

    def test_the_desk_limit_recalls_and_benches(self, drv, tmp_path):
        transport = self._court_world()
        digest, answerer = _harness(drv, tmp_path, transport)
        advisor = drv.MissionAdvisor()
        advisor.turn(transport, digest, answerer, 1, False)
        advisor.desk["prepared"] = None
        advisor.turn(transport, digest, answerer, 12, False)
        assert len(transport.posts) == 1
        advisor.turn(transport, digest, answerer, 13, False)
        assert transport.posts[-1][1] == "Talleyrand, cancel mission with Prussia"
        assert advisor.benched == 2

    def test_it_never_ends_a_mission_it_did_not_send(self, drv, tmp_path):
        transport = _FakeTransport(_live(target="Austria", started=1))
        digest, answerer = _harness(drv, tmp_path, transport)
        drv.MissionAdvisor().turn(transport, digest, answerer, 30, False)
        assert transport.posts == []

    def test_blind_without_a_cabinet(self, drv, tmp_path):
        transport = _FakeTransport(None)
        digest, answerer = _harness(drv, tmp_path, transport)
        advisor = drv.MissionAdvisor()
        advisor.turn(transport, digest, answerer, 1, False)
        advisor.turn(transport, digest, answerer, 2, False)
        assert transport.posts == []
        assert digest.md_path.read_text(encoding="utf-8").count("MISSION ADVISOR blind") == 1


# ════════════════════════════════════════════════════════════════════
# 6. The wizard's spelling is the driver's
# ════════════════════════════════════════════════════════════════════

def _wizard_command_arms():
    """`"<action_id>":` → the string prefix its arm returns, scraped from the
    body of the function that holds the `cancel_mission` arm."""
    src = WIZARD.read_text(encoding="utf-8")
    anchor = src.index('"cancel_mission":')
    start = src.rfind("\nfunc ", 0, anchor)
    end = src.find("\nfunc ", anchor)
    body = src[start:end if end != -1 else len(src)]
    return dict(re.findall(r'"([a-z_]+)":\s*\n\s*return\s+"([^"]*)"\s*\+\s*nation', body))


class TestTheWizardSpellingIsTheDrivers:

    def test_every_advisor_command_is_the_rows_own(self, drv):
        arms = _wizard_command_arms()
        for action_id, template in drv.WIZARD_COMMANDS.items():
            assert action_id in arms, action_id
            assert template == arms[action_id] + "{nation}", action_id

    def test_wizard_command_formats(self, drv):
        assert drv.wizard_command("mission_court", "Prussia") == "court Prussia"
        assert drv.wizard_command("cancel_mission", "PapalStates") == \
            "Talleyrand, cancel mission with PapalStates"
        assert drv.wizard_command("not_a_row", "Prussia") == ""


# ════════════════════════════════════════════════════════════════════
# 7. The digest's MISSION line
# ════════════════════════════════════════════════════════════════════

class TestTheDigestMissionLine:

    def _digest(self, drv, tmp_path):
        return drv.Digest(tmp_path, {"name": "iq4", "seed": "historical",
                                     "llm": "mock", "transport": "fake",
                                     "policy": {}})

    def test_idle_prints_nothing(self, drv, tmp_path):
        digest = self._digest(drv, tmp_path)
        before = digest.md_path.read_text(encoding="utf-8")
        digest.mission_line(None)
        digest.mission_line({"live": False})
        assert digest.md_path.read_text(encoding="utf-8") == before

    def test_a_live_mission_prints_its_line(self, drv, tmp_path):
        digest = self._digest(drv, tmp_path)
        digest.mission_line({"live": True, "type": "COURT_NATION",
                             "type_display": "Courting", "target": "Prussia",
                             "target_display": "Prussia", "net_per_turn": 7,
                             "remaining_note": "≈5 turns to +100 at the present rate"},
                            beat="running")
        text = digest.md_path.read_text(encoding="utf-8")
        assert ("- MISSION Courting — Prussia · net +7 a turn · ≈5 turns to "
                "+100 at the present rate · beat running") in text
        records = [json.loads(line) for line in
                   digest.jsonl_path.read_text(encoding="utf-8").splitlines()]
        assert records[-1]["kind"] == "mission" and records[-1]["net"] == 7

    def test_an_end_prints_once(self, drv, tmp_path):
        digest = self._digest(drv, tmp_path)
        idle = {"live": False, "last": {"type_display": "Gathering Intel",
                                        "target_display": "Austria",
                                        "reason": "duration",
                                        "reason_phrase": "done — 9 provinces open to us until turn 14"}}
        digest.mission_line(idle)
        digest.mission_line(idle)
        text = digest.md_path.read_text(encoding="utf-8")
        assert text.count("- MISSION ended: Gathering Intel — Austria, done — "
                          "9 provinces open to us until turn 14") == 1


# ════════════════════════════════════════════════════════════════════
# 8. Where the hook runs
# ════════════════════════════════════════════════════════════════════

class TestTheHookPlacement:

    def test_after_the_script_before_the_overture(self, drv):
        import inspect
        src = inspect.getsource(drv.run)
        hook = src.index("advisor.turn(")
        assert src.index("for text in turn_scripts.get(") < hook
        assert hook < src.index('if policy["diplomacy"] == "propose":')

    def test_the_mission_line_follows_the_ledger_line(self, drv):
        import inspect
        src = inspect.getsource(drv.run)
        assert src.index("digest.ledger_line(") < src.index("digest.mission_line(")
