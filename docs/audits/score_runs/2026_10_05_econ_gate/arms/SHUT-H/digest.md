# Playtest digest — SHUT-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `47eb92ffc944` (dirty) · content `aae077cedc7a` · driver `e498338939cb`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `declare war on Portugal` → ✓ Choose your war purpose against Portugal.
  - POPUP diplomatic_dialogue: war_purpose_selection #1 → 1
  - POPUP diplomatic_objection: diplomatic_declare_war, Portugal → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #2 → ally_entry_proceed_without
- CMD `declare war on the Papal States` → ✓ Choose your war purpose against PapalStates.
  - POPUP diplomatic_dialogue: war_purpose_selection #3 → 1
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #4 → ally_entry_proceed_without
- CMD `Soult, march to Lisbon` → ✓ Soult begins march to Lisbon. Route: Orleanais → Burgundy → Limousin → Gascony → Bearn → Cartagena → Andalusia → Lisbon. Moves to Orleanais. "Soult, march to Lisbon." Un…
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Route: Piedmont → Rome. Moves to Piedmont. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Bernadotte. Casualties:…
  - ⚔ Archduke Charles (lost 1793) vs Bernadotte (lost 6846) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- ORDER Massena [active]: Massena is marching to Rome (1 turn remaining).
- ORDER Soult [active]: Soult is marching to Lisbon (7 turns remaining).
- ENVOYS WAITING 1 · Denmark open borders
- LEDGER treasury 1626 · net +1168 · threat 97 · provinces 28 · ceiling 28306 · army 179344 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2450 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 6,846 men — lost in a single action.
  - RAIL diplomatic_war_declared: France has declared war on Portugal, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: France has declared war on PapalStates, with 2 allied courts poised to follow.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +9 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 2 — Early October 1805
  - LETTER Denmark: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 107,250 with the corps likely to arrive, up to 113,685 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1835, own corps) vs Mack (lost 23671) — Reinforcements! Davout, Lannes, Murat and Napoleon marched onto the field beside Ney. The enemy's advantage melted away. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Swabia, Ney → secure
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Deroy. Casualties: Arch…
  - 🏴 Austria: Casualties: Archduke Charles 1,101, Bernadotte's army 9,886. Both armies remain in the field. Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1101) vs Bernadotte (lost 5984, own corps) — Ney reached Bernadotte in time, Sire — but even together, the field could not be held.
  - ⚔ Archduke Charles (lost 2140) vs Deroy (lost 5645) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×2, move×1, wait×1
- ORDER Soult [continues]: Soult marches to Burgundy. 6 regions to Lisbon.
- ORDER Massena [interrupted]: Massena hears cannon fire! Abandoning orders — rushing to Munich! Massena moves from Piedmont to Milan (1,178 lost to march)
- LEDGER treasury 2799 · net +1846 · threat 97 · provinces 29 (+1) · ceiling 23491 · army 157006 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2620 · trade 400 · admin 50 · tribute 937 · upkeep 1618 · charges 71 · contributions 80 · occupation 52 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +7 medium/low (diplomatic_treaty_signed, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 29 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
- CMD `Ney, attack Mack` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,321; expect about 82,802 with the corps likely to arrive, up to 95,277 if all march) vs Mack (substantial force) at Franche-Comte — the balance of fo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 324, own corps) vs Mack (lost 19862) — Reinforcements from Lannes, Murat and Napoleon bolstered Davout's position — though Amey never arrived, Sire.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Franche-Comte to Swabia (157 lost to march)
- CMD `Massena, attack Rome` → ✗ Massena cannot reach Rome from Milan! Range: 1, Distance: 2
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc… · ArchdukeCharles holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Swabia!
  - ⚔ Archduke Charles (lost 927) vs Bernadotte (lost 2258, own corps) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today. And Bernadotte was taken on …
  - ⚔ Archduke Charles (lost 1130) vs Deroy (lost 6706) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, wait×2, retreat×1, stance_change×1
- ORDER Soult [continues]: Soult marches to Limousin. 5 regions to Lisbon.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 4665 · net +2064 · threat 97 · provinces 29 (+0) · ceiling 25383 · army 143934 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2575 · trade 400 · admin 50 · tribute 937 · upkeep 1218 · charges 265 · occupation 75 · blockade 250 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia and Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Route: Piedmont → Rome. Moves to Piedmont. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `Massena, attack Rome` → ✓ ASSAULT — Massena storms the works at Rome alone: 35,829 men, 42,027 in the assault's reckoning (+2% from the corps at his side), against a garrison of 10,000. the garri…
  - ↳ Massena assaults the Rome garrison! Garrison: 10,000 -> 5,000 (-5,000). Massena loses 2,131 troops. Garrison holds — 5,000 defenders remain. It regains up to 2,000 a tur…
- CMD `Ney, attack Mack` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (21,960; expect about 40,412 with the corps likely to arrive, up to 41,126 if all march) vs Mack (7,776 men) at Munich — the balance of force looks favor…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 128, own corps) vs Mack (lost 6449) — Napoleon and Teulie arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
- ORDER Soult [continues]: Soult marches to Gascony. 4 regions to Lisbon.
- LEDGER treasury 6431 · net +1676 · threat 97 · provinces 29 (+0) · ceiling 22419 · army 138694 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2597 · trade 400 · admin 50 · tribute 937 · upkeep 1452 · charges 464 · occupation 52 · blockade 250 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Munich — Mack's corps breaks a second time on this ground and flees.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Portugal and Papal States rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Massena, attack Rome` → ✓ ASSAULT — Massena storms the works at Rome alone: 33,636 men, 38,681 in the assault's reckoning, against a garrison of 7,000. the garrison breaks below 5,000.
  - ↳ Massena assaults the Rome garrison! Garrison collapses (7,000 -> 0). Massena loses 1,521 troops in the assault. Massena marches into Rome! (963 lost to march)
  - POPUP capture_choice[capture]: Rome, Massena → secure
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Murat, attack Archduke Charles` → ✓ Murat pursues Archduke Charles (at Franconia). Cavalry charges through Swabia -> Franconia. The province is secured. A standing order, not a single attack: he closes 2 p…
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's assault collapses into chaos! Brutal stalemate between Archduke Charles and Murat. Heavy casualties …
  - ⚔ Archduke Charles (lost 3437) vs Murat (lost 2416, own corps) — Ney, Davout, Napoleon and Teulie arrived in time to steady Murat's position. The field was held, nothing further. — The corps system brought Davout in. — The corps system brought Teulie in. — Berthier: the corps marched apart and arrived together.
  - verbs: attack×1, wait×1
- ORDER Murat [active]: Murat is pursuing Archduke Charles (0 turns remaining).
- ORDER Soult [continues]: Soult marches to Bearn. 3 regions to Lisbon.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7747 · net +1425 · threat 97 · provinces 31 (+2) · ceiling 20791 · army 131811 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2662 · trade 362 · admin 50 · tribute 919 · upkeep 1368 · charges 627 · occupation 257 · blockade 226 · admiralty 90
- DISPATCH: Sire — Papal States is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Sire — the Papal States has been eliminated from the war.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +6 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy, coercive_demand, cs_tier_shift)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Naples and Russia (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 4 approaches to Britain and Russia are rebuffed (open borders agreement)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign a Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign a Open Borders Agreement

## Turn 6 — Early December 1805
  - MAILBOX #2 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #8 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +6 (94 → 100); bond -30 → -10 (-1 a turn). Cost: 1 DP. → display-only
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "We march. Pity whatever slows us."
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Bearn! Range: 1, Distance: 3
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
- ORDER Soult [continues]: Soult marches to Cartagena. 2 regions to Lisbon.
- ORDER Murat [continues]: Murat hears cannon fire at Milan but cannot answer it — Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles. The pur…
- LEDGER treasury 8394 · net +556 · threat 85 · provinces 31 (+0) · ceiling 13334 · army 130930 · vassals Holland 100 · Switzerland 99
  - NET income 2742 · trade 362 · admin 50 · tribute 337 · upkeep 1696 · charges 718 · occupation 205 · blockade 226 · admiralty 90
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +7 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, cs_tier_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Naples (defensive alliance)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: PapalStates rebuffs Britain (defensive alliance)

## Turn 7 — Late December 1805
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Cartagena! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✓ MUSTER — Soult (28,909) vs Paget (screening force) at Aragon — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 816) vs Paget (lost 3006) — A costly day for Paget: the losses ran two to one in Soult's favour, and Paget is still in the field. — The Line Holds +15% (Paget)
- CMD `Davout, attack Archduke Charles` → ✓ Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be told twice than bury them once."
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be told twice than bury them once."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (21,236; expect about 29,891 with the corps likely to arrive, up to 30,100 if all march) vs Archduke Charles (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Murat: marches under your written support order — but he is nursing a grievance and will bring NOTHING to the fighting — he will NOT make it in time
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack; the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Davout (21,236; expect about 29,891 with the corps likely to arrive, up to 30,100 if all march) vs Archduke Charles (substantial force) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 4466, own corps) vs Archduke Charles (lost 1488) — Napoleon marched to Davout's guns as ordered. It was not enough.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (149 lost to march) Captured: France → Austria · ArchdukeJohn marches from Provence into Lyonnais unopposed! (147 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (149 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Lyonnais unopposed! (147 lost to march) Captured: France → Austria
  - verbs: attack×2, wait×2, recruit×2, move×1
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "It is done. Point me at something that shoots back, Sire."
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1712) vs Mack (lost 9509) — The exchange went Murat's way, Sire — Mack paid twice what Murat did, though the day decided nothing yet.
  - POPUP capture_choice[capture]: Bohemia, Murat → secure
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
  - POPUP diplomatic_dialogue: Britain, armistice_losing #10 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 8939 · net +968 · threat 96 · provinces 30 (-1) · ceiling 16868 · army 119621 · vassals Holland 100 · Switzerland 98
  - NET income 2651 · trade 362 · admin 50 · tribute 337 · upkeep 1236 · charges 846 · occupation 260 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - TURN EVENTS 11
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG nation_eliminated: The Papal States has been eliminated from the war.

## Turn 8 — Early January 1806
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "Good. An army rots standing still."
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✗ Cannot attack Paget — armistice with Britain (5 turns remaining).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×3, wait×1
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #11 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +2 (98 → 100); bond -30 → -10 (-1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 10089 · net +647 · threat 94 · provinces 30 (+0) · ceiling 15250 · army 119621 · vassals Holland 100 · Switzerland 97
  - NET income 2773 · trade 362 · admin 50 · upkeep 1236 · charges 1012 · occupation 200 · admiralty 90
- DISPATCH: Sire — Lyonnais and Provence lie in enemy hands. Austria holds them.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Cagliari–Rome crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 7
- DIPLO +6 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, blockade_broken ×2, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 18 approaches rebuffed, chiefly from Britain and Naples (defensive alliance)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: 20 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✗ Cannot attack Paget — armistice with Britain (4 turns remaining).
- CMD `Soult, attack Wellesley` → ✗ Cannot attack Wellesley — armistice with Britain (4 turns remaining).
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 9 actions, 4 attacks — Britain, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov's assault collapses into chaos! Kutuzov gains the advantage over Murat. Casualties: Kutuzov 1,687, Murat's army… · Archduke John's forces press forward aggressively. Archduke John gains the advantage over Murat. Casualties: Archduke J… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Murat. Casualties: Archduke Charles… · Castanos strikes back after successfully defending!
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Castanos advances into Leon. (109 lost to march) Leon has been captured by Spain!
  - ⚔ Kutuzov (lost 1687) vs Murat (lost 2574, own corps) — Napoleon marched to Murat's guns as ordered. It was not enough.
  - ⚔ Archduke John (lost 1425) vs Murat (lost 2429) — Murat was close. A period of drilling could have changed the outcome. — The Hofkriegsrat's orders reached Archduke Charles too late.
  - ⚔ Archduke Charles (lost 519, own corps) vs Murat (lost 6351) — The toll on Murat's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Castanos (lost 154) vs Paget (lost 663) — The line gave way. Paget is falling back, and not in good order. — The Line Holds +15% (Paget)
  - verbs: attack×4, unfortify×2, move×1, form_square×1, wait×1
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "Done — and I trust the next order has more fire in it."
- ORDER Murat [awaiting_response]: Murat is cornered at Bohemia with 3,128 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Bohemia with 3,128 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 10194 · net +615 · threat 92 · provinces 30 (+0) · ceiling 14607 · army 104261 · vassals Holland 93 · Switzerland 90
  - NET income 2764 · trade 362 · admin 50 · upkeep 1116 · charges 1140 · occupation 215 · admiralty 90
- DISPATCH: Sire — Murat, crowned three turns ago, has been beaten in the field.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 6
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 10 — Early February 1806
  - MAILBOX #5 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #12 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Wellesley` → ✗ Cannot attack Wellesley — armistice with Britain (3 turns remaining).
- CMD `Soult, attack Paget` → ✗ Cannot attack Paget — armistice with Britain (3 turns remaining).
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Bohemia where he stands! Captured: France → Austria · Archduke John's forces press forward aggressively. Archduke John gains the advantage over Napoleon. Casualties: Archduk… · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles takes Bohemia where he stands! Captured: France → Austria
  - ⚔ Archduke John (lost 230) vs Napoleon (lost 2373) — Where was Ney? Napoleon held the field alone — reinforcement never came.
  - ⚔ Archduke John (lost 868) vs Deroy (lost 1276) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×3, move×1, break_square×1, fortify×1
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 10786 · net +582 · threat 90 · provinces 29 (-1) · ceiling 14811 · army 100946 · vassals Holland 90 · Switzerland 87
  - NET income 2762 · trade 362 · admin 50 · upkeep 1092 · charges 1268 · contributions 27 · occupation 115 · admiralty 90
- DISPATCH: Sire — Marshal Murat has been taken. Austria holds him prisoner.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Britain and Naples (defensive alliance)

## Turn 11 — Late February 1806
  - MAILBOX #6 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #13 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `Massena, attack Rome` → ✗ Rome is already controlled by France
- CMD `Soult, attack Wellesley` → ✗ Cannot attack Wellesley — armistice with Britain (2 turns remaining).
- CMD `Soult, attack Paget` → ✗ Cannot attack Paget — armistice with Britain (2 turns remaining).
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×3, move×1
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "Accomplished. The men want a battle, not another road."
- ENVOYS WAITING 2 · Hesse open borders · Britain settlement offer
- LEDGER treasury 11408 · net +502 · threat 88 · provinces 29 (+0) · ceiling 14804 · army 100946 · vassals Holland 89 · Switzerland 86
  - NET income 2775 · trade 362 · admin 50 · upkeep 1092 · charges 1388 · occupation 115 · admiralty 90
- DISPATCH: Sire — the war with Austria is over. Massena holds under your own orders and was not moved — the treaty offers a road, it does not overrule the Emperor. Their passage lapses with the corridor.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: 10 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
  - LETTER Hesse: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #16 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Portugal (8 pairs resolved). Status quo: Franconia and Swabia stay ours by the treaty — titled. Status quo: Lyonnais and Provence stay Austrian by the treaty. → display-only
- CMD `Massena, march to Rome` → ✓ Massena begins march to Rome. Massena: "We march. Pity whatever slows us."
- CMD `Soult, attack Wellesley` → ✗ We are not at war with Britain, Sire — Wellesley may not be attacked while the peace holds. Declare war on Britain first, or leave him be.
- CMD `Soult, attack Paget` → ✓ Choose your war purpose against Britain. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #17 → 1
  -     ↳ refused: The armistice with Britain holds for 5 more turns. We cannot declare war until it expires.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 13756 · net +2168 · threat 64 · provinces 29 (+0) · ceiling 173102 · army 110946 · vassals Holland 86 · Switzerland 83
  - NET income 2847 · trade 387 · admin 50 · upkeep 872 · charges 159 · occupation 85
- DISPATCH: Sire — under the peace with Britain. Massena is on the wrong side of the frontier at Rome, Sire — the ground changed hands under him. Berthier has put him on the road home to Savoy; he has 8 turns of…
  - RAIL status_quo_conceded: Lyonnais and Provence — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Portugal: settlement ratified.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 7
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: And Sardinia and Austria stir at their own designs.
- DIPLO +7 medium/low (diplomatic_treaty_signed, diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent ×2, blockade_broken)
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG ai_ai_proposal_refused: 2 approaches from Naples and Sardinia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: Naples rebuffs Austria (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 88 to 64.
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Britain and Naples (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Naples (defensive alliance)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

---
finished: **completed** · commands 58 · popups 36 · battles 18
