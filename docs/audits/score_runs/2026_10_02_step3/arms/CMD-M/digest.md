# Playtest digest — CMD-M

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `53f476feb019` (dirty) · content `2be9b7964cb7` · driver `912b2f0472a7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 3461, own corps) vs Mack (lost 9416) — Reinforcements from Davout and Napoleon bolstered Ney's position — though Soult, Lannes, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Mack.
- CMD `Lannes, move to Rhineland` → ✓ Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?'
  - POPUP strategic_interrupt: Lannes, contact_bad_odds, Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 2403, own corps) vs Mack (lost 9146) — Ney and Bernadotte's timely arrival aided Lannes. Soult and Murat, however, were conspicuously absent.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charl…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franconia. (1,570 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1649, own corps) vs Deroy (lost 9954) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: stance_change×2, move×1, attack×1, wait×1
- ORDER Lannes [active]: Lannes is marching to Rhineland (3 turns remaining).
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1635 · net +1454 · threat 67 · provinces 28 · ceiling 34455 · army 174947 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2164 · blockade 219 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,922; expect about 79,016 with the corps likely to arrive, up to 91,502 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 853, own corps) vs Mack (lost 15856) — Lannes and Massena arrived to reinforce Ney, but Murat and Bernadotte failed to reach the field in time.
- CMD `Davout, attack Mack` → ✓ Davout pursues Mack (at Munich). Moves to Swabia. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt…
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Davout. Casualties: Archduke Charle… · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeCharles holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - ⚔ Archduke Charles (lost 2157, own corps) vs Davout (lost 4663, own corps) — Reinforcements from Napoleon bolstered Davout's position — though Ney, Soult and Murat never arrived, Sire.
  - ⚔ Archduke John (lost 223, own corps) vs Deroy (lost 5643) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1314, own corps) vs Bernadotte (lost 6686) — Bernadotte stood alone, Sire. Ney and Soult never came.
  - ⚔ Archduke John (lost 1030, own corps) vs Davout (lost 3226) — Not one corps reached Davout. Ney, Soult and Murat were expected; Davout fought the battle single-handed.
  - verbs: attack×4
- ORDER Davout [active]: Davout is pursuing Mack (0 turns remaining).
- ORDER Lannes [active]: Lannes answered the guns this turn and stands at Munich; his march resumes next turn.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2922 · net +2095 · threat 73 · provinces 28 (+0) · ceiling 36267 · army 152285 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 937 · upkeep 1504 · charges 57 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +9 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 13 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (16,244; expect about 81,886 with the corps likely to arrive, up to 82,721 if all march) vs Mack (15,705 men) at Franconia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 115, own corps) vs Mack (lost 14660) — Lannes and Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was taken on that field …
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 687 gold (×3 at war) (×1.15 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 actions unused) Turn 4 begins!
- SPENT 687g on this turn's orders
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Davout. Casualties: Arc… · Archduke John launches a decisive assault. Archduke John gains the advantage over Davout. Casualties: Archduke John 1,3… · Archduke John delivers an effective strike. Brutal stalemate between Archduke John and Murat. Heavy casualties on both …
  - 🏴 Austria: Casualties: Archduke John 1,392, Davout 5,002. Both armies remain in the field. Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 2272, own corps) vs Davout (lost 2396, own corps) — Ney and Napoleon arrived to reinforce Davout, but Soult and Murat failed to reach the field in time.
  - ⚔ Archduke John (lost 486, own corps) vs Davout (lost 5002) — Davout stood alone, Sire. Soult and Murat never came.
  - ⚔ Archduke John (lost 1251, own corps) vs Murat (lost 3743) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×3, form_square×1
- ORDER Lannes [active]: Lannes answered the guns this turn and stands at Franconia; his march resumes next turn.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4138 · net +2316 · threat 81 · provinces 29 (+1) · ceiling 25820 · army 138014 · vassals Holland 94 · Kingdom of Italy 94 · Switzerland 89
  - NET income 2621 · trade 525 · admin 50 · tribute 937 · upkeep 1100 · charges 228 · occupation 70 · blockade 329 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Bavaria and Hanover rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Franconia to Tyrol. Tyrol falls to France! (was Austria) (2,312 lost to march)
  - POPUP capture_choice[capture]: Tyrol, Massena → secure
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Murat. Casualties: Archduke…
  - ⚔ Archduke Charles (lost 2035) vs Murat (lost 4656, own corps) — Reinforcements from Napoleon bolstered Murat's position — though Soult never arrived, Sire.
  - verbs: move×2, attack×1, fortify×1
- ORDER Lannes [interrupted]: Lannes hears cannon fire! Abandoning orders — rushing to Franche-Comte! Lannes moves from Franconia to Swabia. Swabia falls to France! (was Austria) …
  - POPUP marshal_audience: shadow_command, Marshal Soult asks for a command → detach
  -     ↳ Soult straightens. "You will not regret it, Sire." March him to Franconia and the front is his — the order is…
- LEDGER treasury 6284 · net +2060 · threat 83 · provinces 31 (+2) · ceiling 24161 · army 127992 · vassals Holland 92 · Kingdom of Italy 92 · Switzerland 85
  - NET income 2670 · trade 587 · admin 50 · tribute 937 · upkeep 1000 · charges 493 · contributions 59 · occupation 174 · blockade 368 · admiralty 90
- DISPATCH: Sire — Napoleon's corps has been broken at Franche-Comte. He must reform before he fights again.
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Russia, Naples and Denmark rebuff Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ Ney pursues Archduke Charles (at Franche-Comte). Moves to Swabia. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted…
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (914 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (136 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franche-Comte where he stands! Captured: France → Austria · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,380 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,388 troops in the…
  - 🏴 Austria: ArchdukeCharles takes Franche-Comte where he stands! Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -69g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - verbs: attack×3, move×1
- ORDER Ney [active]: Ney is pursuing Archduke Charles (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 8145 · net +1402 · threat 81 · provinces 30 (-1) · ceiling 19981 · army 123989 · vassals Holland 92 · Kingdom of Italy 92 · Switzerland 93
  - NET income 2613 · trade 587 · admin 50 · tribute 487 · upkeep 976 · charges 727 · occupation 174 · blockade 368 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of 30,368 stands there. A garrison you detach (3,000 men) holds a province against a …
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke John is at Munich, just one region away.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Munich instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1315, own corps) vs Archduke John (lost 2803, own corps) — Ney and Massena arrived to reinforce Lannes, but Soult and Murat failed to reach the field in time.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Provence unopposed! (206 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (206 lost to march) Captured: France → Austria
  - verbs: attack×1
- ORDER Ney [active]: Ney answered the guns this turn and stands at Swabia; the pursuit resumes next turn.
- LEDGER treasury 9270 · net +1187 · threat 69 · provinces 29 (-1) · ceiling 18808 · army 116414 · vassals Holland 92 · Switzerland 92
  - NET income 2676 · trade 599 · admin 50 · tribute 337 · upkeep 896 · charges 904 · contributions 110 · occupation 100 · blockade 375 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - TURN EVENTS 3
- DIPLO +4 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ Ney: 'ArchdukeJohn bars the way!' Engaging!
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 424, own corps) vs Archduke John (lost 5620) — Reinforcements from Lannes and Massena bolstered Ney's position — though Soult and Murat never arrived, Sire.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 3). Moved to Swabia. Route: Swabia -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Not enough actions for a strategic pursuit! Need 2, have 1.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Milan into Tyrol unopposed! (386 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Milan into Tyrol unopposed! (386 lost to march) Captured: France → Austria
  - verbs: attack×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
- ORDER Ney [active]: Ney is pursuing Archduke Charles (1 turn remaining).
- LEDGER treasury 10338 · net +977 · threat 70 · provinces 28 (-1) · ceiling 17942 · army 112295 · vassals Holland 93 · Switzerland 92
  - NET income 2570 · trade 599 · admin 50 · tribute 337 · upkeep 864 · charges 1070 · contributions 110 · occupation 70 · blockade 375 · admiralty 90
- DISPATCH: Sire — Franche-Comte and Provence lie in enemy hands. Austria holds them.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Davout can give chase.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John a…
  - POPUP objection: Ney, Ney firmly objects: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Milan instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 60, own corps) vs Archduke John (lost 3850) — Lannes and Massena arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. And Archduke John …
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Massena is already in Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout : Davout: 'Cannon fire at Milan, Sire. Investigate?'
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Milan, Sire. Investigate?' → investigate
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
- LEDGER treasury 11392 · net +899 · threat 71 · provinces 28 (+0) · ceiling 18215 · army 111005 · vassals Holland 94 · Switzerland 92
  - NET income 2574 · trade 599 · admin 50 · tribute 337 · upkeep 856 · charges 1235 · contributions 110 · requisitions 75 · occupation 70 · blockade 375 · admiralty 90
- DISPATCH: Sire — the Archduke John of Austria is taken at Milan — he is our prisoner, and their order of battle is one commander shorter.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 155…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- SPENT 1552g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10904 · net +920 · threat 69 · provinces 28 (+0) · ceiling 17727 · army 114005 · vassals Holland 94 · Switzerland 91
  - NET income 2609 · trade 599 · admin 50 · tribute 337 · upkeep 880 · charges 1200 · contributions 150 · requisitions 75 · occupation 55 · blockade 375 · admiralty 90
- DISPATCH: Sire — 3 turns now with Franche-Comte and Provence in enemy hands. The country counts every one of them.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Munich to Franconia (111 lost to march)
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, ma…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich.
  - saved `CMD-M_t10` → Game saved: CMD-M_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 1 action unused) Turn 11 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles executes a brilliant maneuver! Archduke Charles gains the advantage over Ney. Casualties: Archduke Cha…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Franconia. (658 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 811) vs Ney (lost 4447) — Not one corps reached Ney. Soult was expected; Ney fought the battle single-handed.
  - verbs: attack×1, form_square×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11557 · net +723 · threat 67 · provinces 27 (-1) · ceiling 16647 · army 108482 · vassals Holland 92 · Switzerland 88
  - NET income 2481 · trade 599 · admin 50 · tribute 337 · upkeep 832 · charges 1357 · contributions 150 · requisitions 75 · occupation 15 · blockade 375 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Piedmont.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: Britain rebuffs 4 courts (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Swabia stays ours by the treaty — titled. Status quo: Franche-Comte, Franconia and Provence stay Austrian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Lannes, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Murat can already reach the body of the realm from w…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: break_square×1, fortify×1
- ORDER Lannes [continues]: Lannes marches to Munich. 1 region to Swabia.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14110 · net +2185 · threat 36 · provinces 27 (+0) · ceiling 196166 · army 107322 · vassals Holland 100 · Switzerland 87
  - NET income 2484 · trade 635 · admin 50 · upkeep 824 · charges 145 · occupation 15
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 7
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_coalition_dissolved, status_quo_titled, law_enacted_abroad, diplomatic_dp_regen, blockade_broken ×3, agenda_shift)
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Sardinia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 67 to 33.

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [completed]: Lannes arrives at Swabia. Lannes: "It is done. Point me at something that shoots back, Sire."
- LEDGER treasury 16306 · net +2170 · threat 39 · provinces 27 (+0) · ceiling 197083 · army 105616 · vassals Holland 99 · Switzerland 86
  - NET income 2487 · trade 635 · admin 50 · upkeep 816 · charges 171 · occupation 15
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as service to the strong.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as service to the strong.
- COURTS: And Russia stirs at its own design.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Davout can already reach the body of the realm from …
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 18503 · net +2395 · threat 42 · provinces 27 (+0) · ceiling 218083 · army 103961 · vassals Holland 98 · Switzerland 85
  - NET income 2490 · trade 635 · admin 50 · tribute 225 · upkeep 792 · charges 198 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte and Provence 7 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will conduct dril…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will conduct drill training instead.) → trust
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Insisting costs 2 actions — he must fir…
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will conduct drill training instead.) → trust
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 20909 · net +2378 · threat 45 · provinces 27 (+0) · ceiling 219000 · army 102355 · vassals Holland 97 · Switzerland 84
  - NET income 2493 · trade 635 · admin 50 · tribute 225 · upkeep 784 · charges 226 · occupation 15
- DISPATCH: Sire — Massena is no nearer home, and the safe passage runs out in 2 turns. After that his corps will be interned where it stands.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #14 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 93%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22834 · net +2124 · threat 45 · provinces 27 (+0) · ceiling 199833 · army 103707 · vassals Holland 96 · Switzerland 94
  - NET income 2496 · trade 635 · admin 50 · upkeep 792 · charges 250 · occupation 15
- DISPATCH: Sire — Massena is no nearer home, and the safe passage runs out in 1 turn. After that his corps will be interned where it stands.
  - TURN EVENTS 10
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, diplomatic_ai_ai_treaty)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Ney can already reach the body of the realm from where…
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 2 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24969 · net +2110 · threat 45 · provinces 27 (+0) · ceiling 200750 · army 102109 · vassals Holland 95 · Switzerland 94
  - NET income 2499 · trade 635 · admin 50 · upkeep 784 · charges 275 · occupation 15
- DISPATCH: Sire — Massena is no nearer home, and the safe passage runs out in 0 turns. After that his corps will be interned where it stands.
  - TURN EVENTS 4
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Swa…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 17 ended. Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 27090 · net +2343 · threat 45 · provinces 27 (+0) · ceiling 222333 · army 69081 · vassals Holland 94 · Switzerland 94
  - NET income 2502 · trade 635 · admin 50 · upkeep 528 · charges 301 · occupation 15
- DISPATCH: Sire — Marshal Massena's corps was interned at Milan by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 29452 · net +2334 · threat 45 · provinces 27 (+0) · ceiling 223916 · army 67578 · vassals Holland 93 · Switzerland 94
  - NET income 2505 · trade 635 · admin 50 · upkeep 512 · charges 329 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as service to the strong.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31805 · net +2662 · threat 45 · provinces 27 (+0) · ceiling 253583 · army 66118 · vassals Holland 92 · Switzerland 94
  - NET income 2508 · trade 635 · admin 50 · tribute 337 · upkeep 496 · charges 357 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
  - saved `CMD-M_t20` → Game saved: CMD-M_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 34477 · net +2640 · threat 45 · provinces 27 (+0) · ceiling 254416 · army 64703 · vassals Holland 91 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 337 · upkeep 488 · charges 389 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte and Provence 14 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 21 — Late July 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 1 action unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 36406 · net +2272 · threat 45 · provinces 27 (+0) · ceiling 225666 · army 66240 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · upkeep 496 · charges 412 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 38686 · net +2477 · threat 45 · provinces 27 (+0) · ceiling 245083 · army 64822 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 225 · upkeep 488 · charges 440 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 41171 · net +2455 · threat 45 · provinces 27 (+0) · ceiling 245750 · army 63446 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 225 · upkeep 480 · charges 470 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte and Provence 17 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 92%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 43388 · net +2413 · threat 45 · provinces 27 (+0) · ceiling 244416 · army 65021 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 225 · upkeep 496 · charges 496 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 1
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as service to the strong.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 45817 · net +2400 · threat 45 · provinces 27 (+0) · ceiling 245750 · army 63639 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 225 · upkeep 480 · charges 525 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 48225 · net +2379 · threat 45 · provinces 27 (+0) · ceiling 246416 · army 62299 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 225 · upkeep 472 · charges 554 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte and Provence 20 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 81%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 50373 · net +2345 · threat 45 · provinces 27 (+0) · ceiling 245750 · army 63908 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 225 · upkeep 480 · charges 580 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 52726 · net +2662 · threat 45 · provinces 27 (+0) · ceiling 274500 · army 62559 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 562 · upkeep 472 · charges 608 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 55404 · net +2646 · threat 49 · provinces 27 (+0) · ceiling 275833 · army 61250 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 562 · upkeep 456 · charges 640 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte and Provence 23 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-M_t30` → Game saved: CMD-M_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 58058 · net +2622 · threat 53 · provinces 27 (+0) · ceiling 276500 · army 59981 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 562 · upkeep 448 · charges 672 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as service to the strong.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Trust him and he will conduct drill tra…
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Trust him and he will conduct drill training instead.) → trust
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 60680 · net +2590 · threat 57 · provinces 27 (+0) · ceiling 276500 · army 58750 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 562 · upkeep 448 · charges 704 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 63286 · net +2575 · threat 60 · provinces 27 (+0) · ceiling 277833 · army 57556 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 562 · upkeep 432 · charges 735 · occupation 15
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 65487 · net +2541 · threat 58 · provinces 27 (+0) · ceiling 277166 · army 59307 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 635 · admin 50 · tribute 562 · upkeep 440 · charges 761 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 67998 · net +2481 · threat 56 · provinces 27 (+0) · ceiling 274666 · army 58096 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 597 · admin 50 · tribute 562 · upkeep 432 · charges 791 · occupation 15
- DISPATCH: Sire — Marshal Ney's claim is 26 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 68690 · net +456 · threat 54 · provinces 27 (+0) · ceiling 81630 · army 56921 · vassals Holland 100 · Switzerland 94
  - NET income 2510 · trade 561 · admin 50 · tribute 562 · upkeep 424 · charges 2347 · occupation 15 · blockade 351 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Austria, Sweden, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_offensive_cascade: Russia has joined Britain's war against France, honoring their alliance.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 3 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +5 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And Sweden, Sardinia, Austria and Prussia stir at their own designs.
- DIPLO +14 medium/low (diplomatic_dp_regen, witness_strike_recorded ×2, diplomatic_treaty_broken ×2, blockade_begins ×3, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG coalition_declared: The Fourth Austrian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia, Sweden
  - LOG ai_ai_proposal_refused: Austria rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Trust him and he will attack Archduke C…
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Trust him and he will attack Archduke Charles at Franconia instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1280, own corps) vs Archduke Charles (lost 2308) — Reinforcements from Lannes and Murat bolstered Ney's position — though Soult never arrived, Sire.
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 90%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- SPENT 600g on this turn's orders
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Murat. Casualties: Archduke Ch… · Archduke Charles's forces strike with perfect coordination! Brutal stalemate between Archduke Charles and Soult. Heavy … · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Lannes. Casualties: Arc…
  - 🏴 Austria: [!] No word came for Ney, cornered at Swabia — the enemy did not wait. [!] MARSHAL CAPTURED — Ney is taken by Austria at Swabia!
  - ⚔ Archduke Charles (lost 674) vs Davout (lost 2074, own corps) — Ney's timely arrival aided Davout. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 393) vs Murat (lost 8203) — Where was Soult? Murat held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 3054) vs Soult (lost 2251, own corps) — Napoleon arrived to reinforce Soult, but Bernadotte failed to reach the field in time.
  - ⚔ Archduke Charles (lost 1606) vs Lannes (lost 1361, own corps) — Lannes fought without Bernadotte's support. The roads, or the will, proved insufficient.
  - verbs: attack×4, unfortify×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Swabia with 3,331 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
- ORDER Murat [awaiting_response]: Murat is cornered at Munich with 1,867 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Swabia with 3,331 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Munich with 1,867 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 62293 · net -4253 · threat 52 · provinces 27 (+0) · ceiling 26245 · army 28325 · vassals Holland 100 · Switzerland 98
  - NET income 2453 · trade 561 · admin 50 · tribute 562 · upkeep 216 · charges 7114 · contributions 93 · occupation 15 · blockade 351 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 14,828 men ashore at Andalusia.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_dp_regen, sovereign_takes_field, paymaster_subsidy)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, fortify` → ✗ Soult cannot fortify while engaged with enemy forces! Enemy present: Archduke Charles. Attack or retreat first.
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's attack meets fierce resistance. Archduke Charles gains the advantage over Davout. Casualties: Archdu… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke Ch… · ArchdukeCharles holds them at Lorraine while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: Casualties: Archduke Charles 783, Davout's army 3,941. Both armies remain in the field. Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 783) vs Davout (lost 1366, own corps) — A grievous defeat for Davout, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 409) vs Bernadotte (lost 3359) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 103) vs Napoleon (lost 1320) — A grievous defeat for Napoleon, Sire. The losses are severe.
  - verbs: attack×3
- LEDGER treasury 57191 · net -4262 · threat 50 · provinces 26 (-1) · ceiling 24096 · army 18873 · vassals Holland 100 · Switzerland 100
  - NET income 2329 · trade 561 · admin 50 · tribute 562 · upkeep 136 · charges 7108 · contributions 79 · blockade 351 · admiralty 90
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Lannes, fortify` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Davout. Casualties: Archduk… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Soult. Casualties: Arch… · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Bernadotte. Casualties: Archdu… · ArchdukeCharles holds them at Orleanais while allies attack from Lorraine! (+1 coordination)
  - 🏴 Austria: [!] MARSHAL CAPTURED — Davout is taken by Austria at Lorraine!
  - 🏴 Austria: [!] Soult's troops are BROKEN (morale 0%)! FORCED RETREAT! Lorraine has been captured by Austria!
  - ⚔ Archduke Charles (lost 95) vs Davout (lost 1003) — Davout's army has been badly mauled. Archduke Charles proved the stronger force today. And Davout was taken on that fie…
  - ⚔ Archduke Charles (lost 283) vs Soult (lost 4315) — Soult's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 114) vs Bernadotte (lost 1732) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 45) vs Napoleon (lost 477) — The line gave way. Napoleon is falling back, and not in good order.
  - verbs: attack×4
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Orleanais — 832 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Orleanais — 832 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 51148 · net -4947 · threat 48 · provinces 25 (-1) · ceiling 19916 · army 8558 · vassals Holland 100 · Switzerland 100
  - NET income 2235 · trade 561 · admin 50 · tribute 562 · upkeep 64 · charges 7785 · contributions 65 · blockade 351 · admiralty 90
- DISPATCH: Sire — Lorraine has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of 39,498 stands there. A garrison you detach (3,000 men) holds a province against a march…
  - TURN EVENTS 4
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Marshal Davout is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, unfortify` → ✗ Soult is not currently fortified.
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Bernadotte commands our foot at Burgundy — march …
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Soult. Casualties: Archduke Cha… · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Bernadotte. Casualties: Archdu…
  - 🏴 Britain: Wellesley moves from Aragon to Bearn. Bearn falls to Britain!
  - 🏴 Austria: [!] Soult's troops are BROKEN (morale 0%)! FORCED RETREAT! Orleanais has been captured by Austria!
  - ⚔ Archduke Charles (lost 170) vs Soult (lost 2987) — The toll on Soult's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 72) vs Bernadotte (lost 1081) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, move×1
- LEDGER treasury 45786 · net -4465 · threat 45 · provinces 23 (-2) · ceiling 18686 · army 4425 · vassals Holland 100 · Switzerland 100
  - NET income 2086 · trade 561 · admin 50 · tribute 562 · upkeep 32 · charges 7215 · contributions 36 · blockade 351 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - TURN EVENTS 3
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 14 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Britain (Defensive Alliance)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 15 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 15 approaches from Britain and Austria are rebuffed (defensive alliance)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, fortify` → ✗ Marshal Davout is a prisoner of Austria, Sire — no order can reach him until his release.
  - saved `CMD-M_t40` → Game saved: CMD-M_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 6 actions, 5 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Soult. Casualties: Archduke… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke Ch… · ArchdukeCharles marches from Limousin into Berry unopposed! (998 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,968 troops.…
  - 🏴 Austria: [!] Soult's troops are BROKEN (morale 0%)! FORCED RETREAT! Burgundy has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Limousin. (1,029 lost to march) Limousin has been captured by Austria!
  - 🏴 Austria: ArchdukeCharles marches from Limousin into Berry unopposed! (998 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -119g, France -150g. Captured: France → Austria
  - ⚔ Archduke Charles (lost 69) vs Soult (lost 1468) — A grievous defeat for Soult, Sire. The losses are severe. And Soult was taken on that field — Austria holds him.
  - ⚔ Archduke Charles (lost 31) vs Bernadotte (lost 659) — Bernadotte was driven from the field. His men are scattered.
  - verbs: attack×5, grant_dotation×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 41557 · net -3277 · threat 42 · provinces 19 (-4) · ceiling 19046 · army 679 · vassals Holland 100 · Switzerland 100
  - NET income 1750 · trade 561 · admin 50 · tribute 562 · charges 5759 · blockade 351 · admiralty 90
- DISPATCH: Sire — Burgundy has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of 34,358 stands there. A garrison you detach (3,000 men) holds a province against a march…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Sardinia (DEFENSIVE ALLIANCE → NON AGGRESSION)

---
finished: **completed** · commands 200 · popups 46 · battles 33
