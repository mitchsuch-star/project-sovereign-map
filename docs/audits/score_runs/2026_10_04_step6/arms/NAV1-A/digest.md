# Playtest digest — NAV1-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "decline_from": "Britain,Portugal,PapalStates,Naples"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `d10182082767` (dirty) · content `1ecab161811e` · driver `fe441ad83bb4`
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
- CMD `Massena, take Rome` → ✓ Massena begins march to Rome. Route: Piedmont → Rome. Moves to Piedmont. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `Soult, take Lisbon` → ✓ Soult begins march to Lisbon. Route: Orleanais → Burgundy → Limousin → Gascony → Bearn → Cartagena → Andalusia → Lisbon. Moves to Orleanais. "Soult, take Lisbon." No mor…
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 85,373 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2621, own corps) vs Mack (lost 14380) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Murat and Bernadotte never arrived, S… — Berthier: the corps marched apart and arrived together.
  - saved `NAV1-A_t1` → Game saved: NAV1-A_t1
- CMD `end turn` → ✓ Turn 1 ended. Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a devastating assault! Archduke Charles gains the advantage over Bernadotte. Casualties: Arch…
  - ⚔ Archduke Charles (lost 2461) vs Bernadotte (lost 5419, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
- ORDER Massena [active]: Massena is marching to Rome (1 turn remaining).
- ORDER Soult [active]: Soult is marching to Lisbon (7 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 1741 · net +1634 · threat 97 · provinces 28 · ceiling 35760 · army 168705 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 1984 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,419 men — lost in a single action.
  - RAIL diplomatic_war_declared: France has declared war on Portugal, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: France has declared war on PapalStates, with 2 allied courts poised to follow.
  - TURN EVENTS 5
- DIPLO +9 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 2 — Early October 1805
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,137; expect about 74,324 with the corps likely to arrive, up to 84,446 if all march) vs Mack (substantial force) at Munich — the balance of force loo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1117, own corps) vs Mack (lost 11299) — Reinforcements from Ney, Lannes, Napoleon and Teulie bolstered Davout's position — though Murat never arrived, Sire. — Berthier: the corps marched apart and arrived together.
- CMD `Murat, attack Mack` → ✓ MUSTER — Murat (22,000; expect about 23,427 with the corps likely to arrive, up to 30,089 if all march) vs Mack (substantial force) at Tyrol — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 4050) vs Archduke John (lost 2773) — Murat stood alone, Sire. Davout never came.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,651; expect about 33,117 with the corps likely to arrive, up to 37,875 if all march) vs Mack (24,210 men) at Tyrol — the balance of force looks even — a…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1780, own corps) vs Archduke John (lost 3802) — Davout arrived in time to steady Ney's position. The field was held, nothing further. — The corps system brought Davout in.
- CMD `Massena, take Rome` → ✓ ASSAULT — Massena storms the works at Rome alone: 39,293 men, 45,186 in the assault's reckoning, against a garrison of 10,000. the garrison breaks below 5,000.
  - ↳ Massena assaults the Rome garrison! Garrison: 10,000 -> 5,000 (-5,000). Massena loses 2,173 troops. Garrison holds — 5,000 defenders remain. It regains up to 2,000 a tur…
  - saved `NAV1-A_t2` → Game saved: NAV1-A_t2
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's attack falters disastrously! Archduke Charles gains the advantage over Bernadotte. Casualties: Archd… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Murat. Casualties: Archduke…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,404 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 748) vs Bernadotte (lost 6200) — A grievous defeat for Bernadotte, Sire. The losses are severe. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 1526) vs Deroy (lost 8049) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 1999) vs Murat (lost 5149, own corps) — Amey marched to Murat's guns as ordered. It was not enough. — The corps system brought Amey in.
  - verbs: attack×3, fortify×1
- ORDER Soult [continues]: Soult marches to Burgundy. 6 regions to Lisbon.
- LEDGER treasury 2948 · net +2324 · threat 97 · provinces 28 (+0) · ceiling 26277 · army 140347 · vassals Holland 97 · Kingdom of Italy 96 · Switzerland 93
  - NET income 2575 · trade 350 · admin 50 · tribute 937 · upkeep 1120 · charges 94 · contributions 65 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 14 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 4 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Britain and Russia rebuff Prussia (open borders agreement)

## Turn 3 — Late October 1805
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (14,919; expect about 59,055 with the corps likely to arrive, up to 70,564 if all march) vs Mack (23,876 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 538, own corps) vs Mack (lost 15458, own corps) — Davout, Lannes, Napoleon and Teulie arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. — The corps system brought Teulie in.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (18,096; expect about 27,067 with the corps likely to arrive) vs Mack (strength unknown) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 120, own corps) vs Mack (lost 6305) — Ney arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire.
- CMD `Massena, take Rome` → ✓ ASSAULT — Massena storms the works at Rome alone: 36,988 men, 42,536 in the assault's reckoning, against a garrison of 7,000. the garrison breaks below 5,000.
  - ↳ Massena assaults the Rome garrison! Garrison collapses (7,000 -> 0). Massena loses 1,521 troops in the assault. Massena marches into Rome! (1,064 lost to march)
  - POPUP capture_choice[capture]: Rome, Massena → secure
- CMD `Lannes, march to Normandy` → ✗ Not enough actions! Need 2, have 1.
  - saved `NAV1-A_t3` → Game saved: NAV1-A_t3
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Murat. Casualties: Archduke…
  - ⚔ Archduke Charles (lost 747) vs Murat (lost 10421) — Where was Amey? Murat held the field alone — reinforcement never came.
  - verbs: attack×1, wait×1
- ORDER Soult [continues]: Soult marches to Limousin. 5 regions to Lisbon.
- ORDER Murat [awaiting_response]: Murat is cornered at Franche-Comte with 2,244 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Franche-Comte with 2,244 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
- LEDGER treasury 4796 · net +2272 · threat 97 · provinces 30 (+2) · ceiling 25007 · army 122300 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 92
  - NET income 2651 · trade 375 · admin 50 · tribute 937 · upkeep 944 · charges 314 · contributions 51 · requisitions 50 · occupation 157 · blockade 235 · admiralty 90
- DISPATCH: Sire — Papal States is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Sire — the Papal States has been eliminated from the war.
  - TURN EVENTS 9
- DIPLO +4 medium/low (diplomatic_we_threshold ×2, diplomatic_dp_regen, cs_tier_shift)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Naples and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 5 approaches from Austria, Prussia and Naples are rebuffed (defensive alliance)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia, Naples and Spain are rebuffed (open borders agreement)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Naples and Russia (Open Borders Agreement)

## Turn 4 — Early November 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is engaged with Archduke John and cannot begin a strategic march. Deal with the engagement first.
- CMD `Davout, attack Archduke Charles` → ✗ Davout is engaged with Archduke John and cannot begin a strategic march. Deal with the engagement first.
- CMD `Massena, take Rome` → ✓ Massena begins march to Rome. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `Murat, attack Mack` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
  - saved `NAV1-A_t4` → Game saved: NAV1-A_t4
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franche-Comte where he stands! Captured: France → Austria · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduk…
  - 🏴 Austria: ArchdukeCharles takes Franche-Comte where he stands! Captured: France → Austria
  - ⚔ Archduke Charles (lost 1637) vs Bernadotte (lost 1440, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - verbs: attack×2
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
- ORDER Soult [continues]: Soult marches to Gascony. 4 regions to Lisbon.
- LEDGER treasury 6868 · net +2034 · threat 95 · provinces 29 (-1) · ceiling 23760 · army 117746 · vassals Holland 96 · Kingdom of Italy 93 · Switzerland 88
  - NET income 2602 · trade 375 · admin 50 · tribute 937 · upkeep 912 · charges 586 · requisitions 50 · occupation 157 · blockade 235 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of 40,042 stands there. A garrison you detach (3,000 men) holds a province against a …
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 9 approaches from Ottoman Empire, Sweden and Naples are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Naples (open borders agreement)
  - LOG ai_ai_proposal_refused: 4 approaches from Austria, Prussia and Naples are rebuffed (defensive alliance)
  - LOG nation_eliminated: The Papal States has been eliminated from the war.
  - LOG ai_ai_proposal_refused: 2 approaches from Naples and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ Ney pursues Archduke Charles (at Franche-Comte). Moves to Franconia. The province is secured. A standing order, not a single attack: he closes 1 province a turn, attacks…
- CMD `Murat, attack Archduke John` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, take Rome` → ✓ Massena is already carrying out that order. No change.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
  - saved `NAV1-A_t5` → Game saved: NAV1-A_t5
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces strike with perfect coordination! Archduke Charles gains the advantage over Lannes. Casualtie…
  - ⚔ Archduke Charles (lost 2698) vs Lannes (lost 1539, own corps) — Reinforcements from Davout bolstered Lannes's position — though Ney never arrived, Sire.
  - verbs: attack×1
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "Accomplished. The men want a battle, not another road."
- ORDER Ney [active]: Ney is pursuing Archduke Charles (0 turns remaining).
- ORDER Soult [continues]: Soult marches to Bearn. 3 regions to Lisbon.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 8857 · net +1907 · threat 95 · provinces 30 (+1) · ceiling 23847 · army 113137 · vassals Holland 94 · Kingdom of Italy 90 · Switzerland 84
  - NET income 2768 · trade 337 · admin 50 · tribute 937 · upkeep 880 · charges 872 · requisitions 50 · occupation 182 · blockade 211 · admiralty 90
- DISPATCH: Sire — Franche-Comte lies in enemy hands. Austria holds it.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 18 approaches rebuffed, chiefly from Prussia and Naples (defensive alliance)

## Turn 6 — Early December 1805
  - MAILBOX #1 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #7 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +10 (90 → 100); bond -30 → -10 (-1 a turn). Cost: 1 DP. Our net rises by 45g a turn — 25g of income forfeited, 52g of occupation relieved, 18g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Davout, attack Archduke Charles` → ✓ Davout notes the risks but prepares the attack. Davout halts before the order is carried out. "I will go if you order it, Sire — but look at the ground first. This is no…
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I will go if you order it, Sire — but look at the ground first. This is not a battle, it is an arithmetic problem."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (16,293; expect about 24,034 with the corps likely to arrive, up to 25,807 if all march) vs Archduke Charles (substantial force) at Carniola — the balance of force looks unfavorable.
  WILL NOT — Lannes: is dug in and will not abandon his works
  WILL NOT — Bernadotte: is in no condition to fight
  WILL JOIN — Napoleon: is willing to march if the roads allow — likely to make it in time (about 98%) (The corps system lowers the bar by 10)
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 76%); order 'Teulie, support Davout' and it rises to about 100% (The corps system lowers the bar by 10)
  The Emperor commands in person — every corps on this field fights +10% harder, if he marches.
  The band weighs more than the men: all told, Davout's own modifiers weigh 10% against the attack; the ground favors the defender (+15%, hills).
  What Carniola can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Davout (16,293; expect about 24,034 with the corps likely to arrive, up to 25,807 if all march) vs Archduke Charles (substantial force) at Carniola — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 2892, own corps) vs Archduke Charles (lost 1489) — Napoleon and Teulie marched to Davout's guns as ordered. It was not enough.
- CMD `Ney, attack Archduke John` → ✓ Ney pursues Archduke John (at Vienna). Moves to Bohemia. The province is secured. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival,…
- CMD `Massena, take Rome` → ✗ Not enough actions! Need 2, have 1.
- CMD `Bernadotte, attack Archduke Charles` → ✗ Bernadotte is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
  - saved `NAV1-A_t6` → Game saved: NAV1-A_t6
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Ney [active]: Ney is pursuing Archduke John (0 turns remaining).
- ORDER Soult [continues]: Soult marches to Cartagena. 2 regions to Lisbon.
- ORDER Teulie [retired]: Teulie's question is overtaken, Sire — Teulie has marched clear of Carniola. He awaits new orders.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10575 · net +1655 · threat 95 · provinces 30 (+0) · ceiling 22885 · army 107779 · vassals Holland 92 · Kingdom of Italy 98 · Switzerland 80
  - NET income 2797 · trade 337 · admin 50 · tribute 956 · upkeep 832 · charges 1152 · occupation 200 · blockade 211 · admiralty 90
- DISPATCH: Sire — Napoleon's corps has been broken at Carniola. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,212g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 8
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_we_threshold, enemy_marshal_commissioned, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 8 approaches to Britain and Russia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: PapalStates rebuffs Britain (defensive alliance)

## Turn 7 — Late December 1805
  - MAILBOX #2 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #8 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond -30 → -10 (-1 a turn). Cost: 1 DP. → display-only
- CMD `Massena, take Rome` → ✓ Massena begins march to Rome. Massena: "At the double, Sire — the men will smell powder soon enough."
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Cartagena! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✓ MUSTER — Soult (28,909) vs Paget (screening force) at Aragon — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 781) vs Paget (lost 3211) — An exemplary engagement by Soult. The outcome was never in doubt. And Paget was taken on that field — France holds him. — The Line Holds +15% (Paget)
- CMD `Davout, attack Archduke John` → ✓ Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be told twice than bury them once."
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "Before I commit the corps: the odds are against us, and I would rather be told twice than bury them once."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (13,401; expect about 22,181 with the corps likely to arrive, up to 22,530 if all march) vs Archduke John (small force) at Vienna — the balance of force looks unfavorable.
  WILL JOIN — Ney: marches under your written support order — likely to make it in time (about 96%) (The corps system lowers the bar by 10)
  Archduke John does not stand alone: at least 1 enemy corps within reach of Vienna would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  What Vienna can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Davout (13,401; expect about 22,181 with the corps likely to arrive, up to 22,530 if all march) vs Archduke John (small force) at Vienna — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 2402, own corps) vs Archduke John (lost 414, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - saved `NAV1-A_t7` → Game saved: NAV1-A_t7
- CMD `end turn` → ✓ Turn 7 ended. Turn 8 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Lannes. Casualties: Archduke C…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Bohemia. (717 lost to march) Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 295) vs Ney (lost 6229, own corps) — Teulie's timely arrival aided Ney. Bernadotte, however, was conspicuously absent. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 760) vs Lannes (lost 2831, own corps) — Lannes's fortified position was overwhelmed. A costly investment lost, Sire.
  - verbs: attack×2, unfortify×1, move×1
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 11327 · net +1309 · threat 96 · provinces 29 (-1) · ceiling 19934 · army 90508 · vassals Holland 87 · Kingdom of Italy 93 · Switzerland 84
  - NET income 2754 · trade 337 · admin 50 · tribute 712 · upkeep 696 · charges 1417 · occupation 130 · blockade 211 · admiralty 90
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - TURN EVENTS 13
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 8 — Early January 1806
  - MAILBOX #3 Britain incoming_proposal: Britain — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #9 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
- CMD `declare war on Naples` → ✓ Choose your war purpose against Naples.
  - POPUP diplomatic_dialogue: war_purpose_selection #10 → 1
  - POPUP diplomatic_objection: diplomatic_declare_war, Naples → proceed
  - POPUP diplomatic_dialogue: proposal_confirm #11 → ally_entry_proceed_without
- CMD `Massena, take Naples` → ✓ MUSTER — Massena (34,403) vs Damas (substantial force) at Naples — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 2286) vs Damas (lost 3636) — Massena broke through fortified positions — extraordinary courage from the men.
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
  - saved `NAV1-A_t8` → Game saved: NAV1-A_t8
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 7 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Mack gains the advantage over Ney. Casualties: Mack 817, Ney's army 2,357. Both armies …
  - ⚔ Mack (lost 817) vs Ney (lost 1366, own corps) — Ney held superior ground, yet Mack prevailed. A grim day, Sire. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: move×2, retreat×1, stance_change×1, attack×1, unfortify×1, wait×1
- ORDER Ney [awaiting_response]: Ney is cornered at Tyrol with 3,976 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Tyrol with 3,976 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: shadow_command, Marshal Lannes asks for a command → detach
  -     ↳ Lannes straightens. "You will not regret it, Sire." March him to Franconia and the front is his — the order i…
  -     ↳ audience: No marshal waits upon you, Sire.
- LEDGER treasury 12573 · net +1238 · threat 97 · provinces 29 (+0) · ceiling 20383 · army 80072 · vassals Holland 87 · Kingdom of Italy 96 · Switzerland 83
  - NET income 2830 · trade 337 · admin 50 · tribute 712 · upkeep 616 · charges 1674 · occupation 100 · blockade 211 · admiralty 90
- DISPATCH: Sire — Napoleon's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL diplomatic_war_declared: France has declared war on Naples, with 1 allied court poised to follow.
  - TURN EVENTS 10
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Naples are rebuffed (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 9 — Late January 1806
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Massena, take Naples` → ✓ MUSTER — Massena (32,117) vs Damas (14,364 men) at Naples — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 1890) vs Damas (lost 3502) — The engagement proceeded as one might expect, Sire.
  - saved `NAV1-A_t9` → Game saved: NAV1-A_t9
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack launches a decisive assault. Mack gains the advantage over Davout. Casualties: Mack 966, Davout 1,819. Both armies… · ArchdukeJohn marches from Bohemia into Franconia unopposed! (76 lost to march) Captured: France → Austria · Mack's forces advance steadily. Mack gains the advantage over Lannes. Casualties: Mack 405, Lannes 2,208. Both armies r… · Damas's forces advance steadily. Massena holds the line. Casualties: Damas 4,751, Massena 804. Both armies remain in th…
  - 🏴 Austria: [!] Davout's troops are BROKEN (morale 0%)! FORCED RETREAT! Tyrol has been captured by Austria!
  - 🏴 Austria: ArchdukeJohn marches from Bohemia into Franconia unopposed! (76 lost to march) Captured: France → Austria
  - 🏴 Naples: [!] MARSHAL CAPTURED — Damas is taken by France at Naples!
  - ⚔ Mack (lost 966) vs Davout (lost 1819) — Davout held superior ground, yet Mack prevailed. A grim day, Sire.
  - ⚔ Mack (lost 405) vs Lannes (lost 2208) — The walls were not enough. Mack broke through Lannes's prepared defenses.
  - ⚔ Damas (lost 4751) vs Massena (lost 804) — Complete dominance on the field. Damas crumbled before Massena. And Damas was taken on that field — France holds him.
  - verbs: attack×4
- ORDER Lannes [awaiting_response]: Lannes is cornered at Milan with 3,574 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Milan with 3,574 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13834 · net +1368 · threat 97 · provinces 28 (-1) · ceiling 23862 · army 69190 · vassals Holland 86 · Kingdom of Italy 98 · Switzerland 81
  - NET income 2768 · trade 337 · admin 50 · tribute 694 · upkeep 536 · charges 1614 · occupation 30 · blockade 211 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 13
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Prussia (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #4 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → reject_settlement_offer
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Massena, take Naples` → ✓ ASSAULT — Massena storms the works at Naples alone: 29,423 men, 33,836 in the assault's reckoning, against a garrison of 15,000. the garrison breaks below 5,000.
  - ↳ Massena assaults the Naples garrison! Garrison: 15,000 -> 7,500 (-7,500). Massena loses 3,260 troops. Garrison holds — 7,500 defenders remain. It regains up to 2,000 a t…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `NAV1-A_t10` → Game saved: NAV1-A_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #13 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 15066 · net +1159 · threat 95 · provinces 28 (+0) · ceiling 23176 · army 65538 · vassals Holland 85 · Kingdom of Italy 100 · Switzerland 79
  - NET income 2774 · trade 337 · admin 50 · tribute 698 · upkeep 504 · charges 1865 · occupation 30 · blockade 211 · admiralty 90
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 10
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Naples and Portugal rebuff Austria (defensive alliance)

## Turn 11 — Late February 1806
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Shrapnel` → ✗ No intelligence on Shrapnel's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Massena, take Naples` → ✓ ASSAULT — Massena storms the works at Naples alone: 26,163 men, 30,087 in the assault's reckoning, against a garrison of 9,500. the garrison breaks below 5,000.
  - ↳ Massena assaults the Naples garrison! Garrison collapses (9,500 -> 0). Massena loses 2,065 troops in the assault. Massena marches into Naples! (438 lost to march)
  - POPUP capture_choice[capture]: Naples, Massena → secure
  - saved `NAV1-A_t11` → Game saved: NAV1-A_t11
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 15782 · net +637 · threat 97 · provinces 29 (+1) · ceiling 19488 · army 62655 · vassals Holland 85 · Kingdom of Italy 100 · Switzerland 78
  - NET income 2823 · trade 349 · admin 50 · tribute 703 · upkeep 480 · charges 2364 · occupation 135 · blockade 219 · admiralty 90
- DISPATCH: Sire — Naples is knocked out of the war. No army remains beneath their colours.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL nation_eliminated: Sire — Naples has been eliminated from the war.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,351 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 12 — Early March 1806
  - MAILBOX #6 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (85 → 95); bond -45 → -25 (-2 a turn). Cost: 1 DP. → display-only
- CMD `Soult, attack Lisbon` → ✗ Soult cannot reach Lisbon from Aragon! Range: 1, Distance: 2
- CMD `Soult, attack Shrapnel` → ✗ No intelligence on Shrapnel's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Massena, take Naples` → ✓ Massena begins march to Naples. Massena: "Good. An army rots standing still."
  - saved `NAV1-A_t12` → Game saved: NAV1-A_t12
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, forced_march×1
- ORDER Massena [active]: Massena is marching to Naples (0 turns remaining).
- LEDGER treasury 16075 · net +197 · threat 94 · provinces 29 (+0) · ceiling 17200 · army 62286 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 76
  - NET income 2831 · trade 299 · admin 50 · tribute 370 · upkeep 480 · charges 2460 · occupation 135 · blockade 188 · admiralty 90
- DISPATCH: Sire — Marshal Soult's household goes unpaid. His patience erodes with his purse.
  - TURN EVENTS 8
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade ×2, paymaster_subsidy, agenda_shift ×2, diplomatic_relation_shift)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG nation_eliminated: Naples has been eliminated from the war.

## Turn 13 — Late March 1806
- CMD `Soult, attack Shrapnel` → ✗ No intelligence on Shrapnel's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ No intelligence on Wellesley's position, Sire. Scout for him before Soult can give chase.
- CMD `Massena, take Rome` → ✓ Massena begins march to Rome. Moves to Rome. Massena: "At the double, Sire — the men will smell powder soon enough."
  - saved `NAV1-A_t13` → Game saved: NAV1-A_t13
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Prussia, Spain and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 2,314 troops in th…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -115g, Bavaria -175g. Captured: Bavaria → Austria
  - verbs: move×1, attack×1
- ORDER Massena [active]: Massena is marching to Rome (0 turns remaining).
- LEDGER treasury 16257 · net +105 · threat 91 · provinces 29 (+0) · ceiling 16842 · army 61662 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 74
  - NET income 2838 · trade 224 · admin 50 · tribute 375 · upkeep 480 · charges 2537 · occupation 135 · blockade 140 · admiralty 90
- DISPATCH: Sire — the enemy has held Franche-Comte 9 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 200g reaches Russia

## Turn 14 — Early April 1806
- CMD `Soult, attack Shrapnel` → ✗ No intelligence on Shrapnel's position, Sire. Scout for him before Soult can give chase.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✓ MUSTER — Soult (26,385) vs Wellesley (4,257 men) at Madrid — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 493) vs Wellesley (lost 1581) — Complete dominance on the field. Wellesley crumbled before Soult. — The Line Holds +15% (Wellesley)
- CMD `Soult, take Porto` → ✓ Soult begins march to Porto. Route: Leon → Lisbon → Porto. Moves to Leon. "Soult, take Porto." No more and no less. (1 AP — Soult executes precise orders with fewer cour…
  - saved `NAV1-A_t14` → Game saved: NAV1-A_t14
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: 7 actions, 2 attacks — Russia, Austria, Prussia and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos faces a difficult fight. Castanos gains the advantage over Shrapnel. Casualties: Castanos 421, Shrapnel 957. B… · Castanos's forces advance steadily. Castanos gains the advantage over Wellesley. Casualties: Castanos 243, Wellesley 54…
  - 🏴 Spain: [!] MARSHAL CAPTURED — Wellesley is taken by Spain at Madrid!
  - ⚔ Castanos (lost 421) vs Shrapnel (lost 957) — Shrapnel's fortified position was overwhelmed. A costly investment lost, Sire. — The Line Holds +15% (Shrapnel)
  - ⚔ Castanos (lost 243) vs Wellesley (lost 541) — Even Wellesley's fortifications could not hold, Sire. Castanos overran the position. And Wellesley was taken on that fi… — The Line Holds +15% (Wellesley)
  - verbs: fortify×3, attack×2, move×1, naval_expedition×1
- ORDER Massena [completed]: Massena arrives at Rome. Massena: "Accomplished. The men want a battle, not another road."
- ORDER Soult [active]: Soult is marching to Porto (2 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Britain, armistice_losing #16 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 16934 · net +774 · threat 91 · provinces 29 (+0) · ceiling 22052 · army 60257 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 73
  - NET income 2942 · trade 224 · admin 50 · tribute 600 · upkeep 464 · charges 2258 · occupation 90 · blockade 140 · admiralty 90
- DISPATCH: Sire — 7 turns without settlement on Marshal Soult. A rente would close it today; the arrears will not close themselves.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 15 — Late April 1806
- CMD `Soult, attack Shrapnel` → ✓ MUSTER — Soult (25,328) vs Shrapnel (2,043 men) at Lisbon — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 196) vs Shrapnel (lost 984) — Soult stormed the enemy fortifications! A feat of arms, Sire. And Shrapnel was taken on that field — France holds him. — The Line Holds +15% (Shrapnel)
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ Wellesley is a prisoner of Spain at Madrid, Sire — he leads no army.
- CMD `Soult, attack Porto` → ✗ Soult cannot reach Porto from Leon! Range: 1, Distance: 2
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `NAV1-A_t15` → Game saved: NAV1-A_t15
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_audience: shadow_command, Marshal Davout asks for a command → detach
  -     ↳ Davout straightens. "You will not regret it, Sire." March him to Normandy and the front is his — the order is…
  - POPUP diplomatic_dialogue: Russia, armistice_losing #17 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
  - POPUP diplomatic_dialogue: Portugal, armistice_losing #18 → reject
  - POPUP proposal_result: You have rejected Portugal's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #19 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (72 → 82); bond -25 → -5 (-1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 3 · Russia armistice losing · Portugal armistice losing · Switzerland client petition
- LEDGER treasury 17713 · net +393 · threat 91 · provinces 29 (+0) · ceiling 20249 · army 59725 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 82
  - NET income 2952 · trade 224 · admin 50 · tribute 375 · upkeep 456 · charges 2432 · occupation 90 · blockade 140 · admiralty 90
- DISPATCH: Sire — General Shrapnel of Britain is taken at Lisbon — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 7
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, cs_tier_shift, blockade_broken)
  - LOG ai_ai_proposal_refused: Portugal rebuffs Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Portugal's armistice proposal

## Turn 16 — Early May 1806
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✓ Soult pursues Wellesley (at Madrid). Moves to Aragon. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an inter…
- CMD `Soult, take Alentejo` → ✓ Soult begins march to Alentejo. Route: Beira → Andalusia → Alentejo. Moves to Beira. The province is secured. "Soult, take Alentejo." It will be done exactly, Sire. (1 A…
  - saved `NAV1-A_t16` → Game saved: NAV1-A_t16
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 2 actions unused) Turn 17 begins!
- enemy phase: 6 actions, 4 attacks — Russia, Prussia, Spain and 3 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Davout. Casualties: Archduke C… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc… · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,054 (-4,946). ArchdukeCharles loses 3,404 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,054 -> 0). ArchdukeCharles loses 1,966 troops in the…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Davout is taken by Austria at Milan!
  - 🏴 Austria: [!] No word came for Teulie, cornered at Milan — the enemy did not wait. [!] MARSHAL CAPTURED — Teulie is taken by Austria at Milan!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -98g, Kingdom of Italy -126g. Captured: KingdomOfItaly → Austria
  - ⚔ Archduke Charles (lost 399) vs Davout (lost 2082, own corps) — The toll on Davout's forces is heavy, Sire. This defeat will be felt. And Davout was taken on that field — Austria hold…
  - ⚔ Archduke Charles (lost 89) vs Bernadotte (lost 879, own corps) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: attack×4, drill×1, naval_expedition×1
- ORDER Soult [active]: Soult is marching to Alentejo (2 turns remaining).
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 17257 · net -224 · threat 90 · provinces 30 (+1) · ceiling 16071 · army 49601 · vassals Holland 93 · Kingdom of Italy 88 · Switzerland 77
  - NET income 3000 · trade 224 · admin 50 · tribute 150 · upkeep 384 · charges 2892 · occupation 142 · blockade 140 · admiralty 90
- DISPATCH: Sire — Marshal Davout has been taken. Austria holds him prisoner.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 17 — Late May 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #20 → reject_settlement_offer
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✓ MUSTER — Soult (23,675) vs Wellesley (5,000 men) at Lisbon — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 411) vs Wellesley (lost 2970) — An exemplary engagement by Soult. The outcome was never in doubt. And Wellesley was taken on that field — France holds … — The Line Holds +15% (Wellesley)
- CMD `Soult, attack Alentejo` → ✗ Soult cannot reach Alentejo from Beira! Range: 1, Distance: 2
  - saved `NAV1-A_t17` → Game saved: NAV1-A_t17
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 3 actions unused) Turn 18 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc… · ArchdukeCharles holds them at Piedmont while allies attack from Milan! (+1 coordination)
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Piedmont!
  - ⚔ Archduke Charles (lost 921) vs Bernadotte (lost 183, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless. And Bernadotte was taken on that …
  - ⚔ Archduke Charles (lost 49) vs Napoleon (lost 513) — Napoleon's corps broke, Sire. They are streaming back from the field.
  - verbs: attack×2
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Piedmont — 691 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Piedmont — 691 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 16799 · net -573 · threat 90 · provinces 30 (+0) · ceiling 14077 · army 45700 · vassals Holland 90 · Kingdom of Italy 85 · Switzerland 73
  - NET income 3004 · trade 224 · admin 50 · upkeep 360 · charges 3119 · occupation 142 · blockade 140 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - TURN EVENTS 9
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 18 — Early June 1806
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ Wellesley is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Moore` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `NAV1-A_t18` → Game saved: NAV1-A_t18
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Piedmont where he stands! Captured: KingdomOfItaly → Austria
  - 🏴 Austria: ArchdukeCharles takes Piedmont where he stands! Captured: KingdomOfItaly → Austria
  - verbs: move×3, attack×1, unfortify×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 2507) vs Archduke Charles (lost 1154) — Geography was our enemy today, Sire. Archduke Charles held the superior ground.
- LEDGER treasury 16674 · net +0 · threat 77 · provinces 30 (+0) · ceiling 16671 · army 43193 · vassals Holland 86 · Switzerland 68
  - NET income 3084 · trade 236 · admin 50 · upkeep 336 · charges 2676 · occupation 120 · blockade 148 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (balance_of_europe_shifted, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 33% of active European bloc power.

## Turn 19 — Late June 1806
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ Wellesley is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Moore` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
  - saved `NAV1-A_t19` → Game saved: NAV1-A_t19
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (101 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (101 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn moves from Provence to Lyonnais. Lyonnais falls to Austria!
  - verbs: attack×1, move×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 16094 · net -120 · threat 74 · provinces 28 (-2) · ceiling 15526 · army 43193 · vassals Holland 84 · Switzerland 65
  - NET income 2914 · trade 236 · admin 50 · tribute 337 · upkeep 336 · charges 2993 · occupation 90 · blockade 148 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 20 — Early July 1806
  - MAILBOX #12 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #21 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ Wellesley is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Moore` → ✗ No intelligence on Moore's position, Sire. Scout for him before Lannes can give chase.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `NAV1-A_t20` → Game saved: NAV1-A_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ORDER Massena [continues]: Massena marches to Piedmont. 1 region to Savoy.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (82 → 86); bond -25 → -5 (-1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14714 · net +635 · threat 72 · provinces 28 (+0) · ceiling 19492 · army 75695 · vassals Holland 86 · Switzerland 62
  - NET income 2920 · trade 248 · admin 50 · upkeep 560 · charges 1688 · occupation 90 · blockade 155 · admiralty 90
- DISPATCH: Sire — the Emperor's star is out. The Presence that gave his corps +10% on the field gives nothing this morning — Europe has learned that Napoleon can be beaten.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 21 — Late July 1806
  - saved `NAV1-A_t21` → Game saved: NAV1-A_t21
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [completed]: Massena arrives at Savoy. Massena: "It is done. Point me at something that shoots back, Sire."
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  - POPUP diplomatic_dialogue: Britain, armistice_losing #23 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 15408 · net +602 · threat 70 · provinces 28 (+0) · ceiling 19936 · army 73721 · vassals Holland 85 · Switzerland 59
  - NET income 2964 · trade 248 · admin 50 · upkeep 560 · charges 1780 · occupation 75 · blockade 155 · admiralty 90
- DISPATCH: Sire — Franche-Comte, Lyonnais and Provence lie in enemy hands. Austria holds them.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +7 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal

## Turn 22 — Early August 1806
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ Wellesley is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Moore` → ✗ No intelligence on Moore's position, Sire. Scout for him before Lannes can give chase.
  - saved `NAV1-A_t22` → Game saved: NAV1-A_t22
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Portugal, armistice_losing #24 → reject
  - POPUP proposal_result: You have rejected Portugal's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Portugal armistice losing
- LEDGER treasury 16016 · net +527 · threat 68 · provinces 28 (+0) · ceiling 19981 · army 71866 · vassals Holland 84 · Switzerland 56
  - NET income 2970 · trade 248 · admin 50 · upkeep 560 · charges 1861 · occupation 75 · blockade 155 · admiralty 90
- DISPATCH: Sire — Marshal Soult's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Portugal's armistice proposal

## Turn 23 — Late August 1806
  - saved `NAV1-A_t23` → Game saved: NAV1-A_t23
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 16605 · net +736 · threat 66 · provinces 28 (+0) · ceiling 22143 · army 70123 · vassals Holland 83 · Switzerland 53
  - NET income 2976 · trade 248 · admin 50 · tribute 225 · upkeep 504 · charges 1939 · occupation 75 · blockade 155 · admiralty 90
- DISPATCH: Sire — Marshal Soult's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 24 — Early September 1806
  - MAILBOX #16 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #25 → reject_settlement_offer
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ Wellesley is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Moore` → ✗ No intelligence on Moore's position, Sire. Scout for him before Lannes can give chase.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `NAV1-A_t24` → Game saved: NAV1-A_t24
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17347 · net +643 · threat 64 · provinces 28 (+0) · ceiling 22188 · army 68485 · vassals Holland 82 · Switzerland 50
  - NET income 2982 · trade 248 · admin 50 · tribute 225 · upkeep 504 · charges 2038 · occupation 75 · blockade 155 · admiralty 90
- DISPATCH: Sire — the enemy has held Franche-Comte, Lyonnais and Provence 5 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 25 — Late September 1806
  - saved `NAV1-A_t25` → Game saved: NAV1-A_t25
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Denmark open borders
- LEDGER treasury 17996 · net +563 · threat 62 · provinces 28 (+0) · ceiling 22233 · army 66945 · vassals Holland 81 · Switzerland 42
  - NET income 2988 · trade 248 · admin 50 · tribute 225 · upkeep 504 · charges 2124 · occupation 75 · blockade 155 · admiralty 90
- DISPATCH: Sire — Marshal Soult's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +5 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 26 — Early October 1806
  - LETTER Denmark: Open Borders Agreement → accept
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ Wellesley is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Moore` → ✗ No intelligence on Moore's position, Sire. Scout for him before Lannes can give chase.
  - saved `NAV1-A_t26` → Game saved: NAV1-A_t26
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Hesse open borders
- LEDGER treasury 18359 · net +315 · threat 50 · provinces 28 (+0) · ceiling 20727 · army 65496 · vassals Holland 80
  - NET income 2994 · trade 298 · admin 50 · upkeep 504 · charges 2172 · occupation 75 · blockade 186 · admiralty 90
- DISPATCH: Sire — Switzerland is no longer ours. Russia is their protector now.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_vassal_transferred: Switzerland passes from France's suzerainty to Russia's.
  - RAIL diplomatic_vassal_defected: THE DEFECTION: Russia's gold turns Switzerland against France.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +5 medium/low (diplomatic_treaty_signed, diplomatic_vassal_courting, diplomatic_vassal_contingent, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 27 — Late October 1806
  - LETTER Hesse: Open Borders Agreement → accept
  - saved `NAV1-A_t27` → Game saved: NAV1-A_t27
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18823 · net +272 · threat 48 · provinces 28 (+0) · ceiling 20870 · army 64138 · vassals Holland 79
  - NET income 3000 · trade 335 · admin 50 · upkeep 504 · charges 2234 · occupation 75 · blockade 210 · admiralty 90
- DISPATCH: Sire — Marshal Soult's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)

## Turn 28 — Early November 1806
- CMD `Soult, attack Shrapnel` → ✗ Shrapnel is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Paget` → ✗ Paget is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, attack Wellesley` → ✗ Wellesley is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Moore` → ✗ No intelligence on Moore's position, Sire. Scout for him before Lannes can give chase.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `NAV1-A_t28` → Game saved: NAV1-A_t28
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 19157 · net +627 · threat 46 · provinces 28 (+0) · ceiling 23875 · army 62864 · vassals Holland 78
  - NET income 3006 · trade 335 · admin 50 · tribute 337 · upkeep 448 · charges 2278 · occupation 75 · blockade 210 · admiralty 90
- DISPATCH: Sire — Marshal Soult's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - TURN EVENTS 1
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 29 — Late November 1806
  - MAILBOX #19 Britain incoming_proposal: Britain — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #28 → reject
  - POPUP proposal_result: You have rejected Britain's proposal. Talleyrand will convey your decision. → display-only
  - saved `NAV1-A_t29` → Game saved: NAV1-A_t29
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Portugal armistice losing · Holland client petition
- LEDGER treasury 19790 · net +549 · threat 43 · provinces 28 (+0) · ceiling 23920 · army 61660 · vassals Holland 77
  - NET income 3012 · trade 335 · admin 50 · tribute 337 · upkeep 448 · charges 2362 · occupation 75 · blockade 210 · admiralty 90
- DISPATCH: Sire — the enemy has held Franche-Comte, Lyonnais and Provence 10 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Britain's armistice proposal

## Turn 30 — Early December 1806
  - MAILBOX #20 Portugal incoming_proposal: Portugal — Armistice → activated
  - MAILBOX #21 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Portugal, armistice_losing #29 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #30 → grant the petition
  - POPUP diplomatic_dialogue: Portugal, armistice_losing #29 → reject
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (77 → 81); bond -5 → 15 (+0 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #30 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - saved `NAV1-A_t30` → Game saved: NAV1-A_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 20008 · net +189 · threat 40 · provinces 28 (+0) · ceiling 21427 · army 60533 · vassals Holland 81
  - NET income 3018 · trade 335 · admin 50 · upkeep 448 · charges 2391 · occupation 75 · blockade 210 · admiralty 90
- DISPATCH: Sire — Marshal Soult's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Portugal's armistice proposal

---
finished: **completed** · commands 133 · popups 79 · battles 34
