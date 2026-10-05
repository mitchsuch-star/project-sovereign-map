# SF-R — the final reading (October 5, 2026)

**The Score Finish's second full reading**, taken on the same instrument and checklist v1 as the baseline (`docs/audits/SCORE_BASELINE_2026_09_29.md`, tree `c20d5bba`), per `docs/SCORE_FINISH_SPEC.md` §3 Step 8. The archive is `docs/audits/score_runs/2026_10_05_sfr/`. The rows the reading filed are `docs/BUG_FIXES.md` §Score Finish Step 8 and `docs/DESIGN_REFINEMENT.md` §Score Finish Step 8. The depth campaign's report is `docs/audits/SFR_DEPTH_CAMPAIGN_2026_10_05.md`.

## In one paragraph

**Directional 6.71 → 7.50 over 13 of 14 pillars.** The two readings exercise different thirteen pillars:
- UI/UX is newly exercised, because the client arm ran.
- Marshal drama is no longer exercised: five of its eight items measured, and its first floor is red.

Over the twelve pillars both readings exercise, the move is **6.69 → 7.50**.

- **Ceilings passed rose from 40 to 58 of 84.** The rule asks 56, with every floor green.
- **Nine pillars moved up past the panel's spread**, and **eight are at their target item count**.
- **Two moved down:**
  - **Command** is capped at 6.00 by one P1 the reading found and verified at the wire: SFR-D11, "march home to Franche-Comte" marches to Lorraine. Its items rose from 3 to 5 ceilings, and the uncapped reading would be 8.00.
  - **AI aliveness** fell from 6 ceilings to 3. One of its three falls is the user's open question (§6 row 18). One is a new design row for the user (SFR-DR1: the league declares and rarely strikes). The third is a filed defect (SFR-B14: a rival court lets its laws lapse in a long war).
- **The done-when (§7) is not met:**
  - six pillars are short of target;
  - 77 defect rows are open, all owned;
  - §6 rows 18 and 22 still wait on the user.
- **The reading stands as the frozen instrument read it.** Three readers were found stale or wrong during the reading. They are filed as SFR-I4, I5 and I7, and their corrected marks are shown in §3 but not claimed. One of them (SFR-I7) would bring combat legibility to its target on this reading.

## 1. How it was read

**The instrument:** `tools/score_run.py` (run, check, packet, compare) and checklist v1 (`docs/SCORE_CHECKLIST_V1.json`), unchanged since the baseline.

**Arms.** 41 arms ran on `0f5e8d84`, the tree of Step 7b's frames:
- the driver arms (808 turns between them);
- the AI-V sweep (seven seeds);
- the agenda evaluation;
- the suite arm;
- the client arm: Godot in a window parked off-screen, 131 surfaces × Interface Scales 1.0 and 2.0 = 262 frames, 0 SCRIPT ERROR, parse harness and boot smoke exit 0.

**What the step added to the instrument** (pins `tests/test_score_finish_step8.py`):
- **The `OP-LIVE` arm:** the opening on the live parser, with the user's key. It reads command C6, live against offline on the same lines. 1 of its 145 lines reached the model, with 0 misreads.
- **The UI/UX readers** over the client arm's machine record.
- **The fresh HOLD script.**
- **The suite arm's encoding fix (SFR-I1).** Every session exit since the baseline had skipped that arm, so the defect had not been seen.

**The blind panel.** Three agents with fresh contexts read only `panel_packet/`.
- **EYES marks:** each marked the EYES items, and two of three agreeing makes the mark. **The marks are provisional; the user's own marks override them**, by the user's choice for this reading. Six items were marked:
  - agendas C6 ✗;
  - combat legibility C6 ✓;
  - first contact C2 ✗;
  - narration C6 ✗;
  - naval C6 ✗;
  - vassals C6 ✓.
- **Not judged:** three items no scorer could judge (marshal drama C6, UI/UX C5 and C6).
- **Scores:** per pillar, each scorer gave the anchor plus an adjustment of −0.25, 0 or +0.25. The median and the spread are published (`panel.json`, assembled by `tools/score_panel.py`).

**HOLD, written fresh and blind** (`tools/playtest_scripts/score_hold_2026_10_05.json`: twenty questions, twenty orders), was read on both trees in the same session. The second tree is `c20d5bba`, on a detached worktree.

**One hand-played depth campaign.** Twenty-six turns of France/1805 were played through the driver in chunks of 2–3 turns, each continuing from the last save:
- turns 1–16 on the live parser;
- turns 17–26 keyless.

A separate agent played it, and its 44 findings are recorded verbatim. It feeds the findings rate, not the score.

## 2. The reading

| Pillar | Baseline (`c20d5bba`) | Final (`0f5e8d84`) | Ceilings | Floors | Target | Panel median (spread), baseline → final | At target? |
|---|---|---|---|---|---|---|---|
| The ending | 5.00 | 7.50 | 0 → 4 | 2/2 → 2/2 | 3 | 5.0 (0.25) → 7.5 (0.0) | ✓ |
| Diplomacy | 5.75 | 8.50 | 3 → 6 | 2/2 → 2/2 | 3 | 5.75 (0.25) → 8.25 (0.25) | ✓ |
| First contact | 7.00–7.50 | 8.00 | 3 → 5 | 2/2 → 2/2 | 4 | 7.0 (0.0) → 7.75 (0.25) | ✓ |
| Economy | 7.00 | 7.00 | 3 → 3 | 2/2 → 2/2 | 3 | 7.0 (0.0) → 7.0 (0.25) | ✓ |
| Naval | 7.00–8.00 | 7.50–8.00 | 3 → 4 | 2/2 → 2/2 | 3 | 7.25 (0.25) → 7.75 (0.25) | ✓ |
| Living balance | 6.50 | 8.50 | 2 → 6 | 2/2 → 2/2 | 3 | 6.25 (0.0) → 8.5 (0.0) | ✓ |
| Combat legibility | 5.50–5.75 | 7.00–7.50 | 2 → 3 | 1/2 → 2/2 | 4 | 5.75 (0.25) → 7.0 (0.25) | ✗ 3 of 4 |
| Marshal drama | 7.00–8.00 | NOT EXERCISED | 3 → 2 | 2/2 → 1/2 | 4 | 7.0 (0.25) → — | ✗ not exercised; floor red |
| Vassals | 7.00–7.50 | 7.50–8.00 | 3 → 4 | 2/2 → 2/2 | 4 | 7.0 (0.25) → 7.5 (0.0) | ✓ |
| UI/UX | NOT EXERCISED | 7.50–8.50 | 0 → 4 | 0/2 → 2/2 | 4 | — → 7.25 (0.0) | ✓ |
| Command & parsing | 7.00–7.50 | **6.00** (items: 8.00) | 3 → 5 | 2/2 → 2/2 | 5 | 7.0 (0.25) → 6.0 (0.25) | ✗ P1 SFR-D11 |
| Narration | 7.00–8.00 | 7.50–8.00 | 3 → 4 | 2/2 → 2/2 | 5 | 6.75 (0.0) → 7.25 (0.25) | ✗ 4 of 5 |
| AI aliveness | 8.50 | 7.00 | 6 → 3 | 2/2 → 2/2 | 5 | 8.5 (0.0) → 7.0 (0.0) | ✗ 3 of 5 |
| Agendas & formables | 7.00–8.00 | 8.00 | 3 → 5 | 2/2 → 2/2 | 6 | 7.0 (0.25) → 8.0 (0.0) | ✗ 5 of 6 |

**The directional (§4.4: the mean of each exercised pillar's low end):**

| Reading | Baseline | Final |
|---|---|---|
| As the rule reads it, over 13 of 14 | 6.71 | **7.50** |
| Like for like: the 12 pillars exercised in both | 6.69 | 7.50 |
| All 14, marshal drama at the "otherwise" branch it would read if exercised (5.50 with C5 failing, 5.75 with C5 passing) | — | 7.36–7.38 |

**The claims (§4.5)** — a move is claimed only when an item flipped AND the median moved by more than the larger spread:
- **MOVED up:** the ending, diplomacy, first contact, naval, living balance, combat legibility, vassals, narration, agendas.
- **MOVED down:** command (the cap), AI aliveness.
- **Held:** economy.
- **Not comparable:** marshal drama and UI/UX, each exercised in one reading only.

## 3. Every item flip since the baseline, with its cause

Item by item, baseline → final (✓ pass · ✗ fail · `·` unmeasured; ⟵ marks a flip):

- **The ending:** F1 ✓→✓ · F2 ✓→✓ · C1 ✗→✓ ⟵ · C2 ✗→✓ ⟵ · C3 ✗→✓ ⟵ · C4 ✗→✗ · C5 ✗→✗ · C6 ✗→✓ ⟵
- **Diplomacy:** F1 ✓→✓ · F2 ✓→✓ · C1 ✓→✓ · C2 ✓→✓ · C3 ✗→✓ ⟵ · C4 ✗→✓ ⟵ · C5 ✓→✓ · C6 ✗→✓ ⟵
- **First contact:** F1 ✓→✓ · F2 ✓→✓ · C1 ✗→✓ ⟵ · C2 ·→✗ ⟵ · C3 ✗→✓ ⟵ · C4 ✓→✓ · C5 ✓→✓ · C6 ✓→✓
- **Economy:** F1 ✓→✓ · F2 ✓→✓ · C1 ✓→✗ ⟵ · C2 ✗→✗ · C3 ✗→✓ ⟵ · C4 ✓→✓ · C5 ✗→✗ · C6 ✓→✓
- **Naval:** F1 ✓→✓ · F2 ✓→✓ · C1 ✓→✓ · C2 ✓→✓ · C3 ✗→✓ ⟵ · C4 ✓→✓ · C5 ·→· · C6 ·→✗ ⟵
- **Living balance:** F1 ✓→✓ · F2 ✓→✓ · C1 ✗→✓ ⟵ · C2 ✗→✓ ⟵ · C3 ✓→✓ · C4 ✗→✓ ⟵ · C5 ✗→✓ ⟵ · C6 ✓→✓
- **Combat legibility:** F1 ✗→✓ ⟵ · F2 ✓→✓ · C1 ✓→✓ · C2 ✓→✓ · C3 ✗→· ⟵ · C4 ✗→✗ · C5 ✗→✗ · C6 ·→✓ ⟵
- **Marshal drama:** F1 ✓→✗ ⟵ · F2 ✓→✓ · C1 ✓→✗ ⟵ · C2 ✓→✓ · C3 ✗→✓ ⟵ · C4 ·→· · C5 ✓→· ⟵ · C6 ·→·
- **Vassals:** F1 ✓→✓ · F2 ✓→✓ · C1 ✓→✓ · C2 ✓→✓ · C3 ✓→✓ · C4 ✗→✗ · C5 ✗→· ⟵ · C6 ·→✓ ⟵
- **UI/UX:** F1 ·→✓ ⟵ · F2 ·→✓ ⟵ · C1 ·→✓ ⟵ · C2 ·→✓ ⟵ · C3 ·→✓ ⟵ · C4 ✗→✓ ⟵ · C5 ·→· · C6 ·→·
- **Command & parsing:** F1 ✓→✓ · F2 ✓→✓ · C1 ✓→✓ · C2 ✓→✓ · C3 ✗→✗ · C4 ✗→✓ ⟵ · C5 ✓→✓ · C6 ·→✓ ⟵
- **Narration:** F1 ✓→✓ · F2 ✓→✓ · C1 ✗→✓ ⟵ · C2 ✓→✓ · C3 ·→· · C4 ✓→✓ · C5 ✓→✓ · C6 ·→✗ ⟵
- **AI aliveness:** F1 ✓→✓ · F2 ✓→✓ · C1 ✓→✗ ⟵ · C2 ✓→✓ · C3 ✓→✓ · C4 ✓→✓ · C5 ✓→✗ ⟵ · C6 ✓→✗ ⟵
- **Agendas & formables:** F1 ✓→✓ · F2 ✓→✓ · C1 ✓→✓ · C2 ✓→✓ · C3 ✗→✓ ⟵ · C4 ✓→✓ · C5 ·→✓ ⟵ · C6 ·→✗ ⟵

### 3.1 The rises, and the step that made each

**The ending: C1, C2, C3, C6.** Step 1, "The peace holds", built these: the summons, the alarm forecast, every refuser's price, and a sitting that dissolves for a named cause. On the CONG arm the Congress dissolves on turn 28 and names the provinces it fell for.

**Diplomacy.**
- **C3:** the volte-face fires through §6 row 20 (Step 7 slice 6).
- **C4:** the Cabinet's verbs start a mission or refuse with a price (Step 4, W4/CRT-8).
- **C6:** no treaty is refused after it was accepted on the commanded arms (Step 1, SF-V1).

**First contact.**
- **C1:** 14 → 2 question shrugs on the fresh HOLD (Step 4, the state desk).
- **C3:** the desk answers "where are the Russians" and "why is Europe alarmed" (Step 2).

**Economy C3:** the quoted Charges equal the billed ones on battle-free turns (Step 6, SF-V7).

**Naval C3:** the expedition quotes its odds and names its lever, and Munster falls (Step 6, SF-V6).

**Living balance: C1, C2, C4, C5.**
- An AI-vs-AI war, and a standalone third-party settlement, on every seed (Step 3 SF-LB-1, Step 4 SF-LB-2/2b/2c).
- No declaration inside the fresh-peace floor.
- After the peace the page names the next league and its keep-out prices (Step 7b).

**Combat legibility.**
- **F1:** every battle line names both sides' losses (Step 2, SR-6a).
- **C6 (EYES):** the diorama's contingents and their losses read at both scales.

**Marshal drama C3:** 59 voiced battles, none repeated within three wins (Step 2, SF-MD-1).

**Vassals C6 (EYES):** the boot Vassals tab reads at both scales.

**UI/UX: F1, F2, C1–C4.** The client arm ran for the first time, and found 0 script errors, 0 blank frames, 0 buttons off-screen, 0 clipped text, and 0 raw keys, `<null>`s or `(s)`s. C4: the worst end turn raised 3 blocking modals (the B-slices and Step 1's PL-14 net).

**Command.**
- **C4:** every docked command line executes or asks (Chunk 3b).
- **C6:** the OP-LIVE arm, measured for the first time — 0 misreads, 0 lines lost to the model.

**Narration C1:** no headline class holds the page for more than 4 of 10 turns (Step 7b's standing-line rule).

**Agendas.**
- **C3:** gate terms flip to met between saves.
- **C5:** the carve is stated, proclaimed and flipped in play (Step 5, the AGD arm).

### 3.2 The falls, and what each one is (§7.3: a fall blocks until it is explained)

| Item | What happened | What it is |
|---|---|---|
| **Economy C1** ✓→✗ | On LAW the Staff is enacted at loop 10; the item asks 9. | The field read's measured cost (§6 row 22): France loses fewer men, fields about 10,000 more by turn 2, and pays their upkeep. **The user's**, before SF-R — unanswered. |
| **Marshal drama F1** ✓→✗ (a floor) | 5 crisis-tier petition modals on the flagship arm; the item asks ≤ 4. | The same row: the bigger victories crown more men, and the crisis tier keeps its modal (B1). **§6 row 22, the user's.** |
| **Marshal drama C1** ✓→✗ | OP shows 6 petition modals and 2 audiences; the item asks ≤ 3 and ≥ 3. | The same cause on the OP arm (more crowns → more crisis-tier cards). **§6 row 22.** |
| **Marshal drama C5** ✓→· | No claim read as eroded. | **The instrument (SFR-I4).** The dispatch now says "Lannes's claim is 21 turns in arrears" without "Marshal" (SF5-X3's style helper), and the reader keys on "Marshal X's claim". The digest also does not record the Unmet Marshals block where the earlier notice lives. Corrected for the copy alone, the reader would read OP's Soult as unannounced, which it cannot see either way. Left unmeasured; the pillar is not exercised and its floor is red regardless. |
| **AI aliveness C1** ✓→✗ | 15 laws and **2 lapses** on CMD-M: Austria cannot pay for the Landwehr, then the Generalissimus, at turns 35–37. | A real AI defect (**SFR-B14**, SF-RR4). RF-3's purse test reads the chest at the enactment only; the player has the lapse forecast and the repeal lever, and the AI does not use them (GR5). |
| **AI aliveness C5** ✓→✗ | Archduke Charles fortifies, unfortifies and fortifies again within 3 turns (CMD-H turns 8–11, 33–36). | The field-read board (row 16) and the item's wording: **§6 row 18, the user's**, before SF-R — unanswered. |
| **AI aliveness C6** ✓→✗ | Visible AI attacks on CMD-H 15/24, CMD-A 5/19 and CMD-M 11/39 of the turns at war; the item asks ≥ 50% on every arm. | Part reader, part game. The reader counts any court's declaration as France at war (**SFR-I5**): on CMD-M, "Prussia has declared war on Hanover" lands on the turn of France's peace and counts 22 peace turns. Read France-only, the arms give 8/10, 5/19 and 11/17. The verdict holds on CMD-A, where the league that declares at turn 31 attacks on 1 of its 10 turns — **SFR-DR1**, a design question for the user (§5). |
| **First contact C2** ·→✗ (EYES) | The panel, 3 of 3. | **SFR-H8.** "How many turns would it take Davout to march from Rhineland to Lorraine?" → "No lawful road runs from Rhineland to Rhineland." |
| **Naval C6** ·→✗ (EYES) | The panel, 2 of 3: the compact top bar's nav buttons are blank at 2.0, and the Admiralty chip is gold, not crimson. | Probably the capture, not the client (**SFR-I3**: the harness loads a non-null icon that draws nothing; `top_bar._fit_bar`'s letter fallback fires only for a null one). **The user's eye decides.** |
| **Narration C6** ·→✗ (EYES) | The panel, 3 of 3. | Standing headlines hold the page on mornings with bigger news. On CMD-H turn 27, "Lannes's claim is 21 turns in arrears" leads while France enters a war (also SFR-B9). |
| **Agendas C6** ·→✗ (EYES) | The panel, 2 of 3. | `IQ10_WIZARD_FORMABLES_ENTRY` shows only "Loading…" — the entry frame was shot before its list arrived; the fresh-boot step-1 frame shows the Formable Nations entry. A re-shoot is SF-RR5's; **the user's eye decides.** |
| **Combat legibility C3**, **vassals C5**: ✗→· | No capital taken after a field battle; no client capital attacked. | The board no longer produces the event: RS-3 halts a field win before the works (Step 3), and VD-C's contingents defend the clients (Step 5). Neither was a passing item; no ceiling was lost. |

Every fall is explained:
- three are the user's open rows (§6 rows 18 and 22);
- three are filed defects (SFR-B14, SFR-H8, and the narration EYES class);
- two are the instrument;
- one is the user's eye;
- two are a board that no longer produces the event.

### 3.3 What the instrument mis-read (filed; corrected marks shown, not claimed)

| Row | Item | As read | Corrected | Effect |
|---|---|---|---|---|
| **SFR-I7** | Combat legibility C5 (no raw keys in combat text) | ✗ on both readings | ✓ on both. Every raw key it counts is in the enemy-phase text the client never renders (baseline 124, final 46); the ⚔ and MUSTER lines carry none on either tree. | Combat legibility: baseline 2 → 3 ceilings, final 3 → 4, **its target**. The directional on the rule's 13: 7.50 → 7.54. |
| **SFR-I5** | AI aliveness C6 | ✗ (15/24, 5/19, 11/39) | ✗ (8/10, 5/19, 11/17) | None — CMD-A fails either way. |
| **SFR-I4** | Marshal drama C5 | · | ✗, by an instrument still blind to the Unmet Marshals block | None — the pillar stays not exercised, floor red. |
| **SFR-I6** | Combat legibility C4, economy C5 | ✗ on both readings | Not readable: the DL arm's staging drifted (Davout's fortify refused for actions; his levy on Swabia). | Unknown until the arm is re-staged. |

**Why the frozen readers stand.** This reading reports what the instrument built before it read; changing a ruler after seeing its marks is the bias §4 guards against. The corrections land in SF-RR6, and the next reading — a session exit's `check`, or a third full reading — uses them on both archives.

## 4. HOLD, fresh and blind, on both trees

| Tree | C1: question shrugs (of 20) | C3: orders as meant (of 20) | C6: lines read by the model / misreads |
|---|---|---|---|
| `c20d5bba` (the baseline) | 14 | 6 | 2 of 145 / 0 |
| `0f5e8d84` (final) | 2 | 11 | 1 of 145 / 0 |

**The final tree's nine order misses are filed as SFR-H1 … H3, H5 … H7 and H13 (owned by SF-RR1) and SFR-H4 (an order asked as a question, owned by SF-RR2):**
- an issuance premise with a contraction ("if Mack's still in Swabia") refused as a contingency;
- "pass the Staff law" asking for a marshal named Staff;
- a typo after "Tell X to";
- an affordability premise;
- "commission another marshal";
- three levies refused for their ground without naming the marshal;
- a premise already true ("If Ney beat Mack, give him a rente for it") refused as a contingency.

**Its question misses — two shrugs and four wrong answers — are SFR-H8 … H11 and H14, owned by SF-RR2** (H12 is the TYPED arm's).

**Neither tree executed a line the player did not mean on the HOLD.**

## 5. The findings rate (§4.4 — beside the score, never subtracted)

| Source | Turns | Rows | Per 10 turns | P1 · P2 · P3 · P4 |
|---|---|---|---|---|
| Hand-played depth campaign | 26 (16 keyed, 10 keyless) | 43 | **16.5** | 1 · 25 · 16 · 1 |
| … turns 1–10 | 10 | 27 | 27.0 | |
| … turns 11–20 | 10 | 11 | 11.0 | |
| … turns 21–26 | 6 | 5 | 8.3 | |
| Driver arms (HOLD, the panel's verified flags, the reading's own items) | 808 | 34 | 0.4 | 0 · 5 · 23 · 6 |

**How the hand count was settled:**
- **One P1, verified at the wire on the final tree (SFR-D11).** The playtester's three other claimed P1s (SFR-D5, D28, D29) are graded P2, and each row says why: a driver artefact, the truce's own rule with a missing warning, and a false warning.
- **Two rows were not about the game:** SFR-D12 and D13 read enemy-phase text the client never renders. They are folded into the instrument row SFR-I2 and counted once.
- **The keyless stretch found fewer rows (8 against 36).** It played after the war had ended, on a quieter board.

**The driver rate is not comparable to the hand rate.** The arms are a benchmark, not a defect hunt. Their rows come from three sources:
- the panel reading the digests and frames;
- the reading's own items;
- the fresh HOLD.

## 6. The census (`tools/defect_census.py`, at the commit that lands this memo)

**Totals:**
- **defect:** 77 OPEN — 1 P1, 30 P2, 39 P3, 7 P4. Before the reading the defect ledger stood at 0 open.
- **design:** 2 OPEN, both the user's: SF-NAV-1-D1 (§6 row 17) and SFR-DR1.

| Pillar | Open | P1 | P2 | Rows |
|---|---|---|---|---|
| command | 18 | 1 | 10 | SFR-H1–H3, H5–H7, H13, D7–D11, D20, D24, D25, D37, D38, D41 (**P1: SFR-D11**) |
| narration | 11 | 0 | 4 | SFR-D14, D21, D29, D30, D32, D33, D36, D43, D44, B8, B9 |
| diplomacy | 10 | 0 | 5 | SFR-D16, D26, D28, D34, D40, D42, B1, B2, B5, B13 |
| first contact | 10 | 0 | 2 | SFR-H4, H8–H12, H14, D1, D2, D19 |
| none (the instrument) | 6 | 0 | 0 | SFR-I2–I7 |
| ai aliveness | 5 | 0 | 1 | SFR-D5, D35, B4, B14, DR1 |
| combat legibility | 5 | 0 | 2 | SFR-D4, D15, D17, D31, B10 |
| marshal drama | 5 | 0 | 3 | SFR-D3, D6, D18, D22, B6 |
| economy | 2 | 0 | 2 | SFR-D23, D39 |
| ui/ux | 2 | 0 | 0 | SFR-D27, B11 |
| vassals | 2 | 0 | 0 | SFR-B7, B15 |
| agendas | 1 | 0 | 0 | SFR-B12 |
| ending | 1 | 0 | 1 | SFR-B3 → ROADMAP 13 (VP-2) |
| naval | 1 | 0 | 0 | SF-NAV-1-D1 (design, the user's) |

**Every open row carries an SF tag and an owner:**
- the residue slices SF-RR1 … RR6 (`SCORE_FINISH_SPEC.md` §3 Step 9);
- ROADMAP 13, for the Imperial Peace's morning;
- the user, for the two design rows.

## 7. The done-when (§7)

| # | Condition | State |
|---|---|---|
| 1 | Every live defect row closed, or handed outside under GR9 | **✗** — 77 open, all owned (§6). The reading filed 77 rows against a ledger that stood at 0. |
| 2 | Every design row disposed | **✓, with the user** — the two open rows are the user's rulings, each with its evidence and recommendation. |
| 3 | Same instrument and checklist version; every pillar at target with both floors green and no P1; no fall unexplained | **✗** — same instrument and v1 ✓; 8 of 14 at target; every fall explained (§3.2). |
| 4 | The panel published | **✓** — `panel.json`; claims per §4.5 (§2). |
| 5 | A played road reaches the Congress, and the sitting holds or dissolves for a visible cause | **✓** — SF-END-1 (Step 1) and the CONG arm (ending C1: dissolved on turn 28, its cause named). |
| 6 | The §6 rulings answered | **✗** — rows 18 and 22 are recommendations not applied, the user's; rows 17, 19, 20 and 21 were ruled under the delegation and are FOR USER CONFIRMATION. |

**Per pillar short of target, the residue and its owner:**

- **Combat legibility (3 of 4).**
  - C5 is the instrument (SFR-I7; corrected, the pillar reaches 4 — §3.3).
  - C4 is the DL arm's staging (SFR-I6).
  - Owner: **SF-RR6**, then a re-read.
- **Marshal drama (not exercised; F1 red).**
  - F1 and C1 are **§6 row 22, the user's**: the crisis tier's threshold is the lever the row names; never the field read.
  - C5 is the instrument (SFR-I4, SF-RR6).
  - C4 and C6 had nothing to read on the arms (no crown moved; the panel could not judge the petition frame at 2.0, SFR-B11).
- **Command (P1).** SFR-D11 caps it. Owner: **SF-RR1, first**. The pillar's items meet the target (5 of 5) without the cap.
- **Narration (4 of 5).**
  - C6 (EYES, provisional): standing headlines over bigger news (SFR-B9, D43). Owner: **SF-RR3**.
  - C3 had nothing to read: no road came within 5 of the summons.
- **AI aliveness (3 of 5).**
  - C1: SFR-B14, **SF-RR4**.
  - C5: **§6 row 18, the user's**.
  - C6: SFR-DR1, **the user's**, after SF-RR4's probe.
- **Agendas (5 of 6).** C6 (EYES, provisional): the formables entry frame is to be re-shot. Owner: **SF-RR5**; the user's eye decides.

## 8. Limits of this reading

- **The EYES marks are the panel's, and provisional.** The user chose to review them later; any of the six marks the user changes flips its item and is re-read with `score_run.py check --eyes`.
  - **UI/UX C5** ("the user signs off ≥ 9 of 10 named frames") was not marked: the ten frames were never named.
  - **UI/UX C6** ("a 5-turn Mode C session") was not run for this reading.
  - Both are the user's to mark.
- **The panel's own context carries CLAUDE.md**, which quotes older impression scores, as at the baseline. The scorers were told to disregard it. No scorer cited it.
- **The depth campaign was played by an agent through the driver**, not by a human at the client. Its rows are the playtester's, verbatim, and mostly unverified beyond the quoted digest lines; each row says so. SFR-D11 was reproduced at the wire, and SFR-D34 on the OP arm.
- **The game code is `0f5e8d84` exactly.** The instrument's additions — the OP-LIVE arm, the C6 and UI/UX readers, the suite arm's encoding — ride the commit that lands this memo. The c20d5bba re-read used the same additions on its worktree.
- **Seeded outcomes are reported per seed**, never as laws: CMD-H / CMD-A / CMD-M are the historical, austerlitz and marengo seeds.
- **Three readers are known wrong** (SFR-I4, I5, I7) and one arm's staging has drifted (SFR-I6). The reading uses them as built (§3.3).

## 9. What follows

**Step 9 — the residue of the final reading** (`SCORE_FINISH_SPEC.md` §3) owns 76 of the 77 rows, in six slices, in this order:

1. **SF-RR1 "the orders the reading met"** — the P1 first.
2. **SF-RR2 "the desk answers what was asked"**.
3. **SF-RR3 "the page and the copy"**.
4. **SF-RR4 "war, truce and the standing order"** — SFR-DR1's probe first.
5. **SF-RR5 "the frames at both scales"**.
6. **SF-RR6 "the instrument reads what the player sees"**.

**After Step 9:**
- each slice's session exit re-reads the AUTO items it touched (§5);
- SFR-B3 is ROADMAP 13's;
- the ROADMAP spine resumes at position 11, Playtest Round 0.

## Addendum — after the reading (October 5, 2026, the same session)

SF-RR1 part (i) landed after the reading was taken and committed (`1ab11696`). It fixed **SFR-D11**, the P1 that capped command, and **SFR-H1**, the contracted premise (rules `SYSTEMS_REFERENCE.md` §96).
- **The reading above stands as measured.** Command reads 6.00 at the reading, and the directional stays 7.50.
- **The census after the slice:** defect 75 OPEN with **no P1**.
- **The fresh HOLD arm re-run on the slice's tree:** command C3 12 of 20 (11 at the reading). The item still fails its bar of 18, and SF-RR1 part (ii) owns the remaining misses.
- **No other arm was re-run.** This is a session exit's item flip, not a second reading (§5).
