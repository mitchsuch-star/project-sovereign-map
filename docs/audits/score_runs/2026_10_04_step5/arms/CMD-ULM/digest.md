# Playtest digest — CMD-ULM

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `f3ce1b57a0d2` (dirty) · content `170d75572bda` · driver `97a08b1cbe43`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 85,373 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2333, own corps) vs Mack (lost 16826) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc…
  - ⚔ Archduke Charles (lost 2505) vs Bernadotte (lost 5102, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 1624 · net +1481 · threat 72 · provinces 28 · ceiling 32854 · army 174014 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2156 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,102 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,797; expect about 93,967 with the corps likely to arrive, up to 105,598 if all march) vs Mack (substantial force) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 749, own corps) vs Mack (lost 19011) — Davout, Massena and Napoleon arrived to reinforce Ney, but Teulie failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,091; expect about 36,938 with the corps likely to arrive, up to 44,171 if all march) vs Mack (substantial force) at Tyrol — the balance of force look…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1793, own corps) vs Archduke John (lost 3165) — Reinforcement from Ney and Teulie kept Davout standing, Sire — but neither side yielded the ground. — The corps system brought Ney in. — Berthier: the corps marched apart and arrived together.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Bernadotte. Casualties:… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha… · Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Murat. Casualties: Archduke Charl…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,397 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 919) vs Bernadotte (lost 7184) — A grievous defeat for Bernadotte, Sire. The losses are severe. And Bernadotte was taken on that field — Austria holds h…
  - ⚔ Archduke Charles (lost 1555) vs Deroy (lost 7979) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2029) vs Murat (lost 6819) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Naples open borders · Portugal open borders
- LEDGER treasury 2943 · net +2211 · threat 78 · provinces 28 (+0) · ceiling 25780 · army 144263 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 92
  - NET income 2575 · trade 425 · admin 50 · tribute 937 · upkeep 1264 · charges 91 · contributions 65 · blockade 266 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- COURTS: The court of Prussia eases over The Hanoverian Prize — service to the strong is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Naples: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (15,660; expect about 92,892 with the corps likely to arrive, up to 101,268 if all march) vs Mack (14,087 men) at Tyrol — the balance of force looks favorab…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 393, own corps) vs Mack (lost 13431, own corps) — Davout, Massena, Napoleon and Teulie's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was ta… — The corps system brought Napoleon in. — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (166 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 632 gold (×3 at war) (×1.05 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 632g on this turn's orders
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Murat. Casualties: Archduke… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha…
  - 🏴 Austria: Casualties: Archduke Charles 1,437, Murat's army 9,834. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - ⚔ Archduke Charles (lost 1437) vs Murat (lost 7393, own corps) — Lannes arrived to reinforce Murat, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 567) vs Deroy (lost 6675) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×2, move×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4356 · net +2269 · threat 88 · provinces 29 (+1) · ceiling 25056 · army 129477 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 89
  - NET income 2565 · trade 475 · admin 50 · tribute 937 · upkeep 1008 · charges 258 · occupation 104 · blockade 298 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps sta…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 10
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Deroy. Casualties: Arch…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,089 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 133) vs Deroy (lost 3158) — A grievous defeat for Deroy, Sire. The losses are severe.
  - verbs: attack×1, move×1, fortify×1, wait×1
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6817 · net +2082 · threat 86 · provinces 28 (-1) · ceiling 25271 · army 123856 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 87
  - NET income 2542 · trade 550 · admin 50 · tribute 937 · upkeep 968 · charges 543 · occupation 52 · blockade 344 · admiralty 90
- DISPATCH: Sire — Franche-Comte lies in enemy hands. Austria holds it.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (13,222; expect about 63,035 with the corps likely to arrive, up to 69,965 if all march) vs Archduke Charles (34,156 men) at Franconia — the balance of forc…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1162, own corps) vs Archduke Charles (lost 5003) — Reinforcement from Massena, Napoleon and Teulie kept Ney standing, Sire — but neither side yielded the ground. — The corps system brought Teulie in.
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia. Swabia falls to France! (was Austria) (950 lost to march)
  - POPUP capture_choice[capture]: Swabia, Soult → secure
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (73 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 8975 · net +1955 · threat 86 · provinces 29 (+1) · ceiling 25479 · army 115030 · vassals Holland 95 · Kingdom of Italy 94 · Switzerland 85
  - NET income 2631 · trade 612 · admin 50 · tribute 937 · upkeep 896 · charges 825 · occupation 82 · blockade 382 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Massena, Napoleon and Teulie stand 69,063 men at Tyrol, which feeds 30,000. 39,063 too many. 14,616 men lost in 3 turns. A supply depot at Tyrol would ease it; Milan can feed 75,0…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #9 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #12 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +6 (94 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 5g a turn — 99g of income forfeited, 30g of occupation relieved, 74g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke John is at Bohemia, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 35/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, move×1, form_square×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10859 · net +1632 · threat 84 · provinces 28 (-1) · ceiling 24277 · army 111251 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 83
  - NET income 2533 · trade 612 · admin 50 · tribute 1012 · upkeep 864 · charges 1077 · contributions 110 · occupation 52 · blockade 382 · admiralty 90
- DISPATCH: Sire — 3 turns now with Franche-Comte in enemy hands. The country counts every one of them.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +3 medium/low (enemy_marshal_commissioned, law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
  - MAILBOX #10 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (10,663; expect about 64,350 with the corps likely to arrive, up to 71,288 if all march) vs Archduke Charles (29,153 men) at Franconia — the balance of forc…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 809, own corps) vs Archduke Charles (lost 5021, own corps) — Reinforcements from Davout, Massena, Napoleon and Teulie bolstered Ney's position — though Soult never arrived, Sire.
- CMD `Davout, move to Bohemia` → ✗ Cannot advance while engaged with Archduke Charles and Archduke John at Franconia. He may fall back to friendly ground — Swabia — or fight.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (7,243; expect about 44,795 with the corps likely to arrive, up to 48,551 if all march) vs Archduke Charles (24,132 men) at Franconia — the balance of for…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 1005, own corps) vs Archduke Charles (lost 3495, own corps) — Soult never reached the guns. The battle was decided without them, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12064 · net +1387 · threat 85 · provinces 28 (+0) · ceiling 22797 · army 101747 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2582 · trade 612 · admin 50 · tribute 789 · upkeep 784 · charges 1300 · contributions 110 · requisitions 50 · occupation 30 · blockade 382 · admiralty 90
- DISPATCH: Sire — Ney, crowned five turns ago, has been driven back.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 5
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 5 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.) → trust
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 2). Moved to Tyrol. Route: Tyrol -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 13454 · net +1174 · threat 83 · provinces 28 (+0) · ceiling 22317 · army 101017 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2584 · trade 612 · admin 50 · tribute 790 · upkeep 784 · charges 1516 · contributions 110 · requisitions 50 · occupation 30 · blockade 382 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 1…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Massena holds the line. Casualties: Archduke Charles 3,680, Massena's ar…
  - ⚔ Archduke Charles (lost 3680) vs Massena (lost 1706, own corps) — Napoleon and Teulie's timely arrival bolstered Massena's position. Well-coordinated, Sire.
  - verbs: attack×1
- ORDER Massena [completed]: Massena arrives at Milan. Massena: "It is done. Point me at something that shoots back, Sire."
- LEDGER treasury 13548 · net +1058 · threat 81 · provinces 28 (+0) · ceiling 21276 · army 101855 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2586 · trade 612 · admin 50 · tribute 775 · upkeep 784 · charges 1579 · contributions 150 · requisitions 50 · occupation 30 · blockade 382 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +6 medium/low (law_enacted_abroad ×3, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Swabia to Franconia. Franconia falls to France! (was Austria) (97 lost to march)
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, fortify` → ✗ Davout is already fortified at Franconia (+12% defense).
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich.
  - saved `CMD-ULM_t10` → Game saved: CMD-ULM_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John launches a devastating assault! Napoleon holds the line. Casualties: Archduke John 5,213, Napoleon's army…
  - ⚔ Archduke John (lost 5213) vs Napoleon (lost 179, own corps) — Ney and Massena arrived to reinforce Napoleon! The timely arrival swung the battle in our favor, Sire. — Berthier: the corps marched apart and arrived together.
  - verbs: naval_expedition×1, attack×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 14515 · net +835 · threat 81 · provinces 29 (+1) · ceiling 20461 · army 99756 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2644 · trade 612 · admin 50 · tribute 769 · upkeep 776 · charges 1757 · contributions 150 · occupation 85 · blockade 382 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 3279 gold.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria

## Turn 11 — Late February 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #16 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Franconia and Swabia stay ours by the treaty — titled. Status quo: Franche-Comte stays Austrian by the treaty. Status quo: Andalusia stays British by the treaty. Status quo: Tyrol stays ours by the treaty — titled. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Lorraine to Franconia (92 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: Holland, client_petition #17 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 20362 · net +2123 · threat 43 · provinces 29 (+0) · ceiling 70904 · army 103576 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2648 · trade 648 · admin 50 · tribute 433 · upkeep 800 · charges 771 · occupation 85
- DISPATCH: Sire — Ney, Massena and Napoleon stand 31,596 men at Tyrol, which feeds 30,000. 1,596 too many. 2,504 men lost in 2 turns. Kingdom of Italy's magazines feed us as our own — the army is simply too lar…
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: Gold indemnity: 3279 gold from Britain to France.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 7
- COURTS: The court of Sardinia eases over The House of Savoy Restored — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- DIPLO +11 medium/low (diplomatic_coalition_dissolved, status_quo_titled ×2, diplomatic_dp_regen, diplomatic_vassal_contingent ×2, blockade_broken ×3, agenda_shift ×2)
  - LOG ai_ai_proposal_refused: 14 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 81 to 40.
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 15% -> 19%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22888 · net +2718 · threat 45 · provinces 29 (+0) · ceiling 249333 · army 105920 · vassals Holland 99 · Kingdom of Italy 99 · Switzerland 90
  - NET income 2714 · trade 648 · admin 50 · tribute 435 · upkeep 824 · charges 250 · occupation 55
- DISPATCH: Sire — Ney, Massena and Napoleon stand 30,940 men at Tyrol, which feeds 30,000. 940 too many. 3,160 men lost in 3 turns. Kingdom of Italy's magazines feed us as our own — the army is simply too large…
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,572 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  -     ↳ refused: The armistice with Austria holds for 3 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✗ Davout is already in Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 25622 · net +2701 · threat 45 · provinces 29 (+0) · ceiling 250666 · army 105288 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 89
  - NET income 2720 · trade 648 · admin 50 · tribute 437 · upkeep 816 · charges 283 · occupation 55
- DISPATCH: Sire — Marshal Massena's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 14 — Early April 1806
  - MAILBOX #13 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #19 → grant the petition
  - POPUP proposal_result: Franconia is ceded to the Kingdom of Italy. Loyalty +2 (98 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. Our net rises by 16g a turn — 96g of income forfeited, 40g of occupation relieved, 72g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Tyr…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Tyrol and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 28367 · net +2937 · threat 45 · provinces 28 (-1) · ceiling 273083 · army 104678 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 88
  - NET income 2627 · trade 648 · admin 50 · tribute 759 · upkeep 816 · charges 316 · occupation 15
- DISPATCH: Sire — Marshal Massena's household goes unpaid. His patience erodes with his purse.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,224g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 11
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 31073 · net +2897 · threat 45 · provinces 28 (+0) · ceiling 272416 · army 107086 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2630 · trade 648 · admin 50 · tribute 764 · upkeep 832 · charges 348 · occupation 15
- DISPATCH: Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, coercive_demand)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 16 — Early May 1806
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 33795 · net +2689 · threat 45 · provinces 28 (+0) · ceiling 257833 · army 106505 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2633 · trade 648 · admin 50 · tribute 570 · upkeep 816 · charges 381 · occupation 15
- DISPATCH: Sire — 7 turns without settlement on Marshal Massena. A rente would close it today; the arrears will not close themselves.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL broken_bargain: The compact with Sweden lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 8
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: And Britain and Russia stir at their own designs.
- DIPLO +3 medium/low (diplomatic_dp_regen, blockade_begins, diplomatic_relation_shift)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 36492 · net +2665 · threat 45 · provinces 28 (+0) · ceiling 258500 · army 105936 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2636 · trade 648 · admin 50 · tribute 575 · upkeep 816 · charges 413 · occupation 15
- DISPATCH: Sire — Marshal Massena's claim is 8 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 39165 · net +2641 · threat 45 · provinces 28 (+0) · ceiling 259166 · army 105378 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2639 · trade 648 · admin 50 · tribute 580 · upkeep 816 · charges 445 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte 15 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Karelia. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes begins marching to Franconia (distance: 2). Moved to Swabia. Route: Swabia -> Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 1 action unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [active]: Lannes is marching to Franconia (2 turns remaining).
- LEDGER treasury 41822 · net +2962 · threat 45 · provinces 28 (+0) · ceiling 288583 · army 104831 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2642 · trade 648 · admin 50 · tribute 922 · upkeep 808 · charges 477 · occupation 15
- DISPATCH: Sire — Marshal Massena's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Karelia — Russia is not forgiven

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-ULM_t20` → Game saved: CMD-ULM_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [completed]: Lannes arrives at Franconia. Lannes: "Done — and I trust the next order has more fire in it."
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 44793 · net +2935 · threat 45 · provinces 28 (+0) · ceiling 289333 · army 104130 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2645 · trade 648 · admin 50 · tribute 928 · upkeep 808 · charges 513 · occupation 15
- DISPATCH: Sire — Marshal Massena's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 21 — Late July 1806
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #21 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 47399 · net +2575 · threat 45 · provinces 28 (+0) · ceiling 261916 · army 103605 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2648 · trade 648 · admin 50 · tribute 596 · upkeep 808 · charges 544 · occupation 15
- DISPATCH: Sire — the enemy has held Franche-Comte 18 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
  - MAILBOX #16 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #22 → grant the petition
  - POPUP proposal_result: Swabia is ceded to the Kingdom of Italy. Loyalty +0 (100 → 100, already full); bond 40 → 40 (+2 a turn). Cost: 1 DP. Our net falls by 20g a turn — 138g of income forfeited, 15g of occupation relieved, 103g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 49970 · net +2540 · threat 45 · provinces 27 (-1) · ceiling 261583 · army 103090 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 707 · upkeep 800 · charges 575
- DISPATCH: Sire — Marshal Massena's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 52525 · net +2749 · threat 45 · provinces 27 (+0) · ceiling 281583 · army 102586 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 939 · upkeep 792 · charges 606
- DISPATCH: Sire — Marshal Massena's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 55282 · net +2724 · threat 45 · provinces 27 (+0) · ceiling 282250 · army 102092 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 947 · upkeep 792 · charges 639
- DISPATCH: Sire — the enemy has held Franche-Comte 21 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 58021 · net +2706 · threat 45 · provinces 27 (+0) · ceiling 283500 · army 101608 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 954 · upkeep 784 · charges 672
- DISPATCH: Sire — Marshal Massena's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 60733 · net +2680 · threat 45 · provinces 27 (+0) · ceiling 284000 · army 101134 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 960 · upkeep 784 · charges 704
- DISPATCH: Sire — Marshal Massena's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 63416 · net +2651 · threat 45 · provinces 27 (+0) · ceiling 284250 · army 100669 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 963 · upkeep 784 · charges 736
- DISPATCH: Sire — the enemy has held Franche-Comte 24 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 66070 · net +2959 · threat 45 · provinces 27 (+0) · ceiling 312583 · army 100214 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 1303 · upkeep 784 · charges 768
- DISPATCH: Sire — Marshal Massena's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 69048 · net +2942 · threat 49 · provinces 27 (+0) · ceiling 314166 · army 99767 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 1306 · upkeep 768 · charges 804
- DISPATCH: Sire — Marshal Massena's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-ULM_t30` → Game saved: CMD-ULM_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 72001 · net +2917 · threat 53 · provinces 27 (+0) · ceiling 315083 · army 99330 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 1309 · upkeep 760 · charges 840
- DISPATCH: Sire — the enemy has held Franche-Comte 27 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 74921 · net +2885 · threat 57 · provinces 27 (+0) · ceiling 315333 · army 98901 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 1312 · upkeep 760 · charges 875
- DISPATCH: Sire — Marshal Massena's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 77806 · net +2851 · threat 60 · provinces 27 (+0) · ceiling 315333 · army 98480 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 1312 · upkeep 760 · charges 909
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: Austria rebuffs Britain (defensive alliance)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 80665 · net +2825 · threat 58 · provinces 27 (+0) · ceiling 316000 · army 98068 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 648 · admin 50 · tribute 1312 · upkeep 752 · charges 943
- DISPATCH: Sire — Marshal Massena's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, naval_expedition×1
- LEDGER treasury 83452 · net +2753 · threat 56 · provinces 27 (+0) · ceiling 312833 · army 97664 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 610 · admin 50 · tribute 1312 · upkeep 752 · charges 977
- DISPATCH: Sire — Marshal Massena's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 14,044 men ashore at Stockholm.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG ai_ai_proposal_refused: Austria and Naples rebuff Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 12 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (500g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Britain (Defensive Alliance)
  - LOG ai_ai_proposal_refused: 12 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 15 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 84091 · net +356 · threat 54 · provinces 27 (+0) · ceiling 94187 · army 97268 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2510 · trade 574 · admin 50 · tribute 1312 · upkeep 752 · charges 2889 · blockade 359 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL expedition_landed: THE LANDING: Bennigsen has put 4,901 men ashore at Lapland.
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +6 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: And Britain stirs at its own design.
- DIPLO +16 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken, cs_tier_shift, blockade_begins ×4, agenda_shift, diplomatic_relation_shift ×5)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).
  - LOG coalition_declared: The Fourth Austrian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia, Sweden
  - LOG third_party_peace: THE CONGRESS: Russia and Sweden make peace without France

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✓ Massena challenges the order: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Trust him and he will attack …
  - POPUP objection: Massena, Massena challenges the order: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Trust him and he will attack Archduke Charles at Bohemia instead.) → trust
  - ↳ MUSTER — Massena (11,395; expect about 30,047 with the corps likely to arrive, up to 32,609 if all march) vs Archduke Charles (large force) at Bohemia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 3355, own corps) vs Archduke Charles (lost 2356) — Lannes, Murat and Napoleon marched to Massena's guns as ordered. It was not enough. — The corps system brought Murat in. — The corps system brought Napoleon in. — Berthier: the corps marched apart and arrived together.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles holds them at Tyrol while allies attack from Bohemia! (+1 coordination) · Archduke John's forces advance steadily. Davout holds the line. Casualties: Archduke John 2,192, Davout 1,451. Both arm… · ArchdukeCharles holds them at Tyrol while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: [!] No word came for Ney, cornered at Tyrol — the enemy did not wait. [!] MARSHAL CAPTURED — Ney is taken by Austria at Tyrol!
  - ⚔ Archduke Charles (lost 550) vs Ney (lost 2674) — Ney's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Archduke Charles (lost 129) vs Ney (lost 1513) — The hills were ours, but Archduke Charles took them. Ney's position was overrun. And Ney was taken on that field — Aust… — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke John (lost 2192) vs Davout (lost 1451) — Davout stood alone, Sire. Soult never came.
  - ⚔ Archduke Charles (lost 318) vs Lannes (lost 6194) — The hills were ours, but Archduke Charles took them. Lannes's position was overrun. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: attack×4, move×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → accept_settlement_offer
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #23 already answered this chain)
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 79655 · net -3390 · threat 52 · provinces 27 (+0) · ceiling 40232 · army 74548 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2510 · trade 574 · admin 50 · tribute 1187 · upkeep 584 · charges 6678 · blockade 359 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL settlement_offer_arrival: Russia has offered terms to settle Russia vs Sweden.
  - TURN EVENTS 10
- DIPLO +6 medium/low (diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, paymaster_subsidy)

## Turn 37 — Late March 1807
  - MAILBOX #17 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → request_settlement_revision
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #23 already answered this chain)
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke John delivers an effective strike. Archduke John gains the advantage over Murat. Casualties: Archduke John 2,1… · ArchdukeJohn holds them at Tyrol while allies attack from Bohemia! (+1 coordination)
  - ⚔ Archduke John (lost 2168) vs Murat (lost 1634, own corps) — Davout and Teulie marched to Murat's guns as ordered. It was not enough. — Berthier: the corps marched apart and arrived together.
  - ⚔ Archduke John (lost 58) vs Napoleon (lost 551) — The line gave way. Napoleon is falling back, and not in good order.
  - verbs: attack×2, retreat×1, stance_change×1, recruit×1
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Tyrol — 833 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Tyrol — 833 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 75803 · net -5007 · threat 50 · provinces 27 (+0) · ceiling 31567 · army 69721 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2510 · trade 574 · admin 50 · tribute 1190 · upkeep 528 · charges 8354 · blockade 359 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Tyrol. He must reform before he fights again.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).

## Turn 38 — Early April 1807
  - MAILBOX #17 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #23 → reject_settlement_offer
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Lannes, fortify` → ✗ Lannes is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn takes Tyrol where he stands! Captured: KingdomOfItaly → Austria · Archduke John faces a difficult fight. Brutal stalemate between Archduke John and Teulie. Heavy casualties on both side…
  - 🏴 Austria: ArchdukeJohn takes Tyrol where he stands! Captured: KingdomOfItaly → Austria
  - ⚔ Archduke John (lost 1536) vs Teulie (lost 1730) — Neither Teulie nor Archduke John could claim the field. The armies remain locked.
  - verbs: attack×2, form_square×1
- LEDGER treasury 70646 · net -4713 · threat 48 · provinces 27 (+0) · ceiling 30430 · army 68794 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2510 · trade 574 · admin 50 · tribute 1175 · upkeep 528 · charges 8045 · blockade 359 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke John is at Tyrol, just one region away.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke John delivers an effective strike. Archduke John gains the advantage over Teulie. Casualties: Archduke John 99… · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Davout. Casualties: Archduke C… · ArchdukeJohn flanks from Tyrol while allies attack from Bohemia! (+1 coordination)
  - ⚔ Archduke John (lost 992) vs Teulie (lost 2466) — A standard affair. Nothing unusual to report.
  - ⚔ Archduke Charles (lost 1336) vs Davout (lost 2595, own corps) — Davout fought without Soult's support. The roads, or the will, proved insufficient.
  - ⚔ Archduke John (lost 80, own corps) vs Murat (lost 3282) — Where was Soult? Murat held the field alone — reinforcement never came.
  - verbs: attack×3, move×1
- ORDER Murat [awaiting_response]: Murat is cornered at Franconia with 1,928 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Franconia with 1,928 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 64696 · net -4909 · threat 46 · provinces 27 (+0) · ceiling 27046 · army 56691 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2510 · trade 574 · admin 50 · tribute 1013 · upkeep 432 · charges 8175 · blockade 359 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 40 — Early May 1807
  - MAILBOX #18 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #24 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
  - saved `CMD-ULM_t40` → Game saved: CMD-ULM_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 53287 · net -986 · threat 44 · provinces 27 (+0) · ceiling 41485 · army 69542 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2510 · trade 586 · admin 50 · tribute 1123 · upkeep 512 · charges 4287 · blockade 366 · admiralty 90
- DISPATCH: Sire — Marshal Murat has been taken. Austria holds him prisoner.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - TURN EVENTS 10
- DIPLO +7 medium/low (status_quo_titled, diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade ×2, paymaster_subsidy)
  - LOG coalition_member_left: Austria has left the coalition.

---
finished: **completed** · commands 200 · popups 57 · battles 27
