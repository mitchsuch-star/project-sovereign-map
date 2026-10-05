# Playtest digest — s7-names-cmdh

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ca4192a11e32` (dirty) · content `60dbe676c0f4` · driver `0ed3b63d33e5`
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
- LEDGER treasury 1651 · net +1439 · threat 76 · provinces 28 · ceiling 32747 · army 174609 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 2156 · blockade 250 · admiralty 90
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
- CMD `Soult, move to Alsace` → ✗ Not enough actions! Need 1, have 0.
- CMD `Murat, move to Franche-Comte` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Charle…
  - ⚔ Archduke Charles (lost 4330) vs Massena (lost 4342, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 2676) vs Teulie (lost 1357, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×2, wait×1
- ORDER Davout [active]: Davout is pursuing Mack (0 turns remaining).
- ORDER Ney [active]: Ney is pursuing Mack (0 turns remaining).
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2908 · net +1641 · threat 74 · provinces 28 (+0) · ceiling 31580 · army 164669 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 829 · upkeep 1856 · charges 51 · blockade 281 · admiralty 90
- DISPATCH: Supply cost you 1,246 men, at Franconia.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
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
- LEDGER treasury 3614 · net +1697 · threat 82 · provinces 29 (+1) · ceiling 21142 · army 158721 · vassals Holland 96 · Kingdom of Italy 95 · Switzerland 90
  - NET income 2636 · trade 525 · admin 50 · tribute 799 · upkeep 1668 · charges 156 · occupation 70 · blockade 329 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is taken at Bohemia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia and Naples (open borders agreement)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 5471 · net +1571 · threat 80 · provinces 29 (+0) · ceiling 21180 · army 157806 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 88
  - NET income 2637 · trade 587 · admin 50 · tribute 802 · upkeep 1630 · charges 347 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria, Naples and Denmark rebuff Prussia (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (19,903; expect about 35,414 with the corps likely to arrive, up to 36,150 if all march) vs Archduke Charles (substantial force) at Tyrol — the balance of f…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 4215, own corps) vs Archduke Charles (lost 1737, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✗ Murat is already in Swabia.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John engages in solid combat. Archduke John gains the advantage over Teulie. Casualties: Archduke John 159, Te… · ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,799 troops. Garrison… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,653 troops in the assau… · Deroy launches a decisive assault. Brutal stalemate between Deroy and Archduke John. Heavy casualties on both sides: De…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -82g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - ⚔ Archduke John (lost 159) vs Teulie (lost 1635) — A grievous defeat for Teulie, Sire. The losses are severe.
  - ⚔ Deroy (lost 1972) vs Archduke John (lost 1717) — Neither Archduke John nor Deroy could claim the field. The armies remain locked.
  - verbs: attack×4, unfortify×1, move×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7056 · net +1857 · threat 78 · provinces 29 (+0) · ceiling 29918 · army 147272 · vassals Holland 92 · Kingdom of Italy 89 · Switzerland 82
  - NET income 2734 · trade 587 · admin 50 · tribute 712 · upkeep 1318 · charges 410 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Tyrol, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Munich instead.) → trust
  - ↳ MUSTER — Lannes (15,578; expect about 52,635 with the corps likely to arrive, up to 53,203 if all march) vs Archduke John (10,377 men) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 553, own corps) vs Archduke John (lost 7017) — Murat, Bernadotte and Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2, unfortify×1, form_square×1
  - ⚡ AUTONOMOUS: [Shield] Archduke Charles steps forward to cover Archduke John's retreat! "Archduke John is in no condition to fight - I'll handle this!"
  - ⚔ Murat (lost 2670, own corps) vs Archduke Charles (lost 4179) — Ney, Davout and Lannes arrived in time to steady Murat's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 8317 · net +1422 · threat 79 · provinces 29 (+0) · ceiling 20319 · army 137778 · vassals Holland 93 · Kingdom of Italy 90 · Switzerland 92
  - NET income 2737 · trade 587 · admin 50 · tribute 487 · upkeep 1084 · charges 747 · contributions 110 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - TURN EVENTS 10
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, coercive_demand)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (15,688; expect about 50,298 with the corps likely to arrive, up to 53,051 if all march) vs Archduke Charles (27,032 men) at Tyrol — the balance of force lo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1792, own corps) vs Archduke Charles (lost 3518) — Davout, Lannes and Napoleon arrived in time to steady Ney's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (15,637) vs Archduke Charles (23,514 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 5454) vs Archduke Charles (lost 661) — Ney reached Murat in time, Sire — but even together, the field could not be held.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - 🏴 Bavaria: Deroy moves from Franconia to Tyrol. Tyrol falls to Bavaria!
  - ⚔ Archduke Charles (lost 1888) vs Davout (lost 2085) — Neither Davout nor Archduke Charles could claim the field. The armies remain locked.
  - verbs: attack×1, move×1, wait×1
- LEDGER treasury 9280 · net +1327 · threat 77 · provinces 29 (+0) · ceiling 19484 · army 124352 · vassals Holland 91 · Kingdom of Italy 88 · Switzerland 89
  - NET income 2725 · trade 587 · admin 50 · tribute 487 · upkeep 968 · charges 946 · contributions 110 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 10
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout notes the risks but prepares the attack. MUSTER — Davout (18,056) vs Archduke Charles (substantial force) at Carniola — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 3928) vs Archduke Charles (lost 779) — Geography was our enemy today, Sire. Archduke Charles held the superior ground.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 2). Moved to Tyrol. Route: Tyrol -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Carniola into Bohemia unopposed! (585 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Carniola into Bohemia unopposed! (585 lost to march) Captured: France → Austria
  - verbs: attack×1, fortify×1, wait×1, recruit×1
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 10367 · net +1085 · threat 75 · provinces 28 (-1) · ceiling 18319 · army 118539 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 86
  - NET income 2590 · trade 587 · admin 50 · tribute 487 · upkeep 920 · charges 1141 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Bohemia into Carniola unopposed! (651 lost to march) Captured: Bavaria → Austria · Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Deroy. Heavy casualties on … · Archduke Charles executes a brilliant maneuver! Brutal stalemate between Archduke Charles and Deroy. Heavy casualties o…
  - 🏴 Austria: ArchdukeCharles marches from Bohemia into Carniola unopposed! (651 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 2030) vs Deroy (lost 2505) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 1928) vs Deroy (lost 2040) — Stalemate. Deroy and Archduke Charles glare at each other across the field.
  - verbs: attack×3, move×1, unfortify×1, wait×1
- ORDER Massena [continues]: Massena hears cannon fire at Croatia but cannot answer it — Cannot move into Carniola - enemy forces present! Use ATTACK to engage Archduke Charles, …
- LEDGER treasury 11428 · net +886 · threat 73 · provinces 28 (+0) · ceiling 17773 · army 117148 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 85
  - NET income 2590 · trade 587 · admin 50 · tribute 487 · upkeep 904 · charges 1316 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 16 approaches from Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs Naples, Denmark and Bavaria (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Munich to Franconia (125 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Croatia, Franconia, Munich, Swabia, Tyrol.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 5 actions, 3 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Brutal stalemate between Archduke Charles and Deroy. Heavy casualties on both… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke… · ArchdukeCharles holds them at Croatia while allies attack from Carniola! (+1 coordination)
  - ⚔ Archduke Charles (lost 1676) vs Deroy (lost 1806) — Neither Deroy nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1190) vs Deroy (lost 1989) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - ⚔ Archduke Charles (lost 916) vs Deroy (lost 1677) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, naval_expedition×1, wait×1
- ORDER Massena [continues]: Massena hears cannon fire at Croatia but cannot answer it — Cannot move into Carniola - enemy forces present! Use ATTACK to engage Archduke John. His…
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 12314 · net +730 · threat 71 · provinces 28 (+0) · ceiling 17420 · army 117023 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 84
  - NET income 2590 · trade 587 · admin 50 · tribute 487 · upkeep 904 · charges 1472 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #10 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #11 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Andalusia stays British by the treaty. Status quo: Croatia and Tyrol stay Bavarian by the treaty. Status quo: Milan stays Austrian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (101 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, drill×1, fortify×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 15037 · net +2690 · threat 38 · provinces 28 (+0) · ceiling 239166 · army 116922 · vassals Holland 87 · Kingdom of Italy 79 · Switzerland 83
  - NET income 2590 · trade 623 · admin 50 · tribute 487 · upkeep 904 · charges 156
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL status_quo_conceded: Milan — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Revanche — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent ×2, blockade_broken ×3, agenda_shift)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 71 to 35.

## Turn 12 — Early March 1806
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #12 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, unfortify×1, stance_change×1, wait×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 17390 · net +2325 · threat 41 · provinces 28 (+0) · ceiling 211083 · army 116922 · vassals Holland 96 · Kingdom of Italy 77 · Switzerland 82
  - NET income 2590 · trade 623 · admin 50 · tribute 150 · upkeep 904 · charges 184
- DISPATCH: Sire — Lannes has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 14 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
  - MAILBOX #11 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #13 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (77 → 87); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #14 → 1
  -     ↳ refused: The armistice with Austria holds for 3 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✗ Davout is already in Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 10 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×4, wait×3, move×2, drill×1
- LEDGER treasury 19581 · net +2390 · threat 44 · provinces 28 (+0) · ceiling 218666 · army 115829 · vassals Holland 95 · Kingdom of Italy 86 · Switzerland 81
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 888 · charges 210
- DISPATCH: Sire — 7 turns without settlement on Lannes. A rente would close it today; the arrears will not close themselves.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, coercive_demand)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Massena, move to Tyrol` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 14 ended. Turn 15 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×3, wait×2
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 21979 · net +2369 · threat 45 · provinces 28 (+0) · ceiling 219333 · army 114769 · vassals Holland 94 · Kingdom of Italy 85 · Switzerland 80
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 880 · charges 239
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL broken_bargain: The compact with Sweden lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, blockade_begins, diplomatic_relation_shift)

## Turn 15 — Late April 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #15 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 8 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×4, wait×3, drill×1
- LEDGER treasury 24131 · net +2126 · threat 45 · provinces 28 (+0) · ceiling 201250 · army 113740 · vassals Holland 93 · Kingdom of Italy 84 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · upkeep 872 · charges 265
- DISPATCH: Sire — Lannes's claim is 9 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Munich. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 7 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×4, wait×2, garrison×1
- LEDGER treasury 26273 · net +2116 · threat 45 · provinces 28 (+0) · ceiling 202583 · army 112743 · vassals Holland 92 · Kingdom of Italy 83 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · upkeep 856 · charges 291
- DISPATCH: Sire — Lannes's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Karelia. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3, recruit×2, drill×1
- LEDGER treasury 28389 · net +2091 · threat 45 · provinces 28 (+0) · ceiling 202583 · army 111775 · vassals Holland 91 · Kingdom of Italy 82 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · upkeep 856 · charges 316
- DISPATCH: Sire — Lannes's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG design_promoted: REVANCHE: Sweden swears to retake Karelia — Russia is not forgiven

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 30488 · net +2074 · threat 45 · provinces 28 (+0) · ceiling 203250 · army 110836 · vassals Holland 90 · Kingdom of Italy 81 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · upkeep 848 · charges 341
- DISPATCH: Sire — Lannes's claim is 12 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Munich to Franconia (108 lost to march, 216 to enemy harassment)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 32570 · net +2394 · threat 45 · provinces 28 (+0) · ceiling 232000 · army 108817 · vassals Holland 89 · Kingdom of Italy 80 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · tribute 337 · upkeep 840 · charges 366
- DISPATCH: Sire — Lannes's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (NON AGGRESSION → OPEN BORDERS)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 34988 · net +2539 · threat 45 · provinces 28 (+0) · ceiling 246500 · army 107220 · vassals Holland 88 · Kingdom of Italy 79 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · tribute 487 · upkeep 816 · charges 395
- DISPATCH: Sire — Lannes's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
  - MAILBOX #13 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #16 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 37190 · net +2175 · threat 45 · provinces 28 (+0) · ceiling 218416 · army 105711 · vassals Holland 98 · Kingdom of Italy 78 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · tribute 150 · upkeep 816 · charges 422
- DISPATCH: Sire — Lannes's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
  - MAILBOX #14 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #17 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (78 → 88); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 39239 · net +2250 · threat 45 · provinces 28 (+0) · ceiling 226666 · army 104268 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 792 · charges 446
- DISPATCH: Sire — Lannes's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×3, wait×2
- LEDGER treasury 41497 · net +2231 · threat 45 · provinces 28 (+0) · ceiling 227333 · army 102882 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 784 · charges 473
- DISPATCH: Sire — Lannes's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- LEDGER treasury 43728 · net +2204 · threat 45 · provinces 28 (+0) · ceiling 227333 · army 101551 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 784 · charges 500
- DISPATCH: Sire — Lannes's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- LEDGER treasury 45956 · net +2201 · threat 45 · provinces 28 (+0) · ceiling 229333 · army 100275 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 760 · charges 527
- DISPATCH: Sire — Austria moves toward war with Bavaria. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Austria will move on Bavaria. You may compensate (1,320g — you can afford it); guarantee Bavaria (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 5
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×3, wait×2
- LEDGER treasury 48157 · net +2175 · threat 45 · provinces 28 (+0) · ceiling 229333 · army 99050 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 760 · charges 553
- DISPATCH: Sire — Lannes's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +6 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad ×2, diplomatic_dp_regen, coercive_demand)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- LEDGER treasury 49314 · net +969 · threat 49 · provinces 28 (+0) · ceiling 76829 · army 97873 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 611 · admin 50 · tribute 225 · upkeep 752 · charges 1665 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - RAIL diplomatic_alliance_cascade: France enters the war against Austria via its alliance with Bavaria.
  - RAIL diplomatic_war_declared: Austria has declared war on Bavaria, shattering the Peace Treaty, with 1 allied court poised to follow.
  - TURN EVENTS 4
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_dp_regen, witness_strike_recorded, diplomatic_treaty_broken, diplomatic_relation_shift)
  - LOG ai_ai_proposal_refused: Austria rebuffs Britain (defensive alliance)
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with Bavaria by declaring war.
  - LOG diplomatic_treaty_broken: France was forced to break the Peace Treaty with Austria (cascade).
  - LOG defensive_cascade: Defensive cascade: France joins war via Bavaria

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
- LEDGER treasury 50299 · net +1133 · threat 53 · provinces 28 (+0) · ceiling 79786 · army 96765 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 611 · admin 50 · tribute 562 · upkeep 736 · charges 1854 · admiralty 90
- DISPATCH: Sire — Croatia has been taken by Austria.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, sovereign_takes_field)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Mack is at Bohemia, just one region away.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: 8 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×3, recruit×2, unfortify×1, form_square×1, wait×1
- LEDGER treasury 51448 · net +1096 · threat 57 · provinces 28 (+0) · ceiling 77793 · army 95692 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 720 · charges 2057 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Mack at Bohemia instead.)
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Mack at Bohemia instead.) → trust
  - ↳ MUSTER — Massena (16,980; expect about 34,948 with the corps likely to arrive, up to 35,497 if all march) vs Mack (42,601 men) at Bohemia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 3927, own corps) vs Mack (lost 3283, own corps) — Ney, Lannes and Murat reached Massena in time, Sire — but even together, the field could not be held. — The corps system brought Murat in.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Brutal stalemate between Archduke Charles and Deroy. Heavy casualties… · Archduke John's forces press forward aggressively. Brutal stalemate between Archduke John and Deroy. Heavy casualties o… · Archduke Charles delivers an effective strike. Brutal stalemate between Archduke Charles and Deroy. Heavy casualties on…
  - ⚔ Archduke Charles (lost 2997) vs Deroy (lost 3513) — Neither Deroy nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Archduke John (lost 1384, own corps) vs Deroy (lost 3197) — Neither Deroy nor Archduke John could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1790, own corps) vs Deroy (lost 3004) — Stalemate. Deroy and Archduke Charles glare at each other across the field.
  - verbs: attack×3, fortify×1, wait×1
- ORDER Murat [retired]: Murat's question is overtaken, Sire — Murat has marched clear of Bohemia. He awaits new orders.
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 52011 · net +689 · threat 55 · provinces 28 (+0) · ceiling 65670 · army 88144 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 664 · charges 2520 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Austria has offered terms to settle Austria vs Bavaria.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_we_threshold, diplomatic_dp_regen)

## Turn 31 — Late December 1806
  - MAILBOX #15 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #18 already answered this chain)
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes cannot drill with enemy forces nearby! Mack is at Bohemia, just one region away.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 3 actions unused) Turn 32 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Deroy. Casualties: Arch… · ArchdukeCharles holds them at Tyrol while allies attack from Bohemia! (+1 coordination)
  - ⚔ Archduke Charles (lost 1692) vs Deroy (lost 2765) — Even the favorable ground could not save Deroy, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke Charles (lost 1122) vs Deroy (lost 2788) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: recruit×3, attack×2, wait×2
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 52700 · net +492 · threat 53 · provinces 28 (+0) · ceiling 61869 · army 87452 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 664 · charges 2717 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
  - MAILBOX #15 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → request_settlement_revision
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #18 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke…
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Tyrol has been captured by Austria!
  - ⚔ Archduke Charles (lost 942) vs Deroy (lost 4587) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: wait×2, recruit×2, attack×1, form_square×1
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 53208 · net +317 · threat 51 · provinces 28 (+0) · ceiling 58778 · army 85569 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 648 · charges 2908 · admiralty 90
- DISPATCH: Sire — Tyrol has been taken by Austria.
  - TURN EVENTS 4
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 33 — Late January 1807
  - MAILBOX #15 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → reject_settlement_offer
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Mack is at Bohemia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, move×1, unfortify×1, fortify×1, form_square×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 53525 · net +134 · threat 49 · provinces 28 (+0) · ceiling 55750 · army 83773 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 611 · admin 50 · tribute 712 · upkeep 648 · charges 3091 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 27 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
  - MAILBOX #16 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #19 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Massena is not currently fortified.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 8 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Franconia garrison! Garrison: 3,000 -> 1,500 (-1,500). ArchdukeCharles loses 770 troops. G… · ArchdukeJohn assaults the Franconia garrison! Garrison: 1,500 -> 750 (-750). ArchdukeJohn loses 404 troops. Garrison ho… · ArchdukeCharles assaults the Franconia garrison! Garrison: 750 -> 375 (-375). ArchdukeCharles loses 224 troops. Garriso…
  - 🏴 Austria: ArchdukeJohn moves from Bohemia to Franconia. Franconia falls to Austria!
  - verbs: attack×3, move×2, unfortify×1, break_square×1, wait×1
- LEDGER treasury 56035 · net +2472 · threat 47 · provinces 28 (+0) · ceiling 218644 · army 82887 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 632 · charges 821
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Redeem Italy — service to the strong is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (462 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1764) vs Deroy (lost 4114) — Deroy's corps broke, Sire. They are streaming back from the field.
  - verbs: wait×2, move×1, fortify×1, attack×1, recruit×1
- ORDER Lannes [continues]: Lannes marches to Swabia. 1 region to Rhineland.
- ORDER Murat [completed]: Murat arrives at Rhineland. Murat: "Accomplished. The men want a battle, not another road."
- ORDER Ney [error]: Ney could not advance toward Rhineland.
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 58531 · net +2458 · threat 45 · provinces 28 (+0) · ceiling 220223 · army 80670 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 608 · charges 859
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL settlement_offer_arrival: Austria has offered terms to settle Austria vs Bavaria.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 36 — Early March 1807
  - MAILBOX #17 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → accept_settlement_offer
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #20 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, fortify×1, move×1
- ORDER Lannes [completed]: Lannes arrives at Franche-Comte. Lannes: "Accomplished. The men want a battle, not another road."
- ORDER Soult [completed]: "the road home — safe passage granted by the peace" — executed as written. Soult arrives at Franche-Comte. Awaiting your next word.
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 60997 · net +2429 · threat 45 · provinces 28 (+0) · ceiling 220750 · army 79849 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 600 · charges 896
- DISPATCH: Sire — Davout and Ney are no nearer home, and the safe passage runs out in 1 turn. After that their corps will be interned where they stand.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 37 — Late March 1807
  - MAILBOX #17 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → request_settlement_revision
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #20 already answered this chain)
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, unfortify×1, move×1
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 63434 · net +2400 · threat 45 · provinces 28 (+0) · ceiling 221276 · army 79063 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 592 · charges 933
- DISPATCH: Sire — Davout and Ney are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 38 — Early April 1807
  - MAILBOX #17 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → reject_settlement_offer
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3, recruit×2, move×1
- LEDGER treasury 64368 · net +699 · threat 45 · provinces 28 (+0) · ceiling 81158 · army 78309 · vassals Holland 96 · Kingdom of Italy 86 · Switzerland 88
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 592 · charges 2594 · requisitions 50 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 32 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Redeem Italy — prepared now to go as far as war.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces (Archduke John) present at Franconia!
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 95% -> 72%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 600g on this turn's orders
- enemy phase: 8 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Ney. Casualties: Archduke Charles… · Deroy marches from Franche-Comte into Swabia unopposed! (364 lost to march — forward supply lines reduce losses) Captur…
  - 🏴 Bavaria: Deroy marches from Franche-Comte into Swabia unopposed! (364 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - ⚔ Archduke Charles (lost 1031) vs Ney (lost 1066, own corps) — Napoleon reached Ney in time, Sire — but even together, the field could not be held.
  - verbs: attack×2, move×2, retreat×1, unfortify×1, stance_change×1, recruit×1
- ORDER Ney [awaiting_response]: Ney is cornered at Franconia with 3,725 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Franconia with 3,725 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 64177 · net +333 · threat 45 · provinces 28 (+0) · ceiling 71216 · army 73516 · vassals Holland 94 · Kingdom of Italy 84 · Switzerland 86
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 568 · charges 2934 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Munich (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy marches from Swabia into Franconia unopposed! (309 lost to march — forward supply lines reduce losses) Captured: …
  - 🏴 Bavaria: Deroy marches from Swabia into Franconia unopposed! (309 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - verbs: attack×1, wait×1
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 64526 · net +132 · threat 45 · provinces 28 (+0) · ceiling 67138 · army 72496 · vassals Holland 94 · Kingdom of Italy 84 · Switzerland 86
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 552 · charges 3151 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL settlement_offer_arrival: Austria has offered terms to settle Austria vs Bavaria.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Name census (NPC-12 / SF5-X3)

- verdict **PASS** · keys ArchdukeCharles, ArchdukeJohn · 771 responses · 844236 strings · 2452 carrying a display name · 0 leaks

---
finished: **completed** · commands 200 · popups 53 · battles 31
