"""NV-3 — The Descent on England (docs/NAVAL_SPEC.md §5.3, §11).

The full H3 chain, every step visible to both sides: the camp (staged at 2
turns, the boulogne_camp beat), Britain's DERIVED reaction (blockade→guard,
which lapses the blockade — the two-front tension with no scripting), the
Grand Diversion (once per war, seeded 45%: a window or a Trafalgar), and
the A4 worked-example pin — the Combined Fleet with a successful diversion
opens the Strait at the 0.9× floor, and no proper subset of it does.

A1 also lives here: parity-by-build takes ~25+ turns — you cannot
crash-build a navy, which is the fact Napoleon ran into.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import naval
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _mass_the_camp(world, strength=45000):
    """Put a Grand Army at Normandy (an authored camp province — and,
    since NV-8c cut the Flanders line, the invasion beach itself)."""
    ney = world.get_marshal("Ney")
    ney.location = "Normandy"
    ney.strength = strength
    world._build_marshal_index()
    return ney


def _at_drill_ceiling(world):
    """§5.3.4's steady state: Britain guards, the Combined Fleet recovered
    to the war drill ceiling."""
    world.fleets["Britain"]["posture"] = "guard"
    world.fleets["Britain"]["readiness"] = 100
    for nation in ("France", "Spain", "Holland"):
        world.fleets[nation]["readiness"] = naval.NAVY_DRILL_CEILING


# ═══════════════════════════════════════════════════════════════════════════
# THE CAMP (§5.3.1)
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCamp:
    def test_forty_thousand_men_start_the_clock(self, world):
        _mass_the_camp(world)
        assert naval.camp_strength(world, "France") >= 40000
        naval._camp_tick(world)
        assert world.fleets["France"]["camp_turns"] == 1
        assert not naval.camp_staged(world, "France")

    def test_staged_at_two_fires_the_beat_once(self, world):
        _mass_the_camp(world)
        naval._camp_tick(world)
        naval._camp_tick(world)
        assert naval.camp_staged(world, "France")
        beats = [e for e in world.event_log if e.get("type") == "boulogne_camp"]
        assert len(beats) == 1
        naval._camp_tick(world)  # stays staged — never refires
        beats = [e for e in world.event_log if e.get("type") == "boulogne_camp"]
        assert len(beats) == 1

    def test_a_dispersed_camp_resets(self, world):
        ney = _mass_the_camp(world)
        naval._camp_tick(world)
        ney.strength = 10000
        naval._camp_tick(world)
        assert world.fleets["France"]["camp_turns"] == 0

    def test_no_island_war_no_camp(self, world):
        """The camp counts only against an island naval enemy."""
        _mass_the_camp(world)
        world.diplomatic_states[world._make_diplo_key("Britain", "France")] = "PEACE"
        world.invalidate_active_nations_cache()
        naval._camp_tick(world)
        assert world.fleets["France"]["camp_turns"] == 0


class TestBritainsReaction:
    def test_a_staged_camp_pulls_the_fleet_home(self, world):
        """§5.3.2: posture flips blockade→guard — and the blockade of
        Brest/Toulon LAPSES, the two-front tension with no scripting."""
        _mass_the_camp(world)
        world.fleets["France"]["camp_turns"] = naval.DESCENT_CAMP_STAGED_TURNS
        naval.derive_ai_postures(world)
        assert world.fleets["Britain"]["posture"] == "guard"
        assert not naval.is_blockaded(world, "France")  # pressure lifted

    def test_a_live_window_also_holds_the_guard(self, world):
        world.fleets["France"]["window_turns"] = 2
        naval.derive_ai_postures(world)
        assert world.fleets["Britain"]["posture"] == "guard"

    def test_no_camp_means_blockade(self, world):
        naval.derive_ai_postures(world)
        assert world.fleets["Britain"]["posture"] == "blockade"


# ═══════════════════════════════════════════════════════════════════════════
# A4 — THE WORKED EXAMPLE (§5.3.4 at the v1.0.3 drill ceiling)
# ═══════════════════════════════════════════════════════════════════════════

class TestA4WorkedExample:
    """A4, MEASURED on the shipped scenario (the anchor's falsifiable SHAPE
    is the pin): the full Combined Fleet + a successful diversion clears
    the 0.9× floor, and NO proper subset of it does.

    Correction recorded (NV-3 landing record): the spec's §5.3.4 table
    quoted Britain ALONE at 100/50 — but the spec's OWN §3.1 pooling rule
    adds Russia's Baltic squadron to Britain's coverage (Britain|Russia
    alliance, both at war with France, same guard mode): coverage is
    ~110 → windowed ~55, so the measured ratios are 0.53 shut / 1.07
    window-open / 0.74 no-Spain-shut. The 1805 conclusion is unchanged —
    it needed Spain, and Trafalgar ended it."""

    def test_without_a_window_the_strait_is_hopeless(self, world):
        _at_drill_ceiling(world)
        verdict = naval.crossing_check(world, "France", "Normandy", "London")
        assert not verdict["allowed"]
        # ≈59 pooled effective — the spec's mover-side arithmetic exactly.
        assert verdict["mover_effective"] == pytest.approx(59.0, abs=1.0)
        assert verdict["ratio"] == pytest.approx(0.53, abs=0.02)

    def test_the_combined_fleet_with_a_window_opens_it(self, world):
        """France 33.75 + Spain 18.0 + Batavia 7.2 ≈ 59 vs the halved
        coverage → ≥ 0.9. The mechanics re-derive the actual 1805 plan."""
        _at_drill_ceiling(world)
        world.fleets["France"]["window_turns"] = 2
        verdict = naval.crossing_check(world, "France", "Normandy", "London")
        assert verdict["allowed"], verdict
        assert verdict["verdict"] == "window"
        assert verdict["ratio"] == pytest.approx(1.07, abs=0.03)
        assert verdict["ratio"] >= naval.WINDOW_CROSSING_FLOOR

    def test_no_proper_subset_opens_it(self, world):
        """Without Spain the pool is ~41 → below the floor — SHUT. Why the
        plan needed Spain, and why Trafalgar ended it."""
        _at_drill_ceiling(world)
        world.fleets["France"]["window_turns"] = 2
        world.fleets["Spain"]["ships"] = 0
        verdict = naval.crossing_check(world, "France", "Normandy", "London")
        assert not verdict["allowed"]
        assert verdict["ratio"] == pytest.approx(0.74, abs=0.03)
        assert verdict["ratio"] < naval.WINDOW_CROSSING_FLOOR

    def test_the_landing_is_the_existing_land_game(self, world):
        """§5.3.5: during the window the MOVE passes the gate; London's
        25k tier garrison and everything after is the land war (DEF-6's
        'demoted to a naval-gated edge' arm — the pin flips consciously)."""
        _at_drill_ceiling(world)
        world.fleets["France"]["window_turns"] = 2
        ney = _mass_the_camp(world, strength=45000)
        # Clear the British field army from London for a clean move check
        # (the garrison is the region's, not a marshal).
        for m in world.get_marshals_by_nation("Britain"):
            if m.location == "London":
                m.location = "Wessex"
        world._build_marshal_index()
        executor = CommandExecutor()
        result = executor._movement._execute_move(
            ney, "London", world, {"world": world})
        assert result["success"], result["message"]
        assert ney.location == "London"


# ═══════════════════════════════════════════════════════════════════════════
# THE GRAND DIVERSION (§5.3.3a — once per war, seeded 45%)
# ═══════════════════════════════════════════════════════════════════════════

def _seed_with_outcome(world, nation, want_success):
    """Find a campaign seed whose diversion roll goes the wanted way —
    determinism harnessed, not bypassed (the AI-0b discipline)."""
    for i in range(64):
        candidate = f"nv3-{i}"
        world.campaign_seed = candidate
        namespace = f"naval::diversion::{int(world.current_turn)}::{nation}"
        if naval._pct_roll(world, namespace, naval.DIVERSION_SUCCESS_PCT) == want_success:
            return candidate
    raise AssertionError("no seed found in 64 tries")


class TestGrandDiversion:
    def test_success_opens_the_window(self, world):
        _seed_with_outcome(world, "France", True)
        result = naval.resolve_diversion(world, "France")
        assert result["success"] and result["window"]
        assert world.fleets["France"]["window_turns"] == naval.WINDOW_TURNS
        opens = [e for e in world.event_log if e.get("type") == "strait_open"]
        assert len(opens) == 1

    def test_failure_is_trafalgar_as_it_happened(self, world):
        """Intercepted returning, at bad readiness — the fleet fights §4.4
        and history's actual outcome is one of the reachable endings."""
        _seed_with_outcome(world, "France", False)
        ships0 = world.fleets["France"]["ships"]
        result = naval.resolve_diversion(world, "France")
        assert result["success"] and not result["window"]
        assert world.fleets["France"]["ships"] < ships0
        action = result["fleet_action"]
        assert action["loser"] == "France"

    def test_once_per_war(self, world):
        _seed_with_outcome(world, "France", True)
        naval.resolve_diversion(world, "France")
        second = naval.resolve_diversion(world, "France")
        assert not second["success"]
        assert "already" in second["message"]

    def test_the_spent_feint_resets_at_peace(self, world):
        world.fleets["France"]["diversion_used"] = True
        for enemy in list(world.get_nations_at_war_with("France")):
            world.diplomatic_states[world._make_diplo_key("France", enemy)] = "PEACE"
        world.invalidate_active_nations_cache()
        naval.process_naval_turn(world)
        assert world.fleets["France"]["diversion_used"] is False

    def test_the_verb_rides_the_executor(self, world):
        _seed_with_outcome(world, "France", True)
        executor = CommandExecutor()
        result = executor._naval._execute_naval_diversion(
            {"action": "naval_diversion",
             "raw_command": "order the diversion"}, {"world": world})
        assert result["success"]

    def test_window_decrements_and_the_shut_beat_fires(self, world):
        """The verdict-flip machinery announces the Strait closing again —
        the §5.3 window's whole drama is that the game says when."""
        _at_drill_ceiling(world)
        _mass_the_camp(world)  # keeps the Channel link tracked at Normandy
        world.fleets["France"]["window_turns"] = 1
        naval.process_naval_turn(world)  # records the OPEN verdict, decrements to 0
        world.fleets["Britain"]["posture"] = "guard"
        naval.process_naval_turn(world)  # verdict flips shut → beat
        shuts = [e for e in world.event_log if e.get("type") == "strait_shut"]
        assert len(shuts) >= 1


# ═══════════════════════════════════════════════════════════════════════════
# A1 — TIME IS THE WALL (§3.5 brake 1)
# ═══════════════════════════════════════════════════════════════════════════

class TestA1ParityByBuild:
    def test_parity_takes_twenty_five_plus_turns(self, world):
        """France cannot reach RN effective parity by building alone before
        turn ~25 at sustained spend: even at readiness 100 and the full
        2/turn rate, (100 − 45) hulls ÷ 2 ≈ 28 turns; at the war drill
        ceiling 75 it is 44. The §13.2 program cost: ≥ 18,000g."""
        rn_effective = 100.0
        boot_ships = world.fleets["France"]["ships"]
        ships_needed_at_100 = rn_effective / 1.0
        turns_at_best = (ships_needed_at_100 - boot_ships) / naval.SHIP_BUILD_RATE
        assert turns_at_best >= 25
        program_gold = (ships_needed_at_100 - boot_ships) * naval.SHIP_COST
        assert program_gold >= 18000

    def test_the_blockaded_build_is_half_rate(self, world):
        assert naval.build_rate(world, "France") == 1  # blockaded at boot
        world.fleets["Britain"]["posture"] = "guard"
        assert naval.build_rate(world, "France") == 2


# ═══════════════════════════════════════════════════════════════════════════
# THE TICK END-TO-END (advance_turn wiring)
# ═══════════════════════════════════════════════════════════════════════════

class TestAdvanceTurnWiring:
    def test_the_admiralty_tick_runs_inside_advance_turn(self, world):
        """One end-turn: postures derived, readiness moved, the blockade
        rot visible — wired before the income phase."""
        r0 = world.fleets["France"]["readiness"]
        world.advance_turn()
        assert world.fleets["Britain"]["posture"] == "blockade"
        assert world.fleets["France"]["readiness"] == r0 - naval.READINESS_TICK

    def test_fleetless_world_advances_untouched(self):
        legacy = WorldState(player_nation="France")
        legacy.advance_turn()  # no crash, no fleets minted
        assert legacy.fleets == {}
