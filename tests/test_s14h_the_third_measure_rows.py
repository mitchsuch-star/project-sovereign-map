"""Pre-Deploy S14h — the third measure's rows (DD-B, October 25–26, 2026).

The pins of `docs/BUG_FIXES.md` §S14G: one class per row (`TestS14G<n>`),
one per sibling the sweep found (`TestS14GX<n>`), and the rulings' own
classes (`TestS14GD1`, `TestS14GD2`, `TestS14GD3`, `TestS14GD6`). Part 1
(October 26, 2026) holds the twelve P2s S14G-1 … 12 with the four rulings
built as recommended and the part's siblings; part 2 adds the P3s
S14G-13 … 33 and the instrument row S14G-I1. Each section below carries its
row's record: the cause, the sighting, the fix. Merged from the part's row
files (`tests/test_s14h_row<NN>.py`) by the landing's merge script; the
sections' helpers are prefixed `_r<n>_` so the file stays one module (the
hook's `--dist loadgroup` keeps it on one worker).
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import contextlib
import inspect
import io
import json
import pathlib
import random
import re

import pytest


# ══════════════════════════════════════════════════════════════════════════
# row01
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 - S14G-1 with its ruling S14G-D1 (October 26, 2026).
#
# THE ROW (`docs/BUG_FIXES.md` S14G-1, `docs/DESIGN_REFINEMENT.md` S14G-D1):
# retaking an ALLY's capital from the enemy scored as the conquest of an enemy
# capital. The sighting (DD-B's third measure, conquest #5, P2, turn 3, action
# 58): Ney, with the whole army, attacked Archduke Charles at Munich - Bavaria's
# capital, which Austria had just taken from the ally - and drove him out. The
# reply said "Europe's alarm rises +8 ... Captured an enemy capital +15", the
# top bar's Threat went 84 -> 100/100, and the capture asked "Plunder it for
# 1,200 gold" and handed Munich to France. Three arms read the liberation of an
# ally's ground as a conquest: `capture_region`'s +2 `region_capture` (the
# province's starting owner was neither France nor a title France held), the
# pipeline's +15 `capital_capture` (no check of whose capital, nor whose hand it
# ended in) and `_attempt_region_capture`'s plunder question (skipped only for
# `is_own_soil_recapture`, France's own starting soil). `_alarm_line` printed
# the applied total beside raw parts that did not add up to it when the cap at
# 100 clipped a row.
#
# THE RULING (S14G-D1, October 26, 2026, taken as recommended): a LIBERATION,
# HANDED BACK AT ONCE. A province whose home nation (`game_end.home_nation_of`)
# is an ally (ALLIANCE / DEFENSIVE_ALLIANCE) or a client (a vassal whose lord is
# the capturer, or the capturer's own lord) of the capturer, retaken from an
# enemy (the controller at the moment of capture is at war with the capturer
# and is not the home nation), returns to the home nation's control AT ONCE:
# no plunder/secure question, no `region_capture` and no `capital_capture`
# alarm (the battle's own alarm stands), and the line says whose it is -
# "Munich, Bavaria's capital, retaken - handed back to Bavaria." If the home
# court is gone (not in `get_active_nations`) there is nobody to hand it to: the
# capture stays a conquest as today and the reply says so in one clause
# ("Bavaria's court is gone - Munich is held for the peace.").
#
# THE FIX. ONE predicate, `world_state.liberates_ally_ground(world, region,
# capturer) -> home | ''` (THE SEAM: held down it answers '' and every arm
# reads today's conquest, byte for byte), read by `capture_region` (the
# hand-back, the title, the +2), `_attempt_region_capture` (the question, the
# event, the line), `_apply_occupation_capture_effects` (the fortress
# completing), the `_post_combat_pipeline`'s +15 (a `liberated` key from the
# capture's result - or, for the garrison assault whose pipeline runs BEFORE
# the capture, the predicate read on the board as it stands) and the reckless
# auto-charge's own bare-assignment copy - for the player and the AI alike
# (Golden Rule 5). One builder for the sentence (`liberation_line`) and one for
# the secure-and-log (`complete_liberation`); the surfaces that announce a
# capture read `CombatExecutor._capture_words`. `_alarm_line` prints each
# clipped row's applied share and "(capped at 100)".
#
# WHAT WAS KEPT. The battle's own alarm (battle_win, decisive_victory), the
# glory ladder, the +5 authority a captured capital earns the player, the war
# contribution's `allied_region_restored` kind and the campaign ledger's
# capture record (the war remembers who retook what); `_pursuit_capture_guard`
# (an ally-HELD province stays "not ours to take"); the own-soil liberation
# (CA8-13) untouched; the peace-time return (`game_end.ally_homeland_returns`)
# for what a liberation did not reach. Sibling pins below are
# `TestS14GX1_<k>`; the orchestrator renumbers them.
#
# The board: the shipped 1805 scenario (`WorldState.from_scenario`), France
# allied to Bavaria (Munich, Swabia, Franconia), Austria at war with both.
# Archduke Charles stood in for Mack in no test: his Habsburg Resolve holds him
# in the field at 15% morale at any strength, so "driven out" is not
# deterministic; Mack at Munich is destroyed outright - the nearest the board
# allows to the sighting.

_R1_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")

_R1_MUNICH_LINE = "Munich, Bavaria's capital, retaken — handed back to Bavaria."
_R1_SWABIA_LINE = "Swabia, Bavaria's province, retaken — handed back to Bavaria."


def _r1_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r1_boot():
    from backend.models.world_state import WorldState
    with _r1_quiet():
        return WorldState.from_scenario(str(_R1_SCENARIO))


def _r1_copy(boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


def _r1_take(world, region: str, nation: str = "Austria") -> None:
    """The enemy's capture, staged through the real seam (a conquest record
    and all) - then the alarm book is cleared so the test reads only the
    capture under test."""
    with _r1_quiet():
        world.capture_region(region, nation)
    world.threat_sources_this_turn = []


def _r1_executor():
    from backend.commands.executor import CommandExecutor
    with _r1_quiet():
        return CommandExecutor()


def _r1_board(boot, region: str = "Munich", *, foe: str = "Mack", foe_strength: int = 2500,
              lead: str = "Ney", lead_at: str = "Franche-Comte"):
    """Austria holds `region` (Bavaria's), `foe` stands in it, `lead` is one
    march away with the army. Returns (world, game_state, executor)."""
    world = _r1_copy(boot)
    _r1_take(world, region)
    enemy = world.get_marshal(foe)
    enemy.location = region
    enemy.strength = foe_strength
    ney = world.get_marshal(lead)
    ney.location = lead_at
    ney.strength = 40000
    world.threat_sources_this_turn = []
    world.calculate_visibility()
    return world, {"world": world}, _r1_executor()


def _r1_attack(executor, game_state, lead: str = "Ney", foe: str = "Mack") -> dict:
    random.seed(7)
    with _r1_quiet():
        return executor.execute({"command": {
            "raw_input": f"{lead}, attack {foe}", "marshal": lead,
            "action": "attack", "target": foe}}, game_state)


def _r1_france_rows(world) -> list:
    return [r for r in world.threat_sources_this_turn
            if isinstance(r, dict) and r.get("target") == "France"]


def _r1_sources(world, nation: str = "France") -> list:
    return [r["source"] for r in world.threat_sources_this_turn
            if isinstance(r, dict) and r.get("target") == nation]


class TestS14G1:
    """The defect on the shipped board. The old reading, reproduced before the
    fix: Ney destroys Mack at Munich; Munich went to France; the reply read
    "[Alarm] Europe's alarm rises +20 - Conquered territory +2, Won a battle
    +3, Captured an enemy capital +15." and "Your forces have taken Munich.
    Plunder it for 1,200 gold ..."; `pending_capture_choice` stood."""

    def test_munich_is_handed_back_to_bavaria_at_once(self, _r1_boot):
        world, gs, ex = _r1_board(_r1_boot)
        assert world.get_region("Munich").controller == "Austria"
        result = _r1_attack(ex, gs)
        assert result.get("success") is True
        # control returns to the home nation, not to France
        assert world.get_region("Munich").controller == "Bavaria"
        # no plunder / secure question, in the world and on the reply
        assert world.pending_capture_choice is None
        assert not result.get("pending_capture_choice")
        assert "capture_data" not in result
        assert "Plunder" not in result["message"] and "plunder" not in result["message"]
        # the line says whose capital it is
        assert _R1_MUNICH_LINE in result["message"]
        # Ney holds the ground he marched into (the ally's soil, as a friend)
        assert world.get_marshal("Ney").location == "Munich"

    def test_the_conquest_alarm_is_not_scored(self, _r1_boot):
        world, gs, ex = _r1_board(_r1_boot)
        before = int(world.threat_by_target.get("France", 0))
        result = _r1_attack(ex, gs)
        sources = _r1_sources(world)
        assert "capital_capture" not in sources
        assert "region_capture" not in sources
        assert sources and set(sources) <= {"battle_win", "decisive_victory"}, sources
        assert "Captured an enemy capital" not in result["message"]
        assert "Conquered territory" not in result["message"]
        # the battle's own alarm stands (+3 won a battle)
        assert "Won a battle +3" in result["message"]
        assert int(world.threat_by_target["France"]) - before <= 8
        # Austria's own earlier +2 (the staged capture) is not France's row
        assert all(r.get("target") != "France" or r["source"] != "region_capture"
                   for r in world.threat_sources_this_turn)

    def test_the_province_leaves_no_conquest_title_for_france(self, _r1_boot):
        """A liberation leaves no title record - the home court holds its own
        ground - so neither the peace-time return nor the status quo can read
        Munich as a conquest of France's."""
        world, gs, ex = _r1_board(_r1_boot)
        assert world.province_title.get("Munich", {}).get("holder") == "Austria"
        _r1_attack(ex, gs)
        assert "Munich" not in world.province_title
        from backend.game_logic import game_end
        assert "Munich" not in sum(
            game_end.ally_homeland_returns(world, "France", "Austria").values(), [])

    def test_the_log_row_the_event_and_the_chronicle(self, _r1_boot):
        world, gs, ex = _r1_board(_r1_boot)
        result = _r1_attack(ex, gs)
        rows = [e for e in world.event_log if e.get("type") == "region_captured"
                and e.get("region") == "Munich" and e.get("captured_by") == "France"]
        assert len(rows) == 1
        row = rows[0]
        assert row["method"] == "liberated"
        assert row["liberated_to"] == "Bavaria"
        assert row["captured_from"] == "Austria"
        assert row["capital"] is True
        # the battle event the client reads names the court it went back to
        battle = result["events"][0]
        assert battle["region_conquered"] is True
        assert battle["liberated_to"] == "Bavaria"
        # the campaign log's third-person line (with and without a world)
        from backend.campaign_log import format_event_oneliner
        expect = "Munich, Bavaria's capital, retaken by France — handed back to Bavaria."
        assert format_event_oneliner(row, "France", world) == expect
        assert format_event_oneliner(row, "France") == expect

    def test_the_battle_report_leads_with_the_liberation_not_falls_to(self, _r1_boot):
        """The After-Action Report's capture note (EG-X5) said "Munich falls to
        Ney." over a province handed back to Bavaria - the driven CMD-H arm,
        turn 6, read it. The note leads with the liberation's line and keeps
        the works clause it always carried."""
        world, gs, ex = _r1_board(_r1_boot)
        world.get_region("Munich").garrison_strength = 2000   # the driven arm's 2,000
        result = _r1_attack(ex, gs)
        note = result["battle_report"]["capture_note"]
        assert note == (f"{_R1_MUNICH_LINE} The last 2,000 of the garrison at Munich "
                        f"give way."), note
        assert "falls to" not in note

    def test_the_morning_dispatch_carries_the_line(self, _r1_boot):
        from backend.game_logic import dispatch
        world, gs, ex = _r1_board(_r1_boot)
        _r1_attack(ex, gs)
        with _r1_quiet():
            head = dispatch._build_headline(world, "France", record=False)
        said = [head["text"]] + list(head.get("sub_beats") or [])
        assert f"Sire — {_R1_MUNICH_LINE}" in said, said

    def test_fog_and_visibility_read_the_allied_soil_consistently(self, _r1_boot):
        from backend.models.intel import FULL
        world, gs, ex = _r1_board(_r1_boot)
        _r1_attack(ex, gs)
        world.calculate_visibility()
        assert world.get_region_intel("Munich").visibility == FULL   # Ney stands there
        region = world.get_region("Munich")
        assert int(region.garrison_strength) == 0 and not region.garrison_detachment
        assert int(region.stability) == 25
        assert "Munich" in world.get_nation_regions("Bavaria")
        assert "Munich" not in world.get_nation_regions("France")

    def test_the_players_own_liberation_is_no_third_party_dispatch_line(self, _r1_boot):
        """DDB-43's "two OTHER courts" line (province_changed_hands) is for a
        province passing between courts that are not the player's; the
        player's own liberation is his act, said in his reply and his
        dispatch's liberation class - never also as Austria-to-Bavaria news."""
        world, gs, ex = _r1_board(_r1_boot)
        world.pending_dispatch_events = []
        _r1_attack(ex, gs)
        assert [e for e in world.pending_dispatch_events
                if e["type"] == "province_changed_hands"] == []

    def test_the_alarm_line_prints_the_applied_share_when_the_cap_clips(self, _r1_boot):
        """The old line: "+8" beside "+2 +3 +5 +15" - the applied total beside
        raw parts that do not add up. Now each clipped row shows what reached
        the bar, and the line says the cap clipped it."""
        from backend.commands.combat_executor import CombatExecutor
        from backend.game_logic.coalition import add_threat
        world = _r1_copy(_r1_boot)
        world.threat_by_target["France"] = 84
        world.threat_sources_this_turn = []
        for amount, key in ((2, "region_capture"), (3, "battle_win"),
                            (5, "decisive_victory"), (15, "capital_capture")):
            add_threat(world, amount, key, target="France")
        line = CombatExecutor._alarm_line(world, 0)
        assert line == (
            "\n[Alarm] Europe's alarm rises +16 — Conquered territory +2, Won a battle +3, "
            "Won a decisive battle +5, Captured an enemy capital +15 (+6 counted) "
            "(capped at 100).")
        assert int(world.threat_by_target["France"]) == 100

    def test_the_alarm_line_with_no_clip_is_unchanged_and_a_full_bar_says_so(self, _r1_boot):
        from backend.commands.combat_executor import CombatExecutor
        from backend.game_logic.coalition import add_threat
        world = _r1_copy(_r1_boot)
        world.threat_by_target["France"] = 40
        world.threat_sources_this_turn = []
        add_threat(world, 3, "battle_win", target="France")
        assert (CombatExecutor._alarm_line(world, 0)
                == "\n[Alarm] Europe's alarm rises +3 — Won a battle +3.")
        world.threat_by_target["France"] = 100
        world.threat_sources_this_turn = []
        add_threat(world, 3, "battle_win", target="France")
        assert (CombatExecutor._alarm_line(world, 0)
                == "\n[Alarm] Europe's alarm holds at 100 — Won a battle +3 (+0 counted) "
                   "(capped at 100).")


class TestS14GD1:
    """The ruling's arms. Liberation, handed back at once; the home court
    gone - a conquest as today with the one clause; the predicate's reach;
    the seam held down restores today's reading byte for byte."""

    def test_the_predicate_reaches_an_ally_a_client_and_a_lord(self, _r1_boot):
        from backend.models import world_state as ws
        world = _r1_copy(_r1_boot)
        # an ally (Bavaria, ALLIANCE with France), its capital held by Austria
        _r1_take(world, "Munich")
        assert ws.liberates_ally_ground(world, "Munich", "France") == "Bavaria"
        # a client: Holland is France's vassal; Britain holds Amsterdam
        _r1_take(world, "Amsterdam", "Britain")
        assert world.get_diplomatic_state("France", "Holland") == "VASSAL"
        assert ws.liberates_ally_ground(world, "Amsterdam", "France") == "Holland"
        # the capturer's own LORD: Holland (the client) retakes France's
        # ground from Britain - handed back to France
        _r1_take(world, "Normandy", "Britain")
        assert world.get_diplomatic_state("Holland", "Britain") == "WAR"
        assert ws.liberates_ally_ground(world, "Normandy", "Holland") == "France"

    def test_the_predicate_is_silent_outside_the_ruling(self, _r1_boot):
        from backend.models import world_state as ws
        world = _r1_copy(_r1_boot)
        # own soil is CA8-13's liberation, not this one
        _r1_take(world, "Lorraine")
        assert ws.is_own_soil_recapture(world, "Lorraine", "France")
        assert ws.liberates_ally_ground(world, "Lorraine", "France") == ""
        # a court at PEACE with the capturer is no friend: Berlin held by Austria
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"
        _r1_take(world, "Berlin")
        assert ws.liberates_ally_ground(world, "Berlin", "France") == ""
        # the holder is not an enemy (Bavaria's own province held by Bavaria)
        assert ws.liberates_ally_ground(world, "Swabia", "France") == ""
        # an enemy's own ground (Vienna held by Austria) - a conquest
        assert ws.liberates_ally_ground(world, "Vienna", "France") == ""
        # no capturer, no region
        assert ws.liberates_ally_ground(world, "", "France") == ""
        assert ws.liberates_ally_ground(world, "Munich", "") == ""

    def test_a_gone_home_court_stays_a_conquest_and_says_so(self, _r1_boot):
        """Austria takes ALL of Bavaria (the court is eliminated, its ties go
        with it): nobody is left to hand Munich to. The capture is today's
        conquest - France holds it, the question is asked, the +2 and the +15
        stand - and the reply says why in one clause."""
        world = _r1_copy(_r1_boot)
        for region in ("Franconia", "Swabia", "Munich"):
            _r1_take(world, region)
        assert "Bavaria" not in world.get_active_nations()
        from backend.models import world_state as ws
        assert ws.liberates_ally_ground(world, "Munich", "France") == ""
        assert ws.liberation_court_gone(world, "Munich", "France") == "Bavaria"
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Munich", 2500
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Franche-Comte", 40000
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        result = _r1_attack(_r1_executor(), {"world": world})
        assert world.get_region("Munich").controller == "France"
        assert world.pending_capture_choice is not None
        assert "Plunder it for" in result["message"]
        assert "Bavaria's court is gone — Munich is held for the peace." in result["message"]
        assert "liberated_to" not in result["events"][0]
        sources = _r1_sources(world)
        assert "capital_capture" in sources and "region_capture" in sources

    def test_a_province_of_a_court_never_gone_carries_no_clause(self, _r1_boot):
        """The clause belongs to a vanished court alone: Munich retaken for a
        LIVE Bavaria reads the liberation line and never the clause."""
        world, gs, ex = _r1_board(_r1_boot)
        result = _r1_attack(ex, gs)
        assert "court is gone" not in result["message"]

    def test_the_seam_held_down_restores_the_conquest_byte_for_byte(self, _r1_boot, monkeypatch):
        """THE SEAM: `world_state.liberates_ally_ground` answering '' is
        today's reading - Munich to France, the plunder question, the +2 and
        the +15 and the old sentence."""
        from backend.models import world_state as ws
        monkeypatch.setattr(ws, "liberates_ally_ground", lambda *a, **k: "")
        world, gs, ex = _r1_board(_r1_boot)
        world.get_region("Munich").garrison_strength = 2000
        result = _r1_attack(ex, gs)
        assert world.get_region("Munich").controller == "France"
        assert world.pending_capture_choice is not None
        assert result.get("pending_capture_choice") is True
        assert "Plunder it for" in result["message"]
        assert "Munich has been captured by France!" in result["message"]
        assert "retaken" not in result["message"]
        assert "Captured an enemy capital +15" in result["message"]
        assert "Conquered territory +2" in result["message"]
        sources = _r1_sources(world)
        assert "capital_capture" in sources and "region_capture" in sources
        assert world.province_title["Munich"]["holder"] == "France"
        assert "liberated_to" not in result["events"][0]
        assert result["battle_report"]["capture_note"].startswith("Munich falls to Ney.")

    def test_the_names_and_the_possessive(self, _r1_boot):
        from backend.models import world_state as ws
        world = _r1_copy(_r1_boot)
        assert ws.liberation_line(world, "Rome", "PapalStates") == (
            "Rome, the Papal States' capital, retaken — handed back to the Papal States.")
        assert ws.liberation_line(world, "Munich", "Bavaria") == _R1_MUNICH_LINE
        assert ws.liberation_line(world, "Swabia", "Bavaria") == _R1_SWABIA_LINE
        assert ws.liberation_gone_clause(world, "Rome", "PapalStates") == (
            "The Papal States' court is gone — Rome is held for the peace.")
        # a log asked without a world still names the court
        assert ws.liberation_line(None, "Munich", "Bavaria", by="France", capital=True) == (
            "Munich, Bavaria's capital, retaken by France — handed back to Bavaria.")

    def test_the_peace_time_return_stays_for_what_a_liberation_did_not_reach(self, _r1_boot):
        """`ally_homeland_returns` is untouched (PC-F75): a province France
        holds by a conquest record naming a member of the ceder's bloc (Russia,
        Austria's ally) whose home nation is France's co-belligerent still
        goes home at the peace. The liberation writes no such record - nothing
        is left to return."""
        from backend.game_logic import game_end
        world = _r1_copy(_r1_boot)
        with _r1_quiet():
            world.capture_region("Franconia", "France")      # (Bavaria's; a plain hold)
        world.province_title["Franconia"] = {
            "kind": game_end.TITLE_CONQUEST, "since": 1, "from": "Russia",
            "holder": "France", "house": "France"}
        back = game_end.ally_homeland_returns(world, "France", "Austria")
        assert back.get("Bavaria") == ["Franconia"]


class TestS14GX1:
    """Sibling: the OCCUPATION road. A fortified province (the occupation
    branch of `_attempt_region_capture`) completes its capture at the turn's
    tick through `_apply_occupation_capture_effects`, which read no
    liberation - it would have asked "plunder it for ..." the turn after the
    siege. It now completes as a liberation, and the siege's own opening
    sentence says the province will be handed back."""

    def _fortress(self, boot):
        world = _r1_copy(boot)
        _r1_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        ney = world.get_marshal("Ney")
        ney.location = "Swabia"
        world.get_region("Swabia").buildings.append({"type": "fortification", "level": 1})
        world.calculate_visibility()
        return world, ney

    def test_the_siege_says_it_will_be_handed_back(self, _r1_boot):
        world, ney = self._fortress(_r1_boot)
        capture = _r1_executor()._combat._attempt_region_capture(
            ney, "Swabia", world, {"world": world}, had_garrison=False)
        assert capture["occupation_started"] is True
        assert capture["message"].endswith(
            "Swabia is fortified! Ney must hold for 1 turn to capture. "
            "It will be handed back to Bavaria.")
        assert world.get_region("Swabia").controller == "Austria"

    def test_the_fortress_completes_as_a_liberation(self, _r1_boot):
        world, ney = self._fortress(_r1_boot)
        _r1_executor()._combat._attempt_region_capture(
            ney, "Swabia", world, {"world": world}, had_garrison=False)
        with _r1_quiet():
            events = world._process_tactical_states()
        done = [e for e in events if e.get("type") == "occupation_complete"]
        assert len(done) == 1
        assert done[0]["message"] == f"Ney has secured the fortress at Swabia! {_R1_SWABIA_LINE}"
        assert done[0]["capture_choice"] == "liberated"
        assert world.get_region("Swabia").controller == "Bavaria"
        assert world.pending_capture_choice is None
        assert "Swabia" not in world.province_title
        assert [e["liberated_to"] for e in world.event_log
                if e.get("type") == "region_captured" and e.get("region") == "Swabia"
                and e.get("captured_by") == "France"] == ["Bavaria"]

    def test_a_gone_court_says_so_at_the_siege_and_at_the_completion(self, _r1_boot):
        """The occupation road carries the D1 clause too: a fortress of a
        vanished court is a conquest as today, and both the siege's opening
        and the completing tick say why the province is held, not handed."""
        world = _r1_copy(_r1_boot)
        for region in ("Franconia", "Swabia", "Munich"):
            _r1_take(world, region)
        assert "Bavaria" not in world.get_active_nations()
        world.get_marshal("Mack").location = "Tyrol"
        ney = world.get_marshal("Ney")
        ney.location = "Swabia"
        world.get_region("Swabia").buildings.append({"type": "fortification", "level": 1})
        capture = _r1_executor()._combat._attempt_region_capture(
            ney, "Swabia", world, {"world": world}, had_garrison=False)
        clause = "Bavaria's court is gone — Swabia is held for the peace."
        assert capture["message"].endswith(clause)
        assert "handed back" not in capture["message"]
        with _r1_quiet():
            events = world._process_tactical_states()
        done = [e for e in events if e.get("type") == "occupation_complete"][0]
        assert clause in done["message"]
        assert "Plunder it for" in done["message"]
        assert world.get_region("Swabia").controller == "France"
        assert world.pending_capture_choice is not None

    def test_the_fortress_held_down_asks_again(self, _r1_boot, monkeypatch):
        from backend.models import world_state as ws
        monkeypatch.setattr(ws, "liberates_ally_ground", lambda *a, **k: "")
        world, ney = self._fortress(_r1_boot)
        capture = _r1_executor()._combat._attempt_region_capture(
            ney, "Swabia", world, {"world": world}, had_garrison=False)
        assert "handed back" not in capture["message"]
        with _r1_quiet():
            world._process_tactical_states()
        assert world.get_region("Swabia").controller == "France"
        assert world.pending_capture_choice is not None


class TestS14GX2:
    """Sibling: the AI's road (Golden Rule 5). The AI walks the same
    `_attempt_region_capture`; Russia - Austria's ally - retaking Austrian
    ground from France hands it back too, and never plunders the ally's land
    (an aggressive AI marshal would have paid himself x4 to sack it)."""

    def _board(self, boot, region: str = "Moravia"):
        world = _r1_copy(boot)
        _r1_take(world, region, "France")
        kut = world.get_marshal("Kutuzov")
        # a province next to `region` for the marshal to stand in
        kut.location = world.get_region(region).adjacent_regions[0]
        kut.strength = 38000
        return world, kut

    def test_the_ai_hands_austrian_ground_back(self, _r1_boot):
        world, kut = self._board(_r1_boot)
        assert world.get_diplomatic_state("Russia", "Austria") == "ALLIANCE"
        gold = int(world.nation_gold.get("Russia", 0))
        capture = _r1_executor()._combat._attempt_region_capture(
            kut, "Moravia", world, {"world": world})
        assert capture["captured"] is True
        assert capture["liberated_to"] == "Austria"
        assert capture["capture_choice"] == "liberated"
        assert world.get_region("Moravia").controller == "Austria"
        assert not getattr(world.get_region("Moravia"), "plundered", False)
        assert int(world.nation_gold.get("Russia", 0)) == gold   # no windfall
        assert world.pending_capture_choice is None
        assert "Russia" not in [r["target"] for r in world.threat_sources_this_turn
                                if r.get("source") == "region_capture"]
        row = [e for e in world.event_log if e.get("type") == "region_captured"
               and e.get("captured_by") == "Russia"][-1]
        assert row["method"] == "liberated" and row["liberated_to"] == "Austria"
        assert capture["liberation_line"] == (
            "Moravia, Austria's province, retaken — handed back to Austria.")

    def test_a_third_party_liberation_is_announced_to_the_court_that_holds_it(self, _r1_boot):
        """Two courts that are not the player's: Britain retakes Austrian
        Moravia from Prussia (Britain and Austria are allied; Prussia is at war
        with Britain) - the DDB-43 line names the court that NOW holds the
        province, Austria, not the liberator."""
        world = _r1_copy(_r1_boot)
        world.diplomatic_states[world._make_diplo_key("Britain", "Prussia")] = "WAR"
        _r1_take(world, "Moravia", "Prussia")
        world.pending_dispatch_events = []
        moore = world.get_marshal("Moore")
        moore.location, moore.strength = "Bohemia", 30000
        capture = _r1_executor()._combat._attempt_region_capture(
            moore, "Moravia", world, {"world": world})
        assert capture["liberated_to"] == "Austria"
        moved = [e for e in world.pending_dispatch_events
                 if e["type"] == "province_changed_hands"]
        assert len(moved) == 1
        assert moved[0]["template_vars"]["new_display"] == "Austria"
        assert moved[0]["template_vars"]["old_display"] == "Prussia"

    def test_the_ai_attack_hands_vienna_back_with_no_capital_alarm(self, _r1_boot):
        """Through the executor, as the enemy phase walks it: Kutuzov destroys
        the French corps at Vienna and the capital goes back to Austria - no
        +15 for Russia."""
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Vienna", "France")
        davout = world.get_marshal("Davout")
        davout.location, davout.strength = "Vienna", 5      # a corps the guns cannot fail to destroy
        kut = world.get_marshal("Kutuzov")
        kut.location = "Moravia"
        kut.strength = 38000
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        random.seed(3)
        with _r1_quiet():
            result = _r1_executor().execute({"command": {
                "type": "specific", "marshal": "Kutuzov", "action": "attack",
                "target": "Davout", "_autonomous_execution": True}}, {"world": world})
        assert result.get("success") is True, result
        assert world.get_region("Vienna").controller == "Austria"
        assert "capital_capture" not in _r1_sources(world, "Russia")
        assert "region_capture" not in _r1_sources(world, "Russia")
        assert any(e.get("type") == "region_captured" and e.get("liberated_to") == "Austria"
                   and e.get("capital") is True for e in world.event_log)


class TestS14GX3:
    """Sibling: the CLIENT's ground and the ally's NON-capital provinces. The
    ruling reaches every province of the home court, not the capital alone
    (Swabia - "Bavaria's province") and a client of the capturer (Holland, a
    French vassal), at the instant capture."""

    def test_a_non_capital_province_of_the_ally(self, _r1_boot):
        world, gs, ex = _r1_board(_r1_boot, "Swabia")
        result = _r1_attack(ex, gs)
        assert world.get_region("Swabia").controller == "Bavaria"
        assert _R1_SWABIA_LINE in result["message"]
        assert world.pending_capture_choice is None
        sources = _r1_sources(world)
        assert "region_capture" not in sources and "capital_capture" not in sources
        row = [e for e in world.event_log if e.get("type") == "region_captured"
               and e.get("captured_by") == "France"][-1]
        assert "capital" not in row and row["liberated_to"] == "Bavaria"

    def test_a_clients_ground_is_handed_back_to_the_client(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Gelderland", "Britain")
        ney = world.get_marshal("Ney")
        ney.location = "Gelderland"
        capture = _r1_executor()._combat._attempt_region_capture(
            ney, "Gelderland", world, {"world": world})
        assert capture["liberated_to"] == "Holland"
        assert world.get_region("Gelderland").controller == "Holland"
        assert capture["message"] == (
            "Gelderland, Holland's province, retaken — handed back to Holland.")
        assert world.pending_capture_choice is None


class TestS14GX4:
    """Sibling: the MARCH. The PF-3 move-capture (an empty enemy-held province
    walked into, `auto_secure=True`) called the same capture pipeline and said
    "Swabia falls to France! (was Austria)" - and "The province is secured."
    The march now says whose ground it is, and nothing is secured for France."""

    def test_the_march_hands_swabia_back(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        bern = world.get_marshal("Bernadotte")
        assert bern.location == "Franconia"
        world.calculate_visibility()
        with _r1_quiet():
            result = _r1_executor().execute({"command": {
                "raw_input": "Bernadotte, move to Swabia", "marshal": "Bernadotte",
                "action": "move", "target": "Swabia"}}, {"world": world})
        assert result["success"] is True
        assert _R1_SWABIA_LINE in result["message"]
        assert "falls to" not in result["message"]
        assert "secured" not in result["message"]
        assert world.get_region("Swabia").controller == "Bavaria"
        assert world.pending_capture_choice is None
        assert result["events"][0]["liberated_to"] == "Bavaria"
        assert result["events"][0]["captured_by"] == "France"

    def test_the_march_held_down_reads_as_before(self, _r1_boot, monkeypatch):
        from backend.models import world_state as ws
        monkeypatch.setattr(ws, "liberates_ally_ground", lambda *a, **k: "")
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        world.calculate_visibility()
        with _r1_quiet():
            result = _r1_executor().execute({"command": {
                "raw_input": "Bernadotte, move to Swabia", "marshal": "Bernadotte",
                "action": "move", "target": "Swabia"}}, {"world": world})
        assert "Swabia falls to France! (was Austria)" in result["message"]
        assert world.get_region("Swabia").controller == "France"


class TestS14GX5:
    """Sibling: every site that ANNOUNCES a capture. The garrison assault, the
    unopposed march into an empty province, the glorious charge each wrote
    their own "Captured: Austria -> France" / "has been captured by France!"
    sentence beside a province that had gone back to Bavaria; they read one
    helper now (`CombatExecutor._capture_words`)."""

    def test_the_unopposed_attack_march(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        ney = world.get_marshal("Ney")
        ney.location = "Rhineland"
        world.calculate_visibility()
        with _r1_quiet():
            result = _r1_executor().execute({"command": {
                "raw_input": "Ney, attack Swabia", "marshal": "Ney",
                "action": "attack", "target": "Swabia"}}, {"world": world})
        assert _R1_SWABIA_LINE in result["message"]
        assert "Captured:" not in result["message"]
        assert not result.get("pending_capture_choice")
        assert result["events"][0]["liberated_to"] == "Bavaria"
        assert world.get_region("Swabia").controller == "Bavaria"

    def test_the_garrison_assault_says_it_and_scores_no_conquest(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Rhineland", 40000
        region = world.get_region("Swabia")
        region.garrison_strength, region.garrison_detachment = 3000, True
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        with _r1_quiet():
            result = _r1_executor().execute({"command": {
                "raw_input": "Ney, attack Swabia", "marshal": "Ney",
                "action": "attack", "target": "Swabia"}}, {"world": world})
        assert _R1_SWABIA_LINE in result["message"]
        assert "Captured:" not in result["message"]
        assert world.get_region("Swabia").controller == "Bavaria"
        assert not result.get("pending_capture_choice")
        assert "region_capture" not in _r1_sources(world)

    def test_the_garrison_assault_on_a_capital_scores_no_capital_alarm(self, _r1_boot):
        """The garrison pipeline runs BEFORE the capture, so it reads the
        liberation off the board as it stands: Munich's garrison collapsing
        is no "captured an enemy capital"."""
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Munich")
        world.get_marshal("Mack").location = "Tyrol"
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Franche-Comte", 40000
        region = world.get_region("Munich")
        region.garrison_strength, region.garrison_detachment = 3000, True
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        with _r1_quiet():
            result = _r1_executor().execute({"command": {
                "raw_input": "Ney, attack Munich", "marshal": "Ney",
                "action": "attack", "target": "Munich"}}, {"world": world})
        assert _R1_MUNICH_LINE in result["message"], result["message"]
        assert world.get_region("Munich").controller == "Bavaria"
        assert "capital_capture" not in _r1_sources(world)

    def test_the_glorious_charge(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Swabia")
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Swabia", 600
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Franche-Comte", 3
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        random.seed(5)
        with _r1_quiet():
            result = _r1_executor()._combat._execute_glorious_charge(
                murat, "Mack", world, {"world": world})
        assert _R1_SWABIA_LINE in result["message"]
        assert "has been captured by" not in result["message"]
        assert result["events"][0]["liberated_to"] == "Bavaria"
        assert world.pending_capture_choice is None

    def test_the_helper_reads_the_line_the_clause_or_the_default(self):
        from backend.commands.combat_executor import CombatExecutor
        words = CombatExecutor._capture_words
        assert words({"liberation_line": "X, Y's capital, retaken."}, " d") == " X, Y's capital, retaken."
        assert words({"liberation_gone_line": "Z."}, " d") == " d Z."
        assert words({}, " d") == " d"
        assert words(None, " d") == " d"

    def test_a_landing_reports_the_line_through_the_capture_message(self, _r1_boot):
        """The naval landing appends `capture["message"]` when non-empty: the
        liberation's message IS its line, so the beach says it with no edit
        to the naval verb."""
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Swabia")
        ney = world.get_marshal("Ney")
        ney.location = "Swabia"
        capture = _r1_executor()._combat._attempt_region_capture(
            ney, "Swabia", world, {"world": world})
        assert capture["message"] == _R1_SWABIA_LINE == capture["liberation_line"]


class TestS14GX6:
    """Sibling: the reckless AUTO-charge's own copy (`WorldState.
    _process_reckless_cavalry_turn_start`) - a bare controller assignment
    outside `capture_region`, with its own +15 - handed the province to the
    charger and scored the capital. It reads the same predicate."""

    def test_the_auto_charge_hands_swabia_back(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Swabia")
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Swabia", 600
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Franche-Comte", 4
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        random.seed(5)
        with _r1_quiet():
            events = world._process_reckless_cavalry_turn_start()
        text = " ".join(str(e.get("message")) for e in events)
        assert _R1_SWABIA_LINE in text, text
        assert world.get_region("Swabia").controller == "Bavaria"
        assert "Swabia" not in world.province_title
        assert [e["liberated_to"] for e in world.event_log
                if e.get("type") == "region_captured" and e.get("region") == "Swabia"
                and e.get("captured_by") == "France"] == ["Bavaria"]

    def test_the_auto_charge_on_a_capital_scores_no_alarm(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Munich")
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Munich", 600
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Franche-Comte", 4
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        random.seed(5)
        with _r1_quiet():
            world._process_reckless_cavalry_turn_start()
        assert world.get_region("Munich").controller == "Bavaria"
        assert "capital_capture" not in _r1_sources(world)

    def test_the_auto_charge_held_down_is_the_old_conquest(self, _r1_boot, monkeypatch):
        from backend.models import world_state as ws
        monkeypatch.setattr(ws, "liberates_ally_ground", lambda *a, **k: "")
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Munich")
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Munich", 600
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Franche-Comte", 4
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        random.seed(5)
        with _r1_quiet():
            world._process_reckless_cavalry_turn_start()
        assert world.get_region("Munich").controller == "France"
        assert "capital_capture" in _r1_sources(world)


class TestS14GX7:
    """Sibling: the dispatch's own rule. A won field absorbs the bare
    `region_taken` map fact ("the victory line carries it"); the liberation
    line is the one fact the victory line does not carry (whose ground it
    is), so it is its own class - `region_liberated`, ranked with a routine
    conquest - and survives the absorption."""

    def test_the_class_is_registered_in_every_table(self):
        from backend.game_logic import dispatch
        assert dispatch.HEADLINE_WEIGHTS["region_liberated"] == dispatch.HEADLINE_WEIGHTS["region_taken"] == 68
        assert dispatch._HEADLINE_TEMPLATES["region_liberated"] == "Sire — {line}"
        assert dispatch._HEADLINE_BERTHIER_NOTES["region_liberated"]
        assert "region_liberated" not in dispatch.STANDING_HEADLINE_CLASSES

    def test_a_lone_liberation_leads_the_dispatch(self, _r1_boot):
        from backend.game_logic import dispatch
        world = _r1_copy(_r1_boot)
        world.event_log = [{
            "type": "region_captured", "region": "Munich", "captured_by": "France",
            "captured_from": "Austria", "method": "liberated",
            "liberated_to": "Bavaria", "capital": True,
            "turn": int(world.current_turn)}]
        with _r1_quiet():
            head = dispatch._build_headline(world, "France", record=False)
        assert head["class"] == "region_liberated"
        assert head["text"] == f"Sire — {_R1_MUNICH_LINE}"

    def test_a_plain_conquest_keeps_its_old_class_and_line(self, _r1_boot):
        from backend.game_logic import dispatch
        world = _r1_copy(_r1_boot)
        world.event_log = [{
            "type": "region_captured", "region": "Bohemia", "captured_by": "France",
            "captured_from": "Austria", "method": "secure",
            "turn": int(world.current_turn)}]
        with _r1_quiet():
            head = dispatch._build_headline(world, "France", record=False)
        assert head["class"] == "region_taken"
        assert "Bohemia" in head["text"] and "retaken" not in head["text"]


class TestS14GX8:
    """Sibling: what the ruling did NOT widen. An ally-HELD province stays
    "not ours to take" (PT-F1's `_pursuit_capture_guard`: Swabia in Bavarian
    hands, Mack standing on it, is fought and never transferred); and the own
    soil of France keeps its CA8-13 liberation (no question, `secure`)."""

    def test_an_ally_held_province_is_still_not_ours_to_take(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        assert world.get_region("Swabia").controller == "Bavaria"
        mack = world.get_marshal("Mack")
        mack.strength = 2500
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Franche-Comte", 40000
        world.calculate_visibility()
        result = _r1_attack(_r1_executor(), {"world": world})
        assert world.get_region("Swabia").controller == "Bavaria"
        assert "remains Bavaria's soil" in result["message"]
        assert "retaken" not in result["message"]
        assert world.pending_capture_choice is None

    def test_the_storming_of_an_enemys_own_capital_still_scores(self, _r1_boot):
        """The negative the predicate must keep: Vienna is AUSTRIA's own
        capital, held by Austria - no ally's ground at all. France storming
        it is the conquest it always was: +15 `capital_capture`, +2
        `region_capture`, the plunder question and the province to France."""
        world = _r1_copy(_r1_boot)
        world.get_region("Vienna").garrison_strength = 0
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Vienna", 5
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Moravia", 40000
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        result = _r1_attack(_r1_executor(), {"world": world})
        assert world.get_region("Vienna").controller == "France", result["message"]
        assert world.pending_capture_choice is not None
        assert "Captured an enemy capital +15" in result["message"]
        assert "retaken" not in result["message"]
        assert "capital_capture" in _r1_sources(world)

    def test_own_soil_keeps_the_ca8_13_liberation(self, _r1_boot):
        world = _r1_copy(_r1_boot)
        _r1_take(world, "Lorraine")
        ney = world.get_marshal("Ney")
        ney.location = "Lorraine"
        capture = _r1_executor()._combat._attempt_region_capture(
            ney, "Lorraine", world, {"world": world})
        assert capture["captured"] is True
        assert capture["capture_choice"] == "secure"
        assert "liberated_to" not in capture
        assert world.get_region("Lorraine").controller == "France"
        assert world.pending_capture_choice is None


# ══════════════════════════════════════════════════════════════════════════
# row02
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 — row 2: S14G-2 with its ruling S14G-D2 (October 26, 2026).
#
# The aggressive marshal's cannon-fire interrupt, KEPT and SAID.
#
# The cause as traced (DD-B's third measure, conquest #7, turn 6, action 117): an
# aggressive marshal drops a standing order and rushes alone to another man's
# battle, and no order reply says he will. `strategic._check_interrupts` runs for
# every order type before the order's own handler; only "literal" is exempt. For
# an aggressive man a lawful battle (a war his nation is IN) within two provinces
# REDIRECTS him — the order is dropped (`_handle_interrupt` sets
# `strategic_order = None`) and he walks to the guns. Massena (22,000, morale
# 36%) on a standing "support Napoleon" at Bohemia, the army massed for Vienna,
# "hears cannon fire! Abandoning orders — rushing to Hungary!" — alone, next to
# Kutuzov's 33,000. The MOVE_TO / HOLD / SUPPORT / FOLLOW replies promised only
# the march; End Turn's gate (S14E-7) named the morale pairing but not that his
# standing order would carry him into it.
#
# S14G-D2 (RULED as recommended, October 26, 2026): KEEP THE INTERRUPT, SAY IT AT
# THE ORDER AND AT THE GATE — it is the character the game sells ("personality is
# character, not situation"); removing it would flatten four marshals into one.
#
# What the fix does: ONE fragment (`strategic.AGGRESSIVE_INTERRUPT_TERMS`, behind
# `aggressive_interrupt_clause`) read by every surface — the MOVE_TO / HOLD /
# SUPPORT / FOLLOW (and typed PURSUE) reply, the standing quote's `terms`, and a
# second End Turn gate clause (`dispatch.end_turn_interrupt_warning`, folded into
# the one `end_turn_army_warning` string the client already latches) built from
# the very facts the interrupt reads. Kept: the interrupt itself is unchanged
# (no behaviour seam; the gate is player-only text).

_R2_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")


def _r2_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r2_boot():
    from backend.models.world_state import WorldState
    with _r2_quiet():
        return WorldState.from_scenario(str(_R2_SCENARIO))


@pytest.fixture
def _r2_board(_r2_boot):
    """The shipped 1805 board; Massena (aggressive, morale 36%) at Bohemia, the
    army's Emperor away at Lorraine, Kutuzov (Russia, at war with France) one
    province off at Hungary with the Russian army visible."""
    from backend.commands.executor import CommandExecutor
    from backend.models.world_state import WorldState
    world = WorldState.from_dict(json.loads(json.dumps(_r2_boot.to_dict(), default=str)))
    massena = world.get_marshal("Massena")
    kutuzov = world.get_marshal("Kutuzov")
    assert massena.personality == "aggressive" and world.is_at_war("France", "Russia")
    massena.location = "Bohemia"
    massena.morale = 36
    kutuzov.location = "Hungary"
    world.calculate_visibility()
    return world, {"world": world}, CommandExecutor(), massena, kutuzov


def _r2_order(executor, game_state, marshal, raw, strategic_type, action, target):
    with _r2_quiet():
        return executor.execute({
            "command": {"raw_input": raw, "marshal": marshal, "action": action, "target": target},
            "is_strategic": True, "strategic_type": strategic_type,
        }, game_state)


def _r2_sentence():
    from backend.commands.strategic import AGGRESSIVE_INTERRUPT_TERMS
    return f"He will drop this order for {AGGRESSIVE_INTERRUPT_TERMS}."


_R2_WORDS = ("He will drop this order for any battle within two provinces "
             "in a war of ours.")


class TestS14G2:
    """The sighting on the shipped board: Massena on a standing SUPPORT with a
    lawful battle at Hungary; the interrupt still redirects him (kept), the
    reply, the quote and the gate all say it. Before: the SUPPORT reply never
    mentioned the interrupt and the gate named only the morale pairing."""

    def test_the_words_are_the_briefs(self):
        assert _r2_sentence() == _R2_WORDS

    def test_the_interrupt_is_kept_and_still_redirects_him(self, _r2_board):
        """KEPT (S14G-D2): the mechanic is untouched — aggressive + lawful
        redirects, the order is dropped for the guns."""
        from backend.commands import strategic as ST
        world, gs, executor, massena, kutuzov = _r2_board
        _r2_order(executor, gs, "Massena", "Massena, support Napoleon", "SUPPORT",
                  "support", "Napoleon")
        assert massena.strategic_order is not None
        world.record_battle("Hungary", "Kutuzov", "Mack", "defender_won")
        interrupt = ST.StrategicOrderProcessor(executor)._check_interrupts(massena, world)
        assert interrupt is not None and interrupt["action"] == "redirect"
        assert interrupt["battle_location"] == "Hungary"

    @pytest.mark.parametrize("strategic_type,action,raw,target", [
        ("SUPPORT", "support", "Massena, support Napoleon", "Napoleon"),
        ("MOVE_TO", "move", "Massena, march to Franconia", "Franconia"),
        ("HOLD", "hold", "Massena, hold Bohemia", "Bohemia"),
    ])
    def test_the_reply_says_it(self, _r2_board, strategic_type, action, raw, target):
        world, gs, executor, massena, _k = _r2_board
        reply = _r2_order(executor, gs, "Massena", raw, strategic_type, action, target)
        assert reply.get("success") is True, reply.get("message")
        assert _R2_WORDS in reply["message"], reply["message"]

    def test_the_follow_reply_says_it(self, _r2_board):
        world, gs, executor, massena, _k = _r2_board
        with _r2_quiet():
            reply = executor.execute({
                "command": {"raw_input": "Massena, follow Napoleon", "marshal": "Massena",
                            "action": "support", "target": "Napoleon"},
                "is_strategic": True, "strategic_type": "SUPPORT",
                "standing_follow": True}, gs)
        assert reply.get("success") is True, reply.get("message")
        assert massena.strategic_order.standing_follow is True
        assert "stands until you cancel it" in reply["message"]
        assert _R2_WORDS in reply["message"], reply["message"]

    def test_the_quote_says_it_before_the_order(self, _r2_board):
        """The choice is made at the quote: `terms` carries the same words."""
        from backend.commands.order_quotes import follow_quote, march_quote, support_quote
        world, gs, executor, massena, _k = _r2_board
        napoleon = world.get_marshal("Napoleon")
        assert _R2_WORDS in march_quote(world, massena, "Franconia")["terms"]
        assert _R2_WORDS in support_quote(world, massena, napoleon)["terms"]
        assert _R2_WORDS in follow_quote(world, massena, napoleon)["terms"]

    def test_the_march_reply_and_its_quote_say_the_same_words(self, _r2_board):
        from backend.commands.order_quotes import march_quote
        world, gs, executor, massena, _k = _r2_board
        terms = march_quote(world, massena, "Franconia")["terms"]
        reply = _r2_order(executor, gs, "Massena", "Massena, march to Franconia", "MOVE_TO",
                          "move", "Franconia")
        assert terms and terms in reply["message"]

    def test_the_gate_names_the_corps_and_the_foe_beside_it(self, _r2_board):
        """End Turn's second clause, from the facts the interrupt reads: an
        aggressive corps holding a standing order with a VISIBLE enemy of a war
        of ours within two provinces — one line, the foe as the player's intel
        shows him (a band at PARTIAL), through the one army-warning string."""
        from backend.game_logic.dispatch import (
            end_turn_army_warning, end_turn_interrupt_warning)
        world, gs, executor, massena, kutuzov = _r2_board
        assert end_turn_interrupt_warning(world, "France") is None   # no order yet
        _r2_order(executor, gs, "Massena", "Massena, hold Bohemia", "HOLD", "hold", "Bohemia")
        line = end_turn_interrupt_warning(world, "France")
        assert line is not None
        assert line.startswith("Massena (aggressive) holds a standing order at Bohemia with ")
        assert "Kutuzov's ~" in line or "Archduke" in line or "Mack's" in line
        assert line.endswith("— he will drop it for any battle within two provinces "
                             "in a war of ours.")
        # the same string the client already latches (morale pairing, if any, closes it)
        assert end_turn_army_warning(world, "France").startswith(line)

    def test_the_gate_names_the_largest_foe_in_range_at_the_shown_figure(self, _r2_board):
        from backend.game_logic import intel_surfaces as surf
        from backend.game_logic.dispatch import BAND_MIDPOINTS, end_turn_interrupt_warning
        from backend.models.intel import FULL
        world, gs, executor, massena, kutuzov = _r2_board
        _r2_order(executor, gs, "Massena", "Massena, hold Bohemia", "HOLD", "hold", "Bohemia")
        line = end_turn_interrupt_warning(world, "France")
        seen = {}
        for foe in world.get_visible_enemies("France"):
            if 0 <= world.get_distance("Bohemia", foe.location) <= 2:
                row = surf.sighting_row(world, "France", foe)
                shown = (int(row["strength"]) if row["visibility"] == FULL
                         else int(BAND_MIDPOINTS.get(row["strength_display"], 0)))
                seen[row["name"]] = shown
        assert seen
        biggest = min(seen, key=lambda k: (-seen[k], k))   # ties: the name, as the gate ranks
        assert f"with {biggest}'s " in line, (line, seen)

    def test_a_foe_out_of_sight_or_out_of_range_is_not_named(self, _r2_board):
        """Fog-honest: the gate reads `get_visible_enemies`; nothing within two
        provinces — or nothing seen — and the corps stands un-nagged."""
        from backend.game_logic.dispatch import end_turn_interrupt_warning
        world, gs, executor, massena, kutuzov = _r2_board
        _r2_order(executor, gs, "Massena", "Massena, hold Bohemia", "HOLD", "hold", "Bohemia")
        assert end_turn_interrupt_warning(world, "France") is not None
        # march him home to a quiet corner of France: no foe within two provinces
        massena.location = "Brittany"
        world.calculate_visibility()
        assert end_turn_interrupt_warning(world, "France") is None

    def test_a_corps_that_chose_continue_is_not_warned(self, _r2_board):
        """The gate reads the interrupt's own suppression: `cannon_fire_ignored_turn`."""
        from backend.game_logic.dispatch import end_turn_interrupt_warning
        world, gs, executor, massena, kutuzov = _r2_board
        _r2_order(executor, gs, "Massena", "Massena, hold Bohemia", "HOLD", "hold", "Bohemia")
        assert end_turn_interrupt_warning(world, "France") is not None
        massena.cannon_fire_ignored_turn = world.current_turn
        assert end_turn_interrupt_warning(world, "France") is None

    def test_the_gate_is_the_players_only_and_a_pure_read(self, _r2_board):
        from backend.game_logic.dispatch import end_turn_interrupt_warning
        world, gs, executor, massena, kutuzov = _r2_board
        _r2_order(executor, gs, "Massena", "Massena, hold Bohemia", "HOLD", "hold", "Bohemia")
        before = json.dumps(world.to_dict(), default=str, sort_keys=True)
        assert end_turn_interrupt_warning(world, "Austria") is None
        end_turn_interrupt_warning(world, "France")
        assert json.dumps(world.to_dict(), default=str, sort_keys=True) == before

    def test_the_other_temperaments_get_no_clause_and_no_warning(self, _r2_board):
        """Aggressive only: a cautious or literal marshal is not rushed; a
        literal one is never interrupted at all (the Grouchy moment)."""
        from backend.commands.strategic import aggressive_interrupt_clause
        from backend.game_logic.dispatch import end_turn_interrupt_warning
        world, gs, executor, massena, kutuzov = _r2_board
        for name, personality in (("Davout", "cautious"), ("Soult", "literal")):
            who = world.get_marshal(name)
            assert who.personality == personality
            assert aggressive_interrupt_clause(world, who) == ""
        _r2_order(executor, gs, "Davout", "Davout, march to Franconia", "MOVE_TO", "move",
                  "Franconia")
        _r2_order(executor, gs, "Soult", "Soult, march to Franconia", "MOVE_TO", "move",
                  "Franconia")
        assert end_turn_interrupt_warning(world, "France") is None

    def test_the_treatys_road_home_is_not_his_to_drop(self, _r2_board):
        """FA-D6: `_check_interrupts` exempts the treaty's road home — so the
        words must not claim otherwise for it."""
        from backend.commands import strategic as ST
        from backend.game_logic import withdrawal
        world, gs, executor, massena, kutuzov = _r2_board
        _r2_order(executor, gs, "Massena", "Massena, hold Bohemia", "HOLD", "hold", "Bohemia")
        order = massena.strategic_order
        assert ST.aggressive_interrupt_applies(world, massena, order) is True
        original = withdrawal.is_road_home_order
        try:
            withdrawal.is_road_home_order = lambda o: True
            assert ST.aggressive_interrupt_applies(world, massena, order) is False
            assert ST.aggressive_interrupt_clause(world, massena, order) == ""
        finally:
            withdrawal.is_road_home_order = original

    def test_the_range_is_one_constant_the_interrupt_reads(self):
        """Shown == applied: the sentence says "two provinces" from the very
        constant `_check_interrupts` passes to `get_battles_within_range`."""
        import inspect
        from backend.commands import strategic as ST
        assert ST.CANNON_FIRE_RANGE == 2 and "two provinces" in ST.AGGRESSIVE_INTERRUPT_TERMS
        src = inspect.getsource(ST.StrategicOrderProcessor._check_interrupts)
        assert "CANNON_FIRE_RANGE" in src and "get_battles_within_range(marshal.location, 2)" not in src


class TestS14GD2:
    """S14G-D2 — KEEP THE INTERRUPT, SAY IT AT THE ORDER AND AT THE GATE (ruled
    as recommended, October 26, 2026). A morale floor is the one dial offered
    and NOT taken: a 36% corps is still interrupted, and the order says so."""

    def test_a_spent_aggressive_corps_is_still_interrupted_and_was_told(self, _r2_board):
        from backend.commands import strategic as ST
        world, gs, executor, massena, kutuzov = _r2_board
        assert massena.morale < 40
        reply = _r2_order(executor, gs, "Massena", "Massena, support Napoleon", "SUPPORT",
                          "support", "Napoleon")
        assert _R2_WORDS in reply["message"]
        world.record_battle("Hungary", "Kutuzov", "Mack", "defender_won")
        interrupt = ST.StrategicOrderProcessor(executor)._check_interrupts(massena, world)
        assert interrupt["action"] == "redirect"      # the deed is kept, at any morale

    def test_the_end_to_end_turn_change_drops_the_order_as_said(self, _r2_board):
        """The whole sighting through `process_strategic_orders`: the order is
        dropped at the turn change and he is at (or marching to) the guns."""
        from backend.commands import strategic as ST
        world, gs, executor, massena, kutuzov = _r2_board
        world.current_turn = 6
        _r2_order(executor, gs, "Massena", "Massena, hold Bohemia", "HOLD", "hold", "Bohemia")
        massena.strategic_order.issued_turn = 4
        world.record_battle("Hungary", "Kutuzov", "Mack", "defender_won")
        with _r2_quiet():
            rows = ST.StrategicOrderProcessor(executor).process_strategic_orders(world, gs)
        mine = [r for r in rows if r.get("marshal") == "Massena"]
        assert mine and mine[0].get("interrupt") == "cannon_fire"
        assert "Abandoning orders" in mine[0]["message"] or "cannot answer" in mine[0]["message"]

    def test_every_standing_order_type_the_interrupt_reads_is_said(self):
        """The class: the interrupt reads every order type, so every reply
        builder of a standing order carries the clause (PURSUE's upgraded line
        names it in its own words) — a source census of the reply stage."""
        import inspect
        from backend.commands import strategic_executor as se
        src = inspect.getsource(se.StrategicExecutor._strategic_response)
        # MOVE_TO, PURSUE (typed), HOLD, FOLLOW, SUPPORT
        assert src.count("_aggressive_interrupt_clause(") >= 5, src.count("_aggressive_interrupt_clause(")


class TestS14GX13:
    """S14G-X13 (the sweep): the typed PURSUE of an aggressive man is the same
    standing order the interrupt drops, and its reply said nothing — only the
    attack-upgraded PURSUE named "an interrupt". The clause now rides it too."""

    def test_a_typed_pursue_says_it(self, _r2_board):
        world, gs, executor, massena, kutuzov = _r2_board
        # Archduke John stands at Tyrol, one province from Bohemia, in sight
        reply = _r2_order(executor, gs, "Massena", "Massena, pursue Archduke John", "PURSUE",
                          "pursue", "ArchdukeJohn")
        assert reply.get("success") is True, reply.get("message")
        assert "pursues Archduke John" in reply["message"]
        assert _R2_WORDS in reply["message"], reply["message"]

    def test_a_cautious_mans_pursue_says_nothing(self, _r2_board):
        world, gs, executor, massena, kutuzov = _r2_board
        davout = world.get_marshal("Davout")
        davout.location = "Bohemia"
        world.calculate_visibility()
        reply = _r2_order(executor, gs, "Davout", "Davout, pursue Archduke John", "PURSUE",
                          "pursue", "ArchdukeJohn")
        assert reply.get("success") is True, reply.get("message")
        assert "He will drop this order" not in reply["message"]


class TestS14GX14:
    """S14G-X14 (the sweep): the Staff's army quote prints a row per corps
    (`army_quote["corps"]`); an aggressive corps' row carries its terms too —
    the group card's lines are each the very `march_quote`."""

    def test_the_army_rows_and_the_group_quotes_carry_terms(self, _r2_board):
        from backend.commands.order_quotes import group_march_quotes
        world, gs, executor, massena, kutuzov = _r2_board
        quotes = group_march_quotes(world, ["Massena", "Davout"], "Franconia")["quotes"]
        by = {q["marshal"]: q for q in quotes}
        assert _R2_WORDS in by["Massena"]["terms"]
        assert by["Davout"]["terms"] == ""

    def test_the_army_quotes_corps_rows_carry_terms(self, _r2_board, monkeypatch):
        from backend.commands import group_orders as G
        from backend.commands.order_quotes import army_quote
        world, gs, executor, massena, kutuzov = _r2_board
        monkeypatch.setattr(G, "army_order_available", lambda w, nation=None: True)
        monkeypatch.setattr(G, "authority_of", lambda w, nation=None: 90)
        world.actions_remaining = 4
        massena.location = "Rhineland"       # in the Emperor's reach, beside Davout (cautious)
        world.calculate_visibility()
        quote = army_quote(world, "Franconia")
        assert quote["ok"] is True, quote
        rows = {c["marshal"]: c for c in quote["corps"]}
        assert _R2_WORDS in rows["Massena"]["terms"]
        assert rows["Davout"]["terms"] == ""


# ══════════════════════════════════════════════════════════════════════════
# row03
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 — row 3: S14G-3 (October 26, 2026).
#
# "Support Napoleon" lapses or follows according to the supporter's NAME.
#
# The cause as traced (conquest #8, turn 11, action 222): a supporter not
# co-located with his ally walks to him every tick (`_execute_support`, the
# "SUPPORT silently follows" arm); the "lapses of itself" rule the reply promises
# sat only in the CO-LOCATED branch and was evaluated at the supporter's own
# tick. `process_strategic_orders` walks the player's marshals ALPHABETICALLY, so
# Davout and Lannes (sorting before Napoleon) saw him still at home and lapsed
# ("Napoleon is secure"), while Ney (after him) found him already gone, followed
# him ("moves to support Napoleon. 0 regions away") — and, arriving, was only
# evaluated a tick LATER, by which time the Emperor had marched again: Ney
# followed the seven-turn road home while the other two stopped. SUPPORT costs 1
# AP (SR-2e), so players use it as a cheap group move — and the reply said only
# that the order "lapses of itself".
#
# What the fix does: the "ally is safe" reading is one helper
# (`StrategicOrderProcessor._support_ally_is_safe`); the follow branch, once the
# supporter has ARRIVED beside an ally who is out of danger, completes the order
# on the SAME tick ("{ally} is secure") through THE SEAM
# `StrategicOrderProcessor._support_lapses_on_arrival` — a plain support lapses
# on arrival for every supporter alike. A named duration and a FOLLOW keep their
# terms. The reply (and the quote's `terms`, through one helper,
# `strategic.support_terms_clause`) says what it does: he goes to the ally now,
# stays only while the ally is in danger, the order lapses of itself, and
# "follow" keeps him at the ally's side. Kept: the follow itself, the lapse rule,
# the co-located arm.
#
# The AI never walks `_execute_support`: `process_strategic_orders` reads only the
# player's marshals and no backend/ai module builds a strategic order.

_R3_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")


def _r3_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r3_boot():
    from backend.models.world_state import WorldState
    with _r3_quiet():
        return WorldState.from_scenario(str(_R3_SCENARIO))


def _r3_support(world, name, ally="Napoleon", **kw):
    from backend.models.marshal import StrategicOrder
    m = world.get_marshal(name)
    m.strategic_order = StrategicOrder(
        command_type="SUPPORT", target=ally, target_type="marshal",
        started_turn=world.current_turn - 1, original_command=f"{name}, support {ally}",
        issued_turn=world.current_turn - 1, arrived_turn=world.current_turn - 1, **kw)
    return m


@pytest.fixture
def _r3_board(_r3_boot):
    """The Emperor at Paris on a march for Lyonnais by Berry and Limousin; Davout
    and Lannes (sorting before him) and Ney (after) all at Paris on a plain
    "support Napoleon". Paris, Berry, Limousin and their neighbours are quiet
    French ground — the ally is safe wherever he stands."""
    from backend.commands.executor import CommandExecutor
    from backend.models.marshal import StrategicOrder
    from backend.models.world_state import WorldState
    world = WorldState.from_dict(json.loads(json.dumps(_r3_boot.to_dict(), default=str)))
    napoleon = world.get_marshal("Napoleon")
    napoleon.location = "Paris"
    napoleon.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target="Lyonnais", target_type="region",
        started_turn=world.current_turn - 1, original_command="Napoleon, march to Lyonnais",
        path=["Berry", "Limousin", "Lyonnais"], issued_turn=world.current_turn - 1)
    for name in ("Davout", "Lannes", "Ney"):
        world.get_marshal(name).location = "Paris"
        _r3_support(world, name)
    world.calculate_visibility()
    return world, {"world": world}, CommandExecutor()


def _r3_tick(executor, world, gs):
    from backend.commands.strategic import StrategicOrderProcessor
    with _r3_quiet():
        return StrategicOrderProcessor(executor).process_strategic_orders(world, gs)


def _r3_where(world):
    return {n: (world.get_marshal(n).location,
                getattr(world.get_marshal(n).strategic_order, "command_type", None))
            for n in ("Davout", "Lannes", "Ney", "Napoleon")}


class TestS14G3:
    """The sighting: three supporters named before and after the ally, the ally
    marching away. Before: Davout and Lannes lapsed and Ney followed him tick
    after tick; after: all three lapse alike and none follows him across the
    country."""

    def test_the_alphabetical_split_is_reproduced_with_the_seam_down(self, _r3_board):
        """Today's behaviour (the seam patched to None): the sighting itself."""
        from backend.commands.strategic import StrategicOrderProcessor
        world, gs, executor = _r3_board
        original = StrategicOrderProcessor._support_lapses_on_arrival
        StrategicOrderProcessor._support_lapses_on_arrival = lambda self, *a, **k: None
        try:
            _r3_tick(executor, world, gs)
            first = _r3_where(world)
            _r3_tick(executor, world, gs)
            second = _r3_where(world)
        finally:
            StrategicOrderProcessor._support_lapses_on_arrival = original
        # Davout and Lannes sorted before the Emperor: they lapsed at Paris ...
        assert first["Davout"] == ("Paris", None) and first["Lannes"] == ("Paris", None)
        # ... Ney sorted after him: he followed to Berry and still holds the order
        assert first["Ney"] == ("Berry", "SUPPORT") and first["Napoleon"][0] == "Berry"
        # and he follows him again the next tick, order still standing
        assert second["Ney"] == ("Limousin", "SUPPORT") and second["Napoleon"][0] == "Limousin"

    def test_all_three_lapse_alike_whatever_their_names(self, _r3_board):
        world, gs, executor = _r3_board
        rows = _r3_tick(executor, world, gs)
        after = _r3_where(world)
        for name in ("Davout", "Lannes", "Ney"):
            assert after[name][1] is None, (name, after)       # the order is over for every one
        by = {r["marshal"]: r for r in rows}
        for name in ("Davout", "Lannes", "Ney"):
            assert by[name]["order_status"] == "completed", by[name]
            assert "Napoleon is secure" in by[name]["reason"]
        # Ney stepped to the Emperor's new province, arrived, and the order was over
        assert after["Ney"][0] == "Berry" == after["Napoleon"][0]
        assert after["Davout"][0] == after["Lannes"][0] == "Paris"

    def test_none_follows_him_across_the_country(self, _r3_board):
        """Two more ticks: the Emperor marches on to Limousin and Lyonnais; nobody
        walks after him (Ney used to follow the whole road home)."""
        world, gs, executor = _r3_board
        _r3_tick(executor, world, gs)
        _r3_tick(executor, world, gs)
        _r3_tick(executor, world, gs)
        after = _r3_where(world)
        assert after["Napoleon"][0] == "Lyonnais"
        assert after["Ney"] == ("Berry", None)
        assert after["Davout"] == ("Paris", None) and after["Lannes"] == ("Paris", None)

    def test_the_arrival_row_says_he_moved_then_the_order_lapsed(self, _r3_board):
        world, gs, executor = _r3_board
        rows = _r3_tick(executor, world, gs)
        ney = next(r for r in rows if r["marshal"] == "Ney")
        assert ney["message"].startswith("Ney moves to support Napoleon. ")
        assert ney["regions_moved"] == ["Berry"]

    def test_a_far_supporter_follows_until_he_arrives_then_the_order_lapses(self, _r3_board):
        """The follow itself is kept: Ney two provinces from a still Emperor
        walks to him and the order lapses the very tick he arrives (it used to
        read "0 regions away" and stand a tick more)."""
        world, gs, executor = _r3_board
        napoleon = world.get_marshal("Napoleon")
        napoleon.strategic_order = None
        napoleon.location = "Berry"
        for name in ("Davout", "Lannes"):
            world.get_marshal(name).strategic_order = None
        ney = world.get_marshal("Ney")
        ney.location = "Paris"           # beside Berry: one march
        rows = _r3_tick(executor, world, gs)
        assert ney.location == "Berry" and ney.strategic_order is None
        row = next(r for r in rows if r["marshal"] == "Ney")
        assert row["order_status"] == "completed"
        assert "0 regions away" not in row["message"]

    def test_an_ally_in_danger_keeps_the_order_standing(self, _r3_board):
        """The lapse is "once out of danger": a visible enemy beside the ally
        and the support stands (the order is for exactly that hour)."""
        world, gs, executor = _r3_board
        napoleon = world.get_marshal("Napoleon")
        napoleon.strategic_order = None
        napoleon.location = "Berry"
        for name in ("Davout", "Lannes"):
            world.get_marshal(name).strategic_order = None
        mack = world.get_marshal("Mack")
        mack.location = "Maine"          # French soil beside Berry: in sight
        world.calculate_visibility()
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        rows = _r3_tick(executor, world, gs)
        assert ney.location == "Berry"
        assert ney.strategic_order is not None and ney.strategic_order.command_type == "SUPPORT"
        row = next(r for r in rows if r["marshal"] == "Ney")
        assert row["order_status"] == "continues"

    def test_a_named_duration_is_honoured(self, _r3_board):
        """"Support for N turns": the term is the player's, the arrival does not
        end it."""
        from backend.models.marshal import StrategicCondition
        world, gs, executor = _r3_board
        napoleon = world.get_marshal("Napoleon")
        napoleon.strategic_order = None
        napoleon.location = "Berry"
        for name in ("Davout", "Lannes"):
            world.get_marshal(name).strategic_order = None
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        ney.strategic_order.condition = StrategicCondition(max_turns=5)
        _r3_tick(executor, world, gs)
        assert ney.location == "Berry"
        assert ney.strategic_order is not None

    def test_a_follow_never_lapses_on_arrival(self, _r3_board):
        """AO: the FOLLOW is the order that stays at his side."""
        world, gs, executor = _r3_board
        napoleon = world.get_marshal("Napoleon")
        napoleon.strategic_order = None
        napoleon.location = "Berry"
        for name in ("Davout", "Lannes"):
            world.get_marshal(name).strategic_order = None
        ney = _r3_support(world, "Ney", standing_follow=True)
        ney.location = "Paris"
        _r3_tick(executor, world, gs)
        assert ney.location == "Berry"
        assert ney.strategic_order is not None and ney.strategic_order.standing_follow is True

    def test_the_co_located_lapse_is_unchanged(self, _r3_board):
        """The arm that always worked: beside a safe ally at the start of the
        tick, the order lapses in place."""
        world, gs, executor = _r3_board
        napoleon = world.get_marshal("Napoleon")
        napoleon.strategic_order = None          # he stays at Paris
        rows = _r3_tick(executor, world, gs)
        for name in ("Davout", "Lannes", "Ney"):
            assert world.get_marshal(name).strategic_order is None
            assert world.get_marshal(name).location == "Paris"
        assert all(r["order_status"] == "completed" for r in rows
                   if r["marshal"] in ("Davout", "Lannes", "Ney"))

    def test_the_safe_reading_is_one_helper_both_arms_read(self):
        import inspect
        from backend.commands.strategic import StrategicOrderProcessor as P
        body = inspect.getsource(P._execute_support)
        assert "self._support_ally_is_safe(" in body
        assert "get_visible_enemies_in_region" not in body
        assert "self._support_ally_is_safe(" in inspect.getsource(P._support_lapses_on_arrival)

    def test_the_ai_never_walks_support(self):
        """The seam is the player's: `process_strategic_orders` reads only the
        player's marshals, and no backend/ai module builds a strategic order."""
        import inspect
        from backend.commands.strategic import StrategicOrderProcessor as P
        src = inspect.getsource(P.process_strategic_orders)
        assert "m.nation == world.player_nation" in src
        root = Path(__file__).resolve().parents[1] / "backend" / "ai"
        for path in root.glob("*.py"):
            assert "StrategicOrder(" not in path.read_text(encoding="utf-8"), path.name


class TestS14G3Reply:
    """The SUPPORT reply says what it does (and the quote, through the one helper)."""

    _SENTENCE = ("He goes to Napoleon now and stays only while Napoleon is in danger — the "
                 "order lapses of itself once Napoleon is out of danger; 'Ney, follow "
                 "Napoleon' keeps him at Napoleon's side. Name a duration to hold him to it.")

    def _order(self, executor, gs, line, **extra):
        with _r3_quiet():
            return executor.execute({
                "command": {"raw_input": line, "marshal": "Ney", "action": "support",
                            "target": "Napoleon"},
                "is_strategic": True, "strategic_type": "SUPPORT", **extra}, gs)

    def test_the_reply_says_what_the_order_does(self, _r3_board):
        world, gs, executor = _r3_board
        world.get_marshal("Ney").strategic_order = None
        reply = self._order(executor, gs, "Ney, support Napoleon")
        assert reply["success"] is True, reply["message"]
        assert self._SENTENCE in reply["message"], reply["message"]
        assert "when Napoleon leads a battle within reach, he will march to the guns" in reply["message"]

    def test_the_quote_says_it_in_the_same_words(self, _r3_board):
        from backend.commands.order_quotes import support_quote
        world, gs, executor = _r3_board
        ney = world.get_marshal("Ney")
        ney.strategic_order = None
        ney.location = "Paris"
        terms = support_quote(world, ney, world.get_marshal("Napoleon"))["terms"]
        assert self._SENTENCE in terms
        reply = self._order(executor, gs, "Ney, support Napoleon")
        # shown == applied: the quote's `terms` is a verbatim stretch of the reply
        # (Ney is aggressive, so it carries the interrupt clause after the support's)
        assert terms in reply["message"], (terms, reply["message"])
        assert terms.endswith("in a war of ours.")

    def test_a_timed_support_says_the_term_is_held(self, _r3_board):
        world, gs, executor = _r3_board
        world.get_marshal("Ney").strategic_order = None
        reply = self._order(executor, gs, "Ney, support Napoleon for 3 turns",
                            strategic_condition={"max_turns": 3})
        assert reply["success"] is True, reply["message"]
        assert "for the term you named" in reply["message"]
        assert "Name a duration" not in reply["message"]

    def test_the_old_sentence_is_gone(self, _r3_board):
        world, gs, executor = _r3_board
        world.get_marshal("Ney").strategic_order = None
        reply = self._order(executor, gs, "Ney, support Napoleon")
        assert "The order lapses of itself once" not in reply["message"]

    def test_a_follow_quote_carries_no_support_clause(self, _r3_board):
        from backend.commands.order_quotes import follow_quote
        world, gs, executor = _r3_board
        ney = world.get_marshal("Ney")
        ney.strategic_order = None
        ney.location = "Paris"
        terms = follow_quote(world, ney, world.get_marshal("Napoleon"))["terms"]
        assert "lapses of itself" not in terms


class TestS14GX15:
    """S14G-X15 (the sweep): the order's other roads through `_execute_support`
    — the "adjust course to follow" answer (`_respond_ally_moving`) and the
    interrupt answers' movement step (`_execute_movement_step`) — reach the SAME
    seam, so a supporter who arrives by an answer lapses the same way."""

    def test_the_movement_step_reaches_the_arrival_lapse(self, _r3_board):
        from backend.commands.strategic import StrategicOrderProcessor
        world, gs, executor = _r3_board
        napoleon = world.get_marshal("Napoleon")
        napoleon.strategic_order = None
        napoleon.location = "Berry"
        for name in ("Davout", "Lannes"):
            world.get_marshal(name).strategic_order = None
        ney = world.get_marshal("Ney")
        ney.location = "Paris"
        with _r3_quiet():
            result = StrategicOrderProcessor(executor)._execute_movement_step(ney, world, gs)
        assert result["order_status"] == "completed" and result["success"] is True
        assert ney.strategic_order is None and ney.location == "Berry"


# ══════════════════════════════════════════════════════════════════════════
# row04
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 — row 4: S14G-4 (October 26, 2026).
#
# A march order for the province the corps already stands in is accepted, spends
# an action and replaces the standing order — and the dispatch's "HALTED …
# awaiting your word" stays on the page after "Continue as Ordered" has answered it.
#
# The row as filed ("Continue as Ordered halted Napoleon's march") was a
# misreading: Napoleon DID arrive (sea #2, turn 3: action 33 replies "Napoleon
# arrives at Flanders"). The dispatch was built after the advance raised the
# cannon-fire interrupt, so it read "HALTED at Orleanais — awaiting your word";
# S14E-30 deliberately shows the dispatch BEFORE the question, and
# `continue_order` then stepped him on — nothing retracted the line. The real
# defect is what followed: at action 38 the player typed "Napoleon, march to
# Flanders" (he already stood there) and it was ACCEPTED, charged 1 AP and
# "arrived" on the next tick. `_strategic_path` skipped the road stage for a
# destination he stands in but nothing refused it; the order was created, replaced
# any standing order silently, and the plain `move` refuses the same order ("is
# already in").
#
# What the fix does: (1) `_strategic_path` refuses a MOVE_TO to the corps' own
# province FREE, before any order is created or replaced, in one shared sentence
# (`strategic.own_province_march_refusal`); HOLD on the own province stays legal
# ("hold here"), PURSUE / SUPPORT are untouched, and a march that carries a verb
# for its arrival keeps the verb's business. (2) The quote (`order_quotes`)
# marks the own province not-a-destination in the same words, `march_reach` never
# lists it (even when a standing order still names it), `march_roads` offers it no
# road. (3) The ONE answer seam (`StrategicOrderProcessor.handle_response`)
# marks the stored dispatch line answered (`dispatch.mark_interrupt_answered`):
# "HALTED at Orleanais — answered: continued." Kept: S14E-30 (the dispatch shows
# before the question); `GET /dispatch` still re-derives the roster live.

_R4_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")
_R4_REPO = pathlib.Path(__file__).resolve().parent.parent


def _r4_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r4_boot():
    from backend.models.world_state import WorldState
    with _r4_quiet():
        return WorldState.from_scenario(str(_R4_SCENARIO))


@pytest.fixture
def _r4_board(_r4_boot):
    from backend.commands.executor import CommandExecutor
    from backend.models.world_state import WorldState
    world = WorldState.from_dict(json.loads(json.dumps(_r4_boot.to_dict(), default=str)))
    return world, {"world": world}, CommandExecutor()


@pytest.fixture
def _r4_shipped(monkeypatch):
    """The shipped 1805 world at all three seams with a mock parser (the SR-2e
    idiom) — the sighting at the real `POST /command`."""
    from fastapi.testclient import TestClient
    import backend.main as M
    from backend.commands.parser import CommandParser
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    return TestClient(M.app), M.world


def _r4_post(client, command):
    return client.post("/command", json={"command": command}).json()


def _r4_march(executor, game_state, marshal, target, **extra):
    with _r4_quiet():
        return executor.execute({
            "command": {"raw_input": f"{marshal}, march to {target}", "marshal": marshal,
                        "action": "move", "target": target},
            "is_strategic": True, "strategic_type": "MOVE_TO", **extra}, game_state)


class TestS14G4:
    """The sighting on the shipped board: "Napoleon, march to <the province he
    stands in>". Before: accepted, 1 AP ("[3/4 actions remaining]"), a MOVE_TO
    with an empty path created and any standing order replaced; after: refused
    free, nothing created, nothing replaced."""

    def test_the_sighting_at_the_wire(self, _r4_shipped):
        client, world = _r4_shipped
        napoleon = world.get_marshal("Napoleon")
        here = napoleon.location
        ap = int(world.actions_remaining)
        data = _r4_post(client, f"Napoleon, march to {here}")
        assert data.get("success") is False, data.get("message")
        assert data["message"].startswith(f"Napoleon already stands at {here} — nothing spent.")
        assert int(world.actions_remaining) == ap
        assert napoleon.strategic_order is None

    def test_a_standing_order_is_not_replaced(self, _r4_board):
        world, gs, executor = _r4_board
        napoleon = world.get_marshal("Napoleon")
        first = _r4_march(executor, gs, "Napoleon", "Swabia")
        assert first["success"] is True, first["message"]
        standing = napoleon.strategic_order
        assert standing is not None and standing.target == "Swabia"
        ap = int(world.actions_remaining)
        here = napoleon.location
        reply = _r4_march(executor, gs, "Napoleon", here)
        assert reply["success"] is False
        assert reply["message"] == f"Napoleon already stands at {here} — nothing spent."
        assert reply["variable_action_cost"] == 0
        assert napoleon.strategic_order is standing        # the very object, untouched
        assert int(world.actions_remaining) == ap

    def test_it_is_the_one_sentence_the_quote_says(self, _r4_board):
        from backend.commands.order_quotes import march_quote
        from backend.commands.strategic import own_province_march_refusal
        world, gs, executor = _r4_board
        napoleon = world.get_marshal("Napoleon")
        here = napoleon.location
        sentence = own_province_march_refusal(napoleon, here)
        assert sentence == f"Napoleon already stands at {here} — nothing spent."
        assert _r4_march(executor, gs, "Napoleon", here)["message"] == sentence
        q = march_quote(world, napoleon, here)
        assert q["ok"] is False and q["refusal"] == sentence and q["already"] is False
        assert q["terms"] == "" and q["road"] == []

    def test_a_leftover_order_to_the_own_province_still_quotes_not_a_destination(self, _r4_board):
        """The quote said "ok" (the identical-order arm: `already`) once an
        order to the own province existed — a save from before the fix; and the
        map's ETA tint listed the province."""
        from backend.commands.order_quotes import march_quote, march_reach
        from backend.commands.strategic import march_roads
        from backend.models.marshal import StrategicOrder
        world, gs, executor = _r4_board
        napoleon = world.get_marshal("Napoleon")
        here = napoleon.location
        napoleon.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target=here, target_type="region",
            started_turn=world.current_turn, issued_turn=world.current_turn,
            original_command=f"Napoleon, march to {here}", path=[])
        q = march_quote(world, napoleon, here)
        assert q["ok"] is False and q["already"] is False
        assert "already stands at" in q["refusal"]
        reach = march_reach(world, napoleon)
        assert here not in reach["reach"]
        road, refusal, _kind = march_roads(world, napoleon)[here]
        assert road is None and refusal is not None           # no road is offered to it

    def test_every_other_province_is_still_offered(self, _r4_board):
        from backend.commands.order_quotes import march_quote, march_reach
        world, gs, executor = _r4_board
        napoleon = world.get_marshal("Napoleon")
        reach = march_reach(world, napoleon)["reach"]
        assert reach and napoleon.location not in reach
        dest = next(iter(reach))
        assert march_quote(world, napoleon, dest)["ok"] is True

    def test_hold_here_stays_legal(self, _r4_board):
        """HOLD on the own province is "hold here" — the same destination, a
        different order."""
        world, gs, executor = _r4_board
        napoleon = world.get_marshal("Napoleon")
        with _r4_quiet():
            reply = executor.execute({
                "command": {"raw_input": f"Napoleon, hold {napoleon.location}",
                            "marshal": "Napoleon", "action": "hold",
                            "target": napoleon.location},
                "is_strategic": True, "strategic_type": "HOLD"}, gs)
        assert reply["success"] is True, reply["message"]
        assert napoleon.strategic_order is not None and napoleon.strategic_order.command_type == "HOLD"

    def test_a_support_of_an_ally_in_the_same_province_is_legitimate(self, _r4_board):
        world, gs, executor = _r4_board
        assert world.get_marshal("Ney").location == world.get_marshal("Davout").location
        with _r4_quiet():
            reply = executor.execute({
                "command": {"raw_input": "Ney, support Davout", "marshal": "Ney",
                            "action": "support", "target": "Davout"},
                "is_strategic": True, "strategic_type": "SUPPORT"}, gs)
        assert reply["success"] is True, reply["message"]

    def test_a_march_that_carries_a_verb_for_its_arrival_keeps_the_verbs_business(self, _r4_board):
        """"march to X then fortify" at X is not the empty march the row
        refuses: the verb is the order's business, and the quote agrees."""
        from backend.commands.order_quotes import _standing_quote, _blank
        world, gs, executor = _r4_board
        ney = world.get_marshal("Ney")
        here = ney.location
        reply = _r4_march(executor, gs, "Ney", here, arrival_verb="fortify")
        assert "already stands at" not in reply["message"]
        q = _blank("march", ney, here, f"Ney, march to {here}")
        q = _standing_quote(world, ney, here, "MOVE_TO", here, "march", q, None,
                            arrival={"attack_on_arrival": False, "arrival_verb": "fortify"})
        assert "already stands at" not in q["refusal"]

    def test_the_plain_move_says_the_same_fact(self, _r4_board):
        """The belt the strategic road now matches: `move` to the own province
        was always refused ("is already in") — the march is now too."""
        world, gs, executor = _r4_board
        with _r4_quiet():
            reply = executor.execute({"command": {
                "raw_input": "Napoleon, move to Lorraine", "marshal": "Napoleon",
                "action": "move", "target": "Lorraine"}}, gs)
        assert reply["success"] is False and "already in Lorraine" in reply["message"]

    def test_the_group_card_line_is_unchanged(self, _r4_board):
        """A Ctrl-click group's member standing on the destination is named
        ("already at X"), never quoted — a different surface already free and
        honest; kept (test_cc5_the_war_table pins it)."""
        from backend.commands.order_quotes import group_march_quotes
        world, gs, executor = _r4_board
        dest = world.get_marshal("Ney").location
        q = group_march_quotes(world, ["Ney"], dest)["quotes"][0]
        assert q["ok"] is False and q["refusal"] == f"already at {dest}" and q["here"] is True


# ───────────────────────────── the dispatch's HALTED line ──────────────────────────────

def _r4_halt_napoleon(world, gs, executor):
    """Napoleon on a march with a lawful battle one province off: the turn
    change raises the cannon-fire question (a sovereign asks)."""
    from backend.commands.strategic import StrategicOrderProcessor
    from backend.models.marshal import StrategicOrder
    napoleon = world.get_marshal("Napoleon")
    napoleon.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target="Franconia", target_type="region",
        started_turn=world.current_turn - 1, issued_turn=world.current_turn - 1,
        original_command="Napoleon, march to Franconia", path=["Franconia"])
    world.record_battle("Swabia", "Mack", "Deroy", "defender_won")
    with _r4_quiet():
        rows = StrategicOrderProcessor(executor).process_strategic_orders(world, gs)
    assert napoleon.pending_interrupt, rows
    return napoleon


def _r4_store_dispatch(world):
    from backend.game_logic.dispatch import _build_marshal_status
    world.last_morning_dispatch = {"marshals": _build_marshal_status(world, "France")}
    return next(r for r in world.last_morning_dispatch["marshals"] if r["name"] == "Napoleon")


class TestS14G4Dispatch:
    """The stored dispatch's HALTED line, marked answered at the ONE answer seam."""

    def test_the_halted_line_is_there_before_the_answer(self, _r4_board):
        """S14E-30 kept: the dispatch shows BEFORE the question is answered."""
        world, gs, executor = _r4_board
        napoleon = _r4_halt_napoleon(world, gs, executor)
        row = _r4_store_dispatch(world)
        assert row["status"] == "awaiting_decision"
        assert row["status_note"].startswith("HALTED at ")
        assert "awaiting your word" in row["status_note"].lower()

    def test_continue_as_ordered_marks_the_line_answered(self, _r4_board):
        from backend.commands.strategic import StrategicOrderProcessor
        world, gs, executor = _r4_board
        napoleon = _r4_halt_napoleon(world, gs, executor)
        where = _r4_store_dispatch(world)["status_note"].split(" — ")[0]   # "HALTED at Lorraine"
        with _r4_quiet():
            result = StrategicOrderProcessor(executor).handle_response(
                "Napoleon", "cannon_fire", "continue_order", world, gs)
        assert result["success"] is True, result
        row = next(r for r in world.last_morning_dispatch["marshals"] if r["name"] == "Napoleon")
        assert row["status_note"] == f"{where} — answered: continued."
        assert row["status"] == "answered"

    @pytest.mark.parametrize("choice,word", [
        ("continue_order", "continued"), ("hold_position", "held"), ("investigate", "went to the guns"),
    ])
    def test_every_answer_arm_marks_its_own_word(self, _r4_board, choice, word):
        from backend.commands.strategic import StrategicOrderProcessor
        world, gs, executor = _r4_board
        _r4_halt_napoleon(world, gs, executor)
        _r4_store_dispatch(world)
        with _r4_quiet():
            result = StrategicOrderProcessor(executor).handle_response(
                "Napoleon", "cannon_fire", choice, world, gs)
        row = next(r for r in world.last_morning_dispatch["marshals"] if r["name"] == "Napoleon")
        if result.get("success"):
            assert row["status_note"].endswith(f"— answered: {word}."), (choice, row)
        else:   # an answer the executor refused marks nothing
            assert row["status"] == "awaiting_decision"

    def test_a_refused_answer_marks_nothing(self, _r4_board):
        from backend.commands.strategic import StrategicOrderProcessor
        world, gs, executor = _r4_board
        _r4_halt_napoleon(world, gs, executor)
        before = dict(_r4_store_dispatch(world))
        with _r4_quiet():
            result = StrategicOrderProcessor(executor).handle_response(
                "Napoleon", "cannon_fire", "not_an_option", world, gs)
        assert result["success"] is False
        row = next(r for r in world.last_morning_dispatch["marshals"] if r["name"] == "Napoleon")
        assert row == before

    def test_the_answer_endpoint_marks_it_at_the_wire(self, _r4_shipped):
        client, world = _r4_shipped
        import backend.main as M
        napoleon = _r4_halt_napoleon(world, M.game_state, M.executor)
        row = _r4_store_dispatch(world)
        assert row["status_note"].startswith("HALTED at ")
        data = client.post("/strategic_response", json={
            "marshal_name": "Napoleon", "response_type": "cannon_fire",
            "choice": "continue_order"}).json()
        assert data.get("success") is True, data.get("message")
        row = next(r for r in world.last_morning_dispatch["marshals"] if r["name"] == "Napoleon")
        assert row["status_note"].endswith("— answered: continued.")

    def test_the_live_reread_is_unchanged_and_says_what_he_does_now(self, _r4_shipped):
        """`GET /dispatch` re-derives the roster from the board (S14E-30): after
        the answer the corps is no longer HALTED there."""
        client, world = _r4_shipped
        import backend.main as M
        _r4_halt_napoleon(world, M.game_state, M.executor)
        _r4_store_dispatch(world)
        client.post("/strategic_response", json={
            "marshal_name": "Napoleon", "response_type": "cannon_fire",
            "choice": "continue_order"})
        live = client.get("/dispatch").json()
        rows = {r["name"]: r for r in (live.get("dispatch") or live).get("marshals", [])}
        assert "Napoleon" in rows
        assert "HALTED" not in str(rows["Napoleon"].get("status_note", ""))
        assert rows["Napoleon"]["status"] == "en_route"

    def test_the_arcs_note_is_not_overwritten(self, _r4_board):
        """A row whose note is the marshal's arc line (it outranks the halt note)
        keeps its words and takes the status alone."""
        from backend.game_logic.dispatch import mark_interrupt_answered
        world, gs, executor = _r4_board
        world.last_morning_dispatch = {"marshals": [{
            "name": "Ney", "status": "awaiting_decision",
            "status_note": "Beaten at Tyrol three turns running."}]}
        assert mark_interrupt_answered(world, "Ney", "continue_order") is True
        row = world.last_morning_dispatch["marshals"][0]
        assert row["status_note"] == "Beaten at Tyrol three turns running."
        assert row["status"] == "answered"

    def test_only_a_halted_row_is_marked(self, _r4_board):
        from backend.game_logic.dispatch import mark_interrupt_answered
        world, gs, executor = _r4_board
        world.last_morning_dispatch = {}
        assert mark_interrupt_answered(world, "Ney", "continue_order") is False   # no dispatch
        world.last_morning_dispatch = {"marshals": [
            {"name": "Ney", "status": "en_route", "status_note": "Moving to Swabia."}]}
        assert mark_interrupt_answered(world, "Ney", "continue_order") is False
        assert mark_interrupt_answered(world, "Nobody", "continue_order") is False
        assert world.last_morning_dispatch["marshals"][0]["status_note"] == "Moving to Swabia."

    def test_an_encircled_or_muster_row_reads_its_own_head(self, _r4_board):
        from backend.game_logic.dispatch import mark_interrupt_answered
        world, gs, executor = _r4_board
        world.last_morning_dispatch = {"marshals": [
            {"name": "Ney", "status": "awaiting_decision",
             "status_note": "ENCIRCLED at Swabia by Mack — awaiting your word."}]}
        assert mark_interrupt_answered(world, "Ney", "fight_to_the_last")
        assert (world.last_morning_dispatch["marshals"][0]["status_note"]
                == "ENCIRCLED at Swabia by Mack — answered: fought to the last.")

    def test_there_is_one_answer_seam(self):
        """Both of main.py's roads answer through `handle_response`, so one
        wrap marks every answer; a third road would show here."""
        src = (_R4_REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert src.count("strategic_exec.handle_response(") == 2
        import inspect
        from backend.commands.strategic import StrategicOrderProcessor as P
        assert "mark_interrupt_answered" in inspect.getsource(P.handle_response)
        assert "_handle_response_body" in inspect.getsource(P.handle_response)


class TestS14GX16:
    """S14G-X16 (the sweep): the identical-order arm of `_standing_quote` and
    the `already` arm of `march_reach` both said "ok" for the own province when a
    standing order still named it — the quote and the tint disagreed with the
    refusal the typed order now gives. Pinned above
    (`test_a_leftover_order_to_the_own_province_still_quotes_not_a_destination`);
    this class pins the class: the quote's own-province arm sits BEFORE the
    identical-order arm, for MOVE_TO only."""

    def test_the_arm_order_and_scope(self, _r4_board):
        import inspect
        from backend.commands import order_quotes as OQ
        src = inspect.getsource(OQ._standing_quote)
        assert src.index("own_province_march_refusal") < src.index("already=True")
        world, gs, executor = _r4_board
        ney = world.get_marshal("Ney")
        davout = world.get_marshal("Davout")
        # a SUPPORT of an ally in the own province is quoted ok (road: none)
        q = OQ.support_quote(world, ney, davout)
        assert q["ok"] is True and q["road"] == []


# ══════════════════════════════════════════════════════════════════════════
# row05
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 - row S14G-5 (DD-B's third measure, October 26, 2026).
#
# THE ROW. A marshal's audience card names a quarry that has since gone
# ("Send him against Mack into Munich") and sends him, alone, at whoever is
# weakest in reach - announced only after the actions and the battle.
#
# CAUSE AS TRACED (`docs/BUG_FIXES.md` S14G-5, commit a47bc116): the card's
# `command` arm baked its detail at build time, in the previous turn's pass;
# `refresh_petition_affordability` re-derived only `enabled` and
# `unavailable_reason`; on the click `_apply_command_choice` re-derived the
# quarry through `find_autonomous_attack_target` (the weakest enemy in or
# adjacent to his province) and ran PURSUE with `objection_response="proceed"`
# - no comparison with the man the card named, no odds gate, the switch told
# only after the 2 AP and the battle ("Archduke Charles, then."). The dispatch
# warning ("Murat is eyeing Mack's position at Munich") was re-targeted the
# same way, silently, at fire time.
#
# SIGHTING: sea road #4, turn 4, action 63 (`docs/audits/dd_b/sea_2026_10_25/
# frames/0063.jpg`): Ney beat Mack (action 57), the tooltip at action 62 still
# named Mack, the click sent Ney alone at Archduke Charles (31,690 against
# 18,920) - 5,379 men lost to Charles's 2,632 on a card that never named him.
#
# WHAT THE FIX DOES (all in `backend/game_logic/jealousy.py`, player-only - the
# shared `find_autonomous_attack_target` and the odds gate are untouched, so no
# series seam is needed):
#
#   * the command option NAMES its quarry (`quarry`, `quarry_region`);
#   * the delivery seam re-derives the arm from the live board
#     (`_with_live_details` -> `_command_option(card=...)`), PURE - the stored
#     petition keeps the builder's verdict - and a changed quarry is SAID on the
#     card, with the figures and "asks once more";
#   * the click (`_apply_command_choice` -> `_command_card_ask`) compares the
#     live man with the card's: unchanged = the order runs as it always did;
#     changed = NOTHING is spent and he is ASKED, in the petition's own
#     re-delivery (`success: False`, `requires_input: True`, the delivered card
#     attached), with Berthier's band; when the odds hold him
#     (`glory_attack_held_by_the_odds`, the predicate an unasked glory attack
#     obeys on both boards) the order is REFUSED, free, and the card stands. The
#     ask re-stamps the stored card to the live man, so the second click is the
#     "yes";
#   * the dispatch warning says the target may change, records WHOM it named in
#     the already-serialized `jealousy_history["__warned__"]` (zero new fields),
#     and the fire-time lines name the man actually struck when he is not the
#     one warned of.
#
# SWEEP (the other arms whose detail is baked at build time and re-read at the
# click): confrontation `command` (this row, re-derives now); `acknowledge`
# (S14G-X18 - his men and the turns left, re-derived now); `promise` /
# `Reassign` and `rebuke` (constants and a rung that moves only on the pair's own
# fire, which re-queues the card - nothing to re-derive); rivalry `mediate` /
# `force_reconciliation` (S14G-X19 - banded on the Emperor's authority, which
# the click reads LIVE; re-derived now); the Fontainebleau `concede` arm (GE-3
# re-prices at delivery already); `let_be`, `reprimand`, `accept_breach`,
# `separate`, shadow and war-weary arms (personality / constants only).

_R5_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")


def _r5_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r5_boot():
    from backend.models.world_state import WorldState
    with _r5_quiet():
        return WorldState.from_scenario(str(_R5_SCENARIO))


@pytest.fixture
def _r5_board(_r5_boot):
    """The shipped 1805 board. Murat (aggressive, 22,000, Franche-Comte) is
    envious of Ney; Mack (52,000) stands at Swabia, adjacent - the quarry a
    card built now names. `_r5_flee` then makes the sighting: Mack beaten and
    gone to Tyrol, Archduke Charles arrived at Munich."""
    from backend.commands.executor import CommandExecutor
    from backend.models.world_state import WorldState
    world = WorldState.from_dict(json.loads(json.dumps(_r5_boot.to_dict(), default=str)))
    murat = world.get_marshal("Murat")
    assert murat.personality == "aggressive" and murat.location == "Franche-Comte"
    murat.jealous_of = "Ney"
    murat.jealousy_turns_remaining = 3
    world.actions_remaining = 4
    world.calculate_visibility()
    random.seed(1805)         # the order's battle rolls dice; the pins read its text
    with _r5_quiet():
        executor = CommandExecutor()
    return SimpleNamespace(world=world, executor=executor, murat=murat,
                           ney=world.get_marshal("Ney"),
                           mack=world.get_marshal("Mack"),
                           charles=world.get_marshal("ArchdukeCharles"))


def _r5_card(b):
    """Queue Murat's confrontation and return the STORED petition."""
    from backend.game_logic import jealousy as J
    with _r5_quiet():
        status = J.queue_confrontation_petition(b.world, b.murat, b.ney, 1)
    assert status == J.PETITION_QUEUED
    return b.world.pending_marshal_petition


def _r5_opt(petition, oid="command"):
    return next(o for o in petition["options"] if o["id"] == oid)


def _r5_flee(b, charles_strength=31690, charles_at="Munich"):
    """The sighting: Mack beaten and gone to Tyrol, Archduke Charles
    arrived where the order would now fall."""
    b.mack.location = "Tyrol"
    b.charles.location = charles_at
    b.charles.strength = charles_strength
    b.world.calculate_visibility()


def _r5_full(b, region="Munich"):
    """Scouted: the player reads the province at FULL visibility."""
    from backend.models.intel import FULL
    b.world.intel[region].visibility = FULL


def _r5_answer(b, choice="command"):
    from backend.game_logic import jealousy as J
    with _r5_quiet():
        return J.handle_petition_response(
            b.world, choice, executor=b.executor,
            game_state={"world": b.world, "executor": b.executor})


def _r5_delivered(b):
    from backend.game_logic import jealousy as J
    return J.refresh_petition_affordability(b.world.pending_marshal_petition, b.world)


class TestS14G5:
    """The sighting on the shipped board: the card built on Mack, Mack beaten
    and gone, Archduke Charles in reach. OLD reading: the delivered card still
    read "Send him against Mack into Swabia", the click spent 2 AP and ran
    PURSUE at Charles, and "Archduke Charles, then." was said after the
    battle."""

    def test_the_stored_card_names_its_quarry(self, _r5_board):
        card = _r5_card(_r5_board)
        opt = _r5_opt(card)
        assert opt["quarry"] == "Mack" and opt["quarry_region"] == "Swabia"
        assert opt["detail"].startswith("Send him against Mack into Swabia. A grievance ends")

    def test_the_delivered_card_names_the_live_man_and_says_the_change(self, _r5_board):
        from backend.commands.combat_executor import CombatExecutor
        b = _r5_board
        stored = _r5_card(b)
        before = json.dumps(stored, sort_keys=True, default=str)
        _r5_flee(b)
        opt = _r5_opt(_r5_delivered(b))
        theirs = CombatExecutor._fog_banded_strength(b.charles, b.world)
        assert opt["quarry"] == "ArchdukeCharles" and opt["quarry_region"] == "Munich"
        assert ("Mack has left Swabia — send him against Archduke Charles "
                "into Munich instead") in opt["detail"]
        assert f"({theirs} against his 22,000)?" in opt["detail"]
        assert "asks once more, free, with Berthier's reading of the odds" in opt["detail"]
        assert "Giving the order may bring on a battle at once." in opt["detail"]
        assert opt["enabled"] is True
        # PURE: the stored card keeps the builder's verdict.
        assert json.dumps(stored, sort_keys=True, default=str) == before

    def test_a_click_on_a_changed_quarry_spends_nothing_and_asks(self, _r5_board):
        from backend.commands.combat_executor import CombatExecutor
        b = _r5_board
        stored = _r5_card(b)
        _r5_flee(b)
        _r5_full(b)
        result = _r5_answer(b)
        assert result["success"] is False
        assert result["requires_input"] is True and result["quarry_changed"] is True
        assert b.world.actions_remaining == 4 and result["action_info"]["cost"] == 0
        assert b.murat.strategic_order is None
        msg = result["message"]
        assert msg.startswith("Mack has left Swabia; Archduke Charles at Munich (31,690 men against his 22,000) "
                              "is what stands in his reach now. Berthier reads the odds ")
        assert msg.endswith("Send him?")
        assert CombatExecutor._fog_banded_strength(b.charles, b.world) == "31,690 men"
        # the petition STANDS and is re-delivered carrying the live man
        assert b.world.pending_marshal_petition is stored
        card = _r5_opt(result["marshal_petition"])
        assert card["quarry"] == "ArchdukeCharles" and card["enabled"] is True
        assert card["detail"].startswith("Send him against Archduke Charles into Munich. A grievance")

    def test_the_second_click_is_the_yes(self, _r5_board):
        b = _r5_board
        _r5_card(b)
        _r5_flee(b)
        first = _r5_answer(b)
        assert first["success"] is False and b.world.actions_remaining == 4
        second = _r5_answer(b)
        assert second["success"] is True
        order = b.murat.strategic_order
        assert order is not None and order.command_type == "PURSUE"
        assert order.target == "ArchdukeCharles"
        assert b.world.actions_remaining == 2
        assert second["message"].startswith("\"Archduke Charles, then.\"")
        assert b.world.pending_marshal_petition is None

    def test_the_band_is_all_he_is_told_when_the_province_is_not_scouted(self, _r5_board):
        """Fog-honest (R5): the enemy's strength is the player's own reading
        of it - the intel band below FULL visibility, never the exact count."""
        from backend.models.intel import PARTIAL, get_strength_band
        b = _r5_board
        _r5_card(b)
        _r5_flee(b)
        b.world.intel["Munich"].visibility = PARTIAL
        msg = _r5_answer(b)["message"]
        assert "31,690" not in msg
        assert f"({get_strength_band(31690)} against his 22,000)" in msg

    def test_the_exact_figure_is_told_when_the_province_is_scouted(self, _r5_board):
        b = _r5_board
        _r5_card(b)
        _r5_flee(b)
        _r5_full(b)
        assert "(31,690 men against his 22,000)" in _r5_answer(b)["message"]

    def test_the_gate_band_refuses_free_and_the_card_stands(self, _r5_board):
        """The odds hold him as they hold an unasked glory attack
        (`glory_attack_held_by_the_odds`): REFUSED, free, the card standing -
        and clicking again does not turn the refusal into a yes."""
        from backend.game_logic import jealousy as J
        b = _r5_board
        stored = _r5_card(b)
        _r5_flee(b, charles_strength=150000)
        _r5_full(b)
        assert J.glory_attack_held_by_the_odds(b.world, b.executor, b.murat, b.charles) is not None
        for _ in range(2):
            result = _r5_answer(b)
            assert result["success"] is False and result.get("held_by_odds") is True
            assert "requires_input" not in result
            assert b.world.actions_remaining == 4 and b.murat.strategic_order is None
            msg = result["message"]
            assert msg.startswith("Mack has left Swabia; Archduke Charles at Munich "
                                  "(150,000 men against his 22,000) is what stands in his reach now, "
                                  "and the odds hold him — 1 to 2 against Archduke Charles's position at Munich.")
            assert msg.endswith("He is not sent: nothing was spent, and the card stands.")
            assert b.world.pending_marshal_petition is stored
        assert _r5_opt(stored)["quarry"] == "Mack"        # not re-stamped: still refused

    def test_the_unscouted_force_is_named_in_the_ask(self, _r5_board):
        """S14E-X75's rule, carried here: when the odds weigh a force of his
        the player has not scouted, the line `_unscouted_note_for` speaks
        rides the ask (staged by stub - the shipped board's Charles has no
        corps to answer his guns)."""
        b = _r5_board
        b.executor._combat._unscouted_note_for = lambda m, e, w: "SCOUT THE ROUND."
        _r5_card(b)
        _r5_flee(b)
        assert _r5_answer(b)["message"].endswith(" SCOUT THE ROUND. Send him?")

    def test_the_unscouted_force_is_named_in_the_refusal(self, _r5_board):
        b = _r5_board
        b.executor._combat._unscouted_note_for = lambda m, e, w: "SCOUT THE ROUND."
        _r5_card(b)
        _r5_flee(b, charles_strength=150000)
        refusal = _r5_answer(b)["message"]
        assert ("against Archduke Charles's position at Munich. SCOUT THE ROUND. "
                "He is not sent") in refusal

    def test_the_gate_is_the_one_predicate_the_glory_attack_reads(self, _r5_board, monkeypatch):
        """Seam check: the refusal reads `glory_attack_held_by_the_odds`, the
        function the unasked glory attack and the AI's P3.9 rung read."""
        from backend.game_logic import jealousy as J
        b = _r5_board
        _r5_card(b)
        _r5_flee(b)                                         # favourable by the muster
        monkeypatch.setattr(J, "glory_attack_held_by_the_odds",
                            lambda *a, **k: {"band": "unfavorable", "ratio": 0.25})
        held = _r5_answer(b)
        assert held.get("held_by_odds") is True and "1 to 4 against" in held["message"]
        monkeypatch.undo()
        assert _r5_answer(b).get("requires_input") is True

    def test_an_unchanged_quarry_runs_as_it_always_did(self, _r5_board):
        b = _r5_board
        _r5_card(b)
        result = _r5_answer(b)                              # nothing moved
        assert result["success"] is True and "requires_input" not in result
        assert b.murat.strategic_order.target == "Mack"
        assert b.world.actions_remaining == 2
        assert result["message"].startswith("\"Mack, then.\"")

    def test_a_quarry_that_left_and_left_nobody_says_what_became_of_him(self, _r5_board):
        b = _r5_board
        _r5_card(b)
        b.mack.location = "Tyrol"                            # out of reach, nobody else near
        b.world.calculate_visibility()
        opt = _r5_opt(_r5_delivered(b))
        assert opt["enabled"] is False
        assert opt["unavailable_reason"] == ("Mack has left Swabia. There is no enemy within "
                                             "his reach to send him against.")
        result = _r5_answer(b)
        assert result["success"] is False and "requires_input" not in result
        assert result["message"] == opt["unavailable_reason"]
        assert b.world.actions_remaining == 4

    def test_the_clause_says_why_in_each_case(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        w = b.world
        # the man is out of the field
        b.mack.strength = 0
        assert J._quarry_changed_clause(w, "Mack", "Swabia", b.charles, "Munich") == "Mack is out of the field"
        assert J._quarry_changed_clause(w, "Mack", "Swabia", b.charles, "Munich", past=True) == "Mack was out of the field"
        b.mack.strength = 52000
        # he moved on
        b.mack.location = "Tyrol"
        assert J._quarry_changed_clause(w, "Mack", "Swabia", b.charles, "Munich") == "Mack has left Swabia"
        # the same man, a different province
        assert J._quarry_changed_clause(w, "Mack", "Swabia", b.mack, "Tyrol") == "Mack has moved from Swabia to Tyrol"
        # he stands where he stood but is no longer the one the order falls on
        b.mack.location = "Swabia"
        assert J._quarry_changed_clause(w, "Mack", "Swabia", b.charles, "Munich") == \
            "Mack is no longer the weakest in his reach"
        assert J._quarry_changed_clause(w, "Mack", "Swabia", None, "") == "Mack is no longer within his reach"

    def test_a_weaker_man_arriving_changes_the_quarry_too(self, _r5_board):
        """Mack has not moved; a weaker corps came into reach - the order
        would now fall on him. The same ask."""
        b = _r5_board
        _r5_card(b)
        b.charles.location = "Munich"
        b.charles.strength = 9000
        b.world.calculate_visibility()
        result = _r5_answer(b)
        assert result["success"] is False and result["requires_input"] is True
        assert result["message"].startswith("Mack is no longer the weakest in his reach; "
                                            "Archduke Charles at Munich (")
        assert b.world.actions_remaining == 4

    def test_a_card_without_a_recorded_quarry_runs_as_before(self, _r5_board):
        """A card queued before this row (or built with nobody in reach)
        carries no `quarry`: nothing to compare, the order runs as it always
        did - the degradation is the old behaviour, never a crash."""
        b = _r5_board
        stored = _r5_card(b)
        opt = _r5_opt(stored)
        opt.pop("quarry")
        opt.pop("quarry_region")
        _r5_flee(b)
        result = _r5_answer(b)
        assert result["success"] is True
        assert b.murat.strategic_order.target == "ArchdukeCharles"

    def test_the_no_quarry_reason_is_the_availability_sentence(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        b.mack.location = "Tyrol"
        b.world.calculate_visibility()
        assert J.command_arm_availability(b.world, b.murat)[1] == J._NO_QUARRY_REASON

    def test_the_endpoint_hands_the_ask_to_the_client_and_spends_nothing(self, monkeypatch):
        """Through the real `POST /marshal_petition_response` on the booted
        shipped board: the reply is the question the client's marshal_petition
        route draws (the delivered card attached, the live man named), the
        message its own result prints first, and the pool untouched. OLD
        reading: `success: True`, 2 AP gone, a battle fought at Munich."""
        import backend.main as M
        from fastapi.testclient import TestClient
        from tests import _chip_census as C
        from backend.game_logic import jealousy as J
        prior = (M.world, M.game_state.get("world"), M.parser)
        try:
            C.board_env(monkeypatch)
            client = TestClient(M.app)
            with _r5_quiet():
                client.post("/new_game")
            world = M.world
            murat, ney = world.get_marshal("Murat"), world.get_marshal("Ney")
            murat.jealous_of = "Ney"
            murat.jealousy_turns_remaining = 3
            with _r5_quiet():
                assert J.queue_confrontation_petition(world, murat, ney, 1) == J.PETITION_QUEUED
            world.get_marshal("Mack").location = "Tyrol"
            charles = world.get_marshal("ArchdukeCharles")
            charles.location, charles.strength = "Munich", 31690
            world.calculate_visibility()
            ap = int(world.actions_remaining)
            with _r5_quiet():
                reply = client.post("/marshal_petition_response",
                                    json={"choice": "command"}).json()
            assert reply["success"] is False and reply["requires_input"] is True
            assert reply["message"].startswith(
                "Mack has left Swabia; Archduke Charles at Munich (")
            assert reply["message"].endswith("Send him?")
            assert int(world.actions_remaining) == ap and murat.strategic_order is None
            card = next(o for o in reply["marshal_petition"]["options"] if o["id"] == "command")
            assert card["quarry"] == "ArchdukeCharles" and card["enabled"] is True
            assert reply["action_info"]["cost"] == 0
            with _r5_quiet():
                again = client.post("/marshal_petition_response",
                                    json={"choice": "command"}).json()
            assert again["success"] is True and int(world.actions_remaining) == ap - 2
        finally:
            M.world, M.game_state["world"], M.parser = prior

    def test_the_ask_reaches_the_client_through_the_petition_route(self, _r5_board):
        """Surface check through the real endpoint helper: a failed answer's
        body carries the question the client's marshal_petition route draws
        (`marshal_petition` is a `_QUESTION_KEYS` member) and the message the
        command's own result prints first."""
        from backend import main as M
        b = _r5_board
        _r5_card(b)
        _r5_flee(b)
        result = _r5_answer(b)
        assert "marshal_petition" in M._QUESTION_KEYS
        assert M._result_carries_question(result) is True
        body = {k: v for k, v in result.items() if k != "marshal_petition"}
        assert "Send him?" in body["message"] and body["requires_input"] is True
        assert all(not isinstance(v, float) for v in body.values())


def _r5_aggressive_watch(b):
    """Murat warned, the jealousy pass run, Mack still at Swabia."""
    from backend.game_logic import jealousy as J
    b.world._jealousy_processed_turn = None
    with _r5_quiet():
        events = J.process_turn(b.world)
    return [e for e in events if e["type"] == "jealousy_autonomous_warning"]


class TestS14GX18:
    """The dispatch warning's fire-time re-target (the row's own second
    cause, `jealousy.py` the warning at ~4628 and its fire at ~4851): the
    warning named Mack ("Murat is eyeing Mack's position at ...") and the
    target was re-derived silently when he went. OLD reading: the fire-time
    beat "Murat, hungry for glory, has attacked Archduke Charles on his own
    initiative." with nothing said of Mack. NOW: the warning says the target
    may change and records whom it named (`__warned__` in the serialized
    `jealousy_history`), and the fire-time lines name both men."""

    def test_the_warning_says_the_target_may_change_and_records_whom_it_named(self, _r5_board):
        b = _r5_board
        warnings = _r5_aggressive_watch(b)
        assert len(warnings) == 1
        assert warnings[0]["message"] == (
            "Murat is eyeing Mack's position at Swabia. I cannot guarantee he "
            "will wait for orders, Sire — and if Mack has moved by the time he "
            "goes, he will take whoever is weakest in his reach. Give him "
            "something to do and he will stand down.")
        rec = b.murat.jealousy_history["__warned__"]
        assert rec["quarry"] == "Mack" and rec["region"] == "Swabia"
        assert isinstance(rec["turn"], int)

    def test_the_record_survives_a_save(self, _r5_board):
        from backend.models.marshal import Marshal
        b = _r5_board
        _r5_aggressive_watch(b)
        again = Marshal.from_dict(json.loads(json.dumps(b.murat.to_dict(), default=str)))
        assert again.jealousy_history["__warned__"]["quarry"] == "Mack"
        assert again.jealousy_autonomous_warned is True

    def test_the_fire_time_beat_names_both_men_when_the_quarry_changed(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        _r5_aggressive_watch(b)
        _r5_flee(b)                                           # Mack gone, Charles at Munich
        with _r5_quiet():
            J.process_autonomous_attacks(b.world, b.executor, {"world": b.world})
        events = b.world._pending_jealousy_turn_events
        beats = [e for e in events if e["type"] == "jealousy_autonomous_attack"]
        assert len(beats) == 1
        assert beats[0]["message"] == (
            "Murat, warned of eyeing Mack, strikes Archduke Charles at Munich "
            "instead — Mack had left Swabia, and he took the weakest man in his "
            "reach on his own initiative.")
        assert "__warned__" not in b.murat.jealousy_history          # read, used, cleared
        assert b.murat.jealousy_autonomous_warned is False

    def test_the_fire_time_beat_is_unchanged_when_the_quarry_stands(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        _r5_aggressive_watch(b)
        with _r5_quiet():
            J.process_autonomous_attacks(b.world, b.executor, {"world": b.world})
        beats = [e for e in b.world._pending_jealousy_turn_events
                 if e["type"] == "jealousy_autonomous_attack"]
        assert [e["message"] for e in beats] == [
            "Murat, hungry for glory, has attacked Mack on his own initiative."]

    def test_a_hand_set_flag_with_no_record_reads_as_it_always_did(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        b.murat.jealousy_autonomous_warned = True            # no `__warned__`
        _r5_flee(b)
        with _r5_quiet():
            J.process_autonomous_attacks(b.world, b.executor, {"world": b.world})
        beats = [e for e in b.world._pending_jealousy_turn_events
                 if e["type"] == "jealousy_autonomous_attack"]
        assert [e["message"] for e in beats] == [
            "Murat, hungry for glory, has attacked Archduke Charles on his own initiative."]

    def test_a_held_attack_on_a_changed_quarry_names_the_man_warned_of(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        _r5_aggressive_watch(b)
        _r5_flee(b, charles_strength=150000)
        with _r5_quiet():
            J.process_autonomous_attacks(b.world, b.executor, {"world": b.world})
        refused = [e for e in b.world._pending_jealousy_turn_events
                   if e["type"] == "jealousy_autonomous_refused"]
        assert len(refused) == 1 and refused[0]["held_by_odds"] is True
        assert refused[0]["message"].startswith(
            "Murat meant to go at Archduke Charles on his own initiative, but the odds held him")
        assert refused[0]["message"].endswith(
            " (Warned of eyeing Mack at Swabia, he found that Mack had left Swabia; the man in "
            "his reach was Archduke Charles at Munich.)")

    def test_a_warned_man_who_left_and_left_nobody_is_named_in_the_refusal(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        _r5_aggressive_watch(b)
        b.mack.location = "Tyrol"
        b.world.calculate_visibility()
        with _r5_quiet():
            results = J.process_autonomous_attacks(b.world, b.executor, {"world": b.world})
        assert results == []
        refused = [e for e in b.world._pending_jealousy_turn_events
                   if e["type"] == "jealousy_autonomous_refused"]
        assert [e["message"] for e in refused] == [
            "Murat meant to go at Mack on his own initiative, but Mack had left Swabia, "
            "and no enemy stood within his reach when the moment came — he stands where "
            "he was, and his orders are unchanged."]


class TestS14GX19:
    """S14G-X18: the confrontation's `acknowledge` ("Let it stand") arm
    printed his men and the turns left on his grievance as the BUILD turn read
    them; the combat math reads them live. OLD reading: "For 3 more turns he
    brings NONE of his 22,000 men ..." delivered after the clock had run down
    and the army had bled. NOW re-derived at delivery
    (`_with_live_details`), pure - the stored card keeps the builder's."""

    def test_the_standing_cost_is_re_read_at_delivery(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        stored = _r5_card(b)
        built = _r5_opt(stored, "acknowledge")["detail"]
        assert "For 3 more turns" in built and "22,000" in built
        b.murat.jealousy_turns_remaining = 1
        b.murat.strength = 15000
        shown = _r5_opt(_r5_delivered(b), "acknowledge")["detail"]
        assert "For 1 more turn " in shown and "15,000" in shown and "22,000" not in shown
        assert shown == J._standing_cost_detail(b.murat, b.ney)
        assert _r5_opt(stored, "acknowledge")["detail"] == built   # pure


class TestS14GX20:
    """S14G-X19: the rivalry card's Mediate and Force Reconciliation print the
    odds banded on the Emperor's authority AT BUILD, and the click bands on
    his authority LIVE (`_apply_rivalry_choice`). OLD reading: "Your word
    carries: 70% the breach is mended outright" shown at authority 75, rolled
    at the 40-point band after a defeat took twenty points. NOW the delivered
    card reads the authority the click will read."""

    def _rival(self, b, new_value):
        from backend.game_logic import jealousy as J
        with _r5_quiet():
            status = J.queue_rivalry_petition(b.world, b.murat, b.ney, new_value)
        assert status == J.PETITION_QUEUED
        return b.world.pending_marshal_petition

    def test_mediate_is_re_banded_on_the_live_authority(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        b.world.authority_tracker.authority = 75
        stored = self._rival(b, -1)
        built = _r5_opt(stored, "mediate")["detail"]
        assert built == J._mediate_detail(75)
        b.world.authority_tracker.authority = 45
        shown = _r5_opt(_r5_delivered(b), "mediate")["detail"]
        assert shown == J._mediate_detail(45) != built
        assert _r5_opt(stored, "mediate")["detail"] == built       # pure

    def test_force_reconciliation_is_re_banded_too(self, _r5_board):
        from backend.game_logic import jealousy as J
        b = _r5_board
        b.world.authority_tracker.authority = 85
        stored = self._rival(b, -2)
        assert _r5_opt(stored, "force_reconciliation")["detail"] == J._force_detail(85)
        b.world.authority_tracker.authority = 30
        shown = _r5_opt(_r5_delivered(b), "force_reconciliation")["detail"]
        assert shown == J._force_detail(30)

    def test_an_ap_only_stub_world_leaves_the_card_as_built(self):
        """The delivery pins hand the refresher a world that is only AP: the
        live re-derivation must leave such a card exactly as it was."""
        from backend.game_logic import jealousy as J
        petition = {"kind": "rivalry_confrontation", "context": {"marshal": "Murat"},
                    "options": [{"id": "mediate", "detail": "as built", "ap_cost": 1,
                                 "enabled": True}]}
        out = J.refresh_petition_affordability(
            petition, SimpleNamespace(actions_remaining=4))
        assert out["options"][0]["detail"] == "as built"


# ══════════════════════════════════════════════════════════════════════════
# row06
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 — row S14G-6 with its ruling S14G-D3 (October 26, 2026).
#
# THE CAUSE as traced (DD-B's third measure, `docs/BUG_FIXES.md` §S14G, S14G-6):
# every unanswered envoy letter - a Portuguese Open Borders courtesy as much as an
# armistice from Austria - shut the Cabinet (the diplomacy wizard, and every chip
# that opens it) for the turn: `DialogueManager.has_current_turn_offers` counted
# every `CURRENT_TURN_OFFER_TYPES` item that was not a moment letter. The lock was
# said only on tooltips (the Not Now button, the Cabinet button) and after the
# click (the echo, the wizard's notice - S14E-18's fix, `Utils.cabinet_shut_line`);
# `main.gd::_cabinet_locked` had no reader; the Envoys badge's tooltip never said
# it; the letter's body never stated it.
#
# THE SIGHTINGS: conquest #6 (P2, turn 5, action 92) pressed Not Now on Austria's
# armistice to deal with the Hanover crisis and found the Cabinet shut - "nothing
# on the Not Now button says it"; diplomacy #11 (P3, turn 2, action 42) tried the
# Cabinet with three minor-court letters unanswered (the Porte's and Portugal's
# Open Borders) and met a locked wizard.
#
# THE RULING S14G-D3 (the user, "Take S14G-D1 ... D7 as recommended"): ONLY A GREAT
# COURT'S LETTER OR AN ULTIMATUM LOCKS - a lesser court's routine letter answers in
# place and never shuts the Cabinet, the way a moment letter already does; and
# whichever letters lock, the lock stands on the button's face and in the letter.
#
# THE FIX
# * `DialogueManager.letter_locks_cabinet(item)` is THE seam: a letter locks when
#   it is an ultimatum, or from a great court (`power_tier == "major"`, the one
#   notion: `NATION_POWER_TIERS` read as `world.get_power_tier` reads it), or a WAR
#   decision whatever the sender (`WAR_DECISION_LETTER_TYPES`: peace, harsh peace,
#   every armistice, a brokered peace, an ally's call to arms). `has_current_turn_offers`,
#   `locking_letters` and the wire stamp all read it through `item_locks_cabinet`
#   (the type and moment-letter filters stand OUTSIDE the seam). Seam down =
#   `lambda self, item: True` = today's reading, byte for byte.
# * The payload: the letter's popup / dialogue leaves `_wire_dialogue` with
#   `locks_cabinet` (bool) on a COPY; the base envelope, `/test` and both
#   `/diplomatic_preview` payloads carry `cabinet_locked_by` (the printed court
#   names) beside `cabinet_locked` / `cabinet_locked_until`.
# * Godot: the popup's Not Now reads "Not Now (Cabinet stays shut)" and a line
#   under the buttons says "Set aside - the Cabinet stays shut ..." for a letter
#   that locks (a quieter "waits in the mailbox ... the Cabinet stays open" line
#   for one that does not), the body prints the sentence in amber, the Cabinet
#   button's FACE reads "The Cabinet - shut" in amber (its tooltip names the
#   court), the Envoys badge's tooltip names whose letter shuts it, the wizard's
#   notice names it too - every surface calling the one sentence
#   `Utils.cabinet_shut_line`.
#
# KEPT: `lapse_pending_offers` is untouched (a lesser letter still lapses at the
# turn's end); the mailbox still lists every letter; a moment letter still locks
# nothing (S14c seam 9); a call to arms still stands to its answer-by turn.
#
# Helpers and fixtures are prefixed `_r6_` so the file merges into one module.

_R6_REPO = Path(__file__).resolve().parents[1]
_R6_SCRIPTS = _R6_REPO / "godot-client" / "project-sovereign" / "scripts"
_R6_SCENARIO = (_R6_REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                / "europe_1805.json")

_R6_SHUT = "the Cabinet stays shut until it is answered or the turn ends."


def _r6_quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _r6_src(name: str) -> str:
    return (_R6_SCRIPTS / name).read_text(encoding="utf-8")


def _r6_func(src: str, name: str) -> str:
    """A GDScript function's body: from its header to the next top-level one."""
    start = src.index(f"func {name}(")
    ends = [e for e in (src.find("\nfunc ", start + 1), src.find("\nstatic func ", start + 1))
            if e != -1]
    return src[start:min(ends) if ends else len(src)]


@pytest.fixture(scope="module")
def _r6_boot():
    from backend.models.world_state import WorldState
    with _r6_quiet():
        return WorldState.from_scenario(str(_R6_SCENARIO))


@pytest.fixture
def _r6_world(_r6_boot):
    """The shipped 1805 board, a private copy per test."""
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_r6_boot.to_dict(), default=str)))


def _r6_terms(court: str, ttype: str, **extra) -> dict:
    return {"type": ttype, "proposer_nation": court, "target_nation": "France",
            "demands": [], "sweeteners": [], "clauses": [], **extra}


def _r6_letter(world, court: str, ptype: str = "open_borders", ttype: str | None = None):
    """A court's letter built by the REAL builder and pushed on the dialogue
    manager (what the transport does), without the delivery gates."""
    from backend.game_logic.ai_diplomacy import _make_proposal, build_ai_proposal_dialogue
    terms = _r6_terms(court, ttype or ptype)
    with _r6_quiet():
        dialogue = build_ai_proposal_dialogue(_make_proposal(court, ptype, 5, terms, world), world)
        world.dialogue_manager.push(dialogue)
    return dialogue


def _r6_hand_letter(court: str, label: str, ttype: str | None = None, dtype: str = "incoming_proposal") -> dict:
    """A hand-built letter of the shape every builder writes (the predicate
    reads only `type`, `target_nation` and `context`)."""
    terms = {"type": ttype or label}
    return {"type": dtype, "target_nation": court, "blocking": False,
            "context": {"proposal": terms, "source_nation": court, "proposal_type": label}}


def _r6_ultimatum(world, court: str):
    from backend.game_logic.ai_diplomacy import _build_ai_ultimatum_dialogue, _make_proposal
    terms = _r6_terms(court, "ultimatum_demand",
                      demands=[{"type": "gold_lump", "value": 300}])
    with _r6_quiet():
        dialogue = _build_ai_ultimatum_dialogue(_make_proposal(court, "ultimatum", 7, terms, world), world)
        world.dialogue_manager.push(dialogue)
    return dialogue


def _r6_base(world) -> dict:
    import backend.main as M
    with _r6_quiet():
        return M.build_base_response(world, success=True, message="x")


@contextlib.contextmanager
def _r6_served(world):
    """Swap the three module globals together (the testclient world swap)."""
    import backend.main as M
    from backend.commands.parser import CommandParser
    from fastapi.testclient import TestClient
    saved = (M.game_state["world"], M.world, M.parser)
    M.game_state["world"] = world
    M.world = world
    M.parser = CommandParser(use_real_llm=False)
    try:
        with _r6_quiet():
            yield TestClient(M.app)
    finally:
        M.game_state["world"], M.world, M.parser = saved


def _r6_wire(world, dialogue) -> dict:
    """The letter's popup payload as the client receives it."""
    import backend.main as M
    with _r6_quiet():
        popup = M._build_pending_envoy_popup_from_dialogue(world, dialogue)
        return M._wire_dialogue(world, popup)


# ══════════════════════════════════════════════════════════════════════════
# S14G-6 — the lock is said where the player decides, and a courtesy holds none
# ══════════════════════════════════════════════════════════════════════════

class TestS14G6:
    """Reproduced on the shipped 1805 board. THE OLD READING: Portugal's Open
    Borders courtesy, pushed as a current-turn letter, made
    `has_current_turn_offers()` True, `get_available_diplomatic_actions` return
    [] (the wizard's gate), `/diplomatic_preview` carry `dialogue_pending: true`
    and the base envelope `cabinet_locked: true` - the Cabinet shut on a
    routine mail. NOW: the courtesy answers in place (it stays on the envoy
    badge and in the mailbox), the wizard is open, the envelope says
    `cabinet_locked: false` with no court named; Austria's armistice still
    shuts it and the envelope names Austria."""

    def test_a_portuguese_courtesy_leaves_the_wizard_open(self, _r6_world):
        w = _r6_world
        _r6_letter(w, "Portugal", "open_borders")
        dm = w.dialogue_manager
        assert dm.has_current_turn_offers() is False
        # the wizard's gate (court page) passes: actions are listed, not []
        from backend.game_logic.diplomacy import get_available_diplomatic_actions, get_diplomatic_preview
        assert get_available_diplomatic_actions(w, "Austria") != []
        assert get_diplomatic_preview(w, "Austria")["dialogue_pending"] is False
        base = _r6_base(w)
        assert base["cabinet_locked"] is False
        assert base["cabinet_locked_by"] == []
        assert base["cabinet_locked_until"] == 0
        # still mail: the badge counts it and the mailbox lists it
        assert base["pending_envoy_count"] == 1
        rows = dm.get_mailbox_items(w)
        assert [r["source_nation"] for r in rows] == ["Portugal"]

    def test_the_porte_and_three_minor_courts_together_lock_nothing(self, _r6_world):
        """DD-B diplomacy #11: three minor-court letters on turn 2."""
        w = _r6_world
        for court in ("Portugal", "Ottoman", "Saxony"):
            _r6_letter(w, court, "open_borders")
        assert w.dialogue_manager.get_mailbox_count() == 3
        assert w.dialogue_manager.has_current_turn_offers() is False
        assert _r6_base(w)["cabinet_locked"] is False

    def test_the_wizard_payloads_say_it_is_open(self, _r6_world):
        w = _r6_world
        _r6_letter(w, "Portugal", "open_borders")
        with _r6_served(w) as client:
            nations = client.get("/diplomatic_preview").json()
            court = client.get("/diplomatic_preview", params={"nation": "Austria"}).json()
            hello = client.get("/test").json()
        for payload in (nations, court):
            assert payload["dialogue_pending"] is False
            assert payload["cabinet_locked"] is False
            assert payload["cabinet_locked_by"] == []
            assert payload["pending_envoy_count"] == 1
        assert hello["cabinet_locked"] is False and hello["cabinet_locked_by"] == []

    def test_austrias_armistice_still_shuts_it_and_the_envelope_names_her(self, _r6_world):
        """The conquest road's sighting: the armistice IS a war decision."""
        w = _r6_world
        _r6_letter(w, "Austria", "armistice")
        assert w.dialogue_manager.has_current_turn_offers() is True
        base = _r6_base(w)
        assert base["cabinet_locked"] is True
        assert base["cabinet_locked_by"] == ["Austria"]
        assert isinstance(base["cabinet_locked_by"], list)
        with _r6_served(w) as client:
            nations = client.get("/diplomatic_preview").json()
            court = client.get("/diplomatic_preview", params={"nation": "Prussia"}).json()
            hello = client.get("/test").json()
        for payload in (nations, court):
            assert payload["dialogue_pending"] is True
            assert payload["cabinet_locked"] is True
            assert payload["cabinet_locked_by"] == ["Austria"]
        assert hello["cabinet_locked"] is True and hello["cabinet_locked_by"] == ["Austria"]

    def test_the_courts_are_named_once_each_in_the_order_they_wrote(self, _r6_world):
        w = _r6_world
        _r6_letter(w, "Austria", "armistice")
        _r6_letter(w, "Prussia", "open_borders")
        _r6_letter(w, "Portugal", "open_borders")     # a courtesy: not named
        _r6_letter(w, "Austria", "peace")             # again: once
        assert _r6_base(w)["cabinet_locked_by"] == ["Austria", "Prussia"]

    def test_a_formed_court_is_named_by_its_printed_form(self, _r6_world):
        """The name is the popup's own `from_nation_display` (formed name +
        article): the Ottoman court's war letter names "the Ottoman Empire"."""
        from backend.display_names import with_definite_article
        from backend.game_logic.formations import formed_display_name
        w = _r6_world
        _r6_letter(w, "Ottoman", "peace")
        want = with_definite_article(formed_display_name(w, "Ottoman"))
        assert _r6_base(w)["cabinet_locked_by"] == [want]

    def test_the_letter_carries_its_own_verdict_to_the_popup(self, _r6_world):
        """`locks_cabinet` rides the incoming letter's payload - on a COPY."""
        w = _r6_world
        austria = _r6_letter(w, "Austria", "armistice")
        portugal = _r6_letter(w, "Portugal", "open_borders")
        assert _r6_wire(w, austria)["locks_cabinet"] is True
        assert _r6_wire(w, portugal)["locks_cabinet"] is False
        # the stored dialogues never gain the key (a copy leaves the door)
        for stored in (austria, portugal):
            assert "locks_cabinet" not in stored
            assert "locks_cabinet" not in (stored.get("popup_payload") or {})

    def test_the_dialogue_payload_carries_it_too(self, _r6_world):
        import backend.main as M
        w = _r6_world
        austria = _r6_letter(w, "Austria", "armistice")
        portugal = _r6_letter(w, "Portugal", "open_borders")
        assert M._wire_dialogue(w, austria)["locks_cabinet"] is True
        assert M._wire_dialogue(w, portugal)["locks_cabinet"] is False
        assert "locks_cabinet" not in austria

    def test_pending_envoy_serves_the_verdict_on_the_active_letter(self, _r6_world):
        w = _r6_world
        _r6_letter(w, "Portugal", "open_borders")
        with _r6_served(w) as client:
            courtesy = client.get("/pending_envoy").json()
        assert courtesy["incoming_proposal"]["locks_cabinet"] is False
        w2 = _r6_world
        w2.dialogue_manager.remove_matching(lambda d: True)
        _r6_letter(w2, "Austria", "armistice")
        with _r6_served(w2) as client:
            war = client.get("/pending_envoy").json()
        assert war["incoming_proposal"]["locks_cabinet"] is True
        assert isinstance(war["incoming_proposal"]["locks_cabinet"], bool)

    def test_a_non_letter_payload_passes_through_untouched(self, _r6_world):
        """A proposal RESULT (no dialogue behind it) and a non-offer dialogue
        gain no `locks_cabinet` key."""
        import backend.main as M
        w = _r6_world
        assert "locks_cabinet" not in M._wire_dialogue(w, {"from_nation": "Austria"})
        assert "locks_cabinet" not in M._wire_dialogue(w, {"type": "advisory", "dialogue_id": 99})
        assert M._wire_dialogue(w, None) is None

    def test_answering_the_locking_letter_lifts_the_lock_with_courtesies_standing(self, _r6_world):
        w = _r6_world
        austria = _r6_letter(w, "Austria", "armistice")
        _r6_letter(w, "Portugal", "open_borders")
        assert w.dialogue_manager.has_current_turn_offers() is True
        w.dialogue_manager.remove_matching(lambda d: d is austria)
        assert w.dialogue_manager.has_current_turn_offers() is False
        assert w.dialogue_manager.get_mailbox_count() == 1

    def test_a_lesser_letter_still_lapses_at_the_turns_end(self, _r6_world):
        """`lapse_pending_offers` is untouched: nothing about the lock changed
        what the turn's end does to mail."""
        w = _r6_world
        _r6_letter(w, "Portugal", "open_borders")
        lapsed = w.dialogue_manager.lapse_pending_offers(int(w.current_turn), world=w)
        assert [row["nation"] for row in lapsed] == ["Portugal"]
        assert w.dialogue_manager.get_mailbox_count() == 0

    def test_a_moment_letter_still_locks_nothing(self):
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        dm.push({"type": "incoming_proposal", "target_nation": "Austria", "blocking": False,
                 "context": {"proposal_type": "moment_letter", "proposal": {}}})
        assert dm.has_current_turn_offers() is False
        assert dm.locking_letters() == []

    # ── the Godot text, every surface through the one sentence ───────────

    def test_one_sentence_one_source_across_every_script(self):
        """The lock is worded ONCE (`Utils.cabinet_shut_line`); no other script
        spells it."""
        fragment = "stays shut until it is answered"
        spellings = [p.name for p in sorted(_R6_SCRIPTS.glob("*.gd"))
                     if fragment in p.read_text(encoding="utf-8")]
        assert spellings == ["utils.gd"], spellings
        body = _r6_func(_r6_src("utils.gd"), "cabinet_shut_line")
        assert f'return "{_R6_SHUT}"' in body

    def test_the_popup_says_the_lock_on_the_button_under_it_and_in_the_body(self):
        popup = _r6_src("incoming_proposal_popup.gd")
        # the Not Now label and the line under the buttons
        assert 'const NOT_NOW_LOCKED_LABEL := "Not Now (Cabinet stays shut)"' in popup
        assert 'const NOT_NOW_LABEL := "Not Now"' in popup
        assert 'const SET_ASIDE_LOCKED_PREFIX := "Set aside — "' in popup
        show = _r6_func(popup, "show_proposal")
        assert 'bool(data.get("locks_cabinet", false))' in show
        arm = show[show.index("S14E-18 (S14f part 2): a set-aside letter still stands"):
                   show.index("# Button labels adapt to context")]
        assert "dismiss_btn.text = NOT_NOW_LOCKED_LABEL" in arm
        assert "_set_aside_line.text = SET_ASIDE_LOCKED_PREFIX + Utils.cabinet_shut_line(_lock_by_turn)" in arm
        assert "Utils.UI_WARNING" in arm       # amber, the palette's own
        # the line is a Label under the ButtonContainer (the VBox's last child)
        ready = _r6_func(popup, "_ready")
        assert "_set_aside_line = Label.new()" in ready
        assert "$PanelContainer/VBoxContainer.add_child(_set_aside_line)" in ready
        # the body carries the sentence, set to start a sentence, in amber
        body_arm = show[show.index("S14G-6 (Pre-Deploy S14h part 1, October 26, 2026): the lock in the"):
                        show.index("# Backend prose (clause strings")]
        assert "Utils.cabinet_shut_sentence(body_lock_turn)" in body_arm
        assert "Utils.COLOR_WARNING" in body_arm
        # composed, the player reads the brief's words
        assert ("Set aside — " + _R6_SHUT).startswith(
            "Set aside — the Cabinet stays shut until it is answered or the turn ends.")

    def test_the_popup_says_a_courtesy_waits_and_the_cabinet_stays_open(self):
        popup = _r6_src("incoming_proposal_popup.gd")
        assert ('const SET_ASIDE_WAITS_LINE := "Set aside — it waits in the mailbox until '
                'the turn ends; the Cabinet stays open."') in popup
        show = _r6_func(popup, "show_proposal")
        assert ('"Set this letter aside — it waits in the mailbox and the Cabinet stays open. '
                'The envoy badge reopens it."') in show
        # a moment letter's own line is untouched
        assert '"Set this letter aside. The envoy badge reopens it."' in show

    def test_the_cabinet_buttons_face_reads_its_own_flag_in_amber(self):
        main = _r6_src("main.gd")
        assert 'const CABINET_SHUT_FACE := "⚖ The Cabinet — shut"' in main
        body = _r6_func(main, "_set_cabinet_locked")
        # `_cabinet_locked` has a reader: the face branches on it
        assert "if _cabinet_locked:" in body
        assert "diplomacy_button.text = CABINET_SHUT_FACE" in body
        assert 'diplomacy_button.add_theme_color_override("font_color", Utils.UI_WARNING)' in body
        # the tooltip names the court(s), then the one sentence
        assert ('"The Cabinet (F1) — " + Utils.cabinet_shut_lead(_cabinet_locked_by) '
                '+ Utils.cabinet_shut_line(until)') in body
        # and the authored face comes back when the lock lifts
        assert "diplomacy_button.text = _cabinet_face_default_text" in body
        assert ('diplomacy_button.add_theme_color_override("font_color", '
                '_cabinet_face_default_color)') in body
        assert "_cabinet_locked_by = []" in body
        # fed by the backend's `cabinet_locked_by`, read before the lock is applied
        upd = _r6_func(main, "_update_diplomatic_top_bar")
        assert 'response.get("cabinet_locked_by", [])' in upd
        assert upd.index('response.get("cabinet_locked_by", [])') < upd.index("_set_cabinet_locked(")
        assert 'diplo_data["cabinet_locked_by"] = _cabinet_locked_by' in upd

    def test_the_envoys_badge_names_whose_letter_shuts_the_cabinet(self):
        bar = _r6_src("top_bar.gd")
        body = _r6_func(bar, "update_mailbox_count")
        assert "if _cabinet_locked:" in body
        assert ("Utils.cabinet_shut_lead(_cabinet_locked_by, true) "
                "+ Utils.cabinet_shut_line(_cabinet_locked_until)") in body
        upd = _r6_func(bar, "update_diplomatic_fields")
        assert 'data.get("cabinet_locked_by", [])' in upd
        assert 'int(data.get("cabinet_locked_until", 0))' in upd
        # a count of zero says no lock (the badge's idle branch is unchanged)
        assert 'mailbox_btn.tooltip_text = "No pending envoys."' in body

    def test_the_wizards_notice_names_the_court(self):
        wiz = _r6_src("diplomacy_wizard.gd")
        body = _r6_func(wiz, "_add_dialogue_gate_notice")
        assert "Utils.cabinet_shut_letters(locked_by)" in body
        assert "Utils.cabinet_shut_line(locked_until)" in body
        assert "An unanswered envoy awaits your reply" in body
        for render in ("_render_nations", "_render_preview"):
            src = _r6_func(wiz, render)
            assert 'data.get("cabinet_locked_by", [])' in src, render
            assert 'bool(data.get("cabinet_locked", pending_envoy_count > 0))' in src, render

    def test_the_helper_composes_the_names_the_way_the_surfaces_read_them(self):
        """`cabinet_shut_letters` / `cabinet_shut_lead`: the noun phrase and the
        lead every surface puts before `cabinet_shut_line`."""
        utils = _r6_src("utils.gd")
        letters = _r6_func(utils, "cabinet_shut_letters")
        assert 'return str(owners[0]) + " letter"' in letters
        assert '" and " + str(owners[owners.size() - 1]) + " letters"' in letters
        lead = _r6_func(utils, "cabinet_shut_lead")
        assert '" unanswered — "' in lead
        assert 'letters = "a letter"' in lead
        assert "cabinet_shut_line" in _r6_func(utils, "cabinet_shut_sentence")


# ══════════════════════════════════════════════════════════════════════════
# S14G-D3 — only a great court's letter, an ultimatum or a war decision locks
# ══════════════════════════════════════════════════════════════════════════

class TestS14GD3:
    """The ruling as built (`DialogueManager.letter_locks_cabinet`). WHICH
    LETTERS: an ultimatum (any sender); any letter from a great court (an
    authored `power_tier == "major"` - France's rivals Britain, Russia,
    Austria, Prussia, the one notion `world.get_power_tier` reads); a WAR
    DECISION from any court - peace, harsh peace, armistice (all four
    variants), a brokered peace, an ally's call to arms; a letter that names
    no court (the old reading). EVERYTHING ELSE answers in place: a lesser
    court's open borders, non-aggression, gift, alliance, design purchase,
    neutrality compact, offer of submission, its client's petition and its
    counter-offer in a courtesy negotiation."""

    def test_the_great_courts_and_the_lesser_courts_are_the_authored_tiers(self, _r6_world):
        from backend.nation_config import NATION_POWER_TIERS
        majors = sorted(n for n, t in NATION_POWER_TIERS.items() if t == "major")
        assert majors == ["Austria", "Britain", "France", "Prussia", "Russia"]
        dm = _r6_world.dialogue_manager
        for court in majors:
            assert dm.letter_locks_cabinet(_r6_hand_letter(court, "open_borders")) is True, court
        for court in sorted(n for n, t in NATION_POWER_TIERS.items() if t != "major"):
            assert dm.letter_locks_cabinet(_r6_hand_letter(court, "open_borders")) is False, court

    def test_only_a_great_courts_courtesy_locks_among_the_shipped_boards_courts(self, _r6_world):
        """Every non-player court of the shipped board, a courtesy each: the
        lock is exactly `world.get_power_tier(court) == "major"`."""
        w = _r6_world
        dm = w.dialogue_manager
        for court in sorted(w.enemy_nations):
            letter = _r6_hand_letter(court, "open_borders")
            assert dm.letter_locks_cabinet(letter) is (w.get_power_tier(court) == "major"), court

    @pytest.mark.parametrize("label", ["non_aggression", "open_borders", "friendly_gift",
                                       "alliance", "defensive_alliance", "design_purchase",
                                       "sell_neutrality", "offer_vassalage", "opportunistic",
                                       "client_petition"])
    def test_a_lesser_courts_non_war_letter_never_locks(self, label):
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        assert dm.letter_locks_cabinet(_r6_hand_letter("Portugal", label)) is False
        assert dm.letter_locks_cabinet(_r6_hand_letter("Ottoman", label)) is False

    @pytest.mark.parametrize("label", ["peace", "harsh_peace", "armistice", "armistice_losing",
                                       "armistice_stalemate", "armistice_winning",
                                       "broker_peace", "call_to_arms"])
    def test_a_lesser_courts_war_decision_locks(self, label):
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        assert dm.letter_locks_cabinet(_r6_hand_letter("Portugal", label)) is True

    def test_a_rewritten_terms_type_is_still_a_war_decision(self):
        """`harsh_peace` is rewritten to terms type `peace` downstream and
        `armistice_stalemate` to `armistice_losing`: the label or the terms,
        either reads as the war letter it is."""
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        assert dm.letter_locks_cabinet(_r6_hand_letter("Portugal", "", ttype="peace")) is True
        assert dm.letter_locks_cabinet(
            _r6_hand_letter("Portugal", "armistice_stalemate", ttype="armistice_losing")) is True
        assert dm.letter_locks_cabinet(_r6_hand_letter("Portugal", "friendly_gift",
                                                       ttype="open_borders")) is False

    def test_every_armistice_the_game_names_is_a_war_decision(self):
        from backend.display_names import PROPOSAL_TYPE_DISPLAY
        from backend.models.dialogue_manager import WAR_DECISION_LETTER_TYPES
        armistices = {k for k, v in PROPOSAL_TYPE_DISPLAY.items() if v == "Armistice"}
        assert armistices and armistices <= WAR_DECISION_LETTER_TYPES
        assert {"peace", "harsh_peace", "broker_peace", "call_to_arms"} <= WAR_DECISION_LETTER_TYPES
        # and the courtesies are NOT in it
        assert not ({"open_borders", "non_aggression", "friendly_gift", "alliance",
                     "defensive_alliance", "client_petition"} & WAR_DECISION_LETTER_TYPES)

    def test_an_ultimatum_locks_whoever_sends_it(self, _r6_world):
        w = _r6_world
        ult = _r6_ultimatum(w, "Portugal")
        assert ult["type"] == "incoming_ultimatum"
        assert w.dialogue_manager.has_current_turn_offers() is True
        base = _r6_base(w)
        assert base["cabinet_locked"] is True and base["cabinet_locked_by"] == ["Portugal"]
        assert _r6_wire(w, ult)["locks_cabinet"] is True

    def test_a_real_peace_from_a_lesser_court_locks(self, _r6_world):
        w = _r6_world
        _r6_letter(w, "Portugal", "peace")
        assert w.dialogue_manager.has_current_turn_offers() is True
        assert _r6_base(w)["cabinet_locked_by"] == ["Portugal"]

    def test_a_great_courts_courtesy_locks(self, _r6_world):
        """"A great court's letter locks" - Prussia's Open Borders, the same
        letter Portugal's courtesy is, from a court that matters."""
        w = _r6_world
        _r6_letter(w, "Prussia", "open_borders")
        assert w.dialogue_manager.has_current_turn_offers() is True
        assert _r6_base(w)["cabinet_locked_by"] == ["Prussia"]

    def test_a_lesser_courts_counter_in_a_courtesy_negotiation_does_not_lock(self):
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        original = {"type": "open_borders"}
        counter = {"type": "counter_offer", "target_nation": "Portugal",
                   "context": {"proposal": {"type": "open_borders"},
                               "original_proposal": original, "source_nation": "Portugal",
                               "is_counter": True, "proposal_type": "open_borders"}}
        response = {"type": "counter_offer_response", "target_nation": "Portugal",
                    "context": {"source_nation": "Portugal", "original_proposal": original,
                                "counter_terms": {"type": "open_borders"}}}
        assert dm.letter_locks_cabinet(counter) is False
        assert dm.letter_locks_cabinet(response) is False
        # ...but a counter on a PEACE negotiation is a war decision, and a
        # great court's counter locks whatever it is about
        peace = {"type": "counter_offer_response", "target_nation": "Portugal",
                 "context": {"source_nation": "Portugal", "original_proposal": {"type": "peace"},
                             "counter_terms": {"type": "peace"}}}
        assert dm.letter_locks_cabinet(peace) is True
        great = dict(counter, target_nation="Austria")
        assert dm.letter_locks_cabinet(great) is True

    def test_a_letter_with_no_sender_keeps_the_old_reading(self):
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        assert dm.letter_locks_cabinet({"type": "incoming_proposal"}) is True

    def test_what_is_not_a_current_turn_offer_never_locks(self):
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        for dtype in ("incoming_settlement_offer", "ally_settlement_petition", "advisory",
                      "terms_guidance", "settlement_confirm"):
            assert dm.letter_locks_cabinet({"type": dtype, "target_nation": "Austria"}) is False, dtype
            assert dm.item_locks_cabinet({"type": dtype, "target_nation": "Austria"}) is False, dtype
        assert dm.letter_locks_cabinet(None) is False and dm.item_locks_cabinet("x") is False

    def test_a_call_to_arms_from_a_lesser_ally_locks_to_its_answer_by_turn(self, _r6_world):
        """S14E-X92's reading survives: the call stands two turns and the lock
        says so (`cabinet_locked_until`)."""
        from backend.game_logic import call_to_arms
        w = _r6_world
        with _r6_quiet():
            call_to_arms.post_call(w, ally="Spain", target="Britain", callee="France", war_id="w6")
        base = _r6_base(w)
        assert base["cabinet_locked"] is True
        assert base["cabinet_locked_until"] == int(w.current_turn) + 2
        assert base["cabinet_locked_by"] == ["Spain"]

    def test_the_seam_down_the_courtesy_locks_again(self, _r6_world, monkeypatch):
        """THE SEAM: `DialogueManager.letter_locks_cabinet` patched to its old
        reading (every current-turn offer that is not a moment letter locks)
        restores today's lock on every road - the dialogue manager, the base
        envelope, the wizard's gate and the wire."""
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        from backend.models.dialogue_manager import DialogueManager
        w = _r6_world
        courtesy = _r6_letter(w, "Portugal", "open_borders")
        assert w.dialogue_manager.has_current_turn_offers() is False
        monkeypatch.setattr(DialogueManager, "letter_locks_cabinet", lambda self, item: True)
        assert w.dialogue_manager.has_current_turn_offers() is True
        assert get_available_diplomatic_actions(w, "Austria") == []
        base = _r6_base(w)
        assert base["cabinet_locked"] is True and base["cabinet_locked_by"] == ["Portugal"]
        assert _r6_wire(w, courtesy)["locks_cabinet"] is True

    def test_the_seam_down_keeps_the_moment_letter_unlocking(self, monkeypatch):
        """The type and moment filters stand OUTSIDE the seam: 'down' is
        today's reading, in which a moment letter never locked."""
        from backend.models.dialogue_manager import DialogueManager
        monkeypatch.setattr(DialogueManager, "letter_locks_cabinet", lambda self, item: True)
        dm = DialogueManager()
        dm.push({"type": "incoming_proposal", "target_nation": "Portugal", "blocking": False,
                 "context": {"proposal_type": "moment_letter", "proposal": {}}})
        assert dm.has_current_turn_offers() is False
        dm2 = DialogueManager()
        dm2.push({"type": "advisory", "target_nation": "Portugal"})
        assert dm2.has_current_turn_offers() is False

    def test_the_docstring_names_which_types_were_counted(self):
        from backend.models.dialogue_manager import DialogueManager
        doc = DialogueManager.letter_locks_cabinet.__doc__
        for word in ("ultimatum", "GREAT COURT", "WAR DECISION", "WAR_DECISION_LETTER_TYPES",
                     "call to arms", "lapse_pending_offers", "Seam \"down\""):
            assert word in doc, word

    def test_the_lock_is_not_a_second_gate_for_the_ai(self, _r6_world):
        """Golden Rule 5: the lock gates the PLAYER's Cabinet; the AI never
        reads it (`has_current_turn_offers` has no reader in the AI's roads),
        so no series arm moves. Pinned by source: nothing under `backend/ai/`
        or the turn manager asks it."""
        for rel in ("backend/ai", "backend/game_logic/turn_manager.py",
                    "backend/game_logic/ai_diplomacy.py"):
            path = _R6_REPO / rel
            files = sorted(path.rglob("*.py")) if path.is_dir() else [path]
            for f in files:
                text = f.read_text(encoding="utf-8")
                assert "has_current_turn_offers" not in text, f.name
                assert "letter_locks_cabinet" not in text, f.name


# ══════════════════════════════════════════════════════════════════════════
# S14G-X21 — the wizard named an ENVOY for a lock a hard stop kept
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX21:
    """Cause: `diplomacy_wizard.gd::_add_dialogue_gate_notice` took its first
    branch on `pending_envoy_count > 0` alone, so a Cabinet gated by a hard-stop
    or local-planning dialogue (the terms you are drafting) with ANY mail
    waiting read "An unanswered envoy awaits your reply - the Cabinet stays shut
    ... Reopen Envoys to answer it" - naming a letter that held nothing shut and
    sending the player to a mailbox the hard stop refuses to open. With S14G-D3
    a lesser court's courtesy is exactly that mail.

    Fixed (same file): the payloads carry `cabinet_locked` (a LETTER is what
    gates) and `cabinet_locked_by`; the envoy branch needs both the count and
    the flag, the dialogue's own name wins otherwise."""

    def test_a_hard_stop_with_a_courtesy_waiting_names_the_dialogue_not_the_envoy(self, _r6_world):
        w = _r6_world
        w.dialogue_manager.push({"type": "terms_guidance", "blocking": False})
        _r6_letter(w, "Portugal", "open_borders")      # queued behind it
        with _r6_served(w) as client:
            reply = client.get("/diplomatic_preview").json()
        assert reply["dialogue_pending"] is True
        assert reply["dialogue_pending_name"] == "the terms you are drafting"
        assert reply["pending_envoy_count"] == 1
        assert reply["cabinet_locked"] is False        # no LETTER holds it shut

    def test_a_locking_letter_behind_the_dialogue_still_says_so(self, _r6_world):
        w = _r6_world
        w.dialogue_manager.push({"type": "terms_guidance", "blocking": False})
        _r6_letter(w, "Austria", "armistice")
        with _r6_served(w) as client:
            reply = client.get("/diplomatic_preview").json()
        assert reply["cabinet_locked"] is True and reply["cabinet_locked_by"] == ["Austria"]

    def test_the_notice_branches_on_the_flag(self):
        body = _r6_func(_r6_src("diplomacy_wizard.gd"), "_add_dialogue_gate_notice")
        assert "if pending_envoy_count > 0 and letter_locks:" in body
        assert 'elif dialogue_name != "":' in body
        # the Open Envoys button follows the same gate
        assert body.count("pending_envoy_count > 0 and letter_locks") == 2


# ══════════════════════════════════════════════════════════════════════════
# S14G-X22 — Not Now's tooltip and the click's echo claimed a lock a courtesy never held
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX22:
    """Cause: S14E-18's tooltip on the popup's Not Now button and its echo
    ("Setting aside Portugal's proposal - the Cabinet stays shut ...",
    `main.gd::_on_incoming_proposal_choice`) said the lock for EVERY letter -
    after S14G-D3 a lesser court's courtesy holds none, so the old words would
    have told the player something false at the very click.

    Fixed (same files): the tooltip and the echo say the lock only when the
    letter's `locks_cabinet` holds; a courtesy's tooltip, line under the
    buttons and echo say it waits in the mailbox until the turn ends and the
    Cabinet stays open."""

    def test_the_echo_says_the_lock_only_for_a_letter_that_holds_it(self):
        main = _r6_src("main.gd")
        body = _r6_func(main, "_on_incoming_proposal_choice")
        dismiss = body[body.index('if choice == "dismiss":'):body.index("# LV-3 (row EP F2)")]
        assert 'if bool(data.get("locks_cabinet", false)):' in dismiss
        assert "Setting aside %s's proposal — %s Click the envoy badge to revisit." in dismiss
        assert ("Setting aside %s's proposal — it waits in the mailbox until the turn ends, "
                "and the Cabinet stays open. Click the envoy badge to revisit.") in dismiss
        assert dismiss.index('if bool(data.get("locks_cabinet", false)):') \
            < dismiss.index("Utils.cabinet_shut_line(")
        # the moment letter's echo is untouched
        moment = dismiss[dismiss.index("if is_moment:"):dismiss.index("else:")]
        assert "cabinet_shut_line" not in moment and "locks_cabinet" not in moment

    def test_the_tooltips_carry_the_two_readings(self):
        show = _r6_func(_r6_src("incoming_proposal_popup.gd"), "show_proposal")
        arm = show[show.index("S14E-18 (S14f part 2): a set-aside letter still stands"):
                   show.index("# Button labels adapt to context")]
        assert arm.index("if locks_cabinet:") < arm.index("Utils.cabinet_shut_line(_lock_by_turn)")
        assert "it waits in the mailbox and the Cabinet stays open" in arm
        # a call to arms stands to its answer-by turn, and still says so
        assert 'int(data.get("answer_by_turn", 0)) if is_call_to_arms else 0' in arm


# ══════════════════════════════════════════════════════════════════════════
# S14G-X23 — every reader of the lock reads the one predicate
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX23:
    """The sweep of the lock's readers (what the wizard, the ledger's vassal
    chips, the region panel's Negotiate chip and the war HUD's roads ask):
    all of them ask `DialogueManager.has_current_turn_offers`, which now asks
    the one predicate - so a lesser court's courtesy blocks nothing anywhere.
    Pinned: `get_available_diplomatic_actions` (the wizard's action rows,
    which the Negotiate chip's `open_for_nation` and the ledger's vassal chips
    both call), `get_diplomatic_preview`, the nations list and the vassal
    ledger's `actions_blocked`."""

    def test_the_wizards_action_rows_open_for_a_courtesy_and_close_for_a_war_letter(self, _r6_world):
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        w = _r6_world
        _r6_letter(w, "Portugal", "open_borders")
        assert get_available_diplomatic_actions(w, "Prussia") != []
        w2 = _r6_world
        w2.dialogue_manager.remove_matching(lambda d: True)
        _r6_letter(w2, "Austria", "armistice")
        assert get_available_diplomatic_actions(w2, "Prussia") == []

    def test_the_vassal_ledgers_chips_are_not_suspended_by_a_courtesy(self, _r6_world):
        from backend.game_logic.diplomatic_ledger import _build_vassals
        w = _r6_world
        _r6_letter(w, "Portugal", "open_borders")
        with _r6_quiet():
            quiet = _build_vassals(w)
        assert quiet.get("actions_blocked") is False
        w2 = _r6_world
        w2.dialogue_manager.remove_matching(lambda d: True)
        _r6_letter(w2, "Austria", "armistice")
        with _r6_quiet():
            shut = _build_vassals(w2)
        assert shut.get("actions_blocked") is True

    def test_no_reader_keeps_its_own_copy_of_the_lock(self):
        """Every backend reader goes through `has_current_turn_offers` - none
        re-derives the lock from `CURRENT_TURN_OFFER_TYPES` itself except the
        two that need the CONTENT of a call to arms (`_cabinet_locked_until`)
        and the lapse path."""
        import re
        readers = []
        for path in (_R6_REPO / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if re.search(r"dialogue_pending\s*=\s*.*has_current_turn_offers", text):
                readers.append(path.name)
        assert sorted(readers) == ["diplomacy.py", "main.py"]


# ══════════════════════════════════════════════════════════════════════════
# row07
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 — row S14G-7 (October 26, 2026).
#
# S14G-7 (P2, DD-B's third measure): an armistice with Austria leaves Bavaria's
# war running — Austria takes the ground under the French corps, Berthier
# marches them home, and the terms said only a count. The preview read "Bavaria
# stays at war with Austria … her war runs on, and 7 French corps stand on
# Bavarian soil under the truce" (`diplomacy.allies_whose_war_runs_on` /
# `truce_followers_line` and the WARNING row of `get_peace_commitment_conflicts`)
# as one bullet among many: the count, not the consequence. Under an ARMISTICE
# France is not at war with Austria, so the corps cannot fight for the ally; the
# next enemy phase showed Austria storming Munich and Swabia with the corps
# standing there; a province that changes hands strands them
# (`corps_on_closed_soil`: "they may march out") and Berthier's road-home orders
# (`withdrawal.offer_road_home`, free, automatic) march them out ("put on the
# road home to Nivernais; 5 turns of safe passage") — so ONE dispatch said "may
# march out" and "already marched" about the same corps. A 2-AP march INTO the
# ally's province after the accept got no warning at the order. Sightings:
# diplomacy #7 (turn 5, action 105) and sea #6 (turn 7, action 117).
#
# The fix (this file pins it on the shipped 1805 board, France allied to
# Bavaria and at war with Austria, Ney and Davout at Swabia):
#
# * ONE sentence, `diplomacy.truce_runs_on_consequence`: "Your corps will not
#   fight for her under the truce; Austria may take her provinces where your
#   corps stand, and ground that changes hands puts them on the road home —
#   Berthier marches them out (up to 5 turns of safe passage) and none may enter it
#   again." The turns are the corridor's own formula
#   (`diplomacy.road_home_safe_passage_turns`: the longest march home plus
#   `EVACUATION_SLACK_TURNS`, backstopped by `EVACUATION_MAX_TURNS`). It ends
#   `truce_followers_line` (the armistice's dispatch line) and the `war_runs_on`
#   row of the confirm and the incoming letter — and the row LEADS the list.
# * A front note on a march into an ally's province a truce partner of ours is
#   at war with (`movement_executor.front_note`, from the one predicate
#   `diplomacy.truce_front_of_an_ally`), printed on the plain move's reply. The
#   strategic march's reply and the typed march's quote call the same helper
#   (wired by the orchestrator in wave 2 — their functions are another row's).
# * The dispatch's `corps_on_closed_soil` tail reads the corps' own standing
#   orders when the page is built (`dispatch.closed_soil_fate`): "Berthier has
#   already put Ney and Davout on the road home to Rhineland (4 turns of safe
#   passage), and no corps of ours may enter it again." when the free road-home
#   order stands, "they may march out, but no corps of ours may enter it again."
#   when it does not.
# * The sibling: `separate_peace_words` (and the incoming-peace and
#   joined-at-a-call rows) says the same consequence for an ally a separate
#   PEACE leaves fighting while our corps stand on her soil.
#
# Kept: the count's words (`test_dd1_s8_the_verbs` still pin them), severity
# WARNING (never HARD_STOP — the armistice is not refused), the AI's acceptance
# (it reads no text — player-only text, so the change is unconditional and
# there is no seam or lever).

_R7_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")

_R7_CONSEQUENCE_WORDS = (
    "Your corps will not fight for her under the truce",
    "Austria may take her provinces where your corps stand",
    "ground that changes hands puts them on the road home",
    "Berthier marches them out (up to 5 turns of safe passage)",
    "none may enter it again",
)


def _r7_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r7_boot():
    from backend.models.world_state import WorldState
    with _r7_quiet():
        return WorldState.from_scenario(str(_R7_SCENARIO))


@pytest.fixture
def _r7_world(_r7_boot):
    """The shipped 1805 board; Ney and Davout stand at Swabia (Bavarian soil),
    Bernadotte already at Franconia (Bavarian soil) — three corps on an
    ally's soil, France at war with Austria, Bavaria allied to France."""
    from backend.models.world_state import WorldState
    world = WorldState.from_dict(json.loads(json.dumps(_r7_boot.to_dict(), default=str)))
    assert world.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"
    assert world.get_diplomatic_state("France", "Austria") == "WAR"
    assert world.get_diplomatic_state("Bavaria", "Austria") == "WAR"
    world.marshals["Ney"].location = "Swabia"
    world.marshals["Davout"].location = "Swabia"
    assert world.regions["Swabia"].controller == "Bavaria"
    return world


def _r7_sign_the_truce(world):
    """France and Austria sign the armistice through the one ratifier."""
    from backend.game_logic import diplomacy as D
    variant = D.armistice_variant_for(world, "France", "Austria")
    with _r7_quiet():
        event = world._ratify_treaty({"type": variant, "proposer_nation": "France",
                                      "target_nation": "Austria", "sweeteners": [],
                                      "demands": [], "clauses": []})
    assert event and event.get("type") != "diplomatic_treaty_failed", event
    assert world.get_diplomatic_state("France", "Austria") == "ARMISTICE"


def _r7_queued(world, event_type):
    return [e for e in world.pending_dispatch_events
            if (e.get("event_type") or e.get("type")) == event_type]


def _r7_move(world, marshal, target):
    from backend.commands.executor import CommandExecutor
    with _r7_quiet():
        return CommandExecutor().execute({
            "command": {"raw_input": f"{marshal}, move to {target}", "marshal": marshal,
                        "action": "move", "target": target},
        }, {"world": world})


def _r7_the_ground_changes_hands(world, region="Swabia", to="Austria"):
    """Austria storms `region` under the truce, as the sighting's enemy phase."""
    from backend.models.world_state import announce_third_party_capture
    old = world.regions[region].controller
    world.regions[region].controller = to
    world.invalidate_active_nations_cache()
    announce_third_party_capture(world, region, old, to)


# ══════════════════════════════════════════════════════════════════════════
# S14G-7 — the truce says what it does to the corps
# ══════════════════════════════════════════════════════════════════════════

class TestS14G7:
    """Reproduced on the shipped board: Ney and Davout at Swabia, Bernadotte
    at Franconia, an armistice with Austria drafted. The OLD sentence read
    "Bavaria stays at war with Austria — an ally, not a client: her war runs
    on, and 3 French corps stand on Bavarian soil under the truce." and
    stopped; every surface ends on the consequence now."""

    def test_the_truce_line_says_the_consequence_after_the_count(self, _r7_world):
        from backend.game_logic import diplomacy as D
        line = D.truce_followers_line(_r7_world, "France", "Austria")
        # the count is kept, word for word
        assert "Bavaria stays at war with Austria" in line
        assert "3 French corps stand on Bavarian soil under the truce." in line
        for words in _R7_CONSEQUENCE_WORDS:
            assert words in line, (words, line)
        assert line.index("stand on Bavarian soil") < line.index("Your corps will not fight")
        assert line.endswith("none may enter it again.")

    def test_the_confirm_row_leads_the_list_and_ends_on_the_consequence(self, _r7_world):
        from backend.game_logic import diplomacy as D
        snap = D.build_war_context_snapshot(_r7_world, "France", "Austria", "armistice_winning")
        rows = snap["commitment_conflicts"]
        assert [r["conflict_type"] for r in rows][0] == "war_runs_on", rows
        assert len(rows) >= 2, "the bloc note rides behind it; the order is the point"
        row = rows[0]
        assert row["severity"] == "WARNING", "a truce is never refused (no HARD_STOP)"
        assert row["affected_entity"] == "Bavaria"
        assert "Bavaria stays at war with Austria under this truce" in row["display"]
        assert "3 French corps stand on Bavarian soil under the truce." in row["display"]
        for words in _R7_CONSEQUENCE_WORDS:
            assert words in row["display"], (words, row["display"])
        assert row["display"].endswith("none may enter it again.")
        assert row["detail"]["safe_passage_turns"] == 5
        assert isinstance(row["detail"]["safe_passage_turns"], int)

    def test_the_conflicts_put_the_row_first_whatever_the_order_built(self, _r7_world, monkeypatch):
        """A bargain-breach row built AFTER the loop and a bloc row do not
        push it down: a stable sort keeps every other row's place."""
        from backend.game_logic import diplomacy as D
        monkeypatch.setattr(D, "_get_live_bargains", lambda world: [{
            "promiser": "France", "target_enemy": "Austria", "beneficiary": "Russia",
            "claim_term": {"claim_region": "Tyrol"}, "id": "b1"}])
        conflicts = D.get_peace_commitment_conflicts(_r7_world, "France", "Austria", [], truce=True)
        kinds = [c["conflict_type"] for c in conflicts]
        assert kinds[0] == "war_runs_on" and "bargain_breach" in kinds, kinds

    def test_the_incoming_armistice_letter_carries_the_same_words(self, _r7_world):
        """The AI proposes the truce (Austria's letter): the letter's
        `commitment_conflicts` lead with the same row, the same words."""
        from backend.game_logic.mailbox_payloads import attach_peace_preview
        payload = attach_peace_preview(_r7_world, {}, "Austria", {
            "type": "armistice_winning", "proposer_nation": "Austria",
            "target_nation": "France", "sweeteners": [], "demands": [], "clauses": []})
        rows = payload["commitment_conflicts"]
        assert rows[0]["conflict_type"] == "war_runs_on", rows
        for words in _R7_CONSEQUENCE_WORDS:
            assert words in rows[0]["display"], (words, rows[0]["display"])

    def test_the_dispatch_names_the_consequence_on_the_truce(self, _r7_world):
        from backend.game_logic.dispatch import _format_dispatch_event_text
        _r7_sign_the_truce(_r7_world)
        (queued,) = _r7_queued(_r7_world, "armistice_ratified")
        text = _format_dispatch_event_text("armistice_ratified", queued["template_vars"])
        assert "A truce with Austria" in text
        assert "stand on Bavarian soil under the truce" in text
        for words in _R7_CONSEQUENCE_WORDS:
            assert words in text, (words, text)
        assert "{followers}" not in text

    def test_the_quoted_passage_is_the_corridors_own(self, _r7_world):
        """The N the truce quotes is the N Berthier then writes: for the corps
        whose ground changes hands (Ney and Davout at Swabia, one march from
        home) the quote equals the standing grant's turns left once Austria
        takes Swabia and the tick runs; the line's own figure — the farthest
        corps that stands on her soil (Bernadotte at Franconia, two marches) —
        is the ceiling, said "up to"."""
        from backend.game_logic import diplomacy as D
        from backend.game_logic import withdrawal as W
        quoted = D.road_home_safe_passage_turns(_r7_world, "France", ["Ney", "Davout"])
        ceiling = D.road_home_safe_passage_turns(
            _r7_world, "France", ["Ney", "Davout", "Bernadotte"])
        home = W.cached_home_zone(_r7_world, "France")
        assert quoted == 1 + W.EVACUATION_SLACK_TURNS == 4
        assert ceiling == 2 + W.EVACUATION_SLACK_TURNS == 5
        assert W.distance_home_from(_r7_world, "France", "Swabia", home, with_grant=False) == 1
        assert W.distance_home_from(_r7_world, "France", "Franconia", home, with_grant=False) == 2
        _r7_sign_the_truce(_r7_world)
        _r7_the_ground_changes_hands(_r7_world)
        with _r7_quiet():
            W.process_evacuation_grants(_r7_world)
        reading = W.passage_reading(_r7_world, "France")
        assert reading["turns_left"] == quoted, reading
        assert reading["turns_left"] <= ceiling

    def test_no_corps_on_her_soil_says_only_that_they_will_not_fight(self, _r7_world):
        from backend.game_logic import diplomacy as D
        for m in _r7_world.marshals.values():
            if m.nation == "France" and m.location in ("Swabia", "Franconia", "Munich"):
                m.location = "Paris"
        line = D.truce_followers_line(_r7_world, "France", "Austria")
        assert "no corps of ours stands on Bavarian soil" in line
        assert "Your corps will not fight for her under the truce; Austria may take her provinces." in line
        assert "road home" not in line, "nothing stands there to be marched out"

    def test_a_march_into_the_ally_after_the_accept_prints_the_front_note(self, _r7_world):
        """The sea road's 2-AP march to Swabia ordered AFTER the accept: the
        reply said its supply and nothing of the front."""
        _r7_sign_the_truce(_r7_world)
        _r7_world.marshals["Soult"].location = "Lorraine"
        result = _r7_move(_r7_world, "Soult", "Swabia")
        assert result["success"], result
        assert ("Swabia is Bavaria's front — Austria, under truce with us, is at war "
                "with her; a corps there will not fight, and marches home if the "
                "ground changes hands.") in result["message"], result["message"]

    def test_the_note_is_for_a_front_only(self, _r7_world):
        """Not at war with the truce partner: no note. Not an ally's
        province: no note. Not the player's corps: no note."""
        from backend.commands.movement_executor import front_line, front_note
        ney = _r7_world.marshals["Ney"]
        assert front_line(_r7_world, ney, "Swabia") == "", "no truce yet — Austria is at war with us"
        _r7_sign_the_truce(_r7_world)
        assert front_line(_r7_world, ney, "Swabia").startswith("Swabia is Bavaria's front")
        assert front_note(_r7_world, ney, "Swabia") == "\n" + front_line(_r7_world, ney, "Swabia")
        assert front_line(_r7_world, ney, "Lorraine") == "", "French soil"
        assert front_line(_r7_world, ney, "Tyrol") == "", "Austria's own"
        austrian = next(m for m in _r7_world.marshals.values() if m.nation == "Austria")
        assert front_line(_r7_world, austrian, "Swabia") == "", "the AI's corps read nothing (Rule 5)"

    def test_the_dispatch_says_already_when_berthier_has_put_them_on_the_road(self, _r7_world):
        """Swabia falls under the truce; the free road-home order is written
        at the tick, AFTER the capture queued the line. The page said "they
        may march out" in one line and "put on the road home to …" in the
        next; the closed-soil line now reads the orders when it is BUILT."""
        from backend.game_logic.dispatch import _build_diplomatic_events_section
        _r7_sign_the_truce(_r7_world)
        _r7_the_ground_changes_hands(_r7_world)
        (queued,) = _r7_queued(_r7_world, "corps_on_closed_soil")
        assert queued["template_vars"]["fate"] == (
            "they may march out, but no corps of ours may enter it again."), (
            "queued before the tick: no order stands yet")
        with _r7_quiet():
            from backend.game_logic.withdrawal import process_evacuation_grants
            process_evacuation_grants(_r7_world)
        assert _r7_world.marshals["Ney"].strategic_order is not None
        rows = _build_diplomatic_events_section(_r7_world, "France")
        (line,) = [r["text"] for r in rows if r["type"] == "corps_on_closed_soil"]
        assert "Ney and Davout stand on Swabia, now Austria's soil — an armistice stands between us:" in line
        assert "Berthier has already put Ney and Davout on the road home to " in line, line
        assert "(4 turns of safe passage), and no corps of ours may enter it again." in line, line
        assert "may march out" not in line, "one line, one story"

    def test_the_dispatch_says_may_march_out_while_no_road_order_stands(self, _r7_world):
        from backend.game_logic.dispatch import _build_diplomatic_events_section
        _r7_sign_the_truce(_r7_world)
        _r7_the_ground_changes_hands(_r7_world)
        rows = _build_diplomatic_events_section(_r7_world, "France")
        (line,) = [r["text"] for r in rows if r["type"] == "corps_on_closed_soil"]
        assert line.endswith("they may march out, but no corps of ours may enter it again."), line
        assert "already" not in line


class TestS14GX28:
    """S14G-X28 — the sibling in `movement_executor`: a RETREAT onto an ally's
    front (`Ney, retreat to Swabia` with a truce of ours leaving Bavaria's war
    running) put the corps on the front with the pay note and nothing of the
    front, as the plain move did before S14G-7."""

    def _retreat(self, world):
        """Ney at Franconia with a Russian corps (at war with us) beside him
        — in danger, so the free retreat is open — retreats to Swabia."""
        from backend.commands.executor import CommandExecutor
        world.marshals["Ney"].location = "Franconia"
        russian = next(m for m in world.marshals.values() if m.nation == "Russia")
        russian.location = "Franconia"
        with _r7_quiet():
            return CommandExecutor().execute({
                "command": {"raw_input": "Ney, retreat to Swabia", "marshal": "Ney",
                            "action": "retreat", "target": "Swabia"}}, {"world": world})

    def test_a_retreat_to_the_allys_front_says_the_front(self, _r7_world, monkeypatch):
        # The mood variance (`objection_v2.apply_mood_variance`, ~10% up a
        # level) sometimes made Ney object to the retreat ("Retreat? We can
        # still fight!") and stay put - a roll of the shared `random` state, so
        # the test failed after other modules had seeded it. Held to the
        # evaluated level in THIS test only: he never objects.
        monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                            lambda concern: concern)
        _r7_sign_the_truce(_r7_world)
        result = self._retreat(_r7_world)
        assert result["success"], result
        assert _r7_world.marshals["Ney"].location == "Swabia"
        assert ("Swabia is Bavaria's front — Austria, under truce with us, is at war "
                "with her; a corps there will not fight, and marches home if the "
                "ground changes hands.") in result["message"], result["message"]

    def test_a_retreat_before_the_truce_says_no_front(self, _r7_world):
        result = self._retreat(_r7_world)
        assert result["success"], result
        assert "'s front" not in result["message"], result["message"]


class TestS14G7ClosedSoilFate:
    """`dispatch.closed_soil_fate` on its own: one corps, two corps, a mix."""

    def _road(self, world, name, dest="Rhineland"):
        from backend.game_logic.withdrawal import ROAD_HOME_COMMAND
        from backend.models.marshal import StrategicOrder
        world.marshals[name].strategic_order = StrategicOrder(
            command_type="MOVE_TO", target=dest, target_type="region",
            started_turn=int(world.current_turn), original_command=ROAD_HOME_COMMAND, path=[dest])

    def test_a_corps_with_no_road_order_may_march_out(self, _r7_world):
        from backend.game_logic.dispatch import closed_soil_fate
        assert closed_soil_fate(_r7_world, ["Ney"], "he") == (
            "he may march out, but no corps of ours may enter it again.")

    def test_a_corps_a_players_own_order_holds_is_not_on_the_road(self, _r7_world):
        from backend.game_logic.dispatch import closed_soil_fate
        from backend.models.marshal import StrategicOrder
        _r7_world.marshals["Ney"].strategic_order = StrategicOrder(
            command_type="HOLD", target="Swabia", target_type="region",
            started_turn=int(_r7_world.current_turn), original_command="Ney, hold Swabia")
        assert closed_soil_fate(_r7_world, ["Ney"], "he").startswith("he may march out")

    def test_one_corps_on_the_road_is_named_with_where(self, _r7_world):
        from backend.game_logic.dispatch import closed_soil_fate
        self._road(_r7_world, "Ney")
        fate = closed_soil_fate(_r7_world, ["Ney"], "he")
        assert fate == ("Berthier has already put Ney on the road home to Rhineland, "
                        "and no corps of ours may enter it again."), fate

    def test_a_mix_says_both_without_contradiction(self, _r7_world):
        from backend.game_logic.dispatch import closed_soil_fate
        self._road(_r7_world, "Ney")
        fate = closed_soil_fate(_r7_world, ["Ney", "Davout"], "they")
        assert fate == ("Berthier has already put Ney on the road home to Rhineland; "
                        "Davout may march out. No corps of ours may enter it again."), fate

    def test_two_roads_two_destinations(self, _r7_world):
        from backend.game_logic.dispatch import closed_soil_fate
        self._road(_r7_world, "Ney", "Rhineland")
        self._road(_r7_world, "Davout", "Lorraine")
        fate = closed_soil_fate(_r7_world, ["Ney", "Davout"], "they")
        assert "on the road home — Ney to Rhineland, Davout to Lorraine, and" in fate, fate

    def test_an_event_queued_before_the_tail_was_a_variable_still_renders(self):
        from backend.game_logic.dispatch import _format_dispatch_event_text
        text = _format_dispatch_event_text("corps_on_closed_soil", {
            "marshals": "Ney", "stand": "stands", "they": "he", "region": "Swabia",
            "new_display": "Austria", "reason": "an armistice stands between us"})
        assert text == ("Ney stands on Swabia, now Austria's soil — an armistice stands "
                        "between us: he may march out, but no corps of ours may enter it again.")


class TestS14GX27:
    """S14G-X27 — the sibling `separate_peace_words`: an ally a separate PEACE
    leaves fighting ("Bavaria stays at war with Austria after this separate
    peace — she fights on alone; it costs -10 relation with her.") said only a
    state while our corps stood on her soil, exactly as the truce's count did.
    The same fact (an ally left at war, our corps on her soil) carries the same
    consequence — "under this peace"."""

    @pytest.fixture
    def _left(self, _r7_world, monkeypatch):
        """France does not lead the war: Bavaria is LEFT FIGHTING, not carried."""
        monkeypatch.setattr("backend.game_logic.settlement_ratify.carried_in_allies",
                            lambda world, proposer, target: [])
        return _r7_world

    def test_the_left_ally_with_our_corps_on_her_soil_carries_the_consequence(self, _left):
        from backend.game_logic import diplomacy as D
        words = D.separate_peace_words(_left, "France", "Austria")
        assert words["left"] == ["Bavaria"] and words["carried"] == []
        sentence = words["per_ally"]["Bavaria"]
        assert sentence.startswith("Bavaria stays at war with Austria after this separate peace "
                                   "— she fights on alone; it costs ")
        assert ("Your corps will not fight for her under this peace; Austria may take her "
                "provinces where your corps stand, and ground that changes hands puts them "
                "on the road home — Berthier marches them out (up to 5 turns of safe passage) and "
                "none may enter it again.") in sentence, sentence
        assert words["consequence"]["Bavaria"] in words["display"] == words["chip"]

    def test_the_left_ally_with_none_of_our_corps_there_says_nothing_more(self, _left):
        from backend.game_logic import diplomacy as D
        for m in _left.marshals.values():
            if m.nation == "France" and m.location in ("Swabia", "Franconia", "Munich"):
                m.location = "Paris"
        words = D.separate_peace_words(_left, "France", "Austria")
        assert words["consequence"] == {}
        assert words["display"].endswith("relation with her.")

    def test_the_incoming_peace_row_and_the_confirm_row_carry_it_too(self, _left):
        from backend.game_logic import diplomacy as D
        incoming = D.get_peace_commitment_conflicts(_left, "France", "Austria", [], incoming=True)
        (row,) = [c for c in incoming if c["conflict_type"] == "paradox"]
        assert row["display"].endswith("none may enter it again."), row["display"]
        assert "Your corps will not fight for her under this peace" in row["display"]
        outgoing = D.get_peace_commitment_conflicts(_left, "France", "Austria", [])
        (row,) = [c for c in outgoing if c["conflict_type"] == "paradox"]
        assert "Berthier marches them out (up to 5 turns of safe passage)" in row["display"]

    def test_a_carried_ally_says_nothing_of_the_road(self, _r7_world):
        """The peace ends her war in the same instrument: nothing runs on."""
        from backend.game_logic import diplomacy as D
        words = D.separate_peace_words(_r7_world, "France", "Austria")
        assert words["carried"] == ["Bavaria"] and words["consequence"] == {}
        assert "road home" not in words["display"]


# ══════════════════════════════════════════════════════════════════════════
# row08
# ══════════════════════════════════════════════════════════════════════════
# S14G-8 (Pre-Deploy S14h part 1, October 26, 2026) — "Satisfy their design".
#
# The cause as traced (DD-B's third measure, diplomacy #1, turn 1, action 22,
# `docs/audits/dd_b/diplomacy_2026_10_25/frames/0022.jpg`): Talleyrand's counsel
# "Satisfy their design (Britain)" became the action `expand_options` carrying
# only `target_nation` — the design's title and the provinces it covets were
# dropped — and the executor re-routed it to the vague standstill menu ("war with
# Britain is at a standstill — Propose peace / Press advantage / Wait"). The
# menu's body was two sentences (its option descriptions rendered as tooltips
# alone), its "Propose peace" was an `execute_proposal` that SENT a plain peace
# at once (3 of the 5 DP gone) with no terms, no acceptance band and no price
# shown first, and at war score +0 the suggested terms never include the coveted
# province (the pipeline authors the cession only at `war_score < -20`), so the
# "peace" could not satisfy the design it was advised to satisfy.
#
# What the fix does (player-only text and routing; no seam — the AI never reads
# a dialogue, and `generate_suggested_terms`' coveted-cession arm is lifted into
# `inject_coveted_cession` byte for byte):
#
# * the counsel carries the design (`design_id`, `design_title`, `coveted`) and
#   its tooltip says what the button opens and what it costs (3 DP, shown
#   before anything is sent);
# * its `expand_options` arm opens a `proposal_confirm` PRE-LOADED with the
#   peace and the cession of the coveted province France holds
#   (`design_confirm_dialogue` → `design_peace_terms`), the confirm's own
#   estimate and DP price beside it, nothing spent;
# * every generic-menu `execute_proposal` option (T1 … T5 and the fallback) now
#   OPENS that confirm instead of sending (`_open_confirm_for_menu_option`), and
#   the menu's body prints each option — description, DP price, terms — so the
#   choice is made on what it is (`_with_menu_body`); the Godot option list
#   renders the description as a line under each button;
# * DDB-9's `_stamp_menu_sends` still arrives a refused send disabled, and the
#   body says why.
#
# Siblings: S14G-X30 (T2's "Offer concessions" sent the SAME package as "Sue for
# peace" under a label that promised gold or territory — it opens the confirm's
# own sweetened round); S14G-X31 (the other four open_proposal counsels land on
# the same menu and now show a body and open the confirm); S14G-X32 (the
# confirm's "Harsher" / "More generous" redrafted from nothing — striking a
# cession the pipeline does not author at this war score — they build on the
# package now).

_R8_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")
_R8_POPUP = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
             / "scripts" / "proposal_confirm_popup.gd")


def _r8_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r8_boot():
    from backend.models.world_state import WorldState
    with _r8_quiet():
        return WorldState.from_scenario(str(_R8_SCENARIO))


@pytest.fixture
def _r8_world(_r8_boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(_r8_boot.to_dict(), default=str)))


def _r8_executor():
    from backend.commands.executor import CommandExecutor
    with _r8_quiet():
        return CommandExecutor()


def _r8_advice(world):
    """The war room's advisory dialogue on the live board, mounted as the
    client's open dialogue (the Cabinet's counsel card)."""
    from backend.game_logic.diplomatic_advisory import generate_advisory
    with _r8_quiet():
        advice = generate_advisory(None, "assess_situation", world)
    world.dialogue_manager.replace(advice)
    return advice


def _r8_click(world, executor, index: int) -> dict:
    """Answer the top dialogue by 1-based option index, as the client does."""
    with _r8_quiet():
        return executor.handle_diplomatic_dialogue_response(index, {"world": world})


def _r8_index_of(dialogue: dict, action: str, label: str = "") -> int:
    for n, opt in enumerate(dialogue["options"], start=1):
        if opt["action"] == action and (not label or opt["label"] == label):
            return n
    raise AssertionError(f"no {action!r} option {label!r} in {[o['label'] for o in dialogue['options']]}")


def _r8_option(dialogue: dict, action: str, label: str = "") -> dict:
    return dialogue["options"][_r8_index_of(dialogue, action, label) - 1]


def _r8_vague(world, executor, target: str) -> dict:
    """The typed vague "propose to <target>" — the road that lands on the
    generic menu (T1 … T5)."""
    data = {"action": "diplomatic_proposal", "diplomat": "Talleyrand",
            "target_nation": target, "proposal_type": None, "clauses": [],
            "is_question": False, "has_diplomatic_keywords": True,
            "tone": "propose", "raw_text": f"propose to {target}"}
    with _r8_quiet():
        result = executor._execute_diplomatic_proposal(data, world)
    return result["diplomatic_dialogue"]


def _r8_stamp_score(world, target: str, france_score: int) -> None:
    key = world._make_diplo_key("France", target)
    world.war_scores[key] = france_score if key.split("|")[0] == "France" else -france_score


def _r8_sweeteners(terms: dict, kind: str) -> list:
    return [s for s in terms.get("sweeteners", []) if s.get("type") == kind]


# ══════════════════════════════════════════════════════════════════════════
# S14G-8 — the counsel and the confirm it opens
# ══════════════════════════════════════════════════════════════════════════

class TestS14G8:
    """The sighting, reproduced on the shipped 1805 board at turn 1: France at
    war with Britain, Britain's design "The Low Countries" live, Flanders held
    by France. Old reading: the counsel's option was `expand_options` with
    `terms == {"target_nation": "Britain"}`; choosing it mounted a
    `proposal_options` card ("at a standstill") and its first button sent a
    plain Peace Treaty for 3 DP."""

    def test_the_counsel_carries_the_design_and_its_coveted_province(self, _r8_world):
        advice = _r8_advice(_r8_world)
        counsel = advice["options"][0]
        assert counsel["label"] == "Satisfy their design (Britain)"
        assert counsel["action"] == "expand_options"
        terms = counsel["terms"]
        assert terms["target_nation"] == "Britain"
        assert terms["design_id"] == "low_countries"
        assert terms["design_title"] == "The Low Countries"
        assert terms["coveted"] == ["Flanders"]
        # the recommendation record (context) carries the same design
        design = advice["context"]["recommendation"]["design"]
        assert design == {"target_nation": "Britain", "design_id": "low_countries",
                          "design_title": "The Low Countries", "coveted": ["Flanders"]}

    def test_the_counsel_says_what_the_button_opens_and_what_it_costs(self, _r8_world):
        """Quote first: the tooltip names the province, the cession, the DP
        price (the confirm's own figure) and that nothing is sent."""
        from backend.game_logic.diplomatic_dialogue import proposal_dp_cost
        advice = _r8_advice(_r8_world)
        description = advice["options"][0]["description"]
        price = proposal_dp_cost(_r8_world, "Britain", "peace")
        assert price == 3 and isinstance(price, int)
        assert "Flanders" in description
        assert "cession" in description
        assert f"{price} DP" in description
        assert "before anything is sent" in description
        # and the prose of the counsel names the province it would cede
        assert "We hold what their court wants — Flanders;" in advice["talleyrand_text"]

    def test_choosing_it_opens_a_confirm_with_the_cession_and_spends_nothing(self, _r8_world):
        world = _r8_world
        executor = _r8_executor()
        _r8_advice(world)
        dp_before = int(world.diplomatic_points)
        reply = _r8_click(world, executor, 1)
        assert reply["success"] is True
        dialogue = reply["diplomatic_dialogue"]
        # the OLD reading: the vague standstill menu
        assert dialogue["type"] != "proposal_options"
        assert "at a standstill" not in dialogue["talleyrand_text"]
        # the NEW one: a confirm pre-loaded with the peace and the cession
        assert dialogue["type"] == "proposal_confirm"
        send = _r8_option(dialogue, "execute_proposal")
        assert send["terms"]["type"] == "peace"
        cession = _r8_sweeteners(send["terms"], "territory_cede")
        assert cession and cession[0]["regions"] == ["Flanders"]
        assert "territory_flanders" in send["terms"]["clauses"]
        lines = dialogue["proposal_terms_summary"]
        assert any("Flanders" in line for line in lines), lines
        assert any(row.get("display_label") == "France cedes Flanders to Britain"
                   for row in dialogue["annotated_terms"])
        # the court's reading and the price stand before anything is sent
        assert isinstance(dialogue["acceptance_estimate"], int)
        assert 0 <= dialogue["acceptance_estimate"] <= 100
        assert dialogue["acceptance_outcome"] in ("ACCEPT", "REJECT", "COUNTER_OFFER")
        assert dialogue["dp_cost"] == 3
        # the design rides the dialogue's context
        assert dialogue["context"]["design"] == {
            "design_id": "low_countries", "design_title": "The Low Countries",
            "coveted": ["Flanders"], "ceded": "Flanders"}
        # the lead line names the court, the design and the province
        head = dialogue["talleyrand_text"]
        assert "The Low Countries" in head and "Flanders" in head
        assert "Nothing leaves until you send it." in head
        # NOTHING was spent or sent
        assert int(world.diplomatic_points) == dp_before
        assert world.proposal_in_transit is None
        # the mounted dialogue is the confirm
        assert world.dialogue_manager.peek()["type"] == "proposal_confirm"

    def test_the_cession_is_what_the_estimate_reads(self, _r8_world):
        """The design is IN the priced package: the confirm's estimate beats the
        plain peace's (0 on this board — the old send's figure) because the
        estimator credits a design advanced (`agenda_acceptance_mod`)."""
        world = _r8_world
        executor = _r8_executor()
        _r8_advice(world)
        design = _r8_click(world, executor, 1)["diplomatic_dialogue"]
        assert design["acceptance_estimate"] > 0
        assert world.dialogue_manager.pop() is not None
        plain = _r8_vague(world, executor, "Britain")
        assert plain["type"] == "proposal_options"
        plain_confirm = _r8_click(world, executor, 1)["diplomatic_dialogue"]
        assert plain_confirm["type"] == "proposal_confirm"
        assert not _r8_sweeteners(_r8_option(plain_confirm, "execute_proposal")["terms"],
                                  "territory_cede")
        assert design["acceptance_estimate"] > plain_confirm["acceptance_estimate"]

    def test_the_send_is_the_confirms_own_and_carries_the_design(self, _r8_world):
        world = _r8_world
        world.talleyrand_defiance_cooldown = 9  # no sabotage roll on the send
        executor = _r8_executor()
        _r8_advice(world)
        dialogue = _r8_click(world, executor, 1)["diplomatic_dialogue"]
        assert int(world.diplomatic_points) == 5
        sent = _r8_click(world, executor, _r8_index_of(dialogue, "execute_proposal"))
        assert sent["success"] is True
        assert "3 DP spent" in sent["message"]
        assert int(world.diplomatic_points) == 2
        proposal = world.proposal_in_transit["proposal"]
        assert proposal["type"] == "peace" and proposal["target_nation"] == "Britain"
        assert _r8_sweeteners(proposal, "territory_cede")[0]["regions"] == ["Flanders"]

    def test_the_same_road_serves_every_court_whose_design_we_can_satisfy(self, _r8_world):
        """Austria's "Redeem Italy" (Milan, Piedmont, Savoy — France holds
        Savoy directly): the confirm cedes the province France actually holds,
        and a design that is not table-satisfiable (Russia's Arbiter of Europe)
        yields no confirm at all — the arm falls back to the menu."""
        from backend.game_logic.diplomatic_dialogue import design_confirm_dialogue
        world = _r8_world
        with _r8_quiet():
            austria = design_confirm_dialogue(world, "Austria", {"design_id": "redeem_italy"})
            russia = design_confirm_dialogue(world, "Russia", {"design_id": "arbiter_of_europe"})
            stale = design_confirm_dialogue(world, "Austria", {"design_id": "some_other_design"})
        assert russia is None and stale is None
        assert austria["type"] == "proposal_confirm"
        terms = _r8_option(austria, "execute_proposal")["terms"]
        assert _r8_sweeteners(terms, "territory_cede")[0]["regions"] == ["Savoy"]
        assert austria["context"]["design"]["design_title"] == "Redeem Italy"
        assert isinstance(austria["dp_cost"], int) and isinstance(austria["acceptance_estimate"], int)
        assert world.proposal_in_transit is None and int(world.diplomatic_points) == 5

    def test_a_stale_counsel_falls_back_to_the_menu_and_the_menu_has_a_body(self, _r8_world):
        """The war ended between the counsel and the click: nothing to satisfy
        at the table — the arm falls back to the generic menu, never a crash."""
        world = _r8_world
        executor = _r8_executor()
        _r8_advice(world)
        key = world._make_diplo_key("France", "Britain")
        world.diplomatic_states[key] = "PEACE"
        reply = _r8_click(world, executor, 1)
        dialogue = reply["diplomatic_dialogue"]
        assert dialogue["type"] == "proposal_options"
        assert "The paths before us, Sire:" in dialogue["talleyrand_text"]

    def test_the_generic_menus_propose_peace_opens_the_confirm_it_no_longer_sends(self, _r8_world):
        """The typed vague "propose to Britain" lands on the same T3 card; its
        first button was the plain 3-DP send."""
        world = _r8_world
        executor = _r8_executor()
        menu = _r8_vague(world, executor, "Britain")
        assert menu["type"] == "proposal_options"
        assert menu["talleyrand_text"].startswith("Sire, the war with Britain is at a standstill.")
        dp_before = int(world.diplomatic_points)
        reply = _r8_click(world, executor, _r8_index_of(menu, "execute_proposal", "Propose peace"))
        assert reply["success"] is True
        confirm = reply["diplomatic_dialogue"]
        assert confirm["type"] == "proposal_confirm"
        assert "\"Propose peace\"" in confirm["talleyrand_text"]
        assert confirm["dp_cost"] == 3 and isinstance(confirm["acceptance_estimate"], int)
        assert int(world.diplomatic_points) == dp_before
        assert world.proposal_in_transit is None
        # the send is the confirm's own, and it spends there
        world.talleyrand_defiance_cooldown = 9
        sent = _r8_click(world, executor, _r8_index_of(confirm, "execute_proposal"))
        assert sent["success"] is True
        assert int(world.diplomatic_points) == dp_before - 3
        assert world.proposal_in_transit is not None

    def test_the_menus_body_prints_each_option_its_price_and_its_terms(self, _r8_world):
        world = _r8_world
        menu = _r8_vague(world, _r8_executor(), "Britain")
        text = menu["talleyrand_text"]
        assert "The paths before us, Sire:" in text
        for option in menu["options"]:
            assert option["label"] in text
            assert option["description"] in text
        peace = next(line for line in text.splitlines() if line.startswith("• Propose peace"))
        assert "End the bloodshed on balanced terms." in peace
        assert "Terms: Peace Treaty (end state of war)." in peace
        assert "3 DP to send; the draft opens for your review first." in peace
        # a dismissal carries no price line
        wait = next(line for line in text.splitlines() if line.startswith("• Wait"))
        assert "DP" not in wait

    def test_the_menus_dp_is_the_confirms_dp_for_every_proposal_type(self, _r8_world):
        """One price: the helper the menu body and the counsel tooltip quote is
        the figure `_enrich_proposal_summary` prints on the confirm."""
        from backend.game_logic.diplomatic_dialogue import (
            confirm_dialogue_for_terms, proposal_dp_cost,
        )
        world = _r8_world
        for target, ptypes in (("Britain", ("peace", "armistice")),
                               ("Prussia", ("alliance", "non_aggression",
                                            "open_borders", "vassalage"))):
            for ptype in ptypes:
                with _r8_quiet():
                    confirm = confirm_dialogue_for_terms(world, target, ptype, None)
                assert confirm["dp_cost"] == proposal_dp_cost(world, target, ptype), (target, ptype)

    def test_the_picker_renders_each_description_under_its_button(self):
        """The client's option list: the description stands as a line under the
        button (picker only), the button's own label and tooltip unchanged."""
        src = _R8_POPUP.read_text(encoding="utf-8")
        start = src.index("var is_options_picker = (dtype == \"proposal_options\")")
        block = src[start:src.index("# Re-front Slice 2", start)]
        assert "btn.text = original_label" in block
        assert "btn.tooltip_text = original_tooltip" in block
        assert 'if is_options_picker and original_tooltip != "":' in block
        assert "var cell := VBoxContainer.new()" in block
        assert "cell.add_child(btn)" in block
        assert "var note := Label.new()" in block
        assert "note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART" in block
        assert 'note.theme_type_variation = &"Caption"' in block
        # a shut option's own reason in place of its description
        assert "disabled_reason if (not available and disabled_reason != \"\") else original_tooltip" in block
        assert "button_container.add_child(cell)" in block
        # every other dialogue type still adds the bare button
        assert "else:\n\t\t\tbutton_container.add_child(btn)" in block
        # and every line is tab-indented (GDScript)
        for line in block.splitlines():
            assert not line.startswith(" "), repr(line)


# ══════════════════════════════════════════════════════════════════════════
# S14G-X30 — T2's "Offer concessions" was the same package as "Sue for peace"
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX30:
    """Sibling found by the body: the menu now prints each option's terms, and
    T2's two options read IDENTICAL — "Offer concessions" ("Sweeten the deal
    with gold or territory") was an `execute_proposal` on the very same drafted
    peace as "Sue for peace". It is the confirm's own sweetened round now."""

    def _t2(self, world, executor):
        _r8_stamp_score(world, "Britain", -50)
        menu = _r8_vague(world, executor, "Britain")
        assert menu["talleyrand_text"].startswith("Sire, our position against Britain is... precarious.")
        return menu

    def test_the_concessions_option_opens_a_sweetened_draft_not_the_same_package(self, _r8_world):
        from backend.game_logic.diplomatic_templates import same_package
        world = _r8_world
        executor = _r8_executor()
        menu = self._t2(world, executor)
        sue = _r8_option(menu, "execute_proposal", "Sue for peace")
        concessions = _r8_option(menu, "modify_generous", "Offer concessions")
        assert concessions["terms"]["proposal_type"] == "peace"
        # the old reading: an execute_proposal on the identical package
        assert not [o for o in menu["options"]
                    if o["action"] == "execute_proposal" and o["label"] == "Offer concessions"]
        dp_before = int(world.diplomatic_points)
        reply = _r8_click(world, executor, _r8_index_of(menu, "modify_generous", "Offer concessions"))
        draft = reply["diplomatic_dialogue"]
        assert draft["type"] == "proposal_confirm"
        sweetened = _r8_option(draft, "execute_proposal")["terms"]
        assert not same_package(sweetened, sue["terms"])
        assert any("gold" in s.get("type", "") for s in sweetened["sweeteners"])
        assert sweetened["demands"] == []
        assert int(world.diplomatic_points) == dp_before
        assert world.proposal_in_transit is None
        assert isinstance(draft["dp_cost"], int) and isinstance(draft["acceptance_estimate"], int)

    def test_the_body_says_the_concessions_draft_opens_for_review(self, _r8_world):
        world = _r8_world
        menu = self._t2(world, _r8_executor())
        line = next(l for l in menu["talleyrand_text"].splitlines()
                    if l.startswith("• Offer concessions"))
        assert "Opens a sweetened draft for your review; 3 DP only if you send it." in line
        assert "Terms:" not in line  # it never claims the unsweetened package


# ══════════════════════════════════════════════════════════════════════════
# S14G-X31 — the other open_proposal counsels land on the same menu
# ══════════════════════════════════════════════════════════════════════════

_R8_COUNSELS = {
    # site (diplomatic_advisory._build_situation_recommendation) → its option shape
    "congress": {"kind": "open_proposal", "target_nation": "Austria",
                 "label": "Win over Austria", "description": "The court the Imperial Peace is waiting on.",
                 "text": "The Congress waits on Austria, Sire."},
    "open_talks": {"kind": "open_proposal", "target_nation": "Austria",
                   "label": "Open talks with Austria", "description": "Open a proposal toward a settlement.",
                   "text": "A war gone still."},
    "shore_up": {"kind": "open_proposal", "target_nation": "Prussia",
                 "label": "Shore up Prussia", "description": "Open a proposal to steady our weakest ally.",
                 "text": "the coalition means to fight."},
    "court_weak_link": {"kind": "open_proposal", "target_nation": "Russia",
                        "label": "Court Russia", "description": "Open a proposal to the coalition's weak link.",
                        "text": "links can be… loosened."},
    "approach": {"kind": "open_proposal", "target_nation": "Prussia",
                 "label": "Approach Prussia", "description": "Open a proposal — the ripest diplomatic opening.",
                 "text": "Prussia is neither friend nor enemy."},
}


class TestS14GX31:
    """Sweep of the class: every counsel that opens the menu (the five sites at
    `diplomatic_advisory.py` 370, 459, 536, 546, 641 — Congress, Open talks,
    Shore up, Court the weak link, Approach) carries the target alone, lands on
    the generic menu, and from there every send opens the confirm."""

    @pytest.mark.parametrize("site", sorted(_R8_COUNSELS))
    def test_each_counsels_menu_has_a_body_and_its_sends_open_the_confirm(
            self, _r8_world, monkeypatch, site):
        from backend.game_logic import diplomatic_advisory as ADV
        recommendation = dict(_R8_COUNSELS[site])
        monkeypatch.setattr(ADV, "_build_situation_recommendation",
                            lambda *a, **k: dict(recommendation))
        world = _r8_world
        executor = _r8_executor()
        advice = _r8_advice(world)
        option = advice["options"][0]
        assert option["action"] == "expand_options"
        assert option["terms"] == {"target_nation": recommendation["target_nation"]}
        dp_before = int(world.diplomatic_points)
        menu = _r8_click(world, executor, 1)["diplomatic_dialogue"]
        assert menu["type"] == "proposal_options"
        text = menu["talleyrand_text"]
        assert "The paths before us, Sire:" in text
        for opt in menu["options"]:
            assert opt["label"] in text
        sends = [o for o in menu["options"]
                 if o["action"] == "execute_proposal" and o.get("available", True) is not False]
        assert sends, [o["label"] for o in menu["options"]]
        confirm = _r8_click(world, executor, _r8_index_of(menu, "execute_proposal", sends[0]["label"]))
        assert confirm["success"] is True
        assert confirm["diplomatic_dialogue"]["type"] == "proposal_confirm"
        assert isinstance(confirm["diplomatic_dialogue"]["dp_cost"], int)
        assert int(world.diplomatic_points) == dp_before
        assert world.proposal_in_transit is None

    @pytest.mark.parametrize("relation, first_label, first_type", [
        (-10, "Propose open borders", "open_borders"),    # T4 — the tense menu (neutral falls to it)
        (50, "Propose alliance", "alliance"),            # T5 — friendly
    ])
    def test_the_peace_menus_t4_and_t5_open_the_confirm_too(
            self, _r8_world, relation, first_label, first_type):
        world = _r8_world
        key = world._make_diplo_key("France", "Prussia")
        assert world.get_diplomatic_state("France", "Prussia") == "PEACE"
        world.nation_relations[key] = relation
        executor = _r8_executor()
        menu = _r8_vague(world, executor, "Prussia")
        assert menu["type"] == "proposal_options"
        option = _r8_option(menu, "execute_proposal", first_label)
        assert option.get("available", True) is not False, option
        line = next(l for l in menu["talleyrand_text"].splitlines()
                    if l.startswith(f"• {first_label}"))
        assert " DP to send; the draft opens for your review first." in line
        dp_before = int(world.diplomatic_points)
        reply = _r8_click(world, executor, _r8_index_of(menu, "execute_proposal", first_label))
        confirm = reply["diplomatic_dialogue"]
        assert confirm["type"] == "proposal_confirm"
        assert _r8_option(confirm, "execute_proposal")["terms"]["proposal_type"] == first_type
        assert isinstance(confirm["dp_cost"], int)
        assert int(world.diplomatic_points) == dp_before and world.proposal_in_transit is None

    def test_ddb9_on_the_real_board_the_shut_send_reads_shut_in_the_body(self, _r8_world):
        """No monkeypatch: at relations -50 the open-borders send is refused by
        the verdict itself (`an Open Borders needs -20`) — disabled on the
        option, said in the body, and the "No additional terms" filler of a
        pact's summary never reaches an open option's line."""
        world = _r8_world
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = -50
        menu = _r8_vague(world, _r8_executor(), "Prussia")
        borders = _r8_option(menu, "execute_proposal", "Propose open borders")
        assert borders["available"] is False
        line = next(l for l in menu["talleyrand_text"].splitlines()
                    if l.startswith("• Propose open borders"))
        assert line == ("• Propose open borders — shut: Relations with Prussia "
                        "stand at -50; an Open Borders needs -20.")
        world.nation_relations[key] = 50
        friendly = _r8_vague(world, _r8_executor(), "Prussia")
        assert "No additional terms" not in friendly["talleyrand_text"]

    def test_the_mission_option_quotes_its_dp_a_turn(self, _r8_world):
        world = _r8_world
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = -50
        menu = _r8_vague(world, _r8_executor(), "Prussia")
        line = next(l for l in menu["talleyrand_text"].splitlines()
                    if l.startswith("• Improve relations"))
        assert "1 DP a turn while he is away." in line

    def test_ddb9_a_refused_send_still_arrives_disabled_and_the_body_says_why(
            self, _r8_world, monkeypatch):
        """The DDB-9 stamp (`_stamp_menu_sends`) on the new road: a send the
        verdict refuses is disabled with the verdict's words — on the option
        AND in the body line."""
        from backend.game_logic import treaty as TREATY
        reason = "The court will not receive that instrument today."
        monkeypatch.setattr(TREATY, "can_sign", lambda *a, **k: SimpleNamespace(
            ok=False, message=reason, clause="test"))
        menu = _r8_vague(_r8_world, _r8_executor(), "Britain")
        peace = _r8_option(menu, "execute_proposal", "Propose peace")
        assert peace["available"] is False and peace["enabled"] is False
        assert peace["disabled_reason_display"] == reason
        line = next(l for l in menu["talleyrand_text"].splitlines()
                    if l.startswith("• Propose peace"))
        assert line == f"• Propose peace — shut: {reason}"
        assert "DP to send" not in line


# ══════════════════════════════════════════════════════════════════════════
# S14G-X32 — the confirm's modify arms build on the package
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX32:
    """Found building the fix: the confirm's "Harsher terms" / "More generous"
    carry no package, so the arms redrafted from `generate_suggested_terms` —
    which authors the coveted cession only at `war_score < -20`. Pressing
    "More generous" on the design's confirm (war score +0) would have STRUCK
    the cession it opened with. Both options carry the package now."""

    def test_more_generous_keeps_the_cession(self, _r8_world):
        world = _r8_world
        executor = _r8_executor()
        _r8_advice(world)
        design = _r8_click(world, executor, 1)["diplomatic_dialogue"]
        for action in ("modify_harsh", "modify_generous"):
            carried = _r8_option(design, action)["terms"]
            assert _r8_sweeteners(carried, "territory_cede")[0]["regions"] == ["Flanders"]
            assert carried["proposal_type"] == "peace"
        reply = _r8_click(world, executor, _r8_index_of(design, "modify_generous"))
        generous = reply["diplomatic_dialogue"]
        assert generous["type"] == "proposal_confirm"
        terms = _r8_option(generous, "execute_proposal")["terms"]
        assert _r8_sweeteners(terms, "territory_cede")[0]["regions"] == ["Flanders"]
        assert any("gold" in s.get("type", "") for s in terms["sweeteners"])
        assert world.proposal_in_transit is None and int(world.diplomatic_points) == 5

    def test_the_helper_is_the_pipelines_own_clause_pair(self, _r8_world):
        """`generate_suggested_terms`' coveted-territory arm (at `war_score <
        -20`) builds its pair through `inject_coveted_cession`; the design
        counsel's confirm calls the same one — shown == applied."""
        from backend.game_logic.diplomatic_templates import (
            design_peace_terms, generate_suggested_terms, inject_coveted_cession,
        )
        world = _r8_world
        pair = inject_coveted_cession({"sweeteners": [], "clauses": []}, "Flanders")
        assert pair == {"sweeteners": [{"type": "territory_cede", "value": 1,
                                        "regions": ["Flanders"]}],
                        "clauses": ["territory_flanders"]}
        _r8_stamp_score(world, "Britain", -40)
        with _r8_quiet():
            losing = generate_suggested_terms("Britain", "peace", world, deterministic=True)
            designed = design_peace_terms(world, "Britain", ["Flanders"])
        assert _r8_sweeteners(losing, "territory_cede") == pair["sweeteners"]
        assert "territory_flanders" in losing["clauses"]
        assert _r8_sweeteners(designed, "territory_cede") == pair["sweeteners"]
        assert "territory_flanders" in designed["clauses"]
        # inject is idempotent and replaces any earlier cession
        again = inject_coveted_cession(dict(designed), "Brabant")
        assert _r8_sweeteners(again, "territory_cede") == [
            {"type": "territory_cede", "value": 1, "regions": ["Brabant"]}]
        assert again["clauses"].count("territory_flanders") == 1

    def test_no_ai_road_reaches_the_menu_or_the_confirm_builders(self):
        """Player-only, no seam (Golden Rule 5): the AI builds and sends its
        proposals through `ai_diplomacy`, never through a dialogue."""
        root = Path(__file__).resolve().parents[1] / "backend"
        for rel in ("game_logic/ai_diplomacy.py", "ai/enemy_ai.py",
                    "game_logic/turn_manager.py"):
            src = (root / rel).read_text(encoding="utf-8")
            for name in ("confirm_dialogue_for_terms", "design_confirm_dialogue",
                         "menu_option_confirm_dialogue", "_open_confirm_for_menu_option",
                         "_with_menu_body"):
                assert name not in src, (rel, name)


# ══════════════════════════════════════════════════════════════════════════
# S14G-X33 — the picker's click resolves the option it was drawn for
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX33:
    """Found reading the option list's binding: the popup bound the 1-based
    index only for the nation list's `expand_options` rows; every other picker
    button emitted its bare action string and `main.gd` resolves that to the
    FIRST option carrying it. T1's "Harsh demands" and T2's "Stall" share
    `execute_proposal` with their sibling — the second button of each pair
    opened the first one's draft. The picker binds the index for every option
    now; the backend resolves `options[index - 1]`."""

    def test_the_popup_binds_the_index_for_every_picker_option(self):
        src = _R8_POPUP.read_text(encoding="utf-8")
        assert 'if is_options_picker and action_str == "expand_options":' not in src
        assert "\t\tif is_options_picker:\n\t\t\taction_str = str(idx)\n" in src
        # the war-purpose picker keeps its own arm of the same chain
        assert ('\t\telif dtype == "war_purpose_selection" and action_str in '
                '["select_war_objective", "declare_war_article"]:\n\t\t\taction_str = str(idx)') in src

    def test_t2_stall_by_its_index_opens_the_armistice_draft(self, _r8_world):
        world = _r8_world
        executor = _r8_executor()
        _r8_stamp_score(world, "Britain", -50)
        menu = _r8_vague(world, executor, "Britain")
        stall_index = _r8_index_of(menu, "execute_proposal", "Stall")
        assert stall_index == 3
        assert _r8_index_of(menu, "execute_proposal", "Sue for peace") == 1
        confirm = _r8_click(world, executor, stall_index)["diplomatic_dialogue"]
        assert confirm["type"] == "proposal_confirm"
        assert _r8_option(confirm, "execute_proposal")["terms"]["proposal_type"] == "armistice"
        assert "\"Stall\"" in confirm["talleyrand_text"]


    def test_the_second_of_two_sends_opens_its_own_package(self, _r8_world):
        """T1's pair on a board where the harsh draft survives easing (the
        shipped 1805 board always collapses it — the coalition will sign
        nothing harsher): two `execute_proposal` options, two packages; the
        second button's index opens the SECOND package, not the first."""
        world = _r8_world
        executor = _r8_executor()
        generous = {"type": "peace", "proposal_type": "peace", "sweeteners": [],
                    "demands": [], "clauses": []}
        harsh = {"type": "peace", "proposal_type": "peace", "sweeteners": [],
                 "demands": [{"type": "gold_per_turn", "value": 300}], "clauses": []}
        world.dialogue_manager.replace({
            "type": "proposal_options", "target_nation": "Britain",
            "talleyrand_text": "Sire.", "context": {}, "turn_created": 1, "blocking": False,
            "options": [
                {"label": "Generous peace", "description": "g.", "action": "execute_proposal",
                 "terms": generous},
                {"label": "Harsh demands", "description": "h.", "action": "execute_proposal",
                 "variant": "harsh", "terms": harsh},
                {"label": "Continue fighting", "description": "c.", "action": "dismiss"},
            ]})
        confirm = _r8_click(world, executor, 2)["diplomatic_dialogue"]
        assert confirm["type"] == "proposal_confirm"
        carried = _r8_option(confirm, "execute_proposal")["terms"]
        assert carried["demands"] == [{"type": "gold_per_turn", "value": 300}]
        assert "\"Harsh demands\"" in confirm["talleyrand_text"]
        assert world.proposal_in_transit is None


# ══════════════════════════════════════════════════════════════════════════
# row09
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 — row S14G-9 with its ruling S14G-D6 (October 26, 2026).
#
# S14G-9 (P2, DD-B's third measure): two buy-offs (about 2,300 gold) left Britain
# and Russia "she would join" the next league, and the page said the design
# sleeps, not that the court still counts. League membership is
# `coalition.qualifies_for_coalition` (relation below −10, the fresh-peace and
# cooldown checks); it never reads a sleeping design. A buy-off does two things:
# it sleeps the design 15 turns and adds +5 relations (`instruments.py`); the
# page footer said only "puts the design to sleep 15 turns", `buyoff_quote`
# likewise omitted the +5 and that the court still counts toward the league,
# `compute_buyoff_price` returns None once no design is live (so the clause just
# vanished), NOTHING showed which bargains were in force or their
# `expires_turn`, and `dispatch.py`'s `league_paid` note ("a court bought off now
# is a regiment the league never fields") contradicted the predicate. On turn 11
# the dispatch said "Britain and Russia would now join a league against us" and
# the Balance page still listed both as "she would join" (diplomacy #6, action
# 214).
#
# S14G-D6 (RULED as recommended, October 26, 2026): YES — KEEP THE PREDICATE,
# STATE IT. A buy-off sleeps a court's DESIGN (what it wants), not its grievance
# (what it thinks of France); the league forms on relations. The honest cost is
# the sentence, and the court's row says how long the sleep has to run.
#
# The fix (this file pins it on the shipped 1805 board at peace with every court,
# Britain / Russia / Austria at −50, 6,000 gold, 5 DP, turn 7):
#
# * ONE sentence, `instruments.buyoff_league_clause()`: "+5 relations; she still
#   counts toward a league until relations reach −10" (the −10 is
#   `coalition.LEAGUE_KEEP_OUT_RELATION` — the number lives in one place). With
#   the court's live relation it carries the arithmetic and says which of three
#   things is true of her. Called by `buyoff_quote`, the Balance of Europe
#   footer, the league rows' price clause and the wizard chip's tooltip.
# * `instruments.bargain_turns_left(world, payer, court)` reads
#   `compensation_bargains.expires_turn`; the court's league row says "Design
#   bought off, 15 turns left; her league place is her relations." (the desk's
#   answer and the dispatch's `league_joins` headline read the same detail), and
#   the Compacts line says "France bought off Britain's design (15 turns
#   left)".
# * A court the forecast priced and `compute_buyoff_price` could not (no design
#   live) says "No design to buy off; her league place is her relations." in
#   place of nothing.
# * `dispatch._HEADLINE_BERTHIER_NOTES["league_paid"]`: "Gold buys a design's
#   sleep, Sire, not a court's goodwill — a court bought off still counts toward
#   the league while its relations stand under −10."
#
# Kept: `qualifies_for_coalition` UNCHANGED (pinned: a court with a sleeping
# design and relation −20 still qualifies; at −10 she does not). Player-only
# text, no seam (the AI reads no sentence; the BASELINE_SERIES is numbers).

_R9_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                / "assets" / "maps" / "europe_1805.json")
_R9_ROOT = Path(__file__).resolve().parents[1]

_BAR = "−10"                       # coalition.LEAGUE_KEEP_OUT_RELATION, printed
_SENTENCE = "+5 relations; she still counts toward a league until relations reach −10"


def _r9_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r9_boot():
    from backend.models.world_state import WorldState
    with _r9_quiet():
        return WorldState.from_scenario(str(_R9_SCENARIO))


@pytest.fixture
def _r9_world(_r9_boot):
    """The shipped 1805 board, turn 7: France at peace with every court, the
    three great powers at −50 (they QUALIFY below −10), 6,000 gold, 5 DP."""
    from backend.models.world_state import WorldState
    with _r9_quiet():
        w = WorldState.from_dict(json.loads(json.dumps(_r9_boot.to_dict(), default=str)))
    w.current_turn = 7
    w.nation_gold["France"] = 6000
    w.diplomatic_points = 5
    for nation in w.get_active_nations():
        if nation == "France":
            continue
        key = w._make_diplo_key("France", nation)
        if w.diplomatic_states.get(key) == "WAR":
            w.diplomatic_states[key] = "PEACE"
        if nation in ("Austria", "Britain", "Russia"):
            w.nation_relations[key] = -50
    w.invalidate_active_nations_cache()
    w.active_coalition = None
    w.coalition_brewing = None
    w.threat_by_target["France"] = 45
    return w


def _r9_rel(w, court):
    return int(w.nation_relations.get(w._make_diplo_key("France", court), 0) or 0)


def _r9_set_rel(w, court, value):
    w.nation_relations[w._make_diplo_key("France", court)] = int(value)
    w.invalidate_bloc_members_cache()


def _r9_say(w, court, *, confirmed=False):
    """The player's road: `buy off <court>` through the shared executor."""
    from backend.commands.executor import CommandExecutor
    command = {"action": "buy_off_design", "target": court, "raw_input": f"buy off {court}"}
    if confirmed:
        command["confirmed"] = True
    with _r9_quiet():
        return CommandExecutor().execute({"command": command}, {"world": w})


def _r9_row(w, court):
    from backend.game_logic import coalition as C
    (row,) = [r for r in C.league_rows(w) if r["nation"] == court]
    return row


def _r9_buy(w, court):
    out = _r9_say(w, court, confirmed=True)
    assert out["success"] is True, out
    w.invalidate_bloc_members_cache()
    return out


# ══════════════════════════════════════════════════════════════════════════
# S14G-9 — the buy-off says what it does to her place in a league
# ══════════════════════════════════════════════════════════════════════════

class TestS14G9:
    """Reproduced (before the fix): Britain at −50, `buy off Britain` quoted
    the price, the point, the chest, the 15-turn sleep, the renege and the
    design that wakes next — and nothing of the +5 or of the league; the page
    footer read "puts the design to sleep 15 turns"; after the purchase
    Britain's row read "she would join" with no word of the bargain."""

    def test_the_helper_is_the_ruled_sentence(self):
        from backend.game_logic.instruments import buyoff_league_clause
        assert buyoff_league_clause() == _SENTENCE

    def test_the_bar_is_the_coalitions_own_number(self):
        from backend.game_logic import coalition as C
        from backend.game_logic.instruments import buyoff_league_clause
        assert C.LEAGUE_KEEP_OUT_RELATION == -10
        assert C._minus(C.LEAGUE_KEEP_OUT_RELATION) == _BAR
        assert f"reach {C._minus(C.LEAGUE_KEEP_OUT_RELATION)}" in buyoff_league_clause()

    def test_the_bonus_is_the_constant_the_purchase_applies(self, _r9_world):
        from backend.game_logic.instruments import BUYOFF_RELATION_BONUS, buyoff_league_clause
        w = _r9_world
        before = _r9_rel(w, "Britain")
        _r9_buy(w, "Britain")
        assert _r9_rel(w, "Britain") - before == BUYOFF_RELATION_BONUS == 5
        assert buyoff_league_clause().startswith(f"+{BUYOFF_RELATION_BONUS} relations")

    def test_the_quote_names_the_plus_five_and_the_league(self, _r9_world):
        w = _r9_world
        text = _r9_say(w, "Britain")["message"]
        assert ("It buys the design's sleep, not her goodwill: +5 relations (−50 → −45); "
                "she still counts toward a league until relations reach −10.") in text, text
        # the quote spent nothing
        assert _r9_rel(w, "Britain") == -50 and w.compensation_bargains == []
        assert text.endswith("Buy it off? (yes / no)")

    def test_the_quotes_arithmetic_is_the_one_applied(self, _r9_world):
        """Shown == applied: the relation the quote says she is carried to."""
        w = _r9_world
        text = _r9_say(w, "Britain")["message"]
        _r9_buy(w, "Britain")
        assert "(−50 → −45)" in text and _r9_rel(w, "Britain") == -45

    def test_a_buyoff_that_lifts_her_past_the_line_says_so(self, _r9_world):
        """Britain at −13: the +5 alone takes her to −8, past −10 — the quote
        must not say "she still counts"."""
        w = _r9_world
        _r9_set_rel(w, "Britain", -13)
        text = _r9_say(w, "Britain")["message"]
        assert ("+5 relations lifts her from −13 to −8, past the −10 line a league "
                "counts her below") in text, text
        assert "she still counts" not in text

    def test_a_court_already_past_the_line_says_so(self):
        from backend.game_logic.instruments import buyoff_league_clause
        assert buyoff_league_clause(-8) == (
            "+5 relations (−8 → −3); she already stands past the −10 line a league "
            "counts her below")
        assert buyoff_league_clause(-10).startswith("+5 relations (−10 → −5); she already")
        # the bar itself is the boundary the predicate draws: −11 is below it
        assert buyoff_league_clause(-11) == (
            "+5 relations lifts her from −11 to −6, past the −10 line a league counts her below")

    def test_the_footer_carries_the_sentence(self, _r9_world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        from backend.game_logic.instruments import COMPENSATION_TERM_TURNS, INSTRUMENT_DP_COST
        w = _r9_world
        with _r9_quiet():
            boe = build_diplomatic_ledger(w)["balance_of_europe"]
        assert boe["league_footer"] == (
            f"Talleyrand courts one court at a time; a buy-off is one order each "
            f"({INSTRUMENT_DP_COST} DP and the gold named) and puts the design to sleep "
            f"{COMPENSATION_TERM_TURNS} turns — {_SENTENCE}. The forecast holds the board still.")

    def test_the_row_after_a_buyoff_says_turns_left_and_still_joins(self, _r9_world):
        """The sighting: Britain bought off and still in the table."""
        w = _r9_world
        _r9_buy(w, "Britain")
        row = _r9_row(w, "Britain")
        assert row["status"] == "joins"
        assert "she would join." in row["text"]
        assert "Design bought off, 15 turns left; her league place is her relations." in row["text"]
        # the court beside her that was NOT bought off says nothing of a bargain
        assert "bought off" not in _r9_row(w, "Russia")["text"].replace("buying off", "")

    def test_the_turns_left_count_down_with_the_calendar(self, _r9_world):
        from backend.game_logic.instruments import COMPENSATION_TERM_TURNS, bargain_turns_left
        w = _r9_world
        assert bargain_turns_left(w, "France", "Britain") is None
        _r9_buy(w, "Britain")
        assert bargain_turns_left(w, "France", "Britain") == COMPENSATION_TERM_TURNS == 15
        w.current_turn += 3
        w.invalidate_bloc_members_cache()
        assert bargain_turns_left(w, "France", "Britain") == 12
        assert "Design bought off, 12 turns left;" in _r9_row(w, "Britain")["text"]
        w.current_turn += 11
        assert bargain_turns_left(w, "France", "Britain") == 1
        assert "Design bought off, 1 turn left;" in _r9_row(w, "Britain")["text"]
        w.current_turn += 5
        assert bargain_turns_left(w, "France", "Britain") == 0       # never negative

    def test_the_reader_counts_only_the_payers_design_bargains(self, _r9_world):
        from backend.game_logic.instruments import bargain_turns_left
        w = _r9_world
        _r9_buy(w, "Britain")
        assert bargain_turns_left(w, "Britain", "France") is None     # not the payer
        assert bargain_turns_left(w, "France", "Russia") is None      # not the court
        # the hostage bond of a province paid carries no design id: no sleep to count
        w.compensation_bargains.append({
            "payer": "France", "recipient": "Russia", "design_id": "",
            "granted": {"region": "Poland"}, "turn": 7, "expires_turn": 22})
        assert bargain_turns_left(w, "France", "Russia") is None
        # the probe `next_design_after_buyoff` lays down is never read
        w.compensation_bargains.append({
            "payer": "France", "recipient": "Russia", "design_id": "x", "_probe": True,
            "turn": 7, "expires_turn": 22})
        assert bargain_turns_left(w, "France", "Russia") is None

    def test_a_court_the_forecast_priced_with_no_design_says_so(self, _r9_world):
        """`compute_buyoff_price` returns None once no design is live: the
        buy-off clause used to vanish and the row said nothing in its place."""
        from backend.game_logic.instruments import compute_buyoff_price
        w = _r9_world
        _r9_set_rel(w, "Saxony", -30)
        assert compute_buyoff_price(w, "Saxony") is None
        row = _r9_row(w, "Saxony")
        assert row["status"] == "joins"
        assert "No design to buy off; her league place is her relations." in row["text"]

    def test_the_courts_whose_design_is_live_are_not_told_there_is_none(self, _r9_world):
        w = _r9_world
        assert "No design to buy off" not in _r9_row(w, "Britain")["text"]

    def test_the_desk_and_the_dispatch_headline_read_the_same_detail(self, _r9_world):
        from backend.game_logic import coalition as C
        w = _r9_world
        _r9_buy(w, "Britain")
        forecast = C.league_forecast(w)
        (row,) = [r for r in forecast["courts"] if r["nation"] == "Britain"]
        detail = C.league_row_detail(w, row, forecast)
        assert detail.startswith("Design bought off, 15 turns left;"), detail
        # the league_joins headline (`dispatch`) builds its line from this detail
        assert detail in C.league_row_text(w, row, forecast)

    def test_a_great_power_that_stays_out_still_tells_of_its_bargain(self, _r9_world):
        """Bought off AND lifted past the line: the row is the "stays out" row —
        and says why, with the sleep beside it."""
        w = _r9_world
        _r9_set_rel(w, "Britain", -14)
        _r9_buy(w, "Britain")                                     # −14 → −9
        row = _r9_row(w, "Britain")
        assert row["status"] == "out"
        assert row["text"].startswith("Britain — relations −9: she stays out of a league")
        assert row["text"].endswith(
            "Design bought off, 15 turns left; her league place is her relations.")

class TestS14GX39:
    """Sibling: the ledger's Compacts line ("France bought off Britain's
    design") named the bargain and never how long the design sleeps — NOT
    FOUND: any reader of `expires_turn` the player could see
    (`instruments.build_instruments_line`). FIXED: "(15 turns left)"."""

    def test_the_compacts_line_names_how_long_the_design_sleeps(self, _r9_world):
        from backend.game_logic.instruments import build_instruments_line
        w = _r9_world
        _r9_buy(w, "Britain")
        assert build_instruments_line(w, "Britain") == "France bought off Britain's design (15 turns left)"
        assert build_instruments_line(w, "France") == "France bought off Britain's design (15 turns left)"
        w.current_turn += 14
        assert build_instruments_line(w, "Britain") == "France bought off Britain's design (1 turn left)"

    def test_the_peace_table_compensation_line_is_untouched(self, _r9_world):
        from backend.game_logic.instruments import build_instruments_line
        w = _r9_world
        w.compensation_bargains.append({
            "payer": "France", "recipient": "Russia", "design_id": "arbiter_of_europe",
            "granted": {"clause": "territory_compensate", "region": "Poland"},
            "turn": 7, "expires_turn": 22})
        assert build_instruments_line(w, "Russia") == "France compensated Russia at the peace (Poland)"

    def test_the_client_prints_the_line_as_sent(self):
        """The Godot ledger prints `compacts` through one humanise call — no
        client-side copy of the line to keep in step."""
        source = (_R9_ROOT / "godot-client" / "project-sovereign" / "scripts"
                  / "diplomatic_ledger.gd").read_text(encoding="utf-8")
        assert 'n.get("compacts")' in source and "humanize_nation_keys_in_text(str(compacts))" in source


class TestS14GX40:
    """Sibling: the league row's price clause ("buying off her design (N gold)
    is enough alone") read as the SLEEP keeping her out. It is the +5
    relations that lifts her past the line — the clause says so, from the one
    builder (`league_price_clause`; the counsel's own control line is filed)."""

    def test_the_price_clause_names_the_plus_five(self, _r9_world):
        """Before the buy-off: the row's price names what the gold does."""
        w = _r9_world
        text = _r9_row(w, "Britain")["text"]
        assert "buying off her design costs " in text
        assert f"({_SENTENCE})" in text, text

    def test_the_price_clause_of_a_buyoff_that_is_enough_alone_says_why(self, _r9_world):
        """Prussia at −13: "enough alone" because the +5 lifts her past −10 —
        not because the design sleeps."""
        w = _r9_world
        _r9_set_rel(w, "Prussia", -13)
        text = _r9_row(w, "Prussia")["text"]
        assert "is enough alone (+5 relations lifts her from −13 to −8, past the −10 line" in text, text

    def test_the_dispatchs_paid_line_carries_it(self, _r9_world):
        """The league_paid headline's "the price to keep her out" is the same clause."""
        from backend.game_logic import coalition as C
        w = _r9_world
        forecast = C.league_forecast(w)
        (row,) = [r for r in forecast["courts"] if r["nation"] == "Britain"]
        assert f"({_SENTENCE})" in C.league_price_clause(w, row)


class TestS14GX41:
    """Sibling: the wizard's Buy Off chip tooltip said "the design sleeps
    while the bargain stands" and nothing of the league — the typed order's
    quote and the chip now say the one sentence."""

    def test_the_typed_order_and_the_chip_say_the_same_sentence(self, _r9_world):
        from backend.game_logic.diplomacy import _instrument_actions
        from backend.game_logic.instruments import buyoff_league_clause
        w = _r9_world
        with _r9_quiet():
            chip = next(a for a in _instrument_actions(w, "France", "Britain")
                        if a["action"] == "buy_off_design")
        clause = buyoff_league_clause(-50)
        assert f"It buys the design's sleep, not her goodwill: {clause}." in chip["effect_text"], chip
        assert clause in _r9_say(w, "Britain")["message"]

    def test_the_chip_keeps_its_old_sentences(self, _r9_world):
        from backend.game_logic.diplomacy import _instrument_actions
        w = _r9_world
        with _r9_quiet():
            chip = next(a for a in _instrument_actions(w, "France", "Britain")
                        if a["action"] == "buy_off_design")
        text = chip["effect_text"]
        assert text.startswith("The design sleeps while the bargain stands — and waking it by "
                               "betrayal is the strongest casus belli in Europe.")
        assert "No other design wakes after it." in text


class TestS14G9Dispatch:
    """The `league_paid` closing note contradicted the predicate."""

    def test_the_note_is_the_corrected_sentence(self):
        from backend.game_logic import coalition as C
        from backend.game_logic.dispatch import _HEADLINE_BERTHIER_NOTES
        note = _HEADLINE_BERTHIER_NOTES["league_paid"]
        assert note == ("Gold buys a design's sleep, Sire, not a court's goodwill — a court "
                        "bought off still counts toward the league while its relations "
                        "stand under −10.")
        assert f"under {C._minus(C.LEAGUE_KEEP_OUT_RELATION)}." in note       # one number
        assert "regiment" not in note and "never fields" not in note

    def test_the_old_sentence_is_nowhere_in_the_backend(self):
        for path in (_R9_ROOT / "backend").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert "a regiment the league never fields" not in text, path
            assert "Gold buys armies, Sire" not in text, path

    def test_the_headline_still_closes_with_the_class_note(self, _r9_world):
        """The census (the class has a note) holds, and the page's own close reads it."""
        from backend.game_logic.dispatch import _HEADLINE_BERTHIER_NOTES
        assert str(_HEADLINE_BERTHIER_NOTES.get("league_paid") or "").strip()


# ══════════════════════════════════════════════════════════════════════════
# S14G-D6 — the predicate stays: a bought-off court still counts
# ══════════════════════════════════════════════════════════════════════════

class TestS14GD6:
    """The ruling (YES — KEEP THE PREDICATE, STATE IT): `qualifies_for_coalition`
    never reads a sleeping design. Exempting a bought court would make the
    buy-off a 1,100-gold league ban the relations page contradicts. If the
    user wants the buy-off to be a ban, the dial is one clause in
    `qualifies_for_coalition` and a re-measure of the league series."""

    def test_a_court_with_a_sleeping_design_and_relation_minus_20_still_qualifies(self, _r9_world):
        from backend.game_logic.coalition import qualifies_for_coalition
        from backend.game_logic.instruments import design_suspended
        w = _r9_world
        _r9_buy(w, "Britain")
        assert design_suspended(w, "Britain", w.compensation_bargains[-1]["design_id"])
        _r9_set_rel(w, "Britain", -20)
        assert qualifies_for_coalition("Britain", w) is True

    def test_the_boundary_is_relations_not_the_bargain(self, _r9_world):
        from backend.game_logic.coalition import qualifies_for_coalition
        w = _r9_world
        _r9_buy(w, "Britain")
        _r9_set_rel(w, "Britain", -11)
        assert qualifies_for_coalition("Britain", w) is True
        _r9_set_rel(w, "Britain", -10)
        assert qualifies_for_coalition("Britain", w) is False

    def test_the_forecast_keeps_her_in_the_table(self, _r9_world):
        from backend.game_logic import coalition as C
        w = _r9_world
        _r9_buy(w, "Britain")
        _r9_buy(w, "Russia")
        forecast = C.league_forecast(w)
        by = {r["nation"]: r for r in forecast["courts"]}
        assert by["Britain"]["status"] == C.LEAGUE_JOINS
        assert by["Russia"]["status"] == C.LEAGUE_JOINS
        assert {"Britain", "Russia"} <= set(forecast["joiners"])

    def test_the_predicate_reads_no_bargain(self):
        from backend.game_logic.coalition import qualifies_for_coalition
        source = inspect.getsource(qualifies_for_coalition)
        assert "compensation_bargains" not in source
        assert "design_suspended" not in source
        assert "bargain" not in source

    def test_the_sleep_does_not_change_the_row_status(self, _r9_world):
        """Same relation, bargain or none: the status is the relation's."""
        w = _r9_world
        _r9_set_rel(w, "Britain", -45)
        plain = _r9_row(w, "Britain")["status"]
        w.compensation_bargains.append({
            "payer": "France", "recipient": "Britain", "design_id": "low_countries",
            "granted": {}, "turn": 7, "expires_turn": 22})
        w.invalidate_bloc_members_cache()
        assert _r9_row(w, "Britain")["status"] == plain == "joins"

    def test_the_sentence_is_said_at_every_surface_the_choice_is_made(self, _r9_world):
        """The sweep's roll-call: the order's quote, the chip, the footer, the row."""
        from backend.game_logic.diplomacy import _instrument_actions
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        w = _r9_world
        with _r9_quiet():
            chip = next(a for a in _instrument_actions(w, "France", "Britain")
                        if a["action"] == "buy_off_design")
            footer = build_diplomatic_ledger(w)["balance_of_europe"]["league_footer"]
        surfaces = {
            "quote": _r9_say(w, "Britain")["message"],
            "chip": chip["effect_text"],
            "footer": footer,
            "row": _r9_row(w, "Britain")["text"],
        }
        for name, text in surfaces.items():
            assert "she still counts toward a league until relations reach −10" in text, name


# ══════════════════════════════════════════════════════════════════════════
# row10
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 — row S14G-10 (October 26, 2026).
#
# S14G-10 (P2, DD-B's third measure): the licence's quote omits what the licensed
# war costs. `sponsorship_quote` stated the 1 DP, "pledges non-interference for
# 10 turns" and the renege bond (−25); nothing of the war it licenses. When the
# licensee declares, `declare_war` applies `declaration_relation_penalties`
# (−15 indirect, halved with a casus belli) to the AGGRESSOR's relations with
# every court that is neither party — France's included, so France–Prussia fell
# 15 and the Improve Relations courtship under way (+18 → +2) was undone. The
# player's "lowers everyone's opinion of me" overstated it: it is PRUSSIA's
# relations with every court that fall, and the loss France feels is the Prussia
# courtship it had running. `declaration_cost_clause` had no subject
# ("relations with every court, France's included, fall 15"); the treaty-break
# letter (`commitments_routing`) the same; `guarantee_quote` and `buyoff_quote`
# named no later third-party cost either. The player granted the licence on turn
# 4 (the box talked only of reneging), declined to stop the war on turn 10, and
# on turn 11 read "Prussia has declared war on Hanover — relations with every
# court, France's included, fall 15" (diplomacy #10, action 212).
#
# The fix (pinned here on the shipped 1805 board at peace with every court):
#
# * `instruments.licensed_war_cost_clause`, appended to `sponsorship_quote` (the
#   licence AND the sponsor) and to the sponsor chip's tooltip: "If Prussia then
#   declares on Hanover, her relations with every court, France's included, fall
#   15 (France–Prussia now -10, -5 once this compact is struck, -20 after her
#   declaration)." Computed live from `declaration_relation_penalties` (halved
#   and said so when the licensee holds a renege grievance against the aim - the
#   casus belli the design war's declaration reads; a licence is NOT itself one),
#   the live France–licensee relation, the compact's own +5, and, when an
#   Improve Relations (or any relation-earning) mission on a pair the
#   declaration would hit is live, "the Improve Relations mission running with
#   Prussia is set back the same 15" (the mission's pair is
#   `mission_pair_snapshot`'s own; `declare_war` books the same shock).
# * `diplomacy.declaration_cost_clause(cost, player, aggressor=None)`: with a
#   subject - "Prussia's relations with every court, France's included, fall 15"
#   - and every beat that has an aggressor passes it: the rail row and the
#   dispatch beat of a declaration, the treaty break's letter. The subjectless
#   form survives for a caller with none (the AI downgrade's lines, filed).
# * Sweep: `guarantee_quote` (and its chip) name what honouring the pledge costs,
#   from the same penalties function: "Honouring it means declaring on the
#   aggressor: France's relations fall 30 with that court and 15 with every
#   other (15 and 7 after a rejected ultimatum)." `buyoff_quote` names no later
#   third-party cost - none exists: a purchase between two courts licenses no war.
#
# Kept: the licence's price (1 DP), the term, the renege bond and the quote-first
# idiom are word for word; `declaration_cost_to_player` (the figure, S14E-9) is
# untouched. Player-only text, no seam. The ledger row's "undone" is worded "set
# back the same 15": the declaration writes −15 to the pair and the mission's
# earned work stays on its books, so "undone" over-states a mission that had
# earned less than 15.

_R10_SCENARIO = (Path(__file__).resolve().parents[1] / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")

_R10_WAR = ("her relations with every court, France's included, fall 15 "
            "(France–Prussia now -10, -5 once this compact is struck, -20 after her declaration)")


def _r10_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r10_boot():
    from backend.models.world_state import WorldState
    with _r10_quiet():
        return WorldState.from_scenario(str(_R10_SCENARIO))


@pytest.fixture
def _r10_world(_r10_boot):
    """The shipped 1805 board, turn 4: France at peace with every court,
    Prussia at −10 (her opening relation), 5 DP, gold for a sponsorship."""
    from backend.models.world_state import WorldState
    with _r10_quiet():
        w = WorldState.from_dict(json.loads(json.dumps(_r10_boot.to_dict(), default=str)))
    w.current_turn = 4
    w.nation_gold["France"] = 6000
    w.diplomatic_points = 5
    for nation in w.get_active_nations():
        if nation == "France":
            continue
        key = w._make_diplo_key("France", nation)
        if w.diplomatic_states.get(key) == "WAR":
            w.diplomatic_states[key] = "PEACE"
    w.invalidate_active_nations_cache()
    w.active_coalition = None
    w.coalition_brewing = None
    w.pending_dispatch_events = []
    return w


@pytest.fixture(autouse=True)
def _r10_no_blowback(monkeypatch):
    from backend.game_logic import diplomatic_dialogue as DD
    monkeypatch.setitem(DD.MISSION_EFFECTS["COURT_NATION"], "undermine_chance", 0.0)


def _r10_rel(w, a, b):
    return int(w.nation_relations.get(w._make_diplo_key(a, b), 0) or 0)


def _r10_set_rel(w, a, b, value):
    w.nation_relations[w._make_diplo_key(a, b)] = int(value)


def _r10_say(w, text, action="sponsor_design", target="Prussia", **extra):
    """The player's road: one typed order through the shared executor."""
    from backend.commands.executor import CommandExecutor
    command = {"action": action, "target": target, "raw_input": text, "raw_command": text}
    command.update(extra)
    with _r10_quiet():
        return CommandExecutor().execute({"command": command}, {"world": w})


def _r10_mission(w, mission_type, target, **extra):
    mission = {
        "type": mission_type, "target": target, "turns_active": 0,
        "paused": False, "paused_turns": 0, "started_turn": int(w.current_turn),
        "initial_relation": _r10_rel(w, w.player_nation, target),
    }
    mission.update(extra)
    w.active_diplomatic_mission = mission
    w.talleyrand_state = "ON_MISSION"
    return mission


def _r10_declare(w, aggressor="Prussia", target="Hanover", **kw):
    from backend.game_logic import diplomacy as D
    with _r10_quiet():
        res = D.declare_war(w, aggressor, target, **kw)
    assert res["success"], res
    return res


def _r10_grievance(w, victim, breaker):
    """`victim` holds a live renege grievance against `breaker` (the casus
    belli the design war's declaration reads)."""
    w.betrayal_history[f"{breaker}|{victim}"] = {
        "grievance_flags": [{"grievance_type": "bargain_reneged"}]}


# ══════════════════════════════════════════════════════════════════════════
# S14G-10 — the licence's quote names what the licensed war costs
# ══════════════════════════════════════════════════════════════════════════

class TestS14G10:
    """Reproduced (before the fix): `license Prussia against Hanover` quoted
    "License Prussia's design against Hanover: no gold, 1 diplomatic point.
    France blesses it and pledges non-interference for 10 turns. The compact
    binds France: … is reneging — relations -25 and the strongest casus belli
    in Europe. License it? (yes / no)" — and nothing of the war."""

    def test_the_licence_quote_names_the_fall_and_the_arithmetic(self, _r10_world):
        w = _r10_world
        out = _r10_say(w, "license Prussia against Hanover")
        text = out["message"]
        assert text.startswith("License Prussia's design against Hanover: no gold, 1 diplomatic point.")
        assert f"If Prussia then declares on Hanover, {_R10_WAR}." in text, text
        assert text.endswith("License it? (yes / no)")
        assert w.diplomatic_points == 5 and w.directed_sponsorships == []   # the quote spent nothing

    def test_the_sponsor_quote_names_it_too(self, _r10_world):
        w = _r10_world
        text = _r10_say(w, "sponsor Prussia against Hanover 200 gold")["message"]
        assert text.startswith("Sponsor Prussia's design against Hanover: 200 gold a turn")
        assert f"If Prussia then declares on Hanover, {_R10_WAR}." in text, text
        assert text.endswith("Sponsor it? (yes / no)")
        # the renege bond is still there, ahead of it
        assert text.index("is reneging") < text.index("If Prussia then declares")

    def test_the_figures_are_the_declarations_own(self, _r10_world):
        """Shown == applied: grant the licence the quote describes, let Prussia
        declare, and read the relations the quote promised."""
        from backend.game_logic.diplomacy import declaration_relation_penalties
        from backend.game_logic.instruments import grant_directed_sponsorship
        w = _r10_world
        assert declaration_relation_penalties(False)[1] == -15
        _r10_set_rel(w, "France", "Prussia", -10)
        before_every = {n: _r10_rel(w, "Prussia", n) for n in w.get_active_nations()
                        if n not in ("Prussia", "Hanover")}
        grant_directed_sponsorship(w, payer="France", recipient="Prussia", aim="Hanover",
                                   amount_per_turn=0)
        assert _r10_rel(w, "France", "Prussia") == -5            # "once this compact is struck"
        _r10_declare(w, "Prussia", "Hanover")
        assert _r10_rel(w, "France", "Prussia") == -20           # "after her declaration"
        for nation, was in before_every.items():                 # "with every court"
            expected = max(-100, was - 15) if nation != "France" else None
            if expected is not None:
                assert _r10_rel(w, "Prussia", nation) == expected, nation

    def test_a_casus_belli_halves_it_and_the_quote_says_so(self, _r10_world):
        """The design war's declaration reads the licensee's renege grievance
        against the aim (`war_council._declare_design_war`): the quote reads the
        same predicate - a licence is not itself a casus belli."""
        from backend.game_logic.instruments import grant_directed_sponsorship, has_renege_grievance
        w = _r10_world
        _r10_set_rel(w, "France", "Prussia", -10)
        assert has_renege_grievance(w, "Prussia", "Hanover") is False
        plain = _r10_say(w, "license Prussia against Hanover")["message"]
        assert "halved" not in plain and "fall 15 (" in plain
        _r10_grievance(w, victim="Prussia", breaker="Hanover")
        assert has_renege_grievance(w, "Prussia", "Hanover") is True
        text = _r10_say(w, "license Prussia against Hanover")["message"]
        assert ("her relations with every court, France's included, fall 7, halved by "
                "Prussia's casus belli against Hanover "
                "(France–Prussia now -10, -5 once this compact is struck, -12 after her "
                "declaration).") in text, text
        # applied: the declaration with the casus belli takes 7
        grant_directed_sponsorship(w, payer="France", recipient="Prussia", aim="Hanover",
                                   amount_per_turn=0)
        _r10_declare(w, "Prussia", "Hanover", casus_belli=True)
        assert _r10_rel(w, "France", "Prussia") == -12

    def test_the_live_relation_is_the_one_quoted(self, _r10_world):
        w = _r10_world
        _r10_set_rel(w, "France", "Prussia", 18)
        text = _r10_say(w, "license Prussia against Hanover")["message"]
        assert "(France–Prussia now +18, +23 once this compact is struck, +8 after her declaration)" in text
        _r10_set_rel(w, "France", "Prussia", 0)
        text = _r10_say(w, "license Prussia against Hanover")["message"]
        assert "(France–Prussia now 0, +5 once this compact is struck, -10 after her declaration)" in text

    def test_the_clamp_is_honoured(self, _r10_world):
        w = _r10_world
        _r10_set_rel(w, "France", "Prussia", 98)
        text = _r10_say(w, "license Prussia against Hanover")["message"]
        assert "(France–Prussia now +98, +100 once this compact is struck, +85 after" in text
        _r10_set_rel(w, "France", "Prussia", -99)
        text = _r10_say(w, "license Prussia against Hanover")["message"]
        assert "-99, -94 once this compact is struck, -100 after" in text

    def test_a_running_courtship_is_named_and_is_set_back(self, _r10_world):
        """The sighting: the Improve Relations the player had running with
        Prussia. The quote names it; the declaration books the same shock."""
        from backend.game_logic.instruments import grant_directed_sponsorship
        w = _r10_world
        _r10_set_rel(w, "France", "Prussia", 10)
        _r10_mission(w, "IMPROVE_RELATIONS", "Prussia")
        text = _r10_say(w, "license Prussia against Hanover")["message"]
        assert ("; the Improve Relations mission running with Prussia is set back the "
                "same 15.") in text, text
        grant_directed_sponsorship(w, payer="France", recipient="Prussia", aim="Hanover",
                                   amount_per_turn=0)
        _r10_declare(w, "Prussia", "Hanover")
        (shock,) = [s for s in w.active_diplomatic_mission["shocks"] if s["kind"] == "war_declaration"]
        assert shock["delta"] == -15 and (shock["by"], shock["on"]) == ("Prussia", "Hanover")

    def test_no_mission_no_clause(self, _r10_world):
        text = _r10_say(_r10_world, "license Prussia against Hanover")["message"]
        assert "mission" not in text

    def test_a_mission_the_declaration_does_not_reach_is_not_named(self, _r10_world):
        w = _r10_world
        # a courtship of ANOTHER court: Prussia's declaration does not write that pair
        _r10_mission(w, "IMPROVE_RELATIONS", "Austria")
        assert "mission" not in _r10_say(w, "license Prussia against Hanover")["message"]
        # an intel mission on Prussia earns no relations: nothing is "set back"
        _r10_mission(w, "GATHER_INTEL", "Prussia")
        assert "mission" not in _r10_say(w, "license Prussia against Hanover")["message"]
        # a COMPLETED mission is a record, not a commitment
        _r10_mission(w, "IMPROVE_RELATIONS", "Prussia", completed=True)
        assert "mission" not in _r10_say(w, "license Prussia against Hanover")["message"]

    def test_the_mission_clause_names_the_mission_by_its_row(self, _r10_world):
        w = _r10_world
        _r10_mission(w, "COURT_NATION", "Prussia")
        assert "the Court mission running with Prussia is set back the same 15" in (
            _r10_say(w, "license Prussia against Hanover")["message"])

    def test_the_chip_tooltip_says_it_too(self, _r10_world):
        from backend.game_logic.diplomacy import _instrument_actions
        w = _r10_world
        with _r10_quiet():
            chip = next(a for a in _instrument_actions(w, "France", "Prussia")
                        if a["action"] == "sponsor_design")
        assert f"If Prussia then declares on Hanover, {_R10_WAR}." in chip["effect_text"], chip

    def test_no_clause_where_no_third_court_is_hit(self, _r10_world):
        from backend.game_logic.instruments import licensed_war_cost_clause
        w = _r10_world
        assert licensed_war_cost_clause(w, "France", "Prussia", "") == ""
        assert licensed_war_cost_clause(w, "France", "Prussia", "France") == ""
        assert licensed_war_cost_clause(w, "France", "Prussia", "Prussia") == ""

    def test_the_licence_price_and_bond_are_word_for_word(self, _r10_world):
        """Kept: everything the quote said before it still says, in order."""
        text = _r10_say(_r10_world, "license Prussia against Hanover")["message"]
        assert text.startswith(
            "License Prussia's design against Hanover: no gold, 1 diplomatic point. "
            "France blesses it and pledges non-interference for 10 turns. "
            "The compact binds France: marching on Prussia before it lapses, or "
            "guaranteeing Hanover, is reneging — relations -25 and the strongest "
            "casus belli in Europe. If Prussia then declares on Hanover,")

    def test_confirming_still_mints_the_licence(self, _r10_world):
        w = _r10_world
        out = _r10_say(w, "license Prussia against Hanover", confirmed=True)
        assert out["success"] is True and out["sponsorship"]["amount_per_turn"] == 0
        assert w.diplomatic_points == 4


# ══════════════════════════════════════════════════════════════════════════
# S14G-10 — the declaration clause has a subject
# ══════════════════════════════════════════════════════════════════════════

class TestS14G10Subject:
    def test_the_clause_names_whose_relations_fall(self):
        from backend.game_logic.diplomacy import declaration_cost_clause
        assert declaration_cost_clause(15, "France", aggressor="Prussia") == (
            "Prussia's relations with every court, France's included, fall 15")

    def test_a_court_with_an_article_takes_it(self):
        from backend.game_logic.diplomacy import declaration_cost_clause
        assert declaration_cost_clause(15, "France", aggressor="Ottoman").startswith(
            "the Ottoman Empire's relations with every court")
        assert declaration_cost_clause(10, "France", aggressor="the Duchy of Warsaw").startswith(
            "the Duchy of Warsaw's relations")

    def test_the_subjectless_form_survives_for_a_caller_with_none(self):
        from backend.game_logic.diplomacy import declaration_cost_clause
        assert declaration_cost_clause(10, "France") == (
            "relations with every court, France's included, fall 10")
        assert declaration_cost_clause(5, "France", aggressor=None) == (
            "relations with every court, France's included, fall 5")

    def test_a_cost_of_nothing_is_nothing(self):
        from backend.game_logic.diplomacy import declaration_cost_clause
        assert declaration_cost_clause(0, "France", aggressor="Prussia") == ""

    def test_the_rail_row_of_a_declaration_names_the_aggressor(self, _r10_world):
        """Caller 1: `declare_war`'s rail row (the sighting's "Prussia Declares War!")."""
        w = _r10_world
        _r10_declare(w, "Prussia", "Hanover")
        (row,) = [n for n in w.notifications.get_pending() if n.get("type") == "war_declared"]
        assert row["message"].endswith(
            "— Prussia's relations with every court, France's included, fall 15."), row["message"]

    def test_the_dispatch_beat_of_a_declaration_names_the_aggressor(self, _r10_world):
        """Caller 2: the dispatch's `diplomatic_war_declared` beat."""
        from backend.game_logic.dispatch import _build_diplomatic_events_section
        w = _r10_world
        _r10_declare(w, "Prussia", "Hanover")
        with _r10_quiet():
            events = _build_diplomatic_events_section(w, "France")
        (beat,) = [e for e in events if e["type"] == "diplomatic_war_declared"]
        assert beat["text"].startswith("Prussia has declared war on Hanover"), beat
        assert beat["text"].endswith(
            "— Prussia's relations with every court, France's included, fall 15."), beat

    def test_a_casus_belli_halves_the_figure_and_keeps_the_subject(self, _r10_world):
        w = _r10_world
        _r10_declare(w, "Prussia", "Hanover", casus_belli=True)
        (row,) = [n for n in w.notifications.get_pending() if n.get("type") == "war_declared"]
        assert row["message"].endswith(
            "— Prussia's relations with every court, France's included, fall 7."), row["message"]

    def test_our_own_war_adds_nothing(self, _r10_world):
        w = _r10_world
        _r10_declare(w, "France", "Hanover")
        (row,) = [n for n in w.notifications.get_pending() if n.get("type") == "war_declared"]
        assert "relations with every court" not in row["message"]

    def test_the_treaty_breaks_letter_names_the_breaker(self):
        """Caller 3: `commitments_routing`'s break clause."""
        from backend.game_logic.commitments_routing import format_commitments_notice
        text = format_commitments_notice("diplomatic_treaty_broken", {
            "breaker": "Austria", "injured_party": "Prussia", "treaty_type_display": "Full Alliance",
            "reason_phrase": "without seeking release", "relation_cost": 10, "player": "France"})
        assert text == (
            "Austria has broken the Full Alliance with Prussia without seeking release — "
            "Austria's relations with every court, France's included, fall 10.")

    def test_a_break_from_the_real_verb_reads_the_same(self, _r10_world):
        from backend.game_logic.diplomacy import break_treaty
        w = _r10_world
        key = w._make_diplo_key("Austria", "Prussia")
        w.diplomatic_states[key] = "ALLIANCE"
        w.active_treaties = {key: {"type": "alliance", "nations": ["Austria", "Prussia"]}}
        w.nation_relations[key] = 50
        w.nation_dp = {"Austria": 5, "Prussia": 5}
        with _r10_quiet():
            result = break_treaty(key, "Austria", w)
        assert result["success"] is True
        rail = [n["message"] for n in w.notifications.get_pending() if "broken" in n["message"]]
        assert rail == [
            "Austria has broken the Full Alliance with Prussia without seeking release — "
            "Austria's relations with every court, France's included, fall 10."]


# ══════════════════════════════════════════════════════════════════════════
# S14G-X10.k — the sweep: the pledge's later cost
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX44:
    """The guarantee quote named the abandonment clock and the renege bond but
    not what honouring the pledge costs: France declares on the aggressor, and
    that declaration takes the penalties off France's own relations."""

    def test_the_guarantee_quote_names_what_honouring_costs(self, _r10_world):
        w = _r10_world
        text = _r10_say(w, "guarantee Prussia", action="guarantee_nation")["message"]
        assert ("Honouring it means declaring on the aggressor: France's relations fall 30 "
                "with that court and 15 with every other (15 and 7 after a rejected "
                "ultimatum).") in text, text
        assert text.endswith("Guarantee them? (yes / no)")

    def test_the_figures_are_the_penalties_functions_own(self):
        from backend.game_logic.diplomacy import declaration_relation_penalties
        from backend.game_logic.instruments import guarantee_honour_cost_clause
        direct, indirect = declaration_relation_penalties(False)
        half_direct, half_indirect = declaration_relation_penalties(True)
        assert (direct, indirect, half_direct, half_indirect) == (-30, -15, -15, -7)
        assert guarantee_honour_cost_clause() == (
            f"Honouring it means declaring on the aggressor: France's relations fall "
            f"{-direct} with that court and {-indirect} with every other "
            f"({-half_direct} and {-half_indirect} after a rejected ultimatum)")

    def test_the_figures_are_what_a_declaration_applies(self, _r10_world):
        """Shown == applied: France declares on Hanover, and her relations with
        Hanover and with Austria fall by the quoted figures."""
        w = _r10_world
        hanover, austria = _r10_rel(w, "France", "Hanover"), _r10_rel(w, "France", "Austria")
        _r10_declare(w, "France", "Hanover")
        assert _r10_rel(w, "France", "Hanover") == max(-100, hanover - 30)
        assert _r10_rel(w, "France", "Austria") == max(-100, austria - 15)

    def test_the_chip_says_it_too(self, _r10_world):
        from backend.game_logic.diplomacy import _instrument_actions
        from backend.game_logic.instruments import guarantee_honour_cost_clause
        w = _r10_world
        with _r10_quiet():
            chip = next(a for a in _instrument_actions(w, "France", "Prussia")
                        if a["action"] == "guarantee_nation")
        assert guarantee_honour_cost_clause() in chip["effect_text"], chip

    def test_the_quote_still_names_the_abandonment_clock(self, _r10_world):
        text = _r10_say(_r10_world, "guarantee Prussia", action="guarantee_nation")["message"]
        assert "France would have 2 turns to enter that war, or the pledge is abandoned" in text
        assert "their willingness falls by 8" in text


class TestS14GX45:
    """The buy-off names no later third-party cost, and none exists: a
    purchase between two courts licenses no war (pinned so a later change that
    adds one is made on purpose)."""

    def test_the_buyoff_quote_names_no_declaration_cost(self, _r10_world):
        from backend.commands.executor import CommandExecutor
        w = _r10_world
        w.nation_relations[w._make_diplo_key("France", "Prussia")] = -30
        with _r10_quiet():
            out = CommandExecutor().execute(
                {"command": {"action": "buy_off_design", "target": "Prussia",
                             "raw_input": "buy off Prussia"}}, {"world": w})
        text = out["message"]
        assert "declares on" not in text and "every court" not in text


# ══════════════════════════════════════════════════════════════════════════
# row11
# ══════════════════════════════════════════════════════════════════════════
# S14G-11 (Pre-Deploy S14h part 1, October 26, 2026) - guarded ground is said
# before it is crossed.
#
# The cause as traced (DD-B's third measure, conquest #10, turn 10, action 251,
# `docs/audits/dd_b/conquest_2026_10_25/frames/0251.jpg`): "Soult, march to
# Flanders" answered "Route: Dresden -> Berlin -> Brunswick -> Amsterdam ->
# Flanders" and nothing else. Prussia had taken up Armed Neutrality the same turn
# (Hanover, Westphalia, Brunswick, Berlin, Brandenburg), and on turn 13 "Prussia
# seethes: France's columns cross Brunswick in defiance of its declared
# neutrality" - the Ansbach trap (`agendas.process_agenda_violations`,
# NATION_AGENDAS_SPEC section 5.9), -25 with Prussia, the relation at -32, a
# courting mission undone, an Open Borders signed on turn 2 notwithstanding (it is
# no exemption: the trap reads war and armistice, an ally, a lord or client and
# one's own soil). `march_detour_reading` returned None because a guarded province
# is OPEN ground; the reply printed only the route; the "takes up a new design:
# Armed Neutrality" beat carried only the title; the Open Borders letter said "each
# side's armies may cross the other's provinces".
#
# What the fix does:
#
# * `agendas.guarded_provinces_for(world, violator)` - the guard map and the
#   nation-level exemptions, factored out of `process_agenda_violations`, which
#   now reads it (so the ask and the trap cannot disagree); THE SEAM;
# * `strategic.march_guard_reading` / `march_guard_sentence` - the guarded ground
#   a lawful road crosses and its sentence, built from the trap's own clause
#   (`agendas.guard_ground_clause`: the design's provinces and the constant the
#   trap charges); player only;
# * `strategic_executor.march_guard_ask` - a typed march, hold, support, follow or
#   pursuit whose road crosses guarded ground asks FIRST, free, on the detour
#   ask's channel ("... - march, go round or cancel?"); a detour that also crosses
#   guarded ground carries the sentence in its OWN question; "march" issues the
#   order with the sentence after its route, "go round" takes the road round the
#   guarded provinces (offered only when one exists);
# * the march quote carries `guard`, the desk and the card and the panel print it;
# * the shift beat, the Diplomacy ledger's stance line and the Open Borders effect
#   line carry the provinces and the price, through the same constant.
#
# Siblings fixed here: S14G-X43 (the desk's buy-off answer named no league
# consequence), S14G-X17 (a group's member line printed his name twice),
# S14G-X36 (the design confirm's summary printed its cession twice), S14G-X47
# (S14G-7's front note reaches the typed march's reply and the per-turn step),
# S14G-X48 (the quote's `terms`, `front` and `guard` reach the desk, the card,
# the group card and the panel, army rows included), S14G-X49 (the stance line).

_R11_ROOT = Path(__file__).resolve().parents[1]
_R11_SCENARIO = (_R11_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")
_R11_SCRIPTS = _R11_ROOT / "godot-client" / "project-sovereign" / "scripts"

_R11_SENTENCE = ("Berlin and Brunswick are Prussia's guarded ground (Armed Neutrality) "
                 "— standing in them costs −25 with Prussia.")
_R11_FRONT = ("Swabia is Bavaria's front — Austria, under truce with us, is at war with her; "
              "a corps there will not fight, and marches home if the ground changes hands.")


def _r11_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r11_boot():
    from backend.models.world_state import WorldState
    with _r11_quiet():
        return WorldState.from_scenario(str(_R11_SCENARIO))


def _r11_copy(boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


def _r11_set(w, a: str, b: str, state: str) -> None:
    from backend.game_logic.diplomacy import set_diplomatic_state
    with _r11_quiet():
        set_diplomatic_state(w, a, b, state, "test")


def _r11_armed(w) -> None:
    """Prussia's Hanoverian prize is satisfied (Hanover, Brunswick, Westphalia
    are hers) and she is at peace: her second design, Armed Neutrality, is the
    ACTIVE one; France and Prussia have signed Open Borders."""
    for name in ("Hanover", "Brunswick", "Westphalia"):
        w.regions[name].controller = "Prussia"
    _r11_set(w, "France", "Prussia", "OPEN_BORDERS")
    w.invalidate_active_nations_cache()
    w.invalidate_bloc_members_cache()


def _r11_board(boot):
    """The sighting's board: Prussia armed-neutral, Open Borders signed, Soult
    (literal, one province a turn, 1 AP) at Dresden. The lawful road to
    Flanders is Dresden -> Berlin -> Brunswick -> Amsterdam -> Flanders."""
    from backend.game_logic.agendas import get_active_agenda
    w = _r11_copy(boot)
    _r11_armed(w)
    assert get_active_agenda("Prussia", w).id == "armed_neutrality"
    assert w.get_diplomatic_state("France", "Prussia") == "OPEN_BORDERS"
    soult = w.get_marshal("Soult")
    assert soult.personality == "literal" and soult.movement_range == 1
    soult.location = "Dresden"
    with _r11_quiet():
        w.calculate_visibility()
    return w


@pytest.fixture
def _r11_w(_r11_boot):
    return _r11_board(_r11_boot)


@contextlib.contextmanager
def _r11_client(w):
    """The player's road: /command on a swapped world (three globals, restored)."""
    with _r11_quiet():
        import backend.main as M
        from backend.commands.parser import CommandParser
        from fastapi.testclient import TestClient
    saved = (M.game_state["world"], M.world, M.parser)
    M.game_state["world"] = w
    M.world = w
    M.parser = CommandParser(use_real_llm=False)
    try:
        yield TestClient(M.app)
    finally:
        M.game_state["world"], M.world, M.parser = saved


def _r11_say(client, text: str) -> dict:
    with _r11_quiet():
        return client.post("/command", json={"command": text}).json()


def _r11_guarded(w, nation="France"):
    from backend.game_logic.agendas import guarded_provinces_for
    return guarded_provinces_for(w, nation)


# ══════════════════════════════════════════════════════════════════════════
# S14G-11 - the guarded ground, said at the order
# ══════════════════════════════════════════════════════════════════════════

class TestS14G11:
    """The sighting, reproduced on the shipped 1805 board: Prussia armed-neutral,
    Open Borders signed, Soult at Dresden, "Soult, march to Flanders". Old
    reading: accepted at once (1 AP, Soult at Berlin) with the reply "Route:
    Berlin -> Brunswick -> Amsterdam -> Flanders." and no word of the -25."""

    def test_the_guard_map_and_the_reading(self, _r11_w):
        from backend.commands import strategic as S
        w = _r11_w
        guarded = _r11_guarded(w)
        assert {r for r, h in guarded.items() if h == "Prussia"} == {
            "Hanover", "Westphalia", "Brunswick", "Berlin", "Brandenburg"}
        soult = w.get_marshal("Soult")
        road, refusal, _kind = S.march_road(w, soult, "Flanders", "MOVE_TO")
        assert refusal is None and road == ["Berlin", "Brunswick", "Amsterdam", "Flanders"]
        reading = S.march_guard_reading(w, soult, "Flanders", road, "MOVE_TO")
        assert reading["provinces"] == ["Berlin", "Brunswick"]
        assert reading["holder"] == "Prussia" and reading["design_title"] == "Armed Neutrality"
        assert reading["penalty"] == -25 and isinstance(reading["penalty"], int)
        assert S.march_guard_sentence(reading) == _R11_SENTENCE

    def test_the_typed_march_asks_first_and_spends_nothing(self, _r11_w):
        w = _r11_w
        soult = w.get_marshal("Soult")
        ap = int(w.actions_remaining)
        with _r11_client(w) as client:
            out = _r11_say(client, "Soult, march to Flanders")
        assert out.get("state") == "awaiting_clarification", out.get("message")
        assert out.get("clarification_kind") == "march_guard_ask"
        assert out.get("free_action") is True
        assert out["marshal"] == "Berthier" and out["interpreted_target"] == "Flanders"
        assert out["message"] == _R11_SENTENCE.rstrip(".") + " — march, go round or cancel?"
        # nothing walked, nothing spent, no order standing
        assert soult.location == "Dresden" and soult.strategic_order is None
        assert int(w.actions_remaining) == ap
        assert (out.get("action_info") or {}).get("cost", 0) == 0
        march, around = out["options"]
        assert march["label"] == "March (1 AP)" and march["command"] == "Soult, march to Flanders"
        assert march["flags"] == {"_guard_confirmed": True}
        assert around["label"] == "Go round (1 AP, 5 provinces)"
        assert around["flags"] == {"_march_confirmed": True, "_guard_confirmed": True,
                                   "_guard_go_round": True}
        # a button click re-sends an option's command verbatim: the two must differ
        assert around["command"] != march["command"]
        assert around["command"].replace("  ", " ", 1) == march["command"]

    def test_march_issues_the_order_and_the_reply_says_it_after_the_route(self, _r11_w):
        w = _r11_w
        soult = w.get_marshal("Soult")
        ap = int(w.actions_remaining)
        with _r11_client(w) as client:
            ask = _r11_say(client, "Soult, march to Flanders")
            assert ask.get("clarification_kind") == "march_guard_ask"
            out = _r11_say(client, "march")
        assert out.get("success") is True, out.get("message")
        assert out.get("state") != "awaiting_clarification"      # one question, never two
        msg = out["message"]
        assert ("Route: Berlin → Brunswick → Amsterdam → Flanders. " + _R11_SENTENCE) in msg, msg
        assert soult.strategic_order is not None and soult.strategic_order.target == "Flanders"
        assert int(w.actions_remaining) == ap - 1                # the literal's 1 AP, once
        assert soult.location == "Berlin"

    def test_the_price_stated_is_the_price_charged(self, _r11_w):
        """The ask's -25 is the trap's: march anyway, stand in Berlin, the pass
        charges exactly the sentence's figure."""
        from backend.game_logic.agendas import process_agenda_violations
        w = _r11_w
        key = w._make_diplo_key("France", "Prussia")
        before = int(w.nation_relations.get(key, 0))
        with _r11_client(w) as client:
            _r11_say(client, "Soult, march to Flanders")
            _r11_say(client, "march")
        with _r11_quiet():
            events = process_agenda_violations(w)
        assert [(e["violator"], e["guard_holder"], e["region"]) for e in events] == [
            ("France", "Prussia", "Berlin")]
        assert int(w.nation_relations.get(key, 0)) == max(-100, before - 25)

    def test_go_round_takes_the_road_that_avoids_the_guarded_ground(self, _r11_w):
        w = _r11_w
        soult = w.get_marshal("Soult")
        ap = int(w.actions_remaining)
        with _r11_client(w) as client:
            _r11_say(client, "Soult, march to Flanders")
            out = _r11_say(client, "go round")
        assert out.get("success") is True, out.get("message")
        msg = out["message"]
        assert "Route: Franconia → Swabia → Rhineland → Brabant → Flanders." in msg, msg
        assert ("The road goes round the guarded ground at Berlin and Brunswick, "
                "and Prussia is not offended.") in msg, msg
        assert "costs −25" not in msg
        order = soult.strategic_order
        assert order is not None and order.target == "Flanders"
        guarded = set(_r11_guarded(w))
        assert not guarded & set([soult.location] + list(order.path))
        assert int(w.actions_remaining) == ap - 1
        assert "  " not in order.original_command      # the order keeps the player's own words

    def test_the_buttons_own_command_resolves_to_go_round(self, _r11_w):
        w = _r11_w
        soult = w.get_marshal("Soult")
        with _r11_client(w) as client:
            ask = _r11_say(client, "Soult, march to Flanders")
            around = ask["options"][1]
            out = _r11_say(client, around["command"])
        assert out.get("success") is True, out.get("message")
        assert "The road goes round the guarded ground at Berlin and Brunswick" in out["message"]
        assert soult.location == "Franconia"

    def test_cancel_spends_nothing(self, _r11_w):
        w = _r11_w
        soult = w.get_marshal("Soult")
        ap = int(w.actions_remaining)
        with _r11_client(w) as client:
            _r11_say(client, "Soult, march to Flanders")
            out = _r11_say(client, "cancel")
        assert out.get("success") is True and "withdrawn" in out["message"]
        assert soult.location == "Dresden" and soult.strategic_order is None
        assert int(w.actions_remaining) == ap

    def test_a_road_that_crosses_no_guarded_ground_never_asks(self, _r11_w):
        w = _r11_w
        soult = w.get_marshal("Soult")
        with _r11_client(w) as client:
            out = _r11_say(client, "Soult, march to Bohemia")
        assert out.get("state") != "awaiting_clarification", out.get("message")
        assert "guarded ground" not in out["message"]
        assert soult.strategic_order is not None

    def test_open_borders_is_no_exemption_and_its_letter_says_so(self, _r11_w):
        """Open Borders was signed (the board's own state) and the ask still
        fires; the effect line of the clause now says why, through the trap's
        constant (and an alliance letter - whose allies the trap exempts - does
        not say it)."""
        from backend.display_names import clause_effect_words
        assert _r11_w.get_diplomatic_state("France", "Prussia") == "OPEN_BORDERS"
        line = clause_effect_words("open_borders", "open_borders")
        assert ("each side's armies may cross the other's provinces — but not a province she "
                "has declared guarded (Armed Neutrality): a column there still offends her (−25)") in line
        assert "each side's armies may cross the other's provinces" in clause_effect_words(
            "open_borders", "alliance")
        assert "declared guarded" not in clause_effect_words("open_borders", "alliance")
        assert "declared guarded" in clause_effect_words("open_borders", "non_aggression")

    def test_the_price_is_one_constant(self, _r11_w, monkeypatch):
        from backend.commands import strategic as S
        from backend.display_names import clause_effect_words
        from backend.game_logic import agendas as A
        w = _r11_w
        monkeypatch.setattr(A, "AGENDA_VIOLATION_RELATION_PENALTY", -40)
        assert "(−40)" in clause_effect_words("open_borders", "open_borders")
        soult = w.get_marshal("Soult")
        reading = S.march_guard_reading(w, soult, "Flanders",
                                        ["Berlin", "Brunswick", "Amsterdam", "Flanders"], "MOVE_TO")
        assert reading["penalty"] == -40
        assert "costs −40 with Prussia" in S.march_guard_sentence(reading)

    def test_the_shift_beat_names_the_provinces_and_the_price(self, _r11_boot):
        from backend.campaign_log import format_event_oneliner
        from backend.game_logic.agendas import process_agenda_shifts
        from backend.game_logic.dispatch import _DIPLOMATIC_EVENT_TEMPLATES
        w = _r11_copy(_r11_boot)
        with _r11_quiet():
            process_agenda_shifts(w)                       # the boot is recorded silently
        assert w.nation_agenda_seen["Prussia"] == "hanoverian_prize"
        w.pending_dispatch_events = []
        _r11_armed(w)
        with _r11_quiet():
            events = process_agenda_shifts(w)
        assert [e["agenda_id"] for e in events if e["nation"] == "Prussia"] == ["armed_neutrality"]
        (beat,) = [e for e in w.pending_dispatch_events
                   if (e.get("event_type") or e.get("type")) == "agenda_shift"
                   and e["template_vars"]["nation"] == "Prussia"]
        focus = beat["template_vars"]["focus"]
        assert focus == ("Armed Neutrality — Hanover, Westphalia, Brunswick, Berlin and Brandenburg "
                         "are Prussia's guarded ground — standing in them costs −25 with Prussia")
        line = _DIPLOMATIC_EVENT_TEMPLATES["agenda_shift"].format(nation="Prussia", focus=focus)
        assert line == ("The court of Prussia takes up a new design: " + focus + ".")
        (logged,) = [e for e in w.event_log if e["type"] == "agenda_shift" and e["nation"] == "Prussia"]
        assert format_event_oneliner(logged) == "The court of Prussia takes up a new design: " + focus

    def test_a_shift_to_any_other_design_carries_its_title_alone(self, _r11_boot):
        """The negative control: a shift to a design that guards nothing."""
        from backend.game_logic.agendas import process_agenda_shifts
        w = _r11_copy(_r11_boot)
        with _r11_quiet():
            process_agenda_shifts(w)
        w.pending_dispatch_events = []
        w.nation_agenda_seen["Austria"] = "__stale__"
        with _r11_quiet():
            process_agenda_shifts(w)
        (beat,) = [e for e in w.pending_dispatch_events
                   if (e.get("event_type") or e.get("type")) == "agenda_shift"
                   and e["template_vars"]["nation"] == "Austria"]
        assert beat["template_vars"]["focus"] == "Redeem Italy"

    def test_the_march_quote_carries_the_sentence(self, _r11_w):
        from backend.commands.order_quotes import march_quote, march_quotes_for_region
        w = _r11_w
        soult = w.get_marshal("Soult")
        q = march_quote(w, soult, "Flanders")
        assert q["ok"] and q["guard"] == _R11_SENTENCE and q["front"] == ""
        assert march_quote(w, soult, "Bohemia")["guard"] == ""
        row = next(r for r in march_quotes_for_region(w, "Flanders")["march"]
                   if r["marshal"] == "Soult")
        assert row["guard"] == _R11_SENTENCE
        # the quote and the ask print one sentence
        with _r11_client(w) as client:
            ask = _r11_say(client, "Soult, march to Flanders")
        assert ask["message"].startswith(q["guard"].rstrip("."))

    def test_the_desk_prints_it_before_the_order(self, _r11_w):
        from backend.ai.state_desk import _answer_march_cost
        text = _answer_march_cost(_r11_w, "Flanders", "Soult")
        assert _R11_SENTENCE in text, text

    def test_the_cooldown_the_trap_keeps_is_the_asks_too(self, _r11_w):
        """A pair that already paid inside the window is not asked about again
        for a -25 the trap will not charge; the window passing restores it."""
        from backend.commands import strategic as S
        from backend.game_logic.agendas import AGENDA_VIOLATION_COOLDOWN, process_agenda_violations
        w = _r11_w
        soult = w.get_marshal("Soult")
        road = ["Berlin", "Brunswick", "Amsterdam", "Flanders"]
        w.marshals["Ney"].location = "Berlin"
        with _r11_quiet():
            assert len(process_agenda_violations(w)) == 1
        assert S.march_guard_reading(w, soult, "Flanders", road, "MOVE_TO") is None
        w.current_turn += AGENDA_VIOLATION_COOLDOWN
        assert S.march_guard_reading(w, soult, "Flanders", road, "MOVE_TO") is not None

    def test_the_ais_column_pays_the_trap_and_never_asks(self, _r11_w):
        """Golden Rule 5: the reading is the player's corps only; the AI's column
        pays the trap exactly as before."""
        from backend.commands import strategic as S
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.agendas import process_agenda_violations
        w = _r11_w
        british = next(m for m in w.marshals.values() if m.nation == "Britain")
        british.location = "Brunswick"
        assert S.march_guard_reading(w, british, "Flanders", ["Amsterdam", "Flanders"], "MOVE_TO") is None
        assert S.march_guard_reading(w, british, "Flanders", ["Brunswick", "Flanders"], "MOVE_TO") is None
        with _r11_quiet():
            events = process_agenda_violations(w)
        assert [(e["violator"], e["guard_holder"]) for e in events] == [("Britain", "Prussia")]
        with _r11_quiet():
            out = CommandExecutor().execute({
                "command": {"raw_input": f"{british.name}, march to Flanders",
                            "marshal": british.name, "action": "move", "target": "Flanders"},
                "is_strategic": True, "strategic_type": "MOVE_TO"}, {"world": w})
        assert out.get("state") != "awaiting_clarification"

    def test_the_ask_has_one_caller_and_the_ai_source_never_reads_it(self):
        text = (_R11_ROOT / "backend" / "commands" / "strategic_executor.py").read_text(encoding="utf-8")
        assert text.count("march_guard_ask(") == 2            # the definition and the road stage
        ai_src = (_R11_ROOT / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        assert "march_guard" not in ai_src


class TestS14G11TheTrapSeam:
    """The seam: `agendas.guarded_provinces_for`. The trap reads its map through
    the module global, so the ask and the trap cannot disagree; the refactor is
    identity for the AI (the existing agenda tests stay green) and these pins show
    the helper IS the trap's own reading state by state."""

    @pytest.mark.parametrize("state", ["PEACE", "OPEN_BORDERS", "NON_AGGRESSION",
                                       "DEFENSIVE_ALLIANCE", "ALLIANCE", "ARMISTICE", "WAR"])
    def test_the_helper_equals_what_the_trap_fires_on(self, _r11_boot, state):
        from backend.game_logic.agendas import process_agenda_violations
        w = _r11_copy(_r11_boot)
        _r11_armed(w)
        _r11_set(w, "France", "Prussia", state)
        w.invalidate_bloc_members_cache()
        w.marshals["Ney"].location = "Berlin"
        with _r11_quiet():
            fired = bool(process_agenda_violations(w))
        assert fired == ("Berlin" in _r11_guarded(w)), state
        assert fired == (state in ("PEACE", "OPEN_BORDERS", "NON_AGGRESSION")), state

    def test_own_soil_a_lord_a_client_and_a_peaceful_nation_are_exempt_in_both(self, _r11_boot):
        from backend.game_logic.agendas import process_agenda_violations
        # own soil: a garrison on a province France holds is no transit (Brandenburg,
        # not Berlin - Prussia's capital lost is her survival override, no guard at all)
        w = _r11_copy(_r11_boot)
        _r11_armed(w)
        w.regions["Brandenburg"].controller = "France"
        w.invalidate_active_nations_cache()
        w.invalidate_bloc_members_cache()
        w.marshals["Ney"].location = "Brandenburg"
        assert "Brandenburg" not in _r11_guarded(w) and "Berlin" in _r11_guarded(w)
        with _r11_quiet():
            assert process_agenda_violations(w) == []
        w.marshals["Ney"].location = "Berlin"
        with _r11_quiet():
            assert len(process_agenda_violations(w)) == 1
        # a lord's guard is no outrage to its client, and a client's none to its lord
        for lord, client in (("Prussia", "France"), ("France", "Prussia")):
            w = _r11_copy(_r11_boot)
            _r11_armed(w)
            w.vassals[client] = {"lord": lord}
            w.marshals["Ney"].location = "Berlin"
            fired = bool(process_agenda_violations(w))
            assert fired == ("Berlin" in _r11_guarded(w)), (lord, client)
        # peace with the whole world: only a belligerent's columns offend
        w = _r11_copy(_r11_boot)
        _r11_armed(w)
        for nation in list(w.get_nations_at_war_with("France")):
            w.diplomatic_states[w._make_diplo_key("France", nation)] = "PEACE"
        w.invalidate_bloc_members_cache()
        w.marshals["Ney"].location = "Berlin"
        assert _r11_guarded(w) == {}
        with _r11_quiet():
            assert process_agenda_violations(w) == []

    def test_the_trap_reads_the_helper_through_the_module_global(self, _r11_boot, monkeypatch):
        """THE SEAM: patched to the empty reading the trap never fires; the ask,
        which reads the same helper, never asks."""
        from backend.commands import strategic as S
        from backend.game_logic import agendas as A
        w = _r11_board(_r11_boot)
        w.marshals["Ney"].location = "Berlin"
        monkeypatch.setattr(A, "guarded_provinces_for", lambda world, violator: {})
        with _r11_quiet():
            assert A.process_agenda_violations(w) == []
        assert S.march_guard_reading(w, w.get_marshal("Soult"), "Flanders",
                                     ["Berlin", "Brunswick", "Amsterdam", "Flanders"], "MOVE_TO") is None
        monkeypatch.undo()
        with _r11_quiet():
            assert len(A.process_agenda_violations(w)) == 1

    def test_the_cooldown_is_lifted_unchanged(self, _r11_boot):
        from backend.game_logic.agendas import AGENDA_VIOLATION_COOLDOWN, violation_on_cooldown
        w = _r11_copy(_r11_boot)
        assert violation_on_cooldown(w, "France", "Prussia") is False
        w.log_event({"type": "agenda_violation", "violator": "France", "guard_holder": "Prussia"})
        assert violation_on_cooldown(w, "France", "Prussia") is True
        assert violation_on_cooldown(w, "France", "Denmark") is False
        w.current_turn += AGENDA_VIOLATION_COOLDOWN
        assert violation_on_cooldown(w, "France", "Prussia") is False
        w.current_turn -= AGENDA_VIOLATION_COOLDOWN
        cap = w.MAX_EVENT_LOG_SIZE
        w.event_log = [{"type": "noise", "turn": int(w.current_turn)} for _ in range(cap)]
        assert violation_on_cooldown(w, "France", "Prussia") is True     # the rolled log fails SAFE

    def test_the_helper_is_deck_agnostic(self, _r11_boot, monkeypatch):
        """Poland's Guard the Vistula and Ulster/Munster's Erin Free read through
        the same helper: an active guard design is a guard, whoever authored it."""
        from backend.game_logic import agendas as A
        w = _r11_copy(_r11_boot)
        views = {
            "Poland": A.AgendaView(nation="Poland", id="guard_the_vistula", type="guard_neutrality",
                                   title="Guard the Vistula", blurb="",
                                   regions=("Posen", "Lithuania", "Volhynia"), params={}),
            "Ireland": A.AgendaView(nation="Ireland", id="erin_free", type="guard_neutrality",
                                    title="Erin Free", blurb="", regions=("Ulster", "Munster"),
                                    params={}),
        }
        real = A.get_active_agenda
        monkeypatch.setattr(w, "get_active_nations", lambda: ["France", *views])
        monkeypatch.setattr(A, "get_active_agenda",
                            lambda nation, world: views.get(nation) or real(nation, world))
        guarded = _r11_guarded(w)
        assert {r: h for r, h in guarded.items() if h == "Poland"} == {
            "Posen": "Poland", "Lithuania": "Poland", "Volhynia": "Poland"}
        assert {r: h for r, h in guarded.items() if h == "Ireland"} == {
            "Ulster": "Ireland", "Munster": "Ireland"}
        assert A.guard_ground_clause(w, "Poland", ["Posen", "Lithuania", "Volhynia"], "Guard the Vistula") == (
            "Posen, Lithuania and Volhynia are Poland's guarded ground (Guard the Vistula) "
            "— standing in them costs −25 with Poland")

    def test_denmarks_holstein_asks_the_same_question(self, _r11_boot):
        """The other deck on the shipped board: Denmark's Neutrality of the North
        (active at boot, Holstein and Copenhagen). Ney's road to Holstein crosses
        Gelderland, Brunswick and Hanover - none of them guarded here."""
        from backend.commands import strategic as S
        w = _r11_copy(_r11_boot)
        _r11_set(w, "France", "Denmark", "OPEN_BORDERS")
        _r11_set(w, "France", "Hanover", "OPEN_BORDERS")
        ney = w.get_marshal("Ney")
        road, refusal, _kind = S.march_road(w, ney, "Copenhagen", "MOVE_TO")
        assert refusal is None
        reading = S.march_guard_reading(w, ney, "Copenhagen", road, "MOVE_TO")
        assert reading["holder"] == "Denmark" and reading["provinces"] == ["Holstein", "Copenhagen"]
        assert S.march_guard_sentence(reading) == (
            "Holstein and Copenhagen are Denmark's guarded ground (Neutrality of the North) "
            "— standing in them costs −25 with Denmark.")
        assert S.march_guard_round_road(w, ney, "Copenhagen", "MOVE_TO") is None      # the destination is guarded
        # the Ottoman deck, too: the helper names the Straits
        assert {r: h for r, h in _r11_guarded(w).items() if h == "Ottoman"} == {
            "Constantinople": "Ottoman", "Rumelia": "Ottoman"}


class TestS14G11EveryOrderWhoseRoadCrossesGuardedGround:
    """The sweep's class: a hold on a guarded province, a support whose ally
    stands on one, the Staff's army order, a detour that also crosses guarded
    ground."""

    def test_a_hold_on_a_guarded_province_asks_and_says_it_after(self, _r11_w):
        w = _r11_w
        soult = w.get_marshal("Soult")
        with _r11_client(w) as client:
            out = _r11_say(client, "Soult, hold Berlin")
            assert out.get("clarification_kind") == "march_guard_ask", out.get("message")
            assert out["message"] == ("Berlin is Prussia's guarded ground (Armed Neutrality) — "
                                      "standing in it costs −25 with Prussia — hold, or cancel?")
            assert len(out["options"]) == 1                  # the destination itself is guarded: no way round
            done = _r11_say(client, "hold")
        assert done.get("success") is True, done.get("message")
        assert "Berlin is Prussia's guarded ground (Armed Neutrality)" in done["message"]
        assert soult.strategic_order is not None and soult.strategic_order.command_type == "HOLD"

    def test_a_support_whose_ally_stands_on_guarded_ground_asks(self, _r11_w):
        w = _r11_w
        w.get_marshal("Davout").location = "Berlin"
        soult = w.get_marshal("Soult")
        with _r11_client(w) as client:
            out = _r11_say(client, "Soult, support Davout")
            assert out.get("clarification_kind") == "march_guard_ask", out.get("message")
            assert out["message"] == ("Berlin is Prussia's guarded ground (Armed Neutrality) — "
                                      "standing in it costs −25 with Prussia — support, or cancel?")
            done = _r11_say(client, "support")
        assert done.get("success") is True, done.get("message")
        assert "moves to support Davout (at Berlin). Berlin is Prussia's guarded ground" in done["message"]
        assert soult.strategic_order is not None and soult.strategic_order.command_type == "SUPPORT"

    def test_the_staffs_army_order_is_never_asked_and_says_it(self, _r11_w):
        from backend.commands.executor import CommandExecutor
        w = _r11_w
        with _r11_quiet():
            out = CommandExecutor().execute({
                "command": {"raw_input": "Soult, march to Flanders", "marshal": "Soult",
                            "action": "move", "target": "Flanders", "_army_order": True},
                "is_strategic": True, "strategic_type": "MOVE_TO"}, {"world": w})
        assert out.get("state") != "awaiting_clarification", out.get("message")
        assert _R11_SENTENCE in out["message"], out["message"]

    def test_a_detour_that_crosses_guarded_ground_asks_once_with_both_sentences(self, _r11_w, monkeypatch):
        """A road the diplomacy detours (the S14E-22 reading, here stood in by a
        fixed reading - no shipped board both shuts the direct road and leaves a
        guarded province on the lawful one) that ALSO crosses guarded ground asks
        ONE question carrying both sentences; "march" confirms both flags and the
        order is issued with no second ask."""
        from backend.commands import strategic as S
        w = _r11_w
        soult = w.get_marshal("Soult")
        reading = {"via": "Hanover", "closed_by": "Hanover", "state": "PEACE", "direct": 3,
                   "lawful": 4, "turns": 4, "courts": ["Prussia"], "foreign": ["Prussia"]}
        monkeypatch.setattr(S, "march_detour_reading", lambda *a, **k: reading)
        with _r11_client(w) as client:
            out = _r11_say(client, "Soult, march to Flanders")
            assert out.get("clarification_kind") == "march_detour_ask", out.get("message")
            assert out["message"] == (
                "The direct road to Flanders via Hanover is closed — Hanover keeps its frontier shut; "
                "the lawful road is 4 provinces, 4 turns, through Prussia. " + _R11_SENTENCE.rstrip(".")
                + " — march, go round or cancel?")
            march, around = out["options"]
            assert march["flags"] == {"_march_confirmed": True, "_guard_confirmed": True}
            assert around["flags"]["_guard_go_round"] is True and around["command"] != march["command"]
            done = _r11_say(client, "march")
        assert done.get("success") is True, done.get("message")
        assert done.get("state") != "awaiting_clarification"          # one question, never two
        assert _R11_SENTENCE in done["message"]
        assert soult.strategic_order is not None and soult.strategic_order.target == "Flanders"


# ══════════════════════════════════════════════════════════════════════════
# S14G-X49 - the stance line names every guarded province
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX49:
    """The Diplomacy ledger's stance line named the FIRST guarded province and
    called a crossing "an outrage" ("Armed and neutral — foreign columns near
    Hanover would be an outrage."); it now says every province and the price,
    in the one clause."""

    def test_the_stance_line(self, _r11_w):
        from backend.game_logic.agendas import build_agenda_payload
        payload = build_agenda_payload("Prussia", _r11_w)
        assert payload["stance_line"] == (
            "Armed and neutral — Hanover, Westphalia, Brunswick, Berlin and Brandenburg "
            "are Prussia's guarded ground — standing in them costs −25 with Prussia.")
        assert "an outrage" not in payload["stance_line"]


# ══════════════════════════════════════════════════════════════════════════
# S14G-X43 - the desk's buy-off answer says what the buy-off does to a league
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX43:
    """S14G-X43 (the S14G-9 / S14G-D6 sweep): "Buying off Britain's design would
    cost 1,100 gold, Sire, and one diplomatic point." said gold and a point and
    nothing of the league - the buy-off quote, the Balance page and the wizard's
    chip all carry `instruments.buyoff_league_clause`. The desk's answer is the
    same sentence, with the live relation."""

    def test_the_desk_answer_carries_the_league_clause(self, _r11_boot):
        from backend.ai.state_desk import _answer_buyoff
        from backend.game_logic.instruments import buyoff_league_clause, compute_buyoff_price
        w = _r11_copy(_r11_boot)
        price = compute_buyoff_price(w, "Britain")
        assert price is not None
        relation = int(w.nation_relations.get(w._make_diplo_key("France", "Britain"), 0) or 0)
        said = _answer_buyoff(w, "Britain")
        assert said.startswith("Buying off Britain's design would cost ")
        assert "gold, Sire, and one diplomatic point." in said
        assert (f"It buys the design's sleep, not her goodwill: {buyoff_league_clause(relation)}.") in said, said

    def test_a_court_with_no_design_is_unchanged(self, _r11_boot):
        from backend.ai.state_desk import _answer_buyoff
        w = _r11_copy(_r11_boot)
        said = _answer_buyoff(w, "Portugal")
        assert "league" not in said


# ══════════════════════════════════════════════════════════════════════════
# S14G-X17 - a group's member line prints his name once
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX17:
    """S14G-X17's sibling in the group's own formatting: "everyone, march to
    Rhineland" with Ney and Davout already standing there printed "Ney: Ney
    already stands at Rhineland - nothing spent." - the group's "Name: " prefix
    over a reply that opens with the name. The refusal sentence is shared with
    the quote and the typed order, so the line is fixed where it is formatted."""

    def test_the_member_line_reads_the_refusal_once(self, _r11_boot):
        w = _r11_copy(_r11_boot)
        assert w.get_marshal("Ney").location == "Rhineland" == w.get_marshal("Davout").location
        with _r11_client(w) as client:
            out = _r11_say(client, "everyone, march to Rhineland")
        text = str(out.get("message") or "")
        assert "\nNey already stands at Rhineland — nothing spent." in text, text
        assert "\nDavout already stands at Rhineland — nothing spent." in text, text
        assert "Ney: Ney" not in text and "Davout: Davout" not in text

    def test_the_prefix_stays_where_the_reply_does_not_open_with_his_name(self):
        from backend.commands.group_orders import _member_line
        assert _member_line("Ney", "Ney halts his march and awaits new orders.") == (
            "Ney halts his march and awaits new orders.")
        assert _member_line("Ney", "Ney's order stands.") == "Ney's order stands."
        assert _member_line("Ney", "The order is refused.") == "Ney: The order is refused."
        assert _member_line("Ney", "Neyland is far.") == "Ney: Neyland is far."       # a name, not a prefix
        assert _member_line("Ney", "") == "Ney: done."
        assert _member_line("ArchdukeJohn", "Archduke John begins march to Tyrol.") == (
            "Archduke John begins march to Tyrol.")


# ══════════════════════════════════════════════════════════════════════════
# S14G-X36 - the design confirm's summary prints its cession once
# ══════════════════════════════════════════════════════════════════════════

def _r11_confirm(boot) -> dict:
    """The S14G-8 stage: Talleyrand's "Satisfy their design (Britain)" counsel
    opens a proposal_confirm pre-loaded with the peace and the cession of
    Flanders (the string clause `territory_flanders` AND the structured
    `territory_cede` sweetener)."""
    from backend.commands.executor import CommandExecutor
    from backend.game_logic.diplomatic_advisory import generate_advisory
    w = _r11_copy(boot)
    with _r11_quiet():
        executor = CommandExecutor()
        advice = generate_advisory(None, "assess_situation", w)
        w.dialogue_manager.replace(advice)
        reply = executor.handle_diplomatic_dialogue_response(1, {"world": w})
    return reply["diplomatic_dialogue"]


class TestS14GX36:
    """S14G-X36 (found by S14G-8's build, filed under row 8): the confirm's
    `proposal_terms_summary` printed a cession twice - "Territory Flanders" (the
    legacy string clause) then "France cedes Flanders" (the structured
    sweetener); the client reads `annotated_terms`, which has one row. The
    summary now prints the structured clause and drops the string clause naming
    the same province; a string clause with no structured twin stands alone."""

    def test_the_summary_prints_the_cession_once(self, _r11_boot):
        dialogue = _r11_confirm(_r11_boot)
        assert dialogue["type"] == "proposal_confirm"
        lines = dialogue["proposal_terms_summary"]
        assert lines[:2] == ["Peace Treaty (end state of war)", "France cedes Flanders"], lines
        assert sum("Flanders" in line for line in lines) == 1, lines
        assert "Territory Flanders" not in lines
        assert [row["display_label"] for row in dialogue["annotated_terms"]
                if "Flanders" in row.get("display_label", "")] == ["France cedes Flanders to Britain"]

    def test_a_string_clause_alone_and_a_different_province_stand(self):
        from backend.display_names import format_terms_for_display
        alone = {"type": "peace", "proposer_nation": "France", "target_nation": "Britain",
                 "sweeteners": [], "demands": [], "clauses": ["territory_flanders"]}
        assert "Territory Flanders" in format_terms_for_display(alone, "peace", "Britain")
        other = dict(alone, sweeteners=[{"type": "territory_cede", "value": 1, "regions": ["Artois"]}])
        lines = format_terms_for_display(other, "peace", "Britain")
        assert "Territory Flanders" in lines and "France cedes Artois" in lines
        twin = dict(alone, sweeteners=[{"type": "territory_cede", "value": 1, "regions": ["Flanders"]}])
        lines = format_terms_for_display(twin, "peace", "Britain")
        assert "Territory Flanders" not in lines and "France cedes Flanders" in lines
        spaced = {"type": "peace", "proposer_nation": "France", "target_nation": "Britain",
                  "sweeteners": [{"type": "territory_cede", "value": 1, "regions": ["Lower Saxony"]}],
                  "demands": [], "clauses": ["territory_lower_saxony"]}
        assert format_terms_for_display(spaced, "peace", "Britain") == [
            "Peace Treaty (end state of war)", "France cedes Lower Saxony"]

    def test_the_dialogue_wrapper_is_the_same_summary(self):
        from backend.display_names import format_terms_for_display
        from backend.game_logic.diplomatic_dialogue import _format_terms_for_display
        terms = {"type": "peace", "proposer_nation": "France", "target_nation": "Britain",
                 "sweeteners": [{"type": "territory_cede", "value": 1, "regions": ["Flanders"]}],
                 "demands": [], "clauses": ["territory_flanders"]}
        assert _format_terms_for_display(terms, "peace", "Britain") == format_terms_for_display(
            terms, "peace", "Britain")


# ══════════════════════════════════════════════════════════════════════════
# S14G-X47 - the front note reaches the typed march's reply and the per-turn step
# ══════════════════════════════════════════════════════════════════════════

def _r11_front_world(boot):
    """The S14G-7 stage: France allied to Bavaria; Austria, at war with Bavaria,
    under armistice with France; Soult at Lorraine, one province from Swabia."""
    from backend.game_logic import diplomacy as D
    w = _r11_copy(boot)
    assert w.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"
    assert w.get_diplomatic_state("Bavaria", "Austria") == "WAR"
    variant = D.armistice_variant_for(w, "France", "Austria")
    with _r11_quiet():
        event = w._ratify_treaty({"type": variant, "proposer_nation": "France",
                                  "target_nation": "Austria", "sweeteners": [],
                                  "demands": [], "clauses": []})
    assert event and event.get("type") != "diplomatic_treaty_failed", event
    assert w.get_diplomatic_state("France", "Austria") == "ARMISTICE"
    w.get_marshal("Soult").location = "Lorraine"
    with _r11_quiet():
        w.calculate_visibility()
    return w


class TestS14GX47:
    """S14G-7 built `front_line` / `front_note` and wired the plain `move`; the
    typed MARCH's reply and the standing march's per-turn step - the two roads
    that say "Moves to Swabia." - printed the camp and pay notes and not the
    front. Reproduced: "Soult, march to Swabia" after the accept answered "...
    Moves to Swabia." and nothing of the front."""

    def test_the_typed_marchs_reply_says_the_front(self, _r11_boot):
        w = _r11_front_world(_r11_boot)
        with _r11_client(w) as client:
            out = _r11_say(client, "Soult, march to Swabia")
        assert out.get("success") is True, out.get("message")
        assert w.get_marshal("Soult").location == "Swabia"
        assert _R11_FRONT in out["message"], out["message"]
        assert out["message"].count(_R11_FRONT) == 1

    def test_no_truce_no_front_note(self, _r11_boot):
        """The negative control: before the armistice Austria is at war with us
        and the same march prints nothing of a front."""
        w = _r11_copy(_r11_boot)
        w.get_marshal("Soult").location = "Lorraine"
        with _r11_client(w) as client:
            out = _r11_say(client, "Soult, march to Swabia")
        assert out.get("success") is True and "front" not in out["message"].replace("front of", "")
        assert "Bavaria's front" not in out["message"]

    def test_the_standing_marchs_step_says_the_front_it_stops_on(self, _r11_boot):
        from backend.commands.executor import CommandExecutor
        from backend.commands.strategic import StrategicOrderProcessor
        w = _r11_front_world(_r11_boot)
        soult = w.get_marshal("Soult")
        with _r11_client(w) as client:
            first = _r11_say(client, "Soult, march to Franconia")
        assert first.get("success") is True, first.get("message")
        assert soult.location == "Swabia" and soult.strategic_order.path == ["Franconia"]
        proc = StrategicOrderProcessor(CommandExecutor())
        w.current_turn += 1
        soult.strategic_order.issued_turn = w.current_turn - 1
        with _r11_quiet():
            report = proc._execute_strategic_turn(soult, w, {"world": w}) or {}
        assert soult.location == "Franconia", report
        assert ("Franconia is Bavaria's front — Austria, under truce with us, is at war with "
                "her; a corps there will not fight, and marches home if the ground changes "
                "hands.") in report["message"], report["message"]

    def test_the_quote_and_the_desk_carry_the_front(self, _r11_boot):
        from backend.ai.state_desk import _answer_march_cost
        from backend.commands.order_quotes import march_quote
        w = _r11_front_world(_r11_boot)
        soult = w.get_marshal("Soult")
        q = march_quote(w, soult, "Swabia")
        assert q["front"] == _R11_FRONT
        assert march_quote(w, soult, "Orleanais")["front"] == ""
        assert _R11_FRONT in _answer_march_cost(w, "Swabia", "Soult")


# ══════════════════════════════════════════════════════════════════════════
# S14G-X48 - the quote's riders reach every reader
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX48:
    """S14G-2 / S14G-3 added `terms` to the quote, S14G-7 `front`, S14G-11
    `guard`; the readers were the desk (`state_desk._quote_sentences`), the
    order card (`order_confirm_card.gd::_terms` and `show_group`) and the
    province panel (`region_panel.gd::_quote_notes`, and the army row's corps).
    Each rider must reach each reader - a quote field no surface prints is a
    consequence stated nowhere."""

    def test_the_desk_prints_every_rider(self):
        from backend.ai.state_desk import _quote_sentences
        me = SimpleNamespace(name="Soult")
        q = {"note": "", "camp": "", "departs": "", "detour": "", "pay": "",
             "guard": _R11_SENTENCE, "front": _R11_FRONT,
             "terms": "Soult goes to Davout now; the order lapses of itself.",
             "replaces": "", "objection": "none", "already": False}
        said = _quote_sentences(None, q, me)
        for sentence in (_R11_SENTENCE, _R11_FRONT, q["terms"]):
            assert sentence in said, said
        assert _quote_sentences(None, {"objection": "none"}, me) == ""

    def test_a_supports_terms_reach_the_desk_through_the_quote(self, _r11_boot):
        from backend.ai.state_desk import _quote_sentences
        from backend.commands.order_quotes import support_quote
        w = _r11_copy(_r11_boot)
        soult, davout = w.get_marshal("Soult"), w.get_marshal("Davout")
        q = support_quote(w, soult, davout)
        assert q["terms"] != ""
        assert q["terms"] in _quote_sentences(w, q, soult)

    def test_the_army_rows_carry_guard_and_front(self, _r11_w):
        """The Staff's one order quotes each corps' card: `guard`, `front` and
        `terms` ride its row (the panel prints them under the army row)."""
        from backend.commands.order_quotes import march_quote
        w = _r11_w
        mq = march_quote(w, w.get_marshal("Soult"), "Flanders")
        assert {"guard", "front", "terms"} <= set(mq)
        text = (_R11_ROOT / "backend" / "commands" / "order_quotes.py").read_text(encoding="utf-8")
        assert '"guard": mq["guard"], "front": mq["front"]' in text

    def test_the_blank_quote_defaults_the_new_fields(self):
        from backend.commands.order_quotes import _blank
        q = _blank("march", SimpleNamespace(name="Soult"), "Flanders", "Soult, march to Flanders")
        assert q["guard"] == "" and q["front"] == "" and q["terms"] == ""

    @staticmethod
    def _func(src: str, name: str) -> str:
        marker = f"func {name}("
        assert marker in src, name
        return src.split(marker, 1)[1].split("\nfunc ", 1)[0].split("\nstatic func ", 1)[0]

    def test_the_card_reads_them_in_its_terms_and_its_group_rows(self):
        src = (_R11_SCRIPTS / "order_confirm_card.gd").read_text(encoding="utf-8")
        terms = self._func(src, "_terms")
        group = self._func(src, "show_group")
        for key in ("guard", "front", "terms"):
            assert f'q.get("{key}", "")' in terms, key
            assert f'q.get("{key}", "")' in group, key
        # after the pay line, in the warning colour, and a line only when non-empty
        assert terms.index('q.get("pay", "")') < terms.index('q.get("guard", "")') \
            < terms.index('q.get("front", "")') < terms.index('q.get("terms", "")')
        assert 'lines.append("[color=#" + Utils.COLOR_WARNING + "]" + guard + "[/color]")' in terms
        assert 'lines.append("   [color=#" + Utils.COLOR_WARNING + "]" + terms_row + "[/color]")' in group
        for ln in (terms + group).splitlines():
            assert not ln.startswith("  "), repr(ln)               # GDScript uses TABS

    def test_the_panel_reads_them_in_its_notes_and_its_army_rows(self):
        src = (_R11_SCRIPTS / "region_panel.gd").read_text(encoding="utf-8")
        notes = self._func(src, "_quote_notes")
        assert notes.index('q.get("pay", "")') < notes.index('q.get("guard", "")') \
            < notes.index('q.get("front", "")') < notes.index('q.get("terms", "")') \
            < notes.index('q.get("replaces", "")')
        for key in ("guard", "front", "terms"):
            assert f'q.get("{key}", "")' in notes, key
        assert "notes.append(guard)" in notes and "notes.append(front)" in notes \
            and "notes.append(terms_text)" in notes
        rows = self._func(src, "_army_rider_rows")
        assert 'for rider in ["guard", "front", "terms"]:' in rows
        assert 'army.get("corps", [])' in rows
        assert ("out += _army_detour_rows(army)" in src
                and src.index("out += _army_detour_rows(army)") < src.index("out += _army_rider_rows(army)"))
        for ln in rows.splitlines():
            assert not ln.startswith("  "), repr(ln)


# ══════════════════════════════════════════════════════════════════════════
# row12
# ══════════════════════════════════════════════════════════════════════════
# S14G-12 (Pre-Deploy S14h part 1, October 26, 2026) — the table's gold ceiling
# is stated on a line the header never showed, and the standing hint "use More
# generous until each accepts" was false there.
#
# THE CAUSE AS TRACED. The scorer credits France's gold to a court at one point a
# 25 gold, capped at 40 points = 1,000 gold (`settlement_scoring.py`
# CONCESSION_GOLD_CAP x CONCESSION_GOLD_DIVISOR; the pair's lines are summed before
# the cap, PC-F62); the dial stops there (DDB-33) and its note IS authored ("Gold
# past 1,000 buys nothing more from Britain at this table, Sire.", a `dial_note`
# voice beat). But (1) the popup drew the beats as the LAST lines of the header, a
# `scroll_active`, `fit_content = false` RichTextLabel that shows about nine lines
# at 5120x1440, so the player never saw it (sea #8, frames 0266 / 0272 / 0278); (2)
# the standing hint pivoted only for a treasury bound (PF-1) and a legitimacy
# mismatch (S14E-6), so it read "Use 'More generous' ... until each accepts" where
# gold bought nothing; (3) the per-line [+] (`settlement_demand_set_magnitude`) had
# no ceiling and would have spent 1,100 gold that bought nothing.
#
# THE SIGHTING. Sea #8 (P2, turn 16, action 275): the Britain-alone table with
# "Erect Ireland" demanded (term harshness -23, legitimacy -20, 17 of 50), "More
# generous" stopped at 1,000g and 26 of 50 with 5,241g spare, and "Ease Britain" and
# "More generous" then did nothing the player could see. The old reading, on the
# same staged board: the hint said "Use 'More generous' (or ease a court) until
# each accepts"; the magnitude verb set 1,500 gold; the line carried no bound.
#
# WHAT THE FIX DOES. (1) Godot: the beats stand directly under the verdict, ABOVE
# the treasury / narration / advisory block; a header taller than its pane says so
# with a "more below" chip, and a header too short to show the beats is scrolled to
# them. (2) The hint's THIRD arm: a holdout whose gold has reached the ceiling is
# told where it stands, what weighs on it and the ways out (the clause's Remove,
# land at the scorer's own province weight, the court's Drop where the row offers
# it); the legitimacy mismatch wins where both apply, PF-1's treasury arm first.
# (3) `settlement_demand_set_magnitude` clamps a line that PAYS a court to what the
# credit still counts and answers in the authored note ("... — set to 1,000.");
# `amount_max` rides the line's `magnitude` so the row control shows the bound.
#
# WHAT WAS KEPT. The dial's own ceiling arm and its note, byte for byte (the
# sentence is now built once by `credit_ceiling_note`); a court-dictated clause kept
# or lowered is never clamped (PC-R3); PF-1's and S14E-6's hint arms; the verdict
# leading the preamble (G4F-7). Player-only text and a verb the AI never walks: no
# series seam. The sibling classes are `TestS14GX52` (the truce row's priority,
# Godot half of S14G-7) and `TestS14GX53` (the menu body outside the quotation).

_R12_REPO = Path(__file__).resolve().parents[1]
_R12_SCENARIO = (_R12_REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")
_R12_SCRIPTS = _R12_REPO / "godot-client" / "project-sovereign" / "scripts"
_R12_NOTE = "Gold past 1,000 buys nothing more from Britain at this table, Sire."


def _r12_quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _r12_gd(name: str) -> str:
    return (_R12_SCRIPTS / name).read_text(encoding="utf-8")


def _r12_function(src: str, name: str) -> str:
    """One GDScript function's text, from its `func` line to the next `func`."""
    return src.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]


@pytest.fixture(scope="module")
def _r12_boot():
    from backend.models.world_state import WorldState
    with _r12_quiet():
        return WorldState.from_scenario(str(_R12_SCENARIO))


@pytest.fixture
def _r12_board(_r12_boot):
    """The shipped 1805 board as the sea sighting held it: France rich (6,000g)
    and holding Ulster and Munster, so "Erect Ireland" is an eligible carve."""
    from backend.models.world_state import WorldState
    w = WorldState.from_dict(json.loads(json.dumps(_r12_boot.to_dict(), default=str)))
    w.nation_gold["France"] = 6000
    for region in ("Ulster", "Munster"):
        w.regions[region].controller = "France"
    w.invalidate_active_nations_cache()
    return w


def _r12_gold(amount=1000, kind="gold_indemnity", **extra):
    return dict({"type": kind, "from": "France", "to": "Britain", "amount": amount,
                 "authored_by": "player"}, **extra)


_R12_IRELAND = {"type": "create_client", "from": "Britain", "to": "France", "tag": "Ireland",
                "client_display_name": "Ireland", "provinces": ["Ulster", "Munster"],
                "authored_by": "player"}


def _r12_stage(w, terms, covered=("Britain",)):
    from backend.game_logic import settlement_staging as SS
    with _r12_quiet():
        preview = SS.build_settlement_preview(
            w, war_id="war_1", settlement_terms=list(terms),
            covered_enemy_participants=list(covered), actor_nation="France",
            ignore_active_dialogue=True)
        assert preview.get("success"), preview
        dialogue = SS.build_settlement_confirm_dialogue(
            w, preview, caller_kind=SS.SETTLEMENT_EDITOR_CALLER_KIND, dialogue_mode="PROPOSE")
    w.dialogue_manager.push(dialogue)
    return dialogue


def _r12_act(w, action, params, dialogue=None):
    from backend.game_logic.settlement_actions import handle_settlement_dialogue_action
    with _r12_quiet():
        return handle_settlement_dialogue_action(
            w, action=action, dialogue=dialogue or w.dialogue_manager.peek(), action_params=params)


def _r12_row(dialogue, court="Britain"):
    return next(r for r in dialogue["per_court_acceptance"] if r["nation"] == court)


def _r12_synthetic(nation, total=26, component="term_harshness_penalty", value=-23,
                   display="Term harshness", detail="", line=""):
    row = {"nation": nation, "total": total, "threshold": 50, "band": "reject",
           "top_blocker_component": component, "top_blocker_value": value,
           "top_blocker_display": display, "top_blocker_detail": detail}
    if line:
        row["top_blocker_line"] = line
    return row


class TestS14G12:
    """The decided fix on the shipped board: the hint, the verb, the bound, the note."""

    def test_a_the_sighting_the_hint_names_the_ceiling_the_points_and_the_blocker(self, _r12_board):
        """OLD READING: "Britain won't accept these terms yet. Use 'More generous' (or
        ease a court) until each accepts ..." — false: the dial stops at the credit
        ceiling and gold past it buys nothing."""
        from backend.game_logic.settlement_scoring import gold_land_rates
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(1000), _R12_IRELAND])
        row = _r12_row(dialogue)
        hint = dialogue["propose_carry_hint"]
        land = int(gold_land_rates()["credit"])
        assert land == 875
        # the sighting's top blocker: the demand the player laid on Britain
        assert row["top_blocker_component"] == "term_harshness_penalty"
        assert int(row["top_blocker_value"]) == -23
        assert hint.startswith(
            f"Gold is at its ceiling for Britain ({int(row['total'])} of {int(row['threshold'])}); "
            "what weighs on her is the erection of Ireland (-23) — remove it or offer land "
            f"(a province weighs about {land:,}g).")
        assert "Use 'More generous'" not in hint
        # the way on from the hint is still the review (the tail the other arms carry)
        assert "Then 'Submit for Review' to ratify." in hint

    def test_b_a_multi_court_table_offers_the_drop_and_keeps_the_generic_sentence_for_the_rest(self, _r12_board):
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(1000), _R12_IRELAND],
                              covered=("Britain", "Austria"))
        hint = dialogue["propose_carry_hint"]
        assert "Gold is at its ceiling for Britain (" in hint
        assert hint.endswith("— remove it, offer land (a province weighs about 875g), or drop Britain.")
        # a court the ceiling does not touch keeps the generic road
        assert hint.startswith("Austria won't accept these terms yet. Use 'More generous'")

    def test_c_below_the_ceiling_the_old_hint_stands(self, _r12_board):
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(500), _R12_IRELAND])
        hint = dialogue["propose_carry_hint"]
        assert hint.startswith("Britain won't accept these terms yet. Use 'More generous'")
        assert "ceiling" not in hint

    def test_d_the_arm_is_the_one_helper_the_pivot_reads(self, _r12_board, monkeypatch):
        """Holding the ceiling reading down restores the old hint exactly."""
        from backend.game_logic import settlement_staging as SS
        monkeypatch.setattr(SS, "court_gold_at_credit_ceiling", lambda terms, court: False)
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(1000), _R12_IRELAND])
        assert dialogue["propose_carry_hint"] == (
            "Britain won't accept these terms yet. Use 'More generous' (or ease a court) until "
            "each accepts, then 'Submit for Review' to ratify. "
            "Submitting now only opens a review you cannot ratify.")

    def test_e_the_ceiling_is_read_from_the_scorers_constants(self, monkeypatch):
        from backend.game_logic import settlement_staging as SS
        assert SS.credit_gold_ceiling() == 1000
        monkeypatch.setattr(SS, "CONCESSION_GOLD_CAP", 20)
        assert SS.credit_gold_ceiling() == 500
        assert SS.credit_ceiling_note("Austria") == (
            "Gold past 500 buys nothing more from Austria at this table, Sire.")
        assert SS.court_gold_at_credit_ceiling([_r12_gold(500)], "Britain") is True
        assert SS.court_gold_at_credit_ceiling([_r12_gold(499)], "Britain") is False

    def test_f_a_split_payment_reaches_the_ceiling_as_the_scorer_sums_it(self):
        """PC-F62: a pair's lines are summed before the cap — three lines of 400 are the
        ceiling, and a stream counts its whole projected obligation."""
        from backend.game_logic import settlement_staging as SS
        three = [_r12_gold(400), _r12_gold(400), _r12_gold(400)]
        assert SS.court_gold_at_credit_ceiling(three, "Britain") is True
        assert SS.court_gold_at_credit_ceiling(three[:2], "Britain") is False
        stream = [_r12_gold(100, kind="gold_per_turn", turns=10)]
        assert SS.court_gold_at_credit_ceiling(stream, "Britain") is True
        # a demand ON the court has no ceiling
        demand = {"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 5000}
        assert SS.court_gold_at_credit_ceiling([demand], "Britain") is False

    def test_g_set_magnitude_past_the_ceiling_clamps_and_says_so(self, _r12_board):
        """OLD READING: the verb set 1,500 gold ("Set 1500 gold from France.") — gold
        that bought nothing."""
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(900), _R12_IRELAND])
        result = _r12_act(_r12_board, "settlement_demand_set_magnitude", {
            "clause_index": 1, "expected_type": "gold_indemnity", "amount": 1500}, dialogue)
        assert result["success"] is True, result.get("error_display")
        assert result["message"] == (
            "Gold past 1,000 buys nothing more from Britain at this table, Sire — set to 1,000.")
        terms = result["diplomatic_dialogue"]["settlement_terms"]
        assert next(t for t in terms if t["type"] == "gold_indemnity")["amount"] == 1000
        beats = result["diplomatic_dialogue"]["authoring_voice_beats"]
        assert [(b["kind"], b["line"]) for b in beats] == [(
            "dial_note",
            "Gold past 1,000 buys nothing more from Britain at this table, Sire — set to 1,000.")]
        # and the hint the restaged table carries is the third arm's
        assert result["diplomatic_dialogue"]["propose_carry_hint"].startswith(
            "Gold is at its ceiling for Britain (")

    def test_h_set_magnitude_at_or_under_the_ceiling_is_untouched(self, _r12_board):
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(500), _R12_IRELAND])
        result = _r12_act(_r12_board, "settlement_demand_set_magnitude", {
            "clause_index": 1, "expected_type": "gold_indemnity", "amount": 1000}, dialogue)
        assert result["success"] is True, result.get("error_display")
        assert result["message"] == "Set 1000 gold from France."
        assert not result["diplomatic_dialogue"].get("authoring_voice_beats")

    def test_i_the_next_restage_drops_the_beat(self, _r12_board):
        """GT-Slice-V: the beats are one-shot."""
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(900), _R12_IRELAND])
        clamped = _r12_act(_r12_board, "settlement_demand_set_magnitude", {
            "clause_index": 1, "expected_type": "gold_indemnity", "amount": 1500}, dialogue)
        assert clamped["diplomatic_dialogue"]["authoring_voice_beats"]
        again = _r12_act(_r12_board, "settlement_demand_set_magnitude", {
            "clause_index": 1, "expected_type": "gold_indemnity", "amount": 900})
        assert not again["diplomatic_dialogue"].get("authoring_voice_beats")

    def test_j_amount_max_rides_the_line_that_pays_the_court(self, _r12_board):
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(900), _R12_IRELAND])
        lines = _r12_row(dialogue)["current_demands"]
        paying = next(l for l in lines if l["clause_type"] == "gold_indemnity")
        assert paying["magnitude"]["amount_max"] == 1000
        assert isinstance(paying["magnitude"]["amount_max"], int)
        assert paying["magnitude"]["amount_min"] == 1
        # a demand on the court carries none
        demand = {"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 300,
                  "authored_by": "player"}
        lines = _r12_row(_r12_stage(_r12_board, [{"type": "peace"}, demand]))["current_demands"]
        assert "amount_max" not in next(l for l in lines if l["clause_type"] == "gold_indemnity")["magnitude"]

    def test_k_a_stream_carries_its_bound_per_turn_and_clamps_its_term(self, _r12_board):
        stream = _r12_gold(100, kind="gold_per_turn", turns=5)
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, stream])
        magnitude = next(l for l in _r12_row(dialogue)["current_demands"]
                         if l["clause_type"] == "gold_per_turn")["magnitude"]
        assert magnitude["amount_max"] == 200 and magnitude["turns"] == 5
        # the term past what the credit counts is clamped, in the same sentence
        result = _r12_act(_r12_board, "settlement_demand_set_magnitude", {
            "clause_index": 1, "expected_type": "gold_per_turn", "turns": 20}, dialogue)
        assert result["success"] is True, result.get("error_display")
        assert result["message"] == (
            "Gold past 1,000 buys nothing more from Britain at this table, Sire — set to 10 turns.")
        kept = next(t for t in result["diplomatic_dialogue"]["settlement_terms"]
                    if t["type"] == "gold_per_turn")
        assert (kept["amount"], kept["turns"]) == (100, 10)
        # and an amount past it, per turn
        again = _r12_act(_r12_board, "settlement_demand_set_magnitude", {
            "clause_index": 1, "expected_type": "gold_per_turn", "amount": 300})
        kept = next(t for t in again["diplomatic_dialogue"]["settlement_terms"]
                    if t["type"] == "gold_per_turn")
        assert (kept["amount"], kept["turns"]) == (100, 10)

    def test_l_a_split_line_is_bounded_by_what_its_sibling_already_carries(self, _r12_board):
        """The scorer sums a pair's lines before the cap, so the bound of one line is
        the ceiling less the others."""
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(600), _r12_gold(600)])
        lines = [l for l in _r12_row(dialogue)["current_demands"] if l["clause_type"] == "gold_indemnity"]
        assert [l["magnitude"]["amount_max"] for l in lines] == [400, 400]
        result = _r12_act(_r12_board, "settlement_demand_set_magnitude", {
            "clause_index": 2, "expected_type": "gold_indemnity", "amount": 900}, dialogue)
        assert result["message"] == (
            "Gold past 1,000 buys nothing more from Britain at this table, Sire — set to 400.")

    def test_m_a_court_dictated_clause_kept_or_lowered_is_not_clamped(self, _r12_board):
        """PC-R3: the ask is the court's, priced to the war; only raising it is the player's."""
        from backend.game_logic.settlement_actions import (
            _clamp_to_credit_ceiling, _court_dictated_and_not_raised)
        before = _r12_gold(1200, authored_by="Britain")
        kept = dict(before)
        assert _court_dictated_and_not_raised(_r12_board, before, kept, "gold_indemnity") is True
        raised = dict(before, amount=1300)
        assert _court_dictated_and_not_raised(_r12_board, before, raised, "gold_indemnity") is False
        # the player's own line is never exempt
        mine = _r12_gold(1200)
        assert _court_dictated_and_not_raised(_r12_board, mine, dict(mine), "gold_indemnity") is False
        # and the clamp itself leaves a payment of the court's own side alone
        clause = {"type": "gold_indemnity", "from": "Britain", "to": "France", "amount": 5000}
        assert _clamp_to_credit_ceiling([clause], 0, clause, ["Britain"],
                                        amount_given=True, turns_given=False) == ""
        assert clause["amount"] == 5000

    def test_n_the_dial_says_the_note_at_the_ceiling_for_ease_and_for_more_generous(self, _r12_board):
        """Item 4's pins: `Ease Britain` (the focused dial) and the table's `More
        generous` at the ceiling both say the authored note, as a beat the header
        carries — the note was authored and shipped all along."""
        for scope in ("Britain", "table"):
            dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(1000), _R12_IRELAND])
            result = _r12_act(_r12_board, "settlement_dial_generous", {"scope": scope}, dialogue)
            assert result["success"] is True, result.get("error_display")
            beats = result["diplomatic_dialogue"]["authoring_voice_beats"]
            assert [(b["kind"], b["line"]) for b in beats] == [("dial_note", _R12_NOTE)], scope
            assert _R12_NOTE in result["message"], scope

    def test_o_the_standing_hint_names_what_it_names_for_a_blocker_that_is_not_a_clause(self):
        from backend.game_logic import settlement_staging as SS
        row = _r12_synthetic("Britain", total=24, component="agenda_settlement_mod",
                             value=-8, display="National design")
        hint = SS._settlement_propose_carry_hint(
            ["Britain"], [row], settlement_terms=[_r12_gold(1000)])
        assert hint.startswith(
            "Gold is at its ceiling for Britain (24 of 50); what weighs on her is national design "
            "(-8) — offer land (a province weighs about 875g).")
        assert "remove it" not in hint

    def test_p_a_legitimacy_mismatch_wins_where_both_apply(self):
        """S14E-6's arm names the clause and its cures; the ceiling arm stands aside."""
        from backend.game_logic import settlement_staging as SS
        line = ("The demand for Beira on Portugal reads as a claim of victory the field has not "
                "delivered — remove it, or drop Austria.")
        portugal = _r12_synthetic("Portugal", component="settlement_tier_legitimacy", value=-20,
                                  display="Settlement legitimacy", detail="tier_mismatch", line=line)
        terms = [dict(_r12_gold(1000), to="Portugal")]
        hint = SS._settlement_propose_carry_hint(["Portugal"], [portugal], settlement_terms=terms)
        assert "ceiling" not in hint and line in hint
        # a mixed table: the mismatch court speaks its line, the ceiling court its own
        britain = _r12_synthetic("Britain")
        both = SS._settlement_propose_carry_hint(
            ["Portugal", "Britain"], [portugal, britain],
            settlement_terms=terms + [_r12_gold(1000)])
        assert line in both and "Gold is at its ceiling for Britain (26 of 50)" in both
        assert "Gold is at its ceiling for Portugal" not in both

    def test_q_the_treasury_bound_still_leads(self):
        from backend.game_logic import settlement_staging as SS
        hint = SS._settlement_propose_carry_hint(
            ["Britain"], [_r12_synthetic("Britain")],
            budget_bound_constraint={"budget_bound": True}, settlement_terms=[_r12_gold(1000)])
        assert hint.startswith("Britain won't accept, and the treasury cannot raise the gold offer further.")

    def test_r_the_hint_without_terms_is_the_old_hint(self):
        """The two arms an earlier row pinned call the hint with no terms."""
        from backend.game_logic import settlement_staging as SS
        hint = SS._settlement_propose_carry_hint(["Britain"], [_r12_synthetic("Britain")])
        assert hint.startswith("Britain won't accept these terms yet. Use 'More generous'")


class TestS14G12Header:
    """The Godot half, pinned by reading the .gd (Godot is not run here)."""

    def test_a_the_beats_stand_under_the_verdict_and_above_the_treasury(self):
        src = _r12_gd("proposal_confirm_popup.gd")
        preamble = _r12_function(src, "_build_settlement_table_preamble")
        verdict = preamble.index("carry_verdict_display")
        beats = preamble.index("_settlement_voice_beats_bbcode(data)")
        treasury = preamble.index('data.get("treasury_line"')
        narration = preamble.index('data.get("multi_court_table_narration")')
        advisory = preamble.index('data.get("targeted_posture_advisory")')
        assert verdict < beats < treasury < narration < advisory
        # the old trailing block is gone — the beats are drawn once, at the top
        assert "authoring_voice_beats" not in preamble

    def test_b_each_beat_is_its_own_line_and_the_dial_note_is_drawn_like_the_caution(self):
        src = _r12_gd("proposal_confirm_popup.gd")
        helper = _r12_function(src, "_settlement_voice_beats_bbcode")
        assert 'data.get("authoring_voice_beats", [])' in helper
        assert '["talleyrand_caution", "dial_note"]' in helper
        assert helper.count('\\n"') >= 2   # a newline closes every beat's line

    def test_c_a_header_taller_than_its_pane_says_so(self):
        src = _r12_gd("proposal_confirm_popup.gd")
        assert "▼ more below" in src
        ready = _r12_function(src, "_ready")
        assert "_install_header_cue()" in ready
        cue = _r12_function(src, "_install_header_cue")
        assert "content_label.get_v_scroll_bar()" in cue and "content_label.add_child(cue)" in cue
        update = _r12_function(src, "_update_header_cue")
        assert "bar.max_value - bar.page" in update
        shown = _r12_function(src, "show_dialogue")
        assert 'call_deferred("_update_header_cue")' in shown and "_reveal_header_beats()" in shown

    def test_d_a_header_too_short_for_the_beats_is_scrolled_to_them(self):
        src = _r12_gd("proposal_confirm_popup.gd")
        reveal = _r12_function(src, "_reveal_header_beats")
        assert "scroll_to_paragraph(paragraph)" in reveal and "get_paragraph_offset" in reveal
        shown = _r12_function(src, "show_dialogue")
        # the paragraph the beats stand at: the head's newlines + the preamble's
        assert 'content_bbcode.count("\\n")' in shown
        assert "_header_beat_paragraph = head_paragraphs + _preamble_beat_paragraph" in shown
        assert "_header_beat_paragraph = -1" in shown

    def test_e_the_row_control_renders_the_bound(self):
        src = _r12_gd("proposal_confirm_popup.gd")
        lines = _r12_function(src, "_build_court_authoring_lines")
        assert 'magnitude.has("amount_max")' in lines and "up to %s%s" in lines
        # the [+] still fires the verb: the server's note is the answer past the bound
        assert "amount:+" in lines

    def test_f_the_scene_is_untouched(self):
        """The header's pane stays what it was (shared by every dialogue type); the
        cue and the scroll change no layout."""
        scene = (_R12_REPO / "godot-client" / "project-sovereign" / "scenes"
                 / "proposal_confirm_popup.tscn").read_text(encoding="utf-8")
        node = scene.split('[node name="ContentLabel"', 1)[1].split("[node ", 1)[0]
        assert "custom_minimum_size = Vector2(0, 72)" in node
        assert "scroll_active = true" in node and "fit_content = false" in node

    def test_g_the_other_scrolling_headers_are_listed_and_left(self):
        """The sweep: every RichTextLabel the popups make `scroll_active` with
        `fit_content = false` (nine other scenes + this scene's footer). Only
        this popup's header buried an authored line; the rest are bodies that
        scroll by design and carry no one-shot beat."""
        scenes = _R12_REPO / "godot-client" / "project-sovereign" / "scenes"
        found = sorted(
            p.name for p in scenes.glob("*.tscn")
            if "fit_content = false" in p.read_text(encoding="utf-8"))
        assert "proposal_confirm_popup.tscn" in found
        for name in ("incoming_proposal_popup.tscn", "war_detail_popup.tscn",
                     "talleyrand_objection_popup.tscn"):
            assert name in found


class TestS14GX52:
    """S14G-X52 — the truce row's confirm ordering, the Godot half of S14G-7.

    Cause: the backend sorts the `war_runs_on` conflict first and its `display`
    carries the consequence sentence, but both popups sorted conflict rows by
    priority and gave EVERY `WARNING` priority 1, so the dialogue's own warnings
    (priority 1 beside it, an unstable `sort_custom`) could print before the
    row the whole confirm turns on. Fix: a `war_runs_on` conflict sorts at
    priority 0 beside `HARD_STOP`, in the confirm popup and the incoming-letter
    popup alike (the `WARNING -> 1` line stays; the row's own check follows it,
    since the row's severity IS `WARNING`)."""

    @pytest.mark.parametrize("name,var", [
        ("proposal_confirm_popup.gd", "priority"),
        ("incoming_proposal_popup.gd", "conflict_priority"),
    ])
    def test_the_truce_row_sorts_beside_hard_stop(self, name, var):
        src = _r12_gd(name)
        warning_line = f"\t\t\t\t{var} = 1"
        assert warning_line in src
        guard = 'if conflict is Dictionary and str(conflict.get("conflict_type", "")) == "war_runs_on":'
        assert guard in src
        at = src.index(guard)
        assert f"{var} = 0" in src[at:at + len(guard) + 40]
        # the override FOLLOWS the severity line it must beat
        assert src.rindex(warning_line, 0, at) < at

    def test_the_backend_row_is_a_warning_the_override_must_beat(self):
        """The reason the order matters: the row's severity is WARNING."""
        src = (_R12_REPO / "backend" / "game_logic" / "diplomacy.py").read_text(encoding="utf-8")
        row = src.split('"conflict_type": "war_runs_on",', 1)[1].split("})", 1)[0]
        assert '"severity": "WARNING"' in row


class TestS14GX53:
    """S14G-X53 — S14G-8's menu body renders OUTSIDE Talleyrand's quotation marks.

    Cause: `diplomatic_dialogue._with_menu_body` appends "\\n\\nThe paths before
    us, Sire:\\n• …" to the menu's `talleyrand_text`, and `_build_content` wrapped
    the whole field in the italic quoted paragraph, so the option list stood
    inside the quotation marks. Fix: a small helper splits at the marker — the
    prose stays quoted and italic, the list renders after it as plain lines (its
    lead-in bold, one line per option, the bullet kept)."""

    def test_the_marker_is_the_backends_marker(self):
        src = _r12_gd("proposal_confirm_popup.gd")
        marker = re.search(r'const MENU_BODY_MARKER := "(.*)"', src).group(1)
        assert marker == "\\n\\nThe paths before us, Sire:"
        from backend.game_logic.diplomatic_dialogue import _with_menu_body
        body = _with_menu_body(
            None, "Sire, the court is cold.",
            [{"label": "Propose peace", "description": "Open a draft", "action": "dismiss"},
             {"label": "Stall", "description": "Wait a turn", "action": "dismiss"}],
            "Austria")
        assert marker.encode().decode("unicode_escape") in body
        prose, _, tail = body.partition(marker.encode().decode("unicode_escape"))
        assert prose == "Sire, the court is cold."
        assert tail.startswith("\n• Propose peace — Open a draft.")

    def test_build_content_routes_the_voice_through_the_splitter(self):
        src = _r12_gd("proposal_confirm_popup.gd")
        content = _r12_function(src, "_build_content")
        assert "_talleyrand_paragraph_bbcode(str(ttext))" in content
        # the quotation is no longer written around the whole field here
        assert '[i]\\"%s\\"[/i]' not in content.split("# Talleyrand commentary", 1)[1]

    def test_the_prose_stays_quoted_and_the_list_is_plain(self):
        src = _r12_gd("proposal_confirm_popup.gd")
        helper = _r12_function(src, "_talleyrand_paragraph_bbcode")
        assert "ttext.find(MENU_BODY_MARKER)" in helper
        # the prose: italic, quoted
        assert '[color=#c0b080][i]\\"%s\\"[/i][/color]' in helper
        # the list: its own lines after the quotation, the lead-in bold, no italics, no quotes
        after = helper.split("if at >= 0:", 1)[1]
        assert "[/i]" not in after and '\\"' not in after
        assert '[b]%s[/b]' in after and 'split("\\n")' in after
        assert 'ttext.substr(at + 2)' in after   # past the blank line, into the lead-in


class TestS14GX54:
    """S14G-X54 — the targeted-posture advice no longer counsels the dead lever.

    Cause: `_settlement_targeted_posture_advisory` (settlement_staging.py) lists
    every below-threshold, dialable holdout as an "ease" candidate, so the sea #8
    frames read "I'd ease Britain, Sire — the table is yours to shape." over a
    table whose gold was at the credit ceiling and bought nothing more — the same
    false counsel as the standing hint, one line above it. Fix: a holdout whose
    gold has reached the ceiling (`court_gold_at_credit_ceiling`, the one test the
    hint reads) is not offered as an "ease" candidate; the carry hint says what
    weighs on it instead."""

    def test_the_advisory_does_not_counsel_easing_a_court_whose_gold_is_spent(self, _r12_board):
        spent = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(1000), _R12_IRELAND])
        assert spent["targeted_posture_advisory"] == ""
        # below the ceiling the counsel stands, as it always did
        open_ = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(500), _R12_IRELAND])
        assert open_["targeted_posture_advisory"] == (
            "I'd ease Britain, Sire — the table is yours to shape.")

    def test_a_court_the_ceiling_does_not_touch_is_still_counselled(self):
        from backend.game_logic import settlement_staging as SS
        rows = [_r12_synthetic("Britain"), _r12_synthetic("Austria")]
        terms = [_r12_gold(1000)]
        assert SS._settlement_targeted_posture_advisory(
            rows, ["Britain", "Austria"], settlement_terms=terms) == (
            "I'd ease Austria, Sire — the table is yours to shape.")
        # with no terms in hand (the old call) the counsel is the old counsel
        assert SS._settlement_targeted_posture_advisory(rows, ["Britain", "Austria"]) == (
            "I'd ease Austria, Britain, Sire — the table is yours to shape.")


def _r12_add(w, court="Britain", clause_type="gold_indemnity", group="offer", dialogue=None, **params):
    return _r12_act(w, "settlement_demand_add", dict(
        nation=court, clause_type=clause_type, group=group, **params), dialogue)


class TestS14GX55:
    """S14G-X55 — the add verb and the Offer rows no longer author a line that buys nothing.

    Cause: the `settlement_demand_add` gold branch took any amount, and
    `_guided_gold_offer_default` (settlement_baseline.py — read by the add verb's
    default and by the court row's Offer suggestion) reads the TREASURY only, so an
    Offer line was authored beside lines that already filled the pair's credit
    ceiling (the scorer sums a pair's lines before the cap — PC-F62). The sibling
    of S14G-12's per-line [+]. Fix: the add verb clamps an offer through
    `_clamp_to_credit_ceiling` (reply and `dial_note` beat in the authored note,
    "— set to N."), refuses FREE with that note where the ceiling is already full
    (`credit_ceiling_full`, nothing authored), and the row's Offer suggestions read
    the pair's other lines (`credit_headroom`) at the call site — the default
    function itself, in another module, is not touched. A demand ON a court has no
    ceiling and is never clamped."""

    def test_an_offer_past_the_ceiling_is_clamped_and_says_so(self, _r12_board):
        """OLD READING: the line was added whole ("Offered 1500 gold from France.")."""
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(600)])
        result = _r12_add(_r12_board, amount=900, dialogue=dialogue)
        assert result["success"] is True, result.get("error_display")
        gold = [t for t in result["diplomatic_dialogue"]["settlement_terms"]
                if t["type"] == "gold_indemnity"]
        assert sorted(int(t["amount"]) for t in gold) == [400, 600]
        note = "Gold past 1,000 buys nothing more from Britain at this table, Sire — set to 400."
        assert result["message"] == f"Offered 400 gold from France. {note}"
        beats = result["diplomatic_dialogue"]["authoring_voice_beats"]
        assert (beats[0]["kind"], beats[0]["line"]) == ("dial_note", note)
        # the court's own reaction still follows the note
        assert any(b["kind"] == "court_reaction" for b in beats[1:])

    def test_an_offer_under_the_ceiling_is_untouched(self, _r12_board):
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(600)])
        result = _r12_add(_r12_board, amount=300, dialogue=dialogue)
        assert result["success"] is True, result.get("error_display")
        assert result["message"] == "Offered 300 gold from France."
        assert [b["kind"] for b in result["diplomatic_dialogue"]["authoring_voice_beats"]] == [
            "court_reaction"]

    def test_a_full_ceiling_refuses_free_and_authors_nothing(self, _r12_board):
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(1000)])
        terms_before = [dict(t) for t in dialogue["settlement_terms"]]
        gold = _r12_board.nation_gold["France"]
        result = _r12_add(_r12_board, amount=100, dialogue=dialogue)
        assert result["success"] is False
        assert result["error"] == "credit_ceiling_full"
        assert result["error_display"] == _R12_NOTE
        assert result["mutated"] is False
        assert _r12_board.nation_gold["France"] == gold
        # the staged draft is exactly what it was
        mounted = _r12_board.dialogue_manager.peek()
        assert [dict(t) for t in mounted["settlement_terms"]] == terms_before
        # and the default (no amount named) is refused the same way
        again = _r12_add(_r12_board, dialogue=mounted)
        assert again["success"] is False and again["error_display"] == _R12_NOTE

    def test_a_stream_is_clamped_per_turn_and_refused_where_the_room_is_under_its_floor(self, _r12_board):
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(800)])
        result = _r12_add(_r12_board, clause_type="gold_per_turn", amount=300, turns=5,
                          dialogue=dialogue)
        assert result["success"] is True, result.get("error_display")
        kept = next(t for t in result["diplomatic_dialogue"]["settlement_terms"]
                    if t["type"] == "gold_per_turn")
        assert (kept["amount"], kept["turns"]) == (40, 5)        # 200 of room, over 5 turns
        assert result["message"].endswith(
            "Gold past 1,000 buys nothing more from Britain at this table, Sire — set to 40.")
        # 20 gold of room across 3 turns is under the stream's 10-a-turn floor
        tight = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(980)])
        refused = _r12_add(_r12_board, clause_type="gold_per_turn", amount=50, turns=3,
                           dialogue=tight)
        assert refused["success"] is False and refused["error"] == "credit_ceiling_full"

    def test_a_demand_on_the_court_has_no_ceiling(self, _r12_board):
        dialogue = _r12_stage(_r12_board, [{"type": "peace"}, _r12_gold(1000)])
        result = _r12_add(_r12_board, group="demand", amount=1200, dialogue=dialogue)
        if result["success"]:          # the court's purse may refuse it; the ceiling never does
            assert "buys nothing more" not in result["message"]
        else:
            assert result["error"] != "credit_ceiling_full"

    def test_the_offer_rows_read_the_pairs_other_lines(self, _r12_board):
        """The row's Offer N gold suggestion is capped at what the credit still
        counts and is not offered where the ceiling is full; its `amount_max` is the
        room, not the whole ceiling."""
        def offers(terms):
            row = _r12_row(_r12_stage(_r12_board, terms))
            return [s for s in row["demand_suggestions"]
                    if s["group"] == "offer" and s["clause_type"] == "gold_indemnity"]
        # nothing staged: the row is the old row, bounded by the whole ceiling
        fresh = offers([{"type": "peace"}])
        assert fresh and fresh[0]["magnitude"]["amount_max"] == 1000
        # 950 staged: the row offers no more than the 50 that still counts
        near = offers([{"type": "peace"}, _r12_gold(950)])
        assert near and int(near[0]["magnitude"]["amount"]) == 50
        assert near[0]["magnitude"]["amount_max"] == 50
        assert near[0]["label"] == "Offer 50 gold to Britain"
        # the ceiling full: no Offer-gold row at all
        assert offers([{"type": "peace"}, _r12_gold(1000)]) == []

    def test_the_room_the_refusal_reads_is_the_room_the_clamp_reads(self):
        """One pair reading: the free refusal's headroom and the clamp's bound are the
        same ceiling less the same other lines (player-only, no series seam)."""
        from backend.game_logic import settlement_staging as SS
        terms = [{"type": "peace"}, _r12_gold(600), _r12_gold(250, kind="gold_lump")]
        room = SS.credit_headroom(terms, "France", "Britain")
        assert room == 150
        assert SS.credit_line_amount_max(terms + [_r12_gold(900)], 3, "Britain") == room
        # another payer's or another court's lines do not count against the pair
        assert SS.credit_headroom(terms, "Spain", "Britain") == 1000
        assert SS.credit_headroom(terms, "France", "Austria") == 1000


# ══════════════════════════════════════════════════════════════════════════
# row13
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 - three siblings of S14G-1 and S14G-7 (October 26, 2026).
#
# WAVE 2's brief for the files that own the battle, the march, the landing and
# the desk: `combat_executor`, `movement_executor`, `world_state`,
# `naval_executor`, `battle_diorama`, `question_desk` and the three client
# scripts that print a capture. Each class below is one sibling; the
# orchestrator renumbers `S14G-X10` / `S14G-X12` / `S14G-X29` at the merge.
#
# S14G-X10 - THE CLIENT STILL PRINTED A LIBERATION AS A CAPTURE. Wave 1 made a
# province whose home nation is an ally or a client of the capturer, retaken from
# an enemy, a LIBERATION handed back at once (`world_state.liberates_ally_ground`,
# the backend's one sentence `liberation_line`). Three client lines never heard:
# `main.gd::_display_battle_result` printed "⚑ Munich captured! ⚑" under the
# liberation's own reply, `enemy_phase_dialog.gd` printed "Munich CAPTURED!" (and
# "Region captured: …", and " — Swabia falls") over the enemy phase's version, and
# `battle_diorama.gd::_sub_banner_text` printed "Munich falls to France." over the
# tableau. The fix carries the key through, from every producer to every reader:
# the event the backend stamps (`liberated_to`, now also `liberated_to_name` - the
# court as it prints, article and all: "the Kingdom of Italy"), the diorama payload
# (`liberated_to` and `liberation_line`, built by `build_battle_diorama` from the
# battle event) and the three client lines, which read the liberation when the
# payload says so: "⚑ Munich — handed back to Bavaria ⚑" / "MUNICH HANDED BACK TO
# BAVARIA" / " — Swabia is handed back to Bavaria" / the backend's own sentence.
# No new seam: the key rides the predicate's answer, so held down
# (`liberates_ally_ground` -> '') no key is written and every client line is
# today's, byte for byte.
#
# S14G-X12 - ONLY THE MAIN ATTACK PRINTED THE `[Alarm]` LINE. `_alarm_line`
# (DDB-42, now with each clipped row's applied share) is read at the main attack's
# compose step from the rows written since `_attack_open`; every other site that
# writes alarm rows for the player printed nothing: the garrison assault (the win,
# the capital's +15, the capture's +2), the glorious charge, the attack's own
# unopposed march into an empty province (+2), the plain march's walk-in capture
# (+2), the auto-bombardment's advance, the naval landing's capture (+2), the
# reckless auto-charge and the siege that completes at the turn's tick (+2). The fix: one mark (`CombatExecutor._alarm_mark`, the
# `rows_before` idiom) and one rider (`CombatExecutor._alarm_rider`, `_alarm_line`
# for the player's own corps only - an AI corps' reply prints nothing) at each
# site. No new seam: it counts the book the pipeline already writes.
#
# S14G-X29 - THE FRONT NOTE'S OTHER SITES. S14G-7 told a march into an ally's
# province whose war a truce of ours leaves running that "a corps there will not
# fight, and marches home if the ground changes hands" - on the plain march and
# the retreat. Every other site that prints the campaign pay of a step onto allied
# soil printed the pay and not the front: the battle's advance, the auto-bombardment
# kill's advance, the charge's advance, a breakout and a rout, the bare attack's
# approach step, the general attack's fallback step, the pursuit ask's first march,
# the reckless cavalry's ride, rout and advance, the naval expedition's card and
# landing, and the desk's "can he reach it". `movement_executor.front_clause` (the
# clause form beside `campaign_pay_clause`) and `front_note`/`front_line` print the
# ONE sentence (`front_line`) beside the pay at each. No new seam: the predicate is
# `diplomacy.truce_front_of_an_ally`; the AI's corps print nothing.
#
# S14G-X50 / S14G-X51 - S14G-11's guarded ground reaches two more doors. The
# typed `move to <province>` into ground an active guard_neutrality design guards
# (Prussia's Armed Neutrality) was silent - "Soult, move to Berlin" moved and the
# -25 followed - and the pursuit ask (`clarification_kind: pursuit_ask`) printed
# the detour and pay riders but not the guarded ground its road crosses. The plain
# move (`movement_executor.move_guard_ask`, one hop or the auto-upgraded road) asks
# first, free, on the march ask's channel ("... - move or cancel?"; the answered
# option carries the `_guard_confirmed` flag, plumbed by the executor into
# `_execute_move(guard_confirmed=...)`) and its reply carries the
# sentence as a rider (`guard_note`); the pursuit ask prints
# `strategic.march_guard_sentence` of its road beside the other riders. No new
# seam: the reading is `strategic.march_guard_reading` over
# `agendas.guarded_provinces_for` (the trap's own map; held down it is today's
# silence), player only.
#
# Every pin runs on the shipped 1805 board (`WorldState.from_scenario`); the
# client pins read the `.gd` source (the Godot engine is not run).

_R13_REPO = Path(__file__).resolve().parents[1]
_R13_SCENARIO = (_R13_REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")
_R13_SCRIPTS = _R13_REPO / "godot-client" / "project-sovereign" / "scripts"

_R13_MUNICH_LINE = "Munich, Bavaria's capital, retaken — handed back to Bavaria."
_R13_SWABIA_LINE = "Swabia, Bavaria's province, retaken — handed back to Bavaria."
_R13_SWABIA_FRONT = ("Swabia is Bavaria's front — Austria, under truce with us, is at war "
                     "with her; a corps there will not fight, and marches home if the "
                     "ground changes hands.")
_R13_GALICIA_FRONT = ("Galicia is Spain's front — Britain, under truce with us, is at war "
                      "with her; a corps there will not fight, and marches home if the "
                      "ground changes hands.")
_R13_SWABIA_PAY = "Swabia is Bavaria's soil — the corps standing there are fed by contract"


def _r13_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r13_boot():
    from backend.models.world_state import WorldState
    with _r13_quiet():
        return WorldState.from_scenario(str(_R13_SCENARIO))


def _r13_copy(boot):
    from backend.models.world_state import WorldState
    return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


def _r13_executor():
    from backend.commands.executor import CommandExecutor
    with _r13_quiet():
        return CommandExecutor()


def _r13_take(world, region: str, nation: str = "Austria") -> None:
    """The enemy's capture, staged through the real seam, then the alarm book
    cleared so a test reads only the act under test."""
    with _r13_quiet():
        world.capture_region(region, nation)
    world.threat_sources_this_turn = []


def _r13_clear_austria(world, keep=()) -> None:
    for m in world.marshals.values():
        if m.nation == "Austria" and m.name not in keep:
            m.location = "Tyrol"


def _r13_sign_the_truce(world) -> None:
    """France and Austria sign the armistice through the one ratifier: Bavaria
    stays allied to France and at war with Austria - Swabia is her front."""
    from backend.game_logic import diplomacy as D
    variant = D.armistice_variant_for(world, "France", "Austria")
    with _r13_quiet():
        event = world._ratify_treaty({"type": variant, "proposer_nation": "France",
                                      "target_nation": "Austria", "sweeteners": [],
                                      "demands": [], "clauses": []})
    assert event and event.get("type") != "diplomatic_treaty_failed", event
    assert world.get_diplomatic_state("France", "Austria") == "ARMISTICE"


def _r13_front_world(boot):
    world = _r13_copy(boot)
    _r13_sign_the_truce(world)
    return world


def _r13_command(executor, world, raw: str, marshal: str, action: str, target, seed: int = 7):
    random.seed(seed)
    with _r13_quiet():
        return executor.execute({"command": {
            "raw_input": raw, "marshal": marshal, "action": action, "target": target}},
            {"world": world})


def _r13_alarm_text(world) -> str:
    """The line the player should read for ALL the rows the act wrote."""
    from backend.commands.combat_executor import CombatExecutor
    return CombatExecutor._alarm_line(world, 0)


def _r13_gd(name: str) -> str:
    return (_R13_SCRIPTS / name).read_text(encoding="utf-8")


def _r13_func(src: str, name: str) -> str:
    """The body of one GDScript func (to the next top-level func)."""
    m = re.search(rf"(?ms)^(?:static )?func {re.escape(name)}\(.*?(?=^(?:static )?func |^const |\Z)", src)
    assert m, name
    return m.group(0)


def _r13_munich_board(boot, *, seam_down=False, monkeypatch=None):
    """Austria holds Munich (Bavaria's capital), Mack stands in it, Ney is one
    march off with the army - the S14G-1 sighting."""
    if seam_down:
        from backend.models import world_state as ws
        monkeypatch.setattr(ws, "liberates_ally_ground", lambda *a, **k: "")
    world = _r13_copy(boot)
    _r13_take(world, "Munich")
    mack = world.get_marshal("Mack")
    mack.location, mack.strength = "Munich", 2500
    ney = world.get_marshal("Ney")
    ney.location, ney.strength = "Franche-Comte", 40000
    world.calculate_visibility()
    return world


# ══════════════════════════════════════════════════════════════════════════
# S14G-X10 - the client's three lines read a liberation as one
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX10:
    """The sighting: Ney retakes Munich for Bavaria. The backend's reply says
    "Munich, Bavaria's capital, retaken — handed back to Bavaria." and the
    client printed "⚑ Munich captured! ⚑" under it (and the enemy phase's and the
    tableau's lines read "CAPTURED!" / "falls to France.")."""

    def test_the_battle_event_names_the_court_it_went_back_to(self, _r13_boot):
        world = _r13_munich_board(_r13_boot)
        result = _r13_command(_r13_executor(), world, "Ney, attack Mack", "Ney", "attack", "Mack")
        assert result["success"] is True
        battle = result["events"][0]
        assert battle["type"] == "battle" and battle["region_conquered"] is True
        assert battle["liberated_to"] == "Bavaria"
        assert battle["liberated_to_name"] == "Bavaria"
        assert battle["region_name"] == "Munich"

    def test_the_diorama_payload_carries_the_line(self, _r13_boot):
        world = _r13_munich_board(_r13_boot)
        result = _r13_command(_r13_executor(), world, "Ney, attack Mack", "Ney", "attack", "Mack")
        payload = result["battle_diorama"]
        assert payload["region_conquered"] is True
        assert payload["liberated_to"] == "Bavaria"
        assert payload["liberation_line"] == _R13_MUNICH_LINE
        # the same payload rides the event (the enemy-phase transport)
        assert result["events"][0]["diorama"] is payload

    def test_a_conquest_carries_no_liberation_key_anywhere(self, _r13_boot, monkeypatch):
        """THE SEAM held down (wave 1's `liberates_ally_ground` -> ''): the
        same board is a conquest, and nothing the client reads says otherwise -
        the event, the payload and so every client line are today's."""
        world = _r13_munich_board(_r13_boot, seam_down=True, monkeypatch=monkeypatch)
        result = _r13_command(_r13_executor(), world, "Ney, attack Mack", "Ney", "attack", "Mack")
        battle = result["events"][0]
        assert battle["region_conquered"] is True
        assert "liberated_to" not in battle and "liberated_to_name" not in battle
        payload = result["battle_diorama"]
        assert payload["region_conquered"] is True
        assert "liberated_to" not in payload and "liberation_line" not in payload

    def test_a_field_battle_that_took_nothing_carries_none(self, _r13_boot):
        world = _r13_copy(_r13_boot)
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Swabia", 2500   # Bavaria's own, held by Bavaria: no capture
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Franche-Comte", 40000
        world.calculate_visibility()
        result = _r13_command(_r13_executor(), world, "Ney, attack Mack", "Ney", "attack", "Mack")
        payload = result["battle_diorama"]
        assert payload["region_conquered"] is False
        assert "liberated_to" not in payload and "liberation_line" not in payload
        assert "liberated_to" not in result["events"][0]

    def test_the_court_rides_with_its_article(self, _r13_boot):
        """A court that reads with "the": the client has no article rule, so
        the capture's result carries the printed name beside the key."""
        world = _r13_copy(_r13_boot)
        _r13_take(world, "Piedmont")
        assert world.get_diplomatic_state("France", "KingdomOfItaly") == "VASSAL"
        ney = world.get_marshal("Ney")
        ney.location = "Savoy"
        capture = _r13_executor()._combat._attempt_region_capture(
            ney, "Piedmont", world, {"world": world})
        assert capture["liberated_to"] == "KingdomOfItaly"
        assert capture["liberated_to_name"] == "the Kingdom of Italy"
        assert capture["liberation_line"] == (
            "Piedmont, the Kingdom of Italy's province, retaken — handed back to "
            "the Kingdom of Italy.")

    def test_every_producer_stamps_the_printed_name(self, _r13_boot):
        """The conquest event of the garrison assault, the unopposed march, the
        plain march's `move` event and the glorious charge's event: each stamps
        `liberated_to_name` beside `liberated_to`."""
        ex = _r13_executor()
        # the garrison assault (a detachment that fights)
        world = _r13_copy(_r13_boot)
        _r13_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        world.get_marshal("Ney").location = "Rhineland"
        region = world.get_region("Swabia")
        region.garrison_strength, region.garrison_detachment = 3000, True
        world.calculate_visibility()
        result = _r13_command(ex, world, "Ney, attack Swabia", "Ney", "attack", "Swabia")
        conquest = [e for e in result["events"] if e["type"] == "conquest"][0]
        assert conquest["liberated_to"] == "Bavaria" and conquest["liberated_to_name"] == "Bavaria"
        # the unopposed attack march
        world = _r13_copy(_r13_boot)
        _r13_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        world.get_marshal("Ney").location = "Rhineland"
        world.calculate_visibility()
        result = _r13_command(ex, world, "Ney, attack Swabia", "Ney", "attack", "Swabia")
        assert result["events"][0]["liberated_to_name"] == "Bavaria"
        # the plain march
        world = _r13_copy(_r13_boot)
        _r13_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        world.calculate_visibility()
        result = _r13_command(ex, world, "Bernadotte, move to Swabia", "Bernadotte", "move", "Swabia")
        assert result["events"][0]["liberated_to"] == "Bavaria"
        assert result["events"][0]["liberated_to_name"] == "Bavaria"
        # the glorious charge
        world = _r13_copy(_r13_boot)
        _r13_take(world, "Swabia")
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Swabia", 600
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Franche-Comte", 3
        world.calculate_visibility()
        random.seed(5)
        with _r13_quiet():
            charge = ex._combat._execute_glorious_charge(murat, "Mack", world, {"world": world})
        assert charge["events"][0]["liberated_to"] == "Bavaria"
        assert charge["events"][0]["liberated_to_name"] == "Bavaria"

    def test_the_auto_bombardment_kill_stamps_it_too(self, _r13_boot):
        from backend.commands.combat_executor import CombatExecutor
        from backend.models.marshal import StrategicOrder
        world = _r13_copy(_r13_boot)
        _r13_take(world, "Swabia")
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Swabia", 300
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Franche-Comte", 40000
        gun = world.get_marshal("Lannes")
        gun.artillery = True
        gun.location = "Franche-Comte"
        gun.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="support Ney")
        world.calculate_visibility()

        def _lethal(self, m, defender, w, gs):
            defender.strength = 0
            return {"success": True, "bombardment_result": {"defender": {"casualties": 300}}}

        real = CombatExecutor._execute_bombardment
        CombatExecutor._execute_bombardment = _lethal
        try:
            result = _r13_command(_r13_executor(), world, "Ney, attack Mack", "Ney", "attack", "Mack")
        finally:
            CombatExecutor._execute_bombardment = real
        assert result.get("auto_bombardment") is True
        event = result["events"][0]
        assert event["liberated_to"] == "Bavaria" and event["liberated_to_name"] == "Bavaria"

    # ── the three client lines (source pins; the engine is not run) ─────────

    def test_the_terminal_flourish_reads_the_liberation(self):
        body = _r13_func(_r13_gd("main.gd"), "_display_battle_result")
        assert 'event.get("liberated_to_name", "")' in body
        assert 'event.get("liberated_to", "")' in body
        assert 'Utils.display_nation_name(liberated_key)' in body
        assert '" — handed back to " + liberated_home + " ⚑[/color]"' in body
        # the capture flourish survives for a capture, in the else branch
        assert body.index("handed back to") < body.index('captured! ⚑[/color]")')
        assert re.search(r'else:\n\t\t\tadd_output\("\[color=#" \+ Utils\.COLOR_CONQUEST \+ "\]   ⚑ " '
                         r'\+ region_name \+ " captured! ⚑\[/color\]"\)', body)

    def test_the_enemy_phase_lines_read_the_liberation(self):
        src = _r13_gd("enemy_phase_dialog.gd")
        helper = _r13_func(src, "_liberated_court")
        assert 'event.get("liberated_to", "")' in helper
        assert 'event.get("liberated_to_name", "")' in helper
        assert "Utils.display_nation_name(key)" in helper
        # the battle arm
        assert 'str(region).to_upper() + " HANDED BACK TO " + battle_home.to_upper() + battle_was' in src
        assert '" CAPTURED!" + battle_was + battle_choice_str' in src          # a capture keeps its line
        # the conquest arm
        assert 'str(region).to_upper() + " HANDED BACK TO " + conquest_home.to_upper() + conquest_was' in src
        assert '"]    Region captured: " + region + conquest_was + choice_str' in src
        # the move arm
        assert '" is handed back to " + move_home' in src
        assert '" falls"' in src
        # one reader for all three
        assert src.count("_liberated_court(") == 4   # the definition + the three arms

    def test_the_tableau_banner_reads_the_payload_line(self):
        body = _r13_func(_r13_gd("battle_diorama.gd"), "_sub_banner_text")
        assert 'str(_data.get("liberation_line", ""))' in body
        assert 'str(_data.get("liberated_to", "")) != ""' in body
        assert body.index("return liberation") < body.index('"%s falls to %s."')
        assert '"%s falls to %s."' in body and '"%s is lost."' in body       # the capture's own

    def test_the_client_reads_exactly_the_keys_the_backend_writes(self):
        """The wire: each key a client line reads is a key the backend stamps."""
        import inspect
        from backend.commands import combat_executor, movement_executor
        from backend.game_logic import battle_diorama
        backend = (inspect.getsource(combat_executor) + inspect.getsource(movement_executor)
                   + inspect.getsource(battle_diorama))
        for key in ("liberated_to", "liberated_to_name", "liberation_line"):
            assert f'"{key}"' in backend, key
        client = (_r13_gd("main.gd") + _r13_gd("enemy_phase_dialog.gd") + _r13_gd("battle_diorama.gd"))
        for key in ("liberated_to", "liberated_to_name", "liberation_line"):
            assert f'"{key}"' in client, key


# ══════════════════════════════════════════════════════════════════════════
# S14G-X12 - the [Alarm] line at every site that writes alarm rows
# ══════════════════════════════════════════════════════════════════════════

def _r13_vienna_board(boot, *, garrison: int = 8000, lead: str = "Ney", lead_at: str = "Moravia"):
    """Austria's own capital, undefended by marshals: a CONQUEST on every road
    (no ally's ground), so the rows are the full set - the win, the capital's
    +15 and the capture's +2."""
    world = _r13_copy(boot)
    _r13_clear_austria(world)
    marshal = world.get_marshal(lead)
    marshal.location, marshal.strength = lead_at, 40000
    vienna = world.get_region("Vienna")
    vienna.garrison_strength, vienna.garrison_detachment = garrison, False
    world.threat_sources_this_turn = []
    world.calculate_visibility()
    return world


class TestS14GX12:
    """The old reading, on the shipped board: every one of these acts wrote
    alarm rows (`world.threat_sources_this_turn`, the bar rose) and the reply
    said nothing of Europe - only the main attack's compose step read the rows.
    Each reply now ends its capture's paragraph with the main attack's own
    `[Alarm]` line, from the act's own mark."""

    def test_the_garrison_assault_prints_the_alarm(self, _r13_boot):
        world = _r13_vienna_board(_r13_boot)
        result = _r13_command(_r13_executor(), world, "Ney, attack Vienna", "Ney", "attack", "Vienna", seed=3)
        assert result["success"] is True
        msg = result["message"]
        assert world.get_region("Vienna").controller == "France"
        assert ("\n[Alarm] Europe's alarm rises +20 — Won a battle +3, Captured an enemy "
                "capital +15, Conquered territory +2.") in msg
        assert _r13_alarm_text(world) in msg          # shown == written
        # after the capture's words, before the plunder question
        assert msg.index("Captured: Austria → France") < msg.index("[Alarm]") < msg.index("Plunder it")

    def test_a_liberation_assault_prints_only_what_it_scored(self, _r13_boot):
        """Munich's garrison, retaken for Bavaria: the win alone - no +15, no
        +2 - so the line is short and true."""
        world = _r13_copy(_r13_boot)
        _r13_take(world, "Munich")
        world.get_marshal("Mack").location = "Tyrol"
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Franche-Comte", 40000
        region = world.get_region("Munich")
        region.garrison_strength, region.garrison_detachment = 3000, True
        world.calculate_visibility()
        result = _r13_command(_r13_executor(), world, "Ney, attack Munich", "Ney", "attack", "Munich")
        assert _R13_MUNICH_LINE in result["message"]
        assert "\n[Alarm] Europe's alarm rises +3 — Won a battle +3." in result["message"]
        assert "capital" not in result["message"].split("[Alarm]")[1].split("\n")[0]

    def test_the_cap_at_100_is_said_on_the_assault_too(self, _r13_boot):
        world = _r13_vienna_board(_r13_boot)
        world.threat_by_target["France"] = 90
        result = _r13_command(_r13_executor(), world, "Ney, attack Vienna", "Ney", "attack", "Vienna", seed=3)
        line = _r13_alarm_text(world)
        assert "(capped at 100)" in line and "counted)" in line
        assert line in result["message"]

    def test_the_glorious_charge_prints_the_alarm(self, _r13_boot):
        world = _r13_copy(_r13_boot)
        _r13_clear_austria(world, keep=("Mack",))
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Vienna", 600
        world.get_region("Vienna").garrison_strength = 0
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Moravia", 3
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        random.seed(5)
        with _r13_quiet():
            result = _r13_executor()._combat._execute_glorious_charge(
                murat, "Mack", world, {"world": world})
        msg = result["message"]
        assert ("\n[Alarm] Europe's alarm rises +20 — Conquered territory +2, Won a battle +3, "
                "Captured an enemy capital +15.") in msg
        assert _r13_alarm_text(world) in msg
        assert msg.index("[Alarm]") < msg.index("Recklessness reset")

    def test_the_unopposed_attack_march_prints_the_alarm(self, _r13_boot):
        world = _r13_vienna_board(_r13_boot)
        world.get_marshal("Ney").location = "Moravia"
        result = _r13_command(_r13_executor(), world, "Ney, attack Hungary", "Ney", "attack", "Hungary", seed=3)
        msg = result["message"]
        assert "Ney marches from Moravia into Hungary unopposed!" in msg
        assert "\n[Alarm] Europe's alarm rises +2 — Conquered territory +2." in msg
        assert msg.index("Captured: Austria → France") < msg.index("[Alarm]") < msg.index("Plunder it")

    def test_the_plain_march_prints_the_alarm_after_its_own_figures(self, _r13_boot):
        world = _r13_vienna_board(_r13_boot)
        result = _r13_command(_r13_executor(), world, "Ney, move to Hungary", "Ney", "move", "Hungary")
        msg = result["message"]
        assert "Hungary falls to France! (was Austria)" in msg
        # the alarm closes the capture's sentence AFTER the march's attrition,
        # never inside it
        assert re.search(r"lost to march\)\n\[Alarm\] Europe's alarm rises \+2 — "
                         r"Conquered territory \+2\.", msg), msg
        assert _r13_alarm_text(world) in msg

    def test_the_march_that_takes_nothing_prints_no_alarm(self, _r13_boot):
        world = _r13_copy(_r13_boot)
        world.get_marshal("Ney").location = "Rhineland"
        result = _r13_command(_r13_executor(), world, "Ney, move to Lorraine", "Ney", "move", "Lorraine")
        assert "[Alarm]" not in result["message"]

    def test_the_auto_bombardment_advance_prints_the_alarm(self, _r13_boot):
        from backend.commands.combat_executor import CombatExecutor
        from backend.models.marshal import StrategicOrder
        world = _r13_copy(_r13_boot)
        _r13_clear_austria(world)
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Vienna", 300
        world.get_region("Vienna").garrison_strength = 0
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Moravia", 40000
        gun = world.get_marshal("Lannes")
        gun.artillery = True
        gun.location = "Moravia"
        gun.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="support Ney")
        world.threat_sources_this_turn = []
        world.calculate_visibility()

        def _lethal(self, m, defender, w, gs):
            defender.strength = 0
            return {"success": True, "bombardment_result": {"defender": {"casualties": 300}}}

        real = CombatExecutor._execute_bombardment
        CombatExecutor._execute_bombardment = _lethal
        try:
            result = _r13_command(_r13_executor(), world, "Ney, attack Mack", "Ney", "attack", "Mack")
        finally:
            CombatExecutor._execute_bombardment = real
        assert result.get("auto_bombardment") is True
        msg = result["message"]
        assert "The preparatory bombardment destroyed Mack." in msg
        assert ("\n[Alarm] Europe's alarm rises +20 — Conquered territory +2, Won a battle +3, "
                "Captured an enemy capital +15.") in msg
        assert _r13_alarm_text(world) in msg

    def test_the_landings_capture_prints_the_alarm(self, _r13_boot):
        world = _r13_copy(_r13_boot)
        world.fleets["Britain"]["ships"] = 0
        soult = world.get_marshal("Soult")
        soult.location, soult.strength, soult.strategic_order = "Brittany", 10000, None
        world._build_marshal_index()
        world.threat_sources_this_turn = []
        with _r13_quiet():
            result = _r13_executor()._naval._execute_naval_expedition(
                {"marshal": "Soult", "action": "naval_expedition", "target": "Munster",
                 "raw_command": "land Soult in Munster confirmed"}, {"world": world})
        assert result["landed"] is True
        msg = result["message"]
        assert "\n[Alarm] Europe's alarm rises +2 — Conquered territory +2." in msg
        assert msg.index("THE LANDING") < msg.index("[Alarm]") < msg.index("Plunder it")

    def test_the_reckless_auto_charge_prints_the_alarm(self, _r13_boot):
        world = _r13_copy(_r13_boot)
        _r13_clear_austria(world, keep=("Mack",))
        mack = world.get_marshal("Mack")
        mack.location, mack.strength = "Vienna", 600
        world.get_region("Vienna").garrison_strength = 0
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Moravia", 4
        world.threat_sources_this_turn = []
        world.calculate_visibility()
        random.seed(5)
        with _r13_quiet():
            events = world._process_reckless_cavalry_turn_start()
        (charge,) = [e for e in events if e["type"] == "auto_glorious_charge"]
        text = charge["message"]
        assert "Vienna captured by France!" in text
        assert ("\n[Alarm] Europe's alarm rises +18 — Won a battle +3, Captured an enemy "
                "capital +15.") in text
        assert _r13_alarm_text(world) in text
        assert text.index("[Alarm]") < text.index("FREE ACTION")

    def test_the_sieges_completion_prints_the_alarm(self, _r13_boot):
        """The fortress that completes at the turn's tick (a sibling the sweep
        found): its capture wrote the +2 and the `occupation_complete` line said
        nothing of Europe. A liberation writes no row, so it prints none."""
        world = _r13_vienna_board(_r13_boot)
        ney = world.get_marshal("Ney")
        ney.location = "Hungary"
        world.get_region("Hungary").buildings.append({"type": "fortification", "level": 1})
        capture = _r13_executor()._combat._attempt_region_capture(
            ney, "Hungary", world, {"world": world}, had_garrison=False)
        assert capture["occupation_started"] is True
        world.threat_sources_this_turn = []
        with _r13_quiet():
            events = world._process_tactical_states()
        (done,) = [e for e in events if e.get("type") == "occupation_complete"]
        assert done["message"].startswith("Ney has secured the fortress at Hungary!")
        assert "\n[Alarm] Europe's alarm rises +2 — Conquered territory +2." in done["message"]
        assert _r13_alarm_text(world) in done["message"]
        # a liberation (Swabia, retaken for Bavaria) writes no row and prints none
        world = _r13_copy(_r13_boot)
        _r13_take(world, "Swabia")
        world.get_marshal("Mack").location = "Tyrol"
        ney = world.get_marshal("Ney")
        ney.location = "Swabia"
        world.get_region("Swabia").buildings.append({"type": "fortification", "level": 1})
        _r13_executor()._combat._attempt_region_capture(
            ney, "Swabia", world, {"world": world}, had_garrison=False)
        with _r13_quiet():
            events = world._process_tactical_states()
        (done,) = [e for e in events if e.get("type") == "occupation_complete"]
        assert done["message"] == f"Ney has secured the fortress at Swabia! {_R13_SWABIA_LINE}"

    def test_the_ai_corps_prints_nothing(self, _r13_boot):
        """The alarm is the player's ledger: the rider answers '' for an AI
        corps, whatever rows stand (Golden Rule 5 keeps the AI on the same
        rows; only the player's text changes)."""
        from backend.commands.combat_executor import CombatExecutor
        from backend.game_logic.coalition import add_threat
        world = _r13_copy(_r13_boot)
        world.threat_sources_this_turn = []
        mark = CombatExecutor._alarm_mark(world)
        add_threat(world, 3, "battle_win", target="France")
        assert mark == 0
        assert CombatExecutor._alarm_rider(world, world.get_marshal("Ney"), mark) == (
            "\n[Alarm] Europe's alarm rises +3 — Won a battle +3.")
        assert CombatExecutor._alarm_rider(world, world.get_marshal("Kutuzov"), mark) == ""
        assert CombatExecutor._alarm_rider(world, world.get_marshal("Ney"), None) == ""

    def test_the_rider_prints_only_rows_since_its_mark(self, _r13_boot):
        from backend.commands.combat_executor import CombatExecutor
        from backend.game_logic.coalition import add_threat
        world = _r13_copy(_r13_boot)
        world.threat_sources_this_turn = []
        add_threat(world, 2, "region_capture", target="France")       # an earlier act's row
        mark = CombatExecutor._alarm_mark(world)
        assert mark == 1
        assert CombatExecutor._alarm_rider(world, world.get_marshal("Ney"), mark) == ""
        add_threat(world, 3, "battle_win", target="France")
        assert CombatExecutor._alarm_rider(world, world.get_marshal("Ney"), mark) == (
            "\n[Alarm] Europe's alarm rises +3 — Won a battle +3.")


# ══════════════════════════════════════════════════════════════════════════
# S14G-X29 - the front note beside the campaign pay at every other site
# ══════════════════════════════════════════════════════════════════════════

def _r13_assert_pay_then_front(message: str, front: str = _R13_SWABIA_FRONT,
                               pay: str = _R13_SWABIA_PAY) -> None:
    assert front in message, message
    assert pay in message, message
    assert message.index(pay) < message.index(front)


class TestS14GX29:
    """The sighting (S14G-7's sea road): a 2-AP step onto Swabia after the
    armistice with Austria, told the pay ("Swabia is Bavaria's soil — … −288g
    more a turn") and nothing of the front (Austria, under truce with us, is at
    war with Bavaria). S14G-7 wired the plain march and the retreat; these are
    the other sites that print the same pay."""

    def test_the_battle_advance(self, _r13_boot):
        world = _r13_front_world(_r13_boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Swabia", 2500
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Franche-Comte", 40000
        world.calculate_visibility()
        result = _r13_command(_r13_executor(), world, "Ney, attack Kutuzov", "Ney", "attack", "Kutuzov")
        assert "Ney advances into Swabia." in result["message"]
        _r13_assert_pay_then_front(result["message"])

    def test_the_glorious_charges_advance(self, _r13_boot):
        world = _r13_front_world(_r13_boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Swabia", 600
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Franche-Comte", 3
        world.calculate_visibility()
        random.seed(5)
        with _r13_quiet():
            result = _r13_executor()._combat._execute_glorious_charge(
                murat, "Kutuzov", world, {"world": world})
        assert "Murat advances into Swabia." in result["message"]
        _r13_assert_pay_then_front(result["message"])

    def test_the_auto_bombardments_advance(self, _r13_boot):
        from backend.commands.combat_executor import CombatExecutor
        from backend.models.marshal import StrategicOrder
        world = _r13_front_world(_r13_boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Swabia", 300
        ney = world.get_marshal("Ney")
        ney.location, ney.strength = "Franche-Comte", 40000
        gun = world.get_marshal("Lannes")
        gun.artillery = True
        gun.location = "Franche-Comte"
        gun.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="support Ney")
        world.calculate_visibility()

        def _lethal(self, m, defender, w, gs):
            defender.strength = 0
            return {"success": True, "bombardment_result": {"defender": {"casualties": 300}}}

        real = CombatExecutor._execute_bombardment
        CombatExecutor._execute_bombardment = _lethal
        try:
            result = _r13_command(_r13_executor(), world, "Ney, attack Kutuzov", "Ney", "attack", "Kutuzov")
        finally:
            CombatExecutor._execute_bombardment = real
        assert "Ney advances into Swabia." in result["message"]
        _r13_assert_pay_then_front(result["message"])

    def test_the_bare_attacks_approach_step(self, _r13_boot):
        """`Ney, attack` with nobody in reach and no pursuit ask: the one step
        toward the nearest foe says the pay and the front."""
        world = _r13_front_world(_r13_boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Tyrol", 600
        ney = world.get_marshal("Ney")
        ney.location = "Rhineland"
        world.calculate_visibility()
        with _r13_quiet():
            result = _r13_executor()._combat._execute_attack(
                ney, None, world, {"world": world}, {"action": "attack", "marshal": "Ney"})
        assert "Ney advances from Rhineland to Swabia, moving toward Kutuzov at Tyrol!" in result["message"]
        _r13_assert_pay_then_front(result["message"])

    def test_the_general_attacks_fallback_step(self, _r13_boot):
        world = _r13_front_world(_r13_boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Tyrol", 600
        for m in world.marshals.values():
            if m.nation == "France" and m.name != "Ney":
                m.location = "Lorraine"
        world.get_marshal("Ney").location = "Rhineland"
        world.calculate_visibility()
        with _r13_quiet():
            result = _r13_executor()._combat._execute_general_attack(
                {"action": "attack", "command_type": "general", "raw_input": "attack"},
                {"world": world})
        assert "Ney advances toward Kutuzov:" in result["message"]
        _r13_assert_pay_then_front(result["message"])

    def test_the_pursuit_ask_names_the_front_of_the_first_march(self, _r13_boot):
        world = _r13_front_world(_r13_boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Tyrol", 600
        world.get_marshal("Ney").location = "Rhineland"
        world.calculate_visibility()
        result = _r13_command(_r13_executor(), world, "Ney, attack Kutuzov", "Ney", "attack", "Kutuzov")
        assert result.get("clarification_kind") == "pursuit_ask"
        assert "Kutuzov stands at Tyrol, three marches off." in result["message"]
        _r13_assert_pay_then_front(result["message"])
        # the question still closes the sentence
        assert result["message"].index(_R13_SWABIA_FRONT) < result["message"].index(
            "Pursue him (2 AP")

    def test_a_breakout_onto_the_front(self, _r13_boot, monkeypatch):
        world = _r13_front_world(_r13_boot)
        ney = world.get_marshal("Ney")
        ney.location = "Franche-Comte"
        kut = world.get_marshal("Kutuzov")
        kut.location = "Franche-Comte"
        monkeypatch.setattr(world, "get_safe_retreat_destination", lambda *a, **k: "Swabia")
        with _r13_quiet():
            text = _r13_executor()._combat.apply_successful_breakout(ney, kut, world)
        assert text.startswith("Ney falls back on Swabia, his corps disordered but in the field.")
        _r13_assert_pay_then_front(text)

    def test_a_rout_onto_the_front(self, _r13_boot, monkeypatch):
        world = _r13_front_world(_r13_boot)
        ney = world.get_marshal("Ney")
        ney.location = "Franche-Comte"
        kut = world.get_marshal("Kutuzov")
        kut.location = "Franche-Comte"
        monkeypatch.setattr(world, "get_safe_retreat_destination", lambda *a, **k: "Swabia")
        with _r13_quiet():
            text = _r13_executor()._combat._apply_forced_retreat_or_break(
                ney, kut, world, skip_fate=True)
        assert "Ney's broken army flees to Swabia!" in text
        _r13_assert_pay_then_front(text)

    def test_the_reckless_cavalrys_free_ride(self, _r13_boot):
        world = _r13_front_world(_r13_boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Tyrol", 600
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Rhineland", 4
        world.calculate_visibility()
        random.seed(5)
        with _r13_quiet():
            events = world._process_reckless_cavalry_turn_start()
        (ride,) = [e for e in events if e["type"] == "reckless_move"]
        assert "Auto-moved: Rhineland → Swabia" in ride["message"]
        _r13_assert_pay_then_front(ride["message"])
        assert ride["message"].index(_R13_SWABIA_FRONT) < ride["message"].index("FREE ACTION")

    def test_the_reckless_auto_charges_advance(self, _r13_boot):
        world = _r13_front_world(_r13_boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Swabia", 600
        murat = world.get_marshal("Murat")
        murat.location, murat.recklessness = "Franche-Comte", 4
        world.calculate_visibility()
        random.seed(5)
        with _r13_quiet():
            events = world._process_reckless_cavalry_turn_start()
        (charge,) = [e for e in events if e["type"] == "auto_glorious_charge"]
        _r13_assert_pay_then_front(charge["message"])

    def test_the_naval_card_and_the_landing(self, _r13_boot):
        """The sea road's own sighting (#6): a landing on an ally's coast whose
        war a truce of ours leaves running - Spain's Galicia, France in an
        armistice with Britain."""
        world = _r13_copy(_r13_boot)
        world.diplomatic_states[world._make_diplo_key("France", "Britain")] = "ARMISTICE"
        soult = world.get_marshal("Soult")
        soult.location, soult.strength, soult.strategic_order = "Brittany", 10000, None
        world._build_marshal_index()
        ex = _r13_executor()
        with _r13_quiet():
            card = ex._naval._execute_naval_expedition(
                {"marshal": "Soult", "action": "naval_expedition", "target": "Galicia",
                 "raw_command": "land Soult in Galicia"}, {"world": world})
        assert card["naval_confirm"] is True
        pay = "Galicia is Spain's soil — the corps standing there are fed by contract"
        _r13_assert_pay_then_front(card["message"], _R13_GALICIA_FRONT, pay)
        assert card["message"].index(_R13_GALICIA_FRONT) < card["message"].index("Sail? (yes / no)")
        world.fleets["Britain"]["ships"] = 0
        with _r13_quiet():
            landed = ex._naval._execute_naval_expedition(
                {"marshal": "Soult", "action": "naval_expedition", "target": "Galicia",
                 "raw_command": "land Soult in Galicia confirmed"}, {"world": world})
        assert landed["landed"] is True
        _r13_assert_pay_then_front(landed["message"], _R13_GALICIA_FRONT, pay)

    def test_the_desk_answers_what_the_march_would(self, _r13_boot):
        from backend.ai.question_desk import answer_board_question
        world = _r13_front_world(_r13_boot)
        world.get_marshal("Ney").location = "Rhineland"
        world.calculate_visibility()
        said = answer_board_question(world, {
            "kind": "reach", "subject": "Ney", "subject_type": "marshal", "place": "Swabia"})
        assert said.startswith("Yes, Sire — Ney can reach Swabia from Rhineland this very turn")
        _r13_assert_pay_then_front(said)

    def test_before_the_truce_no_site_says_a_front(self, _r13_boot):
        """The negative: the same stops on the boot board (France at war with
        Austria, no armistice) are not fronts - the pay stands alone."""
        from backend.ai.question_desk import answer_board_question
        world = _r13_copy(_r13_boot)
        world.get_marshal("Ney").location = "Rhineland"
        world.calculate_visibility()
        said = answer_board_question(world, {
            "kind": "reach", "subject": "Ney", "subject_type": "marshal", "place": "Swabia"})
        assert _R13_SWABIA_PAY in said and "'s front" not in said
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Tyrol", 600
        with _r13_quiet():
            result = _r13_executor()._combat._execute_attack(
                world.get_marshal("Ney"), None, world, {"world": world},
                {"action": "attack", "marshal": "Ney"})
        assert "Swabia" in result["message"] and "'s front" not in result["message"]

    def test_the_ais_corps_prints_no_front(self, _r13_boot):
        """Player-only text (Rule 5): the clause answers '' for an AI corps."""
        from backend.commands.movement_executor import front_clause, front_note, front_line
        world = _r13_front_world(_r13_boot)
        ai = world.get_marshal("Kutuzov")
        assert front_line(world, ai, "Swabia") == ""
        assert front_clause(world, ai, "Swabia") == ""
        assert front_note(world, ai, "Swabia") == ""
        ney = world.get_marshal("Ney")
        assert front_clause(world, ney, "Swabia") == " " + _R13_SWABIA_FRONT
        assert front_note(world, ney, "Swabia") == "\n" + _R13_SWABIA_FRONT
        assert front_clause(world, ney, "Lorraine") == ""

    def test_every_pay_site_in_the_owned_files_is_paired_with_a_front_site(self):
        """The census (the sweep rule): a file that prints the campaign pay of a
        step prints the front beside it - a new pay site that forgets the front
        reds here. Counted on the imports each site makes."""
        files = {
            "backend/commands/combat_executor.py": 8,
            "backend/models/world_state.py": 4,
            "backend/commands/naval_executor.py": 2,
            "backend/ai/question_desk.py": 1,
        }
        pattern = re.compile(r"from backend\.commands\.movement_executor import ([^\n(]+)")
        for rel, expected in files.items():
            src = (_R13_REPO / rel).read_text(encoding="utf-8")
            pay = front = 0
            for line in pattern.findall(src):
                for name in [n.strip().split(" as ")[0] for n in line.split(",")]:
                    if name in ("campaign_pay_line", "campaign_pay_note", "campaign_pay_clause"):
                        pay += 1
                    elif name in ("front_line", "front_note", "front_clause"):
                        front += 1
            assert (pay, front) == (expected, expected), (rel, pay, front)


# ══════════════════════════════════════════════════════════════════════════
# S14G-X50 / S14G-X51 - guarded ground on the plain move and the pursuit
# ══════════════════════════════════════════════════════════════════════════

_R13_GUARD_BERLIN = ("Berlin is Prussia's guarded ground (Armed Neutrality) — standing in it "
                     "costs −25 with Prussia.")
_R13_GUARD_ROAD = ("Berlin and Brunswick are Prussia's guarded ground (Armed Neutrality) — "
                   "standing in them costs −25 with Prussia.")


def _r13_set(world, a: str, b: str, state: str) -> None:
    from backend.game_logic.diplomacy import set_diplomatic_state
    with _r13_quiet():
        set_diplomatic_state(world, a, b, state, "test")


def _r13_armed_board(boot):
    """S14G-11's sighting board: Prussia armed-neutral (Hanover, Brunswick and
    Westphalia hers, at peace), Open Borders signed, Soult (literal, one
    province a turn) at Dresden - Berlin one march off."""
    from backend.game_logic.agendas import get_active_agenda
    world = _r13_copy(boot)
    for name in ("Hanover", "Brunswick", "Westphalia"):
        world.regions[name].controller = "Prussia"
    _r13_set(world, "France", "Prussia", "OPEN_BORDERS")
    world.invalidate_active_nations_cache()
    world.invalidate_bloc_members_cache()
    assert get_active_agenda("Prussia", world).id == "armed_neutrality"
    soult = world.get_marshal("Soult")
    assert soult.movement_range == 1
    soult.location = "Dresden"
    with _r13_quiet():
        world.calculate_visibility()
    return world


@contextlib.contextmanager
def _r13_client(world):
    """The player's road: /command on a swapped world (three globals, restored)."""
    with _r13_quiet():
        import backend.main as M
        from backend.commands.parser import CommandParser
        from fastapi.testclient import TestClient
    saved = (M.game_state["world"], M.world, M.parser)
    M.game_state["world"] = world
    M.world = world
    M.parser = CommandParser(use_real_llm=False)
    try:
        yield TestClient(M.app)
    finally:
        M.game_state["world"], M.world, M.parser = saved


def _r13_say(client, text: str) -> dict:
    with _r13_quiet():
        return client.post("/command", json={"command": text}).json()


class TestS14GX50:
    """S14G-11 made a typed `march to` ask before it crosses guarded ground. The
    old reading, on the same board: "Soult, move to Berlin" - the order one verb
    over - walked into Prussia's Armed Neutrality in silence ("Soult moves from
    Dresden to Berlin") and the -25 followed at the turn. The plain move now
    asks first, free, on the same channel, with the same sentence; its answered
    "move" runs as typed and the reply carries the sentence. (The answered mark
    is the option's `_guard_confirmed` flag, merged onto the re-parsed command as
    the strategic ask's is and plumbed by `CommandExecutor._execute_specific`
    into `_execute_move(guard_confirmed=...)`, so the echo and the history line
    keep the player's own words.)"""

    def test_the_plain_move_asks_first_and_spends_nothing(self, _r13_boot):
        world = _r13_armed_board(_r13_boot)
        soult = world.get_marshal("Soult")
        ap = int(world.actions_remaining)
        with _r13_client(world) as client:
            out = _r13_say(client, "Soult, move to Berlin")
        assert out.get("state") == "awaiting_clarification", out.get("message")
        assert out["clarification_kind"] == "march_guard_ask"
        assert out["free_action"] is True and out["marshal"] == "Berthier"
        assert out["interpreted_target"] == "Berlin"
        assert out["message"] == _R13_GUARD_BERLIN.rstrip(".") + " — move or cancel?"
        assert soult.location == "Dresden" and int(world.actions_remaining) == ap
        (move,) = out["options"]
        assert move["label"] == "Move (1 AP)" and move["target"] == "Berlin"
        assert "move" in move["aliases"] and "move anyway" in move["aliases"]
        # the answered option is the player's own words, verbatim, and carries
        # the flag that keeps the move from asking twice
        assert move["command"] == "Soult, move to Berlin"
        assert move["flags"] == {"_guard_confirmed": True}

    def test_move_answers_the_ask_and_the_reply_carries_the_sentence(self, _r13_boot):
        world = _r13_armed_board(_r13_boot)
        soult = world.get_marshal("Soult")
        ap = int(world.actions_remaining)
        with _r13_client(world) as client:
            ask = _r13_say(client, "Soult, move to Berlin")
            assert ask["clarification_kind"] == "march_guard_ask"
            out = _r13_say(client, "move")
        assert out.get("success") is True, out.get("message")
        assert out.get("state") != "awaiting_clarification"      # one question, never two
        assert out["message"].startswith("Soult moves from Dresden to Berlin")
        assert out["message"].endswith("\n" + _R13_GUARD_BERLIN), out["message"]
        assert soult.location == "Berlin" and int(world.actions_remaining) == ap - 1

    def test_the_buttons_own_command_resolves_to_the_move(self, _r13_boot):
        world = _r13_armed_board(_r13_boot)
        soult = world.get_marshal("Soult")
        with _r13_client(world) as client:
            ask = _r13_say(client, "Soult, move to Berlin")
            out = _r13_say(client, ask["options"][0]["command"])
        assert out.get("success") is True and out.get("state") != "awaiting_clarification"
        assert soult.location == "Berlin"
        # the echo keeps the player's own words: no double space anywhere
        assert "  " not in ask["options"][0]["command"]

    def test_cancel_spends_nothing(self, _r13_boot):
        world = _r13_armed_board(_r13_boot)
        soult = world.get_marshal("Soult")
        ap = int(world.actions_remaining)
        with _r13_client(world) as client:
            _r13_say(client, "Soult, move to Berlin")
            _r13_say(client, "cancel")
        assert soult.location == "Dresden" and int(world.actions_remaining) == ap

    def test_the_price_stated_is_the_price_charged(self, _r13_boot):
        from backend.game_logic.agendas import process_agenda_violations
        world = _r13_armed_board(_r13_boot)
        key = world._make_diplo_key("France", "Prussia")
        before = int(world.nation_relations.get(key, 0))
        with _r13_client(world) as client:
            _r13_say(client, "Soult, move to Berlin")
            _r13_say(client, "move")
        with _r13_quiet():
            events = process_agenda_violations(world)
        assert [(e["violator"], e["guard_holder"], e["region"]) for e in events] == [
            ("France", "Prussia", "Berlin")]
        assert int(world.nation_relations.get(key, 0)) == max(-100, before - 25)

    def test_the_far_move_asks_with_the_roads_sentence(self, _r13_boot):
        """`move to Flanders` is the march one verb over (the auto-upgrade): the
        road Dresden -> Berlin -> Brunswick -> Amsterdam -> Flanders crosses two
        guarded provinces - asked first; the answered order's reply carries the
        sentence after its route."""
        world = _r13_armed_board(_r13_boot)
        soult = world.get_marshal("Soult")
        ap = int(world.actions_remaining)
        with _r13_client(world) as client:
            ask = _r13_say(client, "Soult, move to Flanders")
            assert ask["clarification_kind"] == "march_guard_ask"
            assert ask["message"] == _R13_GUARD_ROAD.rstrip(".") + " — move or cancel?"
            assert soult.location == "Dresden" and soult.strategic_order is None
            assert int(world.actions_remaining) == ap
            out = _r13_say(client, "move")
        assert out.get("success") is True, out.get("message")
        assert "Route: Berlin -> Brunswick -> Amsterdam -> Flanders." in out["message"]
        assert out["message"].endswith("\n" + _R13_GUARD_ROAD), out["message"]
        assert soult.strategic_order is not None and soult.strategic_order.target == "Flanders"

    def test_ground_nobody_guards_is_not_asked(self, _r13_boot):
        world = _r13_armed_board(_r13_boot)
        with _r13_client(world) as client:
            out = _r13_say(client, "Soult, move to Bohemia")
        assert out.get("state") != "awaiting_clarification", out.get("message")
        assert out["message"].startswith("Soult moves from Dresden to Bohemia")
        assert "guarded ground" not in out["message"]

    def test_the_trap_map_held_down_is_the_old_silence(self, _r13_boot, monkeypatch):
        """THE SEAM held down (`agendas.guarded_provinces_for` -> {}): the same
        order is today's silent move - no ask, no rider."""
        from backend.game_logic import agendas
        monkeypatch.setattr(agendas, "guarded_provinces_for", lambda *a, **k: {})
        world = _r13_armed_board(_r13_boot)
        with _r13_client(world) as client:
            out = _r13_say(client, "Soult, move to Berlin")
        assert out.get("state") != "awaiting_clarification"
        assert out["message"].startswith("Soult moves from Dresden to Berlin")
        assert "guarded ground" not in out["message"]

    def test_an_order_with_no_typed_line_never_asks_and_still_says_it(self, _r13_boot):
        """The answered objection's road and every internal caller reach the move
        with no typed line: no ask (there is nobody to ask), and the reply's
        rider tells the player what was crossed."""
        world = _r13_armed_board(_r13_boot)
        soult = world.get_marshal("Soult")
        with _r13_quiet():
            result = _r13_executor()._movement._execute_move(
                soult, "Berlin", world, {"world": world})
        assert result["success"] is True and soult.location == "Berlin"
        assert result["message"].endswith("\n" + _R13_GUARD_BERLIN), result["message"]

    def test_the_ais_corps_is_never_asked_or_told(self, _r13_boot):
        from backend.commands.movement_executor import guard_note, move_guard_ask
        world = _r13_armed_board(_r13_boot)
        ai = world.get_marshal("Kutuzov")
        assert guard_note(world, ai, "Berlin", ["Berlin"]) == ""
        assert move_guard_ask(world, ai, "Berlin", ["Berlin"], "Kutuzov, move to Berlin", 1) is None
        # nor a per-hop step of a standing order (its own reply carries the sentence)
        soult = world.get_marshal("Soult")
        assert guard_note(world, soult, "Berlin", ["Berlin"], strategic_execution=True) == ""
        assert guard_note(world, soult, "Berlin", ["Berlin"]) == "\n" + _R13_GUARD_BERLIN

    def test_an_answered_ask_is_never_asked_again(self, _r13_boot):
        """The flag on the command (`_guard_confirmed`) is what `_execute_move`
        reads: with it the same order runs with no ask and carries the rider; the
        executor plumbs it from the command dict, as `_strategic_execution`."""
        world = _r13_armed_board(_r13_boot)
        soult = world.get_marshal("Soult")
        random.seed(7)
        with _r13_quiet():
            result = _r13_executor().execute({"command": {
                "raw_input": "Soult, move to Berlin", "_raw_input": "Soult, move to Berlin",
                "marshal": "Soult", "action": "move",
                "target": "Berlin", "_guard_confirmed": True}}, {"world": world})
        assert result["success"] is True and soult.location == "Berlin"
        assert result.get("state") != "awaiting_clarification"
        assert result["message"].endswith("\n" + _R13_GUARD_BERLIN), result["message"]
        # without the flag the same command asks
        world = _r13_armed_board(_r13_boot)
        with _r13_quiet():
            asked = _r13_executor().execute({"command": {
                "raw_input": "Soult, move to Berlin", "_raw_input": "Soult, move to Berlin",
                "marshal": "Soult", "action": "move",
                "target": "Berlin"}}, {"world": world})
        assert asked.get("clarification_kind") == "march_guard_ask"
        assert world.get_marshal("Soult").location == "Dresden"


class TestS14GX51:
    """S14G-11's reading reaches the pursuit ask (S14G-X51): "Soult, attack
    Kutuzov" with Kutuzov at Amsterdam is out of reach and asks to pursue, and
    the ask printed the detour and pay riders but not the guarded ground its
    road crosses - the pursuit ask is that road's one question (the answered
    order never asks again), so the -25 went unsaid."""

    @staticmethod
    def _board(boot):
        world = _r13_armed_board(boot)
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Amsterdam", 600
        world.update_intel_from_battle("Amsterdam", world.current_turn)
        with _r13_quiet():
            world.calculate_visibility()
        return world

    def test_the_pursuit_ask_names_the_guarded_ground(self, _r13_boot):
        world = self._board(_r13_boot)
        with _r13_client(world) as client:
            out = _r13_say(client, "Soult, attack Kutuzov")
        assert out["clarification_kind"] == "pursuit_ask", out.get("message")
        assert out["message"] == (
            f"Kutuzov stands at Amsterdam, three marches off. {_R13_GUARD_ROAD} "
            "Pursue him (1 AP — a standing order; the first march takes Soult to Berlin, "
            "Prussia's soil), or cancel?")
        assert out["free_action"] is True
        assert world.get_marshal("Soult").location == "Dresden"

    def test_the_answered_pursuit_is_one_question_and_carries_the_sentence(self, _r13_boot):
        world = self._board(_r13_boot)
        soult = world.get_marshal("Soult")
        with _r13_client(world) as client:
            _r13_say(client, "Soult, attack Kutuzov")
            out = _r13_say(client, "pursue")
        assert out.get("success") is True, out.get("message")
        assert out.get("state") != "awaiting_clarification"      # never a second guard ask
        assert _R13_GUARD_ROAD in out["message"]
        assert soult.strategic_order is not None
        assert soult.strategic_order.command_type == "PURSUE"

    def test_a_road_over_unguarded_ground_has_no_such_sentence(self, _r13_boot):
        """The boot board (no Armed Neutrality): the same pursuit's ask carries
        no guarded-ground sentence."""
        world = _r13_copy(_r13_boot)
        world.get_marshal("Soult").location = "Dresden"
        kut = world.get_marshal("Kutuzov")
        kut.location, kut.strength = "Amsterdam", 600
        world.update_intel_from_battle("Amsterdam", world.current_turn)
        with _r13_quiet():
            world.calculate_visibility()
        with _r13_client(world) as client:
            out = _r13_say(client, "Soult, attack Kutuzov")
        message = out.get("message") or ""
        assert "guarded ground" not in message, message


# ══════════════════════════════════════════════════════════════════════════
# row14
# ══════════════════════════════════════════════════════════════════════════
# Pre-Deploy S14h part 1 — the six wave-2 siblings of row 14 (October 26, 2026).
#
# Six sibling rows of S14G (DD-B's third measure), each the same defect class the
# slice is named for: a consequence stated in ONE place while the player decides
# in ANOTHER. Each is its own test class (`TestS14GX<row>_<k>`, placeholder ids the
# orchestrator renumbers at the merge); helpers are prefixed `_r14_`.
#
# S14G-X42 - the counsel's "Buy Off Their Design - keeps Prussia out of the next
# league: buying off her design (N gold) is enough alone" said it was enough and
# not WHY (`coalition.league_cheapest_keep_out`'s clause literal). The design's
# sleep is not what keeps her out of a league - the +5 relations that lift her
# past the -10 line are (S14G-9 / S14G-D6). The clause is built from the ONE
# builder `league_price_clause` calls (`instruments.buyoff_league_clause`).
#
# S14G-X46 - the AI downgrade's two lines (`ai_diplomacy` turn line,
# `campaign_log` one-liner) kept the SUBJECTLESS clause ("relations with every
# court, France's included, fall 5"); S14G-10 gave the declaration beat a subject.
# Both now pass `aggressor=` the court that downgrades, which is `nation_a`
# (`diplomacy.execute_downgrade`'s ACTOR): "Prussia's relations with every court,
# France's included, fall 5". Text only - the figure and every relation write are
# untouched (pinned: the world is byte-identical with the clause's subject
# patched away).
#
# S14G-X34 - the counsel "Shore up Spain" (`diplomatic_advisory` rung 2) was an
# `open_proposal`: it landed on the generic proposal menu for a court we ALREADY
# ALLY with, where "Propose alliance" and "Non-aggression pact" are shut ("We
# already have Alliance with Spain...") and only Vassalage - of our own ally -
# stands open: a counsel that led to a menu of shut doors. The instrument that
# shores up an ally exists: the Cabinet's mission to her court (Reassure Ally in
# a full alliance, Improve Relations in a defensive one), read from the ONE lever
# `diplomacy.slide_lever` (the gates the Cabinet's mission rows read). The counsel
# is now that mission, its price in the tooltip; when the lever is shut it says
# what stands in the way and offers no door.
#
# S14G-X35 - `player_proposal_cooldowns` was read only at the typed entry
# (`_execute_diplomatic_proposal`), never at the confirm's send
# (`_choice_proposal`): a counsel or menu road to a court that refused us last turn
# reached the confirm and the envoy departed (its DP spent) to a court that would not
# receive him. The predicate is lifted into `proposal_cooldown_refusal`; the typed
# entry and the confirm's send both read it, the same words, refused free.
#
# S14G-X24 - the mailbox rows carry `locks_cabinet` (from `item_locks_cabinet`,
# the one predicate S14G-6 built) and `mailbox_panel.gd` marks the locking rows -
# the letter's popup, the Not Now button, the Cabinet button and the Envoys badge
# said whether a letter shuts the Cabinet, and the mailbox, where the player picks
# which letter to open, did not.
#
# S14G-X25 - the Vassals tab's notice "Envoys await your reply - vassal
# instruments are suspended until the matter is answered" named no court and said
# "envoys" even when a hard-stop dialogue was the whole cause. `_build_vassals`
# now sends the cause (`blocked_by`: "letter" with the printed courts, or
# "dialogue" with its player-facing name) and the notice names it.

_R14_ROOT = Path(__file__).resolve().parents[1]
_R14_SCRIPTS = _R14_ROOT / "godot-client" / "project-sovereign" / "scripts"
_R14_SCENARIO = (_R14_ROOT / "godot-client" / "project-sovereign" / "assets" / "maps"
                 / "europe_1805.json")


def _r14_quiet():
    return contextlib.redirect_stdout(io.StringIO())


@pytest.fixture(scope="module")
def _r14_boot():
    from backend.models.world_state import WorldState
    with _r14_quiet():
        return WorldState.from_scenario(str(_R14_SCENARIO))


def _r14_copy(boot):
    from backend.models.world_state import WorldState
    with _r14_quiet():
        return WorldState.from_dict(json.loads(json.dumps(boot.to_dict(), default=str)))


@pytest.fixture
def _r14_world(_r14_boot):
    """The shipped 1805 board, a private copy per test."""
    return _r14_copy(_r14_boot)


def _r14_executor():
    from backend.commands.executor import CommandExecutor
    with _r14_quiet():
        return CommandExecutor()


def _r14_src(name: str) -> str:
    return (_R14_SCRIPTS / name).read_text(encoding="utf-8")


def _r14_func(src: str, name: str) -> str:
    """A GDScript function's body: from its header to the next top-level one."""
    start = src.index(f"func {name}(")
    ends = [e for e in (src.find("\nfunc ", start + 1), src.find("\nstatic func ", start + 1))
            if e != -1]
    return src[start:min(ends) if ends else len(src)]


def _r14_rel(w, a, b):
    return int(w.nation_relations.get(w._make_diplo_key(a, b), 0) or 0)


# ══════════════════════════════════════════════════════════════════════════
# S14G-X42 — the league counsel says WHY the buy-off is enough
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def _r14_peace(_r14_world):
    """The shipped board at turn 20: France at peace with every court, the
    three great powers at -50 (they QUALIFY below -10), Prussia at -13 (three
    under the bar: the +5 lifts her past it), the chest full."""
    w = _r14_world
    w.current_turn = 20
    w.active_coalition = None
    w.coalition_brewing = None
    w.coalition_cooldown = 0
    for nation in w.get_active_nations():
        if nation == "France":
            continue
        key = w._make_diplo_key("France", nation)
        if w.diplomatic_states.get(key) == "WAR":
            w.diplomatic_states[key] = "PEACE"
        if nation in ("Austria", "Britain", "Russia"):
            w.nation_relations[key] = -50
    w.nation_relations[w._make_diplo_key("France", "Prussia")] = -13
    w.invalidate_active_nations_cache()
    w.invalidate_bloc_members_cache()
    w.threat_by_target["France"] = 45
    w.threat_sources_this_turn = []
    w.pending_dispatch_events = []
    w.event_log = []
    w.nation_gold["France"] = 99999
    w.diplomatic_points = 5
    for m in w.marshals.values():
        m.last_battle_turn = 9
    return w


class TestS14GX42:
    """The sighting (DD-B diplomacy, the realm's league counsel at peace): "F1 ->
    Prussia -> Buy Off Their Design - keeps Prussia out of the next league:
    buying off her design (N gold) is enough alone". OLD READING: the clause
    ended at "enough alone" - the player read the design's sleep as the thing
    that keeps her out; it is the +5 relations past the -10 line."""

    def test_the_counsel_names_why_it_is_enough(self, _r14_peace):
        from backend.ai.counsel import league_counsel
        from backend.game_logic import coalition as C
        from backend.game_logic.instruments import buyoff_league_clause
        w = _r14_peace
        row = [r for r in C.league_forecast(w)["courts"] if r["nation"] == "Prussia"][0]
        (line,) = league_counsel(w, "France")
        price = int(row["buyoff"])
        assert line == (
            "F1 → Prussia → Buy Off Their Design — keeps Prussia out of the next league: "
            f"buying off her design ({price:,} gold) is enough alone "
            f"({buyoff_league_clause(-13)})"), line
        assert "+5 relations lifts her from −13 to −8, past the −10 line" in line
        assert int(row["relation"]) == -13

    def test_the_old_prefix_the_page_pins_survives(self, _r14_peace):
        """`test_at_peace_what_can_i_do_names_the_cheapest` asserts only the
        prefix through "buying off her design (" - it holds."""
        from backend.ai.counsel import league_counsel
        (line,) = league_counsel(_r14_peace, "France")
        assert line.startswith(
            "F1 → Prussia → Buy Off Their Design — keeps Prussia out of the next "
            "league: buying off her design (")

    def test_every_surface_of_the_pick_carries_the_sentence(self, _r14_peace):
        """The counsel's clause, the order text the desk prints and the one the
        league row prints (`league_price_clause`) are one sentence."""
        from backend.game_logic import coalition as C
        w = _r14_peace
        pick = C.league_cheapest_keep_out(w)
        assert pick["nation"] == "Prussia"
        sentence = "+5 relations lifts her from −13 to −8, past the −10 line"
        assert sentence in pick["clause"]
        assert sentence in pick["order_text"]
        assert sentence in pick["text"]          # the dispatch's realm line (`league_price_clause`)
        row = [r for r in C.league_forecast(w)["courts"] if r["nation"] == "Prussia"][0]
        assert sentence in C.league_price_clause(w, row)

    def test_the_road_when_the_buyoff_is_not_enough_is_untouched(self, _r14_peace):
        """With no gold the cheapest keep-out is Talleyrand's road - its clause
        is not a buy-off clause and is unchanged."""
        from backend.ai.counsel import league_counsel
        w = _r14_peace
        w.nation_gold["France"] = 0
        (line,) = league_counsel(w, "France")
        assert line == ("F1 → Prussia → Improve Relations — keeps Prussia out of the next "
                        "league: Talleyrand brings her to −10 in 1 turn (1 DP)")


# ══════════════════════════════════════════════════════════════════════════
# S14G-X46 — the AI downgrade's clause has a subject
# ══════════════════════════════════════════════════════════════════════════

_R14_CLAUSE = "relations with every court, France's included, fall 5"


def _r14_stage_downgrade(w, state="ALLIANCE", a="Prussia", b="Sweden", relation=20):
    """Two AI courts under a treaty, the stronger twice the weaker (Prussia
    78,000 against Sweden 12,000), relation < 30, neither at war with France:
    the pair Trigger 2 of `_process_ai_ai_rivalry` fires on."""
    key = w._make_diplo_key(a, b)
    w.diplomatic_states[key] = state
    w.nation_relations[key] = int(relation)
    w.active_treaties = {key: {"type": state.lower(), "nations": [a, b]}}
    w.invalidate_bloc_members_cache()
    return key


def _r14_run_rivalry(w):
    from backend.game_logic import ai_diplomacy as AD
    with _r14_quiet():
        return AD._process_ai_ai_rivalry(w)


class TestS14GX46:
    """The sighting: S14G-10's sentence ("Prussia's relations with every court,
    France's included, fall 15") on the declaration beat, while the AI's
    downgrade line beside it still read "- relations with every court, France's
    included, fall 5." with nobody in it. The two lines now name the court that
    downgrades."""

    def test_the_turn_line_names_the_downgrading_court(self, _r14_world):
        w = _r14_world
        _r14_stage_downgrade(w)
        events = [e for e in _r14_run_rivalry(w) if e.get("type") == "ai_ai_downgrade"]
        (event,) = events
        assert event["message"] == (
            "Prussia has downgraded relations with Sweden: Alliance → Defensive Alliance "
            f"— Prussia's {_R14_CLAUSE}.")
        assert event["relation_cost"] == 5 and isinstance(event["relation_cost"], int)

    def test_the_campaign_log_line_names_the_actor(self, _r14_world):
        from backend.campaign_log import format_event_oneliner
        w = _r14_world
        _r14_stage_downgrade(w)
        _r14_run_rivalry(w)
        logged = [e for e in w.event_log if e.get("type") == "diplomatic_downgrade"][-1]
        assert logged["nation_a"] == "Prussia"        # the ACTOR (`execute_downgrade`)
        line = format_event_oneliner(logged, "France", w)
        assert line == ("Relations downgraded: Prussia–Sweden "
                        f"(Alliance → Defensive Alliance) — Prussia's {_R14_CLAUSE}")

    def test_the_subject_is_the_actor_whoever_it_is(self):
        """Hand events: the clause's subject is `nation_a`, not a fixed court."""
        from backend.campaign_log import format_event_oneliner
        base = {"type": "diplomatic_downgrade", "nation_b": "Prussia",
                "from_state": "ALLIANCE", "to_state": "DEFENSIVE_ALLIANCE",
                "relation_cost": 5, "player": "France", "turn": 4}
        austria = format_event_oneliner({**base, "nation_a": "Austria"}, "France")
        russia = format_event_oneliner({**base, "nation_a": "Russia"}, "France")
        assert austria.endswith(f"— Austria's {_R14_CLAUSE}"), austria
        assert russia.endswith(f"— Russia's {_R14_CLAUSE}"), russia

    def test_a_cost_free_step_names_nothing(self, _r14_world):
        """The two lower steps cost France nothing: no clause, so no subject."""
        w = _r14_world
        _r14_stage_downgrade(w, "NON_AGGRESSION")
        (event,) = [e for e in _r14_run_rivalry(w) if e.get("type") == "ai_ai_downgrade"]
        assert event["relation_cost"] == 0
        assert "relations with every court" not in event["message"]

    def test_the_subjectless_form_survives_for_a_caller_with_no_aggressor(self):
        from backend.game_logic.diplomacy import declaration_cost_clause
        assert declaration_cost_clause(5, "France") == _R14_CLAUSE
        assert declaration_cost_clause(5, "France", aggressor="Prussia") == f"Prussia's {_R14_CLAUSE}"

    def test_text_only_the_world_is_byte_identical_without_the_subject(self, _r14_boot, monkeypatch):
        """No seam is needed: patch the clause back to the subjectless form and
        the run moves every relation, state and alarm exactly as before."""
        from backend.game_logic import diplomacy as D
        real = D.declaration_cost_clause
        a, b = _r14_copy(_r14_boot), _r14_copy(_r14_boot)
        _r14_stage_downgrade(a)
        _r14_stage_downgrade(b)
        _r14_run_rivalry(a)
        monkeypatch.setattr(D, "declaration_cost_clause",
                            lambda cost, player="France", aggressor=None: real(cost, player))
        _r14_run_rivalry(b)
        for field in ("nation_relations", "diplomatic_states", "threat_by_target", "active_treaties"):
            assert getattr(a, field) == getattr(b, field), field


# ══════════════════════════════════════════════════════════════════════════
# S14G-X34 — "Shore up <ally>" is the Cabinet's mission, never a menu of shut doors
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def _r14_war_room(_r14_world, monkeypatch):
    """The war room with rung 2's inputs: the coalition bearing down
    ("aggressive", threat 70) and France with no war the settlement rungs would
    read first (the real rung 2, called with no war rows)."""
    from backend.game_logic import diplomatic_advisory as ADV
    real = ADV._build_situation_recommendation
    monkeypatch.setattr(
        ADV, "_build_situation_recommendation",
        lambda world, player, war_rows, coalition_info, posture:
        real(world, player, [], coalition_info, "aggressive"))
    w = _r14_world
    w.threat_level = 70
    w.diplomatic_points = 5
    return w


def _r14_advice(world):
    from backend.game_logic.diplomatic_advisory import generate_advisory
    with _r14_quiet():
        advice = generate_advisory(None, "assess_situation", world)
    world.dialogue_manager.replace(advice)
    return advice


def _r14_click(world, executor, index):
    with _r14_quiet():
        return executor.handle_diplomatic_dialogue_response(index, {"world": world})


def _r14_rec(world):
    from backend.game_logic import diplomatic_advisory as ADV
    with _r14_quiet():
        return ADV._build_situation_recommendation(world, "France", [], None, "aggressive")


class TestS14GX34:
    """The sighting: the war room's rung 2 counsel "Shore up Spain" (the weakest
    ally, a full ALLIANCE) was an `open_proposal` and landed on the T5 "views us
    favorably" menu where "Propose alliance" and "Non-aggression pact" are shut
    ("We already have Alliance with Spain.") and only "Vassalage" of our own ally
    is open. NOW the counsel is the Reassure Ally mission to her court."""

    def test_the_old_counsels_menu_was_a_menu_of_shut_doors(self, _r14_war_room):
        """Documents the OLD road: `expand_options` at Spain lands on a menu
        whose two proposal rows are shut."""
        w = _r14_war_room
        w.dialogue_manager.replace({
            "type": "advisory", "target_nation": "", "talleyrand_text": "x",
            "options": [{"label": "Shore up Spain", "description": "d", "action": "expand_options",
                         "terms": {"target_nation": "Spain"}},
                        {"label": "Thank you", "description": "d", "action": "dismiss"}],
            "context": {}, "turn_created": 1, "blocking": False})
        menu = _r14_click(w, _r14_executor(), 1)["diplomatic_dialogue"]
        shut = [o["label"] for o in menu["options"]
                if o["action"] == "execute_proposal" and o.get("available") is False]
        assert shut == ["Propose alliance", "Non-aggression pact"], shut

    def test_the_counsel_is_the_reassure_mission_with_its_price(self, _r14_war_room):
        w = _r14_war_room
        assert w.get_diplomatic_state("France", "Spain") == "ALLIANCE"
        rec = _r14_rec(w)
        assert rec["kind"] == "start_mission"
        assert rec["mission_type"] == "REASSURE_ALLY" and rec["target_nation"] == "Spain"
        assert rec["label"] == "Reassure Ally (Spain)"
        assert rec["description"] == ("Send Talleyrand to Spain: +4 relations a turn for "
                                      "1 DP a turn (you have 5 DP).")
        assert rec["text"] == ("the coalition means to fight — steady Spain, our least certain "
                               "friend, before they test him. Reassure Ally: +4 relations a turn "
                               "for 1 DP a turn.")

    def test_the_price_is_the_applied_one(self, _r14_war_room):
        """Shown == applied: the figure is the tick's own (`mission_effect_magnitude`,
        skill scaling included) and the cost the mission table's."""
        from backend.game_logic.diplomatic_dialogue import MISSION_DP_COSTS, mission_effect_magnitude
        w = _r14_war_room
        rec = _r14_rec(w)
        gain = mission_effect_magnitude(w, "REASSURE_ALLY", "relation_change")
        assert f"{gain:+d} relations a turn for {MISSION_DP_COSTS['REASSURE_ALLY']} DP a turn" in rec["description"]

    def test_the_option_starts_the_mission_through_the_cabinets_own_stage(self, _r14_war_room):
        w = _r14_war_room
        advice = _r14_advice(w)
        first = advice["options"][0]
        assert first["action"] == "start_mission"
        assert first["terms"] == {"mission_type": "REASSURE_ALLY", "target_nation": "Spain"}
        assert [o["action"] for o in advice["options"]] == ["start_mission", "dismiss"]
        assert advice["context"]["action_hints"] == ["Reassure Ally (Spain)"]
        dp_before = int(w.diplomatic_points)
        result = _r14_click(w, _r14_executor(), 1)
        assert result["success"] is True
        assert result["message"] == "Talleyrand begins efforts to reassure Spain. (1 DP/turn)"
        mission = w.active_diplomatic_mission
        assert mission["type"] == "REASSURE_ALLY" and mission["target"] == "Spain"
        assert mission["started_state"] == "ALLIANCE"
        assert w.talleyrand_state == "ON_MISSION"
        assert int(w.diplomatic_points) == dp_before        # the mission bills per turn, at the tick

    def test_a_defensive_ally_is_improved_not_reassured(self, _r14_war_room):
        """The Cabinet's own rows: Reassure Ally is a full alliance's; a defensive
        alliance is improved (`MISSION_ROWS_BY_STATE`)."""
        w = _r14_war_room
        w.diplomatic_states[w._make_diplo_key("France", "Spain")] = "DEFENSIVE_ALLIANCE"
        rec = _r14_rec(w)
        assert rec["kind"] == "start_mission" and rec["mission_type"] == "IMPROVE_RELATIONS"
        assert rec["label"] == "Improve Relations (Spain)"
        _r14_advice(w)
        result = _r14_click(w, _r14_executor(), 1)
        assert result["success"] is True
        assert w.active_diplomatic_mission["type"] == "IMPROVE_RELATIONS"

    @pytest.mark.parametrize("setup,needle", [
        ("busy", "recall Talleyrand from Austria first"),
        ("dp", "needs 1 DP, and you have 0"),
        ("here", "Talleyrand is already at Spain's court"),
        ("transit", "opens when Talleyrand is home"),
    ])
    def test_a_shut_lever_says_what_stands_in_the_way_and_offers_no_door(self, _r14_war_room, setup, needle):
        w = _r14_war_room
        if setup == "busy":
            w.active_diplomatic_mission = {"type": "GATHER_INTEL", "target": "Austria",
                                           "turns_active": 0, "paused": False}
            w.talleyrand_state = "ON_MISSION"
        elif setup == "dp":
            w.diplomatic_points = 0
        elif setup == "here":
            w.active_diplomatic_mission = {"type": "REASSURE_ALLY", "target": "Spain",
                                           "turns_active": 1, "paused": False}
            w.talleyrand_state = "ON_MISSION"
        else:
            w.talleyrand_state = "IN_TRANSIT"
        rec = _r14_rec(w)
        assert rec["kind"] == "counsel_only" and rec["label"] == ""
        assert needle in rec["text"], rec["text"]
        assert rec["text"].startswith("the coalition means to fight — steady Spain")
        advice = _r14_advice(w)
        assert [o["action"] for o in advice["options"]] == ["dismiss"]
        assert advice["context"]["action_hints"] == []
        assert "My counsel, Sire: the coalition means to fight — steady Spain" in advice["talleyrand_text"]

    @pytest.mark.parametrize("setup", ["open", "busy", "dp", "transit"])
    def test_the_counsels_door_is_open_exactly_when_the_cabinets_row_is(self, _r14_war_room, setup):
        """The counsel can never offer a mission the Cabinet's row would refuse."""
        from backend.game_logic.diplomacy import get_available_diplomatic_actions
        w = _r14_war_room
        if setup == "busy":
            w.active_diplomatic_mission = {"type": "GATHER_INTEL", "target": "Austria",
                                           "turns_active": 0, "paused": False}
        elif setup == "dp":
            w.diplomatic_points = 0
        elif setup == "transit":
            w.talleyrand_state = "IN_TRANSIT"
        with _r14_quiet():
            rows = get_available_diplomatic_actions(w, "Spain")
        row = [r for r in rows if r["action"] == "mission_reassure"][0]
        assert (_r14_rec(w)["kind"] == "start_mission") is bool(row["available"]), setup

    def test_the_other_open_proposal_counsels_are_untouched(self, _r14_world):
        """With no ally the rung still courts the coalition's weak link."""
        from backend.game_logic import diplomatic_advisory as ADV
        w = _r14_world
        w.threat_level = 70
        for key in list(w.diplomatic_states):
            if w.diplomatic_states[key] in ("ALLIANCE", "DEFENSIVE_ALLIANCE") and "France" in key.split("|"):
                w.diplomatic_states[key] = "PEACE"
        with _r14_quiet():
            rec = ADV._build_situation_recommendation(w, "France", [], {"weak_link": "Russia"}, "aggressive")
        assert rec["kind"] == "open_proposal" and rec["label"] == "Court Russia"


# ══════════════════════════════════════════════════════════════════════════
# S14G-X35 — the confirm's send reads the proposal cooldown
# ══════════════════════════════════════════════════════════════════════════

_R14_PATIENCE = ("Talleyrand advises patience, Sire. Prussia refused us; the court will "
                 "not receive another envoy for 2 more turns.")


def _r14_counsel_to_confirm(world, executor, target="Prussia"):
    """Counsel -> generic menu -> the confirm: the road that never passes the
    typed entry (`expand_options` re-routes as a vague proposal)."""
    world.dialogue_manager.replace({
        "type": "advisory", "target_nation": "", "talleyrand_text": "x",
        "options": [{"label": f"Approach {target}", "description": "d", "action": "expand_options",
                     "terms": {"target_nation": target}},
                    {"label": "Thank you", "description": "d", "action": "dismiss"}],
        "context": {}, "turn_created": 1, "blocking": False})
    menu = _r14_click(world, executor, 1)["diplomatic_dialogue"]
    assert menu["type"] == "proposal_options"
    send = [n for n, o in enumerate(menu["options"], 1)
            if o["action"] == "execute_proposal" and o.get("available", True) is not False][0]
    confirm = _r14_click(world, executor, send)["diplomatic_dialogue"]
    assert confirm["type"] == "proposal_confirm"
    return confirm


def _r14_send_index(confirm):
    return [n for n, o in enumerate(confirm["options"], 1) if o["action"] == "execute_proposal"][0]


def _r14_typed(world, executor, target, ptype):
    data = {"action": "diplomatic_proposal", "diplomat": "Talleyrand", "target_nation": target,
            "proposal_type": ptype, "clauses": [], "is_question": False,
            "has_diplomatic_keywords": True, "tone": "propose",
            "raw_text": f"propose {ptype} to {target}"}
    with _r14_quiet():
        return executor._execute_diplomatic_proposal(data, world)


@pytest.fixture
def _r14_tense(_r14_world):
    """Prussia at -10 (the T4 tense menu: Propose open borders), Talleyrand's
    defiance cooled so the control send is deterministic."""
    w = _r14_world
    w.nation_relations[w._make_diplo_key("France", "Prussia")] = -10
    w.talleyrand_defiance_cooldown = 99
    w.diplomatic_points = 5
    return w


class TestS14GX35:
    """The sighting: a court that refused us last turn is reached by a counsel
    or a menu road ("Approach Prussia" -> the menu -> Send as suggested). OLD
    READING: the confirm's send never asked `player_proposal_cooldowns`, the
    envoy departed and its DP were spent; only the typed entry refused. NOW the
    confirm's send refuses, free, in the typed entry's words."""

    def test_the_confirms_send_refuses_a_court_on_cooldown(self, _r14_tense):
        w = _r14_tense
        ex = _r14_executor()
        confirm = _r14_counsel_to_confirm(w, ex)
        w.player_proposal_cooldowns["Prussia"] = 2          # she refused us a turn ago
        dp_before = int(w.diplomatic_points)
        result = _r14_click(w, ex, _r14_send_index(confirm))
        assert result["success"] is False
        assert result["message"] == _R14_PATIENCE
        assert int(w.diplomatic_points) == dp_before        # refused free
        assert w.proposal_in_transit is None
        assert w.talleyrand_state != "IN_TRANSIT"
        assert result["diplomatic_dialogue"]["type"] == "proposal_confirm"      # the confirm stands

    def test_the_words_are_the_typed_entrys(self, _r14_tense):
        w = _r14_tense
        ex = _r14_executor()
        confirm = _r14_counsel_to_confirm(w, ex)
        w.player_proposal_cooldowns["Prussia"] = 2
        typed = _r14_typed(w, ex, "Prussia", "open_borders")
        sent = _r14_click(w, ex, _r14_send_index(confirm))
        assert typed["success"] is False and typed["message"] == sent["message"] == _R14_PATIENCE

    def test_the_per_type_cooldown_is_read_too(self, _r14_tense):
        w = _r14_tense
        ex = _r14_executor()
        confirm = _r14_counsel_to_confirm(w, ex)
        w.player_proposal_cooldowns["Prussia_open_borders"] = 3
        typed = _r14_typed(w, ex, "Prussia", "open_borders")
        sent = _r14_click(w, ex, _r14_send_index(confirm))
        assert sent["success"] is False
        assert sent["message"] == typed["message"]
        assert "she will not hear it again for 3 more turns" in sent["message"]
        assert w.proposal_in_transit is None

    def test_a_court_off_cooldown_still_receives_the_envoy(self, _r14_tense):
        """The control: the same road with no cooldown sends (and spends)."""
        w = _r14_tense
        ex = _r14_executor()
        confirm = _r14_counsel_to_confirm(w, ex)
        dp_before = int(w.diplomatic_points)
        result = _r14_click(w, ex, _r14_send_index(confirm))
        assert result["success"] is True and "Talleyrand departs" in result["message"]
        assert w.proposal_in_transit is not None and w.proposal_in_transit["target"] == "Prussia"
        assert int(w.diplomatic_points) < dp_before

    def test_a_cooldown_of_zero_is_no_cooldown(self, _r14_world):
        from backend.commands.diplomatic_executor import proposal_cooldown_refusal
        w = _r14_world
        w.player_proposal_cooldowns["Prussia"] = 0
        w.player_proposal_cooldowns["Prussia_peace"] = 0
        assert proposal_cooldown_refusal(w, "Prussia", "peace") is None
        assert proposal_cooldown_refusal(w, "Prussia", None) is None
        assert proposal_cooldown_refusal(w, "", "peace") is None

    def test_the_one_predicate_is_read_by_the_typed_entry_and_the_confirm(self):
        """Both roads read `proposal_cooldown_refusal`; neither keeps the inline copy
        (S14G-X38 adds the override send as a third reader)."""
        import ast
        src = (_R14_ROOT / "backend" / "commands" / "diplomatic_executor.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        readers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                body = ast.get_source_segment(src, node) or ""
                if "proposal_cooldown_refusal(" in body and node.name != "proposal_cooldown_refusal":
                    readers.append(node.name)
        assert {"_choice_proposal", "_execute_diplomatic_proposal"} <= set(readers), readers
        # the reads of the slot live in the helper alone
        direct = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and "player_proposal_cooldowns" in (ast.get_source_segment(src, n) or "")
                  and n.name not in ("proposal_cooldown_refusal",)]
        assert not [d for d in direct if d in ("_choice_proposal", "_execute_diplomatic_proposal")], direct


# ══════════════════════════════════════════════════════════════════════════
# S14G-X24 — the mailbox rows carry the lock
# ══════════════════════════════════════════════════════════════════════════

def _r14_letter(world, court, ptype="open_borders"):
    """A court's letter built by the REAL builder and pushed on the dialogue
    manager (what the transport does), without the delivery gates."""
    from backend.game_logic.ai_diplomacy import _make_proposal, build_ai_proposal_dialogue
    terms = {"type": ptype, "proposer_nation": court, "target_nation": "France",
             "demands": [], "sweeteners": [], "clauses": []}
    with _r14_quiet():
        dialogue = build_ai_proposal_dialogue(_make_proposal(court, ptype, 5, terms, world), world)
        world.dialogue_manager.push(dialogue)
    return dialogue


def _r14_ultimatum(world, court):
    from backend.game_logic.ai_diplomacy import _build_ai_ultimatum_dialogue, _make_proposal
    terms = {"type": "ultimatum_demand", "proposer_nation": court, "target_nation": "France",
             "demands": [{"type": "gold_lump", "value": 300}], "sweeteners": [], "clauses": []}
    with _r14_quiet():
        dialogue = _build_ai_ultimatum_dialogue(_make_proposal(court, "ultimatum", 7, terms, world), world)
        world.dialogue_manager.push(dialogue)
    return dialogue


def _r14_rows(world):
    return {r["source_nation"]: r for r in world.dialogue_manager.get_mailbox_items(world)}


class TestS14GX24:
    """The sighting (S14G-6's sweep): the letter's popup, its Not Now button, the
    Cabinet button and the Envoys badge said whether a letter shuts the Cabinet;
    the mailbox row - where the player chooses which letter to open - did not.
    OLD READING: the row's keys stopped at `reason`; a Portuguese courtesy and
    Austria's armistice looked alike."""

    def test_a_row_says_whether_its_letter_locks(self, _r14_world):
        w = _r14_world
        _r14_letter(w, "Portugal", "open_borders")
        _r14_letter(w, "Austria", "armistice")
        rows = _r14_rows(w)
        assert rows["Portugal"]["locks_cabinet"] is False
        assert rows["Austria"]["locks_cabinet"] is True

    def test_an_ultimatum_locks_whoever_sends_it(self, _r14_world):
        w = _r14_world
        _r14_ultimatum(w, "Portugal")
        assert _r14_rows(w)["Portugal"]["locks_cabinet"] is True

    def test_the_row_reads_the_one_predicate(self, _r14_world, monkeypatch):
        """The row can never disagree with the lock: the seam patched to its
        "down" reading (every current-turn offer locks) turns the courtesy's row
        - and the lock itself - on together."""
        from backend.models.dialogue_manager import DialogueManager
        w = _r14_world
        _r14_letter(w, "Portugal", "open_borders")
        dm = w.dialogue_manager
        assert dm.has_current_turn_offers() is False
        assert _r14_rows(w)["Portugal"]["locks_cabinet"] is False
        monkeypatch.setattr(DialogueManager, "letter_locks_cabinet", lambda self, item: True)
        assert dm.has_current_turn_offers() is True
        assert _r14_rows(w)["Portugal"]["locks_cabinet"] is True

    def test_every_row_carries_a_bool_and_a_non_offer_never_locks(self, _r14_world):
        """The key rides EVERY row (an older client tolerates its absence); a
        row that is not a current-turn offer says False."""
        w = _r14_world
        _r14_letter(w, "Austria", "armistice")
        w.dialogue_manager.push({"type": "ally_settlement_petition", "ally_nation": "Spain",
                                 "petition_type": "ally_petition", "war_id": "w1",
                                 "summary_text": "Spain asks", "context": {}, "turn_created": 3})
        rows = w.dialogue_manager.get_mailbox_items(w)
        assert len(rows) == 2
        assert all(type(r["locks_cabinet"]) is bool for r in rows)
        petition = [r for r in rows if r["item_type"] == "ally_settlement_petition"][0]
        assert petition["locks_cabinet"] is False

    def test_the_wire_carries_it(self, _r14_world):
        """`GET /mailbox` hands the rows through untouched."""
        import backend.main as M
        from backend.commands.parser import CommandParser
        from fastapi.testclient import TestClient
        w = _r14_world
        _r14_letter(w, "Austria", "armistice")
        saved = (M.game_state["world"], M.world, M.parser)
        M.game_state["world"] = w
        M.world = w
        M.parser = CommandParser(use_real_llm=False)
        try:
            with _r14_quiet():
                body = TestClient(M.app).get("/mailbox").json()
        finally:
            M.game_state["world"], M.world, M.parser = saved
        assert [r["locks_cabinet"] for r in body["items"]] == [True]

    def test_the_panel_marks_a_locking_row_in_the_one_sentence(self):
        src = _r14_src("mailbox_panel.gd")
        row = _r14_func(src, "_build_item_row")
        assert 'bool(item.get("locks_cabinet", false))' in row
        assert 'lock_label.text = "Shuts the Cabinet"' in row
        # the tooltip is the lock's ONE sentence, never a second wording
        assert "lock_label.tooltip_text = Utils.cabinet_shut_sentence()" in row
        assert "Utils.UI_WARNING" in row
        # the tooltip must show AND the click must still open the row
        assert "lock_label.mouse_filter = Control.MOUSE_FILTER_PASS" in row
        # it sits in the top row, after the type label and before the Open button
        assert (row.index("top_row.add_child(type_label)")
                < row.index("top_row.add_child(lock_label)")
                < row.index("var open_btn = Button.new()"))

    def test_the_gdscript_added_is_tab_indented(self):
        row = _r14_func(_r14_src("mailbox_panel.gd"), "_build_item_row")
        start = row.index("# S14G-X24")
        block = row[start:row.index("# S14E-27 (S14f part 2): the word is the press.")]
        for line in block.splitlines():
            assert not line.startswith(" "), repr(line)


# ══════════════════════════════════════════════════════════════════════════
# S14G-X25 — the Vassals tab's notice names what suspends it
# ══════════════════════════════════════════════════════════════════════════

def _r14_vassals(world):
    from backend.game_logic.diplomatic_ledger import _build_vassals
    with _r14_quiet():
        return _build_vassals(world)


class TestS14GX25:
    """The sighting: the Vassals tab said "Envoys await your reply - vassal
    instruments are suspended until the matter is answered" - no court in it,
    and "envoys" even when the cause was a hard-stop dialogue (the terms being
    drafted, a war purpose yet to be declared), not a letter. NOW the payload
    sends the cause and the notice names it."""

    def test_a_quiet_board_blocks_nothing(self, _r14_world):
        out = _r14_vassals(_r14_world)
        assert out["actions_blocked"] is False
        assert out["blocked_by"] == "" and out["blocked_by_courts"] == [] and out["blocked_by_dialogue"] == ""

    def test_a_great_courts_letter_is_named(self, _r14_world):
        w = _r14_world
        _r14_letter(w, "Austria", "armistice")
        out = _r14_vassals(w)
        assert out["actions_blocked"] is True
        assert out["blocked_by"] == "letter"
        assert out["blocked_by_courts"] == ["Austria"]
        assert out["blocked_by_dialogue"] == ""

    def test_the_names_are_the_wires_cabinet_locked_by(self, _r14_world):
        """One naming rule: the ledger's courts are `main._cabinet_locked_by`'s
        (the printed form - "the Ottoman Empire" - once each)."""
        import backend.main as M
        w = _r14_world
        _r14_letter(w, "Austria", "armistice")
        _r14_letter(w, "Russia", "armistice")
        assert _r14_vassals(w)["blocked_by_courts"] == M._cabinet_locked_by(w) == ["Austria", "Russia"]

    def test_a_lesser_courts_courtesy_blocks_nothing(self, _r14_world):
        w = _r14_world
        _r14_letter(w, "Portugal", "open_borders")
        out = _r14_vassals(w)
        assert out["actions_blocked"] is False and out["blocked_by"] == ""

    @pytest.mark.parametrize("dtype,name", [
        ("terms_guidance", "the terms you are drafting"),
        ("war_purpose_selection", "a war purpose yet to be declared"),
    ])
    def test_a_dialogue_is_named_not_called_an_envoy(self, _r14_world, dtype, name):
        from backend.display_names import dialogue_display_name
        w = _r14_world
        w.dialogue_manager.replace({"type": dtype, "target_nation": "Prussia", "options": [],
                                    "context": {}, "turn_created": 1, "blocking": False})
        out = _r14_vassals(w)
        assert out["actions_blocked"] is True
        assert out["blocked_by"] == "dialogue" and out["blocked_by_courts"] == []
        assert out["blocked_by_dialogue"] == name == dialogue_display_name(dtype)

    def test_a_standing_letter_outranks_the_dialogue_as_the_wizard_does(self, _r14_world):
        w = _r14_world
        _r14_letter(w, "Austria", "armistice")
        w.dialogue_manager.preempt({"type": "terms_guidance", "target_nation": "Prussia", "options": [],
                                    "context": {}, "turn_created": 1, "blocking": False})
        out = _r14_vassals(w)
        assert out["blocked_by"] == "letter" and out["blocked_by_courts"] == ["Austria"]

    def test_the_payload_is_strings_only(self, _r14_world):
        w = _r14_world
        _r14_letter(w, "Austria", "armistice")
        out = _r14_vassals(w)
        assert all(isinstance(c, str) for c in out["blocked_by_courts"])
        assert isinstance(out["blocked_by"], str) and isinstance(out["blocked_by_dialogue"], str)

    def test_the_ledger_carries_it_to_the_client(self, _r14_world):
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        w = _r14_world
        _r14_letter(w, "Austria", "armistice")
        with _r14_quiet():
            ledger = build_diplomatic_ledger(w)
        assert ledger["vassals"]["blocked_by_courts"] == ["Austria"]

    def test_the_notice_names_its_cause_and_the_old_sentence_is_gone(self):
        src = _r14_src("diplomatic_ledger.gd")
        render = _r14_func(src, "_render_vassals")
        assert "Envoys await your reply — vassal instruments" not in src
        assert "_vassal_block_notice(vassal_data)" in render
        notice = _r14_func(src, "_vassal_block_notice")
        # a letter: the lock's one lead ("Austria's letter stands unanswered — ")
        assert "Utils.cabinet_shut_lead(courts, true)" in notice
        assert '"vassal instruments are suspended until "' in notice
        assert '"it is answered."' in notice and '"they are answered."' in notice
        # a dialogue: its name, number-neutral
        assert ('"You have " + dialogue_name + " awaiting your answer — vassal instruments are '
                'suspended until the matter is answered."') in notice
        # the cause key the backend sends
        assert 'vassal_data.get("blocked_by", "")' in notice
        assert "blocked_by_courts" in notice and "blocked_by_dialogue" in notice
        for line in notice.splitlines():
            assert not line.startswith(" "), repr(line)

    def test_the_lead_the_notice_calls_is_the_one_that_builds_the_sentence(self):
        """`Utils.cabinet_shut_lead` exists and takes the printed courts."""
        utils = _r14_src("utils.gd")
        assert "static func cabinet_shut_lead(courts: Array, capitalize: bool = false)" in utils


# ══════════════════════════════════════════════════════════════════════════
# S14G-X37 — rung 4 never "approaches" a full ally
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX37:
    """Sibling of S14G-X34, found by its sweep: rung 4 of the war room's counsel
    ("Approach {court}", the ripest diplomatic opening: relation -10..40, no war,
    no cooldown) picked the court with the HIGHEST relation in the band - on the
    shipped 1805 boot that is Spain, our ALLY at +40, "neither friend nor enemy
    (relations +40)", and "Approach Spain" landed on the menu whose alliance and
    pact rows are shut. NOW a court in a full ALLIANCE with France is no opening
    (a defensive ally keeps its open door: the upgrade)."""

    def _rung4(self, world):
        from backend.game_logic import diplomatic_advisory as ADV
        with _r14_quiet():
            return ADV._build_situation_recommendation(world, "France", [], None, "defensive")

    def test_the_boots_ally_at_plus_forty_is_not_the_opening(self, _r14_world):
        w = _r14_world
        assert w.get_diplomatic_state("France", "Spain") == "ALLIANCE"
        assert _r14_rel(w, "France", "Spain") == 40
        rec = self._rung4(w)
        assert rec["kind"] == "open_proposal"
        assert rec["target_nation"] != "Spain"
        assert w.get_diplomatic_state("France", rec["target_nation"]) != "ALLIANCE"
        assert "neither friend nor enemy" in rec["text"]
        assert -10 <= _r14_rel(w, "France", rec["target_nation"]) <= 40

    def test_the_pick_is_the_best_court_that_is_not_an_ally(self, _r14_world):
        """Denmark (+10, at peace) on the shipped board: the highest relation
        among the courts that are no ally (Bavaria at +60 is out of the band)."""
        assert self._rung4(_r14_world)["target_nation"] == "Denmark"

    def test_a_defensive_ally_keeps_its_open_upgrade_door(self, _r14_world):
        w = _r14_world
        w.diplomatic_states[w._make_diplo_key("France", "Spain")] = "DEFENSIVE_ALLIANCE"
        assert self._rung4(w)["target_nation"] == "Spain"

    def test_no_court_but_allies_in_the_band_gives_no_rung_4_counsel(self, _r14_world):
        """The class: with every other court out of the band the rung is silent,
        never an ally it would mislabel."""
        w = _r14_world
        for nation in w.get_active_nations():
            if nation in ("France", "Spain"):
                continue
            w.nation_relations[w._make_diplo_key("France", nation)] = -90
        assert self._rung4(w) is None


# ══════════════════════════════════════════════════════════════════════════
# S14G-X38 — the override send reads the cooldown too
# ══════════════════════════════════════════════════════════════════════════

def _r14_override_dialogue(world, target="Prussia", ptype="open_borders"):
    """The objection's confirm with its `send_override` option, mounted as
    the executor's own tests mount it."""
    world.dialogue_manager.replace({
        "type": "proposal_confirm", "target_nation": target, "talleyrand_text": "I object, Sire.",
        "options": [
            {"label": "Send my terms", "description": "Override.", "action": "send_override",
             "terms": {"proposal_type": ptype, "demands": [], "sweeteners": []}},
            {"label": "Reconsider", "description": "Go back.", "action": "reconsider"}],
        "context": {"original_proposal": {"proposal_type": ptype}},
        "turn_created": 1, "blocking": False})


class TestS14GX38:
    """Sibling of S14G-X35: `send_override` (the pre-proposal objection's "Send
    my terms", in `_choice_counsel`) is the confirm's send by another road and
    never asked the court's cooldown - the envoy departed to a court that had
    refused us. NOW it reads `proposal_cooldown_refusal`, the same words, refused
    free with the objection still up."""

    def test_the_override_send_refuses_a_court_on_cooldown(self, _r14_tense):
        w = _r14_tense
        _r14_override_dialogue(w)
        w.player_proposal_cooldowns["Prussia"] = 2
        dp_before = int(w.diplomatic_points)
        result = _r14_click(w, _r14_executor(), 1)
        assert result["success"] is False
        assert result["message"] == _R14_PATIENCE
        assert int(w.diplomatic_points) == dp_before
        assert w.proposal_in_transit is None and w.talleyrand_state != "IN_TRANSIT"
        assert result["diplomatic_dialogue"]["type"] == "proposal_confirm"      # the objection stands

    def test_the_words_are_the_typed_entrys_and_the_per_type_key_is_read(self, _r14_tense):
        w = _r14_tense
        ex = _r14_executor()
        _r14_override_dialogue(w)
        w.player_proposal_cooldowns["Prussia_open_borders"] = 3
        typed = _r14_typed(w, ex, "Prussia", "open_borders")
        sent = _r14_click(w, ex, 1)
        assert sent["success"] is False and sent["message"] == typed["message"]
        assert "she will not hear it again for 3 more turns" in sent["message"]
        assert w.proposal_in_transit is None

    def test_a_court_off_cooldown_still_receives_the_override(self, _r14_tense):
        """The control: the same click with no cooldown sends."""
        w = _r14_tense
        _r14_override_dialogue(w)
        result = _r14_click(w, _r14_executor(), 1)
        assert result["success"] is True
        assert w.proposal_in_transit is not None and w.talleyrand_state == "IN_TRANSIT"

    def test_the_predicate_has_three_readers(self):
        import ast
        src = (_R14_ROOT / "backend" / "commands" / "diplomatic_executor.py").read_text(encoding="utf-8")
        readers = sorted(
            n.name for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.FunctionDef) and n.name != "proposal_cooldown_refusal"
            and "proposal_cooldown_refusal(" in (ast.get_source_segment(src, n) or ""))
        assert readers == ["_choice_counsel", "_choice_proposal", "_execute_diplomatic_proposal"], readers


# ══════════════════════════════════════════════════════════════════════════
# S14G-X26 — the wire's lock names are the ledger's (one source)
# ══════════════════════════════════════════════════════════════════════════

class TestS14GX26:
    """Sibling of S14G-X25: `main._cabinet_locked_by` repeated the body of
    `DialogueManager.locking_court_names`. It now delegates - the wire
    (`cabinet_locked_by`) and the Vassals tab (`blocked_by_courts`) read ONE
    method, so they can never name different courts."""

    def test_the_wire_delegates_to_the_one_method(self):
        import ast
        src = (_R14_ROOT / "backend" / "main.py").read_text(encoding="utf-8")
        node = [n for n in ast.walk(ast.parse(src))
                if isinstance(n, ast.FunctionDef) and n.name == "_cabinet_locked_by"][0]
        body = ast.get_source_segment(src, node)
        assert "locking_court_names(world)" in body
        assert "locking_letters" not in body.split('"""')[2]       # no copy of the loop
        assert "formed_display_name" not in body.split('"""')[2]

    def test_equality_stays_for_none_one_and_several_courts(self, _r14_world):
        import backend.main as M
        w = _r14_world
        assert M._cabinet_locked_by(w) == w.dialogue_manager.locking_court_names(w) == []
        _r14_letter(w, "Austria", "armistice")
        assert M._cabinet_locked_by(w) == w.dialogue_manager.locking_court_names(w) == ["Austria"]
        _r14_letter(w, "Russia", "armistice")
        _r14_letter(w, "Austria", "peace")             # the same court twice: once
        assert (M._cabinet_locked_by(w) == w.dialogue_manager.locking_court_names(w)
                == _r14_vassals(w)["blocked_by_courts"] == ["Austria", "Russia"])

    def test_the_printed_form_is_kept(self, _r14_world):
        """A court that takes an article is named with it ("the Ottoman Empire")."""
        import backend.main as M
        w = _r14_world
        _r14_ultimatum(w, "Ottoman")
        assert M._cabinet_locked_by(w) == ["the Ottoman Empire"]

    def test_the_wire_carries_it_on_the_base_envelope(self, _r14_world):
        import backend.main as M
        w = _r14_world
        _r14_letter(w, "Austria", "armistice")
        with _r14_quiet():
            base = M.build_base_response(w, success=True, message="x")
        assert base["cabinet_locked_by"] == ["Austria"]
