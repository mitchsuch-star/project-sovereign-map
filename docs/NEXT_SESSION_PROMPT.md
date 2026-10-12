# NEXT SESSION PROMPT — Pre-Deploy S9: UXR-2 "The layout law"

> Overwritten each time a session hands off. Current hand-off: **October 12,
> 2026, after S8b landed CODE-2a with CODE-1 batch 6 at its head** —
> `CombatExecutor._execute_attack` is a driver of twenty `_attack_*` stages
> behind one `AttackContext` (slots, no defaults past the six parameters, so an
> unassigned read raises as the local did; the old `locals()` reads are
> `getattr(ctx, …)` / `hasattr(ctx, …)`; a falling-through stage returns
> `_NEXT_STAGE`), cut mechanically at top-level statement boundaries with
> `BASELINE_SERIES` + M1–M7 byte-identical and no re-record; **functions over
> 500 lines 34 → 33**; the source-text pins read "the attack" through
> `tests/_attack_stages.py`; the shape pinned in
> `tests/test_code2a_the_attack_is_staged.py`. Batch 6 retired all 126
> pre-October levers no batch had named, **levers 358 → 231**. Landing records
> `docs/CODE_HEALTH_PLAN.md` §CODE-1 BATCH 6 + §CODE-2 "CODE-2a landing
> record"; `docs/PRE_DEPLOY_PLAN.md` §2 (S8b STRUCK; **S9 = UXR-2 is NEXT**);
> no `SYSTEMS_REFERENCE.md` section (a pure refactor moves no rule).
> Routing authority: `docs/PRE_DEPLOY_PLAN.md` §2 → `docs/UX_UI_REVIEW_PLAN.md`
> §UXR-2; `docs/STATUS.md` ▶ NEXT UP and the `CLAUDE.md` LIVE STATE line point
> there. The Score Finish residue (`SCORE_FINISH_SPEC.md` §3 Step 9) stays
> PAUSED until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S9 — UXR-2: the layout law.** Routing authority = `docs/PRE_DEPLOY_PLAN.md` §2 → `docs/UX_UI_REVIEW_PLAN.md` §UXR-2 (the rule, the five parts, the done-when). Work directly on master per `CLAUDE.md`'s workflow; commit and push at each clean slice. `git fetch origin` first and read `git log -3 --stat` before touching anything. Plan Mode first (the user's standing preference for a non-trivial session); land the first low-risk slice, then pause for review before the large one.

**The rule** (`UX_UI_REVIEW_PLAN.md` §UXR-2): a surface is either ANCHORED (its rect a fraction of the viewport, with min and max in logical px) or CLAMPED-AND-GRIPPED (a fixed authored rect `clamp_centered_panel` shrinks, a grip resizes it, the size remembered in `ui_settings.cfg`). No surface is a bare fixed rect. The five parts: (1) grips on the Strategic Ledger, the Generals screen, the dispatch view, the campaign log and the Gazette — the terminal's grip (`main.gd`, U2 Part 1) becomes a shared `ResizeGrip` node, persistence in `ui_settings.gd` (`get/set_panel_size(name)`); (2) anchors for the HUD family (top bar, war-status panel, notification rail, region panel, tutorial card); (3) a clamp-coverage census over every `CanvasLayer` popup (layers 100–122), a pin failing on an uncovered fixed rect; (4) the override diet — the 268 font-size overrides to named theme sizes, ratcheted; (5) scroll where content is unbounded, enforced by a scene census. **Done when:** every surface anchored or clamped-and-gripped by the census; the five screens resize and remember; UXR-0 reads 0 RED rows on every surface at every resolution — which takes UXR-X5 (the diorama's tableau labels) and UXR-X6 (the war-detail bar tags), both routed here (`UX_UI_REVIEW_PLAN.md` §"Landing record — S1b").

**Read first, in this order:** `UX_UI_REVIEW_PLAN.md` §UXR-0 / §UXR-1 and both landing records (the instrument, the derivation, what S1a/S1b already moved); `godot-client/project-sovereign/scripts/utils.gd` (`clamp_centered_panel` and its docstring's scroll rule); `ui_settings.gd`; the terminal grip in `main.gd`; `tests/test_uxr0_readability.py` (the ratchet with the routed-families invariant) and `tests/test_uxr1b_settings_additions.py`; `docs/PLAYTESTING.md` Mode C (the client capture harness). The user's monitor is ONE 5120×1440 panel — every reading includes it.

**Traps.** Any `.gd` edit needs the Godot parse harness re-run (run it via `Start-Process`, read its exit code) and `tools/godot_parse_report.json` re-committed (a stale-report guard pins it). Confirm Godot is frontmost before any synthetic input. EP-F2's census forbids "(s)" hedges in client strings — use `Utils.plural`. A Bash heredoc halves backslashes, turns `\b` into a BACKSPACE byte and aborts on a `'` inside `python - <<EOF` — write every script and every doc insertion with the Write tool. `git add -A` never; stage by name. The hook runs ruff + the full parallel suite (~7 min): commit with `run_in_background: true` from Bash, a message file, never `--no-verify`, no tracked edit while it runs (the suite reads the WORKING TREE). Read the hook log's `[pre-commit]` and `EXIT=` lines before believing a commit. `ruff` is not on Bash's PATH — `".venv/Scripts/python.exe" -m ruff check backend/`. The console is cp1252 (a script that prints `▶` dies AFTER its writes — check the files, not the traceback). `-n 8` without `--dist loadgroup` fakes order failures. `core.autocrlf=true`: keep each file's own newline. Never kill a `-m backend.main` process; run a test pair beside the user's 8005 with `SOVEREIGN_PORT=8006`. `CLAUDE.md` is at 61,983 B of its 62,000 cap — pay for a new LIVE STATE row by cutting the oldest.

**Code-health rules now in force:** a new lever lives one session after its attribution, then retires at the next slice's head (`tools/retire_lever.py`; the October levers + `THE_LEAGUE_TREATS_WHEN_SPENT`'s staging bundle are CODE-1's November batch, at a head once October 2026 closes). The attack is staged: a combat fix lands in the `_attack_<stage>` that owns it (the driver's docstring is the index; a shared local is `ctx.<name>` and must be a field of `AttackContext`); a pin about "the attack's source" reads `tests/_attack_stages.attack_source()`.

**Records the commits carry:** `UX_UI_REVIEW_PLAN.md` §UXR-2 landing record, `PRE_DEPLOY_PLAN.md` §2 (the S9 row struck), `STATUS.md` ▶ NEXT UP (seven ▶ blocks at most — the oldest to `docs/archive/STATUS_2026_Q4.md`, newest first), the `CLAUDE.md` LIVE STATE line, `SYSTEMS_REFERENCE.md` §111 for the layout rule, `BUG_FIXES.md` rows for anything found, this file rewritten for the next row (`PRE_DEPLOY_PLAN.md` §2).

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a readability ratchet, edit a committed blind file, tune an instrument to a fix.
