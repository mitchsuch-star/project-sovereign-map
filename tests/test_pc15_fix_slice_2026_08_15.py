"""The PC15 fix slice — pins for the Aug 15, 2026 comprehensive-playtest rows.

Rows fixed here (docs/BUG_FIXES.md §Comprehensive Playtest PC15):
  PC15-1  a destroyed marshal vanishes silently (+ the captured-prisoner
          deletion sibling on the glorious-charge / coordinated-cleanup pops)
  PC15-2  a pending order-bound interrupt swallows explicitly-addressed
          commands (dead names included — the guard was roster-bound)
  PC15-3  a stale settlement pair-substitute confirm wedges later proposals
  PC15-4  a dead marshal's name silently commands a different marshal
  PC15-9  tutorial beat VI anchor (gate widened; ambient-RNG window pinned)
  plus the P2/P3 sweep rows 6/7/11/12/13/14/17.

Design-gated rows (PC15-5 neutral soil, PC15-15 truce floor, PC15-D1..D4)
are deliberately NOT touched.
"""

import random
import re
from pathlib import Path

import pytest

from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
TUTORIAL_SCENARIO = str(
    REPO / "godot-client" / "project-sovereign" / "assets" / "maps"
    / "tutorial_1805.json")


def _read(rel: str) -> str:
    return (REPO / "godot-client" / "project-sovereign" / rel).read_text(
        encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# PC15-9 — tutorial beat VI ("The Guns Speak") anchor
# ═══════════════════════════════════════════════════════════════════════════


class TestPC15n9TutorialBombardmentWindow:
    def test_bombardment_gate_is_two(self):
        """The beat opens the first turn the guns can legally fire (marched
        T1, laid overnight) — a gate of 3 left exactly ONE guaranteed player
        turn before Austria's reaction to Kienmayer's fate could rotate
        Jellacic off the Tyrol anchor."""
        overlay = _read("scripts/tutorial_overlay.gd")
        step = re.search(
            r'"id":\s*"bombardment".*?"turn_gate":\s*(\d+)', overlay, re.S)
        assert step, "bombardment step lost from the tutor step table"
        assert int(step.group(1)) == 2

    def test_bombardment_body_names_the_fallback(self):
        """TUT-F4c idiom: a beat the war can refuse SAYS what to do when the
        anchor slips (the school moves on; any enemy in reach serves)."""
        overlay = _read("scripts/tutorial_overlay.gd")
        step = re.search(
            r'"id":\s*"bombardment".*?"body":\s*"([^"]*)"', overlay, re.S)
        assert step
        body = step.group(1)
        assert "slip away" in body
        assert "school will move on" in body

    @pytest.mark.parametrize("seed", [0, 1, 2])
    def test_jellacic_holds_tyrol_through_the_widened_window(self, seed):
        """Why the old pins held while the live run drifted: the variance is
        the GLOBAL combat RNG (Kienmayer's fate against the player's corps),
        which no campaign-seed pin covers. This pin seeds that RNG and walks
        the actual enemy phases: Jellacic must still hold Tyrol at the start
        of player turns 2 AND 3 — the widened window both gate turns wide."""
        from backend.game_logic.turn_manager import TurnManager

        random.seed(seed)
        world = WorldState.from_scenario(TUTORIAL_SCENARIO)
        tm = TurnManager(world)
        for expected_turn in (2, 3):
            tm.end_turn({"world": world})
            assert world.current_turn == expected_turn
            jellacic = world.marshals.get("Jellacic")
            assert jellacic is not None, (
                f"seed {seed}: Jellacic gone by T{expected_turn}")
            assert jellacic.location == "Tyrol", (
                f"seed {seed}: Jellacic left Tyrol by T{expected_turn} "
                f"(at {jellacic.location}) — beat VI's anchor broke")


# ═══════════════════════════════════════════════════════════════════════════
# PC15-1 — a destroyed marshal must never vanish silently
# ═══════════════════════════════════════════════════════════════════════════


class TestPC15n1DestroyMarshalSeam:
    def _world(self):
        from tests.conftest import MarshalFactory, WorldFactory
        ney = MarshalFactory.infantry(name="Ney")
        return WorldFactory.with_marshals([ney], current_turn=7)

    def test_destroy_records_tombstone_and_event(self):
        world = self._world()
        ney = world.marshals["Ney"]
        ney.location = "Belgium"
        assert world.destroy_marshal(ney, cause="battle", victor="Austria")
        assert "Ney" not in world.marshals
        tomb = world.fallen_marshals["Ney"]
        assert tomb["nation"] == "France"
        assert tomb["turn"] == 7
        assert tomb["location"] == "Belgium"
        assert tomb["cause"] == "battle"
        events = [e for e in world.event_log
                  if e.get("type") == "marshal_destroyed"]
        assert len(events) == 1
        assert events[0]["marshal"] == "Ney"
        assert events[0]["victor"] == "Austria"

    def test_a_prisoner_is_never_destroyed_by_a_strength_check(self):
        """The PC15-1 sibling: capture sets strength=0 BY DESIGN (W6-7),
        and the glorious-charge / coordinated-cleanup pops ran after the
        capture arm — deleting the prisoner the same tick his capture
        event was written. The rule now lives in the one seam."""
        world = self._world()
        ney = world.marshals["Ney"]
        ney.strength = 0
        ney.captured_by = "Austria"
        assert world.destroy_marshal(ney, cause="battle") is False
        assert "Ney" in world.marshals, "the prisoner was deleted"
        assert "Ney" not in world.fallen_marshals
        assert not [e for e in world.event_log
                    if e.get("type") == "marshal_destroyed"]

    def test_string_form_and_missing_name(self):
        world = self._world()
        assert world.destroy_marshal("Ney", cause="attrition")
        assert "Ney" in world.fallen_marshals
        assert world.destroy_marshal("Ney", cause="attrition") is False
        assert world.destroy_marshal("Nobody", cause="battle") is False

    def test_log_false_still_tombstones(self):
        world = self._world()
        assert world.destroy_marshal("Ney", cause="dismissed", log=False)
        assert world.fallen_marshals["Ney"]["cause"] == "dismissed"
        assert not [e for e in world.event_log
                    if e.get("type") == "marshal_destroyed"]

    def test_fallen_roster_survives_serialization(self):
        world = self._world()
        world.destroy_marshal("Ney", cause="battle", victor="Austria")
        from backend.models.world_state import WorldState
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.fallen_marshals["Ney"]["cause"] == "battle"
        assert reloaded.fallen_marshals["Ney"]["turn"] == 7

    def test_attrition_sweep_reaches_the_event_log(self):
        """The old `marshal_eliminated` type was never in
        CAMPAIGN_LOG_TYPES — the sweep's kills were invisible. The sweep
        now funnels through destroy_marshal: tombstone + a
        `marshal_destroyed` row in world.event_log."""
        world = self._world()
        ney = world.marshals["Ney"]
        ney.strength = 0
        events = world.process_supply_attrition()
        assert "Ney" not in world.marshals
        assert world.fallen_marshals["Ney"]["cause"] == "attrition"
        assert any(e.get("type") == "marshal_destroyed"
                   and e.get("marshal") == "Ney" for e in events)
        assert any(e.get("type") == "marshal_destroyed"
                   and e.get("marshal") == "Ney" for e in world.event_log)

    def test_no_bare_pop_survives_outside_the_seam(self):
        """Census guard (the IGR-E whole-backend idiom): every removal of a
        marshal from world.marshals funnels through destroy_marshal. The
        only sanctioned raw pops are destroy_marshal itself and
        _eliminate_nation's prisoner arm — both in world_state.py."""
        backend_dir = REPO / "backend"
        offenders = []
        for path in backend_dir.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            pops = text.count("marshals.pop(")
            dels = len(re.findall(
                r"del\s+(?:world|self)\.marshals\[", text))
            if path.name == "world_state.py":
                assert pops == 2, (
                    f"world_state.py sanctioned-pop count moved ({pops}) — "
                    "re-audit destroy_marshal/_eliminate_nation")
                pops = 0
            if pops or dels:
                offenders.append((str(path), pops, dels))
        assert not offenders, offenders


class TestPC15n1CampaignLogVocabulary:
    def test_type_registered(self):
        from backend.campaign_log import CAMPAIGN_LOG_TYPES, CATEGORY_MAP
        assert "marshal_destroyed" in CAMPAIGN_LOG_TYPES
        assert CATEGORY_MAP.get("marshal_destroyed") == "combat"

    def test_oneliner_arms(self):
        from backend.campaign_log import format_event_oneliner
        line = format_event_oneliner({
            "type": "marshal_destroyed", "marshal": "Ney",
            "location": "Ulm", "victor": "Austria", "cause": "battle"})
        assert "Ney" in line and "DESTROYED" in line and "Austria" in line
        starved = format_event_oneliner({
            "type": "marshal_destroyed", "marshal": "Ney",
            "location": "Tyrol", "cause": "attrition"})
        assert "attrition" in starved

    def _filter(self, world, event):
        from backend.campaign_log import filter_campaign_log
        world.event_log = [dict(event, turn=world.current_turn)]
        return filter_campaign_log(world.event_log, world)

    def test_fog_own_fall_always_visible(self):
        from tests.conftest import MarshalFactory, WorldFactory
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney")], current_turn=5)
        rows = self._filter(world, {
            "type": "marshal_destroyed", "marshal": "Ney",
            "nation": "France", "victor": "Austria", "location": "Spain"})
        assert len(rows) == 1

    def test_fog_enemy_fall_by_our_hand_visible(self):
        from tests.conftest import MarshalFactory, WorldFactory
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney")], current_turn=5)
        rows = self._filter(world, {
            "type": "marshal_destroyed", "marshal": "Mack",
            "nation": "Austria", "victor": "France", "location": "Ulm"})
        assert len(rows) == 1

    def test_fog_third_party_fall_needs_intel(self):
        from tests.conftest import MarshalFactory, WorldFactory
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney")], current_turn=5)
        world.region_intel = {}
        rows = self._filter(world, {
            "type": "marshal_destroyed", "marshal": "Mack",
            "nation": "Austria", "victor": "Russia",
            "location": "NowhereVisible"})
        assert rows == []


class TestPC15n1DispatchLadder:
    """Mirrors CA9-F12's capture ladder: own loss / our kill / third party."""

    @staticmethod
    def _world_with(event):
        from tests.conftest import MarshalFactory, WorldFactory
        ney = MarshalFactory.infantry(name="Ney")
        world = WorldFactory.with_marshals([ney], current_turn=5)
        world.event_log = [dict(event, turn=5)]
        return world

    @staticmethod
    def _headline(world):
        from backend.game_logic import dispatch as dispatch_mod
        return dispatch_mod._build_headline(world, "France") or {}

    def test_own_fall_leads_the_briefing(self):
        head = self._headline(self._world_with({
            "type": "marshal_destroyed", "marshal": "Ney",
            "nation": "France", "victor": "Austria", "location": "Ulm",
            "cause": "battle"}))
        assert head.get("class") == "marshal_destroyed", head
        assert "DESTROYED" in head["text"]
        assert "Ney" in head["text"] and "Ulm" in head["text"]

    def test_annihilation_outranks_capture(self):
        from backend.game_logic.dispatch import HEADLINE_WEIGHTS as w
        assert w["marshal_destroyed"] > w["marshal_captured"]
        assert w["enemy_marshal_destroyed"] > w["enemy_marshal_captured"]
        assert w["enemy_marshal_destroyed"] < w["own_broken"]

    def test_our_kill_is_a_triumph_class(self):
        head = self._headline(self._world_with({
            "type": "marshal_destroyed", "marshal": "Mack",
            "nation": "Austria", "victor": "France", "location": "Ulm",
            "cause": "battle"}))
        assert head.get("class") == "enemy_marshal_destroyed", head
        assert "Mack" in head["text"]

    def test_third_party_fall_is_no_candidate(self):
        """Gate CA8-D6: a third party's kill is never our triumph, and is
        not our wound either."""
        head = self._headline(self._world_with({
            "type": "marshal_destroyed", "marshal": "Mack",
            "nation": "Austria", "victor": "Russia", "location": "Ulm",
            "cause": "battle"}))
        assert head.get("class") not in (
            "marshal_destroyed", "enemy_marshal_destroyed"), head

    def test_berthier_notes_exist_for_both_classes(self):
        from backend.game_logic.dispatch import _HEADLINE_BERTHIER_NOTES
        assert "marshal_destroyed" in _HEADLINE_BERTHIER_NOTES
        assert "enemy_marshal_destroyed" in _HEADLINE_BERTHIER_NOTES


# ═══════════════════════════════════════════════════════════════════════════
# PC15-2 — a pending interrupt must not swallow addressed commands
# PC15-4 — a dead marshal's name refuses, never substitutes
# ═══════════════════════════════════════════════════════════════════════════


def _two_marshal_war_world():
    from tests.conftest import MarshalFactory, WorldFactory
    soult = MarshalFactory.infantry(name="Soult", location="Belgium",
                                    strength=20000, personality="cautious")
    davout = MarshalFactory.infantry(name="Davout", location="Rhine",
                                     strength=20000, personality="cautious")
    enemy = MarshalFactory.enemy(name="Buxhowden", location="Belgium",
                                 nation="Austria", strength=15000,
                                 personality="cautious")
    world = WorldFactory.with_marshals([soult, davout, enemy])
    key = "|".join(sorted(["France", "Austria"]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn
    return world


@pytest.fixture()
def pc15_endpoint():
    from fastapi.testclient import TestClient

    from backend.commands.executor import CommandExecutor
    from backend.commands.parser import CommandParser
    import backend.main as main_module

    saved = (main_module.parser, main_module.world,
             main_module.game_state, main_module.executor)
    main_module.parser = CommandParser(use_real_llm=False)
    main_module.world = _two_marshal_war_world()
    main_module.game_state = {"world": main_module.world}
    main_module.executor = CommandExecutor()
    try:
        yield TestClient(main_module.app), main_module
    finally:
        (main_module.parser, main_module.world,
         main_module.game_state, main_module.executor) = saved


class TestPC15n2InterruptRouteAddressGuard:
    def _arm_interrupt(self, world, name="Soult",
                       interrupt_type="destination_blocked",
                       options=None, **extra):
        m = world.get_marshal(name)
        m.pending_interrupt = dict({
            "marshal": name,
            "interrupt_type": interrupt_type,
            "options": options or ["attack", "go_around", "cancel_order"],
        }, **extra)
        return m

    def test_dead_name_address_is_not_an_interrupt_answer(self, pc15_endpoint):
        """The flagship T19 hit: 'Murat, attack Buxhowden' (Murat destroyed)
        was consumed as SOULT's destination_blocked answer because the
        addressed-other check was roster-bound. The leading address token is
        now honoured whether or not the name still lives."""
        client, m = pc15_endpoint
        m.world.fallen_marshals["Murat"] = {
            "nation": "France", "turn": 3, "location": "Ulm",
            "cause": "battle"}
        self._arm_interrupt(m.world, "Soult")
        resp = client.post(
            "/command", json={"command": "Murat, attack Buxhowden"}).json()
        # Not consumed: the interrupt still stands (a decision with options
        # is preserved), and the reply is about MURAT, not Soult's battle.
        assert m.world.get_marshal("Soult").pending_interrupt is not None
        assert "Murat" in resp.get("message", "")
        assert "lost to us" in resp.get("message", "")

    def test_living_other_marshal_address_still_falls_through(self, pc15_endpoint):
        """CONTROL — the arm that always worked is untouched."""
        client, m = pc15_endpoint
        self._arm_interrupt(m.world, "Soult")
        client.post("/command", json={"command": "Davout, hold position"})
        assert m.world.get_marshal("Soult").pending_interrupt is not None

    def test_same_marshal_fresh_order_elsewhere_falls_through(self, pc15_endpoint):
        """The naval T8 hit: 'Davout, march to London' while Davout held a
        cannon_fire interrupt resolved as "investigate" and the order was
        eaten. An addressed command naming foreign ground is a fresh order."""
        client, m = pc15_endpoint
        self._arm_interrupt(
            m.world, "Davout", interrupt_type="cannon_fire",
            options=["investigate", "continue_order", "cancel_order"],
            location="Rhine")
        resp = client.post(
            "/command", json={"command": "Davout, march to Picardy"}).json()
        # Never consumed as "investigate": the response is a real order
        # outcome for Davout (move/strategic), not an interrupt echo.
        assert "investigate" not in str(resp.get("message", "")).lower()

    def test_bare_answers_still_route(self, pc15_endpoint):
        """Sweep-5 contract untouched: an un-addressed 'press on' answers
        the pending interrupt."""
        client, m = pc15_endpoint
        self._arm_interrupt(
            m.world, "Soult", interrupt_type="contact_bad_odds",
            options=["attack_anyway", "hold_position", "cancel_order"])
        client.post("/command", json={"command": "press on"})
        assert m.world.get_marshal("Soult").pending_interrupt is None, (
            "the bare affirmative stopped routing — over-correction")

    def test_addressed_answer_to_own_marshal_still_routes(self, pc15_endpoint):
        """'Soult, press on' names the interrupt's OWN marshal and no
        foreign ground — it is an answer and must keep routing."""
        client, m = pc15_endpoint
        self._arm_interrupt(
            m.world, "Soult", interrupt_type="contact_bad_odds",
            options=["attack_anyway", "hold_position", "cancel_order"])
        client.post("/command", json={"command": "Soult, press on"})
        assert m.world.get_marshal("Soult").pending_interrupt is None

    def test_attack_naming_the_interrupts_own_enemy_still_routes(self, pc15_endpoint):
        """'Soult, attack Buxhowden' where Buxhowden IS the interrupt's
        enemy is the answer 'attack', not a fresh order."""
        client, m = pc15_endpoint
        self._arm_interrupt(
            m.world, "Soult", interrupt_type="destination_blocked",
            options=["attack", "go_around", "cancel_order"],
            enemy="Buxhowden", location="Belgium")
        client.post("/command", json={"command": "Soult, attack Buxhowden"})
        assert m.world.get_marshal("Soult").pending_interrupt is None


class TestPC15n4FallenNameRefusal:
    def test_dead_name_refuses_and_no_substitute_acts(self, pc15_endpoint):
        """The flagship T23 hit: 'Ney, attack Archduke Charles' with Ney
        destroyed fell back to the fast parser's bare attack and SOULT's
        muster ran. The address seam now reads the roster of the dead."""
        client, m = pc15_endpoint
        m.world.fallen_marshals["Ney"] = {
            "nation": "France", "turn": 5, "location": "Ulm",
            "cause": "battle"}
        before_ap = int(m.world.actions_remaining)
        resp = client.post(
            "/command", json={"command": "Ney, attack Buxhowden"}).json()
        assert resp.get("success") is False
        assert "Ney is lost to us" in resp.get("message", "")
        assert "Ulm" in resp.get("message", "")
        assert int(m.world.actions_remaining) == before_ap, (
            "the refusal cost AP — something still executed")
        # And the enemy was never attacked by a substitute.
        assert m.world.get_marshal("Buxhowden").strength == 15000

    def test_captured_name_refuses_with_his_fate(self, pc15_endpoint):
        client, m = pc15_endpoint
        soult = m.world.get_marshal("Soult")
        soult.strength = 0
        soult.captured_by = "Austria"
        resp = client.post(
            "/command", json={"command": "Soult, attack Buxhowden"}).json()
        assert resp.get("success") is False
        assert "prisoner" in resp.get("message", "")
        assert "Austria" in resp.get("message", "")

    def test_living_marshal_unaffected(self, pc15_endpoint):
        """CONTROL: a living addressed marshal parses normally."""
        client, m = pc15_endpoint
        resp = client.post(
            "/command", json={"command": "Davout, hold position"}).json()
        assert "lost to us" not in str(resp.get("message", ""))
        assert "prisoner" not in str(resp.get("message", ""))

    def test_never_existed_name_keeps_the_cr2_clarify(self, pc15_endpoint):
        """A name with no tombstone is NOT ours to refuse — the CR-2
        unknown-name clarify (or its refusal) owns it."""
        client, m = pc15_endpoint
        resp = client.post(
            "/command", json={"command": "Wellington, attack Buxhowden"}).json()
        assert "lost to us" not in str(resp.get("message", ""))

    def test_attacking_a_destroyed_enemy_answers_honestly(self):
        """The enemy side: 'attack Mack' after his annihilation fell
        through to region fuzzy-matching. The tombstone answers."""
        from backend.commands.combat_executor import CombatExecutor
        from backend.commands.executor import CommandExecutor

        world = _two_marshal_war_world()
        world.destroy_marshal("Buxhowden", cause="battle", victor="France")
        executor = CommandExecutor()
        combat = CombatExecutor(executor)
        resolution = combat._resolve_auto_assign_attacker(
            {"action": "attack", "target": "Buxhowden"}, world)
        assert resolution["kind"] == "error"
        msg = resolution["error"]["message"]
        assert "no longer exists" in msg
        assert "Belgium" in msg


# ═══════════════════════════════════════════════════════════════════════════
# PC15-3 — the stale settlement pair-substitute confirm wedge
# ═══════════════════════════════════════════════════════════════════════════


def _pair_substitute_chooser(turn_created=None):
    dlg = {
        "type": "settlement_pair_substitute_confirm",
        "dialogue_type": "settlement_pair_substitute_confirm",
        "selected_target_nation": "Austria",
        "war_id": "war_1",
        "available_action_ids": ["confirm_pair_substitute",
                                 "keep_joint_settlement"],
        "options": [
            {"action": "confirm_pair_substitute",
             "label": "Proceed — peace with Austria alone"},
            {"action": "keep_joint_settlement",
             "label": "Stay with the joint settlement"},
        ],
        "blocking": True,
    }
    if turn_created is not None:
        dlg["turn_created"] = turn_created
    return dlg


class TestPC15n3SettlementConfirmWedge:
    def test_chooser_is_a_named_hard_stop(self):
        from backend.commands.dialogue_routing import hard_stop_subject
        from backend.models.dialogue_manager import DialogueManager
        assert ("settlement_pair_substitute_confirm"
                in DialogueManager.HARD_STOP_TYPES)
        subject = hard_stop_subject(_pair_substitute_chooser())
        assert "joint settlement" in subject

    def test_typed_confirm_and_keep_resolve_the_chooser(self):
        """The wedge's engine: typed 'confirm' mapped only to actions the
        chooser does not offer, so the word fell through to the parser
        while the chooser stayed mounted — eight loops measured."""
        from backend.commands.dialogue_routing import match_dialogue_answer
        chooser = _pair_substitute_chooser()
        assert match_dialogue_answer(chooser, "confirm") is not None
        assert match_dialogue_answer(chooser, "proceed") is not None
        assert match_dialogue_answer(chooser, "keep") is not None
        assert match_dialogue_answer(chooser, "no") is not None

    def test_dialogue_court_reads_the_selected_target(self):
        from backend.commands.dialogue_routing import dialogue_court
        assert dialogue_court(_pair_substitute_chooser()) == "Austria"

    def test_clear_stale_sweeps_the_queue(self):
        """A stale dialogue displaced into the QUEUE was immortal —
        clear_stale only ever inspected the active slot — and was promoted
        turns later to eat every subsequent 'confirm'."""
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        dm.push(_pair_substitute_chooser(turn_created=3))
        # Displace it into the queue behind a fresh current.
        dm.preempt({"type": "advisory", "turn_created": 10,
                    "blocking": False})
        assert len(dm.iter_queue()) == 1
        # Past the blocking timeout: 3 + 2 < 10.
        dm.clear_stale(10)
        assert dm.iter_queue() == [], "the stale queued chooser survived"

    def test_clear_stale_queue_sweep_spares_mailbox_items(self):
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        dm.push({"type": "incoming_settlement_offer", "turn_created": 1,
                 "blocking": False})
        dm.preempt({"type": "advisory", "turn_created": 10,
                    "blocking": False})
        dm.clear_stale(10)
        types = [d.get("type") for d in dm.iter_queue()]
        assert "incoming_settlement_offer" in types

    def test_clear_stale_queue_sweep_keeps_fresh_items(self):
        from backend.models.dialogue_manager import DialogueManager
        dm = DialogueManager()
        dm.push(_pair_substitute_chooser(turn_created=10))
        dm.preempt({"type": "advisory", "turn_created": 10,
                    "blocking": False})
        dm.clear_stale(10)
        assert len(dm.iter_queue()) == 1

    def test_chooser_mount_stamps_turn_created(self):
        """The chooser was the only staged dialogue without turn_created —
        clear_stale read it as turn 0. Source pin on the push site."""
        src = (REPO / "backend" / "game_logic"
               / "settlement_actions.py").read_text(encoding="utf-8")
        idx = src.index("_build_pair_substitute_confirm_dialogue(\n        dialogue,")
        window = src[idx:idx + 800]
        assert 'confirm_dialogue["turn_created"]' in window
        assert "dialogue_manager.replace(confirm_dialogue)" in window

    def test_unrelated_command_names_the_blocker(self, pc15_endpoint):
        """PT-A3 discipline over the endpoint: with the chooser active, an
        ordinary order is refused NAMING the choice — never silently
        passed through while the chooser blocks proposals."""
        client, m = pc15_endpoint
        m.world.dialogue_manager.push(_pair_substitute_chooser(
            turn_created=int(m.world.current_turn)))
        resp = client.post(
            "/command", json={"command": "Davout, hold position"}).json()
        assert resp.get("success") is False
        assert "joint settlement" in (resp.get("message") or "")
        assert m.world.pending_diplomatic_dialogue is not None
        m.world.dialogue_manager.pop()

    def test_driver_answers_the_chooser(self):
        import sys
        sys.path.insert(0, str(REPO / "tools"))
        try:
            import playtest_driver
        finally:
            sys.path.pop(0)
        assert ("settlement_pair_substitute_confirm"
                in playtest_driver.DIALOGUE_TYPE_ANSWERS)


# ═══════════════════════════════════════════════════════════════════════════
# The P2/P3 sweep — PC15-6 / 7 / 11 / 12 / 13 / 17
# (PC15-14's pin lives in test_mc_q3_command_rally.py, flipped consciously)
# ═══════════════════════════════════════════════════════════════════════════


class TestPC15n6RequestTermsNamesTheSubstitution:
    def test_template_names_both_courts_and_the_why(self):
        from backend.game_logic.diplomatic_templates import (
            resolve_settlement_voice_line,
        )
        line = resolve_settlement_voice_line(
            "settlement_request_terms_sent_for_court_talleyrand",
            court="Britain", named_court="Austria",
            war_label="the war of the coalition")
        assert "Austria" in line
        assert "Britain" in line
        assert "leader's to name" in line


class TestPC15n7DiversionQuoteConfirm:
    def _naval_world(self):
        from tests.conftest import MarshalFactory, WorldFactory
        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney")])
        world.fleets = {
            "France": {"ships": 40, "readiness": 53, "posture": "port",
                       "home_ports": ["Brittany"], "dockyards": []},
            "Britain": {"ships": 100, "readiness": 80, "posture": "blockade",
                        "home_ports": ["London"], "dockyards": []},
        }
        key = "|".join(sorted(["France", "Britain"]))
        world.diplomatic_states[key] = "WAR"
        world.war_start_turns[key] = world.current_turn
        return world

    def _executor(self):
        from backend.commands.executor import CommandExecutor
        from backend.commands.naval_executor import NavalExecutor
        return NavalExecutor(CommandExecutor())

    def test_bare_diversion_quotes_and_does_not_burn_the_attempt(self):
        """The naval-descent T5 loss: 'order the diversion' at readiness 53
        resolved instantly and cost 46 sail. The typed path now states its
        terms first — and the once-per-war latch is untouched by the quote."""
        world = self._naval_world()
        result = self._executor()._execute_naval_diversion(
            {"action": "naval_diversion", "raw_input": "order the diversion"},
            {"world": world})
        assert result.get("naval_confirm") is True
        assert result.get("state") == "awaiting_clarification"
        msg = result.get("message", "")
        assert "once only" in msg
        # CONSCIOUS FLIP (Aug 30, 2026 review): this asserted the modal quoted
        # "her current readiness (53)" — and that sentence was false. The
        # failure arm docks EXPEDITION_TURNBACK_READINESS BEFORE the battle,
        # so she is brought to action at 43, not 53: shown was not applied on
        # the single number the player is being asked to bet a fleet on. The
        # quote now comes from `naval.diversion_failure_readiness`, the same
        # function `resolve_diversion` assigns from, so the two cannot drift.
        from backend.game_logic import naval as _naval
        _expected = _naval.diversion_failure_readiness(world.fleets["France"])
        assert _expected == 53 - _naval.EXPEDITION_TURNBACK_READINESS
        assert f"readiness {_expected}" in msg, msg
        assert not world.fleets["France"].get("diversion_used"), (
            "the quote consumed the once-per-war attempt")

    def test_confirmed_diversion_resolves(self):
        world = self._naval_world()
        result = self._executor()._execute_naval_diversion(
            {"action": "naval_diversion",
             "raw_input": "order the diversion confirmed"},
            {"world": world})
        assert result.get("state") != "awaiting_clarification"
        assert world.fleets["France"].get("diversion_used") is True

    def test_ai_path_is_untouched(self):
        """GR5: an AI actor's diversion resolves without the confirm gate
        (the rung already weighed it)."""
        world = self._naval_world()
        world.fleets["Britain"]["diversion_used"] = False
        result = self._executor()._execute_naval_diversion(
            {"action": "naval_diversion", "_acting_nation": "Britain"},
            {"world": world})
        assert result.get("state") != "awaiting_clarification"


class TestPC15n11RefusalNamesReasonAndRemedy:
    def test_structural_codes_have_their_own_sentences(self):
        from backend.display_names import settlement_disabled_reason_display
        one_to_one = settlement_disabled_reason_display("war_not_multi_party")
        assert "two courts" in one_to_one
        assert "Negotiate" in one_to_one
        pending = settlement_disabled_reason_display("offer_already_pending")
        assert "already on the desk" in pending
        generic = settlement_disabled_reason_display(
            "request_terms_ineligible")
        assert "bilateral peace" in generic, "the generic arm lost its remedy"


class TestPC15n12SupplyHeadlineGrammar:
    def test_singular_marshal_gets_singular_verbs(self):
        from backend.game_logic.dispatch import (
            _HEADLINE_TEMPLATES,
            _STANDING_ESCALATION,
        )
        fields = {"who": "Massena", "stand": "stands", "have": "has",
                  "strength": "21,858", "region": "Munich",
                  "capacity": "15,000", "over": "6,858",
                  "losses": "4,000 men", "turns": "4", "remedy": "Move."}
        primary = _HEADLINE_TEMPLATES["supply_strain"].format(**fields)
        assert "Massena stands 21,858 men" in primary
        variant = _STANDING_ESCALATION["supply_strain"][1].format(**fields)
        assert "Massena has been 4 turns over" in variant

    def test_candidate_builder_computes_the_verbs(self):
        from tests.conftest import MarshalFactory, WorldFactory
        from backend.game_logic import dispatch as dispatch_mod

        massena = MarshalFactory.infantry(name="Massena",
                                          location="Belgium",
                                          strength=200000)
        world = WorldFactory.with_marshals([massena], current_turn=6)
        for turn in (5, 6):
            world.event_log.append({
                "type": "supply_attrition", "nation": "France",
                "region": "Belgium", "marshal": "Massena",
                "losses": 2000, "turn": turn})
        candidate = dispatch_mod._supply_strain_candidate(world, "France")
        assert candidate is not None
        assert candidate["fields"]["stand"] == "stands"
        assert candidate["fields"]["have"] == "has"


class TestPC15n13GeographicDidYouMean:
    def test_gibberish_target_with_origin_names_the_roads(self):
        from tests.conftest import MarshalFactory, WorldFactory
        from backend.commands.executor import CommandExecutor

        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Paris")])
        executor = CommandExecutor()
        region, error = executor._fuzzy_match_region(
            "Zxqwv", world, near="Paris")
        assert region is None
        assert "From Paris the roads lead to" in error["message"]
        paris_adj = set(world.get_region("Paris").adjacent_regions)
        assert set(error["suggestions"]).issubset(paris_adj)

    def test_without_origin_behaviour_is_unchanged(self):
        from tests.conftest import MarshalFactory, WorldFactory
        from backend.commands.executor import CommandExecutor

        world = WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney", location="Paris")])
        executor = CommandExecutor()
        region, error = executor._fuzzy_match_region("Zxqwv", world)
        assert region is None
        assert "roads lead to" not in error["message"]


class TestPC15n17StaleRebellionPopupRetiredAtLoad:
    def _world(self):
        from tests.conftest import MarshalFactory, WorldFactory
        return WorldFactory.with_marshals(
            [MarshalFactory.infantry(name="Ney")], current_turn=8)

    def test_popup_for_a_non_vassal_is_retired(self):
        from backend.models.world_state import WorldState
        world = self._world()
        world.vassal_rebellion_imminent_popup = {
            "nation": "Switzerland", "loyalty": 8}
        world.vassal_rebellion_imminent_popups = [
            {"nation": "Switzerland", "loyalty": 8}]
        world.dialogue_manager.push({
            "type": "vassal_rebellion_imminent",
            "target_nation": "Switzerland",
            "turn_created": 8, "blocking": True})
        reloaded = WorldState.from_dict(world.to_dict())
        assert reloaded.vassal_rebellion_imminent_popup is None
        assert reloaded.vassal_rebellion_imminent_popups == []
        current = reloaded.pending_diplomatic_dialogue
        assert not (current or {}).get("type") == "vassal_rebellion_imminent"

    def test_popup_for_a_live_vassal_survives(self):
        from backend.models.world_state import WorldState
        world = self._world()
        world.vassals["Switzerland"] = {
            "lord": "France", "loyalty": 8, "regions": []}
        world.vassal_rebellion_imminent_popups = [
            {"nation": "Switzerland", "loyalty": 8}]
        reloaded = WorldState.from_dict(world.to_dict())
        assert len(reloaded.vassal_rebellion_imminent_popups) == 1
