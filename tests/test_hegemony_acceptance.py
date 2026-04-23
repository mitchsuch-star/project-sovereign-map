"""
B-B1-lite acceptance-formula decoupling tests
(RELIABILITY_COMMITMENTS_SPEC v2.4.3 §9.1 + §9.2 + §11.2).

Covers:
- `hegemony_target_mod` gate conditions + share curve + clamp
- `bilateral_betrayal_mod` strike ladder + composition with hard_reject
- `reliability_modifier` narrowing (// 10, cap +/-6)
- `components` dict surfaces both new terms independently
- `build_proposal_commitment_warnings` emits `hegemony` with band-aware text
- Same-turn treaty ratification → preview reads new share (not lagging
  `hegemony_signal_high_water`)
- `decision_reason` alias round-trip: `concern_pressure` -> "hegemony pressure"

Not covered here (anti-scope, owned by other slices):
- `grievance_modifier` + composite -60 floor -> B-B4
- `commitment_event_metadata` betrayal referents -> post-B-B1-lite
- Balance of Europe ledger payload / headline -> C-lite
"""

from __future__ import annotations

import pytest

from backend.display_names import (
    FEEDBACK_STRINGS,
    diplomatic_decision_reason_display,
)
from backend.game_logic import coalition as coalition_mod
from backend.game_logic.diplomacy import (
    WARNING_CATEGORY_ORDER,
    _sort_structured_warnings,
    bilateral_betrayal_mod,
    build_proposal_commitment_warnings,
    calculate_acceptance,
    hegemony_target_mod,
)
from backend.models.world_state import WorldState


# ════════════════════════════════════════════════════════════════
# HELPERS — share control via WorldState geometry + monkeypatch seam
# ════════════════════════════════════════════════════════════════

def _clean_world() -> WorldState:
    """Mirror of `_clean_diplo_world` from test_hegemony_engine.py. Built
    locally to keep this suite self-contained and immune to accidental
    cross-file refactors."""
    world = WorldState()
    world.diplomatic_states = {}
    world.vassals = {}
    world.hegemony_signal_high_water = 0
    world.hegemony_signal_hegemon = None
    world.hegemony_relaxation_bands_fired = set()
    world.positive_threat_delta_this_turn = False
    world._bloc_members_cache = {}
    world._bloc_members_cache_turn = -1
    world.notifications._pending = []
    world.invalidate_active_nations_cache()
    return world


def _stub_hegemon(monkeypatch, hegemon: str, share: float) -> None:
    """Force `_identify_max_bloc_share` to return `(hegemon, share)`. Used
    by curve tests that need precise shares not cleanly expressible via
    integer region/tier math (0.33 and 0.635 boundary points)."""
    monkeypatch.setattr(
        coalition_mod,
        "_identify_max_bloc_share",
        lambda world: (hegemon, share),
    )


def _set_regions(world: WorldState, nation: str, count: int) -> None:
    """Minimal region-count setter for geometric share tests. Only assigns
    from `__sink__`-controlled regions — never cannibalizes existing
    controllers. Call order matters: strip all regions to sink before the
    first assignment."""
    if nation != world.player_nation and nation not in world.enemy_nations:
        world.enemy_nations.append(nation)
    region_names = list(world.regions.keys())
    for name in region_names:
        if world.regions[name].controller == nation:
            world.regions[name].controller = "__sink__"
    assigned = 0
    for name in region_names:
        if assigned >= count:
            break
        if world.regions[name].controller == "__sink__":
            world.regions[name].controller = nation
            assigned += 1
    world.invalidate_active_nations_cache()


def _seed_betrayal_strikes(world: WorldState, actor: str, victim: str, count: int) -> None:
    """Write `count` active bilateral strikes directly into
    `betrayal_history`. Bypasses `_record_betrayal_strike` so we can pin
    exact counts without dual-strike-per-episode suppression."""
    current_turn = int(getattr(world, "current_turn", 0))
    key = f"{actor}|{victim}"
    world.betrayal_history = getattr(world, "betrayal_history", {}) or {}
    world.betrayal_history[key] = {
        "strikes": [
            {
                "severity": "medium",
                "turn": current_turn,
                "episode_id": f"fixture_{i}",
                "decays_on_turn": current_turn + 10,
            }
            for i in range(count)
        ],
        "categories": [],
        "last_turn": current_turn,
    }


def _minimal_proposal(proposer: str, target: str, ptype: str = "peace") -> dict:
    return {
        "type": ptype,
        "proposer_nation": proposer,
        "target_nation": target,
        "sweeteners": [],
        "demands": [],
        "clauses": [],
    }


# ════════════════════════════════════════════════════════════════
# 1. hegemony_target_mod — gates
# ════════════════════════════════════════════════════════════════

class TestHegemonyTargetModGates:
    def test_no_hegemon_returns_zero(self, monkeypatch):
        world = _clean_world()
        _stub_hegemon(monkeypatch, None, 0.0)
        assert hegemony_target_mod("France", "Austria", world) == 0

    def test_asker_outside_hegemon_bloc_returns_zero(self, monkeypatch):
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.55)
        # Austria is not in France's bloc by default (empty alliances).
        assert "Austria" not in world.get_bloc_members("France")
        assert hegemony_target_mod("Austria", "Prussia", world) == 0

    def test_target_inside_hegemon_bloc_returns_zero(self, monkeypatch):
        world = _clean_world()
        # Make Saxony an ally of France (Saxony joins France's bloc).
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "ALLIANCE"
        world.invalidate_bloc_members_cache()
        _stub_hegemon(monkeypatch, "France", 0.55)
        assert "Saxony" in world.get_bloc_members("France")
        # Intra-bloc proposal: France -> Saxony, both in bloc.
        assert hegemony_target_mod("France", "Saxony", world) == 0

    def test_asker_equals_target_returns_zero(self, monkeypatch):
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.55)
        assert hegemony_target_mod("France", "France", world) == 0


# ════════════════════════════════════════════════════════════════
# 2. hegemony_target_mod — share curve + clamp
# ════════════════════════════════════════════════════════════════

class TestHegemonyTargetModCurve:
    @pytest.mark.parametrize(
        "share, expected",
        [
            (0.30, 0),       # exact floor, integer truncation
            (0.33, -1),      # 0.03 * 60 = 1.8 -> -int = -1
            (0.50, -12),     # 0.20 * 60 = 12 -> -12
            (0.60, -18),     # 0.30 * 60 = 18 -> -18
            (0.635, -20),    # 0.335 * 60 = 20.1 -> clamp at -20
            (0.70, -20),     # 0.40 * 60 = 24 -> clamp at -20
            (0.95, -20),     # extreme share, clamp holds
        ],
    )
    def test_curve_honors_formula_and_clamp(self, monkeypatch, share, expected):
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", share)
        assert hegemony_target_mod("France", "Austria", world) == expected

    def test_below_thirty_percent_returns_zero(self, monkeypatch):
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.29)
        assert hegemony_target_mod("France", "Austria", world) == 0


# ════════════════════════════════════════════════════════════════
# 3. bilateral_betrayal_mod — strike ladder + composition
# ════════════════════════════════════════════════════════════════

class TestBilateralBetrayalMod:
    @pytest.mark.parametrize(
        "strike_count, expected",
        [(0, 0), (1, -6), (2, -12), (3, -18)],
    )
    def test_flat_six_per_active_strike(self, strike_count, expected):
        world = _clean_world()
        _seed_betrayal_strikes(world, "France", "Austria", strike_count)
        assert bilateral_betrayal_mod("France", "Austria", world) == expected

    def test_three_strike_composition_with_hard_reject(self):
        """3 active strikes: bilateral_betrayal_mod returns -18 AND the
        hard_reject_posture path fires on deep-treaty proposals. Both
        surface in components — neither is dead weight."""
        world = _clean_world()
        _seed_betrayal_strikes(world, "France", "Austria", 3)
        # Shallow (peace) proposal: hard_reject doesn't fire on non-deep.
        proposal = _minimal_proposal("France", "Austria", ptype="peace")
        result = calculate_acceptance(proposal, world)
        assert result["components"]["bilateral_betrayal_mod"] == -18
        assert result["components"]["hard_reject_posture"] == 0, (
            "Shallow proposal: hard_reject_posture is gated on _DEEP_TREATY_TYPES only"
        )
        # Deep (alliance) proposal: hard_reject fires at -100 AND
        # bilateral_betrayal_mod still provenanced at -18.
        deep_proposal = _minimal_proposal("France", "Austria", ptype="alliance")
        deep_result = calculate_acceptance(deep_proposal, world)
        assert deep_result["components"]["bilateral_betrayal_mod"] == -18
        assert deep_result["components"]["hard_reject_posture"] in (-100, -20), (
            "Deep-treaty hard-reject applies -100 (or -20 with shared enemy)"
        )

    def test_asker_equals_target_returns_zero(self):
        world = _clean_world()
        _seed_betrayal_strikes(world, "France", "France", 2)
        assert bilateral_betrayal_mod("France", "France", world) == 0


# ════════════════════════════════════════════════════════════════
# 4. reliability_modifier narrowing — // 10, cap +/-6
# ════════════════════════════════════════════════════════════════

class TestReliabilityModifierNarrowing:
    @pytest.mark.parametrize(
        "reliability, expected",
        [
            (0, 0),
            (10, 1),
            (30, 3),
            (60, 6),       # cap top
            (100, 6),      # hard cap
            (-10, -1),
            (-30, -3),
            (-60, -6),     # cap bottom
            (-100, -6),    # hard cap
        ],
    )
    def test_narrowed_formula(self, reliability, expected):
        world = _clean_world()
        world.diplomatic_reliability = {"France": reliability}
        proposal = _minimal_proposal("France", "Austria", ptype="peace")
        result = calculate_acceptance(proposal, world)
        assert result["components"]["reliability_modifier"] == expected


# ════════════════════════════════════════════════════════════════
# 5. Components dict — both new terms surface independently
# ════════════════════════════════════════════════════════════════

class TestComponentsSurface:
    def test_both_terms_keyed_independently(self, monkeypatch):
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.55)
        # Ensure France is seen as the hegemon leader (it's in its own bloc).
        _seed_betrayal_strikes(world, "France", "Austria", 1)
        proposal = _minimal_proposal("France", "Austria", ptype="peace")
        result = calculate_acceptance(proposal, world)
        components = result["components"]
        assert "hegemony_target_mod" in components
        assert "bilateral_betrayal_mod" in components
        # Hegemony: share=0.55 -> -int(0.25 * 60) = -15
        assert components["hegemony_target_mod"] == -15
        # Betrayal: 1 strike -> -6
        assert components["bilateral_betrayal_mod"] == -6

    def test_components_independence_when_one_zero(self, monkeypatch):
        """Hegemony active, betrayal zero: both keyed, one nonzero."""
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.55)
        proposal = _minimal_proposal("France", "Austria", ptype="peace")
        result = calculate_acceptance(proposal, world)
        assert result["components"]["hegemony_target_mod"] == -15
        assert result["components"]["bilateral_betrayal_mod"] == 0

    def test_feedback_strings_registered_for_new_keys(self):
        """Display-layer dict must carry negative voicing for both terms
        so `_generate_feedback` can surface them as largest-negative
        factors."""
        assert "hegemony_target_mod" in FEEDBACK_STRINGS
        assert FEEDBACK_STRINGS["hegemony_target_mod"]["negative"]
        assert "bilateral_betrayal_mod" in FEEDBACK_STRINGS
        assert FEEDBACK_STRINGS["bilateral_betrayal_mod"]["negative"]


# ════════════════════════════════════════════════════════════════
# 6. Preview warning — band-aware hegemony category
# ════════════════════════════════════════════════════════════════

class TestHegemonyWarningBands:
    def test_pre_noticed_zone_label_free(self, monkeypatch):
        """30-33%: no proper noun, no descriptive bloc phrase."""
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.31)
        warnings = build_proposal_commitment_warnings(
            world, "France", "Austria", "peace"
        )
        hegemony = [w for w in warnings if w["category"] == "hegemony"]
        assert len(hegemony) == 1
        text = hegemony[0]["text"]
        assert hegemony[0]["severity"] == "low"
        # Must not leak the descriptive label or proper noun at 30-33%
        assert "French" not in text, "30-33% zone must stay label-free"
        assert "System" not in text

    def test_noticed_band_descriptive_label(self, monkeypatch):
        """33-49%: descriptive bloc phrase, no proper noun."""
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.40)
        warnings = build_proposal_commitment_warnings(
            world, "France", "Austria", "peace"
        )
        hegemony = [w for w in warnings if w["category"] == "hegemony"]
        assert len(hegemony) == 1
        text = hegemony[0]["text"]
        assert hegemony[0]["severity"] == "medium"
        # Descriptive label ("French-led alignment") present, proper noun absent.
        assert "French-led alignment" in text or "alignment" in text
        assert "System" not in text, "Proper noun is 50%+ only"

    def test_alarming_band_proper_noun(self, monkeypatch):
        """50-59%: bloc_label (proper noun) from describe_hegemon_bloc."""
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.55)
        warnings = build_proposal_commitment_warnings(
            world, "France", "Austria", "peace"
        )
        hegemony = [w for w in warnings if w["category"] == "hegemony"]
        assert len(hegemony) == 1
        assert hegemony[0]["severity"] == "high"
        # describe_hegemon_bloc authors "French System" for France at 50%+.
        assert "French System" in hegemony[0]["text"]

    def test_crisis_band_critical_severity(self, monkeypatch):
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.65)
        warnings = build_proposal_commitment_warnings(
            world, "France", "Austria", "peace"
        )
        hegemony = [w for w in warnings if w["category"] == "hegemony"]
        assert len(hegemony) == 1
        assert hegemony[0]["severity"] == "critical"

    def test_asker_not_in_bloc_no_warning(self, monkeypatch):
        """Non-bloc asker must NOT see a hegemony warning — gates mirror
        `hegemony_target_mod` (prevents warning-without-modifier confusion)."""
        world = _clean_world()
        _stub_hegemon(monkeypatch, "France", 0.55)
        # Austria is not in France's bloc.
        warnings = build_proposal_commitment_warnings(
            world, "Austria", "Prussia", "peace"
        )
        assert not any(w["category"] == "hegemony" for w in warnings)

    def test_intra_bloc_target_no_warning(self, monkeypatch):
        world = _clean_world()
        key = world._make_diplo_key("France", "Saxony")
        world.diplomatic_states[key] = "ALLIANCE"
        world.invalidate_bloc_members_cache()
        _stub_hegemon(monkeypatch, "France", 0.55)
        warnings = build_proposal_commitment_warnings(
            world, "France", "Saxony", "peace"
        )
        assert not any(w["category"] == "hegemony" for w in warnings)

    def test_category_ordering_and_alias_preservation(self):
        """`concern` -> hegemony (sort key 4), `rivalry` -> peace_conflict
        (sort key 5). Both aliases remain so legacy saves/tests keep working."""
        assert WARNING_CATEGORY_ORDER["concern"] == WARNING_CATEGORY_ORDER["hegemony"]
        assert WARNING_CATEGORY_ORDER["rivalry"] == WARNING_CATEGORY_ORDER["peace_conflict"]

    def test_severity_sort_within_warning_list(self, monkeypatch):
        """Sort order: critical first. Construct a critical `hard_reject` +
        a medium `hegemony` and assert `hard_reject` sorts first."""
        world = _clean_world()
        _seed_betrayal_strikes(world, "France", "Austria", 3)
        _stub_hegemon(monkeypatch, "France", 0.40)
        warnings = build_proposal_commitment_warnings(
            world, "France", "Austria", "alliance"
        )
        # Re-apply the sort contract to verify input-order independence.
        sorted_warnings = _sort_structured_warnings(warnings)
        assert sorted_warnings[0]["category"] == "hard_reject"
        assert sorted_warnings[0]["severity"] == "critical"


# ════════════════════════════════════════════════════════════════
# 7. Cache invalidation — live share, not lagging high_water
# ════════════════════════════════════════════════════════════════

class TestHegemonyCacheInvalidation:
    def test_same_turn_bloc_widen_reads_new_share(self):
        """Same-turn ALLIANCE ratification widens the hegemon bloc.
        `build_proposal_commitment_warnings` must read the live share via
        `_identify_max_bloc_share`, NOT the sticky
        `world.hegemony_signal_high_water` field. Pins R3 from the plan."""
        world = _clean_world()
        # Deterministic geometry: F=9pts, A=6, B=6, P=6, R=3 (total 30).
        # France share = 9/30 = 0.30 — pre-noticed band, boundary zero.
        for r in world.regions.values():
            r.controller = "__sink__"
        _set_regions(world, "France", 3)
        _set_regions(world, "Austria", 2)
        _set_regions(world, "Britain", 2)
        _set_regions(world, "Prussia", 2)
        _set_regions(world, "Russia", 1)

        from backend.game_logic.coalition import _identify_max_bloc_share
        hegemon_before, share_before = _identify_max_bloc_share(world)
        assert hegemon_before == "France"
        assert share_before == pytest.approx(0.30, abs=1e-6)

        # Stale high_water — would lie if preview read from it.
        world.hegemony_signal_high_water = 0
        world.hegemony_signal_hegemon = "France"

        # Pre-alliance preview: band 0 (pre-noticed), severity "low".
        warnings_before = build_proposal_commitment_warnings(
            world, "France", "Britain", "peace"
        )
        heg_before = [w for w in warnings_before if w["category"] == "hegemony"]
        assert len(heg_before) == 1
        assert heg_before[0]["severity"] == "low"

        # Same-turn ALLIANCE ratification widens the hegemon bloc to F+A.
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        world.invalidate_bloc_members_cache()
        world.invalidate_active_nations_cache()

        # Post-alliance: bloc {F, A} = 15 pts / 30 = 0.50. Band 2 (alarming).
        # Tie-break may pick Austria (alphabetical) as hegemon identity —
        # irrelevant to the preview gate since France stays in-bloc.
        _, share_after = _identify_max_bloc_share(world)
        assert share_after == pytest.approx(0.50, abs=1e-6)

        warnings_after = build_proposal_commitment_warnings(
            world, "France", "Britain", "peace"
        )
        heg_after = [w for w in warnings_after if w["category"] == "hegemony"]
        assert len(heg_after) == 1, (
            "Cache invalidation must produce a fresh post-alliance warning"
        )
        assert heg_after[0]["severity"] == "high", (
            f"Preview lagged high_water (=0); expected band 2 severity='high', "
            f"got {heg_after[0]['severity']}"
        )
        # Proper noun reveal at 50%+.
        assert "System" in heg_after[0]["text"] or "Coalition" in heg_after[0]["text"]


# ════════════════════════════════════════════════════════════════
# 8. decision_reason alias round-trip (spec §10.1)
# ════════════════════════════════════════════════════════════════

class TestDecisionReasonAliasRoundtrip:
    def test_concern_pressure_renders_as_hegemony_pressure(self):
        """Legacy `concern_pressure` enum must render as 'hegemony pressure'
        so v2.4.3-named saves and old saves both display the same phrase."""
        assert diplomatic_decision_reason_display("concern_pressure") == "hegemony pressure"

    def test_hegemony_pressure_renders_as_hegemony_pressure(self):
        """Canonical v2.4.3 token also renders as 'hegemony pressure'."""
        assert diplomatic_decision_reason_display("hegemony_pressure") == "hegemony pressure"
