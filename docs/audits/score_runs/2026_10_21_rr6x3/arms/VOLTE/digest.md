# Playtest digest — VOLTE

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `846097827dc8` (dirty) · content `d8c0700dcbaa` · driver `ab03febad338`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
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
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 571 · net +359 · threat 77 · provinces 28 · ceiling 9417 · army 174609 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
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
- LEDGER treasury 772 · net +636 · threat 75 · provinces 28 (+0) · ceiling 12671 · army 164669 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 829 · upkeep 2912 · blockade 281 · admiralty 90
- DISPATCH: Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
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
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,407; expect about 47,322 with the corps likely to arrive, up to 47,970 if all march) vs Mack (substantial force) at Bohemia — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 299, own corps) vs Mack (lost 15770) — Davout arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. And Mack was taken on that fie…
  - POPUP capture_choice[capture]: Bohemia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (169 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 741 gold (×3 at war) (×1.24 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 741g on this turn's orders
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke Charles attacks Teulie
  - ⚔ Archduke Charles (lost 3013) vs Massena (lost 3743, own corps) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 1757) vs Teulie (lost 1200, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2
- ORDER Davout [completed]: Mack taken prisoner Davout: "Accomplished as ordered. The army is intact."
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 746 · net +1121 · threat 83 · provinces 29 (+1) · ceiling 13210 · army 158721 · vassals Holland 96 · Kingdom of Italy 95 · Switzerland 90
  - NET income 2636 · trade 525 · admin 50 · tribute 799 · upkeep 2400 · occupation 70 · blockade 329 · admiralty 90
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
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 2061 · net +1204 · threat 81 · provinces 29 (+0) · ceiling 13634 · army 157806 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 88
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
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
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
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
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
- LEDGER treasury 2700 · net +1035 · threat 79 · provinces 29 (+0) · ceiling 14840 · army 147272 · vassals Holland 92 · Kingdom of Italy 81 · Switzerland 82
  - NET income 2734 · trade 587 · admin 50 · tribute 799 · upkeep 2578 · charges 59 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Munich. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +11 medium/low (diplomatic_we_threshold ×2, enemy_marshal_commissioned, province_changed_hands, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, coercive_demand, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (300g/turn)

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Kutuzov is at Hungary, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attac…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Munich instead.) → trust
  - ↳ MUSTER — Lannes (15,578; expect about 52,635 with the corps likely to arrive, up to 53,203 if all march) vs Archduke John (6,266 men) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 311, own corps) vs Archduke John (lost 5088) — Murat, Bernadotte and Napoleon arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire. — Munich falls to Lannes. The last 2,000 of the garrison at Munich give way. — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Munich, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Archduke John
  - 🏴 Bavaria: Deroy attacks Archduke John — Tyrol CAPTURED! (was Austria) (secured)
  - ⚔ Deroy (lost 39) vs Archduke John (lost 569) — Archduke John's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×1, wait×1
  - ⚡ AUTONOMOUS: [Shield] Archduke Charles steps forward to cover Archduke John's retreat! "Archduke John is in no condition to fight - I'll handle this!"
  - ⚔ Murat (lost 2674, own corps) vs Archduke Charles (lost 4211) — Ney, Davout and Lannes arrived in time to steady Murat's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 3165 · net +701 · threat 87 · provinces 29 (+0) · ceiling 8909 · army 137914 · vassals Holland 93 · Switzerland 92
  - NET income 2737 · trade 587 · admin 50 · tribute 337 · upkeep 2260 · charges 142 · contributions 110 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — the Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - EXPECTS: Lannes's victories raise his expectation — he now looks for 40g/turn (holds 0g).
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL province_returned: France hands Munich back to Bavaria — the liberated soil comes home.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 9
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +10 medium/low (province_changed_hands ×4, enemy_marshal_commissioned ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `what are Ney's odds against Archduke Charles` → ✓ Ney stands at Bohemia, beyond reach of Archduke Charles at Piedmont this turn, Sire — the order would set him in pursuit, and there is no battle to weigh yet.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Murat (15,653) vs Archduke Charles (substantial force) at Piedmont — the balance of force looks unfavorable.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Piedmont can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 15,653 we muster) would cost ~117g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Murat (15,653) vs Archduke Charles (substantial force) at Piedmont — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 4942) vs Archduke Charles (lost 1037) — The ground itself worked against Murat. Terrain matters, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Archduke Charles
  - ⚔ Deroy (lost 2442) vs Archduke Charles (lost 1350) — A standard affair. Nothing unusual to report.
  - verbs: wait×2, move×1, attack×1
- LEDGER treasury 3728 · net +703 · threat 85 · provinces 29 (+0) · ceiling 9145 · army 132919 · vassals Holland 91 · Switzerland 89
  - NET income 2740 · trade 587 · admin 50 · tribute 337 · upkeep 2140 · charges 223 · contributions 150 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Piedmont. He must reform before he fights again.
  - TURN EVENTS 4
- DIPLO +4 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG province_returned: France hands Munich back to Bavaria — the liberated soil comes home
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Munich — Austria is not forgiven
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 8 — Early January 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `Davout, attack Archduke Charles` → ✓ Archduke Charles stands at Milan, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Tyrol, Bavaria's soil), or cancel?
  - POPUP clarification: Davout, pursuit_ask, Archduke Charles stands at Milan, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Tyrol, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Boh…
- CMD `Soult, drill` → ✗ Not enough actions! Need 1, have 0 — Soult cannot drill today.
- CMD `Massena, move to Milan` → ✗ Not enough actions! Need 1, have 0 — Massena cannot march to Milan today.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Archduke Charles
  - ⚔ Deroy (lost 2265) vs Archduke Charles (lost 1095) — A wise investment in fortification. Archduke Charles's position was impregnable to Deroy's assault.
  - verbs: fortify×1, attack×1, wait×1
- ORDER Davout [active]: Davout is pursuing Archduke Charles.
- LEDGER treasury 4301 · net +491 · threat 83 · provinces 29 (+0) · ceiling 7993 · army 132152 · vassals Holland 91 · Switzerland 88
  - NET income 2790 · trade 587 · admin 50 · tribute 337 · upkeep 2380 · charges 305 · contributions 110 · occupation 20 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 2 more turns
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +7 medium/low (law_enacted_abroad ×2, province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 1 action unused) Turn 10 begins!
- enemy phase: 6 actions, 3 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Paget · Deroy attacks Archduke Charles · Deroy attacks Archduke John
  - 🏴 Bavaria: Deroy moves to Carniola — Carniola falls (was Austria) and is secured
  - ⚔ Castanos (lost 652) vs Paget (lost 1493) — Paget's aggressive posture left the troops exposed when Castanos's attack came. — The Line Holds +15% (Paget)
  - ⚔ Deroy (lost 2078) vs Archduke Charles (lost 1060) — Archduke Charles's fortifications held firm, Sire. Deroy broke against our walls.
  - ⚔ Deroy (lost 760) vs Archduke John (lost 1195) — Archduke John's fortified position was overwhelmed. A costly investment lost, Sire.
  - verbs: attack×3, move×2, fortify×1
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
- ORDER Davout : Davout: 'Cannon fire at Milan, Sire. Investigate?'
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Milan, Sire. Investigate?' → investigate
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1174, own corps) vs Archduke Charles (lost 1674) — Napoleon arrived in time to steady Davout's position. The field was held, nothing further.
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 4736 · net +502 · threat 81 · provinces 29 (+0) · ceiling 8403 · army 130494 · vassals Holland 91 · Switzerland 87
  - NET income 2781 · trade 587 · admin 50 · tribute 337 · upkeep 2300 · charges 374 · contributions 101 · occupation 20 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 1 more turn
  - RAIL settlement_offer_arrival: Austria, for Britain, Austria and Russia, has offered terms to settle the War for Bohemia — Britain + Austria + Russia.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 4
- DIPLO +9 medium/low (province_changed_hands ×5, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 10 — Early February 1806
  - MAILBOX #9 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #14 → request_settlement_revision
  - TERMS (settlement_confirm PROPOSE): peace
  - POPUP diplomatic_dialogue: settlement_confirm #15 → settlement_dial_harsher
  - TERMS (settlement_confirm PROPOSE): peace, gold_indemnity, gold_indemnity, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #16 → settlement_dial_harsher
  - TERMS (settlement_confirm PROPOSE): peace, gold_indemnity, gold_indemnity, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #17 → suspend_settlement_editor (closed — still unratifiable after one harsher dial: Will NOT carry as drafted — every court must reach 50. Holding out: Austria -2/50, Britai…)
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Bohemia to Franconia (156 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Carniola, Franconia, Munich, Swabia, Tyrol.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 8 actions, 1 attacks — Prussia, the Ottoman Empire, Sweden and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Paget
  - 🏴 Russia: Kutuzov moves to Bohemia — Bohemia falls (was France) and is secured
  - ⚔ Castanos (lost 492) vs Paget (lost 873, own corps) — Wellesley marched to Paget's guns as ordered. It was not enough. — The Line Holds +15% (Paget)
  - verbs: stance_change×2, retreat×1, move×1, unfortify×1, fortify×1, recruit×1, attack×1
- ORDER Lannes [interrupted]: Lannes hears cannon fire! Abandoning orders — rushing to Milan! Lannes moves from Franconia to Tyrol (259 lost to march)
- LEDGER treasury 4721 · net -21 · threat 79 · provinces 28 (-1) · ceiling 4564 · army 129738 · vassals Holland 91 · Switzerland 86
  - NET income 2571 · trade 587 · admin 50 · tribute 337 · upkeep 2480 · charges 380 · contributions 248 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Russia.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL province_returned: Russia hands Bohemia back to Austria — the liberated soil comes home.
  - TURN EVENTS 4
- DIPLO +5 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain binds Russia to the war against France — no separate peace for 10 turns (300g/turn)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 9 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `Ney, attack Archduke John` → ✓ Archduke John stands at Vienna, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Dresden, Saxony's soil), or cancel?
  - POPUP clarification: Ney, pursuit_ask, Archduke John stands at Vienna, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Dresden, Saxony's soil), or cancel? → 1 (first option: Pursue Archduke John (2 AP))
- CMD `Lannes, attack Archduke John` → ✓ Archduke John stands at Vienna, two marches off. Pursue him (2 AP — a standing order; the first march meets Kutuzov at Bohemia, Austria's soil), or cancel?
  - POPUP clarification: Lannes, pursuit_ask, Archduke John stands at Vienna, two marches off. Pursue him (2 AP — a standing order; the first march meets Kutuzov at Bohemia, Austria's soil), or cancel? → 1 (first option: Pursue Archduke John (2 AP))
  - POPUP strategic_interrupt: Lannes, contact_bad_odds, Lannes: 'Kutuzov blocks the path at Bohemia. Odds unfavorable. Your orders?' Berthier adds: Ney and Massena would answer the guns — Lannes 12,593, 30,969 with the muster committed, against Kutuzov (substantial force) — weighed together, the balance of force looks even. → attack_anyway
  - ↳ Lannes attacks Kutuzov. MUSTER — Lannes (12,593; expect about 30,969 with the corps likely to arrive, up to 31,409 if all march) vs Kutuzov (substantial force) at Bohemia — the balance of force looks even — a hard fight that may well decide
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 2087, own corps) vs Kutuzov (lost 2583) — The reinforcement arrived, Sire. The verdict of the field went against us regardless. — Berthier: the corps marched apart and arrived together.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (106 lost to march)
- CMD `Massena, fortify` → ✗ Not enough actions! Need 1, have 0 — Massena cannot fortify today.
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Murat · Cuesta attacks Wellesley
  - ⚔ Kutuzov (lost 1707) vs Murat (lost 2035, own corps) — Lannes and Napoleon marched to Murat's guns as ordered. It was not enough. — Berthier: the corps marched apart and arrived together.
  - ⚔ Cuesta (lost 382) vs Wellesley (lost 850) — The walls were not enough. Cuesta broke through Wellesley's prepared defenses. And Wellesley was taken on that field — … — The Line Holds +15% (Wellesley)
  - verbs: move×3, attack×2, wait×1, fortify×1
- ENVOYS WAITING 1 · Naples open borders
- LEDGER treasury 4708 · net +411 · threat 77 · provinces 28 (+0) · ceiling 7400 · army 116473 · vassals Holland 87 · Switzerland 81
  - NET income 2567 · trade 587 · admin 50 · tribute 337 · upkeep 2220 · charges 412 · contributions 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Bohemia. He must reform before he fights again.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG province_returned: Russia hands Bohemia back to Austria — the liberated soil comes home

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Provence · Archduke Charles attacks Lyonnais
  - 🏴 Austria: Archduke Charles attacks Provence — Region captured: Provence (was France) (secured)
  - 🏴 Austria: Archduke Charles attacks Lyonnais — Region captured: Lyonnais (was France) (secured)
  - verbs: attack×2, fortify×1, wait×1
- LEDGER treasury 5177 · net +267 · threat 75 · provinces 26 (-2) · ceiling 7275 · army 114157 · vassals Holland 87 · Switzerland 80
  - NET income 2344 · trade 612 · admin 50 · tribute 337 · upkeep 2200 · charges 404 · blockade 382 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `Ney, attack Archduke John` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Murat, attack Archduke John` → ✗ Murat is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Tyrol to Franconia (171 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Limousin · Archduke John attacks Carniola · Archduke John attacks Hungary
  - 🏴 Austria: Archduke Charles attacks Limousin — Region captured: Limousin (was France) (secured)
  - 🏴 Austria: Archduke John attacks Carniola — Region captured: Carniola (was Bavaria) (secured)
  - 🏴 Austria: Archduke John attacks Hungary — Region captured: Hungary (was Bavaria) (secured)
  - verbs: attack×3, unfortify×1
- LEDGER treasury 5381 · net +388 · threat 73 · provinces 25 (-1) · ceiling 8318 · army 113190 · vassals Holland 87 · Switzerland 79
  - NET income 2242 · trade 612 · admin 50 · tribute 562 · upkeep 2160 · charges 446 · blockade 382 · admiralty 90
- DISPATCH: Sire — Limousin has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a marc…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL expedition_landed: THE LANDING: Paget has put 6,938 men ashore at Lisbon.
  - TURN EVENTS 6
- DIPLO +6 medium/low (province_changed_hands ×4, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 14 — Early April 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 8 actions, 5 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Berry · Hiller attacks Moravia · Archduke Charles attacks Normandy · Hiller attacks Hungary
  - 🏴 Austria: Archduke Charles attacks Berry — Region captured: Berry (was France) (secured)
  - 🏴 Austria: Hiller attacks Moravia — Region captured: Moravia (was Bavaria) (secured)
  - 🏴 Austria: Hiller attacks Hungary — Region captured: Hungary (was Bavaria) (secured)
  - 🏴 Bavaria: Deroy attacks Hiller — Hungary CAPTURED! (was Austria) (secured)
  - ⚔ Deroy (lost 214) vs Hiller (lost 889) — A grievous defeat for Hiller, Sire. The losses are severe.
  - verbs: attack×5, recruit×1, move×1, wait×1
- ENVOYS WAITING 2 · Austria armistice losing · Switzerland client petition
- LEDGER treasury 5808 · net +593 · threat 71 · provinces 24 (-1) · ceiling 10042 · army 112426 · vassals Holland 87 · Switzerland 78
  - NET income 2093 · trade 612 · admin 50 · tribute 562 · upkeep 1756 · charges 533 · requisitions 37 · blockade 382 · admiralty 90
- DISPATCH: Sire — Berry has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes …
  - TURN EVENTS 5
- DIPLO +9 medium/low (province_changed_hands ×4, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×3)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_ai_proposal_refused: 10 courts rebuff Bavaria (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #11 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #21 → accept_ai_proposal
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #22 → grant the petition
  - POPUP diplomatic_dialogue: Austria, armistice_losing #21 → accept_ai_proposal
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (78 → 88); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #22 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #23 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×1, wait×1
- ORDER Lannes [error]: Lannes could not advance toward Franche-Comte.
- ORDER Massena [continues]: Massena marches to Munich. 1 region to Franche-Comte.
- ORDER Ney [continues]: Ney marches to Munich. 1 region to Franche-Comte.
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 5765 · net -49 · threat 68 · provinces 24 (+0) · ceiling 5418 · army 110457 · vassals Holland 87 · Switzerland 88
  - NET income 2097 · trade 612 · admin 50 · tribute 337 · upkeep 2140 · charges 533 · blockade 382 · admiralty 90
- MISSION Improving Relations — Austria · net +11 a turn · ≈26 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Berry, Limousin, Lyonnais and 1 more lie in enemy hands. Austria holds them.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +1 for France (5 battles, 2 decisives kept); the war is …
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on…
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- DIPLO +8 medium/low (balance_of_europe_shifted, diplomatic_treaty_signed, province_changed_hands, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, blockade_broken, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: 8 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (design ask)
  - LOG sponsorship_expired: The bond between Britain and Austria runs its term
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 34% of active European bloc power.

## Turn 16 — Early May 1806
  - MAILBOX #13 Britain incoming_proposal: Britain — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #24 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #25 → start_mission
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Ney can already reach the body of the realm from where…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Tyrol. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Lannes
  - ⚔ Kutuzov (lost 666) vs Lannes (lost 3136) — Lannes stood alone, Sire. Bernadotte never came.
  - verbs: attack×1, break_square×1, fortify×1, recruit×1
- ORDER Massena [completed]: Massena arrives at Franche-Comte. Massena: "It is done. Point me at something that shoots back, Sire."
- ORDER Ney [completed]: Ney arrives at Franche-Comte. Ney: "Done — and I trust the next order has more fire in it."
- ORDER Lannes [awaiting_response]: Lannes is cornered at Tyrol with 4,999 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last…
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Tyrol with 4,999 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- ENVOYS WAITING 2 · Russia settlement offer · Holland client petition
- LEDGER treasury 6323 · net +677 · threat 65 · provinces 24 (+0) · ceiling 10909 · army 102322 · vassals Holland 83 · Switzerland 86
  - NET income 2098 · trade 612 · admin 50 · tribute 337 · upkeep 1692 · charges 638 · admiralty 90
- MISSION Improving Relations — Austria · net +11 a turn · ≈25 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lannes was mauled at Tyrol: a third of his corps — 3,136 men — lost in a single action.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -7 for France (0 battles, 0 decisives kept); the war is …
  - RAIL settlement_offer_arrival: Russia has offered terms to settle the War for Berry — Britain + Austria + Russia.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Britain eases over The Paymaster of Coalitions — alliance is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent, paymaster_subsidy, blockade_broken ×2, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG third_party_peace: THE CONGRESS: Austria and Bavaria make peace without France

## Turn 17 — Late May 1806
  - MAILBOX #14 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #26 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #27 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #26 → accept_settlement_offer
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #28 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Berry — the table with Russia (1 pair resolved). Prisoners: Lannes comes home to Paris under this peace. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #27 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #29 → start_mission
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 7744 · net +1254 · threat 62 · provinces 24 (+0) · ceiling 18403 · army 107322 · vassals Holland 92 · Switzerland 86
  - NET income 2099 · trade 612 · admin 50 · upkeep 832 · charges 675
- MISSION Improving Relations — Austria · net +11 a turn · ≈24 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Marshal Lannes has been taken. Russia holds him prisoner.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL settlement_summary: Settlement of the War for Berry — the table with Russia: settlement ratified.
  - RAIL broken_bargain: The compact with Britain lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — joining the stronger side for pay is now the length of its tether.
- COURTS: And Britain stirs at its own design.
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Russia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Russia breaks the bond with Britain — a separate peace with France inside the term
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Austria (defensive alliance)
  - LOG coalition_member_left: Russia has left the coalition.

## Turn 18 — Early June 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #30 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 8999 · net +1107 · threat 59 · provinces 24 (+0) · ceiling 18411 · army 107322 · vassals Holland 91 · Switzerland 86
  - NET income 2100 · trade 612 · admin 50 · upkeep 832 · charges 823
- MISSION Improving Relations — Austria · net +11 a turn · ≈23 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lannes's claim is 12 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Russia rebuffs Sardinia (defensive alliance)

## Turn 19 — Late June 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #31 → start_mission
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes begins marching to Franconia (distance: 6). Moved to Artois. Route: Artois -> Picardy -> Orleanais -> Lorraine -> Swabia -> Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 1 action unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [active]: Lannes is marching to Franconia (6 turns remaining).
- LEDGER treasury 10285 · net +1175 · threat 27 · provinces 24 (+0) · ceiling 23875 · army 112322 · vassals Holland 90 · Switzerland 86
  - NET income 2100 · trade 612 · admin 50 · upkeep 872 · charges 715
- MISSION Improving Relations — Austria · net +9 a turn · ≈17 turns to +100 at the present rate · beat running
- DISPATCH: Sire — peace with Austria is signed. The truce has ripened into peace, signed on the held line. Status quo: Berry, Limousin, Lyonnais and Provence stay Austrian by the treaty. Prisoners: Mack, our ca…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL status_quo_conceded: Berry, Limousin, Lyonnais and Provence — left with Austria by the peace, titled to them by treaty.
  - RAIL diplomatic_armistice_expired_peace: The armistice between Austria and France has concluded. Peace declared.
  - RAIL allegiance_settled: The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_coalition_dissolved, diplomatic_relation_shift)
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 59 to 29.

## Turn 20 — Early July 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #32 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 2 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [continues]: Lannes marches to Picardy. 4 regions to Franconia.
- LEDGER treasury 9895 · net -366 · threat 25 · provinces 24 (+0) · ceiling 6625 · army 112322 · vassals Holland 89 · Switzerland 86
  - NET income 2100 · trade 612 · admin 50 · upkeep 1772 · charges 884 · blockade 382 · admiralty 90
- MISSION Improving Relations — Austria · net +8 a turn · ≈16 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the truce with Britain has collapsed — the war resumes where it stood, at its age, with its ledger.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +11 medium/low (law_enacted_abroad ×3, doctrine_cured_abroad ×3, diplomatic_dp_regen, diplomatic_mission_progress, blockade_begins ×2, agenda_shift)

## Turn 21 — Late July 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #33 → start_mission
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Soult commands ours at Swabia, ground that takes no levy — march h…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 1 action unused) Turn 22 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Paget attacks Bearn
  - 🏴 Britain: Paget attacks Bearn — Region captured: Bearn (was France) (plundered)
  - 🏴 Britain: Paget moves to Gascony — Gascony falls (was France) and is sacked
  - verbs: attack×1, move×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 9339 · net -493 · threat 23 · provinces 22 (-2) · ceiling 4928 · army 112322 · vassals Holland 90 · Switzerland 86
  - NET income 1910 · trade 612 · admin 50 · upkeep 1772 · charges 821 · blockade 382 · admiralty 90
- MISSION Improving Relations — Austria · net +8 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Bearn has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL settlement_offer_arrival: Britain has offered terms to settle the War for Bearn — Britain. Asking 2380 gold.
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, balance_of_europe_shifted, diplomatic_auto_downgrade)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 36% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 8 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 22 — Early August 1806
  - MAILBOX #16 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #34 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #35 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Bearn — the table with Britain (2 pairs resolved). Status quo: Bearn and Gascony stay British by the treaty. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #36 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Massena is not currently fortified.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 8600 · net +1846 · threat 21 · provinces 22 (+0) · ceiling 162416 · army 112322 · vassals Holland 88 · Switzerland 86
  - NET income 1910 · trade 612 · admin 50 · tribute 225 · upkeep 872 · charges 79
- MISSION Improving Relations — Austria · net +8 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Bearn, Berry, Gascony and 3 more lie in enemy hands. Britain and Austria hold them.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL settlement_summary: Sire, the settlement of the War for Bearn — the table with Britain is not a curtain call; it is an accounting. France must be read beside reactions f…
  - RAIL status_quo_conceded: Bearn and Gascony — left with Britain by the peace, titled to them by treaty.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, blockade_broken ×2)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 23 — Late August 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #37 → start_mission
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Picardy. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10446 · net +1824 · threat 19 · provinces 22 (+0) · ceiling 162416 · army 112322 · vassals Holland 86 · Switzerland 86
  - NET income 1910 · trade 612 · admin 50 · tribute 225 · upkeep 872 · charges 101
- MISSION Improving Relations — Austria · net +7 a turn · ≈13 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lannes's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- DIPLO +7 medium/low (law_enacted_abroad ×4, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 24 — Early September 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #38 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12270 · net +2139 · threat 17 · provinces 22 (+0) · ceiling 190500 · army 112322 · vassals Holland 84 · Switzerland 86
  - NET income 1910 · trade 612 · admin 50 · tribute 562 · upkeep 872 · charges 123
- MISSION Improving Relations — Austria · net +7 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. Bound for now by a fresh peace: Britain. The cheapest court to keep out of it is Hanover: Talleyr…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 25 — Late September 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #39 → start_mission
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Picardy. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14409 · net +2114 · threat 15 · provinces 22 (+0) · ceiling 190500 · army 112322 · vassals Holland 82 · Switzerland 86
  - NET income 1910 · trade 612 · admin 50 · tribute 562 · upkeep 872 · charges 148
- MISSION Improving Relations — Austria · net +7 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Allegiance.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: Russia rebuffs Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 26 — Early October 1806
  - MAILBOX #17 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #40 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (82 → 92); bond 2 → 22 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #41 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16186 · net +1755 · threat 13 · provinces 22 (+0) · ceiling 162416 · army 112322 · vassals Holland 91 · Switzerland 86
  - NET income 1910 · trade 612 · admin 50 · tribute 225 · upkeep 872 · charges 170
- MISSION Improving Relations — Austria · net +7 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Britain would now join a league against us — relations −70. The price to keep her out: Talleyrand brings her to −10 in 7 turns (7 DP).
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 3
- DIPLO +6 medium/low (law_enacted_abroad ×4, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 27 — Late October 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #42 → start_mission
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Picardy. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Picardy (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 70% -> 58%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17695 · net +1713 · threat 11 · provinces 22 (+0) · ceiling 160416 · army 115322 · vassals Holland 90 · Switzerland 86
  - NET income 1910 · trade 612 · admin 50 · tribute 225 · upkeep 896 · charges 188
- MISSION Improving Relations — Austria · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the court of Austria eases over Redeem Italy — gold is now the length of its tether.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Redeem Italy — gold is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (design ask)

## Turn 28 — Early November 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #43 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Austria open borders
- LEDGER treasury 19408 · net +1693 · threat 9 · provinces 22 (+0) · ceiling 160416 · army 115322 · vassals Holland 89 · Switzerland 86
  - NET income 1910 · trade 612 · admin 50 · tribute 225 · upkeep 896 · charges 208
- MISSION Improving Relations — Austria · net +7 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 29 — Late November 1806
  - MAILBOX #18 Austria incoming_proposal: Austria — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Austria, open_borders #44 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #45 → start_mission
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Picardy. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Austria alliance
- LEDGER treasury 21804 · net +1601 · threat 1 · provinces 21 (-1) · ceiling 155166 · army 115322 · vassals Holland 88 · Switzerland 86
  - NET income 1830 · trade 637 · admin 50 · tribute 225 · upkeep 904 · charges 237
- MISSION Improving Relations — Austria · net +7 a turn · ≈7 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the enemy has held Bearn, Berry, Gascony and 4 more 8 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_treaty_signed, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_mission_progress, agenda_shift)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 30 — Early December 1806
  - MAILBOX #19 Austria incoming_proposal: Austria — Full Alliance → activated
  - POPUP diplomatic_dialogue: Austria, alliance #46 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: Open Borders → Alliance with Austria. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% on…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23442 · net +1618 · threat 0 · provinces 21 (+0) · ceiling 158250 · army 115322 · vassals Holland 87 · Switzerland 86
  - NET income 1830 · trade 674 · admin 50 · tribute 225 · upkeep 904 · charges 257
- MISSION Improving Relations — Austria · net +7 a turn · ≈6 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the enemy has held Bearn and Gascony 9 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL volte_face: THE VOLTE-FACE: Austria, beaten and then courted, takes France's hand. Her court turns its gaze to The Eastern Question.
  - TURN EVENTS 3
- DIPLO +7 medium/low (balance_of_europe_shifted, diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, agenda_shift ×3)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Austria are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Russia (defensive alliance)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 48% of active European bloc power.

## Turn 31 — Late December 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Picardy. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25060 · net +1599 · threat 0 · provinces 21 (+0) · ceiling 158250 · army 115322 · vassals Holland 86 · Switzerland 86
  - NET income 1830 · trade 674 · admin 50 · tribute 225 · upkeep 904 · charges 276
- MISSION Improving Relations — Austria · net +7 a turn · ≈5 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lannes's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over The Eastern Question — prepared now to go as far as an ultimatum.
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG volte_face: THE VOLTE-FACE: Austria, beaten and then courted, takes France's hand

## Turn 32 — Early January 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26659 · net +1580 · threat 0 · provinces 21 (+0) · ceiling 158250 · army 115322 · vassals Holland 85 · Switzerland 86
  - NET income 1830 · trade 674 · admin 50 · tribute 225 · upkeep 904 · charges 295
- MISSION Improving Relations — Austria · net +7 a turn · ≈4 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 33 — Late January 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Picardy. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Soult commands ours at Swabia, ground that takes no levy — march h…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 28239 · net +1898 · threat 0 · provinces 21 (+0) · ceiling 186333 · army 115322 · vassals Holland 84 · Switzerland 86
  - NET income 1830 · trade 674 · admin 50 · tribute 562 · upkeep 904 · charges 314
- MISSION Improving Relations — Austria · net +7 a turn · ≈3 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 34 — Early February 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 30112 · net +1850 · threat 0 · provinces 21 (+0) · ceiling 184250 · army 115322 · vassals Holland 83 · Switzerland 86
  - NET income 1830 · trade 649 · admin 50 · tribute 562 · upkeep 904 · charges 337
- MISSION Improving Relations — Austria · net +7 a turn · ≈2 turns to +100 at the present rate · beat running
- DISPATCH: Sire — relations between France and Spain have collapsed: Alliance → Defensive Alliance.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
  - MAILBOX #20 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #47 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (83 → 93); bond 22 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Picardy. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31625 · net +1495 · threat 0 · provinces 21 (+0) · ceiling 156166 · army 115322 · vassals Holland 93 · Switzerland 86
  - NET income 1830 · trade 649 · admin 50 · tribute 225 · upkeep 904 · charges 355
- MISSION Improving Relations — Austria · net +7 a turn · ≈1 turn to +100 at the present rate · beat running
- DISPATCH: Sire — Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 36 — Early March 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% on…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 33120 · net +1477 · threat 0 · provinces 21 (+0) · ceiling 156166 · army 115322 · vassals Holland 93 · Switzerland 86
  - NET income 1830 · trade 649 · admin 50 · tribute 225 · upkeep 904 · charges 373
- MISSION ended: Improving Relations — Austria, relations reached +100
- DISPATCH: Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL crisis_brewing: THE BREWING CRISIS: Austria will move on Ottoman. You may compensate (1,200g — you can afford it); guarantee Ottoman (1 DP — 6 in hand); or let the w…
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_completed)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Austria are rebuffed (design ask)
  - LOG design_bought_off: Ottoman Empire buys off Austria's design — the want sleeps

## Turn 37 — Late March 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Picardy. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 34597 · net +1459 · threat 0 · provinces 21 (+0) · ceiling 156166 · army 115322 · vassals Holland 93 · Switzerland 86
  - NET income 1830 · trade 649 · admin 50 · tribute 225 · upkeep 904 · charges 391
- DISPATCH: Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL crisis_passed: Austria stands down over Ottoman, Sire — the design was bought off — compensation stands.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade ×2)
  - LOG auto_downgrade: Relations auto-downgraded: Britain–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Britain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 38 — Early April 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 36056 · net +1442 · threat 0 · provinces 21 (+0) · ceiling 156166 · army 115322 · vassals Holland 93 · Switzerland 86
  - NET income 1830 · trade 649 · admin 50 · tribute 225 · upkeep 904 · charges 408
- DISPATCH: Sire — Austria stands down over Ottoman Empire; the design was bought off, and the bargain stands.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Picardy (field levy — no depot; capped at 3,000) - Cost: 205 gold (×1.03 over the ordinance). Morale: 78% -> 67%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 205g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 37234 · net +1392 · threat 0 · provinces 21 (+0) · ceiling 153166 · army 118322 · vassals Holland 93 · Switzerland 86
  - NET income 1830 · trade 649 · admin 50 · tribute 225 · upkeep 940 · charges 422
- DISPATCH: Sire — Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franche-Comte (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 38626 · net +1375 · threat 0 · provinces 21 (+0) · ceiling 153166 · army 118322 · vassals Holland 93 · Switzerland 86
  - NET income 1830 · trade 649 · admin 50 · tribute 225 · upkeep 940 · charges 439
- DISPATCH: Sire — the allegiance of Sweden is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sweden → Bid for Their Allegiance.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sweden → Bid for Their Allegi…
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing_other, agenda_shift)
  - LOG coalition_brewing_started: Coalition brewing against Austria — Bavaria consulting (their alarm: 60)
  - LOG sponsorship_granted: Russia sponsors Sweden against Austria (400g/turn)
  - LOG ai_ai_proposal_refused: Russia rebuffs Sweden (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sweden (design ask)

---
finished: **completed** · commands 236 · popups 79 · battles 29
