"""ES-3 super-linear per-corps upkeep + force limit — S5 (Track 2, spec §0.6.3).

Blessed E3 numbers (§0.6.7): base rate 5→8 g per 1,000 troops; per-nation
force limit = 60,000 + 2,500 × controlled regions; over-limit ladder 1.5×
(surcharge +4/1,000) then 2.0× above 150% of the limit (surcharge +8/1,000),
charged as MARGINAL bands on total nation strength. E6: bankruptcy mercy
halves base AND surcharge (`total == base + surcharge` always holds, so the
split ledger lines reconcile to Net by construction).

EUROPE-SCOPED: the legacy 19-region world is a pinned test fixture and keeps
the flat 5/1,000 with no force limit (the N1 pattern — its 865g France total
is load-bearing across the suite; see test_economy_upkeep_bankruptcy.py).

Threading pins (the 6 `calculate_turn_upkeep` callers + ledger + dispatch):
every caller reads `upkeep_data["total"]`, which already folds the surcharge,
so Net math is consistent everywhere; the ledger splits base/surcharge into
separate rendered lines (§3 breakdown-visible), the dispatch situation and
the treasury report carry the over-limit detail, and both turn-end financial
messages annotate the upkeep figure.

Two-sided turn-1 anchor (real 1805 scenario, measured July 9, 2026): every
armed nation stays net-positive under ES-3 alone (min: Naples +356); France
(189k army vs 130k limit) pays a 236g surcharge and absorbs ~47% of gross —
deliberately below the E1 55–70% band, which is measured against the FULL
stacked set (ES-2+ES-3+ES-7) by the S7 band test, the band's tuning
instrument. Austria (126k vs 77.5k limit) reaches the severe 2.0× band.
"""

import inspect
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic.dispatch import _build_situation
from backend.game_logic.ledger import _build_economy
from backend.models.marshal import Marshal
from backend.models.world_state import (
    EUROPE_UPKEEP_RATE,
    FORCE_LIMIT_BASE,
    FORCE_LIMIT_PER_REGION,
    GRANDE_ARMEE_RATE,
    GRANDE_ARMEE_THRESHOLD,
    LEGACY_UPKEEP_RATE,
    WorldState,
)

SCENARIO_PATH = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"
)

_LEDGER_GD = (
    Path(__file__).resolve().parents[1]
    / "godot-client" / "project-sovereign" / "scripts" / "strategic_ledger.gd"
)


@pytest.fixture
def europe():
    """Bare Europe flag world (126 provinces, no marshals)."""
    return WorldState(player_nation="France", sovereign_map="europe")


@pytest.fixture
def legacy():
    return WorldState(player_nation="France")


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


def _copy(world):
    return WorldState.from_dict(world.to_dict())


def _solo_army(world, strength, nation="France"):
    """Give `nation` exactly one marshal of `strength` (bare-world helper)."""
    for name in [n for n, m in world.marshals.items() if m.nation == nation]:
        del world.marshals[name]
    location = world.get_nation_regions(nation)[0]
    world.marshals["TestCorps"] = Marshal(
        name="TestCorps", location=location, strength=strength,
        personality="cautious", nation=nation,
    )


# ══════════════════════════ force limit ══════════════════════════


class TestForceLimit:
    def test_legacy_has_no_force_limit(self, legacy):
        assert legacy.get_force_limit("France") is None

    def test_europe_limit_scales_with_regions(self, europe):
        regions = len(europe.get_nation_regions("France"))
        expected = FORCE_LIMIT_BASE + FORCE_LIMIT_PER_REGION * regions
        assert europe.get_force_limit("France") == expected

    def test_1805_france_limit_is_130k(self, world1805):
        """28 starting provinces → 60,000 + 28×2,500 = 130,000."""
        assert len(world1805.get_nation_regions("France")) == 28
        assert world1805.get_force_limit("France") == 130000

    def test_limit_rides_cached_region_index(self):
        """GR8: the limit is computed per nation per income phase — it must
        read the cached get_nation_regions index, never scan regions."""
        src = inspect.getsource(WorldState.get_force_limit)
        assert "get_nation_regions" in src
        assert "regions.values()" not in src


# ══════════════════ formula — europe (rate 8 + ladder) ══════════════════


class TestEuropeUpkeepFormula:
    def test_rate_is_8_per_1000(self, europe):
        _solo_army(europe, 30000)
        result = europe.calculate_turn_upkeep("France")
        assert result["base"] == 30 * EUROPE_UPKEEP_RATE == 240
        assert result["surcharge"] == 0
        assert result["total"] == 240

    def test_integer_division_floors(self, europe):
        _solo_army(europe, 28500)
        assert europe.calculate_turn_upkeep("France")["total"] == 28 * 8

    def test_at_exactly_the_limit_no_surcharge(self, europe):
        limit = europe.get_force_limit("France")
        _solo_army(europe, limit)
        result = europe.calculate_turn_upkeep("France")
        assert result["surcharge"] == 0
        assert result["over_limit"] is False

    def test_just_over_the_limit_pays_1_5x_band(self, europe):
        """1,500 over → (1500//1000) × 4 = 4g surcharge (marginal, not a
        cliff — only the excess pays the higher rate)."""
        limit = europe.get_force_limit("France")
        _solo_army(europe, limit + 1500)
        result = europe.calculate_turn_upkeep("France")
        assert result["surcharge"] == 4
        assert result["over_limit"] is True
        assert result["total"] == result["base"] + 4

    def test_severe_band_pays_2x_above_150pct(self, europe):
        """At 2× the limit: band up to 150% pays +4/1,000, the rest +8/1,000.
        limit L → band1 = L/2 → (L/2)//1000 × 4; band2 = L/2 → ×8."""
        limit = europe.get_force_limit("France")
        army = limit * 2
        _solo_army(europe, army)
        result = europe.calculate_turn_upkeep("France")
        half = limit // 2
        es3 = (half // 1000) * 4 + (half // 1000) * 8
        # EC-U3: the Grande Armée premium stacks on top of the ES-3 bands for
        # an army above the absolute threshold (limit*2 is well past it here).
        grande = max(0, (army - GRANDE_ARMEE_THRESHOLD) // 1000) * GRANDE_ARMEE_RATE
        expected = es3 + grande
        assert result["surcharge"] == expected
        assert result["grande_armee"] == grande
        assert result["total"] == result["base"] + expected

    def test_surcharge_sums_across_marshals(self, europe):
        """The limit binds on TOTAL nation strength, not per marshal."""
        limit = europe.get_force_limit("France")
        _solo_army(europe, limit)  # one corps exactly at the limit
        location = europe.get_nation_regions("France")[0]
        europe.marshals["SecondCorps"] = Marshal(
            name="SecondCorps", location=location, strength=10000,
            personality="cautious", nation="France",
        )
        result = europe.calculate_turn_upkeep("France")
        assert result["total_strength"] == limit + 10000
        assert result["surcharge"] == 10 * 4

    def test_total_always_equals_base_plus_surcharge(self, europe):
        limit = europe.get_force_limit("France")
        for strength in (500, 30000, limit, limit + 1, limit * 2, limit * 3):
            _solo_army(europe, strength)
            result = europe.calculate_turn_upkeep("France")
            assert result["total"] == result["base"] + result["surcharge"]


# ══════════════════════ E6 — bankruptcy mercy ══════════════════════


class TestMercyCoversSurcharge:
    def test_mercy_halves_base_and_surcharge(self, europe):
        """E6 (blessed): the mercy halving extends to the ES-3 surcharge.
        Both rates are even, so halving each part is exact and
        total == base + surcharge still holds."""
        limit = europe.get_force_limit("France")
        _solo_army(europe, limit * 2)
        full = europe.calculate_turn_upkeep("France")
        europe.nation_bankruptcy_turns["France"] = 1
        merciful = europe.calculate_turn_upkeep("France")
        assert merciful["halved"] is True
        assert merciful["base"] == full["base"] // 2
        assert merciful["surcharge"] == full["surcharge"] // 2
        assert merciful["total"] == merciful["base"] + merciful["surcharge"]

    def test_legacy_mercy_unchanged(self, legacy):
        """Legacy fixture: 865 → 432, no surcharge involved."""
        legacy.nation_bankruptcy_turns["France"] = 1
        result = legacy.calculate_turn_upkeep("France")
        assert result["total"] == 865 // 2
        assert result["surcharge"] == 0


# ══════════════════ legacy fixture world unchanged ══════════════════


class TestLegacyUnchanged:
    def test_legacy_rate_still_5(self, legacy):
        for m in legacy.marshals.values():
            if m.nation == "France":
                m.strength = 0
        legacy.get_marshal("Ney").strength = 30000
        result = legacy.calculate_turn_upkeep("France")
        assert result["total"] == 30 * LEGACY_UPKEEP_RATE == 150

    def test_legacy_huge_army_pays_no_surcharge(self, legacy):
        for m in legacy.marshals.values():
            if m.nation == "France":
                m.strength = 300000
        result = legacy.calculate_turn_upkeep("France")
        assert result["surcharge"] == 0
        assert result["force_limit"] is None
        assert result["over_limit"] is False


# ═══════════════ threading — ledger / dispatch / report ═══════════════


class TestThreading:
    def test_ledger_splits_upkeep_and_reconciles(self, world1805):
        """§3 invariant with a LIVE surcharge: 1805 France starts over its
        force limit, so the surcharge line is non-vacuously exercised."""
        econ = _build_economy(world1805, "France")
        assert econ["upkeep_surcharge"] > 0
        assert econ["upkeep_base"] + econ["upkeep_surcharge"] == econ["upkeep"]
        signed_sum = (
            econ["income"] + econ["trade_income"] + econ["admin_bonus"]
            + econ["treaty_gold"] + econ["vassal_tribute"]
            + econ["settlement_gold"] - econ["upkeep_base"]
            - econ["upkeep_surcharge"]
        )
        assert signed_sum == econ["net"]

    def test_ledger_gd_renders_surcharge_line(self):
        src = _LEDGER_GD.read_text(encoding="utf-8")
        assert '"upkeep_base"' in src
        assert '"upkeep_surcharge"' in src
        assert "Over-limit surcharge" in src

    def test_dispatch_situation_carries_over_limit_detail(self, world1805):
        situation = _build_situation(world1805, "France")
        upkeep_data = world1805.calculate_turn_upkeep("France")
        assert situation["upkeep_surcharge"] == upkeep_data["surcharge"]
        assert situation["force_limit"] == upkeep_data["force_limit"]
        assert situation["over_force_limit"] is True

    def test_treasury_report_shows_over_limit_line(self, world1805):
        world = _copy(world1805)
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "economy"}}, {"world": world}
        )
        assert result["success"] is True
        assert "Over force limit" in result["message"]
        assert "surcharge" in result["message"]

    def test_end_turn_message_annotates_surcharge(self, world1805):
        """The end-turn financial summary (meta_executor) annotates the
        upkeep figure — the surcharge is visible on the surface players
        read every single turn."""
        world = _copy(world1805)
        executor = CommandExecutor()
        result = executor.execute(
            {"command": {"action": "end_turn"}}, {"world": world}
        )
        assert "over-limit" in result.get("message", "")

    def test_ai_nations_pay_through_the_same_seam(self, world1805):
        """GR5: Austria starts in the severe band — its income phase pays
        the surcharged total with zero AI-only code."""
        world = _copy(world1805)
        upkeep_data = world.calculate_turn_upkeep("Austria")
        assert upkeep_data["surcharge"] > 0
        gold_before = world.nation_gold["Austria"]
        result = world.process_income_phase("Austria")
        assert result["upkeep"] == upkeep_data["total"]
        assert world.nation_gold["Austria"] == gold_before + result["net"]


# ═══════════════ two-sided turn-1 anchor (1805 scenario) ═══════════════


class TestTurn1Anchor:
    """Solvency floor for ES-3 ALONE (the full E1 band assertion lands with
    the S7 stacked test). Exact figures are pins of the blessed constants
    against the authored 1805 armies — a conscious re-pin is required if
    either changes."""

    def test_every_armed_nation_stays_net_positive(self, world1805):
        from backend.game_logic.diplomacy import calculate_trade_income
        trade = calculate_trade_income(world1805)
        for nation in world1805.get_active_nations():
            upkeep_data = world1805.calculate_turn_upkeep(nation)
            if upkeep_data["total_strength"] == 0:
                continue
            income = world1805.calculate_turn_income(nation)["income"]
            net = income + trade.get(nation, 0) - upkeep_data["total"]
            assert net > 0, (
                f"{nation} goes net-negative under ES-3 alone "
                f"(income {income} + trade {trade.get(nation, 0)} "
                f"- upkeep {upkeep_data['total']} = {net}) — "
                "no-death-spiral floor violated (E1)."
            )

    def test_france_pays_the_blessed_surcharge(self, world1805):
        """189k army vs 130k limit, below the 195k severe threshold: the ES-3
        over-limit portion is 59,000 over → 59 × 4 = 236g. EC-U3 then stacks
        the Grande Armée premium — 49,000 above the 140k absolute threshold →
        49 × 18 = 882g — for a total surcharge of 1,118g (the two components
        reported separately for legibility)."""
        upkeep_data = world1805.calculate_turn_upkeep("France")
        assert upkeep_data["total_strength"] == 189000
        assert upkeep_data["force_limit"] == 130000
        grande = ((189000 - GRANDE_ARMEE_THRESHOLD) // 1000) * GRANDE_ARMEE_RATE
        assert grande == 882
        assert upkeep_data["grande_armee"] == 882
        assert upkeep_data["surcharge"] == 236 + 882  # ES-3 236 + Grande Armée 882
        assert upkeep_data["total"] == 1512 + 236 + 882

    def test_austria_reaches_the_severe_band(self, world1805):
        """126k army vs 77.5k limit (150% = 116,250): band1 38,750 → 152g,
        band2 9,750 → 72g. The ladder's second rung is live at boot."""
        upkeep_data = world1805.calculate_turn_upkeep("Austria")
        assert upkeep_data["force_limit"] == 77500
        assert upkeep_data["surcharge"] == 152 + 72

    def test_france_absorption_below_the_stacked_band(self, world1805):
        """ES-3 ALONE (the force-limit upkeep, EXCLUDING the EC-U3 Grande
        Armée premium) absorbs ~47% of France's gross — deliberately BELOW
        the 55–70% E1 band. EC-U3 is a separate layer (its own `grande_armee`
        sub-line), so this ES-3-only measure subtracts it; the stacked band
        (ES-2+ES-3+ES-7+EC-U3) is the E1 test's instrument."""
        from backend.game_logic.diplomacy import calculate_trade_income
        up = world1805.calculate_turn_upkeep("France")
        es3_only = up["total"] - up["grande_armee"]  # exclude the EC-U3 layer
        gross = (
            world1805.calculate_turn_income("France")["income"]
            + calculate_trade_income(world1805).get("France", 0)
        )
        absorption = es3_only / gross
        assert 0.40 <= absorption <= 0.55
