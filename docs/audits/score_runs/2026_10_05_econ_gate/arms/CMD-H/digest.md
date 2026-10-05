# Playtest digest — CMD-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
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
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
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
- LEDGER treasury 3725 · net +1198 · threat 87 · provinces 30 (+1) · ceiling 13872 · army 137914 · vassals Holland 93 · Switzerland 92
  - NET income 2776 · trade 587 · admin 50 · tribute 337 · upkeep 1636 · charges 203 · contributions 110 · occupation 145 · blockade 368 · admiralty 90
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 9
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +5 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
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
- LEDGER treasury 4647 · net +1017 · threat 85 · provinces 30 (+0) · ceiling 12740 · army 132054 · vassals Holland 91 · Switzerland 89
  - NET income 2780 · trade 587 · admin 50 · tribute 337 · upkeep 1692 · charges 332 · contributions 110 · occupation 145 · blockade 368 · admiralty 90
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
- LEDGER treasury 5625 · net +844 · threat 83 · provinces 30 (+0) · ceiling 12170 · army 130980 · vassals Holland 91 · Switzerland 88
  - NET income 2916 · trade 587 · admin 50 · tribute 337 · upkeep 1932 · charges 466 · contributions 110 · occupation 80 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 7
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
- LEDGER treasury 6289 · net +564 · threat 81 · provinces 30 (+0) · ceiling 10560 · army 130391 · vassals Holland 91 · Switzerland 87
  - NET income 2920 · trade 587 · admin 50 · tribute 337 · upkeep 2076 · charges 566 · contributions 150 · occupation 80 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 5
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
  - saved `CMD-H_t10` → Game saved: CMD-H_t10
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
- LEDGER treasury 6232 · net +283 · threat 79 · provinces 29 (-1) · ceiling 8250 · army 124752 · vassals Holland 91 · Switzerland 86
  - NET income 2725 · trade 587 · admin 50 · tribute 337 · upkeep 2156 · charges 592 · contributions 150 · occupation 60 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Russia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
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
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 8910 · net +2309 · threat 41 · provinces 29 (+0) · ceiling 201250 · army 128532 · vassals Holland 97 · Switzerland 83
  - NET income 2776 · trade 587 · admin 50 · upkeep 992 · charges 82 · occupation 30
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
  - LOG ai_ai_proposal_refused: 15 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 79 to 39.
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 11225 · net +2287 · threat 43 · provinces 29 (+0) · ceiling 201750 · army 128092 · vassals Holland 96 · Switzerland 82
  - NET income 2782 · trade 587 · admin 50 · upkeep 992 · charges 110 · occupation 30
- DISPATCH: Sire — Davout and Massena stand 34,656 men at Tyrol, which feeds 30,000. 4,656 too many. 1,554 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for the provi…
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (defensive alliance)
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
- LEDGER treasury 13526 · net +2498 · threat 45 · provinces 29 (+0) · ceiling 221666 · army 126285 · vassals Holland 95 · Switzerland 81
  - NET income 2788 · trade 587 · admin 50 · tribute 225 · upkeep 984 · charges 138 · occupation 30
- DISPATCH: Sire — 7 turns without settlement on Lannes. A rente would close it today; the arrears will not close themselves.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 16062 · net +2506 · threat 45 · provinces 29 (+0) · ceiling 224833 · army 124718 · vassals Holland 94 · Switzerland 80
  - NET income 2794 · trade 587 · admin 50 · tribute 225 · upkeep 952 · charges 168 · occupation 30
- DISPATCH: Sire — an envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #15 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 18349 · net +2259 · threat 45 · provinces 29 (+0) · ceiling 206583 · army 123198 · vassals Holland 93 · Switzerland 90
  - NET income 2800 · trade 587 · admin 50 · upkeep 952 · charges 196 · occupation 30
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −75, −85 and −75). The Balance of Europe names the price to keep each out.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Russia (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2
- LEDGER treasury 20622 · net +2246 · threat 45 · provinces 29 (+0) · ceiling 207750 · army 121724 · vassals Holland 92 · Switzerland 90
  - NET income 2806 · trade 587 · admin 50 · upkeep 944 · charges 223 · occupation 30
- DISPATCH: Sire — Lannes's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
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
- LEDGER treasury 22882 · net +2233 · threat 45 · provinces 29 (+0) · ceiling 208916 · army 120294 · vassals Holland 91 · Switzerland 90
  - NET income 2812 · trade 587 · admin 50 · upkeep 936 · charges 250 · occupation 30
- DISPATCH: Sire — Lannes's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 14 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25145 · net +2236 · threat 45 · provinces 29 (+0) · ceiling 211416 · army 118907 · vassals Holland 90 · Switzerland 90
  - NET income 2818 · trade 587 · admin 50 · upkeep 912 · charges 277 · occupation 30
- DISPATCH: Sire — the court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 27387 · net +2552 · threat 45 · provinces 29 (+0) · ceiling 240000 · army 117562 · vassals Holland 89 · Switzerland 90
  - NET income 2824 · trade 587 · admin 50 · tribute 337 · upkeep 912 · charges 304 · occupation 30
- DISPATCH: Sire — Sardinia and Austria have signed the Defensive Alliance.
  - TURN EVENTS 2
- DIPLO +5 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Austria sign a Defensive Alliance

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 22.
  - saved `CMD-H_t20` → Game saved: CMD-H_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 2 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 29961 · net +2543 · threat 45 · provinces 29 (+0) · ceiling 241833 · army 116257 · vassals Holland 88 · Switzerland 90
  - NET income 2830 · trade 587 · admin 50 · tribute 337 · upkeep 896 · charges 335 · occupation 30
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #16 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 32181 · net +2193 · threat 45 · provinces 29 (+0) · ceiling 214916 · army 114991 · vassals Holland 98 · Switzerland 90
  - NET income 2836 · trade 587 · admin 50 · upkeep 888 · charges 362 · occupation 30
- DISPATCH: Sire — Lannes's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Massena is not currently fortified.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 34388 · net +2406 · threat 45 · provinces 29 (+0) · ceiling 234833 · army 113764 · vassals Holland 98 · Switzerland 90
  - NET income 2842 · trade 587 · admin 50 · tribute 225 · upkeep 880 · charges 388 · occupation 30
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Austria, Russia and 3 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Russia rebuffs Sardinia (defensive alliance)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 36816 · net +2399 · threat 45 · provinces 29 (+0) · ceiling 236666 · army 112573 · vassals Holland 98 · Switzerland 90
  - NET income 2848 · trade 587 · admin 50 · tribute 225 · upkeep 864 · charges 417 · occupation 30
- DISPATCH: Sire — Lannes's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 13 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 39221 · net +2376 · threat 45 · provinces 29 (+0) · ceiling 237166 · army 111417 · vassals Holland 98 · Switzerland 90
  - NET income 2854 · trade 587 · admin 50 · tribute 225 · upkeep 864 · charges 446 · occupation 30
- DISPATCH: Sire — Prussia enacts the Krümper System — infantry manpower returns 25% faster.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 41611 · net +2361 · threat 45 · provinces 29 (+0) · ceiling 238333 · army 110297 · vassals Holland 98 · Switzerland 90
  - NET income 2860 · trade 587 · admin 50 · tribute 225 · upkeep 856 · charges 475 · occupation 30
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
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
- LEDGER treasury 44002 · net +2362 · threat 45 · provinces 29 (+0) · ceiling 240833 · army 109210 · vassals Holland 98 · Switzerland 90
  - NET income 2866 · trade 587 · admin 50 · tribute 225 · upkeep 832 · charges 504 · occupation 30
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Austria, Russia and 3 lesser courts would march.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 46370 · net +2340 · threat 45 · provinces 29 (+0) · ceiling 241333 · army 108156 · vassals Holland 98 · Switzerland 90
  - NET income 2872 · trade 587 · admin 50 · tribute 225 · upkeep 832 · charges 532 · occupation 30
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
- LEDGER treasury 48724 · net +2663 · threat 45 · provinces 29 (+0) · ceiling 270583 · army 107133 · vassals Holland 98 · Switzerland 90
  - NET income 2878 · trade 587 · admin 50 · tribute 562 · upkeep 824 · charges 560 · occupation 30
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Austria, Russia and 3 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (defensive alliance)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 51393 · net +2637 · threat 45 · provinces 29 (+0) · ceiling 271083 · army 106141 · vassals Holland 98 · Switzerland 90
  - NET income 2884 · trade 587 · admin 50 · tribute 562 · upkeep 824 · charges 592 · occupation 30
- DISPATCH: Sire — Lannes's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 13 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-H_t30` → Game saved: CMD-H_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 54044 · net +2619 · threat 49 · provinces 29 (+0) · ceiling 272250 · army 105180 · vassals Holland 98 · Switzerland 90
  - NET income 2890 · trade 587 · admin 50 · tribute 562 · upkeep 816 · charges 624 · occupation 30
- DISPATCH: Sire — Europe has watched us 20 quiet turns. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Austria, Russia and 3 lesser courts would march. The cheapest court to keep ou…
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 56687 · net +2611 · threat 53 · provinces 29 (+0) · ceiling 274250 · army 104246 · vassals Holland 98 · Switzerland 90
  - NET income 2890 · trade 587 · admin 50 · tribute 562 · upkeep 792 · charges 656 · occupation 30
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 59298 · net +2580 · threat 57 · provinces 29 (+0) · ceiling 274250 · army 103341 · vassals Holland 98 · Switzerland 90
  - NET income 2890 · trade 587 · admin 50 · tribute 562 · upkeep 792 · charges 687 · occupation 30
- DISPATCH: Sire — Europe has watched us 22 quiet turns. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Austria, Russia and 3 lesser courts would march. The cheapest court to keep ou…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 61878 · net +2549 · threat 60 · provinces 29 (+0) · ceiling 274250 · army 102463 · vassals Holland 98 · Switzerland 90
  - NET income 2890 · trade 587 · admin 50 · tribute 562 · upkeep 792 · charges 718 · occupation 30
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 64397 · net +2489 · threat 58 · provinces 29 (+0) · ceiling 271750 · army 101611 · vassals Holland 98 · Switzerland 90
  - NET income 2890 · trade 549 · admin 50 · tribute 562 · upkeep 784 · charges 748 · occupation 30
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 2 turns (2 DP); buying off her design costs 1…
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Russia rebuffs Sardinia (defensive alliance)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 66894 · net +2467 · threat 56 · provinces 29 (+0) · ceiling 272416 · army 100784 · vassals Holland 98 · Switzerland 90
  - NET income 2890 · trade 549 · admin 50 · tribute 562 · upkeep 776 · charges 778 · occupation 30
- DISPATCH: Sire — St Petersburg now pays London 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 7 turns (7 DP); buying off her design …
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Britain against France (500g/turn)
  - LOG ai_ai_proposal_refused: 13 approaches from Russia and Austria are rebuffed (defensive alliance)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 66789 · net -309 · threat 54 · provinces 29 (+0) · ceiling 57994 · army 99983 · vassals Holland 98 · Switzerland 90
  - NET income 2890 · trade 549 · admin 50 · tribute 562 · upkeep 1616 · charges 2280 · occupation 30 · blockade 344 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_alliance_cascade: Spain enters the war against Britain, Russia, Austria, Sweden, Hanover and Sardinia via its alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 4 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +5 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- COURTS: And Britain and Sardinia stir at their own designs.
- DIPLO +13 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, blockade_begins ×3, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Russia has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG coalition_declared: The Fourth Russian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia, Sweden
  - LOG sponsorship_granted: Russia sponsors Sweden against France (500g/turn)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes cannot drill with enemy forces nearby! Mack is at Bohemia, just one region away.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 8 actions, 4 attacks — Britain, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov launches a decisive assault. Brutal stalemate between Kutuzov and Murat. Heavy casualties on both sides: Kutuzo… · Kutuzov launches a decisive assault. Brutal stalemate between Kutuzov and Ney. Heavy casualties on both sides: Kutuzov … · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Ney. Casualties: Archduke C… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Massena. Casualties: Archdu…
  - 🏴 Austria: [!] No word came for Lannes, cornered at Tyrol — the enemy did not wait. [!] MARSHAL CAPTURED — Lannes is taken by Austria at Tyrol!
  - ⚔ Kutuzov (lost 3615) vs Murat (lost 787, own corps) — Napoleon arrived in time to steady Murat's position. The field was held, nothing further.
  - ⚔ Kutuzov (lost 2947) vs Ney (lost 708, own corps) — Neither Ney nor Kutuzov could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1660) vs Ney (lost 2397, own corps) — A grievous defeat for Ney, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 977) vs Massena (lost 5373, own corps) — Reinforcements from Lannes bolstered Massena's position — though Bernadotte never arrived, Sire.
  - verbs: attack×4, recruit×2, unfortify×1, move×1
- ORDER Ney [awaiting_response]: Ney is cornered at Franconia with 3,215 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Franconia with 3,215 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 65282 · net -743 · threat 52 · provinces 29 (+0) · ceiling 50980 · army 76101 · vassals Holland 100 · Switzerland 98
  - NET income 2890 · trade 549 · admin 50 · tribute 562 · upkeep 1040 · charges 3290 · occupation 30 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.
  - RAIL expedition_landed: THE LANDING: Paget has put 9,323 men ashore at Piedmont.
  - TURN EVENTS 8
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Lannes, fortify` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 5 actions, 3 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Piedmont into Provence unopposed! (93 lost to march) Captured: France → Britain · Paget's forces advance steadily. Paget gains the advantage over Teulie. Casualties: Paget 388, Teulie 3,157. Both armie… · Castanos attacks with overwhelming force. Castanos gains the advantage over Paget. Casualties: Castanos 1,133, Paget 2,…
  - 🏴 Britain: Paget marches from Piedmont into Provence unopposed! (93 lost to march) Captured: France → Britain
  - 🏴 Britain: Paget moves from Provence to Lyonnais. Lyonnais falls to Britain!
  - 🏴 Britain: Paget moves from Lyonnais to Limousin. Limousin falls to Britain!
  - ⚔ Paget (lost 388) vs Teulie (lost 3157) — The toll on Teulie's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Castanos (lost 1133) vs Paget (lost 2154) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price. — The Line Holds +15% (Paget)
  - verbs: attack×3, move×2
- ORDER Teulie [awaiting_response]: Teulie is cornered at Paris with 1,843 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Paris with 1,843 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 62033 · net -3013 · threat 50 · provinces 26 (-3) · ceiling 27784 · army 70317 · vassals Holland 100 · Switzerland 100
  - NET income 2532 · trade 549 · admin 50 · tribute 562 · upkeep 960 · charges 5282 · occupation 30 · blockade 344 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 8
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Sweden
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG ai_ai_proposal_refused: 4 courts rebuff Britain (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Britain sign a Defensive Alliance
  - LOG ai_ai_proposal_refused: 4 courts rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Amey commands our foot at Bern — march him within…
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 60825 · net -1327 · threat 48 · provinces 26 (+0) · ceiling 39140 · army 69549 · vassals Holland 100 · Switzerland 100
  - NET income 2536 · trade 549 · admin 50 · tribute 562 · upkeep 960 · charges 3600 · occupation 30 · blockade 344 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Britain holds him prisoner.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Munich (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-H_t40` → Game saved: CMD-H_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1
- LEDGER treasury 59523 · net -1406 · threat 46 · provinces 26 (+0) · ceiling 37683 · army 68796 · vassals Holland 100 · Switzerland 100
  - NET income 2541 · trade 549 · admin 50 · tribute 562 · upkeep 940 · charges 3704 · occupation 30 · blockade 344 · admiralty 90
- DISPATCH: Sire — Britain's gold reaches Russia — the subsidy stands at 500 this season.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Russia
  - LOG british_subsidy: Britain's gold: 500g reaches Austria

---
finished: **completed** · commands 200 · popups 37 · battles 27
