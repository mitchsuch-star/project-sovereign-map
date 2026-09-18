# Playtest digest — iq8-cmd-austerlitz

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7d10e20c0073` (dirty) · content `457e8f82bc61` · driver `641a9fcf2c43`
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
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
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
  - POPUP diplomatic_dialogue: Holland, client_petition #14 → grant the petition
  - POPUP diplomatic_dialogue: Holland, client_petition → (stale passthrough — #14 already answered this chain)
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 8.
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); standing 0 → 20 (+1 loyalty a turn). Cost: 1 DP. → display-only
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 300 gold (unstable region premium). Morale: 94% -> 89%
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action(s) unused) Turn 7 begins!
- SPENT 300g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, grant_dotation×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #15 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to Kingdom of Italy. Loyalty +10 (88 → 98); standing 0 → 20 (+1 loyalty a turn). Cost: 1 DP and the province's income. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 17317 · net +3469 · threat 45 · provinces 28 (-1) · ceiling 306333 · army 125441 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 81
  - NET income 3381 · trade 560 · admin 50 · tribute 675 · upkeep 984 · charges 183 · occupation 30
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

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
  - POPUP diplomatic_dialogue: Switzerland, client_petition #18 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (79 → 89); standing 0 → 20 (+1 loyalty a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 20830 · net +2706 · threat 45 · provinces 28 (+0) · ceiling 246250 · army 121338 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 89
  - NET income 3383 · trade 560 · admin 50 · tribute 452 · upkeep 944 · charges 225 · occupation 30 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 4 turns over what Tyrol can feed. 9,707 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army is…
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
- LEDGER treasury 23615 · net +2751 · threat 45 · provinces 28 (+0) · ceiling 252833 · army 117486 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 88
  - NET income 3414 · trade 560 · admin 50 · tribute 453 · upkeep 912 · charges 259 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 5 turns over what Tyrol can feed. 8,927 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army is…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 7
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

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
- LEDGER treasury 26041 · net +2763 · threat 45 · provinces 28 (+0) · ceiling 256250 · army 116798 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 87
  - NET income 3417 · trade 560 · admin 50 · tribute 483 · upkeep 904 · charges 288 · occupation 15 · rentes 540
- DISPATCH: Sire — the establishment stands 13,202 men under the ordinance, and the depots hold 96,242. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 6
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
- LEDGER treasury 28825 · net +2751 · threat 45 · provinces 28 (+0) · ceiling 258000 · army 113315 · vassals Holland 94 · Kingdom of Italy 94 · Switzerland 86
  - NET income 3420 · trade 560 · admin 50 · tribute 485 · upkeep 888 · charges 321 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 7 turns over what Tyrol can feed. 7,625 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army is…
  - TURN EVENTS 4
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
- LEDGER treasury 31621 · net +2762 · threat 45 · provinces 28 (+0) · ceiling 261750 · army 110017 · vassals Holland 93 · Kingdom of Italy 93 · Switzerland 85
  - NET income 3423 · trade 560 · admin 50 · tribute 487 · upkeep 848 · charges 355 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 8 turns over what Tyrol can feed. 7,079 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army is…
  - TURN EVENTS 4
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
- LEDGER treasury 34171 · net +2742 · threat 45 · provinces 28 (+0) · ceiling 262666 · army 109830 · vassals Holland 92 · Kingdom of Italy 92 · Switzerland 84
  - NET income 3426 · trade 560 · admin 50 · tribute 487 · upkeep 840 · charges 386 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 5 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

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
- LEDGER treasury 36924 · net +3057 · threat 43 · provinces 28 (+0) · ceiling 291666 · army 106797 · vassals Holland 91 · Kingdom of Italy 91 · Switzerland 83
  - NET income 3429 · trade 560 · admin 50 · tribute 824 · upkeep 832 · charges 419 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 10 turns over what Tyrol can feed. 6,146 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army i…
  - TURN EVENTS 4
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
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 40016 · net +3055 · threat 41 · provinces 28 (+0) · ceiling 294583 · army 103907 · vassals Holland 90 · Kingdom of Italy 90 · Switzerland 82
  - NET income 3432 · trade 560 · admin 50 · tribute 824 · upkeep 800 · charges 456 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 11 turns over what Tyrol can feed. 5,746 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army i…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 15 — Late April 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — A Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #23 → grant the petition
  - POPUP diplomatic_dialogue: Holland, client_petition → (stale passthrough — #23 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (90 → 100); standing 20 → 40 (+2 loyalty a turn). Cost: 1 DP. → display-only
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 93%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 action(s) unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 42515 · net +2916 · threat 39 · provinces 28 (+0) · ceiling 285500 · army 104086 · vassals Holland 100 · Kingdom of Italy 89 · Switzerland 81
  - NET income 3435 · trade 560 · admin 50 · tribute 712 · upkeep 800 · charges 486 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 8 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 16 — Early May 1806
  - MAILBOX #13 KingdomOfItaly incoming_proposal: Kingdom of Italy — A Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #24 → grant the petition
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition → (stale passthrough — #24 already answered this chain)
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
  - POPUP proposal_result: Kingdom of Italy's tribute is remitted for 8 collections (3896g forgone). Loyalty +10 (89 → 99); standing 20 → 40 (+2 loyalty a turn). Cost: 1 DP. → display-only
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action(s) unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 44955 · net +2411 · threat 37 · provinces 28 (+0) · ceiling 245833 · army 101389 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 80
  - NET income 3438 · trade 560 · admin 50 · tribute 225 · upkeep 792 · charges 515 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 13 turns over what Tyrol can feed. 5,057 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army i…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — A Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #25 → grant the petition
  - POPUP diplomatic_dialogue: Switzerland, client_petition → (stale passthrough — #25 already answered this chain)
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); standing 20 → 40 (+2 loyalty a turn). Cost: 1 DP. → display-only
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action(s) unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 47168 · net +2186 · threat 35 · provinces 28 (+0) · ceiling 229333 · army 98804 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3441 · trade 560 · admin 50 · upkeep 768 · charges 542 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 14 turns over what Tyrol can feed. 4,759 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army i…
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 action(s) unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 49381 · net +2187 · threat 33 · provinces 28 (+0) · ceiling 231583 · army 96325 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3444 · trade 560 · admin 50 · upkeep 744 · charges 568 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 11 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 action(s) unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 51595 · net +2187 · threat 31 · provinces 28 (+0) · ceiling 233833 · army 93943 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3447 · trade 560 · admin 50 · upkeep 720 · charges 595 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 16 turns over what Tyrol can feed. 4,235 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army i…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 action(s) unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 53801 · net +2180 · threat 29 · provinces 28 (+0) · ceiling 235416 · army 91652 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · upkeep 704 · charges 621 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 17 turns over what Tyrol can feed. 4,004 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army i…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 action(s) unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, recruit×1
- LEDGER treasury 55607 · net +2150 · threat 27 · provinces 28 (+0) · ceiling 234750 · army 92389 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · upkeep 712 · charges 643 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 14 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 57773 · net +2477 · threat 25 · provinces 28 (+0) · ceiling 264166 · army 90208 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 337 · upkeep 696 · charges 669 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 19 turns over what Tyrol can feed. 3,593 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army i…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action(s) unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 60282 · net +2966 · threat 23 · provinces 28 (+0) · ceiling 307416 · army 88104 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 824 · upkeep 664 · charges 699 · occupation 15 · rentes 540
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon have been 20 turns over what Tyrol can feed. 3,410 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army i…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 93%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 action(s) unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 63010 · net +3142 · threat 21 · provinces 28 (+0) · ceiling 324833 · army 89012 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 680 · charges 732 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 17 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action(s) unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 66160 · net +3113 · threat 19 · provinces 28 (+0) · ceiling 325500 · army 86990 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 672 · charges 769 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 18 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 69281 · net +3083 · threat 17 · provinces 28 (+0) · ceiling 326166 · army 85033 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 664 · charges 807 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 19 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 58% -> 53%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action(s) unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, recruit×1
- LEDGER treasury 72142 · net +3049 · threat 15 · provinces 28 (+0) · ceiling 326166 · army 86078 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 664 · charges 841 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 20 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 action(s) unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 75223 · net +3044 · threat 13 · provinces 28 (+0) · ceiling 328833 · army 84170 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 632 · charges 878 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 21 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
  - MAILBOX #15 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #26 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance → (stale passthrough — #26 already answered this chain)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 78267 · net +3007 · threat 11 · provinces 28 (+0) · ceiling 328833 · army 82309 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 632 · charges 915 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 22 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 action(s) unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 81290 · net +2987 · threat 9 · provinces 28 (+0) · ceiling 330166 · army 80492 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 616 · charges 951 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 23 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action(s) unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 84277 · net +2951 · threat 7 · provinces 28 (+0) · ceiling 330166 · army 78721 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 616 · charges 987 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 24 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — gold is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 action(s) unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 87260 · net +2947 · threat 5 · provinces 28 (+0) · ceiling 332833 · army 76994 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 584 · charges 1023 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 25 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
  - MAILBOX #16 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #27 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance → (stale passthrough — #27 already answered this chain)
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action(s) unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 89826 · net +2901 · threat 3 · provinces 28 (+0) · ceiling 331500 · army 78250 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 560 · admin 50 · tribute 1049 · upkeep 600 · charges 1053 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 26 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 action(s) unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 92685 · net +2824 · threat 1 · provinces 28 (+0) · ceiling 328000 · army 76547 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 510 · admin 50 · tribute 1049 · upkeep 592 · charges 1088 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 27 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action(s) unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 95517 · net +2798 · threat 0 · provinces 28 (+0) · ceiling 328666 · army 74886 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 510 · admin 50 · tribute 1049 · upkeep 584 · charges 1122 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 28 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
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
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 98101 · net +2775 · threat 0 · provinces 28 (+0) · ceiling 329333 · army 76204 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 510 · admin 50 · tribute 1049 · upkeep 576 · charges 1153 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 29 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 action(s) unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 100876 · net +2742 · threat 0 · provinces 28 (+0) · ceiling 329333 · army 74562 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 510 · admin 50 · tribute 1049 · upkeep 576 · charges 1186 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 30 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 action(s) unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 103634 · net +2725 · threat 0 · provinces 28 (+0) · ceiling 330666 · army 72960 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 510 · admin 50 · tribute 1049 · upkeep 560 · charges 1219 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 31 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 73% -> 65%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 action(s) unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 106120 · net +2679 · threat 0 · provinces 28 (+0) · ceiling 329333 · army 74337 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 510 · admin 50 · tribute 1049 · upkeep 576 · charges 1249 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 32 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 action(s) unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 108831 · net +2679 · threat 0 · provinces 28 (+0) · ceiling 332000 · army 72751 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 90
  - NET income 3450 · trade 510 · admin 50 · tribute 1049 · upkeep 544 · charges 1281 · occupation 15 · rentes 540
- DISPATCH: Sire — the levy has stood open 33 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)

---
finished: **completed** · commands 200 · popups 52 · battles 11
