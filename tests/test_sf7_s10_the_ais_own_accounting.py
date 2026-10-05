"""Score Finish Step 7, slice 10 — the AI's own accounting (Oct 5, 2026).

Two mechanics defects the frames' own reading found (slice 9 filed them):

- **SF7-X33 — a refused raid destroyed the garrison it could not take.** The
  attack's unopposed branch cleared a capital's garrison under the collapse
  line (or a detachment under the surrender floor) BEFORE VP-R1 (b)'s
  raiding-party question, so a corps under 5,000 emptied the garrison and was
  then refused: the province untaken, the garrison gone.
- **SF7-X34 — the AI's stagnation tracker counted a capture as achieving
  nothing.** It read only `battle` events, so an attack that took a province
  through a garrison's collapse or an unopposed capture left the marshal
  idle ("ArchdukeJohn attacked but achieved nothing", twice, on the turn he
  took Milan in the live session).

And a third the slice's own board found, through the pre-commit hook:

- **SF7-X35 — a war opened by any road but a declaration had no purpose until
  the next load gave it one** (the census's played round trip diverged on
  `war_objectives` once Switzerland rebelled inside its twelve turns).

Rows `docs/BUG_FIXES.md` SF7-X33 / SF7-X34 / SF7-X35; rules
`docs/SYSTEMS_REFERENCE.md` §93.12; the series attribution
`tools/_sf7_s10_series_arms.py`.
"""

from __future__ import annotations

import ast
import contextlib
import io
import random
from pathlib import Path

from backend.ai import enemy_ai as EA
from backend.commands import combat_executor as CE
from backend.commands.executor import CommandExecutor
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
SCENARIO = REPO / "godot-client" / "project-sovereign" / "assets" / "maps" / "europe_1805.json"


def _boot():
    with contextlib.redirect_stdout(io.StringIO()):
        world = WorldState.from_scenario(str(SCENARIO))
    executor = CommandExecutor()
    return world, executor, {"world": world, "executor": executor}


def _run(executor, game_state, command):
    with contextlib.redirect_stdout(io.StringIO()):
        random.seed(1805)
        return executor.execute({"command": command}, game_state)


# ═════════════════════════ SF7-X33 — the raid leaves the garrison ══════════


class TestARefusedRaidLeavesTheGarrison:
    @staticmethod
    def _stage_vienna(world, garrison=3000, raiders=3000):
        vienna = world.get_region("Vienna")
        for m in world.marshals.values():
            if m.location == "Vienna":
                m.location = "Hungary"
        vienna.garrison_strength = garrison
        vienna.garrison_detachment = False
        ney = world.marshals["Ney"]
        ney.location = "Bohemia"
        ney.strength = raiders
        return vienna

    def test_the_player_raid_is_refused_and_the_garrison_stands(self):
        world, executor, gs = _boot()
        vienna = self._stage_vienna(world)
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "Vienna", "_muster_confirmed": True})
        assert result.get("success") is False
        assert result.get("capture_refused_raiding_party") is True
        assert "raiding party" in result["message"]
        assert vienna.garrison_strength == 3000, "the garrison it could not take stands"
        assert vienna.controller == "Austria"

    def test_gr5_the_ai_raid_is_refused_the_same_way(self):
        world, executor, gs = _boot()
        munich = world.get_region("Munich")
        for m in world.marshals.values():
            if m.location == "Munich":
                m.location = "Franconia"
        munich.garrison_strength = 2500
        munich.garrison_detachment = False
        world.marshals["Mack"].strength = 3000
        result = _run(executor, gs, {"action": "attack", "marshal": "Mack", "target": "Munich",
                                     "_acting_nation": "Austria", "_muster_confirmed": True})
        assert result.get("capture_refused_raiding_party") is True
        assert munich.garrison_strength == 2500

    def test_an_army_still_takes_it(self):
        """The control arm: a corps over the floor finds the garrison giving
        way (slice 9's sentence) and takes the province."""
        world, executor, gs = _boot()
        vienna = self._stage_vienna(world, raiders=30000)
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "Vienna", "_muster_confirmed": True})
        assert result.get("success"), result.get("message")
        assert "give way" in result["message"]
        assert vienna.garrison_strength == 0

    def test_the_lever_restores_the_old_order(self, monkeypatch):
        monkeypatch.setattr(CE.CombatExecutor, "A_REFUSED_RAID_LEAVES_THE_GARRISON", False)
        world, executor, gs = _boot()
        vienna = self._stage_vienna(world)
        result = _run(executor, gs, {"action": "attack", "marshal": "Ney",
                                     "target": "Vienna", "_muster_confirmed": True})
        assert result.get("capture_refused_raiding_party") is True
        assert vienna.garrison_strength == 0, "the old order emptied it first"


# ═════════════════════════ SF7-X34 — a capture is an achievement ═══════════


class TestACaptureIsAnAchievement:
    def test_a_taken_province_counts(self):
        for etype in ("conquest", "occupation_started", "garrison_destroyed"):
            assert EA.attack_achieved_something([{"type": etype}], "ArchdukeJohn"), etype

    def test_the_battle_rule_is_unchanged(self):
        won = {"type": "battle", "victor": "ArchdukeJohn"}
        lost = {"type": "battle", "victor": "Ney"}
        took = {"type": "battle", "victor": "Ney", "region_conquered": True}
        assert EA.attack_achieved_something([won], "ArchdukeJohn") is True
        assert EA.attack_achieved_something([lost], "ArchdukeJohn") is False
        assert EA.attack_achieved_something([took], "ArchdukeJohn") is True

    def test_a_garrison_that_held_is_not_an_achievement(self):
        held = {"type": "garrison_assault", "held": True, "garrison_remaining": 5000}
        assert EA.attack_achieved_something([held], "ArchdukeJohn") is False
        assert EA.attack_achieved_something([], "ArchdukeJohn") is False

    def test_the_milan_shape(self):
        """The live session's turn: the assault that held, then the capture."""
        assert EA.attack_achieved_something(
            [{"type": "garrison_assault", "held": True}], "ArchdukeJohn") is False
        assert EA.attack_achieved_something(
            [{"type": "conquest", "region": "Milan", "unopposed": True,
              "garrison_gave_way": 4800}], "ArchdukeJohn") is True

    def test_the_lever_restores_battles_only(self, monkeypatch):
        monkeypatch.setattr(EA, "THE_STAGNATION_COUNTS_A_CAPTURE", False)
        assert EA.attack_achieved_something([{"type": "conquest"}], "ArchdukeJohn") is False

    def test_the_stagnation_block_reads_the_one_predicate(self):
        """The call site: the tracker's attack arm asks the predicate (an
        AST census — the arm builds no `any(... type == "battle")` of its
        own any more)."""
        src = (REPO / "backend" / "ai" / "enemy_ai.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "attack_achieved_something"]
        assert len(calls) == 1, len(calls)
        assert "attacked but achieved nothing" in src
        assert 'for e in events if e.get("type") == "battle"' not in src


# ═════════════════════════ SF7-X35 — every war has its purpose ═════════════


class TestEveryWarHasItsPurpose:
    """SF7-X35, found when slice 10's board reached Switzerland's rebellion
    inside the census's twelve turns: a war opened by any road but a
    declaration (a cascade, an ally's entry, a rebellion, a defection, a
    collapsed truce) had NO objectives live, and the load migration supplied
    them — `tests/test_serialization_played_world_census.py`'s played round
    trip diverged on `war_objectives`. One rule now serves both seams
    (`diplomacy.give_the_war_its_purpose`)."""

    @staticmethod
    def _pair(world, a, b):
        return (world.war_objectives or {}).get(world._make_diplo_key(a, b)) or {}

    def test_a_cascade_war_opens_with_its_purpose(self):
        from backend.game_logic.diplomacy import set_diplomatic_state
        world, _ex, _gs = _boot()
        assert world.get_diplomatic_state("Prussia", "Hanover") != "WAR"
        set_diplomatic_state(world, "Prussia", "Hanover", "WAR", "defensive_cascade")
        pair = self._pair(world, "Prussia", "Hanover")
        assert pair["Prussia"]["type"] == "defense" and pair["Hanover"]["type"] == "defense"
        assert pair["Prussia"]["target_nation"] == "Hanover"

    def test_a_rebellion_war_opens_with_its_purpose(self):
        from backend.game_logic.diplomacy import set_diplomatic_state
        world, _ex, _gs = _boot()
        set_diplomatic_state(world, "Switzerland", "France", "WAR", "vassal_rebellion")
        pair = self._pair(world, "Switzerland", "France")
        assert set(pair) == {"Switzerland", "France"}

    def test_a_declaration_and_the_treaty_hop_assign_their_own(self):
        """A declaration names the aggressor's purpose itself (and gives the
        defender `defense`), and the settlement's ARMISTICE→WAR→VASSAL hop is
        bookkeeping — the rule stays out of both."""
        from backend.game_logic.diplomacy import set_diplomatic_state
        world, _ex, _gs = _boot()
        set_diplomatic_state(world, "Prussia", "Hanover", "WAR", "war_declaration")
        assert self._pair(world, "Prussia", "Hanover") == {}
        set_diplomatic_state(world, "Prussia", "Saxony", "WAR",
                             "common_peace_vassalage_ratification")
        assert self._pair(world, "Prussia", "Saxony") == {}

    def test_a_purpose_already_set_is_untouched(self):
        from backend.game_logic import diplomacy as D
        world, _ex, _gs = _boot()
        key = world._make_diplo_key("Prussia", "Hanover")
        world.war_objectives[key] = {"Prussia": D.create_war_objective(
            "conquest", "Prussia", "Hanover", ["Hanover"], world.current_turn)}
        D.set_diplomatic_state(world, "Prussia", "Hanover", "WAR", "offensive_cascade")
        assert set(world.war_objectives[key]) == {"Prussia"}
        assert world.war_objectives[key]["Prussia"]["type"] == "conquest"

    def test_the_live_war_survives_the_round_trip(self):
        import json
        from backend.game_logic.diplomacy import set_diplomatic_state
        world, _ex, _gs = _boot()
        set_diplomatic_state(world, "Switzerland", "France", "WAR", "vassal_rebellion")
        with contextlib.redirect_stdout(io.StringIO()):
            back = WorldState.from_dict(json.loads(json.dumps(world.to_dict())))
        assert back.to_dict()["war_objectives"] == world.to_dict()["war_objectives"]

    def test_the_lever_restores_the_purposeless_war(self, monkeypatch):
        from backend.game_logic import diplomacy as D
        monkeypatch.setattr(D, "A_NEW_WAR_HAS_A_PURPOSE", False)
        world, _ex, _gs = _boot()
        D.set_diplomatic_state(world, "Prussia", "Hanover", "WAR", "defensive_cascade")
        assert self._pair(world, "Prussia", "Hanover") == {}

    def test_an_old_save_is_still_migrated(self):
        """FA-S17-17's job is unchanged: a save from before the rule (a pair
        at WAR with no objectives in its data) gets them at load."""
        import json
        from backend.game_logic import diplomacy as D
        world, _ex, _gs = _boot()
        D.set_diplomatic_state(world, "Switzerland", "France", "WAR", "vassal_rebellion")
        data = json.loads(json.dumps(world.to_dict()))
        key = world._make_diplo_key("Switzerland", "France")
        data["war_objectives"].pop(key, None)
        with contextlib.redirect_stdout(io.StringIO()):
            back = WorldState.from_dict(data)
        assert set(back.war_objectives.get(key) or {}) == {"Switzerland", "France"}

    def test_the_legacy_world_boots_purposeless_by_design(self):
        """N1: the legacy fixture keeps its purposeless wars. ⛔ The first cut
        used France–Prussia, which the fixture boots AT WAR — the rule never
        ran and the sweep found the pin INERT; Austria–France opens at PEACE
        (the precondition is asserted)."""
        from backend.game_logic.diplomacy import set_diplomatic_state
        world = WorldState()
        a, b = "Austria", "France"
        assert world.get_diplomatic_state(a, b) == "PEACE"
        set_diplomatic_state(world, a, b, "WAR", "defensive_cascade")
        assert world.get_diplomatic_state(a, b) == "WAR"
        assert self._pair(world, a, b) == {}
