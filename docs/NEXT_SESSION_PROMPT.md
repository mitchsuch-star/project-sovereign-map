# NEXT SESSION PROMPT — Pre-Deploy S12: UXR-3 fixes (part 1 of 2)

> Overwritten each time a session hands off. Current hand-off: **October 13,
> 2026, after S11 (UXR-3, the review) closed.**
>
> The review read 145 surfaces × 8 items against the frozen
> `docs/UX_CHECKLIST_V1.json`: **787 ✓, 373 ✗**. It filed **84 rows** in
> `docs/BUG_FIXES.md` §UXR-3 — the review:
> - UXR3-1 … 73, one per ✗ class;
> - UXR3-F1 … F11, found while reading.
>
> Every row is S12's except F11 (S14's). The review is
> `docs/audits/UXR3_REVIEW_2026_10_13.md`.
>
> **Nothing waits on the user.** On October 13 the user said "make all
> decisions … nothing hanging". Every fork S12 can meet is decided below.
> UXR-4, the user's own eyes at 5120×1440, is at S15, and their marks override
> the readers'.
>
> **S12 is two sessions** (the S11 close re-sized it, `PRE_DEPLOY_PLAN.md` §2):
> - part 1 (this prompt): the class fixes;
> - part 2: the driven proofs, the per-board hierarchy, the found rows, and the
>   closing re-read.
>
> S12b (the Side Desk) follows. The Score Finish residue stays PAUSED until S14.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S12 part 1 — UXR-3 fixes, the classes.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S12.
- Work directly on master per `CLAUDE.md`, and commit and push each part.
- Run `git fetch origin` first and read `git log -5 --stat` before touching anything.
- **Every decision is already made** (the user's ruling, October 13, 2026: "make all decisions … nothing hanging"). This prompt is the approved plan:
  - Do not stop for Plan Mode approval, and do not pause between parts.
  - The rules under "Decided in advance" settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

**What this session is.** A FIX session:
- It fixes the review's rows by class, worst surfaces first.
- It re-reads every item it flipped against the SAME frozen checklist with the SAME tools.
- It records the re-read.

Read first:
- the review's §1–§6;
- `BUG_FIXES.md` §UXR-3 — the review;
- `SYSTEMS_REFERENCE.md` §113 (the instruments);
- `docs/audits/uxr3/review.json` (every surface's eight marks and why).

**Part 1 — the harness's gaps (UXR3-56, 57, 58).** Shoot the three popups the plan names and the manifest has never shot, under the checklist's ids: `objection_dialog`, `capture_choice`, `talleyrand_objection`.
- Each needs a payload capture in `tools/iq10_capture_payloads.py` and a `SHOTS` row in `tools/iq10_run_captures.py`.
- `objection_dialog` and `capture_choice` come from B4b's staged board (`tests/test_b4b_the_one_tail.py::_payloads`: an objection the player overrides, whose attack takes a province, and the Plunder / Secure question).
- `talleyrand_objection` comes from the dict shape `tests/test_deep_audit_session6.py` pins.
- Then read all eight items on each (the shoot, the probe, the census, the fit report, and three blind readers for R2/R5/R8). File any new ✗ beside its row.

**Part 2 — R3 Contrast, by token** (UXR3-3 … 6, 21, 22, 25, 32 … 35, 42, 47, 50 … 52).
- **Decided:** a body-class row never takes a dim step below the floor step `a0a0a8` (`Utils.DIM_FLOOR_INDEX`).
  - Every body use of `COLOR_DIM` (666670) and `COLOR_DIMMED` / `COLOR_GREY` (808080) becomes `COLOR_INFO`.
  - A caption-class row keeps `808080` only where it reads ≥ 3 : 1 on its panel.
  - High contrast still raises every step above.
- **Coloured text under the floor** keeps its hue and lightens until it reads ≥ 4.5 : 1 (body) or ≥ 3 : 1 (caption) on its own panel: `cd5c5c`, `cd6b6b` on `233043`, `b8332e`, `aa4444`. The war-detail side tags and the diorama's ⚔ go to full alpha in a lighter tint.
- This is a visible change of the default look. It is accepted under the review's R3 rule (the user's own decided standard), and UXR-4 judges it.
- Pin each new value in `tests/test_uxr2b_high_contrast.py`'s style.

**Part 3 — R5 / R6, the controls that answer nothing** (UXR3-12 … 14, 23, 37, 38, 43, 63, 67, 68, and R6's SILENT halves).
- **Decided** (honest availability): a control that cannot act in the current state is DISABLED, with its reason as a tooltip.
  - The active tab shows as selected and disabled ("You are reading this book") on both ledgers.
  - Execute is disabled while the command line is empty ("Type an order first").
  - Zoom out is disabled at the minimum zoom; Fit Europe is disabled at the fit.
  - Connect is disabled with no key; Disconnect is disabled while not connected.
  - The menu's Settings button closes Settings when it is open (it answers).
- **The readers' inert-looking controls:**
  - The war HUD's header and war rows get button chrome (a hover fill and the pointing hand).
  - Underlined text that is not a link loses its underline: the coalition view's member rows, and the settlement table's names and "+ Add demand" unless they become real chips.
  - The dispatch's TODAY orders become chips that type their order into the command line.
  - The mailbox's petition row gets a press.
  - The title screen's disabled campaign buttons say why ("Waiting for the game's server…").

**Part 4 — R4 Consistency, by file** (UXR3-7 … 11, 26, 36, 48, 49, 53, 54, 60 … 62, 64 … 66, 72). Every hit's file and source line is in `docs/audits/uxr3/consistency.json`.
- **Decided:**
  - A code grey takes the palette token of its value (within ±1/255). Where none exists, it takes a NEW named token in `utils.gd`'s palette block, with no visual change.
  - A scene grey off the dim ladder moves to the nearest ladder step at or above it: a change of one step at most, accepted.
  - The 11 raw sizes (`main_menu.gd` 5, `battle_diorama.gd` 5, `europe_map_smoke.gd` 1) become named theme steps; the two BBCode sizes become a Label on a theme step. The smoke scene is the developer's, and its 1 may stay.
  - Lower `RAW_RATCHET` (11 → 1) and `BBCODE_SIZE_RATCHET` (2 → 0) in `tests/test_uxr2_override_diet.py`, with the ladder pin extended.
- **The map renderer's 29 greys** take named `Utils.MAP_*` tokens, values unchanged.

**Part 5 — re-read what flipped, and close.**
- Re-capture the payloads.
- Shoot the changed scenes' surfaces at the five resolutions: one engine, `--only` per scene, merged into a fresh whole-manifest index.
- Re-run the census, the fit report, the contrast report and the probe on them.
- Run THREE FRESH blind readers (Agent-tool subagents in one message, the S11 packet's brief) for the R2/R5/R8 marks of changed surfaces.
- Aggregate with `tools/uxr3_review.py`.
- Write `docs/audits/UXR3_REREAD_2026_10_<day>.md`: what flipped, the new scores, the group table.
- Flip each row whose items all re-read ✓ to FIXED, with the commit and the re-read's evidence.
- Leave the rest OPEN for part 2.

**Decided in advance:**
- **The order.** Part 1 first (the gaps are the three worst). Then R3, R5/R6's inert controls, and R4: each is one class and closes rows across all ten groups. Part 2 owns R6's hand-off proofs, the R2/R8 per-board fixes, F1 … F10 and the closing re-read.
- **R6 hand-offs are part 2's.** The proof is a war-room mode of the action probe. It opens each hand-off surface INSIDE the real `main.tscn` against a sandboxed backend (`SOVEREIGN_PORT=8006`, `INK_IRON_SAVE_DIR` set), presses the control, and reads the war room's visible answer within 500 ms: the terminal's echo, a popup, the map. A proven road is cited in `docs/audits/uxr3/live_citations.json`. A road with no visible answer gets an in-surface echo: the chip greys to "Sent: <order>", or the screen closes onto the terminal's echo.
- **The never-pressed controls are part 2's.** Save, Load, New Campaign, Main Menu and Quit are proven by driven tests against a sandboxed backend:
  - Save and Load through the real save road;
  - Main Menu and New Campaign by a harness that sees `main_menu.tscn` stand after the change;
  - Quit by a quit-intercept pin.
- **R2 board subjects are part 2's.** A LIVE subject moves to the first screenful of its surface:
  - a running mission's Cabinet block leads the Forces tab;
  - a binding ceiling leads the Economy tab;
  - the Generals screen lists a captured, captive or petitioning marshal above the Emperor's card, with the state in its header;
  - the Proposed Terms render directly under "Terms:";
  - the settlement table's per-court rows lead;
  - the wizard's Congress row collapses to one line above the court list.
  - A secondary-by-design subject (a clock line in the dispatch, a column in the Moniteur) is re-read with its shot scrolled to it, and moves up only if that still reads ✗.
- **No item is waived.** S12's done-when is §UXR-3's: the top five groups at 8 of 8, none under 6 — and every UXR3 row FIXED with evidence or re-homed with a reason.
- **R4's reader notes** (84, in `review.json`) do not score. Their defects are filed as F1 … F10 and fixed in part 2.
- **F11** ("50 of 45 titled provinces") is S14's backend copy row. Do not touch it here.
- **The Side Desk (UXR-D4)** stays S12b's. Nothing here builds it.
- **A crash or a P1 found while fixing** heads the list. File it with the fix and the pin in the same commit.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Before starting one, check that none is running (`tasklist | grep -ci godot`); a background run started earlier may still hold one. S11 overlapped two probe runs by forgetting a resumed engine.
- **The probe's fresh instance must be fresh.** It restores the settings and the scale before every open (§113.3). Code-built buttons share normalised paths, so press the node the enumeration walked to.
- **A real-time entrance needs `settle_ms`.** Off-screen frames are not time; the main menu needs 2.5 s.
- **The host rule** (§113.5): a HUD piece shot alone reads its war-room record. Keep `war_room_boot` and `war_room_tutorial` in every probe run that probes the top bar, the war HUD, the rail or the tutor card.
- **An untracked test in `tests/` runs in the hook.** Park a test whose records do not exist yet outside `tests/` until its commit.
- **Capture windows take the user's keystrokes** when they open foreground. Read `stray_input` / `focus` before trusting a frame.
- **Never touch the user's live 8005 backend.**
  - A driven harness stubs its api clients (the top bar's too) and refuses `:8005`.
  - Run any backend you need with `SOVEREIGN_PORT=8006` and `INK_IRON_SAVE_DIR` set.
- **A headless root viewport is 64×64.** A driven layout harness needs `--windowed --resolution 1600x900 --position 5200,20`, and `root.mode/size` set on its first tick.
- **`PYTHONDONTWRITEBYTECODE=1` in the shell** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE`.
- **The hook** runs ruff and the full parallel suite (about 7½ min; 30,785 tests at S11's Part 3).
  - Commit with `run_in_background: true` from Bash, using a message file and never `--no-verify`.
  - Make no tracked edit while it runs.
  - Read the hook log's `[pre-commit]` and `EXIT=` lines before believing a commit.
- **Shell.** A Bash heredoc mangles backslashes. Write scripts with the Write tool and run them by path.
- **Git.** Never `git add -A`; stage by name.
- **Line endings.** Python's `write_text` on Windows writes CRLF; normalise records to LF before committing. An edit script must detect the file's own newline.
- **Docs caps.**
  - `CLAUDE.md` must stay ≤ 62,000 B: pay for every new word by trimming the oldest LIVE STATE row.
  - `STATUS.md` keeps seven ▶ blocks at most; the oldest goes to `docs/archive/STATUS_2026_Q4.md`, newest first.

**Code-health rules in force:**
- A new font size is a theme step, not an override (`RAW_RATCHET`). Any dim grey goes through `Utils.toned` / `toned_hex` / the COLOR tokens.
- A fix lands in the stage that owns it:
  - a combat fix in its `_attack_<stage>`;
  - a standing-order fix in its `_strategic_<stage>`;
  - a log line in its `_oneliner_<family>`;
  - a dialogue answer in its `_choice_<family>`;
  - a ratification clause in its `_ratify_<stage>`.
- A new lever lives one session past its attribution, then retires at the next slice's head (`tools/retire_lever.py`).

**The records the close carries:**
- `UX_UI_REVIEW_PLAN.md` §UXR-3: the part 1 landing record.
- `PRE_DEPLOY_PLAN.md` §2: the S12 row, with part 1 struck.
- `STATUS.md` ▶ NEXT UP: a new S12 block.
- `CLAUDE.md`: the LIVE STATE line.
- This file, rewritten for S12 part 2, with every decision made in it as this one was.

**Open with the user:** nothing. UXR-4 (their eyes at 5120×1440) is scheduled at S15 with the deploy.

**Do not:** edit `docs/UX_CHECKLIST_V1.json` (a new rule is a new file), change balance, re-score, touch the Score Finish residue, add a lever, weaken a gate or a ratchet, or build the Side Desk.
