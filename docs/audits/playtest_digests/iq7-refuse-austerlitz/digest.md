# Playtest digest — refuse_austerlitz

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "refuse"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march, up to 96,789 if every corps arrives) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1984, own corps) vs Mack (lost 14668) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 action(s) unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's attack meets fierce resistance. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Arch…
  - ⚔ Archduke Charles (lost 2305) vs Bernadotte (lost 2855, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: PEACE → OPEN_BORDERS with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2491 · net +2342 · threat 75 · provinces 28 · ceiling 55220 · army 173887 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 3400 · trade 400 · admin 50 · tribute 937 · upkeep 2134 · charges 21 · blockade 200 · admiralty 90
- DISPATCH: Supply cost you 1,854 men, at Franconia and Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,462; 91,455 if all march, up to 102,370 if every corps arrives) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 508, own corps) vs Mack (lost 22412) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,385; 27,191 if all march, up to 32,599 if every corps arrives) vs Mack (substantial force) at Tyrol — the balance of force looks even.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1797, own corps) vs Archduke John (lost 2801) — Reinforcement from Ney kept Davout standing, Sire — but neither side yielded the ground.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 action(s) unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,400 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 964) vs Bernadotte (lost 8480) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1529) vs Deroy (lost 7921) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2014) vs Murat (lost 6543) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4580 · net +2825 · threat 81 · provinces 28 (+0) · ceiling 34500 · army 147065 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 92
  - NET income 3382 · trade 450 · admin 50 · tribute 937 · upkeep 1354 · charges 243 · contributions 82 · blockade 225 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (14,366; 63,246 if all march, up to 86,453 if every corps arrives) vs Mack (12,704 men) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 276, own corps) vs Mack (lost 8400, own corps) — Davout, Massena and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was taken on t…
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (165 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 644 gold. Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 action(s) unused) Turn 4 begins!
- SPENT 644g on this turn's orders
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Franche-Comte into Franche-Comte unopposed! (1,168 lost to march) Captured: France → Austr… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A… · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles marches from Franche-Comte into Franche-Comte unopposed! (1,168 lost to march) Captured: France → Austria
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Munich!
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 123) vs Bernadotte (lost 3043) — Not one corps reached Bernadotte. Ney was expected; Bernadotte fought the battle single-handed. And Bernadotte was take…
  - ⚔ Archduke Charles (lost 521) vs Deroy (lost 6263) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, stance_change×1, fortify×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 3518, own corps) vs Archduke Charles (lost 2216) — Lannes arrived to reinforce Murat, but Soult failed to reach the field in time.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6595 · net +2854 · threat 91 · provinces 29 (+1) · ceiling 33115 · army 131426 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 87
  - NET income 3355 · trade 449 · admin 50 · tribute 937 · upkeep 1024 · charges 494 · occupation 104 · blockade 225 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 8
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #10 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #11 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (6 pair(s) resolved). → display-only
- CMD `Ney, attack Mack` → ✗ We are not at war with Austria, Sire — Mack may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 action(s) unused) Turn 5 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 10263 · net +3413 · threat 45 · provinces 29 (+0) · ceiling 91523 · army 132573 · vassals Holland 91 · Kingdom of Italy 92 · Switzerland 85
  - NET income 3357 · trade 560 · admin 50 · tribute 937 · upkeep 1040 · charges 347 · occupation 104
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon stand 70,228 men at Tyrol, which feeds 30,000. 40,228 too many. 8,091 men lost in 2 turns. No depot may be laid at Tyrol — region stability too low (45/100). …
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 91 to 45.
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #12 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #13 → reconsider
- CMD `Lannes, attack Mack` → ✗ We are not at war with Austria, Sire — Mack may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (117 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action(s) unused) Turn 6 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +5 more court(s) not listed
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14136 · net +3827 · threat 45 · provinces 29 (+0) · ceiling 333000 · army 126826 · vassals Holland 89 · Kingdom of Italy 90 · Switzerland 83
  - NET income 3477 · trade 560 · admin 50 · tribute 937 · upkeep 992 · charges 145 · occupation 60
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon stand 66,711 men at Tyrol, which feeds 30,000. 36,711 too many. 11,608 men lost in 3 turns. A supply depot at Tyrol would ease it; Milan can feed 75,000 more …
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 6 — Early December 1805
  - MAILBOX #9 Holland incoming_proposal: Holland — A Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #14 → refuse the petition
  - POPUP diplomatic_dialogue: Holland, client_petition → (stale passthrough — #14 already answered this chain)
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 8.
  - POPUP proposal_result: Holland's petition for relief is refused: loyalty −10 (89 → 79); standing 0 → -20 (-1 loyalty a turn). Nothing is charged. → display-only
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 300 gold (unstable region premium). Morale: 94% -> 89%
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action(s) unused) Turn 7 begins!
- SPENT 300g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, grant_dotation×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #15 → refuse the petition
  - POPUP proposal_result: Kingdom of Italy's petition for Tyrol is refused: loyalty −10 (88 → 78); standing 0 → -20 (-1 loyalty a turn). Nothing is charged. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 17654 · net +3798 · threat 45 · provinces 29 (+0) · ceiling 334083 · army 125441 · vassals Holland 76 · Kingdom of Italy 78 · Switzerland 81
  - NET income 3482 · trade 560 · admin 50 · tribute 937 · upkeep 984 · charges 187 · occupation 60
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Holland rebuffs Austria (defensive alliance)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 7.
- CMD `Davout, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, attack Archduke Charles` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #16 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #17 → reconsider
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 action(s) unused) Turn 8 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, grant_dotation×1, grant_pension×1
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Ney (120g/turn); Davout (120g/turn); Lannes (40g/turn); Massena …
  - POPUP diplomatic_dialogue: Switzerland, client_petition #18 → refuse the petition
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (79 → 69); standing 0 → -20 (-1 loyalty a turn). Nothing is charged. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 21496 · net +3256 · threat 45 · provinces 29 (+0) · ceiling 292750 · army 121338 · vassals Holland 73 · Kingdom of Italy 75 · Switzerland 69
  - NET income 3486 · trade 560 · admin 50 · tribute 937 · upkeep 944 · charges 233 · occupation 60 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 4 turns over what Tyrol can feed. 9,707 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000 …
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.'
  - POPUP objection: Davout, Davout firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' → trust
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Tyr…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 24883 · net +3346 · threat 45 · provinces 29 (+0) · ceiling 303666 · army 117486 · vassals Holland 70 · Kingdom of Italy 72 · Switzerland 66
  - NET income 3555 · trade 560 · admin 50 · tribute 937 · upkeep 912 · charges 274 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 5 turns over what Tyrol can feed. 8,927 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000 …
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 8
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Austria (defensive alliance)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 345…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 action(s) unused) Turn 10 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 27877 · net +3324 · threat 45 · provinces 29 (+0) · ceiling 304833 · army 116798 · vassals Holland 67 · Kingdom of Italy 69 · Switzerland 63
  - NET income 3561 · trade 560 · admin 50 · tribute 937 · upkeep 904 · charges 310 · occupation 30 · rentes 540
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 15,702 men at Paris, and nobody has gone to collect them.
  - TURN EVENTS 7
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Davout, fortify` → ✗ Davout is already fortified at Tyrol (+12% defense).
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 31223 · net +3306 · threat 45 · provinces 29 (+0) · ceiling 306666 · army 113315 · vassals Holland 64 · Kingdom of Italy 66 · Switzerland 60
  - NET income 3567 · trade 560 · admin 50 · tribute 937 · upkeep 888 · charges 350 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 7 turns over what Tyrol can feed. 7,625 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000 …
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #19 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #20 → reconsider
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action(s) unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 34575 · net +3312 · threat 45 · provinces 29 (+0) · ceiling 310500 · army 110017 · vassals Holland 61 · Kingdom of Italy 63 · Switzerland 57
  - NET income 3573 · trade 560 · admin 50 · tribute 937 · upkeep 848 · charges 390 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 8 turns over what Tyrol can feed. 7,079 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000 …
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 38% -> 38%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action(s) unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 37675 · net +3285 · threat 45 · provinces 29 (+0) · ceiling 311416 · army 109830 · vassals Holland 58 · Kingdom of Italy 60 · Switzerland 54
  - NET income 3576 · trade 560 · admin 50 · tribute 937 · upkeep 840 · charges 428 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 6 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Holland rebuffs Austria (defensive alliance)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #21 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #22 → reconsider
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 action(s) unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 40971 · net +3257 · threat 43 · provinces 29 (+0) · ceiling 312333 · army 106797 · vassals Holland 55 · Kingdom of Italy 57 · Switzerland 51
  - NET income 3579 · trade 560 · admin 50 · tribute 937 · upkeep 832 · charges 467 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 10 turns over what Tyrol can feed. 6,146 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Tyrol and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 action(s) unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 44263 · net +3252 · threat 41 · provinces 29 (+0) · ceiling 315250 · army 103907 · vassals Holland 52 · Kingdom of Italy 54 · Switzerland 48
  - NET income 3582 · trade 560 · admin 50 · tribute 937 · upkeep 800 · charges 507 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 11 turns over what Tyrol can feed. 5,746 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000…
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Austria (defensive alliance)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 93%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 action(s) unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 47296 · net +3219 · threat 39 · provinces 29 (+0) · ceiling 315500 · army 104086 · vassals Holland 49 · Kingdom of Italy 51 · Switzerland 40
  - NET income 3585 · trade 560 · admin 50 · tribute 937 · upkeep 800 · charges 543 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 9 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action(s) unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 50526 · net +3191 · threat 37 · provinces 29 (+0) · ceiling 316416 · army 101389 · vassals Holland 41 · Kingdom of Italy 48 · Switzerland 32
  - NET income 3588 · trade 560 · admin 50 · tribute 937 · upkeep 792 · charges 582 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 13 turns over what Tyrol can feed. 5,057 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000…
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action(s) unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 53744 · net +3180 · threat 35 · provinces 29 (+0) · ceiling 318666 · army 98804 · vassals Holland 33 · Kingdom of Italy 40 · Switzerland 24
  - NET income 3591 · trade 560 · admin 50 · tribute 937 · upkeep 768 · charges 620 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 14 turns over what Tyrol can feed. 4,759 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000…
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest ×2)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Tyrol (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 90% -> 78%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 action(s) unused) Turn 19 begins!
- SPENT 170g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 56734 · net +3147 · threat 33 · provinces 29 (+0) · ceiling 318916 · army 99155 · vassals Holland 25 · Kingdom of Italy 32 · Switzerland 16
  - NET income 3594 · trade 560 · admin 50 · tribute 937 · upkeep 768 · charges 656 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 12 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 7
- DIPLO +7 medium/low (diplomatic_vassal_courting ×3, diplomatic_dp_regen, diplomatic_vassal_unrest ×3)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 action(s) unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 59916 · net +3144 · threat 31 · provinces 29 (+0) · ceiling 321833 · army 96618 · vassals Holland 17 · Kingdom of Italy 24 · Switzerland 8
  - NET income 3597 · trade 560 · admin 50 · tribute 937 · upkeep 736 · charges 694 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 16 turns over what Tyrol can feed. 4,560 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000…
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest ×2)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: Switzerland #23 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Switzerland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 action(s) unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 61412 · net +1443 · threat 19 · provinces 29 (+0) · ceiling 102397 · army 94184 · vassals Holland 0 · Kingdom of Italy 6
  - NET income 3600 · trade 560 · admin 50 · tribute 712 · upkeep 728 · charges 2091 · occupation 30 · admiralty 90 · rentes 540
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Holland is on the verge of rebellion!
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_refuses_call: Holland refuses France's call to arms against Switzerland — loyalty 9.
  - RAIL diplomatic_vassal_refuses_call: KingdomOfItaly refuses France's call to arms against Switzerland — loyalty 16.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - RAIL +1 more
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +5 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
  - POPUP vassal_rebellion_imminent: Holland #24 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Holland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 action(s) unused) Turn 22 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, recruit×1
- ENVOYS WAITING 1 · Austria ultimatum demand
- LEDGER treasury 60925 · net +552 · threat 0 · provinces 29 (+0) · ceiling 75281 · army 94788 · vassals none
  - NET income 3600 · trade 560 · admin 50 · upkeep 736 · charges 2262 · occupation 30 · admiralty 90 · rentes 540
- DISPATCH: Sire — Holland is no longer ours. Switzerland's gold bought them.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Switzerland's gold turns Holland against France.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — the Kingdom of Italy has rebelled against France. It is war.
  - TURN EVENTS 7
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, sovereign_takes_field, agenda_shift ×2, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_broke_free: Vassal rebellion: KingdomOfItaly has broken free of France. War.

## Turn 22 — Early August 1806
  - MAILBOX #12 Austria incoming_ultimatum: Austria — Ultimatum → activated
  - POPUP diplomatic_dialogue: Austria, ultimatum_demand #26 → defy
  - POPUP diplomatic_dialogue: Austria, ultimatum_demand → (stale passthrough — #26 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP proposal_result: You have defied Austria's ultimatum. Their court will not forget it — expect their weight behind the next coalition. → display-only
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 61312 · net +371 · threat 0 · provinces 29 (+0) · ceiling 70221 · army 92484 · vassals none
  - NET income 3600 · trade 560 · admin 50 · upkeep 712 · charges 2467 · occupation 30 · admiralty 90 · rentes 540
- DISPATCH: Sire — Kingdom of Italy is no longer ours. They have rebelled, and it is war.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action(s) unused) Turn 24 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos assaults the Milan garrison! Garrison collapses (7,814 -> 0). Castanos loses 2,170 troops in the assault. Cast…
  - 🏴 Spain: [Materiel] Guns, horses and stores lost with the fallen: Spain -108g, Kingdom of Italy -165g. Captured: KingdomOfItaly -> Spain
  - verbs: fortify×2, attack×1
- ENVOYS WAITING 1 · Switzerland settlement offer
- LEDGER treasury 61529 · net +208 · threat 0 · provinces 29 (+0) · ceiling 66151 · army 90266 · vassals none
  - NET income 3600 · trade 572 · admin 50 · upkeep 688 · charges 2666 · occupation 30 · admiralty 90 · rentes 540
- DISPATCH: Sire — Kingdom of Italy is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Spain rebuffs Sardinia (defensive alliance)

## Turn 24 — Early September 1806
  - MAILBOX #13 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #29 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Holland + Switzerland (4 pair(s) resolved). → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 93%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 action(s) unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 63573 · net +2242 · threat 1 · provinces 29 (+0) · ceiling 250333 · army 91068 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 696 · charges 738 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 21 turns over what Tyrol can feed. 3,584 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 66,739…
  - RAIL settlement_summary: Settlement of Switzerland + Holland vs France + Spain: settlement ratified.
  - RAIL allegiance_in_play: The allegiance of Holland is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Spain rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action(s) unused) Turn 26 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, unfortify×1
- LEDGER treasury 65823 · net +2223 · threat 2 · provinces 29 (+0) · ceiling 251000 · army 88947 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 688 · charges 765 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 22 turns over what Tyrol can feed. 3,403 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 66,739…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 68062 · net +2212 · threat 3 · provinces 29 (+0) · ceiling 252333 · army 86899 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 672 · charges 792 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 20 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 58% -> 53%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action(s) unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, recruit×1, fortify×1
- LEDGER treasury 70043 · net +2180 · threat 4 · provinces 29 (+0) · ceiling 251666 · army 87861 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 680 · charges 816 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 21 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Holland and Austria (Defensive Alliance)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 action(s) unused) Turn 29 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, unfortify×1, recruit×1
- LEDGER treasury 72255 · net +2185 · threat 5 · provinces 29 (+0) · ceiling 254333 · army 85888 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 648 · charges 843 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 22 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Holland is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 74448 · net +2167 · threat 4 · provinces 29 (+0) · ceiling 255000 · army 83976 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 640 · charges 869 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 23 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Tyrol (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 98% -> 82%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 action(s) unused) Turn 31 begins!
- SPENT 170g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, fortify×1
- LEDGER treasury 76406 · net +2128 · threat 3 · provinces 29 (+0) · ceiling 253666 · army 84991 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 656 · charges 892 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 24 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Spain rebuffs Sardinia (design ask)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action(s) unused) Turn 32 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, unfortify×1
- LEDGER treasury 78542 · net +2110 · threat 2 · provinces 29 (+0) · ceiling 254333 · army 83071 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 648 · charges 918 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 25 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 action(s) unused) Turn 33 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 80684 · net +2116 · threat 1 · provinces 29 (+0) · ceiling 257000 · army 81214 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 616 · charges 944 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 26 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_ai_ai_treaty)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 38% of active European bloc power.
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action(s) unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, fortify×1
- LEDGER treasury 82410 · net +2072 · threat 0 · provinces 29 (+0) · ceiling 255000 · army 82343 · vassals none
  - NET income 3600 · trade 596 · admin 50 · upkeep 640 · charges 964 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 27 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 37% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 action(s) unused) Turn 35 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, unfortify×1
- LEDGER treasury 84448 · net +2013 · threat 0 · provinces 29 (+0) · ceiling 252166 · army 80518 · vassals none
  - NET income 3600 · trade 546 · admin 50 · upkeep 624 · charges 989 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 28 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action(s) unused) Turn 36 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 86477 · net +2005 · threat 0 · provinces 29 (+0) · ceiling 253500 · army 78737 · vassals none
  - NET income 3600 · trade 546 · admin 50 · upkeep 608 · charges 1013 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 29 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 93%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 action(s) unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, fortify×1
- LEDGER treasury 88259 · net +1983 · threat 0 · provinces 29 (+0) · ceiling 253500 · army 79940 · vassals none
  - NET income 3600 · trade 546 · admin 50 · upkeep 608 · charges 1035 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 30 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: Spain rebuffs Sardinia (design ask)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 action(s) unused) Turn 38 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, unfortify×1
- LEDGER treasury 90242 · net +1960 · threat 0 · provinces 29 (+0) · ceiling 253500 · army 78186 · vassals none
  - NET income 3600 · trade 546 · admin 50 · upkeep 608 · charges 1058 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 31 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 action(s) unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 92226 · net +1960 · threat 0 · provinces 29 (+0) · ceiling 255500 · army 76476 · vassals none
  - NET income 3600 · trade 546 · admin 50 · upkeep 584 · charges 1082 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 32 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 73% -> 65%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 action(s) unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, fortify×1
- LEDGER treasury 93939 · net +1915 · threat 0 · provinces 29 (+0) · ceiling 253500 · army 77747 · vassals none
  - NET income 3600 · trade 546 · admin 50 · upkeep 608 · charges 1103 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 33 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 action(s) unused) Turn 41 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, unfortify×1
- LEDGER treasury 95886 · net +1924 · threat 0 · provinces 29 (+0) · ceiling 256166 · army 76059 · vassals none
  - NET income 3600 · trade 546 · admin 50 · upkeep 576 · charges 1126 · occupation 30 · rentes 540
- DISPATCH: Sire — the levy has stood open 34 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

---
finished: **completed** · commands 200 · popups 49 · battles 11
