"""B-B3 regression tests for the alliance_paradox → commitment_paradox rename.

Spec: docs/RELIABILITY_IMPLEMENTATION_PLAN.md §B-B3.

Three focused regressions:
  1. Rename smoke — declare_war's paradox path emits the canonical type
     and popup field only; the legacy strings must not appear in the
     live dialogue or popup slot.
  2. Alias load gate — saves written with the legacy keys still load:
     WorldState.alliance_paradox_popup migrates to commitment_paradox_popup
     and DialogueManager items with type="alliance_paradox" retain
     hard-stop priority on replay.
  3. No double-emit — a single paradox fires exactly one dialogue and
     one popup slot, with no stray alliance_paradox_popup key serialized
     back out.
"""
from backend.game_logic.diplomacy import declare_war, set_diplomatic_state
from backend.models.dialogue_manager import DialogueManager
from backend.models.world_state import WorldState


def _paradox_world():
    """Build a world where declaring war triggers the alliance paradox.

    France (player) is allied with both Britain (aggressor) and Prussia
    (target); Britain declaring war on Prussia forces the paradox.
    """
    world = WorldState(player_nation="France")
    set_diplomatic_state(world, "France", "Britain", "ALLIANCE", "test_setup")
    set_diplomatic_state(world, "France", "Prussia", "ALLIANCE", "test_setup")
    set_diplomatic_state(world, "Britain", "Prussia", "PEACE", "test_setup")
    return world


# ─── 1. Rename smoke ─────────────────────────────────────────────────────

class TestCommitmentParadoxRenameSmoke:

    def test_declare_war_paradox_emits_canonical_popup(self):
        world = _paradox_world()

        result = declare_war(world, "Britain", "Prussia")

        assert result["success"] is True
        assert world.commitment_paradox_popup is not None
        assert world.commitment_paradox_popup["attacker"] == "Britain"
        assert world.commitment_paradox_popup["defender"] == "Prussia"
        assert world.commitment_paradox_popup["ally"] == "France"

    def test_declare_war_paradox_pushes_canonical_dialogue_type(self):
        world = _paradox_world()

        declare_war(world, "Britain", "Prussia")

        current = world.dialogue_manager.peek()
        assert current is not None
        assert current["type"] == "commitment_paradox"
        assert current["type"] != "alliance_paradox"
        assert world.dialogue_manager.is_hard_stop() is True

    def test_paradox_dialogue_carries_origin_episode_id(self):
        """§6.5 paradox episode_id threads through the dialogue for C3 replay."""
        world = _paradox_world()

        declare_war(world, "Britain", "Prussia")

        current = world.dialogue_manager.peek()
        assert current["origin_episode_id"] is not None
        assert current["episode_id"] == current["origin_episode_id"]


# ─── 2. Alias load gate ──────────────────────────────────────────────────

class TestCommitmentParadoxAliasLoad:

    def test_legacy_world_save_key_migrates_on_load(self):
        """Saves written when the popup field was alliance_paradox_popup
        must still deserialize; canonical key should win over legacy."""
        world = WorldState(player_nation="France")
        base = world.to_dict()

        legacy = dict(base)
        legacy.pop("commitment_paradox_popup", None)
        legacy["alliance_paradox_popup"] = {"attacker": "Russia", "defender": "Austria"}

        restored = WorldState.from_dict(legacy)

        assert restored.commitment_paradox_popup == {
            "attacker": "Russia",
            "defender": "Austria",
        }
        assert restored.alliance_paradox_popup == restored.commitment_paradox_popup

    def test_canonical_key_wins_when_both_present(self):
        world = WorldState(player_nation="France")
        base = world.to_dict()

        both = dict(base)
        both["commitment_paradox_popup"] = {"attacker": "Britain", "defender": "Prussia"}
        both["alliance_paradox_popup"] = {"attacker": "LEGACY", "defender": "LEGACY"}

        restored = WorldState.from_dict(both)

        assert restored.commitment_paradox_popup["attacker"] == "Britain"

    def test_legacy_dialogue_type_still_hard_stops(self):
        """Old saves with type='alliance_paradox' in the dialogue manager
        must remain hard-stop on replay (read-side alias)."""
        legacy = {
            "type": "alliance_paradox",
            "blocking": True,
            "turn_created": 1,
        }
        restored = DialogueManager.from_dict({"current": legacy, "queue": []})

        assert restored.peek()["type"] == "alliance_paradox"  # read-side alias
        assert restored.is_hard_stop() is True
        assert DialogueManager.DIALOGUE_PRIORITY["alliance_paradox"] == 0
        assert DialogueManager.DIALOGUE_PRIORITY["commitment_paradox"] == 0
        assert "alliance_paradox" in DialogueManager.HARD_STOP_TYPES
        assert "commitment_paradox" in DialogueManager.HARD_STOP_TYPES


# ─── 3. No double-emit ───────────────────────────────────────────────────

class TestCommitmentParadoxNoDoubleEmit:

    def test_paradox_pushes_exactly_one_dialogue(self):
        world = _paradox_world()

        declare_war(world, "Britain", "Prussia")

        assert world.dialogue_manager.peek() is not None
        assert world.dialogue_manager.queue_size == 0

    def test_paradox_fills_only_canonical_popup_slot(self):
        world = _paradox_world()

        declare_war(world, "Britain", "Prussia")

        data = world.to_dict()
        assert data["commitment_paradox_popup"] is not None
        # Legacy key must not round-trip out of to_dict — canonical only.
        assert "alliance_paradox_popup" not in data

    def test_paradox_round_trip_preserves_single_active_dialogue(self):
        world = _paradox_world()
        declare_war(world, "Britain", "Prussia")

        restored = WorldState.from_dict(world.to_dict())

        current = restored.dialogue_manager.peek()
        assert current is not None
        assert current["type"] == "commitment_paradox"
        assert restored.dialogue_manager.queue_size == 0
        assert restored.commitment_paradox_popup is not None
