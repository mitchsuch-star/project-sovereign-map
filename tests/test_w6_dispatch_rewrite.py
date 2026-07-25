"""W6-3 — The Dispatch Rewrite: "Berthier tells the story" (EXP-N1).

The audit's top-ranked item: the simulation produces the drama; this slice
makes the morning dispatch TELL it. All deterministic templates over
existing events (GR6) — headline selection (§5.1), danger flags (§5.2),
arc memory (§5.3), cause lines + the NO-INTEL collapse (§5.4).
"""

from backend.game_logic.dispatch import (
    HEADLINE_WEIGHTS,
    _build_headline,
    _build_marshal_arcs,
    _build_marshal_status,
    _collect_supply_attrition_turns,
    _derive_danger,
    _pick_berthier_note,
    build_morning_dispatch,
)
from backend.models.intel import FULL, PARTIAL, UNKNOWN, RegionIntel

from tests.conftest import MarshalFactory, WorldFactory


def _battle_event(world, attacker, atk_nation, defender, def_nation,
                  location, outcome, atk_cas=0, def_cas=0, turn=None):
    world.event_log.append({
        "type": "battle",
        "attacker": attacker, "attacker_nation": atk_nation,
        "defender": defender, "defender_nation": def_nation,
        "location": location, "outcome": outcome,
        "attacker_casualties": atk_cas, "defender_casualties": def_cas,
        "turn": turn if turn is not None else world.current_turn - 1,
    })


# ════════════════════════════════════════════════════════════════════════
# §5.1 Headline selection
# ════════════════════════════════════════════════════════════════════════

class TestHeadlineSelection:
    def test_no_events_no_headline(self):
        world = WorldFactory.basic()
        world.event_log = []
        assert _build_headline(world, "France") is None

    def test_home_region_captured_is_the_top_story(self):
        world = WorldFactory.basic()
        world.event_log = [
            {"type": "region_captured", "region": "Paris",
             "captured_by": "Prussia", "captured_from": "France",
             "turn": world.current_turn - 1},
            {"type": "marshal_broken", "marshal": "Ney", "nation": "France",
             "region": "Belgium", "turn": world.current_turn - 1},
        ]
        headline = _build_headline(world, "France")
        assert headline["class"] == "home_captured"
        assert headline["weight"] == HEADLINE_WEIGHTS["home_captured"]
        assert "Paris has fallen" in headline["text"]
        # The broken marshal becomes a sub-beat, not the headline.
        assert any("Ney" in beat for beat in headline["sub_beats"])

    def test_own_broken_beats_region_lost(self):
        world = WorldFactory.basic()
        # Rhineland is NOT French homeland — captured FROM France it scores
        # region_lost (75), below own_broken (90).
        world.regions["Rhineland"].controller = "Prussia"
        world.event_log = [
            {"type": "region_captured", "region": "Rhineland",
             "captured_by": "Prussia", "captured_from": "France",
             "turn": world.current_turn - 1},
            {"type": "marshal_broken", "marshal": "Ney", "nation": "France",
             "region": "Belgium", "turn": world.current_turn - 1},
        ]
        headline = _build_headline(world, "France")
        assert headline["class"] == "own_broken"

    def test_own_mauled_from_casualty_fraction(self):
        world = WorldFactory.basic()
        ney = world.get_marshal("Ney")
        ney.strength = 6000
        world.event_log = []
        # 4,000 lost against 10,000 pre-battle = 40% → mauled.
        _battle_event(world, "Blucher", "Prussia", "Ney", "France",
                      "Belgium", "attacker_tactical_victory", def_cas=4000)
        headline = _build_headline(world, "France")
        assert headline["class"] == "own_mauled"
        assert "4,000" in headline["text"]

    def test_war_declaration_touching_us(self):
        world = WorldFactory.basic()
        world.event_log = [
            {"type": "war_declaration", "aggressor": "Austria",
             "target": "France", "turn": world.current_turn - 1},
        ]
        headline = _build_headline(world, "France")
        assert headline["class"] == "war_touches_us"
        assert "Austria" in headline["text"]

    def test_ai_vs_ai_war_is_not_our_headline(self):
        """Stage D (AI_INTENT_SPEC §17): an AI-vs-AI war now HAS a lead —
        the europe_at_war class — but it is never dressed as OUR war
        (war_touches_us), and it sits below every France-centric weight
        (pin 13). The old pin asserted None; the real claim it protected
        was the class boundary, kept here."""
        world = WorldFactory.basic()
        world.event_log = [
            {"type": "war_declaration", "aggressor": "Austria",
             "target": "Prussia", "turn": world.current_turn - 1},
        ]
        headline = _build_headline(world, "France")
        assert headline is not None
        assert headline["class"] == "europe_at_war"
        from backend.game_logic.dispatch import HEADLINE_WEIGHTS
        assert headline["weight"] < HEADLINE_WEIGHTS["war_touches_us"]

    def test_enemy_on_our_soil_from_fresh_intel(self):
        world = WorldFactory.basic()
        world.event_log = []
        intel = RegionIntel("Belgium")
        intel.visibility = FULL
        intel.known_marshals = [{"name": "Blucher", "nation": "Prussia",
                                 "strength": 30000}]
        intel.last_updated_turn = world.current_turn
        world.intel["Belgium"] = intel
        assert world.regions["Belgium"].controller == "France"
        headline = _build_headline(world, "France")
        assert headline["class"] == "enemy_on_our_soil"
        assert "Blucher" in headline["text"]
        assert "Belgium" in headline["text"]

    def test_stale_intel_does_not_headline(self):
        world = WorldFactory.basic()
        world.current_turn = 9
        world.event_log = []
        intel = RegionIntel("Belgium")
        intel.visibility = FULL
        intel.known_marshals = [{"name": "Blucher", "nation": "Prussia",
                                 "strength": 30000}]
        intel.last_updated_turn = 3  # ancient
        world.intel["Belgium"] = intel
        assert _build_headline(world, "France") is None

    def test_berthier_note_answers_the_headline(self):
        world = WorldFactory.basic()
        note = _pick_berthier_note(world, "France", [], {},
                                   headline_class="home_captured")
        assert "France herself" in note

    def test_no_headline_falls_back_to_ladder(self):
        world = WorldFactory.basic()
        note = _pick_berthier_note(world, "France", [],
                                   {"bankrupt": True}, headline_class="")
        assert "finances are dire" in note


# ════════════════════════════════════════════════════════════════════════
# §5.2 Danger flags
# ════════════════════════════════════════════════════════════════════════

class TestDangerFlags:
    def _world_with(self, marshal):
        world = WorldFactory.with_marshals([marshal])
        return world

    def test_co_located_superior_enemy_flags(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=20000)
        world = self._world_with(ney)
        intel = RegionIntel("Belgium")
        intel.visibility = FULL
        intel.known_marshals = [{"name": "Blucher", "nation": "Prussia",
                                 "strength": 49000}]
        intel.last_updated_turn = world.current_turn
        world.intel["Belgium"] = intel
        danger = _derive_danger(ney, world, "France", {})
        assert "49,000" in danger

    def test_fogged_co_located_enemy_does_not_flag(self):
        """Fog-legality (R5): the danger flag reads the player's own intel,
        never omniscient marshal data."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=20000)
        blucher = MarshalFactory.enemy(name="Blucher", location="Belgium",
                                       nation="Prussia", strength=49000)
        world = WorldFactory.with_marshals([ney, blucher])
        intel = RegionIntel("Belgium")
        intel.visibility = UNKNOWN  # synthetic: the player cannot see it
        intel.known_marshals = []
        world.intel["Belgium"] = intel
        danger = _derive_danger(ney, world, "France", {})
        assert danger == ""

    def test_band_intel_counts_via_midpoint(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=20000)
        world = self._world_with(ney)
        intel = RegionIntel("Belgium")
        intel.visibility = PARTIAL
        intel.known_marshals = [{"name": "Blucher", "nation": "Prussia",
                                 "band": "large force"}]  # midpoint 55,000
        world.intel["Belgium"] = intel
        danger = _derive_danger(ney, world, "France", {})
        assert "shares the field" in danger

    def test_low_morale_flags(self):
        ney = MarshalFactory.infantry(name="Ney")
        ney.morale = 35
        world = self._world_with(ney)
        danger = _derive_danger(ney, world, "France", {})
        assert "Morale failing" in danger

    def test_forced_retreat_flags(self):
        ney = MarshalFactory.infantry(name="Ney")
        ney.retreated_this_turn = True
        world = self._world_with(ney)
        danger = _derive_danger(ney, world, "France", {})
        assert "Fell back" in danger

    def test_consecutive_supply_attrition_flags(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium")
        world = self._world_with(ney)
        world.current_turn = 6
        supply_turns = {"Ney": [5, 6]}
        danger = _derive_danger(ney, world, "France", supply_turns)
        assert "Starving" in danger

    def test_single_attrition_turn_does_not_flag(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium")
        world = self._world_with(ney)
        world.current_turn = 6
        danger = _derive_danger(ney, world, "France", {"Ney": [6]})
        assert danger == ""

    def test_no_danger_empty_string(self):
        ney = MarshalFactory.infantry(name="Ney")
        world = self._world_with(ney)
        assert _derive_danger(ney, world, "France", {}) == ""

    def test_danger_rides_the_marshal_row(self):
        ney = MarshalFactory.infantry(name="Ney")
        ney.morale = 30
        world = self._world_with(ney)
        rows = _build_marshal_status(world, "France")
        assert rows[0]["danger"] != ""

    def test_supply_events_reach_the_event_log(self):
        """The danger flag needs attrition HISTORY — process_supply_attrition
        now mirrors its events into world.event_log."""
        # 300k men in a town-sized region: far over any derived capacity.
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=300000)
        world = WorldFactory.with_marshals([ney])
        world.process_supply_attrition()
        turns = _collect_supply_attrition_turns(world)
        assert turns.get("Ney"), "supply_attrition missing from event_log"


# ════════════════════════════════════════════════════════════════════════
# §5.3 Arc memory
# ════════════════════════════════════════════════════════════════════════

class TestArcMemory:
    def test_hunted_chain_from_scripted_log(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=300)
        world = WorldFactory.with_marshals([ney])
        world.current_turn = 5
        world.event_log = []
        for turn in (2, 3, 4):
            _battle_event(world, "ArchdukeCharles", "Austria", "Ney",
                          "France", "Belgium", "attacker_tactical_victory",
                          def_cas=4000, turn=turn)
            world.event_log.append({"type": "retreat", "marshal": "Ney",
                                    "turn": turn})
        arcs = _build_marshal_arcs(world, "France")
        assert "Ney" in arcs
        arc = arcs["Ney"]
        assert arc["hunted_by"] == "ArchdukeCharles"
        assert arc["consecutive_defeats"] >= 2
        assert "Hunted by Archduke Charles" in arc["line"]
        assert "300" in arc["line"]

    def test_arc_upgrades_the_status_note(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=300)
        world = WorldFactory.with_marshals([ney])
        world.current_turn = 5
        world.event_log = []
        for turn in (3, 4):
            _battle_event(world, "Blucher", "Prussia", "Ney", "France",
                          "Belgium", "attacker_victory" if turn == 4
                          else "attacker_tactical_victory",
                          def_cas=2000, turn=turn)
        rows = _build_marshal_status(world, "France")
        ney_row = next(r for r in rows if r["name"] == "Ney")
        assert ney_row["arc_note"] != ""
        assert ney_row["status_note"] == ney_row["arc_note"]

    def test_quiet_marshal_has_no_arc(self):
        ney = MarshalFactory.infantry(name="Ney")
        world = WorldFactory.with_marshals([ney])
        world.event_log = []
        assert _build_marshal_arcs(world, "France") == {}

    def test_cap_three_arc_lines(self):
        marshals = [MarshalFactory.infantry(name=f"M{i}", location="Belgium",
                                            strength=5000) for i in range(5)]
        world = WorldFactory.with_marshals(marshals)
        world.current_turn = 5
        world.event_log = []
        for m in marshals:
            for turn in (3, 4):
                _battle_event(world, "Blucher", "Prussia", m.name, "France",
                              "Belgium", "attacker_victory", def_cas=1000,
                              turn=turn)
        arcs = _build_marshal_arcs(world, "France")
        assert len(arcs) == 3


# ════════════════════════════════════════════════════════════════════════
# §5.4 Cause lines + NO-INTEL collapse
# ════════════════════════════════════════════════════════════════════════

class TestVassalReason:
    def test_loyalty_event_names_its_cause(self):
        from backend.game_logic.vassal import AUTONOMY_PUPPET, process_vassal_loyalty
        world = WorldFactory.basic()
        world.vassals["Saxony"] = {
            "lord": "France", "loyalty": 50, "autonomy": AUTONOMY_PUPPET,
            "path": "treaty", "created_turn": 1, "tribute_rate": 0.5,
            "carved_from": "", "regions": [],
        }
        # Neutralize the France|Saxony +40 default relation so the puppet
        # drift (-4) is the dominant (and only) contributor.
        world.nation_relations[world._make_diplo_key("France", "Saxony")] = 0
        events = process_vassal_loyalty(world)
        loyalty_events = [e for e in events if e.get("type") == "vassal_loyalty"]
        assert loyalty_events, "significant drift must emit an event"
        e = loyalty_events[0]
        assert "puppet resentment" in e["reason"]
        assert "puppet resentment" in e["message"]
        assert e["nation"] == "France"

    def test_dispatch_turn_events_render_the_reason(self):
        from backend.game_logic.dispatch import _build_turn_events
        entries = _build_turn_events([{
            "type": "vassal_loyalty", "vassal": "Saxony", "lord": "France",
            "nation": "France", "old_loyalty": 50, "new_loyalty": 46,
            "delta": -4, "reason": "puppet resentment",
            "message": "Saxony loyalty 46 (-4): puppet resentment",
        }], "France")
        assert len(entries) == 1
        assert "puppet resentment" in entries[0]["message"]
        assert entries[0]["severity"] == "warning"


class TestNoIntelCollapse:
    def test_wall_collapses_to_count_and_frontiers(self):
        from backend.intel_report import generate_intel_report
        world = WorldFactory.basic()
        # Fog out everything except Paris (so the frontier = Paris-adjacent).
        for region_name in world.regions:
            intel = world.get_region_intel(region_name)
            intel.visibility = UNKNOWN if region_name != "Paris" else FULL
        report = generate_intel_report(world)
        summary = report["no_intelligence_summary"]
        unknown_count = len(report["no_intelligence"])
        assert f"No word from {unknown_count} provinces" in summary
        assert "beyond the frontiers of" in summary
        # The raw name wall must be GONE from the text.
        assert summary in report["report_text"]
        named = summary.split("frontiers of ", 1)[1].rstrip(".").split(", ")
        assert len(named) <= 8


# ════════════════════════════════════════════════════════════════════════
# Full build integration
# ════════════════════════════════════════════════════════════════════════

class TestDispatchBuildIntegration:
    def test_headline_and_danger_ride_the_dispatch(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=20000)
        world = WorldFactory.with_marshals([ney])
        world.event_log = [
            {"type": "region_captured", "region": "Paris",
             "captured_by": "Prussia", "captured_from": "France",
             "turn": world.current_turn - 1},
        ]
        ney.morale = 30
        dispatch = build_morning_dispatch(world)
        assert dispatch["headline"]["class"] == "home_captured"
        assert dispatch["berthier_note"] == (
            "France herself is under the enemy's boot, Sire. "
            "Every other matter is secondary.")
        ney_row = next(m for m in dispatch["marshals"] if m["name"] == "Ney")
        assert "Morale failing" in ney_row["danger"]

    def test_quiet_turn_has_no_headline_key(self):
        world = WorldFactory.basic()
        world.event_log = []
        dispatch = build_morning_dispatch(world)
        assert "headline" not in dispatch
