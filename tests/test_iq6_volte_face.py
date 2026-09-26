"""IQ-6 "Europe Speaks Its Mind" — the volte-face half (rulings V1–V4).

Row IQ-6's recon (September 14, 2026) split "`volte_face` fired 0 times in
twelve 40-turn runs" in two. The narration half was an instrument defect;
this half is REAL, and these pins hold the correction:

- V1  the window fits the courtship — from the boot war relations the
      game's best courting lever (Improve Relations, skill-scaled) reaches
      the courted floor at best 16 turns after the peace, so a perfect
      player stood at 29 when the 15-turn window closed. 15 -> 20, ceiling
      25 (`THE_WINDOW_FITS_THE_COURTSHIP`).
- V1b a separate peace ends the war (found building T2, beyond the
      contract): the predicate read the PARTICIPANT's exit, so France's
      bilateral peace with Austria — Austria still at war with Bavaria and
      the Kingdom of Italy — never counted as "beaten". The pair's own
      `resolved_turn` answers first (`THE_SEPARATE_PEACE_ENDS_THE_WAR`).
- V2  the courier skips the routine NATION ask cooldown
      (`ai_diplomacy.THE_VOLTE_COURIER_IGNORES_ROUTINE_COOLDOWN`).
- V3  the exhaustion arm is RETIRED under GR9 — the defeat shows on the
      map only (`THE_DEFEAT_IS_THE_SOIL`).
- V4  it speaks its mind: the counsel and the war room name the open door
      (`VOLTE_FACE_SPEAKS_ITS_MIND`).

Every lever set False reproduces the pre-IQ-6 game on its surface; the
identity grid below compares against a VERBATIM copy of the old predicate.
"""

import contextlib
import io
import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import ai_diplomacy as AD
from backend.game_logic import diplomacy as D
from backend.game_logic import diplomatic_advisory as ADV
from backend.game_logic import emergent_designs as ED
from backend.game_logic.diplomatic_dialogue import mission_effect_magnitude
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO = str(REPO_ROOT / "godot-client" / "project-sovereign" / "assets"
               / "maps" / "europe_1805.json")
PLAYER = "France"
FLOOR = ED.VOLTE_FACE_RELATION_FLOOR


def _quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def boot():
    with _quiet():
        return WorldState.from_scenario(SCENARIO)


@pytest.fixture()
def world(boot):
    with _quiet():
        return WorldState.from_dict(boot.to_dict())


def _rel(world, a, b):
    return int(world.nation_relations.get(world._make_diplo_key(a, b), 0) or 0)


def _pressburg(world, cede=("Tyrol",)):
    """France's separate peace with Austria through the REAL bilateral ratify
    (`_ratify_treaty` -> `set_diplomatic_state` -> `cleanup_war_end`, R49
    running, the pair resolved on the boot war instance). One Austrian
    homeland province changes hands BY THE TREATY — never two, which would be
    a punitive partition. Nothing about relations or exhaustion is written."""
    turn = int(world.current_turn)
    demands = [{"type": "territory_cede", "regions": list(cede)}] if cede else []
    with _quiet():
        result = world._ratify_treaty({
            "type": "peace", "proposer_nation": PLAYER,
            "target_nation": "Austria", "sweeteners": [], "demands": demands})
    assert result is not None
    assert world.get_diplomatic_state(PLAYER, "Austria") == "PEACE"
    return turn


def _start_improve(world, target):
    """Drive the REAL `start_mission` dialogue arm (the IQ-4 idiom)."""
    world.talleyrand_defiance_cooldown = 99   # no sabotage die on the send
    world.dialogue_manager.replace({
        "type": "mission", "target_nation": target,
        "talleyrand_text": "Very well, Sire.",
        "options": [
            {"label": "Begin mission", "description": "Start.",
             "action": "start_mission",
             "terms": {"mission_type": "IMPROVE_RELATIONS",
                       "target_nation": target}},
            {"label": "Dismiss", "description": "Cancel.", "action": "dismiss"},
        ],
        "context": {"dp_cost_per_turn": 1},
        "turn_created": int(world.current_turn),
        "blocking": False,
    })
    world.diplomatic_points = max(int(world.diplomatic_points), 5)
    with _quiet():
        result = CommandExecutor()._diplomatic.handle_diplomatic_dialogue_response(
            1, {"world": world})
    assert result.get("success"), result


def _court_mail(world, court):
    manager = world.dialogue_manager
    return [d for d in [manager.peek()] + manager.iter_queue()
            if d and d.get("type") != "mission"
            and ((d.get("context") or {}).get("source_nation") == court
                 or d.get("target_nation") == court)]


def _answer_mail(world, executor, court):
    """The playtest driver's `--diplomacy accept` policy for the court's own
    letters, the conflict confirm included (a live player answers mail — the
    per-nation pending dedupe otherwise holds the court silent)."""
    for _ in range(4):
        bag = _court_mail(world, court)
        if not bag:
            return
        letter = bag[0]
        # IQ-7 (Sept 16, 2026): the handler answers the CURRENT dialogue, so a
        # queued letter must be made current first — exactly what the client's
        # /mailbox/activate does. Before IQ-7 the court's letter was always
        # current here; a client's petition can now sit in front of it, and
        # answering "the letter" would have granted the petition instead and
        # left the letter to trip the per-nation pending dedupe a turn later.
        manager = world.dialogue_manager
        if manager.peek() is not letter and letter.get("mailbox_id") is not None:
            manager.activate_mailbox_item(letter["mailbox_id"])
        with _quiet():
            executor._diplomatic._handle_accept_ai_proposal(letter, world)
        after = _court_mail(world, court)
        if after and after[0] is letter:
            return      # not consumed — do not spin


def _run(world, court="Austria", turns=22, stop_on_fire=True):
    """Turn by turn in `TurnManager.end_turn`'s order: the court's
    diplomatic phase (delivered), then `advance_turn` (the mission tick and
    drift), then the player answers the mail."""
    executor = CommandExecutor()
    rows = []
    for _ in range(turns):
        turn = int(world.current_turn)
        row = {"turn": turn, "relation": _rel(world, PLAYER, court),
               "receptive": ED.volte_face_receptive(world, court, PLAYER),
               "view": ED.volte_face_courtship(world, court, PLAYER),
               "mission": (world.active_diplomatic_mission or {}).get("type")}
        with _quiet():
            proposal = AD.process_diplomatic_phase(court, world)
            if proposal:
                AD.deliver_ai_proposal(proposal, world)
        row["reason"] = (proposal or {}).get("decision_reason")
        rows.append(row)
        with _quiet():
            world.advance_turn()
        _answer_mail(world, executor, court)
        if stop_on_fire and row["reason"] == "volte_face":
            break
    return rows


def _volte_events(world):
    return [e for e in world.event_log if e.get("type") == "volte_face"]


def _volte_dispatches(world):
    return [e for e in world.pending_dispatch_events
            if e.get("type") == "volte_face"]


def _stage_tilsit(world, power="Russia", hegemon="France", relation=45,
                  soil=True, exhaustion=0, ended_ago=2):
    """A beaten court at peace with the hegemon — the unit-level staging
    (the ordinary geometry is T2's, on the real board)."""
    for other in list(world.get_active_nations()):
        key = world._make_diplo_key(power, other)
        if world.diplomatic_states.get(key) in ("WAR", "ARMISTICE"):
            world.diplomatic_states[key] = "PEACE"
    turn = int(world.current_turn)
    world.war_instances["tilsit_war"] = {
        "war_id": "tilsit_war",
        "created_turn": turn - ended_ago - 6,
        "ended_turn": turn - ended_ago,
        "participant_meta": {power: {"side": "attackers"},
                             hegemon: {"side": "defenders"}},
        "side_by_nation": {},
    }
    if soil:
        capital = world.get_nation_capital(power)
        for region_name in world.nation_starting_regions.get(power, []):
            if region_name != capital:
                world.regions[region_name].controller = hegemon
                break
    world.war_exhaustion[power] = int(exhaustion)
    world.nation_relations[world._make_diplo_key(power, hegemon)] = int(relation)
    world.invalidate_bloc_members_cache()
    return world


# ═══════════════════════════ T1 — the arithmetic ══════════════════════════

class TestT1TheWindowFitsTheCourtship:
    def test_the_best_lever_signs_inside_the_window(self, world, monkeypatch):
        """From the first turn of peace, Improve Relations (the tick's own
        skill-scaled effect plus the drift step) carries each beaten great
        power to the courted floor in `ticks`; the courier writes on turn
        peace+ticks and the court signs the next turn — which must still read
        the war as recent. Derived here from production sources, independent
        of the forecast helper, and checked against it."""
        _pressburg(world)
        with _quiet():
            world._ratify_treaty({"type": "peace", "proposer_nation": PLAYER,
                                  "target_nation": "Russia",
                                  "sweeteners": [], "demands": []})
        effect = mission_effect_magnitude(world, "IMPROVE_RELATIONS",
                                          "relation_change")
        assert effect == 8, "Talleyrand's skill scales the +5 base to +8"
        ticks_by_court = {}
        for court in ("Austria", "Russia"):
            relation, ticks = _rel(world, PLAYER, court), 0
            assert relation <= -80, "the boot war relations"
            while relation < FLOOR:
                relation += effect
                relation += D.relation_drift_step(world, PLAYER, court,
                                                  relation=relation, _court=None)
                ticks += 1
            forecast = D.forecast_relation_to(world, court, FLOOR)
            assert forecast is not None and forecast[0] == ticks
            ticks_by_court[court] = ticks
            assert ticks + 1 < ED.volte_face_window() == 20, (court, ticks)
        # Negative control: the pre-IQ-6 window shut the door on a PERFECT
        # courtship (16 is not below 15).
        monkeypatch.setattr(ED, "THE_WINDOW_FITS_THE_COURTSHIP", False)
        assert ED.volte_face_window() == 15
        assert all(t + 1 >= ED.volte_face_window()
                   for t in ticks_by_court.values()), ticks_by_court

    def test_the_forecast_steps_the_drift_like_the_tick(self, world):
        """The counsel's figure is the tick's own arithmetic, DRIFT included.
        From the boot relation the drift step happens not to change the count
        (−80 + 8 a tick and −80 + 9-then-8-then-7 both reach 40 in 15 — the
        mutation sweep found the forecast's drift step unpinned for exactly
        that reason), so this pin starts at −40, where it does: 11 ticks with
        the drift, 10 without. The real mission ticks must agree with the
        forecast, turn for turn."""
        peace_turn = _pressburg(world)
        world.nation_relations[world._make_diplo_key(PLAYER, "Austria")] = -40
        effect = mission_effect_magnitude(world, "IMPROVE_RELATIONS",
                                          "relation_change")
        without_drift = -(-(FLOOR + 40) // effect)
        forecast = D.forecast_relation_to(world, "Austria", FLOOR)[0]
        assert (forecast, without_drift) == (11, 10)
        _start_improve(world, "Austria")
        rows = _run(world)
        first_receptive = next(r for r in rows if r["receptive"])
        assert first_receptive["turn"] == peace_turn + forecast

    def test_the_ceiling_keeps_a_routine_ladder_alliance_ordinary(self, world):
        """Austria's own ladder alliance landed 25 turns after the war on the
        measured arm: a window of 26+ would announce it as a reversal."""
        assert (ED.VOLTE_FACE_WINDOW_BEFORE_IQ6 < ED.VOLTE_FACE_WINDOW
                <= ED.VOLTE_FACE_WINDOW_CEILING == 25)
        _stage_tilsit(world, ended_ago=25)
        assert ED.volte_face_receptive(world, "Russia", PLAYER) is False
        assert ED.maybe_fire_volte_face(world, "Russia", PLAYER) is None
        assert not _volte_events(world)


# ══════════════════ T2 — the ordinary geometry, real board ═════════════════

class TestT2TheOrdinaryGeometry:
    def test_courted_austria_takes_our_hand_once(self, world):
        """A beaten Austria (Tyrol held by France BY THE TREATY, no exhaustion
        anywhere near the old mark), courted through the executor from the
        peace turn: receptive the turn the relation first reaches 40, the
        courier proposes that same turn, the alliance signs through the
        conflict confirm inside the window — exactly one beat, one dispatch."""
        peace_turn = _pressburg(world)
        assert world.regions["Tyrol"].controller == PLAYER
        assert int(world.war_exhaustion.get("Austria", 0) or 0) < ED.VOLTE_FACE_WE_MARK
        assert ED.volte_face_failing_clauses(
            world, "Austria", PLAYER, exhaustive=True) == [ED.VOLTE_CLAUSE_NOT_COURTED]
        forecast_ticks = D.forecast_relation_to(world, "Austria", FLOOR)[0]

        _start_improve(world, "Austria")
        rows = _run(world)

        fired = [r for r in rows if r["reason"] == "volte_face"]
        assert len(fired) == 1, rows
        first_receptive = next(r for r in rows if r["receptive"])
        index = rows.index(first_receptive)
        assert first_receptive["relation"] >= FLOOR > rows[index - 1]["relation"]
        # The counsel's forecast is the tick's own arithmetic: exact here.
        assert first_receptive["turn"] == peace_turn + forecast_ticks
        # V2: the rarest beat is not held by the routine ask cooldown.
        assert fired[0]["turn"] == first_receptive["turn"]
        signing_turn = fired[0]["turn"] + 1
        assert signing_turn - peace_turn < ED.volte_face_window()
        # Every turn before the door opened, the view said so honestly.
        for row in rows[:index]:
            assert row["mission"] == "IMPROVE_RELATIONS"
            view = row["view"]
            assert view is not None, row
            assert view["turns_left"] == (
                peace_turn + ED.volte_face_window() - 2 - row["turn"])
            assert view["last_signing_turn"] >= signing_turn

        assert world.get_diplomatic_state(PLAYER, "Austria") == "ALLIANCE"
        events = _volte_events(world)
        assert len(events) == 1 and events[0]["nation"] == "Austria"
        assert events[0]["partner"] == PLAYER
        assert len(_volte_dispatches(world)) == 1

    def test_uncourted_the_door_never_opens(self, world):
        _pressburg(world)
        rows = _run(world, turns=ED.volte_face_window() + 1)
        assert not any(r["receptive"] for r in rows)
        assert not any(r["reason"] == "volte_face" for r in rows)
        assert not _volte_events(world)

    def test_lever_down_the_old_window_shuts_a_perfect_courtship(
            self, world, monkeypatch):
        """Negative control: at 15 the same courtship is never receptive —
        the relation stands at 35 when the window closes — and the ladder
        alliance the court then asks for is ordinary, not a reversal."""
        monkeypatch.setattr(ED, "THE_WINDOW_FITS_THE_COURTSHIP", False)
        _pressburg(world)
        _start_improve(world, "Austria")
        rows = _run(world, turns=22, stop_on_fire=False)
        assert not any(r["receptive"] for r in rows)
        assert not any(r["reason"] == "volte_face" for r in rows)
        assert not _volte_events(world)


# ═══════════════════ V1b — a separate peace ends the war ═══════════════════

class TestV1bASeparatePeaceEndsTheWar:
    def test_the_pair_resolution_answers(self, world, monkeypatch):
        peace_turn = _pressburg(world)
        instance = world.war_instances["war_1"]
        assert "Austria|Bavaria" in instance["active_diplo_keys"], (
            "Austria still fights France's allies — the geometry that hid it")
        assert instance["participant_meta"]["Austria"].get("exited_turn") is None
        window = ED.volte_face_window()
        assert ED._war_with_ended_recently(world, "Austria", PLAYER, window)
        assert ED._latest_war_end_turn(world, "Austria", PLAYER) == peace_turn
        monkeypatch.setattr(ED, "THE_SEPARATE_PEACE_ENDS_THE_WAR", False)
        assert not ED._war_with_ended_recently(world, "Austria", PLAYER, window)
        assert ED.volte_face_failing_clauses(world, "Austria", PLAYER)[0] == (
            ED.VOLTE_CLAUSE_NOT_BEATEN)

    def test_an_unresolved_pair_is_still_a_war(self, world):
        """Only a RESOLVED pair ends it — the boot war's live pairs never do."""
        for court in ("Austria", "Russia", "Britain"):
            assert not ED._war_with_ended_recently(
                world, court, PLAYER, ED.volte_face_window())


# ═══════════════════ T3 — V2, the courier's cooldown ═══════════════════════

class TestT3TheCourierSkipsTheRoutineCooldown:
    def test_a_routine_acceptance_cooldown_no_longer_holds_it(
            self, world, monkeypatch):
        _stage_tilsit(world)
        world.ai_proposal_cooldowns["Russia|nation"] = 2
        proposal = AD.process_diplomatic_phase("Russia", world)
        assert proposal is not None and proposal["decision_reason"] == "volte_face"

    def test_lever_down_the_routine_cooldown_holds_it(self, world, monkeypatch):
        monkeypatch.setattr(AD, "THE_VOLTE_COURIER_IGNORES_ROUTINE_COOLDOWN", False)
        _stage_tilsit(world)
        world.ai_proposal_cooldowns["Russia|nation"] = 2
        proposal = AD.process_diplomatic_phase("Russia", world)
        assert proposal is None or proposal.get("decision_reason") != "volte_face"

    def test_the_alliance_type_cooldown_still_holds_it(self, world):
        _stage_tilsit(world)
        world.ai_proposal_cooldowns["Russia|alliance"] = 3
        proposal = AD.process_diplomatic_phase("Russia", world)
        assert proposal is None or proposal.get("decision_reason") != "volte_face"

    def test_the_default_check_is_unchanged(self, world):
        """`skip_nation_cooldown` defaults off: every other caller reads the
        nation key exactly as before."""
        world.ai_proposal_cooldowns["Russia|nation"] = 2
        assert AD._is_on_cooldown("Russia", "alliance", world) is True
        assert AD._is_on_cooldown("Russia", "alliance", world,
                                  skip_nation_cooldown=True) is False


# ═══════════════════ T4 — V3, the defeat is the soil ═══════════════════════

class TestT4TheDefeatIsTheSoil:
    def test_exhaustion_alone_no_longer_shows_the_defeat(self, world, monkeypatch):
        _stage_tilsit(world, soil=False, exhaustion=80)
        assert ED.volte_face_receptive(world, "Russia", PLAYER) is False
        assert ED.volte_face_failing_clauses(world, "Russia", PLAYER) == [
            ED.VOLTE_CLAUSE_NO_MARK]
        monkeypatch.setattr(ED, "THE_DEFEAT_IS_THE_SOIL", False)
        assert ED.volte_face_receptive(world, "Russia", PLAYER) is True

    def test_the_soil_alone_shows_it(self, world):
        _stage_tilsit(world, soil=True, exhaustion=0)
        assert ED.volte_face_receptive(world, "Russia", PLAYER) is True


# ═══════════════════ T5 — V4, it speaks its mind ═══════════════════════════

def _walk_numbers(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk_numbers(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_numbers(item)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        yield value


class TestT5ItSpeaksItsMind:
    def _counsel(self, world, court="Austria"):
        actions = D.get_available_diplomatic_actions(world, court)
        with _quiet():
            full = D._recommendation_and_mission(world, court, actions, 10,
                                                 False, world.vassals)
            base = D._base_recommendation_and_mission(world, court, actions, 10,
                                                      False, world.vassals)
        return full, base

    def test_the_counsel_names_the_open_door(self, world, monkeypatch):
        peace_turn = _pressburg(world)
        view = ED.volte_face_courtship(world, "Austria", PLAYER)
        assert view["turns_left"] == ED.volte_face_window() - 2 == 18
        assert view["last_signing_turn"] == peace_turn + ED.volte_face_window() - 1
        ticks = D.forecast_relation_to(world, "Austria", FLOOR)[0]
        line = ED.volte_face_counsel_line(world, "Austria", PLAYER)
        assert line == (
            f"Austria was beaten, not broken — court her to {FLOOR} within "
            f"18 turns and she may take our hand. Relations stand at "
            f"{_rel(world, PLAYER, 'Austria'):+d}; Improve Relations would "
            f"carry them there in ≈{ticks} turns.")
        (text, mission), (base_text, base_mission) = self._counsel(world)
        assert text == f"{base_text} {line}"
        assert mission == base_mission, "display only — the mission is untouched"
        monkeypatch.setattr(ED, "VOLTE_FACE_SPEAKS_ITS_MIND", False)
        (text_down, mission_down), _ = self._counsel(world)
        assert (text_down, mission_down) == (base_text, base_mission)

    def test_the_war_room_says_it_too(self, world, monkeypatch):
        _pressburg(world)
        line = ED.volte_face_counsel_line(world, "Austria", PLAYER)
        with _quiet():
            room = ADV._assess_situation(world)
        assert f"  {line}" in room["talleyrand_text"].split("\n")
        openings = room["context"]["volte_openings"]
        assert [o["nation"] for o in openings] == ["Austria"]
        assert openings[0]["text"] == line
        assert all(isinstance(n, int) for n in _walk_numbers(openings))
        monkeypatch.setattr(ED, "VOLTE_FACE_SPEAKS_ITS_MIND", False)
        with _quiet():
            room_down = ADV._assess_situation(world)
        assert "volte_openings" not in room_down["context"]
        assert "beaten, not broken" not in room_down["talleyrand_text"]

    def test_it_speaks_only_when_courting_is_all_that_is_missing(self, world):
        _pressburg(world)
        # Courted already: receptive — nothing left to counsel.
        key = world._make_diplo_key(PLAYER, "Austria")
        world.nation_relations[key] = FLOOR
        assert ED.volte_face_receptive(world, "Austria", PLAYER) is True
        assert ED.volte_face_counsel_line(world, "Austria", PLAYER) == ""
        world.nation_relations[key] = -80
        assert ED.volte_face_counsel_line(world, "Austria", PLAYER) != ""
        # Humiliated (a punitive record): the door is shut for good.
        ED.record_punitive_cessions(world, {
            "Austria": [("Bohemia", PLAYER), ("Moravia", PLAYER)]})
        assert ED.volte_face_counsel_line(world, "Austria", PLAYER) == ""
        # Still at war (Russia, Britain on the boot board): silent.
        for court in ("Russia", "Britain"):
            assert ED.volte_face_counsel_line(world, court, PLAYER) == ""

    def test_an_unbeaten_court_after_a_white_peace_is_silent(self, world):
        """Russia made peace with no soil lost: not beaten on the map, so
        there is no door to name (V3)."""
        with _quiet():
            world._ratify_treaty({"type": "peace", "proposer_nation": PLAYER,
                                  "target_nation": "Russia",
                                  "sweeteners": [], "demands": []})
        assert ED.volte_face_failing_clauses(world, "Russia", PLAYER)[0] == (
            ED.VOLTE_CLAUSE_NO_MARK)
        assert ED.volte_face_counsel_line(world, "Russia", PLAYER) == ""

    def test_an_honest_no_when_the_road_is_too_long(self, world, monkeypatch):
        """At the old window the same courtship cannot land — and the line
        says so instead of promising it."""
        monkeypatch.setattr(ED, "THE_WINDOW_FITS_THE_COURTSHIP", False)
        _pressburg(world)
        line = ED.volte_face_counsel_line(world, "Austria", PLAYER)
        assert "would not carry them" in line and "13 turns" in line


# ═════════════ The levers down reproduce the pre-IQ-6 predicate ═════════════

def _pre_iq6_war_with_ended_recently(world, power, other, window):
    """VERBATIM copy of the pre-IQ-6 `_war_with_ended_recently` body."""
    turn = int(getattr(world, "current_turn", 0))

    def _scan(instances):
        for instance in instances:
            if not isinstance(instance, dict):
                continue
            meta = instance.get("participant_meta") or {}
            side_by = instance.get("side_by_nation") or {}

            def _side_of(n):
                record = meta.get(n)
                if isinstance(record, dict) and record.get("side"):
                    return record.get("side")
                return side_by.get(n)

            power_side = _side_of(power)
            other_side = _side_of(other)
            if not power_side or not other_side or power_side == other_side:
                continue
            end = (meta.get(power) or {}).get("exited_turn")
            if end is None:
                end = instance.get("ended_turn")
            if end is None:
                continue
            if turn - int(end) < window:
                return True
        return False

    if _scan((getattr(world, "war_instances", {}) or {}).values()):
        return True
    return _scan(getattr(world, "archived_war_instances", []) or [])


def _pre_iq6_receptive(world, power, hegemon):
    """VERBATIM copy of the pre-IQ-6 `volte_face_receptive` (window 15)."""
    if power == hegemon:
        return False
    player = getattr(world, "player_nation", "France")
    if power == player:
        return False
    if world.get_power_tier(power) != "major":
        return False
    if power in (getattr(world, "vassals", {}) or {}):
        return False
    if power not in world.get_active_nations():
        return False
    if world.get_diplomatic_state(power, hegemon) in ("WAR", "ARMISTICE"):
        return False
    from backend.game_logic.settlement_reactions import get_settlement_memories
    if get_settlement_memories(world, actor=hegemon, subject=power,
                               memory_type=ED.PUNITIVE_MEMORY_TYPE):
        return False
    for entry in (getattr(world, "agendas", {}) or {}).get(power) or []:
        if (isinstance(entry, dict) and entry.get("emergent")
                and entry.get("author") == hegemon):
            return False
    if not _pre_iq6_war_with_ended_recently(world, power, hegemon, 15):
        return False
    exhausted = int((getattr(world, "war_exhaustion", {}) or {})
                    .get(power, 0) or 0) >= 40
    hegemon_bloc = set(world.get_bloc_members(hegemon))
    soil_marked = any(
        (lambda c: c and (world._top_overlord(c) or c) in hegemon_bloc)(
            getattr(world.regions.get(r), "controller", None))
        for r in ED._lost_homeland(world, power))
    if not exhausted and not soil_marked:
        return False
    relation = int(world.nation_relations.get(
        world._make_diplo_key(power, hegemon), 0) or 0)
    return relation >= 40


class TestTheLeversDownReproduceThePredicate:
    def test_identity_grid(self, boot, monkeypatch):
        """With V1, V1b and V3 down, the refactored single source answers
        exactly as the pre-IQ-6 predicate on every staged state — including
        a resolved pair the old read ignored."""
        monkeypatch.setattr(ED, "THE_WINDOW_FITS_THE_COURTSHIP", False)
        monkeypatch.setattr(ED, "THE_DEFEAT_IS_THE_SOIL", False)
        monkeypatch.setattr(ED, "THE_SEPARATE_PEACE_ENDS_THE_WAR", False)
        compared = 0
        answers = set()
        for punitive in (False, True):
            with _quiet():
                world = WorldState.from_dict(boot.to_dict())
            _stage_tilsit(world)
            if punitive:
                ED.record_punitive_cessions(world, {
                    "Russia": [("Lithuania", PLAYER), ("Livonia", PLAYER)]})
            capital = world.get_nation_capital("Russia")
            soil_region = next(r for r in world.nation_starting_regions["Russia"]
                               if r != capital)
            instance = world.war_instances["tilsit_war"]
            turn = int(world.current_turn)
            for relation, exhaustion, soil, ago, at_war, pair_meta in itertools.product(
                    (39, 40, 45), (0, 39, 40, 80), (True, False),
                    (0, 14, 15, 16, 20, 21), (False, True), (False, True)):
                world.nation_relations[world._make_diplo_key("Russia", PLAYER)] = relation
                world.war_exhaustion["Russia"] = exhaustion
                world.regions[soil_region].controller = PLAYER if soil else "Russia"
                instance["ended_turn"] = turn - ago
                instance["diplo_key_meta"] = ({"France|Russia": {
                    "pair_status": "resolved", "resolved_turn": turn}}
                    if pair_meta else {})
                world.diplomatic_states[world._make_diplo_key("Russia", PLAYER)] = (
                    "WAR" if at_war else "PEACE")
                world.invalidate_bloc_members_cache()
                for power, hegemon in (("Russia", PLAYER), (PLAYER, "Russia"),
                                       ("Bavaria", PLAYER)):
                    old = _pre_iq6_receptive(world, power, hegemon)
                    assert ED.volte_face_receptive(world, power, hegemon) == old, (
                        punitive, relation, exhaustion, soil, ago, at_war,
                        pair_meta, power)
                    answers.add(old)
                    compared += 1
        assert compared == 2 * 3 * 4 * 2 * 6 * 2 * 2 * 3
        assert answers == {True, False}, "the grid must reach both answers"


# ═════════ T7 — the committed courting script, end to end (slow) ═════════
# The assurance idiom: the real playtest driver as a subprocess, 40 turns of
# the COMMANDED arm with `--diplomacy accept` on the historical seed — once
# with `tools/playtest_scripts/volte_court_austria.json` (the same orders,
# plus Talleyrand courting Austria from loop 5), once without. Measured when
# landed: Britain's war_1 settlement is ratified on world turn 4, Austria's
# homeland stays in France's bloc, the courted court signs on turn 21 and
# the digest carries the beat once; the plain arm carries it zero times.
# ~45 s per arm.

DRIVER = REPO_ROOT / "tools" / "playtest_driver.py"
SCRIPTS = REPO_ROOT / "tools" / "playtest_scripts"

# SR-1d "The League Treats When Spent" (September 26, 2026): PR-D1b gates
# the league's turn-4 settlement offer, so the boot war now ends around
# turn 9-11 and the courtship geometry T7 measures (a peace at t4, the door
# at t20, the beat at t21) no longer holds on the shipped board -- measured
# by the pre-commit hook: the 40-turn courted arm carried the beat ZERO
# times. The ruling's own option, the same one `test_iq6_europe_speaks_its_
# mind.py` takes for every IQ-6 drive: these arms run with THAT lever down
# through the driver's `--lever` flag (recorded in meta.json), because they
# measure the volte-face machinery, not the league's cadence. The board as
# shipped is measured by SR-1d's own record (the `prd1b-cmd-*` archives).
_PRE_SR1D_LEAGUE_CLI = [
    "--lever", "backend.game_logic.ai_diplomacy:THE_LEAGUE_TREATS_WHEN_SPENT=0",
]


def _drive(root: Path, name: str, script: Path):
    env = dict(os.environ)
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START",
                "PYTHONIOENCODING"):   # conftest's sentinel; the cp1252 trap
        env.pop(key, None)
    env.update({"LLM_MODE": "mock", "SOVEREIGN_SEED": "historical",
                "DEBUG_MODE": "false", "PYTHONHASHSEED": "0",
                "INK_IRON_SAVE_DIR": str(root / name / "saves"),
                "PYTHONPATH": str(REPO_ROOT)})
    proc = subprocess.run(
        [sys.executable, str(DRIVER), "--name", name, "--out", str(root),
         "--fresh", "--script", str(script), "--turns", "40",
         "--seed", "historical", "--diplomacy", "accept",
         *_PRE_SR1D_LEAGUE_CLI],
        env=env, cwd=str(REPO_ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=900)
    assert proc.returncode == 0, (proc.stdout[-2000:], proc.stderr[-2000:])
    run = root / name
    records = [json.loads(line) for line in
               (run / "digest.jsonl").read_text(encoding="utf-8").splitlines()
               if line.strip()]
    meta = json.loads((run / "meta.json").read_text(encoding="utf-8"))
    return records, meta


@pytest.fixture(scope="module")
def t7_runs(tmp_path_factory):
    root = tmp_path_factory.mktemp("iq6_t7")
    return {"court": _drive(root, "court", SCRIPTS / "volte_court_austria.json"),
            "plain": _drive(root, "plain", SCRIPTS / "commanded_full40.json")}


def _volte_records(records, kind):
    return [r for r in records
            if r.get("kind") == kind and r.get("dtype") == "volte_face"]


class TestT7TheCommittedScript:
    def test_the_courted_arm_carries_the_beat_exactly_once(self, t7_runs):
        records, meta = t7_runs["court"]
        logged = _volte_records(records, "campaign_log")
        assert len(logged) == 1, logged
        assert "Austria" in logged[0]["text"]
        assert len(_volte_records(records, "rail")) == 1
        counts = meta.get("dispatch_type_counts")
        if counts is not None:     # the IQ-6 N1 tally, when the digest has it
            assert counts.get("volte_face") == 1, counts

    def test_the_plain_commanded_arm_carries_none(self, t7_runs):
        records, meta = t7_runs["plain"]
        assert not [r for r in records if r.get("dtype") == "volte_face"]
        assert not (meta.get("dispatch_type_counts") or {}).get("volte_face")
