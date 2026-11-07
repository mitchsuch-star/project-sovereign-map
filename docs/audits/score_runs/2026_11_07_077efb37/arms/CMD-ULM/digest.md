# Playtest digest — CMD-ULM

seed `ulm` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `ulm` · dice `ulm`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `077efb374d7c` · content `e96449bb3b47` · driver `bd054bd265d8`
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
- MARSHALS Ney trust 75 Reliable glory 1 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
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
- MARSHALS Ney trust 69 Reliable glory 2 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 72 Reliable glory 0 (#5) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
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
- MARSHALS Ney trust 66 Reliable glory 2 (#1) · Davout trust 82 Loyal glory 0 (#3) envies Murat · Soult trust 70 Reliable glory 0 (#4) envies Murat · Lannes trust 85 Loyal glory 0 (#5) · Murat trust 72 Reliable glory 1 (#2) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
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
- MARSHALS Ney trust 66 Reliable glory 2 (#1) · Davout trust 82 Loyal glory 0 (#3) envies Murat · Soult trust 70 Reliable glory 0 (#4) envies Murat · Lannes trust 85 Loyal glory 0 (#5) envies Murat · Murat trust 72 Reliable glory 1 (#2) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Lannes, Murat, Massena and Napoleon stand 67,531 men at Franche-Comte, which feeds 52,500. 15,031 too many. 7,321 men lost in 3 turns. No depot may be laid at Franche-Comte — town regions don'…
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain binds Austria to the war against France — no separate peace for 10 turns (300g/turn)
  - LOG moment: Britain decrees the Magazines for 8 turns (5 authority)
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
- MARSHALS Ney trust 63 Reliable glory 2 (#1) · Davout trust 82 Loyal glory 0 (#3) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 85 Loyal glory 0 (#5) envies Murat · Murat trust 72 Reliable glory 1 (#2) envies Ney · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Ney was mauled at Franconia: a quarter of his corps — 4,565 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +7 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

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
- MARSHALS Ney trust 63 Reliable glory 2 (#1) · Davout trust 82 Loyal glory 0 (#3) envies Murat · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 85 Loyal glory 0 (#5) · Murat trust 72 Reliable glory 1 (#2) · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — not every court of the league has struck us. Britain has no road to us but the sea, and Normandy is a defended shore: she can land only by expedition, 15,000 men at a time. Russia has no lawfu…
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as alliance.
- DIPLO +2 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen)

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
- enemy phase: 9 actions, 1 attacks — Britain, Russia, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Cuesta attacks Paget
  - ⚔ Cuesta (lost 41) vs Paget (lost 594) — Paget was driven from the field. His men are scattered. — The Line Holds +15% (Paget)
  - verbs: break_square×3, fortify×2, wait×2, attack×1, form_square×1
- ORDER Davout [active]: Davout is marching to Bohemia (2 turns remaining).
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 6714 · net +1047 · threat 70 · provinces 29 (+1) · ceiling 11497 · army 118033 · vassals Holland 89 · Kingdom of Italy 85 · Switzerland 87
  - NET income 2604 · trade 612 · admin 50 · tribute 703 · upkeep 1344 · charges 1031 · occupation 75 · blockade 382 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 2 (#1) · Davout trust 82 Loyal glory 0 (#3) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 85 Loyal glory 0 (#5) · Murat trust 69 Reliable glory 1 (#2) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Ney's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Shrapnel has put 3,000 men ashore at Carniola.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, diplomatic_ai_ai_treaty)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
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
- enemy phase: 6 actions, 2 attacks — Russia, Austria, Prussia and 7 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout · Cuesta attacks Paget
  - ⚔ Cuesta (lost 11) vs Paget (lost 189) — Paget's corps broke, Sire. They are streaming back from the field. And Paget was taken on that field — Spain holds him. — The Line Holds +15% (Paget)
  - verbs: attack×2, break_square×1, move×1, wait×1, recruit×1
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: moment_letter #11 → reject_ai_proposal
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 7664 · net +752 · threat 68 · provinces 28 (-1) · ceiling 11568 · army 114687 · vassals Holland 89 · Kingdom of Italy 96 · Switzerland 86
  - NET income 2560 · trade 612 · admin 50 · tribute 735 · upkeep 1644 · charges 1089 · blockade 382 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 1 (#1) · Davout trust 85 Loyal glory 0 (#3) vind +1 envies Murat · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 85 Loyal glory 0 (#5) · Murat trust 69 Reliable glory 1 (#2) · Bernadotte trust 40 Strained glory 0 (#6) envies Ney · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - TURN EVENTS 10
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as war.
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
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
- LEDGER treasury 7870 · net +1008 · threat 66 · provinces 28 (+0) · ceiling 13022 · army 115886 · vassals Holland 89 · Kingdom of Italy 99 · Switzerland 85
  - NET income 2563 · trade 612 · admin 50 · tribute 739 · upkeep 1336 · charges 1148 · blockade 382 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#2) · Davout trust 85 Loyal glory 0 (#3) vind +1 · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 85 Loyal glory 0 (#5) envies Murat · Murat trust 69 Reliable glory 1 (#1) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0
- DISPATCH: Sire — Prussia enacts the Military Reorganisation Commission — +5 morale from every drill.
  - RAIL settlement_offer_arrival: Austria, for Austria and Russia, has offered terms to settle the War for Franconia — Britain + Austria + Russia.
  - TURN EVENTS 9
- DIPLO +4 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 10 — Early February 1806
  - MAILBOX #12 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #13 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War for Franconia — the table with Austria + Russia (4 pairs resolved). Status quo: Franconia stays Austrian by the treaty. Status quo: Tyrol stays ours by the treaty — titled. Prisoners: Mack, our captive, goes home to Vienna under this peace — an Austrian commander back in the field. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Davout, fortify` → ✗ Davout is already fortified at Tyrol (+6% defense).
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich, Swabia.
  - saved `CMD-ULM_t10` → Game saved: CMD-ULM_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout demands to be heard → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 9060 · net +968 · threat 35 · provinces 28 (+0) · ceiling 14710 · army 114845 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2567 · trade 612 · admin 50 · tribute 739 · upkeep 1320 · charges 1208 · blockade 382 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#1) envies Murat · Davout trust 85 Loyal glory 0 (#2) vind +1 envies Murat · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) envies Murat · Murat trust 69 Reliable glory 0 (#5) envies Davout · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0
- DISPATCH: Sire — our peace binds Austria for 4 more turns and Russia for 4 more turns; then each may join a league (relations −79 and −79).
  - RAIL settlement_summary: Sire, the white peace of the War for Franconia — the table with Austria + Russia writes no clause: each side keeps what it holds on the day of signin…
  - RAIL broken_bargain: The compact with Britain lies torn — Austria is named the breaker in every chancery of Europe.
  - TURN EVENTS 9
- COURTS: The court of Austria eases over Primacy in Germany — an ultimatum is now the length of its tether.
- COURTS: The court of Bavaria eases over Revanche — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent, agenda_shift)
  - LOG sponsorship_reneged: THE BROKEN BARGAIN: Austria breaks the bond with Britain — a separate peace with France inside the term
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 66 to 33; Britain remains at war with us.
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✓ Archduke John stands at Franconia, two marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −84g more a turn. Pursue him (2 AP — a…
  - POPUP clarification: Ney, pursuit_ask, Archduke John stands at Franconia, two marches off. Swabia is Bavaria's soil — the corps standing there are fed by contract, about −84g more a turn. Pursue him (2 AP — a standing order; the first march takes Ney to Swabia, Bavaria's soil), or cancel? → 1 (first option: Pursue Archduke John (2 AP))
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Franche-Comte and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout
  - verbs: attack×1, wait×1
- LEDGER treasury 10102 · net +837 · threat 37 · provinces 28 (+0) · ceiling 14889 · army 113322 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 83
  - NET income 2571 · trade 612 · admin 50 · tribute 796 · upkeep 1304 · charges 1416 · blockade 382 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#1) envies Murat · Davout trust 85 Loyal glory 0 (#2) vind +1 envies Murat · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 69 Reliable glory 0 (#5) envies Davout · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0
- DISPATCH: Sire — intelligence reports Britain has raised Wellesley to high command.
  - TURN EVENTS 5
- COURTS: The court of Hesse hardens over The Westphalian Duchy — prepared now to go as far as alliance.
- DIPLO +2 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the nex…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 90% -> 79%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 600g on this turn's orders
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout
  - verbs: attack×1, wait×1
- LEDGER treasury 10396 · net +736 · threat 39 · provinces 28 (+0) · ceiling 14516 · army 114815 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 82
  - NET income 2575 · trade 612 · admin 50 · tribute 796 · upkeep 1328 · charges 1497 · blockade 382 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) vind +1 · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 69 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,272g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 8
- COURTS: The court of Austria hardens over Primacy in Germany — prepared now to go as far as war.
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- DIPLO +2 medium/low (province_changed_hands, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ Murat cannot attack — our peace with Austria is fresh: no war may be declared on her for 2 more turns. Nothing spent.
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 1 attacks — Russia, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout
  - verbs: attack×1, wait×1
- LEDGER treasury 11150 · net +815 · threat 41 · provinces 28 (+0) · ceiling 15634 · army 113383 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 81
  - NET income 2577 · trade 612 · admin 50 · tribute 1021 · upkeep 1312 · charges 1661 · blockade 382 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 69 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0
- DISPATCH: Sire — Prussia moves toward war with Hanover. The design is open; the timing is not.
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
- enemy phase: 2 actions, 0 attacks — Russia, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- ENVOYS WAITING 3 · Britain settlement offer · Switzerland client petition · The Secretariat moment letter
- LEDGER treasury 11966 · net +636 · threat 43 · provinces 28 (+0) · ceiling 15403 · army 112376 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 80
  - NET income 2578 · trade 612 · admin 50 · tribute 1021 · upkeep 1312 · charges 1841 · blockade 382 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 69 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0
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
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #17 → reject_ai_proposal
  - POPUP diplomatic_dialogue: incoming_settlement_offer #15 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: the War with Britain — the table with Britain (3 pairs resolved). → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
  - POPUP diplomatic_dialogue: moment_letter #17 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14160 · net +1974 · threat 45 · provinces 28 (+0) · ceiling 33900 · army 111399 · vassals Holland 87 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2580 · trade 612 · admin 50 · tribute 796 · upkeep 848 · charges 1216
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 69 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — peace with Britain is signed. A white peace — the map stands as it was.
  - RAIL settlement_summary: Sire, the white peace of the War with Britain — the table with Britain writes no clause: each side keeps what it holds on the day of signing, titled …
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Alle…
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - RAIL allegiance_settled: The moment passes: Saxony no longer weighs the flip, and the bidding is closed.
  - RAIL +3 more
  - TURN EVENTS 6
- COURTS: The court of Sardinia eases over The House of Savoy Restored — joining the stronger side for pay is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — joining the stronger side for pay is now the length of its tether.
- COURTS: And Bavaria and Russia stir at their own designs.
- DIPLO +7 medium/low (province_changed_hands, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (4 authority)
  - LOG ai_ai_proposal_refused: 4 approaches to Bavaria, Prussia and Hanover are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 3 approaches from Saxony, Prussia and Hesse are rebuffed (design ask)

## Turn 16 — Early May 1806
  - MAILBOX #16 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
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
- LEDGER treasury 15827 · net +1501 · threat 45 · provinces 28 (+0) · ceiling 30830 · army 110452 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2582 · trade 612 · admin 50 · tribute 487 · upkeep 848 · charges 1382
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 69 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 1 more province. A new design hardens in their court.
  - TURN EVENTS 4
- DIPLO +5 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen, diplomatic_auto_downgrade, agenda_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria, Saxony and Prussia are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: 2 approaches from Saxony and Prussia are rebuffed (design ask)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Hanover broker peace
- LEDGER treasury 17329 · net +1352 · threat 45 · provinces 28 (+0) · ceiling 30840 · army 109533 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2583 · trade 612 · admin 50 · tribute 487 · upkeep 848 · charges 1532
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 69 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — Britain enacts the Horse Guards Reforms — +1 order of the day, from the next refill.
  - RAIL diplomatic_ai_proposal: An envoy from Hanover has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad, province_changed_hands, diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 1 more — Prussia is not forgiven

## Turn 18 — Early June 1806
  - MAILBOX #17 Hanover incoming_proposal: Hanover — Brokered Peace → activated
  - POPUP diplomatic_dialogue: Hanover, broker_peace #20 → accept_ai_proposal
  - POPUP proposal_result: Peace concluded between Hanover and Prussia without France. Prussia takes Hanover. Hanover pays 1,570 gold. Prussia is now free to look elsewhere. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 18691 · net +1225 · threat 45 · provinces 28 (+0) · ceiling 30940 · army 108642 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2585 · trade 612 · admin 50 · tribute 487 · upkeep 840 · charges 1669
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Austria, Russia, Prussia and 3 lesser courts would march. Bound for now b…
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Prussia takes Hanover. Hanover pays 1,570 gold. Prussia is now free to look e…
  - RAIL allegiance_settled: The bidding for Bavaria is closed in our favour, but our relations are too cool for any pact the table can sign.
  - RAIL allegiance_settled: The moment passes: Hesse no longer weighs the flip, and the bidding is closed.
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Austria.
  - TURN EVENTS 6
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- COURTS: The court of Saxony eases over The Wettin Crown — alliance is now the length of its tether.
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_ai_ai_treaty, agenda_shift ×2)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Austria sign a Defensive Alliance
  - LOG moment: The Throne of Holland — a letter of the record is laid before the Emperor

## Turn 19 — Late June 1806
  - MAILBOX #18 The Secretariat incoming_proposal: The Secretariat — A Moment of History → activated
  - POPUP diplomatic_dialogue: moment_letter #21 → reject_ai_proposal
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 19879 · net +1070 · threat 45 · provinces 28 (+0) · ceiling 30570 · army 107778 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2586 · trade 574 · admin 50 · tribute 487 · upkeep 840 · charges 1787
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — Britain would now join a league against us — relations −85. The price to keep her out: Talleyrand brings her to −10 in 9 turns (9 DP); buying off her design costs 1,116 gold and shortens the r…
  - TURN EVENTS 3
- COURTS: The court of Bavaria hardens over Revanche — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (Alliance → Defensive Alliance)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)
  - LOG moment: The Throne of Holland — the Emperor answers: Keep the Republic
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-ULM_t20` → Game saved: CMD-ULM_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 20967 · net +979 · threat 45 · provinces 28 (+0) · ceiling 30750 · army 106940 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2588 · trade 574 · admin 50 · tribute 487 · upkeep 824 · charges 1896
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — Britain enacts the Commissariat — fed provinces feed 25% more men (×1.25).
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, enemy_marshal_commissioned, diplomatic_dp_regen)
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — 'Lannes, recruit' raises them at Franche-Comte. Nothing was spent.
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- LEDGER treasury 21956 · net +890 · threat 45 · provinces 28 (+0) · ceiling 30850 · army 106127 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 487 · upkeep 816 · charges 1995
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (Defensive Alliance → Non-Aggression)
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 22846 · net +1026 · threat 45 · provinces 28 (+0) · ceiling 33100 · army 105338 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 816 · charges 2084
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 29 and declare on turn 32: Britain, Austria, Russia and 3 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: stance_change×1, wait×1
- LEDGER treasury 23880 · net +1267 · threat 45 · provinces 28 (+0) · ceiling 36550 · army 104572 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 1049 · upkeep 808 · charges 2188
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — Britain enacts Congreve's Rockets — artillery levies cost 15% less (×0.85).
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 2 · Holland client petition · The Secretariat moment letter
- LEDGER treasury 25155 · net +1148 · threat 45 · provinces 28 (+0) · ceiling 36630 · army 103829 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 1049 · upkeep 800 · charges 2315
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Austria, Russia and 3 lesser courts would march.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Sardinia → Bid for Their Al…
  - TURN EVENTS 3
- COURTS: The court of Russia eases over The Gulf and the Straits — joining the stronger side for pay is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)
  - LOG moment: The Remounts — an affair of state is laid before the Emperor

## Turn 25 — Late September 1806
  - MAILBOX #19 Holland incoming_proposal: Holland — Client's Petition → activated
  - MAILBOX #20 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  -     ↳ refused: Sire, another matter has arrived since — this concerns another court. Your earlier answer was not delivered; …
  - POPUP diplomatic_dialogue: incoming_proposal #23 → reject_ai_proposal
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: moment_letter #23 → reject_ai_proposal
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 25966 · net +730 · threat 45 · provinces 28 (+0) · ceiling 33260 · army 103108 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 800 · charges 2396
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — the allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Allegiance.
  - RAIL allegiance_in_play: The allegiance of Bavaria is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Bavaria → Bid for Their Alle…
  - TURN EVENTS 5
- COURTS: The court of Bavaria eases over Revanche — joining the stronger side for pay is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Remounts — the Emperor answers: Let the depots wait

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 26712 · net +671 · threat 49 · provinces 28 (+0) · ceiling 33420 · army 102410 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 784 · charges 2471
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — relations between Austria and Britain have collapsed: Alliance → Defensive Alliance.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Britain (Alliance → Defensive Alliance)
  - LOG moment: Russia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Tyrol. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 99% -> 84%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 27162 · net +610 · threat 53 · provinces 28 (+0) · ceiling 33260 · army 104642 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 800 · charges 2516
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — the bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - RAIL allegiance_settled: The bidding for Sardinia is closed: she signs a defensive alliance with Britain.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: Sardinia and Britain sign a Defensive Alliance
  - LOG moment: Austria decrees the Camps of Instruction for 8 turns (4 authority)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 27772 · net +549 · threat 57 · provinces 28 (+0) · ceiling 33260 · army 103898 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 800 · charges 2577
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — Europe has watched us 22 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Austria, Russia and 3 lesser courts would march. The cheapest court to keep ou…
  - RAIL allegiance_settled: The bidding for Bavaria is closed in our favour, but our relations are too cool for any pact the table can sign.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG moment: The Host's Claims — an affair of state is laid before the Emperor

## Turn 29 — Late November 1806
  - MAILBOX #21 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #24 → reject_ai_proposal
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 28321 · net +494 · threat 60 · provinces 28 (+0) · ceiling 33260 · army 103176 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 800 · charges 2632
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — the courts of Europe are drawing together against us.
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_coalition_brewing, agenda_shift)
  - LOG coalition_brewing_started: Coalition brewing — Britain, Russia, Austria, Sweden, Hanover and Sardinia alarmed (threat: 60)
  - LOG sponsorship_granted: Britain sponsors Russia against France (500g/turn)
  - LOG moment: The Host's Claims — the Emperor answers: Live off the land

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Tyrol, Your Majesty — Davout stands there on foreign ground. Recruitment is impossible there.'
  - saved `CMD-ULM_t30` → Game saved: CMD-ULM_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 28823 · net +452 · threat 58 · provinces 28 (+0) · ceiling 33340 · army 102476 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 792 · charges 2682
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — London now pays Sweden 500 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design costs 1…
  - TURN EVENTS 4
- COURTS: The court of Saxony hardens over The Wettin Crown — prepared now to go as far as joining the stronger side for pay.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (500g/turn)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 29275 · net +407 · threat 56 · provinces 28 (+0) · ceiling 33340 · army 101796 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 712 · upkeep 792 · charges 2727
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — St Petersburg now pays Sweden 300 gold a turn against us. She would march in the next league — the price to keep her out: Talleyrand brings her to −10 in 3 turns (3 DP); buying off her design …
  - RAIL allegiance_in_play: The allegiance of Saxony is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Saxony → Bid for Their Allegi…
  - RAIL allegiance_in_play: The allegiance of Hesse is in play — every court with gold or standing now bids for the flip. Bid in the Cabinet: F1 → Hesse → Bid for Their Allegian…
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Bavaria (design ask)
  - LOG moment: Britain decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 28263 · net -637 · threat 54 · provinces 28 (+0) · ceiling 23087 · army 101137 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 574 · admin 50 · tribute 1049 · upkeep 1216 · charges 3235 · blockade 359 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0
- DISPATCH: Sire — Britain, Russia, Austria, Sweden and Sardinia are at war with France. Britain tears up the Peace Treaty to do it. Russia tears up the Peace Treaty to do it. Austria tears up the Peace Treaty t…
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Britain, Russia, Austria, Sweden and Sardinia via their alliance with France.
  - RAIL diplomatic_war_declared: Britain has declared war on France, shattering the Peace Treaty, with 3 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Russia has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Austria has declared war on France, shattering the Peace Treaty, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sweden has declared war on France, with 2 allied courts poised to follow.
  - RAIL diplomatic_war_declared: Sardinia has declared war on France, with 2 allied courts poised to follow.
  - RAIL +4 more
  - TURN EVENTS 4
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: And Sardinia, Britain and Bavaria stir at their own designs.
- DIPLO +15 medium/low (diplomatic_dp_regen, witness_strike_recorded ×3, diplomatic_treaty_broken ×2, blockade_begins ×4, diplomatic_relation_shift ×5)
  - LOG diplomatic_treaty_broken: Britain has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Spain was forced to break the Peace Treaty with Britain (cascade).
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.
  - LOG diplomatic_treaty_broken: Austria has broken the Peace Treaty with France by declaring war.
  - LOG diplomatic_treaty_broken: Bavaria was forced to break the Peace Treaty with Austria (cascade).
  - LOG coalition_declared: The Fourth Austrian Coalition — Coalition formed against France! Members: Austria, Britain, Russia, Sardinia and Sweden

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max …
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Murat commands cavalry — 'Murat, recruit' raises horse for him; foot are raised by an infantry corps — 'Lannes, recruit' raises them at Franche-Comte. Nothing was spent.
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- enemy phase: 7 actions, 3 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout · Archduke Charles attacks Tyrol · Archduke Charles attacks Bernadotte
  - 🏴 Austria: Archduke Charles attacks Tyrol — Tyrol CAPTURED! (was Kingdom of Italy) (secured)
  - ⚔ Archduke Charles (lost 1773) vs Davout (lost 3970) — The hills were ours, but Archduke Charles took them. Davout's position was overrun. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 262) vs Bernadotte (lost 2482) — Bernadotte held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×3, unfortify×2, move×2
- LEDGER treasury 27226 · net -703 · threat 52 · provinces 28 (+0) · ceiling 21893 · army 93184 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 1076 · charges 3329 · blockade 359 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0 · Amey trust 60 Questioning glory 0
- DISPATCH: Sire — Davout's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 12,923 men ashore at Carniola.
  - TURN EVENTS 6
- DIPLO +8 medium/low (province_changed_hands ×2, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×3, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 500g reaches Austria
  - LOG moment: Russia decrees the Magazines for 8 turns (2,500 gold)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 11 actions, 4 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles attacks Deroy · Archduke Charles attacks Wrede · Archduke John attacks Deroy · Archduke Charles attacks Munich
  - 🏴 Austria: Archduke Charles attacks Wrede — Franconia CAPTURED! (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 2901) vs Deroy (lost 3584, own corps) — Neither Deroy nor Archduke Charles could claim the field. The armies remain locked. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 815) vs Wrede (lost 1450, own corps) — An aggressive stance invites disaster when one is not the attacker, Sire. Wrede paid the price. And Wrede was taken on …
  - ⚔ Archduke John (lost 644) vs Deroy (lost 6416) — Even the favorable ground could not save Deroy, Sire. Archduke John overcame the terrain.
  - verbs: move×5, attack×4, wait×1, recruit×1
- LEDGER treasury 26523 · net -689 · threat 50 · provinces 28 (+0) · ceiling 21423 · army 92258 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2590 · trade 574 · admin 50 · tribute 937 · upkeep 1076 · charges 3315 · blockade 359 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#1) · Davout trust 85 Loyal glory 0 (#2) · Soult trust 70 Reliable glory 0 (#3) · Lannes trust 85 Loyal glory 0 (#4) · Murat trust 66 Reliable glory 0 (#5) · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0 · Amey trust 60 Questioning glory 0
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL allegiance_settled: The bidding for Saxony is closed in our favour, but our relations are too cool for any pact the table can sign.
  - RAIL allegiance_settled: The bidding for Hesse is closed in our favour, but our relations are too cool for any pact the table can sign.
  - TURN EVENTS 6
- DIPLO +4 medium/low (province_changed_hands, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG moment: Britain decrees the Magazines for 8 turns (2,500 gold)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✗ Soult cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: 5 actions, 5 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout · Shrapnel bombards Massena · Archduke Charles attacks Munich · Archduke Charles attacks Ney
  - 🏴 Austria: Archduke Charles attacks Munich — The garrison of Munich is destroyed. · Region captured: Munich (was Bavaria) (secured)
  - ⚔ Archduke Charles (lost 1783) vs Ney (lost 772, own corps) — Amey failed to arrive in time. Ney's army fought without expected support.
  - ⚔ Archduke Charles (lost 1279) vs Napoleon (lost 421, own corps) — Napoleon fought without Amey's support. The roads, or the will, proved insufficient.
  - verbs: attack×5
- ORDER Ney [awaiting_response]: Ney is cornered at Franche-Comte with 2,688 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the…
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Franche-Comte with 2,688 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. Fight to the last: one final defense at +25% that bleeds the enemy and halts his pursuit — then the survivors are taken, certainly. Attempt a breakout: 50% he cuts his way out, 50% he is taken. → fight_to_the_last
- ENVOYS WAITING 1 · The Secretariat moment letter
- LEDGER treasury 24613 · net -1433 · threat 48 · provinces 28 (+0) · ceiling 16354 · army 78735 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2575 · trade 574 · admin 50 · tribute 787 · upkeep 980 · charges 3925 · contributions 65 · blockade 359 · admiralty 90
- MARSHALS Ney captured · Davout trust 85 Loyal glory 0 (#1) · Soult trust 70 Reliable glory 0 (#2) · Lannes trust 85 Loyal glory 0 (#3) · Murat captured · Bernadotte trust 40 Strained glory 0 (#4) · Massena trust 60 Questioning glory 0 (#5) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0 · Amey trust 54 Questioning glory 0
- DISPATCH: Sire — Marshal Murat has been taken. Austria holds him prisoner.
  - RAIL expedition_landed: THE LANDING: Paget has put 14,696 men ashore at Piedmont.
  - TURN EVENTS 4
- DIPLO +5 medium/low (province_changed_hands ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG moment: The Squadron for Santo Domingo — an affair of state is laid before the Emperor

## Turn 36 — Early March 1807
  - MAILBOX #22 The Secretariat incoming_proposal: The Secretariat — An Affair of State → activated
  - POPUP diplomatic_dialogue: moment_letter #25 → reject_ai_proposal
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 8% (Ag…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty — Soult stands there on foreign ground. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- enemy phase: 5 actions, 3 attacks — Russia, Prussia, Spain and 8 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout · Archduke Charles attacks Napoleon · Archduke Charles attacks Bernadotte
  - ⚔ Archduke Charles (lost 751) vs Napoleon (lost 662, own corps) — Amey failed to arrive in time. Napoleon's army fought without expected support.
  - ⚔ Archduke Charles (lost 261) vs Bernadotte (lost 998, own corps) — Bernadotte fought without Amey's support. The roads, or the will, proved insufficient.
  - verbs: attack×3, move×2
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Franche-Comte — 1,249 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Franche-Comte — 1,249 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- LEDGER treasury 22175 · net -2210 · threat 46 · provinces 28 (+0) · ceiling 12614 · army 68541 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2539 · trade 574 · admin 50 · tribute 787 · upkeep 908 · charges 4664 · contributions 139 · blockade 359 · admiralty 90
- MARSHALS Ney captured · Davout trust 85 Loyal glory 0 (#1) · Soult trust 70 Reliable glory 0 (#2) · Lannes captured · Murat captured · Bernadotte trust 40 Strained glory 0 (#3) · Massena trust 60 Questioning glory 0 (#4) · Napoleon captured · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0 · Amey trust 48 Questioning glory 0
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - RAIL third_party_peace: THE CONGRESS: Bavaria and Austria have made their peace without France. Bavaria, beaten (-45), sues for peace and Austria takes it on the held line; …
  - TURN EVENTS 4
- COURTS: The court of Saxony eases over The Wettin Crown — alliance is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG moment: The Squadron for Santo Domingo — the Emperor answers: Ferrand must hold alone
  - LOG moment: The Ottoman Empire decrees the Camps of Instruction for 8 turns (2,000 gold)
  - LOG diplomatic_treaty_broken: Russia has broken the Peace Treaty with France by declaring war.
  - LOG sponsorship_granted: Russia sponsors Sweden against France (300g/turn)
  - LOG ai_ai_proposal_refused: Russia rebuffs Saxony (defensive alliance)
  - LOG ai_ai_proposal_refused: Sweden rebuffs Russia (design ask)
  - LOG sponsorship_expired: The compact between Russia and Sweden lapses

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% now, +5% more at the next dawn, then +2% a turn, max 12%. Cannot move or attack while fortified. Use 'unfortify' t…
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 6 actions, 5 attacks — Russia, Prussia, Spain and 7 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout · Shrapnel bombards Massena · Archduke Charles attacks Franche-Comte · Archduke Charles attacks Lorraine
  - 🏴 Austria: Archduke Charles attacks Franche-Comte — Region captured: Franche-Comte (was France) (secured)
  - 🏴 Austria: Archduke Charles attacks Lorraine — Region captured: Lorraine (was France) (secured)
  - 🏴 Austria: Archduke Charles attacks Rhineland — Region captured: Rhineland (was France) (secured)
  - verbs: attack×5, move×1
- ENVOYS WAITING 1 · Austria peace
- LEDGER treasury 19772 · net -1921 · threat 44 · provinces 25 (-3) · ceiling 11684 · army 66765 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2271 · trade 574 · admin 50 · tribute 787 · upkeep 892 · charges 4222 · contributions 40 · blockade 359 · admiralty 90
- MARSHALS Ney captured · Davout trust 85 Loyal glory 0 (#1) · Soult trust 70 Reliable glory 0 (#2) · Lannes captured · Murat captured · Bernadotte trust 40 Strained glory 0 (#3) · Massena trust 60 Questioning glory 0 (#4) · Napoleon captured · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0 · Amey trust 48 Questioning glory 0
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL design_promoted: REVANCHE AGAIN: Bavaria will not forgive Russia the loss of Munich. The old design hardens again in their court.
  - TURN EVENTS 4
- DIPLO +10 medium/low (province_changed_hands ×3, enemy_marshal_commissioned, diplomatic_dp_regen, diplomatic_auto_downgrade ×4, paymaster_subsidy)
  - LOG auto_downgrade: Relations auto-downgraded: Britain–Russia (Alliance → Defensive Alliance)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Sardinia (Defensive Alliance → Non-Aggression)
  - LOG auto_downgrade: Relations auto-downgraded: Britain–Sardinia (Defensive Alliance → Non-Aggression)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: Britain rebuffs Sardinia (design ask)
  - LOG third_party_peace: THE CONGRESS: Bavaria and Austria make peace without France
  - LOG moment: Prussia decrees the Camps of Instruction for 8 turns (2,000 gold)

## Turn 38 — Early April 1807
  - MAILBOX #23 Austria incoming_proposal: Austria — Peace Treaty → activated
  - POPUP diplomatic_dialogue: Austria, peace #26 → accept_ai_proposal
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Peace with Austria. → display-only
  - RATIFIED Austria · PEACE · enemy_victory
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Paget…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Paget at Normandy instead.) → trust
  - ↳ MUSTER — Lannes (5,000; expect about 15,783 with the corps likely to arrive, up to 16,907 if all march; certain 5,000; a bad day (1 in 10) 13,975) vs Paget (small force) at Normandy — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 591, own corps) vs Paget (lost 2825) — Reinforcements! Ney, Murat and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away. — The corps system brought Murat in. — The Line Holds +15% (Paget)
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, move×1, fortify×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 16522 · net -302 · threat 42 · provinces 25 (+0) · ceiling 14761 · army 83589 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2272 · trade 524 · admin 50 · tribute 787 · upkeep 1020 · charges 2497 · blockade 328 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#2) · Davout trust 85 Loyal glory 0 (#3) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 90 Loyal glory 1 (#1) vind +1 · Murat trust 66 Reliable glory 0 (#5) envies Lannes · Bernadotte trust 40 Strained glory 0 (#6) · Massena trust 60 Questioning glory 0 (#7) envies Lannes · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0 · Amey trust 48 Questioning glory 0
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +3% this morning; the courts have begun to notice that he can be beaten.
  - EXPECTS: Lannes's victories raise his expectation — he now looks for 40g/turn (holds 0g).
  - RAIL status_quo_conceded: Franche-Comte, Lorraine and Rhineland — left with Austria by the peace, titled to them by treaty.
  - RAIL peace_ratified: Peace ratified between Austria and France.
  - TURN EVENTS 9
- DIPLO +6 medium/low (diplomatic_treaty_signed, province_changed_hands, diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_auto_downgrade, paymaster_subsidy)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 34% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (Alliance → Defensive Alliance)
  - LOG british_subsidy: Britain's gold: 300g reaches Sweden
  - LOG design_promoted: REVANCHE: Bavaria swears again to retake Munich — Russia is not forgiven
  - LOG coalition_member_left: Austria has left the coalition.

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Shrapnel is at Tyrol, just one region away.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Moore at London inst…
  - POPUP objection: Murat, Murat firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Moore at London instead.) → trust
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Normandy (field levy — no depot; capped at 3,000) - Cost: 600 gold (×3 at war). Morale: 40% -> 40%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 600g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 9 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 15688 · net -213 · threat 40 · provinces 25 (+0) · ceiling 14471 · army 85996 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2278 · trade 524 · admin 50 · tribute 787 · upkeep 1036 · charges 2398 · blockade 328 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#2) · Davout trust 85 Loyal glory 0 (#3) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 90 Loyal glory 1 (#1) vind +1 · Murat trust 69 Reliable glory 0 (#5) vind pending envies Lannes · Bernadotte trust 40 Strained glory 0 (#6) envies Lannes · Massena trust 60 Questioning glory 0 (#7) envies Lannes · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0 · Amey trust 48 Questioning glory 0
- DISPATCH: Sire — Franche-Comte, Lorraine and Rhineland lie in enemy hands. Austria holds them.
  - RAIL third_party_peace: THE CONGRESS: Bavaria and Russia have made their peace without France. Bavaria, beaten (-27), sues for peace and Russia takes it on the held line; th…
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Normandy. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% now, 12% at dawn (the max) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortified. …
  - saved `CMD-ULM_t40` → Game saved: CMD-ULM_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 2 actions unused) Turn 41 begins!
- enemy phase: 8 actions, 5 attacks — Russia, Austria, Prussia and 8 other courts stirred as well, but their formations remain beyond our sight. — Shrapnel bombards Davout · Shrapnel bombards Massena · Deroy attacks Franconia · Deroy attacks Shrapnel
  - 🏴 Bavaria: Deroy attacks Franconia — Region captured: Franconia (was Britain) (secured)
  - ⚔ Deroy (lost 1716) vs Shrapnel (lost 126, own corps) — A pyrrhic victory for Shrapnel. Deroy gave ground grudgingly. — The Line Holds +15% (Shrapnel)
  - ⚔ Deroy (lost 2663) vs Wellesley (lost 363, own corps) — The prepared defenses proved their worth. Deroy could not dislodge Wellesley. — The Line Holds +12% (Wellesley)
  - verbs: attack×5, unfortify×1, fortify×1, recruit×1
- LEDGER treasury 15498 · net -200 · threat 39 · provinces 25 (+0) · ceiling 14383 · army 83485 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2285 · trade 524 · admin 50 · tribute 787 · upkeep 1004 · charges 2424 · blockade 328 · admiralty 90
- MARSHALS Ney trust 63 Reliable glory 0 (#2) · Davout trust 85 Loyal glory 0 (#3) · Soult trust 70 Reliable glory 0 (#4) · Lannes trust 90 Loyal glory 1 (#1) vind +1 · Murat trust 69 Reliable glory 0 (#5) vind pending · Bernadotte trust 40 Strained glory 0 (#6) envies Lannes · Massena trust 60 Questioning glory 0 (#7) · Napoleon trust 100 Loyal glory 0 · Dumonceau trust 60 Questioning glory 0 · Teulie trust 60 Questioning glory 0 · Amey trust 48 Questioning glory 0
- DISPATCH: Sire — London now pays St Petersburg 300 gold a turn against us — her war with us is paid for.
  - UNMET: Lannes expects 40g/turn, holds 0g — patience holds 2 more turns
  - TURN EVENTS 7
- DIPLO +4 medium/low (province_changed_hands, diplomatic_dp_regen, paymaster_subsidy, balance_of_europe_shifted)
  - LOG british_subsidy: Britain's gold: 300g reaches Sweden
  - LOG balance_of_europe_shifted: French-led alignment leads the current largest alignment at 34% of active European bloc power. Spain is the decisive non-France slice of the bloc; le…
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses
  - LOG third_party_peace: THE CONGRESS: Bavaria and Russia make peace without France

---
finished: **completed** · commands 200 · popups 62 · battles 28
