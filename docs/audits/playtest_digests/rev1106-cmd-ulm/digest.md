# Playtest digest — rev1106-cmd-ulm

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `ad73ba09665e` · content `e9a73e243b18` · driver `98b323710bf7`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 106,545 with the corps likely to arrive, up to 114,642 if all march; certain 24,000; a bad day (1 in 10) 94,017) vs Mack (large force)…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2125, own corps) vs Mack (lost 20983) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Murat and Bernadotte never arrived, S… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 2753) vs Bernadotte (lost 4169, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - verbs: move×1, attack×1, retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. Prussia paid 30 gold into the treasury. → display-only
- ENVOYS WAITING 2 · Prussia open borders · Ottoman open borders
- LEDGER treasury 950 · net +687 · threat 72 · provinces 28 · ceiling 7066 · army 175742 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 937 · upkeep 2950 · blockade 250 · admiralty 90
- DISPATCH: Sire — London now pays St Petersburg 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG moment: Britain decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Russia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Austria decrees the Remounts for 8 turns (3 authority)
  - LOG moment: Prussia decrees the Remounts for 8 turns (3 authority)
  - LOG moment: The Ottoman Empire decrees the Remounts for 8 turns (3 authority)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (19,309; expect about 115,278 with the corps likely to arrive, up to 120,589 if all march; certain 19,309; a bad day (1 in 10) 102,177) vs Mack (substantial…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 438, own corps) vs Mack (lost 27183) — Davout, Massena and Napoleon arrived to reinforce Ney, but Teulie failed to reach the field in time. And Mack was taken… — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 actions unused) Turn 3 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte · Archduke Charles attacks Deroy · Archduke Charles attacks Murat
  - 🏴 Austria: Archduke Charles attacks Bernadotte — Franconia CAPTURED! (was Bavaria) (secured)
  - 🏴 Austria: Archduke Charles attacks Deroy — Swabia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1147) vs Bernadotte (lost 6916) — Where was Ney? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 1337) vs Deroy (lost 9004) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 2319) vs Murat (lost 5509) — Murat stood alone, Sire. Ney never came.
  - verbs: attack×3, wait×1
- ENVOYS WAITING 2 · Naples open borders · Portugal open borders
- LEDGER treasury 1191 · net +900 · threat 78 · provinces 28 (+0) · ceiling 6955 · army 155351 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 92
  - NET income 2575 · trade 425 · admin 50 · tribute 937 · upkeep 2666 · contributions 65 · blockade 266 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia eases over The Hanoverian Prize — joining the stronger side for pay is now the length of its tether.
- DIPLO +9 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold ×2, law_enacted_abroad, province_changed_hands ×2, diplomatic_dp_regen, agenda_shift)

## Turn 3 — Late October 1805
  - LETTER Naples: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia. Swabia, Bavaria's province, retaken — handed back to Bavaria. (168 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 716 gold (×3 at war) (×1.19 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 actions unused) Turn 4 begins!
- SPENT 716g on this turn's orders
- enemy phase: 8 actions, 0 attacks — Russia, Prussia, Spain and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×2, wait×2, fortify×1, naval_expedition×1, retreat×1, move×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1821, own corps) vs Archduke Charles (lost 9599) — Lannes, Massena and Napoleon arrived to reinforce Murat, but Ney and Davout failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2107 · net +1769 · threat 76 · provinces 28 (+0) · ceiling 13326 · army 147754 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 91
  - NET income 2561 · trade 475 · admin 50 · tribute 937 · upkeep 1850 · charges 16 · blockade 298 · admiralty 90
- DISPATCH: Sire — Ney, Davout and Bernadotte stand 43,792 men at Munich, which feeds 37,500. 6,292 too many. 6,911 men lost in 2 turns. Bavaria's magazines feed us as our own — the army is simply too large for …
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - RAIL agenda_violation: Portugal seethes: Britain's columns cross Lisbon in defiance of its declared neutrality.
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain rebuffs Sweden, Naples and Portugal (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Munich. Defense bonus: +7% now, 12% at dawn (the m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4072 · net +1572 · threat 74 · provinces 28 (+0) · ceiling 13847 · army 144323 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 89
  - NET income 2562 · trade 550 · admin 50 · tribute 937 · upkeep 1760 · charges 333 · blockade 344 · admiralty 90
- DISPATCH: Sire — Lannes, Murat, Massena and Napoleon stand 67,531 men at Franche-Comte, which feeds 52,500. 15,031 too many. 7,321 men lost in 3 turns. No depot may be laid at Franche-Comte — town regions don'…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 5 — Late November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Ney marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Ney, muster_confirm, Berthier stays the order a moment, Sire: before Ney marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Ney attacks Archduke Charles' to read the muster before you commit — it costs nothing.
MUSTER — Ney (16,987) vs Archduke Charles (substantial force) at Franconia — the balance of force looks unfavorable.
  WILL NOT — Davout: is dug in and will not abandon his works
  WILL NOT — Bernadotte: hesitates — the I Corps weighs its own ambitions — a written order ('Bernadotte, support Ney') would likely bring him
  What Franconia can feed is not known — the province is unscouted.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 16,987 we muster) would cost ~127g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 74/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP; 2 for Bernadotte, who stands neutral) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Ney (16,987) vs Archduke Charles (substantial force) at Franconia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 4565) vs Archduke Charles (lost 1613) — Not one corps reached Ney. Bernadotte was expected; Ney fought the battle single-handed.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (130 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 7 actions, 1 attacks — Russia, Prussia, Spain and 6 other courts stirred as well, but their formations remain beyond our sight. — Archduke John attacks Teulie
  - ⚔ Archduke John (lost 966) vs Teulie (lost 2553) — Teulie stood alone, Sire. Ney and Bernadotte never came.
  - verbs: unfortify×2, form_square×2, attack×1, move×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (83 → 93); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 5156 · net +839 · threat 72 · provinces 28 (+0) · ceiling 10075 · army 136816 · vassals Holland 93 · Kingdom of Italy 89 · Switzerland 93
  - NET income 2564 · trade 612 · admin 50 · tribute 694 · upkeep 2072 · charges 537 · blockade 382 · admiralty 90
- DISPATCH: Sire — Ney was mauled at Franconia: a quarter of his corps — 4,565 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (200g/turn)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 7 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Paget
  - ⚔ Castanos (lost 228) vs Paget (lost 1305) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better. — The Line Holds +15% (Paget)
  - verbs: wait×2, move×2, unfortify×1, attack×1, form_square×1
- LEDGER treasury 6037 · net +718 · threat 70 · provinces 28 (+0) · ceiling 10168 · army 134864 · vassals Holland 93 · Kingdom of Italy 89 · Switzerland 92
  - NET income 2566 · trade 612 · admin 50 · tribute 698 · upkeep 2036 · charges 700 · blockade 382 · admiralty 90
- DISPATCH: Sire — not every court of the league has struck us. Britain has no road to us but the sea, and Normandy is a defended shore: she can land only by expedition, 15,000 men at a time. Russia has no lawfu…
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (12,422; expect about 42,517 with the corps likely to arrive, up to 44,364 if all march; certain 36,516, and a bad day (1 in 10) is no better) vs Archduke C…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 3273, own corps) vs Archduke Charles (lost 1381, own corps) — Reinforcements from Davout bolstered Ney's position — though Murat never arrived, Sire.
- CMD `Davout, move to Bohemia` → ✓ Davout expresses caution about the route but proceeds. Davout begins marching to Bohemia (distance: 2). Moved to Tyrol. Route: Tyrol -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.
  - POPUP strategic_interrupt: Murat, muster_confirm, Berthier stays the order a moment, Sire: before Murat marches on Archduke Charles, read the muster.

The muster reads unfavorable. 'Commit the Attack' to send him in regardless — or Cancel to hold him back.
Ask 'what if Murat attacks Archduke Charles' to read the muster before you commit — it costs nothing.
MUSTER — Murat (12,709) vs Archduke Charles (26,237 men) at Franconia — the balance of force looks unfavorable.
  WILL NOT — Davout: has already marched this turn
  WILL NOT — Soult: awaits explicit orders and will NOT march — order 'Soult, support Murat' and he will march
  WILL NOT — Bernadotte: will not lift a finger for Marshal Murat
  Archduke Charles does not stand alone: at least 1 enemy corps within reach of Franconia would march to him. Their columns gather slowly — The Hofkriegsrat: the bar 10 higher.
  Standing modifiers, already in the band: Archduke Charles stands +31% on the defense (his stance, his character and his works).
  Franconia feeds 32,000 — the whole muster can stand there fed. Living off the land: this stripped country feeds our army 80% of what it would otherwise draw.
  Materiel: every 1,000 men we lose costs 50g in guns, horses and stores, charged at the battle — a hard day (15% of the 12,709 we muster) would cost ~95g.
  A win here adds +3 to Europe's alarm (+5 more if decisive; none on your own soil) — now 72/100.
  Every corps in the province shares the field — that is the design. Only a corps still adjacent can be held out: fortify him (1 AP; 2 for Soult, Bernadotte, who stand neutral) and he stands apart until you move him. → attack_anyway
  - ↳ MUSTER — Murat (12,709) vs Archduke Charles (26,237 men) at Franconia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 6862) vs Archduke Charles (lost 441, own corps) — Murat held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. Turn 8 begins!
- enemy phase: 9 actions, 2 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Cuesta attacks Paget · Cuesta attacks Paget
  - ⚔ Cuesta (lost 44) vs Paget (lost 594) — Paget was driven from the field. His men are scattered. — The Line Holds +15% (Paget)
  - ⚔ Cuesta (lost 8) vs Paget (lost 158) — Paget's corps broke, Sire. They are streaming back from the field. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - verbs: break_square×3, fortify×2, attack×2, drill×1, wait×1
- ORDER Davout [active]: Davout is marching to Bohemia (2 turns remaining).
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 6707 · net +1042 · threat 70 · provinces 29 (+1) · ceiling 11465 · army 118033 · vassals Holland 89 · Kingdom of Italy 85 · Switzerland 87
  - NET income 2597 · trade 612 · admin 50 · tribute 703 · upkeep 1344 · charges 1029 · occupation 75 · blockade 382 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Saxony and Austria sign a Non-Aggression Pact
  - LOG moment: Russia decrees the Magazines for 8 turns (5 authority)

## Turn 8 — Early January 1806
  - MAILBOX #10 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #10 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +10 (85 → 95); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 65g a turn — 37g of income forfeited, 75g of occupation relieved, 27g returned as tribute at today's 75% rate, the force limit falls 2,500 at no cost today. → display-only
- CMD `Davout, attack Archduke Charles` → ✓ Davout respectfully raises concerns: 'Sire, the enemy is too strong. We need reinforcements.' (Trust him and he will fortify current position instead.) Davout's march to…
  - POPUP objection: Davout, Davout respectfully raises concerns: 'Sire, the enemy is too strong. We need reinforcements.' (Trust him and he will fortify current position instead.) → trust
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 2). Moved to Munich. Route: Munich -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: Ney turns openly discontent (trust -3; expect defiance).
  - POPUP diplomatic_dialogue: moment_letter #11 → reject_ai_proposal
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 7664 · net +758 · threat 68 · provinces 28 (-1) · ceiling 11609 · army 115264 · vassals Holland 89 · Kingdom of Italy 96 · Switzerland 86
  - NET income 2564 · trade 612 · admin 50 · tribute 735 · upkeep 1644 · charges 1087 · blockade 382 · admiralty 90
- DISPATCH: Sire — not every court of the league has struck us. Britain has no road to us but the sea, and Normandy is a defended shore: she can land only by expedition, 15,000 men at a time. Russia has no lawfu…
  - TURN EVENTS 10
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG moment: The Bavarian Match — a letter of the record is laid before the Emperor
  - LOG moment: The Bavarian Match — the Emperor answers: Let Baden keep her

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Franche-Comte and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Franche-Comte (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Co…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
- ORDER Massena [completed]: Massena arrives at Milan. Massena: "It is done. Point me at something that shoots back, Sire."
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 7875 · net +1013 · threat 66 · provinces 28 (+0) · ceiling 13060 · army 116463 · vassals Holland 89 · Kingdom of Italy 99 · Switzerland 85
  - NET income 2566 · trade 612 · admin 50 · tribute 739 · upkeep 1336 · charges 1146 · blockade 382 · admiralty 90
- DISPATCH: Sire — Prussia enacts the Military Reorganisation Commission — +5 morale from every drill.
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War for Franconia — Britain + Austria + Russia.
  - TURN EVENTS 8
- DIPLO +5 medium/low (enemy_marshal_commissioned ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)

## Turn 10 — Early February 1806
  - MAILBOX #12 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #13 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Franconia — the table with Austria + Russia (4 pairs resolved). Status quo: Franconia stays Austrian by the treaty. Status quo: Tyrol stays ours by the treaty — titled. Prisoners: Mack, our captive, goes home to Vienna under this peace — an Austrian commander back in the field. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Davout, fortify` → ✗ Davout is already fortified at Tyrol (+12% defense).
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout demands to be heard → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 9067 · net +970 · threat 35 · provinces 28 (+0) · ceiling 14727 · army 115422 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2570 · trade 612 · admin 50 · tribute 739 · upkeep 1320 · charges 1209 · blockade 382 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL settlement_summary: Sire, the white peace of the War for Franconia — the table with Austria + Russia takes nothing and gives nothing. Bavaria is left out: -7 relation.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 6,000 men ashore at Andalusia.
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 8
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Bavaria eases over Revanche — an ultimatum is now the length of its tether.
- DIPLO +6 medium/low (diplomatic_coalition_dissolved, status_quo_titled, province_changed_hands, diplomatic_dp_regen, diplomatic_vassal_contingent, agenda_shift)
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 66 to 33; Britain remains at war with us.
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✓ Archduke John stands at Franconia, two marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −84g more a turn. Pursue him (2 AP — a…
  - POPUP clarification: Ney, pursuit_ask, Archduke John stands at Franconia, two marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −84g more a turn. Pursue him (2 AP — a standing order; the first march takes Ney to Swabia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke John (2 AP))
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Franche-Comte and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Castanos · Castanos attacks Andalusia
  - ⚔ Castanos (lost 785) vs Shrapnel (lost 1218) — The margin was slim. Training and preparation would serve Shrapnel well. — The Line Holds +15% (Shrapnel)
  - verbs: attack×2, wait×2, move×1
- LEDGER treasury 10106 · net +835 · threat 37 · provinces 28 (+0) · ceiling 14889 · army 114412 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 83
  - NET income 2574 · trade 612 · admin 50 · tribute 796 · upkeep 1312 · charges 1413 · blockade 382 · admiralty 90
- DISPATCH: Sire — intelligence reports Britain has raised Wellesley to high command.
  - TURN EVENTS 4
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- DIPLO +2 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the nex…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 90% -> 79%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 600g on this turn's orders
- enemy phase: 6 actions, 2 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Andalusia · Blake attacks Shrapnel
  - 🏴 Spain: Castanos attacks Andalusia — Region captured: Andalusia (was Britain) (secured)
  - ⚔ Blake (lost 86, own corps) vs Shrapnel (lost 2008) — The toll on Shrapnel's forces is heavy, Sire. This defeat will be felt. And Shrapnel was taken on that field — Spain ho… — The Line Holds +15% (Shrapnel)
  - verbs: attack×2, retreat×1, stance_change×1, move×1, wait×1
- LEDGER treasury 10397 · net +734 · threat 39 · provinces 28 (+0) · ceiling 14528 · army 116342 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 82
  - NET income 2575 · trade 612 · admin 50 · tribute 796 · upkeep 1336 · charges 1491 · blockade 382 · admiralty 90
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,272g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 8
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- DIPLO +3 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #15 → 1
  - POPUP diplomatic_dialogue: war_purpose_selection #16 → 1
  -     ↳ refused: Our peace with Austria is fresh: no war may be declared on her for 2 more turns.
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 6 actions, 3 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Andalusia · Cuesta attacks Wellesley · Blake attacks Wellesley
  - ⚔ Castanos (lost 739) vs Wellesley (lost 710) — Neither Wellesley nor Castanos could claim the field. The armies remain locked. — The Line Holds +15% (Wellesley)
  - ⚔ Cuesta (lost 648) vs Wellesley (lost 415) — A standard affair. Nothing unusual to report. — The Line Holds +15% (Wellesley)
  - ⚔ Blake (lost 434) vs Wellesley (lost 317) — Stalemate. Wellesley and Blake glare at each other across the field. — The Line Holds +15% (Wellesley)
  - verbs: attack×3, wait×2, naval_expedition×1
- LEDGER treasury 11141 · net +808 · threat 41 · provinces 28 (+0) · ceiling 15606 · army 115304 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 81
  - NET income 2577 · trade 612 · admin 50 · tribute 1021 · upkeep 1328 · charges 1652 · blockade 382 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 4
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, coercive_demand)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Franche-Comte (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: 4 actions, 2 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Andalusia · Blake attacks Wellesley
  - ⚔ Castanos (lost 495) vs Wellesley (lost 687) — Our fortifications have sustained damage in the fighting. The walls will not hold forever, Your Majesty. — The Line Holds +15% (Wellesley)
  - ⚔ Blake (lost 129, own corps) vs Wellesley (lost 659) — Wellesley was close. A period of drilling could have changed the outcome. — The Line Holds +15% (Wellesley)
  - verbs: attack×2, fortify×1, wait×1
- ENVOYS WAITING 3 · Britain settlement offer · Switzerland client petition · The Secretariat moment letter
- LEDGER treasury 11950 · net +631 · threat 43 · provinces 28 (+0) · ceiling 15375 · army 114297 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 80
  - NET income 2578 · trade 612 · admin 50 · tribute 1021 · upkeep 1328 · charges 1830 · blockade 382 · admiralty 90
- DISPATCH: Sire — Austria, Prussia and Russia would now join a league against us (relations −75, −25 and −75). The Balance of Europe names the price to keep each out.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle the War with Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as joining the stronger side for pay.
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- COURTS: And Saxony stirs at its own design.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 15 — Late April 1806
  - MAILBOX #13 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - MAILBOX #15 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #19 → reject_ai_proposal
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #20 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with Britain — the table with Britain (3 pairs resolved). Status quo: Andalusia stays British by the treaty. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #18 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #18 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: moment_letter #19 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14129 · net +1962 · threat 45 · provinces 28 (+0) · ceiling 33740 · army 113320 · vassals Holland 87 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2580 · trade 612 · admin 50 · tribute 796 · upkeep 864 · charges 1212
- DISPATCH: Sire — peace with Britain is signed. A white peace — the map stands as it was.
  - RAIL settlement_summary: Sire, the white peace of the War with Britain — the table with Britain takes nothing and gives nothing. Spain is left out: -18 relation and a grievan…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Alle…
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - RAIL +3 more
  - TURN EVENTS 6
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — alliance is now the length of its tether.
- COURTS: And Bavaria and Russia stir at their own designs.
- DIPLO +7 medium/low (province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land
  - LOG ai_ai_proposal_refused: 4 approaches to Bavaria, Prussia and Hanover are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 3 approaches from Saxony, Prussia and Hesse are rebuffed (design ask)

## Turn 16 — Early May 1806
  - MAILBOX #16 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #21 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 7 other courts stirred as well, but their formations remain beyond our sight. — Brunswick attacks Alten · Brunswick attacks Wallmoden
  - 🏴 Prussia: Brunswick attacks Wallmoden — Osnabruck CAPTURED! (was Hanover) (secured)
  - ⚔ Brunswick (lost 656) vs Alten (lost 2949) — Not one corps reached Alten. Wallmoden was expected; Alten fought the battle single-handed. And Alten was taken on that… — Frederick's Drill +10% (Brunswick)
  - ⚔ Brunswick (lost 358) vs Wallmoden (lost 1323) — A grievous defeat for Wallmoden, Sire. The losses are severe. And Wallmoden was taken on that field — Prussia holds him. — Frederick's Drill +10% (Brunswick)
  - verbs: attack×2, wait×1
- LEDGER treasury 15784 · net +1489 · threat 45 · provinces 28 (+0) · ceiling 30670 · army 112373 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2582 · trade 612 · admin 50 · tribute 487 · upkeep 864 · charges 1378
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +4 medium/low (province_changed_hands, diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria, Saxony and Prussia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 17274 · net +1341 · threat 45 · provinces 28 (+0) · ceiling 30680 · army 111454 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2583 · trade 612 · admin 50 · tribute 487 · upkeep 864 · charges 1527
- DISPATCH: Sire — Hesse moves toward war with Hanover. The design is open; the timing is not.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - RAIL crisis_brewing: THE BREWING CRISIS: Hesse will move on Hanover. You may compensate (1,320g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the war…
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,617 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 6
- COURTS: The court of Saxony eases over The Wettin Crown — joining the stronger side for pay is now the length of its tether.
- DIPLO +6 medium/low (law_enacted_abroad, province_changed_hands ×2, diplomatic_dp_regen, agenda_shift ×2)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 1 more — Prussia is not forgiven

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 18625 · net +1216 · threat 45 · provinces 28 (+0) · ceiling 30780 · army 110563 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2585 · trade 612 · admin 50 · tribute 487 · upkeep 856 · charges 1662
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Austria, Russia, Prussia and 3 lesser courts would march. Bound for now b…
  - RAIL allegiance_settled: The bidding for Bavaria is closed in our favour, but our relations are too cool for any pact the table can sign.
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Austria.
  - RAIL crisis_passed: Hesse stands down over Hanover, Sire — the moment passed — opportunism decayed.
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Austria sign a Defensive Alliance
  - LOG ai_ai_proposal_refused: Austria rebuffs Hanover (open borders agreement)
  - LOG ai_ai_proposal_refused: Austria rebuffs Hesse (defensive alliance)
  - LOG moment: The Throne of Holland — a letter of the record is laid before the Emperor
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 19 — Late June 1806
  - MAILBOX #17 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #22 → reject_ai_proposal
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 19804 · net +1061 · threat 45 · provinces 28 (+0) · ceiling 30410 · army 109699 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2586 · trade 574 · admin 50 · tribute 487 · upkeep 856 · charges 1780
- DISPATCH: Sire — Britain would now join a league against us — relations −85. The price to keep her out: Talleyrand brings her to −10 in 9 turns (9 DP); buying off her design costs 1,044 gold and shortens the r…
  - TURN EVENTS 3
- COURTS: The court of Bavaria hardens over Revanche — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)
  - LOG moment: The Throne of Holland — the Emperor answers: Keep the Republic

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `rev1106-cmd-ulm_t20` → Game saved: rev1106-cmd-ulm_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 20883 · net +971 · threat 45 · provinces 28 (+0) · ceiling 30590 · army 108861 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2588 · trade 574 · admin 50 · tribute 487 · upkeep 840 · charges 1888
- DISPATCH: Sire — Britain enacts the Militia Transfer — infantry manpower returns 25% faster; cures Irreplaceable — the court's doctrine flaw — while its Staff stands.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — 'Lannes, recruit' raises them at Franche-Comte. Nothing was spent.
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- LEDGER treasury 21864 · net +883 · threat 45 · provinces 28 (+0) · ceiling 30690 · army 108048 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 487 · upkeep 832 · charges 1986
- DISPATCH: Sire — the allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegiance.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Defensive Alliance → Non-Aggression)
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 22747 · net +1020 · threat 45 · provinces 28 (+0) · ceiling 32940 · army 107259 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 832 · charges 2074
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Britain, Austria, Russia, Prussia and 3 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, wait×1
- LEDGER treasury 23775 · net +1262 · threat 45 · provinces 28 (+0) · ceiling 36390 · army 106493 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 1049 · upkeep 824 · charges 2177
- DISPATCH: Sire — the allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegiance.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 2 · Holland client petition · The Secretariat moment letter
- LEDGER treasury 25045 · net +1143 · threat 45 · provinces 28 (+0) · ceiling 36470 · army 105750 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 1049 · upkeep 816 · charges 2304
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Austria, Russia, Prussia and 3 lesser courts would march.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over The Gulf and the Straits — joining the stronger side for pay is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG moment: The Remounts — an affair of state is laid before the Emperor

## Turn 25 — Late September 1806
  - MAILBOX #18 Holland incoming_proposal: Holland — Client's Petition → activated
  - MAILBOX #19 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #23 → grant the petition
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #24 → reject_ai_proposal
  - POPUP diplomatic_dialogue: Holland, client_petition #23 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: moment_letter #24 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 25851 · net +725 · threat 45 · provinces 28 (+0) · ceiling 33100 · army 105029 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 816 · charges 2385
- DISPATCH: Sire — the allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Allegiance.
  - RAIL allegiance_in_play: The allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Alle…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)
  - LOG moment: The Remounts — the Emperor answers: Let the depots wait

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 26592 · net +667 · threat 49 · provinces 28 (+0) · ceiling 33260 · army 104331 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 800 · charges 2459
- DISPATCH: Sire — the moment passes: Bavaria no longer weighs the flip, and the bidding is closed.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - RAIL allegiance_settled: The moment passes: Bavaria no longer weighs the flip, and the bidding is closed.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 84%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 27038 · net +607 · threat 53 · provinces 28 (+0) · ceiling 33100 · army 106563 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 816 · charges 2503
- DISPATCH: Sire — Europe has watched us 21 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Austria, Russia, Prussia and 3 lesser courts would march. The cheapest court t…
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 27645 · net +546 · threat 57 · provinces 28 (+0) · ceiling 33100 · army 105819 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 816 · charges 2564
- DISPATCH: Sire — Europe has watched us 22 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Austria, Russia, Prussia and 3 lesser courts would march. The cheapest court t…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 29 — Late November 1806
  - MAILBOX #20 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #25 → reject_ai_proposal
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 28191 · net +491 · threat 60 · provinces 28 (+0) · ceiling 33100 · army 105097 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 816 · charges 2619
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift ×2)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover and Sardinia alarmed (threat: 60)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 28690 · net +449 · threat 58 · provinces 28 (+0) · ceiling 33180 · army 104397 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 808 · charges 2669
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design costs 1…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 29139 · net +405 · threat 56 · provinces 28 (+0) · ceiling 33180 · army 103717 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 808 · charges 2713
- DISPATCH: Sire — St Petersburg now pays Sweden 400 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design …
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 28128 · net -636 · threat 54 · provinces 28 (+0) · ceiling 22957 · army 103058 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 1049 · upkeep 1232 · charges 3218 · blockade 359 · admiralty 90
- DISPATCH: Sire — Britain, Russia, Austria, Sweden, Hanover and Sardinia are at war with France. Britain tears up the Peace Treaty to do it. Russia tears up the Peace Treaty to do it. Austria tears up the Peace…
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Sweden, Hanover and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 3 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Hanover has declared war on France, with 2 allied courts poised to follow.
  - RAIL +6 more
  - TURN EVENTS 4
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: And Sardinia, Britain, Bavaria and Hesse stir at their own designs.
- DIPLO +15 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken, blockade_begins ×4, diplomatic_relation_shift ×6)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).
  - LOG coalition_declared: The Fourth Austrian Coalition — Coalition formed against France! Members: Austria, Britain, Hanover, Russia, Sardinia and Sweden

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — 'Lannes, recruit' raises them at Franche-Comte. Nothing was spent.
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- enemy phase: 10 actions, 5 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Bernadotte · Castanos attacks Andalusia · Cuesta attacks Wellesley · Alten attacks Artois
  - 🏴 Spain: Cuesta attacks Wellesley — Andalusia CAPTURED! (was Britain) (secured)
  - 🏴 Hanover: Alten attacks Artois — Region captured: Artois (was France) (secured)
  - 🏴 Hanover: Wallmoden attacks Picardy — Region captured: Picardy (was France) (secured)
  - ⚔ Archduke Charles (lost 339) vs Bernadotte (lost 3097) — Bernadotte held superior ground, yet Archduke Charles prevailed. A grim day, Sire. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Castanos (lost 696) vs Wellesley (lost 1187) — Wellesley was close. A period of drilling could have changed the outcome. — The Line Holds +15% (Wellesley)
  - ⚔ Cuesta (lost 622) vs Wellesley (lost 2532) — The toll on Wellesley's forces is heavy, Sire. This defeat will be felt. And Wellesley was taken on that field — Spain … — The Line Holds +15% (Wellesley)
  - verbs: attack×5, move×2, wait×2, grant_pension×1
- LEDGER treasury 27241 · net -741 · threat 52 · provinces 26 (-2) · ceiling 21571 · army 98395 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2440 · trade 574 · admin 50 · tribute 1049 · upkeep 1104 · charges 3301 · blockade 359 · admiralty 90
- DISPATCH: Sire — Artois has fallen to Hanover. Enemy colours fly over French homeland soil. Alten's corps of ~2,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does any…
  - TURN EVENTS 5
- DIPLO +7 medium/low (province_changed_hands, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, paymaster_subsidy)
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: 2 approaches from Austria and Hesse are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Hanover (open borders agreement)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria, Prussia and Hesse are rebuffed (design ask)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 7 actions, 4 attacks — Britain, Russia, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Tyrol · Archduke John attacks Munich · Archduke John attacks Munich · Deroy attacks Munich
  - 🏴 Austria: Archduke John attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 7101) vs Davout (lost 951, own corps) — Reinforcements! Massena and Teulie marched onto the field beside Davout. The enemy's advantage melted away. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Deroy (lost 1785, own corps) vs Archduke John (lost 2125) — Neither Archduke John nor Deroy could claim the field. The armies remain locked.
  - verbs: attack×4, fortify×2, recruit×1
- LEDGER treasury 25415 · net -1536 · threat 50 · provinces 26 (+0) · ceiling 16136 · army 94320 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2440 · trade 574 · admin 50 · tribute 878 · upkeep 1072 · charges 3877 · contributions 80 · blockade 359 · admiralty 90
- DISPATCH: Sire — Artois and Picardy lie in enemy hands. Hanover holds them.
  - EXPECTS: Davout's victories raise his expectation — he now looks for 40g/turn (holds 0g).
  - EXPECTS: Massena's victories raise his expectation — he now looks for 40g/turn (holds 0g).
  - RAIL expedition_landed: THE LANDING: Paget has put 10,000 men ashore at Piedmont.
  - RAIL allegiance_settled: The bidding for Saxony is closed in our favour, but our relations are too cool for any pact the table can sign.
  - RAIL design_promoted: REVANCHE AGAIN: Bavaria will not forgive Austria the loss of Munich. The old design hardens again in their court.
  - TURN EVENTS 6
- DIPLO +7 medium/low (province_changed_hands ×3, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 500g reaches Sweden
  - LOG british_subsidy: Britain's gold: 500g reaches Sweden
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Britain sign a Defensive Alliance

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! Archduke John is at Munich, just one region away.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: 10 actions, 5 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Paget attacks Milan · Paget attacks Milan · Archduke John attacks Wrede · Deroy attacks Munich
  - 🏴 Britain: Paget attacks Milan — The garrison of Milan is destroyed. · Region captured: Milan (was Kingdom of Italy) (plundered)
  - ⚔ Archduke John (lost 709) vs Wrede (lost 1228) — Wrede's aggressive posture left the troops exposed when Archduke John's attack came.
  - ⚔ Deroy (lost 1619) vs Paget (lost 1446) — Neither Paget nor Deroy could claim the field. The armies remain locked. — The Line Holds +15% (Paget)
  - ⚔ Deroy (lost 1085) vs Paget (lost 1281) — An inconclusive affair. Both sides bloodied but unbroken. — The Line Holds +15% (Paget)
  - verbs: attack×5, move×1, wait×1, retreat×1, stance_change×1, recruit×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 23673 · net -1540 · threat 48 · provinces 26 (+0) · ceiling 14588 · army 91569 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2440 · trade 574 · admin 50 · tribute 656 · upkeep 1056 · charges 3675 · contributions 80 · blockade 359 · admiralty 90
- DISPATCH: Sire — Wallmoden has crossed into Orleanais. No French corps stands in his path.
  - TURN EVENTS 7
- DIPLO +3 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG moment: The Squadron for Santo Domingo — an affair of state is laid before the Emperor
  - LOG design_promoted: REVANCHE: Bavaria swears again to retake Munich — Austria is not forgiven
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)
  - LOG moment: Russia decrees the Magazines for 8 turns (2,500 gold)

## Turn 36 — Early March 1807
  - MAILBOX #21 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #26 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Massena, fortify` → ✓ Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke John at Franconia instead.)
  - POPUP objection: Massena, Massena firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Archduke John at Franconia instead.) → trust
  - ↳ MUSTER — Massena (24,797; expect about 32,199 with the corps likely to arrive, up to 34,477 if all march; certain 24,797, and a bad day (1 in 10) is no better) vs Archduke John (11,402 men) at Franconia — the balance of force looks favorabl
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 1094, own corps) vs Archduke John (lost 3651) — Teulie arrived to reinforce Massena! The timely arrival swung the battle in our favor, Sire.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 7 actions, 4 attacks — Russia, Prussia, the Ottoman Empire and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Tyrol · Cuesta attacks Paget · Deroy attacks Munich · Deroy attacks Paget
  - 🏴 Bavaria: Deroy attacks Munich — The last 4,000 of the garrison of Munich give way. · Region captured: Munich (was Austria) (secured)
  - 🏴 Bavaria: Deroy moves to Milan — Milan falls (was Britain) and is secured
  - 🏴 Bavaria: Deroy attacks Paget — Piedmont CAPTURED! (was Britain) (secured)
  - ⚔ Archduke Charles (lost 6774) vs Davout (lost 660, own corps) — Massena arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Cuesta (lost 874) vs Paget (lost 1759) — The hills were ours, but Cuesta took them. Paget's position was overrun. — The Line Holds +15% (Paget)
  - ⚔ Deroy (lost 402) vs Paget (lost 1623) — Paget's aggressive posture left the troops exposed when Deroy's attack came. And Paget was taken on that field — Bavari… — The Line Holds +15% (Paget)
  - verbs: attack×4, move×3
- LEDGER treasury 22003 · net -1358 · threat 49 · provinces 26 (+0) · ceiling 14248 · army 87464 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2440 · trade 574 · admin 50 · tribute 635 · upkeep 1024 · charges 3504 · contributions 80 · blockade 359 · admiralty 90
- DISPATCH: Sire — 3 turns now with Artois and Picardy in enemy hands. The country counts every one of them.
  - UNMET: Davout expects 40g/turn, holds 0g — patience holds 2 more turns
  - UNMET: Massena expects 40g/turn, holds 0g — patience holds 2 more turns
  - TURN EVENTS 4
- DIPLO +5 medium/low (province_changed_hands ×3, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Hesse are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: PapalStates rebuffs Hanover (open borders agreement)
  - LOG moment: The Squadron for Santo Domingo — the Emperor answers: Ferrand must hold alone
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Hesse are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria, Saxony and Hesse are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Hesse are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Hesse are rebuffed (design ask)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 4 actions, 0 attacks — Russia, Austria, Prussia and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, fortify×1, naval_expedition×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 20610 · net -1223 · threat 47 · provinces 26 (+0) · ceiling 13780 · army 86155 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2440 · trade 574 · admin 50 · tribute 600 · upkeep 1024 · charges 3334 · contributions 80 · blockade 359 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - UNMET: Davout expects 40g/turn, holds 0g — patience holds 1 more turn
  - UNMET: Massena expects 40g/turn, holds 0g — patience holds 1 more turn
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 8,000 men ashore at Andalusia.
  - TURN EVENTS 10
- DIPLO +8 medium/low (province_changed_hands ×2, diplomatic_dp_regen, diplomatic_auto_downgrade ×4, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Britain–Sardinia (Defensive Alliance → Non-Aggression)
  - LOG british_subsidy: Britain's gold: 400g reaches Sweden
  - LOG british_subsidy: Britain's gold: 400g reaches Sweden

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Massena, drill` → ✓ Massena begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 40.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 2 actions unused) Turn 39 begins!
- enemy phase: 5 actions, 4 attacks — Russia, Prussia, the Ottoman Empire and 8 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Castanos · Archduke Charles attacks Tyrol · Castanos attacks Andalusia · Castanos attacks Andalusia
  - ⚔ Archduke Charles (lost 7766) vs Davout (lost 518, own corps) — Teulie's timely arrival bolstered Davout's position. Well-coordinated, Sire.
  - ⚔ Castanos (lost 972) vs Shrapnel (lost 1272) — An inconclusive affair. Both sides bloodied but unbroken. — The Line Holds +15% (Shrapnel)
  - ⚔ Castanos (lost 723) vs Shrapnel (lost 1282) — The margin was slim. Training and preparation would serve Shrapnel well. — The Line Holds +15% (Shrapnel)
  - verbs: attack×4, unfortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #27 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #28 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Artois — the table with Austria + Hanover + Russia + Sardinia + Sweden (30 pairs resolved). Status quo: Milan and Piedmont return to Kingdom of Italy by the treaty — homeland retaken by an ally. Status quo: Tyrol stays ours by the treaty — titled. Status quo: Artois and Picardy stay Hanoverian by the treaty. Status quo: Friesland stays Hanoverian by the treaty. → display-only
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 19312 · net -315 · threat 45 · provinces 26 (+0) · ceiling 17188 · army 83439 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2440 · trade 524 · admin 50 · tribute 666 · upkeep 1008 · charges 2569 · blockade 328 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - UNMET: Davout expects 40g/turn, holds 0g — loyalty eroding
  - UNMET: Massena expects 40g/turn, holds 0g — loyalty eroding
  - RAIL settlement_offer_arrival: Austria, for Russia, Austria, Sweden, Hanover and Sardinia, has offered terms to settle the War for Artois — Britain + Russia + Austria + Sweden + Ha…
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_we_threshold ×2, diplomatic_dp_regen, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (Alliance → Defensive Alliance)
  - LOG british_subsidy: Britain's gold: 400g reaches Russia
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Sweden has left the coalition.
  - LOG coalition_member_left: Hanover has left the coalition.
  - LOG coalition_member_left: Sardinia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 45 to 22; Britain remains at war with us.
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Non-Aggression → Open Borders)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Sardinia (Defensive Alliance → Non-Aggression)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 100% -> 83%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 600g on this turn's orders
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks Andalusia · Blake attacks Shrapnel
  - 🏴 Spain: Castanos attacks Andalusia — Region captured: Andalusia (was Britain) (secured)
  - ⚔ Blake (lost 114, own corps) vs Shrapnel (lost 1504) — Shrapnel's army has been badly mauled. Blake proved the stronger force today. And Shrapnel was taken on that field — Sp… — The Line Holds +15% (Shrapnel)
  - verbs: attack×2, grant_pension×1
- LEDGER treasury 18623 · net -104 · threat 25 · provinces 26 (+0) · ceiling 17936 · army 84663 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2440 · trade 524 · admin 50 · tribute 836 · upkeep 1016 · charges 2520 · blockade 328 · admiralty 90
- DISPATCH: Sire — Davout, Massena and Teulie stand 41,751 men at Tyrol, which feeds 30,000. 11,751 too many. 2,832 men lost in 3 turns. Kingdom of Italy's magazines feed us as our own — the army is simply too l…
  - UNMET: Davout expects 40g/turn, holds 0g — loyalty eroding
  - UNMET: Massena expects 40g/turn, holds 0g — loyalty eroding
  - RAIL settlement_summary: Sire, the white peace of the War for Artois — the table with Austria + Hanover + Russia + Sardinia + Sweden takes nothing and gives nothing. Spain is…
  - RAIL status_quo_conceded: Artois and Picardy — left with Hanover by the peace, titled to them by treaty.
  - RAIL status_quo_conceded: Friesland — left with Hanover by the peace, titled to them by treaty.
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 5
- COURTS: The court of Hesse eases over The Westphalian Duchy — joining the stronger side for pay is now the length of its tether.
- DIPLO +5 medium/low (status_quo_titled, diplomatic_coalition_dissolved, province_changed_hands, diplomatic_dp_regen, agenda_shift)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `rev1106-cmd-ulm_t40` → Game saved: rev1106-cmd-ulm_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 2 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 10 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 18547 · net -117 · threat 28 · provinces 26 (+0) · ceiling 17788 · army 82963 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2440 · trade 524 · admin 50 · tribute 840 · upkeep 992 · charges 2561 · blockade 328 · admiralty 90
- DISPATCH: Sire — Davout, Massena and Teulie stand 40,672 men at Tyrol, which feeds 30,000. 10,672 too many. 3,401 men lost in 3 turns. Kingdom of Italy's magazines feed us as our own — the army is simply too l…
  - UNMET: Davout expects 40g/turn, holds 0g — loyalty eroding
  - UNMET: Massena expects 40g/turn, holds 0g — loyalty eroding
  - RAIL expedition_landed: THE LANDING: Blake has put 6,705 men ashore at East Anglia.
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - TURN EVENTS 8
- DIPLO +2 medium/low (province_changed_hands, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Hesse (design ask)

---
finished: **completed** · commands 200 · popups 61 · battles 39
