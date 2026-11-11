# Playtest digest — played-occupier

seed `distant-hussar-64` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "client_petition": "refuse"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `distant-hussar-64` · dice `distant-hussar-64`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `b9172fa0dcf1` (dirty) · content `376b0b62dbd1` · driver `33b559af18c1`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1803, own corps) vs Mack (lost 22726) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Murat, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena
  - ⚔ Archduke Charles (lost 4240) vs Massena (lost 6081) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - TERMS (incoming open_borders from Prussia): Proposal: Open Borders Agreement · Clause: Open borders - each side's armies may cross the other's provinces — but not a province she has declared guarded… · Prussia pays you 30 gold at the signing
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. Prussia paid 30 gold into the treasury. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Saxony open borders
- LEDGER treasury 470 · net +209 · threat 72 · provinces 28 · ceiling 3536 · army 173058 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 3386 · blockade 250 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 1 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — General Mack of Austria is taken at Swabia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - POLICY decline_from -> Austria,Britain,Russia
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Davout, attack Archduke Charles` → ✓ Archduke Charles stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Davout, pursuit_ask, Archduke Charles stands at Tyrol, two marches off. Pursue him (2 AP — a standing order; the first march takes Davout to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (2 AP))
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (900 lost to march)
- CMD `Massena, attack Archduke John` → ✓ Berthier stays the order a moment, Sire: before Massena marches on Archduke John, read the muster.
  - POPUP strategic_interrupt: Massena, muster_confirm, Berthier stays the order a moment, Sire: before Massena marches on Archduke John, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Massena attacks Archduke John' to read the muster before you commit — it costs nothing.
MUSTER — Massena (35,919; expect about 65,398 with the corps likely to arrive, up to 66,115 if all march; certain 35,919) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
  WILL JOIN — Davout: marches under your written support order — his pursuit of Archduke Charles waits a day — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Tyrol
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Massena') would likely bring him
  WILL JOIN — Teulie: will march to the sound of the guns — likely to make it in time (about 98%) (The corps system lowers the bar by 10) — and will stand at Tyrol
  Archduke John does not stand alone: at least 1 enemy corps within reach of Tyrol would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: the ground favors the defender (+25%, mountains).
  What Tyrol can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 66,634 we muster) would cost ~500g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 72/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (2 AP from a neutral stance — 1 to stand defensive, 1 to fortify) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Massena (35,919; expect about 65,398 with the corps likely to arrive, up to 66,115 if all march; certain 35,919) vs Archduke John (substantial force) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 4686, own corps) vs Archduke John (lost 2169, own corps) — Davout and Teulie arrived to reinforce Massena, but Bernadotte failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke Charles attacks Teulie · Archduke Charles attacks Munich
  - ⚔ Archduke Charles (lost 3702) vs Massena (lost 4227, own corps) — Neither Massena nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Archduke Charles (lost 2308) vs Teulie (lost 1443, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×3, stance_change×1, wait×1
- ORDER Davout [active]: Davout is pursuing Archduke Charles.
- ENVOYS WAITING 2 · Portugal open borders · Denmark open borders
- LEDGER treasury 260 · net +606 · threat 70 · provinces 28 (+0) · ceiling 5894 · army 151895 · vassals Holland 98 · Kingdom of Italy 95 · Switzerland 95
  - NET income 2590 · trade 450 · admin 50 · tribute 833 · upkeep 2946 · blockade 281 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 1 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Ney, Soult, Lannes, Murat and Napoleon stand 90,943 men at Swabia, which feeds 60,000. 30,943 too many. 9,285 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply t…
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Prussia and Russia sign an Open Borders Agreement
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Portugal: Open Borders Agreement → accept
  - LETTER Denmark: Open Borders Agreement → accept
- CMD `Soult, attack Archduke Charles` → ✓ Archduke Charles stands at Tyrol, two marches off. Pursue him (1 AP — a standing order; the first march takes Soult to Franconia, Bavaria's soil), or cancel?
  - POPUP clarification: Soult, pursuit_ask, Archduke Charles stands at Tyrol, two marches off. Pursue him (1 AP — a standing order; the first march takes Soult to Franconia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke Charles (1 AP))
- CMD `Massena, attack Archduke John` → ✓ MUSTER — Massena (23,324; expect about 83,658 with the corps likely to arrive, up to 86,201 if all march; certain 23,324) vs Archduke John (16,877 men) at Tyrol — the ba…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 2195, own corps) vs Archduke John (lost 2421, own corps) — Davout, Soult and Teulie's timely arrival aided Massena. Bernadotte, however, was conspicuously absent. — Berthier: the corps marched apart and arrived together.
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- enemy phase: 10 actions, 4 attacks — Russia, Prussia, Spain and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Massena · Archduke Charles attacks Teulie · Archduke Charles attacks Munich · Deroy attacks Archduke John
  - 🏴 Austria: Archduke Charles attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 2170) vs Massena (lost 2580, own corps) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 1076) vs Teulie (lost 1234, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Deroy (lost 2288) vs Archduke John (lost 1629) — Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty.
  - verbs: attack×4, stance_change×1, fortify×1, naval_expedition×1, form_square×1, move×1, wait×1
- ORDER Davout [active]: Davout answered the guns this turn and stands at Franconia; the pursuit resumes next turn.
- ORDER Soult [active]: Soult is pursuing Archduke Charles.
- ORDER Teulie [awaiting_response]: Teulie is cornered at Milan with 3,061 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last…
  - POPUP strategic_interrupt: Teulie, last_stand, Teulie is cornered at Milan with 3,061 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 781 · net +1057 · threat 68 · provinces 28 (+0) · ceiling 8188 · army 135844 · vassals Holland 96 · Kingdom of Italy 90 · Switzerland 91
  - NET income 2590 · trade 500 · admin 50 · tribute 799 · upkeep 2480 · blockade 312 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 1 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL question_turns: THE GERMAN QUESTION TURNS: Austria holds Munich; Berlin watches. Who speaks for Germany?
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Munich. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +8 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG guarantee_pledged: Prussia guarantees Bavaria against Austria's appetite
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (18,893; expect about 107,599 with the corps likely to arrive, up to 116,996 if all march; certain 32,594; a bad day (1 in 10) 88,053) vs Archduke Charles (…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 693, own corps) vs Archduke Charles (lost 11584) — Davout, Soult, Lannes, Murat and Napoleon's timely arrival aided Ney. Bernadotte, however, was conspicuously absent. — Munich, Bavaria's capital, retaken — handed back to Bavaria. The last 2,000 of the garrison at Munich give way. — Berthier: the corps marched apart and arrived together.
- CMD `Massena, drill` → ✗ Massena is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 3 actions unused) Turn 5 begins!
- enemy phase: 4 actions, 0 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, unfortify×1, form_square×1, wait×1
- ORDER Davout [active]: Davout answered the guns this turn and stands at Munich; the pursuit resumes next turn.
- ORDER Soult [active]: Soult answered the guns this turn and stands at Munich; the pursuit resumes next turn.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- ENVOYS WAITING 1 · Saxony non aggression
- LEDGER treasury 2100 · net +1270 · threat 74 · provinces 28 (+0) · ceiling 9312 · army 127013 · vassals Holland 97 · Kingdom of Italy 80 · Switzerland 90
  - NET income 2590 · trade 575 · admin 50 · tribute 802 · upkeep 2280 · charges 17 · blockade 360 · admiralty 90
- MARSHALS Ney trust 75 Reliable glory 3 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 75 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — General Teulie has been taken. Austria holds him prisoner.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (300g/turn)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Munich — Austria is not forgiven
  - LOG moment: Britain decrees the Magazines for 8 turns (5 authority)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 5 — Late November 1805
  - LETTER Saxony: Non-Aggression Pact → accept
- CMD `Lannes, attack Archduke Charles` → ✓ MUSTER — Lannes (13,412; expect about 97,787 with the corps likely to arrive, up to 98,193 if all march; certain 80,905) vs Archduke Charles (10,580 men) at Tyrol — the …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 319, own corps) vs Archduke Charles (lost 6698, own corps) — Reinforcements from Ney, Davout, Soult, Bernadotte and Napoleon bolstered Lannes's position — though Murat never arrive… — The corps system brought Ney in. — Berthier: the corps marched apart and arrived together.
  - POPUP capture_choice[capture]: Tyrol, Lannes → secure
- CMD `Soult, attack Archduke John` → ✓ MUSTER — Soult (22,509; expect about 34,450 with the corps likely to arrive) vs Archduke John (small force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 140, own corps) vs Archduke John (lost 4328) — Lannes arrived to reinforce Soult! The timely arrival swung the battle in our favor, Sire. And Archduke John was taken …
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 4 actions, 0 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, unfortify×1, wait×1
- ORDER Davout [active]: Davout answered the guns this turn and stands at Tyrol; the pursuit resumes next turn.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: Ney turns openly discontent (trust -3; expect defiance).
- ENVOYS WAITING 2 · Denmark non aggression · KingdomOfItaly client petition
- LEDGER treasury 4434 · net +1913 · threat 85 · provinces 29 (+1) · ceiling 13560 · army 120977 · vassals Holland 99 · Kingdom of Italy 82 · Switzerland 90
  - NET income 2611 · trade 587 · admin 50 · tribute 806 · upkeep 1148 · charges 510 · requisitions 50 · occupation 75 · blockade 368 · admiralty 90
- MARSHALS Ney trust 72 Reliable glory 3 (#1) · Davout trust 85 Loyal glory 0 (#4) · Soult trust 70 Reliable glory 2 (#2) · Lannes trust 85 Loyal glory 2 (#3) · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — the Archduke John of Austria is taken at Bohemia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 6
- DIPLO +7 medium/low (diplomatic_treaty_signed, law_enacted_abroad ×2, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, diplomatic_ai_ai_treaty)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Sweden against France (200g/turn)
  - LOG diplomatic_ai_ai_treaty: Austria and the Ottoman Empire sign a Non-Aggression Pact
  - LOG moment: Russia decrees the Magazines for 8 turns (5 authority)
  - LOG diplomatic_ai_ai_treaty: Sweden and Russia sign an Open Borders Agreement
  - LOG diplomatic_ai_ai_treaty: Naples and Russia sign an Open Borders Agreement

## Turn 6 — Early December 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - MAILBOX #10 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - TERMS (incoming client_petition from KingdomOfItaly): Grant it, and Tyrol passes to the Kingdom of Italy: loyalty +10, its bond with us rises 0 → 20 (worth +1 a turn in loya… · Refuse it, and the Kingdom of Italy loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #13 → refuse the petition
  - POPUP proposal_result: The Kingdom of Italy's petition for Tyrol is refused: loyalty −10 (82 → 72); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- CMD `Soult, attack Archduke Charles` → ✓ MUSTER — Soult (21,561; expect about 63,326 with the corps likely to arrive, up to 63,589 if all march; certain 52,396) vs Archduke Charles (9,882 men) at Bohemia — the …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 265, own corps) vs Archduke Charles (lost 5839) — Davout and Napoleon arrived to reinforce Soult, but Ney and Bernadotte failed to reach the field in time. And Archduke … — The corps system brought Davout in.
  - POPUP capture_choice[capture]: Bohemia, Soult → secure
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Tyrol to Bohemia (156 lost to march)
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Spain and 3 other courts stirred, but their formations remain beyond our sight.
- ORDER Davout [completed]: Archduke Charles taken prisoner Davout: "Accomplished as ordered. The army is intact."
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 6300 · net +1482 · threat 88 · provinces 30 (+1) · ceiling 13264 · army 117123 · vassals Holland 100 · Kingdom of Italy 72 · Switzerland 89
  - NET income 2654 · trade 599 · admin 50 · tribute 842 · upkeep 1108 · charges 915 · occupation 175 · blockade 375 · admiralty 90
- MARSHALS Ney trust 69 Reliable glory 3 (#1) · Davout trust 85 Loyal glory 0 (#4) · Soult trust 70 Reliable glory 3 (#2) · Lannes trust 85 Loyal glory 2 (#3) · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — the Archduke Charles of Austria is taken at Bohemia — he is our prisoner, and their order of battle is one commander shorter.
  - EXPECTS: Soult's victories raise his expectation — he now looks for 40g/turn (holds 0g).
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG ai_ai_proposal_refused: Prussia rebuffs Saxony (design ask)

## Turn 7 — Late December 1805
  - MAILBOX #11 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - TERMS (incoming client_petition from Switzerland): Grant it, and Switzerland's tribute of 225g a turn is remitted for 8 collections (1800g forgone): loyalty +10, its bond… · Refuse it, and Switzerland loses 10 loyalty and its bond with us falls 20 (0 → -20: worth -1 a turn in loyalty, now +0)… ·
  - POPUP diplomatic_dialogue: Switzerland, client_petition #15 → refuse the petition
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (89 → 79); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- CMD `Ney, attack Kutuzov` → ✓ MUSTER — Ney (14,804; expect about 54,449 with the corps likely to arrive, up to 56,753 if all march; certain 14,804; a bad day (1 in 10) 45,660) vs Kutuzov (substantial…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1521, own corps) vs Kutuzov (lost 6052) — Davout, Lannes and Napoleon arrived in time to steady Ney's position. The field was held, nothing further.
- CMD `Lannes, attack Bohemia` → ✗ Bohemia is already controlled by France
- CMD `Murat, move to Tyrol` → ✓ Murat moves from Munich to Tyrol (341 lost to march)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Austria, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×4
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
  - POPUP diplomatic_dialogue: moment_letter #16 → reject_ai_proposal
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 7946 · net +1433 · threat 86 · provinces 30 (+0) · ceiling 14459 · army 109432 · vassals Holland 100 · Kingdom of Italy 71 · Switzerland 76
  - NET income 2702 · trade 599 · admin 50 · tribute 847 · upkeep 840 · charges 1308 · occupation 152 · blockade 375 · admiralty 90
- MARSHALS Ney trust 69 Reliable glory 3 (#1) · Davout trust 85 Loyal glory 0 (#4) · Soult trust 70 Reliable glory 3 (#2) · Lannes trust 85 Loyal glory 2 (#3) · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) envies Lannes · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Ney, Davout, Soult, Lannes and Napoleon stand 62,716 men at Bohemia, which feeds 60,000. 2,716 too many. 6,599 men lost in 3 turns. No depot may be laid at Bohemia — no building slots availabl…
  - RAIL allegiance_settled: The moment passes: Sardinia no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 4
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_we_threshold, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven

## Turn 8 — Early January 1806
- CMD `Davout, attack Kutuzov` → ✓ Davout notes the risks but prepares the attack. MUSTER — Davout (13,990; expect about 51,128 with the corps likely to arrive, up to 53,053 if all march; certain 13,990; …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1428, own corps) vs Kutuzov (lost 2645, own corps) — Ney, Lannes and Napoleon arrived in time to steady Davout's position. The field was held, nothing further.
- CMD `Murat, attack Carniola` → ✓ Murat marches from Tyrol into Carniola unopposed! (197 lost to march) Captured: Austria → France
  - POPUP capture_choice[capture]: Carniola, Murat → secure
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 2 actions unused) Turn 9 begins!
- enemy phase: 7 actions, 0 attacks — Britain, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×3, stance_change×2, wait×2
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 9339 · net +1200 · threat 86 · provinces 31 (+1) · ceiling 14636 · army 103216 · vassals Holland 100 · Kingdom of Italy 70 · Switzerland 73
  - NET income 2831 · trade 599 · admin 50 · tribute 851 · upkeep 808 · charges 1661 · occupation 197 · blockade 375 · admiralty 90
- MARSHALS Ney trust 69 Reliable glory 2 (#2) · Davout trust 85 Loyal glory 0 (#4) · Soult trust 70 Reliable glory 3 (#1) · Lannes trust 85 Loyal glory 2 (#3) · Murat trust 72 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) envies Lannes · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Carniola has fallen to our arms. The tricolor flies over it this morning.
  - UNMET: Soult expects 40g/turn, holds 0g — patience holds 2 more turns
  - RAIL settlement_offer_arrival: Austria has offered terms to settle the War for Bohemia — Britain + Austria + Russia. Offering 3090 gold. Its articles: Austria's design pointed else…
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,308g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 9 — Late January 1806
  - MAILBOX #13 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → reject_settlement_offer
- CMD `Soult, attack Vienna` → ✓ MUSTER — Soult (18,754; expect about 50,988 with the corps likely to arrive, up to 52,170 if all march; certain 24,231; a bad day (1 in 10) 44,783) vs Kutuzov (22,727 me…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 1706, own corps) vs Kutuzov (lost 3054, own corps) — Ney, Davout, Lannes and Napoleon arrived in time to steady Soult's position. The field was held, nothing further. — The corps system brought Ney in.
- CMD `Bernadotte, attack Hungary` → ✗ Bernadotte cannot reach Hungary from Tyrol! Range: 1, Distance: 2
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Deroy attacks Hiller · Deroy attacks Liechtenstein
  - ⚔ Deroy (lost 971) vs Hiller (lost 1210, own corps) — Hiller's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Deroy (lost 744) vs Liechtenstein (lost 1812, own corps) — Liechtenstein's army has been badly mauled. Deroy proved the stronger force today. And Liechtenstein was taken on that …
  - verbs: attack×2, unfortify×1, wait×1, move×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
  - TERMS (incoming armistice_losing from Russia): Proposal: Armistice
  - POPUP diplomatic_dialogue: Russia, armistice_losing #20 → reject_ai_proposal
  - POPUP proposal_result: You have rejected Russia's proposal. Talleyrand will convey your decision. → display-only
- ENVOYS WAITING 1 · Russia armistice losing
- LEDGER treasury 10442 · net +962 · threat 84 · provinces 31 (+0) · ceiling 14573 · army 96742 · vassals Holland 100 · Kingdom of Italy 69 · Switzerland 70
  - NET income 2836 · trade 599 · admin 50 · tribute 856 · upkeep 752 · charges 1965 · occupation 197 · blockade 375 · admiralty 90
- MARSHALS Ney trust 69 Reliable glory 2 (#2) envies Soult · Davout trust 85 Loyal glory 0 (#4) · Soult trust 70 Reliable glory 3 (#1) · Lannes trust 85 Loyal glory 2 (#3) · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - UNMET: Soult expects 40g/turn, holds 0g — patience holds 1 more turn
  - RAIL diplomatic_ai_proposal: An envoy from Russia has arrived with a proposal.
  - TURN EVENTS 9
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- COURTS: And Denmark stirs at its own design.
- DIPLO +5 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain binds Russia to the war against France — no separate peace for 10 turns (300g/turn)
  - LOG ai_proposal_rejected: We rejected Russia's armistice proposal

## Turn 10 — Early February 1806
- CMD `Ney, attack Vienna` → ✓ MUSTER — Ney (10,395; expect about 34,741 with the corps likely to arrive, up to 36,155 if all march; certain 10,395; a bad day (1 in 10) 29,372) vs Kutuzov (19,673 men)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1375, own corps) vs Kutuzov (lost 2795, own corps) — Davout, Lannes and Napoleon reached the field beside Ney, Sire — it saved the line, no more.
- CMD `Lannes, attack Moravia` → ✗ Lannes cannot reach Moravia from Bohemia! Range: 1, Distance: 2
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×3
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 11671 · net +1092 · threat 84 · provinces 31 (+0) · ceiling 16890 · army 90619 · vassals Holland 100 · Kingdom of Italy 68 · Switzerland 67
  - NET income 2942 · trade 599 · admin 50 · tribute 860 · upkeep 712 · charges 2023 · occupation 159 · blockade 375 · admiralty 90
- MARSHALS Ney trust 69 Reliable glory 2 (#2) envies Bernadotte · Davout trust 85 Loyal glory 0 (#4) · Soult trust 69 Reliable glory 3 (#1) · Lannes trust 85 Loyal glory 2 (#3) · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) envies Lannes · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured · Pino trust 60 Questioning glory 0
- DISPATCH: Sire — Prussia would now join a league against us — relations −25. A league stands declared without her; she would march in the next — the price to keep her out: Talleyrand brings her to −10 in 2 tur…
  - UNMET: Soult expects 40g/turn, holds 0g — loyalty eroding
  - TURN EVENTS 7
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 11 — Late February 1806
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 actions unused) Turn 12 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×2, wait×2, fortify×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 1016, own corps) vs Bennigsen (lost 503, own corps) — Reinforcement from Davout, Lannes and Napoleon kept Ney standing, Sire — but neither side yielded the ground.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 12760 · net +935 · threat 84 · provinces 31 (+0) · ceiling 17116 · army 85737 · vassals Holland 100 · Kingdom of Italy 67 · Switzerland 64
  - NET income 2995 · trade 599 · admin 50 · tribute 865 · upkeep 664 · charges 2306 · occupation 139 · blockade 375 · admiralty 90
- MARSHALS Ney trust 69 Reliable glory 0 (#3) envies Soult · Davout trust 85 Loyal glory 0 (#4) · Soult trust 68 Reliable glory 3 (#1) · Lannes trust 85 Loyal glory 2 (#2) · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) envies Lannes · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie captured · Pino trust 60 Questioning glory 0
- DISPATCH: Sire — not every court of the league has struck us. Austria has an open road to us — 1 march — and has not struck us. Britain has no road to us but the sea, and Normandy is a defended shore: she can …
  - UNMET: Soult expects 40g/turn, holds 0g — loyalty eroding
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 8
- DIPLO +5 medium/low (law_enacted_abroad ×2, province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

---
finished: **completed** · commands 37 · popups 43 · battles 20
