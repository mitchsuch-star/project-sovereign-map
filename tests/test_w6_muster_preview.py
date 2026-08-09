"""W6-4 — Muster preview + standing orders surfaced (EXP-C1 + E-CA-4).

Before a risky battle the player sees who will fight and WHY the others
won't. The block rides EVERY resolved player attack; whether it also
BLOCKS is the separate muster-gate policy.

CA9 row 2 (Aug 9 2026) narrowed that policy: the confirm arms only for
an `unfavorable` band AND a `cautious` marshal
(`objection_v2.muster_gate_arms`). `even` no longer blocks anyone, and an
aggressive or literal marshal is never stopped. The gate fixtures here
therefore use DAVOUT — the roster's cautious French marshal — where they
previously used Ney; scoping the gate by character means the fixture has
to have the character. Coverage for the arms that no longer block lives
in `test_ca9_row2_muster_gate_scope.py`.

The odds band still reads the CR-5 single source
(`objection_v2.inferred_attack_effective_ratio`) — no second formula.
"""

import pytest

from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


@pytest.fixture(autouse=True)
def _no_mood_variance(monkeypatch):
    """CA9 row 2 scoped the muster gate to CAUTIOUS marshals, so this file's
    gate fixtures use one — and `apply_mood_variance` promotes his MILD odds
    concern to a blocking MODERATE 10% of the time, meaning he objects and
    the gate never arms. That made roughly 1 run in 10 of this file fail on
    a coin flip. The function's own docstring prescribes mocking it, and
    nothing in this file is about mood, so it is neutralised file-wide.

    The promotion is real, intended behaviour and is pinned as such in
    test_ca9_row2_muster_gate_scope.py::TestMoodVarianceCanPreEmptTheGate.
    """
    monkeypatch.setattr("backend.commands.executor.apply_mood_variance",
                        lambda concern: concern)


def _attack(executor, world, marshal="Ney", target="Mack",
            confirmed=False):
    command = {"marshal": marshal, "action": "attack", "target": target}
    if confirmed:
        command["_muster_confirmed"] = True
    return executor.execute({"success": True, "command": command},
                            {"world": world})


# ════════════════════════════════════════════════════════════════════════
# §6.1 The muster block — reason codes
# ════════════════════════════════════════════════════════════════════════

class TestMusterReasons:
    def _base(self, extra_marshals=()):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=60000,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=8000)
        world = WorldFactory.with_marshals([ney, mack, *extra_marshals])
        _war(world)
        executor = CommandExecutor()
        return world, executor, ney, mack

    def _preview(self, world, executor, ney, mack):
        return executor._combat._build_muster_preview(
            ney, mack, world, {"world": world})

    def test_aggressive_adjacent_joins(self):
        soult = MarshalFactory.infantry(name="Soult", location="Paris",
                                        strength=20000,
                                        personality="aggressive")
        world, executor, ney, mack = self._base([soult])
        rows = self._preview(world, executor, ney, mack)["rows"]
        soult_row = next(r for r in rows if r["marshal"] == "Soult")
        assert soult_row["will_join"] is True
        assert soult_row["reason"] == "aggressive_marches"

    def test_literal_refuses_without_order_and_hints_the_fix(self):
        grouchy = MarshalFactory.infantry(name="Grouchy", location="Paris",
                                          strength=20000,
                                          personality="literal")
        world, executor, ney, mack = self._base([grouchy])
        rows = self._preview(world, executor, ney, mack)["rows"]
        row = next(r for r in rows if r["marshal"] == "Grouchy")
        assert row["will_join"] is False
        assert row["reason"] == "literal_awaits_orders"
        assert "Grouchy, support Ney" in row["standing_order_hint"]

    def test_literal_with_support_order_joins(self):
        grouchy = MarshalFactory.infantry(name="Grouchy", location="Paris",
                                          strength=20000,
                                          personality="literal")
        grouchy.strategic_order = StrategicOrder(
            command_type="SUPPORT", target="Ney", target_type="marshal",
            started_turn=1, original_command="Grouchy, support Ney")
        world, executor, ney, mack = self._base([grouchy])
        rows = self._preview(world, executor, ney, mack)["rows"]
        row = next(r for r in rows if r["marshal"] == "Grouchy")
        assert row["will_join"] is True
        assert row["reason"] == "has_support_order"

    def test_fortified_is_static(self):
        davout = MarshalFactory.infantry(name="Davout", location="Paris",
                                         strength=20000)
        davout.fortified = True
        world, executor, ney, mack = self._base([davout])
        rows = self._preview(world, executor, ney, mack)["rows"]
        row = next(r for r in rows if r["marshal"] == "Davout")
        assert row["will_join"] is False
        assert row["reason"] == "fortified_static"

    def test_hostile_refuses(self):
        soult = MarshalFactory.infantry(name="Soult", location="Paris",
                                        strength=20000,
                                        personality="cautious")
        world, executor, ney, mack = self._base([soult])
        soult.set_relationship("Ney", -2)
        rows = self._preview(world, executor, ney, mack)["rows"]
        row = next(r for r in rows if r["marshal"] == "Soult")
        assert row["will_join"] is False
        assert row["reason"] == "hostile_refuses"

    def test_co_located_friendly_shares_the_field(self):
        soult = MarshalFactory.infantry(name="Soult", location="Belgium",
                                        strength=20000)
        world, executor, ney, mack = self._base([soult])
        preview = self._preview(world, executor, ney, mack)
        row = next(r for r in preview["rows"] if r["marshal"] == "Soult")
        assert row["reason"] == "shares_the_field"
        assert "Soult" in preview["shared_casualty_note"]

    def test_fog_partial_target_shows_band_not_exact(self):
        from backend.models.intel import PARTIAL, RegionIntel
        world, executor, ney, mack = self._base()
        intel = RegionIntel("Belgium")
        intel.visibility = PARTIAL
        intel.known_marshals = [{"name": "Mack", "nation": "Austria",
                                 "band": "small force"}]
        world.intel["Belgium"] = intel
        preview = self._preview(world, executor, ney, mack)
        assert preview["target"]["strength_display"] == "small force"
        assert "8,000" not in preview["target"]["strength_display"]

    def test_hint_latches_once_and_serializes(self):
        world, executor, ney, mack = self._base()
        first = self._preview(world, executor, ney, mack)
        assert "Standing orders" in first.get("hint", "")
        assert world.muster_hint_shown is True
        second = self._preview(world, executor, ney, mack)
        assert "hint" not in second
        restored = WorldState.from_dict(world.to_dict())
        assert restored.muster_hint_shown is True


# ════════════════════════════════════════════════════════════════════════
# §6.2 Gating
# ════════════════════════════════════════════════════════════════════════

class TestMusterGate:
    def _bad_odds_world(self):
        # CA9 row 2: the gate arms on character. Davout is the 1805
        # roster's cautious French marshal, so he is the one who stops to
        # ask — Ney (aggressive) charges, and is covered next door.
        # 30k vs 50k, not 20k: at 2.5:1 a cautious marshal raises a V2a
        # OBJECTION, which fires before the muster gate and would leave
        # this class testing the objection system. 1.67:1 is `unfavorable`
        # (so the gate arms) but only MILD concern (so nothing pre-empts
        # it). See test_ca9_row2_muster_gate_scope.py for the measured map.
        davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                         strength=30000,
                                         personality="cautious")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=50000,
                                    personality="cautious")
        world = WorldFactory.with_marshals([davout, mack])
        _war(world)
        # A cautious marshal objects on poor intel alone (STRONG on UNKNOWN,
        # MODERATE on STALE), and that objection pre-empts the muster gate —
        # so this class needs its fog pinned to keep testing the gate.
        world.calculate_visibility()
        return world, CommandExecutor()

    def test_unfavorable_interrupts_without_resolving(self):
        world, executor = self._bad_odds_world()
        ap_before = world.actions_remaining
        mack_before = world.get_marshal("Mack").strength
        result = _attack(executor, world, marshal="Davout")
        assert result.get("requires_input") is True
        interrupt = result["pending_interrupt"]
        assert interrupt["interrupt_type"] == "muster_confirm"
        # The July-7 L1 lesson: every stored interrupt carries `marshal`.
        assert interrupt["marshal"] == "Davout"
        assert world.get_marshal("Davout").pending_interrupt is not None
        # Nothing resolved, nothing spent.
        assert world.get_marshal("Mack").strength == mack_before
        assert world.actions_remaining == ap_before
        assert "MUSTER" in result["message"]

    def test_attack_anyway_resolves_the_battle(self):
        world, executor = self._bad_odds_world()
        _attack(executor, world, marshal="Davout")
        ap_before = world.actions_remaining
        proc = StrategicOrderProcessor(executor)
        result = proc.handle_response("Davout", "muster_confirm",
                                      "attack_anyway", world,
                                      {"world": world})
        assert result.get("success") is True
        assert world.get_marshal("Davout").pending_interrupt is None
        # The battle actually happened this time.
        assert world.get_marshal("Mack").strength < 50000
        # And the resolved attack paid its AP.
        assert world.actions_remaining == ap_before - 1

    def test_cancel_stands_down_free(self):
        world, executor = self._bad_odds_world()
        _attack(executor, world, marshal="Davout")
        ap_before = world.actions_remaining
        proc = StrategicOrderProcessor(executor)
        result = proc.handle_response("Davout", "muster_confirm",
                                      "cancel_order", world,
                                      {"world": world})
        assert result["success"] is True
        assert "stands down" in result["message"]
        assert world.get_marshal("Mack").strength == 50000
        assert world.actions_remaining == ap_before

    def test_favorable_resolves_immediately_with_block(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=60000,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=8000)
        world = WorldFactory.with_marshals([ney, mack])
        _war(world)
        executor = CommandExecutor()
        result = _attack(executor, world)
        assert result.get("requires_input") is None
        assert result.get("muster_preview") is not None
        assert "MUSTER" in result["message"]
        assert world.get_marshal("Mack").strength < 8000

    def test_strategic_execution_bypasses_the_gate(self):
        # Davout WOULD be stopped by the gate on a direct order (see
        # test_unfavorable_interrupts_without_resolving), so this genuinely
        # exercises the bypass rather than passing vacuously.
        world, executor = self._bad_odds_world()
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Davout", "action": "attack",
                         "target": "Mack", "_strategic_execution": True}},
            {"world": world})
        assert result.get("pending_interrupt") is None
        assert world.get_marshal("Mack").strength < 50000

    def test_ai_attack_produces_no_interrupt(self):
        """GR5: the muster confirm is a player legibility surface."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=50000)
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=20000,
                                    personality="aggressive")
        world = WorldFactory.with_marshals([ney, mack])
        _war(world)
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Mack", "action": "attack",
                         "target": "Ney", "_autonomous_execution": True,
                         "_acting_nation": "Austria"}},
            {"world": world})
        assert result.get("pending_interrupt") is None
        assert world.get_marshal("Mack").pending_interrupt is None

    def test_confirmed_reissue_skips_gate_but_keeps_block(self):
        # Same point: the marshal here is the one the gate WOULD stop, so
        # `_muster_confirmed` is doing the work being tested.
        world, executor = self._bad_odds_world()
        result = _attack(executor, world, marshal="Davout", confirmed=True)
        assert result.get("requires_input") is None
        assert result.get("muster_preview") is not None
        assert world.get_marshal("Mack").strength < 50000


# ════════════════════════════════════════════════════════════════════════
# §6.3 / §6.4 Standing orders surfaced + the Grouchy pin
# ════════════════════════════════════════════════════════════════════════

class TestStandingOrders:
    def test_support_creation_confirms_the_doctrine(self):
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000,
                                      personality="aggressive")
        soult = MarshalFactory.infantry(name="Soult", location="Paris",
                                        strength=20000,
                                        personality="literal")
        world = WorldFactory.with_marshals([ney, soult])
        executor = CommandExecutor()
        result = executor.execute(
            {"success": True,
             "is_strategic": True,
             "strategic_type": "SUPPORT",
             "command": {"marshal": "Soult", "action": "support",
                         "target": "Ney"}},
            {"world": world})
        assert result.get("success") is True
        # CA9-F8 (pin re-blessed): the doctrine is still confirmed and the
        # "written order" is still named — that is what this test is for.
        # What changed is the unconditional GUARANTEE. The old sentence
        # promised "Soult will march to Ney's guns" flat, while the code
        # scopes it three ways: the Grouchy Rule honours the order only
        # when Ney LEADS the battle (the one refusal in the played
        # campaign that really was this defect), arrival is still a roll,
        # and the order auto-completes the first turn the ally is safe.
        assert "written order" in result["message"]
        assert "march to the guns" in result["message"]
        assert "when Ney leads a battle" in result["message"], (
            "the confirmation must scope the promise to the case the "
            "Grouchy Rule actually honours")
        assert "lapses of itself" in result["message"], (
            "…and say that an undated order ends the first quiet turn")

    def test_literal_without_support_still_never_auto_reinforces(self):
        """§6.4 scope boundary pin: this slice surfaces the Grouchy Rule —
        it does not change it. The autonomous march-to-guns beat stays
        gated behind its own future design gate."""
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=30000,
                                      personality="aggressive")
        grouchy = MarshalFactory.infantry(name="Grouchy", location="Paris",
                                          strength=20000,
                                          personality="literal")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=30000)
        world = WorldFactory.with_marshals([ney, grouchy, mack])
        _war(world)
        executor = CommandExecutor()
        results = executor._combat._calculate_reinforcements(
            ney, mack, "Belgium", "France", world)
        grouchy_result = next(r for r in results
                              if r["marshal"] == "Grouchy")
        assert grouchy_result["arrived"] is False
        assert grouchy_result["reason"] == "literal_personality"


# ════════════════════════════════════════════════════════════════════════
# Typed-answer routing at the /command tier (ES-7 second-pass integration
# audit fix, July 11 2026): the muster interrupt offers "attack_anyway",
# but main.py's interrupt matcher only mapped attack-words to a choice
# named "attack" — so typing the popup's OWN label ("attack anyway") fell
# through to the parser as a FRESH, ungated attack by a defaulted marshal
# (found live: Massena charged Archduke John into mountain terrain while
# Soult's muster question was still pending).
# ════════════════════════════════════════════════════════════════════════

from fastapi.testclient import TestClient


@pytest.fixture()
def muster_endpoint():
    import backend.main as main_module
    from backend.commands.parser import CommandParser as _CP

    # CA9 row 2: the acting marshal must be CAUTIOUS or the gate no longer
    # arms at all, so Ney is replaced by Davout. The second marshal is the
    # literal Soult rather than the aggressive Massena for the same reason
    # the strengths changed — see below.
    davout = MarshalFactory.infantry(name="Davout", location="Belgium",
                                     strength=50000, personality="cautious")
    soult = MarshalFactory.infantry(name="Soult", location="Paris",
                                    strength=60000,
                                    personality="literal")
    # CO-2 (Combat Overhaul Phase 1): the odds band reflects the TOTAL
    # committed force, so an adjacent AGGRESSIVE musterer would drag 50k vs
    # 90k up to `favorable` and the gate would (correctly) not arm. Soult is
    # literal with no support order, so `literal_awaits_orders` keeps him
    # out of the muster — which is his own W6-5 doctrine, not a fudge — and
    # he remains present for the "the answer resolved for the RIGHT marshal"
    # assertion below.
    # 50k vs 90k is 1.8:1 — `unfavorable` (gate arms) at only MILD concern
    # (no V2a objection pre-empts it). Measured; see
    # test_ca9_row2_muster_gate_scope.py for the full map.
    mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                nation="Austria", strength=90000)
    world = WorldFactory.with_marshals([davout, soult, mack])
    _war(world)
    world.calculate_visibility()  # see TestMusterGate._bad_odds_world
    # The executor is swapped too. It was not before, and that was a latent
    # flake: /command uses the MODULE-GLOBAL executor, which carries
    # per-marshal objection state across tests, so this class's result
    # depended on what ran before it in the module. Caught while re-pointing
    # the fixture at Davout — the class passed alone and failed in the
    # module. Same shape as the sweep-5 fixture, which always did this.
    from backend.commands.executor import CommandExecutor as _CE
    orig = (main_module.parser, main_module.world, main_module.game_state,
            main_module.executor)
    main_module.parser = _CP(use_real_llm=False)
    main_module.world = world
    main_module.game_state = {"world": world}
    main_module.executor = _CE()
    try:
        yield TestClient(main_module.app), world
    finally:
        (main_module.parser, main_module.world, main_module.game_state,
         main_module.executor) = orig


class TestMusterTypedAnswerEndpoint:
    def test_attack_anyway_resolves_the_pending_gate(self, muster_endpoint):
        client, world = muster_endpoint
        opening = client.post(
            "/command", json={"command": "Davout, attack Mack"}).json()
        pending = opening.get("pending_interrupt") or {}
        assert pending.get("interrupt_type") == "muster_confirm", opening.get(
            "message")
        davout = world.marshals["Davout"]
        assert getattr(davout, "pending_interrupt", None)

        answer = client.post(
            "/command", json={"command": "attack anyway"}).json()
        # The gate resolved for DAVOUT vs MACK — the question was consumed,
        # no other marshal fought, and the battle actually happened.
        #
        # Asserted MECHANICALLY, not on battle copy. This previously matched
        # "<name> leads the charge", which is one of several outcome-dependent
        # narrations: Davout at 1.8:1 against loses, so that phrasing never
        # appears and the test failed for a reason unrelated to routing.
        # Casualties on the right marshal and none on the wrong one is the
        # actual claim.
        assert getattr(davout, "pending_interrupt", None) is None
        assert world.marshals["Mack"].strength < 90000
        assert world.marshals["Davout"].strength < 50000
        assert world.marshals["Soult"].strength == 60000
        assert "Davout" in str(answer.get("message", ""))

    def test_cancel_still_stands_down(self, muster_endpoint):
        client, world = muster_endpoint
        client.post("/command", json={"command": "Davout, attack Mack"})
        answer = client.post(
            "/command", json={"command": "cancel"}).json()
        davout = world.marshals["Davout"]
        assert getattr(davout, "pending_interrupt", None) is None
        assert world.marshals["Mack"].strength == 90000
        assert answer.get("success") is not False
