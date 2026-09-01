"""The PC15-D gate rulings — built Aug 15, 2026 under the user's delegated
grant ("make decisions for design gate items").

Gate record = docs/DESIGN_REFINEMENT.md §Comprehensive Playtest (PC15-D1..D4).

  D1 "The Closed Frontier" — the forced-retreat scan obeys the movement
     law: strictly neutral (PEACE/ARMISTICE) soil is never a refuge; a
     cornered army capitulates in place (Ulm, as it happened). Riders: the
     jealousy glory-hunt never targets an enemy standing on neutral soil,
     a jealousy-autonomous attack never stages the war-purpose dialogue,
     and the DP-shortage declaration refusal is a visible receipt.
  D2 "The Ally's Table" — ALLIANCE/DEFENSIVE_ALLIANCE/VASSAL soil feeds a
     guest army at the home 1.5×; Berthier's famine counsel names the
     legal dispersal split with real numbers; the AI's P6.5 rung reads the
     same effective cap.
  D3 (tutorial expectation dormancy) + D4 (exhausted-pair truce floor) —
     see their own classes below.
"""

from pathlib import Path

import pytest

from backend.models.world_state import WorldState
from tests.conftest import MarshalFactory, WorldFactory

REPO = Path(__file__).resolve().parents[1]


def _pair(world, a, b, state):
    key = world._make_diplo_key(a, b)
    world.diplomatic_states[key] = state
    if state == "WAR":
        world.war_start_turns[key] = world.current_turn


# ═══════════════════════════════════════════════════════════════════════════
# D1 — the closed frontier
# ═══════════════════════════════════════════════════════════════════════════


class TestD1RetreatObeysTheMovementLaw:
    def _cornered_world(self, host_state):
        """Ney at Belgium, Wellington's army on him, every OTHER neighbour
        controlled by Prussia under `host_state`. Cautious personality so
        the fate check resolves (an aggressive PLAYER marshal gets the
        last-stand interrupt instead — its own pinned surface)."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=8000,
                                      personality="cautious")
        enemy = MarshalFactory.enemy(name="Wellington", location="Belgium",
                                     nation="Britain", strength=40000)
        world = WorldFactory.with_marshals([ney, enemy])
        _pair(world, "France", "Britain", "WAR")
        _pair(world, "France", "Prussia", host_state)
        belgium = world.get_region("Belgium")
        for adj in belgium.adjacent_regions:
            region = world.get_region(adj)
            if region is not None:
                region.controller = "Prussia"
        return world

    def test_neutral_frontier_is_closed(self):
        """The Mack pin: with every land exit a PEACE court, the scan
        returns None — capitulation in place, never a tour of Berlin."""
        world = self._cornered_world("PEACE")
        dest = world.get_safe_retreat_destination("Ney", "Belgium")
        assert dest is None

    def test_armistice_frontier_is_closed_too(self):
        world = self._cornered_world("ARMISTICE")
        assert world.get_safe_retreat_destination("Ney", "Belgium") is None

    @pytest.mark.parametrize("state", ["ALLIANCE", "OPEN_BORDERS", "VASSAL"])
    def test_open_movement_soil_stays_a_refuge(self, state):
        world = self._cornered_world(state)
        assert world.get_safe_retreat_destination("Ney", "Belgium") is not None

    def test_at_war_soil_still_beats_encirclement(self):
        """Tier 5 unchanged: desperation onto an at-war court's soil is
        still chosen over capitulation."""
        world = self._cornered_world("WAR")
        assert world.get_safe_retreat_destination("Ney", "Belgium") is not None

    def test_cornered_army_is_captured_not_teleported(self):
        """The fate machinery downstream of the closed frontier: a broken
        army with no legal exit and a live captor is CAPTURED (context
        encircled) — the historically exact Ulm outcome, now with the
        PC15-1 receipts behind it."""
        from backend.commands.combat_executor import CombatExecutor
        from backend.commands.executor import CommandExecutor

        world = self._cornered_world("PEACE")
        ney = world.get_marshal("Ney")
        combat = CombatExecutor(CommandExecutor())
        combat._apply_forced_retreat_or_break(
            ney, world.get_marshal("Wellington"), world)
        ney_after = world.get_marshal("Ney")
        assert ney_after is not None
        assert ney_after.captured_by == "Britain"
        # He is held at the CAPTOR's capital (W6-7), never standing on a
        # neutral court's soil as a free army.
        assert ney_after.location == world.get_nation_capital("Britain")
        assert ney_after.strength == 0


class TestD1JealousyHuntRespectsNeutrality:
    def test_enemy_on_neutral_soil_is_not_a_glory_target(self):
        """Lannes stormed BERLIN at peace with Prussia — the glory-hunt
        now skips an at-war enemy standing on a neutral court's soil."""
        from backend.game_logic.jealousy import find_autonomous_attack_target

        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=20000,
                                      personality="aggressive")
        enemy = MarshalFactory.enemy(name="Mack", location="Belgium",
                                     nation="Austria", strength=8000)
        world = WorldFactory.with_marshals([ney, enemy])
        _pair(world, "France", "Austria", "WAR")
        _pair(world, "France", "Prussia", "PEACE")
        world.get_region("Belgium").controller = "Prussia"
        assert find_autonomous_attack_target(world, ney) is None

    def test_enemy_on_his_own_war_soil_is_still_hunted(self):
        from backend.game_logic.jealousy import find_autonomous_attack_target

        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=20000,
                                      personality="aggressive")
        enemy = MarshalFactory.enemy(name="Mack", location="Belgium",
                                     nation="Austria", strength=8000)
        world = WorldFactory.with_marshals([ney, enemy])
        _pair(world, "France", "Austria", "WAR")
        world.get_region("Belgium").controller = "Austria"
        target = find_autonomous_attack_target(world, ney)
        assert target is not None
        assert target[0].name == "Mack"


class TestD1GhostChainClosed:
    def test_autonomous_attack_never_stages_the_war_purpose_dialogue(self):
        """Source census: FOUR sites in combat_executor read the
        `_jealousy_autonomous` flag — the two battle-advance staging sites
        in _execute_attack, the glorious charge's OWN staging site, and the
        reckless-popup predicate that keeps an autonomous attack from ever
        arming `respond_to_glorious_charge`. (The deliberate gate at the
        attack head is untouched.)

        Rewritten by WO slice 17 (Sept 1, 2026). This docstring used to say
        the charge site "takes no command and is reached only by direct
        player charges" — FALSE: `_execute_attack`'s auto-charge arm fires
        `_execute_glorious_charge` for a jealousy-autonomous attack at
        recklessness 3+, and the answered CHARGE/RESTRAIN popup re-entered
        it with the provenance gone. Measured: the answered charge staged
        `war_purpose_selection` from an attack the player never ordered.
        The charge takes `command` now; the behaviour pins live in
        test_wo_slice17_frontier_halts_the_charge.py."""
        src = (REPO / "backend" / "commands"
               / "combat_executor.py").read_text(encoding="utf-8")
        guarded = src.count('.get("_jealousy_autonomous")')
        assert guarded >= 4, (
            "a war-purpose staging site (or the reckless-popup predicate) "
            "lost its autonomous guard")

    def test_dp_shortage_declaration_is_a_visible_receipt(self):
        """'Three modals of theater, no war, no receipt' — the DP-shortage
        exit now rides the result popup so the chain always ENDS on
        screen."""
        from backend.commands.diplomatic_executor import DiplomaticExecutor
        from backend.commands.executor import CommandExecutor

        ney = MarshalFactory.infantry(name="Ney")
        world = WorldFactory.with_marshals([ney])
        world.diplomatic_points = 0
        _pair(world, "France", "Prussia", "PEACE")
        executor = CommandExecutor()
        diplo = DiplomaticExecutor(executor)
        result = diplo._execute_diplomatic_declare_war(
            {"target_nation": "Prussia",
             "war_objective": "conquest",
             "confirmed_objection": True},
            world)
        assert result.get("success") is False
        popup = world.proposal_result_popup
        assert popup is not None, "the refusal left no receipt"
        assert "nothing was relayed" in popup.get("message", "")


# ═══════════════════════════════════════════════════════════════════════════
# D2 — the ally's table
# ═══════════════════════════════════════════════════════════════════════════


class TestD2AllySupply:
    def _world(self, host_state, controller="Prussia"):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium")
        world = WorldFactory.with_marshals([ney])
        if host_state:
            _pair(world, "France", controller, host_state)
        world.get_region("Belgium").controller = controller
        return world

    @pytest.mark.parametrize("state", ["ALLIANCE", "DEFENSIVE_ALLIANCE",
                                       "VASSAL"])
    def test_fed_states_grant_the_home_multiplier(self, state):
        world = self._world(state)
        region = world.get_region("Belgium")
        assert world.get_effective_supply_cap("France", region) == int(
            region.supply_capacity * world.HOME_SUPPLY_MULTIPLIER)

    @pytest.mark.parametrize("state", ["PEACE", "OPEN_BORDERS",
                                       "NON_AGGRESSION", "WAR"])
    def test_stranger_states_stay_base(self, state):
        """The Ansbach line: transit rights are not magazines."""
        world = self._world(state)
        region = world.get_region("Belgium")
        assert world.get_effective_supply_cap(
            "France", region) == region.supply_capacity

    def test_gr5_any_nation_gets_the_same_table(self):
        """A Prussian corps on allied French soil eats from the same
        rule — the predicate reads nations, not the player."""
        world = self._world("ALLIANCE")
        region = world.get_region("Belgium")
        region.controller = "France"
        assert world.get_effective_supply_cap("Prussia", region) == int(
            region.supply_capacity * world.HOME_SUPPLY_MULTIPLIER)

    def test_attrition_pass_inherits_the_table(self):
        """Behavioral: an over-base stack on ALLIED soil under the fed cap
        pays nothing; the same stack on a stranger's soil bleeds."""
        for state, expect_events in (("ALLIANCE", False), ("PEACE", True)):
            ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                          strength=40000)
            world = WorldFactory.with_marshals([ney])
            _pair(world, "France", "Prussia", state)
            world.get_region("Belgium").controller = "Prussia"
            # Belgium base 35,000: 40,000 is over base, under 1.5× (52,500).
            events = [e for e in world.process_supply_attrition()
                      if e.get("marshal") == "Ney"]
            assert bool(events) is expect_events, (state, events)

    def test_strangled_shore_strips_the_allied_table_too(self, monkeypatch):
        """HC-4a interplay: Britain blockading an allied coast starves the
        guest exactly as it would the owner."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium")
        world = WorldFactory.with_marshals([ney])
        _pair(world, "France", "Prussia", "ALLIANCE")
        _pair(world, "France", "Britain", "WAR")
        region = world.get_region("Belgium")
        region.controller = "Prussia"
        region.is_coastal = True
        world.fleets = {"Britain": {"ships": 100, "readiness": 80,
                                    "posture": "blockade",
                                    "home_ports": [], "dockyards": []}}
        import backend.game_logic.naval as naval_mod
        monkeypatch.setattr(naval_mod, "shore_supply_state",
                            lambda w, n, r: "strangled")
        assert world.get_effective_supply_cap(
            "France", region) == region.supply_capacity


class TestD2DispatchNamesTheSplit:
    def _famine_world(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=90000)
        world = WorldFactory.with_marshals([ney], current_turn=6)
        _pair(world, "France", "Prussia", "ALLIANCE")
        world.get_region("Belgium").controller = "Prussia"
        for turn in (5, 6):
            world.event_log.append({
                "type": "supply_attrition", "nation": "France",
                "region": "Belgium", "marshal": "Ney",
                "losses": 2000, "turn": turn})
        return world

    def test_remedy_names_a_neighbour_with_numbers(self):
        from backend.game_logic import dispatch as dispatch_mod

        world = self._famine_world()
        candidate = dispatch_mod._supply_strain_candidate(world, "France")
        assert candidate is not None
        remedy = candidate["fields"]["remedy"]
        assert "can feed" in remedy, remedy
        assert "a corps marched there ends it" in remedy

    def test_fed_ally_soil_names_the_host_not_a_refusal(self):
        """'Not controlled by France' is the wrong story on soil that
        feeds us as our own."""
        from backend.game_logic import dispatch as dispatch_mod

        world = self._famine_world()
        candidate = dispatch_mod._supply_strain_candidate(world, "France")
        remedy = candidate["fields"]["remedy"]
        assert "not controlled by" not in remedy.lower()
        assert "magazines feed us as our own" in remedy

    def test_shown_equals_applied(self):
        """The named headroom derives from the SAME effective cap the
        attrition applies."""
        from backend.game_logic import dispatch as dispatch_mod

        world = self._famine_world()
        candidate = dispatch_mod._supply_strain_candidate(world, "France")
        region = world.get_region("Belgium")
        assert candidate["fields"]["capacity"] == (
            f"{world.get_effective_supply_cap('France', region):,}")


class TestD4TruceFloor:
    """PC15-D4 "The Congress Holds": the exhausted-pair exit writes the
    truce floor, returns unheld homeland, and P3.7 no longer marches
    through a fresh peace."""

    def _boot_1805(self):
        scenario = str(
            REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
            / "europe_1805.json")
        return WorldState.from_scenario(scenario)

    def _find_war(self, world, a, b):
        for war_id, war in (world.war_instances or {}).items():
            parts = war.get("active_participants") or []
            if (a in parts and b in parts
                    and war.get("ended_turn") is None):
                return war_id, war
        return "", {}

    def _arm_pair_exit(self, world, a, b):
        from backend.game_logic.settlement_third_party import (
            PAIR_EXIT_MIN_TURNS,
        )
        war_id, war = self._find_war(world, a, b)
        assert war_id, f"boot instance missing {a}|{b}"
        world.war_exhaustion[a] = 150
        world.war_exhaustion[b] = 150
        pair_key = world._make_diplo_key(a, b)
        meta = war.get("diplo_key_meta", {}).get(pair_key)
        assert meta is not None
        meta["joined_turn"] = int(world.current_turn) - (
            PAIR_EXIT_MIN_TURNS + 2)
        world.war_scores[pair_key] = 0
        return pair_key

    def test_exit_writes_the_floor_and_still_fires(self):
        from backend.game_logic.settlement_third_party import (
            PAIR_EXIT_TRUCE_FLOOR_TURNS,
            process_third_party_settlements,
        )
        world = self._boot_1805()
        pair_key = self._arm_pair_exit(world, "Spain", "Britain")
        events = process_third_party_settlements(world)
        assert any(e.get("type") == "third_party_peace" for e in events), (
            "the [r5] exit regressed — the floor must never un-end wars")
        assert world.get_diplomatic_state("Spain", "Britain") == "PEACE"
        assert world.armistice_cooldowns.get(pair_key) == (
            PAIR_EXIT_TRUCE_FLOOR_TURNS)

    def test_floored_pair_cannot_redeclare(self):
        from backend.game_logic.diplomacy import declare_war
        from backend.game_logic.settlement_third_party import (
            process_third_party_settlements,
        )
        world = self._boot_1805()
        self._arm_pair_exit(world, "Spain", "Britain")
        process_third_party_settlements(world)
        result = declare_war(world, "Spain", "Britain")
        assert result.get("success") is False, (
            "the truce floor did not gate re-declaration")
        assert not world.is_at_war("Spain", "Britain")

    def test_unheld_homeland_returns_and_held_ground_stays(self):
        """The Moravia shape: a home province held with NO standing army
        returns at the exit; an army-occupied one stays (uti
        possidetis)."""
        from backend.game_logic.settlement_third_party import (
            process_third_party_settlements,
        )
        world = self._boot_1805()
        self._arm_pair_exit(world, "Bavaria", "Austria")
        austrian_home = list(
            world.nation_starting_regions.get("Austria", []))
        unheld, held = austrian_home[0], austrian_home[1]
        world.get_region(unheld).controller = "Bavaria"
        world.get_region(held).controller = "Bavaria"
        # Stand a Bavarian marshal on `held` only.
        bav = [m for m in world.marshals.values()
               if m.nation == "Bavaria" and m.strength > 0]
        assert bav, "the 1805 boot has a Bavarian marshal"
        bav[0].location = held
        world.invalidate_active_nations_cache()
        events = process_third_party_settlements(world)
        peace = [e for e in events
                 if e.get("type") == "third_party_peace"
                 and {e.get("proposer"), e.get("accepter")}
                 == {"Bavaria", "Austria"}]
        assert peace, "the Bavaria|Austria pair did not exit"
        assert world.get_region(unheld).controller == "Austria", (
            "the unreturned-homeland landmine survives the peace")
        assert world.get_region(held).controller == "Bavaria", (
            "army-held ground must stay (uti possidetis)")
        assert unheld in peace[0]["consequence"]

    def test_p37_never_marches_through_a_peace(self):
        """P3.7 was the ONLY attack rung with no war-state filter."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        from tests.conftest import MarshalFactory, WorldFactory

        marshal = MarshalFactory.enemy(name="Charles", location="Vienna",
                                       nation="Prussia", strength=30000)
        world = WorldFactory.with_marshals([marshal])
        home = list(world.nation_starting_regions.get("Prussia", []))
        assert home, "legacy world seeds Prussian homeland"
        lost = home[0]
        lost_region = world.get_region(lost)
        lost_region.controller = "Britain"
        lost_region.garrison_strength = 0
        lost_region.garrison_detachment = False
        # Stand him ADJACENT to the lost province (the dist-1 undefended
        # branch — the one the measured Moravia re-declaration took).
        marshal.location = list(lost_region.adjacent_regions)[0]
        ai = EnemyAI(CommandExecutor())
        # Per-turn transients the nation-turn entry normally seeds.
        ai._recapture_marshal_assignments = {}
        ai._recapture_targets_claimed = set()
        for state, expect_action in (("PEACE", False), ("WAR", True)):
            _pair(world, "Prussia", "Britain", state)
            action = ai._find_homeland_defense(marshal, "Prussia", world)
            assert bool(action) is expect_action, (state, action)

    def test_congress_beat_renders_exactly_once(self):
        from tests.conftest import MarshalFactory, WorldFactory
        from backend.game_logic import dispatch as dispatch_mod

        for age, expect in ((0, True), (1, False)):
            ney = MarshalFactory.infantry(name="Ney")
            world = WorldFactory.with_marshals([ney], current_turn=9)
            world.event_log = [{
                "type": "third_party_peace", "proposer": "Austria",
                "accepter": "Bavaria", "turn": 9 - age}]
            head = dispatch_mod._build_headline(world, "France") or {}
            got = head.get("class") == "europe_congress"
            assert got is expect, (age, head)


class TestD3TutorialExpectationDormancy:
    def _lesson_world(self):
        scenario = str(
            REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
            / "tutorial_1805.json")
        return WorldState.from_scenario(scenario)

    def test_lesson_world_is_dotation_dormant(self):
        from backend.game_logic.dotation import (
            dotation_dormant,
            is_dotation_world,
        )
        world = self._lesson_world()
        assert world.scenario_name == "tutorial"
        assert dotation_dormant(world) is True
        assert is_dotation_world(world) is False

    def test_no_erosion_inside_the_school(self):
        """Battles won in the lesson build NO expectation state: the
        grace clock never opens and trust is byte-identical across the
        processor tick."""
        world = self._lesson_world()
        ney = world.get_marshal("Ney")
        ney.battles_won = 4
        trust_before = int(ney.trust.value)
        grace_before = int(getattr(ney, "expectation_grace_turn", -1))
        world._process_dotation_state()
        assert int(ney.trust.value) == trust_before
        assert int(getattr(ney, "expectation_grace_turn", -1)) == grace_before
        assert not getattr(world, "_dotation_processed_turn", None), (
            "the processor ran in the lesson — the dormancy gate leaked")

    def test_campaign_world_still_fires(self):
        """The leak-into-campaign regression arm: an identical state on a
        campaign world processes normally."""
        from backend.game_logic.dotation import is_dotation_world
        from tests.conftest import MarshalFactory, WorldFactory

        ney = MarshalFactory.infantry(name="Ney")
        world = WorldFactory.with_marshals([ney])
        world.sovereign_map = "europe"
        world.scenario_name = "campaign"
        assert is_dotation_world(world) is True
        world._process_dotation_state()
        assert getattr(world, "_dotation_processed_turn", None) == (
            world.current_turn), "the processor did not run on a campaign"

    def test_processor_consults_the_chokepoint(self, monkeypatch):
        """Mutation-style pin: the processor reads is_dotation_world (ONE
        rule, one implementation) — flip the predicate and it goes
        quiet, so the old inline duplicate can never silently return."""
        from tests.conftest import MarshalFactory, WorldFactory
        import backend.game_logic.dotation as dotation_mod

        ney = MarshalFactory.infantry(name="Ney")
        world = WorldFactory.with_marshals([ney])
        world.sovereign_map = "europe"
        world.scenario_name = "campaign"
        monkeypatch.setattr(dotation_mod, "is_dotation_world",
                            lambda w: False)
        world._process_dotation_state()
        assert getattr(world, "_dotation_processed_turn", None) is None


class TestD2TutorialFamineEnds:
    def test_the_school_stack_is_fed_on_allied_swabia(self):
        """The school's own beats co-locate ~50,000 men on Bavarian soil;
        under the Ally's Table the corridor feeds them (no script edit —
        the scenario already authors the alliance)."""
        scenario = str(
            REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
            / "tutorial_1805.json")
        world = WorldState.from_scenario(scenario)
        swabia = world.get_region("Swabia")
        munich = world.get_region("Munich")
        # Swabia and Munich are Bavarian; France|Bavaria boots ALLIANCE.
        assert world.get_diplomatic_state("France", "Bavaria") == "ALLIANCE"
        for region in (swabia, munich):
            if region is None or region.controller != "Bavaria":
                continue
            assert world.get_effective_supply_cap("France", region) == int(
                region.supply_capacity * world.HOME_SUPPLY_MULTIPLIER)
