"""
VS-R — Authority ↔ Vassal-Loyalty Coupling.

Spec: docs/VASSAL_DEEPENING_SPEC.md §2 + research memo
docs/audits/VASSAL_AUTHORITY_COUPLING_RESEARCH_2026_07_14.md.

"The Empire holds because *you* hold." When the lord's imperial grip spirals
(< 30) the satellite web loosens, the cheap levers are blunted, and enemy
courting bites harder — but the coupling is boot-dormant (grip >= 30 → 0,
byte-identical), one-way (never writes authority back), capped, and reversible
(raising grip above 30 arrests it). Symmetric for enemy lords (GR5).

Signal: a DERIVED get_imperial_grip that blends the lord's court standing
(authority_tracker for the player) with a territorial-collapse term — the crux
fix, since the raw authority_tracker does NOT spiral on military collapse.
"""

import pytest

from backend.models.world_state import WorldState
from backend.models.authority import (
    AUTHORITY_ACCELERATE_BELOW,
    GRIP_CAPITAL_LOST,
    GRIP_ENEMY_COURT_BASE,
    VS_R_CHEAP_LEVER_MULT,
    VS_R_DRIFT_CAP,
    VS_R_DRIFT_SPIRAL,
    authority_vassal_drift,
    courting_effectiveness_scale,
    courting_unlock_bonus,
    get_authority_lever_multiplier,
    get_imperial_grip,
)
from backend.game_logic.vassal import (
    process_vassal_loyalty,
    invest_in_vassal,
    change_vassal_autonomy,
    attempt_vassal_courting,
    release_vassal,
    AUTONOMY_PUPPET,
    AUTONOMY_SATELLITE,
    AUTONOMY_AUTONOMOUS,
)


# ═══════════════════════════════════════════════════════════════════════════
# Helpers — bare world where grip == authority (France holds capital + homeland)
# ═══════════════════════════════════════════════════════════════════════════

def _make_world(authority=100):
    world = WorldState()
    world.current_turn = 5
    world.player_nation = "France"
    world.authority_tracker.authority = authority
    return world


def _add_vassal(world, name="Saxony", loyalty=80, autonomy=AUTONOMY_SATELLITE,
                lord="France"):
    world.vassals[name] = {"lord": lord, "loyalty": loyalty, "autonomy": autonomy}
    # Zero the lord relation so the mechanic under test is isolated.
    world.nation_relations[world._make_diplo_key(name, lord)] = 0
    return world.vassals[name]


def _vassal_event(events, name="Saxony"):
    hits = [e for e in events if e.get("type") == "vassal_loyalty"
            and e.get("vassal") == name]
    return hits[0] if hits else None


def _set_war(world, opponent, france_score):
    """Put France at WAR with an ACTIVE `opponent` and pin the score so that
    get_war_score_for(France, opponent) == france_score. war_scores is stored
    from the alphabetically-FIRST nation's perspective, so flip when France is
    second."""
    key = world._make_diplo_key("France", opponent)
    world.diplomatic_states[key] = "WAR"
    world.war_scores[key] = france_score if key.split("|")[0] == "France" else -france_score
    if opponent not in world.enemy_nations:
        world.enemy_nations.append(opponent)
    world.invalidate_active_nations_cache()


# ═══════════════════════════════════════════════════════════════════════════
# A. The banded drift curve (pure function)
# ═══════════════════════════════════════════════════════════════════════════

class TestBandedCurve:
    @pytest.mark.parametrize("grip", [100, 70, 30, 31])
    def test_healthy_and_neutral_bands_zero(self, grip):
        """grip >= 30 contributes exactly 0 — boot-dormant, byte-identical."""
        assert authority_vassal_drift(grip) == 0

    @pytest.mark.parametrize("grip", [29, 20, 15, 1, 0])
    def test_spiral_band_bleeds(self, grip):
        assert authority_vassal_drift(grip) == VS_R_DRIFT_SPIRAL  # -2

    def test_term_never_exceeds_cap(self):
        """The grip term is capped in magnitude (never a runaway multiplier)."""
        for grip in range(-10, 101):
            assert authority_vassal_drift(grip) >= VS_R_DRIFT_CAP  # >= -4
            assert authority_vassal_drift(grip) <= 0               # negative-only


# ═══════════════════════════════════════════════════════════════════════════
# B. get_imperial_grip — the derived signal (the crux fix)
# ═══════════════════════════════════════════════════════════════════════════

class TestImperialGrip:
    def test_boot_player_full_empire_is_100(self):
        world = _make_world(authority=100)
        assert get_imperial_grip(world, "France") == 100  # VS-R dormant

    def test_boot_enemy_intact_is_75(self):
        world = _make_world()
        assert get_imperial_grip(world, "Prussia") == GRIP_ENEMY_COURT_BASE  # 75

    def test_grip_falls_on_capital_loss_even_at_full_authority(self):
        """The headline fix: the raw authority_tracker stays 100 when Paris
        falls; the DERIVED grip drops by the capital dock."""
        world = _make_world(authority=100)
        paris = world.get_nation_capital("France")
        world.regions[paris].controller = "Prussia"
        assert world.authority_tracker.authority == 100  # tracker unmoved...
        assert get_imperial_grip(world, "France") == 100 - GRIP_CAPITAL_LOST  # ...grip fell

    def test_grip_falls_on_losing_war(self):
        world = _make_world(authority=100)
        _set_war(world, "Austria", -60)
        assert get_imperial_grip(world, "France") == 100 - 15  # deep-loss dock

    def test_realistic_collapse_reaches_spiral(self):
        """Low court standing + Paris lost + losing the war → the spiral band.
        The blend is what tips a wavering Emperor over."""
        world = _make_world(authority=65)
        world.regions[world.get_nation_capital("France")].controller = "Prussia"
        _set_war(world, "Austria", -60)
        grip = get_imperial_grip(world, "France")  # 65 - 40 - 15 = 10
        assert grip == 10
        assert grip < AUTHORITY_ACCELERATE_BELOW

    def test_clamped_0_100(self):
        world = _make_world(authority=100)
        world.authority_tracker.authority = 5
        world.regions[world.get_nation_capital("France")].controller = "Prussia"
        _set_war(world, "Austria", -99)
        assert get_imperial_grip(world, "France") == 0  # clamped, not negative


# ═══════════════════════════════════════════════════════════════════════════
# C. Coupling inside process_vassal_loyalty
# ═══════════════════════════════════════════════════════════════════════════

class TestCouplingDrift:
    def test_boot_dormant_byte_identical(self):
        """authority 100 → grip 100 → grip term 0 → satellite drift is exactly
        -2 (the pre-VS-R pin)."""
        world = _make_world(authority=100)
        _add_vassal(world, loyalty=80)
        e = _vassal_event(process_vassal_loyalty(world))
        assert e["delta"] == -2

    def test_neutral_band_no_coupling(self):
        """grip 50 (30–69) still contributes 0."""
        world = _make_world(authority=50)
        _add_vassal(world, loyalty=80)
        e = _vassal_event(process_vassal_loyalty(world))
        assert e["delta"] == -2

    def test_high_band_no_coupling(self):
        world = _make_world(authority=80)
        _add_vassal(world, loyalty=80)
        e = _vassal_event(process_vassal_loyalty(world))
        assert e["delta"] == -2

    def test_spiral_band_accelerates_satellite(self):
        """grip 20 (< 30) → satellite (-2) + grip (-2) = -4."""
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=80, autonomy=AUTONOMY_SATELLITE)
        assert world.vassals["Saxony"]["loyalty"] == 80
        process_vassal_loyalty(world)
        assert world.vassals["Saxony"]["loyalty"] == 76  # 80 - 4

    def test_spiral_band_puppet_is_minus_six(self):
        """Worst realistic case: puppet (-4) + grip (-2) = -6/turn (the grip
        term itself stays at its -2, well within the -4 cap)."""
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=80, autonomy=AUTONOMY_PUPPET)
        process_vassal_loyalty(world)
        assert world.vassals["Saxony"]["loyalty"] == 74  # 80 - 6

    def test_grip_named_in_reason(self):
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=80)
        e = _vassal_event(process_vassal_loyalty(world))
        assert "grip" in e["reason"].lower()

    def test_keys_off_lord_grip_not_vassal_loyalty(self):
        """A low-loyalty vassal under a STRONG lord (grip 100) takes no grip
        coupling — the term reads the LORD's grip, not the vassal's loyalty."""
        world = _make_world(authority=100)
        _add_vassal(world, loyalty=30)
        e = _vassal_event(process_vassal_loyalty(world))
        assert e["delta"] == -2  # pure satellite drift, no grip term


# ═══════════════════════════════════════════════════════════════════════════
# D. "No cheap recovery" — the lever multiplier
# ═══════════════════════════════════════════════════════════════════════════

class TestLeverMultiplier:
    def test_multiplier_full_when_healthy(self):
        world = _make_world(authority=100)
        assert get_authority_lever_multiplier(world, "France") == 1.0

    def test_multiplier_blunts_in_spiral(self):
        world = _make_world(authority=20)
        assert get_authority_lever_multiplier(world, "France") == VS_R_CHEAP_LEVER_MULT

    def test_invest_full_strength_when_healthy(self):
        world = _make_world(authority=100)
        _add_vassal(world, loyalty=50)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 1000
        assert invest_in_vassal(world, "Saxony")["success"]
        assert world.vassals["Saxony"]["loyalty"] == 60  # +10 byte-identical

    def test_invest_blunted_in_spiral_but_full_cost(self):
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=50)
        world.diplomatic_points = 3
        world.nation_gold["France"] = 1000
        res = invest_in_vassal(world, "Saxony")
        assert res["success"]
        assert world.vassals["Saxony"]["loyalty"] == 54  # +int(10*0.4)=+4
        assert world.diplomatic_points == 2      # full DP still paid
        assert world.nation_gold["France"] == 800  # full 200g still paid
        assert "blunt" in res["message"].lower()

    def test_autonomy_up_blunted_in_spiral(self):
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=50, autonomy=AUTONOMY_SATELLITE)
        world.diplomatic_points = 3
        res = change_vassal_autonomy(world, "Saxony", AUTONOMY_AUTONOMOUS)
        assert res["success"]
        assert world.vassals["Saxony"]["loyalty"] == 54  # +int(10*0.4)=+4

    def test_autonomy_down_never_softened(self):
        """Low grip must not CUSHION a downgrade — it is always -15."""
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=50, autonomy=AUTONOMY_AUTONOMOUS)
        world.diplomatic_points = 3
        res = change_vassal_autonomy(world, "Saxony", AUTONOMY_PUPPET)
        assert res["success"]
        assert world.vassals["Saxony"]["loyalty"] == 35  # -15 full

    def test_release_works_in_spiral(self):
        """Release is an existential concession — never softened; still frees
        the vassal at rock-bottom grip."""
        world = _make_world(authority=10)
        _add_vassal(world, loyalty=45)
        assert release_vassal(world, "Saxony")["success"]
        assert "Saxony" not in world.vassals

    def test_subsidy_not_softened_in_spiral(self):
        """A per-turn subsidy clause is NOT a cheap one-shot: a *large* subsidy
        stays existential and contributes full-strength even in the spiral."""
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=80, autonomy=AUTONOMY_SATELLITE)
        world.active_treaties = {
            "France|Saxony": {"clauses": [
                {"type": "gold_per_turn", "from": "France", "to": "Saxony",
                 "amount": 800},
            ]}
        }
        process_vassal_loyalty(world)
        # satellite(-2) + subsidy(+8, unsoftened) + grip(-2) = +4
        assert world.vassals["Saxony"]["loyalty"] == 84


# ═══════════════════════════════════════════════════════════════════════════
# E. Enemy courting scales with the player's weakness
# ═══════════════════════════════════════════════════════════════════════════

class TestCourtingScale:
    def test_pure_scale_functions(self):
        assert courting_unlock_bonus(100) == 0
        assert courting_effectiveness_scale(100) == 1.0
        assert courting_unlock_bonus(0) == 15
        assert courting_effectiveness_scale(0) == 1.5

    def test_courting_unchanged_when_healthy(self):
        world = _make_world(authority=100)
        _add_vassal(world, loyalty=40)
        world.nation_dp["Prussia"] = 5
        world.nation_relations[world._make_diplo_key("Saxony", "Prussia")] = 20
        events = attempt_vassal_courting(world, "Prussia")
        assert events[0]["loyalty_reduction"] == 15  # x1.0
        assert world.vassals["Saxony"]["loyalty"] == 25  # 40 - 15

    def test_courting_reaches_deeper_and_bites_harder_when_weak(self):
        """grip 0 (authority 0): the loyalty<50 unlock widens to <65 and the
        reduction scales x1.5 — the Allies peel a wavering satellite."""
        world = _make_world(authority=0)
        _add_vassal(world, loyalty=60)  # ABOVE 50 — only courtable once weak
        world.nation_dp["Prussia"] = 5
        world.nation_relations[world._make_diplo_key("Saxony", "Prussia")] = 20
        events = attempt_vassal_courting(world, "Prussia")
        assert len(events) == 1                         # unlock widened
        assert events[0]["loyalty_reduction"] == 22     # int(round(15*1.5))
        assert world.vassals["Saxony"]["loyalty"] == 38  # 60 - 22

    def test_courting_still_blocked_above_widened_threshold(self):
        world = _make_world(authority=0)
        _add_vassal(world, loyalty=70)  # above 50 + 15 = 65
        world.nation_dp["Prussia"] = 5
        assert attempt_vassal_courting(world, "Prussia") == []


# ═══════════════════════════════════════════════════════════════════════════
# F. Guardrails: one-way, reversible, no new fields
# ═══════════════════════════════════════════════════════════════════════════

class TestGuardrails:
    def test_one_way_no_authority_writeback(self):
        """Losing vassal loyalty must NEVER move authority (one-way; Q4)."""
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=80, autonomy=AUTONOMY_PUPPET)
        before = world.authority_tracker.authority
        process_vassal_loyalty(world)
        assert world.authority_tracker.authority == before

    def test_no_new_serialized_vassal_fields(self):
        """The grip term is DERIVED — process must not stamp a field onto the
        vassal state dict (zero new serialized fields, memo Q6)."""
        world = _make_world(authority=20)
        v = _add_vassal(world, loyalty=80)
        keys_before = set(v.keys())
        process_vassal_loyalty(world)
        assert set(world.vassals["Saxony"].keys()) == keys_before

    def test_reversible_winning_the_war_arrests_spiral(self):
        """Grip docked into the spiral by a losing war; when the war score
        recovers, grip climbs back above 30 and the coupling relaxes to 0 —
        the Saxony-after-Lützen property, via the one-way loop."""
        world = _make_world(authority=40)
        _add_vassal(world, loyalty=80, autonomy=AUTONOMY_SATELLITE)
        _set_war(world, "Austria", -60)          # grip 40 - 15 = 25 → spiral
        assert get_imperial_grip(world, "France") == 25
        process_vassal_loyalty(world)
        assert world.vassals["Saxony"]["loyalty"] == 76  # -2 -2

        # A decisive victory turns the war score around → grip re-anchors.
        _set_war(world, "Austria", -10)          # no longer < -30
        assert get_imperial_grip(world, "France") == 40  # back above 30
        loy = world.vassals["Saxony"]["loyalty"]
        process_vassal_loyalty(world)
        assert world.vassals["Saxony"]["loyalty"] == loy - 2  # grip term gone

    def test_full_satellite_spiral_is_slow_enough_to_arrest(self):
        """A full 3-satellite spiral (grip pinned < 30) takes many turns to
        collapse — 'he MAY lose them', not an instant wipe (recoverability
        floor >= 8 turns)."""
        world = _make_world(authority=20)
        for n, loy in (("Holland", 100), ("Italy", 100), ("Switzerland", 100)):
            _add_vassal(world, name=n, loyalty=loy, autonomy=AUTONOMY_SATELLITE)
        turns = 0
        while world.vassals and any(s["loyalty"] > 0 for s in world.vassals.values()):
            process_vassal_loyalty(world)
            turns += 1
            # break-guard: satellite(-2)+grip(-2) = -4/turn → 25 turns
            for s in world.vassals.values():
                s["loyalty"] = max(0, s["loyalty"])
            if turns > 40:
                break
        assert turns >= 8

    def test_spiral_band_recovery_hint_variant(self):
        """In the spiral band the hint names the BIG levers, not invest/garrison."""
        world = _make_world(authority=20)
        _add_vassal(world, loyalty=60)  # healthy band vassal, spiralling lord
        e = _vassal_event(process_vassal_loyalty(world))
        hint = e["recovery_hint"].lower()
        assert hint
        assert "invest" not in hint          # cheap gesture retired here
        assert ("subsidy" in hint or "autonomy" in hint
                or "release" in hint or "battle" in hint)

    def test_healthy_band_hint_unchanged(self):
        """At healthy grip the original teaching hint is byte-preserved."""
        world = _make_world(authority=100)
        _add_vassal(world, loyalty=80)
        e = _vassal_event(process_vassal_loyalty(world))
        for lever in ("Invest", "garrison", "autonomy"):
            assert lever.lower() in e["recovery_hint"].lower()


# ═══════════════════════════════════════════════════════════════════════════
# G. GR5 — the coupling fires symmetrically for enemy lords
# ═══════════════════════════════════════════════════════════════════════════

class TestEnemySymmetry:
    def test_enemy_lord_spiral_bleeds_its_satellite(self):
        """An enemy lord whose grip has collapsed (capital lost + deep losing
        war → 20) bleeds its own satellite -2 from the grip term, no special
        path — the coupling is symmetric because it keys off the LORD (GR5)."""
        world = _make_world(authority=100)
        # Collapse Prussia's grip: its capital (Berlin) falls to France + it is
        # deep in a losing war against France (an active, region-holding foe).
        berlin = world.get_nation_capital("Prussia")
        world.regions[berlin].controller = "France"          # capital lost (-40)
        key = world._make_diplo_key("Prussia", "France")     # "France|Prussia"
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 60   # France +60 → Prussia -60 (deep war, -15)
        world.invalidate_active_nations_cache()
        assert get_imperial_grip(world, "Prussia") == 20     # 75 - 40 - 15
        assert get_imperial_grip(world, "Prussia") >= 15     # enemy never sub-15

        world.vassals["Warsaw"] = {"lord": "Prussia", "loyalty": 80,
                                   "autonomy": AUTONOMY_SATELLITE}
        world.nation_relations[world._make_diplo_key("Warsaw", "Prussia")] = 0
        process_vassal_loyalty(world)
        assert world.vassals["Warsaw"]["loyalty"] == 76  # satellite -2 + grip -2
