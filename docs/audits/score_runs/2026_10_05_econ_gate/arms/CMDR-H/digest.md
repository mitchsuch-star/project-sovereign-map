# Playtest digest — CMDR-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "refuse"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `47eb92ffc944` (dirty) · content `aae077cedc7a` · driver `e498338939cb`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1847, own corps) vs Mack (lost 24408) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult and Bernadotte never arr… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Massena. Casualties: Archduke Charl… · Deroy delivers an effective strike. Deroy gains the advantage over Mack. Casualties: Deroy 983, Mack 8,861. Both armies…
  - ⚔ Archduke Charles (lost 3964) vs Massena (lost 6353) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Deroy (lost 983) vs Mack (lost 8861) — Mack stood alone, Sire. Archduke John never came.
  - verbs: attack×2, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 571 · net +359 · threat 77 · provinces 28 · ceiling 9670 · army 174609 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 3236 · blockade 250 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ Ney pursues Mack (at Tyrol). Moves to Franconia. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt,…
- CMD `Davout, attack Mack` → ✓ Davout pursues Mack (at Tyrol). Moves to Franconia. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interru…
- CMD `Soult, move to Alsace` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Alsace today.
- CMD `Murat, move to Franche-Comte` → ✗ Not enough actions! Need 1, have 0 — Murat cannot march to Franche-Comte today.
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Charle…
  - ⚔ Archduke Charles (lost 4330) vs Massena (lost 4342, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 2676) vs Teulie (lost 1357, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×2, wait×1
- ORDER Davout [active]: Davout is pursuing Mack (0 turns remaining).
- ORDER Ney [active]: Ney is pursuing Mack (0 turns remaining).
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 772 · net +636 · threat 75 · provinces 28 (+0) · ceiling 13118 · army 164669 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 829 · upkeep 2912 · blockade 281 · admiralty 90
- DISPATCH: Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 29 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,407; expect about 47,322 with the corps likely to arrive, up to 47,970 if all march) vs Mack (substantial force) at Bohemia — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 299, own corps) vs Mack (lost 15770) — Davout arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. And Mack was taken on that fie…
  - POPUP capture_choice[capture]: Bohemia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (169 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 741 gold (×3 at war) (×1.24 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 741g on this turn's orders
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles struggles in a costly engagement. Brutal stalemate between Archduke Charles and Massena. Heavy casualt… · Archduke Charles's attack meets fierce resistance. Archduke Charles gains the advantage over Teulie. Casualties: Archdu…
  - ⚔ Archduke Charles (lost 3013) vs Massena (lost 3743, own corps) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 1757) vs Teulie (lost 1200, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, wait×1
- ORDER Davout [active]: Davout answered the guns this turn and stands at Bohemia; the pursuit resumes next turn.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 746 · net +1121 · threat 83 · provinces 29 (+1) · ceiling 13580 · army 158721 · vassals Holland 96 · Kingdom of Italy 95 · Switzerland 90
  - NET income 2636 · trade 525 · admin 50 · tribute 799 · upkeep 2400 · occupation 70 · blockade 329 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is taken at Bohemia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples and Bavaria rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 2061 · net +1204 · threat 81 · provinces 29 (+0) · ceiling 14100 · army 157806 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 88
  - NET income 2637 · trade 587 · admin 50 · tribute 802 · upkeep 2338 · charges 6 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign a Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign a Open Borders Agreement

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (19,903; expect about 35,414 with the corps likely to arrive, up to 36,150 if all march) vs Archduke Charles (substantial force) at Tyrol — the balance of f…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 4215, own corps) vs Archduke Charles (lost 1737, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✗ Murat is already in Swabia.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 9 actions, 6 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John launches a decisive assault. Archduke John gains the advantage over Teulie. Casualties: Archduke John 161… · ArchdukeJohn assaults the Munich garrison! Garrison: 10,000 -> 5,771 (-4,229). ArchdukeJohn loses 3,499 troops. Garriso… · ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,771 -> 0). ArchdukeJohn loses 2,385 troops in the assa… · Deroy's forces advance steadily. Brutal stalemate between Deroy and Archduke John. Heavy casualties on both sides: Dero…
  - 🏴 Austria: [!] No word came for Teulie, cornered at Milan — the enemy did not wait. [!] MARSHAL CAPTURED — Teulie is taken by Austria at Milan!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -119g, Bavaria -141g. Captured: Bavaria → Austria
  - ⚔ Archduke John (lost 161) vs Teulie (lost 1798) — A grievous defeat for Teulie, Sire. The losses are severe. And Teulie was taken on that field — Austria holds him.
  - ⚔ Deroy (lost 1810) vs Archduke John (lost 1699) — Archduke John's square formation provided a solid defensive anchor, Sire.
  - ⚔ Deroy (lost 1487) vs Archduke John (lost 1624) — The square held its ground. Archduke John's infantry stood like a fortress on the field.
  - ⚔ Deroy (lost 1319) vs Archduke John (lost 1221) — Archduke John's men formed square and weathered the storm. Discipline held the line.
  - verbs: attack×6, unfortify×1, form_square×1, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 2700 · net +1038 · threat 79 · provinces 29 (+0) · ceiling 15472 · army 147272 · vassals Holland 92 · Kingdom of Italy 81 · Switzerland 82
  - NET income 2734 · trade 587 · admin 50 · tribute 799 · upkeep 2578 · charges 56 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Munich. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +8 medium/low (enemy_marshal_commissioned, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, coercive_demand, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → refuse the petition
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (82 → 72); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Kutuzov is at Hungary, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attac…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Munich instead.) → trust
  - ↳ MUSTER — Lannes (15,578; expect about 52,635 with the corps likely to arrive, up to 53,203 if all march) vs Archduke John (6,266 men) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 311, own corps) vs Archduke John (lost 5088) — Murat, Bernadotte and Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Munich, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks with overwhelming force. Deroy gains the advantage over Archduke John. Casualties: Deroy 39, Archduke Joh…
  - 🏴 Bavaria: [!] Archduke John's troops are BROKEN (morale 0%)! FORCED RETREAT! Deroy advances into Tyrol. (658 lost to march) Tyrol has been captured by Bavaria!
  - ⚔ Deroy (lost 39) vs Archduke John (lost 569) — Archduke John's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×1, wait×1
  - ⚡ AUTONOMOUS: [Shield] Archduke Charles steps forward to cover Archduke John's retreat! "Archduke John is in no condition to fight - I'll handle this!"
  - ⚔ Murat (lost 2674, own corps) vs Archduke Charles (lost 4211) — Ney, Davout and Lannes arrived in time to steady Murat's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 3950 · net +1396 · threat 87 · provinces 30 (+1) · ceiling 15779 · army 137914 · vassals Holland 93 · Switzerland 70
  - NET income 2776 · trade 587 · admin 50 · tribute 562 · upkeep 1636 · charges 230 · contributions 110 · occupation 145 · blockade 368 · admiralty 90
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 10
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +5 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Prussia (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Ney can give chase.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (15,653) vs Archduke Charles (strength unknown) at Piedmont — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 4942) vs Archduke Charles (lost 1037) — The ground itself worked against Murat. Terrain matters, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy engages in solid combat. Archduke Charles holds the line. Casualties: Deroy 2,646, Archduke Charles 1,159. Both a…
  - ⚔ Deroy (lost 2646) vs Archduke Charles (lost 1159) — Deroy bled two men for each of Archduke Charles's. A clear exchange, not yet a decision.
  - verbs: wait×2, move×1, attack×1
- LEDGER treasury 5069 · net +1189 · threat 85 · provinces 30 (+0) · ceiling 14531 · army 132054 · vassals Holland 91 · Switzerland 65
  - NET income 2780 · trade 587 · admin 50 · tribute 562 · upkeep 1692 · charges 385 · contributions 110 · occupation 145 · blockade 368 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Munich. He must reform before he fights again.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Munich — Austria is not forgiven
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout pursues Archduke Charles (at Piedmont). Moves to Franconia. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverte…
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Boh…
- CMD `Soult, drill` → ✗ Not enough actions! Need 1, have 0 — Soult cannot drill today.
- CMD `Massena, move to Milan` → ✗ Not enough actions! Need 1, have 0 — Massena cannot march to Milan today.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy launches a decisive assault. Archduke Charles holds the line. Casualties: Deroy 2,722, Archduke Charles 1,023. Bo… · Deroy marches from Tyrol into Carniola unopposed! (196 lost to march) Captured: Austria → Bavaria · Deroy engages in solid combat. Deroy gains the advantage over Archduke John. Casualties: Deroy 737, Archduke John 1,626…
  - 🏴 Bavaria: Deroy marches from Tyrol into Carniola unopposed! (196 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: FORCED RETREAT! Deroy advances into Hungary. (154 lost to march) Hungary has been captured by Bavaria!
  - ⚔ Deroy (lost 2722) vs Archduke Charles (lost 1023) — A wise investment in fortification. Archduke Charles's position was impregnable to Deroy's assault.
  - ⚔ Deroy (lost 737) vs Archduke John (lost 1626) — The line gave way. Archduke John is falling back, and not in good order. And Archduke John was taken on that field — Ba…
  - verbs: attack×3, fortify×1, wait×1
- ORDER Davout [active]: Davout is pursuing Archduke Charles (0 turns remaining).
- LEDGER treasury 6219 · net +992 · threat 83 · provinces 30 (+0) · ceiling 13917 · army 130980 · vassals Holland 91 · Switzerland 62
  - NET income 2916 · trade 587 · admin 50 · tribute 562 · upkeep 1932 · charges 543 · contributions 110 · occupation 80 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +6 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 1 action unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout pursues Archduke Charles. 1 region away.
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
- LEDGER treasury 7031 · net +691 · threat 81 · provinces 30 (+0) · ceiling 12265 · army 130391 · vassals Holland 91 · Switzerland 59
  - NET income 2920 · trade 587 · admin 50 · tribute 562 · upkeep 2076 · charges 664 · contributions 150 · occupation 80 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: 5 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Bohemia to Franconia (156 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Carniola, Franconia, Hungary, Moravia, Swabia, Tyrol.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Russia: Kutuzov moves from Vienna to Bohemia. Bohemia falls to Russia!
  - verbs: move×1
- ORDER Lannes [awaiting_response]: Lannes: 'Enemy forces discovered at Bohemia! Destination held by Kutuzov. Odds unfavorable — awaiting orders.' Berthier adds: Ney and Massena would a…
  - POPUP strategic_interrupt: Lannes, destination_blocked, Lannes: 'Enemy forces discovered at Bohemia! Destination held by Kutuzov. Odds unfavorable — awaiting orders.' Berthier adds: Ney and Massena would answer the guns — Lannes 12,393, 29,143 with the muster committed, against Kutuzov (strength unknown). → attack_anyway
  - ↳ Lannes attacks Kutuzov. MUSTER — Lannes (12,393; expect about 30,857 with the corps likely to arrive, up to 31,676 if all march) vs Kutuzov (substantial force) at Bohemia — the balance of force looks even — a hard fight that may well decide
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1899, own corps) vs Kutuzov (lost 3000) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 7101 · net +386 · threat 79 · provinces 29 (-1) · ceiling 9857 · army 124752 · vassals Holland 91 · Switzerland 56
  - NET income 2725 · trade 587 · admin 50 · tribute 562 · upkeep 2156 · charges 714 · contributions 150 · occupation 60 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Russia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Munich stays ours by the treaty — titled. Status quo: Bohemia stays Russian by the treaty. Status quo: Carniola, Hungary, Moravia and Tyrol stay Bavarian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (106 lost to march)
- CMD `Massena, fortify` → ✗ Massena is recovering from retreat and cannot fortify. Recovery: 3 turns remaining.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 actions unused) Turn 12 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, wait×1, unfortify×1, stance_change×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → refuse the petition
  - POPUP proposal_result: Holland's petition for relief is refused: loyalty −10 (87 → 77); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 9993 · net +2858 · threat 41 · provinces 29 (+0) · ceiling 248083 · army 128532 · vassals Holland 77 · Switzerland 51
  - NET income 2776 · trade 587 · admin 50 · tribute 562 · upkeep 992 · charges 95 · occupation 30
- DISPATCH: Sire — Massena's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL status_quo_conceded: Bohemia — left with Russia by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 8
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift)
  - LOG ai_ai_proposal_refused: 17 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 79 to 39.

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 12857 · net +2829 · threat 43 · provinces 29 (+0) · ceiling 248583 · army 128092 · vassals Holland 74 · Switzerland 48
  - NET income 2782 · trade 587 · admin 50 · tribute 562 · upkeep 992 · charges 130 · occupation 30
- DISPATCH: Sire — Davout and Massena stand 34,656 men at Tyrol, which feeds 30,000. 4,656 too many. 1,554 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the provi…
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 3 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Murat hesitates briefly but follows orders. Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #14 → 1
  -     ↳ refused: The armistice with Austria holds for 3 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Tyrol to Franconia (192 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 15700 · net +2809 · threat 45 · provinces 29 (+0) · ceiling 249750 · army 126285 · vassals Holland 71 · Switzerland 40
  - NET income 2788 · trade 587 · admin 50 · tribute 562 · upkeep 984 · charges 164 · occupation 30
- DISPATCH: Sire — 7 turns without settlement on Lannes. A rente would close it today; the arrears will not close themselves.
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 6 approaches from Bavaria and Austria are rebuffed (open borders agreement)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 18547 · net +2813 · threat 45 · provinces 29 (+0) · ceiling 252916 · army 124718 · vassals Holland 68 · Switzerland 32
  - NET income 2794 · trade 587 · admin 50 · tribute 562 · upkeep 952 · charges 198 · occupation 30
- DISPATCH: Sire — Talleyrand reports unrest in Switzerland. Invest in them, grant them autonomy, garrison their capital, or cede them a province to steady them.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 21366 · net +2785 · threat 45 · provinces 29 (+0) · ceiling 253416 · army 123198 · vassals Holland 65 · Switzerland 24
  - NET income 2800 · trade 587 · admin 50 · tribute 562 · upkeep 952 · charges 232 · occupation 30
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −75, −85 and −75). The Balance of Europe names the price to keep each out.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Russia (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 24165 · net +2766 · threat 45 · provinces 29 (+0) · ceiling 254583 · army 121724 · vassals Holland 62 · Switzerland 16
  - NET income 2806 · trade 587 · admin 50 · tribute 562 · upkeep 944 · charges 265 · occupation 30
- DISPATCH: Sire — Lannes's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Russia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26945 · net +2746 · threat 45 · provinces 29 (+0) · ceiling 255750 · army 120294 · vassals Holland 59 · Switzerland 8
  - NET income 2812 · trade 587 · admin 50 · tribute 562 · upkeep 936 · charges 299 · occupation 30
- DISPATCH: Sire — Lannes's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 16 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: Switzerland #15 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Switzerland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 27783 · net +726 · threat 37 · provinces 29 (+0) · ceiling 46687 · army 118907 · vassals Holland 46
  - NET income 2818 · trade 587 · admin 50 · tribute 337 · upkeep 1956 · charges 990 · occupation 30 · admiralty 90
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_alliance_cascade: Spain enters the war against Switzerland via its alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - TURN EVENTS 6
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 28515 · net +619 · threat 39 · provinces 29 (+0) · ceiling 43394 · army 117562 · vassals Holland 40
  - NET income 2824 · trade 587 · admin 50 · tribute 337 · upkeep 1956 · charges 1103 · occupation 30 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +6 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Austria sign a Defensive Alliance

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 2 actions unused) Turn 21 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Castanos assaults the Bern garrison! Garrison: 10,000 -> 5,391 (-4,609). Castanos loses 3,472 troops. Garrison holds — … · Castanos assaults the Bern garrison! Garrison collapses (5,391 -> 0). Castanos loses 2,079 troops in the assault. Casta…
  - 🏴 Spain: [Materiel] Guns, horses and stores lost with the fallen: Spain -103g, Switzerland -134g. Captured: Switzerland → Spain
  - verbs: attack×2, move×1
- LEDGER treasury 31075 · net +2530 · threat 40 · provinces 29 (+0) · ceiling 241833 · army 116257 · vassals Holland 32
  - NET income 2830 · trade 587 · admin 50 · tribute 337 · upkeep 896 · charges 348 · occupation 30
- DISPATCH: Sire — Switzerland is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Sire — Switzerland has been eliminated from the war.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 33619 · net +2513 · threat 41 · provinces 29 (+0) · ceiling 243000 · army 114991 · vassals Holland 24
  - NET income 2836 · trade 587 · admin 50 · tribute 337 · upkeep 888 · charges 379 · occupation 30
- DISPATCH: Sire — the levy has stood open 6 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 7
- DIPLO +6 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: 3 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG nation_eliminated: Switzerland has been eliminated from the war.

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Massena is not currently fortified.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 36146 · net +2497 · threat 42 · provinces 29 (+0) · ceiling 244166 · army 113764 · vassals Holland 16
  - NET income 2842 · trade 587 · admin 50 · tribute 337 · upkeep 880 · charges 409 · occupation 30
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Austria, Russia and 3 lesser courts would march.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG ai_ai_proposal_refused: Russia rebuffs Sardinia (defensive alliance)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 38665 · net +2489 · threat 43 · provinces 29 (+0) · ceiling 246000 · army 112573 · vassals Holland 8
  - NET income 2848 · trade 587 · admin 50 · tribute 337 · upkeep 864 · charges 439 · occupation 30
- DISPATCH: Sire — Lannes's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Holland is on the verge of rebellion!
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 13 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: Holland #17 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Holland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 40823 · net +2132 · threat 34 · provinces 29 (+0) · ceiling 218416 · army 111417 · vassals none
  - NET income 2854 · trade 587 · admin 50 · upkeep 864 · charges 465 · occupation 30
- DISPATCH: Sire — Holland is no longer ours. They broke free and stand alone.
  - RAIL diplomatic_vassal_broke_free_peace: Sire — Holland breaks free of France and stands alone — an independent power, and no war declared.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift, diplomatic_relation_shift)
  - LOG vassal_broke_free: Vassal rebellion: Holland breaks free of France and stands alone.
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 42969 · net +2120 · threat 35 · provinces 29 (+0) · ceiling 219583 · army 110297 · vassals none
  - NET income 2860 · trade 587 · admin 50 · upkeep 856 · charges 491 · occupation 30
- DISPATCH: Sire — Holland is no longer ours. They broke free and stand alone.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 45119 · net +2124 · threat 36 · provinces 29 (+0) · ceiling 222083 · army 109210 · vassals none
  - NET income 2866 · trade 587 · admin 50 · upkeep 832 · charges 517 · occupation 30
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 36 and declare on turn 39: Britain, Austria, Russia and 4 lesser courts would march.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 47249 · net +2105 · threat 37 · provinces 29 (+0) · ceiling 222583 · army 108156 · vassals none
  - NET income 2872 · trade 587 · admin 50 · upkeep 832 · charges 542 · occupation 30
- DISPATCH: Sire — Lannes's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 49368 · net +2093 · threat 38 · provinces 29 (+0) · ceiling 223750 · army 107133 · vassals none
  - NET income 2878 · trade 587 · admin 50 · upkeep 824 · charges 568 · occupation 30
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 36 and declare on turn 39: Britain, Austria, Russia and 4 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia rebuffs Sardinia (defensive alliance)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 51467 · net +2074 · threat 39 · provinces 29 (+0) · ceiling 224250 · army 106141 · vassals none
  - NET income 2884 · trade 587 · admin 50 · upkeep 824 · charges 593 · occupation 30
- DISPATCH: Sire — Lannes's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 53555 · net +2063 · threat 43 · provinces 29 (+0) · ceiling 225416 · army 105180 · vassals none
  - NET income 2890 · trade 587 · admin 50 · upkeep 816 · charges 618 · occupation 30
- DISPATCH: Sire — Europe has watched us 20 quiet turns. At this pace the courts consult on turn 36 and declare on turn 39: Britain, Austria, Russia and 4 lesser courts would march. The cheapest court to keep ou…
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 16 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

---
finished: **completed** · commands 150 · popups 35 · battles 21
