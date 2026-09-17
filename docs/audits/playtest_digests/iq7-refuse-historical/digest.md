# Playtest digest — refuse_historical

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "refuse"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march, up to 96,789 if every corps arrives) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1850, own corps) vs Mack (lost 15045) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on both…
  - ⚔ Archduke Charles (lost 4958) vs Massena (lost 5043) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: PEACE → OPEN_BORDERS with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2454 · net +2213 · threat 76 · provinces 28 · ceiling 56681 · army 176527 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 3400 · trade 400 · admin 50 · tribute 895 · upkeep 2224 · charges 18 · blockade 200 · admiralty 90
- DISPATCH: Supply cost you 1,099 men, at Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (21,398; 89,873 if all march, up to 99,901 if every corps arrives) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 610, own corps) vs Mack (lost 21832) — Davout and Massena arrived to reinforce Ney, but Napoleon failed to reach the field in time.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,844; 33,229 if all march, up to 44,912 if every corps arrives) vs Mack (large force) at Tyrol — the balance of force looks even.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 8051) vs Archduke Charles (lost 1192, own corps) — Davout stood alone, Sire. Ney never came.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 action(s) unused) Turn 3 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - ⚔ Archduke Charles (lost 1902) vs Bernadotte (lost 5920) — Bernadotte stood alone, Sire. Ney never came.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4502 · net +2657 · threat 82 · provinces 28 (+0) · ceiling 50310 · army 158756 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 3400 · trade 450 · admin 50 · tribute 901 · upkeep 1684 · charges 145 · blockade 225 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Munich. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 14 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 2 more — Bavaria is not forgiven

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (19,952; 52,723 if all march, up to 54,026 if every corps arrives) vs Mack (13,064 men) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 144, own corps) vs Mack (lost 12146) — Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was taken on that field — France ho…
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn(s) remaining.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (166 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 714 gold. Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 action(s) unused) Turn 4 begins!
- SPENT 714g on this turn's orders
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archd… · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeCharl… · ArchdukeCharles holds them at Swabia while allies attack from Franconia! (+1 coordination) · Deroy marches from Bohemia into Franconia unopposed! (174 lost to march) Captured: Austria → Bavaria
  - 🏴 Austria: Casualties: ArchdukeCharles 1,716, Bernadotte's army 6,048. Both armies remain in the field. Franconia has been captured by Austria!
  - 🏴 Austria: Casualties: ArchdukeCharles 1,210, Napoleon's army 4,735. Both armies remain in the field. Swabia has been captured by Austria!
  - 🏴 Bavaria: Deroy moves from Vienna to Bohemia. Bohemia falls to Bavaria!
  - 🏴 Bavaria: Deroy marches from Bohemia into Franconia unopposed! (174 lost to march) Captured: Austria → Bavaria
  - ⚔ Archduke Charles (lost 1716) vs Bernadotte (lost 2434, own corps) — Lannes arrived to reinforce Bernadotte, but Ney failed to reach the field in time.
  - ⚔ Archduke Charles (lost 2539) vs Lannes (lost 1247, own corps) — Reinforcements from Murat bolstered Lannes's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 1210) vs Napoleon (lost 1957, own corps) — Napoleon fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4, move×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6285 · net +2876 · threat 90 · provinces 29 (+1) · ceiling 33615 · army 142401 · vassals Holland 92 · Kingdom of Italy 92 · Switzerland 87
  - NET income 3427 · trade 525 · admin 50 · tribute 905 · upkeep 1176 · charges 450 · occupation 52 · blockade 263 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 1358 gold.
  - TURN EVENTS 10
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #9 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #10 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (7 pair(s) resolved). → display-only
- CMD `Ney, attack Mack` → ✗ We are not at war with Austria, Sire — Mack may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franche-Comte. Defense bonus: +7% (grows +3% per t…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 action(s) unused) Turn 5 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 11370 · net +3470 · threat 45 · provinces 29 (+0) · ceiling 93976 · army 139318 · vassals Holland 90 · Kingdom of Italy 90 · Switzerland 85
  - NET income 3428 · trade 623 · admin 50 · tribute 910 · upkeep 1096 · charges 393 · occupation 52
- DISPATCH: Sire — Ney, Bernadotte and Massena stand 58,548 men at Tyrol, which feeds 30,000. 28,548 too many. 4,441 men lost in 2 turns. No depot may be laid at Tyrol — region stability too low (45/100). Need 5…
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: Gold indemnity: 1358 gold from Britain to France.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 7
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: 10 approaches rebuffed, chiefly from Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 4 approaches from Austria and Bavaria are rebuffed (open borders agreement)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 90 to 45.

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #11 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #12 → reconsider
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn(s) remaining.
- CMD `Soult, move to Swabia` → ✗ Cannot enter Swabia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, move to Swabia` → ✗ Cannot enter Swabia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 3 action(s) unused) Turn 6 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 15234 · net +3818 · threat 45 · provinces 29 (+0) · ceiling 333333 · army 136392 · vassals Holland 88 · Kingdom of Italy 88 · Switzerland 83
  - NET income 3487 · trade 623 · admin 50 · tribute 914 · upkeep 1068 · charges 158 · occupation 30
- DISPATCH: Sire — Ney, Bernadotte and Massena stand 56,543 men at Tyrol, which feeds 30,000. 26,543 too many. 6,446 men lost in 3 turns. A supply depot at Tyrol would ease it; Milan can feed 75,000 more and Boh…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 6 — Early December 1805
  - MAILBOX #9 Holland incoming_proposal: Holland — A Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → refuse the petition
  - POPUP diplomatic_dialogue: Holland, client_petition → (stale passthrough — #13 already answered this chain)
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 8.
  - POPUP proposal_result: Holland's petition for relief is refused: loyalty −10 (88 → 78); standing 0 → -20 (-1 loyalty a turn). Nothing is charged. → display-only
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 205 gold. Morale: 94% -> 89%
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action(s) unused) Turn 7 begins!
- SPENT 205g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #14 → refuse the petition
  - POPUP proposal_result: Kingdom of Italy's petition for Tyrol is refused: loyalty −10 (86 → 76); standing 0 → -20 (-1 loyalty a turn). Nothing is charged. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 18827 · net +3778 · threat 45 · provinces 29 (+0) · ceiling 333583 · army 136551 · vassals Holland 75 · Kingdom of Italy 76 · Switzerland 81
  - NET income 3489 · trade 623 · admin 50 · tribute 919 · upkeep 1072 · charges 201 · occupation 30
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 7.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 3). Moved to Munich. Route: Munich -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ We are not at war with Austria, Sire — Archduke Charles may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 action(s) unused) Turn 8 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turn(s) remaining).
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Ney (120g/turn); Davout (80g/turn); Lannes (40g/turn); Massena (…
  - POPUP diplomatic_dialogue: Switzerland, client_petition #15 → refuse the petition
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (79 → 69); standing 0 → -20 (-1 loyalty a turn). Nothing is charged. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 22648 · net +3295 · threat 45 · provinces 29 (+0) · ceiling 297166 · army 133547 · vassals Holland 72 · Kingdom of Italy 73 · Switzerland 69
  - NET income 3492 · trade 623 · admin 50 · tribute 923 · upkeep 1036 · charges 247 · occupation 30 · rentes 480
- DISPATCH: Sire — Ney, Bernadotte and Massena have been 4 turns over what Tyrol can feed. 5,650 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Milan can feed 75,000 more a…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ We are not at war with Austria, Sire — Archduke Charles may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Tyr…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shi…
- CMD `Massena, move to Milan` → ✓ Massena moves from Tyrol to Milan (847 lost to march)
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, garrison×1, wait×1
- LEDGER treasury 26009 · net +3320 · threat 45 · provinces 29 (+0) · ceiling 302666 · army 131775 · vassals Holland 69 · Kingdom of Italy 72 · Switzerland 66
  - NET income 3526 · trade 623 · admin 50 · tribute 928 · upkeep 1024 · charges 288 · occupation 15 · rentes 480
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Franche-Comte (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Co…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 action(s) unused) Turn 10 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 28950 · net +3271 · threat 45 · provinces 29 (+0) · ceiling 301500 · army 133868 · vassals Holland 66 · Kingdom of Italy 71 · Switzerland 63
  - NET income 3528 · trade 623 · admin 50 · tribute 932 · upkeep 1044 · charges 323 · occupation 15 · rentes 480
- DISPATCH: Lannes's fortifications decay: 8% → 6%
  - TURN EVENTS 7
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Tyrol to Franconia (163 lost to march, 326 to enemy harassment)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Bohemia, Franconia, Moravia, Munich.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 action(s) unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
- LEDGER treasury 32249 · net +3260 · threat 45 · provinces 29 (+0) · ceiling 303833 · army 132492 · vassals Holland 63 · Kingdom of Italy 70 · Switzerland 60
  - NET income 3531 · trade 623 · admin 50 · tribute 937 · upkeep 1024 · charges 362 · occupation 15 · rentes 480
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 approaches from Britain, Russia and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Denmark and Kingdom of Italy rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples and Switzerland rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: KingdomOfItaly rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 10 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Franche-Comte to Franconia (1,034 lost to march, 442 to enemy harassment)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action(s) unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 35529 · net +3240 · threat 45 · provinces 29 (+0) · ceiling 305500 · army 129399 · vassals Holland 60 · Kingdom of Italy 69 · Switzerland 57
  - NET income 3535 · trade 623 · admin 50 · tribute 937 · upkeep 1008 · charges 402 · occupation 15 · rentes 480
- DISPATCH: Lannes's fortifications decay: 3% → 1%
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: KingdomOfItaly rebuffs Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, m…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 0% -> 11%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action(s) unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 38534 · net +3191 · threat 45 · provinces 29 (+0) · ceiling 304416 · army 130759 · vassals Holland 57 · Kingdom of Italy 68 · Switzerland 54
  - NET income 3538 · trade 623 · admin 50 · tribute 937 · upkeep 1024 · charges 438 · occupation 15 · rentes 480
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Holland rebuffs Prussia (defensive alliance)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #16 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #17 → reconsider
- CMD `Davout, move to Franconia` → ✓ Davout moves from Munich to Franconia (144 lost to march, 289 to enemy harassment)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 action(s) unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 41776 · net +3203 · threat 43 · provinces 29 (+0) · ceiling 308666 · army 127789 · vassals Holland 54 · Kingdom of Italy 67 · Switzerland 51
  - NET income 3541 · trade 623 · admin 50 · tribute 937 · upkeep 976 · charges 477 · occupation 15 · rentes 480
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +5 (now 100).
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: KingdomOfItaly rebuffs Prussia (defensive alliance)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 action(s) unused) Turn 15 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 44982 · net +3168 · threat 41 · provinces 29 (+0) · ceiling 308916 · army 125316 · vassals Holland 51 · Kingdom of Italy 66 · Switzerland 48
  - NET income 3544 · trade 623 · admin 50 · tribute 937 · upkeep 976 · charges 515 · occupation 15 · rentes 480
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples and Switzerland rebuff Prussia (defensive alliance)

## Turn 15 — Late April 1806
  - MAILBOX #12 KingdomOfItaly incoming_proposal: Kingdom of Italy — A Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #18 → refuse the petition
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition → (stale passthrough — #18 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP proposal_result: Kingdom of Italy's petition for Tyrol is refused: loyalty −10 (66 → 56); standing -20 → -40 (-2 loyalty a turn). Nothing is charged. → display-only
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 93%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 action(s) unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 47938 · net +3143 · threat 39 · provinces 29 (+0) · ceiling 309833 · army 125882 · vassals Holland 48 · Kingdom of Italy 54 · Switzerland 40
  - NET income 3547 · trade 623 · admin 50 · tribute 937 · upkeep 968 · charges 551 · occupation 15 · rentes 480
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia (137 lost to march)
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 16 ended. Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 51084 · net +3108 · threat 37 · provinces 29 (+0) · ceiling 310083 · army 124220 · vassals Holland 40 · Kingdom of Italy 52 · Switzerland 32
  - NET income 3550 · trade 623 · admin 50 · tribute 937 · upkeep 968 · charges 589 · occupation 15 · rentes 480
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 22).
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action(s) unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 54208 · net +3087 · threat 35 · provinces 29 (+0) · ceiling 311416 · army 122724 · vassals Holland 32 · Kingdom of Italy 50 · Switzerland 24
  - NET income 3550 · trade 623 · admin 50 · tribute 937 · upkeep 952 · charges 626 · occupation 15 · rentes 480
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest ×2)
  - LOG ai_ai_proposal_refused: 9 approaches from Russia, Austria and Prussia are rebuffed (defensive alliance)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 action(s) unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 57319 · net +3074 · threat 33 · provinces 29 (+0) · ceiling 313416 · army 121259 · vassals Holland 24 · Kingdom of Italy 48 · Switzerland 16
  - NET income 3550 · trade 623 · admin 50 · tribute 937 · upkeep 928 · charges 663 · occupation 15 · rentes 480
- DISPATCH: Ney's fortifications decay: 7% → 5%
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest ×2)
  - LOG ai_ai_proposal_refused: Denmark and Kingdom of Italy rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes begins marching to Franconia (distance: 2). Moved to Rhineland. Route: Rhineland -> Frankfurt -> Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 1 action(s) unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ORDER Lannes [active]: Lannes is marching to Franconia (3 turn(s) remaining).
- LEDGER treasury 60393 · net +3037 · threat 31 · provinces 29 (+0) · ceiling 313416 · army 120671 · vassals Holland 16 · Kingdom of Italy 41 · Switzerland 8
  - NET income 3550 · trade 623 · admin 50 · tribute 937 · upkeep 928 · charges 700 · occupation 15 · rentes 480
- DISPATCH: Soult's fortifications decay: 12% → 11%
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Prussia (defensive alliance)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: Switzerland #19 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Switzerland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Lorraine (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 action(s) unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Lannes [continues]: Lannes marches to Frankfurt. 1 region(s) to Franconia.
- LEDGER treasury 61768 · net +1327 · threat 19 · provinces 29 (+0) · ceiling 99443 · army 120006 · vassals Holland 0 · Kingdom of Italy 24
  - NET income 3550 · trade 623 · admin 50 · tribute 712 · upkeep 920 · charges 2103 · occupation 15 · admiralty 90 · rentes 480
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Holland is on the verge of rebellion!
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_alliance_cascade: Bavaria enters the war via alliance with France.
  - RAIL diplomatic_vassal_refuses_call: Holland refuses France's call to arms against Switzerland — loyalty 8.
  - RAIL diplomatic_vassal_refuses_call: KingdomOfItaly refuses France's call to arms against Switzerland — loyalty 34.
  - RAIL +1 more
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +5 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.
  - LOG ai_ai_proposal_refused: 6 courts rebuff Austria (open borders agreement)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
  - POPUP vassal_rebellion_imminent: Holland #20 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Holland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Frankfurt. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 action(s) unused) Turn 22 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 62566 · net +768 · threat 7 · provinces 29 (+0) · ceiling 82546 · army 120006 · vassals Kingdom of Italy 7
  - NET income 3550 · trade 623 · admin 50 · tribute 375 · upkeep 920 · charges 2325 · occupation 15 · admiralty 90 · rentes 480
- DISPATCH: Sire — Holland is no longer ours. Switzerland's gold bought them.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_alliance_cascade: Bavaria enters the war via alliance with France.
  - RAIL diplomatic_vassal_refuses_call: KingdomOfItaly refuses France's call to arms against Holland — loyalty 19.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Switzerland's gold turns Holland against France.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — the Kingdom of Italy is on the verge of rebellion!
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, sovereign_takes_field, agenda_shift)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: KingdomOfItaly #22 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If KingdomOfItaly's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 action(s) unused) Turn 23 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 62840 · net +263 · threat 0 · provinces 29 (+0) · ceiling 69139 · army 120006 · vassals none
  - NET income 3550 · trade 623 · admin 50 · upkeep 920 · charges 2530 · requisitions 75 · occupation 15 · admiralty 90 · rentes 480
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Holland's gold bought them.
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_alliance_cascade: Bavaria enters the war via alliance with France.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Holland's gold turns the Kingdom of Italy against France.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Austria, Spain and Bavaria rebuff Sardinia (defensive alliance)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Frankfurt. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot sh…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action(s) unused) Turn 24 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). Deroy loses 2,500 troops. Garrison holds — 5,000… · Deroy assaults the Milan garrison! Garrison collapses (5,000 -> 0). Deroy loses 1,388 troops in the assault. Deroy marc…
  - 🏴 Bavaria: [Materiel] Guns, horses and stores lost with the fallen: Bavaria -69g, Kingdom of Italy -125g. Captured: KingdomOfItaly -> Bavaria
  - verbs: attack×2, wait×1
- ENVOYS WAITING 1 · Switzerland settlement offer
- LEDGER treasury 62833 · net -7 · threat 0 · provinces 29 (+0) · ceiling 62669 · army 120006 · vassals none
  - NET income 3550 · trade 623 · admin 50 · upkeep 920 · charges 2725 · occupation 15 · admiralty 90 · rentes 480
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - RAIL design_promoted: REVANCHE: Kingdom of Italy will not forgive Bavaria the loss of Milan. A new design hardens in their court.
  - TURN EVENTS 2
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 24 — Early September 1806
  - MAILBOX #13 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #24 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Holland + KingdomOfItaly + Switzerland (9 pair(s) resolved). → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 action(s) unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 64701 · net +2068 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 752 · occupation 15 · rentes 480
- DISPATCH: Davout's fortifications decay: 12% → 11%
  - RAIL settlement_summary: Settlement of Switzerland + Holland + Kingdom of Italy vs France + Spain + Bavaria: settlement ratified.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Revanche — service to the strong is now the length of its tether.
- COURTS: And 4 other courts stir at their own designs.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Holland rebuffs Austria (defensive alliance)
  - LOG design_promoted: REVANCHE: Kingdom of Italy swears to retake Milan — Bavaria is not forgiven

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Frankfurt. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action(s) unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 66769 · net +2043 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 777 · occupation 15 · rentes 480
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Britain, Denmark and Kingdom of Italy rebuff Austria (open borders agreement)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 68812 · net +2019 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 801 · occupation 15 · rentes 480
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Frankfurt. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Frankfurt, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action(s) unused) Turn 28 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 70831 · net +1995 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 825 · occupation 15 · rentes 480
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 action(s) unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 72826 · net +1971 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 849 · occupation 15 · rentes 480
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 42).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Austria, Spain and Bavaria rebuff Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: 5 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Frankfurt. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot sh…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 74797 · net +1947 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 873 · occupation 15 · rentes 480
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 action(s) unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 76744 · net +1924 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 896 · occupation 15 · rentes 480
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Holland rebuffs Austria (defensive alliance)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Frankfurt. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action(s) unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 78668 · net +1900 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 920 · occupation 15 · rentes 480
- DISPATCH: Ney's fortifications have crumbled completely!
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Britain, Denmark and Kingdom of Italy rebuff Austria (open borders agreement)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 action(s) unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 80568 · net +1878 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 942 · occupation 15 · rentes 480
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Frankfurt. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action(s) unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 82446 · net +1855 · threat 0 · provinces 29 (+0) · ceiling 237000 · army 123006 · vassals none
  - NET income 3550 · trade 659 · admin 50 · upkeep 944 · charges 965 · occupation 15 · rentes 480
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 action(s) unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 84263 · net +1795 · threat 0 · provinces 29 (+0) · ceiling 233833 · army 123006 · vassals none
  - NET income 3550 · trade 621 · admin 50 · upkeep 944 · charges 987 · occupation 15 · rentes 480
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Austria, Spain and Bavaria rebuff Sardinia (defensive alliance)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Frankfurt. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot sh…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action(s) unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 86058 · net +1774 · threat 0 · provinces 29 (+0) · ceiling 233833 · army 123006 · vassals none
  - NET income 3550 · trade 621 · admin 50 · upkeep 944 · charges 1008 · occupation 15 · rentes 480
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 action(s) unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 87585 · net +1731 · threat 0 · provinces 29 (+0) · ceiling 231833 · army 126006 · vassals none
  - NET income 3550 · trade 621 · admin 50 · upkeep 968 · charges 1027 · occupation 15 · rentes 480
- DISPATCH: Ney's fortifications have crumbled completely!
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Holland rebuffs Austria (defensive alliance)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Frankfurt. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 action(s) unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 89316 · net +1711 · threat 0 · provinces 29 (+0) · ceiling 231833 · army 126006 · vassals none
  - NET income 3550 · trade 621 · admin 50 · upkeep 968 · charges 1047 · occupation 15 · rentes 480
- DISPATCH: Ney's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Britain, Denmark and Kingdom of Italy rebuff Austria (open borders agreement)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 action(s) unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 91027 · net +1690 · threat 0 · provinces 29 (+0) · ceiling 231833 · army 126006 · vassals none
  - NET income 3550 · trade 621 · admin 50 · upkeep 968 · charges 1068 · occupation 15 · rentes 480
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Frankfurt, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 action(s) unused) Turn 40 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 92717 · net +1670 · threat 0 · provinces 29 (+0) · ceiling 231833 · army 126006 · vassals none
  - NET income 3550 · trade 621 · admin 50 · upkeep 968 · charges 1088 · occupation 15 · rentes 480
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

## Turn 40 — Early May 1807
  - MAILBOX #14 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #25 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance → (stale passthrough — #25 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 action(s) unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 94387 · net +1650 · threat 0 · provinces 29 (+0) · ceiling 231833 · army 126006 · vassals none
  - NET income 3550 · trade 621 · admin 50 · upkeep 968 · charges 1108 · occupation 15 · rentes 480
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria, Spain and Bavaria rebuff Sardinia (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

---
finished: **completed** · commands 200 · popups 47 · battles 9
