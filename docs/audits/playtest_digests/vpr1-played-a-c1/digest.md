# Playtest digest — vpr1-played-a-c1

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "breakout", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "decline_from": "Hanover,Austria"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `08ed3d374c35` (dirty) · content `ac2f6d51ede2` · driver `196c4ee545c1`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `declare war on Hanover` → ✓ Choose your war purpose against Hanover.
  - POPUP diplomatic_dialogue: war_purpose_selection #1 → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Hanover. Our threat level stands at 70 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Hanover → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #2 → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Hanover! Holland follows France into the war against Hanover! KingdomOfItaly follows France into the war against Hanover! Switzerland follows France into the war against Hanover! → display-only
- CMD `vassalize Bavaria` → ✓ Bavaria has become a Satellite vassal of France (loyalty: 60). Marshals assimilated: Deroy.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1850, own corps) vs Mack (lost 15045) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat, Bernadotte and Deroy ne…
- CMD `Davout, attack Mack` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will adopt DEFENSIVE stance instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will adopt DEFENSIVE stance instead.) → insist
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 803, own corps) vs Mack (lost 15924) — Davout fought without Soult, Murat and Deroy's support. The roads, or the will, proved insufficient. And Mack was taken…
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Murat, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual…
  - ⚔ Archduke Charles (lost 3624, own corps) vs Massena (lost 6504) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Denmark open borders · Hesse open borders
- LEDGER treasury 2121 · net +2060 · threat 97 · provinces 28 · ceiling 50247 · army 193533 · vassals Bavaria 64 · Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 3400 · trade 200 · admin 50 · tribute 1339 · upkeep 2734 · charges 5 · blockade 100 · admiralty 90
- DISPATCH: Sire — Marshal Mack of Austria is taken at Swabia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_war_declared: France has declared war on Hanover, with 2 allied courts poised to follow.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +7 medium/low (diplomatic_carved_vassal_created, diplomatic_we_threshold, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 2 — Early October 1805
  - LETTER Denmark: Open Borders Agreement → accept
  - LETTER Hesse: Open Borders Agreement → accept
- CMD `Ney, move to Munich` → ✓ Ney moves from Swabia to Munich (443 lost to march)
- CMD `Davout, move to Munich` → ✓ Davout moves from Swabia to Munich (668 lost to march)
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Swabia to Munich (310 lost to march)
- CMD `Murat, move to Munich` → ✓ Murat moves from Franche-Comte to Munich (616 lost to march)
- CMD `Massena, move to Piedmont` → ✗ Not enough actions! Need 1, have 0.
- CMD `Napoleon, move to Munich` → ✗ Not enough actions! Need 1, have 0.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 4489 · net +2202 · threat 95 · provinces 28 (+0) · ceiling 52347 · army 187865 · vassals Bavaria 68 · Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 3400 · trade 325 · admin 50 · tribute 1348 · upkeep 2554 · charges 114 · blockade 163 · admiralty 90
- DISPATCH: Supply cost you 3,631 men, at Munich.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 9 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (defensive alliance)

---
finished: **completed** · commands 15 · popups 11 · battles 3
