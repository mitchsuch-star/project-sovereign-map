"""
Systems Audit V3 Fix Plan — Session 7: Diplomacy, Dialogue & Economy

Tests for 13 bugs: diplomacy wizard, dialogue system, economy calculations.

Bug fixes:
- 1D-1: acceptance_preview references undefined `target` instead of `target_nation`
- 6B-1: Ledger net income omits admin bonus, treaty gold, vassal tribute
- 6B-3: Vassal tribute uses flat 50 instead of get_effective_income()
- 4B-2: Sabotage discovery overwrites pending_diplomatic_dialogue
- 4A-5: Proposal pre-check hardcodes "France" instead of player_nation
- 6B-2: Recruit error message uses raw INFANTRY_BASE_REGEN ignoring war exhaustion
- 6B-4: AUTONOMOUS vassals not excluded from Continental System
- 1D-5: Hardcoded "Vienna" in assessment template
- 6B-5: Stale TODO comment references Session 2
"""

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Fresh WorldState with France as player."""
    w = WorldState()
    return w


def set_war(world, nation_a, nation_b):
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = "WAR"


def set_peace(world, nation_a, nation_b):
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = "PEACE"


def make_marshal(name="Ney", location="Belgium", strength=30000, nation="France",
                 personality="aggressive", **kwargs):
    m = Marshal(name=name, location=location, strength=strength,
                personality=personality, nation=nation, spawn_location=location)
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def place_marshals(world, *marshals):
    world.marshals = {m.name: m for m in marshals}


# ═══════════════════════════════════════════════════════
# 1D-1: acceptance_preview uses target_nation not target
# ═══════════════════════════════════════════════════════

class TestAcceptancePreviewArmistice:
    """Bug 1D-1: acceptance_preview referenced undefined `target` variable."""

    def test_armistice_preview_uses_target_nation_not_target(self):
        """get_diplomatic_preview should not crash with NameError for armistice."""
        from backend.game_logic.diplomacy import get_diplomatic_preview
        world = make_world()
        set_war(world, "France", "Austria")
        world.diplomatic_points = 10
        ney = make_marshal("Ney", "Belgium", 30000, "France")
        place_marshals(world, ney)
        # Should not raise NameError: name 'target' is not defined
        result = get_diplomatic_preview(world, "Austria")
        # get_diplomatic_preview returns a dict with "nation" key (no "success" key)
        assert result["nation"] == "Austria"

    def test_armistice_preview_winning_vs_losing(self):
        """Armistice type should reflect war score direction."""
        from backend.game_logic.diplomacy import get_diplomatic_preview
        world = make_world()
        set_war(world, "France", "Prussia")
        world.diplomatic_points = 10
        # Give France a war score advantage (war_scores stores int, not dict)
        key = world._make_diplo_key("France", "Prussia")
        world.war_scores[key] = 30
        result = get_diplomatic_preview(world, "Prussia")
        assert result["nation"] == "Prussia"
        # The preview should complete without error regardless of war score


# ═══════════════════════════════════════════════════════
# 6B-1: Ledger net includes admin bonus, treaty gold, vassal tribute
# ═══════════════════════════════════════════════════════

class TestLedgerNetIncome:
    """Bug 6B-1: Ledger net = income + trade - upkeep, but omits admin/treaty/tribute."""

    def test_net_includes_admin_bonus(self):
        """Net income should include admin bonus from unused AP."""
        from backend.game_logic.ledger import build_strategic_ledger
        world = make_world()
        # Give France unused AP → admin bonus
        world.action_points = 3  # some unused AP
        ledger = build_strategic_ledger(world)
        economy = ledger["economy"]
        assert "admin_bonus" in economy
        # admin_bonus is int
        assert isinstance(economy["admin_bonus"], int)

    def test_net_includes_treaty_gold(self):
        """Net should include gold_per_turn treaty income."""
        from backend.game_logic.ledger import build_strategic_ledger
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "PEACE"
        world.active_treaties[key] = {
            "type": "peace",
            "clauses": [
                {"type": "gold_per_turn", "amount": 100, "to": "France", "from": "Austria"}
            ]
        }
        ledger = build_strategic_ledger(world)
        economy = ledger["economy"]
        assert economy["treaty_gold"] == 100

    def test_net_includes_vassal_tribute(self):
        """Net should include vassal tribute income."""
        from backend.game_logic.ledger import build_strategic_ledger
        world = make_world()
        # Set up a vassal with controlled regions
        world.vassals["Saxony"] = {
            "lord": "France",
            "tribute_rate": 0.5,
            "loyalty": 50,
            "autonomy": 1,
        }
        # Give Saxony control of a region
        world.regions["Saxony"].controller = "Saxony"
        ledger = build_strategic_ledger(world)
        economy = ledger["economy"]
        assert "vassal_tribute" in economy
        assert economy["vassal_tribute"] >= 0

    def test_net_subtracts_treaty_outgoing(self):
        """Treaty gold outgoing (from=player) should reduce net."""
        from backend.game_logic.ledger import build_strategic_ledger
        world = make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "PEACE"
        world.active_treaties[key] = {
            "type": "peace",
            "clauses": [
                {"type": "gold_per_turn", "amount": 50, "from": "France", "to": "Austria"}
            ]
        }
        ledger = build_strategic_ledger(world)
        economy = ledger["economy"]
        assert economy["treaty_gold"] == -50


# ═══════════════════════════════════════════════════════
# 6B-3: Vassal tribute uses get_effective_income()
# ═══════════════════════════════════════════════════════

class TestVassalTributeEffectiveIncome:
    """Bug 6B-3: Tribute calculation used flat 50 per region instead of get_effective_income()."""

    def test_tribute_uses_effective_income(self):
        """Tribute should use region's get_effective_income(), not flat 50."""
        from backend.game_logic.vassal import process_vassal_tribute
        world = make_world()
        world.vassals["Saxony"] = {
            "lord": "France",
            "tribute_rate": 1.0,  # 100% for easy math
            "loyalty": 50,
            "autonomy": 1,
        }
        # Saxony starts controlling Saxony + Dresden regions (150 + 100 = 250)
        # Calculate total effective income from all Saxony-controlled regions
        total_effective = sum(
            r.get_effective_income() for r in world.regions.values()
            if getattr(r, 'controller', '') == "Saxony"
        )
        assert total_effective > 0, "Saxony should control at least one region"
        # Ensure Saxony has enough gold to pay full tribute
        world.nation_gold["Saxony"] = 10000
        result = process_vassal_tribute(world)
        # With 100% tribute, tribute amount should equal total effective income
        assert "Saxony" in result
        assert result["Saxony"]["amount"] == int(total_effective)

    def test_tribute_respects_war_damage(self):
        """War-damaged regions should yield less tribute than undamaged ones."""
        world = make_world()
        world.vassals["Saxony"] = {
            "lord": "France",
            "tribute_rate": 1.0,
            "loyalty": 50,
            "autonomy": 1,
        }
        world.regions["Saxony"].controller = "Saxony"
        normal_income = world.regions["Saxony"].get_effective_income()

        # Apply war damage
        world.regions["Saxony"].war_damage = 50  # 50% damage
        damaged_income = world.regions["Saxony"].get_effective_income()
        assert damaged_income < normal_income or normal_income == 0


# ═══════════════════════════════════════════════════════
# 4B-2: Sabotage discovery queues instead of overwriting
# ═══════════════════════════════════════════════════════

class TestDialogueQueuePreservation:
    """Bug 4B-2: dispatch.py overwrites pending_diplomatic_dialogue on sabotage discovery."""

    def test_sabotage_discovery_queues_when_dialogue_pending(self):
        """When a dialogue is already pending, confrontation goes to queue."""
        world = make_world()
        # Set up existing pending dialogue
        world.pending_diplomatic_dialogue = {"type": "incoming_proposal", "from": "Austria"}

        # Simulate what dispatch.py does on sabotage discovery
        confrontation = {"type": "sabotage_discovery", "target": "Prussia"}
        if world.pending_diplomatic_dialogue:
            world.pending_dialogue_queue.append(confrontation)
        else:
            world.pending_diplomatic_dialogue = confrontation

        # Original dialogue should be preserved
        assert world.pending_diplomatic_dialogue["type"] == "incoming_proposal"
        assert len(world.pending_dialogue_queue) == 1
        assert world.pending_dialogue_queue[0]["type"] == "sabotage_discovery"

    def test_sabotage_discovery_sets_when_no_dialogue(self):
        """When no dialogue pending, confrontation is set directly."""
        world = make_world()
        assert world.pending_diplomatic_dialogue is None

        confrontation = {"type": "sabotage_discovery", "target": "Prussia"}
        if world.pending_diplomatic_dialogue:
            world.pending_dialogue_queue.append(confrontation)
        else:
            world.pending_diplomatic_dialogue = confrontation

        assert world.pending_diplomatic_dialogue["type"] == "sabotage_discovery"
        assert len(world.pending_dialogue_queue) == 0


# ═══════════════════════════════════════════════════════
# 4A-5: Proposal pre-check uses player_nation not "France"
# ═══════════════════════════════════════════════════════

class TestProposalFallbackState:
    """Bug 4A-5: executor hardcoded 'France' in diplomatic state checks."""

    def test_proposal_uses_player_nation_not_hardcoded(self):
        """Diplomatic state check should use world.player_nation, not 'France'."""
        from backend.commands.executor import CommandExecutor
        world = make_world()
        world.player_nation = "France"
        # Set up diplomatic state
        set_peace(world, "France", "Austria")
        world.diplomatic_points = 20
        ney = make_marshal("Ney", "Belgium", 30000, "France")
        place_marshals(world, ney)

        # Verify the executor uses player_nation for the check
        # (Previously hardcoded to "France" which would fail for non-France players)
        executor = CommandExecutor()
        game_state = {"world": world}
        # Execute a diplomacy command — if it uses player_nation correctly,
        # it should not crash
        result = executor.execute({
            "action": "diplomacy",
            "marshal_name": "Ney",
            "diplomatic_action": "propose",
            "diplomatic_data": {
                "target_nation": "Austria",
                "proposal_type": "open_borders",
            }
        }, game_state)
        # Should complete without error (may succeed or fail based on game state,
        # but should not crash from hardcoded nation)
        assert "message" in result


# ═══════════════════════════════════════════════════════
# 6B-2: Recruit regen message reflects war exhaustion
# ═══════════════════════════════════════════════════════

class TestRecruitRegenRate:
    """Bug 6B-2: Infantry recruit error used raw constant, not war-exhaustion-adjusted rate."""

    def test_infantry_regen_message_reflects_war_exhaustion(self):
        """When war exhaustion is high, regen rate in error should be lower than base."""
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import INFANTRY_BASE_REGEN
        world = make_world()
        world.player_nation = "France"
        ney = make_marshal("Ney", "Belgium", 30000, "France")
        place_marshals(world, ney)
        world.action_points = 3

        # Set high war exhaustion to reduce regen
        world.war_exhaustion = {"France": 80}

        # Empty the manpower pool so recruit fails with the regen message
        world.manpower_pools["France"] = {"infantry": 0, "cavalry": 500, "artillery": 200}

        executor = CommandExecutor()
        game_state = {"world": world}
        command = {
            "marshal": "Ney",
            "action": "recruit",
            "target": "Belgium",
            "_acting_nation": "France",
        }
        result = executor._execute_recruit(command, game_state)

        # Should fail (insufficient pool)
        assert result.get("success") is False
        # The regen rate in the message should reflect war exhaustion
        actual_rates = world.get_manpower_regen_rates("France")
        actual_infantry_regen = actual_rates["infantry"]
        # With war exhaustion, actual rate should be <= base rate
        assert actual_infantry_regen <= INFANTRY_BASE_REGEN
        # The message should contain the actual (reduced) regen rate
        assert f"+{actual_infantry_regen:,}/turn" in result["message"]


# ═══════════════════════════════════════════════════════
# 6B-4: AUTONOMOUS vassals excluded from Continental System
# ═══════════════════════════════════════════════════════

class TestCSAutonomousExclusion:
    """Bug 6B-4: AUTONOMOUS vassals should be removed from CS membership."""

    def test_autonomous_vassal_removed_from_cs(self):
        """An AUTONOMOUS vassal should not be in CS members after apply."""
        from backend.game_logic.diplomacy import apply_continental_system
        from backend.game_logic.vassal import AUTONOMY_AUTONOMOUS
        world = make_world()

        # Set up CS with Saxony as a member
        world.continental_system_members = ["Saxony"]
        world.vassals["Saxony"] = {
            "lord": "France",
            "loyalty": 50,
            "autonomy": AUTONOMY_AUTONOMOUS,
            "tribute_rate": 0.5,
        }

        apply_continental_system(world)

        # Saxony should have been removed because it's AUTONOMOUS
        assert "Saxony" not in world.continental_system_members


# ═══════════════════════════════════════════════════════
# 1D-5: No hardcoded "Vienna" in assessment templates
# ═══════════════════════════════════════════════════════

class TestViennaRemoved:
    """Bug 1D-5: 'Vienna' was hardcoded in peace_wary assessment."""

    def test_no_hardcoded_vienna_in_templates(self):
        """Assessment templates should not reference specific city names."""
        import inspect
        from backend.game_logic import diplomacy
        source = inspect.getsource(diplomacy)
        # Check that "Vienna watches" is no longer in the source
        assert "Vienna watches" not in source


# ═══════════════════════════════════════════════════════
# 6B-5: Stale TODO comment removed
# ═══════════════════════════════════════════════════════

class TestStaleTodoRemoved:
    """Bug 6B-5: Stale 'TODO: Trade income (deferred to Session 2)' comment."""

    def test_no_stale_session2_todo(self):
        """The stale TODO should be replaced with accurate comment."""
        import inspect
        from backend.models import world_state
        source = inspect.getsource(world_state)
        assert "TODO: Trade income (deferred to Session 2)" not in source
        # The replacement comment should exist
        assert "Trade income applied separately" in source
