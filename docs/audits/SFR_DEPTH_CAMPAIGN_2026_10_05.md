# SF-R depth campaign — the playtester's findings (October 5, 2026)

Played by a separate agent (it could not write files, so its findings came back as text and are recorded here VERBATIM, unverified; the verification is in the final-reading memo). The driver was run in process, one chunk of 2–3 turns at a time, each chunk continuing from the last one's save. France/1805, seed `historical`. 26 game turns: **16 keyed** (`--llm anthropic`, chunks c01–c08 — the key reached the model on 2 lines, both in c04; everything else parsed offline at ≥ 0.7) and **10 keyless** (`--llm mock`, chunks k01–k05). Every run finished `completed`, with no tracebacks and no unknown blockers. The chunk scripts and digests are archived at `docs/audits/score_runs/2026_10_05_sfr/depth/` (the saves were not kept). The rows filed from this report are `BUG_FIXES.md` §Score Finish Step 8, SFR-D1 … D44; each row says what was verified and what was re-graded, and the memo is `docs/audits/SCORE_FINAL_2026_10_05.md`.

| stretch | P1 | P2 | P3 | total |
|---|---|---|---|---|
| keyed (16 turns) | 4 | 14 | 18 | 36 |
| keyless (10 turns) | 0 | 7 | 1 | 8 |

(The severities are the playtester's guesses. Five keyed findings recur in the keyless stretch: D1, D2, D11, D12, D21. The keyless stretch fell after the war ended, so its lower count partly reflects a quieter board.)

## Play log
| chunk | turns | plan | what happened |
|---|---|---|---|
| c00-recon ×2 | (t1, throwaway) | read the board by asking | Mack at Swabia sits next to six French corps |
| c01 keyed | 1–2 | hold Milan, fall on Mack, court Prussia, Anticipated Class | Davout objected (trusted); Murat and Lannes beat Mack, who fled to Munich; open borders with Prussia, the Ottomans and Portugal |
| c02 keyed | 3–4 | Emperor finishes Mack; Massena fortifies Milan | Mack lost 17,976, but the muster pulled Massena and Teulie off Milan; the trusted objection sent Massena into Tyrol (−9,127) and broke the Emperor's corps |
| c03 keyed | 5–6 | rescue the south; offer Austria an armistice | Milan stormed and the Kingdom of Italy eliminated; Austria refused |
| c04 keyed | 7–8 | retake Milan; Grand Quartier Général; feel out Russia | Milan retaken; Bernadotte captured; Prussia signed a defensive alliance |
| c05 keyed | 9–10 | concentrate at Munich; drill | Britain's settlement offer declined |
| c06 keyed | 11–12 | commission Augereau; clear Gascony | Ney turned back for cannon fire; Austria offered an armistice |
| c07 keyed | 13–14 | truce with Austria; deal with the British raiders | Austria took Munich and Swabia under four French corps; Bavaria eliminated; internment countdown began |
| c08 keyed | 15–16 | get everyone home | Emperor home; Russia offered an armistice |
| k01 keyless | 17–18 | march home; Train des Équipages | peace with Austria; British truce |
| k02 keyless | 19–20 | Emperor to Paris; build a market | peace with Russia; the coalition dissolved |
| k03 keyless | 21–22 | court Britain; bid for Sardinia; retake Provence | Provence found in Spanish hands; Austria refused an alliance |
| k04 keyless | 23–24 | pay Soult; sponsor Sardinia; vassalize Hesse | peace with Britain, at war with no one; Hesse refused |
| k05 keyless | 25–26 | pay Massena; keep Austria out of the next league | Austria at −1, out of the league |

The Third Coalition was broken by turn 24. France ended at 28 provinces (gained Milan, Provence held by Spain), having lost the Kingdom of Italy, Bavaria and Bernadotte. The treasury stood at 17,485 at turn 27.

## Findings (verbatim)
Each entry: game turn · stretch · severity · title, then the evidence (chunk, turn) and what the playtester expected.

**D1** t1–2, again t22 · keyed · P2 · "how is the treasury?" gets no answer.
- Evidence: `how is the treasury?` → "Berthier sets down his pen. 'I cannot answer that from the dispatches, Sire.'" (c00-recon t1, c01 t2, k03 t22). `how much gold do we have?` answers in full (recon2).
- Expected: the treasury report.

**D2** t1–26 · keyed, recurs keyless · P3 · The desk shrugs at plain questions.
- Evidence: the same shrug for `what happened at Swabia?` (c01 t2), `who holds Bavaria?`, `who can stop Paget?` (c04 t7) and `who deserves a reward?` (c06 t11).
- Keyless: `who are we still at war with?` shrugs while `who are we at war with?` answers (k01 t17). Also `is the war with Austria over?` (k01 t17), `how loyal are my marshals?` (k02 t19), `who could become our vassal?` (k04 t23), `is Sardinia still in play?` (k05 t26).
- Expected: an answer, or a pointer to where it is.

**D3** t1 · keyed · P2 · Trusting an objection silently cost two orders.
- Evidence (c01 t1): `Massena, dig in…` cost "2 AP". `Davout, attack Mack at Swabia` → "(Trust him and he will fortify current position instead.)" → trust. `Soult, attack Mack as well` → "✗ Not enough actions! Need 1, have 0". No "actions unused" warning followed. The Insist arm does state this kind of price ("Insisting costs 2 actions — he must first go defensive", c02 t3).
- Expected: the Trust arm states its price.

**D4** t2 · keyed · P2 · The interrupt and the muster give different figures and opposite verdicts for the same corps.
- Evidence (c01 t2), the interrupt: "Odds unfavorable … Lannes 16,957, 35,833 with the muster committed, against Mack (42,190 men)". After `attack_anyway`: "MUSTER — Lannes (16,957; expect about 42,734 … up to 43,430 if all march) … the balance of force looks favorable".
- Expected: one figure and one verdict.

**D5** t2–12 · keyed · **P1** · Standing orders do not stand.
- Massena, under "hold the line" at Milan (c01 t2): "Massena hears cannon fire at Swabia but cannot answer it — Cannot move into Munich…". The Emperor's muster then took Massena and Teulie off Milan (c02 t3 forecast: `"will_join": ["Lannes","Murat","Massena","Teulie"]`). Milan, left bare, fell on t5, and the Kingdom of Italy with it.
- Lannes, under `Lannes, hold Swabia` ("hold this ground turn after turn", c02 t4): "Lannes hears cannon fire! Abandoning orders — rushing to Tyrol!" (c03 t5).
- Ney, under `march to Gascony and drive Paget out`: "Ney hears cannon fire! Abandoning orders — rushing to Swabia!" (c06 t12).
- Expected: a hold holds and a march is not dropped unasked, or the muster warns that it strips Milan.

**D6** t3 · keyed · P2 · The Trust arm named one army and attacked another.
- Evidence (c02 t3): `Massena, fortify Milan` — he was at Munich. The reply: "(Trust him and he will attack Mack at Tyrol instead.) Massena's hold at Milan is set aside." The battle: "Massena (lost 9127, own corps) vs Archduke Charles (lost 1659, own corps)". Next morning: "Napoleon's corps has been broken at Tyrol."
- Expected: "Massena is at Munich, not Milan", and a Trust arm that names the real defender and the odds.

**D7** t3–10 · keyed · P2 · An order naming a province the marshal is not in is carried out where he stands, without a word.
- `Massena, drill your men and rest them at Munich` → "drill exercises at Franconia" (c03 t6). `Ney, defend Swabia` → "Ney shifts to DEFENSIVE stance at Rhineland" (c05 t10). `Murat and Teulie, get to Milan and defend it` was parsed as defend `target Milan` while Murat stood at Munich (c03 t5).
- Expected: march there, or say he is elsewhere.

**D8** t3 · keyed · P2 · Misread: a reward read as a cavalry charge.
- Evidence: `reward Murat for his charge at Swabia` → "✗ Murat needs one victory first: a single battle won as the attacker arms the charge" (c02 t3). Meant: give Murat a rente or estate.

**D9** t10 · keyed · P2 · Misread: "drill your guard" became a standing HOLD.
- Evidence (c05 t10): `Napoleon, drill your guard` → "Napoleon will hold Munich. Holding position." The game had just advised: "A turn of drill … restores it."

**D10** t1–11 · keyed · P2 · Compound orders lose their second half.
- `dig in at Milan and hold the line` → a HOLD only, no fortify (c01 t1). `Davout, break camp and march on Franconia…` → "✗ … 'Davout, unfortify' first" (c03 t5), although the game's own word for unfortify is "breaks camp". `Lannes, unfortify and march on Bohemia` → "Lannes abandons fortified position…"; the march was dropped silently (c06 t11).
- Expected: both halves, or a word on the half not carried.

**D11** t15 keyed and t17 keyless · **P1** · Misread: "march home to Franche-Comte" marches elsewhere.
- `Lannes, march home to Franche-Comte` → "(Our maps read Lorraine as the province nearest your order, Sire.)" (c08 t15). On the morning of "must march today", `Massena, march home to Franche-Comte` → "begins march to Piedmont … (Our maps read Piedmont…)". Murat got the same (k01 t17). Next morning: "Massena and Murat are no nearer home". Franche-Comte is a real province.

**D12** t2–26 · keyed, recurs keyless · P3 · Raw roster keys appear in enemy-phase text.
- Evidence: "ArchdukeCharles halts before Milan's works…" (c01 t2); "Captured: KingdomOfItaly → Austria" (c03 t5); "ArchdukeJohn holds position at Munich…" (k02–k05).

**D13** t2–15 · keyed · P3 · Enemy narration is written in the first person, addressed to "Sire".
- Evidence: "Franche-Comte cannot be reached, Sire — it is France-held soil and we are at war; Mack falls back to Munich instead." (c01 t2); "The enemy's repeated assaults have leveled our defenses. We fight without cover." (Wellesley, c08 t15); "[DANGER] Morale critically low at 11%" on Mack's levy (c04 t8).

**D14** t1–19 · keyed · P3 · Copy slips.
- "the Emperor Napoleon stands at…" (lower-case start); "Under a standing move to order — Franche-Comte." (c08 t16); "Massena, Murat hold under your own orders" (missing "and"); "Milan is Kingdom of Italy's", "Kingdom of Italy is no longer ours" (missing "the"); "the Austria court", "the Russia court", "the Hesse court"; "under the peace with Austria." used for a truce.

**D15** t4 · keyed · P3 · A battle is reported with no outcome.
- Evidence (c02 t4): the whole battle line is "⚔ [Combat] Murat leads the charge! (Aggressive: +15% attack)". The result appears only in "ORDER Murat [breaks]: … Defeated by Archduke John".

**D16** t4, t16 · keyed · P3 · Asking Talleyrand about his mission returns a generic brief on the court.
- Evidence: `Talleyrand, how is the Prussian mission going?` → "…Relations stand at 13 … Hardenberg is bellicose…" (c02 t4). The ledger already shows "net +7 a turn · ≈13 turns". The same happened for Austria (c08 t16).
- Expected: the mission's own status.

**D17** t4, t9 · keyed · P3 · One battle is reported at two places.
- Evidence (c02 t4): "Massena's corps has been broken at Munich" beside "Massena was mauled at Tyrol" and "Napoleon's corps has been broken at Tyrol".

**D18** t1 · keyed · P3 · The objection prices the attack alone.
- Evidence (c01 t1): "The odds are not in our favor" while six corps stood next to Swabia. The next day the same attack, with the muster, read "favorable".

**D19** t1 · keyed · P3 · `how many action points do I have?` returns the rules, not the count. (`how many actions do I have left?` does give the count.)

**D20** t1 · keyed · P3 · `Ney, attack Mack if he is still standing` is refused as "a contingency, not an order", though Mack was standing.

**D21** t5–25 · keyed, recurs keyless · P3 · One-step marches finish at once but linger.
- Evidence (c04 t7): "Moves to Swabia." then "Davout is marching to Swabia (0 turns remaining)". The still-live order drew a cannon-fire question next turn that took him to Franconia. The same pattern for the Emperor, Lannes and Ney.

**D22** t6 · keyed · P2 · An objection that names no alternative: trusting it spends an order and leaves the marshal idle.
- Evidence: `Ney, support Davout` → "Give me a battle of my own." → trust. The turn ended with 1 of 4 orders unused (c03 t6). Next turn: "Marshal Ney awaits orders at Rhineland." The server log shows "Creating PURSUE order for Ney -> ArchdukeJohn".

**D23** t9 · keyed · P2 · Two surfaces disagree on the treasury the same morning.
- Evidence (c04 t9): "compensate (1,200g — the treasury holds -167)" beside "LEDGER treasury 1398".

**D24** t8 · keyed · P2 · `Ney, stop chasing John and hold where you are` is refused: "I could not make out a destination in that order".

**D25** t8 · keyed · P3 · `Lannes and Murat, scout Tyrol`: only Lannes scouts, and Murat is dropped without a word.

**D26** t7–10 · keyed · P3 · A raw code word appears in the answer, and the same question addressed to Talleyrand gets no estimate.
- Evidence: "A bare peace put to Britain today scores 30 — COUNTER_OFFER, Sire." (c05 t10). `Talleyrand, what would Austria accept for peace?` returned a generic brief (c04 t7).

**D27** t9 · keyed · P3 · Province names sit far from their real geography.
- Evidence (c05 t9): "Orleanais borders Ardennes, Brabant, … Flanders, Ile-de-France, … Picardy". Paris does not border Ile-de-France.

**D28** t13–15 · keyed · **P1** · The truce with Austria let Austria walk into the Bavarian provinces French corps stood in, and eliminate Bavaria.
- Evidence (c07): "ArchdukeJohn assaults the Munich garrison! … marches into Munich! … Captured: Bavaria → Austria". The next morning: "Soult and Lannes have been 5 turns over what Munich can feed". "ArchdukeCharles marches from Franconia into Swabia unopposed!" The next morning: "Ney, Davout, Lannes and Napoleon stand 55,374 men at Swabia" and "Sire — Bavaria has been eliminated from the war." Nothing in the armistice offer warned of this.

**D29** t14–19 · keyed · **P1** · Corps on French soil, the Emperor included, are threatened with internment, and the rules cannot be learned by asking.
- Evidence: "Massena and Murat are no nearer home … After that their corps will be interned where they stand" (c07 t15), while `who holds Milan?` → "Milan is ours, Sire." (c08 t15). The drill the game itself recommended "set aside" the march home with no warning. Then `Napoleon, march home…` → "✗ Napoleon is locked in drill exercises this turn" (c08 t15). "no turn to spare — they must march today" appeared two mornings running, then reset to "2 turns to spare". No internment ever happened. `why must Massena go home?`, `what does the truce with Austria mean?`, `how long does the truce with Austria last?` and `is Murat safe from internment?` all shrug.

**D30** t16 · keyed · P2 · The dispatch strands a marshal who has already arrived.
- Evidence (c08): "ORDER Ney [completed]: Ney arrives at Franche-Comte." The next morning: "Ney is on the wrong side of the frontier at Swabia … he has 4 turns of safe passage."

**D31** t13–14 · keyed · P2 · Losses to "enemy harassment" during the truce.
- Evidence (c07): "Davout moves from Munich to Swabia (398 lost to march, 469 to enemy harassment)"; Lannes lost 213 the same way. The only army nearby was Austria's, under the truce.

**D32** t14 · keyed · P2 · The levy reminder is false, and the famine line misdates a newcomer.
- Evidence (c07): "nobody has gone to collect them" on the morning after "Augereau recruits 10,000 infantry at Paris". The same morning: "Soult and Lannes have been 5 turns over what Munich can feed", but Soult had just arrived.

**D33** t12–13 · keyed · P3 · The famine toll shrinks as the count of turns grows.
- Evidence (c06): "2,760 men lost in 3 turns" → "4 turns of famine at Munich now. 2,655 men gone".

**D34** t7, t12 · keyed · P3 · Peace terms are "prepared", then refused at the confirm for a conflict the advisor never mentioned.
- Evidence: the Austria/Bavaria and Britain/Spain alliance paradoxes. "I have prepared terms…" was followed by "I cannot deliver this, Sire — Making peace with Britain while allied with Spain…" (c06 t12).

**D35** t15 · keyed · P3 · An enemy forced march bounces back and forth.
- Evidence (c08): "Paget drives a forced march — Piedmont → Lyonnais → Piedmont → Lyonnais (3 stages…)".

**D36** t6 · keyed · P3 · Losing a whole satellite kingdom ranks below a mauled corps.
- Evidence (c03): headline "Murat was mauled at Tyrol…"; the sub-beat "Kingdom of Italy is no longer ours. Conquered — the satellite is gone."

**D37** t17–21 · keyless · P2 · Common phrasings fail without the key.
- `Soult, take Lyonnais back from Paget`, `Napoleon, return to Paris` and `Ney, keep going to Provence` → "I cannot determine the order. Perhaps: '… attack Paget' or '… move to Paris'?" `Ney, take Provence back` → "cannot parse". Keyed, the model read "take Milan back" and "return to Paris" at 0.85 confidence (c04).

**D38** t25 · keyless · P2 · The second half of an order is dropped while the report says it was done.
- Evidence (k05): `Soult, march to Burgundy and then fortify` → "— executed as written. Soult arrives at Burgundy." Then `is Soult fortified?` → "No, Sire".

**D39** t23–27 · keyless · P2 · The sponsorship is paid off the books.
- `sponsor Sardinia` → "200 gold per turn for 10 turns" (k04 t23). `how much gold do we have?` lists every outgoing except Sardinia: "Net +1,760" (k05 t25). The treasury then grew 152–202 less than the Net each turn; before the sponsorship the gap was 3g. `what are we paying Sardinia?` shrugs.

**D40** t21–26 · keyless · P2 · The allegiance auction gives no way to bid.
- Rail: "every court with gold or standing now bids for the flip". `Talleyrand, bid for Sardinia` → "Sire, I await your instructions regarding Sardinia." (k03 t21). `sponsor Sardinia` instead paid Sardinia to pursue its claims against Austria, the court being courted. Sardinia stayed "she would join" at −38 to −41.

**D41** t22 · keyless · P2 · Asked for cavalry, paid for infantry.
- Evidence (k03): `Soult, recruit cavalry at Lyonnais` → "Marshal Soult commands infantry … Soult recruits 3,000 infantry … Cost: 302 gold". Expected: ask first, or name a cavalry marshal.

**D42** t21–27 · keyless · P2 · An ally keeps a liberated French home province, unannounced, and there is no way to ask for it back.
- The last word was "Provence lies in enemy hands. Britain holds it." (c06 t12). Then `who holds Provence?` → "Provence is held by Spain." (k03 t21, still true at t27). `Talleyrand, ask Spain to give back Provence` → "I await your instructions regarding Spain."

**D43** t19–20 · keyless · P2 · "The war with Britain is over" headlines a truce, and is repeated stale the next day.
- Evidence (k01 t19 morning): the headline says the war is over while the sub-beat reads "a truce … else the war resumes". The same headline returned on the t20 morning, including "Murat … was not moved", after the playtester had moved him.

**D44** t20–26 · keyless · P3 · "Davout's fortifications decay: 6% → 6%" (and "5% → 5%") appears every morning.

## Harness notes (the playtester's)
- The cannon-fire answer was fixed: the driver always answered "investigate", ignoring the script's `"interrupt": "continue"`. The Emperor turning back toward the guns twice is therefore the driver's choice, not a finding.
- The model was barely used: only 2 keyed commands reached it; everything else parsed offline.
- The playtester edited nothing in the repository.
