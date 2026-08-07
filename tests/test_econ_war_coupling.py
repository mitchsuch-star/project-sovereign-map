"""EC-W (Econ War-Coupling pass 3) — memo docs/audits/ECON_WAR_COUPLING_
RESEARCH_2026_07_17.md §3.

The July-17 playtest defect: France's treasury snowballed (+7,500%) while its
army was destroyed (−66%) and Britain stood on core home soil. Upkeep stays
billed on live fielded strength (user steer: "salaries"); these slices add the
MISSING war expenses:

  EC-W1  Contributions of War — enemy-army presence suspends a province's
         income (+ stability bleed) — new signed "Contributions" component.
  EC-W2  The War Effort — France enters the WE system (per-turn + the missing
         defender-loses battle arm) and every nation pays
         int(max(0,treasury) × WE // WAR_EFFORT_DIVISOR)/turn — new signed
         "War Effort" component.
  EC-W3  The Butcher's Bill — one-time int(casualties × MATERIEL_RATE) per
         side at battle resolution (outside Net, plunder precedent).
  EC-W4  Peace with Teeth — indemnities price to the payer's purse (covered
         in test_settlement_incoming_offers.py; the player-ask fraction is
         pinned here).
  EC-W5  fix-in-passing — AI plunder ×1.75 parity (GR5) + the economy
         report's net including infrastructure.

All four mechanics are BOOT-ZERO by construction (presence-/WE-/battle-/
settlement-gated) — the E1 band and per-nation boot solvency stay
byte-identical except the pinned Bavaria case (Mack stands in Swabia at boot:
the historically-correct Sept-1805 occupation).
"""

from pathlib import Path

import pytest

from backend.game_logic.ledger import _build_economy
from backend.game_logic.settlement_baseline import (
    CONCESSION_BASELINE_TREASURY_FRACTION,
)
from backend.models.world_state import (
    DISRUPTION_MIN_STRENGTH,
    DISRUPTION_STABILITY_DRAIN,
    MATERIEL_RATE,
    PLUNDER_INCOME_MULTIPLIER,
    WAR_EFFORT_DIVISOR,
    WorldState,
)

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _hostile_pair(world, a="France", b="Austria"):
    """Ensure a and b are at WAR."""
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = "WAR"


def _park(world, marshal_name, region_name):
    m = world.marshals[marshal_name]
    m.location = region_name
    return m


def _french_region(world, exclude_capital=True):
    for name in world.get_nation_regions("France"):
        region = world.regions[name]
        if exclude_capital and region.is_capital:
            continue
        if region.get_effective_income() > 0:
            return region
    raise AssertionError("no income-bearing French region found")


# ═══════════════════════ EC-W1: Contributions of War ═══════════════════════


class TestDisruptedRegions:
    def test_enemy_army_on_french_soil_disrupts(self, world):
        _hostile_pair(world, "France", "Austria")
        region = _french_region(world)
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength >= DISRUPTION_MIN_STRENGTH)
        _park(world, enemy.name, region.name)
        assert region.name in world.get_disrupted_regions()

    def test_not_at_war_no_disruption(self, world):
        """An army merely passing through a non-belligerent's soil disrupts
        nothing — the gate is strictly is_at_war (boot cases: Bernadotte in
        Franconia, Massena in Milan)."""
        region = _french_region(world)
        # Pick a nation NOT at war with France
        neutral_marshal = None
        for m in world.marshals.values():
            if m.nation != "France" and not world.is_at_war("France", m.nation) \
                    and m.strength >= DISRUPTION_MIN_STRENGTH:
                neutral_marshal = m
                break
        if neutral_marshal is None:
            pytest.skip("no neutral marshal on this boot")
        _park(world, neutral_marshal.name, region.name)
        assert region.name not in world.get_disrupted_regions()

    def test_small_remnant_does_not_disrupt(self, world):
        _hostile_pair(world, "France", "Austria")
        region = _french_region(world)
        enemy = next(m for m in world.marshals.values() if m.nation == "Austria")
        _park(world, enemy.name, region.name)
        enemy.strength = DISRUPTION_MIN_STRENGTH - 1
        assert region.name not in world.get_disrupted_regions()

    def test_captured_marshal_does_not_disrupt(self, world):
        _hostile_pair(world, "France", "Austria")
        region = _french_region(world)
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength >= DISRUPTION_MIN_STRENGTH)
        _park(world, enemy.name, region.name)
        enemy.captured_by = "France"
        assert region.name not in world.get_disrupted_regions()

    def test_legacy_world_never_disrupts(self):
        legacy = WorldState()
        assert legacy.get_disrupted_regions() == set()


class TestContributionsComponent:
    def test_income_suspended_and_named(self, world):
        _hostile_pair(world, "France", "Austria")
        region = _french_region(world)
        expected = region.get_effective_income()
        assert expected > 0
        baseline_net = world.calculate_turn_income("France")
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength >= DISRUPTION_MIN_STRENGTH)
        _park(world, enemy.name, region.name)
        data = world.calculate_turn_income("France")
        assert data["contributions"] == expected
        # income stays GROSS (ES-2 pattern)
        assert data["income"] == baseline_net["income"]
        detail = next(rd for rd in data["breakdown"]["region_details"]
                      if rd["region"] == region.name)
        assert detail["disrupted"] is True
        assert detail["contributions_cost"] == expected

    def test_net_falls_by_the_suspension(self, world):
        _hostile_pair(world, "France", "Austria")
        region = _french_region(world)
        expected = region.get_effective_income()
        before = _build_economy(world, "France")["net"]
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength >= DISRUPTION_MIN_STRENGTH)
        _park(world, enemy.name, region.name)
        after = _build_economy(world, "France")["net"]
        assert after == before - expected

    def test_gr5_mirror_france_disrupts_austria(self, world):
        """France standing on Austrian soil suspends AUSTRIA's income the
        same way (the shared income seam — GR5)."""
        _hostile_pair(world, "France", "Austria")
        target = None
        for name in world.get_nation_regions("Austria"):
            if world.regions[name].get_effective_income() > 0:
                target = world.regions[name]
                break
        assert target is not None
        ney = next(m for m in world.marshals.values()
                   if m.nation == "France" and m.strength >= DISRUPTION_MIN_STRENGTH)
        _park(world, ney.name, target.name)
        data = world.calculate_turn_income("Austria")
        assert data["contributions"] == target.get_effective_income()

    def test_disrupted_estate_feeds_nobody(self, world):
        """EC-W1 estate interlock: a hostile army on an endowed province
        starves the household (satisfaction falls) AND the nation pays no
        dotation skim for it — the income simply never arrives."""
        from backend.game_logic.dotation import get_estate_income
        _hostile_pair(world, "France", "Austria")
        # Endow a French marshal with a conquered (non-homeland) province:
        # flip an Austrian region to France to stage it.
        target = None
        for name in world.get_nation_regions("Austria"):
            region = world.regions[name]
            if not region.is_capital and region.get_effective_income() > 0:
                target = region
                break
        assert target is not None
        target.controller = "France"
        target.stability = 80  # income-bearing
        world.invalidate_active_nations_cache()
        marshal = next(m for m in world.marshals.values() if m.nation == "France")
        marshal.dotation_regions = [target.name]
        assert get_estate_income(marshal, world) == target.get_effective_income()
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength >= DISRUPTION_MIN_STRENGTH
                     and m.name != marshal.name)
        _park(world, enemy.name, target.name)
        assert get_estate_income(marshal, world) == 0
        data = world.calculate_turn_income("France")
        detail = next(rd for rd in data["breakdown"]["region_details"]
                      if rd["region"] == target.name)
        assert detail["dotation_cost"] == 0
        assert detail["disrupted"] is True

    def test_stability_bleeds_under_occupation(self, world):
        _hostile_pair(world, "France", "Austria")
        region = _french_region(world)
        region.stability = 80
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria" and m.strength >= DISRUPTION_MIN_STRENGTH)
        _park(world, enemy.name, region.name)
        world.process_stability_growth()
        assert region.stability == 80 - DISRUPTION_STABILITY_DRAIN
        # Liberation: enemy leaves, normal growth resumes
        _park(world, enemy.name, world.get_nation_capital("Austria"))
        world.process_stability_growth()
        assert region.stability > 80 - DISRUPTION_STABILITY_DRAIN


class TestBootAnchorsHold:
    def test_france_boot_contributions_zero(self, world):
        data = world.calculate_turn_income("France")
        assert data["contributions"] == 0

    def test_austria_britain_prussia_boot_contributions_zero(self, world):
        for nation in ("Austria", "Britain", "Prussia"):
            assert world.calculate_turn_income(nation)["contributions"] == 0

    def test_boot_state_charges_zero_everywhere(self, world):
        """EB-1 re-bless: every nation boots at/below CHARGES_HOARD_FLOOR
        (max boot treasury = Britain's exactly 2,000 = the floor), so the
        Charges of Empire are 0 for everyone on the boot turn — the E1
        anchors are untouched by construction."""
        for nation in ("France", "Austria", "Britain", "Prussia", "Bavaria"):
            assert world.calculate_state_charges(nation) == 0

    def test_bavaria_boot_case_pinned_and_solvent(self, world):
        """The sole boot delta: if Austria boots at war with Bavaria with
        Mack's army standing on Bavarian soil (the actual Sept-1805
        occupation of Swabia), Bavaria loses that province's income and MUST
        remain net-positive regardless."""
        econ = _build_economy(world, "Bavaria")
        disrupted = world.get_disrupted_regions()
        bavarian_disrupted = [
            r for r in disrupted
            if world.regions[r].controller == "Bavaria"
        ]
        if bavarian_disrupted:
            assert econ["contributions"] > 0
        assert econ["net"] > 0, "Bavaria must stay solvent at boot (E1 rule)"

    def test_no_non_bavarian_boot_disruption(self, world):
        """No OTHER nation's soil is disrupted at boot — the E1 anchors for
        France/Austria/Britain/Prussia/Russia stay byte-identical."""
        disrupted = world.get_disrupted_regions()
        owners = {world.regions[r].controller for r in disrupted}
        assert owners <= {"Bavaria"}, (
            f"unexpected boot disruption on {owners} — the E1 boot anchors "
            f"only tolerate the pinned Mack@Swabia case")


# ═══════════════════════ EC-W2: The War Effort ══════════════════════════════


class TestStateChargesDrain:
    """EB-1 (Econ Balance gate Aug 7 2026, ECON_BALANCE_GATE_2026_08_07.md
    §3 EB-1): CONSCIOUS RE-BLESS of the EC-W2 formula pins. The WE-only
    hoard tax was ABSORBED into `calculate_state_charges` — ONE
    condition-priced rate (WE + crown + war + ill + unrest + grip terms)
    over the SAME divisor, on the chest ABOVE a working floor. The
    treasury-fraction SHAPE and WAR_EFFORT_DIVISOR are unchanged; the
    WE arithmetic rides inside the rate."""

    def test_rate_composition_at_war(self, world):
        """The named terms are the formula — pin the composition on the
        boot France (at war, stable interior, full grip): WE + crown +
        war establishment, nothing else."""
        from backend.models.world_state import (
            CHARGES_CROWN_BASE, CHARGES_WAR_RATE)
        world.war_exhaustion["France"] = 100
        rate = world.get_state_charges_rate("France")
        keys = {t["key"] for t in rate["terms"]}
        assert keys == {"war_exhaustion", "crown", "war_establishment"}
        assert rate["rate"] == 100 + CHARGES_CROWN_BASE + CHARGES_WAR_RATE

    def test_formula(self, world):
        from backend.models.world_state import CHARGES_HOARD_FLOOR
        world.nation_gold["France"] = 40000
        world.war_exhaustion["France"] = 100
        rate = world.get_state_charges_rate("France")["rate"]
        assert world.calculate_state_charges("France") == (
            (40000 - CHARGES_HOARD_FLOOR) * rate // WAR_EFFORT_DIVISOR)

    def test_zero_at_or_below_the_hoard_floor(self, world):
        """The floor is the boot-neutrality anchor (B6): a chest at or
        below 2,000 pays NOTHING whatever the conditions."""
        from backend.models.world_state import CHARGES_HOARD_FLOOR
        world.war_exhaustion["France"] = 150
        for gold in (0, -500, CHARGES_HOARD_FLOOR):
            world.nation_gold["France"] = gold
            assert world.calculate_state_charges("France") == 0

    def test_peacetime_crown_term_bites(self, world):
        """THE Aug-7 disease: at peace there was NO brake at all (Prussia
        +298/turn and Spain +1,010/turn linearly forever). The crown term
        now charges every hoard above the floor, war or no war."""
        from backend.models.world_state import (
            CHARGES_CROWN_BASE, CHARGES_HOARD_FLOOR)
        for key, state in list(world.diplomatic_states.items()):
            if state == "WAR" and "Prussia" in key.split("|"):
                world.diplomatic_states[key] = "PEACE"
        world.nation_gold["Prussia"] = 10000
        world.war_exhaustion.pop("Prussia", None)
        rate = world.get_state_charges_rate("Prussia")
        assert {t["key"] for t in rate["terms"]} == {"crown"}
        assert world.calculate_state_charges("Prussia") == (
            (10000 - CHARGES_HOARD_FLOOR) * CHARGES_CROWN_BASE
            // WAR_EFFORT_DIVISOR)

    def test_unrest_term_reads_the_interior(self, world):
        """'The interior is restless': one held province at/below the
        unrest line flips the term on — the condition the WE clock was
        blind to (a collapsing France finally bleeds faster than a
        prospering one)."""
        world.war_exhaustion.pop("France", None)
        keys = {t["key"] for t in world.get_state_charges_rate("France")["terms"]}
        assert "restless_interior" not in keys
        region = world.regions[world.nation_starting_regions["France"][0]]
        region.stability = 40
        keys = {t["key"] for t in world.get_state_charges_rate("France")["terms"]}
        assert "restless_interior" in keys

    def test_legacy_world_pays_nothing(self):
        legacy = WorldState()
        legacy.nation_gold["France"] = 50000
        legacy.war_exhaustion["France"] = 100
        assert legacy.calculate_state_charges("France") == 0

    def test_applied_in_income_phase_and_shown_in_ledger(self, world):
        from backend.models.world_state import CHARGES_HOARD_FLOOR
        world.nation_gold["France"] = 25000
        world.war_exhaustion["France"] = 80
        rate = world.get_state_charges_rate("France")["rate"]
        expected = (25000 - CHARGES_HOARD_FLOOR) * rate // WAR_EFFORT_DIVISOR
        econ = _build_economy(world, "France")
        assert econ["state_charges"] == expected
        result = world.process_income_phase("France")
        assert result["state_charges"] == expected
        # applied: treasury moved by net which includes the drain
        assert result["net"] <= result["income"] - expected + result["admin_bonus"]

    def test_gr5_ai_nation_pays_too(self, world):
        from backend.models.world_state import CHARGES_HOARD_FLOOR
        world.nation_gold["Austria"] = 10000
        world.war_exhaustion["Austria"] = 50
        rate = world.get_state_charges_rate("Austria")["rate"]
        assert world.calculate_state_charges("Austria") == (
            (10000 - CHARGES_HOARD_FLOOR) * rate // WAR_EFFORT_DIVISOR)

    def test_poor_austria_pays_trivially(self, world):
        """The design property that killed the flat-rate alternative: a poor
        nation's drain is ~nothing (boot chest ≤ the floor pays ZERO), so
        Austria's +18 boot margin can never be bankrupted by this term."""
        world.war_exhaustion["Austria"] = 200  # maximum exhaustion
        drain = world.calculate_state_charges("Austria")
        assert drain == 0, (
            f"Austria's boot chest sits under the hoard floor — the charge "
            f"must be exactly 0, got {drain}")

    def test_old_seam_is_gone(self, world):
        """The absorption is total: the old helper and the old key must not
        survive anywhere a caller could silently keep paying WE-only."""
        assert not hasattr(world, "calculate_war_effort_cost")
        assert "war_effort" not in world.calculate_turn_income("France")
        assert "war_effort" not in _build_economy(world, "France")


class TestFranceWEAccrual:
    def test_per_turn_accrual_at_war(self, world):
        from backend.game_logic.coalition import process_coalition_turn
        _hostile_pair(world, "France", "Austria")
        world.war_exhaustion.pop("France", None)
        process_coalition_turn(world)
        assert world.war_exhaustion.get("France", 0) == 8

    def test_decay_at_peace(self, world):
        from backend.game_logic.coalition import process_coalition_turn
        # Clear every French war
        for key, state in list(world.diplomatic_states.items()):
            if state == "WAR" and "France" in key.split("|"):
                world.diplomatic_states[key] = "PEACE"
        world.war_exhaustion["France"] = 20
        process_coalition_turn(world)
        assert world.war_exhaustion.get("France", 0) == 15

    def test_battle_arm_france_loses_as_defender(self, world):
        """The missing loser-accrues arm: an AI attacker beating a French
        defender now adds casualty-scaled WE to France (was: nothing — the
        exact July-17 playtest shape)."""
        from backend.commands.executor import CommandExecutor
        combat = CommandExecutor()._combat
        french = next(m for m in world.marshals.values() if m.nation == "France")
        austrian = next(m for m in world.marshals.values() if m.nation == "Austria")
        _hostile_pair(world, "France", "Austria")
        world.war_exhaustion.pop("France", None)
        ctx = {
            "attacker": austrian,
            "defender": french,
            "defender_nation": "France",
            "battle_region": french.location,
            "outcome": "attacker_victory",
            "attacker_won": True,
            "defender_won": False,
            "attacker_casualties": 2000,
            "defender_casualties": 9000,
            "pre_battle_attacker_strength": austrian.strength,
            "pre_battle_defender_strength": french.strength,
            "battle_result": None,
            "conquered": False,
            "skip_log_battle_event": True,
            "skip_idle_reset": True,
            "skip_cannon_fire_record": True,
            "skip_diplo_record": True,
            "skip_war_damage": True,
            "skip_intel_update": True,
            "skip_coordination_clear": True,
            "skip_relationships": True,
            "skip_last_combat_result": True,
            "skip_exhaustion": True,
        }
        combat._post_combat_pipeline(ctx, world)
        assert world.war_exhaustion.get("France", 0) == 9  # 9000 // 1000


# ═══════════════ Review-round fixes (find→verify July 17) ══════════════════


class TestReviewRoundFixes:
    def test_legacy_world_france_we_tick_gated(self):
        """Finding #1 (HIGH, N1): the legacy fixture world BOOTS at war — an
        ungated France WE tick drifted its pinned economy (WE → infantry
        regen). The tick is Europe-gated; legacy France never accrues."""
        from backend.game_logic.coalition import process_coalition_turn
        legacy = WorldState()
        legacy.war_exhaustion.pop("France", None)
        process_coalition_turn(legacy)
        process_coalition_turn(legacy)
        assert "France" not in legacy.war_exhaustion
        assert legacy.get_manpower_regen_rates("France")["infantry"] == 2500

    def test_europe_france_we_tick_runs(self, world):
        from backend.game_logic.coalition import process_coalition_turn
        _hostile_pair(world, "France", "Austria")
        world.war_exhaustion.pop("France", None)
        process_coalition_turn(world)
        assert world.war_exhaustion.get("France", 0) == 8

    def test_elimination_sheds_war_exhaustion(self, world):
        """Finding #2: elimination ends wars without cleanup_war_end — the
        R49 mirror in _eliminate_nation sheds WE for nations left with no
        remaining wars."""
        for key, state in list(world.diplomatic_states.items()):
            if state == "WAR" and "France" in key.split("|"):
                world.diplomatic_states[key] = "PEACE"
        _hostile_pair(world, "France", "Austria")
        world.war_exhaustion["France"] = 120
        world._eliminate_nation("Austria")
        assert world.war_exhaustion.get("France", 0) == 0

    def test_we_infantry_regen_coupling_recorded_as_intended(self, world):
        """Finding #3, RECORDED AS INTENDED (memo §6): the pre-existing WE →
        infantry-regen penalty (100 WE = halved, 200 = the 1000 floor) now
        reaches France — the manpower half of war-weariness, symmetric with
        the AI nations that always had it, self-healing at peace."""
        base = world.get_manpower_regen_rates("France")["infantry"]
        world.war_exhaustion["France"] = 200
        floored = world.get_manpower_regen_rates("France")["infantry"]
        assert floored == 1000
        assert floored < base

    def test_vassal_tribute_skips_disrupted_provinces(self, world):
        """Finding #9: the lord cannot tithe revenues the invader is eating —
        both the tribute processor and the ledger mirror skip disrupted
        vassal provinces."""
        vassal_name = next(
            (v for v, s in world.vassals.items() if s.get("lord") == "France"),
            None)
        if vassal_name is None:
            pytest.skip("no French vassal on this boot")
        target = None
        for name in world.get_nation_regions(vassal_name):
            if world.regions[name].get_effective_income() > 0:
                target = world.regions[name]
                break
        if target is None:
            pytest.skip("vassal has no income-bearing province")
        before = _build_economy(world, "France")["vassal_tribute"]
        assert before > 0
        _hostile_pair(world, vassal_name, "Austria")
        enemy = next(m for m in world.marshals.values()
                     if m.nation == "Austria"
                     and m.strength >= DISRUPTION_MIN_STRENGTH)
        _park(world, enemy.name, target.name)
        after = _build_economy(world, "France")["vassal_tribute"]
        expected_drop = int(
            target.get_effective_income()
            * world.vassals[vassal_name].get("tribute_rate", 0.5))
        assert after <= before - expected_drop + 1  # int-rounding tolerance

    def test_main_gd_turn_banner_renders_new_components(self):
        """Finding #6b: the Godot turn banner must render the two new Net
        components (mirrors the NET_GOLD_COMPONENTS gd-render guard)."""
        gd = (Path(__file__).resolve().parents[1] / "godot-client"
              / "project-sovereign" / "scripts" / "main.gd"
              ).read_text(encoding="utf-8")
        assert '"contributions"' in gd
        # EB-1 re-bless: the banner renders the Charges of Empire (the
        # absorbed war_effort key must be GONE, not merely joined)
        assert '"state_charges"' in gd
        assert '"war_effort"' not in gd
        # EB-5a/EB-2: the positive components render too
        assert '"requisitions"' in gd
        assert '"overseas"' in gd

    def test_auto_advance_banner_includes_new_components(self):
        """Finding #6a: the executor auto-advance turn_end net must subtract
        contributions/state_charges/infrastructure (source-level pin — the
        banner previously overstated Net on every wartime last-AP advance).
        EB-1 re-bless: war_effort_val became state_charges_val."""
        src = (Path(__file__).resolve().parents[1] / "backend" / "commands"
               / "executor.py").read_text(encoding="utf-8")
        anchor = src.index('"type": "turn_end"')
        window = src[max(0, anchor - 3000):anchor]
        assert "contributions_val" in window
        assert "state_charges_val" in window
        assert "infrastructure_val" in window
        assert "war_effort_val" not in window


# ═══════════════════════ EC-W3: The Butcher's Bill ══════════════════════════


class TestMateriel:
    def test_both_sides_billed(self, world):
        from backend.commands.executor import CommandExecutor
        combat = CommandExecutor()._combat
        french = next(m for m in world.marshals.values() if m.nation == "France")
        austrian = next(m for m in world.marshals.values() if m.nation == "Austria")
        world.nation_gold["France"] = 5000
        world.nation_gold["Austria"] = 5000
        ctx = {
            "attacker": french,
            "defender": austrian,
            "defender_nation": "Austria",
            "battle_region": austrian.location,
            "outcome": "attacker_victory",
            "attacker_won": True,
            "defender_won": False,
            "attacker_casualties": 4000,
            "defender_casualties": 8000,
            "pre_battle_attacker_strength": french.strength,
            "pre_battle_defender_strength": austrian.strength,
            "battle_result": None,
            "conquered": False,
            "skip_log_battle_event": True,
            "skip_idle_reset": True,
            "skip_cannon_fire_record": True,
            "skip_diplo_record": True,
            "skip_war_damage": True,
            "skip_intel_update": True,
            "skip_coordination_clear": True,
            "skip_relationships": True,
            "skip_last_combat_result": True,
            "skip_exhaustion": True,
        }
        out = combat._post_combat_pipeline(ctx, world)
        assert world.nation_gold["France"] == 5000 - int(4000 * MATERIEL_RATE)
        assert world.nation_gold["Austria"] == 5000 - int(8000 * MATERIEL_RATE)
        assert "Materiel" in out.get("materiel_msg", "")

    def test_rate_hierarchy_below_war_recruit(self):
        """Replacing men must cost more than replacing kit: materiel per
        1,000 (50g) < war-priced infantry recruit per 1,000 (200g/10k ×3 =
        60g)."""
        materiel_per_1k = MATERIEL_RATE * 1000
        war_recruit_per_1k = 200 / 10 * 3
        assert materiel_per_1k < war_recruit_per_1k

    def test_legacy_world_not_billed(self):
        """N1: the legacy fixture world's combat gold pins stand."""
        legacy = WorldState()
        from backend.commands.executor import CommandExecutor
        combat = CommandExecutor()._combat
        french = next(m for m in legacy.marshals.values() if m.nation == "France")
        enemy = next(m for m in legacy.marshals.values() if m.nation != "France")
        legacy.nation_gold["France"] = 5000
        ctx = {
            "attacker": french,
            "defender": enemy,
            "defender_nation": enemy.nation,
            "battle_region": enemy.location,
            "outcome": "attacker_victory",
            "attacker_won": True,
            "defender_won": False,
            "attacker_casualties": 4000,
            "defender_casualties": 8000,
            "pre_battle_attacker_strength": french.strength,
            "pre_battle_defender_strength": enemy.strength,
            "battle_result": None,
            "conquered": False,
            "skip_log_battle_event": True,
            "skip_idle_reset": True,
            "skip_cannon_fire_record": True,
            "skip_diplo_record": True,
            "skip_war_damage": True,
            "skip_intel_update": True,
            "skip_coordination_clear": True,
            "skip_relationships": True,
            "skip_last_combat_result": True,
            "skip_exhaustion": True,
        }
        combat._post_combat_pipeline(ctx, legacy)
        assert legacy.nation_gold["France"] == 5000


# ═══════════════════════ EC-W4 (player-ask fraction) ════════════════════════


class TestPlayerAskScaling:
    def test_fraction_constant_sane(self):
        assert 0.0 < CONCESSION_BASELINE_TREASURY_FRACTION <= 0.5


# ═══════════════════════ EC-W5: fix-in-passing pair ═════════════════════════


class TestPlunderParity:
    def test_single_source(self):
        from backend.commands.combat_executor import CombatExecutor
        assert CombatExecutor.PLUNDER_INCOME_MULTIPLIER == PLUNDER_INCOME_MULTIPLIER

    def test_ai_plunder_pays_player_rate(self, world):
        """GR5: the AI personality auto-plunder (an aggressive enemy marshal
        capturing a province) pays the same base-income multiple as the
        player's plunder choice (was ×1.0 — a silent AI discount).

        IGR-E addendum: this test used to set `personality_type`, an
        attribute Marshal does not have, which is what let it pass while the
        production branch it claims to cover was dead code. It now sets the
        real `personality`, so it actually exercises the AI plunder path.
        """
        fr_region = None
        for name in world.get_nation_regions("France"):
            if not world.regions[name].is_capital:
                fr_region = world.regions[name]
                break
        assert fr_region is not None
        austrian = next(m for m in world.marshals.values() if m.nation == "Austria")
        austrian.personality = "aggressive"
        at_gold_before = int(world.nation_gold.get("Austria", 0))
        at_base = fr_region.income_value
        world._apply_occupation_capture_effects(austrian, fr_region.name)
        assert world.nation_gold["Austria"] == at_gold_before + int(
            at_base * PLUNDER_INCOME_MULTIPLIER)


class TestEconomyReportNetFix:
    def test_report_net_includes_infrastructure(self, world):
        """EC-W5b: the treasury report's net must equal the applied net when
        structures exist (infrastructure was missing from the report).

        RE-PINNED CONSCIOUSLY by CA8-10 (creative audit, Aug 4 2026). This
        test used to hand-recompute the expected net from a SUBSET of the
        streams — which is the exact hand-assembly that let admiralty,
        blockade, trade income, treaty gold and vassal tribute go missing
        and made the two income screens disagree by 124%. Re-deriving the
        same subset in the test could only ever confirm the report matched
        its own omissions.

        The invariant EC-W5b actually wanted is that the report agrees with
        the surface whose Net is pinned to the signed sum of its declared
        components (`NET_GOLD_COMPONENTS`). That is what is asserted now,
        and it holds for every future stream without editing this test.
        """
        from backend.commands.executor import CommandExecutor
        from backend.game_logic.ledger import _build_economy
        region = _french_region(world)
        region.buildings.append({"type": "supply_depot", "damaged": False})
        executor = CommandExecutor()
        game_state = {"world": world}
        result = executor._economy._execute_economy(
            {"action": "economy"}, game_state)
        event = next(e for e in result["events"] if e["type"] == "economy_report")
        assert event["infrastructure"] > 0
        assert event["net"] == int(_build_economy(world, "France")["net"])


# ═══════════════════════ The playtest-shape acceptance ══════════════════════


class TestCurveInverts:
    def test_losing_war_shape_pressures_net(self, world):
        """The acceptance shape: stage turn-17 France (rich chest, high WE,
        Britain on home soil) and assert the war-coupled net is materially
        below the uncoupled net — the defect table's '+3,369 while losing'
        can no longer happen."""
        _hostile_pair(world, "France", "Britain")
        uncoupled = _build_economy(world, "France")["net"]
        world.nation_gold["France"] = 51000
        world.war_exhaustion["France"] = 150
        moore = next((m for m in world.marshals.values()
                      if m.nation == "Britain"
                      and m.strength >= DISRUPTION_MIN_STRENGTH), None)
        if moore is not None:
            region = _french_region(world)
            _park(world, moore.name, region.name)
        coupled = _build_economy(world, "France")["net"]
        drain = 51000 * 150 // WAR_EFFORT_DIVISOR  # 3,060
        assert coupled <= uncoupled - drain + 100  # presence term on top
        assert coupled < 1500, (
            f"a France losing at home with a fat chest must feel pressure; "
            f"net={coupled}")
