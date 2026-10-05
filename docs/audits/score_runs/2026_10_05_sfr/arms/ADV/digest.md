# Playtest digest — ADV

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "missions": "advisor"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `0f5e8d843185` (dirty) · content `423b7f09867a` · driver `37f9f712f284`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
  - MISSION ADVISOR branch 1 (reassure an ally) → `reassure Spain`
- CMD `reassure Spain` → ✓ Sire, I shall begin efforts to reassure Spain. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #1 → start_mission
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu…
  - ⚔ Archduke Charles (lost 4431) vs Massena (lost 5819) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1636 · net +1126 · threat 68 · provinces 28 · ceiling 29330 · army 183181 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · blockade 219 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈19 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +9 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_mission_progress, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu… · Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,018, L… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Teulie. Casualties: Archduk…
  - ⚔ Archduke Charles (lost 4386) vs Massena (lost 4395, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 5018) vs Lannes (lost 2582, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 2846) vs Teulie (lost 1351, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×3, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2448 · net +1457 · threat 66 · provinces 28 (+0) · ceiling 29224 · army 170477 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2575 · trade 450 · admin 50 · tribute 829 · upkeep 2052 · charges 24 · blockade 281 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈18 turns to +100 at the present rate · beat running
- DISPATCH: Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 22 approaches from Prussia and Bavaria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Massena. Casualties: Ar… · Mack delivers an effective strike. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 4,735… · Archduke Charles faces a difficult fight. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Charle… · Mack delivers an effective strike. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack 3,710,…
  - ⚔ Archduke Charles (lost 3027) vs Massena (lost 4373, own corps) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Mack (lost 4735) vs Lannes (lost 1981, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 1581) vs Teulie (lost 1392, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Mack (lost 3710) vs Murat (lost 3741, own corps) — Murat fought without Soult's support. The roads, or the will, proved insufficient.
  - verbs: attack×4
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 3,688 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 3,688 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3580 · net +1853 · threat 64 · provinces 28 (+0) · ceiling 29740 · army 153870 · vassals Holland 94 · Kingdom of Italy 90 · Switzerland 88
  - NET income 2551 · trade 525 · admin 50 · tribute 799 · upkeep 1542 · charges 111 · blockade 329 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈17 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 2
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria, Prussia and Naples are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 24 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 7 actions, 5 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack delivers an effective strike. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 3,359… · Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Bernadotte. Casualties: Arc… · Mack's forces press forward aggressively. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack… · Mack flanks from Swabia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: FORCED RETREAT! Mack advances into Franconia. (924 lost to march) Franconia has been captured by Austria!
  - ⚔ Mack (lost 3359) vs Lannes (lost 1886, own corps) — Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 1558) vs Bernadotte (lost 4840) — The engagement proceeded as one might expect, Sire.
  - ⚔ Mack (lost 2937) vs Murat (lost 3363, own corps) — Soult failed to arrive in time. Murat's army fought without expected support.
  - ⚔ Mack (lost 1431) vs Bernadotte (lost 3350) — The line gave way. Bernadotte is falling back, and not in good order.
  - ⚔ Deroy (lost 2919) vs Archduke John (lost 1555) — Archduke John stood alone, Sire. Mack never came.
  - verbs: attack×5, wait×1, recruit×1
- LEDGER treasury 5211 · net +2043 · threat 62 · provinces 28 (+0) · ceiling 22937 · army 138021 · vassals Holland 90 · Kingdom of Italy 74 · Switzerland 82
  - NET income 2551 · trade 587 · admin 50 · tribute 802 · upkeep 1120 · charges 369 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈16 turns to +100 at the present rate · beat running
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +9 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (open borders agreement)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 8 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Bernadotte. Casualties: Archdu… · Mack faces a difficult fight. Deroy holds the line. Casualties: Mack 5,021, Deroy 2,864. Both armies remain in the fiel… · Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Deroy. Heavy casual… · ArchdukeJohn strikes back after successfully defending!
  - ⚔ Archduke Charles (lost 947) vs Bernadotte (lost 3488, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Mack (lost 5021) vs Deroy (lost 2864) — A standard affair. Nothing unusual to report.
  - ⚔ Archduke Charles (lost 2902) vs Deroy (lost 3361) — Stalemate. Deroy and Archduke Charles glare at each other across the field.
  - verbs: attack×4, unfortify×1, move×1, recruit×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7052 · net +1863 · threat 60 · provinces 28 (+0) · ceiling 22121 · army 131602 · vassals Holland 88 · Kingdom of Italy 72 · Switzerland 78
  - NET income 2553 · trade 587 · admin 50 · tribute 799 · upkeep 1044 · charges 624 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the w…
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (78 → 88); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeJohn loses 1,834 troops in the assau…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -91g, Kingdom of Italy -175g. Captured: KingdomOfItaly → Austria
  - verbs: attack×1
- LEDGER treasury 8351 · net +1079 · threat 58 · provinces 28 (+0) · ceiling 15227 · army 131107 · vassals Holland 88 · Kingdom of Italy 72 · Switzerland 87
  - NET income 2554 · trade 587 · admin 50 · tribute 487 · upkeep 1036 · charges 995 · contributions 110 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - TURN EVENTS 4
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_mission_progress, coercive_demand)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Spain rebuffs 4 courts (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke… · ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,404 troops. G…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Franconia. (571 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1184) vs Deroy (lost 4959) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, fortify×1
- LEDGER treasury 9444 · net +897 · threat 56 · provinces 28 (+0) · ceiling 15050 · army 130622 · vassals Holland 88 · Kingdom of Italy 72 · Switzerland 86
  - NET income 2556 · trade 587 · admin 50 · tribute 487 · upkeep 1024 · charges 1191 · contributions 110 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈13 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Franconia has been taken by Austria.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +7 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Bavaria (open borders agreement)

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 2,144 troops in th… · Mack engages in solid combat. Mack gains the advantage over Massena. Casualties: Mack 1,705, Massena 3,770. Both armies…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -107g, Bavaria -175g. Captured: Bavaria → Austria
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Piedmont. (740 lost to march) Piedmont has been captured by Austria!
  - ⚔ Mack (lost 1705) vs Massena (lost 3770) — Massena held superior ground, yet Mack prevailed. A grim day, Sire.
  - verbs: attack×2, move×1, form_square×1
- LEDGER treasury 10049 · net +638 · threat 44 · provinces 28 (+0) · ceiling 13881 · army 126377 · vassals Holland 86 · Switzerland 83
  - NET income 2558 · trade 599 · admin 50 · tribute 337 · upkeep 992 · charges 1339 · contributions 110 · blockade 375 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Massena's corps has been broken at Piedmont. He must reform before he fights again.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Spain rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain and Prussia rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 5 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Prussia (open borders agreement)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Mack gains the advantage over Massena. Casualties: Mack 546, Massena 6,457. Both armies r… · Mack marches from Lyonnais into Provence unopposed! (276 lost to march) Captured: France → Austria
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Lyonnais. (293 lost to march) Lyonnais has been captured by Austria!
  - 🏴 Austria: Mack marches from Lyonnais into Provence unopposed! (276 lost to march) Captured: France → Austria
  - ⚔ Mack (lost 546) vs Massena (lost 6457) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: attack×2
- LEDGER treasury 10159 · net +332 · threat 41 · provinces 26 (-2) · ceiling 12045 · army 119455 · vassals Holland 84 · Switzerland 80
  - NET income 2329 · trade 599 · admin 50 · tribute 337 · upkeep 936 · charges 1432 · contributions 150 · blockade 375 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, balance_of_europe_shifted, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget's forces advance steadily. Paget gains the advantage over Massena. Casualties: Paget 268, Massena 3,558. Both arm… · Mack marches from Provence into Languedoc unopposed! (261 lost to march) Captured: France → Austria
  - 🏴 Britain: [Cavalry] Paget's blood is up! (Recklessness: 1) Paget advances into Limousin. (40 lost to march) Limousin has been captured by Britain!
  - 🏴 Austria: Mack marches from Provence into Languedoc unopposed! (261 lost to march) Captured: France → Austria
  - ⚔ Paget (lost 268) vs Massena (lost 3558) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 10404 · net +324 · threat 38 · provinces 24 (-2) · ceiling 12291 · army 115440 · vassals Holland 82 · Switzerland 77
  - NET income 2141 · trade 599 · admin 50 · tribute 337 · upkeep 896 · charges 1442 · blockade 375 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Limousin has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 4
- DIPLO +7 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift ×3)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_proposal: Britain — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #10 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack marches from Languedoc into Gascony unopposed! (495 lost to march) Captured: France → Austria
  - 🏴 Austria: Mack marches from Languedoc into Gascony unopposed! (495 lost to march) Captured: France → Austria
  - verbs: attack×1
- ENVOYS WAITING 2 · Austria peace · Holland client petition
- LEDGER treasury 10994 · net +460 · threat 35 · provinces 23 (-1) · ceiling 13624 · army 114993 · vassals Holland 80 · Switzerland 76
  - NET income 2032 · trade 599 · admin 50 · tribute 337 · upkeep 896 · charges 1572 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Gascony has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 4
- DIPLO +8 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent, paymaster_subsidy, blockade_broken ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 12 — Early March 1806
  - MAILBOX #10 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, peace #11 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #12 → grant the petition
  - POPUP diplomatic_dialogue: Austria, peace #11 → accept
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (80 → 90); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
  - POPUP diplomatic_dialogue: Holland, client_petition #12 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 10447 · net +898 · threat 32 · provinces 23 (+0) · ceiling 20373 · army 119555 · vassals Holland 89 · Switzerland 75
  - NET income 2034 · trade 611 · admin 50 · upkeep 944 · charges 763 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Gascony, Languedoc, Limousin and 2 more lie in enemy hands. Austria and Britain hold them.
  - RAIL status_quo_conceded: Gascony, Languedoc, Lyonnais and Provence — left with Austria by the peace, titled to them by treaty.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 2
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 13 — Late March 1806
  - MAILBOX #12 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (5 pairs resolved). Status quo: Limousin stays British by the treaty. Status quo: Franconia and Munich stay Austrian by the treaty. → display-only
  - MISSION ADVISOR: recalling Talleyrand — branch 1 has held the desk 12 turns (limit 12)
- CMD `Talleyrand, cancel mission with Spain` → ✓ Talleyrand's mission to Spain has been cancelled.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12127 · net +1885 · threat 14 · provinces 23 (+0) · ceiling 169166 · army 119125 · vassals Holland 88 · Switzerland 74
  - NET income 2036 · trade 635 · admin 50 · tribute 225 · upkeep 940 · charges 121
- DISPATCH: Sire — our peace binds Britain for 4 more turns and Russia for 4 more turns; then each may join a league (relations −83 and −79).
  - RAIL status_quo_conceded: Limousin — left with Britain by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Austria eases over Redeem Italy — service to the strong is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 32 to 16.
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria, Prussia and Naples are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

## Turn 14 — Early April 1806
  - MISSION ADVISOR branch 2 (follow the counsel) → `improve relations with Denmark`
- CMD `improve relations with Denmark` → ✓ Sire, I shall begin efforts to improve relations with Denmark. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #15 → start_mission
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 14013 · net +1863 · threat 12 · provinces 23 (+0) · ceiling 169250 · army 118704 · vassals Holland 87 · Switzerland 73
  - NET income 2037 · trade 635 · admin 50 · tribute 225 · upkeep 940 · charges 144
- MISSION Improving Relations — Denmark · net +7 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — 3 turns now with Gascony, Languedoc, Limousin and 2 more in enemy hands. The country counts every one of them.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: 10 courts rebuff Bavaria (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (73 → 83); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15665 · net +1633 · threat 10 · provinces 23 (+0) · ceiling 151666 · army 118292 · vassals Holland 86 · Switzerland 83
  - NET income 2039 · trade 635 · admin 50 · upkeep 928 · charges 163
- MISSION Improving Relations — Denmark · net +7 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the enemy has held Gascony, Languedoc, Limousin and 2 more 4 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17299 · net +1614 · threat 8 · provinces 23 (+0) · ceiling 151750 · army 117888 · vassals Holland 85 · Switzerland 83
  - NET income 2040 · trade 635 · admin 50 · upkeep 928 · charges 183
- MISSION Improving Relations — Denmark · net +7 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 6 in hand); or let the war …
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 37% of active European bloc power.

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Denmark defensive alliance
- LEDGER treasury 18923 · net +1604 · threat 6 · provinces 23 (+0) · ceiling 152583 · army 117492 · vassals Holland 84 · Switzerland 83
  - NET income 2042 · trade 635 · admin 50 · upkeep 920 · charges 203
- MISSION Improving Relations — Denmark · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −74, −79 and −75). The Balance of Europe names the price to keep each out.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +6 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress, coercive_demand)

## Turn 18 — Early June 1806
  - MAILBOX #14 Denmark incoming_proposal: Denmark — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Denmark, defensive_alliance #17 → accept
  - POPUP proposal_result: You have accepted Denmark's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Denmark. → display-only
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 20537 · net +1595 · threat 4 · provinces 23 (+0) · ceiling 153416 · army 117104 · vassals Holland 83 · Switzerland 83
  - NET income 2044 · trade 635 · admin 50 · upkeep 912 · charges 222
- MISSION Improving Relations — Denmark · net +7 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - RAIL broken_bargain: The compact with Sweden lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 1
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- COURTS: And Russia stirs at its own design.
- DIPLO +7 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_auto_downgrade, blockade_begins, agenda_shift, diplomatic_relation_shift)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22133 · net +1914 · threat 2 · provinces 23 (+0) · ceiling 181583 · army 116722 · vassals Holland 82 · Switzerland 83
  - NET income 2045 · trade 635 · admin 50 · tribute 337 · upkeep 912 · charges 241
- MISSION Improving Relations — Denmark · net +7 a turn · ≈7 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Denmark alliance · Holland client petition
- LEDGER treasury 24057 · net +1901 · threat 0 · provinces 23 (+0) · ceiling 182416 · army 116349 · vassals Holland 81 · Switzerland 83
  - NET income 2047 · trade 635 · admin 50 · tribute 337 · upkeep 904 · charges 264
- MISSION Improving Relations — Denmark · net +7 a turn · ≈6 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

---
finished: **completed** · commands 23 · popups 27 · battles 20
