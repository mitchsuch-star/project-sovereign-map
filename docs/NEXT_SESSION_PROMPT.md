# NEXT SESSION PROMPT — Pre-Deploy S12: UXR-3 fixes (part 2 of 2)

> Overwritten each time a session hands off. Current hand-off: **October 13,
> 2026, after S12 part 1 (the classes) closed.**
>
> Part 1 fixed the review's rows by class and re-read every surface against the
> frozen `docs/UX_CHECKLIST_V1.json` with the same tools and three fresh blind
> readers (`docs/audits/UXR3_REREAD_2026_10_13.md`):
> - **787 → 977 of 1,160 marks ✓.** R1, R3, R4 and R7 read 145 of 145. R6 58 → 97.
> - **Surfaces under 6: 82 → 9.** At 8 of 8: 7 → 32. Every popup reads 8 of 8.
> - **45 of the review's 73 rows are FIXED** with the re-read. 28 stay open.
>   Five new rows (UXR3-74 … 78) file the 36 marks that went ✓ → ✗. Every
>   one is on an element part 1 did not touch; above all UXR-2's resize grip,
>   which fresh readers read as a button the probe's record does not hold (R5
>   on 81 surfaces).
> - Found while fixing: UXR3-X1 and X2 fixed; **X3** (the grip proof's one
>   failure in the hook) and **X4** (the war-room log's colours) open.
>
> §UXR-3's done-when (the top five groups at 8 of 8, none under 6) is NOT met:
> 17 of 115 top-five surfaces read 8 of 8, and 9 surfaces read under 6. Part 2
> owns it.
>
> **Nothing waits on the user.** On October 13 the user said "make all
> decisions … nothing hanging". Every fork part 2 can meet is decided below.
> UXR-4, the user's own eyes at 5120×1440, is at S15, and their marks override
> the readers'.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S12 part 2 — UXR-3 fixes: the grip, the driven proofs, the boards, the found rows, the closing re-read.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S12.
- Work directly on master per `CLAUDE.md`, and commit and push each part.
- Run `git fetch origin` first and read `git log -8 --stat` before touching anything.
- **Every decision is already made** (the user's ruling, October 13, 2026: "make all decisions … nothing hanging"). This prompt is the approved plan:
  - Do not stop for Plan Mode approval, and do not pause between parts.
  - The rules under "Decided in advance" settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

Read first:
- the re-read's §1–§6;
- `BUG_FIXES.md` §UXR-3: the review's still-open rows (each names what still reads ✗), §UXR-3 — the re-read's new ✗ (UXR3-74 … 78), §UXR-3 fixes — found while fixing (X3, X4), and F1 … F10;
- `SYSTEMS_REFERENCE.md` §113 (the instruments; §113.6 is part 1's);
- `docs/audits/uxr3_s12/review.json` and `reread.json` (every surface's marks and every row's state).

**Part 1 — the grip and the plate** (UXR3-74, 75; the open rows UXR3-12, 14, 23, 37, 43, whose last ✗ is the grip; UXR3-F4). This is the largest lever left: it is the only R5 ✗ on 81 surfaces.
- **The probe gains drag controls.** In `tools/uxr3_action_probe.gd`'s enumeration, a visible Control that is not a BaseButton, has a mouse filter other than IGNORE, and has a resize cursor shape (FDIAGSIZE, BDIAGSIZE, HSIZE or VSIZE) is a control of kind `drag`. Its press is a synthetic drag in a fresh instance: press at its centre, two motions of 20 px down and right, release. It answers VISIBLE when any control's rect changed. Pin the new kind in `tests/test_uxr3_the_review.py`'s rails class.
- **The grip says "drag".** `resize_grip.gd` draws a borderless corner hatch of three diagonal strokes in `UI_GOLD` at 0.7 alpha, with no boxed four-arrow icon. Its tooltip is "Drag to resize · double-click to restore". F4: it sits on the panel's corner outside the content. A census pin holds that no grip rect overlaps a text row or a control rect in the frame records.
- **The plate.** The tableau's nameplate becomes a flat engraved label (no fill, no border, no hover), with the same words in the same place. UXR-X9 keeps its own placement row.
- `tests/test_uxr2_grips_driven.py` must pass unchanged.

**Part 2 — R6's driven proofs** (UXR3-15, 16, 17, 27, 40, 45, 55). The proof is a war-room mode of the action probe:
- It opens each hand-off surface INSIDE the real `main.tscn` against a sandboxed backend (`SOVEREIGN_PORT=8006`, `INK_IRON_SAVE_DIR` set) and presses the control.
- It reads the war room's visible answer within 500 ms: the terminal's echo, a popup, or the map.
- A proven road is cited in a new `docs/audits/uxr3_s12/live_citations.json` (the S11 file's format, the S11 citation carried).
- A road with no visible answer gets an in-surface echo: the chip greys to "Sent: <order>", or the screen closes onto the terminal's echo.

**Part 3 — the never-pressed controls** (UXR3-69, 70, 71, 73). Each is proven by a driven test against a sandboxed backend:
- Save and Load through the real save road;
- Main Menu and New Campaign by a harness that sees `main_menu.tscn` stand after the change;
- Quit by a quit-intercept pin;
- the fall registers' "Main Menu" the same way.

**Part 4 — the boards, R2 / R8** (UXR3-1, 2, 18, 19, 20, 24, 28 … 31, 41, 46, 76, 77, 78). A LIVE subject moves to the first screenful of its surface:
- **Strategic Ledger.** A running mission's Cabinet block leads the Forces tab, and a binding ceiling leads the Economy tab.
- **Generals.**
  - A captured, captive or petitioning marshal is listed above the Emperor's card, with its state in the header.
  - The Emperor's card's first line is his state (in the field at X, at the seat, captive).
  - OUR DOCTRINE moves above the marshal cards.
- **Peace popups.** The Proposed Terms render directly under "Terms:", and the settlement table's per-court rows lead.
- **The wizard.** The Congress row collapses to one line above the court list (UXR3-28, 78).
- **The Diplomatic Ledger.**
  - A court's doctrine and laws lines lead its card.
  - On the Talleyrand book, the cooldown counsel leads (UXR3-29).
- **The region panel** leads with its ACTIONS block (recruit, build, repair chips), directly under the title line, and the province's name takes the Lead step (UXR3-76).
- **The rail's mission row** names itself beside its book icon ("Talleyrand at <court> — <kind>") and carries a "Recall" chip. The chip fills `Talleyrand, cancel mission` into the command line and never sends (UXR3-1, 18).
- **The top bar's Cabinet line** becomes a bordered chip in the Admiralty chip's style, which opens the Diplomatic Ledger's Talleyrand book (UXR3-2).
- **The tutor card in the war room** opens at 40 % of the HUD band's width (never under 520 px), its body at BodyLarge (UXR3-46).
- **A secondary-by-design subject** is re-read with its shot scrolled to it, and moves up only if that still reads ✗. This covers the dispatch's and the Moniteur's Congress clock (UXR3-19, 20) and the boot books' Cabinet block (UXR3-77).

**Part 5 — the rows found while reading and fixing** (UXR3-F1 … F10, X3, X4). Each lands by its own row's completion line. In particular:
- **F1:** the war-detail bar's minus reads on every losing bar.
- **F2:** the four-rank diorama's standards stand beside their own commanders.
- **F3:** no line is cut at a scroll's edge.
- **F8:** the fall clock is printed once.
- **F9:** each board stages its must_show; the enemy phase never prints "unknown".
- **F10:** the rail's overflow badge opens the hidden notices.
- **X3:** watch the driven grip proof in every hook. A second failure is investigated before the commit it blocks.
- **X4:** a source census pins every colour `main.gd` writes to the log to a palette token that reads ≥ 4.5 : 1 on the command window's panel.
- F11 stays S14's.

**Part 6 — the closing re-read.** It uses part 1's method on the final committed tree:
- fresh payloads;
- the whole manifest shot at five resolutions; any later fix's scenes re-shot and merged with `tools/uxr3_merge_index.py index`;
- the probe over every surface, any re-probe merged with `… probe`;
- the census, the fit report and the contrast report;
- THREE FRESH blind readers (Agent-tool subagents in one message), each given part 1's brief verbatim (`docs/audits/uxr3_s12/READER_BRIEF.md`, with {N} and {PACKET} filled);
- `tools/uxr3_review.py marks / packets / aggregate`;
- `tools/uxr3_reread.py --before docs/audits/uxr3 --after <records> --write --markdown …`.

Records go to `docs/audits/uxr3_s12b/` and frames with `--frames-dir docs/audits/uxr3_s12b/frames`. The write-up is `docs/audits/UXR3_REREAD2_2026_10_<day>.md`. Flip each row whose items all re-read ✓ to FIXED with its evidence.

**Decided in advance:**
- **The order:** Part 1 first, because the grip is the one cause on 81 surfaces. Then R6, the never-pressed controls, the boards, the found rows, and the closing re-read.
- **No item is waived.** S12's done-when is §UXR-3's: the top five groups at 8 of 8, none under 6, and every UXR3 row FIXED with evidence or re-homed with a reason.
  - A row that still reads ✗ after part 2's closing re-read is re-homed to **UXR-4 (S15)**, with its frames and the readers' reasons, for the user's eyes. The user's mark overrides the readers'.
  - A row is never closed by re-wording its completion.
- **A crash or a P1 found while fixing** heads the list. File it with the fix and the pin in the same commit.
- **The Side Desk (UXR-D4)** stays S12b's. Nothing here builds it.
- **F11** is S14's backend copy row. Do not touch it here.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Check `tasklist | grep -ci godot` before every start.
- **Never edit a client file while a probe or a shoot runs.** It mixes two trees in one record. The hook, too, runs Godot (the engine group), so start no engine during a commit.
- **The hook tests the working tree, not the index.** A later part's test edits parked in the tree fail an earlier part's commit. Copy them aside and restore them after.
- **`append_text` hides a label from the instruments.** Its `text` stays empty, so the contrast census and the probe see nothing in it. Write through `text`. Only the war-room log appends, by design.
- **`--only` matches substrings.** Check the selection with `iq10_run_captures.SHOTS` before a long run.
- **The probe's fresh instance must be fresh** (§113.3). Press the node the enumeration walked to, never a path lookup.
- **A real-time entrance needs `settle_ms`** (the main menu: 2.5 s).
- **The host rule** (§113.5): keep `war_room_boot` and `war_room_tutorial` in every probe run that probes a HUD piece.
- **An untracked test in `tests/` runs in the hook.** Park a test whose records do not exist yet outside `tests/` until its commit.
- **Capture windows take the user's keystrokes** when they open foreground. Read `stray_input` / `focus` before trusting a frame.
- **Never touch the user's live 8005 backend.** Run any backend on `SOVEREIGN_PORT=8006` with `INK_IRON_SAVE_DIR` set.
- **`PYTHONDONTWRITEBYTECODE=1`** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE`.
- **The hook** runs ruff and the full parallel suite (about 7 min; 30,837 tests at part 1's end). Commit with `run_in_background: true` from Bash, with a message file and never `--no-verify`. Read the log's `[pre-commit]` and `EXIT=` lines before believing a commit.
- **Shell.** Bash heredocs mangle backslashes and `\n` inside Python strings. Write scripts with the Write tool and run them by path.
- **Git:** never `git add -A`; stage by name. **Line endings:** normalise records to LF before committing.
- **The census** (`defect_census.py --open`) stars an open id that shares a line with ✅ or an upper-case closing word. Write closing words in lower case on any line that names an open id.
- **Docs caps.** `CLAUDE.md` ≤ 62,000 B (61,946 after part 1's swap). `STATUS.md` keeps seven ▶ blocks; the oldest goes to the top of `docs/archive/STATUS_2026_Q4.md`.

**Code-health rules in force:**
- A new font size is a theme step, not an override (`RAW_RATCHET` 1). A fixed-geometry step joins `Utils.TEXT_SIZE_FIXED_STEPS`.
- A grey is a named palette token (`utils.gd`); a body grey never sits under `COLOR_INFO`.
- A control that cannot act is disabled with its reason (`Utils.set_available`).
- A fix lands in the stage that owns it (`_attack_*`, `_strategic_*`, `_oneliner_*`, `_choice_*`, `_ratify_*`).

**The records the close carries:**
- `UX_UI_REVIEW_PLAN.md` §UXR-3: part 2's landing record.
- `PRE_DEPLOY_PLAN.md` §2: S12 struck.
- `STATUS.md` ▶ NEXT UP: a new block.
- `CLAUDE.md`: the LIVE STATE line.
- This file, rewritten for S12b (the Side Desk), with every decision made in it as this one was.

**Open with the user:** nothing. UXR-4 (their eyes at 5120×1440) is scheduled at S15 with the deploy.

**Do not:** edit `docs/UX_CHECKLIST_V1.json` (a new rule is a new file), change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a ratchet, or build the Side Desk.
