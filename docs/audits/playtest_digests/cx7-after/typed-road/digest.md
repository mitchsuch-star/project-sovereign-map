# Playtest digest — typed-road

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `f52df77fab5e` (dirty) · content `afebc66d24ae` · driver `641a9fcf2c43`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `what can I do` → ✓ These orders would be carried out today, Sire:
- CMD `where is Ney` → ✓ Marshal Ney stands at Rhineland with 24,000 men (morale 100).
- CMD `who holds Swabia` → ✓ Swabia is held by Bavaria.
- CMD `how much is a battalion` → ✓ 654 gold for 10,000 infantry, Sire, at Rhineland. The price rises at war and above the force limit.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 action(s) unused) Turn 2 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on …
  - ⚔ Archduke Charles (lost 4875) vs Massena (lost 5379) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2512 · net +1961 · threat 68 · provinces 28 · ceiling 54105 · army 183621 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 3400 · trade 350 · admin 50 · tribute 895 · upkeep 2450 · charges 19 · blockade 175 · admiralty 90
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 1
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: PEACE → OPEN_BORDERS with Prussia. → display-only
- CMD `what's my income` → ✓ The treasury holds 2,572 gold, Sire. The provinces yield 3,400 and trade 450; the army costs 2,450. Net +2,009 a turn. The full account is in the Strategic Ledger's Econ…
- CMD `am I at war with Prussia` → ✓ No, Sire. France and Prussia stand at Open Borders.
- CMD `what does Austria want` → ✓ Austria pursues Revanche, Sire. What was taken shall be retaken. The court has not forgiven the loss of Bohemia and 1 more. The provinces in question: Bohemia, Carniola.…
- CMD `can Ney reach Vienna` → ✓ Yes, Sire — Ney can reach Vienna from Rhineland in 4 turns: Rhineland -> Swabia -> Franconia -> Bohemia -> Vienna.
- CMD `who is winning` → ✓ War score, Sire — Austria +0 (evenly matched); Britain +0 (evenly matched); Russia +0 (evenly matched). The breakdown is on the war banner on the left (click the war).
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 action(s) unused) Turn 3 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles 2,… · Mack's forces advance steadily. Brutal stalemate between Mack and Lannes. Heavy casualties on both sides: Mack 5,290, L… · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: Casualties: ArchdukeCharles's army 1,318, Deroy 8,956. Both armies remain in the field. Bohemia has been captured by Austria!
  - ⚔ Archduke Charles (lost 2527) vs Deroy (lost 5698) — The battle unfolded without particular distinction.
  - ⚔ Mack (lost 5290) vs Lannes (lost 1524, own corps) — Napoleon's timely arrival aided Lannes. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 917, own corps) vs Deroy (lost 8956) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×4, stance_change×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4492 · net +2039 · threat 66 · provinces 28 (+0) · ceiling 51675 · army 179386 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 3382 · trade 450 · admin 50 · tribute 901 · upkeep 2322 · charges 107 · blockade 225 · admiralty 90
- DISPATCH: Sire — Carniola has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `what happens if I attack Mack` → ✓ Were you to give the order, Sire:
- CMD `why not attack Mack` → ✓ Were you to give the order, Sire:
- CMD `what about attack Mack` → ✓ Were you to give the order, Sire:
- CMD `is it time to attack Mack` → ✓ Were you to give the order, Sire:
- CMD `should I attack` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 6 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archd… · ArchdukeJohn holds them at Franconia while allies attack from Bohemia! (+1 coordination) · Mack completes the encirclement from Swabia! (+2 coordination) · ArchdukeJohn delivers an effective strike. Bernadotte holds the line. Casualties: ArchdukeJohn 5,862, Bernadotte's army…
  - 🏴 Austria: Both armies remain in the field. Mack advances into Franconia. (1,332 lost to march) Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 1263, own corps) vs Bernadotte (lost 6757) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke John (lost 88, own corps) vs Deroy (lost 3095) — Deroy's army has been badly mauled. Archduke John proved the stronger force today.
  - ⚔ Mack (lost 740, own corps) vs Bernadotte (lost 5637) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke John (lost 5862) vs Bernadotte (lost 111, own corps) — Lannes and Massena arrived to reinforce Bernadotte! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×4, wait×1, recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- ENVOYS WAITING 3 · Hesse non aggression · Britain settlement offer · PapalStates open borders
- LEDGER treasury 6445 · net +2410 · threat 64 · provinces 28 (+0) · ceiling 47702 · army 163130 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 91
  - NET income 3384 · trade 525 · admin 50 · tribute 905 · upkeep 1842 · charges 259 · blockade 263 · admiralty 90
- DISPATCH: Sire — Bernadotte, crowned last turn, has been beaten in the field.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
  - MAILBOX #8 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #8 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #9 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (7 pair(s) resolved). → display-only
- CMD `Nay attack Mack` → ✗ There is no 'Nay' in the order of battle, Sire. Whom did you intend?
- CMD `Zorglub attack Mack` → ✗ There is no 'Zorglub' in the order of battle, Sire. Whom did you intend?
- CMD `Wellington retreat` → ✗ There is no 'Wellington' in the order of battle, Sire. Whom did you intend?
- CMD `Davoust, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Rhineland. Defense bonus: +7% (grows +3% per turn,…
- CMD `Ney, attack Mack` → ✗ We are not at war with Austria, Sire — Mack may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 action(s) unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, grant_dotation×1, wait×1
- LEDGER treasury 9713 · net +3125 · threat 32 · provinces 28 (+0) · ceiling 270083 · army 160890 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 89
  - NET income 3386 · trade 623 · admin 50 · tribute 910 · upkeep 1752 · charges 92
- DISPATCH: Sire — Lannes, Bernadotte and Massena stand 51,601 men at Munich, which feeds 37,500. 14,101 too many. 4,648 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large…
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: Austria, Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 64 to 32.

## Turn 5 — Late November 1805
- CMD `Davout, hold Ulm` → ✗ Region 'Ulm' not found.
- CMD `Ney, march to Swabland` → ✗ Region 'Swabland' not found. Did you mean 'Swabia'?
- CMD `halt Ney` → ✓ Ney awaits further orders.
- CMD `cancel Ney` → ✓ Ney awaits further orders.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, m…
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 action(s) unused) Turn 6 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 12904 · net +3153 · threat 32 · provinces 28 (+0) · ceiling 275583 · army 158847 · vassals Holland 93 · Kingdom of Italy 93 · Switzerland 87
  - NET income 3388 · trade 623 · admin 50 · tribute 914 · upkeep 1692 · charges 130
- DISPATCH: Sire — Lannes, Bernadotte and Massena stand 49,558 men at Munich, which feeds 45,000. 4,558 too many. 6,691 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large …
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 6 — Early December 1805
  - MAILBOX #9 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #10 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +7 (93 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `retreat?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `is Swabia defended` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `can Davout attack Mack` → ✓ Were you to give the order, Sire:
- CMD `why did that fail` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `what can I build here` → ✓ At Rhineland we may build: supply depot (300g), fortification (400g), training ground (250g), market (350g), stables (300g).
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #11 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (2856g forgone). Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 15764 · net +2468 · threat 32 · provinces 28 (+0) · ceiling 221416 · army 157782 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 85
  - NET income 3389 · trade 623 · admin 50 · tribute 225 · upkeep 1654 · charges 165
- DISPATCH: Sire — 3 turns of famine at Munich now. 5,348 men gone, and not one of them to the enemy. Bavaria's magazines feed us as our own — the army is simply too large for the province. Milan can feed 75,000…
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 7 — Late December 1805
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 9.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Bernadotte, scout Franconia` → ✓ Bernadotte scouts Franconia: Controlled by Austria. Terrain: Plains. No enemy forces detected.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. Turn 8 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 18257 · net +2463 · threat 32 · provinces 28 (+0) · ceiling 223500 · army 156757 · vassals Holland 98 · Kingdom of Italy 99 · Switzerland 83
  - NET income 3392 · trade 623 · admin 50 · tribute 225 · upkeep 1632 · charges 195
- DISPATCH: Sire — Marshal Massena's household goes unpaid. His patience erodes with his purse.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 8 — Early January 1806
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #12 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `flurble the wibble` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — 'Ney, march to Lorraine', perh…
- CMD `Ney, never attack Mack` → ✗ Berthier lowers the dispatch. "Then no order goes out, Sire — I have relayed nothing. If a standing order is to be stood down, say 'cancel his order'; otherwise tell me …
- CMD `Ney, attack if Davout supports` → ✗ Berthier sets down his pen. "Sire, that is a contingency, not an order — I have no way to hold a dispatch until the enemy moves. Nothing has been relayed. Give me the or…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `what now` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — 'Ney, march to Lorraine', perh…
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 action(s) unused) Turn 9 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  -     ↳ "I will find the means." Rentes are granted: Lannes (40g/turn); Bernadotte (40g/turn); Massena (40g/turn). Th…
- LEDGER treasury 20527 · net +2063 · threat 32 · provinces 28 (+0) · ceiling 192416 · army 155770 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 92
  - NET income 3394 · trade 623 · admin 50 · upkeep 1602 · charges 222 · rentes 180
- DISPATCH: Sire — Lannes, Bernadotte and Massena have been 5 turns over what Munich can feed. 3,077 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too…
  - TURN EVENTS 9
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 9 — Late January 1806
- CMD `quickly attack Mack` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `immediately attack Mack` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `ok retreat` → ✗ No marshals are in danger. None need to retreat.
- CMD `tonight Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Rhi…
- CMD `someone attack Mack` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 action(s) unused) Turn 10 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Lannes: They settle into cold war.
- LEDGER treasury 22622 · net +2070 · threat 32 · provinces 28 (+0) · ceiling 195083 · army 154819 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 91
  - NET income 3396 · trade 623 · admin 50 · upkeep 1572 · charges 247 · rentes 180
- DISPATCH: Sire — Lannes, Bernadotte and Massena have been 6 turns over what Munich can feed. 2,963 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too…
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 10 — Early February 1806
- CMD `cavalry attack Mack` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `guards attack Mack` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Marshal attack Mack` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `anyone scout Swabia` → ✓ Soult scouts Swabia: Controlled by Austria. Terrain: Plains. No enemy forces detected.
- CMD `right, attack Mack` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 action(s) unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 24724 · net +2077 · threat 32 · provinces 28 (+0) · ceiling 197750 · army 153902 · vassals Holland 95 · Kingdom of Italy 96 · Switzerland 90
  - NET income 3398 · trade 623 · admin 50 · upkeep 1542 · charges 272 · rentes 180
- DISPATCH: Ney's fortifications strengthen: +8% defense (MAX)
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 11 — Late February 1806
- CMD `Zorglub pull back` → ✗ There is no 'Zorglub' in the order of battle, Sire. Whom did you intend?
- CMD `Zorglub recon Swabia` → ✗ There is no 'Zorglub' in the order of battle, Sire. Whom did you intend?
- CMD `all marshals, attack` → ✗ No combat-ready marshals!
- CMD `whoever is closest attack Mack` → ✗ Massena is fortified at Munich and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `well retreat` → ✗ No marshals are in danger. None need to retreat.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 26811 · net +2062 · threat 32 · provinces 28 (+0) · ceiling 198583 · army 153012 · vassals Holland 94 · Kingdom of Italy 95 · Switzerland 89
  - NET income 3400 · trade 623 · admin 50 · upkeep 1534 · charges 297 · rentes 180
- DISPATCH: Davout's fortifications decay: 12% → 11%
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 12 — Early March 1806
- CMD `Ney attack Mack?` → ✗ Ney is fortified at Rhineland and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Davout fortify?` → ✗ Davout is already fortified at Rhineland (+11% defense).
- CMD `Soult scout Swabia?` → ✓ Soult scouts Swabia: Controlled by Austria. Terrain: Plains. No enemy forces detected.
- CMD `Murat drill?` → ✓ Murat begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 action(s) unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 28895 · net +2059 · threat 32 · provinces 28 (+0) · ceiling 200416 · army 152139 · vassals Holland 93 · Kingdom of Italy 94 · Switzerland 88
  - NET income 3400 · trade 623 · admin 50 · upkeep 1512 · charges 322 · rentes 180
- DISPATCH: Ney's fortifications decay: 8% → 6%
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 70 · popups 21 · battles 8
