# Playtest digest — CMD-H

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
- CMD `Ney, attack Archduke Charles` → ✓ Archduke Charles stands at Piedmont, three marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Tyrol, Bavaria's soil), or cancel?
  - POPUP clarification: Ney, pursuit_ask, Archduke Charles stands at Piedmont, three marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Tyrol, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
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
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Archduke Charles
  - ⚔ Deroy (lost 2442) vs Archduke Charles (lost 1350) — A standard affair. Nothing unusual to report.
  - verbs: wait×2, move×1, attack×1
- ORDER Ney [active]: Ney is pursuing Archduke Charles.
- LEDGER treasury 3548 · net +546 · threat 85 · provinces 29 (+0) · ceiling 7756 · army 132417 · vassals Holland 91 · Switzerland 89
  - NET income 2740 · trade 587 · admin 50 · tribute 337 · upkeep 2320 · charges 200 · contributions 150 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Piedmont. He must reform before he fights again.
  - TURN EVENTS 5
- DIPLO +4 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG province_returned: France hands Munich back to Bavaria — the liberated soil comes home
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Munich — Austria is not forgiven
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Archduke Charles stands at Milan, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Tyrol, Bavaria's soil), or cancel?
  - POPUP clarification: Davout, pursuit_ask, Archduke Charles stands at Milan, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Tyrol, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Tyr…
- CMD `Soult, drill` → ✗ Not enough actions! Need 1, have 0 — Soult cannot drill today.
- CMD `Massena, move to Milan` → ✗ Not enough actions! Need 1, have 0 — Massena cannot march to Milan today.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Archduke Charles · Deroy attacks Archduke John
  - 🏴 Bavaria: Deroy attacks Archduke John — Hungary CAPTURED! (was Austria) (secured)
  - ⚔ Deroy (lost 2265) vs Archduke Charles (lost 1081) — A wise investment in fortification. Archduke Charles's position was impregnable to Deroy's assault.
  - ⚔ Deroy (lost 592) vs Archduke John (lost 2030) — Archduke John's army has been badly mauled. Deroy proved the stronger force today. And Archduke John was taken on that …
  - verbs: attack×2, fortify×1, wait×1, move×1
- ORDER Davout [active]: Davout is pursuing Archduke Charles.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- LEDGER treasury 3984 · net +373 · threat 83 · provinces 29 (+0) · ceiling 6789 · army 131474 · vassals Holland 91 · Switzerland 88
  - NET income 2790 · trade 587 · admin 50 · tribute 337 · upkeep 2540 · charges 263 · contributions 110 · occupation 20 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 2 more turns
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +8 medium/low (law_enacted_abroad ×2, province_changed_hands ×3, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
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
- LEDGER treasury 4397 · net +579 · threat 81 · provinces 29 (+0) · ceiling 8647 · army 130903 · vassals Holland 91 · Switzerland 87
  - NET income 2781 · trade 587 · admin 50 · tribute 337 · upkeep 2272 · charges 325 · contributions 101 · occupation 20 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 1 more turn
  - RAIL settlement_offer_arrival: Austria, for Britain, Austria and Russia, has offered terms to settle the War for Bohemia — Britain + Austria + Russia.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 5
- DIPLO +10 medium/low (province_changed_hands ×5, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: 7 approaches from Austria, Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #9 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → request_settlement_revision
  - TERMS (settlement_confirm PROPOSE): peace
  - POPUP diplomatic_dialogue: settlement_confirm #16 → settlement_dial_harsher
  - TERMS (settlement_confirm PROPOSE): peace, gold_indemnity, gold_indemnity, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #17 → settlement_dial_harsher
  - TERMS (settlement_confirm PROPOSE): peace, gold_indemnity, gold_indemnity, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #18 → suspend_settlement_editor (closed — still unratifiable after one harsher dial: Will NOT carry as drafted — every court must reach 50. Holding out: Austria 7/50, Britain…)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Tyrol to Franconia (148 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortif…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Franconia, Hungary, Moravia, Munich, Swabia, Tyrol.
  - saved `CMD-H_t10` → Game saved: CMD-H_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 5 actions, 2 attacks — Austria, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Paget · Castanos attacks Wellesley
  - ⚔ Castanos (lost 216) vs Paget (lost 1176) — Paget stood alone, Sire. Wellesley never came. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 829) vs Wellesley (lost 491) — The battle unfolded without particular distinction. — The Line Holds +15% (Wellesley)
  - verbs: move×3, attack×2
- ORDER Lannes [interrupted]: Lannes hears cannon fire! Abandoning orders — rushing to Vienna! Lannes moves from Franconia to Dresden (168 lost to march)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 4957 · net +474 · threat 79 · provinces 29 (+0) · ceiling 8357 · army 130587 · vassals Holland 91 · Switzerland 86
  - NET income 2762 · trade 587 · admin 50 · tribute 337 · upkeep 2272 · charges 411 · contributions 101 · occupation 20 · blockade 368 · admiralty 90
- DISPATCH: Sire — not every court of the league has struck us. Britain has an open road to us — 1 march — and has not struck us. Russia has an open road to us — 1 march — and has not struck us.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain binds Russia to the war against France — no separate peace for 10 turns (300g/turn)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ Archduke John is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Lannes, attack Archduke John` → ✗ Archduke John is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (106 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 3 actions, 2 attacks — Austria, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Lannes · Castanos attacks Wellesley
  - ⚔ Kutuzov (lost 1637) vs Lannes (lost 2526) — The margin was slim. Training and preparation would serve Lannes well.
  - ⚔ Castanos (lost 657) vs Wellesley (lost 445) — Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty. — The Line Holds +15% (Wellesley)
  - verbs: attack×2, fortify×1
- ENVOYS WAITING 1 · Naples open borders
- LEDGER treasury 5362 · net +445 · threat 77 · provinces 29 (+0) · ceiling 8440 · army 127955 · vassals Holland 89 · Switzerland 83
  - NET income 2727 · trade 587 · admin 50 · tribute 337 · upkeep 2232 · charges 485 · contributions 61 · occupation 20 · blockade 368 · admiralty 90
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +9% this morning; the courts have begun to notice that he can be beaten.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +6 medium/low (enemy_marshal_commissioned ×2, province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: 18 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Tyrol, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Dresden, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Lannes · Kutuzov attacks Davout
  - ⚔ Kutuzov (lost 1064) vs Lannes (lost 3487) — A grievous defeat for Lannes, Sire. The losses are severe.
  - ⚔ Kutuzov (lost 1597) vs Davout (lost 2012) — Neither Davout nor Kutuzov could claim the field. The armies remain locked.
  - verbs: attack×2
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1322, own corps) vs Archduke Charles (lost 1491) — Ney, Davout and Napoleon marched to Murat's guns as ordered. It was not enough. — The corps system brought Ney in. — The corps system brought Davout in. — Berthier: the corps marched apart and arrived together.
- LEDGER treasury 5671 · net +506 · threat 75 · provinces 29 (+0) · ceiling 8937 · army 118655 · vassals Holland 85 · Switzerland 78
  - NET income 2670 · trade 612 · admin 50 · tribute 337 · upkeep 2088 · charges 568 · contributions 15 · occupation 20 · blockade 382 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Tyrol. He must reform before he fights again.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Lisbon.
  - TURN EVENTS 9
- DIPLO +6 medium/low (diplomatic_treaty_signed, province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: 4 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Murat, attack Archduke John` → ✗ Murat is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Bohemia to Franconia (163 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 8 actions, 3 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bohemia · Cuesta attacks Wellesley · Castanos attacks Wellesley
  - 🏴 Austria: Archduke Charles attacks Bohemia — Region captured: Bohemia (was France) (secured)
  - ⚔ Cuesta (lost 191, own corps) vs Wellesley (lost 900) — Wellesley's fortified position was overwhelmed. A costly investment lost, Sire. — The Line Holds +15% (Wellesley)
  - ⚔ Castanos (lost 93, own corps) vs Wellesley (lost 360) — A skirmish, Sire. Wellesley's men traded shots with Castanos; there was no battle to speak of. — The Line Holds +15% (Wellesley)
  - verbs: move×3, attack×3, unfortify×1, wait×1
- LEDGER treasury 5761 · net +289 · threat 73 · provinces 28 (-1) · ceiling 7588 · army 118492 · vassals Holland 85 · Switzerland 77
  - NET income 2484 · trade 612 · admin 50 · tribute 562 · upkeep 2280 · charges 594 · contributions 73 · blockade 382 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 8 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 7
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Franconia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 7 actions, 5 attacks — Britain, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Croatia · Archduke Charles attacks Deroy · Cuesta attacks Wellesley · Castanos attacks Shrapnel
  - 🏴 Austria: Archduke Charles attacks Deroy — Croatia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1196) vs Deroy (lost 2697) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 687) vs Deroy (lost 2950) — Even the favorable ground could not save Deroy, Sire. Archduke Charles overcame the terrain.
  - ⚔ Cuesta (lost 216) vs Wellesley (lost 597, own corps) — The walls were not enough. Cuesta broke through Wellesley's prepared defenses. — The Line Holds +15% (Wellesley)
  - ⚔ Castanos (lost 103, own corps) vs Shrapnel (lost 1010) — Shrapnel's guns were caught in transit when Castanos struck. The crews had no time to deploy. — The Line Holds +15% (Shrapnel)
  - ⚔ Cuesta (lost 16, own corps) vs Shrapnel (lost 765) — Cuesta exploited Shrapnel's movement. Artillery must be given time to set up. And Shrapnel was taken on that field — Sp… — The Line Holds +15% (Shrapnel)
  - verbs: attack×5, unfortify×1, move×1
- ENVOYS WAITING 2 · Austria armistice losing · Switzerland client petition
- LEDGER treasury 6094 · net +268 · threat 71 · provinces 28 (+0) · ceiling 7750 · army 118492 · vassals Holland 85 · Switzerland 76
  - NET income 2455 · trade 612 · admin 50 · tribute 562 · upkeep 2280 · charges 659 · blockade 382 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 9 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #11 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #20 → accept_ai_proposal
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #21 → grant the petition
  - POPUP diplomatic_dialogue: Austria, armistice_losing #20 → accept_ai_proposal
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (76 → 86); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Kutuzov is at Bohemia, just one region away.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: 8 actions, 1 attacks — Britain, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Deroy
  - ⚔ Archduke Charles (lost 158) vs Deroy (lost 1831) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: move×4, fortify×2, attack×1, recruit×1
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 6142 · net +27 · threat 69 · provinces 28 (+0) · ceiling 6300 · army 117366 · vassals Holland 85 · Switzerland 86
  - NET income 2460 · trade 612 · admin 50 · tribute 337 · upkeep 2280 · charges 680 · blockade 382 · admiralty 90
- DISPATCH: Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +8 for France (5 battles, 2 decisives kept); the war is …
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 3
- DIPLO +5 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The bond between Britain and Austria runs its term

## Turn 16 — Early May 1806
  - MAILBOX #13 Britain incoming_proposal: Britain — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #22 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 2 actions unused) Turn 17 begins!
- enemy phase: 8 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Liechtenstein attacks Deroy · Liechtenstein attacks Deroy · Archduke Charles attacks Deroy
  - ⚔ Liechtenstein (lost 86) vs Deroy (lost 1307) — Not one corps reached Deroy. Wrede was expected; Deroy fought the battle single-handed.
  - ⚔ Liechtenstein (lost 890) vs Wrede (lost 574) — The engagement proceeded as one might expect, Sire.
  - ⚔ Archduke Charles (lost 529) vs Wrede (lost 2816) — The hills were ours, but Archduke Charles took them. Wrede's position was overrun. And Wrede was taken on that field — …
  - verbs: attack×3, recruit×2, unfortify×1, move×1, wait×1
- ENVOYS WAITING 2 · Austria settlement offer · Holland client petition
- LEDGER treasury 6618 · net +383 · threat 67 · provinces 28 (+0) · ceiling 8897 · army 115986 · vassals Holland 83 · Switzerland 86
  - NET income 2467 · trade 612 · admin 50 · tribute 337 · upkeep 2220 · charges 773 · admiralty 90
- DISPATCH: Sire — a truce with Britain is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns. The ledger stands: the war score reads -7 for France (0 battles, 0 decisives kept); the war is …
  - RAIL settlement_offer_arrival: Austria has offered terms to settle the War with the Third Coalition — Britain + Austria + Russia.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Bavaria and Austria have made their peace without France. Bavaria, beaten (-23), sues for peace and Austria takes it on the held line; …
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 4
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And Sardinia and Austria stir at their own designs.
- DIPLO +6 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, blockade_broken ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
  - MAILBOX #14 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → request_settlement_revision
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #24 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → accept_settlement_offer
  -     ↳ refused: 'Review Settlement Offer' is not open, Sire — Every court in this offer has already made its peace; there is …
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #24 → grant the petition
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → request_settlement_revision
  -     ↳ refused: Every court in this offer has already made its peace; there is no one left for these terms to bind.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #23 already answered this chain)
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franconia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, drill×1, wait×1
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 6691 · net +45 · threat 65 · provinces 28 (+0) · ceiling 6953 · army 114409 · vassals Holland 92 · Switzerland 86
  - NET income 2474 · trade 612 · admin 50 · upkeep 2200 · charges 801 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Vienna 300 gold a turn against us. The coalition has its paymaster; it lacks only its armies.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG third_party_peace: THE CONGRESS: Bavaria and Austria make peace without France
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 18 — Early June 1806
  - MAILBOX #14 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → reject_settlement_offer
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 6936 · net +195 · threat 63 · provinces 28 (+0) · ceiling 8284 · army 112822 · vassals Holland 91 · Switzerland 86
  - NET income 2513 · trade 612 · admin 50 · upkeep 2180 · charges 710 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays Sweden 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 4 turns (4 DP); buying off her design …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Sweden against France (300g/turn)
  - LOG ai_ai_proposal_refused: Russia and Bavaria rebuff Sardinia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Munich. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, wait×1, recruit×1
- LEDGER treasury 7195 · net +215 · threat 61 · provinces 28 (+0) · ceiling 8673 · army 111237 · vassals Holland 90 · Switzerland 86
  - NET income 2517 · trade 612 · admin 50 · upkeep 2120 · charges 754 · admiralty 90
- DISPATCH: Sire — the truce with Austria has collapsed — the war resumes where it stood, at its age, with its ledger.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL allegiance_settled: The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Tyrol, just one region away.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-H_t20` → Game saved: CMD-H_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen attacks Provence
  - 🏴 Russia: Bennigsen attacks Provence — Region captured: Provence (was France) (secured)
  - verbs: attack×1, wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 6883 · net -267 · threat 59 · provinces 27 (-1) · ceiling 5044 · army 110212 · vassals Holland 89 · Switzerland 86
  - NET income 2372 · trade 612 · admin 50 · upkeep 2120 · charges 709 · blockade 382 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Russia. Enemy colours fly over French homeland soil. Bennigsen's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as do…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
  - TURN EVENTS 3
- DIPLO +6 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy, blockade_begins ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (400g/turn)
  - LOG sponsorship_expired: The bond between Britain and Russia runs its term

## Turn 21 — Late July 1806
  - MAILBOX #16 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #25 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'We outnumber them! Let me attack!' (Trust him and he will attack Liechtenstein at Tyrol instead.)
  - POPUP objection: Ney, Ney firmly objects: 'We outnumber them! Let me attack!' (Trust him and he will attack Liechtenstein at Tyrol instead.) → trust
  - ↳ MUSTER — Ney (11,312; expect about 41,473 with the corps likely to arrive, up to 42,291 if all march) vs Liechtenstein (screening force) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 292, own corps) vs Liechtenstein (lost 3100) — Reinforcements! Davout, Lannes and Napoleon marched onto the field beside Ney. The enemy's advantage melted away. — The Hofkriegsrat's orders reached Archduke Charles too late. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces (Liechtenstein) present at Tyrol!
- CMD `Lannes, fortify` → ✗ Lannes cannot fortify while engaged with enemy forces! Enemy present: Liechtenstein. Attack or retreat first.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Soult commands ours at Swabia, ground that takes no levy — march h…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena
  - ⚔ Archduke Charles (lost 1114) vs Massena (lost 3735, own corps) — Reinforcements from Ney and Murat bolstered Massena's position — though Bernadotte never arrived, Sire. — The corps system brought Ney in. — Berthier: the corps marched apart and arrived together.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 6831 · net +256 · threat 60 · provinces 27 (+0) · ceiling 8541 · army 100501 · vassals Holland 89 · Switzerland 85
  - NET income 2377 · trade 612 · admin 50 · upkeep 1628 · charges 720 · requisitions 37 · blockade 382 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Franconia. He must reform before he fights again.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns. The ledger stands: the war score reads -7 for France (2 battles, 0 decisives kept); the war is 2…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 12,086 men ashore at Piedmont.
  - RAIL settlement_offer_arrival: Austria has offered terms to settle the War for Provence — Britain + Austria + Russia.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: 8 courts rebuff Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 22 — Early August 1806
  - MAILBOX #17 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #26 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #27 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Provence — the table with Austria (1 pair resolved). Prisoners: Mack, our captive, goes home to Vienna under this peace — an Austrian commander back in the field. Prisoners: Teulie comes home to Paris under this peace. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Britain: Shrapnel moves to Lyonnais — Lyonnais falls (was France) and is secured
  - verbs: move×1, wait×1
- ORDER Davout [continues]: Davout marches to Munich. 1 region to Franche-Comte.
- ORDER Lannes [continues]: Lannes marches to Munich. 1 region to Franche-Comte.
- ORDER Napoleon [continues]: Napoleon marches to Munich. 1 region to Franche-Comte.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 6717 · net +128 · threat 59 · provinces 26 (-1) · ceiling 7589 · army 101144 · vassals Holland 90 · Switzerland 85
  - NET income 2301 · trade 612 · admin 50 · tribute 225 · upkeep 1900 · charges 688 · blockade 382 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Britain. Enemy colours fly over French homeland soil. Shrapnel's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as do…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL settlement_summary: Settlement of the War for Provence — the table with Austria: settlement ratified.
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 6
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG ai_ai_proposal_refused: 7 approaches from Britain and Austria are rebuffed (defensive alliance)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: 3 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel attacks Limousin
  - 🏴 Britain: Shrapnel attacks Limousin — Region captured: Limousin (was France) (secured)
  - verbs: wait×2, attack×1
- ORDER Lannes [completed]: Lannes arrives at Franche-Comte. Lannes: "It is done. Point me at something that shoots back, Sire."
- ORDER Napoleon [completed]: Napoleon arrives at Franche-Comte.
- LEDGER treasury 6948 · net +197 · threat 58 · provinces 25 (-1) · ceiling 8294 · army 98772 · vassals Holland 91 · Switzerland 85
  - NET income 2216 · trade 612 · admin 50 · tribute 225 · upkeep 1712 · charges 722 · blockade 382 · admiralty 90
- DISPATCH: Sire — Limousin has fallen to Britain. Enemy colours fly over French homeland soil. Shrapnel's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as do…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Teulie · Shrapnel attacks Berry
  - 🏴 Britain: Shrapnel attacks Berry — Region captured: Berry (was France) (secured)
  - verbs: attack×2, wait×2
- LEDGER treasury 7068 · net +440 · threat 56 · provinces 24 (-1) · ceiling 10075 · army 96263 · vassals Holland 92 · Switzerland 85
  - NET income 2071 · trade 612 · admin 50 · tribute 562 · upkeep 1644 · charges 739 · blockade 382 · admiralty 90
- DISPATCH: Sire — Berry has fallen to Britain. Enemy colours fly over French homeland soil. Shrapnel's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_ai_proposal_refused: 6 courts rebuff Britain (defensive alliance)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel attacks Guyenne · Shrapnel attacks Gascony
  - 🏴 Britain: Shrapnel attacks Guyenne — Region captured: Guyenne (was France) (secured)
  - 🏴 Britain: Shrapnel attacks Gascony — Region captured: Gascony (was France) (secured)
  - verbs: attack×2, wait×2, recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 7255 · net +156 · threat 54 · provinces 22 (-2) · ceiling 8192 · army 93949 · vassals Holland 93 · Switzerland 85
  - NET income 1880 · trade 612 · admin 50 · tribute 562 · upkeep 1604 · charges 872 · blockade 382 · admiralty 90
- DISPATCH: Sire — Guyenne has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - TURN EVENTS 11
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain binds Russia to the war against France — no separate peace for 10 turns (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 5 actions, 2 attacks — Austria, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel attacks Bearn · Bennigsen attacks Languedoc
  - 🏴 Britain: Shrapnel attacks Bearn — Region captured: Bearn (was France) (secured)
  - 🏴 Russia: Bennigsen attacks Languedoc — Region captured: Languedoc (was France) (secured)
  - 🏴 Russia: Bennigsen moves to Savoy — Savoy falls (was France) and is secured
  - verbs: attack×2, wait×2, move×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 7191 · net -53 · threat 52 · provinces 19 (-3) · ceiling 6867 · army 91722 · vassals Holland 94 · Switzerland 85
  - NET income 1640 · trade 612 · admin 50 · tribute 562 · upkeep 1584 · charges 861 · blockade 382 · admiralty 90
- DISPATCH: Sire — Bearn has fallen to Britain. Enemy colours fly over French homeland soil. Shrapnel's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL settlement_offer_arrival: Britain has offered terms to settle the War for Bearn — Britain + Russia. Asking 3310 gold.
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG ai_ai_proposal_refused: Naples rebuffs Russia (defensive alliance)

## Turn 27 — Late October 1806
  - MAILBOX #18 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #28 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #29 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Bearn — the table with Britain (2 pairs resolved). Status quo: Bearn, Berry, Gascony, Guyenne, Limousin and Lyonnais stay British by the treaty. → display-only
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 32% -> 34%
- CMD `end turn` → ✓ Turn 27 ended. Turn 28 begins!
- SPENT 600g on this turn's orders
- enemy phase: 5 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen attacks Burgundy
  - 🏴 Russia: Bennigsen attacks Burgundy — Region captured: Burgundy (was France) (secured)
  - 🏴 Russia: Bennigsen moves to Orleanais — Orleanais falls (was France) and is secured
  - 🏴 Russia: Bennigsen moves to Lorraine — Lorraine falls (was France) and is secured
  - verbs: move×2, wait×2, attack×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 4020 · net +641 · threat 24 · provinces 16 (-3) · ceiling 7879 · army 92514 · vassals Holland 93 · Switzerland 85
  - NET income 1410 · trade 612 · admin 50 · tribute 562 · upkeep 1568 · charges 335 · admiralty 90
- DISPATCH: Sire — Burgundy has fallen to Russia. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL status_quo_conceded: Bearn, Berry, Gascony, Guyenne, Limousin and Lyonnais — left with Britain by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of the War for Bearn — the table with Britain: Gold indemnity: 3310 gold from France to Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 7
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as an ultimatum.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×2)
  - LOG ai_ai_proposal_refused: 3 approaches from Russia and Sardinia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG instrument_lapsed: The bond between Britain and Russia lapses — Britain left the war first
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 52 to 26; Russia remains at war with us.

## Turn 28 — Early November 1806
  - MAILBOX #19 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #30 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +7 (93 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen attacks Nivernais
  - 🏴 Russia: Bennigsen attacks Nivernais — Region captured: Nivernais (was France) (secured)
  - verbs: wait×2, attack×1
- LEDGER treasury 4365 · net +294 · threat 22 · provinces 15 (-1) · ceiling 6376 · army 90383 · vassals Holland 100 · Switzerland 85
  - NET income 1370 · trade 612 · admin 50 · tribute 225 · upkeep 1528 · charges 345 · admiralty 90
- DISPATCH: Sire — Nivernais has fallen to Russia. Enemy colours fly over French homeland soil. Bennigsen's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as d…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 9
- DIPLO +4 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen attacks Flanders · Bennigsen attacks Flanders
  - 🏴 Russia: Bennigsen attacks Flanders — The garrison of Flanders is destroyed. · Region captured: Flanders (was France) (secured)
  - verbs: move×2, attack×2, wait×2
- LEDGER treasury 4197 · net +218 · threat 20 · provinces 14 (-1) · ceiling 5640 · army 88322 · vassals Holland 100 · Switzerland 85
  - NET income 1220 · trade 612 · admin 50 · tribute 225 · upkeep 1468 · charges 331 · admiralty 90
- DISPATCH: Sire — Flanders has fallen to Russia. Enemy colours fly over French homeland soil. Bennigsen's corps of 10,467 stands there. A garrison you detach (3,000 men) holds a province against a march, as doe…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
  - saved `CMD-H_t30` → Game saved: CMD-H_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen attacks Picardy · Bennigsen attacks Artois
  - 🏴 Russia: Bennigsen attacks Picardy — Region captured: Picardy (was France) (secured)
  - 🏴 Russia: Bennigsen attacks Artois — Region captured: Artois (was France) (secured)
  - verbs: attack×2, wait×2
- LEDGER treasury 4249 · net +43 · threat 18 · provinces 12 (-2) · ceiling 4500 · army 86331 · vassals Holland 100 · Switzerland 85
  - NET income 1070 · trade 612 · admin 50 · tribute 225 · upkeep 1440 · charges 384 · admiralty 90
- DISPATCH: Sire — Picardy has fallen to Russia. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing t…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Russia.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty, agenda_shift)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Russia sign a Defensive Alliance
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen attacks Teulie · Bennigsen attacks Champagne
  - 🏴 Russia: Bennigsen attacks Champagne — Region captured: Champagne (was France) (secured)
  - ⚔ Bennigsen (lost 393) vs Teulie (lost 1512) — Teulie's army has been badly mauled. Bennigsen proved the stronger force today.
  - verbs: attack×2, wait×2
- ORDER Teulie [awaiting_response]: Teulie is cornered at Paris with 3,268 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last…
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Paris with 3,268 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- LEDGER treasury 4198 · net +44 · threat 15 · provinces 11 (-1) · ceiling 4453 · army 79627 · vassals Holland 98 · Switzerland 83
  - NET income 1012 · trade 612 · admin 50 · tribute 225 · upkeep 1388 · charges 377 · admiralty 90
- DISPATCH: Sire — Champagne has fallen to Russia. Enemy colours fly over French homeland soil. Bennigsen's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as d…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Bennigsen attacks Ile-de-France · Bennigsen attacks Ardennes
  - 🏴 Russia: Bennigsen attacks Ile-de-France — Region captured: Ile-de-France (was France) (secured)
  - 🏴 Russia: Bennigsen attacks Ardennes — Region captured: Ardennes (was France) (secured)
  - verbs: attack×2, wait×2
- LEDGER treasury 4166 · net -26 · threat 12 · provinces 9 (-2) · ceiling 4010 · army 77761 · vassals Holland 98 · Switzerland 83
  - NET income 936 · trade 612 · admin 50 · tribute 225 · upkeep 1388 · charges 371 · admiralty 90
- DISPATCH: Sire — Ile-de-France has fallen to Russia. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps stan…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Davout commands ours at Munich, ground that takes no levy — march …
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 4225 · net +49 · threat 9 · provinces 9 (+0) · ceiling 4505 · army 75954 · vassals Holland 98 · Switzerland 83
  - NET income 941 · trade 612 · admin 50 · tribute 225 · upkeep 1308 · charges 381 · admiralty 90
- DISPATCH: Sire — the Emperor's star rises. The Presence stands at +4% this morning, up from where the defeats had left it.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 4268 · net +35 · threat 6 · provinces 9 (+0) · ceiling 4470 · army 74203 · vassals Holland 98 · Switzerland 83
  - NET income 945 · trade 574 · admin 50 · tribute 225 · upkeep 1280 · charges 389 · admiralty 90
- DISPATCH: Sire — Ardennes, Artois, Bearn and 16 more lie in enemy hands. Russia and Britain hold them.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Russia.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 4348 · net +404 · threat 3 · provinces 9 (+0) · ceiling 6696 · army 72502 · vassals Holland 98 · Switzerland 83
  - NET income 950 · trade 574 · admin 50 · tribute 562 · upkeep 1240 · charges 402 · admiralty 90
- DISPATCH: Sire — Lannes's claim is 29 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Bennigsen at Lorraine instead.)
  - POPUP objection: Ney, Ney respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Bennigsen at Lorraine instead.) → trust
  - ↳ MUSTER — Ney (6,949; expect about 20,764 with the corps likely to arrive, up to 21,491 if all march) vs Bennigsen (small force) at Lorraine — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 708, own corps) vs Bennigsen (lost 2210) — Reinforcement from Lannes, Massena and Napoleon kept Ney standing, Sire — but neither side yielded the ground. — Berthier: the corps marched apart and arrived together.
- CMD `Massena, fortify` → ✗ Massena is recovering from retreat and cannot fortify. Recovery: 3 turns remaining.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 4731 · net +404 · threat 0 · provinces 9 (+0) · ceiling 7069 · army 68931 · vassals Holland 98 · Switzerland 83
  - NET income 950 · trade 574 · admin 50 · tribute 562 · upkeep 1172 · charges 470 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Lorraine. He must reform before he fights again.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 5155 · net +351 · threat 0 · provinces 9 (+0) · ceiling 7185 · army 67568 · vassals Holland 98 · Switzerland 83
  - NET income 950 · trade 574 · admin 50 · tribute 562 · upkeep 1152 · charges 543 · admiralty 90
- DISPATCH: Sire — Britain, Austria and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 5506 · net +290 · threat 0 · provinces 9 (+0) · ceiling 7185 · army 66281 · vassals Holland 98 · Switzerland 83
  - NET income 950 · trade 574 · admin 50 · tribute 562 · upkeep 1152 · charges 604 · admiralty 90
- DISPATCH: Sire — the bidding for Sardinia is closed: she signs a defensive alliance with Russia.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Russia.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 49% -> 46%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 600g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 5299 · net +350 · threat 0 · provinces 9 (+0) · ceiling 7324 · army 68004 · vassals Holland 98 · Switzerland 83
  - NET income 950 · trade 574 · admin 50 · tribute 562 · upkeep 1128 · charges 568 · admiralty 90
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Allegiance.
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-H_t40` → Game saved: CMD-H_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 2 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 5689 · net +323 · threat 0 · provinces 9 (+0) · ceiling 7556 · army 66794 · vassals Holland 98 · Switzerland 83
  - NET income 950 · trade 574 · admin 50 · tribute 562 · upkeep 1088 · charges 635 · admiralty 90
- DISPATCH: Sire — Britain, Austria and 2 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Sweden: Talleyrand brings her to −10 in 2 turns…
  - UNMET: Lannes expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)

---
finished: **completed** · commands 200 · popups 68 · battles 43
