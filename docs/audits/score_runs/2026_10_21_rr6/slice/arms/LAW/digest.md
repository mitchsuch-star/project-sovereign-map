# Playtest digest — LAW

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `d940b5bcea37` (dirty) · content `eb5a83d3aaa1` · driver `92f61a27e85e`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `what laws are in force` → ✓ The laws of state, Sire. No law is in force. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 800. The Train des Équipages: 3,500 gold, …
- CMD `what does the Staff cost` → ✓ The laws of state, Sire. No law is in force. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 800. Berthier's headquarters grown into a …
- CMD `laws` → ✓ The laws of state, Sire. No law is in force. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 800. The Train des Équipages: 3,500 gold, …
- CMD `enact the Anticipated Class` → ✓ The Anticipated Class (the senatus-consultes calling the class early, 1806–07): The Senate calls each year's conscripts before their time: infantry manpower returns 25% …
  - POPUP clarification: The Council of State, The Anticipated Class (the senatus-consultes calling the class early, 1806–07): The Senate calls each year's conscripts before their time: infantry manpower returns 25% faster. 15 authority now, then 150 gold a turn. Authority 100 → 85 — the marshals' calm holds above 70. The treasury holds 800 gold. Enact it? (yes / no) → 1 (first option: Enact the Anticipated Class)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1847, own corps) vs Mack (lost 24408) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Deroy attacks Mack
  - ⚔ Archduke Charles (lost 3964) vs Massena (lost 6353) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Deroy (lost 983) vs Mack (lost 8861) — Mack stood alone, Sire. Archduke John never came.
  - verbs: attack×2, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 396 · net +209 · threat 77 · provinces 28 · ceiling 6318 · army 174609 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 3236 · blockade 250 · admiralty 90 · laws 150
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
- CMD `what does the Code Abroad do` → ✓ The laws of state, Sire. In force: the Anticipated Class. The Code Abroad: 15 authority, then 100 gold a turn — ready to enact. The Civil Code carried into the client st…
- CMD `enact the Code Abroad` → ✓ The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1…
  - POPUP clarification: The Council of State, The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1 loyalty a turn in every one. 15 authority now, then 100 gold a turn. Authority 85 → 70 — the marshals' calm above 70 is lost. The treasury holds 456 gold. Enact it? (yes / no) → 1 (first option: Enact the Code Abroad)
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Ney, attack Mack` → ✓ Mack stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Ney, pursuit_ask, Mack stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Mack (2 AP))
- CMD `Davout, attack Mack` → ✓ Mack stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Davout, pursuit_ask, Mack stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Mack (2 AP))
- CMD `Soult, move to Alsace` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Alsace today.
- CMD `Murat, move to Franche-Comte` → ✗ Not enough actions! Need 1, have 0 — Murat cannot march to Franche-Comte today.
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke Charles attacks Teulie
  - ⚔ Archduke Charles (lost 4330) vs Massena (lost 4342, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 2676) vs Teulie (lost 1357, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×2, wait×1
- ORDER Davout [active]: Davout is pursuing Mack.
- ORDER Ney [active]: Ney is pursuing Mack.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 322 · net +386 · threat 75 · provinces 28 (+0) · ceiling 6849 · army 164669 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 829 · upkeep 2912 · blockade 281 · admiralty 90 · laws 250
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +6% this morning; the courts have begun to notice that he can be beaten.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 29 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `what laws are in force` → ✓ The laws of state, Sire. In force: the Anticipated Class, the Code Abroad. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 404. The Tra…
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 404.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,407; expect about 47,322 with the corps likely to arrive, up to 47,970 if all march) vs Mack (substantial force) at Bohemia — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 299, own corps) vs Mack (lost 15770) — Davout arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. And Mack was taken on that fie…
  - POPUP capture_choice[capture]: Bohemia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (169 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✗ Soult's infantry levy: Berthier shakes his head. 'The treasury cannot support this, Sire. Need 741 gold, have 377.'
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke Charles attacks Teulie
  - ⚔ Archduke Charles (lost 3013) vs Massena (lost 3743, own corps) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 1757) vs Teulie (lost 1200, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2
- ORDER Davout [completed]: Mack taken prisoner Davout: "Accomplished as ordered. The army is intact."
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 902 · net +961 · threat 83 · provinces 29 (+1) · ceiling 10008 · army 155721 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 92
  - NET income 2636 · trade 525 · admin 50 · tribute 799 · upkeep 2310 · occupation 70 · blockade 329 · admiralty 90 · laws 250
- DISPATCH: Sire — General Mack of Austria is taken at Bohemia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples and Bavaria rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 1,007.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 2057 · net +1043 · threat 81 · provinces 29 (+0) · ceiling 10467 · army 154806 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2637 · trade 587 · admin 50 · tribute 802 · upkeep 2248 · charges 7 · occupation 70 · blockade 368 · admiralty 90 · laws 250
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
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,057.
- CMD `what does the Staff cost` → ✓ The laws of state, Sire. In force: the Anticipated Class, the Code Abroad. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 2,057. Berth…
- CMD `Ney, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Ney marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Ney, muster_confirm, Berthier stays the order a moment, Sire: before Ney marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Ney (19,903; expect about 35,414 with the corps likely to arrive, up to 36,150 if all march) vs Archduke Charles (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL NOT — Davout: is dug in and will not abandon his works
  WILL NOT — Bernadotte: will not lift a finger for Marshal Ney
  WILL JOIN — Massena: will march to the sound of the guns — likely to make it in time (about 95%) (The corps system lowers the bar by 10) — and will stand at Tyrol
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Tyrol
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 44,393 we muster) would cost ~333g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP; 2 for Bernadotte, Massena, Teulie, who stand neutral) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Ney (19,903; expect about 35,414 with the corps likely to arrive, up to 36,150 if all march) vs Archduke Charles (substantial force) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 4215, own corps) vs Archduke Charles (lost 1737, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (900 lost to march)
- CMD `Murat, move to Swabia` → ✗ Murat is already in Swabia.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 9 actions, 6 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Teulie · Archduke John attacks Munich · Archduke John attacks Munich · Deroy attacks Munich
  - 🏴 Austria: Archduke John attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - ⚔ Archduke John (lost 161) vs Teulie (lost 1798) — A grievous defeat for Teulie, Sire. The losses are severe. And Teulie was taken on that field — Austria holds him.
  - ⚔ Deroy (lost 1810) vs Archduke John (lost 1699) — Archduke John's square formation provided a solid defensive anchor, Sire.
  - ⚔ Deroy (lost 1487) vs Archduke John (lost 1624) — The square held its ground. Archduke John's infantry stood like a fortress on the field.
  - ⚔ Deroy (lost 1319) vs Archduke John (lost 1221) — Archduke John's men formed square and weathered the storm. Discipline held the line.
  - verbs: attack×6, unfortify×1, form_square×1, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 2548 · net +889 · threat 79 · provinces 29 (+0) · ceiling 10992 · army 144516 · vassals Holland 96 · Kingdom of Italy 85 · Switzerland 86
  - NET income 2734 · trade 587 · admin 50 · tribute 799 · upkeep 2476 · charges 57 · occupation 40 · blockade 368 · admiralty 90 · laws 250
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Munich. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +11 medium/low (diplomatic_we_threshold ×2, enemy_marshal_commissioned, province_changed_hands, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, coercive_demand, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (300g/turn)

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (86 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,548.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `how many diplomatic points do I have` → ✓ Talleyrand holds 6 diplomatic points of 7 — 4 came with this morning's refill and 3 were carried from last turn; what he leaves unspent carries one turn, to at most 7. T…
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Kutuzov is at Hungary, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attac…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Munich instead.) → trust
  - ↳ MUSTER — Lannes (15,590; expect about 51,130 with the corps likely to arrive, up to 51,674 if all march) vs Archduke John (6,266 men) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 321, own corps) vs Archduke John (lost 4876) — Murat, Bernadotte and Napoleon arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire. — Munich falls to Lannes. The last 2,000 of the garrison at Munich give way. — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Munich, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Archduke John
  - 🏴 Bavaria: Deroy attacks Archduke John — Tyrol CAPTURED! (was Austria) (secured)
  - ⚔ Deroy (lost 47) vs Archduke John (lost 672) — Archduke John's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×1, wait×1
  - ⚡ AUTONOMOUS: [Shield] Archduke Charles steps forward to cover Archduke John's retreat! "Archduke John is in no condition to fight - I'll handle this!"
  - ⚔ Murat (lost 2674, own corps) vs Archduke Charles (lost 4212) — Ney, Davout and Lannes arrived in time to steady Murat's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 2828 · net +528 · threat 87 · provinces 29 (+0) · ceiling 6542 · army 135131 · vassals Holland 98 · Switzerland 97
  - NET income 2737 · trade 587 · admin 50 · tribute 337 · upkeep 2208 · charges 117 · contributions 110 · occupation 40 · blockade 368 · admiralty 90 · laws 250
- DISPATCH: Sire — the Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - EXPECTS: Lannes's victories raise his expectation — he now looks for 40g/turn (holds 0g).
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL province_returned: France hands Munich back to Bavaria — the liberated soil comes home.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 10
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +10 medium/low (province_changed_hands ×4, enemy_marshal_commissioned ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,828.
- CMD `repeal the Code Abroad` → ✓ The Code Abroad is repealed — its 100 gold a turn ends, and nothing is refunded. Enacting it again costs its full price (15 authority).
- CMD `what laws are in force` → ✓ The laws of state, Sire. In force: the Anticipated Class. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 2,828. The Train des Équipage…
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Ney, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Ney can give chase.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Murat (15,661) vs Archduke Charles (strength unknown) at Piedmont — the balance of force looks unfavorable.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Piedmont can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 15,661 we muster) would cost ~117g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Murat (15,661) vs Archduke Charles (strength unknown) at Piedmont — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 4942) vs Archduke Charles (lost 1037) — The ground itself worked against Murat. Terrain matters, Sire.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Archduke Charles
  - ⚔ Deroy (lost 2442) vs Archduke Charles (lost 1350) — A standard affair. Nothing unusual to report.
  - verbs: wait×2, move×1, attack×1
- LEDGER treasury 3287 · net +624 · threat 85 · provinces 29 (+0) · ceiling 7454 · army 130136 · vassals Holland 96 · Switzerland 94
  - NET income 2740 · trade 587 · admin 50 · tribute 337 · upkeep 2100 · charges 192 · contributions 150 · occupation 40 · blockade 368 · admiralty 90 · laws 150
- DISPATCH: Sire — Murat's corps has been broken at Piedmont. He must reform before he fights again.
  - TURN EVENTS 4
- DIPLO +4 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG province_returned: France hands Munich back to Bavaria — the liberated soil comes home
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Munich — Austria is not forgiven
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 8 — Early January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 3,287.
- CMD `enact the Code Abroad` → ✓ The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1…
  - POPUP clarification: The Council of State, The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1 loyalty a turn in every one. 15 authority now, then 100 gold a turn. Authority 60 → 45 — the extra diplomatic point is lost (it needs 60). The treasury holds 3,287 gold. Enact it? (yes / no) → 1 (first option: Enact the Code Abroad)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Davout, attack Archduke Charles` → ✓ Archduke Charles stands at Piedmont, six marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Davout, pursuit_ask, Archduke Charles stands at Piedmont, six marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Boh…
- CMD `Soult, drill` → ✗ Not enough actions! Need 1, have 0 — Soult cannot drill today.
- CMD `Massena, move to Milan` → ✗ Not enough actions! Need 1, have 0 — Massena cannot march to Milan today.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Archduke Charles · Deroy attacks Carniola · Deroy attacks Archduke John
  - 🏴 Bavaria: Deroy attacks Carniola — Region captured: Carniola (was Austria) (secured)
  - 🏴 Bavaria: Deroy attacks Archduke John — Hungary CAPTURED! (was Austria) (secured)
  - ⚔ Deroy (lost 2265) vs Archduke Charles (lost 1094) — A wise investment in fortification. Archduke Charles's position was impregnable to Deroy's assault.
  - ⚔ Deroy (lost 602) vs Archduke John (lost 2054) — Archduke John's army has been badly mauled. Deroy proved the stronger force today. And Archduke John was taken on that …
  - verbs: attack×3, fortify×1, wait×1
- ORDER Davout [active]: Davout is pursuing Archduke Charles.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 3656 · net +333 · threat 83 · provinces 29 (+0) · ceiling 5835 · army 129892 · vassals Holland 97 · Switzerland 94
  - NET income 2790 · trade 587 · admin 50 · tribute 337 · upkeep 2340 · charges 253 · contributions 110 · occupation 20 · blockade 368 · admiralty 90 · laws 250
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +3% this morning; the courts have begun to notice that he can be beaten.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 2 more turns
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +10 medium/low (law_enacted_abroad ×2, province_changed_hands ×4, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 3,656.
- CMD `what happened last turn` → ✓ This morning's dispatch leads with: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +3% this morning; the courts have begun to n…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 1 action unused) Turn 10 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Paget
  - ⚔ Castanos (lost 652) vs Paget (lost 1493) — Paget's aggressive posture left the troops exposed when Castanos's attack came. — The Line Holds +15% (Paget)
  - verbs: move×1, attack×1
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
- ORDER Davout : Davout: 'Cannon fire at Vienna, Sire. Investigate?'
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Vienna, Sire. Investigate?' → investigate
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 4009 · net +293 · threat 81 · provinces 29 (+0) · ceiling 5884 · army 129460 · vassals Holland 98 · Switzerland 94
  - NET income 2781 · trade 587 · admin 50 · tribute 337 · upkeep 2320 · charges 313 · contributions 101 · occupation 20 · blockade 368 · admiralty 90 · laws 250
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 1 more turn
  - RAIL settlement_offer_arrival: Austria, for Britain, Austria and Russia, has offered terms to settle the War for Bohemia — Britain + Austria + Russia.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 4
- DIPLO +9 medium/low (province_changed_hands ×5, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)

## Turn 10 — Early February 1806
  - MAILBOX #9 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → request_settlement_revision
  - TERMS (settlement_confirm PROPOSE): peace
  - POPUP diplomatic_dialogue: settlement_confirm #18 → settlement_dial_harsher
  - TERMS (settlement_confirm PROPOSE): peace, gold_indemnity, gold_indemnity, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #19 → settlement_dial_harsher
  - TERMS (settlement_confirm PROPOSE): peace, gold_indemnity, gold_indemnity, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #20 → suspend_settlement_editor (closed — still unratifiable after one harsher dial: Will NOT carry as drafted — every court must reach 50. Holding out: Austria 21/50, Britai…)
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 4,009.
- CMD `what laws are in force` → ✓ The laws of state, Sire. In force: the Anticipated Class, the Code Abroad. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 4,009. The T…
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Ney, move to Franconia` → ✓ Ney moves from Bohemia to Franconia (156 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Dresden. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortif…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Carniola, Franconia, Hungary, Moravia, Munich, Swabia, Tyrol.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 8 actions, 5 attacks — Russia, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — Hiller attacks Bohemia · Hiller attacks Carniola · Hiller attacks Hungary · Castanos attacks Paget
  - 🏴 Austria: Hiller attacks Bohemia — Region captured: Bohemia (was France) (secured)
  - 🏴 Austria: Hiller attacks Carniola — Region captured: Carniola (was Bavaria) (secured)
  - 🏴 Austria: Hiller attacks Hungary — Region captured: Hungary (was Bavaria) (secured)
  - ⚔ Castanos (lost 212) vs Paget (lost 1097) — Paget stood alone, Sire. Wellesley never came. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 750) vs Wellesley (lost 505) — Stalemate. Wellesley and Castanos glare at each other across the field. — The Line Holds +15% (Wellesley)
  - verbs: attack×5, move×2, stance_change×1
- ORDER Lannes [interrupted]: Lannes hears cannon fire! Abandoning orders — rushing to Hungary! Lannes moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) The …
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 4047 · net +26 · threat 81 · provinces 29 (+0) · ceiling 4204 · army 129175 · vassals Holland 99 · Switzerland 94
  - NET income 2612 · trade 587 · admin 50 · tribute 337 · upkeep 2356 · charges 325 · contributions 101 · occupation 70 · blockade 368 · admiralty 90 · laws 250
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 7
- DIPLO +6 medium/low (province_changed_hands ×4, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain binds Russia to the war against France — no separate peace for 10 turns (300g/turn)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

---
finished: **completed** · commands 75 · popups 37 · battles 23
