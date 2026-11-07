# Playtest digest — LAW

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `077efb374d7c` · content `e96449bb3b47` · driver `bd054bd265d8`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `what laws are in force` → ✓ The laws of state, Sire. No law is in force. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 800. The Train des Équipages: 3,500 gold, …
- CMD `what does the Staff cost` → ✓ The laws of state, Sire. No law is in force. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 800. Berthier's headquarters grown into a …
- CMD `laws` → ✓ The laws of state, Sire. No law is in force. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 800. The Train des Équipages: 3,500 gold, …
- CMD `enact the Anticipated Class` → ✓ The Anticipated Class (the senatus-consultes calling the class early, 1806–07): The Senate calls each year's conscripts before their time: infantry manpower returns 25% …
  - POPUP clarification: The Council of State, The Anticipated Class (the senatus-consultes calling the class early, 1806–07): The Senate calls each year's conscripts before their time: infantry manpower returns 25% faster. 15 authority now, then 150 gold a turn. Authority 100 → 85 — the marshals' calm holds above 70. The treasury holds 800 gold. Enact it? (yes / no) → 1 (first option: Enact the Anticipated Class)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1847, own corps) vs Mack (lost 24408) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Deroy attacks Mack
  - ⚔ Archduke Charles (lost 4431) vs Massena (lost 5819) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Deroy (lost 872) vs Mack (lost 10991) — Mack stood alone, Sire. Archduke John never came.
  - verbs: attack×2, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 393 · net +179 · threat 76 · provinces 28 · ceiling 3320 · army 175143 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 3266 · blockade 250 · admiralty 90 · laws 150
- MARSHALS Ney trust 75 Reliable glory 1 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `what does the Code Abroad do` → ✓ The laws of state, Sire. In force: the Anticipated Class. The Code Abroad: 15 authority, then 100 gold a turn — ready to enact. The Civil Code carried into the client st…
- CMD `enact the Code Abroad` → ✓ The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1…
  - POPUP clarification: The Council of State, The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1 loyalty a turn in every one. 15 authority now, then 100 gold a turn. Authority 94 → 79 — the marshals' calm holds above 70; the Presence +10% → +9%. The treasury holds 426 gold. Enact it? (yes / no) → 1 (first option: Enact the Code Abroad)
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Ney, attack Mack` → ✓ Mack stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Ney, pursuit_ask, Mack stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Mack (2 AP))
- CMD `Davout, attack Mack` → ✓ Mack stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Davout, pursuit_ask, Mack stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Mack (2 AP))
- CMD `Soult, move to Alsace` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Alsace today.
- CMD `Murat, move to Franche-Comte` → ✗ Not enough actions! Need 1, have 0 — Murat cannot march to Franche-Comte today.
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke Charles attacks Teulie
  - ⚔ Archduke Charles (lost 4475) vs Massena (lost 4326, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 2660) vs Teulie (lost 1415, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×2, wait×1
- ORDER Davout [active]: Davout is pursuing Mack.
- ORDER Ney [active]: Ney is pursuing Mack.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 261 · net +368 · threat 74 · provinces 28 (+0) · ceiling 4473 · army 165001 · vassals Holland 99 · Kingdom of Italy 98 · Switzerland 96
  - NET income 2590 · trade 450 · admin 50 · tribute 833 · upkeep 2934 · blockade 281 · admiralty 90 · laws 250
- MARSHALS Ney trust 75 Reliable glory 1 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +9% this morning; the courts have begun to notice that he can be beaten.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 3
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `what laws are in force` → ✓ The laws of state, Sire. In force: the Anticipated Class, the Code Abroad. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 355. The Tra…
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 355.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,407; expect about 47,322 with the corps likely to arrive, up to 47,970 if all march; certain 20,407) vs Mack (small force) at Bohemia — the balance of f…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 263, own corps) vs Mack (lost 13883) — Davout arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. And Mack was taken on that fie…
  - POPUP capture_choice[capture]: Bohemia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (169 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✗ Soult's infantry levy: Berthier shakes his head. 'The treasury cannot support this, Sire. Need 743 gold, have 331.'
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- enemy phase: 6 actions, 3 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke Charles attacks Teulie · Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 2482) vs Massena (lost 4658, own corps) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Archduke Charles (lost 1371) vs Teulie (lost 1764, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2808) vs Bernadotte (lost 2194, own corps) — Ney and Lannes arrived in time to steady Bernadotte's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
  - verbs: attack×3, stance_change×1, fortify×1, naval_expedition×1
- ORDER Davout [completed]: Mack taken prisoner Davout: "Accomplished as ordered. The army is intact."
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 3,230 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last…
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 3,230 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 699 · net +1139 · threat 82 · provinces 29 (+1) · ceiling 7787 · army 149929 · vassals Holland 97 · Kingdom of Italy 92 · Switzerland 92
  - NET income 2636 · trade 525 · admin 50 · tribute 799 · upkeep 2102 · occupation 100 · blockade 329 · admiralty 90 · laws 250
- MARSHALS Ney trust 75 Reliable glory 4 (#1) · Davout trust 85 Loyal glory 1 (#2) envies Ney · Soult trust 70 Reliable glory 0 (#3) envies Davout · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - TURN EVENTS 8
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 849.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% now, 12% at dawn (the …
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 2076 · net +1212 · threat 80 · provinces 29 (+0) · ceiling 8135 · army 149040 · vassals Holland 98 · Kingdom of Italy 82 · Switzerland 91
  - NET income 2637 · trade 587 · admin 50 · tribute 799 · upkeep 2038 · charges 15 · occupation 100 · blockade 368 · admiralty 90 · laws 250
- MARSHALS Ney trust 75 Reliable glory 4 (#1) · Davout trust 85 Loyal glory 1 (#2) envies Ney · Soult trust 70 Reliable glory 0 (#3) envies Davout · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG moment: Britain decrees the Magazines for 8 turns (5 authority)
  - LOG moment: Russia decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 5 — Late November 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,076.
- CMD `what does the Staff cost` → ✓ The laws of state, Sire. In force: the Anticipated Class, the Code Abroad. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 2,076. Berth…
- CMD `Ney, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Ney marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Ney, muster_confirm, Berthier stays the order a moment, Sire: before Ney marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Ney attacks Archduke Charles' to read the muster before you commit — it costs nothing.
MUSTER — Ney (19,937) vs Archduke Charles (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL NOT — Davout: is dug in and will not abandon his works
  WILL NOT — Bernadotte: will not lift a finger for Marshal Ney
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 19,937 we muster) would cost ~150g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 80/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP; 2 for Bernadotte, who stands neutral) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Ney (19,937) vs Archduke Charles (substantial force) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 6078) vs Archduke Charles (lost 1039, own corps) — Attacking prepared positions cost Ney dearly. The fortifications held.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (900 lost to march)
- CMD `Murat, move to Swabia` → ✗ Murat is already in Swabia.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 10 actions, 3 attacks — Prussia, Spain, the Ottoman Empire and 5 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Davout · Archduke John attacks Milan · Deroy attacks Archduke John
  - 🏴 Austria: Archduke John attacks Milan — The garrison of Milan is destroyed. · Region captured: Milan (was Kingdom of Italy) (secured)
  - ⚔ Kutuzov (lost 2360) vs Davout (lost 1992) — The enemy's assault has weakened our works. We must repair or consider withdrawal.
  - ⚔ Deroy (lost 2550) vs Archduke John (lost 1478) — Archduke John's square formation provided a solid defensive anchor, Sire.
  - verbs: attack×3, unfortify×2, recruit×2, move×1, form_square×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 2599 · net +799 · threat 78 · provinces 29 (+0) · ceiling 6379 · army 137590 · vassals Holland 97 · Kingdom of Italy 81 · Switzerland 88
  - NET income 2628 · trade 587 · admin 50 · tribute 712 · upkeep 2244 · charges 126 · occupation 100 · blockade 368 · admiralty 90 · laws 250
- MARSHALS Ney trust 75 Reliable glory 4 (#1) · Davout trust 85 Loyal glory 1 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) envies Davout · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 10
- DIPLO +5 medium/low (province_changed_hands, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,599.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `how many diplomatic points do I have` → ✓ Talleyrand holds 6 diplomatic points of 7 — 5 came with this morning's refill and 2 were carried from last turn; what he leaves unspent carries one turn, to at most 7. T…
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Munich instead.) → trust
  - ↳ MUSTER — Lannes (14,364; expect about 51,282 with the corps likely to arrive, up to 51,967 if all march; certain 38,273) vs Archduke John (13,579 men) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 719, own corps) vs Archduke John (lost 6203) — Murat, Bernadotte and Napoleon arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: retreat×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 3336 · net +682 · threat 79 · provinces 29 (+0) · ceiling 7016 · army 133475 · vassals Holland 99 · Kingdom of Italy 83 · Switzerland 99
  - NET income 2707 · trade 587 · admin 50 · tribute 487 · upkeep 2124 · charges 247 · occupation 70 · blockade 368 · admiralty 90 · laws 250
- MARSHALS Ney trust 75 Reliable glory 4 (#1) · Davout trust 85 Loyal glory 1 (#2) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 90 Loyal glory 1 (#3) vind +1 · Murat trust 75 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — the Emperor's star burns full again. The Presence stands at +10%, and Europe remembers what it feared.
  - EXPECTS: Lannes's victories raise his expectation — he now looks for 40g/turn (holds 0g).
  - TURN EVENTS 13
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 7 — Late December 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 3,336.
- CMD `repeal the Code Abroad` → ✓ The Code Abroad is repealed — its 100 gold a turn ends, and nothing is refunded. Enacting it again costs its full price (15 authority).
- CMD `what laws are in force` → ✓ The laws of state, Sire. In force: the Anticipated Class. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 3,336. The Train des Équipage…
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (18,077; expect about 69,887 with the corps likely to arrive, up to 70,615 if all march; certain 41,071) vs Archduke Charles (29,287 men) at Tyrol — the b…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 2084, own corps) vs Archduke Charles (lost 4760) — Davout, Lannes and Napoleon arrived in time to steady Murat's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 11 actions, 3 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bohemia · Archduke Charles attacks Bohemia · Archduke Charles attacks Bohemia
  - ⚔ Archduke Charles (lost 1935) vs Davout (lost 1793) — Neither Davout nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1447) vs Davout (lost 2145) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 1348) vs Davout (lost 1628) — Stalemate. Davout and Archduke Charles glare at each other across the field.
  - verbs: attack×3, stance_change×2, recruit×2, fortify×1, naval_expedition×1, unfortify×1, move×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 3643 · net +671 · threat 77 · provinces 29 (+0) · ceiling 6586 · army 121278 · vassals Holland 99 · Kingdom of Italy 83 · Switzerland 98
  - NET income 2616 · trade 587 · admin 50 · tribute 487 · upkeep 1988 · charges 373 · occupation 100 · blockade 368 · admiralty 90 · laws 150
- MARSHALS Ney trust 75 Reliable glory 4 (#1) · Davout trust 85 Loyal glory 1 (#2) envies Ney · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 90 Loyal glory 1 (#3) vind +1 · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Lannes, Murat, Bernadotte and Napoleon stand 47,344 men at Munich, which feeds 45,000. 2,344 too many. 3,324 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply to…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Carniola.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +5 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor

## Turn 8 — Early January 1806
  - MAILBOX #9 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #14 → reject_ai_proposal
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 3,643.
- CMD `enact the Code Abroad` → ✓ The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1…
  - POPUP clarification: The Council of State, The Code Abroad (the Civil Code imposed in Italy (1806), Westphalia (1807) and Warsaw (1808)): The Civil Code carried into the client states binds them to the Empire: +1 loyalty a turn in every one. 15 authority now, then 100 gold a turn. Authority 83 → 68 — the marshals' calm above 70 is lost; the Emperor's grip falls under 70 and the Charges of Empire rise by 50 rate points (32g a turn at today's chest) until it is restored; the Presence +10% → +7%. The treasury holds 3,643 gold. Enact it? (yes / no) → 1 (first option: Enact the Code Abroad)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Davout, attack Archduke Charles` → ✓ MUSTER — Davout (13,823; expect about 40,657 with the corps likely to arrive, up to 50,071 if all march; certain 25,434; a bad day (1 in 10) 39,116) vs Archduke Charles …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1445, own corps) vs Archduke Charles (lost 1769) — Reinforcements from Ney, Lannes and Napoleon bolstered Davout's position — though Murat never arrived, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 3 turns remaining.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena moves from Piedmont to Milan (181 lost to march)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: 6 actions, 1 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Davout
  - ⚔ Archduke Charles (lost 1033) vs Davout (lost 1837) — The margin was slim. Training and preparation would serve Davout well.
  - verbs: move×2, unfortify×1, fortify×1, attack×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 4106 · net +550 · threat 75 · provinces 29 (+0) · ceiling 6259 · army 113317 · vassals Holland 96 · Kingdom of Italy 82 · Switzerland 94
  - NET income 2590 · trade 587 · admin 50 · tribute 487 · upkeep 1864 · charges 537 · requisitions 75 · occupation 130 · blockade 368 · admiralty 90 · laws 250
- MARSHALS Ney trust 75 Reliable glory 3 (#1) · Davout trust 85 Loyal glory 1 (#2) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 90 Loyal glory 1 (#3) vind +1 · Murat trust 72 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) envies Davout · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Ney's corps has been broken at Tyrol. He must reform before he fights again.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 2 more turns
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,272g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - RAIL third_party_peace: THE CONGRESS: Austria and Bavaria have made their peace without France. Austria, beaten (-34), sues for peace and Bavaria takes it on the held line; …
  - TURN EVENTS 9
- DIPLO +4 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 2 more — Bavaria is not forgiven
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 9 — Late January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 4,106.
- CMD `what happened last turn` → ✓ This morning's dispatch leads with: Sire — Ney's corps has been broken at Tyrol. He must reform before he fights again. Overnight: Ney's army is recovering. Effectivenes…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `Murat, drill` → ✗ Murat cannot drill with enemy forces nearby! Archduke John is at Tyrol, just one region away.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Davout
  - 🏴 Austria: Archduke Charles attacks Davout — Bohemia CAPTURED! (was France) (secured)
  - ⚔ Archduke Charles (lost 701) vs Davout (lost 1991) — Davout's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×1, move×1, fortify×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #16 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #17 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Milan — the table with Austria + Russia (3 pairs resolved). Status quo: Milan stays Austrian by the treaty. Prisoners: Mack, our captive, goes home to Vienna under this peace — an Austrian commander back in the field. Prisoners: Teulie comes home to Paris under this peace. → display-only
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 4729 · net +313 · threat 73 · provinces 28 (-1) · ceiling 6325 · army 113801 · vassals Holland 95 · Kingdom of Italy 83 · Switzerland 92
  - NET income 2590 · trade 587 · admin 50 · tribute 487 · upkeep 2160 · charges 533 · blockade 368 · admiralty 90 · laws 250
- MARSHALS Ney trust 75 Reliable glory 3 (#1) · Davout trust 85 Loyal glory 1 (#2) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 90 Loyal glory 1 (#3) vind +1 · Murat trust 72 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 1 more turn
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War for Milan — Britain + Austria + Russia.
  - TURN EVENTS 8
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- DIPLO +7 medium/low (law_enacted_abroad ×2, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, coercive_demand, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 73 to 36; Britain remains at war with us.
  - LOG third_party_peace: THE CONGRESS: Austria and Bavaria make peace without France

## Turn 10 — Early February 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 4,729.
- CMD `what laws are in force` → ✓ The laws of state, Sire. In force: the Anticipated Class, the Code Abroad. The Grand Quartier Général: 9,000 gold, then 300 gold a turn — the treasury holds 4,729. The T…
- CMD `economy` → ✓ FRANCE TREASURY REPORT
- CMD `Ney, move to Franconia` → ✓ Ney moves from Munich to Franconia (120 lost to march)
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Croatia, Franconia, Munich, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, move×1, stance_change×1
- ORDER Massena [continues]: Massena marches to Munich. 1 region to Franche-Comte.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #18 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (81 → 91); bond -7 → 13 (+0 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 5142 · net +172 · threat 38 · provinces 28 (+0) · ceiling 6004 · army 110641 · vassals Holland 96 · Kingdom of Italy 91 · Switzerland 92
  - NET income 2590 · trade 587 · admin 50 · tribute 337 · upkeep 2060 · charges 624 · blockade 368 · admiralty 90 · laws 250
- MARSHALS Ney trust 75 Reliable glory 0 (#2) · Davout trust 85 Loyal glory 0 (#3) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 89 Loyal glory 1 (#1) vind +1 · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Lannes, Murat, Bernadotte and Napoleon have been 5 turns over what Munich can feed. 11,138 men dead. The country will ask where the army went. Bavaria's magazines feed us as our own — the army…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL status_quo_conceded: Milan — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Sire, the white peace of the War for Milan — the table with Austria + Russia writes no clause: each side keeps what it holds on the day of signing, t…
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover — Prussia's relations with every court, France's included, fall 15.
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 7
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: And Saxony stirs at its own design.
- DIPLO +4 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, agenda_shift, diplomatic_relation_shift)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (4 authority)

---
finished: **completed** · commands 75 · popups 38 · battles 20
