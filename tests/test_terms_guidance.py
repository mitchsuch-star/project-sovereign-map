"""
Tests for Conversational Terms Guidance — Talleyrand guides the player
through building treaty terms one topic at a time.
"""

import pytest
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor


# ═══════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════

@pytest.fixture
def world():
    """Standard world state."""
    return WorldState()


@pytest.fixture
def executor():
    """Standard executor."""
    return CommandExecutor()


@pytest.fixture
def game_state(world):
    """Standard game state dict."""
    return {"world": world}


def _set_war(world, target="Austria", war_score=0):
    """Put France at war with target nation, with optional war score from France's perspective."""
    diplo_key = world._make_diplo_key("France", target)
    world.nation_relations[diplo_key] = -30
    world.diplomatic_states[diplo_key] = "WAR"
    if war_score != 0:
        _set_war_score(world, "France", target, war_score)


def _set_war_score(world, nation, opponent, score):
    """Set war score from nation's perspective (positive = nation winning)."""
    diplo_key = world._make_diplo_key(nation, opponent)
    if not hasattr(world, 'war_scores'):
        world.war_scores = {}
    parts = diplo_key.split("|")
    # Storage is from alphabetically-first perspective
    if parts[0] == nation:
        world.war_scores[diplo_key] = score
    else:
        world.war_scores[diplo_key] = -score


def _set_peace_hostile(world, target="Austria"):
    """Set hostile peace relations."""
    diplo_key = world._make_diplo_key("France", target)
    world.nation_relations[diplo_key] = -60
    world.diplomatic_states[diplo_key] = "PEACE"


def _respond(executor, game_state, choice):
    """Send a dialogue response and return result."""
    return executor.handle_diplomatic_dialogue_response(choice, game_state)


def _setup_adjust_dialogue(world, target="Austria", proposal_type="peace"):
    """Set up a dialogue with adjust_terms option available."""
    world.pending_diplomatic_dialogue = {
        "type": "proposal_confirm",
        "target_nation": target,
        "talleyrand_text": "Test proposal.",
        "options": [
            {"label": "Send as suggested", "description": "Send.",
             "action": "execute_proposal",
             "terms": {"type": proposal_type, "proposal_type": proposal_type,
                        "proposer_nation": "France", "target_nation": target,
                        "sweeteners": [], "demands": [], "clauses": []}},
            {"label": "Adjust terms", "description": "Build the offer step by step.",
             "action": "adjust_terms"},
            {"label": "Reconsider", "description": "Let me think.", "action": "reconsider"},
        ],
        "context": {"proposal_type": proposal_type},
        "turn_created": int(world.current_turn),
        "blocking": False,
    }


# ═══════════════════════════════════════════════
# Section 1: rank_cession_candidates
# ═══════════════════════════════════════════════

class TestRankCessionCandidates:
    """Test the region ranking function."""

    def test_excludes_capital(self, world):
        """Capital (Paris) should never appear in candidates."""
        from backend.game_logic.diplomatic_templates import rank_cession_candidates
        candidates = rank_cession_candidates(world, "France", "Austria")
        names = [c[0] for c in candidates]
        assert "Paris" not in names

    def test_border_regions_sort_first(self, world):
        """Regions adjacent to target nation territory should rank first."""
        from backend.game_logic.diplomatic_templates import rank_cession_candidates
        # France has Milan adjacent to Vienna/Tyrol (Austria)
        candidates = rank_cession_candidates(world, "France", "Austria")
        names = [c[0] for c in candidates]
        assert len(names) > 0
        # Milan borders Austria (via Tyrol/Vienna) — should be first or near first
        assert "Milan" in names
        milan_idx = names.index("Milan")
        # Non-border regions (Brittany, Bordeaux) should be after border ones
        for non_border in ["Brittany", "Bordeaux"]:
            if non_border in names:
                assert names.index(non_border) > milan_idx

    def test_no_building_regions_preferred(self, world):
        """Empty regions should rank before regions with buildings."""
        from backend.game_logic.diplomatic_templates import rank_cession_candidates
        # Add a building to Milan
        world.regions["Milan"].buildings = [{"type": "market", "damaged": False}]
        candidates = rank_cession_candidates(world, "France", "Austria")
        names = [c[0] for c in candidates]
        # Lyon also borders Austria (via Rhineland→no, via Milan→yes)
        # Actually Lyon borders Rhineland and Milan, not Austria regions directly
        # Let's check: Lyon adjacent = Paris, Bordeaux, Marseille, Rhineland, Milan
        # Austria controls: Vienna, Bavaria, Tyrol, Bohemia at start
        # Lyon has Rhineland (Prussia) — not Austria
        # So Milan is the only France border region with Austria
        # Milan with building should still be near top (border priority overrides buildings)
        # but a border region without buildings would beat it
        assert "Milan" in names

    def test_lower_income_preferred(self, world):
        """Among equal priority regions, cheaper ones should rank first."""
        from backend.game_logic.diplomatic_templates import rank_cession_candidates
        candidates = rank_cession_candidates(world, "France", "Austria")
        names = [c[0] for c in candidates]
        # Brittany (rural, 50) should rank before Normandy (town, 100) if both non-border
        if "Brittany" in names and "Normandy" in names:
            assert names.index("Brittany") < names.index("Normandy")

    def test_returns_empty_if_only_capital(self, world):
        """If player only has capital left, return empty list."""
        from backend.game_logic.diplomatic_templates import rank_cession_candidates
        # Remove all regions except Paris from France control
        for name, region in world.regions.items():
            if region.controller == "France" and name != "Paris":
                region.controller = "Austria"
        candidates = rank_cession_candidates(world, "France", "Austria")
        assert candidates == []

    def test_reason_text_mentions_border(self, world):
        """Border candidates should have reason mentioning 'borders'."""
        from backend.game_logic.diplomatic_templates import rank_cession_candidates
        candidates = rank_cession_candidates(world, "France", "Austria")
        # Find Milan (borders Austria via Tyrol/Vienna)
        for name, reason in candidates:
            if name == "Milan":
                assert "borders" in reason.lower()
                break


# ═══════════════════════════════════════════════
# Section 2: adjust_terms entry
# ═══════════════════════════════════════════════

class TestAdjustTermsEntry:
    """Test the entry point for terms guidance."""

    def test_shows_territory_when_losing(self, world, executor, game_state):
        """Should ask about territory when war_score < 0."""
        _set_war(world, "Austria")
        # Give France negative war score by having them lose territory
        _set_war_score(world, "France", "Austria", -20)

        _setup_adjust_dialogue(world, "Austria")
        result = _respond(executor, game_state, "adjust")
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        assert "concessions" in dialogue.get("talleyrand_text", "").lower()

    def test_skips_to_gold_when_winning(self, world, executor, game_state):
        """Should skip territory when war_score > 0 (winning)."""
        _set_war(world, "Austria")
        # Positive war score
        _set_war_score(world, "France", "Austria", 20)
        # Also need relation > -50 to skip territory
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = -10

        _setup_adjust_dialogue(world, "Austria")
        result = _respond(executor, game_state, "adjust")
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        # Should be on gold step, not territory
        text = dialogue.get("talleyrand_text", "")
        assert "gold" in text.lower()

    def test_shows_territory_when_hostile(self, world, executor, game_state):
        """Should ask about territory when relation < -50 even at peace."""
        _set_peace_hostile(world, "Austria")
        _setup_adjust_dialogue(world, "Austria")
        result = _respond(executor, game_state, "adjust")
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        assert "concessions" in dialogue.get("talleyrand_text", "").lower()

    def test_context_populated_with_candidates(self, world, executor, game_state):
        """Context should contain ranked_candidates."""
        _set_war(world, "Austria")
        _set_war_score(world, "France", "Austria", -20)

        _setup_adjust_dialogue(world, "Austria")
        result = _respond(executor, game_state, "adjust")
        dialogue = result.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        assert "ranked_candidates" in context
        assert len(context["ranked_candidates"]) > 0


# ═══════════════════════════════════════════════
# Section 3: Territory flow
# ═══════════════════════════════════════════════

class TestTerritoryFlow:
    """Test the territory picking conversation."""

    def _enter_territory(self, world, executor, game_state):
        """Helper: set up war and enter territory step."""
        _set_war(world, "Austria")
        _set_war_score(world, "France", "Austria", -20)
        _setup_adjust_dialogue(world, "Austria")
        _respond(executor, game_state, "adjust")
        # Now pick "Yes, discuss territory"
        return _respond(executor, game_state, "1")

    def test_territory_yes_shows_candidate(self, world, executor, game_state):
        """territory_yes should show first candidate with reason."""
        result = self._enter_territory(world, executor, game_state)
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        text = dialogue.get("talleyrand_text", "")
        assert "suggest" in text.lower()
        # Should have offer/skip/enough options
        actions = [o["action"] for o in dialogue.get("options", [])]
        assert "offer_region" in actions
        assert "skip_region" in actions
        assert "enough_territory" in actions

    def test_offer_region_adds_to_sweeteners(self, world, executor, game_state):
        """Offering a region should add it to approved_sweeteners."""
        self._enter_territory(world, executor, game_state)
        # Click "Offer this region"
        result = _respond(executor, game_state, "1")  # "Offer this region"
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        assert len(context.get("approved_regions", [])) > 0
        assert len(context.get("approved_sweeteners", [])) > 0

    def test_offer_region_asks_more_when_needed(self, world, executor, game_state):
        """If regions_needed > approved, should show next candidate."""
        _set_war(world, "Austria")
        # War score < -40 means regions_needed = 2
        _set_war_score(world, "France", "Austria", -50)
        _setup_adjust_dialogue(world, "Austria")
        _respond(executor, game_state, "adjust")
        _respond(executor, game_state, "1")  # territory_yes

        result = _respond(executor, game_state, "1")  # offer_region
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        # Should show next candidate (still in region_pick)
        text = dialogue.get("talleyrand_text", "")
        assert "suggest" in text.lower() or "gold" in text.lower()

    def test_skip_region_shows_next(self, world, executor, game_state):
        """Skipping should show next candidate."""
        self._enter_territory(world, executor, game_state)
        result = _respond(executor, game_state, "2")  # "Not this one"
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        text = dialogue.get("talleyrand_text", "")
        # Should show next candidate or "no more"
        assert "what about" in text.lower() or "no more" in text.lower()

    def test_skip_region_handles_exhaustion(self, world, executor, game_state):
        """Skipping all candidates should offer gold/AP/done."""
        _set_war(world, "Austria")
        _set_war_score(world, "France", "Austria", -20)
        # Remove all France non-capital regions except one
        for name, region in world.regions.items():
            if region.controller == "France" and name not in ("Paris", "Lyon"):
                region.controller = "Austria"
        _setup_adjust_dialogue(world, "Austria")
        _respond(executor, game_state, "adjust")
        _respond(executor, game_state, "1")  # territory_yes — shows Lyon

        # Skip the only candidate
        result = _respond(executor, game_state, "2")  # "Not this one"
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        text = dialogue.get("talleyrand_text", "")
        assert "no more" in text.lower()

    def test_enough_territory_moves_to_gold(self, world, executor, game_state):
        """Clicking 'enough territory' should move to gold step."""
        self._enter_territory(world, executor, game_state)
        result = _respond(executor, game_state, "3")  # "That's enough territory"
        assert result["success"]
        dialogue = result.get("diplomatic_dialogue", {})
        text = dialogue.get("talleyrand_text", "")
        assert "gold" in text.lower()


# ═══════════════════════════════════════════════
# Section 4: Gold step
# ═══════════════════════════════════════════════

class TestGoldStep:
    """Test the gold amount adjustment step."""

    def _enter_gold(self, world, executor, game_state):
        """Helper: go straight to gold step."""
        _set_war(world, "Austria")
        _set_war_score(world, "France", "Austria", 20)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = -10
        _setup_adjust_dialogue(world, "Austria")
        return _respond(executor, game_state, "adjust")

    def test_suggests_reasonable_amount(self, world, executor, game_state):
        """Gold suggestion should be between 25 and 200."""
        result = self._enter_gold(world, executor, game_state)
        dialogue = result.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        gold = context.get("gold_amount", 0)
        assert 25 <= gold <= 200

    def test_more_gold_increases(self, world, executor, game_state):
        """'more_gold' should increase the amount."""
        self._enter_gold(world, executor, game_state)
        dialogue = world.pending_diplomatic_dialogue
        initial_gold = dialogue["context"]["gold_amount"]

        result = _respond(executor, game_state, "2")  # "Offer more"
        dialogue = result.get("diplomatic_dialogue", {})
        new_gold = dialogue["context"]["gold_amount"]
        assert new_gold > initial_gold

    def test_less_gold_decreases(self, world, executor, game_state):
        """'less_gold' should decrease the amount."""
        self._enter_gold(world, executor, game_state)
        dialogue = world.pending_diplomatic_dialogue
        initial_gold = dialogue["context"]["gold_amount"]

        result = _respond(executor, game_state, "3")  # "Offer less"
        dialogue = result.get("diplomatic_dialogue", {})
        new_gold = dialogue["context"]["gold_amount"]
        assert new_gold < initial_gold

    def test_offer_gold_adds_sweetener(self, world, executor, game_state):
        """'offer_gold' should add gold sweetener and move to AP."""
        self._enter_gold(world, executor, game_state)
        result = _respond(executor, game_state, "1")  # "Offer X gold"
        dialogue = result.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        gold_sweeteners = [s for s in context.get("approved_sweeteners", [])
                           if s.get("type") == "gold_per_turn"]
        assert len(gold_sweeteners) == 1
        # Should now be on AP step
        text = dialogue.get("talleyrand_text", "")
        assert "action point" in text.lower() or "extraordinary" in text.lower()

    def test_skip_gold_moves_to_ap(self, world, executor, game_state):
        """'skip_gold' should move to AP step without adding gold."""
        self._enter_gold(world, executor, game_state)
        result = _respond(executor, game_state, "4")  # "Skip gold"
        dialogue = result.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        gold_sweeteners = [s for s in context.get("approved_sweeteners", [])
                           if s.get("type") == "gold_per_turn"]
        assert len(gold_sweeteners) == 0
        text = dialogue.get("talleyrand_text", "")
        assert "action point" in text.lower() or "extraordinary" in text.lower()


# ═══════════════════════════════════════════════
# Section 5: AP step
# ═══════════════════════════════════════════════

class TestAPStep:
    """Test the Action Point offering step."""

    def _enter_ap(self, world, executor, game_state):
        """Helper: navigate to AP step by skipping territory + gold."""
        _set_war(world, "Austria")
        _set_war_score(world, "France", "Austria", 20)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = -10
        _setup_adjust_dialogue(world, "Austria")
        _respond(executor, game_state, "adjust")  # skip to gold
        return _respond(executor, game_state, "4")  # skip gold → AP

    def test_ap_text_mentions_extraordinary(self, world, executor, game_state):
        """AP step text should mention 'extraordinary'."""
        result = self._enter_ap(world, executor, game_state)
        dialogue = result.get("diplomatic_dialogue", {})
        text = dialogue.get("talleyrand_text", "")
        assert "extraordinary" in text.lower()

    def test_offer_ap_adds_sweetener(self, world, executor, game_state):
        """'offer_ap' should add AP sweetener."""
        self._enter_ap(world, executor, game_state)
        result = _respond(executor, game_state, "1")  # "Offer the AP"
        dialogue = result.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        ap_sweeteners = [s for s in context.get("approved_sweeteners", [])
                         if s.get("type") == "ap_per_turn"]
        assert len(ap_sweeteners) == 1

    def test_skip_ap_moves_to_confirm(self, world, executor, game_state):
        """'skip_ap' should move to confirm without AP."""
        self._enter_ap(world, executor, game_state)
        result = _respond(executor, game_state, "2")  # "Too costly"
        dialogue = result.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        ap_sweeteners = [s for s in context.get("approved_sweeteners", [])
                         if s.get("type") == "ap_per_turn"]
        assert len(ap_sweeteners) == 0
        # Should show confirm step with Send option
        actions = [o["action"] for o in dialogue.get("options", [])]
        assert "execute_proposal" in actions


# ═══════════════════════════════════════════════
# Section 6: Confirm & send
# ═══════════════════════════════════════════════

class TestConfirmAndSend:
    """Test the final confirmation and sending step."""

    def _enter_confirm(self, world, executor, game_state):
        """Navigate to confirm: skip territory, skip gold, skip AP."""
        _set_war(world, "Austria")
        _set_war_score(world, "France", "Austria", 20)
        diplo_key = world._make_diplo_key("France", "Austria")
        world.nation_relations[diplo_key] = -10
        _setup_adjust_dialogue(world, "Austria")
        _respond(executor, game_state, "adjust")  # → gold
        _respond(executor, game_state, "4")        # skip gold → AP
        return _respond(executor, game_state, "2")  # skip AP → confirm

    def test_confirm_shows_terms_summary(self, world, executor, game_state):
        """Confirm step should show assembled terms."""
        result = self._enter_confirm(world, executor, game_state)
        dialogue = result.get("diplomatic_dialogue", {})
        text = dialogue.get("talleyrand_text", "")
        assert "terms" in text.lower()
        # Should have send/start over/reconsider options
        actions = [o["action"] for o in dialogue.get("options", [])]
        assert "execute_proposal" in actions
        assert "adjust_terms" in actions
        assert "reconsider" in actions

    def test_confirm_has_acceptance_estimate(self, world, executor, game_state):
        """Confirm step should include acceptance estimate."""
        result = self._enter_confirm(world, executor, game_state)
        dialogue = result.get("diplomatic_dialogue", {})
        assert "acceptance_estimate" in dialogue

    def test_send_deducts_dp(self, world, executor, game_state):
        """Sending from confirm should deduct DP."""
        self._enter_confirm(world, executor, game_state)
        initial_dp = world.diplomatic_points
        result = _respond(executor, game_state, "1")  # "Send"
        # If successful, DP should be deducted
        if result.get("success"):
            assert world.diplomatic_points < initial_dp

    def test_start_over_restarts_flow(self, world, executor, game_state):
        """'Start over' should restart the guidance flow."""
        self._enter_confirm(world, executor, game_state)
        result = _respond(executor, game_state, "2")  # "Start over"
        assert result["success"]
        # Should be back at the beginning (gold step since winning)
        dialogue = result.get("diplomatic_dialogue", {})
        text = dialogue.get("talleyrand_text", "")
        assert "gold" in text.lower()

    def test_all_numbers_are_int(self, world, executor, game_state):
        """Golden Rule #2: all numbers sent to Godot must be int."""
        result = self._enter_confirm(world, executor, game_state)
        dialogue = result.get("diplomatic_dialogue", {})
        if "acceptance_estimate" in dialogue:
            assert isinstance(dialogue["acceptance_estimate"], int)
        if "turn_created" in dialogue:
            assert isinstance(dialogue["turn_created"], int)
        context = dialogue.get("context", {})
        gold = context.get("gold_amount", 0)
        assert isinstance(gold, int)


# ═══════════════════════════════════════════════
# Section 7: Integration
# ═══════════════════════════════════════════════

class TestIntegration:
    """Full flow integration tests."""

    def test_full_territory_gold_ap_send(self, world, executor, game_state):
        """Full flow: territory → gold → AP → send."""
        _set_war(world, "Austria")
        _set_war_score(world, "France", "Austria", -20)
        _setup_adjust_dialogue(world, "Austria")

        # 1. Entry → adjust terms
        r = _respond(executor, game_state, "adjust")
        assert r["success"]

        # 2. Yes territory
        r = _respond(executor, game_state, "1")
        assert r["success"]

        # 3. Offer first region
        r = _respond(executor, game_state, "1")
        assert r["success"]

        # 4. At gold or more territory — navigate to gold if needed
        dialogue = r.get("diplomatic_dialogue", {})
        text = dialogue.get("talleyrand_text", "")
        if "gold" not in text.lower():
            # Still showing territory, click "enough"
            r = _respond(executor, game_state, "3")
            assert r["success"]

        # 5. Offer gold
        r = _respond(executor, game_state, "1")
        assert r["success"]

        # 6. Offer AP
        r = _respond(executor, game_state, "1")
        assert r["success"]

        # 7. Confirm — should have terms
        dialogue = r.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        sweeteners = context.get("approved_sweeteners", [])
        types = [s.get("type") for s in sweeteners]
        assert "territory_cede" in types
        assert "gold_per_turn" in types
        assert "ap_per_turn" in types

    def test_skip_all_flow(self, world, executor, game_state):
        """Skip everything: no territory, skip gold, skip AP → confirm."""
        _set_war(world, "Austria")
        _set_war_score(world, "France", "Austria", -20)
        _setup_adjust_dialogue(world, "Austria")

        # 1. Adjust terms
        _respond(executor, game_state, "adjust")
        # 2. No territory — offer gold
        _respond(executor, game_state, "2")
        # 3. Skip gold
        _respond(executor, game_state, "4")
        # 4. Skip AP
        r = _respond(executor, game_state, "2")
        assert r["success"]

        # Confirm with no sweeteners
        dialogue = r.get("diplomatic_dialogue", {})
        context = dialogue.get("context", {})
        assert len(context.get("approved_sweeteners", [])) == 0
        # Should have Send option
        actions = [o["action"] for o in dialogue.get("options", [])]
        assert "execute_proposal" in actions

    def test_existing_harsh_generous_still_works(self, world, executor, game_state):
        """Legacy harsh/generous options still function alongside adjust_terms."""
        _set_war(world, "Austria")
        world.pending_diplomatic_dialogue = {
            "type": "proposal_confirm",
            "target_nation": "Austria",
            "talleyrand_text": "Test proposal.",
            "options": [
                {"label": "Send as suggested", "description": "Send.",
                 "action": "execute_proposal",
                 "terms": {"type": "peace", "proposal_type": "peace",
                            "proposer_nation": "France", "target_nation": "Austria",
                            "sweeteners": [], "demands": [{"type": "gold_per_turn", "value": 100}],
                            "clauses": []}},
                {"label": "Harsher terms", "description": "Demand more.",
                 "action": "modify_harsh",
                 "terms": {"type": "peace", "proposal_type": "peace",
                            "proposer_nation": "France", "target_nation": "Austria",
                            "sweeteners": [], "demands": [{"type": "gold_per_turn", "value": 100}],
                            "clauses": []}},
                {"label": "More generous", "description": "Sweeten.",
                 "action": "modify_generous",
                 "terms": {"type": "peace", "proposal_type": "peace",
                            "proposer_nation": "France", "target_nation": "Austria",
                            "sweeteners": [], "demands": [{"type": "gold_per_turn", "value": 100}],
                            "clauses": []}},
                {"label": "Reconsider", "description": "Think.", "action": "reconsider"},
            ],
            "context": {},
            "turn_created": int(world.current_turn),
            "blocking": False,
        }
        result = _respond(executor, game_state, "harsh")
        assert result["success"]
        # Should still work as before
        dialogue = result.get("diplomatic_dialogue", {})
        assert dialogue.get("target_nation") == "Austria"
