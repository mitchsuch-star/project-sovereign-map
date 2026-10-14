# NEXT SESSION PROMPT — Pre-Deploy S12b: UXR-D4 "The Side Desk" (with UXR-X28 at its head)

> Overwritten each time a session hands off. Current hand-off: **October 14,
> 2026, after S12 (UXR-3 fixes) closed.**
>
> S12 part 2 landed the grip and the plate, R6's war-room proofs, the boards and
> the found rows, then read every surface again against the frozen checklist
> with three fresh blind readers (`docs/audits/UXR3_REREAD2_2026_10_14.md`):
> - **787 → 977 → 1,149 of 1,160 marks ✓.** Seven items read 145 of 145; R2 reads 134.
> - **No surface reads under 6** (82 → 9 → 0). 134 surfaces read 8 of 8.
> - **74 of the 78 rows are FIXED** with their re-reads. The eleven R2 marks
>   left sit on rows UXR3-2, 24, 29, 41 and the new 79 … 81. All are re-homed
>   to UXR-4 (S15) with frames, the readers' reasons and each one's fix
>   decided.
> - UXR-X28 (the map's furniture at the whole-map view) moved here, to this
>   session's head, because the Side Desk changes the map's width.
>
> **Nothing waits on the user.** On October 13 the user said "make all
> decisions … nothing hanging". Every fork this session can meet is decided
> below. UXR-4, the user's own eyes at 5120×1440, is at S15.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S12b — UXR-X28 at its head, then UXR-D4 "The Side Desk": a layer-50 screen pinned NON-modal in the right third, beside a live map.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S12b. The contract is `docs/DESIGN_REFINEMENT.md` UXR-D4 (ruled October 13, 2026 under the user's delegation: build it, non-modal).
- Work directly on master per `CLAUDE.md`, and commit and push each slice.
- Run `git fetch origin` first and read `git log -8 --stat` before touching anything.
- **Every decision is already made** (the user's ruling, October 13, 2026: "make all decisions … nothing hanging"). This prompt is the approved plan:
  - Do not stop for Plan Mode approval, and do not pause between slices.
  - The rules under "Decided in advance" settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

Read first:
- `BUG_FIXES.md` §UXR-2's extras, UXR-X28 (the head), and `docs/audits/UXR3_REREAD2_2026_10_14.md` §1 and §7 (what S12 left and where it went);
- `DESIGN_REFINEMENT.md` UXR-D4 (the ruling) and `SYSTEMS_REFERENCE.md` §111 (the layout law: `clamp_centered_panel`, `refit_surface`, the grips), §112 (HUD Centred: `Utils.hud_band`), §113.7 (S12's rules);
- `top_bar.gd` (`toggle_screen`, `_open_screen`, `_close_screen`, `close_all_screens`, `refit_active_screen`) and `main.gd` (`_on_screen_changed`, `_is_screen_open`, `_is_hotkey_blocked`, every `close_all_screens()` call site);
- the six layer-50 screens: `dispatch_view.gd`, `gazette_view.gd`, `campaign_log.gd`, `marshal_management.gd`, `strategic_ledger.gd`, `diplomatic_ledger.gd`;
- `tools/uxr3_action_probe.py` (`start_backend`, the sandboxed war-room backend) — the driven harness reuses it.

**Slice 0, the head — UXR-X28, the map's furniture** (`BUG_FIXES.md` §UXR-2's extras; moved here at S12's close with its reason).
- **The instrument first.** `tools/iq10_surface_screenshot.gd` records each map-tier text row's screen rect. Map rows sit inside the map's SubViewport: take the label's rect in the viewport's canvas, apply the viewport's canvas transform, then offset by the SubViewportContainer's global rect and scale. Today the frame record carries them with no `rect`, so no census can read them.
- **The census.** `tools/uxr3_frame_census.py` gains `map_overlaps`: every pair of map-tier rows whose rects overlap by at least 1 px², on `war_room_boot`'s whole-map view at the five resolutions. Measure before any fix, and record the count in the slice's commit.
- **The fix.** `map_label_layer.gd`'s occupied-rect avoidance learns the standees' names and the garrison and fog chips. The priority is: province names first, then the standees' names, then the chips. A chip yields: it nudges off a name, or hides at the fit zoom when no free place is within one chip's width. A chip never covers a name, and a name never covers a chip.
- **Done when** the census reads 0 at the five resolutions with the dock closed. Slice 3 adds the dock-open board, and the census must read 0 there too.
- **Test:** the census pin in `tests/test_uxr3_s12b_reread.py`'s style, held on a committed record (`docs/audits/uxr_d4/map_census.json`), plus a source pin on the priority order.

**Slice 1 — the pin and the dock** (client only).
- **Which screens pin:** all six layer-50 screens. Each header row gains a text chip **"Pin"** (pinned: **"Unpin"**) beside its close cross, styled as the family's chip, tooltip "Keep this screen open beside the map — Esc or Unpin closes it". A text chip, not an icon: Phosphor ships no push-pin and nothing is downloaded.
- **One pinned screen at a time.** `top_bar.gd` gains `pinned_screen: String`, `toggle_pin(name)`, `unpin()`, `is_pinned()`. Pinning the open screen moves it from `active_screen` to `pinned_screen`, so `is_screen_open()` is false while only a pinned screen stands. Opening any other screen unpins and closes the pinned one first; the one-screen rule holds.
- **Placement:** `Utils.dock_right(panel)` places a pinned screen's panel in the right third of the HUD band (`Utils.hud_band`), under the top bar (`TOP_BAR_HEIGHT + top_bar_growth() + HUD_MARGIN`) down to `HUD_MARGIN` above the bottom. Its width is the screen's remembered grip width (`clamp_user_size.x`) when the player set one, else a third of the band, clamped to a quarter … a half of the band. The grip hides while docked; unpinning restores the centred rect through `clamp_centered_panel`.
- **Modality:** while pinned, the screen's `BackgroundOverlay` hides and ignores the mouse; `main.gd` restores the map's mouse filter and panning (`_on_screen_changed` keys on `active_screen`, so a pinned screen alone reads as no screen). A decision popup (layer ≥ 100) still draws and blocks above it.
- **The HUD gives the dock its third.** `Utils.hud_band` returns the band minus the dock (its width plus `HUD_MARGIN`) while a screen is pinned, so every HUD surface that already measures from it (the war HUD, the region panel, the tutor card, the rail slot, the command window) re-fits through the existing `_refit_hud_band` road. Pin and unpin both call it.
- **Keys:** typed keys go to the command line unless the pinned screen has focus. The screens' `_input` already yields a bare digit to the caret (SF7-X24); keep that. Esc with a pinned screen, no popup and nothing else open unpins and closes it.

**Slice 2 — it lives through the turn.**
- **Refresh:** every command response and every end turn re-read a pinned screen: `main.gd` calls `top_bar.refresh_pinned()` after `_on_command_result` and after the end-turn chain settles. Each screen gains `refresh_pinned()`: it re-fetches for its CURRENT tab and keeps its scroll (no tab reset, no scroll to top).
- **Which closes keep the pin.** Classify every `close_all_screens()` call site in `main.gd` by one rule: a turn transition, a command, a popup or a mailbox keeps the pin (it closes `active_screen` only); the pause menu, a scene change, a load, a new campaign and the fall unpin as well (a new `top_bar.close_everything()`). Record the classification, site by site, in the slice's commit and in the rules section.
- **The pin is a session state.** It is not saved and not restored on the next launch (the contract does not ask it; nothing promises it).

**Slice 3 — the proof.**
- **The driven harness** `tools/uxr_d4_side_desk_harness.gd` boots the real `main.tscn` against a sandboxed backend, reusing `uxr3_action_probe.py`'s `start_backend` (an unused port from 8006, never 8005, its own `INK_IRON_SAVE_DIR`, the mock parser). It:
  - opens the Strategic Ledger and presses Pin: the panel stands in the right third, the overlay is hidden, `map_area.mouse_filter` is STOP, and a map click selects a province;
  - sends a typed command ("Ney, fortify"): the ledger re-reads (one more `get_ledger` call) and stays pinned;
  - raises a popup (the end-turn chain's enemy phase, layer ≥ 100): the ledger stays visible beneath it;
  - ends the turn: the ledger stays pinned and shows the new turn;
  - presses Esc: the ledger closes and the map stays live.
- **The test** is `tests/test_uxr_d4_the_side_desk.py`: the driven proof plus source pins (one pinned screen; the classification of the close sites; `hud_band` minus the dock). It joins `ENGINE_GROUP_MODULES` in `tests/conftest.py`.
- **The census:** the IQ-10 manifest gains `side_desk_ledger` and `side_desk_generals` (a pinned screen beside the war room). Shot at five resolutions, `uxr0_readability_report.py` reads 0 RED / 0 P1 at 5120×1440, and the frame census (`tools/uxr3_frame_census.py`) reads 0 cut lines, 0 grip overlaps and, with Slice 0's `map_overlaps`, 0 map overlaps with the dock open. These ids are not checklist surfaces (`docs/UX_CHECKLIST_V1.json` stays frozen).

**Done when:** a pinned ledger survives a command, a popup and an end turn beside a live map (the driven test), the census reads clean at 5120×1440, and UXR-X28 reads 0 with the dock open and closed.

**The records the close carries:**
- `DESIGN_REFINEMENT.md` UXR-D4: the landing record; `BUG_FIXES.md` UXR-X28 closed with its census;
- `SYSTEMS_REFERENCE.md`: a new §114 "The Side Desk";
- `PRE_DEPLOY_PLAN.md` §2: S12b struck;
- `STATUS.md` ▶ NEXT UP: a new block (seven kept; the oldest to the top of `docs/archive/STATUS_2026_Q4.md`);
- `CLAUDE.md`: the LIVE STATE line (≤ 62,000 B);
- this file, rewritten for S13 (DD-B: three hand-played campaigns in the client at 5120×1440), with every decision made in it.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Check `tasklist | grep -ci godot` before every start. The hook runs Godot too (the engine group): start no engine during a commit.
- **Never touch the user's live 8005 backend.** Run any backend on `SOVEREIGN_PORT=8006` or above with `INK_IRON_SAVE_DIR` set.
- **The hook tests the working tree, not the index.** Park a later slice's test edits outside `tests/` before committing an earlier slice; an untracked test in `tests/` runs in the hook.
- **`PYTHONDONTWRITEBYTECODE=1`** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE`.
- **The hook** runs ruff and the full parallel suite (about 6:30; 30,897 tests at S12's end). Commit with `run_in_background: true` from Bash, with a message file and never `--no-verify`. Read the log's `[pre-commit]` and `EXIT=` lines before believing a commit.
- **Shell.** Bash heredocs mangle backslashes and `\n` inside Python strings. Write scripts with the Write tool and run them by path. GDScript `:=` cannot infer from an untyped value: type such locals explicitly.
- **A ScrollContainer's panel margin does not clip its child** (S12 part 5b): to shorten what a scroll shows, shorten the scroll.
- **A new client test that drives the engine joins `ENGINE_GROUP_MODULES`**, or two workers fight over one window.
- **Git:** never `git add -A`; stage by name. **Line endings:** normalise records to LF before committing.
- **Docs caps.** `CLAUDE.md` ≤ 62,000 B. `STATUS.md` keeps seven ▶ blocks.

**Code-health rules in force:**
- A new font size is a theme step, not an override (`RAW_RATCHET` 1). A grey is a named palette token. A control that cannot act is disabled with its reason (`Utils.set_available`).
- A fix lands in the stage that owns it (`_attack_*`, `_strategic_*`, `_oneliner_*`, `_choice_*`, `_ratify_*`).

**Open with the user:** nothing. UXR-4 (their eyes at 5120×1440) is at S15 with the deploy; the rows S12 re-homed there wait for it.

**Do not:** edit `docs/UX_CHECKLIST_V1.json`, change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a ratchet, or start DD-B.
