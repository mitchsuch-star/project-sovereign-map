# Playtest digest — ADV

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "missions": "advisor"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `47eb92ffc944` (dirty) · content `aae077cedc7a` · driver `e498338939cb`
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
- LEDGER treasury 1432 · net +922 · threat 68 · provinces 28 · ceiling 24378 · army 183181 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2654 · blockade 219 · admiralty 90
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
- LEDGER treasury 2040 · net +1275 · threat 66 · provinces 28 (+0) · ceiling 25474 · army 170477 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2575 · trade 450 · admin 50 · tribute 829 · upkeep 2256 · charges 2 · blockade 281 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈18 turns to +100 at the present rate · beat running
- DISPATCH: Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Prussia (open borders agreement)
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
- LEDGER treasury 2968 · net +1692 · threat 64 · provinces 28 (+0) · ceiling 26858 · army 153870 · vassals Holland 94 · Kingdom of Italy 90 · Switzerland 88
  - NET income 2551 · trade 525 · admin 50 · tribute 799 · upkeep 1746 · charges 68 · blockade 329 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈17 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 2
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (open borders agreement)
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
- LEDGER treasury 4571 · net +2020 · threat 62 · provinces 28 (+0) · ceiling 22104 · army 138021 · vassals Holland 90 · Kingdom of Italy 74 · Switzerland 82
  - NET income 2551 · trade 587 · admin 50 · tribute 802 · upkeep 1216 · charges 296 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈16 turns to +100 at the present rate · beat running
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the w…
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +9 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 8 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Bernadotte. Casualties: Archdu… · Mack's attack meets fierce resistance. Deroy holds the line. Casualties: Mack 4,940, Deroy 2,837. Both armies remain in… · Archduke Charles's forces advance steadily. Brutal stalemate between Archduke Charles and Deroy. Heavy casualties on bo… · ArchdukeJohn strikes back after successfully defending!
  - ⚔ Archduke Charles (lost 947) vs Bernadotte (lost 3488, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Mack (lost 4940) vs Deroy (lost 2837) — A standard affair. Nothing unusual to report.
  - ⚔ Archduke Charles (lost 2994) vs Deroy (lost 3110) — Stalemate. Deroy and Archduke Charles glare at each other across the field.
  - verbs: attack×4, unfortify×1, move×1, recruit×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 6489 · net +1933 · threat 60 · provinces 28 (+0) · ceiling 22121 · army 131602 · vassals Holland 88 · Kingdom of Italy 72 · Switzerland 78
  - NET income 2553 · trade 587 · admin 50 · tribute 799 · upkeep 1044 · charges 554 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (78 → 88); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeJohn loses 1,834 troops in the assau…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -91g, Kingdom of Italy -175g. Captured: KingdomOfItaly → Austria
  - verbs: attack×1
- LEDGER treasury 7874 · net +1153 · threat 58 · provinces 28 (+0) · ceiling 15227 · army 131107 · vassals Holland 88 · Kingdom of Italy 72 · Switzerland 87
  - NET income 2554 · trade 587 · admin 50 · tribute 487 · upkeep 1036 · charges 921 · contributions 110 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - TURN EVENTS 4
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +5 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: Spain rebuffs Prussia (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke… · Mack delivers an effective strike. Mack gains the advantage over Deroy. Casualties: Mack 1,128, Deroy 4,500. Both armie…
  - 🏴 Austria: [!] Deroy's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Franconia. (476 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1410) vs Deroy (lost 4240) — The battle unfolded without particular distinction.
  - ⚔ Mack (lost 1128) vs Deroy (lost 4500) — Deroy's army has been badly mauled. Mack proved the stronger force today.
  - verbs: attack×2, stance_change×2, fortify×1, wait×1
- LEDGER treasury 9041 · net +962 · threat 56 · provinces 28 (+0) · ceiling 15050 · army 130622 · vassals Holland 88 · Kingdom of Italy 72 · Switzerland 86
  - NET income 2556 · trade 587 · admin 50 · tribute 487 · upkeep 1024 · charges 1126 · contributions 110 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈13 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Franconia has been taken by Austria.
  - TURN EVENTS 4
- DIPLO +6 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 16 courts rebuff Bavaria (open borders agreement)

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Deroy. Casualties: Archduke… · ArchdukeCharles assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,574 troops in th…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Deroy is taken by Austria at Munich!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -78g, Bavaria -125g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 268) vs Deroy (lost 4380) — Even the favorable ground could not save Deroy, Sire. Archduke Charles overcame the terrain. And Deroy was taken on tha…
  - verbs: attack×2
- LEDGER treasury 10005 · net +784 · threat 54 · provinces 28 (+0) · ceiling 14806 · army 130147 · vassals Holland 88 · Kingdom of Italy 72 · Switzerland 85
  - NET income 2558 · trade 587 · admin 50 · tribute 487 · upkeep 1024 · charges 1306 · contributions 110 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Britain and Spain rebuff Bavaria (open borders agreement)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduk… · Mack delivers an effective strike. Mack gains the advantage over Massena. Casualties: Mack 1,750, Massena 3,134. Both a…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Franche-Comte!
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 5%)! FORCED RETREAT! Mack advances into Piedmont. (582 lost to march) Piedmont has been captured by Austria!
  - ⚔ Archduke Charles (lost 365) vs Bernadotte (lost 2494, own corps) — Bernadotte fought without Soult's support. The roads, or the will, proved insufficient. And Bernadotte was taken on tha…
  - ⚔ Mack (lost 1750) vs Massena (lost 3134) — Massena held superior ground, yet Mack prevailed. A grim day, Sire.
  - verbs: attack×2, move×2, retreat×1, unfortify×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franche-Comte with 4,899 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franche-Comte with 4,899 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 10294 · net +569 · threat 42 · provinces 28 (+0) · ceiling 13576 · army 115087 · vassals Holland 84 · Switzerland 80
  - NET income 2551 · trade 587 · admin 50 · tribute 337 · upkeep 912 · charges 1436 · contributions 150 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 3
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: Britain rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Mack gains the advantage over Massena. Casualties: Mack 745, Massena 5,454. Both armies r…
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Lyonnais. (219 lost to march) Lyonnais has been captured by Austria!
  - ⚔ Mack (lost 745) vs Massena (lost 5454) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: form_square×1, attack×1
- LEDGER treasury 10558 · net +413 · threat 40 · provinces 27 (-1) · ceiling 12831 · army 109633 · vassals Holland 82 · Switzerland 77
  - NET income 2473 · trade 587 · admin 50 · tribute 337 · upkeep 872 · charges 1554 · contributions 150 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack faces a difficult fight. Mack gains the advantage over Massena. Casualties: Mack 451, Massena 3,942. Both armies r… · Mack marches from Limousin into Berry unopposed! (195 lost to march) Captured: France → Austria
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Limousin. (197 lost to march) Limousin has been captured by Austria!
  - 🏴 Austria: Mack marches from Limousin into Berry unopposed! (195 lost to march) Captured: France → Austria
  - ⚔ Mack (lost 451) vs Massena (lost 3942) — Massena's army has been badly mauled. Mack proved the stronger force today.
  - verbs: attack×2
- LEDGER treasury 10666 · net +221 · threat 37 · provinces 25 (-2) · ceiling 11840 · army 105691 · vassals Holland 80 · Switzerland 74
  - NET income 2214 · trade 587 · admin 50 · tribute 337 · upkeep 840 · charges 1629 · contributions 40 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Limousin has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, balance_of_europe_shifted, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 3 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget launches a devastating assault! Paget gains the advantage over Massena. Casualties: Paget 218, Massena 3,763. Bot… · Mack assaults the Normandy garrison! Garrison collapses (6,000 -> 0). Mack loses 1,851 troops in the assault. Mack marc… · Mack marches from Normandy into Artois unopposed! (139 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -92g, France -150g. Captured: France → Austria
  - 🏴 Austria: Mack marches from Normandy into Artois unopposed! (139 lost to march) Captured: France → Austria
  - ⚔ Paget (lost 218) vs Massena (lost 3763) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×3
- ORDER Massena [awaiting_response]: Massena is cornered at Paris with 3,315 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Paris with 3,315 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 2 · Britain armistice losing · Austria peace
- LEDGER treasury 10282 · net +204 · threat 34 · provinces 23 (-2) · ceiling 11348 · army 98613 · vassals Holland 78 · Switzerland 71
  - NET income 2048 · trade 587 · admin 50 · tribute 337 · upkeep 784 · charges 1576 · blockade 368 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Normandy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL expedition_landed: THE LANDING: Paget has put 4,105 men ashore at Piedmont.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 3
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: Spain rebuffs Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 13 — Late March 1806
  - MAILBOX #9 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #10 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #10 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Austria. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #11 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
  - POPUP diplomatic_dialogue: Britain, armistice_losing #10 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
  - POPUP diplomatic_dialogue: Austria, peace #11 → accept
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - MISSION ADVISOR: recalling Talleyrand — branch 1 has held the desk 12 turns (limit 12)
- CMD `Talleyrand, cancel mission with Spain` → ✓ Talleyrand's mission to Spain has been cancelled.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
- ENVOYS WAITING 2 · Britain settlement offer · Holland client petition
- LEDGER treasury 10090 · net +1387 · threat 31 · provinces 23 (+0) · ceiling 24295 · army 118013 · vassals Holland 76 · Switzerland 70
  - NET income 2054 · trade 512 · admin 50 · tribute 562 · upkeep 912 · charges 789 · admiralty 90
- DISPATCH: Sire — Marshal Massena has been taken. Austria holds him prisoner.
  - RAIL status_quo_conceded: Artois, Berry, Limousin, Lyonnais and Normandy — left with Austria by the peace, titled to them by treaty.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL +3 more
  - TURN EVENTS 2
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, blockade_broken ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 14 — Early April 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #13 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Britain + Russia (4 pairs resolved). → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - MISSION ADVISOR branch 2 (follow the counsel) → `improve relations with Denmark`
- CMD `improve relations with Denmark` → ✓ Sire, I shall begin efforts to improve relations with Denmark. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #15 → start_mission
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 11928 · net +1816 · threat 13 · provinces 23 (+0) · ceiling 163250 · army 117433 · vassals Holland 85 · Switzerland 69
  - NET income 2060 · trade 512 · admin 50 · tribute 225 · upkeep 912 · charges 119
- MISSION Improving Relations — Denmark · net +7 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Artois, Berry, Limousin and 2 more lie in enemy hands. Austria holds them.
  - RAIL settlement_summary: Settlement of France vs Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 1
- COURTS: The court of Austria eases over Redeem Italy — service to the strong is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress, blockade_broken)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 31 to 15.
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (69 → 79); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13525 · net +1578 · threat 11 · provinces 23 (+0) · ceiling 145000 · army 116869 · vassals Holland 84 · Switzerland 79
  - NET income 2066 · trade 512 · admin 50 · upkeep 912 · charges 138
- MISSION Improving Relations — Denmark · net +7 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — 3 turns now with Artois, Berry, Limousin and 2 more in enemy hands. The country counts every one of them.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 15109 · net +1565 · threat 9 · provinces 23 (+0) · ceiling 145500 · army 116325 · vassals Holland 83 · Switzerland 79
  - NET income 2072 · trade 512 · admin 50 · upkeep 912 · charges 157
- MISSION Improving Relations — Denmark · net +7 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Sardinia and Britain have signed the Defensive Alliance.
  - TURN EVENTS 1
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, balance_of_europe_shifted, diplomatic_ai_ai_treaty)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 37% of active European bloc power.
  - LOG diplomatic_ai_ai_treaty: Sardinia and Britain sign a Defensive Alliance
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Denmark defensive alliance
- LEDGER treasury 16676 · net +1548 · threat 7 · provinces 23 (+0) · ceiling 145666 · army 115797 · vassals Holland 82 · Switzerland 79
  - NET income 2074 · trade 512 · admin 50 · upkeep 912 · charges 176
- MISSION Improving Relations — Denmark · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 18 — Early June 1806
  - MAILBOX #14 Denmark incoming_proposal: Denmark — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Denmark, defensive_alliance #17 → accept
  - POPUP proposal_result: You have accepted Denmark's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Denmark. → display-only
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 18226 · net +1532 · threat 5 · provinces 23 (+0) · ceiling 145833 · army 115285 · vassals Holland 81 · Switzerland 79
  - NET income 2076 · trade 512 · admin 50 · upkeep 912 · charges 194
- MISSION Improving Relations — Denmark · net +7 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −74, −82 and −75). The Balance of Europe names the price to keep each out.
  - TURN EVENTS 1
- DIPLO +6 medium/low (diplomatic_treaty_signed, law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 19759 · net +1514 · threat 3 · provinces 23 (+0) · ceiling 145916 · army 114785 · vassals Holland 80 · Switzerland 79
  - NET income 2077 · trade 512 · admin 50 · upkeep 912 · charges 213
- MISSION Improving Relations — Denmark · net +7 a turn · ≈7 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the court of Austria eases over Redeem Italy — alliance is now the length of its tether.
  - TURN EVENTS 1
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Denmark alliance
- LEDGER treasury 21307 · net +1530 · threat 1 · provinces 23 (+0) · ceiling 148750 · army 114301 · vassals Holland 79 · Switzerland 79
  - NET income 2079 · trade 512 · admin 50 · upkeep 880 · charges 231
- MISSION Improving Relations — Denmark · net +7 a turn · ≈6 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +5 medium/low (law_enacted_abroad ×2, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

---
finished: **completed** · commands 23 · popups 32 · battles 24
