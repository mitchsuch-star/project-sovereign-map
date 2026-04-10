"""
Session 1 Bug Fixes — Regression Tests
Created: April 10, 2026

Covers:
- PL-30: Deferred proposal result survives popup masking, preview distinguishes
         blocking dialogue from deferred result, wizard gets has_deferred_result
- PL-31: Capital-loss defeat removed, regression test targets correct region key
"""
import pytest
from starlette.testclient import TestClient
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.turn_manager import TurnManager
from backend.game_logic.diplomacy import (
    get_diplomatic_preview,
    get_available_diplomatic_actions,
)


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def client():
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def fresh_world():
    import backend.main as main_module
    main_module.world = WorldState()
    main_module.game_state = {"world": main_module.world}
    return main_module.world


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    world = WorldState()
    world.current_turn = 5
    return world


# ═══════════════════════════════════════════════════════════════════════════
# PL-31: Capital-loss defeat removed
# ═══════════════════════════════════════════════════════════════════════════

class TestPL31CapitalLossNotDefeat:
    """PL-31: Capital loss alone must not end the campaign."""

    def test_capital_loss_with_armies_continues(self):
        """Losing Paris while having armies and other territory → game continues."""
        world = _make_world()
        paris = world.regions.get("Paris")
        assert paris is not None, "Region key must be 'Paris'"
        paris.controller = "Prussia"

        # Ensure player has surviving armies
        ney = world.marshals.get("Ney")
        assert ney is not None
        ney.strength = 15000

        tm = TurnManager(world, CommandExecutor())
        result = tm._check_victory_conditions()
        assert result["game_over"] is False

    def test_zero_armies_still_defeats(self):
        """All armies destroyed → defeat (unchanged)."""
        world = _make_world()
        for m in world.get_player_marshals():
            m.strength = 0

        tm = TurnManager(world, CommandExecutor())
        result = tm._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "defeat"
        assert "destroyed" in result["reason"].lower()

    def test_zero_regions_still_defeats(self):
        """All territory lost → defeat (unchanged)."""
        world = _make_world()
        for region in world.regions.values():
            region.controller = "Prussia"
        # Need a living marshal so we don't trigger the armies-destroyed path first
        ney = world.marshals.get("Ney")
        if ney:
            ney.strength = 10000

        tm = TurnManager(world, CommandExecutor())
        result = tm._check_victory_conditions()
        assert result["game_over"] is True
        assert result["result"] == "defeat"
        assert "territory" in result["reason"].lower()

    def test_capital_loss_reason_never_fires(self):
        """No victory-condition result should ever mention 'capital has fallen'."""
        world = _make_world()
        paris = world.regions.get("Paris")
        paris.controller = "Prussia"
        ney = world.marshals.get("Ney")
        ney.strength = 15000

        tm = TurnManager(world, CommandExecutor())
        result = tm._check_victory_conditions()
        reason = (result.get("reason") or "").lower()
        assert "capital" not in reason


# ═══════════════════════════════════════════════════════════════════════════
# PL-30: Deferred proposal result — popup queue behavior
# ═══════════════════════════════════════════════════════════════════════════

class TestPL30DeferredResultSurvivesMasking:
    """PL-30: A proposal_result_popup must survive being masked by a
    higher-priority popup and remain recoverable on the next cycle."""

    def test_proposal_result_masked_by_higher_priority(self):
        """When a higher-priority popup wins, proposal_result stays in queue."""
        world = _make_world()
        # Set a lower-priority proposal result
        world.proposal_result_popup = {
            "result": "accepted",
            "from_nation": "Austria",
            "summary": "Alliance accepted",
        }
        # Set a higher-priority coalition popup
        world.coalition_popup = {
            "coalition_name": "Third Coalition",
            "message": "Coalition declared!",
        }

        # Pop highest — coalition should win
        winner_attr, winner_key, winner_value = world._popup_queue.pop_highest()
        assert winner_key == "coalition_popup"
        assert winner_value["coalition_name"] == "Third Coalition"

        # Proposal result must still be in the queue
        assert world.proposal_result_popup is not None
        assert world.proposal_result_popup["result"] == "accepted"

    def test_proposal_result_delivered_after_masking(self):
        """On the next cycle after masking, proposal_result is delivered."""
        world = _make_world()
        world.proposal_result_popup = {
            "result": "rejected",
            "from_nation": "Prussia",
        }
        world.coalition_popup = {"message": "Coalition!"}

        # First cycle — coalition wins
        world._popup_queue.pop_highest()

        # Second cycle — proposal result should win
        winner_attr, winner_key, winner_value = world._popup_queue.pop_highest()
        assert winner_key == "proposal_result"
        assert winner_value["result"] == "rejected"

        # Queue should now be empty
        assert not world._popup_queue.has_pending()


# ═══════════════════════════════════════════════════════════════════════════
# PL-30: Preview contract — has_deferred_result
# ═══════════════════════════════════════════════════════════════════════════

class TestPL30PreviewDeferredResult:
    """PL-30: /diplomatic_preview must return has_deferred_result flag
    so the wizard can distinguish blocking dialogue from deferred result."""

    def test_preview_no_deferred_no_dialogue(self):
        """Normal state: both flags false."""
        world = _make_world()
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["dialogue_pending"] is False
        assert preview["has_deferred_result"] is False

    def test_preview_deferred_result_only(self):
        """Deferred result pending, no blocking dialogue."""
        world = _make_world()
        world.proposal_result_popup = {"result": "accepted", "from_nation": "Austria"}
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["dialogue_pending"] is False
        assert preview["has_deferred_result"] is True

    def test_preview_blocking_dialogue_only(self):
        """Blocking dialogue pending, no deferred result."""
        world = _make_world()
        world.dialogue_manager.push({
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "blocking": True,
            "context": {},
        })
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["dialogue_pending"] is True
        assert preview["has_deferred_result"] is False

    def test_preview_both_deferred_and_dialogue(self):
        """Both deferred result and blocking dialogue."""
        world = _make_world()
        world.proposal_result_popup = {"result": "accepted", "from_nation": "Austria"}
        world.dialogue_manager.push({
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "blocking": True,
            "context": {},
        })
        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["dialogue_pending"] is True
        assert preview["has_deferred_result"] is True

    def test_actions_blocked_by_dialogue_not_by_deferred_result(self):
        """Actions should be blocked by pending dialogue, not by deferred result alone."""
        world = _make_world()
        # Deferred result only — actions should still be available
        world.proposal_result_popup = {"result": "accepted", "from_nation": "Austria"}
        actions = get_available_diplomatic_actions(world, "Prussia")
        assert len(actions) > 0, "Deferred result alone should not block actions"

    def test_actions_blocked_by_pending_dialogue(self):
        """Pending dialogue should block all diplomatic actions."""
        world = _make_world()
        world.dialogue_manager.push({
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "blocking": True,
            "context": {},
        })
        actions = get_available_diplomatic_actions(world, "Prussia")
        assert len(actions) == 0, "Pending dialogue should block actions"


# ═══════════════════════════════════════════════════════════════════════════
# PL-30: Full response builder — proposal_result passthrough
# ═══════════════════════════════════════════════════════════════════════════

class TestPL30ResponseBuilderPassthrough:
    """PL-30: build_base_response must include popup passthroughs correctly."""

    def test_proposal_result_in_base_response_when_highest(self):
        """When proposal_result is the highest-priority popup, it's delivered."""
        from backend.main import build_base_response
        world = _make_world()
        world.proposal_result_popup = {
            "result": "accepted",
            "from_nation": "Austria",
        }
        response = build_base_response(world)
        assert response.get("proposal_result") is not None
        assert response["proposal_result"]["result"] == "accepted"

    def test_proposal_result_masked_in_base_response(self):
        """When a higher popup masks proposal_result, it stays for next cycle."""
        from backend.main import build_base_response
        world = _make_world()
        world.proposal_result_popup = {"result": "accepted", "from_nation": "Austria"}
        world.coalition_popup = {"message": "Coalition declared!"}

        response = build_base_response(world)
        # Coalition won
        assert response.get("coalition_popup") is not None
        # Proposal result was masked (None in response)
        assert response.get("proposal_result") is None
        # But it's still in the queue for next cycle
        assert world.proposal_result_popup is not None


# ═══════════════════════════════════════════════════════════════════════════
# PL-30: /diplomatic_preview endpoint shape
# ═══════════════════════════════════════════════════════════════════════════

class TestPL30PreviewEndpoint:
    """PL-30: /diplomatic_preview endpoint returns has_deferred_result."""

    def test_step1_includes_has_deferred_result(self, client, fresh_world):
        """Step 1 (no nation) response includes has_deferred_result."""
        response = client.get("/diplomatic_preview").json()
        assert "has_deferred_result" in response
        assert response["has_deferred_result"] is False

    def test_step1_deferred_result_true(self, client, fresh_world):
        """Step 1 shows has_deferred_result=true when result is deferred."""
        fresh_world.proposal_result_popup = {"result": "accepted", "from_nation": "Austria"}
        response = client.get("/diplomatic_preview").json()
        assert response["has_deferred_result"] is True

    def test_step2_includes_has_deferred_result(self, client, fresh_world):
        """Step 2 (with nation) response includes has_deferred_result."""
        response = client.get("/diplomatic_preview?nation=Prussia").json()
        assert "has_deferred_result" in response
        assert response["has_deferred_result"] is False
