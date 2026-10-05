# Playtest digest — CMD-ULM

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `c14678984809` (dirty) · content `d4a1fdd2fc4f` · driver `e498338939cb`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2125, own corps) vs Mack (lost 20983) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc…
  - ⚔ Archduke Charles (lost 2511) vs Bernadotte (lost 5004, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 1648 · net +1473 · threat 72 · provinces 28 · ceiling 33207 · army 174615 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2164 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,004 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (19,003; expect about 115,485 with the corps likely to arrive, up to 120,287 if all march) vs Mack (substantial force) at Munich — the balance of force look…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 445, own corps) vs Mack (lost 27183) — Davout, Massena and Napoleon arrived to reinforce Ney, but Teulie failed to reach the field in time. And Mack was taken… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Bernadotte. Casualties:… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Deroy. Casualties: Arch…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 934) vs Bernadotte (lost 6921) — Where was Ney? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 1814) vs Deroy (lost 6383) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 2 · Naples open borders · Portugal open borders
- LEDGER treasury 3159 · net +1866 · threat 78 · provinces 28 (+0) · ceiling 35776 · army 159956 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 94
  - NET income 2590 · trade 425 · admin 50 · tribute 937 · upkeep 1714 · charges 66 · blockade 266 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 29 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Naples: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 738 gold (×3 at war) (×1.23 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- SPENT 738g on this turn's orders
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, retreat×1, stance_change×1, move×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 2407, own corps) vs Archduke Charles (lost 10850) — Reinforcements from Lannes, Massena and Napoleon bolstered Murat's position — though Ney, Davout and Soult never arrive… — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4413 · net +2045 · threat 79 · provinces 28 (+0) · ceiling 36559 · army 151705 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 475 · admin 50 · tribute 937 · upkeep 1466 · charges 153 · blockade 298 · admiralty 90
- DISPATCH: Sire — Ney, Davout and Bernadotte stand 42,766 men at Munich, which feeds 37,500. 5,266 too many. 6,799 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for …
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia and Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, ma…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6705 · net +2033 · threat 77 · provinces 28 (+0) · ceiling 37134 · army 147170 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2590 · trade 550 · admin 50 · tribute 937 · upkeep 1346 · charges 314 · blockade 344 · admiralty 90
- DISPATCH: Sire — Ney, Davout and Bernadotte stand 41,822 men at Munich, which feeds 37,500. 4,322 too many. 7,743 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large for …
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Archduke Charles` → ✓ Ney pursues Archduke Charles (at Franconia). Moves to Franconia. The province is secured. A standing order, not a single attack: he closes 1 province a turn, attacks on …
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✗ Murat is already in Swabia.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Teulie. Casualties: Arc…
  - ⚔ Archduke Charles (lost 701) vs Teulie (lost 4581) — Teulie stood alone, Sire. Bernadotte never came.
  - verbs: attack×1
- ORDER Ney [active]: Ney is pursuing Archduke Charles (0 turns remaining).
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 2,919 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 2,919 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 8676 · net +1617 · threat 77 · provinces 29 (+1) · ceiling 24221 · army 140688 · vassals Holland 97 · Kingdom of Italy 89 · Switzerland 97
  - NET income 2625 · trade 612 · admin 50 · tribute 694 · upkeep 1128 · charges 694 · occupation 70 · blockade 382 · admiralty 90
- DISPATCH: Sire — Teulie was mauled at Milan: half of his corps — 4,581 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke John is at Bohemia, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 751, Paget 1,284. Bot…
  - ⚔ Castanos (lost 751) vs Paget (lost 1284) — Paget was close. A period of drilling could have changed the outcome. — The Line Holds +15% (Paget)
  - verbs: move×2, wait×1, attack×1
- ORDER Ney [continues]: Ney hears cannon fire at Milan but cannot answer it — Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles. The pursu…
- LEDGER treasury 9997 · net +1158 · threat 65 · provinces 29 (+0) · ceiling 20796 · army 135763 · vassals Holland 97 · Switzerland 96
  - NET income 2626 · trade 612 · admin 50 · tribute 337 · upkeep 1068 · charges 857 · occupation 70 · blockade 382 · admiralty 90
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (16,180; expect about 37,895 with the corps likely to arrive) vs Archduke Charles (substantial force) at Tyrol — the balance of force looks even — a hard fi…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 3746, own corps) vs Archduke Charles (lost 1620) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (15,858) vs Archduke Charles (29,823 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 5597) vs Archduke Charles (lost 1464) — Murat's troops broke against their walls. Fortified positions demand respect.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. Turn 8 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (152 lost to march) Captured: France → Austria · ArchdukeJohn marches from Provence into Lyonnais unopposed! (150 lost to march) Captured: France → Austria · Castanos takes Leon where he stands! Captured: Britain → Spain · Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 337, Paget 1,345. Bot…
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (152 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Lyonnais unopposed! (150 lost to march) Captured: France → Austria
  - 🏴 Spain: Castanos takes Leon where he stands! Captured: Britain → Spain
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Aragon!
  - ⚔ Castanos (lost 337) vs Paget (lost 1345) — Paget held superior ground, yet Castanos prevailed. A grim day, Sire. And Paget was taken on that field — Spain holds h… — The Line Holds +15% (Paget)
  - verbs: attack×4, fortify×1, wait×1
- ORDER Davout [active]: Davout is marching to Bohemia (2 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- LEDGER treasury 10795 · net +1257 · threat 63 · provinces 27 (-2) · ceiling 24510 · army 117023 · vassals Holland 93 · Switzerland 91
  - NET income 2471 · trade 612 · admin 50 · tribute 337 · upkeep 896 · charges 805 · occupation 40 · blockade 382 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 10
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 2). Moved to Munich. Route: Munich -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Lyonnais into Limousin unopposed! (149 lost to march) Captured: France → Austria · ArchdukeCharles strikes back after successfully defending!
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Limousin unopposed! (149 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 2289) vs Bernadotte (lost 615, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×2, move×1, wait×1
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
- ORDER Davout : Davout: 'Cannon fire at Munich, Sire. Investigate?'
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Munich, Sire. Investigate?' → investigate
- LEDGER treasury 11870 · net +1072 · threat 61 · provinces 26 (-1) · ceiling 23031 · army 108133 · vassals Holland 93 · Switzerland 90
  - NET income 2364 · trade 612 · admin 50 · tribute 337 · upkeep 832 · charges 947 · occupation 40 · blockade 382 · admiralty 90
- DISPATCH: Sire — Limousin has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 7
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Limousin into Berry unopposed! (147 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Limousin into Berry unopposed! (147 lost to march) Captured: France → Austria
  - verbs: recruit×2, attack×1, wait×1
- ORDER Massena [completed]: Massena arrives at Milan. Massena: "It is done. Point me at something that shoots back, Sire."
- LEDGER treasury 12902 · net +898 · threat 58 · provinces 25 (-1) · ceiling 21949 · army 103701 · vassals Holland 93 · Switzerland 89
  - NET income 2217 · trade 612 · admin 50 · tribute 337 · upkeep 800 · charges 1081 · requisitions 75 · occupation 40 · blockade 382 · admiralty 90
- DISPATCH: Sire — Berry has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 9
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted, diplomatic_relation_shift)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Swabia to Franconia (102 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich, Swabia.
  - saved `CMD-ULM_t10` → Game saved: CMD-ULM_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 10 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Lisbon into Andalusia unopposed! (50 lost to march) Captured: Spain → Britain · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Ney. Casualties: Archdu… · ArchdukeJohn assaults the Normandy garrison! Garrison: 12,000 -> 7,397 (-4,603). ArchdukeJohn loses 3,333 troops. Garri… · ArchdukeJohn assaults the Normandy garrison! Garrison collapses (7,397 -> 0). ArchdukeJohn loses 2,283 troops in the as…
  - 🏴 Britain: Wellesley marches from Lisbon into Andalusia unopposed! (50 lost to march) Captured: Spain → Britain
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franconia. (763 lost to march) Franconia has been captured by Austria!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -114g, France -159g. Captured: France → Austria
  - ⚔ Archduke Charles (lost 646) vs Ney (lost 4491, own corps) — Reinforcements from Napoleon bolstered Ney's position — though Soult never arrived, Sire.
  - verbs: attack×4, recruit×2, fortify×1, unfortify×1, form_square×1, wait×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 13037 · net +693 · threat 55 · provinces 23 (-2) · ceiling 19155 · army 93663 · vassals Holland 91 · Switzerland 86
  - NET income 2060 · trade 612 · admin 50 · tribute 337 · upkeep 720 · charges 1249 · requisitions 75 · blockade 382 · admiralty 90
- DISPATCH: Sire — Normandy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 9
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #10 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #10 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `Ney, attack Archduke John` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Murat can already reach the body of the realm from w…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 8 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,472 troops. G… · ArchdukeCharles assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,929 troops in th… · Deroy marches from Swabia into Franconia unopposed! (279 lost to march) Captured: Austria → Bavaria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -96g, Bavaria -125g. Captured: Bavaria → Austria
  - 🏴 Bavaria: Deroy marches from Swabia into Franconia unopposed! (279 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy moves from Franconia to Bohemia. Bohemia falls to Bavaria!
  - verbs: move×3, attack×3, break_square×1, fortify×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13679 · net +532 · threat 52 · provinces 23 (+0) · ceiling 18245 · army 91073 · vassals Holland 91 · Switzerland 85
  - NET income 2060 · trade 612 · admin 50 · tribute 337 · upkeep 696 · charges 1359 · blockade 382 · admiralty 90
- DISPATCH: Sire — Berry, Limousin, Lyonnais and 2 more lie in enemy hands. Austria holds them.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Munich. A new design hardens in their court.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +6 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: 18 approaches from Bavaria and Austria are rebuffed (open borders agreement)

## Turn 12 — Early March 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Berry, Limousin, Lyonnais, Normandy and Provence stay Austrian by the treaty. Status quo: Andalusia stays British by the treaty. Status quo: Bohemia stays Bavarian by the treaty. Status quo: Munich stays Austrian by the treaty. → display-only
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: garrison×1, wait×1
- ORDER Davout [completed]: Davout arrives at Franche-Comte. Davout: "It is done. I took the liberty of posting pickets."
- ORDER Napoleon [completed]: Napoleon arrives at Franche-Comte.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 15894 · net +2189 · threat 24 · provinces 23 (+0) · ceiling 198250 · army 94166 · vassals Holland 89 · Switzerland 84
  - NET income 2060 · trade 612 · admin 50 · tribute 337 · upkeep 704 · charges 166
- DISPATCH: Sire — Massena is no nearer home, and the safe passage leaves 2 turns to spare. After that his corps will be interned where it stands.
  - RAIL status_quo_conceded: Berry, Limousin, Lyonnais, Normandy and Provence — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,572 gold. Prussia is now free to look elsewhere.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: And Russia stirs at its own design.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Munich — Austria is not forgiven
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 52 to 26.
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)

## Turn 13 — Late March 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, move to Franconia` → ✓ Davout begins marching to Franconia (distance: 2). Moved to Swabia. Route: Swabia -> Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 4 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×3, wait×1
- ORDER Davout [active]: Davout is marching to Franconia (2 turns remaining).
- LEDGER treasury 17762 · net +2070 · threat 22 · provinces 23 (+0) · ceiling 190250 · army 90833 · vassals Holland 98 · Switzerland 83
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 688 · charges 189
- DISPATCH: Sire — 3 turns now with Berry, Limousin, Lyonnais and 2 more in enemy hands. The country counts every one of them.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Swa…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- ORDER Davout [completed]: Davout arrives at Franconia. Davout: "Done, and done properly — no stragglers, no surprises."
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 19848 · net +2061 · threat 20 · provinces 23 (+0) · ceiling 191583 · army 88620 · vassals Holland 97 · Switzerland 82
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 672 · charges 214
- DISPATCH: Sire — the enemy has held Berry, Limousin, Lyonnais and 2 more 4 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #14 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 21692 · net +1822 · threat 18 · provinces 23 (+0) · ceiling 173500 · army 86951 · vassals Holland 96 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · upkeep 664 · charges 236
- DISPATCH: Sire — Prussia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. Bound for now by a fresh peace: Britain, Russia and Austria. The cheapest court to keep out of i…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✓ Ney begins marching to Bohemia (distance: 2). Moved to Franconia. Route: Franconia -> Bohemia.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Ney [active]: Ney is marching to Bohemia (2 turns remaining).
- LEDGER treasury 23522 · net +1808 · threat 16 · provinces 23 (+0) · ceiling 174166 · army 85751 · vassals Holland 95 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · upkeep 656 · charges 258
- DISPATCH: Sire — Massena is no nearer home, and the safe passage leaves 2 turns to spare. After that his corps will be interned where it stands.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_auto_downgrade)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 36% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 25338 · net +1794 · threat 14 · provinces 23 (+0) · ceiling 174833 · army 84711 · vassals Holland 94 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · upkeep 648 · charges 280
- DISPATCH: Sire — Massena is no nearer home, and the safe passage leaves 2 turns to spare. After that his corps will be interned where it stands.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- DIPLO +4 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×3, wait×1
- LEDGER treasury 27148 · net +1789 · threat 12 · provinces 23 (+0) · ceiling 176166 · army 83704 · vassals Holland 93 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · upkeep 632 · charges 301
- DISPATCH: Sire — Britain, Russia, Austria, Prussia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Prussia: Talleyrand brings her…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Swabia to Franconia (76 lost to march, 153 to enemy harassment)
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 21.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 1 action unused) Turn 20 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 28945 · net +1775 · threat 10 · provinces 23 (+0) · ceiling 176833 · army 82148 · vassals Holland 92 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · upkeep 624 · charges 323
- DISPATCH: Sire — the establishment stands 35,352 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-ULM_t20` → Game saved: CMD-ULM_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 30728 · net +2099 · threat 8 · provinces 23 (+0) · ceiling 205583 · army 80829 · vassals Holland 91 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 337 · upkeep 616 · charges 344
- DISPATCH: Sire — the enemy has held Berry, Limousin, Lyonnais and 2 more 10 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 32851 · net +2097 · threat 5 · provinces 23 (+0) · ceiling 207583 · army 79522 · vassals Holland 90 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 337 · upkeep 592 · charges 370
- DISPATCH: Sire — Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 6
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 22 — Early August 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (90 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. Turn 23 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 34611 · net +1964 · threat 2 · provinces 23 (+0) · ceiling 198250 · army 78248 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 592 · charges 391
- DISPATCH: Sire — Britain, Russia, Austria, Prussia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Prussia: Talleyrand brings her…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 36575 · net +1941 · threat 0 · provinces 23 (+0) · ceiling 198250 · army 76987 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 592 · charges 414
- DISPATCH: Sire — Russia enacts the Extraordinary Levy — infantry levies cost 20% less (×0.8); infantry drafts muster at -10 morale.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat is fortified and cannot drill. Abandon fortification first.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 38532 · net +1933 · threat 0 · provinces 23 (+0) · ceiling 199583 · army 75742 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 576 · charges 438
- DISPATCH: Sire — Austria enacts the Jäger Battalions — infantry drafts muster at +10 morale.
  - TURN EVENTS 5
- COURTS: The court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 40473 · net +1918 · threat 0 · provinces 23 (+0) · ceiling 200250 · army 74532 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 568 · charges 461
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 42407 · net +1911 · threat 0 · provinces 23 (+0) · ceiling 201583 · army 73340 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 552 · charges 484
- DISPATCH: Sire — Russia enacts the War Ministry under Arakcheev — +5 morale from every drill.
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 44334 · net +1903 · threat 0 · provinces 23 (+0) · ceiling 202916 · army 72184 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 536 · charges 508
- DISPATCH: Sire — the court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 46253 · net +1896 · threat 0 · provinces 23 (+0) · ceiling 204250 · army 71062 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 225 · upkeep 520 · charges 531
- DISPATCH: Sire — the establishment stands 46,438 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 48149 · net +2211 · threat 0 · provinces 23 (+0) · ceiling 232333 · army 69958 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 562 · upkeep 520 · charges 553
- DISPATCH: Sire — the enemy has held Berry, Limousin, Lyonnais and 2 more 19 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-ULM_t30` → Game saved: CMD-ULM_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 50368 · net +2192 · threat 0 · provinces 23 (+0) · ceiling 233000 · army 68888 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 562 · upkeep 512 · charges 580
- DISPATCH: Sire — the court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 52576 · net +2182 · threat 0 · provinces 23 (+0) · ceiling 234333 · army 67851 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 562 · upkeep 496 · charges 606
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 54758 · net +2155 · threat 0 · provinces 23 (+0) · ceiling 234333 · army 66834 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 562 · upkeep 496 · charges 633
- DISPATCH: Sire — the court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 56913 · net +2130 · threat 0 · provinces 23 (+0) · ceiling 234333 · army 65861 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 562 · upkeep 496 · charges 658
- DISPATCH: Sire — the court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 59013 · net +2074 · threat 0 · provinces 23 (+0) · ceiling 231833 · army 64918 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 574 · admin 50 · tribute 562 · upkeep 488 · charges 684
- DISPATCH: Sire — relations between France and Spain have collapsed: Alliance → Defensive Alliance.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 61095 · net +2057 · threat 0 · provinces 23 (+0) · ceiling 232500 · army 64003 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 574 · admin 50 · tribute 562 · upkeep 480 · charges 709
- DISPATCH: Sire — Britain, Russia, Austria and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 i…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 63160 · net +2041 · threat 0 · provinces 23 (+0) · ceiling 233166 · army 63114 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 574 · admin 50 · tribute 562 · upkeep 472 · charges 733
- DISPATCH: Sire — Britain, Russia, Austria and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 i…
  - TURN EVENTS 4
- COURTS: The court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 65209 · net +2024 · threat 0 · provinces 23 (+0) · ceiling 233833 · army 62252 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 574 · admin 50 · tribute 562 · upkeep 464 · charges 758
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 67241 · net +2008 · threat 0 · provinces 23 (+0) · ceiling 234500 · army 61416 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 574 · admin 50 · tribute 562 · upkeep 456 · charges 782
- DISPATCH: Sire — the court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 69265 · net +1999 · threat 0 · provinces 23 (+0) · ceiling 235833 · army 60615 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 574 · admin 50 · tribute 562 · upkeep 440 · charges 807
- DISPATCH: Sire — Britain, Russia, Austria and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 i…
  - TURN EVENTS 3
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-ULM_t40` → Game saved: CMD-ULM_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 71264 · net +1975 · threat 0 · provinces 23 (+0) · ceiling 235833 · army 59837 · vassals Holland 100 · Switzerland 92
  - NET income 2060 · trade 574 · admin 50 · tribute 562 · upkeep 440 · charges 831
- DISPATCH: Sire — Britain, Russia, Austria and 2 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Sweden: Talleyrand brings her to −10 in…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 200 · popups 33 · battles 13
