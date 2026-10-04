# Playtest digest — vdc_final2-historical

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `f3ce1b57a0d2` (dirty) · content `c60e8146a928` · driver `d93820e75501`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 85,373 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2157, own corps) vs Mack (lost 17054) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult and Bernadotte never arr… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu…
  - ⚔ Archduke Charles (lost 4213) vs Massena (lost 6225) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1645 · net +1469 · threat 76 · provinces 28 · ceiling 34790 · army 173942 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 2126 · blockade 250 · admiralty 90
- DISPATCH: Supply cost you 2,636 men, at Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,808; expect about 94,391 with the corps likely to arrive, up to 104,979 if all march) vs Mack (substantial force) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 803, own corps) vs Mack (lost 21656) — Davout, Massena and Teulie arrived to reinforce Ney, but Napoleon failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,071; expect about 40,115 with the corps likely to arrive) vs Mack (large force) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 5258, own corps) vs Archduke Charles (lost 2031, own corps) — Ney marched to Davout's guns as ordered. It was not enough.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Dumonceau, move to Flanders` → ✓ Dumonceau moves from Amsterdam to Flanders
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Deroy's forces advance steadily. Archduke John holds the line. Casualties: Deroy 3,032, Archduke John 1,631. Both armie… · Deroy engages in solid combat. Archduke John holds the line. Casualties: Deroy 2,866, Archduke John 1,282. Both armies …
  - ⚔ Archduke Charles (lost 2018) vs Bernadotte (lost 5561) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Deroy (lost 3032) vs Archduke John (lost 1631) — Archduke John's fortifications held firm, Sire. Deroy broke against our walls.
  - ⚔ Deroy (lost 2866) vs Archduke John (lost 1282) — The prepared defenses proved their worth. Deroy could not dislodge Archduke John.
  - verbs: attack×3, fortify×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2971 · net +2005 · threat 82 · provinces 28 (+0) · ceiling 35725 · army 154533 · vassals Holland 97 · Kingdom of Italy 96 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 901 · upkeep 1556 · charges 59 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,561 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 9
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (16,150; expect about 24,894 with the corps likely to arrive, up to 29,891 if all march) vs Mack (11,380 men) at Tyrol — the balance of force looks even — a…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1306, own corps) vs Mack (lost 3465, own corps) — Massena and Teulie's timely arrival aided Ney. Davout, however, was conspicuously absent.
- CMD `Davout, attack Mack` → ✓ Davout: 'Enemy holds Tyrol — destination blocked. How shall I proceed, Sire?'
  - POPUP strategic_interrupt: Davout, contact, Davout: 'Enemy holds Tyrol — destination blocked. How shall I proceed, Sire?' → attack
  - ↳ Davout attacks ArchdukeJohn and wins! Continuing the pursuit. MUSTER — Davout (16,998; expect about 71,839 with the corps likely to arrive) vs Archduke John (12,979 men) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 320, own corps) vs Archduke John (lost 6681) — Davout broke through fortified positions — extraordinary courage from the men.
  - POPUP capture_choice[capture]: Tyrol, Davout → secure
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (167 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 686 gold (×3 at war) (×1.14 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 686g on this turn's orders
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy launches a decisive assault. Deroy gains the advantage over Mack. Casualties: Deroy 169, Mack 4,843. Both armies … · Deroy holds them at Bohemia while allies attack from Franconia! (+1 coordination)
  - 🏴 Bavaria: [!] MARSHAL CAPTURED — Mack is taken by Bavaria at Bohemia!
  - 🏴 Bavaria: [!] Archduke John's troops are BROKEN (morale 0%)! FORCED RETREAT! Bohemia has been captured by Bavaria!
  - ⚔ Deroy (lost 169) vs Mack (lost 4843) — A grievous defeat for Mack, Sire. The losses are severe. And Mack was taken on that field — Bavaria holds him.
  - ⚔ Deroy (lost 192) vs Archduke John (lost 2649) — The toll on Archduke John's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, wait×1, move×1
- ORDER Davout [active]: Davout is pursuing Mack (1 turn remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4407 · net +1989 · threat 88 · provinces 29 (+1) · ceiling 25125 · army 149810 · vassals Holland 99 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2609 · trade 525 · admin 50 · tribute 905 · upkeep 1398 · charges 231 · occupation 52 · blockade 329 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Tyrol — Archduke John's corps is driven from Tyrol yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `Teulie, move to Tyrol` → ✗ Teulie is already in Tyrol.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Vienna into Bohemia unopposed! (1,287 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles marches from Vienna into Bohemia unopposed! (1,287 lost to march) Captured: Bavaria → Austria
  - verbs: attack×1, fortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 6648 · net +1916 · threat 86 · provinces 29 (+0) · ceiling 25961 · army 145537 · vassals Holland 99 · Kingdom of Italy 97 · Switzerland 92
  - NET income 2610 · trade 587 · admin 50 · tribute 910 · upkeep 1270 · charges 461 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples, Denmark and Bavaria rebuff Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (12,835; expect about 19,526 with the corps likely to arrive) vs Archduke Charles (41,636 men) at Bohemia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 5003, own corps) vs Archduke Charles (lost 1456) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Mack is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✗ Murat is already in Swabia.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Teulie [retired]: Teulie's question is overtaken, Sire — Teulie has marched clear of Bohemia. He awaits new orders.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 8664 · net +2153 · threat 84 · provinces 29 (+0) · ceiling 36256 · army 134094 · vassals Holland 97 · Kingdom of Italy 92 · Switzerland 88
  - NET income 2653 · trade 587 · admin 50 · tribute 914 · upkeep 1044 · charges 519 · occupation 30 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
  - MAILBOX #8 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #9 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +8 (92 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 2g a turn — 63g of income forfeited, 30g of occupation relieved, 47g returned as tribute at today's 75% rate, the force limit falls 2,500 (+12g surcharge). → display-only
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Bohemia into Carniola unopposed! (162 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeJohn marches from Bohemia into Carniola unopposed! (162 lost to march) Captured: Bavaria → Austria
  - verbs: move×3, unfortify×1, attack×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10563 · net +1666 · threat 82 · provinces 28 (-1) · ceiling 25543 · army 130500 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 86
  - NET income 2590 · trade 587 · admin 50 · tribute 967 · upkeep 1008 · charges 952 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, coercive_demand)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
  - MAILBOX #9 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (86 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (18,537; expect about 19,646 with the corps likely to arrive, up to 19,987 if all march) vs Archduke Charles (40,180 men) at Bohemia — the balance of forc…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 6467, own corps) vs Archduke Charles (lost 1946) — Reinforcements from Teulie bolstered Murat's position — though Davout never arrived, Sire. — The corps system brought Teulie in. — The Hofkriegsrat's orders reached Archduke John too late.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 9 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeJohn strikes back after successfully defending! · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Davout. Casualties: Arc… · Deroy launches a decisive assault. Deroy gains the advantage over Archduke John. Casualties: Deroy 1,024, Archduke John…
  - 🏴 Austria: Heavy casualties on both sides: Archduke John 3,104, Ney's army 4,607. Franconia has been captured by Austria!
  - 🏴 Austria: [!] No word came for Teulie, cornered at Tyrol — the enemy did not wait. [!] MARSHAL CAPTURED — Teulie is taken by Austria at Tyrol!
  - 🏴 Bavaria: Deroy moves from Croatia to Carniola. Carniola falls to Bavaria!
  - 🏴 Bavaria: Deroy moves from Carniola to Bohemia. Bohemia falls to Bavaria!
  - ⚔ Archduke Charles (lost 727, own corps) vs Bernadotte (lost 6715) — Where was Soult? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke John (lost 911, own corps) vs Ney (lost 1189, own corps) — Reinforcements from Davout, Murat and Napoleon bolstered Ney's position — though Soult never arrived, Sire. — Berthier: the corps marched apart and arrived together.
  - ⚔ Archduke Charles (lost 1117) vs Davout (lost 2688, own corps) — Davout held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Deroy (lost 1024) vs Archduke John (lost 1636) — Archduke John was close. A period of drilling could have changed the outcome.
  - verbs: attack×4, move×3, unfortify×1, form_square×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 11041 · net +1333 · threat 80 · provinces 28 (+0) · ceiling 21073 · army 105776 · vassals Holland 91 · Kingdom of Italy 85 · Switzerland 89
  - NET income 2590 · trade 587 · admin 50 · tribute 698 · upkeep 824 · charges 1200 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Marshal Teulie has been taken. Austria holds him prisoner.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 12
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +6 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, agenda_shift, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! Archduke John is at Franconia, just one region away.
- CMD `Massena, move to Milan` → ✗ Cannot advance while engaged with Archduke Charles at Tyrol. No friendly province adjoins him: he must fight or stand.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 actions unused) Turn 9 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy takes Franconia where he stands! Captured: Austria → Bavaria · Deroy attacks with overwhelming force. Deroy gains the advantage over Archduke John. Casualties: Deroy 508, Archduke Jo… · Deroy holds them at Bohemia while allies attack from Franconia! (+1 coordination)
  - 🏴 Bavaria: Deroy takes Franconia where he stands! Captured: Austria → Bavaria
  - ⚔ Deroy (lost 508) vs Archduke John (lost 2829) — The toll on Archduke John's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Deroy (lost 1938) vs Archduke Charles (lost 1359) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×3, retreat×1, stance_change×1
- LEDGER treasury 12456 · net +1193 · threat 78 · provinces 28 (+0) · ceiling 21227 · army 102875 · vassals Holland 91 · Kingdom of Italy 88 · Switzerland 88
  - NET income 2590 · trade 587 · admin 50 · tribute 748 · upkeep 792 · charges 1422 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Denmark, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 7116) vs Archduke Charles (lost 1125) — Massena's corps broke, Sire. They are streaming back from the field.
- LEDGER treasury 13316 · net +1006 · threat 76 · provinces 28 (+0) · ceiling 20221 · army 93334 · vassals Holland 89 · Kingdom of Italy 89 · Switzerland 85
  - NET income 2590 · trade 587 · admin 50 · tribute 754 · upkeep 720 · charges 1647 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — Massena's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 10
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 22 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Swabia to Franconia (58 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Bohemia, Carniola, Croatia, Franconia, Munich, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: naval_expedition×1, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 14344 · net +839 · threat 74 · provinces 28 (+0) · ceiling 19977 · army 91768 · vassals Holland 89 · Kingdom of Italy 92 · Switzerland 84
  - NET income 2590 · trade 587 · admin 50 · tribute 760 · upkeep 704 · charges 1836 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG ai_ai_proposal_refused: 11 courts rebuff Bavaria (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Andalusia stays British by the treaty. Status quo: Bohemia, Carniola and Croatia stay Bavarian by the treaty. Status quo: Tyrol stays ours by the treaty — titled. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Tyrol to Franconia (103 lost to march)
- CMD `Massena, fortify` → ✗ Massena is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 actions unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 17493 · net +3112 · threat 39 · provinces 28 (+0) · ceiling 276750 · army 95203 · vassals Holland 87 · Kingdom of Italy 93 · Switzerland 83
  - NET income 2590 · trade 623 · admin 50 · tribute 762 · upkeep 728 · charges 185
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 4
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — alliance is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, status_quo_titled, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 74 to 37.
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

## Turn 12 — Early March 1806
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Dumonceau [completed]: Dumonceau arrives at Amsterdam. Dumonceau: "Accomplished as ordered. The army is intact."
- LEDGER treasury 20269 · net +2742 · threat 41 · provinces 28 (+0) · ceiling 248750 · army 93785 · vassals Holland 96 · Kingdom of Italy 94 · Switzerland 82
  - NET income 2590 · trade 623 · admin 50 · tribute 426 · upkeep 728 · charges 219
- DISPATCH: Sire — the establishment stands 36,215 men under the ordinance, and the depots hold 99,994. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #14 → 1
  -     ↳ refused: The armistice with Austria holds for 3 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✓ Davout begins marching to Franconia (distance: 2). Moved to Tyrol. Route: Tyrol -> Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 1 action unused) Turn 14 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Davout [active]: Davout is marching to Franconia (2 turns remaining).
- LEDGER treasury 23056 · net +2754 · threat 43 · provinces 28 (+0) · ceiling 252500 · army 92223 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 81
  - NET income 2590 · trade 623 · admin 50 · tribute 447 · upkeep 704 · charges 252
- DISPATCH: Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, coercive_demand)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Milan to Tyrol (351 lost to march)
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Davout [completed]: Davout arrives at Franconia. Davout: "Done, and done properly — no stragglers, no surprises."
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 25820 · net +2956 · threat 45 · provinces 28 (+0) · ceiling 272083 · army 90447 · vassals Holland 94 · Kingdom of Italy 94 · Switzerland 80
  - NET income 2590 · trade 623 · admin 50 · tribute 674 · upkeep 696 · charges 285
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL broken_bargain: The compact with Sweden lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, blockade_begins, diplomatic_relation_shift)

## Turn 15 — Late April 1806
  - MAILBOX #12 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #15 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (3592g forgone). Loyalty +6 (94 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 28335 · net +2484 · threat 45 · provinces 28 (+0) · ceiling 235333 · army 89152 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 79
  - NET income 2590 · trade 623 · admin 50 · tribute 225 · upkeep 688 · charges 316
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)

## Turn 16 — Early May 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (79 → 89); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia (57 lost to march)
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 16 ended. Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 30602 · net +2240 · threat 45 · provinces 28 (+0) · ceiling 217250 · army 87839 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · upkeep 680 · charges 343
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Karelia. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Fortifying from neutral stance requires 2 actions (1 for stance change + 1 for fortify), but only 1 remaining.
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 32850 · net +2221 · threat 45 · provinces 28 (+0) · ceiling 217916 · army 86621 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · upkeep 672 · charges 370
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Karelia — Russia is not forgiven

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, garrison×1, wait×1
- LEDGER treasury 35071 · net +2195 · threat 45 · provinces 28 (+0) · ceiling 217916 · army 85440 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · upkeep 672 · charges 396
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Swabia to Franconia (100 lost to march)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 37290 · net +2529 · threat 45 · provinces 28 (+0) · ceiling 248000 · army 84776 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 337 · upkeep 648 · charges 423
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 2
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 2 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 39819 · net +2499 · threat 45 · provinces 28 (+0) · ceiling 248000 · army 84223 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 337 · upkeep 648 · charges 453
- DISPATCH: Sire — the establishment stands 45,777 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 21 — Late July 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #17 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 41997 · net +2152 · threat 45 · provinces 28 (+0) · ceiling 221250 · army 83682 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · upkeep 632 · charges 479
- DISPATCH: Sire — the establishment stands 46,318 men under the ordinance, and the depots hold 100,000. 10,000 foot cost 150 gold at Paris, where a marshal must stand to receive them.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✗ Massena is not currently fortified.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 44149 · net +2593 · threat 45 · provinces 28 (+0) · ceiling 260166 · army 83151 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 467 · upkeep 632 · charges 505
- DISPATCH: Sire — 3 turns now with the establishment under the ordinance and the depots standing full. 46,849 men at Paris, and nobody has gone to collect them.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 46744 · net +2789 · threat 45 · provinces 28 (+0) · ceiling 279083 · army 82631 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 694 · upkeep 632 · charges 536
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 49543 · net +2765 · threat 45 · provinces 28 (+0) · ceiling 279916 · army 82121 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 696 · upkeep 624 · charges 570
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 52311 · net +2735 · threat 45 · provinces 28 (+0) · ceiling 280166 · army 81622 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 699 · upkeep 624 · charges 603
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 55048 · net +2704 · threat 45 · provinces 28 (+0) · ceiling 280333 · army 81134 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 701 · upkeep 624 · charges 636
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 57762 · net +2681 · threat 45 · provinces 28 (+0) · ceiling 281166 · army 80655 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 703 · upkeep 616 · charges 669
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 60445 · net +2988 · threat 49 · provinces 28 (+0) · ceiling 309416 · army 80186 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 1042 · upkeep 616 · charges 701
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, law_lapsed_abroad)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (open borders agreement)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 63436 · net +2955 · threat 53 · provinces 28 (+0) · ceiling 309666 · army 79726 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 1045 · upkeep 616 · charges 737
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Britain (defensive alliance)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 66409 · net +2938 · threat 57 · provinces 28 (+0) · ceiling 311166 · army 79275 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 1047 · upkeep 600 · charges 772
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 69349 · net +2904 · threat 60 · provinces 28 (+0) · ceiling 311333 · army 78833 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 1049 · upkeep 600 · charges 808
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover, Sardinia alarmed (threat: 60)
  - LOG ai_ai_proposal_refused: Britain rebuffs Austria (open borders agreement)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 72253 · net +2869 · threat 58 · provinces 28 (+0) · ceiling 311333 · army 78400 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 1049 · upkeep 600 · charges 843
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, law_lapsed_abroad)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 75130 · net +2843 · threat 56 · provinces 28 (+0) · ceiling 312000 · army 77976 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 623 · admin 50 · tribute 1049 · upkeep 592 · charges 877
- DISPATCH: Sire — a quiet morning on the front. The marshals await your word.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 76002 · net +608 · threat 54 · provinces 28 (+0) · ceiling 93250 · army 77560 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 89
  - NET income 2590 · trade 549 · admin 50 · tribute 1049 · upkeep 592 · charges 2604 · blockade 344 · admiralty 90
- DISPATCH: Sire — Britain and France are at war. Britain tears up the Peace Treaty to do it.
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sardinia has declared war on France, with 2 allied courts poised to follow.
  - RAIL +5 more
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +17 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, witness_strike_recorded ×3, diplomatic_treaty_broken, cs_tier_shift, blockade_begins ×4, agenda_shift, diplomatic_relation_shift ×5)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).
  - LOG coalition_declared: The Fourth Russian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia, Sweden
  - LOG third_party_peace: THE CONGRESS: Russia and Sweden make peace without France

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks with overwhelming force. Archduke Charles gains the advantage over Ney. Casualties: Archduke C… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Ney. Casualties: Archdu…
  - 🏴 Austria: [!] No word came for Ney, cornered at Bohemia — the enemy did not wait. [!] MARSHAL CAPTURED — Ney is taken by Austria at Bohemia!
  - ⚔ Archduke Charles (lost 2404) vs Ney (lost 1483, own corps) — Lannes, Murat and Massena marched to Ney's guns as ordered. It was not enough. — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
  - ⚔ Archduke Charles (lost 108, own corps) vs Ney (lost 1832) — A grievous defeat for Ney, Sire. The losses are severe. And Ney was taken on that field — Austria holds him.
  - verbs: attack×2, move×1, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 75674 · net -94 · threat 52 · provinces 28 (+0) · ceiling 73637 · army 63481 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 95
  - NET income 2590 · trade 549 · admin 50 · tribute 1049 · upkeep 480 · charges 3418 · blockade 344 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL settlement_offer_arrival: Russia has offered terms to settle Russia vs Sweden.
  - RAIL third_party_peace: THE CONGRESS: Britain and Sweden have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes o…
  - TURN EVENTS 6
- DIPLO +8 medium/low (diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, paymaster_subsidy, cs_tier_shift, blockade_broken, agenda_shift)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Austria (open borders agreement)

## Turn 36 — Early March 1807
  - MAILBOX #15 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #18 already answered this chain)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✗ Massena is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 4 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 75446 · net -452 · threat 50 · provinces 28 (+0) · ceiling 66314 · army 61535 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 899 · upkeep 464 · charges 3642 · blockade 344 · admiralty 90
- DISPATCH: Sire — Piedmont has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Paget has put 7,323 men ashore at Piedmont.
  - RAIL third_party_peace: THE CONGRESS: Austria and Sweden have made their peace without France. Both courts are spent; their side of the war ends while the greater war goes o…
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).

## Turn 37 — Late March 1807
  - MAILBOX #15 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → request_settlement_revision
  -     ↳ refused: Only the war leader can settle this side.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → (stale passthrough — #18 already answered this chain)
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 8 actions, 4 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget assaults the Milan garrison! Garrison: 10,000 -> 6,442 (-3,558). Paget loses 1,800 troops. Garrison holds — 6,442… · Paget assaults the Milan garrison! Garrison collapses (6,442 -> 0). Paget loses 1,104 troops in the assault. Paget marc… · ArchdukeCharles assaults the Bohemia garrison! Garrison: 750 -> 375 (-375). ArchdukeCharles loses 208 troops. Garrison … · The detachment of 375 at Bohemia lays down its arms. ArchdukeCharles marches from Vienna into Bohemia unopposed! (649 l…
  - 🏴 Britain: [Materiel] Guns, horses and stores lost with the fallen: Britain -55g, Kingdom of Italy -140g. Captured: KingdomOfItaly → Britain
  - 🏴 Austria: ArchdukeCharles marches from Vienna into Bohemia unopposed! (649 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - verbs: attack×4, move×2, wait×1, recruit×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 74777 · net -869 · threat 48 · provinces 28 (+0) · ceiling 58306 · army 59842 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 549 · admin 50 · tribute 674 · upkeep 456 · charges 3842 · blockade 344 · admiralty 90
- DISPATCH: Sire — Milan has been taken by Britain.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: Britain and Sweden rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Britain (defensive alliance)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG ai_ai_proposal_refused: Britain rebuffs Sardinia (design ask)
  - LOG third_party_peace: THE CONGRESS: Austria and Sweden make peace without France
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG third_party_peace: THE CONGRESS: Britain and Sweden make peace without France
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG ai_ai_proposal_refused: Russia rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Britain (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (500g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses
  - LOG ai_ai_proposal_refused: 13 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: 13 approaches from Britain and Austria are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (400g/turn)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Britain (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Britain (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Sardinia lapses

## Turn 38 — Early April 1807
  - MAILBOX #15 Russia incoming_settlement_offer: Russia — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → reject_settlement_offer
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, drill` → ✗ Massena cannot drill with enemy forces nearby! Archduke Charles is at Bohemia, just one region away.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 7 actions, 3 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Paget marches from Munich into Tyrol unopposed! (85 lost to march) Captured: KingdomOfItaly → Britain · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Lannes. Casualties: Archduke Charle… · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Soult. Casualties: Arch…
  - 🏴 Britain: Paget marches from Munich into Tyrol unopposed! (85 lost to march) Captured: KingdomOfItaly → Britain
  - 🏴 Austria: Both armies remain in the field. ArchdukeCharles advances into Franconia. (1,227 lost to march) Franconia has been captured by Austria!
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Swabia!
  - ⚔ Archduke Charles (lost 1749) vs Lannes (lost 1810, own corps) — Reinforcements from Napoleon bolstered Lannes's position — though Bernadotte never arrived, Sire.
  - ⚔ Archduke Charles (lost 1430) vs Soult (lost 2284, own corps) — Soult's fortified position was overwhelmed. A costly investment lost, Sire.
  - verbs: attack×3, move×1, retreat×1, stance_change×1, wait×1
- LEDGER treasury 70703 · net -3499 · threat 36 · provinces 28 (+0) · ceiling 33631 · army 45061 · vassals Holland 100 · Switzerland 100
  - NET income 2590 · trade 561 · admin 50 · tribute 562 · upkeep 336 · charges 6485 · blockade 351 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - TURN EVENTS 8
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, blockade_broken)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Davout is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- enemy phase: 10 actions, 1 attacks — Russia, Prussia, the Ottoman Empire and 3 other courts stirred as well, but their formations remain beyond our sight. — Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 576, Paget …
  - ⚔ Castanos (lost 576) vs Paget (lost 1595) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price. — The Line Holds +15% (Paget)
  - verbs: move×5, retreat×1, stance_change×1, unfortify×1, attack×1, wait×1
- LEDGER treasury 65087 · net -5119 · threat 34 · provinces 28 (+0) · ceiling 24962 · army 42660 · vassals Holland 100 · Switzerland 100
  - NET income 2583 · trade 561 · admin 50 · tribute 562 · upkeep 312 · charges 8049 · contributions 73 · blockade 351 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Lyonnais. No French corps stands in his path.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (NON AGGRESSION → OPEN BORDERS)
  - LOG british_subsidy: Britain's gold: 500g reaches Sardinia
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✗ Massena is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: form_square×1, wait×1
- ENVOYS WAITING 1 · Russia settlement offer
- LEDGER treasury 61943 · net -3029 · threat 32 · provinces 28 (+0) · ceiling 31890 · army 40403 · vassals Holland 100 · Switzerland 100
  - NET income 2585 · trade 561 · admin 50 · tribute 562 · upkeep 304 · charges 6042 · blockade 351 · admiralty 90
- DISPATCH: Sire — the levy has stood open 7 turns. 450 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL settlement_offer_arrival: Russia has offered terms to settle Russia vs France. Asking 12633 gold.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

---
finished: **completed** · commands 200 · popups 43 · battles 25
