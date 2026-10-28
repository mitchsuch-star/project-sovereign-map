# The courts take the field — the record (S14k, October 28, 2026)

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
