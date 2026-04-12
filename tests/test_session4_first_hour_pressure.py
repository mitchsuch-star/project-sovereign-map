"""Session 4 regression coverage for PL-28 and PL-26."""

import random

from backend.commands.executor import CommandExecutor
from backend.game_logic.dispatch import build_morning_dispatch
from backend.models.world_state import WorldState
from backend.notifications import DEFEAT_IMMINENT_WARNING, TURN_LIMIT_WARNING


def _make_world() -> WorldState:
    return WorldState(player_nation="France")


def _make_executor() -> CommandExecutor:
    return CommandExecutor()


def _set_only_french_regions(world: WorldState, region_names) -> None:
    allowed = set(region_names)
    for name, region in world.regions.items():
        region.controller = "France" if name in allowed else "Prussia"
    world.invalidate_active_nations_cache()


def _defeat_warning_notifications(world: WorldState):
    return [
        n for n in world.notifications.get_pending()
        if n.get("type") == DEFEAT_IMMINENT_WARNING
    ]


def _run_naive_opener(seed: int):
    random.seed(seed)
    world = _make_world()
    world.opening_attack_guidance_shown = True
    executor = _make_executor()
    ney = world.get_marshal("Ney")
    wellington = world.get_marshal("Wellington")

    result = executor._combat._execute_attack(ney, "Wellington", world, {"world": world})
    return {
        "result": result,
        "ney_strength": int(ney.strength),
        "wellington_strength": int(wellington.strength),
    }


def _run_prepared_opener(seed: int):
    random.seed(seed)
    world = _make_world()
    world.opening_attack_guidance_shown = True
    executor = _make_executor()
    ney = world.get_marshal("Ney")
    drouot = world.get_marshal("Drouot")
    wellington = world.get_marshal("Wellington")

    drouot.location = "Belgium"
    drouot.moved_this_turn = False
    drouot.bombardments_this_turn = 0

    bombardment = executor._combat._execute_bombardment(drouot, wellington, world, {"world": world})
    attack = executor._combat._execute_attack(ney, "Wellington", world, {"world": world})
    return {
        "bombardment": bombardment,
        "attack": attack,
        "ney_strength": int(ney.strength),
        "wellington_strength": int(wellington.strength),
    }


class TestPL28DefeatImminentWarning:
    def test_one_army_warning_hits_dispatch_and_notifications(self):
        world = _make_world()
        for marshal in world.get_player_marshals():
            if marshal.name != "Ney":
                marshal.strength = 0

        dispatch = build_morning_dispatch(world)

        warning = dispatch.get("defeat_imminent_warning")
        assert warning is not None
        assert warning["living_marshal_count"] == 1
        assert warning["living_marshals"] == ["Ney"]
        assert "campaign ends" in warning["message"]

        notifications = _defeat_warning_notifications(world)
        assert len(notifications) == 1
        assert notifications[0]["title"] == "One Army Remains"

    def test_warning_dedupes_while_persistent_and_clears_on_recovery(self):
        world = _make_world()
        _set_only_french_regions(world, ["Paris"])

        first_dispatch = build_morning_dispatch(world)
        second_dispatch = build_morning_dispatch(world)

        assert first_dispatch.get("defeat_imminent_warning") is not None
        assert second_dispatch.get("defeat_imminent_warning") is not None
        assert len(_defeat_warning_notifications(world)) == 1

        world.regions["Belgium"].controller = "France"
        world.invalidate_active_nations_cache()
        recovered_dispatch = build_morning_dispatch(world)

        assert recovered_dispatch.get("defeat_imminent_warning") is None
        assert _defeat_warning_notifications(world) == []

    def test_turn_limit_warning_stays_separate(self):
        world = _make_world()
        world.current_turn = 36
        world.max_turns = 40
        _set_only_french_regions(world, ["Paris"])

        dispatch = build_morning_dispatch(world)
        notifications = world.notifications.get_pending()
        types = {n["type"] for n in notifications}

        assert dispatch.get("turn_limit_warning") is not None
        assert dispatch.get("defeat_imminent_warning") is not None
        assert TURN_LIMIT_WARNING in types
        assert DEFEAT_IMMINENT_WARNING in types


class TestPL26OpenerGuidance:
    def test_common_opener_surfaces_pre_commit_guidance_once(self):
        world = _make_world()
        executor = _make_executor()
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        result = executor._combat._execute_attack(ney, "Wellington", world, {"world": world})

        assert result["success"] is True
        assert result["free_action"] is True
        assert result.get("opening_attack_guidance") is not None
        assert world.opening_attack_guidance_shown is True
        assert int(ney.strength) == 72000
        assert int(wellington.strength) == 52000

        tip = result["opening_attack_guidance"]["tip"]
        assert "Drouot" in tip
        assert "Davout" in tip

    def test_guidance_falls_back_when_drouot_is_unavailable(self):
        world = _make_world()
        executor = _make_executor()
        world.get_marshal("Drouot").strength = 0
        ney = world.get_marshal("Ney")
        wellington = world.get_marshal("Wellington")

        result = executor._combat._execute_attack(ney, "Wellington", world, {"world": world})

        tip = result["opening_attack_guidance"]["tip"]
        assert "Drouot" not in tip
        assert "Davout" in tip

    def test_guidance_flag_roundtrips_through_save_load(self):
        world = _make_world()
        world.opening_attack_guidance_shown = True

        restored = WorldState.from_dict(world.to_dict())

        assert restored.opening_attack_guidance_shown is True

    def test_prepared_artillery_line_beats_naive_line_deterministically(self):
        for seed in (1, 2, 3, 4, 5):
            naive = _run_naive_opener(seed)
            prepared = _run_prepared_opener(seed)

            assert naive["result"]["success"] is True
            assert prepared["bombardment"]["success"] is True
            assert prepared["attack"]["success"] is True
            assert prepared["ney_strength"] > naive["ney_strength"]
            assert prepared["wellington_strength"] < naive["wellington_strength"]
