# Playtest digest — CMD-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `846097827dc8` (dirty) · content `d8c0700dcbaa` · driver `ab03febad338`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2375, own corps) vs Mack (lost 18369) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Murat and Bernadotte never arrived, S… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 2457) vs Bernadotte (lost 5337, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 893 · net +771 · threat 75 · provinces 28 · ceiling 17544 · army 173606 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2866 · blockade 250 · admiralty 90
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
  - ↳ MUSTER — Davout (23,250; expect about 33,991 with the corps likely to arrive) vs Archduke Charles (49,091 men) at Franconia — the balance of force looks unfavorable.
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (23,250; expect about 33,991 with the corps likely to arrive) vs Archduke Charles (49,091 men) at Franconia — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — likely to make it in time (about 100%) (The corps system lowers the bar by 10) — and will stand at Franconia
  WILL NOT — Bernadotte: stands on the same field and will do NOTHING — order him to support, or he watches
  WILL NOT — Massena: has already marched this turn
  WILL NOT — Napoleon: has already marched this turn
  WILL NOT — Teulie: has already marched this turn
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Franconia would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: all told, Davout's own modifiers weigh 10% against the attack; Archduke Charles stands +3% on the defense (his stance, his character and his works).
  Franconia feeds 60,000 — the whole muster can stand there fed.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 52,702 we muster) would cost ~395g.
  Every corps in the province shares the field — that is the design, and the quarrel above is its one exception: no order holds a corps out of its own province, but a feud does. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Davout (23,250; expect about 33,991 with the corps likely to arrive) vs Archduke Charles (49,091 men) at Franconia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 4724, own corps) vs Archduke Charles (lost 2302) — Ney marched to Davout's guns as ordered. It was not enough.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte · Archduke Charles attacks Deroy · Archduke Charles attacks Murat
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - 🏴 Austria: Archduke Charles attacks Deroy — Swabia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 885) vs Bernadotte (lost 7395) — A grievous defeat for Bernadotte, Sire. The losses are severe. And Bernadotte was taken on that field — Austria holds h…
  - ⚔ Archduke Charles (lost 1607) vs Deroy (lost 7467) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2290) vs Murat (lost 6775) — Murat's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 1309 · net +1486 · threat 81 · provinces 28 (+0) · ceiling 16399 · army 141157 · vassals Holland 94 · Kingdom of Italy 94 · Switzerland 90
  - NET income 2575 · trade 450 · admin 50 · tribute 937 · upkeep 2090 · contributions 65 · blockade 281 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +11 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 29 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franche-Comte — shall Ney engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franche-Comte — shall Ney engage him? → 1 (first option: Archduke Charles at Franche-Comte)
- CMD `Davout, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franche-Comte — shall Davout engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Franche-Comte — shall Davout engage him? → 1 (first option: Archduke Charles at Franche-Comte)
  - ↳ MUSTER — Davout (17,415; expect about 94,559 with the corps likely to arrive, up to 97,954 if all march) vs Archduke Charles (38,732 men) at Franche-Comte — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1125, own corps) vs Archduke Charles (lost 7120) — Massena, Napoleon and Teulie arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire. — The corps system brought Teulie in.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (166 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 623 gold (×3 at war) (×1.04 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 623g on this turn's orders
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, retreat×1, stance_change×1, move×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 2718 · net +2081 · threat 81 · provinces 28 (+0) · ceiling 21907 · army 136924 · vassals Holland 95 · Kingdom of Italy 94 · Switzerland 89
  - NET income 2561 · trade 525 · admin 50 · tribute 937 · upkeep 1456 · charges 77 · contributions 40 · blockade 329 · admiralty 90
- DISPATCH: Sire — Archduke Charles has crossed into Nivernais. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL province_returned: France hands Swabia back to Bavaria — the liberated soil comes home.
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia and Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 4 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke John at Tyrol — shall Ney engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke John at Tyrol — shall Ney engage him? → 1 (first option: Archduke John at Tyrol)
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franche-Comte. Defense bonus: +7% (grows +3% per t…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, retreat×1, stance_change×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1033, own corps) vs Archduke Charles (lost 9213) — Massena, Napoleon and Teulie arrived to reinforce Murat! The timely arrival swung the battle in our favor, Sire.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
- LEDGER treasury 4796 · net +1893 · threat 79 · provinces 28 (+0) · ceiling 21454 · army 130904 · vassals Holland 96 · Kingdom of Italy 94 · Switzerland 88
  - NET income 2558 · trade 587 · admin 50 · tribute 937 · upkeep 1384 · charges 317 · contributions 80 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - TURN EVENTS 10
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (300g/turn)
  - LOG province_returned: France hands Swabia back to Bavaria — the liberated soil comes home
  - LOG ai_ai_proposal_refused: Naples rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ Archduke Charles stands at Orleanais, three marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Swabia, Bavaria's soil), or cancel?
  - POPUP clarification: Ney, pursuit_ask, Archduke Charles stands at Orleanais, three marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Swabia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Lannes, attack Mack` → ✓ Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Orleanais — shall Lannes engage him?
  - POPUP clarification: Berthier, attack_target, Mack fell at Munich on turn 2, Sire — his corps is no more. The nearest in sight is Archduke Charles at Orleanais — shall Lannes engage him? → 1 (first option: Archduke Charles at Orleanais)
  - POPUP clarification: Lannes, pursuit_ask, Archduke Charles stands at Orleanais, two marches off. Pursue him (2 AP — a standing order; the first march takes Lannes to Lorraine), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Soult, move to Swabia` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Swabia today.
- CMD `Murat, move to Swabia` → ✗ Not enough actions! Need 1, have 0 — Murat cannot march to Swabia today.
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Munich · Archduke John attacks Munich · Archduke John attacks Milan · Archduke John attacks Milan
  - 🏴 Austria: Archduke John attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - 🏴 Austria: Archduke John attacks Milan — The garrison of Milan is destroyed. · Region captured: Milan (was Kingdom of Italy) (secured)
  - verbs: attack×4, unfortify×1
- ORDER Lannes [completed]: Archduke Charles taken prisoner Lannes: "Done — and I trust the next order has more fire in it."
- ORDER Ney [completed]: Archduke Charles taken prisoner Ney: "Done — and I trust the next order has more fire in it."
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 690, own corps) vs Archduke Charles (lost 12519) — Massena, Napoleon and Teulie's timely arrival bolstered Murat's position. Well-coordinated, Sire. And Archduke Charles …
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 6734 · net +1636 · threat 77 · provinces 28 (+0) · ceiling 25318 · army 127192 · vassals Holland 97 · Kingdom of Italy 95 · Switzerland 97
  - NET income 2554 · trade 587 · admin 50 · tribute 487 · upkeep 1168 · charges 416 · blockade 368 · admiralty 90
- DISPATCH: Sire — the Archduke Charles of Austria is taken at Orleanais — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +8 medium/low (province_changed_hands ×6, law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 approaches from Austria, Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 8.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 94% -> 89%
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action unused) Turn 7 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: shadow_command, Marshal Massena asks for a command → detach
  -     ↳ Massena straightens. "You will not regret it, Sire." March him to Normandy and the front is his — the order i…
- LEDGER treasury 7795 · net +1521 · threat 75 · provinces 28 (+0) · ceiling 24467 · army 128755 · vassals Holland 97 · Kingdom of Italy 95 · Switzerland 96
  - NET income 2559 · trade 587 · admin 50 · tribute 487 · upkeep 1176 · charges 528 · blockade 368 · admiralty 90
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,212g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 7
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: Spain rebuffs Austria, Prussia and Bavaria (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 7.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 3). Moved to Swabia. Route: Swabia -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 6 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Leon · Castanos attacks Paget
  - 🏴 Spain: Castanos attacks Paget — Leon CAPTURED! (was Britain) (secured)
  - ⚔ Castanos (lost 623) vs Paget (lost 1262) — Paget's aggressive posture left the troops exposed when Castanos's attack came. — The Line Holds +15% (Paget)
  - ⚔ Castanos (lost 329) vs Paget (lost 1223) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better. — The Line Holds +15% (Paget)
  - verbs: move×2, attack×2, stance_change×1, break_square×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 9155 · net +1213 · threat 73 · provinces 28 (+0) · ceiling 22000 · army 127215 · vassals Holland 97 · Kingdom of Italy 95 · Switzerland 95
  - NET income 2562 · trade 587 · admin 50 · tribute 487 · upkeep 1340 · charges 675 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - TURN EVENTS 7
- DIPLO +7 medium/low (province_changed_hands ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Britain rebuffs Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Archduke Charles is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Swa…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shi…
- CMD `Massena, move to Milan` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 6 actions, 5 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Carniola · Archduke John attacks Croatia · Archduke John attacks Croatia · Archduke John attacks Croatia
  - 🏴 Austria: Archduke John attacks Carniola — Region captured: Carniola (was Bavaria) (secured)
  - ⚔ Archduke John (lost 1201) vs Deroy (lost 1141) — Neither Deroy nor Archduke John could claim the field. The armies remain locked.
  - ⚔ Archduke John (lost 974) vs Deroy (lost 1014) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke John (lost 956) vs Deroy (lost 672) — Stalemate. Deroy and Archduke John glare at each other across the field.
  - ⚔ Castanos (lost 65) vs Paget (lost 646) — The line gave way. Paget is falling back, and not in good order. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - verbs: attack×5, fortify×1
- ORDER Davout [continues]: Davout marches to Franconia. 1 region to Bohemia.
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 10381 · net +1084 · threat 71 · provinces 28 (+0) · ceiling 21477 · army 125717 · vassals Holland 97 · Kingdom of Italy 95 · Switzerland 94
  - NET income 2567 · trade 587 · admin 50 · tribute 487 · upkeep 1332 · charges 817 · blockade 368 · admiralty 90
- DISPATCH: Sire — Carniola has been taken by Austria.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War for Croatia — Britain + Austria + Russia. Offering 2170 gold. It also Austria's …
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +7 medium/low (province_changed_hands, law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Spain rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria and Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 17 approaches from Austria, Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
  - MAILBOX #9 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity, territory_compensate
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Croatia — the table with Austria + Russia (4 pairs resolved). Status quo: Croatia stays Bavarian by the treaty. Status quo: Milan stays Austrian by the treaty. Prisoners: Bernadotte comes home to Paris under this peace. Prisoners: Archduke Charles, our captive, goes home to Vienna under this peace — an Austrian commander back in the field. → display-only
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Orleanais. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Orleanais (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: …
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- SPENT 1040g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney demands to be heard → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #19 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +8 (92 → 100); bond -7 → 13 (+0 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 12634 · net +882 · threat 36 · provinces 28 (+0) · ceiling 24109 · army 132322 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2570 · trade 587 · admin 50 · tribute 337 · upkeep 1388 · charges 816 · blockade 368 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL settlement_summary: Sire, the settlement of the War for Croatia — the table with Austria + Russia is not a curtain call; it is an accounting. Spain, Bavaria, KingdomOfIt…
  - RAIL status_quo_conceded: Milan — left with Austria by the peace, titled to them by treaty.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 9
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, province_changed_hands ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, agenda_shift ×2)
  - LOG sponsorship_granted: France licences Austria's design against Ottoman Empire
  - LOG design_bought_off: The peace points Austria elsewhere: France licenses The Eastern Question (Albania) — her other designs sleep
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 71 to 35; Britain remains at war with us.
  - LOG ai_ai_proposal_refused: 11 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain and Russia rebuff Prussia (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Swabia to Franconia (144 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Croatia, Franconia, Munich, Swabia.
  - saved `CMD-A_t10` → Game saved: CMD-A_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Teulie [continues]: Teulie marches to Burgundy. 2 regions to Piedmont.
- LEDGER treasury 13522 · net +783 · threat 37 · provinces 28 (+0) · ceiling 23300 · army 131277 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 92
  - NET income 2572 · trade 587 · admin 50 · tribute 337 · upkeep 1384 · charges 921 · blockade 368 · admiralty 90
- DISPATCH: Sire — Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +4 medium/low (province_changed_hands ×2, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs 4 courts (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat begins marching to Franconia (distance: 3). Moved to Lorraine. Route: Lorraine -> Swabia -> Franconia.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, recruit×2, defend×1
- ORDER Murat [active]: Murat is marching to Franconia (2 turns remaining).
- ORDER Teulie [continues]: Teulie marches to Lyonnais. 1 region to Piedmont.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Davout and Murat: They settle into cold war.
- LEDGER treasury 14319 · net +694 · threat 38 · provinces 28 (+0) · ceiling 22649 · army 129892 · vassals Holland 97 · Kingdom of Italy 96 · Switzerland 91
  - NET income 2574 · trade 587 · admin 50 · tribute 337 · upkeep 1372 · charges 1024 · blockade 368 · admiralty 90
- DISPATCH: Sire — Hanover and Prussia have made peace without us.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 3,010 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 11
- DIPLO +5 medium/low (law_enacted_abroad, province_changed_hands ×2, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: Austria and Naples rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 13 courts rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 13 courts rebuff Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, m…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 95% -> 86%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 600g on this turn's orders
- enemy phase: 7 actions, 3 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Andalusia · Blake attacks Wellesley · Castanos attacks Wellesley
  - 🏴 Spain: Castanos attacks Andalusia — Region captured: Andalusia (was Britain) (secured)
  - ⚔ Blake (lost 153, own corps) vs Wellesley (lost 732) — The margin was slim. Training and preparation would serve Wellesley well. — The Line Holds +15% (Wellesley)
  - ⚔ Castanos (lost 243, own corps) vs Wellesley (lost 562) — A skirmish, Sire. Wellesley's men traded shots with Castanos; there was no battle to speak of. — The Line Holds +15% (Wellesley)
  - verbs: attack×3, unfortify×1, move×1, wait×1, recruit×1
- ORDER Murat [completed]: Murat arrives at Franconia.
- ORDER Teulie [completed]: Teulie arrives at Piedmont. Teulie: "Done — and I trust the next order has more fire in it."
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 14326 · net +543 · threat 39 · provinces 28 (+0) · ceiling 20599 · army 131399 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2575 · trade 587 · admin 50 · tribute 337 · upkeep 1484 · charges 1064 · blockade 368 · admiralty 90
- DISPATCH: Sire — Teulie's contingent comes home crowned with victory — 4,627 of 7,500 men. The Kingdom of Italy rejoices (+6 loyalty).
  - TURN EVENTS 8
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, diplomatic_vassal_contingent)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG ai_ai_proposal_refused: 15 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Murat hesitates briefly but follows orders. Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #20 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #21 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 1 more turn.
- CMD `Davout, move to Franconia` → ✗ Davout is already in Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 8 actions, 1 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Blake attacks Wellesley
  - ⚔ Blake (lost 40, own corps) vs Wellesley (lost 455) — The line gave way. Wellesley is falling back, and not in good order. And Wellesley was taken on that field — Spain hold… — The Line Holds +15% (Wellesley)
  - verbs: wait×2, recruit×2, retreat×1, stance_change×1, attack×1, fortify×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 14875 · net +685 · threat 40 · provinces 28 (+0) · ceiling 22513 · army 130185 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 89
  - NET income 2577 · trade 587 · admin 50 · tribute 562 · upkeep 1480 · charges 1153 · blockade 368 · admiralty 90
- DISPATCH: Sire — Austria and Russia would now join a league against us (relations −65 and −75). The Balance of Europe names the price to keep each out.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle the War with Britain — Britain.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as alliance.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 14 — Early April 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #22 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #23 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with Britain — the table with Britain (3 pairs resolved). → display-only
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Orleanais and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 17482 · net +2576 · threat 42 · provinces 28 (+0) · ceiling 232083 · army 128998 · vassals Holland 94 · Kingdom of Italy 96 · Switzerland 88
  - NET income 2578 · trade 587 · admin 50 · tribute 562 · upkeep 1016 · charges 185
- DISPATCH: Sire — peace with Britain is signed. A white peace — the map stands as it was.
  - RAIL settlement_summary: Sire, the settlement of the War with Britain — the table with Britain is not a curtain call; it is an accounting. France, Spain must be read beside r…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 9
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3)

## Turn 15 — Late April 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #24 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +6 (94 → 100); bond -18 → 2 (+0 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 94%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 19492 · net +2209 · threat 44 · provinces 28 (+0) · ceiling 203500 · army 130835 · vassals Holland 98 · Kingdom of Italy 94 · Switzerland 87
  - NET income 2580 · trade 587 · admin 50 · tribute 225 · upkeep 1024 · charges 209
- DISPATCH: Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Austria will move on Ottoman. You may compensate (1,272g — you can afford it); guarantee Ottoman (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 16 — Early May 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #25 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 21440 · net +1924 · threat 45 · provinces 28 (+0) · ceiling 181750 · army 129725 · vassals Holland 96 · Kingdom of Italy 92 · Switzerland 97
  - NET income 2582 · trade 549 · admin 50 · upkeep 1024 · charges 233
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 27 and declare on turn 30: Russia, Austria, Prussia and 5 lesser courts would march. Bound for now b…
  - RAIL crisis_passed: Austria stands down over Ottoman, Sire — the design was bought off — compensation stands.
  - TURN EVENTS 5
- DIPLO +5 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade ×2)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Orleanais (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 23381 · net +2068 · threat 45 · provinces 28 (+0) · ceiling 195666 · army 128655 · vassals Holland 94 · Kingdom of Italy 90 · Switzerland 97
  - NET income 2583 · trade 549 · admin 50 · tribute 150 · upkeep 1008 · charges 256
- DISPATCH: Sire — Austria stands down over Ottoman Empire; the design was bought off, and the bargain stands.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 25459 · net +2053 · threat 45 · provinces 28 (+0) · ceiling 196500 · army 127616 · vassals Holland 92 · Kingdom of Italy 88 · Switzerland 97
  - NET income 2585 · trade 549 · admin 50 · tribute 150 · upkeep 1000 · charges 281
- DISPATCH: Sire — Britain would now join a league against us — relations −85. The price to keep her out: Talleyrand brings her to −10 in 9 turns (9 DP); buying off her design costs 1,200 gold and shortens the r…
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 19 — Late June 1806
  - MAILBOX #14 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #26 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (88 → 98); bond 13 → 33 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes begins marching to Franconia (distance: 2). Moved to Swabia. Route: Swabia -> Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 1 action unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ORDER Lannes [active]: Lannes is marching to Franconia (2 turns remaining).
- LEDGER treasury 27379 · net +1897 · threat 45 · provinces 28 (+0) · ceiling 185416 · army 126418 · vassals Holland 90 · Kingdom of Italy 97 · Switzerland 97
  - NET income 2586 · trade 549 · admin 50 · upkeep 984 · charges 304
- DISPATCH: Sire — Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Lorraine (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-A_t20` → Game saved: CMD-A_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Lannes [completed]: Lannes arrives at Franconia.
- LEDGER treasury 29294 · net +1892 · threat 45 · provinces 28 (+0) · ceiling 186916 · army 123979 · vassals Holland 88 · Kingdom of Italy 96 · Switzerland 97
  - NET income 2588 · trade 549 · admin 50 · upkeep 968 · charges 327
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 27 and declare on turn 30: Britain, Russia, Austria, Prussia and 5 lesser courts would march.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Lannes commands ours at Franconia, ground that takes no levy — mar…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 31204 · net +1887 · threat 45 · provinces 28 (+0) · ceiling 188416 · army 121867 · vassals Holland 86 · Kingdom of Italy 95 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · upkeep 952 · charges 350
- DISPATCH: Sire — Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
  - TURN EVENTS 7
- DIPLO +6 medium/low (law_enacted_abroad ×3, doctrine_cured_abroad ×2, diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Orleanais. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 33107 · net +2217 · threat 45 · provinces 28 (+0) · ceiling 217833 · army 119849 · vassals Holland 84 · Kingdom of Italy 94 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 337 · upkeep 936 · charges 373
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 28 and declare on turn 31: Britain, Russia, Austria, Prussia and 5 lesser courts would march.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot sh…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 35348 · net +2439 · threat 45 · provinces 28 (+0) · ceiling 238583 · army 117951 · vassals Holland 82 · Kingdom of Italy 93 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 562 · upkeep 912 · charges 400
- DISPATCH: Sire — the establishment stands 12,049 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG instrument_lapsed: The bargain between France and Austria is served in full — the design wakes

## Turn 24 — Early September 1806
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #27 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (82 → 92); bond 2 → 22 (+1 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Orleanais. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 37204 · net +2056 · threat 49 · provinces 28 (+0) · ceiling 208500 · army 119164 · vassals Holland 91 · Kingdom of Italy 92 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 225 · upkeep 936 · charges 422
- DISPATCH: Sire — Russia enacts the War Ministry under Arakcheev — +5 morale from every drill.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 3
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG sponsorship_expired: The compact between France and Austria lapses

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 39276 · net +2047 · threat 53 · provinces 28 (+0) · ceiling 209833 · army 117449 · vassals Holland 90 · Kingdom of Italy 91 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 225 · upkeep 920 · charges 447
- DISPATCH: Sire — the establishment stands 12,551 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 41339 · net +2188 · threat 57 · provinces 28 (+0) · ceiling 223666 · army 115833 · vassals Holland 89 · Kingdom of Italy 90 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 375 · upkeep 904 · charges 472
- DISPATCH: Sire — Europe has watched us 22 quiet turns. At this pace the courts consult on turn 28 and declare on turn 31: Britain, Russia, Austria and 4 lesser courts would march. The cheapest court to keep ou…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sardinia, Holland and Kingdom of Italy rebuff Bavaria (open borders agreement)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 43543 · net +2178 · threat 60 · provinces 28 (+0) · ceiling 225000 · army 114307 · vassals Holland 88 · Kingdom of Italy 89 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 375 · upkeep 888 · charges 498
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sweden → Bid for Their Allegi…
  - TURN EVENTS 4
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Naples, Hanover and Sardinia alarmed (threat: 60)

## Turn 28 — Early November 1806
  - MAILBOX #16 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #28 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (89 → 99); bond 33 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Orleanais. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 45579 · net +2012 · threat 58 · provinces 28 (+0) · ceiling 213166 · army 112851 · vassals Holland 87 · Kingdom of Italy 99 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 225 · upkeep 880 · charges 522
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design costs 1…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot sh…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 47599 · net +1995 · threat 56 · provinces 28 (+0) · ceiling 213833 · army 111452 · vassals Holland 86 · Kingdom of Italy 99 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 225 · upkeep 872 · charges 547
- DISPATCH: Sire — St Petersburg now pays London 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 8 turns (8 DP); buying off her design …
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Orleanais. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
  - saved `CMD-A_t30` → Game saved: CMD-A_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 47904 · net +149 · threat 54 · provinces 28 (+0) · ceiling 52113 · army 110110 · vassals Holland 85 · Kingdom of Italy 99 · Switzerland 97
  - NET income 2590 · trade 549 · admin 50 · tribute 225 · upkeep 1216 · charges 1615 · blockade 344 · admiralty 90
- DISPATCH: Sire — Britain, Russia, Austria, Sweden, Hanover and Sardinia are at war with France. Britain tears up the Peace Treaty to do it. Russia tears up the Peace Treaty to do it. Austria tears up the Peace…
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Sweden, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 3 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +6 more
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: And Britain, Sweden and Sardinia stir at their own designs.
- DIPLO +16 medium/low (law_enacted_abroad, diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken, blockade_begins ×4, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).
  - LOG coalition_declared: The Fourth British Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia and Sweden

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, wait×1
- LEDGER treasury 48073 · net +352 · threat 52 · provinces 28 (+0) · ceiling 57234 · army 108821 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 562 · upkeep 1196 · charges 1769 · blockade 344 · admiralty 90
- DISPATCH: Sire — Croatia has been taken by Austria.
  - TURN EVENTS 6
- DIPLO +9 medium/low (province_changed_hands, enemy_marshal_commissioned ×2, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG instrument_lapsed: The bargain between Ottoman Empire and Austria is served in full — the design wakes
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Britain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG design_bought_off: Ottoman Empire buys off Austria's design — the want sleeps
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 48465 · net +229 · threat 50 · provinces 28 (+0) · ceiling 53947 · army 107893 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 562 · upkeep 1156 · charges 1932 · blockade 344 · admiralty 90
- DISPATCH: Sire — not every court of the league has struck us. Austria has an open road to us — 2 marches — and has not struck us. Britain has no road to us but the sea, and Normandy is a defended shore: she ca…
  - TURN EVENTS 5
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG diplomatic_treaty_broken: Russia has broken the Peace Treaty with France by declaring war.
  - LOG sponsorship_granted: Russia sponsors Sweden against France (400g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG ai_ai_proposal_refused: 15 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Austria are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 15 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG ai_ai_proposal_refused: 17 approaches from Russia and Austria are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke John is at Bohemia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — Lannes commands ours at Franconia, ground that takes no levy — mar…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 48694 · net +70 · threat 48 · provinces 28 (+0) · ceiling 50236 · army 106993 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 562 · upkeep 1156 · charges 2091 · blockade 344 · admiralty 90
- DISPATCH: Sire — Britain's gold reaches Austria — the subsidy stands at 500 this season.
  - TURN EVENTS 3
- DIPLO +4 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Russia (defensive alliance)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Orleanais. Army is now mobile.
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Kutuzov is at Bohemia, just one region away.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Wrede · Kutuzov attacks Deroy
  - 🏴 Russia: Kutuzov attacks Wrede — Carniola CAPTURED! (was Bavaria) (secured)
  - ⚔ Kutuzov (lost 1297) vs Wrede (lost 4828) — An aggressive stance invites disaster when one is not the attacker, Sire. Wrede paid the price.
  - ⚔ Kutuzov (lost 3125) vs Deroy (lost 2429) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×2, wait×2, stance_change×1
- LEDGER treasury 48764 · net -83 · threat 46 · provinces 28 (+0) · ceiling 47020 · army 106120 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 562 · upkeep 1156 · charges 2244 · blockade 344 · admiralty 90
- DISPATCH: Sire — Carniola has been taken by Russia.
  - TURN EVENTS 2
- DIPLO +4 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot sh…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Kutuzov attacks Deroy · Bennigsen attacks Deroy · Kutuzov attacks Wrede
  - 🏴 Russia: Kutuzov attacks Wrede — Tyrol CAPTURED! (was Bavaria) (secured)
  - ⚔ Kutuzov (lost 2367) vs Deroy (lost 2565) — Stalemate. Deroy and Kutuzov glare at each other across the field.
  - ⚔ Bennigsen (lost 2063) vs Deroy (lost 1823) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Kutuzov (lost 708) vs Wrede (lost 2864, own corps) — Wrede held superior ground, yet Kutuzov prevailed. A grim day, Sire. And Wrede was taken on that field — Russia holds h…
  - verbs: attack×3, move×1
- LEDGER treasury 48701 · net -60 · threat 44 · provinces 28 (+0) · ceiling 47527 · army 105274 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 1136 · charges 2391 · blockade 344 · admiralty 90
- DISPATCH: Sire — Tyrol has been taken by Russia.
  - TURN EVENTS 3
- DIPLO +6 medium/low (province_changed_hands, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_auto_downgrade ×2, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Britain–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG british_subsidy: Britain's gold: 500g reaches Russia

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Kutuzov at Tyrol instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Kutuzov at Tyrol instead.) → trust
  - ↳ MUSTER — Ney (5,995; expect about 21,730 with the corps likely to arrive, up to 22,558 if all march) vs Kutuzov (25,409 men) at Tyrol — the balance of force looks even — a hard fight that may go against us.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1608, own corps) vs Kutuzov (lost 1730) — Lannes marched to Ney's guns as ordered. It was not enough.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Orleanais. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- SPENT 600g on this turn's orders
- enemy phase: 11 actions, 4 attacks — Britain, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden attacks Ney · Archduke John attacks Davout · Schwarzenberg attacks Davout · Archduke John attacks Murat
  - ⚔ Buxhowden (lost 2273) vs Ney (lost 756, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke John (lost 930, own corps) vs Davout (lost 1122, own corps) — Davout's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Schwarzenberg (lost 505, own corps) vs Davout (lost 1246, own corps) — Davout's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Archduke John (lost 344, own corps) vs Murat (lost 3997) — Murat was caught in an aggressive posture when Archduke John struck, Sire. A defensive stance would have served better.
  - verbs: attack×4, move×3, unfortify×2, form_square×1, wait×1
- ORDER Murat [awaiting_response]: Murat is cornered at Franconia with 1,063 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the l…
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Franconia with 1,063 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- LEDGER treasury 47133 · net -309 · threat 42 · provinces 28 (+0) · ceiling 42439 · army 88894 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 499 · admin 50 · tribute 712 · upkeep 780 · charges 2978 · blockade 312 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG british_subsidy: Britain's gold: 500g reaches Austria

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 12 actions, 4 attacks — Britain, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden attacks Franconia · Kutuzov attacks Munich · Kutuzov attacks Munich · Archduke John attacks Davout
  - 🏴 Russia: Buxhowden attacks Franconia — Region captured: Franconia (was Bavaria) (secured)
  - 🏴 Russia: Kutuzov attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - ⚔ Archduke John (lost 109, own corps) vs Davout (lost 886) — The line gave way. Davout is falling back, and not in good order.
  - verbs: attack×4, fortify×2, retreat×2, stance_change×2, break_square×1, wait×1
- LEDGER treasury 46791 · net -422 · threat 40 · provinces 28 (+0) · ceiling 40757 · army 88008 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 499 · admin 50 · tribute 712 · upkeep 736 · charges 3135 · blockade 312 · admiralty 90
- DISPATCH: Sire — Marshal Murat has been taken. Austria holds him prisoner.
  - RAIL third_party_peace: THE CONGRESS: Bavaria and Russia have made their peace without France. Bavaria, beaten (-47), sues for peace and Russia takes it on the held line; th…
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 500g reaches Russia
  - LOG province_returned: Russia hands Carniola back to Austria — the liberated soil comes home
  - LOG province_returned: Russia hands Tyrol back to Austria — the liberated soil comes home
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3, stance_change×1
- LEDGER treasury 46369 · net -534 · threat 38 · provinces 28 (+0) · ceiling 39062 · army 87909 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 499 · admin 50 · tribute 712 · upkeep 736 · charges 3247 · blockade 312 · admiralty 90
- DISPATCH: Sire — London now pays St Petersburg 500 gold a turn against us — her war with us is paid for.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG third_party_peace: THE CONGRESS: Bavaria and Russia make peace without France

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 45835 · net -635 · threat 36 · provinces 28 (+0) · ceiling 37510 · army 87909 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 499 · admin 50 · tribute 712 · upkeep 736 · charges 3348 · blockade 312 · admiralty 90
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us — her war with us is paid for.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Orleanais (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-A_t40` → Game saved: CMD-A_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden attacks Lannes · Archduke John attacks Wrede
  - 🏴 Russia: Kutuzov moves to Franche-Comte — Franche-Comte falls (was France) and is secured
  - ⚔ Buxhowden (lost 309) vs Lannes (lost 2465) — Lannes's army has been badly mauled. Buxhowden proved the stronger force today.
  - ⚔ Archduke John (lost 777) vs Wrede (lost 2551) — The toll on Wrede's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, move×2
- ORDER Lannes [awaiting_response]: Lannes is cornered at Swabia with 2,389 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the las…
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Swabia with 2,389 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 43630 · net -1966 · threat 34 · provinces 27 (-1) · ceiling 26137 · army 83055 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2510 · trade 499 · admin 50 · tribute 712 · upkeep 656 · charges 4679 · blockade 312 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Russia. Enemy colours fly over French homeland soil. Kutuzov's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as…
  - RAIL settlement_offer_arrival: Russia, for Britain, Russia, Sweden, Hanover and Sardinia, has offered terms to settle the War for Milan — Britain + Russia + Austria + Sweden + Hano…
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (NON AGGRESSION → OPEN BORDERS)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Britain against France (400g/turn)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

---
finished: **completed** · commands 200 · popups 56 · battles 32
