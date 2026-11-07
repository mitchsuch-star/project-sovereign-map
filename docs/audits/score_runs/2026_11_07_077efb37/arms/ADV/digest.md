# Playtest digest — ADV

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "missions": "advisor"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `077efb374d7c` · content `e96449bb3b47` · driver `bd054bd265d8`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
  - MISSION ADVISOR branch 1 (reassure an ally) → `reassure Spain`
- CMD `reassure Spain` → ✓ Sire, I shall begin efforts to reassure Spain. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #1 → start_mission
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena
  - ⚔ Archduke Charles (lost 4611) vs Massena (lost 4941) — Stalemate. Massena and Archduke Charles glare at each other across the field. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1445 · net +892 · threat 68 · provinces 28 · ceiling 8757 · army 184059 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2684 · blockade 219 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈19 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +10 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, sovereign_takes_field, diplomatic_mission_progress, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Mack attacks Lannes · Archduke Charles attacks Teulie
  - ⚔ Archduke Charles (lost 4572) vs Massena (lost 4401, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Mack (lost 5236) vs Lannes (lost 2415, own corps) — Reinforcement from Napoleon kept Lannes standing, Sire — but neither side yielded the ground.
  - ⚔ Archduke Charles (lost 2631) vs Teulie (lost 1386, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×3, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2008 · net +1254 · threat 66 · provinces 28 (+0) · ceiling 10434 · army 171452 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2575 · trade 450 · admin 50 · tribute 829 · upkeep 2278 · charges 1 · blockade 281 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈18 turns to +100 at the present rate · beat running
- DISPATCH: Sire — St Petersburg now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_we_threshold ×2, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 7 actions, 4 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Mack attacks Bernadotte · Mack attacks Deroy · Archduke Charles attacks Teulie
  - ⚔ Archduke Charles (lost 2837) vs Massena (lost 4255, own corps) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Mack (lost 2834) vs Bernadotte (lost 4591) — Bernadotte was close. A period of drilling could have changed the outcome.
  - ⚔ Mack (lost 3456) vs Deroy (lost 4290) — Neither Deroy nor Mack could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 1624) vs Teulie (lost 1532, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×4, stance_change×1, fortify×1, naval_expedition×1
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 3,553 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last…
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 3,553 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3072 · net +1557 · threat 64 · provinces 28 (+0) · ceiling 12471 · army 157968 · vassals Holland 92 · Kingdom of Italy 87 · Switzerland 86
  - NET income 2577 · trade 525 · admin 50 · tribute 799 · upkeep 1798 · charges 177 · blockade 329 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈17 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - TURN EVENTS 2
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Mack attacks Bernadotte · Archduke Charles attacks Bernadotte · Archduke Charles attacks Deroy
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - ⚔ Mack (lost 1840) vs Bernadotte (lost 3956) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 667) vs Bernadotte (lost 4641) — A grievous defeat for Bernadotte, Sire. The losses are severe. And Bernadotte was taken on that field — Austria holds h…
  - ⚔ Archduke Charles (lost 1595) vs Deroy (lost 3579) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×3, stance_change×1, move×1, wait×1
- LEDGER treasury 4928 · net +1692 · threat 62 · provinces 28 (+0) · ceiling 13140 · army 144826 · vassals Holland 88 · Kingdom of Italy 71 · Switzerland 80
  - NET income 2578 · trade 587 · admin 50 · tribute 802 · upkeep 1264 · charges 603 · blockade 368 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte captured · Massena trust 60 Questioning glory 0 (#6) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈16 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +8 medium/low (diplomatic_treaty_signed ×2, province_changed_hands, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG moment: Britain decrees the Magazines for 8 turns (5 authority)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG ai_ai_proposal_refused: Britain rebuffs Portugal (open borders agreement)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Munich · Mack attacks Munich · Mack attacks Milan
  - 🏴 Austria: Mack attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - verbs: attack×3, fortify×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 6592 · net +1307 · threat 60 · provinces 28 (+0) · ceiling 12836 · army 144826 · vassals Holland 88 · Kingdom of Italy 71 · Switzerland 78
  - NET income 2580 · trade 512 · admin 50 · tribute 799 · upkeep 1264 · charges 960 · blockade 320 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte captured · Massena trust 60 Questioning glory 0 (#6) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — not every court of the league has struck us. Britain has no road to us but the sea, and Normandy is a defended shore: she can land only by expedition, 15,000 men at a time. Russia has an open …
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +7 medium/low (enemy_marshal_commissioned, province_changed_hands, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG moment: Russia decrees the Magazines for 8 turns (5 authority)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (78 → 88); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Milan
  - 🏴 Austria: Archduke John attacks Milan — The garrison of Milan is destroyed. · Region captured: Milan (was Kingdom of Italy) (secured)
  - verbs: attack×1, form_square×1, move×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 7589 · net +770 · threat 58 · provinces 28 (+0) · ceiling 11213 · army 144826 · vassals Holland 88 · Kingdom of Italy 71 · Switzerland 87
  - NET income 2582 · trade 512 · admin 50 · tribute 487 · upkeep 1264 · charges 1187 · blockade 320 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte captured · Massena trust 60 Questioning glory 0 (#6) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Milan has been taken by Austria.
  - TURN EVENTS 2
- DIPLO +4 medium/low (province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG moment: The Squadron for Santo Domingo — an affair of state is laid before the Emperor
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 7 — Late December 1805
  - MAILBOX #9 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #10 → reject_ai_proposal
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Mack attacks Lannes · Archduke Charles attacks Lannes
  - ⚔ Mack (lost 4016) vs Lannes (lost 1517, own corps) — Napoleon arrived in time to steady Lannes's position. The field was held, nothing further.
  - ⚔ Archduke Charles (lost 1998) vs Lannes (lost 1895, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×2
- LEDGER treasury 8234 · net +701 · threat 56 · provinces 28 (+0) · ceiling 11410 · army 139300 · vassals Holland 88 · Kingdom of Italy 71 · Switzerland 86
  - NET income 2567 · trade 512 · admin 50 · tribute 487 · upkeep 1132 · charges 1373 · blockade 320 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte captured · Massena trust 60 Questioning glory 0 (#6) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈13 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Britain's gold reaches Russia — the subsidy stands at 200 this season.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)
  - LOG moment: The Squadron for Santo Domingo — the Emperor answers: Ferrand must hold alone

## Turn 8 — Early January 1806
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Mack attacks Lannes
  - ⚔ Mack (lost 3395) vs Lannes (lost 1139, own corps) — Napoleon reached the field beside Lannes, Sire — it saved the line, no more.
  - verbs: attack×1
- LEDGER treasury 9043 · net +723 · threat 54 · provinces 28 (+0) · ceiling 12736 · army 137010 · vassals Holland 88 · Kingdom of Italy 71 · Switzerland 85
  - NET income 2561 · trade 512 · admin 50 · tribute 487 · upkeep 1100 · charges 1377 · blockade 320 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte captured · Massena trust 60 Questioning glory 0 (#6) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — not every court of the league has struck us. Britain has no road to us but the sea, and Normandy is a defended shore: she can land only by expedition, 15,000 men at a time. Russia has an open …
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,272g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the w…
  - TURN EVENTS 2
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)

## Turn 9 — Late January 1806
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke Charles attacks Provence
  - 🏴 Austria: Archduke Charles attacks Massena — Piedmont CAPTURED! (was Kingdom of Italy) (secured)
  - 🏴 Austria: Archduke Charles attacks Provence — Region captured: Provence (was France) (secured)
  - ⚔ Archduke Charles (lost 735) vs Massena (lost 5886) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×2, unfortify×1, move×1, naval_expedition×1
- LEDGER treasury 9054 · net +209 · threat 41 · provinces 27 (-1) · ceiling 9942 · army 131124 · vassals Holland 86 · Switzerland 82
  - NET income 2412 · trade 512 · admin 50 · tribute 337 · upkeep 1036 · charges 1656 · blockade 320 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte captured · Massena trust 60 Questioning glory 0 (#6) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a marc…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 6,000 men ashore at Andalusia.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 4
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- DIPLO +10 medium/low (province_changed_hands ×2, law_enacted_abroad ×2, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, balance_of_europe_shifted, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)

## Turn 10 — Early February 1806
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 7 actions, 6 attacks — Russia, Prussia, the Ottoman Empire and 6 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Cuesta · Shrapnel bombards Blake · Archduke Charles attacks Massena · Archduke Charles attacks Savoy
  - 🏴 Austria: Archduke Charles attacks Massena — Lyonnais CAPTURED! (was France) (secured)
  - 🏴 Austria: Archduke Charles attacks Savoy — Region captured: Savoy (was France) (secured)
  - ⚔ Archduke Charles (lost 235) vs Massena (lost 6021) — Massena's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Cuesta (lost 853) vs Shrapnel (lost 988) — An inconclusive affair. Both sides bloodied but unbroken. — The Line Holds +15% (Shrapnel)
  - ⚔ Blake (lost 148, own corps) vs Shrapnel (lost 1042) — The toll on Shrapnel's forces is heavy, Sire. This defeat will be felt. — The Line Holds +15% (Shrapnel)
  - verbs: attack×6, move×1
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 8884 · net +69 · threat 38 · provinces 25 (-2) · ceiling 9162 · army 125103 · vassals Holland 84 · Switzerland 79
  - NET income 2254 · trade 512 · admin 50 · tribute 337 · upkeep 984 · charges 1690 · blockade 320 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte captured · Massena trust 60 Questioning glory 0 (#6) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil.
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War for Lyonnais — Britain + Austria + Russia. Asking 2750 gold.
  - RAIL allegiance_settled: The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 4
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: And Saxony stirs at its own design.
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, paymaster_subsidy, agenda_shift ×3, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: Ottoman rebuffs Austria (design ask)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 11 — Late February 1806
  - MAILBOX #10 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Lyonnais — the table with Austria + Russia (2 pairs resolved). Status quo: Lyonnais, Provence and Savoy stay Austrian by the treaty. Prisoners: Bernadotte comes home to Paris under this peace. Prisoners: Teulie comes home to Paris under this peace. → display-only
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight. — Blake attacks Shrapnel
  - ⚔ Blake (lost 35, own corps) vs Shrapnel (lost 808) — The line gave way. Shrapnel is falling back, and not in good order. — The Line Holds +15% (Shrapnel)
  - verbs: attack×1
- ENVOYS WAITING 2 · Britain settlement offer · The Secretariat moment letter
- LEDGER treasury 6824 · net +529 · threat 16 · provinces 25 (+0) · ceiling 9294 · army 135103 · vassals Holland 84 · Switzerland 78
  - NET income 2256 · trade 512 · admin 50 · tribute 337 · upkeep 1104 · charges 1032 · contributions 80 · blockade 320 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lyonnais, Provence and Savoy lie in enemy hands. Austria holds them.
  - RAIL status_quo_conceded: Lyonnais, Provence and Savoy — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of the War for Lyonnais — the table with Austria + Russia: Gold indemnity: 2750 gold from France to Austria.
  - RAIL settlement_offer_arrival: Britain's terms to settle the War with Britain, under Russia's good offices.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 1
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, province_changed_hands ×2, diplomatic_dp_regen, diplomatic_mission_progress, agenda_shift ×2)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG moment: The Proclamation — an affair of state is laid before the Emperor
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 38 to 19; Britain remains at war with us.
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG ai_ai_proposal_refused: 2 approaches from Sardinia and Hesse are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 12 — Early March 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer, under Russia's good offices → activated
  - MAILBOX #12 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #14 → reject_ai_proposal
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #15 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with Britain — the table with Britain (3 pairs resolved). → display-only
  - POPUP diplomatic_dialogue: moment_letter #14 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Brunswick attacks Wallmoden · Brunswick attacks Hanover
  - 🏴 Prussia: Brunswick attacks Wallmoden — Osnabruck CAPTURED! (was Hanover) (secured)
  - ⚔ Brunswick (lost 356) vs Wallmoden (lost 1129) — A grievous defeat for Wallmoden, Sire. The losses are severe. And Wallmoden was taken on that field — Prussia holds him. — Frederick's Drill +10% (Brunswick)
  - verbs: attack×2, wait×1, recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 8394 · net +1413 · threat 13 · provinces 25 (+0) · ceiling 22520 · army 135103 · vassals Holland 82 · Switzerland 77
  - NET income 2257 · trade 512 · admin 50 · tribute 337 · upkeep 1104 · charges 639
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Reassuring Ally — Spain · net +3 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — peace with Britain is signed. A white peace — the map stands as it was.
  - RAIL settlement_summary: Sire, the white peace of the War with Britain — the table with Britain writes no clause: each side keeps what it holds on the day of signing, titled …
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 1 more province. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +9 medium/low (province_changed_hands, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift ×2)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG moment: The Proclamation — the Emperor answers: Let the army march in silence
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 13 — Late March 1806
  - MAILBOX #13 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #16 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - MISSION ADVISOR: recalling Talleyrand — branch 1 has held the desk 12 turns (limit 12)
- CMD `Talleyrand, cancel mission with Spain` → ✓ Talleyrand's mission to Spain has been cancelled.
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 9472 · net +1195 · threat 10 · provinces 25 (+0) · ceiling 21420 · army 135103 · vassals Holland 91 · Switzerland 76
  - NET income 2259 · trade 512 · admin 50 · tribute 225 · upkeep 1104 · charges 747
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — 3 turns now with Lyonnais, Provence and Savoy in enemy hands. The country counts every one of them.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - RAIL crisis_brewing: THE BREWING CRISIS: Hesse will move on Hanover. You may compensate (1,296g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war…
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,850 gold. Prussia is now free to look elsewhere.
- COURTS: The court of Saxony eases over The Wettin Crown — alliance is now the length of its tether.
- DIPLO +6 medium/low (province_changed_hands ×2, enemy_marshal_commissioned, diplomatic_dp_regen, agenda_shift ×2)
  - LOG ai_ai_proposal_refused: Holland rebuffs Hesse (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 1 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 14 — Early April 1806
  - MISSION ADVISOR branch 2 (follow the counsel) → `improve relations with PapalStates`
- CMD `improve relations with PapalStates` → ✓ Sire, I shall begin efforts to improve relations with Papal States. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #17 → start_mission
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10668 · net +1077 · threat 7 · provinces 25 (+0) · ceiling 21430 · army 135103 · vassals Holland 90 · Switzerland 75
  - NET income 2260 · trade 512 · admin 50 · tribute 225 · upkeep 1104 · charges 866
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Improving Relations — Papal States · net +8 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Hesse moves toward war with Hanover. The design is open; the timing is not.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - RAIL crisis_passed: Hesse stands down over Hanover, Sire — the moment passed — opportunism decayed.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 15 — Late April 1806
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #18 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (75 → 85); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 11522 · net +768 · threat 4 · provinces 25 (+0) · ceiling 19200 · army 135103 · vassals Holland 89 · Switzerland 85
  - NET income 2262 · trade 512 · admin 50 · upkeep 1104 · charges 952
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Improving Relations — Papal States · net +7 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Austria and Russia would now join a league against us (relations −75 and −67). The Balance of Europe names the price to keep each out.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12292 · net +693 · threat 1 · provinces 25 (+0) · ceiling 19220 · army 135103 · vassals Holland 88 · Switzerland 85
  - NET income 2264 · trade 512 · admin 50 · upkeep 1104 · charges 1029
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Improving Relations — Papal States · net +7 a turn · ≈13 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Britain would now join a league against us — relations −85. No design to buy off; her league place is her relations. The price to keep her out: Talleyrand brings her to −10 in 9 turns (9 DP).
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 12986 · net +625 · threat 0 · provinces 25 (+0) · ceiling 19230 · army 135103 · vassals Holland 87 · Switzerland 85
  - NET income 2265 · trade 512 · admin 50 · upkeep 1104 · charges 1098
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Improving Relations — Papal States · net +7 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the enemy has held Lyonnais, Provence and Savoy 7 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG moment: The Throne of Holland — a letter of the record is laid before the Emperor

## Turn 18 — Early June 1806
  - MAILBOX #15 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #19 → reject_ai_proposal
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13613 · net +564 · threat 0 · provinces 25 (+0) · ceiling 19250 · army 135103 · vassals Holland 86 · Switzerland 85
  - NET income 2267 · trade 512 · admin 50 · upkeep 1104 · charges 1161
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Improving Relations — Papal States · net +7 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG moment: The Throne of Holland — the Emperor answers: Keep the Republic

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 14178 · net +509 · threat 0 · provinces 25 (+0) · ceiling 19260 · army 135103 · vassals Holland 85 · Switzerland 85
  - NET income 2268 · trade 512 · admin 50 · upkeep 1104 · charges 1217
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Improving Relations — Papal States · net +7 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — the bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Britain.
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_mission_progress, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 36% of active European bloc power.

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 3 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · PapalStates non aggression
- LEDGER treasury 14689 · net +797 · threat 0 · provinces 25 (+0) · ceiling 22650 · army 135103 · vassals Holland 84 · Switzerland 85
  - NET income 2270 · trade 512 · admin 50 · tribute 337 · upkeep 1104 · charges 1268
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Teulie trust 60 Questioning glory 0
- MISSION Improving Relations — Papal States · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — an envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

---
finished: **completed** · commands 23 · popups 28 · battles 20
