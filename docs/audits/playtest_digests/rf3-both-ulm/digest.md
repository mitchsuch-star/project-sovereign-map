# Playtest digest — rf3-both-ulm

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `3d1157842721` (dirty) · content `c696461ccc07` · driver `aef52ad7cbfd`
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
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl…
  - ⚔ Archduke Charles (lost 2053) vs Bernadotte (lost 5685) — Bernadotte stood alone, Sire. Ney never came.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Naples open borders
- LEDGER treasury 2463 · net +2233 · threat 72 · provinces 28 · ceiling 54152 · army 175239 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 3400 · trade 400 · admin 50 · tribute 937 · upkeep 2194 · charges 20 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 5,685 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Naples: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,463.
- CMD `enact the Anticipated Class` → ✓ The Anticipated Class is in force — enacted for 15 authority. It costs 150 gold a turn from now on. Authority 100 → 85.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (21,161; expect about 88,309 with the corps likely to arrive, up to 98,912 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 500, own corps) vs Mack (lost 25069) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (22,709) vs Mack (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — he will NOT make it from the mountains at Munich in time; order 'Ney, support Davout' and it rises to about 76%
  WILL NOT — Bernadotte: is pinned by enemies before his own front
  WILL NOT — Massena: has already marched this turn
  WILL NOT — Napoleon: has already marched this turn
  Mack does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.
  The band weighs more than the men: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 3164) vs Archduke John (lost 1660) — Not one corps reached Davout. Ney was expected; Davout fought the battle single-handed.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archd… · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharle… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - 🏴 Austria: Casualties: ArchdukeCharles's army 738, Bernadotte 6,795. Both armies remain in the field. Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,421 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 539, own corps) vs Bernadotte (lost 6795) — Where was Ney? Bernadotte held the field alone — reinforcement never came. And Bernadotte was taken on that field — Aus…
  - ⚔ Archduke Charles (lost 1550) vs Deroy (lost 8518) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2289) vs Murat (lost 6118) — Murat stood alone, Sire. Ney and Soult never came.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 4424 · net +2677 · threat 78 · provinces 28 (+0) · ceiling 33521 · army 146487 · vassals Holland 94 · Kingdom of Italy 95 · Switzerland 90
  - NET income 3382 · trade 450 · admin 50 · tribute 937 · upkeep 1316 · charges 223 · contributions 82 · blockade 281 · admiralty 90 · laws 150
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- COURTS: The court of Prussia eases over The Hanoverian Prize — alliance is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 4,540.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✓ The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 85 → 70.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,983; expect about 73,801 with the corps likely to arrive, up to 83,630 if all march) vs Mack (8,179 men) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 70, own corps) vs Mack (lost 7338) — Davout and Massena's timely arrival aided Ney. Napoleon, however, was conspicuously absent.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (18,305; expect about 25,822 with the corps likely to arrive, up to 47,399 if all march) vs Mack (837 men) at Franconia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1651, own corps) vs Archduke John (lost 2271) — Reinforcements from Napoleon bolstered Davout's position — though Ney never arrived, Sire.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (166 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 636 gold (×3 at war) (×1.06 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 636g on this turn's orders
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a devastating assault! ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCha… · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Napoleon. Casualties: ArchdukeCha… · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination)
  - 🏴 Austria: Casualties: ArchdukeCharles 1,670, Murat's army 8,609. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - ⚔ Archduke Charles (lost 1670) vs Murat (lost 4196, own corps) — Lannes arrived to reinforce Murat, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 1928) vs Napoleon (lost 1031, own corps) — Ney marched to Napoleon's guns as ordered. It was not enough.
  - ⚔ Archduke Charles (lost 533) vs Deroy (lost 5821) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, wait×2
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 6050 · net +2570 · threat 83 · provinces 29 (+1) · ceiling 26184 · army 129988 · vassals Holland 92 · Kingdom of Italy 93 · Switzerland 86
  - NET income 3355 · trade 525 · admin 50 · tribute 937 · upkeep 1008 · charges 516 · occupation 104 · blockade 329 · admiralty 90 · laws 250
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 11
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 6,155.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (15,328; expect about 23,906 with the corps likely to arrive, up to 26,545 if all march) vs Mack (837 men) at Franconia — the balance of force looks favorab…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 524, own corps) vs Mack (lost 282, own corps) — Reinforcements from Davout bolstered Ney's position — though Massena never arrived, Sire. And Mack was taken on that fi…
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn,…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Napoleon. Casualties: ArchdukeCha… · ArchdukeCharles marches from Munich into Tyrol unopposed! (2,031 lost to march) Captured: France → Austria
  - 🏴 Austria: [!] Napoleon's troops are BROKEN (morale 0%)! FORCED RETREAT! Munich has been captured by Austria!
  - 🏴 Austria: ArchdukeCharles marches from Munich into Tyrol unopposed! (2,031 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 562) vs Napoleon (lost 3496) — Napoleon held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×2, stance_change×1, fortify×1
  - ⚡ AUTONOMOUS: [!] Archduke John is EXPOSED! (Just retreated, no ally to cover)
  - ⚔ Massena (lost 190, own corps) vs Archduke John (lost 5755) — Ney arrived to reinforce Massena! The timely arrival swung the battle in our favor, Sire.
  - POPUP capture_choice[capture]: Bohemia, Massena → secure
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 8485 · net +2149 · threat 91 · provinces 30 (+1) · ceiling 24470 · army 121929 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 85
  - NET income 3351 · trade 524 · admin 50 · tribute 937 · upkeep 952 · charges 871 · occupation 222 · blockade 328 · admiralty 90 · laws 250
- DISPATCH: Sire — Napoleon's corps has been broken at Munich. He must reform before he fights again.
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 8,612.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (14,581) vs Archduke Charles (31,794 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1653, own corps) vs Archduke Charles (lost 932) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (950 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (110 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10629 · net +1972 · threat 89 · provinces 30 (+0) · ceiling 24436 · army 112486 · vassals Holland 92 · Kingdom of Italy 93 · Switzerland 82
  - NET income 3400 · trade 549 · admin 50 · tribute 937 · upkeep 856 · charges 1232 · occupation 192 · blockade 344 · admiralty 90 · laws 250
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 6 — Early December 1805
  - MAILBOX #9 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✓ The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- SPENT 9000g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 4456 · net +2494 · threat 87 · provinces 30 (+0) · ceiling 21534 · army 110712 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 92
  - NET income 3513 · trade 549 · admin 50 · tribute 712 · upkeep 848 · charges 358 · occupation 140 · blockade 344 · admiralty 90 · laws 550
- DISPATCH: Ney's army is recovering. Effectiveness penalty: -15%.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 7 — Late December 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Franconia to Bohemia (145 lost to march)
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (10,937; expect about 14,931 with the corps likely to arrive, up to 16,172 if all march) vs Archduke Charles (30,836 men) at Tyrol — the balance of force …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 3618, own corps) vs Archduke Charles (lost 632) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Tyrol into Bohemia unopposed! (906 lost to march) Captured: France → Austria · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Ney. Casualties: ArchdukeChar… · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles marches from Tyrol into Bohemia unopposed! (906 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 248, own corps) vs Ney (lost 6381, own corps) — Ney fought without Soult's support. The roads, or the will, proved insufficient.
  - ⚔ Archduke John (lost 485, own corps) vs Massena (lost 7989, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
  - verbs: attack×3, unfortify×2, move×1
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Franconia — 432 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Franconia — 432 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 5989 · net +2272 · threat 85 · provinces 29 (-1) · ceiling 19254 · army 84293 · vassals Holland 88 · Kingdom of Italy 89 · Switzerland 86
  - NET income 3409 · trade 549 · admin 50 · tribute 712 · upkeep 656 · charges 682 · contributions 26 · occupation 100 · blockade 344 · admiralty 90 · laws 550
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - TURN EVENTS 8
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 8 — Early January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Davout, attack Archduke Charles` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! ArchdukeCharles is at Franconia, just one region away.
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 2). Moved to Munich. Route: Munich -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles faces a difficult fight. ArchdukeCharles gains the advantage over Davout. Casualties: ArchdukeCharles's… · ArchdukeJohn attacks with overwhelming force. ArchdukeJohn gains the advantage over Ney. Casualties: ArchdukeJohn's arm…
  - 🏴 Austria: Casualties: ArchdukeCharles's army 303, Davout 3,069. Both armies remain in the field. Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 201, own corps) vs Davout (lost 3069) — Davout stood alone, Sire. Soult never came.
  - ⚔ Archduke John (lost 575, own corps) vs Ney (lost 599, own corps) — Ney's army has been badly mauled. Archduke John proved the stronger force today.
  - verbs: attack×2, retreat×2, stance_change×2
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
- ORDER Ney [awaiting_response]: Ney is cornered at Swabia with 4,980 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Swabia with 4,980 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
  - POPUP diplomatic_dialogue: Holland, client_petition #14 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (83 → 87); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 8148 · net +1746 · threat 83 · provinces 28 (-1) · ceiling 17801 · army 71282 · vassals Holland 87 · Kingdom of Italy 84 · Switzerland 80
  - NET income 3374 · trade 549 · admin 50 · tribute 375 · upkeep 552 · charges 1111 · requisitions 75 · occupation 30 · blockade 344 · admiralty 90 · laws 550
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 9 — Late January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 1…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 5 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [completed]: Massena arrives at Milan. Massena: "It is done. Point me at something that shoots back, Sire."
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 8908 · net +1489 · threat 81 · provinces 28 (+0) · ceiling 17000 · army 74083 · vassals Holland 87 · Kingdom of Italy 85 · Switzerland 78
  - NET income 3376 · trade 549 · admin 50 · tribute 375 · upkeep 576 · charges 1271 · occupation 30 · blockade 344 · admiralty 90 · laws 550
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 14 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 4 courts (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #11 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #15 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · stalemate
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 537, Paget … · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Castanos (lost 537) vs Paget (lost 1515) — Paget's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Castanos (lost 253) vs Paget (lost 1137) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better. And …
  - verbs: attack×2, fortify×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Britain + Russia (4 pairs resolved). → display-only
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #17 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +4 (84 → 88); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 2 · Britain settlement offer · KingdomOfItaly client petition
- LEDGER treasury 9906 · net +2551 · threat 80 · provinces 28 (+0) · ceiling 89593 · army 88783 · vassals Holland 87 · Kingdom of Italy 88 · Switzerland 76
  - NET income 3405 · trade 585 · admin 50 · upkeep 672 · charges 252 · occupation 15 · laws 550
- DISPATCH: Sire — peace with Austria is signed. Terms on both sides; the war ends in a stalemate.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +4 medium/low (status_quo_titled, diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 80 to 40.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG ai_ai_proposal_refused: Spain rebuffs 5 courts (open borders agreement)

## Turn 11 — Late February 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke John` → ✗ Ney is recovering from retreat (2 turns remaining) and cannot accept strategic orders.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12460 · net +2472 · threat 40 · provinces 28 (+0) · ceiling 89687 · army 88489 · vassals Holland 85 · Kingdom of Italy 88 · Switzerland 74
  - NET income 3408 · trade 585 · admin 50 · upkeep 672 · charges 334 · occupation 15 · laws 550
- DISPATCH: Sire — the establishment stands 41,511 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - RAIL settlement_summary: Settlement of France + Spain + Holland vs Britain + Russia: settlement ratified.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +5 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: Spain rebuffs Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 15% -> 20%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 14692 · net +2379 · threat 40 · provinces 28 (+0) · ceiling 89031 · army 91201 · vassals Holland 83 · Kingdom of Italy 88 · Switzerland 72
  - NET income 3411 · trade 585 · admin 50 · upkeep 696 · charges 406 · occupation 15 · laws 550
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 38,799 men at Paris, and nobody has gone to collect them.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 13 — Late March 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 5 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17074 · net +2531 · threat 40 · provinces 28 (+0) · ceiling 96156 · army 90919 · vassals Holland 81 · Kingdom of Italy 88 · Switzerland 70
  - NET income 3414 · trade 585 · admin 50 · tribute 225 · upkeep 696 · charges 482 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 4 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 14 — Early April 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 19608 · net +2453 · threat 40 · provinces 28 (+0) · ceiling 96250 · army 90643 · vassals Holland 79 · Kingdom of Italy 88 · Switzerland 68
  - NET income 3417 · trade 585 · admin 50 · tribute 225 · upkeep 696 · charges 563 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 5 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 15 — Late April 1806
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #19 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (68 → 72); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 67% -> 64%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21596 · net +2143 · threat 40 · provinces 28 (+0) · ceiling 88562 · army 93373 · vassals Holland 77 · Kingdom of Italy 88 · Switzerland 71
  - NET income 3420 · trade 585 · admin 50 · upkeep 720 · charges 627 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 6 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 2 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23742 · net +2415 · threat 40 · provinces 28 (+0) · ceiling 99187 · army 93109 · vassals Holland 75 · Kingdom of Italy 88 · Switzerland 70
  - NET income 3423 · trade 585 · admin 50 · tribute 337 · upkeep 720 · charges 695 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 7 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Primacy in Germany — service to the strong is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 2 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 26160 · net +2340 · threat 40 · provinces 28 (+0) · ceiling 99281 · army 92851 · vassals Holland 73 · Kingdom of Italy 88 · Switzerland 69
  - NET income 3426 · trade 585 · admin 50 · tribute 337 · upkeep 720 · charges 773 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 8 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 18 — Early June 1806
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (73 → 77); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 10% -> 19%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- SPENT 170g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 27953 · net +2300 · threat 40 · provinces 28 (+0) · ceiling 99812 · army 95596 · vassals Holland 76 · Kingdom of Italy 88 · Switzerland 68
  - NET income 3429 · trade 585 · admin 50 · tribute 375 · upkeep 744 · charges 830 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 9 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 30256 · net +2229 · threat 39 · provinces 28 (+0) · ceiling 99906 · army 95347 · vassals Holland 75 · Kingdom of Italy 88 · Switzerland 67
  - NET income 3432 · trade 585 · admin 50 · tribute 375 · upkeep 744 · charges 904 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 10 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 32488 · net +2161 · threat 37 · provinces 28 (+0) · ceiling 100000 · army 95104 · vassals Holland 74 · Kingdom of Italy 88 · Switzerland 66
  - NET income 3435 · trade 585 · admin 50 · tribute 375 · upkeep 744 · charges 975 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 11 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 34293 · net +2106 · threat 35 · provinces 28 (+0) · ceiling 100093 · army 97864 · vassals Holland 73 · Kingdom of Italy 88 · Switzerland 65
  - NET income 3438 · trade 585 · admin 50 · tribute 375 · upkeep 744 · charges 1033 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 12 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 36402 · net +2267 · threat 33 · provinces 28 (+0) · ceiling 107218 · army 97630 · vassals Holland 72 · Kingdom of Italy 88 · Switzerland 64
  - NET income 3441 · trade 585 · admin 50 · tribute 600 · upkeep 744 · charges 1100 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 13 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 38672 · net +2197 · threat 31 · provinces 28 (+0) · ceiling 107312 · army 97402 · vassals Holland 71 · Kingdom of Italy 88 · Switzerland 63
  - NET income 3444 · trade 585 · admin 50 · tribute 600 · upkeep 744 · charges 1173 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 14 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
  - MAILBOX #16 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (63 → 67); bond 40 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 74% -> 70%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 40404 · net +1896 · threat 29 · provinces 28 (+0) · ceiling 99625 · army 100177 · vassals Holland 70 · Kingdom of Italy 88 · Switzerland 66
  - NET income 3447 · trade 585 · admin 50 · tribute 375 · upkeep 768 · charges 1228 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 15 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 42303 · net +2175 · threat 27 · provinces 28 (+0) · ceiling 110250 · army 99958 · vassals Holland 69 · Kingdom of Italy 88 · Switzerland 65
  - NET income 3450 · trade 585 · admin 50 · tribute 712 · upkeep 768 · charges 1289 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 16 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 5 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 44478 · net +2105 · threat 25 · provinces 28 (+0) · ceiling 110250 · army 99742 · vassals Holland 68 · Kingdom of Italy 88 · Switzerland 64
  - NET income 3450 · trade 585 · admin 50 · tribute 712 · upkeep 768 · charges 1359 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 17 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
  - MAILBOX #17 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (68 → 72); bond 40 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 40% -> 40%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 46004 · net +1695 · threat 23 · provinces 28 (+0) · ceiling 98968 · army 102529 · vassals Holland 71 · Kingdom of Italy 88 · Switzerland 63
  - NET income 3450 · trade 585 · admin 50 · tribute 375 · upkeep 792 · charges 1408 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 18 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 47699 · net +1641 · threat 21 · provinces 28 (+0) · ceiling 98968 · army 102322 · vassals Holland 70 · Kingdom of Italy 88 · Switzerland 62
  - NET income 3450 · trade 585 · admin 50 · tribute 375 · upkeep 792 · charges 1462 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 19 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 49340 · net +1589 · threat 19 · provinces 28 (+0) · ceiling 98968 · army 102118 · vassals Holland 69 · Kingdom of Italy 88 · Switzerland 61
  - NET income 3450 · trade 585 · admin 50 · tribute 375 · upkeep 792 · charges 1514 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 20 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 39% -> 39%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- SPENT 170g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 50715 · net +1521 · threat 17 · provinces 28 (+0) · ceiling 98218 · army 104920 · vassals Holland 68 · Kingdom of Italy 88 · Switzerland 53
  - NET income 3450 · trade 585 · admin 50 · tribute 375 · upkeep 816 · charges 1558 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 21 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 52236 · net +1697 · threat 15 · provinces 28 (+0) · ceiling 105250 · army 104725 · vassals Holland 67 · Kingdom of Italy 88 · Switzerland 45
  - NET income 3450 · trade 585 · admin 50 · tribute 600 · upkeep 816 · charges 1607 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 22 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 53933 · net +1643 · threat 13 · provinces 28 (+0) · ceiling 105250 · army 104533 · vassals Holland 66 · Kingdom of Italy 88 · Switzerland 37
  - NET income 3450 · trade 585 · admin 50 · tribute 600 · upkeep 816 · charges 1661 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 23 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 55193 · net +1578 · threat 11 · provinces 28 (+0) · ceiling 104500 · army 107344 · vassals Holland 65 · Kingdom of Italy 88 · Switzerland 29
  - NET income 3450 · trade 585 · admin 50 · tribute 600 · upkeep 840 · charges 1702 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 24 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 56721 · net +1816 · threat 9 · provinces 28 (+0) · ceiling 113468 · army 107161 · vassals Holland 64 · Kingdom of Italy 88 · Switzerland 21
  - NET income 3450 · trade 535 · admin 50 · tribute 937 · upkeep 840 · charges 1751 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 25 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 58561 · net +1782 · threat 7 · provinces 28 (+0) · ceiling 114218 · army 106981 · vassals Holland 63 · Kingdom of Italy 88 · Switzerland 13
  - NET income 3450 · trade 535 · admin 50 · tribute 937 · upkeep 816 · charges 1809 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 26 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 36 — Early March 1807
  - MAILBOX #18 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #23 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (63 → 67); bond 40 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 90% -> 85%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 59763 · net +1382 · threat 5 · provinces 28 (+0) · ceiling 102937 · army 109804 · vassals Holland 66 · Kingdom of Italy 88 · Switzerland 5
  - NET income 3450 · trade 535 · admin 50 · tribute 600 · upkeep 840 · charges 1848 · occupation 15 · laws 550
- DISPATCH: Sire — the levy has stood open 27 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
  - POPUP vassal_rebellion_imminent: Switzerland #24 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Switzerland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 59490 · net -258 · threat 0 · provinces 28 (+0) · ceiling 54807 · army 109630 · vassals Holland 55 · Kingdom of Italy 78
  - NET income 3450 · trade 535 · admin 50 · tribute 375 · upkeep 840 · charges 3173 · occupation 15 · admiralty 90 · laws 550
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as an ultimatum.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 59048 · net -416 · threat 0 · provinces 28 (+0) · ceiling 51914 · army 109462 · vassals Holland 49 · Kingdom of Italy 80
  - NET income 3450 · trade 535 · admin 50 · tribute 375 · upkeep 840 · charges 3331 · occupation 15 · admiralty 90 · laws 550
- DISPATCH: Sire — the levy has stood open 29 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 60% -> 57%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 57837 · net -548 · threat 0 · provinces 28 (+0) · ceiling 48931 · army 112297 · vassals Holland 43 · Kingdom of Italy 82
  - NET income 3450 · trade 535 · admin 50 · tribute 375 · upkeep 864 · charges 3439 · occupation 15 · admiralty 90 · laws 550
- DISPATCH: Sire — the levy has stood open 30 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland settlement offer
- LEDGER treasury 57110 · net -680 · threat 0 · provinces 28 (+0) · ceiling 46614 · army 112135 · vassals Holland 37 · Kingdom of Italy 84
  - NET income 3450 · trade 535 · admin 50 · tribute 375 · upkeep 864 · charges 3571 · occupation 15 · admiralty 90 · laws 550
- DISPATCH: Sire — the levy has stood open 31 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

---
finished: **completed** · commands 239 · popups 51 · battles 23
