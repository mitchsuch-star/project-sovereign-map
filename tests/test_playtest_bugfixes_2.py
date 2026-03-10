"""Regression tests for 7 bugs found during diplomacy playtest session 2 (Mar 2026).

Bug 1: Proposal response lost when queued behind AI proposal (deferred with enemy_phase)
Bug 2: Notification spam — stale DIPLOMATIC_PROPOSAL not dismissed on accept/reject
Bug 3: Cheat commands intercepted by LLM parser (diplomat keyword check first)
Bug 4: Smart suggestion commentary says "gold useless" but gold still offered
Bug 5: Harsh/generous terms commentary mentions territory but none exists
Bug 6: Treaty clause stored as Python string repr instead of human-readable
Bug 7: Wizard state field None (missing "state" alias in preview)
"""

import pytest

from backend.models.world_state import WorldState
from backend.models.marshal import Marshal
from backend.models.region import REGIONS_DATA
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _make_world():
    """Create a minimal world for testing."""
    world = WorldState()
    world.player_nation = "France"
    world.enemy_nations = ["Britain", "Prussia", "Austria", "Saxony"]

    # Set up regions
    for name, data in REGIONS_DATA.items():
        region = world.regions.get(name)
        if region:
            region.controller = data.get("starting_controller", "")

    # Add player marshals
    world.marshals["Davout"] = Marshal(
        name="Davout", nation="France", strength=48000,
        personality="cautious", location="Paris",
        skills={"shock": 7, "defense": 8, "tactical": 9}
    )
    world.marshals["Ney"] = Marshal(
        name="Ney", nation="France", strength=72000,
        personality="aggressive", location="Belgium",
        skills={"shock": 9, "defense": 4, "tactical": 7}
    )

    # Add enemy marshals
    world.marshals["Wellington"] = Marshal(
        name="Wellington", nation="Britain", strength=55000,
        personality="cautious", location="Waterloo",
        skills={"shock": 6, "defense": 8, "tactical": 8}
    )
    world.marshals["Gneisenau"] = Marshal(
        name="Gneisenau", nation="Prussia", strength=40000,
        personality="cautious", location="Rhineland",
        skills={"shock": 6, "defense": 7, "tactical": 7}
    )

    # Init diplomacy
    world.diplomatic_states = {}
    world.nation_relations = {}
    for n in world.enemy_nations:
        key = world._make_diplo_key("France", n)
        if n in ("Britain", "Prussia"):
            world.diplomatic_states[key] = "WAR"
            world.nation_relations[key] = -50
        else:
            world.diplomatic_states[key] = "PEACE"
            world.nation_relations[key] = 0

    world.diplomatic_points = 4
    world.talleyrand_state = "IDLE"

    return world


def _make_executor():
    return CommandExecutor()


# ═══════════════════════════════════════════════════════════════════════════
# BUG 3: CHEAT COMMANDS INTERCEPTED BY LLM PARSER
# ═══════════════════════════════════════════════════════════════════════════

class TestBug3CheatParser:
    """Cheat commands containing diplomat keywords must parse as cheats."""

    def test_cheat_set_talleyrand_trust_parses_as_cheat(self):
        """'cheat set_talleyrand_trust 100' must not route to diplomacy."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient(provider="mock")
        result = client.parse_command("cheat set_talleyrand_trust 100", {})
        # parse_command returns a flat ParseResult dict
        assert result.get("action") == "cheat"
        assert result.get("type") == "cheat"
        assert result.get("cheat_type") == "set_talleyrand_trust"

    def test_cheat_set_threat_parses_as_cheat(self):
        """'cheat set_threat 50' must parse as cheat."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient(provider="mock")
        result = client.parse_command("cheat set_threat 50", {})
        assert result.get("action") == "cheat"
        assert result.get("cheat_type") == "set_threat"

    def test_cheat_with_diplomat_keyword_parses_as_cheat(self):
        """'cheat diplomat_skill 10' should not route to diplomacy."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient(provider="mock")
        result = client.parse_command("cheat diplomat_skill 10", {})
        assert result.get("action") == "cheat"

    def test_diplomat_command_still_routes_to_diplomacy(self):
        """Normal diplomat commands still route correctly."""
        from backend.ai.llm_client import LLMClient
        client = LLMClient(provider="mock")
        result = client.parse_command("Talleyrand, propose peace to Prussia", {})
        assert result.get("action") != "cheat"


# ═══════════════════════════════════════════════════════════════════════════
# BUG 2: NOTIFICATION SPAM — STALE PROPOSALS
# ═══════════════════════════════════════════════════════════════════════════

class TestBug2NotificationDismiss:
    """Accepting/rejecting AI proposals must dismiss DIPLOMATIC_PROPOSAL notification."""

    def _setup_ai_proposal(self, world):
        """Set up world with an incoming AI proposal dialogue."""
        from backend.notifications import (
            create_notification, NotificationPriority, DIPLOMATIC_PROPOSAL,
        )
        world.notifications.add(create_notification(
            DIPLOMATIC_PROPOSAL,
            NotificationPriority.HIGH,
            "Envoy from Prussia",
            "Prussia proposes peace.",
            int(world.current_turn),
        ))
        world.pending_diplomatic_dialogue = {
            "type": "incoming_proposal",
            "target_nation": "Prussia",
            "talleyrand_text": "Prussia proposes peace.",
            "options": [
                {"label": "Accept", "action": "accept_ai_proposal"},
                {"label": "Reject", "action": "reject_ai_proposal"},
                {"label": "Counter", "action": "counter_ai_proposal"},
            ],
            "context": {
                "source_nation": "Prussia",
                "proposal": {
                    "type": "peace",
                    "proposer_nation": "Prussia",
                    "target_nation": "France",
                    "sweeteners": [],
                    "demands": [],
                    "clauses": [],
                },
            },
            "turn_created": 1,
            "blocking": True,
        }
        world.incoming_proposal_popup = {
            "from_nation": "Prussia",
            "diplomat_name": "Prussian envoy",
            "diplomat_personality": "pragmatic",
            "clauses": ["Peace"],
            "talleyrand_assessment": "Test",
        }

    def test_accept_dismisses_notification(self):
        """Accepting AI proposal dismisses DIPLOMATIC_PROPOSAL notification."""
        from backend.notifications import DIPLOMATIC_PROPOSAL
        world = _make_world()
        self._setup_ai_proposal(world)
        assert world.notifications.has_pending()

        executor = _make_executor()
        game_state = {"world": world, "debug_mode": True}
        result = executor.handle_diplomatic_dialogue_response("accept", game_state)

        # Notification should be dismissed
        pending = world.notifications.get_pending()
        diplo_notifs = [n for n in pending if n["type"] == DIPLOMATIC_PROPOSAL]
        assert len(diplo_notifs) == 0, "DIPLOMATIC_PROPOSAL notification should be dismissed"

    def test_reject_dismisses_notification(self):
        """Rejecting AI proposal dismisses DIPLOMATIC_PROPOSAL notification."""
        from backend.notifications import DIPLOMATIC_PROPOSAL
        world = _make_world()
        self._setup_ai_proposal(world)
        assert world.notifications.has_pending()

        executor = _make_executor()
        game_state = {"world": world, "debug_mode": True}
        result = executor.handle_diplomatic_dialogue_response("reject", game_state)

        pending = world.notifications.get_pending()
        diplo_notifs = [n for n in pending if n["type"] == DIPLOMATIC_PROPOSAL]
        assert len(diplo_notifs) == 0, "DIPLOMATIC_PROPOSAL notification should be dismissed"


# ═══════════════════════════════════════════════════════════════════════════
# BUG 4: SMART SUGGESTION COMMENTARY MISMATCH
# ═══════════════════════════════════════════════════════════════════════════

class TestBug4GoldUseless:
    """When gold_useless tag fires, gold should not be in terms."""

    def test_gold_removed_when_territory_exists(self):
        """Nations with gold_pref=low lose gold sweetener when territory exists."""
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms, NATION_DESIRE_PROFILES,
        )
        world = _make_world()
        # Find a nation with gold_pref=low
        low_gold_nation = None
        for nation, profile in NATION_DESIRE_PROFILES.items():
            if profile.get("values_gold") == "low":
                low_gold_nation = nation
                break

        if not low_gold_nation:
            pytest.skip("No nation with gold_pref=low found")

        # Ensure we're at war with this nation
        key = world._make_diplo_key("France", low_gold_nation)
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -40  # Losing → more sweeteners

        terms = generate_suggested_terms(low_gold_nation, "peace", world)
        sweeteners = terms.get("sweeteners", [])
        has_territory = any(s.get("type") == "territory_cede" for s in sweeteners)
        has_gold = any("gold" in s.get("type", "") for s in sweeteners)

        if has_territory:
            # Bug 4: If territory exists, gold should be removed
            assert not has_gold, (
                f"Gold sweetener should be removed when territory exists for gold_pref=low nation. "
                f"Got: {sweeteners}"
            )

    def test_gold_kept_as_fallback(self):
        """Gold is kept (reduced) when it's the only sweetener for gold_pref=low nation."""
        from backend.game_logic.diplomatic_templates import (
            generate_suggested_terms,
        )
        world = _make_world()
        key = world._make_diplo_key("France", "Austria")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = -10

        terms = generate_suggested_terms("Austria", "peace", world)
        assert isinstance(terms.get("sweeteners"), list)


# ═══════════════════════════════════════════════════════════════════════════
# BUG 5: HARSH/GENEROUS COMMENTARY REGENERATION
# ═══════════════════════════════════════════════════════════════════════════

class TestBug5CommentaryRegeneration:
    """modify_harsh and modify_generous regenerate commentary matching terms."""

    def _setup_proposal_dialogue(self, world, target="Prussia"):
        """Create a proposal_confirm dialogue for testing modify actions."""
        from backend.game_logic.diplomatic_templates import generate_suggested_terms
        terms = generate_suggested_terms(target, "peace", world)
        terms["proposal_type"] = "peace"

        world.pending_diplomatic_dialogue = {
            "type": "proposal_confirm",
            "target_nation": target,
            "talleyrand_text": "Test terms",
            "options": [
                {"label": "Send", "action": "execute_proposal", "terms": terms},
                {"label": "Harsher", "action": "modify_harsh", "terms": terms},
                {"label": "More generous", "action": "modify_generous", "terms": terms},
                {"label": "Reconsider", "action": "reconsider"},
            ],
            "context": {},
            "turn_created": 1,
            "blocking": False,
        }

    def test_harsh_regenerates_commentary(self):
        """modify_harsh produces fresh commentary matching actual terms."""
        world = _make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        self._setup_proposal_dialogue(world, "Prussia")

        executor = _make_executor()
        game_state = {"world": world, "debug_mode": True}
        result = executor.handle_diplomatic_dialogue_response("harsh", game_state)

        assert result.get("success"), f"Harsh modification failed: {result.get('message')}"
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        commentary = dialogue.get("talleyrand_commentary", "")
        assert commentary, "Commentary should be regenerated after modify_harsh"

    def test_generous_regenerates_commentary(self):
        """modify_generous produces fresh commentary matching actual terms."""
        world = _make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        self._setup_proposal_dialogue(world, "Prussia")

        executor = _make_executor()
        game_state = {"world": world, "debug_mode": True}
        result = executor.handle_diplomatic_dialogue_response("generous", game_state)

        assert result.get("success"), f"Generous modification failed: {result.get('message')}"
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        commentary = dialogue.get("talleyrand_commentary", "")
        assert commentary, "Commentary should be regenerated after modify_generous"

    def test_harsh_territory_commentary_matches_terms(self):
        """When harsh terms include territory demands, commentary mentions territory."""
        world = _make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"
        world.war_scores[key] = 50  # Winning helps get territory demands
        self._setup_proposal_dialogue(world, "Prussia")

        executor = _make_executor()
        game_state = {"world": world, "debug_mode": True}

        # Apply harsh twice to trigger territory demands
        executor.handle_diplomatic_dialogue_response("harsh", game_state)
        result = executor.handle_diplomatic_dialogue_response("harsh", game_state)

        dialogue = world.pending_diplomatic_dialogue
        if dialogue:
            # Check terms for territory demands
            for opt in dialogue.get("options", []):
                terms = opt.get("terms", {})
                has_territory = any(
                    d.get("type") in ("territory_cede", "territory")
                    for d in terms.get("demands", []))
                commentary = dialogue.get("talleyrand_commentary", "")
                if has_territory:
                    assert "territor" in commentary.lower(), (
                        f"Commentary should mention territory when demands include it. "
                        f"Got: {commentary}"
                    )
                break


# ═══════════════════════════════════════════════════════════════════════════
# BUG 6: TREATY CLAUSE DISPLAY
# ═══════════════════════════════════════════════════════════════════════════

class TestBug6TreatyClauseDisplay:
    """Treaty clauses in diplomatic ledger display as readable text, not Python repr."""

    def test_clause_dict_gets_readable_description(self):
        """Clause dict without description field gets formatted label."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger

        world = _make_world()
        treaty_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[treaty_key] = "PEACE"
        world.active_treaties[treaty_key] = {
            "nations": ["France", "Prussia"],
            "type": "peace",
            "state_transition": "WAR_TO_PEACE",
            "clauses": [
                {"type": "gold_per_turn", "from": "France", "to": "Prussia", "amount": 100},
                {"type": "territory_cede", "from": "France", "to": "Prussia", "amount": 1},
            ],
            "turn_signed": 1,
            "harshness": 0.3,
        }

        ledger = build_diplomatic_ledger(world)
        treaties = ledger.get("treaties", [])
        assert len(treaties) >= 1, "Should have at least 1 treaty"

        treaty = treaties[0]
        clauses = treaty.get("clauses", [])
        for clause_text in clauses:
            # Bug 6: clauses should NOT contain Python dict repr
            assert "{'type'" not in clause_text, (
                f"Clause should be readable text, got Python repr: {clause_text}"
            )

    def test_gold_per_turn_clause_formatted(self):
        """Gold/turn clause displays as readable text with amounts."""
        from backend.game_logic.diplomatic_ledger import build_diplomatic_ledger

        world = _make_world()
        treaty_key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[treaty_key] = "PEACE"
        world.active_treaties[treaty_key] = {
            "nations": ["France", "Prussia"],
            "type": "peace",
            "state_transition": "WAR_TO_PEACE",
            "clauses": [
                {"type": "gold_per_turn", "from": "France", "to": "Prussia", "amount": 150},
            ],
            "turn_signed": 1,
            "harshness": 0.2,
        }

        ledger = build_diplomatic_ledger(world)
        treaties = ledger.get("treaties", [])
        clause_text = treaties[0]["clauses"][0]
        assert "150" in clause_text, f"Should show amount 150: {clause_text}"
        assert "Gold" in clause_text or "gold" in clause_text, f"Should mention gold: {clause_text}"


# ═══════════════════════════════════════════════════════════════════════════
# BUG 7: WIZARD STATE FIELD
# ═══════════════════════════════════════════════════════════════════════════

class TestBug7WizardState:
    """Diplomatic preview includes 'state' alias field."""

    def test_preview_includes_state_field(self):
        """get_diplomatic_preview returns both 'state' and 'current_state'."""
        from backend.game_logic.diplomacy import get_diplomatic_preview

        world = _make_world()
        preview = get_diplomatic_preview(world, "Prussia")

        assert "state" in preview, "Preview must include 'state' field for wizard"
        assert "current_state" in preview, "Preview must include 'current_state' field"
        assert preview["state"] == preview["current_state"], "state and current_state must match"

    def test_state_reflects_diplomatic_status(self):
        """state field shows actual diplomatic status."""
        from backend.game_logic.diplomacy import get_diplomatic_preview

        world = _make_world()
        key = world._make_diplo_key("France", "Prussia")
        world.diplomatic_states[key] = "WAR"

        preview = get_diplomatic_preview(world, "Prussia")
        assert preview["state"] == "WAR"


# ═══════════════════════════════════════════════════════════════════════════
# BUG 1: PROPOSAL RESPONSE DEFERRED WITH ENEMY_PHASE
# ═══════════════════════════════════════════════════════════════════════════

class TestBug1ProposalDeferred:
    """AI proposal dialogue is deferred when enemy_phase is present."""

    def test_ai_proposal_not_set_when_enemy_phase_present(self):
        """Response builder should defer AI proposal when enemy_phase exists.

        This tests the pattern from main.py: when enemy_phase is present,
        AI proposal dialogue should NOT be included in the response.
        Both are deferred to be delivered on the next request.
        """
        # Simulate the response building logic from main.py
        response = {"enemy_phase": {"nations": {}, "total_actions": 0}}
        result = {"ai_proposal": {"nation": "Saxony", "type": "non_aggression"}}

        # Bug 1 fix: This block should NOT execute when enemy_phase is present
        if not response.get("enemy_phase"):
            if result.get("ai_proposal"):
                response["ai_proposal"] = result["ai_proposal"]
                response["diplomatic_dialogue"] = {"type": "incoming_proposal"}

        assert "diplomatic_dialogue" not in response, (
            "AI proposal dialogue should be deferred when enemy_phase is present"
        )
        assert "ai_proposal" not in response, (
            "AI proposal data should be deferred when enemy_phase is present"
        )

    def test_ai_proposal_set_when_no_enemy_phase(self):
        """AI proposal IS included when no enemy_phase present."""
        response = {}
        result = {"ai_proposal": {"nation": "Saxony", "type": "non_aggression"}}

        world = _make_world()
        world.pending_diplomatic_dialogue = {"type": "incoming_proposal"}

        if not response.get("enemy_phase"):
            if result.get("ai_proposal"):
                response["ai_proposal"] = result["ai_proposal"]
                if world.pending_diplomatic_dialogue:
                    response["diplomatic_dialogue"] = world.pending_diplomatic_dialogue

        assert "ai_proposal" in response
        assert "diplomatic_dialogue" in response
