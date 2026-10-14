# NEXT SESSION PROMPT — Pre-Deploy S13: DD-B "The fresh-eyes campaign"

> Overwritten each time a session hands off. Current hand-off: **October 14,
> 2026, after S12b (UXR-D4 "The Side Desk", with UXR-X28 at its head) closed.**
>
> S12b landed in four commits on master and the close:
> - **UXR-X28:** the map's furniture went from 71 overlaps to 0 at five
>   resolutions, with the dock closed and open (`docs/audits/uxr_d4/map_census.json`).
> - **UXR-D4:** the six layer-50 screens pin non-modal in the right third.
>   The HUD and the map's whole-Europe view give the dock its third. The
>   pinned screen re-reads after every command and every end turn.
> - **The proof:** a driven run of the real client against a sandboxed backend
>   (`tools/uxr_d4_side_desk_harness.gd`) and the census at five resolutions,
>   both clean. Rules are in `SYSTEMS_REFERENCE.md` §114.
>
> **Nothing waits on the user.** On October 13 the user said "make all
> decisions … nothing hanging". Every fork this session can meet is decided
> below. UXR-4, the user's own eyes at 5120×1440, is at S15. It now also
> reads the Side Desk's and the map's frames.
>
> Paste everything below the line as the opening message of a fresh session.

---

**Pre-Deploy S13 — DD-B "The fresh-eyes campaign": three campaigns played IN THE CLIENT at 5120×1440 by players who have not read the ledgers, one road each (conquest, diplomacy-first, the sea), every confusion filed as a row with a frame.** Routing authority is `docs/PRE_DEPLOY_PLAN.md` §2, row S13, and its DD-B section ("The fresh-eyes campaign"): the weak spot is 16.5 defect rows per 10 hand-played turns against 0.4 scripted.
- Work directly on master per `CLAUDE.md`, and commit and push each slice.
- Run `git fetch origin` first and read `git log -8 --stat` before touching anything.
- **Every decision is already made** (the user's ruling, October 13, 2026: "make all decisions … nothing hanging"). This prompt is the approved plan:
  - Do not stop for Plan Mode approval, and do not pause between slices.
  - The rules under each slice settle every fork; ask the user nothing.
- **The head:** a CODE-1 lever batch runs only if the session starts on or after November 1, 2026 (the November batch). Before then there is none.

Read first:
- `PRE_DEPLOY_PLAN.md` §2 (rows S13–S15) and the DD-B section;
- `docs/PLAYTESTING.md` Mode C (the full client) and "Scoring a build";
- `SYSTEMS_REFERENCE.md` §114.7 (the Side Desk's driven harness, which this session's instrument grows from), §113.3 (the action probe's war-room mode and its traps);
- `tools/uxr_d4_side_desk_harness.gd` and `tools/uxr3_action_probe.py` (`start_backend`, `stop_backend`);
- `tools/_score_probes.py`: the ONE judge's regexes for a typed line's reply (`ACTION_WORDS`, `BOARD_GATE_RX`, `ASKED_RX`, `REFUSED_RX`, `SHRUG_RX`).

**Slice 1 — the instrument: a player's hands on the real client.** The players see exactly what a player sees, and act only as a player can.
- **`tools/dd_b_client.gd`** (a SceneTree script, grown from the Side Desk harness's rails):
  - It boots the game as it launches: the title screen, `main_menu.tscn`, whose real client talks to the sandboxed backend.
  - The window is 5120×1440, parked past the desktop at x 5200, at the Interface Scale a player there gets: `derive_ui_scale` gives 1.4, held in an in-memory `UiSettings` with `_persist` false.
  - It starts from a FIRST launch: the scale card, the parser hint and the tutor are not marked seen, as a new player has them.
  - It refuses the player's 8005.
- **It polls `<run>/inbox/NNNN.json`** for one action at a time. For each action it:
  - runs it as a player would, through real input events (`push_input`) or the control's own road;
  - settles: the API is idle, then 20 frames, then 600 ms of real time (entrances animate in real time);
  - writes `<run>/frames/NNNN.png` (the full frame), `<run>/frames/NNNN_view.jpg` (2560 wide, for reading) and `<run>/state/NNNN.json`.
- **The state record** holds every visible text row with its rect and layer; every visible button with its text, rect and disabled state; which screens, popups and the region panel are open; the focus; the command window's last 12 lines.
- **The actions:**
  - `type <text>`: the command line takes the text and Enter;
  - `click <words>`: the one visible control (a button, a chip, a `[url]` link) whose text holds the words, pressed by a real click at its centre. It is an error when none or several match; the error names the candidates, and `click#N <words>` picks one;
  - `click_at <x> <y>`: logical px, read off the view JPEG ×1.4 (the record states the factor);
  - `key <K>`: Escape, Enter, T, Alt+T, F1 and so on;
  - `scroll <x> <y> up|down <n>`;
  - `look`: no action, a fresh frame.
- **`tools/dd_b_play.py`**:
  - `start --road <conquest|diplomacy|sea> --out <run>` starts a sandboxed backend with `uxr3_action_probe.start_backend`: an unused port from 8006 (never 8005), `<run>/saves`, the mock parser, the historical seed. It then starts the ONE engine.
  - `act --out <run> "<action>"` writes the inbox file and waits for the state (120 s). It prints the view JPEG's path and a compact summary: the open surfaces and their lines, any popup's title and buttons, the command window's tail, the turn.
  - `stop --out <run>` quits the engine, stops the backend and writes `<run>/run.json` (the turn reached, the actions, the durations, the engine's SCRIPT ERROR lines).
- **Test:** `tests/test_dd_b_the_client_hands.py` drives a short script through `dd_b_play.py`:
  - title → Begin → the war room → T → Pin → `type end turn` → the enemy phase → Continue → Esc;
  - it asserts each state record shows what the action should have changed;
  - it joins `ENGINE_GROUP_MODULES` and skips without the engine.

**Slice 2 — the three campaigns.** Three general-purpose subagents, ONE AT A TIME (never two engines at once), each launched with the brief below and nothing else.
- Each plays **20 turns** on its road against its own fresh backend:
  1. **conquest** — "win the war in the field; take Vienna";
  2. **diplomacy-first** — "end the war at the table before fighting it out; make the peace or the alliances you need";
  3. **the sea** — "make the navy count: break the blockade, raise Ireland, or carry the war across the Channel".
- **The brief** is written into `docs/audits/dd_b/PLAYER_BRIEF.md` before the first launch and given verbatim:
  - You are a strategy-game player new to *Ink & Iron*. You know only what the game shows you.
  - You may run only `tools/dd_b_play.py act --out <your run>` and read only your own run directory (the view JPEGs, the state files).
  - You may not read any other repository file, any doc, or any other run.
  - Play as a player would: read the screens, use the tutor, the ledgers and the Side Desk when you want them, and type orders in your own words.
- **The rows.** Each player files every confusion in `<run>/rows.json`: the turn, the action number, the frame, what they did, what they expected, what they saw, and a severity:
  - **P1**: they could not go on; or the game did something they did not order; or it lost their work;
  - **P2**: it cost them a turn, or misled them into a choice they could undo;
  - **P3**: friction, copy or layout.
- **The judge.** After each run, every typed line and its reply is classified by the ONE judge in `tools/_score_probes.py` (extend it there if a reply's shape is new, never inline). A misread or an executed-when-refusal-meant reply is a P1 row by itself, merged with the player's row on the same line if there is one.
- **Records:** `docs/audits/dd_b/<road>/`, holding `actions.log`, `rows.json`, `run.json`, the summaries, and the frames each row cites as JPEG crops; never the full PNGs.

**Slice 3 — the reading, the rows and the close.**
- **De-duplicate across the three roads.** One cause on several sightings is one row that names every sighting and its frame.
- **File the rows in `BUG_FIXES.md` §DD-B.** Each row carries its owner, landing slice, completion definition, STATUS line and behavior test (Golden Rule 9), and the tag `⟨SF step=pre-deploy S13 · DD-B · pillar=…⟩`. A row with no tag aborts the hook.
- **The metric:** rows per 10 turns by severity, per road and across the three.
- **Done when:** under **5 rows per 10 turns** and **0 P1** across the three roads. Otherwise every row is filed and homed. The homing rule:
  - client and copy rows go to a new Pre-Deploy row **S13b "DD-B fixes"**, sized at the close by the count, P1s first;
  - backend design questions go to `DESIGN_REFINEMENT.md` with a recommendation, for the user at S15;
  - nothing is fixed in S13 itself, except a defect that blocks the instrument.
- **The write-up:** `docs/audits/DD_B_FRESH_EYES_<date>.md`.
- **Budget:** 1.5 sessions. If the session ends before the third road, the hand-off names the next road and keeps every decision made.

**The records the close carries:**
- `PRE_DEPLOY_PLAN.md` §2: S13 struck, S13b added and sized;
- `STATUS.md` ▶ NEXT UP: a new block (seven kept; the oldest to the top of `docs/archive/STATUS_2026_Q4.md`);
- `CLAUDE.md`: the LIVE STATE line (≤ 62,000 B: it stands at 61,975, so trim another line as you add one);
- this file, rewritten for S13b (or for S14 if DD-B's done-when is met), with every decision made in it.

**Traps — earlier sessions paid for each of these:**
- **Never run two Godot engines at once.** Check `tasklist | grep -ci godot` before every start. The hook runs Godot too (the engine group): start no engine during a commit.
- **Never touch the user's live 8005 backend.** Run any backend on `SOVEREIGN_PORT=8006` or above with `INK_IRON_SAVE_DIR` set; `start_backend` does both.
- **The hook tests the working tree, not the index.** Park a later slice's test edits outside `tests/` before committing an earlier slice; an untracked test in `tests/` runs in the hook. Do not edit files the tests read while a commit's hook runs.
- **`PYTHONDONTWRITEBYTECODE=1`** fails two stale-bytecode pins. Run pytest and `git commit` with `env -u PYTHONDONTWRITEBYTECODE`.
- **The hook** runs ruff and the full parallel suite (about 6:15; 30,966 tests at S12b's end). Commit with `run_in_background: true` from Bash, with a message file and never `--no-verify`. Read the log's `[pre-commit]` and `EXIT=` lines before believing a commit.
  - **The G4 timing pin can fail under the hook's load** (`test_scale_readiness_phase2.py::test_g4_turn_resolution_map_cost_within_2x_baseline`: 12.8 ms against a 12.0 ms budget, on a client-only commit). Re-run it alone (0.8 s); if it passes, re-commit unchanged.
- **Shell:**
  - Bash heredocs mangle backslashes, and a Python script piped on stdin is decoded as cp1252, so a "…" or a "→" in it breaks a match. Write scripts with the Write tool and run them with `-X utf8`.
  - GDScript `:=` cannot infer from an untyped value (`var x := untyped == y`, or `var b := untyped.method()`): type such locals explicitly. S12b hit it twice.
- **The live backend's rolls differ from the in-process TestClient's.** Ney objected to "Ney, fortify" in-process and complied live. A driven run must handle either answer; it must never script one.
- **A popup chain is longer than its first popup.** The end turn's enemy phase raised the battle tableau behind it. Answer modals until none stands, and record each answer.
- **A camera moved in code redraws the map's names only after the camera writes its transform** (fixed in S12b; for a harness, wait frames after a programmatic move before reading the map).
- **A new client test that drives the engine joins `ENGINE_GROUP_MODULES`**, or two workers fight over one window.
- **Git:** never `git add -A`; stage by name. **Line endings:** normalise records to LF before committing.
- **Docs caps.** `CLAUDE.md` ≤ 62,000 B. `STATUS.md` keeps seven ▶ blocks.

**Code-health rules in force:**
- A new font size is a theme step, not an override (`RAW_RATCHET` 1). A grey is a named palette token. A control that cannot act is disabled with its reason (`Utils.set_available`).
- A fix lands in the stage that owns it (`_attack_*`, `_strategic_*`, `_oneliner_*`, `_choice_*`, `_ratify_*`).

**Open with the user:** nothing. UXR-4 (their eyes at 5120×1440, S15) reads S12's eleven R2 marks and S12b's frames (`docs/audits/uxr_d4/`).

**Do not:**
- edit `docs/UX_CHECKLIST_V1.json`;
- change balance, re-score, add a lever, or weaken a gate or a ratchet;
- touch the Score Finish residue or start S14;
- let a player read the ledgers or the docs.
