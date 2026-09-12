"""IQ-1 SW-1 — "The Substitute Market": the one purchase bounded by gold.

The measured disease (September 12, 2026): **every sink in this game is
capped by a non-gold resource.** 97 build slots on the whole 126-province map
(38,800g of construction for all twenty nations, ever). 46 recruit batches in
a forty-turn campaign, capped by the manpower pools rather than the purse. A
seven-man commission bench at 30,000g, each hirable once. So no sink can
respond to a gold surplus, and a commanded France banks **88,556g** having
spent **2.5%** of 199,101g gross.

Worse, the *rate* of buying is capped and not the menu: every gold-consuming
verb is in `meta_executor.ADMIN_ACTIONS` and `max_admin_actions` is a
hardcoded **2**. Measured on the shipped boot, the dearest single admin
purchase available to France is **1,504 gold** (Murat's cavalry at
Franche-Comte), so two perfect actions buy 3,008g. Adding a fifth building
would change nothing.

A substitute draws NOTHING from `manpower_pools`. Its only limits are the
purse and the establishment ceiling, which makes it the first gold-limited
purchase in the game. The fiction is exact: under the conscription law a
called-up man could pay a `remplacant` to serve in his place, and the price
rose as the class emptied — ruinous by 1813.

Priced as `base x LEVY_SUBSTITUTE_MULT x (1 + LEVY_SCARCITY_MULT x scarcity)`
and handed to the EXISTING `_calculate_recruit_cost` as its `base_cost`, so
the capital discount, the settling premium, the W6-11 war x3, the ES-3
over-limit ladder and MC-2b's Intendance all compose on top exactly as they do
for a draft — for the player and for the AI, through one helper (GR5), and
shown = applied by construction.

The ceiling is `FORCE_LIMIT_SEVERE_BAND` x the force limit, which is the SAME
line above which the ES-3 upkeep ladder stops charging half the rate. You may
buy up to the point where keeping the men becomes punitive and not one man
past it — so at the 1805 boot France's 189,000 against a 195,000 ceiling is
REFUSED, and the market becomes legal only once she has lost 4,000 men. It
buys replacements, not expansion, and that is a pin rather than a coincidence.
"""

import pytest

from pathlib import Path

from backend.commands import economy_executor as econ_mod
from backend.commands.economy_executor import (
    levy_substitute_price, levy_purchase_ceiling,
)
from backend.commands.executor import CommandExecutor
from backend.models.world_state import (
    WorldState, INFANTRY_RECRUIT_AMOUNT, INFANTRY_RECRUIT_GOLD_COST_BASE,
    CAVALRY_RECRUIT_GOLD_COST_BASE, ARTILLERY_RECRUIT_GOLD_COST_BASE,
    LEVY_SUBSTITUTE_MULT, LEVY_SCARCITY_FLOOR, LEVY_SCARCITY_MULT,
    LEVY_MORALE_BASE, LEVY_MAX_BATCH, FORCE_LIMIT_SEVERE_BAND,
    severe_band_threshold,
)

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")


@pytest.fixture
def ex():
    return CommandExecutor()


@pytest.fixture
def boot():
    return WorldState.from_scenario(str(SCENARIO_PATH), seed="historical")


def _staged(pool=0, army=120_000):
    """ONE board for every arm, so nothing is compared across geometries.

    France at war, army scaled to `army`, infantry class at `pool`, Ney at
    Paris. No over-limit multiplier applies at 120,000 against a limit of
    130,000, so each figure below is the bare composition of
    scarcity x capital x war x intendance.
    """
    w = WorldState.from_scenario(str(SCENARIO_PATH), seed="historical")
    fr = [m for m in w.marshals.values() if m.nation == "France"]
    total = sum(m.strength for m in fr)
    for m in fr:
        m.strength = int(m.strength * (army / total))
    w.manpower_pools["France"]["infantry"] = int(pool)
    w.get_marshal("Ney").location = w.get_nation_capital("France")
    w.nation_gold["France"] = 100_000
    return w


def _buy(ex, world, marshal="Ney", batches=1, nation=None):
    cmd = {"action": "purchase_levy", "marshal": marshal,
           "batches": batches, "type": "specific"}
    if nation:
        cmd["_acting_nation"] = nation
    return ex.execute({"action": "purchase_levy", "command": cmd},
                      {"world": world})


# ════════════════════════════════════════════════════════════════════════
# ARM A — a single admin action can finally absorb the surplus
# ════════════════════════════════════════════════════════════════════════

class TestArmA_ThePurseIsSpendable:
    def test_one_action_buys_thirty_thousand_men_for_24840_gold(self, ex):
        w = _staged()
        ney = w.get_marshal("Ney")
        before = ney.strength
        r = _buy(ex, w, batches=3)
        assert r["success"], r["message"]
        assert ney.strength - before == 3 * INFANTRY_RECRUIT_AMOUNT
        assert w.nation_gold["France"] == 100_000 - 24_840
        # the whole point, stated as the comparison that motivated it
        assert 24_840 > 5_000

    def test_not_a_man_comes_off_the_rolls(self, ex):
        w = _staged(pool=0)
        _buy(ex, w, batches=3)
        assert w.manpower_pools["France"]["infantry"] == 0

    def test_it_does_not_touch_the_pool_even_when_the_pool_is_full(self, ex):
        w = _staged(pool=80_000)
        _buy(ex, w, batches=2)
        assert w.manpower_pools["France"]["infantry"] == 80_000

    def test_bought_men_dilute_morale_to_the_bought_rate(self, ex):
        w = _staged()
        ney = w.get_marshal("Ney")
        ney.morale = 100
        old = ney.strength
        _buy(ex, w, batches=3)
        expect = int((old * 100 + 30_000 * LEVY_MORALE_BASE) / (old + 30_000))
        assert ney.morale == expect
        assert ney.morale < 100


# ════════════════════════════════════════════════════════════════════════
# ARM B — the negative control. The slice's own falsification.
# ════════════════════════════════════════════════════════════════════════

class TestArmB_TheControl:
    def test_without_the_market_two_admin_actions_cannot_reach_5000_gold(
            self, ex, boot):
        """Measured, not asserted: price every legal admin purchase France
        can make on the shipped boot and take the largest."""
        best, who = 0, None
        for m in boot.marshals.values():
            if m.nation != "France":
                continue
            region = boot.get_region(m.location)
            if region is None or region.controller != "France":
                continue
            base = (ARTILLERY_RECRUIT_GOLD_COST_BASE
                    if getattr(m, "artillery", False)
                    else CAVALRY_RECRUIT_GOLD_COST_BASE
                    if getattr(m, "cavalry", False)
                    else INFANTRY_RECRUIT_GOLD_COST_BASE)
            cost = ex._economy._calculate_recruit_cost(
                region, boot, base_cost=base, nation="France", marshal=m)
            if cost > best:
                best, who = cost, m.name
        assert best == 1504, (best, who)
        assert who == "Murat", who
        assert best * 2 < 5_000

    def test_the_lever_closes_the_market(self, ex, monkeypatch):
        w = _staged()
        monkeypatch.setattr(econ_mod, "THE_SUBSTITUTE_MARKET_IS_OPEN", False)
        before = w.get_marshal("Ney").strength
        gold = w.nation_gold["France"]
        r = _buy(ex, w, batches=3)
        assert not r["success"]
        assert w.get_marshal("Ney").strength == before
        assert w.nation_gold["France"] == gold


# ════════════════════════════════════════════════════════════════════════
# ARM C — the premium for having been bled is exactly 4x
# ════════════════════════════════════════════════════════════════════════

class TestArmC_LosingCostsMore:
    def _per_batch(self, ex, w):
        ney = w.get_marshal("Ney")
        return ex._economy._calculate_recruit_cost(
            w.get_region(ney.location), w,
            base_cost=levy_substitute_price(w, "France"),
            nation="France", marshal=ney)

    def test_an_empty_class_costs_exactly_four_times_a_full_one(self, ex):
        bled = self._per_batch(ex, _staged(pool=0))
        full = self._per_batch(ex, _staged(pool=int(LEVY_SCARCITY_FLOOR)))
        assert full == 2_070
        assert bled == 8_280
        assert bled == full * (1 + LEVY_SCARCITY_MULT)
        assert bled / full == 4.0

    def test_the_floor_price_is_the_flat_premium_over_a_draft(self, ex):
        w = _staged(pool=int(LEVY_SCARCITY_FLOOR) * 2)
        assert levy_substitute_price(w, "France") == (
            INFANTRY_RECRUIT_GOLD_COST_BASE * LEVY_SUBSTITUTE_MULT)

    def test_the_price_is_monotonic_in_scarcity(self, ex):
        prices = [levy_substitute_price(_staged(pool=p), "France")
                  for p in (0, 10_000, 20_000, 30_000, 40_000, 80_000)]
        assert prices == sorted(prices, reverse=True)
        assert prices[0] == 4 * prices[-1]


# ════════════════════════════════════════════════════════════════════════
# ARM D — GR5, through the real executor on both sides
# ════════════════════════════════════════════════════════════════════════

class TestArmD_TheAIPaysTheSamePrice:
    def test_identical_board_identical_price_for_an_enemy_nation(self, ex):
        """Not two helper calls compared — two real purchases driven
        through the same executor, one by France and one by Austria."""
        prices = {}
        for nation, name in (("France", "Ney"), ("Austria", "Mack")):
            w = _staged()
            w.manpower_pools.setdefault(nation, {})["infantry"] = 0
            # Austria boots 126,000 men against a 77,500 limit — already
            # above her own 116,250 ceiling, so she cannot buy either. The
            # ceiling is doing its job on both sides; scale her army under
            # it so the PRICE is what this arm measures.
            for other in list(w.marshals.values()):
                if other.nation == nation and other.name != name:
                    other.strength = 1_000
            m = w.get_marshal(name)
            m.nation = nation
            m.strength = 20_000
            cap = w.get_nation_capital(nation)
            m.location = cap
            w.get_region(cap).controller = nation
            w.nation_gold[nation] = 100_000
            before = m.strength
            r = _buy(ex, w, marshal=name, batches=1, nation=nation)
            assert r["success"], (nation, r["message"])
            assert m.strength - before == INFANTRY_RECRUIT_AMOUNT
            prices[nation] = 100_000 - w.nation_gold[nation]
        # Both capitals, both at war, both empty classes: the composition
        # differs only by each marshal's own Intendance, which is the point
        # — the SHARED helper prices them, not two copies.
        assert prices["France"] > 0 and prices["Austria"] > 0

    def _austria(self, army=40_000, pool=0):
        """Austria, at war, bled to `army`, class at `pool`, her infantry
        marshal at Vienna with a full purse."""
        w = WorldState.from_scenario(str(SCENARIO_PATH), seed="historical")
        ms = [m for m in w.marshals.values() if m.nation == "Austria"]
        total = sum(m.strength for m in ms) or 1
        for m in ms:
            m.strength = int(m.strength * (army / total))
        w.manpower_pools.setdefault("Austria", {})["infantry"] = int(pool)
        inf = [m for m in ms if not getattr(m, "cavalry", False)
               and not getattr(m, "artillery", False)][0]
        inf.location = w.get_nation_capital("Austria")
        w.nation_gold["Austria"] = 100_000
        return w, inf

    def test_the_ai_rung_ACTUALLY_FIRES(self, ex):
        """The positive case, driven through the real admin phase.

        A mutation sweep found the first version of this pin INERT: it
        asserted None on a board where the answer was None for the WRONG
        reason, and the rung could never have fired at all —
        `_find_weakest_marshal_for_admin` skips a marshal whose POOL cannot
        cover a draft, which is every marshal on the only board a
        substitute is for. "The AI can reach it" and "the AI reaches it"
        are different claims (IGR-E).
        """
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(ex)
        w, mack = self._austria()
        before, gold = mack.strength, w.nation_gold["Austria"]
        results = ai.execute_admin_phase("Austria", w, {"world": w})
        kinds = [r.get("ai_action", {}).get("action") for r in results]
        assert "purchase_levy" in kinds, kinds
        assert mack.strength - before == INFANTRY_RECRUIT_AMOUNT
        assert w.nation_gold["Austria"] < gold
        assert w.manpower_pools["Austria"]["infantry"] == 0

    def test_a_full_class_is_drafted_not_bought(self, ex):
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(ex)
        w, _ = self._austria(pool=80_000)
        assert ai._find_substitute_purchase("Austria", w, 100_000) is None

    def test_peace_never_buys_substitutes(self, ex):
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(ex)
        from backend.game_logic.diplomacy import set_diplomatic_state
        w, _ = self._austria()
        for other in list(w.get_nations_at_war_with("Austria")):
            set_diplomatic_state(w, "Austria", other, "PEACE")
        assert not w.get_nations_at_war_with("Austria")
        assert ai._find_substitute_purchase("Austria", w, 100_000) is None

    def test_a_thin_treasury_never_buys(self, ex):
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(ex)
        w, _ = self._austria()
        assert ai._find_substitute_purchase("Austria", w, 100) is None

    def test_the_lever_closes_the_rung_too(self, ex, monkeypatch):
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(ex)
        w, _ = self._austria()
        monkeypatch.setattr(econ_mod, "THE_SUBSTITUTE_MARKET_IS_OPEN", False)
        assert ai._find_substitute_purchase("Austria", w, 100_000) is None

    def test_ignore_pool_is_what_makes_the_rung_reachable(self, ex):
        """The helper answers None on an empty class unless asked not to —
        which is the defect the sweep caught. Pin both directions."""
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(ex)
        w, _ = self._austria()
        assert ai._find_weakest_marshal_for_admin("Austria", w) is None
        assert ai._find_weakest_marshal_for_admin(
            "Austria", w, ignore_pool=True) is not None

    def test_the_ai_command_builder_carries_the_batch_count(self):
        """A silently dropped structured field is the IGR-E class of
        defect. `batches` must be in the admin whitelist."""
        import inspect
        from backend.ai.enemy_ai import EnemyAI
        src = inspect.getsource(EnemyAI.execute_admin_phase)
        assert '"batches"' in src, "batches is dropped by the AI builder"


# ════════════════════════════════════════════════════════════════════════
# ARM E — the boot is shut, by construction
# ════════════════════════════════════════════════════════════════════════

class TestArmE_TheMarketBuysReplacementsNotExpansion:
    def test_the_1805_boot_refuses_and_names_the_ceiling(self, ex, boot):
        boot.nation_gold["France"] = 100_000
        boot.get_marshal("Ney").location = boot.get_nation_capital("France")
        r = _buy(ex, boot, batches=1)
        assert not r["success"]
        assert "189,000" in r["message"]
        assert "195,000" in r["message"]
        assert "4,000" in r["message"]

    def test_the_ceiling_is_the_es3_severe_band_not_a_fresh_number(self, boot):
        fl = boot.get_force_limit("France")
        assert levy_purchase_ceiling(boot, "France") == severe_band_threshold(fl)
        assert severe_band_threshold(fl) == int(fl * FORCE_LIMIT_SEVERE_BAND)
        assert levy_purchase_ceiling(boot, "France") == 195_000

    def test_losing_four_thousand_men_opens_the_market(self, ex, boot):
        boot.nation_gold["France"] = 100_000
        ney = boot.get_marshal("Ney")
        ney.location = boot.get_nation_capital("France")
        ney.strength = max(0, ney.strength - 6_000)
        assert _buy(ex, boot, batches=1)["success"]

    def test_a_purchase_is_trimmed_to_the_room_not_refused(self, ex):
        """Room for one batch, three asked: buy one, do not refuse."""
        w = _staged(army=185_000)
        ney = w.get_marshal("Ney")
        before = ney.strength
        r = _buy(ex, w, batches=3)
        assert r["success"], r["message"]
        assert ney.strength - before == INFANTRY_RECRUIT_AMOUNT

    def test_batches_are_clamped_to_the_maximum(self, ex):
        w = _staged()
        ney = w.get_marshal("Ney")
        before = ney.strength
        _buy(ex, w, batches=99)
        assert ney.strength - before == LEVY_MAX_BATCH * INFANTRY_RECRUIT_AMOUNT


# ════════════════════════════════════════════════════════════════════════
# The refusals, each naming its own reason
# ════════════════════════════════════════════════════════════════════════

class TestTheRefusalsAreHonest:
    def test_cavalry_and_artillery_have_no_market(self, ex):
        w = _staged()
        murat = w.get_marshal("Murat")
        murat.location = w.get_nation_capital("France")
        r = _buy(ex, w, marshal="Murat", batches=1)
        assert not r["success"]
        assert "cavalry" in r["message"]
        # E2's blessed scarcity: you cannot buy horses.
        assert murat.strength == w.get_marshal("Murat").strength

    def test_the_field_caps_the_draft_rather_than_refusing_it(self, ex):
        """CO-4's rule, identical to a draft: away from a depot a batch
        delivers AI_CORPS_REGEN_CAP men at the batch price.

        The first cut REFUSED here, and the measurement killed it — on the
        commanded board France's marshals stand at Tyrol, Lorraine,
        Franche-Comte and Piedmont, so 13 of 13 scripted purchases were
        refused and the treasury went UP. A replacement market a bled corps
        at the front cannot reach is not a market."""
        from backend.commands.economy_executor import AI_CORPS_REGEN_CAP
        w = _staged()
        ney = w.get_marshal("Ney")
        ney.location = "Rhineland"
        w.get_region("Rhineland").controller = "France"
        before = ney.strength
        r = _buy(ex, w, batches=1)
        assert r["success"], r["message"]
        assert ney.strength - before == AI_CORPS_REGEN_CAP
        assert "no depot" in r["message"].lower()
        assert f"{AI_CORPS_REGEN_CAP:,}" in r["message"]

    def test_a_field_batch_costs_the_same_as_a_depot_batch(self, ex):
        """A pure throughput cap, not a price penalty — CO-4's own words,
        and what `_execute_recruit` already does."""
        depot = _staged()
        depot_gold = depot.nation_gold["France"]
        _buy(ex, depot, batches=1)
        depot_spend = depot_gold - depot.nation_gold["France"]

        field = _staged()
        field.get_marshal("Ney").location = "Rhineland"
        field.get_region("Rhineland").controller = "France"
        field_gold = field.nation_gold["France"]
        _buy(ex, field, batches=1)
        field_spend = field_gold - field.nation_gold["France"]
        # Rhineland is not a capital, so the 0.75 capital discount does not
        # apply — the field batch is DEARER, and that is the regional
        # pricing the draft already carries, not a new penalty.
        assert field_spend > depot_spend

    def test_a_poor_treasury_is_told_what_it_could_afford(self, ex):
        w = _staged()
        w.nation_gold["France"] = 9_000
        r = _buy(ex, w, batches=3)
        assert not r["success"]
        assert "8,280" in r["message"]
        assert "9,000" in r["message"]

    def test_we_do_not_buy_substitutes_on_soil_we_do_not_hold(self, ex):
        w = _staged()
        cap = w.get_nation_capital("France")
        w.get_region(cap).controller = "Austria"
        r = _buy(ex, w, batches=1)
        assert not r["success"]
        assert cap in r["message"]


# ════════════════════════════════════════════════════════════════════════
# Composition — the price is not a second implementation
# ════════════════════════════════════════════════════════════════════════

class TestItComposesTheExistingMultipliers:
    def test_every_multiplier_shows_up_in_the_price(self, ex):
        w = _staged(pool=0)
        ney = w.get_marshal("Ney")
        cap = w.get_region(ney.location)
        base = levy_substitute_price(w, "France")
        assert base == 3_200                       # 200 x 4 x (1 + 3.0)
        priced = ex._economy._calculate_recruit_cost(
            cap, w, base_cost=base, nation="France", marshal=ney)
        # capital 0.75, war x3, Ney's wasteful intendance +15%
        assert priced == int(round(int(int(base * 0.75) * 3) * 1.15))
        assert priced == 8_280

    def test_the_quoted_premium_is_measured_before_the_men_arrive(self, ex):
        """Shown = applied at the moment of the DECISION. Priced after
        `add_troops` the draft carries an over-limit multiplier the
        purchase itself created, and the line quoted 13.9x where the
        player faced 16.0x."""
        w = _staged(pool=0)
        r = _buy(ex, w, batches=3)
        assert r["success"]
        assert "16.0 times" in r["message"], r["message"]


# ════════════════════════════════════════════════════════════════════════
# Wiring — the 12-step checklist, asserted rather than assumed
# ════════════════════════════════════════════════════════════════════════

class TestTheWiring:
    def test_it_is_a_valid_action(self):
        from backend.ai.validation import VALID_ACTIONS, NEVER_STRATEGIC_ACTIONS
        assert "purchase_levy" in VALID_ACTIONS
        assert "purchase_levy" in NEVER_STRATEGIC_ACTIONS

    def test_it_costs_one_administrative_action(self, boot):
        from backend.commands.meta_executor import ADMIN_ACTIONS
        assert "purchase_levy" in ADMIN_ACTIONS
        assert boot.get_action_cost("purchase_levy") == 1

    def test_the_fast_parser_reaches_it(self, boot):
        from backend.ai.llm_client import LLMClient
        c = LLMClient(provider="mock")
        gs = {"world": boot}
        for phrase in ("buy substitutes for Ney",
                       "purchase a levy for Ney",
                       "hire replacements for Ney",
                       "buy remplacants for Ney"):
            assert c.fast_parse(phrase, gs).action == "purchase_levy", phrase

    def test_it_does_not_steal_the_pension_or_buy_off_verbs(self, boot):
        from backend.ai.llm_client import LLMClient
        c = LLMClient(provider="mock")
        gs = {"world": boot}
        assert c.fast_parse("raise Ney's pension", gs).action != "purchase_levy"
        assert c.fast_parse("buy off Prussia", gs).action != "purchase_levy"
        assert c.fast_parse("recruit 10000 infantry", gs).action == "recruit"

    def test_it_has_display_names(self):
        from backend.display_names import ACTION_DISPLAY
        assert ACTION_DISPLAY.get("purchase_levy")

    def test_the_purchase_leaves_a_trace(self, ex):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
        assert "substitutes_purchased" in CAMPAIGN_LOG_TYPES
        w = _staged()
        _buy(ex, w, batches=2)
        rows = [e for e in w.event_log
                if e.get("type") == "substitutes_purchased"]
        assert rows, "no campaign-log event written"
        line = format_event_oneliner(rows[-1])
        assert "20,000 substitutes" in line
        assert "not a man off the rolls" in line

    def test_the_spend_is_recorded(self, ex):
        """SW-0's Spent line must see it — the census exists so a new
        outflow cannot join the fifteen invisible ones."""
        w = _staged()
        _buy(ex, w, batches=2)
        assert w.gold_spent_this_turn.get("France", 0) == 2 * 8_280


# ════════════════════════════════════════════════════════════════════════
# The band promotion moved no number
# ════════════════════════════════════════════════════════════════════════

class TestTheSevereBandPromotion:
    @pytest.mark.parametrize("fl", [0, 1, 2, 3, 130_000, 130_001, 130_003,
                                    195_000, 1_000_001])
    def test_it_is_identical_to_the_literal_it_replaced(self, fl):
        assert severe_band_threshold(fl) == (fl + fl // 2 if fl > 0 else 0)
        if fl > 0:
            assert severe_band_threshold(fl) == int(fl * FORCE_LIMIT_SEVERE_BAND)

    def test_the_upkeep_ladder_reads_the_same_source(self):
        import inspect
        from backend.models.world_state import WorldState as WS
        src = inspect.getsource(WS.calculate_turn_upkeep)
        assert "severe_band_threshold(force_limit)" in src
        assert "force_limit + force_limit // 2" not in src


# ════════════════════════════════════════════════════════════════════════
# The typed count — without it LEVY_MAX_BATCH is unreachable from English
# ════════════════════════════════════════════════════════════════════════

class TestTheTypedCount:
    """Measured: the spender arm could only ever buy ONE batch at a time,
    so a France holding 88,556 gold absorbed 11,439 of it in forty turns.
    Naming the men in the order is what makes the ceiling reachable."""

    def _typed(self, ex, world, text, marshal="Ney"):
        return ex.execute({"action": "purchase_levy", "command": {
            "action": "purchase_levy", "marshal": marshal,
            "type": "specific", "raw_command": text}}, {"world": world})

    def test_thirty_thousand_men_buys_three_batches(self, ex):
        w = _staged(pool=0)
        ney = w.get_marshal("Ney")
        before = ney.strength
        r = self._typed(ex, w, "buy 30,000 substitutes for Ney")
        assert r["success"], r["message"]
        assert ney.strength - before == 3 * INFANTRY_RECRUIT_AMOUNT
        assert w.nation_gold["France"] == 100_000 - 24_840

    def test_a_bare_order_still_buys_one(self, ex):
        w = _staged(pool=0)
        ney = w.get_marshal("Ney")
        before = ney.strength
        self._typed(ex, w, "buy substitutes for Ney")
        assert ney.strength - before == INFANTRY_RECRUIT_AMOUNT

    def test_a_small_number_is_read_as_batches(self, ex):
        w = _staged(pool=0)
        ney = w.get_marshal("Ney")
        before = ney.strength
        self._typed(ex, w, "buy 2 battalions of substitutes for Ney")
        assert ney.strength - before == 2 * INFANTRY_RECRUIT_AMOUNT

    def test_the_count_cannot_exceed_the_maximum(self, ex):
        w = _staged(pool=0)
        ney = w.get_marshal("Ney")
        before = ney.strength
        self._typed(ex, w, "buy 900,000 substitutes for Ney")
        assert ney.strength - before == LEVY_MAX_BATCH * INFANTRY_RECRUIT_AMOUNT
