"""FA slice 13 — "Shipping": the five position-10 blockers.

Rows: FA-29 (the build names a Python command that is not in the zip),
FA-43 (the zip ships CC-BY assets without their notice), FA-N84 (sixteen
licence files reach neither the .pck nor the zip), FA-N56 (the advertised
keys are dead in the state the client puts itself in), FA-57 (three client
surfaces warn the tutorial replaces an autosave the backend has not touched
since TUT-F2).

These are static claims about what SHIPS, so the pins are censuses over the
shipped files rather than behaviour tests — and each is two-directional,
because the failure mode every one of these rows shares is a substring pin
that stays green while the thing it names goes missing.
"""
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CLIENT = REPO / "godot-client" / "project-sovereign"
SCRIPTS = CLIENT / "scripts"
SCENES = CLIENT / "scenes"
DEPLOY = REPO / "deploy"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _tracked(pattern: str):
    """Files git actually tracks — an untracked stray must not red a pin,
    and a file deleted from the repo must."""
    try:
        out = subprocess.run(
            ["git", "ls-files", pattern], cwd=REPO, capture_output=True,
            text=True, timeout=60)
        if out.returncode == 0:
            return [line for line in out.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.SubprocessError):  # pragma: no cover
        pass
    return None


# ══════════════════════════════════════════════════════════════════════════
# FA-29 — the instruction depends on which build is running
# ══════════════════════════════════════════════════════════════════════════

class TestTheLaunchHintBranches:

    def test_the_helper_has_both_arms(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "static func launch_hint()" in utils
        assert 'OS.has_feature("editor")' in utils, (
            "one string for both builds is the defect; it must branch")
        assert "-m backend.main" in utils, "the editor arm names the command"
        assert "launch.bat" in utils, "the template arm names the zip's route"

    def test_the_template_arm_does_not_say_double_click_alone(self):
        """`launch.bat` reuses an already-answering server and then runs
        `start /wait InkAndIron.exe`, so a player who launched the exe
        directly must CLOSE it first or the batch waits behind the window it
        is telling them about."""
        utils = _read(SCRIPTS / "utils.gd")
        at = utils.index("static func launch_hint()")
        body = utils[at:utils.index("\nstatic func ", at + 10)]
        template_arm = body[body.index("return", body.index("return") + 1):]
        assert "close this window" in template_arm.lower(), template_arm

    def test_no_gd_file_states_the_dev_command_unconditionally(self):
        """The two-directional half: a seventh surface must not appear.

        `utils.gd` is the ONE place the string may live, because that is the
        only place it is guarded by a build check.
        """
        offenders = []
        for path in sorted(CLIENT.rglob("*.gd")):
            if path.name == "utils.gd":
                continue
            text = _read(path)
            for marker in ("-m backend.main", "python -m backend"):
                if marker in text:
                    offenders.append(f"{path.name}: {marker}")
        assert offenders == [], (
            "these name a Python command that is not in the zip a tester "
            f"unpacks: {offenders}")

    def test_both_surfaces_read_the_helper(self):
        assert "Utils.launch_hint()" in _read(SCRIPTS / "main_menu.gd")
        assert "Utils.launch_hint()" in _read(SCRIPTS / "main.gd")

    def test_the_version_line_reads_a_real_build_tag(self):
        utils = _read(SCRIPTS / "utils.gd")
        assert "static func build_label()" in utils
        assert "application/config/version" in utils
        project = _read(CLIENT / "project.godot")
        assert re.search(r'^config/version=".+"', project, re.M), (
            "build_label() reads a setting project.godot must author, or "
            "the version line renders empty")
        assert "Utils.build_label()" in _read(SCRIPTS / "main_menu.gd")


# ══════════════════════════════════════════════════════════════════════════
# FA-43 + FA-N84 — the licences ship with the game
# ══════════════════════════════════════════════════════════════════════════

LICENCE_PATTERNS = (
    "godot-client/project-sovereign/assets/**/*-OFL.txt",
    "godot-client/project-sovereign/assets/**/*license*",
    "godot-client/project-sovereign/assets/**/LICENSE",
)


def _build_commands() -> str:
    """build.bat with its `::` comment lines stripped.

    The mutation sweep caught two pins here reading my own COMMENTS:
    the block explaining WHY the notices must be copied names
    `THIRD_PARTY_LICENSES.md` and `*-OFL.txt`, so a census over the raw
    file stayed green with both copy commands deleted. A source pin
    proves a literal exists, never that it is the RIGHT literal.
    """
    build = _read(DEPLOY / "build.bat")
    return "\n".join(ln for ln in build.splitlines()
                     if not ln.strip().startswith("::"))


def _licence_census():
    """Every tracked licence file under assets/, derived at test time.

    Derived rather than listed so a seventeenth licence file reds this pin
    instead of shipping silently — the census IS the obligation.
    """
    found = set()
    for pattern in LICENCE_PATTERNS:
        rows = _tracked(pattern)
        if rows is None:
            pytest.skip("git unavailable")
        found.update(rows)
    return sorted(found)


class TestTheLicencesShip:

    def test_the_census_is_not_empty(self):
        census = _licence_census()
        assert len(census) >= 16, (
            f"the project ships CC-BY and OFL assets; census: {census}")

    def test_every_licence_file_is_carried_into_the_zip(self):
        """Two-directional: each tracked notice is named by build.bat,
        directly or by a wildcard that covers it.

        `test_ui_visual_foundation.py::test_ui1_font_ttf_and_ofl_present`
        checks these files exist IN THE REPO and is almost certainly why the
        project believed the obligation was discharged. It says nothing
        about the distribution. This is the distribution census.
        """
        build = _build_commands()
        missing = []
        for rel in _licence_census():
            name = Path(rel).name
            if name in build:
                continue
            # a wildcard that covers it, e.g. *-OFL.txt
            if name.endswith("-OFL.txt") and "*-OFL.txt" in build:
                continue
            # the extension-less pair, renamed on copy
            stem = Path(rel).parent.name
            if name == "LICENSE" and f"{stem}-LICENSE.txt" in build:
                continue
            missing.append(rel)
        assert missing == [], (
            f"these ship without their notice: {missing}")

    def test_the_extension_less_files_are_renamed_on_copy(self):
        """Godot does not scan extension-less files at all (they are absent
        from its own filesystem cache), and a bare `LICENSE` in a flat
        folder would collide besides."""
        build = _build_commands()
        assert "phosphor-LICENSE.txt" in build
        assert "game-icons-LICENSE.txt" in build

    def test_the_umbrella_file_ships_too(self):
        # It must be COPIED, not merely mentioned: the sweep caught the
        # first cut of this pin satisfied by the `[WARN] ... not copied`
        # line, which is a command and survives deleting the copy above it.
        copies = [ln for ln in _build_commands().splitlines()
                  if ln.strip().lower().startswith("copy /y")
                  and "THIRD_PARTY_LICENSES.md" in ln]
        assert copies, (
            "two surfaces in the product name this file; build.bat must "
            "actually put it in the zip")
        assert (REPO / "THIRD_PARTY_LICENSES.md").exists()

    def test_the_copies_warn_when_they_fail(self):
        """build.bat's own idiom — a silent copy failure is how a notice
        goes missing without anybody noticing."""
        build = _read(DEPLOY / "build.bat")
        at = build.index("Copying third-party licences")
        block = build[at:]
        copies = [ln for ln in block.splitlines()
                  if ln.strip().lower().startswith("copy /y")]
        assert len(copies) >= 5, copies
        warns = [ln for ln in block.splitlines()
                 if "errorlevel 1" in ln and "WARN" in ln]
        assert len(warns) >= len(copies), (
            f"{len(copies)} copies, {len(warns)} warnings")

    def test_no_xcopy_s_on_a_flat_folder(self):
        """`xcopy /s /i` succeeds silently on an empty match, so a future
        rename of the OFL files would leave the folder empty at errorlevel
        0 with no warning."""
        build = _read(DEPLOY / "build.bat")
        at = build.index("Copying third-party licences")
        commands = [ln for ln in build[at:].splitlines()
                    if ln.strip() and not ln.strip().startswith("::")]
        assert not any("xcopy" in ln for ln in commands), commands

    def test_both_credit_surfaces_point_at_the_shipped_copy(self):
        """A copied file that still says "in the source tree" is a second
        dangling pointer."""
        readme = _read(DEPLOY / "README_TESTER.txt")
        assert "THIRD_PARTY_LICENSES.md" in readme
        assert "in the source tree" not in readme
        settings = _read(SCRIPTS / "settings_panel.gd")
        assert "THIRD_PARTY_LICENSES.md" in settings
        assert "licenses" in settings


# ══════════════════════════════════════════════════════════════════════════
# FA-N56 — the advertised keys work in the state the client puts itself in
# ══════════════════════════════════════════════════════════════════════════

def _focus_safe_source() -> str:
    """The whole focus-safe route: the gui_input handler, the SCREEN
    table it dispatches through, and the GAME table this slice added
    beside it."""
    src = _read(SCRIPTS / "main.gd")
    at0 = src.index("const _SCREEN_HOTKEYS := {")
    screens = src[at0:src.index("}", at0) + 1]
    at = src.index("func _on_command_input_gui_input")
    handler = src[at:src.index("\nfunc ", at + 10)]
    at2 = src.index("func _alt_game_key")
    table = src[at2:src.index("\nfunc ", at2 + 10)]
    return screens + handler + table


ADVERTISED = {
    "T": "KEY_T", "G": "KEY_G", "D": "KEY_D", "R": "KEY_R",
    "L": "KEY_L", "N": "KEY_N", "E": "KEY_E", "Tab": "KEY_TAB",
    "M": "KEY_M", "Home": "KEY_HOME",
}


class TestTheAdvertisedKeysAreReachableWhileTyping:

    def test_every_advertised_key_survives_terminal_focus(self):
        """The two-directional census. The client re-grabs the command line
        at 35 sites, so "while typing" is the game's dominant state — and
        before this slice E, Tab, M, +, - and Home were all dead there while
        the README and the boot help taught them."""
        focus_safe = _focus_safe_source()
        dead = [label for label, code in ADVERTISED.items()
                if code not in focus_safe]
        assert dead == [], f"advertised but dead while typing: {dead}"
        assert "KEY_EQUAL" in focus_safe and "KEY_MINUS" in focus_safe

    def test_the_readme_advertises_the_focus_safe_form(self):
        """Even the six keys PC15-18 fixed were advertised in their dead
        form: the README named "Alt" zero times."""
        readme = _read(DEPLOY / "README_TESTER.txt")
        assert readme.count("Alt") >= 8, readme.count("Alt")
        for key in ("T", "G", "D", "R", "L", "N", "E"):
            assert f"{key} / Alt+{key}" in readme, key
        assert "Alt+M" in readme
        assert "Alt+Home" in readme

    def test_the_readme_is_honest_about_the_two_press_escape(self):
        """`Esc` while typing releases focus; the pause menu opens on the
        SECOND press, through `_unhandled_input`."""
        readme = _read(DEPLOY / "README_TESTER.txt")
        assert "second" in readme[readme.index("Esc "):
                                  readme.index("THE MAP")].lower()

    def test_the_boot_help_teaches_the_form_that_works(self):
        """`set_input_enabled(true)` is called four lines after the boot
        help advertises M, +/- and Home — the client teaches six keys and
        then, in the next statement, enters the state that killed four."""
        src = _read(SCRIPTS / "main.gd")
        at = src.index("Commands:")
        help_block = src[at:src.index("set_input_enabled(true)", at)]
        assert "Alt+M" in help_block, help_block
        assert "not typing" in help_block

    def test_end_turn_mirrors_both_gates_its_bare_twin_obeys(self):
        """Bare E sits BELOW `_unhandled_input`'s `if _is_screen_open():
        return`, while the Alt SCREEN keys check only the modal gate. An Alt
        arm that copied the screen-key gate alone would let Alt+E end the
        turn with a full-screen ledger open, where bare E refuses — and
        toggling a screen does not move focus off the command line, so that
        state is ordinary."""
        table = _focus_safe_source()
        at = table.index("KEY_E:")
        arm = table[at:table.index("KEY_TAB:")]
        assert "_is_modal_dialog_open()" in arm, arm
        assert "_is_screen_open()" in arm, arm

    def test_the_map_keys_are_called_not_re_emitted(self):
        """Re-emitting the key event lands on the SAME `text_focused` guard
        in `map_renderer_base._unhandled_input`, so the focused route must
        call through a public door."""
        table = _focus_safe_source()
        assert "map_area.cycle_map_fill_mode()" in table
        assert "map_area.recenter_view()" in table
        assert "map_area.zoom_step(" in table
        base = _read(SCENES / "map_renderer_base.gd")
        assert "func recenter_view()" in base
        assert "func zoom_step(" in base

    def test_cycling_the_map_says_which_view_you_landed_on(self):
        """`cycle_map_fill_mode() -> String` returns the new mode and its
        only other caller discards it."""
        table = _focus_safe_source()
        at = table.index("KEY_M:")
        arm = table[at:table.index("KEY_HOME:")]
        assert "add_output" in arm, arm
        assert "mode" in arm

    def test_the_alt_arm_consumes_the_event_either_way(self):
        """Alt+E must never type an "e" into the command line, even when the
        gate refuses the action."""
        handler = _read(SCRIPTS / "main.gd")
        at = handler.index("func _on_command_input_gui_input")
        body = handler[at:handler.index("\nfunc ", at + 10)]
        # The sweep caught the first cut of this pin passing over a
        # DISABLED arm (`elif false and _alt_game_key(...)`) — it read
        # the mention, not the route. The dispatch must be live.
        assert "elif event.alt_pressed and _alt_game_key(event.keycode):" in body, body
        at2 = body.index("_alt_game_key")
        arm = body[at2:]
        assert "command_input.accept_event()" in arm

    def test_the_bare_route_is_untouched(self):
        """The unfocused path keeps working — this slice adds a road, it
        does not move one."""
        src = _read(SCRIPTS / "main.gd")
        at = src.index("func _unhandled_input")
        body = src[at:at + 6000]
        assert "KEY_E" in body and "KEY_TAB" in body
        base = _read(SCENES / "map_renderer_base.gd")
        assert "KEY_HOME" in base and "KEY_M" in base


# ══════════════════════════════════════════════════════════════════════════
# FA-57 — the School of War keeps the campaign autosave
# ══════════════════════════════════════════════════════════════════════════

class TestTheSchoolKeepsTheAutosave:

    def test_no_client_surface_claims_the_tutorial_replaces_it(self):
        menu = _read(SCRIPTS / "main_menu.gd")
        at = menu.index("Enter the School of War?")
        line = menu[at:menu.index("\n", at)]
        assert "replaced" not in line, line
        main = _read(SCRIPTS / "main.gd")
        at2 = main.index("Convening the School of War")
        line2 = main[at2:main.index("\n", at2)]
        assert "replaced" not in line2, line2
        boot = _read(SCRIPTS / "menu_boot.gd")
        at3 = boot.index("School of War / Danube Lesson")
        entry = boot[at3:boot.index("FA-57", at3)]
        assert "and the autosave" not in entry, entry
        assert "NOT the autosave" in boot, (
            "the header comment is the third surface, and it must say "
            "which way round it is")

    def test_the_promise_to_restore_is_conditional(self):
        """The confirm row also shows in the `came_from_game and no saves`
        arm, where there is nothing on disk at all — `autosave()` is written
        from exactly two places, and a session that hydrated the boot world
        and never ended a turn has no file. An unconditional "Continue
        restores it" would be the same class of lie the row exists to
        remove."""
        menu = _read(SCRIPTS / "main_menu.gd")
        at = menu.index("Enter the School of War?")
        block = menu[at:at + 500]
        assert "Continue restores it" in block
        assert "_saves.size() > 0" in block, (
            "the restore promise must be guarded by there being a save")

    def test_the_begin_confirm_is_left_alone(self):
        """`Begin anew` DOES refresh the autosave — `/new_game` without a
        scenario writes it. Only the tutorial arm was lying."""
        menu = _read(SCRIPTS / "main_menu.gd")
        assert menu.count(
            "Begin anew? The autosave of your running campaign is "
            "replaced.") == 2

    def test_the_backend_still_says_untouched(self):
        """The other half of the contradiction, pinned so a future change to
        the backend reds the client copy rather than silently re-opening
        it."""
        sm = _read(REPO / "backend" / "save_manager.py")
        assert '"skipped": "tutorial"' in sm
        main_py = _read(REPO / "backend" / "main.py")
        assert "Your campaign autosave is untouched." in main_py
