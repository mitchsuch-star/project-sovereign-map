# Playtest digest — rs0928-advisor

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "missions": "advisor"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `91796f250248` · content `8f597da58501` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
  - MISSION ADVISOR branch 1 (reassure an ally) → `reassure Spain`
- CMD `reassure Spain` → ✓ Sire, I shall begin efforts to reassure Spain. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #1 → start_mission
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual…
  - ⚔ Archduke Charles (lost 4431) vs Massena (lost 5919) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1631 · net +1126 · threat 68 · provinces 28 · ceiling 29330 · army 183081 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · blockade 219 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈19 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +7 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_mission_progress, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual… · Mack delivers an effective strike. Mack gains the advantage over Bernadotte. Casualties: Mack 2,804, Bernadotte 4,583. … · Mack holds them at Franconia while allies attack from Swabia! (+1 coordination)
  - ⚔ Archduke Charles (lost 3902) vs Massena (lost 5261) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 2804) vs Bernadotte (lost 4583) — The margin was slim. Training and preparation would serve Bernadotte well.
  - ⚔ Mack (lost 3373) vs Deroy (lost 4534) — Neither Deroy nor Mack could claim the field. The armies remain locked.
  - verbs: attack×3
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2632 · net +1401 · threat 66 · provinces 28 (+0) · ceiling 29771 · army 173237 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 856 · upkeep 2142 · charges 32 · blockade 281 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈18 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,583 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Mack gains the advantage over Bernadotte. Casualties: Mack 1,752, Bernadotte … · ArchdukeCharles struggles in a costly engagement. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualtie… · ArchdukeCharles flanks from Tyrol while allies attack from Franconia! (+1 coordination) · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharle…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Franconia. (1,175 lost to march) Franconia has been captured by Austria!
  - ⚔ Mack (lost 1752) vs Bernadotte (lost 5237) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 3474) vs Massena (lost 4127) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 355) vs Bernadotte (lost 3952) — A grievous defeat for Bernadotte, Sire. The losses are severe. And Bernadotte was taken on that field — Austria holds h…
  - ⚔ Archduke Charles (lost 1927) vs Deroy (lost 3616) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×4, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4020 · net +1843 · threat 64 · provinces 28 (+0) · ceiling 32447 · army 155879 · vassals Holland 94 · Kingdom of Italy 98 · Switzerland 88
  - NET income 2590 · trade 525 · admin 50 · tribute 829 · upkeep 1602 · charges 130 · blockade 329 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈17 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, diplomatic_mission_progress, agenda_shift)
  - LOG ai_ai_proposal_refused: 27 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeCharle… · Mack assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). Mack loses 3,063 troops. Garrison holds — 5,000 … · Mack assaults the Munich garrison! Garrison collapses (5,000 -> 0). Mack loses 1,702 troops in the assault. Mack marche… · Mack's attack meets fierce resistance. Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack …
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -85g, Bavaria -125g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 2184) vs Massena (lost 4336) — A narrow defeat for Massena, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Mack (lost 2778) vs Massena (lost 2768) — Stalemate. Massena and Mack glare at each other across the field.
  - verbs: attack×4
- LEDGER treasury 5713 · net +1793 · threat 62 · provinces 28 (+0) · ceiling 30070 · army 148775 · vassals Holland 92 · Kingdom of Italy 98 · Switzerland 84
  - NET income 2590 · trade 524 · admin 50 · tribute 712 · upkeep 1392 · charges 273 · blockade 328 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈16 turns to +100 at the present rate · beat running
- DISPATCH: 2 satellites drifted — Holland and Switzerland.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 1
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeChar… · Mack flanks from Munich while allies attack from Milan! (+1 coordination)
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Milan. (877 lost to march) Milan has been captured by Austria!
  - ⚔ Archduke Charles (lost 1527) vs Massena (lost 4385) — Massena was close. A period of drilling could have changed the outcome.
  - ⚔ Mack (lost 983) vs Massena (lost 6737) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: attack×2, unfortify×1, stance_change×1, move×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7142 · net +1742 · threat 60 · provinces 28 (+0) · ceiling 22051 · army 137569 · vassals Holland 88 · Kingdom of Italy 94 · Switzerland 78
  - NET income 2590 · trade 524 · admin 50 · tribute 712 · upkeep 1116 · charges 600 · blockade 328 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: 7 approaches to Austria and Spain are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (78 → 88); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Massena. Casualties: Arch…
  - ⚔ Archduke Charles (lost 127, own corps) vs Massena (lost 4312) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×1, fortify×1, wait×1
- ORDER Massena [awaiting_response]: Massena is cornered at Piedmont with 4,071 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Piedmont with 4,071 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 8357 · net +1274 · threat 58 · provinces 28 (+0) · ceiling 18658 · army 129186 · vassals Holland 86 · Kingdom of Italy 92 · Switzerland 85
  - NET income 2590 · trade 524 · admin 50 · tribute 337 · upkeep 1024 · charges 785 · blockade 328 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Massena was mauled at Piedmont: half of his corps — 4,312 men — lost in a single action.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 7 — Late December 1805
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (177 lost to march) Captured: France → Austria · ArchdukeCharles marches from Piedmont into Lyonnais unopposed! (408 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (177 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Lyonnais unopposed! (408 lost to march) Captured: France → Austria
  - verbs: attack×2
- LEDGER treasury 9390 · net +881 · threat 45 · provinces 26 (-2) · ceiling 16337 · army 129186 · vassals Holland 86 · Switzerland 84
  - NET income 2360 · trade 536 · admin 50 · tribute 337 · upkeep 1040 · charges 937 · blockade 335 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈13 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 36% of active European bloc power.
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 8 actions, 3 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Lyonnais into Limousin unopposed! (382 lost to march) Captured: France → Austria · ArchdukeJohn marches from Provence into Languedoc unopposed! (175 lost to march) Captured: France → Austria · Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 604, Paget …
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Limousin unopposed! (382 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Languedoc unopposed! (175 lost to march) Captured: France → Austria
  - ⚔ Castanos (lost 604) vs Paget (lost 1979) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: move×4, attack×3, unfortify×1
- LEDGER treasury 9690 · net +228 · threat 42 · provinces 24 (-2) · ceiling 11112 · army 129186 · vassals Holland 86 · Switzerland 83
  - NET income 2158 · trade 536 · admin 50 · tribute 337 · upkeep 1060 · charges 1230 · contributions 138 · blockade 335 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Limousin into Berry unopposed! (358 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,174 troops.… · ArchdukeJohn marches from Languedoc into Gascony unopposed! (346 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,815 troops in …
  - 🏴 Austria: ArchdukeCharles marches from Limousin into Berry unopposed! (358 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Languedoc into Gascony unopposed! (346 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -90g, France -150g. Captured: France → Austria
  - verbs: attack×4
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 9536 · net +231 · threat 39 · provinces 21 (-3) · ceiling 11195 · army 129186 · vassals Holland 86 · Switzerland 82
  - NET income 1870 · trade 536 · admin 50 · tribute 337 · upkeep 1088 · charges 1049 · blockade 335 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil. Paget's corps of 2,634 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of …
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
- DIPLO +6 medium/low (law_enacted_abroad ×3, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia, Naples and Denmark (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #9 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #10 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 4 actions, 0 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×3, fortify×1
- LEDGER treasury 8841 · net +615 · threat 37 · provinces 21 (+0) · ceiling 16490 · army 139186 · vassals Holland 86 · Switzerland 81
  - NET income 1870 · trade 548 · admin 50 · tribute 337 · upkeep 1208 · charges 550 · blockade 342 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — peace with Austria is signed. The war is over.
  - RAIL peace_ratified: Peace ratified between Austria and France.
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, balance_of_europe_shifted, diplomatic_ai_ai_treaty)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 41% of active European bloc power.
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Britain (Defensive Alliance)
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore attacks with overwhelming force. Moore gains the advantage over Bernadotte. Casualties: Moore 402, Bernadotte 2,5… · Moore holds them at Paris while allies attack from Normandy! (+1 coordination)
  - ⚔ Moore (lost 402) vs Bernadotte (lost 2581) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Moore (lost 446) vs Massena (lost 1830) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: attack×2, move×1, fortify×1, unfortify×1
- ORDER Massena [awaiting_response]: Massena is cornered at Paris with 3,170 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Paris with 3,170 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Britain armistice losing
- LEDGER treasury 8672 · net +58 · threat 35 · provinces 21 (+0) · ceiling 9064 · army 131605 · vassals Holland 82 · Switzerland 76
  - NET income 1830 · trade 548 · admin 50 · tribute 337 · upkeep 1116 · charges 979 · contributions 180 · blockade 342 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Bernadotte's corps has been broken at Paris. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
  - MAILBOX #10 Britain incoming_proposal: Britain — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #11 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Britain settlement offer · Holland client petition
- LEDGER treasury 9656 · net +874 · threat 33 · provinces 21 (+0) · ceiling 19366 · army 131605 · vassals Holland 80 · Switzerland 75
  - NET income 1834 · trade 548 · admin 50 · tribute 337 · upkeep 1116 · charges 689 · admiralty 90
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Marshal Massena has been taken. Britain holds him prisoner.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 2
- COURTS: The court of Britain eases over The Paymaster of Coalitions — alliance is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +8 medium/low (diplomatic_treaty_signed, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, blockade_broken ×2)

## Turn 13 — Late March 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #12 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #13 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (80 → 90); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Britain + Russia (4 pairs resolved). → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - MISSION ADVISOR: recalling Talleyrand — branch 1 has held the desk 12 turns (limit 12)
- CMD `Talleyrand, cancel mission with Spain` → ✓ Talleyrand's mission to Spain has been cancelled.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10850 · net +1404 · threat 14 · provinces 21 (+0) · ceiling 127833 · army 136605 · vassals Holland 89 · Switzerland 74
  - NET income 1839 · trade 572 · admin 50 · tribute 225 · upkeep 1176 · charges 106
- DISPATCH: Bernadotte's army has fully recovered and is combat ready.
  - RAIL settlement_summary: Settlement of France + Spain + Holland vs Britain + Russia: settlement ratified.
  - TURN EVENTS 1
- COURTS: The court of Austria eases over Redeem Italy — service to the strong is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +3 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 33 to 16.

## Turn 14 — Early April 1806
  - MISSION ADVISOR branch 2 (follow the counsel) → `improve relations with Denmark`
- CMD `improve relations with Denmark` → ✓ Sire, I shall begin efforts to improve relations with Denmark. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #15 → start_mission
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 12258 · net +1391 · threat 12 · provinces 21 (+0) · ceiling 128166 · army 136605 · vassals Holland 88 · Switzerland 73
  - NET income 1843 · trade 572 · admin 50 · tribute 225 · upkeep 1176 · charges 123
- MISSION Improving Relations — Denmark · net +7 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: THE LAWS: Austria enacts the New Infantry Regulations — +5 morale from every drill.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (73 → 83); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13428 · net +1156 · threat 10 · provinces 21 (+0) · ceiling 109750 · army 136605 · vassals Holland 87 · Switzerland 83
  - NET income 1847 · trade 572 · admin 50 · upkeep 1176 · charges 137
- MISSION Improving Relations — Denmark · net +7 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire, I believe Denmark may be ready to discuss improved relations. The diplomatic winds favor us.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 14589 · net +1147 · threat 8 · provinces 21 (+0) · ceiling 110166 · army 136605 · vassals Holland 86 · Switzerland 83
  - NET income 1852 · trade 572 · admin 50 · upkeep 1176 · charges 151
- MISSION Improving Relations — Denmark · net +7 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: THE LAWS: Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as service to the strong.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Russian-led alignment leads the current largest alignment at 40% of active European bloc power.
  - LOG ai_ai_proposal_refused: Austria rebuffs Sweden (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Denmark defensive alliance
- LEDGER treasury 15740 · net +1138 · threat 6 · provinces 21 (+0) · ceiling 110500 · army 136605 · vassals Holland 85 · Switzerland 83
  - NET income 1856 · trade 572 · admin 50 · upkeep 1176 · charges 164
- MISSION Improving Relations — Denmark · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: THE LAWS: Russia enacts Arakcheev's Artillery — artillery levies cost 15% less (×0.85).
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
- DIPLO +6 medium/low (law_enacted_abroad ×3, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
  - MAILBOX #14 Denmark incoming_proposal: Denmark — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Denmark, defensive_alliance #17 → accept
  - POPUP proposal_result: You have accepted Denmark's proposal. Treaty signed: Non-Aggression → Defensive Alliance with Denmark. → display-only
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16883 · net +1129 · threat 4 · provinces 21 (+0) · ceiling 110916 · army 136605 · vassals Holland 84 · Switzerland 83
  - NET income 1861 · trade 572 · admin 50 · upkeep 1176 · charges 178
- MISSION Improving Relations — Denmark · net +7 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Denmark and France have signed the Defensive Alliance.
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18016 · net +1119 · threat 1 · provinces 21 (+0) · ceiling 111250 · army 136605 · vassals Holland 83 · Switzerland 83
  - NET income 1865 · trade 572 · admin 50 · upkeep 1176 · charges 192
- MISSION Improving Relations — Denmark · net +7 a turn · ≈7 turns to +100 at the present rate · beat running
- DISPATCH: Talleyrand reports: 7 diplomatic points available (base 3, +1 skill, +1 authority, +2 carried from last turn).
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Denmark alliance
- LEDGER treasury 19140 · net +1448 · threat 0 · provinces 21 (+0) · ceiling 139750 · army 136605 · vassals Holland 82 · Switzerland 83
  - NET income 1870 · trade 572 · admin 50 · tribute 337 · upkeep 1176 · charges 205
- MISSION Improving Relations — Denmark · net +7 a turn · ≈6 turns to +100 at the present rate · beat running
- DISPATCH: THE LAWS: Austria enacts the Generalissimus — every levy costs 10% less (×0.9).
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, agenda_shift)

---
finished: **completed** · commands 23 · popups 29 · battles 16
