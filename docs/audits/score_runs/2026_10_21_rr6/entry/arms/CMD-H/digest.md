# Playtest digest — CMD-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `d940b5bcea37` · content `203320fb1bac` · driver `6a7b022e9e63`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1847, own corps) vs Mack (lost 24408) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Massena. Casualties: Archduke Charl… · Deroy delivers an effective strike. Deroy gains the advantage over Mack. Casualties: Deroy 983, Mack 8,861. Both armies…
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
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Brutal stalemate between Archduke Charles and Massena. Heavy casualties on … · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Charle…
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
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles struggles in a costly engagement. Brutal stalemate between Archduke Charles and Massena. Heavy casualt… · Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Char…
  - ⚔ Archduke Charles (lost 3013) vs Massena (lost 3743, own corps) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 1757) vs Teulie (lost 1200, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, wait×1
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
- enemy phase: 9 actions, 6 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John launches a decisive assault. Archduke John gains the advantage over Teulie. Casualties: Archduke John 161… · ArchdukeJohn assaults the Munich garrison! Garrison: 10,000 -> 5,771 (-4,229). ArchdukeJohn loses 3,499 troops. Garriso… · ArchdukeJohn assaults the Munich garrison! Garrison collapses (5,771 -> 0). ArchdukeJohn loses 2,385 troops in the assa… · Deroy's forces advance steadily. Brutal stalemate between Deroy and Archduke John. Heavy casualties on both sides: Dero…
  - 🏴 Austria: [!] No word came for Teulie, cornered at Milan — the enemy did not wait. [!] MARSHAL CAPTURED — Teulie is taken by Austria at Milan!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -119g, Bavaria -141g. Captured: Bavaria → Austria
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
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks with overwhelming force. Deroy gains the advantage over Archduke John. Casualties: Deroy 39, Archduke Joh…
  - 🏴 Bavaria: Deroy advances into Tyrol. (658 lost to march) Tyrol has been captured by Bavaria!
  - ⚔ Deroy (lost 39) vs Archduke John (lost 569) — Archduke John's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×1, wait×1
  - ⚡ AUTONOMOUS: [Shield] Archduke Charles steps forward to cover Archduke John's retreat! "Archduke John is in no condition to fight - I'll handle this!"
  - ⚔ Murat (lost 2674, own corps) vs Archduke Charles (lost 4211) — Ney, Davout and Lannes arrived in time to steady Murat's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 3165 · net +701 · threat 87 · provinces 29 (+0) · ceiling 8909 · army 137914 · vassals Holland 93 · Switzerland 92
  - NET income 2737 · trade 587 · admin 50 · tribute 337 · upkeep 2260 · charges 142 · contributions 110 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — the Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
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
- CMD `Ney, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Ney can give chase.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Murat (15,653) vs Archduke Charles (strength unknown) at Piedmont — the balance of force looks unfavorable.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Piedmont can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 15,653 we muster) would cost ~117g.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Murat (15,653) vs Archduke Charles (strength unknown) at Piedmont — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 4942) vs Archduke Charles (lost 1037) — The ground itself worked against Murat. Terrain matters, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy's attack meets fierce resistance. Archduke Charles holds the line. Casualties: Deroy 2,442, Archduke Charles 1,35…
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
- CMD `Davout, attack Archduke Charles` → ✓ Archduke Charles stands at Piedmont, six marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Davout, pursuit_ask, Archduke Charles stands at Piedmont, six marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Boh…
- CMD `Soult, drill` → ✗ Not enough actions! Need 1, have 0 — Soult cannot drill today.
- CMD `Massena, move to Milan` → ✗ Not enough actions! Need 1, have 0 — Massena cannot march to Milan today.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy faces a difficult fight. Archduke Charles holds the line. Casualties: Deroy 2,265, Archduke Charles 1,095. Both a… · Deroy marches from Tyrol into Carniola unopposed! (203 lost to march) Captured: Austria → Bavaria · Deroy delivers an effective strike. Deroy gains the advantage over Archduke John. Casualties: Deroy 592, Archduke John …
  - 🏴 Bavaria: Deroy marches from Tyrol into Carniola unopposed! (203 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy advances into Hungary. (162 lost to march) Hungary has been captured by Bavaria!
  - ⚔ Deroy (lost 2265) vs Archduke Charles (lost 1095) — A wise investment in fortification. Archduke Charles's position was impregnable to Deroy's assault.
  - ⚔ Deroy (lost 592) vs Archduke John (lost 2054) — Archduke John's army has been badly mauled. Deroy proved the stronger force today. And Archduke John was taken on that …
  - verbs: attack×3, fortify×1, wait×1
- ORDER Davout [active]: Davout is pursuing Archduke Charles.
- LEDGER treasury 4301 · net +491 · threat 83 · provinces 29 (+0) · ceiling 7993 · army 132675 · vassals Holland 91 · Switzerland 88
  - NET income 2790 · trade 587 · admin 50 · tribute 337 · upkeep 2380 · charges 305 · contributions 110 · occupation 20 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +10 medium/low (law_enacted_abroad ×2, province_changed_hands ×4, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✓ Lannes begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 1 action unused) Turn 10 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos launches a decisive assault. Castanos gains the advantage over Paget. Casualties: Castanos 652, Paget 1,493. B…
  - ⚔ Castanos (lost 652) vs Paget (lost 1493) — Paget's aggressive posture left the troops exposed when Castanos's attack came. — The Line Holds +15% (Paget)
  - verbs: move×1, attack×1
- ORDER Lannes [active]: Lannes is marching to Bohemia (2 turns remaining).
- ORDER Davout : Davout: 'Cannon fire at Vienna, Sire. Investigate?'
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Vienna, Sire. Investigate?' → investigate
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 4812 · net +434 · threat 81 · provinces 29 (+0) · ceiling 8000 · army 132243 · vassals Holland 91 · Switzerland 87
  - NET income 2781 · trade 587 · admin 50 · tribute 337 · upkeep 2360 · charges 382 · contributions 101 · occupation 20 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL settlement_offer_arrival: Austria, for Britain, Austria and Russia, has offered terms to settle the War for Bohemia — Britain + Austria + Russia.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 4
- DIPLO +9 medium/low (province_changed_hands ×5, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)

## Turn 10 — Early February 1806
  - MAILBOX #9 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #14 → request_settlement_revision
  - TERMS (settlement_confirm PROPOSE): peace
  - POPUP diplomatic_dialogue: settlement_confirm #15 → settlement_dial_harsher
  - TERMS (settlement_confirm PROPOSE): peace, gold_indemnity, gold_indemnity, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #16 → settlement_dial_harsher
  - TERMS (settlement_confirm PROPOSE): peace, gold_indemnity, gold_indemnity, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #17 → suspend_settlement_editor (closed — still unratifiable after one harsher dial: Will NOT carry as drafted — every court must reach 50. Holding out: Austria 20/50, Britai…)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Bohemia to Franconia (156 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Dresden. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortif…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Carniola, Franconia, Hungary, Moravia, Munich, Swabia, Tyrol.
  - saved `CMD-H_t10` → Game saved: CMD-H_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 8 actions, 5 attacks — Russia, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — Hiller marches from Vienna into Bohemia unopposed! (16 lost to march — forward supply lines reduce losses) Captured: Fr… · Hiller marches from Bohemia into Carniola unopposed! (39 lost to march) Captured: Bavaria → Austria · Hiller marches from Carniola into Hungary unopposed! (16 lost to march — forward supply lines reduce losses) Captured: … · Castanos engages in solid combat. Castanos gains the advantage over Paget. Casualties: Castanos 212, Paget 1,097. Both …
  - 🏴 Austria: Hiller marches from Vienna into Bohemia unopposed! (16 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - 🏴 Austria: Hiller marches from Bohemia into Carniola unopposed! (39 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Hiller marches from Carniola into Hungary unopposed! (16 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Berry!
  - ⚔ Castanos (lost 212) vs Paget (lost 1097) — Paget stood alone, Sire. Wellesley never came. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 750) vs Wellesley (lost 505) — Stalemate. Wellesley and Castanos glare at each other across the field. — The Line Holds +15% (Wellesley)
  - verbs: attack×5, move×2, stance_change×1
- ORDER Lannes [interrupted]: Lannes hears cannon fire! Abandoning orders — rushing to Hungary! Lannes moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) The …
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 4991 · net +145 · threat 81 · provinces 29 (+0) · ceiling 6030 · army 131958 · vassals Holland 91 · Switzerland 86
  - NET income 2612 · trade 587 · admin 50 · tribute 337 · upkeep 2396 · charges 416 · contributions 101 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - TURN EVENTS 7
- DIPLO +6 medium/low (province_changed_hands ×4, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain binds Russia to the war against France — no separate peace for 10 turns (300g/turn)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ Archduke John is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Lannes, attack Archduke John` → ✗ Archduke John is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (106 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Milan into Tyrol unopposed! (308 lost to march) Captured: Bavaria → Austria · Castanos delivers an effective strike. Brutal stalemate between Castanos and Wellesley. Heavy casualties on both sides:…
  - 🏴 Austria: ArchdukeCharles marches from Milan into Tyrol unopposed! (308 lost to march) Captured: Bavaria → Austria
  - ⚔ Castanos (lost 594) vs Wellesley (lost 519) — Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty. — The Line Holds +15% (Wellesley)
  - verbs: attack×2, fortify×1, unfortify×1, form_square×1
- ENVOYS WAITING 1 · Naples open borders
- LEDGER treasury 5141 · net +119 · threat 79 · provinces 29 (+0) · ceiling 5974 · army 131852 · vassals Holland 91 · Switzerland 85
  - NET income 2577 · trade 587 · admin 50 · tribute 337 · upkeep 2396 · charges 447 · contributions 61 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 6 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +6 medium/low (enemy_marshal_commissioned ×2, province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: 17 approaches from Prussia, Austria and Bavaria are rebuffed (open borders agreement)

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Tyrol, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier advises caution. 'Bohemia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1573, own corps) vs Archduke Charles (lost 1263) — Ney, Lannes and Napoleon marched to Murat's guns as ordered. It was not enough. — The corps system brought Ney in. — Berthier: the corps marched apart and arrived together.
- LEDGER treasury 5438 · net +269 · threat 77 · provinces 29 (+0) · ceiling 7241 · army 128029 · vassals Holland 89 · Switzerland 82
  - NET income 2636 · trade 612 · admin 50 · tribute 337 · upkeep 2328 · charges 511 · contributions 15 · occupation 40 · blockade 382 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Lisbon.
  - TURN EVENTS 9
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: 13 approaches from Prussia, Austria and Bavaria are rebuffed (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Murat, attack Archduke John` → ✗ Murat is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Dresden to Franconia (216 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 7 actions, 3 attacks — Russia, Prussia, the Ottoman Empire and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Provence unopposed! (194 lost to march) Captured: France → Austria · ArchdukeCharles marches from Provence into Lyonnais unopposed! (192 lost to march) Captured: France → Austria · Castanos flanks from Berry while allies attack from Bearn! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (194 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Provence into Lyonnais unopposed! (192 lost to march) Captured: France → Austria
  - ⚔ Castanos (lost 206) vs Wellesley (lost 403) — Hardly an engagement, Sire — a brush between Wellesley and Castanos, and the day moved on. — The Line Holds +15% (Wellesley)
  - verbs: move×3, attack×3, unfortify×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 5400 · net +179 · threat 75 · provinces 27 (-2) · ceiling 6563 · army 127813 · vassals Holland 89 · Switzerland 81
  - NET income 2390 · trade 612 · admin 50 · tribute 562 · upkeep 2328 · charges 522 · contributions 73 · occupation 40 · blockade 382 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_ai_proposal_refused: 18 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)

## Turn 14 — Early April 1806
  - MAILBOX #11 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #19 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Franconia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: 8 actions, 6 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel strikes back after successfully defending! · BOMBARDMENT: Shrapnel → Cuesta · Castanos's forces press forward aggressively. Castanos gains the advantage over Wellesley. Casualties: Castanos 174, We… · Cuesta flanks from Bearn while allies attack from Gascony! (+1 coordination)
  - 🏴 Spain: [!] MARSHAL CAPTURED — Wellesley is taken by Spain at Gascony!
  - ⚔ Castanos (lost 174) vs Wellesley (lost 309) — Where was Shrapnel? Wellesley held the field alone — reinforcement never came. — The Line Holds +15% (Wellesley)
  - ⚔ Cuesta (lost 51, own corps) vs Wellesley (lost 370) — Wellesley stood alone, Sire. Shrapnel never came. And Wellesley was taken on that field — Spain holds him. — The Line Holds +15% (Wellesley)
  - ⚔ Blake (lost 427) vs Shrapnel (lost 382) — An inconclusive affair. Both sides bloodied but unbroken. — The Line Holds +15% (Shrapnel)
  - ⚔ Deroy (lost 606) vs Liechtenstein (lost 2173) — Liechtenstein's army has been badly mauled. Deroy proved the stronger force today.
  - verbs: attack×6, move×1, wait×1
- ENVOYS WAITING 2 · Austria settlement offer · Switzerland client petition
- LEDGER treasury 5585 · net +145 · threat 73 · provinces 27 (+0) · ceiling 6512 · army 127813 · vassals Holland 89 · Switzerland 80
  - NET income 2387 · trade 612 · admin 50 · tribute 562 · upkeep 2328 · charges 559 · contributions 67 · occupation 40 · blockade 382 · admiralty 90
- DISPATCH: Sire — Lyonnais and Provence lie in enemy hands. Austria holds them.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads -4 for France (5 battles, 2 decisives kept); the war is …
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War for Bohemia — Britain + Austria + Russia.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Austria and Bavaria have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes …
  - TURN EVENTS 5
- DIPLO +6 medium/low (diplomatic_treaty_signed, province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_ai_proposal_refused: 10 courts rebuff Bavaria (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #12 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #21 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → accept_settlement_offer
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #22 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Bohemia — the table with Russia (1 pair resolved). → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- enemy phase: 10 actions, 2 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Cuesta launches a decisive assault. Cuesta gains the advantage over Shrapnel. Casualties: Cuesta 313, Shrapnel 669. Bot… · Blake flanks from Aragon while allies attack from Gascony! (+1 coordination)
  - 🏴 Spain: [!] MARSHAL CAPTURED — Shrapnel is taken by Spain at Bordelais!
  - ⚔ Cuesta (lost 313) vs Shrapnel (lost 669) — Shrapnel's fortified position was overwhelmed. A costly investment lost, Sire. — The Line Holds +15% (Shrapnel)
  - ⚔ Blake (lost 108, own corps) vs Shrapnel (lost 503) — Even Shrapnel's fortifications could not hold, Sire. Blake overran the position. And Shrapnel was taken on that field —… — The Line Holds +15% (Shrapnel)
  - verbs: recruit×3, stance_change×2, attack×2, drill×1, fortify×1, wait×1
- ENVOYS WAITING 2 · Britain armistice losing · Britain settlement offer
- LEDGER treasury 5614 · net +13 · threat 71 · provinces 27 (+0) · ceiling 5693 · army 127813 · vassals Holland 89 · Switzerland 90
  - NET income 2409 · trade 612 · admin 50 · tribute 337 · upkeep 2328 · charges 575 · occupation 20 · blockade 382 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 10 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL settlement_summary: Sire, the settlement of the War for Bohemia — the table with Russia is not a curtain call; it is an accounting. Spain must be read beside reactions f…
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain's terms to settle the War for Bohemia — Britain + Austria, under Russia's good offices.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - RAIL broken_bargain: The compact with Britain lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Austria (defensive alliance)
  - LOG sponsorship_expired: The bond between Britain and Austria runs its term
  - LOG coalition_member_left: Russia has left the coalition.

## Turn 16 — Early May 1806
  - MAILBOX #14 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #15 Britain incoming_settlement_offer: Britain — Settlement Offer, under Russia's good offices → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #23 → accept_ai_proposal
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #24 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #25 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Bohemia — the table with Britain (2 pairs resolved). → display-only
  - POPUP diplomatic_dialogue: Britain, armistice_losing #23 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #24 → accept_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Ney, move to Bohemia` → ✓ Ney begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Bohemia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×4, unfortify×1, recruit×1
- ORDER Ney [active]: Ney is marching to Bohemia (2 turns remaining).
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 7528 · net +1654 · threat 37 · provinces 27 (+0) · ceiling 19683 · army 127660 · vassals Holland 87 · Switzerland 90
  - NET income 2410 · trade 612 · admin 50 · tribute 337 · upkeep 984 · charges 751 · occupation 20
- DISPATCH: Sire — 3 turns now with Lyonnais and Provence in enemy hands. The country counts every one of them.
  - RAIL settlement_summary: Settlement of the War for Bohemia — the table with Britain: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And Austria stirs at its own design.
- DIPLO +6 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×2, agenda_shift)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 71 to 35.
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal
  - LOG third_party_peace: THE CONGRESS: Austria and Bavaria make peace without France

## Turn 17 — Late May 1806
  - MAILBOX #16 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #26 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franconia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3, drill×1, garrison×1, recruit×1
- LEDGER treasury 8847 · net +1139 · threat 39 · provinces 27 (+0) · ceiling 17220 · army 127660 · vassals Holland 96 · Switzerland 90
  - NET income 2412 · trade 612 · admin 50 · upkeep 984 · charges 931 · occupation 20
- DISPATCH: Sire — Lannes's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3
- LEDGER treasury 8419 · net -385 · threat 41 · provinces 27 (+0) · ceiling 6067 · army 127660 · vassals Holland 95 · Switzerland 90
  - NET income 2443 · trade 612 · admin 50 · upkeep 2328 · charges 1052 · occupation 20 · admiralty 90
- DISPATCH: Sire — the truce with Austria has collapsed — the war resumes where it stood, at its age, with its ledger.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Bohemia to Franconia (117 lost to march)
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 21.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 1 action unused) Turn 20 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Liechtenstein marches from Vienna into Bohemia unopposed! (14 lost to march — forward supply lines reduce losses) Captu…
  - 🏴 Austria: Liechtenstein marches from Vienna into Bohemia unopposed! (14 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - verbs: attack×1
- LEDGER treasury 7727 · net -602 · threat 43 · provinces 26 (-1) · ceiling 4142 · army 125525 · vassals Holland 94 · Switzerland 90
  - NET income 2246 · trade 574 · admin 50 · upkeep 2420 · charges 962 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - TURN EVENTS 4
- DIPLO +5 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Bohemia, just one region away.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-H_t20` → Game saved: CMD-H_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, recruit×2
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 7186 · net -466 · threat 45 · provinces 26 (+0) · ceiling 4459 · army 123602 · vassals Holland 93 · Switzerland 90
  - NET income 2247 · trade 574 · admin 50 · upkeep 2360 · charges 887 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes and Massena stand 60,834 men at Franconia, which feeds 60,000. 834 too many. 3,941 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too larg…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +5 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 21 — Late July 1806
  - MAILBOX #17 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #27 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Soult commands ours at Swabia, ground that takes no levy — march h…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 1 action unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 8357 · net +998 · threat 45 · provinces 26 (+0) · ceiling 15094 · army 121767 · vassals Holland 92 · Switzerland 90
  - NET income 2250 · trade 574 · admin 50 · upkeep 936 · charges 940
- DISPATCH: Sire — a truce with Austria is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +6 for France (1 battle, 2 decisives kept); the war is 2…
  - TURN EVENTS 6
- COURTS: The court of Austria eases over Redeem Italy — joining the stronger side for pay is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 9373 · net +1090 · threat 45 · provinces 26 (+0) · ceiling 16736 · army 119999 · vassals Holland 91 · Switzerland 90
  - NET income 2252 · trade 574 · admin 50 · tribute 225 · upkeep 920 · charges 1091
- DISPATCH: Sire — Lannes's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10732 · net +1199 · threat 45 · provinces 26 (+0) · ceiling 20889 · army 118284 · vassals Holland 90 · Switzerland 90
  - NET income 2292 · trade 574 · admin 50 · tribute 225 · upkeep 912 · charges 1030
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Russia and 3 lesser courts would march. Held by our truce: Austr…
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat is fortified and cannot drill. Abandon fortification first.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 11959 · net +1419 · threat 45 · provinces 26 (+0) · ceiling 23983 · army 116621 · vassals Holland 89 · Switzerland 90
  - NET income 2296 · trade 574 · admin 50 · tribute 562 · upkeep 888 · charges 1175
- DISPATCH: Sire — Lannes's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14397 · net +2409 · threat 45 · provinces 26 (+0) · ceiling 215083 · army 120007 · vassals Holland 88 · Switzerland 90
  - NET income 2299 · trade 574 · admin 50 · tribute 562 · upkeep 928 · charges 148
- DISPATCH: Sire — peace with Austria is signed. The truce has ripened into peace, signed on the held line. Status quo: Lyonnais and Provence stay Austrian by the treaty. Prisoners: Mack, our captive, goes home …
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL status_quo_conceded: Lyonnais and Provence — left with Austria by the peace, titled to them by treaty.
  - RAIL diplomatic_armistice_expired_peace: The armistice between Austria and France has concluded. Peace declared.
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 26 — Early October 1806
  - MAILBOX #18 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #28 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 16496 · net +2074 · threat 45 · provinces 26 (+0) · ceiling 189250 · army 118442 · vassals Holland 98 · Switzerland 90
  - NET income 2302 · trade 574 · admin 50 · tribute 225 · upkeep 904 · charges 173
- DISPATCH: Sire — London now pays Vienna 400 gold a turn against us. Her peace with us binds her 4 more turns.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18582 · net +2061 · threat 45 · provinces 26 (+0) · ceiling 190250 · army 116924 · vassals Holland 98 · Switzerland 90
  - NET income 2306 · trade 574 · admin 50 · tribute 225 · upkeep 896 · charges 198
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Russia and 3 lesser courts would march. Bound for now by a fresh…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 20676 · net +2068 · threat 45 · provinces 26 (+0) · ceiling 193000 · army 115452 · vassals Holland 98 · Switzerland 90
  - NET income 2331 · trade 574 · admin 50 · tribute 225 · upkeep 888 · charges 224
- DISPATCH: Sire — Russia enacts the War Ministry under Arakcheev — +5 morale from every drill.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22764 · net +2063 · threat 45 · provinces 26 (+0) · ceiling 194666 · army 114022 · vassals Holland 98 · Switzerland 90
  - NET income 2335 · trade 574 · admin 50 · tribute 225 · upkeep 872 · charges 249
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 34 and declare on turn 37: Britain, Russia and 3 lesser courts would march. Bound for now by a fresh…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
  - saved `CMD-H_t30` → Game saved: CMD-H_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 24838 · net +2049 · threat 45 · provinces 26 (+0) · ceiling 195583 · army 112636 · vassals Holland 98 · Switzerland 90
  - NET income 2338 · trade 574 · admin 50 · tribute 225 · upkeep 864 · charges 274
- DISPATCH: Sire — Austria would now join a league against us — relations −45. Britain pays her 400 gold a turn against us. The price to keep her out: Talleyrand brings her to −10 in 4 turns (4 DP); buying off h…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26907 · net +2045 · threat 50 · provinces 26 (+0) · ceiling 197250 · army 111293 · vassals Holland 98 · Switzerland 90
  - NET income 2342 · trade 574 · admin 50 · tribute 225 · upkeep 848 · charges 298
- DISPATCH: Sire — Lannes's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
- COURTS: And Austria stirs at its own design.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 28964 · net +2032 · threat 55 · provinces 26 (+0) · ceiling 198250 · army 109990 · vassals Holland 98 · Switzerland 90
  - NET income 2346 · trade 574 · admin 50 · tribute 225 · upkeep 840 · charges 323
- DISPATCH: Sire — Lannes's claim is 26 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Soult commands ours at Swabia, ground that takes no levy — march h…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 31007 · net +2355 · threat 60 · provinces 26 (+0) · ceiling 227250 · army 108725 · vassals Holland 98 · Switzerland 90
  - NET income 2349 · trade 574 · admin 50 · tribute 562 · upkeep 832 · charges 348
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sweden → Bid for Their Allegi…
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover and Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franconia. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 33372 · net +2337 · threat 59 · provinces 26 (+0) · ceiling 228083 · army 107499 · vassals Holland 98 · Switzerland 90
  - NET income 2351 · trade 574 · admin 50 · tribute 562 · upkeep 824 · charges 376
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 2 turns (2 DP); buying off her design costs 1…
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 35727 · net +2327 · threat 57 · provinces 26 (+0) · ceiling 229583 · army 106309 · vassals Holland 98 · Switzerland 90
  - NET income 2353 · trade 574 · admin 50 · tribute 562 · upkeep 808 · charges 404
- DISPATCH: Sire — St Petersburg now pays London 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 7 turns (7 DP); buying off her design …
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 35800 · net -64 · threat 55 · provinces 26 (+0) · ceiling 34000 · army 105155 · vassals Holland 98 · Switzerland 90
  - NET income 2355 · trade 574 · admin 50 · tribute 562 · upkeep 1940 · charges 1216 · blockade 359 · admiralty 90
- DISPATCH: Sire — Britain, Russia, Austria, Sweden, Hanover and Sardinia are at war with France. Britain tears up the Peace Treaty to do it. Russia tears up the Peace Treaty to do it. Austria tears up the Peace…
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Sweden, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 4 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +7 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- COURTS: And Sardinia, Britain and Austria stir at their own designs.
- DIPLO +13 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, blockade_begins ×3, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG coalition_declared: The Fourth British Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia and Sweden
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes cannot drill with enemy forces nearby! Mack is at Bohemia, just one region away.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, stance_change×1, fortify×1, recruit×1
- LEDGER treasury 35758 · net -176 · threat 53 · provinces 26 (+0) · ceiling 31350 · army 104035 · vassals Holland 100 · Switzerland 100
  - NET income 2357 · trade 574 · admin 50 · tribute 562 · upkeep 1920 · charges 1350 · blockade 359 · admiralty 90
- DISPATCH: Sire — London now pays Vienna 500 gold a turn against us — her war with us is paid for.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 11,140 men ashore at Piedmont.
  - TURN EVENTS 5
- DIPLO +6 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, paymaster_subsidy)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 2 actions unused) Turn 39 begins!
- enemy phase: 8 actions, 5 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel marches from Piedmont into Savoy unopposed! (222 lost to march) Captured: France → Britain · BOMBARDMENT: Shrapnel → Amey · Liechtenstein assaults the Hungary garrison! Garrison: 3,000 -> 1,500 (-1,500). Liechtenstein loses 531 troops. Garriso… · ArchdukeCharles assaults the Hungary garrison! The detachment capitulates to odds of 4:1 or better (1,500 -> 0). Archdu…
  - 🏴 Britain: Shrapnel marches from Piedmont into Savoy unopposed! (222 lost to march) Captured: France → Britain
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -20g, Bavaria -75g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1710, own corps) vs Deroy (lost 4344) — Deroy was close. A period of drilling could have changed the outcome.
  - verbs: attack×5, move×2, unfortify×1
- LEDGER treasury 35525 · net -358 · threat 51 · provinces 25 (-1) · ceiling 27386 · army 102587 · vassals Holland 100 · Switzerland 100
  - NET income 2280 · trade 574 · admin 50 · tribute 562 · upkeep 1900 · charges 1475 · blockade 359 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Britain. Enemy colours fly over French homeland soil. Shrapnel's corps of ~10,000 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - TURN EVENTS 4
- DIPLO +5 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 500g reaches Russia
  - LOG british_subsidy: Britain's gold: 500g reaches Russia
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Britain sign a Defensive Alliance
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG ai_ai_proposal_refused: 9 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 9 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: 9 approaches from Britain and Austria are rebuffed (defensive alliance)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Mack is at Bohemia, just one region away.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- enemy phase: 7 actions, 2 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Amey · Cuesta assaults the Piedmont garrison! Garrison: 3,000 -> 1,500 (-1,500). Cuesta loses 618 troops. Garrison holds — 1,5…
  - 🏴 Bavaria: Wrede moves from Munich to Tyrol. Tyrol falls to Bavaria!
  - verbs: move×4, attack×2, stance_change×1
- LEDGER treasury 35187 · net -455 · threat 49 · provinces 25 (+0) · ceiling 25687 · army 101544 · vassals Holland 100 · Switzerland 100
  - NET income 2280 · trade 574 · admin 50 · tribute 562 · upkeep 1880 · charges 1592 · blockade 359 · admiralty 90
- DISPATCH: Sire — Provence and Savoy lie in enemy hands. Austria and Britain hold them.
  - TURN EVENTS 3
- DIPLO +4 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 500g reaches Russia

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Mack is at Bohemia, just one region away.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franconia (+2% defense).
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
  - saved `CMD-H_t40` → Game saved: CMD-H_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Liechtenstein holds them at Tyrol while allies attack from Carniola! (+1 coordination) · Cuesta's attack meets fierce resistance. Shrapnel holds the line. Casualties: Cuesta's army 1,873, Shrapnel 920. Both a… · Blake struggles in a costly engagement. Shrapnel holds the line. Casualties: Blake's army 1,446, Shrapnel 621. Both arm…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -47g, Bavaria -336g. Tyrol has been captured by Austria!
  - ⚔ Liechtenstein (lost 158, own corps) vs Wrede (lost 6732) — An aggressive stance invites disaster when one is not the attacker, Sire. Wrede paid the price. And Wrede was taken on …
  - ⚔ Cuesta (lost 786, own corps) vs Shrapnel (lost 920) — The prepared defenses proved their worth. Cuesta could not dislodge Shrapnel. — The Line Holds +15% (Shrapnel)
  - ⚔ Blake (lost 1055, own corps) vs Shrapnel (lost 621) — A wise investment in fortification. Shrapnel's position was impregnable to Blake's assault. — The Line Holds +15% (Shrapnel)
  - verbs: attack×3, fortify×2
- LEDGER treasury 34752 · net -546 · threat 47 · provinces 25 (+0) · ceiling 24250 · army 100532 · vassals Holland 100 · Switzerland 100
  - NET income 2280 · trade 574 · admin 50 · tribute 562 · upkeep 1860 · charges 1703 · blockade 359 · admiralty 90
- DISPATCH: Sire — Tyrol has been taken by Austria.
  - TURN EVENTS 4
- DIPLO +4 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 500g reaches Sweden

---
finished: **completed** · commands 200 · popups 56 · battles 36
