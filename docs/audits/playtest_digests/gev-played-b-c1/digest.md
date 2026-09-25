# Playtest digest — gev-played-cB1

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `196c4ee545c1`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `vassalize Bavaria` → ✓ Bavaria has become a Satellite vassal of France (loyalty: 60). Marshals assimilated: Deroy.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march, up to 96,789 if every corps arrives) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1850, own corps) vs Mack (lost 15045) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat, Bernadotte and Deroy ne…
- CMD `Lannes, attack Mack` → ✓ MUSTER — Lannes (16,612; 78,288 if all march, up to 94,769 if every corps arrives) vs Mack (36,955 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 792, own corps) vs Mack (lost 21795) — Soult, Murat, Bernadotte and Deroy never reached the guns. The battle was decided without them, Sire. And Mack was take…
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (308 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on bo…
  - ⚔ Archduke Charles (lost 4612) vs Massena (lost 5422) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2191 · net +2162 · threat 89 · provinces 28 · ceiling 52700 · army 191250 · vassals Bavaria 65 · Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 3400 · trade 275 · admin 50 · tribute 1339 · upkeep 2666 · charges 8 · blockade 138 · admiralty 90
- DISPATCH: Sire — Marshal Mack of Austria is taken at Swabia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +7 medium/low (diplomatic_carved_vassal_created, diplomatic_we_threshold, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, move to Munich` → ✓ Ney moves from Swabia to Munich (396 lost to march)
- CMD `Davout, move to Munich` → ✓ Davout moves from Swabia to Munich (588 lost to march)
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Swabia to Munich (301 lost to march)
- CMD `Murat, move to Munich` → ✓ Murat moves from Swabia to Munich (467 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4599 · net +2240 · threat 87 · provinces 28 (+0) · ceiling 53282 · army 186084 · vassals Bavaria 70 · Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 3400 · trade 350 · admin 50 · tribute 1348 · upkeep 2524 · charges 119 · blockade 175 · admiralty 90
- DISPATCH: Supply cost you 3,414 men, at Munich.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_treaty_signed ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 15 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, ma…
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (900 lost to march)
- CMD `Massena, move to Piedmont` → ✓ Massena moves from Milan to Piedmont (2,194 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 3 ended. Turn 4 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,380 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,322 troops in the…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -66g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - verbs: attack×2, stance_change×1, fortify×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 9891) vs Archduke John (lost 776, own corps) — Murat stood alone, Sire. Ney, Lannes and Deroy never came.
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6756 · net +2420 · threat 85 · provinces 28 (+0) · ceiling 48465 · army 170543 · vassals Bavaria 73 · Holland 98 · Kingdom of Italy 98 · Switzerland 94
  - NET income 3400 · trade 437 · admin 50 · tribute 1161 · upkeep 2044 · charges 275 · blockade 219 · admiralty 90
- DISPATCH: Sire — Murat was mauled at Tyrol: half of his corps — 9,891 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 1358 gold.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia and Naples (open borders agreement)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → reject_settlement_offer
- CMD `Soult, move to Munich` → ✓ Soult moves from Swabia to Munich (1,641 lost to march)
- CMD `Bernadotte, move to Munich` → ✓ Bernadotte moves from Franconia to Munich (340 lost to march)
- CMD `Deroy, move to Munich` → ✓ Deroy moves from Franconia to Munich (616 lost to march)
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'Sire, we have the advantage. Let me strike!'
  - POPUP objection: Massena, Massena firmly objects: 'Sire, we have the advantage. Let me strike!' → insist
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, form_square×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 9615 · net +2585 · threat 83 · provinces 28 (+0) · ceiling 51852 · army 160360 · vassals Bavaria 78 · Holland 98 · Kingdom of Italy 98 · Switzerland 92
  - NET income 3400 · trade 512 · admin 50 · tribute 1163 · upkeep 1728 · charges 466 · blockade 256 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Soult, Lannes, Murat, Bernadotte and Deroy stand 117,752 men at Munich, which feeds 37,500. 80,252 too many. 13,408 men lost in 3 turns. Bavaria's magazines feed us as our own — t…
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

---
finished: **completed** · commands 23 · popups 14 · battles 4
