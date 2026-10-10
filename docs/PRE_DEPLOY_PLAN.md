# The Pre-Deploy Plan — code health, the UX/UI review, and three deep dives

> **Status: PLAN, October 8, 2026. Nothing under it is built.** Written at the
> user's direction: *"organize next steps. first of all we should organize code
> so its easier to fix and debug … make plan for ux and ui review … prioritize
> them then choose key weak spots for a full deep dive before we deploy game."*
>
> This is the umbrella. The two plans it orders are
> `docs/CODE_HEALTH_PLAN.md` (rows CODE-1 … CODE-6) and
> `docs/UX_UI_REVIEW_PLAN.md` (rows UXR-0 … UXR-4). The deep dives are DD-A,
> DD-B, DD-C below. **While this plan runs, the Score Finish residue
> (`SCORE_FINISH_SPEC.md` §3 Step 9, SF-RR1 (ii) … RR6) is PAUSED behind it**
> and resumes at position 10 — the user may re-order.
>
> Every number here was measured on this tree at `4680b361` on October 8, 2026
> with `tools/_code_health_census.py` (new, read-only) and the greps recorded in
> each plan. Re-run the census before building a row; the counts drift.

## 1. The picture

**The game is scored at 7.4–7.5 and still ships a bug every forty seconds of
fresh play.** The final reading's hand-played campaign filed **16.5 defect rows
per 10 turns**; the scripted arms file **0.4**. The 30,000 pins guard the roads
already walked. Two things make the next fifty fixes expensive:

- **The code cannot be held in one head.** 247,116 backend lines; 26 files over
  3,000 lines; **34 functions over 500 lines**, the largest `_execute_attack`
  at **3,945 lines and 382 `if`s**. Every review round since September has
  found a P1 *inside the fix*, and the record says why each time: the function
  the fix touched was too large to see the seam it broke.
- **The scaffolding is still up.** **665 module-level flip levers, 661 ON**,
  each keeping an old branch alive so a test can flip it back (748 test arms set
  one to `False`). **397 `except Exception` handlers, 368 of them neither log
  nor re-raise** — the class that hid the save failure (FA-S15-2) for as long as
  it existed. The session docs cost every session: `CLAUDE.md` is **524 KB**,
  `STATUS.md` **1.6 MB**, `BUG_FIXES.md` **2.2 MB**.

**And the client is unreadable on the user's own monitor.** The tutorial card is
a 396-px fixed rect of 12–13-px type; the project sets no stretch mode and no
DPI detection, so the interface draws at 1:1 physical pixels on an ultra-wide
with Interface Scale defaulting to 1.0 and capped at 2.0. ~~Only four surfaces
have a resize grip.~~ *(Corrected October 9 by the adjustability census: ONE
grip — the terminal's — and a hidden, unsaved edge-drag on the war HUD; the
"four" was a grep matching* the Emperor's grip *in two files.)* The IQ-10
capture harness shoots a 1600×900 window at scales 1.0 and 2.0 — it has never
produced the frame the user sees, which is why 262 clean frames and a "UI/UX
7.5" coexisted with the report. *(Measured October 9: the user's monitor is ONE
5120×1440 panel at 100% Windows scaling, not the 3440×1440 this plan assumed;
and the capture window had been parked ON it, at x = 2565, for every run since
September.)*

None of the code-health rows changes what the game does, so none moves the
score; their gate is **byte-identity** (series, M1–M7, corpus, the score arms'
digests). The UX rows change only what the player sees; their gate is a
measured readability floor and the user's eyes.

## 2. The order

Sizes are sessions. Each code slice carries the byte-identity gate; each UX
slice carries the readability instrument's reading and ends with frames at the
three resolutions. The head of every session from S2 on takes one lever batch
(CODE-1) before its main row.

| # | Row | What lands | Size | Why here |
|---|-----|-----------|------|----------|
| ~~S1~~ **S1a ✅ LANDED October 9, 2026** | **UXR-0 + UXR-1** | The readability instrument (physical-pixel text census at 1920×1080 / 2560×1440 / 3440×1440 / **5120×1440** / 3840×2160) and the fix with the widest reach: Interface Scale auto-derived from the screen at first boot, the cap 2.0 → 3.0, a theme text floor, the first-run "can you read this?" card. **Landing record `UX_UI_REVIEW_PLAN.md` §UXR-1 landing record: named set RED 255 → 0, P1 750 → 0; the user's eyes = UXR-4.** | 1.0 | The user's report; first contact is the tutorial and it cannot be read. Smallest change, largest reach. |
| ~~S1b~~ **✅ LANDED October 9, 2026** | **the Settings additions** (the adjustability review's decisions 4 + 5) | Window mode + size picker; the terminal's default footprint as a viewport fraction; Ctrl+= / − / 0; Reset layout; a CONTROLS reference; the *Body text: Garamond · Plain* option; the sizing card from Settings — and the floor's residue from the whole-client census (the log tiers, six 15s). **Landing record `UX_UI_REVIEW_PLAN.md` §S1b landing record; named set still RED 0 / P1 0.** | 0.5 | Cheap, same seams; the review's "is anything missing" answer |
| S2 step 0 ✅ **LANDED October 9, 2026** | **the hook pays its way** | The pre-commit hook runs the full suite under pytest-xdist (`-n 8 --dist loadgroup`): serial 26:13 → **5:12** measured, the gate whole; two order-dependent pins fixed (an unseeded 30-draw dice test; an endpoint pin reading whatever world the previous module left in `backend.main`); the stall under xdist traced to child processes inheriting the worker's execnet stdin (now DEVNULL in a worker). Record: `CLAUDE.md` Workflow + Commands. | 0.3 | The user's October 9 ask ("it takes sooo long"); every S2 commit after it pays the new price. |
| ~~S2~~ ✅ **LANDED October 9, 2026** | **CODE-4** (record `CODE_HEALTH_PLAN.md` §CODE-4) + **CODE-1 batch 1** (record §CODE-1; 20 of the batch's 46 levers retired — the 26 that landed in October keep their session; `tools/retire_lever.py` + the ratchet pin) | The docs diet (CLAUDE.md → rules + a one-screen state; STATUS/BUG_FIXES history to archives, the census tool reading both) + the lever-retirement tool and its first 100 levers | 1.0 | Pays back every session after it. The tool is proven on small modules before the monsters. |
| ~~S3~~ ✅ **S3 LANDED October 10, 2026** (the instrument — §3.0 landing record: the parse trace + the typed `why`, the metamorphic corpus 2,100 cases / 161 in the ledger, the third blind set 137 / 152 of 300; **S3b the same day: the findings fixed — the ledger 161 → 30, the blind set 162 / 170 of 300, 0 executed-other-than-meant**; S3's head **CODE-1 batch 2** ✅ **LANDED October 10, 2026** — 83 of the game_logic batch's 138 levers retired, 56 October ones kept; levers 645 → 562; record `CODE_HEALTH_PLAN.md` §CODE-1) → **S4 IN PROGRESS: part 1 ✅ LANDED October 10, 2026** (the Reading + the exit predicate + the vocabulary — §3.0 "S4 landing record, part 1": the ledger 30 → 0, the third set re-read 162 → 177, the sixteen command rows struck); **the HOLD arm re-read 12 → 18 of 20; next = the spine split, then the FRESH fourth-author set** | **DD-0 THE COMMAND ROAD** | The one deep dive the user asked for (§3.0): the parse trace on every response, the metamorphic corpus, a third blind author set, one `Reading` object through the pipeline (absorbs CODE-2's `_parse_with_mock_chain` + `_execute_one` splits), the "did I do what was named" predicate | 2.0 | The game's premise; the largest open pillar; where every review round found a P1 inside the fix. |
| S5–S6 | **DD-1 THE TABLE AND THE TREATY** | The diplomacy deep dive (§3.1): one `can_sign` verdict read by every surface that shows a letter, a chip, a price or a counsel line AND by the ratifier; the treaty state-machine fuzzer over the §70/§81 invariants; the three unbuilt verbs the depth campaign reached for | 1.5 | The second-largest open pillar by weight (10 rows, 5 P2); the quarter's P1s were all "the table said yes and the treaty said no". |
| S7 | **CODE-3** + **DD-C** | One `errors.swallow(ctx)` helper through all 368 silent handlers, narrowed where the type is obvious, a ratchet pin; **the save path raises and the player is told**; save/load fault injection over a 40-turn run | 1.0 | The silent class is the one that produced an invisible P1. |
| S8 | **CODE-2a** | `_execute_attack` split into named stages behind one context object; pure refactor | 1.0 | The single largest function; every combat fix since July touched it. |
| S9 | **UXR-2** | The layout law: every panel anchors to a viewport fraction or clamps; a grip on the five big screens; the tutorial card resizable and theme-sized; the 268 font-size overrides reduced to named theme sizes | 1.0 | "Only some boxes are adjustable." |
| S10 | **CODE-2b** | The monster functions the two deep dives did not absorb: `execute_command`, `format_event_oneliner`, `_execute_strategic_command` (one each, as S8) | 1.0 each | DD-0 takes `_parse_with_mock_chain` + `_execute_one`; DD-1 takes `_process_dialogue_choice` + `_ratify_treaty`. |
| S11 | **UXR-3** | The look-and-feel review: every surface scored on the 8-item UX checklist at three resolutions, by three blind readers, fixes filed | 1.0 | The "full look feel ux review." Needs UXR-0's frames. |
| S12 | **UXR-3 fixes** | The review's own rows, worst surfaces first | 1.0 | |
| S13 | **DD-B** | Three fresh-eyes hand-played campaigns IN THE CLIENT at the user's resolution, three roads (conquest / diplomacy-first / the sea); defects per 10 turns as the metric | 1.5 | The 16.5 is the honest number; nothing else measures a new player. |
| S14 | **SF-RR1 (ii) … RR6** | The Score Finish residue resumes | per spec | |
| S15 | **UXR-4 + the deploy** | The user's sign-off at their monitor; the release build; the clean-machine run | 1.0 | |
| later | **CODE-5 / CODE-6** | File splits (`world_state.py`, `diplomacy.py`, `main.py` routers) and the `main.gd` split | 1.0 each | Only after CODE-2; lower payoff per session. |

≈ 15–16 sessions before the deploy, with CODE-1 finishing in the heads of S2–S13.
DD-0 and DD-1 are the two headline deep dives (§3.0, §3.1); DD-A, DD-B and DD-C ride their own rows.

## 3. The deep dives

A deep dive is a row that gets a session of its own, a fresh instrument, and a
written done-when, because the score instrument cannot see it.

### DD-0 — THE COMMAND ROAD: the one component that needs the most attention (S3–S4)

*The user's October 8 ask: "one deep dive for a component of the game that
might need most attention to really elevate things or catch bugs." This is
the pick, with the evidence.*

- **Why this component.** The game's premise is a typed line. Every pillar is
  reached through it, and the keyless mock chain is what the shipped default
  gives every player without a key. It is the largest open pillar (**16
  rows, 9 P2**), it held the final reading's only P1 (`march home to
  Franche-Comte` marched to Lorraine), and the depth campaign's worst class
  lives here: **the game did something other than what was typed, without a
  word** — a drill carried out where he stands instead of at the named
  province (SFR-D7), cavalry asked and infantry paid (SFR-D41), `drill your
  guard` turned into a standing HOLD (SFR-D9), the second half of a compound
  dropped and reported done (SFR-D10, D38). On the fresh blind HOLD set,
  questions read 149 of 150 after the state desk; **orders read 11 of 20.**
  Orders are the gap.
- **Why it keeps breaking.** 27,131 lines across fifteen modules
  (`llm_client.py` 4,559 · `executor.py` 3,881 · `parser.py` 3,768 ·
  `state_desk.py` 2,930 · `dialogue_routing.py` 2,234 · `clause_guards.py`
  2,050 …). The raw text is read by THREE producers in series (the mock chain,
  the strategic layer, the fuzzy target scan), so the guards must blank with
  spaces to keep positions aligned, and a fix to one reader ships a hole in
  another — slices 1, 7, CRT-1, PARSE-NEG and the IQ-7 answer grammar each
  had a P1 found inside the fix by the review round, every time by adding the
  clause the builder had not. `_parse_with_mock_chain` is 1,644 lines whose
  behaviour depends on keyword ORDER; `_execute_one` is 2,173. No other
  component has that signature.
- **The instrument.**
  1. **The parse trace.** Every stage (typo repair, guards, question/condition
     readers, the mock chain, the strategic layer, fuzzy matching, carryover,
     the executor's pre-gates) appends `(stage, span, rule, before → after)` to
     a `parse_trace` list that rides the response under debug and is printed by
     a typed `why` (free, a question). A misread becomes a one-line diagnosis
     instead of a session.
  2. **The metamorphic corpus.** From the 614 golden rows, generate variants
     that must NOT change the reading — politeness, contractions, honorifics,
     a trailing reason clause, a typo in the verb, word order, "please", the
     second name as a role — and variants that MUST flip it to a refusal or a
     question — a negation, a modal question, a hedge. Thousands of cases from
     614 authored ones; it catches by construction what the review rounds have
     been catching by hand.
  3. **A third blind author set.** 300 orders written by someone who has not
     read the project's vocabulary, run keyless and keyed through the real
     `POST /command`, judged by the ONE judge in `tools/_score_probes.py`.
- **The structural fix that falls out.** One tokenised `Reading` object
  (spans, not a mutated string) carried through every stage, so no stage
  re-reads the raw text and nothing blanks with spaces. This IS CODE-2's
  `_parse_with_mock_chain` and `_execute_one` splits, done with a purpose, and
  the trace comes free from the stage boundaries. And one predicate at the
  executor's exit, *"did I act on the marshal, place and arm that were
  named?"*, so a substitution is disclosed or refused, never silent (closes
  SFR-D7 / D9 / D41's class structurally).
- **Done when.** The blind set reads **≥ 85% of orders as meant keyless**
  (the committed fresh census reads 73 of 150 as meant, 53 before part (ii));
  **0 executed-other-than-meant** across the blind set and the metamorphic
  suite; HOLD orders ≥ 17 of 20; the 16 open command rows closed or re-homed;
  the trace on every response; the corpus still 614 of 614 and the series
  byte-identical (the parser is player-only).
- **Why first.** Diplomacy is the other component of this weight (DD-1,
  below, added October 9 at the user's word); it runs second because half its
  defects reach the player through this same typed line, so the trace and the
  `Reading` object are its instrument too. Readability is already S1. Combat
  legibility's misses are display rows the UXR-3 review will reach.

#### DD-0 S3 landing record — the instrument (October 10, 2026)

**All three instruments built, no parser rule changed, the series byte-identical.**
Rules `SYSTEMS_REFERENCE.md` §100 (the trace + `why`), §101 (the metamorphic
corpus), §102 (the third blind set); pins `tests/test_dd0_parse_trace.py` (29),
`tests/test_dd0_metamorphic_corpus.py` (14), `tests/test_dd0_third_blind_set.py`;
memos `docs/audits/METAMORPHIC_CENSUS_2026_10_10.md`,
`docs/audits/UNREHEARSED_CENSUS_2026_10_10.md`; findings `BUG_FIXES.md` §DD-0 S3
(DD0-1 … DD0-10, all owned by S4).

1. **The parse trace** (`backend/ai/parse_trace.py`). One contextvar per
   `/command` request, opened at the door and closed by `build_base_response`
   on every reply road, so it is on EVERY response; a no-op outside a request
   (a direct `parser.parse` pays one `None` check per stage). Rows
   `(stage, rule, span, before → after)` for a rewrite — recorded only when
   something changed — and `(stage, rule, detail)` for a decision; the first
   row is the typed line, the last the ONE terminal `reply · done | refused |
   asked`. Hooked at 60-odd sites: `main.py`'s routers, carryover, premise,
   the request-field override, CR-5, the focus reissue; the parser's ten
   pre-rewrites, six normalisers, the question check, the five splits, fuzzy
   matching, validation, the strategic text build and target override; the
   mock chain's four guards, filler, PARSE-NEG's refusal with its kind, the
   chain's result (its `interpretation` names the arm) and the live
   escalation; `detect_strategic_command`'s prefix / type / target / the
   SFR-D11 relative-place seam; the executor's gates (unbound addressee,
   proper-name ask, auto-attack, standing decision, literal-marshal ask,
   auto-assign scout, **the recruit arm's substitution — SFR-D41's class, now
   disclosed**), an entry-vs-exit `command_changed` row that names every
   in-place substitution without a hook at each site, and the dispatch. On
   the wire under `parse_trace` when the request says `trace: true` or
   `SOVEREIGN_PARSE_TRACE=1`; the world keeps the last trace on a transient
   `_last_parse_trace` (never serialized). **The typed `why`** (`why`,
   `why?`, `why not`, `explain`, `what did you read`, `how did you read
   that`) prints it, free, no history entry, standing (`why` twice prints the
   same order); a `why` with a subject is the state desk's.
2. **The metamorphic corpus** (`backend/ai/parser_metamorphic.py`,
   `tools/metamorphic_census.py`). Twelve families over the 128 order rows of
   the 614: nine `same` (please, honorific, reason tail, dash aside,
   contraction, leading-verb typo, address to the tail, the second name as a
   role, lowercase), one `refusal` (negation), two `question` (modal, hedge),
   each with an applicability predicate (§101 lists the exclusions), judged
   against the parse of the ORIGINAL on the same board. **2,100 cases, 161
   failed — the flip families ALL hold (negation 0 / 190, modal 0 / 60, hedge
   0 / 338: nothing negated ran, no question ordered).** The `same` failures:
   dash aside 70 (the aside becomes the province), second name 31 (`Ney,
   attack Mack with Lannes in support` → a SUPPORT with a generic target —
   the first man's order LOST), please 30, reason tail 18, word order 8, typo
   3, honorific 1; by the trace's last stage `strategic ·
   target_overrides_tactical` 90, `parser · validation_failed` 47. The 161
   are the committed ledger `tests/data/metamorphic_known_failures.json`; the
   harness pins no failure outside it and a count that only falls — S4's
   worklist, pre-attributed by stage. (The generator's first run read 183;
   22 were the generator's own — a negation before a filler or a first
   person, a two-clause line, `Gen.` read as a name — and are excluded by
   rule, recorded in the memo.)
3. **The third blind author set** (300 orders, 31 traps, an agent with no
   repository access; `tools/unrehearsed_census.py --trace` stores each
   row's trace). **Keyless 137 of 300 as meant (45.7 %), keyed 152 (50.7 %,
   64 live parses); the keyed arm closes 40 of the 41 keyless shrugs.** Of
   the judge's 19 dangerous rows, nine are the parser's — `Ney, attack
   Davout` and `everyone — attack everything` attacked the nearest enemy
   behind a disclosure (DD0-1, the exit predicate's own case); `go to
   Gelderland and wait there` / `go to Berlin — no wait, Dresden` lost the
   march to the WAIT arm (DD0-2, SFR-D9's class); `ride to Lannes' aid` →
   a generic SUPPORT resolved to Bernadotte (DD0-3); `drop off a few
   battalions to hold Franconia` → a 2-AP HOLD (DD0-4); `what's in Tyrol?
   Massena, find out` dropped the order (DD0-5); `War with Portugal` → an
   advisory (DD0-6); the contradiction fought (DD0-7) — and ten are honest
   replies in shapes the ONE judge does not know (DD0-8: ten regex
   alternatives, each to be grepped against the committed records and the
   HOLD arm's archive before it lands; the judge is unchanged in S3). The
   shrugs (DD0-9) and the parser's honest refusals (DD0-10) are listed in the
   memo. Each dangerous row was attributed in one read of its trace.

**Gate.** `score_run check` against `docs/audits/score_runs/2026_10_05_sfr/`
identical to the same check on `c33683cd` in a detached worktree (112 items,
0 moved, scores equal, stdout identical; the archive restored after each);
corpus 614 / 614 (the harness's 913 green); the October 3 census records
re-read unchanged; the code-health ratchet untouched (no lever, no new
`except Exception`); ruff clean; the full suite green on the hook.

**Done-when, where it stands after S3:** blind orders as meant keyless 45.7 %
(≥ 85 % wanted, on a FRESH set); executed-other-than-meant 3 by hand on the
blind set, 0 on the metamorphic suite's 588 flip cases (0 wanted); HOLD
orders not re-read in S3 (12 of 20 at the last reading, ≥ 17 wanted); the 16
open command rows untouched (S4); **the trace on every response ✓; the corpus
614 of 614 ✓; the series byte-identical ✓.**

**S3b — the findings fixed (the same day, the user's "fix the bugs").** Rules
`SYSTEMS_REFERENCE.md` §103; pins `tests/test_dd0_s3b_the_fixes.py` (41) + 27 corpus
rows `dd0-*` (the corpus 614 → 641); the ledger rows DD0-1 … DD0-8 FIXED, DD0-9 and
DD0-10 HALF FIXED (their remainder S4's). The pre-parse rewrites
(`backend/ai/dd0_rewrites.py`, first in `parse`, each on the trace): the please and
the urgency, the dash aside, the because-tail, the self-correction, the arrival wait,
the second man in support (→ the relay), the sent marshal, the kill and the field's
battle idioms, the reward idiom, the invested gold, the trailing end turn; the arms
widened (the garrison idiom above the hold, the declaration as a fact, the
contradiction refusal, scout / fortify / drill / square / fleet / expedition / move /
the bare cabinet, the typo pass); the telegraph's separators and the inflected order
through an honorific and a modal; the possessive aid in the strategic layer; an attack
on our own marshal refused by name, `attack everything` asked, in the executor; the
judge's ten shapes (the October 3 records re-read identical, the archive's items
identical, the committed landing records re-read on the by-hand split 6 + 3 / 6 + 3).
**Measured on the same blind file, fresh records: keyless as meant 137 → 162 (54.0 %),
shrugs 41 → 6, misread 0, executed-other-than-meant 0; keyed 152 → 170 (56.7 %),
0 / 0. The metamorphic ledger 161 → 30 (dash aside 70 → 0, please 30 → 0, honorific
→ 0; the flip families still 0).** No lever (the ratchet holds levers lower-only); the
series' items identical to the pre-slice check.

**S4 takes:** the `Reading` object (spans, never a mutated string — the answer
to the 90 `target_overrides_tactical` rows and every "the tail became the
province" class) with `_parse_with_mock_chain` and `_execute_one` split along
the trace's own stage boundaries; the exit predicate *"did I act on the
marshal, place and arm that were named?"* (DD0-1 / DD0-3 / SFR-D41's class —
disclosed or refused, never silent); the DD0 rows; the ledger driven down;
then a FRESH blind set for the done-when, and the HOLD arm re-read.

#### DD-0 S4 landing record, part 1 — the exit predicate and the vocabulary (October 10, 2026)

*The user's call at S4's head: let the exit predicate and the vocabulary land as
a first commit before the spine split, so a stalled rewrite cannot hold the
finished half hostage.* Rules `SYSTEMS_REFERENCE.md` §104; pins
`tests/test_dd0_s4_the_reading.py` (102) + 37 golden-corpus rows `dd0-s4-*` (the
corpus 641 → 678); rows `BUG_FIXES.md` DD0-9 / DD0-10 FIXED and the sixteen open
command rows SFR-H2 … SFR-D41 all struck with evidence (D25 and D38 closed by the
relay already, pinned here).

1. **The Reading** (`backend/ai/reading.py`) — one tokenised reading, peeled from
   the outside in (the rhetoric sentence, the please / dash aside, the support
   suffix, the trailing vocative, the precaution, the reason tail, the comma
   aside, the address through an honorific and a modal, `at him`); the typed line
   is immutable and the string the readers see is COMPOSED from its spans — never
   a splice. Applied first in `CommandParser.parse`, each stage on the trace as
   `reading · <rule>`. **The metamorphic ledger 30 → 0** (2,408 cases, every
   family 0, `LEDGER_CAP` 0); five of the six keyless shrugs read (`hit the Austrians`
   stays the live parser's by IQ-9's gate).
2. **The exit predicate** (`backend/commands/exit_predicate.py`) — `place_pre_check`
   before the objection battery (a stationary arm at a province the marshal is
   not in is refused by name, free — SFR-D7's class closed structurally) and
   `disclose` at `execute`'s exit on the trace's two snapshots (a marshal, target
   or arm that changed and is not named in the reply is appended to it — the net
   under the gates that already disclose).
3. **The vocabulary** — the sixteen rows' readings (§104 lists them), the judge's
   two new refusal shapes (grepped first; the seven committed census records
   re-read to identical classes).

**Measured.** The same third blind file re-read keyless as a fresh record
(`docs/audits/unrehearsed/2026_10_10_third_keyless_s4.json`): **as meant 162 → 177
of 300 (59.0 %), asked 32 → 29, shrugs 6 → 1, misread 0, executed-when-refusal-meant 0**
(the as-meant count moves by one or two run to run with the objection dice). The
series byte-identical (`score_run check` stdout identical to the same check on
`38daa024` in a detached worktree, before and after the judge edit; the archive
restored). **The HOLD arm re-read on this tree: 18 of 20 orders as meant (12 at the last reading, October 5) — past the done-when's floor (≥ 17) and at the checklist item's own bar (≥ 18)**; `tools/hold_arm_reread.py` drives the committed blind HOLD script through the driver as `score_run run` does and reads the digest with the ONE reader. The two misses: `Tell Massena to fortfy at Milan in case …` (read right — Massena OBJECTS, which the reader does not count as done) and `Could Soult drill his corps today?` (a question — SFR-H4, SF-RR2's). SFR-H7's third line, `Buy substitutes to fill out Ney's ranks`, read 17 → 18 once the substitutes desk named the man (`We do not hold Swabia, Sire — Ney stands there, …`). `Have Davout head over to Lorraine and dig in there` is read as meant: the exit predicate refused by name — Davout had been mustered into Swabia by Lannes's attack on turn 1.
Not yet: the FRESH fourth-author set (the ≥ 85 % done-when) and the spine split — S4's
next commits.

### DD-1 — THE TABLE AND THE TREATY: the diplomacy deep dive (S5–S6)

*Added October 9, 2026 at the user's word: "add deep dive on diplo to plan."*

- **Why this component.** The pillar reads 8.50 on the final reading and
  still carries **10 open rows, 5 of them P2**, and every diplomacy P1 of the
  quarter had the same shape: **the table said yes and the treaty said no.**
  The peace that never was (a ratified peace re-broken the same end turn);
  a question that signed a treaty; "Accept Risk" on the rebellion modal
  signing a treaty; the Congress dissolved by the war its own summons made
  possible; an accepted alliance letter refused at ratification and logged as
  OUR rejection (SFR-B2); Talleyrand's own counsel executed and then refused
  for an alliance paradox he never named (SFR-D34); a letter for a war France
  does not lead that can be neither accepted nor revised (SFR-B1); a
  counsel-sent proposal going stale in transit (SFR-B5). Beside them, the
  mechanics the player reached for and could not touch: a truce with Austria
  that left Bavaria's war running under four French corps, unannounced
  (SFR-D28); an ally holding a liberated French home province with no verb to
  ask it back (SFR-D42); an allegiance auction announced as biddable with no
  way to bid (SFR-D40).
- **Why it keeps breaking.** **69,863 lines across fifteen modules**
  (`diplomacy.py` 13,468 · `diplomatic_executor.py` 7,723 · `ai_diplomacy.py`
  5,064 · `diplomatic_templates.py` 5,054 · `coalition.py` 4,398 · the seven
  settlement layers 20,000 · `congress.py` 3,242 …), with `_process_dialogue_choice`
  at 2,215 lines and `_ratify_treaty` at 1,179. **"Can this be signed?" is
  answered in at least six places** — the wizard's chip availability, the
  incoming letter's buttons, the settlement preview's scorer, the counsel's
  suggestion, the Congress price table and the ratifier — and three ratify
  seams apply the clauses. The CA9 through-line in its purest form: the
  advisory surface and the executor are separate implementations of one rule
  and only one is maintained. SF-V1/SF-V5 closed it for AI LETTERS by running
  the ratifier's dry run before the letter is sent; the other five surfaces
  still compute their own answer.
- **The instrument.**
  1. **The sign-ability sweep.** On every arm the driver already runs, every
     surface that shows an answerable letter, an enabled chip, a priced
     Congress row or a counsel line is dry-run through the real ratifier AT THE
     MOMENT IT IS SHOWN (the SF-V1 consent dry run, generalised), and a row
     counts each "shown as signable, refused when signed" and each "refused
     without naming the clause the preview missed". The pin is zero on the
     committed arms and on three fresh seeds.
  2. **The treaty state-machine fuzzer.** Random lawful sequences of
     propose / accept / counter / break / truce / vassalize / release /
     declare / separate peace / Congress summons across courts and seeds, a
     thousand steps a seed, asserting the invariants `SYSTEMS_REFERENCE.md`
     §70 / §81 already state: every war pair has an instance and a purpose; a
     client's war is the lord's war and a truce binds every court that follows
     him; no state changes except through `set_diplomatic_state`; cooldowns
     never negative; `war_instances` / `participant_meta` / `diplo_key_meta`
     agree; the world round-trips through save/load at every step. A
     violation prints the sequence that reached it.
  3. **The answer-binding sweep.** With two or three letters queued in every
     order, every typed answer and every button is asserted to bind to the
     court it names (the IQ-7 closed grammar and the FA-N5 identity stamp,
     generalised to a shuffle test).
- **The structural fix that falls out** (and it absorbs CODE-2's `_process_dialogue_choice` and `_ratify_treaty` splits, done with purpose). ONE verdict, `treaty.can_sign(letter,
  world) → Verdict(ok, clause, price, who_must_consent)`, which IS the
  ratifier's own guard sequence lifted out, read by all six surfaces so a chip
  is enabled, a letter is answerable, a counsel line is offered and a Congress
  row is priced only when the ratifier would sign — and a refusal always
  names the clause. A letter that cannot be signed by construction (SFR-B1's
  leader-only war) is shown as mail with its reason and no buttons.
- **The verbs.** The three the depth campaign reached for: `ask <ally> to
  return <province>` (the liberated home soil, priced by the acceptance
  formula or refused with the clause); `bid for <court>` on an open allegiance
  auction (the §12.6 auction's missing player half); and the truce's followers
  announced — a truce that leaves a satellite's war running says so on the
  confirm and the dispatch, and the satellite's war is the lord's (RS-2's rule
  read at the truce). Each through the shared executor, GR5, a corpus row, a
  wizard chip.
- **Done when.** The sign-ability sweep reads 0 on every committed arm and
  three fresh seeds; the fuzzer holds its invariants for 10 seeds × 1,000
  steps; the answer-binding shuffle reads 0 misbinds; the 10 open rows closed
  or re-homed; `BASELINE_SERIES` byte-identical or re-recorded once with the
  verb's reach counted (the AI never bids or asks back in v1 unless GR5 says
  it must); the diplomacy items hold at 8.25 or better on a re-read of the
  CONG / OP / VOLTE arms.

### DD-A — "Can a new player read it?" (= UXR-0 + UXR-1, S1)

- **Weak spot.** The first ten minutes are the tutorial, and on a 3440-px
  monitor its card is 396 px of 13-px type. There is no DPI detection, no
  stretch mode, and the capture harness never shoots a physical ultra-wide
  frame.
- **Instrument.** The IQ-10 harness gains a `physical` mode: a window of the
  target resolution, Interface Scale as the player would have it, and a census
  of every visible text node's rendered cap height in PHYSICAL pixels. A node
  under **16 px** (≈ 11 pt at arm's length on a 27-inch 1440 panel) is a red
  row; under 13 px is a P1.
- **Done when.** Zero red rows on the tutorial, the dispatch, the terminal, the
  top bar and the Generals screen at all four resolutions with the auto-derived
  scale; the user reads the tutorial card on their monitor without leaning in.

### DD-B — "The fresh-eyes campaign" (S13)

- **Weak spot.** 16.5 defect rows per 10 hand-played turns against 0.4 scripted.
  The driver answers every popup by policy and never clicks; the client is
  where the player lives.
- **Instrument.** Three agents who have not read the ledgers, each playing
  20 turns in the real client (Mode C, `SOVEREIGN_PORT=8006`, the user's
  resolution) on a stated road, filing every confusion as a row with a frame.
  The judge is the ONE judge in `tools/_score_probes.py`; the metric is rows
  per 10 turns by severity.
- **Done when.** Under **5 rows per 10 turns** and **0 P1** across the three
  roads, or the rows are filed and homed and the user rules on the remainder.

### DD-C — "Nothing fails silently" (= CODE-3's second half, S7)

- **Weak spot.** 368 handlers swallow without a word; the save failure that
  broke every save for the rest of a campaign reached the server console and
  nobody else.
- **Instrument.** Fault injection on `save_game` / `autosave` / `load_game`
  (disk full, a non-serializable field planted on a marshal, a truncated file)
  once per turn over a 40-turn driver run; a round-trip equality check
  (`to_dict(from_dict(x)) == x`) on every autosave; the client's save/load
  surfaces asserted to SHOW the failure.
- **Done when.** Every injected fault reaches the player as a sentence on the
  rail or the save dialog and the log at WARNING with the site; the ratchet pin
  holds the silent-handler count at zero in `save_manager.py`,
  `world_state.py`'s serialization and `main.py`'s save routes.

## 4. What is deliberately NOT in this plan

- **No balance or mechanics change.** A code-health slice that moves
  `BASELINE_SERIES` is a bug in the slice.
- **No new UI surfaces.** UXR fixes what exists; the one new element is the
  first-run sizing card.
- **No re-score** until the Score Finish residue resumes (S10); a reading
  during the refactor would measure the instrument's noise.
- **The lever convention stays for NEW slices** (a lever lands with its
  attribution and is retired the session after); CODE-1 retires the backlog,
  it does not ban the practice.

## 5. The user's calls (each has a default; silence takes it)

1. **Order.** Code health first, as asked; UXR-0/1 ahead of it because it is
   one session and the user's own report. *Default: the table above.* ✅ *Taken
   October 9, 2026 ("go"), with the adjustability review's seven decisions at
   their defaults (`docs/audits/UXR_ADJUSTABILITY_REVIEW_2026_10_09.md` §7): S1
   grows to S1a (landed) + S1b (the Settings additions, next).*
2. **The Score Finish residue** pauses until S14. *Default: pause.*
3. **Interface Scale cap** 2.0 → 3.0 and an auto-derived default. *Default: yes.*
4. **Lever retirement scope.** Everything landed before October 1, 2026; the
   October levers keep one more session of attribution. *Default: yes.*
5. **DD-B's players** are agents in the client; the user plays the fourth
   campaign at their own pace. *Default: yes.*
