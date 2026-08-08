"""POSITION 7 — The Danube Lesson (tutorial_1805.json) scenario pins.

The tutorial steers the player into REAL system responses, so every teaching
beat's PRECONDITION is pinned here as arithmetic over the live world — if a
retune moves a number out of its beat's window, the pin names the beat it
breaks. Beat table: docs/TUTORIAL_SCRIPT.md §The Danube Lesson.

The scenario is authored-deterministic: no variance bands, no navies, no
agenda decks, no marshal_pool. scenario_name is the ID ("tutorial") the
client's School of War overlay arms on.
"""

import json
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.commands.objection_v2 import ConcernLevel, evaluate_aggressive
from backend.game_logic.diplomacy import can_enter_territory
from backend.models.world_state import WorldState
from backend.modding.validator import validate_scenario

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "tutorial_1805.json"
)


@pytest.fixture
def tutorial_world():
    """Function-scoped (the AI-V seed-escape lesson: module-scoped fixtures
    build before function-scoped autouse env pins)."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


class TestScenarioFile:
    def test_file_exists_and_validator_passes(self):
        assert SCENARIO_PATH.exists(), "tutorial_1805.json missing"
        result = validate_scenario(str(SCENARIO_PATH))
        assert not result.errors, [f"{e.path}: {e.message}" for e in result.errors]

    def test_scenario_name_is_the_client_contract_id(self):
        """Cross-agent contract: the client overlay arms on exactly
        'tutorial' — the pretty title lives in scenario_description."""
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        assert data["scenario_name"] == "tutorial"
        assert "Danube" in data["scenario_description"]

    def test_no_variance_bands_boot_is_seed_invariant(self, monkeypatch):
        """No authored band → no variance: two boots under DIFFERENT seeds
        produce identical authored facts (AI-0c: no band = no variance)."""
        data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        for value in data["nation_relations"].values():
            assert isinstance(value, int), "tutorial relations must be unbanded"
        assert "threat_level_band" not in data

        monkeypatch.setenv("SOVEREIGN_SEED", "historical")
        w1 = WorldState.from_scenario(str(SCENARIO_PATH))
        monkeypatch.setenv("SOVEREIGN_SEED", "austerlitz")
        w2 = WorldState.from_scenario(str(SCENARIO_PATH))
        for name in ("Ney", "Davout", "Soult", "Senarmont",
                     "Kienmayer", "Jellacic", "ArchdukeCharles", "Schwarzenberg"):
            assert w1.get_marshal(name).location == w2.get_marshal(name).location
            assert w1.get_marshal(name).strength == w2.get_marshal(name).strength
        assert w1.nation_relations.get("Austria|France") == \
            w2.nation_relations.get("Austria|France") == -70
        assert w1.threat_level == w2.threat_level == 20


class TestBootFacts:
    def test_identity_and_treasury(self, tutorial_world):
        w = tutorial_world
        assert w.scenario_name == "tutorial"
        assert w.sovereign_map == "europe"
        assert len(w.regions) == 126
        assert w.player_nation == "France"
        assert w.current_turn == 1
        # EB-1: 900 <= the 2,000 hoard floor → boot charges exactly 0, so the
        # T1 economy lesson shows a clean ledger.
        assert w.gold == 900
        assert w.calculate_state_charges("France") == 0

    def test_wars_and_states(self, tutorial_world):
        w = tutorial_world
        assert w.is_at_war("France", "Austria")
        assert not w.is_at_war("France", "Britain")
        assert not w.is_at_war("France", "Prussia")
        assert w.diplomatic_states.get("Bavaria|France") == "ALLIANCE"
        for vassal in ("Holland", "KingdomOfItaly", "Switzerland"):
            key = "|".join(sorted(["France", vassal]))
            assert w.diplomatic_states.get(key) == "VASSAL", key

    def test_roster_as_authored(self, tutorial_world):
        w = tutorial_world
        # S5 live-drive retune (Aug 8): Jellacic CAUTIOUS (a literal's
        # stagnation-breaker lunged him off the Tyrol anchor by turn 4 —
        # a cautious defender fortifies the pass and stays); Charles at
        # HUNGARY (a Vienna-paired reserve combined and sortied by turn 5,
        # 44k onto the scripted beats — apart, the combined-strength attack
        # arrives in the designed turn-8+ window).
        expected = {
            "Ney": ("France", "Rhineland", 24000, "aggressive"),
            "Davout": ("France", "Lorraine", 26000, "cautious"),
            "Soult": ("France", "Paris", 40000, "literal"),
            "Senarmont": ("France", "Franche-Comte", 14000, "cautious"),
            "Kienmayer": ("Austria", "Swabia", 8000, "literal"),
            "Jellacic": ("Austria", "Tyrol", 8000, "cautious"),
            "ArchdukeCharles": ("Austria", "Hungary", 26000, "cautious"),
            "Schwarzenberg": ("Austria", "Vienna", 24000, "cautious"),
        }
        assert len(w.marshals) == len(expected)
        for name, (nation, location, strength, personality) in expected.items():
            m = w.get_marshal(name)
            assert m is not None, name
            assert m.nation == nation
            assert m.location == location
            assert m.strength == strength
            value = m.personality.value if hasattr(m.personality, "value") else m.personality
            assert value == personality, name
        assert w.get_marshal("Senarmont").artillery is True

    def test_dormant_systems(self, tutorial_world):
        """Each omission is load-bearing: naval, agendas, commissioning."""
        w = tutorial_world
        assert getattr(w, "fleets", {}) == {}
        assert getattr(w, "agendas", {}) == {}
        assert getattr(w, "marshal_pool", {}) == {}

    def test_engine_hint_latches_pre_shown(self, tutorial_world):
        """The four one-shot engine hints are authored true so their popups
        never collide with tutor cards."""
        w = tutorial_world
        assert w.coordination_tutorial_shown is True
        assert w.opening_attack_guidance_shown is True
        assert w.delegation_hint_shown is True
        assert w.muster_hint_shown is True

    def test_ap_pools(self, tutorial_world):
        assert tutorial_world.actions_remaining == 4
        assert tutorial_world.admin_actions_remaining == 2


class TestGeographyAndWalls:
    def test_theater_controllers(self, tutorial_world):
        w = tutorial_world
        for region, controller in [
            ("Swabia", "Bavaria"), ("Munich", "Bavaria"), ("Franconia", "Bavaria"),
            ("Tyrol", "Austria"), ("Vienna", "Austria"), ("Bohemia", "Austria"),
            ("Rhineland", "France"), ("Lorraine", "France"), ("Franche-Comte", "France"),
            ("Nassau", "Hesse"),
        ]:
            assert w.regions[region].controller == controller, region

    def test_beat_adjacency(self, tutorial_world):
        """Every scripted hop is one registry edge."""
        w = tutorial_world
        for a, b in [
            ("Rhineland", "Swabia"),      # T3 Ney's attack
            ("Franche-Comte", "Munich"),  # T1 Senarmont's move (allied transit)
            ("Munich", "Tyrol"),          # T4 bombardment range
            ("Lorraine", "Swabia"), ("Swabia", "Franconia"),  # T5 two-hop march
            ("Franconia", "Tyrol"),       # T6 capture approach
            ("Bohemia", "Tyrol"),         # T8+ the Austrian counter-blow road
        ]:
            assert b in w.regions[a].adjacent_regions, f"{a} -> {b}"
            assert a in w.regions[b].adjacent_regions, f"{b} -> {a}"

    def test_movement_walls(self, tutorial_world):
        """The one-way front: France transits allied Bavaria and enters
        war-held Austria; Austria is WALLED by PEACE soil on every road west
        except through French armies."""
        w = tutorial_world
        assert can_enter_territory(w, "France", "Bavaria")   # ALLIANCE bridge
        assert can_enter_territory(w, "France", "Austria")   # WAR
        assert not can_enter_territory(w, "France", "Hesse")  # PEACE wall
        assert not can_enter_territory(w, "Austria", "Bavaria")  # THE wall
        assert can_enter_territory(w, "Austria", "France")   # war soil only

    def test_kienmayer_has_no_friendly_exit(self, tutorial_world):
        """T3 pin: from Swabia every neighbor is French war soil (a battle)
        or PEACE-walled — no friendly withdrawal exists, so a beaten
        Kienmayer breaks in place or dies. Both branches are scripted."""
        w = tutorial_world
        for neighbor in w.regions["Swabia"].adjacent_regions:
            controller = w.regions[neighbor].controller
            assert controller != "Austria", neighbor
            if controller != "France":
                assert not can_enter_territory(w, "Austria", controller), neighbor


class TestBeatPreconditions:
    def test_t2_objection_is_strong_pre_variance(self, tutorial_world):
        """T2: 'Ney, defend' with Kienmayer PARTIAL-visible adjacent.
        24,000 / band-midpoint 10,000 = 2.4 → STRONG. Mood variance moves at
        most one level, and MODERATE still popups — the beat cannot lose its
        popup. (Never script 'hold' — strategic upgrade evaluates NONE; never
        'fortify' — 2 AP + immobilizes.)"""
        w = tutorial_world
        ney = w.get_marshal("Ney")
        level = evaluate_aggressive(ney, "defend", {"action": "defend"}, {"world": w})
        assert level == ConcernLevel.STRONG

    def test_t3_attack_is_favorable(self, tutorial_world):
        """T3: 24,000 vs 8,000 on plains (no terrain bonus, no fort) — the
        inferred ratio is >= 1.0 so no muster-confirm modal interrupts the
        first battle lesson."""
        w = tutorial_world
        swabia = w.regions["Swabia"]
        assert swabia.terrain == "plains"
        assert not getattr(swabia, "fortification_level", 0)
        ney = w.get_marshal("Ney")
        kienmayer = w.get_marshal("Kienmayer")
        assert ney.strength / kienmayer.strength >= 2.0

    def test_t4_bombardment_geometry(self, tutorial_world):
        """T4: Senarmont fires Munich→Tyrol (adjacent, range 1) having moved
        on T1 only — the artillery moved-this-turn refusal cannot fire."""
        w = tutorial_world
        sen = w.get_marshal("Senarmont")
        assert sen.artillery is True
        assert sen.movement_range == 1
        assert sen.moved_this_turn is False
        assert "Tyrol" in w.regions["Munich"].adjacent_regions

    def test_t6_capture_target_shape(self, tutorial_world):
        """T6: Tyrol is Austrian starting soil, ungarrisoned, unfortified —
        battle-win capture AND the PF-3 empty-move fallback both raise the
        Plunder/Secure modal (not the own-soil auto-secure)."""
        w = tutorial_world
        tyrol = w.regions["Tyrol"]
        assert tyrol.controller == "Austria"
        assert getattr(tyrol, "garrison_strength", 0) == 0
        assert not tyrol.buildings
        # The capitals lesson figures on screen nearby:
        assert w.regions["Munich"].garrison_strength == 10000   # minor tier
        assert w.regions["Vienna"].garrison_strength == 25000   # major tier

    def test_t6_no_enemy_estates_no_stage2(self, tutorial_world):
        """The W6-8 estate stage cannot fire: no enemy marshal holds
        dotation_regions on this world."""
        for m in tutorial_world.marshals.values():
            assert not getattr(m, "dotation_regions", []), m.name

    def test_t7_recruit_price_is_450_at_paris(self, tutorial_world):
        """T7: base 200 × 0.75 capital discount × 3 war pricing = 450, with
        Soult (admin 7) in the neutral Intendance band. The tutor card quotes
        live figures; this pin is why the quoted example stays true."""
        w = tutorial_world
        soult = w.get_marshal("Soult")
        assert soult.skills["administration"] == 7
        cost = CommandExecutor()._economy._calculate_recruit_cost(
            w.regions["Paris"], w, base_cost=200, nation="France", marshal=soult)
        assert cost == 450

    def test_force_limit_headroom(self, tutorial_world):
        """ES-3: the authored roster sits comfortably under the force limit —
        no over-limit warnings interrupt the school."""
        w = tutorial_world
        limit = w.get_force_limit("France")
        fielded = sum(m.strength for m in w.marshals.values()
                      if m.nation == "France")
        assert limit is not None
        assert fielded < limit, (fielded, limit)

    def test_containment_ratios_hold_the_forward_corps(self, tutorial_world):
        """The literal screen corps cannot attack at boot: every P4 ratio is
        under the boldest literal threshold (1.0 − 8% mood = 0.92)."""
        w = tutorial_world
        kien = w.get_marshal("Kienmayer")
        for defender in ("Ney", "Davout", "Senarmont"):
            ratio = kien.strength / w.get_marshal(defender).strength
            assert ratio < 0.92, defender
        # And the Franche-Comte depot garrison is assault-proof for him:
        assert kien.strength / w.regions["Franche-Comte"].garrison_strength < 0.92

    def test_garrison_does_not_starve_the_guns(self, tutorial_world):
        """Risk pin 3: Senarmont (14k) standing at Munich beside the 10k
        Bavarian garrison takes no supply attrition — garrisons do not count
        against marshal supply (the shipped Moore@London precedent)."""
        w = tutorial_world
        sen = w.get_marshal("Senarmont")
        sen.location = "Munich"
        w._build_marshal_index()
        before = sen.strength
        w.process_supply_attrition()
        assert sen.strength == before
