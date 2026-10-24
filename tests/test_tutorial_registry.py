"""S14d part 2 — the lessons' registry (`docs/TABLE_LESSON_SPEC.md` §4.4;
October 23, 2026). The School of War frame generalised to a second lesson
with the Danube BYTE-IDENTICAL: `LESSONS` in the overlay keyed by
`scenario_name`, `on_world_swap` binding `_steps` by name and clearing every
latch (S14D-X20), the released-step notes per lesson (S14D-X19), the
per-lesson done latch, `tutorial_state.SCHOOL_SCENARIOS` the one tuple the
allowlist derives from, `is_school_world()` the one carve-out predicate
(S14D-X16), the unused predicate gone (S14D-X21), the counts read from the
registry (S14D-X22).

The Danube's own pins (`_shipped_steps`, T-B1, the mirror drift pin,
`test_fa_slice8`, the unbreakable harness) are the byte-identity census;
this file pins the frame.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from backend.game_logic import tutorial_state as T
from backend.models.world_state import WorldState

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = PROJECT / "scripts"
OVERLAY = SCRIPTS / "tutorial_overlay.gd"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _func(src: str, name: str) -> str:
    start = src.index(f"func {name}(")
    nxt = src.find("\nfunc ", start + 5)
    return src[start:nxt if nxt > 0 else len(src)]


def _code_lines(src: str):
    """Source lines with comments stripped (a `#` outside a string)."""
    for line in src.split("\n"):
        stripped = line.split("#", 1)[0] if '"' not in line.split("#", 1)[0] or line.lstrip().startswith("#") else line
        yield stripped


class TestTheRegistry:
    def test_the_danube_is_the_first_entry_and_its_table_is_untouched(self):
        src = _read(OVERLAY)
        assert "const LESSONS := {" in src
        entry = src[src.index('\t"tutorial": {', src.index("const LESSONS")):]
        entry = entry[:entry.index("\n\t},")]
        assert '"steps": STEPS,' in entry
        assert '"title": "THE SCHOOL OF WAR",' in entry
        assert '"done": "tutorial",' in entry
        for key in ("refused", "outran", "overdue", "skipped"):
            assert f'"{key}":' in entry, key
        # the Danube's notes, byte for byte (the driven pins read them)
        assert '"The war refused that order — %s The school moves on."' in entry
        assert '"You skipped the last page — the school moves on."' in entry

    def test_every_runtime_read_is_the_bound_lesson_s(self):
        """`STEPS` is read at runtime only through `_steps`: the const stays
        the Danube's census table, the card renders whatever lesson it is
        bound to."""
        src = _read(OVERLAY)
        runtime = []
        for n, line in enumerate(src.split("\n"), start=1):
            code = line.split("#", 1)[0]
            # a READ of the table: an index, its size, an iteration (docstrings
            # that mention the const by name are prose, not reads)
            if re.search(r"\bSTEPS\s*\[|\bSTEPS\.size\(\)|\bin STEPS\b", code):
                runtime.append((n, line.strip()))
        assert runtime == [], runtime
        assert "var _steps: Array = STEPS" in src
        for name in ("_derive_step_for_turn", "_advance_one", "_maybe_catch_up",
                     "_effective_step", "_release_step", "_render"):
            assert "_steps" in _func(src, name), name

    def test_on_world_swap_binds_by_name_and_resets_every_latch(self):
        src = _read(OVERLAY)
        swap = _func(src, "on_world_swap")
        assert "LESSONS.get(name)" in swap
        assert "UiSettings.get_tutorial_done(name)" in swap
        assert "_bind_lesson(name, lesson)" in swap and "_reset_lesson_state()" in swap
        assert 'name != "tutorial"' not in swap
        reset = _func(src, "_reset_lesson_state")
        latches = re.findall(r"^var (_saw_\w+|_kienmayer_state|_last_infantry_pool|_pending_pulse|"
                             r"_last_rendered_turn|_last_sent|_released_note|_done|_minimized)\b",
                             src, re.M)
        assert len(latches) >= 9, latches
        for latch in latches:
            assert re.search(rf"^\t{latch} = ", reset, re.M), f"{latch} is not reset on arming (S14D-X20)"

    def test_the_notes_and_the_title_come_from_the_lesson(self):
        src = _read(OVERLAY)
        assert '_release_step(str(_notes.get("refused", "%s")) % _refusal_reason(response))' in _func(src, "observe")
        assert '_released_note = str(_notes.get("outran", ""))' in _func(src, "_maybe_catch_up")
        render = _func(src, "_render")
        assert "_title_label.text = _lesson_title" in render
        assert 'str(_notes.get("overdue", ""))' in render
        assert '_release_step(str(_notes.get("skipped", "")))' in _func(src, "_on_meta_clicked")
        assert "UiSettings.set_tutorial_done(true, _lesson_id)" in _func(src, "_conclude")
        # no war-voiced literal left outside the registry (S14D-X19)
        body_after_registry = src[src.index("var _steps: Array = STEPS"):]
        assert "The war refused that order" not in body_after_registry
        assert "The war outran the last page" not in body_after_registry

    def test_every_predicate_is_used_and_every_card_names_one(self):
        """S14D-X21: `_pred_turn_gte_13` was defined and no card used it."""
        src = _read(OVERLAY)
        defined = set(re.findall(r"^func (_pred_\w+)\(", src, re.M))
        used = set(re.findall(r'"advance":\s*"(_pred_\w+)"', src))
        assert used <= defined, used - defined
        unused = defined - used
        assert unused == set(), unused


class TestTheDoneLatchPerLesson:
    def test_the_settings_take_a_lesson_and_the_danube_keeps_its_key(self):
        src = _read(SCRIPTS / "ui_settings.gd")
        assert 'static func get_tutorial_done(lesson: String = "tutorial") -> bool:' in src
        assert 'static func set_tutorial_done(done: bool, lesson: String = "tutorial") -> void:' in src
        key = _func(src, "_tutorial_done_key")
        assert 'return "done" if lesson == "tutorial" else "done_" + lesson' in key

    def test_the_menu_clears_the_lesson_it_launches(self):
        launch = _func(_read(SCRIPTS / "main_menu.gd"), "_launch")
        assert "UiSettings.set_tutorial_done(false)" in launch               # the Danube, byte for byte
        assert 'elif action.begins_with("tutorial_"):' in launch
        assert "UiSettings.set_tutorial_done(false, action)" in launch

    def test_main_boots_the_named_lesson(self):
        boot = _func(_read(SCRIPTS / "main.gd"), "_on_tutorial_boot_requested")
        assert 'func _on_tutorial_boot_requested(scenario: String = "tutorial"):' in boot
        assert "api_client.new_game(_on_new_game_result, scenario)" in boot


class TestTheOnePredicate:
    def test_the_allowlist_is_derived_from_the_school_s_tuple(self):
        import backend.main as M
        assert set(M.SCENARIO_ALLOWLIST) == set(T.SCHOOL_SCENARIOS)
        assert M.SCENARIO_ALLOWLIST["tutorial"] == M.MAPS_DIR / "tutorial_1805.json"
        assert M.TUTORIAL_SCENARIO_PATH == M.SCENARIO_ALLOWLIST["tutorial"]
        for name in T.SCHOOL_SCENARIOS:
            assert (M.MAPS_DIR / T.SCENARIO_FILES[name]).is_file(), name
            assert name in T.STEPS_BY_SCENARIO, name

    def test_is_school_world_reads_the_tuple(self):
        world = WorldState(player_nation="France")
        assert T.is_school_world(world) is False
        world.scenario_name = "tutorial"
        assert T.is_school_world(world) is True and T.is_tutorial_world(world) is True
        world.scenario_name = "not_a_lesson"
        assert T.is_school_world(world) is False
        assert T.tutorial_step_for(world) is None

    def test_the_four_carve_outs_read_the_one_predicate(self):
        """S14D-X16: no carve-out keys on the literal any more — the autosave's
        `"skipped": "tutorial"` TAG (and its reader in main.py) is the one
        literal left, and it names a lesson, not the Danube."""
        from backend.game_logic import dotation, jealousy, vassal
        from backend import save_manager
        for module, fn in ((jealousy, "jealousy_dormant"), (dotation, "dotation_dormant"),
                           (vassal, "petitions_live"), (save_manager, "_autosave")):
            import inspect
            assert "is_school_world" in inspect.getsource(getattr(module, fn)), fn
        literal = re.compile(r'scenario_name[^\n]*==\s*"tutorial"')
        hits = []
        for path in (REPO / "backend").rglob("*.py"):
            if path.name == "tutorial_state.py" or "__pycache__" in path.parts:
                continue
            for n, line in enumerate(_read(path).split("\n"), start=1):
                if literal.search(line):
                    hits.append((path.name, n, line.strip()))
        assert hits == [], hits

    def test_every_school_scenario_is_dormant_and_autosave_skipped(self):
        from backend.game_logic import dotation, jealousy, vassal
        from backend import save_manager
        for name in T.SCHOOL_SCENARIOS:
            world = WorldState(player_nation="France")
            world.scenario_name = name
            assert jealousy.jealousy_dormant(world) is True, name
            assert dotation.dotation_dormant(world) is True, name
            assert vassal.petitions_live(world) is False, name
            result = save_manager._autosave(world)
            assert result.get("skipped") == "tutorial", (name, result)


class TestTheInstruments:
    def test_the_harness_reads_the_bound_lesson(self):
        gd = _read(REPO / "tools" / "tutorial_overlay_harness.gd")
        assert "_overlay._steps[index]" in gd and "_overlay.STEPS" not in gd

    def test_the_sweep_s_anchors_still_stand_in_the_overlay(self):
        src = _read(OVERLAY)
        for entry in json.loads(_read(REPO / "tools" / "_sweep_tutorial.json")):
            if entry.get("file", "").endswith("tutorial_overlay.gd"):
                assert entry["old"] in src, entry["id"]

    def test_the_stale_counts_are_gone(self):
        """S14D-X22: three places said "fifteen"/"twenty" predicates."""
        assert "fifteen GDScript functions" not in _read(REPO / "tools" / "playtest_driver.py")
        assert "twenty\n`advance` predicates" not in _read(REPO / "backend" / "game_logic" / "tutorial_state.py")
        fa17 = _read(REPO / "tests" / "test_fa_slice17_f_the_instrument_answers_2026_09_11.py")
        assert "assert len(rows) == 15" not in fa17
