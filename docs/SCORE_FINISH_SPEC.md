# THE SCORE FINISH — every open defect, every pillar, then an honest re-score (row SF)

> **Status: DRAFTED September 28, 2026, by the user's direction. THIS SPEC ROUTES THE REST OF ROW SR (the Score Mandate).**
> The user: *"lay out plan to hit all defects, these pillars … then a rescore at the end with improved methods … create this spec and make status reflect plan and steps."*
> - `docs/SCORE_MANDATE_PLAN.md` keeps:
>   - its landing records (§2 Chunks 1–5, §5);
>   - its three design gates (§4);
>   - the chunk content this spec absorbs by name (Chunks 6–9, 3b).
>
>   This spec supersedes three parts of it:
>   - its §1 scoreboard, replaced by the instrument in §4;
>   - its §5 measurement rule, replaced by §5;
>   - its Chunk 6 bullets. Six of the seven had already landed in Chunks 1–2; Step 2 rebuilds the chunk.
> - **Nothing in this spec is built yet.** Every slice lands under the house rules: its pins, a mutation sweep, `BASELINE_SERIES` + M1–M7 byte-identical or flip-attributed, and the four files.
> - **Evidence, all taken on September 28, 2026 at `c20d5bba`:**
>   - the ledger census `tools/defect_census.py` (new, read-only);
>   - six read-only agents, which re-verified every open row, read each pillar's review history and designed the scoring method;
>   - one reproduction by hand (SF-V4).
>
> **Three of §6's questions were RULED the same day** under the user's delegation, each after research:
> - RS-D1: recognition by defeat, anchored to the capital (§6.1);
> - SR-G7 / PB-D1: "The Armed Peace" (§6.2);
> - SF-V4: a proper name asks (§6.3).
>
> **Step 7b, "The front page of the peace", was added the same day at the user's direction** (*"one more way to increase score … on the end before rescore"*). It is the last build step before the re-score.
>
> **Reading map:** §0 why · §1 the census · §2 the pillars · §3 the build order · §4 the scoring method · §5 cadence · §6 the user's rulings (§6.1–§6.3 the gate records) · §7 done when · §8 what this supersedes · Appendix A the checklist (v1, draft).

---

## §0 Why this exists

The September 28 retest (`docs/audits/PLAYTEST_FULL_RESCORE_2026_09_28.md`) moved four pillars and held ten. Read row by row:

- **Six of the ten belong to chunks that had not started:** narration, AI aliveness, living balance, vassals, agendas and UI/UX. Two of those cannot move in a wire-only retest at all:
  - UI/UX: the client was not opened;
  - agendas: carried at 8.5 since July 25 and never exercised since.
- **Diplomacy had already risen**, at its own exit (6.0 → 6.75).
- **Three were worked on and still held:** command & parsing (Chunk 3), combat legibility and marshal drama (Chunk 4).
  - The retest credited the Chunk 4 work by name, then docked fresh rows (RS-3, RS-5, RS-12, RS-13, RS-24, RS-26).
  - About three quarters of the retest's 29 rows predate the mandate.
  - The work had been fixed to the row and measured on the row; the retest met each class one step over.
- **The measurement cannot resolve anything smaller than half a point:**
  - One scorer produced the score, starting from the old number.
  - Pillars swing ±0.5 between reviews when nothing relevant changed. Naval went 7.0 → 6.5 right after two naval UI improvements; combat legibility went 7.0 → 7.5 → 7.0 over September 12, 23 and 25. A chunk's target is +0.5.
  - Every session plays further than the last (7 → 18 → 28 hand-played turns), so it reaches older defects. Findings per hand-played turn fell 3.7 → 2.2 → 1.1, and the score could not see it.
  - Two deductions stand for behaviour the user ruled intended: the long-peace hoard (SRX-D1), and the unattended France losing.
  - The fourteen targets sum to exactly 7.5 × 14. The directional therefore reaches 7.5 only if every pillar hits its target.
- **The pillars that moved had something countable:**
  - the ending: titled provinces, 39 → 47 of 45;
  - first contact: a fixed arm of 28 questions, shrugs 11 → 0;
  - economy: the turn the Staff was bought.

So this spec does three things, in this order:
1. Count every open defect, and give each one a slice (§1, §3).
2. Give each pillar the lift its evidence names (§2). For the three that held despite the work, that means a capability a player can feel, not only rows.
3. Measure with a fixed instrument, read twice: a baseline on today's tree and a final reading on the finished one (§4, §5). The difference then belongs to the build, not to the reviewer. Between the two readings, progress shows session by session as checklist items that flip.

---

## §1 The census — every open row

### §1.1 The tool

`tools/defect_census.py` reads every row id in `docs/BUG_FIXES.md` and `docs/DESIGN_REFINEMENT.md` and classifies it by the ledgers' own marks:
- a struck or ticked id;
- an upper-case status word;
- a section heading that closes the whole section;
- a table of fixes applied.

Its options:
- `--open` lists the open rows by section. It marks with `*` the rows whose id shares a line with a closing word elsewhere under `docs/`, which are the likeliest to be stale.
- `--json PATH` writes every row.

It is a reading aid with a stated rule, not a proof; that is why every row it counts was verified by hand below. Run:
```
.venv/Scripts/python.exe tools/defect_census.py --open
```

### §1.2 The count at `c20d5bba`, verified

| | The census reads open | Verified open | Partial | Stale (fixed, never struck) | Not a defect / duplicate / owned elsewhere |
|---|---|---|---|---|---|
| **Defect rows** (`BUG_FIXES.md`) | 126 | 86 | 8 | 29 | 3 |
| **Design rows** (`DESIGN_REFINEMENT.md`) | 75 | 13 in scope · 11 user gates | — | 45 | 6 owned elsewhere |

That 126 was counted before this spec filed its four rows. After filing, the census reads 130.

Five live rows are not in the 126:
- NPC-12's open remainder. Its row reads closed for the half that landed; RS-26 owns the rest.
- The four rows filed with this spec (§1.4).

**Live defect work: 86 open + 8 partial + NPC-12 + 4 new = 99 rows.** §3 gives every one a slice.

**The check SF-0 must pass:** after SF-0 strikes the 29 stale rows and the 3 non-defects, and marks NPC-12 open, the census reads 99 open (130 − 32 + 1).

### §1.3 What SF-0 marks (each with its evidence)

**Defect rows fixed but never struck (29):**
- GEV-5, GEV-6: the "GE-V §4 nits", taken by Chunk 1's reserve on September 26 (`test_sr1_quick_wins.py`).
- CX3-CLAIM: CX-7.
- The PC15 fix slice (August 15): PC15-1, PC15-2, PC15-3, PC15-4, PC15-6, PC15-7, PC15-9, PC15-11, PC15-12, PC15-14, PC15-17, PC15-H.
- PC15-5 and PC15-15: the PC15-D rulings, built.
- PC15-10: the petition revisit, B0–B5, accepted September 27.
- EAS-4: the escapable seed pin, fixed August 4.
- S5-1, S5-2, S5-3, S5-5: Batch Q, July 16.
- XR-2: the PF-2 aliases. XR-4: EB-3.
- CX5-L5-N1, CXR1-N1, L2-N1: pointers to CQ-32, CQ-35 and CQ-34, all fixed by CRT-1.
- L2-3: CX-R1, plus CX-7's ruling.

**Not defects (3):**
- CA9-P2 and CA9-P3: notes, not rows.
- CX5-L5-N3: a pointer to CQ-33, which stays open.

**Design rows closed but never marked (45):**
- SR-D1, SR-D3, SR-5c, SR-M.
- AAR-D6, LV-D5, FA-N63.
- UX23-D1, UX23-D2, UX23-D3, UX23-D4: EP F4.
- WO-D1, WO-D2, WO-D3, WO-D5, WO-D15.
- WIN-D1, WIN-D4, WIN-D6, WIN-D7.
- PC15-D1, PC15-D2, PC15-D3, PC15-D4.
- CA9-D1, CA9-D2.
- CA8-D1, CA8-D5: the Econ Balance gate.
- VP-D2, VP-D4.
- W6-ADD-1, W6-ADD-2.
- EXP-N1, EXP-M1, EXP-C1, EXP-E1, EXP-M2, EXP-D1, and E-CA-1 … E-CA-6: Wave 6.
- IQ7-D2: declined.

**Design rows owned elsewhere (6):**
- WO-D4: the Victory & Objectives gate.
- HC-D1: ROADMAP 13.
- EWC-D2: the Pre-EA Balance Pass.
- S5-D3 and VP-D7: the refactoring batch.
- VP-D3: ROADMAP 16.

### §1.4 Filed with this spec (`BUG_FIXES.md` §Score Finish Verification)

- **SF-V1 (P2): an AI court offers a treaty its own ratification refuses.**
  - Sweden's defensive alliance was accepted and then refused 14 times, on five driver arms (the three commanded seeds, the spender, the volte arm).
  - The refusal prints the raw key: "Relations with France are insufficient for DEFENSIVE_ALLIANCE."
  - → Step 1.
- **SF-V2 (P3): the white-peace header reads "Will NOT carry" beside a live Ratify.** This is SR-2a's recorded residue SR-2a-X1, which never got a row. → SR-6b, with SRX-6.
- **SF-V3 (P3, instrument): the Chunk 5 laws arm no longer buys the Staff.**
  - Since SR-5a the treasury reaches 9,000 only at turn 8, and the script types the enactment once, at loop 6.
  - → SF-M.
- **SF-V4 (P2; ruled September 28, 2026 that the marshal asks — §6.3): an attack on a proper name the map does not know fights the nearest enemy.**
  - "Ney, attack Zorglub", "attack Alsace" and "attack Lombardy" each read "Your words named no foe our maps know, Sire — Ney marches on Mack at Swabia", then fight him. Reproduced by hand: Ney 24,000 → about 21,900.
  - An *address* to such a name spends nothing (CX-R1).
  - CX5-L5-F8 ruled the substitution designed for a descriptive phrase ("smash the retreating column"); a proper name was never ruled.
  - → leads CRT-10, with NPC-6 folded in (§6.3).
- **SF-V5 (P2; filed with Step 7b's research): a whole-war settlement letter that cannot be ratified keeps arriving.**
  - On the OP arm, Britain's whole-war letter is re-sent every three turns. While a coalition member is in armistice (Russia from turn 10, Austria from turn 13), accepting it stages a review with `can_ratify: False` ("no single dominant pressure… Vilna is unbeaten"), with Britain at 13/50 on its own letter.
  - The only live road, "Make peace with Britain only", opens a proposal whose Send is disabled while Spain, our ally, still fights Britain.
  - The letter is part of the stack of 4–5 blocking modals on turns 10, 13 and 16 (UI/UX C4).
  - It is SF-V1's class, applied to settlement letters: an offer the game's own ratification refuses.
  - Measured by the gap analysis on a replay of the OP arm; the builder reproduces it at the wire first.
  - → Step 1, as SF-V1's sibling.

### §1.5 Owners that did not hold

The verification found rows homed to slices that then landed without them. This is why the census is read at every exit (§5).

- **Rows whose slice landed without them:**
  - NP-X1, NP-X8, NP-X9, NP-X10 → SR-3b.
  - NPC-6, NPC-9, NPC-10, NPC-11, NPC-13, NPC-17, NPC-18, NPC-21, NPC-25, NPC-26 → SR-2a, SR-3a, SR-3b, SR-4a and SR-2e. NPC-9 was never homed at all.
  - VP-R1-X1 → CRT-7.
  - CQ-22 → the AI drill fix, which rewrote its seam and kept the asymmetry.
- **Rows homed to an owner that had already landed:** NP-X5, NP-X6, NP-X7 → DEF-1, which landed a month before they were filed.
- **Rows homed to an owner that was never a slice:**
  - CQ-22 and IQ5-R1 → "the next combat-mechanics row".
  - CX3-R2 … CX3-R12 → "the next UI slice".

---

## §2 The pillars

The Sept 28 column is the retest's impression score. **The Baseline column is the instrument's reading on `c20d5bba` (Step 0, September 29, 2026 — directional 6.71 over 13 exercised pillars; the archive is `docs/audits/score_runs/2026_09_29_c20d5bba/`).** As predicted, it re-based every row and several read **lower**:
- a verified open P1 caps its pillar, which today hits the ending and diplomacy;
- most of living balance's ceilings are unmet.

That is the new ruler, not a regression. Targets are stated as ceiling counts (§4.4).

| Pillar | Sept 28 | **Baseline (Sept 29)** | Target | Still docked (open rows) | The lift (§3) | Could fall if |
|---|---|---|---|---|---|---|
| **The ending** | 6.75 | **5.00 (RS-2 caps it)** | 7.0 (3 ceilings) | RS-2 (P1), RS-D1, RS-10, RS-16 | Step 1, "The peace holds", with RS-D1 as ruled (the capital latch, §6.1) and SF-END-1 as its exit (the sitting played to its end from the turn-24 save) | The price rider makes the decisive-campaign peace unreachable (then the latch ships alone), or "contested but counted" softens the finish too far |
| **Diplomacy** | 6.75 | **5.75 (RS-1 caps it)** | 7.0 (3) | RS-1 (P1), SF-V1, RS-7, RS-9, RS-18 … RS-22, CQ-36, CX-X3, NPC-21 | Step 1 (RS-1, SF-V1); Step 2 (SF-DIP-1 "the dial survives the drop"; SR-6b copy); Step 4 (CRT-8) | RS-1's fix changes alliance calls (one series re-record) |
| **First contact** | 7.0 | **7.00–7.50** | 7.5 (4) | RS-12, RS-14, RS-15, SRX-5, RS-6, RS-7, CX3-X2, CX3-X3, CX-BEHAV-1 | Step 2 (RS-14, SRX-5); Step 4 (CRT-9 with RS-12/RS-15; SF-CMD-1's first hour); Step 7 (the first ten minutes in the client) | The sourced lines are saturated, so a scorer's own phrasing decides (the HOLD arm, §4.2) |
| **Economy** | 6.75 | **7.00** | 7.0 (3) | RS-D3 (evidence for SR-G7) | Step 3 (SR-G7 gives the chest a war to fund); Step 7b (the keep-out prices give the chest its peacetime use); Step 6 (SF-ECON-1, only if economy C6 still fails after Step 7b) | A new sink re-opens SR-5a's balance |
| **Naval** | 6.75 | **7.00–8.00** | 7.0 (3) | RS-25; SHUT OUT has never held on a played board | Step 6 (SF-NAV-1 "the strangulation, played") | Britain sues from its own war exhaustion before the System bites (6 of 6 arms) |
| **Living balance** | 6.5 | **6.50** | 7.0 (3) | SR-G7 / PB-D1 (the long peace); 0 AI-vs-AI wars; RS-3, RS-27, CQ-22, IQ5-R1, XR-3 | Step 3: SR-G7 "The Armed Peace" as ruled (§6.2) → SF-LB-1 "Europe's own quarrels"; Step 7b makes the league visible and playable-against | The league the fuse brings breaks F1 (France below 20 provinces at turn 40): lengthen the fuse, never lower the watch. A shorter fuse would re-open IQ-3's revolving door |
| **Combat legibility** | 7.0 | **5.50–5.75** | 7.5 (4) | RS-3, RS-4, RS-12, RS-13, RS-26, NPC-13, NPC-17, NPC-25, AAR-5, AAR4-X2, AAR24-X4 | Step 3 (RS-3); Step 2 (RS-13, the AAR rows); Step 4 (SF-CL-1 "the forecast keeps its word") | SR-7d moves the arrival odds (the threshold exists in three copies) |
| **Marshal drama** | 7.0 | **7.00–8.00** | 7.5 (4) | RS-5 + VP-R1-X1, RS-24, NPC-11, CQ-38 | Step 2 (RS-5 + VP-R1-X1; SF-MD-1 "every man his own voice"); Step 7 (B1's audiences on screen) | Floors that bind 0 times, and audiences nobody opens, make the game quiet |
| **Vassals** | 7.0 | **7.00–7.50** | 7.5 (4) | IQ7-D1 (VD-C), IQ7-D3, IQ7-X1, IQ7-X3, CX-X3, VP-D9, IQ7-D4 | Step 5 (SR-8a VD-C, SR-8c) | VD-C touches marshal strength at four exits |
| **UI/UX** | 7.0 (carried) | **NOT EXERCISED (no Godot on the reading machine)** | 7.5 (4) | S5-4, WO-V-D1, WO-V-D2, WO-D14, CX3-R2 … CX3-R12 (8), EAS-2, SRX-6 / SF-V2, the owed sign-offs | Step 7: Chunk 9 as a driven client pass, plus the user's eyes | Skipped again: the pillar is NOT EXERCISED and the directional cannot count it |
| **Command & parsing** | 7.5 | **7.00–7.50** | 8.0 (5) | RS-6, RS-7, RS-8, RS-11; CQ-8, CQ-21, CQ-24, CQ-28, CQ-33, CQ-38; CRT-6's CX5-L5 rows; NP-X1, NP-X8, NP-X9, NP-X10; NPC-6, NPC-9, NPC-10, NPC-18, NPC-26; PC15-13; SF-V4 | Step 4: SF-CMD-1 "the unrehearsed line", then Chunk 3b trimmed to what it confirms | New verbs regress the negation and question guards |
| **Narration** | 7.5 | **7.00–8.00** | 8.0 (5) | RS-D2, RS-17, RS-23, RS-24, AAR-5, NPC-14, NPC-15, NPC-23, NPC-24, NPC-27, IQ6-D3, EAS-2 | Step 2 (SR-6a/6b/6c); **Step 7b: every morning has a front page, and the next coalition is its news** | Step 7b's quiet-turn lead reads as filler to the panel (prefer real rows; name only what changed) |
| **AI aliveness** | 7.5 | **8.50** | 8.0 (5) | AAR-D8 (the garrison grind, the dithering), RS-27 | Step 3 (SR-7a, SF-LB-1, SR-7d) | The Hofkriegsrat drops Austrian arrival odds sharply |
| **Agendas & formables** | 8.5 (carried since Jul 25) | **7.00–8.00** | 8.5 (6) | The Proclamation has never been seen from play; IQ7-D3; IQ6-D1 | Step 5 (SR-8b + SF-AGD-1: a carve to a Proclamation on a played road) | A July score on a build from before the mandate; one 0.5 fall here breaks the directional |

---

## §3 The build order

| Step | What | Sessions | Pillars |
|---|---|---|---|
| **0** | SF-0 the ledger tells the truth · SF-M the instrument + **the baseline reading** | ≈1.5 | measurement |
| — | The user's rulings (§6) — no build session | — | gate Steps 1, 3, 4 and 5 |
| **1** | "The peace holds": RS-1, RS-2, RS-D1 as ruled (the capital latch + the price rider), RS-10, RS-16, SF-V1; SF-END-1 as the exit | ≈1.8 | the ending, diplomacy |
| **2** | Berthier tells the truth: Chunk 6 rebuilt, plus the reserve, SF-MD-1 and SF-DIP-1 | ≈4.0 | narration, drama, combat legibility, diplomacy, first contact |
| **3** | Europe acts without France: Chunk 7 as one balance block, SR-7d last | ≈6.5 | living balance, AI aliveness, economy |
| **4** | The three misses, second pass: SF-CL-1, SF-CMD-1, then Chunk 3b trimmed to what the census confirms — ✅ **COMPLETE October 3, 2026** (the census-unconfirmed remainder, ≈1.5, homed to Step 7's SF-CMD-2) | ≈5.3 | combat legibility, command, first contact |
| **5** | The client stands: Chunk 8 + SF-AGD-1 | ≈2.0 | vassals, agendas |
| **6** | The chest and the sea: SF-NAV-1 (+ SF-ECON-1 only if needed) | ≈0.7 (+1.0) | naval, economy |
| **7** | What the wire says, the screen says: Chunk 9 + the user's eyes; **SF-CMD-2 "the census's remainder"** and **SF-DC-1 "Nothing unnamed"** (homed by Step 4's exit, October 3, 2026) | ≈2.0 + 1.5 + 1.0 | UI/UX (+ first contact, drama, command, living balance) |
| **7b** | **The front page of the peace** (added Sept 28, 2026, the last build step before the re-score): every morning has a front page (SF-NAR-1) + Europe arms in plain sight (SF-LB-3 — renamed October 4, 2026 from "SF-LB-2", which the landed "The Defenceless Prize" carries) | ≈2.5 | narration, economy, living balance, the ending |
| **8** | SF-R, the final reading | ≈1.0 | all |
| | **Total** | **≈28.5 (+1.0 if SF-ECON-1 is needed)** — SF-DC-1's ≈1.0 added at Step 4's exit; SF-CMD-2's ≈1.5 moved, not added | |

**Why the total is larger than the ≈12 sessions the mandate carried for Chunks 6–9 and 3b:**
- Chunk 6's written bullets had six of seven rows already landed, while its real load (the retest's copy rows and the NPC rows homed to it) is about four times its ≈1.0.
- The orphaned rows of §1.5 come back.
- The capability slices the three misses need are new.
- Step 7b (≈2.5) was added at the end by the user's direction. Without it, narration's floor fails on 58 of 120 turns and the pillar is capped at 6.0.

**Why this order:**
1. The P1s first (the mandate's §0-4).
2. Display-only work that touches seven pillars: cheap, no series moves, and the checklist shows it.
3. The weakest pillar's balance block.
4. The misses' second pass, after the resolver has changed.
5. Vassals and agendas.
6. The economy and naval close-outs.
7. The client, so its frames cover the surfaces Steps 1–6 touched.
7b. The front page of the peace, last of all, because it reads what Steps 1–3 build.
8. The reading.

The baseline is pinned to `c20d5bba`, so Steps 0 and 1 may swap if the user wants the P1s fixed first. The baseline then runs on a detached worktree.

### Step 0 — the ledger and the instrument (≈1.5)

**SF-0 "The ledger tells the truth" (≈0.3; docs and the census only).**
- Strike the 29 stale defect rows and mark the 45 design rows, each with its evidence (§1.3). Mark CA9-P2 and CA9-P3 as notes, and CX5-L5-N3 as CQ-33's pointer.
- Re-home every orphan named in §1.5 to its step here, and give NPC-12's row its open-remainder marker.
- Tag each live row with its pillar, and add `--by-pillar` to the census.
- Verify the retest's unfiled "COUNTER expected": the peace offer to Britain at 750 gold a turn plus an action a turn, turns 23–24. File it if it is a defect.
- Close the design rows §6-12 disposes.
- **Home three orphans that Step 7b's research found:**
  - ~~AI-V scene 1, the Confederation of the Rhine.~~ ✅ homed Sept 29 — the SR-8c bullet in Step 5 names it, and `AI_INTENT_SPEC.md` §7a's scene-1 row points there. It is unreachable because the German minors have no agenda deck (their intent reads "indifferent"), even though France's bloc share opens the bandwagon gate.
  - ~~NPC-D1, the Emperor's aura dimming unnarrated.~~ ✅ homed Sept 29 — SR-6a's bullet in Step 2 carries it with NPC-27; the row is tagged `⟨SF step=2 · SR-6a · pillar=narration⟩`.
  - ~~The census cannot count design rows written as `###` headings (NPC-D1 … D4).~~ ✅ converted Sept 29 — the four rows are a table in `DESIGN_REFINEMENT.md` §Napoleon Campaign (NPC-D1 + NPC-D4 OPEN and tagged; NPC-D2 + NPC-D3 disposed), and the census counts them.
- **Done when:** `defect_census.py --open` lists exactly §1's live rows (99, plus SF-V5, plus anything filed since), each with an owner in this spec.

**SF-M "The instrument" (≈1.2).** Build:
- `tools/score_run.py` (`run | check | packet | compare`).
- `docs/SCORE_CHECKLIST_V1.json`: Appendix A, frozen once the user confirms it.
- `tools/_score_probes.py`: the PROBE items.
- The new arms:
  - **DL**: the docked lines, which grow each review.
  - **HOLD**: 20 questions and 20 orders written blind each run.
  - **CONG**: the Congress sitting replayed from the turn-24 save.
- The laws arm fixed (SF-V3).
- Two IQ-10 shots: `proclamation_popup.tscn` and the wizard's formables step.
- Driver fields for the dispatch headline class and the marshal's voice line.

**Then the baseline reading, on `c20d5bba`.**
- The `rs0928-*` archives are reused where their `engine_revision` content hash matches; the first-contact arm re-ran byte-identical.
- Every new arm runs on `c20d5bba` itself, on a detached worktree if production code has moved.
- Output goes to `docs/audits/score_runs/<date>_c20d5bba/`.
- **Done when:**
  - every pillar reads a score, a range, or NOT EXERCISED, with its items;
  - the panel ran;
  - §2 gains a "Baseline" column.

**✅ STEP 0 LANDED September 29, 2026 — landing record** (authoritative for what was built; the reading itself is the memo `docs/audits/SCORE_BASELINE_2026_09_29.md` and the archive `docs/audits/score_runs/2026_09_29_c20d5bba/`; §6 row 2 was taken at its recommended default under the user's "proceed" — checklist v1 is frozen, the user may amend).

- **SF-0, the ledger.** The 29 stale defect rows are struck (`~~id~~` + an evidence note each), CA9-P2 / CA9-P3 / CX5-L5-N3 are disposed as notes, NPC-12 carries its **OPEN REMAINDER** marker (the census reads it `partial`), the 45 design rows are closed with evidence and 6 are **RE-HOMED** to the gate that owns them, §6-12's dispositions are on the rows (WO-D7 + EWC-D3 struck, WO-D8 + WO-D13 ruled, VP-D8 declined, IQ6-D2 tagged to Step 3's gate), the `###` NPC-D rows are a table the census counts, and **every live row carries `⟨SF step=N · slice · pillar=X⟩`** — `tools/defect_census.py --by-pillar` hands the P1s to the rule. The census at landing: **defect 102 OPEN + 1 partial, design 17 OPEN** (§1.2's 99 was the count before this reading filed SF-V6 … SF-V9 and closed SF-V3). Three rows are tagged `pillar=none` on purpose — RS-28 (test hygiene), NP-X5 (a mod example), NP-X7 (a docstring) — hygiene, not a pillar. The three orphans are homed (the struck bullets above). **The retest's "COUNTER expected" was verified NOT a defect:** Britain answers the 750-gold-a-turn peace with an 800-gold lump at ACCEPT 57 — a counter, as the diary expected, not a refusal — so nothing was filed.
- **SF-M, the instrument.** `tools/score_run.py` (`run | check | packet | compare`), `docs/SCORE_CHECKLIST_V1.json` (14 pillars × 8 = 112 items, 56 target ceilings), `tools/_score_probes.py` (30 PROBE readers, every one a read-only stage on a save or a fresh boot, sandboxed under the run's own save dir), the DL / HOLD / CONG arms (`tools/playtest_scripts/score_docked_lines.json`, `score_hold_2026_09_29.json` — 20 questions + 20 orders written blind by an agent that had not seen the corpus — and `score_congress_sitting.json` replaying the turn-24 save), the LAW arm fixed (SF-V3 → FIXED: `enact the Staff` at the head of every loop from 3; the arm enacts it on turn 7), the two IQ-10 shots registered (`proclamation_warsaw`, `wizard_formables_entry` in `tools/iq10_run_captures.py`; payloads captured by `cap_proclamation`, frames not shot — no Godot on this machine), and the driver fields (`headline_class` on the dispatch record, the marshal's `voice` on the battle record, `bill_notes` on the ledger record — each absent on a pre-SF-M archive by construction). Pins: `tests/test_score_finish_step0.py` (45); sweep `tools/_sweep_score_finish_step0.json` **16 of 16 killed, 0 INERT**. Every reader is deterministic across hash seeds (a set-ordered tie-break in narration C1 was found by re-running the check under a second `PYTHONHASHSEED` and fixed).
- **The baseline reading.** Every arm was played fresh on a detached worktree at `c20d5bba` (no `rs0928-*` archive was reused; all 29 digests carry the same `engine_revision.content_hash` `8f597da5…`; the worktree's only differences from `c20d5bba` were the instrument's own files (the driver's three fields, the laws-arm script, the new tools) — `git diff c20d5bba -- backend` is empty; each meta's `dirty: true` flags those instrument files, and the uniform content hash is over the backend, the map registry and the scenario JSON), plus SUITE (the seven named test files, 575 green), PEVAL (corpus 845/845, replay 6/6) and AIV (arm A byte-identical; arm C over 10 seeds). **Directional 6.71 over 13 of 14 pillars.** The ending 5.00 (RS-2 caps it, 0 of 6 ceilings) · diplomacy 5.75 (RS-1 caps it, 3 of 6) · first contact 7.00–7.50 · economy 7.00 · naval 7.00–8.00 · living balance 6.50 · combat legibility 5.50–5.75 (F1 fails: the FLD cannon-fire charge line carries no losses) · marshal drama 7.00–8.00 · vassals 7.00–7.50 · **UI/UX NOT EXERCISED** (no Godot) · command 7.00–7.50 · narration 7.00–8.00 · AI aliveness 8.50 · agendas 7.00–8.00. A range is a pillar with 6–7 items measured; the directional takes the low end. The panel: three blind scorers; the median left the anchor on Naval (7.00 → 7.25), Living balance (6.50 → 6.25), Combat legibility (5.50 → 5.75), Narration (7.00 → 6.75); spread 0.00–0.25 (`panel.json`).
- **Corrections to this spec's own claims, found by the reading.** (1) §4.6's TILSIT probe lives in `tools/_score_probes.py` (`agendas_c4_tilsit`), not a `_score_formables_probe.py`, and "58 against 50" did not reproduce: on the beaten board (`_beaten_prussia`) the bare carve reads **COUNTER_OFFER at 30** and **ACCEPT at 90 with a 6,000-gold sweetener**; a counter is not a signature (IGR-D: the counter drops the client), so the item passes on the sweetened arm and the card raises. (2) The descent arm's precondition is stale since SR-5a (the commission is refused for gold) — **SF-V6**, Step 6. (3) The LAWS forecast under-quotes the Charges of Empire by one tick (463 / 557 …) — **SF-V7**, Step 6. (3b) Two of the panel's flags verified on the digests and filed: **SF-V8** (the landing verb answers for Lannes when Oudinot was named — CRT-2's naval twin, Step 4) and **SF-V9** (the HOLD arm's 12 order misses + 16 shrugs as SF-CMD-1's worklist, Step 4). (4) `typed_road.json`'s "question turns spend 0 actions" is measured by the game's own rule — an ADDRESSED line ending in "?" keeps its order by `clause_guards`' design — so a question turn that carried an order is not a miss (command C5 reads that rule; nothing filed).
- **Not done, and why.** UI/UX is NOT EXERCISED and command C6 (the live parser) is unmeasured: neither a Godot binary nor an API key exists on the reading machine; both run on the user's PC (`--godot`, `ANTHROPIC_API_KEY`). The EYES items carry no marks (`--eyes` takes the user's). The panel's agents necessarily carry the project's `CLAUDE.md` in their system context, which quotes the old impression scores; they were told to disregard it, the anchor is the rule's and the adjustment is bounded to ±0.25 — recorded as the panel's one known leak.

### Step 1 — "The peace holds" (≈1.8; RS-D1 is ruled — §6.1)

| Row | Sev | Fix shape |
|---|---|---|
| RS-1 | P1 | The offensive cascade keeps a fresh peace. A court with a fresh peace or a pair cooldown is not called (`hard_illegal`, "fresh peace with X", no penalty), and the settlement writes the pair cooldown. Lever `THE_CASCADE_KEEPS_A_FRESH_PEACE`, series attributed. Also closes PC15-15's recorded residual (`settlement_third_party.py`). |
| RS-2 | P1 | While the Congress sits, a war France neither declared nor joined marks a refusing ceder's titles CONTESTED but still counted. The break applies when that war ends, and the sue peace re-titles and latches recognition. Lever `A_CONGRESS_WAR_CONTESTS_NOT_BREAKS`. |
| RS-D1 | ruled | §6.1: a signed peace that leaves a great power's capital held by France or her vassal chain latches its recognition (`kind: "capital"`; it breaks when the capital leaves the bloc). The price rider makes the scorer read a retained capital as lost; the latch and the rider each sit behind their own lever, and the rider is measured on the turn-16 shape. Every courtship lever quotes its cost in turns. With it, the RS-1 rider: the cascade reads `spared_from_coalition` while the Congress sits. |
| RS-10 | P2 | Before the summons, the Congress says that the gate drops to 40 and which courts go to war (it reads the brewing league). |
| RS-16 | P3 | The alarm line is built from one forecast of the tick's gains and its decay. |
| SF-V1 | P2 | The AI proposal producer skips a treaty whose relation floor the pair does not meet (the ratifier's own predicate), and the refusal names the treaty. |
| SF-V5 | P2 | An AI court never sends a whole-war letter its own ratification refuses. The letter covers only the pairs actually at war, carries the offering courts' consent (SR-2a's consent trio), and its re-sends honour the letter lifetime. **Pin:** UI/UX C4 (at most 3 blocking modals per end turn on OP). Reproduce at the wire first. |
| **Exit: SF-END-1 "The Imperial Peace, played" (0.4)** | — | Replay `docs/audits/playtest_digests/rs0928-hand-played/retest_t24_summonable.json` by hand through the fixed sitting, to a peace or an honest dissolution. Archive it as the ending's evidence. |

**✅ STEP 1 LANDED September 29, 2026 — landing record** (authoritative for what was built; rules `SYSTEMS_REFERENCE.md` §81; RS-D1's gate record is §6.1 below; the exit's evidence is `docs/audits/playtest_digests/sfend1-the-peace-holds/`; pins `tests/test_step1_the_peace_holds.py` (64) + `tests/test_rs_d1_recognition_by_defeat.py` (31); sweep `tools/_sweep_step1.json` 68 of 68 killed on the pre-exit tree, then the 8 rows the exit's fixes added or re-anchored 8 of 8 killed — 0 INERT, 0 BROKEN (`tools/_sweep_step1.json`, 72 rows); attribution `tools/_step1_series_arms.py` → `tools/_step1_series_arms.json`). Every row was reproduced at its seam before a line was written (RS-2 on the turn-24 save in memory; RS-1 with the boot's three-court peace and `declare_war(Austria, France)`; SF-V1's auction letter at −60; SF-V5 on the OP arm's turn-10 save, where Russia's truce hard-stopped the review with `no_direct_war_score_for_covered_enemy`). Every fix sits behind its own lever; every lever DOWN reproduces the pre-Step-1 behaviour byte-for-byte.

- **RS-1 "The offensive cascade keeps a fresh peace."** ONE predicate `diplomacy.offensive_call_bar` — the fresh-peace floor (PR-1's own), the pair cooldown, and (RS-D1's rider) a court answering the sitting Congress — read at the cascade BEFORE either road (`hard_illegal`, the reason, no penalty) and at `preview_war_declaration` (`offensive_barred`), never in the resolver (one seam). The settlement writes the pair cooldown (`write_settlement_peace_floors`, `FRESH_PEACE_FLOOR_TURNS`) at the end of `_resolve_pair_state_transitions` — **the ONE helper both the player's table and the AI-AI third-party road call, so both inherit it (GR5)**; a truce's popped cooldown is replaced by the peace floor (the C2 armistice pin re-seated consciously). The defensive arm is untouched by design and pinned. PC15-15's KNOWN GAP at `settlement_third_party.PAIR_EXIT_TRUCE_FLOOR_TURNS` is closed. Measured: the retest shape keeps Britain and Russia at PEACE through Austria's declaration; `form_coalition` at T+1 keeps Britain's peace (lever down: WAR).
- **RS-2 "A Congress war contests, not breaks."** While the Congress sits, a WAR entry the Emperor neither declared nor joined (`game_end.player_drew_the_sword`, read off the setter's own argument order per reason) marks the player-house treaty titles CONTESTED — counted, named on the hold ("Austria's war contests what it ceded (Bohemia, Carniola, Moravia …) — counted while the Congress sits"), logged (`congress/contested`) and led (`congress_contested` at 87). The contest ends with the WAR: a signed road drops the mark and the retention pass re-signs (the court latches `table`); an unsigned end — a truce that ran out into peace, an elimination, a repudiation — applies the deferred break; a truce is NOT the war's end (WAR → ARMISTICE keeps the mark; the per-turn lapse reads a truce as the war still on — a hole the first cut had: the truce would have cleared the mark and re-signed the cessions for free); the sitting's end with the war still on lapses the shelter. A province actually LOST still breaks the hold. **Measured on the turn-24 save: 47 of 45 through the league's war** (was 47 → 41 and a dissolution on the same end turn). `test_congress_review_round::test_12` re-seated consciously onto the surviving "reopened" road (the unsigned end).
- **RS-D1 as ruled (§6.1).** The capital latch (`kind: "capital"`, written by `congress.note_ratification(capital_kept=)` from `game_end.note_ratification`'s post-clause read of the map; precedence `table` > `beaten` > `capital`; a vassal's or client's hand counts, an ally's does not; a truce, its expiry and an elimination write nothing), the three breakers (derived in `_signed_record` when the capital leaves the bloc, stamped by the tick — "Vienna left our hands"), the price rider (`settlement_scoring.capital_retained_by_proposer_bloc` → `calculate_leader_own_losses(capital_retained_by_proposer=True)`: the capital LOST, the kept-all bonus forfeited — **measured through the real staging on the Vienna shape: a white peace plus 100 gold reads exactly 20 lower with the rider, the whole difference the rider's; the rider SHIPS**), every courtship lever in turns (`courtship_clause`: "about 17 turns at +8 a turn; the Congress sits 8 — not within one sitting"), the SUES projection's road, the review note and both ratifiers' summary line. **Two of the first cut's arms were dead and are gone:** the REFUSES-at-war capital lever (a court whose capital we hold always SUES) and the unpayable arm's "courting alone" clause (it would lie where relations cannot rise that far, and the arm is unreachable on the shipped board). **The rider reads the proposer LEADER's bloc, not the proposer side:** the first cut counted a co-belligerent ally (Spain holding Vienna) as "ours", which the latch never does. `test_sr1a…::test_it_does_not_latch_the_congress` flipped consciously. **The turn-24 replay with Austria latched, driven:** the league forms without Austria, 47 holds, Austria RECOGNIZES on every tick, the latch unbroken.
- **RS-10 + RS-16 (built, not left to the bank).** `congress.league_warning` on the summonable gate line and the summons' report; `march_blocker` reads the BREWING league. `coalition.forecast_alarm_tick` — ONE forecast of the tick's gains against its decay, the cap included, **pinned equal to the tick on the boot (70 → 68) and on the turn-24 save (56 → 57)** — read by `alarm_road` ("rising 1 a turn: our bloc's weight in Europe +3, the designs we deny +1 against 3 of decay …"); the ending C3 probe reads the signed net (an instrument change, recorded: the legacy "falls N" reads as −N). `test_sr1c`'s two alarm-road pins re-seated consciously.
- **SF-V1.** `ai_diplomacy.treaty_offer_refusal` reads the ratifier's OWN two guards (no downgrade; the relation floor) — no adjacency check, because the ratifier has none; `deliver_ai_proposal` withholds a player-addressed letter they would refuse (it reads the TERMS' type first); the auction offers `best_ratifiable_treaty` (the ladder walked down) or resolves `player_won_no_pact`; the refusal reads "Relations with Sweden stand at −60; a Defensive Alliance needs 20." **The withholding found seven test-fixture families that had staged letters no table could sign** (the letter-book's legacy board had Prussia at WAR at −40 and Saxony already at OPEN_BORDERS; four IQ-7 Prussian pacts at −10 against a floor of 0; two conflict-alert alliances at −40 against 40; a peacetime-convergence pact at −10): each now stages the relation at the treaty's floor, with the rule written at the seed. A CA8 producer test staged a defender at PEACE inside a war instance; it now stands at WAR, as any real board's would.
- **SF-V5.** At the ONE emitter: coverage = the opposing courts with a live WAR pair against our side (`_covered_at_war`); the senior covered court writes it when the leader is in a truce; `no_covered_enemy_at_war` eligibility; the dry run through the per-court table with the offering courts' consent (`_letter_would_carry`), a letter that would not carry withheld with no cooldown spent; the three producers handle a withheld letter, and **a player's request for terms the table cannot answer lapses ALOUD** (the first cut lapsed it in silence — the class the row was filed for). **The same reader at the ANSWER seam** (`settlement_offers._live_covered_for_offer`, found by the Step 1 reading itself — UI/UX C4 still read 5 modals on OP's turn 10 after the emitter's rule, because Russia's truce was signed in the same enemy phase the letter arrived and the letter, ratifiable when SENT, hard-stopped when OPENED): the accept drops a court that has since signed a truce with our side from the coverage, as FA-3 drops a court that left the war, and names it as a truce court. **The re-send provenance finding:** the OP arm's turn-13 and turn-16 letters were the player's own request-terms answer and Russia's mediation through the same emitter — not a lifetime defect — so no lifetime rule was built.
- **The R5b decision.** `ai_diplomacy`'s R5b proposal block (an AI court does not PROPOSE to a court it holds a cooldown with) was left unchanged: SF-V1's predicate governs the transport, and R5b's read already honours the store the settlement now writes.
- **Gates.** Sweep 68 of 68 killed on the pre-exit tree, then the 8 rows the exit's fixes added or re-anchored 8 of 8 killed — 0 INERT, 0 BROKEN (`tools/_sweep_step1.json`, 72 rows); **`BASELINE_SERIES` byte-identical on both arms with the reach counted** (`tools/_step1_series_arms.json`: on the 40-turn ambient board the offensive-call bar is asked 0 times, 0 settlement floors are written, 0 titles contested, 0 latches, the rider read 4 times and true 0, 0 letters withheld of 39 delivered, 0 of 2 settlement letters withheld — a passive France signs nothing and no Congress sits, so every lever's reach is zero by construction, and the identity is a measured fact about the harness, not evidence of inertness); **M1–M7 byte-identical** (11 passed); ruff clean; parse harness not run (no `.gd` touched); full suite full suite green in two parts on this machine (the run restarts after the two Godot parse-report staleness pins, `test_godot_parse_harness.py::test_godot_parse_report_is_not_stale_relative_to_settlement_godot_sources` and `test_map_owner_fill.py::test_parse_report_is_not_stale_relative_to_map_renderer_scripts`, which read this fresh clone's file mtimes against the committed report's timestamp and fail at HEAD with no `.gd` touched — deselected): **16,008 + 11,961 = 27,969 passed, 167 skipped, 1 xfailed, 0 other failures**.
- **SF-END-1, the exit — played, and an honest dissolution.** The turn-24 save through the sitting, the orders chosen by hand off the table the board printed (`tools/playtest_scripts/sf_end1_the_peace_holds.json`; the reading and the files in `docs/audits/playtest_digests/sfend1-the-peace-holds/README.md`): Prussia bought at the summons ("1,800g is laid before Berlin (+18). Prussia now RECOGNIZES"); Britain rejected the offered peace twice; the league declared on day 3 and **Austria's war CONTESTED its six titles — 47 of 45 held, Austria SUED (beaten)**; on day 4 the league's three armies beat four French corps and took Moravia, Carniola, Bohemia and Vienna by force, Davout killed, Massena taken — **"The Congress of Paris dissolves — 45 titled provinces (43 of 45) — Moravia, Carniola, Bohemia and Vienna taken by force."** A fall with a cause the player can see and could have prevented, exactly the §6.1 research's day-4 shape; not the September-28 P1. **Found and fixed by the exit:** the dissolution's first reading named the contest ("… contests what it ceded — counted while the Congress sits") as the cause of a count that had fallen to a LOSS — a short count now names what took it, and the contest only while the count stands; the cooldown line carries the cause for the whole cooldown ("dissolved on turn 28 — the titled provinces fell short (43 of 45) — Moravia, Carniola, Bohemia and Vienna taken by force; it may be summoned again …"); both pinned and swept. **An instrument defect found by the reading:** the ending C1 reader took the FIRST digest line containing "dissolv" — on this tree a league's "Coalition against France has dissolved — the league is spent" row — as the Congress's named cause; it now reads the Congress's own dissolution lines only (`tools/score_run.py::r_ending_C1`). **Observed, not filed:** the driver's acceptance of Austria's sue peace stalled at the existing alliance-paradox choice (Prussia, dragged in by France's own defensive cascade, still at war with Austria) — the player's choice, legible; the dissolution's morning was led by Davout's death (96) over the dissolution beat — the chronicle and the Congress line carry it.
- **Item flips (§5; `score_run.py check` + `compare --base docs/audits/score_runs/2026_09_29_c20d5bba`):** nine arms re-run (CONG, OP, CMD-H/A/M, PROP-H/A/M, VOLTE): **the ending C1 ✗→✓** (dissolved for a named cause — the Congress's own line), **C2 ✗→✓** (the summons), **C3 ✗→✓** (the alarm forecast +1 a turn against the quiet ticks), **C6 ✗→✓** (every refuser's price closes the gap, quotes its turns, or is declared unpayable); **diplomacy C6 ✗→✓** (0 treaty-refused-after-accept lines on the commanded arms); UI/UX C4 still ✗ but the OP arm's worst end turn fell from 5 blocking modals to 4, every one now answerable — Britain's letter RATIFIES ("France vs Austria + Britain, 5 pairs resolved") where it had hard-stopped into a three-modal dead end; the ending C4/C5 (the reach at turn 40) and diplomacy C3 (no volte-face on the volte arm) stay ✗ and are other steps'; combat-legibility F1 reads ✓ only because the FLD arm, where it fails, was not re-run — not a flip. No score is claimed (§5); the arms that did not run read unmeasured
- **Census at landing:** `tools/defect_census.py --open` — defect defect 96 OPEN + 1 partial (was 102 + 1), design 17 OPEN; RS-1, RS-2, RS-10, RS-16, SF-V1, SF-V5 closed; RS-D1 BUILT.

### Step 2 — Berthier tells the truth (≈4.0; display and copy, no series moves)

- **SR-6a "The dispatch pass", rebuilt (≈1.2):**
  - AAR-5, AAR4-X2, AAR24-X4, CRT-4-X1.
  - RS-9 with RS-19, as one coverage-label fix.
  - RS-17 (the headline half).
  - RS-20, plus a neutral fallback for the PL-14 net, which closes that family (IQ7-X4, SR-2-X3).
  - RS-23.
  - RS-D2: the levy yields the headline after three unanswered statements.
  - NPC-14, NPC-15, NPC-27, IQ6-D3, SRX-5.
  - NPC-D1 with NPC-27 (homed by SF-0, Sept 29): the Emperor's aura dimming gets its dispatch beat and its battle-row clause.
- **SR-6b "The copy pass" (≈0.8):**
  - RS-18, RS-21, RS-22, RS-25.
  - RS-26 with NPC-12's census: the humaniser at every producer, and a census pin over the muster and the combat lines.
  - RS-29, NPC-23, NPC-24, NP-X6, NP-X7.
  - SRX-6 with SF-V2.
  - WO-D11's copy half.
- **SR-6c "The near miss is a story" (≈0.3):**
  - RS-17's Moniteur half (the gap ≤ 0 case).
  - EAS-2's backend half: the campaign log gains an importance tier.
- **SF-MD-1 "Every man his own voice" (≈0.5):**
  - RS-24: rotate each man's battle lines on his own counter.
  - Named banks for the French marshals, the Archdukes and Kutuzov, keyed on each man's record.
  - Census: no line repeats within a man's five battles on a 40-turn arm.
- **The reserve (≈0.8):**
  - RS-5 with VP-R1-X1, as one slice: the objection's alternatives come from `get_visible_enemies`, filtered for war and reach, and a refused Trust keeps the objection and the order.
  - RS-13, RS-14.
  - NPC-11, NPC-13, NPC-17, NPC-21, NPC-25.
  - RS-28, NP-X5.
- **SF-DIP-1 "The dial survives the drop" (≈0.4; verify first).** The retest's diary says every dropped cover re-drafts the settlement and resets the dial. If that reproduces, restage from the current dial and name each court's change.

**✅ STEP 2 LANDED October 2, 2026 — landing record** (authoritative for what was built; rules `SYSTEMS_REFERENCE.md` §82; pins `tests/test_sr6_the_dispatch_tells_the_truth.py` (53) + `tests/test_sr6a_the_dispatch_pass.py` (26) + `tests/test_crt4_x1_one_clock.py` (11) + `tests/test_sr6b_the_copy_pass.py` (32) + `tests/test_sr6c_the_near_miss_is_a_story.py` (8) + `tests/test_sf_md1_every_man_his_own_voice.py` (12) + `tests/test_sr6_reserve_the_quick_wins.py` (27) + `tests/test_sf_dip1_the_dial_survives_the_drop.py` (5) + 7 IQ6-D3 pins in `tests/test_ai_intent_narration.py`; sweep `tools/_sweep_step2.json` 68 rows → **68 killed, 0 INERT, 0 BROKEN** at close (two pins came back INERT on the first sweep and were repaired before the commit: the NPC-24 pin formatted the template by hand and reached no production line — it now drives `_supply_strain_candidate` with the lever up and down; the NPC-14 yield pin read `HOMELAND_STATEMENTS` for its own loop, so a 300 was invisible — the blessed 3 is a literal now, with a two-statements-does-not-yield arm); attribution `tools/_step2_series_arms.py` → `tools/_step2_series_arms.json`; the voice census `tools/_sfmd1_voice_census.py`). Every row was reproduced at its seam before a line was written (five read-only readers at the session's head; SF-DIP-1 reproduced by hand — a pressed Austria reset to the bare peace the moment Russia was dropped); every slice sits behind its own module lever (`UPPER_CASE = True`; lever down = the shipped behaviour, byte for byte) — 50 levers in all; **no `.gd` was touched** (no Godot on this machine — EAS-2's client half, the eyes items and the Godot parse-report pins stay Step 7's).

- **SR-6a "The dispatch pass".** ONE module `backend/game_logic/intel_surfaces.py` for every enemy-sighting surface (AAR-5 / AAR4-X2 / AAR24-X4): the men standing in a province the player sees at FULL are read LIVE off the map (exact strength, `intel_turn` = this morning, `source: "live"`), the frozen snapshots only where the fog is real, a `[partial]` row never outranking a live one, a FULL label whose live read is empty treated as yesterday's label; the dispatch's INTELLIGENCE rows, the Strategic Ledger's intel tab (humanised names + `roster_name`) and the Berthier report all read it; known garrisons ride as rows of their own (`kind: "garrison"`, exact at FULL, a band at PARTIAL — `garrison_report.garrison_view` is the fog rule) and a foreign garrison's regrowth is a turn event (`garrison_regen_line`). **CRT-4-X1:** ONE clock `strategic.order_turns_remaining(…, movement_range=, before_tick=)` — `march_turns` for an untimed road, the issuing turn's tick skipped, read AT the tick by the report rows and BEFORE it by the Ledger / relay / desk (`ONE_CLOCK`); `order_eta_phrase` takes the marshal's range. **RS-9 + RS-19:** the ratification record names its coverage (`settlement_ratify.THE_RECORD_NAMES_THE_COVERAGE`, the dialogue's own `war_label`) and the review's coverage chips keep every court — `build_settlement_review(table_covered=…)`, the uncovered list (`_uncovered_courts`), "Whole-war settlement" only when nothing is uncovered, a `coverage_label` stamped. **RS-20 + the neutral net (IQ7-X4, SR-2-X3):** the player's own declaration and its objection carry `suppress_proposal_result_popup`; `main._derive_proposal_result_outcome` falls back to RESOLVED → "Diplomatic Action Noted" (`THE_NET_FALLS_BACK_NEUTRAL`), never a REJECT it did not see. **RS-23:** the defensive cascade writes ONE rail row per ally per turn (`diplomacy._note_alliance_cascade`, keyed `cascade:<ally>:<turn>`, the enemy named — "Prussia, Spain and Bavaria Enter War! … against Austria and Russia via their alliance with France"), the dispatch groups the family (`THE_CASCADE_IS_GROUPED`) and the campaign log names the enemy. **RS-D2 (BUILT):** the levy yields once stated — after `LEVY_STATEMENTS` (3) statements with no material change (headroom ±20%, price, a new war) it leaves the page for the Ledger's own line (`THE_LEVY_YIELDS_ONCE_STATED`, memory on `headline_lead_memory["levy_said"]`, no new field), leads at most `LEVY_LEAD_MAX` (1), and a page it would have carried alone says it is quiet once (`quiet_morning`, weight 5 — narration F1's floor until Step 7b's front page). **RS-17 (the headline half):** the morning the gate opens leads at 86 (`congress_summonable`, told ONCE per opening, latched as `summonable_told` inside `world.congress` — created only at the latch, so a world that never summoned keeps `congress is None`) with each refuser's price, the lowered-gate fuse (RS-10) and the ceder risk (RS-2) as `congress_summonable_term` sub-beats (69). **NPC-14:** the occupied homeland is a STATE — a standing class at 81 (`homeland_occupied`: capital first, ≤3 names + "and N more", the holders named, silent the morning the loss is fresh news) riding PC-7's cooldown and ladder; **and the exit's own reading added its yield** (`HOMELAND_STATEMENTS` 3 → `HOMELAND_YIELDED_WEIGHT` 40, the set as the key, below). **NPC-15:** "{region} has fallen to {captor}". **NPC-27 + NPC-D1 (BUILT):** the situation line reads "authority N at court; the Empire's grip G (word); the Presence at +P%" off ONE derived grip (`authority.get_imperial_grip`), the briefing carries `imperial_grip` / `grip_label` / `aura_pct`, and the aura's band crossing (full → dimming → fading → guttering → out, and back) is a beat (`aura_dimmed` 83, memory `headline_lead_memory["aura_band"]`), with the Generals card's ability line stating today's figure (`THE_CARD_SHOWS_THE_PRESENCE_TODAY`). **IQ6-D3 (BUILT):** the intent narration has a dead band — a weight move under `INTENT_DEAD_BAND` (5) keeps its anchor (`THE_NARRATION_HAS_A_DEAD_BAND`), and the tail names its courts ("And Spain and Holland stir at their own designs", `THE_TAIL_NAMES_ITS_COURTS`). **SRX-5 / RS-14:** the desk reads the table — `demanded` (the letter on the desk, the Congress's answer, the last letter's record), `where_nation` ("Sire — Austria: Mack at Swabia (large force); no word of Archduke Charles"), `alarm` ("Europe's alarm stands at 70 — Formed … the next tick reads 68"), demonyms resolve ("the Russians"), and "remind me / tell me what …" is a question (`clause_guards.TELL_ME_IS_A_QUESTION`).
- **SR-6b "The copy pass".** **RS-18:** the voiced settlement summary fills its two slots from `applied_clauses` (received vs paid against the proposer's bloc; a payment alone is never voiced as a return — `THE_SUMMARY_FILLS_ITS_SLOTS`). **RS-21:** a warning names its component ("National design (+12)", `acceptance_component_display`) and a review every covered court CONSENTED to carries no acceptance concern (`warnings` is the consent-filtered list, `warnings_before_consent` keeps the raw one). **RS-22:** the legitimacy sentence presses ONE court ("Press Austria alone: the separate peace. It costs 3 diplomatic points; you have 5. The others — Russia — can each be treated with alone, at 3 points apiece."). **RS-25:** the Congress's ports lever through a truce or a peace says "the System shuts a port only against a court at war with it — in a truce, no port is closed to her" and the decree's text says "at war" (`congress.THE_SYSTEM_NAMES_ITS_CONDITION`, `reforms.effect_line`). **RS-26 with NPC-12's census pin:** the combat resolver's description seam speaks display names (`combat._field_names`, whole-word, longest key first — both `"description":` sites), the muster hedge and the Ledger's rows too; the census pin drives a real battle and scans every sentence of the reply, the report and the events for a roster key (NPC-12's OPEN REMAINDER — the ~426 other interpolations — stays open and tagged). **RS-29 / NP-X7:** "his support order" (`strategic.A_SUPPORT_ORDER_IS_SINGULAR`); `display_names.marshal_honorific` is the court's own rank — "the Emperor Napoleon" / "the Archduke John" / "General Kutuzov" / "Marshal Ney" — at the dispatch's six wound-and-death lines, the capture headline and the desk, and its docstring states its true coverage. **NPC-23:** "Lannes, Murat and Napoleon stand in his path." **NPC-24:** "1,351 men dead" (`losses_dead`). **NP-X6:** the sovereign's card and the personality table say what the live parser actually does with a delegated order. **SRX-6 + SF-V2:** a white peace speaks its OWN blocker — "it claims no victory, but a whole-war peace still needs every covered court's consent, and not every court consents" (`spoken_blocker_phrase(…, white_peace=True)`, at the dialogue's message AND every per-court holdout line — `resolve_multi_court_settlement_voice(white_peace=)` reads the G4F-19 derivation first) and "Will NOT carry as drafted" never sits beside a live Ratify button (`_verdict_beside_the_button`: "Carries on the leader's word — …", the per-court verdict kept as `per_court_verdict_display`). **WO-D11 (the copy half, BUILT):** a mid-march capture says what it forfeits — " The province is secured. Archduke Charles's estate there is forfeit — the column takes no windfall and buys no goodwill." — and the strategic road now CARRIES the capture sentence (`movement_executor` stamps `capture_note`; `strategic_executor._capture_tail` appends it to every first-step line, `THE_MARCH_REPORTS_ITS_CAPTURE`): the "march to" road had reported only " Moves to X." for every capture it made.
- **SR-6c "The near miss is a story".** **RS-17's Moniteur half:** at a gap ≤ 0 the column speaks — "THE CONGRESS OF PARIS — 47 of 45 provinces titled: the Emperor may summon the powers. London and Vilna would refuse today; Vienna would sign." — or names the one term the summons still waits on (`gazette.THE_MONITEUR_SEES_THE_OPEN_GATE`, `_open_gate_line`); the near-miss column is unchanged. **EAS-2's backend half:** every `GET /campaign_log` row carries a display-only `tier` (lead / notable / routine — `campaign_log.event_tier(event, world)`; `LOG_TIER_LEAD` 23 / `LOG_TIER_NOTABLE` 53 / `LOG_TIER_ROUTINE` 95 partition all 171 types exactly, pinned; a battle that took the province, destroyed or routed a corps or was decisive leads, a capital changing hands leads — read off the world's region, no producer key). The client half (size by weight in `campaign_log.gd`) is Step 7's.
- **SF-MD-1 "Every man his own voice".** **RS-24:** the voice banks rotate on the SPEAKER's own battles — `combat_executor._voice_rotation_key_for` (a decided battle, already counted on his record by `resolve_combat`, subtracts itself back out; a draw counts on neither record and is read from the log's stalemate rows, so every battle advances the key by exactly one), both mouths; a named row no longer ENDS the bank — the personality lines follow it (`voice_bank`, `THE_NAMED_BANK_FALLS_THROUGH`, index 0 of every bank unchanged). **Named banks:** every French marshal of 1805 in every situation (Lannes / Soult / Bernadotte / Massena authored; Ney / Davout / Murat completed), both Archdukes (John had borrowed his personality's "I trade ground for time" three battles running) and Kutuzov, Mack's and Wellington's missing situations; every personality bank grown to five, append-only. **Census:** structurally, every man on the 1805 board × every situation × every five-key window gives five distinct lines (pinned); on the 40-turn commanded arm (`tools/_sfmd1_voice_census.py`): 8 speakers, 26 voiced battles, **0 repeats within any five** — Archduke Charles 8 battles / 8 distinct, Ney 6 / 6; the driver's battle record now carries `enemy_voice` beside `voice`.
- **The reserve.** **RS-5 + VP-R1-X1 + NPC-D4 (BUILT):** the aggressive objection's Trust arm offers only a man the player has SEEN, where the player believes him to be, over water the navy leaves open (`disobedience._get_aggressive_preferred`: `get_visible_enemies` → `pursue_known_location` → the crossing gate, adjacent first then a pursuit within 3; boot: "Trust: Murat attacks Mack", where it had offered an unseen Kutuzov); the alternative's ONE source `get_enemies_in_range` keeps only courts at WAR with the marshal's (an ally's corps was offered, and refused) and, for the player, only men in view; **the backstop:** a Trust whose preferred order the executor REFUSES keeps the objection on the desk and the authority tracker unmoved — "The objection stands — 'insist' presses your original order" — where it had answered "No objection pending" and lost the support order (`A_REFUSED_TRUST_KEEPS_THE_OBJECTION`); **NPC-D4:** the auto-upgrade announces its terms at issue time — "A standing order, not a single attack: he closes 1 province a turn — about 3 turns to Tyrol, attacks on arrival, may be diverted by an interrupt, and stands down if intelligence on him lapses. 'Soult, cancel' recalls him." (`THE_PURSUIT_STATES_ITS_TERMS`; an explicit `pursue` states none). **RS-13:** an attack pressed through an objection (trust / insist / compromise) prints its muster with the confirm popup off (`meta_executor.THE_PRESSED_ATTACK_PRINTS_ITS_MUSTER`, `command={"_muster_confirmed": True}`; the disobey arm, stamped `_disobedience`, keeps none). **NPC-11:** the literal's quote is the player's own words — `"Soult, attack Archduke John." No more and no less.` — the typed text rides the auto-upgrade (`THE_LITERAL_QUOTES_THE_TYPED_ORDER`). **NPC-13:** the engaged-move refusal names the enemy and offers only a retreat that exists ("Cannot advance while engaged with Mack at Swabia. He may fall back to friendly ground — Lorraine, Rhineland — or fight." / "No friendly province adjoins him: he must fight or stand."; `retreat_options` + the typed hint on the result). **NPC-17:** the Emperor leading is not hedged ("if he marches" only when he must), and the hostile row names the lead ("will not lift a finger for the Emperor Napoleon"). **NPC-21:** a typed answer that picks an option a `proposal_confirm` dialogue marked closed is refused with the option's own reason and the dialogue stays on the desk (scoped to that family — the petition families process a closed arm on purpose). **NPC-25:** "needs one victory first: a single battle won as the attacker arms the charge (recklessness 0 of 1)." **NP-X5:** `mods/examples/battle_of_waterloo.json` validates clean — the two seats the runtime rule wants (Britain's Netherlands, the legacy proxy; Prussia's Berlin) stand off the map's edge. **RS-28 — corrected on the record:** the one die the `fixed_rng` fixture left live (the 5% fumble roll) is now pinned, **but it is NOT the mechanism** — a co-located Emperor's arrival takes no die (pinned), and twenty hash seeds pass standalone — so the 1-in-1,008 failure is cross-file state, still unisolated; the npv test now pins the aura's inputs (the lever, the sovereign's flag, grip 100, aura 1.0) before the attack so a recurrence names the leaked input instead of the symptom. **RS-14** is SRX-5's sibling above.
- **SF-DIP-1 "The dial survives the drop" — verified REAL, then built.** Every cover add/drop re-drew the WHOLE package from the baseline. Now the remaining courts keep the terms the player dialled, only the dropped court's clauses are struck, an added court receives the baseline slice authored for it, and the message names each court's change ("Dropped Russia — 0 clauses naming it struck. Austria keeps 1 clause (gold indemnity)."; `settlement_actions.THE_DIAL_SURVIVES_THE_DROP`, `clause_names_court`, `_terms_after_cover_edit`). **The rider the exit found:** with the terms surviving, the letter's consent could survive a coverage change — `consent_kwargs_for_restage(…, covered)` now lapses consent when the covered set differs from the letter's (SR-2a's rule read on both halves; its pin held).
- **The full suite then found four pins the slice's own families had not run** (first run: 4 failed / 28,123 passed), all taken before the commit: (1) `test_iq2_collapse_dispatch.py`'s hand-back — on a France reduced to Paris the new `homeland_occupied` class took the lead the moment `empire_reduced` yielded, so Berthier's note was the occupation's instead of the bleeding treasury's; **a second voice on IQ-2's one fact**, now silent while the realm's collapse state is live (guard in the producer, pinned both ways, sweep row 68 killed); (2) + (3) the two `supply_strain` template pins (`test_pc15_fix_slice_2026_08_15.py`, `test_pc2_pc7_enemy_phase_and_headline.py`) re-seated for the builder's `{losses_dead}` field, the PC15-12 precedent exactly; (4) the Step-0 census pin that used NPC-D1 / NPC-D4 as its OPEN examples now reads them closed.
- **Gates.** Sweep 68 rows → **68 killed, 0 INERT, 0 BROKEN** at close (two pins came back INERT on the first sweep and were repaired before the commit: the NPC-24 pin formatted the template by hand and reached no production line — it now drives `_supply_strain_candidate` with the lever up and down; the NPC-14 yield pin read `HOMELAND_STATEMENTS` for its own loop, so a 300 was invisible — the blessed 3 is a literal now, with a two-statements-does-not-yield arm); **`BASELINE_SERIES` byte-identical on both arms with the reach counted** (`tools/_step2_series_arms.json`: every lever down, every lever up — divergence None on both; on the 40-turn ambient board the objection chain, the cover edit and the live-sighting reader are reached 0 times, the field-name humaniser 58 times and the per-marshal voice key 88 times — display seams only, so the identity is a fact about the harness AND about the step: no series moves, as the step's contract required); **M1–M7 byte-identical** (11 passed); ruff clean; Godot parse harness not run (no `.gd` touched); full suite **28,128 passed, 167 skipped, 2 deselected, 1 xfailed, 0 failed in 14:32** on this machine, run by hand (the pre-commit hook is not installed on this clone — Step 1's precedent; the two deselected tests are the Godot parse-report staleness pins, which read this clone's file mtimes against the committed report's timestamp and fail at HEAD with no `.gd` touched).
- **The exit's own two findings, both fixed in-session** (`score_run.py check` read them off the first re-run, which is why the exit runs before the commit): **(1) `marshal_drama.C5` ✓→✗** — at 81, `homeland_occupied` led 6 of 9 mornings on the OP arm and buried the first erosion notice (55), so Lannes's escalation arrived unannounced; the class now takes RS-D2's own rule (`HOMELAND_STATEMENTS` 3 statements of the same occupied set, then `HOMELAND_YIELDED_WEIGHT` 40 — on the page as a sub-beat, never the lead, until the set changes; memory `headline_lead_memory["homeland_said"]`): C5 reads ✓ again. **(2) `narration.C4` ✓→✗** — the probe's contract was the PRE-AAR-5 one ("every intelligence row … where the intel store last saw him"), which the fix breaks by design (a live row places the man where he STANDS in full view this morning; the store is written before the enemy phase); the probe now accepts a `source: "live"` row standing in a FULL province and skips garrison rows (an instrument change to the reader, not the checklist): C4 reads ✓ again (56 rows).
- **Item flips (§5; `score_run.py check` + `compare --base docs/audits/score_runs/2026_09_29_c20d5bba`, six arms re-run: OP, FLD, DL, CMD-H/A/M):** **diplomacy C6 ✗→✓** (0 treaty-refused-after-accept lines), **the ending C6 ✗→✓** (4 refusers, each price closing the gap, quoting its turns, or declared unpayable), **first contact C3 ✗→✓** ("where are the Russians?" / "why is Europe alarmed?" answered by the desk), **marshal drama C3 ✗→✓** (73 voiced battles, no repeat within three wins); narration F1 ✓ (0 of 40 turns without a headline on every CMD arm), F2 ✓, C2 ✓ (no rail row repeated >3×, no war entry naming no enemy), C4 ✓, C5 ✓; **narration C1 stays ✗** (one class still leads 10 of a 10-turn window on the CMD arms — `estate_eroding` on CMD-H, `homeland_occupied` on CMD-A, the nag Step 7b's family allowance owns); the arms that did not run read unmeasured. No score is claimed (§5).
- **Census at landing:** `tools/defect_census.py --open` — **defect 58 OPEN + 1 partial** (NPC-12's remainder; was 96 + 1), **design 12 OPEN** (was 17): 38 defect rows newly closed (IQ7-X4 and SR-2-X3 already read closed at HEAD and are stamped for the record), RS-D2 / NPC-D1 / NPC-D4 / IQ6-D3 / WO-D11 BUILT.

### Step 3 — Europe acts without France (≈6.5; gate SR-G7 at its head)

Order: RS-3 → SR-7a → SR-7b → SR-G7 (built as ruled) → SR-7c → RS-27 → SF-LB-1 → SR-7d. SR-7d goes last so the doctrines do not confound the long-peace measurement.

- **RS-3** (its shape is ruled in §6): a field win halts before a garrison that still fights, or the garrison fights beside the corps. Flip arm.
- **SR-7a "The AI's odds gate and its dithering"** (AAR-D8), taking with it:
  - CQ-22: one stance rule for drill on every road; the direction is §6's.
  - IQ5-R1: the casualty pool splits by committed bodies.
  - XR-3's remaining half: no march attrition on an in-place capture.

  One series re-record, flip-attributed per lever.
- **SR-7b "The long peace, measured"** (PB-D1): the baseline arms first.
- **SR-G7 "The Armed Peace"**, as ruled (§6.2): the watch at 45 while the hegemon leads ≥ 1/3 of Europe's power, then the 16-quiet-turn fuse at +3 a turn up to the brewing gate. PB-D1's completion clause is its acceptance test (3 of 3 commanded seeds; projected league turns 32 / 29 / 31). SR-7b's baseline arms were already measured by the ruling's research.
- **SR-7c "Dispersion"** (AAR-D4).
- **RS-27** (measure first): bisect what moved the volte-face, then either pin it firing on its arm or re-script the arm.
- **SF-LB-1 "Europe's own quarrels" (≈1.0):** deck authoring — IQ6-D1's Austrian follow-on, and `gulf_and_straits` waking without a volte-face. Measured to open at least one ambient AI-vs-AI war in 40 turns on ≥ 3 of 7 seeds.
- **SR-7d "The Doctrines"** (DC-0 … DC-3c, ≈2.5): `DOCTRINES_SPEC.md` §7.

**✅ LANDED October 2, 2026 — seven of the eight slices (RS-3 → SR-7a → SR-7b → SR-G7 → SR-7c → RS-27 → SF-LB-1); SR-7d "The Doctrines" is NEXT, as its own session (the long-peace measurement it must not confound is done).** Rules `SYSTEMS_REFERENCE.md` §83 (authoritative for the mechanics); rows `BUG_FIXES.md` RS-3 / RS-27 / CQ-22 / IQ5-R1 / XR-3 → FIXED; design rows `DESIGN_REFINEMENT.md` AAR-D8 / AAR-D4 / PB-D1 / IQ6-D1 / SR-G7 → BUILT; pins `test_rs3_the_garrison_stands.py` 11 · `test_sr7a_the_ais_odds_gate.py` 34 · `test_sr_g7_the_armed_peace.py` 36 · `test_sr7c_dispersion.py` 11 · `test_rs27_the_volte_face_fires_on_its_arm.py` 2 (driven) · `test_sf_lb1_europes_own_quarrels.py` 22 · `test_step3_the_contact_prints_its_muster.py` 3; sweep `tools/_sweep_step3.json` 59 rows → **59 killed, 0 INERT, 0 BROKEN** at close (three pins came back INERT on the first sweep and were repaired before the commit: the P4.9 stance pin had staged Mack, a LITERAL the heal drill never offers, so it proved nothing; nothing drove the stagnation breaker under the dither guard; every fuse pin read the constant, so the fuse's number itself was unpinned — a literal 19/20 pin now).
- **Reproduced first, at its seam, before a line:** the pre-tree ambient probe counted RS-3's walk-in once, IQ5-R1's full-strength split 36 times, 2 of the 3 AI drills in AGGRESSIVE stance (CQ-22) and 2 in-place captures charging a march (XR-3); AAR-D8's grind and dither were read off the AI's own rungs.
- **One series re-record, flip-attributed per lever** (`tools/_step3_series_arms.py`, fifteen arms, every lever set in the child, every seam's reach counted — `tools/_step3_series_arms_final.json`): arm 0 byte-identical to the SR-5a series; RS-3 diverges at [12] (9 halts), the odds gate [15], CQ-22 [18], IQ5-R1 [24], XR-3 [5], the Armed Peace [23], dispersion [25], the dither guard [18]; the small-garrison surrender and SF-LB-1's four levers are byte-identical ALONE (12 design asks fire and nothing the ambient board acts on changes); the shipped tree diverges at [13]. The passive France is no worse (3 provinces at turn 40 on arm 0 and on the shipped arm). M1–M7 byte-identical without re-record.
- **SR-G7 as ruled — and the fuse lengthened 16 → 20 by the ruling's own remedy.** At 16 the league came on turn 31 on marengo and the commanded France lost 16 provinces to it (27 → 11; attribution: the Armed Peace alone — every other lever down leaves 11, that one down leaves 27 and no league). At 20 (the band's end): leagues on turns 30 / 40 / 35 (historical / austerlitz / marengo), France 26 / 28 / **19** at turn 40. **PB-D1's clause: 3 of 3** (the alarm rises after the peace and a league declares in turns 12–40 on every commanded seed, not by cascade) — PB-D1 CLOSES. **F1's guard: 2 of 3** — marengo's France (57,000 men at peace; the commanded script never levies) is one province under the floor; reported, not hidden, and the ruling names no lever below the watch: **the user's call** (lower the rise to +2, widen the band, or accept 19 on a France that did not arm during twenty quiet turns). The Armed Peace never holds on the ambient board (a France of 3 provinces leads no bloc).
- **The Armed Peace on CMD-H at fuse 16 never fired** for a reason that is not a miss: the armistice collapsed and France fought Austria from turn 15 to 30, then Britain led the largest bloc. At fuse 20 the same seed brews on 27 and declares on 30.
- **RS-27 measured first** (§83.5): the first bisect was wrong — it read a LOG row the digest dedupes once the rail has printed it — and the shipped tree fires the beat at turn 21; attributed to RS-3 and the odds gate (each necessary); pinned driven, both directions.
- **✅ Both questions below were RULED October 3, 2026 — §6.4 (SF-LB-2 "The Defenceless Prize", the head of Step 4) and §6.5 (the fuse stays).**
- **SF-LB-1's target is NOT met and the question is put:** the four levers and Austria's third design make Europe ASK (Prussia at Hanover, 12–16 asks on the ambient series), harden on refusal, re-aim an allied court, and wake Russia's Baltic design in the armed peace — but 0 of 7 ambient seeds open an AI-vs-AI war, because an acquire design between two AI courts tops out at 71–81 against the `fight` bar of 85 (AI-3r's own choice). **Recommendation:** open the AI-vs-AI crisis at `coerce` (72) when the holder is outmatched ≥ 2:1 on free strength (a `WEIGHT_HOLDER_OUTMATCHED` term, +10, derived) — the Prussia→Hanover case reaches it on every seed measured; the alternative (lowering `fight` itself) re-prices every France-facing design and is not recommended.
- **The exit's own regressions, fixed in-session:** combat C1 (the FLD arm's `attack_anyway` answer fought without a muster — `strategic.THE_ANSWERED_CONTACT_PRINTS_ITS_MUSTER`; and the digest never rendered the answered interrupt's reply, so the fix was invisible to its own instrument — `playtest_driver.THE_DIGEST_PRINTS_THE_ANSWERED_MUSTER`); narration C4 (a prisoner's three-turn-old snapshot led the intelligence rows the morning after his capture — `intel_surfaces.A_PRISONER_IS_NOT_A_SIGHTING`, a Step-2 seam this board exposed); AI C5's dither (the first odds-gate cut made an idle cautious corps fortify / unfortify at peace — the three-part dither guard); the instrument's three readings (combat F2 board refusals counted separately per §4.2, combat C3's works-halt arm, AI aliveness C6's turns at war read off the digest's own war rows).
- **Combat F2 reads a BOARD refusal on OP and FLD:** with RS-3 up, Charles's turn-2 win over Massena halts before Milan's works instead of walking through him, so he stands at Tyrol on turn 3 and breaks Ney at Bohemia twice; the turn-4 scout of Vienna is refused ("recovering from retreat"). A board refusal, counted separately; OP is never re-authored (§4.2).
- **Two ✓→✗ reported, attributed, and NOT tuned:** marshal drama C1 (OP's petition modals 3 → 5 in twenty turns — RS-3 alone: Charles halts before Milan's works, stands at Tyrol and breaks Ney at Bohemia, and the fights that follow fire two more crisis-tier confrontations; the Antechamber's tier rule and SR-4c's cadence are unchanged and are not tuned to pass a count) and AI aliveness C1 (CMD-H: Austria's three laws lapse on turn 31 after a fifteen-turn war with France that the baseline board never fought — the laws lapse when unpaid by the user's own ruling, so a court bankrupted by war lapsing them is the design, reported not tuned).
- **Twenty-two standing pins re-seated consciously, each with its attribution** (the full suite's first run: 22 failed / 28,389 passed): the four series-chain pins (the drill fix, DP-1, RF-3, VP-R1 — one more link: SR-5a's arm 1 is the prior Step 3's arm 0 reproduces, Step 3's ALL arm is the standing series); the WO slice-10 ambient-board figures (ungated seams 11 → 22 + 1, the pair split, the ungated series, cooldowns 12 / 0 → 22 / 0) and WO slice-9's rebellion turns (17 / 23 → 14 / 18; the Kingdom of Italy's elimination step at [12], −12) — **measured with every Step-3 lever down in the child, the SR-5a figures return verbatim** (`tools/_step3_wo_attribution.py` → `_step3_wo_attribution.json`); the FA-D28 grind runs with the small-garrison surrender down (measured lever by lever, the surrender is the sole mover: a 12,000-man garrison surrenders at 500 and the grind ends six assaults in); SR-exit's `garrison_fights` formula gains the 500 floor; the two WO crowding pins stage FOUR corps on a capital (three are free now); the two IQ-7 card pins stage the Swiss loyalty they measure the countdown against (the re-timed board took them under the loyal line); six FA-slice-15b driver pins were red only because the new exit-fix pin set a module lever bare — it uses `monkeypatch` now.
- **Item flips (§5, never a new score):** **✗→✓** combat legibility F1 (71 battle lines, every side's losses named — the FLD arm ran this time; not a Step-3 flip), combat C1 (back to ✓ once the digest rendered the answered muster), living balance C4 (the fresh-peace floor held on every declaration), diplomacy C3 (the volte-face on its arm — RS-27), diplomacy C6, the ending C6, first contact C3, marshal drama C3, agendas C3 (Ireland's gate term flipping to met between saves — the Armed Peace's leagues put Britain at war with France again); **✓→✗** living balance F1 (France 26 / 28 / 19 — marengo one under, the fuse at the band's end, the user's call), marshal drama C1 (OP modals 5 — RS-3's board, attributed), AI aliveness C1 (Austria's three laws lapse after a war the baseline never fought — attributed); narration C4 ✗→✓ after the prisoner-snapshot fix; narration C1 stays ✗ (Step 7b's); **unmeasured this run, ✓ at the baseline:** living balance F2 and the three SUITE-fed F1s (the SUITE arm was not re-run; the suite ran by hand — green), combat F2 (every capital scout a BOARD refusal, counted separately per §4.2), combat C3 (no capital taken after a field battle — RS-3 halts the walk-in; the works-halt arm counts a NAMED garrison when it occurs). No score is claimed (§5); directional reads over the exercised pillars only.
- **Census:** `tools/defect_census.py --open` — **defect 53 OPEN + 1 partial** (NPC-12's remainder; was 58 + 1), **design 9 OPEN** (was 12): RS-3 / RS-27 / CQ-22 / IQ5-R1 / XR-3 FIXED; AAR-D8 / AAR-D4 / IQ6-D1 BUILT, PB-D1 CLOSED, SR-G7 BUILT.
- ~~**▶ NEXT = SR-7d "The Doctrines"**~~ ✅ **SR-7d LANDED October 3, 2026 — STEP 3 IS COMPLETE** (landing record `DOCTRINES_SPEC.md` §7.1; rules `SYSTEMS_REFERENCE.md` §84; pins `tests/test_sr7d_the_doctrines.py` 70; sweep `tools/_sweep_sr7d.json` 61 rows → 61 killed, 0 INERT, 0 BROKEN at close (the first sweep found four pins inert and all four were real weaknesses, repaired: the homeland exemption had never had to decide a STRIPPED Paris; the with-support odds saturate at 99 for every French pair so the bar pin is staged at logistics 0 where 50 vs 60 decides it; the enemy's slow-concentration line had been staged on Archduke Charles, who refuses Mack by the authored hostile pair, so the note was empty and the pin conditional — Archduke John answers; the cures effect line had no pin of its own); the series re-recorded ONCE, nine-arm attributed, arm 0 byte-identical to Step 3's; M1–M7 byte-identical; the exit's arms `docs/audits/score_runs/2026_10_03_sr7d/`: **✗→✓ living balance F1 (France 28 / 21 / 22 at turn 40)**, ✓→✗ first contact C4 / AI aliveness C5 / combat C2 each attributed with the lever down and not tuned, marshal drama C5's reader fixed; **defect 55 OPEN + 1 partial (was 53 + 1 — the two SR-7d rows), design 9 OPEN**). **▶ NEXT = Step 4 "the three misses, second pass"** (§3 Step 4). *(The line below is kept as the record of the slice's size.)*
- **(record)** SR-7d "The Doctrines" (`DOCTRINES_SPEC.md` §7, DC-0 … DC-3c; ≈2.5 sessions, the client slice 1.1) as its own session, then Step 4.

### Step 4 — the three misses, second pass (≈5.3)

- ~~**SF-LB-2 "The Defenceless Prize" (≈0.5, FIRST — §6.4's build, the Step-3 question answered October 3, 2026):** the holder-outmatched weight term + the crisis opening at `coerce` for an AI-vs-AI prize that cannot defend itself; Prussia→Hanover is the measured case; acceptance = living balance C1 on ≥ 3 of 7 seeds plus the variance clause; one series re-record, flip-attributed.~~ ✅ **LANDED October 3, 2026** (landing record §6.4's addendum below; rules `SYSTEMS_REFERENCE.md` §85; pins `tests/test_sf_lb2_the_defenceless_prize.py`): **Prussia takes Hanover on 7 of 7 seeds** — the crisis opens at `coerce` on turn 9 (10 on marengo), the declaration follows on 11 (12), and the war is over by 14 (15); living balance C1 MET; **the variance clause is MEASURED NOT MET** (the opening waits on Berlin's purse, not the ladder — §6 row 14, the user's) and stands as a strict xfail. Three things the ruling did not foresee were built and recorded: a court asks before it demands (eylau's ladder could never climb), the fight road reads the restraints at the opening (Sardinia's and Russia's theatre), and a province outranks a friendly namesake (Prussia's own marshal Brunswick had kept the army in Berlin for the whole war). ~~**▶ NEXT = SF-CL-1 "The forecast keeps its word".**~~ ✅ SF-CL-1 landed October 3, 2026 (the row below); SF-CMD-1 part (i) the census landed the same day. **▶ NEXT = SF-CMD-1 part (ii), the fixes (W1 … W9).**
- ~~**SF-LB-2b "The Chest the Council Can Spend" (≈0.5, the §6 row 14 build, RULED October 3, 2026):** the crisis OPENING reads the chest the court will have when the turn ends; the declaration keeps the live chest; the variance clause's xfail flips.~~ ✅ **LANDED October 3, 2026** (landing record §6.4's second addendum; rules `SYSTEMS_REFERENCE.md` §85.8; pins `tests/test_sf_lb2_the_defenceless_prize.py::TestTheChestTheCouncilCanSpend` + the driven class + `tests/test_ai_intent_assurance.py::TestTheStandingRuleOnCouncilWars`): ONE lever `war_council.THE_COUNCIL_SPENDS_THE_TURNS_INCOME`, ONE seam `ledger.chest_forecast` (the LAWS tab's own projection, `reforms.lapse_forecast` re-routed through it), `_restraint_block_reason(..., forecast=True)` at step 3 only; reproduced at the council's own seam first (the opening had read a post-spending, pre-income purse); **the first openings read {5 ×6, 9} — the clause is STILL NOT MET and its xfail stays strict**: the recommendation's premise ("the ladder varies 3–8") was wrong by measurement — the ladder is climbed after turn 3–4 on six seeds and turn 4's projected chest reads 497 against 500 on each; the war's turn varies (9 / 11 / 12; marengo's first crisis cools on a seeded dip and re-opens); `BASELINE_SERIES` re-recorded ONCE (one lever, arm 0 byte-identical, the shipped tree at [21]); M1–M7 byte-identical; **the six-seed cluster = §6 row 15, put to the user with a recommendation (seeded patience on the design ask); nothing under it built.**
- ~~**SF-CL-1 "The forecast keeps its word" (≈0.8, after Step 3).**
  - Across the benchmark arms, log every prediction beside what the resolver committed: the odds band, "WILL JOIN", the what-if, the scout line, the objection's figure.
  - Fix each class of divergence, and pin the census.~~ ✅ **LANDED October 3, 2026** (rules `SYSTEMS_REFERENCE.md` §86; rows `BUG_FIXES.md` §SF-CL-1 X1–X2 + `DESIGN_REFINEMENT.md` SF-CL-1-D1; pins `tests/test_sf_cl1_the_forecast_keeps_its_word.py` 19; sweep `tools/_sweep_sf_cl1.json` 17 rows → 17 killed, 0 INERT, 0 BROKEN): **the instrument** — `ForecastLedger`, a transport observer in the playtest driver, writes one `forecast` row per surface (the muster's expected / ceiling / band / WILL JOIN with quoted odds, an objection's band, an interrupt's, a scout's garrison, a garrison assault's figures) beside the resolver's new display-only `massed_strength` and the battle; `tools/forecast_census.py` reads them into classes. **Found and fixed:** the structured muster had never reached the wire (X2), and **the muster's ceiling was not a ceiling** — the resolver stamps a coordination bonus of up to +25% on every participant before it sums the committed strength and the preview never priced it (the Emperor's co-located attack: "up to 112,775" against 138,604 fought; X1). `_priced_coordination` now reads the preview under the exact context the resolver will stamp (the mirror honours the resolver's own semantics: arrivals relocate into the field, the lead keeps his province's context — SF-CL-1-D1 files the design question that exposes). **Measured on the exit archive:** **44 forecast rows** (garrison_assault 4, muster 18, objection 16, scout 6); **expected_miss 0 · solo_mismatch 0 · unpromised_arrival 0 · band_disagreement 0 · scout_vs_assault 0**; shortfall_from_absences 1 (the die: CMD-M t1 Ney→Mack: 58,650 fought against 85,373 expected, Lannes (95%), Murat (76%) did not); promise rate 43/48 = 0.896; bands out-bleed even 1/1, favorable 13/15, unfavorable 0/1. **Item flips (§5, never a new score), the seven exit arms against SF-LB-2's exit (`docs/audits/score_runs/2026_10_03_sf_cl1/`, `check` + `compare --base 2026_09_29_c20d5bba`): ZERO.** One ✓→✗ appeared on the first check and was resolved before the commit as the instrument's own time skew, the game untouched: narration C4 read Brunswick's turn-2 Berlin snapshot on the CMD-A turn-10 MORNING rows against an EVENING store that had re-read Berlin empty the same turn (he had marched to Hanover's war; the region-keyed store forgets a man a re-read no longer shows) — `tools/_score_probes.py::narration_c4_intel_row` now reads a frozen snapshot row whose province the store re-read after the row's own turn as true when written, and names such rows in its evidence. Combat C2 stands ✗ as it stood (11 of 13 favorable battles out-bleed; the three "even" battles all did — a sample too small to rank). The arm's course moved because the muster's band now reads the resolver's own figures; the series did not (player-only by construction). **Census at close** (`tools/defect_census.py`): defect 55 OPEN + 1 partial (SF-CL-1-X1, X2 filed FIXED), design 10 OPEN (SF-CL-1-D1 filed). Two CA9 pins re-seated consciously under the priced context (`test_ca9_row3_phase_a_legibility.py` band invariance, `test_creative_audit_ca9_2026_08_08.py` F1 symmetric defender).
- **SF-CMD-1 "The unrehearsed line" (≈1.5).** ✅ **Part (i) THE CENSUS LANDED October 3, 2026** (memo `docs/audits/UNREHEARSED_CENSUS_2026_10_03.md`; rules `SYSTEMS_REFERENCE.md` §87; pins `tests/test_sf_cmd1_the_unrehearsed_census.py` 22; worklist `BUG_FIXES.md` §SF-CMD-1 W1 … W9): 150 orders + 150 questions written blind (`tools/playtest_scripts/unrehearsed_2026_10_03.json`), run keyless and keyed on fresh boot boards (`tools/unrehearsed_census.py`, the ONE judge shared with the HOLD arm in `_score_probes.py`), records committed under `docs/audits/unrehearsed/`. **Keyless:** orders: as meant 53 · asked 28 · board refusal 25 · refused as meant 17 · honest refusal 18 · shrug 9 · **misread 0 · executed-when-refusal-meant 0**; questions: answered 36 · shrug 114. **Keyed:** orders: as meant 55 · asked 30 · board refusal 27 · refused as meant 17 · honest refusal 20 · shrug 1 · **misread 0 · executed-when-refusal-meant 0**; questions: answered 37 · shrug 113. **Nothing the player did not mean was executed on either arm.** The spec's resolution-aware-confidence item did not reproduce (the CX-R1/CRT-2 guards refuse an unresolved target free); it stays a pin. ~~**▶ Part (ii) = the fixes W1 … W9 (the desk's 114 shrugs with CRT-9; the contingency vocabulary; the basic forms; bare diplomacy with CRT-8; the pronoun; the epithets; the adverb and the reason clause; the naval phrasings; the nameless board refusal) — NEXT, then Chunk 3b trimmed to what the census confirms.**~~ ✅ **Part (ii) LANDED October 3, 2026** (rules `SYSTEMS_REFERENCE.md` §88; pins `tests/test_sf_cmd1_part_ii_the_fixes.py`; STATUS top entry): W1 = `backend/ai/state_desk.py`, the desk's second table (the committed census's 114 question shrugs → 0); W2 the contingency phrasings in CR-7's vocabulary (arrival idiom / premise checked at issuance / engagement = SUPPORT / halt tail = the road's rule); W3 the basic forms (both end-turn gates widened; the negated compound ASKS); W4 + CRT-8 (the bare Cabinet verb; RS-7; **§6 rows 7 and 8 taken at their defaults and BUILT** — CX-X3 the gated vassal verb, CQ-36 the honest Break reason); W5 the comma before a second name + the supported pronoun; W6 the epithets; W7 + CRT-6's part; W8; W9 + CRT-9's state probe (RS-4 / CQ-28). **Completion on a FRESH blind file by a second author: questions answered 149 · shrug 1 of 150; orders: as meant 73 · asked 21 · board refusal 18 · refused as meant 24 · honest refusal 8 · shrug 4 · misread 1 · executed-when-refusal-meant 1 (both recorded designs)** (two recorded designs filed by the judge as dangerous, pinned by name). ~~**▶ NEXT = Chunk 3b trimmed to what the census confirms** (CRT-11 — RS-6, RS-8, "follow Ney in"; RS-11 `take <province>`; CRT-9's `.gd` halves CQ-21 / CQ-24; CRT-10 led by SF-V4; SF-V8).~~ ✅ Chunk 3b landed the same day (the bullet below). **Step 4 is complete.**
  - A held-out census of about 300 lines, written without seeing the corpus, run keyless and keyed.
  - Resolution-aware confidence: a parse whose target matches nothing on the board never executes at 0.9. "march in support of Ney" charged a march to "In Support Of Ney".
  - Its census sizes Chunk 3b.
- **Chunk 3b, trimmed to what SF-CMD-1 confirms (≈3.0).** ✅ **LANDED October 3, 2026 — STEP 4 IS COMPLETE** (the user: *"Next is Chunk 3b, trimmed to what the census confirms … In build order"*; rules `SYSTEMS_REFERENCE.md` §89; landing record `COMMAND_ROBUSTNESS_SPEC.md` §12.16; pins `tests/test_crt11_the_second_name_is_heard.py`, `tests/test_rs11_take_and_sf_v8_the_named_corps.py`, `tests/test_crt9_the_state_speaks_first.py`, `tests/test_crt10_the_suggestion_is_honest.py`; sweep `tools/_sweep_chunk3b.json`). **The five the census confirms, built in the user's order:** (1) **CRT-11** — a second name is a ROLE, never a second order: RS-6's supporting phrasings and the HOLD arm's "Lannes, follow Ney in and back him up" are SUPPORT Ney at one action (`second_name.py`), RS-8's destroy clause arms the march's attack on arrival (ONE arrival-tail alternation for all five readers) and the explicit bad-odds interrupt names the muster; (2) **RS-11** — "take <province>" resolves to a marshal and a road the march law allows (`parser.rewrite_take_objective`, `strategic.nearest_lawful_marcher`); (3) **CRT-9's client half** — ONE pure probe `state_probe.order_state_refusal` read by the payload, both chip surfaces and the completer (CQ-21, CQ-24; CX-R2's `_state_gated` exemption deleted; parse harness EXIT=0, boot smoke 0 `SCRIPT ERROR`); (4) **CRT-10 led by SF-V4 as ruled** (§6.3 — the ask, the near miss, the tombstone line folding NPC-6, the bench line, the nothing-in-sight refusal; a description keeps its disclosed substitution); (5) **SF-V8** — a routed order word ("land") is never a marshal's name. **The exit (§5):** `score_run.py check` + `compare` over the eight touched arms, on this tree and on `e631f4bd` in a detached worktree — **one item flips, command C4 ✗ → ✓**; two instrument corrections, each pinned (C4's SF-V4 reading counts a battle as a substitution only BEFORE the player's answer; the ONE judge reads the march law's engaged refusal as the board's). **Step 4's exit also owed SR-7d-X2:** T5 measured — the best point falls 37 → 36 with the doctrines against the same tree's lever-down arm (35 through turns 10–40), **a pass** (`docs/audits/playtest_digests/sf4-q0-*`); T9, T10 and SR-7d-X1 homed to Step 7's SF-DC-1. **The census-unconfirmed rows, re-measured and homed** (the user's trim; GR9): CX5-L5-N2 was found closed by SF-CMD-1 part (ii) W7, lever-attributed; everything else listed below moved to Step 7's **SF-CMD-2**, which opens with the four misreads that still execute (CQ-33, CX5-L5-F7's `protect the rear`, NPC-9's and NP-X1's "Lorraine Myself"). SF-CL-1-D1 is put to the user as §6 row 16. `BASELINE_SERIES` and M1–M7 byte-identical. The rows as the spec first listed them, with their dispositions:
  - **CRT-6 "the retreat is a word":** CQ-33, CX5-L5-F3, F4, F5, F6, F7, N2, N4, N5 — N2 closed (W7); the rest → SF-CMD-2.
  - **CRT-8 "the Cabinet's rules on every road":** RS-7, CQ-36, CX-X3 (§6 rules the last) — all landed with SF-CMD-1 part (ii).
  - **CRT-9 "the state speaks first", as ONE state probe:** RS-4, RS-12, RS-15, CQ-21, CQ-24, CQ-28. `march_state_refusal` gains drill-lock and fortified arms, and those orders are refused free at issuance. — RS-4 + CQ-28 landed with SF-CMD-1 part (ii), CQ-21 + CQ-24 here; RS-12 + RS-15 → SF-CMD-2.
  - **CRT-10 "the suggestion is honest":** led by **SF-V4**, "a proper name asks", as ruled (§6.3, lever `A_PROPER_NAME_ASKS`). Then CX3-X2, CX3-X3, CX-BEHAV-1, PC15-13, and NPC-6 (the tombstone answer, folded into SF-V4's fallen-general case). — SF-V4 + NPC-6 landed here; CX3-X2, CX3-X3, PC15-13 and CX-BEHAV-1's census re-key → SF-CMD-2.
  - **CRT-11 "the second name is heard":** CQ-8, CQ-38 — the role half (RS-6, RS-8, "follow Ney in") landed here; CQ-8 + CQ-38 → SF-CMD-2.
  - **The parser riders (no CRT row named them):** RS-6, RS-8, RS-11, NP-X1, NP-X8, NP-X9, NP-X10, NPC-9, NPC-10, NPC-18, NPC-26 — RS-6, RS-8, RS-11 landed here; the rest → SF-CMD-2.

### Step 5 — the client stands (≈2.0)

- ~~**SR-8a VD-C "The Contingent"** (IQ7-D1), with:~~
  - ~~IQ7-X1: courting and cascades walk every lord (GR5);~~
  - ~~IQ7-X3: the recovery hint fires on a crossing, not on every tick;~~
  - ~~IQ7-X2: dead code deleted.~~
  ✅ **LANDED October 3, 2026** (gate record `VASSAL_DEEPENING_SPEC.md` §9.1 — R1–R12 ruled with research under the user's delegation; landing record §9.2; rules `SYSTEMS_REFERENCE.md` §90; pins `tests/test_vassal_contingent.py`). A loyal satellite in a shared war raises `income × 15 × loyalty`, rounded to 500, in [3,000, 12,000] (boot Holland 6,500 / Kingdom of Italy 7,500 / Switzerland 4,500), under an authored commander, on its lord's flag and its own payroll; its dead bleed it (1 a 500, capped 10 a tick); it marches home when the shared war ends and stands down crowned (+8), decimated (−5) or plainly home, then rests six turns; it walks out on a break; four exit hooks + a per-turn reconciliation; and (R12) its general is his court's, not the Emperor's — no rung on the glory ladder, no reward expectation. **Completion met:** on the commanded 3-seed run both boot contingents are called on turn 2 and march home when the war ends (Dumonceau home on turn 13 on every seed; Teulie decimated on austerlitz, crowned on marengo, taken on historical), and R1's regiments clause reads true for Holland and the Kingdom of Italy from turn 3. IQ7-X1 walks every lord; IQ7-X3 hints 11 / 8 / 6 against 14 / 17 / 16 with its lever down (measured first: 15 / 12 / 17 on the shipped tree); IQ7-X2 deleted. `BASELINE_SERIES` re-recorded ONCE, eighteen-arm attributed (the raise lever the sole mover, diverging at [6]; the unattended France ends with 6 provinces against 3).
- ~~**SR-8b + SF-AGD-1 "The agendas arm":**~~
  - ~~a carve through the settlement path to a Proclamation, on a played road;~~
  - ~~SF-M's TILSIT probe as its instrument;~~
  - ~~the formables gate flipping in play.~~
  ✅ **LANDED October 3, 2026** (rules `SYSTEMS_REFERENCE.md` §91.1–§91.3; pins `tests/test_sf_agd1_the_agendas_arm.py`). The AGD fixture (`tools/gen_agd_fixture.py`) is SF-M's TILSIT board with Posen still Prussian and Britain's war running; the arm (`score_run` arm `AGD`) takes Posen on loop 1 — the Duchy of Warsaw's gate term flips to met in play — then carves the Duchy through the table's own clicks (the driver's new `@` grammar), offers 6,000 gold, submits for review and makes peace with Prussia alone; Prussia signs and the Proclamation fires on turn 3. **Agendas C5 reads ✓ on the arm** ("carve terms stated 3x … Proclamation cards 1 (DuchyOfWarsaw); gate flipped to met in play"). Instrument correction, C3 and C5 alike: a gate term drops its "(currently X-held)" tail when met, so both key on `_gate_term_key`.
- ~~**SR-8c:** IQ7-D3 (a satellite design province France can grant), IQ6-D2's build as ruled (§6 row 12 — the volte-face's NOT-HUMILIATED clause reads the hegemon's bloc), and IQ6-D1's deck review — which also owns **AI-V §7a scene 1, the Confederation of the Rhine** (homed by SF-0, Sept 29): the German minors carry no deck, so the bandwagon gate has nothing to read; the review authors their deck or records the scene unreachable by design.~~ ✅ **LANDED October 3, 2026** (rules `SYSTEMS_REFERENCE.md` §91.4; pins `tests/test_sr8c_the_deck_review.py`). IQ6-D2 built as ruled (`A_CLIENTS_PARTITION_IS_THE_HEGEMONS`; the Bavaria-charged partition forecloses the door, a partition by a court outside the bloc does not). IQ7-D3: Holland's deck gains `ostfriesland` [East Frisia] (gate record R11 — Fontainebleau 1807), pinned unstaged by `TestT5TheDecksPrice`. Scene 1 **recorded unreachable by design** (`AI_INTENT_SPEC.md` §7a): the 1805 half is the boot state, the 1806 half was Napoleon's act — the player's in this game — and a German minor's covet design would make it an asker, never the scene.
- **Found in passing, fixed in the step (`BUG_FIXES.md` §Score Finish Step 5; rules `SYSTEMS_REFERENCE.md` §90.11):** **SF5-X1 (P1)** — a QUESTION answered a strategic interrupt: "should we attack?" fought Ney's bad-odds battle against Mack on the shipped boot (the typed interrupt route ran before any question guard — CRT-3's class, one road over); now it orders nothing and restates the interrupt's question with its answers. **SF5-X2 (P2)** — the route ran ahead of a standing hard stop, and a refused answer destroyed the interrupt and the standing order; the hard stop now outranks it. Pins `tests/test_sf5_the_question_and_the_interrupt.py`.
- ~~**VP-D9:** build the player's bribe verb, or strike it (§6).~~ STRUCK by ruling (§6 row 9, October 3, 2026).
- ~~**SF-LB-2c "The patient ask" (≈0.5, first — §6 row 15, ruled October 3, 2026):** the seeded patience on the court-to-court design ask; acceptance = the three strict xfails flip on the shipped tree, else the clause reads the war's turn and the miss is recorded.~~ ✅ **LANDED October 3, 2026 — the acceptance MET on the first attempt: all three strict xfails flipped on the shipped tree** (landing record §6.4's third addendum; rules `SYSTEMS_REFERENCE.md` §85.9). Prussia→Hanover's first opening now reads 5 / 7 / 7 / 5 / 8 / 5 / 13 across the seven seeds (was 5 ×6 / 9).
- **The exit (October 4, 2026; `score_run.py check` + `compare` over CMD-H / CMD-A / CMD-M / CMD-ULM / CMDR-H / AGD / VOLTE / OP / DL / HOLD / AIV; archive `docs/audits/score_runs/2026_10_04_step5/`):** **This step's flips — the same arms on `f3ce1b57` (Step 5's head) in a detached worktree against this tree:** agendas **C5 · → ✓** (the AGD arm, SR-8b — the arm exists only on this tree); AI aliveness **C5 ✗ → ✓** and **C6 ✓ → ✗**, both attributed to the contingents' board, not to the AI — with the raise lever down the fortify dither (Archduke John, CMD-H turns 9–12) and the 10 / 16 attack ratio both return, and C6's fall is the late war's start (CMD-M: turn 39 against 35; the early war reads 5 of 11 against 5 of 10); diplomacy **C3 ✓ → ✗**, attributed to IQ6-D2 as ruled and to the contingents' board — on the volte arm's own board Bavaria takes Bohemia and two more provinces and Austria's revanche hardens against France's bloc, so the ruling closes the door (both levers down: the beat fires as at `f3ce1b57`; either alone: it does not) — SR-7d-X1's re-script (Step 7, SF-DC-1) now carries both constraints and the RS-27 pin is re-seated with the raise lever down; vassals **C2 held ✓** after an instrument correction (the reader had read the turn's battles against a petition's quote — CMD-A turn 7, four French defeats, −6 for every satellite; the digest now records the loyalty tick and the reader reads the quote against the loyalty the tick started from, pinned). **Against the Sept-29 baseline** on these arms, all measured flips: · → ✓ agendas C5; ✗ → ✓ agendas C3, combat legibility F1, command C4, diplomacy C4, C6, the ending C6, first contact C1, C3, living balance C1, C2, C4, marshal drama C3; ✓ → ✗ AI aliveness C1, C6, combat legibility C2, first contact C4, marshal drama C1 (all but C6 attributed at earlier exits; none of them moves between `f3ce1b57` and this tree). The archived driver arms were re-run on the final tree — their digests are byte-identical to the first exit run, whose AIV arm the archive carries. No score claimed (§5).
- **Gates:** the full suite 29,238 passed, 5 skipped, 1 xfailed, 0 failed (24:31) on the final tree, run by hand before the commit. Census: defect 37 OPEN + 3 partial (IQ7-X1 / X2 / X3 FIXED; SF5-X1 / X2 filed FIXED; SF5-X3 filed OPEN, homed to Step 7), design 5 OPEN (IQ7-D1 / IQ7-D3 / IQ6-D2 BUILT).

### Step 6 — the chest and the sea (≈0.7, +1.0 if needed)

- ~~**SF-NAV-1 "The strangulation, played":**~~
  - ~~One arm that closes 13 of 26 ports, drives out the corps `continent_holders` names, holds SHUT OUT through a sitting, and records why Britain sues.~~
  - ~~If Continental System tier 2 stays unreachable, the A2 anchor goes to the user.~~
  ✅ **PLAYED October 4, 2026 — the A2 anchor GOES TO THE USER (§6 row 17)** (the user: *"finish step 5 commit do a quick check on step 5 then do step 6"*; memo `docs/audits/SF_NAV1_STRANGULATION_2026_10_04.md`; rules `SYSTEMS_REFERENCE.md` §92; pins `tests/test_sf_nav1_the_strangulation_played.py`). The arm `tools/playtest_scripts/sf_nav1_strangulation.json` (benchmark `NAV1-H/A/M`, read by the new `tools/sf_nav1_strangulation_probe.py`): France keeps its war with Britain alone, takes Lisbon, Rome and Naples, holds the Normandy beach against Moore's crossing and hunts every British corps that lands. **SHUT OUT holds on a played board for the first time** — historical turn 11 (14 of 26 ports), marengo turns 13–15 (13 of 26), after Soult took Britain's whole bench (Paget, Wellesley, Shrapnel) — **but never through a sitting**: Spain's war with Britain ends on turn 16 on every seed by the exhausted-pair exit and the closure falls to 10–11; the Tilsit lever that could replace those ports (a peace that enrols the beaten court) is settlement-tier and cannot be sealed while Britain fights on in the same war. **Tier 2 is unreachable** (peak 14 of 26), so the A2 anchor goes to the user with a recommendation (the Tilsit clause on a separate peace). **Why Britain sues:** on turn 8 on every seed, at war exhaustion 70–79, from the war's own +8 a turn — the System adds at most +1. **Riders:** SF-V6 the descent arm re-staged (commission on loop 4 with the purse spared, Oudinot to the Normandy yard, sail on loop 5 — lands 5,000 at 75 in 100 and takes Munster; the naval C3 reader learns the capture question); SF-V7 found an INSTRUMENT defect — on a turn whose end fights no battle the quote equals the bill to the gold, and economy C3 had compared it with the next turn's forecast (the driver now records the end turn's `applied_bill`, its own Butcher's Bill included, and the reader names the one gap the game owns: the enemy phase fights before the bill is drawn); SF6-X1 found playing the descent arm — a confirmed expedition ends the corps' standing order; SF6-X2 found by the exit — the SEA arm's landing had drifted out of a yard's reach since the baseline (naval F2), re-staged to the Normandy yard. **SF-ECON-1** stays conditional: its trigger is read after Step 7b, and economy C6 reads ✓ on this exit (3 of 3 samples name an affordable purchase). **The exit:** the touched arms on this tree and on `d1018208` (Step 5’s quick-check commit) in a detached worktree, archive `docs/audits/score_runs/2026_10_04_step6/` — **economy C3 · → ✓** (unmeasured on Step 5’s tree, whose driver kept no bill; ✗ at the baseline; quoted == billed on turns 10 / 30 / 40 of CMD-H, turn 20 explained by its enemy phase’s 278 gold of materiel), **naval C3 ✗ → ✓** (the descent arm quotes its odds, names the lever and takes Munster), **naval F2 ✗ → ✓** (SF6-X2; ✓ at the baseline, held); no other item on the touched pillars moved; item flips only, never a score (§5). **Gates:** ruff clean; the full suite 29,285 passed, 5 skipped, 1 xfailed, 1 failed (24:51) by hand on the tree before the last two pin edits — the failure the FA-85 staging pin, collected before its conscious re-pin — then the two touched files 19 + 45 passed (the final tree: 29,287 passed, 5 skipped, 1 xfailed under the pre-commit hook); the mutation sweep `tools/_sweep_step6.json` 17 → 17 killed, 0 INERT, 0 BROKEN. Census: defect 36 OPEN + 3 partial (SF-V6 / SF-V7 FIXED; SF6-X1 / SF6-X2 filed FIXED), design 6 OPEN (SF-NAV-1-D1 filed, the user’s).
- **SF-ECON-1 "Acts of the Empire", only if economy C6 still fails after Step 7b:**
  - two or three late acts per deck, priced for the turn 15–30 chest;
  - they turn gold into endgame progress, not income;
  - its own gate comes first (§6).

### Step 7 — what the wire says, the screen says (≈2.0 + the user's eyes)

- **SF-CMD-2 "The census's remainder" (≈1.5; homed by Step 4's exit, October 3, 2026):** the Chunk 3b rows SF-CMD-1's blind census did not confirm, re-measured at the exit (`SYSTEMS_REFERENCE.md` §89.7), each keeping its done-when and pin. **It opens with the four misreads that still execute:** CQ-33 (`with the Guard` → a 2-action HOLD), CX5-L5-F7 (`Ney, protect the rear` → a 2-action HOLD and a march), NPC-9 (`I will march to Lorraine myself and attack Mack` → a march to "Lorraine Myself") and NP-X1 (the same phantom target on a board with no Emperor). Then CRT-6's CX5-L5-F3 … F6, N4, N5; CRT-11's CQ-8 + CQ-38; RS-12 (the what-if reads `state_probe.order_state_refusal` — combat legibility C4 reads it) + RS-15; CRT-10's CX3-X2, CX3-X3, PC15-13, CX-BEHAV-1's census re-key; NP-X8, NP-X9, NP-X10, NPC-10, NPC-18, NPC-26; and SF-V9's HOLD worklist as re-read at the exit (the action pre-gate's nameless refusal — five of the HOLD arm's eleven misses; the contraction read as an address; the levy for a named marshal raised where he stands; "in case" read as a condition; the sponsorship idiom; the marshal as a lower-case subject). Completion: every row's done-when at `POST /command`, corpus rows, and command C3 re-read on the HOLD arm.
- **Step 7's progress (October 4, 2026; the user's brief: *"take it in this order and stop at a clean commit after any slice"*):**
  - ✅ **Slice 1 — §6 row 17 ruled** (gate record §6.6, FOR USER CONFIRMATION — the Tilsit clause; research memo `docs/audits/SF_NAV1_D1_THE_A2_ANCHOR_2026_10_04.md`) with the housekeeping and SF7-X1 (commit `06686cc4`).
  - ✅ **Slice 2 — SF-CMD-2's head LANDED October 4, 2026** (rules `SYSTEMS_REFERENCE.md` §93.2; pins `tests/test_crt6_the_retreat_is_a_word.py::TestTheGuardIsSometimesANoun` + `::TestAPositionIsNotAPlace` and `tests/test_sf_cmd2_the_head.py`; corpus rows `sfcmd2-*` (10); sweep `tools/_sweep_sf_cmd2_head.json` 13 → 13 killed, 0 INERT, 0 BROKEN). **The four misreads that still executed now read as meant at `POST /command` on a fresh 1805 boot**, each reproduced before a line was written: CQ-33 (`Ney, move to Paris with the Guard` marches, `Ney, scout Swabia with the guard` scouts for 1 action, `recruit 5000 men for the guard` raises with the Emperor — `parser.rewrite_guard_company`); CX5-L5-F7 (`Ney, protect the rear` / `guard the rear`, `Lannes, guard the retreat`, `Davout, protect our flank` are the in-place HOLD — `strategic_parser._POSITION_NOUN_RE`); NPC-9 (`I will march to Lorraine myself and attack Mack` and `I will take the field myself and march to Lorraine` are the Emperor's march to Lorraine) and NP-X1 (with no Emperor, `Ney, march to Lorraine myself` marches to Lorraine and `I will march to Lorraine myself` asks which marshal — `parser.strip_self_markers`); **and SF5-RV13** (`attack, what are you waiting for` with and without "?", `hold, do as I say`, `do what I say: attack` answer Ney's interrupt; `Ney, do as I say and attack Mack` attacks on the general road, where it had the desk's shrug — found in the slice; real questions still order nothing — `clause_guards.strip_emphasis`). The parser and command families green (6,480 pins), corpus 887 of 887; `BASELINE_SERIES` and M1–M7 byte-identical by construction (the AI never parses text).
  - ✅ **Slice 3 — §6 row 16's build LANDED October 4, 2026, alone in its own commit** (the user's ruling: read the lead's coordination on the FIELD; rules `SYSTEMS_REFERENCE.md` §93.3; pins `tests/test_sf_cl1_d1_the_coordination_is_read_on_the_field.py` (9); sweep `tools/_sweep_sf_cl1_d1.json` 10 → 10 killed, 0 INERT, 0 BROKEN (the first sweep found one INERT row, and it was right: the lead's explicit adjacency exclusion duplicated SF-CL-1's assumed-present rule — the line is deleted, the row re-aimed at the rule that does the work); evidence `docs/audits/score_runs/2026_10_04_sf7_s3/`). **Conscious re-seats, each measured:** the SF-CL-1 mirror pin (Davout beside Ney now prices on the field; lever down keeps 0); GEV-D1's completion test (realized reads the resolver's own `massed_strength` — the test's reconstruction read each arrival's share outside the stamped context: 6 of 11 within on it, 9 of 11 on the resolver's figure, 9 of 11 on both with the lever down); VP-R1 (c)'s glory staging (John 20,000 → 60,000, Mack sent to Bohemia — four answering corps lift a 20,000-man John to 'even'); the School's no-laurels controls (`test_fa_s16_d4…` — the shipped lesson crowns nobody over 12–20 turns, so the controls run where it crowns and the guard's pin runs on both boards); the IQ-5 family (a third board fixture beside its doctrine and IQ5-R1 ones — its subject is the surface, never the coordination — plus one class reading the labels on the field); RS-27 (the field read down, measured: shipped 0 beats, field down the beat at turn 25, gate down alone 0); the strategic redirect pin seeds its own dice (an RNG-shaped attack: Ney wins and advances on 37 of 40 seeds before, 30 of 40 on the field read; seed 1 on both); the WO slice-9 / slice-10 board pins (`tools/_coord_field_wo_attribution.py`: with both levers down the VD-C figures return); the four `BASELINE_SERIES` chain pins. **What it does:** the resolver hands both sides' context `field=<the battle province>`; a lead attacking from next door is read where his arrivals stand — counted present there, kept out of the adjacent count, which is now read around the battle province (the adjacent-support docstring's own wording); the defender stands on the field already and is unchanged. **The forecast follows in lockstep:** `_priced_coordination` prices every marching joiner present on the field and keeps an arriving gun corps IN the adjacent count, as the resolver keeps him (before that line the preview priced the gun nowhere — a ceiling 693 men short on the staged board); and the glory gate's `muster_odds` reads under the preview's own priced context (SF7-X4: it had read whatever stamps the last battle left). **Scope decision, FOR USER CONFIRMATION:** the cavalry charge and the garrison assault keep the lead's province — neither rolls reinforcements (`_calculate_reinforcements` has one caller, the field battle), so no corps answers them and nothing relocates; the row's defect does not exist on those roads. **The series — ONE re-record, two levers, attributed** (`tools/_coord_field_series_arms.py` → `_final.json`): arm 0 byte-identical; the gate's lever alone byte-identical (46 gate reads, the same band either way on the old reading); the field read alone diverges at [6] (the passive France holds 16 provinces at turn 40); both diverge at [6] and part from the field read alone at [32] (three gate reads, Austria 2 / France 1); **the passive France ends turn 40 with 4 provinces against 6 on arm 0** — two fewer, a late swing on this seed. The same-board shadow (arm 0's own 40 turns, both readings at each of the 44 resolver reads with a field next door): lone AI attacks from next door lose the credit of friends who never marched (Austria's lead bonus falls on 16 of 28, mean −1.5 points; Britain 8 of 12, −2.3); France's four converging attacks rise (mean +15.2; Murat at Swabia on turn 21: +2% → +25% with five arrivals); the arrivals, never stamped before, carry their own coordination into their committed share. **M1–M7 byte-identical** (the harness re-read; in band). **Item flips (§5) — the matched set CMD-H/A/M, AIV, FLD, OP, DL on `b127e41e` and on this tree, each lever down in turn:** the gate's lever alone flips nothing; the field read alone flips all five — **combat legibility C2 ✗ → ✓** (favorable battles out-bleed 12 of 12), **UI/UX C4 ✗ → ✓** (at most 3 blocking popups in one end turn on OP), combat legibility C3 ✓ → · (no capital taken after a field battle on these arms), **economy C6 ✓ → ✗** and **AI aliveness C5 ✓ → ✗**. Neither ✗ is the coordination itself: C6 is a pre-existing counsel defect the new course exposed (SF7-X3 — with the whole army in Germany, "what can I do" names nothing to buy against a 51,120-gold chest), and C5 is the item's own wording (Archduke Charles fortifies on arrival, breaks camp to attack, and fortifies on arrival in another province — §6 row 18, the user's). Commanded France at turn 40: **28 / 29 / 29** provinces (28 / 28 / 28 on `b127e41e`) — living balance F1 held. **Found in passing:** SF7-X2 (the expected figure prices an arriving gun at nothing; the battle counts him whole) and SF7-X3, both homed to **slice 3b**; SF7-X4 fixed here.
  - ✅ **Slice 3b — the two rows slice 3 found, LANDED October 4, 2026** (rules `SYSTEMS_REFERENCE.md` §93.4; pins `tests/test_sf7_3b_the_gun_and_the_purse.py` (9); sweep `tools/_sweep_sf7_3b.json` 6 → 6 killed, 0 INERT, 0 BROKEN). **SF7-X2** — an arriving gun is weighed by his own arrival roll (`combat_executor.AN_ARRIVING_GUN_IS_WEIGHED_BY_HIS_ROLL`): the resolver's Gate-4 block sums every gun that answered at full weight and the expectation had priced him at nothing (Lannes as a gun corps, every promised corps arriving: expected 61,882 → 84,005 against 88,684 massed; the ceiling unchanged); his muster row states his odds. **Conscious re-seats (the hook found four, each attributed to the lever by re-running it down):** PT-A's `test_artillery_is_priced_at_zero_because_it_never_relocates` asserted the premise this row measured false — flipped to `test_an_arriving_gun_is_weighed_by_his_roll` (the roll-weighted share up, 0.0 down); three AI fixtures on the legacy world parked Drouot's 25,000 guns beside the battle (at Paris beside Belgium; `_legacy` parks the roster at Bordeaux, which borders Paris) and the AI now prices him as the battle counts him, so an aggressive Uxbridge retreats at 0.64 and a cautious Wellington keeps his free blow — honest on that board; each test's subject is not the gun, so Drouot is sent to Marseille (`test_enemy_ai_behavior.py::…::test_encirclement_aggressive_attacks`, `test_fa_slice4_…::TestTheCounterPunchIsPriced`, `test_fa_slice4r_…::TestTheFieldPricesTheTargetToo`); the GR5 half is pinned where they found it (`TestTheAISeesTheGunToo`: the counter-punch declines with the gun next door, strikes with the lever down). **SF7-X3** — AAR-18's counsel half: with no corps on our own soil the counsel's build line reads the desk's corps-free finder (`counsel.THE_BUILD_LINE_NEEDS_NO_CORPS`), so CMD-H turns 20 and 30 name a supply depot and a fortification in Paris. **Gates:** `BASELINE_SERIES` byte-identical with the reach counted (`tools/_sf7_3b_series_arms.py`: 0 gun weights read and 0 corps-free build lines served on the ambient board), M1–M7 byte-identical. **Item flips (§5), the same matched set on slice 3's tree and this one:** **economy C6 ✗ → ✓** (9 of 9 samples name an affordable purchase); nothing else moves.
  - ✅ **Slice 4 — §6 row 17's build, the Tilsit clause, LANDED October 4, 2026; the done-when is NOT met (1 of 3 seeds) and comes back to the user** (gate record §6.6 + its landing addendum; rules `SYSTEMS_REFERENCE.md` §93.5; pins `tests/test_sf_nav1_d1_the_tilsit_clause.py` (58); sweep `tools/_sweep_sf7_s4.json` 26 → 26 killed, 0 INERT, 0 BROKEN (the first sweep found two pins INERT and both were right: a member is refused by the join's own idempotency, so the predicate's re-run is pinned on a court only it refuses); arm `tools/playtest_scripts/sf_nav1_tilsit_road.json` (benchmark `NAV1T-H/A/M`); evidence `docs/audits/playtest_digests/sf7s4-tilsit-{historical,austerlitz,marengo}/`). The clause, ONE membership write, ONE predicate, the price in both dialects, the separate peace carrying it, the exit at the WAR transition, the surfaces (§93.5); **SF7-X5** (the plain forced alliance joined the System anyway) and **SF7-X6** fixed; **SF7-X7** filed (a separate peace silent on the French soil it leaves the enemy, homed to the Chunk 9 slice). **Played, per seed:** **historical** — Russia signs on turn 12, Austria on turn 13; SHUT OUT holds **turns 14–30, 17 consecutive turns**, peak **16 of 26 (tier 2, reached for the first time)**; Austria is drawn back to war by the next coalition on turn 20 and the line holds through its exit (16 → 15). **austerlitz** — Russia turn 12, Austria turn 13; peak 16 (tier 2) on turn 14; **SHUT OUT never** — British corps stand on the Continent all 30 turns: Moore lands 25,000 at Guyenne by turn 10 and campaigns in France's south-west (Bearn, Cartagena, Guyenne, Maine) with Wellesley and Shrapnel, and after Austria's separate peace Austria's closed frontier (Champagne, Burgundy and Berry — the status-quo peace left them to it) refuses every French march toward him (SF7-X7); Russia is drawn back to war on turn 17 (closure 13 → 11) and re-signs on turn 24. **marengo** — Russia turn 12, Austria turn 19; peak 16 (tier 2) on turns 13–15; **SHUT OUT never** — 13 of 26 holds turns 16–21 while Shrapnel stands with the Austrians (Hungary, Vienna), and the turn he is gone (22) Russia's return to war takes the closure to 11. The attribution, every seed: the next coalition forms 5–9 turns after the separate peaces (each signing adds the System's +10 alarm) and draws a signatory back to war, and the exit takes its ports — historical held because it had three ports of margin over the line; the other two did not. The 50% line is not tuned (§6.6). **The NAV1 re-read** (Step 6's arm, unchanged; archive `docs/audits/playtest_digests/sf7s4-nav1-reread/`): historical 11 of 26 / never, austerlitz 12 / never, marengo 14 / turns 12–15 (4) — **identical on the pre-slice tree `c5ef3a60`** (slice 4 is inert on it: the System is empty all game). Step 6's own table (14 / turn 11; 12 / never; 13 / turns 13–15) reproduces exactly at slice 2's commit `b127e41e`, and historical already reads 11 / never at slice 3's `ee743a3c` — slice 3's field read moved this arm's battles. **Pins re-seated consciously:** the fourteen campaign-log count pins (172 → 173, `continental_system_membership`); `tests/test_settlement_guided_terms_slice_v.py`'s D5 copy-boundary walk (19 → 20 guided reasons — the new `continental_system_talleyrand` reason is walked and inside the boundary; the hook's first run caught it: 1 failed, 29,442 passed, 5 skipped, 1 xfailed). **Gates:** `BASELINE_SERIES` byte-identical across four arms with the reach counted (`tools/_sf7_s4_series_arms.py`: the System has no member in forty turns, 0 joins, 0 exits), M1–M7 byte-identical; parse harness EXIT=0 (incl. `main.tscn`). Census: defect 32 OPEN + 3 partial (SF7-X7), design 4 OPEN.
  - ✅ **Slice 5a — SF-CMD-2's remainder, the parser's words and the second name, LANDED October 4, 2026** (rules `SYSTEMS_REFERENCE.md` §93.6; pins `tests/test_sf_cmd2_the_remainder.py` + `tests/test_crt11_the_second_name_is_heard.py::TestTheSecondNameIsRelayed` / `::TestTheSecondRewardIsHeard` / `::TestTheLiveSplitterKeepsV2_61` + the CX-5 class rebuilt in `tests/test_cx1_a_question_never_orders.py`; corpus `sfcmd2r-*` (12 rows, 888 of 888); sweep `tools/_sweep_sf7_s5a.json` 30 → 30 killed, 0 INERT, 0 BROKEN). **CQ-8 / CQ-38, the second name is heard:** the first man takes the order; the second man's own order rides CR-7-3's relay for the seal, priced, never sent by the game (`Ney and Soult, attack Mack` → AP 4 → 3, `relay_command` "Soult, support Ney", 1 action — the row's "2 actions" predates SR-2e); a man the muster counts, or whose rente would change nothing, is acknowledged and not relayed; his own order survives the first's refusal; the live road's "coming in a future update" promise is gone; `parse_multiple` deleted as decided. **The parser's words:** the retreat carried out and continued (F3 / F4), the shrug that says how it read a retreat (F5), the pursuit names the man (N4), the disclosure keeps its tense (N5), the inflected order (NP-X9, every marshal), the dead fallback (NP-X10), the anchor guard (NP-X8), talks are not a hold (NPC-10), "the Emperor" a referent (NPC-18), riding down a foe and the court named beside a province (NPC-26); **SF7-X8** ("No Prussia force") found and fixed. **F6:** the CX-5 class re-pinned at the parse on the guard that holds each row. **The sweep caught three weaknesses of the slice's own, all repaired:** an end-to-end pin satisfied by the retreat shrug (which names the retreat), a dead second copy of the continued-retreat rule, and a splitter guard no pin reached (one man named twice). **Built first and removed:** a `moves` keyword in the mock chain read narration ("Mack moves to Swabia") as a move. **Re-seated consciously:** CR-7-3's address-comma pin (`tests/test_cr7_3_the_tail_comes_back.py::TestTheBareComma`) — a LIST of addressees now carries the second man's support on the relay's `dropped_sequel` carrier as kind `second_name`; the comma still never cuts the order; the five `parse_multiple` pins retired onto the live splitter; the IQ-9 "No Prussia force" pin (SF7-X8); `backend/ai/routed_order_words.py` regenerated (+ `continue`, `resume` — the continued-retreat arm), as CX-R1 requires after a parser keyword change. **Gates:** `BASELINE_SERIES` + M1–M7 byte-identical (every path is on the typed road or gated to the player's nation; the ambient arm types no order). Census: defect 18 OPEN + 3 partial, design 4 OPEN.
  - ✅ **Slice 5b — SF-CMD-2's remainder, part b: the desk, the map's names, the HOLD arm, LANDED October 4, 2026** (rules `SYSTEMS_REFERENCE.md` §93.7; pins `tests/test_sf_cmd2_the_remainder_5b.py` + the two row-named pins (`test_command_robustness_cr2_clarification.py::test_no_marshal_question_for_a_destination_the_map_lacks`, `test_wo_slice12_copy_sweep.py::TestWO45TheShortNameGuess::test_a_printed_guess_keeps_the_first_letter`) + the help census re-keyed in `test_cx3_the_predictor.py`; corpus `sfcmd2r-*` (+7) and the help's two re-keyed sentences `sf7-s5b-sponsor-*` (+2) — 897 of 897; sweep `tools/_sweep_sf7_s5b.json` 24 → 24 killed, 0 INERT, 0 BROKEN (the first sweep found one pin INERT and it was right: the mock parser corrects a typo before the clarification sees it, so the branch is pinned directly with a raw typo)). **RS-12** the what-if reads the order's state first (the screens' own `state_probe`); **RS-15** the build line finds ground that takes a building; **CX3-X2** no "Which marshal?" about a place the map lacks; **CX3-X3** a printed guess keeps the first letter (the five filed + Jena print none; Venetia → Vienna and the close typos stand; "Nearby:" retired); **PC15-13** the march road names the roads out of the marshal's province; **CX-BEHAV-1** the help census inverted onto the ONE judge — it found four board refusals the judge did not know and the manual teaching a licence the boot refuses (now Hanover); **SF-V9** the HOLD worklist closed (first contact C1 0 shrugs of 20; the four remaining misses fixed — the contraction, "get me some cavalry", the trailing "in case", the passive build). **Found driving it and fixed:** SF7-X9 (an unknown scout target ran the bare scout for an action), SF7-X10 (a condition clause's foe became the order's destination), SF7-X11 (a levy named for one province raised in another — gold spent; the ruling that re-opens SR-3b's recorded boundary is §6 row 19, FOR USER CONFIRMATION). **Re-seated consciously:** the CA8 low-confidence pin ("Nearby:" → the guess as a question) and its multi-word sensitivity half (now shown with the first-letter lever down); `routed_order_words` regenerated (+ get, find, fetch, see). **Gates:** `BASELINE_SERIES` + M1–M7 byte-identical (typed-road and player-gated paths; an exact name — every AI order — never reaches the matcher); the 146-file regression subset green. Census: defect 12 OPEN + 2 partial, design 4 OPEN.
  - ✅ **Slice 6 — SF-DC-1 "Nothing unnamed", LANDED October 4, 2026** (rules `SYSTEMS_REFERENCE.md` §93.8; the instrument `tools/_doctrine_census.py`, installed by `tools/playtest_driver.py --doctrine-census`; pins `tests/test_sf_dc1_nothing_unnamed.py` + RS-27's two pins re-seated + SR-8c's client pin; sweep `tools/_sweep_sf7_dc1.json` 24 → 24 killed, 0 INERT, 0 BROKEN on its first run; evidence `docs/audits/playtest_digests/sf-dc1-*`; the volte door read turn by turn by `tools/_volte_door_probe.py`). **T9 — PASS:** after every POST every marshal's `_doctrine_terms` equals a fresh `doctrines.derive_terms` — 0 drift in 11,448 marshal checks over 438 POSTs (the Jena road 5,237 / 191, CMD-H 6,211 / 247). **T10 — measured before and after, historical seed:** the census captures each doctrine effect where the mechanics decide it (a roll the bar shift decided, a scaled rout, the standing attack and defence rows, a supply bite re-read with the clause off, a draft priced by the clause) and judges it against the response — visible (the player a party, or the fog filter let it through; an arrival needs the reinforcer seen) and named (the line on a route whose CLIENT function reads the key — the renderers read from the `.gd` source, comments stripped). **Before: 44 visible effects unnamed — 39 dropped by the client and 5 never named on the wire** — SF7-X12 the enemy-phase dialog drew neither `doctrine_lines` nor `morale_line` (6 arrivals), SF7-X13 it read the levy's note off `ai_action` (33 of 33 Austrian levies), SF7-X15 the attrition line never named the clause (5 bites); SF7-X14 (a standing order's battle drew no report) found by the census's model of the client. **After: 53 of 53 named, 0 phantom lines, six distinct moments** (Austria: the Hofkriegsrat, the Hereditary Lands; France: the corps system, living off the land; Prussia: Frederick's Drill; Russia: slow to concentrate); the trajectories are byte-identical before and after (display only). **CMD-H: T10 PASS. The Jena road: T10 MISS on per-court coverage alone, attributed** — Britain fought in the player's sight once, attacking (Paget on Massena); its clause is a defence clause and fired only in Castanos's attacks on Wellesley in Spain, out of sight, and no British levy stood in sight. **SR-7d-X1 — the volte arm reads on the shipped tree with no lever, through §6 row 20:** the re-script was played eleven ways and on every road Bavaria took a second Austrian province before the league was spent, so IQ6-D2's bloc reading closed the door; ruled (FOR USER CONFIRMATION) that the battlefield arm reads the hegemon's vassal chain (`emergent_designs.AN_ALLYS_WAR_IS_ITS_OWN`), the arm unchanged — per seed: historical, the beat on turn 27 (peace turn 11, courted to 42 by turn 26); austerlitz, turn 24; marengo, none (at war again on turn 23). **Re-seated consciously:** RS-27's in-window pin runs with no lever; its arm-0 pin carries the new lever down with Step 3's; SR-8c's revanche pin charges a true client (the Kingdom of Italy). **Gates:** `BASELINE_SERIES` + M1–M7 byte-identical (the passive France courts nobody; the supply line is display only); parse harness EXIT=0 (62 scripts, 9 scenes), boot 0 SCRIPT ERROR. Census: defect 11 OPEN + 1 partial (SR-7d-X1 and X2 closed; SF7-X12 … X15 filed FIXED), design 4 OPEN.

- **SF-DC-1 "Nothing unnamed" (≈1.0; homed by Step 4's exit):** SR-7d-X2's remainder — T9's driven-route drift pin and T10's unnamed-effect census, one instrument for both (an in-process transport observer in the playtest driver comparing every marshal's `_doctrine_terms` with `doctrines.derive_terms` after every POST, beside a census of doctrine effects against the named lines on the Jena road and one commanded arm) — and SR-7d-X1, the volte arm re-scripted for the doctrine board (a courted peace with Austria the beaten party — and, since Step 5's exit, on the contingents' board with no Austrian homeland in France's bloc's hands, IQ6-D2 as ruled) so SF-R reads diplomacy C3 on the shipped tree. Completion: T9 and T10 in the landing record with a pass or an attributed miss; the in-window volte pin runs with no lever. ✅ **LANDED October 4, 2026 — Step 7 slice 6** (landing record above): T9 PASS; T10 PASS on CMD-H, an attributed coverage miss on the Jena road (Britain's clause fired only out of sight); the volte pin runs with no lever through §6 row 20.
- **Chunk 9's own items:**
  - the settlement panel's contradictions, on screen;
  - the client half of the auto-end confirm;
  - the counter-punch rail row;
  - the standing sign-offs: the end screen's four registers, F3's six surfaces, F5's header, the Congress surfaces, VP-R1's muster rows, the RF-4 laws frames.
- **Rows:**
  - S5-4: at its cap, the dialogue queue overflows to the mailbox (push and preempt together).
  - WO-V-D1: the region panel's actions fold.
  - WO-V-D2: no "Intel: Partial" on our own capital.
  - WO-D14: the greyed road names its DP price.
  - The predictor polish: CX3-R2, R4, R5, R6, R9, R10, R11, R12.
  - EAS-2's client half.
  - SF5-X3: a client's general is styled "Marshal" (the capture dispatch's "Marshal Teulie has been taken"; 90 `Marshal {…}` templates) — a style helper read by every template, with a census.
- **Frames:** the IQ-10 frames re-shot at both Interface Scales for every surface Steps 1–6 touched, plus one 5-turn Mode C session.

### Step 7b — The front page of the peace (≈2.5; added September 28, 2026, the last build step before the re-score)

> The user: *"look for one more way to increase score and spec it on the end before rescore."* Two read-only analyses at `c2dfe40b` looked from opposite ends — the checklist's unassigned gaps, and the reviews' unanswered complaints — and reached the same place: **the quiet middle of a winning campaign is not empty, it is untold.**

**The evidence.**
- **Narration's FLOOR fails, and no step fixes it.** The three commanded arms, re-run with the dispatch headline logged per turn:
  - **58 of 120 turns carry no headline at all:** 3 on historical, 25 on austerlitz (turns 17–41), 30 on marengo. On a quiet peace `_build_headline` returns None, so narration F1 fails and the pillar is capped at 6.0. As planned, the mandate would miss on narration for certain.
  - **Where a lead exists, two standing nags alternate:** Lannes's arrears (`estate_eroding`, the script never pays him) on 20 turns, the levy on 10. The worst 10-turn window is 7 of 10, so C1 fails.
  - **RS-D2 alone cannot fix it.** The standing-lead allowance is kept per class, so the lead simply passes from one nag to the other.
- **The news was there.** On `rs0928-cmd-historical`, across turns 11–40 of peace:
  - London and St Petersburg granted Austria **six sponsorships against France**, 300–500 gold a turn;
  - Sweden signed a defensive alliance with Austria;
  - Sweden's allegiance was in play five times.

  None of it ever led the dispatch.
- **The chest can already buy the number that decides the next league.** That number is a court's relation against −10 in `qualifies_for_coalition`. A design buy-off gives +5, a licence +5, and Talleyrand's missions add every turn — but nothing tells the player. This is RS-D3's "nothing left to buy" answered in the period's own terms: Napoleon's subsidies and bribes.
- **The Armed Peace (§6.2) was admitted "only because it is visible and can be played against".** Its planned surfaces are threat rows and the war room. This step puts it where the player reads every morning, with prices.

**Part 1 — Every morning has a front page** (SF-NAR-1, ≈1.2; lever `dispatch.EVERY_MORNING_HAS_A_FRONT_PAGE`).
- **A lead for a quiet turn.** When no event candidate exists, the turn's biggest diplomatic row leads: a sponsorship, a treaty between AI courts, allegiance in play, a law enacted abroad, a design shift. Such a row existed on 25 of 29, 12 of 24 and 25 of 28 quiet turns on the three seeds.
- **Otherwise, a "state of the realm" line leads.** It is built only from existing single sources and names only what changed:
  - the titled count and its roads (`congress.titled`, `game_end.title_roads`);
  - the laws' forecast (`reforms.lapse_forecast`);
  - the alarm's move (`coalition.displayed_threat`);
  - the Armed Peace's fuse.
- **One lead allowance for the whole standing family.** `STANDING_LEAD_MAX` counts across every `STANDING_HEADLINE_CLASSES` entry, kept as a new key in the already-serialized `headline_lead_memory` (no new field). A standing crisis keeps its escalating sub-beat every turn it stands. It retakes the lead only when its stakes change: a new tier, a flip, or a war.
- **A rotation guard.** No class leads more than 4 of any 10 turns unless it is that turn's event news.
- **Absorbed and fed.** RS-D2 (the levy) becomes a special case of this rule. RS-17's summonable and near-miss classes feed the page.

**Part 2 — Europe arms in plain sight** (SF-LB-3, ≈1.3; lever `coalition.THE_LEAGUE_IS_SEEN`; display only, GR6). *Renamed October 4, 2026 (Step 7's housekeeping): this part was drafted as "SF-LB-2" on September 28, before Step 4's §6.4 build took that name for "The Defenceless Prize"; nothing else changes.*
- **One pure reader, `coalition.league_forecast(world, target=None)`.** One roster pass, cached per turn (GR8), written on the target (GR5). Per court it reads:
  - whether `qualifies_for_coalition` holds;
  - the relation shift that would lift it above −10, confirmed through `relation_shift=`;
  - its live sponsorships against us (`instruments.live_sponsorships_for`);
  - the Armed Peace's fuse, or `world.coalition_brewing`;
  - the titled provinces its war would reopen, by `break_signed_titles`' own rule.
- **The price to keep each court out.**
  - Talleyrand's turns to −10, stepped on the tick's own arithmetic in ONE helper shared with RS-D1's cost-in-turns quote (§6.1 item 4);
  - plus `compute_buyoff_price`.
  - A court out of time, or one refusing the Congress, is told as such.
- **Four event headline classes:** `league_paid`, `league_bound`, `league_joins` and `league_fuse` (the fuse at 8, 4 and 2 turns left, never a streak).
  - They weigh 58–66: above the standing nags, below every wound (CA8-D6).
  - They are the "other news" the front page and PC-7's yield rule need.
- **`league_rows`** on the dispatch's coalition section and on the Diplomatic Ledger's Balance of Europe tab. `diplomatic_ledger.gd` prints them in place of the bare "Nations That Would Join Coalition" list.
- **The desk.**
  - It answers "who will march against us?" and "what keeps Austria out?".
  - At peace, "what can I do" names the cheapest keep-out order.
  - RS-14's alarm answer reads the same reader.
- **Rider:** the campaign log's raw "AI-AI treaty: Sweden and Austria (Defensive Alliance)" becomes prose.
- **Limits:** no AI consumes the reader, and no AI courting rung is built or promised (GR9).

**What the player reads** (Berthier's voice; figures illustrative):
- "Sire — London now pays Vienna 500 gold a turn. The Fourth Coalition has its paymaster; it lacks only its armies."
- "Sire — Europe has watched us twelve quiet turns. At this pace the courts consult on turn 32: Austria, Russia, Britain, Sweden and three lesser courts."
- "Austria — relations −36. If she marches, the Treaty of Vienna is torn: Bohemia, Tyrol and Vienna reopen. Talleyrand brings her to −10 in 4 turns (4 DP); buying off her design costs 1,300 gold. A league without Vienna is a league without an army."
- "Russia — relations −61. Courtship needs 9 turns; the courts consult in 6. She will march."

**Honesty rules.**
- A smaller league may be promised, never no league: six lesser courts sat below −10 on the turn-24 save.
- Army sizes appear only through `_format_army_strength` (fog).
- A standing crisis is never suppressed (PC-7), and F2's intent-line cap holds.
- IQ-3's gate and the Armed Peace's fuse are read here, never tuned here.

**Lifts** (Appendix A):
- **Narration.** F1, the floor, rises from about 0.3–0.55 to about 0.95, and C1 from about 0.2 to about 0.8; C6 is raised. Narration's chance of reaching its 8.0 target goes from about 0.15 to about 0.55.
- **Economy C6:** the chest's peacetime use is named, with a price.
- **Living balance:** C5 is re-worded to this step (Appendix A).
- **The ending:** the titled count gets a guard the player can act on.

**Must not break:**
- `BASELINE_SERIES` and M1–M7 stay byte-identical: the dispatch memory and the forecast are read by no AI. Each lever down is byte-identical.
- RS-D2's own completion test holds.
- CA8-5's dedupe, PC-7's note hand-back, and the Moniteur.
- The question desk's read of `last_morning_dispatch`.

**Pins** (`tests/test_sf_page_the_front_page_of_the_peace.py`, driving the three commanded arms):
- 0 of 120 turns without a headline (58 today);
- no class leads more than 4 of any 10 turns (7 today);
- a standing crisis is on the page every turn it stands;
- the CMD-H turn-24 shape leads with the subsidy;
- every quoted turn count matches the stepped tick and flips the counterfactual, and the buy-off gold equals `compute_buyoff_price`;
- a wound outranks the family;
- the rows for a court out of time, and for one refusing the Congress;
- each lever down byte-identical;
- a mutation sweep.

**Frames:** the dispatch view and the Balance of Europe tab, re-shot at both scales. The user's eyes on them ride SF-R's EYES items.

**Placement.** The last build step, after Chunk 9 and before SF-R, by the user's direction. It reads what Steps 1–3 build (RS-D1's turn-cost helper, the Armed Peace's fuse) and nothing later needs it.

**It re-judges SF-ECON-1.** With keep-out prices on the page, the chest has its peacetime use. SF-ECON-1 is taken only if economy C6 still fails after this step.

### Step 8 — SF-R, the final reading (≈1.0)

- **The instrument** on the final tree, with the same checklist version as the baseline (or the baseline re-read under the new version).
- **The blind panel and the user's EYES items.**
- **HOLD, written fresh**, then read on BOTH trees in the same session: the final tree, and `c20d5bba` on a detached worktree.
- **One hand-played depth campaign** (keyed, then a keyless stretch), for the findings rate, not the score.
- **The re-score memo:**
  - every pillar's item flips since the baseline;
  - the median and the spread;
  - the census.

---

## §4 The scoring method

### §4.1 What changes

The score is read from a fixed instrument, not from one reviewer's impression of one campaign. It has four parts:
- a fixed benchmark: the same arms, seeds and dials every time;
- a checklist per pillar, of binary, observable items;
- a frozen rule that turns items into a score;
- a blind panel, which adjusts for feel within ±0.25 and reports its spread.

Defects found in play still count, but as a findings rate reported beside the score; they are never subtracted from it.

### §4.2 The fixed benchmark

**Settings:**
- **Run mode:** Mode A (`tools/playtest_driver.py`), mock parser, `PYTHONHASHSEED=0`, `--archive`.
- **Seeds:** **H** historical, **A** austerlitz, **M** marengo (the commanded table's three), plus `ulm` for the agendas arm.
- **Scripts:** under `tools/playtest_scripts/`.

| Arm | Command | Seeds | Feeds |
|---|---|---|---|
| **FC** | `sr_exit_first_contact.json --turns 2` (the 28 sourced first questions) | H | first contact |
| **OP** — the fixed hand opening | `sr_exit_aar_typed.json --turns 18 --objection insist --diplomacy accept` (the AAR player's 127 typed lines) | H | command, first contact, drama, UI/UX |
| **DL** *(new)* | `score_docked_lines.json --turns 3`: the lines reviews docked (RS-6/7/8/11/12/14/15, PC15-6, AAR-6); grows each review | H | command, first contact, diplomacy |
| **HOLD** *(new each run)* | 20 questions and 20 orders, each with its intended reading, written blind by an agent that has read only the boot briefing | H | command, first contact |
| **CMD** | `commanded_full40.json --turns 40 --diplomacy accept --save-at 10,20,30,40` | H A M, ulm | the ending, living balance, vassals, economy, agendas |
| **FLD** | `sr_exit_chunk4_field.json --turns 10 --objection insist --diplomacy decline` | H | combat legibility, drama |
| **LAW** | `sr_exit_chunk5_laws.json --turns 10 --diplomacy accept` (types `enact the Staff` every loop — SF-V3) | H | economy |
| **SEA** | `sr_exit_chunk5_sea.json --turns 12` · the shut-out `sr5b_shut_out.json --turns 12 --diplomacy accept` (H A M) · the descent `naval_descent.json --turns 14` | H | naval |
| **DIP** | `--turns 20 --diplomacy propose` (H A M) · the advisor `--missions advisor --diplomacy accept --turns 20` · **VOLTE** `volte_court_austria.json --turns 40` | H | diplomacy |
| **END** | Pressburg (`ge3_pressburg.json` from its fixture, `--stop-on-ending`) · the Verdict (`--seed austerlitz --turns 46 --stop-on-ending`) · **CONG** *(new)*: `--from-save …/rs0928-hand-played/retest_t24_summonable.json`, `summon the congress`, `--diplomacy accept --turns 9` · REACH: `sr1e_aar_road.json`, `sr1e_gev_b.json --turns 40` | H | the ending |
| **AGD** *(new, Step 5)* | `sf_agd1_tilsit_road.json --from-save tests/fixtures/playtest_saves/fixture_agd_tilsit.json --turns 3 --diplomacy accept --save-at 1,2,3` — SF-AGD-1's played carve (Posen taken, the Duchy carved through the table's own `@` clicks, the separate peace, the Proclamation) | H | agendas (C5) |
| **SCH** | `tutorial_lesson.json --turns 12` | — | first contact |
| **AIV** | `tools/ai_v_sweep.py --all --turns 40 --acceptance-n 10` | its own | living balance, AI aliveness, agendas |
| **SUITE** | M1–M7, `test_ai_intent_assurance.py`, `parser_eval` (+ `--replay`), the agenda and naval-gate tests | — | floors |
| **CLI** | `iq10_capture_payloads.py` + `iq10_run_captures.py --scales 1.0,2.0` | — | UI/UX |

**Rules:**
- **CONG** replays the hand campaign's frozen end state; no script can replay that road. On today's tree the Congress dissolves at loop 4 with 41 of 45 titled, so RS-2 reproduces in about three seconds.
- **OP is never re-authored.** Board refusals are counted separately from reading refusals. When board refusals pass 50%, a new opening is versioned in.
- **Every deterministic arm is re-run on the final tree.** A baseline archive is reused only when its `engine_revision.content_hash` matches.
- **HOLD, the live-parser arm and the EYES frames are read on both trees in one session** (a detached worktree).

### §4.3 The checklists

Each pillar has eight items: two **floors** (must pass) and six **ceilings** (the climb). Each item is one of:
- **AUTO**: read from the digests, tests and tools today;
- **PROBE**: needs a small read-only probe, built in SF-M;
- **EYES**: needs a person or a screenshot.

Items are derived from what reviewers actually docked and praised, and they exclude behaviour the user has ruled intended: the long-peace hoard (SRX-D1), and the unattended France losing.

Appendix A lists version 1 (112 items). It is frozen once the user confirms it and versioned after that; a new version re-reads the baseline archive before comparing.

### §4.4 The rule (frozen)

| Ceilings passed | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Both floors pass, and no verified open P1 in the pillar | 5.5 | 6.0 | 6.5 | 7.0 | 7.5 | 8.0 | 8.5 |
| Otherwise | 5.0 + 0.25 per ceiling, at most 6.0 | | | | | | |

- **The smallest move that can be claimed is one item.**
- **Coverage:**
  - A pillar is **exercised** when at least 6 of its 8 items were measured.
  - With 1–2 items unmeasured, its score is a range, and the directional uses the low end.
  - With fewer than 6 measured, it is **NOT EXERCISED**: shown greyed with its date, and never averaged.
  - The directional is reported as "x.xx over n/14".
- **Targets become item counts:** 7.0 = 3 ceilings, 7.5 = 4, 8.0 = 5, 8.5 = 6. Every pillar at target is 56 of 84 ceilings with every floor green. That is exactly the directional 7.5 the mandate asks, stated so that it can be checked.
- **A verified open P1 caps its pillar.** P1s are read from the census, which is pillar-tagged in SF-0. Open P2 counts print beside the score.
- **The findings rate** is reported beside the scores and never subtracted: new rows per 10 turns played, by severity, split hand vs driver, and by depth (turns 1–10 / 11–20 / 21+).

### §4.5 The blind panel

1. **`score_run.py packet`** assembles:
   - the checklist results;
   - the digests;
   - the client frames and their index;
   - the census;
   - the findings rate.

   It leaves out `SCORE_MANDATE_PLAN.md` §1, STATUS, `CLAUDE.md`, the audit memos, prior runs and the git log, because commit subjects carry scores.
2. **Three agents with fresh contexts, in parallel, read only the packet.**
   - Each marks the EYES items. The user's own marks override theirs.
   - An agent may flag an item for a human check, but a flag never moves a score.
   - Per pillar, each returns the anchor score, an adjustment of −0.25, 0 or +0.25, and one line citing a digest line or a frame.
3. **The median and the spread (max − min) are published.** A move is claimed only when an item flipped AND the median moved by more than the larger of the two runs' spreads. Otherwise the pillar reads "held".

### §4.6 The two blind spots

**UI/UX.** The IQ-10 capture harness renders the real scenes in a window parked off-screen, with Dummy audio and a shimmed `user://`. While the user's own game is open, run it only with their OK.
- The AUTO half reads `script_errors`, `blank`, `buttons_offscreen`, `clipped_text` and `texts`.
- The EYES half is the same ten frames every run, before and after side by side, plus one 5-turn Mode C session.
- No Godot: the pillar is NOT EXERCISED.

**Agendas.** Scripts reach a carve only from the losing side. The Normandy mirror carve on seed `ulm` raised `nation_proclamation` on `rf3-cmd-on-ulm` at turn 30. `tools/_score_probes.py` (⚑ built Sept 29 as the one probes module — not a separate `_score_formables_probe.py`) does three things:
- reads `GET /formables` at each snapshot, recording gate flips;
- **TILSIT:** stages the IGR-D fixture (France six turns at war with Prussia, holding Posen), then drives the Warsaw `create_client` separate peace through `/respond_to_diplomatic_dialogue`, without patching acceptance (measured 58 against 50). Pass means `nation_proclamation` fires and `DuchyOfWarsaw` stands; **⚑ Measured Sept 29 (`agendas_c4_tilsit`): on the beaten board the bare carve reads COUNTER_OFFER at 30 and ACCEPT at 90 with a 6,000-gold sweetener — the 58-against-50 figure did not reproduce; the probe ratifies the first ACCEPT (a counter is not a signature) and the card raises;**
- adds the two IQ-10 shots from Step 0.

### §4.7 Cost

- **One scoring run costs about 0.3 of a session.**
  - About 45 minutes unattended: the driver arms ≈10, AI-V ≈15–20, the client ≈15.
  - About nine probes and three panel agents.
  - Fifteen minutes of the user's eyes.

  The Sept 28 retest took a full session.
- **The one-time build is SF-M.**
- **Outputs** go to `docs/audits/score_runs/<date>_<sha>/`:
  - `arms/`;
  - `checklist.json`, `scores.json`, `census_by_pillar.json`, `findings_rate.json`;
  - `panel_packet/` and `panel_{1,2,3}.json`;
  - `compare.md`: the item flips, and the median's move against the spread.
- **Hand-played campaigns keep one job:** finding defects in depth, not setting the number.

---

## §5 Cadence

- **The user's September 26 ruling stands:** one exit per session, one residue slice, no pillar re-score mid-way.
- **Two full readings:** the baseline (Step 0) and the final (Step 8), on the same instrument and checklist version.
- **Every session exit adds three cheap reads:**
  - `score_run.py check` over the AUTO items its slices touched. This reports item flips, not scores; they go into the session memo and the STATUS entry, so progress is visible between the two readings.
  - `defect_census.py --open`. If a row the session's slices owned is still open with no new owner, the exit fails.
  - `BASELINE_SERIES` and M1–M7, as before.
- **The interim impression scores** (`SCORE_MANDATE_PLAN.md` §1, marked ⚑⚑) are frozen as history. The baseline supersedes them.

---

## §6 The user's rulings

Recommended defaults are the plan's; every one is the user's to confirm or change. **Rows 1, 3 and 6 were RULED on September 28, 2026 under the user's delegation** (*"make decisions on …"*). Each was researched first; the gate records are §6.1–§6.3, and they are authoritative.

| # | Question | Recommended default | Needed by |
|---|---|---|---|
| 1 | **RS-D1:** does a signed peace that leaves a great power's capital in the French bloc latch its recognition? | ✅ **RULED Sept 28, 2026: YES, anchored to the capital, with a price rider** (§6.1). | Step 1 |
| 2 | **The checklist, v1** (Appendix A), and "the items are the done-when" | Confirm v1. Define done as 56 of 84 ceilings with every floor green, which means every pillar at target. | Step 0, before the baseline freezes **✅ Taken at the recommended default Sept 29, 2026 under the user's "proceed": v1 is frozen (`docs/SCORE_CHECKLIST_V1.json`), done = 56 of 84 ceilings with every floor green and no verified open P1; the user may amend and a new version re-reads the baseline archive.** |
| 3 | **SR-G7 / PB-D1:** a standing alarm floor, so the long peace ends by machinery; which slot rules it | ✅ **RULED Sept 28, 2026: "THE ARMED PEACE"** — a watch line at 45 while France leads a third of Europe's power, then a visible 16-quiet-turn fuse up to the brewing gate (§6.2). The drafted "≥ 40% of the map" was **rejected on measurement**. Built at Step 3; ROADMAP 12 no longer owns PB-D1. | Step 3 |
| 4 | **RS-3's shape** | A field win halts before a garrison that still fights (the march's own predicate). | Step 3 ✅ **TAKEN AT THE DEFAULT AND BUILT October 2, 2026 (Step 3; marked here October 4, 2026, Step 7's housekeeping — the row had never been struck):** `combat_executor.A_FIELD_WIN_HALTS_BEFORE_THE_WORKS` — a field win halts before a garrison that still fights; rules `SYSTEMS_REFERENCE.md` §83.1; pins `tests/test_rs3_the_garrison_stands.py`; `BUG_FIXES.md` RS-3 FIXED. |
| 5 | **CQ-22:** the stance rule for drill on every road | The player's rule for both boards: no drill in aggressive stance. One series re-record. | Step 3 ✅ **TAKEN AT THE DEFAULT AND BUILT October 2, 2026 (Step 3, SR-7a; marked here October 4, 2026):** `tactical_executor.ONE_STANCE_RULE_FOR_DRILL` — a drill in AGGRESSIVE stance is refused on every road, the player's and the AI's (P4.9 and P6); the one series re-record is Step 3's, flip-attributed (CQ-22 diverges at [18]); rules `SYSTEMS_REFERENCE.md` §83.2; `BUG_FIXES.md` CQ-22 FIXED. |
| 6 | **SF-V4:** an attack on a proper name the map does not know | ✅ **RULED Sept 28, 2026: the marshal ASKS, for free, naming only foes in sight**; a descriptive phrase keeps today's disclosed substitution (§6.3). | Step 4 (it leads CRT-10) |
| 7 | **CX-X3:** the typed `vassalize` of a beaten minor | ✅ **TAKEN AT THE DEFAULT AND BUILT October 3, 2026 (SF-CMD-1 part (ii), CRT-8 §8a):** `VassalExecutor.THE_VASSAL_VERB_IS_GATED` — at war the court must be BEATEN (GEV-1's three proofs via `vassal.subjugation_refusal`); at peace the typed verb is routed to the Cabinet's priced vassalage proposal. Rules §88.4. | Step 4 |
| 8 | **CQ-36:** the break row for a boot alliance | ✅ **TAKEN AT THE DEFAULT AND BUILT October 3, 2026 (SF-CMD-1 part (ii), CRT-8):** the row stays dimmed with "An alliance of 1805, not a treaty of ours — there is nothing to break; Downgrade loosens it." in the preview and the executor's refusal. Rules §88.4. | Step 4 |
| 9 | **VP-D9:** the player's defection-bribe verb | Strike it. The AI's on-ramp stays; VD-C is the vassals' lift. | Step 5 ✅ **RULED October 3, 2026 under the user's delegation** (*"rule them with research if you reach them"*): **STRIKE**, at the default. The research: 0 of 20 forty-turn saves on the shipped tree hold an enemy-lord satellite (the exit's CMD-H / CMD-A / CMD-M saves at turns 10–41 and the three Q0 roads at turn 40 — France's satellites only); the one enemy-held satellite measured is Britain's Normandy, carved from French soil on the doctrines-DOWN counterfactual of opening A — so the verb would have no target in a played 1805 campaign. VP-D9 is struck; the domain helper stays for the AI's on-ramp. **Re-open** when a shipped-tree exit arm shows an enemy lord holding a satellite (the Normandy carve is the measured case). |
| 10 | **IQ7-D4:** is the unattended petition calendar a variance target? | No; amend `AI_INTENT_SPEC.md` §3.8. | Step 5 ✅ **RULED October 3, 2026 under the user's delegation** (*"rule them with research if you reach them"*): **NO — the unattended board's petition calendar is not a variance target**, at the default. The research is IQ7-D4's own: the courts reach `fight` on identical turns with the IQ-7 levers up and down on all ten seeds, the narrowed break is a France-party war on a board no player drives, and a ±1 on either constant only re-separates the seeds — jittering the cadence to satisfy the sweep would be design driven by the harness. `AI_INTENT_SPEC.md` §3.8's failure clause is amended to say so; `TestTheCadenceIsSeeded` is not built. |
| 11 | **SF-ECON-1:** a late gold sink ("Acts of the Empire") | Only if economy C6 still fails after Step 7b, whose keep-out prices are the chest's first peacetime use; and then through its own gate. | Step 6 ✅ **RULED October 3, 2026 under the user's delegation** (*"rule them with research if you reach them"*): **taken at the default** — no gate opens now. Economy C6 is read at Step 7b's exit; only if it still fails does SF-ECON-1 come to its own gate. The LAW arm did not run at this exit, so nothing moves the condition. |
| 12 | **The orphaned design gates** | Dispositions below this table. | SF-0, to close the rows |
| 14 | **SF-LB-2's variance clause:** the crisis turn should span ≥ 3 turns across the seeds; measured, Prussia's crisis opens on turn 9 on six seeds and 10 on marengo, because the council reads the chest BEFORE the turn's income and the unseeded economy clears `AI_WAR_TREASURY_FLOOR` (500) on the same turn everywhere (the ladder itself climbs on turns 3–8, seed by seed). | **Read the chest the council can SPEND — the turn's income forecast, as the ledger quotes it** (IQ1-5-1's tick-staleness family, one seam): the opening then falls to the ladder's own turn, which already varies 3–8 across the seeds; the restraints at the DECLARATION keep reading the live chest. Rejected: seeding Prussia's treasury (D7 fixes it Tier 1); lowering the floor (a tune). | ✅ **RULED October 3, 2026 — build the recommendation; BUILT the same day as SF-LB-2b "The Chest the Council Can Spend"** (landing record §6.4's second addendum; rules `SYSTEMS_REFERENCE.md` §85.8): `war_council.THE_COUNCIL_SPENDS_THE_TURNS_INCOME` — the OPENING reads `ledger.chest_forecast` (the ONE projection `reforms.lapse_forecast` reads), the declaration keeps the live chest. **The recommendation's premise was wrong by measurement:** the ladder does not vary 3–8 on the shipped tree — it is climbed after turn 3 or 4 on six seeds — and turn 4's projected chest reads 497 against 500 on every one of them, so the first openings read **{5, 9}** and the clause is STILL NOT MET (the war's turn does vary: 9 / 11 / 12). The xfail stays strict. The remainder is **§6 row 15**. |
| 15 | **The six-seed cluster behind row 14 (filed October 3, 2026 by SF-LB-2b's measurement):** with the forecast read built, Prussia's crisis on Hanover first opens on turn 5 on six of seven seeds (historical, austerlitz, friedland, jena, ulm, marengo) and on 9 on eylau (its second refusal lands on turn 8). On the six, the ladder — any two refused asks of ANY type (`_ladder_climbed` counts the whole refusal record, not the design asks alone) — is climbed after turn 3 or 4 (the design ask on turn 2, a second refusal two turns later, both constant-driven: the ask fires the first turn the court stands at its rung and `NATION_REJECTION_COOLDOWN` / `TYPE_REJECTION_COOLDOWN` are unseeded), and the chest's projection on turn 4 reads **497 against the floor of 500** on every one of them (Prussia's Tier-1 economy at peace plays identically on those seeds — the AI's peacetime spending does not read the seed), so turn 5 is the first turn both gates clear and it is the CHEST, by three gold, that decides. Marengo's seeded weight then dips below `coerce` on turns 5–8, its first crisis cools and a second opens on 10 — so the WAR's turn spans three values (9 / 11 / 12) while the OPENING spans two. The standing rule (no beat on the same turn on every seed) is breached by six of seven. | **Recommendation, not built — a design question put once:** a seeded PATIENCE on the court-to-court design ask — a dwell of `seeded_int(seed, "design_ask_patience::<asker>::<holder>", 0, 4)` turns after the court first stands at its ask rung before the first ask fires (`historical` = 0, so `BASELINE_SERIES` and every historical pin stay byte-identical; AI-0b's §3.8 contract already names cooldowns and dwell as the seed's own terms, so this is that contract applied to the one cadence it missed, not a new mechanic). Projected reach: the ladder climbs on turns 3–8 across the seeds and the first openings spread over 5–9. Rejected: seeding Prussia's treasury (D7, Tier 1); a jitter on `AI_WAR_TREASURY_FLOOR` (a bar the seed should not move — a bankrupt adventure is one on every seed); seeding the AI's peacetime spending (the economy pillar's question, not this row's); the ruling's own re-open, Britain's guarantee of Hanover (AI-3's guarantee rung cannot fire while Britain is at war with France — the whole of 1805 — so it is not a counter here). | **the user**; `tests/test_sf_lb2_the_defenceless_prize.py::TestTheDrivenBoard::test_the_crisis_turn_varies_across_seeds` + `::test_the_seven_seed_record_spans_three_turns` and `tests/test_ai_intent_assurance.py::TestTheStandingRuleOnCouncilWars::test_every_pair_that_opens_on_three_seeds_spans_three_turns` are strict xfails that flip the day it is met ✅ **RULED October 3, 2026 under the user's delegation** (*"rule them with research if you reach them"*): **BUILD THE RECOMMENDATION — seeded patience on the design ask**, as **SF-LB-2c at the head of Step 5**. The research is SF-LB-2b's measurement (the opening is decided by the same turn-4 chest on six seeds because the ladder climbs on the same turns — the cadence the seed was meant to move, §3.8 item 1's own "dwell"), and the patience is that contract applied to the one cadence it missed, `historical` = 0 so `BASELINE_SERIES` and every historical pin stay byte-identical. **Acceptance:** the three strict xfails flip on the shipped tree. **If they do not**, the clause is amended to read the WAR's turn — which already spans three values (9 / 11 / 12) — and the miss is recorded; no third attempt at the opening (IGR-E's two-attempt rule). ✅ **BUILT October 3, 2026 as SF-LB-2c "The patient ask" — MET on the first attempt** (§6.4's third addendum): the three strict xfails flipped on the shipped tree; the clause keeps reading the OPENING. |
| 16 | **SF-CL-1-D1: where an attack's coordination is read (filed by SF-CL-1, put here at Step 4's exit, October 3, 2026).** The resolver relocates every arriving corps INTO the battle province but reads the lead's coordination context in HIS province, so an attack from next door earns none from the corps that answer it: Ney at Rhineland on Mack at Swabia — Davout, Lannes, Murat and the Emperor all march to Swabia and none counts; only a lead already on the field gets the +25%. The forecast says exactly what the resolver does (SF-CL-1), so this is a mechanics question, not a forecast one. | **Read it on the FIELD**, where the arrivals stand and the battle is fought — the corps system's own point (converge, then fight together); the forecast follows through its one seam `_priced_coordination`. Rejected: reading the arrivals' coordination in the lead's province (it would credit corps that never reach the field). It moves combat: one `BASELINE_SERIES` re-record, flip-attributed, and the M1–M7 harness re-read. | Before SF-R (built in Step 7's slot once ruled) ✅ **RULED October 3, 2026 by the user** (in chat, *"i agree"*; written here by Step 5's session): **read the lead's coordination context on the FIELD** — the battle province, where the arriving corps stand. The build stays in **Step 7's slot**, as the row says: `_calculate_coordination_context` reads the battle province, `_priced_coordination` follows in lockstep (SF-CL-1's one forecast seam, so the preview keeps saying what the resolver does), ONE `BASELINE_SERIES` re-record with flip attribution, and a re-read of the M1–M7 harness. Owner row `DESIGN_REFINEMENT.md` SF-CL-1-D1. ✅ **BUILT October 4, 2026** (Step 7 slice 3, alone in its own commit — landing record §3 Step 7; rules `SYSTEMS_REFERENCE.md` §93.3): one re-record with two levers attributed, M1–M7 byte-identical; the item flips it causes and the one wording question it raises are row 18. |
| 19 | **SF7-X11: a named marshal beside a different named province (filed and ruled by Step 7 slice 5b, October 4, 2026).** PF-7 decided a NAMED marshal levies where he stands, and SR-3b recorded the boundary "a NAMED marshal keeps PF-7's road" (`SYSTEMS_REFERENCE.md` §72.3; CRT-2's pin `test_a_named_marshal_keeps_his_own_road`). Measured: `Davout, recruit infantry in Rhineland` with Davout at Lorraine raised 3,000 men at Lorraine for 741 gold — the province the player named silently replaced by his (CRT-2's own class, the name is never replaced); the HOLD arm's `Raise more infantry for Davout in Rhineland` was refused about Swabia for the same reason. CN-1/CN-2's ruling D1 left a re-open condition for the ARM mismatch only ("if the user would rather the named mismatch refuse, spending nothing, than surface"); the PROVINCE mismatch had none. | **RULED under the delegation, FOR USER CONFIRMATION:** his own province keeps PF-7's road; a DIFFERENT province named beside him is refused free, naming both roads (`economy_executor.A_NAMED_LEVY_GROUND_IS_HONOURED`, player orders only — the AI names the marshal's own province, so the series cannot move). Rejected: levying at his province and disclosing the substitution (PF-7's arm-mismatch idiom) — it spends gold at a place the player did not name; marching him to the named province first (an order the player did not give). CRT-2's pin re-seated consciously. | **the user**, at the next review (nothing waits on it; the lever restores the shipped levy). |
| 20 | **SR-7d-X1 / IQ6-D2: an ally's own war and the volte door (filed and ruled by Step 7 slice 6, October 4, 2026).** IQ6-D2 (§6 row 12) reads both arms of the volte-face's NOT-HUMILIATED clause over the hegemon's whole bloc — the TREATY arm (a punitive memory: a partition signed into a peace) and the BATTLEFIELD arm (an emergent revanche, charged to whoever holds the lost homeland). On the 1805 board Bavaria — France's ally, at war with Austria from the boot, Austria having invaded it — takes a second Austrian province between turns 8 and 11 on every road played (eleven, historical seed: the volte arm's own war; France holding Bohemia or nothing; attacking or standing fast after Ulm; a turn-4 separate peace, refused by the alliance paradox; terms asked of London, refused — the league not spent; the Bavarian alliance broken, refused — a bond of 1805), the revanche is charged to Bavaria, and the door closes for the campaign: Austria's volte-face was unreachable on the shipped board, and SR-7d-X1's re-script had no road to take. With IQ6-D2's lever down the shipped arm fires the beat unchanged. | **RULED under the delegation, FOR USER CONFIRMATION: keep the TREATY arm over the bloc; read the BATTLEFIELD arm over the hegemon and its vassal chain** (`emergent_designs.AN_ALLYS_WAR_IS_ITS_OWN`) — a sovereign ally's conquest in its own war is the ally's quarrel; a partition signed into a peace, or taken by France or a French vassal, is France's. The history: Pressburg gave Tyrol to Bavaria and Austria allied with France in 1812; the case IQ6-D2 rested on, Tilsit, was a partition signed for France's new clients. Rejected: narrowing both arms to the vassal chain (a punitive memory is charged to its receiver, so France's own table ceding to an ally would escape); keeping the bloc and re-scripting around another court (Austria is the period's own case and the arm's subject); a staged arm (it must be played). Measured: the shipped arm fires on historical (turn 27) and austerlitz (turn 24), not on marengo (at war again on turn 23); `BASELINE_SERIES` + M1–M7 byte-identical. | **the user**, at the next review; the lever restores IQ6-D2 as built. |
| 18 | **AI aliveness C5's wording (filed by Step 7 slice 3, October 4, 2026).** The item reads "No AI corps fortifies, unfortifies and fortifies again within 3 turns", and the probe counts exactly that. On the field-read board it flips ✓ → ✗ on CMD-H: Archduke Charles fortifies on arrival at Bohemia (turn 8), breaks camp to attack (three attacks on turn 9, two more on turn 10) and fortifies again on arrival at Carniola (turn 11); the same shape on turns 33–36 (the turn-34 break is for two garrison assaults on Franconia). The dither SR-7a (AAR-D8) built its guard against was a different thing — an idle corps held by the odds, force-unfortified by the stagnation breaker and fortified again in place for no state change. The checklist is frozen (v1), so the item is read as written and the flip stands. | **Recommendation, not applied:** a v1.1 reading of C5 that counts a dither only when the second fortify is in the SAME province with no attack and no march between the unfortify and it — SR-7a's own definition — applied to the baseline archive as well, so both readings use one rule (§4's "a new version re-reads the baseline archive before comparing"). Rejected: leaving the item unread on the field-read board (the flip is real by its letter); tuning the cautious kit (the user's rule — do not tune). | **the user**, before SF-R (the final reading). Evidence: `docs/audits/score_runs/2026_10_04_sf7_s3/` (the matched set on `b127e41e` and on slice 3's tree, lever-attributed). |
| 17 | **SF-NAV-1-D1: the System cannot outlast Spain's exit — the A2 anchor (filed by SF-NAV-1, Step 6, October 4, 2026).** The strangulation arm (`sf_nav1_strangulation.json`, three seeds, 30 turns) shut Britain out on a played board for the first time — historical turn 11, marengo turns 13–15 (13–14 of 26 ports, no British corps on the Continent) — but never for a sitting's 8 turns, and the System's tier 2 (16 of 26) was never reached (peak 14). Three measured reasons: (1) Spain's war with Britain ends on turn 16 on every seed by the exhausted-pair exit (`settlement_third_party.PAIR_EXIT_*`: both at war exhaustion ≥ 120, ten turns at war, their war score within ±15 — they never fight each other), taking 3 ports; (2) Britain's descents keep a corps ashore until her bench of three is taken (turns 12–17), and a prisoner comes back with his captor's peace; (3) the Tilsit lever — a peace that enrols the beaten court in the System — is settlement-tier (`forced_alliance` with `includes_continental_system`), so the separate peace cannot carry it and the joint table cannot be sealed while Britain fights on in the same war (the 1805 boot folds all seven starting wars into one). Britain sues on turn 8 on every seed from the war's own exhaustion (+8 a turn; the System adds at most +1 at tier 1). | **(a) The Tilsit clause on a separate peace** — a bilateral peace may carry "joins the Continental System" (no forced alliance), priced as today's CS surcharge (+10 alarm), on a court the Emperor has beaten: the historical mechanism (Prussia and Russia at Tilsit 1807, Austria 1809), legible as a clause with its price, no change to any AI's war behaviour; it reaches tier 2 by diplomacy (Austria 1 + Russia 2 + Prussia 1). Rejected: (b) binding a hegemon's ally to the war (Spain fought Britain until 1808, but the exhausted-pair exit exists to stop the WE-200 ratchet, Stage D [r5]); (c) counting an ally's ports while it is at peace with Britain (a ruling about what an alliance IS, wider than the System); (d) keeping the rule and re-anchoring A2 to tier 1 (honest, but then the System never decides anything — Britain always sues from her own war first). | **the user** (the A2 anchor — `NAVAL_SPEC.md` §5.1 / §20; owner row `DESIGN_REFINEMENT.md` SF-NAV-1-D1); evidence `docs/audits/SF_NAV1_STRANGULATION_2026_10_04.md`; the benchmark's `NAV1-H/A/M` re-reads it the day it is ruled; built in Step 7's slot, before SF-R. ✅ **RULED October 4, 2026 under the user's delegation (Step 7, FOR USER CONFIRMATION): (a), the Tilsit clause on a separate peace, with the System's missing exit and A2 re-anchored** — gate record §6.6 (authoritative); research memo `docs/audits/SF_NAV1_D1_THE_A2_ANCHOR_2026_10_04.md` (the conquest road played on three seeds: peaks 10–13, SHUT OUT held at most 3 turns, never after Spain's exit; the record hand-played board reads 9 of 26). The build is Step 7's row-17 slice; the design row stays open until it lands. ✅ **BUILT October 4, 2026 (Step 7 slice 4; landing addendum §6.6) — the done-when is NOT met:** the Tilsit road (`tools/playtest_scripts/sf_nav1_tilsit_road.json` (benchmark `NAV1T-H/A/M`)) holds SHUT OUT for **17 consecutive turns on historical** (peak 16 of 26, tier 2 for the first time) and **never on austerlitz or marengo** (peak 16 on both) — the next coalition draws a signatory back to war 5–9 turns after the peaces and the exit takes its ports; on austerlitz British corps stay ashore all game behind Austria's closed frontier in France (SF7-X7). **Back with the user**, the 50% line untuned. |
| 13 | **Confirmations already owed** (not blocking) | FA-D29 / FA-S17-1, FA-D4, FA-S2-D1, FA-D23, and the FA-D27 re-open; the RF-4 laws frames | Step 7's sign-offs ✅ **RULED October 3, 2026 under the user's delegation** (*"rule them with research if you reach them"*): **CONFIRMED**, the user's own confirmation of call C6 (`STATUS.md`, September 23 — FA-D29 / FA-S17-1, FA-D4, FA-S2-D1, FA-D23 and the FA-D27 re-open were confirmed AS BUILT under the delegated grant, each keeping its lever and its re-open condition). The research: at this exit the commanded France holds **27 / 24 / 24 provinces at turn 40 with Paris held** (CMD-A / CMD-H / CMD-M), so FA-D27's re-open reading does not fire on the commanded arm; the RF-4 laws frames were signed off October 3 (SF-CMD-1 part (ii), under the user's direction). Each row's own re-open condition stands. |

**Row 12, the orphaned design gates:**
- **WO-D7:** strike, on SR-5a's "keep the rules, make it legible".
- **WO-D8:** "price, not time". The declaration names the betrayal and the alarm it costs.
- **WO-D13:** record the rung-1 precedence as deliberate.
- **EWC-D3:** strike. W6-7's clause covers the release; a ransom is post-EA content.
- **VP-D8:** decline.
- **IQ6-D2:** no default. Rule it at Step 3's gate, after measuring. ✅ **RULED October 3, 2026 under the user's delegation** (*"rule them with research if you reach them"*): **a client's partition is the hegemon's act** — the NOT-HUMILIATED clause of the volte-face reads a punitive memory (and an emergent revanche) authored by ANY member of the hegemon's bloc, the same bloc its BEATEN clause already reads for "the defeat still shows". The research: Tilsit carved Prussia's Polish provinces for the Duchy of Warsaw and its western lands for Westphalia — French clients both — and Prussia's revanche was France's (1813); within the game's doctrine that a partition forecloses the door, the bloc reading is the consistent one. Built with SR-8c at Step 5 (the IQ-6 family), with the pin on the Bavaria-charged partition.

### §6.1 RS-D1 "Recognition by defeat" — RULED September 28, 2026 (gate record)

**The ruling: YES, anchored to the capital.** It amends SR-1a's ruling (2), and ruling (1) stands (a retained province is not reconciled: the ceder's designs still covet it).

**The research** (read-only, at `c20d5bba`):
- **Five things satisfy a court today** (`congress.answer`, congress.py:1056-1135):
  - elimination or vassalage;
  - a `table` latch: a peace signed while the Congress sits;
  - a `beaten` latch: a peace that CEDED provinces by clause (game_end.py:1448-1457);
  - the at-peace formula reaching 50 during the sitting;
  - SHUT OUT.
- **Austria's two retest peaces ceded nothing by clause.** Vienna was kept by a status-quo retention, so no latch was ever written: `world.congress` is `None` in the turn-24 save.
- **ENDGAME §2.4's "a refuser whose capital France holds sues at once" works only for a court at war.** `court_must_sue` returns False at peace. At peace, the capital is worth only a +10 that lapses 15 turns after the peace.
- **The turn-24 save, replayed:** it dissolves at the end of turn 27. On the same tick, Austria's answer turns to "SUES — we hold Vienna" — one tick too late.
- **The same replay with Austria latched:**
  - Austria RECOGNIZES on every tick;
  - the league forms without it;
  - the count holds at 47 through day 3;
  - the Congress falls on day 4 to a real loss in the field (Buxhowden takes Moravia from an unattended Ney).

  That is a fall with a cause the player can see.
- **Alternatives rejected:**
  - (b) GEV-1's "beaten" test at signing: a war score is cleared when the war ends, one recruit undoes "no corps standing", and a white peace after field wins alone would latch a court whose map is intact (GE-3 review #0).
  - (c) a 12–16-turn sitting: it doubles the time the hold is exposed, and the +10 still lapses.
  - (d) no change: the table keeps quoting a price that cannot be paid.

**The mechanics** (Step 1, behind the lever `congress.A_PEACE_THAT_KEEPS_THE_CAPITAL_RECOGNIZES`):

1. **The condition.** In `game_end.note_ratification`, after the clauses apply, any great-power counterpart whose capital is held by France or France's vassal chain is latched `kind: "capital"`, with the capital's name recorded.
   - "France's vassal chain" includes carved clients: the `_top_overlord == France` test that `_capital_taken`, GEV-1 and the title rule already use.
   - An ally is NOT the bloc here.
   - This applies to signed roads only, before or during the sitting. A truce, a truce expiring, or an elimination writes nothing. Player only: the Congress is France's.
2. **What breaks it.**
   - the two existing breakers: any new war between France and the court; the Emperor's capture from its bloc or of a province it covets;
   - **new:** the capital leaving the French bloc by any road — handed back, retaken, taken by a third party, or its holder's rebellion. This is derived inside `_signed_record`, with no new serialized field.

   A later cession peace re-writes the latch as `beaten`; a peace signed during the sitting writes `table`.
3. **The price rider** (its own lever).
   - **The problem:** the peace table scores a status-quo peace that keeps the counterpart's capital as "kept all" (`capital_lost: False`, +5; settlement_scoring.py:813-913). Austria read 52/50 on turn 16 for a peace plus 100 gold.
   - **The rule:** the scorer reads a retained great-power capital as a capital lost, so recognition by defeat costs a defeat, not a white peace.
   - **Measured in Step 1** with a flip arm on the retest's turn-16 shape. If, after the whole decisive campaign (Vienna, Bohemia, Moravia, Dresden and Carniola taken), no peace that keeps Vienna can be signed at all, the rider does not ship: the latch ships alone and the finding is recorded.
4. **What the player reads.**
   - **The Congress row:** "RECOGNIZES — it signed the peace that left Vienna in our hands (turn 16)".
   - **The settlement review and the ratification summary:** "Recognition: Austria will recognize the order at the Congress — Vienna stays ours by this treaty."
   - **The SUES projection** names this road.
   - **Every courtship lever quotes its cost in TURNS** (RS-D1's second half): "court them to 40 — 16 turns; the Congress sits 8".
5. **The rider for RS-1.** While the Congress sits, the offensive cascade also reads `spared_from_coalition`, so a recognizing court is not dragged into the league by an alliance.
6. **Pins** (`tests/test_rs_d1_recognition_by_defeat.py`):
   - both ratifiers latch a white peace that keeps the capital;
   - a capital held by a vassal or client latches; one held by an ally does not;
   - each of the three breakers;
   - a truce, or a truce expiring, never latches;
   - lever down, ruling (2) behaviour returns;
   - the turn-24 replay, driven;
   - the wording.

   `test_congress_of_paris.py::TestTheTable::test_a_white_peace_before_the_summons_does_not_latch` stays green: that peace keeps no capital.
7. **Pin flipped consciously:** `test_sr1a_status_quo_is_a_cession.py::TestTheAARShape::test_it_does_not_latch_the_congress`.
8. **Series.** `BASELINE_SERIES` cannot move, because the ambient board ratifies nothing with France (`congress_writes: 0` on every arm). The build confirms this with a two-arm check.

### §6.2 SR-G7 / PB-D1 "The Armed Peace" — RULED September 28, 2026 (gate record)

**The ruling: a watch line below the brewing gate, and a visible armed-peace fuse.** The drafted default ("Europe stays at Brewing while France holds ≥ 40% of the map") is **rejected on measurement**: it never fires.

**The research** (read-only; the three commanded arms re-run with saves every 5 turns, matching the `rs0928-cmd-*` ledgers exactly):
- **France holds 27–30 of 126 provinces** on the commanded arms (21–25%; 27–30% with satellites), and 36 (29%) on the hand-played Congress road.
- **Read as the bloc power share instead** (provinces × tier weight over France, her satellites and her allies — coalition.py:269-381), the 40% line fires on one seed of three, by 0.002.
- **Why the alarm reaches 0:**
  - The general peace (turns 10–11) spends the league: 95→47, 67→33, 76→38.
  - After that only hegemony (+1) and the agenda grudge (+2 for ten turns) run against decay (−3), so the alarm falls to 0 by turns 36–38.
  - Meanwhile Britain, Russia and Austria all QUALIFY for a league from turns 15–20 to turn 40 (relations −36 to −61). The league is loaded; only the alarm is missing.
  - No AI road reaches a quiet France: every opportunism term needs the holder at war, beaten, exhausted or bankrupt. Austria's Revanche stays below the coerce rung while she re-arms from 34k to 126k.
- **Alternatives rejected:**
  - (a) a floor AT brewing: never fires on provinces, is knife-edge on the bloc share, and where it fires it is IQ-3's revolving door (a new league 8 turns after each spent one).
  - (c) an AI road alone: an ultimatum needs French-held soil in a design, defiance adds less than decay, and "no unilateral AI declare-war" is pinned. At best one seed.
  - A bare clock: IQ-3 had rejected "a cooldown with a memory label". This one is admitted only because it is visible, can be played against, and fires once per quiet period.

**The mechanics** (Step 3, behind the lever `coalition.THE_ARMED_PEACE`; zero new serialized fields; one roster pass, GR8):

1. **The predicate.** All four must hold:
   - the hegemon leads the largest bloc at ≥ 1/3 of Europe's power (the band the code already names "anti-decay", coalition.py:325);
   - no coalition is active or brewing;
   - some court is left to alarm;
   - the Congress is not sitting.
2. **Quiet turns:** the current turn minus the latest `last_battle_turn` among the hegemon's marshals.
3. **The watch: 45** (in-band 40–50). While the predicate holds, decay stops at 45; below 45 decay does not run at all, so hegemony lifts a spent alarm back up.
4. **The fuse: 16 quiet turns** (in-band 12–20; never shorter than the 12-turn title clock).
   - After the fuse, the watch rises **+3 a turn** (source `armed_peace`) until it reaches the brewing gate at 60, where it holds.
   - The existing brewing countdown and `qualifies_for_coalition` do the rest.
5. **Reset.** Any battle by the hegemon restarts the count, and a formed league ends the predicate.
6. **What the player reads.**
   - **Threat rows:** "Europe watches — France leads 40% of Europe's power (floor 45)" and "The courts re-arm (+3)".
   - **The war room** shows the fuse's turns left and names the courts that would consult.
   - **The levers are stated:**
     - a court raised above −10 will not join;
     - a bloc under a third of Europe ends the watch;
     - the Congress suspends it;
     - a declaration takes the alarm from 45 to 65.
7. **GR5.** The predicate is written on *the hegemon*, as D3 already frames every coalition. The build measures the ambient series with the lever flipped:
   - **If the ambient series moves:** the move is attributed and `BASELINE_SERIES` is re-recorded once, provided every guard below holds. The "threat must be EARNED" pin (`test_ai_intent_threat_migration.py`) is then amended consciously.
   - **If a guard fails:** the predicate is scoped to the player, and the reason is recorded.
8. **Acceptance — PB-D1's own clause:** *"A France at peace after the opening war has a reason to act, and a Europe that answers her. On the commanded-accept driver arm, turns 12–40 contain either an AI-initiated war or ultimatum against France, or a French design pursued."*
   - **Measured as:** on 3 of 3 commanded-accept seeds, a coalition declares on France in turns 12–40, not by cascade, and the alarm rises after the peace.
   - **Projected:** the fuse lapses on turns 24 / 21 / 23 (historical / austerlitz / marengo); the league declares on turns 32 / 29 / 31. That is 18–22 turns after the peace — about Pressburg to Jena.
9. **Guards:**
   - IQ-3's declaring board still yields ≤ 3 leagues in 40 turns;
   - France keeps ≥ 20 provinces at turn 40 (checklist F1);
   - the GE-3 Pressburg arm still signs;
   - `BASELINE_SERIES` and M1–M7 are byte-identical with the lever down;
   - the passive France is no worse (it fights on 27 of 40 turns, so "quiet and dominant" never holds there).
10. **Risks recorded:**
    - F1 around turn 30: a France of 83–108k men faces Austria at 89–131k, Russia at 75–80k and Britain at 42–55k. If F1 breaks, lengthen the fuse; do not lower the watch.
    - At 45 the AI-to-AI preemptive-alliance trigger (above 40) wakes, so Europe allies during the quiet. Accepted: that is the point.
    - **The titled count.** A league breaks the treaty and retained titles of every ceder that joins it (`break_signed_titles`), and RS-2's fix covers only the sitting, so the ending's titled count can slide when the fuse brings a league. The build measures the titled count on the Armed Peace's arms and reports it. Step 7b's league rows name the titles at risk and the price to keep the ceder out.
11. **Closes:** PB-D1 closes when this lands with its clause green. RS-D3 closes today, cited as evidence here. ROADMAP 12 no longer owns PB-D1's ruling.

### §6.3 SF-V4 "A proper name asks" — RULED September 28, 2026 (gate record)

**The ruling: an attack that names a proper name matching nothing makes the marshal ASK, for free, naming only foes in sight.** A descriptive phrase keeps today's disclosed substitution. This is CRT-2's principle ("a name the sentence gives is the one acted on, or the order is refused free") and FA-22's addressee rule, applied to the target.

**The research** (probe at `c2dfe40b`, mock parser, a fresh 1805 boot per line, through `POST /command`):
- **Unknown names fight today.** "Ney, attack Zorglub" / "Alsace" / "Lombardy" each fight Mack: one action and about 6,500 French across the muster. The same happens for Venetia, Atlantis, Ulm, Bonaparte and a lowercase "zorglub", for Soult (literal), Davout and Murat alike, and for the driver's own 28 "Soult, attack Paget/Wellesley" lines while those generals are uncommissioned.
- **The same shape of order already gets other answers:**
  - it asks for "Charles" and "Kutusof" (CQ-30);
  - it is refused free for pursue, move, march, recruit and "deal with Zorglub";
  - a bare "attack Zorglub" asks which MARSHAL Zorglub is, and answering "1" sent Soult against Mack.
- **Where the name is dropped:**
  - both parse roads drop an unknown attack target (the mock at `llm_client.py:3375-3464`; the live road at `validation.py:473-475`);
  - the executor then picks the nearest visible foe;
  - `guessed_target_refusal` (combat_executor.py:238) discloses and proceeds.
- **How it got here:** ESP-EV-4 refused (Jul 11) → PS-1 exempted empty orders (Jul 12) → CR-6 §7 exempted auto-assignment (Jul 16) → PS18-R1 switched to disclose-and-proceed because *descriptions* cannot be enumerated (Jul 18). No ruling ever covered a proper name.
- **Alternatives rejected:**
  - (c) keep the substitution: it is a battle nobody ordered, and "he will turn" prints after the fight (CX5-L5-N5);
  - (b) refuse: it recreates the dead end PS-1 fixed, so it is kept only for when nothing is in sight;
  - (d) typo-matching first: kept, as the ask's own first stage.

**The mechanics** (Step 4; SF-V4 LEADS CRT-10, behind the lever `A_PROPER_NAME_ASKS`):

1. **A proper name, defined by grammar** (a pure function of the raw text, the marshal and the world). Take the words after the attack verb, up to the first comma, conjunction, preposition or clause word. A proper name is present when all three hold:
   - the words do not open with a determiner, possessive or quantifier (`_NAME_BLOCKING_PREFIXES`, plus his, her, their, its, our, your, every, any, each, some, all);
   - after filler and `GENERIC_TARGETS` are removed, a word remains that is not on a closed list of military nouns (cavalry, guns, battery, column, flank, vanguard, baggage …) and is not an -ly adverb;
   - that word resolves to no roster marshal, province, nation, demonym or prisoner.

   All six PS18-R1 descriptions stay descriptions, and so does "the Zorglub column".
2. **Behaviour by case:**

   | Case | Behaviour |
   |---|---|
   | Empty, generic, a description, a nation, an exact name, a fogged exact name | unchanged |
   | Unknown proper name | ask, free: "No foe called Zorglub is in sight, Sire. The nearest in sight is Mack at Swabia — shall Ney engage him?" |
   | Near miss of a visible foe (Makc, Mach) | "…did you mean Mack at Swabia?" (CQ-30 widened to transpositions inside the ask) |
   | A fallen general whose death was visible | "Archduke John fell at Tyrol on turn N, Sire — his corps is no more." + the ask (NPC-6). If the death was not visible, the plain ask. |
   | A name on an enemy's uncommissioned bench | the same line as a fogged commissioned general, so a commission never leaks |
   | Nothing in sight | the existing refusal, reworded to "in sight" |
   | Bare "attack Zorglub" (no marshal named) | the target question, never the marshal question |

3. **Fog.**
   - The ask says "in sight", never "known".
   - It offers only foes at PARTIAL visibility or better, nearest first, each with `interpreted_target` set. "yes" or "attack him" engages the foe the question named; today "yes" takes the first option in unsorted order.
4. **The arrival tail.** "march to Swabia then attack Zorglub" marches, arms no attack, and the reply names the dropped word.
5. **Pins** (`tests/test_crt10_the_suggestion_is_honest.py`, at `POST /command`, reading the world before and after):
   - every probe line, for all four personalities: nothing spent or lost, nothing out of sight named, and "yes", "2" and "cancel" each resolve;
   - the six PS18-R1 lines plus "retreating column", "enemy cavalry", "their left flank" and "at dawn" still proceed;
   - the bench answer is identical before and after an AI commission;
   - the fallen-general fog rule holds both ways;
   - the bare road never targets one of our own marshals;
   - a lever-down pin, golden-corpus rows, and a mutation sweep.

   The benchmark's DL arm gains "Ney, attack Zorglub" and "Ney, attack Alsace" (checklist Command C4).
6. **Pins flipped or extended consciously:**
   - the Venetia pin (`test_playtest_command_and_ui_2026_07_18.py:317`) flips;
   - `test_wo_slice10_enemy_direction_gate.py`'s refusal-wording list gains "No foe called".
7. **Series.**
   - `BASELINE_SERIES` and M1–M7 cannot move: only the typed player road carries raw input, and the AI always names exact targets.
   - **The commanded driver arms WILL move.** Their Paget/Wellesley lines now ask, and the driver's clarification policy decides what follows. The build re-reads those arms and records the change as a known move of the benchmark.

---

### §6.4 SF-LB-1's fight bar — "The Defenceless Prize" — RULED October 3, 2026 (gate record)

**The ruling: an AI-vs-AI acquire design whose holder cannot defend the prize opens its crisis at `coerce`, and the asker's weight reads the holder's weakness — the `fight` bar (85) stays where AI-3r put it for everything else.** Two derived terms, one lever, zero new serialized fields:
1. `intent.WEIGHT_HOLDER_OUTMATCHED = +10` when the holder's standing strength plus its guarantors' is at most HALF the asker's FREE strength (`war_council.get_free_strength` against `_standing_strength` + guarantees — the restraint gate's own arithmetic), **an armyless holder counting as outmatched** (the probe's `free_ratio_max = 99` is Hanover fielding no corps).
2. `war_council` opens an AI-vs-AI crisis at **`coerce` (72) instead of `fight` (85) when that same outmatched test holds and the restraints clear**; the ladder (two refused asks on record), the two fore-warned turns, the coercive demand and every restraint (busy / penniless / outmatched / exposed) still gate the declaration exactly as AI-3 built them.

**The research** (`tools/_sf_lb1_fight_bar_probe.py`, seven seeded 40-turn ambient boards at `a091db30`, every AI acquire design aimed at a non-player holder recorded every turn; `--aggregate`):
- **0 AI-vs-AI wars on 7 of 7 seeds, and `war_intents` empty on every one** — the Step-3 reading reproduces under the doctrines.
- **The recommendation Step 3 recorded is wrong by measurement.** A `+10` at a 2:1 free-strength ratio with the bar left at 85 opens NOTHING on Prussia→Hanover: the design tops at 70–73 (coerce on 3 seeds, bandwagon on 3, align on marengo), and +10 reaches 80–83 — under 85 on every seed. The term alone closes no gap.
- **What actually blocks each pair:**
  - **Prussia→Hanover** — the one pair the period demands (Prussia occupied Hanover in 1801 and 1806): the restraint is **None** on 7 of 7 seeds, the ladder is **climbed** (two refusals on record) on turns 3–8 on 6 seeds and 8–13 on the seventh, the free ratio is **infinite** (Hanover fields no corps). The ONLY missing clause is the bar. Prussia sits at `coerce` for 27 turns on three seeds and never fights.
  - **Russia→Sweden** — weight 63–77 (coerce on 3 seeds), free ratio 2.7–2.9 (the only true 2:1 case), the ladder climbs at 21–26, and the restraint is **busy** on every turn of every seed: Russia stands in the coalition's war with France, and a court at war opens no second design war (AI-3r). +10 would carry it to 85 on jena and friedland and change nothing.
  - **Austria→Ottoman** (The Eastern Question) — coerce 71–77, ratio 1.1–1.3 (not outmatched), **busy** (at war with France) — the design Step 3 authored for an allied Austria is live but never free.
  - **Sardinia→Austria** — coerce 76–82, restraint **outmatched** (free strength 0): the right answer, never a war.
- **Projection under the ruling:** Prussia's weight reads 80–83 on 6 seeds and 74 on marengo (all ≥ 72); with the crisis opening at `coerce` under the outmatched test, **Prussia→Hanover opens a crisis on 7 of 7 seeds** on turns 3–13, fore-warns two turns, coerces, and declares — the first AI-vs-AI war of the campaign, at the moment Berlin took it in 1806. Russia→Sweden still waits on the coalition's peace (busy), which is the §3.1a descent working as designed: the Finnish War follows Tilsit.
- **Alternatives rejected:** (a) lowering `fight` for AI-vs-AI pairs — re-prices every design, and AI-3r's N7 ruled "the terms climb to the bar, the bar stays" (the reason stands); (b) the `+10` alone — measured inert above; (c) authoring Hanover an army — the historian pin fixes Tier 1 and Hanover in 1805 was a British possession without a field army; (d) retiring the `busy` restraint — the second war a court at war with France cannot open is D1's successor and the coalition's whole shape.

**✅ LANDED October 3, 2026 — the landing addendum follows the build paragraph.**

**The build — slice SF-LB-2 "The Defenceless Prize" (≈0.5 session), the head of Step 4:** the two clauses behind ONE lever `war_council.THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE` (the weight term under `intent.A_HOLDER_WITHOUT_AN_ARMY_IS_A_PRIZE`); reproduce the Prussia→Hanover ladder at its seam first; the ledger's Intent row and Talleyrand's war-room counsel name the clause ("Hanover cannot defend itself — Berlin's design opens at coerce"); the player's own `guarantee_nation` of Hanover is the counter (a guarantor's strength lifts the holder out of the test — that is the D5 instrument earning its keep, pinned); `BASELINE_SERIES` WILL move (Prussia takes Hanover) — re-record ONCE from a flip arm with arm 0 byte-identical; **acceptance = living balance C1** (≥ 1 AI-vs-AI war in 40 turns on ≥ 3 of 7 seeds — projected 7) **plus variance** (the crisis turn spans ≥ 3 turns across the seeds — measured ladder turns 3–13 already do) and the Step-3 guards (F1 ≥ 20 on the commanded seeds, the historian pins, D2 — Hanover is a minor, its capital may fall and eliminate it). Re-open: if every seed produces the same war on the same turn, Britain's guarantee of its king's electorate is the authored counter (AI-3's guarantee rung, GR5).

#### §6.4 landing addendum — SF-LB-2 LANDED October 3, 2026

**Built as ruled, plus three things the ruling did not foresee, each measured first and each behind its own lever** (rules `SYSTEMS_REFERENCE.md` §85; pins `tests/test_sf_lb2_the_defenceless_prize.py` (46 + the driven class); sweep `tools/_sweep_sf_lb2.json` **28 rows → 28 killed, 0 INERT, 0 BROKEN at close (24 for the slice, 4 for the exit's intel fix)** — the first sweep found five pins inert and every one was a real weakness, repaired: the fraction pin read the constant it was testing; the deny-design pin used a court the player guard already excludes; nothing pinned a climbed ladder at `bandwagon`; the ask-at-coerce pin sat inside the refusal-dedupe window; and `coveters_of_prize` carried a second lever guard that the predicate's own made dead — deleted):
1. **Clause 1 — the weight term.** `intent.WEIGHT_HOLDER_OUTMATCHED = 10` under `intent.A_HOLDER_WITHOUT_AN_ARMY_IS_A_PRIZE`, read through the ONE predicate `war_council.holder_outmatched` (the holder's standing plus its guarantors' at most `HOLDER_OUTMATCHED_FRACTION` 0.5 of the asker's FREE strength; an armyless holder counts; an asker with no free strength threatens nobody) — an AST census pins the fraction read in one place and both readers calling the predicate. Both boards (GR5): a France of 125 men holding Hanover hardens Prussia too, and the opening stays AI-vs-AI (NA-5's road). **Boot: Prussia 59/align → 69/bandwagon** — fourteen pins re-seated consciously, each with the reason on the row.
2. **Clause 2 — the opening at coerce.** `war_council.THE_DEFENCELESS_PRIZE_OPENS_AT_COERCE`: `crisis_rung_holds` is ONE reading for the opening (step 3) AND the liveness poll (step 1), so a crisis opened at coerce is not read dead the next turn; the coerce road requires `_restraint_block_reason` None and the climbed ladder; the record carries `opened_at_price`. The player's guarantee of the holder lifts it out of the reading and the crisis passes `deterred` (pinned); a guarantor AT WAR pledges hollow (N3's +6) and a guarantor too small to reach half the asker's free strength lifts nothing (Denmark 16,000, the Ottoman 24,000 against Prussia's 48,601 free) — pinned both ways.
3. **A court asks before it demands** (`ai_diplomacy.A_COURT_ASKS_BEFORE_IT_DEMANDS`). Measured on eylau: the +10 lifted Prussia to `coerce` on turn 2 with ONE refusal on record, the ask arm stops at `bandwagon`, and the coercive demand is the OPEN crisis's beat — so the ladder could never climb and the design sat at coerce for forty turns. The AI-AI design ask now fires at `coerce` while the ladder is unclimbed; the demand still waits on two refusals (pin 8). Eylau's ladder climbs on turn 8.
4. **The fight road reads the restraints at the opening** (`war_council.A_CRISIS_OPENS_ONLY_WHERE_IT_CAN_DECLARE`; the §8 addendum of `AI_WAR_DECISION_SPEC.md`). Measured: the ask-at-coerce refusals lifted Sardinia to `fight` against Austria with a free strength of 0, and the +10 lifted Russia to `fight` against Sweden while at war with France — both fore-warned (twice, on four seeds) wars the restraints already forbade and cooled `outmatched` / `starved` eight turns later. The ruling made the coerce road open only with the restraints clear; the fight road now reads the same predicate. On the seven-seed probe the ONLY crisis any board opens is Prussia's.
5. **A province outranks a friendly namesake** (`combat_executor.A_PROVINCE_OUTRANKS_A_FRIENDLY_NAMESAKE`). Found by driving the war: Prussia declared on turn 11 and its army stood in Berlin for twenty-nine turns. The undefended-capture rung emits `attack Brunswick` for Hanover's province beside Berlin, and the attack arm's 4D-4 refusal read the name as Prussia's own marshal Brunswick (WO-13's exact collision, "the one survivor"), so every turn ended "No valid actions remaining". Where no enemy answered the name and a province on the map carries it, the province is the only reading; WO-13's order (enemy marshal first) is untouched. Prussia now takes Brunswick and the Hanover capital by turn 14.

**Measured (`tools/_sf_lb1_fight_bar_probe.py`, now the slice's harness — it records every crisis's opening rung and every council war the turn it first stands; the record `docs/audits/probes/sf_lb2/`):** 7 of 7 seeds open Prussia→Hanover at `coerce` (turn 9 ×6, marengo 10), declare on 11 (12), and end the war by 14 (15); no other court opens a crisis. **Living balance C1 MET (7 of 7 against the ≥ 3 target).** **The variance clause is NOT MET:** the opening turn is {9, 10} — the ladder climbs on turns 3–8 seed by seed, but the council reads `penniless` (the chest under 500 at its pre-income siting) until Prussia's unseeded economy clears the floor on the same turn everywhere. Not tuned, by the ruling's own instruction ("if every seed produces the same war on the same turn, do NOT tune"); §6 row 14 carries the recommendation (read the chest the council can spend, the ledger's own forecast). The xfail in the driven-board class is strict: it flips the day the clause is met. **→ Row 14 BUILT October 3, 2026 as SF-LB-2b (the second addendum below); the clause is STILL NOT MET — first openings 5 / 5 / 5 / 5 / 5 / 5 / 9 on historical / austerlitz / friedland / jena / ulm / marengo / eylau (per-seed measurements); the chest's turn-4 projection reads 497 against 500 and the ladder is climbed by then on six seeds. §6 row 15.**

**The series** (`tools/_sf_lb2_series_arms.py` → `_sf_lb2_series_arms_final.json`, ten arms): arm 0 reproduces SR-7d's series byte for byte; W, C, K, R and N are each BYTE-IDENTICAL alone (74 outmatched reads on Prussia>Hanover with W up, yet no rung that opens; K alone opens Sardinia's theatre twice without moving the series); **W+C together are the sole mover** (one crisis, one council war, diverging at [28] — declared and never fought); the shipped tree diverges at [21] because N turns the declaration into a campaign. `BASELINE_SERIES` re-recorded ONCE; the chain pins (the drill fix, DP-1, RF-3, VP-R1) gain one link; the WO slice-10 ungated series re-seated from index 15 with the SR-7d figure returning with every lever down (`tools/_sf_lb2_wo_attribution.py`), the collapse pairs / seams / cooldowns and WO slice-9's rebellion turns measured unchanged. M1–M7 byte-identical. Passive France: 3 provinces at turn 40 on both arms.

**Guards:** the historian pins untouched (Prussia at peace with France at boot); D2 — Hanover a minor, its capital falls (Hanover ends with one province on the ambient board; eliminated on austerlitz); `SWEEP_WAR_ALARM` holds (one council war per seed); F1 read at the exit (the commanded seeds).

**The exit** (`tools/score_run.py run --only AIV/CMD-H/CMD-A/CMD-M/OP/FLD/DL` → `docs/audits/score_runs/2026_10_03_sf_lb2/`, re-driven on the final tree; `check` + `compare --base 2026_09_29_c20d5bba`; no score claimed, §5): **this slice's own flips — living balance C1 ✗→✓ (AI-vs-AI wars per seed 0 → 1 on all eight AIV seeds) and C2 ✗→✓ (a standalone third-party settlement on every seed: Hanover's peace with Prussia)**; the AIV arm was unmeasured at SR-7d's exit, so both are read against Step 3's and the baseline's zeros. F1 holds (France 24 / 27 / 22 at turn 40 on the commanded seeds). **One ✓→✗ appeared on the first re-run and was fixed before the commit:** narration C4 — on the historical commanded seed at turn 30 the intelligence row placed Archduke Charles at Tyrol while the store's reader said Franconia; the sighting module skipped every frozen snapshot in a province in full view today (Franconia, where he was last seen on turn 10 and no longer stands) and fell back to an OLDER Tyrol sighting (turn 8). `intel_surfaces.A_FULL_LABEL_KEEPS_ITS_LAST_SIGHTING`: that snapshot rides as `last_known` with its own turn, so the most recent knowledge wins — unless the man STANDS in a full-view province today, where the live read already spoke (SR-6a's own empty-corps / prisoner pin kept) SR-6a's ledger count pin is re-seated consciously — Uxbridge, in fog at Hanover, is a last sighting at Waterloo, and the store's own reader says so; a label with no man on any roster rides nothing.; zero flips against SR-7d's exit after it. Every other flip against the baseline first appeared at an earlier exit and carries its attribution there (Step 2: diplomacy C6, ending C6, first contact C3, marshal drama C3; Step 3: agendas C3, combat F1, living balance C4, ai_aliveness C1 ✓→✗, marshal drama C1 ✓→✗; SR-7d: combat C2 / C3, first contact C4 ✓→✗, ai_aliveness C5 ✓→✗). Standing ✗: narration C1 (Step 7b's), diplomacy C4, the ending C4/C5, marshal drama C1 and AI aliveness C1 (Step 3's board).

**Standing pins re-seated with their attribution** (the full suite's first run: 19 red): the fourteen boot-weight pins (Prussia 59/align → 69/bandwagon, each with the reason); `tests/test_iq6_europe_speaks_its_mind.py`'s seventeen volte-face geometry pins play the pre-SF-LB-2 board — the two §6.4 clauses held DOWN beside the SR-1d league lever the file already holds (measured in-process: Prussia's war on Hanover moves the Austrian courtship's door from turn 20 to never within 23 turns; with the two clauses down it opens at 20 again); `test_ai_intent_assurance.py`'s scene-4 pin re-seated to its SHAPE — the volte-faced Russia now pursues the Gulf and the Straits to the council's war on Sweden (turn 22 on the historical soil arm, France and Britain joining; the Finnish War of 1808 by machinery) and only then advances its deck, never back against France; the NA-6 dead-name pin caught the clause naming a formed nation by its dead name (`formed_display_name` now, both surfaces).

**Census at close:** defect 55 OPEN + 1 partial (SF-LB-2-X1 filed FIXED), design 10 OPEN (SF-LB-2-D1, row 14's).

**Re-open:** the ruling's own — if every seed still gives the same turn after row 14 is answered, Britain's guarantee of its king's electorate is the authored counter (AI-3's guarantee rung cannot fire while Britain is at war with France, which is the whole of 1805). *(Row 14 answered the same day; six of seven seeds still give turn 5. The re-open names a counter that cannot fire in 1805 — said so, and §6 row 15 carries the live recommendation instead.)*

#### §6.4 second landing addendum — SF-LB-2b "The Chest the Council Can Spend" LANDED October 3, 2026 (§6 row 14's build; the clause still NOT MET — §6 row 15)

**Reproduced first, at the council's own seam** (a wrapper on `_restraint_block_reason` inside `process_war_council`, seven seeds): the opening read `penniless` on turns 4–8 with Prussia's live chest at 8 / 272 / 300 / 288 / 491 while the ledger's projection read 497 / 800 / 788 / 716 / 879 — the council sits after the admin phase's spending (`_advance_turn_internal`) and before the income phase, so the chest it read was the post-spending purse of a court that spends its whole purse every turn; the probe's after-turn snapshot sees the post-income chest and reads None, which is why the SF-LB-2 record had said "restraint None" on every seed. **The projection keeps its word:** the forecast on turn t equals the applied chest after turn t to the gold on every row read (497 = 497, 800 = 800, …).

**Built as ruled** (rules `SYSTEMS_REFERENCE.md` §85.8; pins `tests/test_sf_lb2_the_defenceless_prize.py::TestTheChestTheCouncilCanSpend` 12 + the driven class + `tests/test_ai_intent_assurance.py::TestTheStandingRuleOnCouncilWars`; sweep `tools/_sweep_sf_lb2b.json` 9 rows → 9 killed, 0 INERT, 0 BROKEN):
1. **ONE seam** `ledger.chest_forecast(world, nation) → {chest, net, projected}` — the live chest plus the ledger's forward Net (`_build_economy` with no applied record, the figure the LAWS tab and the end-turn banner already quote). `reforms.lapse_forecast` is re-routed through it (its own `chest + net` deleted); an AST census pins that `war_council.py` never calls `_build_economy` and `lapse_forecast` never does either (`ai_purse_refusal`'s bare Net read is a different question and is not counted).
2. **ONE lever** `war_council.THE_COUNCIL_SPENDS_THE_TURNS_INCOME`; **one parameter** `_restraint_block_reason(world, coveter, target, forecast=False)` — with `forecast=True` and the lever up the `penniless` gate weighs the projected chest; `busy` / `outmatched` / `exposed` are untouched by the arm. **Step 3 (the opening) passes `forecast=True`; step 1 (the declaration) passes nothing** — a call-site census pins exactly those two calls and their flags. A fore-warned crisis whose court holds 120 gold is NOT declared even when its income would clear the floor (`last_soft_block == "penniless"`), and declares the poll the chest is filled. GR5: six courts pacified for the pin read the same two verdicts off the seam's own figure (Austria's 405 Net does not carry 50 over the floor — penniless on BOTH arms; Russia / Britain / Spain / Sweden / the Ottoman carry it).
3. The probe records both reads (`restraint_forecast`, `chest`, `chest_forecast`), the aggregate reports EVERY opening per pair and the FIRST (a crisis can cool and re-open), and the seven records in `docs/audits/probes/sf_lb2/` are overwritten with the shipped tree's.

**Measured, seven seeds (each figure a measurement on its seed):** Prussia→Hanover's FIRST opening reads turn **5** on historical, austerlitz, friedland, jena, ulm and marengo and **9** on eylau (was 9 ×6 / 10); the declaration follows on 9 ×5 / 11 (eylau) / 12 (marengo) and the war is over by 12 ×5 / 14 / 15; marengo's first crisis COOLED when its seeded weight dipped below `coerce` on turns 5–8 and a second opened on turn 10. Living balance C1 holds (7 of 7); no other court opens a crisis (Russia→Sweden `busy` on every read, Sardinia→Austria `outmatched`); `SWEEP_WAR_ALARM` holds. **The variance clause is STILL NOT MET: the first opening spans {5, 9}, two turns.** The recommendation's premise — "the opening then falls to the ladder's own turn, which already varies 3–8" — was the pre-SF-LB-2 snapshot's reading and is corrected here: on the shipped tree the ladder (any two refused asks of ANY type, both constant-driven) is climbed after turn 3 on austerlitz / friedland / jena / ulm / marengo, after 4 on historical, after 8 on eylau; and turn 4's projected chest reads **497 against 500** on the six (Prussia's Tier-1 economy plays identically at peace on them), so the CHEST still decides on turn 5 by three gold. What the forecast read did change: the opening no longer waits four turns on a spent purse, the war follows the ladder two turns sooner, and marengo's seeded dip now has a crisis to cool — the WAR's turn varies three ways. **Put to the user as §6 row 15 with a recommendation (seeded patience on the design ask); nothing under it is built; the three xfails stay strict.**

**The series** (`tools/_sf_lb2b_series_arms.py` → `_sf_lb2b_series_arms_final.json`, two arms): arm 0 (the lever down) reproduces SF-LB-2's series byte for byte; the shipped tree diverges at **[21]** — the alarm's tail 7 / 4 / 1 at [21..23] is gone (Hanover falls before the league's business reaches it); the opening's reads counted 5 `penniless` + 1 None → 1 + 1. `BASELINE_SERIES` re-recorded ONCE; the chain pins (DP-1, the drill fix, RF-3, VP-R1) gain one link; **WO slice-10's UNGATED series re-seated from index 15** (`tools/_sf_lb2b_wo_attribution.py`: the earlier war lands the ungated list on the SR-7d figures again — a coincidence of the alarm's arithmetic, stated as such; the lever down returns the SF-LB-2 figure byte for byte), seams 32 / pairs / cooldowns 32 / 0 / the slice-9 rebellion 14 / 17 unchanged. M1–M7 byte-identical. Passive France 3 provinces at turn 40 on both arms. The IQ-6 volte-face file (the §6.4 clauses held DOWN) and the AI-V scene-4 pin hold unchanged. **One SF-LB-2 pin re-seated consciously:** `TestTheOpeningAtCoerce::test_the_coerce_road_needs_the_restraints_clear` had staged the LIVE chest at floor − 1 and expected no opening; the opening now reads the projection by design, so it stages chest + Net = floor − 1 and asserts `penniless` on both reads.

**Census at close:** defect 55 OPEN + 1 partial (unchanged), design 9 OPEN (SF-LB-2-D1 BUILT; the cluster is §6 row 15, a question not a design row).

#### §6.4 third landing addendum — SF-LB-2c "The patient ask" LANDED October 3, 2026 (§6 row 15's build; the clause MET)

The user's Step 5 direction: *"A court that first stands at its design-ask rung waits `campaign_variance.seeded_int(seed, "design_ask_patience::<asker>::<holder>", 0, 4)` turns before its first ask. `historical` = 0 … If they don't flip, amend the clause to read the war's turn … No third attempt."*

**Built (rules `SYSTEMS_REFERENCE.md` §85.9):**
1. **ONE dwell** `ai_diplomacy.design_ask_patience(world, asker, holder)` — the raw `seeded_int` on the ruling's namespace, collapsed to 0 on the historical seed (the caller's contract; the raw helper reads 4 for `historical`) and with the lever `A_COURT_IS_PATIENT_BEFORE_IT_ASKS` down. `DESIGN_ASK_PATIENCE_MAX = 4`.
2. **ONE gate** `design_ask_patience_holds`, read in trigger 0a only (an AST census — the player-targeted design purchase is untouched): the first call that finds the court at its ask rung writes the anchor `world.design_ask_first_stood["{asker}>{holder}"]` (ONE new serialized field); the ask waits until `turn − anchor ≥ patience`. A pair with a design ask already on the refusal record never waits again (the dwell delays the FIRST ask only); a zero dwell writes nothing, so a historical save is byte-identical too. Like the dedupe window, the wait skips the ASK, not the pair — its other triggers still answer.

**Measured, seven seeds (`tools/_sf_lb1_fight_bar_probe.py`, the records in `docs/audits/probes/sf_lb2/` overwritten):** draws historical 0 (collapsed) · austerlitz 3 · friedland 3 · jena 0 · ulm 4 · marengo 1 · eylau 4. Prussia→Hanover's FIRST opening reads **historical 5 · austerlitz 7 · friedland 7 · jena 5 · ulm 8 · marengo 5 (re-opens 11) · eylau 13** — five distinct turns where SF-LB-2b read two; the declaration follows on 9 ×4 / 10 (ulm) / 13 (marengo) / 15 (eylau). The dwell works THROUGH the rung, not around it: on austerlitz the ladder (any two refusals) is climbed by turn 4 as before, but the design ask's own refusal lands on 5, its +6 lifts the weight to `coerce` on 6, and the crisis opens on 7 — so SF-LB-2b's passing pin (`opened <= first_ladder + 2`) is re-stated on what it always guarded, the purse never delaying a READY court (`opened <= first_ready + 1`, ready = the ladder climbed AND the rung at `coerce`+). The historical record is byte-identical to SF-LB-2b's.

**Acceptance:** `test_sf_lb2_the_defenceless_prize.py::TestTheDrivenBoard::test_the_crisis_turn_varies_across_seeds` (driven: 5 / 7 / 13), `::test_the_seven_seed_record_spans_three_turns` and `test_ai_intent_assurance.py::TestTheStandingRuleOnCouncilWars::test_every_pair_that_opens_on_three_seeds_spans_three_turns` — all three flipped; the strict markers are removed and the docstrings carry the history. **No amendment to the war's turn was needed.**

**Gates:** `BASELINE_SERIES` byte-identical (historical = 0, by construction and measured); M1–M7 byte-identical; the live historical run's opening still equals the record's (5). Pins `TestThePatientAsk` (10); sweep `tools/_sweep_step5.json` SF-LB-2c rows: 9 → 9 killed, 0 INERT, 0 BROKEN.

### §6.5 The Armed Peace's fuse — RULED October 3, 2026 (gate record)

**The ruling: the fuse stays at 20 quiet turns and the rise at +3 a turn.** Nothing is tuned.

**The research:**
- **Under the doctrines (`a091db30`) F1 holds 3 of 3:** France 28 / 21 / 22 at turn 40 (historical / austerlitz / marengo); the fuse lapses on turn 29, the league brews on 32 and declares on 35 on every seed — the ruling's own projection (32 / 29 / 31 at fuse 16) one notch later, as the band's end implies. France holds 27–29 provinces into the league and loses 6–7 to a three-power league in five turns on two seeds: the Armed Peace doing what it was admitted to do.
- **The rise is not a lever.** Re-run with `ARMED_PEACE_RISE = 2` (in-process, three seeds): the fuse lapses on 29, the league brews on 33 and declares on 36 — ONE turn later — because the alarm already stands at 51 when the fuse lapses (hegemony keeps adding while the watch withholds decay). France ends 28 / 27 / 22: the austerlitz swing is the league's course changing with the turn, marengo is byte-equal. A one-turn delay bought by halving the climb is noise, not a remedy.
- **The thin margins are the script's.** The commanded arm holds 27–29 provinces at the lapse with 100,000–130,000 men on austerlitz and marengo and never levies; the historical France carries 28 through the league with 28,000. Twenty announced quiet turns and a chest of 70,000 gold are the player's levers, and Step 7b's front page is where they are named (the price to keep each court out).

**Re-open condition:** if a later re-record breaks F1 on a commanded seed, the remedy is Step 7b (the league's rows and prices on the front page) and the script's own levy — not the fuse (the band's end is reached), not the watch (never lowered), not the rise (measured one turn).

### §6.6 SF-NAV-1-D1 "The Tilsit clause" — the A2 anchor — RULED October 4, 2026 under the user's delegation (gate record; FOR USER CONFIRMATION)

> The user (Step 7's brief): *"RULE §6 ROW 17 … Research before deciding: play the conquest road the Step 6 arm never tried … Arithmetic … My recommendation: (a) the Tilsit clause on a separate peace … Add the missing exit … re-word A2 … Done-when: an arm holds SHUT OUT for 8 consecutive turns on at least 2 of 3 seeds, and the gate record names the road(s) that do it."*

**The ruling: (a), as recommended — the Tilsit clause on a separate peace — with the exit the System lacks and A2 re-anchored to what play measures.** The conquest road is kept as a road and named here; the done-when is read on whichever road holds.

**The research** (memo `docs/audits/SF_NAV1_D1_THE_A2_ANCHOR_2026_10_04.md`; archives `docs/audits/playtest_digests/sfnav1d1-danube-*/`, `sfnav1d1-road-*/`, each with the probe's JSON). Every figure is one played campaign on one seed — three seeds sample the roads the board offers; they prove no road always open or always shut.
- **The conquest road, played on the three benchmark seeds (two committed drafts, two more unkept):** the Danube-first draft peaks at 10–11 of 26 and never holds — Vienna is not taken on any seed (Archduke Charles's army breaks the marches on the Bohemian road and Vienna keeps 25,000 behind him), and meanwhile the Peninsula goes unhunted; the Step 6 arm plus Hanover peaks at 11–13 and holds SHUT OUT once, for 3 turns (marengo turns 13–15), never after Spain's exit (closure 6–10 from turn 17) — Hanover falls to Prussia on two of three seeds (the Defenceless Prize; a Prussian Hanover closes nothing, Prussia being at peace with Britain).
- **The record board:** the hand-played turn-24 save (47 titled provinces, the Congress summonable) holds Vienna and Hanover and reads **9 of 26** — Spain, France's ally, holds Lisbon; Rome and Naples would bring the road to 11.
- **The arithmetic:** after Spain's exit, 13 (the 50% line) wants all eight capitals at once — France, Holland, the Kingdom of Italy, Lisbon, Rome, Naples, Vienna, Hanover — with no margin; tier 2 (16) wants Spain's 3 back or three ports from courts at peace with Britain (each a new war); A2's 80% (21) leaves five of 26 ports open in all Europe.
- **Found first, fixed (SF7-X1, an instrument defect):** the driver signed armistices with courts on its own `--decline-from` list (8 of the 12 draft runs; Step 6's committed NAV1-H arm accepted Portugal's on turn 20) — a stale answer's refusal re-carries the STORED dialogue, whose court the driver never read. Step 6's table reproduces with the fix.

**The build contract** (Step 7's row-17 slice, item 4 of the brief):
1. **The clause `continental_system`, "joins the Continental System"** — canonical `{type, from, to}`: `from` = the court that joins, `to` = the court that imposes it. No alliance (Prussia and Russia at Tilsit, 1807; Austria at Schönbrunn, 1809).
2. **ONE membership write** — `diplomacy.join_continental_system(world, nation, imposer, reason)`, extracted from `settlement_ratify`'s forced-alliance arm; that arm, the bilateral forced-alliance arm and the new clause on both roads call it. The +10 alarm on the imposer is `FORCED_ALLIANCE_CONTINENTAL_SYSTEM_THREAT_SURCHARGE`, one source. Joining rides the existing `diplomatic_continental_system` beat.
3. **Who may be asked — one predicate**, read by the authoring row, both previews and both ratification arms (honest availability, with its reason): the court has continental ports (a non-island `navies` row, ports > 0); it is not already a member; it is not the trade-dominance court; it is not the imposer's satellite or puppet (those join on their own); the imposer is the player — the System is France's own instrument (`apply_continental_system` reads the player as its lord), so no AI writes the clause (GR5 by scope, recorded).
4. **The price, in both harshness dialects** (`calculate_raw_treaty_harshness`, clauses and demands): **0.2** — half a forced alliance's 0.4, below a one-province cession's 0.3 (the court keeps its soil and its sovereignty and gives up its British trade). In the bilateral acceptance `DEMAND_VALUES["continental_system"] = -10` (half the forced alliance's −20), and it counts as a material demand (the war-age penalty applies). "A court the Emperor has beaten" is what the court's own acceptance reads (its war-score term) — not a second gate. In-band tunable; measured at the build: a court at an even war score refuses it, a beaten one signs.
5. **Carried by the separate peace:** `PAIR_SUBSTITUTE_CARRIED_TYPES` gains it (its "the Continental System" dropped label retires); the bilateral demand dialect carries `from`/`to`; `_ratify_treaty` applies it after the peace.
6. **Shown:** the guided "Add demand" row (its terms: the alarm and the System's count, "closes 14 → 15 of 26 ports"); both previews; the ratification summary; the joining beat; THE ADMIRALTY's System line names the members.
7. **The exit:** a member that goes to war with the imposer leaves the System at `set_diplomatic_state`'s WAR transition (every road to war inherits it), as a named beat — `diplomatic_continental_system` with "left" and its reason — and a campaign-log line. The vassal arms are unchanged.
8. **A2 re-anchored** (`NAVAL_SPEC.md` §5.1 and §7): *SHUT OUT — the System at ≥ `cs_shutout_pct` of the Continent's ports with no British corps on the Continent — holds for 8 consecutive turns (a sitting's length) on a played road, on at least 2 of 3 benchmark seeds. Britain sues from her own war; the System is the squeeze that keeps her at the table, not the cause.* The ≥ 80% figure is retired as unreachable (21 of 26 ports).
9. **Must not break:** `BASELINE_SERIES` and M1–M7 byte-identical — the clause is the player's and no AI writes it, and the exit fires only on a member (none on the ambient board; measured at the build, not assumed); the forced-alliance arms' threat and membership byte-identical through the extracted helper.

**Done-when:** an arm holds SHUT OUT for 8 consecutive turns on ≥ 2 of 3 seeds, and this record names the road(s) that do it. The Tilsit road's arm is new (`tools/playtest_scripts/sf_nav1_tilsit_road.json`, benchmark `NAV1T-H/A/M`: the Step 6 arm, plus the clause on Austria's and Russia's separate peaces); NAV1 is re-read beside it. If no arm holds, the miss is reported and attributed and comes back here — the 50% line is not tuned.

**Rejected:** (b) binding a hegemon's ally to the war, (c) counting an ally's ports at peace, (d) re-anchoring A2 to tier 1 with no new road (row 17's arguments); and the conquest road as the anchor's only road (measured above — it may still be one of the roads the record names).

**Re-open condition:** a court at an even war score signing the clause (the price rises in-band); or the conquest road holding on a played arm (A2 then names both roads).

**Landing addendum (Step 7 slice 4, October 4, 2026).** Built as contracted, with one naming deviation FOR USER CONFIRMATION: the clause is `continental_system_join` (the bare `continental_system` is the alarm's source key and the separate peace's retired dropped-label key, and beside `continental_system_lifted` the verb says which way it moves). Item 4's measurement holds (§93.5: at war age 10, level with France, Austria 24 and Russia 28 against 50; Austria signs at 60 points, Russia at 45). Item 9 holds: `BASELINE_SERIES` and M1–M7 byte-identical, measured with the reach counted (no member, no join, no exit in forty turns). Found building it: SF7-X5 (fixed), SF7-X6 (fixed); found playing it: SF7-X7 (homed to Chunk 9). **The done-when — an arm holding SHUT OUT 8 consecutive turns on ≥ 2 of 3 seeds — is NOT met: 1 of 3.** The road the record names: **the Tilsit clause on the separate peaces with Austria and Russia, an offered sum to a court not yet beaten enough** (`tools/playtest_scripts/sf_nav1_tilsit_road.json` (benchmark `NAV1T-H/A/M`)). **historical** — Russia signs on turn 12, Austria on turn 13; SHUT OUT holds **turns 14–30, 17 consecutive turns**, peak **16 of 26 (tier 2, reached for the first time)**; Austria is drawn back to war by the next coalition on turn 20 and the line holds through its exit (16 → 15). **austerlitz** — Russia turn 12, Austria turn 13; peak 16 (tier 2) on turn 14; **SHUT OUT never** — British corps stand on the Continent all 30 turns: Moore lands 25,000 at Guyenne by turn 10 and campaigns in France's south-west (Bearn, Cartagena, Guyenne, Maine) with Wellesley and Shrapnel, and after Austria's separate peace Austria's closed frontier (Champagne, Burgundy and Berry — the status-quo peace left them to it) refuses every French march toward him (SF7-X7); Russia is drawn back to war on turn 17 (closure 13 → 11) and re-signs on turn 24. **marengo** — Russia turn 12, Austria turn 19; peak 16 (tier 2) on turns 13–15; **SHUT OUT never** — 13 of 26 holds turns 16–21 while Shrapnel stands with the Austrians (Hungary, Vienna), and the turn he is gone (22) Russia's return to war takes the closure to 11. The attribution, every seed: the next coalition forms 5–9 turns after the separate peaces (each signing adds the System's +10 alarm) and draws a signatory back to war, and the exit takes its ports — historical held because it had three ports of margin over the line; the other two did not. The 50% line is not tuned (§6.6). Three drafts were played (v1, v2 not kept): v1 — the Step 6 arm with the bare clause every two turns; declining Austria's truce cost the Emperor (captured turn 8 after answering Ney's muster at Swabia); historical SHUT OUT 3 turns. v2 — the Emperor marches to Paris on turn 1, Soult's road to Lisbon is not diverted, the proposals respect the 5-turn same-type cooldown; historical 8 turns (15–22), austerlitz and marengo 0 — each seed signed only ONE of the two courts. v3 (the committed arm) — an offered sum with the clause to a court not yet beaten enough (2,000 rising to 4,000 gold on each retry), and the corps the peaces free join the hunt: Russia signs on turn 12 on all three seeds. **The NAV1 re-read** (Step 6's arm, unchanged; archive `docs/audits/playtest_digests/sf7s4-nav1-reread/`): historical 11 of 26 / never, austerlitz 12 / never, marengo 14 / turns 12–15 (4) — **identical on the pre-slice tree `c5ef3a60`** (slice 4 is inert on it: the System is empty all game). Step 6's own table (14 / turn 11; 12 / never; 13 / turns 13–15) reproduces exactly at slice 2's commit `b127e41e`, and historical already reads 11 / never at slice 3's `ee743a3c` — slice 3's field read moved this arm's battles. **Under this record's own rule the miss comes back to the user:** §6 row 17 stays open as a design row (owner `DESIGN_REFINEMENT.md` SF-NAV-1-D1); the clause, the exit and A2's wording stand as built. What the measurement leaves to decide: whether a court that keeps the System by treaty may be drawn into the next coalition while its peace is young (today it may, after the pair floor — the AI's war behaviour, which this ruling was not to touch), or whether A2 reads 1 of 3 as enough.

## §7 Done when

1. **Every live defect row is closed.** `tools/defect_census.py --open` lists none, except rows this spec hands to an owner outside it under a GR9 contract (owner, landing slice, completion definition, STATUS line, behaviour test).
2. **Every design row is disposed:** closed, ruled, built, or owned by a named slice or gate that exists.
3. **The final reading matches the baseline's method.** It ran on the same instrument and checklist version as the baseline (or on the baseline re-read under the new version).
   - Every pillar is exercised and at its target item count, with both floors green and no verified open P1. Otherwise the memo says, per pillar, why not and who owns the residue.
   - No pillar's item count fell. A fall blocks until it is explained.
4. **The panel is published:** its median and spread. A move smaller than the spread is not claimed.
5. **A played road reaches the Congress**, and the sitting either holds to THE IMPERIAL PEACE or dissolves only for a cause the player can see (SF-END-1, and the CONG arm).
6. **The §6 rulings are answered:** built, struck, or re-homed.

---

## §8 What this supersedes

- **`SCORE_MANDATE_PLAN.md` §1's scoreboard** → the instrument (§4). Its interim numbers stay as history.
- **Its §5 measurement rule** → §5 here. Kept: the session exit, the residue slice, and no mid-way re-score. Added: the baseline and final readings, and the census and checklist reads at each exit.
- **Its §2 Chunk 6 bullets** → Step 2. Six of seven had landed in Chunks 1–2.
- **Its §2 Chunks 7, 8, 9 and 3b** → Steps 3, 5, 7 and 4, with the rows §1 found added.
- **Its §3 quick-win bank** → Step 2's reserve and Step 4. RS-4, RS-12 and RS-15 move to CRT-9's one probe; RS-10 and RS-16 ride Step 1.
- **Unchanged:**
  - the mandate's §0 principles: every pillar rises and none falls; a played campaign's P1s jump the queue; design before build; the four-file rule; balance attributed;
  - its §4 gates;
  - the ROADMAP spine after the program.

---

## Appendix A — the checklist, version 1 (FROZEN September 29, 2026 — taken at the recommended default under the user's "proceed", §6 row 2; the machine copy is `docs/SCORE_CHECKLIST_V1.json`; the user may amend, and a new version re-reads the baseline archive)

**Legend:**
- **F** = floor, **C** = ceiling.
- **Kind:** A = AUTO, P = PROBE, E = EYES.
- **Today:** ✓ / ✗ where it was measured on the `rs0928-*` archives at `c20d5bba`; blank = not yet measured (the baseline reads it).
- Arms refer to §4.2; **T** = titled provinces (`tools/sr1e_titled_probe.py`).
- **Baseline (Sept 29):** ✓ / ✗ / · as the instrument read each item on `c20d5bba` (Step 0's baseline reading; the evidence line for every mark is in `docs/audits/score_runs/2026_09_29_c20d5bba/checklist.json`).

**The ending (target 7.0 = 3 ceilings)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | Pressburg reaches THE IMPERIAL PEACE by turn 36 | A | ✓ | ✓ |
| F2 | The Verdict arm reaches its turn-44 register | A | ✓ (re-run Sept 28: the Verdict at t44, "Eclipse") | ✓ |
| C1 | On CONG, the Congress is never dissolved by a cession reopened in a war France neither declared nor joined, and a fall names its cause (RS-2) *(re-worded Sept 28: the first wording failed on the passive driver losing Moravia, a real loss that SHOULD break the hold)* | A | ✗ | ✗ |
| C2 | The CONG summons names the league gate it lowers (RS-10) | A | ✗ | ✗ |
| C3 | The CONG alarm forecast matches the next tick ±1 (RS-16) | P | ✗ | ✗ |
| C4 | T ≥ 40 at turn 40 on 2 of 3 CMD seeds | A | ✗ (36/34/36) | ✗ |
| C5 | Some benchmark road reaches T ≥ 45 by turn 40 | A | ✗ | ✗ |
| C6 | On CONG, each refuser's price can be paid within the sitting, or the table says it cannot (RS-D1) | P | ✗ | ✗ |

**Diplomacy (7.0 = 3)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | The propose arm ratifies a peace on every seed | A | | ✓ |
| F2 | The advisor arm ticks at least 2 mission types | A | | ✓ |
| C1 | No French peace is broken within 5 turns by another court's cascade (RS-1) | P | ✗ | ✓ |
| C2 | A ratification label names only the covered courts (RS-9) | P | ✗ | ✓ |
| C3 | VOLTE fires `volte_face` (RS-27) | A | ✗ | ✗ |
| C4 | DL's eight Cabinet phrasings each start a mission or give a priced refusal (RS-7) | A | ✗ | ✗ |
| C5 | DL's "request terms from Austria" is answered honestly: by Austria, or by the coalition's leader named as the court that answers for the war (PC15-6) *(re-worded Sept 28: the first wording contradicted PC15-6's shipped design)* | A | | ✓ |
| C6 | No treaty France accepts from an AI offer fails its own ratification (SF-V1) | A | ✗ (14 on 5 arms) | ✗ |

**First contact (7.5 = 4)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | FC has 0 shrugs and 0 refusals | A | ✓ | ✓ |
| F2 | SCH reaches card XIX | A | ✓ | ✓ |
| C1 | At most 2 of HOLD's 20 questions shrug | P | | ✗ |
| C2 | No HOLD answer contradicts the save | E | | · |
| C3 | DL's "where are the Russians" and "why is Europe alarmed" are answered (RS-14) | A | ✗ | ✗ |
| C4 | DL's "what can I do" at 0 military actions names a legal order (RS-15) | A | ✗ | ✓ |
| C5 | Every TODAY order in the boot briefing executes | P | | ✓ |
| C6 | OP's first loop has 0 reading refusals | A | ✓ (OP loop 1: 10 of 10 succeed) | ✓ |

**Economy (7.0 = 3).** The size of the treasury is ruled intended (SRX-D1) and is not read.

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | `net_residual` is 0 on every record | A | ✓ (0 of 457) | ✓ |
| F2 | Britain's turn-1 Net exceeds France's (SR-5a) | P | ✓ | ✓ |
| C1 | On LAW, the Staff is enacted by loop 9 | A | ✗ (SF-V3) | ✓ |
| C2 | Every Net-line move of 10% or more names its cause | P | | ✗ |
| C3 | The quoted Charges and Laws equal what the next turn applies | P | | ✗ |
| C4 | Every priced order charges what it quoted | P | | ✓ |
| C5 | DL's levy at 0 military actions executes (AAR-6) | A | ✓ | ✗ |
| C6 | On CMD turns 20–40, "what can I do" names an affordable purchase on ≥ 80% of turns (RS-D3) | P | | ✓ |

**Naval (7.0 = 3)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | The naval-gate tests are green | A | ✓ | ✓ |
| F2 | SEA has no blocker and no `SCRIPT PRECONDITION` | A | ✓ | ✓ |
| C1 | SEA quotes the second diversion at readiness −25, and both throws print | A | ✓ | ✓ |
| C2 | A fleet action leads the next dispatch | A | ✓ | ✓ |
| C3 | The descent quote names the odds and a lever, and Munster falls | A | | ✗ |
| C4 | On the shut-out arm, Britain sues by turn 10 on 3 of 3 seeds | A | | ✓ |
| C5 | The ports lever explains "(now 0)" during a truce (RS-25) | P | ✗ | · |
| C6 | The Admiralty and fleet frames pass | E | | · |

**Living balance (7.0 = 3).** The unattended France's collapse is ruled intended and is not read.

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | On CMD, France holds ≥ 20 provinces at turn 40 on 3 of 3 seeds | A | ✓ (30/29/27) | ✓ |
| F2 | `BASELINE_SERIES` and M1–M7 are green | A | ✓ | ✓ |
| C1 | AIV-C shows at least one war between two AI courts | A | ✗ | ✗ |
| C2 | AIV-C shows at least one standalone third-party settlement | A | ✗ | ✗ |
| C3 | AIV-C shows exhaustion-driven pair peaces on every seed | A | ✓ (10 of 10 seeds) | ✓ |
| C4 | On CMD, after the general peace, a court declares war on France beyond the fresh-peace floor and not by cascade (PB-D1) | A | ✗ | ✗ |
| C5 | On CMD after the peace, every sponsorship against France and every great power that newly qualifies for a league leads or sub-beats the next dispatch, and each quoted keep-out lever flips `qualifies_for_coalition(relation_shift=)` (Step 7b) *(replaces "threat rises after the peace", which C4 implies once SR-G7 lands)* | P | ✗ | ✗ |
| C6 | On every AIV-C seed, an AI court takes a province from another AI court | A | ✓ (10 of 10 seeds) | ✓ |

**Combat legibility (7.5 = 4)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | Every player battle is logged with both sides' losses | A | | ✗ |
| F2 | OP's turn-4 scout of Vienna names the garrison | A | ✓ | ✓ |
| C1 | Every attack that fought printed its muster first, including through an objection (RS-13) | A | ✗ | ✓ |
| C2 | The bands are monotone: "favorable" attacks out-bleed the enemy ≥ 70% of the time, and more often than "even" | A | ✓ (24/24 vs 9/12) | ✓ |
| C3 | An occupied capital's garrison fights, or is named (RS-3) | P | ✗ | ✗ |
| C4 | DL's what-if for a fortified marshal refuses as the order would (RS-12) | A | ✗ | ✗ |
| C5 | No raw marshal keys in combat text (RS-26) | A | ✗ | ✗ |
| C6 | The diorama frames pass at both scales | E | | · |

**Marshal drama (7.5 = 4)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | On the flagship arm, `_pc15_10_acceptance_probe.py` shows ≤ 4 petition modals and 0 silent losses | P | ✓ | ✓ |
| F2 | On OP, a grievance fires, is heard and resolves | A | | ✓ |
| C1 | OP shows ≤ 3 petition modals and ≥ 3 audiences | A | ✓ (3 and 10) | ✓ |
| C2 | A Trust answer names only a man we can see and reach, and a refused Trust keeps the order (RS-5) | P | ✗ | ✓ |
| C3 | No marshal repeats a victory line within his last three wins (RS-24) | P | ✗ | ✗ |
| C4 | The crown moves only on ≥ 3 glory, and the line names where it went | A | | · |
| C5 | An unmet expectation is announced before trust erodes | P | | ✓ |
| C6 | Five sampled petitions each read in the marshal's own voice | E | | · |

**Vassals (7.5 = 4)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | On CMD, ≥ 2 of 3 satellites remain at turn 40 on 3 of 3 seeds | A | ✓ | ✓ |
| F2 | CMD-H with `--client-petition refuse` loses a satellite by turn 30 | A | | ✓ |
| C1 | CMD shows ≥ 4 priced petitions | A | ✓ (6/4/8) | ✓ |
| C2 | A petition's applied effect equals its quote | P | | ✓ |
| C3 | No French peace leaves a client state at war (SR-1b) | P | | ✓ |
| C4 | Loyalty under 40 draws a line naming the remedy | A | | ✗ |
| C5 | An attacked client capital is contested within 2 turns (VD-C) | P | ✗ | ✗ |
| C6 | The VASSALS tab frame passes | E | | · |

**UI/UX (7.5 = 4)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | CLI: 0 `SCRIPT ERROR`, 0 blank frames, every shot ok | A | | · |
| F2 | The parse harness exits 0 and the boot smoke test is clean | A | ✓ | · |
| C1 | No frame has `buttons_offscreen` | A | | · |
| C2 | No frame has `clipped_text` | A | | · |
| C3 | No frame's text shows a raw key, `<null>` or `(s)` | A | | · |
| C4 | On OP, no end turn raises more than 3 blocking popups (a rail audience is not a blocking popup) | A | ✗ (max 4 blocking; the shape is SF-V5's letter + an incoming treaty) | ✗ |
| C5 | The user signs off ≥ 9 of 10 named frames | E | | · |
| C6 | In a 5-turn Mode C session, nothing is blocked and every hotkey works | E | | · |

**Command & parsing (8.0 = 5)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | The golden corpus passes 100% | A | ✓ | ✓ |
| F2 | The keyless replay passes 100% | A | ✓ | ✓ |
| C1 | OP: ≤ 1 shrug in 127 lines | A | ✓ | ✓ |
| C2 | OP: 0 reading refusals (of the "Cannot find marshal 'Of Ney'" kind, which the hand-played retest met on turn 1) | A | ✓ (none on OP) | ✓ |
| C3 | ≥ 18 of HOLD's 20 orders execute as meant | P | | ✗ |
| C4 | DL's "in support of", "march on X and destroy Y" and "take" execute (RS-6/8/11), and "attack Zorglub" / "attack Alsace" ask without spending anything (SF-V4, §6.3) | A | ✗ | ✗ |
| C5 | On `typed_road.json`, question turns spend 0 actions and order turns spend them | A | | ✓ |
| C6 | OP on the live parser has ≤ 1 misread | A | | · |

**Narration (8.0 = 5)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | Every turn has a headline, and none shows a raw key | A | ✗ (58 of 120 CMD turns have no headline; Step 7b) | ✓ |
| F2 | A dispatch carries ≤ 2 routine intent lines plus a tail | A | | ✓ |
| C1 | No headline class leads more than 4 of any 10 turns (RS-D2, Step 7b) | A | ✗ (7 of 10 on CMD-H: Lannes's arrears on 20 turns, the levy on 10) | ✗ |
| C2 | No rail row repeats more than 3 times a turn, and every war entry names its enemy (RS-23) | A | ✗ | ✓ |
| C3 | The near-miss and summonable headlines fire (RS-17) | P | ✗ | · |
| C4 | The dispatch's intel row matches the intel store (AAR-5) | P | ✗ | ✓ |
| C5 | Le Moniteur keeps its cadence and its special editions | A | | ✓ |
| C6 | Ten sampled dispatches each lead with the turn's biggest event | E | | · |

**AI aliveness (8.0 = 5)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | `test_ai_intent_assurance.py` is green | A | ✓ | ✓ |
| F2 | No arm has a blocker or a traceback | A | ✓ | ✓ |
| C1 | The rival courts enact 13–18 laws with 0 lapses | A | ✓ | ✓ |
| C2 | Every 40-turn arm has ≥ 1 design promotion | A | ✓ | ✓ |
| C3 | Britain lands on the continent on every CMD arm | A | ✓ | ✓ |
| C4 | No AI assaults a garrison under 500 men three times running (AAR-D8) | P | | ✓ |
| C5 | No AI corps fortifies, unfortifies and fortifies again within 3 turns | P | | ✓ |
| C6 | On CMD, visible AI attacks occur on ≥ 50% of the turns at war | A | ✓ (on a knife edge: 5 of 10, 8 of 11, 7 of 11; SR-7a's odds gate removes attacks) | ✓ |

**Agendas & formables (8.5 = 6)**

| # | Item | Kind | Today | Baseline (Sept 29) |
|---|---|---|---|---|
| F1 | The agenda and formables tests are green | A | ✓ | ✓ |
| F2 | `/formables` on every CMD save lists each template with its gate terms | P | | ✓ |
| C1 | Every 40-turn arm has ≥ 2 `agenda_shift` events | A | ✓ | ✓ |
| C2 | On AIV-B, a variance seed opens with a different design (D7) | A | ✓ (ulm, austerlitz, marengo and lodi open with `primacy_germany`) | ✓ |
| C3 | A gate term flips to met during play | P | | ✗ |
| C4 | The TILSIT probe raises `nation_proclamation` | P | | ✓ |
| C5 | On SF-AGD-1's arm, a carve states its terms and the Proclamation card fires *(re-anchored Sept 28: the CMD-ulm carve was an accident of Archduke Charles overrunning Normandy)* | A | | · |
| C6 | The Proclamation and formables frames pass | E | | · |
