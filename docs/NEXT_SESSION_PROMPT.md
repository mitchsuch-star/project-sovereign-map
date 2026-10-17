# NEXT SESSION PROMPT — Pre-Deploy S13c part 3: CC-5 "The war table"

> Overwritten each time a session hands off. Current hand-over: **October 17, 2026, after S13c part 2 (CC-3)
> landed** (one commit on master through the hook).
>
> **What part 2 delivered** (`SYSTEMS_REFERENCE.md` §128; pins `tests/test_cc3_select_click_enter.py`, 67, driven
> by `tools/cc_client_harness.gd`):
> - **Select, click, Enter:** on an EMPTY line a plain click on a piece of ours selects him (`main._select_marshal`):
>   the ring (`scenes/map_order_layer.gd`, screen-space), the strip (`_render_order_strip`, over the map's controls),
>   the ETA tint (`map_renderer_base.REACH_FILL_SHADER` / `reach_fill_layer`, bands this turn · 1 · 2–3 · 4+), the
>   ghost road under the cursor (the reach's road, then the exact quote's after a 0.15 s rest — `_order_quotes`, one
>   GET a target for the selection's life). A click opens the **confirm card** (`scripts/order_confirm_card.gd`,
>   dialog_manager `"order_card"`, layer 123; it takes EVERY key in `_input`; `refit` places it clear of the road and
>   the strip) on the exact quote; [Send] is `_send_map_order` (the typed road), [Put in line] CC-0's offer.
> - **Drag:** `map_renderer_base._arm_piece_drag` / `_release_piece_drag` — a press on our piece waits; 8 px
>   (`PIECE_DRAG_THRESHOLD_PX`) is a drag (`piece_drag_started` → selected), a drop is `piece_dropped` (the card), open
>   water / a panel / Esc is `piece_drag_cancelled`.
> - **The backend (read-only):** `WorldState.weighted_paths_from` (one Dijkstra for every end, pinned equal to
>   `find_weighted_path`), `strategic.march_roads` (the ladder per rung, the avoid-set once; `road_verdict` and
>   `_march_road_from_path` extracted, pinned equal to `march_road`), `order_quotes.march_reach` (pinned equal to
>   `march_quote`), **`GET /march_reach?marshal=`**, **`GET /march_quotes?marshal=&dest=|enemy=|ally=`**.
> - **The siblings:** CC-X11 (a fog chip's enemy is the attack's target — `last_click_fogged`), CC-X12 (a line filled
>   by code lets the selection go — `_refresh_send_button`), CC-X13 (a restored terminal stands on its newest line).
> - **The walk:** `tools/cc3_mode_c_walk.gd` (seven frames, `docs/audits/cc3_client/`).
>
> **The seams CC-5 builds on (and must not break):** the selection lives only beside an empty line and is let go on
> every send / screen / modal / world swap (`_clear_order_selection`); the order layer draws in screen space and
> re-projects on every camera move (`_process` compares the projection) — the order arrows are a second pass there;
> the card is modal and takes every key; `_order_target_key` is the one reading of what a click names.
>
> **Traps part 2 paid for:**
> - `tools/cc_client_harness.gd`: CC-1's scenario c10 EMPTIES `marshal_hitboxes` — re-feed the board
>   (`_update_map_from_game_state`) before anything reads pieces; headless, the root is 64 px square (set
>   `root.size` before pushing mouse events) and the map stays hidden (the stub never answers `/map_topology` — set
>   `visible`); push a mouse motion TWICE (the map reads the control the GUI hovered on the previous motion).
> - A container's minimum size before its first layout reads a wrapping label at width 0 (the card measured
>   1,483 px tall): lay the label out at its width and sum the rows (`order_confirm_card._content_height`).
> - `tests/test_uxr3_s12_fixes.py` censuses every `[color=#…]` in `main.gd` as a palette token — compose any other
>   colour where it lives (the band legend is `map_renderer_base.order_band_legend_bbcode`); FA-94 censuses
>   `esc_control()` overrides (a popup that reads its own Esc in `_input` needs none).
> - `TaskStop` on a backgrounded `python -m backend.main` ends the shell, NOT the server: the walk's second run was
>   served by the first backend (the board already moved). Start the sandbox with PowerShell `Start-Process
>   -PassThru` and stop the process that LISTENS on the port (`netstat -ano`), then check the port is free.
> - `docs/STATUS.md` holds at most seven `> **▶ ▶ ▶` entries (`tests/test_code4_docs_diet.py`) — move the oldest,
>   verbatim, to the top of `docs/archive/STATUS_2026_Q4.md`.
>
> **Nothing waits on the user before CC-5** (UXR-4, the code-signing certificate and AO's three questions are theirs
> before S15, not before this part). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S13c part 3 — CC-5 "The war table" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (S13c part 2, CC-3, has landed; read `git log -1` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP (the CC-5 block), the plan `~/.claude/plans/sorted-yawning-clover.md` §CC-5, `docs/SYSTEMS_REFERENCE.md` §119 (CC-0/1), §121 (CC-2, the quotes), §125 (AO: FOLLOW, the fan-out, the army order — `backend/commands/group_orders.py`) and §128 (CC-3: the selection, the order layer, the card, the drag), and `docs/BUG_FIXES.md` §CC.

Scope, in order:
1. The remaining road: every standing order's remaining road on the player-only `tactical_state` (derived — no save field), with a backend pin that only our corps carry it (the fog boundary).
2. The order arrows: every standing order of ours drawn on `scenes/map_order_layer.gd` as a dashed arrow along its remaining road with an ETA badge (HOLD an anchor, SUPPORT / FOLLOW a line to the friend); a click on an arrow opens a card — [Cancel (1 AP)] through the existing `/cancel_order`, or [Change], which selects him (CC-3's `_select_marshal`).
3. The next idle marshal: `.` (Alt+`.` while typing) cycles our corps with no standing order and no fortify / drill / square, centres the camera and selects him; the help and the School teach it.
4. Group orders: Ctrl-click adds our pieces to a group; a province click opens ONE card with a line per corps (each its own quote) and the summed actions against the pool; Send stops at the first objection, refusal or popup ("2 of 3 sent — Lannes refused: …"). At the part's head, verify whether the named-list address the AO fan-out already reads (`Ney, Davout and Soult, march to Swabia`) can BE the card's Send — one road, no client sequencer; if it cannot, the landing record says why.

Method: drive it on the real client with `tools/cc_client_harness.gd` (an arrow for every standing order and none for an enemy, the Cancel / Change card, the idle cycle skipping the busy, the group card's sum and its stop rule); the CC-2 drift census stays byte-identical; the Godot parse harness EXIT 0 (commit the refreshed `tools/godot_parse_report.json`); a Mode C walk on `SOVEREIGN_PORT=8007` (never 8005 / 8006; `INK_IRON_SAVE_DIR` in the scratchpad) on `tools/cc3_mode_c_walk.gd`'s pattern shows the arrows, `.` and a group order. Sibling sweep after each fix — file from CC-X14. A series attribution only if a change reaches the AI (it should not).

Rules: shared checkout — never stash, reset or switch branches; commit only your own files by explicit path with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>` in the background (the hook runs ruff and the full suite, about 7 minutes); never `--no-verify`; a moved pin is re-seated with its row named.

Close with: docs updated (`SYSTEMS_REFERENCE.md` §129, `BUG_FIXES.md` §CC rows, `PRE_DEPLOY_PLAN.md` §2 S13c, STATUS ▶ NEXT UP naming S13c part 4 (CC-4 "Chained orders", CC-X6 / X7 / X9 at its head) next with its prompt pre-decided and the ▶▶▶ entries kept, `NEXT_SESSION_PROMPT.md` hand-over); one commit through the hook; the report opens with the commit SHA.

Done when: the plan's CC-5 tests pass through the hook; the walk shows the arrows, `.` and a group order; the drift census holds; 0 OPEN §CC rows homed to CC-5.
