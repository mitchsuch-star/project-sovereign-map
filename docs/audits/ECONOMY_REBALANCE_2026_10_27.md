# The economy rebalance — S14j (October 27, 2026)

**The brief, in the user's words:** *"i mean a revalnce of amounts would fix it, dont be dense,i approve events but lets actually fix this economy before build too it shouldnt run away like this. in reall ife you need to maintain conquests etc etc look into why its a runaway theres ways to fix this"* (October 27, 2026).

**The ruling it amends.** Four earlier records let a peaceful treasury grow without bound. The user's sentence overrides all four:
- the August 7 gate ("golden peace … effectively unbounded — allowed, that is the blessing", `ECON_BALANCE_GATE_2026_08_07.md`);
- IQ-1 §0.2 ("IQ-1 does not tax a winning, peaceful, stable France", `IMPROVEMENT_QUEUE_SPEC.md`);
- SRX-D1 ("a golden peace may grow rich");
- EAD-6 ("the peaceful hoard … kept inert by design", `ECONOMY_GATE_2026_10_05.md`).

**Record.** Rules: `SYSTEMS_REFERENCE.md` §159. Seams: `tests/_oct27_seams.py::S14J_SEAMS_BY_ROW`. Series attribution: `tools/_s14j_series_arms.py`. Plan row: `PRE_DEPLOY_PLAN.md` §2 S14j.

## 1. The baseline — measured on the tree before S14j (S14i complete, `e132a8d5`)

**Sources:**
- `tools/score_run.py run --only CMD-H --only CMD-A --only CMD-M --only REACH-AAR`;
- `tools/_vp1_road_arms.py --arms RH` on historical, austerlitz and marengo;
- `tools/ai_v_sweep.py` arm C (ten seeds, `PYTHONHASHSEED=0`);
- an in-process boot probe.

These are the runs the recurring-events gate measured the same morning. They were not archived then; this section archives them.

### 1.1 The commanded France — where the gold comes from

| Arm | Turn | Chest | Field army | Land | Trade | Tribute | Upkeep | Charges (rate) | At war |
|---|---|---|---|---|---|---|---|---|---|
| CMD-A | 2 | 1,589 | 148,351 | 2,590 | 450 | 937 | 2,300 | 0 | 3 courts |
| CMD-A | 10 | 15,660 | 113,351 | 2,728 | 587 | 459 | 1,532 | 929 (170) | 1 |
| CMD-A | 20 | 26,186 | 95,801 | 2,590 | 587 | 625 | 1,372 | 2,314 (239) | 0 |
| CMD-A | 30 | 43,217 | 67,624 | 2,590 | 549 | 1,157 | 512 | 454 (28) | 0 |
| CMD-A | 40 | 75,439 | 57,107 | 2,590 | 549 | 1,187 | 432 | 844 (29) | 0 |
| CMD-H | 30 | 47,404 | 77,771 | 2,790 | 587 | 562 | 592 | 510 (28) | 0 |
| CMD-H | 34 | 58,377 | 72,082 | 2,790 | 499 | 562 | 544 | 644 (29) | 0 |
| CMD-H | 40 | 42,980 | 47,794 | 2,397 | 499 | 562 | 700 | 5,601 (342) | 6 courts |
| CMD-M | 30 | 41,814 | 63,591 | 2,590 | 549 | 937 | 504 | 2,798 (176) | 1 |
| CMD-M | 40 | 49,704 | 79,385 | 2,576 | 549 | 937 | 600 | 1,460 (77) | 0 |

**What France holds.** On all three commanded seeds France holds its 28 boot provinces at turn 40, give or take one. The pile does not come from conquest.

**Over 40 turns:**
- The field army melts from ~150–165k to ~48–80k (battles and attrition, never refilled).
- Upkeep falls from ~2,300–2,900 to ~430–700.
- Gross holds at ~3,900–4,350.

**At peace the chest climbs:**
- about +3,200 a turn on CMD-A, turns 28–40;
- about +2,700 a turn on CMD-H, turns 18–34.

**The Charges at peace** run at a rate of 27–29 (1.1–1.2% a turn of the chest above 2,000).

### 1.2 The courts

| Arm | AI purses, total at T5 | at T40 | Ottoman at T40 | Spain | Denmark | Sweden |
|---|---|---|---|---|---|---|
| CMD-A | 62,530 | 452,806 | 79,477 | 54,554 | 33,261 | 34,142 |
| CMD-H | 63,327 | 380,493 | 78,815 | 32,681 | 33,261 | 28,367 |
| CMD-M | 63,375 | 432,946 | 78,815 | 53,556 | 33,261 | 34,142 |
| AI-V arm C (median of 10) | — | 328,770 | 74,892 | 32,905 | 28,080 | 34,382 |

The passive France of arm C is poor: a median of 3,812 at turn 40, range −1,044 to 5,426. The conquering France of VP1-RH ends at 9.4–15.8k, losing provinces to the coalition (28 → 13–20). Neither runs away. The runaways are the commanded France at peace and every AI court.

### 1.3 The boot (turn 1, the historical seed)

| Court | Provinces | Land | Field men | Upkeep | Force limit | Garrison men | Ledger Net |
|---|---|---|---|---|---|---|---|
| France | 28 | 2,590 | 189,000 | 2,834 | 130,000 | 49,000 (Paris 25k, Normandy 12k, Flanders 12k) | 828 |
| Britain | 11 | 2,326 | 30,000 | 240 | 87,500 | 25,000 | 2,851 |
| Russia | 10 | 1,700 | 70,000 | 560 | 85,000 | 25,000 | — |
| Austria | 7 | 1,250 | 126,000 | 1,232 | 77,500 | 25,000 | 405 (homeland-only +18; trade 350) |
| Prussia | 6 | 1,050 | 78,000 | 636 | 75,000 | 25,000 | — |
| Spain | 9 | 1,350 | 15,000 | 120 | 82,500 | 15,000 | 1,270 |
| Ottoman | 14 | 2,000 | 24,000 | 192 | 95,000 | 15,000 | 1,808 |
| Sweden | 9 | 1,100 | 12,000 | 96 | 82,500 | 15,000 | — |
| Naples | 1 | 300 | 18,000 | 144 | 62,500 | 15,000 | — |
| Denmark | 6 | 800 | 16,000 | 128 | 75,000 | 10,000 | — |
| Bavaria | 3 | 650 | 22,000 | 176 | 67,500 | 10,000 | — |
| Portugal, Hanover, Saxony, Hesse, the Papal States, Sardinia | 1–6 | 300–700 | 0 | 0 | — | 10,000 each | — |
| Holland, the Kingdom of Italy, Switzerland (France's satellites) | 1–4 | 300–500 | 0 | 0 | — | 10,000 each | — |

**Garrisons draw no pay.** 330,000 garrison men stand across Europe, and `calculate_turn_upkeep` bills marshals only. Any corps detached into a garrison stops costing anything.

## 2. Why it runs away

1. **At peace France pays only for its field army, and the army melts.**
   - Upkeep is billed on the corps' fielded strength ("you pay for the soldiers you have", July 14).
   - Battles and attrition take ~100k men over 40 turns, and the scripts do not refill them. The bill falls ~2,300 a turn.
   - Gross stays at ~4,350 a turn: 2,590 from the land, ~550 trade, 560–1,190 tribute.
   - The result is +3,000 to +3,800 a turn at peace.
2. **Nothing France holds costs anything.**
   - Its 49,000 garrison men are free.
   - A conquest settles to a 10% charge within 6–11 turns.
   - The homeland, the clients and the laid-up fleet cost nothing.
3. **Even a full army is cheap at peace.**
   - France at peace with its whole 189,000 men still nets ~1,700.
   - The opening balances because of war-time costs: the Grande Armée premium 882, campaign pay 204, the blockade 175 and the Admiralty 90. Every one of them ends at peace.
4. **The one brake on a pile is 1.2% a turn.**
   - The crown term (30) sets the peace plateau at 2,000 + 2,500 × surplus / 30, which is ~200–280k.
   - The time constant is 83 turns, so the brake never binds within 40 turns.
5. **The courts run the same rules on one small corps.**
   - The Ottomans field 24,000 men (192 a turn) on 2,000 income.
   - Nine courts field no army at all.
   - Each banks 70–95% of its income.

## 3. Why amounts on holdings alone cannot close it

**The opening is tuned and boxed:**
- France's turn-1 absorption (E1) is 0.722 against a ceiling of 0.74. The upkeep rate 8 is the only integer that fits, and gross can fall only 97.
- Austria's homeland-only margin is +18.

**Every turn-1 amount moves the opening.** That covers the upkeep rate, tribute, trade, the land and any homeland charge.

**The largest boot-neutral move falls short.** It would shift all ~1,350 of the war-time costs onto peace maintenance, and a demobilized France would still bank ~2,450 a turn. Tribute and trade cuts break E1 and only move the gold into the clients' hoards.

**So two things must change:**
- the state's own running cost — the crown term, "the household, the pensions, the ministries" — must rise;
- the holdings must cost what they should.

**The counterfactual.** Each arm's recorded flows were replayed, the behaviour held, with only the crown term changed:

| Crown | CMD-A France T40 | CMD-H | CMD-M | AI total T40 (A / H / M) | Ottoman |
|---|---|---|---|---|---|
| 30 (shipped) | 75,761 | 43,172 | 49,876 | 452,806 / 380,493 / 432,946 | 79,477 |
| 100 | 57,316 | 31,227 | 38,415 | 311,416 / 247,781 / 300,075 | 52,021 |
| 150 | 48,182 | 25,506 | 32,831 | 250,434 / 190,916 / 242,709 | 40,374 |
| 200 | 41,246 | 21,310 | 28,629 | 208,623 / 152,318 / 203,372 | 32,514 |
| 300 | 31,624 | 15,803 | 22,819 | 157,101 / 104,960 / 154,554 | 23,097 |

## 4. The rebalance, as built

Three amounts. The same functions bill every court (GR5). Each amount sits behind a named seam (`tests/_oct27_seams.py::S14J_SEAMS_BY_ROW`), and the recorded boards hold all three down (`OCT27_SEAMS_DOWN`).

| Row | The amount | Where | Turn 1 |
|---|---|---|---|
| **J1** a detached garrison keeps its pay | A corps detached into a garrison (`region.garrison_detachment`, the `garrison` verb's own flag) draws the field rate, 8 per 1,000, inside the base. It stays outside the force limit, the Grande Armée, the levy and the substitute market. | `world_state.garrisons_draw_pay`, `garrison_pay_of`; `calculate_turn_upkeep` (`garrison_pay`, `garrison_men`); the vassal grant's `garrison_relieved`; the ledger's upkeep note | Unchanged: no detachment stands at boot |
| **J2** conquests cost what they yield until they are French | Every occupation tier +0.15: 0.50/0.35/0.20/0.10 → 0.65/0.50/0.35/0.25. A settled conquest nets three-quarters of its base, not nine-tenths. | `region.occupation_fraction_for` | Unchanged: nobody holds non-homeland soil |
| **J3** the state's running cost | The Charges' crown term 30 → 250: a tenth of the chest above the 2,000 floor each turn at peace. The AI's purse reads the Net before the Charges, the counsel's rule (EA-18), in the laws rung and the arming rung. | `world_state.charges_crown_rate`; `reforms.ai_reads_net_before_charges` | Unchanged: every chest boots at or under the floor |

### 4.1 What was tried and taken back: paying every garrison

**The first J1** paid every province's garrison: the courts' standing capital garrisons (330,000 men) as well as the detachments. To keep France's opening bill it moved the Grande Armée threshold to 162,000. It held turn 1 and E1, but the measurement turned it back.

**What it did to the courts.** It drew ~2,200 a turn from them:
- Austria's homeland margin fell to −182 and Switzerland's ledger Net to −5.
- The coalition's war chests emptied. Holding J1 alone down on the conquest road gives the scripted conqueror 9–14 provinces at the end (austerlitz, historical); with J1 up it gives 23–27.
- On CMD-H and REACH-AAR it combined with the crown into a 25–30-turn war with Russia, or Britain, funded by British sponsorship.

**The ruling.** A court's standing garrison is raised and kept by its capital, and the courts' war chests are the coalition's strength. Only a detachment draws pay. That closes the exploit (a corps parked in garrisons for free) and charges the men who hold a conquest.

### 4.2 The crown: why 250

Each candidate was measured on the four commanded arms with the narrowed J1 and J2 up. The ceiling is the chest the Charges steer toward (the ledger's own reading).

| Arm | Crown 200: chest at T40 / ceiling | Crown 250: chest at T40 / ceiling |
|---|---|---|
| CMD-H | 22,997 / 17,108 (a war at turn 36) | 18,516 / 15,747 |
| CMD-A | 35,905 / **49,350** | 31,838 / 39,880 |
| CMD-M | 30,010 / 32,990 | 26,342 / 28,008 |
| REACH-AAR | 21,192 / 36,775 | 23,179 / 30,930 |
| AI purses at T40 | 175–218k (two arms over 200k) | 146–193k |

**250 is the lowest value that held both targets on all four arms:** France under 40k, every court under 35k, the courts' total under 200k. At 200, CMD-A steered to 49k.

## 5. The measured after-state (crown 250)

**Sources:**
- `tools/score_run.py run --only CMD-H --only CMD-A --only CMD-M --only LAW --only DL --only REACH-AAR --only AIV` on the S14j tree;
- the same on HEAD in a detached worktree for the like-for-like baseline;
- `tools/_vp1_road_arms.py --arms RH` on three seeds;
- the AIV arm's ten ambient seeds.

### 5.1 France

| Arm | Before: T40 chest / ceiling | After: T40 chest / ceiling | War turns before → after |
|---|---|---|---|
| CMD-H (historical) | 42,980 / 20,450 (58,817 at T35, then a six-court war) | 18,516 / 15,747 | 16 → 16 |
| CMD-A (austerlitz) | 75,439 / 330,666 | 31,838 / 39,880 | 17 → 22 |
| CMD-M (marengo) | 49,704 / 111,750 | 26,342 / 28,008 | 23 → 17 |
| REACH-AAR | 44,893 / 246,583 | 23,179 / 30,930 | 21 → 22 |
| VP1-RH (×3) | 9.4–15.8k at the end | 8.3–9.8k at the end | at war throughout |

**The conquest road.** The scripted conqueror stamps the Decisive Peace at turn 13 on all three seeds; before, marengo never stamped. The coalition still breaks the conqueror: 17 / 18 / 20 provinces at the end on austerlitz / historical / marengo, against 13 / 20 / 28 before (marengo's eclipse at turn 30 then, its fall at 33 now).

**The passive France** (AI-V arm C) is as poor as it was: a T40 median of 3,327 (was 3,812).

### 5.2 The courts

| Reading | Before | After |
|---|---|---|
| AI purses at T40, CMD arms | 380–453k | 146–193k |
| AI purses at T40, AI-V arm C median (10 seeds) | 328,770 | 160,834 |
| The Ottoman Empire at T40 | 75–79k | 26–27k |
| Spain / Sweden / Britain at T40 (arm C median) | 32.9k / 34.4k / 13.7k | 18.2k / 13.3k / 11.7k |
| AI-initiated wars per ambient seed | 1 on every seed | 1 on every seed |

### 5.3 The checklist, like for like (the same seven arms on HEAD and on S14j)

- **Directional:** 6.75 → 6.88. **Economy:** 7.50 → 8.00.
- **Two items flip to pass:**
  - diplomacy C1 — no peace re-broken within five turns (before, CMD-M's Austrian peace was re-broken by an alliance cascade);
  - economy C3 — the Charges quoted equal the Charges billed on every battle-free turn (0 of 3 before, 2 of 2 after).
- **No item regresses.** Economy C1 (the Staff on the LAW arm) and AI aliveness C6 fail before and after.
- **AI aliveness C1 holds, with fewer laws abroad:** (17, 13, 18) enacted against (20, 20, 17).

### 5.4 The series and the records

**The ambient series** (`tools/_s14j_series_arms.py` → `tools/_s14j_series_arms_final.json`):
- Arm 0 (all three held down) reproduces S14i's series byte for byte.
- J1 or J2 held down alone is byte-identical to the shipped series.
- **J3 alone moves it, at [12].** The courts' purses are smaller, so the bribes that buy France's clients land on other turns: Switzerland a turn later (13, was 12), Holland a turn sooner (16, was 17). The idle France's alarm reads 31 at [12] and reaches 0 at [16].

**The seven-seed probe record** (`docs/audits/probes/sf_lb2/`), re-recorded: every seed's crises, declarations and end-of-campaign wars are unchanged; only the rows' chests move.

**The DD-1 quick records** read 0 / 0 (A / B) as before.
