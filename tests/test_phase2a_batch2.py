"""Phase 2A Batch 2 tests: War-to-Peace Transition Cleanup.

R1a: Prune battle_records older than 10 turns
R1b: Clear war data on war end (cleanup_war_end)
R49: Reset war_exhaustion on war end
R47/R30: Cancel strategic orders targeting peaceful nation
R45: Delete active treaties on downgrade
"""
from backend.models.world_state import WorldState
from backend.models.marshal import StrategicOrder
from backend.game_logic.diplomacy import (
    apply_war_score_decay,
    cleanup_war_end,
    execute_downgrade,
)


def make_world():
    return WorldState()


# ═══════════════════════════════════════════════════════
# R1a: Prune old battle records
# ═══════════════════════════════════════════════════════

class TestBattleRecordPruning:
    """R1a: Battle records older than 10 turns pruned during decay."""

    def test_old_records_pruned(self):
        world = make_world()
        world.current_turn = 15
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 10
        world.battle_records[key] = [
            {"turn": 2, "winner": "France"},   # 13 turns old → prune
            {"turn": 12, "winner": "Prussia"},  # 3 turns old → keep
        ]
        apply_war_score_decay(world)
        assert len(world.battle_records[key]) == 1
        assert world.battle_records[key][0]["turn"] == 12

    def test_recent_records_kept(self):
        world = make_world()
        world.current_turn = 8
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 5
        world.battle_records[key] = [
            {"turn": 5, "winner": "France"},  # 3 turns old → keep
            {"turn": 7, "winner": "France"},  # 1 turn old → keep
        ]
        apply_war_score_decay(world)
        assert len(world.battle_records[key]) == 2

    def test_all_old_records_pruned(self):
        world = make_world()
        world.current_turn = 20
        key = world._make_diplo_key("France", "Austria")
        world.war_scores[key] = 10
        world.battle_records[key] = [
            {"turn": 1, "winner": "France"},
            {"turn": 5, "winner": "Austria"},
        ]
        apply_war_score_decay(world)
        assert len(world.battle_records[key]) == 0


# ═══════════════════════════════════════════════════════
# R1b + R49: cleanup_war_end
# ═══════════════════════════════════════════════════════

class TestCleanupWarEnd:
    """R1b: Clear battle_records, decisive_battles, war_scores on war end.
    R49: Reset war_exhaustion."""

    def test_clears_battle_records(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.battle_records[key] = [{"turn": 1, "winner": "France"}]
        cleanup_war_end(world, key)
        assert key not in world.battle_records

    def test_clears_decisive_battles(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.decisive_battles[key] = [{"turn": 1, "winner": "France"}]
        cleanup_war_end(world, key)
        assert key not in world.decisive_battles

    def test_clears_war_scores(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 50
        cleanup_war_end(world, key)
        assert key not in world.war_scores

    def test_resets_war_exhaustion(self):
        world = make_world()
        world.war_exhaustion = {"France": 30, "Prussia": 20, "Austria": 10}
        key = world._make_diplo_key("France", "Prussia")
        cleanup_war_end(world, key)
        assert world.war_exhaustion.get("France") is None
        assert world.war_exhaustion.get("Prussia") is None
        assert world.war_exhaustion.get("Austria") == 10  # Unrelated, kept


# ═══════════════════════════════════════════════════════
# R47/R30: Cancel strategic orders on peace
# ═══════════════════════════════════════════════════════

class TestCancelOrdersOnPeace:
    """R47/R30: PURSUE/MOVE_TO orders targeting the peaceful nation's marshals are cancelled."""

    def test_pursue_order_cancelled(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        # Find a French marshal and give it a PURSUE order targeting a Prussian marshal
        french_marshal = None
        prussian_marshal = None
        for m in world.marshals.values():
            if m.nation == "France" and not french_marshal:
                french_marshal = m
            if m.nation == "Prussia" and not prussian_marshal:
                prussian_marshal = m
        if french_marshal and prussian_marshal:
            french_marshal.strategic_order = StrategicOrder(
                command_type="PURSUE", target=prussian_marshal.name,
                target_type="marshal", started_turn=1,
                original_command="pursue test",
            )
            cleanup_war_end(world, key)
            assert french_marshal.strategic_order is None

    def test_move_to_region_not_cancelled(self):
        """MOVE_TO orders targeting a region (not marshal) should NOT be cancelled."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        french_marshal = next(m for m in world.marshals.values() if m.nation == "France")
        french_marshal.strategic_order = StrategicOrder(
            command_type="MOVE_TO", target="Saxony",
            target_type="region", started_turn=1,
            original_command="move to Saxony",
        )
        cleanup_war_end(world, key)
        # Region-targeted orders should be kept
        assert french_marshal.strategic_order is not None

    def test_unrelated_orders_kept(self):
        """Orders targeting nations NOT in the peace treaty should be kept."""
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        french_marshal = next(m for m in world.marshals.values() if m.nation == "France")
        # Target a British marshal (not part of France-Prussia peace)
        british_marshal = next((m for m in world.marshals.values() if m.nation == "Britain"), None)
        if british_marshal:
            french_marshal.strategic_order = StrategicOrder(
                command_type="PURSUE", target=british_marshal.name,
                target_type="marshal", started_turn=1,
                original_command="pursue test",
            )
            cleanup_war_end(world, key)
            assert french_marshal.strategic_order is not None


# ═══════════════════════════════════════════════════════
# R45: Delete active treaties on downgrade
# ═══════════════════════════════════════════════════════

class TestDeleteTreatyOnDowngrade:
    """R45: active_treaties entry removed on downgrade."""

    def test_treaty_deleted_on_downgrade(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        world.active_treaties[key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
            "turn_signed": 1,
            "harshness": 0,
        }
        execute_downgrade(world, "France", "Austria")
        assert key not in world.active_treaties

    def test_downgrade_still_works(self):
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "ALLIANCE"
        result = execute_downgrade(world, "France", "Austria")
        assert result["success"] is True
        assert result["new_state"] == "DEFENSIVE_ALLIANCE"


# ═══════════════════════════════════════════════════════
# Integration: cleanup_war_end wired in _ratify_treaty
# ═══════════════════════════════════════════════════════

class TestRatifyTreatyCleanup:
    """Verify cleanup_war_end fires on treaty ratification for WAR→PEACE."""

    def test_war_data_cleared_on_peace_treaty(self):
        world = make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 40
        world.battle_records[key] = [{"turn": 1, "winner": "France"}]
        world.war_exhaustion["France"] = 20
        world.war_exhaustion["Prussia"] = 15

        world._ratify_treaty("Prussia", {
            "type": "peace",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        })

        assert key not in world.war_scores
        assert key not in world.battle_records
        assert world.war_exhaustion.get("France") is None
        assert world.war_exhaustion.get("Prussia") is None
