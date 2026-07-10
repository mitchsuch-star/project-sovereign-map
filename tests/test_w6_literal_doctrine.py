"""W6-5 — The Literal Doctrine (user addition, Wave 6).

User steer (load-bearing): literal marshals need not object — the fantasy
is "generals who do exactly what they're ordered." Engagement comes from
fidelity you can SEE (order echo, fidelity beat), precision you can
exploit (1 AP, Immovable), and consequences you were warned about (the
muster preview). Formally supersedes the R59/R153 literal-objection
triggers (converted to a doctrine comment in personality.py).
"""

from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.game_logic.marshal_voice import (
    LITERAL_ACK,
    LITERAL_COMPLETE,
    LITERAL_NO_MARCH,
    emit_literal_fidelity_events,
    literal_ack,
    literal_completion,
    literal_no_march,
)
from backend.models.marshal import StrategicOrder

from tests.conftest import MarshalFactory, WorldFactory


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


def _literal(name="Soult", location="Belgium", strength=20000):
    return MarshalFactory.infantry(name=name, location=location,
                                   strength=strength, personality="literal")


# ════════════════════════════════════════════════════════════════════════
# §7.2.1 Never-objects, pinned
# ════════════════════════════════════════════════════════════════════════

class TestLiteralNeverObjects:
    def test_literal_never_objects(self):
        """A literal marshal ordered into terrible odds raises NO objection
        — the order proceeds/gates through the normal odds machinery
        (the W6-4 muster confirm) instead."""
        soult = _literal(strength=10000)
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=60000)
        world = WorldFactory.with_marshals([soult, mack])
        _war(world)
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Soult", "action": "attack",
                         "target": "Mack"}},
            {"world": world})
        assert world.pending_objection is None
        assert result.get("pending_objection") is None
        # The odds machinery (muster confirm) is what catches it.
        assert result.get("pending_interrupt", {}).get(
            "interrupt_type") == "muster_confirm"

    def test_literal_triggers_table_is_empty_by_design(self):
        from backend.models.personality import (
            PERSONALITY_TRIGGERS, Personality,
        )
        assert PERSONALITY_TRIGGERS[Personality.LITERAL] == {}


# ════════════════════════════════════════════════════════════════════════
# §7.2.2 Order echo & completion report
# ════════════════════════════════════════════════════════════════════════

class TestOrderEcho:
    def test_acknowledgment_quotes_the_verbatim_command(self):
        soult = _literal(location="Paris")
        world = WorldFactory.with_marshals([soult])
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "is_strategic": True,
             "strategic_type": "MOVE_TO",
             "raw_input": "Soult, march to Belgium",
             "command": {"marshal": "Soult", "action": "move",
                         "target": "Belgium"}},
            {"world": world})
        assert result.get("success") is True
        assert '"Soult, march to Belgium."' in result["message"]
        assert "It will be done exactly" in result["message"] \
            or "No more and no less" in result["message"] \
            or "Understood to the letter" in result["message"]

    def test_precision_caption_on_creation(self):
        soult = _literal(location="Paris")
        world = WorldFactory.with_marshals([soult])
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "is_strategic": True,
             "strategic_type": "MOVE_TO",
             "raw_input": "Soult, march to Belgium",
             "command": {"marshal": "Soult", "action": "move",
                         "target": "Belgium"}},
            {"world": world})
        assert "1 AP" in result["message"]
        assert "fewer couriers" in result["message"]

    def test_non_literal_gets_no_echo(self):
        ney = MarshalFactory.infantry(name="Ney", location="Paris",
                                      personality="aggressive")
        world = WorldFactory.with_marshals([ney])
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "is_strategic": True,
             "strategic_type": "MOVE_TO",
             "raw_input": "Ney, march to Belgium",
             "command": {"marshal": "Ney", "action": "move",
                         "target": "Belgium"}},
            {"world": world})
        assert "It will be done exactly" not in result.get("message", "")
        assert "fewer couriers" not in result.get("message", "")

    def test_completion_quotes_the_order(self):
        soult = _literal(location="Belgium")
        soult.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Belgium", target_type="region",
            started_turn=1, original_command="Soult, march to Belgium")
        world = WorldFactory.with_marshals([soult])
        proc = StrategicOrderProcessor(CommandExecutor())
        result = proc._complete_order(soult, world, "Belgium is reached.")
        assert '"Soult, march to Belgium"' in result["message"]
        assert "Belgium is reached." in result["message"]
        assert result["precision_bonus"] is True

    def test_non_literal_completion_unchanged(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      personality="aggressive")
        ney.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Belgium", target_type="region",
            started_turn=1, original_command="Ney, march to Belgium")
        world = WorldFactory.with_marshals([ney])
        proc = StrategicOrderProcessor(CommandExecutor())
        result = proc._complete_order(ney, world, "Belgium is reached.")
        assert result["message"] == "Belgium is reached."


# ════════════════════════════════════════════════════════════════════════
# §7.2.4 The fidelity beat
# ════════════════════════════════════════════════════════════════════════

class TestFidelityBeat:
    def _held_order(self, marshal, location):
        marshal.strategic_order = StrategicOrder(
            command_type="HOLD", target=location, target_type="region",
            started_turn=1, original_command=f"{marshal.name}, hold {location}")

    def test_fires_on_adjacent_battle_held(self):
        soult = _literal(location="Belgium")
        self._held_order(soult, "Belgium")
        world = WorldFactory.with_marshals([soult])
        world.current_turn = 3
        world.event_log = [{
            "type": "battle", "location": "Waterloo",
            "attacker": "Blucher", "attacker_nation": "Prussia",
            "defender": "Ney", "defender_nation": "France",
            "outcome": "stalemate", "turn": 3,
        }]
        events = emit_literal_fidelity_events(world)
        assert len(events) == 1
        e = events[0]
        assert e["type"] == "literal_fidelity"
        assert e["marshal"] == "Soult"
        assert "holds at Belgium" in e["message"]
        assert "Waterloo" in e["message"]
        # Logged into the event log for the campaign log.
        assert any(le.get("type") == "literal_fidelity"
                   for le in world.event_log)

    def test_does_not_fire_for_non_literal(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      personality="aggressive")
        ney.strategic_order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="Ney, hold Belgium")
        world = WorldFactory.with_marshals([ney])
        world.current_turn = 3
        world.event_log = [{
            "type": "battle", "location": "Waterloo",
            "attacker": "Blucher", "attacker_nation": "Prussia",
            "defender": "Davout", "defender_nation": "France",
            "outcome": "stalemate", "turn": 3,
        }]
        assert emit_literal_fidelity_events(world) == []

    def test_absent_when_nothing_changed(self):
        soult = _literal(location="Belgium")
        self._held_order(soult, "Belgium")
        world = WorldFactory.with_marshals([soult])
        world.event_log = []
        assert emit_literal_fidelity_events(world) == []

    def test_absent_without_an_active_order(self):
        soult = _literal(location="Belgium")
        world = WorldFactory.with_marshals([soult])
        world.current_turn = 3
        world.event_log = [{
            "type": "battle", "location": "Waterloo",
            "attacker": "Blucher", "attacker_nation": "Prussia",
            "defender": "Ney", "defender_nation": "France",
            "outcome": "stalemate", "turn": 3,
        }]
        assert emit_literal_fidelity_events(world) == []

    def test_quarry_moved_beat(self):
        soult = _literal(location="Paris")
        soult.strategic_order = StrategicOrder(
            command_type="PURSUE", target="Mack", target_type="marshal",
            started_turn=1, original_command="Soult, pursue Mack",
            target_snapshot_location="Belgium")
        mack = MarshalFactory.enemy(name="Mack", location="Rhineland",
                                    nation="Austria")
        world = WorldFactory.with_marshals([soult, mack])
        world.event_log = []
        events = emit_literal_fidelity_events(world)
        assert len(events) == 1
        assert "quarry has shifted to Rhineland" in events[0]["message"]

    def test_cap_one_per_marshal_per_turn(self):
        soult = _literal(location="Belgium")
        self._held_order(soult, "Belgium")
        world = WorldFactory.with_marshals([soult])
        world.current_turn = 3
        world.event_log = [
            {"type": "battle", "location": "Waterloo",
             "attacker": "Blucher", "attacker_nation": "Prussia",
             "defender": "Ney", "defender_nation": "France",
             "outcome": "stalemate", "turn": 3},
            {"type": "battle", "location": "Rhineland",
             "attacker": "Mack", "attacker_nation": "Austria",
             "defender": "Davout", "defender_nation": "France",
             "outcome": "stalemate", "turn": 3},
        ]
        events = emit_literal_fidelity_events(world)
        assert len(events) == 1

    def test_renders_in_campaign_log_and_dispatch(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, format_event_oneliner
        from backend.game_logic.dispatch import _build_turn_events
        assert "literal_fidelity" in CAMPAIGN_LOG_TYPES
        event = {
            "type": "literal_fidelity", "marshal": "Soult",
            "nation": "France", "location": "Belgium",
            "order_type": "HOLD",
            "message": ("Soult holds at Belgium, per your orders — the "
                        "guns at Waterloo did not move him."),
        }
        line = format_event_oneliner(event)
        assert "did not move him" in line
        entries = _build_turn_events([event], "France")
        assert len(entries) == 1
        assert "per your orders" in entries[0]["message"]


# ════════════════════════════════════════════════════════════════════════
# §7.2.3 Doctrine tells + §7.3 voice-bank hygiene
# ════════════════════════════════════════════════════════════════════════

class TestDoctrineTells:
    def test_marshal_card_carries_the_doctrine(self):
        from backend.game_logic.marshal_overview import build_marshal_overview
        soult = _literal(location="Paris")
        world = WorldFactory.with_marshals([soult])
        overview = build_marshal_overview(world)
        cards = overview if isinstance(overview, list) else overview["marshals"]
        card = next(c for c in cards if c["name"] == "Soult")
        assert "to the letter" in card["personality_description"]

    def test_dispatch_note_appends_to_the_letter(self):
        from backend.game_logic.dispatch import _derive_marshal_status
        soult = _literal(location="Belgium")
        soult.strategic_order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="Soult, hold Belgium")
        world = WorldFactory.with_marshals([soult])
        status, note = _derive_marshal_status(soult, world)
        assert "(to the letter)" in note

    def test_non_literal_note_has_no_letter_tag(self):
        from backend.game_logic.dispatch import _derive_marshal_status
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      personality="aggressive")
        ney.strategic_order = StrategicOrder(
            command_type="HOLD", target="Belgium", target_type="region",
            started_turn=1, original_command="Ney, hold Belgium")
        world = WorldFactory.with_marshals([ney])
        status, note = _derive_marshal_status(ney, world)
        assert "(to the letter)" not in note

    def test_voice_banks_have_variants(self):
        """Anti-rote: >=2 variants per beat, rotation actually rotates."""
        for bank in (LITERAL_ACK, LITERAL_COMPLETE, LITERAL_NO_MARCH):
            assert len(bank) >= 2
        lines = {literal_ack("march to Swabia", t) for t in range(3)}
        assert len(lines) >= 2
        completions = {literal_completion("march to Swabia", "Done.", "Soult", t)
                       for t in range(3)}
        assert len(completions) >= 2

    def test_no_march_bank_keeps_the_shipped_line(self):
        assert literal_no_march("Soult", 0) == (
            "Soult continues to follow standing orders. "
            "The sound of cannon fire grows louder behind him."
        )


# ════════════════════════════════════════════════════════════════════════
# Doctrine ≠ uselessness: a literal marshal WITH the written word marches
# ════════════════════════════════════════════════════════════════════════

class TestLiteralWithOrdersStillFights:
    def test_literal_with_support_order_reinforces(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000,
                                      personality="aggressive")
        soult = _literal(location="Paris")
        soult.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="Soult, support Ney")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=30000)
        world = WorldFactory.with_marshals([ney, soult, mack])
        _war(world)
        executor = CommandExecutor()
        results = executor._combat._calculate_reinforcements(
            ney, mack, "Belgium", "France", world)
        soult_result = next(r for r in results if r["marshal"] == "Soult")
        # Not blocked by the Grouchy Rule — he holds the written word.
        assert soult_result["reason"] != "literal_personality"
        assert soult_result["has_explicit_order"] is True
