# Playtest digest — SHUT-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `declare war on Portugal` → ✓ Choose your war purpose against Portugal.
  - POPUP diplomatic_dialogue: war_purpose_selection #1 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #2 → 1
  - POPUP diplomatic_objection: diplomatic_declare_war, Portugal → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #3 → ally_entry_proceed_without
- CMD `declare war on the Papal States` → ✓ Choose your war purpose against the Papal States.
  - POPUP diplomatic_dialogue: war_purpose_selection #4 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #5 → 1
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #6 → ally_entry_proceed_without
- CMD `Soult, march to Lisbon` → ✓ Soult begins march to Lisbon. Route: Orleanais → Burgundy → Limousin → Gascony → Bearn → Cartagena → Andalusia → Lisbon. Arrives in 8 turns. Moves to Orleanais. "Soult, …
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Route: Piedmont → Rome. Arrives in 2 turns. Moves to Piedmont.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 1666) vs Bernadotte (lost 7369) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
- ORDER Massena [active]: Massena is marching to Rome (1 turn remaining).
- ORDER Soult [active]: Soult is marching to Lisbon (7 turns remaining).
- LEDGER treasury 1642 · net +1210 · threat 97 · provinces 28 · ceiling 11002 · army 178828 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2408 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_war_declared: France has declared war on Portugal, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: France has declared war on PapalStates, with 2 allied courts poised to follow.
  - TURN EVENTS 3
- DIPLO +10 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, blockade_begins ×3)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 104,274 with the corps likely to arrive, up to 112,341 if all march; certain 24,000; a bad day (1 in 10) 91,606) vs Mack (large force)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2305, own corps) vs Mack (lost 17082) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Murat never arrived, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 actions unused) Turn 3 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Franconia · Archduke Charles attacks Bernadotte
  - 🏴 Austria: Archduke Charles attacks Franconia — Region captured: Franconia (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1798) vs Bernadotte (lost 3520, own corps) — Ney and Teulie reached Bernadotte in time, Sire — but even together, the field could not be held. — Berthier: the corps marched apart and arrived together.
  - verbs: attack×2, retreat×1, stance_change×1, move×1, wait×1
- ORDER Soult [continues]: Soult marches to Burgundy. 6 regions to Lisbon.
- ORDER Massena [interrupted]: Massena hears cannon fire! Abandoning orders — rushing to Munich! Massena moves from Piedmont to Milan (1,178 lost to march)
- LEDGER treasury 2849 · net +1742 · threat 97 · provinces 28 (+0) · ceiling 14649 · army 162259 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 1788 · charges 125 · requisitions 37 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +6 medium/low (diplomatic_we_threshold ×2, law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, agenda_shift)

## Turn 3 — Late October 1805
- CMD `Ney, attack Mack` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,916; expect about 52,212 with the corps likely to arrive, up to 53,812 if all march; certain 23,916) vs Mack (33,512 men) at Franconia — the balance …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 957, own corps) vs Mack (lost 12066) — Reinforcements! Lannes and Napoleon marched onto the field beside Davout. The enemy's advantage melted away.
- CMD `Lannes, move to Swabia` → ✗ Cannot advance while engaged with Archduke Charles at Franconia. He may withdraw onto friendly ground — Munich — with 'Lannes, retreat to Munich' (free, −45% effectivene…
- CMD `Massena, attack Rome` → ✗ Massena cannot reach Rome from Milan! Range: 1, Distance: 2
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 0 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, fortify×1, naval_expedition×1, wait×1
- ORDER Soult [continues]: Soult marches to Limousin. 5 regions to Lisbon.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 4707 · net +1642 · threat 97 · provinces 28 (+0) · ceiling 15535 · army 156949 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 1616 · charges 410 · requisitions 50 · blockade 219 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Franconia — Mack's corps breaks a second time on this ground and flees.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden and Naples (open borders agreement)

## Turn 4 — Early November 1805
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Route: Piedmont → Rome. Arrives in 2 turns. Moves to Piedmont.
- CMD `Massena, attack Rome` → ✓ ASSAULT — Massena storms the works at Rome alone: 35,829 men, 41,203 in the assault's reckoning, against a garrison of 10,000. the garrison breaks below 5,000.
  - ↳ Massena assaults the Rome garrison! Garrison: 10,000 -> 5,000 (-5,000). Massena loses 2,173 troops. Garrison holds — 5,000 defenders remain. It regains up to 2,000 a tur…
- CMD `Ney, attack Mack` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (21,979; expect about 49,029 with the corps likely to arrive, up to 50,557 if all march; certain 21,979) vs Mack (substantial force) at Tyrol — the balan…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1018, own corps) vs Mack (lost 7994, own corps) — Lannes and Napoleon arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire.
  - POPUP capture_choice[capture]: Tyrol, Davout → secure
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 5 actions, 3 attacks — Russia, Prussia, Spain and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Swabia · Deroy attacks Franconia · Deroy attacks Mack
  - 🏴 Bavaria: Deroy attacks Swabia — Region captured: Swabia (was Austria) (secured)
  - 🏴 Bavaria: Deroy attacks Franconia — Region captured: Franconia (was Austria) (secured)
  - ⚔ Deroy (lost 335) vs Mack (lost 6438) — A grievous defeat for Mack, Sire. The losses are severe.
  - verbs: attack×3, stance_change×1, wait×1
- ORDER Soult [continues]: Soult marches to Gascony. 4 regions to Lisbon.
- LEDGER treasury 6296 · net +1442 · threat 97 · provinces 29 (+1) · ceiling 13977 · army 147717 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2624 · trade 350 · admin 50 · tribute 937 · upkeep 1330 · charges 805 · occupation 75 · blockade 219 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Tyrol — Mack's corps is broken and flees.
  - TURN EVENTS 5
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +5 medium/low (diplomatic_we_threshold, province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Russia decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 5 — Late November 1805
- CMD `Massena, attack Rome` → ✓ ASSAULT — Massena storms the works at Rome alone: 33,595 men, 38,634 in the assault's reckoning, against a garrison of 7,000. the garrison breaks below 5,000.
  - ↳ Massena assaults the Rome garrison! Garrison collapses (7,000 -> 0). Massena loses 1,521 troops in the assault. Massena marches into Rome! (962 lost to march)
  - POPUP capture_choice[capture]: Rome, Massena → secure
- CMD `Lannes, attack Mack` → ✓ Mack was last seen at Bohemia 1 turn ago, one march off. Pursue him (2 AP — a standing order; the first march meets Archduke John at Bohemia, Austria's soil), or cancel?
  - POPUP clarification: Lannes, pursuit_ask, Mack was last seen at Bohemia 1 turn ago, one march off. Pursue him (2 AP — a standing order; the first march meets Archduke John at Bohemia, Austria's soil), or cancel? → 1 (first option: Pursue Mack (2 AP))
  - ↳ MUSTER — Lannes (14,647; expect about 42,387 with the corps likely to arrive, up to 48,511 if all march; certain 14,647; a bad day (1 in 10) 23,588) vs Archduke John (15,214 men) at Bohemia — the balance of force looks even — a hard fight t
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1887, own corps) vs Archduke John (lost 2230, own corps) — Davout and Napoleon arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire.
  - POPUP capture_choice[capture]: Bohemia, Lannes → secure
- CMD `Murat, attack Archduke Charles` → ✓ Archduke Charles stands at Vienna, four marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −228g more a turn. Pursue him (2 AP —…
  - POPUP clarification: Murat, pursuit_ask, Archduke Charles stands at Vienna, four marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −228g more a turn. Pursue him (2 AP — a standing order; the first march takes Murat to Swabia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 3 actions, 0 attacks — Russia, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, fortify×1, wait×1
- ORDER Lannes [active]: Lannes is pursuing Mack (1 turn remaining).
- ORDER Murat [active]: Murat is pursuing Archduke Charles.
- ORDER Soult [continues]: Soult marches to Bearn. 3 regions to Lisbon.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #12 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +0 (100 → 100, already full); bond -30 → -10 (-1 a turn). Cost: 1 DP. Our net rises by 58g a turn — 35g of income forfeited, 75g of occupation relieved, 26g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 7339 · net +1134 · threat 97 · provinces 30 (+1) · ceiling 13231 · army 137952 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2695 · trade 312 · admin 50 · tribute 963 · upkeep 1324 · charges 1027 · occupation 250 · blockade 195 · admiralty 90
- DISPATCH: Sire — Papal States is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Sire — the Papal States has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +7 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy, diplomatic_ai_ai_treaty ×2, cs_tier_shift, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (Alliance → Defensive Alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Austria and the Ottoman Empire sign a Non-Aggression Pact
  - LOG diplomatic_ai_ai_treaty: Saxony and Austria sign a Non-Aggression Pact
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: The Ottoman Empire and Naples sign a Defensive Alliance
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 6 — Early December 1805
- CMD `Massena, march to Rome` → ✗ Massena already stands at Rome — nothing spent.
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Bearn! Range: 1, Distance: 3
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Ney, attack Archduke Charles` → ✓ Archduke Charles stands at Vienna, four marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −192g more a turn. Pursue him (2 AP —…
  - POPUP clarification: Ney, pursuit_ask, Archduke Charles stands at Vienna, four marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −192g more a turn. Pursue him (2 AP — a standing order; the first march takes Ney to Swabia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Paget
  - ⚔ Castanos (lost 250) vs Paget (lost 1215) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better. And … — The Line Holds +15% (Paget)
  - verbs: wait×2, move×2, unfortify×1, attack×1
- ORDER Lannes [breaks]: Order cancelled: The trail has gone cold, Sire — Mack was last making for Bohemia, and Lannes has no further word of him. Scout for him to take up th…
- ORDER Murat [completed]: [Combat] Murat leads the charge! (Aggressive: +15% attack)
- ORDER Ney [active]: Ney is pursuing Archduke Charles.
- ORDER Soult [continues]: Soult marches to Cartagena. 2 regions to Lisbon.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7989 · net +756 · threat 95 · provinces 30 (+0) · ceiling 11741 · army 128376 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 93
  - NET income 2697 · trade 312 · admin 50 · tribute 964 · upkeep 1528 · charges 1204 · occupation 250 · blockade 195 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven
  - LOG nation_eliminated: The Papal States has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Britain rebuffs Naples (open borders agreement)

## Turn 7 — Late December 1805
  - MAILBOX #2 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #14 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +7 (93 → 100); bond -30 → -10 (-1 a turn). Cost: 1 DP. → display-only
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Cartagena! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✗ Paget is a prisoner of Spain at Madrid, Sire — he leads no army.
- CMD `Davout, attack Archduke Charles` → ✓ Davout notes the risks but prepares the attack. Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be …
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be told twice than bury them once."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Davout attacks Archduke Charles' to read the muster before you commit — it costs nothing.
MUSTER — Davout (15,760; expect about 31,907 with the corps likely to arrive, up to 32,821 if all march; certain 15,760) vs Archduke Charles (38,013 men) at Vienna — the balance of force looks unfavorable.
  WILL JOIN — Lannes: marches to the sound of the guns — the Roland of the Army — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and returns to Bohemia if the works hold
  WILL NOT — Murat: will not lift a finger for Marshal Davout
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and returns to Bohemia if the works hold
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +39% on the defense (his stance, his character and his works).
  Vienna feeds 40,000 — the whole muster can stand there fed. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 32,698 we muster) would cost ~245g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 95/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Davout (15,760; expect about 31,907 with the corps likely to arrive, up to 32,821 if all march; certain 15,760) vs Archduke Charles (38,013 men) at Vienna — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 2341, own corps) vs Archduke Charles (lost 2146) — Lannes and Napoleon marched to Davout's guns as ordered. It was not enough.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 8 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Mack
  - 🏴 Bavaria: Deroy moves to Hungary — Hungary falls (was Austria) and is secured
  - 🏴 Bavaria: Deroy attacks Mack — Moravia CAPTURED! (was Austria) (secured)
  - ⚔ Deroy (lost 1398) vs Mack (lost 3332) — The walls were not enough. Deroy broke through Mack's prepared defenses.
  - verbs: wait×3, recruit×2, defend×1, move×1, attack×1
- ORDER Ney [continues]: Ney pursues Archduke Charles. 2 regions away.
- ORDER Soult [continues]: Soult marches to Andalusia. 1 region to Lisbon.
- LEDGER treasury 8866 · net +866 · threat 93 · provinces 30 (+0) · ceiling 13739 · army 122172 · vassals Holland 96 · Kingdom of Italy 98 · Switzerland 97
  - NET income 2920 · trade 312 · admin 50 · tribute 739 · upkeep 1476 · charges 1219 · occupation 175 · blockade 195 · admiralty 90
- DISPATCH: Sire — Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
  - TURN EVENTS 6
- DIPLO +6 medium/low (law_enacted_abroad, province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)

## Turn 8 — Early January 1806
- CMD `Massena, march to Rome` → ✗ Massena already stands at Rome — nothing spent.
- CMD `Soult, attack Lisbon` → ✓ ASSAULT — Soult storms the works at Lisbon alone: 27,665 men, 31,814 in the assault's reckoning, against a garrison of 10,000. the garrison breaks below 5,000.
  - ↳ Soult assaults the Lisbon garrison! Garrison: 10,000 -> 5,000 (-5,000). Soult loses 2,173 troops. Garrison holds — 5,000 defenders remain. It regains up to 2,000 a turn …
- CMD `Soult, attack Paget` → ✗ Paget is a prisoner of Spain at Madrid, Sire — he leads no army.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 10 actions, 3 attacks — Britain, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Deroy · Archduke John attacks Deroy · Archduke John attacks Hungary
  - 🏴 Austria: Archduke John attacks Deroy — Moravia CAPTURED! (was Bavaria) (secured)
  - 🏴 Austria: Archduke John attacks Hungary — Hungary CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1383, own corps) vs Deroy (lost 4592) — The battle unfolded without particular distinction.
  - ⚔ Archduke John (lost 493, own corps) vs Deroy (lost 4045) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Archduke John (lost 115, own corps) vs Deroy (lost 2955) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×3, form_square×2, unfortify×2, recruit×2, wait×1
- ORDER Ney [continues]: Ney hears cannon fire at Moravia but cannot answer it — Cannot enter Dresden — it is controlled by Saxony (diplomatic state: PEACE). Open borders or …
- ENVOYS WAITING 2 · Portugal armistice losing · Austria settlement offer
- LEDGER treasury 9758 · net +795 · threat 91 · provinces 30 (+0) · ceiling 14106 · army 118319 · vassals Holland 94 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2927 · trade 312 · admin 50 · tribute 796 · upkeep 1412 · charges 1418 · occupation 175 · blockade 195 · admiralty 90
- DISPATCH: Sire — Moravia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL settlement_offer_arrival: Austria has offered terms to settle the War for Bohemia — Britain + Austria + Russia. Offering 1890 gold. Its articles: Austria's design pointed else…
  - TURN EVENTS 7
- DIPLO +4 medium/low (province_changed_hands ×2, diplomatic_dp_regen, agenda_shift)

## Turn 9 — Late January 1806
  - MAILBOX #3 Portugal incoming_proposal: Portugal — Armistice → activated
  - MAILBOX #4 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Portugal, armistice_losing #15 → accept_ai_proposal
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity, territory_compensate
  - POPUP diplomatic_dialogue: settlement_confirm #17 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Bohemia — the table with Austria (3 pairs resolved). Status quo: Bohemia stays ours by the treaty — titled. Status quo: Tyrol stays ours by the treaty — titled. → display-only
  - POPUP diplomatic_dialogue: Portugal, armistice_losing #15 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Portugal's proposal. Treaty signed: At War → Armistice with Portugal. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → accept_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Lisbon` → ✓ Choose your war purpose against Portugal. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #19 → 1
  -     ↳ refused: The armistice with Portugal holds for 5 more turns. We cannot declare war until it expires.
- CMD `Soult, attack Paget` → ✗ Paget is a prisoner of Spain at Madrid, Sire — he leads no army.
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 11 actions, 1 attacks — Britain, Prussia, the Ottoman Empire and 6 other courts stirred as well, but their formations remain beyond our sight. — Cuesta attacks Shrapnel
  - ⚔ Cuesta (lost 239) vs Shrapnel (lost 807) — Shrapnel's fortified position was overwhelmed. A costly investment lost, Sire. — The Line Holds +15% (Shrapnel)
  - verbs: wait×2, move×2, unfortify×1, form_square×1, break_square×1, garrison×1, drill×1, attack×1, recruit×1
- ENVOYS WAITING 2 · Holland client petition · The Secretariat moment letter
- LEDGER treasury 11677 · net +631 · threat 89 · provinces 30 (+0) · ceiling 15492 · army 116707 · vassals Holland 92 · Kingdom of Italy 94 · Switzerland 91
  - NET income 2935 · trade 312 · admin 50 · tribute 796 · upkeep 1404 · charges 1598 · occupation 175 · blockade 195 · admiralty 90
- DISPATCH: Sire — a truce with Portugal is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_summary: Sire, the settlement of the War for Bohemia — the table with Austria is not a curtain call; it is an accounting. Bavaria must be read beside reaction…
  - RAIL armistice_ratified: A truce with Portugal: the fighting stops for 5 turns. The ledger stands: the war score reads -2 for France (1 battle, 0 decisives kept); the war is …
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 5
- DIPLO +7 medium/low (status_quo_titled ×2, diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain binds Russia to the war against France — no separate peace for 10 turns (200g/turn)
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor
  - LOG sponsorship_granted: France licences Austria's design against Ottoman Empire
  - LOG design_bought_off: The peace points Austria elsewhere: France licenses The Eastern Question (Albania) — her other designs sleep
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 10 — Early February 1806
  - MAILBOX #5 Holland incoming_proposal: Holland — Client's Petition → activated
  - MAILBOX #6 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #21 → reject_ai_proposal
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +8 (92 → 100); bond -30 → -10 (-1 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: moment_letter #21 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Massena, march to Rome` → ✗ Massena already stands at Rome — nothing spent.
- CMD `Soult, attack Lisbon` → ✓ Choose your war purpose against Portugal. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #22 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #23 → 1
  -     ↳ refused: The armistice with Portugal holds for 4 more turns. We cannot declare war until it expires.
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ Paget is a prisoner of Spain at Madrid, Sire — he leads no army.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 6 actions, 5 attacks — Britain, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden attacks Murat · Buxhowden attacks Davout · Buxhowden attacks Lannes · Kutuzov attacks Davout
  - ⚔ Buxhowden (lost 3280) vs Murat (lost 1712, own corps) — Ney arrived in time to steady Murat's position. The field was held, nothing further. — The corps system brought Ney in.
  - ⚔ Buxhowden (lost 2922) vs Davout (lost 671, own corps) — The exchange went Davout's way, Sire — Buxhowden paid twice what Davout did, though the day decided nothing yet. — the Russian army would not break: Stubborn softened the rout (−4 morale, not −9)
  - ⚔ Buxhowden (lost 2732) vs Lannes (lost 611, own corps) — The engagement proceeded as one might expect, Sire.
  - ⚔ Kutuzov (lost 1660) vs Davout (lost 1242, own corps) — Davout was close. A period of drilling could have changed the outcome.
  - ⚔ Castanos (lost 40) vs Shrapnel (lost 404) — The walls were not enough. Castanos broke through Shrapnel's prepared defenses. — The Line Holds +15% (Shrapnel)
  - verbs: attack×5, wait×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Davout: They settle into cold war.
- ENVOYS WAITING 1 · Denmark open borders
- LEDGER treasury 11471 · net +170 · threat 87 · provinces 30 (+0) · ceiling 12296 · army 105157 · vassals Holland 99 · Kingdom of Italy 91 · Switzerland 88
  - NET income 2899 · trade 312 · admin 50 · tribute 459 · upkeep 1116 · charges 1947 · contributions 27 · occupation 175 · blockade 195 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 10
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 11 — Late February 1806
  - LETTER Denmark: Open Borders Agreement → accept
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ Paget is a prisoner of Spain at Madrid, Sire — he leads no army.
- CMD `Soult, attack Lisbon` → ✓ Choose your war purpose against Portugal. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #25 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #26 → 1
  -     ↳ refused: The armistice with Portugal holds for 3 more turns. We cannot declare war until it expires.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 actions unused) Turn 12 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Shrapnel
  - ⚔ Castanos (lost 26) vs Shrapnel (lost 267) — Even Shrapnel's fortifications could not hold, Sire. Castanos overran the position. And Shrapnel was taken on that fiel… — The Line Holds +15% (Shrapnel)
  - verbs: attack×1, grant_pension×1, defend×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- ENVOYS WAITING 1 · Hesse open borders
- LEDGER treasury 11702 · net +153 · threat 85 · provinces 30 (+0) · ceiling 12431 · army 104390 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 85
  - NET income 2906 · trade 362 · admin 50 · tribute 459 · upkeep 1108 · charges 2025 · occupation 175 · blockade 226 · admiralty 90
- DISPATCH: Sire — the allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegiance.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 10
- DIPLO +6 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
  - LETTER Hesse: Open Borders Agreement → accept
- CMD `Massena, march to Rome` → ✗ Massena already stands at Rome — nothing spent.
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ Paget is a prisoner of Spain at Madrid, Sire — he leads no army.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 12373 · net +395 · threat 83 · provinces 30 (+0) · ceiling 14538 · army 103646 · vassals Holland 97 · Kingdom of Italy 85 · Switzerland 82
  - NET income 2971 · trade 387 · admin 50 · tribute 459 · upkeep 1108 · charges 1887 · occupation 145 · blockade 242 · admiralty 90
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,284g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (4 authority)

---
finished: **completed** · commands 58 · popups 48 · battles 20
