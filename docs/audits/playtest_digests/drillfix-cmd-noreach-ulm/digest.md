# Playtest digest — drillfix-cmd-noreach-ulm

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `3d1157842721` (dirty) · content `4346446e7d78` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1767, own corps) vs Mack (lost 16826) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's attack meets fierce resistance. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Arch…
  - ⚔ Archduke Charles (lost 2236) vs Bernadotte (lost 2934, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Naples open borders
- LEDGER treasury 2450 · net +2272 · threat 72 · provinces 28 · ceiling 54068 · army 174346 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 3400 · trade 400 · admin 50 · tribute 937 · upkeep 2156 · charges 19 · blockade 250 · admiralty 90
- DISPATCH: Supply cost you 1,871 men, at Franconia and Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Naples: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,524; expect about 84,697 with the corps likely to arrive, up to 95,304 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 463, own corps) vs Mack (lost 21981) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (22,665) vs Mack (substantial force) at Tyrol — the balance of force looks unfavorable.
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
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archd… · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharle… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - 🏴 Austria: Casualties: ArchdukeCharles's army 909, Bernadotte 8,864. Both armies remain in the field. Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,413 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 663, own corps) vs Bernadotte (lost 8864) — Where was Ney? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 1480) vs Deroy (lost 8681) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2289) vs Murat (lost 6084) — Murat stood alone, Sire. Ney and Soult never came.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 4444 · net +2788 · threat 78 · provinces 28 (+0) · ceiling 33722 · army 147782 · vassals Holland 94 · Kingdom of Italy 95 · Switzerland 90
  - NET income 3382 · trade 450 · admin 50 · tribute 937 · upkeep 1346 · charges 232 · contributions 82 · blockade 281 · admiralty 90
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
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (15,717; expect about 70,387 with the corps likely to arrive, up to 81,831 if all march) vs Mack (11,267 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 92, own corps) vs Mack (lost 10110) — Davout and Massena's timely arrival aided Ney. Napoleon, however, was conspicuously absent.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (18,224; expect about 25,726 with the corps likely to arrive, up to 38,442 if all march) vs Mack (1,152 men) at Franconia — the balance of force looks fa…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1635, own corps) vs Archduke John (lost 2335) — Reinforcements from Napoleon bolstered Davout's position — though Ney never arrived, Sire.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (166 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 642 gold (×3 at war) (×1.07 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 642g on this turn's orders
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a devastating assault! ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCha… · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeC… · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination) · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination)
  - 🏴 Austria: Casualties: ArchdukeCharles 1,684, Murat's army 8,503. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 1684) vs Murat (lost 4149, own corps) — Lannes arrived to reinforce Murat, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 133) vs Bernadotte (lost 2635) — Not one corps reached Bernadotte. Ney was expected; Bernadotte fought the battle single-handed.
  - ⚔ Archduke Charles (lost 724) vs Napoleon (lost 3135) — Napoleon stood alone, Sire. Ney never came.
  - ⚔ Archduke Charles (lost 476) vs Deroy (lost 4796) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×4
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 6271 · net +2868 · threat 88 · provinces 29 (+1) · ceiling 31786 · army 126247 · vassals Holland 89 · Kingdom of Italy 90 · Switzerland 83
  - NET income 3355 · trade 449 · admin 50 · tribute 937 · upkeep 968 · charges 480 · occupation 104 · blockade 281 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 13
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (14,395; expect about 22,766 with the corps likely to arrive, up to 25,341 if all march) vs Mack (1,152 men) at Franconia — the balance of force looks favor…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 607, own corps) vs Mack (lost 311, own corps) — Reinforcements from Davout bolstered Ney's position — though Massena never arrived, Sire. And Mack was taken on that fi…
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn,…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, fortify×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 9169 · net +2524 · threat 91 · provinces 30 (+1) · ceiling 30848 · army 122705 · vassals Holland 90 · Kingdom of Italy 91 · Switzerland 82
  - NET income 3383 · trade 524 · admin 50 · tribute 937 · upkeep 944 · charges 834 · occupation 174 · blockade 328 · admiralty 90
- DISPATCH: Sire — Marshal Mack of Austria is taken at Franconia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 10
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (13,651; expect about 14,439 with the corps likely to arrive, up to 14,775 if all march) vs Archduke Charles (35,387 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1627, own corps) vs Archduke Charles (lost 854) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (950 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (111 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 11661 · net +2337 · threat 89 · provinces 30 (+0) · ceiling 30322 · army 111444 · vassals Holland 88 · Kingdom of Italy 89 · Switzerland 78
  - NET income 3452 · trade 549 · admin 50 · tribute 937 · upkeep 856 · charges 1209 · occupation 152 · blockade 344 · admiralty 90
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 11
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)

## Turn 6 — Early December 1805
  - MAILBOX #9 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #12 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 5g a turn — 99g of income forfeited, 30g of occupation relieved, 74g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 14435 · net +2276 · threat 87 · provinces 29 (-1) · ceiling 37558 · army 109872 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 86
  - NET income 3465 · trade 549 · admin 50 · tribute 787 · upkeep 848 · charges 1223 · occupation 70 · blockade 344 · admiralty 90
- DISPATCH: Sire — 3 turns of famine at Tyrol now. 4,270 men gone, and not one of them to the enemy. Kingdom of Italy's magazines feed us as our own — the army is simply too large for the province. Milan can fee…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 10
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (149 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Davout → secure
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (11,014; expect about 11,584 with the corps likely to arrive, up to 11,646 if all march) vs Archduke Charles (33,629 men) at Munich — the balance of force…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 5763, own corps) vs Archduke Charles (lost 272, own corps) — Napoleon's timely arrival aided Murat. Soult, however, was conspicuously absent.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeJohn delivers an effective strike. Soult holds the line. Casualties: ArchdukeJohn's army 4,660, Soult 2,147. Bo… · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,777 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,543 troops in the…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - ⚔ Archduke Charles (lost 2882) vs Soult (lost 4158) — Neither Soult nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Archduke John (lost 1223, own corps) vs Soult (lost 2147) — A decisive victory for Soult! Archduke John was thoroughly outmatched.
  - verbs: attack×4, unfortify×2
- ORDER Napoleon [retired]: Napoleon's question is overtaken, Sire — Napoleon has marched clear of Munich. He awaits new orders.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 15428 · net +1405 · threat 87 · provinces 30 (+1) · ceiling 25401 · army 95403 · vassals Holland 87 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3456 · trade 549 · admin 50 · tribute 564 · upkeep 728 · charges 1890 · occupation 162 · blockade 344 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 10
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout pursues Archduke Charles (at Munich). Moves to Franconia. Davout: "I will follow — at a distance that leaves him no chance to turn on us."
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Mi…
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Milan instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1545, own corps) vs Archduke Charles (lost 1604) — Reinforcements from Massena and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! ArchdukeJohn is at Franche-Comte, just one region away.
- CMD `Massena, move to Milan` → ✗ Cannot move into Milan - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles holds them at Tyrol while allies attack from Milan! (+1 coordination) · ArchdukeCharles holds them at Tyrol while allies attack from Milan! (+1 coordination)
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Tyrol!
  - ⚔ Archduke Charles (lost 69) vs Bernadotte (lost 754) — Bernadotte's corps broke, Sire. They are streaming back from the field. And Bernadotte was taken on that field — Austri…
  - ⚔ Archduke Charles (lost 988) vs Napoleon (lost 90, own corps) — Davout reached Napoleon in time, Sire — but even together, the field could not be held.
  - ⚔ Archduke Charles (lost 25) vs Napoleon (lost 227) — The line gave way. Napoleon is falling back, and not in good order.
  - verbs: attack×3, move×1, wait×1
- ORDER Davout [active]: Davout is pursuing Archduke Charles (0 turns remaining).
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Tyrol — 296 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Tyrol — 296 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 16122 · net +933 · threat 85 · provinces 30 (+0) · ceiling 21557 · army 84300 · vassals Holland 81 · Kingdom of Italy 95 · Switzerland 77
  - NET income 3500 · trade 549 · admin 50 · tribute 487 · upkeep 656 · charges 2423 · occupation 140 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 1…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 5 actions, 1 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos launches a decisive assault. Castanos gains the advantage over Paget. Casualties: Castanos 820, Paget 1,487. B…
  - ⚔ Castanos (lost 820) vs Paget (lost 1487) — Paget was close. A period of drilling could have changed the outcome.
  - verbs: wait×2, move×2, attack×1
- ORDER Davout [continues]: Davout pursues ArchdukeCharles. 0 regions away.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 16182 · net +928 · threat 83 · provinces 30 (+0) · ceiling 21490 · army 86655 · vassals Holland 79 · Kingdom of Italy 94 · Switzerland 74
  - NET income 3537 · trade 549 · admin 50 · tribute 505 · upkeep 680 · charges 2479 · occupation 120 · blockade 344 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)

## Turn 10 — Early February 1806
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (79 → 83); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Ney is already in Franconia.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn's forces press forward aggressively. ArchdukeJohn gains the advantage over Ney. Casualties: ArchdukeJohn 5… · ArchdukeJohn marches from Franconia into Bohemia unopposed! (43 lost to march — forward supply lines reduce losses) Cap… · Castanos takes Leon where he stands! (115 lost to march) Captured: Britain → Spain · Castanos launches a devastating assault! Castanos gains the advantage over Paget. Casualties: Castanos 330, Paget 1,717…
  - 🏴 Austria: FORCED RETREAT! ArchdukeJohn advances into Franconia. (88 lost to march) Franconia has been captured by Austria!
  - 🏴 Austria: ArchdukeJohn marches from Franconia into Bohemia unopposed! (43 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - 🏴 Spain: Castanos takes Leon where he stands! (115 lost to march) Captured: Britain → Spain
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Aragon!
  - ⚔ Archduke John (lost 572) vs Ney (lost 1975) — Ney stood alone, Sire. Soult never came.
  - ⚔ Castanos (lost 330) vs Paget (lost 1717) — Paget held superior ground, yet Castanos prevailed. A grim day, Sire. And Paget was taken on that field — Spain holds h…
  - verbs: attack×4, fortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, peace #16 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · stalemate
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 14163 · net +1651 · threat 81 · provinces 28 (-2) · ceiling 29678 · army 94260 · vassals Holland 80 · Kingdom of Italy 91 · Switzerland 69
  - NET income 3365 · trade 561 · admin 50 · tribute 168 · upkeep 728 · charges 1294 · occupation 30 · blockade 351 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 10
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Murat can already reach the body of the realm from w…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [error]: Davout could not advance toward Swabia.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Britain + Russia (4 pairs resolved). → display-only
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 15816 · net +3009 · threat 80 · provinces 28 (+0) · ceiling 109843 · army 93886 · vassals Holland 79 · Kingdom of Italy 88 · Switzerland 66
  - NET income 3390 · trade 585 · admin 50 · tribute 169 · upkeep 728 · charges 442 · occupation 15
- DISPATCH: Sire — Davout and Massena are no nearer home, and the safe passage runs out in 2 turns. After that their corps will be interned where they stand.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 8
- DIPLO +5 medium/low (status_quo_titled ×2, diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 80 to 40.

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 15% -> 20%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout marches to Franconia. 1 region to Swabia.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 18627 · net +2939 · threat 40 · provinces 28 (+0) · ceiling 110468 · army 96768 · vassals Holland 76 · Kingdom of Italy 85 · Switzerland 63
  - NET income 3393 · trade 585 · admin 50 · tribute 210 · upkeep 752 · charges 532 · occupation 15
- DISPATCH: Sire — the war with Britain is over. Davout, Massena hold under your own orders and were not moved — the treaty offers a road, it does not overrule the Emperor. Their passage lapses with the corridor.
  - RAIL settlement_summary: Settlement of France + Spain + Holland vs Britain + Russia: settlement ratified.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 10
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad ×2, diplomatic_dp_regen, blockade_broken ×3)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, move to Franconia` → ✗ Davout is already in Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #19 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1696g forgone). Loyalty +4 (82 → 86); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 21571 · net +2638 · threat 40 · provinces 28 (+0) · ceiling 104000 · army 96768 · vassals Holland 73 · Kingdom of Italy 86 · Switzerland 60
  - NET income 3396 · trade 585 · admin 50 · upkeep 752 · charges 626 · occupation 15
- DISPATCH: Sire — Massena and Davout are no nearer home, and the safe passage runs out in 1 turn. After that their corps will be interned where they stand.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Swa…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Tyrol and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 24212 · net +2782 · threat 40 · provinces 28 (+0) · ceiling 111125 · army 96768 · vassals Holland 70 · Kingdom of Italy 84 · Switzerland 57
  - NET income 3399 · trade 585 · admin 50 · tribute 225 · upkeep 752 · charges 710 · occupation 15
- DISPATCH: Sire — Massena and Davout are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - TURN EVENTS 8
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 84% -> 79%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26754 · net +2839 · threat 40 · provinces 28 (+0) · ceiling 115468 · army 79103 · vassals Holland 67 · Kingdom of Italy 82 · Switzerland 48
  - NET income 3402 · trade 585 · admin 50 · tribute 225 · upkeep 616 · charges 792 · occupation 15
- DISPATCH: Sire — Marshal Massena's corps was interned at Tyrol by Kingdom of Italy — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Ney can already reach the body of the realm from where…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 29596 · net +2839 · threat 40 · provinces 28 (+0) · ceiling 118312 · army 67416 · vassals Holland 64 · Kingdom of Italy 80 · Switzerland 39
  - NET income 3405 · trade 585 · admin 50 · tribute 225 · upkeep 528 · charges 883 · occupation 15
- DISPATCH: Sire — Marshal Davout's corps was interned at Franconia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 2 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 32438 · net +3088 · threat 40 · provinces 28 (+0) · ceiling 128937 · army 67416 · vassals Holland 61 · Kingdom of Italy 78 · Switzerland 30
  - NET income 3408 · trade 585 · admin 50 · tribute 562 · upkeep 528 · charges 974 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Revanche — service to the strong is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Bernadotte recruits 10,000 infantry (nearest to capital) - Cost: 150 gold (capital discount). Morale: 50% -> 43%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- SPENT 150g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 35279 · net +2921 · threat 40 · provinces 28 (+0) · ceiling 126531 · army 77416 · vassals Holland 58 · Kingdom of Italy 76 · Switzerland 21
  - NET income 3411 · trade 585 · admin 50 · tribute 562 · upkeep 608 · charges 1064 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_auto_downgrade)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 38203 · net +2830 · threat 40 · provinces 28 (+0) · ceiling 126625 · army 77416 · vassals Holland 55 · Kingdom of Italy 74 · Switzerland 12
  - NET income 3414 · trade 585 · admin 50 · tribute 562 · upkeep 608 · charges 1158 · occupation 15
- DISPATCH: Sire — the levy has stood open 9 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 41036 · net +2742 · threat 39 · provinces 28 (+0) · ceiling 126718 · army 77416 · vassals Holland 46 · Kingdom of Italy 72 · Switzerland 3
  - NET income 3417 · trade 585 · admin 50 · tribute 562 · upkeep 608 · charges 1249 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
  - POPUP vassal_rebellion_imminent: Switzerland #20 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Switzerland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 42186 · net +1688 · threat 27 · provinces 28 (+0) · ceiling 72760 · army 80416 · vassals Holland 27 · Kingdom of Italy 60
  - NET income 3420 · trade 585 · admin 50 · tribute 588 · upkeep 632 · charges 2218 · occupation 15 · admiralty 90
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 43751 · net +1473 · threat 25 · provinces 28 (+0) · ceiling 68969 · army 80416 · vassals Holland 20 · Kingdom of Italy 60
  - NET income 3423 · trade 585 · admin 50 · tribute 590 · upkeep 632 · charges 2438 · occupation 15 · admiralty 90
- DISPATCH: Sire — Marshal Soult's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos assaults the Bern garrison! Garrison: 10,000 -> 5,944 (-4,056). Castanos loses 3,472 troops. Garrison holds — … · Castanos assaults the Bern garrison! Garrison collapses (5,944 -> 0). Castanos loses 2,293 troops in the assault. Casta…
  - 🏴 Spain: [Materiel] Guns, horses and stores lost with the fallen: Spain -114g, Switzerland -143g. Captured: Switzerland → Spain
  - verbs: attack×2, move×1
- LEDGER treasury 46433 · net +2597 · threat 23 · provinces 28 (+0) · ceiling 127562 · army 80416 · vassals Holland 11 · Kingdom of Italy 58
  - NET income 3426 · trade 597 · admin 50 · tribute 592 · upkeep 632 · charges 1421 · occupation 15
- DISPATCH: Sire — Switzerland is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Switzerland has been eliminated from the war.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 89% -> 84%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 48793 · net +2503 · threat 21 · provinces 28 (+0) · ceiling 127000 · army 83416 · vassals Holland 2 · Kingdom of Italy 56
  - NET income 3429 · trade 597 · admin 50 · tribute 595 · upkeep 656 · charges 1497 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Holland is on the verge of rebellion!
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)
  - LOG nation_eliminated: Switzerland has been eliminated from the war.

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 27.
  - POPUP vassal_rebellion_imminent: Holland #22 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Holland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 50976 · net +2113 · threat 9 · provinces 28 (+0) · ceiling 117000 · army 83416 · vassals Kingdom of Italy 38
  - NET income 3432 · trade 609 · admin 50 · tribute 260 · upkeep 656 · charges 1567 · occupation 15
- DISPATCH: Sire — Holland is no longer ours. They broke free and stand alone.
  - RAIL diplomatic_vassal_broke_free_peace: Sire — Holland breaks free of France and stands alone — an independent power, and no war declared.
  - RAIL allegiance_in_play: The allegiance of Holland is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, agenda_shift, diplomatic_relation_shift)
  - LOG vassal_broke_free: Vassal rebellion: Holland breaks free of France and stands alone.

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 53094 · net +2050 · threat 7 · provinces 28 (+0) · ceiling 117156 · army 83416 · vassals Kingdom of Italy 30
  - NET income 3435 · trade 609 · admin 50 · tribute 262 · upkeep 656 · charges 1635 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 40% -> 40%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 54905 · net +1972 · threat 5 · provinces 28 (+0) · ceiling 116500 · army 86416 · vassals Kingdom of Italy 22
  - NET income 3438 · trade 609 · admin 50 · tribute 262 · upkeep 680 · charges 1692 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 56880 · net +1911 · threat 3 · provinces 28 (+0) · ceiling 116593 · army 86416 · vassals Kingdom of Italy 14
  - NET income 3441 · trade 609 · admin 50 · tribute 262 · upkeep 680 · charges 1756 · occupation 15
- DISPATCH: Sire — the levy has stood open 18 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 58794 · net +1853 · threat 1 · provinces 28 (+0) · ceiling 116687 · army 86416 · vassals Kingdom of Italy 6
  - NET income 3444 · trade 609 · admin 50 · tribute 262 · upkeep 680 · charges 1817 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — the Kingdom of Italy is on the verge of rebellion!
  - RAIL allegiance_in_play: The allegiance of Holland is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: KingdomOfItaly #24 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If KingdomOfItaly's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Davout` → ✓ Bernadotte recruits 10,000 infantry (nearest to capital) - Cost: 150 gold (capital discount). Morale: 43% -> 41%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- SPENT 150g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 60150 · net +1483 · threat 0 · provinces 28 (+0) · ceiling 106468 · army 96416 · vassals none
  - NET income 3447 · trade 621 · admin 50 · upkeep 760 · charges 1860 · occupation 15
- DISPATCH: Sire — Kingdom of Italy is no longer ours. They broke free and stand alone.
  - RAIL diplomatic_vassal_broke_free_peace: Sire — the Kingdom of Italy breaks free of France and stands alone — an independent power, and no war declared.
  - RAIL design_promoted: REVANCHE: Kingdom of Italy will not forgive Austria the loss of Milan. A new design hardens in their court.
  - TURN EVENTS 2
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_dp_regen, agenda_shift, diplomatic_relation_shift)
  - LOG vassal_broke_free: Vassal rebellion: KingdomOfItaly breaks free of France and stands alone.

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 61636 · net +1438 · threat 0 · provinces 28 (+0) · ceiling 106562 · army 96416 · vassals none
  - NET income 3450 · trade 621 · admin 50 · upkeep 760 · charges 1908 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Kingdom of Italy swears to retake Milan — Austria is not forgiven

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 63074 · net +1392 · threat 0 · provinces 28 (+0) · ceiling 106562 · army 96416 · vassals none
  - NET income 3450 · trade 621 · admin 50 · upkeep 760 · charges 1954 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 64083 · net +1336 · threat 0 · provinces 28 (+0) · ceiling 105812 · army 99416 · vassals none
  - NET income 3450 · trade 621 · admin 50 · upkeep 784 · charges 1986 · occupation 15
- DISPATCH: Sire — the levy has stood open 23 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Holland is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 65369 · net +1245 · threat 0 · provinces 28 (+0) · ceiling 104250 · army 99416 · vassals none
  - NET income 3450 · trade 571 · admin 50 · upkeep 784 · charges 2027 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 27 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 66614 · net +1205 · threat 0 · provinces 28 (+0) · ceiling 104250 · army 99416 · vassals none
  - NET income 3450 · trade 571 · admin 50 · upkeep 784 · charges 2067 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 28 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 67576 · net +1150 · threat 0 · provinces 28 (+0) · ceiling 103500 · army 102416 · vassals none
  - NET income 3450 · trade 571 · admin 50 · upkeep 808 · charges 2098 · occupation 15
- DISPATCH: Sire — the levy has stood open 26 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 68726 · net +1113 · threat 0 · provinces 28 (+0) · ceiling 103500 · army 102416 · vassals none
  - NET income 3450 · trade 571 · admin 50 · upkeep 808 · charges 2135 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 30 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Holland is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 69839 · net +1078 · threat 0 · provinces 28 (+0) · ceiling 103500 · army 102416 · vassals none
  - NET income 3450 · trade 571 · admin 50 · upkeep 808 · charges 2170 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 31 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 60% -> 57%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 70674 · net +1027 · threat 0 · provinces 28 (+0) · ceiling 102750 · army 105416 · vassals none
  - NET income 3450 · trade 571 · admin 50 · upkeep 832 · charges 2197 · occupation 15
- DISPATCH: Sire — the levy has stood open 29 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 71701 · net +994 · threat 0 · provinces 28 (+0) · ceiling 102750 · army 105416 · vassals none
  - NET income 3450 · trade 571 · admin 50 · upkeep 832 · charges 2230 · occupation 15
- DISPATCH: Sire — Marshal Soult's claim is 33 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 200 · popups 54 · battles 25
