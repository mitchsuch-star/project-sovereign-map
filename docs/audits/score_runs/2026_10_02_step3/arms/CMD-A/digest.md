# Playtest digest — CMD-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `53f476feb019` (dirty) · content `2be9b7964cb7` · driver `912b2f0472a7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2621, own corps) vs Mack (lost 14668) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a devastating assault! Archduke Charles gains the advantage over Bernadotte. Casualties: Arch… · ArchdukeJohn holds them at Franconia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 1985, own corps) vs Bernadotte (lost 6478, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - ⚔ Archduke John (lost 328, own corps) vs Bernadotte (lost 5430) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - verbs: stance_change×2, attack×2, move×1, retreat×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1495 · net +1751 · threat 75 · provinces 28 · ceiling 34187 · army 165360 · vassals Holland 97 · Kingdom of Italy 99 · Switzerland 95
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 1886 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,857; expect about 92,068 with the corps likely to arrive, up to 103,011 if all march) vs Mack (substantial force) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1113, own corps) vs Mack (lost 16907, own corps) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,125; expect about 25,817 with the corps likely to arrive, up to 29,971 if all march) vs Mack (strength unknown) at Tyrol — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 322, own corps) vs Mack (lost 12979) — Reinforcements! Ney marched onto the field beside Davout. The enemy's advantage melted away.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Bernadotte. Casualties: Archdu… · ArchdukeCharles holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1161) vs Bernadotte (lost 2616, own corps) — Lannes arrived to reinforce Bernadotte, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 1563) vs Deroy (lost 6551) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 3264 · net +2255 · threat 89 · provinces 28 (+0) · ceiling 36806 · army 147839 · vassals Holland 97 · Kingdom of Italy 99 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 937 · upkeep 1354 · charges 84 · requisitions 37 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 25 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Cannot attack elsewhere while engaged with enemy forces! Archduke John must be dealt with first.
- CMD `Davout, attack Mack` → ✗ Cannot attack elsewhere while engaged with enemy forces! Archduke John must be dealt with first.
- CMD `Lannes, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 682 gold (×3 at war) (×1.14 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- SPENT 682g on this turn's orders
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Murat. Casualties: Archduke…
  - 🏴 Austria: ArchdukeCharles takes Swabia where he stands! Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 2014) vs Murat (lost 5892) — Where was Soult? Murat held the field alone — reinforcement never came.
  - verbs: attack×2, move×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 3009, own corps) vs Archduke Charles (lost 6751) — Reinforcements from Massena and Napoleon bolstered Murat's position — though Soult never arrived, Sire.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4555 · net +2285 · threat 87 · provinces 28 (+0) · ceiling 25479 · army 135645 · vassals Holland 95 · Kingdom of Italy 97 · Switzerland 89
  - NET income 2575 · trade 525 · admin 50 · tribute 937 · upkeep 1076 · charges 279 · contributions 65 · requisitions 37 · blockade 329 · admiralty 90
- DISPATCH: Sire — Murat was mauled at Franche-Comte: a quarter of his corps — 5,892 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 8
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as service to the strong.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Ney can give chase.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Munich to Tyrol. Tyrol falls to France! (was Austria) (2,132 lost to march)
  - POPUP capture_choice[capture]: Tyrol, Massena → secure
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Murat. Casualties: Archduke Charles…
  - 🏴 Austria: Casualties: Archduke Charles 1,164, Murat's army 7,384. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - ⚔ Archduke Charles (lost 1164) vs Murat (lost 5205, own corps) — Napoleon's timely arrival aided Murat. Soult, however, was conspicuously absent.
  - verbs: attack×1, wait×1
- LEDGER treasury 6692 · net +2107 · threat 87 · provinces 28 (+0) · ceiling 24365 · army 121139 · vassals Holland 93 · Kingdom of Italy 95 · Switzerland 85
  - NET income 2546 · trade 587 · admin 50 · tribute 937 · upkeep 944 · charges 559 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps sta…
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (14,629; expect about 45,360 with the corps likely to arrive, up to 45,633 if all march) vs Archduke Charles (substantial force) at Munich — the balance of …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2373, own corps) vs Archduke Charles (lost 2745) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Lannes can give chase.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia. Swabia falls to France! (was Austria) (914 lost to march)
  - POPUP capture_choice[capture]: Swabia, Soult → secure
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (75 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha… · ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,674 troops. G…
  - ⚔ Archduke Charles (lost 254) vs Ney (lost 6977) — A grievous defeat for Ney, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 945) vs Deroy (lost 4436) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×3, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #10 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #11 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 43g a turn — 36g of income forfeited, 52g of occupation relieved, 27g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- ENVOYS WAITING 2 · Austria armistice losing · KingdomOfItaly client petition
- LEDGER treasury 8285 · net +1949 · threat 87 · provinces 28 (+0) · ceiling 22868 · army 104796 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 79
  - NET income 2531 · trade 587 · admin 50 · tribute 946 · upkeep 816 · charges 839 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +4 medium/low (diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 35/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charl…
  - ⚔ Archduke Charles (lost 263) vs Deroy (lost 4598) — A grievous defeat for Deroy, Sire. The losses are severe.
  - verbs: attack×1, fortify×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10167 · net +1604 · threat 85 · provinces 28 (+0) · ceiling 21890 · army 102875 · vassals Holland 89 · Kingdom of Italy 99 · Switzerland 77
  - NET income 2529 · trade 587 · admin 50 · tribute 951 · upkeep 776 · charges 1117 · contributions 110 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Franche-Comte lies in enemy hands. Austria holds it.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
  - MAILBOX #10 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #12 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (77 → 87); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Murat, attack Archduke Charles` → ✗ Cannot attack Archduke Charles — armistice with Austria (4 turns remaining).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 11616 · net +1220 · threat 83 · provinces 28 (+0) · ceiling 20328 · army 100323 · vassals Holland 89 · Kingdom of Italy 98 · Switzerland 86
  - NET income 2530 · trade 587 · admin 50 · tribute 787 · upkeep 768 · charges 1346 · contributions 110 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: Britain and Prussia rebuff Bavaria (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Cannot attack Archduke Charles — armistice with Austria (3 turns remaining).
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Tyr…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena moves from Tyrol to Milan (600 lost to march)
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
- LEDGER treasury 12921 · net +1088 · threat 81 · provinces 28 (+0) · ceiling 20512 · army 98689 · vassals Holland 89 · Kingdom of Italy 99 · Switzerland 85
  - NET income 2573 · trade 587 · admin 50 · tribute 791 · upkeep 752 · charges 1563 · contributions 110 · occupation 30 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has held Franche-Comte 4 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 155…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- SPENT 1552g on this turn's orders
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John's attack meets fierce resistance. Archduke John gains the advantage over Deroy. Casualties: Archduke John… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Deroy is taken by Austria at Munich!
  - ⚔ Archduke John (lost 398) vs Deroy (lost 2127) — Deroy's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Archduke Charles (lost 40, own corps) vs Deroy (lost 1179) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire. And Deroy was taken on that field — Austr…
  - verbs: attack×2, unfortify×1, recruit×1
- LEDGER treasury 12590 · net +1037 · threat 79 · provinces 28 (+0) · ceiling 19670 · army 101371 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2568 · trade 587 · admin 50 · tribute 796 · upkeep 776 · charges 1550 · contributions 150 · occupation 30 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich.
  - saved `CMD-A_t10` → Game saved: CMD-A_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,338 troops. G… · ArchdukeCharles assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,854 troops in th…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -92g, Bavaria -125g. Captured: Bavaria → Austria
  - verbs: attack×2, naval_expedition×1, fortify×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13606 · net +830 · threat 77 · provinces 28 (+0) · ceiling 19152 · army 101059 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 83
  - NET income 2570 · trade 524 · admin 50 · tribute 796 · upkeep 776 · charges 1736 · contributions 150 · occupation 30 · blockade 328 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 11 — Late February 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Britain + Russia (4 pairs resolved). Status quo: Andalusia stays British by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✓ MUSTER — Ney (4,705; expect about 25,826 with the corps likely to arrive, up to 26,937 if all march) vs Archduke John (12,456 men) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 858, own corps) vs Archduke John (lost 1097, own corps) — Reinforcements from Massena bolstered Ney's position — though Soult never arrived, Sire.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Tyrol with 3,847 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia. Franconia falls to France! (was Austria) (100 lost to march)
  - POPUP capture_choice[capture]: Franconia, Murat → secure
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Davout holds the line. Casualties: Mack 5,108, Davout's army 1,005. Both armies remain in… · ArchdukeCharles flanks from Munich while allies attack from Bohemia! (+1 coordination)
  - ⚔ Mack (lost 5108) vs Davout (lost 858, own corps) — Murat arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Archduke Charles (lost 1081) vs Murat (lost 2414, own corps) — Even the favorable ground could not save Murat, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #16 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (84 → 94); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14572 · net +788 · threat 42 · provinces 29 (+1) · ceiling 19506 · army 88453 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 79
  - NET income 2614 · trade 548 · admin 50 · tribute 444 · upkeep 672 · charges 2006 · occupation 100 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL settlement_summary: Settlement of France vs Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 10
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad, diplomatic_dp_regen, blockade_broken ×3, agenda_shift)
  - LOG ai_ai_proposal_refused: 15 approaches from Britain, Russia and Prussia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 77 to 38; Austria remains at war with us.
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 15% -> 21%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- SPENT 600g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, form_square×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 14848 · net +720 · threat 44 · provinces 29 (+0) · ceiling 19266 · army 91095 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 78
  - NET income 2639 · trade 548 · admin 50 · tribute 445 · upkeep 696 · charges 2091 · occupation 85 · admiralty 90
- DISPATCH: Sire — the enemy has held Franche-Comte 8 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 9
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as alliance.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Murat, attack Archduke John` → ✗ Murat is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Tyrol to Franconia (152 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Munich into Tyrol unopposed! (101 lost to march — forward supply lines reduce losses) Capture… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Davout. Casualties: Archduke Ch…
  - 🏴 Austria: ArchdukeJohn marches from Munich into Tyrol unopposed! (101 lost to march — forward supply lines reduce losses) Captured: KingdomOfItaly → Austria
  - 🏴 Austria: ArchdukeCharles advances into Franconia. (307 lost to march — forward supply lines reduce losses) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 936) vs Davout (lost 3313) — The line gave way. Davout is falling back, and not in good order.
  - verbs: move×2, attack×2
- LEDGER treasury 15768 · net +894 · threat 45 · provinces 28 (-1) · ceiling 22201 · army 87279 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 75
  - NET income 2600 · trade 548 · admin 50 · tribute 375 · upkeep 664 · charges 1910 · occupation 15 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 10
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 approaches from Britain, Russia and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Bavaria (open borders agreement)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, move×2
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 16665 · net +950 · threat 45 · provinces 28 (+0) · ceiling 23352 · army 86934 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 74
  - NET income 2603 · trade 548 · admin 50 · tribute 600 · upkeep 664 · charges 2082 · occupation 15 · admiralty 90
- DISPATCH: Sire — the enemy has held Franche-Comte 10 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 10
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Mack is at Franconia, just one region away.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- SPENT 600g on this turn's orders
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack attacks with overwhelming force. Davout holds the line. Casualties: Mack 8,249, Davout's army 837. Both armies rem…
  - ⚔ Mack (lost 8249) vs Davout (lost 296, own corps) — Napoleon's timely arrival bolstered Davout's position. Well-coordinated, Sire.
  - verbs: attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #17 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (74 → 84); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 17014 · net +601 · threat 45 · provinces 28 (+0) · ceiling 21141 · army 88181 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2591 · trade 548 · admin 50 · tribute 375 · upkeep 672 · charges 2186 · occupation 15 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Swabia — Mack's corps is driven from Swabia yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 11
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 17618 · net +467 · threat 45 · provinces 28 (+0) · ceiling 20750 · army 87283 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2594 · trade 548 · admin 50 · tribute 375 · upkeep 672 · charges 2323 · occupation 15 · admiralty 90
- DISPATCH: Sire — Marshal Murat's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 9
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 17 — Late May 1806
  - MAILBOX #14 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #18 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 2 actions unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Lannes and Murat: They settle into cold war.
- LEDGER treasury 19680 · net +1952 · threat 45 · provinces 28 (+0) · ceiling 56085 · army 86403 · vassals Holland 87 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2597 · trade 548 · admin 50 · tribute 375 · upkeep 656 · charges 947 · occupation 15
- DISPATCH: Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 9
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Milan. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 0% -> 8%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- SPENT 170g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 21425 · net +1837 · threat 45 · provinces 28 (+0) · ceiling 55694 · army 88481 · vassals Holland 86 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2600 · trade 548 · admin 50 · tribute 375 · upkeep 680 · charges 1041 · occupation 15
- DISPATCH: Sire — 7 turns without settlement on Marshal Murat. A rente would close it today; the arrears will not close themselves.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23273 · net +2086 · threat 45 · provinces 28 (+0) · ceiling 62186 · army 87577 · vassals Holland 85 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2603 · trade 548 · admin 50 · tribute 712 · upkeep 672 · charges 1140 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 8 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 7
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-A_t20` → Game saved: CMD-A_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 25370 · net +1985 · threat 45 · provinces 28 (+0) · ceiling 62391 · army 86692 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2606 · trade 548 · admin 50 · tribute 712 · upkeep 664 · charges 1252 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte 16 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 8
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 21 — Late July 1806
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (84 → 94); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Milan, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Davout: Murat turns openly discontent (trust -3; expect defiance).
- LEDGER treasury 27973 · net +2572 · threat 45 · provinces 28 (+0) · ceiling 242250 · army 90824 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2609 · trade 560 · admin 50 · tribute 375 · upkeep 696 · charges 311 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armistice_expired_peace: The armistice between Austria and France has concluded. Peace declared.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 9
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as service to the strong.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as service to the strong.
- COURTS: And Prussia stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 30556 · net +2552 · threat 45 · provinces 28 (+0) · ceiling 243166 · army 89974 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2612 · trade 560 · admin 50 · tribute 375 · upkeep 688 · charges 342 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 33111 · net +2749 · threat 45 · provinces 28 (+0) · ceiling 262166 · army 89141 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2615 · trade 560 · admin 50 · tribute 600 · upkeep 688 · charges 373 · occupation 15
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 40,859 men at Paris, and nobody has gone to collect them.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 92%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 35625 · net +2706 · threat 45 · provinces 28 (+0) · ceiling 261083 · army 91264 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2618 · trade 560 · admin 50 · tribute 600 · upkeep 704 · charges 403 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 38342 · net +2684 · threat 45 · provinces 28 (+0) · ceiling 262000 · army 90405 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2621 · trade 560 · admin 50 · tribute 600 · upkeep 696 · charges 436 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- LEDGER treasury 41037 · net +2663 · threat 45 · provinces 28 (+0) · ceiling 262916 · army 89564 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2624 · trade 560 · admin 50 · tribute 600 · upkeep 688 · charges 468 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte 22 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 5
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 41% -> 40%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 43456 · net +2613 · threat 45 · provinces 28 (+0) · ceiling 261166 · army 91738 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2627 · trade 560 · admin 50 · tribute 600 · upkeep 712 · charges 497 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- COURTS: And Prussia stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- LEDGER treasury 46088 · net +2937 · threat 45 · provinces 28 (+0) · ceiling 290833 · army 90930 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2630 · trade 560 · admin 50 · tribute 937 · upkeep 696 · charges 529 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 49036 · net +2913 · threat 45 · provinces 28 (+0) · ceiling 291750 · army 90138 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2633 · trade 560 · admin 50 · tribute 937 · upkeep 688 · charges 564 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte 25 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 28% -> 30%
  - saved `CMD-A_t30` → Game saved: CMD-A_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- SPENT 170g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 51743 · net +2868 · threat 45 · provinces 28 (+0) · ceiling 290666 · army 92302 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2636 · trade 560 · admin 50 · tribute 937 · upkeep 704 · charges 596 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Britain (defensive alliance)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 54614 · net +2836 · threat 45 · provinces 28 (+0) · ceiling 290916 · army 91482 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2639 · trade 560 · admin 50 · tribute 937 · upkeep 704 · charges 631 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 57461 · net +2813 · threat 45 · provinces 28 (+0) · ceiling 291833 · army 90679 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2642 · trade 560 · admin 50 · tribute 937 · upkeep 696 · charges 665 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte 28 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Milan, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 60285 · net +2790 · threat 45 · provinces 28 (+0) · ceiling 292750 · army 89891 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2645 · trade 560 · admin 50 · tribute 937 · upkeep 688 · charges 699 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 63036 · net +2718 · threat 49 · provinces 28 (+0) · ceiling 289500 · army 89119 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2648 · trade 510 · admin 50 · tribute 937 · upkeep 680 · charges 732 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 65757 · net +2688 · threat 53 · provinces 28 (+0) · ceiling 289750 · army 88363 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2651 · trade 510 · admin 50 · tribute 937 · upkeep 680 · charges 765 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte 31 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 92%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 68210 · net +2646 · threat 57 · provinces 28 (+0) · ceiling 288666 · army 90563 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2654 · trade 510 · admin 50 · tribute 937 · upkeep 696 · charges 794 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 70867 · net +2625 · threat 60 · provinces 28 (+0) · ceiling 289583 · army 89778 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2657 · trade 510 · admin 50 · tribute 937 · upkeep 688 · charges 826 · occupation 15
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 73503 · net +2604 · threat 58 · provinces 28 (+0) · ceiling 290500 · army 89009 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2660 · trade 510 · admin 50 · tribute 937 · upkeep 680 · charges 858 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 27 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 60% -> 56%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 75861 · net +2552 · threat 56 · provinces 28 (+0) · ceiling 288500 · army 91256 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2660 · trade 510 · admin 50 · tribute 937 · upkeep 704 · charges 886 · occupation 15
- DISPATCH: Sire — Marshal Murat's claim is 28 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-A_t40` → Game saved: CMD-A_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 76522 · net +401 · threat 54 · provinces 28 (+0) · ceiling 87909 · army 90518 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2660 · trade 474 · admin 50 · tribute 937 · upkeep 696 · charges 2623 · occupation 15 · blockade 296 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_alliance_cascade: Spain enters the war against Britain, Russia, Austria, Sweden and Sardinia via its alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 1 allied court poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 1 allied court poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Armistice, with 1 allied court poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 1 allied court poised to follow.
  - RAIL diplomatic_war_declared: Sardinia has declared war on France, with 1 allied court poised to follow.
  - RAIL +4 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And Sweden, Austria and Sardinia stir at their own designs.
- DIPLO +13 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, blockade_begins ×4, diplomatic_relation_shift ×5)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Armistice with France by declaring war.
  - LOG coalition_declared: The Fourth Austrian Coalition — Coalition formed against France! Members: Austria, Britain, Russia, Sardinia, Sweden
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

---
finished: **completed** · commands 200 · popups 44 · battles 21
