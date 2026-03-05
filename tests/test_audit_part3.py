"""
Diplomacy Audit Part 3 — AI Proposal Spam Fixes
Created: March 4, 2026

Bugs fixed:
- SPAM-1: No acceptance cooldown — nation proposes again immediately after acceptance
- SPAM-2: No pending-proposal deduplication — same nation generates proposals while one pending
- SPAM-3: P7 opportunistic proposes NON_AGGRESSION regardless of current diplomatic state
"""
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.ai_diplomacy import (
    process_diplomatic_phase,
    apply_acceptance_cooldown,
    _has_pending_proposal_from,
    _get_queue,
    deliver_ai_proposal,
    NATION_ACCEPTANCE_COOLDOWN,
)


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a test world with standard 5-nation setup."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_game_state(world=None):
    if world is None:
        world = _make_world()
    return {"world": world}


def _make_executor():
    return CommandExecutor()


def _set_diplo_state(world, nation_a, nation_b, state):
    """Set diplomatic state between two nations."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def _set_relation(world, nation_a, nation_b, value):
    """Set nation relation."""
    key = world._make_diplo_key(nation_a, nation_b)
    world.nation_relations[key] = value


def _set_at_war(world, nation_a, nation_b):
    """Set two nations to WAR state."""
    _set_diplo_state(world, nation_a, nation_b, "WAR")


# ═══════════════════════════════════════════════════════════════════════════
# SPAM-1: ACCEPTANCE COOLDOWN
# ═══════════════════════════════════════════════════════════════════════════

class TestAcceptanceCooldown:
    """After accepting a proposal, the nation should be on cooldown."""

    def test_apply_acceptance_cooldown_sets_nation_cooldown(self):
        """apply_acceptance_cooldown sets a nation-level cooldown."""
        world = _make_world()
        apply_acceptance_cooldown("Saxony", world)
        cooldowns = world.ai_proposal_cooldowns
        assert cooldowns.get("Saxony|nation") == NATION_ACCEPTANCE_COOLDOWN

    def test_acceptance_cooldown_shorter_than_rejection(self):
        """Acceptance cooldown is shorter than rejection cooldown."""
        from backend.game_logic.ai_diplomacy import NATION_REJECTION_COOLDOWN
        assert NATION_ACCEPTANCE_COOLDOWN < NATION_REJECTION_COOLDOWN

    def test_acceptance_cooldown_blocks_next_turn_proposal(self):
        """Nation can't propose the turn after acceptance due to cooldown."""
        world = _make_world()
        # Saxony at PEACE with France, relation > 30 → P4 would fire
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 40)

        # Apply acceptance cooldown (simulating what happens after accept)
        apply_acceptance_cooldown("Saxony", world)

        # Next turn, Saxony should NOT generate a proposal
        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is None

    def test_acceptance_cooldown_expires_and_allows_proposal(self):
        """After cooldown expires, nation can propose again."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 40)

        # Apply acceptance cooldown
        apply_acceptance_cooldown("Saxony", world)

        # Decrement cooldown N times (simulating N turns)
        for _ in range(NATION_ACCEPTANCE_COOLDOWN):
            world._decrement_ai_proposal_cooldowns()

        # Now Saxony SHOULD be able to propose
        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is not None

    def test_executor_accept_applies_cooldown(self):
        """Accepting via executor sets acceptance cooldown on world."""
        world = _make_world()
        executor = _make_executor()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 40)

        # Deliver a proposal from Saxony
        proposal = {
            "source": "Saxony",
            "proposal_type": "open_borders",
            "priority": 4,
            "terms": {
                "type": "open_borders",
                "proposer_nation": "Saxony",
                "target_nation": "France",
                "sweeteners": [],
                "demands": [],
                "clauses": ["open_borders"],
            },
            "talleyrand_assessment": "Test",
            "turn_generated": 5,
        }
        deliver_ai_proposal(proposal, world)

        # Accept via handle_diplomatic_dialogue_response (same path as main.py)
        game_state = _make_game_state(world)
        result = executor.handle_diplomatic_dialogue_response("accept", game_state)
        assert result["success"] is True
        # After acceptance, cooldown should be set
        assert world.ai_proposal_cooldowns.get("Saxony|nation", 0) > 0


# ═══════════════════════════════════════════════════════════════════════════
# SPAM-2: PENDING PROPOSAL DEDUPLICATION
# ═══════════════════════════════════════════════════════════════════════════

class TestPendingProposalDedup:
    """Don't generate proposals if one is already pending from same nation."""

    def test_has_pending_from_active_dialogue(self):
        """_has_pending_proposal_from detects proposal in active dialogue."""
        world = _make_world()
        world.pending_diplomatic_dialogue = {
            "type": "incoming_proposal",
            "blocking": True,
            "context": {"source_nation": "Saxony"},
        }
        assert _has_pending_proposal_from("Saxony", world) is True
        assert _has_pending_proposal_from("Prussia", world) is False

    def test_has_pending_from_queue(self):
        """_has_pending_proposal_from detects proposal in queue."""
        world = _make_world()
        world.diplomatic_queue = [
            {"source": "Austria", "priority": 4, "turn_generated": 5}
        ]
        assert _has_pending_proposal_from("Austria", world) is True
        assert _has_pending_proposal_from("Prussia", world) is False

    def test_has_pending_from_empty(self):
        """_has_pending_proposal_from returns False when nothing pending."""
        world = _make_world()
        assert _has_pending_proposal_from("Saxony", world) is False

    def test_dedup_blocks_proposal_when_dialogue_pending(self):
        """Nation with proposal in active dialogue doesn't generate another."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 40)

        # Set up a pending dialogue from Saxony
        world.pending_diplomatic_dialogue = {
            "type": "incoming_proposal",
            "blocking": True,
            "context": {"source_nation": "Saxony"},
        }

        # Saxony should NOT generate a new proposal
        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is None

    def test_dedup_blocks_proposal_when_queued(self):
        """Nation with proposal in queue doesn't generate another."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 40)

        # Set up a queued proposal from Saxony
        world.diplomatic_queue = [
            {"source": "Saxony", "priority": 4, "turn_generated": 5}
        ]

        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is None

    def test_dedup_allows_different_nation(self):
        """Another nation can still propose even if one nation has pending."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 40)
        _set_diplo_state(world, "France", "Austria", "PEACE")
        _set_relation(world, "France", "Austria", 40)

        # Saxony has pending dialogue
        world.pending_diplomatic_dialogue = {
            "type": "incoming_proposal",
            "blocking": True,
            "context": {"source_nation": "Saxony"},
        }

        # Saxony blocked, Austria can still generate (queued due to blocking)
        saxony_proposal = process_diplomatic_phase("Saxony", world)
        assert saxony_proposal is None

        # Austria should still generate (will be queued since dialogue is blocking)
        austria_proposal = process_diplomatic_phase("Austria", world)
        # It returns None because it gets queued, but queue should have it
        queue = _get_queue(world)
        austria_in_queue = any(item.get("source") == "Austria" for item in queue)
        assert austria_in_queue


# ═══════════════════════════════════════════════════════════════════════════
# SPAM-3: P7 OPPORTUNISTIC STATE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

class TestP7OpportunisticStateCheck:
    """P7 should only fire if current state is below NON_AGGRESSION."""

    def test_p7_fires_at_peace(self):
        """P7 opportunistic fires when at PEACE (below NON_AGGRESSION)."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 0)
        # France at war with 2+ nations
        _set_at_war(world, "France", "Prussia")
        _set_at_war(world, "France", "Austria")

        proposal = process_diplomatic_phase("Saxony", world)
        # Could be P4 (relation > 30) or P7 (opportunistic)
        # With relation=0, P4 won't fire, so P7 should
        assert proposal is not None
        assert proposal["proposal_type"] == "opportunistic"

    def test_p7_fires_at_open_borders(self):
        """P7 opportunistic fires when at OPEN_BORDERS (below NON_AGGRESSION)."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        _set_relation(world, "France", "Saxony", 0)
        _set_at_war(world, "France", "Prussia")
        _set_at_war(world, "France", "Austria")

        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is not None
        assert proposal["proposal_type"] == "opportunistic"

    def test_p7_blocked_at_non_aggression(self):
        """P7 opportunistic does NOT fire when already at NON_AGGRESSION."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "NON_AGGRESSION")
        _set_relation(world, "France", "Saxony", 0)
        _set_at_war(world, "France", "Prussia")
        _set_at_war(world, "France", "Austria")

        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is None

    def test_p7_blocked_at_alliance(self):
        """P7 opportunistic does NOT fire when already at ALLIANCE."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "ALLIANCE")
        _set_relation(world, "France", "Saxony", 0)
        _set_at_war(world, "France", "Prussia")
        _set_at_war(world, "France", "Austria")

        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is None

    def test_p7_blocked_at_defensive_alliance(self):
        """P7 opportunistic does NOT fire at DEFENSIVE_ALLIANCE."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "DEFENSIVE_ALLIANCE")
        _set_relation(world, "France", "Saxony", 0)
        _set_at_war(world, "France", "Prussia")
        _set_at_war(world, "France", "Austria")

        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is None


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION: FULL SPAM SCENARIO
# ═══════════════════════════════════════════════════════════════════════════

class TestAntiSpamIntegration:
    """End-to-end scenarios that verify spam prevention works together."""

    def test_accept_then_no_immediate_followup(self):
        """After accepting Saxony open_borders, no proposal next turn."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 40)

        # Generate and verify proposal exists
        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is not None

        # Simulate acceptance: upgrade state + apply cooldown
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        apply_acceptance_cooldown("Saxony", world)

        # Next turn: no proposal despite valid upgrade available
        proposal2 = process_diplomatic_phase("Saxony", world)
        assert proposal2 is None

    def test_accept_chain_with_cooldowns(self):
        """Accepting proposals still allows future proposals after cooldown."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "PEACE")
        _set_relation(world, "France", "Saxony", 40)

        # First proposal
        proposal1 = process_diplomatic_phase("Saxony", world)
        assert proposal1 is not None

        # Accept: upgrade + cooldown
        _set_diplo_state(world, "France", "Saxony", "OPEN_BORDERS")
        apply_acceptance_cooldown("Saxony", world)

        # Blocked by cooldown
        assert process_diplomatic_phase("Saxony", world) is None

        # Expire cooldown
        for _ in range(NATION_ACCEPTANCE_COOLDOWN):
            world._decrement_ai_proposal_cooldowns()

        # Now next upgrade should be available
        proposal2 = process_diplomatic_phase("Saxony", world)
        assert proposal2 is not None

    def test_p4_already_at_alliance_no_proposal(self):
        """P4 at ALLIANCE: _determine_upgrade_type returns None, no proposal."""
        world = _make_world()
        _set_diplo_state(world, "France", "Saxony", "ALLIANCE")
        _set_relation(world, "France", "Saxony", 40)

        proposal = process_diplomatic_phase("Saxony", world)
        assert proposal is None
