# The courts take the field — the record (S14k, October 28, 2026; part 1 §1–6, part 2 §7)

**The ask.** The user, October 28, 2026: "they should get armies or the ability to make them, we want the game dynamic", then "it should be possible for underdog stories, see EU4: generally the same but some runs are surprising". The plan was approved the same day (Plan Mode). The rules live in `SYSTEMS_REFERENCE.md` §160; this file holds the history, the prototype and the measure, per seed.

## 1. What was wrong (measured on HEAD `49f229d4`)

| Court | Provinces | Income | Boot army | Bench | Why it never acted |
|---|---|---|---|---|---|
| Portugal | 4 | 600 | none | none | no marshal → turn skipped; EA-7's rung found no bench |
| Saxony | 1 | 300 | none | none | the same |
| Hanover | 6 | 700 | none | none | the same — Prussia's "defenceless prize" on every seed |
| Hesse | 2 | 350 | none | none | the same |
| Sardinia | 1 | 300 | none | none | the same |
| Papal States | 1 | 300 | none | none | the same |
| Holland* | 4 | 450 (−337 tribute) | contingent in France's war | none | the same |
| Kingdom of Italy* | 2 | 500 (−375 tribute) | contingent in France's war | none | the same |
| Switzerland* | 1 | 300 (−225 tribute) | none | none | the same |
| Denmark / Naples / Ottomans | 6 / 1 / 14 | 800 / 300 / 2,000 | one general each | none | the day he fell, armyless for good |

\* France's satellites (VD-C contingents fly France's flag). A bought client's "march" against France (OCT27-D12) wrote the war and raised no man.

## 2. The history (a sourced Sonnet researcher; Wikipedia, the ADB on Wikisource, the Napoleon Series, Treccani, the Swiss army's own pages)

- **Portugal:** ~20,000 effectives in 1807 against 48,396 on paper; 18,000 fielded in 1801; ~35,000 regulars under Beresford at the peak; neutral in 1805. Silveira bold to rash (Chaves, Amarante 1809); Bernardim Freire cautious and prickly (the northern army 1808; lynched at Braga 1809); Gomes Freire led the Portuguese Legion for France.
- **Saxony:** a 15,000-man observation corps in the autumn of 1805; 21,144 mobilised in 1806; 31,780 at the 1810 peak. Zezschwitz (b. 1736) cautious and orderly at Jena; Thielmann bold; Le Coq prudent (Grossbeeren, Dennewitz; the Netherlands 1814).
- **Sardinia:** no field army — about 4,000 regulars and 11,500 militia held the island; the only name, the viceroy Charles Felix, no soldier.
- **Hesse-Kassel:** partly mobilised in 1806, disarmed without resistance, no commander of note. **Hesse-Darmstadt:** 3,900 mobilised in 1806; Prince Emil, energetic, led the Hessians from 1809 (Russia, Leipzig) and for the Allies in 1814–15. The game's Hesse (Frankfurt and Nassau, "the hedging Elector") is a composite.
- **Hanover:** no army on its soil in 1805 — ~17,000 dissolved at Artlenburg in 1803; the King's German Legion abroad. Ludwig von Wallmoden methodical (the Göhrde 1813); Charles Alten by-the-book (Oman).
- **Papal States:** no field army; Rome taken in 1808 without a fight.
- **Holland:** a 9,421-man division under Dumonceau in 1805; Janssens dutiful (the Cape 1806, Java 1811).
- **Kingdom of Italy:** ~10,000 fieldable in 1805; Fontanelli prudent (Raab 1809, Hanau 1813).
- **Switzerland:** the Mediation contingent 15,203; Wattenwyl General in 1805, 1809 and 1813, cautious; Bachmann led ~20,000 into Franche-Comté in 1815.
- **The siblings:** Christian August of Augustenborg held Norway in 1808 (Prestebakke, Toverud); Hesse-Philippsthal held Gaeta five months in 1806 ("Gaeta is not Ulm"); Alemdar Mustafa raised the Danube's defence in 1806–07.

## 3. The prototype (in memory, before any file was written)

The 40-turn ambient board (the `--emit-series` loop), the content injected at `json.load` so the validator and `from_dict` booted it as authored content; three seeds (historical / austerlitz / marengo).
- **The boot corps alone** (Portugal 15k, Saxony 15k, Hesse 10k in the first draft): byte-identical series, wars and captures on all three seeds — at peace they sit.
- **Benches, no ceiling:** Sardinia (preparing its design against France) armed to 55k / 85k / 65k on one island province; Switzerland to ~35k after its rebellion. The force limit's one floor was the cause; the tiered floor bounded it (Sardinia 25k) and moved no series alone.
- **The history then ruled the list:** Sardinia and the Papal States to garrisons only; Hesse to a bench (Emil was 15 in 1805); Saxony and Portugal to boot corps (the user's ruling).
- **Part 2's drafts (ten seeds):** ambition first — Hesse reaches coerce on 10 of 10 and opens a war on Hanover on 2 (marengo, borodino), Saxony coerce on 10 of 10 and arms on 8: too common; neutrality first — no minor's ambition wakes on 0 of 10: too rare. The target sits between.

## 4. The measure (part 1; like for like, HEAD in a detached worktree)

| Arm (seed) | France's provinces at the end, HEAD → S14k | Notes |
|---|---|---|
| CMD-H (historical) | 29 → **23** | Hanover raises Wallmoden at war with Prussia, retakes Westphalia and East Frisia by 20, joins the Fourth Coalition at 35 (as on HEAD, where it had no men) and takes Picardy, Lorraine, Burgundy, Nivernais, Orleanais and Lyonnais from France's empty interior by 40 |
| CMD-A (austerlitz) | 28 → 28 | France's chest unchanged |
| CMD-M (marengo) | 26 → 26 | France's chest unchanged |
| REACH-AAR | 22 → 26 | re-timed into a different war; the courts' purses 184k → 140k |
| VP1-RH historical | stamp 13 → 12 | |
| VP1-RH austerlitz | stamp 13 → 13 | |
| VP1-RH marengo | stamp 13 → **never** | Hesse, France's satellite since 8 and drawn into Hanover's war, raises Emil at Nassau after Frankfurt falls; Brunswick destroys him and takes Nassau at 13, one turn before the Confederation holds; the Empire falls at 34, as it did after its stamp before |
| AIV arm C (ten seeds) | — | Prussia on Hanover on every seed, on the same turn as before; on friedland a second declaration at 31 (Hanover, armed, had taken ground back and the Hanoverian Prize woke) — one AI-initiated war on nine seeds, two on one (`SWEEP_WAR_ALARM` 6) |

- **The checklist** (`score_run.py compare`): no item flips; directional 6.88 → 6.88.
- **The seven-seed probe record:** every seed's war, crises and end-of-campaign wars unchanged; the rows re-recorded.
- **Kept on the plan's criteria:** F1 holds (23 / 28 / 26 ≥ 20), the coalition still breaks the conqueror on every seed, no checklist item regresses. The two movers are seeded paths, reported per seed: an underdog Hanover on CMD-H and a satellite that fought and lost on VP1-RH marengo.

## 5. One rule narrowed on the measure

The first build read K3 (the call-up) for every court. On the full suite the RS-27 arm (`volte_court_austria`) lost its volte-face beat, and holding the rows down one at a time named K3 alone — with the minors' benches held down too, so the mover was a court that already fielded an army (the great powers' and the secondaries' benches). The plan had titled the row "a menaced court calls up its first general"; the build now reads it only for a court with no general standing. Re-measured on the narrowed rule: the series, the courting cap and the commanded arms read as above, the RS-27 beat lands at turn 27 (26 with the slice held down), and the Ottomans no longer commission at peace on CMD-A.

## 6. The records

- the series `tools/_s14k_p1_series_arms_final.json` (arm 0 = S14j's series byte for byte; K2 + K3 at [11]);
- the seven-seed probe record `docs/audits/probes/sf_lb2/shipped_*.json` (wars, crises, end-of-campaign wars unchanged on every seed);
- the DD-1 quick records `docs/audits/dd1/sign_ability_*.json` (0 / 0);
- the checklist runs were made in the session's scratchpad (`score_run.py run` on HEAD `49f229d4` in a detached worktree and on the slice, `check` against `docs/SCORE_CHECKLIST_V1_2.json`, `compare`): no item flips, directional 6.88 → 6.88.

## 7. Part 2 — the goals and the New Order (October 28, 2026)

The user: "they should have goals — could be surprised if they get rich and strong … won't happen all the time but possible", "make their strength cap make sense for where they could go, for instance what if ottomans reformed, event perhaps", and "it should be possible for underdog stories, see EU4: generally the same but some runs are surprising". The rules: `SYSTEMS_REFERENCE.md` §160.10 on.

### 7.1 What was built
- **G1 the courts' goals** (existing design types only): Saxony's Wettin Crown (Posen, from Prussia — the Wettins wore Poland's crown 1697–1763 and Saxony took Warsaw after Jena); Hesse's Westphalian Duchy (Westphalia, from Hanover — Hesse-Darmstadt held the Duchy 1803–16); the neutral postures of Portugal (the Old Alliance), Hanover (the Electorate) and Switzerland (the Confederation, asleep while France's satellite); Denmark's Scania and the Porte's Black Sea Shore behind their neutrality, so each wakes only in a war (1808; 1806).
- **G2 the sleepier courts:** Saxony `weight_mod` −8, Hesse −12 (the §3.4 statecraft term; every great power stays 0).
- **G3 the New Order** (Nizam-i Cedid): the Porte's one-law deck, 8,000 gold and 200 a turn; a new `force_limit` clause lifts its floor to a great power's (limit 65,000 → 95,000; war ceiling 97,500 → 142,500) and `recruit_morale` +5 infantry; `under_threat` — the AI proclaims it only at war or called to arms; an empty chest lapses it (the Janissaries' revolt of 1807, by machinery).

### 7.2 The tuning lever the plan named did not hold
The plan tuned the two ambitions with deck order and two banded relations (Prussia–Saxony 35, Hanover–Hesse 15). On the board the relations were inert: Saxony–Prussia decays 31 → −17 by turn 10 by itself — each ask Prussia refuses costs Saxony's goodwill, and Prussia's declaration on Hanover costs every neighbour 15 — so the boot number is gone before the moment it was meant to hold. The build tuned with the existing statecraft `weight_mod` instead (G2): it moves how often the ambitions reach `coerce` — and so how often a minor arms from ambition — while the minor's own war stayed 1 of 10 in every draft that let the ambitions wake. The drafts, on the ten ambient seeds:

| Draft | A minor's own war | `coerce` reached | Prussia on Hanover |
|---|---|---|---|
| No `weight_mod`, the relations banded (or not: every count identical) | 1 of 10 (marengo) | Hesse 9, Saxony 8 | 10 of 10 |
| Neutrality first in every deck (the plan's prototype) | 0 of 10 | none | 10 of 10 |
| **Shipped: −8 / −12** | **1 of 10** (marengo, Hesse on Hanover at 19) | **Hesse 4, Saxony 3** | 10 of 10, the same turns as part 1 |

### 7.3 The shipped goals on the ten ambient seeds (per seed; seeded paths, not laws)

| Seed | AI-initiated wars | Minors' commissions (turn, court, the gate after the turn) | The New Order |
|---|---|---|---|
| historical | Prussia → Hanover 10 | Wallmoden 6 (called up); Emil 13; Janssens 33 (Holland's own design) | — |
| ulm | Prussia → Hanover 14 | Wallmoden 7 (called up); Alten 15 (war) | — |
| austerlitz | Prussia → Hanover 13 | Wallmoden 6; Alten 14 | — |
| jena | Prussia → Hanover 10 | Wallmoden 6; Emil 13 | proclaimed at 40 |
| marengo | Prussia → Hanover 11; **Hesse → Hanover 19** | Wallmoden 10; Emil 12 (its design); Wattenwyl 28 (war) | — |
| eylau | Prussia → Hanover 14 | Wallmoden 7; Alten 15; Emil 15 (its design); Le Coq 17; Wattenwyl 24 (war) | **proclaimed at 17** (limit 95,000) |
| friedland | Prussia → Hanover 13 | Wallmoden 6; Alten 14; Emil 14 (its design); Wattenwyl 22 (war); Janssens 33 (war) | — |
| wagram | Prussia → Hanover 12 | Wallmoden 6; Alten 13; Wattenwyl 21 (war) | — |
| lodi | Prussia → Hanover 13 | Wallmoden 6; Alten 14; Emil 14 (its design) | — |
| rivoli | Prussia → Hanover 14 | Wallmoden 7; Alten 15; Wattenwyl 23 (war) | — |

Hesse raises Emil on six seeds of ten (its Westphalian Duchy at `coerce` while Prussia has Hanover beaten or busy), Saxony Le Coq on one; the Swiss raise Wattenwyl after their break with France on five. **The GR10 sibling (OCT27-D12's line "a bought client marches against its old lord"):** checked — the line stands. A bought client has a bench now and raises its corps once it can pay (Holland raised Janssens at war at 33 on friedland, and at 33 on historical for its own design); until it can pay the line names its entry into the war, which is the fact.

### 7.4 The measure, like for like (part 1's tree = part 2's rows held down, byte for byte per the series record)

| Arm (seed) | France's provinces at turn 40, part 1 → part 2 | Notes |
|---|---|---|
| CMD-H (historical) | 23 → **17** | re-timed from turn 8: Austria holds Lyonnais and Piedmont by 10; at 40 France has lost Béarn, Berry, Gascony, Limousin, Piedmont, Provence to Austria and Flanders, Franche-Comté, the Rhineland to Prussia, and kept the three Hanover took on part 1's board; Amsterdam (35) and Bern (40) fall uncontested |
| CMD-A (austerlitz) | 28 → 28 | |
| CMD-M (marengo) | 26 → 26 | |
| the commanded arm, six more seeds | ulm 26 → 24, jena 25 → 22, eylau 28 → 28, friedland 23 → 26, wagram 24 → 23, lodi 24 → 23 | nine seeds: mean −1.1, 8 of 9 at 20 or more |
| VP1-RH historical / austerlitz / marengo | stamp 12 / 13 / never → 12 / 13 / never | marengo: the Empire falls, as on part 1's board |
| AIV arm C (ten seeds, the score run) | — | Prussia on Hanover on every seed, the same turns; friedland's second declaration at 31 gone (10 AI-initiated wars, was 11) |

**CMD-H attributed** (the arm's argv through the driver, one seam held down at a time): the Old Alliance held down alone → 23; G1 → 23, G2 → 22, G3 → 17; Hanover's, Switzerland's, the two ambitions' and the Scania / Black Sea entries held down alone → 17. Britain and Portugal stand at peace, not allied, so a British column on Portuguese soil would breach Portugal's neutrality: Wellesley no longer walks into neutral Lisbon at turn 8, and the board re-times. The same entry, held down alone, returns the series at [11], the courting cap's 12 and the RS-27 volte-face beat at 27.

**The checklist** (`score_run.py compare`, part 1 → part 2): four items flip, all on CMD-H's re-timed board — `living_balance.F1` (22 → 17 by the checklist's read), `narration.C1` (home provinces captured in the worst window 4 → 6), `vassals.C5` (two client capitals taken uncontested), `vassals.F1` (CMD-H satellites 2 → 1); directional 6.88 → 6.75; Economy 8.00 held.

**Brought to the user before keeping** (the plan's keep rule: F1 on 3 of 3): **"Keep it (Recommended)"** — Britain respecting Portugal's 1805 neutrality is the history (it landed in 1808), and the outlier is one seeded path. The RS-27 arm keeps its purpose with the Old Alliance held down, as its six earlier re-seats held their movers down.

### 7.5 SR-8c's refusal record, measured
SR-8c (October 3, under the delegation) recorded that a German minor's covet design "would make each an asker refused by stronger courts — noise in the refusal record, never the scene". On the historical ambient board: Saxony asks Prussia and Hesse asks Hanover once every six turns (the repeat-ask governor) — five refusals each in forty turns; none reaches the dispatch; each refusal is a rung the design climbs. As the designs climb both courts bandwagon toward France — the player's incoming proposals 17 → 24 in forty turns (Hesse 4 → 8, Saxony 0 → 3; open borders, non-aggression). The SR-8c pins and its records (`AI_INTENT_SPEC.md` §7a scene 1, `SYSTEMS_REFERENCE.md` §91.4) carry the amendment; Bavaria stays deckless.

### 7.6 The sibling sweep (GR10)
- Bavaria, Spain and Naples field armies but carry no goal. **The user: "After S15"** — row S14k-3 heads the slices after the deploy (`PRE_DEPLOY_PLAN.md` §2), tracked by the strict xfail `test_every_armed_court_carries_a_goal`.
- A guard names a sphere, not only its court's soil (Prussia's armed neutrality names Hanoverian ground; Italy's French Savoy; Holland's French Flanders) — kept; the Electorate and Prussia's guard both name Hanover, Westphalia and Brunswick, and on a province two active guards name the existing overwrite decides.
- A neutral posture can be bought off (Denmark's and the Porte's already could, 600 gold) — the D5 contract, unchanged.
- OCT27-D12's "a bought client marches against its old lord" — honest: the client raises its corps once it can pay.

### 7.7 The records (part 2)
- the series `tools/_s14k_p2_series_arms_final.json` (arm 0 = part 1's series byte for byte; G1 at [11]);
- the seven-seed probe record `docs/audits/probes/sf_lb2/shipped_*.json` (Prussia's crisis and war unchanged on every seed; Hesse's crisis on friedland, marengo and eylau, its war on marengo);
- the DD-1 quick records `docs/audits/dd1/sign_ability_*.json` (0 / 0);
- the score runs, the CMD attributions and the sweeps in the session's scratchpad.
