# NEXT SESSION PROMPT — Pre-Deploy S11: UXR-3, the look-and-feel review

> Overwritten each time a session hands off. Current hand-off: **October 13,
> 2026, after S10b (CODE-2c) closed.** `_ratify_treaty` and
> `_process_dialogue_choice` are drivers of nine stages each. Functions over 500
> lines read 28, and **CODE-2 is DONE**: none of its eight named functions is
> over 500 lines.
>
> **Nothing waits on the user.** On October 13 the user said "make all
> decisions … nothing hanging". Every fork this session could meet is decided
> below. UXR-4, the user's own eyes at 5120×1440, is scheduled at S15 with the
> deploy, and their marks override the readers' there.
>
> Records: `docs/UX_UI_REVIEW_PLAN.md` §UXR-3 (the contract), §UXR-0 … §UXR-2
> (the instruments and their landing records). Routing authority:
> `docs/PRE_DEPLOY_PLAN.md` §2, row S11. The Score Finish residue stays PAUSED
> until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S11 — UXR-3, the look-and-feel review.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S11.
- Work directly on master per `CLAUDE.md`, and commit and push each part.
- Run `git fetch origin` first and read `git log -5 --stat` before touching anything.
- **Every decision is already made** (the user's ruling, October 13, 2026: "make all decisions … nothing hanging"). This prompt is the approved plan:
  - Do not stop for Plan Mode approval, and do not pause between parts.
  - The rules under "Decided in advance" settle every fork; ask the user nothing.
- **No CODE-1 batch at this session's head:** October has not closed. The November batch takes the head of the first session that starts on or after November 1, 2026.

**What this session is.** A REVIEW, not a fix session:
- read every surface against a frozen checklist;
- name the worst five;
- file every ✗ as a row owned by S12.

It changes nothing a player sees. S12 ("UXR-3 fixes") takes the rows, worst surfaces first.

**Part 1 — freeze the checklist, its own commit, before any reading.**
- Write `docs/UX_CHECKLIST_V1.json`: the eight items R1–R8 of §UXR-3, each with its judge (instrument / reader / driven) and its exact pass rule as decided below.
- Write the surface list: the ten groups in §UXR-3's order, each split into the concrete surfaces the IQ-10 manifest (`tools/iq10_capture_payloads.py`) already names.
- Add a pin, `tests/test_uxr3_checklist_frozen.py`. It checks the file's eight ids, its surface order, and a SHA of its canonical JSON recorded in the test, so an edit after the reading fails.
- Commit and push. Every reading after this reads THAT file.

**Part 2 — the evidence.**
- **The frames:** `tools/iq10_run_captures.py` over the whole manifest at the five `PHYSICAL_RESOLUTIONS` of `tools/uxr0_readability_report.py` (1920×1080, 2560×1440, 3440×1440, **5120×1440**, 3840×2160).
- **The instruments:**
  - R1: `tools/uxr0_readability_report.py` (run with `-X utf8`);
  - R3: `tools/uxr2b_contrast_report.py`;
  - R4: the override census (`RAW_RATCHET` in `tests/test_uxr2_override_diet.py`) and the theme-token reading;
  - R7: the readability record's clipped / off-screen / under-a-modal flags.
- **The driven records (R5 and R6):** the existing driven harnesses (`tools/mode_c_driven_session.py` and the per-surface `.gd` harnesses in `tools/`). A surface with no driven record yet gets one in the same pattern.

**Part 3 — the reading.**
- **Three blind readers**, as Agent-tool subagents launched in ONE message so they run in parallel. Each gets:
  - the frozen checklist;
  - the frames;
  - the instrument and driven records.

  None sees the others' marks, and none is told what the instruments concluded beyond the records themselves.
- Each returns a mark and a cited frame per surface × reader-judged item. Aggregate two-of-three as `tools/score_panel.py eyes` does, and record the spread (3–0 or 2–1).
- Write `docs/audits/UXR3_REVIEW_2026_10_<day>.md`:
  - the surface × item table;
  - each surface's score out of 8;
  - the worst five named;
  - the spread per mark;
  - every frame cited.
- **File every ✗** as a `docs/BUG_FIXES.md` row in a new section `§UXR-3 — the review`, each with its frame. The tag is `⟨SF step=pre-deploy S12 · UXR-3 <surface> · pillar=ui_ux⟩`, so `test_score_finish_step0.py` accepts it. The owner is S12 ("UXR-3 fixes"); the completion is the item re-read ✓ on that surface. Already-owned rows (UXR-X9, UXR-X28) are cross-referenced, not re-filed.
- Commit and push, then close (the records below).

**Decided in advance:**
- **The user's role.** The user's eyes are UXR-4 at S15, where their marks override. This session never waits for them.
- **R1 runs at all five resolutions.** §UXR-3 says "four", but the instrument reads five and the fifth is the user's own monitor. The stricter reading wins: 0 RED rows at each of the five.
- **R7 covers 1920×1080, 3840×2160 and the user's 5120×1440.**
- **R3 thresholds:** body text ≥ 4.5:1 and captions ≥ 3:1, measured by `uxr2b_contrast_report.py` with High contrast OFF (the default a new player sees). High contrast ON is recorded beside it but never scores.
- **R4 fails on a one-off colour or size** found by the census (an override outside the named theme steps, a grey not routed through `Utils.toned` / `toned_hex` / the COLOR tokens). A reader's "looks inconsistent" without a census hit is recorded but does not fail the item.
- **R6 unproven is ✗.** No driven record showing the answer within the frame means the item fails, and the row's fix is the driven proof plus whatever it finds.
- **Disagreement:** the two-of-three mark stands. A 2–1 ✗ is filed like a 3–0 ✗, with the spread recorded on the row.
- **"Top five by time on screen"** means §UXR-3's first five groups: the war room, the morning dispatch, the Generals screen, the diplomacy wizard with the settlement table, and the Strategic Ledger.
- **The Side Desk (UXR-D4)** does not exist yet; it lands at S12b with its own census. This review does not score it.
- **S11's own done-when:**
  - every surface in the order has a reading;
  - every ✗ is filed with owner S12;
  - the worst five are named.

  §UXR-3's done-when (the top five at 8 of 8, none under 6 of 8) belongs to S12. If the reading already meets it on a surface, record that.
- **A surface the capture harness cannot reach** gets a ✗ on every item it cannot evidence, filed with the harness gap as the row's first fix. It never gets a "skipped".
- **No fix lands in S11,** not even a one-liner, so the reading stays a clean baseline for S12's re-read. A crash or a P1 found while reading is the exception: file it as a P1 with owner S12 at the top of the list.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Two shoots crashed with 0xC0000005 (memory is 1–6 GB free). Chain the shoots sequentially in ONE background command.
- **Capture windows take the user's keystrokes** when they open foreground. The IQ-10 harness sets `root.gui_disable_input` and records `stray_input` / `focus`; read those fields before trusting a frame.
- **Never touch the user's live 8005 backend.**
  - A driven harness stubs its api clients (the top bar's too) and refuses `:8005`.
  - Run any backend you need with `SOVEREIGN_PORT=8006` and `INK_IRON_SAVE_DIR` set, or it rewrites the user's autosave.
- **A headless Godot root viewport is 64×64.** A driven layout harness needs `--windowed --resolution 1600x900 --position 5200,20`, and `root.mode/size` set on its first tick.
- **`iq10_capture_payloads.py --only X` rewrites the manifest.** Never edit a `.gd` during a shoot.
- **`PYTHONDONTWRITEBYTECODE=1` in the shell** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE`.
- **The hook** runs ruff and the full parallel suite (about 6–8 min; about 30,760 tests at S10b).
  - Commit with `run_in_background: true` from Bash, using a message file and never `--no-verify`.
  - Make no tracked edit while it runs.
  - Read the hook log's `[pre-commit]` and `EXIT=` lines before believing a commit.
- **Shell.** A Bash heredoc mangles backslashes and apostrophes. Write scripts with the Write tool and run them by path.
- **Git.** Never `git add -A`; stage by name. Frames a record names are force-added (`git add -f`); the regenerable bulk under `docs/audits/score_runs/**/frames/` is ignored.
- **Line endings.** Working copies can be CRLF while the blobs are LF. An edit script must detect the file's own newline.
- **Docs caps.**
  - `CLAUDE.md` sits at 61,982 / 62,000 B: pay for every new word by trimming the oldest LIVE STATE row.
  - `STATUS.md` keeps seven ▶ blocks at most; the oldest goes to `docs/archive/STATUS_2026_Q4.md`, newest first.

**Code-health rules in force:**
- A new font size is a theme step, not an override (`RAW_RATCHET` 11). Any dim grey goes through `Utils.toned` / `toned_hex` / the COLOR tokens.
- A fix lands in the stage that owns it:
  - a combat fix in its `_attack_<stage>`;
  - a standing-order fix in its `_strategic_<stage>`;
  - a log line in its `_oneliner_<family>`;
  - a dialogue answer in its `_choice_<family>`;
  - a ratification clause in its `_ratify_<stage>`.
- A new lever lives one session past its attribution, then retires at the next slice's head (`tools/retire_lever.py`).

**The records the close carries:**
- `UX_UI_REVIEW_PLAN.md` §UXR-3: the landing record, with the reading's numbers and the worst five.
- `PRE_DEPLOY_PLAN.md` §2: the S11 row, struck.
- `STATUS.md` ▶ NEXT UP: a new S11 block.
- `CLAUDE.md`: the LIVE STATE line.
- This file, rewritten for S12 (UXR-3 fixes, worst five first), with every S12 decision made in it as this one was, so nothing waits on the user.

**Open with the user:** nothing. UXR-4 (their eyes at 5120×1440) is scheduled at S15 with the deploy.

**Do not:** change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a ratchet, edit the checklist after Part 1's commit, or fix during the reading.
