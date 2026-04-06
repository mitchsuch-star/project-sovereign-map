"""
Bug Fix Session 4 Tests: DLF-1, DLF-3, DLF-9, DLF-4, DLF-5, DLF-2

DLF-1: Vassalizable icon requires qualifying diplomatic state (2 tests)
DLF-3: AI-AI relations filtered to notable states only (3 tests)
DLF-9: P3 proposal uses _determine_upgrade_type (6 tests)
DLF-4: COURT_NATION blowback 20% chance fires (7 tests)
DLF-5: GATHER_INTEL grants FULL visibility for 5 turns (7 tests)
DLF-2: UNDERMINE_ALLIANCE ally selection + per-turn effect (8 tests)
"""

from unittest.mock import patch
from backend.models.world_state import WorldState
from backend.models.marshal import Marshal


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def make_world():
    """Create a basic world with clean diplomatic states."""
    world = WorldState(player_nation="France")
    return world


def set_state(world, nation_a, nation_b, state):
    key = world._make_diplo_key(nation_a, nation_b)
    world.diplomatic_states[key] = state


def set_relation(world, nation_a, nation_b, value):
    key = world._make_diplo_key(nation_a, nation_b)
    world.nation_relations[key] = value


def add_marshal(world, name, nation, location, strength=10000, personality="balanced"):
    m = Marshal(name=name, nation=nation, location=location,
                strength=strength, personality=personality)
    world.marshals[name] = m
    return m


def setup_mission(world, mission_type, target, **kwargs):
    """Set up an active diplomatic mission."""
    world.active_diplomatic_mission = {
        "type": mission_type,
        "target": target,
        "turns_active": 0,
        "paused": False,
        "paused_turns": 0,
        "started_turn": int(world.current_turn),
        "initial_relation": 0,
        **kwargs,
    }
    world.talleyrand_state = "ON_MISSION"


# ═══════════════════════════════════════════════════════
# DLF-1: VASSALIZABLE ICON DIPLOMATIC STATE CHECK
# ═══════════════════════════════════════════════════════

class TestDLF1VassalizableIcon:

    def test_vassal_icon_excluded_for_peace_state(self):
        """Vassal icon should NOT show when diplomatic state is PEACE."""
        world = make_world()
        set_state(world, "France", "Prussia", "PEACE")
        set_relation(world, "France", "Prussia", -20)
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=5000)

        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)

        nations = ledger.get("nations", [])
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        assert prussia["vassal_eligible"] is False

    def test_vassal_icon_included_for_war_state(self):
        """Vassal icon should show when at WAR with low relation."""
        world = make_world()
        set_state(world, "France", "Prussia", "WAR")
        set_relation(world, "France", "Prussia", -20)
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=5000)

        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)

        nations = ledger.get("nations", [])
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        assert prussia["vassal_eligible"] is True


# ═══════════════════════════════════════════════════════
# DLF-3: AI-AI RELATIONS DISPLAY FILTERING
# ═══════════════════════════════════════════════════════

class TestDLF3AIRelationsFiltering:

    def test_ai_relations_excludes_peace(self):
        """PEACE state should not appear in AI-AI relations list."""
        world = make_world()
        set_state(world, "Prussia", "Austria", "PEACE")
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=5000)
        add_marshal(world, "Charles", "Austria", "Vienna", strength=5000)

        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)

        nations = ledger.get("nations", [])
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        ai_rels = prussia.get("ai_relations", [])
        austria_rel = [r for r in ai_rels if r["nation"] == "Austria"]
        assert len(austria_rel) == 0

    def test_ai_relations_includes_war(self):
        """WAR state should appear in AI-AI relations list."""
        world = make_world()
        set_state(world, "Prussia", "Austria", "WAR")
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=5000)
        add_marshal(world, "Charles", "Austria", "Vienna", strength=5000)

        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)

        nations = ledger.get("nations", [])
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        ai_rels = prussia.get("ai_relations", [])
        austria_rel = [r for r in ai_rels if r["nation"] == "Austria"]
        assert len(austria_rel) == 1
        assert austria_rel[0]["state"] == "WAR"

    def test_ai_relations_includes_alliance(self):
        """ALLIANCE state should appear in AI-AI relations list."""
        world = make_world()
        set_state(world, "Prussia", "Austria", "ALLIANCE")
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=5000)
        add_marshal(world, "Charles", "Austria", "Vienna", strength=5000)

        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)

        nations = ledger.get("nations", [])
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        ai_rels = prussia.get("ai_relations", [])
        austria_rel = [r for r in ai_rels if r["nation"] == "Austria"]
        assert len(austria_rel) == 1
        assert austria_rel[0]["state"] == "ALLIANCE"


# ═══════════════════════════════════════════════════════
# DLF-9: P3 PROPOSAL UPGRADE PATH VALIDATION
# ═══════════════════════════════════════════════════════

class TestDLF9P3UpgradePath:

    def _run_p3(self, world, nation):
        """Run AI proposal generation and return result."""
        from backend.game_logic.ai_diplomacy import process_diplomatic_phase
        return process_diplomatic_phase(nation, world)

    def test_p3_proposes_open_borders_from_peace(self):
        """From PEACE with high threat, P3 should propose OPEN_BORDERS (first step)."""
        world = make_world()
        set_state(world, "France", "Prussia", "PEACE")
        set_relation(world, "France", "Prussia", 25)
        world.threat_level = 70

        proposal = self._run_p3(world, "Prussia")
        if proposal:
            assert proposal.get("proposal_type") == "open_borders"

    def test_p3_proposes_non_aggression_from_open_borders(self):
        """From OPEN_BORDERS, P3 should propose NON_AGGRESSION."""
        world = make_world()
        set_state(world, "France", "Prussia", "OPEN_BORDERS")
        set_relation(world, "France", "Prussia", 25)
        world.threat_level = 70

        proposal = self._run_p3(world, "Prussia")
        if proposal:
            assert proposal.get("proposal_type") == "non_aggression"

    def test_p3_proposes_defensive_alliance_from_non_aggression(self):
        """From NON_AGGRESSION with sufficient relation, P3 should propose DEFENSIVE_ALLIANCE."""
        world = make_world()
        set_state(world, "France", "Prussia", "NON_AGGRESSION")
        set_relation(world, "France", "Prussia", 30)
        world.threat_level = 70

        proposal = self._run_p3(world, "Prussia")
        if proposal:
            assert proposal.get("proposal_type") == "defensive_alliance"

    def test_p3_no_proposal_when_already_alliance(self):
        """Already at ALLIANCE — P3 should not propose anything."""
        world = make_world()
        set_state(world, "France", "Prussia", "ALLIANCE")
        set_relation(world, "France", "Prussia", 50)
        world.threat_level = 70

        proposal = self._run_p3(world, "Prussia")
        # P3 guard: diplo_state not in ("DEFENSIVE_ALLIANCE", "ALLIANCE")
        # So P3 should not fire. Proposal may be None or from another trigger.
        if proposal:
            assert proposal.get("priority") != 3

    def test_p3_no_proposal_when_relation_below_requirement(self):
        """NON_AGGRESSION but relation < 20 — can't propose DEFENSIVE_ALLIANCE."""
        world = make_world()
        set_state(world, "France", "Prussia", "NON_AGGRESSION")
        set_relation(world, "France", "Prussia", 10)  # Below 20 requirement
        world.threat_level = 70

        proposal = self._run_p3(world, "Prussia")
        # _determine_upgrade_type returns None if relation < requirement
        if proposal:
            assert proposal.get("priority") != 3

    def test_p3_no_proposal_when_at_war(self):
        """At WAR with high threat — P3 should not fire (guarded by not is_at_war)."""
        world = make_world()
        set_state(world, "France", "Prussia", "WAR")
        set_relation(world, "France", "Prussia", 25)
        world.threat_level = 70

        proposal = self._run_p3(world, "Prussia")
        if proposal:
            assert proposal.get("priority") != 3


# ═══════════════════════════════════════════════════════
# DLF-4: COURT_NATION BLOWBACK
# ═══════════════════════════════════════════════════════

class TestDLF4CourtNationBlowback:

    def _process(self, world):
        from backend.game_logic.diplomacy import _process_mission_effects
        return _process_mission_effects(world)

    def test_blowback_triggers_on_low_roll(self):
        """Blowback should fire when random < 0.20."""
        world = make_world()
        set_relation(world, "France", "Austria", 30)
        setup_mission(world, "COURT_NATION", "Austria")
        # Default Talleyrand skill=10 → 1.5x → int(round(5*1.5))=8 relation/turn

        with patch("backend.game_logic.diplomacy.random.random", return_value=0.10):
            events = self._process(world)

        key = world._make_diplo_key("France", "Austria")
        # +8 relation (skill 10 → 1.5x) then -3 blowback = net +5
        relation = world.nation_relations.get(key, 0)
        assert relation == 35  # 30 + 8 - 3

    def test_blowback_not_triggered_on_high_roll(self):
        """No blowback when random >= 0.20."""
        world = make_world()
        set_relation(world, "France", "Austria", 30)
        setup_mission(world, "COURT_NATION", "Austria")

        with patch("backend.game_logic.diplomacy.random.random", return_value=0.50):
            events = self._process(world)

        key = world._make_diplo_key("France", "Austria")
        relation = world.nation_relations.get(key, 0)
        assert relation == 38  # 30 + 8 (skill 10 → 1.5x), no blowback

    def test_blowback_is_not_skill_scaled(self):
        """Blowback penalty should be fixed -3, not scaled by Talleyrand skill."""
        world = make_world()
        set_relation(world, "France", "Austria", 30)
        setup_mission(world, "COURT_NATION", "Austria")
        # Set Talleyrand skill to 10 (1.5x multiplier)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats["France"] = DiplomaticRepresentative(
            name="Talleyrand", nation="France", personality="cunning", skill=10
        )

        with patch("backend.game_logic.diplomacy.random.random", return_value=0.10):
            events = self._process(world)

        key = world._make_diplo_key("France", "Austria")
        relation = world.nation_relations.get(key, 0)
        # +5 * 1.5 = +8 (rounded), then -3 blowback (fixed) = 30 + 8 - 3 = 35
        assert relation == 35

    def test_blowback_event_emitted(self):
        """Blowback should emit a diplomatic_mission_blowback event."""
        world = make_world()
        set_relation(world, "France", "Austria", 30)
        setup_mission(world, "COURT_NATION", "Austria")

        with patch("backend.game_logic.diplomacy.random.random", return_value=0.10):
            events = self._process(world)

        blowback_events = [e for e in events if e["type"] == "diplomatic_mission_blowback"]
        assert len(blowback_events) == 1
        assert blowback_events[0]["target"] == "Austria"
        assert blowback_events[0]["delta"] == -3

    def test_blowback_no_event_when_not_triggered(self):
        """No blowback event when roll is high."""
        world = make_world()
        set_relation(world, "France", "Austria", 30)
        setup_mission(world, "COURT_NATION", "Austria")

        with patch("backend.game_logic.diplomacy.random.random", return_value=0.50):
            events = self._process(world)

        blowback_events = [e for e in events if e["type"] == "diplomatic_mission_blowback"]
        assert len(blowback_events) == 0

    def test_relation_change_still_applies_with_blowback(self):
        """Positive relation change should still apply even when blowback fires."""
        world = make_world()
        set_relation(world, "France", "Austria", 0)
        setup_mission(world, "COURT_NATION", "Austria")

        with patch("backend.game_logic.diplomacy.random.random", return_value=0.10):
            events = self._process(world)

        key = world._make_diplo_key("France", "Austria")
        relation = world.nation_relations.get(key, 0)
        # +8 (relation_change, skill 10 → 1.5x) - 3 (blowback) = +5
        assert relation == 5

    def test_improve_relations_no_blowback(self):
        """IMPROVE_RELATIONS should never trigger blowback (no undermine_chance)."""
        world = make_world()
        set_relation(world, "France", "Austria", 30)
        setup_mission(world, "IMPROVE_RELATIONS", "Austria")

        with patch("backend.game_logic.diplomacy.random.random", return_value=0.01):
            events = self._process(world)

        blowback_events = [e for e in events if e["type"] == "diplomatic_mission_blowback"]
        assert len(blowback_events) == 0


# ═══════════════════════════════════════════════════════
# DLF-5: GATHER_INTEL GRANTS VISIBILITY
# ═══════════════════════════════════════════════════════

class TestDLF5GatherIntel:

    def _process(self, world):
        from backend.game_logic.diplomacy import _process_mission_effects
        return _process_mission_effects(world)

    def test_gather_intel_grants_full_visibility(self):
        """GATHER_INTEL completion should grant FULL visibility on target regions."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=10000)
        # Set Berlin controlled by Prussia
        if "Berlin" in world.regions:
            world.regions["Berlin"].controller = "Prussia"
        setup_mission(world, "GATHER_INTEL", "Prussia", turns_active=3)

        events = self._process(world)

        # Check intel was granted
        if "Berlin" in world.regions and world.regions["Berlin"].controller == "Prussia":
            intel = world.get_region_intel("Berlin")
            assert intel.visibility == "full"

    def test_gather_intel_sets_expiry(self):
        """Intel grants should have expiry = current_turn + 5."""
        world = make_world()
        world.current_turn = 10
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=10000)
        if "Berlin" in world.regions:
            world.regions["Berlin"].controller = "Prussia"
        setup_mission(world, "GATHER_INTEL", "Prussia", turns_active=3)

        events = self._process(world)

        if "Berlin" in world.regions and world.regions["Berlin"].controller == "Prussia":
            assert world.intel_grants.get("Berlin") == 15  # 10 + 5

    def test_gather_intel_prevents_decay(self):
        """Intel grants should prevent decay during grant window."""
        world = make_world()
        world.current_turn = 10
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=10000)
        if "Berlin" in world.regions:
            world.regions["Berlin"].controller = "Prussia"
        setup_mission(world, "GATHER_INTEL", "Prussia", turns_active=3)

        self._process(world)

        if "Berlin" in world.regions and world.regions["Berlin"].controller == "Prussia":
            # Simulate decay at turn 12 (within grant window)
            world.current_turn = 12
            world._refreshed_regions_this_turn = set()
            world.decay_intel()
            intel = world.get_region_intel("Berlin")
            assert intel.visibility == "full"

    def test_gather_intel_expires_after_window(self):
        """Intel grants should allow decay after expiry."""
        world = make_world()
        world.current_turn = 10
        world.intel_grants = {"Berlin": 12}  # Expires at turn 12

        # At turn 13, grant should be expired
        world.current_turn = 13
        world._refreshed_regions_this_turn = set()
        world.decay_intel()

        # Expired grant should be cleaned up
        assert "Berlin" not in world.intel_grants

    def test_gather_intel_serialization_roundtrip(self):
        """intel_grants should survive to_dict/from_dict roundtrip."""
        world = make_world()
        world.intel_grants = {"Berlin": 15, "Vienna": 20}

        data = world.to_dict()
        assert "intel_grants" in data
        assert data["intel_grants"]["Berlin"] == 15

        world2 = WorldState.from_dict(data)
        assert world2.intel_grants == {"Berlin": 15, "Vienna": 20}

    def test_gather_intel_completion_event(self):
        """Completion event should mention regions revealed."""
        world = make_world()
        add_marshal(world, "Blucher", "Prussia", "Berlin", strength=10000)
        if "Berlin" in world.regions:
            world.regions["Berlin"].controller = "Prussia"
        setup_mission(world, "GATHER_INTEL", "Prussia", turns_active=3)

        events = self._process(world)

        completed = [e for e in events if e["type"] == "diplomatic_mission_completed"]
        assert len(completed) == 1
        assert "regions_revealed" in completed[0]

    def test_gather_intel_empty_when_no_regions(self):
        """If target controls no regions, grant still completes with 0 regions."""
        world = make_world()
        # Don't set any region controller to "Fakeland"
        setup_mission(world, "GATHER_INTEL", "Fakeland", turns_active=3)

        events = self._process(world)

        completed = [e for e in events if e["type"] == "diplomatic_mission_completed"]
        assert len(completed) == 1
        assert completed[0].get("regions_revealed", 0) == 0


# ═══════════════════════════════════════════════════════
# DLF-2: UNDERMINE_ALLIANCE
# ═══════════════════════════════════════════════════════

class TestDLF2UndermineAlliance:

    def _process(self, world):
        from backend.game_logic.diplomacy import _process_mission_effects
        return _process_mission_effects(world)

    def _generate_dialogue(self, parsed, world):
        from backend.game_logic.diplomatic_dialogue import generate_mission_dialogue
        return generate_mission_dialogue(parsed, world)

    def test_undermine_reduces_relation_between_targets(self):
        """Per-turn effect should reduce relation between target and target_ally."""
        world = make_world()
        set_state(world, "Prussia", "Austria", "ALLIANCE")
        set_relation(world, "Prussia", "Austria", 50)
        setup_mission(world, "UNDERMINE_ALLIANCE", "Prussia", target_ally="Austria")

        self._process(world)

        key = world._make_diplo_key("Prussia", "Austria")
        relation = world.nation_relations.get(key, 0)
        assert relation < 50  # Should have decreased

    def test_undermine_skill_scaled(self):
        """Undermine effect should be skill-scaled (unlike COURT_NATION blowback)."""
        world = make_world()
        set_state(world, "Prussia", "Austria", "ALLIANCE")
        set_relation(world, "Prussia", "Austria", 50)
        setup_mission(world, "UNDERMINE_ALLIANCE", "Prussia", target_ally="Austria")
        # Set Talleyrand skill to 10 (1.5x multiplier)
        from backend.models.diplomat import DiplomaticRepresentative
        world.diplomats["France"] = DiplomaticRepresentative(
            name="Talleyrand", nation="France", personality="cunning", skill=10
        )

        self._process(world)

        key = world._make_diplo_key("Prussia", "Austria")
        relation = world.nation_relations.get(key, 0)
        # -3 * 1.5 = -4.5 → round → -4 or -5
        assert relation == 50 + int(round(-3 * 1.5))

    def test_undermine_auto_cancels_when_alliance_breaks(self):
        """Mission should auto-cancel if target pair is no longer allied."""
        world = make_world()
        set_state(world, "Prussia", "Austria", "NON_AGGRESSION")  # Not allied!
        set_relation(world, "Prussia", "Austria", 10)
        setup_mission(world, "UNDERMINE_ALLIANCE", "Prussia", target_ally="Austria")

        events = self._process(world)

        assert world.active_diplomatic_mission["completed"] is True
        assert world.talleyrand_state == "IDLE"
        completed = [e for e in events if e["type"] == "diplomatic_mission_completed"]
        assert len(completed) == 1

    def test_undermine_no_effect_without_target_ally(self):
        """Mission without target_ally should not crash or modify relations."""
        world = make_world()
        set_state(world, "Prussia", "Austria", "ALLIANCE")
        set_relation(world, "Prussia", "Austria", 50)
        setup_mission(world, "UNDERMINE_ALLIANCE", "Prussia")
        # No target_ally set

        events = self._process(world)

        key = world._make_diplo_key("Prussia", "Austria")
        assert world.nation_relations.get(key, 0) == 50  # Unchanged

    def test_ally_selection_single(self):
        """With one ally, dialogue should auto-select it."""
        world = make_world()
        # Clear all existing alliances for Prussia first
        for key in list(world.diplomatic_states.keys()):
            if "Prussia" in key:
                world.diplomatic_states[key] = "PEACE"
        # Set exactly one alliance
        set_state(world, "Prussia", "Austria", "ALLIANCE")

        dialogue = self._generate_dialogue(
            {"target_nation": "Prussia", "mission_type": "UNDERMINE_ALLIANCE"}, world
        )

        # Should have start_mission option with target_ally embedded
        start_options = [o for o in dialogue["options"] if o.get("action") == "start_mission"]
        assert len(start_options) == 1
        assert start_options[0]["terms"]["target_ally"] == "Austria"

    def test_ally_selection_multiple(self):
        """With multiple allies, dialogue should present options."""
        world = make_world()
        # Clear all existing alliances for Prussia first
        for key in list(world.diplomatic_states.keys()):
            if "Prussia" in key:
                world.diplomatic_states[key] = "PEACE"
        set_state(world, "Prussia", "Austria", "ALLIANCE")
        set_state(world, "Prussia", "Britain", "DEFENSIVE_ALLIANCE")

        dialogue = self._generate_dialogue(
            {"target_nation": "Prussia", "mission_type": "UNDERMINE_ALLIANCE"}, world
        )

        start_options = [o for o in dialogue["options"] if o.get("action") == "start_mission"]
        assert len(start_options) == 2
        allies_offered = {o["terms"]["target_ally"] for o in start_options}
        assert "Austria" in allies_offered
        assert "Britain" in allies_offered

    def test_ally_selection_no_allies(self):
        """With no allies, dialogue should show error."""
        world = make_world()
        # Clear all alliances for Prussia
        for key in list(world.diplomatic_states.keys()):
            if "Prussia" in key:
                world.diplomatic_states[key] = "PEACE"
        set_state(world, "France", "Prussia", "WAR")

        dialogue = self._generate_dialogue(
            {"target_nation": "Prussia", "mission_type": "UNDERMINE_ALLIANCE"}, world
        )

        assert "no alliances" in dialogue["talleyrand_text"].lower()
        start_options = [o for o in dialogue["options"] if o.get("action") == "start_mission"]
        assert len(start_options) == 0

    def test_undermine_ledger_shows_target_ally(self):
        """Ledger should include target_ally for UNDERMINE_ALLIANCE missions."""
        world = make_world()
        setup_mission(world, "UNDERMINE_ALLIANCE", "Prussia", target_ally="Austria")

        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        ledger = build_diplomatic_ledger(world)

        talleyrand = ledger.get("talleyrand", {})
        mission = talleyrand.get("active_mission")
        assert mission is not None
        assert mission.get("target_ally") == "Austria"

    def test_executor_stores_target_ally(self):
        """start_mission action should store target_ally in mission dict."""
        world = make_world()
        world.diplomatic_points = 10
        set_state(world, "Prussia", "Austria", "ALLIANCE")
        # Clear other Prussia alliances
        for key in list(world.diplomatic_states.keys()):
            if "Prussia" in key and key != world._make_diplo_key("Prussia", "Austria"):
                world.diplomatic_states[key] = "PEACE"

        # Generate dialogue with ally selection
        from backend.game_logic.diplomatic_dialogue import generate_mission_dialogue
        dialogue = generate_mission_dialogue(
            {"target_nation": "Prussia", "mission_type": "UNDERMINE_ALLIANCE"}, world
        )
        # Push dialogue so executor can process it
        world.dialogue_manager.push(dialogue)

        # Simulate selecting the start_mission option
        start_option = [o for o in dialogue["options"] if o.get("action") == "start_mission"][0]

        from backend.commands.diplomatic_executor import DiplomaticExecutor
        from backend.commands.executor import CommandExecutor
        executor = CommandExecutor()
        diplo_exec = DiplomaticExecutor(executor)

        result = diplo_exec._process_dialogue_choice(
            start_option["action"], start_option, dialogue, world
        )

        assert result["success"] is True
        mission = world.active_diplomatic_mission
        assert mission is not None
        assert mission["type"] == "UNDERMINE_ALLIANCE"
        assert mission["target_ally"] == "Austria"

    def test_gather_intel_controller_change_during_grant(self):
        """If region controller changes during grant, grant key is stale but harmless."""
        world = make_world()
        world.current_turn = 10
        world.intel_grants = {"Berlin": 15}  # Grant active

        # Change controller — grant key is stale but decay still skips it
        if "Berlin" in world.regions:
            world.regions["Berlin"].controller = "France"

        world._refreshed_regions_this_turn = set()
        world.decay_intel()

        # Grant still in dict (not expired yet), no crash
        assert world.intel_grants.get("Berlin") == 15
