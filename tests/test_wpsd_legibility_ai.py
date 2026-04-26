"""WPS-D: War Score Legibility + AI + Surface Polish tests.

Spec: `docs/WAR_PURPOSE_SCORE_SEMANTICS_SPEC.md` §11-§14.
Plan: `docs/PEACE_DEALS_UMBRELLA_SPEC.md` §5.

Covers (~18 tests):
  1-3.  Settlement tier classification (boundaries, negative scores, midpoints)
  4-6.  Tier mismatch warnings (forced_alliance, territory, no warning)
  7-9.  Peace preview extension (war_objective, settlement_tier, tier_mismatch)
  10.   Dispatch includes settlement outlook
  11-12. AI ticking pressure modifier (positive pressure, clamped bounds)
  13-14. AI power cap pre-check (blocked, allowed)
  15-16. AI liberation peace evaluation (accepts liberation, refuses without)
  17.   AI liberation target priority in enemy AI
  18.   Dispatch forced alliance / liberation highlighting
"""
from __future__ import annotations

from backend.game_logic.diplomacy import (
    get_settlement_tier,
    get_tier_mismatch_warnings,
    build_war_context_snapshot,
    create_war_objective,
    set_diplomatic_state,
    SETTLEMENT_TIER_DISPLAY,
    TICKING_RATES,
)
from backend.game_logic.ai_diplomacy import (
    _calculate_ticking_pressure,
    ai_check_vassalage_power_cap,
    ai_should_accept_liberation_peace,
)
from backend.game_logic.dispatch import _build_war_objective_section
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _fresh_world() -> WorldState:
    return WorldState(player_nation="France")


def _war_world(opponent: str = "Prussia") -> WorldState:
    world = _fresh_world()
    set_diplomatic_state(world, "France", opponent, "WAR")
    dk = world._make_diplo_key("France", opponent)
    world.war_start_turns[dk] = 1
    return world


def _set_objective(world, nation, target, obj_type, diplo_key=None,
                   accumulated=0, target_regions=None):
    if diplo_key is None:
        diplo_key = world._make_diplo_key(nation, target)
    from backend.models.region import NATION_CAPITALS
    if target_regions is None:
        target_regions = [NATION_CAPITALS.get(target, target)]
    if diplo_key not in world.war_objectives:
        world.war_objectives[diplo_key] = {}
    world.war_objectives[diplo_key][nation] = create_war_objective(
        objective_type=obj_type,
        declaring_nation=nation,
        target_nation=target,
        target_regions=target_regions,
        current_turn=world.current_turn,
    )
    world.war_objectives[diplo_key][nation]["accumulated_ticking"] = accumulated


# ════════════════════════════════════════════════════════════════════════════
# 1-3. SETTLEMENT TIER CLASSIFICATION
# ════════════════════════════════════════════════════════════════════════════

class TestSettlementTiers:

    def test_tier_boundary_conditions(self):
        assert get_settlement_tier(0) == "white_peace"
        assert get_settlement_tier(19) == "white_peace"
        assert get_settlement_tier(20) == "favorable_terms"
        assert get_settlement_tier(39) == "favorable_terms"
        assert get_settlement_tier(40) == "dictated_terms"
        assert get_settlement_tier(59) == "dictated_terms"
        assert get_settlement_tier(60) == "harsh_peace"
        assert get_settlement_tier(79) == "harsh_peace"
        assert get_settlement_tier(80) == "total_victory"
        assert get_settlement_tier(100) == "total_victory"

    def test_negative_scores_mirror_positive(self):
        assert get_settlement_tier(-10) == "white_peace"
        assert get_settlement_tier(-25) == "favorable_terms"
        assert get_settlement_tier(-50) == "dictated_terms"
        assert get_settlement_tier(-65) == "harsh_peace"
        assert get_settlement_tier(-90) == "total_victory"

    def test_all_tiers_have_display_names(self):
        for score in [0, 25, 45, 65, 90]:
            tier = get_settlement_tier(score)
            assert tier in SETTLEMENT_TIER_DISPLAY
            assert SETTLEMENT_TIER_DISPLAY[tier]


# ════════════════════════════════════════════════════════════════════════════
# 4-6. TIER MISMATCH WARNINGS
# ════════════════════════════════════════════════════════════════════════════

class TestTierMismatchWarnings:

    def test_forced_alliance_warns_below_harsh_peace(self):
        terms = {"clauses": [{"clause_type": "forced_alliance"}], "demands": []}
        warnings = get_tier_mismatch_warnings(45, terms)
        assert len(warnings) == 1
        assert warnings[0]["warning_type"] == "tier_mismatch"
        assert warnings[0]["demanded_tier"] == "harsh_peace"
        assert warnings[0]["current_tier"] == "dictated_terms"

    def test_many_territory_demands_warn(self):
        terms = {
            "clauses": [],
            "demands": [
                {"type": "territory", "value": 1},
                {"type": "territory", "value": 1},
                {"type": "territory", "value": 1},
                {"type": "territory", "value": 1},
            ],
        }
        warnings = get_tier_mismatch_warnings(25, terms)
        assert any(w["demanded_tier"] == "harsh_peace" for w in warnings)

    def test_no_warning_when_tier_sufficient(self):
        terms = {"clauses": [{"clause_type": "forced_alliance"}], "demands": []}
        warnings = get_tier_mismatch_warnings(70, terms)
        assert len(warnings) == 0


# ════════════════════════════════════════════════════════════════════════════
# 7-9. PEACE PREVIEW EXTENSION
# ════════════════════════════════════════════════════════════════════════════

class TestPeacePreviewExtension:

    def test_snapshot_includes_settlement_tier(self):
        world = _war_world()
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace")
        assert "settlement_tier" in snapshot
        assert snapshot["settlement_tier"] in SETTLEMENT_TIER_DISPLAY
        assert "settlement_tier_display" in snapshot

    def test_snapshot_includes_war_objective_when_set(self):
        world = _war_world()
        dk = world._make_diplo_key("France", "Prussia")
        _set_objective(world, "France", "Prussia", "conquest",
                       accumulated=10)
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace")
        assert snapshot["war_objective"] is not None
        assert snapshot["war_objective"]["type"] == "conquest"
        assert snapshot["war_objective"]["accumulated_ticking"] == 10

    def test_snapshot_includes_tier_mismatch_warnings(self):
        world = _war_world()
        terms = {
            "type": "peace",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [{"clause_type": "forced_alliance",
                         "from_nation": "Prussia", "to_nation": "France"}],
        }
        snapshot = build_war_context_snapshot(
            world, "France", "Prussia", "peace", terms=terms)
        assert "tier_mismatch_warnings" in snapshot
        assert any(w["warning_type"] == "tier_mismatch"
                   for w in snapshot["tier_mismatch_warnings"])


# ════════════════════════════════════════════════════════════════════════════
# 10. DISPATCH INTEGRATION
# ════════════════════════════════════════════════════════════════════════════

class TestDispatchIntegration:

    def test_dispatch_war_objective_includes_settlement_tier(self):
        world = _war_world()
        _set_objective(world, "France", "Prussia", "conquest",
                       accumulated=5)
        lines = _build_war_objective_section(world, "France")
        assert len(lines) >= 1
        assert "Settlement:" in lines[0]["text"]


# ════════════════════════════════════════════════════════════════════════════
# 11-12. AI TICKING PRESSURE
# ════════════════════════════════════════════════════════════════════════════

class TestAITickingPressure:

    def test_opponent_ticking_increases_pressure(self):
        world = _war_world()
        dk = world._make_diplo_key("France", "Prussia")
        _set_objective(world, "France", "Prussia", "conquest",
                       accumulated=15)
        _set_objective(world, "Prussia", "France", "defense",
                       accumulated=0, diplo_key=dk, target_regions=["Berlin"])
        pressure = _calculate_ticking_pressure("Prussia", "France", dk, world)
        assert pressure > 0

    def test_ticking_pressure_clamped(self):
        world = _war_world()
        dk = world._make_diplo_key("France", "Prussia")
        _set_objective(world, "France", "Prussia", "conquest",
                       accumulated=25)
        _set_objective(world, "Prussia", "France", "defense",
                       accumulated=0, diplo_key=dk, target_regions=["Berlin"])
        pressure = _calculate_ticking_pressure("Prussia", "France", dk, world)
        assert pressure <= 10
        assert pressure >= -10


# ════════════════════════════════════════════════════════════════════════════
# 13-14. AI POWER CAP PRE-CHECK
# ════════════════════════════════════════════════════════════════════════════

class TestAIPowerCapPrecheck:

    def test_ai_vassalage_blocked_for_powerful_nation(self):
        world = _fresh_world()
        allowed = ai_check_vassalage_power_cap("France", "Austria", world)
        assert allowed is False

    def test_ai_vassalage_allowed_for_minor(self):
        world = _fresh_world()
        allowed = ai_check_vassalage_power_cap("France", "Saxony", world)
        assert allowed is True


# ════════════════════════════════════════════════════════════════════════════
# 15-16. AI LIBERATION PEACE EVALUATION
# ════════════════════════════════════════════════════════════════════════════

class TestAILiberationPeace:

    def test_ai_accepts_peace_with_liberation_clause(self):
        world = _war_world("Austria")
        dk = world._make_diplo_key("Austria", "France")
        world.war_objectives[dk] = {}
        world.war_objectives[dk]["Austria"] = create_war_objective(
            objective_type="liberation",
            declaring_nation="Austria",
            target_nation="France",
            target_regions=["Dresden"],
            current_turn=1,
            vassal_nations=["Saxony"],
        )
        terms = {
            "clauses": [{"clause_type": "liberation", "vassal_nation": "Saxony"}],
        }
        assert ai_should_accept_liberation_peace("Austria", "France", terms, world) is True

    def test_ai_refuses_peace_without_liberation_when_score_high(self):
        world = _war_world("Austria")
        dk = world._make_diplo_key("Austria", "France")
        world.war_objectives[dk] = {}
        world.war_objectives[dk]["Austria"] = create_war_objective(
            objective_type="liberation",
            declaring_nation="Austria",
            target_nation="France",
            target_regions=["Dresden"],
            current_turn=1,
            vassal_nations=["Saxony"],
        )
        # Give Austria a high war score (from Austria's perspective)
        world.war_scores[dk] = -50
        terms = {"clauses": []}
        assert ai_should_accept_liberation_peace("Austria", "France", terms, world) is False


# ════════════════════════════════════════════════════════════════════════════
# 17. AI LIBERATION TARGET PRIORITY
# ════════════════════════════════════════════════════════════════════════════

class TestAILiberationTargetPriority:

    def test_liberation_target_method_exists_and_returns_none_without_objective(self):
        from backend.ai.enemy_ai import EnemyAI
        from backend.models.marshal import Marshal
        world = _war_world("Austria")
        ai = EnemyAI(executor=None)
        ai._recapture_targets_claimed = set()
        ai._recapture_marshal_assignments = {}
        m = Marshal("Schwarzenberg", "Austria", "Vienna", 15000)
        result = ai._find_liberation_target(m, "Austria", world)
        assert result is None


# ════════════════════════════════════════════════════════════════════════════
# 18. DISPATCH FORCED ALLIANCE / LIBERATION HIGHLIGHTING
# ════════════════════════════════════════════════════════════════════════════

class TestDispatchForcedAllianceHighlighting:

    def test_dispatch_peace_settlement_includes_forced_alliance(self):
        world = _fresh_world()
        world.peace_ratification_log = [{
            "turn": int(world.current_turn) - 1,
            "new_state": "PEACE",
            "target_nation": "Prussia",
            "war_duration_turns": 5,
            "war_outcome": "french_victory",
            "territory_gained": [],
            "final_war_score": 70,
            "terms_ratified": [
                "Prussia enters forced alliance with France",
            ],
        }]
        from backend.game_logic.dispatch import _build_peace_settlement_section
        settlements = _build_peace_settlement_section(world)
        assert len(settlements) == 1
        assert "forced alliance" in settlements[0]["detail"].lower()
