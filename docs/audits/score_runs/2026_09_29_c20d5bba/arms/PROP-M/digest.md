# Playtest digest — PROP-M

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "propose", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.11.15 · Linux-6.18.44-fc-v37-x86_64-with-glibc2.39 (x86_64) · PYTHONHASHSEED `0` · engine `c20d5bba3ca1` (dirty) · content `8f597da58501` · driver `4489dcc909f5`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Austria while allied with Bavaria (who is…)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl…
  - ⚔ Archduke Charles (lost 1908) vs Bernadotte (lost 6267) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1685 · net +1198 · threat 64 · provinces 28 · ceiling 29227 · army 182623 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 2420 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 6,267 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #5 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's attack falters disastrously! ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archduk… · Mack delivers an effective strike. Bernadotte holds the line. Casualties: Mack 6,936, Bernadotte's army 4,558. Both arm…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 709) vs Bernadotte (lost 5581) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Mack (lost 6936) vs Bernadotte (lost 350, own corps) — Lannes and Massena's timely arrival bolstered Bernadotte's position. Well-coordinated, Sire.
  - verbs: attack×2, move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2843 · net +1559 · threat 62 · provinces 28 (+0) · ceiling 31485 · army 170672 · vassals Holland 97 · Kingdom of Italy 99 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 937 · upkeep 2052 · charges 45 · blockade 281 · admiralty 90
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
  - 🏴 Austria: Casualties: ArchdukeCharles 689, Bernadotte's army 5,674. Both armies remain in the field. Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 1905) vs Lannes (lost 5992) — Lannes stood alone, Sire. Murat never came.
  - ⚔ Archduke Charles (lost 689) vs Bernadotte (lost 1731, own corps) — The hills were ours, but Archduke Charles took them. Bernadotte's position was overrun.
  - verbs: attack×2, retreat×1, stance_change×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1003, own corps) vs Mack (lost 18870) — Reinforcements from Ney, Davout, Massena and Napoleon bolstered Murat's position — though Soult and Lannes never arrive…
  - POPUP proposal_result: Russia has rejected our Peace Treaty. → display-only
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4424 · net +2187 · threat 68 · provinces 28 (+0) · ceiling 35305 · army 146435 · vassals Holland 94 · Kingdom of Italy 96 · Switzerland 88
  - NET income 2590 · trade 449 · admin 50 · tribute 919 · upkeep 1316 · charges 171 · requisitions 37 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 8
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 13 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #11 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's attack meets fierce resistance. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Arch…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Franche-Comte!
  - ⚔ Archduke Charles (lost 2158) vs Bernadotte (lost 405, own corps) — Massena arrived to reinforce Bernadotte, but Ney and Soult failed to reach the field in time. And Bernadotte was taken …
  - verbs: attack×1, retreat×1
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
- LEDGER treasury 6386 · net +1950 · threat 56 · provinces 28 (+0) · ceiling 31124 · army 132553 · vassals Holland 92 · Switzerland 84
  - NET income 2583 · trade 536 · admin 50 · tribute 562 · upkeep 1048 · charges 345 · requisitions 37 · blockade 335 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Spain rebuffs 4 courts (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 5 — Late November 1805
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #12 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 actions unused) Turn 6 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Piedmont into Provence unopposed! (143 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Piedmont into Provence unopposed! (143 lost to march) Captured: France → Austria
  - verbs: move×1, attack×1, stance_change×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 8244 · net +1691 · threat 54 · provinces 27 (-1) · ceiling 28865 · army 126781 · vassals Holland 92 · Switzerland 82
  - NET income 2435 · trade 536 · admin 50 · tribute 562 · upkeep 992 · charges 512 · requisitions 37 · blockade 335 · admiralty 90
- DISPATCH: Sire — Provence has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `propose peace with Russia` → ✗ Talleyrand advises patience, Sire. Russia refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Provence into Lyonnais unopposed! (141 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Provence into Lyonnais unopposed! (141 lost to march) Captured: France → Austria
  - verbs: form_square×1, attack×1
  - POPUP marshal_audience: shadow_command, Marshal Ney asks for a command → detach
  -     ↳ Ney straightens. "You will not regret it, Sire." March him to Rhineland and the front is his — the order is y…
- LEDGER treasury 9671 · net +1286 · threat 51 · provinces 26 (-1) · ceiling 24758 · army 121452 · vassals Holland 92 · Switzerland 91
  - NET income 2356 · trade 536 · admin 50 · tribute 337 · upkeep 952 · charges 653 · requisitions 37 · blockade 335 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 4
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: The court of Prussia eases over The Hanoverian Prize — gold is now the length of its tether.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 36% of active European bloc power.
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 7 — Late December 1805
- CMD `propose peace with Austria` → ✗ Talleyrand advises patience, Sire. Austria refused us; the court will not receive another envoy for 1 more turn.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Lyonnais into Limousin unopposed! (140 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn marches from Lyonnais into Limousin unopposed! (140 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeJohn moves from Limousin to Burgundy. Burgundy falls to Austria!
  - verbs: attack×1, move×1
  - POPUP marshal_audience: shadow_command, Marshal Davout asks for a command → detach
  -     ↳ Davout straightens. "You will not regret it, Sire." March him to Rhineland and the front is his — the order i…
- LEDGER treasury 10619 · net +811 · threat 48 · provinces 24 (-2) · ceiling 17464 · army 116607 · vassals Holland 92 · Switzerland 90
  - NET income 2208 · trade 536 · admin 50 · tribute 337 · upkeep 912 · charges 1020 · requisitions 37 · blockade 335 · admiralty 90
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 8 — Early January 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #14 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 7 actions, 2 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Burgundy into Savoy unopposed! (274 lost to march) Captured: France → Austria · Castanos engages in solid combat. Castanos gains the advantage over Paget. Casualties: Castanos 728, Paget 1,533. Both …
  - 🏴 Austria: ArchdukeJohn marches from Burgundy into Savoy unopposed! (274 lost to march) Captured: France → Austria
  - ⚔ Castanos (lost 728) vs Paget (lost 1533) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: move×4, attack×2, unfortify×1
- LEDGER treasury 10983 · net +282 · threat 45 · provinces 23 (-1) · ceiling 12837 · army 112185 · vassals Holland 92 · Switzerland 89
  - NET income 2118 · trade 536 · admin 50 · tribute 337 · upkeep 872 · charges 1361 · contributions 138 · requisitions 37 · blockade 335 · admiralty 90
- DISPATCH: Sire — Savoy has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forces …
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `propose peace with Russia` → ✓ Sire, regarding the Peace Treaty proposal to Russia, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #15 → confirm
  - POPUP proposal_result: Talleyrand departs for the Russia court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP proposal_result: Russia has accepted our Peace Treaty! → display-only
  - RATIFIED Russia · PEACE · stalemate
- LEDGER treasury 11934 · net +832 · threat 37 · provinces 22 (-1) · ceiling 20702 · army 108133 · vassals Holland 92 · Switzerland 88
  - NET income 2081 · trade 548 · admin 50 · tribute 337 · upkeep 848 · charges 941 · requisitions 37 · blockade 342 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Napoleon have been 6 turns over what Swabia can feed. 13,319 men. The country will ask where the army went. No depot may be laid at Swabia — not controlled by F…
  - RAIL peace_ratified: Peace ratified between France and Russia.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Russia with a response.
  - TURN EVENTS 1
- DIPLO +7 medium/low (diplomatic_proposal_sent, law_enacted_abroad ×3, diplomatic_dp_regen, diplomatic_treaty_signed, paymaster_subsidy)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 10 — Early February 1806
- CMD `propose peace with Britain` → ✓ Sire, regarding the Peace Treaty proposal to Britain, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #16 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1
- LEDGER treasury 12809 · net +757 · threat 34 · provinces 22 (+0) · ceiling 20530 · army 104406 · vassals Holland 92 · Switzerland 87
  - NET income 2084 · trade 548 · admin 50 · tribute 337 · upkeep 808 · charges 1059 · requisitions 37 · blockade 342 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Napoleon have been 7 turns over what Swabia can feed. 12,201 men. The country will ask where the army went. No depot may be laid at Swabia — not controlled by F…
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 11 — Late February 1806
- CMD `propose peace with Austria` → ✓ Sire, regarding the Peace Treaty proposal to Austria, I have prepared terms appropriate to the current military situation.
  - POPUP diplomatic_dialogue: proposal_confirm #17 → confirm
  - POPUP proposal_result: Talleyrand departs for the Austria court with your Peace Treaty proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×1
  - POPUP proposal_result: Austria has rejected our Peace Treaty. → display-only
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13593 · net +670 · threat 31 · provinces 22 (+0) · ceiling 20211 · army 100968 · vassals Holland 92 · Switzerland 86
  - NET income 2087 · trade 548 · admin 50 · tribute 337 · upkeep 784 · charges 1173 · requisitions 37 · blockade 342 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Murat, Massena and Napoleon have been 8 turns over what Swabia can feed. 11,217 men. The country will ask where the army went. No depot may be laid at Swabia — not controlled by F…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Austria with a response.
  - TURN EVENTS 1
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as alliance.
- DIPLO +4 medium/low (diplomatic_proposal_sent, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 12 — Early March 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #19 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain (4 pairs resolved). Status quo: Burgundy, Limousin, Lyonnais, Provence and Savoy stay Austrian by the treaty. → display-only
- CMD `propose peace with Britain` → ✗ We already have Peace with Britain. Talleyrand sees no purpose in proposing what we already possess.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 actions unused) Turn 13 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [completed]: Davout arrives at Franche-Comte. Davout: "It is done. I took the liberty of posting pickets."
- ORDER Massena [completed]: Massena arrives at Franche-Comte. Massena: "Done — and I trust the next order has more fire in it."
- ORDER Murat [completed]: Murat arrives at Franche-Comte. Murat: "It is done. Point me at something that shoots back, Sire."
- ORDER Napoleon [completed]: Napoleon arrives at Franche-Comte.
- ORDER Ney [completed]: Ney arrives at Franche-Comte. Ney: "Accomplished. The men want a battle, not another road."
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 15719 · net +2101 · threat 12 · provinces 22 (+0) · ceiling 190750 · army 102048 · vassals Holland 90 · Switzerland 85
  - NET income 2090 · trade 572 · admin 50 · tribute 337 · upkeep 784 · charges 164
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Spain + Holland vs Britain + Austria: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 2
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, law_enacted_abroad ×2, diplomatic_dp_regen, blockade_broken ×3)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 31 to 15.

## Turn 13 — Late March 1806
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (90 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17491 · net +1976 · threat 9 · provinces 22 (+0) · ceiling 182083 · army 98419 · vassals Holland 99 · Switzerland 84
  - NET income 2090 · trade 572 · admin 50 · tribute 225 · upkeep 776 · charges 185
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Napoleon stand 63,419 men at Franche-Comte, which feeds 52,500. 10,919 too many. 7,549 men lost in 2 turns. No depot may be laid at Franche-Comte — town…
  - TURN EVENTS 1
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 14 — Early April 1806
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 19507 · net +1991 · threat 6 · provinces 22 (+0) · ceiling 185416 · army 95053 · vassals Holland 98 · Switzerland 83
  - NET income 2090 · trade 572 · admin 50 · tribute 225 · upkeep 736 · charges 210
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Napoleon stand 60,053 men at Franche-Comte, which feeds 52,500. 7,553 too many. 10,915 men lost in 3 turns. No depot may be laid at Franche-Comte — town…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 15 — Late April 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21305 · net +1777 · threat 3 · provinces 22 (+0) · ceiling 169333 · army 91923 · vassals Holland 97 · Switzerland 93
  - NET income 2090 · trade 572 · admin 50 · upkeep 704 · charges 231
- DISPATCH: Sire — the levy has stood open 4 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 1
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 46% of active European bloc power.

## Turn 16 — Early May 1806
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23098 · net +1771 · threat 0 · provinces 22 (+0) · ceiling 170666 · army 89007 · vassals Holland 96 · Switzerland 93
  - NET income 2090 · trade 572 · admin 50 · upkeep 688 · charges 253
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Massena and Napoleon have been 4 turns over what Franche-Comte can feed. 9,412 men. The country will ask where the army went. No depot may be laid at Franche-Comte …
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24893 · net +1774 · threat 0 · provinces 22 (+0) · ceiling 172666 · army 86287 · vassals Holland 95 · Switzerland 93
  - NET income 2090 · trade 572 · admin 50 · upkeep 664 · charges 274
- DISPATCH: Sire — the levy has stood open 6 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 26683 · net +1768 · threat 0 · provinces 22 (+0) · ceiling 174000 · army 83725 · vassals Holland 94 · Switzerland 93
  - NET income 2090 · trade 572 · admin 50 · upkeep 648 · charges 296
- DISPATCH: Sire — the levy has stood open 7 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 1
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 28475 · net +1771 · threat 0 · provinces 22 (+0) · ceiling 176000 · army 81293 · vassals Holland 93 · Switzerland 93
  - NET income 2090 · trade 572 · admin 50 · upkeep 624 · charges 317
- DISPATCH: Sire — the levy has stood open 8 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 30262 · net +2102 · threat 0 · provinces 22 (+0) · ceiling 205416 · army 78981 · vassals Holland 92 · Switzerland 93
  - NET income 2090 · trade 572 · admin 50 · tribute 337 · upkeep 608 · charges 339
- DISPATCH: Sire — the levy has stood open 9 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 32 · popups 38 · battles 8
