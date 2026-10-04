# Playtest digest — sf4-q0-gev-b-nodoc

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "client_petition": "grant"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `e631f4bd4a79` (dirty) · content `c4151b82bd80` · driver `f7650c682a9c`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `vassalize Bavaria` → ✓ Sire, regarding the Vassalage proposal to Bavaria, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → confirm
  - POPUP proposal_result: Talleyrand departs for the Bavaria court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2595, own corps) vs Mack (lost 12882) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr… — Berthier: the corps marched apart and arrived together.
- CMD `Lannes, attack Mack` → ✓ MUSTER — Lannes (16,542; expect about 93,571 with the corps likely to arrive, up to 106,179 if all march) vs Mack (39,118 men) at Swabia — the balance of force looks fav…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 1108, own corps) vs Mack (lost 19040) — Soult, Murat and Bernadotte never reached the guns. The battle was decided without them, Sire.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,340; expect about 83,428 with the corps likely to arrive, up to 95,645 if all march) vs Mack (strength unknown) at Munich — the balance of force look…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 154, own corps) vs Mack (lost 14954) — Reinforcements! Ney, Murat and Massena marched onto the field beside Davout. The enemy's advantage melted away. — Berthier: the corps marched apart and arrived together.
- CMD `Murat, move to Swabia` → ✓ Murat moves from Munich to Swabia (305 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces advance steadily. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke …
  - ⚔ Archduke Charles (lost 2132) vs Bernadotte (lost 5610) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Bavaria, vassalage #5 → accept
  - POPUP proposal_result: You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 4 · Bavaria vassalage · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1723 · net +1350 · threat 92 · provinces 28 · ceiling 29663 · army 186467 · vassals Bavaria 60 · Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 275 · admin 50 · tribute 1213 · upkeep 2516 · blockade 172 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a third of his corps — 5,610 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Bavaria with a response.
  - TURN EVENTS 4
- DIPLO +9 medium/low (diplomatic_proposal_sent, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, move to Munich` → ✗ Ney is already in Munich.
- CMD `Davout, move to Munich` → ✗ Davout is already in Munich.
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Swabia to Munich (302 lost to march)
- CMD `Murat, move to Munich` → ✓ Murat moves from Swabia to Munich (527 lost to march)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,777 troops. Garrison… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,543 troops in the assau…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - verbs: attack×2
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 3431 · net +1574 · threat 95 · provinces 28 (+0) · ceiling 33692 · army 177501 · vassals Bavaria 64 · Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 350 · admin 50 · tribute 1205 · upkeep 2238 · charges 74 · blockade 219 · admiralty 90
- DISPATCH: Sire — Milan has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +8 medium/low (diplomatic_carved_vassal_created, diplomatic_treaty_signed ×4, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 15 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, ma…
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (900 lost to march)
- CMD `Massena, move to Piedmont` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1096, own corps) vs Archduke John (lost 7200) — Reinforcements from Massena bolstered Murat's position — though Ney and Lannes never arrived, Sire.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 5299 · net +1791 · threat 96 · provinces 28 (+0) · ceiling 37053 · army 170386 · vassals Bavaria 69 · Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 437 · admin 50 · tribute 1217 · upkeep 2028 · charges 186 · requisitions 75 · blockade 274 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Lannes and Deroy stand 67,931 men at Munich, which feeds 37,500. 30,431 too many. 16,059 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 11
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Soult, move to Munich` → ✓ Soult moves from Swabia to Munich (1,641 lost to march)
- CMD `Bernadotte, move to Munich` → ✓ Bernadotte moves from Franconia to Munich (225 lost to march)
- CMD `Deroy, move to Munich` → ✗ Deroy is already in Munich.
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'We outnumber them! Let me attack!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Tyro…
  - POPUP objection: Massena, Massena firmly objects: 'We outnumber them! Let me attack!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Tyrol instead.) → insist
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Brutal stalemate between Archduke Charles and Ney. Heavy casualties on b… · Archduke Charles's forces advance steadily. Brutal stalemate between Archduke Charles and Ney. Heavy casualties on both…
  - ⚔ Archduke Charles (lost 3320) vs Ney (lost 2573, own corps) — Soult, Murat, Bernadotte and Deroy never reached the guns. The battle was decided without them, Sire.
  - ⚔ Archduke Charles (lost 2541) vs Ney (lost 2261, own corps) — Ney fought without Soult, Murat, Bernadotte and Deroy's support. The roads, or the will, proved insufficient.
  - verbs: attack×2
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 445, own corps) vs Archduke John (lost 6900) — Reinforcements from Lannes bolstered Ney's position — though Soult, Murat, Bernadotte and Deroy never arrived, Sire.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  -     ↳ audience: No marshal waits upon you, Sire.
- LEDGER treasury 7101 · net +1913 · threat 97 · provinces 29 (+1) · ceiling 27446 · army 155610 · vassals Bavaria 74 · Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2590 · trade 512 · admin 50 · tribute 1228 · upkeep 1578 · charges 479 · requisitions 75 · occupation 75 · blockade 320 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Tyrol — Archduke John's corps is driven from Tyrol yet again — broken, and fleeing.
  - TURN EVENTS 13
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 10 courts rebuff Austria (non-aggression pact)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Prussia (open borders agreement)

## Turn 5 — Late November 1805
- CMD `vassalize Hesse` → ✓ Sire, regarding the Vassalage proposal to Hesse, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #11 → confirm
  - POPUP proposal_result: Talleyrand departs for the Hesse court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `vassalize Saxony` → ✓ Sire, regarding the Vassalage proposal to Saxony, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #12 → confirm
  - POPUP proposal_result: Talleyrand departs for the Saxony court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `declare war on Hanover` → ✗ Talleyrand is currently en route to a foreign court. He cannot negotiate until he returns.
- CMD `Soult, move to Franconia` → ✓ Soult moves from Munich to Franconia (587 lost to march)
- CMD `Bernadotte, move to Franconia` → ✓ Bernadotte moves from Munich to Franconia (105 lost to march)
- CMD `Ney, move to Franconia` → ✓ Ney moves from Tyrol to Franconia (113 lost to march)
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Tyrol to Franconia (100 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Bohemia into Tyrol unopposed! (2,612 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Bohemia into Tyrol unopposed! (2,612 lost to march) Captured: France → Austria
  - verbs: attack×1, form_square×1
  - POPUP proposal_result: Saxony has rejected our Vassalage. → display-only
- ENVOYS WAITING 2 · Austria armistice losing · Switzerland client petition
- LEDGER treasury 9352 · net +2083 · threat 95 · provinces 28 (-1) · ceiling 40348 · army 152418 · vassals Bavaria 78 · Holland 100 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 512 · admin 50 · tribute 1240 · upkeep 1480 · charges 494 · requisitions 75 · blockade 320 · admiralty 90
- DISPATCH: Sire — Tyrol has been taken by Austria.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Saxony with a response.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the w…
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_proposal_sent ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
  - MAILBOX #9 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #10 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #13 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Switzerland. Your earlier answer was not delivered; th…
  - POPUP diplomatic_dialogue: incoming_proposal #14 → grant the petition
  - POPUP diplomatic_dialogue: Austria, armistice_losing #13 → accept
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +7 (93 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #14 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Soult, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Bernadotte, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Ney, attack Archduke John` → ✗ Cannot attack Archduke John — armistice with Austria (5 turns remaining).
- CMD `Deroy, move to Franconia` → ✓ Deroy moves from Munich to Franconia (177 lost to march)
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: break_square×1, fortify×1
- ORDER Massena [error]: Massena could not advance toward Franche-Comte.
- ORDER Murat [completed]: Murat arrives at Franche-Comte. Murat: "It is done. Point me at something that shoots back, Sire."
- LEDGER treasury 10991 · net +1451 · threat 93 · provinces 28 (+0) · ceiling 25436 · army 148725 · vassals Bavaria 80 · Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 512 · admin 50 · tribute 1021 · treaty 68 · upkeep 1368 · charges 902 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_treaty_signed, enemy_marshal_commissioned, diplomatic_dp_regen, coercive_demand)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, move to Osnabruck` → ✗ Cannot enter Osnabruck — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Franche-Comte to Franconia (342 lost to march)
- CMD `Lannes, attack Archduke John` → ✗ Cannot attack Archduke John — armistice with Austria (4 turns remaining).
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [error]: Massena could not advance toward Franche-Comte.
- LEDGER treasury 12606 · net +1419 · threat 91 · provinces 28 (+0) · ceiling 26295 · army 143458 · vassals Bavaria 82 · Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 512 · admin 50 · tribute 1027 · treaty 68 · upkeep 1210 · charges 1098 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — Massena is no nearer home, and the safe passage runs out in 1 turn. After that his corps will be interned where it stands.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)

## Turn 8 — Early January 1806
- CMD `Lannes, retreat` → ✗ Lannes is not in danger. No retreat necessary.
- CMD `Massena, attack Archduke John` → ✗ Massena is fortified at Milan and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Soult, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Napoleon, move to Franconia` → ✓ Napoleon moves from Swabia to Franconia (87 lost to march)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [error]: Massena could not advance toward Franche-Comte.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
- LEDGER treasury 14141 · net +1337 · threat 89 · provinces 28 (+0) · ceiling 26653 · army 137939 · vassals Bavaria 84 · Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 512 · admin 50 · tribute 1033 · treaty 68 · upkeep 1100 · charges 1296 · contributions 110 · blockade 320 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 7 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, attack Hanover` → ✗ Bernadotte cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Massena, move to Milan` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Ney, move to Franconia` → ✗ Ney is already in Franconia.
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Massena [error]: Massena could not advance toward Franche-Comte.
- LEDGER treasury 15504 · net +1454 · threat 87 · provinces 28 (+0) · ceiling 28718 · army 98193 · vassals Bavaria 86 · Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 512 · admin 50 · tribute 1039 · treaty 68 · upkeep 760 · charges 1485 · contributions 150 · blockade 320 · admiralty 90
- DISPATCH: Sire — Marshal Massena's corps was interned at Milan by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, move to Oldenburg` → ✓ Bernadotte begins marching to Oldenburg (distance: 4). Moved to Frankfurt. Route: Frankfurt -> Brunswick -> Hanover -> Oldenburg.
- CMD `Deroy, move to Franconia` → ✗ Deroy is already in Franconia.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
  - saved `sf4-q0-gev-b-nodoc_t10` → Game saved: sf4-q0-gev-b-nodoc_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: naval_expedition×1
- ORDER Bernadotte [active]: Bernadotte is marching to Oldenburg (4 turns remaining).
- ENVOYS WAITING 2 · Britain settlement offer · KingdomOfItaly client petition
- LEDGER treasury 16928 · net +1220 · threat 85 · provinces 28 (+0) · ceiling 27697 · army 94302 · vassals Bavaria 88 · Holland 100 · Kingdom of Italy 98 · Switzerland 95
  - NET income 2590 · trade 512 · admin 50 · tribute 1045 · upkeep 728 · charges 1689 · contributions 150 · blockade 320 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 11 — Late February 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #12 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → reject_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Kingdom Of Italy. Your earlier answer was not delivere…
  - POPUP diplomatic_dialogue: incoming_proposal #16 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → reject_settlement_offer
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +2 (98 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #16 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Deroy, move to Bohemia` → ✓ Deroy moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (133 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Deroy → secure
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, move to Franconia` → ✗ Soult is already in Franconia.
- CMD `Napoleon, move to Swabia` → ✓ Napoleon moves from Franconia to Swabia (72 lost to march)
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 7 actions, 5 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks with overwhelming force. Deroy holds the line. Casualties: Archduke John 5,232, Deroy's army 1,21… · Archduke Charles engages in solid combat. Brutal stalemate between Archduke Charles and Soult. Heavy casualties on both… · Castanos's attack falters disastrously! Brutal stalemate between Castanos and Wellesley. Heavy casualties on both sides… · Castanos launches a decisive assault. Brutal stalemate between Castanos and Wellesley. Heavy casualties on both sides: …
  - ⚔ Archduke John (lost 5232) vs Deroy (lost 525, own corps) — Reinforcements from Ney, Lannes and Murat bolstered Deroy's position — though Soult never arrived, Sire.
  - ⚔ Archduke Charles (lost 2801) vs Soult (lost 2010, own corps) — Napoleon arrived to reinforce Soult, but Davout, Bernadotte and Deroy failed to reach the field in time.
  - ⚔ Castanos (lost 632) vs Wellesley (lost 563) — Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty.
  - ⚔ Castanos (lost 492) vs Wellesley (lost 668) — The enemy's repeated assaults have leveled our defenses. We fight without cover.
  - ⚔ Castanos (lost 361) vs Wellesley (lost 646) — The margin was slim. Training and preparation would serve Wellesley well.
  - verbs: attack×5, fortify×1, unfortify×1
- ORDER Bernadotte : Bernadotte: 'Cannon fire at Bohemia, Sire. Investigate?'
  - POPUP strategic_interrupt: Bernadotte, cannon_fire, Bernadotte: 'Cannon fire at Bohemia, Sire. Investigate?' → investigate
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout demands to be heard → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Naples open borders · Bavaria client petition
- LEDGER treasury 17770 · net +856 · threat 85 · provinces 29 (+1) · ceiling 24998 · army 89115 · vassals Bavaria 93 · Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2590 · trade 512 · admin 50 · tribute 833 · upkeep 672 · charges 1867 · contributions 80 · occupation 100 · blockade 320 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 6 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG ai_ai_proposal_refused: Spain rebuffs Naples and Denmark (open borders agreement)

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
  - MAILBOX #14 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #19 → grant the petition
  - POPUP proposal_result: Bohemia is ceded to Bavaria. Loyalty +7 (93 → 100); bond 59 → 59 (+2 a turn). Cost: 1 DP. Our net rises by 100g a turn — 0g of income forfeited, 100g of occupation relieved, 0g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `invest in Saxony` → ✗ Saxony is not a vassal.
- CMD `Soult, move to Bohemia` → ✓ Soult moves from Franconia to Bohemia (167 lost to march)
- CMD `Davout, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `Massena, move to Swabia` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Murat, move to Franconia` → ✓ Murat moves from Bohemia to Franconia (126 lost to march)
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 10 actions, 6 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Davout. Heavy casualties on… · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Murat. Casualties: Archduke Cha… · ArchdukeCharles holds them at Franconia while allies attack from Tyrol! (+1 coordination) · Castanos takes Andalusia where he stands! Captured: Britain → Spain
  - 🏴 Spain: Castanos takes Andalusia where he stands! Captured: Britain → Spain
  - ⚔ Archduke Charles (lost 2469) vs Davout (lost 1772, own corps) — Reinforcements from Napoleon bolstered Davout's position — though Murat never arrived, Sire.
  - ⚔ Archduke Charles (lost 1546) vs Murat (lost 3387, own corps) — Reinforcements from Lannes bolstered Murat's position — though Soult and Deroy never arrived, Sire.
  - ⚔ Archduke Charles (lost 694) vs Bernadotte (lost 3182) — Where were Ney, Soult and Deroy? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Castanos (lost 155) vs Wellesley (lost 754) — Wellesley stood alone, Sire. Paget never came.
  - ⚔ Castanos (lost 820) vs Paget (lost 902) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×6, move×3, break_square×1
- LEDGER treasury 18226 · net +625 · threat 83 · provinces 28 (-1) · ceiling 23060 · army 78095 · vassals Bavaria 100 · Holland 96 · Kingdom of Italy 97 · Switzerland 90
  - NET income 2590 · trade 537 · admin 50 · tribute 650 · upkeep 600 · charges 2096 · contributions 80 · blockade 336 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
- CMD `Soult, attack Vienna` → ✓ ASSAULT — Soult storms the works at Vienna alone: 16,098 men, 20,271 in the assault's reckoning (+10% from the corps at his side), against a garrison of 25,000. Ney, Lan…
  - ↳ Soult assaults the Vienna garrison! Garrison: 25,000 -> 17,906 (-7,094). Soult loses 4,963 troops. Garrison holds — 17,906 defenders remain. It regains up to 2,000 a tur…
- CMD `Deroy, attack Vienna` → ✓ ASSAULT — Deroy storms the works at Vienna alone: 11,904 men, 14,291 in the assault's reckoning (+16% from the corps at his side), against a garrison of 17,906. Ney, Sou…
  - ↳ Deroy assaults the Vienna garrison! Garrison: 17,906 -> 12,905 (-5,001). Deroy loses 3,728 troops. Garrison holds — 12,905 defenders remain. It regains up to 2,000 a tur…
- CMD `Davout, move to Bohemia` → ✓ Davout respectfully raises concerns: 'That road to Bohemia runs through enemy country, Sire. It is dangerous.' (Trust him and he will fortify current position instead.)
  - POPUP objection: Davout, Davout respectfully raises concerns: 'That road to Bohemia runs through enemy country, Sire. It is dangerous.' (Trust him and he will fortify current position instead.) → insist
- CMD `Napoleon, move to Lorraine` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 13 ended. Turn 14 begins!
- enemy phase: 7 actions, 6 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Murat. Casualties: Archduke Ch… · Mack's forces advance steadily. Brutal stalemate between Mack and Ney. Heavy casualties on both sides: Mack 3,838, Ney'… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Bernadotte. Casualties:… · Mack delivers an effective strike. Brutal stalemate between Mack and Ney. Heavy casualties on both sides: Mack 2,095, N…
  - 🏴 Austria: Casualties: Archduke Charles 1,082, Murat's army 5,156. Both armies remain in the field. Franconia has been captured by Austria!
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Munich!
  - ⚔ Archduke Charles (lost 1082) vs Murat (lost 3011, own corps) — Lannes and Napoleon arrived to reinforce Murat, but Soult and Deroy failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
  - ⚔ Mack (lost 3838) vs Ney (lost 813, own corps) — Davout reached the field beside Ney, Sire — it saved the line, no more.
  - ⚔ Archduke Charles (lost 151) vs Bernadotte (lost 2477) — The hills were ours, but Archduke Charles took them. Bernadotte's position was overrun. And Bernadotte was taken on tha…
  - ⚔ Mack (lost 2095) vs Ney (lost 1124, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Castanos (lost 549) vs Wellesley (lost 244, own corps) — Paget reached the field beside Wellesley, Sire — it saved the line, no more.
  - ⚔ Castanos (lost 404) vs Paget (lost 1111) — Paget's aggressive posture left the troops exposed when Castanos's attack came.
  - verbs: attack×6, move×1
- ORDER Davout [active]: Davout is marching to Bohemia (0 turns remaining).
- LEDGER treasury 17784 · net +736 · threat 83 · provinces 29 (+1) · ceiling 22701 · army 51073 · vassals Bavaria 96 · Holland 90 · Kingdom of Italy 92 · Switzerland 83
  - NET income 2627 · trade 537 · admin 50 · tribute 825 · upkeep 384 · charges 2361 · contributions 80 · occupation 52 · blockade 336 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 9
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 14 — Early April 1806
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Soult, move to Swabia` → ✓ Soult begins marching to Swabia (distance: 2). Moved to Tyrol. Route: Munich -> Swabia.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Napoleon, move to Orleanais` → ✓ Berthier: 'Enemy at Franconia. How shall I proceed, Sire?'
  - POPUP strategic_interrupt: Napoleon, contact, Berthier: 'Enemy at Franconia. How shall I proceed, Sire?' → attack
  - ↳ Napoleon attacks ArchdukeCharles. MUSTER — Napoleon (3,135; expect about 7,169 with the corps likely to arrive, up to 7,612 if all march) vs Archduke Charles (29,510 men) at Franconia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 1222, own corps) vs Archduke Charles (lost 324) — Reinforcements from Ney bolstered Napoleon's position — though Soult and Deroy never arrived, Sire.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 7 actions, 4 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Mack flanks from Hungary while allies attack from Franconia! (+1 coordination) · Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 154, Paget … · Castanos's forces press forward aggressively. Castanos gains the advantage over Wellesley. Casualties: Castanos 87, Wel…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Deroy is taken by Austria at Bohemia!
  - ⚔ Archduke Charles (lost 524) vs Ney (lost 2279, own corps) — Soult failed to arrive in time. Ney's army fought without expected support.
  - ⚔ Mack (lost 45) vs Napoleon (lost 521) — Not one corps reached Napoleon. Soult was expected; Napoleon fought the battle single-handed.
  - ⚔ Castanos (lost 154) vs Paget (lost 874) — A grievous defeat for Paget, Sire. The losses are severe.
  - ⚔ Castanos (lost 87) vs Wellesley (lost 360) — The line gave way. Wellesley is falling back, and not in good order.
  - verbs: attack×4, move×2, stance_change×1
- ORDER Soult [active]: Soult is marching to Swabia (2 turns remaining).
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Bohemia — 813 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Bohemia — 813 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 18286 · net +380 · threat 81 · provinces 29 (+0) · ceiling 20396 · army 35903 · vassals Bavaria 92 · Holland 84 · Kingdom of Italy 87 · Switzerland 76
  - NET income 2627 · trade 537 · admin 50 · tribute 832 · upkeep 264 · charges 2924 · occupation 52 · blockade 336 · admiralty 90
- DISPATCH: Sire — Marshal Deroy has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 11
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 15 — Late April 1806
  - MAILBOX #15 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (76 → 86); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Bernadotte, move to Hanover` → ✗ Marshal Bernadotte is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Napoleon, move to Paris` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Murat, move to Paris` → ✓ Murat begins marching to Paris (distance: 5). Moved to Milan. Route: Milan -> Piedmont -> Lyonnais -> Limousin -> Paris.
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 7 actions, 5 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Bohemia where he stands! Captured: Bavaria → Austria · Mack engages in solid combat. Brutal stalemate between Mack and Ney. Heavy casualties on both sides: Mack 2,464, Ney's … · Archduke Charles's forces advance steadily. Brutal stalemate between Archduke Charles and Davout. Heavy casualties on b… · Castanos's forces advance steadily. Castanos gains the advantage over Paget. Casualties: Castanos 32, Paget 373. Both a…
  - 🏴 Austria: ArchdukeCharles takes Bohemia where he stands! Captured: Bavaria → Austria
  - 🏴 Spain: [!] MARSHAL CAPTURED — Paget is taken by Spain at Aragon!
  - ⚔ Mack (lost 2464) vs Ney (lost 310, own corps) — Stalemate. Ney and Mack glare at each other across the field.
  - ⚔ Archduke Charles (lost 1390, own corps) vs Davout (lost 1525, own corps) — Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty.
  - ⚔ Castanos (lost 32) vs Paget (lost 373) — The line gave way. Paget is falling back, and not in good order. And Paget was taken on that field — Spain holds him.
  - ⚔ Castanos (lost 37) vs Wellesley (lost 208) — Wellesley was driven from the field. His men are scattered.
  - verbs: attack×5, move×1, fortify×1
- ORDER Murat [active]: Murat is marching to Paris (3 turns remaining).
- ORDER Soult [continues]: Soult marches to Munich. 1 region to Swabia.
- ORDER Ney [awaiting_response]: Ney is cornered at Tyrol with 1,608 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Tyrol with 1,608 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 2 · Britain armistice losing · Russia armistice losing
- LEDGER treasury 17830 · net -220 · threat 79 · provinces 29 (+0) · ceiling 16804 · army 29105 · vassals Bavaria 96 · Holland 84 · Kingdom of Italy 90 · Switzerland 86
  - NET income 2613 · trade 537 · admin 50 · tribute 613 · upkeep 224 · charges 3406 · requisitions 75 · occupation 52 · blockade 336 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (400g/turn)
  - LOG ai_ai_proposal_refused: Holland and Kingdom of Italy rebuff Austria (non-aggression pact)

## Turn 16 — Early May 1806
  - MAILBOX #16 Britain incoming_proposal: Britain — Armistice → activated
  - MAILBOX #17 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Britain, armistice_losing #21 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Russia. Your earlier answer was not delivered; the mat…
  - POPUP diplomatic_dialogue: incoming_proposal #22 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
  - POPUP diplomatic_dialogue: Britain, armistice_losing #21 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Armistice with Britain. → display-only
  - POPUP diplomatic_dialogue: Russia, armistice_losing #22 → accept
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Napoleon, recruit infantry` → ✗ Marshal Napoleon is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, move to Paris` → ✗ Marshal Massena is lost to us, Sire — his corps was destroyed at Milan. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Munich. Sharpen today, strike tomorrow — bonus ready turn 17, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 actions unused) Turn 17 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Davout. Casualties: Archduk… · ArchdukeJohn holds them at Tyrol while allies attack from Bohemia! (+1 coordination) · Mack flanks from Bohemia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 1009, own corps) vs Davout (lost 1755, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Archduke John (lost 622, own corps) vs Davout (lost 1331, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Mack (lost 979, own corps) vs Davout (lost 1725) — Stalemate. Davout and Mack glare at each other across the field.
  - verbs: attack×3, fortify×1
- ENVOYS WAITING 2 · Austria peace · Holland client petition
- LEDGER treasury 18054 · net +362 · threat 77 · provinces 29 (+0) · ceiling 19931 · army 23135 · vassals Bavaria 98 · Holland 80 · Kingdom of Italy 89 · Switzerland 84
  - NET income 2585 · trade 537 · admin 50 · tribute 619 · upkeep 176 · charges 3088 · occupation 75 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Britain: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL +1 more
  - TURN EVENTS 7
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And Britain stirs at its own design.
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy, blockade_broken ×2)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG ai_ai_proposal_refused: 7 courts rebuff Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 17 — Late May 1806
  - MAILBOX #18 Austria incoming_proposal: Austria — Peace Treaty → activated
  - MAILBOX #19 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, peace #23 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #24 → grant the petition
  - POPUP diplomatic_dialogue: Austria, peace #23 → accept
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (80 → 90); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - RATIFIED Austria · PEACE · stalemate
  - POPUP diplomatic_dialogue: Holland, client_petition #24 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2, fortify×1, drill×1
- LEDGER treasury 17686 · net +2123 · threat 76 · provinces 29 (+0) · ceiling 51919 · army 42535 · vassals Bavaria 100 · Holland 89 · Kingdom of Italy 88 · Switzerland 84
  - NET income 2586 · trade 549 · admin 50 · tribute 289 · upkeep 304 · charges 972 · occupation 75
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +3% this morning; the courts have begun to notice that he can be beaten.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - TURN EVENTS 7
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +4 medium/low (status_quo_titled, diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout demands to be heard → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 19819 · net +2151 · threat 75 · provinces 29 (+0) · ceiling 54500 · army 41955 · vassals Bavaria 100 · Holland 88 · Kingdom of Italy 87 · Switzerland 84
  - NET income 2588 · trade 549 · admin 50 · tribute 447 · upkeep 304 · charges 1104 · occupation 75
- DISPATCH: Sire — the establishment stands 90,545 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, drill×1, wait×1
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 22023 · net +2067 · threat 74 · provinces 29 (+0) · ceiling 55354 · army 41391 · vassals Bavaria 100 · Holland 87 · Kingdom of Italy 86 · Switzerland 84
  - NET income 2612 · trade 549 · admin 50 · tribute 453 · upkeep 304 · charges 1241 · occupation 52
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 91,109 men at Paris, and nobody has gone to collect them.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 20 — Early July 1806
  - MAILBOX #20 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #25 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to Bavaria. Loyalty +0 (100 → 100, already full); bond 59 → 59 (+2 a turn). Cost: 1 DP. Our net rises by 46g a turn — 22g of income forfeited, 52g of occupation relieved, 16g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
  - saved `sf4-q0-gev-b-nodoc_t20` → Game saved: sf4-q0-gev-b-nodoc_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 23846 · net +1653 · threat 73 · provinces 28 (-1) · ceiling 52136 · army 40847 · vassals Bavaria 100 · Holland 86 · Kingdom of Italy 85 · Switzerland 84
  - NET income 2590 · trade 549 · admin 50 · tribute 477 · upkeep 304 · charges 1275 · blockade 344 · admiralty 90
- DISPATCH: Sire — the levy has stood open 4 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between Britain and France has collapsed. War resumes!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
  - TURN EVENTS 3
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as an ultimatum.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, blockade_begins ×2)

## Turn 21 — Late July 1806
  - MAILBOX #21 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #26 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (85 → 95); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- LEDGER treasury 25205 · net +1205 · threat 72 · provinces 27 (-1) · ceiling 44759 · army 40319 · vassals Bavaria 100 · Holland 87 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2440 · trade 549 · admin 50 · tribute 333 · upkeep 304 · charges 1429 · blockade 344 · admiralty 90
- DISPATCH: Sire — Corsica has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - RAIL expedition_landed: THE LANDING: Wellesley has put 10,645 men ashore at Corsica.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG british_subsidy: Britain's gold: 400g reaches Russia

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 26414 · net +1281 · threat 71 · provinces 27 (+0) · ceiling 46182 · army 39807 · vassals Bavaria 100 · Holland 88 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2440 · trade 549 · admin 50 · tribute 562 · upkeep 304 · charges 1582 · blockade 344 · admiralty 90
- DISPATCH: Sire — Corsica lies in enemy hands. Britain holds it.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 27589 · net +1017 · threat 70 · provinces 26 (-1) · ceiling 42544 · army 39307 · vassals Bavaria 100 · Holland 89 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 606 · upkeep 304 · charges 1740 · blockade 344 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Provence.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 28644 · net +1235 · threat 69 · provinces 26 (+0) · ceiling 45988 · army 38823 · vassals Bavaria 100 · Holland 90 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 949 · upkeep 272 · charges 1897 · blockade 344 · admiralty 90
- DISPATCH: Sire — Corsica and Provence lie in enemy hands. Britain holds them.
  - TURN EVENTS 2
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 29885 · net +1064 · threat 68 · provinces 26 (+0) · ceiling 44177 · army 38355 · vassals Bavaria 100 · Holland 91 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 955 · upkeep 272 · charges 2074 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 8 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 26 — Early October 1806
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 30955 · net +898 · threat 66 · provinces 26 (+0) · ceiling 42515 · army 37899 · vassals Bavaria 100 · Holland 92 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 961 · upkeep 272 · charges 2246 · blockade 344 · admiralty 90
- DISPATCH: Sire — 3 turns now with Corsica and Provence in enemy hands. The country counts every one of them.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 31855 · net +734 · threat 64 · provinces 26 (+0) · ceiling 40935 · army 37459 · vassals Bavaria 100 · Holland 93 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 963 · upkeep 272 · charges 2412 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)

## Turn 28 — Early November 1806
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 32613 · net +749 · threat 62 · provinces 26 (+0) · ceiling 41523 · army 37031 · vassals Bavaria 100 · Holland 94 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 1137 · upkeep 272 · charges 2571 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 33364 · net +588 · threat 60 · provinces 26 (+0) · ceiling 40096 · army 36615 · vassals Bavaria 100 · Holland 95 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 1139 · upkeep 272 · charges 2734 · blockade 344 · admiralty 90
- DISPATCH: Sire — the enemy has held Corsica and Provence 6 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 30 — Early December 1806
  - saved `sf4-q0-gev-b-nodoc_t30` → Game saved: sf4-q0-gev-b-nodoc_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 33954 · net +436 · threat 58 · provinces 26 (+0) · ceiling 38769 · army 36211 · vassals Bavaria 100 · Holland 96 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 1141 · upkeep 272 · charges 2888 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 34393 · net +296 · threat 56 · provinces 26 (+0) · ceiling 37544 · army 35819 · vassals Bavaria 100 · Holland 97 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 1144 · upkeep 272 · charges 3031 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 32 — Early January 1807
  - MAILBOX #22 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #27 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 34691 · net +165 · threat 54 · provinces 26 (+0) · ceiling 36390 · army 35439 · vassals Bavaria 100 · Holland 98 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 1146 · upkeep 272 · charges 3164 · blockade 344 · admiralty 90
- DISPATCH: Sire — the enemy has held Corsica and Provence 9 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 34890 · net +74 · threat 52 · provinces 26 (+0) · ceiling 35630 · army 35071 · vassals Bavaria 100 · Holland 99 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 549 · admin 50 · tribute 1148 · upkeep 240 · charges 3289 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 34948 · net -53 · threat 50 · provinces 26 (+0) · ceiling 34432 · army 34715 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 499 · admin 50 · tribute 1150 · upkeep 240 · charges 3400 · blockade 312 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 34898 · net -150 · threat 48 · provinces 26 (+0) · ceiling 33484 · army 34371 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 499 · admin 50 · tribute 1153 · upkeep 240 · charges 3500 · blockade 312 · admiralty 90
- DISPATCH: Sire — the enemy has held Corsica and Provence 12 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 36 — Early March 1807
  - MAILBOX #23 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #28 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 34750 · net -237 · threat 46 · provinces 26 (+0) · ceiling 32583 · army 34035 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 499 · admin 50 · tribute 1155 · upkeep 240 · charges 3589 · blockade 312 · admiralty 90
- DISPATCH: Sire — a truce with Russia is signed. The fighting stops for 5 turns; peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)

## Turn 37 — Late March 1807
  - MAILBOX #24 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #29 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 34515 · net -313 · threat 44 · provinces 26 (+0) · ceiling 31734 · army 33711 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 499 · admin 50 · tribute 1157 · upkeep 240 · charges 3667 · blockade 312 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)

## Turn 38 — Early April 1807
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 34204 · net -379 · threat 42 · provinces 26 (+0) · ceiling 30931 · army 33395 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 499 · admin 50 · tribute 1159 · upkeep 240 · charges 3735 · blockade 312 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 39 — Late April 1807
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 33828 · net -434 · threat 40 · provinces 26 (+0) · ceiling 30179 · army 33091 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 499 · admin 50 · tribute 1162 · upkeep 240 · charges 3793 · blockade 312 · admiralty 90
- DISPATCH: Sire — the enemy has held Corsica and Provence 16 turns. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)

## Turn 40 — Early May 1807
  - saved `sf4-q0-gev-b-nodoc_t40` → Game saved: sf4-q0-gev-b-nodoc_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
  - POPUP redemption: Deroy, 20 → grant_autonomy
  -     ↳ Deroy has been granted autonomy. They will act independently for 3 turns, using their own judgment in battle.
- LEDGER treasury 33398 · net -480 · threat 24 · provinces 26 (+0) · ceiling 29475 · army 32795 · vassals Bavaria 100 · Holland 100 · Kingdom of Italy 95 · Switzerland 84
  - NET income 2290 · trade 511 · admin 50 · tribute 1162 · upkeep 240 · charges 3843 · blockade 320 · admiralty 90
- DISPATCH: Sire — Marshal Deroy's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armistice_expired_peace: The armistice between France and Russia has concluded. Peace declared.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_coalition_dissolved, agenda_shift)
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 40 to 20; Britain remains at war with us.

---
finished: **completed** · commands 109 · popups 70 · battles 36
