"""SR-2e "Standing orders reliable" (Score Mandate, September 26, 2026).

The user's ruling of SR-D3 as option (c) FIRST: the multiplier the design
already intends — the standing order — made reliable before any new action
point is minted (`docs/SCORE_MANDATE_PLAN.md` §2 Chunk 2 / §4 SR-D3). The
slice carries:

  * SUPPORT costs ONE action for every marshal (`Marshal.strategic_order_ap`);
  * AAR-10 a march keeps its tail through a reinforcement;
  * SR-4b folded in whole — AAR-8 (a question the player cannot answer),
    AAR-9 (cannon fire for a war France is not in), AAR-11 (the vindication
    verdict on the wrong battle), CRT-4 (the road law read where it is
    quoted) and CRT-5 (an answer is read closed).

Every row was reproduced at the real `POST /command` on the shipped 1805 boot
before a line was written; every rule sits behind a lever whose down arm
reproduces the row.

This section: the SUPPORT price. Measured before: `Davout, support Ney`
4 → 2 actions; the relationship-SUPPORT objection's Insist and Compromise
buttons said 2, and the compromise charged 2.
"""

import ast
import pathlib

import pytest
from fastapi.testclient import TestClient

import backend.commands.strategic_executor as SE
import backend.main as M
import backend.models.marshal as MA
from backend.commands.parser import CommandParser


REPO = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture
def shipped(monkeypatch):
    """A fresh SHIPPED 1805 world at all three seams with a mock parser (the
    CRT-1 idiom). The suite pins `SOVEREIGN_SCENARIO=none`; these rows need
    the real roster (Ney + Davout at Rhineland, Bernadotte at Franconia —
    Davout's rival in the authored web)."""
    for key in ("SOVEREIGN_SCENARIO", "SOVEREIGN_MAP", "SOVEREIGN_SMOKE_START"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LLM_MODE", "mock")
    M._reset_world_state()
    monkeypatch.setattr(M, "parser", CommandParser(use_real_llm=False))
    assert M.parser.llm.use_real_api is False, "a probe must never pay for a parse"
    return TestClient(M.app), M.world


def post(client, command):
    return client.post("/command", json={"command": command}).json()


def order_of(world, name):
    return getattr(world.marshals[name], "strategic_order", None)


# ═══════════════════════════════════════════════════════════════════════════
# SUPPORT costs one action
# ═══════════════════════════════════════════════════════════════════════════

class TestSupportIsOneAction:
    """The single source prices a SUPPORT at one action for every marshal."""

    def test_the_source_prices_support_at_one(self, shipped):
        _client, world = shipped
        davout = world.marshals["Davout"]          # cautious
        ney = world.marshals["Ney"]                # aggressive
        for m in (davout, ney):
            assert m.strategic_order_ap(order_type="SUPPORT") == 1
            for other in ("MOVE_TO", "PURSUE", "HOLD"):
                assert m.strategic_order_ap(order_type=other) == 2, other
            assert m.strategic_order_ap() == 2     # an unnamed order: 2

    def test_the_lever_down_restores_two(self, shipped, monkeypatch):
        _client, world = shipped
        monkeypatch.setattr(MA, "A_SUPPORT_ORDER_IS_ONE_ACTION", False)
        assert world.marshals["Davout"].strategic_order_ap(
            order_type="SUPPORT") == 2

    def test_literal_and_sovereign_stay_at_one(self, shipped):
        _client, world = shipped
        for name in ("Soult", "Napoleon"):
            m = world.marshals[name]
            for t in ("MOVE_TO", "PURSUE", "HOLD", "SUPPORT"):
                assert m.strategic_order_ap(order_type=t) == 1, (name, t)

    def test_support_at_the_wire_charges_one(self, shipped):
        client, world = shipped
        before = int(world.actions_remaining)
        data = post(client, "Davout, support Ney")
        assert data.get("success") is True, data.get("message")
        assert int(world.actions_remaining) == before - 1
        order = order_of(world, "Davout")
        assert order is not None and order.command_type == "SUPPORT"

    def test_support_is_accepted_at_one_action(self, shipped):
        """At one action the order is taken, never refused "Need 2"."""
        client, world = shipped
        world.actions_remaining = 1
        data = post(client, "Davout, support Ney")
        assert data.get("success") is True, data.get("message")
        assert "Need 2" not in str(data.get("message") or "")
        assert int(world.actions_remaining) == 0
        assert order_of(world, "Davout").command_type == "SUPPORT"

    def test_a_march_still_costs_two(self, shipped):
        client, world = shipped
        before = int(world.actions_remaining)
        data = post(client, "Davout, march to Lorraine")
        assert data.get("success") is True, data.get("message")
        assert int(world.actions_remaining) == before - 2

    def test_the_lever_down_charges_two_at_the_wire(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(MA, "A_SUPPORT_ORDER_IS_ONE_ACTION", False)
        before = int(world.actions_remaining)
        post(client, "Davout, support Ney")
        assert int(world.actions_remaining) == before - 2


class TestTheSupportObjectionQuotesWhatItCharges:
    """Bernadotte (Davout's rival, −2 in the authored web) objects to
    supporting him. Every button quotes the order's own price and the
    answer charges it (shown = applied)."""

    @pytest.fixture
    def objected(self, shipped, monkeypatch):
        client, world = shipped
        # `apply_mood_variance`'s own docstring: mock it, or the objection is
        # a roll (a mild concern proceeds with "I have reservations").
        monkeypatch.setattr(SE, "apply_mood_variance", lambda concern: concern)
        # The insist answer rolls V2b defiance (6% for Bernadotte here) on the
        # GLOBAL random stream, so an unpinned roll made this pin depend on
        # every test before it (found at the second Sept 28 session exit: a
        # subset run defied and left no order). Defiance has its own pins;
        # this one prices the answer.
        monkeypatch.setattr("backend.commands.defiance.calculate_defiance_chance",
                            lambda *a, **k: 0.0)
        data = post(client, "Bernadotte, support Davout")
        objection = data.get("objection") or {}
        assert objection.get("options"), data.get("message")
        return client, world, objection

    def test_the_buttons_quote_one(self, objected):
        _client, _world, objection = objected
        by_type = {o["type"]: o for o in objection["options"]}
        assert by_type["proceed"]["ap_cost"] == 1
        assert by_type["compromise"]["ap_cost"] == 1

    @pytest.mark.parametrize("choice,has_order", [
        ("insist", True), ("compromise", True), ("trust", False)])
    def test_every_answer_charges_one(self, objected, choice, has_order):
        client, world, _objection = objected
        before = int(world.actions_remaining)
        data = client.post("/respond_to_objection",
                           json={"choice": choice}).json()
        assert data.get("success") is True, data.get("message")
        assert int(world.actions_remaining) == before - 1, choice
        assert (order_of(world, "Bernadotte") is not None) is has_order

    def test_a_compromise_is_priced_as_the_order_it_softens(self, shipped):
        """`_build_strategic_options`: the compromise can never cost more
        than insisting on the order it softens — for a march both are 2,
        for a support both are 1."""
        from backend.commands.disobedience import _build_strategic_options
        _client, world = shipped
        davout = world.marshals["Davout"]
        for kind, price in (("MOVE_TO", 2), ("SUPPORT", 1)):
            options = _build_strategic_options(
                davout, None, {"action": kind.lower(), "max_turns": 3},
                "Insist", "Compromise", kind)
            by_type = {o["type"]: o for o in options}
            assert by_type["proceed"]["ap_cost"] == price, kind
            assert by_type["compromise"]["ap_cost"] == price, kind


class TestEveryPricingSiteNamesItsOrder:
    """A structural census: every call of `strategic_order_ap(` in the
    backend names the order it prices (`order_type=`), so the next order
    type priced apart cannot be priced at one site and quoted at another."""

    def test_every_call_names_the_order(self):
        missing = []
        for path in (REPO / "backend").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "strategic_order_ap"):
                    kws = {k.arg for k in node.keywords}
                    if "order_type" not in kws:
                        missing.append(f"{path.name}:{node.lineno}")
        assert not missing, missing

    def test_the_census_is_sensitive(self):
        """The walk finds calls (a census that matches nothing is inert)."""
        found = 0
        for path in (REPO / "backend").rglob("*.py"):
            found += path.read_text(encoding="utf-8").count(
                "strategic_order_ap(")
        assert found >= 8, found

    def test_the_help_names_the_support_price(self, shipped):
        client, _world = shipped
        text = str(post(client, "help").get("message") or "")
        assert "support 1 AP" in text, text[:400]


# ═══════════════════════════════════════════════════════════════════════════
# AAR-11 — the vindication verdict is bound to its order
# ═══════════════════════════════════════════════════════════════════════════

import random  # noqa: E402

import backend.commands.defiance as DEF  # noqa: E402
import backend.commands.executor as EX  # noqa: E402
import backend.commands.vindication as VIND  # noqa: E402
from backend.commands.vindication import VindicationTracker  # noqa: E402


@pytest.fixture
def obedient(monkeypatch):
    """An objection is a roll of mood and his obedience a roll of defiance —
    both pinned (`apply_mood_variance`'s own docstring: mock it)."""
    monkeypatch.setattr(EX, "apply_mood_variance", lambda concern: concern)
    monkeypatch.setattr(DEF, "calculate_defiance_chance", lambda *a, **k: 0.0)
    random.seed(11)


class TestTheVerdictIsBoundToItsOrder:
    """The Creative AAR: an insisted `fortify` was judged five turns later
    by an ordered attack on Archduke Charles ("concerns were justified",
    trust −5, authority −5)."""

    def test_an_insisted_fortify_stores_no_verdict(self, shipped, obedient):
        client, world = shipped
        data = post(client, "Massena, fortify")
        assert data.get("objection") or data.get("pending_objection"), data.get("message")
        post(client, "insist")
        assert "Massena" not in world.vindication_tracker.pending

    def test_the_lever_down_stores_the_name_keyed_entry(self, shipped, obedient,
                                                        monkeypatch):
        client, world = shipped
        monkeypatch.setattr(VIND, "THE_VERDICT_IS_BOUND_TO_ITS_ORDER", False)
        post(client, "Massena, fortify")
        post(client, "insist")
        assert world.vindication_tracker.pending["Massena"]["choice"] == "insist"

    def test_the_aar_chain_draws_no_verdict_on_another_battle(self, shipped, obedient):
        client, world = shipped
        post(client, "Massena, fortify")
        post(client, "insist")
        massena = world.marshals["Massena"]
        massena.fortified = False
        massena.strength = 3000
        trust_before = massena.trust.value
        message = str(post(client, "Massena, attack Archduke John").get("message") or "")
        assert "[Vindication]" not in message, message
        assert massena.trust.value == trust_before

    def test_an_insisted_attack_is_judged_by_its_own_battle(self, shipped, obedient):
        """The positive control: the answered attack fights in the answering
        call, and its battle is its own."""
        client, world = shipped
        world.marshals["Mack"].strength = 60000
        data = post(client, "Davout, attack Mack")
        assert data.get("objection") or data.get("pending_objection"), data.get("message")
        message = str(post(client, "insist").get("message") or "")
        assert "[Vindication]" in message, message
        assert "Davout" not in world.vindication_tracker.pending

    def test_a_new_order_expires_the_entry(self, shipped):
        client, world = shipped
        world.vindication_tracker.record_choice(
            "Ney", "insist", {"action": "attack", "target": "Mack"},
            executed_order={"action": "attack", "target": "Mack"},
            turn=world.current_turn)
        data = post(client, "Ney, march to Lorraine")
        assert data.get("success") is True, data.get("message")
        assert "Ney" not in world.vindication_tracker.pending

    def test_a_refused_new_order_hands_the_entry_back(self, shipped):
        client, world = shipped
        world.vindication_tracker.record_choice(
            "Ney", "insist", {"action": "attack", "target": "Mack"},
            executed_order={"action": "attack", "target": "Mack"},
            turn=world.current_turn)
        data = post(client, "Ney, march to London")      # the crossing: refused
        assert not data.get("success"), data.get("message")
        assert world.vindication_tracker.pending["Ney"]["choice"] == "insist"

    def test_a_read_expires_nothing(self, shipped):
        client, world = shipped
        world.vindication_tracker.record_choice(
            "Ney", "insist", {"action": "attack", "target": "Mack"},
            executed_order={"action": "attack", "target": "Mack"},
            turn=world.current_turn)
        post(client, "status")
        assert "Ney" in world.vindication_tracker.pending

    def test_another_battle_leaves_the_question_standing(self, shipped):
        _client, world = shipped
        tracker = world.vindication_tracker
        tracker.record_choice(
            "Ney", "insist", {"action": "attack", "target": "Mack"},
            executed_order={"action": "attack", "target": "Mack"}, turn=1)
        assert tracker.resolve_battle("Ney", "defeat", world,
                                      defender_name="ArchdukeJohn",
                                      battle_region="Tyrol") is None
        assert "Ney" in tracker.pending
        assert tracker.resolve_battle("Ney", "victory", world,
                                      defender_name="Mack",
                                      battle_region="Swabia") is not None
        assert "Ney" not in tracker.pending

    def test_a_march_is_judged_at_its_province(self, shipped):
        _client, world = shipped
        tracker = world.vindication_tracker
        tracker.record_choice(
            "Ney", "insist", {"action": "move", "target": "Swabia"},
            executed_order={"action": "move", "target": "Swabia"}, turn=1)
        assert tracker.resolve_battle("Ney", "victory", world,
                                      defender_name="Mack",
                                      battle_region="Swabia") is not None

    def test_a_legacy_entry_is_dropped_unjudged(self, shipped):
        _client, world = shipped
        tracker = world.vindication_tracker
        tracker.pending["Ney"] = {"choice": "insist", "original_order": {},
                                  "alternative": None, "turn_recorded": None}
        assert tracker.resolve_battle("Ney", "defeat", world,
                                      defender_name="Mack",
                                      battle_region="Swabia") is None
        assert "Ney" not in tracker.pending

    def test_the_unit_api_keeps_the_name_keyed_road(self):
        """A caller that binds nothing (the tracker's own unit callers)
        keeps the name-keyed behaviour."""
        tracker = VindicationTracker()
        tracker.record_choice("Ney", "trust", {"action": "attack"})
        assert tracker.pending["Ney"]["turn_recorded"] is None
        assert "executed_order" not in tracker.pending["Ney"]

    def test_the_defiance_arm_clears_the_entry(self):
        src = (REPO / "backend" / "commands" / "meta_executor.py").read_text(
            encoding="utf-8")
        head = src.index("# ═══ DEFIANCE FIRES ═══")
        assert "clear_pending(marshal_name)" in src[head:head + 900]

    def test_every_production_site_binds(self):
        """Census: every production `record_choice(` passes the executed
        order and every production `resolve_battle(` of the tracker passes
        the battle's identity."""
        offenders = []
        for path in (REPO / "backend").rglob("*.py"):
            if path.name == "vindication.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)):
                    continue
                kws = {k.arg for k in node.keywords}
                if node.func.attr == "record_choice" and "executed_order" not in kws:
                    offenders.append(f"{path.name}:{node.lineno} record_choice")
                if (node.func.attr == "resolve_battle"
                        and "vindication" in ast.unparse(node.func.value)
                        and not {"defender_name", "battle_region"} <= kws):
                    offenders.append(f"{path.name}:{node.lineno} resolve_battle")
        assert not offenders, offenders


# ═══════════════════════════════════════════════════════════════════════════
# AAR-9 — the guns must be our war
# ═══════════════════════════════════════════════════════════════════════════

import backend.commands.strategic as ST  # noqa: E402
from backend.models.marshal import StrategicOrder  # noqa: E402


def _marching(world, name, location, target):
    m = world.marshals[name]
    m.location = location
    m.strategic_order = StrategicOrder(
        command_type="MOVE_TO", target=target, target_type="region",
        started_turn=world.current_turn - 1,
        original_command=f"{name}, march to {target}",
        path=[], issued_turn=world.current_turn - 1)
    return m


def _peace_with_austria(world):
    from backend.game_logic.diplomacy import follow_the_lord, set_diplomatic_state
    set_diplomatic_state(world, "France", "Austria", "PEACE", reason="probe_treaty")
    follow_the_lord(world, "France", "Austria", "PEACE", reason="probe_treaty")


class TestTheGunsMustBeOurWar:
    """The Creative AAR: Massena, marching under the French peace, "hears
    cannon fire! Abandoning orders — rushing to Munich!" for a Bavaria-vs-
    Austria battle."""

    def _interrupt(self, world, marshal):
        processor = ST.StrategicOrderProcessor(M.executor)
        return processor._check_interrupts(marshal, world)

    def test_a_third_party_war_is_asked_not_rushed(self, shipped):
        _client, world = shipped
        _peace_with_austria(world)
        massena = _marching(world, "Massena", "Tyrol", "Provence")
        world.record_battle("Munich", "Mack", "Deroy", "defender_won")
        interrupt = self._interrupt(world, massena)
        assert interrupt is not None
        assert interrupt["action"] == "ask"
        assert interrupt["not_our_war"] is True
        assert "France is not in it" in interrupt["message"]

    def test_the_lever_down_rushes(self, shipped, monkeypatch):
        _client, world = shipped
        monkeypatch.setattr(ST, "THE_GUNS_MUST_BE_OUR_WAR", False)
        _peace_with_austria(world)
        massena = _marching(world, "Massena", "Tyrol", "Provence")
        world.record_battle("Munich", "Mack", "Deroy", "defender_won")
        assert self._interrupt(world, massena)["action"] == "redirect"

    def test_our_war_still_rushes(self, shipped):
        _client, world = shipped
        massena = _marching(world, "Massena", "Tyrol", "Provence")
        world.record_battle("Munich", "Mack", "Deroy", "defender_won")
        assert self._interrupt(world, massena)["action"] == "redirect"

    def test_a_refused_step_names_its_own_reason(self, shipped):
        """The step loop kept only successes, so every refused first step
        was reported as "no road leads there"."""
        _client, world = shipped
        massena = _marching(world, "Massena", "Tyrol", "Provence")
        massena.fortified = True
        processor = ST.StrategicOrderProcessor(M.executor)
        row = processor._handle_interrupt(
            massena, {"type": "cannon_fire", "action": "redirect",
                      "battle_location": "Munich"}, world, M.game_state)
        assert "fortified" in row["message"], row["message"]
        assert "no road leads there" not in row["message"]
        assert massena.strategic_order is not None

    def test_a_destroyed_participant_is_read_off_his_tombstone(self, shipped):
        _client, world = shipped
        _peace_with_austria(world)
        massena = _marching(world, "Massena", "Tyrol", "Provence")
        world.fallen_marshals["Ghost"] = {"nation": "Austria", "turn": 1,
                                          "location": "Munich", "cause": "probe"}
        battle = {"location": "Munich", "attacker": "Ghost",
                  "defender": "Deroy", "result": "x"}
        assert ST._cannon_fire_nation(world, "Ghost") == "Austria"
        assert ST.cannon_fire_is_lawful(world, massena, battle) is False

    def test_the_ask_row_names_whose_war(self, shipped):
        """End to end: the end-turn report is an ASK that says so, and the
        march stands."""
        client, world = shipped
        _peace_with_austria(world)
        world.marshals["Deroy"].strength = 150000
        massena = _marching(world, "Massena", "Tyrol", "Provence")
        world.record_battle("Munich", "Mack", "Deroy", "defender_won")
        random.seed(3)
        data = post(client, "end turn")
        rows = [r for r in (data.get("strategic_reports") or [])
                if r.get("marshal") == "Massena"]
        assert rows, data.get("strategic_reports")
        asked = [r for r in rows if r.get("interrupt_type") == "cannon_fire"]
        assert asked and asked[0].get("requires_input") is True, rows
        assert "France is not in it" in asked[0]["message"], asked[0]["message"]
        assert massena.strategic_order is not None
        assert "Abandoning orders" not in " ".join(
            str(r.get("message") or "") for r in rows)


# ═══════════════════════════════════════════════════════════════════════════
# AAR-10 — a march keeps its tail through a reinforcement
# ═══════════════════════════════════════════════════════════════════════════

def _stage_massena_reinforces(client, world, john_strength):
    """The agent's staging: Massena marches for Vienna, then Soult attacks
    Archduke John at Bohemia with Massena at Tyrol beside it."""
    random.seed(11)
    john = world.marshals["ArchdukeJohn"]
    john.location = "Hungary"
    post(client, "Massena, march to Vienna")
    post(client, "end turn")
    john.location = "Bohemia"
    john.strength = john_strength
    john.morale = 100
    world.marshals["Soult"].location = "Franconia"
    world.marshals["ArchdukeCharles"].location = "Naples"
    data = post(client, "Soult, attack Archduke John")
    if data.get("pending_capture_choice") or \
            "('plunder' or 'secure')" in str(data.get("message") or ""):
        post(client, "secure")     # the capture question, answered
    return data


class TestAMarchKeepsItsTail:

    def test_the_order_stands_through_a_victory(self, shipped):
        client, world = shipped
        data = _stage_massena_reinforces(client, world, 6000)
        massena = world.marshals["Massena"]
        assert massena.strategic_order is not None
        assert massena.strategic_order.command_type == "MOVE_TO"
        assert massena.strategic_order.target == "Vienna"
        assert "stands and resumes next turn" in str(data.get("message") or "")
        voided = [e for e in world.event_log
                  if isinstance(e, dict) and e.get("type") == "order_voided_by_battle"]
        assert not voided

    def test_the_order_stands_through_a_withdrawal(self, shipped):
        client, world = shipped
        _stage_massena_reinforces(client, world, 250000)
        massena = world.marshals["Massena"]
        assert massena.location == "Tyrol"
        assert massena.strategic_order is not None
        assert massena.strategic_order.target == "Vienna"

    def test_he_does_not_march_twice_and_then_arrives(self, shipped):
        client, world = shipped
        _stage_massena_reinforces(client, world, 6000)
        massena = world.marshals["Massena"]
        where = massena.location
        data = post(client, "end turn")
        rows = [r for r in (data.get("strategic_reports") or [])
                if r.get("marshal") == "Massena"]
        assert any("answered the guns this turn" in str(r.get("message") or "")
                   for r in rows), rows
        assert massena.location == where
        post(client, "end turn")
        assert massena.location == "Vienna"

    def test_a_pursuit_that_fought_its_quarry_takes_its_pause(self, shipped):
        """A kept PURSUE whose reinforcement fought his own quarry stamps
        the pursuit's one-turn pause (`_should_auto_attack`)."""
        client, world = shipped
        random.seed(11)
        john = world.marshals["ArchdukeJohn"]
        john.location = "Hungary"
        post(client, "Massena, march to Vienna")
        post(client, "end turn")
        massena = world.marshals["Massena"]
        massena.strategic_order = StrategicOrder(
            command_type="PURSUE", target="ArchdukeJohn", target_type="marshal",
            started_turn=world.current_turn - 1,
            original_command="Massena, pursue Archduke John",
            path=[], issued_turn=world.current_turn - 1)
        john.location = "Bohemia"
        john.strength = 6000
        john.morale = 100
        world.marshals["Soult"].location = "Franconia"
        world.marshals["ArchdukeCharles"].location = "Naples"
        post(client, "Soult, attack Archduke John")
        order = massena.strategic_order
        assert massena.reinforced_this_turn is True
        assert order is not None and order.command_type == "PURSUE"
        assert order.last_combat_enemy == "ArchdukeJohn"
        assert order.last_combat_turn == world.current_turn

    def test_the_lever_down_voids_the_order(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(ST, "A_MARCH_KEEPS_ITS_TAIL", False)
        _stage_massena_reinforces(client, world, 6000)
        assert world.marshals["Massena"].strategic_order is None

    @pytest.mark.parametrize("lever,walks", [(True, False), (False, True)])
    def test_the_ai_road_home_takes_the_same_skip(self, shipped, monkeypatch,
                                                  lever, walks):
        """GR5: an AI corps that answered a battle's guns this turn does not
        also walk its road home this turn (the WIN-D3 staging)."""
        from backend.ai.enemy_ai import EnemyAI
        from backend.commands.executor import CommandExecutor
        from backend.game_logic import withdrawal as W
        from backend.game_logic.diplomacy import set_diplomatic_state
        monkeypatch.setattr(ST, "A_MARCH_KEEPS_ITS_TAIL", lever)
        _client, world = shipped
        kutuzov = world.marshals["Kutuzov"]
        set_diplomatic_state(world, "France", "Russia", "WAR")
        world.regions["Moravia"].controller = "France"
        kutuzov.location = "Moravia"
        kutuzov.retreat_recovery = 0
        set_diplomatic_state(world, "France", "Russia", "PEACE")
        assert W.is_road_home_order(kutuzov.strategic_order)
        step = W.next_step_home(world, kutuzov)
        assert step
        kutuzov.reinforced_this_turn = True
        action, _ = EnemyAI(CommandExecutor())._evaluate_marshal(
            kutuzov, "Russia", world)
        took_the_road = bool(action and action.get("action") == "move"
                             and action.get("target") == step)
        assert took_the_road is walks, action


# ═══════════════════════════════════════════════════════════════════════════
# AAR-8 — a question the player cannot answer is never shipped
# ═══════════════════════════════════════════════════════════════════════════

class TestAQuestionRowIsAnswerable:

    def test_a_dead_row_is_overtaken(self, shipped):
        _client, world = shipped
        davout = world.marshals["Davout"]
        davout.pending_interrupt = None
        row = {"marshal": "Davout", "command": "MOVE_TO", "requires_input": True,
               "interrupt_type": "destination_blocked", "message": "ask"}
        out = ST.reconcile_question_rows(world, [row])
        assert out[0] is not row
        assert out[0]["requires_input"] is False
        assert out[0]["order_status"] == "overtaken"
        assert "overtaken" in out[0]["message"]

    def test_a_live_row_stands(self, shipped):
        _client, world = shipped
        davout = _marching(world, "Davout", "Rhineland", "Swabia")
        row = {"marshal": "Davout", "command": "MOVE_TO", "requires_input": True,
               "interrupt_type": "destination_blocked", "message": "ask"}
        davout.pending_interrupt = row
        assert ST.reconcile_question_rows(world, [row])[0] is row

    def test_an_order_bound_question_without_its_order_is_dead(self, shipped):
        _client, world = shipped
        davout = world.marshals["Davout"]
        davout.strategic_order = None
        row = {"marshal": "Davout", "requires_input": True,
               "interrupt_type": "destination_blocked", "message": "ask"}
        davout.pending_interrupt = dict(row)
        assert ST.reconcile_question_rows(world, [row])[0]["requires_input"] is False

    def test_the_pass_reconciles_its_own_rows(self, shipped):
        """The first net: `process_strategic_orders` itself ships no dead
        question (the AAR board, read from the processor, not the response)."""
        _client, world = shipped
        world.marshals["Mack"].strength = 20000
        world.marshals["Deroy"].location = "Dresden"
        for name in ("Davout", "Ney"):
            m = _marching(world, name, "Rhineland", "Swabia")
            m.strategic_order.path = ["Swabia"]
        random.seed(1)
        processor = ST.StrategicOrderProcessor(M.executor)
        reports = processor.process_strategic_orders(world, M.game_state)
        for row in reports:
            if row.get("requires_input"):
                m = world.marshals.get(row.get("marshal"))
                assert m is not None and ST.question_row_is_live(world, row), row

    def test_the_end_turn_reconciles_what_the_pass_shipped(self, shipped,
                                                           monkeypatch):
        """The second net: a question spent AFTER the pass (the advance, the
        grievance pass, the autonomous marshals) is reconciled where the
        end turn ships the rows."""
        client, world = shipped
        dead = {"marshal": "Davout", "command": "MOVE_TO",
                "requires_input": True, "interrupt_type": "destination_blocked",
                "order_status": "awaiting_response", "message": "ask"}
        monkeypatch.setattr(ST.StrategicOrderProcessor, "process_strategic_orders",
                            lambda self, w, gs: [dict(dead)])
        world.marshals["Davout"].pending_interrupt = None
        data = post(client, "end turn")
        rows = [r for r in (data.get("strategic_reports") or [])
                if r.get("marshal") == "Davout"]
        assert rows and rows[0]["order_status"] == "overtaken", rows
        assert rows[0]["requires_input"] is False

    def test_the_lever_down_ships_the_row(self, shipped, monkeypatch):
        _client, world = shipped
        monkeypatch.setattr(ST, "A_QUESTION_ROW_IS_ANSWERABLE", False)
        row = {"marshal": "Davout", "requires_input": True, "message": "ask"}
        assert ST.reconcile_question_rows(world, [row])[0] is row

    def test_the_aar_board_ships_no_unanswerable_question(self, shipped):
        """The agent's staging: Davout (cautious) asks about Swabia first,
        then Ney's arrival battle there recruits him."""
        client, world = shipped
        world.marshals["Mack"].strength = 20000
        world.marshals["Deroy"].location = "Dresden"
        for name in ("Davout", "Ney"):
            m = _marching(world, name, "Rhineland", "Swabia")
            m.strategic_order.path = ["Swabia"]
        random.seed(1)
        data = post(client, "end turn")
        for row in data.get("strategic_reports") or []:
            if row.get("requires_input"):
                m = world.marshals.get(row.get("marshal"))
                assert m is not None and m.pending_interrupt is not None, row
        rows = [r for r in (data.get("strategic_reports") or [])
                if r.get("marshal") == "Davout"]
        assert rows, data.get("strategic_reports")
        if world.marshals["Davout"].pending_interrupt is None:
            assert all(not r.get("requires_input") for r in rows), rows
            assert any(r.get("order_status") == "overtaken" for r in rows), rows


# ═══════════════════════════════════════════════════════════════════════════
# CRT-4 — the road law is read where it is quoted and where it is taken
# ═══════════════════════════════════════════════════════════════════════════

# Destinations the desk answered "Yes" and the march refused, measured on the
# shipped boot (the CR-6 triage's 33): closed frontiers and sea legs.
BARRED = ["London", "Scotland", "Ulster", "Corsica", "Berlin", "Brunswick",
          "Dresden", "Rome", "Lisbon"]


def _march_refused(client, world, name, place):
    before = int(world.actions_remaining)
    data = post(client, f"{name}, march to {place}")
    refused = (not data.get("success")) and int(world.actions_remaining) == before
    return refused, data


class TestTheDeskReadsTheMarch:

    @pytest.mark.parametrize("place", BARRED)
    def test_a_barred_road_is_no_at_the_desk_and_refused_by_the_march(
            self, shipped, place):
        client, world = shipped
        if place not in world.regions:
            pytest.skip(f"{place} is not a province on this board")
        answer = str(post(client, f"can Davout reach {place}").get("message") or "")
        assert not answer.startswith("Yes"), answer
        refused, data = _march_refused(client, world, "Davout", place)
        assert refused, data.get("message")

    @pytest.mark.parametrize("name,place", [
        ("Davout", "Lorraine"), ("Murat", "Normandy"), ("Ney", "Vienna"),
        ("Soult", "Normandy"), ("Murat", "Orleanais")])
    def test_a_yes_is_a_march_the_order_takes(self, shipped, name, place):
        client, world = shipped
        answer = str(post(client, f"can {name} reach {place}").get("message") or "")
        assert answer.startswith("Yes"), answer
        before = int(world.actions_remaining)
        data = post(client, f"{name}, march to {place}")
        taken = (int(world.actions_remaining) < before
                 or world.marshals[name].strategic_order is not None
                 or world.marshals[name].pending_interrupt is not None
                 or bool(data.get("objection") or data.get("pending_objection")))
        assert taken, data.get("message")

    def test_the_lever_down_answers_yes_across_the_water(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(ST, "THE_ROAD_LAW_IS_READ_WHERE_QUOTED", False)
        answer = str(post(client, "can Davout reach London").get("message") or "")
        assert answer.startswith("Yes"), answer


class TestTheDeskQuotesTheMarchsClock:
    """On a quiet board (no foreign corps) the driven arrival fits
    `march_turns` 32 of 32 (the CRT-4 recon); the desk quotes it."""

    def test_the_law(self):
        assert ST.march_turns(1, 1) == 0
        assert ST.march_turns(2, 2) == 0
        assert ST.march_turns(2, 1) == 2
        assert ST.march_turns(5, 2) == 3
        assert ST.march_turns(4, 1) == 4

    def test_within_reach_arrives_on_the_order(self, shipped):
        client, _world = shipped
        answer = str(post(client, "can Murat reach Orleanais").get("message") or "")
        assert "this very turn" in answer, answer

    @pytest.mark.parametrize("name,place,turns", [
        ("Murat", "Normandy", 3), ("Soult", "Normandy", 4)])
    def test_the_quote_is_the_driven_arrival(self, shipped, name, place, turns):
        client, world = shipped
        for m in list(world.marshals.values()):
            if m.nation != "France":
                m.strength = 0
        answer = str(post(client, f"can {name} reach {place}").get("message") or "")
        assert f"in {turns} turns" in answer, answer
        post(client, f"{name}, march to {place}")
        marshal = world.marshals[name]
        ends = 0
        while marshal.location != place and ends < 8:
            post(client, "end turn")
            ends += 1
        assert marshal.location == place
        assert ends == turns

    def test_a_visible_foe_on_the_road_is_named(self, shipped):
        client, _world = shipped
        answer = str(post(client, "can Ney reach Vienna").get("message") or "")
        assert "Mack stands on the road at Swabia" in answer, answer

    def test_the_state_speaks(self, shipped):
        client, world = shipped
        world.actions_remaining = 1
        answer = str(post(client, "can Davout reach Normandy").get("message") or "")
        assert answer.startswith("Not today"), answer
        assert "only 1 action remains" in answer, answer
        literal = str(post(client, "can Soult reach Normandy").get("message") or "")
        assert literal.startswith("Yes"), literal


class TestMoveToAsksTheRoadFirst:
    """CQ-31's remainder: a cautious marshal OBJECTED to `move to London`
    (Insist bought "Execution failed: the crossing is barred") while the
    march refuses it free."""

    @pytest.mark.parametrize("lever", [True, False])
    def test_move_to_walks_the_marchs_road(self, shipped, obedient,
                                          monkeypatch, lever):
        """`move to <far X>` is the march one verb over: a cautious man
        walks the march's own road around the enemy he can see."""
        monkeypatch.setattr(ST, "THE_ROAD_LAW_IS_READ_WHERE_QUOTED", lever)
        client, world = shipped
        random.seed(5)
        data = post(client, "Davout, move to Vienna")
        if data.get("objection") or data.get("pending_objection"):
            client.post("/respond_to_objection", json={"choice": "insist"})
        order = world.marshals["Davout"].strategic_order
        assert order is not None
        assert ("Swabia" in list(order.path)) is (not lever), list(order.path)

    def test_no_objection_before_the_road_law(self, shipped, monkeypatch):
        client, world = shipped
        monkeypatch.setattr(EX, "apply_mood_variance", lambda concern: concern)
        before = int(world.actions_remaining)
        data = post(client, "Bernadotte, move to London")
        assert not (data.get("objection") or data.get("pending_objection")), \
            data.get("message")
        assert not data.get("success")
        assert int(world.actions_remaining) == before
        assert "crossing" in str(data.get("message") or "").lower()
