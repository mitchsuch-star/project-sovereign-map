"""W6-8 — The Spoils of War: estate confiscation (EXP-E1).

Wave 6 slice 8 (docs/WAVE6_FUN_FACTOR_SPEC.md §10): conquering the province
that sustains an ENEMY marshal's estate poses a second capture choice —
confiscate the estate (2x effective-income windfall, -10 relations, the
capturer's cautious marshals -1 trust, the region becomes endowable) or
respect the title (the estate stays on the marshal's rolls; +5 acceptance
with his nation, cap one per nation, serialized world.respected_estates).

GR5: the AI conqueror applies a deterministic rule instead of the popup —
confiscate when at war with the estate-holder's nation, respect otherwise.

The second question rides the same capture_choice pipeline (stage="estate")
and carries a dialogue_id minted from the W6-0 counter, so a stale popup
answer can never resolve the wrong matter.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.commands.executor import CommandExecutor
from backend.game_logic.diplomacy import calculate_acceptance
from backend.game_logic.dotation import (
    CONFISCATION_CAUTIOUS_TRUST,
    CONFISCATION_INCOME_MULT,
    CONFISCATION_RELATIONS_PENALTY,
    GRACE_TURNS,
    RESPECT_ACCEPTANCE_BONUS,
    apply_ai_estate_rule,
    apply_estate_respect,
    check_estate_eligibility,
    find_enemy_estate_holder,
    get_satisfaction,
    is_estate_respected,
    prune_respected_estates,
    respected_estate_mod,
)
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "europe_1805.json"
)


@pytest.fixture(scope="module")
def world1805():
    """Read-only module-scoped 1805 campaign — mutating tests copy it."""
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


@pytest.fixture
def executor():
    return CommandExecutor()


def _austrian_marshal(world):
    return next(m for m in world.marshals.values()
                if m.nation == "Austria" and m.strength > 0)


def _estate_region(world, holder, controller=None):
    """Give `holder` an estate on soil his nation controls (state-level,
    like test_economy_es7_dotation's _endow), then optionally flip the
    province to `controller` (simulating the capture)."""
    region = next(
        r for r in world.regions.values()
        if r.controller == holder.nation and not r.is_capital
        and r.region_type != "capital" and r.income_value > 0
    )
    holder.dotation_regions.append(region.name)
    if controller:
        region.controller = controller
        world.invalidate_active_nations_cache()
    return region


def _seed_stage1(world, region, capturer="Ney", prev="Austria"):
    world.pending_capture_choice = {
        "region": region.name,
        "capturer": capturer,
        "previous_controller": prev,
    }


def _resolve_stage1(executor, world, choice="secure"):
    return executor.handle_capture_choice(choice, {"world": world})


# ════════════════════════════════════════════════════════════════════════
# The second question mounts only on estate soil
# ════════════════════════════════════════════════════════════════════════


class TestEstateChoiceMounting:
    def test_non_estate_capture_has_no_second_stage(self, world, executor):
        region = next(r for r in world.regions.values()
                      if r.controller == "Austria" and not r.is_capital)
        region.controller = "France"
        world.invalidate_active_nations_cache()
        _seed_stage1(world, region)
        result = _resolve_stage1(executor, world)
        assert result["success"] is True
        assert world.pending_capture_choice is None
        assert "pending_capture_choice" not in result

    def test_estate_capture_mounts_second_stage(self, world, executor):
        holder = _austrian_marshal(world)
        region = _estate_region(world, holder, controller="France")
        _seed_stage1(world, region)
        result = _resolve_stage1(executor, world)
        assert result["success"] is True
        pending = world.pending_capture_choice
        assert pending is not None
        assert pending["stage"] == "estate"
        assert pending["estate_holder"] == holder.name
        assert pending["estate_holder_nation"] == "Austria"
        assert pending["options"] == ["confiscate", "respect"]
        assert isinstance(pending["dialogue_id"], int)
        assert pending["windfall"] == int(
            CONFISCATION_INCOME_MULT * region.get_effective_income())
        # The result re-attaches the question for the popup chain
        assert result["pending_capture_choice"] is True
        assert result["capture_data"] is pending
        assert holder.name in result["message"]

    def test_own_estate_recapture_asks_nothing(self, world, executor):
        """Recapturing a PLAYER marshal's occupied estate is a rescue, not
        a choice — find_enemy_estate_holder excludes own-nation marshals."""
        french = next(m for m in world.marshals.values()
                      if m.nation == "France" and m.strength > 0)
        region = next(r for r in world.regions.values()
                      if r.controller == "France" and not r.is_capital
                      and r.region_type != "capital")
        french.dotation_regions.append(region.name)
        assert find_enemy_estate_holder(world, region.name, "France") is None

    def test_dialogue_id_minted_from_w6_0_counter(self, world, executor):
        holder = _austrian_marshal(world)
        region = _estate_region(world, holder, controller="France")
        before = world.dialogue_manager._next_dialogue_id
        _seed_stage1(world, region)
        _resolve_stage1(executor, world)
        assert world.pending_capture_choice["dialogue_id"] == before
        assert world.dialogue_manager._next_dialogue_id == before + 1


# ════════════════════════════════════════════════════════════════════════
# Confiscation
# ════════════════════════════════════════════════════════════════════════


class TestConfiscation:
    def _mount(self, world, executor):
        holder = _austrian_marshal(world)
        region = _estate_region(world, holder, controller="France")
        _seed_stage1(world, region)
        _resolve_stage1(executor, world)
        return holder, region

    def test_confiscate_strips_windfalls_relations_trust(self, world, executor):
        holder, region = self._mount(world, executor)
        cautious = [m for m in world.marshals.values()
                    if m.nation == "France" and m.personality == "cautious"]
        if not cautious:
            volunteer = next(m for m in world.marshals.values()
                             if m.nation == "France" and m.strength > 0)
            volunteer.personality = "cautious"
            cautious = [volunteer]
        trust_before = {m.name: m.trust.value if hasattr(m.trust, "value")
                        else m.trust for m in cautious}
        gold_before = world.nation_gold.get("France", 0)
        relation_before = world.nation_relations.get(
            world._make_diplo_key("France", "Austria"), 0)
        promised = world.pending_capture_choice["windfall"]

        result = executor.handle_capture_choice("confiscate", {"world": world})

        assert result["success"] is True
        assert world.pending_capture_choice is None
        assert region.name not in holder.dotation_regions
        assert world.nation_gold["France"] == gold_before + promised
        assert world.nation_relations[
            world._make_diplo_key("France", "Austria")
        ] == relation_before + CONFISCATION_RELATIONS_PENALTY
        for m in cautious:
            now = m.trust.value if hasattr(m.trust, "value") else m.trust
            assert now == trust_before[m.name] + CONFISCATION_CAUTIOUS_TRUST
        assert any(e["type"] == "estate_confiscated"
                   for e in world.event_log)

    def test_confiscated_holder_erodes_via_existing_machinery(self, world, executor):
        holder, region = self._mount(world, executor)
        holder.battles_won = 3  # expectation 120 > satisfaction 0
        holder.expectation_grace_turn = -1
        executor.handle_capture_choice("confiscate", {"world": world})
        trust_before = (holder.trust.value if hasattr(holder.trust, "value")
                        else holder.trust)
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert holder.expectation_grace_turn == world.current_turn
        world.current_turn += GRACE_TURNS
        world._dotation_processed_turn = None
        world._process_dotation_state()
        trust_after = (holder.trust.value if hasattr(holder.trust, "value")
                       else holder.trust)
        assert trust_after < trust_before

    def test_confiscated_region_becomes_endowable(self, world, executor):
        """The audit's exact dead end, reversed: Mack's old duchy can be
        endowed to a French marshal once confiscated."""
        holder, region = self._mount(world, executor)
        eligible_before, reason = check_estate_eligibility(
            world, "France", region.name)
        assert eligible_before is False
        assert holder.name in reason  # "already sustains Marshal X's household"
        executor.handle_capture_choice("confiscate", {"world": world})
        # Non-homeland (Austrian soil), non-capital, now un-dotated:
        eligible_after, _ = check_estate_eligibility(world, "France", region.name)
        assert eligible_after is True
        ney = world.marshals.get("Ney")
        assert ney is not None
        result = executor.execute(
            {"command": {"marshal": "Ney", "action": "grant_dotation",
                         "target": region.name, "type": "specific"}},
            {"world": world},
        )
        assert result["success"] is True, result.get("message")
        assert region.name in ney.dotation_regions

    def test_wrong_token_refused_with_question_restated(self, world, executor):
        self._mount(world, executor)
        result = executor.handle_capture_choice("plunder", {"world": world})
        assert result["success"] is False
        assert world.pending_capture_choice is not None  # not cleared
        assert "confiscate" in result["message"]
        assert "respect" in result["message"]
        assert result["pending_capture_choice"] is True

    def test_stale_dialogue_id_refused(self, world, executor):
        self._mount(world, executor)
        current_id = world.pending_capture_choice["dialogue_id"]
        result = executor.handle_capture_choice(
            "confiscate", {"world": world}, dialogue_id=current_id - 1)
        assert result["success"] is False
        assert result.get("stale_dialogue") is True
        assert world.pending_capture_choice is not None
        # Matching id applies
        result = executor.handle_capture_choice(
            "confiscate", {"world": world}, dialogue_id=current_id)
        assert result["success"] is True
        assert world.pending_capture_choice is None


# ════════════════════════════════════════════════════════════════════════
# Respect the title
# ════════════════════════════════════════════════════════════════════════


class TestRespect:
    def _respected(self, world, executor):
        holder = _austrian_marshal(world)
        region = _estate_region(world, holder, controller="France")
        _seed_stage1(world, region)
        _resolve_stage1(executor, world)
        result = executor.handle_capture_choice("respect", {"world": world})
        assert result["success"] is True
        return holder, region

    def test_respect_stores_entry_and_keeps_estate(self, world, executor):
        holder, region = self._respected(world, executor)
        assert world.pending_capture_choice is None
        assert region.name in holder.dotation_regions
        assert is_estate_respected(world, holder.name, region.name)
        entry = world.respected_estates[0]
        assert entry == {"region": region.name, "marshal": holder.name,
                         "nation": "Austria", "respecter": "France"}

    def test_respected_estate_survives_prune_and_pays_satisfaction(
            self, world, executor):
        holder, region = self._respected(world, executor)
        sat = get_satisfaction(holder, world)
        assert sat >= region.get_effective_income()
        world._dotation_processed_turn = None
        world._process_dotation_state()
        assert region.name in holder.dotation_regions  # prune skipped it
        assert not any(e["type"] == "estate_lost"
                       and e["region"] == region.name
                       for e in world.event_log)

    def test_acceptance_term_applies_and_caps(self, world, executor):
        holder, region = self._respected(world, executor)
        # A second respected Austrian estate must NOT stack (cap 1/nation)
        holder2 = next(m for m in world.marshals.values()
                       if m.nation == "Austria" and m is not holder)
        region2 = _estate_region(world, holder2, controller="France")
        apply_estate_respect(world, region2, holder2, "France")
        assert respected_estate_mod(world, "France", "Austria") == \
            RESPECT_ACCEPTANCE_BONUS
        # And it credits only the respecter, only toward the holder nation
        assert respected_estate_mod(world, "Prussia", "Austria") == 0
        assert respected_estate_mod(world, "France", "Prussia") == 0
        acceptance = calculate_acceptance(
            {"type": "non_aggression", "proposer_nation": "France",
             "target_nation": "Austria"}, world)
        assert acceptance["components"]["respected_estate_mod"] == \
            RESPECT_ACCEPTANCE_BONUS

    def test_entry_pruned_when_respecter_loses_region(self, world, executor):
        holder, region = self._respected(world, executor)
        region.controller = "Prussia"  # changed hands outside the pipeline
        world.invalidate_active_nations_cache()
        assert not is_estate_respected(world, holder.name, region.name)
        prune_respected_estates(world)
        assert world.respected_estates == []
        assert respected_estate_mod(world, "France", "Austria") == 0

    def test_respected_foreign_estate_not_listed_endowable(self, world, executor):
        """Review fix: a respected FOREIGN estate on our occupied soil must
        not be offered as endowable (the executor would always refuse it,
        and the AI grant rung starved on the refusal)."""
        from backend.game_logic.dotation import list_eligible_estates
        holder, region = self._respected(world, executor)
        assert region.controller == "France"
        assert region.name not in list_eligible_estates(world, "France")
        # And the refusal-consistency invariant holds for everything listed
        for name in list_eligible_estates(world, "France")[:6]:
            ok, _ = check_estate_eligibility(world, "France", name)
            assert ok, f"{name} listed but refused"

    def test_entry_pruned_when_estate_returns_home(self, world, executor):
        holder, region = self._respected(world, executor)
        region.controller = "Austria"  # holder nation recaptured
        world.invalidate_active_nations_cache()
        prune_respected_estates(world)
        assert world.respected_estates == []
        # Satisfaction is natural again (controller == nation)
        assert get_satisfaction(holder, world) >= region.get_effective_income()


# ════════════════════════════════════════════════════════════════════════
# GR5 — the AI conqueror's deterministic rule
# ════════════════════════════════════════════════════════════════════════


class TestAIRule:
    def test_ai_confiscates_at_war(self, world):
        """France and Austria are at war at the 1805 boot — an Austrian
        conqueror confiscates a French marshal's estate (symmetry: the
        player's marshals are not safe either)."""
        french = next(m for m in world.marshals.values()
                      if m.nation == "France" and m.strength > 0)
        region = next(r for r in world.regions.values()
                      if r.controller == "France" and not r.is_capital
                      and r.region_type != "capital")
        french.dotation_regions.append(region.name)
        region.controller = "Austria"
        world.invalidate_active_nations_cache()
        assert world.is_at_war("Austria", "France")
        gold_before = world.nation_gold.get("Austria", 0)
        outcome = apply_ai_estate_rule(world, region, "Austria")
        assert outcome["choice"] == "confiscate"
        assert region.name not in french.dotation_regions
        assert world.nation_gold["Austria"] > gold_before
        # The victim court is told at once (player-marshal victim)
        notes = world.notifications.get_pending()
        assert any(n["type"] == "estate_confiscated" for n in notes)

    def test_ai_respects_when_not_at_war(self, world):
        holder = _austrian_marshal(world)
        region = _estate_region(world, holder)
        region.controller = "Prussia"
        world.invalidate_active_nations_cache()
        assert not world.is_at_war("Prussia", "Austria")
        outcome = apply_ai_estate_rule(world, region, "Prussia")
        assert outcome["choice"] == "respect"
        assert region.name in holder.dotation_regions
        assert is_estate_respected(world, holder.name, region.name)

    def test_ai_rule_noop_off_estate_soil(self, world):
        region = next(r for r in world.regions.values()
                      if r.controller == "Austria" and not r.is_capital)
        region.controller = "France"
        world.invalidate_active_nations_cache()
        assert apply_ai_estate_rule(world, region, "France") is None


# ════════════════════════════════════════════════════════════════════════
# Serialization
# ════════════════════════════════════════════════════════════════════════


class TestSerialization:
    def test_respected_estates_round_trip(self, world, executor):
        holder = _austrian_marshal(world)
        region = _estate_region(world, holder, controller="France")
        apply_estate_respect(world, region, holder, "France")
        loaded = WorldState.from_dict(world.to_dict())
        assert loaded.respected_estates == world.respected_estates
        holder2 = loaded.marshals[holder.name]
        assert is_estate_respected(loaded, holder2.name, region.name)

    def test_estate_stage_pending_round_trips(self, world, executor):
        holder = _austrian_marshal(world)
        region = _estate_region(world, holder, controller="France")
        _seed_stage1(world, region)
        _resolve_stage1(executor, world)
        pending = world.pending_capture_choice
        loaded = WorldState.from_dict(world.to_dict())
        assert loaded.pending_capture_choice == pending
        # The minted-id counter round-trips with the dialogue manager, so a
        # post-load question can never repeat a used identity.
        assert (loaded.dialogue_manager._next_dialogue_id
                == world.dialogue_manager._next_dialogue_id)

    def test_absent_field_defaults_empty(self, world):
        data = world.to_dict()
        data.pop("respected_estates", None)
        loaded = WorldState.from_dict(data)
        assert loaded.respected_estates == []


# ════════════════════════════════════════════════════════════════════════
# Typed surface (W6-0 pending-question router)
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture()
def endpoint():
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP

    original_parser = main_module.parser
    original_world = main_module.world
    original_game_state = main_module.game_state
    main_module.parser = _CP(use_real_llm=False)
    main_module.world = WorldState.from_scenario(str(SCENARIO_PATH))
    main_module.game_state = {"world": main_module.world}
    try:
        yield TestClient(main_module.app), main_module
    finally:
        main_module.parser = original_parser
        main_module.world = original_world
        main_module.game_state = original_game_state


class TestTypedSurface:
    def _mount_estate(self, m):
        world = m.world
        holder = _austrian_marshal(world)
        region = _estate_region(world, holder, controller="France")
        _seed_stage1(world, region)
        CommandExecutor().handle_capture_choice("secure", {"world": world})
        assert world.pending_capture_choice["stage"] == "estate"
        return holder, region

    def test_typed_confiscate_resolves(self, endpoint):
        client, m = endpoint
        holder, region = self._mount_estate(m)
        data = client.post("/command", json={"command": "confiscate"}).json()
        assert data["success"] is True
        assert m.world.pending_capture_choice is None
        assert region.name not in holder.dotation_regions

    def test_typed_respect_resolves(self, endpoint):
        client, m = endpoint
        holder, region = self._mount_estate(m)
        data = client.post("/command", json={"command": "respect"}).json()
        assert data["success"] is True
        assert m.world.pending_capture_choice is None
        assert is_estate_respected(m.world, holder.name, region.name)

    def test_typed_tokens_with_nothing_pending_fall_through(self, endpoint):
        client, m = endpoint
        assert m.world.pending_capture_choice is None
        data = client.post("/command", json={"command": "respect"}).json()
        assert data.get("capture_choice") is None

    def test_other_commands_blocked_with_estate_question(self, endpoint):
        client, m = endpoint
        self._mount_estate(m)
        data = client.post("/command", json={"command": "status"}).json()
        assert data["success"] is False
        assert "confiscate" in data["message"]
        assert "respect" in data["message"]

    def test_capture_choice_endpoint_stale_id(self, endpoint):
        client, m = endpoint
        self._mount_estate(m)
        current_id = m.world.pending_capture_choice["dialogue_id"]
        data = client.post("/capture_choice", json={
            "choice": "confiscate", "dialogue_id": current_id - 1}).json()
        assert data["success"] is False
        assert data.get("stale_dialogue") is True
        assert m.world.pending_capture_choice is not None
        data = client.post("/capture_choice", json={
            "choice": "confiscate", "dialogue_id": current_id}).json()
        assert data["success"] is True
        assert m.world.pending_capture_choice is None


# ════════════════════════════════════════════════════════════════════════
# Campaign log
# ════════════════════════════════════════════════════════════════════════


class TestCampaignLog:
    def test_oneliners(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "estate_confiscated", "marshal": "Mack",
            "nation": "Austria", "region": "Swabia",
            "confiscated_by": "France",
        })
        assert "France" in line and "Mack" in line and "Swabia" in line
        line = format_event_oneliner({
            "type": "estate_respected", "marshal": "Mack",
            "nation": "Austria", "region": "Swabia",
            "respected_by": "France",
        })
        assert "honored" in line and "Swabia" in line
