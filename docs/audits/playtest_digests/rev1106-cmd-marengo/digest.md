# Playtest digest — rev1106-cmd-marengo

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 3234, own corps) vs Mack (lost 11259) — Reinforcements from Davout and Napoleon bolstered Ney's position — though Lannes, Murat and Bernadotte never arrived, S… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: Ney, Davout, Murat and Napoleon would answer the guns — Lannes 18,000, 101,140 wi…
  - POPUP strategic_interrupt: Lannes, contact_bad_odds, Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' Berthier adds: Ney, Davout, Murat and Napoleon would answer the guns — Lannes 18,000, 101,140 with the muster committed, against Mack (40,741 men) — weighed together, the balance of force looks favorable. → attack_anyway
  - ↳ Lannes attacks Mack and wins! Continuing his march. MUSTER — Lannes (18,000; expect about 101,140 with the corps likely to arrive, up to 105,990 if all march; certain 85,376, and a bad day (1 in 10) is no better) vs Mack (40,741 men) at Swa
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1521, own corps) vs Mack (lost 16422) — Murat and Bernadotte never reached the guns. The battle was decided without them, Sire. And Mack was taken on that fiel…
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 2945) vs Bernadotte (lost 3982, own corps) — Ney and Lannes marched to Bernadotte's guns as ordered. It was not enough. — The corps system brought Ney in.
  - verbs: move×1, attack×1
- ORDER Lannes [active]: Lannes is marching to Rhineland.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. Prussia paid 30 gold into the treasury. → display-only
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 702 · net +809 · threat 75 · provinces 28 · ceiling 7762 · army 168138 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2828 · blockade 250 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is taken at Swabia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 actions unused) Turn 3 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1912) vs Bernadotte (lost 4090, own corps) — Ney and Lannes reached Bernadotte in time, Sire — but even together, the field could not be held. — The corps system brought Ney in.
  - verbs: attack×1, move×1, wait×1
- ENVOYS WAITING 2 · Portugal open borders · Denmark non aggression
- LEDGER treasury 1662 · net +1260 · threat 73 · provinces 28 (+0) · ceiling 10377 · army 157523 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 425 · admin 50 · tribute 937 · upkeep 2386 · blockade 266 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 7
- COURTS: The court of Prussia eases over The Hanoverian Prize — joining the stronger side for pay is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, province_changed_hands, diplomatic_we_threshold, diplomatic_dp_regen)

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Non-Aggression Pact → accept
- CMD `Ney, attack Mack` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 2 turns remaining.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✗ Lannes is already in Swabia.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 727 gold (×3 at war) (×1.21 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- SPENT 727g on this turn's orders
- enemy phase: 4 actions, 0 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, fortify×1, naval_expedition×1, wait×1
- ENVOYS WAITING 2 · Saxony open borders · Hesse non aggression
- LEDGER treasury 2362 · net +1290 · threat 71 · provinces 28 (+0) · ceiling 10756 · army 157055 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2590 · trade 500 · admin 50 · tribute 937 · upkeep 2330 · charges 55 · blockade 312 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes, Bernadotte and Napoleon stand 60,055 men at Swabia, which feeds 60,000. 55 too many. 9,164 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - TURN EVENTS 6
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Saxony: Open Borders Agreement → accept
  - LETTER Hesse: Non-Aggression Pact → accept
- CMD `Ney, attack Mack` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Swabia. Defense bonus: +7% now, 12% at dawn (the m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Munich
  - 🏴 Austria: Archduke John attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - verbs: unfortify×1, attack×1, form_square×1, wait×1
- ENVOYS WAITING 1 · PapalStates open borders
- LEDGER treasury 3880 · net +1202 · threat 69 · provinces 28 (+0) · ceiling 11540 · army 153840 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 562 · admin 50 · tribute 937 · upkeep 2202 · charges 294 · blockade 351 · admiralty 90
- DISPATCH: Sire — Munich has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Bavaria and Austria have made their peace without France. Bavaria, beaten (-37), sues for peace and Austria takes it on the held line; …
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Munich. A new design hardens in their court.
  - TURN EVENTS 9
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG ai_ai_proposal_refused: Britain rebuffs Portugal (open borders agreement)

## Turn 5 — Late November 1805
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Archduke Charles` → ✓ Archduke Charles stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Ney, pursuit_ask, Archduke Charles stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (308 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Paget
  - ⚔ Castanos (lost 72) vs Paget (lost 833) — Even Paget's fortifications could not hold, Sire. Castanos overran the position. — The Line Holds +15% (Paget)
  - verbs: attack×1, fortify×1
- ORDER Ney [active]: Ney is pursuing Archduke Charles.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Lannes: They settle into cold war.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (88 → 98); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 4890 · net +491 · threat 67 · provinces 28 (+0) · ceiling 7956 · army 146738 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 587 · admin 50 · tribute 712 · upkeep 2528 · charges 462 · blockade 368 · admiralty 90
- DISPATCH: Sire — Davout, Soult, Lannes, Murat, Bernadotte and Napoleon stand 90,316 men at Swabia, which feeds 60,000. 30,316 too many. 12,342 men lost in 3 turns. Bavaria's magazines feed us as our own — the …
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +6 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG third_party_peace: THE CONGRESS: Bavaria and Austria make peace without France
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Munich — Austria is not forgiven
  - LOG moment: Russia decrees the Magazines for 8 turns (5 authority)
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Kutuzov is at Bohemia, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 2 other courts stirred, but their formations remain beyond our sight.
- ORDER Ney [continues]: Ney pursues Archduke Charles. 0 regions away.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 5626 · net +585 · threat 67 · provinces 29 (+1) · ceiling 8651 · army 141252 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2627 · trade 587 · admin 50 · tribute 712 · upkeep 2158 · charges 700 · occupation 75 · blockade 368 · admiralty 90
- DISPATCH: Sire — Davout, Soult, Lannes, Murat, Bernadotte and Napoleon stand 85,118 men at Swabia, which feeds 60,000. 25,118 too many. 14,072 men lost in 3 turns. Bavaria's magazines feed us as our own — the …
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, diplomatic_ai_ai_treaty)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG diplomatic_ai_ai_treaty: Saxony and Austria sign a Non-Aggression Pact

## Turn 7 — Late December 1805
  - MAILBOX #9 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #10 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +0 (100 → 100, already full); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 53g a turn — 37g of income forfeited, 75g of occupation relieved, 27g returned as tribute at today's 75% rate, the force limit falls 2,500 (+12g surcharge). → display-only
- CMD `Ney, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Ney can give chase.
- CMD `Davout, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Kutuzov.
- CMD `Murat, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Murat can give chase.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 actions unused) Turn 8 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Tyrol · Cuesta attacks Paget
  - 🏴 Austria: Archduke Charles attacks Tyrol — Tyrol CAPTURED! (was Kingdom of Italy) (secured)
  - ⚔ Archduke Charles (lost 3741, own corps) vs Ney (lost 1489, own corps) — Reinforcement from Massena and Teulie kept Ney standing, Sire — but neither side yielded the ground.
  - ⚔ Cuesta (lost 44) vs Paget (lost 765) — Paget's fortified position was overwhelmed. A costly investment lost, Sire. — The Line Holds +15% (Paget)
  - verbs: move×4, attack×2
- ENVOYS WAITING 2 · Austria armistice losing · The Secretariat moment letter
- LEDGER treasury 6354 · net +784 · threat 65 · provinces 28 (-1) · ceiling 10949 · army 132259 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 587 · admin 50 · tribute 712 · upkeep 1956 · charges 741 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +4 medium/low (enemy_marshal_commissioned, province_changed_hands, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor

## Turn 8 — Early January 1806
  - MAILBOX #10 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #11 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → accept_ai_proposal
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #12 → reject_ai_proposal
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
  - POPUP diplomatic_dialogue: moment_letter #12 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.) → trust
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Massena is already in Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: 5 actions, 1 attacks — Russia, Prussia, the Ottoman Empire and 6 other courts stirred as well, but their formations remain beyond our sight. — Cuesta attacks Paget
  - ⚔ Cuesta (lost 7) vs Paget (lost 163) — The walls were not enough. Cuesta broke through Paget's prepared defenses. — The Line Holds +15% (Paget)
  - verbs: fortify×2, stance_change×1, naval_expedition×1, attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 7219 · net +700 · threat 63 · provinces 28 (+0) · ceiling 11251 · army 127837 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2583 · trade 587 · admin 50 · tribute 712 · upkeep 1868 · charges 906 · blockade 368 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns. The ledger stands: the war score reads +5 for France (5 battles, 1 drawn, 2 decisives kept); th…
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - TURN EVENTS 10
- DIPLO +6 medium/low (diplomatic_treaty_signed, province_changed_hands, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Murat stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Andalusia
  - 🏴 Spain: Castanos attacks Andalusia — Region captured: Andalusia (was Britain) (secured)
  - verbs: attack×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 8021 · net +644 · threat 61 · provinces 28 (+0) · ceiling 11660 · army 123741 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2585 · trade 587 · admin 50 · tribute 712 · upkeep 1768 · charges 1064 · blockade 368 · admiralty 90
- DISPATCH: Sire — Davout, Lannes, Bernadotte and Napoleon have been 6 turns over what Swabia can feed. 27,376 men dead. The country will ask where the army went. Bavaria's magazines feed us as our own — the arm…
  - RAIL settlement_offer_arrival: Britain, for Britain and Russia, has offered terms to settle the War with the Third Coalition — Britain + Austria + Russia.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,188g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 5
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- DIPLO +6 medium/low (enemy_marshal_commissioned ×2, law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 10 — Early February 1806
  - MAILBOX #12 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with the Third Coalition — the table with Britain + Russia (4 pairs resolved). → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney begins marching to Franconia (distance: 2). Moved to Piedmont. Route: Piedmont -> Lyonnais -> Burgundy -> Orleanais -> Lorraine -> Swabia -> Franconia.
- CMD `Davout, fortify` → ✗ Davout is already fortified at Swabia (+12% defense).
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Franconia, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: nothing visible — Austria, Britain, Spain and 2 other courts stirred, but their formations remain beyond our sight.
- ORDER Ney [active]: Ney is marching to Franconia (7 turns remaining).
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 10104 · net +1763 · threat 32 · provinces 28 (+0) · ceiling 21576 · army 119690 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2586 · trade 587 · admin 50 · tribute 712 · upkeep 928 · charges 1244
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Sire, the white peace of the War with the Third Coalition — the table with Britain + Russia takes nothing and gives nothing. Spain is left out: -18 r…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 6
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_vassal_contingent, coercive_demand, blockade_broken ×3, agenda_shift)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 61 to 30.
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 11 — Late February 1806
  - MAILBOX #13 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke John` → ✗ Cannot attack Archduke John — armistice with Austria (2 turns remaining).
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (153 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: nothing visible — Austria, Britain, Spain and 2 other courts stirred, but their formations remain beyond our sight.
- ORDER Ney [continues]: Ney marches to Lyonnais. 5 regions to Franconia.
- LEDGER treasury 11548 · net +1222 · threat 34 · provinces 28 (+0) · ceiling 19500 · army 117434 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2588 · trade 587 · admin 50 · tribute 375 · upkeep 912 · charges 1466
- DISPATCH: Sire — Prussia would now join a league against us — relations −25. The price to keep her out: Talleyrand brings her to −10 in 2 turns (2 DP); buying off her design costs 1,296 gold (+5 relations; she…
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover — Prussia's relations with every court, France's included, fall 15.
  - TURN EVENTS 4
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as an ultimatum.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: And Saxony stirs at its own design.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Lyonnais. Troops will be locked in training next turn, bonus ready turn 14. Ney's march to Franconia is set aside.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the nex…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Lannes stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: nothing visible — Austria, Britain, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 11744 · net +131 · threat 36 · provinces 28 (+0) · ceiling 12466 · army 115415 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 91
  - NET income 2590 · trade 587 · admin 50 · tribute 375 · upkeep 1628 · charges 1753 · admiralty 90
- DISPATCH: Sire — the truce with Austria has collapsed — the war resumes where it stood, at its age, with its ledger.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - RAIL allegiance_settled: The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 6
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: And Russia stirs at its own design.
- DIPLO +4 medium/low (law_enacted_abroad, province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia and Hesse (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia and Hesse (design ask)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Berthier stays the order a moment, Sire: before Murat marches on Archduke John, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Archduke John, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Murat attacks Archduke John' to read the muster before you commit — it costs nothing.
MUSTER — Murat (15,218) vs Archduke John (small force) at Tyrol — the balance of force looks unfavorable.
  WILL NOT — Massena: is dug in and will not abandon his works
  Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 15,218 we muster) would cost ~114g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 36/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Murat (15,218) vs Archduke John (small force) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 6317) vs Archduke John (lost 690, own corps) — The enemy fortifications proved formidable, Sire. Murat's assault was repulsed.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Swabia to Franconia (121 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 10 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Davout
  - ⚔ Archduke Charles (lost 1566) vs Davout (lost 2085, own corps) — Davout fought without Napoleon's support. The roads, or the will, proved insufficient. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: unfortify×2, attack×1, form_square×1, recruit×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 11658 · net +483 · threat 38 · provinces 28 (+0) · ceiling 14180 · army 105339 · vassals Holland 93 · Kingdom of Italy 99 · Switzerland 86
  - NET income 2590 · trade 587 · admin 50 · tribute 600 · upkeep 1408 · charges 1846 · admiralty 90
- DISPATCH: Sire — Murat was mauled at Tyrol: a third of his corps — 6,317 men — lost in a single action.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG moment: The Arch-Chancellor's Letters — an affair of state is laid before the Emperor
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 14 — Early April 1806
  - MAILBOX #14 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #16 → reject_ai_proposal
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will move to Piedmont instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will move to Piedmont instead.) → trust
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 10 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Davout · Archduke John attacks Davout · Hiller attacks Davout
  - ⚔ Archduke Charles (lost 1613) vs Davout (lost 1533, own corps) — Napoleon reached Davout in time, Sire — but even together, the field could not be held.
  - ⚔ Archduke John (lost 1232) vs Davout (lost 681, own corps) — Stalemate. Davout and Archduke John glare at each other across the field. — The Hofkriegsrat's orders reached Archduke Charles too late.
  - ⚔ Hiller (lost 676) vs Davout (lost 632) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: attack×3
- ENVOYS WAITING 2 · Austria settlement offer · Switzerland client petition
- LEDGER treasury 12056 · net +446 · threat 40 · provinces 28 (+0) · ceiling 14317 · army 99404 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 83
  - NET income 2590 · trade 587 · admin 50 · tribute 600 · upkeep 1308 · charges 1983 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Austria has offered terms to settle the War with Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,670 gold. Prussia is now free to look elsewhere.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 3 more provinces. A new design hardens in their court.
  - TURN EVENTS 7
- COURTS: The court of Hesse eases over The Westphalian Duchy — gold is now the length of its tether.
- COURTS: The court of Saxony eases over The Wettin Crown — alliance is now the length of its tether.
- DIPLO +9 medium/low (law_enacted_abroad, province_changed_hands ×3, diplomatic_dp_regen, diplomatic_vassal_contingent, diplomatic_auto_downgrade, agenda_shift ×2)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: 3 approaches from Saxony and Hesse are rebuffed (defensive alliance)
  - LOG moment: The Arch-Chancellor's Letters — the Emperor answers: Let the Council act

## Turn 15 — Late April 1806
  - MAILBOX #15 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - MAILBOX #16 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #18 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #19 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with Austria — the table with Austria (2 pairs resolved). Prisoners: Mack, our captive, goes home to Vienna under this peace — an Austrian commander back in the field. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #18 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13893 · net +1653 · threat 43 · provinces 28 (+0) · ceiling 30420 · army 97771 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 587 · admin 50 · tribute 375 · upkeep 760 · charges 1189
- DISPATCH: Sire — peace with Austria is signed. A white peace — the map stands as it was.
  - RAIL settlement_summary: Settlement of the War with Austria — the table with Austria: a white peace.
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - RAIL crisis_brewing: THE BREWING CRISIS: Austria will move on Bavaria. You may compensate (1,332g — you can afford it); guarantee Bavaria (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 8
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And Sardinia and Hesse stir at their own designs.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent)
  - LOG ai_ai_proposal_refused: Russia and Austria rebuff Hanover (open borders agreement)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Hesse (design ask)
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 3 more — Prussia is not forgiven

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 actions unused) Turn 17 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 15524 · net +1468 · threat 45 · provinces 28 (+0) · ceiling 30200 · army 96203 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 549 · admin 50 · tribute 375 · upkeep 744 · charges 1352
- DISPATCH: Sire — Austria moves toward war with Bavaria. The design is open; the timing is not.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, coercive_demand)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (Alliance → Defensive Alliance)
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Pie…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Not enough actions! Need 1, have 0 — Massena cannot fortify today.
- CMD `end turn` → ✓ Turn 17 ended. Turn 18 begins!
- enemy phase: nothing visible — Austria, Britain, Prussia and 4 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 16168 · net +521 · threat 45 · provinces 28 (+0) · ceiling 20392 · army 94699 · vassals Holland 87 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 549 · admin 50 · tribute 375 · upkeep 1208 · charges 1745 · admiralty 90
- DISPATCH: Sire — Austria has declared war on Bavaria. The stated cause: Primacy in Germany.
  - RAIL diplomatic_alliance_cascade: France enters the war against Austria via its alliance with Bavaria.
  - RAIL diplomatic_offensive_cascade: Britain has joined Austria's war against Bavaria, honoring their alliance.
  - RAIL diplomatic_war_declared: Austria has declared war on Bavaria, with 2 allied courts poised to follow — Austria's relations with every court, France's included, fall 15.
  - TURN EVENTS 5
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +7 medium/low (law_enacted_abroad ×3, diplomatic_dp_regen, diplomatic_treaty_broken, witness_strike_recorded, diplomatic_relation_shift)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)
  - LOG diplomatic_treaty_broken: France was forced to break the Peace Treaty with Austria (cascade).
  - LOG defensive_cascade: Defensive cascade: France joins war via Bavaria
  - LOG moment: The Throne of Holland — a letter of the record is laid before the Emperor

## Turn 18 — Early June 1806
  - MAILBOX #17 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #20 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 7 actions, 1 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Davout
  - 🏴 Austria: Archduke Charles attacks Davout — Franconia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1020) vs Davout (lost 1434, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless. — The corps system brought Murat in.
  - verbs: move×3, recruit×2, attack×1, wait×1
- LEDGER treasury 16638 · net +804 · threat 45 · provinces 28 (+0) · ceiling 22895 · army 90251 · vassals Holland 86 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 1128 · charges 1879 · admiralty 90
- DISPATCH: Sire — Marshal Davout has been KILLED at Franconia — struck down at the head of his corps. 5,648 men pass to Murat. He will not return to the order of battle.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as joining the stronger side for pay.
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, sovereign_takes_field)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG moment: The Throne of Holland — the Emperor answers: Keep the Republic

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Piedmont. Army is now mobile.
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, move to Franconia` → ✗ Cannot move into Franconia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John, Hiller.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 6 actions, 1 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Hiller attacks Murat
  - ⚔ Hiller (lost 1506) vs Murat (lost 355, own corps) — A costly day for Hiller: the losses ran two to one in Murat's favour, and Hiller is still in the field.
  - verbs: form_square×2, attack×1, move×1, wait×1, recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 17445 · net +685 · threat 45 · provinces 28 (+0) · ceiling 22628 · army 87623 · vassals Holland 86 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 549 · admin 50 · tribute 712 · upkeep 1088 · charges 2038 · admiralty 90
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Defensive Alliance → Non-Aggression)

## Turn 20 — Early July 1806
  - MAILBOX #18 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #21 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (86 → 96); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Piedmont. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `rev1106-cmd-marengo_t20` → Game saved: rev1106-cmd-marengo_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 10 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Soult · Archduke John attacks Murat
  - ⚔ Archduke Charles (lost 1657) vs Soult (lost 1758, own corps) — Even Soult's fortifications could not hold, Sire. Archduke Charles overran the position.
  - ⚔ Archduke John (lost 681, own corps) vs Murat (lost 4135, own corps) — The toll on Murat's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2
- ORDER Lannes [awaiting_response]: Lannes is cornered at Swabia with 4,187 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the las…
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Swabia with 4,187 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- LEDGER treasury 17682 · net +656 · threat 45 · provinces 28 (+0) · ceiling 22236 · army 72230 · vassals Holland 92 · Kingdom of Italy 97 · Switzerland 90
  - NET income 2590 · trade 549 · admin 50 · tribute 375 · upkeep 560 · charges 2258 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Swabia. He must reform before he fights again.
  - TURN EVENTS 9
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_we_threshold ×2, diplomatic_dp_regen)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG ai_ai_proposal_refused: Austria rebuffs Hanover (open borders agreement)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Saxony and Hesse (defensive alliance)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — 'Soult, recruit' raises them at Lorraine. Nothing was spent.
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Swabia · Archduke John attacks Soult
  - 🏴 Austria: Archduke Charles attacks Swabia — Region captured: Swabia (was Bavaria) (secured)
  - ⚔ Archduke John (lost 425) vs Soult (lost 3174) — Soult's fortified position was overwhelmed. A costly investment lost, Sire.
  - verbs: attack×2, move×2
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 17529 · net -46 · threat 45 · provinces 28 (+0) · ceiling 17272 · army 68732 · vassals Holland 90 · Kingdom of Italy 96 · Switzerland 88
  - NET income 2581 · trade 462 · admin 50 · tribute 375 · upkeep 528 · charges 2795 · contributions 101 · admiralty 90
- DISPATCH: Sire — Marshal Lannes has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - TURN EVENTS 12
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Orleanais. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Murat · Hiller attacks Bernadotte · Mack attacks Rhineland
  - 🏴 Austria: Mack attacks Rhineland — Region captured: Rhineland (was France) (secured)
  - ⚔ Archduke Charles (lost 227) vs Murat (lost 3709, own corps) — Murat's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Hiller (lost 28, own corps) vs Bernadotte (lost 1971) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - verbs: attack×3, retreat×1, stance_change×1
- ORDER Murat [awaiting_response]: Murat is cornered at Lorraine with 2,125 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the la…
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Lorraine — 807 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Lorraine with 2,125 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Lorraine — 807 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 16611 · net -572 · threat 45 · provinces 27 (-1) · ceiling 14220 · army 59385 · vassals Holland 86 · Kingdom of Italy 93 · Switzerland 84
  - NET income 2431 · trade 462 · admin 50 · tribute 600 · upkeep 464 · charges 3500 · contributions 61 · admiralty 90
- DISPATCH: Sire — Rhineland has fallen to Austria. Enemy colours fly over French homeland soil. Mack's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 7
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, drill` → ✗ Soult is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Lorraine · Hiller attacks Soult · Hiller attacks Bernadotte
  - 🏴 Austria: Archduke Charles attacks Lorraine — Region captured: Lorraine (was France) (secured)
  - 🏴 Austria: Hiller attacks Bernadotte — Orleanais CAPTURED! (was France) (secured)
  - ⚔ Hiller (lost 258) vs Soult (lost 541) — The line gave way. Soult is falling back, and not in good order.
  - ⚔ Hiller (lost 33) vs Bernadotte (lost 648) — Bernadotte was driven from the field. His men are scattered.
  - verbs: attack×3, move×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 16341 · net -230 · threat 42 · provinces 25 (-2) · ceiling 15271 · army 58196 · vassals Holland 82 · Kingdom of Italy 90 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 600 · upkeep 456 · charges 3086 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, agenda_shift)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 34% of active European bloc power.

## Turn 24 — Early September 1806
  - MAILBOX #19 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #22 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 26.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Burgundy (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 0% -> 12%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 15037 · net +1238 · threat 41 · provinces 25 (+0) · ceiling 25350 · army 76196 · vassals Holland 82 · Kingdom of Italy 91 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 600 · upkeep 600 · charges 1564
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +4% this morning; the courts have begun to notice that he can be beaten.
  - RAIL status_quo_conceded: Lorraine, Orleanais and Rhineland — left with Austria by the peace, titled to them by treaty.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 25 — Late September 1806
  - MAILBOX #20 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #23 → reject_ai_proposal
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Piedmont. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✗ Soult is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 16275 · net +1089 · threat 40 · provinces 25 (+0) · ceiling 25350 · army 76196 · vassals Holland 82 · Kingdom of Italy 90 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 600 · upkeep 600 · charges 1713
- DISPATCH: Sire — Lorraine, Orleanais and Rhineland lie in enemy hands. Austria holds them.
  - RAIL allegiance_settled: The bidding for Hesse is closed in our favour, but our relations are too cool for any pact the table can sign.
  - TURN EVENTS 9
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 17364 · net +959 · threat 39 · provinces 25 (+0) · ceiling 25350 · army 76196 · vassals Holland 82 · Kingdom of Italy 91 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 600 · upkeep 600 · charges 1843
- DISPATCH: Sire — 3 turns now with Lorraine, Orleanais and Rhineland in enemy hands. The country counts every one of them.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, unfortify` → ✗ Soult is not currently fortified.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 10,000 infantry at Paris - Cost: 150 gold (capital discount). Morale: 60% -> 46%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 150g on this turn's orders
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 18086 · net +1129 · threat 38 · provinces 25 (+0) · ceiling 27491 · army 86196 · vassals Holland 82 · Kingdom of Italy 92 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 680 · charges 1930
- DISPATCH: Sire — Austria enacts the Corps d'Armée — +1 order of the day, from the next refill; cures The Hofkriegsrat — the court's doctrine flaw — while its Staff stands.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 1 action unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 19215 · net +994 · threat 37 · provinces 25 (+0) · ceiling 27491 · army 86196 · vassals Holland 82 · Kingdom of Italy 93 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 680 · charges 2065
- DISPATCH: Sire — Austria and Britain would now join a league against us (relations −92 and −71). The Balance of Europe names the price to keep each out.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Paris. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Burgundy. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot sh…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Piedmont. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 20209 · net +874 · threat 36 · provinces 25 (+0) · ceiling 27491 · army 86196 · vassals Holland 82 · Kingdom of Italy 94 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 680 · charges 2185
- DISPATCH: Sire — the ordinance allows 36,304 more men to the establishment, and the depots hold 97,500. 10,000 foot cost 150 gold at Paris under Lannes — 'recruit infantry in Paris'.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 3
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: And Sardinia and Austria stir at their own designs.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Remounts — an affair of state is laid before the Emperor

## Turn 30 — Early December 1806
  - MAILBOX #21 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #24 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat is fortified and cannot drill. Abandon fortification first.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Davout` → ✓ Lannes recruits 10,000 infantry (nearest to capital) - Cost: 150 gold (capital discount). Morale: 46% -> 43%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- SPENT 150g on this turn's orders
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 20846 · net +718 · threat 35 · provinces 25 (+0) · ceiling 26825 · army 96196 · vassals Holland 82 · Kingdom of Italy 95 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 760 · charges 2261
- DISPATCH: Sire — the enemy has held Lorraine, Orleanais and Rhineland 7 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Britain (Alliance → Defensive Alliance)
  - LOG moment: The Remounts — the Emperor answers: Let the depots wait

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will conduct drill training instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will conduct drill training instead.) → trust
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Burgundy. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify'…
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21564 · net +632 · threat 34 · provinces 25 (+0) · ceiling 26825 · army 96196 · vassals Holland 82 · Kingdom of Italy 96 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 760 · charges 2347
- DISPATCH: Sire — the ordinance allows 26,304 more men to the establishment, and the depots hold 92,500. 10,000 foot cost 150 gold at Paris under Lannes — 'recruit infantry in Paris'.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL allegiance_settled: The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22196 · net +556 · threat 33 · provinces 25 (+0) · ceiling 26825 · army 96196 · vassals Holland 82 · Kingdom of Italy 97 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 760 · charges 2423
- DISPATCH: Sire — London now pays Vienna 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 9 turns (9 DP); buying off her design costs 1…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Paris. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Aggr…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Burgundy. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — 'Lannes, recruit' raises them at Paris. Nothing was spent.
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 22752 · net +489 · threat 30 · provinces 25 (+0) · ceiling 26825 · army 96196 · vassals Holland 82 · Kingdom of Italy 98 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 760 · charges 2490
- DISPATCH: Sire — the enemy has held Lorraine, Orleanais and Rhineland 10 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Piedmont. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23241 · net +431 · threat 27 · provinces 25 (+0) · ceiling 26825 · army 96196 · vassals Holland 82 · Kingdom of Italy 99 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 760 · charges 2548
- DISPATCH: Sire — London now pays St Petersburg 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design …
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Paris. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Burgundy. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot sh…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 23672 · net +379 · threat 24 · provinces 25 (+0) · ceiling 26825 · army 96196 · vassals Holland 82 · Kingdom of Italy 100 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 760 · charges 2600
- DISPATCH: Sire — St Petersburg now pays Vienna 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 9 turns (9 DP); buying off her design …
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 36 — Early March 1807
  - MAILBOX #22 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #25 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Piedmont. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Aggress…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Burgundy (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 32% -> 33%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23826 · net +336 · threat 21 · provinces 25 (+0) · ceiling 26625 · army 99196 · vassals Holland 82 · Kingdom of Italy 99 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 784 · charges 2619
- DISPATCH: Sire — Austria, Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 i…
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Burgundy. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify'…
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24162 · net +296 · threat 18 · provinces 25 (+0) · ceiling 26625 · army 99196 · vassals Holland 82 · Kingdom of Italy 100 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 784 · charges 2659
- DISPATCH: Sire — the ordinance allows 23,304 more men to the establishment, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris under Lannes — 'recruit infantry in Paris'.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Piedmont. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24458 · net +261 · threat 15 · provinces 25 (+0) · ceiling 26625 · army 99196 · vassals Holland 82 · Kingdom of Italy 100 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 784 · charges 2694
- DISPATCH: Sire — the enemy has held Lorraine, Orleanais and Rhineland 15 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Burgundy. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 10,000 infantry at Paris - Cost: 150 gold (capital discount). Morale: 63% -> 56%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 150g on this turn's orders
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24482 · net +178 · threat 12 · provinces 25 (+0) · ceiling 25958 · army 109196 · vassals Holland 82 · Kingdom of Italy 100 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 864 · charges 2697
- DISPATCH: Sire — Austria, Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 i…
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Piedmont. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
  - saved `rev1106-cmd-marengo_t40` → Game saved: rev1106-cmd-marengo_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Austria, Prussia and 2 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 24660 · net +156 · threat 9 · provinces 25 (+0) · ceiling 25958 · army 109196 · vassals Holland 82 · Kingdom of Italy 100 · Switzerland 80
  - NET income 2290 · trade 462 · admin 50 · tribute 937 · upkeep 864 · charges 2719
- DISPATCH: Sire — the ordinance allows 13,304 more men to the establishment, and the depots hold 95,000. 10,000 foot cost 150 gold at Paris under Lannes — 'recruit infantry in Paris'.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing_other, agenda_shift)
  - LOG coalition_brewing_started: Coalition brewing against Britain — Spain consulting (their alarm: 60)

---
finished: **completed** · commands 200 · popups 56 · battles 22
