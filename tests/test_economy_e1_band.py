"""THE stacked two-sided E1 band test — Track-2 acceptance (S7, §0.6.7 E1).

ONE test file measures the anti-snowball band with ES-2 (occupation) + ES-3
(super-linear upkeep + force limit) + ES-7 (estate redirect) STACKED, on the
real 1805 campaign, from BOTH sides (France AND a minor AI) — the tuning
instrument the EC-2 gate named as the slice acceptance.

Absorption metric: drains / gross, where
  drains = occupation + dotation_skim + upkeep_base + upkeep_surcharge
  gross  = region income + trade income + admin bonus + incoming treaty gold
           + vassal tribute + incoming settlement gold
(the TOTAL economy including the diplomatic layer, per E1).

═══ MEASURED ANCHORS (EC-U3 re-tune, July 14, 2026) ═══

  turn-1 France:                     absorption 55.5%  net +2,107
  doubled empire, fresh (hostile):   absorption 84%+   (heavily absorbed)
  doubled empire, steady state
    (pacified + doubled army
     + 3 endowed marshals):          absorption 100%+  edge of sustainability
  boot solvency: every armed nation net-positive; Austria +18 is STILL the
    BINDING constraint (126k army vs 77.5k force limit at boot) — and STILL
    byte-unchanged, because EC-U3's Grande Armée surcharge is keyed on
    ABSOLUTE strength above 140k, which at boot ONLY France (189k) crosses.

  EC-U3 (Combat Overhaul Phase 4, Sweep-3 follow-up) is what moved turn-1
  France from the old measured 36.9% into the EC-2 aspirational 55–70% band:
  a premium upkeep rate (GRANDE_ARMEE_RATE g/1,000 above GRANDE_ARMEE_THRESHOLD)
  on France's uniquely-huge army, modelling the ruinous diseconomies of scale
  a supermassive standing army carried. It cuts France's homeland surplus ~29%
  and makes a FULLY-doubled army the edge of sustainability (not a spiral).

═══ THE RECORDED TENSION (band retune input for the user) ═══

The blessed E1 turn-1 anchor (~55-70% of TOTAL net) is NOT simultaneously
satisfiable with the harder blessed invariant "every armed nation
net-positive at boot" at the blessed E3 constants: reaching 55% at turn 1
needs upkeep rate ~12, which drives Austria (+18 at rate 8) hundreds of
gold negative at boot — a permanent-bankruptcy major in the no-lose
sandbox. The tuning instrument therefore pins the MEASURED stacked shape:
the band's SPIRIT lands at the anchors conquest actually creates (fresh
conquest ~84% absorbed — "digest before you bite" at scale; steady-state
doubled empire ~55%, inside the blessed band; doubled empire yields FAR
less than doubled net). The turn-1 gross-absorption number itself (~37%)
is recorded as below the aspirational band, bounded here, and flagged in
ECONOMY_REVISIT_SPEC §0.6.3 (Track-2 S7 note) for the next tuning gate.
Re-pinning these ranges after a user-blessed retune is a band retune (no
new gate); changing the SHAPE is not.
"""

from pathlib import Path

import pytest

from backend.game_logic.dotation import list_eligible_estates
from backend.game_logic.ledger import _build_economy
from backend.models.world_state import WorldState

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _absorption(world, nation):
    """(drains, gross, absorption, net) over the TOTAL economy (E1)."""
    e = _build_economy(world, nation)
    gross = (e["income"] + e["trade_income"] + e["admin_bonus"]
             + max(0, e["treaty_gold"]) + e["vassal_tribute"]
             + max(0, e["settlement_gold"]))
    drains = (e["occupation"] + e["dotation_skim"] + e["upkeep_base"]
              + e["upkeep_surcharge"])
    return drains, gross, (drains / gross if gross else 0.0), e["net"]


def _double_empire(world, nation="France", stability=10):
    """Flip `nation`-starting-count foreign non-capital provinces to it."""
    target_count = len(world.nation_starting_regions.get(nation, []))
    homeland = set(world.nation_starting_regions.get(nation, []))
    flipped = 0
    for region in world.regions.values():
        if flipped >= target_count:
            break
        if (region.controller and region.controller != nation
                and not region.is_capital and region.name not in homeland):
            region.controller = nation
            region.stability = stability
            flipped += 1
    world.invalidate_active_nations_cache()
    return flipped


def _endow_marshals(world, nation, count=3):
    """Give `count` marshals capped expectation + one rich estate each."""
    marshals = [m for m in world.marshals.values()
                if m.nation == nation and m.strength > 0][:count]
    for m in marshals:
        m.battles_won = 10  # capped expectation
        eligible = list_eligible_estates(world, nation)
        if eligible:
            m.dotation_regions.append(eligible[0])
    return marshals


class TestTurnOneAnchor:
    def test_france_turn_one_absorption_bounded(self, world):
        """EC-U3 (Sweep-3 follow-up) REACHED the aspirational anchor. The
        Grande Armée surcharge (a premium on France's uniquely-huge 189k army,
        above the 140k absolute threshold) lifts France's turn-1 stacked
        absorption from the old measured 36.9% to ~55.5% — inside the original
        EC-2 aspirational 55–70% band that rate-8 alone could not reach
        without breaking Austria's +18 boot solvency (EC-U3 touches ONLY
        France at boot, so Austria is byte-unchanged). Bounded so drift is a
        conscious retune: below 0.50 the Grande Armée bite weakened; above
        0.62 the rate was pushed past the measured sweet spot (re-verify the
        doubled-empire steady state stays out of a death-spiral)."""
        drains, gross, absorption, net = _absorption(world, "France")
        assert 0.50 <= absorption <= 0.62, (
            f"France turn-1 stacked absorption {absorption:.1%} left the "
            f"measured range (drains={drains} gross={gross})")
        assert net > 0

    def test_every_armed_nation_net_positive_at_boot(self, world):
        """The BINDING two-sided constraint (Austria +18): any across-the-
        board drain increase breaks this before it reaches the aspirational
        turn-1 band — the no-lose sandbox must not boot a major into
        permanent bankruptcy."""
        for nation in world.get_active_nations():
            income = world.calculate_turn_income(nation)
            upkeep = world.calculate_turn_upkeep(nation)
            net = (income["income"] - income["occupation"]
                   - income["dotation_skim"] - upkeep["total"])
            assert net > 0, f"{nation} net-negative at boot ({net})"

    def test_boot_has_no_occupation_or_dotation(self, world):
        """At turn 1 only ES-3 bites (amendment-3 rationale): occupation and
        dotations are structurally 0 at boot — homeland IS starting control
        and no estates exist yet."""
        for nation in world.get_active_nations():
            income = world.calculate_turn_income(nation)
            assert income["occupation"] == 0
            assert income["dotation_skim"] == 0


class TestDoubledEmpire:
    def test_fresh_conquest_heavily_absorbed(self, world):
        """Doubled empire on fresh hostile soil: ~84% of the whole economy
        absorbed — expansion is digested, not banked (anti-snowball's
        transitional arm)."""
        _double_empire(world, stability=10)
        drains, gross, absorption, net = _absorption(world, "France")
        assert absorption >= 0.70, (
            f"fresh doubled-empire absorption {absorption:.1%} — the "
            f"digest-before-you-bite pressure collapsed")
        # ...but never unrecoverable: even here France stays solvent
        assert net > -world.nation_gold.get("France", 0)

    def test_steady_state_lands_in_blessed_band(self, world):
        """EC-U3 sharpened the anti-snowball at the top end. Doubling the
        empire AND fielding a fully-doubled army (~378k) now runs the Grande
        Armée surcharge hard — absorption climbs past 0.70 (from the old
        54.5%) and the empire sits at the EDGE of sustainability (near
        break-even). This is the intended lesson: grow your army with your
        ECONOMY, not your map. Crucially it is NOT a death-spiral — over six
        turns the bankruptcy counter never reaches the desertion tier (3) and
        the treasury holds positive (the mercy + income growth arrest it)."""
        _double_empire(world, stability=100)
        for m in world.marshals.values():
            if m.nation == "France":
                m.strength *= 2
        _endow_marshals(world, "France", count=3)
        drains, gross, absorption, net = _absorption(world, "France")
        # a fully-doubled army is now HEAVILY absorbed (the sharpened
        # anti-snowball), not the comfortable ~55% of the pre-EC-U3 world.
        # Bounded on BOTH sides (the name is historical — it now asserts the
        # heavily-absorbed edge, not the old 55-70% band): below 0.70 the
        # Grande Armée surcharge stopped biting; above 1.30 the rate was
        # over-tuned past the edge of sustainability into a hard deficit even
        # the 6-turn no-spiral check below could miss on turn 1.
        assert 0.70 <= absorption <= 1.30, (
            f"steady-state doubled-army absorption {absorption:.1%} left the "
            f"measured edge-of-sustainability range (drains={drains} gross={gross})")
        # ...but sustainable: no death-spiral, treasury does not collapse
        for _ in range(6):
            world.advance_turn()
        assert world.nation_bankruptcy_turns.get("France", 0) < 3, (
            "doubled-army France death-spiralled under the Grande Armée surcharge")
        assert world.nation_gold["France"] > 0
        # the stack is genuinely three-drain here
        econ = _build_economy(world, "France")
        assert econ["occupation"] > 0
        assert econ["dotation_skim"] > 0
        assert econ["upkeep_surcharge"] > 0

    def test_doubled_empire_yields_less_than_doubled_net(self, world):
        """The anti-snowball core: doubling the empire must NOT double the
        net — the marginal yield of conquest is well under 100%."""
        _, _, _, net_start = _absorption(world, "France")
        _double_empire(world, stability=100)
        for m in world.marshals.values():
            if m.nation == "France":
                m.strength *= 2
        _endow_marshals(world, "France", count=3)
        _, _, _, net_doubled = _absorption(world, "France")
        assert net_doubled < 2 * net_start, (
            f"doubled empire more than doubled net "
            f"({net_start} -> {net_doubled}) — snowball")

    def test_pacification_is_the_recovery_path(self, world):
        """Never-net-negative-UNRECOVERABLE: the hostile transitional state
        recovers by pacifying — stability growth alone drops absorption and
        raises net (no seam-specific relief needed)."""
        _double_empire(world, stability=10)
        _, _, absorption_hostile, net_hostile = _absorption(world, "France")
        for _ in range(6):  # stability grows ~+5-10/turn
            world.advance_turn()
        _, _, absorption_later, net_later = _absorption(world, "France")
        assert absorption_later < absorption_hostile
        assert net_later > net_hostile


class TestMinorAISide:
    """The two-sided arm: a minor 800g AI reaches every sink through the
    SAME seams (GR5) and never death-spirals in the no-lose sandbox."""

    NATION = "Bavaria"  # 800g at boot, armed (ES-3 payer)

    def test_minor_reaches_every_stacked_sink(self, world):
        assert world.nation_gold[self.NATION] == 800
        # conquest -> occupation; endowment -> redirect; army -> upkeep
        homeland = set(world.nation_starting_regions[self.NATION])
        conquest = next(
            r for r in world.regions.values()
            if r.controller and r.controller != self.NATION
            and not r.is_capital and r.name not in homeland)
        conquest.controller = self.NATION
        conquest.stability = 10
        world.invalidate_active_nations_cache()
        marshal = next(m for m in world.marshals.values()
                       if m.nation == self.NATION and m.strength > 0)
        marshal.battles_won = 5
        # endow the conquest itself — the redirect sink
        marshal.dotation_regions.append(conquest.name)
        income = world.calculate_turn_income(self.NATION)
        upkeep = world.calculate_turn_upkeep(self.NATION)
        assert income["dotation_skim"] >= 0     # estate held (hostile: 0 eff)
        assert upkeep["total"] > 0
        # the endowed conquest pays NO occupation (amendment 4) — flip a
        # second conquest to exercise the occupation sink too
        conquest2 = next(
            r for r in world.regions.values()
            if r.controller and r.controller != self.NATION
            and not r.is_capital and r.name not in homeland)
        conquest2.controller = self.NATION
        conquest2.stability = 10
        world.invalidate_active_nations_cache()
        income = world.calculate_turn_income(self.NATION)
        assert income["occupation"] > 0

    def test_minor_never_death_spirals_under_the_stack(self, world):
        """8 turns with conquest + estate + army stacked: the minor's
        treasury never collapses into the desertion spiral (bankruptcy 3+)
        — the E6 mercy + structurally-floored redirect hold."""
        homeland = set(world.nation_starting_regions[self.NATION])
        conquest = next(
            r for r in world.regions.values()
            if r.controller and r.controller != self.NATION
            and not r.is_capital and r.name not in homeland)
        conquest.controller = self.NATION
        conquest.stability = 10
        world.invalidate_active_nations_cache()
        marshal = next(m for m in world.marshals.values()
                       if m.nation == self.NATION and m.strength > 0)
        marshal.battles_won = 5
        marshal.dotation_regions.append(conquest.name)
        start_gold = world.nation_gold[self.NATION]
        for _ in range(8):
            world.advance_turn()
            assert world.nation_bankruptcy_turns.get(self.NATION, 0) < 3, (
                f"{self.NATION} spiralled into desertion under the stack")
        assert world.nation_gold[self.NATION] > start_gold // 2

    def test_minor_marshal_erodes_and_endowment_stops_it(self, world):
        """Two-sided ES-7: the minor's OWN marshal erodes over the same
        grace/erosion curve, and a (state-level) endowment stops the bleed
        — identical machinery, no AI-only code."""
        marshal = next(m for m in world.marshals.values()
                       if m.nation == self.NATION and m.strength > 0)
        marshal.battles_won = 2  # expectation 80
        trust_start = marshal.trust.value
        for _ in range(3):
            world.advance_turn()
        assert marshal.trust.value < trust_start  # eroding
        # endow a rich-enough province -> shortfall 0 -> bleed stops
        homeland = set(world.nation_starting_regions[self.NATION])
        estate = next(
            r for r in world.regions.values()
            if r.controller and r.controller != self.NATION
            and not r.is_capital and r.name not in homeland
            and r.income_value >= 100)
        estate.controller = self.NATION
        estate.stability = 100
        world.invalidate_active_nations_cache()
        marshal.dotation_regions.append(estate.name)
        eroded = marshal.trust.value
        world.advance_turn()
        assert marshal.trust.value >= eroded  # paying stopped the bleed
