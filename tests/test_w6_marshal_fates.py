"""W6-7 — Marshal Fates: capture, ransom, the last stand (EXP-M1).

Commit 1 (capture core): a cornered marshal (strength < 5,000 on forced
retreat, or encircled/desperation-only retreat) rolls escape 60% /
captured 40%; pure encirclement is captured outright; an aggressive
player marshal gets the last-stand choice (fight_to_the_last /
attempt_breakout), an aggressive AI marshal decides by deterministic rule.
Captured marshals leave the map (held at the captor's capital, strength
0), half their men filter home to the manpower pool, and their ES-7
expectations freeze. Building Blocks: identical rules for the AI — Mack
at Ulm becomes capturable.
"""

import random

import pytest

from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.models.marshal import Marshal
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _cornered_pair(personality="cautious", strength=3000,
                   nation="France", enemy_nation="Austria"):
    """A weak marshal at Belgium facing a monster — fate-trigger territory."""
    weak = MarshalFactory.infantry(name="Weak", location="Belgium",
                                   strength=strength,
                                   personality=personality, nation=nation)
    monster = MarshalFactory.enemy(name="Monster", location="Belgium",
                                   nation=enemy_nation, strength=80000,
                                   personality="cautious")
    world = WorldFactory.with_marshals([weak, monster])
    _war(world, nation, enemy_nation)
    return world, weak, monster


class TestFateTrigger:
    def test_strong_marshal_with_safe_retreat_never_rolls(self):
        world, weak, monster = _cornered_pair(strength=20000)
        executor = CommandExecutor()
        msg = executor._combat._check_marshal_fate(weak, monster, world)
        assert msg is None
        assert weak.captured_by == ""

    def test_low_strength_triggers_the_roll(self):
        world, weak, monster = _cornered_pair(strength=3000)
        executor = CommandExecutor()
        random.seed(1)
        outcomes = set()
        for seed in range(12):
            world2, weak2, monster2 = _cornered_pair(strength=3000)
            random.seed(seed)
            msg = CommandExecutor()._combat._check_marshal_fate(
                weak2, monster2, world2)
            outcomes.add("captured" if weak2.captured_by else "escaped")
        # Seeded roll reaches BOTH branches across seeds.
        assert outcomes == {"captured", "escaped"}

    def test_encirclement_is_captured_outright(self):
        weak = MarshalFactory.infantry(name="Weak", location="Belgium",
                                       strength=12000,
                                       personality="cautious")
        monster = MarshalFactory.enemy(name="Monster", location="Belgium",
                                       nation="Austria", strength=80000)
        # Enemies in EVERY Belgium-adjacent region → encircled.
        blockers = [
            MarshalFactory.enemy(name=f"Blk{i}", location=loc,
                                 nation="Austria", strength=30000)
            for i, loc in enumerate(
                ["Paris", "Normandy", "Netherlands", "Waterloo", "Rhineland"])
        ]
        world = WorldFactory.with_marshals([weak, monster, *blockers])
        _war(world)
        executor = CommandExecutor()
        msg = executor._combat._check_marshal_fate(weak, monster, world)
        assert msg is not None and "CAPTURED" in msg
        assert weak.captured_by == "Austria"

    def test_capture_moves_him_to_the_captor_capital(self):
        world, weak, monster = _cornered_pair()
        executor = CommandExecutor()
        msg = executor._combat._capture_marshal(weak, "Austria", world)
        assert weak.captured_by == "Austria"
        assert weak.strength == 0
        assert weak.location == world.get_nation_capital("Austria")
        assert weak.captured_turn == world.current_turn
        assert "CAPTURED" in msg

    def test_half_the_men_filter_home(self):
        world, weak, monster = _cornered_pair(strength=4000)
        pool_before = world.manpower_pools["France"]["infantry"]
        CommandExecutor()._combat._capture_marshal(weak, "Austria", world)
        assert world.manpower_pools["France"]["infantry"] \
            == pool_before + 2000

    def test_capture_event_reaches_log_and_headline(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
        from backend.game_logic.dispatch import HEADLINE_WEIGHTS, _build_headline
        assert "marshal_captured" in CAMPAIGN_LOG_TYPES
        assert HEADLINE_WEIGHTS["marshal_captured"] == 95
        world, weak, monster = _cornered_pair()
        CommandExecutor()._combat._capture_marshal(weak, "Austria", world)
        events = [e for e in world.event_log
                  if e.get("type") == "marshal_captured"]
        assert len(events) == 1
        assert "CAPTURED" in format_event_oneliner(events[0])
        headline = _build_headline(world, "France")
        assert headline["class"] == "marshal_captured"


class TestLastStand:
    def test_player_aggressive_gets_the_choice(self):
        world, weak, monster = _cornered_pair(personality="aggressive")
        executor = CommandExecutor()
        msg = executor._combat._check_marshal_fate(weak, monster, world)
        assert msg is not None and "CORNERED" in msg
        pi = weak.pending_interrupt
        assert pi["interrupt_type"] == "last_stand"
        assert pi["marshal"] == "Weak"  # the July-7 L1 lesson
        assert set(pi["options"]) == {"fight_to_the_last", "attempt_breakout"}
        assert weak.captured_by == ""  # nothing resolved yet

    def test_fight_to_the_last_bleeds_and_halts_the_enemy(self):
        world, weak, monster = _cornered_pair(personality="aggressive")
        executor = CommandExecutor()
        executor._combat._check_marshal_fate(weak, monster, world)
        enemy_before = monster.strength
        proc = StrategicOrderProcessor(executor)
        result = proc.handle_response("Weak", "last_stand",
                                      "fight_to_the_last", world,
                                      {"world": world})
        assert result["success"] is True
        assert "LAST STAND" in result["message"]
        assert monster.strength < enemy_before
        assert monster.moved_this_turn is True  # the pursuit is halted
        assert weak.captured_by == "Austria"    # survivors taken after
        assert any(e.get("type") == "last_stand" for e in world.event_log)

    def test_breakout_rolls_both_ways(self):
        outcomes = set()
        for seed in range(14):
            world, weak, monster = _cornered_pair(personality="aggressive")
            executor = CommandExecutor()
            executor._combat._check_marshal_fate(weak, monster, world)
            random.seed(seed)
            proc = StrategicOrderProcessor(executor)
            proc.handle_response("Weak", "last_stand", "attempt_breakout",
                                 world, {"world": world})
            outcomes.add("captured" if weak.captured_by else "escaped")
        assert outcomes == {"captured", "escaped"}

    def test_ai_aggressive_fights_on_home_soil(self):
        """GR5: the AI rule is deterministic — defending homeland ground,
        an aggressive AI marshal dies on his feet (and bleeds the victor)."""
        weak = MarshalFactory.enemy(name="Mack", location="Rhineland",
                                    nation="Prussia", strength=3000,
                                    personality="aggressive")
        hunter = MarshalFactory.infantry(name="Ney", location="Rhineland",
                                         strength=80000)
        world = WorldFactory.with_marshals([weak, hunter])
        _war(world, "France", "Prussia")
        assert "Rhineland" in world.nation_starting_regions.get("Prussia", [])
        hunter_before = hunter.strength
        msg = CommandExecutor()._combat._check_marshal_fate(
            weak, hunter, world)
        assert msg is not None and "LAST STAND" in msg
        assert weak.captured_by == "France"
        assert hunter.strength < hunter_before

    def test_mack_is_capturable_by_the_player(self):
        """Building Blocks: the same fate machinery takes enemy marshals."""
        outcomes = set()
        for seed in range(14):
            mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                        nation="Austria", strength=3000,
                                        personality="cautious")
            ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                          strength=80000)
            world = WorldFactory.with_marshals([mack, ney])
            _war(world)
            random.seed(seed)
            CommandExecutor()._combat._check_marshal_fate(mack, ney, world)
            outcomes.add("captured" if mack.captured_by else "escaped")
        assert "captured" in outcomes


class TestCapturedState:
    def _captured(self):
        world, weak, monster = _cornered_pair()
        CommandExecutor()._combat._capture_marshal(weak, "Austria", world)
        return world, weak

    def test_serialization_round_trip(self):
        world, weak = self._captured()
        restored = WorldState.from_dict(world.to_dict())
        m = restored.get_marshal("Weak")
        assert m.captured_by == "Austria"
        assert m.captured_turn == world.current_turn

    def test_marshal_defaults(self):
        m = MarshalFactory.infantry(name="Ney")
        data = m.to_dict()
        del data["captured_by"]
        del data["captured_turn"]
        restored = Marshal.from_dict(data)
        assert restored.captured_by == ""
        assert restored.captured_turn == -1

    def test_attrition_sweep_never_deletes_a_prisoner(self):
        world, weak = self._captured()
        world.process_supply_attrition()
        assert world.get_marshal("Weak") is not None

    def test_absent_from_dispatch_roster_present_in_prisoners(self):
        from backend.game_logic.dispatch import build_morning_dispatch
        world, weak = self._captured()
        dispatch = build_morning_dispatch(world)
        names = [m["name"] for m in dispatch["marshals"]]
        assert "Weak" not in names
        assert dispatch["prisoners"][0]["name"] == "Weak"
        assert dispatch["prisoners"][0]["captor"] == "Austria"

    def test_marshal_card_names_the_fate(self):
        from backend.game_logic.marshal_overview import build_marshal_overview
        world, weak = self._captured()
        cards = build_marshal_overview(world)
        card = next(c for c in cards if c["name"] == "Weak")
        assert card["captured"] is True
        assert "PRISONER of Austria" in card["status_note"]

    def test_muster_and_reinforcement_scans_skip_prisoners(self):
        world, weak = self._captured()
        # Give the prisoner's nation another battle to scan around.
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000)
        mack = MarshalFactory.enemy(name="Mack2", location="Belgium",
                                    nation="Austria", strength=30000)
        world.marshals["Ney"] = ney
        world.marshals["Mack2"] = mack
        executor = CommandExecutor()
        results = executor._combat._calculate_reinforcements(
            ney, mack, "Belgium", "France", world)
        assert all(r["marshal"] != "Weak" for r in results)
        preview = executor._combat._build_muster_preview(
            ney, mack, world, {"world": world})
        assert all(r["marshal"] != "Weak" for r in preview["rows"])

    def test_enemy_ai_contact_scan_survives_prisoners(self):
        from backend.ai.enemy_ai import EnemyAI
        world, weak = self._captured()
        ai = EnemyAI(CommandExecutor())
        # A full AI turn for the captor nation must not crash on the
        # 0-strength prisoner standing in their capital.
        try:
            ai.process_nation_turn("Austria", world, {"world": world})
        except Exception as exc:  # pragma: no cover
            pytest.fail(f"enemy AI crashed on a captured marshal: {exc}")

    def test_es7_expectations_freeze_while_captured(self):
        """The cheapest rule, pinned: no erosion while he sits in a foreign
        capital — the grace clock resets."""
        world, weak = self._captured()
        world.sovereign_map = "europe"
        weak.battles_won = 8            # high expectation
        weak.expectation_grace_turn = 1  # clock was running
        trust_before = weak.trust.value if hasattr(weak.trust, "value") \
            else weak.trust
        world.current_turn = 10
        world._dotation_processed_turn = None
        world._process_dotation_state()
        # The grace clock is reset and trust untouched by erosion.
        assert weak.expectation_grace_turn == -1
        trust_after = weak.trust.value if hasattr(weak.trust, "value") \
            else weak.trust
        assert trust_after == trust_before
