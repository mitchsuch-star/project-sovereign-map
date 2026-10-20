# NEXT SESSION PROMPT — Pre-Deploy S14 part 1: PC-R7 (ii) "the moderate peace"

> Overwritten each time a session hands off. Current hand-over: **October 19, 2026, after S13b part 4 ("the voice,
> the client and the sea") landed — S13b is COMPLETE** (two commits on master through the hook: `94ce4c44` the code,
> then the close).
>
> **What part 4 delivered** (`SYSTEMS_REFERENCE.md` §132; rows `BUG_FIXES.md` §DD-B; pins
> `tests/test_ddb_s13b_the_sea.py`, `the_voice.py`, `the_client.py`, `the_rulings.py::TestDDBX6`):
> - **DDB-21 (the P2):** a corps on soil its court holds by title is home (`withdrawal.is_home_at`,
>   `game_end.holds_by_title`); the corridor is judged after the peace's titles; ONE embark rule
>   (`naval.embark_position_ok`, the home zone walked by land). Siblings X26 (no internment by nobody), X27 (the
>   beachhead return while the war runs).
> - **The voice:** the compound question (`question_desk.classify_compound_question`, X28's yes/no tail, X29's two
>   marshals); the rail's state cards end with their state and its one-shot events age out
>   (`notifications.EVENT_NOTICE_TYPES`, X30, X31); "… to join Ney and Davout" one order; one reference section per
>   "how do I …" and `help <topic>` (`backend/ai/help_topics.py`, the new PORTS AND THE CONTINENTAL SYSTEM
>   section); the Congress's own figures; a released prisoner named; a fallen court's purposes concluded; the Armed
>   Peace's hold named; one siege, one outcome.
> - **The client:** one Esc ladder (`main._escape_closes_topmost`); the caption at the crossfade's midpoint; an
>   ally's loss in red (`captured_from_alignment`); three lines a notch and the tall reply raised until the next
>   command. Driven by `tools/ddb_s13b_client_harness.gd`; walked by `tools/ddb_s13b_mode_c_walk.gd`
>   (`docs/audits/ddb_s13b_client/`).
> - **The sea:** the Admiralty's port rule and open courts (`naval.ports_by_court_against`), whose sail counts and
>   the camp's count, both postures named, the rot's remedy and the blockade's price before the order
>   (`naval.posture_phrase`, `window_remedy`), the named yard, and the rail's sea notices (`naval_state_changed`).
> - **The instruments:** the series byte-identical with every part-4 seam up and down
>   (`tools/_ddb_s13b4_series_arms_final.json`); the CMD-H-DOWN driven arm re-seated with DDB-21's title seam named.
>
> **Traps part 4 paid for:**
> - The bash heredoc mangles backslashes in a payload — two edits broke on it again (a regex move, a test pin).
>   Every script and every multi-line edit through the Write / Edit tools.
> - A full parallel run reads the working tree: a driver subprocess imported `naval.py` BETWEEN two edits of one
>   refactor (an `UnboundLocalError`) and six driven pins failed. Never edit backend files while a full run plays;
>   re-run a failing module on the settled tree before believing it.
> - The client's "before": a HEAD copy of the Godot project in the scratchpad (`cp -r godot-client/project-sovereign`
>   with its `.godot` cache, then `git show HEAD:<script>` over the edited scripts) and the harness run with
>   `--path` there. A field the HEAD client lacks must be read defensively (`_main.get(x) == true`,
>   `has_method`), or the harness dies on `bool(null)`.
> - The Mode C backend: `Start-Process … -m backend.main` with `$env:SOVEREIGN_PORT = "8007"`,
>   `LLM_MODE=mock` (the .env says anthropic) and `INK_IRON_SAVE_DIR` in the scratchpad; stop the PID that LISTENS
>   on 8007 (`netstat -ano`) — the Start-Process PID can be a launcher. 8005 is the player's game: never touched.
> - A new notification type needs the rail's TWO maps (`TYPE_ICONS`, `TYPE_ICON_SVGS` in `notification_bar.gd`) —
>   the REV-V3 census reads them. A notice posted INSIDE the advance (post-increment) stands one morning more than
>   one posted in the player's turn or the enemy phase.
> - The help body is executed by CX-3's census (every double-quoted string is typed): new reference text quotes
>   only orders that run.
> - Line endings: `git ls-files --eol` is the authority (a `grep -c $'\r$'` read here was not to be trusted).
> - `CLAUDE.md` stands within ~150 bytes of its 62,000-byte cap: swap its live-state rows, never grow them.
>
> **Nothing waits on the user before S14** (UXR-4, the code-signing certificate and AO's three questions are theirs
> before S15). Paste everything below the line as the opening message of a fresh session.

---

Pre-Deploy S14 part 1 — PC-R7 (ii) "the moderate peace", half one — build on master in the shared checkout `C:\Users\User\PycharmProjects\project-sovereign-map` (S13b is complete; read `git log -1` for the head).

Read first: `docs/STATUS.md` ▶ NEXT UP (the S14 block), `docs/PRE_DEPLOY_PLAN.md` §2 S14, `docs/BUG_FIXES.md` §PC row PC-R7 (its completion line), `docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §40 J (the design) and §46 J (the decision, "built in two halves"), `docs/SYSTEMS_REFERENCE.md` §122–§127 (the peace rulings as built) and the settlement contracts named in `CLAUDE.md`'s "Peace Deals" row (`SETTLEMENT_GUIDED_TERMS_SPEC.md`, `SETTLEMENT_CONVERSATIONAL_REFRONT_SPEC.md`).

Scope — PC-R7 (ii) is two sessions (§40 J); this part takes the clause end to end:
1. **Size it at the head** against the seams the row names (`settlement_validation`'s canonical clause types, `settlement_scoring.compute_settlement_package_raw_harshness`, both scorers, both ratifiers, the guided rows, the AI producer `ai_diplomacy` settlement catalogue, `agendas.py` — Austria's Eastern Question, `diplomatic_templates` desire profiles) and write the split into the row before building.
2. **`territory_compensate`** — the loser paid in a third party's province, or its design pointed elsewhere: validated (`settlement_validation`), scored by BOTH scorers (the table's and the bilateral), ratified by BOTH ratifiers (the settlement table and the bilateral treaty), authorable from the guided rows, and offered by the AI producer where its desire profile fits (GR5: the AI's letter carries what the player's may).
3. **The moderate Pressburg** (Salzburg for Tyrol) authorable and carrying on the Vienna-held board (`tests/fixtures/pc_boards/`), pinned in `tests/test_pc_rulings.py::TestPCR7` beside (i)'s pins; `::TestPCR7::test_ii_the_compensation_clause_heads_s14` re-seated to what lands.
4. **Part 2 (the next session, named in the row):** declared goals at the declaration plus composable articles at the table (a declared term dropped at the peace refunds part of its cost), and the coalition's no-separate-peace bond priced (Chaumont); then SF-RR7 (SFR-B3 "Europe waits on Paris", with DDB-X4).

Rules: reproduce the gap on the board before building; the sibling sweep after every fix (CLAUDE.md Rule 10 — each sibling filed and fixed in this part or heading the next); a fix that reaches the AI — and this one does, through the producer — runs the attribution arms (`tools/_pc_s13e4_series_arms.py`'s idiom: function seams, never a new lever) with `BASELINE_SERIES` byte-identical or every movement attributed and named; the DD-1 sign-ability sweep and the treaty fuzzer re-run where `can_sign` or a ratifier moves; the Godot parse harness if a `.gd` changes. Commit through the hook by explicit path, in the background: `env -u PYTHONDONTWRITEBYTECODE -u PYTHONIOENCODING git commit -F <msg> -- <paths>`; never `--no-verify`, never stash, reset or switch branches.

Done when the compensation clause is validated, scored, ratified and offered end to end, the moderate Pressburg carries on the Vienna-held board with its pins, and PC-R7's row names what part 2 still owes. Close with `docs/STATUS.md` ▶ NEXT UP naming S14 part 2 and this file overwritten for it.
