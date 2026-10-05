# Playtest digest — CMD-ULM

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `47eb92ffc944` (dirty) · content `aae077cedc7a` · driver `e498338939cb`
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
- LEDGER treasury 904 · net +729 · threat 72 · provinces 28 · ceiling 17444 · army 174615 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2908 · blockade 250 · admiralty 90
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
- LEDGER treasury 1347 · net +864 · threat 79 · provinces 28 (+0) · ceiling 17104 · army 159956 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 94
  - NET income 2590 · trade 425 · admin 50 · tribute 937 · upkeep 2782 · blockade 266 · admiralty 90
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
- LEDGER treasury 1236 · net +818 · threat 80 · provinces 28 (+0) · ceiling 14861 · army 151705 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 475 · admin 50 · tribute 937 · upkeep 2846 · blockade 298 · admiralty 90
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
- LEDGER treasury 2356 · net +992 · threat 78 · provinces 28 (+0) · ceiling 17194 · army 147170 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2590 · trade 550 · admin 50 · tribute 937 · upkeep 2678 · charges 23 · blockade 344 · admiralty 90
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
- LEDGER treasury 3313 · net +723 · threat 78 · provinces 29 (+1) · ceiling 10259 · army 140688 · vassals Holland 97 · Kingdom of Italy 89 · Switzerland 97
  - NET income 2625 · trade 612 · admin 50 · tribute 694 · upkeep 2580 · charges 136 · occupation 70 · blockade 382 · admiralty 90
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
- LEDGER treasury 3800 · net +431 · threat 66 · provinces 29 (+0) · ceiling 7811 · army 135763 · vassals Holland 97 · Switzerland 96
  - NET income 2626 · trade 612 · admin 50 · tribute 337 · upkeep 2460 · charges 192 · occupation 70 · blockade 382 · admiralty 90
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
- LEDGER treasury 4005 · net +739 · threat 64 · provinces 27 (-2) · ceiling 12065 · army 117023 · vassals Holland 93 · Switzerland 91
  - NET income 2471 · trade 612 · admin 50 · tribute 337 · upkeep 2036 · charges 183 · occupation 40 · blockade 382 · admiralty 90
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
- LEDGER treasury 4667 · net +515 · threat 62 · provinces 26 (-1) · ceiling 10031 · army 108133 · vassals Holland 93 · Switzerland 90
  - NET income 2364 · trade 612 · admin 50 · tribute 337 · upkeep 2080 · charges 256 · occupation 40 · blockade 382 · admiralty 90
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
- LEDGER treasury 5466 · net +712 · threat 59 · provinces 25 (-1) · ceiling 12635 · army 103701 · vassals Holland 93 · Switzerland 89
  - NET income 2217 · trade 612 · admin 50 · tribute 337 · upkeep 1724 · charges 343 · requisitions 75 · occupation 40 · blockade 382 · admiralty 90
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
- enemy phase: 8 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Wellesley marches from Lisbon into Andalusia unopposed! (50 lost to march) Captured: Spain → Britain · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Ney. Casualties: Archdu… · ArchdukeJohn marches from Berry into Guyenne unopposed! (146 lost to march) Captured: France → Austria · ArchdukeJohn marches from Guyenne into Gascony unopposed! (289 lost to march) Captured: France → Austria
  - 🏴 Britain: Wellesley marches from Lisbon into Andalusia unopposed! (50 lost to march) Captured: Spain → Britain
  - 🏴 Austria: ArchdukeJohn marches from Berry into Guyenne unopposed! (146 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Guyenne into Gascony unopposed! (289 lost to march) Captured: France → Austria
  - ⚔ Archduke Charles (lost 565) vs Ney (lost 5181, own corps) — Reinforcements from Napoleon bolstered Ney's position — though Soult never arrived, Sire.
  - verbs: attack×4, recruit×2, fortify×1, wait×1
- ORDER Ney [awaiting_response]: Ney is cornered at Franconia with 4,995 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Franconia with 4,995 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Davout and Murat: They settle into cold war.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #10 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 5689 · net +371 · threat 56 · provinces 23 (-2) · ceiling 9095 · army 88076 · vassals Holland 91 · Switzerland 86
  - NET income 1985 · trade 612 · admin 50 · tribute 337 · upkeep 1700 · charges 401 · occupation 40 · blockade 382 · admiralty 90
- DISPATCH: Sire — Guyenne has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 14
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (80 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos's forces press forward aggressively. Castanos gains the advantage over Wellesley. Casualties: Castanos 450, We… · Castanos holds them at Andalusia while allies attack from Cartagena! (+1 coordination)
  - ⚔ Castanos (lost 450) vs Wellesley (lost 806) — The walls were not enough. Castanos broke through Wellesley's prepared defenses. — The Line Holds +15% (Wellesley)
  - ⚔ Castanos (lost 434) vs Wellesley (lost 577) — Stalemate. Wellesley and Castanos glare at each other across the field. — The Line Holds +15% (Wellesley)
  - verbs: attack×2, garrison×1, move×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 6167 · net +413 · threat 53 · provinces 23 (+0) · ceiling 9848 · army 86836 · vassals Holland 91 · Switzerland 85
  - NET income 1988 · trade 612 · admin 50 · tribute 337 · upkeep 1596 · charges 466 · occupation 40 · blockade 382 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Franconia stays ours by the treaty — titled. Status quo: Berry, Gascony, Guyenne, Limousin, Lyonnais and Provence stay Austrian by the treaty. Status quo: Andalusia stays British by the treaty. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 8396 · net +2203 · threat 24 · provinces 23 (+0) · ceiling 191916 · army 95711 · vassals Holland 89 · Switzerland 84
  - NET income 2028 · trade 612 · admin 50 · tribute 337 · upkeep 728 · charges 76 · occupation 20
- DISPATCH: Sire — Berry, Gascony, Guyenne and 3 more lie in enemy hands. Austria holds them.
  - RAIL status_quo_conceded: Berry, Gascony, Guyenne, Limousin, Lyonnais and Provence — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,572 gold. Prussia is now free to look elsewhere.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL +2 more
  - TURN EVENTS 8
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: And Russia stirs at its own design.
- DIPLO +8 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 53 to 26.
  - LOG ai_ai_proposal_refused: 18 approaches from Bavaria and Austria are rebuffed (open borders agreement)

## Turn 13 — Late March 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Munich to Franconia
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 10274 · net +2080 · threat 22 · provinces 23 (+0) · ceiling 183583 · army 94619 · vassals Holland 98 · Switzerland 83
  - NET income 2032 · trade 612 · admin 50 · tribute 225 · upkeep 720 · charges 99 · occupation 20
- DISPATCH: Sire — 3 turns now with Berry, Gascony, Guyenne and 3 more in enemy hands. The country counts every one of them.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG ai_ai_proposal_refused: 15 approaches from Austria and Bavaria are rebuffed (open borders agreement)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 12358 · net +2059 · threat 20 · provinces 23 (+0) · ceiling 183916 · army 93560 · vassals Holland 97 · Switzerland 82
  - NET income 2036 · trade 612 · admin 50 · tribute 225 · upkeep 720 · charges 124 · occupation 20
- DISPATCH: Sire — Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG ai_ai_proposal_refused: 11 courts rebuff Bavaria (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #14 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 14212 · net +1832 · threat 18 · provinces 23 (+0) · ceiling 166833 · army 92533 · vassals Holland 96 · Switzerland 92
  - NET income 2040 · trade 612 · admin 50 · upkeep 704 · charges 146 · occupation 20
- DISPATCH: Sire — Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Ney can already reach the body of the realm from where…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 16056 · net +1822 · threat 16 · provinces 23 (+0) · ceiling 167833 · army 91536 · vassals Holland 95 · Switzerland 92
  - NET income 2044 · trade 612 · admin 50 · upkeep 696 · charges 168 · occupation 20
- DISPATCH: Sire — Massena is no nearer home, and the safe passage leaves 2 turns to spare. After that his corps will be interned where it stands.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Bavaria (open borders agreement)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 17890 · net +1812 · threat 14 · provinces 23 (+0) · ceiling 168833 · army 90569 · vassals Holland 94 · Switzerland 92
  - NET income 2048 · trade 612 · admin 50 · upkeep 688 · charges 190 · occupation 20
- DISPATCH: Sire — Massena is no nearer home, and the safe passage leaves one turn to spare. After that his corps will be interned where it stands.
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 33% -> 34%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- SPENT 170g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 19497 · net +1781 · threat 12 · provinces 23 (+0) · ceiling 167833 · army 92632 · vassals Holland 93 · Switzerland 92
  - NET income 2052 · trade 612 · admin 50 · upkeep 704 · charges 209 · occupation 20
- DISPATCH: Sire — Massena is no nearer home, and the safe passage leaves no turn to spare — he must march today. After that his corps will be interned where it stands.
  - TURN EVENTS 5
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Swabia to Franconia
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 21298 · net +1963 · threat 10 · provinces 23 (+0) · ceiling 184833 · army 67266 · vassals Holland 92 · Switzerland 92
  - NET income 2056 · trade 612 · admin 50 · upkeep 504 · charges 231 · occupation 20
- DISPATCH: Sire — Marshal Massena's corps was interned at Milan by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
  - saved `CMD-ULM_t20` → Game saved: CMD-ULM_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 23265 · net +2280 · threat 8 · provinces 23 (+0) · ceiling 213250 · army 65769 · vassals Holland 91 · Switzerland 92
  - NET income 2060 · trade 612 · admin 50 · tribute 337 · upkeep 504 · charges 255 · occupation 20
- DISPATCH: Sire — the establishment stands 51,731 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Franconia (field levy — no depot; capped at 3,000) (recruitment is drafted in fix…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 25175 · net +2253 · threat 5 · provinces 23 (+0) · ceiling 212916 · army 67223 · vassals Holland 90 · Switzerland 92
  - NET income 2064 · trade 612 · admin 50 · tribute 337 · upkeep 512 · charges 278 · occupation 20
- DISPATCH: Sire — the enemy has held Berry, Gascony, Guyenne and 3 more 11 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_auto_downgrade)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 37% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 22 — Early August 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (90 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 27103 · net +2130 · threat 2 · provinces 23 (+0) · ceiling 204583 · army 65718 · vassals Holland 100 · Switzerland 92
  - NET income 2068 · trade 612 · admin 50 · tribute 225 · upkeep 504 · charges 301 · occupation 20
- DISPATCH: Sire — Britain, Russia, Austria, Prussia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Prussia: Talleyrand brings her…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 29245 · net +2117 · threat 0 · provinces 23 (+0) · ceiling 205583 · army 64254 · vassals Holland 100 · Switzerland 92
  - NET income 2072 · trade 612 · admin 50 · tribute 225 · upkeep 496 · charges 326 · occupation 20
- DISPATCH: Sire — Austria enacts the Jäger Battalions — infantry drafts muster at +10 morale.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 31382 · net +2111 · threat 0 · provinces 23 (+0) · ceiling 207250 · army 62830 · vassals Holland 100 · Switzerland 92
  - NET income 2076 · trade 612 · admin 50 · tribute 225 · upkeep 480 · charges 352 · occupation 20
- DISPATCH: Sire — Russia enacts the War Ministry under Arakcheev — +5 morale from every drill.
  - TURN EVENTS 2
- COURTS: The court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 33505 · net +2097 · threat 0 · provinces 23 (+0) · ceiling 208250 · army 61445 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 225 · upkeep 472 · charges 378 · occupation 20
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 35610 · net +2080 · threat 0 · provinces 23 (+0) · ceiling 208916 · army 60096 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 225 · upkeep 464 · charges 403 · occupation 20
- DISPATCH: Sire — Austria enacts the New Infantry Regulations — +5 morale from every drill.
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 80%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 37460 · net +2050 · threat 0 · provinces 23 (+0) · ceiling 208250 · army 61696 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 225 · upkeep 472 · charges 425 · occupation 20
- DISPATCH: Sire — the court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
  - TURN EVENTS 3
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 39518 · net +2033 · threat 0 · provinces 23 (+0) · ceiling 208916 · army 60333 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 225 · upkeep 464 · charges 450 · occupation 20
- DISPATCH: Sire — Britain, Russia, Austria and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 i…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 41567 · net +2362 · threat 0 · provinces 23 (+0) · ceiling 238333 · army 59007 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 562 · upkeep 448 · charges 474 · occupation 20
- DISPATCH: Sire — Prussia enacts the Military Reorganisation Commission — +5 morale from every drill.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 54% -> 51%
  - saved `CMD-ULM_t30` → Game saved: CMD-ULM_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- SPENT 170g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 43728 · net +2328 · threat 0 · provinces 23 (+0) · ceiling 237666 · army 60627 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 562 · upkeep 456 · charges 500 · occupation 20
- DISPATCH: Sire — the court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 46064 · net +2308 · threat 0 · provinces 23 (+0) · ceiling 238333 · army 59285 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 562 · upkeep 448 · charges 528 · occupation 20
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 48380 · net +2288 · threat 0 · provinces 23 (+0) · ceiling 239000 · army 57981 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 562 · upkeep 440 · charges 556 · occupation 20
- DISPATCH: Sire — the court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Franconia (field levy — no depot; capped at 3,000) (recruitment is drafted in fix…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 50294 · net +2257 · threat 0 · provinces 23 (+0) · ceiling 238333 · army 59622 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 612 · admin 50 · tribute 562 · upkeep 448 · charges 579 · occupation 20
- DISPATCH: Sire — Britain, Russia, Austria and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 i…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 52521 · net +2200 · threat 0 · provinces 23 (+0) · ceiling 235833 · army 58300 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 574 · admin 50 · tribute 562 · upkeep 440 · charges 606 · occupation 20
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
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 54729 · net +2182 · threat 0 · provinces 23 (+0) · ceiling 236500 · army 57015 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 574 · admin 50 · tribute 562 · upkeep 432 · charges 632 · occupation 20
- DISPATCH: Sire — the establishment stands 60,485 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 56919 · net +2163 · threat 0 · provinces 23 (+0) · ceiling 237166 · army 55764 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 574 · admin 50 · tribute 562 · upkeep 424 · charges 659 · occupation 20
- DISPATCH: Sire — the enemy has held Berry, Gascony, Guyenne and 3 more 26 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over The Gulf and the Straits — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 59098 · net +2153 · threat 0 · provinces 23 (+0) · ceiling 238500 · army 54549 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 574 · admin 50 · tribute 562 · upkeep 408 · charges 685 · occupation 20
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 61259 · net +2135 · threat 0 · provinces 23 (+0) · ceiling 239166 · army 53367 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 574 · admin 50 · tribute 562 · upkeep 400 · charges 711 · occupation 20
- DISPATCH: Sire — the court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 81%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 63156 · net +2097 · threat 0 · provinces 23 (+0) · ceiling 237833 · army 55128 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 574 · admin 50 · tribute 562 · upkeep 416 · charges 733 · occupation 20
- DISPATCH: Sire — the court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
  - TURN EVENTS 2
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-ULM_t40` → Game saved: CMD-ULM_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 65261 · net +2079 · threat 0 · provinces 23 (+0) · ceiling 238500 · army 53923 · vassals Holland 100 · Switzerland 92
  - NET income 2080 · trade 574 · admin 50 · tribute 562 · upkeep 408 · charges 759 · occupation 20
- DISPATCH: Sire — Britain, Russia, Austria and 2 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Sweden: Talleyrand brings her to −10 in…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 200 · popups 35 · battles 15
