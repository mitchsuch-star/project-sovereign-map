"""ES-7 SECOND PASS (§0.6.8, July 11, 2026) — the reward portfolio.

Estates + rentes as a genuine two-instrument decision:
- The RENTE (grant_pension / revoke_pension): treasury pension sized to the
  marshal's current gap; face counts fully toward satisfaction; the treasury
  pays ceil(RENTE_PREMIUM × face)/turn through the income phase. Instant,
  war-safe, revocable — premium-priced, static, titleless.
- The STEWARD interplay: estate provinces stabilize faster under a
  high-administration holder (+5/turn) and slower under a wasteful one
  (−2/turn) — land appreciates, a rente never does.
- Foresight (item 3): every territory-authoring surface warns when a clause
  would cede a province sustaining a PLAYER marshal's estate.
- Expectation legibility (item 4): dispatch expectation-rise lines +
  grace-countdown, the shortfall-open notification, and honest erosion
  advice (never "endow him" when nothing is endowable).
- Dead-zone fix (item 5): only LIVE rival claims block a grant; dead claims
  are stripped eagerly at grant time.

Europe-scoped like the rest of ES-7 (N1: the legacy fixture world has no
dotation economy). Spec record: docs/ECONOMY_REVISIT_SPEC.md §0.6.8.
"""

import re
from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic.dotation import (
    GRACE_TURNS,
    RENTE_AI_TREASURY_FLOOR,
    RENTE_AI_TREASURY_MULT,
    RENTE_PREMIUM,
    build_rente_offer,
    check_estate_eligibility,
    compute_rente_face,
    estate_cession_warning,
    get_estate_income,
    get_estate_steward_map,
    get_expectation,
    get_nation_rente_bill,
    get_rente_cost,
    get_satisfaction,
    strip_dead_estate_claims,
)
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)
GD_DIR = REPO / "godot-client" / "project-sovereign"


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


def _french_marshal(world):
    return next(m for m in world.marshals.values()
                if m.nation == "France" and m.strength > 0)


def _enemy_marshal(world):
    return next(m for m in world.marshals.values()
                if m.nation != "France" and m.strength > 0)


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


def _execute(world, command_dict):
    executor = CommandExecutor()
    return executor.execute({"command": command_dict}, {"world": world})


def _grant_pension(world, marshal_name, **extra):
    command = {"marshal": marshal_name, "action": "grant_pension",
               "type": "specific"}
    command.update(extra)
    return _execute(world, command)


def _revoke_pension(world, marshal_name, **extra):
    command = {"marshal": marshal_name, "action": "revoke_pension",
               "type": "specific"}
    command.update(extra)
    return _execute(world, command)


def _trust(m):
    return m.trust.value if hasattr(m.trust, "value") else m.trust


# ═══════════════════════════ CONSTANTS PINS ════════════════════════════════


class TestConstants:
    def test_blessed_starting_values(self):
        # In-band tunable; a change here is a tuning decision, not drift.
        assert RENTE_PREMIUM == pytest.approx(1.5)
        assert RENTE_AI_TREASURY_MULT == 10
        assert RENTE_AI_TREASURY_FLOOR == 400
        assert Marshal.STEWARD_FAST_ADMIN == 8
        assert Marshal.STEWARD_WASTEFUL_ADMIN == 3
        assert Marshal.STEWARD_FAST_BONUS == 5
        assert Marshal.STEWARD_WASTEFUL_MALUS == -2

    def test_rente_cost_is_ceil_premium(self):
        assert get_rente_cost(0) == 0
        assert get_rente_cost(-40) == 0
        assert get_rente_cost(80) == 120
        assert get_rente_cost(81) == 122  # ceil(121.5)
        assert get_rente_cost(1) == 2     # ceil(1.5)


# ═══════════════════════ SATISFACTION & OFFER MATH ═════════════════════════


class TestSatisfactionMath:
    def test_pension_counts_fully_toward_satisfaction(self, world):
        m = _french_marshal(world)
        m.battles_won = 3  # expectation 120
        m.pension = 50
        assert get_estate_income(m, world) == 0
        assert get_satisfaction(m, world) == 50

    def test_captured_marshal_pension_neither_counts_nor_pays(self, world):
        m = _french_marshal(world)
        m.pension = 80
        m.captured_by = "Austria"
        assert get_satisfaction(m, world) == 0
        assert get_nation_rente_bill(world, "France") == 0

    def test_nation_rente_bill_sums_premium_costs(self, world):
        marshals = [m for m in world.marshals.values()
                    if m.nation == "France" and m.strength > 0][:2]
        marshals[0].pension = 80   # cost 120
        marshals[1].pension = 41   # cost ceil(61.5) = 62
        assert get_nation_rente_bill(world, "France") == 182
        assert get_nation_rente_bill(world, "Austria") == 0

    def test_rente_bill_zero_on_legacy_world(self, legacy):
        m = next(m for m in legacy.marshals.values() if m.nation == "France")
        m.pension = 100
        assert get_nation_rente_bill(legacy, "France") == 0

    def test_offer_face_ignores_existing_pension(self, world):
        # Re-granting must close the WHOLE gap, not just the delta over the
        # current pension (the top-up verb).
        m = _french_marshal(world)
        m.battles_won = 3  # expectation 120
        m.pension = 40
        assert compute_rente_face(m, world) == 120
        offer = build_rente_offer(m, world)
        assert offer == {"face": 120, "cost": 180}


# ═══════════════════════════ THE GRANT ACTION ══════════════════════════════


class TestGrantPension:
    def test_grant_full_wiring(self, world):
        m = _french_marshal(world)
        m.battles_won = 2  # expectation 80
        gold_before = world.nation_gold["France"]
        admin_before = world.admin_actions_remaining
        trust_before = _trust(m)
        result = _grant_pension(world, m.name)
        assert result["success"] is True
        assert m.pension == 80
        # No fee at grant — the recurring premium is the whole cost.
        assert world.nation_gold["France"] == gold_before
        # 1 admin AP by the router (ADMIN_ACTIONS membership).
        assert world.admin_actions_remaining == admin_before - 1
        # Paying never buys trust (same rule as the estate).
        assert _trust(m) == trust_before
        # The message explains the instrument: face AND true cost.
        assert "80g/turn" in result["message"]
        assert "120g/turn" in result["message"]
        assert any(e["type"] == "rente_granted" for e in world.event_log)

    def test_regrant_resizes_to_close_the_gap(self, world):
        m = _french_marshal(world)
        m.battles_won = 2  # expectation 80
        assert _grant_pension(world, m.name)["success"] is True
        assert m.pension == 80
        m.battles_won = 4  # expectation 160 — he won again
        result = _grant_pension(world, m.name)
        assert result["success"] is True
        assert m.pension == 160  # replaced, not stacked

    def test_grant_refused_when_expectation_met(self, world):
        m = _french_marshal(world)
        m.battles_won = 0
        result = _grant_pension(world, m.name)
        assert result["success"] is False
        assert "already met" in result["message"]
        assert m.pension == 0

    def test_grant_refused_for_captured_marshal(self, world):
        m = _french_marshal(world)
        m.battles_won = 2
        m.captured_by = "Austria"
        result = _grant_pension(world, m.name)
        assert result["success"] is False
        assert m.pension == 0

    def test_grant_refused_on_legacy_world(self, legacy):
        m = next(m for m in legacy.marshals.values() if m.nation == "France")
        m.battles_won = 5
        result = _grant_pension(legacy, m.name)
        assert result["success"] is False
        assert "not available" in result["message"]

    def test_grant_refused_for_foreign_marshal(self, world):
        enemy = _enemy_marshal(world)
        enemy.battles_won = 5
        result = _grant_pension(world, enemy.name,
                                _acting_nation="France")
        assert result["success"] is False
        assert enemy.pension == 0


class TestRevokePension:
    def test_revoke_full_wiring(self, world):
        m = _french_marshal(world)
        m.battles_won = 2
        assert _grant_pension(world, m.name)["success"] is True
        result = _revoke_pension(world, m.name)
        assert result["success"] is True
        assert m.pension == 0
        assert any(e["type"] == "rente_revoked" for e in world.event_log)

    def test_revoke_refused_without_pension(self, world):
        m = _french_marshal(world)
        result = _revoke_pension(world, m.name)
        assert result["success"] is False

    def test_revoke_copy_is_honest_when_estates_cover(self, world):
        # Review fix: revoking a rente made redundant by estate income must
        # not threaten erosion that cannot happen.
        m = _french_marshal(world)
        m.battles_won = 1  # expectation 40
        region = _conquer(world, stability=100, min_income=50)
        m.dotation_regions.append(region.name)  # estates cover ≥40 alone
        m.pension = 40
        result = _revoke_pension(world, m.name)
        assert result["success"] is True
        assert "redundant" in result["message"]
        assert "frays loyalty" not in result["message"]

    def test_revoke_copy_warns_when_shortfall_reopens(self, world):
        m = _french_marshal(world)
        m.battles_won = 2  # expectation 80, no estates
        m.pension = 80
        result = _revoke_pension(world, m.name)
        assert result["success"] is True
        assert "frays loyalty" in result["message"]

    def test_revoke_reopens_the_shortfall_machinery(self, world):
        m = _french_marshal(world)
        m.battles_won = 1  # expectation 40
        world.current_turn = 10
        m.pension = 40
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert m.expectation_grace_turn == -1  # met — no clock
        m.pension = 0  # revoked
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert m.expectation_grace_turn == world.current_turn  # grace opens
        trust_before = _trust(m)
        world.current_turn += GRACE_TURNS
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert _trust(m) == trust_before - 1  # erosion resumes


# ═══════════════════════ INCOME PHASE & LEDGER ═════════════════════════════


class TestRenteEconomySeam:
    def test_income_phase_charges_the_premium_bill(self, world):
        m = _french_marshal(world)
        m.pension = 80  # cost 120
        income_data = world.calculate_turn_income("France")
        assert income_data["rente_cost"] == 120
        assert income_data["breakdown"]["rente_cost"] == 120
        gold_before = world.nation_gold["France"]
        result = world.process_income_phase("France")
        assert result["rente_cost"] == 120
        assert "-120 rentes" in result["message"]
        expected_net = (result["income"] - result["occupation"]
                        - result["dotation_skim"] - 120
                        - result["upkeep"] + result["admin_bonus"]
                        # DEF-5 naval (conscious flip): boot France pays the
                        # Admiralty (90) on the 1805 world.
                        - result["admiralty"])
        assert result["net"] == expected_net
        assert world.nation_gold["France"] == gold_before + expected_net

    def test_no_pensions_means_zero_bill(self, world):
        income_data = world.calculate_turn_income("France")
        assert income_data["rente_cost"] == 0

    def test_treasury_report_names_the_pensioned_marshal(self, world):
        m = _french_marshal(world)
        m.pension = 80
        result = _execute(world, {"action": "economy", "type": "general",
                                  "marshal": None})
        assert result["success"] is True
        assert "Rentes: -120g" in result["message"]
        assert m.name in result["message"]


# ═══════════════════════════ THE AI RUNG (GR5) ═════════════════════════════


class TestAIRenteRung:
    def _rung(self, world, treasury, skip=None):
        from backend.ai.enemy_ai import EnemyAI
        ai = EnemyAI(CommandExecutor())
        return ai._find_dotation_grant("Austria", world, treasury,
                                       skip or set())

    def _needy_austrian(self, world):
        m = next(m for m in world.marshals.values()
                 if m.nation == "Austria" and m.strength > 0)
        m.battles_won = 3  # expectation 120 ≥ threshold 80
        return m

    def test_ai_prefers_land_when_eligible(self, world):
        m = self._needy_austrian(world)
        _conquer(world, nation="Austria", stability=80)
        grant = self._rung(world, treasury=5000)
        assert grant is not None
        assert grant["action"] == "grant_dotation"
        assert grant["marshal"] == m.name

    def test_ai_falls_back_to_rente_when_no_land(self, world):
        m = self._needy_austrian(world)
        # No conquered province for Austria at boot (starting soil is
        # homeland by construction) — the land arm is empty.
        grant = self._rung(world, treasury=5000)
        assert grant is not None
        assert grant["action"] == "grant_pension"
        assert grant["marshal"] == m.name

    def test_ai_rente_respects_the_treasury_guard(self, world):
        self._needy_austrian(world)
        # face 120 → cost 180 → guard max(400, 1800) = 1800
        assert self._rung(world, treasury=1799) is None
        assert self._rung(world, treasury=1800) is not None

    def test_ai_rente_respects_skip_actions(self, world):
        self._needy_austrian(world)
        assert self._rung(world, treasury=5000,
                          skip={"grant_pension"}) is None

    def test_ai_never_rewards_a_captured_marshal(self, world):
        m = self._needy_austrian(world)
        m.captured_by = "France"
        assert self._rung(world, treasury=5000) is None


# ═══════════════════════ THE STEWARD (item 2) ══════════════════════════════


class TestSteward:
    @pytest.mark.parametrize("admin,expected", [
        (10, 5), (9, 5), (8, 5),      # prosperous tier
        (7, 0), (5, 0), (4, 0),       # baseline, byte-identical
        (3, -2), (2, -2), (1, -2),    # the wasteful lord
    ])
    def test_tier_boundaries(self, world, admin, expected):
        m = _french_marshal(world)
        m.skills["administration"] = admin
        assert m.get_estate_stability_bonus() == expected

    def test_steward_map_only_own_controlled_estates(self, world):
        m = _french_marshal(world)
        m.skills["administration"] = 9
        region = _conquer(world, stability=60)
        m.dotation_regions.append(region.name)
        assert get_estate_steward_map(world) == {region.name: 5}
        # Occupied estate (controller flipped): never in the map.
        region.controller = "Austria"
        assert get_estate_steward_map(world) == {}

    def test_stability_growth_applies_the_delta(self, world):
        m = _french_marshal(world)
        m.skills["administration"] = 9
        region = _conquer(world, stability=60)
        m.dotation_regions.append(region.name)
        # Pick a region with no marshal standing in it (no garrison bonus).
        assert not world._has_marshal_in_region(region.name, "France")
        world.process_stability_growth()
        assert region.stability == 70  # base 5 + steward 5

    def test_wasteful_lord_slows_growth(self, world):
        m = _french_marshal(world)
        m.skills["administration"] = 2
        region = _conquer(world, stability=60)
        m.dotation_regions.append(region.name)
        assert not world._has_marshal_in_region(region.name, "France")
        world.process_stability_growth()
        assert region.stability == 63  # base 5 − 2

    def test_legacy_world_is_untouched(self, legacy):
        assert get_estate_steward_map(legacy) == {}


# ═══════════════════ DEAD-ZONE FIX (item 5) ════════════════════════════════


class TestDeadClaimEligibility:
    def _foreign_estate_flipped_to_france(self, world):
        """An Austrian marshal's estate whose province France now holds —
        the treaty-transfer dead zone."""
        enemy = _enemy_marshal(world)
        region = _conquer(world, nation=enemy.nation, stability=80)
        enemy.dotation_regions.append(region.name)
        region.controller = "France"  # treaty-style bare flip
        world.invalidate_active_nations_cache()
        return enemy, region

    def test_dead_claim_no_longer_blocks_eligibility(self, world):
        enemy, region = self._foreign_estate_flipped_to_france(world)
        ok, reason = check_estate_eligibility(world, "France", region.name)
        assert ok, reason

    def test_live_claim_still_blocks(self, world):
        # A French marshal's own estate stays blocked for a second grant.
        m = _french_marshal(world)
        region = _conquer(world, stability=80)
        m.dotation_regions.append(region.name)
        ok, reason = check_estate_eligibility(world, "France", region.name)
        assert not ok
        assert m.name in reason

    def test_grant_eagerly_strips_the_dead_claim(self, world):
        enemy, region = self._foreign_estate_flipped_to_france(world)
        m = _french_marshal(world)
        m.battles_won = 3
        world.nation_gold["France"] = 5000
        result = _execute(world, {
            "marshal": m.name, "action": "grant_dotation",
            "target": region.name, "type": "specific",
        })
        assert result["success"] is True, result["message"]
        assert region.name in m.dotation_regions
        assert region.name not in enemy.dotation_regions
        assert any(e["type"] == "estate_lost" and e["marshal"] == enemy.name
                   for e in world.event_log)

    def test_strip_helper_leaves_live_claims_alone(self, world):
        m = _french_marshal(world)
        region = _conquer(world, stability=80)
        m.dotation_regions.append(region.name)
        assert strip_dead_estate_claims(world, region.name) == []
        assert region.name in m.dotation_regions

    def test_pending_capture_choice_keeps_the_claim_live(self, world):
        # W6-8 pin: while confiscate/respect is unanswered the player may
        # yet choose RESPECT — the region is not endowable and the claim
        # must not be stripped.
        enemy, region = self._foreign_estate_flipped_to_france(world)
        world.pending_capture_choice = {
            "region": region.name,
            "capturer": "Ney",
            "previous_controller": enemy.nation,
        }
        ok, reason = check_estate_eligibility(world, "France", region.name)
        assert not ok
        assert enemy.name in reason
        assert strip_dead_estate_claims(world, region.name) == []
        assert region.name in enemy.dotation_regions


# ═══════════════ FORESIGHT WARNINGS (item 3) ═══════════════════════════════


class TestEstateCessionWarnings:
    def _french_estate(self, world):
        m = _french_marshal(world)
        region = _conquer(world, stability=80)
        m.dotation_regions.append(region.name)
        return m, region

    def test_warning_names_the_marshal(self, world):
        m, region = self._french_estate(world)
        text = estate_cession_warning(world, region.name)
        assert m.name in text
        assert region.name in text

    def test_no_warning_for_plain_provinces(self, world):
        region = _conquer(world, stability=80)
        assert estate_cession_warning(world, region.name) == ""

    def test_no_warning_for_enemy_estates(self, world):
        enemy = _enemy_marshal(world)
        region = _conquer(world, nation=enemy.nation)
        enemy.dotation_regions.append(region.name)
        assert estate_cession_warning(world, region.name) == ""

    def test_no_warning_when_player_does_not_control(self, world):
        # A stripped-but-still-listed estate (dead claim) is not a cession.
        m, region = self._french_estate(world)
        region.controller = "Austria"
        world.invalidate_active_nations_cache()
        assert estate_cession_warning(world, region.name) == ""

    def test_settlement_review_carries_the_warning_row(self, world):
        from backend.game_logic.settlement_presentation import (
            build_settlement_review,
        )
        m, region = self._french_estate(world)
        review = build_settlement_review(
            war_id="war-test",
            war_label="Test War",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            terms=[{"type": "territory_cede", "from": "France",
                    "to": "Austria", "region": region.name}],
            allies=[],
            warnings=[],
            acceptance=None,
            world=world,
        )
        warning_section = review["sections"]["warnings"]
        rows = list(warning_section["inline"]) + list(
            warning_section["overflow"])
        assert any(r.get("code") == "estate_cession" and m.name in
                   str(r.get("detail", "")) for r in rows), rows
        # The compact cap must keep the estate warning INLINE.
        assert any(r.get("code") == "estate_cession"
                   for r in warning_section["inline"])

    def test_review_warning_covers_the_plural_regions_shape(self, world):
        # Review hardening: territory clauses carry either `region` or
        # `regions: [...]` — the warning loop covers both.
        from backend.game_logic.settlement_presentation import (
            build_settlement_review,
        )
        m, region = self._french_estate(world)
        review = build_settlement_review(
            war_id="war-test",
            war_label="Test War",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            terms=[{"type": "territory_cede", "from": "France",
                    "to": "Austria", "regions": [region.name]}],
            allies=[],
            warnings=[],
            acceptance=None,
            world=world,
        )
        warning_section = review["sections"]["warnings"]
        rows = list(warning_section["inline"]) + list(
            warning_section["overflow"])
        assert any(r.get("code") == "estate_cession" for r in rows), rows

    def test_review_without_estates_has_no_warning_row(self, world):
        from backend.game_logic.settlement_presentation import (
            build_settlement_review,
        )
        region = _conquer(world, stability=80)
        review = build_settlement_review(
            war_id="war-test",
            war_label="Test War",
            proposer_side="attackers",
            accepting_side="defenders",
            covered_enemy_participants=["Austria"],
            terms=[{"type": "territory_cede", "from": "France",
                    "to": "Austria", "region": region.name}],
            allies=[],
            warnings=[],
            acceptance=None,
            world=world,
        )
        warning_section = review["sections"]["warnings"]
        rows = list(warning_section["inline"]) + list(
            warning_section["overflow"])
        assert not any(r.get("code") == "estate_cession" for r in rows)


# ═══════════ EXPECTATION LEGIBILITY (item 4) ═══════════════════════════════


class TestExpectationLegibility:
    def test_dispatch_announces_expectation_rises(self, world):
        from backend.game_logic.dispatch import _build_situation
        m = _french_marshal(world)
        m.battles_won = 2  # expectation 80, nothing held
        situation = _build_situation(world, "France")
        rises = situation["expectation_rises"]
        assert any(r["marshal"] == m.name and r["expectation"] == 80
                   for r in rises)
        assert m.last_expectation_seen == 80
        # Reconciled: the next dispatch stays quiet until he wins again.
        situation2 = _build_situation(world, "France")
        assert not any(r["marshal"] == m.name
                       for r in situation2["expectation_rises"])

    def test_dispatch_grace_countdown_and_pension_ride_unmet(self, world):
        from backend.game_logic.dispatch import _build_situation
        m = _french_marshal(world)
        m.battles_won = 3  # expectation 120
        m.pension = 40     # satisfaction 40 — short 80
        world.current_turn = 10
        m.expectation_grace_turn = 9  # one turn into grace
        situation = _build_situation(world, "France")
        row = next(u for u in situation["unmet_marshals"]
                   if u["marshal"] == m.name)
        assert row["pension"] == 40
        assert row["grace_turns_left"] == GRACE_TURNS - 1
        assert situation["rente_cost"] == get_rente_cost(40)

    def test_shortfall_open_fires_the_expectation_notification(self, world):
        m = _french_marshal(world)
        m.battles_won = 2
        world.current_turn = 10
        world._dotation_processed_turn = None
        world._process_dotation_state()
        pending = world.notifications.get_pending()
        mine = [n for n in pending if n["type"] == "dotation_expectation"
                and n["details"].get("marshal") == m.name]
        assert len(mine) == 1
        assert "rente" in mine[0]["message"]

    def test_erosion_advice_is_honest_when_nothing_is_endowable(self, world):
        m = _french_marshal(world)
        m.battles_won = 2
        world.current_turn = 10
        m.expectation_grace_turn = world.current_turn - GRACE_TURNS
        world._dotation_processed_turn = None
        world._process_dotation_state()
        pending = world.notifications.get_pending()
        erosion = [n for n in pending if n["type"] == "dotation_erosion"
                   and n["details"].get("marshal") == m.name]
        assert len(erosion) == 1
        # France holds no conquered province at boot — the advice must not
        # tell the player to endow.
        assert "no conquered province remains" in erosion[0]["message"]
        assert "rente" in erosion[0]["message"]

    def test_erosion_advice_offers_both_remedies_when_land_exists(self, world):
        m = _french_marshal(world)
        m.battles_won = 2
        _conquer(world, stability=80)
        world.current_turn = 10
        m.expectation_grace_turn = world.current_turn - GRACE_TURNS
        world._dotation_processed_turn = None
        world._process_dotation_state()
        pending = world.notifications.get_pending()
        erosion = [n for n in pending if n["type"] == "dotation_erosion"
                   and n["details"].get("marshal") == m.name]
        assert len(erosion) == 1
        assert "estate or grant him a rente" in erosion[0]["message"]


# ═══════════════ BATTLE-REPORT NOTE (item 4c, audit fix) ═══════════════════


class TestBattleReportExpectationNote:
    def _decisive_win(self, world):
        ney = world.marshals["Ney"]
        mack = world.marshals["Mack"]
        mack.location = ney.location
        mack.strength = 900  # dies whatever the rolls — the win is certain
        mack.fortified = False
        result = _execute(world, {"marshal": "Ney", "action": "attack",
                                  "target": "Mack", "type": "specific",
                                  "_muster_confirmed": True})
        return ney, result

    def test_note_fires_on_any_battles_won_increment(self, world):
        # Audit fix (July 11): the increment seams differ by path —
        # combat.py bumps only on decisive outcomes, the coordination
        # caller bumps on tactical wins, and the destruction sweep can
        # kill after a tactical outcome. The note reads the battles_won
        # DELTA, so it fires in every one of those cases.
        ney, result = self._decisive_win(world)
        assert result["success"] is True
        assert ney.battles_won >= 1
        note = (result.get("battle_report") or {}).get("expectation_note", "")
        assert "expectation of reward" in note, result.get("battle_report")

    def test_no_note_at_the_expectation_cap(self, world):
        world.marshals["Ney"].battles_won = 8  # already at the 300 cap
        ney, result = self._decisive_win(world)
        assert ney.battles_won >= 9
        br = result.get("battle_report") or {}
        assert "expectation_note" not in br


# ═══════════ ESP-EV-3: UNIFIED WIN SEMANTICS (solo = coordination) ═════════


class TestUnifiedWinSemantics:
    """ESP-EV-3 (July 11, 2026): solo tactical victories count toward
    battles_won/battles_lost — unified with the coordination caller's
    long-standing semantics (combat_executor atk_won/def_won include
    tactical outcomes). A marshal's record — and his ES-7 reward
    expectation — no longer depends on whether allies happened to march."""

    def _battle(self, seed, atk_strength, def_strength):
        import random
        from tests.conftest import MarshalFactory, WorldFactory
        random.seed(seed)
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=atk_strength,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=def_strength)
        w = WorldFactory.with_marshals([ney, mack])
        key = "|".join(sorted(["France", "Austria"]))
        w.diplomatic_states[key] = "WAR"
        w.war_start_turns[key] = w.current_turn
        result = _execute(w, {"marshal": "Ney", "action": "attack",
                              "target": "Mack", "type": "specific",
                              "_muster_confirmed": True})
        ev = (result.get("events") or [{}])[0]
        return ev.get("outcome"), ney, mack

    def test_attacker_tactical_and_stalemate_bookkeeping(self):
        observed = set()
        for seed in range(40):
            outcome, ney, mack = self._battle(seed, 40000, 26000)
            observed.add(outcome)
            if outcome == "attacker_tactical_victory":
                assert ney.battles_won == 1 and mack.battles_lost == 1
                assert ney.battles_lost == 0 and mack.battles_won == 0
            elif outcome == "stalemate":
                assert ney.battles_won == 0 and mack.battles_won == 0
                assert ney.battles_lost == 0 and mack.battles_lost == 0
        assert "attacker_tactical_victory" in observed, observed

    def test_defender_tactical_bookkeeping(self):
        observed = set()
        for seed in range(60):
            outcome, ney, mack = self._battle(seed, 14000, 42000)
            observed.add(outcome)
            if outcome == "defender_tactical_victory":
                assert mack.battles_won == 1 and ney.battles_lost == 1
                assert mack.battles_lost == 0 and ney.battles_won == 0
        assert "defender_tactical_victory" in observed, observed


# ═══════════ ESP-EV-4: THE GUESSED-TARGET GUARD (attack path) ══════════════


class TestGuessedTargetGuard:
    """ESP-EV-4 (July 11, 2026): a lethal order never fires at a
    live-LLM-substituted target the player's own words never mentioned
    ('attack Venetia' → Archduke John at Tyrol, observed live). The
    BUG-CA-3 / W6-1 rule, applied to the attack path."""

    def test_substituted_target_is_refused(self, world):
        john = world.marshals["ArchdukeJohn"]
        strength_before = john.strength
        result = _execute(world, {
            "marshal": "Massena", "action": "attack",
            "target": "ArchdukeJohn", "type": "specific",
            "_raw_input": "Massena, attack Venetia",
        })
        # PIN CONSCIOUSLY FLIPPED July 18, 2026. The guard used to end in a
        # flat terminal refusal that listed the visible enemies as prose and
        # offered nothing to click or type back — the playtest dead end
        # ("it just gives options" and nothing happens). It now raises the
        # answerable attack-target clarification instead. The load-bearing
        # invariants are unchanged and asserted below: no battle is fought,
        # and no interrupt is staged.
        assert result["state"] == "awaiting_clarification"
        assert result["clarification_kind"] == "attack_target"
        assert "will not charge at a guess" in result["message"]
        assert john.strength == strength_before  # nobody fought
        assert result.get("pending_interrupt") is None
        # Every option must reissue a fully-formed named attack, so answering
        # runs the ordinary pipeline rather than re-entering the refused guess.
        assert result["options"]
        for option in result["options"]:
            assert option["command"].startswith("Massena, attack ")
            assert option["target"] in world.marshals

    def test_guessed_target_refusal_is_answerable_by_typing(self, world):
        """The typed channel is the PRIMARY answer path in the terminal — the
        printed choices must resolve when typed back verbatim."""
        from backend.commands.clarification import interpret_clarification_answer

        result = _execute(world, {
            "marshal": "Massena", "action": "attack",
            "target": "ArchdukeJohn", "type": "specific",
            "_raw_input": "Massena, attack Venetia",
        })
        dialogue = {"options": result["options"]}
        answer = interpret_clarification_answer(dialogue, "ArchdukeJohn")
        assert answer.get("command") == "Massena, attack ArchdukeJohn"

    def test_target_named_by_location_passes_the_guard(self, world):
        # "the force at Tyrol" — the resolved enemy's LOCATION appears in
        # the raw text, so the parse is grounded, not a guess.
        result = _execute(world, {
            "marshal": "Massena", "action": "attack",
            "target": "ArchdukeJohn", "type": "specific",
            "_raw_input": "Massena, attack the force at Tyrol",
        })
        assert "will not charge at a guess" not in str(result.get("message", ""))

    def test_target_named_by_nation_passes_the_guard(self, world):
        result = _execute(world, {
            "marshal": "Massena", "action": "attack",
            "target": "ArchdukeJohn", "type": "specific",
            "_raw_input": "Massena, attack the Austrians",
        })
        assert "will not charge at a guess" not in str(result.get("message", ""))

    def test_no_raw_text_bypasses_the_guard(self, world):
        # AI, strategic execution, and muster re-issues carry no raw text —
        # the guard is a typed-player-order protection only.
        result = _execute(world, {
            "marshal": "Massena", "action": "attack",
            "target": "ArchdukeJohn", "type": "specific",
        })
        assert "will not charge at a guess" not in str(result.get("message", ""))

    # ── False-refusal regressions (July 12, 2026) — the guard must only
    #    fire on a SPECIFIC name the player typed that resolution overrode,
    #    never on a delegated / open / partially-named order. ──

    def test_delegated_open_target_passes_the_guard(self):
        # "attack the nearest enemy" — the player named nothing specific, so
        # the resolved target being absent from the raw text is NOT a guess.
        world = WorldState.from_dict(
            WorldState.from_scenario(str(SCENARIO_PATH)).to_dict())
        result = _execute(world, {
            "marshal": "Massena", "action": "attack",
            "target": "ArchdukeJohn", "type": "specific",
            "_raw_input": "Massena, attack the nearest enemy",
        })
        assert "will not charge at a guess" not in str(result.get("message", ""))

    def test_bare_attack_verb_passes_the_guard(self):
        # Bare "Ney, attack" — the engine auto-targets; a delegated target is
        # never a guess. (THE reported "Ney attack doesn't work" case.)
        world = WorldState.from_dict(
            WorldState.from_scenario(str(SCENARIO_PATH)).to_dict())
        result = _execute(world, {
            "marshal": "Ney", "action": "attack",
            "target": "", "type": "specific",
            "_raw_input": "Ney, attack",
        })
        assert "will not charge at a guess" not in str(result.get("message", ""))

    def test_partial_name_grounds_the_target(self):
        # "attack John" grounds "Archduke John" by word overlap — not a guess.
        world = WorldState.from_dict(
            WorldState.from_scenario(str(SCENARIO_PATH)).to_dict())
        result = _execute(world, {
            "marshal": "Massena", "action": "attack",
            "target": "ArchdukeJohn", "type": "specific",
            "_raw_input": "Massena, attack John",
        })
        assert "will not charge at a guess" not in str(result.get("message", ""))

    def test_a_SHARED_title_does_not_ground_the_target(self):
        """CONSCIOUS FLIP, August 16, 2026 — NPC-3.

        This used to assert that "the Archduke" GROUNDS a resolution to
        ArchdukeJohn. It must not, and that acceptance was the hole the P1
        went through: the shipped roster has TWO Archdukes, so "Archduke"
        identifies a rank and not a man, and treating it as grounding let
        `Ney, attack Archduke John` be resolved to Archduke CHARLES and
        waved through — the muster named Charles, the battle was fought
        against Charles, and the word "John" never appeared.

        The rule is the one `llm_client.unique_name_tokens` already states
        for the parser, now applied to the guard meant to catch the parser:
        a token owned by two candidates grounds neither. The sibling test
        above, which types the UNIQUE surname "John", still grounds and
        still passes — that is what keeps this from being a blanket
        tightening.
        """
        world = WorldState.from_dict(
            WorldState.from_scenario(str(SCENARIO_PATH)).to_dict())
        assert sum(1 for m in world.marshals
                   if m.startswith("Archduke")) >= 2, (
            "precondition: the title really is shared")
        result = _execute(world, {
            "marshal": "Massena", "action": "attack",
            "target": "ArchdukeJohn", "type": "specific",
            "_raw_input": "Massena, attack the Archduke",
        })
        assert "will not charge at a guess" in str(result.get("message", "")), (
            "an ambiguous title must be asked about, not guessed at")


# ═══════════════════ CARD PAYLOAD (Reward dialog data) ═════════════════════


class TestRewardCardPayload:
    def test_card_exposes_the_portfolio(self, world):
        from backend.game_logic.marshal_overview import _build_estates
        m = _french_marshal(world)
        m.battles_won = 3  # expectation 120
        m.skills["administration"] = 9
        region = _conquer(world, stability=80, min_income=50)
        card = _build_estates(m, world)
        assert card["expectation"] == 120
        assert card["estate_income"] == 0      # estates only, no pension blend
        assert card["rente_offer"]["face"] == 120
        assert card["rente_offer"]["cost"] == 180
        assert card["investiture_fee"] == 200
        assert card["steward_tier"] == "prosperous"
        details = card["eligible_estate_details"]
        assert details and all(
            set(d) >= {"region", "income"} for d in details)
        assert any(d["region"] == region.name for d in details)

    def test_card_estate_income_excludes_pension(self, world):
        from backend.game_logic.marshal_overview import _build_estates
        m = _french_marshal(world)
        m.battles_won = 3
        m.pension = 50
        card = _build_estates(m, world)
        assert card["estate_income"] == 0
        assert card["pension"] == 50
        assert card["pension_cost"] == 75
        assert card["expectation_shortfall"] == 70  # 120 − 50

    def test_legacy_card_is_inert(self, legacy):
        from backend.game_logic.marshal_overview import _build_estates
        m = next(m for m in legacy.marshals.values() if m.nation == "France")
        card = _build_estates(m, legacy)
        assert card["pension"] == 0
        assert card["rente_offer"] == {"face": 0, "cost": 0,
                                       "would_change": False}
        assert card["steward_note"] == ""

    def test_dotation_world_flag_distinguishes_worlds(self, world, legacy):
        # The card carries is_dotation_world so the client can show the
        # "reward exists — win battles to unlock it" explainer on Europe
        # (where the reward portfolio is real) but stay silent on the legacy
        # fixture world (no dotation economy). Fix for "where are the buttons?"
        from backend.game_logic.marshal_overview import _build_estates
        europe_card = _build_estates(_french_marshal(world), world)
        legacy_m = next(m for m in legacy.marshals.values()
                        if m.nation == "France")
        legacy_card = _build_estates(legacy_m, legacy)
        assert europe_card["is_dotation_world"] is True
        assert legacy_card["is_dotation_world"] is False

    def test_captured_card_offers_no_reward_options(self, world):
        # Review fix: the executors refuse a prisoner, so the card must
        # not dangle a rente offer or estate options he cannot receive.
        from backend.game_logic.marshal_overview import _build_estates
        m = _french_marshal(world)
        m.battles_won = 5
        m.pension = 40
        m.captured_by = "Austria"
        _conquer(world, stability=80)
        card = _build_estates(m, world)
        assert card["rente_offer"] == {"face": 0, "cost": 0,
                                       "would_change": False}
        assert card["eligible_estate_details"] == []
        assert card["eligible_estates"] == []
        assert card["pension"] == 0  # suspended while captured

    def test_card_has_no_float_premium_key(self, world):
        # GR2 (review fix): no float rides the Godot-bound payload; the
        # dialog derives the premium from the int face/cost pair.
        from backend.game_logic.marshal_overview import _build_estates
        m = _french_marshal(world)
        card = _build_estates(m, world)
        assert "rente_premium" not in card
        for key, value in card.items():
            if isinstance(value, float):
                raise AssertionError(f"float in card payload: {key}={value}")


# ═══════════════════════════ SERIALIZATION ═════════════════════════════════


class TestSerialization:
    def test_pension_fields_roundtrip(self, world):
        m = _french_marshal(world)
        m.pension = 123
        m.last_expectation_seen = 240
        clone = WorldState.from_dict(world.to_dict())
        m2 = clone.marshals[m.name]
        assert m2.pension == 123
        assert m2.last_expectation_seen == 240

    def test_old_saves_default_to_zero(self, world):
        m = _french_marshal(world)
        data = m.to_dict()
        data.pop("pension", None)
        data.pop("last_expectation_seen", None)
        m2 = Marshal.from_dict(data)
        assert m2.pension == 0
        assert m2.last_expectation_seen == 0


# ═══════════════════ GODOT RENDER GUARDS (house convention) ════════════════


class TestGodotSurfaces:
    def test_reward_dialog_scene_and_script_exist(self):
        assert (GD_DIR / "scenes" / "reward_dialog.tscn").is_file()
        assert (GD_DIR / "scripts" / "reward_dialog.gd").is_file()

    def test_reward_dialog_registered_in_main(self):
        src = (GD_DIR / "scripts" / "main.gd").read_text(encoding="utf-8")
        assert 'dialog_manager.register("reward_dialog"' in src
        assert "_on_reward_command" in src
        assert '"expectation_note"' in src

    def test_marshal_card_has_the_reward_link(self):
        src = (GD_DIR / "scripts" / "marshal_management.gd").read_text(
            encoding="utf-8")
        assert "meta_clicked" in src
        assert "url=reward:" in src
        assert "reward_requested" in src
        assert "refresh_if_open" in src

    def test_ledger_renders_the_rentes_line(self):
        src = (GD_DIR / "scripts" / "strategic_ledger.gd").read_text(
            encoding="utf-8")
        assert '"rente_cost"' in src
        assert "Rentes: -" in src

    def test_dispatch_renders_rises_and_grace(self):
        src = (GD_DIR / "scripts" / "dispatch_view.gd").read_text(
            encoding="utf-8")
        assert '"expectation_rises"' in src
        assert '"grace_turns_left"' in src

    def test_turn_banner_renders_the_rente_component(self):
        src = (GD_DIR / "scripts" / "main.gd").read_text(encoding="utf-8")
        assert 'event.get("rente_cost", 0)' in src

    def test_reward_dialog_explains_both_instruments(self):
        src = (GD_DIR / "scripts" / "reward_dialog.gd").read_text(
            encoding="utf-8")
        # §0.6.8 item 6: every option explains its instrument. The premium
        # prose is DERIVED from the backend face/cost pair (review fix —
        # a hardcoded "half again" would lie after an in-band retune).
        assert "ESTATE" in src and "RENTE" in src
        assert "above its face" in src
        assert "HALF AGAIN" not in src

    def test_reward_link_hidden_for_prisoners(self):
        src = (GD_DIR / "scripts" / "marshal_management.gd").read_text(
            encoding="utf-8")
        assert 'not m.get("captured", false)' in src


# ═══════════════ JEALOUSY-GRAPH GUARD (grep-assert, house rule) ═════════════


class TestJealousyGraphGuard:
    def test_dotation_module_never_touches_relationships(self):
        src = (REPO / "backend" / "game_logic" / "dotation.py").read_text(
            encoding="utf-8")
        assert not re.search(r"\bmodify_relationship\s*\(", src)
