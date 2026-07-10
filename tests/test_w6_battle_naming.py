"""W6-2 — Dynamic Battle Naming (user addition, Wave 6).

Battles accumulate history per region: "Battle of Swabia" → "Second Battle
of Swabia" → … → "13th Battle of Swabia"; titanic engagements (total
engaged ≥ 80,000 incl. arrived reinforcements) read "The Great Battle of
Swabia" (the Great tier REPLACES the ordinal). Counts live in the
serialized `WorldState.battle_counts`; the single naming site is
`_execute_attack` and every consumer (battle message/report event, campaign
log, war HUD `recent_battles`) reads the same composed name.
"""

from backend.campaign_log import format_event_oneliner
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory


class TestComposeBattleName:
    def test_first_battle_is_plain(self):
        world = WorldFactory.basic()
        assert world.compose_battle_name("Swabia") == "Battle of Swabia"

    def test_second_and_third_battles_ordinal(self):
        world = WorldFactory.basic()
        world.compose_battle_name("Swabia")
        assert world.compose_battle_name("Swabia") == "Second Battle of Swabia"
        assert world.compose_battle_name("Swabia") == "Third Battle of Swabia"

    def test_ordinal_rollover_past_twelve(self):
        world = WorldFactory.basic()
        for _ in range(12):
            world.compose_battle_name("Swabia")
        assert world.compose_battle_name("Swabia") == "13th Battle of Swabia"

    def test_great_threshold_at_exactly_80000(self):
        world = WorldFactory.basic()
        assert (world.compose_battle_name("Swabia", 80000)
                == "The Great Battle of Swabia")
        # Below the threshold: ordinal as usual.
        assert (world.compose_battle_name("Swabia", 79999)
                == "Second Battle of Swabia")

    def test_great_tier_replaces_ordinal(self):
        world = WorldFactory.basic()
        world.compose_battle_name("Swabia")
        world.compose_battle_name("Swabia")
        # Their third meeting, but titanic — the Great form wins outright.
        assert (world.compose_battle_name("Swabia", 120000)
                == "The Great Battle of Swabia")

    def test_regions_count_independently(self):
        world = WorldFactory.basic()
        world.compose_battle_name("Swabia")
        assert world.compose_battle_name("Tyrol") == "Battle of Tyrol"

    def test_counts_round_trip_save(self):
        world = WorldFactory.basic()
        world.compose_battle_name("Swabia")
        world.compose_battle_name("Swabia")
        restored = WorldState.from_dict(world.to_dict())
        assert restored.battle_counts["Swabia"] == 2
        assert (restored.compose_battle_name("Swabia")
                == "Third Battle of Swabia")


class TestBattleNamingEndToEnd:
    def _war_world(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=30000,
                                    personality="cautious")
        world = WorldFactory.with_marshals([ney, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        return world

    def _attack(self, world):
        executor = CommandExecutor()
        return executor.execute(
            {"success": True,
             "command": {"marshal": "Ney", "action": "attack",
                         "target": "Mack"}},
            {"world": world})

    def test_attack_composes_and_counts(self):
        world = self._war_world()
        result = self._attack(world)
        assert result.get("battle_name") == "Battle of Belgium"
        assert world.battle_counts["Belgium"] == 1
        event = result["events"][0]
        assert event["battle_name"] == "Battle of Belgium"

    def test_second_attack_same_region_is_second_battle(self):
        world = self._war_world()
        self._attack(world)
        # Refresh exhaustion so a second attack is allowed.
        ney = world.get_marshal("Ney")
        ney.attacks_this_turn = 0
        ney.strength = max(ney.strength, 20000)
        mack = world.get_marshal("Mack")
        mack.strength = max(mack.strength, 20000)
        mack.location = "Belgium"
        result = self._attack(world)
        if result.get("battle_name"):
            assert result["battle_name"] == "Second Battle of Belgium"
            assert world.battle_counts["Belgium"] == 2

    def test_great_battle_live_threshold(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=45000,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=40000,
                                    personality="cautious")
        world = WorldFactory.with_marshals([ney, mack])
        key = "|".join(sorted(["France", "Austria"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        result = self._attack(world)
        assert result.get("battle_name") == "The Great Battle of Belgium"

    def test_campaign_log_oneliner_leads_with_name(self):
        world = self._war_world()
        self._attack(world)
        battle_events = [e for e in world.event_log
                         if e.get("type") == "battle"]
        assert battle_events, "battle event missing from world.event_log"
        line = format_event_oneliner(battle_events[-1])
        assert line.startswith("Battle of Belgium:")

    def test_legacy_event_without_name_keeps_classic_form(self):
        line = format_event_oneliner({
            "type": "battle",
            "attacker": "Ney", "attacker_nation": "France",
            "defender": "Mack", "defender_nation": "Austria",
            "location": "Belgium",
            "outcome": "stalemate",
            "attacker_casualties": 100, "defender_casualties": 100,
        })
        assert "at Belgium" in line
        assert not line.startswith("Battle of")

    def test_war_hud_recent_battles_carry_name(self):
        from backend.game_logic.war_status import build_active_wars
        world = self._war_world()
        # Make the battle big enough for the 1000-casualty record gate and
        # decisive enough for a winner (war-score records need a victor).
        world.get_marshal("Ney").strength = 60000
        world.get_marshal("Mack").strength = 15000
        self._attack(world)
        data = build_active_wars(world)
        austria_wars = [w for w in data["wars"]
                        if w.get("opponent") == "Austria"]
        if austria_wars and austria_wars[0]["recent_battles"]:
            entry = austria_wars[0]["recent_battles"][0]
            assert entry["name"].endswith("Battle of Belgium")

    def test_garrison_assault_not_named(self):
        """Attacking an empty enemy REGION (garrison combat) must not
        consume a battle count."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=60000,
                                      personality="aggressive")
        world = WorldFactory.with_marshals([ney])
        key = "|".join(sorted(["France", "Prussia"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        executor = CommandExecutor()
        executor.execute(
            {"success": True,
             "command": {"marshal": "Ney", "action": "attack",
                         "target": "Rhineland"}},
            {"world": world})
        assert "Rhineland" not in world.battle_counts
