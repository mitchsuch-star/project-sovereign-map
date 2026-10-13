# NEXT SESSION PROMPT — Pre-Deploy S9b: UXR-2's adjustability extras

> Overwritten each time a session hands off. Current hand-off: **October 12,
> 2026, after S9 landed UXR-2 "the layout law"** in six commits on master: A
> `77172273` the routed families (UXR-X5/X6), B `5a62690e` the named sizes +
> scroll, C `af7f1e79` the grips + the refit road, the review fixes
> `95b3a1b5`, D `7ce88863` the anchors, then E the landing re-shoot.
> - **The law** holds for every CanvasLayer, checked by `tests/test_uxr2_layout_law.py` with an empty allowlist.
> - **Seven surfaces resize and remember:** the six top-bar screens and the war HUD, each with a shared `ResizeGrip`, proven driven by `tests/test_uxr2_grips_driven.py`.
> - **Raw font-size overrides fell 72 → 18.**
> - **The whole client reads 0 RED / 0 P1** at five resolutions.
>
> Records: `docs/UX_UI_REVIEW_PLAN.md` §UXR-2 landing record; rules `SYSTEMS_REFERENCE.md` §111; rows `BUG_FIXES.md` §UXR-2 (UXR-X5 … X20).
> Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2 (S9 STRUCK; **S9b is NEXT**), with `docs/STATUS.md` ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line pointing there. The Score Finish residue (`SCORE_FINISH_SPEC.md` §3 Step 9) stays PAUSED until S14.
>
> **⏸ RESUME NOTE (October 12, 2026, mid-S9b):** Slices A (UXR-D1, Text size), B (UXR-D3, HUD width + `[− ⌂ +]`) and C (UXR-X4, the map's furniture, + UXR-X26 / X27) LANDED on master. The approved plan's last slice is **D High contrast** (with the contrast instrument), then the hand-off to S10. Read `docs/UX_UI_REVIEW_PLAN.md` §UXR-2's S9b landing record and `BUG_FIXES.md` §UXR-2's extras first. **Capture runs: ONE engine at a time.** Two concurrent shoots ran this machine out of memory (Vulkan swap-chain / `mem` null crashes, exit 0xC0000005).
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S9b — UXR-2's adjustability extras.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S9b, which the user re-homed from S9 on October 12, 2026. Work directly on master per `CLAUDE.md`'s workflow, and commit and push at each clean slice. Run `git fetch origin` first and read `git log -5 --stat` before touching anything. Use Plan Mode first (the user's standing preference for a non-trivial session). Land the first low-risk slice, then pause for review.

**The four rows.** Each row carries its done-when and its test.
- **UXR-D1** (`DESIGN_REFINEMENT.md` §UXR) — a *Text size* slider in Settings → INTERFACE that scales the theme's named sizes alone. It works on the ladder S9's diet built in `ui/main_theme.tres` (Caption 14 · Body 16 · BodyLarge 17 · Lead 18 · ScreenTitle 20 · DialogTitle 22 · DialogTitleLarge 24 · DisplayTitle 28 · DisplayTitleLarge 30 · HeadingLabel 22) and moves no panel rect. Test: the census at text size 1.5 and scale 1.0 reads 0 RED on the five named surfaces. Remember the 18 named raw overrides (`tests/test_uxr2_override_diet.py`'s `EXEMPT`) do not ride the theme.
- **UXR-D2** — *High contrast*: every `UI_TEXT_DIM`-class text raised one token. Test: contrast measured off the frames, ≥ 4.5 : 1 for body and ≥ 3 : 1 for captions on the five named surfaces.
- **UXR-D3** — *HUD width: Full · Centred*: the HUD (command window, rail, top bar clusters, war HUD) confined to a central band of about 2560 logical px on a wider viewport, plus a ⌂ Fit Europe button. Test: the driven grip harness at 5120×1440 with Centred reads every HUD rect inside the band, and the layout-law census still passes. S9's anchors are its foundation: `Utils.TOP_BAR_HEIGHT`, `fraction_px`, the HUD's `_fit_*`.
- **UXR-X4** (`BUG_FIXES.md` §UXR-0) — the map's own furniture (name stacks, garrison chips, sail counts, and the map tooltip's 11-px `draw_string` text, which no census sees) follows the Interface Scale. Completion: the five raw sizes leave `map_renderer_base.gd`'s exemption, and the physical census's `map_small` count reads 0 at the derived scale.

**Read first, in this order:**
- `UX_UI_REVIEW_PLAN.md` §UXR-2's landing record (what S9 built and measured), then `SYSTEMS_REFERENCE.md` §111 (the law, the grip, the store, the clamps, the refit road, the ladder).
- `scripts/ui_settings.gd` (the store, `reset_layout`), `scripts/settings_panel.gd` (DISPLAY / INTERFACE) and `scripts/utils.gd` (`apply_body_font` — the model for a theme swap; `fraction_px`, `clamp_anchored_panel`).
- `tests/test_uxr0_readability.py` (the ratchet now at 0 / 0 — keep it there) and `docs/PLAYTESTING.md` Mode C.

The user's monitor is ONE 5120×1440 panel; every reading includes it.

**Traps — S9 paid for each of these:**
- **Godot edits.** Any `.gd` edit needs the parse harness re-run (via `Start-Process`; read its exit code) and `tools/godot_parse_report.json` re-committed. A new `class_name` needs a `--headless --import` pass first.
- **Driven harnesses.** A headless root viewport is 64×64. A driven harness that needs room must open a real window (`--windowed --resolution 1600x900 --position 5200,20`) and set `root.mode/size` on its first tick, not in `_init` (the project's maximize lands after `_init`).
  - **Stub every API client.** A harness must stub the top bar's client too (`top_bar.set_api_client`); swapping `main.api_client` alone sent real GETs to the user's 8005. Set `SOVEREIGN_PORT` in the test env and refuse `:8005`.
  - **Clear leftover state.** A driven "remembers" pin must clear the node's leftover state, or it proves the meta and not the store.
- **Capture runs.** Never edit a `.gd` while an IQ-10 capture shoots this repo's project (scripts load lazily). A BEFORE comes from a worktree (`git worktree add --detach`, `--headless --import` it, `--project <wt>/godot-client/project-sovereign`).
  - `iq10_capture_payloads.py --only X` rewrites the manifest with X alone; run the full capture before a full shoot.
  - `uxr0_readability_report.py` must run under `python -X utf8` (cp1252 dies on `→`).
  - A run's per-frame flags are in `<run>/result.json` → `results[].frames[]` (`clipped_text`, `buttons_offscreen`).
- **Font tests.** `tests/test_uxr1_scale_fix.py` runs `tools/uxr1_font_floor_sweep.py` for real, which can rewrite sources: never run it during a capture. A literal 14 in an override kills it; use a variation.
- **Pytest.** `-n N` without `--dist loadgroup` fakes order failures. An order-dependent world-swap leak (a module that swaps `M.world` without `M.game_state["world"]`) can surface when new modules shift the distribution; fix the test to read the world the endpoint reads.
- **Shell.** A Bash heredoc halves backslashes, turns `\b` into a BACKSPACE byte and aborts on a `'` inside `python - <<EOF`; write scripts with the Write tool.
- **Git.** Never `git add -A`; stage by name.
- **The hook** runs ruff and the full parallel suite (~7.5 min). Commit with `run_in_background: true` from Bash, using a message file and never `--no-verify`, and make no tracked edit while it runs. Read the hook log's `[pre-commit]` and `EXIT=` lines before believing a commit.
- **Running things.** `ruff` is not on Bash's PATH: use `".venv/Scripts/python.exe" -m ruff check backend/`. Never kill a `-m backend.main` process; run a test pair beside the user's 8005 with `SOVEREIGN_PORT=8006`.
- **Docs caps.** `CLAUDE.md` sits near its 62,000 B cap: pay for a new LIVE STATE row by cutting the oldest. `STATUS.md` keeps seven ▶ blocks at most; the oldest goes to `docs/archive/STATUS_2026_Q4.md`, newest first.

**Code-health rules in force:** a new lever lives one session past its attribution and then retires at the next slice's head (`tools/retire_lever.py`); CODE-1's November batch takes its head once October closes. A combat fix lands in the `_attack_<stage>` that owns it. The layout law is a census now: a new CanvasLayer surface must be CLAMPED (with a grip at layer 50) or FITTED by a named fitter reached by `size_changed` or `refit()`, and a new font size is a theme step, not an override (`RAW_RATCHET` 18).

**The records each commit carries:**
- `UX_UI_REVIEW_PLAN.md`: an S9b landing record under §UXR-2's.
- `PRE_DEPLOY_PLAN.md` §2: the S9b row struck.
- `STATUS.md` ▶ NEXT UP.
- The `CLAUDE.md` LIVE STATE line.
- `SYSTEMS_REFERENCE.md` §112 for the three settings and the map's scale term.
- `DESIGN_REFINEMENT.md`: D1–D3 BUILT. `BUG_FIXES.md`: X4 FIXED, plus rows for anything found.
- This file, rewritten for S10 (CODE-2b).

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a readability ratchet, edit a committed blind file, or tune an instrument to a fix.
