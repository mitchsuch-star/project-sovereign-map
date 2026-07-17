"""DD8 — Metternich's Armed Mediation (DWL-DIP-METTERNICH, 8.EVAL Batch Q).

Rejecting a Schemer-authored PEACE-family proposal plants a once-per-rejection,
5-turn-expiring war-pressure marker for that nation on the coalition-threat
scalar. AI-only, anti-stacking. See DIPLOMACY_SPEC.md §5c.
"""

from backend.models.world_state import WorldState
from backend.models.diplomat import DiplomaticRepresentative
from backend.game_logic.coalition import (
    record_schemer_peace_rejection,
    _calculate_schemer_peace_rejection_threat,
    process_coalition_turn,
    SCHEMER_PEACE_REJECTION_PRESSURE_TURNS,
    SCHEMER_PEACE_REJECTION_PRESSURE_AMOUNT,
    SCHEMER_PEACE_REJECTION_PRESSURE_CAP,
)


def _world():
    w = WorldState()
    w.current_turn = 10
    return w


def _set_diplomat(world, nation, personality):
    world.diplomats[nation] = DiplomaticRepresentative(
        name=f"{nation}Envoy", nation=nation, personality=personality, skill=8
    )


def test_austria_diplomat_is_schemer_by_default():
    """Austria ships Metternich (Schemer) — the canonical DD8 trigger source."""
    w = _world()
    metternich = w.diplomats.get("Austria")
    assert metternich is not None
    assert metternich.personality == "schemer"


def test_rejecting_schemer_peace_plants_marker():
    w = _world()
    _set_diplomat(w, "Austria", "schemer")
    planted = record_schemer_peace_rejection(w, "Austria", "armistice")
    assert planted is True
    assert w.schemer_rejection_pressure.get("Austria") == 10 + SCHEMER_PEACE_REJECTION_PRESSURE_TURNS


def test_peace_type_variants_all_qualify():
    for ptype in ("peace", "harsh_peace", "armistice",
                  "armistice_losing", "armistice_winning", "armistice_stalemate"):
        w = _world()
        _set_diplomat(w, "Austria", "schemer")
        assert record_schemer_peace_rejection(w, "Austria", ptype) is True, ptype


def test_non_peace_proposal_does_not_plant():
    """Subsidy / trade / alliance asks must NOT plant a war-pressure marker."""
    for ptype in ("open_borders", "alliance", "non_aggression", "gold_lump", "trade"):
        w = _world()
        _set_diplomat(w, "Austria", "schemer")
        assert record_schemer_peace_rejection(w, "Austria", ptype) is False, ptype
        assert not w.schemer_rejection_pressure


def test_non_schemer_proposer_does_not_plant():
    """A hawk/dove/loyalist court's rejected peace does not arm the marker."""
    for personality in ("hawk", "dove", "loyalist"):
        w = _world()
        _set_diplomat(w, "Russia", personality)
        assert record_schemer_peace_rejection(w, "Russia", "peace") is False, personality


def test_player_nation_never_plants():
    w = _world()
    _set_diplomat(w, "France", "schemer")
    assert record_schemer_peace_rejection(w, "France", "peace") is False


def test_threat_contribution_and_cap():
    w = _world()
    # One active marker → one unit of pressure.
    _set_diplomat(w, "Austria", "schemer")
    record_schemer_peace_rejection(w, "Austria", "armistice")
    assert _calculate_schemer_peace_rejection_threat(w) == SCHEMER_PEACE_REJECTION_PRESSURE_AMOUNT
    # Several markers → capped total.
    for n in ("Russia", "Prussia", "Britain", "Spain"):
        _set_diplomat(w, n, "schemer")
        record_schemer_peace_rejection(w, n, "peace")
    assert _calculate_schemer_peace_rejection_threat(w) == SCHEMER_PEACE_REJECTION_PRESSURE_CAP


def test_anti_stacking_refreshes_not_stacks():
    """A repeat rejection from the same nation refreshes expiry, never stacks."""
    w = _world()
    _set_diplomat(w, "Austria", "schemer")
    record_schemer_peace_rejection(w, "Austria", "armistice")
    first = _calculate_schemer_peace_rejection_threat(w)
    w.current_turn = 12
    record_schemer_peace_rejection(w, "Austria", "peace")  # same nation again
    assert len(w.schemer_rejection_pressure) == 1  # still one marker
    assert w.schemer_rejection_pressure["Austria"] == 12 + SCHEMER_PEACE_REJECTION_PRESSURE_TURNS
    assert _calculate_schemer_peace_rejection_threat(w) == first  # no stacked pressure


def test_marker_expires_and_is_pruned():
    w = _world()
    _set_diplomat(w, "Austria", "schemer")
    record_schemer_peace_rejection(w, "Austria", "armistice")  # expires turn 15
    w.current_turn = 15  # expires_on_turn <= current_turn → expired
    assert _calculate_schemer_peace_rejection_threat(w) == 0
    assert "Austria" not in w.schemer_rejection_pressure  # pruned in place


def test_process_coalition_turn_adds_threat():
    w = _world()
    _set_diplomat(w, "Austria", "schemer")
    record_schemer_peace_rejection(w, "Austria", "armistice")
    before = w.threat_level
    process_coalition_turn(w)
    # Threat moves by the DD8 contribution net of decay; the source is logged.
    sources = [s["source"] for s in w.threat_sources_this_turn]
    assert "schemer_peace_rejection" in sources
    assert w.threat_level >= before  # net non-negative given the standing pressure


def test_marker_serialization_roundtrip():
    w = _world()
    _set_diplomat(w, "Austria", "schemer")
    record_schemer_peace_rejection(w, "Austria", "armistice")
    data = w.to_dict()
    assert data["schemer_rejection_pressure"] == {"Austria": 15}
    w2 = WorldState.from_dict(data)
    assert w2.schemer_rejection_pressure == {"Austria": 15}


def test_executor_reject_path_plants_marker():
    """End-to-end: the reject-AI-proposal executor handler plants the marker."""
    from backend.commands.executor import CommandExecutor
    w = _world()
    _set_diplomat(w, "Austria", "schemer")
    ex = CommandExecutor()
    dialogue = {
        "type": "incoming_proposal",
        "context": {
            "source_nation": "Austria",
            "proposal_type": "armistice",
            "proposal": {"type": "armistice"},
        },
    }
    # Prime the dialogue stack so pop() has something to remove.
    w.dialogue_manager.push({"type": "incoming_proposal", "context": dialogue["context"]})
    result = ex._handle_reject_ai_proposal(dialogue, w)
    assert result["success"] is True
    assert w.schemer_rejection_pressure.get("Austria") == 15
