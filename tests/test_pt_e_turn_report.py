"""Row PT, slice E — the turn report becomes readable.

Build spec: `docs/PLAYTEST_FIXES_SPEC.md` §2 PT-E.

Narration is the only pillar the playtest scored UP, and it is held under
7 by volume rather than quality: 101 dispatch lines over 14 turns, 7.2
per morning, 45% jealousy, 30% supply, the identical vassal remedy tail
eleven times, and ~149 fog sentences against 63 real enemy actions.

* **E1** the dispatch could never narrate anything that happened during
  the turn — the queue is wiped between the phases that fill it and the
  briefing that reports them.
* **E2** `diplomatic_events` rendered only on the screen nobody opens.
* **E3** `turn_events` is collapsed by family at the view seam.
* **E4** one fog sentence naming the courts, not one per court.
* **E5** the enemy phase narrates a bloodless capture of our own soil —
  and stops over-showing a route that merely ended on a lit square.
* **E6** `construction_complete` is fog-classed as a building, not as
  marshal state.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import backend.main as M
from backend.game_logic.dispatch import (
    COLLAPSIBLE_TURN_EVENT_TYPES,
    _build_turn_events,
    collapse_turn_events,
    queue_dispatch_event,
)

from tests.conftest import WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "godot-client" / "project-sovereign" / "scripts"


# ═══════════════════════════════════════════════════════════════════════
# E1 — the queue survives the turn it reports on
# ═══════════════════════════════════════════════════════════════════════

class TestTheDispatchCanNarrateItsOwnTurn:
    def test_an_event_queued_this_turn_reaches_the_dispatch(self):
        """MEASURED: 18 consecutive dispatches, not one `nation_eliminated`
        or war-declaration line, although three fired. The Kingdom of Italy
        — the player's OWN vassal — was destroyed on turn 2 and the turn-3
        briefing carried `['diplomatic_dp_regen', 'paymaster_subsidy',
        'agenda_shift']`. The fog rule on both lost types is "always"."""
        world = WorldFactory.basic()
        queue_dispatch_event(world, "diplomatic_war_declared",
                             {"nation": "Austria", "target": "France"},
                             "always")
        world.advance_turn()
        assert any(e.get("type") == "diplomatic_war_declared"
                   for e in world.pending_dispatch_events)

    def test_last_turns_events_are_pruned(self):
        world = WorldFactory.basic()
        queue_dispatch_event(world, "diplomatic_war_declared",
                             {"nation": "Austria", "target": "France"},
                             "always")
        world.advance_turn()
        world.advance_turn()
        assert not any(e.get("type") == "diplomatic_war_declared"
                       for e in world.pending_dispatch_events)

    def test_the_queue_does_not_grow_without_bound(self):
        world = WorldFactory.basic()
        for _ in range(6):
            queue_dispatch_event(world, "diplomatic_war_declared",
                                 {"nation": "Austria", "target": "France"},
                                 "always")
            world.advance_turn()
        declared = [e for e in world.pending_dispatch_events
                    if e.get("type") == "diplomatic_war_declared"]
        assert len(declared) <= 1

    def test_events_are_stamped_with_their_turn(self):
        world = WorldFactory.basic()
        world.current_turn = 7
        queue_dispatch_event(world, "diplomatic_war_declared", {}, "always")
        assert world.pending_dispatch_events[-1]["queued_turn"] == 7

    def test_an_unstamped_event_is_kept(self):
        """Three producers append directly instead of through the helper.
        Keeping is the safe direction — the defect was deletion."""
        world = WorldFactory.basic()
        world.pending_dispatch_events.append({"type": "hand_rolled"})
        world.advance_turn()
        assert any(e.get("type") == "hand_rolled"
                   for e in world.pending_dispatch_events)


# ═══════════════════════════════════════════════════════════════════════
# E2 — the terminal renders the diplomatic rail
# ═══════════════════════════════════════════════════════════════════════

class TestTheTerminalShowsDiplomacy:
    def test_main_gd_renders_diplomatic_events(self):
        """`main.gd` had ZERO references to the key; the block lived only
        on the re-read screen."""
        src = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        assert 'data.get("diplomatic_events"' in src
        assert "DIPLOMATIC EVENTS" in src

    def test_it_keeps_the_priority_colouring_the_other_surface_uses(self):
        main = (SCRIPTS / "main.gd").read_text(encoding="utf-8")
        block = main.split("═══ DIPLOMATIC EVENTS ═══")[1].split(
            "Peace Deals BPH-D")[0]
        for arm in ('"HIGH"', '"MEDIUM"', '"LOW"'):
            assert arm in block


# ═══════════════════════════════════════════════════════════════════════
# E3 — turn events collapse by family
# ═══════════════════════════════════════════════════════════════════════

def _supply(region, losses, marshal="Ney"):
    return {"type": "supply_attrition", "nation": "France", "region": region,
            "losses": losses, "marshal": marshal,
            "message": f"{marshal} loses {losses:,} troops to supply at {region}"}


def _vassal(name, delta=-2):
    return {"type": "vassal_loyalty", "nation": "France", "vassal": name,
            "lord": "France", "delta": delta,
            "message": f"{name}'s loyalty {'falls' if delta < 0 else 'rises'}"}


class TestTurnEventsCollapse:
    def test_supply_becomes_one_line_naming_the_places(self):
        """The spec's own example sentence."""
        rows = _build_turn_events(
            [_supply("Tyrol", 1200), _supply("Milan", 827, "Davout")],
            "France")
        assert len(rows) == 1
        assert "2,027 men" in rows[0]["message"]
        assert "Tyrol and Milan" in rows[0]["message"]
        assert rows[0]["collapsed_count"] == 2

    def test_three_satellites_drifted(self):
        rows = _build_turn_events(
            [_vassal("Bavaria"), _vassal("Holland"), _vassal("Saxony")],
            "France")
        assert len(rows) == 1
        assert "3 satellites drifted" in rows[0]["message"]

    def test_a_bucket_of_one_passes_through_untouched(self):
        """Only a genuine repeat collapses — IGR-B's rule 3."""
        one = _supply("Tyrol", 1200)
        rows = _build_turn_events([one], "France")
        assert rows[0]["message"] == one["message"]
        assert "collapsed_count" not in rows[0]

    def test_uncollapsible_families_are_never_bucketed(self):
        """An explicit allowlist, never a bare key. IGR-B's docstring
        records what a bare key costs."""
        rows = _build_turn_events(
            [{"type": "marshal_captured", "nation": "France",
              "message": "Ney is taken prisoner!"},
             {"type": "marshal_captured", "nation": "France",
              "message": "Davout is taken prisoner!"}],
            "France")
        assert len(rows) == 2
        assert "marshal_captured" not in COLLAPSIBLE_TURN_EVENT_TYPES

    def test_the_severity_still_reaches_the_client(self):
        rows = _build_turn_events([_supply("Tyrol", 1200),
                                   _supply("Milan", 827)], "France")
        assert rows[0]["severity"] == "warning"

    def test_the_collapse_never_mutates_its_input(self):
        """IGR-B rule 2: `filter_campaign_log` returns ORIGINALS, and
        in-place stamping bakes view state into every save."""
        rows = [{"message": "a", "severity": "warning",
                 "type": "supply_attrition", "_source": _supply("Tyrol", 5)},
                {"message": "b", "severity": "warning",
                 "type": "supply_attrition", "_source": _supply("Milan", 5)}]
        snapshot = [dict(r) for r in rows]
        collapse_turn_events(rows)
        assert rows == snapshot

    def test_the_internal_source_key_never_reaches_the_client(self):
        rows = _build_turn_events([_supply("Tyrol", 1200),
                                   _supply("Milan", 827)], "France")
        for row in rows:
            assert "_source" not in row

    def test_a_long_list_stops_being_a_wall(self):
        rows = _build_turn_events(
            [_vassal(n) for n in ("Bavaria", "Holland", "Saxony", "Naples",
                                  "Warsaw", "Westphalia")], "France")
        assert len(rows) == 1
        assert "and 3 more" in rows[0]["message"]

    def test_rising_and_falling_never_share_a_line(self):
        """The bucket key includes `severity`, and W6-3 makes a falling
        vassal a warning and a rising one mere info. Collapsing them
        together would flatten the colour the client renders by — so they
        are deliberately two rows, and no branch pretends otherwise."""
        rows = _build_turn_events(
            [_vassal("Bavaria", -2), _vassal("Holland", 3)], "France")
        assert len(rows) == 2
        assert {r["severity"] for r in rows} == {"warning", "info"}

    def test_first_seen_order_is_preserved(self):
        rows = _build_turn_events(
            [{"type": "marshal_captured", "nation": "France",
              "message": "Ney is taken prisoner!"},
             _supply("Tyrol", 1200), _supply("Milan", 827)], "France")
        assert rows[0]["message"] == "Ney is taken prisoner!"


# ═══════════════════════════════════════════════════════════════════════
# E4 — one fog sentence
# ═══════════════════════════════════════════════════════════════════════

class TestTheFogLineIsOneSentence:
    def test_many_courts_become_one_line(self):
        joined = M._join_courts(["Austria", "Prussia", "Russia", "Britain",
                                 "Spain", "Denmark"], capitalize=True)
        assert joined.count(" and ") == 1
        assert "3 other courts" in joined

    def test_a_short_list_loses_no_names(self):
        joined = M._join_courts(["Austria", "Prussia"])
        assert joined == "Austria and Prussia"

    def test_one_court_is_just_the_court(self):
        assert M._join_courts(["Austria"]) == "Austria"

    def test_empty_is_empty(self):
        assert M._join_courts([]) == ""

    def test_the_emitter_produces_a_single_entry(self):
        """It emitted one full sentence per hidden court, uncapped, and
        `enemy_phase_dialog.gd:96-100` printed every one — 7-10 lines on
        16 of 18 phases, all ending in the same seven words."""
        src = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        block = src.split('cleaned_phase["fog_hidden_nations"]')[1].split(
            "return cleaned_phase")[0]
        assert "_join_courts" in block
        assert "for n in _hidden" not in block, (
            "a comprehension here is one sentence per court again")


# ═══════════════════════════════════════════════════════════════════════
# E5 / E6 — the enemy phase and the fog class
# ═══════════════════════════════════════════════════════════════════════

class TestABloodlessCaptureIsReported:
    def test_the_move_event_carries_the_capture(self):
        """The arm that reads this would be production-dead without it:
        `region_captured` goes to the CAMPAIGN LOG, and the executor's own
        `events` list said only "move"."""
        src = (REPO / "backend" / "commands"
               / "movement_executor.py").read_text(encoding="utf-8")
        assert 'events[0]["captured_from"] = _old_controller' in src

    def test_the_filter_reads_that_field(self):
        src = (REPO / "backend" / "main.py").read_text(encoding="utf-8")
        assert 'evt.get("captured_from") == player_nation' in src

    def test_own_soil_is_partial_by_construction(self):
        """Which is why the FULL gate suppressed it: the province is ours,
        so we never have FULL on it once it changes hands."""
        from backend.models.intel import FULL

        world = WorldFactory.basic()
        world.calculate_visibility()
        own = [r for r in world.regions.values()
               if r.controller == world.player_nation]
        assert own, "fixture must hold territory"
        assert any(world.get_region_intel(r.name).visibility != FULL
                   for r in own), (
            "if every own region were FULL this row could not have happened")


class TestConstructionIsFogClassedAsABuilding:
    def test_the_event_names_its_owner(self):
        src = (REPO / "backend" / "models" / "world_state.py").read_text(
            encoding="utf-8")
        for block in src.split('"type": "construction_complete"')[1:]:
            head = block.split("})")[0]
            assert '"nation"' in head, (
                "without it the player-side check can never match and the "
                "event always falls to the PARTIAL region arm")

    def test_a_foreign_build_needs_full_visibility(self):
        """`FOG_OF_WAR_SPEC.md:327` classes buildings FULL-only on foreign
        soil; 7 of 11 leaked, including "Supply Depot in Berlin!"."""
        from backend.commands.meta_executor import _filter_tactical_events_by_fog

        world = WorldFactory.basic()
        world.calculate_visibility()
        enemy_region = next(
            (r for r in world.regions.values()
             if r.controller and r.controller != world.player_nation), None)
        assert enemy_region is not None
        from backend.models.intel import FULL, PARTIAL

        intel = world.get_region_intel(enemy_region.name)
        intel.visibility = PARTIAL
        event = {"type": "construction_complete", "region": enemy_region.name,
                 "building": "supply_depot", "nation": enemy_region.controller,
                 "message": "Construction complete: Supply Depot!"}
        assert _filter_tactical_events_by_fog([event], world) == []
        intel.visibility = FULL
        assert _filter_tactical_events_by_fog([event], world) == [event]

    def test_our_own_build_is_always_ours_to_know(self):
        from backend.commands.meta_executor import _filter_tactical_events_by_fog

        world = WorldFactory.basic()
        world.calculate_visibility()
        own = next(r for r in world.regions.values()
                   if r.controller == world.player_nation)
        event = {"type": "construction_complete", "region": own.name,
                 "building": "supply_depot", "nation": world.player_nation,
                 "message": "Construction complete: Supply Depot!"}
        assert _filter_tactical_events_by_fog([event], world) == [event]

    def test_and_it_can_now_reach_the_dispatch_at_all(self):
        """`_build_turn_events` drops anything with no `nation`, so the
        type's whitelist entry and its `severity="good"` were both dead
        code."""
        rows = _build_turn_events(
            [{"type": "construction_complete", "nation": "France",
              "region": "Paris", "building": "supply_depot",
              "message": "Construction complete: Supply Depot in Paris!"}],
            "France")
        assert len(rows) == 1
        assert rows[0]["severity"] == "good"
