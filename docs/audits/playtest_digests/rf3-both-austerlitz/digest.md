# Playtest digest — rf3-both-austerlitz

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `3d1157842721` (dirty) · content `c696461ccc07` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 800.
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
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2447 · net +2294 · threat 75 · provinces 28 · ceiling 54094 · army 173887 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 3400 · trade 400 · admin 50 · tribute 937 · upkeep 2134 · charges 19 · blockade 250 · admiralty 90
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
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,507.
- CMD `enact the Anticipated Class` → ✓ The Anticipated Class is in force — enacted for 15 authority. It costs 150 gold a turn from now on. Authority 100 → 85.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,462; expect about 91,455 with the corps likely to arrive, up to 102,370 if all march) vs Mack (substantial force) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 547, own corps) vs Mack (lost 21712) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."
  - POPUP strategic_interrupt: Davout, muster_confirm, Davout halts before the order is carried out. "I can attack, Sire. I cannot promise you an army afterwards. Say the word and it is done."

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
MUSTER — Davout (22,333; expect about 27,128 with the corps likely to arrive, up to 32,524 if all march) vs Mack (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Ney: will march to the sound of the guns — may make it from the mountains at Munich in time (about 47%); order 'Ney, support Davout' and it rises to about 99%
  WILL NOT — Bernadotte: is pinned by enemies before his own front
  WILL NOT — Massena: has already marched this turn
  WILL NOT — Napoleon: has already marched this turn
  Mack does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him.
  The band weighs more than the men: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1797, own corps) vs Archduke John (lost 2794) — Reinforcement from Ney kept Davout standing, Sire — but neither side yielded the ground.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (1,394 lost to march) Swabia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1051) vs Bernadotte (lost 8166) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1668) vs Deroy (lost 7614) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2197) vs Murat (lost 6270) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4324 · net +2644 · threat 81 · provinces 28 (+0) · ceiling 32446 · army 147437 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 92
  - NET income 3382 · trade 450 · admin 50 · tribute 937 · upkeep 1354 · charges 218 · contributions 82 · blockade 281 · admiralty 90 · laws 150
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
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 4,406.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✓ The Code Abroad is in force — enacted for 15 authority. It costs 100 gold a turn from now on. Authority 90 → 75.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (14,330; expect about 63,096 with the corps likely to arrive, up to 85,057 if all march) vs Mack (13,392 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 306, own corps) vs Mack (lost 8235, own corps) — Davout, Massena and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (18,891; expect about 22,465 with the corps likely to arrive, up to 26,487 if all march) vs Mack (strength unknown) at Bohemia — the balance of force loo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 103) vs Mack (lost 3777) — Davout stood alone, Sire. Ney never came. And Mack was taken on that field — France holds him.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia falls to France! (was Austria) (165 lost to march)
  - POPUP capture_choice[capture]: Swabia, Lannes → secure
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 644 gold (×3 at war) (×1.07 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 644g on this turn's orders
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCharles … · ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl… · ArchdukeCharles holds them at Munich while allies attack from Franche-Comte! (+1 coordination)
  - 🏴 Austria: Casualties: ArchdukeCharles 1,664, Murat's army 7,355. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 1664) vs Murat (lost 3585, own corps) — Lannes arrived to reinforce Murat, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 152) vs Bernadotte (lost 2970) — Not one corps reached Bernadotte. Ney was expected; Bernadotte fought the battle single-handed.
  - ⚔ Archduke Charles (lost 583) vs Deroy (lost 5837) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, stance_change×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6055 · net +2638 · threat 94 · provinces 29 (+1) · ceiling 30656 · army 133681 · vassals Holland 95 · Kingdom of Italy 96 · Switzerland 89
  - NET income 3355 · trade 449 · admin 50 · tribute 937 · upkeep 1044 · charges 434 · requisitions 50 · occupation 104 · blockade 281 · admiralty 90 · laws 250
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 11
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 6,160.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✗ Davout cannot fortify while engaged with enemy forces! Enemy present: ArchdukeJohn. Attack or retreat first.
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,777 troops. Ga…
  - verbs: attack×1, fortify×1
- LEDGER treasury 8813 · net +2360 · threat 92 · provinces 29 (+0) · ceiling 30188 · army 129955 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 88
  - NET income 3357 · trade 524 · admin 50 · tribute 919 · upkeep 1016 · charges 752 · requisitions 50 · occupation 104 · blockade 328 · admiralty 90 · laws 250
- DISPATCH: Sire — Ney, Bernadotte, Massena and Napoleon stand 56,086 men at Tyrol, which feeds 30,000. 26,086 too many. 5,411 men lost in 2 turns. No depot may be laid at Tyrol — region stability too low (45/10…
  - TURN EVENTS 5
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 5 — Late November 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 8,813.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (12,535; expect about 50,577 with the corps likely to arrive, up to 54,860 if all march) vs Archduke Charles (33,265 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1129, own corps) vs Archduke Charles (lost 3365) — Reinforcement from Massena and Napoleon kept Ney standing, Sire — but neither side yielded the ground.
- CMD `Lannes, attack Mack` → ✗ Lannes is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (950 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (114 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 11085 · net +2221 · threat 90 · provinces 29 (+0) · ceiling 30161 · army 121958 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 87
  - NET income 3425 · trade 524 · admin 50 · tribute 923 · upkeep 944 · charges 1057 · requisitions 50 · occupation 82 · blockade 328 · admiralty 90 · laws 250
- DISPATCH: Sire — Ney, Bernadotte, Massena and Napoleon stand 49,153 men at Tyrol, which feeds 30,000. 19,153 too many. 7,490 men lost in 3 turns. A supply depot at Tyrol would ease it; Milan can feed 75,000 mo…
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 6 — Early December 1805
  - MAILBOX #8 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #10 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 5g a turn — 99g of income forfeited, 30g of occupation relieved, 74g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `enact the Staff` → ✓ The Grand Quartier Général is in force — enacted for 9,000 gold. It costs 300 gold a turn from now on. From the next refill, one more order each day.
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! ArchdukeCharles is at Munich, just one region away.
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 45/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- SPENT 9000g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (86 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 5127 · net +2569 · threat 88 · provinces 28 (-1) · ceiling 33796 · army 120014 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 3381 · trade 524 · admin 50 · tribute 778 · upkeep 936 · charges 280 · requisitions 50 · occupation 30 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — 3 turns of famine at Tyrol now. 6,623 men gone, and not one of them to the enemy. Kingdom of Italy's magazines feed us as our own — the army is simply too large for the province. Milan can fee…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 7 — Late December 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (10,510; expect about 41,235 with the corps likely to arrive, up to 44,694 if all march) vs Archduke Charles (29,900 men) at Munich — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1161, own corps) vs Archduke Charles (lost 2529) — Reinforcements from Massena and Napoleon bolstered Ney's position — though Soult never arrived, Sire.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (11,380) vs Archduke Charles (27,371 men) at Munich — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 6145) vs Archduke Charles (lost 397) — Not one corps reached Murat. Soult was expected; Murat fought the battle single-handed.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - ⚔ Archduke Charles (lost 235) vs Ney (lost 5068) — The toll on Ney's forces is heavy, Sire. This defeat will be felt.
  - verbs: unfortify×1, attack×1
- ORDER Ney [awaiting_response]: Ney is cornered at Milan with 4,235 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Milan with 4,235 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
- LEDGER treasury 6805 · net +2202 · threat 86 · provinces 28 (+0) · ceiling 24114 · army 98827 · vassals Holland 93 · Kingdom of Italy 98 · Switzerland 90
  - NET income 3383 · trade 524 · admin 50 · tribute 564 · upkeep 760 · charges 611 · requisitions 50 · occupation 30 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - TURN EVENTS 9
- DIPLO +2 medium/low (diplomatic_we_threshold, diplomatic_dp_regen)

## Turn 8 — Early January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Davout, attack Archduke Charles` → ✓ Davout pursues Archduke Charles (at Milan). Moves to Tyrol. Davout: "I will follow — at a distance that leaves him no chance to turn on us."
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Cannot move into Milan - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
- ORDER Davout [active]: Davout is pursuing Archduke Charles (0 turns remaining).
- LEDGER treasury 8991 · net +1901 · threat 84 · provinces 28 (+0) · ceiling 23564 · army 96431 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3385 · trade 524 · admin 50 · tribute 595 · upkeep 744 · charges 911 · occupation 30 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 9 — Late January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 1…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 5 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, move×1
- ORDER Davout [continues]: Davout pursues ArchdukeCharles. 0 regions away.
- LEDGER treasury 9877 · net +1689 · threat 82 · provinces 28 (+0) · ceiling 22516 · army 98452 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3417 · trade 524 · admin 50 · tribute 418 · upkeep 760 · charges 1052 · requisitions 75 · occupation 15 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Bernadotte, Massena and Napoleon have been 6 turns over what Tyrol can feed. 3,357 men. The country will ask where the army went. Kingdom of Italy's magazines feed us as our own — the army is …
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Anticipated Class` → ✗ The Anticipated Class is already in force (since turn 2).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, ma…
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos delivers an effective strike. Castanos gains the advantage over Paget. Casualties: Castanos 635, Paget 1,272. … · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Castanos (lost 635) vs Paget (lost 1272) — Paget's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Castanos (lost 292) vs Paget (lost 1370) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better.
  - verbs: attack×2, form_square×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #12 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 11581 · net +1585 · threat 80 · provinces 28 (+0) · ceiling 23162 · army 97845 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3420 · trade 524 · admin 50 · tribute 636 · upkeep 752 · charges 1310 · occupation 15 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)

## Turn 11 — Late February 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, attack Archduke John` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Murat can already reach the body of the realm from w…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 actions unused) Turn 12 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks with overwhelming force. Castanos gains the advantage over Paget. Casualties: Castanos 45, Paget 766. …
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Aragon!
  - ⚔ Castanos (lost 45) vs Paget (lost 766) — The walls were not enough. Castanos broke through Paget's prepared defenses. And Paget was taken on that field — Spain …
  - verbs: unfortify×2, move×1, attack×1, fortify×1
- ORDER Bernadotte [continues]: Bernadotte marches to Franconia. 1 region to Swabia.
- ORDER Davout [error]: Davout could not advance toward Swabia.
- ORDER Napoleon [continues]: Napoleon marches to Franconia. 1 region to Swabia.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13152 · net +1351 · threat 78 · provinces 28 (+0) · ceiling 22800 · army 97348 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3423 · trade 524 · admin 50 · tribute 642 · upkeep 744 · charges 1561 · occupation 15 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Massena is no nearer home, and the safe passage runs out in 2 turns. After that his corps will be interned where it stands.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 9 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 12 — Early March 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #14 → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace #15 → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm #16 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `enact the Code Abroad` → ✗ The Code Abroad is already in force (since turn 3).
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 17% -> 21%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 3 actions unused) Turn 13 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Bernadotte [completed]: Bernadotte arrives at Swabia. Bernadotte: "It is done. I took the liberty of posting pickets."
- ORDER Davout [completed]: Davout arrives at Swabia. Davout: "Accomplished as ordered. The army is intact."
- ORDER Napoleon [completed]: Napoleon arrives at Swabia.
- LEDGER treasury 13919 · net +1197 · threat 76 · provinces 28 (+0) · ceiling 22272 · army 98727 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3426 · trade 524 · admin 50 · tribute 646 · upkeep 760 · charges 1706 · occupation 15 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Massena is no nearer home, and the safe passage runs out in 1 turn. After that his corps will be interned where it stands.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 10 approaches rebuffed, chiefly from Prussia (open borders agreement)

## Turn 13 — Late March 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Ney, attack Archduke John` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Murat, attack Archduke John` → ✗ Cannot attack ArchdukeJohn — armistice with Austria (3 turns remaining).
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Davout can already reach the body of the realm from …
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 5 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15103 · net +1010 · threat 74 · provinces 28 (+0) · ceiling 22000 · army 97155 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3429 · trade 524 · admin 50 · tribute 652 · upkeep 744 · charges 1918 · occupation 15 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Massena is no nearer home, and the safe passage runs out in 0 turns. After that his corps will be interned where it stands.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Tyrol and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 5 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16078 · net +1230 · threat 72 · provinces 28 (+0) · ceiling 24299 · army 72686 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3432 · trade 524 · admin 50 · tribute 881 · upkeep 568 · charges 2106 · occupation 15 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Marshal Massena's corps was interned at Tyrol by Kingdom of Italy — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 15 — Late April 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- SPENT 600g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Britain armistice losing · Russia armistice losing
- LEDGER treasury 16730 · net +1086 · threat 70 · provinces 28 (+0) · ceiling 23832 · army 74118 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3435 · trade 524 · admin 50 · tribute 886 · upkeep 576 · charges 2250 · occupation 15 · blockade 328 · admiralty 90 · laws 550
- DISPATCH: Sire — Britain and Spain have made peace without us.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as service to the strong.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)

## Turn 16 — Early May 1806
  - MAILBOX #12 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #13 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #17 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Russia. Your earlier answer was not delivered; the mat…
  - POPUP diplomatic_dialogue: incoming_proposal #18 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
  - POPUP diplomatic_dialogue: Britain, armistice_losing #17 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #18 → accept
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Ney, move to Bohemia` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 2 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 17976 · net +1051 · threat 68 · provinces 28 (+0) · ceiling 24711 · army 72596 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 3438 · trade 524 · admin 50 · tribute 754 · upkeep 568 · charges 2492 · occupation 15 · admiralty 90 · laws 550
- DISPATCH: Sire — Tyrol has been taken by Austria.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy, blockade_broken ×2)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 17 — Late May 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +1 (99 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 3 actions unused) Turn 18 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 1,906 troops in the…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -95g, Kingdom of Italy -175g. Captured: KingdomOfItaly → Austria
  - verbs: attack×1, fortify×1
- LEDGER treasury 18478 · net +422 · threat 56 · provinces 28 (+0) · ceiling 21126 · army 71119 · vassals Holland 100 · Switzerland 90
  - NET income 3441 · trade 536 · admin 50 · tribute 225 · upkeep 552 · charges 2623 · occupation 15 · admiralty 90 · laws 550
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 510 gold (×3 at war) (Davout's intendance: -15%). Morale: 85% -> 77%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- SPENT 510g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, unfortify×1
- LEDGER treasury 18390 · net +379 · threat 54 · provinces 28 (+0) · ceiling 20719 · army 72597 · vassals Holland 100 · Switzerland 90
  - NET income 3444 · trade 536 · admin 50 · tribute 225 · upkeep 560 · charges 2661 · occupation 15 · admiralty 90 · laws 550
- DISPATCH: DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 31).
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 19 — Late June 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes begins marching to Franconia (distance: 2). Moved to Swabia. Route: Swabia -> Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [active]: Lannes is marching to Franconia (2 turns remaining).
- LEDGER treasury 18743 · net +295 · threat 52 · provinces 28 (+0) · ceiling 20520 · army 69954 · vassals Holland 100 · Switzerland 90
  - NET income 3447 · trade 536 · admin 50 · tribute 225 · upkeep 536 · charges 2772 · occupation 15 · admiralty 90 · laws 550
- DISPATCH: Sire — Davout, Soult, Lannes, Bernadotte and Napoleon stand 61,719 men at Swabia, which feeds 60,000. 1,719 too many. 5,642 men lost in 3 turns. A supply depot at Swabia would ease it; Rhineland can …
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)

## Turn 20 — Early July 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 6).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 5 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [completed]: Lannes arrives at Franconia. Lannes: "Done — and I trust the next order has more fire in it."
- LEDGER treasury 18165 · net -464 · threat 52 · provinces 29 (+1) · ceiling 15808 · army 68394 · vassals Holland 100 · Switzerland 90
  - NET income 3500 · trade 536 · admin 50 · tribute 225 · upkeep 528 · charges 3187 · occupation 85 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Sire — Franconia has fallen to our arms. The tricolor flies over it this morning.
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
  - TURN EVENTS 2
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as service to the strong.
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_begins ×2)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 approaches from Britain, Russia and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke John at Bohemia instead.)
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke John at Bohemia instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 3404) vs Archduke John (lost 1711) — Lannes was driven from the field. His men are scattered.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 16702 · net -181 · threat 50 · provinces 29 (+0) · ceiling 15790 · army 65723 · vassals Holland 100 · Switzerland 88
  - NET income 3500 · trade 536 · admin 50 · tribute 225 · upkeep 504 · charges 2928 · occupation 85 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Sire — Lannes's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Piedmont.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16529 · net -139 · threat 48 · provinces 29 (+0) · ceiling 15830 · army 63545 · vassals Holland 100 · Switzerland 88
  - NET income 3500 · trade 536 · admin 50 · tribute 225 · upkeep 496 · charges 2894 · occupation 85 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 87).
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 6 courts rebuff Prussia (defensive alliance)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! ArchdukeCharles is at Munich, just one region away.
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16414 · net -92 · threat 46 · provinces 29 (+0) · ceiling 15950 · army 61455 · vassals Holland 100 · Switzerland 88
  - NET income 3500 · trade 536 · admin 50 · tribute 225 · upkeep 472 · charges 2871 · occupation 85 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - TURN EVENTS 3
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 94% -> 87%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 5 actions unused) Turn 25 begins!
- SPENT 600g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Austria: ArchdukeJohn moves from Bohemia to Franconia. Franconia falls to Austria!
  - verbs: move×1
- LEDGER treasury 16235 · net +712 · threat 44 · provinces 28 (-1) · ceiling 20439 · army 62328 · vassals Holland 100 · Switzerland 88
  - NET income 3450 · trade 536 · admin 50 · tribute 562 · upkeep 488 · charges 2408 · occupation 15 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Sire — Franconia has been taken by Austria.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Lannes cannot drill with enemy forces nearby! ArchdukeJohn is at Franconia, just one region away.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16979 · net +618 · threat 42 · provinces 28 (+0) · ceiling 20628 · army 60287 · vassals Holland 100 · Switzerland 88
  - NET income 3450 · trade 536 · admin 50 · tribute 562 · upkeep 456 · charges 2534 · occupation 15 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Soult's fortifications strengthen: +7% defense (max 12%)
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 5 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17605 · net +520 · threat 40 · provinces 28 (+0) · ceiling 20676 · army 58327 · vassals Holland 100 · Switzerland 88
  - NET income 3450 · trade 536 · admin 50 · tribute 562 · upkeep 448 · charges 2640 · occupation 15 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! ArchdukeCharles is at Munich, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Munich instead.)
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke Charles at Munich instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 2937, own corps) vs Archduke Charles (lost 1129) — Reinforcements from Davout and Napoleon bolstered Lannes's position — though Bernadotte never arrived, Sire.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 0% -> 13%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 3 actions unused) Turn 28 begins!
- SPENT 600g on this turn's orders
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles holds them at Swabia while allies attack from Munich! (+1 coordination) · ArchdukeJohn holds them at Swabia while allies attack from Munich! (+1 coordination)
  - ⚔ Archduke Charles (lost 1807) vs Bernadotte (lost 155, own corps) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1811, own corps) vs Soult (lost 2907, own corps) — Murat reached Soult in time, Sire — but even together, the field could not be held.
  - ⚔ Archduke John (lost 438, own corps) vs Soult (lost 4765) — The battle unfolded without particular distinction.
  - verbs: attack×3, move×1
- LEDGER treasury 16156 · net +177 · threat 38 · provinces 28 (+0) · ceiling 16995 · army 38701 · vassals Holland 96 · Switzerland 82
  - NET income 3369 · trade 536 · admin 50 · tribute 562 · upkeep 288 · charges 2978 · contributions 69 · occupation 30 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Sire — Lannes's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Piedmont.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 8
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 5 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Napoleon. Casualties: Arc… · ArchdukeJohn delivers an effective strike. ArchdukeJohn gains the advantage over Davout. Casualties: ArchdukeJohn's arm…
  - ⚔ Archduke Charles (lost 32, own corps) vs Napoleon (lost 643) — A skirmish, Sire. Napoleon's men traded shots with Archduke Charles; there was no battle to speak of.
  - ⚔ Archduke John (lost 118, own corps) vs Davout (lost 2340) — A grievous defeat for Davout, Sire. The losses are severe.
  - verbs: attack×2
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Swabia — 594 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Swabia — 594 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 16211 · net +161 · threat 36 · provinces 28 (+0) · ceiling 16966 · army 33722 · vassals Holland 94 · Switzerland 78
  - NET income 3319 · trade 536 · admin 50 · tribute 562 · upkeep 248 · charges 3012 · contributions 19 · occupation 52 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Sire — Davout's corps has been broken at Swabia. He must reform before he fights again.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✗ Davout is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Soult, drill` → ✗ Soult is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 5 actions unused) Turn 30 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Swabia where he stands! (517 lost to march — forward supply lines reduce losses) Captured: France… · ArchdukeJohn launches a decisive assault. ArchdukeJohn gains the advantage over Davout. Casualties: ArchdukeJohn 175, D… · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Soult. Casualties: Archdu…
  - 🏴 Austria: ArchdukeCharles takes Swabia where he stands! (517 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - ⚔ Archduke John (lost 175) vs Davout (lost 1962) — Davout's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Archduke Charles (lost 420) vs Soult (lost 4946) — Soult's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, retreat×1, grant_dotation×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 15600 · net -201 · threat 34 · provinces 27 (-1) · ceiling 14780 · army 26283 · vassals Holland 90 · Switzerland 72
  - NET income 3272 · trade 536 · admin 50 · tribute 562 · upkeep 184 · charges 3340 · contributions 122 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 30 — Early December 1806
  - MAILBOX #15 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (72 → 76); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 510 gold (×3 at war) (Davout's intendance: -15%). Morale: 0% -> 19%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 5 actions unused) Turn 31 begins!
- SPENT 510g on this turn's orders
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeC… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Lorraine!
  - ⚔ Archduke Charles (lost 290) vs Bernadotte (lost 244, own corps) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today. And Bernadotte was taken on …
  - ⚔ Archduke Charles (lost 379) vs Murat (lost 6739) — Murat was caught in an aggressive posture when Archduke Charles struck, Sire. A defensive stance would have served bett…
  - verbs: attack×2
- ORDER Murat [awaiting_response]: Murat is cornered at Lorraine with 1,886 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Lorraine with 1,886 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 14402 · net -135 · threat 32 · provinces 27 (+0) · ceiling 13861 · army 17162 · vassals Holland 86 · Switzerland 71
  - NET income 3222 · trade 536 · admin 50 · tribute 337 · upkeep 128 · charges 3105 · contributions 72 · blockade 335 · admiralty 90 · laws 550
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 31 — Late December 1806
  - MAILBOX #16 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #21 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · stalemate
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Lannes, drill` → ✗ Lannes is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Soult, fortify` → ✗ Soult is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 3 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13791 · net +1373 · threat 31 · provinces 27 (+0) · ceiling 24189 · army 36220 · vassals Holland 86 · Switzerland 70
  - NET income 3224 · trade 548 · admin 50 · tribute 337 · upkeep 248 · charges 1556 · blockade 342 · admiralty 90 · laws 550
- DISPATCH: Sire — Marshal Murat has been taken. Austria holds him prisoner.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 32 — Early January 1807
  - MAILBOX #17 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #22 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #23 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Britain + Russia (3 pairs resolved). → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Austria ultimatum demand · Holland client petition
- LEDGER treasury 16801 · net +2914 · threat 15 · provinces 27 (+0) · ceiling 107843 · army 35305 · vassals Holland 84 · Switzerland 69
  - NET income 3226 · trade 572 · admin 50 · tribute 337 · upkeep 248 · charges 473 · laws 550
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Holland vs Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +4 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×2)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 31 to 15.
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Britain (Defensive Alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Portugal rebuffs Britain (defensive alliance)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Britain (defensive alliance)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 33 — Late January 1807
  - MAILBOX #18 Austria incoming_ultimatum: Austria — Ultimatum → activated
  - MAILBOX #19 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, ultimatum_demand #24 → defy
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #25 → grant the petition
  - POPUP diplomatic_dialogue: Austria, ultimatum_demand #24 → defy
  - POPUP proposal_result: You have defied Austria's ultimatum. Their court will not forget it — expect their weight behind the next coalition. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #25 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Orleanais. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Orleanais. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✗ Soult is not currently fortified.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 5,000 cavalry at Paris (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is note…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 3 actions unused) Turn 34 begins!
- SPENT 259g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 19064 · net +2466 · threat 17 · provinces 27 (+0) · ceiling 96125 · army 39263 · vassals Holland 87 · Switzerland 68
  - NET income 3228 · trade 572 · admin 50 · upkeep 288 · charges 546 · laws 550
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Massena, unfortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21518 · net +2376 · threat 19 · provinces 27 (+0) · ceiling 95750 · army 38251 · vassals Holland 86 · Switzerland 67
  - NET income 3258 · trade 522 · admin 50 · upkeep 280 · charges 624 · laws 550
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Orleanais. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Orleanais. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Orleanais. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot s…
- CMD `Murat, drill` → ✗ Murat is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23905 · net +2311 · threat 21 · provinces 27 (+0) · ceiling 96093 · army 37266 · vassals Holland 85 · Switzerland 66
  - NET income 3261 · trade 522 · admin 50 · upkeep 272 · charges 700 · laws 550
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 60).
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 10% -> 20%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25976 · net +2223 · threat 23 · provinces 27 (+0) · ceiling 95437 · army 39249 · vassals Holland 84 · Switzerland 65
  - NET income 3264 · trade 522 · admin 50 · upkeep 296 · charges 767 · laws 550
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Orleanais. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Orleanais. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 28210 · net +2388 · threat 25 · provinces 27 (+0) · ceiling 102812 · army 38256 · vassals Holland 83 · Switzerland 64
  - NET income 3267 · trade 522 · admin 50 · tribute 225 · upkeep 288 · charges 838 · laws 550
- DISPATCH: Ney's fortifications strengthen: +8% defense (MAX)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Massena, drill` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 30625 · net +2337 · threat 27 · provinces 27 (+0) · ceiling 103656 · army 37289 · vassals Holland 82 · Switzerland 55
  - NET income 3270 · trade 522 · admin 50 · tribute 225 · upkeep 264 · charges 916 · laws 550
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Orleanais. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Orleanais. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Orleanais (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 10% -> 21%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 32731 · net +2257 · threat 29 · provinces 27 (+0) · ceiling 103250 · army 39289 · vassals Holland 81 · Switzerland 46
  - NET income 3273 · trade 522 · admin 50 · tribute 225 · upkeep 280 · charges 983 · laws 550
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Tyrol. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 34999 · net +2533 · threat 28 · provinces 27 (+0) · ceiling 114125 · army 38313 · vassals Holland 80 · Switzerland 37
  - NET income 3276 · trade 522 · admin 50 · tribute 562 · upkeep 272 · charges 1055 · laws 550
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 41% of active European bloc power.

---
finished: **completed** · commands 239 · popups 61 · battles 30
