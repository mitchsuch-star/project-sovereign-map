# NEXT SESSION PROMPT — Pre-Deploy S13c part 4: CC-4 "Chained orders"

> Overwritten each time a session hands off. Current hand-over: **October 18, 2026, after S13c part 3 (CC-5)
> landed** (one commit on master through the hook).
>
> **What part 3 delivered** (`SYSTEMS_REFERENCE.md` §129; pins `tests/test_cc5_the_war_table.py`, 40, the
> client driven by `tools/cc_client_harness.gd`):
> - **The remaining road:** `strategic.standing_order_road` on the player-only `tactical_state.order_road` —
>   `remaining_road` (`order.path` with the province he stands in stripped from its head), the one clock's road arm
>   (`road_turns_remaining`, extracted from `order_turns_remaining`), where it is bound, the halt, the cancel's
>   price and trust (`strategic_executor.cancel_trust_change`, the executor's own rule). Derived, never saved, no
>   pathfinding; no enemy corps carries it.
> - **The arrows:** `map_renderer_base._refresh_order_arrows` (rebuilt with the hit boxes) → `map_order_layer`'s
>   second pass (dashed road, head or anchor, the ETA badge, badges bound for one province stepped apart,
>   `arrow_at` for the click). The card's ARROW face (`open_standing_card`): [Cancel order] →
>   `main._send_cancel_order` → POST `/cancel_order` (ONE cancel road — the Orders tab's rides it, CC-X15),
>   [Change] (Enter) → `_select_marshal`.
> - **`.`:** `main._cycle_idle_marshal` at three doors (the bare key off the line, a bare `.` on an EMPTY focused
>   line, Alt+`.` while typing); `map_renderer_base.focus_on_marshal`.
> - **Groups:** Ctrl-click (`_click_groups_a_marshal`, `_set_order_group`; rings via `set_order_group`) → a
>   province → the card's GROUP face on `GET /march_quotes?marshals=…&dest=…` (`order_quotes.group_march_quotes`)
>   → Send = `_send_group_orders`, one line at a time down the typed road, stopping at the first question or
>   refusal. The named-list line is NOT that road: CQ-8's relay by ruling (pinned —
>   `TestTheNamedListIsCQ8sRelay`), which is why CF-9 is re-opened as **CC-X17** for this part.
> - **The siblings:** CC-X14 (the literal detour in the quote and the reach — `order_quotes.literal_detour`,
>   `_literal_detours`), CC-X15 (one cancel road), CC-X16 (`order_turns_remaining(…, location=)` — the stale road
>   head on the Orders tab, the dispatch, the desk and the relay).
>
> **The seams CC-4 builds on (and must not break):** the relay (`backend/commands/relay.py` — one tail, one
> command's life, never auto-sent: CR-7-8); `_handle_move_to_arrival` (`strategic.py`) where an `arrival_verb` will
> run; `strategic_executor._handle_strategic_objection_from_endpoint` (Compromise, CC-X7); the arrows read
> `order_road` — a new order shape (an arrival verb, a contingency) must still draw (add its words to
> `map_renderer_base.order_arrow_label` and the card's `standing_headline` if it needs them).
>
> **Traps part 3 paid for:**
> - `tools/cc_client_harness.gd` holds every send / cancel / group-GET callback now (`answer_send`, `held`); a
>   scenario answers each with the REAL backend's reply, built in the pytest on a world rebuilt the same way
>   (`_table` in `tests/test_cc5_the_war_table.py`). The harness has a `_frames` COUNTER — a coroutine helper must
>   be named otherwise (`_wait_frames`). A spec with `cc5_only` runs CC-5 alone on a 1600×900 root.
> - The flat mood (`_flat`): with it Ney OBJECTS to `fortify`; a named list whose first man must simply spend
>   leads with the Emperor (a sovereign never objects).
> - `strategic_order_ap`: a march is 2, 1 for a literal man or the Emperor; a cancel is 1; four actions a turn —
>   a Mode C walk that gives orders and cancels must fit one turn (no debug refill exists).
> - At the whole-Europe fit the camera is clamped and cannot turn to anyone: zoom in before checking a focus.
> - `CLAUDE.md` stands within ~150 bytes of its 62,000-byte cap (`tests/test_code_health_ratchet.py`): swap its
>   live-state rows, never grow them.
> - The bash heredoc mangles some GDScript/Python payloads (quotes, tabs): write scripts with the Write tool.
> - `TaskStop` leaves a backgrounded backend alive: start the sandbox with PowerShell `Start-Process -PassThru`,
>   stop the PID that LISTENS on 8007 (`netstat -ano`), check the port is free.
>
> **Nothing waits on the user before CC-4** (UXR-4, the code-signing certificate and AO's three questions are
> theirs before S15). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S13c part 4 — CC-4 "Chained orders" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (S13c part 3, CC-5, has landed; read `git log -1` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP (the CC-4 block), the plan `~/.claude/plans/sorted-yawning-clover.md` §CC-4 and its decisions D6–D8, `docs/SYSTEMS_REFERENCE.md` §4 Stage 2c (the relay), §119, §121, §125, §128 and §129, and `docs/BUG_FIXES.md` §CC and §CF (CF-5).

Scope, in order:
1. The head — each reproduced before its fix, its sibling sweep after: CC-X6 (`hold … until Davout arrives then attack` drops the attack in silence — relayed and named), CC-X7 (Compromise keeps the typed condition, merged as whichever-first), CC-X9 (a PURSUE outliving its destroyed quarry — reproduce or strike with the reason), CC-X17 (a typed named list relays every further name in turn for the seal, never spent — CQ-8; re-seat `tests/test_cc5_the_war_table.py::TestTheNamedListIsCQ8sRelay` with the row named).
2. The arrival verb (D7): `march to Vienna then fortify | hold | drill | defend` sets `arrival_verb` (a new `StrategicOrder` field, default None), executed by `_handle_move_to_arrival`; the march paid once; CF-5.
3. The contradiction (D6): a refused tail suggests the legal order where the relay predicate allows ("Ney can't attack once fortified — 'Ney, attack Mack then fortify'?"); the relay stays the player's seal.
4. The contingency (D8): `Ney, if Mack advances fall back to Bohemia` / `… if the enemy comes within reach, attack` — a HOLD with its own `contingency {who, then}` field; HOLD's price at issue, free when it fires; it watches only the hold province and its neighbours in the holder's own sight; evaluated at the strategic phase after the enemy phase; the objection asked at issue only; the `if` refusal lifted for this pattern only (`when` / `once` / `in case` stay refused, pinned by negative corpus rows); the identity check counts the contingency; it warns on a fortified or marching holder. The AI issues no standing orders (a Rule-5 note).
5. The parser rider: corpus rows, `python -m tools.gen_routed_order_words`, a `prompt_builder.py` few-shot, serialization (`tests/test_serialization_enforcement.py`, `SAVE_FORMAT_REFERENCE.md`), the help.

Method: pins in `tests/test_cc4_chained_orders.py` (each arrival verb; the contingency fires on a seen approach and never on a fogged one; AP paid once and nothing charged when it fires; Compromise keeps the condition; the honest then-attack tail; the contradiction suggestion; a save round-trip); the driven attribution arms byte-identical to `BASELINE_SERIES`, or each movement attributed and named; CC-2's drift census unchanged; the Godot parse harness EXIT 0 if any `.gd` changes (commit the refreshed `tools/godot_parse_report.json`); a Mode C check on `SOVEREIGN_PORT=8007` (never 8005 / 8006; `INK_IRON_SAVE_DIR` in the scratchpad): `march to X then fortify` arriving and fortifying, a contingency firing on a seen approach, both on the war table. Moved pins re-seated with their reasons (corpus `parseneg-until-then-attack-holds`, `test_cr7_1`'s until-then rows, `test_cr7_3`'s tail rows). Sibling sweep after each fix — file from CC-X18.

Rules: shared checkout — never stash, reset or switch branches; commit only your own files by explicit path with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>` in the background (the hook runs ruff and the full suite, about 7 minutes); never `--no-verify`; a moved pin is re-seated with its row named. The user's own game may be running from this checkout on port 8005 — never stop, restart or send commands to it; your sandbox backend runs on 8007 only.

Close with: docs updated (`SYSTEMS_REFERENCE.md` §130, `BUG_FIXES.md` §CC rows, `PRE_DEPLOY_PLAN.md` §2 S13c (row CC complete), STATUS ▶ NEXT UP naming S13b part 4 next with its prompt pre-decided and at most seven ▶▶▶ entries kept (move the oldest verbatim to the top of `docs/archive/STATUS_2026_Q4.md`), `NEXT_SESSION_PROMPT.md` hand-over); one commit through the hook; the report opens with the commit SHA.

Done when: the plan's CC-4 tests pass through the hook; the attribution arms hold; 0 OPEN §CC rows remain.
