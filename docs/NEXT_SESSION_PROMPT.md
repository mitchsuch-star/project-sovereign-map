# NEXT SESSION PROMPT — Pre-Deploy S14b part 1: VP-1's substrate, unarmed

> Overwritten each time a session hands off. Current hand-over: **October 22, 2026, after VP-1's gate was RULED**
> (`docs/VP1_DESIGNS_SPEC.md`; commits through the hook — `git log -3`).
>
> **What the last session delivered:**
> - **S14b's head LANDED** (`200cdf91`; `SYSTEMS_REFERENCE.md` §142): RR6-X3 one sighting rule
>   (`intel_surfaces.last_seen` — in sight now, else the newest sighting; the store learns what the enemy-phase
>   dialog shows), its siblings RR6-X4 … X11, and UXR3-F11 the titled tally.
> - **VP-1's gate RULED** (`docs/VP1_DESIGNS_SPEC.md`): three roads of two designs each (the Protector of the Rhine,
>   the Crowns of Italy, the Continental System), an irreversible priced proclamation from the Cabinet's road page,
>   no gold rewards, THE DECISIVE PEACE (a fifth register, mark and continue, a waypoint toward the Congress),
>   WO-D4(b) as Road III, SF-ECON-1 as four Acts of the Empire; six amendments flagged (A1 … A6), no user ruling
>   reversed; its siblings `BUG_FIXES.md` §VP1 VP1-X1 … X10 filed OPEN, owned by parts 1 and 2.
>
> **Traps the last session paid for:**
> - **A commanded arm moved by a fix is a different campaign for its remaining turns** — attribute with the fix held
>   down at its seam (`--seam MODULE:NAME=EXPR`, EXPR over the call's args `a`), never by reading the end state.
> - **The ambient series runner ends turns at the turn manager** (`tm.end_turn`) — a write placed in
>   `meta_executor` never reaches it; count each seam's reach before calling the series "proven".
> - **The full suite is ~32,500 tests, ~7.5 minutes at `-n 8`**; a `-x` run stops early and hides failures.
> - **Test worlds that replace `world.regions` keep the legacy boot's intel store** — clear `world.intel`.
> - The Bash tool's heredoc eats backslashes: scripts with the Write tool, edits with Edit, CRLF docs normalised
>   to LF and written back CRLF.
> - `CLAUDE.md` at 61,869 of 62,000 bytes.
>
> **Nothing waits on the user before S15** (UXR-4, the code-signing certificate, AO's three questions and
> SF-NAV-1-D1 are theirs). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14b part 1 — VP-1 "The Emperor's Designs": the substrate, UNARMED — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (read `git log -3` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP, `docs/VP1_DESIGNS_SPEC.md` (the whole record — §2 the six designs, §3 the store and the branch, §4 the decisive peace's rule, §7 the series, §9 Part 1), `docs/BUG_FIXES.md` §VP1 (VP1-X1, X2, X3, X9), `backend/game_logic/agendas.py` (`_controlled_by_self_or_vassal`, `get_active_agenda`), `backend/game_logic/formations.py` (`format_progress`, the `rewarded` latch, `_announce`), `backend/game_logic/game_end.py` (`province_title_kind`, `record_ending`, `process_end_of_turn`, `note_ratification`), `backend/game_logic/naval.py` (`closed_ports_against`, `trade_dominance_nation`), `backend/game_logic/vassal.py` (`process_vassal_loyalty`, `AUTONOMY_DRIFT`), `backend/game_logic/emergent_designs.py` (`maybe_fire_volte_face`), `backend/game_logic/compensation.py` (ruling J — unchanged), `backend/models/world_state.py` (`_backfill_reforms` idiom, serialization).

Scope (the record's §9 Part 1 — the design is the record's; flag any reversal):
0. **The user's rule (October 20, 2026): diplomacy is never typed.** Part 1 ships no player road: the shipped `europe_1805.json` gains no `imperial_designs` block until part 2; the store is armed only on a staged test scenario.
1. **The head — reproduce first:** the record's "reproduce first" facts on today's tree (the boot readings Rhine 0 / 3, Iron Crown 2 / 3, System 10 / 26; the three road gates true at boot; Bavaria's vassalage price; the drift −2 / −4); the Tilsit road (`tools/playtest_scripts/sf_nav1_tilsit_road.json`) re-run on three seeds with the Blockade's 13-of-26 latch reported at K = 6 (report, never move K to fit); VP1-X1, X2, X3 reproduced on boards.
2. **Build:** `backend/game_logic/imperial_designs.py` — the store (`world.imperial_designs`, one serialized field, `to_dict`/`from_dict` with `.get`, the `_backfill_imperial_designs` idiom, `SAVE_FORMAT_REFERENCE.md`, the serialization test), the validator (`_validate_imperial_designs`), the six predicates nation-parameterized on the authored `owner`, holds and latches, `note_terms` at every war-ending treaty the owner signs (terms are facts, recorded before any proclamation), the tick in `process_end_of_turn` with THE DECISIVE PEACE's rule computed but its stamp seam held off until part 3, the three reward seams (the suspended drift, `CS_ORDER_DECAY`, the one-shot authority), VP1-X1, X2, X3 (each behind its own series lever) and X9.
3. **Measure:** `tools/_vp1_series_arms.py` — `BASELINE_SERIES` byte-identical with every seam up and down, each seam's reach counted; the archived commanded arms' games byte-identical (`tools/_vp1_arm_attribution.py`).

Done when `tests/test_vp1_the_emperors_designs.py` holds the record's Part 1 done-when (§9), VP1-X1, X2, X3, X9 are FIXED with their pins, the full suite is green through the hook, STATUS ▶ NEXT UP names part 2, and this file is overwritten for it.

Rules: reproduce each gap on a board before building; the sibling sweep after every fix (CLAUDE.md Rule 10); a change that reaches the AI or the backend runs the attribution arms with `BASELINE_SERIES` byte-identical or every movement attributed (count the reach); edit CRLF files with a script that preserves line endings. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.
