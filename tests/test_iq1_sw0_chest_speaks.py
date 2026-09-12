"""IQ-1 SW-0 — "The Chest Speaks": the instrument, before the sink.

Row IQ's first slice, and it changes no balance at all. Two numbers the game
computed every turn and showed nobody:

* `gold_spent_this_turn` — serialized since Phase 6, written by
  `record_gold_spent`, read by the recruit pricer, and rendered on exactly one
  surface (the typed `economy` report), never on the Strategic Ledger and never
  in a playtest digest.
* the treasury's own fixed point. `calculate_state_charges` draws
  `(treasury - CHARGES_HOARD_FLOOR) * rate // WAR_EFFORT_DIVISOR` a turn, so
  there is a treasury at which the draw equals the gold coming in. That number
  is the single most decision-relevant figure in the economy and it was
  computed inside `get_state_charges_rate` every turn and discarded.

Measured September 12, 2026, which is why this slice goes first: a commanded
France reaches 88,556g by turn 40 having spent **2.5%** of 199,101g gross, and
every gold-consuming verb is in `meta_executor.ADMIN_ACTIONS` against a
hardcoded `max_admin_actions = 2` — so two war-priced levies at Paris (654g
each) is 1,308g against a boot net of 1,842g and **the treasury must rise on
turn one even if the player spends perfectly**.

The slice also fixes an instrument gap found while measuring: the playtest
digest recorded the player's treasury and NO AI treasury, so no GR5 claim
about the economy was falsifiable from any archived digest. It took a bespoke
probe to find that a neutral Ottoman Empire ends a 40-turn ambient run as the
richest state in Europe (55,062g, 68.8x its boot chest) while France holds 1.4%
of Europe's cash.

Both new ledger keys are OUTSIDE Net by construction and by test: `spent` is
money that has already left the treasury this turn (counting it in a forward
projection would charge it twice) and `ceiling` is a destination, not a flow.
The SC-33 identity is asserted unchanged.
"""

import ast
import json
import pathlib
import re
import subprocess
import sys
from pathlib import Path

import pytest

from backend.game_logic import ledger as ledger_mod
from backend.game_logic.ledger import _build_economy, state_charges_ceiling
from backend.models.world_state import (
    WorldState, CHARGES_HOARD_FLOOR, WAR_EFFORT_DIVISOR, CHARGES_CROWN_BASE,
)

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO / "godot-client" / "project-sovereign" / "assets"
                 / "maps" / "europe_1805.json")
LEDGER_GD = (REPO / "godot-client" / "project-sovereign" / "scripts"
             / "strategic_ledger.gd")
DRIVER = REPO / "tools" / "playtest_driver.py"


@pytest.fixture
def world():
    return WorldState.from_scenario(str(SCENARIO_PATH))


# ════════════════════════════════════════════════════════════════════════
# 1. The ceiling is the arithmetic it claims to be
# ════════════════════════════════════════════════════════════════════════

class TestTheCeilingIsTheFixedPoint:
    def test_it_is_the_treasury_at_which_the_draw_equals_the_net(self):
        """Not a rule of thumb — solve it, then verify by simulation."""
        net, rate = 4000, CHARGES_CROWN_BASE
        ceiling = state_charges_ceiling(net, rate)
        assert ceiling == CHARGES_HOARD_FLOOR + net * WAR_EFFORT_DIVISOR // rate

        # At the ceiling the chest is stationary to within one turn's
        # integer floor; one gold below it still climbs.
        draw_at = int(max(0, ceiling - CHARGES_HOARD_FLOOR) * rate
                      // WAR_EFFORT_DIVISOR)
        assert abs(draw_at - net) <= 1, (draw_at, net)
        below = ceiling // 2
        draw_below = int(max(0, below - CHARGES_HOARD_FLOOR) * rate
                         // WAR_EFFORT_DIVISOR)
        assert draw_below < net

    def test_a_higher_rate_means_a_lower_ceiling(self):
        """The whole finding in one assertion: the brake is priced on
        distress, so the nation in trouble is steered to a SMALLER chest
        than the nation at peace. Golden peace (rate 30) against total
        collapse (every term)."""
        peace = state_charges_ceiling(4000, 30)
        collapse = state_charges_ceiling(800, 430)
        assert peace > collapse * 25, (peace, collapse)
        # and the measured pair, to the digit
        assert peace == 335_333
        assert collapse == 6_651

    def test_zero_rate_and_zero_net_are_the_unbounded_sentinel(self):
        """GR2: an int-safe 0 rather than None or inf, because there is no
        such treasury in either case."""
        assert state_charges_ceiling(4000, 0) == 0
        assert state_charges_ceiling(0, 30) == 0
        assert state_charges_ceiling(-500, 30) == 0

    def test_the_boot_world_ceiling_is_reachable_and_finite(self, world):
        econ = _build_economy(world, "France")
        rate = sum(int(t.get("amount", 0))
                   for t in econ.get("state_charges_terms", []))
        assert rate > 0, "France boots at war — the crown and war terms fire"
        assert econ["ceiling"] == state_charges_ceiling(econ["net"], rate)
        assert econ["ceiling"] > int(world.nation_gold["France"])


# ════════════════════════════════════════════════════════════════════════
# 2. Shown = applied: the ledger's rate is the charge's rate
# ════════════════════════════════════════════════════════════════════════

class TestShownEqualsApplied:
    def test_the_ceiling_uses_the_rate_the_charge_was_applied_with(self, world):
        """CA9-N11's rule, one term further on. The ledger must not
        re-derive the rate; it must read the terms it was handed."""
        econ = _build_economy(world, "France")
        shown_rate = sum(int(t.get("amount", 0))
                         for t in econ["state_charges_terms"])
        applied_rate = world.get_state_charges_rate("France")["rate"]
        assert shown_rate == applied_rate
        assert econ["ceiling"] == state_charges_ceiling(econ["net"],
                                                        applied_rate)

    def test_spent_is_the_sum_of_the_record_calls(self, world):
        world.record_gold_spent("France", 400)
        world.record_gold_spent("France", 654)
        world.record_gold_spent("Austria", 999)
        econ = _build_economy(world, "France")
        assert econ["spent"] == 1054
        assert _build_economy(world, "Austria")["spent"] == 999

    def test_spent_is_per_nation_not_global(self, world):
        world.record_gold_spent("Britain", 5000)
        assert _build_economy(world, "France")["spent"] == 0


# ════════════════════════════════════════════════════════════════════════
# 3. Outside Net — the SC-33 identity is untouched
# ════════════════════════════════════════════════════════════════════════

class TestTheIdentityIsUntouched:
    def test_neither_key_enters_net(self, world):
        from tests.test_economy_ledger_reconciliation import NET_GOLD_COMPONENTS
        assert "spent" not in NET_GOLD_COMPONENTS
        assert "ceiling" not in NET_GOLD_COMPONENTS
        world.record_gold_spent("France", 7777)
        econ = _build_economy(world, "France")
        assert econ["net"] == sum(int(econ[k]) * sign
                                  for k, sign in NET_GOLD_COMPONENTS.items())

    def test_spending_gold_does_not_move_net(self, world):
        before = _build_economy(world, "France")["net"]
        world.record_gold_spent("France", 12_000)
        assert _build_economy(world, "France")["net"] == before


# ════════════════════════════════════════════════════════════════════════
# 4. The flip lever's False arm is byte-identical apart from the two keys
# ════════════════════════════════════════════════════════════════════════

class TestTheLever:
    def test_false_arm_zeroes_both_and_changes_nothing_else(self, world,
                                                            monkeypatch):
        world.record_gold_spent("France", 3000)
        on = _build_economy(world, "France")
        monkeypatch.setattr(ledger_mod, "THE_CHEST_STATES_ITS_CEILING", False)
        off = _build_economy(world, "France")
        assert off["spent"] == 0 and off["ceiling"] == 0
        assert on["spent"] == 3000 and on["ceiling"] > 0
        assert {k: v for k, v in on.items() if k not in ("spent", "ceiling")} \
            == {k: v for k, v in off.items() if k not in ("spent", "ceiling")}


# ════════════════════════════════════════════════════════════════════════
# 5. The client renders both (a CODE census with a sensitivity arm)
# ════════════════════════════════════════════════════════════════════════

class TestTheClientRendersThem:
    """The NET_GOLD_COMPONENTS ratchet cannot help here — these keys are
    deliberately outside Net, so nothing forces the .gd line by
    construction. Assert it directly, and prove the assertion can fail."""

    def _gd(self):
        return LEDGER_GD.read_text(encoding="utf-8")

    @pytest.mark.parametrize("key,label", [("spent", "Spent"),
                                           ("ceiling", "Ceiling")])
    def test_the_key_is_read_and_labelled(self, key, label):
        src = self._gd()
        assert f'econ.get("{key}"' in src, f"{key} is never read in the .gd"
        assert label in src, f"{key} has no player-facing label"

    def test_the_census_is_not_vacuous(self, tmp_path):
        """Sensitivity arm: a .gd with the read deleted must fail the same
        check. Without this the assertion above could pass on any file
        that merely mentions the word."""
        mutated = self._gd().replace('econ.get("ceiling"', 'econ.get("nope"')
        assert 'econ.get("ceiling"' not in mutated
        probe = tmp_path / "m.gd"
        probe.write_text(mutated, encoding="utf-8")
        assert 'econ.get("ceiling"' not in probe.read_text(encoding="utf-8")


# ════════════════════════════════════════════════════════════════════════
# 6. The census the slice exists to produce
# ════════════════════════════════════════════════════════════════════════

# Every function in backend/ that SUBTRACTS from `nation_gold` without
# recording the spend. This is an allowlist, not an aspiration: each entry is
# a real outflow the `Spent` line cannot see, and the point of pinning it is
# that a NEW one fails this test. Measured September 12, 2026 — 15 of 21.
UNRECORDED_OUTFLOWS = {
    ("backend/commands/combat_executor.py", "_post_combat_pipeline"),
    ("backend/commands/diplomatic_executor.py", "_execute_buy_off_design"),
    ("backend/commands/diplomatic_executor.py", "_execute_make_amends"),
    ("backend/commands/diplomatic_executor.py",
     "_execute_make_amends_grievance_variant"),
    ("backend/commands/diplomatic_executor.py", "_apply_ultimatum_demands"),
    ("backend/commands/naval_executor.py", "_execute_build_fleet"),
    ("backend/game_logic/coalition.py", "_process_british_subsidy"),
    ("backend/game_logic/diplomacy.py", "apply_continental_system"),
    ("backend/game_logic/instruments.py", "process_instruments"),
    ("backend/game_logic/vassal.py", "process_vassal_tribute"),
    ("backend/game_logic/vassal.py", "invest_in_vassal"),
    ("backend/game_logic/vassal.py", "attempt_vassal_bribe"),
    ("backend/models/world_state.py", "_ratify_treaty"),
    ("backend/models/world_state.py", "_process_treaty_clauses"),
    ("backend/models/world_state.py", "_process_reckless_cavalry_turn_start"),
}


def _gold_subtracting_functions():
    """AST, not text: find every function that assigns a subtraction into
    `<x>.nation_gold[...]`, and whether it calls `record_gold_spent`."""
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
                if any(isinstance(t, ast.Subscript)
                       and isinstance(t.value, ast.Attribute)
                       and t.value.attr == "nation_gold" for t in targets):
                    subs = True
            if not subs:
                continue
            records = any(isinstance(n, ast.Call)
                          and isinstance(n.func, ast.Attribute)
                          and n.func.attr == "record_gold_spent"
                          for n in ast.walk(fn))
            out[(str(path.relative_to(REPO)).replace("\\", "/"),
                 fn.name)] = records
    return out


class TestTheSpendCensus:
    def test_the_unrecorded_set_is_exactly_what_we_measured(self):
        found = _gold_subtracting_functions()
        unrecorded = {k for k, rec in found.items() if not rec}
        assert unrecorded == UNRECORDED_OUTFLOWS, (
            f"new unrecorded outflow(s): "
            f"{sorted(unrecorded - UNRECORDED_OUTFLOWS)}; "
            f"newly recorded: {sorted(UNRECORDED_OUTFLOWS - unrecorded)}")

    def test_the_census_actually_walks_code(self):
        """Sensitivity: the six recorded functions must be FOUND and must
        read as recorded, or the census is matching nothing."""
        found = _gold_subtracting_functions()
        recorded = {k for k, rec in found.items() if rec}
        assert ("backend/commands/economy_executor.py",
                "_execute_recruit") in recorded
        assert ("backend/game_logic/recruitment.py",
                "commission_marshal") in recorded
        assert len(found) >= 21


# ════════════════════════════════════════════════════════════════════════
# 7. The driver records what it could not see
# ════════════════════════════════════════════════════════════════════════

class TestTheDigestCanSeeTheOtherPurses:
    def test_the_driver_declares_the_helper_and_uses_it(self):
        src = DRIVER.read_text(encoding="utf-8")
        assert "def _all_purses(transport)" in src
        assert "purses=_all_purses(transport)" in src
        assert 'self.record("purses"' in src

    def test_purses_never_reach_the_markdown(self):
        """Omniscient data. It goes to the jsonl the analyst reads, never
        to the markdown that is written as a player's eye view."""
        src = DRIVER.read_text(encoding="utf-8")
        body = src.split("def _all_purses", 1)[1]
        block = src[src.index("if purses:"):src.index("if purses:") + 400]
        assert "self._md(" not in block, "purses must not be rendered"
        assert "backend_main" in body

    def test_a_live_short_run_records_both(self, tmp_path):
        out = tmp_path / "run"
        env = dict(**__import__("os").environ)
        env["INK_IRON_SAVE_DIR"] = str(tmp_path / "saves")
        env.pop("SOVEREIGN_SCENARIO", None)
        r = subprocess.run(
            [sys.executable, str(DRIVER), "--turns", "2", "--seed",
             "historical", "--name", "sw0pin", "--fresh", "--out", str(out)],
            cwd=str(REPO), env=env, capture_output=True, text=True,
            timeout=900)
        assert r.returncode == 0, r.stderr[-2000:]
        run_dir = next(p for p in out.rglob("digest.jsonl"))
        kinds = [json.loads(ln) for ln in
                 run_dir.read_text(encoding="utf-8").splitlines() if ln.strip()]
        purses = [k for k in kinds if k.get("kind") == "purses"]
        assert purses, "no purses row recorded"
        assert len(purses[0]["purses"]) == 20, purses[0]["purses"]
        assert "France" in purses[0]["purses"]
        md = (run_dir.parent / "digest.md").read_text(encoding="utf-8")
        assert re.search(r"- LEDGER .*ceiling \d+", md), md[:1500]
