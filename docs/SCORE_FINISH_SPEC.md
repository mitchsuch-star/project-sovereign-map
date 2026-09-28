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
| **The ending** | 6.75 | 7.0 (3 ceilings) | RS-2 (P1), RS-D1, RS-10, RS-16 | Step 1, "The peace holds", with RS-D1 as ruled (the capital latch, §6.1) and SF-END-1 as its exit (the sitting played to its end from the turn-24 save) | The price rider makes the decisive-campaign peace unreachable (then the latch ships alone), or "contested but counted" softens the finish too far |
| **Diplomacy** | 6.75 | 7.0 (3) | RS-1 (P1), SF-V1, RS-7, RS-9, RS-18 … RS-22, CQ-36, CX-X3, NPC-21 | Step 1 (RS-1, SF-V1); Step 2 (SF-DIP-1 "the dial survives the drop"; SR-6b copy); Step 4 (CRT-8) | RS-1's fix changes alliance calls (one series re-record) |
| **First contact** | 7.0 | 7.5 (4) | RS-12, RS-14, RS-15, SRX-5, RS-6, RS-7, CX3-X2, CX3-X3, CX-BEHAV-1 | Step 2 (RS-14, SRX-5); Step 4 (CRT-9 with RS-12/RS-15; SF-CMD-1's first hour); Step 7 (the first ten minutes in the client) | The sourced lines are saturated, so a scorer's own phrasing decides (the HOLD arm, §4.2) |
| **Economy** | 6.75 | 7.0 (3) | RS-D3 (evidence for SR-G7) | Step 3 (SR-G7 gives the chest a war to fund); Step 6 (SF-ECON-1, only if the items still fall short) | A new sink re-opens SR-5a's balance |
| **Naval** | 6.75 | 7.0 (3) | RS-25; SHUT OUT has never held on a played board | Step 6 (SF-NAV-1 "the strangulation, played") | Britain sues from its own war exhaustion before the System bites (6 of 6 arms) |
| **Living balance** | 6.5 | 7.0 (3) | SR-G7 / PB-D1 (the long peace); 0 AI-vs-AI wars; RS-3, RS-27, CQ-22, IQ5-R1, XR-3 | Step 3: SR-G7 "The Armed Peace" as ruled (§6.2) → SF-LB-1 "Europe's own quarrels" | The league the fuse brings breaks F1 (France below 20 provinces at turn 40): lengthen the fuse, never lower the watch. A shorter fuse would re-open IQ-3's revolving door |
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
| **1** | "The peace holds": RS-1, RS-2, RS-D1 as ruled (the capital latch + the price rider), RS-10, RS-16, SF-V1; SF-END-1 as the exit | ≈1.8 | the ending, diplomacy |
| **2** | Berthier tells the truth: Chunk 6 rebuilt, plus the reserve, SF-MD-1 and SF-DIP-1 | ≈4.0 | narration, drama, combat legibility, diplomacy, first contact |
| **3** | Europe acts without France: Chunk 7 as one balance block, SR-7d last | ≈6.5 | living balance, AI aliveness, economy |
| **4** | The three misses, second pass: SF-CL-1, SF-CMD-1, then Chunk 3b trimmed to what the census confirms | ≈5.3 | combat legibility, command, first contact |
| **5** | The client stands: Chunk 8 + SF-AGD-1 | ≈2.0 | vassals, agendas |
| **6** | The chest and the sea: SF-NAV-1 (+ SF-ECON-1 only if needed) | ≈0.7 (+1.0) | naval, economy |
| **7** | What the wire says, the screen says: Chunk 9 + the user's eyes | ≈2.0 | UI/UX (+ first contact, drama) |
| **8** | SF-R, the final reading | ≈1.0 | all |
| | **Total** | **≈25–26** | |

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

### Step 1 — "The peace holds" (≈1.8; RS-D1 is ruled — §6.1)

| Row | Sev | Fix shape |
|---|---|---|
| RS-1 | P1 | The offensive cascade keeps a fresh peace. A court with a fresh peace or a pair cooldown is not called (`hard_illegal`, "fresh peace with X", no penalty), and the settlement writes the pair cooldown. Lever `THE_CASCADE_KEEPS_A_FRESH_PEACE`, series attributed. Also closes PC15-15's recorded residual (`settlement_third_party.py`). |
| RS-2 | P1 | While the Congress sits, a war France neither declared nor joined marks a refusing ceder's titles CONTESTED but still counted. The break applies when that war ends, and the sue peace re-titles and latches recognition. Lever `A_CONGRESS_WAR_CONTESTS_NOT_BREAKS`. |
| RS-D1 | ruled | §6.1: a signed peace that leaves a great power's capital held by France or her vassal chain latches its recognition (`kind: "capital"`; it breaks when the capital leaves the bloc). The price rider makes the scorer read a retained capital as lost; the latch and the rider each sit behind their own lever, and the rider is measured on the turn-16 shape. Every courtship lever quotes its cost in turns. With it, the RS-1 rider: the cascade reads `spared_from_coalition` while the Congress sits. |
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
- **SR-G7 "The Armed Peace"**, as ruled (§6.2): the watch at 45 while the hegemon leads ≥ 1/3 of Europe's power, then the 16-quiet-turn fuse at +3 a turn up to the brewing gate. PB-D1's completion clause is its acceptance test (3 of 3 commanded seeds; projected league turns 32 / 29 / 31). SR-7b's baseline arms were already measured by the ruling's research.
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
  - **CRT-10 "the suggestion is honest":** led by **SF-V4**, "a proper name asks", as ruled (§6.3, lever `A_PROPER_NAME_ASKS`). Then CX3-X2, CX3-X3, CX-BEHAV-1, PC15-13, and NPC-6 (the tombstone answer, folded into SF-V4's fallen-general case).
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

Recommended defaults are the plan's; every one is the user's to confirm or change. **Rows 1, 3 and 6 were RULED on September 28, 2026 under the user's delegation** (*"make decisions on …"*). Each was researched first; the gate records are §6.1–§6.3, and they are authoritative.

| # | Question | Recommended default | Needed by |
|---|---|---|---|
| 1 | **RS-D1:** does a signed peace that leaves a great power's capital in the French bloc latch its recognition? | ✅ **RULED Sept 28, 2026: YES, anchored to the capital, with a price rider** (§6.1). | Step 1 |
| 2 | **The checklist, v1** (Appendix A), and "the items are the done-when" | Confirm v1. Define done as 56 of 84 ceilings with every floor green, which means every pillar at target. | Step 0, before the baseline freezes |
| 3 | **SR-G7 / PB-D1:** a standing alarm floor, so the long peace ends by machinery; which slot rules it | ✅ **RULED Sept 28, 2026: "THE ARMED PEACE"** — a watch line at 45 while France leads a third of Europe's power, then a visible 16-quiet-turn fuse up to the brewing gate (§6.2). The drafted "≥ 40% of the map" was **rejected on measurement**. Built at Step 3; ROADMAP 12 no longer owns PB-D1. | Step 3 |
| 4 | **RS-3's shape** | A field win halts before a garrison that still fights (the march's own predicate). | Step 3 |
| 5 | **CQ-22:** the stance rule for drill on every road | The player's rule for both boards: no drill in aggressive stance. One series re-record. | Step 3 |
| 6 | **SF-V4:** an attack on a proper name the map does not know | ✅ **RULED Sept 28, 2026: the marshal ASKS, for free, naming only foes in sight**; a descriptive phrase keeps today's disclosed substitution (§6.3). | Step 4 (it leads CRT-10) |
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
| C4 | DL's "in support of", "march on X and destroy Y" and "take" execute (RS-6/8/11), and "attack Zorglub" / "attack Alsace" ask without spending anything (SF-V4, §6.3) | A | ✗ |
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
