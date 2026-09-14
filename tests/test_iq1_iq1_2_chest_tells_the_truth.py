"""IQ-1 IQ1-2 — "The Chest Tells the Truth": the instrument, the audit, the contract.

Row IQ-1's third slice, and like SW-0 it changes no balance at all. It goes
before the recurring sink because three of the row's four completion items
cannot be MEASURED until it lands, and because the instrument was lying in
three separate ways that a reader of the Strategic Ledger would have believed.

1. THE CEILING WAS NOT A FIXED POINT. `_build_economy` fed
   `state_charges_ceiling` the net that had ALREADY had `state_charges`
   subtracted from it. The fixed point is defined against the gold coming
   IN, so a number whose entire content is "the treasury this is steering
   toward, independent of where the treasury is now" slid with the chest.
   Measured on ONE unchanged 1805 boot world at ONE unchanged rate (80),
   varying only the treasury:

       800 -> 59,562 · 5,000 -> 56,562 · 20,000 -> 41,562
       40,000 -> 21,562 · 60,000 -> 0 · 88,556 -> 0

   against a true fixed point of 59,562 at all six. Two faces, both real:
   at rate 80 (the boot, at war) the line DISAPPEARS at a large chest,
   because `strategic_ledger.gd` renders `if ceiling > 0` and the sentinel
   had swallowed it; at rate 30 — the turn-40 peace board row IQ-1 was
   opened over — it renders 252,000 against a true 338,500, so on the
   disease arm the player was told the brake was 86,500 gold closer than
   it is. The shipped figure ALWAYS understated.

2. THE ECONOMY TAB ANSWERED FOR FRANCE WHEN ASKED ABOUT AUSTRIA.
   `"treasury": int(world.gold)` and `bankruptcy_turns` read
   `player_nation`-scoped properties while the function takes a `player`
   argument every other key in the payload honours. Measured on the boot:
   asked about Austria it reported 800 against a real 700; about Britain,
   800 against 2,000. No GR5 claim about an AI court's economy — and this
   row is going to make several — was readable until this was fixed.

3. THE DIGEST DID NOT RECONCILE, AND COULD NOT SEE THE SINK. The driver
   kept a FOURTH hand-maintained copy of the ledger's net expression and it
   had drifted: `admin_bonus` was missing, leaving a residual of exactly
   +50 on 40 of 40 LEDGER rows of both archived IQ-1 arms. And `spent`
   rendered on ZERO rows of all three archived digests — including the
   spender arm that bought 18,852 gold of substitutes — because the engine
   clears `gold_spent_this_turn` inside `advance_turn` and the driver's only
   two `/ledger` reads were the turn header and post-end-turn.

⚠ M1-M7 BEING GREEN IS WORTH NOTHING AS EVIDENCE FOR THIS ROW, and every
IQ-1 slice must say so: `tests/test_combat_sweep_metrics.py` contains zero
references to gold, income, stability, upkeep or turn advance, so it is
structurally blind to every economy change. `BASELINE_SERIES` is the only
real instrument, and for THIS slice its byte-identity is a property of the
fix rather than a fact about the harness — no gold AMOUNT changes anywhere.
"""

import ast
import io
import json
import pathlib
import re
import sys

import pytest

from backend.game_logic import ledger as ledger_mod
from backend.game_logic.ledger import (
    _build_economy, state_charges_ceiling, NET_GOLD_COMPONENTS,
    CEILING_BOUNDED, CEILING_NO_RATE, CEILING_NO_SURPLUS,
)
from backend.models.world_state import (
    WorldState, CHARGES_HOARD_FLOOR, WAR_EFFORT_DIVISOR,
)

REPO = pathlib.Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")
LEDGER_GD = (REPO / "godot-client" / "project-sovereign" / "scripts"
             / "strategic_ledger.gd")
DRIVER = REPO / "tools" / "playtest_driver.py"

# The chests the defect was measured across, and the shipped (wrong) reading
# at each. Kept as data so the negative control cannot drift from the claim.
MEASURED_DEFECT = {800: 59_562, 5_000: 56_562, 20_000: 41_562,
                   40_000: 21_562, 60_000: 0, 88_556: 0}
TRUE_FIXED_POINT = 59_562


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def lever_down():
    """Set the module global in THIS process and restore it. The slice-9
    idiom: never rewrite a production source file from a test."""
    before = ledger_mod.THE_CHEST_TELLS_THE_TRUTH
    ledger_mod.THE_CHEST_TELLS_THE_TRUTH = False
    yield
    ledger_mod.THE_CHEST_TELLS_THE_TRUTH = before


# ════════════════════════════════════════════════════════════════════════
# 1. The ceiling is a FIXED POINT — it does not move with the chest
# ════════════════════════════════════════════════════════════════════════

class TestTheCeilingIsAFixedPoint:
    def test_it_is_the_same_number_at_every_treasury(self, world):
        """The whole content of the claim. One world, one rate, six chests."""
        seen = {}
        for chest in MEASURED_DEFECT:
            world.nation_gold["France"] = chest
            econ = _build_economy(world, "France")
            seen[chest] = econ["ceiling"]
        assert set(seen.values()) == {TRUE_FIXED_POINT}, seen

    def test_the_rate_really_was_held_constant(self, world):
        """Without this the test above could pass by the rate moving to
        compensate — it would be measuring nothing."""
        rates = set()
        for chest in MEASURED_DEFECT:
            world.nation_gold["France"] = chest
            econ = _build_economy(world, "France")
            rates.add(sum(int(t.get("amount", 0))
                          for t in econ["state_charges_terms"]))
        assert len(rates) == 1, f"the rate moved across the sweep: {rates}"

    def test_the_negative_control_reproduces_the_defect(self, world, lever_down):
        """The mechanic is load-bearing: with the lever down, every one of
        the six measured wrong readings comes back, to the gold."""
        for chest, shipped in MEASURED_DEFECT.items():
            world.nation_gold["France"] = chest
            assert _build_economy(world, "France")["ceiling"] == shipped, chest

    def test_the_fix_is_the_pre_charge_gross(self, world):
        """Stated as arithmetic rather than as the production expression,
        so this cannot become the tautology the two SW-0 pins were."""
        world.nation_gold["France"] = 40_000
        econ = _build_economy(world, "France")
        rate = sum(int(t.get("amount", 0)) for t in econ["state_charges_terms"])
        gross = econ["net"] + econ["state_charges"]
        assert econ["state_charges"] > 0, "the charge must bite in this fixture"
        assert econ["ceiling"] == (
            CHARGES_HOARD_FLOOR + gross * WAR_EFFORT_DIVISOR // rate)

    def test_at_the_fixed_point_the_draw_equals_the_income(self, world):
        """What 'fixed point' MEANS, checked against the engine's own charge
        rather than against the ledger that computed it."""
        world.nation_gold["France"] = 40_000
        econ = _build_economy(world, "France")
        world.nation_gold["France"] = econ["ceiling"]
        after = _build_economy(world, "France")
        gross = after["net"] + after["state_charges"]
        # Integer division, so allow the one-gold rounding the floor implies.
        assert abs(after["state_charges"] - gross) <= 2, (
            f"charge {after['state_charges']} vs gross {gross}")


class TestTheThreeCeilingStates:
    def test_a_real_fixed_point_says_bounded(self, world):
        world.nation_gold["France"] = 20_000
        assert _build_economy(world, "France")["ceiling_state"] == CEILING_BOUNDED

    def test_no_rate_and_no_surplus_are_different_sentences(self, world):
        """They were the same zero, and they are different facts: 'nothing
        is drawing on the chest' vs 'the chest is not growing'."""
        assert CEILING_NO_RATE != CEILING_NO_SURPLUS
        assert state_charges_ceiling(4_000, 0) == 0
        assert state_charges_ceiling(0, 30) == 0

    def test_the_legacy_world_reports_unbounded(self):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT, and the INERT
        answered a question rather than asking for a better pin: swapping
        CEILING_NO_RATE for CEILING_NO_SURPLUS killed nothing, because
        nothing here had ever DRIVEN the no-rate state.

        It is reachable, and exactly once: `get_state_charges_rate` returns
        `{"rate": 0, "terms": []}` for any world whose `sovereign_map` is
        not "europe" (N1, the 19-region rollback). On a Europe world the
        crown term is unconditional, so the rate is never 0 there — which
        is the fact the pin should have been stating all along.
        """
        legacy = WorldState()
        assert getattr(legacy, "sovereign_map", "legacy") != "europe"
        assert legacy.get_state_charges_rate(legacy.player_nation)["rate"] == 0
        econ = _build_economy(legacy, legacy.player_nation)
        assert econ["ceiling_state"] == CEILING_NO_RATE
        assert econ["ceiling"] == 0

    def test_the_no_surplus_state_is_driven_too(self, world):
        """The other zero, on a Europe world that IS charged but is not
        making money — so the two arms are distinguished by behaviour and
        not merely by two different string constants."""
        # A low chest, so the CHARGE is zero and cannot mask the loss. The
        # first cut of this fixture used a 500,000 chest and failed: at that
        # size the charge (49,800) exceeds the loss, so the GROSS stays
        # positive and the state is correctly `bounded`. That is the engine
        # being right and the fixture being wrong, and it is worth keeping
        # in writing — "make the player poor" and "make the player lose
        # money" are different states here.
        world.nation_gold["France"] = 0
        for region in world.regions.values():
            if region.controller == "France":
                region.controller = "Spain"
        econ = _build_economy(world, "France")
        rate = sum(int(t.get("amount", 0)) for t in econ["state_charges_terms"])
        assert rate > 0, "a Europe world always pays the crown term"
        assert econ["net"] + econ["state_charges"] <= 0, (
            f"fixture failed to make a loser: gross "
            f"{econ['net'] + econ['state_charges']}")
        assert econ["ceiling_state"] == CEILING_NO_SURPLUS
        assert econ["ceiling"] == 0

    def test_the_state_is_absent_from_net(self, world):
        assert "ceiling_state" not in NET_GOLD_COMPONENTS
        econ = _build_economy(world, "France")
        assert econ["net"] == sum(int(econ[k]) * s
                                  for k, s in NET_GOLD_COMPONENTS.items())


# ════════════════════════════════════════════════════════════════════════
# 2. The economy tab answers for the nation it was ASKED about
# ════════════════════════════════════════════════════════════════════════

class TestItAnswersForTheCourtAsked:
    @pytest.mark.parametrize("nation", ["France", "Austria", "Britain",
                                        "Russia", "Prussia"])
    def test_the_treasury_is_that_nations_own_chest(self, world, nation):
        econ = _build_economy(world, nation)
        assert econ["treasury"] == int(world.nation_gold.get(nation, 0))

    def test_the_boot_spread_is_real(self, world):
        """The fixture must actually distinguish the nations, or the test
        above passes on a board where every chest happens to be equal."""
        chests = {n: int(world.nation_gold.get(n, 0))
                  for n in ("France", "Austria", "Britain")}
        assert len(set(chests.values())) == 3, chests

    def test_the_negative_control_reproduces_the_defect(self, world, lever_down):
        assert _build_economy(world, "Austria")["treasury"] == \
            int(world.nation_gold["France"])
        assert _build_economy(world, "Britain")["treasury"] == \
            int(world.nation_gold["France"])

    def test_the_player_case_is_byte_identical(self, world, lever_down):
        """The fix must not move the player's own reading by a single key."""
        off = _build_economy(world, "France")
        ledger_mod.THE_CHEST_TELLS_THE_TRUTH = True
        on = _build_economy(world, "France")
        for key in off:
            if key in ("ceiling", "ceiling_state"):
                continue
            assert on[key] == off[key], f"{key} moved for the player"

    def test_the_levy_answers_for_that_nation_too(self, world):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT. Reverting
        `_levy_block(world, player)` to `_levy_block(world, None)` killed
        nothing: this class only ever asserted `treasury` and
        `bankruptcy_turns`, which is precisely how the original defect —
        two of three player-scoped reads — survived in the first place."""
        fr = _build_economy(world, "France")["levy"]
        au = _build_economy(world, "Austria")["levy"]
        assert fr["force_limit"] != au["force_limit"], (
            "the levy block is answering for one nation on both queries")
        assert au["force_limit"] == int(world.get_force_limit("Austria") or 0)
        assert (au["infantry_pool"]
                == int(world.manpower_pools.get("Austria", {}).get("infantry", 0)))

    def test_the_whole_payload_agrees_about_whose_economy_it_is(self, world):
        """The defect was a payload contradicting itself. State that as one
        assertion over every nation-shaped key at once."""
        for nation in ("Austria", "Britain", "Russia"):
            econ = _build_economy(world, nation)
            assert econ["treasury"] == int(world.nation_gold.get(nation, 0))
            assert econ["levy"]["force_limit"] == int(
                world.get_force_limit(nation) or 0)
            assert econ["army_strength_total"] == int(
                world.calculate_turn_upkeep(nation).get("total_strength", 0))

    def test_bankruptcy_is_per_nation_too(self, world):
        world.nation_bankruptcy_turns["Austria"] = 3
        assert _build_economy(world, "Austria")["bankruptcy_turns"] == 3
        assert _build_economy(world, "France")["bankruptcy_turns"] == 0


# ════════════════════════════════════════════════════════════════════════
# 3. One canonical map — the ledger is the source of its own truth
# ════════════════════════════════════════════════════════════════════════

class TestOneCanonicalComponentMap:
    def test_the_map_reconciles_net_exactly(self, world):
        econ = _build_economy(world, "France")
        assert sum(int(econ[k]) * s
                   for k, s in NET_GOLD_COMPONENTS.items()) == econ["net"]

    def test_the_reconciliation_test_imports_it(self):
        src = (REPO / "tests" / "test_economy_ledger_reconciliation.py").read_text(
            encoding="utf-8")
        assert "from backend.game_logic.ledger import NET_GOLD_COMPONENTS" in src
        assert not re.search(r"^NET_GOLD_COMPONENTS = \{", src, re.M), (
            "the third hand-maintained copy is back")

    def test_the_driver_imports_it_too(self):
        src = DRIVER.read_text(encoding="utf-8")
        assert "NET_GOLD_COMPONENTS as _ENGINE_NET_COMPONENTS" in src

    def test_the_drivers_display_set_covers_the_canonical_map(self):
        """The +50 residual, as a standing gate. The digest folds
        upkeep_base + upkeep_surcharge into one `upkeep` row on purpose —
        `total == base + surcharge` is a pinned ES-3 invariant — and any
        OTHER divergence is drift of the kind this slice exists to end."""
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv
        shown = {k for k, _ in drv.NET_COMPONENTS}
        unfolded = (shown - set(drv.NET_COMPONENTS_FOLDED)) | {
            x for pair in drv.NET_COMPONENTS_FOLDED.values() for x in pair}
        assert unfolded == set(NET_GOLD_COMPONENTS), (
            f"missing {set(NET_GOLD_COMPONENTS) - unfolded}, "
            f"extra {unfolded - set(NET_GOLD_COMPONENTS)}")

    def test_admin_bonus_is_the_component_that_was_missing(self):
        """Name the defect, so a future reader knows what this guards."""
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv
        assert "admin_bonus" in {k for k, _ in drv.NET_COMPONENTS}
        assert "admin_bonus" in NET_GOLD_COMPONENTS

    def test_the_driver_signs_are_derived_not_restated(self):
        """⚠ REWRITTEN BY THE REVIEW ROUND. The first cut asserted a subset
        and one absent key — which a hand-written literal satisfies, so it
        could not tell derived from restated, and it would have passed with a
        set that wrongly negated a POSITIVE component. Assert the EXACT set,
        derived here the same way, and assert no positive component is in it."""
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv
        expected = {k for k, sign in NET_GOLD_COMPONENTS.items() if sign < 0}
        # `upkeep` is the declared fold (base + surcharge), so it is the one
        # member with no canonical counterpart. Nothing else may differ.
        assert drv._NET_NEGATIVE_KEYS - expected == {"upkeep"}
        assert expected - drv._NET_NEGATIVE_KEYS == set()
        positives = {k for k, sign in NET_GOLD_COMPONENTS.items() if sign > 0}
        assert not (positives & drv._NET_NEGATIVE_KEYS), (
            "a POSITIVE component is being negated by the digest")


# ════════════════════════════════════════════════════════════════════════
# 4. The fifteen outflows are judged, row by row
# ════════════════════════════════════════════════════════════════════════

from tests.test_iq1_sw0_chest_speaks import (  # noqa: E402
    _is_nation_gold_target, UNRECORDED_OUTFLOWS,
)


def _gold_subtracting_functions():
    out = {}
    for path in sorted((REPO / "backend").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            subs = False
            for node in ast.walk(fn):
                if isinstance(node, ast.AugAssign):
                    if not isinstance(node.op, ast.Sub):
                        continue
                    targets = [node.target]
                elif isinstance(node, ast.Assign):
                    if not any(isinstance(n, ast.BinOp)
                               and isinstance(n.op, ast.Sub)
                               for n in ast.walk(node.value)):
                        continue
                    targets = node.targets
                else:
                    continue
                # IQ1-2 review round: this matched ONLY
                # `<x>.nation_gold[...]` (an Attribute value), so a function
                # that takes a LOCAL ALIAS first —
                # `nation_gold = world.nation_gold; nation_gold[p] = b - t` —
                # was invisible to it. Two real production outflows were
                # escaping (settlement_offers, settlement_ratify), so the
                # coverage claim was 22 of 24 and a NEW outflow written in that
                # idiom would have red nothing. A bare Name target counts too.
                for t in targets:
                    if _is_nation_gold_target(t):
                        subs = True
            if not subs:
                continue
            rec = any(isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Attribute)
                      and n.func.attr == "record_gold_spent"
                      for n in ast.walk(fn))
            out[(str(path.relative_to(REPO)).replace("\\", "/"), fn.name)] = rec
    return out


# The seven that MOVED, with what they buy. A player purchase belongs in the
# turn's `Spent` line; that is the whole disposition rule.
MOVED_TO_SPENT = {
    ("backend/commands/naval_executor.py", "_execute_build_fleet"),
    ("backend/commands/diplomatic_executor.py", "_execute_buy_off_design"),
    ("backend/commands/diplomatic_executor.py", "_execute_make_amends"),
    ("backend/commands/diplomatic_executor.py",
     "_execute_make_amends_grievance_variant"),
    ("backend/commands/diplomatic_executor.py", "_apply_ultimatum_demands"),
    ("backend/game_logic/vassal.py", "invest_in_vassal"),
    ("backend/game_logic/vassal.py", "attempt_vassal_bribe"),
}


class TestTheOutflowsAreJudged:
    def test_the_seven_purchases_now_record(self):
        found = _gold_subtracting_functions()
        for site in sorted(MOVED_TO_SPENT):
            assert site in found, f"{site} no longer subtracts gold at all"
            assert found[site], f"{site} still does not record its spend"

    def test_the_allowlist_is_exactly_the_ten_survivors(self):
        """⚠ REVIEW ROUND: this said EIGHT. It is TEN, and the two extra were
        not "kept" — they were INVISIBLE to a census that matched only
        `<x>.nation_gold[...]` and so could not see a local alias. The
        coverage claim was 22 of 24. Both are settlement transfers and both
        are disposition (B), owner IQ1-3a."""
        assert len(UNRECORDED_OUTFLOWS) == 10
        assert not (MOVED_TO_SPENT & UNRECORDED_OUTFLOWS)
        for late in (("backend/game_logic/settlement_offers.py",
                      "process_recurring_settlement_payments"),
                     ("backend/game_logic/settlement_ratify.py",
                      "_apply_settlement_terms")):
            assert late in UNRECORDED_OUTFLOWS

    def test_the_census_sees_a_local_alias(self):
        """The sensitivity arm for the widening itself: a function that
        aliases `nation_gold` to a local and then subtracts through the alias
        must be FOUND. Without this the widening could be reverted silently."""
        import ast as _ast
        src = (REPO / "backend/game_logic/settlement_ratify.py").read_text(
            encoding="utf-8")
        tree = _ast.parse(src)
        hits = []
        for fn in _ast.walk(tree):
            if not isinstance(fn, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                continue
            for node in _ast.walk(fn):
                if isinstance(node, _ast.Assign):
                    for t in node.targets:
                        if (isinstance(t, _ast.Subscript)
                                and isinstance(t.value, _ast.Name)
                                and t.value.id == "nation_gold"):
                            hits.append(fn.name)
        assert "_apply_settlement_terms" in hits, (
            "the bare-alias idiom this census was widened for is gone — "
            "re-check whether the widening is still needed")
        found = _gold_subtracting_functions()
        assert ("backend/game_logic/settlement_ratify.py",
                "_apply_settlement_terms") in found

    def test_every_survivor_states_its_reason_at_the_call_site(self):
        """GR9: SW-0 deferred this to 'a later slice' with no slice id. A
        survivor without a written reason is an open-ended deferral."""
        for rel, fn_name in sorted(UNRECORDED_OUTFLOWS):
            src = (REPO / rel).read_text(encoding="utf-8")
            tree = ast.parse(src)
            body = None
            for fn in ast.walk(tree):
                if (isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and fn.name == fn_name):
                    lines = src.splitlines()[fn.lineno - 1:fn.end_lineno]
                    body = "\n".join(lines)
            assert body is not None, f"{rel}::{fn_name} not found"
            assert "IQ1-2 (3)" in body, (
                f"{rel}::{fn_name} stays unrecorded with no stated reason")

    def test_the_reasons_are_not_vacuous(self):
        """⚠ REWRITTEN BY THE REVIEW ROUND. The first cut asserted that two
        function NAMES exist in vassal.py and nothing whatsoever about the
        markers its own docstring said it guarded — it would have passed with
        every reason deleted.

        What it must prove is that the marker is read from the FUNCTION BODY
        and not from anywhere in the file: `vassal.py` contains BOTH a
        recorded purchase (`invest_in_vassal`) and an unrecorded survivor
        (`process_vassal_tribute`), so a file-wide grep cannot tell them
        apart and this asserts the per-function reader does."""
        src = (REPO / "backend/game_logic/vassal.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        bodies = {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                bodies[fn.name] = "\n".join(
                    src.splitlines()[fn.lineno - 1:fn.end_lineno])
        assert "IQ1-2 (3)" in bodies["process_vassal_tribute"], (
            "the survivor's reason is not in its own body")
        # …and the marker is NOT smeared across the whole file: a function in
        # the same module that is neither a survivor nor a purchase must be
        # clean, or the per-function read proves nothing.
        clean = [n for n, b in bodies.items()
                 if "IQ1-2 (3)" not in b and "record_gold_spent" not in b]
        assert clean, "every function in vassal.py carries the marker — the "
        assert "IQ1-2 (3)" in src

    def test_the_amount_recorded_is_the_amount_subtracted(self, world):
        """⚠ ADDED BY THE REVIEW ROUND, which was right that the seven sites
        were pinned by a PRESENCE census only — blind to the amount, to the
        nation, and to whether the call is reachable at all. Driven for real
        through the production function, both ways round.

        ⚠ The first cut of this fixture did not reach the spend: the boot
        vassals sit at LOYALTY_MAX and the verb refuses there by design (WO-D2
        contract 6, "charges NOTHING"). Which makes the refusal the other half
        of the pin, and the more valuable half — a recorder outside its own
        branch would charge a refused purchase.
        """
        from backend.game_logic import vassal as vassal_mod
        from backend.game_logic.vassal import INVEST_GOLD_COST, LOYALTY_MAX

        target = next(iter(getattr(world, "vassals", {}) or {}), None)
        assert target, "the 1805 boot world has vassals — fixture precondition"
        lord = world.vassals[target]["lord"]

        # (a) THE REFUSAL RECORDS NOTHING. Loyalty at max, so the verb refuses.
        world.vassals[target]["loyalty"] = LOYALTY_MAX
        world.gold_spent_this_turn = {}
        world.nation_gold[lord] = 5_000
        refused = vassal_mod.invest_in_vassal(world, target, actor=lord)
        assert refused.get("success") is False
        assert int(world.nation_gold.get(lord, 0)) == 5_000, "a refusal charged"
        assert int(world.gold_spent_this_turn.get(lord, 0)) == 0, (
            "a REFUSED purchase was recorded as a spend")

        # (b) THE SPEND RECORDS EXACTLY WHAT LEFT THE CHEST.
        world.vassals[target]["loyalty"] = 40
        world.vassal_investment_cooldowns = {}
        world.nation_dp = getattr(world, "nation_dp", {}) or {}
        world.nation_dp[lord] = 10
        world.gold_spent_this_turn = {}
        world.nation_gold[lord] = 5_000
        ok = vassal_mod.invest_in_vassal(world, target, actor=lord)
        assert ok.get("success") is True, ok.get("message")
        moved = 5_000 - int(world.nation_gold.get(lord, 0))
        recorded = int(world.gold_spent_this_turn.get(lord, 0))
        assert moved == INVEST_GOLD_COST
        assert recorded == moved, (
            f"recorded {recorded} but {moved} left the chest")
        # …and against the RIGHT nation, not the player by reflex.
        assert set(world.gold_spent_this_turn) == {lord}

    def test_each_recorder_names_the_amount_its_own_site_subtracts(self):
        """⚠ SYNTHESIS ROUND (IQ12-P3): six of the seven sites had no pin that
        could see a WRONG AMOUNT or a WRONG NATION — only a presence census and
        an indent census, neither of which reads the arguments.

        Driving all seven through production would need seven fixtures; what
        is cheap and binding is to assert each recorder's ARGUMENTS against the
        subtraction beside it, by name. A recorder handed a different constant,
        or a different nation variable, reds here."""
        expected = {
            ("backend/commands/naval_executor.py", "naval.SHIP_COST", "actor"),
            ("backend/commands/diplomatic_executor.py", "amount", "player"),
            ("backend/commands/diplomatic_executor.py",
             "self._MAKE_AMENDS_GOLD_COST", "player"),
            ("backend/commands/diplomatic_executor.py",
             "self._MAKE_AMENDS_GRIEVANCE_GOLD_COST", "player"),
            ("backend/commands/diplomatic_executor.py", "transfer",
             "target_nation"),
            ("backend/game_logic/vassal.py", "INVEST_GOLD_COST", "lord"),
            ("backend/game_logic/vassal.py", "BRIBE_FREE_COST // 2", "nation"),
            ("backend/game_logic/vassal.py", "BRIBE_TRANSFER_COST", "nation"),
            ("backend/game_logic/vassal.py", "BRIBE_FREE_COST", "nation"),
        }
        found = set()
        for rel in {e[0] for e in expected}:
            src = (REPO / rel).read_text(encoding="utf-8")
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "record_gold_spent"):
                    continue
                # AST, not a line parser: the grievance-variant call WRAPS
                # across two lines and a line parser read it as empty — which
                # is how the first cut of this pin failed.
                nation = ast.unparse(node.args[0])
                amount = ast.unparse(node.args[1])
                if amount.startswith("int(") and amount.endswith(")"):
                    amount = amount[4:-1]
                found.add((rel, amount.strip(), nation.strip()))
        assert found == expected, (
            f"recorder arguments drifted.\n  unexpected: {sorted(found - expected)}"
            f"\n  missing:    {sorted(expected - found)}")

    def test_no_recorder_is_handed_the_player_by_reflex(self):
        """The GR5 half, structurally: not one of the nine calls may name
        `player_nation`. The nation recorded is always the nation debited."""
        for rel in ("backend/commands/naval_executor.py",
                    "backend/commands/diplomatic_executor.py",
                    "backend/game_logic/vassal.py"):
            for line in (REPO / rel).read_text(encoding="utf-8").splitlines():
                if "record_gold_spent(" in line and not line.strip().startswith("#"):
                    assert "player_nation" not in line, (
                        f"{rel}: a recorder names player_nation — an AI court's "
                        f"purchase would be charged to the player: {line.strip()}")

    def test_a_non_player_lord_is_charged_against_itself(self, world):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT, and it is the GR5
        half. Re-pointing the recorder at `world.player_nation` killed nothing,
        because on the shipped 1805 board every vassal's lord IS France, which
        IS the player — so "records the lord" and "records the player" are the
        same assertion there, and a GR5 defect would have been invisible.

        Give the vassal a lord who is not the player and the two come apart.
        """
        from backend.game_logic import vassal as vassal_mod
        from backend.game_logic.vassal import INVEST_GOLD_COST, LOYALTY_MAX

        target = next(iter(getattr(world, "vassals", {}) or {}), None)
        assert target
        lord = "Austria"
        assert lord != world.player_nation, "fixture precondition"
        world.vassals[target]["lord"] = lord
        world.vassals[target]["loyalty"] = min(40, LOYALTY_MAX - 1)
        world.vassal_investment_cooldowns = {}
        world.nation_dp = getattr(world, "nation_dp", {}) or {}
        world.nation_dp[lord] = 10
        world.nation_gold[lord] = 5_000
        world.gold_spent_this_turn = {}

        ok = vassal_mod.invest_in_vassal(world, target, actor=lord)
        assert ok.get("success") is True, ok.get("message")
        assert int(world.gold_spent_this_turn.get(lord, 0)) == INVEST_GOLD_COST
        assert world.player_nation not in world.gold_spent_this_turn, (
            "an AI lord's purchase was charged to the PLAYER's Spent line")

    def test_the_clamped_ultimatum_records_what_moved_not_what_was_asked(self):
        """The clamp, stated as arithmetic over the production expression:
        `transfer = min(int(value), max(0, available))` and the recorder is
        handed `transfer`. A recorder handed `value` would over-report every
        time a court cannot pay in full."""
        src = (REPO / "backend/commands/diplomatic_executor.py").read_text(
            encoding="utf-8")
        idx = src.index("world.record_gold_spent(target_nation, int(transfer))")
        window = src[max(0, idx - 700):idx]
        assert "transfer = min(int(value), max(0, available))" in window, (
            "the ultimatum recorder is no longer downstream of the clamp")
        assert "record_gold_spent(target_nation, int(value))" not in src, (
            "the ultimatum records the DEMAND, not the gold that moved")

    def test_every_recorder_sits_with_its_own_subtraction(self):
        """A record outside the conditional that guards the subtraction would
        report a spend on a REFUSED purchase.

        ⚠ The first cut of this pin asserted an absolute indent >= 8 and was
        simply WRONG about the code: `invest_in_vassal` validates and returns
        early, so its subtraction and its recorder both sit at function-body
        level. The real invariant is that the recorder matches the INDENT of
        the `nation_gold` write it accompanies — same branch, same guard.
        """
        for rel in ("backend/commands/naval_executor.py",
                    "backend/game_logic/vassal.py",
                    "backend/commands/diplomatic_executor.py"):
            lines = (REPO / rel).read_text(encoding="utf-8").splitlines()
            recorders = [i for i, ln in enumerate(lines)
                         if "record_gold_spent(" in ln
                         and not ln.strip().startswith("#")]
            assert recorders, f"{rel}: no recorder found"
            for i in recorders:
                indent = len(lines[i]) - len(lines[i].lstrip())
                # Walk back to the nearest `nation_gold` write and require the
                # same indentation — i.e. the same branch.
                near = None
                for j in range(i - 1, max(0, i - 12), -1):
                    if "nation_gold[" in lines[j] and "=" in lines[j]:
                        near = len(lines[j]) - len(lines[j].lstrip())
                        break
                assert near is not None, (
                    f"{rel}:{i + 1} records a spend with no nearby "
                    f"nation_gold write — is it still beside its subtraction?")
                assert indent == near, (
                    f"{rel}:{i + 1} recorder indent {indent} != subtraction "
                    f"indent {near} — it may be outside the guarding branch")

    def test_the_residual_detects_a_dropped_component(self):
        """⚠ ADDED BY THE REVIEW ROUND: `net_residual` is the slice's own
        drift detector and it had NO behavioural pin and no sweep mutation, so
        a sign error would ship silently. Drive the recorder's arithmetic and
        assert both the zero case and the +50 the archive actually showed."""
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv

        class Stub:
            def __init__(self):
                self.md = []
                self.rec = []

            def _md(self, text):
                self.md.append(text)

            def record(self, kind, **kw):
                self.rec.append((kind, kw))

            ledger_line = drv.Digest.ledger_line

        econ = {"income": 3550, "trade_income": 620, "admin_bonus": 50,
                "overseas": 0, "vassal_tribute": 937, "treaty_gold": 0,
                "settlement_gold": 0, "requisitions": 0, "upkeep": 624,
                "state_charges": 1038, "contributions": 0, "occupation": 15,
                "blockade": 0, "admiralty": 480, "infrastructure": 0,
                "dotation_skim": 0, "rente_cost": 0}
        net = 3550 + 620 + 50 + 937 - 624 - 1038 - 15 - 480

        good = Stub()
        good.ledger_line(1000, net, 40, 29, economy=econ)
        rows = [kw for kind, kw in good.rec if kind == "economy"]
        assert rows and rows[0]["net_residual"] == 0, rows

        # Drop `admin_bonus` — the exact archived defect — and the residual
        # must read +50, i.e. "the printed sub-line UNDER-counts by 50".
        blind = Stub()
        without = {k: v for k, v in econ.items() if k != "admin_bonus"}
        blind.ledger_line(1000, net, 40, 29, economy=without)
        rows = [kw for kind, kw in blind.rec if kind == "economy"]
        assert rows and rows[0]["net_residual"] == 50, (
            f"expected +50 (under-count), got {rows[0]['net_residual']} — "
            f"the SIGN is the thing every prose statement of this defect uses")

    def test_the_census_still_reds_on_a_new_unrecorded_outflow(self):
        """⚠ REWRITTEN BY THE REVIEW ROUND. The first cut asserted
        `len(found) >= 22` and `sum(...) >= 14` — two LOWER BOUNDS, which a
        new unrecorded outflow satisfies happily. The census's actual
        contract is the EXACT-MATCH allowlist, so state it, and drive the
        failure by synthesising a new outflow on a temp module."""
        found = _gold_subtracting_functions()
        unrecorded = {k for k, rec in found.items() if not rec}
        assert unrecorded == UNRECORDED_OUTFLOWS, (
            f"new unrecorded outflow(s): {sorted(unrecorded - UNRECORDED_OUTFLOWS)}; "
            f"newly recorded: {sorted(UNRECORDED_OUTFLOWS - unrecorded)}")

    def test_the_census_would_actually_see_a_new_outflow(self, tmp_path):
        """The sensitivity arm the bound-based pin never had: run the census's
        own AST logic over a synthesised module that subtracts from
        `nation_gold` without recording, and assert it is FOUND — through both
        idioms, attribute and local alias."""
        probe = tmp_path / "probe.py"
        probe.write_text(
            "def attribute_form(world, n, amount):\n"
            "    world.nation_gold[n] = world.nation_gold.get(n, 0) - amount\n"
            "\n"
            "def alias_form(world, n, amount):\n"
            "    nation_gold = world.nation_gold\n"
            "    nation_gold[n] = nation_gold.get(n, 0) - amount\n",
            encoding="utf-8")
        tree = ast.parse(probe.read_text(encoding="utf-8"))
        seen = set()
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(fn):
                targets = (node.targets if isinstance(node, ast.Assign)
                           else [node.target] if isinstance(node, ast.AugAssign)
                           else [])
                if any(_is_nation_gold_target(t) for t in targets):
                    seen.add(fn.name)
        assert seen == {"attribute_form", "alias_form"}, (
            f"the census cannot see {{'attribute_form','alias_form'}} - {seen}")


# ════════════════════════════════════════════════════════════════════════
# 5. The digest can see the sink
# ════════════════════════════════════════════════════════════════════════

class TestTheDigestCanSeeTheSink:
    def test_there_is_a_read_before_the_turn_ends(self):
        """`spent` is cleared by `advance_turn`, so a post-end-turn read is
        structurally always zero — which is why it rendered on 0 of 117
        archived rows including the arm that bought 18,852 gold."""
        src = DRIVER.read_text(encoding="utf-8")
        idx_read = src.index("digest.observe_spend(_pre_econ)")
        idx_end = src.index('transport.post("/command", {"command": "end turn"})')
        assert idx_read < idx_end, "the read must precede the end turn"
        # …and the FLUSH must follow it, because the turn_end event carries the
        # auto-advance figure (synthesis round). Ordering both ways round.
        idx_flush = src.index("digest.turn_spend(None)")
        idx_fold = src.index("digest.observe_end_turn_spend(response)")
        assert idx_end < idx_fold < idx_flush, (
            "the structured turn_end spend must be folded in before the flush")

    def test_the_producer_is_not_inside_ledger_line(self):
        """`ledger_line` IS borrowed by a stub (the module comment records
        it), so a transport call inside it breaks from a distance."""
        src = DRIVER.read_text(encoding="utf-8")
        start = src.index("    def ledger_line(")
        end = src.index("    def dispatch(", start)
        assert "transport.get" not in src[start:end]

    def test_turn_spend_prints_only_when_something_was_bought(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv

        class Stub:
            def __init__(self):
                self.md = []
                self.rec = []

            def _md(self, text):
                self.md.append(text)

            def record(self, kind, **kw):
                self.rec.append((kind, kw))

            turn_spend = drv.Digest.turn_spend
            observe_spend = drv.Digest.observe_spend

        quiet = Stub()
        quiet.turn_spend({"spent": 0})
        assert quiet.md == [] and quiet.rec == []

        absent = Stub()
        absent.turn_spend(None)
        assert absent.md == []

        bought = Stub()
        bought.turn_spend({"spent": 654, "treasury": 1200})
        assert bought.md and "654" in bought.md[0]
        assert bought.rec and bought.rec[0][0] == "turn_spend"

        # Review round: the HIGH-WATER MARK. `/command` auto-ends the turn on
        # the last action point and the engine clears the tally then, so a
        # single read before `end turn` missed a purchase made with the last
        # AP. The peak survives a later reading of ZERO.
        peak = Stub()
        peak.observe_spend({"spent": 8189, "treasury": 15412})
        peak.turn_spend({"spent": 0})
        assert peak.md and "8189" in peak.md[0]

        # …and it RESETS, or turn 2 would inherit turn 1's figure.
        assert int(getattr(peak, "_turn_spend_peak", 0) or 0) == 0
        peak.md.clear()
        peak.turn_spend({"spent": 0})
        assert peak.md == []

        # ⚠ And `turn_spend` must NOT call another borrowed method: a stub
        # that borrows only `turn_spend` must still work. This pin caught
        # exactly that regression when the peak logic was first factored out.
        class Lone:
            def __init__(self):
                self.md = []
                self.rec = []

            def _md(self, text):
                self.md.append(text)

            def record(self, kind, **kw):
                self.rec.append((kind, kw))

            turn_spend = drv.Digest.turn_spend

        lone = Lone()
        lone.turn_spend({"spent": 400, "treasury": 900})
        assert lone.md and "400" in lone.md[0]

    def test_the_auto_advance_spend_is_not_lost(self):
        """⚠ SYNTHESIS ROUND (IQ12-R2). `/command` auto-ends the turn on the
        last action point and clears the tally inside that same call, so the
        pre-`end turn` read missed the purchase. The first record called that
        "a stated limit — the figure is in the end-turn banner the digest
        already prints", which was FALSE (the digest prints only the message's
        first line; the archived spender digest has zero `| Spent:`). It is
        closed by reading the STRUCTURED `spent` on the turn_end event.

        `test_there_is_a_read_before_the_turn_ends` is a source-index
        comparison and is structurally blind to a second clear site; this
        drives the producer."""
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv

        class Stub:
            def __init__(self):
                self.md = []
                self.rec = []

            def _md(self, text):
                self.md.append(text)

            def record(self, kind, **kw):
                self.rec.append((kind, kw))

            observe_spend = drv.Digest.observe_spend
            observe_end_turn_spend = drv.Digest.observe_end_turn_spend
            turn_spend = drv.Digest.turn_spend

        # The auto-advance case: the /ledger read sees a CLEARED tally (0),
        # and only the turn_end event carries the figure.
        st = Stub()
        st.observe_spend({"spent": 0, "treasury": 900})
        st.observe_end_turn_spend({"events": [
            {"type": "turn_end", "spent": 4012, "treasury": 900}]})
        st.turn_spend(None)
        assert st.md and "4012" in st.md[0], (
            "a purchase made with the last action point is still lost")
        rows = [kw for kind, kw in st.rec if kind == "turn_spend"]
        assert rows and rows[0]["spent"] == 4012

        # And the ordinary case still wins when it is larger, so folding the
        # event cannot UNDERSTATE a turn the mid-turn read saw whole.
        st2 = Stub()
        st2.observe_spend({"spent": 8189, "treasury": 15412})
        st2.observe_end_turn_spend({"events": [
            {"type": "turn_end", "spent": 0, "treasury": 15412}]})
        st2.turn_spend(None)
        assert st2.md and "8189" in st2.md[0]

        # A response with no turn_end event must be harmless.
        st3 = Stub()
        st3.observe_end_turn_spend({"events": [{"type": "battle"}]})
        st3.observe_end_turn_spend(None)
        st3.turn_spend(None)
        assert st3.md == []

    def test_the_banner_source_the_first_record_named_is_not_captured(self):
        """Pin the measurement that killed the false mitigation, so nobody
        re-asserts it: `Digest.command` prints the message's FIRST LINE only,
        and the archived digests carry no banner component at all."""
        src = DRIVER.read_text(encoding="utf-8")
        start = src.index("    def command(")
        body = src[start:src.index("\n    def ", start + 10)]
        assert "first_line(" in body, (
            "if command() now prints the whole message, re-check whether the "
            "banner reaches the digest and update the record")
        archived = (REPO / "docs/audits/playtest_digests"
                    / "iq12-spender-cmd-historical" / "digest.md").read_text(
                        encoding="utf-8")
        for banner in ("| Spent:", "| Treasury:", "| Upkeep:"):
            assert banner not in archived, (
                f"{banner} now reaches the archive — the 'stated limit' the "
                f"first record claimed would have been true after all")

    def test_the_army_reaches_the_ledger_row(self):
        src = DRIVER.read_text(encoding="utf-8")
        assert 'army=((body or {}).get("economy") or {}).get(' in src
        assert '"army_strength_total"' in src

    def test_the_army_key_is_where_the_driver_looks_for_it(self, world):
        """Navigate by the payload, not by hope: the key is in `economy`,
        not in `forces`, and the first cut of this slice read `forces`."""
        econ = _build_economy(world, "France")
        assert isinstance(econ.get("army_strength_total"), int)
        assert econ["army_strength_total"] > 0

    def test_the_residual_is_recorded(self):
        src = DRIVER.read_text(encoding="utf-8")
        assert "net_residual" in src

    def test_the_ledger_row_does_not_record_the_dead_spent_key(self):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT. Re-adding
        `spent=spent` to the LEDGER record killed nothing. That read runs
        AFTER the turn ends, when the engine has cleared the tally, so it
        recorded a FALSE 0 into the jsonl beside `turn_spend`'s true figure —
        worse than recording nothing, because an archived run then has two
        disagreeing answers."""
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv

        class Stub:
            def __init__(self):
                self.md = []
                self.rec = []

            def _md(self, text):
                self.md.append(text)

            def record(self, kind, **kw):
                self.rec.append((kind, kw))

            ledger_line = drv.Digest.ledger_line

        st = Stub()
        st.ledger_line(1000, 500, 40, 29, economy={"income": 500, "spent": 0})
        rows = [kw for kind, kw in st.rec if kind == "ledger"]
        assert rows, "no ledger row recorded"
        assert "spent" not in rows[0], (
            "the LEDGER row records `spent`, which is structurally zero on "
            "that read — the live figure is turn_spend's")
        assert "ceiling_state" in rows[0], (
            "which of the two zeros `ceiling` means must be recorded")


# ════════════════════════════════════════════════════════════════════════
# 6. The client renders all three states
# ════════════════════════════════════════════════════════════════════════

class TestTheClientRendersTheThreeStates:
    def _gd(self):
        return LEDGER_GD.read_text(encoding="utf-8")

    def test_the_state_key_is_read(self):
        assert 'econ.get("ceiling_state"' in self._gd()

    @pytest.mark.parametrize("state", ["unbounded", "no_surplus"])
    def test_each_sentinel_has_its_own_sentence(self, state):
        src = self._gd()
        assert f'ceiling_state == "{state}"' in src

    def test_the_above_the_ceiling_case_has_copy(self):
        """⚠ DOCSTRING CORRECTED BY THE REVIEW ROUND. This said the case
        "could not previously be rendered at all". It was rendered — by the
        generic arm, with the wrong sentence and often the calm colour. What
        was unreachable was a ceiling below the chest that is also CORRECT."""
        src = self._gd()
        assert "treasury > ceiling" in src
        assert "drawing it down" in src

    def test_the_false_claim_cannot_return_unmarked(self):
        """⚠ SYNTHESIS ROUND. The FALSE claim "could not previously be
        rendered" was in FOUR places; the review round corrected two and wrote
        "Corrected in both places" over the partial fix — this repo's own
        named failure mode,
        committed in the very sentence that fixed the first instance of it.

        So the completeness statement is DERIVED from here instead of written
        from memory: every surviving occurrence of the phrase must sit beside a
        FALSE/CORRECTION marker, i.e. be part of the correction rather than the
        claim.
        """
        # Assembled rather than written, so this pin's OWN definition of the
        # phrase is not an occurrence of it. (The first cut flagged itself.)
        phrase = " ".join(["could", "not", "previously", "be", "rendered"])
        targets = [
            REPO / "backend/game_logic/ledger.py",
            REPO / "docs/IMPROVEMENT_QUEUE_SPEC.md",
            REPO / "godot-client/project-sovereign/scripts/strategic_ledger.gd",
            REPO / "tests/test_iq1_iq1_2_chest_tells_the_truth.py",
        ]
        unmarked = []
        for path in targets:
            lines = path.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines):
                if phrase not in line:
                    continue
                # ⚠ The window looks BACKWARD only. A mutation proved the
                # first cut inert: re-asserting the claim on a line whose
                # CORRECTION block follows it passed happily, because the
                # marker was in the forward half of the window. A correction
                # announces itself before it quotes the thing it corrects.
                window = "\n".join(lines[max(0, i - 6):i + 1])
                # Marker ROOTS, not whole words: the first cut listed
                # "CORRECTION" and missed a docstring that says "CORRECTED".
                if not any(m in window for m in ("FALSE", "false", "CORRECT",
                                                 "wrong", "is not")):
                    unmarked.append(f"{path.name}:{i + 1}")
        assert not unmarked, (
            f"the phrase stands unmarked (i.e. as a CLAIM) at: {unmarked}")

    def test_the_measured_band_is_on_the_record(self):
        """The correction has to carry its measurement or it is just a
        different assertion. 29 of 58 probed chests rendered the case."""
        spec = (REPO / "docs/IMPROVEMENT_QUEUE_SPEC.md").read_text(
            encoding="utf-8")
        assert "29 of 58" in spec
        assert "30,562" in spec

    def test_the_worst_state_is_not_the_calmest_colour(self):
        """Review round: `no_surplus` — the treasury not growing at all — was
        rendered in COLOR_DIMMED, calmer than the informational bounded line.
        Pin the ladder so the inversion cannot come back."""
        src = self._gd()
        block = src[src.index('ceiling_state == "no_surplus"'):]
        block = block[:block.index("elif ceiling > 0")]
        assert "COLOR_ERROR" in block, "the worst ceiling state must not be dimmed"
        assert "COLOR_DIMMED" not in block

    def test_the_unbounded_copy_names_the_charges_not_the_chest(self):
        """Review round: "nothing is drawing on the chest" prints ~20 lines
        under an Upkeep line that is drawing on it."""
        src = self._gd()
        block = src[src.index('ceiling_state == "unbounded"'):]
        block = block[:block.index('elif ceiling_state')]
        # Read only the RENDERED lines — a comment explaining the old copy
        # legitimately quotes it, and the first cut of this pin failed on its
        # own explanation.
        rendered = "\n".join(ln for ln in block.splitlines()
                              if "bbcode" in ln or "[color" in ln or "Ceiling" in ln)
        assert "charges of empire do not draw" in rendered
        assert "nothing is drawing on the chest" not in rendered

    def test_the_gd_literals_are_the_backend_constants(self):
        """Review round, found by THREE lenses independently: the three render
        arms were joined to the backend's three constants by nothing at all, so
        renaming a sentinel's VALUE would silently blank the Ceiling line with
        every pin green. Assert the actual values appear in the .gd."""
        src = self._gd()
        for const in (CEILING_NO_RATE, CEILING_NO_SURPLUS):
            assert f'ceiling_state == "{const}"' in src, (
                f"the .gd does not branch on {const!r} — the backend constant "
                f"and the client literal have drifted apart")
        assert CEILING_BOUNDED == "bounded"
        assert 'econ.get("ceiling_state", "bounded")' in src, (
            "the .gd default must be CEILING_BOUNDED's value")

    def test_the_census_is_not_vacuous(self):
        """⚠ REWRITTEN BY THE REVIEW ROUND. The first cut wrote a mutated copy
        to a temp file and asserted the mutation had happened — a `str.replace`
        tautology that executed ZERO production code and was the only claimed
        sensitivity arm for the slice's only `.gd`.

        The real question is whether the assertion binds to the RENDER path
        rather than to a passing mention, so require the key read and the
        branch on it to sit inside `_render_economy` itself."""
        src = self._gd()
        start = src.index("func _render_economy")
        nxt = src.find("\nfunc ", start + 1)
        body = src[start:nxt if nxt != -1 else len(src)]
        assert 'econ.get("ceiling_state"' in body, (
            "ceiling_state is read somewhere, but not in _render_economy")
        for const in (CEILING_NO_RATE, CEILING_NO_SURPLUS):
            assert f'"{const}"' in body
        assert "Ceiling:" in body


# ════════════════════════════════════════════════════════════════════════
# 7. A player can learn the sink exists
# ════════════════════════════════════════════════════════════════════════

class TestTheRecordIsNotStale:
    """⚠ SYNTHESIS ROUND. The landing record published "(44)" tests and "21
    killed" after the review round had made them 64 and 33. A figure restated
    in prose goes stale silently, so derive it — and name which line to edit."""

    def test_the_instrument_counts_are_not_stale(self):
        import subprocess
        spec = (REPO / "docs/IMPROVEMENT_QUEUE_SPEC.md").read_text(
            encoding="utf-8")
        sweep = json.loads(
            (REPO / "tools/_sweep_iq1_iq1_2.json").read_text(encoding="utf-8"))
        out = subprocess.run(
            [sys.executable, "-m", "pytest", str(pathlib.Path(__file__)),
             "--collect-only", "-q", "--no-header", "-p", "no:randomly"],
            capture_output=True, text=True, cwd=str(REPO))
        m = re.search(r"(\d+) tests collected", out.stdout)
        assert m, out.stdout[-500:]
        collected = int(m.group(1))
        assert f"(**{collected}** at close)" in spec, (
            f"IMPROVEMENT_QUEUE_SPEC §0.5 names a test count that is not "
            f"{collected} — update the 'Tests' line of the IQ1-2 record")
        assert f"(**{len(sweep)}** mutations)" in spec, (
            f"the record names a sweep size that is not {len(sweep)} — update "
            f"the same line")


class TestThePlayerCanLearnItExists:
    def test_the_help_text_names_the_verb(self):
        """⚠ REVIEW ROUND: `assert "substitutes" in src` matched a COMMENT and
        survived deleting the entire help entry. Scope it to the help STRING —
        the block between the `recruit` entry and the next section."""
        src = (REPO / "backend/commands/meta_executor.py").read_text(
            encoding="utf-8")
        assert "  substitutes -" in src, "the help entry is gone"
        block = src[src.index("  substitutes -"):]
        block = block[:block.index("\n\n")]
        assert "buy substitutes for Ney" in block

    def test_the_phrasings_the_help_teaches_actually_parse(self):
        """A help entry naming a sentence the parser refuses is worse than
        no entry. Both phrasings are pinned golden-corpus rows."""
        corpus = json.loads(
            (REPO / "tests/data/parser_golden_corpus.json").read_text(
                encoding="utf-8"))
        rows = corpus["entries"] if isinstance(corpus, dict) else corpus
        utterances = {r.get("utterance") for r in rows if isinstance(r, dict)}
        src = (REPO / "backend/commands/meta_executor.py").read_text(
            encoding="utf-8")
        # Derive the taught phrasings from the help block itself, so adding
        # a fourth one to the copy cannot escape the gate.
        block = src[src.index("  substitutes -"):]
        block = block[:block.index("\n\n")]
        taught = re.findall(r'"([^"]+)"', block)
        assert len(taught) >= 3, f"expected the help to quote commands: {taught}"
        for phrase in taught:
            assert phrase in utterances, (
                f"help teaches {phrase!r} but no golden-corpus row pins it")

    def test_it_names_the_gates_that_actually_refuse(self):
        """⚠ WRITTEN BECAUSE A MUTATION CAME BACK INERT, and because the help
        was measured wrong: it named the TREASURY as the limit while the
        board's own archive shows 6 of 13 scripted purchases refused on the
        own-soil gate and every success capped at 9,000 of 30,000 men asked."""
        src = (REPO / "backend/commands/meta_executor.py").read_text(
            encoding="utf-8")
        block = src[src.index("  substitutes -"):]
        block = block[:block.index("\n\n")]
        assert "ground WE hold" in block, "the own-soil gate is not named"
        assert "smaller draft" in block, "the field batch cap is not named"
        assert "morale" in block, "the morale dilution is not named"

    def test_it_says_what_makes_it_different(self):
        """The one fact that makes it a sink: it costs gold and no men."""
        src = (REPO / "backend/commands/meta_executor.py").read_text(
            encoding="utf-8")
        block = src[src.index("  substitutes -"):]
        block = block[:block.index("\n\n")] if "\n\n" in block else block[:1200]
        assert "NO men" in block or "no men" in block.lower()
        assert "TREASURY" in block or "treasury" in block.lower()
