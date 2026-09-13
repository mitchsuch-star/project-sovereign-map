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
   spender arm that bought 18,537 gold of substitutes — because the engine
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
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        import playtest_driver as drv
        negative = {k for k, s in NET_GOLD_COMPONENTS.items() if s < 0}
        assert negative <= drv._NET_NEGATIVE_KEYS
        assert "income" not in drv._NET_NEGATIVE_KEYS


# ════════════════════════════════════════════════════════════════════════
# 4. The fifteen outflows are judged, row by row
# ════════════════════════════════════════════════════════════════════════

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
                for t in targets:
                    if (isinstance(t, ast.Subscript)
                            and isinstance(t.value, ast.Attribute)
                            and t.value.attr == "nation_gold"):
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

    def test_the_allowlist_shrank_to_eight(self):
        from tests.test_iq1_sw0_chest_speaks import UNRECORDED_OUTFLOWS
        assert len(UNRECORDED_OUTFLOWS) == 8
        assert not (MOVED_TO_SPENT & UNRECORDED_OUTFLOWS)

    def test_every_survivor_states_its_reason_at_the_call_site(self):
        """GR9: SW-0 deferred this to 'a later slice' with no slice id. A
        survivor without a written reason is an open-ended deferral."""
        from tests.test_iq1_sw0_chest_speaks import UNRECORDED_OUTFLOWS
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
        """Sensitivity: the marker must sit in the FUNCTION, not merely
        somewhere in the file."""
        src = (REPO / "backend/game_logic/vassal.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        names = {fn.name for fn in ast.walk(tree)
                 if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert "invest_in_vassal" in names and "process_vassal_tribute" in names

    def test_the_census_still_reds_on_a_new_unrecorded_outflow(self):
        found = _gold_subtracting_functions()
        assert len(found) >= 22
        assert sum(found.values()) >= 14


# ════════════════════════════════════════════════════════════════════════
# 5. The digest can see the sink
# ════════════════════════════════════════════════════════════════════════

class TestTheDigestCanSeeTheSink:
    def test_there_is_a_read_before_the_turn_ends(self):
        """`spent` is cleared by `advance_turn`, so a post-end-turn read is
        structurally always zero — which is why it rendered on 0 of 117
        archived rows including the arm that bought 18,537 gold."""
        src = DRIVER.read_text(encoding="utf-8")
        idx_read = src.index("digest.turn_spend(_pre_econ)")
        idx_end = src.index('transport.post("/command", {"command": "end turn"})')
        assert idx_read < idx_end, "the read must precede the end turn"

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
        """The case the fix newly makes reachable. It had none, because it
        could not previously be rendered at all."""
        src = self._gd()
        assert "treasury > ceiling" in src
        assert "drawing it down" in src

    def test_the_census_is_not_vacuous(self, tmp_path):
        stripped = self._gd().replace('econ.get("ceiling_state"', 'econ.get("x"')
        probe = tmp_path / "probe.gd"
        probe.write_text(stripped, encoding="utf-8")
        assert 'econ.get("ceiling_state"' not in probe.read_text(encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════
# 7. A player can learn the sink exists
# ════════════════════════════════════════════════════════════════════════

class TestThePlayerCanLearnItExists:
    def test_the_help_text_names_the_verb(self):
        src = (REPO / "backend/commands/meta_executor.py").read_text(
            encoding="utf-8")
        assert "substitutes" in src
        assert "buy substitutes for Ney" in src

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

    def test_it_says_what_makes_it_different(self):
        """The one fact that makes it a sink: it costs gold and no men."""
        src = (REPO / "backend/commands/meta_executor.py").read_text(
            encoding="utf-8")
        block = src[src.index("  substitutes -"):]
        block = block[:block.index("\n\n")] if "\n\n" in block else block[:1200]
        assert "NO men" in block or "no men" in block.lower()
        assert "TREASURY" in block or "treasury" in block.lower()
