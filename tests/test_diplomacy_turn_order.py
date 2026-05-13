from backend.game_logic.diplomacy import process_diplomacy_turn
from backend.models.world_state import WorldState


def _install_vassal(
    world: WorldState,
    *,
    lord: str = "France",
    vassal: str = "Saxony",
    loyalty: int = 60,
) -> str:
    world.vassals[vassal] = {
        "lord": lord,
        "loyalty": int(loyalty),
        "autonomy": 1,
        "path": "treaty",
        "created_turn": 1,
        "tribute_rate": 0.75,
        "carved_from": None,
        "regions": None,
    }
    key = world._make_diplo_key(lord, vassal)
    world.diplomatic_states[key] = "VASSAL"
    world.nation_relations[key] = 0
    return key


def test_vassal_rebellion_runs_before_armistice_expiration():
    world = WorldState(player_nation="France")
    key = _install_vassal(world, loyalty=0)
    world.diplomatic_states[key] = "ARMISTICE"
    world.armistice_turns = {key: 4}
    world.nation_relations[key] = 0

    events = process_diplomacy_turn(world)
    event_types = [event.get("type") for event in events]

    assert event_types.index("vassal_rebellion_armistice") < event_types.index(
        "armistice_expired_peace"
    )
    assert "Saxony" not in world.vassals
    assert world.diplomatic_states[key] == "PEACE"


def test_advance_turn_decrements_vassal_cooldowns_once():
    world = WorldState(player_nation="France")
    _install_vassal(world, loyalty=60)
    world.vassal_investment_cooldowns = {"Saxony": 2}

    world.advance_turn()

    assert world.vassal_investment_cooldowns == {"Saxony": 1}
