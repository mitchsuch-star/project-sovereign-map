# NEXT SESSION PROMPT — Pre-Deploy S13c part 2: CC-3 "Select, click, Enter" (+ drag)

> Overwritten each time a session hands off. Current hand-off: **October 17, 2026, after S13e part 4
> landed** (one commit on master through the hook). **S13e — the four peace parts — is COMPLETE.**
>
> **What part 4 delivered** (`SYSTEMS_REFERENCE.md` §127; pins `tests/test_pc_rulings.py`):
> - **PC-R7 (i) — the war titled by its stake.** `backend/game_logic/war_title.py::war_title` (the ONE
>   builder: the chair's named purpose → an AI war's design → an enemy's purpose → the ground in play → the
>   league → the court), `war_title_for_pair`, `settlement_war_label` (with its article, for the settlement
>   sentences), `titled_label` (the table's heading). Read by the war row (`war_title`, `war_title_line`,
>   `war_roster_display`, `held_line`), the HUD card and its tooltip, the war and truce popups, the truce card,
>   the wizard, the dispatch's purpose line, the Charges, the table and its records, the request-terms label,
>   the foreign wars, the desk's "what is the war for", the letters' War Summary. F41: the peace rows say
>   whom they address (`name_the_courts_a_peace_row_addresses`); the war popup has one Negotiate per court.
> - **PC-R7 (ii) heads S14** (`PRE_DEPLOY_PLAN.md` §2 S14's head; the row stays OPEN; `TestPCR7::test_ii`).
> - **The rows:** F57 (a carve writes the punitive record), F74 (`agendas._entry_achieved`), F75
>   (`game_end.ally_homeland_returns`), F83 (`diplomacy.lift_continental_system`, `continental_system_lifted_until`
>   serialized), F81's second road (`settlement_reactions.reward_named_carried_allies`), F28
>   (`settlement_third_party.sub_pair_loser_sues`), F29 (`client_pair_is_the_lords_war`), F30
>   (`vassal.client_leads_its_own_war`), F33 (`held_line` / `held_line_note`), F11, F14 (`terms_jitter`), F45,
>   F85 (the Tilsit fixture DRIVEN; the Congress fixtures producible), F86 (the driver's decline dial).
>   Siblings PC-X21 … X27 (the bilateral occupied-homeland cession through `bilateral_cession_carries`; the
>   status quo's summary; the C4 probe; the Congress fixture's unowned wars; the foreign wars; the desk; the
>   letter's War Summary).
> - **The instruments:** the series byte-identical on eleven arms (`tools/_pc_s13e4_series_arms.py`); the DD-1
>   sweep A = 0 / B = 0; the fuzzer ten seeds × 1,000, 0; F's reactivity re-read (`tools/_pc_s13e4_reactivity.py`,
>   the report's §47: all ten levers move a court's answer on the Vienna-held board); the Part IV frames
>   re-shot at 5120×1440 on both turn-6 boards (`docs/audits/peace_client/`).
>
> **The seams CC-3 builds on (and must not break):** the war card's TEXT is now the war's title ("War for
> Bohemia") and a truce card reads "War for Bohemia — Austria, truce 4t" — a click on either still opens the
> popup; the war popup's buttons are "Negotiate with <court>" (one per court); CC-2's quotes stay
> byte-identical to `/command` (the drift census); S13f's FOLLOW / ARMY rows and CF-6's chips sit on the
> province panel's own-marshal row.
>
> **Traps part 4 paid for:**
> - A `.gd` file may hold CRLF lines: a Python `str.replace` on "\n"-joined text misses — use the Edit tool.
> - The ratify context is a slotted dataclass: a new `ctx._field` needs its `field(init=False)` declaration.
> - The bilateral ratifier titles the status quo at the state write, BEFORE the one-time clauses move a
>   province: anything that reads "what we hold" after the signature must read the controller now.
> - CLAUDE.md sits ~140 bytes under its 62,000-byte cap.
> - The pc4 harness: a seeded save carries the Kingdom of Italy's petition — refuse it before the wizard opens;
>   a second End Turn is needed when envoys would lapse (the first only warns).
>
> **Nothing waits on the user before CC-3** (UXR-4, the code-signing certificate and AO's three questions
> are theirs before S15, not before this part). Paste everything below the line as the opening message of a
> fresh session.

---

Pre-Deploy S13c part 2 — CC-3 "Select, click, Enter" (+ drag) — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (S13e is complete; read `git log -1` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP (the CC-3 block), the plan `~/.claude/plans/sorted-yawning-clover.md` §CC-3 and its decision D4 (map gestures open a modal confirm card; panel chips send directly), `docs/SYSTEMS_REFERENCE.md` §119 (CC-0/1), §121 (CC-2 "March here" and `GET /march_quotes`), §125 (AO: FOLLOW, the fan-out, the army order) and §126 (CF: the three chips, the remedy offer), and `docs/BUG_FIXES.md` §CC.

Scope, in order:
1. Selection: on an empty line a click on an own token selects that marshal — a ring, a status strip ("Soult selected — click a province: march · an enemy: attack · a marshal: support · Esc cancels"), the reachable provinces tinted by ETA band from ONE pathfinding pass (Rule 8: the cautious avoid set computed once).
2. Hover and click: the quote's road drawn as a ghost line (new `scenes/map_order_layer.gd`); the exact quote fetched once and cached; with a selection a province click beats fleet pieces.
3. The confirm card (D4): modal, registered with `dialog_manager`, Enter / Esc its own and blocking `_execute_command`; the exact command, AP, turns, `replaces`, `objection: possible`; [Send] [Put in line] [Cancel]; an enemy in reach → attack, out of reach → march then attack, an own marshal → support; "Put in line" through `_line_offer`.
4. Drag: left-press on an own token with no draft → 8 px → dragging with a ghost line; release on a province opens the card; water or Esc cancels; middle-drag pan unchanged.
5. The Esc ladder gains "cancel selection"; the selection clears on Esc, right-click, a send, end turn, any modal, load / new game, or the marshal missing from the next payload; clicks are ignored while a command is in flight.

Method: drive it on the real client with `tools/cc_client_harness.gd` (the selection lifecycle, the drag threshold, the card's command equal to the quote's, Enter and Esc on the card — Enter never reaches the line or ends the turn — and the panel shut while a marshal is selected); the CC-2 drift census stays byte-identical; the Godot parse harness EXIT 0 (commit the refreshed `tools/godot_parse_report.json`); a Mode C walk on `SOVEREIGN_PORT=8007` (never 8005 / 8006; `INK_IRON_SAVE_DIR` in the scratchpad) shows each gesture. Sibling sweep after each fix — file from CC-X11 (the other gestures, the war room, the region panel). A series attribution only if a change reaches the AI (it should not: CC-3 is client-side).

Rules: shared checkout — never stash, reset or switch branches; commit only your own files by explicit path with `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>` in the background (the hook runs ruff and the full suite, about 6.5 minutes); never `--no-verify`; a moved pin is re-seated with its row named.

Close with: docs updated (`SYSTEMS_REFERENCE.md` §128, `BUG_FIXES.md` §CC rows, `PRE_DEPLOY_PLAN.md` §2 S13c, STATUS ▶ NEXT UP naming S13c part 3 (CC-5 "The war table") next with its prompt pre-decided and the ▶▶▶ entries kept, `NEXT_SESSION_PROMPT.md` hand-over); one commit through the hook; the report opens with the commit SHA.

Done when: the plan's CC-3 tests pass through the hook; the walk shows select → hover → click → Send and drag → card; the drift census holds; 0 OPEN §CC rows homed to CC-3.
