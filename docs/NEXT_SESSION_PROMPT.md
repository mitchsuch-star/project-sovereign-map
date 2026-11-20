# NEXT SESSION PROMPT — Row IC, Session 2b: the task to prove himself (read the first block)

> **READ THIS FIRST — the next session is ROW IC's SESSION 2b** (the section "## Row IC, Session 2b — the task to
> prove himself: the plan, decided" below). Then row IC's Sessions 3 and 4, then **Session H, the deploy** (its
> section is kept below, with the lines that overrule it). The order is `PRE_DEPLOY_PLAN.md` §2 (row IC).
>
> Overwritten each time a session hands off. Current hand-over: **November 20, 2026 — ROW IC, SESSION 2: BUTTONS
> FOR ORDERS, THE LINE FOR TASKS, EXACT ORDERS ✅ BUILT AND COMMITTED — NOT PUSHED (it waits for his word).** His
> words: "make sure buttons exist for simpler things but typing is used for missions and excepts a wide array if
> things". Built (`SYSTEMS_REFERENCE.md` §231; `BUG_FIXES.md` §"Row IC, Session 2"; `tests/test_ic7_the_buttons.py`,
> `test_ic8_the_line.py`, `test_ic9_exact_orders.py`; the driven `TestRowIC7TheButtons`): **the buttons** — one
> client table `SIMPLE_ORDER_BUTTONS` (`scripts/simple_orders.gd`), the card's second row (Stand here · Stay put ·
> Posture · Give him a task…), the enemy card's other choices (Chase him, Bombard, Charge him, Attack held back), a
> march's "then", the province's "Look at it", the group's Attack… / Support… / Fall back… / Garrison…; **the line
> for tasks** — the word table (`backend/ai/word_table.py` → generated `task_words.py` / `task_words.gd`), the
> read-back's rows (Taken · Not taken · He says · Enter sends), the typed gate (`typed: true`), what the line
> refuses (`task_line.py`), the ready tasks (`GET /task_presets`); **exact orders** — `StrategicOrder.if_thens`
> (`backend/commands/if_thens.py`: eight ifs, five thens, three lines for a literal man and one on a hold for the
> others). Ten rows closed (UI6-X70, X73, X74, X75, WS-12 with GRD-33, WS-14, IC-V1 … IC-V4). **NOT built: the
> trust crisis's "Grant Autonomy" replaced by a task to prove himself** — the plan's decided fork was taken at the
> checkpoint; it is Session 2b (row IC2-D1, two strict-xfail pins).
> **Its traps (fresh):** (1) a harness's client hides the reading under the command line (`UiSettings.get_readback`
> defaults to off under a harness) — a walk that means to read it sets `DD_B_READBACK=1`; (2) the general's card
> stands on its BOTTOM edge: whatever makes it taller lifts every row above the new one — add rows above what was
> pressed, or in the hint's place; (3) the order card's headline is ONE clipped line, and an autowrap Label in it
> made the card 1,400 px tall (a container reads a wrapping label at width 0) — long words go in the terms, which
> wrap; (4) a standing order's mark on the map is pressed with the instrument's `click_mark <Marshal>` (pieces,
> labels and the near-grab take the click almost everywhere else); (5) the map MOVES when a card opens — read every
> place off the state, never a remembered pixel; (6) the attack's twenty stages are read from `_execute_attack`'s
> source by a dozen tests — a new step goes INSIDE a stage, never around the loop; (7) a new marshal-order word
> must bind to a NAME (the metamorphic ratchet), and `python -m tools.gen_task_words` then
> `python -m tools.gen_routed_order_words` after any change to the word table; (8) the ledger's row tag is
> `⟨SF step=… ⟩` (U+27E8 / U+27E9), not the brackets it looks like; (9) Bash heredocs mangle apostrophes and
> backslashes — write files with the Write tool; (10) the broad suite's output is block-buffered: its file looks
> stalled for minutes, the run is not.
>
> The hand-over before it: **November 20, 2026 — ROW IC, THE REVIEW OF
> "ON HIS OWN": THE DESIGN'S VERSION 6 ✅ WRITTEN, COMMITTED AND PUSHED at his word ("commit and push these
> with it").** His words: "review the new autonomous generla conmcept assure low authority autonomy isnt in
> conflict even removing it if needed and make sure buttons exist for simpler things but typing is used for
> missions and excepts a wide array if things and also if army has differner personalities they arent all doing
> same thing every turn etc full reveiw and u[pdates". The plan approved in Plan Mode. **No game code changed**:
> the design (`docs/INDEPENDENT_COMMAND_SPEC.md` version 6 — §1.1 his three rulings, §1.3 what the code showed,
> §6.7 how the men differ, §6.11 autonomy you grant, §8 buttons and typed tasks, §9.1 an army's task, §15 the
> re-cut build, §16 D24–D31, §19.4 how the review ran), the ledger of every finding
> (`docs/audits/ic_focus_groups/round4_review_ledger.md`), four defects filed with strict-xfail pins
> (`BUG_FIXES.md` §"Row IC — the review of 'on his own'": IC-V1 a one-word condition dropped in silence, IC-V2 the
> read-back shows no condition, IC-V3 a man in the trust crisis's three turns can fight twice in one end of turn,
> IC-V4 the missing buttons; `tests/test_ic_review_pins.py`), seven typed-road rows moved from Session H's head to
> IC-8 (UI6-X70, X73, X74, X75, WS-12 with GRD-33, WS-14), row IC homed in `PRE_DEPLOY_PLAN.md` §2 (the plan-homes
> pin taught `IC-7` … `IC-15`), and the six stale "not pushed" record lines corrected. **What version 6 rules:**
> the trust crisis's "Grant Autonomy" (three turns on the enemy's AI) is REMOVED by his consent and replaced by a
> task to prove himself under exact orders with today's rewards; every simple order is a button; a task is a typed
> sentence (the line opens filled with his proposal, chips write into it, a wide word table, a four-row read-back);
> men differ in seven ways with no dice (a seeded "day's nerve" only if R-VARIETY is missed); an army's task puts
> its commander on his own and the rest in support.
> **Its traps (fresh):** (1) a quoted CAPITAL closing word in a ledger row (ACCEPTED, RETIRED, RE-HOMED, NOT TAKEN,
> RULED …) makes `tools/defect_census.py` read an OPEN row as disposed or closed — quote in lower case; (2) a row
> naming an id beside a closing word earns that id the census's "*" (informational; no test reads it); (3) the
> review workflow failed on its last line (a variable named `P4`, returned as `p4`) — its resume RE-RAN the
> panels, which turned out useful (two independent samples) but cost tokens; check a script's return names; (4)
> `.venv` reads of the 1805 board need `SOVEREIGN_SCENARIO`/`SOVEREIGN_MAP`/`SOVEREIGN_SMOKE_START` popped (the
> suite pins `none`); (5) a `cd` inside a Bash call moves the session's working directory — use absolute paths.
>
> The hand-over before it: **November 19, 2026 — ROW IC, THE SECOND
> COMMIT: DIRECTIVES ✅ BUILT AND COMMITTED, and PUSHED November 20 at his word, "Push it" (the desk and row PW
> part 3 before it were pushed November 19 at his word, "Push both").** His
> rulings in Plan Mode: "One list for all", "Yes, named armies", "Desk, then directives". Built
> (`SYSTEMS_REFERENCE.md` §230; `BUG_FIXES.md` §IC directives — none open; `tests/test_ic4_the_directive.py`,
> `test_ic5_named_armies.py`, `test_ic6_the_war_goal.py`; the driven `TestRowICDirectives`): **the directive**
> (`backend/commands/directive.py` — `address`, `quote`, `stale`, `give`; `/command` with `list_first` = the ask,
> `members` + `expect_ap` = the give, refused free and drawn again when it no longer holds, a man charged more
> than his row putting the board back; `GET /directive_quote`; one Take-back unit); **named armies**
> (`world.armies`, the free action `army`, the chip, "Army of Italy, hold"); **the war goal** (`world.war_goals`,
> the free action `set_war_goal`, THE WAR line's "your war goal", the gold ring, the TO DECIDE row that opens the
> march as one list). **A typed list of names now orders every man named** (ruling 1 — the seam
> `directive.a_named_list_is_one_directive`; the relay's rule is pinned with it down). **Its four blind readings**
> (`docs/audits/ic_client/directives/README.md`): 21/21, 28/30 (NOT met — "see the list" read as the roster;
> built out), 15/15, 12/12 — twelve fresh readers; sixteen levers built from what they said confused them. **Its
> review:** see the ledger. **Inert where unused:** the byte-identity series and the France band reproduce.
> **The directives' traps (fresh):** (1) every `/command` the client sends carries `list_first` — a test or tool
> that posts without it has the order carried out at once, with no list (scripts, the band and the series do), so the client's road and the
> scripts' road differ for lines to several; read `main._directive_road`'s docstring; (2) a group stopped by a
> question pops the list's prices off the stash (the men who wait go on later at their own price): anything
> built after the run must read the prices kept before it (`group_orders._carry_out`'s `shown_prices`); (3) the
> order card is a CanvasLayer — a reader of its `visible` must read it by name (`card.get("visible")`), not as a
> CanvasItem; (4) the card's room is reckoned from UNDER the top bar — two edges of the whole height is 26 px too
> much at 765; (5) a card that opens on a placeholder and fills grows under the eye: open once, when the data
> lands, and show the placeholder only after a delay; (6) the map's draw pass may now step a displaced name BELOW
> a mark (`map_label_layer._nudge_clear(…, allow_down)`); the layout pass never does; (7) blind readers take the
> question's words as literally as the screen's — "every corps of the Army of Italy" drew hedges about the other
> six marshals; and a hint's first sentence primes every answer after it; (8) the Bash tool mangles heredocs
> with backslashes or quotes — write scripts with the Write tool and run them alone (it bit twice again).
>
> The hand-over before it: **November 19, 2026 — ROW IC, THE DESK ✅ BUILT AND COMMITTED, and PUSHED November 19
> at his word ("Push both")** (`SYSTEMS_REFERENCE.md` §229; `BUG_FIXES.md` §IC — 31 rows, none open): the `desk`
> key (THE PEACE, THE WAR, TO DECIDE), what a seen enemy can reach, the card at the map's corner, the list when
> End Turn stops, the danger mark, the menu's steer to the School of War. Its traps are kept in §229 and in its
> landing record (`docs/INDEPENDENT_COMMAND_SPEC.md` §15).
>
> The hand-over before it: **November 19, 2026 — ROW PW PART 3, "THE
> FINISHING PASS" ✅ BUILT AND COMMITTED (on his word; pushed November 19 at his word, "Push both").** His words: "fix these the general
> game ux and perhaps animate pieces moving and make sure the game isnt clunky or wierd to play … dont ask me
> questions use reason", then "sound when they move too think of a human playing game, also evaluate the
> utility of the parser and typed commands". Built (`SYSTEMS_REFERENCE.md` §228; `BUG_FIXES.md` §PW part 3;
> `tests/test_pw3_the_finishing_pass.py`; the driven `TestRowPW3TheFinishingPass`): **PW2-D1 CLOSED** (no
> price says "AP" — `display_names.actions_words`); **the take-back** (`backend/commands/take_back.py`,
> `POST /undo`, the Take back chip, Ctrl+Z, the typed `undo`); **the march** (a piece walks its road, a trail,
> the order's own cue for the walk's length, a halt); one flash; words beside every counter; trust and
> authority said; Talleyrand's plain line and a table that adds up; **the map's key** (`map_key.gd`, K); the
> empty command line's ideas; Esc sets a letter aside. **One row open and owned — PW3-D1** (the Cabinet's
> first page seats two courts above a scroll at 1.8: its courts in columns; strict-xfail
> `TestPW3D1TheCabinetsCourtListHasRoom`). Recommended, not built: the typed "who threatens me?".
> **Its blind reading** (`docs/audits/pw_client/README.md`, part 3): reading 5 NOT MET (what "Admin" buys and
> which arm each levy is; "+828"'s period; the port's mark read as a stopwatch), each fixed, reading 6 with three
> new readers MET, 18 of 18; the readers' still-unclear list there is the next UX pass's worklist (what
> Authority and Threat measure on the bar; the idle dot; "Scale + −"; "100%" on the card).
> the full test suite passes on the final build.
>
> **Part 3's traps (fresh):** a new `class_name` needs the engine's class cache (`--import`) — load a new
> script by path; a two-line lambda inside a call does not parse; a panel standing on the map needs its own
> CanvasLayer (the map's names draw over layer 0); `clickshots <x> <y> [n] [gap_ms]` on the instrument takes
> frames WHILE the board moves; STATUS, the Q4 archive and CLAUDE.md are MIXED or LF line endings — patch on
> bytes and match each anchor as it stands; the suite ran slowly beside a windowed instrument — stop the
> instrument before the suite; `tests/test_s14f…::TestS14EX155` is the census of the reply envelope's keys
> (a new key on `build_base_response` joins it).
>
> The hand-over before it: **November 18, 2026 — ROW PW "PLAIN WORDS",
> BOTH PARTS ✅ LANDED (two commits, each through the hook and pushed at the user's word, "commit and push
> everything when you are done"; his ruling "Keep going — all screens").** **Part 2** (`SYSTEMS_REFERENCE.md`
> §227.10–§227.14; `BUG_FIXES.md` §PW part 2 — 40 rows, ONE open and owned, PW2-D1): the enemy's moves played
> on the map before the report (his "can we show the pieces moving or something better?"), a typed line that
> forgives a slipped key (GRD-16 built with it: "did you mean Ney?"), and plain words on the rest of the
> screens (the Cabinet, the peace table's faces, a marshal's objection, a letter's IN SHORT, the battle's
> dice). Its review: nineteen findings, sixteen fixed. Its blind reading met the bar on the final tree, 18 of
> 18 (`docs/audits/pw_client/README.md`). **PW2-D1 heads Session H:** no price a player acts on says "AP" —
> every tag reads "N actions" (251 pins in 81 test files; the strict-xfail `TestPW2D1NoPriceTagSaysAP`).
> **Part 1** —
> the user's FIRST playtest (thirteen turns: "everything feels convoluted and opaque and disconnected") and
> the fixes of everything he reported: the sounds that would not stop, generals easier to click and sent on
> one click (a move next door costs 1 action), the order that TAKES a province a corps stands in, the turn's
> report that opens on what changed for the player, the battle and the peace table in everyday words, the
> dial that never gives his land unasked, the forecast that says what the peace will do, windows that stand
> still at his own setup (Interface Scale 1.8 on 5120 x 1377). Rules `SYSTEMS_REFERENCE.md` §227; ledger
> `BUG_FIXES.md` §PW (54 rows, 0 open); pins `tests/test_pw_plain_words.py`; the blind reading and what
> its readers still found unclear `docs/audits/pw_client/README.md`; **CLAUDE.md golden rule 11 — plain
> words — is now standing law** (read `memory/feedback_first_playtest_ux_is_key.md`). Then Session H,
> below — its head gains PW2-D1 and loses GRD-16 (built).
>
> The hand-over before it: **November 18, 2026 — ROW OC "THE RULINGS
> BUILT" ✅ LANDED (committed and pushed at the user's word, "commit and push")** (the rules and the measure
> `SYSTEMS_REFERENCE.md` §226; the ledger `BUG_FIXES.md` §OC; the rulings
> `docs/audits/OPEN_CALLS_RULED_2026_11_17.md` §5; the seams `tests/_oc_seams.py`; the pins
> `tests/test_oc_the_rulings_to_build.py`).
> **What landed:** the four slices the November 17 rulings homed before the deploy — **the courts' purse**
> (an AI court buys a law only once it uses what the law gives; a court at war saves for its General Staff
> against the price and one turn of upkeep, and holds its discretionary gold while the Staff is within reach;
> every cheap purchase keeps a turn of upkeep; a court keeps its doctrine cure's authority in hand), **the
> Emperor's purse** (the mercy turn after a deficit pays no arrears down — deficit, solvent, solvent deserts
> at turn 11; a restless interior costs 75 a province, capped at 250), **the Strangulation's letter** (a
> Britain whose ports the System closes and whose war-weariness has passed 80 writes for an armistice with no
> contact) and **golden rule 1** (the ground's scaling of a reckless cavalryman's dash read in
> `Marshal.get_attack_modifier` alone; the coordination magnitudes named on the marshal). The deploy gate is
> MET on the final tree (band 26 / 27 / 28, story classes 10, the roster in three readings, no annexation
> outside aim), its clause 2 — a minor raised by promotion — read on thirty ambient seeds by the user's ruling
> (`DYNAMISM_SPEC.md` §7): two campaigns in thirty raise one, with row OC as without it.
> **Open with the user: NONE.** What stays the user's is an act, not a call: **the certificate is a purchase**
> (a payment the user makes), and the walk is the user's own.

**FIRST — in this order:**

0. `git log`: the review of "on his own" is ONE commit (the design, the ledgers, the plan's row and the pins — no
   game code), pushed November 20 at the user's word; before it row IC's two commits — the desk (pushed November 19,
   "Push both") and directives (pushed November 20, "Push it") — and row PW's, each through the hook. Read
   `STATUS.md` ▶ NEXT UP first, then the spec's §1.3, §6.11, §8 and §15.
1. **ROW IC, SESSION 2** — the section "## Row IC, Session 2 — the plan, decided" below. Plan Mode first (the
   user's standing rule); the plan is decided there, so the Plan-Mode draft is that plan made concrete — no question
   is owed him.
2. **Then row IC's Sessions 3 and 4** (the spec's §15: on his own; the voice and the other side of the hill), each
   its own Plan-Mode session.
3. **Then SESSION H — S15 THE DEPLOY** (the section below; read first `PRE_DEPLOY_PLAN.md` §2 S15 and
   `DYNAMISM_SPEC.md` §7). Its head's open rows — each a defect with a strict-xfail pin, none a call:
   **WS-10** (the war room keeps the bare digits; a docked ledger's tabs move to Alt+1–8 and its lead line says
   so — `TestWS10TwoSurfacesClaimTheBareDigits`), **WS-R** (the readers' unconfirmed finds), **PW3-D1** (row PW
   part 3: the Cabinet's first page seats its courts in columns — `TestPW3D1TheCabinetsCourtListHasRoom`); **moved
   November 20, 2026 to row IC's IC-8** (the read-back of typed tasks depends on them): **WS-12 with GRD-33** (the
   live model's number moves nothing — `TestWS12AModelsNumberMovesAMarshal`, `TestSessionHsHead::test_grd33_…`),
   **WS-14** (the readback's standing question) and **UI6-X70, X73, X74, X75** (the typed order road's compound
   subjects; GRD-16, "Did you mean Ney?", was BUILT by row PW part 2); and — CLOSED by row
   PW part 3, kept here as the record — **PW2-D1** (row PW part 2:
   no price a player acts on says "AP" — every tag on a chip, a button and a message reads "N actions",
   "1 action" or "free", its 251 pins re-seated and the chips re-read for fit at 1.0, 1.5, 1.8 and 2.0;
   `TestPW2D1NoPriceTagSaysAP`). `tools/defect_census.py --open` lists them; the release waits for 0 open
   defect rows.

**What rows BA and OC change in Session H's brief below** (the brief is kept as it stood; these lines overrule
it where they differ):

- **Row BA has no open row.** BA1-X4, BA1-X8, BA2-X6, BA2-X16, BA5-X15, BA5-X16 and BA5-X17 are closed, and
  so are WS-13 and WS-15 (the weak-spot review's two battle-pipeline rows). The head is the list in step 1.
- **The gate's record files — read each clause against row OC's** (`tools/_oc_*_2026_11_18.json`; the tool
  `tools/_oc_measure.py`): the probe `tools/_oc_probe_2026_11_18.json` (arm 0 identical to `9c5228a5` on every
  key); the band `tools/_oc_band_2026_11_18.json` (ALL 26 / 27 / 28; the STAFF arm's CMD-M 20 is the ladder's
  one breach, reported in §226.2); the day's sweeps `_oc_sweep_0_` (72 of 72 equal the commit before) and
  `_oc_sweep_all_`; the ambient ten `tools/_dy_signature_oc_all_2026_11_18.json` and
  `tools/_oc_all_census_2026_11_18.json`; the harness `tools/_oc_chain_d_2026_11_18.json`; the series
  `tools/_oc_series_arms_final.json`; the purse `_oc_purse_0_` / `_oc_purse_all_`, T8 `_oc_t8_0_` / `_oc_t8_all_`
  and the sea arms `_oc_sea_`; **the gate `tools/_oc_gate_2026_11_18.json`**, its clause 2 read on thirty ambient
  seeds (`tools/_oc_promotions_wide_2026_11_18.json`; the user's ruling, `DYNAMISM_SPEC.md` §7). BA-6's records
  (`tools/_ba6_*_2026_11_17.json`) stand as the game before row OC. Row OC changed no `.gd`: the client's
  records are BA-6's — `docs/audits/ba1_client/walk_record.json` (the walk of record) and
  `docs/audits/ba6_mode_c_2026_11_17/` (the live boards); the DD-1 sign-ability records
  `docs/audits/dd1/sign_ability_*.json` are re-taken on row OC's final tree.
- **The user's walk** is also the first look at BA-6 and the court: the survey plates under every table (plains, forest, hills, mountains, a town, a river crossing — never mirrored); the day's taller panel and its three-line cards, the free words' stakes, "+N more", the dice's luck line, the legend; and the Generals screen's court — the order of precedence, each marshal's bonds with their causes, a title in the Emperor's gift and its price, a claim, an account after a joint defeat. Row OC adds no screen: what the walk may meet is the courts' purses (an AI court buying fewer laws and reaching its Staff) and, in a war with a strangled Britain, an armistice letter with Talleyrand's line on the System.

**Row OC's traps (fresh; `SYSTEMS_REFERENCE.md` §226.3 has them in full):** a purchase rung's sibling is the
rung that saves for it (the save's reach was found on Russia's trace, not by a grep); a done-when about the
close is read to its cause (GRD-21's two misses are wars, not purchases); a wider sample is not a lower bar,
but it is an easier one — say both in the record; never edit a chain script while its chain runs (bash reads
it as it goes) — queue a second short chain.

**BA-6's traps (`SYSTEMS_REFERENCE.md` §225 has them in full):** a probe must hold its seams before the world is built (BA6-X7); count what a played court does before believing a rule lives — `tools/_ba6_court_count.py` found the Auerstedt rule deaf for France; a row built after the final chain goes LAST on the ladder, so only its arm and ALL are re-taken; when the world-line moves, run the full suite before the frozen pass (the treaty fuzzer's seed re-timed onto two latent defects, BA6-X5 and X6) and re-take the DD-1 sign-ability records (its pin compares a live run with them); a decorator keeps a CODE-2a driver a driver; a review row not upheld reads "REFUTED — not upheld" or the census counts it open; a frozen copy leaves `docs/audits/` out; never chain two heredocs with `||` (the shell ran the second script's lines as commands and hung — write patches with the Write tool); commit with `env -u PYTHONDONTWRITEBYTECODE`.

**The standing rules** (unchanged): commit on master through the pre-commit hook only when the user asks;
never `--no-verify`; no branches, no worktrees, no stash; nothing pushed unless asked; no player-facing cut or
deferral without the user's word; the model never moves a number; subagents run on Sonnet or Haiku; play
every new rule out before the long measure; one commit and one review a session. If it will not fit, stop and
say what is built and what is not.

---

## Row IC, Session 2b — the task to prove himself: the plan, decided (November 20, 2026)

**What it is.** The half of IC-9 that Session 2 handed on at its checkpoint (ledger row **IC2-D1**, `BUG_FIXES.md`
§"Row IC, Session 2"; `SYSTEMS_REFERENCE.md` §231.10): the trust crisis's "Grant Autonomy" replaced by **"Give him
a task to prove himself"**, and the old engine deleted in the same commit. Everything it stands on is built:
exact orders (`backend/commands/if_thens.py`, `StrategicOrder.if_thens`), the saved field
`StrategicOrder.opening_take` (None today; nothing reads it yet), the read-back and the buttons.

**Read first:** `docs/INDEPENDENT_COMMAND_SPEC.md` version 6 §6.11, §7, §12, §13 (the words census; R-INERT's one
exception — the audience's arm), §15; `SYSTEMS_REFERENCE.md` §231; the strict-xfail pins
`tests/test_ic_review_pins.py::TestIC2D1TheTrialReplacesGrantAutonomy`. Plan Mode first; verify every name below
against the code before relying on it (the line numbers of the November 20 plan have moved).

**Scope — one slice, one commit, one review, one measure:**

1. **The proposal** (`backend/game_logic/trial.py`, new): `proposal(world, marshal)`, PURE — bold: take the
   nearest enemy-held place France SEES within reach; careful: hold his province; literal: hold, and if
   outnumbered fall back to his nearest held province; nothing in reach: hold where he stands. The bold man's take
   is a HOLD whose saved `opening_take` the strategic pass runs on its first night — the take order as
   `take_quote` builds it, at no cost, its battle reported in the strategic rows like a fired if-then; his hold
   then stands where he ends.
2. **The audience** (`backend/commands/disobedience.py`): the arm `trial` replaces `grant_autonomy`, ALWAYS offered
   (the last field marshal too; the `/debug/trigger_redemption` no-world fallback too), its text the proposal in
   full; `check_redemption_threshold`'s guard reads `trial`. Answering installs the exact order (free) and
   `marshal.trial = {line, turns_left: 3, won, lost, taken, given}`; he takes no other order meanwhile (the
   executor's block, replacing "acting independently"); **"Call him back"** (the cancel slot's face;
   `_execute_cancel`) ends it, trust unchanged; the combat pipeline counts his battles won and lost (attacking or
   defending) and defended places taken; after three turns the bands apply — spectacular (two battles won or a
   defended place taken) +40 trust and +10 authority (`standing.move`, cause `spectacular_return`), good +25, none
   +15, poor +5 — his order cleared, a morning line; the five-turn cooldown kept. A man on trial is never warned
   and makes no jealous strike (IC-V3's guard `jealousy.acts_independently` is re-seated on the trial).
3. **Old saves:** `Marshal.from_dict` parks the legacy autonomy values on a non-saved attribute;
   `WorldState.from_dict` settles the man just before its `return` (the same bands on what he achieved) and writes
   one line through `world.log_event` with a weight in the dispatch's priority table. A saved `pending_redemption`
   whose options still name `grant_autonomy` has them rebuilt at load; the answer also accepts the old id as the
   trial, so a standing question never sticks.
4. **Deleted in the same commit:** `TurnManager._process_autonomous_marshals`, `_end_autonomy`, their call and
   report keys (`turn_manager.py`, `main.py`); the debug arm `set_autonomy`, its help line, the `[AUTO]` tag,
   `/debug/marshal_status`'s readout; the `grant_autonomy` arm, its words and `main.py`'s `autonomous` /
   `autonomy_turns` reply keys; `meta_executor`'s INDEPENDENT COMMAND REPORT; `while_you_waited._own_way`, its seam
   and its reader in `enemy_phase_dialog.gd`; `state_probe`'s "acting on his own authority"; the reads in
   `war_council.py`, `enemy_ai.py`, `combat_executor.py`, `marshal_overview.py` (and the client's
   `marshal_management.gd`). The fields `autonomous`, `autonomy_turns`, `autonomy_reason`, `autonomous_*` leave
   the Marshal. `EnemyAI.decide_single_action` refuses a player-nation marshal.
5. **Client:** `redemption_dialog.gd/.tscn` (AutonomyButton → TrialButton with the proposal), `main.gd` (the
   "AUTONOMY GRANTED" banner → the task's line; the typed shortcut), `marshal_management.gd` (the flag → "On a
   task to prove himself — 2 turns left").
6. **The words census** (a test): "autonomy" / "independent command" on no marshals'-screen string (the vassal
   scale exempt by name); "on his own" nowhere on them before Session 3 — the jealous strike says "without waiting
   for orders", V2b says "refused your order".
7. **Tests rewritten, never deleted:** `test_autonomy.py` (→ the trial), `test_redemption_v2b.py`,
   `test_administrative_role.py` (last marshal → the trial), `test_wo41_redemption_survives_the_save.py`, and every
   other file naming `grant_autonomy` or the old fields (about twenty: fa26, fa_slice14, fa_slice17_f,
   fa_slice17_p2b, systems_audit_session2 / v2_session3, serialization, marshal_overview, ic3, endpoint_wiring,
   response_pipeline, t3_5, bombardment, iq7_satellites, pt_b_silent_losses, vassal_recovery_lever, …).
   `tools/playtest_driver.py` default `redemption: "trial"`; recorded digests are history and stay.

**Saves:** `Marshal.trial` (new; `to_dict` / `from_dict` with `.get`, `SAVE_FORMAT_REFERENCE.md`, the enforcement
test). The legacy autonomy keys are read once and dropped.

**The measure:** the France band on the commanded arms with the driver's new answer, per seed, naming which
campaigns met a trust crisis and how they moved (R-INERT's one exception); `BASELINE_SERIES` in the hook's run.
**The reading:** §13's third version-6 question, in Session 2's form — "Why does Davout propose a different task
to prove himself from Ney?" — on the audience's window at the user's setup (Interface Scale 1.8 on 5120 x 1377),
the key written before any frame, three fresh readers.

**Forks, decided now** (each one line to reverse): the trial's window cannot hold the proposal at his setup → the
proposal wraps, the type never shrinks; a man with no enemy in sight and nothing to hold → "hold where he stands";
the measure moves the band outside 23–28 on any commanded seed → say so per seed, and keep the shipped bands (the
rewards are today's).

**Done when:** IC2-D1 closed with its two pins promoted; the audience offers no autonomy arm; no French marshal is
ever moved by the enemy's decision logic; an old save settles; the words census passes; `tools/defect_census.py
--open` lists no IC row. STATUS line: *"ROW IC, SESSION 2b — THE TASK TO PROVE HIMSELF"*. Then Session 3
(`docs/INDEPENDENT_COMMAND_SPEC.md` §15).

---

## Row IC, Session 2 — the plan as it was decided (November 20, 2026) — ✅ BUILT the same day, less item 3's trial (Session 2b, above)

**Read first:** `docs/INDEPENDENT_COMMAND_SPEC.md` version 6 — §8 (all of it), §7, §6.11, §13 (R-INERT's one
exception, the words census, R-READ's version-6 questions), §14's version-6 rows, §15's Session 2 table;
`BUG_FIXES.md` §"Row IC — the review of 'on his own'" (IC-V1 … IC-V4) and the rows moved there (UI6-X70, X73,
X74, X75, WS-12, WS-14; GRD-33 in `DESIGN_REFINEMENT.md`); `tests/test_ic_review_pins.py`. Verify every line of
§14 against the code before relying on it. Press everything in the real client at the user's setup (Interface
Scale 1.8 on 5120 x 1377).

**Scope — three slices, one commit, one review, one measure** (the user's "combine slices per session"):

1. **IC-7, the buttons** (§8.1; closes IC-V4). Where each goes, decided:
   - "Chase him" beside Attack on the order card that a click on an enemy opens — a new quote kind `pursue` through
     `order_quotes`, priced as the standing PURSUE (2 actions; 1 for a literal man and the sovereign);
   - the card's Hold slot becomes a pair: "Stand here · 1 action" (`defend`) and "Hold the ground · 2 actions";
   - "Look at <province>" on a click on a province he can look into (the targeted `scout`);
   - one "Posture" slot: stance, and form or break square where the executor allows it;
   - "Bombard" beside Attack for a gun corps; "Charge" / "Restrain" on a reckless horseman's card;
   - "Stay put" — free; quiets his "no orders" row for this turn only; never "engaged" for a literal man's
     restlessness; never clears a warning;
   - the march card's "then …" pick (hold · fortify · dig in);
   - the group face's Attack…, Support…, Fall back…, Garrison… — each the directive's one list first.
   One client table, `SIMPLE_ORDER_BUTTONS` (the pin's name): each row a verb, its label, its price word and where it
   shows. The Help's Orders page footer (`codex_view.gd`) and the boot help say what is true.
2. **IC-8, the line for tasks** (§8.2–§8.5; closes IC-V1, IC-V2 and the moved rows). **First** the typed road's
   defects — UI6-X70, X73, X74, X75, WS-14, WS-12 with GRD-33 (as ruled November 17: the model's number moves
   nothing; the literal man's buff expires at the turn's end), IC-V1 (name a one-word clause in the read-back's "not
   taken" row; keep the two-word floor `cr2-when-ready-then-retreat-not-split` depends on; re-seat the corpus row
   `parseneg-retreat-if-outnumbered-executes` to expect the note) and IC-V2 (the read-back's condition and if-then
   from `describe_condition` / `describe_contingency`). **Then** the word table (one table in `backend/ai/`, its
   lists generated into the parser like `tools/gen_routed_order_words`, a census test, a golden-corpus row per part);
   the read-back's four rows ("Send what I understood" sends the restated line, shown); the refusals with the
   nearest sentence written in (an unseen enemy and a name that does not exist read the same); "Give him a task…"
   opening the line with ready sentences (in Session 2 the exact-order presets and today's standing orders with
   their conditions — his own on-his-own proposal lands with Session 3); the chips.
3. **IC-9, exact orders and the trial** (§7, §6.11; closes IC-V3). The list of if-thens (three for a literal man,
   one for the others as today); the six new ifs and three new answers, deterministic, reading France's own sight;
   each used once ("2 of 3 left"); the renew row; one thing a turn. Then the audience's **"Give him a task to prove
   himself"** — his proposal by nature (bold: take the nearest enemy-held place France sees within reach; careful:
   hold his province; literal: hold, and fall back on his nearest held province if outnumbered; nothing in reach:
   hold where he stands), as an exact order for three turns; the bands (+40 trust and +10 authority / +25 / +15 /
   +5; "spectacular" = two battles won or a defended place taken); "Call him back"; always offered; the five-turn
   cooldown kept; an old save settles on load with a morning line. **Delete** `TurnManager._process_autonomous_marshals`,
   `_end_autonomy`, the debug arm and the old arm (keep the `autonomous` fields only to read an old save); the words
   census test; the playtest driver's default audience answer becomes the trial.

**The measure** (one sweep, with arms): R-INERT on every arm but the audience's — with the buttons and the line
unused, the byte-identity series and the France band reproduce; the audience's arm re-reads the band and names,
per seed, which campaigns met a trust crisis and how they moved. **R-READ** for the buttons and the line: §13's
three version-6 questions, the answer key written before any frame, three fresh readers, frames at his setup.

**Forks, decided now** (each one line to reverse):
- A button whose verb the executor refuses where it would show (stance, square, charge): greyed, with the
  executor's own refusal as its hover — never a dead button.
- The card cannot hold the new slots at his setup: the least-used fold behind "▸ more" (UI-3's fold idiom); the
  type never shrinks.
- Naming the one-word clause breaks `cr2-when-ready-then-retreat-not-split`: name it in the read-back only; the
  parse's split keeps its floor.
- The session cannot hold all three slices at the standard: land IC-7 and IC-8, and hand IC-9 to its own session
  the same day — safe, because "on his own", the thing the old autonomy conflicts with, is not built before
  Session 3. Say so in STATUS.
- New saved fields (the if-then list, used lines, the trial's task, turns and score): `to_dict` / `from_dict` with
  `.get` defaults, `SAVE_FORMAT_REFERENCE.md`, the enforcement test, and the take-back's `ORDER_KEYS` decided field
  by field.

**Done when:** the pins of IC-V1 … IC-V4 and of the moved rows are promoted to behaviour tests and green; §15's
Session 2 done-whens hold; `tools/defect_census.py --open` lists none of those rows; the band is re-read; the
reading meets its bar, or the report says which question it missed. One review before the commit (three readers by
lane, each finding put to a skeptic). STATUS line: *"ROW IC, SESSION 2 — BUTTONS FOR ORDERS, THE LINE FOR TASKS,
EXACT ORDERS"*. Then Session 3 (`docs/INDEPENDENT_COMMAND_SPEC.md` §15).

---

## Row IC, the second commit — directives ✅ BUILT November 19, 2026

Built from the plan the user approved in Plan Mode ("One list for all", "Yes, named armies", "Desk, then
directives"); its record is the landing record in `docs/INDEPENDENT_COMMAND_SPEC.md` §15, the rules
`SYSTEMS_REFERENCE.md` §230, the ledger `BUG_FIXES.md` §IC directives, the readings
`docs/audits/ic_client/directives/README.md`.

---

## Session H: S15 the deploy (the prompt as it stood on November 13–14, 2026 — read it with the lines above; rows BA's and OC's lines overrule it where they differ)

> Two things changed since it was written: **WS-11 is closed** (row BA's BA-1) and **WS-16 is BA-3's**, so the
> weak-spot review brings SIX rows to Session H's head, not seven; and **BA1-X4** and **BA1-X8** join that head,
> with **BA2-X6** (row BA's BA-2: the province panel, scrolled, on a cut line) and **BA2-X16** (its review: the
> four older live-client walk tools and the mutation sweep's missing lock).
>
> The hand-over before row BA: **November 13, 2026 — SESSION UI-6 ✅ LANDED: THE
> LAST READING** (`UI_VISUAL_FOUNDATION_SPEC.md` §14; `SYSTEMS_REFERENCE.md` §217; `BUG_FIXES.md` §UI6;
> `tests/test_ui6_*.py`, `tests/test_parse_preview*.py`). The user's "this is last scoring make all deicisons and fix
> this, while at it please analyze if there are better ways to interact with gernals as well and to make typing
> clicking etc cleaner": every decision ruled (UI-5's eighteen kept, N1–N12 new); the generals rebuilt for play (the
> selection card with seven fixed slots and digits 1–7, right-click orders, the next idle marshal after an order, the
> marshal row, the Generals screen as roster + detail with its orders pinned); typing (the readback line,
> `GET /parse_preview`, never executed; the history's offers on today's board); the fog ruled by the recorded doctrine
> (name and side public, place secret) with every position leak in the live order road fixed (four compound-subject rows left open, at session H's head — (0) below); the crash the measure
> found (a scroll flipping its bar forever in one frame — every ScrollContainer keeps its gutter); blind readers
> 7 / 7 / 7, the mean of the marks 7.07 → 7.43 (every UI-5 six now 7 or 8 but the war room at 2.0). **Session H's walk now includes the user's own look at UI-6:** the frames in `docs/audits/ui_gilt6/`,
> the live walk's in `docs/audits/ui6_mode_c_2026_11_13/`; each decision one switch or one line; the levers the final
> readers name (§14 "What holds it now"), the user's to rule.
>
> The sessions before it: **Session UI-5 (November 13) — the full measure** (§13; sound, pictures, Help & Keys,
> saves; 7 / 7 / 7, mean 7.07) and Sessions UI, UI-2, UI-3, UI-4 (November 11–12, the client's re-skin; §9–§12).
>
> The session before the UI sessions: **November 11, 2026 — SESSION G5 ✅ LANDED: A
> CLIENT RALLIES AGAINST THE HOUSE** (`DYNAMISM_SPEC.md` §7e the landing record, §2b session G5, §8 rows G5-*;
> `SYSTEMS_REFERENCE.md` §211; `tests/test_session_g5_a_client_rallies.py`; ONE sweep with three arms 0 / RALLY /
> ALL on three surfaces, the series re-read). The user's "do what you deem best then tell me what next", to
> session G4's five readings: the commission ceiling, the band and Italy's numbers STAND; the neutral client is
> re-cut — where her lord already fights the aggressor's house a client takes up his war with it and marches on
> its client (`diplomacy.a_client_rallies_against_the_house`), staying out only where her lord is at peace with
> that house; and the sweep's catch — the gate's annexation read counts a house's AUTHORED aims though it stands
> under the survival override (`war_council.the_gate_reads_the_authored_aims`; marengo read 2 on the voice, 0 as
> authored). **Measured:** arm 0 == session G4 byte for byte on both surfaces; the rally moves six ambient seeds
> and the harness's lodi; classes 10 of 10; **the promotion clause MET on TWO seeds again (lodi 33, marengo
> 39)**; the roster in TWO readings (friedland's kingdom falls again); annexations 0 on both surfaces; **the band
> 26 / 26 / 25**; the series unmoved.
>
> The session before it: **November 11, 2026 — SESSION G4 ✅ LANDED: THE
> OPEN READINGS, RULED AND BUILT** (`DYNAMISM_SPEC.md` §7d the landing record, §2b session G4, §8 rows G4-*;
> `SYSTEMS_REFERENCE.md` §210; `tests/test_session_g4_the_open_readings.py`; ONE sweep with eleven arms 0 / FORM /
> WON / LAPSE / REAR / CEILING / ALLY / GUNS / WAGON / HOUSE / ALL on three surfaces, the series re-read; drafted in
> Plan Mode and approved). The user's "evaluate options choose the best", then "and decide and do these":
> fourteen rulings — a nation proclaimed on what it HOLDS at its authored bar (`forms.at`, Italy 3 of 5;
> `forms.first`, Rome then Naples; `formations.backfill_forms` at load); an ally's soil is not won; a pact lapses
> at the vassalage; a backer is no menace; the people drive out a foreign king (and a king named in the treaty is
> seated though his laurels fade); a commission reads the arming ceiling; the Emperor's ally takes no separate
> peace while it wins; no guns from a sanctuary; a bandwagoner joins a neighbour's war; a client joins no war
> against a client of a house it is at peace with (the DD-1 fuzzer's catch); the dispatch drops an overtaken
> capture; the crown row leads the demands; no "§" in the chip. **Measured:** arm 0 == session G3 byte for byte
> on both surfaces; six rules move no ambient seed; classes 10 of 10 on every arm; **the promotion clause MET on
> ONE seed (lodi 33 — marengo's turn-40 crown falls out of the window on CEILING's arm)**; the roster in THREE
> readings; annexations 0 on both surfaces; **the band 26 / 26 / 25** (28 / 27 / 25 before ALLY and GUNS); the
> series unmoved.
>
> Before that: **November 11, 2026 — SESSION G3 ✅ LANDED: A
> CLIENT SWEARS NO PACT OF ITS OWN** (`DYNAMISM_SPEC.md` §7c the landing record, §2b session G3, §8 row G3-CLIENT;
> `SYSTEMS_REFERENCE.md` §209; `tests/test_session_g3_a_client_swears_no_pact.py`; ONE sweep with two arms 0 /
> CLIENT on three surfaces, the series re-read; drafted in Plan Mode and approved). The user's "Rule on clients
> first", then "make best cal for game": **a client's foreign policy is its lord's** — no defensive alliance and no
> alliance is proposed to or from a court that answers to a lord (`ai_diplomacy.a_client_swears_no_pact_of_its_own`;
> `client_in_the_pair` the one read, at the poll's gate and the recipient-addressed road's guard, `reason: client`;
> every lord's clients alike; a non-aggression pact, open borders, the player's own proposals and a standing pact
> untouched); the Vassals card says it (`diplomatic_ledger.CLIENT_POLICY_LINE`). **Measured:** arm 0 == session G2
> byte for byte on both surfaces; ambient no seed moves; **the AI-France harness's annexation line 4 → 0** (the
> Kingdom of Italy is never called into Naples' Roman war; client pacts 19 → 0); the band 28 / 27 / 25; the series
> unmoved (735 bites on the rig); every gate clause as session G2 left it. **Reported:** a freed Kingdom of Italy no
> longer proclaims Italy on the pacts it signed as a client (four harness seeds → none) — put to the user, with
> two smaller readings (a pact brought into a vassalage; a client's non-aggression pacts).
>
> The session before it: **November 11, 2026 — SESSION G2 ✅ LANDED: THE
> PLAYED CAMPAIGN** (`DYNAMISM_SPEC.md` §7b the landing record, §2b session G2, §8 rows G2-*; `SYSTEMS_REFERENCE.md`
> §208; `tests/test_session_g2_the_played_campaign.py`; ONE sweep with four arms 0 / ASK / LADDER / ALL on three
> surfaces, the series re-read; drafted in Plan Mode and approved). A France was played by hand on a fresh seed and
> five defects were fixed at the cause: the king survives the separate peace (`_pair_substitute_seed_terms` carries
> `crowns.CROWN_CLAUSE_KEYS`); the war names the beaten (`crowns.the_war_names_the_beaten` — the pair's score, then
> the burden; the ceding court recognizes the crown it signs); a court at `fight` still asks
> (`ai_diplomacy.a_court_at_fight_still_asks`); the ladder outlasts the rest
> (`ai_diplomacy.the_ladder_outlasts_the_rest`, 24 turns); a backed design dares (`intent.a_backed_design_dares`,
> +10 — the one new mechanic). The marshals' side told (the pick's price, the Generals screen's REIGNING block, the
> rebel king named); the crown row's name opens the king list. **The gate on the shipped tree:** classes 10 of 10;
> Hesse promoted on lodi (33) and marengo (40); the roster {Kingdom of Italy, Papal States} on jena and wagram;
> `annexations_outside_aim` 0 AMBIENT; the band 28 / 27 / 25; the series unmoved. **CORRECTED:** the AI-France
> harness reads 4 provinces kept outside aim (jena and wagram — the cast Naples keeps Milan and Piedmont, the soil of
> the player's own erased client; session G's tree read 2 and its record said 0) — pinned at what it reads, the
> cure the user's ruling on his own clients and "sign at the last" (never a silent 0).
>
> The session before it: **November 11, 2026 — SESSION G ✅ LANDED: THE GATE
> EARNED** (`DYNAMISM_SPEC.md` §7a the landing record, §7 the gate's reading, §2b session G, §8 rows G-PACT / G-CHEST;
> `SYSTEMS_REFERENCE.md` §207; `tests/test_session_g_the_gate_earned.py`, 19 pins; the seams G-PACT / G-CHEST in
> `tests/_t3_seams.py`; ONE sweep with three arms (0 / PACT / ALL) on three surfaces, the series re-read, ONE commit;
> drafted in Plan Mode and approved). The user's word at session F's close: **"Earn them first."**
> **As built:** **no pact with the coveted** (`ai_diplomacy.no_pact_with_the_coveted`; `pact_with_the_coveted` the one
> read; `_evaluate_ai_ai_proposal` wraps `_evaluate_ai_ai_triggers`, `_resolve_ai_ai_proposal` refuses with `reason:
> covets`) — the defect that defused the cast Naples' Roman Expedition at turn 3 (jena, wagram) and Hesse's Westphalian
> Duchy at turn 16 (marengo): an AI court allied the very court whose province it coveted and the ally clause read the
> want as "won". **A crown is bought with the whole chest** (`reforms.a_crown_is_bought_with_the_whole_chest`;
> `_purse_bar` returns the price for `is_promotion` rows; every other law keeps the reserve).
> **The measure (`tools/_gate_measure.py`, `_gate_series_arms.py`; the pins `TestTheSessionGMeasure`):** arm 0
> reproduces session F byte for byte on both surfaces; PACT alone moves jena / lodi / marengo / wagram and earns both
> clauses — **lodi: Hesse's Grand Ducal Title at 33** (Westphalia 25, the aim peace 26); **wagram: the Papal States
> erased at 31** by the cast Naples (the crisis 27, the declaration 29, Rome stormed 30–31), then her war runs on to
> Sardinia and Austria; marengo: Hesse holds Westphalia from 25 under the old bar; jena: Austria's pact with the Pope at
> 23 deters Naples. ALL adds **marengo's crown at 40**. Classes 10 of 10 on every arm; the band 28 / 27 / 26 → **28 /
> 27 / 25**; the harness moves six seeds, promotes nobody; the series unmoved (the pact seam biting 105 times on the rig).
> **THE DEPLOY GATE READS MET IN FULL (§7): classes 10 ≥ 6; a minor at secondary rank by promotion on two seeds; the
> roster in two readings; `annexations_outside_aim` 0 on the ambient record (the harness read 2 — corrected by
> session G2, above); the band inside 23–28; 0 open GR rows.**
>
> **What session G leaves with the user (none blocks the deploy):** (a) **the understudy's reach** — a Naples at war
> with Austria has no authored aim against her, so the conduct rule leaves her free to plunder Piedmont, Lyonnais and
> Limousin from Austria's hands (`captures_outside_aim` 251 → 269): a reading on a court at war without an aim;
> (b) **the chest's number** — the price alone (built), or a half-reserve; (c) **the commanded middle arm** 26 → 25;
> (d) **jena's Pope under Vienna's wing** — the deterrence working, or an understudy's ask-ladder one refusal short
> (`REFUSAL_MEMORY_TURNS`); (e) session F's three, session E's four, session D's three and session C's five stand.

**THEN — SESSION H (`DYNAMISM_SPEC.md` §2b): S15 THE DEPLOY — the user's own walk.** The order: **(0) Session UI-6's
four open rows** (and one note from BA-3's review, not a row: the enemy phase's filter blanks the structured
origin of a march seen to arrive (PT-E5) but leaves the action's `message` string — "… moves from Hungary
to Bohemia" — on the wire; the client never prints it; decide whether the wire should carry it)
(`BUG_FIXES.md` §UI6 — UI6-X70, X73, X74, X75: a report subject naming a friend or a title, a third
clause after an arrival, a friend-only report subject, a title-first list; nothing spent wrongly by any): each is a
strict-xfail pin in `tests/test_ui6_fog_siblings.py` that turns red the day it lands — fix each at its cause, sweep
the class on both roads (`/command` and `GET /parse_preview`; rule 10), re-point the pin to the landing's words, and
the census reads 0 open defect rows before (1) — counting **the weak-spot review's six still open** (`BUG_FIXES.md` §WS, November 14, 2026: WS-10 and WS-12 are the user's rulings, put to them first — WS-11 was ruled and closed by row BA's BA-1, and WS-16 is BA-3's; WS-13, WS-14 and WS-15 fixed at their cause; WS-R's twelve finds each confirmed or refuted; pins in `tests/test_ws_weak_spot_review_2026_11_13.py`) and **BA1-X4** (`BUG_FIXES.md` §BA1: the tableau's lines at Text size 150 % and over; the strict-xfail pin `tests/test_ba1_the_battle_in_acts.py::TestBA1X4TheTableAtLargeType`); **(1) the gate
checks, each against its record file — ROW BA'S BA-4 RECORDS, listed in the head above; the `_g5_*` files named in this
paragraph are the game before row BA** (`PRE_DEPLOY_PLAN.md` §2 S15; `DYNAMISM_SPEC.md` §2 the S15 row, §7):
0 open GR rows (`.venv/Scripts/python.exe tools/defect_census.py --open`); story classes ≥ 6 — 10
(`_dy_signature_g5_2026_11_11.json`, session G5's shipped arm); a minor at secondary rank by promotion on ≥ 1 seed —
lodi 33 and marengo 39, TWO seeds (`_g5_census_2026_11_11.json` `rank_promotions`); the roster varying — two
readings: jena's and wagram's {Kingdom of Italy, Papal States}, {Kingdom of Italy} on eight (the signature's
`eliminations`); `annexations_outside_aim` 0 on the AMBIENT record (`_g5_census_2026_11_11.json` — by session G5's
corrected read; the old read counts 2 on marengo, `_g5_rally_census_2026_11_11.json`) and 0 on the AI-France
harness (`_g5_chain_d_2026_11_11.json` arm ALL), reported, never gated; the France band 23–28 — **28 / 28 / 27
(`tools/_ba4_band_2026_11_16_k50.json` — row BA's BA-4, the final tree; the readings of 26 / 26 / 25, 26 / 27 / 28 and
28 / 27 / 27 before it are the game before that session)**;
the historian test green on every seed (the suite's pins); the ratchet (`tests/test_code_health_ratchet.py`); the
parse harness green; **(2) the build** — `deploy\build.bat`, UNSIGNED until the certificate arrives
(`SYSTEMS_REFERENCE.md` §153.3–§153.4, `UX_UI_REVIEW_PLAN.md` §UXR-4: nothing on this machine — no signtool, no
certificate in either store; the day it arrives, `INK_IRON_SIGNTOOL_ARGS` / `SIGNTOOL` and the same script);
**(3) the clean-environment run** (a fresh clone, the venv from `requirements`, the hook installed with `Copy-Item
scripts/git-hooks/pre-commit .git/hooks/pre-commit`, the backend as `-m backend.main`, the client from the export, one
forty-turn Mode C walk by the user — `docs/PLAYTESTING.md`; the walk is also the user's first look at row BA's battle table in motion (the readers' blind marks were not taken for it: his look is the reading) and at Session
UI's new skin — the gilt frame, the desk, the books as cards, End Turn gilt on a spent day — its before / after pairs
in `docs/audits/ui_gilt/`, its reversals one line each, `UI_VISUAL_FOUNDATION_SPEC.md` §9); **(4) the release record** (the commit SHA, the gate's
readings with their record files, the certificate's state, the user's walk's notes — `SYSTEMS_REFERENCE.md` §211,
`STATUS.md`). **After the deploy** (`PRE_DEPLOY_PLAN.md` §2; no cuts without consent, spec §0): S14k-3 (Spain alone),
S16, S17c.

**The commit:** session H's commits are the user's walk's — the release record and any gate fix each its own commit
through the hook (about 10 minutes; never `--no-verify`); push only on the user's word.

**Session G5's own traps (fresh):** a gate number that moves is READ TO ITS CAUSE before it is believed — replay
both arms and put the read's inputs side by side (marengo's 2 was the instrument: a court under the survival
override has no design voice, so `_house_aims` read empty; `authored=True` is the deck as written); the three-arm
sweep on three surfaces takes about seven minutes — re-run it WHOLE on the final tree; a rule that removes a war
pair to keep an invariant has a sibling that completes the war instead — play the real road
(`vassal._client_takes_the_field`) before choosing; session G4's own neutral-client pin holds G5-RALLY down; an
ally's branch of the cascade is untouched (the fuzzer exempts a bought client's pairs — it leads its own war);
`( cmd & )` in a shell loop is not waited on by `wait`; STATUS holds 7 "▶ ▶ ▶" entries (session D archived).

**Session G4's own traps (fresh):** PLAY THE RULES OUT BEFORE THE SWEEP — three restarts here, each for a
fix the played checks found mid-measure (a freed Italy aimed at France, not Rome; a king's laurels fading before
ratification; the fuzzer's latent I2); the deck rides the save — a new authored key on an existing deck entry
needs `formations.backfill_forms` (entries are never added: the AI-0d precedent stands for goals), and only the
client walk on an OLD save shows it; an acquire design's obstacle is the FIRST unmet target in its order
(`forms.first` leads it for a forming design); `_court_demand_suggestions` sits at exactly 500 lines — wrap at
its call; a rebelling client still carries its lord's row while the war cascade runs; the treaty fuzzer's ledger
is a zero ratchet and a shifted world-line can reach a latent class — bisect by holding each seam down
(`treaty_fuzzer.run_seed`); the glob `_dy_signature_g4_*_2026_11_11.json` does not match the shipped arm's
record; T2-3's, T3-4's and T3-5's own stagings hold G4-WAGON / G4-ALLY down by autouse fixtures; CLAUDE.md is
patched on bytes under its script's 62,000 assert; STATUS holds 7 "▶ ▶ ▶" entries (session C archived).

**Session G3's own traps (fresh):** the AMBIENT surface cannot see a client rule — the idle France's kingdom is
gone by turn 23 on every seed; the harness and a commanded France are its surfaces; the harness's France refuses
every petition and loses its clients (`final.vassals` is empty on most seeds) — read a client's story off the events
(`vassal_broke_free`, `vassal_defected` with `outcome: free_*` or `transfer`, `vassal_transferred`); a harness
`formations` entry is a proclamation a freed client can reach through the ally clause (`agendas.region_coveted`
reads a target in an ally's bloc as met) — read the design's list before believing it gathered anything;
`_UPGRADE_ORDER` starts at WAR and the first step above PEACE is OPEN_BORDERS; `tools/dd_b_play.py` loads a save
copied into `<run>/saves/` before `start` ("Load a Campaign…" lists it); CLAUDE.md is patched on bytes and held
under 62,000 LF bytes by its own script's assert; STATUS holds 7 "▶ ▶ ▶" entries (session B archived); **stopping a
background commit orphans the hook** — git dies, `sh .git/hooks/pre-commit`, the pytest controller, its workers and
any headless engine run on (27 processes): find them by `ParentProcessId` from the hook's `sh` and stop the tree
before committing again, or let the commit finish; `test_ep_f4`'s `_decisive_win` rolls on `DECISIVE_ROLL` since
this session (unseeded, seed 261 left 69 of Mack's 900 to escape and failed the hook's first run).

**Session G's own traps (fresh):** the AI–AI poll's body is `_evaluate_ai_ai_triggers` — a gate on its outcomes wraps
it, never sits inside it (0a's alignment arm must still exclude the obstacle, the design ask must still pass);
`get_agenda_covets` already excludes an ALLY's soil, so `pact_with_the_coveted` reads the live deck and never undoes a
pact already standing; a `crisis_passed` with `cause: satisfied` after a treaty is the ally clause speaking — check
the pair's state before believing the want was won; `spawn_run(seed, 10000, 40)` from `tools.ai_v_sweep` gives a
seed's whole story in five seconds — the digest's `intents` (per court: design, against, weight, rung) and
`wars_opened` rows are the diagnosis; the census's `signed_cessions` consequence lines carry the indemnity ("Hanover
pays 243 gold"); `test_sf_lb2`'s caller census names the poll's body by function name; the Awakening's beats move
when a people's court is erased (the Pope's gone with Rome); CLAUDE.md sat at 61,988 LF bytes after this session's
trims (12 bytes of headroom — the next row trims first); STATUS holds 7 "▶ ▶ ▶" entries (session A archived).

**Session F's own traps (fresh):** a `gold` clause prices ZERO burden — the dialect's names are `gold_lump` (bilateral)
and `gold_indemnity` (settlement), `territory_cede` with `regions`; Russia's seat on the drawn map is **Vilna** (the
Alarm's `_seat` → `seat_as_metonym`), never St Petersburg; a vassal pair trades nothing (`calculate_trade_breakdown`
skips it) — a client-side trade price is an empty set; `filter_campaign_log` sits at EXACTLY 500 lines — a new
court-knowledge type joins `levee`'s line, never its own; `calculate_acceptance` is already 630+ lines (counted among
the 28); the Net components have a cross-file tripwire (`test_economy_ledger_reconciliation.EXPECTED_NET_SIGNS`) and
the scorer's components three set pins (`test_ca8_gate_closeout`, `test_common_peace_acceptance`,
`test_settlement_guided_terms_slice3`); the census pins are SEVENTEEN now (the sixteen `== N  # …` lines plus
`test_dy5`'s bare one) and `test_iq7`'s unexplained check names every slice tag; the carved people's scalar lives under
the vassal row's `carved_from`; the Neapolitans are already stirred by the carve (`AW.move` adds to a live row); a
Python patch script that inserts after an anchor is NOT idempotent when the new text begins with the anchor — guard
with `if new in text`; the Godot parse report regenerates with `Start-Process … --headless --quit --path
godot-client/project-sovereign --script ../../tools/godot_parse_check.gd` AFTER the `.gd` edits (exit 0, 13 KB).

**Session E's own traps (fresh):** the guided rows hang on `per_court_acceptance[]` (the confirm popup's
`_per_court_row`), each court's `demand_suggestions[]` — not on a `per_court_rows` key; `_demand_clause_label` is
the table's clause-words function in `settlement_actions`; `world._starting_controllers` is the Europe map's
starting-controller read (`get_starting_controllers()` bare is the legacy world's); a peace treaty has its OWN
trust reactions (Soult −5 on the Naples peace) — a trust pin reads against a control carve of the same board; the
threat slot caps at 100 (`min(100, before + 12)`); `display_nation` does not know a formed name — use
`formations.formed_display_name`; `formable_nations` templates are validated in the `validate_scenario` loop
(`_validate_crown_block` beside the `seeds` check), the top-level block in `_validate_crowns`; a new heraldry SVG
needs its `.svg.import` sidecar — a headless `--import` pass writes it (`Start-Process … --headless --import --path
godot-client/project-sovereign`), then `git add -f` both (the ignored `assets/`) and a line in
`THIRD_PARTY_LICENSES.md`; the parse report regenerates with `--script ../../tools/godot_parse_check.gd` AFTER the
`.gd` edits; the gift's two pins (`test_dy2` `TestTheEmperorsGift`) hold `a_victor_erects_a_crown` down — their
board is the AI road's live case; `CARVE_TAGS` + `CROWN_TAGS` in `test_nation_agendas_formables` (the catalogue
census 10, the Formables page 12); the jealousy council's stash is `world._pending_jealousy_turn_events`; the
seam-down strike keys on `crown.since == "DY-6"` (an older template keeps its place, its block struck); a
measure's four arms with ten harness seeds each ran 28 minutes alone, the series 3 beside it.

**Session D's, C's, B's, A's and the earlier traps:** unchanged from the prior prompts — read them in the archive's
copies (`git show 90bada87:docs/NEXT_SESSION_PROMPT.md` for session D's, `git show 2589f3c1:docs/NEXT_SESSION_PROMPT.md`
for session C's, `git show 93f82fb2:docs/NEXT_SESSION_PROMPT.md` for the earlier), every one still binding.

**Open with the user beyond session H's head (none blocks the deploy):** session G5's readings
(`DYNAMISM_SPEC.md` §7e — Switzerland bought on six unattended seeds; friedland's kingdom falls again; the gate's
read corrected in the session that tripped it; the ally's branch); session G4's five are RULED (§7e), session
G3's three and session G2's list are RULED (§7d); session G's four
readings above; session F's three levers (`DYNAMISM_SPEC.md` §6c); session E's four readings (`DYNAMISM_SPEC.md` §6b); session D's three
(the letter's floor; the levée's reach; the dial's ambient road); session C's five (the march does not visibly bleed
— the ulcer's teeth; the letters' seat at the desk; the bands' pace; the raised gate's clauses 2 and 3; the pacing
record's drift); session B's three (the envy's cap at the coerce floor too; the crowns after the gift; no second
great-power war on the 1805 board — the content levers); GRD-38; GRD-37; the design rows of `DESIGN_REFINEMENT.md`
§GRD; the flip's two readings (`AUTHORITY_CURRENCY_SPEC.md` §6.8.3); the Crown's readings (`EVENTS_SPEC.md` §18);
the road record's readings (`VP1_DESIGNS_SPEC.md` §14.6); S14d's A1; AO's three questions (`REFORMS_SPEC.md` §5a);
the crown term's level; SF-NAV-1-D1; Britain's letter without contact; the hook's remaining levers; the two
hash-seed orderings with no reader yet checked. (`test_ep_f4`'s flake is CLOSED — session G3's hook caught it and
its helper now rolls on a fixed seed.)

**After session H — the session plan (`docs/DYNAMISM_SPEC.md` §2b; no cuts without consent, spec §0):** the deploy
is the last session of the plan. **After the deploy:** S14k-3 (Spain alone), S16, S17c (`PRE_DEPLOY_PLAN.md` §2).

**Traps the rows have paid for (do not re-discover):** the ratchet has NO headroom — levers 231 of 231
(seams are named functions, zero-arg, in the module they gate), functions over 500 lines 28 of 28,
`WorldState.to_dict` 497 of 500 (every new field in an existing store), CLAUDE.md within 62,000 LF bytes
(27 bytes of headroom after session E's `crowns.py` row — the next row trims first), STATUS at most 7 "▶ ▶ ▶"
entries (archive the oldest to the top of `docs/archive/STATUS_2026_Q4.md` — session E archived THE LEDGER);
every `except Exception` must speak; a measure chain runs ALONE and no backend, test or deck edit lands while it
runs; **a sweep or driver PARENT runs PLAIN, never `-X utf8`**; **never pipe a measure's output through `tail`
into the task file**; a probe itself runs under `python -X utf8` when IT prints; the recorded boards' hold-list is
`tests/_oct27_seams.py` (it folds `tests/_t3_seams.py`'s rows — a new seam goes THERE); **a record superseded but
still pinned is KEPT under a dated or named file and its pins re-pointed**; the rig-record pins in
`test_ai_drill_fix_2026_09_27.py` re-link through `SERIES_BEFORE_*` constants when the live constant moves on; the
bytecode pins fail under the shell's `PYTHONDONTWRITEBYTECODE=1` (run pytest and the commit with `env -u
PYTHONDONTWRITEBYTECODE`); the driver reads `--seam`, never `INK_IRON_SEAMS`; every rig shim passes through `*a,
**k`; a rig re-run writes its OWN record (`--out`); the scenario and every asset sidecar sit under the ignored
`assets/` — `git add -f` them; the docs are CRLF or LF per file (STATUS, SYSTEMS_REFERENCE, MODDING_FORMAT, CLAUDE.md,
the archive CRLF — patched on bytes; DYNAMISM_SPEC, SAVE_FORMAT_REFERENCE and this prompt LF); the deck JSON files,
the scenario and the golden corpus are hand-formatted — insert text, never re-dump; the three decks are one deck,
in lockstep; commit with `env -u PYTHONDONTWRITEBYTECODE git commit -F <file>` from Bash in the background (the
hook runs ruff and the full suite, about 8.5 minutes; never `--no-verify`) and read the log's EXIT line; a test
module that opens a Godot WINDOW or starts a sandboxed backend joins `ENGINE_LANES["engine"]`; a `.gd` edit with
the morning's parse report FAILS the hook (regenerate `tools/godot_parse_report.json`); `tools/playtest_runs/` is
gitignored; `get_visible_enemies` is the PLAYER's fog; a rung's structured field reaches the executor only
through `enemy_ai.execute_admin_phase`'s whitelist; an UNQUOTED Bash heredoc runs every backticked name in
its body as a command — write every script with the Write tool; the cheapest proof that a change moves
nothing is the keyed world probe (`to_dict` per turn, one hash per top-level key, against a `git archive
HEAD` copy, `PYTHONHASHSEED=0`).
