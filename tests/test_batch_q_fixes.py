"""Batch Q (Phase 8.5 opener) — quick-wins & honest-counsel fixes.

Dispositions set at 8.EVAL (docs/audits/EVAL_8_2026_07_16.md §1). This file
pins the clean backend/doc fixes landed in the first Batch-Q chunk:

- S5-1  enemy-AI square↔fortify self-cancelling loop (hold ONE stance)
- S5-2  raw camelCase marshal keys leaking into rejection copy
- S5-3  stale DOTATION_EXPECTATION rail notice (live numbers + countdown)
- S5-5  bombard no-guns guard bypass + fixed-corps copy citing the capped size
- S5-D2 MOVE_TO issuance-time passability honesty (no silent 2-AP waste)
- AUD-g Talleyrand military-advantage band realignment + grammar
- AUD-e / S5-4  doc/docstring reconciliation pins
"""

import pytest

from backend.ai.enemy_ai import EnemyAI
from backend.commands.executor import CommandExecutor
from backend.game_logic.diplomatic_advisory import _get_military_advantage
from backend.models.dialogue_manager import DialogueManager
from backend.models.marshal import Marshal, Stance
from backend.models.region import Region
from backend.models.world_state import WorldState


def _game_state(world):
    return {"world": world}


def _france_at_war_with(world, other):
    key = world._make_diplo_key("France", other)
    world.diplomatic_states[key] = "WAR"


# ════════════════════════════════════════════════════════════════════════
# S5-1 — enemy AI must not churn between square and fortification
# ════════════════════════════════════════════════════════════════════════

class TestS51SquareFortifyLoop:
    def _ai(self):
        return EnemyAI(CommandExecutor())

    def _defender_world(self):
        world = WorldState()
        world.marshals = {}
        world.regions = {
            "Hold": Region("Hold", ["Front"], 100),
            "Front": Region("Front", ["Hold"], 100),
        }
        world.regions["Hold"].controller = "Britain"
        world.regions["Front"].controller = "France"
        world.player_nation = "France"
        moore = Marshal("Moore", "Hold", 30000, "cautious", "Britain")
        moore.stance = Stance.DEFENSIVE
        world.marshals["Moore"] = moore
        return world, moore

    def test_consider_fortify_holds_square(self):
        """A marshal already in square must NOT be handed a fortify order —
        that break-then-reform-next-turn is the self-cancelling loop."""
        ai = self._ai()
        world, moore = self._defender_world()
        moore.square_formation = True
        moore.fortified = False
        assert ai._consider_fortify(moore, world) is None

    def test_consider_fortify_still_fires_when_not_in_square(self):
        """The guard is square-only: a defensive, un-fortified, un-squared
        marshal still fortifies (regression guard on the guard)."""
        ai = self._ai()
        world, moore = self._defender_world()
        moore.square_formation = False
        moore.fortified = False
        result = ai._consider_fortify(moore, world)
        assert result is not None
        assert result["action"] in ("fortify", "stance_change")

    def test_square_marshal_never_evaluated_to_fortify(self):
        """End-to-end: an infantry marshal in square with cavalry adjacent
        holds the square — the full decision tree never returns 'fortify'."""
        ai = self._ai()
        world, moore = self._defender_world()
        moore.square_formation = True
        moore.fortified = False
        _france_at_war_with(world, "Britain")
        # French cavalry adjacent to Moore's region (the reason he's in square)
        hussar = Marshal("Hussar", "Front", 8000, "aggressive", "France",
                         cavalry=True)
        world.marshals["Hussar"] = hussar
        action, _priority = ai._evaluate_marshal(moore, "Britain", world)
        if action is not None:
            assert action.get("action") != "fortify"


# ════════════════════════════════════════════════════════════════════════
# S5-2 — no raw camelCase marshal keys in player-facing rejection copy
# ════════════════════════════════════════════════════════════════════════

class TestS52HumanizeRejectionCopy:
    CAMEL = "ArchdukeCharles"
    HUMAN = "Archduke Charles"

    def _engaged_world(self):
        world = WorldState()
        world.marshals = {}
        world.regions = {
            "Paris": Region("Paris", ["Vienna"], 100),
            "Vienna": Region("Vienna", ["Paris"], 100),
        }
        world.regions["Paris"].controller = "France"
        world.regions["Vienna"].controller = "Austria"
        world.player_nation = "France"
        world.current_turn = 1
        _france_at_war_with(world, "Austria")
        ney = Marshal("Ney", "Paris", 30000, "aggressive", "France")
        charles = Marshal(self.CAMEL, "Paris", 30000, "cautious", "Austria")
        world.marshals["Ney"] = ney
        world.marshals[self.CAMEL] = charles
        return world

    def test_attack_engaged_copy_humanized(self):
        world = self._engaged_world()
        ex = CommandExecutor()
        ney = world.marshals["Ney"]
        result = ex._combat._execute_attack(
            ney, "Vienna", world, _game_state(world))
        msg = result.get("message", "")
        assert self.HUMAN in msg
        assert self.CAMEL not in msg
        assert self.CAMEL not in result.get("suggestion", "")

    def test_strategic_march_engaged_copy_humanized(self):
        world = self._engaged_world()
        ex = CommandExecutor()
        result = ex._strategic._execute_strategic_command(
            {"strategic_type": "MOVE_TO"},
            {"marshal": "Ney", "action": "move", "target": "Vienna"},
            _game_state(world))
        msg = result.get("message", "")
        assert self.HUMAN in msg
        assert self.CAMEL not in msg

    def test_move_into_visible_enemy_copy_humanized(self):
        from backend.models.intel import FULL
        world = WorldState()
        world.marshals = {}
        world.regions = {
            "Paris": Region("Paris", ["Vienna"], 100),
            "Vienna": Region("Vienna", ["Paris"], 100),
        }
        world.regions["Paris"].controller = "France"
        world.regions["Vienna"].controller = "Austria"
        world.player_nation = "France"
        world.current_turn = 1
        _france_at_war_with(world, "Austria")
        ney = Marshal("Ney", "Paris", 30000, "aggressive", "France")
        charles = Marshal(self.CAMEL, "Vienna", 30000, "cautious", "Austria")
        world.marshals["Ney"] = ney
        world.marshals[self.CAMEL] = charles
        world.get_region_intel("Vienna").visibility = FULL
        ex = CommandExecutor()
        result = ex._movement._execute_move(
            ney, "Vienna", world, _game_state(world))
        msg = result.get("message", "")
        assert self.HUMAN in msg
        assert self.CAMEL not in msg


# ════════════════════════════════════════════════════════════════════════
# S5-3 — reward-expectation rail notice stays live (numbers + countdown)
# ════════════════════════════════════════════════════════════════════════

class TestS53DotationRailLive:
    def _europe_world(self):
        world = WorldState()
        world.sovereign_map = "europe"
        world.player_nation = "France"
        world.current_turn = 10
        world.marshals.clear()
        ney = Marshal("Ney", "Paris", 30000, "aggressive", "France")
        ney.battles_won = 2          # expectation = 40 * 2 = 80
        ney.dotation_regions = []    # no estates → satisfaction 0
        ney.pension = 0
        ney.expectation_grace_turn = -1
        world.marshals["Ney"] = ney
        return world, ney

    def _notice(self, world):
        from backend.notifications import DOTATION_EXPECTATION
        return [n for n in world.notifications.get_pending()
                if n["type"] == DOTATION_EXPECTATION
                and n.get("details", {}).get("marshal") == "Ney"]

    def test_open_then_refresh_then_dismiss(self):
        world, ney = self._europe_world()

        # Turn 10 — shortfall opens.
        world._process_dotation_state()
        notices = self._notice(world)
        assert len(notices) == 1
        assert notices[0]["details"]["expectation"] == 80
        assert notices[0]["details"]["remaining_grace"] == 2
        assert "80g/turn" in notices[0]["message"]

        # Turn 11 — expectation GROWS; the rail must track it (not stay 80).
        ney.battles_won = 4          # expectation = 160
        world.current_turn = 11
        world._process_dotation_state()
        notices = self._notice(world)
        assert len(notices) == 1, "must not stack a duplicate"
        assert notices[0]["details"]["expectation"] == 160
        assert notices[0]["details"]["remaining_grace"] == 1
        assert "160g/turn" in notices[0]["message"]
        assert "one more turn" in notices[0]["message"]

        # Turn 12 — grace elapses → erosion owns the narrative; the stale
        # NORMAL expectation notice is dropped so the rail never contradicts
        # the dispatch/erosion HIGH notice.
        world.current_turn = 12
        world._process_dotation_state()
        assert self._notice(world) == []
        from backend.notifications import DOTATION_EROSION
        erosion = [n for n in world.notifications.get_pending()
                   if n["type"] == DOTATION_EROSION]
        assert erosion, "erosion notice should fire when grace elapses"

    def test_paying_back_to_met_dismisses_notice(self):
        """Adversarial-review finding: if the player DOES reward the marshal
        mid-grace, the stale 'reward him' rail notice must clear — it must not
        contradict the grant confirmation."""
        world, ney = self._europe_world()

        # Turn 10 — shortfall opens, notice posted.
        world._process_dotation_state()
        assert len(self._notice(world)) == 1

        # Turn 11 — player endows him (rente face meets the 80g expectation).
        ney.pension = 80  # satisfaction now 80 == expectation → met
        world.current_turn = 11
        world._process_dotation_state()
        assert self._notice(world) == [], \
            "the reward-expectation notice must be dismissed once met"


# ════════════════════════════════════════════════════════════════════════
# S5-5 — bombard no-guns guard (single source) + fixed-corps copy
# ════════════════════════════════════════════════════════════════════════

class TestS55BombardGuard:
    def test_no_artillery_marshal_cannot_bombard(self):
        world = WorldState()
        world.marshals = {}
        world.regions = {
            "Paris": Region("Paris", ["Vienna"], 100),
            "Vienna": Region("Vienna", ["Paris"], 100),
        }
        world.regions["Paris"].controller = "France"
        world.regions["Vienna"].controller = "Austria"
        world.player_nation = "France"
        _france_at_war_with(world, "Austria")
        ney = Marshal("Ney", "Paris", 30000, "aggressive", "France")
        ney.artillery = False
        enemy = Marshal("Charles", "Vienna", 20000, "cautious", "Austria")
        world.marshals["Ney"] = ney
        world.marshals["Charles"] = enemy
        ex = CommandExecutor()
        result = ex._combat._execute_bombardment(ney, enemy, world,
                                                  _game_state(world))
        assert result["success"] is False
        assert "no artillery" in result["message"].lower()


class TestS55CorpsSizeCopy:
    def test_field_capped_note_cites_true_corps_size(self):
        world = WorldState()
        world.marshals = {}
        world.regions = {
            "Field": Region("Field", ["Front"], 100, region_type="town"),
            "Front": Region("Front", ["Field"], 100, region_type="town"),
        }
        world.regions["Field"].controller = "France"
        world.regions["Field"].stability = 100
        world.regions["Front"].controller = "France"
        world.player_nation = "France"
        world.nation_gold["France"] = 100000
        world.manpower_pools["France"] = {
            "infantry": 50000, "cavalry": 20000, "artillery": 10000}
        ney = Marshal("Ney", "Field", 30000, "aggressive", "France")
        world.marshals["Ney"] = ney
        ex = CommandExecutor()
        result = ex._economy._execute_recruit(
            {"marshal": "Ney", "raw_command": "recruit 500 men"},
            _game_state(world))
        assert result["success"] is True, result.get("message")
        msg = result["message"]
        # Field-capped delivery is 3,000; the TRUE fixed corps is 10,000.
        assert "capped at 3,000" in msg
        assert "fixed corps of 10,000" in msg
        assert "fixed corps of 3,000" not in msg


# ════════════════════════════════════════════════════════════════════════
# S5-D2 — MOVE_TO issuance-time passability honesty
# ════════════════════════════════════════════════════════════════════════

class TestS5D2IssuancePassability:
    def _blocked_world(self):
        world = WorldState()
        world.marshals = {}
        world.regions = {
            "Home": Region("Home", ["Gate"], 100),
            "Gate": Region("Gate", ["Home", "Goal"], 100),
            "Goal": Region("Goal", ["Gate"], 100),
        }
        world.regions["Home"].controller = "France"
        world.regions["Gate"].controller = "Austria"   # PEACE by default → closed
        world.regions["Goal"].controller = "France"
        world.player_nation = "France"
        world.current_turn = 1
        ney = Marshal("Ney", "Home", 30000, "aggressive", "France")
        world.marshals["Ney"] = ney
        return world

    def test_unreachable_dest_rejected_at_issuance_no_ap(self):
        world = self._blocked_world()
        ex = CommandExecutor()
        result = ex._strategic._execute_strategic_command(
            {"strategic_type": "MOVE_TO"},
            {"marshal": "Ney", "action": "move", "target": "Goal"},
            _game_state(world))
        assert result["success"] is False
        assert result.get("variable_action_cost") == 0
        msg = result["message"].lower()
        assert "no open road" in msg
        assert "gate" in msg  # the blocking frontier is named

    def test_open_corridor_not_rejected(self):
        """When a passable route exists, the rider must not fire."""
        world = self._blocked_world()
        # Open the frontier: France at war with Austria → territory passable.
        _france_at_war_with(world, "Austria")
        ex = CommandExecutor()
        result = ex._strategic._execute_strategic_command(
            {"strategic_type": "MOVE_TO"},
            {"marshal": "Ney", "action": "move", "target": "Goal"},
            _game_state(world))
        # Not the S5-D2 rejection (order may still succeed or pend objection).
        assert not (result.get("success") is False
                    and "no open road" in result.get("message", "").lower())


# ════════════════════════════════════════════════════════════════════════
# AUD-g — military-advantage bands: symmetric, grammatical, real parity tier
# ════════════════════════════════════════════════════════════════════════

class TestAudGMilitaryBands:
    def _world_with_ratio(self, nation_strength, player_strength=20000):
        """British marshal at Paris → FULL visibility for France."""
        world = WorldState()
        world.marshals = {}
        world.regions = {"Paris": Region("Paris", [], 100)}
        world.regions["Paris"].controller = "France"
        world.player_nation = "France"
        ney = Marshal("Ney", "Paris", player_strength, "aggressive", "France")
        brit = Marshal("Wellington", "Paris", nation_strength, "cautious",
                       "Britain")
        world.marshals["Ney"] = ney
        world.marshals["Wellington"] = brit
        world.calculate_visibility()
        return world

    @pytest.mark.parametrize("ratio_strength,expected", [
        (40000, "overwhelming"),   # 2.0
        (25000, "superior"),       # 1.25
        (20000, "comparable"),     # 1.0 — the real parity tier (was "slight")
        (16000, "inferior"),       # 0.8 (0.67–0.87)
        (8000, "overmatched"),     # 0.4
    ])
    def test_band_labels(self, ratio_strength, expected):
        world = self._world_with_ratio(ratio_strength)
        assert _get_military_advantage("Britain", world) == expected

    def test_no_dead_even_or_ungrammatical_disadvantage(self):
        """The dead 'even' tier and the ungrammatical 'disadvantage' word are
        gone across the full-visibility range."""
        for strength in (8000, 16000, 20000, 25000, 40000):
            band = self._get(strength)
            assert band not in ("even", "disadvantage", "slight", "significant")

    def _get(self, strength):
        return _get_military_advantage("Britain", self._world_with_ratio(strength))


# ════════════════════════════════════════════════════════════════════════
# AUD-e / S5-4 — doc & docstring reconciliation pins
# ════════════════════════════════════════════════════════════════════════

class TestDocReconciliation:
    def test_select_next_action_docstring_matches_shipped_sort(self):
        doc = EnemyAI._select_next_marshal_action.__doc__
        assert "SHIPPED sort" in doc
        assert "round-robin" in doc.lower()
        # The stale, false claim must be gone.
        assert "priority <= 60) override" not in doc

    def test_preempt_docstring_notes_no_longer_hard_stop_only(self):
        doc = DialogueManager.preempt.__doc__
        assert "S5-4" in doc
        assert "Pre-EA Dialogue Robustness" in doc
        assert "hard-stop-only" in doc  # explicitly retracted
