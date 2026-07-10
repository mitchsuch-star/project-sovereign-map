"""W6-4 — Muster preview + standing orders surfaced (EXP-C1 + E-CA-4).

Before a risky battle the player sees who will fight and WHY the others
won't; unfavorable/even odds route through a one-modal muster confirm
(the E-CA-4 odds warning), favorable odds resolve straight through with
the block prepended. The odds band reads the CR-5 single source
(`objection_v2.inferred_attack_effective_ratio`) — no second formula.
"""

from backend.commands.executor import CommandExecutor
from backend.commands.strategic import StrategicOrderProcessor
from backend.models.marshal import StrategicOrder
from backend.models.world_state import WorldState

from tests.conftest import MarshalFactory, WorldFactory


def _war(world, a="France", b="Austria"):
    key = "|".join(sorted([a, b]))
    world.diplomatic_states[key] = "WAR"
    world.war_start_turns[key] = world.current_turn


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
        ney = MarshalFactory.infantry(name="Ney", location="Belgium",
                                      strength=20000,
                                      personality="aggressive")
        mack = MarshalFactory.enemy(name="Mack", location="Belgium",
                                    nation="Austria", strength=50000,
                                    personality="cautious")
        world = WorldFactory.with_marshals([ney, mack])
        _war(world)
        return world, CommandExecutor()

    def test_unfavorable_interrupts_without_resolving(self):
        world, executor = self._bad_odds_world()
        ap_before = world.actions_remaining
        mack_before = world.get_marshal("Mack").strength
        result = _attack(executor, world)
        assert result.get("requires_input") is True
        interrupt = result["pending_interrupt"]
        assert interrupt["interrupt_type"] == "muster_confirm"
        # The July-7 L1 lesson: every stored interrupt carries `marshal`.
        assert interrupt["marshal"] == "Ney"
        assert world.get_marshal("Ney").pending_interrupt is not None
        # Nothing resolved, nothing spent.
        assert world.get_marshal("Mack").strength == mack_before
        assert world.actions_remaining == ap_before
        assert "MUSTER" in result["message"]

    def test_attack_anyway_resolves_the_battle(self):
        world, executor = self._bad_odds_world()
        _attack(executor, world)
        ap_before = world.actions_remaining
        proc = StrategicOrderProcessor(executor)
        result = proc.handle_response("Ney", "muster_confirm",
                                      "attack_anyway", world,
                                      {"world": world})
        assert result.get("success") is True
        assert world.get_marshal("Ney").pending_interrupt is None
        # The battle actually happened this time.
        assert world.get_marshal("Mack").strength < 50000
        # And the resolved attack paid its AP.
        assert world.actions_remaining == ap_before - 1

    def test_cancel_stands_down_free(self):
        world, executor = self._bad_odds_world()
        _attack(executor, world)
        ap_before = world.actions_remaining
        proc = StrategicOrderProcessor(executor)
        result = proc.handle_response("Ney", "muster_confirm",
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
        world, executor = self._bad_odds_world()
        result = executor.execute(
            {"success": True,
             "command": {"marshal": "Ney", "action": "attack",
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
        world, executor = self._bad_odds_world()
        result = _attack(executor, world, confirmed=True)
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
        assert "march to Ney's guns" in result["message"]
        assert "written order" in result["message"]

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
