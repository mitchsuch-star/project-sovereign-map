"""Slice C1b raw-vs-clamped treaty-harshness contract tests.

Spec §6.acceptance line 1115 requires a raw, unclamped sum for the
common-peace `term_harshness_penalty` so the helper can normalize over the
1.5 ceiling. Bilateral acceptance must keep the existing 1.0-clamped
behavior of `calculate_treaty_harshness()`. These tests pin both helpers
side by side.
"""

from __future__ import annotations

from backend.game_logic.diplomatic_templates import (
    calculate_raw_treaty_harshness,
    calculate_treaty_harshness,
)


def test_clamped_helper_caps_at_1_0():
    """`calculate_treaty_harshness()` (bilateral) must keep `min(1.0, ...)`."""
    treaty = {
        "clauses": [
            {"type": "territory_cede", "regions": ["A", "B", "C", "D", "E"]},
            {"type": "forced_alliance"},
        ],
    }
    # Raw = 0.3 * 5 + 0.4 = 1.9. Clamped = 1.0.
    assert calculate_treaty_harshness(treaty) == 1.0


def test_raw_helper_returns_unclamped_sum():
    """`calculate_raw_treaty_harshness()` returns the unclamped sum so
    common-peace can normalize over the 1.5 ceiling internally."""
    treaty = {
        "clauses": [
            {"type": "territory_cede", "regions": ["A", "B", "C", "D", "E"]},
            {"type": "forced_alliance"},
        ],
    }
    raw = calculate_raw_treaty_harshness(treaty)
    # 0.3 * 5 + 0.4 = 1.9 — must NOT be clamped at 1.0.
    assert abs(raw - 1.9) < 1e-9


def test_raw_helper_matches_clamped_for_below_1_packages():
    """For packages whose raw sum is already below 1.0, the two helpers
    must agree (same underlying clause/demand iteration)."""
    treaty = {
        "clauses": [
            {"type": "territory_cede", "regions": ["A"]},
        ],
        "demands": [
            {"type": "gold_per_turn", "amount": 100},
        ],
    }
    raw = calculate_raw_treaty_harshness(treaty)
    clamped = calculate_treaty_harshness(treaty)
    # Raw < 1.0 so they must agree.
    assert abs(raw - clamped) < 1e-9


def test_raw_helper_scores_dependency_demands():
    """Common-peace dependency terms must contribute to raw harshness."""
    treaty = {
        "demands": [
            {"type": "vassalage", "from": "Austria", "to": "France"},
            {"type": "subjugation", "from": "Saxony", "to": "France"},
        ],
    }

    raw = calculate_raw_treaty_harshness(treaty)

    assert abs(raw - 1.0) < 1e-9
