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
        # The courts signing in this ratification are never named; a court
        # genuinely still at war (war_2's Switzerland here) may be.
        for court in ("Austria", "Britain", "Russia"):
            assert court not in log.get("courts_at_war", [])

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

    def test_a_treaty_that_leaves_a_low_threat_league_spends_nothing(self):
        """A treaty ejection that leaves TWO members standing while the alarm
        is below 20 dissolves the league for LOW THREAT, not for too few
        members. The spend is the treaty breaking the league, and this treaty
        did not break it — the alarm had already let it go."""
        world = _europe()
        assert len(world.active_coalition["members"]) == 3
        world.threat_by_target["France"] = 15
        world.threat_sources_this_turn = []
        _set(world, "France", "Britain", "PEACE")
        assert world.active_coalition is None
        assert _dissolved_logs(world)[-1]["reason"] == "low_threat"
        assert _spend_rows(world) == []
        assert int(world.threat_by_target["France"]) == 15

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
        assert "No league gathers below 60" in text
        assert "would carry the alarm to 60" in text
        C.THE_LEAGUE_SPENDS_ITS_ALARM = False
        text = _assess_situation(self._quiet_board(40))["talleyrand_text"]
        assert "No league gathers below 60" not in text

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

    def test_during_the_cooldown_he_speaks_conditionally(self):
        """The courts' cooldown still running: the declaration's 65 may decay
        below 60 before it lapses, so he promises nothing — measured on the
        austerlitz commanded arm, where no league gathered."""
        world = self._board(45)
        world.coalition_cooldown = 3
        text = self._declare(world)["diplomatic_objection_popup"]["objection_text"]
        assert "would carry it to 65" in text
        assert "3 turns yet" in text
        assert "if the alarm still stands at 60 when they have" in text
        assert "gathers, and" not in text.split("yet")[0]

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
        """+10 everywhere: the declaration's own −15 leaves every court at −5,
        still above the −10 line — nobody would join, so he says nothing.
        (At 0 the review round's correction applies: −15 carries them over.)"""
        world = self._board(45)
        # Every court explicitly — a court with no stored France key (Hesse)
        # falls back to the default relation, which −15 carries over the line.
        for n in list(world.get_active_nations()):
            if n != "France":
                world.nation_relations[world._make_diplo_key("France", n)] = 10
        assert C.get_qualifying_nations(world) == []
        assert C.declaration_would_gather_a_league(world, "France") is None

    def test_the_target_alone_does_not_make_a_league(self):
        """The declaration's target joins through the at-war arm, but a league
        needs a qualifying court besides it — a target who is the only court
        past −10 gathers nothing, and he does not object."""
        world = self._board(45)
        for n in list(world.get_active_nations()):
            if n != "France" and world.get_diplomatic_state("France", n) != "WAR":
                world.nation_relations[world._make_diplo_key("France", n)] = 10
        world.nation_relations[world._make_diplo_key("France", "Prussia")] = -5
        assert C.declaration_would_gather_a_league(world, "France",
                                                    target="Prussia") is None
        assert not self._declare(world).get("diplomatic_objection_popup")

    def test_no_projection_while_a_league_already_stands(self):
        world = self._board(45)
        world.active_coalition = {"name": "Third Coalition",
                                  "target_nation": "France",
                                  "members": ["Austria", "Britain"]}
        assert C.declaration_would_gather_a_league(world, "France") is None


# ════════════════════════════════════════════════════════════════════
# 10. The review round (Sept 14, 2026) — four lenses, one refuter each
# ════════════════════════════════════════════════════════════════════

def _declare_with(world, **data):
    from backend.commands.executor import CommandExecutor
    payload = {"target_nation": "Prussia", "war_objective": "conquest"}
    payload.update(data)
    with _quiet():
        return CommandExecutor()._diplomatic._execute_diplomatic_declare_war(
            payload, world)


def _talleyrand_board(alarm):
    world = _europe()
    world.active_coalition = None
    world.coalition_brewing = None
    world.threat_by_target["France"] = alarm
    _hostile_minors(world)
    world.diplomatic_points = 5
    return world


class TestTheReviewRoundSpend:

    def test_a_treaty_that_annexes_one_of_two_courts_whole_spends_the_league(self):
        """[P1→P2, NARROWED] The settlement's own elimination used to remove
        the member WITHOUT the treaty flag, so a two-court league dissolved
        unspent and the ≥90 override re-formed it on the next tick."""
        from backend.game_logic.settlement_ratify import _apply_settlement_terms
        world = _europe()
        _set(world, "France", "Britain", "PEACE")
        assert set(world.active_coalition["members"]) == {"Austria", "Russia"}
        russia = sorted(world.get_nation_regions("Russia"))
        for region in russia[1:]:
            world.regions[region].controller = "Prussia"
        world.invalidate_active_nations_cache()
        world.war_scores[world._make_diplo_key("France", "Russia")] = 100
        world.threat_by_target["France"] = 80
        world.threat_sources_this_turn = []
        with _quiet():
            _apply_settlement_terms(
                world, settlement_terms=[{
                    "type": "territory_cede", "from": "Russia", "to": "France",
                    "regions": [russia[0]], "value": 1}],
                war_id="war_probe", settlement_route_id="probe")
        assert not world.get_nation_regions("Russia")
        assert world.active_coalition is None
        assert len(_spend_rows(world)) == 1
        # the treaty's own +8 kept whole: (88 - 8) // 2 + 8
        assert int(world.threat_by_target["France"]) == 48
        assert _dissolved_logs(world)[-1]["alarm_spent"] == {"from": 88, "to": 48}

    def test_the_treaty_elimination_sites_pass_the_flag_and_capture_does_not(self):
        import inspect
        from backend.game_logic import formations, settlement_ratify
        assert "_eliminate_nation(nation, by_treaty=True)" in inspect.getsource(
            settlement_ratify._apply_settlement_terms)
        assert "_eliminate_nation(cc_from, by_treaty=True)" in inspect.getsource(
            formations.apply_create_client_clause)
        assert "self._eliminate_nation(nation, by_treaty=True)" in inspect.getsource(
            WorldState._ratify_treaty)
        assert "by_treaty" not in inspect.getsource(WorldState.capture_region)

    def test_breaking_a_truce_never_spends(self):
        """[P1, CONFIRMED] `break_treaty` maps a broken ARMISTICE to PEACE; the
        repudiation dissolved a two-court league and halved the alarm."""
        world = _europe()
        _set(world, "France", "Britain", "PEACE")
        _set(world, "France", "Austria", "ARMISTICE", "armistice")
        assert world.active_coalition is not None
        world.threat_by_target["France"] = 85
        world.threat_sources_this_turn = []
        _set(world, "France", "Austria", "PEACE", "treaty_break")
        assert world.active_coalition is None, "the ejection itself still fires"
        assert _spend_rows(world) == []
        assert int(world.threat_by_target["France"]) == 85
        assert "alarm_spent" not in _dissolved_logs(world)[-1]

    def test_a_clipped_treaty_add_spends_the_same_in_either_order(self):
        """[P3, CONFIRMED] A vassalization that clips at 100 recorded its
        requested +25 while only +10 reached the slot, so the plan order
        decided the result (62 vs 70 at a start of 90)."""
        world = _europe()
        world.threat_by_target["France"] = 90
        world.threat_sources_this_turn = []
        C.add_threat(world, 25, "conquest_vassalization")
        row = world.threat_sources_this_turn[-1]
        assert row["amount"] == 25 and row["applied"] == 10
        add_first = C.league_spent_alarm(world, "France")["to"]
        spend_first = min(100, 90 // C.LEAGUE_SPENT_DIVISOR + 25)
        assert add_first == spend_first == 70

    def test_an_unclipped_add_keeps_its_row_shape(self):
        world = _europe()
        world.threat_by_target["France"] = 40
        world.threat_sources_this_turn = []
        C.add_threat(world, 20, "war_declaration")
        assert world.threat_sources_this_turn[-1] == {
            "source": "war_declaration", "amount": 20, "target": "France"}

    def test_the_arithmetic_guards(self):
        world = _europe()
        world.threat_by_target["France"] = 20
        world.threat_sources_this_turn = [
            {"source": "treaty_annex", "amount": 40, "target": "France"}]
        assert C.league_spent_alarm(world, "France") == {"from": 20, "to": 20}
        world.threat_by_target["France"] = 60
        world.threat_sources_this_turn = [
            {"source": "treaty_annex", "amount": -8, "target": "France"},
            {"source": "forced_alliance", "amount": 10, "target": "France"}]
        assert C.league_spent_alarm(world, "France") == {"from": 60, "to": 35}


class TestTheReviewRoundCopy:

    def test_the_separate_peace_names_the_court_still_at_war(self):
        """[P3] The spend arm stamped `courts_at_war = []` on every road, so
        the chronicle dropped Russia, genuinely still fighting."""
        from backend.campaign_log import format_event_oneliner
        world = _europe()
        _set(world, "France", "Britain", "PEACE")
        _set(world, "France", "Austria", "PEACE")
        log = _dissolved_logs(world)[-1]
        assert "Russia" in log["courts_at_war"]
        for court in log["courts_at_war"]:
            assert world.get_diplomatic_state("France", court) == "WAR"
        note = _pending(world, "Coalition Dissolved")[-1]["message"]
        assert "at war with us all the same" in note and "Russia" in note
        line = format_event_oneliner(log)
        assert "the league is spent" in line and "Russia" in line

    def test_courts_signing_in_the_same_ratification_are_not_named(self):
        world = _europe()
        _set(world, "France", "Britain", "PEACE")
        with C.treaty_in_flight(world, ["Austria", "Russia"]):
            assert C.courts_in_flight(world) == {"Austria", "Russia"}
            _set(world, "France", "Austria", "PEACE")
        assert "Russia" not in _dissolved_logs(world)[-1]["courts_at_war"]
        assert "_treaty_courts_in_flight" not in vars(world)
        assert C.courts_in_flight(world) == set()

    def test_the_ratifiers_open_the_marker(self):
        import inspect
        from backend.game_logic import settlement_ratify, settlement_third_party
        assert "treaty_in_flight(world, plan_courts(plan))" in inspect.getsource(
            settlement_ratify.ratify_settlement_confirm)
        assert "treaty_in_flight(world, settlement_ratify.plan_courts(plan))" in (
            inspect.getsource(settlement_third_party))

    def test_the_clause_arms(self):
        world = _europe()
        assert C.league_spent_clause(world, "France", {"from": 90, "to": 45}) == (
            "The league is spent — Europe's alarm falls from 90 to 45; no new "
            "coalition gathers below 60.")
        assert "Europe's alarm stands at 30;" in C.league_spent_clause(
            world, "France", {"from": 30, "to": 30})
        high = C.league_spent_clause(world, "France", {"from": 100, "to": 70})
        assert "keep it at the 60 at which a coalition gathers" in high
        assert "no new coalition" not in high
        assert "Europe's alarm against Austria falls from 80 to 40" in (
            C.league_spent_clause(world, "Austria", {"from": 80, "to": 40}))

    def test_the_non_france_chronicle_line(self):
        from backend.campaign_log import format_event_oneliner
        assert format_event_oneliner({
            "type": "coalition_dissolved", "target_nation": "Austria",
            "alarm_spent": {"from": 80, "to": 40}}) == (
            "Coalition against Austria has dissolved — the league is spent.")

    def test_the_gates_stay_quiet_at_or_above_sixty(self):
        from backend.game_logic.diplomatic_advisory import _assess_situation
        from backend.game_logic.diplomatic_ledger import _build_balance_of_europe
        world = _europe()
        world.active_coalition = None
        world.coalition_cooldown = 1
        world.threat_by_target["France"] = 65
        with _quiet():
            C.process_coalition_turn(world)
        assert _pending(world, "Coalition Cooldown Ended")[-1]["message"] == (
            "A new coalition may form if threat remains high.")
        board = _talleyrand_board(65)
        board.coalition_cooldown = 3
        assert "headline_note" not in _build_balance_of_europe(board)
        assert "No league gathers" not in (
            _assess_situation(_talleyrand_board(65))["talleyrand_text"])


class TestTheReviewRoundTalleyrand:

    def test_he_counts_the_courts_his_own_declaration_alienates(self):
        """[P2→P3] Courts within 15 of the −10 line cross it on the
        declaration's own relation cost; he counted them before it."""
        world = _talleyrand_board(45)
        for n in list(world.get_active_nations()):
            if n != "France" and world.get_diplomatic_state("France", n) != "WAR":
                world.nation_relations[world._make_diplo_key("France", n)] = -5
        assert C.get_qualifying_nations(world) == []
        projection = C.declaration_would_gather_a_league(world, "France",
                                                          target="Prussia")
        assert projection and projection["courts"]
        assert "Prussia" not in projection["courts"]
        text = _declare_with(world)["diplomatic_objection_popup"]["objection_text"]
        assert "would carry it to 65" in text

    def test_no_projection_while_a_league_brews(self):
        world = _talleyrand_board(45)
        world.coalition_brewing = {"target_nation": "France", "turns_remaining": 2,
                                   "qualifying_nations": ["Sweden"]}
        assert C.declaration_would_gather_a_league(world, "France") is None

    def test_an_eclipse_league_does_not_silence_him(self):
        world = _talleyrand_board(45)
        world.active_coalition = {"name": "x", "target_nation": "Austria",
                                  "members": ["Russia", "Prussia"]}
        assert C.declaration_would_gather_a_league(world, "France") is not None

    def test_he_makes_no_claim_about_the_last_league(self):
        text = _declare_with(_talleyrand_board(45))[
            "diplomatic_objection_popup"]["objection_text"]
        assert "spent at the peace table" not in text
        assert "hand it the next league" in text

    def test_a_confirmed_objection_is_not_staged_again(self):
        """[P4, CONFIRMED] Without the guard, Proceed re-staged the same
        objection forever (the July-25 soft-lock class)."""
        world = _talleyrand_board(45)
        assert _declare_with(world).get("diplomatic_objection_popup")
        world.diplomatic_objection_popup = None
        again = _declare_with(world, confirmed_objection=True)
        assert not again.get("diplomatic_objection_popup")
        assert world.diplomatic_objection_popup is None

    def test_a_casus_belli_halves_the_projection(self):
        world = _talleyrand_board(45)
        world.casus_belli[world._make_diplo_key("France", "Prussia")] = True
        assert not _declare_with(world).get("diplomatic_objection_popup")
        world = _talleyrand_board(50)
        world.casus_belli[world._make_diplo_key("France", "Prussia")] = True
        text = _declare_with(world)["diplomatic_objection_popup"]["objection_text"]
        assert "would carry it to 60" in text

    def test_a_long_roll_of_courts_is_summarised(self):
        import re
        world = _talleyrand_board(45)
        for n in ("Denmark", "Portugal", "Saxony"):
            world.nation_relations[world._make_diplo_key("France", n)] = -80
        text = _declare_with(world)["diplomatic_objection_popup"]["objection_text"]
        assert re.search(r"and \d+ other courts would join it", text), text


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
