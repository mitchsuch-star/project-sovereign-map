# Playtest digest — iq8-cmd-marengo

seed `marengo` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `marengo` · dice `marengo`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7d10e20c0073` (dirty) · content `457e8f82bc61` · driver `641a9fcf2c43`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march, up to 96,789 if every corps arrives) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2629, own corps) vs Mack (lost 9416) — Reinforcements from Davout and Napoleon bolstered Ney's position — though Soult, Lannes, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Mack.
- CMD `Lannes, move to Rhineland` → ✓ Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?'
  - POPUP strategic_interrupt: Lannes, contact_bad_odds, Lannes: 'Mack blocks the path at Swabia. Odds unfavorable. Your orders?' → attack_anyway
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1858, own corps) vs Mack (lost 9277) — Ney and Bernadotte's timely arrival aided Lannes. Soult and Murat, however, were conspicuously absent.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 action(s) unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles'…
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franconia. (1,573 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1538, own corps) vs Deroy (lost 9954) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - verbs: stance_change×2, move×1, attack×1, wait×1
- ORDER Lannes [active]: Lannes is marching to Rhineland (3 turn(s) remaining).
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2489 · net +2288 · threat 67 · provinces 28 · ceiling 57480 · army 174905 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 3400 · trade 350 · admin 50 · tribute 937 · upkeep 2164 · charges 20 · blockade 175 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: PEACE → OPEN_BORDERS with Prussia. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders → (stale passthrough — #1 already answered this chain)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (18,578; 80,289 if all march, up to 92,807 if every corps arrives) vs Mack (substantial force) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 607, own corps) vs Mack (lost 16736) — Lannes and Massena arrived to reinforce Ney, but Murat and Bernadotte failed to reach the field in time.
- CMD `Davout, attack Mack` → ✓ Davout pursues Mack (at Munich). Moves to Swabia. Davout: "Pursuit, then. I do not intend to be led into anything."
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action(s) unused) Turn 3 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Davout. Casualties: ArchdukeChar… · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeCharles holds them at Swabia while allies attack from Franconia! (+1 coordination) · ArchdukeJohn holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - ⚔ Archduke Charles (lost 2212, own corps) vs Davout (lost 3849, own corps) — Reinforcements from Napoleon bolstered Davout's position — though Ney, Soult and Murat never arrived, Sire.
  - ⚔ Archduke John (lost 197, own corps) vs Deroy (lost 5519) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1031, own corps) vs Bernadotte (lost 7183) — Bernadotte stood alone, Sire. Ney and Soult never came.
  - ⚔ Archduke John (lost 723, own corps) vs Davout (lost 3757) — Not one corps reached Davout. Ney, Soult and Murat were expected; Davout fought the battle single-handed.
  - verbs: attack×4, wait×1
- ORDER Davout [active]: Davout is pursuing Mack (0 turn(s) remaining).
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4676 · net +2905 · threat 73 · provinces 28 (+0) · ceiling 53409 · army 151093 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 3400 · trade 450 · admin 50 · tribute 937 · upkeep 1458 · charges 159 · blockade 225 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (16,882; 82,090 if all march, up to 82,928 if every corps arrives) vs Mack (14,707 men) at Franconia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 82, own corps) vs Mack (lost 13728) — Lannes and Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire. And Mack was taken on that field …
  - POPUP capture_choice[capture]: Franconia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 681 gold. Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 action(s) unused) Turn 4 begins!
- SPENT 681g on this turn's orders
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces advance steadily. Brutal stalemate between ArchdukeCharles and Davout. Heavy casualties on bot… · ArchdukeJohn's forces advance steadily. ArchdukeJohn gains the advantage over Davout. Casualties: ArchdukeJohn's army 1…
  - ⚔ Archduke Charles (lost 2739, own corps) vs Davout (lost 1065, own corps) — Ney, Murat and Napoleon arrived to reinforce Davout, but Soult failed to reach the field in time.
  - ⚔ Archduke John (lost 445, own corps) vs Davout (lost 4515) — Davout stood alone, Sire. Soult never came.
  - verbs: attack×2, move×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6813 · net +2904 · threat 81 · provinces 29 (+1) · ceiling 36082 · army 141281 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 91
  - NET income 3438 · trade 525 · admin 50 · tribute 937 · upkeep 1146 · charges 477 · occupation 70 · blockade 263 · admiralty 90
- DISPATCH: Sire — Marshal Mack of Austria is taken at Franconia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #9 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #10 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (7 pair(s) resolved). → display-only
- CMD `Ney, attack Mack` → ✗ We are not at war with Austria, Sire — Mack may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, ma…
- CMD `Massena, move to Tyrol` → ✗ Cannot enter Tyrol — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 action(s) unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
  - POPUP marshal_petition: shadow_command, Marshal Soult asks for a command → detach
  -     ↳ Soult straightens. "You will not regret it, Sire." Name him a front of his own when one opens — the order is …
- LEDGER treasury 10583 · net +3511 · threat 40 · provinces 29 (+0) · ceiling 94166 · army 138190 · vassals Holland 94 · Kingdom of Italy 94 · Switzerland 89
  - NET income 3439 · trade 623 · admin 50 · tribute 937 · upkeep 1108 · charges 360 · occupation 70
- DISPATCH: Sire — Ney, Lannes and Massena stand 64,000 men at Franconia, which feeds 60,000. 4,000 too many. 4,479 men lost in 2 turns. No depot may be laid at Franconia — region stability too low (45/100). Nee…
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 7
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 81 to 40.

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #11 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #12 → reconsider
- CMD `Lannes, attack Mack` → ✗ We are not at war with Austria, Sire — Mack may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (933 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (221 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action(s) unused) Turn 6 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: defend×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (92 → 100); standing 0 → 20 (+1 loyalty a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14534 · net +3566 · threat 40 · provinces 29 (+0) · ceiling 311666 · army 133779 · vassals Holland 100 · Kingdom of Italy 92 · Switzerland 87
  - NET income 3519 · trade 623 · admin 50 · tribute 600 · upkeep 1036 · charges 150 · occupation 40
- DISPATCH: Sire — Ney, Lannes and Massena stand 61,929 men at Franconia, which feeds 60,000. 1,929 too many. 6,550 men lost in 3 turns. A supply depot at Franconia would ease it; Frankfurt can feed 50,000 more …
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a proposal.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 8.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 1 action(s) unused) Turn 7 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Ney (120g/turn); Lannes (120g/turn); Bernadotte (40g/turn). The …
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #14 → grant the petition
  - POPUP proposal_result: Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (90 → 100); standing 0 → 20 (+1 loyalty a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 18131 · net +2759 · threat 40 · provinces 29 (+0) · ceiling 248000 · army 130647 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 85
  - NET income 3522 · trade 623 · admin 50 · tribute 225 · upkeep 1008 · charges 193 · occupation 40 · rentes 420
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a proposal.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — gold is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 7.
- CMD `Davout, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, attack Archduke Charles` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #15 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #16 → reconsider
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 action(s) unused) Turn 8 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 20902 · net +2738 · threat 40 · provinces 29 (+0) · ceiling 249000 · army 127634 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 83
  - NET income 3526 · trade 623 · admin 50 · tribute 225 · upkeep 1000 · charges 226 · occupation 40 · rentes 420
- DISPATCH: Sire — Marshal Massena's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 8 — Early January 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — A Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #17 → grant the petition
  - POPUP diplomatic_dialogue: Switzerland, client_petition → (stale passthrough — #17 already answered this chain)
- CMD `Davout, attack Archduke Charles` → ✗ We are not at war with Austria, Sire — Archduke Charles may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); standing 0 → 20 (+1 loyalty a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action(s) unused) Turn 9 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 23520 · net +2586 · threat 40 · provinces 29 (+0) · ceiling 239000 · army 124730 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 92
  - NET income 3571 · trade 623 · admin 50 · upkeep 960 · charges 258 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's household goes unpaid. His patience erodes with his purse.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Franconia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 action(s) unused) Turn 10 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 26118 · net +2567 · threat 40 · provinces 29 (+0) · ceiling 240000 · army 121933 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 91
  - NET income 3575 · trade 623 · admin 50 · upkeep 952 · charges 289 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena has now gone unrewarded 7 turns. The staff have noticed which of us he no longer looks at.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Primacy in Germany — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Ney is already in Franconia.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 action(s) unused) Turn 11 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 28721 · net +2572 · threat 40 · provinces 29 (+0) · ceiling 243000 · army 119224 · vassals Holland 95 · Kingdom of Italy 96 · Switzerland 90
  - NET income 3579 · trade 623 · admin 50 · upkeep 920 · charges 320 · occupation 20 · rentes 420
- DISPATCH: Sire — 8 turns without settlement on Marshal Massena. A rente would close it today; the arrears will not close themselves.
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #19 → reconsider
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Franconia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 31314 · net +2562 · threat 40 · provinces 29 (+0) · ceiling 244750 · army 116120 · vassals Holland 94 · Kingdom of Italy 95 · Switzerland 89
  - NET income 3584 · trade 623 · admin 50 · upkeep 904 · charges 351 · occupation 20 · rentes 420
- DISPATCH: Sire — Ney, Lannes, Murat and Massena stand 67,750 men at Franconia, which feeds 60,000. 7,750 too many. 6,443 men lost in 3 turns. A supply depot at Franconia would ease it; Frankfurt can feed 50,00…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 85% -> 75%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action(s) unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 33665 · net +2546 · threat 40 · provinces 29 (+0) · ceiling 245750 · army 116025 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 88
  - NET income 3588 · trade 623 · admin 50 · upkeep 896 · charges 379 · occupation 20 · rentes 420
- DISPATCH: Sire — Ney, Lannes, Murat and Massena stand 67,655 men at Franconia, which feeds 60,000. 7,655 too many. 7,835 men lost in 3 turns. A supply depot at Franconia would ease it; Frankfurt can feed 50,00…
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #20 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #21 → reconsider
- CMD `Davout, move to Franconia` → ✓ Davout moves from Swabia to Franconia
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 action(s) unused) Turn 14 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 36247 · net +2888 · threat 38 · provinces 29 (+0) · ceiling 276833 · army 111869 · vassals Holland 92 · Kingdom of Italy 93 · Switzerland 87
  - NET income 3592 · trade 623 · admin 50 · tribute 337 · upkeep 864 · charges 410 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Franconia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' → trust
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Franconia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 39171 · net +3263 · threat 36 · provinces 29 (+0) · ceiling 311083 · army 108021 · vassals Holland 91 · Kingdom of Italy 92 · Switzerland 86
  - NET income 3596 · trade 623 · admin 50 · tribute 712 · upkeep 832 · charges 446 · occupation 20 · rentes 420
- DISPATCH: Sire — Ney, Davout, Lannes, Murat and Massena have been 4 turns over what Franconia can feed. 11,099 men. The country will ask where the army went. A supply depot at Franconia would ease it; Frankfur…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 16 approaches rebuffed, chiefly from Bavaria (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #12 Holland incoming_proposal: Holland — A Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP diplomatic_dialogue: Holland, client_petition → (stale passthrough — #22 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (91 → 100); standing 20 → 40 (+2 loyalty a turn). Cost: 1 DP. → display-only
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 action(s) unused) Turn 16 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 42133 · net +3152 · threat 34 · provinces 29 (+0) · ceiling 304750 · army 104448 · vassals Holland 100 · Kingdom of Italy 91 · Switzerland 85
  - NET income 3600 · trade 623 · admin 50 · tribute 600 · upkeep 800 · charges 481 · occupation 20 · rentes 420
- DISPATCH: Sire — Ney, Davout, Lannes, Murat and Massena have been 5 turns over what Franconia can feed. 11,577 men. The country will ask where the army went. A supply depot at Franconia would ease it; Frankfur…
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 16 — Early May 1806
  - MAILBOX #13 KingdomOfItaly incoming_proposal: Kingdom of Italy — A Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #23 → grant the petition
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition → (stale passthrough — #23 already answered this chain)
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
  - POPUP proposal_result: Kingdom of Italy's tribute is remitted for 8 collections (3000g forgone). Loyalty +10 (91 → 100); standing 20 → 40 (+2 loyalty a turn). Cost: 1 DP. → display-only
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action(s) unused) Turn 17 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 44926 · net +2759 · threat 32 · provinces 29 (+0) · ceiling 274833 · army 101124 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 84
  - NET income 3600 · trade 623 · admin 50 · tribute 225 · upkeep 784 · charges 515 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 17 — Late May 1806
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — A Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #24 → grant the petition
  - POPUP diplomatic_dialogue: Switzerland, client_petition → (stale passthrough — #24 already answered this chain)
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (84 → 94); standing 20 → 40 (+2 loyalty a turn). Cost: 1 DP. → display-only
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franconia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action(s) unused) Turn 18 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 47492 · net +2536 · threat 30 · provinces 29 (+0) · ceiling 258750 · army 98026 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · upkeep 752 · charges 545 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Bavaria (open borders agreement)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 37% -> 37%
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 action(s) unused) Turn 19 begins!
- SPENT 170g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 49843 · net +2515 · threat 28 · provinces 29 (+0) · ceiling 259416 · army 97937 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · upkeep 744 · charges 574 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 action(s) unused) Turn 20 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 52374 · net +2501 · threat 26 · provinces 29 (+0) · ceiling 260750 · army 95052 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · upkeep 728 · charges 604 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 action(s) unused) Turn 21 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 54899 · net +2495 · threat 24 · provinces 29 (+0) · ceiling 262750 · army 92319 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · upkeep 704 · charges 634 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Franconia (field levy — no depot; capped at 3,000) (recruitment is drafted in fix…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 action(s) unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 57028 · net +2469 · threat 22 · provinces 29 (+0) · ceiling 262750 · army 92574 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · upkeep 704 · charges 660 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 action(s) unused) Turn 23 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 59505 · net +2784 · threat 20 · provinces 29 (+0) · ceiling 291500 · army 89966 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 337 · upkeep 696 · charges 690 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action(s) unused) Turn 24 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 62313 · net +3150 · threat 18 · provinces 29 (+0) · ceiling 324750 · army 87489 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 712 · upkeep 672 · charges 723 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 action(s) unused) Turn 25 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 65487 · net +3361 · threat 16 · provinces 29 (+0) · ceiling 345500 · army 85135 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 648 · charges 761 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action(s) unused) Turn 26 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
  - POPUP redemption: Massena, 20 → grant_autonomy
  -     ↳ Massena has been granted autonomy. They will act independently for 3 turns, using their own judgment in battl…
- LEDGER treasury 68864 · net +3336 · threat 14 · provinces 29 (+0) · ceiling 346833 · army 82898 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 632 · charges 802 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is acting independently. 3 turns remaining.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 72208 · net +3304 · threat 12 · provinces 29 (+0) · ceiling 347500 · army 80775 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 624 · charges 842 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 95% -> 77%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action(s) unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 75297 · net +3275 · threat 10 · provinces 29 (+0) · ceiling 348166 · army 81607 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 616 · charges 879 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Massena is not currently fortified.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 78580 · net +3244 · threat 8 · provinces 29 (+0) · ceiling 348833 · army 79547 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 608 · charges 918 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 26 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 81848 · net +3228 · threat 6 · provinces 29 (+0) · ceiling 350833 · army 77591 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 584 · charges 958 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 27 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only).…
- CMD `recruit 10000 infantry with Davout` → ✓ Davout recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 170 gold (Davout's intendance: -15%). Morale: 57% -> 50%
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 action(s) unused) Turn 31 begins!
- SPENT 170g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 84867 · net +3176 · threat 4 · provinces 29 (+0) · ceiling 349500 · army 78582 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 600 · charges 994 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 28 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' → trust
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 action(s) unused) Turn 32 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 88051 · net +3146 · threat 2 · provinces 29 (+0) · ceiling 350166 · army 76673 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 592 · charges 1032 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 29 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 action(s) unused) Turn 33 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 91229 · net +3140 · threat 0 · provinces 29 (+0) · ceiling 352833 · army 74860 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 560 · charges 1070 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 30 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Franconia (field levy — no depot; capped at 3,000) (recruitment is drafted in fix…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action(s) unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 93987 · net +3091 · threat 0 · provinces 29 (+0) · ceiling 351500 · army 75988 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 623 · admin 50 · tribute 937 · upkeep 576 · charges 1103 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 31 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Franconia. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 action(s) unused) Turn 35 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 97048 · net +3024 · threat 0 · provinces 29 (+0) · ceiling 349000 · army 74209 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 585 · admin 50 · tribute 937 · upkeep 568 · charges 1140 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 32 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action(s) unused) Turn 36 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
  - POPUP redemption: Massena, 19 → grant_autonomy
  -     ↳ Massena has been granted autonomy. They will act independently for 3 turns, using their own judgment in battl…
- LEDGER treasury 100096 · net +3011 · threat 0 · provinces 29 (+0) · ceiling 351000 · army 72518 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 585 · admin 50 · tribute 937 · upkeep 544 · charges 1177 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 33 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, fortify` → ✗ Massena is acting independently. 3 turns remaining.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 action(s) unused) Turn 37 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 103115 · net +2983 · threat 0 · provinces 29 (+0) · ceiling 351666 · army 70912 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 585 · admin 50 · tribute 937 · upkeep 536 · charges 1213 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 34 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 action(s) unused) Turn 38 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 106106 · net +2955 · threat 0 · provinces 29 (+0) · ceiling 352333 · army 69387 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 585 · admin 50 · tribute 937 · upkeep 528 · charges 1249 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 35 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is acting independently. 1 turn remaining.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 action(s) unused) Turn 39 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 109085 · net +2943 · threat 0 · provinces 29 (+0) · ceiling 354333 · army 67938 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 585 · admin 50 · tribute 937 · upkeep 504 · charges 1285 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 36 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franconia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 97% -> 75%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 action(s) unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 111790 · net +2895 · threat 0 · provinces 29 (+0) · ceiling 353000 · army 69412 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 585 · admin 50 · tribute 937 · upkeep 520 · charges 1317 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 37 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Franconia (+0% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 action(s) unused) Turn 41 begins!
- enemy phase: nothing visible — Our scouts report activity within the borders of Britain, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Russia, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Austria, but their formations remain beyond our sight.
  - fogged: Our scouts report activity within the borders of Prussia, but their formations remain beyond our sight.
  - fogged: +6 more court(s) not listed
- LEDGER treasury 114693 · net +2868 · threat 0 · provinces 29 (+0) · ceiling 353666 · army 67962 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 94
  - NET income 3600 · trade 585 · admin 50 · tribute 937 · upkeep 512 · charges 1352 · occupation 20 · rentes 420
- DISPATCH: Sire — Marshal Massena's claim is 38 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 200 · popups 53 · battles 11
