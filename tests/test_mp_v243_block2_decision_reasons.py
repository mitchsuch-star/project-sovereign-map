from backend.display_names import diplomatic_decision_reason_display
from backend.game_logic.diplomacy import (
    determine_ai_offer_decision_reason,
    determine_counterparty_decision_reason,
)
from backend.game_logic.mailbox_payloads import build_pending_envoy_popup_from_terms
from backend.models.world_state import WorldState


def _make_world() -> WorldState:
    world = WorldState(player_nation="France")
    world.enemy_nations = []
    return world


def test_ai_offer_reason_uses_hegemony_pressure_when_threat_or_wars_are_high():
    world = _make_world()
    world.threat_level = 65

    assert determine_ai_offer_decision_reason("Britain", "alliance", world) == "hegemony_pressure"


def test_ai_offer_reason_uses_unknown_baseline_when_no_pressure_is_detected():
    world = _make_world()
    world.threat_level = 0

    assert determine_ai_offer_decision_reason("Prussia", "alliance", world) == "unknown_baseline"


def test_counterparty_reason_uses_hegemony_pressure_as_the_default_branch():
    world = _make_world()
    proposal = {
        "proposer_nation": "France",
        "target_nation": "Austria",
        "type": "alliance",
    }

    assert determine_counterparty_decision_reason(proposal, world, acceptance_result={"components": {}}) == "hegemony_pressure"


def test_decision_reason_display_keeps_legacy_rival_pressure_as_alias():
    assert diplomatic_decision_reason_display("hegemony_pressure") == "hegemony pressure"
    assert diplomatic_decision_reason_display("unknown_baseline") == "unknown baseline"
    assert diplomatic_decision_reason_display("rival_pressure") == "hegemony pressure"
    assert diplomatic_decision_reason_display("concern_pressure") == "hegemony pressure"


def test_pending_envoy_popup_displays_legacy_rival_pressure_with_canonical_label():
    popup = build_pending_envoy_popup_from_terms(
        _make_world(),
        nation="Prussia",
        terms={"type": "peace", "demands": [], "sweeteners": [], "clauses": []},
        decision_reason="rival_pressure",
    )

    assert popup["decision_reason"] == "rival_pressure"
    assert popup["decision_reason_display"] == "hegemony pressure"


# ── S14D-X37 (October 23, 2026): the stamp follows the feedback's own ranking ──


def test_s14d_x37_the_stamp_follows_the_feedbacks_top_term():
    """Probed on the 1805 boot: every refusal stamped `hegemony_pressure` on a
    bare `hegemony_target_mod < 0` test while the feedback named the league in
    15 of 16 cases. The stamp now reads the largest negative term over the
    ONE trackable set the feedback ranks."""
    world = _make_world()
    proposal = {"proposer_nation": "France", "target_nation": "Austria", "type": "peace"}

    def reason(components):
        return determine_counterparty_decision_reason(
            proposal, world, acceptance_result={"components": components})

    assert reason({"coalition_loyalty": -15, "relation_modifier": -10, "hegemony_target_mod": -5}) == "league_loyalty"
    assert reason({"coalition_bond": -20, "hegemony_target_mod": -5}) == "league_loyalty"
    assert reason({"relation_modifier": -10, "hegemony_target_mod": -5}) == "cold_court"
    assert reason({"hegemony_target_mod": -12, "relation_modifier": -3}) == "hegemony_pressure"
    assert reason({"agenda_mod": -8, "hegemony_target_mod": -5}) == "agenda_pursuit"
    assert reason({"war_weariness": -14, "hegemony_target_mod": -5}) == "war_overload"
    assert diplomatic_decision_reason_display("league_loyalty") == "the league's bond"
    assert diplomatic_decision_reason_display("cold_court") == "an old hostility"


def test_s14d_x37_both_reasons_are_voiced_in_every_register():
    from backend.game_logic.diplomatic_templates import _INCOMING_MOTIVE_LINES, _MOTIVE_REASONS
    for reason in ("league_loyalty", "cold_court"):
        assert reason in _MOTIVE_REASONS
        for register in ("hawk", "schemer", "dove", "chancery", "loyalist"):
            lines = _INCOMING_MOTIVE_LINES[(register, reason)]
            assert len(lines) >= 2 and all("{nation}" in ln for ln in lines), (register, reason)


def test_s14d_x37_the_feedback_and_the_stamp_share_one_ranking():
    import inspect
    from backend.game_logic import diplomacy as D
    assert "_ranked_components(components)" in inspect.getsource(D._generate_feedback)
    assert "_ranked_components(components)[1][0]" in inspect.getsource(D.determine_counterparty_decision_reason)
    assert D._REASON_BY_TOP_TERM["coalition_loyalty"] == "league_loyalty"
