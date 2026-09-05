# REPRO J1 - slice 13, the position-10 shipping blockers

Repo read-only at master `a1ed5c9d`. No repo file touched. Probes under
`scratchpad/repro/j1/`. All five rows are STATIC claims; every one was checked by
reading the shipped files and by running the census each row describes.

## Summary

| Row | Verdict | Measured mechanism |
|---|---|---|
| FA-29 | REPRODUCED (and WIDER) | The three dev strings are shipped verbatim; `has_feature`/`is_debug_build`/`is_editor_hint` return **ZERO hits across EVERY tracked file in the whole Godot project** (not just the five scripts the row grepped), so no arm can exist. **The row's own `fix_shape` reds the pin it says it protects** - moving the string into `Utils.launch_hint()` removes `-m backend.main` from `main_menu.gd`, and `test_main_menu_and_ux_pass.py:129` reads that file specifically. |
| FA-43 | REPRODUCED, every cited line CURRENT | `build.bat` does exactly three `copy` at 52/58/61; `all_datas` is mutated at exactly 125 and 139 (three map JSONs); regex `LICEN[SC]E\|OFL\|THIRD_PARTY` matches **0** times in either file. The two credit surfaces (settings_panel.gd:312, README_TESTER.txt:247) name a file that is not in the distribution. |
| FA-N84 | REPRODUCED, mechanism proven at engine level | Census L = **exactly 16** tracked licence files beside **26** tracked `.ttf`. Godot's OWN editor filesystem cache types every one of the 13 OFL files and `kenney-license.txt` as `TextFile/TextFile`, while `.ttf` is `FontFile/FontFile` and `.json` is `JSON/JSON`. `export_filter="all_resources"` skips TextFile; `include_filter=""`, so nothing carries them. The two extension-less `LICENSE` files are not in the cache **at all**. FA-43's fix does NOT discharge it (confirmed: `THIRD_PARTY_LICENSES.md` only *points at* `assets/fonts/`). |
| FA-N56 | REPRODUCED and WIDER | Focus-safe keys are exactly `F1`, `Alt+{L,T,G,D,R,N}`, `UP`, `DOWN`, `ESCAPE`. **E, Tab, M, +, -, Home are all dead while typing**, and the client re-grabs focus at 35 sites. **The README mentions "Alt" ZERO times**, so even the six keys PC15-18 fixed are advertised in a dead form. `cycle_map_fill_mode` has exactly ONE caller, inside the guard. NARROWING: M is not unreachable - a left-click on the map calls `gui_release_focus()` - but nothing tells the player that, and there is no button/menu route. Also `Esc - Pause menu` needs **two** presses while typing. |
| FA-57 | REPRODUCED as filed (VERIFIED stands) | Three client surfaces say the tutorial replaces the campaign autosave; the backend has not since TUT-F2 and says so in the same terminal. NARROWING on the row's own **fix copy**: "Continue restores it" is a NEW lie in the `came_from_game and _saves.is_empty()` arm. |

---

## Per row

### FA-29 - the shipped build names a Python command that is not in the zip

**Probes:** `probe_2_hotkey_census.py` section F; direct reads.

**Evidence (quoted source, current line numbers):**

```
scripts/main_menu.gd:346    version.text = "Ink & Iron - development build"
scripts/main_menu.gd:527        _status_label.text = "The war office does not answer - start the backend:  .venv\\Scripts\\python.exe -m backend.main"
scripts/main.gd:754         add_output("[color=#" + Utils.COLOR_INFO + "]Start the Python server: python -m backend.main[/color]")
```

Census (probe 2 section F), run as `git grep -n -E "has_feature|is_debug_build|is_editor_hint" -- godot-client`:

```
(ZERO hits across every tracked file in the Godot project)
```

That is **wider than the row's claim** - the row grepped five scripts; I grepped
every tracked `.gd` and `.tscn` in the project. There is no branch anywhere.

README contradiction, verbatim at `deploy/README_TESTER.txt:207-209` (row's line
numbers EXACT):

```
207  "Game window opens but can't connect"
208    - The main menu names the launch command when the server is
209      down; use launch.bat rather than starting the exe alone
```

The reachability is real: `deploy/launch.bat:68-73` polls `/test` for ~30 s and
`exit /b 1`s on failure, so the *only* way a stranger sees the menu's dead string
is the exact case README:208 anticipates - starting `InkAndIron.exe` alone - or a
server that dies mid-session.

**(a) True seam BY SYMBOL:**
- `godot-client/project-sovereign/scripts/main_menu.gd::_apply_backend_state` (the
  `else` arm, line 527) - the menu status label.
- `godot-client/project-sovereign/scripts/main.gd` - the `else` arm of the
  connection-test callback (line 753-755); it has no enclosing named function I
  could anchor on other than the `_on_connection_test` body, so navigate by the
  literal `"Cannot reach headquarters!"`.
- `godot-client/project-sovereign/scripts/main_menu.gd` version label construction
  (line 340-350, node `"VersionLine"`).
- Proposed new home: `scripts/utils.gd` (`extends Node` / `class_name Utils`, so a
  `static func launch_hint()` is legal; it already hosts
  `backend_url()` / `backend_origin_label()`).

**(b) What the row's own filed fix would BREAK - CONFIRMED, and it is the pin the
row claims to protect:**

```
tests/test_main_menu_and_ux_pass.py:125-130
    def test_menu_buttons_are_honest_about_the_backend(self):
        gd = _read(SCRIPTS / "main_menu.gd")
        # polls /test, states the reason, and names the real launch command
        assert '"/test"' in gd or "/test" in gd
        assert "-m backend.main" in gd            <-- line 129
        assert "disabled = not" in gd
```

`SCRIPTS = GODOT_ROOT / "scripts"` and `_read` is a plain file read. The row's fix
says *"both main_menu.gd:527 and main.gd:745 read it [Utils.launch_hint()]"* AND
*"Keep the dev string so test_main_menu_and_ux_pass.py:129 holds"*. Those two
sentences are mutually exclusive: if `main_menu.gd` reads the helper, the literal
`-m backend.main` leaves `main_menu.gd` and line 129 goes red. This is a sixth
member of the "fix_shape contradicts its own summary" family.

Second, smaller break: the row wants the version line to "read a build tag".
`project.godot` has **no** `config/version` key today (verified, `[application]`
holds only `config/name`, `run/main_scene`, `config/features`, `boot_splash/*`,
`config/icon`), so `ProjectSettings.get_setting("application/config/version")`
returns null and the label would render empty. The key must be added.
`tests/test_main_menu_and_ux_pass.py::TestProjectIdentity` pins only
`run/main_scene`, `config/name`, `config/icon`, `boot_splash/*` - adding a version
key breaks nothing.

**(c) Minimal correct fix.**

`scripts/utils.gd`, new static, both arms literal:

```
static func launch_hint() -> String:
    if OS.has_feature("editor"):
        return ".venv\\Scripts\\python.exe -m backend.main"
    return "Close this window and start the game with launch.bat (it starts the server first and must stay open)."
```

- editor arm MUST contain the substring `-m backend.main` (that is the string the
  developer actually types, and it is what a re-pointed pin will assert).
- template arm must NOT say "double-click launch.bat" alone: `launch.bat:52-57`
  reuses an already-answering server and `:100` runs `start /wait InkAndIron.exe`,
  so the honest instruction is *close this window first*, which is what I wrote.

Call sites: `main_menu.gd:527` (`... does not answer - " + Utils.launch_hint()`)
and `main.gd:754` (`add_output(... + Utils.launch_hint() + ...)`). Version line:
`"Ink & Iron - " + str(ProjectSettings.get_setting("application/config/version", "development build"))`.

Then **re-point the pin two-directionally** rather than trying to keep it:

```
def test_menu_buttons_are_honest_about_the_backend(self):
    gd = _read(SCRIPTS / "main_menu.gd")
    utils = _read(SCRIPTS / "utils.gd")
    assert "/test" in gd
    assert "Utils.launch_hint()" in gd
    assert "disabled = not" in gd
    assert "-m backend.main" in utils          # the editor arm survives
    assert "launch.bat" in utils               # the template arm exists
    assert 'has_feature("editor")' in utils    # it BRANCHES
```

**(d) Existing tests that pin today's behaviour and would flip:**

| test | assertion |
|---|---|
| `tests/test_main_menu_and_ux_pass.py::TestMainMenuScene::test_menu_buttons_are_honest_about_the_backend` (line 129) | `assert "-m backend.main" in gd` where `gd = _read(SCRIPTS / "main_menu.gd")` - **reds** the moment the string moves to `utils.gd` |

Nothing pins `main.gd:754` or the version label; I found no test reading
`"development build"` or `"Start the Python server"` anywhere under `tests/`.

---

### FA-43 - the zip ships CC-BY assets without THIRD_PARTY_LICENSES.md

**Probe:** `probe_3_licenses.py` sections B, F.

**Evidence:**

```
   build.bat copy statements:
     52: copy /y "deploy\dist_template\config.txt" "deploy\dist\ink_iron_server\config.txt" >nul
     58: copy /y "deploy\launch.bat" "deploy\dist\ink_iron_server\launch.bat" >nul
     61: copy /y "deploy\README_TESTER.txt" "deploy\dist\ink_iron_server\README_TESTER.txt" >nul
   build.bat license-regex matches: 0
   ink_iron.spec license-regex matches: 0
   spec all_datas.append lines:
     125: all_datas = uvicorn_datas + fastapi_datas + starlette_datas
     139: all_datas.append((os.path.join(_MAPS_SRC, _map_file), _MAPS_DST))
     146: datas=all_datas,
```

Exactly three copies, exactly two `all_datas` mutations, the second being the
three map JSONs at `deploy/ink_iron.spec:134-139`. Every cited line number in the
row is CURRENT - the only such row in this family.

The two surfaces that name the missing file:

```
   settings_panel.gd:312 + "public domain (Wikimedia Commons / IMSLP) - Full terms: THIRD_PARTY_LICENSES.md.")
   README_TESTER.txt:247 licenses - see THIRD_PARTY_LICENSES.md in the source tree.
   THIRD_PARTY_LICENSES.md size: 16254
```

The obligation is LIVE, not theoretical: the CC-BY assets actually ship. Verified
by asset type - `assets/ui/icons/game-icons/*.svg` (75 tracked icon SVGs, typed
`CompressedTexture2D/CompressedTexture2D` in the filesystem cache) and
`assets/audio/battle/musket_battle_volley.mp3` (163 tracked audio files, all with
committed `.import` sidecars) are RESOURCES, so they ride the `.pck` under
`all_resources` while their notice does not.

**(a) True seam BY SYMBOL:** `deploy/build.bat`, the copy block at lines 49-61
(it has no function structure - navigate by the literal
`copy /y "deploy\README_TESTER.txt"`). Second surface:
`deploy/README_TESTER.txt:247` (`in the source tree`).

**(b) What the row's fix would BREAK:** nothing in the suite - but it is
**INCOMPLETE by its own evidence**. `THIRD_PARTY_LICENSES.md:28-29` reads:

```
Free to embed and ship. Obligation: bundle each family's `OFL.txt` (already saved beside
the `.ttf` in `assets/fonts/`).
```

So the file FA-43 copies is a document that discharges its own obligation by
*pointing at a directory that is not in the zip either*. Copying it alone leaves
the OFL obligation open - which is exactly FA-N84's claim, and I confirm it: the
row is right that FA-43 does not discharge FA-N84.

**(c) Minimal correct fix:** land FA-43 and FA-N84 as ONE edit to the same block
(see FA-N84 below). Also fix the README's own sentence
(`:247 in the source tree` -> `in this folder`) or the copied file becomes a
second dangling pointer.

**(d) Existing tests that would flip:** none. The nearest neighbours are
`tests/test_prebuild_fixes_2026_08_14.py::TestResourceHygiene::test_build_bat_demands_fresh_export_and_mock_smoke`
(`assert "FRESH export" in text` / `assert "mock mode" in text`) - substring pins
on `build.bat` that adding copy lines cannot disturb - and
`tests/test_main_menu_and_ux_pass.py::TestMainMenuScene::test_paintings_are_valid_jpegs_and_credited`
(line 95-100, `licenses = _read(REPO_ROOT / "THIRD_PARTY_LICENSES.md")`), which
pins the file's CONTENT in the repo, not its shipping.

---

### FA-N84 - sixteen licence files reach neither the .pck nor the zip

**Probes:** `probe_3_licenses.py` (A, C, D), `probe_1_pck.py`.

**Census L - exactly 16, matching the row to the file:**

```
   godot-client/project-sovereign/assets/fonts/AlegreyaSans-OFL.txt
   ... (13 *-OFL.txt) ...
   godot-client/project-sovereign/assets/ui/bars/kenney-license.txt
   godot-client/project-sovereign/assets/ui/icons/game-icons/LICENSE
   godot-client/project-sovereign/assets/ui/icons/phosphor/LICENSE
   COUNT: 16
   tracked .ttf: 26
```

**Export preset (current):**

```
   export_filter = "all_resources"
   include_filter = ""
   exclude_filter = ""
```

**MECHANISM - proven from Godot's own editor filesystem cache** (this is what the
row's truncated text was reaching for, and I confirm it at
`godot-client/project-sovereign/.godot/editor/filesystem_cache10`):

```
   AlegreyaSans-OFL.txt  ->  TextFile/TextFile
   Cinzel-OFL.txt        ->  TextFile/TextFile
   Cinzel[wght].ttf      ->  FontFile/FontFile
   europe.json           ->  JSON/JSON
   kenney-license.txt    ->  TextFile/TextFile
   ... (all 13 OFL files TextFile/TextFile) ...
```

Godot's `all_resources` mode walks the EditorFileSystem and **skips entries typed
`TextFile`/`OtherFile`**; non-resource files are added only by `include_filter`
(the "Filters to export non-resource files/folders" field), which is empty. The
`.ttf` (`FontFile`) and the `.json` (`JSON`) ARE resources and do ride - the same
cache proves the discrimination, so this is not a guess about the engine, it is
Godot's own classification of these exact files.

The two extension-less `LICENSE` files do not appear in the cache **at all**
(`grep -a "LICENSE" filesystem_cache*` returns nothing) - Godot does not scan
extension-less files, so they are excluded a second, independent way. **Any fix
that relies on `include_filter` must therefore rename them on copy** (e.g.
`phosphor-LICENSE.txt`), exactly as the row's fix shape says.

Confidence on the `all_resources` reading: **high**, resting on (i) the
`TextFile/TextFile` vs `FontFile`/`JSON` split above and (ii) `deploy/build.bat:71-73`,
which itself warns *"verify europe_1805.json is inside the new .pck"* - the
project already treats non-`.gd`/`.tscn` payload as at-risk. Corroboration but
NOT proof: the shipped March-2026 `InkAndIron.pck` (GDPC, 114 entries) holds only
`.remap/.gdc/.scn/.ctex/.svg/.import` plus Godot's own `.cfg/.bin`, ZERO `.txt` -
however `git ls-tree` at that build's commit `c9099e65` shows **zero** `.txt`,
`.json` or `.md` under `res://` at the time, so the pck cannot settle it alone and
I report it as corroboration only.

**(a) True seam BY SYMBOL:** `deploy/build.bat`, the same copy block as FA-43
(navigate by `copy /y "deploy\README_TESTER.txt"`). Optional second seam:
`godot-client/project-sovereign/export_presets.cfg::include_filter`.

**(b) What the row's fix would BREAK:** nothing in the suite. Two real hazards in
its construction, both worth fixing while landing:
1. `xcopy /y /i /s "...assets\fonts\*-OFL.txt" "...\licenses\fonts\"` uses `/s`,
   which is pointless (the OFL files are all at one level) and, combined with
   `/i`, silently succeeds on an empty match - so a future rename of the OFL files
   would leave the folder empty with `errorlevel 0` and no warning. Use `copy /y`
   per-family or an `xcopy` without `/s` plus an `if errorlevel 1 echo [WARN]`
   arm, matching build.bat's existing style at :53-55.
2. Its alternative (setting `include_filter="*.txt"` in the preset) would sweep
   the WHOLE project's `.txt` into the `.pck` and is worse; keep the copy-to-zip
   route the row chose.

**(c) Minimal correct fix:** one block appended after `build.bat:61`:
- `mkdir` a `licenses\` folder in the dist,
- copy the 13 `assets\fonts\*-OFL.txt` into `licenses\fonts\`,
- copy `assets\ui\bars\kenney-license.txt` into `licenses\`,
- copy the two extension-less `LICENSE` files renamed to
  `licenses\phosphor-LICENSE.txt` / `licenses\game-icons-LICENSE.txt`,
- copy `THIRD_PARTY_LICENSES.md` to the dist root (FA-43),
- each with the `if errorlevel 1 echo [WARN]` arm build.bat already uses,
- and amend `README_TESTER.txt:247` `in the source tree` -> `in this folder (and
  licenses\)` and `settings_panel.gd:312` to say the same.

**Test (the row's own two-directional shape, which I endorse):** derive L from
`git ls-files` at test time, assert `len(L) > 0`, and assert every basename in L
appears in `build.bat` (directly or via the wildcard that covers it) - so adding a
seventeenth licence file to `assets/` reds the pin. A substring check on
`"OFL"` alone would pass forever.

**(d) Existing tests that would flip:** none. Adjacent, and worth knowing it does
NOT cover this: `tests/test_ui_visual_foundation.py::test_ui1_font_ttf_and_ofl_present`
line 152, `assert (FONTS_DIR / ofl).exists(), f"missing license {ofl} (OFL required)"`
- a **repo-presence** pin only. It is the reason the project believes the OFL
obligation is handled; it says nothing about the distribution.

---

### FA-N56 - the advertised keys are dead in the state the client puts itself in

**Probe:** `probe_2_hotkey_census.py` (the two-directional census the row asks for).

**What survives terminal focus** - `main.gd::_on_command_input_gui_input`
(line 898, body 972 chars):

```
keys handled under focus: ['KEY_DOWN', 'KEY_ESCAPE', 'KEY_F1', 'KEY_UP']
   + Alt+ table _SCREEN_HOTKEYS: ['KEY_D', 'KEY_G', 'KEY_L', 'KEY_N', 'KEY_R', 'KEY_T']
```

**The census (probe 2 section C):**

```
  F1    KEY_F1       ALIVE bare while typing
  T     KEY_T        ALIVE only as Alt+T (README never says 'Alt')
  G     KEY_G        ALIVE only as Alt+G (README never says 'Alt')
  D     KEY_D        ALIVE only as Alt+D (README never says 'Alt')
  R     KEY_R        ALIVE only as Alt+R (README never says 'Alt')
  L     KEY_L        ALIVE only as Alt+L (README never says 'Alt')
  N     KEY_N        ALIVE only as Alt+N (README never says 'Alt')
  E     KEY_E        DEAD while typing -> _unhandled_input (needs UNFOCUSED input)
  Tab   KEY_TAB      DEAD while typing -> _unhandled_input (needs UNFOCUSED input)
  Esc   KEY_ESCAPE   ALIVE bare while typing
  M     KEY_M        DEAD while typing -> map_renderer_base._unhandled_input (returns on LineEdit focus)
  +     KEY_EQUAL    DEAD while typing -> map_renderer_base._unhandled_input (returns on LineEdit focus)
  -     KEY_MINUS    DEAD while typing -> map_renderer_base._unhandled_input (returns on LineEdit focus)
  Home  KEY_HOME     DEAD while typing -> map_renderer_base._unhandled_input (returns on LineEdit focus)

README mentions 'Alt' : 0
command_input.grab_focus() occurrences in main.gd: 35
```

**REPRODUCED and WIDER than filed in two ways:**

1. **The README - the surface a stranger reads - never names the Alt form at
   all.** So even the six keys PC15-18 *did* fix are advertised in their dead form
   (`README_TESTER.txt:79-88` lists bare `T G D R L N`). PC15-18 put the honest
   form only in `top_bar.gd:130-131` tooltips (`key + " - or Alt+" + key + " while
   typing"`). The row's framing "left the rest behind" understates it: it left the
   *advertising* behind for all of them.
2. **`Esc - Pause menu` (README:88) is a two-press while typing.** The gui_input
   arm at `main.gd:917-919` does `command_input.release_focus()` only; the pause
   menu opens on the SECOND Esc via `_unhandled_input` (`main.gd:999-1004`).

**NARROWING (against the row):** the row says map coloring "has no other route in
the entire client". The *binding* claim is exactly true -

```
godot-client/project-sovereign/scenes/map_renderer_base.gd:1076:func cycle_map_fill_mode() -> String:
godot-client/project-sovereign/scenes/map_renderer_base.gd:2214:                              cycle_map_fill_mode()
```

- definition plus one call site, inside the guard. But M is **not unreachable**:
`map_renderer_base.gd:2007` calls `get_viewport().gui_release_focus()` on any
LEFT or MIDDLE click on the map, so *click the map, then press M* works. Nothing
in the client or the README says so, and the next command re-grabs focus. Mouse
wheel zoom and province clicks are unaffected (they live in `_input`, not
`_unhandled_input`). Arrow-key panning is also focus-guarded
(`_handle_pan_key_event:2052-2057`) but is not advertised, so it is not part of
this row.

**Row detail corrections:** `grep -c 'command_input.grab_focus()'` is **35**, not
the filed 37. Line numbers: `set_input_enabled` is at **4054** (filed 3932),
`_is_hotkey_blocked` at **5482** (filed 5342), E/Tab at **1072/1077** (filed
1063/1068), boot help at **733-741** (filed 726-737). `map_renderer_base.gd`
2198-2214 and 1076-1082, `top_bar.gd` 121-131 and `README_TESTER.txt` 78-94 are
all EXACT.

**(a) True seam BY SYMBOL:** `main.gd::_on_command_input_gui_input` (the single
decision point), plus - for the map keys - a public forwarding API on
`scenes/map_renderer_base.gd` (today only `cycle_map_fill_mode` is public;
`_center_view_on_map` (1927) and `_zoom_at_point` (2215) are underscore-private).
`main.gd` reaches the map as `@onready var map_area = $MapArea` (line 189).
Second seam, copy: `deploy/README_TESTER.txt` HOTKEYS + THE MAP blocks and
`main.gd`'s boot-help lines 739-741.

**(b) What the row's filed fix would BREAK - three things it does not mention:**

1. **Alt+E would end the turn with a full-screen ledger open, where bare E
   refuses.** The bare arm sits BELOW `if _is_screen_open(): return`
   (`main.gd:1068-1069`); the Alt arm in `_on_command_input_gui_input` checks only
   `_is_modal_dialog_open()`. Toggling a screen does not move focus off the
   command line, so this state is ordinary. The fix must mirror BOTH gates, or
   consciously decide to diverge and say so.
2. **Forwarding a key event to the map cannot work** - re-emitting hits the same
   `text_focused` guard at `map_renderer_base.gd:2199-2202`. The forward must be a
   direct method call, which means adding public wrappers (or calling
   underscore-private methods across scripts, against project convention).
3. **The README rewrite reds three assertions** (see (d)). The row's own Test
   section proposes parsing the README's HOTKEYS block, which is fine, but the
   existing exact-line pins must be re-pointed in the same commit.

Minor: the row proposes `Alt+\`` for the terminal toggle. `KEY_QUOTELEFT` is free
in both handlers - verified, no other consumer.

**(c) Minimal correct fix:**
- Extend `_on_command_input_gui_input` with one `elif event.alt_pressed:` block
  holding a second dispatch table `_ALT_ACTIONS := {KEY_E: ..., KEY_QUOTELEFT: ...,
  KEY_M: ..., KEY_HOME: ..., KEY_EQUAL: ..., KEY_MINUS: ...}`, each arm calling the
  SAME predicate its unfocused twin calls (`_is_modal_dialog_open()` **and**
  `_is_screen_open()` for E/Tab; nothing extra for the map keys, which the
  unfocused path also allows only when no screen is open).
- Add `map_area` public wrappers: `recenter_view()`, `zoom_step(f: float)` -
  `cycle_map_fill_mode()` is already public. Use its **discarded String return**
  (see cross-row) to print the new mode into the terminal, so pressing it gives
  feedback.
- Rewrite the README HOTKEYS block as `T / Alt+T - Strategic Ledger ...` and the
  THE MAP block as `... Alt+M to cycle map coloring (bare keys work whenever you
  are not typing)`, and the same in `main.gd`'s boot help at 739-741.
- Pin two-directionally: parse every key advertised in the README's two blocks and
  in main.gd's boot help, and assert each appears in the focus-safe arm.

**(d) Existing tests that pin today's behaviour and would flip:**

| test | assertion |
|---|---|
| `tests/test_prebuild_fixes_2026_08_14.py::TestReadmeTesterCurrent::test_hotkeys_match_main_gd` (251-253) | `assert "R   - Morning Dispatch" in text` / `assert "D   - Diplomatic Ledger" in text` / `assert "N   - Le Moniteur" in text` - **all three red** on any README HOTKEYS rewrite that changes column spacing or prefixes `Alt+` |
| `tests/test_pc15_16_18_visual_fixes_2026_08_15.py::TestPC1518HotkeysReachableWhileTyping::test_screen_hotkey_table_is_complete` (239-248) | `assert re.search(key + r':\s*"' + screen + '"', table)` over `_SCREEN_HOTKEYS` - survives an addition, reds if the table is restructured into a merged `_ALT_ACTIONS` |
| `tests/test_pc15_16_18_visual_fixes_2026_08_15.py::...::test_alt_route_exists_and_keeps_the_modal_gate` (250-260) | `handler = src[at:at + 2500]` then `assert "alt_pressed" in handler` / `"_SCREEN_HOTKEYS"` / `"_is_modal_dialog_open()"` - survives, but see cross-row: the scrape overshoots the 972-char handler by 1528 chars |
| `tests/test_pc15_16_18_visual_fixes_2026_08_15.py::...::test_bare_keys_still_work_unfocused` (262-269) | `assert "KEY_N" in handler` / `assert 'toggle_screen("gazette")' in handler` over `_unhandled_input[:5000]` - survives |
| `tests/test_pc15_16_18_visual_fixes_2026_08_15.py::...::test_buttons_advertise_the_focus_safe_form` (271-274) | `assert "Alt+" in src` over `top_bar.gd` - survives |

---

### FA-57 - the School of War warns it replaces an autosave the backend never touches

**Probe:** direct reads; digest read.

**The three client surfaces (current line numbers):**

```
scripts/main_menu.gd:444      _confirm_label.text = "Enter the School of War? The autosave of your running campaign is replaced."
scripts/main.gd:6378          add_output("[color=#" + Utils.COLOR_INFO + "]Convening the School of War. Current autosave will be replaced.[/color]")
scripts/menu_boot.gd:19-21    #   "tutorial"  - POST /new_game {"scenario": "tutorial"} (POSITION 7: the
                              #                 School of War / Danube Lesson; replaces the running world
                              #                 and the autosave exactly like new_game)
```

**The backend, contradicting all three in the same terminal:**

```
backend/main.py:4404-4410
        autosave_result = autosave(new_world)
        autosave_ok = bool(autosave_result.get("success", False))
        message = "New campaign started."
        if autosave_result.get("skipped") == "tutorial":
            # The lesson never writes the campaign's autosave slot - shown,
            # not silent, so nobody reads "refreshed" over a skip.
            message += " Your campaign autosave is untouched."

backend/save_manager.py:266-272 (in def autosave)
    if str(getattr(world, "scenario_name", "")) == "tutorial":
        return {
            "success": True,
            "skipped": "tutorial",
            "message": "Tutorial - campaign autosave untouched",
            "filepath": "",
        }
```

Live evidence, `docs/audits/playtest_digests/audit-tutorial/digest.md`:

```
  - new game -> New campaign started. Your campaign autosave is untouched.
```

Verdict: **REPRODUCED as filed.** Line-number drift: `main.gd` is **6378**, not
the filed 6238; `backend/main.py` is **4400-4421**, not 4040-4051;
`save_manager.py` is **255-277**, not ~256-269. `main_menu.gd:444`,
`menu_boot.gd:19-21` and the test lines are EXACT.

**(a) True seam BY SYMBOL:**
- `scripts/main_menu.gd::_on_tutorial_pressed` (line 438-448) - the confirm row.
  **NOT** `_on_begin_pressed` (426-436), whose identical sentence at line 431 is
  TRUE (`/new_game` without a scenario does refresh the autosave).
- `scripts/main.gd::_on_tutorial_boot_requested` (the function whose docstring is
  at 6375 and whose `add_output` is at 6378).
- `scripts/menu_boot.gd` header comment, the `"tutorial"` line.

**(b) What the row's filed fix would BREAK - one real thing:** its replacement
copy, *"its autosave is kept - Continue restores it"*, is a NEW false statement in
one reachable arm. The confirm row is shown when
`_saves.size() > 0 or MenuBoot.came_from_game` (`main_menu.gd:442`). In the
`came_from_game and _saves.is_empty()` arm there is **no save file at all** -
`autosave()` is written from exactly two places
(`backend/main.py:4404` at `/new_game`, `backend/commands/meta_executor.py:482` at
turn start), so a session that hydrated the backend's boot world and never ended a
turn has nothing on disk. In that arm the tutorial DOES destroy the live world
irrecoverably, and "Continue restores it" would be the same class of lie the row
exists to remove.

**(c) Minimal correct fix:** copy only, three surfaces, and keep the promise
conditional:

- `main_menu.gd:444` -> `"Enter the School of War? Your running campaign leaves the table."`, and when `_saves.size() > 0` append `" Its autosave is kept - Continue restores it."` (that branch is one line and the data is already in `_saves`).
- `main.gd:6378` -> `"Convening the School of War. Your campaign autosave is kept."`
- `menu_boot.gd:19-21` -> `... replaces the running world; the campaign autosave is NOT touched (save_manager.autosave no-ops for scenario_name == "tutorial", TUT-F2).`

Leave `main_menu.gd:237` and `:431` (the Begin confirm) alone - they are accurate.

**(d) Existing tests that pin today's behaviour and would flip:** **none.** The
"replaced" strings are unpinned; I grepped `tests/` for them and for
`"School of War"` in a copy-asserting form and found only structural pins
(`tests/test_tutorial_position7.py::TestClientStructuralPins::test_g4_menu_pins`
asserts `'_add_menu_button("tutorial"' in menu`, `'_launch("tutorial")' in menu`,
`'"begin", "return", "tutorial":' in menu` - all survive).

Pins that FIX the backend side and must keep passing (they will, the fix is
client-copy only):

| test | assertion |
|---|---|
| `tests/test_tutorial_position7.py::TestTutorialSaveIsolation::test_new_game_tutorial_leaves_existing_autosave_untouched` (line 385) | `assert "campaign autosave is untouched" in data["message"]` |
| `tests/test_tutorial_position7.py::TestTutorialSaveIsolation::test_tutorial_end_turn_does_not_write_autosave` (395) | `assert not autosave_path.exists()` |

One nearby pin worth knowing about, because it constrains the WORDING:
`tests/test_main_menu_and_ux_pass.py::TestMainMenuScene::test_begin_confirms_before_replacing_a_campaign`
(line 132-135) asserts `assert "autosave" in gd.lower()` over `main_menu.gd`. The
proposed copy keeps the word, so it holds - but a rewrite that drops "autosave"
from the file entirely would red it.

---

## Cross-row findings

1. **FA-29's `fix_shape` contradicts its own `_corrected` caveat.** Moving the
   string into `Utils.launch_hint()` is the one change that reds
   `test_main_menu_and_ux_pass.py:129`, the pin the row explicitly says it is
   protecting. This is a SEVENTH member of the "fix_shape vs summary" family
   beyond the six CLAUDE.md names (FA-54, FA-D13, FA-D18, FA-D24, FA-D25, FA-100).

2. **FA-57's replacement copy introduces a new false statement** in the
   `came_from_game and no saves` arm. A copy-only row whose fix text is itself
   unverified copy.

3. **A loose fixed-length scrape in an existing pin.**
   `tests/test_pc15_16_18_visual_fixes_2026_08_15.py:253` does
   `handler = src[at:at + 2500]` where the real
   `_on_command_input_gui_input` body is **972** chars; the window runs 1528 chars
   past it, through `_history_previous`, `_history_next` and into
   `_unhandled_input`'s docstring. I checked: `alt_pressed`, `_SCREEN_HOTKEYS` and
   `_is_modal_dialog_open()` are all currently **absent** from the overshoot, so
   the pin is not vacuous today - but it is one refactor away from being satisfied
   by a neighbouring function. Same class as the NA-6 dead-name pin the IGR-B
   round found (4 of 7 arms non-binding from a fixed 2,400-char scrape). Bound it
   to the function body (`src[at:src.index("\nfunc ", at+10)]`) while slice 13 is
   in that file.

4. **`cycle_map_fill_mode() -> String` returns the new mode and its only caller
   discards it** (`map_renderer_base.gd:2214`, bare call). So even when M reaches
   the map, the player is told nothing about which of blended/political/terrain
   they landed on. Free win inside FA-N56.

5. **`set_input_enabled(true)` is called on line 745 of `main.gd`, four lines
   after the boot help advertises M, +/- and Home** - the client teaches six keys
   and then, in the next statement, enters the state that kills four of them. The
   two are literally adjacent in the same function.

6. **The `.pck` question is settled for the JSONs too**, as a by-product:
   `europe.json` / `europe_1805.json` are typed `JSON/JSON` in the filesystem
   cache, i.e. real resources, so ROADMAP row 10's "verify JSONs in the .pck"
   remainder should PASS on a fresh export. Worth recording; not a row.

7. **A licence-family blind spot in the existing pins.**
   `test_ui_visual_foundation.py::test_ui1_font_ttf_and_ofl_present` says
   `"(OFL required)"` and checks only that the file exists in the repo. It is
   almost certainly why the project believes the obligation is discharged. Any
   FA-N84 pin must be a distribution census, and should carry a comment saying so
   at that assertion.

8. **Confidence note offered honestly:** my `all_resources` reading is inferred
   from Godot's own `TextFile/TextFile` vs `FontFile`/`JSON` typing plus the
   project's own build.bat warning, not from running an export. The March-2026
   `.pck` I parsed has ZERO `.txt` but its source tree had zero `.txt` under
   `res://`, so it corroborates nothing on its own and I have not treated it as
   proof. If the builder wants certainty before writing the pin, one fresh export
   settles it in five minutes.

## Probe inventory

- `scratchpad/repro/j1/probe_1_pck.py` - parses the GDPC file table of the shipped
  March-2026 `deploy/dist/ink_iron_server/InkAndIron.pck` (114 entries, extension
  histogram, non-resource hunt).
- `scratchpad/repro/j1/probe_2_hotkey_census.py` - FA-N56's two-directional
  census: focus-safe keycodes, the `_SCREEN_HOTKEYS` table, the README HOTKEYS/THE
  MAP blocks, main.gd's boot help, per-key verdicts, `grab_focus` count,
  `cycle_map_fill_mode` callers, and the project-wide `has_feature` census (FA-29).
- `scratchpad/repro/j1/probe_3_licenses.py` - FA-43/FA-N84: export preset fields,
  build.bat copy statements + licence regex, spec `all_datas` mutations, the
  16-file census L, Godot's editor filesystem-cache typing of the OFL/ttf/json
  files, and the two credit surfaces that name the missing file.
