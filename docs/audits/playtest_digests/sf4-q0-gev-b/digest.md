# Playtest digest — sf4-q0-gev-b

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "client_petition": "grant"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `e631f4bd4a79` (dirty) · content `c4151b82bd80` · driver `f7650c682a9c`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `vassalize Bavaria` → ✓ Sire, regarding the Vassalage proposal to Bavaria, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #1 → confirm
  - POPUP proposal_result: Talleyrand departs for the Bavaria court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 85,373 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2294, own corps) vs Mack (lost 14577) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult and Bernadotte never arr… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Lannes, attack Mack` → ✓ MUSTER — Lannes (16,711; expect about 106,366 with the corps likely to arrive) vs Mack (37,423 men) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 858, own corps) vs Mack (lost 27821) — Soult and Bernadotte never reached the guns. The battle was decided without them, Sire.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,758; expect about 82,273 with the corps likely to arrive, up to 85,131 if all march) vs Mack (strength unknown) at Munich — the balance of force look…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 74, own corps) vs Mack (lost 8332) — Reinforcements! Ney and Massena marched onto the field beside Davout. The enemy's advantage melted away. And Mack was t… — Berthier: the corps marched apart and arrived together.
- CMD `Murat, move to Swabia` → ✗ Murat is already in Swabia.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 1 action unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Bernadotte. Casualties: Archduke Ch…
  - ⚔ Archduke Charles (lost 1566) vs Bernadotte (lost 7455) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 4 · Bavaria vassalage · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1712 · net +1762 · threat 87 · provinces 28 · ceiling 37240 · army 164192 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 350 · admin 50 · tribute 937 · upkeep 1856 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Bavaria with a response.
  - TURN EVENTS 2
- DIPLO +9 medium/low (diplomatic_proposal_sent, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #4 Bavaria counter_offer_response: Bavaria — Vassalage → activated
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Bavaria, vassalage #5 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Prussia. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #2 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
  - POPUP diplomatic_dialogue: Bavaria, vassalage #5 → accept
  - POPUP proposal_result: You have accepted Bavaria's counter-proposal. Treaty signed: Alliance → Vassal with Bavaria. → display-only
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → accept
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Ney, move to Munich` → ✗ Ney is already in Munich.
- CMD `Davout, move to Munich` → ✗ Davout is already in Munich.
- CMD `Lannes, move to Munich` → ✓ Lannes moves from Swabia to Munich (307 lost to march)
- CMD `Murat, move to Munich` → ✓ Murat moves from Swabia to Munich (441 lost to march)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - verbs: attack×1, form_square×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 3510 · net +1658 · threat 90 · provinces 28 (+0) · ceiling 34669 · army 176003 · vassals Bavaria 64 · Holland 100 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 350 · admin 50 · tribute 1273 · upkeep 2216 · charges 80 · blockade 219 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +8 medium/low (diplomatic_treaty_signed ×4, diplomatic_carved_vassal_created, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 15 approaches from Prussia and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia (open borders agreement)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, ma…
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (900 lost to march)
- CMD `Massena, move to Piedmont` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 5216 · net +1527 · threat 78 · provinces 28 (+0) · ceiling 32283 · army 166485 · vassals Bavaria 68 · Holland 100 · Switzerland 95
  - NET income 2590 · trade 449 · admin 50 · tribute 906 · upkeep 1916 · charges 181 · blockade 281 · admiralty 90
- DISPATCH: Sire — Kingdom of Italy is no longer ours. Conquered — the satellite is gone.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG ai_ai_proposal_refused: 7 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Soult, move to Munich` → ✓ Soult moves from Swabia to Munich (1,542 lost to march)
- CMD `Bernadotte, move to Munich` → ✓ Bernadotte moves from Swabia to Munich (180 lost to march)
- CMD `Deroy, move to Munich` → ✗ Deroy is already in Munich.
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Jo…
  - POPUP objection: Massena, Massena firmly objects: 'Sire, we have the advantage. Let me strike!' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Tyrol instead.) → insist
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Piedmont into Provence unopposed! (1,271 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Piedmont into Provence unopposed! (1,271 lost to march) Captured: France → Austria
  - verbs: attack×1
- LEDGER treasury 7057 · net +1622 · threat 76 · provinces 27 (-1) · ceiling 34265 · army 155399 · vassals Bavaria 72 · Holland 100 · Switzerland 93
  - NET income 2440 · trade 524 · admin 50 · tribute 913 · upkeep 1586 · charges 301 · blockade 328 · admiralty 90
- DISPATCH: Sire — Provence has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia (open borders agreement)
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 5 — Late November 1805
- CMD `vassalize Hesse` → ✓ Sire, regarding the Vassalage proposal to Hesse, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #10 → confirm
  - POPUP proposal_result: Talleyrand departs for the Hesse court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `vassalize Saxony` → ✓ Sire, regarding the Vassalage proposal to Saxony, I have prepared terms that reflect the current diplomatic climate.
  - POPUP diplomatic_dialogue: proposal_confirm #11 → confirm
  - POPUP proposal_result: Talleyrand departs for the Saxony court with your Vassalage proposal. Expect a response by next turn. (3 DP spent) → display-only
- CMD `declare war on Hanover` → ✗ Talleyrand is currently en route to a foreign court. He cannot negotiate until he returns.
- CMD `Soult, move to Franconia` → ✓ Soult moves from Munich to Franconia. Franconia falls to France! (was Austria) (525 lost to march)
  - POPUP capture_choice[capture]: Franconia, Soult → secure
- CMD `Bernadotte, move to Franconia` → ✓ Bernadotte moves from Munich to Franconia (83 lost to march)
- CMD `Ney, move to Franconia` → ✓ Ney moves from Munich to Franconia (160 lost to march)
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Munich to Franconia (125 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Provence into Lyonnais unopposed! (1,233 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Provence into Lyonnais unopposed! (1,233 lost to march) Captured: France → Austria
  - verbs: attack×1
  - POPUP proposal_result: Saxony has rejected our Vassalage. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 8628 · net +1409 · threat 76 · provinces 27 (+0) · ceiling 23810 · army 148523 · vassals Bavaria 76 · Holland 100 · Switzerland 91
  - NET income 2404 · trade 524 · admin 50 · tribute 922 · upkeep 1388 · charges 615 · occupation 70 · blockade 328 · admiralty 90
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_proposal_returned: Talleyrand returns from Saxony with a response.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 6 in hand); or let the w…
  - TURN EVENTS 6
- DIPLO +5 medium/low (diplomatic_proposal_sent ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Austria, Naples and Denmark rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 6 — Early December 1805
  - MAILBOX #9 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #13 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Soult, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Bernadotte, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Ney, attack Archduke John` → ✗ No intelligence on Archduke John's position, Sire. Scout for him before Ney can give chase.
- CMD `Deroy, move to Franconia` → ✓ Deroy moves from Munich to Franconia (163 lost to march)
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Lyonnais into Limousin unopposed! (1,106 lost to march) Captured: France → Austria · ArchdukeCharles assaults the Paris garrison! Garrison: 25,000 -> 13,735 (-11,265). ArchdukeCharles loses 6,944 troops. … · ArchdukeCharles assaults the Paris garrison! Garrison: 13,735 -> 6,868 (-6,867). ArchdukeCharles loses 4,239 troops. Ga…
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Limousin unopposed! (1,106 lost to march) Captured: France → Austria
  - verbs: attack×3
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 8808 · net +953 · threat 73 · provinces 26 (-1) · ceiling 17823 · army 143080 · vassals Bavaria 80 · Holland 100 · Switzerland 99
  - NET income 2234 · trade 524 · admin 50 · tribute 699 · upkeep 1238 · charges 718 · contributions 110 · occupation 70 · blockade 328 · admiralty 90
- DISPATCH: Sire — Limousin has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, balance_of_europe_shifted, coercive_demand)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
  - MAILBOX #10 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #14 → grant the petition
  - POPUP proposal_result: Franconia is ceded to Bavaria. Loyalty +11 (80 → 91); bond 59 → 59 (+2 a turn). Cost: 1 DP. Our net rises by 50g a turn — 46g of income forfeited, 70g of occupation relieved, 34g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, move to Osnabruck` → ✗ Cannot enter Osnabruck — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Munich to Franconia (152 lost to march)
- CMD `Lannes, attack Archduke John` → ✗ No intelligence on Archduke John's position, Sire. Scout for him before Lannes can give chase.
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 3 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Paris garrison! Garrison collapses (8,868 -> 0). ArchdukeCharles loses 2,463 troops in the… · ArchdukeCharles assaults the Normandy garrison! Garrison collapses (6,000 -> 0). ArchdukeCharles loses 2,083 troops in … · ArchdukeCharles marches from Normandy into Berry unopposed! (158 lost to march) Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -123g, France -221g. Captured: France → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -104g, France -150g. Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Normandy into Berry unopposed! (158 lost to march) Captured: France → Austria
  - verbs: attack×3
- LEDGER treasury 9077 · net +819 · threat 70 · provinces 22 (-4) · ceiling 16595 · army 137312 · vassals Bavaria 95 · Holland 100 · Switzerland 98
  - NET income 1840 · trade 524 · admin 50 · tribute 736 · upkeep 1144 · charges 769 · blockade 328 · admiralty 90
- DISPATCH: Sire — Paris HAS FALLEN. Our capital is in Austria's hands, and every courier in Europe is already carrying the news.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +7 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×3, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 8 — Early January 1806
- CMD `Lannes, retreat` → ✗ Lannes is not in danger. No retreat necessary.
- CMD `Massena, attack Archduke John` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Soult, move to Brunswick` → ✗ Cannot enter Brunswick — it is controlled by Hanover (diplomatic state: PEACE). Open borders or higher required.
- CMD `Napoleon, move to Franconia` → ✓ Napoleon moves from Swabia to Franconia (86 lost to march)
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 9 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore engages in solid combat. Moore gains the advantage over Castanos. Casualties: Moore's army 1,457, Castanos 3,017.… · Paget holds them at Normandy while allies attack from London! (+1 coordination) · ArchdukeCharles marches from Berry into Gascony unopposed! (314 lost to march) Captured: France → Austria · ArchdukeCharles marches from Gascony into Guyenne unopposed! (153 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Berry into Gascony unopposed! (314 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Gascony into Guyenne unopposed! (153 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles moves from Guyenne to Anjou. Anjou falls to Austria!
  - ⚔ Moore (lost 1337, own corps) vs Castanos (lost 3017) — The walls were not enough. Moore broke through Castanos's prepared defenses.
  - ⚔ Paget (lost 213, own corps) vs Castanos (lost 5510) — The walls were not enough. Paget broke through Castanos's prepared defenses.
  - verbs: attack×4, move×3, unfortify×2
- LEDGER treasury 9669 · net +503 · threat 67 · provinces 19 (-3) · ceiling 14151 · army 131142 · vassals Bavaria 99 · Holland 100 · Switzerland 97
  - NET income 1510 · trade 524 · admin 50 · tribute 811 · upkeep 1116 · charges 858 · blockade 328 · admiralty 90
- DISPATCH: Sire — Gascony has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing …
  - TURN EVENTS 6
- DIPLO +4 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 9 — Late January 1806
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, attack Hanover` → ✗ Bernadotte cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Massena, move to Milan` → ✗ Massena is fortified at Munich and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Ney, move to Franconia` → ✗ Ney is already in Franconia.
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore executes a brilliant maneuver! Moore gains the advantage over Castanos. Casualties: Moore's army 172, Castanos 2,… · Paget attacks with overwhelming force. Paget decisively defeats Castanos! Castanos's army is destroyed. Paget's army su…
  - 🏴 Britain: Both armies remain in the field. Moore advances into Maine. (594 lost to march) Maine has been captured by Britain!
  - 🏴 Britain: Castanos's army is destroyed! Paget advances into Brittany. (40 lost to march) Brittany has been captured by Britain!
  - ⚔ Moore (lost 141, own corps) vs Castanos (lost 2714) — Even Castanos's fortifications could not hold, Sire. Moore overran the position.
  - ⚔ Paget (lost 13, own corps) vs Castanos (lost 2838) — The terrain heavily favored Paget. Castanos's men paid the price.
  - verbs: attack×2, move×1, garrison×1
- LEDGER treasury 9847 · net +127 · threat 64 · provinces 17 (-2) · ceiling 10719 · army 125407 · vassals Bavaria 100 · Holland 100 · Switzerland 96
  - NET income 1350 · trade 524 · admin 50 · tribute 816 · upkeep 1056 · charges 1139 · blockade 328 · admiralty 90
- DISPATCH: Sire — Maine has fallen to Britain. Enemy colours fly over French homeland soil. Paget's corps of 4,055 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any g…
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 6 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `Soult, attack Hanover` → ✗ Soult cannot reach Hanover from Franconia! Range: 1, Distance: 3
- CMD `Bernadotte, move to Oldenburg` → ✓ Bernadotte begins marching to Oldenburg (distance: 4). Moved to Frankfurt. Route: Frankfurt -> Brunswick -> Hanover -> Oldenburg.
- CMD `Deroy, move to Franconia` → ✗ Deroy is already in Franconia.
- CMD `Lannes, move to Franconia` → ✗ Lannes is already in Franconia.
  - saved `sf4-q0-gev-b_t10` → Game saved: sf4-q0-gev-b_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 1 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Limousin into Languedoc unopposed! (147 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Limousin into Languedoc unopposed! (147 lost to march) Captured: France → Austria
  - verbs: fortify×2, attack×1
- ORDER Bernadotte [active]: Bernadotte is marching to Oldenburg (4 turns remaining).
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 9593 · net -234 · threat 61 · provinces 16 (-1) · ceiling 8278 · army 120797 · vassals Bavaria 100 · Holland 100 · Switzerland 95
  - NET income 1270 · trade 524 · admin 50 · tribute 820 · upkeep 1016 · charges 1354 · contributions 110 · blockade 328 · admiralty 90
- DISPATCH: Sire — Languedoc has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standin…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Asking 3627 gold.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 4
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 11 — Late February 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → reject_settlement_offer
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Deroy, move to Bohemia` → ✓ Deroy moves from Franconia to Bohemia. Bohemia falls to France! (was Austria) (122 lost to march)
  - POPUP capture_choice[capture]: Bohemia, Deroy → secure
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, move to Franconia` → ✗ Soult is already in Franconia.
- CMD `Napoleon, move to Swabia` → ✓ Napoleon moves from Franconia to Swabia (71 lost to march)
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks with overwhelming force. Deroy holds the line. Casualties: Archduke John 5,032, Deroy's army 1,40…
  - ⚔ Archduke John (lost 5032) vs Deroy (lost 536, own corps) — Reinforcements from Ney, Lannes and Murat bolstered Deroy's position — though Soult never arrived, Sire.
  - verbs: attack×1
- ORDER Bernadotte : Bernadotte: 'Cannon fire at Bohemia, Sire. Investigate?'
  - POPUP strategic_interrupt: Bernadotte, cannon_fire, Bernadotte: 'Cannon fire at Bohemia, Sire. Investigate?' → investigate
- ENVOYS WAITING 1 · Naples open borders
- LEDGER treasury 9246 · net -250 · threat 60 · provinces 17 (+1) · ceiling 7871 · army 117278 · vassals Bavaria 100 · Holland 100 · Switzerland 95
  - NET income 1270 · trade 524 · admin 50 · tribute 823 · upkeep 968 · charges 1321 · contributions 110 · occupation 100 · blockade 328 · admiralty 90
- DISPATCH: Sire — Paris, Anjou and Berry and 9 more lie in enemy hands — the capital among them. Austria and Britain hold them.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
- CMD `invest in Saxony` → ✗ Saxony is not a vassal.
- CMD `Soult, move to Bohemia` → ✓ Soult moves from Franconia to Bohemia (181 lost to march)
- CMD `Davout, move to Tyrol` → ✓ Davout moves from Munich to Tyrol. Tyrol falls to France! (was Austria) (308 lost to march)
  - POPUP capture_choice[capture]: Tyrol, Davout → secure
- CMD `Massena, move to Swabia` → ✗ Massena is fortified at Munich and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Bohemia to Franconia (112 lost to march)
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Lyonnais into Savoy unopposed! (465 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Lyonnais into Savoy unopposed! (465 lost to march) Captured: France → Austria
  - verbs: attack×1
- LEDGER treasury 9135 · net -236 · threat 59 · provinces 17 (+0) · ceiling 7862 · army 115217 · vassals Bavaria 100 · Holland 100 · Switzerland 94
  - NET income 1274 · trade 549 · admin 50 · tribute 825 · upkeep 944 · charges 1324 · contributions 110 · occupation 122 · blockade 344 · admiralty 90
- DISPATCH: Sire — Savoy has fallen to Austria. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing th…
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
- CMD `Soult, attack Vienna` → ✓ MUSTER — Soult (17,441; expect about 29,574 with the corps likely to arrive, up to 29,961 if all march) vs Archduke John (small force) at Vienna — the balance of force l…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 972, own corps) vs Archduke John (lost 3852, own corps) — Ney and Lannes arrived to reinforce Soult, but Deroy failed to reach the field in time. — The corps system brought Ney in.
- CMD `Deroy, attack Vienna` → ✓ MUSTER — Deroy (10,888; expect about 27,137 with the corps likely to arrive) vs Hiller (4,229 men) at Vienna — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Deroy (lost 192, own corps) vs Hiller (lost 2591) — Soult failed to arrive in time. Deroy's army fought without expected support. And Hiller was taken on that field — Fran…
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Tyrol to Bohemia (151 lost to march)
- CMD `Napoleon, move to Lorraine` → ✓ Napoleon moves from Swabia to Lorraine
- CMD `end turn` → ✓ Turn 13 ended. Turn 14 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, fortify×1, recruit×1
- LEDGER treasury 9140 · net +282 · threat 62 · provinces 17 (+0) · ceiling 10900 · army 113253 · vassals Bavaria 100 · Holland 100 · Switzerland 95
  - NET income 1275 · trade 549 · admin 50 · tribute 1053 · upkeep 912 · charges 1142 · contributions 110 · requisitions 75 · occupation 122 · blockade 344 · admiralty 90
- DISPATCH: Sire — General Hiller of Austria is taken at Vienna — he is our prisoner, and their order of battle is one commander shorter.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 14 — Early April 1806
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Soult, move to Swabia` → ✓ Soult begins marching to Swabia (distance: 2). Moved to Franconia. Route: Franconia -> Swabia.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortif…
- CMD `Napoleon, move to Orleanais` → ✓ Napoleon moves from Lorraine to Orleanais
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 3 actions, 1 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Normandy into Artois unopposed! (192 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore marches from Normandy into Artois unopposed! (192 lost to march) Captured: France → Britain
  - 🏴 Britain: Moore moves from Artois to Champagne. Champagne falls to Britain!
  - 🏴 Britain: Moore moves from Champagne to Burgundy. Burgundy falls to Britain!
  - verbs: move×2, attack×1
- ORDER Soult [active]: Soult is marching to Swabia (2 turns remaining).
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 9227 · net +47 · threat 59 · provinces 14 (-3) · ceiling 9468 · army 113089 · vassals Bavaria 100 · Holland 100 · Switzerland 94
  - NET income 1184 · trade 549 · admin 50 · tribute 1055 · upkeep 944 · charges 1396 · requisitions 75 · occupation 92 · blockade 344 · admiralty 90
- DISPATCH: Sire — Artois has fallen to Britain. Enemy colours fly over French homeland soil. Wellesley's corps of ~2,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does…
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Britain and Spain have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes on…
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +6 medium/low (law_enacted_abroad, doctrine_cured_abroad, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_expired: The compact between Russia and Britain lapses

## Turn 15 — Late April 1806
  - MAILBOX #13 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #19 → grant the petition
  - POPUP proposal_result: Bohemia is ceded to Bavaria. Loyalty +0 (100 → 100, already full); bond 59 → 59 (+2 a turn). Cost: 1 DP. Our net falls by 5g a turn — 147g of income forfeited, 40g of occupation relieved, 110g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Bernadotte, move to Hanover` → ✓ Bernadotte begins marching to Hanover (distance: 3). Moved to Frankfurt. Route: Frankfurt -> Brunswick -> Hanover.
- CMD `Napoleon, move to Paris` → ✓ Berthier: 'Enemy at Burgundy. How shall I proceed, Sire?'
  - POPUP strategic_interrupt: Napoleon, contact, Berthier: 'Enemy at Burgundy. How shall I proceed, Sire?' → attack
  - ↳ Napoleon attacks Moore. MUSTER — Napoleon (7,067) vs Moore (substantial force) at Burgundy — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Napoleon (lost 2748) vs Moore (lost 501) — The toll on Napoleon's forces is heavy, Sire. This defeat will be felt. — The Line Holds +15% (Moore)
- CMD `Murat, move to Paris` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 1 action unused) Turn 16 begins!
- enemy phase: 7 actions, 4 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore marches from Burgundy into Orleanais unopposed! (181 lost to march) Captured: France → Britain · Wellesley's forces press forward aggressively. Wellesley gains the advantage over Napoleon. Casualties: Wellesley's arm… · Paget delivers an effective strike. Paget decisively defeats Napoleon! Napoleon's army is destroyed. Paget's army suffe… · Moore assaults the Flanders garrison! Garrison: 12,000 -> 6,000 (-6,000). Moore loses 3,052 troops. Garrison holds — 6,…
  - 🏴 Britain: Moore marches from Burgundy into Orleanais unopposed! (181 lost to march) Captured: France → Britain
  - 🏴 Britain: Both armies remain in the field. Wellesley advances into Picardy. (47 lost to march) Picardy has been captured by Britain!
  - 🏴 Britain: Paget advances into Ile-de-France. (38 lost to march) Ile-de-France has been captured by Britain!
  - ⚔ Wellesley (lost 13, own corps) vs Napoleon (lost 1418) — The toll on Napoleon's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Paget (lost 13, own corps) vs Napoleon (lost 1125) — The Emperor himself was taken on that field — Britain holds him.
  - verbs: attack×4, move×1, fortify×1, grant_dotation×1
- ORDER Bernadotte [active]: Bernadotte is marching to Hanover (3 turns remaining).
- ORDER Soult [completed]: As ordered: "move to Swabia". Soult arrives at Swabia. Soult stands ready for instruction.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
  - POPUP diplomatic_dialogue: Russia, armistice_losing #20 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
  - POPUP diplomatic_dialogue: Austria, armistice_losing #21 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +4 (92 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 3 · Russia armistice losing · Austria armistice losing · Holland client petition
- LEDGER treasury 8689 · net -412 · threat 56 · provinces 10 (-4) · ceiling 6666 · army 105797 · vassals Bavaria 96 · Holland 96 · Switzerland 85
  - NET income 865 · trade 549 · admin 50 · tribute 870 · upkeep 896 · charges 1364 · occupation 52 · blockade 344 · admiralty 90
- DISPATCH: Sire — the Emperor himself is TAKEN. Britain holds him, and the Empire holds its breath.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG third_party_peace: THE CONGRESS: Britain and Spain make peace without France

## Turn 16 — Early May 1806
- CMD `invest in Hesse` → ✗ Hesse is not a vassal.
- CMD `Napoleon, recruit infantry` → ✗ Marshal Napoleon is a prisoner of Britain, Sire — no order can reach him until his release.
- CMD `Massena, move to Paris` → ✗ Massena is fortified at Munich and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 17, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 actions unused) Turn 17 begins!
- enemy phase: 3 actions, 2 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Moore assaults the Flanders garrison! Garrison collapses (6,000 -> 0). Moore loses 1,634 troops in the assault. Moore m… · Moore marches from Brabant into Lorraine unopposed! (129 lost to march) Captured: France → Britain
  - 🏴 Britain: [Materiel] Guns, horses and stores lost with the fallen: Britain -81g, France -150g. Captured: France → Britain
  - 🏴 Britain: Moore marches from Brabant into Lorraine unopposed! (129 lost to march) Captured: France → Britain
  - verbs: attack×2, unfortify×1
- ORDER Bernadotte [continues]: Bernadotte marches to Brunswick. 1 region to Hanover.
- ORDER Lannes [continues]: Lannes marches to Bohemia. 1 region to Tyrol.
- ORDER Ney [continues]: Ney marches to Bohemia. 1 region to Tyrol.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Britain, peace #23 → accept
  - POPUP proposal_result: You have accepted Britain's proposal. Treaty signed: At War → Peace with Britain. → display-only
  - RATIFIED Britain · PEACE · enemy_victory
  - POPUP diplomatic_dialogue: Switzerland, client_petition #24 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (82 → 86); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 2 · Britain peace · Switzerland client petition
- LEDGER treasury 6662 · net +679 · threat 53 · provinces 8 (-2) · ceiling 18040 · army 109242 · vassals Bavaria 96 · Holland 95 · Switzerland 86
  - NET income 692 · trade 561 · admin 50 · tribute 647 · upkeep 964 · charges 277 · occupation 30
- DISPATCH: Sire — Flanders has fallen to Britain. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing…
  - RAIL balance_of_europe_shifted: Vienna System leads the current largest alignment at 50% of active European bloc power.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from Britain has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL +2 more
  - TURN EVENTS 10
- COURTS: The court of Austria eases over Revanche — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (defensive alliance)

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Bernadotte [completed]: Bernadotte arrives at Hanover. Bernadotte: "It is done. I took the liberty of posting pickets."
- ORDER Davout [error]: Davout could not advance toward Bearn.
- ORDER Deroy [continues]: Deroy marches to Tyrol. 6 regions to Bearn.
- ORDER Lannes [continues]: Lannes marches to Tyrol. 6 regions to Bearn.
- ORDER Massena [error]: Massena could not advance toward Bearn.
- ORDER Murat [continues]: Murat marches to Lorraine. 5 regions to Bearn.
- ORDER Ney [continues]: Ney marches to Tyrol. 6 regions to Bearn.
- ORDER Soult [continues]: Soult marches to Lorraine. 5 regions to Bearn.
- LEDGER treasury 7375 · net +670 · threat 50 · provinces 8 (+0) · ceiling 18610 · army 107157 · vassals Bavaria 96 · Holland 92 · Switzerland 84
  - NET income 692 · trade 561 · admin 50 · tribute 649 · upkeep 932 · charges 320 · occupation 30
- DISPATCH: Sire — the Emperor's star is out. The Presence that gave his corps +10% on the field gives nothing this morning — Europe has learned that Napoleon can be beaten.
  - RAIL peace_ratified: Peace ratified between Britain and France.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Austria eases over Revanche — service to the strong is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, coercive_demand, blockade_broken ×2)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Britain (defensive alliance)
  - LOG balance_of_europe_shifted: Vienna System leads the current largest alignment at 50% of active European bloc power.

## Turn 18 — Early June 1806
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- ORDER Bernadotte [continues]: Bernadotte marches to Oldenburg. 6 regions to Bearn.
- ORDER Davout [error]: Davout could not advance toward Bearn.
- ORDER Deroy [continues]: Deroy marches to Milan. 5 regions to Bearn.
- ORDER Lannes [continues]: Lannes marches to Milan. 5 regions to Bearn.
- ORDER Massena [error]: Massena could not advance toward Bearn.
- ORDER Murat [continues]: Murat marches to Burgundy. 3 regions to Bearn.
- ORDER Ney [continues]: Ney marches to Milan. 5 regions to Bearn.
- ORDER Soult [continues]: Soult marches to Orleanais. 4 regions to Bearn.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 8059 · net +643 · threat 47 · provinces 8 (+0) · ceiling 18845 · army 106355 · vassals Bavaria 96 · Holland 89 · Switzerland 82
  - NET income 692 · trade 561 · admin 50 · tribute 651 · upkeep 920 · charges 361 · occupation 30
- DISPATCH: Sire — Paris, Anjou and Artois and 18 more lie in enemy hands — the capital among them. Austria and Britain hold them.
  - RAIL diplomatic_offensive_cascade: Britain has joined Russia's war against Sweden, honoring their alliance.
  - RAIL diplomatic_offensive_cascade: Austria has joined Russia's war against Sweden, honoring their alliance.
  - TURN EVENTS 8
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_dp_regen, blockade_begins, agenda_shift, diplomatic_relation_shift)

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 4 actions, 0 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×3, unfortify×1
- ORDER Bernadotte [continues]: Bernadotte marches to Westphalia. 5 regions to Bearn.
- ORDER Davout [error]: Davout could not advance toward Bearn.
- ORDER Deroy [continues]: Deroy marches to Piedmont. 4 regions to Bearn.
- ORDER Lannes [continues]: Lannes marches to Piedmont. 4 regions to Bearn.
- ORDER Massena [error]: Massena could not advance toward Bearn.
- ORDER Murat [continues]: Murat marches to Gascony. 1 region to Bearn.
- ORDER Ney [continues]: Ney marches to Piedmont. 4 regions to Bearn.
- ORDER Soult [continues]: Soult marches to Burgundy. 3 regions to Bearn.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 8758 · net +658 · threat 44 · provinces 8 (+0) · ceiling 19785 · army 104654 · vassals Bavaria 96 · Holland 86 · Switzerland 80
  - NET income 692 · trade 561 · admin 50 · tribute 691 · upkeep 904 · charges 402 · occupation 30
- DISPATCH: Sire — Davout, Massena and Bernadotte are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
  - saved `sf4-q0-gev-b_t20` → Game saved: sf4-q0-gev-b_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ORDER Bernadotte [continues]: Bernadotte marches to Artois. 4 regions to Bearn.
- ORDER Davout [error]: Davout could not advance toward Bearn.
- ORDER Deroy [continues]: Deroy marches to Lyonnais. 3 regions to Bearn.
- ORDER Lannes [continues]: Lannes marches to Lyonnais. 3 regions to Bearn.
- ORDER Massena [error]: Massena could not advance toward Bearn.
- ORDER Murat [completed]: Murat arrives at Bearn. Murat: "It is done. Point me at something that shoots back, Sire."
- ORDER Ney [continues]: Ney marches to Lyonnais. 3 regions to Bearn.
- ORDER Soult [continues]: Soult marches to Limousin. 2 regions to Bearn.
- LEDGER treasury 9291 · net +465 · threat 41 · provinces 8 (+0) · ceiling 14697 · army 103191 · vassals Bavaria 96 · Holland 83 · Switzerland 78
  - NET income 730 · trade 561 · admin 50 · tribute 693 · upkeep 884 · charges 627 · requisitions 47 · occupation 15 · admiralty 90
- DISPATCH: Sire — under the peace with Britain. Bernadotte is on the wrong side of the frontier at Artois, Sire — the ground changed hands under him. Berthier has put him on the road home to Nivernais; he has 6…
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - TURN EVENTS 8
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as war.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: Britain rebuffs Russia (design ask)

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Davout. Casualties: Arc…
  - ⚔ Archduke Charles (lost 1306, own corps) vs Davout (lost 2776) — The walls were not enough. Archduke Charles broke through Davout's prepared defenses. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: move×2, attack×1
- ORDER Bernadotte [continues]: Bernadotte marches to Champagne. 2 regions to Nivernais.
- ORDER Davout [awaiting_response]: Davout: 'Enemy at Bohemia. How shall I proceed?'
- ORDER Deroy [continues]: Deroy marches to Limousin. 2 regions to Bearn.
- ORDER Lannes [continues]: Lannes marches to Limousin. 2 regions to Bearn.
- ORDER Massena [error]: Massena could not advance toward Bearn.
- ORDER Ney [continues]: Ney marches to Limousin. 2 regions to Bearn.
- ORDER Soult [continues]: Soult marches to Gascony. 1 region to Bearn.
  - POPUP strategic_interrupt: Davout, contact, Davout: 'Enemy at Bohemia. How shall I proceed?' → attack
- LEDGER treasury 9112 · net -58 · threat 38 · provinces 10 (+2) · ceiling 8726 · army 99338 · vassals Bavaria 96 · Holland 78 · Switzerland 74
  - NET income 784 · trade 561 · admin 50 · tribute 543 · upkeep 816 · charges 1075 · occupation 15 · admiralty 90
- DISPATCH: Sire — the enemy has held Paris, Anjou and Artois and 16 more 5 turns — the capital among them. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Uleaborg and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- DIPLO +5 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 22 — Early August 1806
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 actions unused) Turn 23 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Davout. Casualties: Archduke Charle… · Archduke John's forces press forward aggressively. Archduke John gains the advantage over Davout. Casualties: Archduke …
  - 🏴 Austria: Casualties: Archduke Charles 1,057, Davout 3,415. Both armies remain in the field. Bohemia has been captured by Austria!
  - 🏴 Austria: ArchdukeJohn advances into Tyrol. (107 lost to march — forward supply lines reduce losses) Tyrol has been captured by Austria!
  - ⚔ Archduke Charles (lost 762, own corps) vs Davout (lost 3415) — Even Davout's fortifications could not hold, Sire. Archduke Charles overran the position.
  - ⚔ Archduke John (lost 149, own corps) vs Davout (lost 3058) — Davout's fortified position was overwhelmed. A costly investment lost, Sire.
  - verbs: attack×2, fortify×1
- ORDER Bernadotte [completed]: Bernadotte arrives at Limousin. Bernadotte: "It is done. I took the liberty of posting pickets."
- ORDER Massena [error]: Massena could not advance toward Bearn.
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 8523 · net -246 · threat 35 · provinces 9 (-1) · ceiling 6987 · army 91884 · vassals Bavaria 94 · Holland 71 · Switzerland 68
  - NET income 634 · trade 561 · admin 50 · tribute 393 · upkeep 748 · charges 1046 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Uleaborg and 1 more — Russia is not forgiven

## Turn 23 — Late August 1806
  - MAILBOX #19 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #25 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, unfortify×1
- ORDER Davout [error]: Davout could not advance toward Limousin.
- ORDER Massena [error]: Massena could not advance toward Limousin.
- LEDGER treasury 7786 · net +823 · threat 15 · provinces 9 (+0) · ceiling 19331 · army 91038 · vassals Bavaria 94 · Holland 68 · Switzerland 66
  - NET income 744 · trade 573 · admin 50 · tribute 693 · upkeep 736 · charges 411 · admiralty 90
- DISPATCH: Sire — the enemy has held Paris, Anjou and Artois and 16 more 7 turns — the capital among them. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_coalition_dissolved, diplomatic_treaty_signed, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 35 to 17; Russia remains at war with us.

## Turn 24 — Early September 1806
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Davout [error]: Davout could not advance toward Limousin.
- ORDER Massena [error]: Massena could not advance toward Limousin.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
  - POPUP diplomatic_dialogue: Holland, client_petition #26 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2400g forgone). Loyalty +4 (65 → 69); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 8629 · net +686 · threat 13 · provinces 9 (+0) · ceiling 17846 · army 90218 · vassals Bavaria 94 · Holland 69 · Switzerland 64
  - NET income 744 · trade 573 · admin 50 · tribute 618 · upkeep 716 · charges 493 · admiralty 90
- DISPATCH: Sire — the enemy has held Paris, Anjou and Artois and 16 more 8 turns — the capital among them. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [error]: Davout could not advance toward Limousin.
- ORDER Massena [error]: Massena could not advance toward Limousin.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 9319 · net +616 · threat 11 · provinces 9 (+0) · ceiling 17244 · army 89421 · vassals Bavaria 94 · Holland 67 · Switzerland 62
  - NET income 744 · trade 573 · admin 50 · tribute 618 · upkeep 712 · charges 567 · admiralty 90
- DISPATCH: Sire — Davout and Massena are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 26 — Early October 1806
  - MAILBOX #21 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #27 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +4 (62 → 66); bond 40 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [error]: Davout could not advance toward Limousin.
- ORDER Massena [error]: Massena could not advance toward Limousin.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Deroy seeks an audience → acknowledge
  -     ↳ Deroy's grievance runs its course.
- LEDGER treasury 9774 · net +682 · threat 9 · provinces 9 (+0) · ceiling 18212 · army 55111 · vassals Bavaria 94 · Holland 65 · Switzerland 64
  - NET income 800 · trade 573 · admin 50 · tribute 393 · upkeep 416 · charges 628 · admiralty 90
- DISPATCH: Sire — Marshal Davout's corps was interned at Munich by Bavaria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 8
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 10464 · net +608 · threat 7 · provinces 9 (+0) · ceiling 17690 · army 54363 · vassals Bavaria 92 · Holland 63 · Switzerland 62
  - NET income 800 · trade 573 · admin 50 · tribute 393 · upkeep 408 · charges 710 · admiralty 90
- DISPATCH: Sire — Marshal Massena's corps was interned at Munich by Bavaria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 28 — Early November 1806
  - MAILBOX #22 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #28 → grant the petition
  - POPUP proposal_result: Bavaria's tribute is remitted for 8 collections (3144g forgone). Loyalty +4 (92 → 96); bond 59 → 59 (+2 a turn). Cost: 1 DP. → display-only
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10679 · net +169 · threat 5 · provinces 9 (+0) · ceiling 12607 · army 53637 · vassals Bavaria 94 · Holland 61 · Switzerland 60
  - NET income 800 · trade 573 · admin 50 · upkeep 408 · charges 756 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10856 · net +133 · threat 3 · provinces 9 (+0) · ceiling 12320 · army 52933 · vassals Bavaria 92 · Holland 52 · Switzerland 51
  - NET income 800 · trade 573 · admin 50 · upkeep 400 · charges 800 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_vassal_courting ×2, diplomatic_dp_regen)

## Turn 30 — Early December 1806
  - saved `sf4-q0-gev-b_t30` → Game saved: sf4-q0-gev-b_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 10997 · net +99 · threat 1 · provinces 9 (+0) · ceiling 12053 · army 52250 · vassals Bavaria 90 · Holland 43 · Switzerland 42
  - NET income 800 · trade 573 · admin 50 · upkeep 392 · charges 842 · admiralty 90
- DISPATCH: Sire — the enemy has held Paris, Anjou and Artois and 16 more 14 turns — the capital among them. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 11096 · net +61 · threat 0 · provinces 9 (+0) · ceiling 11721 · army 51587 · vassals Bavaria 88 · Holland 34 · Switzerland 33
  - NET income 800 · trade 573 · admin 50 · upkeep 392 · charges 880 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest ×2, diplomatic_auto_downgrade)

## Turn 32 — Early January 1807
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 11165 · net +333 · threat 0 · provinces 9 (+0) · ceiling 14490 · army 50944 · vassals Bavaria 86 · Holland 25 · Switzerland 24
  - NET income 800 · trade 573 · admin 50 · tribute 300 · upkeep 384 · charges 916 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest ×2)

## Turn 33 — Late January 1807
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 11506 · net +501 · threat 0 · provinces 9 (+0) · ceiling 16360 · army 50321 · vassals Bavaria 84 · Holland 16 · Switzerland 15
  - NET income 800 · trade 573 · admin 50 · tribute 525 · upkeep 376 · charges 981 · admiralty 90
- DISPATCH: Sire — the enemy has held Paris, Anjou and Artois and 16 more 17 turns — the capital among them. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest ×2)

## Turn 34 — Early February 1807
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 4 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
  - POPUP redemption: Deroy, 20 → grant_autonomy
  -     ↳ Deroy has been granted autonomy. They will act independently for 3 turns, using their own judgment in battle.
- LEDGER treasury 11965 · net +380 · threat 0 · provinces 9 (+0) · ceiling 15533 · army 49716 · vassals Bavaria 82 · Holland 7 · Switzerland 6
  - NET income 800 · trade 523 · admin 50 · tribute 525 · upkeep 368 · charges 1060 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Holland is on the verge of rebellion!
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - TURN EVENTS 2
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 11820 · net +232 · threat 0 · provinces 9 (+0) · ceiling 13934 · army 49130 · vassals Bavaria 60
  - NET income 800 · trade 523 · admin 50 · tribute 393 · upkeep 368 · charges 1076 · admiralty 90
- DISPATCH: Sire — Holland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - RAIL diplomatic_alliance_cascade: Spain enters the war against Holland and Switzerland via its alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Holland has rebelled against France. It is war.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, agenda_shift, diplomatic_relation_shift ×2)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG vassal_auto_join_war: Vassal Bavaria joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Holland has broken free of France. War.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.

## Turn 36 — Early March 1807
  - MAILBOX #23 Russia incoming_proposal: Russia — Armistice → activated
  - POPUP diplomatic_dialogue: Russia, armistice_losing #31 → accept
  - POPUP proposal_result: You have accepted Russia's proposal. Treaty signed: At War → Armistice with Russia. → display-only
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12052 · net +175 · threat 0 · provinces 9 (+0) · ceiling 13595 · army 48561 · vassals Bavaria 55
  - NET income 800 · trade 523 · admin 50 · tribute 393 · upkeep 368 · charges 1133 · admiralty 90
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL armistice_ratified: A truce with Russia: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_vassal_courting, diplomatic_dp_regen, sovereign_takes_field)

## Turn 37 — Late March 1807
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12235 · net +129 · threat 0 · provinces 9 (+0) · ceiling 13344 · army 48009 · vassals Bavaria 50
  - NET income 800 · trade 523 · admin 50 · tribute 393 · upkeep 360 · charges 1187 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 26 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland settlement offer
- LEDGER treasury 12372 · net +88 · threat 0 · provinces 9 (+0) · ceiling 13107 · army 47473 · vassals Bavaria 45
  - NET income 800 · trade 523 · admin 50 · tribute 393 · upkeep 352 · charges 1236 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 27 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL settlement_offer_arrival: Holland has offered terms to settle Holland vs France.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 39 — Late April 1807
  - MAILBOX #24 Holland incoming_settlement_offer: Holland — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #34 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12460 · net +44 · threat 0 · provinces 9 (+0) · ceiling 12816 · army 46954 · vassals Bavaria 40
  - NET income 800 · trade 523 · admin 50 · tribute 393 · upkeep 352 · charges 1280 · admiralty 90
- DISPATCH: Sire — the enemy has held Paris, Anjou and Artois and 16 more 23 turns — the capital among them. Each turn he holds them is a turn his recruiting sergeants work our ground.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 40 — Early May 1807
  - saved `sf4-q0-gev-b_t40` → Game saved: sf4-q0-gev-b_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 5 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 12512 · net +12 · threat 0 · provinces 9 (+0) · ceiling 12605 · army 46449 · vassals Bavaria 35
  - NET income 800 · trade 523 · admin 50 · tribute 393 · upkeep 344 · charges 1320 · admiralty 90
- DISPATCH: Sire — Marshal Murat's claim is 29 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armistice_expired_war: The armistice between France and Russia has collapsed. War resumes!
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)

---
finished: **completed** · commands 109 · popups 68 · battles 17
