# NEXT SESSION PROMPT — Pre-Deploy S13b part 4: "the voice, the client and the sea"

> Overwritten each time a session hands off. Current hand-over: **October 19, 2026, after S13c part 4 (CC-4
> "Chained orders") landed — row CC is COMPLETE** (two commits on master through the hook: `d6a0cd8d` the head,
> then the builds).
>
> **What part 4 delivered** (`SYSTEMS_REFERENCE.md` §130; pins `tests/test_cc4_chained_orders.py`, 72; the Mode C
> walk `tools/cc4_mode_c_walk.gd`, frames `docs/audits/cc4_client/`):
> - **The head:** CC-X6 (the until-then tail named), CC-X7 (Compromise keeps the typed condition, whichever comes
>   first — `StrategicCondition.cap_turns`), CC-X9 / X19 (no pursuit or support outlives its man —
>   `strategic.quarry_fate`, `support_friend_fallen`), CC-X17 (every further name relayed in turn), CC-X18.
> - **D7 the arrival verb (CF-5):** `StrategicOrder.arrival_verb` — `march to X then fortify | hold | drill | defend`,
>   done free on arrival (`strategic._handle_move_to_arrival`, `run_arrival_verb`, `install_arrival_hold`; the
>   first-step arrival `strategic_executor._arrive_on_the_first_step`); CC-X22 a `move to` head with such a tail is
>   the march (`parser._arrival_verb_boundary`); CC-X20 the order's identity counts its arrival
>   (`strategic.order_arrival_matches`, ONE rule for F10, stage 5, the quote and the reach).
> - **D6 the contradiction asked first:** `relay.reorder_suggestion` on `/command`'s ordinary road — a head that
>   leaves the corps standing with a tail that moves or attacks sends NOTHING and offers the order that gives both
>   in the remedy slot, only where it is coherent (`_strikes_now`, `_has_a_road`; never a pursuit tail).
> - **D8 the standing contingency:** `StrategicOrder.contingency` — `Ney, if Mack advances, fall back to Lorraine` /
>   `… if the enemy comes within reach, attack` (`condition_grammar.extract_contingency`, restated as a HOLD before
>   any reader); watched on the hold province and the neighbours we SEE (`strategic.contingency_trigger`); fired
>   free at the head of the order pass (`StrategicOrderProcessor._fire_contingency`); CC-X21 a conditional line is
>   never an interrupt's answer (`main._line_is_a_contingency`).
> - **CC-X23 / X24:** a cautious holder's works now rise at the turn's end (the gate D7 relaxed), and the hold's and
>   the sally's reports read what the executor answered.
>
> **Traps part 4 paid for:**
> - The bash heredoc collapses `\\` to `\` and turns `\b` into a backspace byte in a payload — write every script
>   (Python or GDScript) with the Write tool, then run it.
> - The interrupt route (`main._command_interrupt_answer`) reads answer KEYWORDS before any parse: a new line shape
>   that carries "attack", "hold", "march to"… must be checked against a pending question (CC-X21 was that).
> - An aggressive marshal answers the guns of his own accord (the cannon-fire redirect): a Mode C walk that needs a
>   march to ARRIVE uses a literal man (Soult). The terminal is trimmed — read a block by its heading
>   ("--- Strategic Order Updates ---"), never by a character offset.
> - A "before" measurement without touching the shared checkout: `git archive HEAD backend <the maps dir> | tar -x
>   -C <scratch>` and run the probe with that dir first on `sys.path` (never stash, never reset).
> - Patch the executor at its type (`type(M.executor).execute`), never the instance (the singleton-shadow trap).
> - `CLAUDE.md` stands within ~150 bytes of its 62,000-byte cap: swap its live-state rows, never grow them.
> - `TaskStop` leaves a backgrounded backend alive: stop the PID that LISTENS on 8007 (`netstat -ano`, check its
>   command line is `backend.main`), never 8005 (the player's game) or 8006.
>
> **Nothing waits on the user before S13b part 4** (UXR-4, the code-signing certificate and AO's three questions
> are theirs before S15; PC-R7 (ii) heads S14). Paste everything below the line as the opening message of a fresh
> session.

---

Pre-Deploy S13b part 4 — "the voice, the client and the sea" — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (S13c is complete; read `git log -1` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP (the S13b part 4 block), `docs/BUG_FIXES.md` §DD-B (DDB-21, DDB-45 … 62 and DDB-X6 — their filed fix shapes), `docs/audits/DD_B_RULINGS_2026_10_14.md`, `docs/SYSTEMS_REFERENCE.md` §115–§118, and `docs/NAVAL_SPEC.md` §17–§18 for the sea rows.

Scope, in order:
1. **The P2 first — DDB-21:** a corps standing in a province the peace just titled to France is "stranded" and faces internment. Reproduce on the 1805 board, fix at the home-zone rule, sweep its class.
2. **The voice (S13b-4):** DDB-45 (a two-part question read as one), DDB-46 (the rail keeps stale cards), DDB-47 ("… to join Ney and Davout" split into a second order — mind CC-X17's relay and CQ-8), DDB-48 ("How do I …?" dumps the whole reference), DDB-49 (the reference's developer note and stale Congress count — the help body is CX-3's census), DDB-50 (a released enemy marshal returns unannounced), DDB-51 (a war purpose against an eliminated court), DDB-52 (the Armed Peace's alarm "holds" while the sum falls), DDB-53 (one siege, three contradicting dispatch lines).
3. **The client (S13b-5):** DDB-54 (the first Escape only leaves the line), DDB-55 (the title caption names the next painting early), DDB-56 (an ally's lost province in good-news colour), DDB-57 (the command window too short to read a long reply).
4. **The sea (S13b-6):** DDB-58 … 61 (the Admiralty's closed ports, its automatic states read as orders, the postures question, the readiness rot and the blockade's price before the order), DDB-62 ("lay down a ship at Normandy" lays it at Bordelais), DDB-X6 (the blockade's start and end and a diversion window never announced).

Rules: reproduce each row before its fix; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this part or heading the next); pins `tests/test_ddb_s13b_<slice>.py::TestDDB<n>`; where a fix reaches the AI, the driven attribution arms byte-identical to `BASELINE_SERIES` or each movement attributed and named; the Godot parse harness for the client rows and a Mode C walk on `SOVEREIGN_PORT=8007` (never 8005 / 8006; `INK_IRON_SAVE_DIR` in the scratchpad) for DDB-54 … 57. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when every row above is FIXED with its test and 0 §DD-B rows homed to S13b remain OPEN (DD-B's re-measure is S14e). Close with `docs/STATUS.md` ▶ NEXT UP naming S14 (PC-R7 (ii) at its head) and this file overwritten for it.
