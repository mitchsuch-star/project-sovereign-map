# Playtest digest — CMD-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `88cd6378f016` (dirty) · content `08fe8a7fc9ef` · driver `2cbaf8455dd8`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2375, own corps) vs Mack (lost 18369) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a devastating assault! Archduke Charles gains the advantage over Bernadotte. Casualties: Arch…
  - ⚔ Archduke Charles (lost 2457) vs Bernadotte (lost 5337, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1625 · net +1503 · threat 75 · provinces 28 · ceiling 33312 · army 173606 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2134 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,337 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,677; expect about 124,084 with the corps likely to arrive, up to 128,436 if all march) vs Mack (substantial force) at Munich — the balance of force look…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 402, own corps) vs Mack (lost 31817) — Davout, Massena, Napoleon and Teulie arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franconia — shall Davout engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franconia — shall Davout engage him? → 1 (first option: Archduke Charles at Franconia)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.) → trust
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Bernadotte. Casualties: Archdu… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Charles… · Archduke Charles's attack meets fierce resistance. Archduke Charles gains the advantage over Murat. Casualties: Archduk…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,398 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 880) vs Bernadotte (lost 6738) — Where was Ney? Bernadotte held the field alone — reinforcement never came. And Bernadotte was taken on that field — Aus…
  - ⚔ Archduke Charles (lost 1581) vs Deroy (lost 7005) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2079) vs Murat (lost 5894) — Murat stood alone, Sire. Ney and Soult never came.
  - verbs: attack×3, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 3185 · net +2098 · threat 81 · provinces 28 (+0) · ceiling 25690 · army 148652 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 92
  - NET income 2575 · trade 450 · admin 50 · tribute 937 · upkeep 1368 · charges 110 · contributions 65 · blockade 281 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +9 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franche-Comte — shall Ney engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franche-Comte — shall Ney engage him? → 1 (first option: Archduke Charles at Franche-Comte)
  - ↳ MUSTER — Ney (16,836; expect about 85,611 with the corps likely to arrive, up to 90,554 if all march) vs Archduke Charles (41,029 men) at Franche-Comte — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1475, own corps) vs Archduke Charles (lost 9649) — Massena, Napoleon and Teulie's timely arrival aided Ney. Soult, however, was conspicuously absent. — The corps system brought Teulie in.
- CMD `Davout, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franche-Comte — shall Davout engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franche-Comte — shall Davout engage him? → 1 (first option: Archduke Charles at Franche-Comte)
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (166 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 653 gold (×3 at war) (×1.09 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 653g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
  - ⚡ AUTONOMOUS: Murat holds them at Franche-Comte while allies attack from Munich! (+1 coordination)
  - ⚔ Murat (lost 1020, own corps) vs Archduke Charles (lost 18343) — Lannes arrived to reinforce Murat, but Soult failed to reach the field in time. And Archduke Charles was taken on that …
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4671 · net +2229 · threat 97 · provinces 29 (+1) · ceiling 26781 · army 138911 · vassals Holland 98 · Kingdom of Italy 96 · Switzerland 92
  - NET income 2577 · trade 525 · admin 50 · tribute 937 · upkeep 1120 · charges 269 · occupation 52 · blockade 329 · admiralty 90
- DISPATCH: Sire — the Archduke Charles of Austria is taken at Franche-Comte — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke John at Tyrol — shall Ney engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke John at Tyrol — shall Ney engage him? → 1 (first option: Archduke John at Tyrol)
- CMD `Davout, fortify` → ✗ Davout is already fortified at Munich (+12% defense).
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Ney [active]: Ney is pursuing Archduke John (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 7076 · net +2052 · threat 95 · provinces 29 (+0) · ceiling 26798 · army 135383 · vassals Holland 98 · Kingdom of Italy 96 · Switzerland 90
  - NET income 2579 · trade 587 · admin 50 · tribute 937 · upkeep 1064 · charges 527 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Lannes, Murat, Massena, Napoleon and Teulie stand 71,980 men at Franche-Comte, which feeds 52,500. 19,480 too many. 9,436 men lost in 3 turns. No depot may be laid at Franche-Comte — town regi…
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke John at Tyrol — shall Lannes engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke John at Tyrol — shall Lannes engage him? → 1 (first option: Archduke John at Tyrol)
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (133 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,777 troops. Garrison… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,543 troops in the assau… · ArchdukeJohn marches from Milan into Piedmont unopposed! (310 lost to march) Captured: KingdomOfItaly → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - 🏴 Austria: ArchdukeJohn marches from Milan into Piedmont unopposed! (310 lost to march) Captured: KingdomOfItaly → Austria
  - verbs: attack×3, unfortify×1, move×1
- ORDER Lannes [active]: Lannes is pursuing Archduke John (0 turns remaining).
- ORDER Ney [interrupted]: Ney hears cannon fire! Abandoning orders — rushing to Milan!
  - ⚔ [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #14 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 8694 · net +1310 · threat 83 · provinces 29 (+0) · ceiling 20773 · army 129933 · vassals Holland 98 · Switzerland 98
  - NET income 2582 · trade 599 · admin 50 · tribute 337 · upkeep 1016 · charges 725 · occupation 52 · blockade 375 · admiralty 90
- DISPATCH: Sire — Ney, crowned three turns ago, has been driven back.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Milan instead.) → trust
  - ↳ MUSTER — Lannes (13,168; expect about 30,457 with the corps likely to arrive, up to 35,777 if all march) vs Archduke John (12,244 men) at Milan — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 945, own corps) vs Archduke John (lost 3378) — Davout arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire. — The corps system brought Davout in.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: retreat×1, stance_change×1, wait×1, recruit×1
  - POPUP marshal_audience: shadow_command, Marshal Massena asks for a command → detach
  -     ↳ Massena straightens. "You will not regret it, Sire." March him to Savoy and the front is his — the order is y…
- LEDGER treasury 9975 · net +1199 · threat 84 · provinces 29 (+0) · ceiling 20638 · army 126934 · vassals Holland 99 · Switzerland 98
  - NET income 2639 · trade 599 · admin 50 · tribute 337 · upkeep 1000 · charges 896 · contributions 110 · requisitions 75 · occupation 30 · blockade 375 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,212g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✓ Davout expresses caution about the route but proceeds. Davout begins marching to Bohemia (distance: 2). Moved to Munich. Route: Munich -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks with overwhelming force. Deroy gains the advantage over Archduke John. Casualties: Deroy 837, Archduke Jo…
  - ⚔ Deroy (lost 837) vs Archduke John (lost 1760) — Archduke John was close. A period of drilling could have changed the outcome.
  - verbs: move×1, wait×1, attack×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
- LEDGER treasury 11193 · net +1052 · threat 82 · provinces 29 (+0) · ceiling 20287 · army 125467 · vassals Holland 99 · Switzerland 97
  - NET income 2642 · trade 599 · admin 50 · tribute 337 · upkeep 984 · charges 1062 · contributions 110 · requisitions 75 · occupation 30 · blockade 375 · admiralty 90
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Davout [continues]: Davout marches to Franconia. 1 region to Bohemia.
- LEDGER treasury 12249 · net +901 · threat 80 · provinces 29 (+0) · ceiling 19828 · army 124293 · vassals Holland 99 · Switzerland 96
  - NET income 2646 · trade 599 · admin 50 · tribute 337 · upkeep 984 · charges 1217 · contributions 110 · requisitions 75 · occupation 30 · blockade 375 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Tyrol. Route: Tyrol -> Bohemia.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 155…
- CMD `end turn` → ✓ Turn 9 ended. Turn 10 begins!
- SPENT 1552g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Davout [completed]: Davout arrives at Bohemia. Davout: "It is done. I took the liberty of posting pickets."
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11682 · net +862 · threat 80 · provinces 30 (+1) · ceiling 18745 · army 125907 · vassals Holland 99 · Switzerland 95
  - NET income 2715 · trade 599 · admin 50 · tribute 337 · upkeep 976 · charges 1181 · contributions 150 · occupation 67 · blockade 375 · admiralty 90
- DISPATCH: Sire — Tyrol has fallen to our arms. The tricolor flies over it this morning.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 3052 gold.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 10 — Early February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #16 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Swabia and Tyrol stay ours by the treaty — titled. Status quo: Bohemia and Carniola stay Bavarian by the treaty. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney begins marching to Franconia (distance: 2). Moved to Swabia. Route: Swabia -> Franconia.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortif…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Bohemia, Carniola, Franconia, Munich.
  - saved `CMD-A_t10` → Game saved: CMD-A_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 1 action unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Ney [active]: Ney is marching to Franconia (2 turns remaining).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult demands to be heard → acknowledge
  -     ↳ Soult's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #17 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +3 (97 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 16876 · net +1715 · threat 43 · provinces 30 (+0) · ceiling 57690 · army 129715 · vassals Holland 100 · Switzerland 94
  - NET income 2721 · trade 635 · admin 50 · upkeep 1000 · charges 624 · occupation 67
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: Gold indemnity: 3052 gold from Britain to France.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 10
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift ×2)
  - LOG ai_ai_proposal_refused: 9 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 80 to 40.
  - LOG ai_ai_proposal_refused: 16 approaches from Bavaria and Austria are rebuffed (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (158 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ORDER Ney [completed]: Ney arrives at Franconia. Ney: "Done — and I trust the next order has more fire in it."
- LEDGER treasury 19139 · net +2236 · threat 45 · provinces 30 (+0) · ceiling 205416 · army 129446 · vassals Holland 99 · Switzerland 93
  - NET income 2801 · trade 635 · admin 50 · upkeep 1000 · charges 205 · occupation 45
- DISPATCH: Sire — Marshal Lannes's household goes unpaid. His patience erodes with his purse.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,351 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 11 courts rebuff Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Tyrol (field levy — no depot; capped at 3,000) - Cost: 300 gold (unstable region premium). Morale: 80% -> 71%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 300g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 21033 · net +2193 · threat 45 · provinces 30 (+0) · ceiling 203750 · army 132446 · vassals Holland 98 · Switzerland 92
  - NET income 2805 · trade 635 · admin 50 · upkeep 1024 · charges 228 · occupation 45
- DISPATCH: Sire — Lannes has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - TURN EVENTS 7
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  -     ↳ refused: The armistice with Austria holds for 2 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Bohemia to Franconia (199 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23231 · net +2397 · threat 45 · provinces 30 (+0) · ceiling 222916 · army 132247 · vassals Holland 97 · Switzerland 91
  - NET income 2810 · trade 635 · admin 50 · tribute 225 · upkeep 1024 · charges 254 · occupation 45
- DISPATCH: Sire — Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Franche-Comte and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 25685 · net +2424 · threat 45 · provinces 30 (+0) · ceiling 227666 · army 132247 · vassals Holland 96 · Switzerland 90
  - NET income 2852 · trade 635 · admin 50 · tribute 225 · upkeep 1024 · charges 284 · occupation 30
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −75, −85 and −75). The Balance of Europe names the price to keep each out.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #19 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (90 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 27643 · net +2157 · threat 45 · provinces 30 (+0) · ceiling 207333 · army 135247 · vassals Holland 95 · Switzerland 100
  - NET income 2857 · trade 635 · admin 50 · upkeep 1048 · charges 307 · occupation 30
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia (110 lost to march)
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Tyrol. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Franconia today.
- CMD `end turn` → ✓ Turn 16 ended. Turn 17 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: garrison×1, wait×1, recruit×1
- LEDGER treasury 29813 · net +2144 · threat 45 · provinces 30 (+0) · ceiling 208416 · army 135137 · vassals Holland 94 · Switzerland 100
  - NET income 2862 · trade 635 · admin 50 · upkeep 1040 · charges 333 · occupation 30
- DISPATCH: Sire — Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franche-Comte (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 31961 · net +2122 · threat 45 · provinces 30 (+0) · ceiling 208750 · army 135137 · vassals Holland 93 · Switzerland 100
  - NET income 2866 · trade 635 · admin 50 · upkeep 1040 · charges 359 · occupation 30
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 28 and declare on turn 31: Britain, Austria, Russia, Prussia and 4 lesser courts would march.
  - TURN EVENTS 5
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 34088 · net +2438 · threat 45 · provinces 30 (+0) · ceiling 237250 · army 135137 · vassals Holland 92 · Switzerland 100
  - NET income 2871 · trade 635 · admin 50 · tribute 337 · upkeep 1040 · charges 385 · occupation 30
- DISPATCH: Sire — the court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Tyrol to Franconia (148 lost to march)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 36530 · net +2413 · threat 45 · provinces 30 (+0) · ceiling 237583 · army 134989 · vassals Holland 91 · Switzerland 100
  - NET income 2875 · trade 635 · admin 50 · tribute 337 · upkeep 1040 · charges 414 · occupation 30
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as service to the strong.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-A_t20` → Game saved: CMD-A_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 38611 · net +2056 · threat 45 · provinces 30 (+0) · ceiling 209916 · army 134989 · vassals Holland 100 · Switzerland 100
  - NET income 2880 · trade 635 · admin 50 · upkeep 1040 · charges 439 · occupation 30
- DISPATCH: Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,224g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 40669 · net +2033 · threat 45 · provinces 30 (+0) · ceiling 210083 · army 134989 · vassals Holland 100 · Switzerland 100
  - NET income 2882 · trade 635 · admin 50 · upkeep 1040 · charges 464 · occupation 30
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Britain, Austria, Russia, Prussia and 4 lesser courts would march.
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, coercive_demand)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 42703 · net +2235 · threat 45 · provinces 30 (+0) · ceiling 228916 · army 134989 · vassals Holland 100 · Switzerland 100
  - NET income 2883 · trade 635 · admin 50 · tribute 225 · upkeep 1040 · charges 488 · occupation 30
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - TURN EVENTS 2
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty, blockade_begins, diplomatic_relation_shift)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Austria sign a Defensive Alliance
  - LOG ai_ai_proposal_refused: 8 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 44940 · net +2210 · threat 45 · provinces 30 (+0) · ceiling 229083 · army 134989 · vassals Holland 100 · Switzerland 100
  - NET income 2885 · trade 635 · admin 50 · tribute 225 · upkeep 1040 · charges 515 · occupation 30
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Russia, Britain, Austria and 4 lesser courts would march.
  - RAIL expedition_landed: THE LANDING: Paget has put 9,323 men ashore at Estonia.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% on…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 46897 · net +2156 · threat 45 · provinces 30 (+0) · ceiling 226500 · army 137989 · vassals Holland 100 · Switzerland 100
  - NET income 2886 · trade 635 · admin 50 · tribute 225 · upkeep 1072 · charges 538 · occupation 30
- DISPATCH: Sire — Russia enacts the War Ministry under Arakcheev — +5 morale from every drill.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Britain the loss of Uleaborg and 1 more province. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: naval_expedition×1, wait×1
- LEDGER treasury 49055 · net +2132 · threat 49 · provinces 30 (+0) · ceiling 226666 · army 137989 · vassals Holland 100 · Switzerland 100
  - NET income 2888 · trade 635 · admin 50 · tribute 225 · upkeep 1072 · charges 564 · occupation 30
- DISPATCH: Sire — Wellesley has put 5,000 men ashore at Stockholm.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Stockholm.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Uleaborg and 1 more — Britain is not forgiven
  - LOG ai_ai_proposal_refused: 13 approaches from Britain, Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden and Portugal rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 14 approaches from Britain, Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: 14 approaches from Britain, Austria and Sardinia are rebuffed (defensive alliance)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 51189 · net +2108 · threat 53 · provinces 30 (+0) · ceiling 226833 · army 137989 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 635 · admin 50 · tribute 225 · upkeep 1072 · charges 590 · occupation 30
- DISPATCH: Sire — Europe has watched us 21 quiet turns. At this pace the courts consult on turn 29 and declare on turn 32: Russia, Britain, Austria and 4 lesser courts would march. The cheapest court to keep ou…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Britain rebuffs Russia (design ask)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 53297 · net +2420 · threat 57 · provinces 30 (+0) · ceiling 254916 · army 137989 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 635 · admin 50 · tribute 562 · upkeep 1072 · charges 615 · occupation 30
- DISPATCH: Sire — relations between Britain and Russia have collapsed: Alliance → Defensive Alliance.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade ×2)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 55717 · net +2391 · threat 60 · provinces 30 (+0) · ceiling 254916 · army 137989 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 635 · admin 50 · tribute 562 · upkeep 1072 · charges 644 · occupation 30
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL expedition_landed: THE LANDING: Bennigsen has put 7,950 men ashore at Stockholm.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: 8 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 58108 · net +2362 · threat 58 · provinces 30 (+0) · ceiling 254916 · army 137989 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 635 · admin 50 · tribute 562 · upkeep 1072 · charges 673 · occupation 30
- DISPATCH: Sire — St Petersburg now pays London 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 7 turns (7 DP); buying off her design …
  - TURN EVENTS 3
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as service to the strong.
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% on…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-A_t30` → Game saved: CMD-A_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 60470 · net +2334 · threat 56 · provinces 30 (+0) · ceiling 254916 · army 137989 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 635 · admin 50 · tribute 562 · upkeep 1072 · charges 701 · occupation 30
- DISPATCH: Sire — The courts consult now and declare on turn 32: Russia, Britain, Austria and 3 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 61133 · net +453 · threat 54 · provinces 30 (+0) · ceiling 73988 · army 137989 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 599 · admin 50 · tribute 562 · upkeep 1072 · charges 2081 · occupation 30 · blockade 375 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_offensive_cascade: Austria has joined Britain's war against France, honoring their alliance.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 3 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sardinia has declared war on France, with 2 allied courts poised to follow.
  - RAIL +5 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And Austria stirs at its own design.
- DIPLO +13 medium/low (diplomatic_dp_regen, witness_strike_recorded ×2, diplomatic_treaty_broken, cs_tier_shift, blockade_begins ×3, diplomatic_relation_shift ×5)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG diplomatic_treaty_broken: Austria was forced to break the Peace Treaty with France (cascade).
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG coalition_declared: The Fourth Russian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia, Sweden

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, garrison×1, recruit×1
- LEDGER treasury 61590 · net +250 · threat 52 · provinces 30 (+0) · ceiling 68093 · army 136320 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 599 · admin 50 · tribute 562 · upkeep 1068 · charges 2288 · occupation 30 · blockade 375 · admiralty 90
- DISPATCH: Sire — Russia and France are at war. Russia tears up the Peace Treaty to do it.
  - TURN EVENTS 4
- DIPLO +6 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, paymaster_subsidy)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Ney. Casualties: Archduke Charl… · Archduke John's forces advance steadily. Archduke John gains the advantage over Ney. Casualties: Archduke John 738, Ney…
  - ⚔ Archduke Charles (lost 2454) vs Ney (lost 3242, own corps) — Murat marched to Ney's guns as ordered. It was not enough. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke John (lost 738) vs Ney (lost 3192) — A grievous defeat for Ney, Sire. The losses are severe.
  - verbs: attack×2, wait×1
- ORDER Ney [awaiting_response]: Ney is cornered at Bohemia with 4,523 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Bohemia with 4,523 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 61021 · net -265 · threat 50 · provinces 30 (+0) · ceiling 55669 · army 121198 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 599 · admin 50 · tribute 562 · upkeep 944 · charges 2927 · occupation 30 · blockade 375 · admiralty 90
- DISPATCH: Sire — Ney was mauled at Bohemia: a quarter of his corps — 3,242 men — lost in a single action.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 60758 · net -438 · threat 48 · provinces 30 (+0) · ceiling 52454 · army 119805 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 561 · admin 50 · tribute 562 · upkeep 928 · charges 3102 · occupation 30 · blockade 351 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL settlement_offer_arrival: Russia has offered terms to settle Russia vs Sweden.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Austria (defensive alliance)

## Turn 35 — Late February 1807
  - MAILBOX #13 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #21 → accept_settlement_offer
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #21 already answered this chain)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 60320 · net -601 · threat 46 · provinces 30 (+0) · ceiling 49571 · army 119805 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 561 · admin 50 · tribute 562 · upkeep 928 · charges 3265 · occupation 30 · blockade 351 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 29 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 5 approaches from Austria and Sardinia are rebuffed (defensive alliance)

## Turn 36 — Early March 1807
  - MAILBOX #13 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #21 → request_settlement_revision
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #21 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% on…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- SPENT 600g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 59111 · net -732 · threat 44 · provinces 30 (+0) · ceiling 46729 · army 122393 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 561 · admin 50 · tribute 562 · upkeep 944 · charges 3380 · occupation 30 · blockade 351 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 30 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade ×2, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 37 — Late March 1807
  - MAILBOX #13 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #21 → reject_settlement_offer
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 58379 · net -870 · threat 42 · provinces 30 (+0) · ceiling 44435 · army 121992 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 561 · admin 50 · tribute 562 · upkeep 944 · charges 3518 · occupation 30 · blockade 351 · admiralty 90
- DISPATCH: Sire — Russia and Sweden have made peace without us.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Russia and Sweden have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on…
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 38 — Early April 1807
  - MAILBOX #14 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #22 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
- LEDGER treasury 57517 · net -985 · threat 40 · provinces 30 (+0) · ceiling 42487 · army 120638 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 561 · admin 50 · tribute 562 · upkeep 936 · charges 3641 · occupation 30 · blockade 351 · admiralty 90
- DISPATCH: Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG third_party_peace: THE CONGRESS: Russia and Sweden make peace without France

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 56540 · net -1088 · threat 38 · provinces 30 (+0) · ceiling 40720 · army 119348 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 561 · admin 50 · tribute 562 · upkeep 928 · charges 3752 · occupation 30 · blockade 351 · admiralty 90
- DISPATCH: Sire — London now pays St Petersburg 500 gold a turn against us — her war with us is paid for.
  - RAIL settlement_offer_arrival: Russia has offered terms to settle Russia vs Sweden.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 40 — Early May 1807
  - MAILBOX #15 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → accept_settlement_offer
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #23 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franche-Comte (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-A_t40` → Game saved: CMD-A_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 55460 · net -1177 · threat 36 · provinces 30 (+0) · ceiling 39111 · army 118087 · vassals Holland 100 · Switzerland 100
  - NET income 2890 · trade 561 · admin 50 · tribute 562 · upkeep 920 · charges 3849 · occupation 30 · blockade 351 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

---
finished: **completed** · commands 200 · popups 49 · battles 13
