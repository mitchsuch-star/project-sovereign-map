# Playtest digest — TYPED

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `077efb374d7c` · content `e96449bb3b47` · driver `bd054bd265d8`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `what can I do` → ✓ These orders would be carried out today, Sire:
  - ↳ Ney, attack Mack / Davout, march to Lorraine
- CMD `where is Ney` → ✓ Marshal Ney stands at Rhineland with 24,000 men (morale 100).
- CMD `who holds Swabia` → ✓ Swabia is held by Bavaria.
- CMD `how much is a battalion` → ✓ 741 gold for 3,000 infantry, Sire — 'recruit infantry in Rhineland' raises them under Davout — a field levy, capped by what the province feeds. At Paris the bare order i…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena
  - ⚔ Archduke Charles (lost 4611) vs Massena (lost 4941) — Stalemate. Massena and Archduke Charles glare at each other across the field. — The Hofkriegsrat's orders reached Archduke John too late.
  - verbs: attack×1, wait×1
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1445 · net +892 · threat 68 · provinces 28 · ceiling 8757 · army 184059 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 98
  - NET income 2590 · trade 350 · admin 50 · tribute 895 · upkeep 2684 · blockade 219 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +9 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
  - MAILBOX #1 Prussia incoming_proposal: Prussia — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- CMD `what's my income` → ✓ The treasury holds 1,478 gold, Sire. In: the provinces 2,590, vassal tribute 895, trade 450, the administration 50. Out: the army 1,472, the surcharge above the force li…
- CMD `am I at war with Prussia` → ✓ No, Sire. France and Prussia stand at Open Borders.
- CMD `what does Austria want` → ✓ Austria pursues Redeem Italy, Sire. The priority theater of 1805 - Charles holds the main army in Italy; the losses of Campo Formio and Luneville must be undone. The pro…
- CMD `can Ney reach Vienna` → ✓ Yes, Sire — Ney can reach Vienna from Rhineland in 4 turns: Rhineland -> Swabia -> Franconia -> Bohemia -> Vienna. Mack stands on the road at Swabia — the march will mee…
- CMD `who is winning` → ✓ War score, Sire — the Third Coalition (Britain, Austria and Russia) +0 (evenly matched). The breakdown is on the ACTIVE WARS banner in the lower right (click the war).
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
- DISPATCH: Sire — St Petersburg now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 1
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_we_threshold ×2, diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `what happens if I attack Mack` → ✓ Were you to give the order, Sire:
  - ↳ MUSTER — Ney (24,000; expect about 100,011 with the corps likely to arrive, up to 107,144 if all march; certain 24,000; a bad day (1 in 10) 89,048) vs Mack (large force)…
- CMD `why not attack Mack` → ✓ Were you to give the order, Sire:
  - ↳ MUSTER — Ney (24,000; expect about 100,011 with the corps likely to arrive, up to 107,144 if all march; certain 24,000; a bad day (1 in 10) 89,048) vs Mack (large force)…
- CMD `what about attack Mack` → ✓ Were you to give the order, Sire:
  - ↳ MUSTER — Ney (24,000; expect about 100,011 with the corps likely to arrive, up to 107,144 if all march; certain 24,000; a bad day (1 in 10) 89,048) vs Mack (large force)…
- CMD `is it time to attack Mack` → ✓ Were you to give the order, Sire:
  - ↳ MUSTER — Ney (24,000; expect about 100,011 with the corps likely to arrive, up to 107,144 if all march; certain 24,000; a bad day (1 in 10) 89,048) vs Mack (large force)…
- CMD `should I attack` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
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
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - TURN EVENTS 2
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Nay attack Mack` → ✗ There is no 'Nay' in the order of battle, Sire. Whom did you intend?
- CMD `Zorglub attack Mack` → ✗ There is no 'Zorglub' in the order of battle, Sire. Whom did you intend?
- CMD `Wellington retreat` → ✗ There is no 'Wellington' in the order of battle, Sire. Whom did you intend?
- CMD `Davoust, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Rhineland. Defense bonus: +7% now, 12% at dawn (th…
- CMD `Ney, attack Mack` → ✓ Mack stands at Franconia, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Swabia, Austria's soil), or cancel?
  - POPUP clarification: Ney, pursuit_ask, Mack stands at Franconia, two marches off. Pursue him (2 AP — a standing order; the first march takes Ney to Swabia, Austria's soil), or cancel? → 1 (first option: Pursue Mack (2 AP))
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Mack attacks Bernadotte · Archduke Charles attacks Bernadotte · Archduke Charles attacks Deroy
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - ⚔ Mack (lost 2724) vs Bernadotte (lost 2675, own corps) — Ney reached Bernadotte in time, Sire — but even together, the field could not be held. — The corps system brought Ney in.
  - ⚔ Archduke Charles (lost 790) vs Bernadotte (lost 5485) — A grievous defeat for Bernadotte, Sire. The losses are severe.
  - ⚔ Archduke Charles (lost 1561) vs Deroy (lost 4123) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×3, stance_change×1, move×1, wait×1
- ORDER Ney [active]: Ney is pursuing Mack.
- LEDGER treasury 4524 · net +1465 · threat 62 · provinces 28 (+0) · ceiling 12771 · army 147308 · vassals Holland 88 · Kingdom of Italy 71 · Switzerland 80
  - NET income 2578 · trade 587 · admin 50 · tribute 802 · upkeep 1646 · charges 448 · blockade 368 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 5
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, province_changed_hands, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG moment: Britain decrees the Magazines for 8 turns (5 authority)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG ai_ai_proposal_refused: Britain rebuffs Portugal (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Davout, hold Ulm` → ✗ Region 'Ulm' not found.
- CMD `Ney, march to Swabland` → ✗ Region 'Swabland' not found. Did you mean 'Swabia'?
- CMD `halt Ney` → ✓ Ney breaks off the pursuit.
- CMD `cancel Ney` → ✓ Ney awaits further orders.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Lorraine. Defense bonus: +2% now, +5% more at the n…
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 9 actions, 4 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte · Mack attacks Munich · Mack attacks Deroy · Archduke John attacks Munich
  - 🏴 Austria: Archduke John attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1537) vs Bernadotte (lost 988, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Mack (lost 1632) vs Deroy (lost 3636) — A standard affair. Nothing unusual to report.
  - verbs: attack×4, retreat×2, unfortify×1, stance_change×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 5962 · net +1308 · threat 60 · provinces 28 (+0) · ceiling 12051 · army 141014 · vassals Holland 86 · Kingdom of Italy 69 · Switzerland 76
  - NET income 2580 · trade 587 · admin 50 · tribute 806 · upkeep 1406 · charges 851 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Bernadotte's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL third_party_peace: THE CONGRESS: Bavaria and Austria have made their peace without France. Bavaria, beaten (-41), sues for peace and Austria takes it on the held line; …
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +7 medium/low (diplomatic_we_threshold, province_changed_hands, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (76 → 86); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `retreat?` → ✓ Berthier sets down his pen. "I cannot answer that from the dispatches, Sire."
- CMD `is Swabia defended` → ✓ Swabia is Bavaria's, Sire; Ney's 20,060 stand there. No corps at war with Bavaria stands within two marches of it, so far as our intelligence reaches — it looks safe tod…
- CMD `can Davout attack Mack` → ✓ The order would be refused, Sire: Davout is fortified — unfortify first. Nothing spent.
- CMD `why did that fail` → ✓ 'can Davout attack Mack' was a question, Sire, and nothing was spent — the answer was a refusal: The order would be refused, Sire: Davout is fortified — unfortify first.…
- CMD `what can I build here` → ✓ At Rhineland we may build: supply depot (300g), fortification (400g), training ground (250g), market (350g), stables (300g).
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Milan
  - verbs: attack×1, form_square×1, move×1, wait×1
- LEDGER treasury 7070 · net +854 · threat 58 · provinces 28 (+0) · ceiling 10986 · army 140189 · vassals Holland 86 · Kingdom of Italy 69 · Switzerland 85
  - NET income 2582 · trade 587 · admin 50 · tribute 574 · upkeep 1376 · charges 1105 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — St Petersburg now pays Sweden 200 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 5 turns (5 DP); buying off her design …
  - TURN EVENTS 4
- DIPLO +2 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG third_party_peace: THE CONGRESS: Bavaria and Austria make peace without France
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 7 — Late December 1805
- CMD `Murat, drill` → ✗ Murat cannot drill with enemy forces nearby! Archduke John is at Munich, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Bernadotte, scout Franconia` → ✗ Bernadotte is recovering from retreat and cannot scout. Recovery: 1 turn remaining.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Milan
  - 🏴 Austria: Archduke John attacks Milan — The garrison of Milan is destroyed. · Region captured: Milan (was Kingdom of Italy) (secured)
  - verbs: attack×1, wait×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 7850 · net +591 · threat 56 · provinces 28 (+0) · ceiling 10521 · army 139381 · vassals Holland 86 · Kingdom of Italy 69 · Switzerland 84
  - NET income 2583 · trade 587 · admin 50 · tribute 487 · upkeep 1364 · charges 1294 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Milan has been taken by Austria.
  - TURN EVENTS 6
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor
  - LOG moment: Russia decrees the Magazines for 8 turns (5 authority)

## Turn 8 — Early January 1806
  - MAILBOX #9 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #10 → reject_ai_proposal
- CMD `flurble the wibble` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — 'Massena, attack Archduke John…
- CMD `Ney, never attack Mack` → ✗ Berthier lowers the dispatch. "Then no order goes out, Sire — I have relayed nothing. If a standing order is to be stood down, say 'cancel his order'; otherwise tell me …
- CMD `Ney, attack if Davout supports` → ✗ Berthier sets down his pen. "Sire, that is a contingency, not an order — I have no way to hold a dispatch until 'if Davout supports' comes to pass. Nothing has been rela…
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at M…
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Milan instead.) → trust
  - ↳ MUSTER — Massena (19,865) vs Archduke John (11,633 men) at Milan — the balance of force looks even — a hard fight that may well decide nothing.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 4360) vs Archduke John (lost 815) — Massena's corps broke, Sire. They are streaming back from the field.
- CMD `what now` → ✓ These orders would be carried out today, Sire:
  - ↳ Ney, march to Munich / Davout, unfortify
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1
- LEDGER treasury 8161 · net +390 · threat 44 · provinces 28 (+0) · ceiling 9867 · army 134229 · vassals Holland 84 · Switzerland 81
  - NET income 2585 · trade 587 · admin 50 · tribute 337 · upkeep 1304 · charges 1407 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 63 Reliable glory 0 (#7) vind -1 · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL nation_eliminated: Sire — the Kingdom of Italy has been eliminated from the war.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,272g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 7
- DIPLO +5 medium/low (law_enacted_abroad ×2, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (design ask)
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 9 — Late January 1806
- CMD `quickly attack Mack` → ✗ No marshals in range of Mack
- CMD `immediately attack Mack` → ✗ No marshals in range of Mack
- CMD `ok retreat` → ✓ General retreat ordered! Teulie falling back!
- CMD `tonight Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Swa…
- CMD `someone attack Mack` → ✗ No marshals in range of Mack
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke John attacks Provence
  - 🏴 Austria: Archduke Charles attacks Massena — Lyonnais CAPTURED! (was France) (secured)
  - 🏴 Austria: Archduke John attacks Provence — Region captured: Provence (was France) (secured)
  - ⚔ Archduke Charles (lost 325) vs Massena (lost 7323) — Massena's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, move×1, wait×1
- LEDGER treasury 8064 · net +181 · threat 41 · provinces 26 (-2) · ceiling 8816 · army 126130 · vassals Holland 82 · Switzerland 78
  - NET income 2356 · trade 587 · admin 50 · tribute 337 · upkeep 1236 · charges 1455 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 63 Reliable glory 0 (#7) vind -1 · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Lyonnais has fallen to Austria. Enemy colours fly over French homeland soil. Archduke Charles's corps of 25,760 stands there. A garrison you detach (3,000 men) holds a province against a march…
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 6,000 men ashore at Piedmont.
  - RAIL allegiance_settled: The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 7
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- DIPLO +6 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 35% of active European bloc power.
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG nation_eliminated: The Kingdom of Italy has been eliminated from the war.
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)

## Turn 10 — Early February 1806
- CMD `cavalry attack Mack` → ✓ Murat firmly objects: 'An attack on Mack, Sire? There is no battle in it. Give me the enemy.' (Trust him and he will defend at Franche-Comte instead.)
  - POPUP objection: Murat, Murat firmly objects: 'An attack on Mack, Sire? There is no battle in it. Give me the enemy.' (Trust him and he will defend at Franche-Comte instead.) → trust
- CMD `guards attack Mack` → ✓ Murat hesitates briefly but follows orders. Berthier stays the order a moment, Sire: before Murat marches on Mack, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Mack, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Murat attacks Mack' to read the muster before you commit — it costs nothing.
MUSTER — Murat (20,693) vs Mack (large force) at Tyrol — the balance of force looks unfavorable.
  Standing modifiers, already in the band: Murat attacks from a defensive stance (−10%); the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 20,693 we muster) would cost ~155g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 41/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
- CMD `Marshal attack Mack` → ✓ Berthier stays the order a moment, Sire: before Murat marches on Mack, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Mack, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Murat attacks Mack' to read the muster before you commit — it costs nothing.
MUSTER — Murat (20,693) vs Mack (large force) at Tyrol — the balance of force looks unfavorable.
  Standing modifiers, already in the band: Murat attacks from a defensive stance (−10%); the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 20,693 we muster) would cost ~155g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 41/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
- CMD `anyone scout Swabia` → ✓ Ney scouts Swabia: Controlled by Bavaria. Terrain: Plains. No enemy forces detected.
- CMD `right, attack Mack` → ✓ Berthier stays the order a moment, Sire: before Murat marches on Mack, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Mack, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Murat attacks Mack' to read the muster before you commit — it costs nothing.
MUSTER — Murat (20,693) vs Mack (large force) at Tyrol — the balance of force looks unfavorable.
  Standing modifiers, already in the band: Murat attacks from a defensive stance (−10%); the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 20,693 we muster) would cost ~155g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 41/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP) and he stands apart until you move him. → attack_anyway
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 8 actions, 2 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke John attacks Languedoc
  - 🏴 Britain: Shrapnel moves to Burgundy — Burgundy falls (was France) and is secured
  - 🏴 Britain: Shrapnel moves to Champagne — Champagne falls (was France) and is secured
  - 🏴 Austria: Archduke John attacks Languedoc — Region captured: Languedoc (was France) (secured)
  - ⚔ Archduke Charles (lost 168) vs Massena (lost 3788) — The toll on Massena's forces is heavy, Sire. This defeat will be felt.
  - verbs: move×4, attack×2, wait×1, recruit×1
- ORDER Massena [awaiting_response]: Massena is cornered at Limousin with 4,394 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the …
  - POPUP strategic_interrupt: Massena, last_stand, Massena is cornered at Limousin with 4,394 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 7447 · net -290 · threat 38 · provinces 23 (-3) · ceiling 6406 · army 117187 · vassals Holland 80 · Switzerland 75
  - NET income 2171 · trade 587 · admin 50 · tribute 337 · upkeep 1152 · charges 1522 · contributions 303 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 78 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena captured · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Burgundy has fallen to Britain. Enemy colours fly over French homeland soil.
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War for Burgundy — Britain + Austria + Russia. Asking 2750 gold.
  - TURN EVENTS 7
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: And Saxony stirs at its own design.
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 11 — Late February 1806
  - MAILBOX #10 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #11 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace, gold_indemnity
  - POPUP diplomatic_dialogue: settlement_confirm #12 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Burgundy — the table with Austria + Russia (2 pairs resolved). Status quo: Languedoc, Lyonnais and Provence stay Austrian by the treaty. Prisoners: Massena comes home to Paris under this peace. Prisoners: Teulie comes home to Paris under this peace. → display-only
- CMD `Zorglub pull back` → ✗ There is no 'Zorglub' in the order of battle, Sire. Whom did you intend?
- CMD `Zorglub recon Swabia` → ✗ There is no 'Zorglub' in the order of battle, Sire. Whom did you intend?
- CMD `all marshals, attack` → ✓ Which marshal shall lead the attack, Sire?
  - POPUP clarification: Berthier, marshal_choice, Which marshal shall lead the attack, Sire? → 1 (first option: Massena)
  - ↳ MUSTER — Massena (5,000) vs Shrapnel (4,837 men) at Paris — the balance of force looks even — a hard fight that may go against us.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 821) vs Shrapnel (lost 368) — The margin was slim. Training and preparation would serve Massena well. — The Line Holds +15% (Shrapnel)
- CMD `whoever is closest attack Mack` → ✗ Murat cannot attack — our peace with Austria is fresh: no war may be declared on her for 5 more turns. Nothing spent.
- CMD `well retreat` → ✗ No marshals are in danger. None need to retreat.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 actions unused) Turn 12 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Shrapnel · Cuesta attacks Shrapnel
  - 🏴 Spain: Cuesta attacks Shrapnel — Champagne CAPTURED! (was Britain)
  - ⚔ Castanos (lost 403) vs Shrapnel (lost 1181) — The engagement proceeded as one might expect, Sire. — The Line Holds +15% (Shrapnel)
  - ⚔ Cuesta (lost 71, own corps) vs Shrapnel (lost 2052) — Shrapnel's army has been badly mauled. Cuesta proved the stronger force today. And Shrapnel was taken on that field — S… — The Line Holds +15% (Shrapnel)
  - verbs: attack×2, recruit×2, move×1, wait×1
- LEDGER treasury 5525 · net +670 · threat 17 · provinces 24 (+1) · ceiling 8603 · army 125621 · vassals Holland 78 · Switzerland 72
  - NET income 2165 · trade 587 · admin 50 · tribute 337 · upkeep 1244 · charges 767 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 78 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 63 Reliable glory 0 (#7) vind -1 · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Marshal Massena has been taken. Austria holds him prisoner.
  - RAIL status_quo_conceded: Languedoc, Lyonnais and Provence — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of the War for Burgundy — the table with Austria + Russia: Gold indemnity: 2750 gold from France to Austria.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 5
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_coalition_dissolved, province_changed_hands, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 38 to 19; Britain remains at war with us.
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: 3 approaches from Sardinia, Saxony and Prussia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

## Turn 12 — Early March 1806
- CMD `Ney attack Mack?` → ✗ Ney is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Davout fortify?` → ✗ Davout is already fortified at Rhineland (+11% defense).
- CMD `Soult scout Swabia?` → ✓ Soult scouts Swabia: Controlled by Bavaria. Terrain: Plains. No enemy forces detected.
- CMD `Murat drill?` → ✓ Murat begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 8 actions, 1 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight. — Brunswick attacks Wallmoden
  - ⚔ Brunswick (lost 374) vs Wallmoden (lost 1157) — A grievous defeat for Wallmoden, Sire. The losses are severe. — Frederick's Drill +10% (Brunswick)
  - verbs: wait×2, recruit×2, attack×1, fortify×1, retreat×1, stance_change×1
- ENVOYS WAITING 2 · Britain settlement offer · The Secretariat moment letter
- LEDGER treasury 6234 · net +541 · threat 15 · provinces 25 (+1) · ceiling 8687 · army 124891 · vassals Holland 78 · Switzerland 71
  - NET income 2182 · trade 587 · admin 50 · tribute 337 · upkeep 1224 · charges 933 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 63 Reliable glory 0 (#7) vind -1 · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Languedoc, Lyonnais and Provence lie in enemy hands. Austria holds them.
  - RAIL settlement_offer_arrival: Britain's terms to settle the War with Britain, under Russia's good offices.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, agenda_shift ×2)
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG moment: The Squadron for Santo Domingo — an affair of state is laid before the Emperor

---
finished: **completed** · commands 70 · popups 25 · battles 20
