# Playtest digest — sr5a-staff-ulm

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `716b09a7294c` (dirty) · content `dcf75e5f3732` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 800.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1767, own corps) vs Mack (lost 16826) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archd…
  - ⚔ Archduke Charles (lost 2521) vs Bernadotte (lost 3071, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Naples open borders
- LEDGER treasury 1624 · net +1481 · threat 72 · provinces 28 · ceiling 32854 · army 174044 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2156 · blockade 250 · admiralty 90
- DISPATCH: Supply cost you 1,860 men, at Franconia and Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Naples: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 1,624.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,354; expect about 84,529 with the corps likely to arrive, up to 95,136 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 456, own corps) vs Mack (lost 22104) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (22,670) vs Mack (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — he will NOT make it from the mountains at Munich in time; order 'Ney, support Davout' and it rises to about 76%
  WILL NOT — Bernadotte: is pinned by enemies before his own front
  WILL NOT — Massena: has already marched this turn
  WILL NOT — Napoleon: has already marched this turn
  Mack does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.
  The band weighs more than the men: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 3164) vs Archduke John (lost 1657) — Not one corps reached Davout. Ney was expected; Davout fought the battle single-handed.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Murat. Casualties: Archdu…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,389 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1084) vs Bernadotte (lost 8033) — Where was Ney? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 1584) vs Deroy (lost 7799) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2128) vs Murat (lost 7085) — Murat stood alone, Sire. Ney and Soult never came.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 2821 · net +2149 · threat 78 · provinces 28 (+0) · ceiling 24479 · army 147314 · vassals Holland 94 · Kingdom of Italy 95 · Switzerland 90
  - NET income 2575 · trade 450 · admin 50 · tribute 937 · upkeep 1346 · charges 81 · contributions 65 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — alliance is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,937.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (15,568; expect about 70,250 with the corps likely to arrive, up to 81,697 if all march) vs Mack (11,144 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 400, own corps) vs Mack (lost 5255, own corps) — Davout and Massena's timely arrival aided Ney. Napoleon, however, was conspicuously absent.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (17,865) vs Mack (strength unknown) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 135) vs Mack (lost 4178) — Davout stood alone, Sire. Ney never came. And Mack was taken on that field — France holds him.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (166 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 642 gold (×3 at war) (×1.07 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 642g on this turn's orders
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franche-Comte where he stands! (1,113 lost to march) Captured: France → Austria · ArchdukeCharles struggles in a costly engagement. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Arch… · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination) · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles takes Franche-Comte where he stands! (1,113 lost to march) Captured: France → Austria
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 165) vs Bernadotte (lost 3022) — Not one corps reached Bernadotte. Ney was expected; Bernadotte fought the battle single-handed.
  - ⚔ Archduke Charles (lost 559) vs Napoleon (lost 3091) — Napoleon stood alone, Sire. Ney never came.
  - ⚔ Archduke Charles (lost 504) vs Deroy (lost 5617) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×4, stance_change×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 2738, own corps) vs Archduke Charles (lost 3591) — Lannes and Napoleon arrived to reinforce Murat, but Soult failed to reach the field in time.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 4052 · net +2314 · threat 91 · provinces 29 (+1) · ceiling 24000 · army 130624 · vassals Holland 90 · Kingdom of Italy 91 · Switzerland 84
  - NET income 2565 · trade 449 · admin 50 · tribute 937 · upkeep 1024 · charges 238 · requisitions 50 · occupation 104 · blockade 281 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 11
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 4,157.
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✗ Davout cannot fortify while engaged with enemy forces! Enemy present: Archduke John. Attack or retreat first.
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 6505 · net +2062 · threat 89 · provinces 29 (+0) · ceiling 23795 · army 128315 · vassals Holland 90 · Kingdom of Italy 91 · Switzerland 82
  - NET income 2567 · trade 524 · admin 50 · tribute 937 · upkeep 1008 · charges 536 · requisitions 50 · occupation 104 · blockade 328 · admiralty 90
- DISPATCH: Sire — Ney, Bernadotte, Massena and Napoleon stand 52,307 men at Tyrol, which feeds 30,000. 22,307 too many. 4,795 men lost in 2 turns. No depot may be laid at Tyrol — region stability too low (45/10…
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 6,632.
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (13,617; expect about 60,444 with the corps likely to arrive, up to 66,004 if all march) vs Archduke Charles (32,641 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1085, own corps) vs Archduke Charles (lost 3674) — Reinforcement from Lannes, Massena and Napoleon kept Ney standing, Sire — but neither side yielded the ground.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (120 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 8829 · net +2204 · threat 87 · provinces 29 (+0) · ceiling 32073 · army 118520 · vassals Holland 90 · Kingdom of Italy 91 · Switzerland 80
  - NET income 2687 · trade 549 · admin 50 · tribute 937 · upkeep 928 · charges 647 · requisitions 50 · occupation 60 · blockade 344 · admiralty 90
- DISPATCH: Sire — Napoleon's corps has been broken at Munich. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #9 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #11 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 5g a turn — 99g of income forfeited, 30g of occupation relieved, 74g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 8,829.
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Munich, just one region away.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Munich instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1548, own corps) vs Archduke Charles (lost 2038) — Reinforcements from Massena bolstered Lannes's position — though Ney, Soult, Murat and Bernadotte never arrived, Sire.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 900 gold (unstable region premium) (×3 at war). Morale: 94% -> 89%
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- SPENT 900g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #12 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 9984 · net +1868 · threat 85 · provinces 28 (-1) · ceiling 28075 · army 113457 · vassals Holland 88 · Kingdom of Italy 99 · Switzerland 86
  - NET income 2591 · trade 549 · admin 50 · tribute 787 · upkeep 872 · charges 823 · requisitions 50 · occupation 30 · blockade 344 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_we_threshold, diplomatic_dp_regen)

## Turn 7 — Late December 1805
- CMD `enact the Staff` → ✓ The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day…
  - POPUP clarification: The Council of State, The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day. 9,000 gold now, then 300 gold a turn; one more order each day from the next refill. The treasury holds 9,984 gold. Enact it? (yes / no) → 1 (first option: Enact the Grand Quartier Général)
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (11,613; expect about 37,368 with the corps likely to arrive, up to 40,190 if all march) vs Archduke Charles (26,929 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1091, own corps) vs Archduke Charles (lost 3027) — Reinforcements from Lannes, Massena and Napoleon bolstered Ney's position — though Soult never arrived, Sire.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (11,422) vs Archduke Charles (23,902 men) at Munich — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 6167) vs Archduke Charles (lost 614) — Not one corps reached Murat. Ney and Soult were expected; Murat fought the battle single-handed.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- SPENT 9000g on this turn's orders
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,543 troops in the…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - verbs: attack×2, unfortify×1
- ORDER Napoleon [retired]: Napoleon's question is overtaken, Sire — Napoleon has marched clear of Munich. He awaits new orders.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 2680 · net +2166 · threat 83 · provinces 28 (+0) · ceiling 18602 · army 101427 · vassals Holland 84 · Kingdom of Italy 96 · Switzerland 81
  - NET income 2593 · trade 549 · admin 50 · tribute 564 · upkeep 784 · charges 92 · requisitions 50 · occupation 30 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - TURN EVENTS 7
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 8 — Early January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Davout, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Davout can give chase.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Mi…
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Milan instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 905, own corps) vs Archduke Charles (lost 2331) — Massena and Napoleon reached the field beside Ney, Sire — it saved the line, no more.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Cannot move into Milan - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 6 actions, 1 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos launches a devastating assault! Castanos gains the advantage over Paget. Casualties: Castanos 692, Paget 1,803…
  - ⚔ Castanos (lost 692) vs Paget (lost 1803) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: move×4, unfortify×1, attack×1
- ORDER Napoleon [retired]: Napoleon's question is overtaken, Sire — Napoleon has marched clear of Milan. He awaits new orders.
- ORDER Ney [retired]: Ney's question is overtaken, Sire — Archduke Charles has drawn off out of sight. He awaits new orders.
- LEDGER treasury 4487 · net +1621 · threat 81 · provinces 28 (+0) · ceiling 13973 · army 97409 · vassals Holland 84 · Kingdom of Italy 97 · Switzerland 80
  - NET income 2612 · trade 549 · admin 50 · tribute 415 · upkeep 744 · charges 424 · contributions 138 · requisitions 50 · occupation 15 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — Paget has crossed into Berry. No French corps stands in his path.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: Spain rebuffs 5 courts (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 1…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, fortify×1
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
- LEDGER treasury 5357 · net +1594 · threat 79 · provinces 28 (+0) · ceiling 14517 · army 99345 · vassals Holland 84 · Kingdom of Italy 98 · Switzerland 79
  - NET income 2618 · trade 549 · admin 50 · tribute 418 · upkeep 768 · charges 584 · contributions 40 · requisitions 100 · occupation 15 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — Paget has crossed into Normandy. No French corps stands in his path.
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 14 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Tyrol to Franconia. Franconia falls to France! (was Austria) (87 lost to march)
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [completed]: Lannes arrives at Bohemia. Lannes: "Done — and I trust the next order has more fire in it."
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 6852 · net +1220 · threat 81 · provinces 30 (+2) · ceiling 13732 · army 98729 · vassals Holland 84 · Kingdom of Italy 99 · Switzerland 78
  - NET income 2714 · trade 549 · admin 50 · tribute 447 · upkeep 752 · charges 859 · contributions 40 · occupation 155 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — Franconia has fallen to our arms. The tricolor flies over it this morning.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 11 — Late February 1806
  - MAILBOX #11 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #15 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, attack Archduke John` → ✗ Cannot attack Archduke John — armistice with Austria (5 turns remaining).
- CMD `Lannes, attack Archduke John` → ✗ Cannot attack Archduke John — armistice with Austria (5 turns remaining).
- CMD `Murat, move to Franconia` → ✓ Murat moves from Lorraine to Franconia (82 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 8081 · net +991 · threat 79 · provinces 30 (+0) · ceiling 13574 · army 98220 · vassals Holland 84 · Kingdom of Italy 98 · Switzerland 77
  - NET income 2721 · trade 549 · admin 50 · tribute 449 · upkeep 752 · charges 1097 · contributions 40 · occupation 155 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Piedmont.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 10 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 12 — Early March 1806
  - MAILBOX #12 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #17 → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace #18 → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm #19 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier advises caution. 'Bohemia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Piedmont into Provence unopposed! (50 lost to march) Captured: France → Britain
  - 🏴 Britain: Wellesley marches from Piedmont into Provence unopposed! (50 lost to march) Captured: France → Britain
  - verbs: attack×1
- LEDGER treasury 9141 · net +846 · threat 77 · provinces 29 (-1) · ceiling 13748 · army 97800 · vassals Holland 84 · Kingdom of Italy 97 · Switzerland 76
  - NET income 2762 · trade 549 · admin 50 · tribute 449 · upkeep 744 · charges 1311 · contributions 80 · occupation 95 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_ai_proposal_refused: 9 approaches rebuffed, chiefly from Prussia (open borders agreement)

## Turn 13 — Late March 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ Cannot attack Archduke John — armistice with Austria (3 turns remaining).
- CMD `Davout, move to Franconia` → ✓ Davout moves from Bohemia to Franconia (175 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 9913 · net +605 · threat 75 · provinces 29 (+0) · ceiling 13150 · army 96532 · vassals Holland 84 · Kingdom of Italy 96 · Switzerland 75
  - NET income 2761 · trade 549 · admin 50 · tribute 449 · upkeep 744 · charges 1478 · contributions 153 · occupation 95 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — the enemy has stood on our ground 6 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +4 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
  - MAILBOX #13 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #20 → grant the petition
  - POPUP proposal_result: Bohemia is ceded to the Kingdom of Italy. Loyalty +4 (96 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. Our net rises by 3g a turn — 150g of income forfeited, 40g of occupation relieved, 113g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Tyrol and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10438 · net +625 · threat 73 · provinces 28 (-1) · ceiling 13726 · army 95462 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 74
  - NET income 2619 · trade 549 · admin 50 · tribute 787 · upkeep 728 · charges 1603 · contributions 260 · occupation 55 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — the enemy has stood on our ground 7 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, diplomatic_ai_ai_treaty)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 15 — Late April 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 99% -> 94%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Russia armistice losing · Switzerland client petition
- LEDGER treasury 10608 · net +621 · threat 71 · provinces 28 (+0) · ceiling 13821 · army 97412 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 73
  - NET income 2671 · trade 549 · admin 50 · tribute 787 · upkeep 744 · charges 1663 · contributions 260 · occupation 35 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — Britain and Spain have made peace without us.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 16 — Early May 1806
  - MAILBOX #14 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #15 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #21 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #22 → grant the petition
  - POPUP diplomatic_dialogue: Russia, armistice_losing #21 → accept
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (73 → 83); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #22 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia (81 lost to march)
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Bohemia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Ney. Casualties: ArchdukeChar…
  - ⚔ Archduke Charles (lost 568, own corps) vs Ney (lost 3177, own corps) — Bernadotte and Napoleon never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×1
- ORDER Ney [awaiting_response]: Ney is cornered at Bohemia with 4,851 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Bohemia with 4,851 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 10641 · net +303 · threat 69 · provinces 28 (+0) · ceiling 12133 · army 84700 · vassals Holland 82 · Kingdom of Italy 100 · Switzerland 81
  - NET income 2680 · trade 549 · admin 50 · tribute 449 · upkeep 648 · charges 1748 · contributions 260 · occupation 35 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — Lannes's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: 8 approaches from Russia and Prussia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 17 — Late May 1806
  - MAILBOX #16 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #24 → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace #25 → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm #26 → confirm
  - POPUP proposal_result: Talleyrand departs for the Britain court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✗ Lannes is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Bohemia where he stands! (236 lost to march — forward supply lines reduce losses) Captured: Kingd… · ArchdukeJohn delivers an effective strike. ArchdukeJohn gains the advantage over Bernadotte. Casualties: ArchdukeJohn's… · Schwarzenberg holds them at Tyrol while allies attack from Bohemia! (+1 coordination) · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Lannes. Casualties: Archd…
  - 🏴 Austria: ArchdukeCharles takes Bohemia where he stands! (236 lost to march — forward supply lines reduce losses) Captured: KingdomOfItaly → Austria
  - ⚔ Archduke John (lost 911, own corps) vs Bernadotte (lost 238, own corps) — Even the favorable ground could not save Bernadotte, Sire. Archduke John overcame the terrain.
  - ⚔ Schwarzenberg (lost 9, own corps) vs Napoleon (lost 366) — A skirmish, Sire. Napoleon's men traded shots with Schwarzenberg; there was no battle to speak of.
  - ⚔ Archduke Charles (lost 1673) vs Lannes (lost 681, own corps) — The toll on Lannes's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franconia with 4,744 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Tyrol — 516 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franconia with 4,744 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Tyrol — 516 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 1 · Britain peace
- LEDGER treasury 10509 · net +197 · threat 67 · provinces 28 (+0) · ceiling 11451 · army 71456 · vassals Holland 76 · Kingdom of Italy 96 · Switzerland 75
  - NET income 2669 · trade 549 · admin 50 · tribute 337 · upkeep 552 · charges 1769 · contributions 318 · occupation 35 · blockade 344 · admiralty 90 · laws 300
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Britain with a response.
  - TURN EVENTS 9
- DIPLO +4 medium/low (diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
  - MAILBOX #17 Britain counter_offer_response: Britain — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Britain, peace #27 → accept
  - POPUP proposal_result: You have accepted Britain's counter-proposal. Treaty signed: At War → Peace with Britain. → display-only
  - RATIFIED Britain · PEACE · stalemate
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 510 gold (×3 at war) (Davout's intendance: -15%). Morale: 56% -> 53%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- SPENT 510g on this turn's orders
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn takes Tyrol where he stands! (173 lost to march — forward supply lines reduce losses) Captured: KingdomOfI…
  - 🏴 Austria: ArchdukeJohn takes Tyrol where he stands! (173 lost to march — forward supply lines reduce losses) Captured: KingdomOfItaly → Austria
  - verbs: retreat×1, attack×1, fortify×1, stance_change×1, move×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 9788 · net +1249 · threat 56 · provinces 28 (+0) · ceiling 16803 · army 73833 · vassals Holland 72 · Switzerland 73
  - NET income 2676 · trade 573 · admin 50 · tribute 337 · upkeep 576 · charges 1386 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL peace_ratified: Peace ratified between France and Britain.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 6
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +6 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, blockade_broken ×2, agenda_shift)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Britain and Sardinia (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.

## Turn 19 — Late June 1806
  - MAILBOX #18 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #28 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (72 → 76); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 5 actions unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, fortify×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 10723 · net +769 · threat 55 · provinces 28 (+0) · ceiling 15039 · army 73223 · vassals Holland 73 · Switzerland 71
  - NET income 2683 · trade 573 · admin 50 · upkeep 560 · charges 1552 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: The Emperor is a prisoner of Austria. THE EAGLE IN CHAINS: 2 of 10 — the regency falls at the end of turn 27 (8 turns remain) unless he is freed: accept Austria's terms — any peace with Austria frees…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 20 — Early July 1806
  - MAILBOX #19 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #29 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · stalemate
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 11099 · net +1713 · threat 27 · provinces 28 (+0) · ceiling 40424 · army 87325 · vassals Holland 70 · Switzerland 69
  - NET income 2690 · trade 585 · admin 50 · upkeep 656 · charges 531 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — peace with Austria is signed. Terms on both sides; the war ends in a stalemate.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - TURN EVENTS 5
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +5 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen)
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 55 to 27.

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 11793 · net +1621 · threat 27 · provinces 28 (+0) · ceiling 38103 · army 89446 · vassals Holland 67 · Switzerland 67
  - NET income 2694 · trade 585 · admin 50 · upkeep 680 · charges 603 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the establishment stands 40,554 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 450 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 13426 · net +1496 · threat 27 · provinces 28 (+0) · ceiling 36506 · army 88584 · vassals Holland 64 · Switzerland 65
  - NET income 2698 · trade 585 · admin 50 · upkeep 672 · charges 740 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 41,416 men at Paris, and nobody has gone to collect them.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Paris. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 14934 · net +1594 · threat 27 · provinces 28 (+0) · ceiling 38367 · army 87740 · vassals Holland 61 · Switzerland 63
  - NET income 2702 · trade 585 · admin 50 · tribute 225 · upkeep 664 · charges 879 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 4 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- SPENT 600g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, unfortify×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 15924 · net +1462 · threat 27 · provinces 28 (+0) · ceiling 36452 · army 89913 · vassals Holland 58 · Switzerland 61
  - NET income 2706 · trade 585 · admin 50 · tribute 225 · upkeep 688 · charges 991 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 5 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
  - MAILBOX #20 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #30 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (61 → 65); bond 40 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 17165 · net +1104 · threat 27 · provinces 28 (+0) · ceiling 32000 · army 89104 · vassals Holland 55 · Switzerland 63
  - NET income 2710 · trade 585 · admin 50 · upkeep 688 · charges 1128 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 6 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 5 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 18277 · net +1314 · threat 27 · provinces 28 (+0) · ceiling 35208 · army 88310 · vassals Holland 52 · Switzerland 61
  - NET income 2710 · trade 585 · admin 50 · tribute 337 · upkeep 680 · charges 1263 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 7 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Canno…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 10,000 infantry at Paris - Cost: 450 gold (capital discount) (×3 at war). Morale: 60% -> 46%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 450g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, unfortify×1
- LEDGER treasury 19071 · net +1118 · threat 26 · provinces 28 (+0) · ceiling 32903 · army 97334 · vassals Holland 43 · Switzerland 59
  - NET income 2710 · trade 585 · admin 50 · tribute 337 · upkeep 760 · charges 1379 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 8 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 20205 · net +984 · threat 25 · provinces 28 (+0) · ceiling 31916 · army 96374 · vassals Holland 34 · Switzerland 57
  - NET income 2710 · trade 585 · admin 50 · tribute 337 · upkeep 744 · charges 1529 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 9 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Paris. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1, recruit×1
- LEDGER treasury 21205 · net +855 · threat 23 · provinces 28 (+0) · ceiling 31002 · army 95435 · vassals Holland 25 · Switzerland 55
  - NET income 2710 · trade 585 · admin 50 · tribute 337 · upkeep 728 · charges 1674 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 10 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 510 gold (×3 at war) (Davout's intendance: -15%). Morale: 73% -> 66%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- SPENT 510g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, unfortify×1, recruit×1
- ENVOYS WAITING 1 · Austria ultimatum demand
- LEDGER treasury 21545 · net +739 · threat 21 · provinces 28 (+0) · ceiling 29710 · army 97455 · vassals Holland 16 · Switzerland 53
  - NET income 2710 · trade 585 · admin 50 · tribute 337 · upkeep 752 · charges 1766 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 11 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 31 — Late December 1806
  - MAILBOX #21 Austria incoming_ultimatum: Austria — Ultimatum → activated
  - POPUP diplomatic_dialogue: Austria, ultimatum_demand #31 → defy
  - POPUP proposal_result: You have defied Austria's ultimatum. Their court will not forget it — expect their weight behind the next coalition. → display-only
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 22308 · net +629 · threat 21 · provinces 28 (+0) · ceiling 29019 · army 96493 · vassals Holland 7 · Switzerland 45
  - NET income 2710 · trade 585 · admin 50 · tribute 337 · upkeep 728 · charges 1900 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 12 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Holland is on the verge of rebellion!
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: Holland #32 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Holland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1, recruit×1
- LEDGER treasury 22616 · net +438 · threat 11 · provinces 28 (+0) · ceiling 27134 · army 95551 · vassals Switzerland 37
  - NET income 2710 · trade 585 · admin 50 · tribute 225 · upkeep 712 · charges 1995 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — Holland is no longer ours. Russia is their protector now.
  - RAIL diplomatic_vassal_transferred: Holland passes from France's suzerainty to Russia's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Russia's gold turns Holland against France.
  - TURN EVENTS 5
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Canno…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, unfortify×1
- LEDGER treasury 22070 · net +402 · threat 11 · provinces 28 (+0) · ceiling 26090 · army 97629 · vassals Switzerland 29
  - NET income 2710 · trade 585 · admin 50 · tribute 225 · upkeep 736 · charges 2007 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 14 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franconia. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 22422 · net +252 · threat 11 · provinces 28 (+0) · ceiling 24858 · army 96724 · vassals Switzerland 21
  - NET income 2710 · trade 535 · admin 50 · tribute 225 · upkeep 736 · charges 2107 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 15 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Paris. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 22682 · net +167 · threat 11 · provinces 28 (+0) · ceiling 24246 · army 95839 · vassals Switzerland 13
  - NET income 2710 · trade 535 · admin 50 · tribute 225 · upkeep 728 · charges 2200 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 16 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 36 — Early March 1807
  - MAILBOX #22 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #33 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, unfortify×1
- LEDGER treasury 24243 · net +1730 · threat 11 · provinces 28 (+0) · ceiling 78281 · army 97970 · vassals Switzerland 5
  - NET income 2710 · trade 535 · admin 50 · tribute 225 · upkeep 744 · charges 711 · occupation 35 · laws 300
- DISPATCH: Sire — a truce with Russia is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - TURN EVENTS 5
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — service to the strong is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +2 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
  - POPUP vassal_rebellion_imminent: Switzerland #34 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Switzerland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 25150 · net +783 · threat 1 · provinces 28 (+0) · ceiling 38541 · army 97118 · vassals none
  - NET income 2710 · trade 535 · admin 50 · upkeep 736 · charges 1351 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as an ultimatum.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 25933 · net +660 · threat 0 · provinces 28 (+0) · ceiling 36642 · army 96286 · vassals none
  - NET income 2710 · trade 535 · admin 50 · upkeep 736 · charges 1474 · occupation 35 · admiralty 90 · laws 300
- DISPATCH: Sire — the levy has stood open 19 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 10,000 infantry at Paris - Cost: 450 gold (capital discount) (×3 at war). Morale: 66% -> 53%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 450g on this turn's orders
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos assaults the Bern garrison! Garrison collapses (7,743 -> 0). Castanos loses 2,688 troops in the assault. Casta…
  - 🏴 Spain: [Materiel] Guns, horses and stores lost with the fallen: Spain -134g, Switzerland -161g. Captured: Switzerland → Spain
  - verbs: fortify×1, unfortify×1, attack×1, wait×1
- LEDGER treasury 26871 · net +1369 · threat 0 · provinces 28 (+0) · ceiling 69625 · army 105268 · vassals none
  - NET income 2710 · trade 547 · admin 50 · upkeep 808 · charges 795 · occupation 35 · laws 300
- DISPATCH: Sire — Switzerland is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Switzerland has been eliminated from the war.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — service to the strong is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franconia (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, fortify×1
- LEDGER treasury 28260 · net +1344 · threat 0 · provinces 28 (+0) · ceiling 70250 · army 104272 · vassals none
  - NET income 2710 · trade 559 · admin 50 · upkeep 800 · charges 840 · occupation 35 · laws 300
- DISPATCH: Sire — the levy has stood open 21 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_armistice_expired_peace: The armistice between France and Russia has concluded. Peace declared.
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as an ultimatum.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG nation_eliminated: Switzerland has been eliminated from the war.

---
finished: **completed** · commands 220 · popups 71 · battles 23
