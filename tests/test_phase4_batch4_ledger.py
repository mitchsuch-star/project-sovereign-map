"""
Phase 4 Batch 4: Ledger & Alliance Paradox
Tests for R17a (war score breakdown), R17b (proposal cooldowns),
R17c (treaty gold costs), R12 (alliance paradox).
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════ FIXTURES ═══════

@pytest.fixture
def world():
    w = WorldState()
    if not hasattr(w, 'pending_dispatch_events'):
        w.pending_dispatch_events = []
    return w


@pytest.fixture
def executor():
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    return {"world": world}


# ═══════ R17a: WAR SCORE BREAKDOWN IN NATIONS TAB ═══════

class TestR17aWarScoreBreakdown:
    """R17a: Nations at WAR show war score component breakdown."""

    def test_war_score_breakdown_appears_for_at_war(self, world):
        """Nations AT_WAR should have a war_score_breakdown dict."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        # Set Prussia at war with France
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "WAR"
        ledger = build_diplomatic_ledger(world)
        nations = ledger["nations"]
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        assert prussia["war_score_breakdown"] is not None
        assert "total" in prussia["war_score_breakdown"]
        assert "territory" in prussia["war_score_breakdown"]
        assert "battles" in prussia["war_score_breakdown"]
        assert "decisive" in prussia["war_score_breakdown"]
        assert "capital" in prussia["war_score_breakdown"]

    def test_war_score_breakdown_none_for_peace(self, world):
        """Nations at PEACE should have war_score_breakdown = None."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[diplo_key] = "PEACE"
        ledger = build_diplomatic_ledger(world)
        nations = ledger["nations"]
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        assert prussia["war_score_breakdown"] is None

    def test_war_score_breakdown_values_are_ints(self, world):
        """All war score components must be int() wrapped for Godot."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        diplo_key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[diplo_key] = "WAR"
        ledger = build_diplomatic_ledger(world)
        nations = ledger["nations"]
        austria = next((n for n in nations if n["name"] == "Austria"), None)
        assert austria is not None
        breakdown = austria["war_score_breakdown"]
        assert breakdown is not None
        for key, val in breakdown.items():
            assert isinstance(val, int), f"Component {key} = {val} is not int"


# ═══════ R17b: PROPOSAL COOLDOWNS PER NATION ═══════

class TestR17bProposalCooldowns:
    """R17b: Nations tab shows proposal cooldown turns remaining."""

    def test_cooldown_shown_for_nation(self, world):
        """Nation-level cooldown appears in ledger."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world.player_proposal_cooldowns = {"Prussia": 3}
        ledger = build_diplomatic_ledger(world)
        nations = ledger["nations"]
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        assert prussia["proposal_cooldowns"] is not None
        assert prussia["proposal_cooldowns"]["nation"] == 3

    def test_type_cooldown_shown(self, world):
        """Per-type cooldown appears in ledger."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world.player_proposal_cooldowns = {"Prussia_peace": 5}
        ledger = build_diplomatic_ledger(world)
        nations = ledger["nations"]
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        assert prussia["proposal_cooldowns"] is not None
        assert prussia["proposal_cooldowns"]["peace"] == 5

    def test_no_cooldown_returns_none(self, world):
        """No cooldown for a nation returns None."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        world.player_proposal_cooldowns = {}
        ledger = build_diplomatic_ledger(world)
        nations = ledger["nations"]
        prussia = next((n for n in nations if n["name"] == "Prussia"), None)
        assert prussia is not None
        assert prussia["proposal_cooldowns"] is None


# ═══════ R17c: TREATY GOLD/TURN COSTS ═══════

class TestR17cTreatyGoldCosts:
    """R17c: Treaties tab shows gold/turn costs from clauses."""

    def test_gold_per_turn_shown(self, world):
        """Treaty with gold_per_turn clause shows cost."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        diplo_key = world._make_diplo_key("France", "Prussia")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Prussia"],
            "type": "peace",
            "clauses": [
                {"type": "gold_per_turn", "from": "France", "to": "Prussia", "amount": 200}
            ],
        }
        ledger = build_diplomatic_ledger(world)
        treaties = ledger["treaties"]
        assert len(treaties) >= 1
        treaty = treaties[0]
        assert treaty["gold_per_turn"] is not None
        assert len(treaty["gold_per_turn"]) == 1
        assert treaty["gold_per_turn"][0]["from"] == "France"
        assert treaty["gold_per_turn"][0]["to"] == "Prussia"
        assert treaty["gold_per_turn"][0]["amount"] == 200

    def test_no_gold_clause_returns_none(self, world):
        """Treaty without gold_per_turn clause returns None."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger
        diplo_key = world._make_diplo_key("France", "Austria")
        world.active_treaties[diplo_key] = {
            "nations": ["France", "Austria"],
            "type": "alliance",
            "clauses": [],
        }
        ledger = build_diplomatic_ledger(world)
        treaties = ledger["treaties"]
        treaty = next((t for t in treaties if "Austria" in (t["nation_a"], t["nation_b"])), None)
        assert treaty is not None
        assert treaty["gold_per_turn"] is None


# ═══════ R12: ALLIANCE PARADOX ═══════

class TestR12CommitmentParadox:
    """R12: Commitment paradox detected when AI allies of France go to war."""

    def test_paradox_detected(self, world):
        """When both attacker and defender are allied with player, popup is set."""
        from backend.game_logic.diplomacy import declare_war
        player = world.player_nation  # France
        # Set both Prussia and Austria as allied with France
        world.diplomatic_states[world._make_diplo_key(player, "Prussia")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key(player, "Austria")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "PEACE"
        # Prussia declares war on Austria
        result = declare_war(world, "Prussia", "Austria")
        assert result["success"]
        # Alliance paradox popup should be set
        assert world.commitment_paradox_popup is not None
        assert world.commitment_paradox_popup["attacker"] == "Prussia"
        assert world.commitment_paradox_popup["defender"] == "Austria"

    def test_paradox_not_triggered_if_not_allied(self, world):
        """No paradox if player is not allied with both nations."""
        from backend.game_logic.diplomacy import declare_war
        player = world.player_nation
        world.diplomatic_states[world._make_diplo_key(player, "Prussia")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key(player, "Austria")] = "PEACE"
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "PEACE"
        result = declare_war(world, "Prussia", "Austria")
        assert result["success"]
        assert world.commitment_paradox_popup is None

    def test_paradox_creates_dialogue(self, world):
        """Alliance paradox also creates a pending_diplomatic_dialogue with two options."""
        from backend.game_logic.diplomacy import declare_war
        player = world.player_nation
        world.diplomatic_states[world._make_diplo_key(player, "Prussia")] = "DEFENSIVE_ALLIANCE"
        world.diplomatic_states[world._make_diplo_key(player, "Austria")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "PEACE"
        declare_war(world, "Prussia", "Austria")
        # V2-89: alliance paradox now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue["type"] == "commitment_paradox"
        assert dialogue["episode_id"] == dialogue["origin_episode_id"]
        assert dialogue["primary_nation"] == "Prussia"
        assert dialogue["secondary_nation"] == "Austria"
        assert len(dialogue["options"]) == 2
        assert dialogue["options"][0]["action"] == "honor_defender"
        assert dialogue["options"][1]["action"] == "break_defender_alliance"

    def test_paradox_dialogue_previews_both_branches_under_one_episode(self, world):
        """Both paradox branches should carry deterministic fallout under one origin episode."""
        from backend.game_logic.diplomacy import declare_war
        player = world.player_nation
        world.diplomatic_states[world._make_diplo_key(player, "Prussia")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key(player, "Austria")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "PEACE"

        declare_war(world, "Prussia", "Austria")

        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert "Honor Austria:" in dialogue.get("talleyrand_text", "")
        assert "Side with Prussia:" in dialogue.get("talleyrand_text", "")
        assert dialogue.get("origin_episode_id")
        assert dialogue["honor_defender_preview"]["episode_id"] == dialogue["origin_episode_id"]
        assert dialogue["break_defender_preview"]["episode_id"] == dialogue["origin_episode_id"]

    def test_honor_defender_choice(self, world, executor, game_state):
        """Choosing 'honor defender' declares war on the attacker."""
        from backend.game_logic.diplomacy import declare_war
        player = world.player_nation
        world.diplomatic_states[world._make_diplo_key(player, "Prussia")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key(player, "Austria")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "PEACE"
        declare_war(world, "Prussia", "Austria")
        # V2-89: alliance paradox now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        # Now handle the dialogue choice
        assert world.pending_diplomatic_dialogue is not None
        result = executor.handle_diplomatic_dialogue_response("1", game_state)
        assert result.get("success"), result.get("message")
        # France should now be at war with Prussia (the attacker)
        assert world.is_at_war(player, "Prussia")
        # Dialogue and popup should be cleared
        assert world.pending_diplomatic_dialogue is None
        assert world.commitment_paradox_popup is None

    def test_honor_defender_logs_commitment_paradox_resolution(self, world, executor, game_state):
        from backend.game_logic.diplomacy import declare_war
        player = world.player_nation
        world.diplomatic_states[world._make_diplo_key(player, "Prussia")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key(player, "Austria")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "PEACE"

        declare_war(world, "Prussia", "Austria")
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        paradox_episode = world.pending_diplomatic_dialogue["origin_episode_id"]

        result = executor.handle_diplomatic_dialogue_response("1", game_state)

        assert result.get("success"), result.get("message")
        paradox_events = [
            e for e in world.event_log
            if e.get("type") == "commitment_paradox_resolved"
        ]
        assert paradox_events
        latest = paradox_events[-1]
        assert latest.get("episode_id") == paradox_episode
        assert latest.get("chosen_nation") == "Austria"
        assert latest.get("spurned_nation") == "Prussia"
        dispatch_events = [
            e for e in world.pending_dispatch_events
            if e.get("type") == "commitment_paradox_resolved"
        ]
        assert dispatch_events == []

    def test_break_defender_choice(self, world, executor, game_state):
        """Choosing 'break defender alliance' downgrades alliance with defender."""
        from backend.game_logic.diplomacy import declare_war
        player = world.player_nation
        world.diplomatic_states[world._make_diplo_key(player, "Prussia")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key(player, "Austria")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "PEACE"
        declare_war(world, "Prussia", "Austria")
        # V2-89: alliance paradox now appends to queue; pop to active dialogue
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        assert world.pending_diplomatic_dialogue is not None
        # Choose option 2: break alliance with defender (Austria)
        result = executor.handle_diplomatic_dialogue_response("2", game_state)
        assert result.get("success"), result.get("message")
        # France should NOT be at war with Prussia
        assert not world.is_at_war(player, "Prussia")
        # Alliance with Austria (defender) should be broken / downgraded
        state = world.get_diplomatic_state(player, "Austria")
        assert state == "PEACE", f"Expected PEACE, got {state}"
        # Dialogue and popup should be cleared
        assert world.pending_diplomatic_dialogue is None
        assert world.commitment_paradox_popup is None

    def test_break_defender_logs_commitment_paradox_resolution(self, world, executor, game_state):
        from backend.game_logic.diplomacy import declare_war
        player = world.player_nation
        world.diplomatic_states[world._make_diplo_key(player, "Prussia")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key(player, "Austria")] = "ALLIANCE"
        world.diplomatic_states[world._make_diplo_key("Austria", "Prussia")] = "PEACE"

        declare_war(world, "Prussia", "Austria")
        if world.dialogue_manager._queue and not world.pending_diplomatic_dialogue:
            world.dialogue_manager.promote_if_empty()
        paradox_episode = world.pending_diplomatic_dialogue["origin_episode_id"]

        result = executor.handle_diplomatic_dialogue_response("2", game_state)

        assert result.get("success"), result.get("message")
        paradox_events = [
            e for e in world.event_log
            if e.get("type") == "commitment_paradox_resolved"
        ]
        assert paradox_events
        latest = paradox_events[-1]
        assert latest.get("episode_id") == paradox_episode
        assert latest.get("chosen_nation") == "Prussia"
        assert latest.get("spurned_nation") == "Austria"
        dispatch_events = [
            e for e in world.pending_dispatch_events
            if e.get("type") == "commitment_paradox_resolved"
        ]
        assert dispatch_events == []
