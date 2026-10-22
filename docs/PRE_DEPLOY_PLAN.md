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

**Every error is fixed before the deploy** (the user's delegation, October 14,
2026: "assure the plan has all errors fixed in coming sessions and any similar
errors they find while working"):
- **Every open row has a session.** At that date the ledgers held 143 open
  defect rows and no open design row; each names its session below — the DD-B
  rows S13b, the Score Finish residue and SFR-B3 S14, the UXR-4 marks S15's
  head. A row filed later is homed to a session in this table the day it is
  filed, never after the deploy.
- **The sibling sweep** (from S13b on): every fix ends with a search for its
  class — the same mechanism on the other courts, dialogues, popups and roads,
  and the AI's side of the same executor. Each sibling found is filed as a
  found row (tagged) and fixed in the same slice with its own test; one too
  large for the slice heads the next part. A slice's commit names its sweep
  (what was searched, what was found).
- **The re-measure** (S14e, after the new features): if DD-B's done-when is
  not met, its new rows become S14f before S15.
- **The deploy gate** (S15): the release build waits for 0 OPEN defect rows.
- **What comes in before the deploy** (the user, October 14, 2026: "add events
  to plan as well … i agree with rest … make sure everything reflects future
  plans"): VP-1 "The Emperor's Designs" (S14b), the events system with its
  historical moments (S14c), the table lesson — the onboarding pass (S14d), DW-2
  (DDB-X5, S13b part 1), the naval rail alerts (DDB-X6, S13b part 4) and code
  signing (S15). Everything else after the deploy has its home in
  `docs/ROADMAP.md` §"Where the future work lives".

| # | Row | What lands | Size | Why here |
|---|-----|-----------|------|----------|
| ~~S1~~ **S1a ✅ LANDED October 9, 2026** | **UXR-0 + UXR-1** | The readability instrument (physical-pixel text census at 1920×1080 / 2560×1440 / 3440×1440 / **5120×1440** / 3840×2160) and the fix with the widest reach: Interface Scale auto-derived from the screen at first boot, the cap 2.0 → 3.0, a theme text floor, the first-run "can you read this?" card. **Landing record `UX_UI_REVIEW_PLAN.md` §UXR-1 landing record: named set RED 255 → 0, P1 750 → 0; the user's eyes = UXR-4.** | 1.0 | The user's report; first contact is the tutorial and it cannot be read. Smallest change, largest reach. |
| ~~S1b~~ **✅ LANDED October 9, 2026** | **the Settings additions** (the adjustability review's decisions 4 + 5) | Window mode + size picker; the terminal's default footprint as a viewport fraction; Ctrl+= / − / 0; Reset layout; a CONTROLS reference; the *Body text: Garamond · Plain* option; the sizing card from Settings — and the floor's residue from the whole-client census (the log tiers, six 15s). **Landing record `UX_UI_REVIEW_PLAN.md` §S1b landing record; named set still RED 0 / P1 0.** | 0.5 | Cheap, same seams; the review's "is anything missing" answer |
| S2 step 0 ✅ **LANDED October 9, 2026** | **the hook pays its way** | The pre-commit hook runs the full suite under pytest-xdist (`-n 8 --dist loadgroup`): serial 26:13 → **5:12** measured, the gate whole; two order-dependent pins fixed (an unseeded 30-draw dice test; an endpoint pin reading whatever world the previous module left in `backend.main`); the stall under xdist traced to child processes inheriting the worker's execnet stdin (now DEVNULL in a worker). Record: `CLAUDE.md` Workflow + Commands. | 0.3 | The user's October 9 ask ("it takes sooo long"); every S2 commit after it pays the new price. |
| ~~S2~~ ✅ **LANDED October 9, 2026** | **CODE-4** (record `CODE_HEALTH_PLAN.md` §CODE-4) + **CODE-1 batch 1** (record §CODE-1; 20 of the batch's 46 levers retired — the 26 that landed in October keep their session; `tools/retire_lever.py` + the ratchet pin) | The docs diet (CLAUDE.md → rules + a one-screen state; STATUS/BUG_FIXES history to archives, the census tool reading both) + the lever-retirement tool and its first 100 levers | 1.0 | Pays back every session after it. The tool is proven on small modules before the monsters. |
| ~~S3~~ ~~S4~~ ✅ **S3 LANDED October 10, 2026** (the instrument — §3.0 landing record: the parse trace + the typed `why`, the metamorphic corpus 2,100 cases / 161 in the ledger, the third blind set 137 / 152 of 300; **S3b the same day: the findings fixed — the ledger 161 → 30, the blind set 162 / 170 of 300, 0 executed-other-than-meant**; S3's head **CODE-1 batch 2** ✅ **LANDED October 10, 2026** — 83 of the game_logic batch's 138 levers retired, 56 October ones kept; levers 645 → 562; record `CODE_HEALTH_PLAN.md` §CODE-1) → **S4 IN PROGRESS: part 1 ✅ LANDED October 10, 2026** (the Reading + the exit predicate + the vocabulary — §3.0 "S4 landing record, part 1": the ledger 30 → 0, the third set re-read 162 → 177, the sixteen command rows struck); the HOLD arm re-read 12 → 18 of 20; **part 2 ✅ the measurement, the same day: the FRESH fourth-author set reads keyless 119 of 300 (39.7 %) / keyed 134 — the ≥ 85 % done-when NOT met, the worklist DD0-11 … DD0-17 filed; part 3 ✅ the same day: both spines split byte-identical, the slot reader, DD0-11 … DD0-17 fixed, the fourth set re-read 119 → 145 / 141 (two runs, the dice); the FIFTH fresh author reads 125 of 300 as meant (41.7 %) / 241 read right by hand (80.3 %) — the done-when NOT met a second time; **RULED October 11, 2026: the instrument is RE-BASED — the done-when reads READ RIGHT BY HAND ≥ 85 % keyless + 0 executed-other-than-meant on a FRESH set, `as_meant` beside (§3.0 the ruling line); part 4 ✅ LANDED October 11, 2026 — the instrument (`unrehearsed_census.py --by-hand`, a hand file beside each record), DD0-18 and DD0-19 fixed (the fifth and sixth sets re-read 289 and 290 of 300 by hand, 0 executions), and the SEVENTH fresh author reads 255 of 300 by hand (85.0 %) with 0 executed-other-than-meant — MET at the floor; DD0-20 (its register) OPEN, owned by S5's head. S4 STRUCK.** | **DD-0 THE COMMAND ROAD** | The one deep dive the user asked for (§3.0): the parse trace on every response, the metamorphic corpus, a third blind author set, one `Reading` object through the pipeline (absorbs CODE-2's `_parse_with_mock_chain` + `_execute_one` splits), the "did I do what was named" predicate | 2.0 | The game's premise; the largest open pillar; where every review round found a P1 inside the fix. |
| S5–S6 (▶ IN PROGRESS: **the head, CODE-1 batch 3, ✅ LANDED October 11, 2026** — 66 of the four files' 78 levers retired, 12 October ones kept; levers 562 → 496; record `CODE_HEALTH_PLAN.md` §CODE-1 BATCH 3, which also files batch 5 for the 116 levers in the game_logic modules over 3,000 lines the plan had left unnamed; **DD0-20 ✅ LANDED the same day** — the seventh set re-read 255 → 294 of 300 by hand keyless (98.0 %), keyed 281 → 296, 0 executed-other-than-meant (§3.0 "DD-0 S5 landing record"); **DD-1 S6 THE INSTRUMENT ✅ LANDED October 11, 2026** — the sign-ability sweep (A = 11, B = 2), the treaty fuzzer (81 distinct violations in 7 classes over 10 × 1,000) and the answer-binding shuffle (4 misbinds, one class) built and read, DD1-1 … DD1-12 filed (§3.1 "DD-1 S6 landing record"); **Step 2 the structural fix ▶ NEXT**) | **DD-1 THE TABLE AND THE TREATY** | The diplomacy deep dive (§3.1): one `can_sign` verdict read by every surface that shows a letter, a chip, a price or a counsel line AND by the ratifier; the treaty state-machine fuzzer over the §70/§81 invariants; the three unbuilt verbs the depth campaign reached for | 1.5 | The second-largest open pillar by weight (10 rows, 5 P2); the quarter's P1s were all "the table said yes and the treaty said no". |
| ~~S7~~ (✅ **STRUCK October 11, 2026** — **Slice A LANDED** the same day: one exit for a pair, DD1-5 … DD1-11 fixed, the fuzzer **81 → 0** over 10 × 1,000 + the smoke seed, the shuffle **4 → 0** over 312 rows (§3.1 "DD-1 S7 landing record, Slice A"; rules §107); **Slice B LANDED** after the review pause: `treaty.can_sign` the ONE verdict read by every surface AND the ratifier, DD1-1 … DD1-4 + DD1-12 + SFR-B1 / B2 / B5 / D34 fixed, **the sweep 11 / 2 → 0 / 0** on every committed arm and the three seeds, the diplomacy pillar re-read 8.5 (§3.1 "DD-1 S7 landing record, Slice B"; rules `SYSTEMS_REFERENCE.md` §108). **DD-1 Step 3 the verbs = S8's head**; CODE-3 + DD-C = S7b) | **DD-1 Step 2 THE STRUCTURAL FIX** | Slice A: `cleanup_war_end` the one exit (every road restamps the instance), the client rule on ENTRY, the re-entry's stamps, the purpose on re-war, the round trip's three producers, the declaration's words, the display map's nouns. Slice B: `treaty.can_sign(world, letter) → Verdict` read by every surface AND the ratifier; DD1-1 … DD1-4 + DD1-12 + SFR-B1 / B2 / B5 / D34; the sweep 11 / 2 → 0 / 0 | 1.0 | DD-1 was sized 1.5 sessions; Step 2 takes this slot and the rows below move one down. |
| ~~S7b~~ ✅ **LANDED October 12, 2026** (three commits: `43dd8c59` CODE-1 batch 5 at its head — levers 429 → 358, `CODE_HEALTH_PLAN.md` §CODE-1 BATCH 5; `d495b2b2` `backend/errors.py` + DD-C — the save path's typed `SaveError`, every fault a sentence and a WARNING with its site, 40 of 40 injected faults reached the player over the commanded forty-turn campaign, §3 "DD-C landing record"; the third, the conversion — **silent handlers 367 → 6**, the residue named, 0 report sites in five played campaigns, `CODE_HEALTH_PLAN.md` §CODE-3 parts 1–2; rules `SYSTEMS_REFERENCE.md` §110. **CODE-3 DONE; DD-C DONE**) | **CODE-3** + **DD-C** | One `errors.swallow(ctx)` helper through all 368 silent handlers, narrowed where the type is obvious, a ratchet pin; **the save path raises and the player is told**; save/load fault injection over a 40-turn run | 1.0 | The silent class is the one that produced an invisible P1. |
| ~~S8~~ ✅ **TAKEN by DD-1 Step 3 THE VERBS — LANDED October 12, 2026** (§3.1 "DD-1 S8 landing record": `ask <ally> to return <province>`, `bid for <court>`, the truce's followers announced — SFR-D42 / D40 / D28 FIXED, rules `SYSTEMS_REFERENCE.md` §109, pins `tests/test_dd1_s8_the_verbs.py`; the head **CODE-1 batch 4**, levers 496 → 429, `CODE_HEALTH_PLAN.md` §CODE-1 BATCH 4). **CODE-2a moves one down; S7b (CODE-3 + DD-C) LANDED October 12, 2026.** ~~S8b~~ ✅ **CODE-2a LANDED October 12, 2026** (`CODE_HEALTH_PLAN.md` §CODE-2 "CODE-2a landing record": `_execute_attack` a driver of twenty `_attack_*` stages behind one `AttackContext`, `BASELINE_SERIES` + M1–M7 byte-identical with no re-record, functions over 500 lines 34 → 33, pins `tests/test_code2a_the_attack_is_staged.py`; the head **CODE-1 batch 6**, levers 358 → 231, §CODE-1 BATCH 6). **S9 UXR-2 is NEXT.** | **CODE-2a** | `_execute_attack` split into named stages behind one context object; pure refactor | 1.0 | The single largest function; every combat fix since July touched it. |
| ~~S9~~ ✅ **LANDED October 12, 2026** (`UX_UI_REVIEW_PLAN.md` §UXR-2 landing record. Six commits: A `77172273` the routed families (UXR-X5/X6), B `5a62690e` the named sizes + scroll, C `af7f1e79` the grips + the refit road, the review fixes `95b3a1b5`, D `7ce88863` the anchors, E the landing re-shoot. The law holds for every CanvasLayer, the allowlist is empty, and six screens plus the war HUD resize and remember (driven). Raw font-size overrides 72 → 18; the whole client reads 0 RED / 0 P1 at five resolutions. Rules `SYSTEMS_REFERENCE.md` §111; rows `BUG_FIXES.md` §UXR-2 UXR-X5 … X20. **S9b is NEXT.**) | **UXR-2** | The layout law: every panel anchors to a viewport fraction or clamps; a grip on the five big screens; the tutorial card resizable and theme-sized; the 268 font-size overrides reduced to named theme sizes | 1.0 | "Only some boxes are adjustable." |
| ~~S9b~~ ✅ **LANDED October 13, 2026** (`UX_UI_REVIEW_PLAN.md` §UXR-2's S9b landing record. Four commits: A `1f91f761` Text size, B `a472497f` HUD width + `[− ⌂ +]`, C `786839b9` the map's furniture, D High contrast. Text size at 150 % reads 0 RED with every text node scaled; Centred holds every HUD rect inside a 2560-px band at 5120×1440; the map's `map_small` 34 → 0; contrast under the floor 20 → 0. Rules `SYSTEMS_REFERENCE.md` §112; rows `BUG_FIXES.md` §UXR-2's extras UXR-X21 … X28. **S10 is NEXT.**) | **UXR-2's adjustability extras** (re-homed from S9 by the user's ruling, October 12, 2026 — `UX_UI_REVIEW_PLAN.md` §UXR-2 landing record) | Four rows filed against S9 that the layout law does not need, each with its own done-when and test: **UXR-D1**, a *Text size* slider for the theme's named sizes alone (needs part 4's diet first); **UXR-D2**, *High contrast*; **UXR-D3**, *HUD width: Full · Centred* plus a ⌂ Fit Europe button; **UXR-X4**, the map's own labels follow the Interface Scale (and the map tooltip's 11-px `draw_string` text, which no census sees). The rows are in `DESIGN_REFINEMENT.md` §UXR and `BUG_FIXES.md` §UXR-0 / UXR-1. | 1.0 | They land before UXR-3 so the review sees them. UXR-D4 (the Side Desk) keeps its own gate. |
| ~~S10~~ ✅ **LANDED October 13, 2026** (`CODE_HEALTH_PLAN.md` §CODE-2b landing records, slices 1–3. Three commits: `b135a7d0` `execute_command` = fifteen `_command_*` stages; `9e819cc4` `format_event_oneliner` = twelve `_oneliner_*` stages; then `_execute_strategic_command` = eleven `_strategic_*` stages. Functions over 500 lines 33 → 30; `score_run check` identical at every cut. **S10b is NEXT.**) | **CODE-2b** | The monster functions the two deep dives did not absorb: `execute_command`, `format_event_oneliner`, `_execute_strategic_command` (one each, as S8) | 1.0 each | DD-0 took `_parse_with_mock_chain` + `_execute_one` (38 and 11 lines). DD-1 was to take `_process_dialogue_choice` + `_ratify_treaty` and did not split them: they are S10b's. |
| ~~S10b~~ ✅ **LANDED October 13, 2026** (`CODE_HEALTH_PLAN.md` §CODE-2c landing records, slices 1–2. Two commits: `80b05b2f` `_ratify_treaty` = nine `_ratify_*` stages; then `_process_dialogue_choice` = nine `_choice_*` stages, cut by the tool's new elif mode. Functions over 500 lines 30 → 28; `score_run check` identical at both cuts. **CODE-2 is DONE. S11 is NEXT.**) | **CODE-2c** | The two DD-1 left whole (measured closing S10; the user's ruling, October 13, 2026): `WorldState._ratify_treaty` (1,024 lines, body mode) then `DiplomaticExecutor._process_dialogue_choice` (2,210 lines, ONE `elif` chain: the tool needs an elif-chain mode). One commit each, run straight through: the user's October 13 ruling made every decision in advance, so there is no review pause. Done when neither is over 500 and the cap reads 28; CODE-2's done-when is then met (`CODE_HEALTH_PLAN.md` §CODE-2c) | 1.0 | Net: DD-1's sweep, fuzzer and shuffle, `score_run check`, the series, byte-for-byte. |
| ~~S11~~ ✅ **LANDED October 13, 2026** (`UX_UI_REVIEW_PLAN.md` §UXR-3 landing record; the review `docs/audits/UXR3_REVIEW_2026_10_13.md`. Three commits and the close: `603d983f` the checklist frozen (`docs/UX_CHECKLIST_V1.json`: R1–R8, and 145 surfaces in the ten groups), `db565b1a` the evidence (five resolutions, the action probe, the consistency census, the fit report), `1cca0d31` the reading: three blind readers, two of three, **787 ✓ / 373 ✗** on 1,160 marks, the worst five named, 84 rows in `BUG_FIXES.md` §UXR-3 — the review. Rules `SYSTEMS_REFERENCE.md` §113. **S12 is NEXT, re-sized to two sessions.**) | **UXR-3** | The look-and-feel review: every surface scored on the 8-item UX checklist at three resolutions, by three blind readers, fixes filed | 1.0 | The "full look feel ux review." Needs UXR-0's frames. |
| ~~S12 (two parts)~~ ✅ **LANDED October 14, 2026; S12 STRUCK** (`UX_UI_REVIEW_PLAN.md` §UXR-3 part 1 and part 2 landing records; the closing re-read `docs/audits/UXR3_REREAD2_2026_10_14.md`: **787 → 977 → 1,149 of 1,160 ✓**; seven items at 145 of 145, R2 134; **no surface under 6** (82 → 9 → 0); 134 surfaces at 8 of 8; 74 of the 78 rows FIXED with their re-reads, 7 re-homed to UXR-4 (S15) with frames, reasons and decided fixes; UXR-X28 to S12b's head. Part 1: six commits `de86a83c` … `46f668ef` and the close; part 2: eight commits `56fe00b0` … `d34cbe91` and the close. The top five groups read 104 of their 115 surfaces at 8 of 8 — the eleven short are R2 marks the user reads at UXR-4. **S12b is NEXT.**) | **UXR-3 fixes** | The review's own rows (`BUG_FIXES.md` §UXR-3 — the review: 83 of its 84; the end screen's copy row is S14's), worst surfaces first. Part 1: the three popups never shot, then the classes: R3 by token, R5/R6's inert controls, R4 by file. Part 2: R6's driven proofs (a war-room mode of the action probe against a sandboxed backend), the never-pressed controls, the per-board hierarchy, the rows found while reading, and the closing re-read. Done when the top five groups read 8 of 8, no surface reads under 6, and every row is fixed with its re-read or re-homed with a reason (`UX_UI_REVIEW_PLAN.md` §UXR-3) | 2.0 | Re-sized by the S11 close (October 13, 2026): 373 ✗ in 83 rows, three surfaces never shot, and R6's hand-offs need a driven proof the harness does not have yet. |
| ~~S12b~~ ✅ **LANDED October 14, 2026; S12b STRUCK** (four commits on master, `4b863aad` … `2a14b290`, and the close; `DESIGN_REFINEMENT.md` UXR-D4's landing record, `BUG_FIXES.md` UXR-X28 FIXED; rules `SYSTEMS_REFERENCE.md` §114; records `docs/audits/uxr_d4/`. **UXR-X28:** the map's furniture 71 overlaps → 0 at five resolutions, dock closed and open. **UXR-D4:** the six screens pin non-modal in the right third; the HUD and the map's view give the dock its third; the driven proof — a pinned ledger survives a command, a popup and an end turn beside a live map — passes against a sandboxed backend; the census reads 0 RED / 0 P1, 0 cut lines, 0 map overlaps. **S13 is NEXT.**) | **UXR-D4 "The Side Desk"** | **Its head: UXR-X28** (moved from S12 at its close, October 14, 2026 — the map's furniture at the whole-map view, measured with the dock open and closed; the harness first records the map tier's rects; `BUG_FIXES.md` §UXR-2's extras). Then: a layer-50 screen pinned NON-modal in the right third beside a live map. Ruled October 13, 2026 under the user's delegation; the contract is `DESIGN_REFINEMENT.md` UXR-D4. Done when a pinned ledger survives a command, a popup and an end turn; test `tests/test_uxr_d4_the_side_desk.py` | 1.0 | The one feature a 32:9 player names first, and the user plays at 5120×1440; it lands before DD-B so the campaigns use it. |
| ~~S13~~ ✅ **LANDED October 14, 2026; S13 STRUCK — done-when NOT met, every row filed and homed** (`docs/audits/DD_B_FRESH_EYES_2026_10_14.md`; records `docs/audits/dd_b/`; rules `SYSTEMS_REFERENCE.md` §115; four commits on master: `a4fd195b` the instrument, `2ca0fed5` / `fb6d751e` / the close the three roads. Three players who had read nothing played 20 turns each in the client at 5120×1440 — conquest, diplomacy-first, the sea, all to Turn 21, 1,075 actions, 0 SCRIPT ERRORs; the ONE judge reads 0 P1 (it learned two reply shapes, 0 committed census orders moved). 96 player rows → **69 causes: 11.5 rows per 10 turns, 3 P1** (per road 14.0 / 16.0 / 12.5). 62 rows to **S13b** (`BUG_FIXES.md` §DD-B), 9 design questions to `DESIGN_REFINEMENT.md` §DD-B for the user at S15. **S13b is NEXT.**) | **DD-B** | Three fresh-eyes hand-played campaigns IN THE CLIENT at the user's resolution, three roads (conquest / diplomacy-first / the sea); defects per 10 turns as the metric | 1.5 | The 16.5 is the honest number; nothing else measures a new player. |
| ~~S13b (four parts)~~ ✅ **COMPLETE October 19, 2026** | **DD-B fixes and the rulings' builds** | `BUG_FIXES.md` §DD-B: DDB-1 … DDB-62 (P1s first), the rulings' builds DDB-R1 … R7, the siblings DDB-X1 … X3 and the two rows brought forward DDB-X5 (DW-2) and DDB-X6 (the naval rail alerts) — the nine design rows ruled October 14, 2026 under the user's delegation (`docs/audits/DD_B_RULINGS_2026_10_14.md`). ~~**Part 1**~~ ✅ **LANDED October 14, 2026** (`08c54539` the P1s, `6f360d03` the table; rules `SYSTEMS_REFERENCE.md` §116): the P1s with D8 / D9 built (DDB-1; DDB-2 with "France is asked"; DDB-3 with "a truce pauses the shared war"), the table's P2s (DDB-4 … 12) and DDB-X5 FIXED; its sweep found DDB-X7 … X11 (X7, X8, X10 FIXED; X9, X11 head part 2); the series byte-identical on every arm. ~~**Part 2**~~ ✅ **LANDED October 15, 2026** (`8f3f1141` the head, `33643c45` the table, `cd8f3210` the field; rules `SYSTEMS_REFERENCE.md` §117): DDB-X9, DDB-X11, DDB-13 … 20 and DDB-22 … 44 FIXED; its sweeps found DDB-X12 … X22 (all FIXED but X17, which heads part 3); the series byte-identical on all eighteen arms. ~~**Part 3**~~ ✅ **LANDED October 15, 2026** (`eba57ba4` the head, `ab6314a9` the orders, `89db8acc` the garrison and the retreat; rules `SYSTEMS_REFERENCE.md` §118): DDB-X17 FIXED; the rulings' builds DDB-R1 … R7 BUILT (ask first; the muster gate widened; no auto-end; the arm refused; the peace's sink; the capitulation at 4:1; the withdrawal named); DDB-X1 … X3 FIXED; its sweeps found DDB-X23 … X25 (all FIXED); `BASELINE_SERIES` re-pinned once, by DDB-X3 (the AI's retreat onto an ally's soil), every other arm byte-identical. ~~**Part 4**~~ ✅ **LANDED October 19, 2026** (`94ce4c44` the code, then the close; rules `SYSTEMS_REFERENCE.md` §132): DDB-21 (a corps on soil its court holds by title is home; ONE embark rule), the voice (DDB-45 … 53), the client (DDB-54 … 57, driven and walked on `SOVEREIGN_PORT=8007`, `docs/audits/ddb_s13b_client/`) and the sea (DDB-58 … 62, DDB-X6) FIXED; its sweeps found DDB-X26 … X32 (all FIXED); the series byte-identical with every part-4 seam up and down (`tools/_ddb_s13b4_series_arms_final.json`). **S13b COMPLETE — 0 rows homed to S13b OPEN; S14 is NEXT.** **The sibling sweep holds in every part** (the rule above the table). Done when every row is FIXED with its test (`tests/test_ddb_s13b_<slice>.py::TestDDB<n>`, `tests/test_ddb_s13b_the_rulings.py::TestDDBR<n>` / `TestDDBX<n>`); DD-B's re-measure is S14e | 4.0 | Added by the S13 close and re-sized by the rulings (October 14, 2026): 62 rows + 7 builds + 5 siblings and brought-forward rows, P1s first. The re-measure moved to S14e so it reads the new features too. |
| ~~S13c (five parts)~~ ✅ **COMPLETE October 19, 2026** — **CC-0 + CC-1 ✅ LANDED October 15, 2026; CC-2 ✅ LANDED October 15, 2026; part 2 (CC-3) ✅ LANDED October 17, 2026; part 3 (CC-5) ✅ LANDED October 18, 2026; part 4 (CC-4) ✅ LANDED October 19, 2026** | **CC "Click & Command"** (brought ahead of S13b part 4 by the user, October 15, 2026: "lets focus on comamnds"; the four features they picked — names clicked into the line, "March here", select-then-click orders, smarter typed chaining — plus the creative extras; the plan `~/.claude/plans/sorted-yawning-clover.md`) | **Every click order travels the same `/command` road as typed text, the rules stay in the backend, and a half-typed line is never destroyed.** ~~**Part 0**~~ ✅ CC-0 "The line is the player's" + CC-1 "Click names into the line" — type-through, offers held beside the line, every sender retiring the end-turn latch, the panel chip's wire guard, the front piece wins; a map click while the caret waits for a name writes it, Shift-click always, the suggestion row clickable, the map lights the province the draft names (`BUG_FIXES.md` §CC: CC-X1 … X5 FIXED, and CC-X10 — the next order's keys dropped after Enter, found by the row's own capture; pins `tests/test_cc_click_and_command.py`, driven by `tools/cc_client_harness.gd`). ~~**Part 1 CC-2 "March here"**~~ ✅ (landing record `SYSTEMS_REFERENCE.md` §121; the boot drift census 1,000 / 1,000 and 72 / 72) — `strategic.march_quote()` extracted from the question desk's reach answer (one builder; AP by `strategic_order_ap(order_type="MOVE_TO")`), `GET /march_quotes`, the panel's March here / Support / March & attack rows, drift-pinned against `/command`, and CC-X8. ~~**Part 2 CC-3 "Select, click, Enter"**~~ ✅ (landing record `SYSTEMS_REFERENCE.md` §128; pins `tests/test_cc3_select_click_enter.py`) — select a piece (the ring, the strip), the ETA tint from one pathfinding pass per rung of the road law (`GET /march_reach`, pinned equal to `march_road` and `march_quote` on every province), the ghost road, the confirm card on the exact quote (`GET /march_quotes?marshal=…`; modal, Enter / Esc its own, placed clear of the road it confirms), drag-to-order with an 8 px threshold, the Esc ladder and the clearing rules; CC-X11 … X13 FIXED (an enemy known by his fog chip is the attack's target; a line filled by code lets the selection go; a restored terminal stands on its newest line); the Mode C walk on `SOVEREIGN_PORT=8007` (`docs/audits/cc3_client/`). ~~**Part 3 CC-5 "The war table"**~~ ✅ (landing record `SYSTEMS_REFERENCE.md` §129; pins `tests/test_cc5_the_war_table.py`) — every standing order an arrow along its remaining road (the player-only `tactical_state.order_road`, derived — our corps only, pinned) with its ETA badge and a Cancel / Change card (one cancel road through `/cancel_order`), `.` the next idle marshal, Ctrl-click groups on ONE card summed against the pool and sent one line at a time down the typed road, stopping at the first question or refusal (the named-list line is CQ-8's relay by ruling — the landing record says why); CC-X14 … X16 FIXED (the literal march's detour in the quote and the reach, the Orders tab's cancel on the one road, the stale road head); the Mode C walk (`docs/audits/cc5_client/`). ~~**Part 4 CC-4 "Chained orders"**~~ ✅ (landing record `SYSTEMS_REFERENCE.md` §130; pins `tests/test_cc4_chained_orders.py`; commits `d6a0cd8d` the head, then the builds) — CC-X6, CC-X7, CC-X9 and CC-X17 at its head; `arrival_verb` (march … then fortify / hold / drill / defend, done free on arrival; a `move to` with such a tail is the march); the contradiction asked first, nothing spent, with the order that gives both offered beside the line where it is coherent (the user's D6); the standing contingency ("if Mack advances, fall back to Lorraine" / "… attack") on its own field, watching only what the holder sees, fired free at the turn's end; CF-5 and the siblings CC-X18 … X24 FIXED (a conditional line is never an interrupt's answer; a cautious holder's works rise at the turn's end); the Mode C walk on `SOVEREIGN_PORT=8007` (`docs/audits/cc4_client/`). Done when every part's pins pass through the hook, the driven attribution arms are byte-identical (or each movement attributed and named), and a Mode C walk on `SOVEREIGN_PORT=8007` shows each gesture | 5 parts (CC-0 + CC-1 done) | The user asked for it by name; CC-0's fixes (the turn ending mid-draft, the overwritten draft) were live defects in the command road every other row's player uses. **S13c COMPLETE (row CC complete); next: S13b part 4 (✅ LANDED October 19, 2026), then S14.** |
| ~~S13d (one part)~~ ✅ **LANDED October 15, 2026; S13d STRUCK** (`BUG_FIXES.md` §PC: PC-F1, F3, F5, F6 FIXED with the sweeps' PC-X1 … X4; rules `SYSTEMS_REFERENCE.md` §120; pins `tests/test_pc_peace_conundrum_fixes.py`; the series attributed — `BASELINE_SERIES` byte-identical, the commanded CMD-H campaign re-timed from turn 11 by PC-F5 alone; the report's B–E stay the user's) | **PC — the peace conundrum's fixes** (`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` §4 A; the report's B–E expansions are the user's to rule) | `BUG_FIXES.md` §PC: PC-F1 (name the ally), PC-F3 (the war panel shows the score the peace math reads), PC-F5 (the AI reads this turn's score), PC-F6 (the decisive credit and the holding garrison), each with its sibling sweep. Proposed October 15, 2026 as its own session; if not started by S14, it heads S14 | 1 | The live campaign that asked "why won't Austria make peace" found two scoring defects and two legibility gaps on the road every war ends by. |
| S13e (**four parts**, one session each — ✅ COMPLETE October 17, 2026; the user's calls October 16, 2026: "assure these items are next up in work", then "make all decisions and make this work next before rest of work" — ahead of S13c part 2, which follows it with S13c parts 3–4 and S13b part 4) — **part 1 ✅ LANDED October 16, 2026** (`SYSTEMS_REFERENCE.md` §122), **part 2 ✅ LANDED October 16, 2026** (`SYSTEMS_REFERENCE.md` §123), **part 3 ✅ LANDED October 16, 2026** (`SYSTEMS_REFERENCE.md` §124), **part 4 ✅ LANDED October 17, 2026** (`SYSTEMS_REFERENCE.md` §127; pins `tests/test_pc_rulings.py`; **S13e is COMPLETE** — PC-R7 (ii) heads S14; **S13c part 2 (CC-3) is NEXT**) | **PC parts 2–5 — the peace research's defects and its rulings, DECIDED** (`docs/audits/PEACE_CONUNDRUM_2026_10_15.md` Parts II–V; **§46 the gate record, October 16, 2026, under the user's delegation: B folded into C, C, D, I, E, H, G and J decided, F unchanged, K — Talleyrand's counsel alive — added** ("we want to make sure tallyrand recs work better … arent just set in stone and boring"); builds `BUG_FIXES.md` §PC **PC-R1 … R8**) | ~~**Part 1 — the one verdict and the counsel:**~~ ✅ LANDED October 16, 2026 — PC-R1 (i)–(iv) (the HARD_STOP a priced WARNING or a carry-in, owner `COALITION_SPEC.md` §6a.1; `carried_in_allies` read by the table's plan and the bilateral ratifier; `court_own_readiness` + §6a's loyalty term; `separate_peace_words` on every surface; F53's `to`) and **PC-R8** (`counsel.py`: a reading over the roads that carry, composed from the authored pools with a per-court memory, his own mind and the override tally, one builder for the wizard, the card and the table, and K item 6 — the road he names opens with the draft he priced); the P1s **PC-F9, F49, F50, F51**; the client's lies F48, F34, F67, F78, F65, F73, F76, F37; the counsel's rows F12, F35, F36, F40, F43, F10, F25, F88; siblings PC-X5 … X7. The sweep A = 0 / B = 0, the fuzzer 0, the series byte-identical on eight arms (`tools/_pc_s13e_series_arms_final.json`). The Part IV M1 / M3 / M5 frames re-shot (`docs/audits/peace_client/`). ~~**Part 2 — the truce and the dictated peace:**~~ ✅ LANDED October 16, 2026 — PC-R2 (D: the ledger and the war's age kept through the truce and the collapse, exhaustion held, the two signed exits and the collapse with the hope predicate read once by the expiry and the AI's ask, the one wording F44), PC-R3 (I: the player's clause types by tier priced by the player's scorers, the offer history's ratchet, the indemnity to the war with sureties held until paid, the refusal's price on the Charges / the petitions / the panel, the regime arm; the ulm pin), PC-R1 (v) (the ally's bill from the desire profile, F81's standing, the two Pressburgs' line, F70); F59, F69, F82, F87; the table's authoring holes F54, F56, F52, F62; F13, F22; siblings PC-X8 … X12. The series byte-identical on seven arms (`tools/_pc_s13e2_series_arms_final.json`), the sweep A = 0 / B = 0, the fuzzer 0; the M7 / M8 frames re-shot (`SYSTEMS_REFERENCE.md` §123). ~~**Part 3 — the scores and the clock:**~~ ✅ LANDED October 16, 2026 — PC-R4 (E: each court on its OWN pair for the base and the tier, the 0.10 stake floor — covered, not consulted, never a veto; a burdened court always consulted; the payee credited in full; the league's letter dry-run as the player's, written by contribution on the writer's own pair — F63), PC-R5 (H: +8 kept; occupation +1 a province, subsidy ±2, finance +2, named on the war popup and the HUD; the gate reads the live rate; F42, F31, F20), PC-R6 (G: caps kept, decay then cap, the shield down with the capital held and a ticking that falls, the fill shown, the trend drawn — F84; every ±100 literal pinned; F38, F39); F55, F71, F60, F61, F27, F26; the coalition's shape F58, F66, F77, F79, F80 (at its root); the sea F64, F68; siblings PC-X13 … X20. The series byte-identical on fourteen arms (`tools/_pc_s13e3_series_arms_final.json`), the sweep A = 0 / B = 0, the fuzzer 0; the M1 / M2 frames re-shot (`SYSTEMS_REFERENCE.md` §124). ~~**Part 4 — the stake, the memory, the instruments:**~~ ✅ LANDED October 17, 2026 — PC-R7 (i) (J: the war titled by its stake on every surface — `war_title.py`, one builder; the table titles the same object); F41, F72; the AI's memory F57, F74, F75, F83 and F81's second road; F28, F29, F30, F33; F11, F14, F45; the instruments F85 (the fixtures driven / producible), F86; siblings PC-X21 … X27. **PC-R7 (ii) — the compensation clause, composed terms, the ally's bond — sized at the part's head and HEADS S14** (two sessions by §40 J; the row stays OPEN). F's reactivity re-read (the report's §47): on the Vienna-held board all ten levers move at least one court's answer (three only where G's decay or D's truce made them live). The series byte-identical on eleven arms (`tools/_pc_s13e4_series_arms_final.json`), the sweep A = 0 / B = 0, the fuzzer 0; the Part IV frames re-shot at 5120×1440 on both turn-6 boards (`SYSTEMS_REFERENCE.md` §127). Each part: the sibling sweep after every fix; a series attribution where a fix reaches the AI (`BASELINE_SERIES` attributed, never re-pinned blind); the DD-1 sign-ability sweep and fuzzer re-run where the predicate moves. **Done when:** 0 OPEN §PC rows; the Part IV frames re-shot on the two turn-6 boards so every peace moment names the road that carries and its price; the three Part V replays pass as tests (the Pressburg trade authorable and ratified with Tyrol to Bavaria; a truce that keeps the ledger; a dictated peace carrying a province on ulm). PC-F46 and F47 (layout) stay with UXR-4 at S15's head. | 4 | The research found the AI's beaten court silent where it should sue, Talleyrand's surfaces offering, pricing or drafting what the game then refuses, and his counsel a fixed string; the five peaces of the period showed what the machinery must sign. |
| ~~S13f (one part)~~ ✅ **LANDED October 17, 2026; S13f STRUCK** (gate + landing record `REFORMS_SPEC.md` §5a; rules `SYSTEMS_REFERENCE.md` §125; pins `tests/test_ao_the_army_order.py`; rows `BUG_FIXES.md` §CF: CF-1 and CF-9 FIXED, CF-2 and CF-3 STRUCK by the user, CF-5 folded into CC-4, CF-4 / CF-6 / CF-7 / CF-8 FIXED October 17, 2026 in a side session — rules `SYSTEMS_REFERENCE.md` §126, pins `tests/test_cf_the_four_rows.py`) | **AO "the army order"** — from the command-feel review (`docs/audits/COMMAND_FEEL_2026_10_16.md` §10) and the user's rulings of October 16–17, 2026 ("the army moves as one after getting the tech; before then the corps may follow a friendly unit, it just costs more; all army orders only work if Napoleon's authority is high enough"; then "make decisions and code it, make it work well") | **FOLLOW** — `Soult, follow Ney` / `march with` / `keep pace with` / `accompany`: a SUPPORT that stands (`standing_follow`), re-paths each turn, never lapses on "secure"; `follow <enemy>` is the PURSUE. **The fan-out** — `everyone fortify`, `all marshals march to Swabia`, `the army marches on Munich`: every corps in turn at its own price, the sum against the pool at the head, refusals named, the pool's edge named, an objection pausing the order (the popup) and the rest going on when it is answered — on the popup, interrupt and typed roads. **The army order** — with the Staff in force a collective standing order is ONE order at 2 actions for the Emperor's column (within 2 provinces of the sovereign), free and unasked for its members under the authority gate (70 carries · 50–69 a doubter refuses · below 50 the fan-out with the reason). The province panel's FOLLOW rows and THE ARMY row (a dimmed chip that names the reform until it is bought). "everyone retreat" and "everyone attack Mack" unchanged. Three questions left open to the user in §5a. | 1 | The group order was the typed road's largest hole (fortify is 15 % of everything a France issues) and the Staff's +1 was a thin reward for 9,000 gold; the user's ladder gives the reform its historical meaning. |
| ~~S14~~ ✅ **COMPLETE October 21, 2026** (part 1 ✅ LANDED October 20, 2026; part 2 ✅ LANDED October 20, 2026; part 3 ✅ LANDED October 20, 2026 — PC-R7 CLOSED; part 4 ✅ LANDED October 20, 2026 — SF-RR7, SFR-B3 / PC-X69 / DDB-X4 FIXED; **the Score Finish residue: SF-RR1 (ii) ✅ CLOSED by its re-read and SF-RR2 … RR6 ✅ LANDED October 21, 2026 (`SYSTEMS_REFERENCE.md` §137–§141) — the residue COMPLETE; its last sibling, RR6-X3, and the ending's copy row UXR3-F11 head S14b**) | **PC-R7 (ii) + SF-RR7 + SF-RR1 (ii) … RR6** | **Its head, PC-R7 (ii) "the moderate peace"** (ruling J's second half, sized at S13e part 4's head and moved here — `BUG_FIXES.md` §PC PC-R7, OPEN). ~~**Part 1 — the compensation clause**~~ ✅ **LANDED October 20, 2026** (rules `SYSTEMS_REFERENCE.md` §133): `territory_compensate` (`backend/game_logic/compensation.py` — paid: a third party's frontier province; pointed: the loser's own design recognised and licensed) validated, scored by both scorers, ratified by both ratifiers, authored from the guided rows, carried by the hand-off and asked by the AI's letter; the moderate Pressburg carries on the Vienna-held board (71 / 58 against the harsh 36); the siblings PC-X28 … X32 FIXED; the series byte-identical on four arms, IQ-6's courted drive re-measured and attributed. ~~**Part 2 — declared goals**~~ ✅ **LANDED October 20, 2026** (rules `SYSTEMS_REFERENCE.md` §134; sized at its head — the bond did not fit beside it and heads part 3): the War Purpose card and the AI's design war declare up to two ARTICLES (a province, an indemnity, a client — `backend/game_logic/declared_goals.py`), priced at the declaration in the treaty annex's per-province alarm on the declarer's slot; a declared article is legitimate at the table (the tier read's surprise skips it), the table opens on the declared draft, its guided rows lead with them and the counsel prices that draft first; every road that ends a war settles each article once, a dropped one refunding half its alarm; the series byte-identical on six arms. ~~**Part 3 — the bond**~~ ✅ **LANDED October 20, 2026; PC-R7 CLOSED** (rules `SYSTEMS_REFERENCE.md` §135): the league's no-separate-peace bond (Chaumont — `backend/game_logic/bond.py`), a dated D5 record of `kind="bond"` the paymaster mints for the member about to break ranks whom its gold can hold (GR5: France's Cabinet row "Bind <ally> to the War" calls the same mint); priced on each surface at its own gold rate — the break-ranks lines deeper, the table's component on her separate peace (−40 for a fresh 400-gold bond), the bilateral's (−12); a separate peace inside the term reneged as a broken bargain; France's bid (1,000 gold, or a compensation) offsets it — named by the counsel, offered at the table, staged by the Cabinet's "Outbid Britain's Bond"; the siblings PC-X52 … X60 FIXED; the series moved by the mint alone (Britain binds Austria at turn 10), attributed and re-pinned. The whole of (ii): the `territory_compensate` clause (the loser paid in a third party's province, or its design pointed elsewhere) validated, scored by both scorers, ratified by both ratifiers and offered by the AI; declared goals at the declaration plus composable articles at the table (a declared term dropped at the peace refunds part of its cost); the coalition's no-separate-peace bond priced; the moderate Pressburg (Salzburg for Tyrol) authorable and carrying on the Vienna-held board. Done when `tests/test_pc_rulings.py::TestPCR7` carries the (ii) pins and the series moved is attributed. ~~**Part 4 — SF-RR7 "the morning of the peace"**~~ ✅ **LANDED October 20, 2026** (rules `SYSTEMS_REFERENCE.md` §136; pins `tests/test_vp2_the_imperial_peaces_morning.py`): SFR-B3 ruled "Europe waits on Paris" and built — while the Congress sits and fewer than two great powers refuse it no new league declares against France (a brew holds at its last turn, the instant bar brews instead; the two-refuser gate untouched), the signing spends the alarm to the Armed Peace's watch (45) and dismisses any brew, and the page names what the peace bought; the PRESS arm's morning carries no league, the alarm reads 45; PC-X69 ruled (a bonded great power's Congress suit is her priced separate peace — the sue line reads the bond's depth, every surface tells it, the renege stands); DDB-X4 (the Congress's series arms flip fourteen live seams and re-read `BASELINE_SERIES` byte for byte); the siblings RR7-X1 … X9 FIXED. **Then the Score Finish residue resumes (NEXT),** with the October 13 rulings: EG-D3's bench for Spain, Sweden and Bavaria (SF-RR4) and EG-D1's checklist v1.2 re-band (SF-RR6); EG-D2 was ruled keep, with nothing to build | per spec | |
| S14b (gate + three parts; **its head ✅ LANDED October 21, 2026 — RR6-X3 one sighting rule (with RR6-X4 … X11) and UXR3-F11 the titled tally, `SYSTEMS_REFERENCE.md` §142; VP-1's gate ✅ RULED October 22, 2026 — `docs/VP1_DESIGNS_SPEC.md` (three roads, six designs, THE DECISIVE PEACE; its siblings `BUG_FIXES.md` §VP1); ▶ NEXT — part 1, the substrate unarmed (§9)**) | **VP-1 "The Emperor's Designs"** (from ROADMAP 12, brought before the deploy October 14, 2026) | **France's own objectives**, on the nation-agendas substrate the AI's designs already use: a short deck of designs for France (each an objective with its progress shown on an existing screen — the Diplomatic Ledger's Balance of Europe and the morning dispatch — and a reward on completion), two or three paths with the branch irreversible, and a **decisive-peace triumph** that ends a campaign short of the Congress through GE's `record_ending` seam (mark and continue, as every ending). **The gate first**, ruled in its own session under the standing delegation (research, then rule; a reversal of a user ruling is flagged): the drafted questions (`docs/audits/ROAD_TO_EA_REPLAN_2026_08_03.md` §52), what the designs are (the Rhine / Italy / the Continental System / humbling a court — history-first, the user's lean), their rewards, how the triumph sits beside the Congress and the Verdict, and the two parked ideas it absorbs — WO-D4(b) winning by economic dominance and SF-ECON-1 "Acts of the Empire" (a gold road into the designs, the peace road's sink). Done when the gate is recorded, the designs are playable and pinned through the real endpoints, a commanded 40-turn arm completes one design and the triumph records, the series moved re-pinned with this row named, and the store page's entry condition (c) reads met | 3.0 | No road reached an ending in 20 turns, the peace road's second half was empty (DD-B), and the store page's own condition (c) asks for it. |
| S14c (gate + four parts) | **Events and historical moments** (from ROADMAP §8.5 and the August 3 cut list, brought before the deploy by the user October 14, 2026: "add events to plan as well") | **An event engine on the existing transport**: an event is a decision letter on the incoming-proposal / mailbox road (or a dispatch beat for a choice-less moment) whose two or three answers each run through existing seams — gold, trust, relations, stability, a court's alarm — deterministically (Golden Rule 6). **A first authored deck for 1805–1807**: the historical moments keyed to their dates or conditions (Trafalgar's news, the Confederation of the Rhine, the end of the Holy Roman Empire, the Berlin Decree, Tilsit), and situational events keyed to the board (a marshal's quarrel, a province's unrest, a court's overture), varied per campaign seed inside authored bounds (AI_INTENT D7's rule). Events about AI courts reach them through the same functions (Golden Rule 5). Paced by the one-foregrounded-crisis tempo rule (AI_INTENT §4.6a) so the log never floods (IGR-1). **The gate first**, under the standing delegation: does the derived drama already cover a moment (the August 3 memo's question), the deck's contents, the cap, and the **Diplomacy & Flavor Content Menu** (`DESIGN_REFINEMENT.md` 8.EVAL rows: marriage alliances, vassal personality events, secret treaties, the point-of-no-return popup …) picked at the same gate. Done when the gate is recorded, the engine and the deck are pinned, a seeded 40-turn sweep shows events firing within the cap on every seed, the client shows each as a decision with its consequences named, and the moved series re-pinned with this row named **VP-1 hand-off (October 22, 2026, `docs/VP1_DESIGNS_SPEC.md` §11):** an event on the Confederation of the Rhine, the end of the Holy Roman Empire, the Berlin Decree or Tilsit reads `world.imperial_designs` — it never fires on a forsworn road and never doubles a proclamation. | 4.0 | The empty second half of the peace road (DD-B), and the narrative the user asked for; the engine is new machinery, so it lands before the re-measure reads it. |
| S14d | **The table lesson — the onboarding pass** (`DESIGN_REFINEMENT.md` 8.EVAL "Pre-EA Onboarding & Teaching Pass": R159 + "The Congress" lesson) | **Each core screen names the mechanic it shows** the first time it opens (the Cabinet, the settlement table, the per-court separate peace, the LAWS book, the Admiralty's camp and staging, the muster's free "what if" preview, VP-1's designs, an event letter), and **a second School of War lesson, "The Table"**: a short authored scenario that teaches a separate peace, a vassal proposal and Talleyrand's missions in a few steps, built like the Danube lesson. Built last of the new features so it teaches final mechanics (the roadmap's own warning). Done when every core screen carries its line, the lesson plays through on the real client (the DD-B instrument) and its pins hold, and a new-player run reaches the table on turn 1 | 1.5 | Every road to the table was shut on turn 1 for the diplomacy player; the settlement screens made most of DD-B's P2s; LAWS and staging went unexplained. |
| S14e | **DD-B's re-measure** (moved from S13b part 5) | Three fresh players, the same brief and roads, 20 turns each IN THE CLIENT on the DD-B instrument (`SYSTEMS_REFERENCE.md` §115), reading the game Round 0 will meet: the DD-B fixes, the rulings, VP-1, the events and the table lesson. Every row filed by DD-B's rule, de-duplicated, homed. Done when under 5 rows per 10 turns and 0 P1 — otherwise every new row is homed to S14f | 1.0 | Measures the build external testers will get. |
| S14f (if needed) | **The re-measure's rows** | Whatever S14e files, sized at S14e's close, P1s first, the sibling sweep in force. Done when every row is FIXED with its test | sized at S14e | The deploy gate (0 open defect rows) holds S15 until it is empty. |
| S15 | **UXR-4 + the deploy** | **The deploy gate (ruled October 14, 2026): the release build does not start while any defect row is OPEN** — the UXR-4 marks are read and fixed at S15's head, before the build. **Code signing** (from ROADMAP 16, brought here October 14, 2026): the release build signs the server and client executables with the user's code-signing certificate, and the clean-machine run checks that SmartScreen raises no block — owed by the user before S15: the certificate (a purchase; an OV/EV certificate or Azure Trusted Signing). The user's sign-off at their monitor, which also reads the eleven R2 marks S12 re-homed (rows UXR3-2, 24, 29, 41, 79 … 81, `UX_UI_REVIEW_PLAN.md` §UXR-4; its head re-stages UXR3-41's two boards) and the peace report's two layout rows, PC-F46 (the armistice letter's cost below the fold) and PC-F47 (the default tooltip panel: translucent, unwrapped), fixed at its head; the release build; the clean-machine run | 1.0 | |
| S16 (after the deploy) | **CODE-6** | The `main.gd` split into the four scripts `CODE_HEALTH_PLAN.md` §CODE-6 names. Done when the parse harness, the driven harnesses and the boot smoke read 0 `SCRIPT ERROR`, and the ratchet gains a `main.gd` line cap | 1.0 | Ruled October 13, 2026 under the user's delegation: the first post-deploy patches land in the client, so the client file goes first. |
| S17a–d (after the deploy) | **CODE-5** | The file splits, one per session, in the order `CODE_HEALTH_PLAN.md` §CODE-5 lists them: `world_state.py`, `diplomacy.py`, `main.py` routers, `combat_executor.py`. Each is import-only; done when `score_run check` is identical, the re-exports are removed one session later with the tests re-pointed, and the ratchet gains the file's line cap | 1.0 each | Ruled October 13, 2026: none changes what the game does, so none waits in front of the deploy. |

≈ 31–32 sessions before the deploy (October 14, 2026: S13b added by the S13 close and sized at four parts by the rulings, S14 grown by SF-RR7, and S14b VP-1, S14c events, S14d the table lesson and S14e the re-measure brought before the deploy by the user; S12b added October 13, 2026; S12 re-sized to two by the S11 close), with CODE-1 finishing in the heads of S2–S13.
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

#### DD-0 S4 landing record, part 2 — the measurement (October 10, 2026)

**The done-when, read on a FRESH set — and NOT met.** A fourth blind author (an
agent that used no tool: never the repository, the corpus, the tests, the docs or
the three earlier blind files) wrote 300 orders from the boot screen's facts and the
judge's family names; the file `tools/playtest_scripts/unrehearsed_2026_10_10_fourth.json`
was saved as written. Run keyless and keyed on this tree through the real
`POST /command`, read by the ONE judge, every row carrying its trace (records
`docs/audits/unrehearsed/2026_10_10_fourth_{keyless,keyed}.json`; memo
`docs/audits/UNREHEARSED_CENSUS_2026_10_10_FOURTH.md`; pins
`tests/test_dd0_fourth_blind_set.py`):

| arm | as meant | asked | board refusal | refused as meant | honest refusal | shrug | misread (judge) | executed when refusal meant (judge) |
|---|---|---|---|---|---|---|---|---|
| keyless | **119 (39.7 %)** | 37 | 49 | 24 | 27 | **33** | 5 | 6 |
| keyed (54 live parses) | **134** | | | | | 3 | 4 | 7 |

By hand, of the judge's eleven keyless dangerous rows: **two real executions**
(`Murat, your light horse to the Tyrol — eyes only, no fighting.` FOUGHT — DD0-11;
`Berthier, inform the courts: France declares war on Sweden.` became a charm
mission — DD0-12), one wrong order on the desk (DD0-13), two dropped halves behind
a question (DD0-14), one disclosed substitution (the retreat road's safe province,
said), five honest refusals in shapes the judge does not know (DD0-8's next rows).
The 33 shrugs are the march register's idioms (15 — DD0-15), the attack register
(DD0-16) and the desks' idioms (DD0-17). The same tree reads the third set at 177
of 300: a file rehearsed by its own fixes against a fresh author's 119.

**What the measurement says.** The Reading closed the ledger and the third set's
shrugs because those were the classes the instrument had named; a fresh author
names new ones at once. The ≥ 85 % will not be reached by rewrite rules alone — it
needs the spine split's second half, the readers consuming the Reading's slots
(addressee, verb, objects) instead of re-scanning a composed string, so that
`Murat — rhineland — go.`, `ney franconia pls` and `Marshal Davout is to march his
corps to Franconia` are one reading. **S4 part 3 takes:** the spine split
(`_parse_with_mock_chain` / `_execute_one` along the trace's stages, the Reading
carried through), DD0-11 … DD0-17, the fourth set re-read (the file stays blind —
a fifth author's set for the done-when if the fourth becomes rehearsed), the HOLD
arm re-read; then S5–S6 DD-1 (its head CODE-1 batch 3).

#### DD-0 S4 landing record, part 3 — the spine split, the slot reader, the worklist, the fifth author (October 10, 2026)

**The spine split, both halves, byte-identical** (rules `SYSTEMS_REFERENCE.md` §104
part 3; pins `tests/test_dd0_s4_part3_the_slots.py`). `_parse_with_mock_chain` (1,704
lines) is eleven named stages reading ONE `_ChainState`; `_execute_one` (2,208 lines)
is ten reading ONE `_ExecState`; every line sliced verbatim, each stage's early return
the chain's end; `tools/gen_routed_order_words.py` walks the stages (the harvest
unchanged); `score_run check` byte-identical to `38daa024` after each half; the full
suite on the hook. Found by the split: the chain's invest idiom was dead code since
S3b (the `or` inside the `any(...)` call) — fixed.

**The second half — the slot reader.** When the verb chain finds nothing, the
Reading's slots (the addressee, the places, the foes, the residue) are read instead
of the composed string: a man and a destination in the words of a march IS the march;
a man, one foe and a trigger word IS the attack. The Reading gains the statement after
the address, the trailing statement, the dash aside, the emphatic tail, the inverted
name, the second telegraph, the courtesy modal; the strategic layer keeps the chain's
KNOWN place or commander instead of re-scanning. **DD0-11 … DD0-17 all fixed** but the
Cabinet's bare desk (DD0-18's half); the judge learned three refusal shapes and
withheld two (49 committed classes would move).

**Measured.** The fourth set as fresh runs: **keyless 119 → 145 / 141 of 300 (48.3 / 47.0 %, two runs — the objection dice),
shrugs 33 → 5, misread 5 → 2 (the judge's desk class), executed-when-refusal-meant
6 → 3 (all the judge's; by hand 0); keyed 134 → 150 (18 live parses).** The third
set 177 → 182 / 176 (two runs, the dice); the HOLD arm 18 of 20 before and after the executor split; the
metamorphic ledger 0; corpus 678. **The fourth file is rehearsed by its own fixes, so
a FIFTH blind author (zero tool uses) wrote 300 orders: keyless 125 of 300 as meant
(41.7 %), keyed 137 — the ≥ 85 % done-when NOT met a second time; read RIGHT by
hand (as meant + asked + the board's refusal + refused as meant) 241 of 300
(80.3 %).** By hand one real execution (`Ney, strike camp, abandon the works.` fought
— `strike` read as the battle verb) and one chooser staged against our own vassal
(`Declare war on Holland.`); the 29 shrugs' register filed as DD0-18 (memo
`docs/audits/UNREHEARSED_CENSUS_2026_10_10_FIFTH.md`; pins
`tests/test_dd0_fifth_blind_set.py`); the file stays blind.

**What the second measurement says — put to the user at part 4's head.** Two fresh
authors on two trees read ~40 % as meant and ~80 % read right by hand. The gap is
the boot board's: the provinces beside our corps are a neutral's (Hesse, Saxony,
Switzerland, Bavaria), so a quarter of every author's marches are refused by the
border law, and the marshals object to a quarter of the rest — both the game reading
right, neither `as_meant`. The gap between 80 % and the parser's ceiling IS the
parser's (each author's new register). **S4 part 4 takes, at the user's word:** keep
the done-when as written and widen the vocabulary author by author (DD0-18, then a
sixth author), or re-base its instrument to *read right by hand ≥ 85 % and 0
executed-other-than-meant* (recommended — the pillar's actual question); either way
DD0-18 (a) and (b) first. Then S5–S6 DD-1 (its head CODE-1 batch 3).

**▶ RULING (October 11, 2026) — THE INSTRUMENT IS RE-BASED.** The DD-0 done-when
reads: *a FRESH blind set reads ≥ 85 % READ RIGHT BY HAND keyless (as meant + asked
+ the board's own refusal + refused as meant) with 0 executed-other-than-meant*; the
`as_meant` figure is printed beside it, never in its place. Made at part 4's head;
recorded here, in §2's S4 row, `STATUS.md` ▶ NEXT UP, `SYSTEMS_REFERENCE.md` §104
part 4 and the `CLAUDE.md` LIVE STATE line; not to be re-opened.

#### DD-0 S4 landing record, part 4 — the re-based instrument, DD0-18, the sixth author (October 11, 2026)

**The instrument** (rules `SYSTEMS_REFERENCE.md` §104 part 4; pins
`tests/test_dd0_fifth_blind_set.py` re-seated). `tools/unrehearsed_census.py` prints
**read right by hand** (as meant + asked + board refusal + refused as meant) and
**executed other than meant (by hand)** beside the judge's classes, with `as_meant`
beside both. The judge's `misread` / `executed_when_refusal_meant` are its PROXIES:
each proxy row is read against its trace by a person and the reading is a committed
file beside the records (`docs/audits/unrehearsed/by_hand/<set>.json`, applied with
`--by-hand`), each verdict pinned to the reply it was read against (`reply_starts`) —
a re-read whose reply changes makes the verdict stale and the row UNREAD, and an
unread proxy leaves the by-hand count `None`, never a default 0. The verdicts:
`executed` (the dangerous class), `staged`, `disclosed`, `asked`, `honest_refusal`,
`wrong_desk`, `board_refusal`. **The fifth set on the re-based instrument, before
the fixes: keyless 241 of 300 read right (80.3 %), executed other than meant 1
(`Ney, strike camp, abandon the works.` fought); keyed 265 of 300 (88.3 %), 1.** The
hand also reads an `honest_refusal` as the BOARD's own when the reply is the board's
in a shape the judge does not know (the border law's *"Cannot enter Frankfurt — it is
controlled by Hesse (PEACE)"*, the levy's reach rule, the unknown law) — the record
then carries `read_right_by_hand`. The judge learned `is our own vassal` (new this
part) and the Cabinet's three WAR-state card openings as ASKED; the two PEACE-state
cards were withheld (each moves two lines in every third-set record).

**DD0-18 fixed** (rules §104 part 4; pins `tests/test_dd0_s4_part4_the_register.py`,
59): (a) an unfortify idiom in a line naming no foe outranks a bare battle verb — the
ORDER, with `strike / break camp` joining the idiom and `break camp and march to
Bohemia` kept as ONE march (D10's pin); (b) `own_vassal_refusal` — the Cabinet refuses
a war on a satellite of ours in words before the chooser, `declare_war` the player's
backstop; (c)–(e) the register (the inflected verbs, the march and retreat idioms, the
purpose and participle tails, the watch precaution, the foe statement before the
order, the desks, the Cabinet's bare desk → the IMPROVE_RELATIONS mission and the
court by its seat, `lannes dont move` → the hold). **The fifth set re-read: keyless
as meant 125 → 144, shrugs 29 → 1, read right by hand 241 → 289 of 300 (96.3 %),
executed other than meant 1 → 0; keyed 291 (97.0 %), 0.**

**The SIXTH fresh author (zero tool uses; memo `docs/audits/UNREHEARSED_CENSUS_2026_
10_11_SIXTH.md`): keyless 249 of 300 by the judge (83.0 %) — and by hand THREE real
executions** (`Send the fleet to attack Swabia.` fought with Soult's corps; `Davout:
drill. The new conscripts are green.` recruited; `Bernadotte leaves 3000 men to hold
Franconia` held) — **NOT met on the hard clause. Filed and fixed the same day as
DD0-19** (the fleet as a subject is refused before any routing; the generic tokens of
a multi-word name no longer keep a statement; the garrison idiom's inflections; the
19 shrugs' register). Re-read, rehearsed: 290 of 300 by hand (96.7 %), 0; keyed 295, 0.

**The SEVENTH fresh author — the done-when READ (zero tool uses; nothing in the file
read or tuned before its run; memo `docs/audits/UNREHEARSED_CENSUS_2026_10_11_SEVENTH.md`;
pins `tests/test_dd0_seventh_blind_set.py`): keyless 255 of 300 READ RIGHT BY HAND
(85.0 %), 0 executed-other-than-meant — MET, at the floor with no margin, and 255
again on a second run of the final tree; keyed 281 (93.7 %), 0; `as_meant` 152 / 300
(50.7 %) beside.** The eleven rows the hand moved
are the border law (seven), the reach rule (one) and three refuse-meant lines the
board refused; the six proxy rows ran nothing (two wrong desks, one staged proposal,
three board refusals). The 26 shrugs and the parser's 15 honest refusals are
**DD0-20**, OPEN and owned by S5's head beside CODE-1 batch 3 (the file stays blind;
the done-when is met, so it requires no eighth author).

**The floors held:** the third set re-read 273 of 300 by hand, as meant 179 (182 / 176
before — the objection dice), 0 / 0; the fourth set 286 / 290 by hand, 0; the HOLD
arm 18 of 20; the metamorphic ledger 0 (2,408 cases); the routed order words
regenerated (367); no lever landed; the full suite on the hook. `score_run check`
was NOT run: part 4 changes the parser's reading by design and the plan forbids a
re-score. **S4 is STRUCK; next S5–S6 DD-1, its head CODE-1 batch 3 (`diplomacy.py`,
`vassal.py`, `jealousy.py`, `naval.py`) with DD0-20 beside it.**

#### DD-0 S5 landing record — DD0-20, the seventh set's register (October 11, 2026)

*Landed beside CODE-1 batch 3 at S5's head (batch 3's own record:
`CODE_HEALTH_PLAN.md` §CODE-1 BATCH 3). Rules `SYSTEMS_REFERENCE.md` §105; row
`BUG_FIXES.md` DD0-20 struck; pins `tests/test_dd0_s5_the_register.py` (53) and
`tests/test_dd0_seventh_blind_set.py` re-seated; memo
`docs/audits/UNREHEARSED_CENSUS_2026_10_11_SEVENTH.md` "The re-read".*

- **What was built.** The 26 shrugs, the two wrong desks and the parser's share of
  the 15 honest refusals, each re-typed and driven through the real `POST
  /command` — the Reading learned the possessive on a name, the from-to pair, the
  haste clause (`before Mack can slip away`), the ground-to-be-held purpose
  (`Secure the rear.`, `to cover the northern flank`, `to form the reserve`), the
  comma support suffix (`, Ney in support`), the muster that is no rhetoric and
  the title alone (`the Archduke` when one is in view); the rewrites learned the
  arrow, the colour tails (the hour, the calendar, the weather, the rations, `save
  the corps` — never the bare `tomorrow`, FA-7's deferral), the cry before the dash
  (`Sortez —`), the aim before an addressed order, the Cabinet's delegation (`Have
  the Cabinet …`, `a treaty of alliance`), the mission's aim behind the dash,
  `sound out <court>` (the assessment), the foe premise joined by `so`, `assail /
  assault <foe>'s position / break <foe> / run <foe> to ground / goes in against`,
  `the Guard and I`, the depot asked of Berthier, gold sent to a court's treasury,
  `draft and enact`, `where the foe is, there he goes`, `is ordered to <place>`,
  `everybody on <foe> (Soult leads)`, `talk to <court> about`, `is to retire`, the
  levy's register (`a levy in Guyenne`, `call up men in Flanders`, `more men at
  Lyonnais` — the bare `levy <place>` stays CX-R1's), `mend the walls at`. The
  Cabinet reads the court named FIRST (`sound out Denmark … to the British` is
  Denmark; the alias table and the roster patterns by position; an alias at a
  word's start only) and refuses in words a letter that asks a court for its men
  (`no_letter_asks_for_men` — a loyal satellite's contingent takes the field of
  its own accord, VD-C). The head-restating rule set names every new head shape so
  the executor's addressee gate, which reads the TYPED line, takes no consumed
  head for a name.
- **The re-read (fresh runs, the file blind):** keyless as meant 152 → 174 / 173
  on two runs of the final tree, shrug 26 → 1 / 2 (the bare `probe`; `berthier
  appoint mortier` with the dice), the judge's four 244 → 277, **read right by hand
  255 → 294 of 300 (98.0 %) on both runs**, executed other than meant 0; keyed 162 → 172 / 175 as meant,
  **281 → 296 (98.7 %) on both runs**, 0, the model consulted on 7 lines where it
  had been on 37. The hand file: the two wrong-desk rows withdrawn with their traces, four
  board refusals added (the border law ×2, the reach rule ×2), each pinned to its
  reply. The three refusals left on both arms are the design's own contingencies.
- **The floors held:** the dd0 / cx / cmd1 / cr7 / robustness pin batch 3,072
  green (the metamorphic ledger 0, the third set's floor, the HOLD arm); one pin
  moved during the build and moved back — D10's `and hold the line` had been
  eaten by the first cut of the ground-purpose peel (`hold` left the verb list,
  the `and` form withdrawn); **the hook's full run caught two more**, both
  narrowed and pinned beside the register: the possessive strip had read
  `Mack's line of retreat` as Mack and Lannes RETREATED (CRT-6's pin; the strip
  now reads the ground he holds — position / camp / works — and never before
  `of`), and the Cabinet's delegation head had taken `Have Talleyrand back
  Prussia's quarrel with Austria` away from the sponsorship idiom that reads its
  aim (the head now reads the office — the Cabinet, the foreign office — never
  the man). Routed order words unchanged (no router keyword moved); no lever;
  `score_run check` not run (the hand-off forbids the re-score).
- **Recorded, not filed:** `Davout, go to Swabia before Mack attacks.` marches on
  this tree AND on the committed one (`6633633a`) — the clause-guard reads
  `before <foe> attacks` as no contingency; the new haste peel declines it (an
  order verb in the clause) and leaves that reading where it was.

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
- **The structural fix that falls out** (and it absorbs CODE-2's `_process_dialogue_choice` and `_ratify_treaty` splits, done with purpose — *corrected October 13, 2026: it did not; both stayed over 500 lines and are S10b's CODE-2c*). ONE verdict, `treaty.can_sign(letter,
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

#### DD-1 S6 landing record — the instrument before the fix (October 11, 2026)

*The three instruments built and read on the committed tree, nothing fixed —
the findings are Step 2's worklist, exactly as DD-0 S3 did. Rules
`SYSTEMS_REFERENCE.md` §106; rows `BUG_FIXES.md` §DD-1 S6 (DD1-1 … DD1-12, all
OPEN, owned by Step 2); memos `docs/audits/SIGN_ABILITY_SWEEP_2026_10_11.md`,
`docs/audits/TREATY_FUZZER_2026_10_11.md`, `docs/audits/ANSWER_BINDING_2026_10_11.md`;
records `docs/audits/dd1/`; pins `tests/test_dd1_sign_ability_sweep.py` (20),
`tests/test_dd1_treaty_fuzzer.py` (14), `tests/test_dd1_answer_binding_shuffle.py`
(10); ledgers `tests/data/treaty_fuzzer_known_violations.json`,
`tests/data/answer_binding_known_misbinds.json`. No change in `backend/`:
`BASELINE_SERIES` byte-identical by construction, no lever, no `.gd`, no
re-score.*

- **1. The sign-ability sweep** (`tools/sign_ability_sweep.py`). Every promise
  of the six surfaces dry-run through the REAL ratifier on a clone of the
  world at the moment it is shown (the accept road itself — never a second
  copy of its rules; 6 ms a clone), on `score_run`'s six diplomacy arms and
  three fresh seeds. **2,830 promises; A "shown as signable, refused when
  signed" = 11, every one a LETTER** — the ally petition that cannot be
  granted from the letter (×4, and its editor's raw code is B = 2), the
  client petition for a province already given, SFR-B1's leader-only
  settlement letter (×2, reproduced), the one-on-one settlement letter (×2);
  **every chip (2,287), Congress row (253) and settlement verdict (148) agreed
  with the ratifier**; the counsel never named a treaty on these arms; no real
  sign by the player was refused on any arm (SF-V1 / SF-V5 hold for the
  bilateral letters they govern — the eleven are petitions and settlement
  offers, which they do not).
- **2. The treaty state-machine fuzzer** (`tools/treaty_fuzzer.py`). Random
  lawful sequences of the ten verbs through the real executor as structured
  commands, the §70 / §81 invariants read after every step, the world
  round-tripped every step, every write to `diplomatic_states` attributed to
  its frame. **10 seeds × 1,000 steps: 81 distinct violations in 7 classes** —
  the bilateral armistice and the conquest vassalage leave the war instance
  claiming the pair at war (14, up to 330 steps); a WAR pair with no purpose
  (5, papered over by the load migration); the save round trip not identity
  on the pending popups, a counter-offer's `blocking`, a notification and the
  purpose (55); a client taken by an AI lord keeps the wars the lord does not
  fight (4 — SFR-D28's rule from the other side); a re-declared resolved pair
  keeps its exited / resolved stamps (3). **I3 held on every seed — 0 writes
  outside `set_diplomatic_state` over 10,000 steps**; nothing below zero; no
  verb raised. The refusal tally: the raw `war_instance_side_conflict` code
  36 times; the smoke seed's I7: `VASSAL→OPEN_BORDERS` signed by the ratifier.
- **3. The answer-binding shuffle** (`tools/answer_binding_shuffle.py`). Three
  letters in every order, every typed form and every button through the real
  endpoints against the shipped contract. **312 rows: 308 bound; 4 misbinds,
  ONE class** — `decline <court>'s pact` is not read as an answer (`pact` is no
  matter noun) and falls to the order desk; nothing moved.
- **The done-when, read:** the sweep 0 / 0 → **11 / 2, NOT met**; the fuzzer
  0 → **81 in 7 classes, NOT met**; the shuffle 0 → **4, NOT met** — each
  asserted NOT met in its pin so it is re-seated on purpose when Step 2 lands;
  every count lower-only, every class ledger a ratchet.
- **What the reading says about Step 2.** The five polled surfaces already
  agree with the ratifier on these arms — the "six places" problem is live in
  the LETTERS (petitions, settlement offers) and in the ratifier's own
  blindness (`validate_transition` unread; the instance not restamped on the
  bilateral exits). `can_sign` therefore has two halves: the guard sequence
  lifted out (the state machine first, then the ladder, the floors, the
  eligibility gates, the clauses) read by every emitter and every button; and
  ONE exit for a pair (the ratifier, the conquest and the settlement all
  restamp the instance through it). DD1-1 … DD1-12 are the worklist, with
  SFR-B1 / B2 / B5 / D34 and the other open diplomacy rows beside them.
- **Found building, kept in the tools:** the driver re-execs itself when
  `PYTHONHASHSEED` is unset (the child sets it); a dry run on a clone must
  restore `random`'s state or it moves the arm's own dice; the engine prints
  through `print`, not only `debug_print`, so the fuzzer captures stdout per
  step; `settlement_actions` imports `ratify_settlement_confirm` by name, so
  both bindings are patched; the console's cp1252 chokes on the arrows in the
  engine's own messages — every tool reconfigures stdout to UTF-8.

#### DD-1 S7 landing record, Slice A — one exit for a pair (October 11, 2026)

*Step 2b and the fuzzer's and shuffle's rows, fixed at their seams and read
back by the instruments as they stand; Slice B (`can_sign`, Step 2a) follows
the review pause. Rules `SYSTEMS_REFERENCE.md` §107; rows DD1-5 … DD1-11
FIXED in `BUG_FIXES.md` §DD-1 S6 (each with its re-read as evidence); pins
`tests/test_dd1_s7_one_exit.py` (nine); the instruments' own pins re-seated
to 0 (`tests/test_dd1_treaty_fuzzer.py`, `tests/test_dd1_answer_binding_shuffle.py`);
one older pin re-seated (`test_sr1b…::test_the_lords_truce_is_the_clients_truce`,
"war" → "armistice"). No lever, no `.gd`, no re-score; `BASELINE_SERIES`
byte-identical. The §2 table: DD-1 was sized 1.5 sessions, so Step 2 takes
the S7 slot and CODE-3 + DD-C move to S7b.*

- **The reading.** `tools/treaty_fuzzer.py`: **81 → 0** distinct violations
  over 10 × 1,000 + the 120-step smoke seed (every record re-run, the ledger
  `tests/data/treaty_fuzzer_known_violations.json` emptied); I3 still 0
  writes outside the setter; the refusal tally no longer carries a raw code.
  `tools/answer_binding_shuffle.py`: **4 → 0** misbinds over 312 rows (the
  record re-run, the ledger emptied). The sweep untouched (A = 11 / B = 2 —
  Slice B's rows).
- **The one exit** (§107.1): `cleanup_war_end` restamps the pair's instance
  from the state the setter wrote — ARMISTICE pauses the pair
  (`mark_pair_armistice`), a peace resolves it — on every road that already
  passed through it; the typed conquest and the forced-alliance arm (its
  setter now first) join it; the cheat's own mark retired (DD1-5, I1
  ownership 14 → 0).
- **The client rule on ENTRY** (§107.2): `_reconcile_vassal_diplomacy` reads
  §70.2 when a court becomes a client — its wars with courts the lord does not
  fight follow the lord's footing through the exit, its own war (it or that
  court leads) excepted, the settlement's plan rows skipped; reason
  `vassalage_entry` is a signed peace (DD1-8, I2 4 → 0).
- **The re-entry** (§107.3): a reopened pair leaves the resolved list; a
  returning court's row is merged, exit stamps cleared, first `joined_turn`
  kept (DD1-10, I5 3 → 0). **The purpose** (§107.4): live = not concluded;
  the load migration stays dormant for pre-S7 saves — the user's call, the
  default taken (DD1-6, I1 purpose 5 → 0).
- **The round trip** (§107.5, DD1-7): the row's popup diagnosis was wrong —
  `from_dict` restored the slots; the load pass retired what the live world
  kept stale. Three producers fixed, no load change: the letter-popup slots
  read against the manager; the counter producers write `blocking: False` (a
  current-turn offer by type; `blocking` has no reader); a cooled quarrel
  retires its standing card on the live world (I6 55 → 0). Nothing re-homed
  to DD-C. The hook's first run caught four older pins that held the OLD
  behaviour (the counter's `blocking` True; the GET as the first seam to
  retire a cooled card; a stale letter slot survivable on the live world;
  F6 / SR-4c's replacement bypass keyed on a stale card still standing) —
  each re-seated with its rule, the bypass keyed on the settlement record
  instead, and the load pass reading the raw slot so a pre-S7 save keeps its
  receipt.
- **The words** (§107.6, DD1-11): `backend/game_logic/treaty.py` born with
  `declaration_refusal_words` — "Bavaria fights beside us in the war with
  Austria — end that war first". **The nouns** (§107.7, DD1-9):
  `_CLOSED_MATTER_NOUNS` ∪ the words of `PROPOSAL_TYPE_DISPLAY`.
- **Found fixing, kept:** `_ratify_treaty` is `WorldState._ratify_treaty`
  (`world_state.py`), not the executor's; its refusal dict is prose only. A
  synthetic fixture whose states table disagrees with its instance must keep
  the old behaviour — the exit trusts only an ARMISTICE written or
  `conclude_objectives`, nothing defensive beyond that. A re-war on a
  resolved pair opens a FRESH instance unless the pair is re-attached to the
  old one (`attach_pair_to_war_instance` is the reopening, the fuzzer's
  road). The fuzzer's I2 exempts a war the client OR the court leads — the
  entry rule mirrors it verbatim. The ally petition speaks `available` and
  the client petition `enabled`, and the sweep reads `enabled` — Slice B's
  `stamp_option` writes both from one verdict.
- **Slice B's worklist, unchanged:** DD1-1 … DD1-4, DD1-12; SFR-B1 / B2 /
  B5 / D34 closed by it; SFR-B3 / B4 / D43 already homed (ending /
  ai_aliveness / narration); Step 3's verbs (SFR-D28 announce half, D40, D42)
  for S8's head.

#### DD-1 S7 landing record, Slice B — `can_sign`, the ratifier's spine (October 11, 2026)

*Step 2a: ONE verdict, `treaty.can_sign(world, letter) → Verdict`, the
ratifier's guard sequence lifted out of `WorldState._ratify_treaty` and read
by every surface that shows a letter, a chip, a price or a counsel line AND
by the ratifier, which keeps no guard of its own. Rules
`SYSTEMS_REFERENCE.md` §108; rows DD1-1 … DD1-4 and DD1-12 FIXED in
`BUG_FIXES.md` §DD-1 S6, SFR-B1 / B2 / B5 / D34 FIXED in §Step 8 (each
with the sweep's re-read as evidence); SFR-B3 / B4 / D43 recorded there as
already homed (VP-2 / SF-RR3 / SF-RR3 — ending, ai_aliveness, narration);
pins `tests/test_dd1_s7_can_sign.py` (25, one per rule),
`tests/test_dd1_sign_ability_sweep.py` re-seated to 0 / 0 (the done-when
MET, the four S6 clauses asserted gone, the caps zero, the live quick set
matched to its re-recorded record); the ten records
`docs/audits/dd1/sign_ability_*.json` re-recorded; memo
`docs/audits/SIGN_ABILITY_SWEEP_2026_10_11.md` §The re-read. ONE `.gd` edit
(`incoming_proposal_popup.gd`: `enabled` read for any letter's accept). No
lever, no re-score, no new serialized field; `BASELINE_SERIES` byte-identical.*

- **The reading.** `tools/sign_ability_sweep.py`: **A 11 → 0, B 2 → 0** over
  the nine committed arms and the quick seed (2,822 promises; the fuzzer and
  the shuffle still 0, their pins now assert it). Reproduced before fixing on
  the OP and PRESS arms from the committed records: PRESS t28 was TWO client
  petitions for Brunswick (Hesse's by the Congress's summons, Holland's by the
  end turn — the two producers each read the lord's own list); OP / REACH-AAR
  t7 was the ally petition read at ARRIVAL while the settlement editor was the
  current hard stop (the instrument displaces the editor into the queue, a
  state no player road reaches) and read again when shown, its grant's
  editor withholding Ratify with a hard stop whose `reason` key the
  confirm builder never read (so the popup fell back to the raw code).
- **The verdict** (§108.1). Four letter kinds, dispatched by shape: (a) a
  TREATY letter — the ladder (its sentence byte-identical), the `vassal_pair`
  clause (no treaty is signed inside a vassalage; release is the road),
  `validate_transition` (DD1-12 — the ratifier had never read the state
  machine), the floors (player only, byte-identical), the AP clause read
  PROPOSER-over-target (it read the player's score against `target`, which
  on an AI letter was France against herself), the AI-AI alliance rule, the
  war bargains, the vassal gates through the creator's ONE predicate
  (`vassal.vassal_treaty_refusal`, which `create_vassal_treaty` reads too),
  and with `at_send=True` the send road's own paradox HARD_STOP on a player's
  outgoing peace (SFR-D34); (b) a SETTLEMENT offer — the settlement road's
  eligibility gate for France's side, closing ONLY on `one_to_one_war` /
  `not_side_leader` (DD1-3, SFR-B1; the other codes would silence the
  producer, whose `offer_already_pending` already governs), then SF-V5's own
  carry; (c) an ALLY petition — the war live, a suspended draft to join (a
  MOUNTED editor means "back out first" — the handler's mounted arm is
  reachable by no answer seam), the clause still prevalidating (DD1-1); (d)
  a CLIENT petition — `vassal._grant_verdict` (DD1-2). Every refusal in
  words; `names_a_raw_code` is the sweep's own `_RAW_CODE_RX`.
- **The stamp** (§108.2). `stamp_option` writes ONE verdict under every key
  its readers use — `enabled` + `reason` (the client petition's popup, the
  driver, the sweep), `available` + `disabled_reason_display` (the ally
  petition's popup, the wizard) — and the `closed_clause` marker. Two verdicts
  disable WITHOUT the marker (`closes=False`): a client petition's `stands`
  (its handler's road must run — IQ7-RV2's DP-short Grant STANDS) and an ally
  petition's closed table (its handler's refusal ROUTES to the table, SR-2a).
- **Who reads it** (§108.3). The ratifier (`refusal_dict`: the same dict plus
  `clause`); SF-V1's `treaty_offer_refusal` (the legacy debug strings kept
  for the ladder and floor clauses); SF-V5's `_emit_settlement_offer_for_war`
  (the eligibility arm before the carry, the refusal named in telemetry);
  `build_ai_proposal_dialogue` at build and `refresh_letter_verdict` at the
  four `main.py` read seams (the incoming-proposal popup, the envoy payload,
  the pending-envoy poll and the mailbox activation for settlement letters);
  the ally petition at birth and at its refresher; the client petition's keys;
  the answer seam (NPC-21 widened by MARKER, never by dialogue type — a
  marked accept is refused with the verdict's words, the letter standing,
  nothing logged as our rejection, no cooldown: SFR-B2 / SFR-B5); the send
  road (`execute_proposal` reads `can_sign(at_send=True)` — a proposal the
  table would refuse never departs, SFR-D34's paradox named through the same
  words); the wizard's chips (`_proposal_action` asks the verdict first, its
  sentence on `disabled_reason_display`, FA-D17's words kept for the paradox);
  the Congress's `_treaty_lever` and the peace levers (closed in words under
  `peace_closed`); the counsel's `_treaty_hint` (an alliance at relation 31
  against a floor of 40 now hints the defensive alliance; at war under the
  paradox, the armistice); the in-transit stale return names the clause.
- **Beside the verdict.** DD1-2's root: `petition_subject` skips a province
  another client's STANDING petition names (`regions_under_petition`). DD1-1's
  B rows: the confirm's `ratify_blocked_reason` reads a hard stop's `reason`
  through the settlement display map (`no_direct_war_score_for_covered_enemy`
  added, in words, the court named beside). DD1-4: `propose_white_peace` on a
  live war the player names reads the eligibility gate BEFORE the backfill
  resolver, so a war gone one-on-one refuses with its own clause.
- **Found by the fuzzer's live pin, fixed (its walk differs per
  `PYTHONHASHSEED`; seeds 4 and 5 reached what 0–3 did not):** the carve's
  pair stamp (`formations._seed_client_roster`) wrote `diplomatic_states`
  directly — through the setter now (I3); and a shadow-command card whose
  marshal (or Emperor) marched in `advance_turn` stood stale on the live
  world while the load pass retired it (DD1-7's class) — `end_turn` reads
  `petition_retirement_reason` once more after `advance_turn`, with its
  receipt (I6). Both seeds read 0 under every hash seed tried.
- **Pins re-seated with the rule (seven):** `test_sr2a_one_verdict_per_screen::
  test_an_open_table_flips_the_arm` (a mounted editor reads "back out
  first"; the suspended draft is the open table); `test_crt1…::
  test_the_proposal_confirm_twin_sends_nothing` and `test_phase4_batch3…::
  test_proposal_sent_logged` (the send road refuses a pact under its floor
  and a peace with a court already at peace — the fixtures send a treaty
  the table signs); `test_iq10_client_pass::test_the_line_does_not_add_a_
  second_full_stop` (the `.gd` verb line); `test_iq7_review_round::
  TestClientSourcePins` (the `.gd` reads `enabled` for any letter);
  `test_igr_f_envoy_digest::test_the_headline_names_a_formed_court` (the
  Kingdom of Italy boots as France's client — its letter is withheld now; the
  headline is read on a released Italy); the sweep pin (above).
- **Found fixing, kept:** the ratifier's refusal dict names `target_nation`
  on the ladder / floor / AP clauses and the player's counterpart on the
  bargain / vassal clauses — the verdict carries `target` so the dict is
  byte-identical; the paradox is the SEND road's gate, not the ratifier's
  (an incoming peace under it is a WARNING, and the Congress's "sign a peace"
  lever reads the ratifier's view, since the court's own envoy can bring it);
  the chip under the paradox keeps FA-D17's exact words (pinned); a hard
  stop is `{"reason", "enemy"}`, never `display` / `code`.
- **The score re-read** (CONG / OP / VOLTE through `score_run run` into a
  scratch dir, `check` run THERE, the archive untouched): the diplomacy
  items — see §108.5 for the figures.
- **S8's head:** Step 3 the verbs — `ask <ally> to return <province>`
  (SFR-D42), `bid for <court>` (SFR-D40), the truce's followers announced
  (SFR-D28's announce half); then CODE-3 + DD-C (S7b). CODE-1 batch 4 / 5
  ride the heads after DD-1. ✅ **S8 LANDED October 12, 2026 — the record
  below.**

#### DD-1 S8 landing record, Step 3 — the verbs (October 12, 2026)

*Step 3: the three verbs the depth campaign reached for and could not touch,
each through the shared executor (GR5), a corpus row and a wizard chip, each
reading ONE verdict the way `can_sign` taught. Rules `SYSTEMS_REFERENCE.md`
§109; rows `BUG_FIXES.md` SFR-D42 / SFR-D40 / SFR-D28 FIXED (SFR-D28's entry
half was Slice A's DD1-8); pins `tests/test_dd1_s8_the_verbs.py` (37); seven
corpus rows `dd1-s8-*`; `backend/ai/routed_order_words.py` regenerated (+7
words: asks, bid, bids, demands, enter, outbid, requests — `tell` / `urge`
left out of the ask regex: as routed order words they turned CRT-3's
"well then tell me why not retreat" from a question into an order); the
sweep's chip poll widened to the two new chips (`tools/sign_ability_sweep.py`
`VERB_CHIPS` / `dry_verb_chip`), its committed records UNCHANGED (no arm shows
either chip: no home province is ally-held and no auction opens on the nine
arms or the quick seed — A 0 / B 0 re-read); the fuzzer and the shuffle 0;
`BASELINE_SERIES` + M1–M7 byte-identical with no re-record; two `.gd` edits
(the wizard's two echoes; the Cabinet door's court-gated keywords in
`main.gd`, so a typed ask-back or bid is claimed by the wizard like every
other diplomatic order — WO slice 7's ruling; the Godot parse report
regenerated). The session's head was CODE-1 batch 4
(`CODE_HEALTH_PLAN.md` §CODE-1 BATCH 4): levers 496 → 429.*

- **`ask <ally> to return <province>` (SFR-D42).** `treaty.can_ask_return(world,
  asker, holder, region) → Verdict` is the ONE gate — the clause in words
  when the ask cannot be made: no province named (the ones the ally holds
  listed), unknown, not our home soil, already ours, not held by that court,
  not an ally (the state named), the holder's own live war purpose on it, no
  DP; `treaty.ask_return_score` is the ONE answer, the acceptance formula for
  a return (the relation between the courts, +25 fighting beside us against a
  common enemy, −income // 10 and −20 more for a capital, +15 when the ally
  took it from OUR enemy — the liberator's road, −40 when it took it from us;
  granted at 40). `diplomacy.ask_return_province` is the act: a delivered
  ask costs 1 DP whatever the answer (the player's pool; an AI court's
  `nation_dp` when it holds any — the sponsor rung's rule); a grant moves
  the province exactly as a treaty cession does (controller, stability 50,
  the title record — popped, a home province being title by construction);
  ONE log type `province_returned` with its `outcome`, the dispatch beat on a
  grant. Read by the chip under the ally's card (`_ask_return_actions`, one
  per home province the ally holds, `region` on the row, the likelihood from
  the formula), the typed road (`diplomatic_ask_return` — the ask-verb
  regex `_asks_a_province_back`, read before the mission and proposal arms
  that swallowed it; the province resolved from the raw text by the longest
  region name) and the AI's own tick (`ai_diplomacy.process_province_returns`,
  GR5: a court asks its ally only when the formula says the ally would
  grant — boot-dormant, pinned; the series unmoved).
- **`bid for <court>` (SFR-D40).** `ai_diplomacy.allegiance_bid_refusal` is
  the ONE gate (no auction open — the court named and the ones in play
  listed; at war with it; no sum; the chest; the DP), `place_allegiance_bid`
  the act: the gold moves to the minor's chest at once (a gift, not a bond),
  the bid is recorded on the auction (`bids[suitor]`, cumulative, in the
  save — `SAVE_FORMAT_REFERENCE.md`) and weighed at the resolution as
  `gold // AUCTION_SPONSORSHIP_LEAN_DIVISOR` beside relations and standing
  patronage (100 gold = ten turns of a 10 g/turn subsidy); a bidder is a
  suitor by that act. The typed road (`diplomatic_bid`, `_bids_for_a_court`;
  the sum from the raw text, `DEFAULT_ALLEGIANCE_BID` 100 when none), the
  chip on the court's card (`_bid_actions`, shown only while the auction is
  open) and the chip on the auction's own notice (`action_command` on the
  flip announcement — the dotation / recall idiom); the Admiralty-style
  ledger line names our standing bid. No AI court bids in v1 (its standing
  patronage is its bid, §12.6) — the function is theirs to call.
- **The truce's followers (SFR-D28's announce half).** `get_peace_commitment_
  conflicts(…, truce=True)`: for an ARMISTICE the paradox arm is not a stop
  (the send road exempts a truce) but the truce's own WARNING — `war_runs_on`,
  "Bavaria stays at war with Austria under this truce — an ally, not a
  client: her war runs on, and 3 French corps stand on Bavarian soil under
  the truce" (`allies_whose_war_runs_on`: the speaker's allies, never its
  clients, still at war with the counterpart or its clients; our corps on
  that ally's soil counted) — read by the armistice's confirm and the
  incoming letter through `build_war_context_snapshot`; the clients the truce
  BINDS stay on the SR-1b clients line beside it. The dispatch's
  `armistice_ratified` carries `{followers}` = `diplomacy.truce_followers_line`
  (both halves) from the ratifier's one producer.
- **The recipe, walked:** `VALID_ACTIONS` + the no-marshal list + the
  `DIPLOMATIC_ACTION_ALLOWLIST`, the parser's list, `_action_costs` (0 AP),
  the executor's free-action list and dispatch tuple, the delegated-method
  set, the three display maps, the prompt builder's diplomatic types,
  `CAMPAIGN_LOG_TYPES` 173 → 175 (`allegiance_bid`, `province_returned`,
  flipped consciously; the category, the routine tier, the court-to-court
  visibility arm, the one-liners), the dispatch's template / row / priority,
  the transit-gated sets (both verbs dispatch through `_execute_diplomatic`'s
  gate; the FA-N81 echo table taught the ask arm's `ask_region` var), the
  CN-4 census taught the same var.
- **Found building, kept:** a French corps already stands on Bavarian soil
  at boot, so the followers line counts three with Ney and Lannes marched in
  (the pins count, never hard-code); the notification collector's reader is
  `to_list`, not `get_all`. **The hook's first run failed 41:** four more
  `len(CAMPAIGN_LOG_TYPES) == 173` pins (flipped to 175 with the note), the
  meta-executor's twin `free_actions` list, the IQ-1 chest census (the bid
  now calls `record_gold_spent`), the AAR-15 truce pin's exact
  `template_vars` (the `followers` key popped before the compare), and the
  seventeen parser cassettes — the parse prompt renders its action list
  from `VALID_ACTIONS`, so the two new actions moved every prompt's hash;
  the fingerprints were re-stamped keylessly (the L-1 / RF-1 idiom:
  `request.prompt_sha256` / `prompt_chars`, the manifest, the re-stamp
  record; the responses untouched) and the prompt builder's own text was
  left as it was (the fast parser routes both verbs above the LLM gate).
- **Gate:** the new pins 37; `test_campaign_log`, `test_ai_intent_participation`,
  `test_cx_r1…` (the routed words), `test_dd1_s7_can_sign`, the serialization
  pin, `test_sr2a…`, the FA-N81 transit pins, the CR-1 corpus gate (685
  rows), the ratchet (`LEVERS_CAP` 429), the CN-4 chip census (31), the DD-1
  instrument pins (sweep / fuzzer / shuffle, 83 with the one-exit and
  retire-tool pins), `test_ai_intent_threat_migration` + `_variance` +
  `_assurance` (121 — `BASELINE_SERIES` byte-identical); `ruff` clean; the
  full suite on the hook.
- **Next:** S7b — CODE-3 + DD-C (`CODE_HEALTH_PLAN.md` §CODE-3; §3 DD-C),
  CODE-1 batch 5 at its head (the 116 levers in the `game_logic` modules
  over 3,000 lines).

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
- **✅ Run October 14, 2026 (S13) — NOT met; filed and homed.** 69 causes in 60
  turns (11.5 per 10 turns; P1 3 · P2 21 · P3 45); 62 rows to S13b, 9 design
  questions to `DESIGN_REFINEMENT.md` §DD-B for the user at S15. The write-up is
  `docs/audits/DD_B_FRESH_EYES_2026_10_14.md`.

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

#### DD-C landing record — nothing fails silently: the save path (October 12, 2026)

*Pre-Deploy S7b, the session's second commit (after CODE-1 batch 5 at its
head); CODE-3 slice 1 lands beside it (`CODE_HEALTH_PLAN.md` §CODE-3, part
1). Rules `SYSTEMS_REFERENCE.md` §110; pins
`tests/test_dd_c_nothing_fails_silently.py` (33).*

- **What was still silent, measured on `91c85e43`** (FA-S15-2 had already put
  the AUTOSAVE's failure on the rail): a manual save's and a load's failure
  reached the player as the raw OS error — filesystem path included — and
  reached no log at all; a corrupt save **vanished from the Load menu without
  a word**, so Continue silently resumed whatever older save came next; a
  failed **Final save** said nothing on either of its roads, and
  `write_final_save` could raise before its own `try`; `list_saves`' `except
  (json.JSONDecodeError, Exception)` swallowed as broadly as any bare handler
  and the census could not see it (a tuple); the client printed "Save failed:
  Save failed: [Errno 28] …".
- **The reading of "the save path raises `SaveError`"** (a deviation from the
  plan's words, recorded): the STAGES raise a typed
  `save_manager.SaveError(message, kind, site, reason, detail)` — the folder,
  the world's own `to_dict` (FA-S15-1's `delattr` failed there), the write,
  the read, the parse, the version, the rebuild — and the DOORS (`save_game`,
  `load_game`, `autosave`, `write_final_save`, `delete_save`, `list_saves`)
  convert it: `report(err, err.site, every=True)` and the sentence. The doors
  keep FA-S15-2's contract and ruling — none raises, a save never aborts the
  turn — because `executor.py`'s typed `save <name>`, the routes and the
  fixture tools consume the dict, and a raising door is the one-of-several
  shape FA-S15-2 refused. One conversion per door; no caller remembers anything.
- **The sentences** (a filename at most, never a path; every pinned fragment
  kept): "Save failed — the disk is full. Free some space and save again." /
  "…the saves folder cannot be written to (permission denied)." / "…part of
  the campaign could not be written down. This is a bug; the server log names
  the part." / "Load failed — the save file is corrupt and cannot be read; it
  may have been cut short while it was written." / "…save file not found:
  x.json" / "…the campaign in this save could not be rebuilt (KeyError). This
  is a bug; the server log has the details. Your current campaign is
  untouched." The log names the first value JSON cannot write by its path
  (`world_state.marshals.Ney.original_nation (object)`). The write keeps
  `json.dump` streaming into the temp file (FA-S15-2's forcing shim fails the
  save there), and a failed write removes the half-written temp file and
  leaves the previous save whole.
- **The surfaces.** The autosave's rail row (still its one producer, now
  behind `save_manager._announce_failure`) carries the reason sentence in
  `details.detail` instead of the OS text; a failed Final save raises its own
  title ("The campaign's Final save could not be written") on both roads;
  `GET /saves` carries `damaged: [{filename, saved_at, message}]` beside
  `saves` (no `success` key — the clients gate on shape; `list_saves()` keeps
  its contract); `load_dialog.gd` lists the damaged files disabled with the
  reason; Continue in `main.gd` resumes the newest READABLE save and names any
  newer file it could not read; `_failure_line` prints the backend's sentence
  once (the prefix only where a route's own refusal lacks it).
  `load_dialog.gd` joined the parse harness and its stale-guard list; the
  harness reads 67 scripts, 0 failures.
- **The routes** (`main.py`, CODE-3 item 4): the 14 crash handlers report at
  WARNING with their site (`every=True`) and carry `debug_error {class, site}`
  under `DEBUG_MODE` only; their `traceback.print_exc()` STAYS — the score
  instrument's `ai_aliveness.F2` reads "Traceback" in an arm's log as a crash,
  and a route that fails is one (the design review's catch). The five silent
  preview / ledger routes speak the same way. `main.py` reads 0 silent.
- **The instrument:** `tools/save_faults.py`, driven by the driver's new
  `--save-faults` at FA-102's turn boundary (in-process only; `getattr`, the
  hand-built `Namespace`s; in `meta.json` only when on): one fault a turn,
  rotating a full disk (the write raises `OSError(ENOSPC)` after a partial
  write), a non-JSON value planted in a serialized Marshal field alternating
  with FA-S15-1's own `delattr`, and a save cut to half its bytes; each probe
  checks the sentence reached the player (the `/save` / `/load` reply, the
  rail row, the `/saves` damaged list), a WARNING named the stage's site (and
  the planted field's path), the world was untouched (measured around direct
  `save_manager` calls — the HTTP envelope mutates the world on its own), the
  next clean autosave recovered and retired the row, and the round trip
  `to_dict(from_dict(x)) == x` held on the file it wrote.
- **The reading** (`commanded_full40.json`, 40 turns, 32 s): **40 of 40
  faults reached the player and the log** — disk full 14, unserializable 13
  (planted 7, `delattr` 6), truncated 13; **40 of 40 round trips equal**; the
  world untouched every time. **The instrument is transparent:** the probed
  run's digest equals the plain run's line for line. *Found reaching that:*
  the round trip's scratch world passes `WorldState.__init__`, which empties
  Berthier's display-only line rotation (IQ-8 item 8's chokepoint for "a
  campaign begins") — twelve battle lines took other words, casualties
  identical; the instrument restores the counter around its check. (The
  default driver policy's passive France falls at turn 34 — The Eclipse — so
  the forty-turn reading rides the commanded script.)
- **The design review** (a read-only Plan agent before slice 1) is folded in
  throughout: the `report` binding in five modules (`turn_manager` keeps a
  local `report = []` beside a silent handler — the conversion uses an
  `_errors` alias there), the F2 "Traceback" gate, the tuple handler, the
  identifier-only site hints, `debug_error` read from main's own
  `DEBUG_MODE` (the dev `.env` sets it, conftest does not pin it), the Final
  save, and the envelope's pollution of a diff taken across a route.
- **Retired with the rewrite:** FA-S15-2's two levers
  (`SAVE_DIR_FAILURE_IS_CAUGHT`, `SAVE_FAILURE_IS_ANNOUNCED`, Sept 6) and
  their two lever-down tests; L1's live half is re-pinned
  (`test_save_game_never_raises_on_a_directory_failure`).
- **Found by the hook, not by the slice's own family run** (the first commit
  attempt aborted on three): two FA-16c source pins read the load's
  "Clear transient per-turn data" block through
  `inspect.getsource(load_game)` — the block moved into `_rebuild_world` with
  the rebuild stage, so both re-seat onto that stage, their intent unchanged;
  and EP-F2's plural-hedge census caught the Continue line's "file(s)" (now
  `Utils.plural` with its verb agreeing).
- **Gate:** the DD-C pins 33, FA-S15-2 + `test_save_load` + the endpoint,
  restart, tutorial, menu, GE-1 and health-check families (383 together);
  `BASELINE_SERIES` + M1–M7 byte-identical with no re-record, the CR-1 corpus
  harness, the driver's own pins (1,224 together); `ruff` clean; the Godot
  parse harness 0 failures; the full suite on the hook.
- **Done-when:** every injected fault reaches the player as a sentence on the
  rail or the save dialog and the log at WARNING with the site — **MET** (40
  of 40); 0 silent handlers in `save_manager.py` and `main.py` — **MET**;
  `world_state.py`'s — **MET** by CODE-3's conversion, the session's third
  commit (`CODE_HEALTH_PLAN.md` §CODE-3 part 2: silent 367 → 6, the residue
  the console tee and the reporter's guard). **DD-C DONE.**

## 4. What is deliberately NOT in this plan

- **No balance or mechanics change** — except where a row names one: since
  October 14, 2026 the DD-B rulings (S13b), SFR-B3 (S14), VP-1 (S14b), the
  events (S14c) and DW-2 (DDB-X5). Each re-pins any series it moves with its
  row named; a code-health slice that moves `BASELINE_SERIES` is still a bug in
  the slice.
- **No new UI surfaces** — except where a row names one: the first-run sizing
  card, and since October 14, 2026 the event letter (S14c, on the existing
  mailbox transport), VP-1's designs (S14b, on existing screens) and the
  School's second lesson (S14d, the existing lesson frame).
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
