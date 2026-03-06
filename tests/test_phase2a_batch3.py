"""Phase 2A Batch 3 tests: Armistice System + Treaty Gold Floor.

R5a: Armistice expiration after 5 turns
R5b: Armistice cooldown on entry + blocks proposals
R3: Gold floor in treaty clause processing
"""
from backend.models.world_state import WorldState
from backend.game_logic.diplomacy import _process_armistice_expiration


def make_world():
    return WorldState()


# ═══════════════════════════════════════════════════════
# R5a: Armistice expiration
# ═══════════════════════════════════════════════════════

class TestArmisticeExpiration:
    """R5a: Armistice expires after 5 turns, transitions to PEACE or WAR."""

    def test_armistice_increments_counter(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        _process_armistice_expiration(world)
        assert world.armistice_turns[key] == 1

    def test_armistice_expires_to_peace_after_5_turns(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.nation_relations[key] = 0  # Above -60 threshold
        world.armistice_turns[key] = 4  # Will become 5 on processing
        events = _process_armistice_expiration(world)
        assert world.diplomatic_states[key] == "PEACE"
        assert len(events) == 1
        assert events[0]["type"] == "armistice_expired_peace"

    def test_armistice_expires_to_war_when_hostile(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.nation_relations[key] = -80  # Below -60 threshold
        world.armistice_turns[key] = 4
        events = _process_armistice_expiration(world)
        assert world.diplomatic_states[key] == "WAR"
        assert len(events) == 1
        assert events[0]["type"] == "armistice_expired_war"

    def test_armistice_not_expired_before_5_turns(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.armistice_turns[key] = 2
        events = _process_armistice_expiration(world)
        assert world.diplomatic_states[key] == "ARMISTICE"
        assert len(events) == 0
        assert world.armistice_turns[key] == 3

    def test_tracking_cleared_when_not_armistice(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "PEACE"
        world.armistice_turns[key] = 3
        _process_armistice_expiration(world)
        assert key not in world.armistice_turns

    def test_tracking_cleared_after_expiration(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.nation_relations[key] = 0
        world.armistice_turns[key] = 4
        _process_armistice_expiration(world)
        assert key not in world.armistice_turns

    def test_peace_transition_calls_cleanup(self):
        """War data should be cleared when armistice expires to peace."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "ARMISTICE"
        world.nation_relations[key] = 0
        world.armistice_turns[key] = 4
        world.war_scores[key] = 30
        world.battle_records[key] = [{"turn": 1, "winner": "France"}]
        _process_armistice_expiration(world)
        assert key not in world.war_scores
        assert key not in world.battle_records


# ═══════════════════════════════════════════════════════
# R5b: Armistice cooldown
# ═══════════════════════════════════════════════════════

class TestArmisticeCooldown:
    """R5b: Armistice cooldown set on entry, blocks proposals."""

    def test_cooldown_set_on_armistice_treaty(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world._ratify_treaty({
            "type": "armistice_losing",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        })
        assert world.armistice_cooldowns.get(key) == 5

    def test_ai_proposal_blocked_by_cooldown(self):
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.armistice_cooldowns[key] = 3
        # Prussia should not propose while on cooldown
        result = process_diplomatic_phase("Prussia", world)
        assert result is None


# ═══════════════════════════════════════════════════════
# R5a/R5b: Serialization
# ═══════════════════════════════════════════════════════

class TestArmisticeSerialization:
    """armistice_turns field round-trips correctly."""

    def test_armistice_turns_in_to_dict(self):
        world = make_world()
        world.armistice_turns = {"Austria|France": 3}
        data = world.to_dict()
        assert data["armistice_turns"] == {"Austria|France": 3}

    def test_armistice_turns_from_dict(self):
        world = make_world()
        world.armistice_turns = {"Austria|France": 3}
        data = world.to_dict()
        world2 = WorldState.from_dict(data)
        assert world2.armistice_turns == {"Austria|France": 3}

    def test_armistice_turns_default_empty(self):
        data = make_world().to_dict()
        del data["armistice_turns"]
        world2 = WorldState.from_dict(data)
        assert world2.armistice_turns == {}


# ═══════════════════════════════════════════════════════
# R3: Gold floor in treaty clauses
# ═══════════════════════════════════════════════════════

class TestGoldFloor:
    """R3: Gold transfer capped at available gold, never goes negative."""

    def test_gold_transfer_capped_at_available(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[key] = {
            "clauses": [{
                "type": "gold_per_turn",
                "from": "France",
                "to": "Prussia",
                "amount": 5000,  # Way more than France has
            }],
        }
        france_gold = world.nation_gold["France"]
        prussia_gold = world.nation_gold["Prussia"]
        world._process_treaty_clauses()
        assert world.nation_gold["France"] == 0  # Never negative
        assert world.nation_gold["Prussia"] == prussia_gold + france_gold

    def test_gold_never_negative(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.nation_gold["France"] = 0
        world.active_treaties[key] = {
            "clauses": [{
                "type": "gold_per_turn",
                "from": "France",
                "to": "Austria",
                "amount": 100,
            }],
        }
        austria_gold = world.nation_gold["Austria"]
        world._process_treaty_clauses()
        assert world.nation_gold["France"] == 0
        assert world.nation_gold["Austria"] == austria_gold  # No transfer

    def test_dispatch_event_on_failed_payment(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.nation_gold["France"] = 50
        world.active_treaties[key] = {
            "clauses": [{
                "type": "gold_per_turn",
                "from": "France",
                "to": "Austria",
                "amount": 100,
            }],
        }
        world._process_treaty_clauses()
        # Should have queued a dispatch event
        assert len(world.pending_dispatch_events) > 0
        event = world.pending_dispatch_events[-1]
        assert event["type"] == "diplomatic_treaty_payment_failed"

    def test_normal_transfer_no_dispatch_event(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.nation_gold["France"] = 5000
        events_before = len(world.pending_dispatch_events)
        world.active_treaties[key] = {
            "clauses": [{
                "type": "gold_per_turn",
                "from": "France",
                "to": "Austria",
                "amount": 100,
            }],
        }
        world._process_treaty_clauses()
        assert len(world.pending_dispatch_events) == events_before
