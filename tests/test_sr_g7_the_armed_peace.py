"""SR-G7 / PB-D1 "The Armed Peace" (Score Finish Step 3, October 2, 2026;
gate record SCORE_FINISH_SPEC.md §6.2, RULED September 28, 2026).

The long peace ends by machinery: while the hegemon leads ≥ 1/3 of
Europe's power with no league active or brewing, a court left to alarm and
no Congress sitting, the alarm's decay stops at the WATCH (45) — and after
20 quiet turns (no battle by the hegemon; the ruling's 16 lengthened to the band's 20 on measurement — F1) the alarm RISES +3 a turn to the
brewing gate, where the existing league machinery takes over. ONE reading
(`coalition.armed_peace_reading`) feeds the tick, the RS-16 forecast, the
Balance-of-Europe rows, the war room and the dispatch beat. Written on the
hegemon (GR5). Lever `coalition.THE_ARMED_PEACE`; False = the alarm decays
to 0 at a long peace, byte for byte.
"""
from __future__ import annotations

import contextlib
import copy
import json
import io
from pathlib import Path

import pytest

from backend.game_logic import coalition as CO
from backend.game_logic import congress as CG
from backend.game_logic import diplomatic_advisory as DA
from backend.game_logic import diplomatic_ledger as DL
from backend.models.world_state import WorldState

SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
            / "assets" / "maps" / "europe_1805.json")


def _quiet_france(turn: int = 20, threat: int = 30, quiet_turns=None):
    """A France at peace with every court after the opening war: no league
    stands or brews, the great powers' relations sit below -10 (they
    QUALIFY), and nobody has fought for `quiet_turns` turns (default: never
    since the boot, so quiet == turn)."""
    world = WorldState.from_scenario(str(SCENARIO))
    france = world.player_nation
    world.current_turn = turn
    world.active_coalition = None
    world.coalition_brewing = None
    world.coalition_cooldown = 0
    for nation in world.get_active_nations():
        if nation == france:
            continue
        key = world._make_diplo_key(france, nation)
        if world.diplomatic_states.get(key) == "WAR":
            world.diplomatic_states[key] = "PEACE"
        if nation in ("Austria", "Britain", "Russia"):
            world.nation_relations[key] = -50
    world.invalidate_active_nations_cache()
    world.threat_by_target[france] = int(threat)
    world.threat_sources_this_turn = []
    world.pending_dispatch_events = []
    for m in world.marshals.values():
        m.last_battle_turn = -1 if quiet_turns is None else int(turn - quiet_turns)
    return world


def _tick(world):
    with contextlib.redirect_stdout(io.StringIO()):
        CO.process_coalition_turn(world)
    return int(world.threat_level)


class TestThePredicate:
    def test_a_quiet_dominant_france_holds(self):
        world = _quiet_france()
        r = CO.armed_peace_reading(world)
        assert r["holds"] and r["hegemon"] == "France" and r["share"] >= 0.33
        assert r["watch"] == 45 and r["gate"] == 60

    def test_a_standing_league_ends_it(self):
        world = WorldState.from_scenario(str(SCENARIO))
        assert world.active_coalition is not None    # the Third Coalition
        r = CO.armed_peace_reading(world)
        assert not r["holds"] and r["reason"] == "league"

    def test_a_brewing_league_ends_it(self):
        world = _quiet_france()
        world.coalition_brewing = {"target_nation": "France", "turns_remaining": 2,
                                   "qualifying_nations": ["Austria"]}
        assert CO.armed_peace_reading(world)["reason"] == "league"

    def test_a_bloc_under_a_third_ends_the_watch(self, monkeypatch):
        world = _quiet_france()
        monkeypatch.setattr(CO, "_identify_max_bloc_share", lambda w: ("France", 0.30))
        r = CO.armed_peace_reading(world)
        assert not r["holds"] and r["reason"] == "no_hegemon"

    def test_nobody_left_to_alarm_ends_it(self, monkeypatch):
        world = _quiet_france()
        monkeypatch.setattr(CO, "no_court_left_to_alarm", lambda w, t=None: True)
        assert CO.armed_peace_reading(world)["reason"] == "nobody_left"

    def test_the_congress_suspends_it(self, monkeypatch):
        world = _quiet_france()
        monkeypatch.setattr(CG, "sitting", lambda w: True)
        assert CO.armed_peace_reading(world)["reason"] == "congress"

    def test_lever_down_reads_nothing(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_ARMED_PEACE", False)
        r = CO.armed_peace_reading(_quiet_france())
        assert not r["holds"] and r["reason"] == "lever"

    def test_quiet_turns_count_from_the_last_battle_either_side(self):
        world = _quiet_france(turn=20)
        assert CO.hegemon_quiet_turns(world, "France") == 20
        world.marshals["Ney"].last_battle_turn = 17        # Ney was ATTACKED on 17
        assert CO.hegemon_quiet_turns(world, "France") == 3
        world.marshals["Ney"].strength = 0                  # a destroyed corps does not count
        assert CO.hegemon_quiet_turns(world, "France") == 20


class TestTheWatch:
    @pytest.mark.parametrize("level,expected", [(50, 48), (46, 45), (45, 45), (30, 31), (0, 1)])
    def test_the_decay_stops_at_the_watch(self, level, expected):
        """The tick adds hegemony's +1 before the decay (the ledger's own
        order): 50 → 51 → 48; 46 → 47 → 45 (clamped); 45 → 46 → 45; below
        the watch no decay runs, so 30 → 31 and 0 → 1."""
        world = _quiet_france(turn=5, threat=level)        # quiet 5: no rise yet
        assert CO._calculate_threat_decay(world) >= 3
        assert _tick(world) == expected

    def test_the_pure_clamp(self):
        r = CO.armed_peace_reading(_quiet_france(turn=5, threat=45))
        assert CO.armed_peace_decay(r, "France", 50, 3) == 3
        assert CO.armed_peace_decay(r, "France", 46, 3) == 1
        assert CO.armed_peace_decay(r, "France", 45, 3) == 0
        assert CO.armed_peace_decay(r, "France", 20, 3) == 0
        assert CO.armed_peace_rise(r, "France", 45) == 0

    def test_below_the_watch_hegemony_lifts_a_spent_alarm(self):
        """Decay does not run under the watch, so the +1 hegemony tick
        climbs: a spent alarm comes back up to 45 and holds there."""
        world = _quiet_france(turn=5, threat=20)
        levels = []
        for _ in range(30):
            levels.append(_tick(world))
            world.current_turn += 1
            world.threat_sources_this_turn = []
            for m in world.marshals.values():      # keep the quiet SHORT: the fuse is the next class's
                m.last_battle_turn = world.current_turn - 5
        assert levels[0] > 20 and max(levels) <= 45
        assert levels[-1] == 45

    def test_the_watch_row_is_written_when_decay_is_held(self):
        world = _quiet_france(turn=5, threat=46)
        _tick(world)
        rows = [s for s in world.threat_sources_this_turn if s.get("source") == "armed_peace_watch"]
        assert len(rows) == 1
        assert rows[0]["amount"] == 0 and rows[0]["held"] >= 1
        assert rows[0]["label"].startswith("Europe watches — the French bloc leads ")
        assert "(the alarm holds at 45)" in rows[0]["label"]

    def test_lever_down_the_alarm_decays_to_nothing(self, monkeypatch):
        monkeypatch.setattr(CO, "THE_ARMED_PEACE", False)
        world = _quiet_france(turn=5, threat=46)
        after = _tick(world)
        assert after < 45
        assert not any(s.get("source") == "armed_peace_watch" for s in world.threat_sources_this_turn)


class TestTheFuse:
    def test_fifteen_quiet_turns_is_not_yet_the_fuse(self):
        world = _quiet_france(turn=20, threat=45, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS - 1)
        r = CO.armed_peace_reading(world)
        assert r["fuse_turns_left"] == 1 and r["rise"] == 0
        assert _tick(world) == 45
        assert not any(s.get("source") == "armed_peace" for s in world.threat_sources_this_turn)

    def test_sixteen_quiet_turns_lights_it(self):
        world = _quiet_france(turn=20, threat=45, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        r = CO.armed_peace_reading(world)
        assert r["fuse_turns_left"] == 0 and r["rise"] == 3
        assert _tick(world) == 49         # +1 hegemony, +3 the courts re-arm, no decay
        rows = [s for s in world.threat_sources_this_turn if s.get("source") == "armed_peace"]
        assert rows and rows[0]["amount"] == 3

    def test_the_rise_stops_at_the_brewing_gate(self):
        world = _quiet_france(turn=20, threat=58, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        assert _tick(world) == 60
        world = _quiet_france(turn=20, threat=60, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        assert _tick(world) == 60

    def test_after_the_fuse_the_alarm_only_climbs(self):
        """Measured on the first cut: a +3 added above a FIXED floor was
        undone by the next tick's decay back to 45 (CMD-A oscillated
        48 / 50 / 47) and the gate was never reached. After the fuse no
        decay runs on the hegemon's slot: the alarm climbs to 60 and holds."""
        world = _quiet_france(turn=20, threat=45, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        levels = []
        for _ in range(6):
            levels.append(_tick(world))
            world.current_turn += 1
            world.threat_sources_this_turn = []
            world.coalition_brewing = None       # the climb alone, not the countdown
        assert levels == sorted(levels) and levels[-1] == 60 and levels[0] > 45
        assert levels[-2] == 60, levels     # the gate is the floor it HOLDS at
        r = CO.armed_peace_reading(world)
        assert CO.armed_peace_decay(r, "France", 55, 3) == 0      # below the gate: no decay
        assert CO.armed_peace_decay(r, "France", 65, 3) == 3      # above it: back down to the gate
        assert CO.armed_peace_decay(r, "France", 61, 3) == 1

    def test_at_the_gate_the_league_brews_by_the_old_machinery(self):
        world = _quiet_france(turn=20, threat=58, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        _tick(world)
        assert world.threat_level == 60
        assert world.coalition_brewing is not None
        assert set(world.coalition_brewing.get("qualifying_nations", [])) >= {"Austria", "Britain", "Russia"}

    def test_a_battle_restarts_the_count(self):
        world = _quiet_france(turn=20, threat=45, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        world.marshals["Davout"].last_battle_turn = 19
        r = CO.armed_peace_reading(world)
        assert r["quiet_turns"] == 1 and r["rise"] == 0 and r["fuse_turns_left"] == CO.ARMED_PEACE_FUSE_TURNS - 1

    def test_the_beat_fires_on_the_lapse_tick_only(self):
        world = _quiet_france(turn=20, threat=45, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        _tick(world)
        beats = [e for e in world.pending_dispatch_events
                 if e.get("type") == "diplomatic_armed_peace_fuse"]
        assert len(beats) == 1
        vars_ = beats[0].get("template_vars") or beats[0].get("vars") or {}
        assert int(vars_.get("quiet", 0)) == CO.ARMED_PEACE_FUSE_TURNS and int(vars_.get("rise", 0)) == 3
        world.pending_dispatch_events = []
        world.current_turn += 1
        world.threat_sources_this_turn = []
        _tick(world)
        assert not any(e.get("type") == "diplomatic_armed_peace_fuse"
                       for e in world.pending_dispatch_events)


class TestTheForecastIsTheTick:
    @pytest.mark.parametrize("threat,quiet", [(50, 5), (45, 5), (20, 5), (45, 20), (58, 20), (60, 20)])
    def test_rs16s_forecast_equals_the_tick(self, threat, quiet):
        world = _quiet_france(turn=20, threat=threat, quiet_turns=quiet)
        forecast = CO.forecast_alarm_tick(world)
        probe = copy.deepcopy(world)
        after = _tick(probe)
        assert forecast["next"] == after, (forecast, after)
        if quiet >= CO.ARMED_PEACE_FUSE_TURNS and threat < 60:
            assert any("re-arm" in label for label, _ in forecast["gains"])


class TestTheSurfaces:
    def test_the_ledger_row_shows_the_watch_without_a_figure(self):
        world = _quiet_france(turn=5, threat=46)
        _tick(world)
        boe = DL.build_diplomatic_ledger(world)["balance_of_europe"]
        row = next(s for s in boe["threat_sources_this_turn"] if s["source"] == "armed_peace_watch")
        assert row["display"] == row["label"] and "(+0)" not in row["display"]
        assert "Europe watches" in row["display"]
        ap = boe["armed_peace"]
        assert ap["holds"] is True and ap["watch"] == 45 and ap["share_pct"] >= 33
        assert isinstance(ap["fuse_turns_left"], int)

    def test_the_rise_row_is_named(self):
        world = _quiet_france(turn=20, threat=45, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        _tick(world)
        boe = DL.build_diplomatic_ledger(world)["balance_of_europe"]
        row = next(s for s in boe["threat_sources_this_turn"] if s["source"] == "armed_peace")
        assert row["display"] == "The courts re-arm (+3)"

    def test_the_war_room_names_the_fuse_and_the_levers(self):
        world = _quiet_france(turn=10, threat=45)
        lines = DA.armed_peace_war_room_lines(world)
        text = "\n".join(lines)
        assert "THE ARMED PEACE" in text and "holds at 45" in text
        assert f"in {CO.ARMED_PEACE_FUSE_TURNS - 10} turns the courts re-arm" in text
        assert "Austria" in text and "Britain" in text and "Russia" in text
        assert "a court raised above -10 will not join" in text
        assert "the Congress suspends it" in text
        world = _quiet_france(turn=20, threat=45, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        assert "the courts re-arm: the alarm rises 3 a turn" in "\n".join(
            DA.armed_peace_war_room_lines(world))

    def test_the_war_room_is_silent_when_it_does_not_hold(self):
        world = WorldState.from_scenario(str(SCENARIO))     # a league stands
        assert DA.armed_peace_war_room_lines(world) == []

    def test_the_advisory_carries_the_lines(self):
        world = _quiet_france(turn=10, threat=45)
        with contextlib.redirect_stdout(io.StringIO()):
            payload = DA.generate_advisory(None, "assess_situation", world)
        text = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
        assert "THE ARMED PEACE" in text


class TestGR5:
    def test_a_non_player_hegemon_is_watched_the_same_way(self, monkeypatch):
        monkeypatch.setattr(CO, "_identify_max_bloc_share", lambda w: ("Austria", 0.40))
        monkeypatch.setattr(CO, "no_court_left_to_alarm", lambda w, t=None: False)
        # before the fuse: the watch
        world = _quiet_france(turn=20, threat=0, quiet_turns=5)
        r = CO.armed_peace_reading(world)
        assert r["holds"] and r["hegemon"] == "Austria" and r["rise"] == 0
        assert CO.armed_peace_decay(r, "Austria", 50, 3) == 3 and CO.armed_peace_decay(r, "Austria", 46, 3) == 1
        assert CO.armed_peace_decay(r, "Austria", 45, 3) == 0
        # France's slot is NOT the hegemon's: full decay, no rise
        assert CO.armed_peace_decay(r, "France", 46, 3) == 3
        assert CO.armed_peace_rise(r, "France", 45) == 0
        # after the fuse: the rise, on Austria's slot alone
        world = _quiet_france(turn=20, threat=0, quiet_turns=CO.ARMED_PEACE_FUSE_TURNS)
        r = CO.armed_peace_reading(world)
        assert r["rise"] == 3
        assert CO.armed_peace_rise(r, "Austria", 45) == 3 and CO.armed_peace_decay(r, "Austria", 50, 3) == 0
        assert CO.armed_peace_rise(r, "France", 45) == 0
        # the tick moves Austria's slot through reduce_threat / add_threat
        world.threat_by_target["Austria"] = 45
        _tick(world)
        assert world.threat_by_target["Austria"] >= 48


class TestTheFuseIsTwenty:
    """The ruling's 16 was lengthened to 20 on measurement (F1 broke on
    marengo at 16); the number is pinned as a LITERAL here, where every
    other fuse pin reads the constant."""

    def test_nineteen_quiet_turns_do_not_light_it_and_twenty_do(self):
        world = _quiet_france(turn=30, threat=45, quiet_turns=19)
        assert CO.armed_peace_reading(world)["rise"] == 0
        assert _tick(world) == 45
        world = _quiet_france(turn=30, threat=45, quiet_turns=20)
        assert CO.armed_peace_reading(world)["rise"] == 3
        assert _tick(world) == 49
