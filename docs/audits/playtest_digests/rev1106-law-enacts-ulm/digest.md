# Playtest digest — rev1106-law-enacts-ulm

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 800.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2125, own corps) vs Mack (lost 20983) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Murat and Bernadotte never arrived, S… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 2753) vs Bernadotte (lost 4169, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. Prussia paid 30 gold into the treasury. → display-only
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 950 · net +687 · threat 72 · provinces 28 · ceiling 7066 · army 175742 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2950 · blockade 250 · admiralty 90
- DISPATCH: Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 983.
- CMD `enact the Anticipated Class` → ✓ The Anticipated Class (the senatus-consultes calling the class early, 1806–07): The Senate calls each year's conscripts before their time: infantry manpower returns 25% …
  - POPUP clarification: The Council of State, The Anticipated Class (the senatus-consultes calling the class early, 1806–07): The Senate calls each year's conscripts before their time: infantry manpower returns 25% faster. 15 authority now, then 150 gold a turn. Authority 100 → 85 — the marshals' calm holds above 70. The treasury holds 983 gold. Enact it? (yes / no) → 1 (first option: Enact the Anticipated Class)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (19,309; expect about 115,278 with the corps likely to arrive, up to 120,589 if all march; certain 19,309; a bad day (1 in 10) 102,177) vs Mack (substantial…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 438, own corps) vs Mack (lost 27183) — Davout, Massena and Napoleon arrived to reinforce Ney, but Teulie failed to reach the field in time. And Mack was taken… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte · Archduke Charles attacks Deroy · Archduke Charles attacks Murat
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - 🏴 Austria: Archduke Charles attacks Deroy — Swabia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1147) vs Bernadotte (lost 6916) — Where was Ney? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 1337) vs Deroy (lost 9004) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2319) vs Murat (lost 5509) — Murat stood alone, Sire. Ney never came.
  - verbs: attack×3, wait×1
- ENVOYS WAITING 2 · Naples open borders · Portugal open borders
- LEDGER treasury 1016 · net +750 · threat 78 · provinces 28 (+0) · ceiling 6129 · army 155351 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 92
  - NET income 2575 · trade 425 · admin 50 · tribute 937 · upkeep 2666 · contributions 65 · blockade 266 · admiralty 90 · laws 150
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — joining the stronger side for pay is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, law_enacted_abroad, province_changed_hands ×2, diplomatic_dp_regen, agenda_shift)

## Turn 3 — Late October 1805
  - LETTER Naples: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 1,173.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✓ The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1…
  - POPUP clarification: The Council of State, The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1 loyalty a turn in every one. 15 authority now, then 100 gold a turn. Authority 94 → 79 — the marshals' calm holds above 70; the Presence +10% → +9%. The treasury holds 1,173 gold. Enact it? (yes / no) → 1 (first option: Enact the Code Abroad)
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia, Bavaria's province, retaken — handed back to Bavaria. (168 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 716 gold (×3 at war) (×1.19 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 actions unused) Turn 4 begins!
- SPENT 716g on this turn's orders
- enemy phase: 8 actions, 0 attacks — Russia, Prussia, Spain and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×2, wait×2, fortify×1, naval_expedition×1, retreat×1, move×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1836, own corps) vs Archduke Charles (lost 9428) — Lannes, Massena and Napoleon arrived to reinforce Murat, but Ney and Davout failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 1655 · net +1535 · threat 76 · provinces 28 (+0) · ceiling 11690 · army 147711 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 92
  - NET income 2561 · trade 475 · admin 50 · tribute 937 · upkeep 1850 · blockade 298 · admiralty 90 · laws 250
- DISPATCH: Sire — Ney, Davout and Bernadotte stand 43,792 men at Munich, which feeds 37,500. 6,292 too many. 6,911 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for …
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 1,746.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% now, 12% at dawn (the m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3401 · net +1429 · threat 74 · provinces 28 (+0) · ceiling 12241 · army 144285 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2562 · trade 550 · admin 50 · tribute 937 · upkeep 1760 · charges 226 · blockade 344 · admiralty 90 · laws 250
- DISPATCH: Sire — Lannes, Murat, Massena and Napoleon stand 67,493 men at Franche-Comte, which feeds 52,500. 14,993 too many. 7,313 men lost in 3 turns. No depot may be laid at Franche-Comte — town regions don'…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 5 — Late November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 3,551.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Ney marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Ney, muster_confirm, Berthier stays the order a moment, Sire: before Ney marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Ney attacks Archduke Charles' to read the muster before you commit — it costs nothing.
MUSTER — Ney (16,987) vs Archduke Charles (substantial force) at Franconia — the balance of force looks unfavorable.
  WILL NOT — Davout: is dug in and will not abandon his works
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  What Franconia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 16,987 we muster) would cost ~127g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 74/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP; 2 for Bernadotte, who stands neutral) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Ney (16,987) vs Archduke Charles (substantial force) at Franconia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 4590) vs Archduke Charles (lost 1613) — Not one corps reached Ney. Bernadotte was expected; Ney fought the battle single-handed.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (130 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 7 actions, 1 attacks — Russia, Prussia, Spain and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Teulie
  - ⚔ Archduke John (lost 1073) vs Teulie (lost 2244) — Teulie stood alone, Sire. Bernadotte never came.
  - verbs: unfortify×2, form_square×2, attack×1, move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (86 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 4523 · net +860 · threat 72 · provinces 28 (+0) · ceiling 9552 · army 135435 · vassals Holland 96 · Kingdom of Italy 93 · Switzerland 96
  - NET income 2564 · trade 612 · admin 50 · tribute 694 · upkeep 1908 · charges 430 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — Ney's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)

## Turn 6 — Early December 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 4,523.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 7 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Paget
  - ⚔ Castanos (lost 228) vs Paget (lost 1305) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better. — The Line Holds +15% (Paget)
  - verbs: wait×2, move×2, unfortify×1, attack×1, form_square×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
- LEDGER treasury 5429 · net +740 · threat 70 · provinces 28 (+0) · ceiling 9678 · army 132425 · vassals Holland 97 · Kingdom of Italy 94 · Switzerland 96
  - NET income 2566 · trade 612 · admin 50 · tribute 698 · upkeep 1868 · charges 596 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — 5 turns of famine at Franche-Comte now. 12,564 men gone, and not one of them to the enemy. No depot may be laid at Franche-Comte — town regions don't support buildings (need city or larger). L…
  - TURN EVENTS 8
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)

## Turn 7 — Late December 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 5,429.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✓ Davout respectfully raises concerns: 'That road to Bohemia runs through enemy country, Sire. It is dangerous.' (Trust him and he will fortify current position instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'That road to Bohemia runs through enemy country, Sire. It is dangerous.' (Trust him and he will fortify current position instead.) → trust
- CMD `Murat, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Murat attacks Archduke Charles' to read the muster before you commit — it costs nothing.
MUSTER — Murat (12,696) vs Archduke Charles (27,780 men) at Franconia — the balance of force looks unfavorable.
  WILL NOT — Davout: is dug in and will not abandon his works
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Murat' and he will march
  WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Franconia would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: Archduke Charles stands +31% on the defense (his stance, his character and his works).
  Franconia feeds 32,000 — the whole muster can stand there fed. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 12,696 we muster) would cost ~95g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 70/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP; 2 for Soult, Bernadotte, who stand neutral) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Murat (12,696) vs Archduke Charles (27,780 men) at Franconia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 6855) vs Archduke Charles (lost 440, own corps) — Murat held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 9 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Cuesta attacks Paget
  - ⚔ Cuesta (lost 48) vs Paget (lost 634) — Paget was driven from the field. His men are scattered. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - verbs: break_square×3, fortify×2, wait×2, attack×1, drill×1
- LEDGER treasury 6113 · net +827 · threat 68 · provinces 28 (+0) · ceiling 10616 · army 122589 · vassals Holland 96 · Kingdom of Italy 93 · Switzerland 94
  - NET income 2567 · trade 612 · admin 50 · tribute 703 · upkeep 1628 · charges 755 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — Murat's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 10
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Saxony and Austria sign a Non-Aggression Pact
  - LOG moment: Russia decrees the Magazines for 8 turns (5 authority)

## Turn 8 — Early January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 6,113.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Davout, attack Archduke Charles` → ✗ Davout is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 2). Moved to Munich. Route: Munich -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Davout and Murat: Murat turns openly discontent (trust -3; expect defiance).
  - POPUP diplomatic_dialogue: moment_letter #12 → reject_ai_proposal
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 6650 · net +424 · threat 66 · provinces 28 (+0) · ceiling 8916 · army 118670 · vassals Holland 97 · Kingdom of Italy 94 · Switzerland 94
  - NET income 2569 · trade 612 · admin 50 · tribute 707 · upkeep 1924 · charges 868 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 9 — Late January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 6,650.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Franche-Comte and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Franche-Comte (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Co…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
- ORDER Massena [completed]: Massena arrives at Milan. Massena: "It is done. Point me at something that shoots back, Sire."
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 6529 · net +754 · threat 64 · provinces 28 (+0) · ceiling 10494 · army 119370 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2570 · trade 612 · admin 50 · tribute 712 · upkeep 1608 · charges 860 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — Prussia enacts the Military Reorganisation Commission — +5 morale from every drill.
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War for Franconia — Britain + Austria + Russia.
  - TURN EVENTS 6
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)

## Turn 10 — Early February 1806
  - MAILBOX #11 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Franconia — the table with Austria + Russia (4 pairs resolved). Status quo: Franconia stays Austrian by the treaty. Prisoners: Mack, our captive, goes home to Vienna under this peace — an Austrian commander back in the field. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 6,529.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Davout, fortify` → ✗ Davout is already fortified at Munich (+12% defense).
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney demands to be heard → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 7436 · net +739 · threat 34 · provinces 28 (+0) · ceiling 11787 · army 117748 · vassals Holland 99 · Kingdom of Italy 98 · Switzerland 94
  - NET income 2572 · trade 612 · admin 50 · tribute 712 · upkeep 1564 · charges 921 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL settlement_summary: Sire, the white peace of the War for Franconia — the table with Austria + Russia takes nothing and gives nothing. Bavaria is left out: -7 relation.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 6,000 men ashore at Andalusia.
  - RAIL allegiance_in_play: The allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Alle…
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 9
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Bavaria eases over Revanche — joining the stronger side for pay is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_coalition_dissolved, province_changed_hands, diplomatic_dp_regen, diplomatic_vassal_contingent, agenda_shift)
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 64 to 32; Britain remains at war with us.
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 11 — Late February 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 7,436.
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke John` → ✓ Archduke John stands at Franconia, two marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −108g more a turn. Pursue him (2 AP — …
  - POPUP clarification: Ney, pursuit_ask, Archduke John stands at Franconia, two marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −108g more a turn. Pursue him (2 AP — a standing order; the first march takes Ney to Swabia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke John (2 AP))
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Franche-Comte and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 7 actions, 3 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Castanos · Castanos attacks Andalusia · Castanos attacks Andalusia
  - ⚔ Castanos (lost 813) vs Shrapnel (lost 1155) — Stalemate. Shrapnel and Castanos glare at each other across the field. — The Line Holds +15% (Shrapnel)
  - ⚔ Castanos (lost 677) vs Shrapnel (lost 865) — Neither Shrapnel nor Castanos could claim the field. The armies remain locked. — The Line Holds +15% (Shrapnel)
  - verbs: attack×3, wait×2, recruit×2
- LEDGER treasury 8197 · net +612 · threat 36 · provinces 28 (+0) · ceiling 11733 · army 116095 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 94
  - NET income 2574 · trade 612 · admin 50 · tribute 712 · upkeep 1544 · charges 1070 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — intelligence reports Britain has raised Wellesley to high command.
  - TURN EVENTS 3
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- DIPLO +2 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 12 — Early March 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 8,197.
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the nex…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 90% -> 79%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 600g on this turn's orders
- enemy phase: 7 actions, 3 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Castanos · Castanos attacks Andalusia · Castanos attacks Andalusia
  - ⚔ Castanos (lost 594) vs Shrapnel (lost 891) — Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty. — The Line Holds +15% (Shrapnel)
  - ⚔ Castanos (lost 369) vs Shrapnel (lost 775) — Even Shrapnel's fortifications could not hold, Sire. Castanos overran the position. — The Line Holds +15% (Shrapnel)
  - verbs: attack×3, fortify×1, move×1, recruit×1, wait×1
- LEDGER treasury 8272 · net +564 · threat 38 · provinces 28 (+0) · ceiling 11471 · army 117407 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2575 · trade 612 · admin 50 · tribute 712 · upkeep 1560 · charges 1103 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,272g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 8
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 13 — Late March 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 8,272.
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #16 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #17 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 2 more turns.
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 8 actions, 2 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Cuesta attacks Shrapnel · Castanos attacks Andalusia
  - 🏴 Spain: Castanos attacks Andalusia — Region captured: Andalusia (was Britain) (secured)
  - ⚔ Cuesta (lost 168) vs Shrapnel (lost 1395) — The toll on Shrapnel's forces is heavy, Sire. This defeat will be felt. And Shrapnel was taken on that field — Spain ho… — The Line Holds +15% (Shrapnel)
  - verbs: attack×2, unfortify×1, retreat×1, stance_change×1, move×1, grant_pension×1, wait×1
- LEDGER treasury 8858 · net +686 · threat 40 · provinces 28 (+0) · ceiling 12680 · army 115777 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2577 · trade 612 · admin 50 · tribute 937 · upkeep 1540 · charges 1228 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - RAIL allegiance_settled: The bidding for Bavaria is closed in our favour, but our relations are too cool for any pact the table can sign.
  - TURN EVENTS 4
- COURTS: The court of Bavaria hardens over Revanche — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, coercive_demand)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)

## Turn 14 — Early April 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 8,858.
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Franche-Comte (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 2 · Britain settlement offer · The Secretariat moment letter
- LEDGER treasury 9553 · net +546 · threat 42 · provinces 28 (+0) · ceiling 12542 · army 114204 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2578 · trade 612 · admin 50 · tribute 937 · upkeep 1532 · charges 1377 · blockade 382 · admiralty 90 · laws 250
- DISPATCH: Sire — Asturias has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Asturias.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle the War with Britain.
  - TURN EVENTS 5
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: And Saxony stirs at its own design.
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 15 — Late April 1806
  - MAILBOX #12 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #13 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #19 → reject_ai_proposal
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #20 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with Britain — the table with Britain (3 pairs resolved). Status quo: Asturias stays British by the treaty. → display-only
  - POPUP diplomatic_dialogue: moment_letter #19 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `enact the Staff` → ✓ The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day…
  - POPUP clarification: The Council of State, The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day. 9,000 gold now, then 300 gold a turn; one more order each day from the next refill. The treasury holds 9,553 gold. Enact it? (yes / no) → 1 (first option: Enact the Grand Quartier Général)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 9000g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 3293 · net +2636 · threat 45 · provinces 28 (+0) · ceiling 29650 · army 112681 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2580 · trade 612 · admin 50 · tribute 937 · upkeep 864 · charges 129 · laws 550
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +9% this morning; the courts have begun to notice that he can be beaten.
  - RAIL settlement_summary: Sire, the white peace of the War with Britain — the table with Britain takes nothing and gives nothing. Spain is left out: -18 relation and a grievan…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL +2 more
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- COURTS: And Britain, Bavaria and Russia stir at their own designs.
- DIPLO +7 medium/low (province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land
  - LOG ai_ai_proposal_refused: 4 approaches to Bavaria, Prussia and Hanover are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 3 approaches from Saxony, Prussia and Hesse are rebuffed (design ask)

## Turn 16 — Early May 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +1 (99 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 15).
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 2 actions unused) Turn 17 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 7 other courts stirred as well, but their formations remain beyond our sight. — Brunswick attacks Alten · Brunswick attacks Wallmoden
  - 🏴 Prussia: Brunswick attacks Wallmoden — Osnabruck CAPTURED! (was Hanover) (secured)
  - ⚔ Brunswick (lost 656) vs Alten (lost 2949) — Not one corps reached Alten. Wallmoden was expected; Alten fought the battle single-handed. And Alten was taken on that… — Frederick's Drill +10% (Brunswick)
  - ⚔ Brunswick (lost 358) vs Wallmoden (lost 1323) — A grievous defeat for Wallmoden, Sire. The losses are severe. And Wallmoden was taken on that field — Prussia holds him. — Frederick's Drill +10% (Brunswick)
  - verbs: attack×2, wait×1
- LEDGER treasury 5594 · net +2071 · threat 45 · provinces 28 (+0) · ceiling 26300 · army 111209 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2582 · trade 612 · admin 50 · tribute 600 · upkeep 864 · charges 359 · laws 550
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +4 medium/low (province_changed_hands, diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria, Saxony and Prussia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)

## Turn 17 — Late May 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 15).
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified.…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 2 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 7674 · net +1872 · threat 45 · provinces 28 (+0) · ceiling 26390 · army 109783 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2583 · trade 612 · admin 50 · tribute 600 · upkeep 856 · charges 567 · laws 550
- DISPATCH: Sire — Hesse moves toward war with Hanover. The design is open; the timing is not.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - RAIL crisis_brewing: THE BREWING CRISIS: Hesse will move on Hanover. You may compensate (1,320g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war…
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,617 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 6
- COURTS: The court of Saxony eases over The Wettin Crown — joining the stronger side for pay is now the length of its tether.
- DIPLO +6 medium/low (law_enacted_abroad, province_changed_hands ×2, diplomatic_dp_regen, agenda_shift ×2)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 1 more — Prussia is not forgiven
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 18 — Early June 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 15).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 9564 · net +1701 · threat 45 · provinces 28 (+0) · ceiling 26570 · army 108405 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2585 · trade 612 · admin 50 · tribute 600 · upkeep 840 · charges 756 · laws 550
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Austria, Russia, Prussia and 3 lesser courts would march. Bound for now b…
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Austria.
  - RAIL crisis_passed: Hesse stands down over Hanover, Sire — the moment passed — opportunism decayed.
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Austria sign a Defensive Alliance
  - LOG ai_ai_proposal_refused: Austria rebuffs Hanover (open borders agreement)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 19 — Late June 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 15).
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 11228 · net +1498 · threat 45 · provinces 28 (+0) · ceiling 26200 · army 107072 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2586 · trade 574 · admin 50 · tribute 600 · upkeep 840 · charges 922 · laws 550
- DISPATCH: Sire — Britain would now join a league against us — relations −85. The price to keep her out: Talleyrand brings her to −10 in 9 turns (9 DP); buying off her design costs 1,044 gold and shortens the r…
  - RAIL allegiance_in_play: The allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Alle…
  - TURN EVENTS 3
- COURTS: The court of Bavaria hardens over Revanche — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)

## Turn 20 — Early July 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 15).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 12760 · net +1378 · threat 45 · provinces 28 (+0) · ceiling 26540 · army 105542 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2588 · trade 574 · admin 50 · tribute 600 · upkeep 808 · charges 1076 · laws 550
- DISPATCH: Sire — the moment passes: Bavaria no longer weighs the flip, and the bidding is closed.
  - RAIL allegiance_settled: The moment passes: Bavaria no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG moment: The Relief of Santo Domingo — an affair of state is laid before the Emperor
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 21 — Late July 1806
  - MAILBOX #15 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #23 → reject_ai_proposal
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — 'Lannes, recruit' raises them at Franche-Comte. Nothing was spent.
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1, recruit×1
- LEDGER treasury 14140 · net +1242 · threat 45 · provinces 28 (+0) · ceiling 26560 · army 104004 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 600 · upkeep 808 · charges 1214 · laws 550
- DISPATCH: Sire — the allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegiance.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Defensive Alliance → Non-Aggression)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG moment: The Relief of Santo Domingo — the Emperor answers: Ferrand must hold alone

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 15406 · net +1140 · threat 45 · provinces 28 (+0) · ceiling 26800 · army 102529 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 600 · upkeep 784 · charges 1340 · laws 550
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Britain, Austria, Russia, Prussia and 3 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified.…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, wait×1
- LEDGER treasury 16554 · net +1370 · threat 45 · provinces 28 (+0) · ceiling 30250 · army 101115 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 776 · charges 1455 · laws 550
- DISPATCH: Sire — the allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegiance.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 17932 · net +1240 · threat 45 · provinces 28 (+0) · ceiling 30330 · army 99754 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 768 · charges 1593 · laws 550
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Austria, Russia, Prussia and 3 lesser courts would march.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Russia eases over The Gulf and the Straits — joining the stronger side for pay is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 25 — Late September 1806
  - MAILBOX #16 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #24 → reject_ai_proposal
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 19172 · net +1116 · threat 45 · provinces 28 (+0) · ceiling 30330 · army 98389 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 768 · charges 1717 · laws 550
- DISPATCH: Sire — Europe has watched us 19 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Austria, Russia, Prussia and 3 lesser courts would march. The cheapest court t…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 5 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 20304 · net +1019 · threat 49 · provinces 28 (+0) · ceiling 30490 · army 97080 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 752 · charges 1830 · laws 550
- DISPATCH: Sire — the court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 84%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 21110 · net +930 · threat 53 · provinces 28 (+0) · ceiling 30410 · army 98735 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 760 · charges 1911 · laws 550
- DISPATCH: Sire — the bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 22048 · net +845 · threat 57 · provinces 28 (+0) · ceiling 30490 · army 97443 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 752 · charges 2004 · laws 550
- DISPATCH: Sire — Europe has watched us 22 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Austria, Russia, Prussia and 3 lesser courts would march. The cheapest court t…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified.…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 22901 · net +767 · threat 60 · provinces 28 (+0) · ceiling 30570 · army 96200 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 744 · charges 2090 · laws 550
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover and Sardinia alarmed (threat: 60)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 23676 · net +698 · threat 58 · provinces 28 (+0) · ceiling 30650 · army 95006 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 736 · charges 2167 · laws 550
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design costs 1…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 actions unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 24390 · net +642 · threat 56 · provinces 28 (+0) · ceiling 30810 · army 93856 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 720 · charges 2239 · laws 550
- DISPATCH: Sire — St Petersburg now pays Sweden 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design …
  - RAIL allegiance_in_play: The allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Alle…
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)
  - LOG moment: The Remounts — an affair of state is laid before the Emperor

## Turn 32 — Early January 1807
  - MAILBOX #17 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #25 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 23620 · net -747 · threat 54 · provinces 28 (+0) · ceiling 17551 · army 92749 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 1236 · charges 2663 · blockade 359 · admiralty 90 · laws 550
- DISPATCH: Sire — Britain, Russia, Austria, Sweden, Hanover and Sardinia are at war with France. Britain tears up the Peace Treaty to do it. Russia tears up the Peace Treaty to do it. Austria tears up the Peace…
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Sweden, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 3 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +7 more
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- COURTS: And Russia, Sardinia, Britain, Bavaria and Hesse stir at their own designs.
- DIPLO +15 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken, blockade_begins ×4, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).
  - LOG coalition_declared: The Fourth Austrian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia and Sweden
  - LOG moment: The Remounts — the Emperor answers: Let the depots wait

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — 'Lannes, recruit' raises them at Franche-Comte. Nothing was spent.
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 3 actions unused) Turn 34 begins!
- enemy phase: 11 actions, 6 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Wellesley attacks Galicia · Archduke Charles attacks Davout · Archduke John attacks Davout · Archduke Charles attacks Bernadotte
  - 🏴 Britain: Wellesley attacks Galicia — Region captured: Galicia (was Spain) (secured)
  - 🏴 Hanover: Alten attacks Artois — Region captured: Artois (was France) (secured)
  - 🏴 Hanover: Wallmoden attacks Picardy — Region captured: Picardy (was France) (secured)
  - ⚔ Archduke Charles (lost 2989) vs Davout (lost 1308, own corps) — Ney and Napoleon arrived in time to steady Davout's position. The field was held, nothing further. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke John (lost 812, own corps) vs Davout (lost 2625) — Stalemate. Davout and Archduke John glare at each other across the field.
  - ⚔ Archduke Charles (lost 140, own corps) vs Bernadotte (lost 1155) — Bernadotte held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×6, unfortify×2, move×2, recruit×1
- LEDGER treasury 21765 · net -1395 · threat 52 · provinces 26 (-2) · ceiling 13191 · army 86010 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2433 · trade 574 · admin 50 · tribute 937 · upkeep 1100 · charges 3217 · contributions 73 · blockade 359 · admiralty 90 · laws 550
- DISPATCH: Sire — Artois has fallen to Hanover. Enemy colours fly over French homeland soil. Alten's corps of ~2,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any…
  - TURN EVENTS 5
- DIPLO +9 medium/low (province_changed_hands ×3, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Sweden
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Britain sign a Defensive Alliance
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Hanover (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 11 actions, 4 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Deroy · Archduke Charles attacks Tyrol · Archduke Charles attacks Tyrol · Archduke Charles attacks Tyrol
  - ⚔ Archduke Charles (lost 4722) vs Deroy (lost 2333, own corps) — The engagement proceeded as one might expect, Sire.
  - ⚔ Archduke Charles (lost 3253, own corps) vs Deroy (lost 2964, own corps) — Stalemate. Deroy and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 3308) vs Deroy (lost 2364, own corps) — Neither Deroy nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 2883) vs Deroy (lost 1979, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: move×6, attack×4, recruit×1
- LEDGER treasury 20365 · net -1246 · threat 50 · provinces 26 (+0) · ceiling 12893 · army 85136 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2435 · trade 574 · admin 50 · tribute 937 · upkeep 1100 · charges 3063 · contributions 80 · blockade 359 · admiralty 90 · laws 550
- DISPATCH: Sire — Artois and Picardy lie in enemy hands. Hanover holds them.
  - RAIL allegiance_settled: The bidding for Saxony is closed in our favour, but our relations are too cool for any pact the table can sign.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Carniola and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +8 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_we_threshold ×2, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 500g reaches Sweden

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified.…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 3 actions unused) Turn 36 begins!
- enemy phase: 5 actions, 3 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Tyrol · Archduke Charles attacks Carniola · Archduke Charles attacks Carniola
  - 🏴 Austria: Archduke Charles attacks Tyrol — Region captured: Tyrol (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 2502) vs Deroy (lost 2281) — Stalemate. Deroy and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 2176) vs Deroy (lost 1706) — Neither Deroy nor Archduke Charles could claim the field. The armies remain locked.
  - verbs: attack×3, fortify×1, move×1
- LEDGER treasury 19128 · net -1099 · threat 48 · provinces 26 (+0) · ceiling 12690 · army 84298 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2436 · trade 574 · admin 50 · tribute 937 · upkeep 1092 · charges 2925 · contributions 80 · blockade 359 · admiralty 90 · laws 550
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - TURN EVENTS 4
- DIPLO +5 medium/low (province_changed_hands ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Russia
  - LOG design_promoted: REVANCHE: Austria swears to retake Carniola and 1 more — Bavaria is not forgiven
  - LOG moment: Russia decrees the Magazines for 8 turns (2,500 gold)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Tyrol instead.)
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Tyrol instead.) → trust
  - ↳ MUSTER — Massena (26,057; expect about 34,394 with the corps likely to arrive, up to 34,595 if all march; certain 26,057) vs Archduke Charles (30,910 men) at Tyrol — the balance of force looks even — a hard fight that may go against us.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 2511, own corps) vs Archduke Charles (lost 3303) — Reinforcement from Teulie kept Massena standing, Sire — but neither side yielded the ground.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- enemy phase: 8 actions, 4 attacks — Britain, Prussia, the Ottoman Empire and 7 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Deroy · Archduke Charles attacks Deroy · Cuesta attacks Asturias · Blake attacks Wellesley
  - 🏴 Russia: Kutuzov attacks Deroy — Bohemia CAPTURED! (was Bavaria) (secured)
  - 🏴 Austria: Archduke Charles attacks Deroy — Carniola CAPTURED! (was Bavaria) (secured)
  - ⚔ Kutuzov (lost 949) vs Deroy (lost 4136) — Deroy's army has been badly mauled. Kutuzov proved the stronger force today.
  - ⚔ Archduke Charles (lost 207) vs Deroy (lost 2785) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun. And Deroy was taken on that field — …
  - ⚔ Cuesta (lost 536) vs Wellesley (lost 668) — The enemy's repeated assaults have leveled our defenses. We fight without cover. — The Line Holds +15% (Wellesley)
  - ⚔ Blake (lost 343, own corps) vs Wellesley (lost 751) — A narrow defeat for Wellesley, Sire. Better-prepared troops might have tipped the balance. — The Line Holds +15% (Wellesley)
  - verbs: attack×4, move×3, garrison×1
- LEDGER treasury 17900 · net -957 · threat 46 · provinces 26 (+0) · ceiling 12496 · army 80981 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2438 · trade 574 · admin 50 · tribute 937 · upkeep 1060 · charges 2817 · contributions 80 · blockade 359 · admiralty 90 · laws 550
- DISPATCH: Sire — Bohemia has been taken by Russia.
  - TURN EVENTS 3
- DIPLO +5 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 500g reaches Sweden
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: PapalStates rebuffs Hanover (open borders agreement)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG diplomatic_treaty_broken: Russia has broken the Peace Treaty with France by declaring war.
  - LOG sponsorship_granted: Russia sponsors Sweden against France (400g/turn)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Hesse are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Wellesley · Cuesta attacks Wellesley · Blake attacks Asturias
  - 🏴 Spain: Blake attacks Asturias — Region captured: Asturias (was Britain) (secured)
  - ⚔ Castanos (lost 222, own corps) vs Wellesley (lost 877) — Wellesley's corps broke, Sire. They are streaming back from the field. — The Line Holds +15% (Wellesley)
  - ⚔ Cuesta (lost 26, own corps) vs Wellesley (lost 1293) — The hills were ours, but Cuesta took them. Wellesley's position was overrun. — The Line Holds +15% (Wellesley)
  - verbs: attack×3, fortify×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 16791 · net -972 · threat 44 · provinces 26 (+0) · ceiling 11426 · army 80207 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2433 · trade 574 · admin 50 · tribute 900 · upkeep 1060 · charges 2680 · contributions 190 · blockade 359 · admiralty 90 · laws 550
- DISPATCH: Sire — Friesland has been taken by Hanover.
  - TURN EVENTS 4
- DIPLO +9 medium/low (province_changed_hands ×2, diplomatic_dp_regen, diplomatic_auto_downgrade ×5, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Britain (Non-Aggression → Open Borders)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Non-Aggression → Open Borders)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Sardinia (Defensive Alliance → Non-Aggression)
  - LOG auto_downgrade: Relations auto-downgraded: Britain–Sardinia (Defensive Alliance → Non-Aggression)
  - LOG british_subsidy: Britain's gold: 400g reaches Sweden
  - LOG moment: The Squadron for Santo Domingo — an affair of state is laid before the Emperor

## Turn 38 — Early April 1807
  - MAILBOX #18 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #26 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 40.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight. — Cuesta attacks Wellesley
  - ⚔ Cuesta (lost 59) vs Wellesley (lost 596) — Wellesley was driven from the field. His men are scattered. And Wellesley was taken on that field — Spain holds him. — The Line Holds +15% (Wellesley)
  - verbs: move×1, fortify×1, attack×1
- LEDGER treasury 15758 · net -900 · threat 42 · provinces 26 (+0) · ceiling 10893 · army 79465 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2423 · trade 524 · admin 50 · tribute 750 · upkeep 1052 · charges 2547 · contributions 80 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Piedmont has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Paget has put 10,000 men ashore at Piedmont.
  - TURN EVENTS 4
- DIPLO +4 medium/low (province_changed_hands, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (Alliance → Defensive Alliance)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs Sardinia (design ask)
  - LOG moment: The Squadron for Santo Domingo — the Emperor answers: Ferrand must hold alone

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke Charles is at Tyrol, just one region away.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 83%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 14364 · net -667 · threat 40 · provinces 27 (+1) · ceiling 10821 · army 81631 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2454 · trade 524 · admin 50 · tribute 750 · upkeep 1068 · charges 2329 · contributions 80 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — the enemy has held Picardy 6 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Sweden
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified.…
  - saved `rev1106-law-enacts-ulm_t40` → Game saved: rev1106-law-enacts-ulm_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 2 actions unused) Turn 41 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight. — Cuesta attacks Picardy · Wallmoden attacks Cuesta · Alten attacks Artois
  - 🏴 Spain: Cuesta attacks Picardy — Region captured: Picardy (was Hanover)
  - 🏴 Hanover: Alten attacks Artois — Region captured: Artois (was France) (secured)
  - ⚔ Wallmoden (lost 454) vs Cuesta (lost 813) — Cuesta was caught in an aggressive posture when Wallmoden struck, Sire. A defensive stance would have served better.
  - verbs: attack×3
- LEDGER treasury 13683 · net -595 · threat 38 · provinces 27 (+0) · ceiling 10583 · army 80830 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2432 · trade 524 · admin 50 · tribute 750 · upkeep 1060 · charges 2243 · contributions 80 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Artois has fallen to Hanover. Enemy colours fly over French homeland soil. Alten's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does an…
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

---
finished: **completed** · commands 239 · popups 49 · battles 37
