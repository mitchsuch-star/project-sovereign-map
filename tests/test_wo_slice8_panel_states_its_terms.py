"""WO slice 8 — "The Panel States Its Terms" (WEIRD_OUTCOMES_SPEC §3
slice 8: WO-D1-A + WO-D4-A + G3).

The muster preview quotes the supply arithmetic and G3's sentence; the
supply figure is single-sourced everywhere it renders; build chips state
their terms.

THE RECON CORRECTED THE CONTRACT before a line was written (the slice-6
method), and three corrections changed what got built:

1. The spec's illustrative sentence — "the whole muster standing there
   costs 11,340 a turn" at 78,676 men — is UNREACHABLE: the engine caps
   the attrition rate at 6%/turn (`min(0.06, ...)`), so that stack can
   never lose more than 4,720. The preview prints the engine's own
   number, through the engine's own arithmetic.
2. `committed_strength` ("78,676 if all march") is α-scaled,
   arrival-priced COMBAT WEIGHT, not a headcount — the supply bill
   prices BODIES: lead + joiners + same-province corps that stand there
   whether they fight or not.
3. The exclusion G3 teaches is FORTIFY (1 AP, stands until moved) —
   `restrain` is a Glorious-Charge response verb and excludes nothing,
   and HOLD's `holding_position` flag is set for literal marshals only.

The four surfaces that must show ONE figure: the muster preview, the
strategic ledger's territories rows, the map summary (which feeds both
the region panel and the map tooltip through one payload key), and the
supply-strain dispatch headline (already effective since PC15-D2). At the
1805 boot the raw-vs-effective split differed on 47 of 126 provinces —
every French province showed a figure a third below the bill.
"""

import ast
import inspect
import re
from pathlib import Path

import pytest

from backend.commands import combat_executor as combat_executor_module
from backend.commands.economy_executor import EconomyExecutor
from backend.commands.executor import CommandExecutor
from backend.game_logic.ledger import _build_territories
from backend.models import world_state as world_state_module
from backend.models.region import BUILDING_TYPES
from backend.models.world_state import WorldState, infrastructure_upkeep_rate

from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)
REGION_PANEL_GD = (
    REPO / "godot-client" / "project-sovereign" / "scripts"
    / "region_panel.gd"
)


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _legacy_pair(lead_strength=60000, joiner_strength=20000):
    """Ney at Belgium (French soil), Mack invading it, Soult adjacent."""
    ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                  strength=lead_strength,
                                  personality="aggressive")
    soult = MarshalFactory.infantry(name="Soult", location="Paris",
                                    strength=joiner_strength,
                                    personality="aggressive")
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=8000)
    world = WorldFactory.with_marshals([ney, soult, mack])
    _war(world)
    executor = CommandExecutor()
    return world, executor, ney, soult, mack


def _preview(world, executor, lead, enemy):
    return executor._combat._build_muster_preview(
        lead, enemy, world, {"world": world})


# ════════════════════════════════════════════════════════════════════════
# 1. The rate is ONE arithmetic — engine and preview both call it
# ════════════════════════════════════════════════════════════════════════

class TestRateSingleSource:

    def test_under_cap_few_corps_is_free(self):
        assert WorldState.supply_attrition_rate(30000, 60000, 2) == 0.0

    def test_under_cap_three_corps_pays_the_stacking_penalty(self):
        # The death-ball term fires with zero excess: (3-1) × 1%.
        assert WorldState.supply_attrition_rate(30000, 60000, 3) == \
            pytest.approx(0.02)

    def test_over_cap_formula_matches_the_engine_comment(self):
        # excess_ratio 0.311266... × 0.015 = 0.4669%, one corps.
        rate = WorldState.supply_attrition_rate(78676, 60000, 1)
        assert rate == pytest.approx(min(0.03, (18676 / 60000) * 0.015))

    def test_the_six_percent_ceiling_holds(self):
        # The spec's illustrative 11,340/turn at 78,676 men needs 14.4%;
        # the engine's ceiling makes 4,720 the true maximum.
        rate = WorldState.supply_attrition_rate(78676, 60000, 12)
        assert rate == pytest.approx(0.06)
        assert int(78676 * rate) == 4720

    def test_zero_cap_is_guarded(self):
        assert WorldState.supply_attrition_rate(1000, 0, 1) == 0.0

    def test_engine_calls_the_rate_and_keeps_no_copy(self):
        src = inspect.getsource(WorldState.process_supply_attrition)
        assert "supply_attrition_rate(" in src, (
            "the engine stopped calling the shared rate")
        assert "0.015" not in src and "excess_ratio" not in src, (
            "the engine grew its own copy of the rate arithmetic back")

    def test_preview_calls_the_rate_and_keeps_no_copy(self):
        src = inspect.getsource(
            combat_executor_module.CombatExecutor._build_muster_preview)
        assert "supply_attrition_rate(" in src, (
            "the preview no longer asks the engine's own arithmetic")
        assert "0.015" not in src, (
            "the preview grew a copy of the rate formula")

    def test_the_rate_lives_in_exactly_one_place(self):
        """AST census (the slice-6 method note: a grep is not a census):
        the 0.015 slope literal appears exactly once in world_state.py —
        inside `supply_attrition_rate` — and nowhere in the combat
        executor."""
        ws_src = Path(world_state_module.__file__).read_text(
            encoding="utf-8")
        tree = ast.parse(ws_src)
        hits = [n for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and n.value == 0.015]
        assert len(hits) == 1, (
            f"0.015 appears {len(hits)} times in world_state.py")
        # (combat_executor.py carries an unrelated 0.015 — the
        # retreat-return casualty rate — so the file-wide sweep scopes to
        # the two functions this slice owns, pinned above by getsource.)
        for fn in (combat_executor_module.CombatExecutor
                   ._build_muster_preview,
                   combat_executor_module.CombatExecutor
                   ._format_muster_lines):
            assert "0.015" not in inspect.getsource(fn)


# ════════════════════════════════════════════════════════════════════════
# 2. Shown = applied — the preview's price IS the engine's bill
# ════════════════════════════════════════════════════════════════════════

class TestPreviewPriceEqualsEngineBill:

    def test_over_capacity_quote_matches_the_engine_exactly(self):
        world, executor, ney, soult, mack = _legacy_pair(
            lead_strength=90000, joiner_strength=40000)
        preview = _preview(world, executor, ney, mack)
        quote = preview["supply"]
        assert quote["attrition_per_turn"] > 0, (
            "fixture must stand over capacity or the parity proves nothing")
        assert quote["bodies"] == 130000
        assert quote["corps"] == 2

        # Enact the counterfactual the sentence states: the whole muster
        # standing at Belgium, the enemy gone.
        mack.location = "Paris"
        soult.location = "Belgium"
        events = world.process_supply_attrition()
        billed = sum(e["losses"] for e in events
                     if e.get("type") == "supply_attrition"
                     and e.get("region") == "Belgium"
                     and e.get("nation") == "France")
        assert billed == quote["attrition_per_turn"], (
            f"preview quoted {quote['attrition_per_turn']}, "
            f"engine billed {billed}")

    def test_stacking_under_cap_quote_matches_the_engine(self):
        """Three corps under the cap still pay the death-ball 2% — the
        dominant term for a large muster, and the arm a naive
        excess-only quote would miss."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=10000,
                                      personality="aggressive")
        soult = MarshalFactory.infantry(name="Soult", location="Paris",
                                        strength=5000,
                                        personality="aggressive")
        murat = MarshalFactory.infantry(name="Murat", location="Paris",
                                        strength=5000,
                                        personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=4000)
        world = WorldFactory.with_marshals([ney, soult, murat, mack])
        _war(world)
        executor = CommandExecutor()
        preview = _preview(world, executor, ney, mack)
        quote = preview["supply"]
        fed = quote["fed"]
        assert quote["bodies"] == 20000 and quote["bodies"] <= fed, (
            "fixture must stand UNDER capacity for the stacking arm")
        assert quote["corps"] == 3
        expected_rate = WorldState.supply_attrition_rate(20000, fed, 3)
        assert expected_rate == pytest.approx(0.02)
        assert quote["attrition_per_turn"] == sum(
            int(s * expected_rate) for s in (10000, 5000, 5000))

        mack.location = "Paris"
        soult.location = "Belgium"
        murat.location = "Belgium"
        events = world.process_supply_attrition()
        billed = sum(e["losses"] for e in events
                     if e.get("type") == "supply_attrition"
                     and e.get("region") == "Belgium"
                     and e.get("nation") == "France")
        assert billed == quote["attrition_per_turn"]

    def test_bodies_are_raw_strengths_not_committed_weight(self):
        """The recon's correction 2: `committed_strength` is α-scaled
        arrival-priced combat weight. The bill counts mouths."""
        world, executor, ney, soult, mack = _legacy_pair()
        preview = _preview(world, executor, ney, mack)
        assert preview["supply"]["bodies"] == \
            int(ney.strength) + int(soult.strength)

    def test_a_same_province_non_joiner_still_eats(self):
        """A −2 hostile corps in the battle province brings NOTHING to
        the fighting (shares_the_field_apart) but stands there and eats.
        (Review [C-F3] precision: the quote prices the MUSTER-ALONE
        counterfactual — player-side bodies only; the engine pools
        nation-blind, so any surviving third party would raise the real
        bill above it. The parity tests enact exactly the quoted
        hypothesis.)"""
        world, executor, ney, soult, mack = _legacy_pair()
        soult.location = "Belgium"
        ney.set_relationship(soult.name, -2)
        soult.set_relationship(ney.name, -2)
        preview = _preview(world, executor, ney, mack)
        apart = next(r for r in preview["rows"]
                     if r["marshal"] == "Soult")
        assert apart["will_join"] is False, (
            "precondition: the hostile pair must not join")
        assert preview["supply"]["bodies"] == \
            int(ney.strength) + int(soult.strength)
        assert preview["supply"]["corps"] == 2

    def test_fed_figure_is_the_effective_cap(self):
        world, executor, ney, soult, mack = _legacy_pair()
        preview = _preview(world, executor, ney, mack)
        region = world.get_region("Belgium")
        assert preview["supply"]["fed"] == \
            world.get_effective_supply_cap("France", region)


# ════════════════════════════════════════════════════════════════════════
# 3. The sentences — produced AND rendered (the NP-V lesson)
# ════════════════════════════════════════════════════════════════════════

class TestTheSentences:

    def test_over_capacity_sentence_quotes_both_figures(self):
        world, executor, ney, soult, mack = _legacy_pair(
            lead_strength=90000, joiner_strength=40000)
        preview = _preview(world, executor, ney, mack)
        note = preview["supply_note"]
        fed = preview["supply"]["fed"]
        cost = preview["supply"]["attrition_per_turn"]
        assert f"{fed:,}" in note
        assert f"~{cost:,}" in note
        assert "feeds" in note

    def test_fed_sentence_when_the_province_can_carry_them(self):
        world, executor, ney, soult, mack = _legacy_pair(
            lead_strength=10000, joiner_strength=5000)
        preview = _preview(world, executor, ney, mack)
        assert preview["supply"]["attrition_per_turn"] == 0
        assert "can stand there fed" in preview["supply_note"]

    def test_g3_sentence_is_always_stated(self):
        """G3 (gate ruling): every corps in the battle province fights,
        BY DESIGN, and the game says so — on the commit screen."""
        world, executor, ney, soult, mack = _legacy_pair()
        preview = _preview(world, executor, ney, mack)
        note = preview["province_fights_note"]
        assert "Every corps in the province shares the field" in note

    def test_g3_teaches_fortify_not_restrain(self):
        """Recon correction 3: the real 1-AP permanent exclusion is
        FORTIFY (`fortified_static` / Rule 7); `restrain` is a
        charge-response verb and HOLD is literal-only."""
        world, executor, ney, soult, mack = _legacy_pair()
        note = _preview(world, executor, ney, mack)["province_fights_note"]
        assert "adjacent" in note
        assert "fortify" in note.lower()
        assert "(1 AP)" in note
        assert "restrain" not in note.lower()
        assert world._action_costs["fortify"] == 1, (
            "the taught price drifted from the applied one")

    def test_both_sentences_are_rendered_by_the_formatter(self):
        """A producer field no formatter reads is the NP-V defect — the
        render is pinned, not just the dict."""
        world, executor, ney, soult, mack = _legacy_pair(
            lead_strength=90000, joiner_strength=40000)
        preview = _preview(world, executor, ney, mack)
        text = executor._combat._format_muster_lines(preview)
        assert preview["supply_note"] in text
        assert preview["province_fights_note"] in text

    def test_formatter_survives_a_preview_without_the_new_keys(self):
        """Two standing fixtures build literal preview dicts — the
        formatter must .get(), never []. (This dict is strictly SMALLER
        than theirs — it also omits committed_strength — which exercises
        more .get paths, not fewer.)"""
        executor = CommandExecutor()
        text = executor._combat._format_muster_lines({
            "attacker": {"name": "Ney", "strength": 24000},
            "target": {"name": "Mack", "location": "Belgium",
                       "strength_display": "8,000"},
            "odds_band": "favorable",
            "rows": [],
            "shared_casualty_note": "",
        })
        assert "MUSTER — Ney (24,000) vs" in text


# ════════════════════════════════════════════════════════════════════════
# 4. Fog — the preview prices exactly when the panel prints
# ════════════════════════════════════════════════════════════════════════

class TestFogDiscipline:

    def test_unscouted_province_sentinels_and_says_so(self, world):
        """An enemy province below FULL: the quote is the -1 sentinel and
        the sentence admits ignorance — no digit leaks that the panel
        would hide."""
        executor = CommandExecutor()
        lead = next(m for m in world.marshals.values()
                    if m.nation == "France" and m.strength > 0)
        lead.location = "Paris"
        enemy = world.marshals.get("Mack")
        enemy.location = "Tyrol"
        world.calculate_visibility()
        assert not world.region_econ_visible("Tyrol"), (
            "precondition: Tyrol must be fogged below FULL from Paris")
        preview = _preview(world, executor, lead, enemy)
        assert preview["supply"]["fed"] == -1
        assert preview["supply"]["attrition_per_turn"] == -1
        assert "not known" in preview["supply_note"]
        assert "unscouted" in preview["supply_note"]
        text = executor._combat._format_muster_lines(preview)
        assert "not known" in text
        region = world.get_region("Tyrol")
        hidden = world.get_effective_supply_cap("France", region)
        assert f"{hidden:,}" not in preview["supply_note"]

    def test_the_predicate_is_shared_with_the_filtered_summary(self):
        """The fog rule exists ONCE: `region_econ_visible` gates both the
        payload's econ block and the preview's quote."""
        src = inspect.getsource(WorldState.get_filtered_game_state_summary)
        assert "region_econ_visible(" in src
        src2 = inspect.getsource(
            combat_executor_module.CombatExecutor._build_muster_preview)
        assert "region_econ_visible(" in src2

    def test_predicate_own_soil_true_full_true_partial_false(self, world):
        from backend.models.intel import FULL, PARTIAL
        assert world.region_econ_visible("Paris") is True
        lead = next(m for m in world.marshals.values()
                    if m.nation == "France" and m.strength > 0)
        lead.location = "Tyrol"
        world.calculate_visibility()
        assert world.get_region_intel("Tyrol").visibility == FULL
        assert world.region_econ_visible("Tyrol") is True, (
            "a marshal standing in the province is FULL")
        # The partial-false arm the name promises (review [G-F2]): pull
        # the marshal back out — Tyrol drops below FULL and the predicate
        # closes with it.
        lead.location = "Paris"
        world.calculate_visibility()
        vis = world.get_region_intel("Tyrol").visibility
        assert vis != FULL, "fixture drifted: Tyrol stayed FULL from Paris"
        if vis == PARTIAL:
            assert world.region_econ_visible("Tyrol") is False, (
                "PARTIAL must not open the econ block")
        else:
            assert world.region_econ_visible("Tyrol") is False


# ════════════════════════════════════════════════════════════════════════
# 5. ONE supply figure across the four surfaces
# ════════════════════════════════════════════════════════════════════════

class TestOneSupplyFigure:

    def test_own_soil_summary_ledger_and_engine_agree(self, world):
        region = world.get_region("Paris")
        effective = world.get_effective_supply_cap("France", region)
        raw = region.supply_capacity
        assert effective == int(raw * WorldState.HOME_SUPPLY_MULTIPLIER), (
            "precondition: own soil is fed")
        summary = world.get_filtered_game_state_summary()
        assert summary["map_data"]["Paris"]["supply_capacity"] == effective
        rows = _build_territories(world, "France")
        paris_row = next(r for r in rows if r["name"] == "Paris")
        assert paris_row["supply_capacity"] == effective

    def test_allied_soil_the_spec_example_swabia_feeds_60000(self, world):
        """The spec's own worked example: Swabia (Bavarian, allied) raw
        40,000 → France is fed at 60,000 through the ally's-table arm —
        and the preview, the summary and the engine all say 60,000."""
        executor = CommandExecutor()
        region = world.get_region("Swabia")
        assert region.controller == "Bavaria", "boot drifted"
        effective = world.get_effective_supply_cap("France", region)
        assert region.supply_capacity == 40000
        assert effective == 60000
        lead = next(m for m in world.marshals.values()
                    if m.nation == "France" and m.strength > 0)
        lead.location = "Swabia"
        world.calculate_visibility()
        mack = world.marshals.get("Mack")
        assert mack is not None and mack.location == "Swabia", (
            "boot drifted: Mack no longer stands at Swabia")
        preview = _preview(world, executor, lead, mack)
        assert preview["supply"]["fed"] == 60000
        summary = world.get_filtered_game_state_summary()
        assert summary["map_data"]["Swabia"]["supply_capacity"] == 60000

    def test_fogged_summary_row_keeps_the_sentinel(self, world):
        summary = world.get_filtered_game_state_summary()
        fogged = [name for name, rd in summary["map_data"].items()
                  if rd["supply_capacity"] == -1]
        assert fogged, ("no fogged rows at boot — the sentinel case "
                        "is untested")
        for name in fogged:
            assert summary["map_data"][name]["visibility_status"] not in (
                "full",), name

    def test_ledger_verdict_reads_the_effective_threshold(self, world):
        """The PT-D5 false-alarm band is dead: pooled strength between
        the raw and effective caps reads OK (the engine bills nothing
        there); above the effective cap reads Over capacity."""
        region = world.get_region("Paris")
        raw = region.supply_capacity
        effective = world.get_effective_supply_cap("France", region)
        assert effective > raw
        french = [m for m in world.marshals.values()
                  if m.nation == "France" and m.strength > 0]
        # Everyone out of Paris, then one corps inside the band.
        for m in french:
            m.location = "Picardy"
        inside_band = raw + (effective - raw) // 2
        french[0].location = "Paris"
        french[0].strength = inside_band
        rows = _build_territories(world, "France")
        paris_row = next(r for r in rows if r["name"] == "Paris")
        assert paris_row["supply_status"] == "OK", (
            "the false alarm inside the fed band is back")
        french[0].strength = effective + 1000
        rows = _build_territories(world, "France")
        paris_row = next(r for r in rows if r["name"] == "Paris")
        assert paris_row["supply_status"] == "Over capacity"

    def test_the_dispatch_twin_reads_the_same_helper(self):
        """PC15-D2 made the supply-strain headline effective; this slice
        must not have forked it. AST call-count, not a substring — a
        docstring could satisfy a grep (review [G-F4]; the file's own
        'a grep is not a census' rule applied to itself)."""
        import textwrap

        from backend.game_logic import dispatch as dispatch_mod
        src = textwrap.dedent(
            inspect.getsource(dispatch_mod._supply_strain_candidate))
        tree = ast.parse(src)
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "get_effective_supply_cap"]
        assert len(calls) >= 1, (
            "the headline no longer CALLS the shared cap helper")


# ════════════════════════════════════════════════════════════════════════
# 6. Build chips state their terms (WO-D4-A)
# ════════════════════════════════════════════════════════════════════════

class TestBuildTermsPayload:

    def _terms(self, world, region_name):
        summary = world.get_filtered_game_state_summary()
        return summary["map_data"][region_name].get("build_terms", {})

    def test_player_provinces_carry_terms_others_do_not(self, world):
        summary = world.get_filtered_game_state_summary()
        for name, rd in summary["map_data"].items():
            terms = rd.get("build_terms", {})
            region = world.get_region(name)
            if region.controller == "France":
                assert terms, f"{name}: player province without terms"
            else:
                assert terms == {} or "build_terms" not in rd, (
                    f"{name}: foreign province carries build terms")

    def test_costs_are_the_executors_own(self, world):
        terms = self._terms(world, "Paris")
        for key in ("supply_depot", "fortification", "training_ground",
                    "market", "stables"):
            assert terms[key]["cost"] == BUILDING_TYPES[key]["gold_cost"]
        assert terms["watchtower"]["cost"] == \
            EconomyExecutor.WATCHTOWER_GOLD_COST
        assert terms["repair"]["cost"] == EconomyExecutor.REPAIR_COST
        assert terms["upkeep"] == infrastructure_upkeep_rate(
            world.get_region("Paris"))

    def test_upkeep_is_tier_scaled_not_flat(self, world):
        """Paris (capital) bills 40 — the same digit as the flat
        fallback, so the capital row alone would let a hardcoded 40
        survive. A city province must read the CITY rate, and the two
        must differ or this test proves nothing."""
        city = next(r for r in world.regions.values()
                    if r.controller == "France"
                    and r.region_type == "city")
        summary = world.get_filtered_game_state_summary()
        city_upkeep = summary["map_data"][city.name]["build_terms"]["upkeep"]
        capital_upkeep = summary["map_data"]["Paris"]["build_terms"]["upkeep"]
        assert city_upkeep == infrastructure_upkeep_rate(city)
        assert city_upkeep != capital_upkeep, (
            "fixture no longer distinguishes the tiers")

    def test_depot_supply_figure_is_the_real_delta(self, world):
        """The chip's supply term must equal what the effective cap
        ACTUALLY rises by when the depot stands — terrain scaling and
        the fed multiplier included (a flat +10,000 would be the
        two-figures-one-label trap on 3 of France's boot provinces)."""
        region = world.get_region("Paris")
        assert not region.has_building("supply_depot")
        quoted = self._terms(world, "Paris")["supply_depot"]["supply"]
        before = world.get_effective_supply_cap("France", region)
        region.buildings.append({"type": "supply_depot"})
        after = world.get_effective_supply_cap("France", region)
        assert quoted == after - before
        assert quoted != 10000 or region.supply_modifier == 1.0

    def test_depot_and_market_income_figures_are_delivered_gold(self, world):
        """Income deltas run the region's own arithmetic both ways —
        stability and war damage included, so a chip on unrest soil
        quotes the truth, not the brochure."""
        region = world.get_region("Paris")
        terms = self._terms(world, "Paris")
        before = region.get_effective_income()
        region.buildings.append({"type": "supply_depot"})
        assert terms["supply_depot"]["income"] == \
            region.get_effective_income() - before
        region.buildings.pop()
        before = region.get_effective_income()
        region.buildings.append({"type": "market"})
        assert terms["market"]["income"] == \
            region.get_effective_income() - before

    def test_market_on_hostile_soil_quotes_zero(self, world):
        """`base × 0.0 stability = 0` — the no-gaming rule, stated on
        the chip instead of discovered after 350 gold."""
        region = world.get_region("Paris")
        region.stability = 20
        terms = self._terms(world, "Paris")
        assert terms["market"]["income"] == 0

    def test_stables_figure_is_the_nation_marginal(self, world):
        """ES-1b caps the SUMMED plains+stables bonus: the chip quotes
        what one more stables actually adds — and the quote equals the
        real regen change when the building lands."""
        quoted = self._terms(world, "Paris")["stables"]["cavalry"]
        assert quoted == world.stables_cavalry_marginal("France")
        assert quoted == 0, (
            "boot drifted: France's 24 plains no longer saturate the "
            "ES-1b cap — re-derive this pin, don't delete it")
        before = world.get_manpower_regen_rates("France")["cavalry"]
        world.get_region("Paris").buildings.append({"type": "stables"})
        after = world.get_manpower_regen_rates("France")["cavalry"]
        assert quoted == after - before

    def test_stables_marginal_positive_arm(self, world):
        """A nation UNDER the cap is quoted the real +750 — both arms of
        min() live, or a hardcoded 0 would survive the France case.
        Review [G-F1]: the assertion runs at the PAYLOAD leaf, not just
        the function — with the under-cap nation seated as player, the
        summary's own chip term must carry the +750, so a `= 0` hardcode
        at either payload seam dies here."""
        from backend.models.world_state import (
            CAVALRY_REGEN_BONUS_CAP, STABLES_CAVALRY_REGEN,
        )
        under_cap = next(
            (n for n in world.get_active_nations()
             if world.stables_cavalry_marginal(n) == STABLES_CAVALRY_REGEN),
            None)
        assert under_cap is not None, (
            "no boot nation sits under the ES-1b cap — the positive arm "
            "is unreachable and this fixture must craft one")
        controlled = [world.regions[n]
                      for n in world.get_nation_regions(under_cap)]
        bonus = world._cavalry_territory_bonus(controlled)
        assert bonus + STABLES_CAVALRY_REGEN <= CAVALRY_REGEN_BONUS_CAP
        world.player_nation = under_cap
        summary = world.get_filtered_game_state_summary()
        own_rows = [rd for rd in summary["map_data"].values()
                    if rd.get("controller") == under_cap
                    and rd.get("build_terms")]
        assert own_rows, f"{under_cap}: no chip terms on its own provinces"
        for rd in own_rows:
            assert rd["build_terms"]["stables"]["cavalry"] == \
                STABLES_CAVALRY_REGEN

    def test_fort_pct_and_training_figures_are_the_applied_constants(
            self, world):
        from backend.commands.objection_v2 import (
            REGION_FORTIFICATION_DEFENSE_BONUS,
        )
        terms = self._terms(world, "Paris")
        assert terms["fortification"]["defense_pct"] == int(
            round(REGION_FORTIFICATION_DEFENSE_BONUS * 100))
        assert terms["training_ground"]["recruit_morale"] == \
            EconomyExecutor.RECRUIT_MORALE_TRAINED
        assert terms["training_ground"]["recruit_morale_base"] == \
            EconomyExecutor.RECRUIT_MORALE_BASE
        assert terms["training_ground"]["drill_gain"] == \
            WorldState.DRILL_MORALE_GAIN_TRAINED
        assert terms["training_ground"]["drill_gain_base"] == \
            WorldState.DRILL_MORALE_GAIN

    def test_every_leaf_is_an_int(self, world):
        """Golden Rule 2 — Godot crashes on floats."""
        terms = self._terms(world, "Paris")
        def walk(node):
            if isinstance(node, dict):
                for v in node.values():
                    walk(v)
            else:
                assert isinstance(node, int), node
        walk(terms)

    def test_the_executors_read_the_promoted_constants(self):
        """The chip quotes class constants; these pins hold the executors
        to the SAME names, so a retune moves both or neither."""
        src = inspect.getsource(EconomyExecutor._execute_recruit)
        # The ASSIGNMENT form, not the bare name — the Shorncliffe note
        # also mentions the constant, and a bare-substring pin went inert
        # the moment it did (found by the sweep, review round).
        assert "RECRUIT_MORALE = self.RECRUIT_MORALE_BASE" in src
        assert "RECRUIT_MORALE = self.RECRUIT_MORALE_TRAINED" in src
        src = inspect.getsource(EconomyExecutor._execute_repair)
        assert "self.REPAIR_COST" in src
        assert EconomyExecutor.RECRUIT_MORALE_BASE == 40
        assert EconomyExecutor.RECRUIT_MORALE_TRAINED == 70
        assert EconomyExecutor.REPAIR_COST == 150


class TestPanelReadsThePayload:

    def test_chips_derive_terms_from_the_payload(self):
        """The ui6 precedent (`test_chip_terms_derive_from_payload`)
        extended to the region panel: terms are payload reads, and none
        of the five build costs is hardcoded in the .gd."""
        src = REGION_PANEL_GD.read_text(encoding="utf-8")
        assert 'data.get("build_terms"' in src
        assert "_build_terms_text" in src
        for literal in ('"300g"', '"400g"', '"250g"', '"350g"', '"150g"',
                        "300g\"", "10,000 supply"):
            assert literal not in src, (
                f"hardcoded term {literal} in region_panel.gd")

    def test_the_chip_stems_survive(self):
        """The ui6 contract pins literal command stems — kept."""
        src = REGION_PANEL_GD.read_text(encoding="utf-8")
        assert "build watchtower in " in src
        assert "repair buildings in " in src
        for key in BUILDING_TYPES:
            assert f'"{key}"' in src

    def test_the_upkeep_header_is_payload_read(self):
        src = REGION_PANEL_GD.read_text(encoding="utf-8")
        assert 'terms.get("upkeep"' in src
        assert "keeps " in src


# ════════════════════════════════════════════════════════════════════════
# 7. BASELINE_SERIES immunity — structural, then proven by the suite
# ════════════════════════════════════════════════════════════════════════

class TestBaselineImmunity:

    def test_the_preview_has_exactly_one_call_site(self):
        """§2 C-8: player-gated, ONE call site — preview changes are
        structurally unable to move BASELINE_SERIES. (The subprocess
        proof is the standing control arm in test_ai_intent_assurance,
        which runs the 40-turn ambient series and compares bytes.)"""
        src = Path(combat_executor_module.__file__).read_text(
            encoding="utf-8")
        tree = ast.parse(src)
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "_build_muster_preview"]
        assert len(calls) == 1

    def test_the_engine_refactor_is_semantics_preserving(self):
        """The extracted rate reproduces the pre-slice loop on the
        boundary cells the old inline code special-cased."""
        cases = [
            # (total, cap, n) → the pre-slice hand arithmetic
            (59999, 60000, 1, 0.0),
            (60000, 60000, 2, 0.0),          # total <= cap, n < 3
            (60000, 60000, 3, 0.02),         # under cap, stacking
            (60001, 60000, 1, min(0.03, (1 / 60000) * 0.015)),
            (300000, 60000, 1, 0.03),        # slope saturates
            (300000, 60000, 9, 0.06),        # ceiling
        ]
        for total, cap, n, expected in cases:
            assert WorldState.supply_attrition_rate(total, cap, n) == \
                pytest.approx(expected), (total, cap, n)

    def test_effective_cap_decomposition_is_byte_identical(self, world):
        """`get_effective_supply_cap` = int(raw × multiplier) after the
        split — every boot province, both the fed and unfed arms."""
        for region in world.regions.values():
            mult = world._supply_multiplier("France", region)
            assert world.get_effective_supply_cap("France", region) == \
                int(region.supply_capacity * mult), region.name


# ════════════════════════════════════════════════════════════════════════
# 8. The review round (three-lens fleet at b089701) — confirmed findings
# ════════════════════════════════════════════════════════════════════════

class TestReviewRoundFixes:

    # ── [B-F1] the shore memo is nation-keyed, not per-region ─────────

    def test_one_shore_verdict_per_nation_per_summary(self, world,
                                                      monkeypatch):
        """The old (nation, region) key took 81 misses / 0 hits per
        response — 81 identical fleet scans. The summary asks for ONE
        nation (the player), so the whole pass costs at most one
        verdict."""
        from backend.game_logic import naval as naval_mod
        calls = {"n": 0}
        real = naval_mod.shore_supply_state

        def counting(w, nation, region_name):
            calls["n"] += 1
            return real(w, nation, region_name)

        monkeypatch.setattr(naval_mod, "shore_supply_state", counting)
        world.get_filtered_game_state_summary()
        assert calls["n"] <= 1, (
            f"{calls['n']} shore scans for a one-nation pass — the memo "
            f"key regressed to per-region")
        assert calls["n"] == 1, (
            "precondition: the naval arm must be live at boot (France is "
            "at war and holds coastal provinces) or this pin is vacuous")

    # ── [B-F2] artillery bodies never stand in the battle province ────

    def test_adjacent_artillery_joiner_is_not_billed(self):
        """The resolver keeps adjacent guns as fire support — they never
        relocate, so their bodies never eat the battle province's bread.
        A co-located gun DOES stand there and counts."""
        world, executor, ney, soult, mack = _legacy_pair()
        guns = MarshalFactory.infantry(name="Marmont", location="Paris",
                                       strength=12000,
                                       personality="aggressive")
        guns.artillery = True
        world.marshals["Marmont"] = guns
        preview = _preview(world, executor, ney, mack)
        row = next(r for r in preview["rows"] if r["marshal"] == "Marmont")
        assert row["will_join"] is True, (
            "precondition: the gun must be a JOINER for the exclusion "
            "to mean anything")
        assert preview["supply"]["bodies"] == \
            int(ney.strength) + int(soult.strength)
        # Co-located guns stand on the field and eat.
        guns.location = "Belgium"
        preview = _preview(world, executor, ney, mack)
        assert preview["supply"]["bodies"] == (
            int(ney.strength) + int(soult.strength) + int(guns.strength))

    # ── [B-F3] enemy soil: quote == bill while the controller stands ──

    def test_enemy_soil_parity_uncaptured(self):
        """The third parity arm: on enemy-held soil the quote prices the
        UNFED cap, and standing there without a capture bills exactly
        that. (A capturing victory flips the controller and RAISES the
        cap — the recorded conservatism; this arm pins the exact case.)"""
        world, executor, ney, soult, mack = _legacy_pair(
            lead_strength=90000, joiner_strength=40000)
        region = world.get_region("Belgium")
        region.controller = "Austria"
        soult.location = "Belgium"      # gives FULL sight + joins
        world.calculate_visibility()
        preview = _preview(world, executor, ney, mack)
        quote = preview["supply"]
        assert quote["fed"] == region.supply_capacity, (
            "enemy soil must quote the UNFED base cap")
        assert quote["attrition_per_turn"] > 0, (
            "fixture must stand over the base cap")
        mack.location = "Paris"
        ney.location = "Belgium"
        events = world.process_supply_attrition()
        billed = sum(e["losses"] for e in events
                     if e.get("type") == "supply_attrition"
                     and e.get("region") == "Belgium"
                     and e.get("nation") == "France")
        assert billed == quote["attrition_per_turn"]

    # ── [B-F4] the fort bonus has ONE name ────────────────────────────

    def test_fort_bonus_census_no_scattered_literals(self):
        """Six 0.25 copies applied what the chip quotes by name. The
        census is a proximity scan (the field-battle site kept its
        literal two lines below the has_building check, so a line-based
        grep would miss a resurrected split form)."""
        backend_dir = REPO / "backend"
        offenders = []
        # The bonus is always keyed to `has_building("fortification")` —
        # scoping the window there excludes the unrelated 0.25s (the
        # building-damage chance keys on `building["type"]`).
        needle = 'has_building("fortification")'
        for py in backend_dir.rglob("*.py"):
            if py.name == "objection_v2.py":
                continue  # the definition + its docstring
            text = py.read_text(encoding="utf-8")
            for m in re.finditer(re.escape(needle), text):
                window = text[max(0, m.start() - 150):m.end() + 150]
                if "0.25" in window:
                    offenders.append(f"{py.name}:{m.start()}")
        assert not offenders, (
            f"fort-bonus literal(s) beside the has_building check outside "
            f"the named constant: {offenders}")

    def test_resolver_and_chip_read_the_same_name(self, world):
        from backend.commands import combat_executor as ce
        src = Path(ce.__file__).read_text(encoding="utf-8")
        assert src.count("REGION_FORTIFICATION_DEFENSE_BONUS") >= 5, (
            "the resolver sites stopped reading the named constant")
        from backend.commands.objection_v2 import (
            REGION_FORTIFICATION_DEFENSE_BONUS,
        )
        terms = world.get_filtered_game_state_summary()[
            "map_data"]["Paris"]["build_terms"]
        assert terms["fortification"]["defense_pct"] == int(
            round(REGION_FORTIFICATION_DEFENSE_BONUS * 100))

    # ── [B-F5] a legacy world quotes no upkeep it never bills ─────────

    def test_legacy_world_quotes_zero_upkeep(self):
        world, executor, ney, soult, mack = _legacy_pair()
        summary = world.get_filtered_game_state_summary()
        rows = [rd for rd in summary["map_data"].values()
                if rd.get("build_terms")]
        assert rows, "legacy player provinces carry chip terms"
        for rd in rows:
            assert rd["build_terms"]["upkeep"] == 0, (
                "the legacy world bills no infrastructure upkeep — "
                "quoting the Europe rate there is the MC-2b class")

    # ── [B-F6] the Shorncliffe note reads the promoted constant ───────

    def test_shorncliffe_note_reads_the_constant(self):
        src = inspect.getsource(EconomyExecutor._execute_recruit)
        assert "{self.RECRUIT_MORALE_BASE}" in src, (
            "the ', not 40' literal came back — the note must track the "
            "promoted constant")
        assert "not 40" not in src

    # ── [C-F2] the ledger's verdict knows the death-ball arm ──────────

    def test_ledger_crowded_verdict(self, world):
        """Three corps under the effective cap bill 2%+/turn — the tab
        beside the preview that quotes that cost must not read OK."""
        region = world.get_region("Paris")
        effective = world.get_effective_supply_cap("France", region)
        french = [m for m in world.marshals.values()
                  if m.nation == "France" and m.strength > 0]
        assert len(french) >= 3
        for m in french:
            m.location = "Picardy"
        per_corps = max(1000, (effective // 4) // 1000 * 1000)
        for m in french[:3]:
            m.location = "Paris"
            m.strength = per_corps
        rows = _build_territories(world, "France")
        paris_row = next(r for r in rows if r["name"] == "Paris")
        assert paris_row["supply_status"] == "Crowded", paris_row
        # Two corps under cap stay OK (no stacking bill below 3).
        french[2].location = "Picardy"
        rows = _build_territories(world, "France")
        paris_row = next(r for r in rows if r["name"] == "Paris")
        assert paris_row["supply_status"] == "OK"

    # ── [C-F1] the G3 sentence names its one exception ────────────────

    def test_g3_names_the_quarrel_exception_when_present(self):
        world, executor, ney, soult, mack = _legacy_pair()
        soult.location = "Belgium"
        ney.set_relationship(soult.name, -2)
        soult.set_relationship(ney.name, -2)
        preview = _preview(world, executor, ney, mack)
        assert any(r.get("reason") == "shares_the_field_apart"
                   for r in preview["rows"]), "precondition"
        note = preview["province_fights_note"]
        assert "its one exception" in note
        assert "feud" in note

    def test_g3_stays_plain_without_a_quarrel(self):
        world, executor, ney, soult, mack = _legacy_pair()
        note = _preview(world, executor, ney, mack)["province_fights_note"]
        assert "exception" not in note
        assert "that is the design." in note
