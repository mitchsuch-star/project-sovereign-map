# Playtest digest — PROP-A

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.11.15 · Linux-6.18.44-fc-v37-x86_64-with-glibc2.39 (x86_64) · PYTHONHASHSEED `0` · engine `c20d5bba3ca1` (dirty) · content `8f597da58501` · driver `4489dcc909f5`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl…
  - ⚔ Archduke Charles (lost 1753) vs Bernadotte (lost 6658) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1666 · net +1198 · threat 67 · provinces 28 · ceiling 29227 · army 182236 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2420 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 6,658 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #5 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCha… · Mack delivers an effective strike. Bernadotte holds the line. Casualties: Mack 7,681, Bernadotte's army 4,171. Both arm…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 551) vs Bernadotte (lost 5660) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Mack (lost 7681) vs Bernadotte (lost 292, own corps) — Lannes and Massena's timely arrival bolstered Bernadotte's position. Well-coordinated, Sire.
  - verbs: attack×2, move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2831 · net +1551 · threat 65 · provinces 28 (+0) · ceiling 31338 · army 170603 · vassals Holland 97 · Kingdom of Italy 99 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 937 · upkeep 2060 · charges 45 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 22 approaches from Bavaria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #8 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeCharl… · ArchdukeCharles holds them at Munich while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: Casualties: ArchdukeCharles 735, Bernadotte's army 5,981. Both armies remain in the field. Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 2104) vs Lannes (lost 5368) — Lannes stood alone, Sire. Murat never came.
  - ⚔ Archduke Charles (lost 735) vs Bernadotte (lost 1630, own corps) — The hills were ours, but Archduke Charles took them. Bernadotte's position was overrun. And Bernadotte was taken on tha…
  - verbs: attack×2, retreat×1, stance_change×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1004, own corps) vs Mack (lost 16385) — Reinforcements from Ney, Davout, Massena and Napoleon bolstered Murat's position — though Soult and Lannes never arrive…
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4486 · net +2242 · threat 71 · provinces 28 (+0) · ceiling 36152 · army 144172 · vassals Holland 94 · Kingdom of Italy 96 · Switzerland 88
  - NET income 2590 · trade 449 · admin 50 · tribute 919 · upkeep 1256 · charges 176 · requisitions 37 · blockade 281 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 9
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #11 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Lannes. Casualties: ArchdukeCharles 1…
  - ⚔ Archduke Charles (lost 168) vs Lannes (lost 4419) — Where were Soult and Murat? Lannes held the field alone — reinforcement never came.
  - verbs: attack×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franche-Comte with 2,209 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 312, own corps) vs Mack (lost 25228) — Reinforcements from Davout, Massena and Napoleon bolstered Ney's position — though Murat never arrived, Sire. And Mack …
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franche-Comte with 2,209 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP capture_choice[capture]: Franconia, Ney → secure
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
  -     ↳ audience: No marshal waits upon you, Sire.
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
- LEDGER treasury 6222 · net +1663 · threat 69 · provinces 29 (+1) · ceiling 21503 · army 132838 · vassals Holland 93 · Switzerland 85
  - NET income 2583 · trade 536 · admin 50 · tribute 562 · upkeep 1048 · charges 459 · contributions 73 · requisitions 37 · occupation 100 · blockade 335 · admiralty 90
- DISPATCH: Sire — Marshal Mack of Austria is taken at Franconia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 9
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 approaches from Prussia and Sardinia are rebuffed (defensive alliance)

## Turn 5 — Late November 1805
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #13 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franche-Comte where he stands! (1,183 lost to march) Captured: France → Austria · ArchdukeJohn marches from Piedmont into Provence unopposed! (143 lost to march) Captured: France → Austria · ArchdukeCharles marches from Franche-Comte into Nivernais unopposed! (1,147 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles takes Franche-Comte where he stands! (1,183 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (143 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Franche-Comte into Nivernais unopposed! (1,147 lost to march) Captured: France → Austria
  - verbs: attack×3
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7763 · net +1355 · threat 66 · provinces 26 (-3) · ceiling 19857 · army 129854 · vassals Holland 93 · Switzerland 83
  - NET income 2350 · trade 536 · admin 50 · tribute 562 · upkeep 1040 · charges 645 · requisitions 37 · occupation 70 · blockade 335 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. Archduke Charles's corps of 40,139 stands there. A garrison you detach (3,000 men) holds a province against a march, as d…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #14 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Russia` → ✗ Talleyrand advises patience, Sire. Russia refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Nivernais into Orleanais unopposed! (1,102 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Flanders garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 2,857 troops.… · ArchdukeJohn marches from Provence into Lyonnais unopposed! (141 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Flanders garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,666 troops in …
  - 🏴 Austria: ArchdukeCharles marches from Nivernais into Orleanais unopposed! (1,102 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Lyonnais unopposed! (141 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -83g, France -150g. Captured: France → Austria
  - verbs: attack×4
  - POPUP marshal_audience: shadow_command, Marshal Davout asks for a command → detach
  -     ↳ Davout straightens. "You will not regret it, Sire." March him to Franconia and the front is his — the order i…
- LEDGER treasury 8165 · net +731 · threat 63 · provinces 23 (-3) · ceiling 14194 · army 127036 · vassals Holland 93 · Switzerland 92
  - NET income 2041 · trade 536 · admin 50 · tribute 337 · upkeep 1028 · charges 747 · requisitions 37 · occupation 70 · blockade 335 · admiralty 90
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there for…
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✗ Talleyrand advises patience, Sire. Austria refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Flanders into Picardy unopposed! (906 lost to march) Captured: France → Austria · ArchdukeJohn marches from Lyonnais into Limousin unopposed! (140 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Flanders into Picardy unopposed! (906 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Limousin unopposed! (140 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn moves from Limousin to Burgundy. Burgundy falls to Austria!
  - verbs: attack×2, move×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Davout and Murat: Murat turns openly discontent (trust -3; expect defiance).
- LEDGER treasury 8797 · net +534 · threat 60 · provinces 20 (-3) · ceiling 13085 · army 124372 · vassals Holland 93 · Switzerland 91
  - NET income 1916 · trade 536 · admin 50 · tribute 337 · upkeep 1032 · charges 845 · requisitions 37 · occupation 40 · blockade 335 · admiralty 90
- DISPATCH: Sire — Picardy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - TURN EVENTS 4
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Prussia (defensive alliance)

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #15 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 9 actions, 4 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Picardy into Artois unopposed! (825 lost to march) Captured: France → Austria · ArchdukeJohn marches from Burgundy into Savoy unopposed! (274 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Normandy garrison! Garrison: 12,000 -> 6,000 (-6,000). ArchdukeCharles loses 3,333 troops.… · Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 686, Paget 1,627. Bot…
  - 🏴 Austria: ArchdukeCharles marches from Picardy into Artois unopposed! (825 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Burgundy into Savoy unopposed! (274 lost to march) Captured: France → Austria
  - ⚔ Castanos (lost 686) vs Paget (lost 1627) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: move×4, attack×4, unfortify×1
- LEDGER treasury 8714 · net +168 · threat 57 · provinces 18 (-2) · ceiling 9996 · army 121850 · vassals Holland 93 · Switzerland 90
  - NET income 1713 · trade 536 · admin 50 · tribute 337 · upkeep 1024 · charges 878 · contributions 138 · requisitions 37 · occupation 40 · blockade 335 · admiralty 90
- DISPATCH: Sire — Artois has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 8 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Normandy garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 1,666 troops in … · ArchdukeCharles marches from Normandy into Berry unopposed! (364 lost to march) Captured: France → Austria · ArchdukeCharles marches from Berry into Guyenne unopposed! (342 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -83g, France -150g. Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Normandy into Berry unopposed! (364 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Berry into Guyenne unopposed! (342 lost to march) Captured: France → Austria
  - verbs: attack×3
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
  - RATIFIED Russia · PEACE · white_peace
- LEDGER treasury 8796 · net +187 · threat 54 · provinces 15 (-3) · ceiling 10539 · army 119458 · vassals Holland 93 · Switzerland 89
  - NET income 1432 · trade 548 · admin 50 · tribute 337 · upkeep 1020 · charges 725 · requisitions 37 · occupation 40 · blockade 342 · admiralty 90
- DISPATCH: Sire — Normandy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL peace_ratified: Peace ratified between France and Russia.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_proposal_sent, law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_treaty_signed, paymaster_subsidy)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: 10 courts rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain and Russia rebuff Prussia (open borders agreement)

## Turn 10 — Early February 1806
- CMD `request terms from Britain` → ✓ I shall ask Britain's chancery to name its terms for France + Spain + Holland vs Britain + Austria, Sire. Expect an answer with the next dispatches.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Guyenne into Gascony unopposed! (644 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Guyenne into Gascony unopposed! (644 lost to march) Captured: France → Austria
  - verbs: attack×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 8951 · net +116 · threat 51 · provinces 14 (-1) · ceiling 10000 · army 117187 · vassals Holland 93 · Switzerland 88
  - NET income 1360 · trade 548 · admin 50 · tribute 337 · upkeep 1000 · charges 764 · requisitions 37 · occupation 20 · blockade 342 · admiralty 90
- DISPATCH: Sire — Gascony has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 1
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 approaches from Prussia and Sardinia are rebuffed (defensive alliance)

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (4 pairs resolved). Status quo: Franconia stays ours by the treaty — titled. Status quo: Artois, Berry, Burgundy, Flanders, Franche-Comte, Gascony, Guyenne, Limousin, Lyonnais, Nivernais, Normandy, Orleanais, Picardy, Provence and Savoy stay Austrian by the treaty. → display-only
- CMD `propose peace with Austria` → ✗ We already have Peace with Austria. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- ORDER Davout [continues]: Davout marches to Swabia. 3 regions to Ardennes.
- ORDER Massena [continues]: Massena marches to Swabia. 3 regions to Ardennes.
- ORDER Murat [continues]: Murat marches to Orleanais. 1 region to Ardennes.
- ORDER Napoleon [continues]: Napoleon marches to Swabia. 3 regions to Ardennes.
- ORDER Ney [continues]: Ney marches to Swabia. 3 regions to Ardennes.
- ORDER Soult [continues]: Soult marches to Orleanais. 1 region to Ardennes.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: Murat turns openly discontent (trust -3; expect defiance).
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 10127 · net +825 · threat 22 · provinces 14 (+0) · ceiling 78833 · army 120738 · vassals Holland 100 · Switzerland 87
  - NET income 1364 · trade 572 · admin 50 · upkeep 1044 · charges 97 · occupation 20
- DISPATCH: Sire — the war with Austria is over. 6 corps stand on the wrong side of the new frontier. Berthier has given them the road home — Ney to Ardennes, Davout to Ardennes, Soult to Ardennes, Murat to Arde…
  - RAIL settlement_summary: Settlement of France + Spain + Holland vs Britain + Austria: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — gold is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +8 medium/low (diplomatic_coalition_dissolved, status_quo_titled, law_enacted_abroad ×2, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Sweden (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 51 to 25.

## Turn 12 — Early March 1806
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [continues]: Davout marches to Lorraine. 2 regions to Ardennes.
- ORDER Massena [continues]: Massena marches to Lorraine. 2 regions to Ardennes.
- ORDER Murat [completed]: Murat arrives at Ardennes. Murat: "Accomplished. The men want a battle, not another road."
- ORDER Napoleon [continues]: Napoleon marches to Lorraine. 2 regions to Ardennes.
- ORDER Ney [continues]: Ney marches to Lorraine. 2 regions to Ardennes.
- ORDER Soult [completed]: "the road home — safe passage granted by the peace" — executed as written. Soult arrives at Ardennes. Awaiting your next word.
- LEDGER treasury 10992 · net +855 · threat 19 · provinces 14 (+0) · ceiling 82166 · army 117534 · vassals Holland 99 · Switzerland 86
  - NET income 1368 · trade 572 · admin 50 · upkeep 1008 · charges 107 · occupation 20
- DISPATCH: Supply cost you 3,204 men, at Lorraine and Ardennes.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 13 — Late March 1806
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, recruit×1
- ORDER Davout [continues]: Davout marches to Orleanais. 1 region to Ardennes.
- ORDER Massena [continues]: Massena marches to Orleanais. 1 region to Ardennes.
- ORDER Napoleon [continues]: Napoleon marches to Orleanais. 1 region to Ardennes.
- ORDER Ney [continues]: Ney marches to Orleanais. 1 region to Ardennes.
- LEDGER treasury 11923 · net +1144 · threat 16 · provinces 14 (+0) · ceiling 107250 · army 111901 · vassals Holland 98 · Switzerland 85
  - NET income 1372 · trade 572 · admin 50 · tribute 225 · upkeep 936 · charges 119 · occupation 20
- DISPATCH: Sire — Ney, Davout, Massena and Napoleon stand 57,545 men at Orleanais, which feeds 35,000. 22,545 too many. 5,349 men lost in 2 turns. No depot may be laid at Orleanais — not controlled by France. L…
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [completed]: Davout arrives at Ardennes. Davout: "It is done. I took the liberty of posting pickets."
- ORDER Massena [completed]: Massena arrives at Ardennes. Massena: "Done — and I trust the next order has more fire in it."
- ORDER Napoleon [completed]: Napoleon arrives at Ardennes.
- ORDER Ney [completed]: Ney arrives at Ardennes. Ney: "Accomplished. The men want a battle, not another road."
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 13143 · net +1206 · threat 13 · provinces 14 (+0) · ceiling 113583 · army 105790 · vassals Holland 97 · Switzerland 84
  - NET income 1376 · trade 572 · admin 50 · tribute 225 · upkeep 864 · charges 133 · occupation 20
- DISPATCH: Sire — Ney, Davout, Soult, Murat, Massena and Napoleon stand 95,790 men at Ardennes, which feeds 22,500. 73,290 too many. 8,484 men lost in 3 turns. No depot may be laid at Ardennes — rural regions d…
  - RAIL balance_of_europe_shifted: British Interest leads the current largest alignment at 54% of active European bloc power.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Britain (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 14196 · net +1040 · threat 10 · provinces 14 (+0) · ceiling 100833 · army 100047 · vassals Holland 96 · Switzerland 94
  - NET income 1380 · trade 572 · admin 50 · upkeep 796 · charges 146 · occupation 20
- DISPATCH: Sire — Ney, Davout, Soult, Murat, Massena and Napoleon stand 90,047 men at Ardennes, which feeds 22,500. 67,547 too many. 13,006 men lost in 3 turns. No depot may be laid at Ardennes — rural regions …
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG balance_of_europe_shifted: British Interest leads the current largest alignment at 54% of active European bloc power.

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15308 · net +1099 · threat 7 · provinces 14 (+0) · ceiling 106833 · army 94648 · vassals Holland 95 · Switzerland 94
  - NET income 1384 · trade 572 · admin 50 · upkeep 728 · charges 159 · occupation 20
- DISPATCH: Sire — 3 turns of famine at Ardennes now. 17,253 men gone, and not one of them to the enemy. No depot may be laid at Ardennes — rural regions don't support buildings (need city or larger). Ile-de-Fra…
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 16451 · net +1129 · threat 4 · provinces 14 (+0) · ceiling 110500 · army 89572 · vassals Holland 94 · Switzerland 94
  - NET income 1388 · trade 572 · admin 50 · upkeep 688 · charges 173 · occupation 20
- DISPATCH: Sire — Ney, Davout, Soult, Murat, Massena and Napoleon have been 4 turns over what Ardennes can feed. 16,218 men. The country will ask where the army went. No depot may be laid at Ardennes — rural re…
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Sardinia against Austria (400g/turn)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Britain (defensive alliance)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17616 · net +1151 · threat 1 · provinces 14 (+0) · ceiling 113500 · army 84800 · vassals Holland 93 · Switzerland 94
  - NET income 1392 · trade 572 · admin 50 · upkeep 656 · charges 187 · occupation 20
- DISPATCH: Sire — the establishment stands 10,200 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18803 · net +1510 · threat 0 · provinces 14 (+0) · ceiling 144583 · army 80314 · vassals Holland 92 · Switzerland 94
  - NET income 1396 · trade 572 · admin 50 · tribute 337 · upkeep 624 · charges 201 · occupation 20
- DISPATCH: Sire — Ney, Davout, Soult, Murat, Massena and Napoleon have been 6 turns over what Ardennes can feed. 14,334 men. The country will ask where the army went. No depot may be laid at Ardennes — rural re…
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Sweden against Austria (500g/turn)
  - LOG ai_ai_proposal_refused: Russia rebuffs Britain (defensive alliance)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 20349 · net +1527 · threat 0 · provinces 14 (+0) · ceiling 147583 · army 76099 · vassals Holland 91 · Switzerland 94
  - NET income 1400 · trade 572 · admin 50 · tribute 337 · upkeep 592 · charges 220 · occupation 20
- DISPATCH: Sire — Ney, Davout, Soult, Murat, Massena and Napoleon have been 7 turns over what Ardennes can feed. 13,473 men. The country will ask where the army went. No depot may be laid at Ardennes — rural re…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

---
finished: **completed** · commands 31 · popups 38 · battles 9
