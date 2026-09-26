# Playtest digest — prd1b-cmd-austerlitz

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `759414f922cb` (dirty) · content `f797f1101c51` · driver `196c4ee545c1`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1984, own corps) vs Mack (lost 14668) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's attack meets fierce resistance. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Arch…
  - ⚔ Archduke Charles (lost 2305) vs Bernadotte (lost 2855, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2491 · net +2342 · threat 75 · provinces 28 · ceiling 55220 · army 173887 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 3400 · trade 400 · admin 50 · tribute 937 · upkeep 2134 · charges 21 · blockade 200 · admiralty 90
- DISPATCH: Supply cost you 1,854 men, at Franconia and Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,462; expect about 91,455 with the corps likely to arrive, up to 102,370 if all march) vs Mack (substantial force) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 508, own corps) vs Mack (lost 22412) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,385; expect about 27,191 with the corps likely to arrive, up to 32,599 if all march) vs Mack (substantial force) at Tyrol — the balance of force look…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1797, own corps) vs Archduke John (lost 2801) — Reinforcement from Ney kept Davout standing, Sire — but neither side yielded the ground.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,400 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 964) vs Bernadotte (lost 8480) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1529) vs Deroy (lost 7921) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2014) vs Murat (lost 6543) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4580 · net +2825 · threat 81 · provinces 28 (+0) · ceiling 34500 · army 147065 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 92
  - NET income 3382 · trade 450 · admin 50 · tribute 937 · upkeep 1354 · charges 243 · contributions 82 · blockade 225 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (14,366; expect about 63,246 with the corps likely to arrive, up to 86,453 if all march) vs Mack (12,704 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 276, own corps) vs Mack (lost 8400, own corps) — Davout, Massena and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was taken on t…
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (165 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 644 gold (×3 at war) (×1.07 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 644g on this turn's orders
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh… · ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl… · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination)
  - 🏴 Austria: Casualties: ArchdukeCharles 1,640, Murat's army 7,790. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 1640) vs Murat (lost 3763, own corps) — Lannes arrived to reinforce Murat, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 169) vs Bernadotte (lost 2675) — Not one corps reached Bernadotte. Ney was expected; Bernadotte fought the battle single-handed.
  - ⚔ Archduke Charles (lost 492) vs Deroy (lost 6124) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, stance_change×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6590 · net +2855 · threat 91 · provinces 29 (+1) · ceiling 33115 · army 131607 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 87
  - NET income 3355 · trade 449 · admin 50 · tribute 937 · upkeep 1024 · charges 493 · occupation 104 · blockade 225 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 10
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,777 troops. Ga…
  - verbs: attack×1, fortify×1
- LEDGER treasury 9585 · net +2570 · threat 89 · provinces 29 (+0) · ceiling 32776 · army 125944 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 85
  - NET income 3357 · trade 524 · admin 50 · tribute 919 · upkeep 984 · charges 840 · occupation 104 · blockade 262 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Bernadotte, Massena and Napoleon stand 71,354 men at Tyrol, which feeds 30,000. 41,354 too many. 9,393 men lost in 2 turns. No depot may be laid at Tyrol — region stability too lo…
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (12,203; expect about 49,228 with the corps likely to arrive, up to 54,444 if all march) vs Archduke Charles (33,720 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1122, own corps) vs Archduke Charles (lost 3527) — Reinforcement from Massena and Napoleon kept Ney standing, Sire — but neither side yielded the ground.
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (950 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (110 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 12082 · net +2419 · threat 87 · provinces 29 (+0) · ceiling 32859 · army 116186 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 83
  - NET income 3425 · trade 524 · admin 50 · tribute 923 · upkeep 896 · charges 1173 · occupation 82 · blockade 262 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Bernadotte, Massena and Napoleon stand 62,656 men at Tyrol, which feeds 30,000. 32,656 too many. 13,268 men lost in 3 turns. A supply depot at Tyrol would ease it; Milan can feed …
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 6 — Early December 1805
  - MAILBOX #8 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #10 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +6 (94 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 5g a turn — 99g of income forfeited, 30g of occupation relieved, 74g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! ArchdukeJohn is at Bohemia, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, move×1, form_square×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (81 → 91); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 14907 · net +2347 · threat 85 · provinces 28 (-1) · ceiling 41095 · army 112661 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3381 · trade 524 · admin 50 · tribute 778 · upkeep 848 · charges 1156 · occupation 30 · blockade 262 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (9,849; expect about 41,606 with the corps likely to arrive, up to 61,231 if all march) vs Archduke Charles (30,193 men) at Munich — the balance of force lo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1002, own corps) vs Archduke Charles (lost 2823) — Reinforcements from Massena and Napoleon bolstered Ney's position — though Davout and Soult never arrived, Sire.
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Tyrol to Bohemia. Bohemia falls to France! (was Austria) (149 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Davout → secure
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (10,953) vs Archduke Charles (27,370 men) at Munich — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 5913) vs Archduke Charles (lost 393) — Not one corps reached Murat. Soult was expected; Murat fought the battle single-handed.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeJohn's forces advance steadily. ArchdukeJohn gains the advantage over Lannes. Casualties: ArchdukeJohn 951, Lan…
  - ⚔ Archduke Charles (lost 269) vs Ney (lost 4466) — The toll on Ney's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke John (lost 951) vs Lannes (lost 1738) — Where was Soult? Lannes held the field alone — reinforcement never came.
  - verbs: attack×2, move×2, unfortify×1, break_square×1
- ORDER Ney [awaiting_response]: Ney is cornered at Milan with 4,337 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Milan with 4,337 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 15671 · net +1398 · threat 85 · provinces 29 (+1) · ceiling 25855 · army 91021 · vassals Holland 87 · Kingdom of Italy 97 · Switzerland 84
  - NET income 3421 · trade 524 · admin 50 · tribute 564 · upkeep 696 · charges 1875 · contributions 138 · occupation 100 · blockade 262 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout pursues Archduke Charles (at Milan). Moves to Tyrol. Davout: "I will follow — at a distance that leaves him no chance to turn on us."
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! ArchdukeJohn is at Lorraine, just one region away.
- CMD `Massena, move to Milan` → ✗ Cannot move into Milan - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn engages in solid combat. ArchdukeJohn gains the advantage over Murat. Casualties: ArchdukeJohn 220, Murat … · ArchdukeCharles marches from Milan into Piedmont unopposed! (962 lost to march) Captured: KingdomOfItaly → Austria · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,645 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,543 troops in the…
  - 🏴 Austria: ArchdukeCharles marches from Milan into Piedmont unopposed! (962 lost to march) Captured: KingdomOfItaly → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - ⚔ Archduke John (lost 220) vs Murat (lost 3105) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×4
- ORDER Davout [active]: Davout is pursuing Archduke Charles (0 turns remaining).
- ORDER Murat [awaiting_response]: Murat is cornered at Lorraine with 1,935 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Lorraine with 1,935 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 16755 · net +1070 · threat 83 · provinces 29 (+0) · ceiling 24220 · army 84006 · vassals Holland 85 · Kingdom of Italy 96 · Switzerland 81
  - NET income 3411 · trade 524 · admin 50 · tribute 415 · upkeep 640 · charges 2112 · contributions 126 · occupation 100 · blockade 262 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier checks the order of battle. 'No marshal of cavalry can reach Paris, Sire — none of ours stands within reach.' No commander of horse serves us, and none waits on…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Lorraine into Lorraine unopposed! (94 lost to march) Captured: France → Austria · ArchdukeJohn marches from Lorraine into Orleanais unopposed! (93 lost to march) Captured: France → Austria · Castanos's attack meets fierce resistance. Castanos gains the advantage over Paget. Casualties: Castanos 728, Paget 1,3… · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Lorraine into Lorraine unopposed! (94 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Lorraine into Orleanais unopposed! (93 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn moves from Orleanais to Nivernais. Nivernais falls to Austria!
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Castanos (lost 728) vs Paget (lost 1373) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - ⚔ Castanos (lost 401) vs Paget (lost 1695) — Paget's aggressive posture left the troops exposed when Castanos's attack came.
  - verbs: attack×4, move×2, fortify×1
- ORDER Davout [continues]: Davout pursues ArchdukeCharles. 0 regions away.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 17752 · net +851 · threat 80 · provinces 26 (-3) · ceiling 23564 · army 83144 · vassals Holland 85 · Kingdom of Italy 97 · Switzerland 80
  - NET income 3167 · trade 524 · admin 50 · tribute 418 · upkeep 640 · charges 2306 · requisitions 75 · occupation 85 · blockade 262 · admiralty 90
- DISPATCH: Sire — Lorraine has fallen. Enemy colours fly over French homeland soil. ArchdukeJohn's corps of 10,029 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any g…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.

## Turn 10 — Early February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Bohemia and Swabia stay ours by the treaty — titled. Status quo: Franche-Comte, Lorraine, Nivernais and Orleanais stay Austrian by the treaty. Status quo: Tyrol stays ours by the treaty — titled. Status quo: Milan and Piedmont stay Austrian by the treaty. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Ney can already reach the body of the realm from whe…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×3, unfortify×1, fortify×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 20521 · net +2316 · threat 39 · provinces 26 (+0) · ceiling 75642 · army 92030 · vassals Holland 93 · Kingdom of Italy 96 · Switzerland 79
  - NET income 3170 · trade 560 · admin 50 · tribute 110 · upkeep 712 · charges 777 · occupation 85
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 10
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, status_quo_titled ×2, diplomatic_dp_regen, blockade_broken ×3)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 80 to 40.

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is recovering from retreat (1 turn remaining) and cannot accept strategic orders.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Murat can already reach the body of the realm from w…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23535 · net +2978 · threat 38 · provinces 26 (+0) · ceiling 271666 · army 91480 · vassals Holland 92 · Kingdom of Italy 95 · Switzerland 78
  - NET income 3273 · trade 560 · admin 50 · tribute 112 · upkeep 704 · charges 258 · occupation 55
- DISPATCH: Sire — the establishment stands 33,520 men under the ordinance, and the depots hold 98,703. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 4% -> 12%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26269 · net +2924 · threat 37 · provinces 26 (+0) · ceiling 269916 · army 93940 · vassals Holland 91 · Kingdom of Italy 94 · Switzerland 77
  - NET income 3276 · trade 560 · admin 50 · tribute 112 · upkeep 728 · charges 291 · occupation 55
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 31,060 men at Paris, and nobody has gone to collect them.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG ai_ai_proposal_refused: Holland rebuffs Austria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ Murat is recovering from retreat (2 turns remaining) and cannot accept strategic orders.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Munich to Franconia (136 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 29196 · net +2892 · threat 36 · provinces 26 (+0) · ceiling 270166 · army 93276 · vassals Holland 90 · Kingdom of Italy 93 · Switzerland 76
  - NET income 3279 · trade 560 · admin 50 · tribute 112 · upkeep 728 · charges 326 · occupation 55
- DISPATCH: Sire — the levy has stood open 4 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 14 — Early April 1806
  - MAILBOX #12 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #16 → grant the petition
  - POPUP proposal_result: Bohemia is ceded to the Kingdom of Italy. Loyalty +7 (93 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. Our net rises by 3g a turn — 150g of income forfeited, 40g of occupation relieved, 113g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Tyrol and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 32102 · net +3096 · threat 35 · provinces 25 (-1) · ceiling 290083 · army 92758 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 75
  - NET income 3132 · trade 560 · admin 50 · tribute 450 · upkeep 720 · charges 361 · occupation 15
- DISPATCH: Sire — the levy has stood open 5 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 94% -> 89%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 34955 · net +3041 · threat 34 · provinces 25 (+0) · ceiling 288333 · army 95250 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 74
  - NET income 3135 · trade 560 · admin 50 · tribute 450 · upkeep 744 · charges 395 · occupation 15
- DISPATCH: Sire — Davout is no nearer home, and the safe passage runs out in 2 turns. After that his corps will be interned where it stands.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — gold is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sweden (defensive alliance)

## Turn 16 — Early May 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #17 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (74 → 84); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✓ Ney begins marching to Bohemia (distance: 6). Moved to Artois. Route: Artois -> Picardy -> Flanders -> Brabant -> Rhineland -> Frankfurt -> Berlin -> Dresden -> Bohemia.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Ney [active]: Ney is marching to Bohemia (9 turns remaining).
- LEDGER treasury 37819 · net +2830 · threat 33 · provinces 25 (+0) · ceiling 273583 · army 94753 · vassals Holland 87 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3138 · trade 560 · admin 50 · tribute 262 · upkeep 736 · charges 429 · occupation 15
- DISPATCH: Sire — Davout is no nearer home, and the safe passage runs out in 1 turn. After that his corps will be interned where it stands.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Artois. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 40660 · net +2807 · threat 32 · provinces 25 (+0) · ceiling 274500 · army 94265 · vassals Holland 86 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3141 · trade 560 · admin 50 · tribute 262 · upkeep 728 · charges 463 · occupation 15
- DISPATCH: Sire — Davout is no nearer home, and the safe passage runs out in 0 turns. After that his corps will be interned where it stands.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 43470 · net +3217 · threat 31 · provinces 25 (+0) · ceiling 311500 · army 80280 · vassals Holland 85 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3144 · trade 560 · admin 50 · tribute 599 · upkeep 624 · charges 497 · occupation 15
- DISPATCH: Sire — Marshal Davout's corps was interned at Franconia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 41% of active European bloc power.

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Artois. Army is now mobile.
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 21.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 46698 · net +3189 · threat 28 · provinces 25 (+0) · ceiling 312416 · army 79813 · vassals Holland 84 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3147 · trade 560 · admin 50 · tribute 599 · upkeep 616 · charges 536 · occupation 15
- DISPATCH: Sire — Marshal Davout's corps was interned at Franconia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #18 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (84 → 94); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Artois. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 49553 · net +2821 · threat 25 · provinces 25 (+0) · ceiling 284583 · army 79354 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 262 · upkeep 616 · charges 570 · occupation 15
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 5,000 cavalry at Paris (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is note…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- SPENT 259g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 52053 · net +2751 · threat 22 · provinces 25 (+0) · ceiling 281250 · army 83905 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 262 · upkeep 656 · charges 600 · occupation 15
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 70).
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 54812 · net +2726 · threat 19 · provinces 25 (+0) · ceiling 281916 · army 83464 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 262 · upkeep 648 · charges 633 · occupation 15
- DISPATCH: Lannes's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 57538 · net +2918 · threat 16 · provinces 25 (+0) · ceiling 300666 · army 83032 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 487 · upkeep 648 · charges 666 · occupation 15
- DISPATCH: DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 99).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat is fortified and cannot drill. Abandon fortification first.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 94%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 60209 · net +2862 · threat 13 · provinces 25 (+0) · ceiling 298666 · army 85608 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 487 · upkeep 672 · charges 698 · occupation 15
- DISPATCH: Massena's fortifications have crumbled completely!
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Artois. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 63079 · net +2836 · threat 10 · provinces 25 (+0) · ceiling 299333 · army 85193 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 487 · upkeep 664 · charges 732 · occupation 15
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 65915 · net +2802 · threat 7 · provinces 25 (+0) · ceiling 299333 · army 84787 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 487 · upkeep 664 · charges 766 · occupation 15
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 80).
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 32% -> 33%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 68470 · net +3084 · threat 4 · provinces 25 (+0) · ceiling 325416 · army 87389 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 824 · upkeep 688 · charges 797 · occupation 15
- DISPATCH: Lannes's fortifications have crumbled completely!
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 71562 · net +3055 · threat 1 · provinces 25 (+0) · ceiling 326083 · army 86998 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 824 · upkeep 680 · charges 834 · occupation 15
- DISPATCH: Lannes's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Artois. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 74617 · net +3018 · threat 0 · provinces 25 (+0) · ceiling 326083 · army 86615 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 824 · upkeep 680 · charges 871 · occupation 15
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✓ Ney recruits 10,000 infantry (nearest to capital) - Cost: 172 gold (capital discount) (Ney's intendance: +15%). Morale: 80% -> 53%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- SPENT 172g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 77360 · net +2905 · threat 0 · provinces 25 (+0) · ceiling 319416 · army 96240 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 824 · upkeep 760 · charges 904 · occupation 15
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 63).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Artois. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 80281 · net +2886 · threat 0 · provinces 25 (+0) · ceiling 320750 · army 95873 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 824 · upkeep 744 · charges 939 · occupation 15
- DISPATCH: Ney's fortifications have crumbled completely!
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Artois. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 83167 · net +2851 · threat 0 · provinces 25 (+0) · ceiling 320750 · army 95513 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 824 · upkeep 744 · charges 974 · occupation 15
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 35% of active European bloc power.

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 5,000 cavalry at Paris (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is note…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- SPENT 259g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 85698 · net +2781 · threat 0 · provinces 25 (+0) · ceiling 317416 · army 100160 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 560 · admin 50 · tribute 824 · upkeep 784 · charges 1004 · occupation 15
- DISPATCH: Lannes's fortifications have crumbled completely!
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Artois. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 88429 · net +2698 · threat 0 · provinces 25 (+0) · ceiling 313250 · army 99815 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 510 · admin 50 · tribute 824 · upkeep 784 · charges 1037 · occupation 15
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 91135 · net +2674 · threat 0 · provinces 25 (+0) · ceiling 313916 · army 99476 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 510 · admin 50 · tribute 824 · upkeep 776 · charges 1069 · occupation 15
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 73).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Artois. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 95%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 93562 · net +2621 · threat 0 · provinces 25 (+0) · ceiling 311916 · army 102144 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 510 · admin 50 · tribute 824 · upkeep 800 · charges 1098 · occupation 15
- DISPATCH: Ney's fortifications have crumbled completely!
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 96191 · net +2597 · threat 0 · provinces 25 (+0) · ceiling 312583 · army 101818 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 510 · admin 50 · tribute 824 · upkeep 792 · charges 1130 · occupation 15
- DISPATCH: Ney's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Artois. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 98788 · net +2566 · threat 0 · provinces 25 (+0) · ceiling 312583 · army 101499 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 510 · admin 50 · tribute 824 · upkeep 792 · charges 1161 · occupation 15
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
  - MAILBOX #15 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #19 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 53% -> 50%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 101115 · net +2522 · threat 0 · provinces 25 (+0) · ceiling 311250 · army 104186 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 510 · admin 50 · tribute 824 · upkeep 808 · charges 1189 · occupation 15
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Artois. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+2% defense).
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 103637 · net +2492 · threat 0 · provinces 25 (+0) · ceiling 311250 · army 103879 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3150 · trade 510 · admin 50 · tribute 824 · upkeep 808 · charges 1219 · occupation 15
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)

---
finished: **completed** · commands 200 · popups 40 · battles 19
