from backend.game_logic.diplomacy import WARNING_CATEGORY_ORDER, _build_breach_warnings


def _sample_breach_preview():
    return {
        "breach_severity": "high",
        "reliability_before": 12,
        "reliability_after": 2,
        "would_trigger_hard_reject": False,
    }


def test_war_joiner_preview_warnings_use_peace_conflict_category():
    warnings = _build_breach_warnings(
        _sample_breach_preview(),
        {
            "defensive_joiners": ["Austria"],
            "offensive_joiners": ["Prussia"],
        },
    )

    joiner_warnings = [warning for warning in warnings if warning["text"].startswith("Likely ")]
    assert len(joiner_warnings) == 2
    assert {warning["category"] for warning in joiner_warnings} == {"peace_conflict"}


def test_warning_category_order_keeps_legacy_aliases_stable():
    assert WARNING_CATEGORY_ORDER["hegemony"] == WARNING_CATEGORY_ORDER["concern"] == 4
    assert WARNING_CATEGORY_ORDER["peace_conflict"] == WARNING_CATEGORY_ORDER["rivalry"] == 5
