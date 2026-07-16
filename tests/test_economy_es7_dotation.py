"""ES-7 "The Cost of Success" — estate endowments / dotations (S7, Track 2).

Blessed shape (EC-2 gate record, spec §0.6.7 — July 9, 2026):
  - Amendment 1: FULL-income redirect — satisfaction = the estate's full
    effective income; the nation's ledger loses the same amount as a signed
    "Dotations" component; the 0.30 skim constant is DELETED.
  - Amendment 4: grant scope = player-held, non-capital, non-vassal,
    un-dotated, NON-HOMELAND (conquered) provinces only; estate provinces
    are EXEMPT from the ES-2 occupation cost (named test below pins the
    exemption as deliberate).
  - E5: REP_STEP 40 · EXPECTATION_CAP 300 · investiture fee 200g + 1 admin
    AP · EROSION_MAX -3/turn · SHORTFALL_PER_POINT 50 · grace-turn 2.

The falsifiable core of the reframe: NO payment ever raises trust on demand
(zero trust on grant — the no-bribe negative assertion) and erosion runs
through modify_trust ONLY, never modify_relationship (grep-assert guard).

Europe-scoped (N1): the legacy 19-region fixture world has no dotation
economy — zero legacy pins move.

The E1 stacked band test (Track-2 acceptance) lives in
test_economy_e1_band.py.
"""

import re
from pathlib import Path

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic.dispatch import _build_situation
from backend.game_logic.dotation import (
    AI_GRANT_SHORTFALL_THRESHOLD,
    EROSION_MAX,
    EXPECTATION_CAP,
    GRACE_TURNS,
    INVESTITURE_FEE,
    REP_STEP,
    SHORTFALL_PER_POINT,
    check_estate_eligibility,
    compute_investiture_fee,
    derive_title,
    get_expectation,
    get_satisfaction,
    get_shortfall,
    is_eroding,
    list_eligible_estates,
)
from backend.game_logic.ledger import _build_economy
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


@pytest.fixture
def legacy():
    return WorldState(player_nation="France")


def _conquer(world, nation="France", stability=80, min_income=0):
    """Flip one foreign non-capital, non-homeland region to `nation`."""
    homeland = set(world.nation_starting_regions.get(nation, []))
    armed = {m.nation for m in world.marshals.values() if m.strength > 0}
    for safe in (True, False):
        for region in world.regions.values():
            if not region.controller or region.controller == nation:
                continue
            if region.name in homeland or region.is_capital:
                continue
            if region.income_value < min_income:
                continue
            if safe and region.controller in armed:
                continue
            region.controller = nation
            region.stability = stability
            world.invalidate_active_nations_cache()
            return region
    raise AssertionError("no conquerable region found")


def _endow(world, marshal, stability=80, nation=None, min_income=0):
    """Conquer a province and endow it to `marshal` directly (state-level)."""
    region = _conquer(world, nation=nation or marshal.nation,
                      stability=stability, min_income=min_income)
    marshal.dotation_regions.append(region.name)
    return region


def _french_marshal(world):
    return next(m for m in world.marshals.values()
                if m.nation == "France" and m.strength > 0)


# ═══════════════════════ E5 blessed constants ═══════════════════════


class TestBlessedConstants:
    def test_e5_values(self):
        """§0.6.7 blessed starting values — a conscious re-pin is a band
        retune (no new gate); a SHAPE change is not."""
        assert REP_STEP == 40
        assert EXPECTATION_CAP == 300
        assert INVESTITURE_FEE == 200
        assert EROSION_MAX == 3
        assert SHORTFALL_PER_POINT == 50
        assert GRACE_TURNS == 2

    def test_no_skim_constant_exists(self):
        """Amendment 1: the 0.30 skim constant is DELETED — satisfaction is
        the estate's FULL effective income."""
        import backend.game_logic.dotation as dotation
        assert not any("SKIM" in name for name in dir(dotation))


# ═══════════════════════ expectation model ═══════════════════════


class TestExpectation:
    def test_expectation_is_rep_step_times_wins(self, world):
        m = _french_marshal(world)
        m.battles_won = 3
        assert get_expectation(m) == 3 * REP_STEP

    def test_expectation_caps(self, world):
        m = _french_marshal(world)
        m.battles_won = 100
        assert get_expectation(m) == EXPECTATION_CAP

    def test_satisfaction_is_full_effective_income(self, world):
        """Amendment 1: full-income redirect — one decent estate can meet a
        capped expectation (the 30%-skim arithmetic never could)."""
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        assert get_satisfaction(m, world) == region.get_effective_income()

    def test_satisfaction_drops_when_estate_lost(self, world):
        """State-driven: recomputed from currently-held regions — a cede,
        recapture, rebellion, or vassal grab needs no seam-specific hook."""
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        assert get_satisfaction(m, world) > 0
        region.controller = "Austria"
        world.invalidate_active_nations_cache()
        assert get_satisfaction(m, world) == 0


# ═══════════════════════ serialization ═══════════════════════


class TestSerialization:
    def test_fields_round_trip(self, world):
        m = _french_marshal(world)
        _endow(world, m)
        m.expectation_grace_turn = 7
        data = m.to_dict()
        loaded = Marshal.from_dict(data)
        assert loaded.dotation_regions == m.dotation_regions
        assert loaded.expectation_grace_turn == 7

    def test_save_compat_defaults(self, world):
        """Old saves (fields absent) load with no estates and grace -1 — the
        first shortfall turn merely STARTS the grace clock, so a loaded
        veteran takes no instant retroactive erosion."""
        m = _french_marshal(world)
        data = m.to_dict()
        del data["dotation_regions"]
        del data["expectation_grace_turn"]
        loaded = Marshal.from_dict(data)
        assert loaded.dotation_regions == []
        assert loaded.expectation_grace_turn == -1

    def test_world_round_trip_preserves_dotations(self, world):
        m = _french_marshal(world)
        region = _endow(world, m)
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.get_marshal(m.name).dotation_regions == [region.name]


# ═══════════════════════ grant action ═══════════════════════


class TestGrantAction:
    def _grant(self, world, marshal_name, target, **extra):
        executor = CommandExecutor()
        command = {"marshal": marshal_name, "action": "grant_dotation",
                   "target": target, "type": "specific"}
        command.update(extra)
        return executor.execute({"command": command}, {"world": world})

    def test_grant_success_full_wiring(self, world):
        m = _french_marshal(world)
        m.battles_won = 5
        region = _conquer(world, stability=80)
        gold_before = world.nation_gold["France"]
        admin_before = world.admin_actions_remaining
        result = self._grant(world, m.name, region.name)
        assert result["success"] is True
        assert region.name in m.dotation_regions
        # investiture fee deducted in-executor + 1 admin AP by the router
        assert world.nation_gold["France"] == gold_before - INVESTITURE_FEE
        assert world.admin_actions_remaining == admin_before - 1
        # province-derived title (flavor, GR6) rides the message
        assert derive_title(region.name) in result["message"]

    def test_no_trust_bump_on_grant(self, world):
        """THE no-bribe negative assertion (§0.6.2 non-goal): the endowment
        is a promise, not a purchase — zero trust on grant, ever."""
        m = _french_marshal(world)
        m.battles_won = 5
        region = _conquer(world, stability=80)
        trust_before = m.trust.value
        result = self._grant(world, m.name, region.name)
        assert result["success"] is True
        assert m.trust.value == trust_before

    def test_second_estate_no_fee(self, world):
        """Re-endow (adding land to an existing title) is 1 AP, no fee."""
        m = _french_marshal(world)
        first = _conquer(world, stability=80)
        assert self._grant(world, m.name, first.name)["success"]
        second = _conquer(world, stability=80)
        gold_before = world.nation_gold["France"]
        assert self._grant(world, m.name, second.name)["success"]
        assert world.nation_gold["France"] == gold_before  # no fee
        assert compute_investiture_fee(m) == 0

    def test_homeland_refused(self, world):
        """Amendment 4: the Domaine Extraordinaire never draws on the
        homeland — conquered provinces only."""
        m = _french_marshal(world)
        home = world.nation_starting_regions["France"][0]
        result = self._grant(world, m.name, home)
        assert result["success"] is False
        assert home not in m.dotation_regions

    def test_capital_refused(self, world):
        m = _french_marshal(world)
        capital = next(r for r in world.regions.values()
                       if r.controller == "France" and r.is_capital)
        assert self._grant(world, m.name, capital.name)["success"] is False

    def test_foreign_soil_refused(self, world):
        m = _french_marshal(world)
        foreign = next(r for r in world.regions.values()
                       if r.controller == "Austria")
        assert self._grant(world, m.name, foreign.name)["success"] is False

    def test_already_dotated_refused(self, world):
        """Un-dotated predicate: one estate funds one household."""
        marshals = [m for m in world.marshals.values()
                    if m.nation == "France" and m.strength > 0]
        region = _conquer(world, stability=80)
        assert self._grant(world, marshals[0].name, region.name)["success"]
        result = self._grant(world, marshals[1].name, region.name)
        assert result["success"] is False
        assert marshals[0].name in result["message"]

    def test_insufficient_gold_refused(self, world):
        m = _french_marshal(world)
        region = _conquer(world, stability=80)
        world.nation_gold["France"] = INVESTITURE_FEE - 1
        result = self._grant(world, m.name, region.name)
        assert result["success"] is False
        assert region.name not in m.dotation_regions

    def test_no_admin_ap_refused(self, world):
        m = _french_marshal(world)
        region = _conquer(world, stability=80)
        world.admin_actions_remaining = 0
        result = self._grant(world, m.name, region.name)
        assert result["success"] is False
        assert region.name not in m.dotation_regions

    def test_missing_target_lists_eligible(self, world):
        m = _french_marshal(world)
        region = _conquer(world, stability=80)
        result = self._grant(world, m.name, None)
        assert result["success"] is False
        assert region.name in result["message"]

    def test_legacy_world_refused(self, legacy):
        """ES-7 is Europe-scoped (N1) — the legacy fixture refuses."""
        m = next(m for m in legacy.marshals.values()
                 if m.nation == "France")
        result = self._grant(legacy, m.name, "Belgium")
        assert result["success"] is False
        assert m.dotation_regions == []

    def test_vassal_soil_structurally_ineligible(self, world):
        """Non-vassal predicate is structural: vassal soil has the vassal as
        controller, so it fails the controller check (tribute and dotation
        sets are disjoint by construction — no double-count)."""
        region = _conquer(world, stability=80)
        region.controller = "Bavaria"  # handed to a vassal nation
        world.invalidate_active_nations_cache()
        ok, reason = check_estate_eligibility(world, "France", region.name)
        assert ok is False


# ═══════════════ income redirect (amendment 1) ═══════════════


class TestIncomeRedirect:
    def test_full_income_redirected(self, world):
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        data = world.calculate_turn_income("France")
        assert data["dotation_skim"] == region.get_effective_income()

    def test_income_stays_gross(self, world):
        m = _french_marshal(world)
        before = world.calculate_turn_income("France")["income"]
        region = _endow(world, m, stability=100)
        data = world.calculate_turn_income("France")
        assert data["income"] == before + region.get_effective_income()

    def test_income_phase_subtracts_redirect(self, world):
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        gold_before = world.nation_gold["France"]
        result = world.process_income_phase("France")
        assert result["dotation_skim"] == region.get_effective_income()
        assert "dotations" in result["message"]
        assert world.nation_gold["France"] == gold_before + result["net"]
        assert result["net"] == (result["income"] - result["occupation"]
                                 - result["dotation_skim"] - result["upkeep"]
                                 + result["admin_bonus"])

    def test_estate_exempt_from_occupation_is_deliberate(self, world):
        """Amendment 4 named test: the endowed province pays NO ES-2
        occupation cost — his household administers it. The exemption is
        deliberate, not a tier accident (a hostile estate would otherwise
        pay the 50% tier)."""
        m = _french_marshal(world)
        region = _endow(world, m, stability=10)  # hostile tier
        data = world.calculate_turn_income("France")
        row = next(rd for rd in data["breakdown"]["region_details"]
                   if rd["region"] == region.name)
        assert row["occupation_cost"] == 0
        assert row["estate_of"] == m.name
        # ...and flipping the same region back to un-dotated re-applies it
        m.dotation_regions.remove(region.name)
        data = world.calculate_turn_income("France")
        row = next(rd for rd in data["breakdown"]["region_details"]
                   if rd["region"] == region.name)
        assert row["occupation_cost"] > 0

    def test_skim_stops_when_region_lost(self, world):
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        assert world.calculate_turn_income("France")["dotation_skim"] > 0
        region.controller = "Austria"
        world.invalidate_active_nations_cache()
        assert world.calculate_turn_income("France")["dotation_skim"] == 0

    def test_no_bankruptcy_mercy_needed(self, world):
        """E6: the redirect needs no mercy — it redirects income the nation
        is earning, so the estate's net contribution floors at 0 (the skim
        never exceeds what the estate itself brought in)."""
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        world.nation_bankruptcy_turns["France"] = 2
        data = world.calculate_turn_income("France")
        assert data["dotation_skim"] == region.get_effective_income()

    def test_ai_nation_pays_same_seam(self, world):
        """GR5: an AI court's endowment redirects through the identical
        process_income_phase seam — zero AI-only code."""
        mack = next(m for m in world.marshals.values()
                    if m.nation == "Austria" and m.strength > 0)
        region = _endow(world, mack, stability=100, nation="Austria")
        gold_before = world.nation_gold.get("Austria", 0)
        result = world.process_income_phase("Austria")
        assert result["dotation_skim"] == region.get_effective_income()
        assert world.nation_gold["Austria"] == gold_before + result["net"]


# ═══════════════ reconciliation: grace / erosion / prune ═══════════════


class TestReconciliation:
    def test_grace_two_full_turns_before_erosion(self, world):
        """Blessed grace-turn 2: a marshal must not begin souring two turns
        after a victory — erosion starts on the THIRD unmet turn."""
        m = _french_marshal(world)
        m.battles_won = 5  # expectation 200, shortfall 200 -> -3 capped
        trust_start = m.trust.value
        world.advance_turn()  # shortfall observed: grace clock starts
        assert m.trust.value == trust_start
        world.advance_turn()  # within grace
        assert m.trust.value == trust_start
        world.advance_turn()  # grace elapsed: erosion begins
        assert m.trust.value == trust_start - EROSION_MAX

    def test_erosion_magnitude_scales_and_caps(self, world):
        m = _french_marshal(world)
        m.battles_won = 1  # expectation 40 -> ceil(40/50) = 1 point
        world.current_turn = 10  # keep grace_turn clear of the -1 sentinel
        m.expectation_grace_turn = world.current_turn - GRACE_TURNS
        trust_start = m.trust.value
        world._process_dotation_state()
        assert m.trust.value == trust_start - 1

    def test_met_expectation_stops_the_bleed(self, world):
        """Paying stops the bleed (grace resets) — and never buys trust."""
        m = _french_marshal(world)
        m.battles_won = 2  # expectation 80
        world.current_turn = 10
        m.expectation_grace_turn = world.current_turn - GRACE_TURNS
        region = _endow(world, m, stability=100, min_income=100)
        assert region.get_effective_income() >= get_expectation(m)
        trust_start = m.trust.value
        world._process_dotation_state()
        assert m.trust.value == trust_start        # no erosion...
        assert m.expectation_grace_turn == -1      # ...clock reset
        # and NOT a trust bump either (the reframe's core)
        assert m.trust.value == trust_start

    def test_idempotent_within_a_turn(self, world):
        """§0.6.2 idempotency pin: reconciliation run twice in one turn
        yields one result — a duplicate call never double-erodes."""
        m = _french_marshal(world)
        m.battles_won = 5
        world.current_turn = 10
        m.expectation_grace_turn = world.current_turn - GRACE_TURNS
        world._process_dotation_state()
        trust_after_first = m.trust.value
        world._process_dotation_state()
        assert m.trust.value == trust_after_first

    def test_prune_on_region_loss_fires_notification(self, world):
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        region.controller = "Austria"
        world.invalidate_active_nations_cache()
        # force a fresh reconciliation this turn
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert region.name not in m.dotation_regions
        notes = [n for n in world.notifications.get_pending()
                 if n["type"] == "estate_lost"]
        assert notes and m.name in notes[-1]["message"]
        events = [e for e in world.event_log if e.get("type") == "estate_lost"]
        assert events and events[-1]["region"] == region.name

    def test_first_erosion_fires_notification_once(self, world):
        m = _french_marshal(world)
        m.battles_won = 5
        world.advance_turn()
        world.advance_turn()
        world.advance_turn()  # first eroding turn
        notes = [n for n in world.notifications.get_pending()
                 if n["type"] == "dotation_erosion"]
        assert len(notes) == 1
        world.advance_turn()  # keeps eroding, no second notification
        notes = [n for n in world.notifications.get_pending()
                 if n["type"] == "dotation_erosion"]
        assert len(notes) == 1

    def test_marshal_removal_frees_the_estate(self, world):
        """E5 prune path for marshal removal: dotations live on the marshal,
        so his estates die with him — the province is eligible again."""
        m = _french_marshal(world)
        region = _endow(world, m, stability=80)
        assert check_estate_eligibility(world, "France", region.name)[0] is False
        world.marshals.pop(m.name)
        assert check_estate_eligibility(world, "France", region.name)[0] is True
        assert world.calculate_turn_income("France")["dotation_skim"] == 0

    def test_ai_marshal_erodes_identically(self, world):
        """GR5: AI winners build expectation and erode through the same
        nation-agnostic reconciliation loop."""
        mack = next(m for m in world.marshals.values()
                    if m.nation == "Austria" and m.strength > 0)
        mack.battles_won = 5
        world.current_turn = 10
        mack.expectation_grace_turn = world.current_turn - GRACE_TURNS
        trust_start = mack.trust.value
        world._process_dotation_state()
        assert mack.trust.value == trust_start - EROSION_MAX

    def test_legacy_world_never_erodes(self, legacy):
        """N1: legacy-fixture marshals with wins never erode — zero legacy
        pins move."""
        m = next(m for m in legacy.marshals.values() if m.nation == "France")
        m.battles_won = 10
        trust_start = m.trust.value
        for _ in range(4):
            legacy.advance_turn()
        assert m.trust.value == trust_start

    def test_modify_relationship_exclusion_guard(self):
        """Grep-assert (§0.6.2 non-goal): the entire dotation subsystem
        touches modify_trust ONLY — never the Jealousy relationship graph."""
        sources = [
            (REPO / "backend" / "game_logic" / "dotation.py").read_text(
                encoding="utf-8"),
        ]
        ws_src = (REPO / "backend" / "models" / "world_state.py").read_text(
            encoding="utf-8")
        # isolate the reconciliation method body
        match = re.search(
            r"def _process_dotation_state.*?(?=\n    def )", ws_src, re.S)
        assert match, "_process_dotation_state not found"
        sources.append(match.group(0))
        econ_src = (REPO / "backend" / "commands" / "economy_executor.py"
                    ).read_text(encoding="utf-8")
        match = re.search(
            r"def _execute_grant_dotation.*?(?=\n    def )", econ_src, re.S)
        assert match, "_execute_grant_dotation not found"
        sources.append(match.group(0))
        # match CALLS, not prose — the docstrings themselves name the
        # exclusion rule
        for src in sources:
            assert not re.search(r"\bmodify_relationship\s*\(", src)


# ═══════════════════════ AI grant rung (GR5) ═══════════════════════


class TestAIGrant:
    def test_ai_picks_grant_for_shortfalling_marshal(self, world):
        mack = next(m for m in world.marshals.values()
                    if m.nation == "Austria" and m.strength > 0)
        mack.battles_won = 5  # shortfall 200 >= threshold 80
        region = _conquer(world, nation="Austria", stability=80)
        world.nation_gold["Austria"] = 1000
        ai = EnemyAI(CommandExecutor())
        action = ai._pick_admin_action("Austria", world, admin_ap=2)
        assert action == {"action": "grant_dotation", "marshal": mack.name,
                          "target": region.name}

    def test_ai_grant_executes_with_fee_in_executor(self, world):
        """The AI grant flows through the SAME executor; the fee reduces the
        AI treasury in-executor (never a negative admin bonus — that path
        would double-count against execute_admin_phase's direct payout)."""
        mack = next(m for m in world.marshals.values()
                    if m.nation == "Austria" and m.strength > 0)
        mack.battles_won = 5
        region = _conquer(world, nation="Austria", stability=80)
        world.nation_gold["Austria"] = 1000
        executor = CommandExecutor()
        result = executor.execute({"command": {
            "marshal": mack.name, "action": "grant_dotation",
            "target": region.name, "_acting_nation": "Austria",
            "type": "specific",
        }}, {"world": world})
        assert result["success"] is True
        assert region.name in mack.dotation_regions
        assert world.nation_gold["Austria"] == 1000 - INVESTITURE_FEE

    def test_ai_skips_when_no_shortfall(self, world):
        world.nation_gold["Austria"] = 1000
        _conquer(world, nation="Austria", stability=80)
        ai = EnemyAI(CommandExecutor())
        action = ai._pick_admin_action("Austria", world, admin_ap=2)
        assert action is None or action.get("action") != "grant_dotation"

    def test_ai_skips_when_treasury_below_fee(self, world):
        mack = next(m for m in world.marshals.values()
                    if m.nation == "Austria" and m.strength > 0)
        mack.battles_won = 5
        _conquer(world, nation="Austria", stability=80)
        world.nation_gold["Austria"] = INVESTITURE_FEE - 1
        ai = EnemyAI(CommandExecutor())
        action = ai._pick_admin_action("Austria", world, admin_ap=2)
        assert action is None or action.get("action") != "grant_dotation"

    def test_threshold_constant(self):
        assert AI_GRANT_SHORTFALL_THRESHOLD == 2 * REP_STEP


# ═══════════════ threading: ledger / dispatch / reports ═══════════════


class TestThreading:
    def test_ledger_carries_dotation_and_reconciles(self, world):
        m = _french_marshal(world)
        _endow(world, m, stability=100)
        econ = _build_economy(world, "France")
        assert econ["dotation_skim"] > 0
        signed_sum = (
            econ["income"] + econ["trade_income"] + econ["admin_bonus"]
            + econ["treaty_gold"] + econ["vassal_tribute"]
            + econ["settlement_gold"] - econ["occupation"]
            - econ["dotation_skim"] - econ["upkeep_base"]
            - econ["upkeep_surcharge"]
        )
        assert signed_sum == econ["net"]

    def test_ledger_gd_renders_dotations_line(self):
        src = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "strategic_ledger.gd").read_text(encoding="utf-8")
        assert '"dotation_skim"' in src
        assert "Dotations" in src

    def test_dispatch_situation_carries_redirect_and_rollup(self, world):
        m = _french_marshal(world)
        # Expectation 240 sits ABOVE the highest non-capital estate income
        # (major_city 200), so the marshal stays unmet no matter which region
        # _conquer picks — the July 16 map-registry renames shifted the first
        # safe pick from Algarve (city, 150) to Piedmont (major_city, 200),
        # where an expectation of exactly 200 was silently fully met.
        m.battles_won = 6  # expectation 240
        region = _endow(world, m, stability=100)
        situation = _build_situation(world, "France")
        assert situation["dotation_skim"] == region.get_effective_income()
        unmet = situation["unmet_marshals"]
        entry = next(u for u in unmet if u["marshal"] == m.name)
        assert entry["expectation"] == 240
        assert entry["satisfaction"] == region.get_effective_income()
        assert entry["shortfall"] == max(
            0, 240 - region.get_effective_income())
        # treasury_delta subtracts the redirect
        income_data = world.calculate_turn_income("France")
        upkeep_data = world.calculate_turn_upkeep("France")
        from backend.game_logic.diplomacy import calculate_trade_income
        trade = calculate_trade_income(world).get("France", 0)
        assert situation["treasury_delta"] == (
            income_data["income"] + trade - income_data["occupation"]
            - income_data["dotation_skim"] - upkeep_data["total"])

    def test_dispatch_gd_renders_unmet_marshals(self):
        src = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "dispatch_view.gd").read_text(encoding="utf-8")
        assert '"unmet_marshals"' in src

    def test_treasury_report_shows_dotation_lines(self, world):
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        result = CommandExecutor().execute(
            {"command": {"action": "economy"}}, {"world": world})
        assert result["success"] is True
        assert "Dotations:" in result["message"]
        assert f"estate of Marshal {m.name}" in result["message"]
        assert region.name in result["message"]

    def test_end_turn_message_annotates_dotations(self, world):
        m = _french_marshal(world)
        _endow(world, m, stability=100)
        result = CommandExecutor().execute(
            {"command": {"action": "end_turn"}}, {"world": world})
        assert "Dotations:" in result.get("message", "")

    def test_turn_end_event_carries_dotation_int(self, world):
        m = _french_marshal(world)
        region = _endow(world, m, stability=100)
        result = CommandExecutor().execute(
            {"command": {"action": "end_turn"}}, {"world": world})
        turn_end = next(e for e in result["events"]
                        if e.get("type") == "turn_end")
        assert isinstance(turn_end["dotation_skim"], int)
        assert region.controller == "France"
        assert turn_end["dotation_skim"] == (
            world.calculate_turn_income("France")["dotation_skim"])
        assert turn_end["dotation_skim"] > 0

    def test_main_gd_renders_dotation_banner(self):
        src = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "main.gd").read_text(encoding="utf-8")
        assert '"dotation_skim"' in src

    def test_marshal_overview_card_carries_estates(self, world):
        from backend.game_logic.marshal_overview import build_marshal_overview
        m = _french_marshal(world)
        m.battles_won = 5
        region = _endow(world, m, stability=100)
        cards = build_marshal_overview(world)
        card = next(c for c in cards if c["name"] == m.name)
        assert card["expectation"] == 200
        assert card["estate_income"] == region.get_effective_income()
        assert card["estate_regions"] == [region.name]
        assert card["estate_title"] == derive_title(region.name)
        if card["expectation_shortfall"] > 0:
            assert card["eligible_estates"] is not None

    def test_marshal_management_gd_renders_estate_lines(self):
        src = (REPO / "godot-client" / "project-sovereign" / "scripts"
               / "marshal_management.gd").read_text(encoding="utf-8")
        for key in ('"expectation"', '"estate_income"',
                    '"expectation_shortfall"', '"estate_title"',
                    '"eligible_estates"'):
            assert key in src

    def test_eroding_tag_on_objection_copy_seam(self):
        """§0.6.2 legibility surface: the objection message seam appends the
        'frayed by neglect' tag for an eroding marshal (cosmetic, GR6)."""
        src = (REPO / "backend" / "commands" / "executor.py").read_text(
            encoding="utf-8")
        assert "frayed by neglect" in src
        assert "is_eroding" in src


# ═══════════════════════ helpers / misc ═══════════════════════


class TestHelpers:
    def test_derive_title(self):
        assert derive_title("Swabia") == "Duke of Swabia"

    def test_list_eligible_sorted_richest_first(self, world):
        r1 = _conquer(world, stability=100)
        r2 = _conquer(world, stability=100)
        eligible = list_eligible_estates(world, "France")
        assert set(eligible) >= {r1.name, r2.name}
        incomes = [world.regions[r].get_effective_income() for r in eligible]
        assert incomes == sorted(incomes, reverse=True)

    def test_shortfall_and_eroding_helpers(self, world):
        m = _french_marshal(world)
        m.battles_won = 5
        assert get_shortfall(m, world) == 200
        assert is_eroding(m, world) is False
        world.current_turn = 10
        m.expectation_grace_turn = world.current_turn - GRACE_TURNS
        assert is_eroding(m, world) is True
