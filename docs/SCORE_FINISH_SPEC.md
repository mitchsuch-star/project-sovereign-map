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
> **Reading map:** §0 why · §1 the census · §2 the pillars · §3 the build order · §4 the scoring method · §5 cadence · §6 the user's rulings · §7 done when · §8 what this supersedes · Appendix A the checklist (v1, draft).

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
- **SF-V4 (P2, needs a ruling): an attack on a proper name the map does not know fights the nearest enemy.**
  - "Ney, attack Zorglub", "attack Alsace" and "attack Lombardy" each read "Your words named no foe our maps know, Sire — Ney marches on Mack at Swabia", then fight him. Reproduced by hand: Ney 24,000 → about 21,900.
  - An *address* to such a name spends nothing (CX-R1).
  - CX5-L5-F8 ruled the substitution designed for a descriptive phrase ("smash the retreating column"); a proper name was never ruled.
  - → CRT-10 with NPC-6, after §6's ruling.

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

The Sept 28 column is the retest's impression score. The instrument's baseline (§5) will re-base every row, and several will read **lower**:
- a verified open P1 caps its pillar, which today hits the ending and diplomacy;
- most of living balance's ceilings are unmet.

That is the new ruler, not a regression. Targets are stated as ceiling counts (§4.4).

| Pillar | Sept 28 | Target | Still docked (open rows) | The lift (§3) | Could fall if |
|---|---|---|---|---|---|
| **The ending** | 6.75 | 7.0 (3 ceilings) | RS-2 (P1), RS-D1, RS-10, RS-16 | Step 1, "The peace holds", with SF-END-1 as its exit (the sitting played to its end from the turn-24 save) | RS-D1 is left as it stands (the sitting stays unwinnable at −90), or "contested but counted" softens the finish too far |
| **Diplomacy** | 6.75 | 7.0 (3) | RS-1 (P1), SF-V1, RS-7, RS-9, RS-18 … RS-22, CQ-36, CX-X3, NPC-21 | Step 1 (RS-1, SF-V1); Step 2 (SF-DIP-1 "the dial survives the drop"; SR-6b copy); Step 4 (CRT-8) | RS-1's fix changes alliance calls (one series re-record) |
| **First contact** | 7.0 | 7.5 (4) | RS-12, RS-14, RS-15, SRX-5, RS-6, RS-7, CX3-X2, CX3-X3, CX-BEHAV-1 | Step 2 (RS-14, SRX-5); Step 4 (CRT-9 with RS-12/RS-15; SF-CMD-1's first hour); Step 7 (the first ten minutes in the client) | The sourced lines are saturated, so a scorer's own phrasing decides (the HOLD arm, §4.2) |
| **Economy** | 6.75 | 7.0 (3) | RS-D3 (evidence for SR-G7) | Step 3 (SR-G7 gives the chest a war to fund); Step 6 (SF-ECON-1, only if the items still fall short) | A new sink re-opens SR-5a's balance |
| **Naval** | 6.75 | 7.0 (3) | RS-25; SHUT OUT has never held on a played board | Step 6 (SF-NAV-1 "the strangulation, played") | Britain sues from its own war exhaustion before the System bites (6 of 6 arms) |
| **Living balance** | 6.5 | 7.0 (3) | SR-G7 / PB-D1 (the long peace); 0 AI-vs-AI wars; RS-3, RS-27, CQ-22, IQ5-R1, XR-3 | Step 3: SR-7b measures → SR-G7 ruled and built → SF-LB-1 "Europe's own quarrels" | A standing "Brewing" re-opens IQ-3's revolving door |
| **Combat legibility** | 7.0 | 7.5 (4) | RS-3, RS-4, RS-12, RS-13, RS-26, NPC-13, NPC-17, NPC-25, AAR-5, AAR4-X2, AAR24-X4 | Step 3 (RS-3); Step 2 (RS-13, the AAR rows); Step 4 (SF-CL-1 "the forecast keeps its word") | SR-7d moves the arrival odds (the threshold exists in three copies) |
| **Marshal drama** | 7.0 | 7.5 (4) | RS-5 + VP-R1-X1, RS-24, NPC-11, CQ-38 | Step 2 (RS-5 + VP-R1-X1; SF-MD-1 "every man his own voice"); Step 7 (B1's audiences on screen) | Floors that bind 0 times, and audiences nobody opens, make the game quiet |
| **Vassals** | 7.0 | 7.5 (4) | IQ7-D1 (VD-C), IQ7-D3, IQ7-X1, IQ7-X3, CX-X3, VP-D9, IQ7-D4 | Step 5 (SR-8a VD-C, SR-8c) | VD-C touches marshal strength at four exits |
| **UI/UX** | 7.0 (carried) | 7.5 (4) | S5-4, WO-V-D1, WO-V-D2, WO-D14, CX3-R2 … CX3-R12 (8), EAS-2, SRX-6 / SF-V2, the owed sign-offs | Step 7: Chunk 9 as a driven client pass, plus the user's eyes | Skipped again: the pillar is NOT EXERCISED and the directional cannot count it |
| **Command & parsing** | 7.5 | 8.0 (5) | RS-6, RS-7, RS-8, RS-11; CQ-8, CQ-21, CQ-24, CQ-28, CQ-33, CQ-38; CRT-6's CX5-L5 rows; NP-X1, NP-X8, NP-X9, NP-X10; NPC-6, NPC-9, NPC-10, NPC-18, NPC-26; PC15-13; SF-V4 | Step 4: SF-CMD-1 "the unrehearsed line", then Chunk 3b trimmed to what it confirms | New verbs regress the negation and question guards |
| **Narration** | 7.5 | 8.0 (5) | RS-D2, RS-17, RS-23, RS-24, AAR-5, NPC-14, NPC-15, NPC-23, NPC-24, NPC-27, IQ6-D3, EAS-2 | Step 2 (SR-6a/6b/6c); Step 3 gives the quiet middle news to lead with | Once the levy yields, peace turns have no lead story |
| **AI aliveness** | 7.5 | 8.0 (5) | AAR-D8 (the garrison grind, the dithering), RS-27 | Step 3 (SR-7a, SF-LB-1, SR-7d) | The Hofkriegsrat drops Austrian arrival odds sharply |
| **Agendas & formables** | 8.5 (carried since Jul 25) | 8.5 (6) | The Proclamation has never been seen from play; IQ7-D3; IQ6-D1 | Step 5 (SR-8b + SF-AGD-1: a carve to a Proclamation on a played road) | A July score on a build from before the mandate; one 0.5 fall here breaks the directional |

---

## §3 The build order

| Step | What | Sessions | Pillars |
|---|---|---|---|
| **0** | SF-0 the ledger tells the truth · SF-M the instrument + **the baseline reading** | ≈1.5 | measurement |
| — | The user's rulings (§6) — no build session | — | gate Steps 1, 3, 4 and 5 |
| **1** | "The peace holds": RS-1, RS-2 (+ RS-D1), RS-10, RS-16, SF-V1; SF-END-1 as the exit | ≈1.5 | the ending, diplomacy |
| **2** | Berthier tells the truth: Chunk 6 rebuilt, plus the reserve, SF-MD-1 and SF-DIP-1 | ≈4.0 | narration, drama, combat legibility, diplomacy, first contact |
| **3** | Europe acts without France: Chunk 7 as one balance block, SR-7d last | ≈6.5 | living balance, AI aliveness, economy |
| **4** | The three misses, second pass: SF-CL-1, SF-CMD-1, then Chunk 3b trimmed to what the census confirms | ≈5.3 | combat legibility, command, first contact |
| **5** | The client stands: Chunk 8 + SF-AGD-1 | ≈2.0 | vassals, agendas |
| **6** | The chest and the sea: SF-NAV-1 (+ SF-ECON-1 only if needed) | ≈0.7 (+1.0) | naval, economy |
| **7** | What the wire says, the screen says: Chunk 9 + the user's eyes | ≈2.0 | UI/UX (+ first contact, drama) |
| **8** | SF-R, the final reading | ≈1.0 | all |
| | **Total** | **≈24–25** | |

**Why the total is larger than the ≈12 sessions the mandate carried for Chunks 6–9 and 3b:**
- Chunk 6's written bullets had six of seven rows already landed, while its real load (the retest's copy rows and the NPC rows homed to it) is about four times its ≈1.0.
- The orphaned rows of §1.5 come back.
- The capability slices the three misses need are new.

**Why this order:**
1. The P1s first (the mandate's §0-4).
2. Display-only work that touches seven pillars: cheap, no series moves, and the checklist shows it.
3. The weakest pillar's balance block.
4. The misses' second pass, after the resolver has changed.
5. Vassals and agendas.
6. The economy and naval close-outs.
7. The client last, so its frames cover everything.
8. The reading.

The baseline is pinned to `c20d5bba`, so Steps 0 and 1 may swap if the user wants the P1s fixed first. The baseline then runs on a detached worktree.

### Step 0 — the ledger and the instrument (≈1.5)

**SF-0 "The ledger tells the truth" (≈0.3; docs and the census only).**
- Strike the 29 stale defect rows and mark the 45 design rows, each with its evidence (§1.3). Mark CA9-P2 and CA9-P3 as notes, and CX5-L5-N3 as CQ-33's pointer.
- Re-home every orphan named in §1.5 to its step here, and give NPC-12's row its open-remainder marker.
- Tag each live row with its pillar, and add `--by-pillar` to the census.
- Verify the retest's unfiled "COUNTER expected": the peace offer to Britain at 750 gold a turn plus an action a turn, turns 23–24. File it if it is a defect.
- Close the design rows §6-12 disposes.
- **Done when:** `defect_census.py --open` lists exactly §1's 99 live rows, plus anything filed since, each with an owner in this spec.

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

### Step 1 — "The peace holds" (≈1.5; the latch half needs RS-D1 ruled)

| Row | Sev | Fix shape |
|---|---|---|
| RS-1 | P1 | The offensive cascade keeps a fresh peace. A court with a fresh peace or a pair cooldown is not called (`hard_illegal`, "fresh peace with X", no penalty), and the settlement writes the pair cooldown. Lever `THE_CASCADE_KEEPS_A_FRESH_PEACE`, series attributed. Also closes PC15-15's recorded residual (`settlement_third_party.py`). |
| RS-2 | P1 | While the Congress sits, a war France neither declared nor joined marks a refusing ceder's titles CONTESTED but still counted. The break applies when that war ends, and the sue peace re-titles and latches recognition. Lever `A_CONGRESS_WAR_CONTESTS_NOT_BREAKS`. With RS-D1, if ruled yes: a signed peace that leaves a great power's capital in the French bloc latches its recognition. |
| RS-10 | P2 | Before the summons, the Congress says that the gate drops to 40 and which courts go to war (it reads the brewing league). |
| RS-16 | P3 | The alarm line is built from one forecast of the tick's gains and its decay. |
| SF-V1 | P2 | The AI proposal producer skips a treaty whose relation floor the pair does not meet (the ratifier's own predicate), and the refusal names the treaty. |
| **Exit: SF-END-1 "The Imperial Peace, played" (0.4)** | — | Replay `docs/audits/playtest_digests/rs0928-hand-played/retest_t24_summonable.json` by hand through the fixed sitting, to a peace or an honest dissolution. Archive it as the ending's evidence. |

### Step 2 — Berthier tells the truth (≈4.0; display and copy, no series moves)

- **SR-6a "The dispatch pass", rebuilt (≈1.2):**
  - AAR-5, AAR4-X2, AAR24-X4, CRT-4-X1.
  - RS-9 with RS-19, as one coverage-label fix.
  - RS-17 (the headline half).
  - RS-20, plus a neutral fallback for the PL-14 net, which closes that family (IQ7-X4, SR-2-X3).
  - RS-23.
  - RS-D2: the levy yields the headline after three unanswered statements.
  - NPC-14, NPC-15, NPC-27, IQ6-D3, SRX-5.
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

### Step 3 — Europe acts without France (≈6.5; gate SR-G7 at its head)

Order: RS-3 → SR-7a → SR-7b → SR-G7 (built as ruled) → SR-7c → RS-27 → SF-LB-1 → SR-7d. SR-7d goes last so the doctrines do not confound the long-peace measurement.

- **RS-3** (its shape is ruled in §6): a field win halts before a garrison that still fights, or the garrison fights beside the corps. Flip arm.
- **SR-7a "The AI's odds gate and its dithering"** (AAR-D8), taking with it:
  - CQ-22: one stance rule for drill on every road; the direction is §6's.
  - IQ5-R1: the casualty pool splits by committed bodies.
  - XR-3's remaining half: no march attrition on an in-place capture.

  One series re-record, flip-attributed per lever.
- **SR-7b "The long peace, measured"** (PB-D1): the baseline arms first.
- **SR-G7**, built as ruled. Recommended: Europe stays at Brewing while France holds ≥ 40% of the map. PB-D1's completion clause is its acceptance test.
- **SR-7c "Dispersion"** (AAR-D4).
- **RS-27** (measure first): bisect what moved the volte-face, then either pin it firing on its arm or re-script the arm.
- **SF-LB-1 "Europe's own quarrels" (≈1.0):** deck authoring — IQ6-D1's Austrian follow-on, and `gulf_and_straits` waking without a volte-face. Measured to open at least one ambient AI-vs-AI war in 40 turns on ≥ 3 of 7 seeds.
- **SR-7d "The Doctrines"** (DC-0 … DC-3c, ≈2.5): `DOCTRINES_SPEC.md` §7.

### Step 4 — the three misses, second pass (≈5.3)

- **SF-CL-1 "The forecast keeps its word" (≈0.8, after Step 3).**
  - Across the benchmark arms, log every prediction beside what the resolver committed: the odds band, "WILL JOIN", the what-if, the scout line, the objection's figure.
  - Fix each class of divergence, and pin the census.
- **SF-CMD-1 "The unrehearsed line" (≈1.5).**
  - A held-out census of about 300 lines, written without seeing the corpus, run keyless and keyed.
  - Resolution-aware confidence: a parse whose target matches nothing on the board never executes at 0.9. "march in support of Ney" charged a march to "In Support Of Ney".
  - Its census sizes Chunk 3b.
- **Chunk 3b, trimmed to what SF-CMD-1 confirms (≈3.0):**
  - **CRT-6 "the retreat is a word":** CQ-33, CX5-L5-F3, F4, F5, F6, F7, N2, N4, N5.
  - **CRT-8 "the Cabinet's rules on every road":** RS-7, CQ-36, CX-X3 (§6 rules the last).
  - **CRT-9 "the state speaks first", as ONE state probe:** RS-4, RS-12, RS-15, CQ-21, CQ-24, CQ-28. `march_state_refusal` gains drill-lock and fortified arms, and those orders are refused free at issuance.
  - **CRT-10 "the suggestion is honest":** CX3-X2, CX3-X3, CX-BEHAV-1, PC15-13; NPC-6 (the tombstone answer); SF-V4 (per §6).
  - **CRT-11 "the second name is heard":** CQ-8, CQ-38.
  - **The parser riders (no CRT row named them):** RS-6, RS-8, RS-11, NP-X1, NP-X8, NP-X9, NP-X10, NPC-9, NPC-10, NPC-18, NPC-26.

### Step 5 — the client stands (≈2.0)

- **SR-8a VD-C "The Contingent"** (IQ7-D1), with:
  - IQ7-X1: courting and cascades walk every lord (GR5);
  - IQ7-X3: the recovery hint fires on a crossing, not on every tick;
  - IQ7-X2: dead code deleted.
- **SR-8b + SF-AGD-1 "The agendas arm":**
  - a carve through the settlement path to a Proclamation, on a played road;
  - SF-M's TILSIT probe as its instrument;
  - the formables gate flipping in play.
- **SR-8c:** IQ7-D3 (a satellite design province France can grant), and IQ6-D1's deck review.
- **VP-D9:** build the player's bribe verb, or strike it (§6).

### Step 6 — the chest and the sea (≈0.7, +1.0 if needed)

- **SF-NAV-1 "The strangulation, played":**
  - One arm that closes 13 of 26 ports, drives out the corps `continent_holders` names, holds SHUT OUT through a sitting, and records why Britain sues.
  - If Continental System tier 2 stays unreachable, the A2 anchor goes to the user.
- **SF-ECON-1 "Acts of the Empire", only if the economy's items are still short after Step 3:**
  - two or three late acts per deck, priced for the turn 15–30 chest;
  - they turn gold into endgame progress, not income;
  - its own gate comes first (§6).

### Step 7 — what the wire says, the screen says (≈2.0 + the user's eyes)

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
- **Frames:** the IQ-10 frames re-shot at both Interface Scales for every surface Steps 1–6 touched, plus one 5-turn Mode C session.

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

**Agendas.** Scripts reach a carve only from the losing side. The Normandy mirror carve on seed `ulm` raised `nation_proclamation` on `rf3-cmd-on-ulm` at turn 30. `tools/_score_formables_probe.py` does three things:
- reads `GET /formables` at each snapshot, recording gate flips;
- **TILSIT:** stages the IGR-D fixture (France six turns at war with Prussia, holding Posen), then drives the Warsaw `create_client` separate peace through `/respond_to_diplomatic_dialogue`, without patching acceptance (measured 58 against 50). Pass means `nation_proclamation` fires and `DuchyOfWarsaw` stands;
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

Recommended defaults are the plan's; every one is the user's to confirm or change.

| # | Question | Recommended default | Needed by |
|---|---|---|---|
| 1 | **RS-D1:** does a signed peace that leaves a great power's capital in the French bloc latch its recognition? | **Yes**, and the Congress table prices each lever in turns. The alternative is a 12–16-turn sitting. | Step 1 (the latch half) |
| 2 | **The checklist, v1** (Appendix A), and "the items are the done-when" | Confirm v1. Define done as 56 of 84 ceilings with every floor green, which means every pillar at target. | Step 0, before the baseline freezes |
| 3 | **SR-G7 / PB-D1:** a standing alarm floor, so the long peace ends by machinery; which slot rules it | Europe stays at Brewing while France holds ≥ 40% of the map. Ruled at Chunk 7's head (Step 3), with SR-7b measuring first. ROADMAP 12 stops owning PB-D1. | Step 3 |
| 4 | **RS-3's shape** | A field win halts before a garrison that still fights (the march's own predicate). | Step 3 |
| 5 | **CQ-22:** the stance rule for drill on every road | The player's rule for both boards: no drill in aggressive stance. One series re-record. | Step 3 |
| 6 | **SF-V4:** an attack on a proper name the map does not know | **Ask**, as the address rule does: "No foe called Zorglub is known — the nearest is Mack at Swabia. Attack him?" A descriptive phrase keeps CX5-L5-F8's substitution. | Step 4 |
| 7 | **CX-X3:** the typed `vassalize` of a beaten minor | Route it through the Cabinet's priced proposal (acceptance plus DP). GEV-1's three proofs stay the rule for great powers. | Step 4 |
| 8 | **CQ-36:** the break row for a boot alliance | Keep the dim, and make its reason honest: "an alliance of 1805, not a treaty of ours". | Step 4 |
| 9 | **VP-D9:** the player's defection-bribe verb | Strike it. The AI's on-ramp stays; VD-C is the vassals' lift. | Step 5 |
| 10 | **IQ7-D4:** is the unattended petition calendar a variance target? | No; amend `AI_INTENT_SPEC.md` §3.8. | Step 5 |
| 11 | **SF-ECON-1:** a late gold sink ("Acts of the Empire") | Only if the economy's items still fall short after Step 3, and then through its own gate. | Step 6 |
| 12 | **The orphaned design gates** | Dispositions below this table. | SF-0, to close the rows |
| 13 | **Confirmations already owed** (not blocking) | FA-D29 / FA-S17-1, FA-D4, FA-S2-D1, FA-D23, and the FA-D27 re-open; the RF-4 laws frames | Step 7's sign-offs |

**Row 12, the orphaned design gates:**
- **WO-D7:** strike, on SR-5a's "keep the rules, make it legible".
- **WO-D8:** "price, not time". The declaration names the betrayal and the alarm it costs.
- **WO-D13:** record the rung-1 precedence as deliberate.
- **EWC-D3:** strike. W6-7's clause covers the release; a ransom is post-EA content.
- **VP-D8:** decline.
- **IQ6-D2:** no default. Rule it at Step 3's gate, after measuring.

---

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

## Appendix A — the checklist, version 1 (DRAFT, FOR USER CONFIRMATION)

**Legend:**
- **F** = floor, **C** = ceiling.
- **Kind:** A = AUTO, P = PROBE, E = EYES.
- **Today:** ✓ / ✗ where it was measured on the `rs0928-*` archives at `c20d5bba`; blank = not yet measured (the baseline reads it).
- Arms refer to §4.2; **T** = titled provinces (`tools/sr1e_titled_probe.py`).

**The ending (target 7.0 = 3 ceilings)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | Pressburg reaches THE IMPERIAL PEACE by turn 36 | A | ✓ |
| F2 | The Verdict arm reaches its turn-44 register | A | |
| C1 | The Congress on CONG survives its sitting unless France declares war (RS-2) | A | ✗ |
| C2 | The CONG summons names the league gate it lowers (RS-10) | A | ✗ |
| C3 | The CONG alarm forecast matches the next tick ±1 (RS-16) | P | ✗ |
| C4 | T ≥ 40 at turn 40 on 2 of 3 CMD seeds | A | ✗ (36/34/36) |
| C5 | Some benchmark road reaches T ≥ 45 by turn 40 | A | ✗ |
| C6 | On CONG, each refuser's price can be paid within the sitting, or the table says it cannot (RS-D1) | P | ✗ |

**Diplomacy (7.0 = 3)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | The propose arm ratifies a peace on every seed | A | |
| F2 | The advisor arm ticks at least 2 mission types | A | |
| C1 | No French peace is broken within 5 turns by another court's cascade (RS-1) | P | ✗ |
| C2 | A ratification label names only the covered courts (RS-9) | P | ✗ |
| C3 | VOLTE fires `volte_face` (RS-27) | A | ✗ |
| C4 | DL's eight Cabinet phrasings each start a mission or give a priced refusal (RS-7) | A | ✗ |
| C5 | DL's "request terms from Austria" is answered by Austria (PC15-6) | A | |
| C6 | No treaty France accepts from an AI offer fails its own ratification (SF-V1) | A | ✗ (14 on 5 arms) |

**First contact (7.5 = 4)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | FC has 0 shrugs and 0 refusals | A | ✓ |
| F2 | SCH reaches card XIX | A | ✓ |
| C1 | At most 2 of HOLD's 20 questions shrug | P | |
| C2 | No HOLD answer contradicts the save | E | |
| C3 | DL's "where are the Russians" and "why is Europe alarmed" are answered (RS-14) | A | ✗ |
| C4 | DL's "what can I do" at 0 military actions names a legal order (RS-15) | A | ✗ |
| C5 | Every TODAY order in the boot briefing executes | P | |
| C6 | OP's first loop has 0 reading refusals | A | |

**Economy (7.0 = 3).** The size of the treasury is ruled intended (SRX-D1) and is not read.

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | `net_residual` is 0 on every record | A | ✓ (0 of 457) |
| F2 | Britain's turn-1 Net exceeds France's (SR-5a) | P | ✓ |
| C1 | On LAW, the Staff is enacted by loop 9 | A | ✗ (SF-V3) |
| C2 | Every Net-line move of 10% or more names its cause | P | |
| C3 | The quoted Charges and Laws equal what the next turn applies | P | |
| C4 | Every priced order charges what it quoted | P | |
| C5 | DL's levy at 0 military actions executes (AAR-6) | A | ✓ |
| C6 | On CMD turns 20–40, "what can I do" names an affordable purchase on ≥ 80% of turns (RS-D3) | P | |

**Naval (7.0 = 3)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | The naval-gate tests are green | A | ✓ |
| F2 | SEA has no blocker and no `SCRIPT PRECONDITION` | A | ✓ |
| C1 | SEA quotes the second diversion at readiness −25, and both throws print | A | ✓ |
| C2 | A fleet action leads the next dispatch | A | ✓ |
| C3 | The descent quote names the odds and a lever, and Munster falls | A | |
| C4 | On the shut-out arm, Britain sues by turn 10 on 3 of 3 seeds | A | |
| C5 | The ports lever explains "(now 0)" during a truce (RS-25) | P | ✗ |
| C6 | The Admiralty and fleet frames pass | E | |

**Living balance (7.0 = 3).** The unattended France's collapse is ruled intended and is not read.

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | On CMD, France holds ≥ 20 provinces at turn 40 on 3 of 3 seeds | A | ✓ (30/29/27) |
| F2 | `BASELINE_SERIES` and M1–M7 are green | A | ✓ |
| C1 | AIV-C shows at least one war between two AI courts | A | ✗ |
| C2 | AIV-C shows at least one standalone third-party settlement | A | ✗ |
| C3 | AIV-C shows exhaustion-driven pair peaces on every seed | A | |
| C4 | On CMD, after the general peace, a court declares war on France beyond the fresh-peace floor and not by cascade (PB-D1) | A | ✗ |
| C5 | On CMD, threat rises at least once after that peace | A | ✗ |
| C6 | On every AIV-C seed, an AI court takes a province from another AI court | A | |

**Combat legibility (7.5 = 4)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | Every player battle is logged with both sides' losses | A | |
| F2 | OP's turn-4 scout of Vienna names the garrison | A | ✓ |
| C1 | Every attack that fought printed its muster first, including through an objection (RS-13) | A | ✗ |
| C2 | The bands are monotone: "favorable" attacks out-bleed the enemy ≥ 70% of the time, and more often than "even" | A | ✓ (24/24 vs 9/12) |
| C3 | An occupied capital's garrison fights, or is named (RS-3) | P | ✗ |
| C4 | DL's what-if for a fortified marshal refuses as the order would (RS-12) | A | ✗ |
| C5 | No raw marshal keys in combat text (RS-26) | A | ✗ |
| C6 | The diorama frames pass at both scales | E | |

**Marshal drama (7.5 = 4)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | On the flagship arm, `_pc15_10_acceptance_probe.py` shows ≤ 4 petition modals and 0 silent losses | P | ✓ |
| F2 | On OP, a grievance fires, is heard and resolves | A | |
| C1 | OP shows ≤ 3 petition modals and ≥ 3 audiences | A | ✓ (3 and 10) |
| C2 | A Trust answer names only a man we can see and reach, and a refused Trust keeps the order (RS-5) | P | ✗ |
| C3 | No marshal repeats a victory line within his last three wins (RS-24) | P | ✗ |
| C4 | The crown moves only on ≥ 3 glory, and the line names where it went | A | |
| C5 | An unmet expectation is announced before trust erodes | P | |
| C6 | Five sampled petitions each read in the marshal's own voice | E | |

**Vassals (7.5 = 4)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | On CMD, ≥ 2 of 3 satellites remain at turn 40 on 3 of 3 seeds | A | ✓ |
| F2 | CMD-H with `--client-petition refuse` loses a satellite by turn 30 | A | |
| C1 | CMD shows ≥ 4 priced petitions | A | ✓ (6/4/8) |
| C2 | A petition's applied effect equals its quote | P | |
| C3 | No French peace leaves a client state at war (SR-1b) | P | |
| C4 | Loyalty under 40 draws a line naming the remedy | A | |
| C5 | An attacked client capital is contested within 2 turns (VD-C) | P | ✗ |
| C6 | The VASSALS tab frame passes | E | |

**UI/UX (7.5 = 4)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | CLI: 0 `SCRIPT ERROR`, 0 blank frames, every shot ok | A | |
| F2 | The parse harness exits 0 and the boot smoke test is clean | A | ✓ |
| C1 | No frame has `buttons_offscreen` | A | |
| C2 | No frame has `clipped_text` | A | |
| C3 | No frame's text shows a raw key, `<null>` or `(s)` | A | |
| C4 | On OP, no end turn raises more than 3 blocking popups | A | ✗ (max 5) |
| C5 | The user signs off ≥ 9 of 10 named frames | E | |
| C6 | In a 5-turn Mode C session, nothing is blocked and every hotkey works | E | |

**Command & parsing (8.0 = 5)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | The golden corpus passes 100% | A | ✓ |
| F2 | The keyless replay passes 100% | A | ✓ |
| C1 | OP: ≤ 1 shrug in 127 lines | A | ✓ |
| C2 | OP: 0 reading refusals (of the "Cannot find marshal 'Of Ney'" kind, which the hand-played retest met on turn 1) | A | |
| C3 | ≥ 18 of HOLD's 20 orders execute as meant | P | |
| C4 | DL's "in support of", "march on X and destroy Y" and "take" execute (RS-6/8/11) | A | ✗ |
| C5 | On `typed_road.json`, question turns spend 0 actions and order turns spend them | A | |
| C6 | OP on the live parser has ≤ 1 misread | A | |

**Narration (8.0 = 5)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | Every turn has a headline, and none shows a raw key | A | |
| F2 | A dispatch carries ≤ 2 routine intent lines plus a tail | A | |
| C1 | No headline class leads more than 4 of any 10 turns (RS-D2) | A | ✗ (7 on CMD-H) |
| C2 | No rail row repeats more than 3 times a turn, and every war entry names its enemy (RS-23) | A | ✗ |
| C3 | The near-miss and summonable headlines fire (RS-17) | P | ✗ |
| C4 | The dispatch's intel row matches the intel store (AAR-5) | P | ✗ |
| C5 | Le Moniteur keeps its cadence and its special editions | A | |
| C6 | Ten sampled dispatches each lead with the turn's biggest event | E | |

**AI aliveness (8.0 = 5)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | `test_ai_intent_assurance.py` is green | A | ✓ |
| F2 | No arm has a blocker or a traceback | A | ✓ |
| C1 | The rival courts enact 13–18 laws with 0 lapses | A | ✓ |
| C2 | Every 40-turn arm has ≥ 1 design promotion | A | ✓ |
| C3 | Britain lands on the continent on every CMD arm | A | ✓ |
| C4 | No AI assaults a garrison under 500 men three times running (AAR-D8) | P | |
| C5 | No AI corps fortifies, unfortifies and fortifies again within 3 turns | P | |
| C6 | On CMD, visible AI attacks occur on ≥ 50% of the turns at war | A | |

**Agendas & formables (8.5 = 6)**

| # | Item | Kind | Today |
|---|---|---|---|
| F1 | The agenda and formables tests are green | A | ✓ |
| F2 | `/formables` on every CMD save lists each template with its gate terms | P | |
| C1 | Every 40-turn arm has ≥ 2 `agenda_shift` events | A | ✓ |
| C2 | On AIV-B, a variance seed opens with a different design (D7) | A | |
| C3 | A gate term flips to met during play | P | |
| C4 | The TILSIT probe raises `nation_proclamation` | P | |
| C5 | On CMD-ulm, the Normandy carve states its terms and the card fires | A | |
| C6 | The Proclamation and formables frames pass | E | |
