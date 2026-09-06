"""FA-S16-D4 (FA-98) — "The School Has No Laurels".

The twelve-turn lesson reported *"Ney, crowned four turns ago, has been
beaten in the field"* about a mechanic it never teaches. TUT-F5 had gated
jealousy in the School and deliberately left glory running so "the Generals
screen stays honest."

⚠ **That carve-out is CONSCIOUSLY OVERRULED, and the reason is that the
crown is not a display.** It is +1 shock / +1 defense / +1 administration;
Ney's admin 3→4 crosses the MC-2b Intendance tier boundary, which is a
recruit price; and **Austria's Schwarzenberg is crowned in the lesson too**,
so it is an AI-side combat modifier. What the carve-out was protecting is
`battles_won`, and `battles_won` is measured byte-identical under the gate.

⚠ **The leak is FIVE wide, not the four the row counts.** `glory_crown_lost`
fires twice in the shipped trust lesson and is **never written to
`event_log`** — only the gain branch logs — so an `event_log` census is blind
to it by construction. These pins read the DELIVERED events.

⚠ **Gating glory alone SWAPS a leak rather than closing it.** §4's
restlessness loop has a literal arm that reads `consecutive_hold_turns` and
never touches the ladder. Measured on the shipped trust lesson: at HEAD the
`warned >= 1` break is consumed by Davout's ladder arm at turn 2, so gating
glory alone makes *Soult's* line appear where it does not fire today. Both
guards ship, on separate levers, so the two are measurable apart.
"""

import ast
import importlib.util
import inspect
import os
import pathlib
import sys

import pytest

from backend.game_logic import dispatch, dotation, jealousy
from backend.models.world_state import WorldState

REPO = pathlib.Path(__file__).resolve().parents[1]
TUTORIAL = str(REPO / "godot-client" / "project-sovereign" / "assets" /
               "maps" / "tutorial_1805.json")
CAMPAIGN = str(REPO / "godot-client" / "project-sovereign" / "assets" /
               "maps" / "europe_1805.json")


def _quiet(fn, *a, **k):
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


@pytest.fixture
def lesson():
    return _quiet(WorldState.from_scenario, TUTORIAL)


@pytest.fixture
def campaign():
    return _quiet(WorldState.from_scenario, CAMPAIGN)


# ═══════════════════════════════════════════════════════════════════════════
# The predicate
# ═══════════════════════════════════════════════════════════════════════════

class TestThePredicate:

    def test_both_directions_against_the_real_boot_value(self, lesson,
                                                         campaign):
        """⚠ Assert against the campaign world's ACTUAL name, not "" — a pin
        that compares to the empty string passes on a world that has no
        scenario at all and proves nothing about the discriminator."""
        assert campaign.scenario_name == "The Third Coalition, 1805"
        assert jealousy.glory_dormant(lesson) is True
        assert jealousy.glory_dormant(campaign) is False

    def test_the_lever_reproduces_head(self, lesson, monkeypatch):
        monkeypatch.setattr(jealousy, "GLORY_DORMANT_ACTIVE", False)
        assert jealousy.glory_dormant(lesson) is False

    def test_it_is_not_folded_into_jealousy_dormant(self):
        """The two carve-outs answer different questions and one of them
        overrules a written precedent. They keep separate names and separate
        levers so a future reader can move one without the other."""
        assert jealousy.GLORY_DORMANT_ACTIVE is not None
        assert jealousy.RESTLESSNESS_SLEEPS_IN_SCHOOL is not None
        src = inspect.getsource(jealousy.jealousy_dormant)
        assert "GLORY_DORMANT_ACTIVE" not in src


# ═══════════════════════════════════════════════════════════════════════════
# The chokepoint really is one
# ═══════════════════════════════════════════════════════════════════════════

class TestTheChokepointIsComplete:

    def _append_calls(self):
        tree = ast.parse((REPO / "backend" / "game_logic" /
                          "jealousy.py").read_text(encoding="utf-8"))
        inside, outside = [], []
        owner = None
        for node in ast.walk(tree):
            if (isinstance(node, ast.FunctionDef)
                    and node.name == "record_battle_glory"):
                owner = (node.lineno, node.end_lineno)
        assert owner
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "_append_glory"):
                (inside if owner[0] <= node.lineno <= owner[1]
                 else outside).append(node.lineno)
        return inside, outside

    def test_every_accrual_is_inside_the_gated_function(self):
        """An AST census, not a grep: a call in another function would
        accrue glory in the School with the gate green."""
        inside, outside = self._append_calls()
        assert inside, "no accrual calls found at all — the census is broken"
        assert outside == [], f"ungated accrual at lines {outside}"

    def test_the_census_can_see_an_offender(self, tmp_path):
        """Sensitivity arm. Without it the census above passes on a walker
        that finds nothing (slice 15's own lesson: `assert borrowed or True`
        under a walk that matched nothing on any file)."""
        src = "def elsewhere():\n    _append_glory(1)\n"
        tree = ast.parse(src)
        found = [n.lineno for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "_append_glory"]
        assert found == [2]


# ═══════════════════════════════════════════════════════════════════════════
# Driven: the lesson, twelve turns, both levers
# ═══════════════════════════════════════════════════════════════════════════

def _drive(script, turns=12, glory=True, restless=True):
    """The real driver, IN-PROCESS.

    ⚠ `playtest_driver.main()` re-execs a subprocess, which silently
    discards a monkeypatched lever — an arm taken that way measures HEAD
    and reports it as the fix.
    """
    import argparse
    import contextlib
    import io
    import tempfile

    spec = importlib.util.spec_from_file_location(
        "pdrv_d4", str(REPO / "tools" / "playtest_driver.py"))
    drv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drv)

    real = jealousy.process_turn
    caught = []

    def wrapped(world):
        evs = real(world)
        for e in (evs or []):
            caught.append((world.current_turn, e.get("type"),
                           e.get("marshal")))
        return evs

    prev_glory = jealousy.GLORY_DORMANT_ACTIVE
    prev_rest = jealousy.RESTLESSNESS_SLEEPS_IN_SCHOOL
    prev_save = os.environ.get("INK_IRON_SAVE_DIR")
    prev_seed = os.environ.get("SOVEREIGN_SEED")
    prev_llm = os.environ.get("LLM_MODE")
    tmp = tempfile.mkdtemp()
    try:
        jealousy.GLORY_DORMANT_ACTIVE = glory
        jealousy.RESTLESSNESS_SLEEPS_IN_SCHOOL = restless
        jealousy.process_turn = wrapped
        os.environ["INK_IRON_SAVE_DIR"] = os.path.join(tmp, "saves")
        os.environ["SOVEREIGN_SEED"] = "historical"
        os.environ["LLM_MODE"] = "mock"
        ns = argparse.Namespace(
            name="d4", turns=turns, seed="historical", llm="mock",
            scenario="", script=str(REPO / "tools" / "playtest_scripts" /
                                    (script + ".json")),
            from_save="", http="", out=os.path.join(tmp, "out"),
            save_at="", objection="", diplomacy="", cheats=False,
            strict=False, verbose=False, fresh=True, archive=False)
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                drv.run(ns)
            except SystemExit:
                pass
    finally:
        jealousy.process_turn = real
        jealousy.GLORY_DORMANT_ACTIVE = prev_glory
        jealousy.RESTLESSNESS_SLEEPS_IN_SCHOOL = prev_rest
        for k, v in (("INK_IRON_SAVE_DIR", prev_save),
                     ("SOVEREIGN_SEED", prev_seed), ("LLM_MODE", prev_llm)):
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return caught


@pytest.mark.skipif(sys.platform not in ("win32", "linux", "darwin"),
                    reason="driver")
class TestTheLessonIsSilent:

    def test_no_glory_beat_of_either_kind(self):
        """⚠ Reads the DELIVERED events, not `event_log`. The loss beat is
        never logged — only the gain branch calls `world.log_event` — so an
        `event_log` census cannot see half the leak."""
        got = _drive("tutorial_lesson_trust")
        assert [c for c in got if c[1] in ("glory_crowned",
                                           "glory_crown_lost")] == []

    def test_the_negative_control_produces_both_kinds(self):
        """If the lever-False arm produced nothing, the pin above would be
        green on a lesson that never crowns anyone anyway."""
        got = _drive("tutorial_lesson_trust", glory=False, restless=False)
        gained = [c for c in got if c[1] == "glory_crowned"]
        lost = [c for c in got if c[1] == "glory_crown_lost"]
        assert len(gained) == 3, gained
        assert len(lost) == 2, lost

    def test_no_restlessness_beat_of_any_arm(self):
        """⚠ This is the pin the filed recommendation REDS on its own build:
        gating glory alone leaves §4's literal arm firing."""
        got = _drive("tutorial_lesson_trust")
        assert [c for c in got if c[1] == "jealousy_restlessness"] == []

    def test_the_two_guards_are_independent(self):
        """⚠ ADDED after a sweep: D4/g came back INERT, and it was right to.

        On the lesson world `glory_dormant` and `jealousy_dormant` agree, so
        keying the restlessness guard on the WRONG one is invisible — until
        someone sets `GLORY_DORMANT_ACTIVE = False` to put the ladder back,
        at which point a glory-keyed guard silently re-opens TUT-F5's
        separate contract. This is the one combination that can tell them
        apart, and nothing else in the file drives it.
        """
        got = _drive("tutorial_lesson_trust", glory=False, restless=True)
        assert [c for c in got if c[1] == "jealousy_restlessness"] == []
        # …and glory is genuinely back, so the arm is not vacuous
        assert [c for c in got if c[1] == "glory_crowned"]

    def test_gating_glory_alone_unmasks_soult(self):
        """The measurement that forced the second guard. At HEAD the single
        allowed warning is consumed by Davout's LADDER arm; silence the
        ladder and Soult's LITERAL arm takes the slot — a beat that does not
        fire in the shipped lesson appears because of the fix."""
        head = _drive("tutorial_lesson_trust", glory=False, restless=False)
        glory_only = _drive("tutorial_lesson_trust", glory=True,
                            restless=False)
        head_r = [c for c in head if c[1] == "jealousy_restlessness"]
        only_r = [c for c in glory_only if c[1] == "jealousy_restlessness"]
        assert head_r and "Soult" not in {c[2] for c in head_r}
        assert "Soult" in {c[2] for c in only_r}


# ═══════════════════════════════════════════════════════════════════════════
# The mechanic sleeps, on BOTH sides
# ═══════════════════════════════════════════════════════════════════════════

class TestTheMechanicSleeps:

    def test_no_marshal_of_any_nation_accrues_or_wears(self, lesson):
        """⚠ Over every marshal, not over France: Austria's Schwarzenberg is
        crowned in the shipped lesson, defense 7→8."""
        jealousy.record_battle_glory(
            lesson, lesson.get_marshal("Ney"),
            next(m for m in lesson.marshals.values() if m.nation != "France"),
            True, False, 100, 9000, True, 30000, 20000)
        assert all(not getattr(m, "glory_events", [])
                   for m in lesson.marshals.values())
        jealousy.recompute_crowns(lesson)
        for m in lesson.marshals.values():
            assert not getattr(m, "glory_crowned", False), m.name
            for skill in getattr(type(m), "CROWN_SKILLS", ("shock", "defense")):
                assert m.get_effective_skill(skill) == m.skills.get(skill, 5)
            assert m.get_admin_with_crown() == m.skills.get("administration", 5)

    def test_the_campaign_world_still_crowns(self, campaign):
        """The pin above passes on a deleted feature without this one."""
        ney = campaign.get_marshal("Ney")
        foe = next(m for m in campaign.marshals.values()
                   if m.nation != "France")
        jealousy.record_battle_glory(campaign, ney, foe, True, False,
                                     100, 9000, True, 30000, 20000)
        assert ney.glory_events, "the campaign board stopped accruing glory"

    def test_the_ladder_payload_is_empty_in_the_school(self, lesson,
                                                       campaign):
        assert jealousy.build_glory_ladder_payload(lesson) == []
        # the one `.gd` reader guards on size() > 1
        ney = campaign.get_marshal("Ney")
        foe = next(m for m in campaign.marshals.values()
                   if m.nation != "France")
        jealousy.record_battle_glory(campaign, ney, foe, True, False,
                                     100, 9000, True, 30000, 20000)
        assert len(jealousy.build_glory_ladder_payload(campaign)) > 1


# ═══════════════════════════════════════════════════════════════════════════
# The migration case — invisible to any fresh-run pin
# ═══════════════════════════════════════════════════════════════════════════

class TestALoadedLesson:

    def test_a_migrated_crown_is_cleared_in_silence(self, lesson):
        """⚠ TUT-F2 permits manual saves in the tutorial, so a save written
        before this build carries `glory_crowned: True`. An accrual gate
        cannot reach stored state.

        Both alternatives were measured and both are worse: `return []`
        freezes the crown forever at +1 skills, and leaving the function
        running delivers "the laurels have passed" into the classroom when
        the 8-turn window rolls the events off.
        """
        ney = lesson.get_marshal("Ney")
        ney.glory_crowned = True
        ney.glory_events = [{"turn": lesson.current_turn, "points": 5}]
        base = ney.skills.get("shock", 5)
        assert ney.get_effective_skill("shock") == base + 1

        events = jealousy.recompute_crowns(lesson)
        assert ney.glory_crowned is False
        assert ney.get_effective_skill("shock") == base
        assert [e for e in events
                if e.get("type") in ("glory_crowned", "glory_crown_lost")] == []

    def test_the_same_blob_on_the_campaign_world_keeps_its_crown(self,
                                                                 campaign):
        ney = campaign.get_marshal("Ney")
        ney.glory_crowned = True
        ney.glory_events = [{"turn": campaign.current_turn, "points": 50}]
        jealousy.recompute_crowns(campaign)
        assert ney.glory_crowned is True


# ═══════════════════════════════════════════════════════════════════════════
# The beat is unreachable, not merely unrendered
# ═══════════════════════════════════════════════════════════════════════════

class TestTheSentenceIsGone:

    def test_the_appositive_needs_a_crown_turn(self, lesson):
        ney = lesson.get_marshal("Ney")
        line = dispatch._compose_reversal_line(
            lesson, ney, None, None, None, False, 1, "", "")
        assert "crowned" not in line
        assert line, "the reversal line vanished entirely"

    def test_the_campaign_board_still_says_it(self, campaign):
        """Paired arm: without it the pin above passes on a deleted
        sentence."""
        ney = campaign.get_marshal("Ney")
        line = dispatch._compose_reversal_line(
            campaign, ney, 2, None, None, False, 1, "", "")
        assert "crowned" in line

    def test_the_school_produces_no_crown_turn(self, lesson):
        arcs = dispatch._build_marshal_arcs(lesson, lesson.player_nation) or {}
        for name, arc in (arcs.items() if isinstance(arcs, dict) else []):
            assert not (arc or {}).get("crown_turn"), name


# ═══════════════════════════════════════════════════════════════════════════
# What the overrule cost, and what it did not
# ═══════════════════════════════════════════════════════════════════════════

class TestTheCarveOutThatWasOverruled:

    def test_battles_won_is_what_the_carve_out_was_really_protecting(self):
        """⚠ The defence of overruling PC15-D3's written clause. `battles_won`
        — the number the Generals screen and the dotation record actually
        need — is byte-identical with the lever either way. Measured, not
        asserted: 6/5/5/0 on the trust script, 4/3/3/0 on the insist script.

        ⚠ Do NOT hard-code those figures against a foreign script: the
        recommendation quoted 4/3/0/3 from one branch and this build measures
        6/5/5/0 on the other, and a literal would red on arrival.
        """
        import argparse
        import contextlib
        import io
        import tempfile

        spec = importlib.util.spec_from_file_location(
            "pdrv_d4b", str(REPO / "tools" / "playtest_driver.py"))
        drv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(drv)

        seen = {}
        real = dispatch._build_marshal_arcs
        worlds = []

        def spy(world, *a, **k):
            worlds.append(world)
            return real(world, *a, **k)

        for lever in (True, False):
            prev = jealousy.GLORY_DORMANT_ACTIVE
            prev_save = os.environ.get("INK_IRON_SAVE_DIR")
            tmp = tempfile.mkdtemp()
            try:
                jealousy.GLORY_DORMANT_ACTIVE = lever
                dispatch._build_marshal_arcs = spy
                os.environ["INK_IRON_SAVE_DIR"] = os.path.join(tmp, "s")
                os.environ["SOVEREIGN_SEED"] = "historical"
                worlds.clear()
                ns = argparse.Namespace(
                    name="d4b", turns=12, seed="historical", llm="mock",
                    scenario="",
                    script=str(REPO / "tools" / "playtest_scripts" /
                               "tutorial_lesson_trust.json"),
                    from_save="", http="", out=os.path.join(tmp, "o"),
                    save_at="", objection="", diplomacy="", cheats=False,
                    strict=False, verbose=False, fresh=True, archive=False)
                with contextlib.redirect_stdout(io.StringIO()):
                    try:
                        drv.run(ns)
                    except SystemExit:
                        pass
                w = worlds[-1]
                seen[lever] = {m.name: getattr(m, "battles_won", 0)
                               for m in w.marshals.values()
                               if m.nation == w.player_nation}
            finally:
                jealousy.GLORY_DORMANT_ACTIVE = prev
                dispatch._build_marshal_arcs = real
                if prev_save is None:
                    os.environ.pop("INK_IRON_SAVE_DIR", None)
                else:
                    os.environ["INK_IRON_SAVE_DIR"] = prev_save

        assert seen[True] == seen[False], seen
        assert sum(seen[True].values()) > 0, "nobody won a battle — vacuous"

    def test_the_two_prose_sites_were_narrowed(self):
        """Both docstrings claimed glory keeps accruing. One of them is the
        precedent this build overrules; leaving it standing is how the next
        reader concludes the overrule was an accident."""
        assert "NARROWED" in (dotation.dotation_dormant.__doc__ or "")
        assert "CORRECTED" in (jealousy.jealousy_dormant.__doc__ or "")

    def test_the_scenario_name_contract_was_corrected(self):
        """⚠ `scenario_name`'s own declaration said "NO mechanic may ever
        branch on this field" — false since TUT-F5, and this build makes it
        emphatically false by gating a live combat modifier on it."""
        src = (REPO / "backend" / "models" /
               "world_state.py").read_text(encoding="utf-8")
        i = src.index("self.scenario_name: str")
        window = src[max(0, i - 1600):i]
        assert "NO mechanic may ever branch on this field" not in window
        assert "carve-out" in window.lower()

    def test_the_gd_prohibition_holds(self):
        """⚠ `test_tutorial_position7.py:263` pins "only glory answers envy"
        in `marshal_management.gd` as a CONSCIOUS FLIP of the R159 contract.
        The recommendation offered deleting it as a free one-string edit; it
        is not free, and this build does not take it."""
        gd = (REPO / "godot-client" / "project-sovereign" / "scripts" /
              "marshal_management.gd").read_text(encoding="utf-8")
        assert "only glory answers envy" in gd


# ═══════════════════════════════════════════════════════════════════════════
# The harnesses need no re-record, and here is why
# ═══════════════════════════════════════════════════════════════════════════

class TestHarnessImmunity:

    def test_neither_harness_world_is_the_lesson(self, campaign):
        """State the reason rather than treating a green harness as
        evidence: `BASELINE_SERIES` and M1–M7 boot the campaign scenario or
        the bare world, and `glory_dormant` is world-scoped."""
        assert campaign.scenario_name != "tutorial"
        for f in ("test_ai_intent_threat_migration.py",
                  "test_combat_sweep_metrics.py"):
            src = (REPO / "tests" / f).read_text(encoding="utf-8")
            assert "tutorial" not in src


# ═══════════════════════════════════════════════════════════════════════════
# The ruling is on the record
# ═══════════════════════════════════════════════════════════════════════════

class TestTheRulingIsRecorded:

    def test_the_gate_block_records_the_decision(self):
        gate = (REPO / "docs" / "DESIGN_REFINEMENT.md").read_text(
            encoding="utf-8")
        block = gate[gate.index("### FA-S16-D4"):]
        # ⚠ D1's section follows D4 in the file, so slicing to "## Source
        # Documents" swallows it and the pin passes on D1's banner.
        block = block[:block.index("### FA-S16-D1")]
        assert "RULED" in block
        assert "BUG_FIXES.md" in block

    def test_the_row_names_the_fifth_leak_and_the_overrule(self):
        rows = (REPO / "docs" / "BUG_FIXES.md").read_text(encoding="utf-8")
        line = [ln for ln in rows.split("\n")
                if ln.lstrip("> ").startswith("| **FA-98** |")]
        assert line, "FA-98's row has gone missing"
        assert "NOT BUILT" not in line[0]
        assert "glory_crown_lost" in line[0], (
            "the row's four-leak framing must be corrected to five")
        assert "PC15-D3" in line[0], (
            "the overrule of a written carve-out belongs on the row")
