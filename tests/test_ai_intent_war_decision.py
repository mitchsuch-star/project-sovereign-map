"""AI-3 — The Decision for War (docs/AI_INTENT_SPEC.md §4.3, §4.3a, §13.1;
gate record §16; landing record §17).

Pins carried here:
- The ladder gate (§5 pin 8): no cold-open wars — refusals or a renege
  grievance on the SERIALIZED record.
- Fore-warning before war, always: beat 2 → beat 3 → declaration, never
  earlier than the foregrounded tenure.
- Pin 21: every foregrounded crisis ends on screen — the war, or The
  Crisis Passes with its §12.1 cause named.
- Pin 15: no undeclared conquest — refused declarations abort at both
  combat seams, and the OPEN_MOVEMENT capture hole is closed.
- D1's cap (§16.1-1): at most 2 live AI-initiated wars.
- AI-3c: the army agrees with the ledger — the frontier bias exists,
  releases with the crisis, and is deckless-neutral.
- §4.3a's blocked case: the co-belligerent side-exit helper is executable.
"""

from pathlib import Path

import pytest

from backend.commands.executor import CommandExecutor
from backend.game_logic import war_council
from backend.game_logic.ai_diplomacy import record_diplomatic_refusal
from backend.game_logic.diplomacy import declare_war
from backend.game_logic.instruments import (
    _mint_grievance,
    create_compensation_bargain,
    pledge_guarantee,
)
from backend.game_logic.intent import get_nation_intent
from backend.game_logic.war_council import (
    MAX_SIMULTANEOUS_AI_WARS,
    can_declare_war,
    count_ai_initiated_wars,
    exit_shared_wars_for_defection,
    get_intent_frontier,
    process_war_council,
)
from backend.models.world_state import WorldState

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (REPO_ROOT / "godot-client" / "project-sovereign"
                 / "assets" / "maps" / "europe_1805.json")


@pytest.fixture(scope="module")
def world1805():
    return WorldState.from_scenario(str(SCENARIO_PATH))


@pytest.fixture()
def world(world1805):
    return WorldState.from_dict(world1805.to_dict())


def _arm_prussia_crisis(world):
    """Drive Prussia's hanoverian_prize to the fight rung with a climbed
    ladder: cold relations (+8), a reneged bargain (+15, and the ladder's
    skip-rungs casus), Hanover busy (+6) and bankrupt (+3) on base 55 —
    weight 87 ≥ 85 on the historical seed (jitter 0)."""
    world.nation_relations[world._make_diplo_key("Prussia", "Hanover")] = -45
    _mint_grievance(world, breaker="Hanover", victim="Prussia",
                    grievance_type="bargain_reneged", source="test_fixture")
    declare_war(world, "Hanover", "Denmark")
    world.nation_gold["Hanover"] = -50
    world.nation_gold["Prussia"] = max(
        int(world.nation_gold.get("Prussia", 0)), 2000)
    world.invalidate_bloc_members_cache()


def _poll_next_turn(world):
    """Advance the clock one turn and run the council poll (the fixture's
    stand-in for the advance_turn slot)."""
    world.current_turn = int(world.current_turn) + 1
    return process_war_council(world)


class TestPreview:
    """§4.3a-4 — the shared can_declare_war preview."""

    def test_self_war_refused(self, world):
        assert can_declare_war(world, "Prussia", "Prussia")["reason"] == "self_war"

    def test_already_at_war_refused(self, world):
        result = can_declare_war(world, "Austria", "France")
        assert result["reason"] == "already_at_war"

    def test_armistice_cooldown_refused(self, world):
        key = world._make_diplo_key("Prussia", "Hanover")
        world.armistice_cooldowns[key] = 3
        assert can_declare_war(world, "Prussia", "Hanover")["reason"] == \
            "armistice_cooldown"

    def test_treaty_in_the_way_named(self, world):
        from backend.game_logic.diplomacy import set_diplomatic_state
        set_diplomatic_state(world, "Prussia", "Hanover", "NON_AGGRESSION",
                            "test_fixture")
        assert can_declare_war(world, "Prussia", "Hanover")["reason"] == \
            "treaty_in_the_way"

    def test_clean_pair_ok(self, world):
        assert can_declare_war(world, "Prussia", "Hanover")["ok"] is True


class TestCrisisLifecycle:
    """Beat 2 → beat 3 → declaration, on the fore-warning clock."""

    def test_crisis_opens_foregrounded_with_beat_2(self, world):
        _arm_prussia_crisis(world)
        view = get_nation_intent("Prussia", world)
        assert view.price == "fight" and view.against == "Hanover"
        events = process_war_council(world)
        assert "Prussia" in world.war_intents
        record = world.war_intents["Prussia"]
        assert record["foregrounded"] is True
        brewing = [e for e in events if e["type"] == "crisis_brewing"]
        assert brewing and brewing[0]["target"] == "Hanover"
        # Beat 2 reaches the campaign log (the fore-warning is public).
        assert any(e.get("type") == "crisis_brewing" for e in world.event_log)

    def test_coercive_demand_fires_next_turn_on_the_record(self, world):
        _arm_prussia_crisis(world)
        process_war_council(world)
        events = _poll_next_turn(world)
        demands = [e for e in events if e["type"] == "coercive_demand"]
        assert demands, "beat 3's AI-AI arm must fire on the second poll"
        refusals = world.diplomatic_refusals.get("Prussia>Hanover") or []
        assert any(e.get("type") == war_council.COERCIVE_DEMAND_TYPE
                   for e in refusals), "the demand lands on the SERIALIZED record"

    def test_no_declaration_before_forewarn_tenure(self, world):
        _arm_prussia_crisis(world)
        process_war_council(world)          # T0: opens
        _poll_next_turn(world)              # T1: coerce
        assert not world.is_at_war("Prussia", "Hanover"), \
            "tenure 1 < CRISIS_FOREWARN_TURNS — no war yet"

    def test_declaration_fires_with_reason_and_design(self, world):
        _arm_prussia_crisis(world)
        process_war_council(world)
        _poll_next_turn(world)
        events = _poll_next_turn(world)     # T2: tenure satisfied
        assert world.is_at_war("Prussia", "Hanover")
        declared = [e for e in events if e["type"] == "ai_war_declared"]
        assert declared and declared[0]["stated_reason"]
        assert "Prussia" not in world.war_intents, "the crisis record closes"
        # The instance carries the design and the stated reason (pin 4).
        wars = [w for w in world.war_instances.values()
                if w.get("ai_initiated")]
        assert wars and wars[0].get("stated_reason")
        assert wars[0].get("design_id") == "hanoverian_prize"
        # The objective carries the DESIGN's provinces, not [capital].
        key = world._make_diplo_key("Prussia", "Hanover")
        objective = world.war_objectives[key]["Prussia"]
        assert objective.get("design") == "hanoverian_prize"
        assert "Hanover" in (objective.get("target_regions") or [])
        # The logged declaration carries the stated reason for the headline.
        logged = [e for e in world.event_log
                  if e.get("type") == "war_declaration"
                  and e.get("aggressor") == "Prussia"]
        assert logged and logged[-1].get("stated_reason")
        # Review fix [r9]: the REAL declared war counts against D1's cap.
        assert count_ai_initiated_wars(world) == 1

    def test_ladder_gate_blocks_cold_open(self, world, monkeypatch):
        """Weight alone never declares — §5 pin 8's no-cold-open-wars.
        The fight rung is forced through the intent seam so the LADDER
        gate is the only variable: no refusals, no grievance → no crisis."""
        from backend.game_logic import intent as intent_module
        forced = intent_module.IntentView(
            nation="Prussia", want_id="hanoverian_prize",
            want_title="The Hanoverian Prize", want_type="acquire_regions",
            against="Hanover", weight=90, price="fight")
        monkeypatch.setattr(
            intent_module, "get_nation_intent",
            lambda nation, w: forced if nation == "Prussia"
            else intent_module._indifferent(nation))
        assert not world.diplomatic_refusals.get("Prussia>Hanover")
        process_war_council(world)
        assert "Prussia" not in world.war_intents, \
            "an unclimbed ladder never even fore-warns"

    def test_refusals_satisfy_the_ladder_gate(self, world, monkeypatch):
        from backend.game_logic import intent as intent_module
        forced = intent_module.IntentView(
            nation="Prussia", want_id="hanoverian_prize",
            want_title="The Hanoverian Prize", want_type="acquire_regions",
            against="Hanover", weight=90, price="fight")
        monkeypatch.setattr(
            intent_module, "get_nation_intent",
            lambda nation, w: forced if nation == "Prussia"
            else intent_module._indifferent(nation))
        # Two refused asks inside the memory window, types apart so the
        # 6-turn dedupe admits both.
        world.current_turn = 20
        record_diplomatic_refusal(world, "Prussia", "Hanover", "design_purchase")
        record_diplomatic_refusal(world, "Prussia", "Hanover", "alignment")
        process_war_council(world)
        assert "Prussia" in world.war_intents

    def test_d1_cap_holds_the_crisis_open(self, world):
        _arm_prussia_crisis(world)
        # Two live AI-initiated wars already stand (D1's denominator) —
        # LIVE means two standing sides (review fix [r2 HIGH]: a war
        # decided by elimination stops counting).
        world.war_instances["wf1"] = {
            "ai_initiated": True, "ended_turn": None,
            "active_participants": ["Sweden", "Denmark"],
        }
        world.war_instances["wf2"] = {
            "ai_initiated": True, "ended_turn": None,
            "active_participants": ["Spain", "Portugal"],
        }
        assert count_ai_initiated_wars(world) >= MAX_SIMULTANEOUS_AI_WARS
        process_war_council(world)
        _poll_next_turn(world)
        _poll_next_turn(world)
        assert not world.is_at_war("Prussia", "Hanover"), "D1's cap holds"
        assert "Prussia" in world.war_intents, "the crisis waits, does not die"

    def test_elimination_frees_the_d1_cap(self, world):
        """Review fix [r2 HIGH]: a design war won by ELIMINATING the minor
        never receives ended_turn — the cap must not count it forever."""
        world.war_instances["wf_won"] = {
            "ai_initiated": True, "ended_turn": None,
            # The loser was eliminated and stripped from the sides.
            "active_participants": ["Prussia"],
        }
        assert count_ai_initiated_wars(world) == 0


class TestCrisisPasses:
    """Beat 7 (pin 21) — the other ending, cause named."""

    def _open(self, world):
        _arm_prussia_crisis(world)
        process_war_council(world)
        assert "Prussia" in world.war_intents

    def test_bought_off(self, world):
        self._open(world)
        create_compensation_bargain(
            world, payer="Hanover", recipient="Prussia",
            design_id="hanoverian_prize", granted={"kind": "gold", "amount": 900})
        events = _poll_next_turn(world)
        passed = [e for e in events if e["type"] == "crisis_passed"]
        assert passed and passed[0]["cause"] == "bought_off"
        assert "Prussia" not in world.war_intents

    def test_deterred_by_guarantee(self, world):
        self._open(world)
        pledge_guarantee(world, guarantor="Russia", protected="Hanover")
        world.invalidate_bloc_members_cache()
        events = _poll_next_turn(world)
        passed = [e for e in events if e["type"] == "crisis_passed"]
        # Review fix [r9]: a HARD assert, not a skip — if a retune ever
        # keeps the rung at fight through the -8 deterrent, this test must
        # fail loudly, not go dark (weight 87 - 8 = 79 < 85 today).
        assert get_nation_intent("Prussia", world).price != "fight", \
            "the -8 deterrent must drop the fixture's rung below fight"
        assert passed and passed[0]["cause"] == "deterred"

    def test_satisfied_when_the_want_is_won(self, world):
        self._open(world)
        region = world.regions["Hanover"]
        region.controller = "Prussia"
        world.invalidate_active_nations_cache()
        events = _poll_next_turn(world)
        passed = [e for e in events if e["type"] == "crisis_passed"]
        assert passed and passed[0]["cause"] == "satisfied"

    def test_stalled_predicate_cools_on_screen(self, world):
        """Pin 21's termination guarantee: a crisis whose declaration
        predicate goes permanently refused ends as starved, on screen."""
        self._open(world)
        key = world._make_diplo_key("Prussia", "Hanover")
        world.armistice_cooldowns[key] = 99
        passed = []
        for _ in range(6):
            events = _poll_next_turn(world)
            passed += [e for e in events if e["type"] == "crisis_passed"]
            if passed:
                break
        assert passed and passed[0]["cause"] == "starved"
        assert "Prussia" not in world.war_intents


class TestPin15NoUndeclaredConquest:
    """§4.3a-3 + the OPEN_MOVEMENT capture hole."""

    def test_refused_declaration_aborts_the_attack(self, world):
        executor = CommandExecutor()
        gs = {"world": world, "debug_mode": True}
        # An Austrian marshal beside Prussian soil, pair under armistice
        # cooldown → the declaration is refused → the attack must abort.
        austrian = next(m for m in world.marshals.values()
                        if m.nation == "Austria" and m.strength > 0)
        prussian_region = next(r.name for r in world.regions.values()
                               if r.controller == "Prussia"
                               and r.adjacent_regions)
        key = world._make_diplo_key("Austria", "Prussia")
        world.armistice_cooldowns[key] = 5
        austrian.location = world.regions[prussian_region].adjacent_regions[0]
        world._build_marshal_index()
        before_controller = world.regions[prussian_region].controller
        before_strengths = {m.name: int(m.strength)
                            for m in world.marshals.values()}
        before_locations = {m.name: m.location
                            for m in world.marshals.values()}
        before_war_count = len(world.war_instances)
        before_captures = sum(1 for e in world.event_log
                              if e.get("type") == "region_captured")
        result = executor._execute_attack(austrian, prussian_region, world, gs)
        assert result.get("success") is False
        assert world.regions[prussian_region].controller == before_controller
        assert not world.is_at_war("Austria", "Prussia")
        # Pin 15's FULL second clause: the refused declaration leaves the
        # world byte-identical — no battle ran, nobody moved, no instance,
        # no conquest event (review fix [r9]).
        assert {m.name: int(m.strength)
                for m in world.marshals.values()} == before_strengths
        assert {m.name: m.location
                for m in world.marshals.values()} == before_locations
        assert len(world.war_instances) == before_war_count
        assert sum(1 for e in world.event_log
                   if e.get("type") == "region_captured") == before_captures

    def test_open_movement_capture_requires_declaration(self, world):
        """The can_enter_territory shortcut is closed: an attack on a
        NON_AGGRESSION partner's undefended region declares first."""
        from backend.game_logic.diplomacy import set_diplomatic_state
        executor = CommandExecutor()
        gs = {"world": world, "debug_mode": True}
        set_diplomatic_state(world, "Austria", "Prussia", "NON_AGGRESSION",
                            "test_fixture")
        austrian = next(m for m in world.marshals.values()
                        if m.nation == "Austria" and m.strength > 0)
        target = next(r.name for r in world.regions.values()
                      if r.controller == "Prussia"
                      and not world.get_marshals_in_region(r.name)
                      and r.adjacent_regions)
        austrian.location = world.regions[target].adjacent_regions[0]
        world._build_marshal_index()
        executor._execute_attack(austrian, target, world, gs)
        # Whatever the combat outcome, the pair is now formally at WAR —
        # no province changes hands outside a war the ledger can name.
        assert world.is_at_war("Austria", "Prussia")


class TestAI3cFrontier:
    """§13.1 — the army agrees with the ledger."""

    def test_frontier_lists_massing_ground(self, world):
        _arm_prussia_crisis(world)
        process_war_council(world)
        frontier = get_intent_frontier(world, "Prussia")
        assert frontier, "a live crisis must expose massing ground"
        assert "Hanover" in frontier, "the design's object anchors the bias"
        allowed = {"Hanover"} | set(world.regions["Hanover"].adjacent_regions)
        assert set(frontier) <= allowed

    def test_frontier_releases_with_the_crisis(self, world):
        _arm_prussia_crisis(world)
        process_war_council(world)
        assert get_intent_frontier(world, "Prussia")
        create_compensation_bargain(
            world, payer="Hanover", recipient="Prussia",
            design_id="hanoverian_prize", granted={"kind": "gold", "amount": 900})
        _poll_next_turn(world)  # the crisis passes; the cache turn moved
        assert get_intent_frontier(world, "Prussia") == []

    def test_deckless_world_reads_empty(self):
        bare = WorldState()
        assert get_intent_frontier(bare, "Britain") == []
        assert process_war_council(bare) == []
        assert bare.war_intents == {}


class TestGuarantorJoin:
    """The join arm: an AI guarantor honours; France is pleaded with.

    Exercised at the declaration step directly — organically a lone
    guarantee's -8 deters the crisis first (the design working), so the
    join arm's live case is the coveter whose weight clears even that
    bar. The step is the seam either way."""

    def _record(self):
        return {
            "coveter": "Prussia", "target": "Hanover",
            "design_id": "hanoverian_prize",
            "want_title": "The Hanoverian Prize",
            "opened_turn": 1, "foregrounded": True, "foregrounded_turn": 1,
            "coerce_recorded_turn": 2, "treaty_broken_turn": None,
        }

    def test_ai_guarantor_honours_at_declaration(self, world):
        pledge_guarantee(world, guarantor="Denmark", protected="Hanover")
        events = []
        assert war_council._declare_design_war(
            world, "Prussia", self._record(), events) is True
        assert world.is_at_war("Prussia", "Hanover")
        honored = [e for e in events if e["type"] == "guarantee_honored"]
        assert honored and honored[0]["guarantor"] == "Denmark"
        assert world.is_at_war("Denmark", "Prussia")

    def test_france_guarantee_pleads_not_conscripts(self, world):
        pledge_guarantee(world, guarantor="France", protected="Hanover")
        events = []
        assert war_council._declare_design_war(
            world, "Prussia", self._record(), events) is True
        assert not world.is_at_war("France", "Prussia"), \
            "the player is never auto-conscripted"
        queued = [e for e in (getattr(world, "pending_dispatch_events", []) or [])
                  if e.get("type") == "guarantee_called"]
        assert queued, "the ward's plea reaches the dispatch"


class TestDefectionHelper:
    """§4.3a's mainline blocked case — executable, scripted."""

    def test_co_belligerent_exit_then_declare(self, world):
        # Austria and Britain share the anti-France war sides at boot; a
        # direct declaration between them is side-conflict blocked.
        preview = can_declare_war(world, "Austria", "Britain")
        assert preview["reason"] == "war_instance_side_conflict"
        result = exit_shared_wars_for_defection(world, "Austria", "Britain")
        assert "France" in result["exited"]
        assert not world.is_at_war("Austria", "France")
        after = declare_war(world, "Austria", "Britain")
        assert after.get("success") is True
        assert world.is_at_war("Austria", "Britain")


class TestSerialization:
    def test_crisis_survives_a_save(self, world):
        """Pin 8's sister: mid-ladder state — rung, tenure, the coerce
        step — must round-trip, or fore-warning lies across a load."""
        _arm_prussia_crisis(world)
        process_war_council(world)
        _poll_next_turn(world)
        record = dict(world.war_intents["Prussia"])
        loaded = WorldState.from_dict(world.to_dict())
        assert loaded.war_intents["Prussia"] == record
        assert (loaded.diplomatic_refusals.get("Prussia>Hanover")
                == world.diplomatic_refusals.get("Prussia>Hanover"))
        # Review fix [r9]: the CLOCK drives the loaded world — the
        # declaration fires on schedule after the load, exactly as it
        # would have without one (the behaviour, not just the record).
        loaded.current_turn = int(loaded.current_turn) + 1
        process_war_council(loaded)
        assert loaded.is_at_war("Prussia", "Hanover"), \
            "fore-warning must not lie across a save/load"

    def test_pre_stage_d_saves_read_empty(self, world):
        data = world.to_dict()
        data.pop("war_intents", None)
        loaded = WorldState.from_dict(data)
        assert loaded.war_intents == {}
