"""T0-B "Rule 4 and the drill" — the second slice of Tier 0 of the November 6,
2026 whole-game review (`docs/audits/GAME_REVIEW_2026_11_06.md` §4.1 #2, #6,
#15; `BUG_FIXES.md` §GR GR-56, GR-57, GR-58; the rules `SYSTEMS_REFERENCE.md`
§179).

COMBAT-1 (filed P1, verified P2) — a drilled corps kept its +20% (and the +5%
personality synergy) through every garrison assault: the field battle cleared
the four drill fields inline and the garrison assault never did. One helper,
`Marshal.consume_drill()`, is the reset for both — read through
`get_attack_modifier()` first, then cleared (Golden Rule 4).
COMBAT-2 — the fallback table was keyed lowercase and the strategic road
passed its type UPPERCASE, so an aggressive marshal who defied a standing HOLD
sulked. The table is read case-blind.
COMBAT-5 — Precision Execution's `min(8, base + 1)` lowered a 9 or 10 to 8.
It never lowers a skill now.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from backend.commands.defiance import get_defiant_action  # noqa: E402
from backend.commands.executor import CommandExecutor  # noqa: E402
from backend.models.marshal import Marshal  # noqa: E402
from backend.models.world_state import WorldState  # noqa: E402


def _staged_assault(shock_bonus=2, garrison=20000):
    """The CA8-19 staging: Ney alone at Berlin, the garrison British."""
    world = WorldState()
    for m in world.marshals.values():
        if m.nation == "France":
            m.location = "Bordeaux"
    target = world.get_region("Berlin")
    target.controller = "Britain"
    target.garrison_strength = garrison
    target.garrison_detachment = False
    ney = world.marshals["Ney"]
    ney.location = "Berlin"
    ney.strength = 12000
    ney.drilling = False
    ney.drilling_locked = False
    ney.drill_complete_turn = 1 if shock_bonus else -1
    ney.shock_bonus = shock_bonus
    return world, ney, CommandExecutor()


class TestTheAssaultSpendsTheDrill:
    """COMBAT-1 (GR-56)."""

    def test_a_drilled_corps_spends_its_drill_on_the_assault(self):
        world, ney, executor = _staged_assault()
        drilled = ney.get_attack_modifier(consume=False)
        result = executor._combat._resolve_garrison_combat(ney, world.get_region("Berlin"), world, {"world": world})
        assert ney.shock_bonus == 0, "the drill is spent by the assault"
        assert ney.drilling is False and ney.drilling_locked is False
        assert ney.drill_complete_turn == -1
        assert "the drill is spent" in result.get("message", ""), result.get("message")
        assert "+20%" in result.get("message", "")
        after = ney.get_attack_modifier(consume=False)
        assert after < drilled
        assert abs(after * 1.2 * 1.05 - drilled) < 0.02 or abs(after * 1.2 - drilled) < 0.02, (drilled, after)

    def test_the_executor_route_spends_it_too(self):
        """The road an order takes — `CommandExecutor.execute` → the attack
        pipeline → the garrison resolver — spends the drill as the resolver
        does when called alone (the AI's P4.25 and the player's typed assault
        both arrive this way)."""
        world, ney, executor = _staged_assault()
        foe = world.get_region("Berlin").controller
        if not world.is_at_war(ney.nation, foe):
            pytest.skip(f"France is not at war with {foe} on this board")
        # The garrison alone holds Berlin: an enemy corps standing there would
        # make the order a field battle (and the odds muster would stay it).
        for other in world.marshals.values():
            if other.nation != ney.nation and other.location == "Berlin":
                other.location = next(r.name for r in world.regions.values()
                                      if r.controller == other.nation and r.name != "Berlin")
        result = executor.execute(
            {"command": {"marshal": "Ney", "action": "attack", "target": "Berlin", "type": "specific"}},
            {"world": world})
        assert result.get("success") is True, result.get("message")
        assert "the drill is spent" in result.get("message", ""), result.get("message")
        assert ney.shock_bonus == 0 and ney.drill_complete_turn == -1

    def test_the_second_assault_runs_without_it(self):
        world, ney, executor = _staged_assault()
        berlin = world.get_region("Berlin")
        executor._combat._resolve_garrison_combat(ney, berlin, world, {"world": world})
        if berlin.garrison_strength <= 5000 or ney.location != "Berlin":
            pytest.skip("the first assault took the garrison on this roll")
        second = executor._combat._resolve_garrison_combat(ney, berlin, world, {"world": world})
        assert "the drill is spent" not in second.get("message", "")
        assert ney.shock_bonus == 0

    def test_an_undrilled_assault_says_nothing_of_a_drill(self):
        world, ney, executor = _staged_assault(shock_bonus=0)
        result = executor._combat._resolve_garrison_combat(ney, world.get_region("Berlin"), world, {"world": world})
        assert "drill" not in result.get("message", "").lower()

    def test_the_read_only_snapshot_leaves_the_drill(self):
        world, ney, _ = _staged_assault()
        ney.get_attack_modifier(consume=False)
        assert ney.shock_bonus == 2, "a preview spends nothing"

    def test_consume_drill_is_the_one_reset(self):
        m = Marshal("Davout", "Paris", 20000, "cautious", nation="France")
        m.drilling = True
        m.drilling_locked = True
        m.drill_complete_turn = 7
        m.shock_bonus = 2
        assert m.consume_drill() == 2
        assert (m.shock_bonus, m.drilling, m.drilling_locked, m.drill_complete_turn) == (0, False, False, -1)
        assert m.consume_drill() == 0, "a second call finds nothing standing"

    def test_the_transient_clear_resets_the_timer_too(self):
        m = Marshal("Davout", "Paris", 20000, "cautious", nation="France")
        m.drilling_locked = True
        m.drill_complete_turn = 7
        m.shock_bonus = 2
        m.clear_combat_transient_state()
        assert (m.shock_bonus, m.drilling, m.drilling_locked, m.drill_complete_turn) == (0, False, False, -1)

    def test_a_blow_while_drilling_loses_all_four(self):
        from backend.game_logic.combat import _cancel_drill
        m = Marshal("Davout", "Paris", 20000, "cautious", nation="France")
        m.drilling_locked = True
        m.drill_complete_turn = 9
        m.shock_bonus = 2
        _cancel_drill(m)
        assert (m.shock_bonus, m.drilling, m.drilling_locked, m.drill_complete_turn) == (0, False, False, -1)


class TestTheTableIsCaseBlind:
    """COMBAT-2 (GR-57)."""

    @staticmethod
    def _marshal(personality, artillery=False):
        m = Marshal("X", "Paris", 20000, personality, nation="France")
        m.artillery = artillery
        return m

    def test_the_hold_row_is_reached_from_the_strategic_road(self):
        ney = self._marshal("aggressive")
        assert get_defiant_action(ney, "HOLD") == "attack"
        assert get_defiant_action(ney, "hold") == "attack"
        assert get_defiant_action(ney, "SUPPORT") == "attack"
        assert get_defiant_action(ney, "MOVE_TO") == "attack"
        assert get_defiant_action(ney, "WAIT") == "attack"
        assert get_defiant_action(ney, "ATTACK") is None, "would not object"

    def test_the_cautious_row_both_ways(self):
        davout = self._marshal("cautious")
        assert get_defiant_action(davout, "ATTACK") == "fortify"
        assert get_defiant_action(davout, "attack") == "fortify"
        assert get_defiant_action(davout, "SUPPORT") == "fortify"
        assert get_defiant_action(davout, "MOVE_TO") == "fortify"
        assert get_defiant_action(davout, "HOLD") is None
        assert get_defiant_action(davout, "hold") is None

    def test_artillery_routes_to_bombardment_either_way(self):
        guns = self._marshal("aggressive", artillery=True)
        assert get_defiant_action(guns, "HOLD") == "bombardment"
        assert get_defiant_action(guns, "hold") == "bombardment"

    def test_literal_never_defies_and_pursue_stays_unwritten(self):
        assert get_defiant_action(self._marshal("literal"), "HOLD") is None
        # GRD-31 (for the user): PURSUE is in neither row of the spec's table.
        assert get_defiant_action(self._marshal("aggressive"), "PURSUE") is None
        assert get_defiant_action(self._marshal("cautious"), "PURSUE") is None
        assert get_defiant_action(self._marshal("aggressive"), None) is None

    def test_a_standing_hold_defied_by_an_aggressive_marshal_attacks(self, monkeypatch):
        """End to end on the strategic road: the objection carries
        `strategic_type` "HOLD"; insist, the roll fires, and the aggressive
        marshal attacks the nearest enemy instead of sulking."""
        import backend.commands.strategic_executor as road
        world = WorldState()
        ney = world.get_marshal("Ney")
        assert ney.personality == "aggressive"
        enemy = next(m for m in world.marshals.values() if m.nation != world.player_nation)
        monkeypatch.setattr(world, "find_nearest_enemy", lambda loc: (enemy, 1))
        executor = CommandExecutor()
        seen = {}

        def fake_attack(marshal, target_name, w, gs, command=None):
            seen["target"] = target_name
            seen["defiance"] = bool((command or {}).get("_defiance"))
            return {"success": True, "message": "charged"}

        monkeypatch.setattr(executor._combat, "_execute_attack", fake_attack)
        # the handler imports the chance LOCALLY from `defiance` — patch it there
        monkeypatch.setattr("backend.commands.defiance.calculate_defiance_chance", lambda *a, **k: 0.4)
        monkeypatch.setattr(road.random, "random", lambda: 0.0)
        world.pending_strategic_objection = {
            "marshal_name": "Ney",
            "original_command": {"marshal": "Ney", "action": "hold", "target": ney.location},
            "parsed_command": {"command": {"marshal": "Ney", "action": "hold", "target": ney.location}},
            "strategic_type": "HOLD", "path": [], "target": ney.location,
            "concern_level": "STRONG",
            "options": [
                {"type": "proceed", "text": "Insist", "trust_change": -10, "ap_cost": 2},
                {"type": "preferred", "text": "Trust", "trust_change": 3, "ap_cost": 1}],
            "trust_gain": 3, "insist_penalty": -10,
        }
        executor._strategic._handle_strategic_objection_from_endpoint("insist", {"world": world})
        assert seen.get("target") == enemy.name, "the HOLD row reached: an attack, not a sulk"
        assert seen.get("defiance") is True
        rows = [n for n in world.notifications.to_list() if n.get("type") == "marshal_defied_order"]
        assert rows and "attack" in rows[-1]["message"].lower()


class TestPrecisionNeverLowersASkill:
    """COMBAT-5 (GR-58)."""

    @staticmethod
    def _literal(tactical):
        m = Marshal("Soult", "Paris", 20000, "literal", nation="France")
        m.skills["tactical"] = tactical
        m.precision_execution_active = True
        m.precision_execution_turns = 3
        return m

    def test_a_nine_stays_a_nine(self):
        assert self._literal(9).get_effective_skill("tactical") == 9

    def test_a_ten_stays_a_ten(self):
        assert self._literal(10).get_effective_skill("tactical") == 10

    def test_the_cap_still_holds_below_it(self):
        assert self._literal(7).get_effective_skill("tactical") == 8
        assert self._literal(8).get_effective_skill("tactical") == 8
        assert self._literal(5).get_effective_skill("tactical") == 6

    def test_without_precision_nothing_moves(self):
        m = self._literal(9)
        m.precision_execution_active = False
        assert m.get_effective_skill("tactical") == 9

    def test_the_crown_still_adds_on_top(self):
        """A crown skill at 9 under precision AND the crown reads 10 (the crown's
        +1 after precision's, clamped at 10); a crown skill at 10 stays 10;
        tactical is not a crown skill, so the crown leaves its 9 alone."""
        m = self._literal(9)
        m.skills["shock"] = 9
        m.glory_crowned = True
        assert "shock" in m.CROWN_SKILLS and "tactical" not in m.CROWN_SKILLS
        assert m.get_effective_skill("shock") == 10
        assert m.get_effective_skill("tactical") == 9
        m.skills["shock"] = 10
        assert m.get_effective_skill("shock") == 10
        m.precision_execution_active = False
        assert m.get_effective_skill("shock") == 10 and m.get_effective_skill("tactical") == 9
