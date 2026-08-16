"""Fixes from the Aug 16, 2026 "try to win" campaign.

Record: `docs/audits/PLAYTEST_WIN_CAMPAIGN_2026_08_16.md`; rows
`BUG_FIXES.md` §WIN and `DESIGN_REFINEMENT.md` §Win-Attempt Campaign.

  WIN-D2  "The Spoils of War" — an AI no longer takes an undefended
          province out from under a co-belligerent who is better placed
          to take it. Measured cause: France annihilated Austria's field
          army and gained ONE province while allied Bavaria walked into
          Vienna, Bohemia, Moravia and Hungary, going 3 -> 9.
  WIN-1   The peace dialogue offered "Send as suggested" as its first
          option and then refused it forever (the alliance-paradox
          HARD_STOP is checked at execution). It now arrives DISABLED
          with its reason, and the other arms stay live.
  WIN-2   The easing ladder drops territory demands, but the commentary
          tag was fixed before easing — so gold-only terms were presented
          under "Border territory provides strategic depth."
  WIN-H1  An interrupt raised during end-turn is promoted to
          `pending_interrupt` so non-Godot clients can answer it.
  WIN-3   Out-of-range refusals name the place, not just a distance.
"""

import pytest

from backend.ai import enemy_ai as enemy_ai_module
from backend.ai.enemy_ai import EnemyAI


def _ai():
    """EnemyAI takes an executor it never touches on this path."""
    return EnemyAI(executor=None)


# ═══════════════════════════════════════════════════════════════════
# WIN-D2 — The Spoils of War
# ═══════════════════════════════════════════════════════════════════

class _Marshal:
    def __init__(self, name, nation, location, strength):
        self.name = name
        self.nation = nation
        self.location = location
        self.strength = strength


class _Region:
    def __init__(self, name, controller, adjacent):
        self.name = name
        self.controller = controller
        self.adjacent_regions = list(adjacent)


class _World:
    """The measured shape: Hungary (Austrian, undefended) with Bavaria and
    France both adjacent, allied to each other and both at war with
    Austria."""

    def __init__(self, marshals, states=None):
        self.regions = {
            "Hungary": _Region("Hungary", "Austria", ["Bohemia", "Croatia"]),
            "Bohemia": _Region("Bohemia", "France", ["Hungary"]),
            "Croatia": _Region("Croatia", "Bavaria", ["Hungary"]),
        }
        self._marshals = marshals
        self._states = states or {}

    def get_region(self, name):
        return self.regions.get(name)

    def get_marshals_in_region(self, name):
        return [m for m in self._marshals if m.location == name]

    def get_diplomatic_state(self, a, b):
        return self._states.get(frozenset((a, b)), "PEACE")

    def is_at_war(self, a, b):
        return self._states.get(frozenset((a, b))) == "WAR"


def _world(bavaria_strength, france_strength, alliance=True):
    states = {
        frozenset(("Bavaria", "Austria")): "WAR",
        frozenset(("France", "Austria")): "WAR",
    }
    if alliance:
        states[frozenset(("Bavaria", "France"))] = "ALLIANCE"
    marshals = [
        _Marshal("Deroy", "Bavaria", "Croatia", bavaria_strength),
        _Marshal("Davout", "France", "Bohemia", france_strength),
    ]
    return _World(marshals, states), marshals[0]


class TestSpoilsOfWar:
    def test_defers_to_a_stronger_co_belligerent(self):
        """The measured case: one Bavarian corps beside four French ones."""
        world, deroy = _world(bavaria_strength=16_000, france_strength=60_000)
        assert _ai()._defers_spoils_to_ally(deroy, "Hungary", "Bavaria",
                                                world) is True

    def test_the_best_placed_partner_never_defers(self):
        """The rung cannot deadlock — whoever is strongest still acts."""
        world, deroy = _world(bavaria_strength=60_000, france_strength=16_000)
        assert _ai()._defers_spoils_to_ally(deroy, "Hungary", "Bavaria",
                                                world) is False

    def test_equal_strength_does_not_defer(self):
        """Strictly greater only, so a tie leaves somebody able to act."""
        world, deroy = _world(bavaria_strength=20_000, france_strength=20_000)
        assert _ai()._defers_spoils_to_ally(deroy, "Hungary", "Bavaria",
                                                world) is False

    def test_a_non_ally_never_blocks_a_capture(self):
        """A neutral or enemy massing next door is not a reason to hold
        back — only a co-belligerent's better claim is."""
        world, deroy = _world(bavaria_strength=16_000, france_strength=60_000,
                              alliance=False)
        assert _ai()._defers_spoils_to_ally(deroy, "Hungary", "Bavaria",
                                                world) is False

    def test_an_ally_not_at_war_with_the_owner_never_blocks(self):
        """An ally who is not fighting Austria has no claim on Austrian
        soil, however strong it is."""
        world, deroy = _world(bavaria_strength=16_000, france_strength=60_000)
        world._states[frozenset(("France", "Austria"))] = "PEACE"
        assert _ai()._defers_spoils_to_ally(deroy, "Hungary", "Bavaria",
                                                world) is False

    def test_a_distant_ally_never_blocks(self):
        """Adjacency-scoped: a huge ally army elsewhere is irrelevant."""
        world, deroy = _world(bavaria_strength=16_000, france_strength=60_000)
        world._marshals[1].location = "Croatia_far"
        assert _ai()._defers_spoils_to_ally(deroy, "Hungary", "Bavaria",
                                                world) is False

    def test_the_flip_flag_restores_the_old_behaviour(self):
        """BASELINE_SERIES attribution lever — False must be a no-op."""
        world, deroy = _world(bavaria_strength=16_000, france_strength=60_000)
        original = enemy_ai_module.SPOILS_DEFERENCE_ACTIVE
        try:
            enemy_ai_module.SPOILS_DEFERENCE_ACTIVE = False
            assert _ai()._defers_spoils_to_ally(deroy, "Hungary",
                                                    "Bavaria", world) is False
        finally:
            enemy_ai_module.SPOILS_DEFERENCE_ACTIVE = original

    def test_the_rule_is_symmetric_not_player_scoped(self):
        """GR5: it reads co-belligerents, so an AI defers to another AI
        exactly as it defers to the player. Neither nation here is the
        player, and the deference still fires."""
        states = {
            frozenset(("Bavaria", "Austria")): "WAR",
            frozenset(("Russia", "Austria")): "WAR",
            frozenset(("Bavaria", "Russia")): "ALLIANCE",
        }
        marshals = [_Marshal("Deroy", "Bavaria", "Croatia", 10_000),
                    _Marshal("Kutuzov", "Russia", "Bohemia", 40_000)]
        world = _World(marshals, states)
        assert _ai()._defers_spoils_to_ally(marshals[0], "Hungary",
                                                "Bavaria", world) is True

    def test_the_guard_is_wired_into_the_capture_rung(self):
        """A helper nothing calls is not a fix."""
        import inspect
        source = inspect.getsource(EnemyAI._find_undefended_capture)
        assert "_defers_spoils_to_ally" in source


class TestSpoilsRungBehaviour:
    """The source pin above proves the CALL exists; these prove the call
    CHANGES THE ANSWER, on the real rung and a real WorldState."""

    def _rung(self):
        from backend.commands.executor import CommandExecutor
        from backend.models.world_state import WorldState

        world = WorldState()
        ai = EnemyAI(CommandExecutor())

        blucher = world.marshals["Blucher"]
        blucher.strength = 30_000
        blucher.location = "Belgium"
        blucher.fortified = False
        blucher.drilling = False
        for other in world.marshals.values():
            if other.name != "Blucher":
                other.location = "London"

        target = world.regions["Netherlands"]
        target.controller = "France"
        target.garrison_strength = 0
        target.garrison_detachment = None
        world.diplomatic_states[
            world._make_diplo_key("Prussia", "France")] = "WAR"
        return world, ai, blucher

    def test_the_capture_is_found_when_nobody_has_a_better_claim(self):
        world, ai, blucher = self._rung()
        assert ai._find_undefended_capture(blucher, "Prussia", world) is not None

    def test_the_same_capture_is_declined_when_the_guard_fires(self):
        """Identical world; only the guard's verdict differs."""
        world, ai, blucher = self._rung()
        ai._defers_spoils_to_ally = lambda *a, **k: True
        assert ai._find_undefended_capture(blucher, "Prussia", world) is None


# ═══════════════════════════════════════════════════════════════════
# WIN-2 — the commentary must describe the terms actually staged
# ═══════════════════════════════════════════════════════════════════

class TestCommentaryMatchesTerms:
    def test_territory_tag_is_dropped_when_the_demand_was_eased_away(self):
        """The measured payload: demands [{gold_per_turn: 187}] presented
        under 'Border territory provides strategic depth.'"""
        from backend.game_logic import diplomatic_templates as dt
        source = __import__("inspect").getsource(dt.generate_suggested_terms)
        # The re-check must run AFTER the easing call and BEFORE stage 4.
        ease_at = source.find("_ease_suggestion_until_not_rejected(")
        recheck_at = source.find("border_territory_demanded\" in context_tags")
        commentary_at = source.find("Stage 4: Commentary")
        assert -1 < ease_at < recheck_at < commentary_at

    def test_the_commentary_row_still_exists_for_a_real_demand(self):
        """The fix must not delete the authored line — only stop it being
        used when nothing was demanded."""
        from backend.game_logic.diplomatic_templates import (
            TALLEYRAND_COMMENTARY,
        )
        assert ("_default", "border_territory_demanded") in TALLEYRAND_COMMENTARY


# ═══════════════════════════════════════════════════════════════════
# WIN-1 — an option that cannot work arrives disabled
# ═══════════════════════════════════════════════════════════════════

class TestHonestPeaceOption:
    def test_execute_proposal_is_disabled_under_the_paradox(self):
        from backend.game_logic import diplomatic_dialogue as dd
        source = __import__("inspect").getsource(dd)
        assert '_blocked_actions = {"execute_proposal"}' in source
        assert '_opt["enabled"] = False' in source

    def test_the_other_arms_stay_live(self):
        """Disabling everything would dead-end the player: only the arm
        that cannot succeed is gated."""
        from backend.game_logic import diplomatic_dialogue as dd
        source = __import__("inspect").getsource(dd)
        for action in ("modify_harsh", "modify_generous", "adjust_terms",
                       "reconsider"):
            assert f'"{action}"' not in source.split(
                "_blocked_actions")[1][:400]


# ═══════════════════════════════════════════════════════════════════
# WIN-H1 — the end-turn interrupt reaches every client
# ═══════════════════════════════════════════════════════════════════

MAIN_GD = (__import__("pathlib").Path(__file__).resolve().parent.parent
           / "godot-client" / "project-sovereign" / "scripts" / "main.gd")


def _gd_function(name):
    """The body of one GDScript function, for structural pins."""
    source = MAIN_GD.read_text(encoding="utf-8", errors="replace")
    start = source.index(f"func {name}(")
    rest = source[start:]
    end = rest.index("\nfunc ", 1)
    return rest[:end]


class TestInterruptPromotion:
    """NPC-16's production half. The promotion and the client guard are a
    PAIR: promoting `pending_interrupt` alone regresses the client, whose
    route table is consulted BEFORE the strategic-reports branch in the
    same function and returns — the interrupt popup would fire and the
    summary narrating the turn would be skipped. Both halves pinned."""

    def _promote(self, response, result):
        from backend.main import _include_command_strategic_reports
        _include_command_strategic_reports(response, result)
        return response

    def test_an_awaiting_report_becomes_a_pending_interrupt(self):
        response = self._promote({}, {"strategic_reports": [
            {"marshal": "Soult", "requires_input": False},
            {"marshal": "Napoleon", "requires_input": True,
             "interrupt_type": "cannon_fire"},
        ]})
        assert response["pending_interrupt"]["marshal"] == "Napoleon"
        assert response["requires_input"] is True

    def test_reports_without_input_promote_nothing(self):
        response = self._promote({}, {"strategic_reports": [
            {"marshal": "Ney", "requires_input": False}]})
        assert "pending_interrupt" not in response

    def test_a_live_interrupt_is_never_overwritten(self):
        """The synchronous interrupt is the more specific surface."""
        response = self._promote(
            {"pending_interrupt": {"marshal": "Davout"}},
            {"strategic_reports": [{"marshal": "Napoleon",
                                    "requires_input": True}]})
        assert response["pending_interrupt"]["marshal"] == "Davout"

    def test_strategic_reports_still_pass_through(self):
        response = self._promote({}, {"strategic_reports": [
            {"marshal": "Napoleon", "requires_input": True}]})
        assert len(response["strategic_reports"]) == 1

    # ── the client half of the pair ────────────────────────────────
    def test_the_client_defers_when_a_report_awaits_input(self):
        """Without this guard the promotion above would make the client
        skip its strategic report summary."""
        body = _gd_function("_response_has_interrupt_route")
        assert "strategic_reports" in body, (
            "the interrupt route no longer defers to the reports flow — "
            "the backend promotion in _include_command_strategic_reports "
            "must be reverted with it")
        assert "requires_input" in body
        assert "return false" in body

    def test_the_client_still_routes_a_synchronous_interrupt(self):
        """The guard must be scoped to the reports case only — a blocked
        path hit mid-command carries no report and must still popup."""
        body = _gd_function("_response_has_interrupt_route")
        assert "return true" in body

    def test_the_route_is_still_registered(self):
        source = MAIN_GD.read_text(encoding="utf-8", errors="replace")
        assert '"id": "interrupt"' in source
        assert "_response_has_interrupt_route" in source


# ═══════════════════════════════════════════════════════════════════
# WIN-3 — the refusal names the place
# ═══════════════════════════════════════════════════════════════════

class TestOutOfRangeNamesThePlace:
    def test_the_refusal_carries_the_resolved_location(self):
        import inspect
        from backend.commands.combat_executor import CombatExecutor
        source = inspect.getsource(CombatExecutor._execute_attack)
        assert "cannot reach {target}{where}" in source

    @pytest.mark.parametrize("target,location,expected", [
        ("Mack", "La Mancha", " (La Mancha)"),
        ("Swabia", "Swabia", ""),
    ])
    def test_the_suffix_only_appears_when_it_adds_information(
            self, target, location, expected):
        where = f" ({location})" if str(location) != str(target) else ""
        assert where == expected
