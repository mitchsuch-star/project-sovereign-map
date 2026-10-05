# Playtest digest — CMD-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `c14678984809` (dirty) · content `d4a1fdd2fc4f` · driver `e498338939cb`
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
  - LOG ai_ai_proposal_refused: 29 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
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
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia and Bavaria (open borders agreement)
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
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
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
- LEDGER treasury 8686 · net +1306 · threat 83 · provinces 29 (+0) · ceiling 20726 · army 129866 · vassals Holland 98 · Switzerland 98
  - NET income 2582 · trade 587 · admin 50 · tribute 337 · upkeep 1016 · charges 724 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned three turns ago, has been driven back.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_vassal_contingent)
  - LOG ai_ai_proposal_refused: 7 approaches from Austria, Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Milan instead.) → trust
  - ↳ MUSTER — Lannes (13,138; expect about 30,427 with the corps likely to arrive, up to 35,747 if all march) vs Archduke John (12,182 men) at Milan — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 939, own corps) vs Archduke John (lost 3375) — Davout arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire. — The corps system brought Davout in.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 9 actions, 2 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos delivers an effective strike. Castanos gains the advantage over Paget. Casualties: Castanos 648, Paget 1,563. … · Deroy's forces press forward aggressively. Deroy gains the advantage over Archduke John. Casualties: Deroy 1,095, Archd…
  - ⚔ Castanos (lost 648) vs Paget (lost 1563) — Paget's army has been badly mauled. Castanos proved the stronger force today. — The Line Holds +15% (Paget)
  - ⚔ Deroy (lost 1095) vs Archduke John (lost 1661) — Even the favorable ground could not save Archduke John, Sire. Deroy overcame the terrain.
  - verbs: wait×2, move×2, attack×2, retreat×1, stance_change×1, recruit×1
  - POPUP marshal_audience: shadow_command, Marshal Massena asks for a command → detach
  -     ↳ Massena straightens. "You will not regret it, Sire." March him to Savoy and the front is his — the order is y…
- LEDGER treasury 10271 · net +1519 · threat 84 · provinces 29 (+0) · ceiling 28699 · army 126879 · vassals Holland 99 · Switzerland 98
  - NET income 2639 · trade 587 · admin 50 · tribute 337 · upkeep 1000 · charges 681 · requisitions 75 · occupation 30 · blockade 368 · admiralty 90
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,212g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✓ Davout expresses caution about the route but proceeds. Davout begins marching to Bohemia (distance: 2). Moved to Munich. Route: Munich -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 9 actions, 4 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos takes Leon where he stands! Captured: Britain → Spain · Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 286, Paget … · Deroy takes Tyrol where he stands! Captured: Austria → Bavaria · Deroy engages in solid combat. Brutal stalemate between Deroy and Archduke John. Heavy casualties on both sides: Deroy …
  - 🏴 Spain: Castanos takes Leon where he stands! Captured: Britain → Spain
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Aragon!
  - 🏴 Bavaria: Deroy takes Tyrol where he stands! Captured: Austria → Bavaria
  - ⚔ Castanos (lost 286) vs Paget (lost 1429) — Paget held superior ground, yet Castanos prevailed. A grim day, Sire. And Paget was taken on that field — Spain holds h… — The Line Holds +15% (Paget)
  - ⚔ Deroy (lost 954) vs Archduke John (lost 1401) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×4, wait×2, retreat×1, stance_change×1, fortify×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
- LEDGER treasury 11809 · net +1380 · threat 82 · provinces 29 (+0) · ceiling 27922 · army 125412 · vassals Holland 99 · Switzerland 97
  - NET income 2642 · trade 587 · admin 50 · tribute 337 · upkeep 984 · charges 839 · requisitions 75 · occupation 30 · blockade 368 · admiralty 90
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, coercive_demand, agenda_shift)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy assaults the Milan garrison! Garrison collapses (6,000 -> 0). Deroy loses 1,666 troops in the assault. Deroy marc…
  - 🏴 Bavaria: [Materiel] Guns, horses and stores lost with the fallen: Bavaria -83g, Austria -150g. Captured: Austria → Bavaria
  - verbs: attack×1, wait×1
- ORDER Davout : Davout: 'Cannon fire at Milan, Sire. Investigate?'
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Milan, Sire. Investigate?' → investigate
- LEDGER treasury 13118 · net +1161 · threat 80 · provinces 29 (+0) · ceiling 26189 · army 124239 · vassals Holland 99 · Switzerland 96
  - NET income 2646 · trade 587 · admin 50 · tribute 337 · upkeep 984 · charges 987 · occupation 30 · blockade 368 · admiralty 90
- DISPATCH: Sire — Prussia would now join a league against us — relations −25. Courtship needs 2 turns; a league stands declared. She will march.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: 15 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Tyrol. Route: Tyrol -> Bohemia.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 155…
- CMD `end turn` → ✓ Turn 9 ended. Turn 10 begins!
- SPENT 1552g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult demands to be heard → acknowledge
  -     ↳ Soult's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #16 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Swabia stays ours by the treaty — titled. Status quo: Bohemia, Milan and Tyrol stay Bavarian by the treaty. → display-only
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 14756 · net +2461 · threat 78 · provinces 29 (+0) · ceiling 219833 · army 131064 · vassals Holland 99 · Switzerland 95
  - NET income 2679 · trade 587 · admin 50 · tribute 337 · upkeep 1024 · charges 153 · occupation 15
- DISPATCH: Sire — Prussia has declared war on Hanover. The stated cause: The Hanoverian Prize.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 1868 gold.
  - TURN EVENTS 9
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 78 to 39.
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 24 approaches from Bavaria and Prussia are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney begins marching to Franconia (distance: 2). Moved to Swabia. Route: Swabia -> Franconia.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Bohemia, Franconia, Milan, Munich, Tyrol.
  - saved `CMD-A_t10` → Game saved: CMD-A_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 1 action unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Ney [active]: Ney is marching to Franconia (2 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #17 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +3 (97 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 17238 · net +2116 · threat 42 · provinces 29 (+0) · ceiling 193500 · army 129873 · vassals Holland 100 · Switzerland 94
  - NET income 2684 · trade 587 · admin 50 · upkeep 1008 · charges 182 · occupation 15
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: Gold indemnity: 1868 gold from Britain to France.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 6
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift ×2)
  - LOG ai_ai_proposal_refused: 6 approaches from Britain and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 13 courts rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (158 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ORDER Ney [completed]: Ney arrives at Franconia. Ney: "Done — and I trust the next order has more fire in it."
- LEDGER treasury 19359 · net +2095 · threat 45 · provinces 29 (+0) · ceiling 193916 · army 129604 · vassals Holland 99 · Switzerland 93
  - NET income 2689 · trade 587 · admin 50 · upkeep 1008 · charges 208 · occupation 15
- DISPATCH: Sire — Marshal Lannes's household goes unpaid. His patience erodes with his purse.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,351 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: Britain rebuffs Denmark and Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 21458 · net +2074 · threat 45 · provinces 29 (+0) · ceiling 194250 · army 129604 · vassals Holland 98 · Switzerland 92
  - NET income 2693 · trade 587 · admin 50 · upkeep 1008 · charges 233 · occupation 15
- DISPATCH: Sire — Lannes has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  -     ↳ refused: The armistice with Austria holds for 2 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✓ Davout begins marching to Franconia (distance: 2). Moved to Tyrol. Route: Tyrol -> Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 1 action unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [active]: Davout is marching to Franconia (2 turns remaining).
- LEDGER treasury 23545 · net +2287 · threat 45 · provinces 29 (+0) · ceiling 214083 · army 128844 · vassals Holland 97 · Switzerland 91
  - NET income 2698 · trade 587 · admin 50 · tribute 225 · upkeep 1000 · charges 258 · occupation 15
- DISPATCH: Sire — Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
  - TURN EVENTS 4
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Franche-Comte and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [completed]: Davout arrives at Franconia. Davout: "Done, and done properly — no stragglers, no surprises."
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 25836 · net +2263 · threat 45 · provinces 29 (+0) · ceiling 214416 · army 128649 · vassals Holland 96 · Switzerland 90
  - NET income 2702 · trade 587 · admin 50 · tribute 225 · upkeep 1000 · charges 286 · occupation 15
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −75, −85 and −75). The Balance of Europe names the price to keep each out.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as alliance.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)

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
- LEDGER treasury 27633 · net +1998 · threat 45 · provinces 29 (+0) · ceiling 194083 · army 131649 · vassals Holland 95 · Switzerland 100
  - NET income 2707 · trade 587 · admin 50 · upkeep 1024 · charges 307 · occupation 15
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 11 courts rebuff Bavaria (open borders agreement)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia (110 lost to march)
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Tyrol. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Franconia today.
- CMD `end turn` → ✓ Turn 16 ended. Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 29644 · net +1987 · threat 45 · provinces 29 (+0) · ceiling 195166 · army 131539 · vassals Holland 94 · Switzerland 100
  - NET income 2712 · trade 587 · admin 50 · upkeep 1016 · charges 331 · occupation 15
- DISPATCH: Sire — Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: 9 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sardinia, Holland and Kingdom of Italy rebuff Bavaria (open borders agreement)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franche-Comte (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31635 · net +1967 · threat 45 · provinces 29 (+0) · ceiling 195500 · army 131539 · vassals Holland 93 · Switzerland 100
  - NET income 2716 · trade 587 · admin 50 · upkeep 1016 · charges 355 · occupation 15
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
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 33607 · net +2285 · threat 45 · provinces 29 (+0) · ceiling 224000 · army 131539 · vassals Holland 92 · Switzerland 100
  - NET income 2721 · trade 587 · admin 50 · tribute 337 · upkeep 1016 · charges 379 · occupation 15
- DISPATCH: Sire — Russia enacts Arakcheev's Artillery — artillery levies cost 15% less (×0.85).
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Tyrol to Franconia (117 lost to march)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 35896 · net +2262 · threat 45 · provinces 29 (+0) · ceiling 224333 · army 131422 · vassals Holland 91 · Switzerland 100
  - NET income 2725 · trade 587 · admin 50 · tribute 337 · upkeep 1016 · charges 406 · occupation 15
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
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 37826 · net +1907 · threat 45 · provinces 29 (+0) · ceiling 196666 · army 131422 · vassals Holland 100 · Switzerland 100
  - NET income 2730 · trade 587 · admin 50 · upkeep 1016 · charges 429 · occupation 15
- DISPATCH: Sire — the court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
  - TURN EVENTS 3
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 39735 · net +1886 · threat 45 · provinces 29 (+0) · ceiling 196833 · army 131422 · vassals Holland 100 · Switzerland 100
  - NET income 2732 · trade 587 · admin 50 · upkeep 1016 · charges 452 · occupation 15
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Britain, Austria, Russia, Prussia and 4 lesser courts would march.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 41622 · net +2089 · threat 45 · provinces 29 (+0) · ceiling 215666 · army 131422 · vassals Holland 100 · Switzerland 100
  - NET income 2733 · trade 587 · admin 50 · tribute 225 · upkeep 1016 · charges 475 · occupation 15
- DISPATCH: Sire — Sardinia and Austria have signed the Defensive Alliance.
  - TURN EVENTS 2
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Austria sign a Defensive Alliance
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 43713 · net +2066 · threat 45 · provinces 29 (+0) · ceiling 215833 · army 131422 · vassals Holland 100 · Switzerland 100
  - NET income 2735 · trade 587 · admin 50 · tribute 225 · upkeep 1016 · charges 500 · occupation 15
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Britain, Austria, Russia and 4 lesser courts would march.
  - TURN EVENTS 2
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as service to the strong.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% on…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 45529 · net +2017 · threat 45 · provinces 29 (+0) · ceiling 213583 · army 134422 · vassals Holland 100 · Switzerland 100
  - NET income 2736 · trade 587 · admin 50 · tribute 225 · upkeep 1044 · charges 522 · occupation 15
- DISPATCH: Sire — Russia enacts the War Ministry under Arakcheev — +5 morale from every drill.
  - TURN EVENTS 2
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 47548 · net +1995 · threat 49 · provinces 29 (+0) · ceiling 213750 · army 134422 · vassals Holland 100 · Switzerland 100
  - NET income 2738 · trade 587 · admin 50 · tribute 225 · upkeep 1044 · charges 546 · occupation 15
- DISPATCH: Sire — Prussia enacts the Krümper System — infantry manpower returns 25% faster.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 49545 · net +1973 · threat 53 · provinces 29 (+0) · ceiling 213916 · army 134422 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 587 · admin 50 · tribute 225 · upkeep 1044 · charges 570 · occupation 15
- DISPATCH: Sire — the court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 51518 · net +2286 · threat 57 · provinces 29 (+0) · ceiling 242000 · army 134422 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 587 · admin 50 · tribute 562 · upkeep 1044 · charges 594 · occupation 15
- DISPATCH: Sire — Austria enacts the New Infantry Regulations — +5 morale from every drill.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 53804 · net +2259 · threat 60 · provinces 29 (+0) · ceiling 242000 · army 134422 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 587 · admin 50 · tribute 562 · upkeep 1044 · charges 621 · occupation 15
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 56063 · net +2232 · threat 58 · provinces 29 (+0) · ceiling 242000 · army 134422 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 587 · admin 50 · tribute 562 · upkeep 1044 · charges 648 · occupation 15
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design costs 1…
  - TURN EVENTS 3
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% on…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-A_t30` → Game saved: CMD-A_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 58295 · net +2205 · threat 56 · provinces 29 (+0) · ceiling 242000 · army 134422 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 587 · admin 50 · tribute 562 · upkeep 1044 · charges 675 · occupation 15
- DISPATCH: Sire — St Petersburg now pays London 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 7 turns (7 DP); buying off her design …
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 58916 · net +419 · threat 54 · provinces 29 (+0) · ceiling 70806 · army 134422 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 587 · admin 50 · tribute 562 · upkeep 1044 · charges 2003 · occupation 15 · blockade 368 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Sweden, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 4 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +5 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And Sweden, Austria and Sardinia stir at their own designs.
- DIPLO +14 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken, blockade_begins ×3, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG coalition_declared: The Fourth British Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia, Sweden

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Ney. Casualties: Archduke C… · ArchdukeJohn marches from Bohemia into Tyrol unopposed! (420 lost to march) Captured: Bavaria → Austria · ArchdukeJohn assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 3,404 troops. Garriso… · ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,891 troops in the assa…
  - 🏴 Austria: ArchdukeCharles advances into Bohemia. (796 lost to march — forward supply lines reduce losses) Bohemia has been captured by Austria!
  - 🏴 Austria: ArchdukeJohn marches from Bohemia into Tyrol unopposed! (420 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -94g, Bavaria -125g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1916, own corps) vs Ney (lost 4041, own corps) — Reinforcements from Murat bolstered Ney's position — though Davout never arrived, Sire.
  - verbs: attack×4, form_square×1
- LEDGER treasury 58664 · net -63 · threat 52 · provinces 29 (+0) · ceiling 57265 · army 125295 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 587 · admin 50 · tribute 562 · upkeep 968 · charges 2561 · occupation 15 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Bohemia. He must reform before he fights again.
  - TURN EVENTS 7
- DIPLO +8 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke Charles is at Bohemia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Brutal stalemate between Archduke Charles and Ney. Heavy casualties on both s…
  - ⚔ Archduke Charles (lost 3484) vs Ney (lost 1054, own corps) — Soult failed to arrive in time. Ney's army fought without expected support.
  - verbs: form_square×2, attack×1, move×1, retreat×1, stance_change×1
- LEDGER treasury 58285 · net -321 · threat 50 · provinces 29 (+0) · ceiling 51960 · army 120665 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 587 · admin 50 · tribute 562 · upkeep 928 · charges 2859 · occupation 15 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — The last 4,000 of the garrison at Munich give way. Deroy marches from Milan into Munich unopposed! (651 lost to march —… · Deroy engages in solid combat. Brutal stalemate between Deroy and Archduke John. Heavy casualties on both sides: Deroy …
  - 🏴 Bavaria: Deroy marches from Milan into Munich unopposed! (651 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - ⚔ Deroy (lost 1058) vs Archduke John (lost 1345) — Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty.
  - verbs: move×2, attack×2, fortify×1
- LEDGER treasury 57958 · net -489 · threat 48 · provinces 29 (+0) · ceiling 48888 · army 119911 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 549 · admin 50 · tribute 562 · upkeep 920 · charges 3021 · occupation 15 · blockade 344 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 28 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).
  - LOG ai_ai_proposal_refused: 8 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 approaches from Austria and Sardinia are rebuffed (defensive alliance)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 10 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Brutal stalemate between Archduke Charles and Davout. Heavy casualties o… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Lannes. Casualties: Arc…
  - ⚔ Archduke Charles (lost 2686) vs Davout (lost 1703, own corps) — The enemy's assault has weakened our works. We must repair or consider withdrawal.
  - ⚔ Archduke Charles (lost 2248, own corps) vs Lannes (lost 1914, own corps) — Lannes was close. A period of drilling could have changed the outcome.
  - verbs: attack×2, stance_change×2, recruit×2, move×1, retreat×1, break_square×1, wait×1
- LEDGER treasury 56977 · net -798 · threat 46 · provinces 29 (+0) · ceiling 44012 · army 111039 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 549 · admin 50 · tribute 562 · upkeep 864 · charges 3386 · occupation 15 · blockade 344 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Franconia instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Franconia instead.) → trust
  - ↳ MUSTER — Ney (5,478; expect about 35,521 with the corps likely to arrive) vs Archduke Charles (37,776 men) at Franconia — the balance of force looks even — a hard fight that may go against us.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1209, own corps) vs Archduke Charles (lost 2810, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% on…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- SPENT 600g on this turn's orders
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Schwarzenberg delivers an effective strike. Schwarzenberg gains the advantage over Lannes. Casualties: Schwarzenberg's …
  - 🏴 Austria: [!] No word came for Ney, cornered at Franconia — the enemy did not wait. [!] MARSHAL CAPTURED — Ney is taken by Austria at Franconia!
  - ⚔ Archduke Charles (lost 1404, own corps) vs Lannes (lost 1586, own corps) — Ney arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Schwarzenberg (lost 114, own corps) vs Lannes (lost 1548, own corps) — Soult failed to arrive in time. Lannes's army fought without expected support.
  - verbs: attack×2, wait×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franconia with 2,836 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franconia with 2,836 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 54653 · net -1172 · threat 44 · provinces 29 (+0) · ceiling 38810 · army 93912 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 549 · admin 50 · tribute 562 · upkeep 728 · charges 3896 · occupation 15 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 6
- DIPLO +6 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade ×4, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Britain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Sardinia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria · ArchdukeCharles assaults the Munich garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,824 troops in th… · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,025 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,702 troops in the…
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -91g, Bavaria -150g. Captured: Bavaria → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -85g, Bavaria -125g. Captured: Bavaria → Austria
  - verbs: attack×4, form_square×1
- LEDGER treasury 53457 · net -1272 · threat 42 · provinces 29 (+0) · ceiling 36974 · army 92780 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 462 · admin 50 · tribute 562 · upkeep 720 · charges 3972 · occupation 15 · blockade 289 · admiralty 90
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, move×1
- LEDGER treasury 52193 · net -1327 · threat 40 · provinces 29 (+0) · ceiling 35681 · army 91671 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 462 · admin 50 · tribute 562 · upkeep 712 · charges 4035 · occupation 15 · blockade 289 · admiralty 90
- DISPATCH: Sire — Marshal Davout's household goes unpaid. His patience erodes with his purse.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke John is at Franconia, just one region away.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Bernadotte recruits 10,000 infantry (nearest to capital) - Cost: 450 gold (capital discount) (×3 at war). Morale: 50% -> 43%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 450g on this turn's orders
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2, form_square×2, move×2
- LEDGER treasury 50355 · net -1406 · threat 38 · provinces 29 (+0) · ceiling 33531 · army 100584 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 462 · admin 50 · tribute 562 · upkeep 784 · charges 4042 · occupation 15 · blockade 289 · admiralty 90
- DISPATCH: Sire — London now pays St Petersburg 500 gold a turn against us — her war with us is paid for.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franche-Comte (+2% defense).
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
  - saved `CMD-A_t40` → Game saved: CMD-A_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×1, wait×1
- LEDGER treasury 48957 · net -1431 · threat 36 · provinces 29 (+0) · ceiling 32460 · army 99519 · vassals Holland 100 · Switzerland 100
  - NET income 2740 · trade 462 · admin 50 · tribute 562 · upkeep 776 · charges 4075 · occupation 15 · blockade 289 · admiralty 90
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us — her war with us is paid for.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria

---
finished: **completed** · commands 200 · popups 43 · battles 22
