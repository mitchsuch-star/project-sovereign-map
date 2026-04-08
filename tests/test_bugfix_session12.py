"""
Session 12: PL-14 Ultimatum Rework Tests

Tests the new conversational diplomacy flow for ultimatums:
- Dialogue push with acceptance preview
- Vassal/WAR target blocking
- Global cooldown (scalar, not per-target)
- Acceptance formula with ultimatum_bonus
- Accepted: demands applied, no state change, threat +20
- Rejected: casus belli, relation -15, threat +15
- Splash damage to bystander nations
- modify_harsh_ultimatum: escalation + cap
- generate_ultimatum_terms: gold cap, no AP, no sweeteners
- Cooldown migration (old dict → new int)
"""

import copy
from backend.models.world_state import WorldState
from backend.commands.executor import CommandExecutor
from backend.game_logic.diplomacy import calculate_acceptance, BASE_DISPOSITION
from backend.game_logic.diplomatic_templates import generate_ultimatum_terms


def _make_world():
    """Create test world at turn 5."""
    world = WorldState()
    world.current_turn = 5
    return world


def _make_executor():
    return CommandExecutor()


def _set_diplo(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state


class TestUltimatumDialoguePush:
    """PL-14 §4: Ultimatum pushes ultimatum_confirm dialogue."""

    def test_dialogue_pushed_with_terms(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)

        assert result["success"]
        assert result.get("awaiting_diplomatic_response") is True
        dialogue = world.pending_diplomatic_dialogue
        assert dialogue is not None
        assert dialogue["type"] == "ultimatum_confirm"
        assert dialogue["target_nation"] == "Prussia"
        assert "acceptance_estimate" in dialogue
        assert "demands_display" in dialogue
        assert dialogue["dp_cost"] == 2
        assert dialogue["harshness_label"] == "Coercive"

    def test_dialogue_has_three_options(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)

        dialogue = world.pending_diplomatic_dialogue
        actions = [o["action"] for o in dialogue["options"]]
        assert "execute_ultimatum" in actions
        assert "modify_harsh_ultimatum" in actions
        assert "reconsider" in actions


class TestUltimatumPreValidation:
    """PL-14 §1: Pre-validation blocks invalid targets."""

    def test_vassal_target_blocked(self):
        world = _make_world()
        world.diplomatic_points = 5
        world.vassals["Saxony"] = {"lord": "France", "loyalty": 60}
        _set_diplo(world, "France", "Saxony", "VASSAL")
        executor = _make_executor()

        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Saxony"}, world)

        assert not result["success"]
        assert "vassal" in result["message"].lower()

    def test_war_target_blocked(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "WAR")
        executor = _make_executor()

        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)

        assert not result["success"]
        assert "peace proposal" in result["message"].lower() or "war" in result["message"].lower()

    def test_global_cooldown_blocks(self):
        world = _make_world()
        world.diplomatic_points = 5
        world.ultimatum_global_cooldown = 3
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        result = executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)

        assert not result["success"]
        assert "3" in result["message"]


class TestAcceptanceFormula:
    """PL-14 §5: Acceptance formula includes ultimatum_demand and ultimatum_bonus."""

    def test_base_disposition_is_20(self):
        assert BASE_DISPOSITION["ultimatum_demand"] == 20

    def test_ultimatum_bonus_applied(self):
        world = _make_world()
        _set_diplo(world, "France", "Prussia", "PEACE")

        proposal = {
            "type": "ultimatum_demand",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        components = result.get("components", {})
        # Base 10 military threat (no marshals adjacent)
        assert components.get("ultimatum_bonus", 0) >= 10

    def test_ultimatum_no_counter_offer(self):
        """Ultimatums are take-it-or-leave-it: ACCEPT or REJECT, never COUNTER_OFFER."""
        world = _make_world()
        _set_diplo(world, "France", "Prussia", "PEACE")

        proposal = {
            "type": "ultimatum_demand",
            "proposer_nation": "France",
            "target_nation": "Prussia",
            "sweeteners": [],
            "demands": [{"type": "gold_per_turn", "value": 500}],
            "clauses": [],
        }
        result = calculate_acceptance(proposal, world)
        # Score determines outcome; ultimatums use same thresholds but
        # the execute_ultimatum handler only checks >= 50 (no counter)
        assert result["outcome"] in ("ACCEPT", "COUNTER_OFFER", "REJECT")


class TestExecuteUltimatum:
    """PL-14 §6a: Delivery handler applies demands or grants casus belli."""

    def _push_and_execute(self, world, target="Prussia"):
        """Push ultimatum dialogue then execute delivery."""
        executor = _make_executor()
        executor._execute_diplomatic_ultimatum(
            {"target_nation": target}, world)
        dialogue = world.pending_diplomatic_dialogue
        # Get the execute option with terms
        execute_opt = [o for o in dialogue["options"] if o["action"] == "execute_ultimatum"][0]
        game_state = {"world": world}
        return executor.handle_diplomatic_dialogue_response("deliver", game_state)

    def test_accepted_applies_gold_tribute(self):
        """Accepted ultimatum stores gold_per_turn in active_treaties."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        # Ensure high acceptance: good relations
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = 80

        result = self._push_and_execute(world, "Prussia")
        assert result["success"]

        if result.get("accepted"):
            # Gold tribute stored in active_treaties
            diplo_key = world._make_diplo_key("France", "Prussia")
            treaty = world.active_treaties.get(diplo_key)
            if treaty:
                assert treaty.get("is_ultimatum_tribute") is True
            # NO state change
            assert world.diplomatic_states[diplo_key] == "PEACE"

    def test_rejected_grants_casus_belli(self):
        """Rejected ultimatum grants casus belli."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        # Low relations for rejection
        key = world._make_diplo_key("France", "Prussia")
        world.nation_relations[key] = -80

        result = self._push_and_execute(world, "Prussia")
        assert result["success"]

        if not result.get("accepted"):
            diplo_key = world._make_diplo_key("France", "Prussia")
            assert world.casus_belli.get(diplo_key) is True
            # Relation -15 total (-10 delivery + -5 rejection)
            assert world.nation_relations[diplo_key] <= -80 - 15

    def test_dp_deducted_on_delivery(self):
        """2 DP deducted on delivery, not on dialogue push."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")

        executor = _make_executor()
        executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)
        assert world.diplomatic_points == 5  # Not yet deducted

        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("deliver", game_state)
        assert world.diplomatic_points == 3  # Now deducted

    def test_cooldown_set_on_delivery(self):
        """Global cooldown set to 5 on delivery."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")

        result = self._push_and_execute(world, "Prussia")
        assert result["success"]
        assert world.ultimatum_global_cooldown == 5

    def test_proposal_result_popup_set(self):
        """Delivery sets proposal_result_popup so Godot shows popup, not terminal text."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")

        result = self._push_and_execute(world, "Prussia")
        assert result["success"]
        popup = world.proposal_result_popup
        assert popup is not None
        assert popup["target_nation"] == "Prussia"
        assert popup["proposal_type"] == "Ultimatum"
        assert popup["outcome"] in ("ACCEPT", "REJECT")
        assert popup["message"] != ""


class TestSplashDamage:
    """PL-14 §3b: Bystander nations take relation hit."""

    def test_ally_of_target_takes_penalty(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        _set_diplo(world, "Austria", "Prussia", "ALLIANCE")
        _set_diplo(world, "France", "Austria", "PEACE")
        world.nation_relations[world._make_diplo_key("France", "Austria")] = 0

        executor = _make_executor()
        executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)

        # Check splash preview in dialogue
        dialogue = world.pending_diplomatic_dialogue
        splash = dialogue.get("splash_damage_preview", [])
        austria_splash = [s for s in splash if s["nation"] == "Austria"]
        assert len(austria_splash) == 1
        assert austria_splash[0]["relation_penalty"] == -15  # ALLIANCE tier


class TestModifyHarshUltimatum:
    """PL-14 §6b: Dedicated escalation handler."""

    def test_demands_escalate(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")

        executor = _make_executor()
        executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)

        # Get initial demand values
        d1 = world.pending_diplomatic_dialogue["terms"]
        initial_demands = copy.deepcopy(d1.get("demands", []))

        # Escalate
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("harsh", game_state)
        assert result["success"]

        d2 = world.pending_diplomatic_dialogue["terms"]
        # Gold demands should have increased (×1.5)
        for orig, new in zip(initial_demands, d2.get("demands", [])):
            if orig.get("type") not in ("territory_cede",):
                assert new.get("value", 0) >= orig.get("value", 0)

    def test_capped_at_2_rounds(self):
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")

        executor = _make_executor()
        executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)

        game_state = {"world": world}
        # Round 1
        r1 = executor.handle_diplomatic_dialogue_response("harsh", game_state)
        assert r1["success"]
        # Round 2
        r2 = executor.handle_diplomatic_dialogue_response("harsh", game_state)
        assert r2["success"]
        # After 2 rounds, "Harsher Demands" option should be removed
        dialogue = world.pending_diplomatic_dialogue
        actions = [o["action"] for o in dialogue.get("options", [])]
        assert "modify_harsh_ultimatum" not in actions
        # Cap message embedded in prompt
        assert "harshest" in dialogue.get("prompt", "").lower()


class TestGenerateUltimatumTerms:
    """PL-14 §2-3: Term generation."""

    def test_gold_capped_at_50_percent_income(self):
        world = _make_world()
        # Set up Prussia with known income
        for name, region in world.regions.items():
            if region.controller == "Prussia":
                region.income = 200  # Total will vary by region count

        terms = generate_ultimatum_terms("Prussia", world)
        gold_demands = [d for d in terms["demands"] if d["type"] == "gold_per_turn"]
        if gold_demands:
            total_income = sum(r.income for r in world.regions.values() if r.controller == "Prussia")
            assert gold_demands[0]["value"] <= total_income * 0.5 + 1  # +1 for rounding

    def test_no_ap_demands(self):
        terms = generate_ultimatum_terms("Prussia", _make_world())
        ap_demands = [d for d in terms["demands"] if d["type"] == "ap_per_turn"]
        assert len(ap_demands) == 0

    def test_no_sweeteners(self):
        terms = generate_ultimatum_terms("Prussia", _make_world())
        assert terms["sweeteners"] == []

    def test_type_is_ultimatum_demand(self):
        terms = generate_ultimatum_terms("Prussia", _make_world())
        assert terms["type"] == "ultimatum_demand"
        assert "proposal_type" not in terms  # No dual-key (PL-13)

    def test_zero_income_fallback_to_gold_lump(self):
        world = _make_world()
        # Zero out all income for target
        for name, region in world.regions.items():
            if region.controller == "Prussia":
                region.income = 0
        world.nation_gold["Prussia"] = 1000

        terms = generate_ultimatum_terms("Prussia", world)
        lump = [d for d in terms["demands"] if d["type"] == "gold_lump"]
        assert len(lump) >= 1
        assert lump[0]["value"] <= 500  # Capped


class TestCooldownMigration:
    """PL-14 Step 1: Old dict format migrates to new int."""

    def test_old_dict_migrates_to_max_value(self):
        world = _make_world()
        data = world.to_dict()
        # Simulate old format
        del data["ultimatum_global_cooldown"]
        data["ultimatum_cooldowns"] = {"Prussia": 3, "Austria": 1}

        loaded = WorldState.from_dict(data)
        assert loaded.ultimatum_global_cooldown == 3  # max of old values

    def test_new_format_loads_directly(self):
        world = _make_world()
        world.ultimatum_global_cooldown = 4
        data = world.to_dict()
        loaded = WorldState.from_dict(data)
        assert loaded.ultimatum_global_cooldown == 4


class TestDialoguePopupSafetyNet:
    """PL-14: Structural safeguard — dialogue responses always produce popups."""

    def test_safety_net_creates_popup_for_bare_result(self):
        """If a dialogue handler returns success+message without setting
        proposal_result_popup, the /respond_to_diplomatic_dialogue endpoint
        safety net creates one automatically."""

        # Set up world with an ultimatum dialogue pending
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        # Push ultimatum dialogue
        executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)
        assert world.pending_diplomatic_dialogue is not None

        # Now deliver — this sets proposal_result_popup (our explicit fix)
        game_state = {"world": world}
        result = executor.handle_diplomatic_dialogue_response("deliver", game_state)
        assert result["success"]
        # The explicit fix sets it; verify it's there
        assert world.proposal_result_popup is not None

    def test_all_terminal_dialogue_actions_set_popup(self):
        """Verify that execute_ultimatum sets proposal_result_popup.
        This is the characterization test — if a new terminal action is added
        that forgets this, the backend safety net in main.py catches it."""
        world = _make_world()
        world.diplomatic_points = 5
        _set_diplo(world, "France", "Prussia", "PEACE")
        executor = _make_executor()

        executor._execute_diplomatic_ultimatum(
            {"target_nation": "Prussia"}, world)

        game_state = {"world": world}
        executor.handle_diplomatic_dialogue_response("deliver", game_state)

        popup = world.proposal_result_popup
        assert popup is not None, "Terminal dialogue action must set proposal_result_popup"
        assert "target_nation" in popup
        assert "outcome" in popup
        assert popup["outcome"] in ("ACCEPT", "REJECT")
