# Playtest digest — rs0928-ambient

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `91796f250248` · content `8f597da58501` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual…
  - ⚔ Archduke Charles (lost 4431) vs Massena (lost 5919) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1631 · net +1126 · threat 68 · provinces 28 · ceiling 29330 · army 183081 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · blockade 219 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual… · Mack delivers an effective strike. Mack gains the advantage over Bernadotte. Casualties: Mack 2,804, Bernadotte 4,583. … · Mack holds them at Franconia while allies attack from Swabia! (+1 coordination)
  - ⚔ Archduke Charles (lost 3902) vs Massena (lost 5261) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 2804) vs Bernadotte (lost 4583) — The margin was slim. Training and preparation would serve Bernadotte well.
  - ⚔ Mack (lost 3373) vs Deroy (lost 4534) — Neither Deroy nor Mack could claim the field. The armies remain locked.
  - verbs: attack×3
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2534 · net +1368 · threat 66 · provinces 28 (+0) · ceiling 29034 · army 173237 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 350 · admin 50 · tribute 856 · upkeep 2142 · charges 27 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,583 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_proposal_rejected: We rejected the Ottoman Empire's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Portugal's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Mack gains the advantage over Bernadotte. Casualties: Mack 1,752, Bernadotte … · ArchdukeCharles struggles in a costly engagement. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualtie… · ArchdukeCharles flanks from Tyrol while allies attack from Franconia! (+1 coordination) · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharle…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Franconia. (1,175 lost to march) Franconia has been captured by Austria!
  - ⚔ Mack (lost 1752) vs Bernadotte (lost 5237) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 3474) vs Massena (lost 4127) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 355) vs Bernadotte (lost 3952) — A grievous defeat for Bernadotte, Sire. The losses are severe. And Bernadotte was taken on that field — Austria holds h…
  - ⚔ Archduke Charles (lost 1927) vs Deroy (lost 3616) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×4, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3778 · net +1793 · threat 64 · provinces 28 (+0) · ceiling 31444 · army 155879 · vassals Holland 94 · Kingdom of Italy 98 · Switzerland 88
  - NET income 2590 · trade 350 · admin 50 · tribute 829 · upkeep 1602 · charges 115 · blockade 219 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 27 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Saxony's open borders agreement proposal
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeCharle… · Mack assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). Mack loses 3,063 troops. Garrison holds — 5,000 … · Mack assaults the Munich garrison! Garrison collapses (5,000 -> 0). Mack loses 1,702 troops in the assault. Mack marche… · Mack's attack meets fierce resistance. Brutal stalemate between Mack and Massena. Heavy casualties on both sides: Mack …
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -85g, Bavaria -125g. Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 2184) vs Massena (lost 4336) — A narrow defeat for Massena, Sire. Better-prepared troops might have tipped the balance.
  - ⚔ Mack (lost 2778) vs Massena (lost 2768) — Stalemate. Massena and Mack glare at each other across the field.
  - verbs: attack×4
- LEDGER treasury 5282 · net +1717 · threat 62 · provinces 28 (+0) · ceiling 28603 · army 148775 · vassals Holland 92 · Kingdom of Italy 98 · Switzerland 84
  - NET income 2590 · trade 237 · admin 50 · tribute 712 · upkeep 1392 · charges 241 · blockade 149 · admiralty 90
- DISPATCH: 2 satellites drifted — Holland and Switzerland.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected the Papal States' open borders agreement proposal
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Massena. Casualties: ArchdukeChar… · Mack flanks from Munich while allies attack from Milan! (+1 coordination)
  - 🏴 Austria: [!] Massena's troops are BROKEN (morale 0%)! FORCED RETREAT! Mack advances into Milan. (877 lost to march) Milan has been captured by Austria!
  - ⚔ Archduke Charles (lost 1527) vs Massena (lost 4385) — Massena was close. A period of drilling could have changed the outcome.
  - ⚔ Mack (lost 983) vs Massena (lost 6737) — A grievous defeat for Massena, Sire. The losses are severe.
  - verbs: attack×2, unfortify×1, stance_change×1, move×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Switzerland client petition
- LEDGER treasury 6652 · net +1691 · threat 60 · provinces 28 (+0) · ceiling 21126 · army 137569 · vassals Holland 88 · Kingdom of Italy 94 · Switzerland 78
  - NET income 2590 · trade 237 · admin 50 · tribute 712 · upkeep 1116 · charges 543 · blockade 149 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: 7 approaches to Austria and Spain are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - MAILBOX #8 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #10 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #8 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #10 → refuse the petition
  - POPUP diplomatic_dialogue: Prussia, open_borders #8 → reject
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (78 → 68); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → refuse the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Massena. Casualties: Arch…
  - ⚔ Archduke Charles (lost 127, own corps) vs Massena (lost 4312) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×1, fortify×1, wait×1
- ORDER Massena [awaiting_response]: Massena is cornered at Piedmont with 4,071 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Piedmont with 4,071 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 8043 · net +1430 · threat 58 · provinces 28 (+0) · ceiling 19605 · army 129186 · vassals Holland 86 · Kingdom of Italy 92 · Switzerland 63
  - NET income 2590 · trade 237 · admin 50 · tribute 562 · upkeep 1024 · charges 746 · blockade 149 · admiralty 90
- DISPATCH: Sire — Massena was mauled at Piedmont: half of his corps — 4,312 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected the Ottoman Empire's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 7 — Late December 1805
  - MAILBOX #11 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #11 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (177 lost to march) Captured: France → Austria · ArchdukeCharles marches from Piedmont into Lyonnais unopposed! (408 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (177 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Lyonnais unopposed! (408 lost to march) Captured: France → Austria
  - verbs: attack×2
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 9237 · net +1023 · threat 45 · provinces 26 (-2) · ceiling 17299 · army 129186 · vassals Holland 86 · Switzerland 60
  - NET income 2360 · trade 262 · admin 50 · tribute 562 · upkeep 1040 · charges 917 · blockade 164 · admiralty 90
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 36% of active European bloc power.
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 8 — Early January 1806
  - MAILBOX #12 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #12 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 8 actions, 3 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Lyonnais into Limousin unopposed! (382 lost to march) Captured: France → Austria · ArchdukeJohn marches from Provence into Languedoc unopposed! (175 lost to march) Captured: France → Austria · Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 604, Paget …
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Limousin unopposed! (382 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Languedoc unopposed! (175 lost to march) Captured: France → Austria
  - ⚔ Castanos (lost 604) vs Paget (lost 1979) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: move×4, attack×3, unfortify×1
- LEDGER treasury 9683 · net +351 · threat 42 · provinces 24 (-2) · ceiling 11875 · army 129186 · vassals Holland 86 · Switzerland 57
  - NET income 2158 · trade 262 · admin 50 · tribute 562 · upkeep 1060 · charges 1229 · contributions 138 · blockade 164 · admiralty 90
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 1
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
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
- ENVOYS WAITING 2 · Austria peace · Prussia open borders
- LEDGER treasury 9652 · net +337 · threat 39 · provinces 21 (-3) · ceiling 12071 · army 129186 · vassals Holland 86 · Switzerland 54
  - NET income 1870 · trade 262 · admin 50 · tribute 562 · upkeep 1088 · charges 1065 · blockade 164 · admiralty 90
- DISPATCH: Sire — Berry has fallen. Enemy colours fly over French homeland soil. Paget's corps of 2,634 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of …
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia, Naples and Denmark (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #13 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #14 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Austria, peace #13 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #14 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Austria, peace #13 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #14 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Normandy into Artois unopposed! (173 lost to march) Captured: France → Austria · ArchdukeJohn marches from Gascony into Guyenne unopposed! (170 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Normandy into Artois unopposed! (173 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Gascony into Guyenne unopposed! (170 lost to march) Captured: France → Austria
  - verbs: attack×2
- LEDGER treasury 9749 · net +59 · threat 38 · provinces 19 (-2) · ceiling 10160 · army 129186 · vassals Holland 86 · Switzerland 51
  - NET income 1650 · trade 262 · admin 50 · tribute 562 · upkeep 1108 · charges 1103 · blockade 164 · admiralty 90
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces…
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 43% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 4 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Normandy into Maine unopposed! (859 lost to march) Captured: France → Britain · ArchdukeJohn marches from Guyenne into Bordelais unopposed! (336 lost to march) Captured: France → Austria · Mack marches from Piedmont into Savoy unopposed! (1,262 lost to march) Captured: France → Austria · ArchdukeCharles marches from Artois into Champagne unopposed! (171 lost to march) Captured: France → Austria
  - 🏴 Britain: Moore marches from Normandy into Maine unopposed! (859 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeJohn marches from Guyenne into Bordelais unopposed! (336 lost to march) Captured: France → Austria
  - 🏴 Austria: Mack marches from Piedmont into Savoy unopposed! (1,262 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Artois into Champagne unopposed! (171 lost to march) Captured: France → Austria
  - verbs: attack×4
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 9488 · net -248 · threat 37 · provinces 15 (-4) · ceiling 7782 · army 129186 · vassals Holland 86 · Switzerland 48
  - NET income 1370 · trade 262 · admin 50 · tribute 562 · upkeep 1148 · charges 1090 · blockade 164 · admiralty 90
- DISPATCH: Sire — Maine has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3899 gold.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Britain (Defensive Alliance)

## Turn 12 — Early March 1806
  - MAILBOX #15 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: 5 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Maine into Anjou unopposed! (785 lost to march) Captured: France → Britain · ArchdukeCharles marches from Champagne into Burgundy unopposed! (169 lost to march) Captured: France → Austria · ArchdukeJohn marches from Bordelais into Bearn unopposed! (329 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Flanders garrison! Garrison: 12,000 -> 6,759 (-5,241). ArchdukeCharles loses 3,333 troops.…
  - 🏴 Britain: Moore marches from Maine into Anjou unopposed! (785 lost to march) Captured: France → Britain
  - 🏴 Austria: ArchdukeCharles marches from Champagne into Burgundy unopposed! (169 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles moves from Burgundy to Orleanais. Orleanais falls to Austria!
  - 🏴 Austria: ArchdukeJohn marches from Bordelais into Bearn unopposed! (329 lost to march) Captured: France → Austria
  - verbs: attack×4, move×1
- LEDGER treasury 8490 · net -633 · threat 36 · provinces 11 (-4) · ceiling 4797 · army 129186 · vassals Holland 86 · Switzerland 40
  - NET income 1048 · trade 262 · admin 50 · tribute 562 · upkeep 1188 · charges 1113 · blockade 164 · admiralty 90
- DISPATCH: Sire — Anjou has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - RAIL balance_of_europe_shifted: British Interest leads the current largest alignment at 51% of active European bloc power.
  - TURN EVENTS 1
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Anjou into Brittany unopposed! (493 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Anjou into Brittany unopposed! (493 lost to march) Captured: France → Britain
  - verbs: attack×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 7308 · net -961 · threat 25 · provinces 10 (-1) · ceiling 2615 · army 129186 · vassals Holland 76
  - NET income 971 · trade 262 · admin 50 · tribute 337 · upkeep 1200 · charges 1087 · contributions 40 · blockade 164 · admiralty 90
- DISPATCH: Sire — Brittany has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - RAIL diplomatic_alliance_cascade: Spain enters the war via alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - TURN EVENTS 1
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG balance_of_europe_shifted: British Interest leads the current largest alignment at 51% of active European bloc power.

## Turn 14 — Early April 1806
  - MAILBOX #16 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #16 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Hesse non aggression
- LEDGER treasury 6550 · net -640 · threat 22 · provinces 10 (+0) · ceiling 2949 · army 129186 · vassals Holland 78
  - NET income 974 · trade 262 · admin 50 · tribute 337 · upkeep 1200 · charges 809 · blockade 164 · admiralty 90
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +3 medium/low (diplomatic_dp_regen, sovereign_takes_field, paymaster_subsidy)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 15 — Late April 1806
  - MAILBOX #17 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #18 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 5736 · net -657 · threat 19 · provinces 10 (+0) · ceiling 2625 · army 129186 · vassals Holland 80
  - NET income 977 · trade 262 · admin 50 · tribute 337 · upkeep 1200 · charges 789 · contributions 40 · blockade 164 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Nivernais. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 1
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, diplomatic_coalition_dissolved, blockade_broken)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG coalition_dissolved: Coalition against France has dissolved — Austria, Britain, Russia and Switzerland remain at war with us.
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain (defensive alliance)

## Turn 16 — Early May 1806
  - MAILBOX #18 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #19 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack marches from Burgundy into Ile-de-France unopposed! (464 lost to march) Captured: France → Austria
  - 🏴 Austria: Mack marches from Burgundy into Ile-de-France unopposed! (464 lost to march) Captured: France → Austria
  - verbs: attack×1
- ENVOYS WAITING 3 · Prussia open borders · Britain settlement offer · Switzerland settlement offer
- LEDGER treasury 4834 · net -720 · threat 18 · provinces 9 (-1) · army 129186 · vassals Holland 82
  - NET income 940 · trade 262 · admin 50 · tribute 337 · upkeep 1228 · charges 607 · contributions 220 · blockade 164 · admiralty 90
- DISPATCH: Sire — Ile-de-France has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 2294 gold.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 17 — Late May 1806
  - MAILBOX #19 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #20 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #21 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #20 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #22 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer #21 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders #20 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #22 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack marches from Ile-de-France into Picardy unopposed! (431 lost to march) Captured: France → Austria · Mack assaults the Flanders garrison! Garrison collapses (6,759 -> 0). Mack loses 1,877 troops in the assault. Mack marc…
  - 🏴 Austria: Mack marches from Ile-de-France into Picardy unopposed! (431 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -93g, France -168g. Captured: France → Austria
  - verbs: attack×2
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 3699 · net -762 · threat 17 · provinces 7 (-2) · army 129186 · vassals Holland 84
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1272 · charges 375 · contributions 260 · blockade 164 · admiralty 90
- DISPATCH: Sire — Picardy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 18 — Early June 1806
  - MAILBOX #22 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #23 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 2977 · net -565 · threat 18 · provinces 7 (+0) · army 129186 · vassals Holland 86
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1272 · charges 218 · contributions 220 · blockade 164 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Austria's peace treaty proposal
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Austria (defensive alliance)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 2372 · net -471 · threat 19 · provinces 7 (+0) · army 129186 · vassals Holland 88
  - NET income 750 · trade 262 · admin 50 · tribute 337 · upkeep 1272 · charges 84 · contributions 260 · blockade 164 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Britain: Moore moves from Burgundy to Nivernais. Nivernais falls to Britain!
  - verbs: move×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 1873 · net -415 · threat 18 · provinces 6 (-1) · army 129186 · vassals Holland 90
  - NET income 710 · trade 262 · admin 50 · tribute 337 · upkeep 1300 · contributions 220 · blockade 164 · admiralty 90
- DISPATCH: Sire — Nivernais has fallen. Enemy colours fly over French homeland soil. Moore's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any garris…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 21 — Late July 1806
  - MAILBOX #23 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #24 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · Switzerland settlement offer
- LEDGER treasury 1458 · net -415 · threat 17 · provinces 6 (+0) · army 129186 · vassals Holland 92
  - NET income 710 · trade 262 · admin 50 · tribute 337 · upkeep 1300 · contributions 220 · blockade 164 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 7 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 749 gold.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 22 — Early August 1806
  - MAILBOX #24 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #25 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #26 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #25 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #27 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer #26 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, non_aggression #25 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #27 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 1 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Orleanais into Ardennes unopposed! (196 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Orleanais into Ardennes unopposed! (196 lost to march) Captured: France → Britain
  - verbs: attack×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 1195 · net -263 · threat 14 · provinces 5 (-1) · army 129186 · vassals Holland 94
  - NET income 670 · trade 262 · admin 50 · tribute 337 · upkeep 1328 · blockade 164 · admiralty 90
- DISPATCH: Sire — Ardennes has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 23 — Late August 1806
  - MAILBOX #27 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #28 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 932 · net -263 · threat 13 · provinces 5 (+0) · army 129186 · vassals Holland 96
  - NET income 670 · trade 262 · admin 50 · tribute 337 · upkeep 1328 · blockade 164 · admiralty 90
- DISPATCH: Holland loyalty 96 (+2): a common enemy
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 24 — Early September 1806
  - MAILBOX #28 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #29 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 669 · net -263 · threat 12 · provinces 5 (+0) · army 129186 · vassals Holland 98
  - NET income 670 · trade 262 · admin 50 · tribute 337 · upkeep 1328 · blockade 164 · admiralty 90
- DISPATCH: Holland loyalty 98 (+2): a common enemy
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 369 · net -300 · threat 11 · provinces 5 (+0) · army 129186 · vassals Holland 100
  - NET income 670 · trade 262 · admin 50 · tribute 300 · upkeep 1328 · blockade 164 · admiralty 90
- DISPATCH: Sire — Brabant has been taken by Britain.
  - TURN EVENTS 1
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Britain settlement offer · Switzerland settlement offer
- LEDGER treasury 69 · net -300 · threat 10 · provinces 5 (+0) · army 129186 · vassals Holland 100
  - NET income 670 · trade 262 · admin 50 · tribute 300 · upkeep 1328 · blockade 164 · admiralty 90
- DISPATCH: War Purpose: Defense vs Britain — the homeland — 5 of 28 provinces held (ticking: +25, +1/turn)  |  Settlement: Favorable Terms — theirs to impose (-22)
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 147 gold.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
  - MAILBOX #29 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #30 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #30 → reject_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_settlement_offer #31 → reject_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #30 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury -231 · net +364 · threat 7 · provinces 5 (+0) · ceiling 3830 · army 129186 · vassals Holland 100
  - NET income 670 · trade 262 · admin 50 · tribute 300 · upkeep 664 · blockade 164 · admiralty 90
- DISPATCH: Sire — Spain and Switzerland have made peace without us.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Spain and Switzerland have made their peace without France. Both courts are spent; their side of the war ends while the greater war goe…
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain, Russia and Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain, Russia and Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain, Russia and Austria (defensive alliance)

## Turn 28 — Early November 1806
  - MAILBOX #31 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #32 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 3 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget attacks with overwhelming force. Lannes holds the line. Casualties: Paget's army 3,878, Lannes's army 1,955. Both… · Paget's forces advance steadily. Murat holds the line. Casualties: Paget 2,315, Murat's army 1,146. Both armies remain … · Mack launches a decisive assault. Soult holds the line. Casualties: Mack's army 11,397, Soult's army 2,825. Both armies…
  - ⚔ Paget (lost 1989, own corps) vs Lannes (lost 879, own corps) — Lannes fought without Soult and Napoleon's support. The roads, or the will, proved insufficient.
  - ⚔ Paget (lost 2315) vs Murat (lost 498, own corps) — Napoleon's timely arrival aided Murat. Soult, however, was conspicuously absent.
  - ⚔ Mack (lost 7807, own corps) vs Soult (lost 730, own corps) — Reinforcements! Ney, Davout, Lannes and Murat marched onto the field beside Soult. The enemy's advantage melted away.
  - verbs: attack×3
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
  - POPUP diplomatic_dialogue: Hesse, non_aggression #33 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Switzerland, armistice_losing #34 → reject
  - POPUP proposal_result: You have rejected Switzerland's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 2 · Hesse non aggression · Switzerland armistice losing
- LEDGER treasury -97 · net +429 · threat 9 · provinces 5 (+0) · ceiling 4123 · army 117204 · vassals Holland 100
  - NET income 635 · trade 262 · admin 50 · tribute 300 · upkeep 564 · blockade 164 · admiralty 90
- DISPATCH: Supply cost you 6,056 men, at Lorraine.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal
  - LOG ai_proposal_rejected: We rejected Switzerland's armistice proposal
  - LOG third_party_peace: THE CONGRESS: Spain and Switzerland make peace without France
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. Brutal stalemate between ArchdukeCharles and Soult. Heavy casualties on both s… · Mack attacks with overwhelming force. Soult holds the line. Casualties: Mack 9,794, Soult's army 997. Both armies remai…
  - ⚔ Archduke Charles (lost 4036) vs Soult (lost 1741, own corps) — Stalemate. Soult and Archduke Charles glare at each other across the field.
  - ⚔ Mack (lost 9794) vs Soult (lost 599, own corps) — A decisive victory for Soult! Mack was thoroughly outmatched.
  - verbs: attack×2
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 700, own corps) vs Wellesley (lost 1037, own corps) — Davout, Lannes and Napoleon arrived to reinforce Ney, but Soult and Murat failed to reach the field in time.
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 95 · net +22 · threat 14 · provinces 5 (+0) · ceiling 2107 · army 106676 · vassals Holland 100
  - NET income 606 · trade 262 · admin 50 · tribute 300 · upkeep 952 · requisitions 10 · blockade 164 · admiralty 90
- DISPATCH: Sire — Marshal Paget of Britain is taken at Nivernais — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 30 — Early December 1806
  - MAILBOX #34 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #35 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 4 actions, 1 attacks — Austria, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Buxhowden marches from Swabia into Rhineland unopposed! (762 lost to march) Captured: France → Russia
  - 🏴 Russia: Buxhowden marches from Swabia into Rhineland unopposed! (762 lost to march) Captured: France → Russia
  - verbs: move×1, stance_change×1, recruit×1, attack×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 58, own corps) vs Wellesley (lost 1747) — Davout, Lannes and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Wellesley was taken …
- ENVOYS WAITING 1 · Prussia open borders
- LEDGER treasury 40 · net -46 · threat 16 · provinces 5 (+0) · army 102599 · vassals Holland 100
  - NET income 508 · trade 262 · admin 50 · tribute 300 · upkeep 912 · blockade 164 · admiralty 90
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 31 — Late December 1806
  - MAILBOX #35 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #36 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Ney · BOMBARDMENT: Shrapnel → Davout
  - verbs: attack×2, recruit×2, wait×1
- ENVOYS WAITING 2 · Austria armistice losing · Switzerland settlement offer
- LEDGER treasury 62 · net +22 · threat 15 · provinces 5 (+0) · ceiling 2093 · army 96667 · vassals Holland 100
  - NET income 512 · trade 262 · admin 50 · tribute 300 · upkeep 848 · blockade 164 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes and Napoleon stand 54,403 men at Burgundy, which feeds 22,500. 31,903 too many. 6,753 men lost in 2 turns. No depot may be laid at Burgundy — rural regions don't support bu…
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain, Russia and Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 32 — Early January 1807
  - MAILBOX #36 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #37 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #37 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #38 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Austria, armistice_losing #37 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #38 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn's forces advance steadily. Soult holds the line. Casualties: ArchdukeJohn's army 6,378, Soult's army 1,788… · Mack delivers an effective strike. Soult holds the line. Casualties: Mack 7,454, Soult's army 1,420. Both armies remain…
  - ⚔ Archduke John (lost 1596, own corps) vs Soult (lost 1074, own corps) — A decisive victory for Soult! Archduke John was thoroughly outmatched.
  - ⚔ Mack (lost 7454) vs Soult (lost 853, own corps) — Complete dominance on the field. Mack crumbled before Soult.
  - verbs: attack×2, form_square×1
  - POPUP marshal_audience: shadow_command, Marshal Lannes asks for a command → detach
  -     ↳ Lannes straightens. "You will not regret it, Sire." March him to Burgundy and the front is his — the order is…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #39 → reject_settlement_offer
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 11 · net +109 · threat 16 · provinces 5 (+0) · ceiling 2523 · army 90671 · vassals Holland 100
  - NET income 527 · trade 262 · admin 50 · tribute 300 · upkeep 776 · blockade 164 · admiralty 90
- DISPATCH: Sire — Marshal Soult holds the field at Lorraine — Mack's corps is driven from Lorraine yet again — broken, and fleeing.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Britain: Moore moves from Nivernais to Franche-Comte. Franche-Comte falls to Britain!
  - verbs: move×1
  - POPUP marshal_audience: shadow_command, Marshal Davout asks for a command → detach
  -     ↳ Davout straightens. "You will not regret it, Sire." March him to Burgundy and the front is his — the order is…
- LEDGER treasury 67 · net +56 · threat 17 · provinces 4 (-1) · ceiling 2268 · army 88123 · vassals Holland 100
  - NET income 458 · trade 262 · admin 50 · tribute 300 · upkeep 760 · blockade 164 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. Moore's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any ga…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Russia (defensive alliance)

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Ney · BOMBARDMENT: Shrapnel → Davout
  - verbs: attack×2
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 176 · net +109 · threat 16 · provinces 4 (+0) · ceiling 2521 · army 83781 · vassals Holland 100
  - NET income 461 · trade 212 · admin 50 · tribute 300 · upkeep 692 · blockade 132 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes and Napoleon have been 4 turns over what Burgundy can feed. 7,502 men. The country will ask where the army went. No depot may be laid at Burgundy — rural regions don't supp…
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
  - MAILBOX #39 Denmark incoming_proposal: Denmark — Non-Aggression Pact → activated
  - POPUP diplomatic_dialogue: Denmark, non_aggression #40 → reject
  - POPUP proposal_result: You have rejected Denmark's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Ney · BOMBARDMENT: Shrapnel → Davout
  - verbs: attack×2
- ENVOYS WAITING 2 · Hesse non aggression · Switzerland armistice losing
- LEDGER treasury 337 · net +161 · threat 15 · provinces 4 (+0) · ceiling 2766 · army 79878 · vassals Holland 100
  - NET income 473 · trade 212 · admin 50 · tribute 300 · upkeep 652 · blockade 132 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes and Napoleon have been 5 turns over what Burgundy can feed. 6,566 men. The country will ask where the army went. No depot may be laid at Burgundy — rural regions don't supp…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Denmark's non-aggression pact proposal
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)

## Turn 36 — Early March 1807
  - MAILBOX #40 Hesse incoming_proposal: Hesse — Non-Aggression Pact → activated
  - MAILBOX #41 Switzerland incoming_proposal: Switzerland — Armistice → activated
  - POPUP diplomatic_dialogue: Hesse, non_aggression #41 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #42 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Switzerland's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Hesse, non_aggression #41 → reject
  - POPUP proposal_result: You have rejected Hesse's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: Switzerland, armistice_losing #42 → reject
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 3 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Ney · BOMBARDMENT: Shrapnel → Davout · Mack faces a difficult fight. Ney holds the line. Casualties: Mack 7,642, Ney's army 1,192. Both armies remain in the f…
  - ⚔ Mack (lost 7642) vs Ney (lost 324, own corps) — Complete dominance on the field. Mack crumbled before Ney.
  - verbs: attack×3
- ENVOYS WAITING 2 · Russia armistice losing · Switzerland settlement offer
- LEDGER treasury 494 · net +216 · threat 12 · provinces 4 (+0) · ceiling 3127 · army 75620 · vassals Holland 100
  - NET income 472 · trade 212 · admin 50 · tribute 300 · upkeep 596 · blockade 132 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Burgundy — Mack's corps breaks a second time on this ground and flees.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Switzerland has offered terms to settle Switzerland vs France.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Switzerland's armistice proposal
  - LOG ai_proposal_rejected: We rejected Hesse's non-aggression pact proposal

## Turn 37 — Late March 1807
  - MAILBOX #42 Russia incoming_proposal: Russia — Armistice → activated
  - MAILBOX #43 Switzerland incoming_settlement_offer: Switzerland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #43 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #44 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Russia, armistice_losing #43 → reject
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #44 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Moore assaults the Amsterdam garrison! Garrison: 10,000 -> 5,000 (-5,000). Moore loses 2,777 troops. Garrison holds — 5… · Moore assaults the Amsterdam garrison! Garrison collapses (5,000 -> 0). Moore loses 1,543 troops in the assault. Moore …
  - 🏴 Britain: [Materiel] Guns, horses and stores lost with the fallen: Britain -77g, Holland -125g. Captured: Holland → Britain
  - verbs: move×3, attack×2
- ENVOYS WAITING 2 · Prussia open borders · Britain settlement offer
- LEDGER treasury 500 · net +6 · threat 11 · provinces 4 (+0) · ceiling 2031 · army 74183 · vassals Holland 100
  - NET income 475 · trade 212 · admin 50 · tribute 75 · upkeep 584 · blockade 132 · admiralty 90
- DISPATCH: Sire — Amsterdam has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 197 gold.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain and Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 38 — Early April 1807
  - MAILBOX #44 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - MAILBOX #45 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #45 → reject
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #46 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Prussia, open_borders #45 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #46 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 487 · net -13 · threat 10 · provinces 4 (+0) · army 72834 · vassals Holland 100
  - NET income 478 · trade 212 · admin 50 · tribute 37 · upkeep 568 · blockade 132 · admiralty 90
- DISPATCH: Sire — Gelderland has been taken by Britain.
  - RAIL balance_of_europe_shifted: British Interest leads the current largest alignment at 60% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Britain, Russia and Austria (defensive alliance)
  - LOG ai_proposal_rejected: We rejected Prussia's open borders agreement proposal

## Turn 39 — Late April 1807
  - MAILBOX #46 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #47 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 3 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Ney · BOMBARDMENT: Shrapnel → Davout · Mack's attack meets fierce resistance. Ney holds the line. Casualties: Mack 5,003, Ney's army 1,439. Both armies remain…
  - ⚔ Mack (lost 5003) vs Ney (lost 378, own corps) — An exemplary engagement by Ney. The outcome was never in doubt.
  - verbs: attack×3
- LEDGER treasury 450 · net +34 · threat 11 · provinces 4 (+0) · ceiling 2176 · army 68785 · vassals Holland 100
  - NET income 477 · trade 212 · admin 50 · tribute 37 · upkeep 520 · blockade 132 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Burgundy — Mack's corps is driven from Burgundy yet again — broken, and fleeing.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG balance_of_europe_shifted: British Interest leads the current largest alignment at 60% of active European bloc power.
  - LOG ai_proposal_rejected: We rejected Austria's armistice proposal

## Turn 40 — Early May 1807
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 2 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — BOMBARDMENT: Shrapnel → Ney · BOMBARDMENT: Shrapnel → Davout
  - verbs: attack×2
- LEDGER treasury 503 · net +53 · threat 12 · provinces 4 (+0) · ceiling 2274 · army 66530 · vassals Holland 100
  - NET income 480 · trade 212 · admin 50 · tribute 37 · upkeep 504 · blockade 132 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes and Napoleon have been 10 turns over what Burgundy can feed. 3,407 men. The country will ask where the army went. No depot may be laid at Burgundy — rural regions don't sup…
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 40 · popups 95 · battles 25
