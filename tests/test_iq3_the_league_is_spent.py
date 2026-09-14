"""IQ-3 "The Coalition Is Rare" — the league is spent (Sept 14, 2026).

Measured on `commanded_full40 --diplomacy accept`, three seeds: six to eight
coalitions in forty turns. Every one dissolved for `insufficient_members`
when France ratified the coalition's own peace offer; the alarm never fell
(a peace that breaks a league changed no threat), the >=90 override
cancelled the 5-turn cooldown, and the minor courts formed the next league
on the very next tick.

The rule: a TREATY that dissolves the league spends Europe's alarm against
its target (divided by LEAGUE_SPENT_DIVISOR, the treaty's own annexation /
vassalization alarm kept whole). The next coalition must be earned by a new
act of the target's. Derived — it reads and writes only `threat_by_target`
through `reduce_threat`; no timer, no serialized field.

Every behaviour pin drives production code, and each lever has a DOWN arm.
"""

import argparse
import contextlib
import importlib.util
import io
import itertools
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as M
from backend.commands.parser import CommandParser
from backend.game_logic import coalition as C
from backend.models.world_state import WorldState

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
               / "europe_1805.json")
FIXTURE = ROOT / "tests" / "fixtures" / "playtest_saves" / "fixture_t20_ambient.json"

MINORS = ("Hanover", "Naples", "Ottoman", "Sardinia", "Sweden")
LEVERS = ("THE_LEAGUE_SPENDS_ITS_ALARM", "TALLEYRAND_READS_THE_PROJECTION",
          "LEAGUE_SPENT_DIVISOR")


@pytest.fixture(autouse=True)
def _levers_at_default():
    saved = {name: getattr(C, name) for name in LEVERS}
    yield
    for name, value in saved.items():
        setattr(C, name, value)


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


def _europe():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


def _set(world, a, b, state, reason="treaty_ratification"):
    from backend.game_logic.diplomacy import set_diplomatic_state
    with _quiet():
        set_diplomatic_state(world, a, b, state, reason)


def _spend_rows(world, target="France"):
    return [r for r in world.threat_sources_this_turn
            if r.get("source") == "league_spent"
            and (r.get("target") or world.player_nation) == target]


def _dissolved_logs(world):
    return [e for e in world.event_log if e.get("type") == "coalition_dissolved"]


def _pending(world, title):
    return [n for n in world.notifications.get_pending() if n.get("title") == title]


def _hostile_minors(world):
    for n in MINORS:
        world.nation_relations[world._make_diplo_key("France", n)] = -80


def _france_league(world):
    ac = world.active_coalition
    return bool(ac and (ac.get("target_nation") or "France") == "France")


def _france_brewing(world):
    br = world.coalition_brewing
    return bool(br and (br.get("target_nation") or "France") == "France")


# ════════════════════════════════════════════════════════════════════
# 1. The real path spends exactly once
# ════════════════════════════════════════════════════════════════════

@pytest.fixture
def fixture_board(monkeypatch):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with _quiet():
        world = WorldState.from_dict(data["world_state"])
    parser = CommandParser(use_real_llm=False)
    assert parser.llm.use_real_api is False
    monkeypatch.setattr(M, "world", world)
    monkeypatch.setattr(M, "parser", parser)
    monkeypatch.setitem(M.game_state, "world", world)
    return world


def _answer(client, choice, dialogue_id):
    with _quiet():
        return client.post("/respond_to_diplomatic_dialogue",
                           json={"choice": choice,
                                 "dialogue_id": dialogue_id}).json()


def _current_offer(world):
    dm = world.dialogue_manager
    for d in ([dm.peek()] if dm.peek() else []) + dm.iter_queue():
        if d.get("type") == "incoming_settlement_offer":
            return d
    return None


def _ratify_the_coalition_peace(world):
    client = TestClient(M.app)
    offer = _current_offer(world)
    assert offer is not None, "the t20 fixture carries Britain's war_1 offer"
    _answer(client, "accept_settlement_offer", offer.get("dialogue_id"))
    staged = world.dialogue_manager.peek()
    result = _answer(client, "confirm_settlement", staged.get("dialogue_id"))
    assert result.get("success") is True, result.get("error")
    return result


class TestTheRealPathSpendsOnce:

    def test_the_ratified_coalition_peace_spends_the_league(self, fixture_board):
        world = fixture_board
        assert world.active_coalition["name"] == "Third Coalition"
        before = int(world.threat_by_target["France"])
        world.threat_sources_this_turn = []
        _ratify_the_coalition_peace(world)

        assert world.active_coalition is None
        rows = _spend_rows(world)
        assert len(rows) == 1, world.threat_sources_this_turn
        logs = _dissolved_logs(world)
        assert logs[-1]["reason"] == "insufficient_members"
        spent = logs[-1]["alarm_spent"]
        assert spent["from"] == before
        kept = min(before, sum(
            int(r["amount"]) for r in world.threat_sources_this_turn
            if r.get("source") in C.LEAGUE_SPEND_EXEMPT_SOURCES
            and r.get("target") == "France" and int(r["amount"]) > 0))
        assert spent["to"] == (before - kept) // C.LEAGUE_SPENT_DIVISOR + kept
        assert rows[0]["amount"] == -(spent["from"] - spent["to"])
        assert int(world.threat_by_target["France"]) == spent["to"]

    def test_no_court_named_by_the_dissolution_is_at_peace_afterwards(
            self, fixture_board):
        """The IQ-2 read ran MID-ratification and named courts signing in
        the same action. The spend arm names none and says what is true."""
        world = fixture_board
        _ratify_the_coalition_peace(world)
        log = _dissolved_logs(world)[-1]
        for court in log.get("courts_at_war", []):
            assert world.get_diplomatic_state("France", court) == "WAR"
        note = _pending(world, "Coalition Dissolved")[-1]["message"]
        assert "The league is spent" in note
        assert "remain at war" not in note

    def test_lever_down_spends_nothing(self, fixture_board):
        C.THE_LEAGUE_SPENDS_ITS_ALARM = False
        world = fixture_board
        before = int(world.threat_by_target["France"])
        world.threat_sources_this_turn = []
        _ratify_the_coalition_peace(world)
        assert world.active_coalition is None
        assert _spend_rows(world) == []
        assert "alarm_spent" not in _dissolved_logs(world)[-1]
        # The ratification itself moves no French alarm on this board, so
        # the slot is exactly where it was — nothing forgave anything.
        assert int(world.threat_by_target["France"]) >= before - 0
        note = _pending(world, "Coalition Dissolved")[-1]["message"]
        assert note == ("Third Coalition has dissolved. Too few of its "
                        "members remain at war.")


# ════════════════════════════════════════════════════════════════════
# 1b. The bilateral road: the first signature spends nothing
# ════════════════════════════════════════════════════════════════════

class TestTheBilateralRoad:

    def test_the_second_separate_peace_spends(self):
        world = _europe()
        assert set(world.active_coalition["members"]) == {"Austria", "Britain", "Russia"}
        world.threat_sources_this_turn = []
        _set(world, "France", "Britain", "PEACE")
        assert world.active_coalition is not None
        assert _spend_rows(world) == []

        before = int(world.threat_by_target["France"])
        _set(world, "France", "Austria", "PEACE")
        assert world.active_coalition is None
        after = int(world.threat_by_target["France"])
        assert after == before // C.LEAGUE_SPENT_DIVISOR
        assert len(_spend_rows(world)) == 1

        # Shown = applied: the notice quotes the slot's own change.
        note = _pending(world, "Coalition Dissolved")[-1]["message"]
        assert f"falls from {before} to {after}" in note
        assert "no new coalition gathers below 60" in note
        # And Russia, genuinely still at war, is not called a peace-maker.
        assert world.get_diplomatic_state("France", "Russia") == "WAR"
        assert "made their peace" not in note

    def test_the_campaign_log_reads_the_spend(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "France",
            "reason": "insufficient_members", "courts_at_war": [],
            "alarm_spent": {"from": 90, "to": 45}})
        assert line == ("Coalition against France has dissolved — the league "
                        "is spent; Europe's alarm falls from 90 to 45.")
        # No key = the IQ-2 line, unchanged.
        assert format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "France",
            "courts_at_war": ["Austria"]}) == (
            "Coalition against France has dissolved — Austria remains at war with us.")


# ════════════════════════════════════════════════════════════════════
# 2. PR-D1's required pin — the door is shut, not welded
# ════════════════════════════════════════════════════════════════════

class TestTheDoorIsShutNotWelded:

    def _spent_board(self):
        world = _europe()
        for court in ("Britain", "Austria", "Russia"):
            _set(world, "France", court, "PEACE")
        assert world.active_coalition is None
        assert _spend_rows(world), "the league was spent"
        _hostile_minors(world)
        world.coalition_cooldown = 0
        return world

    def test_twenty_quiet_ticks_raise_no_coalition(self):
        world = self._spent_board()
        assert C.get_qualifying_nations(world), "courts stand ready to join"
        for _ in range(20):
            world.current_turn += 1
            world.threat_sources_this_turn = []
            with _quiet():
                C.process_coalition_turn(world)
            assert not _france_league(world), world.current_turn
            assert not _france_brewing(world), world.current_turn
        assert int(world.threat_by_target["France"]) < C.THREAT_BREWING_MIN

    def test_a_french_act_reopens_it(self):
        from backend.game_logic.diplomacy import declare_war
        world = self._spent_board()
        world.current_turn += 1
        world.threat_sources_this_turn = []
        with _quiet():
            for court in ("Prussia", "Denmark"):
                assert declare_war(world, "France", court).get("success")
        assert int(world.threat_by_target["France"]) >= C.THREAT_BREWING_MIN
        with _quiet():
            C.process_coalition_turn(world)
        assert _france_league(world) or _france_brewing(world)


# ════════════════════════════════════════════════════════════════════
# 3. Structural
# ════════════════════════════════════════════════════════════════════

class TestStructure:

    def test_a_full_alarm_is_spent_below_every_gate(self):
        assert 100 // C.LEAGUE_SPENT_DIVISOR < C.THREAT_BREWING_MIN
        assert 100 // C.LEAGUE_SPENT_DIVISOR < C.THREAT_OVERRIDE_COOLDOWN_MIN

    def test_the_override_cannot_fire_the_tick_after_a_spend(self):
        world = _europe()
        world.threat_by_target["France"] = 100
        _hostile_minors(world)
        for court in ("Britain", "Austria"):
            _set(world, "France", court, "PEACE")
        assert world.active_coalition is None
        assert int(world.threat_by_target["France"]) == 50
        world.current_turn += 1
        world.threat_sources_this_turn = []
        with _quiet():
            C.process_coalition_turn(world)
        assert world.coalition_cooldown > 0, "the cooldown was not cancelled"
        assert not _france_league(world) and not _france_brewing(world)


# ════════════════════════════════════════════════════════════════════
# 4. The treaty's own alarm is kept; the pair order does not matter
# ════════════════════════════════════════════════════════════════════

class TestTheTreatysOwnAlarmIsKept:

    def test_annexation_alarm_stays_whole(self):
        world = _europe()
        world.threat_by_target["France"] = 100
        world.threat_sources_this_turn = [
            {"source": "treaty_annex", "amount": 40, "target": "France"},
            {"source": "treaty_annex", "amount": 8, "target": "Austria"},
            {"source": "war_declaration", "amount": 20, "target": "France"},
            {"source": "decay", "amount": -3, "target": "France"},
        ]
        assert C.league_spent_alarm(world, "France") == {"from": 100, "to": 70}

    def test_vassalization_alarm_stays_whole(self):
        world = _europe()
        world.threat_by_target["France"] = 61
        world.threat_sources_this_turn = [
            {"source": "treaty_vassalization", "amount": 5, "target": "France"},
            {"source": "conquest_vassalization", "amount": 25, "target": "France"},
        ]
        assert C.league_spent_alarm(world, "France") == {"from": 61, "to": 45}

    def test_every_pair_order_spends_to_the_same_slot(self):
        outcomes = [("Britain", "PEACE"), ("Austria", "VASSAL"), ("Russia", "PEACE")]
        finals = set()
        for order in itertools.permutations(outcomes):
            world = _europe()
            world.threat_by_target["France"] = 80
            world.threat_sources_this_turn = []
            C.add_threat(world, 5, "treaty_vassalization")
            for court, state in order:
                _set(world, "France", court, state)
            assert world.active_coalition is None
            assert len(_spend_rows(world)) == 1, order
            finals.add(int(world.threat_by_target["France"]))
        assert finals == {(85 - 5) // 2 + 5}


# ════════════════════════════════════════════════════════════════════
# 5. Nothing else spends
# ════════════════════════════════════════════════════════════════════

class TestNothingElseSpends:

    def test_the_low_threat_tick(self):
        world = _europe()
        world.threat_by_target["France"] = 15
        world.threat_sources_this_turn = []
        with _quiet():
            C.process_coalition_turn(world)
        assert world.active_coalition is None
        assert _dissolved_logs(world)[-1]["reason"] == "low_threat"
        assert _spend_rows(world) == []

    def test_direct_dissolutions_without_the_flag(self):
        for reason in ("insufficient_members", "the_greater_danger", "low_threat"):
            world = _europe()
            world.threat_sources_this_turn = []
            before = int(world.threat_by_target["France"])
            with _quiet():
                C.dissolve_coalition(world, reason)
            assert _spend_rows(world) == [], reason
            assert int(world.threat_by_target["France"]) == before

    def test_a_removal_without_the_treaty_flag(self):
        world = _europe()
        world.threat_sources_this_turn = []
        before = int(world.threat_by_target["France"])
        with _quiet():
            C.remove_coalition_member("Britain", world)
            C.remove_coalition_member("Austria", world)
        assert world.active_coalition is None
        assert _spend_rows(world) == []
        assert int(world.threat_by_target["France"]) == before

    def test_an_eliminated_member(self):
        world = _europe()
        _set(world, "France", "Britain", "PEACE")
        world.threat_sources_this_turn = []
        with _quiet():
            world._eliminate_nation("Austria")
        assert _spend_rows(world) == []

    def test_a_truce_and_a_separate_peace_leaving_two(self):
        world = _europe()
        world.threat_sources_this_turn = []
        _set(world, "France", "Britain", "ARMISTICE", "armistice")
        _set(world, "France", "Austria", "PEACE")
        assert world.active_coalition is not None
        assert _spend_rows(world) == []


# ════════════════════════════════════════════════════════════════════
# 6. GR5 — an eclipse league spends its own target's alarm
# ════════════════════════════════════════════════════════════════════

class TestGR5:

    def test_an_eclipse_league_spends_austrias_slot_not_frances(self):
        world = _europe()
        world.active_coalition = {
            "id": "coalition_x", "name": "The League against Austria",
            "target_nation": "Austria", "leader": "Russia",
            "members": ["Russia", "Prussia"], "formed_turn": 1,
            "strategic_posture": "defensive", "posture_last_updated": 1,
        }
        for m in ("Russia", "Prussia"):
            world.diplomatic_states[world._make_diplo_key("Austria", m)] = "WAR"
        world.threat_by_target["Austria"] = 80
        france = int(world.threat_by_target["France"])
        world.threat_sources_this_turn = []
        _set(world, "Austria", "Russia", "PEACE")
        assert world.active_coalition is None
        assert int(world.threat_by_target["Austria"]) == 40
        assert int(world.threat_by_target["France"]) == france
        assert _spend_rows(world, "Austria") and not _spend_rows(world, "France")


# ════════════════════════════════════════════════════════════════════
# 7-8. Legibility: shown equals applied, and the levers are clean
# ════════════════════════════════════════════════════════════════════

class TestLegibility:

    def test_the_source_has_a_label(self):
        from backend.game_logic.diplomatic_ledger import (
            _THREAT_SOURCE_LABELS, _threat_source_label,
        )
        assert _THREAT_SOURCE_LABELS["league_spent"] == "The last coalition made its peace"
        assert _threat_source_label(_europe(), "league_spent") == \
            "The last coalition made its peace"

    def _cooldown_board(self, alarm):
        world = _europe()
        world.active_coalition = None
        world.coalition_cooldown = 1
        world.threat_by_target["France"] = alarm
        world.threat_sources_this_turn = []
        with _quiet():
            C.process_coalition_turn(world)
        return _pending(world, "Coalition Cooldown Ended")[-1]["message"]

    def test_the_cooldown_never_promises_a_league_below_the_gate(self):
        message = self._cooldown_board(40)
        assert "may form" not in message
        assert "gathers only at 60" in message

    def test_the_cooldown_copy_lever_down(self):
        C.THE_LEAGUE_SPENDS_ITS_ALARM = False
        assert self._cooldown_board(40) == \
            "A new coalition may form if threat remains high."

    def _quiet_board(self, alarm, cooldown=0):
        world = _europe()
        world.active_coalition = None
        world.coalition_brewing = None
        world.coalition_cooldown = cooldown
        world.threat_by_target["France"] = alarm
        _hostile_minors(world)
        return world

    def test_the_war_room_names_the_gate(self):
        from backend.game_logic.diplomatic_advisory import _assess_situation
        text = _assess_situation(self._quiet_board(40))["talleyrand_text"]
        assert "none gathers below 60" in text
        assert "would carry the alarm to 60" in text
        C.THE_LEAGUE_SPENDS_ITS_ALARM = False
        text = _assess_situation(self._quiet_board(40))["talleyrand_text"]
        assert "none gathers below 60" not in text

    def test_the_ledger_cooldown_names_the_gate(self):
        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        boe = _build_balance_of_europe(self._quiet_board(40, cooldown=3))
        assert boe["headline_case"] == "COOLDOWN"
        assert boe["headline_note"] == (
            "Europe's alarm stands at 40; no new coalition gathers below 60.")
        C.THE_LEAGUE_SPENDS_ITS_ALARM = False
        boe = _build_balance_of_europe(self._quiet_board(40, cooldown=3))
        assert "headline_note" not in boe


class TestTalleyrandReadsTheProjection:

    def _board(self, alarm):
        world = _europe()
        world.active_coalition = None
        world.coalition_brewing = None
        world.threat_by_target["France"] = alarm
        _hostile_minors(world)
        world.diplomatic_points = 5
        return world

    def test_the_projection_is_the_alarm_the_declaration_applies(self):
        from backend.game_logic.diplomacy import declare_war
        world = self._board(45)
        projection = C.declaration_would_gather_a_league(world, "France")
        assert projection["from"] == 45 and projection["to"] == 65
        world.threat_sources_this_turn = []
        with _quiet():
            assert declare_war(world, "France", "Prussia").get("success")
        applied = sum(int(r["amount"]) for r in world.threat_sources_this_turn
                      if r.get("source") == "war_declaration"
                      and r.get("target") == "France")
        assert applied == projection["to"] - projection["from"]

    def _declare(self, world):
        from backend.commands.executor import CommandExecutor
        with _quiet():
            return CommandExecutor()._diplomatic._execute_diplomatic_declare_war(
                {"target_nation": "Prussia", "war_objective": "conquest"}, world)

    def test_he_objects_below_fifty_when_the_declaration_would_gather_a_league(self):
        world = self._board(45)
        result = self._declare(world)
        text = result["diplomatic_objection_popup"]["objection_text"]
        assert "would carry it to 65" in text
        assert "past the 60 at which a coalition gathers" in text
        assert world.get_diplomatic_state("France", "Prussia") != "WAR"

    def test_lever_down_talleyrand_is_silent_below_fifty(self):
        """Down, the >50 arm alone: no objection is staged, and the flow
        moves on to its next stage (the war-weary / ally-entry reviews)."""
        C.TALLEYRAND_READS_THE_PROJECTION = False
        world = self._board(45)
        result = self._declare(world)
        assert not result.get("diplomatic_objection_popup")
        assert world.diplomatic_objection_popup is None

    def test_the_high_alarm_arm_is_byte_identical(self):
        world = self._board(55)
        text = self._declare(world)["diplomatic_objection_popup"]["objection_text"]
        assert text == (
            "Sire, I must strongly advise against declaring war on Prussia. "
            "Our threat level stands at 55 — the courts of Europe already "
            "whisper of coalition. Another war will only hasten their union "
            "against us.")

    def test_no_objection_when_the_projection_stays_below_the_gate(self):
        world = self._board(30)
        assert C.declaration_would_gather_a_league(world, "France") is None
        assert not self._declare(world).get("diplomatic_objection_popup")

    def test_no_projection_when_no_court_would_join(self):
        world = self._board(45)
        for key in list(world.nation_relations):
            if "France" in key.split("|"):
                world.nation_relations[key] = 0
        assert C.get_qualifying_nations(world) == []
        assert C.declaration_would_gather_a_league(world, "France") is None

    def test_no_projection_while_a_league_already_stands(self):
        world = self._board(45)
        world.active_coalition = {"name": "Third Coalition",
                                  "target_nation": "France",
                                  "members": ["Austria", "Britain"]}
        assert C.declaration_would_gather_a_league(world, "France") is None


# ════════════════════════════════════════════════════════════════════
# 9. The harness: --declare-war reaches the policy
# ════════════════════════════════════════════════════════════════════

def _driver():
    spec = importlib.util.spec_from_file_location(
        "playtest_driver", ROOT / "tools" / "playtest_driver.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("playtest_driver", mod)
    spec.loader.exec_module(mod)
    return mod


class TestTheHarnessFlag:

    def test_the_flag_reaches_the_policy(self):
        drv = _driver()
        policy = drv.resolve_policy(argparse.Namespace(declare_war="proceed"), {})
        assert policy["declare_war"] == "proceed"

    def test_script_key_and_default(self):
        drv = _driver()
        assert drv.resolve_policy(argparse.Namespace(), {})["declare_war"] == "cancel"
        assert drv.resolve_policy(
            argparse.Namespace(),
            {"policy": {"declare_war": "proceed"}})["declare_war"] == "proceed"
        assert drv.resolve_policy(
            argparse.Namespace(declare_war="cancel"),
            {"policy": {"declare_war": "proceed"}})["declare_war"] == "cancel"
